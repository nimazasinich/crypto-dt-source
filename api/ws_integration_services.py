"""
WebSocket API for Integration Services

This module provides WebSocket endpoints for integration services
including HuggingFace AI models and persistence operations.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

from backend.services.ws_service_manager import ws_manager, ServiceType
from backend.services.hf_registry import HFRegistry
from backend.services.hf_client import HFClient
from backend.services.persistence_service import PersistenceService
from config import Config

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Integration Service Handlers
# ============================================================================


class IntegrationStreamers:
    """Handles data streaming for integration services"""

    def __init__(self):
        self.config = Config()
        try:
            self.hf_registry = HFRegistry()
        except:
            self.hf_registry = None
            logger.warning("HFRegistry not available")

        try:
            self.hf_client = HFClient()
        except:
            self.hf_client = None
            logger.warning("HFClient not available")

        try:
            self.persistence_service = PersistenceService()
        except:
            self.persistence_service = None
            logger.warning("PersistenceService not available")

    # ========================================================================
    # HuggingFace Streaming
    # ========================================================================

    async def stream_hf_registry_status(self):
        """Stream HuggingFace registry status"""
        if not self.hf_registry:
            return None

        try:
            status = self.hf_registry.get_status()
            if status:
                return {
                    "total_models": status.get("total_models", 0),
                    "total_datasets": status.get("total_datasets", 0),
                    "available_models": status.get("available_models", []),
                    "available_datasets": status.get("available_datasets", []),
                    "last_refresh": status.get("last_refresh"),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming HF registry status: {e}")
            return None

    async def stream_hf_model_usage(self):
        """Stream HuggingFace model usage statistics"""
        if not self.hf_client:
            return None

        try:
            usage = self.hf_client.get_usage_stats()
            if usage:
                return {
                    "total_requests": usage.get("total_requests", 0),
                    "successful_requests": usage.get("successful_requests", 0),
                    "failed_requests": usage.get("failed_requests", 0),
                    "average_latency": usage.get("average_latency"),
                    "model_usage": usage.get("model_usage", {}),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming HF model usage: {e}")
            return None

    async def stream_sentiment_results(self):
        """Stream real-time sentiment analysis results"""
        if not self.hf_client:
            return None

        try:
            # This would stream sentiment results as they're processed
            results = self.hf_client.get_recent_results()
            if results:
                return {"sentiment_results": results, "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error streaming sentiment results: {e}")
            return None

    async def stream_model_events(self):
        """Stream model loading and unloading events"""
        if not self.hf_registry:
            return None

        try:
            events = self.hf_registry.get_recent_events()
            if events:
                return {"model_events": events, "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error streaming model events: {e}")
            return None

    # ========================================================================
    # Persistence Service Streaming
    # ========================================================================

    async def stream_persistence_status(self):
        """Stream persistence service status"""
        if not self.persistence_service:
            return None

        try:
            status = self.persistence_service.get_status()
            if status:
                return {
                    "storage_location": status.get("storage_location"),
                    "total_records": status.get("total_records", 0),
                    "storage_size": status.get("storage_size"),
                    "last_save": status.get("last_save"),
                    "active_writers": status.get("active_writers", 0),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            logger.error(f"Error streaming persistence status: {e}")
            return None

    async def stream_save_events(self):
        """Stream data save events"""
        if not self.persistence_service:
            return None

        try:
            events = self.persistence_service.get_recent_saves()
            if events:
                return {"save_events": events, "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error streaming save events: {e}")
            return None

    async def stream_export_progress(self):
        """Stream export operation progress"""
        if not self.persistence_service:
            return None

        try:
            progress = self.persistence_service.get_export_progress()
            if progress:
                return {"export_operations": progress, "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error streaming export progress: {e}")
            return None

    async def stream_backup_events(self):
        """Stream backup creation events"""
        if not self.persistence_service:
            return None

        try:
            backups = self.persistence_service.get_recent_backups()
            if backups:
                return {"backup_events": backups, "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Error streaming backup events: {e}")
            return None


# Global instance
integration_streamers = IntegrationStreamers()


# ============================================================================
# Background Streaming Tasks
# ============================================================================


async def start_integration_streams():
    """Start all integration stream tasks"""
    logger.info("Starting integration WebSocket streams")

    tasks = [
        # HuggingFace Registry
        asyncio.create_task(
            ws_manager.start_service_stream(
                ServiceType.HUGGINGFACE,
                integration_streamers.stream_hf_registry_status,
                interval=60.0,  # 1 minute updates
            )
        ),
        # Persistence Service
        asyncio.create_task(
            ws_manager.start_service_stream(
                ServiceType.PERSISTENCE,
                integration_streamers.stream_persistence_status,
                interval=30.0,  # 30 second updates
            )
        ),
    ]

    await asyncio.gather(*tasks, return_exceptions=True)


# ============================================================================
# WebSocket Endpoints
# ============================================================================


@router.websocket("/ws/integration")
async def websocket_integration_endpoint(websocket: WebSocket):
    """
    Unified WebSocket endpoint for all integration services

    Connection URL: ws://host:port/ws/integration

    After connecting, send subscription messages:
    {
        "action": "subscribe",
        "service": "huggingface" | "persistence" | "all"
    }

    To unsubscribe:
    {
        "action": "unsubscribe",
        "service": "service_name"
    }
    """
    connection = await ws_manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)

    except WebSocketDisconnect:
        logger.info(f"Integration client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"Integration WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)


@router.websocket("/ws/huggingface")
async def websocket_huggingface(websocket: WebSocket):
    """
    Dedicated WebSocket endpoint for HuggingFace services

    Auto-subscribes to huggingface service
    """
    connection = await ws_manager.connect(websocket)
    connection.subscribe(ServiceType.HUGGINGFACE)

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)
    except WebSocketDisconnect:
        logger.info(f"HuggingFace client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"HuggingFace WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)


@router.websocket("/ws/persistence")
async def websocket_persistence(websocket: WebSocket):
    """
    Dedicated WebSocket endpoint for persistence service

    Auto-subscribes to persistence service
    """
    connection = await ws_manager.connect(websocket)
    connection.subscribe(ServiceType.PERSISTENCE)

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)
    except WebSocketDisconnect:
        logger.info(f"Persistence client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"Persistence WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)


@router.websocket("/ws/ai")
async def websocket_ai(websocket: WebSocket):
    """
    Dedicated WebSocket endpoint for AI/ML operations (alias for HuggingFace)

    Auto-subscribes to huggingface service
    """
    connection = await ws_manager.connect(websocket)
    connection.subscribe(ServiceType.HUGGINGFACE)

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)
    except WebSocketDisconnect:
        logger.info(f"AI client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"AI WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)
