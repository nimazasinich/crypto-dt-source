#!/usr/bin/env python3
"""
Configuration API Router
========================
API endpoints for configuration management and hot reload
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging

from backend.services.config_manager import get_config_manager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/config",
    tags=["Configuration"]
)

# Get global config manager instance
config_manager = get_config_manager()


@router.post("/reload")
async def reload_config(config_name: Optional[str] = Query(None, description="Specific config to reload (reloads all if omitted)")) -> JSONResponse:
    """
    Manually reload configuration files.
    
    Reloads a specific configuration file or all configuration files.
    
    Args:
        config_name: Optional specific config name to reload
    
    Returns:
        JSON response with reload status
    """
    try:
        result = config_manager.manual_reload(config_name)

        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": result["message"],
                    "data": result
                }
            )
        else:
            raise HTTPException(status_code=404, detail=result["message"])

    except Exception as e:
        logger.error(f"Error reloading config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/status")
async def get_config_status() -> JSONResponse:
    """
    Get configuration status.
    
    Returns the status of all loaded configurations.
    
    Returns:
        JSON response with config status
    """
    try:
        all_configs = config_manager.get_all_configs()

        status = {
            "loaded_configs": list(all_configs.keys()),
            "config_count": len(all_configs),
            "configs": {}
        }

        for config_name, config_data in all_configs.items():
            status["configs"][config_name] = {
                "version": config_data.get("version", "unknown"),
                "last_updated": config_data.get("last_updated", "unknown"),
                "keys": list(config_data.keys())
            }

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": status
            }
        )

    except Exception as e:
        logger.error(f"Error getting config status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{config_name}")
async def get_config(config_name: str) -> JSONResponse:
    """
    Get a specific configuration.
    
    Retrieves the current configuration for a specific config name.
    
    Args:
        config_name: Name of the config to retrieve
    
    Returns:
        JSON response with configuration data
    """
    try:
        config = config_manager.get_config(config_name)

        if config is None:
            raise HTTPException(status_code=404, detail=f"Config '{config_name}' not found")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "config_name": config_name,
                "data": config
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

