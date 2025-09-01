# ipdr_analyzer/producer/service.py
from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import threading
import os

app = FastAPI()

class Req(BaseModel):
    file_path: str
    case_id: str = None

def _run_processing(file_path: str, case_id: str | None):
    cmd = ["python3", "/app/ipdr_analyzer/producer/main.py", file_path]
    if case_id:
        cmd.append(case_id)
    # Run synchronously but inside a background thread so HTTP returns quickly
    subprocess.run(cmd, check=False)

@app.post("/process")
def process(req: Req):
    # quick validation
    if not os.path.exists(req.file_path):
        return {"status": "error", "reason": "file_not_found", "path": req.file_path}
    threading.Thread(target=_run_processing, args=(req.file_path, req.case_id)).start()
    return {"status": "started", "file": req.file_path, "case_id": req.case_id}
