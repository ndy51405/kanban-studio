import os
from pathlib import Path
from typing import Generator
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from app.db import init_db
from app.main import app
from app.schemas import AIChatResponse, BoardData, Card


@pytest.fixture
def test_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[Path, None, None]:
    db_file = tmp_path / "test_chat_pm.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_file))
    init_db(db_file)
    yield db_file


@pytest.fixture
def client(test_db: Path) -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


def test_chat_conversational_leaves_db_unchanged(client: TestClient) -> None:
    mock_resp = AIChatResponse(
        reply="Your board looks great! You have 5 columns.",
        board=None,
    )
    with patch("app.main.chat_with_kanban", return_value=mock_resp):
        res = client.post(
            "/api/chat",
            json={"message": "How is my board doing?", "history": []},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["reply"] == "Your board looks great! You have 5 columns."
        assert data["board"] is None

        # Verify database board remains unchanged
        board_res = client.get("/api/kanban")
        assert len(board_res.json()["cards"]) == 8


def test_chat_board_mutation_persists_to_db(client: TestClient) -> None:
    board_res = client.get("/api/kanban")
    mutated_board = BoardData.model_validate(board_res.json())

    new_card_id = "card-mock-1"
    mutated_board.cards[new_card_id] = Card(
        id=new_card_id,
        title="Created by AI",
        details="Generated via mock",
    )
    mutated_board.columns[0].cardIds.append(new_card_id)

    mock_resp = AIChatResponse(
        reply="I've added the card 'Created by AI' to Backlog.",
        board=mutated_board,
    )

    with patch("app.main.chat_with_kanban", return_value=mock_resp):
        res = client.post(
            "/api/chat",
            json={
                "message": "Add a card titled 'Created by AI' to Backlog",
                "history": [],
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert "Created by AI" in data["reply"]
        assert data["board"] is not None
        assert new_card_id in data["board"]["cards"]

        # Verify change persisted to SQLite
        persisted_res = client.get("/api/kanban")
        persisted_board = persisted_res.json()
        assert new_card_id in persisted_board["cards"]
        assert persisted_board["cards"][new_card_id]["title"] == "Created by AI"
        assert new_card_id in persisted_board["columns"][0]["cardIds"]


def test_live_ai_chat_creates_card_in_sqlite(client: TestClient) -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set; skipping live AI integration test")

    res = client.post(
        "/api/chat",
        json={
            "message": "Add a card titled 'Launch MVP' to the Backlog column with details 'Ship MVP'",
            "history": [],
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["reply"]) > 0
    assert data["board"] is not None

    cards = data["board"]["cards"]
    created_card = next(
        (c for c in cards.values() if "Launch MVP" in c["title"]), None
    )
    assert created_card is not None, f"Expected 'Launch MVP' card in cards, got: {cards}"

    backlog_col = next(
        col for col in data["board"]["columns"] if col["id"] == "col-backlog"
    )
    assert created_card["id"] in backlog_col["cardIds"]

    # Verify persisted in SQLite
    db_res = client.get("/api/kanban")
    db_board = db_res.json()
    assert created_card["id"] in db_board["cards"]
    assert created_card["id"] in db_board["columns"][0]["cardIds"]

