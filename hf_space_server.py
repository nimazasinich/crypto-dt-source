"""
HuggingFace Space Server - REAL DATA ONLY
Main server for HuggingFace Space deployment

═══════════════════════════════════════════════════════════════
              ⚠️ ABSOLUTELY NO FAKE DATA ⚠️

    ✅ ONLY real data from database cache
    ✅ ONLY real data from free APIs (via background workers)
    ✅ ONLY real AI model inference
    ✅ If data not available → return error
═══════════════════════════════════════════════════════════════
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.hf_endpoints import router as hf_router
from database.db_manager import db_manager
from database.models import Base
from ai_models import initialize_models
from workers.market_data_worker import start_market_data_worker
from workers.ohlc_data_worker import start_ohlc_data_worker
from utils.logger import setup_logger

logger = setup_logger("hf_server")

# Application startup time
start_time = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan - startup and shutdown
    """
    global start_time
    import time

    start_time = time.time()

    logger.info("=" * 70)
    logger.info("🚀 Starting HuggingFace Space Server - REAL DATA ONLY")
    logger.info("=" * 70)

    # 1. Initialize database
    logger.info("📊 Initializing database...")
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=db_manager.engine)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

    # 2. Initialize AI models
    logger.info("🤖 Initializing AI models...")
    try:
        model_status = initialize_models()
        logger.info(f"✅ AI models initialized: {model_status}")
    except Exception as e:
        logger.warning(f"⚠️ AI models initialization warning: {e}")
        # Continue even if models fail - can use fallback

    # 3. Start background workers
    logger.info("🔄 Starting background workers...")
    try:
        # Start market data worker (CoinGecko)
        await start_market_data_worker()
        logger.info("✅ Market data worker started")

        # Start OHLC data worker (Binance)
        await start_ohlc_data_worker()
        logger.info("✅ OHLC data worker started")
    except Exception as e:
        logger.error(f"❌ Worker startup failed: {e}")
        # Continue even if workers fail initially

    # 4. Check HF_TOKEN
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    if hf_token:
        logger.info(f"🔑 HF_TOKEN configured (length: {len(hf_token)})")
    else:
        logger.warning("⚠️ HF_TOKEN not configured - authentication will fail")

    logger.info("=" * 70)
    logger.info("✅ HuggingFace Space Server is ready!")
    logger.info("📍 Endpoints:")
    logger.info("   - GET  /api/market           - Real market data")
    logger.info("   - GET  /api/market/history   - Real OHLCV data")
    logger.info("   - POST /api/sentiment/analyze - Real AI sentiment")
    logger.info("   - GET  /api/health           - Health check")
    logger.info("=" * 70)

    # Store start time in app state
    app.state.start_time = start_time

    yield

    # Shutdown
    logger.info("🛑 Shutting down HuggingFace Space Server...")


# Create FastAPI app
app = FastAPI(
    title="HuggingFace Crypto Data Engine",
    description="Real-time cryptocurrency data API with AI-powered sentiment analysis",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include HuggingFace endpoints
app.include_router(hf_router)


@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": "HuggingFace Crypto Data Engine",
        "version": "1.0.0",
        "status": "online",
        "description": "Real-time cryptocurrency data with AI sentiment analysis",
        "endpoints": {
            "market": "/api/market",
            "history": "/api/market/history",
            "sentiment": "/api/sentiment/analyze",
            "health": "/api/health",
        },
        "authentication": "Bearer token required (HF_TOKEN)",
        "data_sources": {
            "market_data": "CoinGecko (FREE API)",
            "ohlc_data": "Binance (FREE API)",
            "sentiment": "HuggingFace AI Models",
        },
        "note": "All data is REAL - no fake/mock/placeholder data",
    }


@app.get("/status")
async def status():
    """
    Server status endpoint (no authentication required)
    """
    import time

    uptime = int(time.time() - start_time) if start_time else 0

    return {"status": "online", "uptime_seconds": uptime, "timestamp": int(time.time() * 1000)}


if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PORT", "7860"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(app, host=host, port=port, log_level="info", access_log=True)
