"""
WebSocket Support Module
Provides real-time updates via WebSocket connections with connection management
"""

import asyncio
import json
from datetime import datetime
from typing import Set, Dict, Any, Optional, List
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from starlette.websockets import WebSocketState
from utils.logger import setup_logger
from database.db_manager import db_manager
from monitoring.rate_limiter import rate_limiter
from config import config

# Setup logger
logger = setup_logger("websocket", level="INFO")

# Create router for WebSocket routes
router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts messages to all connected clients
    """

    def __init__(self):
        """Initialize connection manager"""
        self.active_connections: Set[WebSocket] = set()
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        self._broadcast_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def connect(self, websocket: WebSocket, client_id: str = None):
        """
        Accept and register a new WebSocket connection

        Args:
            websocket: WebSocket connection
            client_id: Optional client identifier
        """
        await websocket.accept()
        self.active_connections.add(websocket)

        # Store metadata
        self.connection_metadata[websocket] = {
            "client_id": client_id or f"client_{id(websocket)}",
            "connected_at": datetime.utcnow().isoformat(),
            "last_ping": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"WebSocket connected: {self.connection_metadata[websocket]['client_id']} "
            f"(Total connections: {len(self.active_connections)})"
        )

        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connection_established",
                "client_id": self.connection_metadata[websocket]["client_id"],
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connected to Crypto API Monitor WebSocket",
            },
            websocket,
        )

    def disconnect(self, websocket: WebSocket):
        """
        Unregister and close a WebSocket connection

        Args:
            websocket: WebSocket connection to disconnect
        """
        if websocket in self.active_connections:
            client_id = self.connection_metadata.get(websocket, {}).get("client_id", "unknown")
            self.active_connections.remove(websocket)

            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]

            logger.info(
                f"WebSocket disconnected: {client_id} "
                f"(Remaining connections: {len(self.active_connections)})"
            )

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """
        Send a message to a specific WebSocket connection

        Args:
            message: Message dictionary to send
            websocket: Target WebSocket connection
        """
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected clients

        Args:
            message: Message dictionary to broadcast
        """
        disconnected = []

        for connection in self.active_connections.copy():
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_json(message)
                else:
                    disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_status_update(self):
        """
        Broadcast system status update to all connected clients
        """
        try:
            # Get latest system metrics
            latest_metrics = db_manager.get_latest_system_metrics()

            # Get all providers
            providers = config.get_all_providers()

            # Get rate limit statuses
            rate_limit_statuses = rate_limiter.get_all_statuses()

            # Get recent alerts (last hour, unacknowledged)
            alerts = db_manager.get_alerts(acknowledged=False, hours=1)

            # Build status message
            message = {
                "type": "status_update",
                "timestamp": datetime.utcnow().isoformat(),
                "system_metrics": {
                    "total_providers": (
                        latest_metrics.total_providers if latest_metrics else len(providers)
                    ),
                    "online_count": latest_metrics.online_count if latest_metrics else 0,
                    "degraded_count": latest_metrics.degraded_count if latest_metrics else 0,
                    "offline_count": latest_metrics.offline_count if latest_metrics else 0,
                    "avg_response_time_ms": (
                        latest_metrics.avg_response_time_ms if latest_metrics else 0
                    ),
                    "total_requests_hour": (
                        latest_metrics.total_requests_hour if latest_metrics else 0
                    ),
                    "total_failures_hour": (
                        latest_metrics.total_failures_hour if latest_metrics else 0
                    ),
                    "system_health": latest_metrics.system_health if latest_metrics else "unknown",
                },
                "alert_count": len(alerts),
                "active_websocket_clients": len(self.active_connections),
            }

            await self.broadcast(message)
            logger.debug(f"Broadcasted status update to {len(self.active_connections)} clients")

        except Exception as e:
            logger.error(f"Error broadcasting status update: {e}", exc_info=True)

    async def broadcast_new_log_entry(self, log_type: str, log_data: Dict[str, Any]):
        """
        Broadcast a new log entry

        Args:
            log_type: Type of log (connection, failure, collection, rate_limit)
            log_data: Log data dictionary
        """
        try:
            message = {
                "type": "new_log_entry",
                "timestamp": datetime.utcnow().isoformat(),
                "log_type": log_type,
                "data": log_data,
            }

            await self.broadcast(message)
            logger.debug(f"Broadcasted new {log_type} log entry")

        except Exception as e:
            logger.error(f"Error broadcasting log entry: {e}", exc_info=True)

    async def broadcast_rate_limit_alert(self, provider_name: str, percentage: float):
        """
        Broadcast rate limit alert

        Args:
            provider_name: Provider name
            percentage: Current usage percentage
        """
        try:
            message = {
                "type": "rate_limit_alert",
                "timestamp": datetime.utcnow().isoformat(),
                "provider": provider_name,
                "percentage": percentage,
                "severity": "critical" if percentage >= 95 else "warning",
            }

            await self.broadcast(message)
            logger.info(f"Broadcasted rate limit alert for {provider_name} ({percentage}%)")

        except Exception as e:
            logger.error(f"Error broadcasting rate limit alert: {e}", exc_info=True)

    async def broadcast_provider_status_change(
        self, provider_name: str, old_status: str, new_status: str, details: Optional[Dict] = None
    ):
        """
        Broadcast provider status change

        Args:
            provider_name: Provider name
            old_status: Previous status
            new_status: New status
            details: Optional details about the change
        """
        try:
            message = {
                "type": "provider_status_change",
                "timestamp": datetime.utcnow().isoformat(),
                "provider": provider_name,
                "old_status": old_status,
                "new_status": new_status,
                "details": details or {},
            }

            await self.broadcast(message)
            logger.info(
                f"Broadcasted provider status change: {provider_name} "
                f"{old_status} -> {new_status}"
            )

        except Exception as e:
            logger.error(f"Error broadcasting provider status change: {e}", exc_info=True)

    async def _periodic_broadcast_loop(self):
        """
        Background task that broadcasts updates every 10 seconds
        """
        logger.info("Starting periodic broadcast loop")

        while self._is_running:
            try:
                # Broadcast status update
                await self.broadcast_status_update()

                # Check for rate limit warnings
                rate_limit_statuses = rate_limiter.get_all_statuses()
                for provider, status_data in rate_limit_statuses.items():
                    if status_data and status_data.get("percentage", 0) >= 80:
                        await self.broadcast_rate_limit_alert(provider, status_data["percentage"])

                # Wait 10 seconds before next broadcast
                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Error in periodic broadcast loop: {e}", exc_info=True)
                await asyncio.sleep(10)

        logger.info("Periodic broadcast loop stopped")

    async def _heartbeat_loop(self):
        """
        Background task that sends heartbeat pings to all clients
        """
        logger.info("Starting heartbeat loop")

        while self._is_running:
            try:
                # Send ping to all connected clients
                ping_message = {"type": "ping", "timestamp": datetime.utcnow().isoformat()}

                await self.broadcast(ping_message)

                # Wait 30 seconds before next heartbeat
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}", exc_info=True)
                await asyncio.sleep(30)

        logger.info("Heartbeat loop stopped")

    async def start_background_tasks(self):
        """
        Start background broadcast and heartbeat tasks
        """
        if self._is_running:
            logger.warning("Background tasks already running")
            return

        self._is_running = True

        # Start periodic broadcast task
        self._broadcast_task = asyncio.create_task(self._periodic_broadcast_loop())
        logger.info("Started periodic broadcast task")

        # Start heartbeat task
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("Started heartbeat task")

    async def stop_background_tasks(self):
        """
        Stop background broadcast and heartbeat tasks
        """
        if not self._is_running:
            logger.warning("Background tasks not running")
            return

        self._is_running = False

        # Cancel broadcast task
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try:
                await self._broadcast_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped periodic broadcast task")

        # Cancel heartbeat task
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped heartbeat task")

    async def close_all_connections(self):
        """
        Close all active WebSocket connections
        """
        logger.info(f"Closing {len(self.active_connections)} active connections")

        for connection in self.active_connections.copy():
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.close(code=1000, reason="Server shutdown")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

        self.active_connections.clear()
        self.connection_metadata.clear()
        logger.info("All WebSocket connections closed")

    def get_connection_count(self) -> int:
        """
        Get the number of active connections

        Returns:
            Number of active connections
        """
        return len(self.active_connections)

    def get_connection_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all active connections

        Returns:
            List of connection metadata dictionaries
        """
        return [
            {
                "client_id": metadata["client_id"],
                "connected_at": metadata["connected_at"],
                "last_ping": metadata["last_ping"],
            }
            for metadata in self.connection_metadata.values()
        ]


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates

    Provides:
    - System status updates every 10 seconds
    - Real-time log entries
    - Rate limit alerts
    - Provider status changes
    - Heartbeat pings every 30 seconds

    Message Types:
    - connection_established: Sent when client connects
    - status_update: Periodic system status (every 10s)
    - new_log_entry: New log entry notification
    - rate_limit_alert: Rate limit warning
    - provider_status_change: Provider status change
    - ping: Heartbeat ping (every 30s)
    """
    client_id = None

    try:
        # Connect client
        await manager.connect(websocket)
        client_id = manager.connection_metadata.get(websocket, {}).get("client_id", "unknown")

        # Start background tasks if not already running
        if not manager._is_running:
            await manager.start_background_tasks()

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (pong responses, etc.)
                data = await websocket.receive_text()

                # Parse message
                try:
                    message = json.loads(data)

                    # Handle pong response
                    if message.get("type") == "pong":
                        if websocket in manager.connection_metadata:
                            manager.connection_metadata[websocket][
                                "last_ping"
                            ] = datetime.utcnow().isoformat()
                        logger.debug(f"Received pong from {client_id}")

                    # Handle subscription requests (future enhancement)
                    elif message.get("type") == "subscribe":
                        # Could implement topic-based subscriptions here
                        logger.debug(f"Client {client_id} subscription request: {message}")

                    # Handle unsubscribe requests (future enhancement)
                    elif message.get("type") == "unsubscribe":
                        logger.debug(f"Client {client_id} unsubscribe request: {message}")

                except json.JSONDecodeError:
                    logger.warning(f"Received invalid JSON from {client_id}: {data}")

            except WebSocketDisconnect:
                logger.info(f"Client {client_id} disconnected")
                break

            except Exception as e:
                logger.error(f"Error handling message from {client_id}: {e}", exc_info=True)
                break

    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}", exc_info=True)

    finally:
        # Disconnect client
        manager.disconnect(websocket)


@router.get("/ws/stats")
async def websocket_stats():
    """
    Get WebSocket connection statistics

    Returns:
        Dictionary with connection stats
    """
    return {
        "active_connections": manager.get_connection_count(),
        "connections": manager.get_connection_info(),
        "background_tasks_running": manager._is_running,
        "timestamp": datetime.utcnow().isoformat(),
    }


# Export manager and router
__all__ = ["router", "manager", "ConnectionManager"]
