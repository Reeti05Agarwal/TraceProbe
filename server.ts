// server.ts
import express from "express";
import multer from "multer";
import path from "path";
import fs from "fs";
import { Client as ESClient } from "@elastic/elasticsearch";
import axios from "axios";
import FormData from "form-data";
import bcrypt from "bcrypt";
import { fileURLToPath } from "url";
import os from "os";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const PORT = process.env.PORT ? Number(process.env.PORT) : 3000;

const UPLOAD_DIR =
  process.env.UPLOAD_DIR || path.join(process.cwd(), "data", "uploads");
fs.mkdirSync(UPLOAD_DIR, { recursive: true });
const upload = multer({ dest: UPLOAD_DIR });

app.use(express.static(path.join(__dirname, "public")));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// URLs
const ES_URL = process.env.ELASTICSEARCH_URL || "http://elasticsearch:9200";
const KIBANA_URL = process.env.KIBANA_URL || "http://kibana:5601";
const PRODUCER_URL = process.env.PRODUCER_URL || "http://producer:5000";

const es = new ESClient({ node: ES_URL });

// --- Helpers ---

async function createKibanaSpace(spaceId: string, spaceName: string) {
  try {
    await axios.post(
      `${KIBANA_URL}/api/spaces/space`,
      { id: spaceId, name: spaceName, disabledFeatures: [] },
      { headers: { "kbn-xsrf": "true" } }
    );
  } catch (err: any) {
    if (!(err.response && err.response.status === 409)) throw err;
  }
}

async function createIndexPattern(
  spaceId: string,
  indexPatternId: string,
  timeField = "timestamp"
) {
  const headers = { "kbn-xsrf": "true", "Content-Type": "application/json" };
  const body = { attributes: { title: indexPatternId, timeFieldName: timeField } };
  try {
    await axios.post(
      `${KIBANA_URL}/s/${encodeURIComponent(
        spaceId
      )}/api/saved_objects/index-pattern/${encodeURIComponent(indexPatternId)}`,
      body,
      { headers }
    );
  } catch (err: any) {
    if (!(err.response && err.response.status === 409)) throw err; // ignore "already exists"
  }
}

// Patch NDJSON: remove index-patterns, only adjust references
function patchNdjson(templatePath: string, caseId: string): string {
  const newIndexPatternId = `ipdr_connections_${caseId}`;
  const lines = fs
    .readFileSync(templatePath, "utf-8")
    .split("\n")
    .filter((l) => l.trim().length > 0);

  const patched = lines
    .map((line) => {
      try {
        const obj = JSON.parse(line);

        // drop index-pattern objects entirely (we create separately)
        if (obj.type === "index-pattern") return null;

        // patch references in dashboards/visualizations
        if (Array.isArray(obj.references)) {
          obj.references = obj.references.map((ref: any) =>
            ref.type === "index-pattern"
              ? { ...ref, id: newIndexPatternId }
              : ref
          );
        }

        return JSON.stringify(obj);
      } catch {
        console.warn("Skipping unparsable line in template:", line);
        return line;
      }
    })
    .filter(Boolean); // remove nulls

  const tmpPath = path.join(os.tmpdir(), `dashboard_${caseId}.ndjson`);
  fs.writeFileSync(tmpPath, patched.join("\n"));
  return tmpPath;
}

async function importDashboardTemplate(
  spaceId: string,
  templatePath: string,
  caseId: string
) {
  const patchedPath = patchNdjson(templatePath, caseId);
  const form = new FormData();
  form.append("file", fs.createReadStream(patchedPath));

  const headers = { ...form.getHeaders(), "kbn-xsrf": "true" };
  const url = `${KIBANA_URL}/s/${spaceId}/api/saved_objects/_import?overwrite=true`;

  const response = await axios.post(url, form, {
    headers,
    maxBodyLength: Infinity,
    maxContentLength: Infinity,
  });
  console.log("Import response:", response.data);
}

// --- Routes ---
// GET /api/cases (list all cases)
app.get("/api/cases", async (req, res) => {
  try {
    const result = await es.search({
      index: "cases",
      size: 100, // adjust as needed
      sort: [{ date_created: { order: "desc" } }],
      query: { match_all: {} },
    });

    const cases = result.hits.hits.map((hit: any) => {
      const c = hit._source;
      return {
        case_id: c.case_id,
        case_name: c.case_name,
        investigator_id: c.investigator_id,  
        description: c.description,
        date_created: c.date_created,
        dashboard_url: `http://kibana:5601/s/${c.case_name}/app/home`,
      };
    });

    res.json(cases);
  } catch (err: any) {
    console.error("Error fetching cases:", err?.response?.data || err.toString());
    res.status(500).json({ error: "server_error" });
  }
});



app.post("/api/cases", upload.single("file"), async (req, res) => {
  try {
    const { case_name, investigator_id, password, description } = req.body;
    if (!case_name || !investigator_id || !password || !req.file) {
      return res.status(400).json({ error: "missing_fields" });
    }

    const caseId = case_name
      .toLowerCase()
      .replace(/[^a-z0-9-_]/g, "-")
      .slice(0, 40);

    const savedFileName = `${caseId}__${Date.now()}__${req.file.originalname}`;
    const savedFilePath = path.join(UPLOAD_DIR, savedFileName);
    fs.renameSync(req.file.path, savedFilePath);

    const passwordHash = await bcrypt.hash(password, 10);

    const caseDoc = {
      case_id: caseId,
      case_name,
      investigator_id,
      password_hash: passwordHash,
      description,
      upload_file: savedFileName,
      date_created: new Date().toISOString(),
    };
    await es.index({ index: "cases", document: caseDoc });

    await createKibanaSpace(caseId, case_name);

    const indexPatternId = `ipdr_connections_${caseId}`;
    await createIndexPattern(caseId, indexPatternId);

    const templatePath = path.join(
      __dirname,
      "templates",
      "dashboard_template.ndjson"
    );
    if (fs.existsSync(templatePath)) {
      console.log("❤️ Importing dashboard for", caseId);
      await importDashboardTemplate(caseId, templatePath, caseId);
    }

    await axios.post(`${PRODUCER_URL}/process`, {
      file_path: savedFilePath,
      case_id: caseId,
    });

    res.json({ status: "ok", case: caseDoc });
  } catch (err: any) {
    console.error("Create case error:", err?.response?.data || err.toString());
    res.status(500).json({ error: String(err) });
  }
});

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "views", "index.html"));
});

app.listen(PORT, () => {
  console.log(`Frontend server listening on http://0.0.0.0:${PORT}`);
});

// POST /api/blacklist/:type (upload/paste list)
app.post("/api/blacklist/:type", async (req, res) => {
  try {
    const { type } = req.params; // "ip" | "domain" | ...
    const { entries } = req.body; // array of strings
    if (!Array.isArray(entries) || entries.length === 0) {
      return res.status(400).json({ error: "No entries provided" });
    }

    // ensure directory exists
    const dirPath = path.join(process.cwd(), "data", "blacklist");
    fs.mkdirSync(dirPath, { recursive: true });

    const filePath = path.join(dirPath, `blacklist_${type}.json`);

    // load existing entries
    let current: string[] = [];
    if (fs.existsSync(filePath)) {
      current = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    }

    const inserted: string[] = [];
    const skipped: string[] = [];

    for (const value of entries.map((v) => v.trim().toLowerCase())) {
      if (!value) continue;

      if (current.includes(value)) {
        skipped.push(value);
      } else {
        current.push(value);
        inserted.push(value);
      }
    }

    // save back to file
    fs.writeFileSync(filePath, JSON.stringify(current, null, 2), "utf-8");
    console.log("Blacklist file path:", filePath);


    res.json({ inserted, skipped });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "server_error" });
  }
});

// GET /api/blacklist/:type (show all)
app.get("/api/blacklist/:type", async (req, res) => {
  try {
    const { type } = req.params;
    const filePath = path.join(__dirname, "data", "blacklist", `blacklist_${type}.json`);

    if (!fs.existsSync(filePath)) return res.json([]);

    const data = fs.readFileSync(filePath, "utf-8");
    const entries = JSON.parse(data);
    res.json(entries);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "server_error" });
  }
});