from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import app


def test_health_returns_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_endpoint_returns_200() -> None:
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200


def test_metrics_content_type_is_prometheus() -> None:
    client = TestClient(app)
    response = client.get("/metrics")
    assert "text/plain" in response.headers["content-type"]
