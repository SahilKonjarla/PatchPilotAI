from typing import Dict

from fastapi import FastAPI

app = FastAPI(
    title="PatchPilotAI",
    description="Lightweight multi-agent code debugging and app review backend.",
    version="0.1.0",
)


@app.get("/")
def read_root() -> Dict[str, str]:
    return {
        "app": "PatchPilotAI",
        "status": "running",
        "message": "FastAPI backend starter is online.",
    }


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}
