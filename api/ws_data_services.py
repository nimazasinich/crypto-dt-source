"""
WebSocket API for Data Collection Services

This module provides WebSocket endpoints for real-time data streaming
from all data collection services.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.services.ws_service_manager import ServiceType, ws_manager
from collectors.explorers import ExplorerDataCollector
from collectors.market_data import MarketDataCollector
from collectors.news import NewsCollector
from collectors.onchain import OnChainCollector
from collectors.rpc_nodes import RPCNodeCollector
from collectors.sentiment import SentimentCollector
from collectors.whale_tracking import WhaleTrackingCollector
from config import Config

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Data Collection Service Handlers
# ============================================================================


class DataCollectionStreamers:
    """Handles data streaming for all collection services"""

    def __init__(self):
        self.config = Config()
        self.market_data_collector = MarketDataCollector(self.config)
        self.explorer_collector = ExplorerDataCollector(self.config)
        self.news_collector = NewsCollector(self.config)
        self.sentiment_collector = SentimentCollector(self.config)
        self.whale_collector = WhaleTrackingCollector(self.config)
        self.rpc_collector = RPCNodeCollector(self.config)
        self.onchain_collector = OnChainCollector(self.config)

    # ========================================================================
    # Market Data Streaming
    # ========================================================================

    async def stream_market_data(self):
        """Stream real-time market data"""
        try:
            data = await self.market_data_collector.collect()
            if data:
                return {
                    "prices": data.get("prices", {}),
                    "volumes": data.get("volumes", {}),
                    "market_caps": data.get("market_caps", {}),
                    "price_changes": data.get("price_changes", {}),
                    "source": data.get("source", "unknown"),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming market data: {e}")
            return None

    async def stream_order_books(self):
        """Stream order book data"""
        try:
            # This would integrate with market_data_extended for order book data
            data = await self.market_data_collector.collect()
            if data and "order_book" in data:
                return {
                    "bids": data["order_book"].get("bids", []),
                    "asks": data["order_book"].get("asks", []),
                    "spread": data["order_book"].get("spread"),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming order books: {e}")
            return None

    # ========================================================================
    # Explorer Data Streaming
    # ========================================================================

    async def stream_explorer_data(self):
        """Stream blockchain explorer data"""
        try:
            data = await self.explorer_collector.collect()
            if data:
                return {
                    "latest_block": data.get("latest_block"),
                    "network_hashrate": data.get("network_hashrate"),
                    "difficulty": data.get("difficulty"),
                    "mempool_size": data.get("mempool_size"),
                    "transactions_count": data.get("transactions_count"),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming explorer data: {e}")
            return None

    async def stream_transactions(self):
        """Stream recent transactions"""
        try:
            data = await self.explorer_collector.collect()
            if data and "recent_transactions" in data:
                return {
                    "transactions": data["recent_transactions"],
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming transactions: {e}")
            return None

    # ========================================================================
    # News Streaming
    # ========================================================================

    async def stream_news(self):
        """Stream news updates"""
        try:
            data = await self.news_collector.collect()
            if data and "articles" in data:
                return {
                    "articles": data["articles"][:10],  # Latest 10 articles
                    "sources": data.get("sources", []),
                    "categories": data.get("categories", []),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming news: {e}")
            return None

    async def stream_breaking_news(self):
        """Stream breaking news alerts"""
        try:
            data = await self.news_collector.collect()
            if data and "breaking" in data:
                return {
                    "breaking_news": data["breaking"],
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming breaking news: {e}")
            return None

    # ========================================================================
    # Sentiment Streaming
    # ========================================================================

    async def stream_sentiment(self):
        """Stream sentiment analysis data"""
        try:
            data = await self.sentiment_collector.collect()
            if data:
                return {
                    "overall_sentiment": data.get("overall_sentiment"),
                    "sentiment_score": data.get("sentiment_score"),
                    "social_volume": data.get("social_volume"),
                    "trending_topics": data.get("trending_topics", []),
                    "sentiment_by_source": data.get("by_source", {}),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming sentiment: {e}")
            return None

    async def stream_social_trends(self):
        """Stream social media trends"""
        try:
            data = await self.sentiment_collector.collect()
            if data and "social_trends" in data:
                return {"trends": data["social_trends"], "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error streaming social trends: {e}")
            return None

    # ========================================================================
    # Whale Tracking Streaming
    # ========================================================================

    async def stream_whale_activity(self):
        """Stream whale transaction data"""
        try:
            data = await self.whale_collector.collect()
            if data:
                return {
                    "large_transactions": data.get("large_transactions", []),
                    "whale_wallets": data.get("whale_wallets", []),
                    "total_volume": data.get("total_volume"),
                    "alert_threshold": data.get("alert_threshold"),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming whale activity: {e}")
            return None

    async def stream_whale_alerts(self):
        """Stream whale transaction alerts"""
        try:
            data = await self.whale_collector.collect()
            if data and "alerts" in data:
                return {"alerts": data["alerts"], "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error streaming whale alerts: {e}")
            return None

    # ========================================================================
    # RPC Node Streaming
    # ========================================================================

    async def stream_rpc_status(self):
        """Stream RPC node status"""
        try:
            data = await self.rpc_collector.collect()
            if data:
                return {
                    "nodes": data.get("nodes", []),
                    "active_nodes": data.get("active_nodes"),
                    "total_nodes": data.get("total_nodes"),
                    "average_latency": data.get("average_latency"),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming RPC status: {e}")
            return None

    async def stream_blockchain_events(self):
        """Stream blockchain events from RPC nodes"""
        try:
            data = await self.rpc_collector.collect()
            if data and "events" in data:
                return {
                    "events": data["events"],
                    "block_number": data.get("block_number"),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming blockchain events: {e}")
            return None

    # ========================================================================
    # On-Chain Analytics Streaming
    # ========================================================================

    async def stream_onchain_metrics(self):
        """Stream on-chain analytics"""
        try:
            data = await self.onchain_collector.collect()
            if data:
                return {
                    "active_addresses": data.get("active_addresses"),
                    "transaction_count": data.get("transaction_count"),
                    "total_fees": data.get("total_fees"),
                    "gas_price": data.get("gas_price"),
                    "network_utilization": data.get("network_utilization"),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming on-chain metrics: {e}")
            return None

    async def stream_contract_events(self):
        """Stream smart contract events"""
        try:
            data = await self.onchain_collector.collect()
            if data and "contract_events" in data:
                return {
                    "events": data["contract_events"],
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming contract events: {e}")
            return None


# Global instance
data_streamers = DataCollectionStreamers()


# ============================================================================
# Background Streaming Tasks
# ============================================================================


async def start_data_collection_streams():
    """Start all data collection stream tasks"""
    logger.info("Starting data collection WebSocket streams")

    tasks = [
        # Market Data
        asyncio.create_task(
            ws_manager.start_service_stream(
                ServiceType.MARKET_DATA,
                data_streamers.stream_market_data,
                interval=5.0,  # 5 second updates
            )
        ),
        # Explorer Data
        asyncio.create_task(
            ws_manager.start_service_stream(
                ServiceType.EXPLORERS,
                data_streamers.stream_explorer_data,
                interval=10.0,  # 10 second updates
            )
        ),
        # News
        asyncio.create_task(
            ws_manager.start_service_stream(
                ServiceType.NEWS, data_streamers.stream_news, interval=60.0  # 1 minute updates
            )
        ),
        # Sentiment
        asyncio.create_task(
            ws_manager.start_service_stream(
                ServiceType.SENTIMENT,
                data_streamers.stream_sentiment,
                interval=30.0,  # 30 second updates
            )
        ),
        # Whale Tracking
        asyncio.create_task(
            ws_manager.start_service_stream(
                ServiceType.WHALE_TRACKING,
                data_streamers.stream_whale_activity,
                interval=15.0,  # 15 second updates
            )
        ),
        # RPC Nodes
        asyncio.create_task(
            ws_manager.start_service_stream(
                ServiceType.RPC_NODES,
                data_streamers.stream_rpc_status,
                interval=20.0,  # 20 second updates
            )
        ),
        # On-Chain Analytics
        asyncio.create_task(
            ws_manager.start_service_stream(
                ServiceType.ONCHAIN,
                data_streamers.stream_onchain_metrics,
                interval=30.0,  # 30 second updates
            )
        ),
    ]

    await asyncio.gather(*tasks, return_exceptions=True)


# ============================================================================
# WebSocket Endpoints
# ============================================================================


@router.websocket("/ws/data")
async def websocket_data_endpoint(websocket: WebSocket):
    """
    Unified WebSocket endpoint for all data collection services

    Connection URL: ws://host:port/ws/data

    After connecting, send subscription messages:
    {
        "action": "subscribe",
        "service": "market_data" | "explorers" | "news" | "sentiment" |
                   "whale_tracking" | "rpc_nodes" | "onchain" | "all"
    }

    To unsubscribe:
    {
        "action": "unsubscribe",
        "service": "service_name"
    }

    To get status:
    {
        "action": "get_status"
    }
    """
    connection = await ws_manager.connect(websocket)

    try:
        while True:
            # Receive and handle client messages
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)

    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"WebSocket error for client {connection.client_id}: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)


@router.websocket("/ws/market_data")
async def websocket_market_data(websocket: WebSocket):
    """
    Dedicated WebSocket endpoint for market data

    Auto-subscribes to market_data service
    """
    connection = await ws_manager.connect(websocket)
    connection.subscribe(ServiceType.MARKET_DATA)

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)
    except WebSocketDisconnect:
        logger.info(f"Market data client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"Market data WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)


@router.websocket("/ws/whale_tracking")
async def websocket_whale_tracking(websocket: WebSocket):
    """
    Dedicated WebSocket endpoint for whale tracking

    Auto-subscribes to whale_tracking service
    """
    connection = await ws_manager.connect(websocket)
    connection.subscribe(ServiceType.WHALE_TRACKING)

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)
    except WebSocketDisconnect:
        logger.info(f"Whale tracking client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"Whale tracking WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)


@router.websocket("/ws/news")
async def websocket_news(websocket: WebSocket):
    """
    Dedicated WebSocket endpoint for news

    Auto-subscribes to news service
    """
    connection = await ws_manager.connect(websocket)
    connection.subscribe(ServiceType.NEWS)

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)
    except WebSocketDisconnect:
        logger.info(f"News client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"News WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)


@router.websocket("/ws/sentiment")
async def websocket_sentiment(websocket: WebSocket):
    """
    Dedicated WebSocket endpoint for sentiment analysis

    Auto-subscribes to sentiment service
    """
    connection = await ws_manager.connect(websocket)
    connection.subscribe(ServiceType.SENTIMENT)

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)
    except WebSocketDisconnect:
        logger.info(f"Sentiment client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"Sentiment WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)
