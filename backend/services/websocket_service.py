"""
WebSocket Service
Handles real-time data updates to connected clients
"""
import asyncio
import json
import logging
from typing import Dict, Set, Any, List, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""

    def __init__(self):
        # Active connections by client ID
        self.active_connections: Dict[str, WebSocket] = {}

        # Subscriptions: {api_id: set(client_ids)}
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)

        # Reverse subscriptions: {client_id: set(api_ids)}
        self.client_subscriptions: Dict[str, Set[str]] = defaultdict(set)

        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, metadata: Optional[Dict] = None):
        """
        Connect a new WebSocket client

        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
            metadata: Optional metadata about the connection
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_metadata[client_id] = metadata or {}

        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        """
        Disconnect a WebSocket client

        Args:
            client_id: Client identifier
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        # Remove all subscriptions for this client
        for api_id in self.client_subscriptions.get(client_id, set()).copy():
            self.unsubscribe(client_id, api_id)

        if client_id in self.client_subscriptions:
            del self.client_subscriptions[client_id]

        if client_id in self.connection_metadata:
            del self.connection_metadata[client_id]

        logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")

    def subscribe(self, client_id: str, api_id: str):
        """
        Subscribe a client to API updates

        Args:
            client_id: Client identifier
            api_id: API identifier to subscribe to
        """
        self.subscriptions[api_id].add(client_id)
        self.client_subscriptions[client_id].add(api_id)

        logger.debug(f"Client {client_id} subscribed to {api_id}")

    def unsubscribe(self, client_id: str, api_id: str):
        """
        Unsubscribe a client from API updates

        Args:
            client_id: Client identifier
            api_id: API identifier to unsubscribe from
        """
        if api_id in self.subscriptions:
            self.subscriptions[api_id].discard(client_id)

            # Clean up empty subscription sets
            if not self.subscriptions[api_id]:
                del self.subscriptions[api_id]

        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].discard(api_id)

        logger.debug(f"Client {client_id} unsubscribed from {api_id}")

    def subscribe_all(self, client_id: str):
        """
        Subscribe a client to all API updates

        Args:
            client_id: Client identifier
        """
        self.client_subscriptions[client_id].add('*')
        logger.debug(f"Client {client_id} subscribed to all updates")

    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """
        Send a message to a specific client

        Args:
            message: Message data
            client_id: Target client identifier
        """
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: Dict[str, Any], api_id: Optional[str] = None):
        """
        Broadcast a message to subscribed clients

        Args:
            message: Message data
            api_id: Optional API ID (broadcasts to all if None)
        """
        if api_id:
            # Send to clients subscribed to this specific API
            target_clients = self.subscriptions.get(api_id, set())

            # Also include clients subscribed to all updates
            target_clients = target_clients.union(
                {cid for cid, subs in self.client_subscriptions.items() if '*' in subs}
            )
        else:
            # Broadcast to all connected clients
            target_clients = set(self.active_connections.keys())

        # Send to all target clients
        disconnected_clients = []

        for client_id in target_clients:
            if client_id in self.active_connections:
                websocket = self.active_connections[client_id]
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    async def broadcast_api_update(self, api_id: str, data: Dict[str, Any], metadata: Optional[Dict] = None):
        """
        Broadcast an API data update

        Args:
            api_id: API identifier
            data: Updated data
            metadata: Optional metadata about the update
        """
        message = {
            'type': 'api_update',
            'api_id': api_id,
            'data': data,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }

        await self.broadcast(message, api_id)

    async def broadcast_status_update(self, status: Dict[str, Any]):
        """
        Broadcast a system status update

        Args:
            status: Status data
        """
        message = {
            'type': 'status_update',
            'status': status,
            'timestamp': datetime.now().isoformat()
        }

        await self.broadcast(message)

    async def broadcast_schedule_update(self, schedule_info: Dict[str, Any]):
        """
        Broadcast a schedule update

        Args:
            schedule_info: Schedule information
        """
        message = {
            'type': 'schedule_update',
            'schedule': schedule_info,
            'timestamp': datetime.now().isoformat()
        }

        await self.broadcast(message)

    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get connection statistics

        Returns:
            Statistics about connections and subscriptions
        """
        return {
            'total_connections': len(self.active_connections),
            'total_subscriptions': sum(len(subs) for subs in self.subscriptions.values()),
            'apis_with_subscribers': len(self.subscriptions),
            'clients': {
                client_id: {
                    'subscriptions': list(self.client_subscriptions.get(client_id, set())),
                    'metadata': self.connection_metadata.get(client_id, {})
                }
                for client_id in self.active_connections.keys()
            }
        }


class WebSocketService:
    """WebSocket service for real-time updates"""

    def __init__(self, scheduler_service=None, persistence_service=None):
        self.connection_manager = ConnectionManager()
        self.scheduler_service = scheduler_service
        self.persistence_service = persistence_service
        self.running = False

        # Register callbacks with scheduler if available
        if self.scheduler_service:
            self._register_scheduler_callbacks()

    def _register_scheduler_callbacks(self):
        """Register callbacks with the scheduler service"""
        # This would be called after scheduler is initialized
        # For now, we'll use a different approach where scheduler calls websocket service
        pass

    async def handle_client_message(self, websocket: WebSocket, client_id: str, message: Dict[str, Any]):
        """
        Handle incoming messages from clients

        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            message: Message from client
        """
        try:
            message_type = message.get('type')

            if message_type == 'subscribe':
                # Subscribe to specific API
                api_id = message.get('api_id')
                if api_id:
                    self.connection_manager.subscribe(client_id, api_id)
                    await self.connection_manager.send_personal_message({
                        'type': 'subscribed',
                        'api_id': api_id,
                        'status': 'success'
                    }, client_id)

            elif message_type == 'subscribe_all':
                # Subscribe to all updates
                self.connection_manager.subscribe_all(client_id)
                await self.connection_manager.send_personal_message({
                    'type': 'subscribed',
                    'api_id': '*',
                    'status': 'success'
                }, client_id)

            elif message_type == 'unsubscribe':
                # Unsubscribe from specific API
                api_id = message.get('api_id')
                if api_id:
                    self.connection_manager.unsubscribe(client_id, api_id)
                    await self.connection_manager.send_personal_message({
                        'type': 'unsubscribed',
                        'api_id': api_id,
                        'status': 'success'
                    }, client_id)

            elif message_type == 'get_data':
                # Request current cached data
                api_id = message.get('api_id')
                if api_id and self.persistence_service:
                    data = self.persistence_service.get_cached_data(api_id)
                    await self.connection_manager.send_personal_message({
                        'type': 'data_response',
                        'api_id': api_id,
                        'data': data
                    }, client_id)

            elif message_type == 'get_all_data':
                # Request all cached data
                if self.persistence_service:
                    data = self.persistence_service.get_all_cached_data()
                    await self.connection_manager.send_personal_message({
                        'type': 'data_response',
                        'data': data
                    }, client_id)

            elif message_type == 'get_schedule':
                # Request schedule information
                if self.scheduler_service:
                    schedules = self.scheduler_service.get_all_task_statuses()
                    await self.connection_manager.send_personal_message({
                        'type': 'schedule_response',
                        'schedules': schedules
                    }, client_id)

            elif message_type == 'update_schedule':
                # Update schedule for an API
                api_id = message.get('api_id')
                interval = message.get('interval')
                enabled = message.get('enabled')

                if api_id and self.scheduler_service:
                    self.scheduler_service.update_task_schedule(api_id, interval, enabled)
                    await self.connection_manager.send_personal_message({
                        'type': 'schedule_updated',
                        'api_id': api_id,
                        'status': 'success'
                    }, client_id)

            elif message_type == 'force_update':
                # Force immediate update for an API
                api_id = message.get('api_id')
                if api_id and self.scheduler_service:
                    success = await self.scheduler_service.force_update(api_id)
                    await self.connection_manager.send_personal_message({
                        'type': 'update_result',
                        'api_id': api_id,
                        'status': 'success' if success else 'failed'
                    }, client_id)

            elif message_type == 'ping':
                # Heartbeat
                await self.connection_manager.send_personal_message({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }, client_id)

            else:
                logger.warning(f"Unknown message type from {client_id}: {message_type}")

        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            await self.connection_manager.send_personal_message({
                'type': 'error',
                'message': str(e)
            }, client_id)

    async def notify_data_update(self, api_id: str, data: Dict[str, Any], metadata: Optional[Dict] = None):
        """
        Notify clients about data updates

        Args:
            api_id: API identifier
            data: Updated data
            metadata: Optional metadata
        """
        await self.connection_manager.broadcast_api_update(api_id, data, metadata)

    async def notify_status_update(self, status: Dict[str, Any]):
        """
        Notify clients about status updates

        Args:
            status: Status information
        """
        await self.connection_manager.broadcast_status_update(status)

    async def notify_schedule_update(self, schedule_info: Dict[str, Any]):
        """
        Notify clients about schedule updates

        Args:
            schedule_info: Schedule information
        """
        await self.connection_manager.broadcast_schedule_update(schedule_info)

    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket service statistics"""
        return self.connection_manager.get_connection_stats()


# Global instance
websocket_service = WebSocketService()
