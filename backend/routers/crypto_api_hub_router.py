#!/usr/bin/env python3
"""
Crypto API Hub Router - Backend endpoints for the API Hub Dashboard
Provides service management, API testing, and CORS proxy functionality
"""

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import logging
import json
import aiohttp
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/crypto-hub", tags=["Crypto API Hub"])

# Path to services data
SERVICES_FILE = Path("crypto_api_hub_services.json")


# ============================================================================
# Models
# ============================================================================

class APITestRequest(BaseModel):
    """Request model for API testing"""
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = None


class APITestResponse(BaseModel):
    """Response model for API testing"""
    success: bool
    status_code: int
    data: Any
    error: Optional[str] = None


# ============================================================================
# Helper Functions
# ============================================================================

def load_services() -> Dict[str, Any]:
    """Load services data from JSON file"""
    try:
        if not SERVICES_FILE.exists():
            logger.error(f"Services file not found: {SERVICES_FILE}")
            return {
                "metadata": {
                    "version": "1.0.0",
                    "total_services": 0,
                    "total_endpoints": 0,
                    "api_keys_count": 0,
                    "last_updated": "2025-11-27"
                },
                "categories": {}
            }

        with open(SERVICES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading services: {e}")
        raise HTTPException(status_code=500, detail="Failed to load services data")


def get_service_count(services_data: Dict[str, Any]) -> Dict[str, int]:
    """Calculate service statistics"""
    total_services = 0
    total_endpoints = 0
    api_keys_count = 0

    for category_name, category_data in services_data.get("categories", {}).items():
        for service in category_data.get("services", []):
            total_services += 1
            total_endpoints += len(service.get("endpoints", []))
            if service.get("key"):
                api_keys_count += 1

    return {
        "total_services": total_services,
        "total_endpoints": total_endpoints,
        "api_keys_count": api_keys_count
    }


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/services")
async def get_all_services():
    """
    Get all crypto API services

    Returns complete services data with all categories and endpoints
    """
    try:
        services_data = load_services()
        stats = get_service_count(services_data)

        # Update metadata with current stats
        services_data["metadata"].update(stats)

        return JSONResponse(content=services_data)
    except Exception as e:
        logger.error(f"Error in get_all_services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/category/{category}")
async def get_services_by_category(category: str):
    """
    Get services for a specific category

    Args:
        category: Category name (explorer, market, news, sentiment, analytics)
    """
    try:
        services_data = load_services()
        categories = services_data.get("categories", {})

        if category not in categories:
            raise HTTPException(
                status_code=404,
                detail=f"Category '{category}' not found. Available: {list(categories.keys())}"
            )

        return JSONResponse(content=categories[category])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_services_by_category: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/search")
async def search_services(
    q: str = Query(..., min_length=1, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Search services by name, description, or URL

    Args:
        q: Search query
        category: Optional category filter
    """
    try:
        services_data = load_services()
        results = []

        query_lower = q.lower()
        categories_to_search = services_data.get("categories", {})

        # Filter by category if specified
        if category:
            if category in categories_to_search:
                categories_to_search = {category: categories_to_search[category]}
            else:
                return JSONResponse(content={"results": [], "count": 0})

        # Search through services
        for cat_name, cat_data in categories_to_search.items():
            for service in cat_data.get("services", []):
                # Search in name, description, and URL
                if (query_lower in service.get("name", "").lower() or
                    query_lower in service.get("description", "").lower() or
                    query_lower in service.get("url", "").lower()):

                    results.append({
                        "category": cat_name,
                        "service": service
                    })

        return JSONResponse(content={
            "results": results,
            "count": len(results),
            "query": q
        })
    except Exception as e:
        logger.error(f"Error in search_services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_statistics():
    """
    Get statistics about the API hub

    Returns counts of services, endpoints, and API keys
    """
    try:
        services_data = load_services()
        stats = get_service_count(services_data)

        # Add category breakdown
        category_stats = {}
        for cat_name, cat_data in services_data.get("categories", {}).items():
            services = cat_data.get("services", [])
            endpoints_count = sum(len(s.get("endpoints", [])) for s in services)

            category_stats[cat_name] = {
                "services_count": len(services),
                "endpoints_count": endpoints_count,
                "has_keys": sum(1 for s in services if s.get("key"))
            }

        return JSONResponse(content={
            **stats,
            "categories": category_stats,
            "metadata": services_data.get("metadata", {})
        })
    except Exception as e:
        logger.error(f"Error in get_statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_api_endpoint(request: APITestRequest):
    """
    Test an API endpoint with CORS proxy

    Allows testing external APIs that might have CORS restrictions
    """
    try:
        # Validate URL
        if not request.url or not request.url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Invalid URL")

        # Prepare headers
        headers = request.headers or {}
        if "User-Agent" not in headers:
            headers["User-Agent"] = "Crypto-API-Hub/1.0"

        # Make request
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                if request.method.upper() == "GET":
                    async with session.get(request.url, headers=headers) as response:
                        status_code = response.status
                        try:
                            data = await response.json()
                        except:
                            data = await response.text()

                elif request.method.upper() == "POST":
                    async with session.post(
                        request.url,
                        headers=headers,
                        data=request.body
                    ) as response:
                        status_code = response.status
                        try:
                            data = await response.json()
                        except:
                            data = await response.text()

                elif request.method.upper() == "PUT":
                    async with session.put(
                        request.url,
                        headers=headers,
                        data=request.body
                    ) as response:
                        status_code = response.status
                        try:
                            data = await response.json()
                        except:
                            data = await response.text()

                elif request.method.upper() == "DELETE":
                    async with session.delete(request.url, headers=headers) as response:
                        status_code = response.status
                        try:
                            data = await response.json()
                        except:
                            data = await response.text()

                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unsupported HTTP method: {request.method}"
                    )

                return JSONResponse(content={
                    "success": True,
                    "status_code": status_code,
                    "data": data,
                    "tested_url": request.url,
                    "method": request.method.upper()
                })

            except aiohttp.ClientError as e:
                logger.error(f"API test error: {e}")
                return JSONResponse(
                    status_code=200,  # Return 200 but with error in response
                    content={
                        "success": False,
                        "status_code": 0,
                        "data": None,
                        "error": f"Request failed: {str(e)}",
                        "tested_url": request.url
                    }
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in test_api_endpoint: {e}")
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "status_code": 0,
                "data": None,
                "error": str(e),
                "tested_url": request.url
            }
        )


@router.get("/categories")
async def get_categories():
    """
    Get list of all available categories

    Returns category names and metadata
    """
    try:
        services_data = load_services()
        categories = []

        for cat_name, cat_data in services_data.get("categories", {}).items():
            services_count = len(cat_data.get("services", []))

            categories.append({
                "id": cat_name,
                "name": cat_data.get("name", cat_name.title()),
                "description": cat_data.get("description", ""),
                "icon": cat_data.get("icon", ""),
                "services_count": services_count
            })

        return JSONResponse(content={
            "categories": categories,
            "total": len(categories)
        })
    except Exception as e:
        logger.error(f"Error in get_categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={
        "status": "healthy",
        "service": "crypto-api-hub",
        "version": "1.0.0"
    })
