"""
Resources Endpoint - API router for resource statistics
"""
from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/resources", tags=["resources"])

@router.get("/stats")
async def resources_stats() -> Dict[str, Any]:
    """Get resource statistics"""
    return {
        "total": 0,
        "active": 0,
        "categories": [],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@router.get("/list")
async def resources_list() -> Dict[str, Any]:
    """Get list of all resources"""
    return {
        "resources": [],
        "total": 0,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

