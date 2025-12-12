"""
HF Space Complete API Router
Implements all required endpoints for Hugging Face Space deployment
using REAL data providers.
"""
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging
import asyncio
import json
import os
from pathlib import Path

# Import Real Data Providers
from backend.live_data.providers import (
    coingecko_provider, 
    binance_provider, 
    cryptopanic_provider, 
    alternative_me_provider
)
from backend.cache.cache_manager import cache_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["HF Space Complete API"])

# ============================================================================
# Pydantic Models for Request/Response
# ============================================================================

class MetaInfo(BaseModel):
    """Metadata for all responses"""
    cache_ttl_seconds: int = Field(default=30, description="Cache TTL in seconds")
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    source: str = Field(default="live", description="Data source")

class MarketItem(BaseModel):
    """Market ticker item"""
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    source: str = "live"

class MarketResponse(BaseModel):
    """Market snapshot response"""
    last_updated: str
    items: List[MarketItem]
    meta: MetaInfo

class NewsArticle(BaseModel):
    """News article"""
    id: str
    title: str
    url: str
    source: str
    summary: Optional[str] = None
    published_at: str

class NewsResponse(BaseModel):
    """News response"""
    articles: List[NewsArticle]
    meta: MetaInfo

class SentimentResponse(BaseModel):
    """Sentiment analysis response"""
    score: float
    label: str  # positive, negative, neutral
    details: Optional[Dict[str, Any]] = None
    meta: MetaInfo

class GasPrice(BaseModel):
    """Gas price information"""
    fast: float
    standard: float
    slow: float
    unit: str = "gwei"

class GasResponse(BaseModel):
    """Gas price response"""
    chain: str
    gas_prices: Optional[GasPrice] = None
    timestamp: str
    meta: MetaInfo

# ============================================================================
# Market & Pairs Endpoints
# ============================================================================

@router.get("/api/market", response_model=MarketResponse)
async def get_market_snapshot():
    """
    Get current market snapshot with prices, changes, and volumes.
    Uses CoinGecko API.
    """
    cache_key = "market_snapshot"
    cached = await cache_manager.get(cache_key)
    if cached:
        return cached

    try:
        data = await coingecko_provider.get_market_data(ids="bitcoin,ethereum,tron,solana,binancecoin,ripple")
        
        items = []
        for coin in data:
            items.append(MarketItem(
                symbol=coin.get('symbol', '').upper(),
                price=coin.get('current_price', 0),
                change_24h=coin.get('price_change_percentage_24h', 0),
                volume_24h=coin.get('total_volume', 0),
                source="coingecko"
            ))
        
        response = MarketResponse(
            last_updated=datetime.now().isoformat(),
            items=items,
            meta=MetaInfo(cache_ttl_seconds=60, source="coingecko")
        )
        
        await cache_manager.set(cache_key, response, ttl=60)
        return response
    
    except Exception as e:
        logger.error(f"Error in get_market_snapshot: {e}")
        # Return empty list or cached stale data if available, but NEVER fake data
        raise HTTPException(status_code=503, detail="Market data unavailable")

@router.get("/api/market/ohlc")
async def get_ohlc(
    symbol: str = Query(..., description="Trading symbol (e.g., BTC)"),
    interval: int = Query(60, description="Interval in minutes"),
    limit: int = Query(100, description="Number of candles")
):
    """Get OHLC candlestick data from Binance"""
    cache_key = f"ohlc_{symbol}_{interval}_{limit}"
    cached = await cache_manager.get(cache_key)
    if cached:
        return cached

    try:
        # Map minutes to Binance intervals
        binance_interval = "1h"
        if interval == 1: binance_interval = "1m"
        elif interval == 5: binance_interval = "5m"
        elif interval == 15: binance_interval = "15m"
        elif interval == 60: binance_interval = "1h"
        elif interval == 240: binance_interval = "4h"
        elif interval == 1440: binance_interval = "1d"

        # Binance symbol needs to be e.g., BTCUSDT
        formatted_symbol = symbol.upper()
        if not formatted_symbol.endswith("USDT") and not formatted_symbol.endswith("USD"):
             formatted_symbol += "USDT"
        
        klines = await binance_provider.get_klines(formatted_symbol, interval=binance_interval, limit=limit)
        
        ohlc_data = []
        for k in klines:
            # Binance kline: [open_time, open, high, low, close, volume, ...]
            ohlc_data.append({
                "ts": int(k[0] / 1000),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5])
            })
        
        response = {
            "symbol": symbol,
            "interval": interval,
            "data": ohlc_data,
            "meta": MetaInfo(cache_ttl_seconds=60, source="binance").dict()
        }
        
        await cache_manager.set(cache_key, response, ttl=60)
        return response

    except Exception as e:
        logger.error(f"Error in get_ohlc: {e}")
        # Try fallbacks? For now, fail gracefully.
        raise HTTPException(status_code=503, detail="OHLC data unavailable")

# ============================================================================
# News & Sentiment Endpoints
# ============================================================================

@router.get("/api/news", response_model=NewsResponse)
async def get_news(
    limit: int = Query(20, description="Number of articles"),
    source: Optional[str] = Query(None, description="Filter by source")
):
    """Get cryptocurrency news from CryptoPanic"""
    cache_key = f"news_{limit}_{source}"
    cached = await cache_manager.get(cache_key)
    if cached:
        return cached

    try:
        data = await cryptopanic_provider.get_news()
        
        articles = []
        results = data.get('results', [])[:limit]
        
        for post in results:
            articles.append(NewsArticle(
                id=str(post.get('id')),
                title=post.get('title', ''),
                url=post.get('url', ''),
                source=post.get('source', {}).get('title', 'Unknown'),
                summary=post.get('slug', ''),
                published_at=post.get('published_at', datetime.now().isoformat())
            ))
        
        response = NewsResponse(
            articles=articles,
            meta=MetaInfo(cache_ttl_seconds=300, source="cryptopanic")
        )
        
        await cache_manager.set(cache_key, response, ttl=300)
        return response
    
    except Exception as e:
        logger.error(f"Error in get_news: {e}")
        return NewsResponse(articles=[], meta=MetaInfo(source="error"))


@router.get("/api/sentiment/global")
async def get_global_sentiment():
    """Get global market sentiment (Fear & Greed Index)"""
    cache_key = "sentiment_global"
    cached = await cache_manager.get(cache_key)
    if cached:
        return cached
        
    try:
        data = await alternative_me_provider.get_fear_and_greed()
        fng_value = 50
        classification = "Neutral"
        
        if data.get('data'):
            item = data['data'][0]
            fng_value = int(item.get('value', 50))
            classification = item.get('value_classification', 'Neutral')
            
        result = {
            "score": fng_value,
            "label": classification,
            "meta": MetaInfo(cache_ttl_seconds=3600, source="alternative.me").dict()
        }
        
        await cache_manager.set(cache_key, result, ttl=3600)
        return result
    except Exception as e:
        logger.error(f"Error in get_global_sentiment: {e}")
        raise HTTPException(status_code=503, detail="Sentiment data unavailable")

# ============================================================================
# Blockchain Endpoints
# ============================================================================

@router.get("/api/crypto/blockchain/gas", response_model=GasResponse)
async def get_gas_prices(chain: str = Query("ethereum", description="Blockchain network")):
    """Get gas prices - Placeholder for real implementation"""
    # TODO: Implement Etherscan or similar provider
    # For now, return empty/null to indicate no data rather than fake data
    return GasResponse(
        chain=chain,
        gas_prices=None,
        timestamp=datetime.now().isoformat(),
        meta=MetaInfo(source="unavailable")
    )

# ============================================================================
# System Management
# ============================================================================

@router.get("/api/status")
async def get_system_status():
    """Get overall system status"""
    from backend.live_data.providers import get_all_providers_status
    
    provider_status = await get_all_providers_status()
    
    return {
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'providers': provider_status,
        'version': '1.0.0',
        'meta': MetaInfo(source="system").dict()
    }
