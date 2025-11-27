#!/usr/bin/env python3
"""
Synchronization API Router
Provides REST API endpoints for triggering and monitoring synchronization
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from typing import Optional
from pydantic import BaseModel
import logging
from datetime import datetime
import os

from backend.services.sync_orchestrator import sync_orchestrator
from backend.services.sync_database_updater import sync_db_updater
from backend.services.github_sync_service import github_sync_service
from backend.services.huggingface_sync_service import huggingface_sync_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/sync",
    tags=["Synchronization"]
)


class SyncRequest(BaseModel):
    """Sync request model"""
    branch: str = "main"
    commit_message: str = "Sync with Hugging Face models and datasets"


# Global variable to track sync status
sync_status = {
    "is_running": False,
    "last_sync": None,
    "last_result": None
}


async def run_sync_background(branch: str, commit_message: str):
    """Run sync in background"""
    global sync_status
    
    try:
        sync_status["is_running"] = True
        
        # Run complete sync
        result = await sync_orchestrator.run_complete_sync(
            branch=branch,
            commit_message=commit_message
        )
        
        # Update database
        if result.get("hf_models"):
            models_data = result["hf_models"].get("models", [])
            sync_db_updater.update_models(models_data)
        
        if result.get("hf_datasets"):
            datasets_data = result["hf_datasets"].get("datasets", [])
            sync_db_updater.update_datasets(datasets_data)
        
        # Record history
        sync_db_updater.record_sync_history(result)
        
        sync_status["last_sync"] = datetime.utcnow().isoformat()
        sync_status["last_result"] = {
            "success": result.get("success"),
            "duration": result.get("duration_seconds"),
            "summary": result.get("summary")
        }
    
    except Exception as e:
        logger.error(f"❌ Background sync failed: {e}")
        sync_status["last_result"] = {
            "success": False,
            "error": str(e)
        }
    finally:
        sync_status["is_running"] = False


@router.post("/run")
async def run_sync(
    request: SyncRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger complete synchronization (runs in background)
    
    This endpoint triggers a complete sync workflow:
    1. Fetch GitHub commits
    2. Sync HuggingFace models
    3. Sync HuggingFace datasets
    4. Perform git operations (pull, add, commit, push)
    5. Update database
    6. Generate report
    
    Example:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/sync/run" \
      -H "Content-Type: application/json" \
      -d '{"branch": "main", "commit_message": "Sync update"}'
    ```
    """
    if sync_status["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="Sync is already running. Please wait for it to complete."
        )
    
    # Start sync in background
    background_tasks.add_task(
        run_sync_background,
        request.branch,
        request.commit_message
    )
    
    return {
        "success": True,
        "message": "Synchronization started in background",
        "branch": request.branch,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status")
async def get_sync_status():
    """
    Get current sync status
    
    Returns information about:
    - Is sync currently running?
    - When was the last sync?
    - What was the result of the last sync?
    """
    return {
        "success": True,
        "status": sync_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/github/commits")
async def get_github_commits(
    branch: str = Query("main", description="Branch name"),
    limit: int = Query(10, description="Number of commits")
):
    """
    Get latest GitHub commits
    
    Example:
    ```bash
    curl "http://localhost:8000/api/v1/sync/github/commits?branch=main&limit=10"
    ```
    """
    try:
        result = await github_sync_service.get_latest_commits(branch=branch, limit=limit)
        return result
    except Exception as e:
        logger.error(f"❌ Failed to get commits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hf/models")
async def get_hf_models():
    """
    Get HuggingFace models information
    
    Fetches information about all configured models from HuggingFace.
    """
    try:
        result = await huggingface_sync_service.sync_models()
        return result
    except Exception as e:
        logger.error(f"❌ Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hf/datasets")
async def get_hf_datasets():
    """
    Get HuggingFace datasets information
    
    Fetches information about all configured datasets from HuggingFace.
    """
    try:
        result = await huggingface_sync_service.sync_datasets()
        return result
    except Exception as e:
        logger.error(f"❌ Failed to get datasets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database/models")
async def get_db_models():
    """
    Get synced models from database
    
    Returns all models that have been synchronized and stored in the database.
    """
    try:
        models = sync_db_updater.get_synced_models()
        return {
            "success": True,
            "models": models,
            "count": len(models),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get models from database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database/datasets")
async def get_db_datasets():
    """
    Get synced datasets from database
    
    Returns all datasets that have been synchronized and stored in the database.
    """
    try:
        datasets = sync_db_updater.get_synced_datasets()
        return {
            "success": True,
            "datasets": datasets,
            "count": len(datasets),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get datasets from database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_sync_history(
    limit: int = Query(10, description="Number of history entries")
):
    """
    Get synchronization history
    
    Returns the history of past synchronization operations.
    
    Example:
    ```bash
    curl "http://localhost:8000/api/v1/sync/history?limit=10"
    ```
    """
    try:
        history = sync_db_updater.get_sync_history(limit=limit)
        return {
            "success": True,
            "history": history,
            "count": len(history),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get sync history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports")
async def get_sync_reports():
    """
    Get list of available sync reports
    
    Returns all generated sync report files.
    """
    try:
        report_dir = "/workspace/sync_reports"
        
        if not os.path.exists(report_dir):
            return {
                "success": True,
                "reports": [],
                "count": 0
            }
        
        reports = []
        for filename in os.listdir(report_dir):
            if filename.startswith("sync_report_") and filename.endswith(".txt"):
                filepath = os.path.join(report_dir, filename)
                stat = os.stat(filepath)
                reports.append({
                    "filename": filename,
                    "path": filepath,
                    "size_bytes": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
        
        # Sort by creation time (newest first)
        reports.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "success": True,
            "reports": reports,
            "count": len(reports),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/latest")
async def get_latest_report():
    """
    Get the latest sync report content
    
    Returns the content of the most recent sync report as a file download.
    """
    try:
        report_dir = "/workspace/sync_reports"
        
        if not os.path.exists(report_dir):
            raise HTTPException(status_code=404, detail="No reports found")
        
        # Get all report files
        reports = [
            f for f in os.listdir(report_dir)
            if f.startswith("sync_report_") and f.endswith(".txt")
        ]
        
        if not reports:
            raise HTTPException(status_code=404, detail="No reports found")
        
        # Sort by modification time (newest first)
        reports.sort(key=lambda x: os.path.getmtime(os.path.join(report_dir, x)), reverse=True)
        
        latest_report = reports[0]
        filepath = os.path.join(report_dir, latest_report)
        
        return FileResponse(
            filepath,
            media_type="text/plain",
            filename=latest_report
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get latest report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Export router
__all__ = ["router"]
