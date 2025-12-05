#!/usr/bin/env python3
"""
Hugging Face Spaces - Additional API Endpoints
Exposes all resources from JSON files via REST API
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from pathlib import Path
import logging

from api_resources_manager import get_resources_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/resources", tags=["Resources"])

# Initialize resources manager
resources_mgr = get_resources_manager()


class ResourceSearchRequest(BaseModel):
    """Request model for resource search"""
    query: str
    limit: int = 10


class ResourceStats(BaseModel):
    """Statistics about loaded resources"""
    unified_resources: Dict[str, Any]
    hub_services: Dict[str, Any]


@router.get("/stats", response_model=ResourceStats)
async def get_resource_stats():
    """
    Get statistics about all loaded API resources
    
    Returns count of RPC nodes, explorers, APIs, etc.
    """
    try:
        stats = resources_mgr.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rpc-nodes")
async def get_rpc_nodes(chain: Optional[str] = Query(None, description="Filter by blockchain (ethereum, bsc, tron, polygon)")):
    """
    Get all RPC node endpoints
    
    Args:
        chain: Optional blockchain filter (ethereum, bsc, tron, polygon)
    
    Returns:
        List of RPC node configurations with URLs and auth
    """
    try:
        nodes = resources_mgr.get_rpc_nodes(chain)
        return {
            "total": len(nodes),
            "chain_filter": chain,
            "nodes": nodes
        }
    except Exception as e:
        logger.error(f"Error getting RPC nodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explorers")
async def get_block_explorers(
    chain: Optional[str] = Query(None, description="Filter by blockchain"),
    role: Optional[str] = Query(None, description="Filter by role (primary, fallback)")
):
    """
    Get blockchain explorer APIs
    
    Args:
        chain: Optional blockchain filter
        role: Optional role filter (primary, fallback)
    
    Returns:
        List of block explorer APIs with endpoints
    """
    try:
        explorers = resources_mgr.get_block_explorers(chain, role)
        return {
            "total": len(explorers),
            "filters": {"chain": chain, "role": role},
            "explorers": explorers
        }
    except Exception as e:
        logger.error(f"Error getting explorers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-apis")
async def get_market_apis(role: Optional[str] = Query(None, description="Filter by role (free, paid, primary)")):
    """
    Get market data API providers
    
    Args:
        role: Optional role filter
    
    Returns:
        List of market data APIs (CoinGecko, CoinMarketCap, etc.)
    """
    try:
        apis = resources_mgr.get_market_data_apis(role)
        return {
            "total": len(apis),
            "role_filter": role,
            "apis": apis
        }
    except Exception as e:
        logger.error(f"Error getting market APIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news-apis")
async def get_news_apis():
    """
    Get news aggregator APIs
    
    Returns:
        List of crypto news sources and RSS feeds
    """
    try:
        apis = resources_mgr.get_news_apis()
        return {
            "total": len(apis),
            "apis": apis
        }
    except Exception as e:
        logger.error(f"Error getting news APIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment-apis")
async def get_sentiment_apis():
    """
    Get sentiment analysis APIs
    
    Returns:
        List of sentiment tracking services (Fear & Greed, social metrics, etc.)
    """
    try:
        apis = resources_mgr.get_sentiment_apis()
        return {
            "total": len(apis),
            "apis": apis
        }
    except Exception as e:
        logger.error(f"Error getting sentiment APIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/whale-apis")
async def get_whale_apis():
    """
    Get whale tracking APIs
    
    Returns:
        List of whale alert and large transaction monitoring services
    """
    try:
        apis = resources_mgr.get_whale_tracking_apis()
        return {
            "total": len(apis),
            "apis": apis
        }
    except Exception as e:
        logger.error(f"Error getting whale APIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/onchain-apis")
async def get_onchain_apis():
    """
    Get on-chain analytics APIs
    
    Returns:
        List of blockchain analytics services (Glassnode, Nansen, etc.)
    """
    try:
        apis = resources_mgr.get_onchain_analytics_apis()
        return {
            "total": len(apis),
            "apis": apis
        }
    except Exception as e:
        logger.error(f"Error getting on-chain APIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hf-resources")
async def get_hf_resources(
    resource_type: Optional[str] = Query(None, description="Filter by type (model, dataset)")
):
    """
    Get Hugging Face resources (models and datasets)
    
    Args:
        resource_type: Optional filter by type (model or dataset)
    
    Returns:
        List of HF models and datasets for crypto analysis
    """
    try:
        resources = resources_mgr.get_hf_resources(resource_type)
        return {
            "total": len(resources),
            "type_filter": resource_type,
            "resources": resources
        }
    except Exception as e:
        logger.error(f"Error getting HF resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/free-endpoints")
async def get_free_endpoints(
    category: Optional[str] = Query(None, description="Filter by category (market, news, sentiment, etc.)")
):
    """
    Get free HTTP endpoints (no authentication required)
    
    Args:
        category: Optional category filter
    
    Returns:
        List of free-to-use API endpoints
    """
    try:
        endpoints = resources_mgr.get_free_http_endpoints(category)
        return {
            "total": len(endpoints),
            "category_filter": category,
            "endpoints": endpoints
        }
    except Exception as e:
        logger.error(f"Error getting free endpoints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories():
    """
    Get all service categories
    
    Returns:
        List of available categories (explorer, market, news, sentiment, analytics)
    """
    try:
        categories = resources_mgr.get_all_categories()
        return {
            "total": len(categories),
            "categories": categories
        }
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/{category}")
async def get_services_by_category(category: str):
    """
    Get all services in a specific category
    
    Args:
        category: Category name (explorer, market, news, sentiment, analytics)
    
    Returns:
        List of services in that category with endpoints and API keys
    """
    try:
        services = resources_mgr.get_services_by_category(category)
        if not services:
            raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
        
        return {
            "category": category,
            "total": len(services),
            "services": services
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service/{name}")
async def get_service_by_name(name: str):
    """
    Get a specific service by name
    
    Args:
        name: Service name (e.g., 'CoinGecko', 'Etherscan')
    
    Returns:
        Service configuration with endpoints and API key
    """
    try:
        service = resources_mgr.get_service_by_name(name)
        if not service:
            raise HTTPException(status_code=404, detail=f"Service '{name}' not found")
        
        return service
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_resources(request: ResourceSearchRequest):
    """
    Search all resources by name or description
    
    Args:
        request: Search query and limit
    
    Returns:
        List of matching resources
    """
    try:
        results = resources_mgr.search_resources(request.query, request.limit)
        return {
            "query": request.query,
            "total": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error searching resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api-keys")
async def get_api_keys_info():
    """
    Get information about available API keys
    
    Returns:
        List of services with API keys (keys are masked for security)
    """
    try:
        keys = resources_mgr.get_api_keys()
        
        # Mask keys for security
        masked_keys = {}
        for name, key in keys.items():
            if len(key) > 12:
                masked_keys[name] = f"{key[:8]}...{key[-4:]}"
            else:
                masked_keys[name] = "***"
        
        return {
            "total": len(masked_keys),
            "services_with_keys": list(masked_keys.keys()),
            "masked_keys": masked_keys
        }
    except Exception as e:
        logger.error(f"Error getting API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resource/{resource_id}")
async def get_resource_by_id(resource_id: str):
    """
    Get a specific resource by ID
    
    Args:
        resource_id: Unique resource identifier
    
    Returns:
        Resource configuration
    """
    try:
        resource = resources_mgr.get_resource_by_id(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail=f"Resource '{resource_id}' not found")
        
        return resource
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resource: {e}")
        raise HTTPException(status_code=500, detail=str(e))

