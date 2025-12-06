"""Tests for the /api/ai/decision endpoint in hf_space_server."""
from fastapi.testclient import TestClient

from hf_space_server import app


def test_ai_decision_basic_response() -> None:
    """Endpoint should return a structured AI decision payload."""
    client = TestClient(app)

    payload = {
        "symbol": "BTC",
        "horizon": "swing",
        "risk_tolerance": "moderate",
        "context": "Test context",
        "model": "test-model",
    }

    response = client.post("/api/ai/decision", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["symbol"] == "BTC"
    assert data["horizon"] == "swing"
    assert data["decision"] in {"BUY", "SELL", "HOLD"}
    assert 0.5 <= data["confidence"] <= 0.95
    assert isinstance(data["signals"], list)
    assert isinstance(data["risks"], list)

