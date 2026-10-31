from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Hello from FastAPI"}


def test_root_serves_kanban_app() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Kanban Studio" in response.text


def test_serves_next_static_assets() -> None:
    html = client.get("/").text
    asset = html.split('src="/_next/')[1].split('"')[0]
    response = client.get(f"/_next/{asset}")
    assert response.status_code == 200
