#!/usr/bin/env python3
"""
Cryptocurrency Data Engine Server - REAL DATA ONLY
FastAPI server that provides cryptocurrency data from real sources
NO MOCK DATA - All endpoints return real data from live APIs
"""

import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# Lifespan context manager
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Cryptocurrency Data Engine Server")
    logger.info("=" * 80)
    logger.info("📊 Mode: REAL DATA ONLY (NO MOCK DATA)")
    logger.info("=" * 80)
    
    # Check environment variables
    hf_token = os.getenv("HF_API_TOKEN", "")
    newsapi_key = os.getenv("NEWSAPI_KEY", "")
    cryptopanic_token = os.getenv("CRYPTOPANIC_TOKEN", "")
    
    logger.info("🔑 API Keys Status:")
    logger.info(f"  - HuggingFace API Token: {'✅ Set' if hf_token else '⚠️ Not set'}")
    logger.info(f"  - NewsAPI Key: {'✅ Set' if newsapi_key else '⚠️ Not set'}")
    logger.info(f"  - CryptoPanic Token: {'✅ Set' if cryptopanic_token else '⚠️ Not set'}")
    
    logger.info("")
    logger.info("📡 Data Sources:")
    logger.info("  - CoinGecko API: https://api.coingecko.com/api/v3")
    logger.info("  - Binance Public API: https://api.binance.com/api/v3")
    logger.info("  - HuggingFace Inference: https://api-inference.huggingface.co")
    logger.info("  - NewsAPI: https://newsapi.org/v2")
    
    logger.info("")
    logger.info("🎯 Available Endpoints:")
    logger.info("  - GET  /api/health           - Health check")
    logger.info("  - GET  /api/status           - System status")
    logger.info("  - GET  /api/market           - Real-time market prices (CoinGecko)")
    logger.info("  - GET  /api/market/history   - OHLCV historical data (Binance)")
    logger.info("  - GET  /api/trending         - Trending coins (CoinGecko)")
    logger.info("  - POST /api/sentiment/analyze - Sentiment analysis (HuggingFace)")
    logger.info("  - GET  /api/news/latest      - Latest crypto news")
    
    logger.info("")
    logger.info("✅ Server started successfully!")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Cryptocurrency Data Engine Server")


# ============================================================================
# Create FastAPI app
# ============================================================================

app = FastAPI(
    title="Cryptocurrency Data Engine API",
    description=(
        "Cryptocurrency data API providing REAL data from live sources. "
        "NO MOCK DATA - All endpoints fetch real data from CoinGecko, Binance, "
        "HuggingFace, and news APIs."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ============================================================================
# CORS Middleware
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Include routers
# ============================================================================

try:
    from backend.routers.crypto_data_engine_api import router as data_engine_router
    
    app.include_router(
        data_engine_router,
        tags=["Crypto Data Engine"]
    )
    
    logger.info("✅ Crypto Data Engine router loaded successfully")

except ImportError as e:
    logger.error(f"❌ Failed to import crypto_data_engine_api router: {e}")
    logger.error("Server will start with limited functionality")


# ============================================================================
# Root endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Cryptocurrency Data Engine API",
        "version": "1.0.0",
        "description": "Real cryptocurrency data from live APIs - NO MOCK DATA",
        "mode": "REAL_DATA_ONLY",
        "documentation": "/docs",
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "market_prices": "/api/market",
            "ohlcv_history": "/api/market/history",
            "trending_coins": "/api/trending",
            "sentiment_analysis": "/api/sentiment/analyze",
            "latest_news": "/api/news/latest"
        },
        "data_sources": {
            "coingecko": "Market prices, trending coins",
            "binance": "OHLCV historical data",
            "huggingface": "Sentiment analysis",
            "newsapi": "Cryptocurrency news"
        }
    }


# ============================================================================
# Error handlers
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "detail": f"The endpoint {request.url.path} does not exist",
            "documentation": "/docs"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
            "timestamp": int(Path(__file__).stat().st_mtime)
        }
    )


# ============================================================================
# Main entry point (for local development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "crypto_data_engine_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
