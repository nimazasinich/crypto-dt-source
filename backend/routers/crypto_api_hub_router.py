"""
Crypto API Hub Router
FastAPI router for the Crypto API Hub Dashboard endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from crypto_api_hub_backend import crypto_hub_service, APIRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/crypto-hub", tags=["Crypto API Hub"])


@router.get("/services")
async def get_services():
    """
    Get all crypto API services

    Returns all 74+ services organized by category
    """
    try:
        services = await crypto_hub_service.get_services()
        return JSONResponse(content=services)
    except Exception as e:
        logger.error(f"Error getting services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/{category}")
async def get_services_by_category(category: str):
    """
    Get services by category

    Categories: explorer, market, news, sentiment, analytics
    """
    try:
        services = await crypto_hub_service.get_services_by_category(category)
        return JSONResponse(content={"category": category, "services": services})
    except Exception as e:
        logger.error(f"Error getting services by category {category}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_services(query: str):
    """
    Search services by name, URL, or category
    """
    try:
        results = await crypto_hub_service.search_services(query)
        return JSONResponse(content={"query": query, "results": results})
    except Exception as e:
        logger.error(f"Error searching services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/proxy")
async def proxy_request(request: APIRequest):
    """
    Proxy API requests to avoid CORS issues

    This endpoint acts as a proxy to make requests to external APIs
    """
    try:
        result = await crypto_hub_service.test_endpoint(
            url=request.url, method=request.method, headers=request.headers, body=request.body
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error proxying request to {request.url}: {e}")
        return JSONResponse(
            status_code=500, content={"error": "Proxy request failed", "details": str(e)}
        )


@router.get("/stats")
async def get_stats():
    """
    Get statistics about all services

    Returns total counts of services, endpoints, and API keys
    """
    try:
        stats = await crypto_hub_service.get_service_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate/{service_name}")
async def validate_service(service_name: str):
    """
    Validate a service by testing its endpoints

    Tests the first 3 endpoints of the specified service
    """
    try:
        result = await crypto_hub_service.validate_service(service_name)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating service {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-endpoint")
async def test_endpoint(url: str, method: str = "GET", headers: Optional[str] = None):
    """
    Test a single endpoint

    Quick endpoint testing without body
    """
    try:
        import json

        headers_dict = json.loads(headers) if headers else None

        result = await crypto_hub_service.test_endpoint(
            url=url, method=method, headers=headers_dict
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error testing endpoint {url}: {e}")
        return JSONResponse(
            status_code=500, content={"error": "Endpoint test failed", "details": str(e)}
        )


# Add shutdown event to close HTTP client
@router.on_event("shutdown")
async def shutdown_event():
    """Close HTTP client on shutdown"""
    await crypto_hub_service.close()
