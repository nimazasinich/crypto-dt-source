#!/usr/bin/env python3
"""
Service Status & Discovery API Router
Provides endpoints for service discovery and health monitoring
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from backend.services.service_discovery import (
    get_service_discovery,
    ServiceCategory,
    INTERNAL_SERVICES
)
from backend.services.health_checker import (
    get_health_checker,
    perform_health_check,
    ServiceStatus
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/services", tags=["Service Discovery & Status"])


@router.get("/discover")
async def discover_services(
    category: Optional[str] = Query(None, description="Filter by category"),
    refresh: bool = Query(False, description="Force refresh discovery")
):
    """
    Discover all services used in the project
    
    Returns comprehensive list of all discovered services
    """
    try:
        discovery = get_service_discovery()
        
        if refresh:
            logger.info("🔄 Refreshing service discovery...")
            discovery.discover_all_services()
        
        # Get services
        if category:
            try:
                cat_enum = ServiceCategory(category)
                services = discovery.get_services_by_category(cat_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        else:
            services = discovery.get_all_services()
        
        # Add internal services
        all_services = [
            {
                "id": s.id,
                "name": s.name,
                "category": s.category.value,
                "base_url": s.base_url,
                "endpoints": s.endpoints,
                "requires_auth": s.requires_auth,
                "api_key_env": s.api_key_env,
                "discovered_in": s.discovered_in,
                "features": s.features,
                "priority": s.priority,
                "rate_limit": s.rate_limit,
                "documentation_url": s.documentation_url
            }
            for s in services
        ]
        
        # Add internal services if no category filter
        if not category:
            for internal in INTERNAL_SERVICES:
                all_services.append(internal)
        
        return {
            "success": True,
            "total_services": len(all_services),
            "category_filter": category,
            "services": all_services,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Service discovery failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service discovery failed: {str(e)}")


@router.get("/health")
async def check_services_health(
    service_id: Optional[str] = Query(None, description="Check specific service"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    force_check: bool = Query(False, description="Force new health check")
):
    """
    Check health status of all services
    
    Performs health checks and returns status information
    """
    try:
        checker = get_health_checker()
        
        # Force new check if requested or no cached results
        if force_check or not checker.health_results:
            logger.info("🔍 Performing health checks...")
            await perform_health_check()
        
        # Get results
        if service_id:
            if service_id not in checker.health_results:
                raise HTTPException(status_code=404, detail=f"Service '{service_id}' not found")
            
            result = checker.health_results[service_id]
            return {
                "success": True,
                "service": {
                    "id": result.service_id,
                    "name": result.service_name,
                    "status": result.status.value,
                    "response_time_ms": result.response_time_ms,
                    "status_code": result.status_code,
                    "error_message": result.error_message,
                    "checked_at": result.checked_at,
                    "endpoint_checked": result.endpoint_checked,
                    "additional_info": result.additional_info
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Filter by status if requested
        results = list(checker.health_results.values())
        if status_filter:
            try:
                status_enum = ServiceStatus(status_filter)
                results = [r for r in results if r.status == status_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")
        
        return {
            "success": True,
            "total_services": len(results),
            "summary": checker.get_health_summary(),
            "services": [
                {
                    "id": r.service_id,
                    "name": r.service_name,
                    "status": r.status.value,
                    "response_time_ms": r.response_time_ms,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "checked_at": r.checked_at,
                    "endpoint_checked": r.endpoint_checked,
                    "additional_info": r.additional_info
                }
                for r in results
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/categories")
async def get_service_categories():
    """
    Get all service categories
    
    Returns list of available service categories with counts
    """
    try:
        discovery = get_service_discovery()
        
        categories = {}
        for category in ServiceCategory:
            services = discovery.get_services_by_category(category)
            categories[category.value] = {
                "name": category.value,
                "display_name": category.value.replace('_', ' ').title(),
                "count": len(services)
            }
        
        return {
            "success": True,
            "categories": categories,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to get categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_service_statistics():
    """
    Get comprehensive service statistics
    
    Returns statistics about discovered services and their health
    """
    try:
        discovery = get_service_discovery()
        checker = get_health_checker()
        
        # Get discovery stats
        all_services = discovery.get_all_services()
        
        category_counts = {}
        for category in ServiceCategory:
            count = len(discovery.get_services_by_category(category))
            if count > 0:
                category_counts[category.value] = count
        
        auth_required = len([s for s in all_services if s.requires_auth])
        no_auth = len([s for s in all_services if not s.requires_auth])
        
        # Get health stats if available
        health_summary = checker.get_health_summary() if checker.health_results else None
        
        return {
            "success": True,
            "discovery": {
                "total_services": len(all_services) + len(INTERNAL_SERVICES),
                "external_services": len(all_services),
                "internal_services": len(INTERNAL_SERVICES),
                "by_category": category_counts,
                "requires_auth": auth_required,
                "no_auth": no_auth
            },
            "health": health_summary,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health/check")
async def trigger_health_check():
    """
    Trigger a new health check for all services
    
    Forces a fresh health check of all discovered services
    """
    try:
        logger.info("🔄 Triggering health check...")
        result = await perform_health_check()
        
        return {
            "success": True,
            "message": "Health check completed",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/search")
async def search_services(
    query: str = Query(..., description="Search query"),
    include_health: bool = Query(False, description="Include health status")
):
    """
    Search services by name, category, or features
    
    Searches through all discovered services
    """
    try:
        discovery = get_service_discovery()
        checker = get_health_checker()
        
        query_lower = query.lower()
        
        # Search services
        matching_services = []
        for service in discovery.get_all_services():
            if (query_lower in service.name.lower() or
                query_lower in service.category.value.lower() or
                any(query_lower in f.lower() for f in service.features) or
                query_lower in service.base_url.lower()):
                
                service_dict = {
                    "id": service.id,
                    "name": service.name,
                    "category": service.category.value,
                    "base_url": service.base_url,
                    "features": service.features,
                    "requires_auth": service.requires_auth
                }
                
                # Add health status if requested
                if include_health and service.id in checker.health_results:
                    health = checker.health_results[service.id]
                    service_dict["health"] = {
                        "status": health.status.value,
                        "response_time_ms": health.response_time_ms,
                        "checked_at": health.checked_at
                    }
                
                matching_services.append(service_dict)
        
        return {
            "success": True,
            "query": query,
            "results_count": len(matching_services),
            "services": matching_services,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Service search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_service_data(
    format: str = Query("json", description="Export format (json)"),
    include_health: bool = Query(True, description="Include health data")
):
    """
    Export complete service discovery and health data
    
    Exports all service information in requested format
    """
    try:
        discovery = get_service_discovery()
        checker = get_health_checker()
        
        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "discovery": discovery.export_to_dict()
        }
        
        if include_health:
            export_data["health"] = checker.export_to_dict()
        
        return {
            "success": True,
            "format": format,
            "data": export_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Initialize on module load
@router.on_event("startup")
async def startup_service_discovery():
    """Initialize service discovery on startup"""
    try:
        logger.info("🚀 Initializing service discovery...")
        discovery = get_service_discovery()
        logger.info(f"✅ Discovered {len(discovery.discovered_services)} services")
    except Exception as e:
        logger.error(f"❌ Service discovery initialization failed: {e}")
