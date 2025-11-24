#!/usr/bin/env python3
"""
Unified App - Complete Integration
FastAPI + Static UI + Unified Resource Loader
Ready for Docker/HuggingFace Spaces deployment
"""

import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import our unified API service router
from unified_api_service import router as api_router, init_loader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment configuration
PORT = int(os.getenv("PORT", "7860"))
HOST = os.getenv("HOST", "0.0.0.0")

# Paths
WORKSPACE_ROOT = Path("/app" if Path("/app").exists() else ".")
STATIC_DIR = WORKSPACE_ROOT / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Create main app
app = FastAPI(
    title="Crypto Intelligence Hub - Unified",
    description="AI-Powered Cryptocurrency Data Collection & Analysis Center",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    logger.info("🚀 Starting Unified Crypto Intelligence Hub")
    logger.info(f"📁 Workspace: {WORKSPACE_ROOT}")
    logger.info(f"🌐 Port: {PORT}")

    # Initialize unified resource loader
    init_loader()

    logger.info("✅ Unified App Ready!")


# Include the unified API router
app.include_router(api_router)


# Serve static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def serve_index():
    """Serve the main index.html file"""
    index_file = WORKSPACE_ROOT / "index.html"

    if index_file.exists():
        return FileResponse(str(index_file))

    # Fallback: return API info
    return {
        "name": "Crypto Intelligence Hub - Unified",
        "version": "2.0.0",
        "status": "running",
        "api_docs": "/docs",
        "api_base": "/api",
        "note": "index.html not found - serving API only"
    }


@app.get("/ai-tools")
async def serve_ai_tools():
    """Serve the AI tools page"""
    ai_tools_file = WORKSPACE_ROOT / "ai_tools.html"

    if ai_tools_file.exists():
        return FileResponse(str(ai_tools_file))

    return {"error": "AI tools page not found"}


@app.get("/admin")
async def serve_admin():
    """Serve the admin page"""
    admin_file = WORKSPACE_ROOT / "admin.html"

    if admin_file.exists():
        return FileResponse(str(admin_file))

    return {"error": "Admin page not found"}


@app.get("/health")
async def health_check():
    """Health check for the entire application"""
    return {
        "status": "healthy",
        "app": "unified",
        "version": "2.0.0",
        "api_available": True
    }


@app.get("/info")
async def app_info():
    """Get application information"""
    return {
        "app": "Crypto Intelligence Hub - Unified",
        "version": "2.0.0",
        "description": "Unified cryptocurrency data platform with single JSON source of truth",
        "features": [
            "Unified Resource Loader (137+ data sources)",
            "Market Data APIs (CoinGecko, Binance, etc.)",
            "News APIs (CryptoPanic, CoinStats, RSS feeds)",
            "Sentiment APIs (Fear & Greed Index)",
            "Block Explorers (Etherscan, BscScan, TronScan)",
            "On-chain Analytics",
            "Whale Tracking",
            "HuggingFace AI Models",
            "Static UI (index.html, ai_tools.html)",
            "FastAPI Backend",
            "Docker Ready"
        ],
        "endpoints": {
            "main": "/",
            "ai_tools": "/ai-tools",
            "admin": "/admin",
            "api_docs": "/docs",
            "api_resources": "/api/resources/stats",
            "api_market": "/api/market/price/{symbol}",
            "api_news": "/api/news",
            "api_sentiment": "/api/sentiment/fear-greed",
            "api_health": "/api/health"
        },
        "data_source": "crypto_resources_unified_2025-11-11.json"
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting server on {HOST}:{PORT}")

    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )
