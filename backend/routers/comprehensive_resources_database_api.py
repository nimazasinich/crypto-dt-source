#!/usr/bin/env python3
"""
Comprehensive Resources Database API - Complete Crypto Data Sources
Exposes all 400+ resources from api-resources folder:
- 274+ resources from crypto_resources_unified_2025-11-11.json
- 162+ resources from ultimate_crypto_pipeline_2025_NZasinich.json
- RPC nodes, block explorers, market data, news, sentiment, on-chain analytics, whale tracking, etc.

Endpoints:
- GET /api/resources/database - Get all resources
- GET /api/resources/database/categories - Get all categories
- GET /api/resources/database/category/{category} - Get resources by category
- GET /api/resources/database/search - Search resources
- GET /api/resources/database/stats - Database statistics
- GET /api/resources/database/random - Get random resources
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import json
from pathlib import Path
import random

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Resources Database API"])

# Load resources from JSON files
RESOURCES_DIR = Path(__file__).resolve().parent.parent.parent / "api-resources"

_RESOURCES_CACHE = None
_ULTIMATE_PIPELINE_CACHE = None


def load_unified_resources() -> Dict:
    """Load resources from crypto_resources_unified_2025-11-11.json"""
    global _RESOURCES_CACHE
    
    if _RESOURCES_CACHE is not None:
        return _RESOURCES_CACHE
    
    try:
        file_path = RESOURCES_DIR / "crypto_resources_unified_2025-11-11.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _RESOURCES_CACHE = data.get('registry', {})
            return _RESOURCES_CACHE
    except Exception as e:
        logger.error(f"Error loading unified resources: {e}")
        return {}


def load_ultimate_pipeline() -> Dict:
    """Load resources from ultimate_crypto_pipeline_2025_NZasinich.json"""
    global _ULTIMATE_PIPELINE_CACHE
    
    if _ULTIMATE_PIPELINE_CACHE is not None:
        return _ULTIMATE_PIPELINE_CACHE
    
    try:
        file_path = RESOURCES_DIR / "ultimate_crypto_pipeline_2025_NZasinich.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _ULTIMATE_PIPELINE_CACHE = data
            return _ULTIMATE_PIPELINE_CACHE
    except Exception as e:
        logger.error(f"Error loading ultimate pipeline: {e}")
        return {}


def get_all_resources() -> Dict[str, Any]:
    """Get all resources from both files, consolidated"""
    unified = load_unified_resources()
    pipeline = load_ultimate_pipeline()
    
    # Consolidate resources
    consolidated = {
        "unified_resources": unified,
        "pipeline_resources": pipeline.get("files", [{}])[0].get("content", {}).get("resources", []) if pipeline.get("files") else []
    }
    
    return consolidated


# ============================================================================
# GET /api/resources/database
# ============================================================================

@router.get("/api/resources/database")
async def get_resources_database(
    category: Optional[str] = Query(None, description="Filter by category"),
    source: Optional[str] = Query("all", description="Source: unified, pipeline, all"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit results")
):
    """
    Get comprehensive resources database
    
    Returns all 400+ cryptocurrency data sources including:
    - RPC nodes (24)
    - Block explorers (33)
    - Market data APIs (33)
    - News APIs (17)
    - Sentiment APIs (14)
    - On-chain analytics (14)
    - Whale tracking (10)
    - HuggingFace resources (9)
    - Free HTTP endpoints (13)
    - Local backend routes (106)
    - Ultimate pipeline (162)
    """
    try:
        all_resources = get_all_resources()
        
        result = {
            "success": True,
            "source_files": {
                "unified": "crypto_resources_unified_2025-11-11.json",
                "pipeline": "ultimate_crypto_pipeline_2025_NZasinich.json"
            }
        }
        
        if source == "unified" or source == "all":
            unified = all_resources["unified_resources"]
            
            # Filter by category if specified
            if category:
                unified_filtered = {
                    category: unified.get(category, [])
                }
            else:
                unified_filtered = {k: v for k, v in unified.items() if k != "metadata" and isinstance(v, list)}
            
            result["unified_resources"] = {
                "categories": list(unified_filtered.keys()),
                "total_categories": len(unified_filtered),
                "resources": unified_filtered,
                "metadata": unified.get("metadata", {})
            }
        
        if source == "pipeline" or source == "all":
            pipeline_resources = all_resources["pipeline_resources"]
            
            # Filter by category if specified
            if category:
                pipeline_filtered = [
                    r for r in pipeline_resources
                    if r.get("category", "").lower() == category.lower()
                ]
            else:
                pipeline_filtered = pipeline_resources
            
            # Apply limit
            if limit:
                pipeline_filtered = pipeline_filtered[:limit]
            
            # Group by category
            pipeline_by_category = {}
            for resource in pipeline_filtered:
                cat = resource.get("category", "uncategorized")
                if cat not in pipeline_by_category:
                    pipeline_by_category[cat] = []
                pipeline_by_category[cat].append(resource)
            
            result["pipeline_resources"] = {
                "total_resources": len(pipeline_filtered),
                "categories": list(pipeline_by_category.keys()),
                "total_categories": len(pipeline_by_category),
                "resources_by_category": pipeline_by_category,
                "resources_flat": pipeline_filtered if not category else None
            }
        
        result["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting resources database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/resources/database/categories
# ============================================================================

@router.get("/api/resources/database/categories")
async def get_database_categories():
    """
    Get all available resource categories
    
    Returns complete list of categories from both data sources
    """
    try:
        all_resources = get_all_resources()
        
        # Get unified categories
        unified = all_resources["unified_resources"]
        unified_categories = [k for k in unified.keys() if k != "metadata" and isinstance(unified[k], list)]
        
        # Get pipeline categories
        pipeline_resources = all_resources["pipeline_resources"]
        pipeline_categories = list(set(r.get("category", "uncategorized") for r in pipeline_resources))
        
        # Count resources per category
        unified_counts = {
            cat: len(unified[cat]) for cat in unified_categories
        }
        
        pipeline_counts = {}
        for resource in pipeline_resources:
            cat = resource.get("category", "uncategorized")
            pipeline_counts[cat] = pipeline_counts.get(cat, 0) + 1
        
        return {
            "success": True,
            "unified_resources": {
                "categories": unified_categories,
                "total_categories": len(unified_categories),
                "counts": unified_counts,
                "total_resources": sum(unified_counts.values())
            },
            "pipeline_resources": {
                "categories": sorted(pipeline_categories),
                "total_categories": len(pipeline_categories),
                "counts": pipeline_counts,
                "total_resources": len(pipeline_resources)
            },
            "combined": {
                "unique_categories": len(set(unified_categories + pipeline_categories)),
                "total_resources": sum(unified_counts.values()) + len(pipeline_resources)
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/resources/database/category/{category}
# ============================================================================

@router.get("/api/resources/database/category/{category}")
async def get_resources_by_category(
    category: str,
    source: str = Query("all", description="Source: unified, pipeline, all"),
    limit: Optional[int] = Query(None, ge=1, le=1000)
):
    """
    Get resources from a specific category
    
    Available categories:
    - rpc_nodes
    - block_explorers
    - market_data_apis
    - news_apis
    - sentiment_apis
    - onchain_analytics_apis
    - whale_tracking_apis
    - community_sentiment_apis
    - hf_resources
    - free_http_endpoints
    - local_backend_routes
    - cors_proxies
    """
    try:
        all_resources = get_all_resources()
        result = {"success": True, "category": category}
        
        if source in ["unified", "all"]:
            unified = all_resources["unified_resources"]
            category_resources = unified.get(category, [])
            
            if limit:
                category_resources = category_resources[:limit]
            
            result["unified_resources"] = {
                "count": len(category_resources),
                "resources": category_resources
            }
        
        if source in ["pipeline", "all"]:
            pipeline_resources = all_resources["pipeline_resources"]
            filtered = [
                r for r in pipeline_resources
                if r.get("category", "").lower() == category.lower()
            ]
            
            if limit:
                filtered = filtered[:limit]
            
            result["pipeline_resources"] = {
                "count": len(filtered),
                "resources": filtered
            }
        
        result["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting category resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/resources/database/search
# ============================================================================

@router.get("/api/resources/database/search")
async def search_resources(
    q: str = Query(..., min_length=2, description="Search query"),
    fields: Optional[str] = Query("name,url,desc", description="Fields to search: name,url,desc,category"),
    source: str = Query("all", description="Source: unified, pipeline, all"),
    limit: int = Query(50, ge=1, le=500)
):
    """
    Search resources by keyword
    
    Searches across name, URL, description, and category fields
    """
    try:
        all_resources = get_all_resources()
        query_lower = q.lower()
        search_fields = fields.split(",")
        
        results = []
        
        # Search unified resources
        if source in ["unified", "all"]:
            unified = all_resources["unified_resources"]
            
            for category, resources in unified.items():
                if category == "metadata" or not isinstance(resources, list):
                    continue
                
                for resource in resources:
                    # Check if resource matches query
                    matches = False
                    
                    if "name" in search_fields and query_lower in str(resource.get("name", "")).lower():
                        matches = True
                    if "url" in search_fields and query_lower in str(resource.get("base_url", "")).lower():
                        matches = True
                    if "desc" in search_fields and query_lower in str(resource.get("notes", "")).lower():
                        matches = True
                    if "category" in search_fields and query_lower in category.lower():
                        matches = True
                    
                    if matches:
                        results.append({
                            "source": "unified",
                            "category": category,
                            "resource": resource
                        })
        
        # Search pipeline resources
        if source in ["pipeline", "all"]:
            pipeline_resources = all_resources["pipeline_resources"]
            
            for resource in pipeline_resources:
                matches = False
                
                if "name" in search_fields and query_lower in str(resource.get("name", "")).lower():
                    matches = True
                if "url" in search_fields and query_lower in str(resource.get("url", "")).lower():
                    matches = True
                if "desc" in search_fields and query_lower in str(resource.get("desc", "")).lower():
                    matches = True
                if "category" in search_fields and query_lower in str(resource.get("category", "")).lower():
                    matches = True
                
                if matches:
                    results.append({
                        "source": "pipeline",
                        "category": resource.get("category", "uncategorized"),
                        "resource": resource
                    })
        
        # Apply limit
        results = results[:limit]
        
        return {
            "success": True,
            "query": q,
            "search_fields": search_fields,
            "total_results": len(results),
            "results": results,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error searching resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/resources/database/stats
# ============================================================================

@router.get("/api/resources/database/stats")
async def get_database_stats():
    """
    Get comprehensive statistics about the resources database
    
    Returns counts, categories, free vs paid, and more
    """
    try:
        all_resources = get_all_resources()
        
        # Unified resources stats
        unified = all_resources["unified_resources"]
        unified_categories = {k: len(v) for k, v in unified.items() if k != "metadata" and isinstance(v, list)}
        
        # Pipeline resources stats
        pipeline_resources = all_resources["pipeline_resources"]
        
        pipeline_by_category = {}
        free_count = 0
        paid_count = 0
        
        for resource in pipeline_resources:
            cat = resource.get("category", "uncategorized")
            pipeline_by_category[cat] = pipeline_by_category.get(cat, 0) + 1
            
            if resource.get("free", True):
                free_count += 1
            else:
                paid_count += 1
        
        # Combined stats
        total_unified = sum(unified_categories.values())
        total_pipeline = len(pipeline_resources)
        total_resources = total_unified + total_pipeline
        
        return {
            "success": True,
            "overview": {
                "total_resources": total_resources,
                "unified_resources": total_unified,
                "pipeline_resources": total_pipeline,
                "total_categories": len(set(list(unified_categories.keys()) + list(pipeline_by_category.keys()))),
                "unique_data_sources": 2
            },
            "unified_resources": {
                "total": total_unified,
                "categories": unified_categories,
                "top_categories": sorted(unified_categories.items(), key=lambda x: x[1], reverse=True)[:5],
                "metadata": unified.get("metadata", {})
            },
            "pipeline_resources": {
                "total": total_pipeline,
                "categories": pipeline_by_category,
                "free_resources": free_count,
                "paid_resources": paid_count,
                "top_categories": sorted(pipeline_by_category.items(), key=lambda x: x[1], reverse=True)[:5]
            },
            "coverage": {
                "rpc_nodes": unified_categories.get("rpc_nodes", 0),
                "block_explorers": unified_categories.get("block_explorers", 0) + pipeline_by_category.get("Block Explorer", 0),
                "market_data": unified_categories.get("market_data_apis", 0) + pipeline_by_category.get("Market Data", 0),
                "news_apis": unified_categories.get("news_apis", 0) + pipeline_by_category.get("News", 0),
                "sentiment_apis": unified_categories.get("sentiment_apis", 0),
                "analytics": unified_categories.get("onchain_analytics_apis", 0) + pipeline_by_category.get("On-chain", 0),
                "whale_tracking": unified_categories.get("whale_tracking_apis", 0),
                "defi": pipeline_by_category.get("DeFi", 0),
                "nft": pipeline_by_category.get("NFT", 0)
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/resources/database/random
# ============================================================================

@router.get("/api/resources/database/random")
async def get_random_resources(
    count: int = Query(10, ge=1, le=100, description="Number of random resources"),
    category: Optional[str] = Query(None, description="Filter by category"),
    source: str = Query("all", description="Source: unified, pipeline, all")
):
    """
    Get random resources from the database
    
    Useful for discovering new data sources
    """
    try:
        all_resources = get_all_resources()
        all_items = []
        
        # Collect all resources
        if source in ["unified", "all"]:
            unified = all_resources["unified_resources"]
            
            for cat, resources in unified.items():
                if cat == "metadata" or not isinstance(resources, list):
                    continue
                
                if category and cat != category:
                    continue
                
                for resource in resources:
                    all_items.append({
                        "source": "unified",
                        "category": cat,
                        "resource": resource
                    })
        
        if source in ["pipeline", "all"]:
            pipeline_resources = all_resources["pipeline_resources"]
            
            for resource in pipeline_resources:
                if category and resource.get("category", "").lower() != category.lower():
                    continue
                
                all_items.append({
                    "source": "pipeline",
                    "category": resource.get("category", "uncategorized"),
                    "resource": resource
                })
        
        # Get random sample
        sample_size = min(count, len(all_items))
        random_resources = random.sample(all_items, sample_size) if all_items else []
        
        return {
            "success": True,
            "requested_count": count,
            "returned_count": len(random_resources),
            "total_available": len(all_items),
            "resources": random_resources,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error getting random resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


logger.info("✅ Comprehensive Resources Database API Router loaded")
