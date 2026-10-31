from pathlib import Path
from typing import Generator
import pytest
from fastapi.testclient import TestClient

from app.db import init_db
from app.main import app


@pytest.fixture
def test_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[Path, None, None]:
    db_file = tmp_path / "test_pm.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_file))
    init_db(db_file)
    yield db_file


@pytest.fixture
def client(test_db: Path) -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def test_init_db_creates_file_and_seeds_defaults(test_db: Path) -> None:
    assert test_db.exists()
    assert test_db.stat().st_size > 0


def test_login_success(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )
    assert response.status_code == 200
    assert response.json() == {"username": "user", "status": "ok"}


def test_login_invalid_password(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_invalid_user(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "nonexistent", "password": "password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_get_kanban_board_seeded(client: TestClient) -> None:
    response = client.get("/api/kanban")
    assert response.status_code == 200
    data = response.json()
    assert "columns" in data
    assert "cards" in data
    assert len(data["columns"]) == 5
    assert len(data["cards"]) == 8

    # Verify column IDs and initial cards match specification
    column_ids = [col["id"] for col in data["columns"]]
    assert column_ids == [
        "col-backlog",
        "col-discovery",
        "col-progress",
        "col-review",
        "col-done",
    ]
    assert "card-1" in data["cards"]
    assert data["cards"]["card-1"]["title"] == "Align roadmap themes"


def test_put_kanban_board_persists_changes(client: TestClient) -> None:
    get_res = client.get("/api/kanban")
    board = get_res.json()

    # 1. Rename column
    board["columns"][0]["title"] = "Upcoming Ideas"

    # 2. Add new card
    board["cards"]["card-99"] = {
        "id": "card-99",
        "title": "New feature",
        "details": "Integration test details",
    }
    board["columns"][0]["cardIds"].append("card-99")

    # 3. Edit existing card
    board["cards"]["card-1"]["title"] = "Updated title"

    # 4. Move card across columns
    board["columns"][0]["cardIds"].remove("card-2")
    board["columns"][1]["cardIds"].append("card-2")

    # 5. Delete card
    del board["cards"]["card-8"]
    board["columns"][4]["cardIds"].remove("card-8")

    put_res = client.put("/api/kanban", json=board)
    assert put_res.status_code == 200

    # Fetch again and verify persistence in SQLite
    verify_res = client.get("/api/kanban")
    assert verify_res.status_code == 200
    updated_board = verify_res.json()

    assert updated_board["columns"][0]["title"] == "Upcoming Ideas"
    assert "card-99" in updated_board["cards"]
    assert updated_board["cards"]["card-99"]["title"] == "New feature"
    assert updated_board["cards"]["card-1"]["title"] == "Updated title"
    assert "card-2" in updated_board["columns"][1]["cardIds"]
    assert "card-8" not in updated_board["cards"]
    assert "card-8" not in updated_board["columns"][4]["cardIds"]


def test_put_kanban_invalid_payload_rejected(client: TestClient) -> None:
    # Missing cards object
    invalid_board = {"columns": []}
    response = client.put("/api/kanban", json=invalid_board)
    assert response.status_code == 422

