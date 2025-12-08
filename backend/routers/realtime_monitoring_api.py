#!/usr/bin/env python3
"""
Real-Time System Monitoring API
Provides real-time data for animated monitoring dashboard
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import json
import sqlite3
from pathlib import Path

from backend.services.ai_models_monitor import db as ai_models_db, monitor as ai_monitor, agent as ai_agent
from database.db_manager import db_manager
from monitoring.source_pool_manager import SourcePoolManager
from utils.logger import setup_logger

logger = setup_logger("realtime_monitoring")

router = APIRouter(prefix="/api/monitoring", tags=["Real-Time Monitoring"])

# Track active WebSocket connections
active_connections: List[WebSocket] = []

# Request tracking (in-memory for real-time)
request_log: List[Dict[str, Any]] = []
MAX_REQUEST_LOG = 100


def add_request_log(entry: Dict[str, Any]):
    """Add request to log"""
    entry['timestamp'] = datetime.now().isoformat()
    request_log.insert(0, entry)
    if len(request_log) > MAX_REQUEST_LOG:
        request_log.pop()


@router.get("/status")
async def get_system_status():
    """
    Get comprehensive system status for monitoring dashboard
    """
    try:
        # AI Models Status
        ai_models = ai_models_db.get_all_models()
        ai_models_status = {
            "total": len(ai_models),
            "available": sum(1 for m in ai_models if m.get('success_rate', 0) > 50),
            "failed": sum(1 for m in ai_models if m.get('success_rate', 0) == 0),
            "loading": 0,
            "models": [
                {
                    "id": m['model_id'],
                    "status": "available" if m.get('success_rate', 0) > 50 else "failed",
                    "success_rate": m.get('success_rate', 0) or 0
                }
                for m in ai_models
            ]
        }
        
        # Data Sources Status
        session = db_manager.get_session()
        try:
            from database.models import Provider, SourcePool, PoolMember
            providers = session.query(Provider).all()
            pools = session.query(SourcePool).all()
            
            sources_status = {
                "total": len(providers),
                "active": 0,
                "inactive": 0,
                "categories": {},
                "pools": len(pools),
                "sources": []
            }
            
            for provider in providers:
                category = provider.category or "unknown"
                if category not in sources_status["categories"]:
                    sources_status["categories"][category] = {"total": 0, "active": 0}
                
                sources_status["categories"][category]["total"] += 1
                sources_status["sources"].append({
                    "id": provider.id,
                    "name": provider.name,
                    "category": category,
                    "status": "active",  # TODO: Check actual status
                    "endpoint": provider.endpoint_url
                })
                sources_status["active"] += 1
        finally:
            session.close()
        
        # Database Status
        db_status = {
            "online": True,
            "last_check": datetime.now().isoformat(),
            "ai_models_db": Path("data/ai_models.db").exists(),
            "main_db": True  # Assume online if we got session
        }
        
        # Recent Requests
        recent_requests = request_log[:20]
        
        # System Stats
        stats = {
            "total_sources": sources_status["total"],
            "active_sources": sources_status["active"],
            "total_models": ai_models_status["total"],
            "available_models": ai_models_status["available"],
            "requests_last_minute": len([r for r in recent_requests 
                                        if datetime.fromisoformat(r['timestamp']) > datetime.now() - timedelta(minutes=1)]),
            "requests_last_hour": len([r for r in recent_requests 
                                      if datetime.fromisoformat(r['timestamp']) > datetime.now() - timedelta(hours=1)])
        }
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "ai_models": ai_models_status,
            "data_sources": sources_status,
            "database": db_status,
            "recent_requests": recent_requests,
            "stats": stats,
            "agent_running": ai_agent.running if hasattr(ai_agent, 'running') else False
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/sources/detailed")
async def get_detailed_sources():
    """Get detailed source information with endpoints"""
    try:
        session = db_manager.get_session()
        try:
            from database.models import Provider, SourcePool, PoolMember
            providers = session.query(Provider).all()
            
            sources = []
            for provider in providers:
                sources.append({
                    "id": provider.id,
                    "name": provider.name,
                    "category": provider.category,
                    "endpoint": provider.endpoint_url,
                    "status": "active",  # TODO: Check health
                    "priority": provider.priority_tier,
                    "requires_key": provider.requires_key
                })
            
            return {
                "success": True,
                "sources": sources,
                "total": len(sources)
            }
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error getting detailed sources: {e}")
        return {"success": False, "error": str(e)}


@router.get("/requests/recent")
async def get_recent_requests(limit: int = 50):
    """Get recent API requests"""
    return {
        "success": True,
        "requests": request_log[:limit],
        "total": len(request_log)
    }


@router.post("/requests/log")
async def log_request(request_data: Dict[str, Any]):
    """Log an API request (called by middleware or other endpoints)"""
    add_request_log(request_data)
    return {"success": True}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time monitoring updates
    """
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"WebSocket connected. Total connections: {len(active_connections)}")
    
    try:
        # Send initial status
        status = await get_system_status()
        await websocket.send_json(status)
        
        # Keep connection alive and send updates
        while True:
            # Wait for client message (ping)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if data == "ping":
                    # Send current status
                    status = await get_system_status()
                    await websocket.send_json(status)
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({"type": "heartbeat", "timestamp": datetime.now().isoformat()})
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info(f"WebSocket removed. Total connections: {len(active_connections)}")


async def broadcast_update(data: Dict[str, Any]):
    """Broadcast update to all connected WebSocket clients"""
    if not active_connections:
        return
    
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except Exception as e:
            logger.warning(f"Failed to send to WebSocket: {e}")
            disconnected.append(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)

