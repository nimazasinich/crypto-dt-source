#!/usr/bin/env python3
"""
Source Health Monitoring API
Provides real-time health status of all data sources
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/source-health", tags=["Source Health"])


@router.get("/status")
async def get_all_sources_health() -> Dict[str, Any]:
    """
    Get health status of all tracked data sources
    
    Returns:
        Real-time health metrics for all sources
    """
    try:
        from backend.core.safe_http_client import health_tracker
        
        sources = health_tracker.get_all_sources()
        
        # Calculate aggregate metrics
        total_sources = len(sources)
        healthy_count = sum(1 for s in sources.values() if s["status"] == "healthy")
        degraded_count = sum(1 for s in sources.values() if s["status"] == "degraded")
        offline_count = sum(1 for s in sources.values() if s["status"] == "offline")
        unknown_count = sum(1 for s in sources.values() if s["status"] == "unknown")
        
        # Calculate overall health percentage
        health_score = 0
        if total_sources > 0:
            health_score = int((healthy_count / total_sources) * 100)
        
        return {
            "success": True,
            "summary": {
                "total": total_sources,
                "healthy": healthy_count,
                "degraded": degraded_count,
                "offline": offline_count,
                "unknown": unknown_count,
                "health_score": health_score
            },
            "sources": sources,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error getting source health: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Failed to get source health",
                "detail": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.get("/status/{source_name}")
async def get_source_health(source_name: str) -> Dict[str, Any]:
    """
    Get health status for a specific source
    
    Args:
        source_name: Name of the data source
    
    Returns:
        Detailed health metrics for the source
    """
    try:
        from backend.core.safe_http_client import health_tracker
        
        source = health_tracker.get_source_health(source_name)
        
        # Convert datetime objects to ISO format
        result = {
            **source,
            "last_success": source["last_success"].isoformat() + "Z" if source["last_success"] else None,
            "last_failure": source["last_failure"].isoformat() + "Z" if source["last_failure"] else None,
            "created_at": source["created_at"].isoformat() + "Z" if source["created_at"] else None,
        }
        
        # Convert enum to string
        if "status" in result:
            result["status"] = result["status"].value if hasattr(result["status"], "value") else result["status"]
        
        return {
            "success": True,
            "source_name": source_name,
            "health": result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error getting health for {source_name}: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to get health for {source_name}",
                "detail": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post("/reset/{source_name}")
async def reset_source_health(source_name: str) -> Dict[str, Any]:
    """
    Reset health tracking for a specific source
    
    Args:
        source_name: Name of the data source to reset
    
    Returns:
        Confirmation of reset
    """
    try:
        from backend.core.safe_http_client import health_tracker
        
        health_tracker.reset_source(source_name)
        
        return {
            "success": True,
            "message": f"Health tracking reset for {source_name}",
            "source_name": source_name,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error resetting health for {source_name}: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to reset health for {source_name}",
                "detail": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post("/reset-all")
async def reset_all_health() -> Dict[str, Any]:
    """
    Reset health tracking for all sources
    
    Returns:
        Confirmation of reset
    """
    try:
        from backend.core.safe_http_client import health_tracker
        
        sources = list(health_tracker.get_all_sources().keys())
        
        for source in sources:
            health_tracker.reset_source(source)
        
        return {
            "success": True,
            "message": f"Health tracking reset for {len(sources)} sources",
            "reset_count": len(sources),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error resetting all health: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Failed to reset all health",
                "detail": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


logger.info("✅ Source Health API Router loaded")
