"""
WebSocket Connection Handler for Real-time Updates
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_status_update(data: dict):
    """Broadcast status update to all clients"""
    await manager.broadcast({
        "type": "status_update",
        "data": data
    })


async def broadcast_log_entry(log: dict):
    """Broadcast new log entry"""
    await manager.broadcast({
        "type": "new_log_entry",
        "data": log
    })


async def broadcast_rate_limit_alert(alert: dict):
    """Broadcast rate limit alert"""
    await manager.broadcast({
        "type": "rate_limit_alert",
        "data": alert
    })
