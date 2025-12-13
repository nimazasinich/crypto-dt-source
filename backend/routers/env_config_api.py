#!/usr/bin/env python3
"""
Environment Configuration API
Provides API endpoints for viewing configuration status
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["Configuration"])


@router.get("/features")
async def get_features_status() -> Dict[str, Any]:
    """
    Get status of all features
    
    Returns:
        Dictionary of features and their enabled status
    """
    try:
        from backend.core.env_config import env_config
        
        features = env_config.get_all_features()
        
        enabled_count = sum(1 for enabled in features.values() if enabled)
        total_count = len(features)
        
        return {
            "success": True,
            "summary": {
                "total": total_count,
                "enabled": enabled_count,
                "disabled": total_count - enabled_count
            },
            "features": features,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error getting features status: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Failed to get features status",
                "detail": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.get("/features/{feature_name}")
async def get_feature_config(feature_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific feature
    
    Args:
        feature_name: Name of the feature
    
    Returns:
        Feature configuration details
    """
    try:
        from backend.core.env_config import env_config
        
        config = env_config.get_feature_config(feature_name)
        
        return {
            "success": True,
            "feature": feature_name,
            **config,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error getting feature config for {feature_name}: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to get feature config for {feature_name}",
                "detail": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.get("/missing")
async def get_missing_variables() -> Dict[str, Any]:
    """
    Get list of missing environment variables
    
    Returns:
        List of missing variables
    """
    try:
        from backend.core.env_config import env_config
        
        missing = env_config.get_missing_vars()
        
        return {
            "success": True,
            "count": len(missing),
            "missing_variables": missing,
            "recommendation": "Set these variables in .env file to enable additional features",
            "reference": "See .env.example for expected variable names",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error getting missing variables: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Failed to get missing variables",
                "detail": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post("/reload")
async def reload_configuration() -> Dict[str, Any]:
    """
    Reload configuration from environment
    
    Returns:
        Confirmation of reload
    """
    try:
        from backend.core.env_config import env_config
        
        env_config.reload()
        
        features = env_config.get_all_features()
        enabled_count = sum(1 for enabled in features.values() if enabled)
        
        return {
            "success": True,
            "message": "Configuration reloaded successfully",
            "summary": {
                "total_features": len(features),
                "enabled_features": enabled_count
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error reloading configuration: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Failed to reload configuration",
                "detail": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


logger.info("✅ Environment Configuration API Router loaded")
