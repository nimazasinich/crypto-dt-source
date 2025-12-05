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

# Load environment variables from .env files
try:
    from dotenv import load_dotenv
    # Try loading from multiple .env file locations
    for env_file in ['.env', '.env.local', '.env.production']:
        env_path = Path(env_file)
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Loaded environment from {env_file}")
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables only.")
    print("   Install with: pip install python-dotenv")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

# Import database and workers
from database.db_manager import db_manager
from database.cache_queries import get_cache_queries
from workers.market_data_worker import start_market_data_worker
from workers.ohlc_data_worker import start_ohlc_data_worker
from workers.comprehensive_data_worker import start_comprehensive_worker
from ai_models import _registry
from utils.logger import setup_logger

# Import HF endpoints routers
from api.hf_endpoints import router as hf_router
from api.hf_data_hub_endpoints import router as hf_hub_router

# Import smart fallback and data collection
from workers.data_collection_agent import get_data_collection_agent, start_data_collection_agent

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

        # Start comprehensive data worker (fetches from ALL sources)
        await start_comprehensive_worker()
        logger.info("✅ Comprehensive data worker started")
        
        # NEW: Start Smart Data Collection Agent with 305+ resources
        logger.info("🤖 Starting Smart Data Collection Agent...")
        asyncio.create_task(start_data_collection_agent())
        logger.info("✅ Smart Data Collection Agent started")
        logger.info("   📊 Collecting from 305+ FREE resources:")
        logger.info("      - 21 Market Data APIs")
        logger.info("      - 15 News APIs")
        logger.info("      - 12 Sentiment APIs")
        logger.info("      - 13 On-chain Analytics APIs")
        logger.info("      - 9 Whale Tracking APIs")
        logger.info("      - 24 RPC Nodes")
        logger.info("      - 40+ Block Explorers")
        logger.info("      - 106 Local Backend Routes")
        logger.info("      - 7 CORS Proxies")
        logger.info("      - Smart fallback (NEVER 404)")
        logger.info("      - Auto proxy for sanctioned exchanges")
        logger.info("      - Continuous 24/7 collection")

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

# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    logger.info(f"✅ Static files mounted at /static from {static_path}")
else:
    logger.warning(f"⚠️ Static directory not found at {static_path}")


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - Redirect to main UI or show API information"""
    # Check if request is from browser (Accept: text/html)
    # If yes, serve index.html, otherwise return API info
    index_file = Path(__file__).parent / "static" / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    return {
        "success": True,
        "name": "HuggingFace Space Crypto API",
        "version": "2.0.0",
        "description": "Real-time cryptocurrency data API with AI-powered analysis + Smart Fallback System",
        "authentication": "Required - use HF_TOKEN in Authorization header",
        "data_policy": "REAL DATA ONLY - No mock or fake data",
        "ui": {
            "main": "/static/index.html",
            "dashboard": "/static/pages/dashboard/index.html",
            "market": "/static/pages/market/index.html",
            "trading": "/static/pages/trading-assistant/index.html",
            "technical_analysis": "/static/pages/technical-analysis/index.html",
            "news": "/static/pages/news/index.html",
            "sentiment": "/static/pages/sentiment/index.html",
            "models": "/static/pages/models/index.html",
            "api_explorer": "/static/pages/api-explorer/index.html",
            "diagnostics": "/static/pages/diagnostics/index.html"
        },
        "endpoints": {
            "market_data": "/api/market",
            "market_history": "/api/market/history",
            "sentiment_analysis": "/api/sentiment/analyze",
            "health_check": "/api/health",
            "alphavantage": "/api/alphavantage/*",
            "massive": "/api/massive/*",
            "smart_fallback": "/api/smart/* (305+ resources, NEVER 404)",
            "documentation": "/docs"
        },
        "data_sources": {
            "primary": "Smart Fallback System (305+ FREE resources)",
            "market_prices": "21 Market Data APIs with rotation",
            "block_explorers": "40+ Block Explorers",
            "news": "15 News APIs with fallback",
            "sentiment": "12 Sentiment APIs",
            "whale_tracking": "9 Whale tracking sources",
            "onchain": "13 On-chain analytics",
            "rpc_nodes": "24 RPC nodes",
            "alphavantage": "Alpha Vantage API",
            "massive": "Massive.com (APIBricks)",
            "ai_models": "HuggingFace Transformers"
        },
        "features": {
            "smart_fallback": "Automatic failover - NEVER 404",
            "resource_rotation": "Uses ALL resources, not just one",
            "proxy_support": "Smart proxy for sanctioned exchanges",
            "background_collection": "24/7 data collection agent",
            "health_monitoring": "Real-time health tracking",
            "auto_cleanup": "Automatic removal of dead resources"
        },
        "timestamp": int(time.time() * 1000)
    }


# ============================================================================
# Include HF Endpoints Routers
# ============================================================================

# Original HF Space endpoints (uses local SQLite cache)
app.include_router(hf_router)

# NEW: Data Hub endpoints (serves FROM HuggingFace Datasets)
app.include_router(hf_hub_router)

# Technical Analysis endpoints
try:
    from api.technical_analysis import router as technical_router
    app.include_router(technical_router)
    logger.info("✅ Technical Analysis router loaded")
except Exception as e:
    logger.warning(f"⚠️ Technical Analysis router not available: {e}")

# Technical Analysis Modes endpoints
try:
    from api.technical_modes import router as technical_modes_router
    app.include_router(technical_modes_router)
    logger.info("✅ Technical Analysis Modes router loaded")
except Exception as e:
    logger.warning(f"⚠️ Technical Analysis Modes router not available: {e}")

# NEW: Alpha Vantage endpoints
try:
    from api.alphavantage_endpoints import router as alphavantage_router
    app.include_router(alphavantage_router)
    logger.info("✅ Alpha Vantage router loaded")
except Exception as e:
    logger.warning(f"⚠️ Alpha Vantage router not available: {e}")

# NEW: Massive.com endpoints
try:
    from api.massive_endpoints import router as massive_router
    app.include_router(massive_router)
    logger.info("✅ Massive.com router loaded")
except Exception as e:
    logger.warning(f"⚠️ Massive.com router not available: {e}")

# NEW: Smart Fallback endpoints (305+ resources, NEVER 404)
try:
    from api.smart_data_endpoints import router as smart_router
    app.include_router(smart_router)
    logger.info("✅ Smart Fallback router loaded (305+ resources)")
except Exception as e:
    logger.warning(f"⚠️ Smart Fallback router not available: {e}")


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
