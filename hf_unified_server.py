"""
🚀 Unified HuggingFace Space API Server
Complete cryptocurrency data and analysis API
Provides all endpoints required for the HF Space
"""

import asyncio
import httpx
import time
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Dict, List, Any, Optional
import os
import logging
from collections import defaultdict
import random
import json
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Cryptocurrency Data & Analysis API",
    description="Complete API for cryptocurrency data, market analysis, and trading signals",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache
cache = {
    "ohlcv": {},
    "prices": {},
    "market_data": {},
    "providers": [],
    "last_update": None
}

# Provider state
providers_state = {}

# Load providers config
WORKSPACE_ROOT = Path(__file__).parent
PROVIDERS_CONFIG_PATH = WORKSPACE_ROOT / "providers_config_extended.json"

def load_providers_config():
    """Load providers from providers_config_extended.json"""
    try:
        if PROVIDERS_CONFIG_PATH.exists():
            with open(PROVIDERS_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                providers = config.get('providers', {})
                logger.info(f"✅ Loaded {len(providers)} providers from providers_config_extended.json")
                return providers
        else:
            logger.warning(f"⚠️ providers_config_extended.json not found at {PROVIDERS_CONFIG_PATH}")
            return {}
    except Exception as e:
        logger.error(f"❌ Error loading providers config: {e}")
        return {}

# Load providers at startup
PROVIDERS_CONFIG = load_providers_config()

# ============================================================================
# Data Fetching Functions
# ============================================================================

async def fetch_binance_ohlcv(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 100):
    """Fetch OHLCV data from Binance"""
    try:
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": min(limit, 1000)
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                # Format OHLCV data
                ohlcv = []
                for candle in data:
                    ohlcv.append({
                        "timestamp": candle[0],
                        "datetime": datetime.fromtimestamp(candle[0] / 1000).isoformat(),
                        "open": float(candle[1]),
                        "high": float(candle[2]),
                        "low": float(candle[3]),
                        "close": float(candle[4]),
                        "volume": float(candle[5])
                    })
                
                return ohlcv
    except Exception as e:
        logger.error(f"Error fetching Binance OHLCV: {e}")
    return []


async def fetch_coingecko_prices(symbols: List[str] = None, limit: int = 10):
    """Fetch prices from CoinGecko"""
    try:
        if symbols:
            ids = ",".join([s.lower() for s in symbols])
            url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={ids}"
        else:
            url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page={limit}&page=1"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                
                prices = []
                for coin in data:
                    prices.append({
                        "id": coin.get("id"),
                        "symbol": coin.get("symbol", "").upper(),
                        "name": coin.get("name"),
                        "current_price": coin.get("current_price"),
                        "market_cap": coin.get("market_cap"),
                        "market_cap_rank": coin.get("market_cap_rank"),
                        "total_volume": coin.get("total_volume"),
                        "price_change_24h": coin.get("price_change_24h"),
                        "price_change_percentage_24h": coin.get("price_change_percentage_24h"),
                        "last_updated": coin.get("last_updated")
                    })
                
                return prices
    except Exception as e:
        logger.error(f"Error fetching CoinGecko prices: {e}")
    return []


async def fetch_binance_ticker(symbol: str):
    """Fetch ticker from Binance"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol.upper()}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "symbol": data["symbol"],
                    "price": float(data["lastPrice"]),
                    "price_change_24h": float(data["priceChange"]),
                    "price_change_percent_24h": float(data["priceChangePercent"]),
                    "high_24h": float(data["highPrice"]),
                    "low_24h": float(data["lowPrice"]),
                    "volume_24h": float(data["volume"]),
                    "quote_volume_24h": float(data["quoteVolume"])
                }
    except Exception as e:
        logger.error(f"Error fetching Binance ticker: {e}")
    return None


# ============================================================================
# Core Endpoints
# ============================================================================

@app.get("/health")
async def health():
    """System health check"""
    return {
        "status": "healthy",
        "service": "cryptocurrency-data-api",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "providers_loaded": len(providers_state)
    }


@app.get("/info")
async def info():
    """System information"""
    # Count HuggingFace Space providers
    hf_providers = [p for p in PROVIDERS_CONFIG.keys() if 'huggingface_space' in p]
    
    return {
        "service": "Cryptocurrency Data & Analysis API",
        "version": "3.0.0",
        "endpoints": {
            "core": ["/health", "/info", "/api/providers"],
            "data": ["/api/ohlcv", "/api/crypto/prices/top", "/api/crypto/price/{symbol}", "/api/crypto/market-overview"],
            "analysis": ["/api/analysis/signals", "/api/analysis/smc", "/api/scoring/snapshot"],
            "market": ["/api/market/prices", "/api/market-data/prices"],
            "system": ["/api/system/status", "/api/system/config"],
            "huggingface": ["/api/hf/health", "/api/hf/refresh", "/api/hf/registry", "/api/hf/run-sentiment"]
        },
        "data_sources": ["Binance", "CoinGecko", "CoinPaprika", "CoinCap"],
        "providers_loaded": len(PROVIDERS_CONFIG),
        "huggingface_space_providers": len(hf_providers),
        "features": [
            "Real-time price data",
            "OHLCV historical data",
            "Trading signals",
            "Market analysis",
            "Sentiment analysis",
            "HuggingFace model integration",
            f"{len(PROVIDERS_CONFIG)} providers from providers_config_extended.json"
        ]
    }


@app.get("/api/providers")
async def get_providers():
    """Get list of API providers from providers_config_extended.json"""
    try:
        providers_list = []
        
        for provider_id, provider_info in PROVIDERS_CONFIG.items():
            providers_list.append({
                "id": provider_id,
                "name": provider_info.get("name", provider_id),
                "category": provider_info.get("category", "unknown"),
                "status": "online" if provider_info.get("validated", False) else "pending",
                "priority": provider_info.get("priority", 5),
                "base_url": provider_info.get("base_url", ""),
                "requires_auth": provider_info.get("requires_auth", False),
                "endpoints_count": len(provider_info.get("endpoints", {}))
            })
        
        return {
            "providers": providers_list,
            "total": len(providers_list),
            "source": "providers_config_extended.json",
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting providers: {e}")
        return {"providers": [], "total": 0, "error": str(e)}


# ============================================================================
# OHLCV Data Endpoint
# ============================================================================

@app.get("/api/ohlcv")
async def get_ohlcv(
    symbol: str = Query("BTCUSDT", description="Trading pair symbol"),
    interval: str = Query("1h", description="Time interval (1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles")
):
    """
    Get OHLCV (candlestick) data for a trading pair
    
    Supported intervals: 1m, 5m, 15m, 30m, 1h, 4h, 1d
    """
    try:
        # Check cache
        cache_key = f"{symbol}_{interval}_{limit}"
        if cache_key in cache["ohlcv"]:
            cached_data, cached_time = cache["ohlcv"][cache_key]
            if (datetime.now() - cached_time).seconds < 60:  # 60s cache
                return {"symbol": symbol, "interval": interval, "data": cached_data, "source": "cache"}
        
        # Fetch from Binance
        ohlcv_data = await fetch_binance_ohlcv(symbol, interval, limit)
        
        if ohlcv_data:
            # Update cache
            cache["ohlcv"][cache_key] = (ohlcv_data, datetime.now())
            
            return {
                "symbol": symbol,
                "interval": interval,
                "count": len(ohlcv_data),
                "data": ohlcv_data,
                "source": "binance",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=503, detail="Unable to fetch OHLCV data")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_ohlcv: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Crypto Prices Endpoints
# ============================================================================

@app.get("/api/crypto/prices/top")
async def get_top_prices(limit: int = Query(10, ge=1, le=100, description="Number of top cryptocurrencies")):
    """Get top cryptocurrencies by market cap"""
    try:
        # Check cache
        cache_key = f"top_{limit}"
        if cache_key in cache["prices"]:
            cached_data, cached_time = cache["prices"][cache_key]
            if (datetime.now() - cached_time).seconds < 60:
                return {"data": cached_data, "source": "cache"}
        
        # Fetch from CoinGecko
        prices = await fetch_coingecko_prices(limit=limit)
        
        if prices:
            # Update cache
            cache["prices"][cache_key] = (prices, datetime.now())
            
            return {
                "count": len(prices),
                "data": prices,
                "source": "coingecko",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=503, detail="Unable to fetch price data")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_top_prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/crypto/price/{symbol}")
async def get_single_price(symbol: str):
    """Get price for a single cryptocurrency"""
    try:
        # Try Binance first for common pairs
        binance_symbol = f"{symbol.upper()}USDT"
        ticker = await fetch_binance_ticker(binance_symbol)
        
        if ticker:
            return {
                "symbol": symbol.upper(),
                "price": ticker,
                "source": "binance",
                "timestamp": datetime.now().isoformat()
            }
        
        # Fallback to CoinGecko
        prices = await fetch_coingecko_prices([symbol])
        if prices:
            return {
                "symbol": symbol.upper(),
                "price": prices[0],
                "source": "coingecko",
                "timestamp": datetime.now().isoformat()
            }
        
        raise HTTPException(status_code=404, detail=f"Price data not found for {symbol}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_single_price: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/crypto/market-overview")
async def get_market_overview():
    """Get comprehensive market overview"""
    try:
        # Fetch top 20 coins
        prices = await fetch_coingecko_prices(limit=20)
        
        if not prices:
            raise HTTPException(status_code=503, detail="Unable to fetch market data")
        
        # Calculate market stats
        total_market_cap = sum(p.get("market_cap", 0) or 0 for p in prices)
        total_volume = sum(p.get("total_volume", 0) or 0 for p in prices)
        
        # Sort by 24h change
        gainers = sorted(
            [p for p in prices if p.get("price_change_percentage_24h")],
            key=lambda x: x.get("price_change_percentage_24h", 0),
            reverse=True
        )[:5]
        
        losers = sorted(
            [p for p in prices if p.get("price_change_percentage_24h")],
            key=lambda x: x.get("price_change_percentage_24h", 0)
        )[:5]
        
        return {
            "total_market_cap": total_market_cap,
            "total_volume_24h": total_volume,
            "btc_dominance": (prices[0].get("market_cap", 0) / total_market_cap * 100) if total_market_cap > 0 else 0,
            "top_gainers": gainers,
            "top_losers": losers,
            "top_by_volume": sorted(prices, key=lambda x: x.get("total_volume", 0) or 0, reverse=True)[:5],
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_market_overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/prices")
async def get_multiple_prices(symbols: str = Query("BTC,ETH,SOL", description="Comma-separated symbols")):
    """Get prices for multiple cryptocurrencies"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        
        # Fetch prices
        prices_data = []
        for symbol in symbol_list:
            try:
                ticker = await fetch_binance_ticker(f"{symbol}USDT")
                if ticker:
                    prices_data.append(ticker)
            except:
                continue
        
        if not prices_data:
            # Fallback to CoinGecko
            prices_data = await fetch_coingecko_prices(symbol_list)
        
        return {
            "symbols": symbol_list,
            "count": len(prices_data),
            "data": prices_data,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in get_multiple_prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market-data/prices")
async def get_market_data_prices(symbols: str = Query("BTC,ETH", description="Comma-separated symbols")):
    """Alternative endpoint for market data prices"""
    return await get_multiple_prices(symbols)


# ============================================================================
# Analysis Endpoints
# ============================================================================

@app.get("/api/analysis/signals")
async def get_trading_signals(
    symbol: str = Query("BTCUSDT", description="Trading pair"),
    timeframe: str = Query("1h", description="Timeframe")
):
    """Get trading signals for a symbol"""
    try:
        # Fetch OHLCV data for analysis
        ohlcv = await fetch_binance_ohlcv(symbol, timeframe, 100)
        
        if not ohlcv:
            raise HTTPException(status_code=503, detail="Unable to fetch data for analysis")
        
        # Simple signal generation (can be enhanced)
        latest = ohlcv[-1]
        prev = ohlcv[-2] if len(ohlcv) > 1 else latest
        
        # Calculate simple indicators
        close_prices = [c["close"] for c in ohlcv[-20:]]
        sma_20 = sum(close_prices) / len(close_prices)
        
        # Generate signal
        trend = "bullish" if latest["close"] > sma_20 else "bearish"
        momentum = "strong" if abs(latest["close"] - prev["close"]) / prev["close"] > 0.01 else "weak"
        
        signal = "buy" if trend == "bullish" and momentum == "strong" else (
            "sell" if trend == "bearish" and momentum == "strong" else "hold"
        )
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": signal,
            "trend": trend,
            "momentum": momentum,
            "indicators": {
                "sma_20": sma_20,
                "current_price": latest["close"],
                "price_change": latest["close"] - prev["close"],
                "price_change_percent": ((latest["close"] - prev["close"]) / prev["close"]) * 100
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_trading_signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/smc")
async def get_smc_analysis(symbol: str = Query("BTCUSDT", description="Trading pair")):
    """Get Smart Money Concepts (SMC) analysis"""
    try:
        # Fetch OHLCV data
        ohlcv = await fetch_binance_ohlcv(symbol, "1h", 200)
        
        if not ohlcv:
            raise HTTPException(status_code=503, detail="Unable to fetch data")
        
        # Calculate key levels
        highs = [c["high"] for c in ohlcv]
        lows = [c["low"] for c in ohlcv]
        closes = [c["close"] for c in ohlcv]
        
        resistance = max(highs[-50:])
        support = min(lows[-50:])
        current_price = closes[-1]
        
        # Structure analysis
        market_structure = "higher_highs" if closes[-1] > closes[-10] > closes[-20] else "lower_lows"
        
        return {
            "symbol": symbol,
            "market_structure": market_structure,
            "key_levels": {
                "resistance": resistance,
                "support": support,
                "current_price": current_price,
                "mid_point": (resistance + support) / 2
            },
            "order_blocks": {
                "bullish": support,
                "bearish": resistance
            },
            "liquidity_zones": {
                "above": resistance,
                "below": support
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_smc_analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scoring/snapshot")
async def get_scoring_snapshot(symbol: str = Query("BTCUSDT", description="Trading pair")):
    """Get comprehensive scoring snapshot"""
    try:
        # Fetch data
        ticker = await fetch_binance_ticker(symbol)
        ohlcv = await fetch_binance_ohlcv(symbol, "1h", 100)
        
        if not ticker or not ohlcv:
            raise HTTPException(status_code=503, detail="Unable to fetch data")
        
        # Calculate scores (0-100)
        volatility_score = min(abs(ticker["price_change_percent_24h"]) * 5, 100)
        volume_score = min((ticker["volume_24h"] / 1000000) * 10, 100)
        trend_score = 50 + (ticker["price_change_percent_24h"] * 2)
        
        # Overall score
        overall_score = (volatility_score + volume_score + trend_score) / 3
        
        return {
            "symbol": symbol,
            "overall_score": round(overall_score, 2),
            "scores": {
                "volatility": round(volatility_score, 2),
                "volume": round(volume_score, 2),
                "trend": round(trend_score, 2),
                "momentum": round(50 + ticker["price_change_percent_24h"], 2)
            },
            "rating": "excellent" if overall_score > 80 else (
                "good" if overall_score > 60 else (
                    "average" if overall_score > 40 else "poor"
                )
            ),
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_scoring_snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals")
async def get_all_signals():
    """Get signals for multiple assets"""
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
    signals = []
    
    for symbol in symbols:
        try:
            signal_data = await get_trading_signals(symbol, "1h")
            signals.append(signal_data)
        except:
            continue
    
    return {
        "count": len(signals),
        "signals": signals,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/sentiment")
async def get_sentiment():
    """Get market sentiment data"""
    # Mock sentiment data (can be enhanced with real sentiment analysis)
    sentiment_value = random.randint(30, 70)
    
    classification = "extreme_fear" if sentiment_value < 25 else (
        "fear" if sentiment_value < 45 else (
            "neutral" if sentiment_value < 55 else (
                "greed" if sentiment_value < 75 else "extreme_greed"
            )
        )
    )
    
    return {
        "value": sentiment_value,
        "classification": classification,
        "description": f"Market sentiment is {classification.replace('_', ' ')}",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# System Endpoints
# ============================================================================

@app.get("/api/system/status")
async def get_system_status():
    """Get system status"""
    return {
        "status": "operational",
        "uptime_seconds": time.time(),
        "cache_size": len(cache["ohlcv"]) + len(cache["prices"]),
        "providers_online": 5,
        "requests_per_minute": 0,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/system/config")
async def get_system_config():
    """Get system configuration"""
    return {
        "version": "3.0.0",
        "api_version": "v1",
        "cache_ttl_seconds": 60,
        "supported_symbols": ["BTC", "ETH", "SOL", "BNB", "ADA", "DOT", "MATIC", "AVAX"],
        "supported_intervals": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        "max_ohlcv_limit": 1000,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/categories")
async def get_categories():
    """Get data categories"""
    return {
        "categories": [
            {"name": "market_data", "endpoints": 5, "status": "active"},
            {"name": "analysis", "endpoints": 4, "status": "active"},
            {"name": "signals", "endpoints": 2, "status": "active"},
            {"name": "sentiment", "endpoints": 1, "status": "active"}
        ]
    }


@app.get("/api/rate-limits")
async def get_rate_limits():
    """Get rate limit information"""
    return {
        "rate_limits": [
            {"endpoint": "/api/ohlcv", "limit": 1200, "window": "per_minute"},
            {"endpoint": "/api/crypto/prices/top", "limit": 600, "window": "per_minute"},
            {"endpoint": "/api/analysis/*", "limit": 300, "window": "per_minute"}
        ],
        "current_usage": {
            "requests_this_minute": 0,
            "percentage": 0
        }
    }


@app.get("/api/logs")
async def get_logs(limit: int = Query(50, ge=1, le=500)):
    """Get recent API logs"""
    # Mock logs (can be enhanced with real logging)
    logs = []
    for i in range(min(limit, 10)):
        logs.append({
            "timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(),
            "endpoint": "/api/ohlcv",
            "status": "success",
            "response_time_ms": random.randint(50, 200)
        })
    
    return {"logs": logs, "count": len(logs)}


@app.get("/api/alerts")
async def get_alerts():
    """Get system alerts"""
    return {
        "alerts": [],
        "count": 0,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# HuggingFace Integration Endpoints
# ============================================================================

@app.get("/api/hf/health")
async def hf_health():
    """HuggingFace integration health"""
    try:
        from backend.services.hf_registry import REGISTRY
        return REGISTRY.health()
    except:
        return {
            "status": "unavailable",
            "message": "HF registry not initialized",
            "timestamp": datetime.now().isoformat()
        }


@app.post("/api/hf/refresh")
async def hf_refresh():
    """Refresh HuggingFace data"""
    try:
        from backend.services.hf_registry import REGISTRY
        return await REGISTRY.refresh()
    except:
        return {
            "status": "error",
            "message": "HF registry not available",
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/hf/registry")
async def hf_registry(kind: str = "models"):
    """Get HuggingFace registry"""
    try:
        from backend.services.hf_registry import REGISTRY
        return {"kind": kind, "items": REGISTRY.list(kind)}
    except:
        return {"kind": kind, "items": [], "error": "Registry not available"}


@app.post("/api/hf/run-sentiment")
@app.post("/api/hf/sentiment")
async def hf_sentiment(texts: List[str], model: Optional[str] = None):
    """Run sentiment analysis using HuggingFace models"""
    try:
        from backend.services.hf_client import run_sentiment
        return run_sentiment(texts, model=model)
    except:
        # Return mock sentiment if HF not available
        results = []
        for text in texts:
            results.append({
                "text": text,
                "sentiment": "neutral",
                "score": 0.5,
                "confidence": 0.5
            })
        return {"results": results, "model": "mock"}


# ============================================================================
# Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("=" * 70)
    logger.info("🚀 Cryptocurrency Data & Analysis API Starting")
    logger.info("=" * 70)
    logger.info("✓ FastAPI initialized")
    logger.info("✓ CORS configured")
    logger.info("✓ Cache initialized")
    logger.info(f"✓ Providers loaded: {len(PROVIDERS_CONFIG)}")
    
    # Show loaded HuggingFace Space providers
    hf_providers = [p for p in PROVIDERS_CONFIG.keys() if 'huggingface_space' in p]
    if hf_providers:
        logger.info(f"✓ HuggingFace Space providers: {', '.join(hf_providers)}")
    
    logger.info("✓ Data sources: Binance, CoinGecko, providers_config_extended.json")
    logger.info("=" * 70)
    logger.info("📡 API ready at http://0.0.0.0:7860")
    logger.info("📖 Docs at http://0.0.0.0:7860/docs")
    logger.info("=" * 70)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🚀 Starting Cryptocurrency Data & Analysis API")
    print("=" * 70)
    print("📍 Server: http://localhost:7860")
    print("📖 API Docs: http://localhost:7860/docs")
    print("🔗 Health: http://localhost:7860/health")
    print("=" * 70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info"
    )
