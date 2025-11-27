"""
Integrated API Router
Combines all services for a comprehensive backend API
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import uuid
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["Integrated API"])

# These will be set by the main application
config_loader = None
scheduler_service = None
persistence_service = None
websocket_service = None


def set_services(config, scheduler, persistence, websocket):
    """Set service instances"""
    global config_loader, scheduler_service, persistence_service, websocket_service
    config_loader = config
    scheduler_service = scheduler
    persistence_service = persistence
    websocket_service = websocket


# ============================================================================
# WebSocket Endpoint
# ============================================================================


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    client_id = str(uuid.uuid4())

    try:
        await websocket_service.connection_manager.connect(
            websocket, client_id, metadata={"connected_at": datetime.now().isoformat()}
        )

        # Send welcome message
        await websocket_service.connection_manager.send_personal_message(
            {
                "type": "connected",
                "client_id": client_id,
                "message": "Connected to crypto data tracker",
            },
            client_id,
        )

        # Handle messages
        while True:
            data = await websocket.receive_json()
            await websocket_service.handle_client_message(websocket, client_id, data)

    except WebSocketDisconnect:
        websocket_service.connection_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        websocket_service.connection_manager.disconnect(client_id)


# ============================================================================
# Configuration Endpoints
# ============================================================================


@router.get("/config/apis")
async def get_all_apis():
    """Get all configured APIs"""
    return {"apis": config_loader.get_all_apis(), "total": len(config_loader.apis)}


@router.get("/config/apis/{api_id}")
async def get_api(api_id: str):
    """Get specific API configuration"""
    api = config_loader.apis.get(api_id)

    if not api:
        raise HTTPException(status_code=404, detail="API not found")

    return api


@router.get("/config/categories")
async def get_categories():
    """Get all API categories"""
    categories = config_loader.get_categories()

    category_stats = {}
    for category in categories:
        apis = config_loader.get_apis_by_category(category)
        category_stats[category] = {"count": len(apis), "apis": list(apis.keys())}

    return {"categories": categories, "stats": category_stats}


@router.get("/config/apis/category/{category}")
async def get_apis_by_category(category: str):
    """Get APIs by category"""
    apis = config_loader.get_apis_by_category(category)

    return {"category": category, "apis": apis, "count": len(apis)}


@router.post("/config/apis")
async def add_custom_api(api_data: Dict[str, Any]):
    """Add a custom API"""
    try:
        success = config_loader.add_custom_api(api_data)

        if success:
            return {"status": "success", "message": "API added successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to add API")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/config/apis/{api_id}")
async def remove_api(api_id: str):
    """Remove an API"""
    success = config_loader.remove_api(api_id)

    if success:
        return {"status": "success", "message": "API removed successfully"}
    else:
        raise HTTPException(status_code=404, detail="API not found")


@router.get("/config/export")
async def export_config():
    """Export configuration to JSON"""
    filepath = f"data/exports/config_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    config_loader.export_config(filepath)

    return FileResponse(
        filepath, media_type="application/json", filename=os.path.basename(filepath)
    )


# ============================================================================
# Scheduler Endpoints
# ============================================================================


@router.get("/schedule/tasks")
async def get_all_schedules():
    """Get all scheduled tasks"""
    return scheduler_service.get_all_task_statuses()


@router.get("/schedule/tasks/{api_id}")
async def get_schedule(api_id: str):
    """Get schedule for specific API"""
    status = scheduler_service.get_task_status(api_id)

    if not status:
        raise HTTPException(status_code=404, detail="Task not found")

    return status


@router.put("/schedule/tasks/{api_id}")
async def update_schedule(
    api_id: str, interval: Optional[int] = None, enabled: Optional[bool] = None
):
    """Update schedule for an API"""
    try:
        scheduler_service.update_task_schedule(api_id, interval, enabled)

        # Notify WebSocket clients
        await websocket_service.notify_schedule_update(
            {"api_id": api_id, "interval": interval, "enabled": enabled}
        )

        return {
            "status": "success",
            "message": "Schedule updated",
            "task": scheduler_service.get_task_status(api_id),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule/tasks/{api_id}/force-update")
async def force_update(api_id: str):
    """Force immediate update for an API"""
    try:
        success = await scheduler_service.force_update(api_id)

        if success:
            return {
                "status": "success",
                "message": "Update completed",
                "task": scheduler_service.get_task_status(api_id),
            }
        else:
            raise HTTPException(status_code=500, detail="Update failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedule/export")
async def export_schedules():
    """Export schedules to JSON"""
    filepath = f"data/exports/schedules_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    scheduler_service.export_schedules(filepath)

    return FileResponse(
        filepath, media_type="application/json", filename=os.path.basename(filepath)
    )


# ============================================================================
# Data Endpoints
# ============================================================================


@router.get("/data/cached")
async def get_all_cached_data():
    """Get all cached data"""
    return persistence_service.get_all_cached_data()


@router.get("/data/cached/{api_id}")
async def get_cached_data(api_id: str):
    """Get cached data for specific API"""
    data = persistence_service.get_cached_data(api_id)

    if not data:
        raise HTTPException(status_code=404, detail="No cached data found")

    return data


@router.get("/data/history/{api_id}")
async def get_history(api_id: str, limit: int = 100):
    """Get historical data for an API"""
    history = persistence_service.get_history(api_id, limit)

    return {"api_id": api_id, "history": history, "count": len(history)}


@router.get("/data/statistics")
async def get_data_statistics():
    """Get data storage statistics"""
    return persistence_service.get_statistics()


# ============================================================================
# Export/Import Endpoints
# ============================================================================


@router.post("/export/json")
async def export_to_json(
    api_ids: Optional[List[str]] = None,
    include_history: bool = False,
    background_tasks: BackgroundTasks = None,
):
    """Export data to JSON"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"data/exports/data_export_{timestamp}.json"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        await persistence_service.export_to_json(filepath, api_ids, include_history)

        return {
            "status": "success",
            "filepath": filepath,
            "download_url": f"/api/v2/download?file={filepath}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/csv")
async def export_to_csv(api_ids: Optional[List[str]] = None, flatten: bool = True):
    """Export data to CSV"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"data/exports/data_export_{timestamp}.csv"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        await persistence_service.export_to_csv(filepath, api_ids, flatten)

        return {
            "status": "success",
            "filepath": filepath,
            "download_url": f"/api/v2/download?file={filepath}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/history/{api_id}")
async def export_history(api_id: str):
    """Export historical data for an API to CSV"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"data/exports/{api_id}_history_{timestamp}.csv"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        await persistence_service.export_history_to_csv(filepath, api_id)

        return {
            "status": "success",
            "filepath": filepath,
            "download_url": f"/api/v2/download?file={filepath}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download")
async def download_file(file: str):
    """Download exported file"""
    if not os.path.exists(file):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file, media_type="application/octet-stream", filename=os.path.basename(file)
    )


@router.post("/backup")
async def create_backup():
    """Create a backup of all data"""
    try:
        backup_file = await persistence_service.backup_all_data()

        return {
            "status": "success",
            "backup_file": backup_file,
            "download_url": f"/api/v2/download?file={backup_file}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore")
async def restore_from_backup(backup_file: str):
    """Restore data from backup"""
    try:
        success = await persistence_service.restore_from_backup(backup_file)

        if success:
            return {"status": "success", "message": "Data restored successfully"}
        else:
            raise HTTPException(status_code=500, detail="Restore failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Status Endpoints
# ============================================================================


@router.get("/status")
async def get_system_status():
    """Get overall system status"""
    return {
        "timestamp": datetime.now().isoformat(),
        "services": {
            "config_loader": {
                "apis_loaded": len(config_loader.apis),
                "categories": len(config_loader.get_categories()),
                "schedules": len(config_loader.schedules),
            },
            "scheduler": {
                "running": scheduler_service.running,
                "total_tasks": len(scheduler_service.tasks),
                "realtime_tasks": len(scheduler_service.realtime_tasks),
                "cache_size": len(scheduler_service.data_cache),
            },
            "persistence": {
                "cached_apis": len(persistence_service.cache),
                "apis_with_history": len(persistence_service.history),
                "total_history_records": sum(len(h) for h in persistence_service.history.values()),
            },
            "websocket": websocket_service.get_stats(),
        },
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "config": config_loader is not None,
            "scheduler": scheduler_service is not None and scheduler_service.running,
            "persistence": persistence_service is not None,
            "websocket": websocket_service is not None,
        },
    }


# ============================================================================
# Cleanup Endpoints
# ============================================================================


@router.post("/cleanup/cache")
async def clear_cache():
    """Clear all cached data"""
    persistence_service.clear_cache()
    return {"status": "success", "message": "Cache cleared"}


@router.post("/cleanup/history")
async def clear_history(api_id: Optional[str] = None):
    """Clear history"""
    persistence_service.clear_history(api_id)

    if api_id:
        return {"status": "success", "message": f"History cleared for {api_id}"}
    else:
        return {"status": "success", "message": "All history cleared"}


@router.post("/cleanup/old-data")
async def cleanup_old_data(days: int = 7):
    """Remove data older than specified days"""
    removed = await persistence_service.cleanup_old_data(days)

    return {
        "status": "success",
        "message": f"Cleaned up {removed} old records",
        "removed_count": removed,
    }
