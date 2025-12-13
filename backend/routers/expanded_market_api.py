#!/usr/bin/env python3
"""
Expanded Market API Router - Additional Market Data Endpoints
Implements:
- POST /api/coins/search - Search coins by name/symbol
- GET /api/coins/{id}/details - Detailed coin information
- GET /api/coins/{id}/history - Historical price data (OHLCV)
- GET /api/coins/{id}/chart - Chart data (1h/24h/7d/30d/1y)
- GET /api/market/categories - Market categories
- GET /api/market/gainers - Top gainers (24h)
- GET /api/market/losers - Top losers (24h)
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging
import time
import httpx
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Expanded Market API"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CoinSearchRequest(BaseModel):
    """Request model for coin search"""
    q: str
    limit: int = 20


# ============================================================================
# Helper Functions
# ============================================================================

async def fetch_from_coingecko(endpoint: str, params: dict = None) -> dict:
    """Fetch data from CoinGecko API with error handling"""
    base_url = "https://api.coingecko.com/api/v3"
    url = f"{base_url}/{endpoint}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"CoinGecko API error ({endpoint}): {e}")
        raise HTTPException(status_code=502, detail=f"External API error: {str(e)}")


async def fetch_from_coinpaprika(endpoint: str) -> dict:
    """Fetch data from CoinPaprika API as fallback"""
    base_url = "https://api.coinpaprika.com/v1"
    url = f"{base_url}/{endpoint}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"CoinPaprika API error ({endpoint}): {e}")
        return None


async def fetch_from_coincap(endpoint: str) -> dict:
    """Fetch data from CoinCap API as fallback"""
    base_url = "https://api.coincap.io/v2"
    url = f"{base_url}/{endpoint}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("data", data)
    except Exception as e:
        logger.error(f"CoinCap API error ({endpoint}): {e}")
        return None


# ============================================================================
# POST /api/coins/search
# ============================================================================

@router.post("/api/coins/search")
async def search_coins(request: CoinSearchRequest):
    """
    Search coins by name or symbol
    
    This endpoint searches across multiple free APIs:
    - CoinGecko (primary)
    - CoinPaprika (fallback)
    - CoinCap (fallback)
    """
    try:
        query = request.q.lower().strip()
        limit = min(request.limit, 100)
        
        if not query or len(query) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
        
        # Try CoinGecko first
        try:
            coins_list = await fetch_from_coingecko("coins/list")
            
            # Filter coins matching query
            matches = [
                coin for coin in coins_list
                if query in coin.get("id", "").lower() or 
                   query in coin.get("symbol", "").lower() or 
                   query in coin.get("name", "").lower()
            ][:limit]
            
            # Fetch market data for matches
            if matches:
                coin_ids = ",".join([c["id"] for c in matches[:50]])
                market_data = await fetch_from_coingecko(
                    "coins/markets",
                    params={
                        "vs_currency": "usd",
                        "ids": coin_ids,
                        "order": "market_cap_desc"
                    }
                )
                
                results = []
                for coin in market_data[:limit]:
                    results.append({
                        "id": coin.get("id"),
                        "symbol": coin.get("symbol", "").upper(),
                        "name": coin.get("name"),
                        "image": coin.get("image"),
                        "current_price": coin.get("current_price"),
                        "market_cap": coin.get("market_cap"),
                        "market_cap_rank": coin.get("market_cap_rank"),
                        "price_change_24h": coin.get("price_change_percentage_24h"),
                        "total_volume": coin.get("total_volume")
                    })
                
                return {
                    "success": True,
                    "query": request.q,
                    "count": len(results),
                    "results": results,
                    "source": "coingecko",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
        
        except Exception as e:
            logger.warning(f"CoinGecko search failed: {e}, trying fallback...")
        
        # Fallback to CoinPaprika
        try:
            coins = await fetch_from_coinpaprika("coins")
            matches = [
                coin for coin in coins
                if query in coin.get("id", "").lower() or 
                   query in coin.get("symbol", "").lower() or 
                   query in coin.get("name", "").lower()
            ][:limit]
            
            results = []
            for coin in matches:
                # Fetch ticker data
                ticker = await fetch_from_coinpaprika(f"tickers/{coin['id']}")
                if ticker:
                    results.append({
                        "id": coin.get("id"),
                        "symbol": coin.get("symbol", "").upper(),
                        "name": coin.get("name"),
                        "image": "",
                        "current_price": ticker.get("quotes", {}).get("USD", {}).get("price", 0),
                        "market_cap": ticker.get("quotes", {}).get("USD", {}).get("market_cap", 0),
                        "market_cap_rank": coin.get("rank", 0),
                        "price_change_24h": ticker.get("quotes", {}).get("USD", {}).get("percent_change_24h", 0),
                        "total_volume": ticker.get("quotes", {}).get("USD", {}).get("volume_24h", 0)
                    })
            
            return {
                "success": True,
                "query": request.q,
                "count": len(results),
                "results": results,
                "source": "coinpaprika",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        
        except Exception as e:
            logger.error(f"All search APIs failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="Search service temporarily unavailable"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/coins/{id}/details
# ============================================================================

@router.get("/api/coins/{coin_id}/details")
async def get_coin_details(coin_id: str):
    """
    Get detailed information about a specific coin
    
    Returns comprehensive data including:
    - Basic info (name, symbol, description)
    - Market data (price, volume, market cap)
    - Supply information
    - ATH/ATL data
    - Links and social media
    """
    try:
        # Try CoinGecko first
        try:
            data = await fetch_from_coingecko(f"coins/{coin_id}")
            
            return {
                "success": True,
                "id": data.get("id"),
                "symbol": data.get("symbol", "").upper(),
                "name": data.get("name"),
                "description": data.get("description", {}).get("en", "")[:500] + "...",
                "image": data.get("image", {}).get("large"),
                "categories": data.get("categories", []),
                "market_data": {
                    "current_price": data.get("market_data", {}).get("current_price", {}).get("usd"),
                    "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd"),
                    "market_cap_rank": data.get("market_cap_rank"),
                    "total_volume": data.get("market_data", {}).get("total_volume", {}).get("usd"),
                    "high_24h": data.get("market_data", {}).get("high_24h", {}).get("usd"),
                    "low_24h": data.get("market_data", {}).get("low_24h", {}).get("usd"),
                    "price_change_24h": data.get("market_data", {}).get("price_change_percentage_24h"),
                    "price_change_7d": data.get("market_data", {}).get("price_change_percentage_7d"),
                    "price_change_30d": data.get("market_data", {}).get("price_change_percentage_30d"),
                    "circulating_supply": data.get("market_data", {}).get("circulating_supply"),
                    "total_supply": data.get("market_data", {}).get("total_supply"),
                    "max_supply": data.get("market_data", {}).get("max_supply"),
                    "ath": data.get("market_data", {}).get("ath", {}).get("usd"),
                    "ath_date": data.get("market_data", {}).get("ath_date", {}).get("usd"),
                    "atl": data.get("market_data", {}).get("atl", {}).get("usd"),
                    "atl_date": data.get("market_data", {}).get("atl_date", {}).get("usd")
                },
                "links": {
                    "homepage": data.get("links", {}).get("homepage", []),
                    "blockchain_site": data.get("links", {}).get("blockchain_site", [])[:3],
                    "twitter": data.get("links", {}).get("twitter_screen_name"),
                    "telegram": data.get("links", {}).get("telegram_channel_identifier")
                },
                "source": "coingecko",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        
        except Exception as e:
            logger.warning(f"CoinGecko details failed: {e}, trying fallback...")
        
        # Fallback to CoinPaprika
        coin_info = await fetch_from_coinpaprika(f"coins/{coin_id}")
        ticker = await fetch_from_coinpaprika(f"tickers/{coin_id}")
        
        if not coin_info or not ticker:
            raise HTTPException(status_code=404, detail=f"Coin {coin_id} not found")
        
        return {
            "success": True,
            "id": coin_info.get("id"),
            "symbol": coin_info.get("symbol", "").upper(),
            "name": coin_info.get("name"),
            "description": coin_info.get("description", "")[:500] + "...",
            "image": "",
            "categories": [],
            "market_data": {
                "current_price": ticker.get("quotes", {}).get("USD", {}).get("price"),
                "market_cap": ticker.get("quotes", {}).get("USD", {}).get("market_cap"),
                "market_cap_rank": coin_info.get("rank"),
                "total_volume": ticker.get("quotes", {}).get("USD", {}).get("volume_24h"),
                "price_change_24h": ticker.get("quotes", {}).get("USD", {}).get("percent_change_24h"),
                "circulating_supply": ticker.get("circulating_supply"),
                "total_supply": ticker.get("total_supply"),
                "max_supply": ticker.get("max_supply"),
                "ath": ticker.get("quotes", {}).get("USD", {}).get("ath_price"),
                "ath_date": ticker.get("quotes", {}).get("USD", {}).get("ath_date")
            },
            "links": {
                "homepage": [coin_info.get("links", {}).get("website", [""])[0]],
                "twitter": coin_info.get("links", {}).get("twitter", [""])[0]
            },
            "source": "coinpaprika",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching coin details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/coins/{id}/history
# ============================================================================

@router.get("/api/coins/{coin_id}/history")
async def get_coin_history(
    coin_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
    interval: str = Query("daily", description="Data interval: daily, hourly")
):
    """
    Get historical price data (OHLCV) for a coin
    
    Supports multiple timeframes:
    - daily: Up to 365 days
    - hourly: Up to 90 days
    """
    try:
        # Map interval to CoinGecko format
        if interval == "hourly" and days > 90:
            days = 90
        
        data = await fetch_from_coingecko(
            f"coins/{coin_id}/market_chart",
            params={"vs_currency": "usd", "days": days}
        )
        
        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])
        market_caps = data.get("market_caps", [])
        
        # Format response
        history = []
        for i in range(len(prices)):
            history.append({
                "timestamp": prices[i][0],
                "date": datetime.fromtimestamp(prices[i][0] / 1000).isoformat() + "Z",
                "price": prices[i][1],
                "volume": volumes[i][1] if i < len(volumes) else 0,
                "market_cap": market_caps[i][1] if i < len(market_caps) else 0
            })
        
        return {
            "success": True,
            "coin_id": coin_id,
            "days": days,
            "interval": interval,
            "count": len(history),
            "data": history,
            "source": "coingecko",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/coins/{id}/chart
# ============================================================================

@router.get("/api/coins/{coin_id}/chart")
async def get_coin_chart(
    coin_id: str,
    timeframe: str = Query("24h", description="Timeframe: 1h, 24h, 7d, 30d, 1y")
):
    """
    Get chart data optimized for frontend display
    
    Supported timeframes:
    - 1h: Last hour (minute resolution)
    - 24h: Last 24 hours (hourly resolution)
    - 7d: Last 7 days (hourly resolution)
    - 30d: Last 30 days (daily resolution)
    - 1y: Last year (daily resolution)
    """
    try:
        # Map timeframe to days parameter
        timeframe_map = {
            "1h": 0.042,  # ~1 hour
            "24h": 1,
            "7d": 7,
            "30d": 30,
            "1y": 365
        }
        
        days = timeframe_map.get(timeframe, 1)
        
        data = await fetch_from_coingecko(
            f"coins/{coin_id}/market_chart",
            params={"vs_currency": "usd", "days": days}
        )
        
        prices = data.get("prices", [])
        
        # Format for charting
        chart_data = {
            "labels": [datetime.fromtimestamp(p[0] / 1000).strftime("%Y-%m-%d %H:%M") for p in prices],
            "prices": [p[1] for p in prices]
        }
        
        # Calculate statistics
        price_values = [p[1] for p in prices]
        stats = {
            "high": max(price_values) if price_values else 0,
            "low": min(price_values) if price_values else 0,
            "avg": sum(price_values) / len(price_values) if price_values else 0,
            "change": ((price_values[-1] - price_values[0]) / price_values[0] * 100) if len(price_values) > 1 else 0
        }
        
        return {
            "success": True,
            "coin_id": coin_id,
            "timeframe": timeframe,
            "chart": chart_data,
            "stats": stats,
            "source": "coingecko",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error fetching chart data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/market/categories
# ============================================================================

@router.get("/api/market/categories")
async def get_market_categories():
    """
    Get cryptocurrency market categories
    
    Returns categories like DeFi, NFT, Gaming, etc. with market data
    """
    try:
        data = await fetch_from_coingecko("coins/categories")
        
        categories = []
        for cat in data[:50]:  # Limit to top 50
            categories.append({
                "id": cat.get("id"),
                "name": cat.get("name"),
                "market_cap": cat.get("market_cap"),
                "market_cap_change_24h": cat.get("market_cap_change_24h"),
                "volume_24h": cat.get("volume_24h"),
                "top_3_coins": cat.get("top_3_coins", [])
            })
        
        return {
            "success": True,
            "count": len(categories),
            "categories": categories,
            "source": "coingecko",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/market/gainers
# ============================================================================

@router.get("/api/market/gainers")
async def get_top_gainers(limit: int = Query(10, ge=1, le=100)):
    """
    Get top gainers in the last 24 hours
    """
    try:
        # Fetch market data sorted by price change
        data = await fetch_from_coingecko(
            "coins/markets",
            params={
                "vs_currency": "usd",
                "order": "price_change_percentage_24h_desc",
                "per_page": limit,
                "page": 1,
                "sparkline": False
            }
        )
        
        gainers = []
        for coin in data:
            if coin.get("price_change_percentage_24h", 0) > 0:
                gainers.append({
                    "id": coin.get("id"),
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name"),
                    "image": coin.get("image"),
                    "current_price": coin.get("current_price"),
                    "price_change_24h": coin.get("price_change_percentage_24h"),
                    "market_cap": coin.get("market_cap"),
                    "volume_24h": coin.get("total_volume")
                })
        
        return {
            "success": True,
            "count": len(gainers),
            "gainers": gainers,
            "source": "coingecko",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error fetching gainers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/market/losers
# ============================================================================

@router.get("/api/market/losers")
async def get_top_losers(limit: int = Query(10, ge=1, le=100)):
    """
    Get top losers in the last 24 hours
    """
    try:
        # Fetch market data sorted by price change (ascending)
        data = await fetch_from_coingecko(
            "coins/markets",
            params={
                "vs_currency": "usd",
                "order": "price_change_percentage_24h_asc",
                "per_page": limit,
                "page": 1,
                "sparkline": False
            }
        )
        
        losers = []
        for coin in data:
            if coin.get("price_change_percentage_24h", 0) < 0:
                losers.append({
                    "id": coin.get("id"),
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name"),
                    "image": coin.get("image"),
                    "current_price": coin.get("current_price"),
                    "price_change_24h": coin.get("price_change_percentage_24h"),
                    "market_cap": coin.get("market_cap"),
                    "volume_24h": coin.get("total_volume")
                })
        
        return {
            "success": True,
            "count": len(losers),
            "losers": losers,
            "source": "coingecko",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Error fetching losers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


logger.info("✅ Expanded Market API Router loaded")
