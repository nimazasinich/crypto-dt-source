"""HuggingFace Cryptocurrency Data Engine - Main Application"""
from __future__ import annotations
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core.config import settings, get_supported_symbols, get_supported_intervals
from core.aggregator import get_aggregator
from core.cache import cache, cache_key, get_or_set
from core.models import (
    OHLCVResponse, PricesResponse, SentimentResponse,
    MarketOverviewResponse, HealthResponse, ErrorResponse, ErrorDetail, CacheInfo
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application"""
    logger.info("Starting HuggingFace Crypto Data Engine...")
    logger.info(f"Version: {settings.VERSION}")
    logger.info(f"Environment: {settings.ENV}")

    # Initialize aggregator
    aggregator = get_aggregator()

    yield

    # Cleanup
    logger.info("Shutting down...")
    await aggregator.close()


# Create FastAPI app
app = FastAPI(
    title="HuggingFace Cryptocurrency Data Engine",
    description="Comprehensive cryptocurrency data aggregator with multi-provider support",
    version=settings.VERSION,
    lifespan=lifespan
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message=str(exc)
            ),
            timestamp=int(time.time() * 1000)
        ).dict()
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "HuggingFace Cryptocurrency Data Engine",
        "version": settings.VERSION,
        "status": "online",
        "endpoints": {
            "health": "/api/health",
            "ohlcv": "/api/ohlcv",
            "prices": "/api/prices",
            "sentiment": "/api/sentiment",
            "market": "/api/market/overview",
            "docs": "/docs"
        }
    }


@app.get("/api/health", response_model=HealthResponse)
@limiter.limit(f"{settings.RATE_LIMIT_HEALTH or 999999}/minute")
async def health_check(request: Request):
    """Health check endpoint with provider status"""
    aggregator = get_aggregator()

    # Get provider health
    providers = await aggregator.get_all_provider_health()

    # Determine overall status
    online_count = sum(1 for p in providers if p.status == "online")
    if online_count == 0:
        overall_status = "unhealthy"
    elif online_count < len(providers) / 2:
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    # Get cache stats
    cache_stats = cache.get_stats()

    return HealthResponse(
        status=overall_status,
        uptime=aggregator.get_uptime(),
        version=settings.VERSION,
        providers=providers,
        cache=CacheInfo(**cache_stats)
    )


@app.get("/api/ohlcv", response_model=OHLCVResponse)
@limiter.limit(f"{settings.RATE_LIMIT_OHLCV}/minute")
async def get_ohlcv(
    request: Request,
    symbol: str = Query(..., description="Symbol (e.g., BTC, BTCUSDT, BTC/USDT)"),
    interval: str = Query("1h", description="Interval (1m, 5m, 15m, 1h, 4h, 1d, 1w)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles (1-1000)")
):
    """Get OHLCV candlestick data with multi-provider fallback"""

    # Validate interval
    if interval not in get_supported_intervals():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interval. Supported: {', '.join(get_supported_intervals())}"
        )

    # Normalize symbol
    normalized_symbol = symbol.upper().replace("/", "").replace("-", "")

    # Generate cache key
    key = cache_key("ohlcv", symbol=normalized_symbol, interval=interval, limit=limit)

    async def fetch():
        aggregator = get_aggregator()
        data, source = await aggregator.fetch_ohlcv(normalized_symbol, interval, limit)
        return {"data": data, "source": source}

    try:
        # Get from cache or fetch
        result = await get_or_set(key, settings.CACHE_TTL_OHLCV, fetch)

        return OHLCVResponse(
            data=result["data"],
            symbol=normalized_symbol,
            interval=interval,
            count=len(result["data"]),
            source=result["source"],
            timestamp=int(time.time() * 1000)
        )

    except Exception as e:
        logger.error(f"OHLCV fetch failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=ErrorDetail(
                code="PROVIDER_ERROR",
                message=f"All data providers failed: {str(e)}"
            ).dict()
        )


@app.get("/api/prices", response_model=PricesResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PRICES}/minute")
async def get_prices(
    request: Request,
    symbols: str = Query(None, description="Comma-separated symbols (e.g., BTC,ETH,SOL)"),
    convert: str = Query("USDT", description="Convert to currency (USD, USDT)")
):
    """Get real-time prices with multi-provider aggregation"""

    # Parse symbols
    if symbols:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
    else:
        # Use default symbols
        symbol_list = get_supported_symbols()

    # Generate cache key
    key = cache_key("prices", symbols=",".join(sorted(symbol_list)))

    async def fetch():
        aggregator = get_aggregator()
        data, source = await aggregator.fetch_prices(symbol_list)
        return {"data": data, "source": source}

    try:
        # Get from cache or fetch
        result = await get_or_set(key, settings.CACHE_TTL_PRICES, fetch)

        return PricesResponse(
            data=result["data"],
            timestamp=int(time.time() * 1000),
            source=result["source"]
        )

    except Exception as e:
        logger.error(f"Price fetch failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=ErrorDetail(
                code="PROVIDER_ERROR",
                message=f"All price providers failed: {str(e)}"
            ).dict()
        )


@app.get("/api/sentiment", response_model=SentimentResponse)
@limiter.limit(f"{settings.RATE_LIMIT_SENTIMENT}/minute")
async def get_sentiment(request: Request):
    """Get market sentiment data (Fear & Greed Index)"""

    if not settings.ENABLE_SENTIMENT:
        raise HTTPException(
            status_code=503,
            detail="Sentiment analysis is disabled"
        )

    # Cache key
    key = cache_key("sentiment")

    async def fetch():
        aggregator = get_aggregator()
        return await aggregator.fetch_sentiment()

    try:
        # Get from cache or fetch
        data = await get_or_set(key, settings.CACHE_TTL_SENTIMENT, fetch)

        return SentimentResponse(
            data=data,
            timestamp=int(time.time() * 1000)
        )

    except Exception as e:
        logger.error(f"Sentiment fetch failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=ErrorDetail(
                code="PROVIDER_ERROR",
                message=f"Failed to fetch sentiment: {str(e)}"
            ).dict()
        )


@app.get("/api/market/overview", response_model=MarketOverviewResponse)
@limiter.limit(f"{settings.RATE_LIMIT_SENTIMENT}/minute")
async def get_market_overview(request: Request):
    """Get market overview with global statistics"""

    # Cache key
    key = cache_key("market_overview")

    async def fetch():
        aggregator = get_aggregator()
        return await aggregator.fetch_market_overview()

    try:
        # Get from cache or fetch
        data = await get_or_set(key, settings.CACHE_TTL_MARKET, fetch)

        return MarketOverviewResponse(
            data=data,
            timestamp=int(time.time() * 1000)
        )

    except Exception as e:
        logger.error(f"Market overview fetch failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=ErrorDetail(
                code="PROVIDER_ERROR",
                message=f"Failed to fetch market overview: {str(e)}"
            ).dict()
        )


@app.post("/api/cache/clear")
async def clear_cache():
    """Clear all cached data"""
    cache.clear()
    return {"success": True, "message": "Cache cleared"}


@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return cache.get_stats()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=(settings.ENV == "development"),
        log_level="info"
    )
