"""WebSocket tests for hf_space_server."""
from fastapi.testclient import TestClient

from hf_space_server import app


def test_websocket_ai_data_basic_echo() -> None:
    """WebSocket should accept connection and send status payload."""
    client = TestClient(app)

    with client.websocket_connect("/ws/ai/data") as websocket:
        websocket.send_text("ping")
        message = websocket.receive_text()
        assert "status" in message
        assert "Realtime channel active" in message


