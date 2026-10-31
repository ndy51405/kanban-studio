import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Project Management MVP API")

# Built Next.js static export; defaults to frontend/out in the repo, overridden in Docker.
STATIC_DIR = Path(
    os.environ.get("STATIC_DIR", Path(__file__).resolve().parents[2] / "frontend" / "out")
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "message": "Hello from FastAPI"}


if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
