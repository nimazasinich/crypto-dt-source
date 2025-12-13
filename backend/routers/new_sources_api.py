#!/usr/bin/env python3
"""
New Data Sources API Router
Exposes the newly integrated Crypto API Clean and Crypto DT Source APIs
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional, List
import logging

# Import new client services
from backend.services.crypto_api_clean_client import (
    get_crypto_api_clean_service,
    CryptoAPICleanService
)
from backend.services.crypto_dt_source_client import (
    get_crypto_dt_source_service,
    CryptoDTSourceService
)

# Import fallback manager
from backend.services.api_fallback_manager import get_fallback_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/new-sources", tags=["New Data Sources"])

# Initialize services
crypto_api_clean = get_crypto_api_clean_service()
crypto_dt_source = get_crypto_dt_source_service()

# Setup fallback managers
price_fallback = get_fallback_manager("cryptocurrency_prices")
sentiment_fallback = get_fallback_manager("sentiment_analysis")
resources_fallback = get_fallback_manager("resource_database")


# ==================== CRYPTO API CLEAN ENDPOINTS ====================

@router.get("/crypto-api-clean/health")
async def crypto_api_clean_health():
    """Health check for Crypto API Clean"""
    result = await crypto_api_clean.health_check()
    if not result["success"]:
        raise HTTPException(status_code=503, detail=result.get("error", "Service unavailable"))
    return result


@router.get("/crypto-api-clean/stats")
async def get_crypto_api_clean_stats():
    """
    Get statistics from Crypto API Clean resource database
    Returns: Total resources (281+), categories (12), breakdown
    """
    result = await crypto_api_clean.get_resources_stats()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.get("/crypto-api-clean/resources")
async def get_crypto_api_clean_resources(
    category: Optional[str] = Query(None, description="Filter by category (e.g., market_data_apis, sentiment_apis)")
):
    """
    Get resources from Crypto API Clean database
    
    Categories available:
    - rpc_nodes (24)
    - block_explorers (33)
    - market_data_apis (33)
    - news_apis (17)
    - sentiment_apis (14)
    - onchain_analytics_apis (14)
    - whale_tracking_apis (10)
    - hf_resources (9)
    - free_http_endpoints (13)
    - cors_proxies (7)
    - community_sentiment_apis (1)
    - local_backend_routes (106)
    """
    if category:
        result = await crypto_api_clean.get_resources_by_category(category)
    else:
        result = await crypto_api_clean.get_all_resources()
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.get("/crypto-api-clean/categories")
async def get_crypto_api_clean_categories():
    """Get list of all resource categories"""
    result = await crypto_api_clean.get_categories()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


# ==================== CRYPTO DT SOURCE ENDPOINTS ====================

@router.get("/crypto-dt-source/health")
async def crypto_dt_source_health():
    """Health check for Crypto DT Source"""
    result = await crypto_dt_source.health_check()
    if not result["success"]:
        raise HTTPException(status_code=503, detail=result.get("error", "Service unavailable"))
    return result


@router.get("/crypto-dt-source/status")
async def get_crypto_dt_source_status():
    """
    Get system status from Crypto DT Source
    Returns: Models, datasets, external APIs availability
    """
    result = await crypto_dt_source.get_status()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.get("/crypto-dt-source/prices")
async def get_crypto_dt_prices(
    ids: str = Query("bitcoin,ethereum", description="Comma-separated coin IDs"),
    vs_currencies: str = Query("usd", description="Comma-separated currencies")
):
    """
    Get cryptocurrency prices from Crypto DT Source (via CoinGecko)
    
    Examples:
    - /prices?ids=bitcoin&vs_currencies=usd
    - /prices?ids=bitcoin,ethereum,solana&vs_currencies=usd,eur
    """
    result = await crypto_dt_source.get_coingecko_price(ids=ids, vs_currencies=vs_currencies)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.get("/crypto-dt-source/klines")
async def get_crypto_dt_klines(
    symbol: str = Query("BTCUSDT", description="Trading pair"),
    interval: str = Query("1h", description="Time interval (1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(100, description="Number of candles", ge=1, le=1000)
):
    """
    Get candlestick/OHLCV data from Crypto DT Source (via Binance)
    
    Examples:
    - /klines?symbol=BTCUSDT&interval=1h&limit=100
    - /klines?symbol=ETHUSDT&interval=4h&limit=50
    """
    result = await crypto_dt_source.get_binance_klines(symbol=symbol, interval=interval, limit=limit)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.get("/crypto-dt-source/fear-greed")
async def get_crypto_dt_fear_greed(
    limit: int = Query(1, description="Number of historical data points", ge=1, le=30)
):
    """
    Get Fear & Greed Index from Crypto DT Source (via Alternative.me)
    
    Returns index value (0-100) and classification:
    - 0-24: Extreme Fear
    - 25-49: Fear
    - 50: Neutral
    - 51-74: Greed
    - 75-100: Extreme Greed
    """
    result = await crypto_dt_source.get_fear_greed_index(limit=limit)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.get("/crypto-dt-source/sentiment")
async def analyze_crypto_dt_sentiment(
    text: str = Query(..., description="Text to analyze"),
    model_key: str = Query("cryptobert_kk08", description="Model to use")
):
    """
    Analyze sentiment using Crypto DT Source HuggingFace models
    
    Available models:
    - cryptobert_kk08: kk08/CryptoBERT
    - twitter_sentiment: cardiffnlp/twitter-roberta-base-sentiment-latest
    - finbert: ProsusAI/finbert
    - cryptobert_elkulako: ElKulako/cryptobert
    
    Example:
    - /sentiment?text=Bitcoin is doing great today!&model_key=cryptobert_kk08
    """
    result = await crypto_dt_source.get_hf_sentiment(text=text, model_key=model_key)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.get("/crypto-dt-source/reddit")
async def get_crypto_dt_reddit(
    subreddit: str = Query("cryptocurrency", description="Subreddit name"),
    time_filter: str = Query("day", description="Time filter (hour, day, week, month, year, all)"),
    limit: int = Query(25, description="Number of posts", ge=1, le=100)
):
    """
    Get top Reddit posts from Crypto DT Source
    
    Example:
    - /reddit?subreddit=cryptocurrency&time_filter=day&limit=10
    - /reddit?subreddit=bitcoin&time_filter=week&limit=25
    """
    result = await crypto_dt_source.get_reddit_top(subreddit=subreddit, time_filter=time_filter, limit=limit)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.get("/crypto-dt-source/news")
async def get_crypto_dt_news(
    feed_name: str = Query("coindesk", description="Feed name (coindesk, cointelegraph, bitcoinmagazine, decrypt, theblock)"),
    limit: int = Query(20, description="Number of articles", ge=1, le=100)
):
    """
    Get crypto news from RSS feeds via Crypto DT Source
    
    Available feeds:
    - coindesk
    - cointelegraph
    - bitcoinmagazine
    - decrypt
    - theblock
    
    Example:
    - /news?feed_name=coindesk&limit=10
    """
    result = await crypto_dt_source.get_rss_feed(feed_name=feed_name, limit=limit)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.get("/crypto-dt-source/models")
async def get_crypto_dt_models():
    """
    Get list of available HuggingFace models in Crypto DT Source
    
    Returns 4 sentiment analysis models for crypto text analysis
    """
    result = await crypto_dt_source.get_hf_models()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.get("/crypto-dt-source/datasets")
async def get_crypto_dt_datasets():
    """
    Get list of available HuggingFace datasets in Crypto DT Source
    
    Returns 5 crypto datasets including Bitcoin, Ethereum, Solana, and Ripple data
    """
    result = await crypto_dt_source.get_hf_datasets()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


# ==================== UNIFIED ENDPOINTS WITH FALLBACK ====================

@router.get("/prices/unified")
async def get_unified_prices(
    ids: str = Query("bitcoin,ethereum", description="Comma-separated coin IDs")
):
    """
    Get cryptocurrency prices with automatic fallback
    
    Priority:
    1. Crypto DT Source (CoinGecko)
    2. Direct CoinGecko (if available)
    3. Other market data providers
    """
    
    async def fetch_from_crypto_dt():
        result = await crypto_dt_source.get_coingecko_price(ids=ids, vs_currencies="usd")
        if result["success"]:
            return result["data"]
        raise Exception(result.get("error", "Unknown error"))
    
    # Add provider to fallback if not already added
    if not price_fallback.providers:
        price_fallback.add_provider("CryptoDTSource", 1, fetch_from_crypto_dt, cooldown_seconds=180)
    
    result = await price_fallback.fetch_with_fallback()
    
    return {
        "success": result["success"],
        "data": result.get("data"),
        "provider": result.get("provider"),
        "attempts": result.get("attempts"),
        "timestamp": result.get("timestamp")
    }


@router.get("/resources/unified")
async def get_unified_resources(
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get cryptocurrency resources with automatic fallback
    
    Priority:
    1. Crypto API Clean (281+ resources)
    2. Other resource databases (if available)
    """
    
    async def fetch_from_crypto_api_clean():
        if category:
            result = await crypto_api_clean.get_resources_by_category(category)
        else:
            result = await crypto_api_clean.get_all_resources()
        
        if result["success"]:
            return result["data"]
        raise Exception(result.get("error", "Unknown error"))
    
    # Add provider to fallback if not already added
    if not resources_fallback.providers:
        resources_fallback.add_provider("CryptoAPIClean", 1, fetch_from_crypto_api_clean, cooldown_seconds=180)
    
    result = await resources_fallback.fetch_with_fallback()
    
    return {
        "success": result["success"],
        "data": result.get("data"),
        "provider": result.get("provider"),
        "attempts": result.get("attempts")
    }


# ==================== STATUS & HEALTH ====================

@router.get("/status")
async def get_new_sources_status():
    """
    Get comprehensive status of all new data sources
    """
    crypto_api_clean_health = await crypto_api_clean.health_check()
    crypto_dt_source_health = await crypto_dt_source.health_check()
    
    return {
        "sources": {
            "crypto_api_clean": {
                "name": "Crypto API Clean",
                "base_url": crypto_api_clean.base_url,
                "status": "operational" if crypto_api_clean_health["success"] else "degraded",
                "features": [
                    "281+ cryptocurrency resources",
                    "12 resource categories",
                    "RPC nodes, block explorers, market data APIs",
                    "News APIs, sentiment APIs, on-chain analytics",
                    "Whale tracking, HuggingFace resources"
                ],
                "health": crypto_api_clean_health,
                "priority": 2,
                "weight": 75
            },
            "crypto_dt_source": {
                "name": "Crypto DT Source",
                "base_url": crypto_dt_source.base_url,
                "status": "operational" if crypto_dt_source_health["success"] else "degraded",
                "features": [
                    "Unified cryptocurrency data API v2.0.0",
                    "4 HuggingFace sentiment models",
                    "5 crypto datasets",
                    "CoinGecko prices, Binance klines",
                    "Fear & Greed Index, Reddit posts, RSS feeds"
                ],
                "health": crypto_dt_source_health,
                "priority": 2,
                "weight": 75
            }
        },
        "integration": {
            "fallback_enabled": True,
            "total_new_sources": 2,
            "total_resources_added": "281+",
            "integrated_date": "2025-12-13"
        }
    }


@router.get("/test-all")
async def test_all_new_sources():
    """
    Test all new data sources to verify integration
    """
    results = {}
    
    # Test Crypto API Clean
    try:
        stats = await crypto_api_clean.get_resources_stats()
        results["crypto_api_clean"] = {
            "status": "success" if stats["success"] else "failed",
            "data": stats.get("data"),
            "response_time_ms": stats.get("response_time_ms")
        }
    except Exception as e:
        results["crypto_api_clean"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Test Crypto DT Source
    try:
        status = await crypto_dt_source.get_status()
        btc_price = await crypto_dt_source.get_btc_price()
        results["crypto_dt_source"] = {
            "status": "success" if status["success"] else "failed",
            "system_status": status.get("data"),
            "btc_price": btc_price,
            "response_time_ms": status.get("response_time_ms")
        }
    except Exception as e:
        results["crypto_dt_source"] = {
            "status": "error",
            "error": str(e)
        }
    
    return {
        "test_results": results,
        "timestamp": "2025-12-13",
        "all_tests_passed": all(r.get("status") == "success" for r in results.values())
    }
