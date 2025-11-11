"""
WebSocket API for Monitoring Services

This module provides WebSocket endpoints for real-time monitoring data
including health checks, pool management, and scheduler status.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

from backend.services.ws_service_manager import ws_manager, ServiceType
from monitoring.health_checker import HealthChecker
from monitoring.source_pool_manager import SourcePoolManager
from monitoring.scheduler import TaskScheduler
from config import Config

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Monitoring Service Handlers
# ============================================================================

class MonitoringStreamers:
    """Handles data streaming for all monitoring services"""

    def __init__(self):
        self.config = Config()
        self.health_checker = HealthChecker()
        try:
            self.pool_manager = SourcePoolManager()
        except:
            self.pool_manager = None
            logger.warning("SourcePoolManager not available")

        try:
            self.scheduler = TaskScheduler()
        except:
            self.scheduler = None
            logger.warning("TaskScheduler not available")

    # ========================================================================
    # Health Checker Streaming
    # ========================================================================

    async def stream_health_status(self):
        """Stream health check status for all providers"""
        try:
            health_data = await self.health_checker.check_all_providers()
            if health_data:
                return {
                    "overall_health": health_data.get("overall_health", "unknown"),
                    "healthy_count": health_data.get("healthy_count", 0),
                    "unhealthy_count": health_data.get("unhealthy_count", 0),
                    "total_providers": health_data.get("total_providers", 0),
                    "providers": health_data.get("providers", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error streaming health status: {e}")
            return None

    async def stream_provider_health(self):
        """Stream individual provider health changes"""
        try:
            health_data = await self.health_checker.check_all_providers()
            if health_data and "providers" in health_data:
                # Filter for providers with issues
                issues = {
                    name: status
                    for name, status in health_data["providers"].items()
                    if status.get("status") != "healthy"
                }

                if issues:
                    return {
                        "providers_with_issues": issues,
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            logger.error(f"Error streaming provider health: {e}")
            return None

    async def stream_health_alerts(self):
        """Stream health alerts for critical issues"""
        try:
            health_data = await self.health_checker.check_all_providers()
            if health_data:
                critical_issues = []

                for name, status in health_data.get("providers", {}).items():
                    if status.get("status") == "critical":
                        critical_issues.append({
                            "provider": name,
                            "status": status,
                            "alert_level": "critical"
                        })
                    elif status.get("status") == "unhealthy":
                        critical_issues.append({
                            "provider": name,
                            "status": status,
                            "alert_level": "warning"
                        })

                if critical_issues:
                    return {
                        "alerts": critical_issues,
                        "total_alerts": len(critical_issues),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            logger.error(f"Error streaming health alerts: {e}")
            return None

    # ========================================================================
    # Pool Manager Streaming
    # ========================================================================

    async def stream_pool_status(self):
        """Stream source pool management status"""
        if not self.pool_manager:
            return None

        try:
            pool_data = self.pool_manager.get_status()
            if pool_data:
                return {
                    "pools": pool_data.get("pools", {}),
                    "active_sources": pool_data.get("active_sources", []),
                    "inactive_sources": pool_data.get("inactive_sources", []),
                    "failover_count": pool_data.get("failover_count", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error streaming pool status: {e}")
            return None

    async def stream_failover_events(self):
        """Stream failover events"""
        if not self.pool_manager:
            return None

        try:
            events = self.pool_manager.get_recent_failovers()
            if events:
                return {
                    "failover_events": events,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error streaming failover events: {e}")
            return None

    async def stream_source_health(self):
        """Stream individual source health in pools"""
        if not self.pool_manager:
            return None

        try:
            health_data = self.pool_manager.get_source_health()
            if health_data:
                return {
                    "source_health": health_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error streaming source health: {e}")
            return None

    # ========================================================================
    # Scheduler Streaming
    # ========================================================================

    async def stream_scheduler_status(self):
        """Stream scheduler status"""
        if not self.scheduler:
            return None

        try:
            status_data = self.scheduler.get_status()
            if status_data:
                return {
                    "running": status_data.get("running", False),
                    "total_jobs": status_data.get("total_jobs", 0),
                    "active_jobs": status_data.get("active_jobs", 0),
                    "jobs": status_data.get("jobs", []),
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error streaming scheduler status: {e}")
            return None

    async def stream_job_executions(self):
        """Stream job execution events"""
        if not self.scheduler:
            return None

        try:
            executions = self.scheduler.get_recent_executions()
            if executions:
                return {
                    "executions": executions,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error streaming job executions: {e}")
            return None

    async def stream_job_failures(self):
        """Stream job failures"""
        if not self.scheduler:
            return None

        try:
            failures = self.scheduler.get_recent_failures()
            if failures:
                return {
                    "failures": failures,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error streaming job failures: {e}")
            return None


# Global instance
monitoring_streamers = MonitoringStreamers()


# ============================================================================
# Background Streaming Tasks
# ============================================================================

async def start_monitoring_streams():
    """Start all monitoring stream tasks"""
    logger.info("Starting monitoring WebSocket streams")

    tasks = [
        # Health Checker
        asyncio.create_task(ws_manager.start_service_stream(
            ServiceType.HEALTH_CHECKER,
            monitoring_streamers.stream_health_status,
            interval=30.0  # 30 second updates
        )),

        # Pool Manager
        asyncio.create_task(ws_manager.start_service_stream(
            ServiceType.POOL_MANAGER,
            monitoring_streamers.stream_pool_status,
            interval=20.0  # 20 second updates
        )),

        # Scheduler
        asyncio.create_task(ws_manager.start_service_stream(
            ServiceType.SCHEDULER,
            monitoring_streamers.stream_scheduler_status,
            interval=15.0  # 15 second updates
        )),
    ]

    await asyncio.gather(*tasks, return_exceptions=True)


# ============================================================================
# WebSocket Endpoints
# ============================================================================

@router.websocket("/ws/monitoring")
async def websocket_monitoring_endpoint(websocket: WebSocket):
    """
    Unified WebSocket endpoint for all monitoring services

    Connection URL: ws://host:port/ws/monitoring

    After connecting, send subscription messages:
    {
        "action": "subscribe",
        "service": "health_checker" | "pool_manager" | "scheduler" | "all"
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
        logger.info(f"Monitoring client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"Monitoring WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)


@router.websocket("/ws/health")
async def websocket_health(websocket: WebSocket):
    """
    Dedicated WebSocket endpoint for health monitoring

    Auto-subscribes to health_checker service
    """
    connection = await ws_manager.connect(websocket)
    connection.subscribe(ServiceType.HEALTH_CHECKER)

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)
    except WebSocketDisconnect:
        logger.info(f"Health monitoring client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"Health monitoring WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)


@router.websocket("/ws/pool_status")
async def websocket_pool_status(websocket: WebSocket):
    """
    Dedicated WebSocket endpoint for pool manager status

    Auto-subscribes to pool_manager service
    """
    connection = await ws_manager.connect(websocket)
    connection.subscribe(ServiceType.POOL_MANAGER)

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)
    except WebSocketDisconnect:
        logger.info(f"Pool status client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"Pool status WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)


@router.websocket("/ws/scheduler_status")
async def websocket_scheduler_status(websocket: WebSocket):
    """
    Dedicated WebSocket endpoint for scheduler status

    Auto-subscribes to scheduler service
    """
    connection = await ws_manager.connect(websocket)
    connection.subscribe(ServiceType.SCHEDULER)

    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_client_message(connection, data)
    except WebSocketDisconnect:
        logger.info(f"Scheduler status client disconnected: {connection.client_id}")
    except Exception as e:
        logger.error(f"Scheduler status WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(connection.client_id)
