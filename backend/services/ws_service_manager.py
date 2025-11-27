"""
Centralized WebSocket Service Manager

This module provides a unified interface for managing WebSocket connections
and broadcasting real-time data from various services.
"""

import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ServiceType(str, Enum):
    """Available service types for WebSocket subscriptions"""

    # Data Collection Services
    MARKET_DATA = "market_data"
    EXPLORERS = "explorers"
    NEWS = "news"
    SENTIMENT = "sentiment"
    WHALE_TRACKING = "whale_tracking"
    RPC_NODES = "rpc_nodes"
    ONCHAIN = "onchain"

    # Monitoring Services
    HEALTH_CHECKER = "health_checker"
    POOL_MANAGER = "pool_manager"
    SCHEDULER = "scheduler"

    # Integration Services
    HUGGINGFACE = "huggingface"
    PERSISTENCE = "persistence"

    # System Services
    SYSTEM = "system"
    ALL = "all"


class WebSocketConnection:
    """Represents a single WebSocket connection with subscription management"""

    def __init__(self, websocket: WebSocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.subscriptions: Set[ServiceType] = set()
        self.connected_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.metadata: Dict[str, Any] = {}

    async def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send a message to the client

        Returns:
            bool: True if successful, False if failed
        """
        try:
            await self.websocket.send_json(message)
            self.last_activity = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Error sending message to client {self.client_id}: {e}")
            return False

    def subscribe(self, service: ServiceType):
        """Subscribe to a service"""
        self.subscriptions.add(service)
        logger.info(f"Client {self.client_id} subscribed to {service.value}")

    def unsubscribe(self, service: ServiceType):
        """Unsubscribe from a service"""
        self.subscriptions.discard(service)
        logger.info(f"Client {self.client_id} unsubscribed from {service.value}")

    def is_subscribed(self, service: ServiceType) -> bool:
        """Check if subscribed to a service or 'all'"""
        return service in self.subscriptions or ServiceType.ALL in self.subscriptions


class WebSocketServiceManager:
    """
    Centralized manager for all WebSocket connections and service broadcasts
    """

    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.service_handlers: Dict[ServiceType, List[Callable]] = {}
        self._lock = asyncio.Lock()
        self._client_counter = 0

    def generate_client_id(self) -> str:
        """Generate a unique client ID"""
        self._client_counter += 1
        return f"client_{self._client_counter}_{int(datetime.utcnow().timestamp())}"

    async def connect(self, websocket: WebSocket) -> WebSocketConnection:
        """
        Accept a new WebSocket connection

        Args:
            websocket: The FastAPI WebSocket instance

        Returns:
            WebSocketConnection: The connection object
        """
        await websocket.accept()
        client_id = self.generate_client_id()

        async with self._lock:
            connection = WebSocketConnection(websocket, client_id)
            self.connections[client_id] = connection

        logger.info(f"New WebSocket connection: {client_id}")

        # Send connection established message
        await connection.send_message(
            {
                "type": "connection_established",
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat(),
                "available_services": [s.value for s in ServiceType],
            }
        )

        return connection

    async def disconnect(self, client_id: str):
        """
        Disconnect a client

        Args:
            client_id: The client ID to disconnect
        """
        async with self._lock:
            if client_id in self.connections:
                connection = self.connections[client_id]
                try:
                    await connection.websocket.close()
                except:
                    pass
                del self.connections[client_id]
                logger.info(f"Client disconnected: {client_id}")

    async def broadcast(
        self,
        service: ServiceType,
        message_type: str,
        data: Any,
        filter_func: Optional[Callable[[WebSocketConnection], bool]] = None,
    ):
        """
        Broadcast a message to all subscribed clients

        Args:
            service: The service sending the message
            message_type: Type of message
            data: Message payload
            filter_func: Optional function to filter which clients receive the message
        """
        message = {
            "service": service.value,
            "type": message_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        disconnected_clients = []

        async with self._lock:
            for client_id, connection in self.connections.items():
                # Check subscription and optional filter
                if connection.is_subscribed(service):
                    if filter_func is None or filter_func(connection):
                        success = await connection.send_message(message)
                        if not success:
                            disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)

    async def send_to_client(
        self, client_id: str, service: ServiceType, message_type: str, data: Any
    ) -> bool:
        """
        Send a message to a specific client

        Args:
            client_id: Target client ID
            service: Service sending the message
            message_type: Type of message
            data: Message payload

        Returns:
            bool: True if successful
        """
        async with self._lock:
            if client_id in self.connections:
                connection = self.connections[client_id]
                message = {
                    "service": service.value,
                    "type": message_type,
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                return await connection.send_message(message)
        return False

    async def handle_client_message(self, connection: WebSocketConnection, message: Dict[str, Any]):
        """
        Handle incoming messages from clients

        Expected message format:
        {
            "action": "subscribe" | "unsubscribe" | "get_status" | "ping",
            "service": "service_name" (for subscribe/unsubscribe),
            "data": {} (optional additional data)
        }
        """
        action = message.get("action")

        if action == "subscribe":
            service_name = message.get("service")
            if service_name:
                try:
                    service = ServiceType(service_name)
                    connection.subscribe(service)
                    await connection.send_message(
                        {
                            "service": "system",
                            "type": "subscription_confirmed",
                            "data": {
                                "service": service_name,
                                "subscriptions": [s.value for s in connection.subscriptions],
                            },
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                except ValueError:
                    await connection.send_message(
                        {
                            "service": "system",
                            "type": "error",
                            "data": {
                                "message": f"Invalid service: {service_name}",
                                "available_services": [s.value for s in ServiceType],
                            },
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

        elif action == "unsubscribe":
            service_name = message.get("service")
            if service_name:
                try:
                    service = ServiceType(service_name)
                    connection.unsubscribe(service)
                    await connection.send_message(
                        {
                            "service": "system",
                            "type": "unsubscription_confirmed",
                            "data": {
                                "service": service_name,
                                "subscriptions": [s.value for s in connection.subscriptions],
                            },
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                except ValueError:
                    await connection.send_message(
                        {
                            "service": "system",
                            "type": "error",
                            "data": {"message": f"Invalid service: {service_name}"},
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

        elif action == "get_status":
            await connection.send_message(
                {
                    "service": "system",
                    "type": "status",
                    "data": {
                        "client_id": connection.client_id,
                        "connected_at": connection.connected_at.isoformat(),
                        "last_activity": connection.last_activity.isoformat(),
                        "subscriptions": [s.value for s in connection.subscriptions],
                        "total_clients": len(self.connections),
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        elif action == "ping":
            await connection.send_message(
                {
                    "service": "system",
                    "type": "pong",
                    "data": message.get("data", {}),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        else:
            await connection.send_message(
                {
                    "service": "system",
                    "type": "error",
                    "data": {
                        "message": f"Unknown action: {action}",
                        "supported_actions": ["subscribe", "unsubscribe", "get_status", "ping"],
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    async def start_service_stream(
        self, service: ServiceType, data_generator: Callable, interval: float = 1.0
    ):
        """
        Start a continuous data stream for a service

        Args:
            service: The service type
            data_generator: Async function that generates data
            interval: Update interval in seconds
        """
        logger.info(f"Starting stream for service: {service.value}")

        while True:
            try:
                # Check if anyone is subscribed
                has_subscribers = False
                async with self._lock:
                    for connection in self.connections.values():
                        if connection.is_subscribed(service):
                            has_subscribers = True
                            break

                # Only fetch data if there are subscribers
                if has_subscribers:
                    data = await data_generator()
                    if data:
                        await self.broadcast(service=service, message_type="update", data=data)

                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                logger.info(f"Stream cancelled for service: {service.value}")
                break
            except Exception as e:
                logger.error(f"Error in service stream {service.value}: {e}")
                await asyncio.sleep(interval)

    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics"""
        subscription_counts = {}
        for service in ServiceType:
            subscription_counts[service.value] = sum(
                1 for conn in self.connections.values() if conn.is_subscribed(service)
            )

        return {
            "total_connections": len(self.connections),
            "clients": [
                {
                    "client_id": conn.client_id,
                    "connected_at": conn.connected_at.isoformat(),
                    "last_activity": conn.last_activity.isoformat(),
                    "subscriptions": [s.value for s in conn.subscriptions],
                }
                for conn in self.connections.values()
            ],
            "subscription_counts": subscription_counts,
        }


# Global instance
ws_manager = WebSocketServiceManager()
