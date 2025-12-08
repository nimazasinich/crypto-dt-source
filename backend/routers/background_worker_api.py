"""
Background Worker Management API
Provides endpoints to manage and monitor the background data collection worker
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

from backend.workers.background_collector_worker import get_worker_instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/worker", tags=["Background Worker"])


@router.get("/status")
async def get_worker_status():
    """
    Get background worker status and statistics
    
    Returns:
        Worker status including collection stats, schedules, and recent errors
    """
    try:
        worker = await get_worker_instance()
        stats = worker.get_stats()
        
        return JSONResponse(content={
            "success": True,
            "worker_status": stats,
            "message_fa": "وضعیت Worker به موفقیت دریافت شد",
            "message_en": "Worker status retrieved successfully"
        })
        
    except Exception as e:
        logger.error(f"Error getting worker status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_worker():
    """
    Start the background worker
    
    Returns:
        Success status
    """
    try:
        worker = await get_worker_instance()
        
        if worker.is_running:
            return JSONResponse(content={
                "success": False,
                "message_fa": "Worker در حال اجرا است",
                "message_en": "Worker is already running"
            })
        
        worker.start()
        
        return JSONResponse(content={
            "success": True,
            "message_fa": "Worker با موفقیت راه‌اندازی شد",
            "message_en": "Worker started successfully",
            "schedules": {
                "ui_data": "Every 5 minutes",
                "historical_data": "Every 15 minutes"
            }
        })
        
    except Exception as e:
        logger.error(f"Error starting worker: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_worker():
    """
    Stop the background worker
    
    Returns:
        Success status
    """
    try:
        worker = await get_worker_instance()
        
        if not worker.is_running:
            return JSONResponse(content={
                "success": False,
                "message_fa": "Worker در حال اجرا نیست",
                "message_en": "Worker is not running"
            })
        
        worker.stop()
        
        return JSONResponse(content={
            "success": True,
            "message_fa": "Worker با موفقیت متوقف شد",
            "message_en": "Worker stopped successfully"
        })
        
    except Exception as e:
        logger.error(f"Error stopping worker: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/force-collection")
async def force_collection(collection_type: str = "both"):
    """
    Force immediate data collection
    
    Args:
        collection_type: Type of collection ('ui', 'historical', or 'both')
    
    Returns:
        Success status
    """
    try:
        if collection_type not in ['ui', 'historical', 'both']:
            raise HTTPException(
                status_code=400,
                detail="Invalid collection_type. Must be 'ui', 'historical', or 'both'"
            )
        
        worker = await get_worker_instance()
        
        if not worker.is_running:
            raise HTTPException(
                status_code=400,
                detail="Worker is not running. Start the worker first."
            )
        
        worker.force_collection(collection_type)
        
        return JSONResponse(content={
            "success": True,
            "message_fa": f"جمع‌آوری {collection_type} با موفقیت آغاز شد",
            "message_en": f"Manual {collection_type} collection started successfully",
            "collection_type": collection_type
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error forcing collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_collection_stats():
    """
    Get detailed collection statistics
    
    Returns:
        Detailed statistics about data collections
    """
    try:
        worker = await get_worker_instance()
        stats = worker.get_stats()
        
        return JSONResponse(content={
            "success": True,
            "statistics": {
                "total_ui_collections": stats['ui_collections'],
                "total_historical_collections": stats['historical_collections'],
                "total_records_saved": stats['total_records_saved'],
                "last_ui_collection": stats['last_ui_collection'],
                "last_historical_collection": stats['last_historical_collection'],
                "average_records_per_ui_collection": (
                    stats['total_records_saved'] / stats['ui_collections']
                    if stats['ui_collections'] > 0 else 0
                ),
                "average_records_per_historical_collection": (
                    stats['total_records_saved'] / stats['historical_collections']
                    if stats['historical_collections'] > 0 else 0
                )
            },
            "recent_errors": stats['recent_errors'],
            "message_fa": "آمار جمع‌آوری داده‌ها",
            "message_en": "Data collection statistics"
        })
        
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules")
async def get_schedules():
    """
    Get current collection schedules
    
    Returns:
        Schedule information for all collection jobs
    """
    try:
        worker = await get_worker_instance()
        stats = worker.get_stats()
        
        return JSONResponse(content={
            "success": True,
            "schedules": stats['scheduler_jobs'],
            "message_fa": "زمان‌بندی جمع‌آوری داده‌ها",
            "message_en": "Data collection schedules"
        })
        
    except Exception as e:
        logger.error(f"Error getting schedules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def worker_health_check():
    """
    Health check for background worker
    
    Returns:
        Health status
    """
    try:
        worker = await get_worker_instance()
        
        is_healthy = worker.is_running
        
        return JSONResponse(content={
            "success": True,
            "healthy": is_healthy,
            "status": "running" if is_healthy else "stopped",
            "message_fa": "Worker سالم است" if is_healthy else "Worker متوقف است",
            "message_en": "Worker is healthy" if is_healthy else "Worker is stopped"
        })
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "healthy": False,
                "status": "error",
                "error": str(e),
                "message_fa": "خطا در بررسی سلامت Worker",
                "message_en": "Error checking worker health"
            }
        )
