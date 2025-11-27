#!/usr/bin/env python3
"""
Real Data API Router - UNIFIED HUGGINGFACE ONLY
=================================================
✅ تمام داده‌ها از HuggingFace Space
✅ بدون WebSocket (فقط HTTP REST API)
✅ بدون استفاده مستقیم از CoinMarketCap, NewsAPI, etc.
✅ تمام درخواست‌ها از طریق HuggingFaceUnifiedClient

Reference: crypto_resources_unified_2025-11-11.json
"""

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import logging

# Import ONLY HuggingFace Unified Client
from backend.services.hf_unified_client import get_hf_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Unified HuggingFace API"])

# Get singleton HF client
hf_client = get_hf_client()


# ============================================================================
# Pydantic Models
# ============================================================================


class PredictRequest(BaseModel):
    """Model prediction request"""

    symbol: str
    context: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


class SentimentRequest(BaseModel):
    """Sentiment analysis request"""

    text: str
    mode: Optional[str] = "crypto"


# ============================================================================
# Market Data Endpoints - از HuggingFace فقط
# ============================================================================


@router.get("/api/market")
async def get_market_snapshot(
    limit: int = Query(100, description="Number of symbols"),
    symbols: Optional[str] = Query(None, description="Comma-separated symbols (e.g., BTC,ETH)"),
):
    """
    دریافت داده‌های بازار از HuggingFace Space

    ✅ فقط از HuggingFace
    ❌ بدون CoinMarketCap
    ❌ بدون API های دیگر
    """
    try:
        symbol_list = None
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(",")]

        result = await hf_client.get_market_prices(symbols=symbol_list, limit=limit)

        if not result.get("success"):
            raise HTTPException(
                status_code=503, detail=result.get("error", "HuggingFace Space returned error")
            )

        logger.info(f"✅ Market data from HF: {len(result.get('data', []))} symbols")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Market data failed: {e}")
        raise HTTPException(
            status_code=503, detail=f"Failed to fetch market data from HuggingFace: {str(e)}"
        )


@router.get("/api/market/history")
async def get_market_history(
    symbol: str = Query(..., description="Symbol (e.g., BTCUSDT)"),
    timeframe: str = Query("1h", description="Timeframe (1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(1000, description="Number of candles"),
):
    """
    دریافت داده‌های OHLCV از HuggingFace Space

    ✅ فقط از HuggingFace
    ❌ بدون CoinMarketCap یا Binance
    """
    try:
        result = await hf_client.get_market_history(symbol=symbol, timeframe=timeframe, limit=limit)

        if not result.get("success"):
            raise HTTPException(
                status_code=404, detail=result.get("error", "OHLCV data not available")
            )

        logger.info(
            f"✅ OHLCV from HF: {symbol} {timeframe} ({len(result.get('data', []))} candles)"
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ OHLCV data failed: {e}")
        raise HTTPException(
            status_code=503, detail=f"Failed to fetch OHLCV data from HuggingFace: {str(e)}"
        )


@router.get("/api/market/pairs")
async def get_trading_pairs():
    """
    دریافت لیست جفت‌های معاملاتی

    در صورت عدم وجود endpoint در HuggingFace، از اطلاعات market data استفاده می‌شود
    """
    try:
        # Try to get pairs from HF
        # If not available, derive from market data
        market_data = await hf_client.get_market_prices(limit=50)

        if not market_data.get("success"):
            raise HTTPException(status_code=503, detail="Failed to fetch market data")

        pairs = []
        for item in market_data.get("data", []):
            symbol = item.get("symbol", "")
            if symbol:
                pairs.append(
                    {
                        "pair": f"{symbol}/USDT",
                        "base": symbol,
                        "quote": "USDT",
                        "tick_size": 0.01,
                        "min_qty": 0.001,
                    }
                )

        return {
            "success": True,
            "pairs": pairs,
            "meta": {
                "cache_ttl_seconds": 300,
                "generated_at": datetime.utcnow().isoformat(),
                "source": "hf_engine",
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Trading pairs failed: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch trading pairs: {str(e)}")


@router.get("/api/market/tickers")
async def get_tickers(
    limit: int = Query(100, description="Number of tickers"),
    sort: str = Query("market_cap", description="Sort by: market_cap, volume, change"),
):
    """
    دریافت tickers مرتب‌شده از HuggingFace
    """
    try:
        market_data = await hf_client.get_market_prices(limit=limit)

        if not market_data.get("success"):
            raise HTTPException(status_code=503, detail="Failed to fetch market data")

        tickers = []
        for item in market_data.get("data", []):
            tickers.append(
                {
                    "symbol": item.get("symbol", ""),
                    "price": item.get("price", 0),
                    "change_24h": item.get("change_24h", 0),
                    "volume_24h": item.get("volume_24h", 0),
                    "market_cap": item.get("market_cap", 0),
                }
            )

        # Sort tickers
        if sort == "volume":
            tickers.sort(key=lambda x: x.get("volume_24h", 0), reverse=True)
        elif sort == "change":
            tickers.sort(key=lambda x: x.get("change_24h", 0), reverse=True)
        elif sort == "market_cap":
            tickers.sort(key=lambda x: x.get("market_cap", 0), reverse=True)

        return {
            "success": True,
            "tickers": tickers,
            "meta": {
                "cache_ttl_seconds": 60,
                "generated_at": datetime.utcnow().isoformat(),
                "source": "hf_engine",
                "sort": sort,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Tickers failed: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch tickers: {str(e)}")


# ============================================================================
# Sentiment Analysis - از HuggingFace فقط
# ============================================================================


@router.post("/api/sentiment/analyze")
async def analyze_sentiment(request: SentimentRequest):
    """
    تحلیل احساسات با مدل‌های AI در HuggingFace

    ✅ فقط از HuggingFace AI Models
    ❌ بدون مدل‌های محلی
    """
    try:
        result = await hf_client.analyze_sentiment(text=request.text)

        if not result.get("success"):
            raise HTTPException(
                status_code=500, detail=result.get("error", "Sentiment analysis failed")
            )

        logger.info(f"✅ Sentiment from HF: {result.get('data', {}).get('sentiment')}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze sentiment: {str(e)}")


# ============================================================================
# News - از HuggingFace فقط
# ============================================================================


@router.get("/api/news")
async def get_news(
    limit: int = Query(20, description="Number of articles"),
    source: Optional[str] = Query(None, description="Filter by source"),
):
    """
    دریافت اخبار از HuggingFace Space

    ✅ فقط از HuggingFace
    ❌ بدون NewsAPI مستقیم
    """
    try:
        result = await hf_client.get_news(limit=limit, source=source)

        logger.info(f"✅ News from HF: {len(result.get('articles', []))} articles")
        return result

    except Exception as e:
        logger.error(f"❌ News failed: {e}")
        raise HTTPException(
            status_code=503, detail=f"Failed to fetch news from HuggingFace: {str(e)}"
        )


@router.get("/api/news/latest")
async def get_latest_news(
    symbol: str = Query("BTC", description="Crypto symbol"),
    limit: int = Query(10, description="Number of articles"),
):
    """
    دریافت آخرین اخبار برای سمبل خاص
    """
    try:
        # HF news endpoint filters by source, we return all and user can filter client-side
        result = await hf_client.get_news(limit=limit)

        return {
            "success": True,
            "symbol": symbol,
            "news": result.get("articles", []),
            "meta": {
                "total": len(result.get("articles", [])),
                "source": "hf_engine",
                "timestamp": datetime.utcnow().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"❌ Latest news failed: {e}")
        raise HTTPException(status_code=503, detail=f"Failed to fetch latest news: {str(e)}")


# ============================================================================
# Blockchain Data - از HuggingFace فقط
# ============================================================================


@router.get("/api/blockchain/gas")
async def get_gas_prices(chain: str = Query("ethereum", description="Blockchain network")):
    """
    دریافت قیمت گس از HuggingFace Space

    ✅ فقط از HuggingFace
    ❌ بدون Etherscan/BSCScan مستقیم
    """
    try:
        result = await hf_client.get_blockchain_gas_prices(chain=chain)

        logger.info(f"✅ Gas prices from HF: {chain}")
        return result

    except Exception as e:
        logger.error(f"❌ Gas prices failed: {e}")
        raise HTTPException(
            status_code=503, detail=f"Failed to fetch gas prices from HuggingFace: {str(e)}"
        )


@router.get("/api/blockchain/stats")
async def get_blockchain_stats(
    chain: str = Query("ethereum", description="Blockchain network"),
    hours: int = Query(24, description="Time window in hours"),
):
    """
    دریافت آمار بلاکچین از HuggingFace Space
    """
    try:
        result = await hf_client.get_blockchain_stats(chain=chain, hours=hours)

        logger.info(f"✅ Blockchain stats from HF: {chain}")
        return result

    except Exception as e:
        logger.error(f"❌ Blockchain stats failed: {e}")
        raise HTTPException(
            status_code=503, detail=f"Failed to fetch blockchain stats from HuggingFace: {str(e)}"
        )


# ============================================================================
# Whale Tracking - از HuggingFace فقط
# ============================================================================


@router.get("/api/whales/transactions")
async def get_whale_transactions(
    limit: int = Query(50, description="Number of transactions"),
    chain: Optional[str] = Query(None, description="Filter by blockchain"),
    min_amount_usd: float = Query(100000, description="Minimum amount in USD"),
):
    """
    دریافت تراکنش‌های نهنگ‌ها از HuggingFace Space
    """
    try:
        result = await hf_client.get_whale_transactions(
            limit=limit, chain=chain, min_amount_usd=min_amount_usd
        )

        logger.info(f"✅ Whale transactions from HF: {len(result.get('transactions', []))}")
        return result

    except Exception as e:
        logger.error(f"❌ Whale transactions failed: {e}")
        raise HTTPException(
            status_code=503, detail=f"Failed to fetch whale transactions from HuggingFace: {str(e)}"
        )


@router.get("/api/whales/stats")
async def get_whale_stats(hours: int = Query(24, description="Time window in hours")):
    """
    دریافت آمار نهنگ‌ها از HuggingFace Space
    """
    try:
        result = await hf_client.get_whale_stats(hours=hours)

        logger.info(f"✅ Whale stats from HF")
        return result

    except Exception as e:
        logger.error(f"❌ Whale stats failed: {e}")
        raise HTTPException(
            status_code=503, detail=f"Failed to fetch whale stats from HuggingFace: {str(e)}"
        )


# ============================================================================
# Health & Status
# ============================================================================


@router.get("/api/health")
async def health_check():
    """
    بررسی سلامت سیستم با چک HuggingFace Space
    """
    try:
        hf_health = await hf_client.health_check()

        return {
            "status": "healthy" if hf_health.get("success") else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "huggingface_space": hf_health,
            "checks": {
                "hf_space_connection": hf_health.get("success", False),
                "hf_database": hf_health.get("database", "unknown"),
                "hf_ai_models": hf_health.get("ai_models", {}),
            },
        }

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "checks": {"hf_space_connection": False},
        }


@router.get("/api/status")
async def get_system_status():
    """
    دریافت وضعیت کلی سیستم
    """
    try:
        hf_status = await hf_client.get_system_status()

        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "mode": "UNIFIED_HUGGINGFACE_ONLY",
            "mock_data": False,
            "direct_api_calls": False,
            "all_via_huggingface": True,
            "huggingface_space": hf_status,
            "version": "3.0.0-unified-hf",
        }

    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        return {
            "status": "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "mode": "UNIFIED_HUGGINGFACE_ONLY",
        }


@router.get("/api/providers")
async def get_providers():
    """
    لیست ارائه‌دهندگان - فقط HuggingFace
    """
    providers = [
        {
            "id": "huggingface_space",
            "name": "HuggingFace Space",
            "category": "all",
            "status": "active",
            "capabilities": [
                "market_data",
                "ohlcv",
                "sentiment_analysis",
                "news",
                "blockchain_stats",
                "whale_tracking",
                "ai_models",
            ],
            "has_api_token": True,
            "endpoint": hf_client.base_url,
        }
    ]

    return {
        "success": True,
        "providers": providers,
        "total": len(providers),
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "unified_source": "huggingface_space",
            "no_direct_api_calls": True,
        },
    }


# Export router
__all__ = ["router"]
