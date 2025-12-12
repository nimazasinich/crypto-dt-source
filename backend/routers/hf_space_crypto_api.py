#!/usr/bin/env python3
"""
HuggingFace Space Crypto Resources API Router
روتر API برای دسترسی به منابع کریپتو در HuggingFace Space

This router provides endpoints to access the external HF Space Crypto API:
https://really-amin-crypto-api-clean.hf.space

Endpoints:
- /api/hf-space/coins/top - Top coins by market cap
- /api/hf-space/trending - Trending coins
- /api/hf-space/market - Market overview
- /api/hf-space/sentiment - Fear & Greed Index
- /api/hf-space/resources - Resource database
"""

from fastapi import APIRouter, Query, HTTPException, Path
from typing import Optional, List
import logging

from backend.services.hf_space_crypto_client import get_hf_space_crypto_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/hf-space",
    tags=["HuggingFace Space Crypto API"]
)


# ===== MARKET DATA ENDPOINTS =====

@router.get("/coins/top")
async def get_top_coins(
    limit: int = Query(50, ge=1, le=250, description="Number of coins to return")
):
    """
    Get top coins by market cap from HF Space API
    
    دریافت برترین ارزها بر اساس مارکت کپ
    
    Source: HuggingFace Space Crypto API → CoinGecko
    
    Returns:
        - coins: List of top coins with price, market cap, volume, etc.
        - total: Total number of coins returned
        - timestamp: Data timestamp
    """
    try:
        service = get_hf_space_crypto_service()
        result = await service.get_top_coins(limit=limit)
        
        if not result["success"]:
            raise HTTPException(
                status_code=503,
                detail=f"HF Space API unavailable: {result.get('error')}"
            )
        
        return result["data"]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Top coins endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending_coins():
    """
    Get trending coins from HF Space API
    
    دریافت ارزهای ترند
    
    Source: HuggingFace Space Crypto API → CoinGecko
    
    Returns:
        - coins: List of trending coins
        - total: Total number of trending coins
        - timestamp: Data timestamp
    """
    try:
        service = get_hf_space_crypto_service()
        result = await service.get_trending()
        
        if not result["success"]:
            raise HTTPException(
                status_code=503,
                detail=f"HF Space API unavailable: {result.get('error')}"
            )
        
        return result["data"]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Trending coins endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market")
async def get_market_overview():
    """
    Get global market overview from HF Space API
    
    خلاصه کلی بازار
    
    Source: HuggingFace Space Crypto API → CoinGecko
    
    Returns:
        - total_market_cap: Total market cap in USD
        - total_volume: 24h trading volume
        - market_cap_percentage: Dominance by coin (BTC, ETH, etc.)
        - active_cryptocurrencies: Number of active cryptos
        - markets: Number of markets
    """
    try:
        service = get_hf_space_crypto_service()
        result = await service.get_market_overview()
        
        if not result["success"]:
            raise HTTPException(
                status_code=503,
                detail=f"HF Space API unavailable: {result.get('error')}"
            )
        
        return result["data"]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Market overview endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== SENTIMENT ENDPOINTS =====

@router.get("/sentiment")
async def get_global_sentiment(
    timeframe: str = Query("1D", description="Timeframe for sentiment data")
):
    """
    Get Fear & Greed Index from HF Space API
    
    شاخص ترس و طمع
    
    Source: HuggingFace Space Crypto API → Alternative.me
    
    Returns:
        - fear_greed_index: Current index value (0-100)
        - sentiment: Classification (fear, greed, etc.)
        - market_mood: Market mood (bearish, bullish, neutral)
        - confidence: Confidence score
        - source: Data source (alternative.me)
    """
    try:
        service = get_hf_space_crypto_service()
        result = await service.get_global_sentiment(timeframe=timeframe)
        
        if not result["success"]:
            raise HTTPException(
                status_code=503,
                detail=f"HF Space API unavailable: {result.get('error')}"
            )
        
        return result["data"]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Sentiment endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment/{symbol}")
async def get_asset_sentiment(
    symbol: str = Path(..., description="Asset symbol (e.g., BTC, ETH)")
):
    """
    Get sentiment for specific asset from HF Space API
    
    احساسات یک ارز خاص
    
    Returns:
        - symbol: Asset symbol
        - sentiment: Sentiment classification
        - score: Sentiment score
        - confidence: Confidence score
    """
    try:
        service = get_hf_space_crypto_service()
        result = await service.get_asset_sentiment(symbol.upper())
        
        if not result["success"]:
            raise HTTPException(
                status_code=503,
                detail=f"HF Space API unavailable: {result.get('error')}"
            )
        
        return result["data"]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Asset sentiment endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== RESOURCES DATABASE ENDPOINTS =====

@router.get("/resources/stats")
async def get_resources_stats():
    """
    Get resources database statistics from HF Space API
    
    آمار منابع
    
    Returns:
        - total_resources: Total number of resources (281)
        - total_categories: Number of categories (12)
        - categories: Resource count per category
        - metadata: Database metadata
    """
    try:
        service = get_hf_space_crypto_service()
        result = await service.get_resources_stats()
        
        if not result["success"]:
            raise HTTPException(
                status_code=503,
                detail=f"HF Space API unavailable: {result.get('error')}"
            )
        
        return result["data"]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Resources stats endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/categories")
async def get_categories():
    """
    Get list of resource categories from HF Space API
    
    لیست دسته‌بندی‌ها
    
    Returns:
        - total: Number of categories
        - categories: List of categories with name, count, and endpoint
    """
    try:
        service = get_hf_space_crypto_service()
        result = await service.get_categories()
        
        if not result["success"]:
            raise HTTPException(
                status_code=503,
                detail=f"HF Space API unavailable: {result.get('error')}"
            )
        
        return result["data"]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Categories endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/category/{category}")
async def get_resources_by_category(
    category: str = Path(
        ...,
        description="Category name (rpc_nodes, block_explorers, market_data_apis, etc.)"
    )
):
    """
    Get resources for a specific category from HF Space API
    
    منابع یک دسته خاص
    
    Available categories:
    - rpc_nodes (24 resources)
    - block_explorers (33 resources)
    - market_data_apis (33 resources)
    - news_apis (17 resources)
    - sentiment_apis (14 resources)
    - onchain_analytics_apis (14 resources)
    - whale_tracking_apis (10 resources)
    - hf_resources (9 resources)
    - free_http_endpoints (13 resources)
    - local_backend_routes (106 resources)
    - cors_proxies (7 resources)
    - community_sentiment_apis (1 resource)
    
    Returns:
        - category: Category name
        - total: Number of resources in category
        - resources: List of resources with name, base_url, auth, endpoints
    """
    try:
        service = get_hf_space_crypto_service()
        result = await service.get_resources_by_category(category)
        
        if not result["success"]:
            raise HTTPException(
                status_code=503,
                detail=f"HF Space API unavailable: {result.get('error')}"
            )
        
        return result["data"]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Resources by category endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/all")
async def get_all_resources():
    """
    Get all resources list from HF Space API
    
    لیست همه منابع
    
    Returns:
        - total: Total number of resources (281)
        - resources: List of all resources
    """
    try:
        service = get_hf_space_crypto_service()
        result = await service.get_all_resources()
        
        if not result["success"]:
            raise HTTPException(
                status_code=503,
                detail=f"HF Space API unavailable: {result.get('error')}"
            )
        
        return result["data"]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ All resources endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== SYSTEM STATUS ENDPOINTS =====

@router.get("/health")
async def health_check():
    """
    Check HF Space API health status
    
    بررسی سلامت API
    
    Returns:
        - status: Health status
        - resources_loaded: Whether resources are loaded
        - total_categories: Number of categories
    """
    try:
        service = get_hf_space_crypto_service()
        result = await service.health_check()
        
        if not result["success"]:
            return {
                "status": "unavailable",
                "error": result.get("error"),
                "source": "hf_space_crypto_api"
            }
        
        return {
            **result["data"],
            "source": "hf_space_crypto_api"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "source": "hf_space_crypto_api"
        }


@router.get("/providers")
async def get_providers_status():
    """
    Get data providers status from HF Space API
    
    وضعیت provider ها
    
    Returns:
        - providers: List of providers with status, latency, success rate
        - total: Number of providers
    """
    try:
        service = get_hf_space_crypto_service()
        result = await service.get_providers_status()
        
        if not result["success"]:
            raise HTTPException(
                status_code=503,
                detail=f"HF Space API unavailable: {result.get('error')}"
            )
        
        return result["data"]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Providers status endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_system_status():
    """
    Get system status from HF Space API
    
    وضعیت سیستم
    
    Returns:
        - status: System status (online, offline)
        - health: System health
        - avg_response_time: Average response time
        - cache_hit_rate: Cache hit rate
        - uptime: System uptime
    """
    try:
        service = get_hf_space_crypto_service()
        result = await service.get_system_status()
        
        if not result["success"]:
            raise HTTPException(
                status_code=503,
                detail=f"HF Space API unavailable: {result.get('error')}"
            )
        
        return result["data"]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ System status endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
