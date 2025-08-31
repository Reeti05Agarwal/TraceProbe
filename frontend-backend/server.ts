// server.ts

import express from "express";
import multer from "multer";
import path from "path";
import fs from "fs";
import { Client as ESClient } from "@elastic/elasticsearch";
import axios from "axios"; 
import { exec } from "child_process";
import bcrypt from "bcrypt"; 
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const PORT = process.env.PORT ? Number(process.env.PORT) : 3000;

// IMPORTANT: when running inside docker, mount ./data to /data and set UPLOAD_DIR to /data/uploads
const UPLOAD_DIR = process.env.UPLOAD_DIR || path.join(process.cwd(), "data", "uploads");
const upload = multer({ dest: UPLOAD_DIR });

// Elasticsearch & Kibana & Producer URLs (configure via env)
const ES_URL = process.env.ELASTICSEARCH_URL || "http://elasticsearch:9200";
const KIBANA_URL = process.env.KIBANA_URL || "http://kibana:5601";
const PRODUCER_URL = process.env.PRODUCER_URL || "http://producer:5000";

const es = new ESClient({ node: ES_URL });

// Serve static UI assets
app.use(express.static("public"));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// API to get cases
app.get("/api/cases", async (req, res) => {
  try {
    const resp = await es.search({
      index: "cases",
      size: 100,
      sort: [{ "date_created": { order: "desc" } }]
    });
    const hits = resp.hits.hits.map(h => ({ id: h._id, ...(h._source as any) }));
    res.json(hits);
  } catch (e) {
    res.status(500).json({ error: String(e) });
  }
});

// Helper: create Kibana space
async function createKibanaSpace(spaceId: string, spaceName: string) {
  const body = { id: spaceId, name: spaceName, disabledFeatures: [] };
  await axios.post(`${KIBANA_URL}/api/spaces/space`, body, { headers: { "kbn-xsrf": "true" } });
}

// --- Updated: Import dashboard using host-side script ---
// async function importDashboardTemplate(spaceId: string, templatePath: string) {
//   const templateFileName = path.basename(templatePath);
//   return new Promise<void>((resolve, reject) => {
//     const command = `./import_dashboard.sh ${spaceId} ${templateFileName}`;
//     exec(command, (err, stdout, stderr) => {
//       if (err) return reject(err);
//       console.log("Kibana CLI stdout:\n", stdout);
//       console.error("Kibana CLI stderr:\n", stderr);
//       resolve();
//     });
//   });
// }


// async function importDashboardTemplate(spaceId: string, templatePath: string) {
//   const form = new FormData();
//   form.append('file', fs.createReadStream(templatePath));

//   const headers = {
//     ...form.getHeaders(), // sets Content-Type to multipart/form-data correctly
//     'kbn-xsrf': 'true',
//   };

//   const url = `http://kibana:5601/s/${spaceId}/api/saved_objects/_import?overwrite=true`;

//   try {
//     const response = await axios.post(url, form, { headers });
//     console.log("Import response:", response.data);
//   } catch (err: any) {
//     console.error("Import failed:", err.response?.data || err.message);
//   }
// }


// Helper: create index pattern inside the space
async function createIndexPattern(spaceId: string, indexPatternId: string, title: string, timeField = "timestamp") {
  const headers = { "kbn-xsrf": "true", "Content-Type": "application/json" };
  const body = { attributes: { title, timeFieldName: timeField } };
  await axios.post(
    `${KIBANA_URL}/s/${encodeURIComponent(spaceId)}/api/saved_objects/index-pattern/${encodeURIComponent(indexPatternId)}`,
    body,
    { headers }
  );
}

// POST /api/cases : create case and upload file
app.post("/api/cases", upload.single("file"), async (req, res) => {
  try {
    const { case_name, investigator_id, password, description } = req.body;
    if (!case_name || !investigator_id || !password || !req.file) {
      return res.status(400).json({ error: "missing_fields" });
    }

    // generate safe case_id
    const caseId = case_name.toLowerCase().replace(/[^a-z0-9-_]/g, "-").slice(0, 40);

    // save uploaded file
    const origName = req.file.originalname;
    const savedFileName = `${caseId}__${Date.now()}__${origName}`;
    const savedFilePath = path.join(UPLOAD_DIR, savedFileName);
    fs.renameSync(req.file.path, savedFilePath);

    // hash password
    const passwordHash = await bcrypt.hash(password, 10);

    // create case document in ES
    const caseDoc = {
      case_id: caseId,
      case_name,
      investigator_id,
      password_hash: passwordHash,
      description,
      upload_file: savedFileName,
      date_created: new Date().toISOString()
    };
    await es.index({ index: "cases", document: caseDoc });

    // Create Kibana space
    try {
      await createKibanaSpace(caseId, case_name);
    } catch (err: any) {
      if (err.response && err.response.status !== 409) throw err;
    }

    // // Import dashboard template using host script
    // const templatePath = path.join(process.cwd(), "templates", "dashboard_template.ndjson");
    // if (fs.existsSync(templatePath)) {
    //   await importDashboardTemplate(caseId, templatePath);
    // } else {
    //   console.warn("dashboard template not found, skipping import:", templatePath);
    // }

    // Create index pattern
    const indexPatternId = `ipdr_connections_${caseId}`;
    await createIndexPattern(caseId, indexPatternId, "ipdr_connections");

    // Trigger producer
    await axios.post(`${PRODUCER_URL}/process`, { file_path: savedFilePath, case_id: caseId });
    console.log("Saved file path:", savedFilePath);
    console.log("Sending to producer:", `${PRODUCER_URL}/process`);

    res.json({ status: "ok", case: caseDoc });

  } catch (err: any) {
    console.error("Create case error:", err && err.toString());
    res.status(500).json({ error: String(err) });
  }
});

// Minimal index page
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "views", "index.html"));
});

app.listen(PORT, () => {
  console.log(`Frontend server listening on http://0.0.0.0:${PORT}`);
});
