from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "freelance-monitor"


def test_orders_rejects_invalid_limit():
    response = client.get("/orders/?limit=0")

    assert response.status_code == 422


def test_orders_rejects_invalid_status():
    response = client.get("/orders/?status=unknown")

    assert response.status_code == 422
