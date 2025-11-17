import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from api_dashboard_backend import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ok", "degraded"}
    assert "services" in payload


def _assert_optional_success(response):
    if response.status_code == 200:
        return response.json()
    assert response.status_code in {502, 503}
    return None


def test_coins_top_endpoint() -> None:
    response = client.get("/api/coins/top?limit=3")
    payload = _assert_optional_success(response)
    if payload:
        assert payload["count"] <= 3


def test_query_router() -> None:
    response = client.post("/api/query", json={"query": "Bitcoin price"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["type"] == "price"


def test_websocket_connection() -> None:
    with client.websocket_connect("/ws") as websocket:
        message = websocket.receive_json()
        assert message["type"] in {"connected", "update"}
