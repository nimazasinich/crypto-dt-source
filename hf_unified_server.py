"""Unified HuggingFace Space API Server leveraging shared collectors and AI helpers."""

import asyncio
import time
from datetime import datetime, timedelta
from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Any, Dict, List, Optional, Union
import logging
import random
import json
from pathlib import Path

from ai_models import (
    analyze_chart_points,
    analyze_crypto_sentiment,
    analyze_market_text,
    get_model_info,
    initialize_models,
    registry_status,
)
from collectors.aggregator import (
    CollectorError,
    MarketDataCollector,
    NewsCollector,
    ProviderStatusCollector,
)
from config import COIN_SYMBOL_MAPPING, get_settings

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

# Runtime state
START_TIME = time.time()
cache = {"ohlcv": {}, "prices": {}, "market_data": {}, "providers": [], "last_update": None}
settings = get_settings()
market_collector = MarketDataCollector()
news_collector = NewsCollector()
provider_collector = ProviderStatusCollector()

# Load providers config
WORKSPACE_ROOT = Path(__file__).parent
PROVIDERS_CONFIG_PATH = settings.providers_config_path

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

# Mount static files (CSS, JS)
try:
    static_path = WORKSPACE_ROOT / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
        logger.info(f"✅ Static files mounted from {static_path}")
    else:
        logger.warning(f"⚠️ Static directory not found: {static_path}")
except Exception as e:
    logger.error(f"❌ Error mounting static files: {e}")

# ============================================================================
# Helper utilities & Data Fetching Functions
# ============================================================================

def _normalize_asset_symbol(symbol: str) -> str:
    symbol = (symbol or "").upper()
    suffixes = ("USDT", "USD", "BTC", "ETH", "BNB")
    for suffix in suffixes:
        if symbol.endswith(suffix) and len(symbol) > len(suffix):
            return symbol[: -len(suffix)]
    return symbol


def _format_price_record(record: Dict[str, Any]) -> Dict[str, Any]:
    price = record.get("price") or record.get("current_price")
    change_pct = record.get("change_24h") or record.get("price_change_percentage_24h")
    change_abs = None
    if price is not None and change_pct is not None:
        try:
            change_abs = float(price) * float(change_pct) / 100.0
        except (TypeError, ValueError):
            change_abs = None

    return {
        "id": record.get("id") or record.get("symbol", "").lower(),
        "symbol": record.get("symbol", "").upper(),
        "name": record.get("name"),
        "current_price": price,
        "market_cap": record.get("market_cap"),
        "market_cap_rank": record.get("rank"),
        "total_volume": record.get("volume_24h") or record.get("total_volume"),
        "price_change_24h": change_abs,
        "price_change_percentage_24h": change_pct,
        "high_24h": record.get("high_24h"),
        "low_24h": record.get("low_24h"),
        "last_updated": record.get("last_updated"),
    }


async def fetch_binance_ohlcv(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 100):
    """Fetch OHLCV data from Binance via the shared collector."""

    try:
        candles = await market_collector.get_ohlcv(symbol, interval, limit)
        return [
            {
                **candle,
                "timestamp": int(datetime.fromisoformat(candle["timestamp"]).timestamp() * 1000),
                "datetime": candle["timestamp"],
            }
            for candle in candles
        ]
    except CollectorError as exc:
        logger.error("Error fetching OHLCV: %s", exc)
        return []


async def fetch_coingecko_prices(symbols: Optional[List[str]] = None, limit: int = 10):
    """Fetch price snapshots using the shared market collector."""

    try:
        if symbols:
            tasks = [market_collector.get_coin_details(_normalize_asset_symbol(sym)) for sym in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            coins: List[Dict[str, Any]] = []
            for result in results:
                if isinstance(result, Exception):
                    continue
                coins.append(_format_price_record(result))
            return coins

        top = await market_collector.get_top_coins(limit=limit)
        return [_format_price_record(entry) for entry in top]
    except CollectorError as exc:
        logger.error("Error fetching aggregated prices: %s", exc)
        return []


async def fetch_binance_ticker(symbol: str):
    """Provide ticker-like information sourced from CoinGecko market data."""

    try:
        coin = await market_collector.get_coin_details(_normalize_asset_symbol(symbol))
    except CollectorError as exc:
        logger.error("Unable to load ticker for %s: %s", symbol, exc)
        return None

    price = coin.get("price")
    change_pct = coin.get("change_24h") or 0.0
    change_abs = price * change_pct / 100 if price is not None and change_pct is not None else None

    return {
        "symbol": symbol.upper(),
        "price": price,
        "price_change_24h": change_abs,
        "price_change_percent_24h": change_pct,
        "high_24h": coin.get("high_24h"),
        "low_24h": coin.get("low_24h"),
        "volume_24h": coin.get("volume_24h"),
        "quote_volume_24h": coin.get("volume_24h"),
    }


# ============================================================================
# Core Endpoints
# ============================================================================

@app.get("/health")
async def health():
    """System health check using shared collectors."""

    async def _safe_call(coro):
        try:
            data = await coro
            return {"status": "ok", "count": len(data) if hasattr(data, "__len__") else 1}
        except Exception as exc:  # pragma: no cover - network heavy
            return {"status": "error", "detail": str(exc)}

    market_task = asyncio.create_task(_safe_call(market_collector.get_top_coins(limit=3)))
    news_task = asyncio.create_task(_safe_call(news_collector.get_latest_news(limit=3)))
    providers_task = asyncio.create_task(_safe_call(provider_collector.get_providers_status()))

    market_status, news_status, providers_status = await asyncio.gather(
        market_task, news_task, providers_task
    )

    ai_status = registry_status()
    service_states = {
        "market_data": market_status,
        "news": news_status,
        "providers": providers_status,
        "ai_models": ai_status,
    }

    degraded = any(state.get("status") != "ok" for state in (market_status, news_status, providers_status))
    overall = "healthy" if not degraded else "degraded"

    return {
        "status": overall,
        "service": "cryptocurrency-data-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": app.version,
        "providers_loaded": market_status.get("count", 0),
        "services": service_states,
    }


@app.get("/info")
async def info():
    """System information"""
    hf_providers = [p for p in PROVIDERS_CONFIG.keys() if "huggingface_space" in p]

    return {
        "service": "Cryptocurrency Data & Analysis API",
        "version": app.version,
        "endpoints": {
            "core": ["/health", "/info", "/api/providers"],
            "data": ["/api/ohlcv", "/api/crypto/prices/top", "/api/crypto/price/{symbol}", "/api/crypto/market-overview"],
            "analysis": ["/api/analysis/signals", "/api/analysis/smc", "/api/scoring/snapshot"],
            "market": ["/api/market/prices", "/api/market-data/prices"],
            "system": ["/api/system/status", "/api/system/config"],
            "huggingface": ["/api/hf/health", "/api/hf/refresh", "/api/hf/registry", "/api/hf/run-sentiment"],
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
            f"{len(PROVIDERS_CONFIG)} providers from providers_config_extended.json",
        ],
        "ai_registry": registry_status(),
    }


@app.get("/api/providers")
async def get_providers():
    """Get list of API providers and their health."""

    try:
        statuses = await provider_collector.get_providers_status()
    except Exception as exc:  # pragma: no cover - network heavy
        logger.error("Error getting providers: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))

    providers_list = []
    for status in statuses:
        meta = PROVIDERS_CONFIG.get(status["provider_id"], {})
        providers_list.append(
            {
                **status,
                "base_url": meta.get("base_url"),
                "requires_auth": meta.get("requires_auth"),
                "priority": meta.get("priority"),
            }
        )

    return {
        "providers": providers_list,
        "total": len(providers_list),
        "source": str(PROVIDERS_CONFIG_PATH),
        "last_updated": datetime.utcnow().isoformat(),
    }


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

        ai_summary = analyze_chart_points(symbol, timeframe, ohlcv)

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
            "analysis": ai_summary,
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
    try:
        news = await news_collector.get_latest_news(limit=5)
    except CollectorError as exc:
        logger.warning("Sentiment fallback due to news error: %s", exc)
        news = []

    text = " ".join(item.get("title", "") for item in news).strip() or "Crypto market update"
    analysis = analyze_market_text(text)
    score = analysis.get("signals", {}).get("crypto", {}).get("score", 0.0)
    normalized_value = int((score + 1) * 50)

    if normalized_value < 20:
        classification = "extreme_fear"
    elif normalized_value < 40:
        classification = "fear"
    elif normalized_value < 60:
        classification = "neutral"
    elif normalized_value < 80:
        classification = "greed"
    else:
        classification = "extreme_greed"

    return {
        "value": normalized_value,
        "classification": classification,
        "description": f"Market sentiment is {classification.replace('_', ' ')}",
        "analysis": analysis,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================================
# System Endpoints
# ============================================================================

@app.get("/api/system/status")
async def get_system_status():
    """Get system status"""
    providers = await provider_collector.get_providers_status()
    online = sum(1 for provider in providers if provider.get("status") == "online")

    cache_items = (
        len(getattr(market_collector.cache, "_store", {}))
        + len(getattr(news_collector.cache, "_store", {}))
        + len(getattr(provider_collector.cache, "_store", {}))
    )

    return {
        "status": "operational" if online else "maintenance",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "cache_size": cache_items,
        "providers_online": online,
        "requests_per_minute": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/system/config")
async def get_system_config():
    """Get system configuration"""
    return {
        "version": app.version,
        "api_version": "v1",
        "cache_ttl_seconds": settings.cache_ttl,
        "supported_symbols": sorted(set(COIN_SYMBOL_MAPPING.values())),
        "supported_intervals": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        "max_ohlcv_limit": 1000,
        "timestamp": datetime.utcnow().isoformat(),
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
    status = registry_status()
    status["timestamp"] = datetime.utcnow().isoformat()
    return status


@app.post("/api/hf/refresh")
async def hf_refresh():
    """Refresh HuggingFace data"""
    result = initialize_models()
    return {"status": "ok" if result.get("success") else "degraded", **result, "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/hf/registry")
async def hf_registry(kind: str = "models"):
    """Get HuggingFace registry"""
    info = get_model_info()
    return {"kind": kind, "items": info.get("model_names", info)}


def _resolve_sentiment_payload(payload: Union[List[str], Dict[str, Any]]) -> Dict[str, Any]:
    if isinstance(payload, list):
        return {"texts": payload, "mode": "auto"}
    if isinstance(payload, dict):
        texts = payload.get("texts") or payload.get("text")
        if isinstance(texts, str):
            texts = [texts]
        if not isinstance(texts, list):
            raise ValueError("texts must be provided")
        mode = payload.get("mode") or payload.get("model") or "auto"
        return {"texts": texts, "mode": mode}
    raise ValueError("Invalid payload")


@app.post("/api/hf/run-sentiment")
@app.post("/api/hf/sentiment")
async def hf_sentiment(payload: Union[List[str], Dict[str, Any]] = Body(...)):
    """Run sentiment analysis using shared AI helpers."""

    try:
        resolved = _resolve_sentiment_payload(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    mode = (resolved.get("mode") or "auto").lower()
    texts = resolved["texts"]
    results: List[Dict[str, Any]] = []
    for text in texts:
        if mode == "crypto":
            analysis = analyze_crypto_sentiment(text)
        elif mode == "financial":
            analysis = analyze_market_text(text).get("signals", {}).get("financial", {})
        elif mode == "social":
            analysis = analyze_market_text(text).get("signals", {}).get("social", {})
        else:
            analysis = analyze_market_text(text)
        results.append({"text": text, "result": analysis})

    return {"mode": mode, "results": results, "timestamp": datetime.utcnow().isoformat()}


# ============================================================================
# HTML Routes - Serve UI files
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main admin dashboard (admin.html)"""
    admin_path = WORKSPACE_ROOT / "admin.html"
    if admin_path.exists():
        return FileResponse(admin_path)
    return HTMLResponse("<h1>Cryptocurrency Data & Analysis API</h1><p>See <a href='/docs'>/docs</a> for API documentation</p>")

@app.get("/index.html", response_class=HTMLResponse)
async def index():
    """Serve index.html"""
    return FileResponse(WORKSPACE_ROOT / "index.html")

@app.get("/dashboard.html", response_class=HTMLResponse)
async def dashboard():
    """Serve dashboard.html"""
    return FileResponse(WORKSPACE_ROOT / "dashboard.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_alt():
    """Alternative route for dashboard"""
    return FileResponse(WORKSPACE_ROOT / "dashboard.html")

@app.get("/admin.html", response_class=HTMLResponse)
async def admin():
    """Serve admin panel"""
    return FileResponse(WORKSPACE_ROOT / "admin.html")

@app.get("/admin", response_class=HTMLResponse)
async def admin_alt():
    """Alternative route for admin"""
    return FileResponse(WORKSPACE_ROOT / "admin.html")

@app.get("/hf_console.html", response_class=HTMLResponse)
async def hf_console():
    """Serve HuggingFace console"""
    return FileResponse(WORKSPACE_ROOT / "hf_console.html")

@app.get("/console", response_class=HTMLResponse)
async def console_alt():
    """Alternative route for HF console"""
    return FileResponse(WORKSPACE_ROOT / "hf_console.html")

@app.get("/pool_management.html", response_class=HTMLResponse)
async def pool_management():
    """Serve pool management UI"""
    return FileResponse(WORKSPACE_ROOT / "pool_management.html")

@app.get("/unified_dashboard.html", response_class=HTMLResponse)
async def unified_dashboard():
    """Serve unified dashboard"""
    return FileResponse(WORKSPACE_ROOT / "unified_dashboard.html")

@app.get("/simple_overview.html", response_class=HTMLResponse)
async def simple_overview():
    """Serve simple overview"""
    return FileResponse(WORKSPACE_ROOT / "simple_overview.html")

# Generic HTML file handler
@app.get("/{filename}.html", response_class=HTMLResponse)
async def serve_html(filename: str):
    """Serve any HTML file from workspace root"""
    file_path = WORKSPACE_ROOT / f"{filename}.html"
    if file_path.exists():
        return FileResponse(file_path)
    return HTMLResponse(f"<h1>File {filename}.html not found</h1>", status_code=404)


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
    
    # Check HTML files
    html_files = ["index.html", "dashboard.html", "admin.html", "hf_console.html"]
    available_html = [f for f in html_files if (WORKSPACE_ROOT / f).exists()]
    logger.info(f"✓ UI files: {len(available_html)}/{len(html_files)} available")
    
    logger.info("=" * 70)
    logger.info("📡 API ready at http://0.0.0.0:7860")
    logger.info("📖 Docs at http://0.0.0.0:7860/docs")
    logger.info("🎨 UI at http://0.0.0.0:7860/ (admin.html)")
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
