#!/usr/bin/env python3
"""
HuggingFace Space FastAPI Application - REAL DATA ONLY
Complete implementation with authentication, real data endpoints, and background workers

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
    
    NO EXCEPTIONS TO THIS RULE
═══════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

# Import database and workers
from database.db_manager import db_manager
from database.cache_queries import get_cache_queries
from workers.market_data_worker import start_market_data_worker
from workers.ohlc_data_worker import start_ohlc_data_worker
from ai_models import _registry
from utils.logger import setup_logger

# Import HF endpoints router
from api.hf_endpoints import router as hf_router

# Setup logging
logger = setup_logger("hf_space_api", level="INFO")

# Global state
app_start_time = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    global app_start_time
    app_start_time = time.time()
    
    logger.info("=" * 80)
    logger.info("🚀 Starting HuggingFace Space API Server - REAL DATA ONLY")
    logger.info("=" * 80)
    
    # Phase 1: Initialize database
    logger.info("📊 Phase 1: Initializing database...")
    try:
        # Initialize database tables
        success = db_manager.init_database()
        if success:
            logger.info("✅ Database tables created successfully")
        else:
            logger.error("❌ Failed to initialize database tables")
            raise Exception("Database initialization failed")
        
        # Test database connection
        health = db_manager.health_check()
        if health.get("status") == "healthy":
            logger.info(f"✅ Database connection healthy: {health}")
        else:
            logger.warning(f"⚠️  Database health check warning: {health}")
    
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}", exc_info=True)
        raise
    
    # Phase 2: Initialize AI models
    logger.info("🤖 Phase 2: Initializing AI models...")
    try:
        result = _registry.initialize_models()
        if result.get("status") in ["ok", "fallback_only"]:
            logger.info(f"✅ AI models initialized: {result}")
        else:
            logger.warning(f"⚠️  AI model initialization warning: {result}")
    except Exception as e:
        logger.error(f"❌ AI model initialization error: {e}", exc_info=True)
        # Don't fail on model errors - continue with fallback
    
    # Phase 3: Start background workers
    logger.info("⚙️  Phase 3: Starting background workers...")
    try:
        # Start market data worker (fetches from CoinGecko)
        await start_market_data_worker()
        logger.info("✅ Market data worker started")
        
        # Start OHLC data worker (fetches from Binance)
        await start_ohlc_data_worker()
        logger.info("✅ OHLC data worker started")
        
    except Exception as e:
        logger.error(f"❌ Worker startup error: {e}", exc_info=True)
        # Don't fail on worker errors - they will retry
    
    # Phase 4: Ready
    logger.info("=" * 80)
    logger.info("✅ HuggingFace Space API Server is READY")
    logger.info(f"📡 Endpoints available at: http://0.0.0.0:7860/api/*")
    logger.info(f"📖 API Documentation: http://0.0.0.0:7860/docs")
    logger.info(f"🔒 Authentication: Required (HF_TOKEN)")
    logger.info("=" * 80)
    
    # Store start time in app state
    app.state.start_time = app_start_time
    
    # Yield control back to FastAPI
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down HuggingFace Space API Server...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="HuggingFace Space Crypto API - REAL DATA ONLY",
    description="""
    Cryptocurrency Data API with REAL data from free APIs
    
    ## 🔒 Authentication Required
    All endpoints require HF_TOKEN authentication via Authorization header
    
    ## 📡 Available Endpoints
    - GET  /api/market - Real-time market prices from CoinGecko
    - GET  /api/market/history - OHLCV candlestick data from Binance
    - POST /api/sentiment/analyze - AI sentiment analysis using real models
    - GET  /api/health - System health check
    
    ## ⚠️ CRITICAL RULE: NO FAKE DATA
    All endpoints return REAL data from database cache or return error.
    NO mock, placeholder, or generated data is ever returned.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "success": True,
        "name": "HuggingFace Space Crypto API",
        "version": "1.0.0",
        "description": "Real-time cryptocurrency data API with AI-powered analysis",
        "authentication": "Required - use HF_TOKEN in Authorization header",
        "data_policy": "REAL DATA ONLY - No mock or fake data",
        "endpoints": {
            "market_data": "/api/market",
            "market_history": "/api/market/history",
            "sentiment_analysis": "/api/sentiment/analyze",
            "health_check": "/api/health",
            "documentation": "/docs"
        },
        "data_sources": {
            "market_prices": "CoinGecko (FREE API)",
            "ohlcv_data": "Binance (FREE API)",
            "ai_models": "HuggingFace Transformers"
        },
        "timestamp": int(time.time() * 1000)
    }


# ============================================================================
# Include HF Endpoints Router
# ============================================================================

app.include_router(hf_router)


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "Endpoint not found",
            "path": str(request.url.path),
            "available_endpoints": [
                "/api/market",
                "/api/market/history",
                "/api/sentiment/analyze",
                "/api/health",
                "/docs"
            ],
            "source": "hf_engine",
            "timestamp": int(time.time() * 1000)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc),
            "source": "hf_engine",
            "timestamp": int(time.time() * 1000)
        }
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (HuggingFace Spaces uses 7860)
    port = int(os.getenv("PORT", "7860"))
    
    logger.info(f"🚀 Starting server on port {port}")
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
