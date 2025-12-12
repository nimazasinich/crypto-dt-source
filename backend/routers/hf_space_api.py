"""
HF Space Complete API Router
Implements all required endpoints for Hugging Face Space deployment
using REAL data providers managed by the Orchestrator.
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

# Import Orchestrator
from backend.orchestration.provider_manager import provider_manager

# Ensure real providers are registered (side-effect import)
from backend.live_data import providers as _live_providers  # noqa: F401

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
    latency_ms: Optional[float] = None

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
    Uses Provider Orchestrator (CoinGecko, Binance, etc.)
    """
    response = await provider_manager.fetch_data(
        "market",
        params={"ids": "bitcoin,ethereum,tron,solana,binancecoin,ripple", "vs_currency": "usd"},
        use_cache=True,
        ttl=60
    )
    
    if not response["success"]:
        raise HTTPException(status_code=503, detail=response["error"])
        
    data = response["data"]
    items = []
    
    # Handle different provider formats if needed, but fetch functions should normalize
    # Assuming coingecko format for "market" category list
    if isinstance(data, list):
        for coin in data:
            items.append(MarketItem(
                symbol=coin.get('symbol', '').upper(),
                price=coin.get('current_price', 0),
                change_24h=coin.get('price_change_percentage_24h', 0),
                volume_24h=coin.get('total_volume', 0),
                source=response["source"]
            ))
            
    return MarketResponse(
        last_updated=response["timestamp"],
        items=items,
        meta=MetaInfo(
            cache_ttl_seconds=60, 
            source=response["source"],
            latency_ms=response.get("latency_ms")
        )
    )

@router.get("/api/market/ohlc")
async def get_ohlc(
    symbol: str = Query(..., description="Trading symbol (e.g., BTC)"),
    interval: int = Query(60, description="Interval in minutes"),
    limit: int = Query(100, description="Number of candles")
):
    """Get OHLC candlestick data via Orchestrator"""
    
    # Map minutes to common string format if needed by providers, 
    # but fetch_binance_klines handles it.
    interval_str = "1h"
    if interval < 60:
        interval_str = f"{interval}m"
    elif interval == 60:
        interval_str = "1h"
    elif interval == 240:
        interval_str = "4h"
    elif interval == 1440:
        interval_str = "1d"

    response = await provider_manager.fetch_data(
        "ohlc",
        params={
            "symbol": symbol,
            "interval": interval_str,
            "limit": limit
        },
        use_cache=True,
        ttl=60
    )

    if not response["success"]:
        raise HTTPException(status_code=503, detail=response["error"])

    # Transform provider-specific format to standard OHLC
    # - Binance klines: [time, open, high, low, close, volume, ...]
    # - CoinGecko OHLC: [timestamp, open, high, low, close]
    klines = response["data"]
    ohlc_data = []
    
    if isinstance(klines, list):
        for k in klines:
            if isinstance(k, list) and len(k) >= 6:
                ohlc_data.append({
                    "ts": int(k[0] / 1000),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5])
                })
            elif isinstance(k, list) and len(k) == 5:
                # CoinGecko OHLC (ms timestamp)
                ts_raw = k[0]
                try:
                    ts = int(ts_raw / 1000) if isinstance(ts_raw, (int, float)) and ts_raw > 10**11 else int(ts_raw)
                except Exception:
                    continue
                try:
                    ohlc_data.append(
                        {
                            "ts": ts,
                            "open": float(k[1]),
                            "high": float(k[2]),
                            "low": float(k[3]),
                            "close": float(k[4]),
                            "volume": 0.0,
                        }
                    )
                except Exception:
                    continue

    return {
        "symbol": symbol,
        "interval": interval,
        "data": ohlc_data,
        "meta": MetaInfo(
            cache_ttl_seconds=60, 
            source=response["source"],
            latency_ms=response.get("latency_ms")
        ).dict()
    }

# ============================================================================
# News & Sentiment Endpoints
# ============================================================================

@router.get("/api/news", response_model=NewsResponse)
async def get_news(
    limit: int = Query(20, description="Number of articles"),
    source: Optional[str] = Query(None, description="Filter by source")
):
    """Get cryptocurrency news via Orchestrator"""
    
    response = await provider_manager.fetch_data(
        "news",
        params={"filter": "hot", "query": "crypto"}, # Params for different providers
        use_cache=True,
        ttl=300
    )
    
    if not response["success"]:
        return NewsResponse(articles=[], meta=MetaInfo(source="error"))

    data = response["data"]
    articles = []
    
    # Normalize CryptoPanic / NewsAPI formats
    if "results" in data: # CryptoPanic
        for post in data.get('results', [])[:limit]:
            articles.append(NewsArticle(
                id=str(post.get('id')),
                title=post.get('title', ''),
                url=post.get('url', ''),
                source=post.get('source', {}).get('title', 'Unknown'),
                summary=post.get('slug', ''),
                published_at=post.get('published_at', datetime.now().isoformat())
            ))
    elif "articles" in data: # NewsAPI
        for post in data.get('articles', [])[:limit]:
            articles.append(NewsArticle(
                id=str(hash(post.get('url', ''))),
                title=post.get('title', ''),
                url=post.get('url', ''),
                source=post.get('source', {}).get('name', 'Unknown'),
                summary=post.get('description', ''),
                published_at=post.get('publishedAt', datetime.now().isoformat())
            ))

    return NewsResponse(
        articles=articles,
        meta=MetaInfo(
            cache_ttl_seconds=300, 
            source=response["source"],
            latency_ms=response.get("latency_ms")
        )
    )


@router.get("/api/sentiment/global")
async def get_global_sentiment():
    """Get global market sentiment via Orchestrator"""
    
    response = await provider_manager.fetch_data(
        "sentiment",
        params={"limit": 1},
        use_cache=True,
        ttl=3600
    )
    
    if not response["success"]:
        raise HTTPException(status_code=503, detail=response["error"])
        
    data = response["data"]
    fng_value = 50
    classification = "Neutral"
    
    # Alternative.me format
    if data.get('data'):
        item = data['data'][0]
        fng_value = int(item.get('value', 50))
        classification = item.get('value_classification', 'Neutral')
        
    return {
        "score": fng_value,
        "label": classification,
        "meta": MetaInfo(
            cache_ttl_seconds=3600, 
            source=response["source"],
            latency_ms=response.get("latency_ms")
        ).dict()
    }

# ============================================================================
# Blockchain Endpoints
# ============================================================================

@router.get("/api/crypto/blockchain/gas", response_model=GasResponse)
async def get_gas_prices(chain: str = Query("ethereum", description="Blockchain network")):
    """Get gas prices via Orchestrator"""
    
    if chain.lower() != "ethereum":
        # Fallback or implement other chains
        return GasResponse(
            chain=chain,
            gas_prices=None,
            timestamp=datetime.now().isoformat(),
            meta=MetaInfo(source="unavailable")
        )

    response = await provider_manager.fetch_data(
        "onchain",
        params={},
        use_cache=True,
        ttl=15
    )
    
    if not response["success"]:
        return GasResponse(
            chain=chain,
            gas_prices=None,
            timestamp=datetime.now().isoformat(),
            meta=MetaInfo(source="unavailable")
        )
        
    data = response["data"]
    result = data.get("result", {})
    
    gas_price = None
    if result:
        # Etherscan returns data in result
        try:
            gas_price = GasPrice(
                fast=float(result.get("FastGasPrice", 0)),
                standard=float(result.get("ProposeGasPrice", 0)),
                slow=float(result.get("SafeGasPrice", 0))
            )
        except:
            pass

    return GasResponse(
        chain=chain,
        gas_prices=gas_price,
        timestamp=datetime.now().isoformat(),
        meta=MetaInfo(
            cache_ttl_seconds=15, 
            source=response["source"],
            latency_ms=response.get("latency_ms")
        )
    )

# ============================================================================
# System Management
# ============================================================================

@router.get("/api/status")
async def get_system_status():
    """Get overall system status"""
    stats = provider_manager.get_stats()
    
    return {
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'providers': stats,
        'version': '2.0.0',
        'meta': MetaInfo(source="system").dict()
    }
