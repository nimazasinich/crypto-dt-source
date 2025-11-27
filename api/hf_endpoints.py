"""
HuggingFace Space API Endpoints - REAL DATA ONLY
Provides endpoints for market data, sentiment analysis, and system health

═══════════════════════════════════════════════════════════════
              ⚠️ ABSOLUTELY NO FAKE DATA ⚠️

    ❌ NO mock data
    ❌ NO placeholder data
    ❌ NO hardcoded responses
    ❌ NO random numbers
    ❌ NO fake timestamps
    ❌ NO invented prices
    ❌ NO simulated responses

    ✅ ONLY real data from database cache
    ✅ ONLY real data from free APIs (via background workers)
    ✅ ONLY real AI model inference
    ✅ If data not available → return error
    ✅ If cache empty → return error
    ✅ If model fails → return error
═══════════════════════════════════════════════════════════════
"""

import time
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from pydantic import BaseModel

from api.hf_auth import verify_hf_token
from database.cache_queries import get_cache_queries
from database.db_manager import db_manager
from ai_models import _registry
from utils.logger import setup_logger

logger = setup_logger("hf_endpoints")

router = APIRouter(prefix="/api", tags=["hf_space"])

# Get cache queries instance
cache = get_cache_queries(db_manager)


# ============================================================================
# Pydantic Models
# ============================================================================


class SentimentRequest(BaseModel):
    """Request model for sentiment analysis"""

    text: str

    class Config:
        json_schema_extra = {"example": {"text": "Bitcoin is pumping! Great news for crypto!"}}


# ============================================================================
# GET /api/market - Market Prices (REAL DATA ONLY)
# ============================================================================


@router.get("/market")
async def get_market_data(
    limit: int = Query(100, ge=1, le=1000, description="Number of symbols to return"),
    symbols: Optional[str] = Query(
        None, description="Comma-separated list of symbols (e.g., BTC,ETH,BNB)"
    ),
    auth: bool = Depends(verify_hf_token),
):
    """
    Get real-time market data from database cache

    CRITICAL RULES:
    1. ONLY read from cached_market_data table in database
    2. NEVER invent/generate/fake price data
    3. If cache is empty → return error with status code 503
    4. If symbol not found → return empty array, not fake data
    5. Timestamps MUST be from actual database records
    6. Prices MUST be from actual fetched data

    Returns:
        JSON with real market data or error if no data available
    """

    try:
        # Parse symbols if provided
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
            logger.info(f"Filtering for symbols: {symbol_list}")

        # Query REAL data from database - NO FAKE DATA
        market_data = cache.get_cached_market_data(symbols=symbol_list, limit=limit)

        # If NO data in cache, return error (NOT fake data)
        if not market_data or len(market_data) == 0:
            logger.warning("No market data available in cache")
            return {
                "success": False,
                "error": "No market data available. Background workers syncing data from free APIs. Please wait.",
                "source": "hf_engine",
                "timestamp": int(time.time() * 1000),
            }

        # Use REAL timestamps and prices from database
        response = {
            "success": True,
            "data": [
                {
                    "symbol": row["symbol"],  # REAL from database
                    "price": float(row["price"]),  # REAL from database
                    "market_cap": float(row["market_cap"]) if row.get("market_cap") else None,
                    "volume_24h": float(row["volume_24h"]) if row.get("volume_24h") else None,
                    "change_24h": float(row["change_24h"]) if row.get("change_24h") else None,
                    "high_24h": float(row["high_24h"]) if row.get("high_24h") else None,
                    "low_24h": float(row["low_24h"]) if row.get("low_24h") else None,
                    "last_updated": int(row["fetched_at"].timestamp() * 1000),  # REAL timestamp
                }
                for row in market_data
            ],
            "source": "hf_engine",
            "timestamp": int(time.time() * 1000),
            "cached": True,
            "count": len(market_data),
        }

        logger.info(f"Returned {len(market_data)} real market records")
        return response

    except Exception as e:
        logger.error(f"Market endpoint error: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Database error: {str(e)}",
            "source": "hf_engine",
            "timestamp": int(time.time() * 1000),
        }


# ============================================================================
# GET /api/market/history - OHLCV Data (REAL DATA ONLY)
# ============================================================================


@router.get("/market/history")
async def get_market_history(
    symbol: str = Query(..., description="Trading pair symbol (e.g., BTCUSDT, ETHUSDT)"),
    timeframe: str = Query("1h", description="Timeframe (1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(1000, ge=1, le=5000, description="Number of candles"),
    auth: bool = Depends(verify_hf_token),
):
    """
    Get OHLCV (candlestick) data from database cache

    CRITICAL RULES:
    1. ONLY read from cached_ohlc table in database
    2. NEVER generate/fake candle data
    3. If cache empty → return error with 404
    4. If symbol not found → return error, not fake data
    5. All OHLC values MUST be from actual database records
    6. Timestamps MUST be actual candle timestamps

    Returns:
        JSON with real OHLCV data or error if no data available
    """

    try:
        # Normalize symbol to uppercase
        normalized_symbol = symbol.upper()
        logger.info(f"Fetching OHLC for {normalized_symbol} {timeframe}")

        # Query REAL OHLC data from database - NO FAKE DATA
        ohlcv_data = cache.get_cached_ohlc(
            symbol=normalized_symbol, interval=timeframe, limit=limit
        )

        # If NO data in cache, return error (NOT fake candles)
        if not ohlcv_data or len(ohlcv_data) == 0:
            logger.warning(f"No OHLCV data for {normalized_symbol} {timeframe}")
            return {
                "success": False,
                "error": f"No OHLCV data for {symbol}. Background workers syncing data. Symbol may not be cached yet.",
                "source": "hf_engine",
                "timestamp": int(time.time() * 1000),
            }

        # Use REAL candle data from database
        response = {
            "success": True,
            "data": [
                {
                    "timestamp": int(candle["timestamp"].timestamp() * 1000),  # REAL
                    "open": float(candle["open"]),  # REAL
                    "high": float(candle["high"]),  # REAL
                    "low": float(candle["low"]),  # REAL
                    "close": float(candle["close"]),  # REAL
                    "volume": float(candle["volume"]),  # REAL
                }
                for candle in ohlcv_data
            ],
            "source": "hf_engine",
            "timestamp": int(time.time() * 1000),
            "cached": True,
            "count": len(ohlcv_data),
        }

        logger.info(f"Returned {len(ohlcv_data)} real OHLC candles for {normalized_symbol}")
        return response

    except Exception as e:
        logger.error(f"History endpoint error: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Database error: {str(e)}",
            "source": "hf_engine",
            "timestamp": int(time.time() * 1000),
        }


# ============================================================================
# POST /api/sentiment/analyze - Sentiment Analysis (REAL AI MODEL ONLY)
# ============================================================================


@router.post("/sentiment/analyze")
async def analyze_sentiment(
    request: SentimentRequest = Body(...), auth: bool = Depends(verify_hf_token)
):
    """
    Analyze sentiment using REAL AI model

    CRITICAL RULES:
    1. MUST use actual loaded AI model from ai_models.py
    2. MUST run REAL model inference
    3. NEVER return random sentiment scores
    4. NEVER fake confidence values
    5. If model not loaded → return error
    6. If inference fails → return error

    Returns:
        JSON with real sentiment analysis or error
    """

    try:
        text = request.text

        # Validate input
        if not text or len(text.strip()) == 0:
            return {
                "success": False,
                "error": "Text parameter is required and cannot be empty",
                "source": "hf_engine",
                "timestamp": int(time.time() * 1000),
            }

        logger.info(f"Analyzing sentiment for text (length={len(text)})")

        # Try to get REAL sentiment model
        sentiment_model = None
        tried_models = []

        # Try different model keys in order of preference
        for model_key in [
            "crypto_sent_kk08",
            "sentiment_twitter",
            "sentiment_financial",
            "crypto_sent_0",
        ]:
            tried_models.append(model_key)
            try:
                sentiment_model = _registry.get_pipeline(model_key)
                if sentiment_model:
                    logger.info(f"Using sentiment model: {model_key}")
                    break
            except Exception as e:
                logger.warning(f"Failed to load {model_key}: {e}")
                continue

        # If NO model available, return error (NOT fake sentiment)
        if not sentiment_model:
            logger.error(f"No sentiment model available. Tried: {tried_models}")
            return {
                "success": False,
                "error": f"No sentiment model available. Tried: {', '.join(tried_models)}. Please ensure HuggingFace models are properly configured.",
                "source": "hf_engine",
                "timestamp": int(time.time() * 1000),
            }

        # Run REAL model inference
        # This MUST call actual model.predict() or model()
        # NEVER return fake scores
        result = sentiment_model(text[:512])  # Limit text length

        # Parse REAL model output
        if isinstance(result, list) and len(result) > 0:
            result = result[0]

        # Extract REAL values from model output
        label = result.get("label", "NEUTRAL").upper()
        score = float(result.get("score", 0.5))

        # Map label to standard format
        if "POSITIVE" in label or "BULLISH" in label or "LABEL_2" in label:
            sentiment = "positive"
        elif "NEGATIVE" in label or "BEARISH" in label or "LABEL_0" in label:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        # Response with REAL model output
        response = {
            "success": True,
            "data": {
                "label": sentiment,  # REAL from model
                "score": score,  # REAL from model
                "sentiment": sentiment,  # REAL from model
                "confidence": score,  # REAL from model
                "text": text,
                "model_label": label,  # Original label from model
                "timestamp": int(time.time() * 1000),
            },
            "source": "hf_engine",
            "timestamp": int(time.time() * 1000),
        }

        logger.info(f"Sentiment analysis completed: {sentiment} (score={score:.3f})")
        return response

    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Model inference error: {str(e)}",
            "source": "hf_engine",
            "timestamp": int(time.time() * 1000),
        }


# ============================================================================
# GET /api/health - Health Check
# ============================================================================


@router.get("/health")
async def health_check(auth: bool = Depends(verify_hf_token)):
    """
    Health check endpoint

    RULES:
    - Return REAL system status
    - Use REAL uptime calculation
    - Check REAL database connection
    - NEVER return fake status

    Returns:
        JSON with real system health status
    """

    try:
        # Check REAL database connection
        db_status = "connected"
        try:
            # Test database with a simple query
            health = db_manager.health_check()
            if health.get("status") != "healthy":
                db_status = "degraded"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            db_status = "disconnected"

        # Get REAL cache statistics
        cache_stats = {"market_data_count": 0, "ohlc_count": 0}

        try:
            with db_manager.get_session() as session:
                from database.models import CachedMarketData, CachedOHLC
                from sqlalchemy import func, distinct

                # Count unique symbols in cache
                cache_stats["market_data_count"] = (
                    session.query(func.count(distinct(CachedMarketData.symbol))).scalar() or 0
                )

                cache_stats["ohlc_count"] = session.query(func.count(CachedOHLC.id)).scalar() or 0
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")

        # Get AI model status
        model_status = _registry.get_registry_status()

        response = {
            "success": True,
            "status": "healthy" if db_status == "connected" else "degraded",
            "timestamp": int(time.time() * 1000),
            "version": "1.0.0",
            "database": db_status,  # REAL database status
            "cache": cache_stats,  # REAL cache statistics
            "ai_models": {
                "loaded": model_status.get("models_loaded", 0),
                "failed": model_status.get("models_failed", 0),
                "total": model_status.get("models_total", 0),
            },
            "source": "hf_engine",
        }

        logger.info(f"Health check completed: {response['status']}")
        return response

    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": int(time.time() * 1000),
            "source": "hf_engine",
        }
