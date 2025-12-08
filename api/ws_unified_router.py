"""
Unified WebSocket Router

This module provides a master WebSocket endpoint that can access all services
and manage subscriptions across data collection, monitoring, and integration services.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import logging

from backend.services.ws_service_manager import ws_manager, ServiceType
from api.ws_data_services import start_data_collection_streams
from api.ws_monitoring_services import start_monitoring_streams
from api.ws_integration_services import start_integration_streams

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Master WebSocket Endpoint
# ============================================================================

@router.websocket("/ws/master")
async def websocket_master_endpoint(websocket: WebSocket):
    """
    Master WebSocket endpoint with access to ALL services

    Connection URL: ws://host:port/ws/master

    After connecting, send subscription messages:
    {
        "action": "subscribe",
        "service": "market_data" | "explorers" | "news" | "sentiment" |
                   "whale_tracking" | "rpc_nodes" | "onchain" |
                   "health_checker" | "pool_manager" | "scheduler" |
                   "huggingface" | "persistence" | "system" | "all"
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

    To ping:
    {
        "action": "ping",
        "data": {"your": "data"}
    }
    """
    connection = await ws_manager.connect(websocket)

    # Send welcome message with all available services
    await connection.send_message({
        "service": "system",
        "type": "welcome",
        "data": {
            "message": "Connected to master WebSocket endpoint",
            "available_services": {
                "data_collection": [
                    ServiceType.MARKET_DATA.value,
                    ServiceType.EXPLORERS.value,
                    ServiceType.NEWS.value,
                    ServiceType.SENTIMENT.value,
                    ServiceType.WHALE_TRACKING.value,
                    ServiceType.RPC_NODES.value,
                    ServiceType.ONCHAIN.value
                ],
                "monitoring": [
                    ServiceType.HEALTH_CHECKER.value,
                    ServiceType.POOL_MANAGER.value,
                    ServiceType.SCHEDULER.value
                ],
                "integration": [
                    ServiceType.HUGGINGFACE.value,
                    ServiceType.PERSISTENCE.value
                ],
                "system": [
                    ServiceType.SYSTEM.value,
                    ServiceType.ALL.value
                ]
            },
            "usage": {
                "subscribe": {"action": "subscribe", "service": "service_name"},
                "unsubscribe": {"action": "unsubscribe", "service": "service_name"},
                "get_status": {"action": "get_status"},
                "ping": {"action": "ping"}
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    })

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)

    except WebSocketDisconnect:
        logger.info(f"Master client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"Master WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)


@router.websocket("/ws/all")
async def websocket_all_services(websocket: WebSocket):
    """
    WebSocket endpoint with automatic subscription to ALL services

    Connection URL: ws://host:port/ws/all

    Automatically subscribes to all available services.
    You'll receive updates from all data collection, monitoring, and integration services.
    """
    connection = await ws_manager.connect(websocket)
    connection.subscribe(ServiceType.ALL)

    await connection.send_message({
        "service": "system",
        "type": "auto_subscribed",
        "data": {
            "message": "Automatically subscribed to all services",
            "subscription": ServiceType.ALL.value
        },
        "timestamp": datetime.utcnow().isoformat()
    })

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)

    except WebSocketDisconnect:
        logger.info(f"All-services client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"All-services WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)


@router.websocket("/ws")
async def websocket_default_endpoint(websocket: WebSocket):
    """
    Default WebSocket endpoint (alias for master endpoint)

    Connection URL: ws://host:port/ws

    Provides access to all services with subscription management.
    """
    connection = await ws_manager.connect(websocket)

    await connection.send_message({
        "service": "system",
        "type": "welcome",
        "data": {
            "message": "Connected to default WebSocket endpoint",
            "hint": "Send subscription messages to receive updates",
            "example": {"action": "subscribe", "service": "market_data"}
        },
        "timestamp": datetime.utcnow().isoformat()
    })

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)

    except WebSocketDisconnect:
        logger.info(f"Default client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"Default WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)


# ============================================================================
# REST API Endpoints for WebSocket Management
# ============================================================================

@router.get("/ws/stats")
async def get_websocket_stats():
    """
    Get WebSocket statistics

    Returns information about active connections, subscriptions, and services.
    """
    stats = ws_manager.get_stats()
    return {
        "status": "success",
        "data": stats,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ws/services")
async def get_available_services():
    """
    Get list of all available WebSocket services

    Returns categorized list of services that can be subscribed to.
    """
    return {
        "status": "success",
        "data": {
            "services": {
                "data_collection": {
                    "market_data": {
                        "name": "Market Data",
                        "description": "Real-time cryptocurrency prices, volumes, and market caps",
                        "update_interval": "5 seconds",
                        "endpoints": ["/ws/data", "/ws/market_data"]
                    },
                    "explorers": {
                        "name": "Blockchain Explorers",
                        "description": "Blockchain data, transactions, and network stats",
                        "update_interval": "10 seconds",
                        "endpoints": ["/ws/data"]
                    },
                    "news": {
                        "name": "News Aggregation",
                        "description": "Cryptocurrency news from multiple sources",
                        "update_interval": "60 seconds",
                        "endpoints": ["/ws/data", "/ws/news"]
                    },
                    "sentiment": {
                        "name": "Sentiment Analysis",
                        "description": "Market sentiment and social media trends",
                        "update_interval": "30 seconds",
                        "endpoints": ["/ws/data", "/ws/sentiment"]
                    },
                    "whale_tracking": {
                        "name": "Whale Tracking",
                        "description": "Large transaction monitoring and whale wallet tracking",
                        "update_interval": "15 seconds",
                        "endpoints": ["/ws/data", "/ws/whale_tracking"]
                    },
                    "rpc_nodes": {
                        "name": "RPC Nodes",
                        "description": "Blockchain RPC node status and events",
                        "update_interval": "20 seconds",
                        "endpoints": ["/ws/data"]
                    },
                    "onchain": {
                        "name": "On-Chain Analytics",
                        "description": "On-chain metrics and smart contract events",
                        "update_interval": "30 seconds",
                        "endpoints": ["/ws/data"]
                    }
                },
                "monitoring": {
                    "health_checker": {
                        "name": "Health Monitoring",
                        "description": "Provider health checks and system status",
                        "update_interval": "30 seconds",
                        "endpoints": ["/ws/monitoring", "/ws/health"]
                    },
                    "pool_manager": {
                        "name": "Pool Management",
                        "description": "Source pool status and failover events",
                        "update_interval": "20 seconds",
                        "endpoints": ["/ws/monitoring", "/ws/pool_status"]
                    },
                    "scheduler": {
                        "name": "Task Scheduler",
                        "description": "Scheduled task execution and status",
                        "update_interval": "15 seconds",
                        "endpoints": ["/ws/monitoring", "/ws/scheduler_status"]
                    }
                },
                "integration": {
                    "huggingface": {
                        "name": "HuggingFace AI",
                        "description": "AI model registry and sentiment analysis",
                        "update_interval": "60 seconds",
                        "endpoints": ["/ws/integration", "/ws/huggingface", "/ws/ai"]
                    },
                    "persistence": {
                        "name": "Data Persistence",
                        "description": "Data storage, exports, and backups",
                        "update_interval": "30 seconds",
                        "endpoints": ["/ws/integration", "/ws/persistence"]
                    }
                },
                "system": {
                    "all": {
                        "name": "All Services",
                        "description": "Subscribe to all available services",
                        "endpoints": ["/ws/all"]
                    }
                }
            },
            "master_endpoints": {
                "/ws": "Default endpoint with subscription management",
                "/ws/master": "Master endpoint with all service access",
                "/ws/all": "Auto-subscribe to all services"
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ws/endpoints")
async def get_websocket_endpoints():
    """
    Get list of all WebSocket endpoints

    Returns all available WebSocket connection URLs.
    """
    return {
        "status": "success",
        "data": {
            "master_endpoints": {
                "/ws": "Default WebSocket endpoint",
                "/ws/master": "Master endpoint with all services",
                "/ws/all": "Auto-subscribe to all services"
            },
            "data_collection_endpoints": {
                "/ws/data": "Unified data collection endpoint",
                "/ws/market_data": "Market data only",
                "/ws/whale_tracking": "Whale tracking only",
                "/ws/news": "News only",
                "/ws/sentiment": "Sentiment analysis only"
            },
            "monitoring_endpoints": {
                "/ws/monitoring": "Unified monitoring endpoint",
                "/ws/health": "Health monitoring only",
                "/ws/pool_status": "Pool manager only",
                "/ws/scheduler_status": "Scheduler only"
            },
            "integration_endpoints": {
                "/ws/integration": "Unified integration endpoint",
                "/ws/huggingface": "HuggingFace services only",
                "/ws/ai": "AI/ML services (alias for HuggingFace)",
                "/ws/persistence": "Persistence services only"
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Background Task Orchestration
# ============================================================================

async def start_all_websocket_streams():
    """
    Start all WebSocket streaming tasks

    This should be called on application startup to initialize all
    background streaming services.
    """
    logger.info("Starting all WebSocket streaming services")

    # Start all streaming tasks concurrently
    await asyncio.gather(
        start_data_collection_streams(),
        start_monitoring_streams(),
        start_integration_streams(),
        return_exceptions=True
    )

    logger.info("All WebSocket streaming services started")
