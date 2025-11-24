#!/usr/bin/env python3
"""
Unified API Service
FastAPI service that uses UnifiedResourceLoader to provide access to all crypto data
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
import httpx
import asyncio
from datetime import datetime
import logging

from unified_resource_loader import get_loader, APIResource

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize APIRouter instead of FastAPI app
router = APIRouter(prefix="/api", tags=["unified"])

# Global loader instance
loader = None


def init_loader():
    """Initialize the resource loader"""
    global loader
    if loader is None:
        loader = get_loader()
        logger.info(f"✅ Loaded {len(loader.resources)} resources")
    return loader


# ==================== RESOURCE ENDPOINTS ====================

@router.get("/resources/stats")
async def get_resource_stats():
    """Get statistics about available resources"""
    return loader.get_stats()


@router.get("/resources/categories")
async def get_categories():
    """Get list of all available categories"""
    return {
        "categories": loader.get_available_categories(),
        "total": len(loader.get_available_categories())
    }


@router.get("/resources/category/{category}")
async def get_resources_by_category(category: str):
    """Get all resources in a specific category"""
    resources = loader.get_resources_by_category(category)

    return {
        "category": category,
        "count": len(resources),
        "resources": [
            {
                "id": r.id,
                "name": r.name,
                "base_url": r.base_url,
                "requires_auth": r.requires_auth(),
                "priority": r.priority,
                "docs_url": r.docs_url
            }
            for r in resources
        ]
    }


@router.get("/resources/search")
async def search_resources(q: str = Query(..., min_length=2)):
    """Search resources by name or ID"""
    results = loader.search_resources(q)

    return {
        "query": q,
        "count": len(results),
        "results": [
            {
                "id": r.id,
                "name": r.name,
                "category": r.category,
                "base_url": r.base_url
            }
            for r in results
        ]
    }


@router.get("/resources/{resource_id}")
async def get_resource_details(resource_id: str):
    """Get detailed information about a specific resource"""
    resource = loader.get_resource(resource_id)

    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource '{resource_id}' not found")

    return {
        "id": resource.id,
        "name": resource.name,
        "category": resource.category,
        "base_url": resource.base_url,
        "auth_type": resource.auth_type,
        "requires_auth": resource.requires_auth(),
        "has_key": resource.api_key is not None,
        "endpoints": resource.endpoints,
        "docs_url": resource.docs_url,
        "notes": resource.notes,
        "priority": resource.priority
    }


# ==================== MARKET DATA ENDPOINTS ====================

async def fetch_from_resource(resource: APIResource, endpoint: str = "", params: Dict = None) -> Dict:
    """Generic function to fetch data from a resource"""
    try:
        url = resource.get_full_url(endpoint)
        headers = resource.get_headers()
        query_params = {**resource.get_query_params(), **(params or {})}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            return response.json()

    except Exception as e:
        logger.error(f"Error fetching from {resource.id}: {e}")
        return None


@router.get("/market/price/{symbol}")
async def get_price(symbol: str):
    """Get current price for a cryptocurrency symbol"""
    symbol = symbol.lower()

    # Try CoinGecko first (primary free source)
    coingecko = loader.get_resource("coingecko")
    if coingecko:
        data = await fetch_from_resource(
            coingecko,
            f"simple/price?ids={symbol}&vs_currencies=usd,btc"
        )
        if data and symbol in data:
            return {
                "symbol": symbol,
                "source": "coingecko",
                "data": data[symbol],
                "timestamp": datetime.now().isoformat()
            }

    # Fallback to Binance
    binance = loader.get_resource("binance_public")
    if binance:
        pair = f"{symbol.upper()}USDT"
        data = await fetch_from_resource(
            binance,
            f"api/v3/ticker/price?symbol={pair}"
        )
        if data:
            return {
                "symbol": symbol,
                "source": "binance",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }

    raise HTTPException(status_code=404, detail=f"Price data not available for {symbol}")


@router.get("/market/prices")
async def get_multiple_prices(symbols: str = Query(..., description="Comma-separated symbols")):
    """Get prices for multiple cryptocurrencies"""
    symbol_list = [s.strip().lower() for s in symbols.split(",")]

    coingecko = loader.get_resource("coingecko")
    if not coingecko:
        raise HTTPException(status_code=503, detail="Market data service unavailable")

    ids = ",".join(symbol_list)
    data = await fetch_from_resource(
        coingecko,
        f"simple/price?ids={ids}&vs_currencies=usd,btc,eth"
    )

    if not data:
        raise HTTPException(status_code=503, detail="Failed to fetch price data")

    return {
        "symbols": symbol_list,
        "source": "coingecko",
        "data": data,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/market/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    days: int = Query(7, ge=1, le=365),
    interval: str = Query("daily", regex="^(daily|hourly)$")
):
    """Get historical price data for a cryptocurrency"""
    symbol = symbol.lower()

    # CoinGecko historical data
    coingecko = loader.get_resource("coingecko")
    if coingecko:
        endpoint = f"coins/{symbol}/market_chart?vs_currency=usd&days={days}"
        if interval == "hourly":
            endpoint += "&interval=hourly"

        data = await fetch_from_resource(coingecko, endpoint)
        if data:
            return {
                "symbol": symbol,
                "days": days,
                "interval": interval,
                "source": "coingecko",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }

    # Fallback to Binance klines
    binance = loader.get_resource("binance_public")
    if binance:
        pair = f"{symbol.upper()}USDT"
        interval_map = {"hourly": "1h", "daily": "1d"}
        kline_interval = interval_map.get(interval, "1d")

        data = await fetch_from_resource(
            binance,
            f"api/v3/klines?symbol={pair}&interval={kline_interval}&limit={days * 24 if interval == 'hourly' else days}"
        )
        if data:
            return {
                "symbol": symbol,
                "days": days,
                "interval": interval,
                "source": "binance",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }

    raise HTTPException(status_code=404, detail=f"Historical data not available for {symbol}")


@router.get("/market/trending")
async def get_trending_coins():
    """Get trending cryptocurrencies"""
    coingecko = loader.get_resource("coingecko")
    if not coingecko:
        raise HTTPException(status_code=503, detail="Service unavailable")

    data = await fetch_from_resource(coingecko, "search/trending")

    if not data:
        raise HTTPException(status_code=503, detail="Failed to fetch trending data")

    return {
        "source": "coingecko",
        "data": data,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/market/global")
async def get_global_market_data():
    """Get global cryptocurrency market data"""
    coingecko = loader.get_resource("coingecko")
    if not coingecko:
        raise HTTPException(status_code=503, detail="Service unavailable")

    data = await fetch_from_resource(coingecko, "global")

    if not data:
        raise HTTPException(status_code=503, detail="Failed to fetch global data")

    return {
        "source": "coingecko",
        "data": data,
        "timestamp": datetime.now().isoformat()
    }


# ==================== NEWS ENDPOINTS ====================

@router.get("/news")
async def get_crypto_news(limit: int = Query(10, ge=1, le=50)):
    """Get latest cryptocurrency news"""
    news_sources = loader.get_primary_resources("news")

    all_news = []

    # Try CryptoPanic first
    cryptopanic = loader.get_resource("cryptopanic")
    if cryptopanic:
        data = await fetch_from_resource(cryptopanic, f"posts/?public=true")
        if data and "results" in data:
            all_news.extend([
                {
                    "source": "cryptopanic",
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "published_at": item.get("published_at"),
                    "domain": item.get("domain")
                }
                for item in data["results"][:limit]
            ])

    # Try CoinStats News
    coinstats_news = loader.get_resource("coinstats_news")
    if coinstats_news and len(all_news) < limit:
        data = await fetch_from_resource(coinstats_news, "public/v1/news")
        if data and isinstance(data, list):
            all_news.extend([
                {
                    "source": "coinstats",
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "published_at": item.get("feedDate"),
                    "description": item.get("description")
                }
                for item in data[:limit - len(all_news)]
            ])

    return {
        "count": len(all_news),
        "news": all_news[:limit],
        "timestamp": datetime.now().isoformat()
    }


# ==================== SENTIMENT ENDPOINTS ====================

@router.get("/sentiment/fear-greed")
async def get_fear_greed_index():
    """Get Fear & Greed Index"""
    # Try alternative.me
    altme = loader.get_resource("alternative_me_fng")
    if altme:
        data = await fetch_from_resource(altme, "fng/?limit=1&format=json")
        if data:
            return {
                "source": "alternative.me",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }

    # Try other sources
    cfgi = loader.get_resource("cfgi_v1")
    if cfgi:
        data = await fetch_from_resource(cfgi, "v1/fear-greed")
        if data:
            return {
                "source": "cfgi",
                "data": data,
                "timestamp": datetime.now().isoformat()
            }

    raise HTTPException(status_code=503, detail="Fear & Greed index unavailable")


@router.get("/sentiment/social/{symbol}")
async def get_social_sentiment(symbol: str):
    """Get social sentiment for a cryptocurrency"""
    symbol = symbol.lower()

    # This would integrate with LunarCrush, Santiment, etc.
    # For now, return structure for future implementation

    return {
        "symbol": symbol,
        "message": "Social sentiment endpoint - ready for integration",
        "available_sources": [r.name for r in loader.get_resources_by_category("sentiment")],
        "timestamp": datetime.now().isoformat()
    }


# ==================== TRADING PAIRS ENDPOINT ====================

@router.get("/trading-pairs")
async def get_trading_pairs():
    """Get available trading pairs"""
    # Read from trading_pairs.txt if exists
    try:
        with open("trading_pairs.txt", "r") as f:
            pairs = [line.strip() for line in f if line.strip()]

        return {
            "count": len(pairs),
            "pairs": pairs,
            "timestamp": datetime.now().isoformat()
        }
    except FileNotFoundError:
        # Fallback: get from Binance
        binance = loader.get_resource("binance_public")
        if binance:
            data = await fetch_from_resource(binance, "api/v3/exchangeInfo")
            if data and "symbols" in data:
                pairs = [
                    f"{s['baseAsset']}/{s['quoteAsset']}"
                    for s in data["symbols"]
                    if s["status"] == "TRADING"
                ]
                return {
                    "count": len(pairs),
                    "pairs": pairs,
                    "source": "binance",
                    "timestamp": datetime.now().isoformat()
                }

        raise HTTPException(status_code=503, detail="Trading pairs unavailable")


# ==================== PROVIDER STATUS ====================

@router.get("/providers/status")
async def get_provider_status():
    """Get status of all configured providers"""
    categories = loader.get_available_categories()

    status = {
        "total_resources": len(loader.resources),
        "categories": {},
        "timestamp": datetime.now().isoformat()
    }

    for category in categories:
        resources = loader.get_resources_by_category(category)
        free_count = len([r for r in resources if not r.requires_auth()])
        auth_count = len([r for r in resources if r.requires_auth()])

        status["categories"][category] = {
            "total": len(resources),
            "free": free_count,
            "requires_auth": auth_count,
            "resources": [
                {
                    "id": r.id,
                    "name": r.name,
                    "requires_auth": r.requires_auth(),
                    "has_key": r.api_key is not None
                }
                for r in resources
            ]
        }

    return status


# ==================== HEALTH CHECK ====================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "resources_loaded": len(loader.resources) if loader else 0,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Unified Crypto Data API",
        "version": "1.0.0",
        "description": "Unified API for all cryptocurrency data sources",
        "resources_loaded": len(loader.resources) if loader else 0,
        "endpoints": {
            "resources": "/api/resources/stats",
            "market": "/api/market/price/{symbol}",
            "news": "/api/news",
            "sentiment": "/api/sentiment/fear-greed",
            "health": "/api/health",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
