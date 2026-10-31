import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.db import authenticate_user, get_board_data, init_db, update_board_data
from app.schemas import BoardData, LoginRequest, LoginResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Project Management MVP API", lifespan=lifespan)

# Built Next.js static export; defaults to frontend/out in the repo, overridden in Docker.
STATIC_DIR = Path(
    os.environ.get("STATIC_DIR", Path(__file__).resolve().parents[2] / "frontend" / "out")
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "message": "Hello from FastAPI"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    if not authenticate_user(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return LoginResponse(username=payload.username, status="ok")


@app.get("/api/kanban", response_model=BoardData)
def get_kanban() -> BoardData:
    data = get_board_data("user")
    if data is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return BoardData.model_validate(data)


@app.put("/api/kanban", response_model=BoardData)
def update_kanban(payload: BoardData) -> BoardData:
    success = update_board_data("user", payload.model_dump())
    if not success:
        raise HTTPException(status_code=404, detail="Board or user not found")
    return payload


if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
