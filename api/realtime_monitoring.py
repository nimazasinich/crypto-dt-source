"""
Real-Time Monitoring Service with WebSocket Push Updates

This module provides real-time monitoring capabilities:
- Push updates for market data
- Real-time news alerts
- Sentiment changes
- Data collection status
- System health monitoring

All data is pushed via WebSocket when changes occur,
not just on a fixed interval.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

logger = logging.getLogger(__name__)

router = APIRouter()


# ===== CONNECTION MANAGER =====

class RealTimeConnectionManager:
    """
    Manages WebSocket connections for real-time updates
    Supports multiple channels for different data types
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # client_id -> set of channels
        self.channel_subscribers: Dict[str, Set[str]] = {}  # channel -> set of client_ids
        self._client_counter = 0
    
    async def connect(self, websocket: WebSocket) -> str:
        """Accept connection and return client ID"""
        await websocket.accept()
        self._client_counter += 1
        client_id = f"client_{self._client_counter}_{datetime.utcnow().timestamp()}"
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        logger.info(f"Real-time client connected: {client_id}")
        return client_id
    
    def disconnect(self, client_id: str):
        """Remove client and clean up subscriptions"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        if client_id in self.subscriptions:
            # Remove from all channel subscriber lists
            for channel in self.subscriptions[client_id]:
                if channel in self.channel_subscribers:
                    self.channel_subscribers[channel].discard(client_id)
            del self.subscriptions[client_id]
        
        logger.info(f"Real-time client disconnected: {client_id}")
    
    def subscribe(self, client_id: str, channel: str):
        """Subscribe client to a channel"""
        if client_id not in self.subscriptions:
            self.subscriptions[client_id] = set()
        self.subscriptions[client_id].add(channel)
        
        if channel not in self.channel_subscribers:
            self.channel_subscribers[channel] = set()
        self.channel_subscribers[channel].add(client_id)
        
        logger.debug(f"Client {client_id} subscribed to {channel}")
    
    def unsubscribe(self, client_id: str, channel: str):
        """Unsubscribe client from a channel"""
        if client_id in self.subscriptions:
            self.subscriptions[client_id].discard(channel)
        if channel in self.channel_subscribers:
            self.channel_subscribers[channel].discard(client_id)
    
    async def broadcast_to_channel(self, channel: str, data: Dict[str, Any]):
        """Broadcast message to all subscribers of a channel"""
        if channel not in self.channel_subscribers:
            return
        
        message = {
            "channel": channel,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        disconnected = []
        for client_id in self.channel_subscribers[channel]:
            try:
                websocket = self.active_connections.get(client_id)
                if websocket:
                    await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to {client_id}: {e}")
                disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def send_to_client(self, client_id: str, data: Dict[str, Any]):
        """Send message to specific client"""
        websocket = self.active_connections.get(client_id)
        if websocket:
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.warning(f"Failed to send to {client_id}: {e}")
                self.disconnect(client_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "channels": {
                channel: len(subscribers) 
                for channel, subscribers in self.channel_subscribers.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }


# Global connection manager
connection_manager = RealTimeConnectionManager()


# ===== AVAILABLE CHANNELS =====

class Channels:
    """Available WebSocket channels"""
    MARKET_DATA = "market_data"
    PRICE_UPDATES = "price_updates"
    NEWS = "news"
    SENTIMENT = "sentiment"
    WHALE_ALERTS = "whale_alerts"
    COLLECTION_STATUS = "collection_status"
    SYSTEM_HEALTH = "system_health"
    ALL = "all"


# ===== REAL-TIME PUBLISHER =====

class RealTimePublisher:
    """
    Publishes data to WebSocket channels in real-time
    Used by data collectors to push updates
    """
    
    def __init__(self, manager: RealTimeConnectionManager):
        self.manager = manager
        self.last_data: Dict[str, Any] = {}  # Cache last data per channel
    
    async def publish_market_data(self, data: List[Dict[str, Any]]):
        """Publish market data update"""
        # Only publish if data has changed significantly
        if self._has_significant_change(Channels.MARKET_DATA, data):
            await self.manager.broadcast_to_channel(Channels.MARKET_DATA, {
                "type": "market_update",
                "coins": data,
                "count": len(data)
            })
            self.last_data[Channels.MARKET_DATA] = data
    
    async def publish_price_update(self, symbol: str, price: float, change_24h: float = None):
        """Publish single price update"""
        await self.manager.broadcast_to_channel(Channels.PRICE_UPDATES, {
            "type": "price_update",
            "symbol": symbol,
            "price": price,
            "change_24h": change_24h
        })
    
    async def publish_news(self, articles: List[Dict[str, Any]]):
        """Publish news articles"""
        await self.manager.broadcast_to_channel(Channels.NEWS, {
            "type": "news_update",
            "articles": articles,
            "count": len(articles)
        })
    
    async def publish_sentiment(self, sentiment_data: Dict[str, Any]):
        """Publish sentiment update"""
        await self.manager.broadcast_to_channel(Channels.SENTIMENT, {
            "type": "sentiment_update",
            "data": sentiment_data
        })
    
    async def publish_whale_alert(self, transaction: Dict[str, Any]):
        """Publish whale transaction alert"""
        await self.manager.broadcast_to_channel(Channels.WHALE_ALERTS, {
            "type": "whale_alert",
            "transaction": transaction
        })
    
    async def publish_collection_status(self, collector_name: str, status: Dict[str, Any]):
        """Publish data collection status"""
        await self.manager.broadcast_to_channel(Channels.COLLECTION_STATUS, {
            "type": "collection_status",
            "collector": collector_name,
            "status": status
        })
    
    async def publish_system_health(self, health_data: Dict[str, Any]):
        """Publish system health update"""
        await self.manager.broadcast_to_channel(Channels.SYSTEM_HEALTH, {
            "type": "health_update",
            "data": health_data
        })
    
    def _has_significant_change(self, channel: str, new_data: Any) -> bool:
        """Check if data has changed significantly (to avoid spam)"""
        if channel not in self.last_data:
            return True
        
        # For market data, check if any price changed more than 0.1%
        if channel == Channels.MARKET_DATA:
            old_prices = {d.get("symbol"): d.get("price", 0) for d in self.last_data.get(channel, [])}
            for item in new_data:
                symbol = item.get("symbol")
                new_price = item.get("price", 0)
                old_price = old_prices.get(symbol, 0)
                if old_price > 0 and abs((new_price - old_price) / old_price) > 0.001:
                    return True
            return False
        
        return True


# Global publisher
publisher = RealTimePublisher(connection_manager)


def get_realtime_publisher() -> RealTimePublisher:
    """Get global publisher instance"""
    return publisher


# ===== WEBSOCKET ENDPOINTS =====

@router.websocket("/ws/realtime")
async def websocket_realtime(websocket: WebSocket):
    """
    Main real-time WebSocket endpoint
    
    After connecting, send subscription messages:
    {
        "action": "subscribe",
        "channels": ["market_data", "news", "sentiment"]
    }
    
    Or subscribe to all:
    {
        "action": "subscribe",
        "channels": ["all"]
    }
    
    To unsubscribe:
    {
        "action": "unsubscribe",
        "channels": ["news"]
    }
    """
    client_id = await connection_manager.connect(websocket)
    
    try:
        # Send welcome message with available channels
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "available_channels": [
                Channels.MARKET_DATA,
                Channels.PRICE_UPDATES,
                Channels.NEWS,
                Channels.SENTIMENT,
                Channels.WHALE_ALERTS,
                Channels.COLLECTION_STATUS,
                Channels.SYSTEM_HEALTH,
                Channels.ALL
            ],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            channels = data.get("channels", [])
            
            if action == "subscribe":
                if Channels.ALL in channels:
                    # Subscribe to all channels
                    for channel in [Channels.MARKET_DATA, Channels.PRICE_UPDATES, 
                                   Channels.NEWS, Channels.SENTIMENT,
                                   Channels.WHALE_ALERTS, Channels.COLLECTION_STATUS,
                                   Channels.SYSTEM_HEALTH]:
                        connection_manager.subscribe(client_id, channel)
                else:
                    for channel in channels:
                        connection_manager.subscribe(client_id, channel)
                
                await websocket.send_json({
                    "type": "subscribed",
                    "channels": list(connection_manager.subscriptions.get(client_id, set())),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif action == "unsubscribe":
                for channel in channels:
                    connection_manager.unsubscribe(client_id, channel)
                
                await websocket.send_json({
                    "type": "unsubscribed",
                    "channels": channels,
                    "remaining": list(connection_manager.subscriptions.get(client_id, set())),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif action == "get_stats":
                await websocket.send_json({
                    "type": "stats",
                    "data": connection_manager.get_stats()
                })
            
            elif action == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
    finally:
        connection_manager.disconnect(client_id)


@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """Dedicated WebSocket for price updates only"""
    client_id = await connection_manager.connect(websocket)
    connection_manager.subscribe(client_id, Channels.PRICE_UPDATES)
    connection_manager.subscribe(client_id, Channels.MARKET_DATA)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "channels": [Channels.PRICE_UPDATES, Channels.MARKET_DATA],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Price WebSocket error: {e}")
    finally:
        connection_manager.disconnect(client_id)


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """Dedicated WebSocket for alerts (whale, sentiment changes)"""
    client_id = await connection_manager.connect(websocket)
    connection_manager.subscribe(client_id, Channels.WHALE_ALERTS)
    connection_manager.subscribe(client_id, Channels.SENTIMENT)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "channels": [Channels.WHALE_ALERTS, Channels.SENTIMENT],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Alerts WebSocket error: {e}")
    finally:
        connection_manager.disconnect(client_id)


# ===== BACKGROUND TASKS =====

async def start_realtime_monitoring():
    """Start real-time monitoring background tasks"""
    logger.info("Starting real-time monitoring services...")
    
    # Import data collection worker
    try:
        from workers.data_collection_worker import get_data_collection_worker, get_realtime_fetcher
        worker = get_data_collection_worker()
        fetcher = get_realtime_fetcher()
        
        # Start periodic health check broadcasts
        asyncio.create_task(_broadcast_health_status())
        
        # Start periodic market data broadcasts
        asyncio.create_task(_broadcast_market_updates(fetcher))
        
        logger.info("Real-time monitoring services started")
    except Exception as e:
        logger.error(f"Failed to start real-time monitoring: {e}")


async def _broadcast_health_status():
    """Periodically broadcast system health"""
    while True:
        try:
            health_data = {
                "status": "healthy",
                "connections": connection_manager.get_stats(),
                "timestamp": datetime.utcnow().isoformat()
            }
            await publisher.publish_system_health(health_data)
        except Exception as e:
            logger.error(f"Health broadcast error: {e}")
        
        await asyncio.sleep(30)  # Every 30 seconds


async def _broadcast_market_updates(fetcher):
    """Periodically broadcast market updates"""
    while True:
        try:
            # Only broadcast if there are subscribers
            if connection_manager.channel_subscribers.get(Channels.MARKET_DATA):
                # Fetch latest data
                price_result = await fetcher.fetch_price("BTC")
                if price_result.get("success"):
                    await publisher.publish_price_update(
                        "BTC",
                        price_result.get("price"),
                        None
                    )
        except Exception as e:
            logger.error(f"Market broadcast error: {e}")
        
        await asyncio.sleep(60)  # Every minute


# ===== HTTP ENDPOINTS FOR STATS =====

@router.get("/api/realtime/stats")
async def get_realtime_stats():
    """Get real-time connection statistics"""
    return {
        "success": True,
        "data": connection_manager.get_stats()
    }


@router.get("/api/realtime/channels")
async def get_available_channels():
    """Get available real-time channels"""
    return {
        "success": True,
        "channels": [
            {"id": Channels.MARKET_DATA, "name": "Market Data", "description": "Real-time market prices and stats"},
            {"id": Channels.PRICE_UPDATES, "name": "Price Updates", "description": "Individual price changes"},
            {"id": Channels.NEWS, "name": "News", "description": "Latest crypto news articles"},
            {"id": Channels.SENTIMENT, "name": "Sentiment", "description": "Market sentiment updates"},
            {"id": Channels.WHALE_ALERTS, "name": "Whale Alerts", "description": "Large transaction alerts"},
            {"id": Channels.COLLECTION_STATUS, "name": "Collection Status", "description": "Data collection progress"},
            {"id": Channels.SYSTEM_HEALTH, "name": "System Health", "description": "System health monitoring"}
        ]
    }
