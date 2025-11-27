#!/usr/bin/env python3
"""
Unified App - Complete Integration
FastAPI + Static UI + Unified Resource Loader
Ready for Docker/HuggingFace Spaces deployment
Full dashboard routing with static pages support
"""

import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import our unified API service router
try:
    from unified_api_service import router as api_router, init_loader
except ImportError:
    api_router = None
    def init_loader():
        pass

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
PAGES_DIR = STATIC_DIR / "pages"
STATIC_DIR.mkdir(exist_ok=True)

def get_page_index(page_name: str) -> Path:
    """Get the index.html path for a page"""
    page_path = PAGES_DIR / page_name / "index.html"
    return page_path if page_path.exists() else None

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
if api_router:
    app.include_router(api_router)


# Serve static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ============================================================================
# PAGE ROUTES - Dynamic routing for all pages in static/pages
# ============================================================================

@app.get("/")
async def serve_index():
    """Serve the main dashboard from static/pages/dashboard"""
    page_path = get_page_index("dashboard")
    if page_path:
        return FileResponse(str(page_path))
    
    # Fallback to root index.html
    index_file = WORKSPACE_ROOT / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))

    return {
        "name": "Crypto Intelligence Hub - Unified",
        "version": "2.0.0",
        "status": "running",
        "api_docs": "/docs",
        "api_base": "/api",
        "note": "Dashboard not found - serving API only"
    }


@app.get("/dashboard")
async def dashboard_page():
    """Serve the main dashboard"""
    return await serve_index()


@app.get("/dashboard/{path:path}")
async def dashboard_subpage(path: str):
    """Handle dashboard sub-routes"""
    path = path.strip("/")
    page_path = get_page_index(path)
    if page_path:
        return FileResponse(str(page_path))
    return await serve_index()


@app.get("/market")
async def market_page():
    page_path = get_page_index("market")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Market page not found"}


@app.get("/models")
async def models_page():
    page_path = get_page_index("models")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Models page not found"}


@app.get("/sentiment")
async def sentiment_page():
    page_path = get_page_index("sentiment")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Sentiment page not found"}


@app.get("/ai-analyst")
async def ai_analyst_page():
    page_path = get_page_index("ai-analyst")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "AI Analyst page not found"}


@app.get("/trading-assistant")
async def trading_assistant_page():
    page_path = get_page_index("trading-assistant")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Trading Assistant page not found"}


@app.get("/news")
async def news_page():
    page_path = get_page_index("news")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "News page not found"}


@app.get("/providers")
async def providers_page():
    page_path = get_page_index("providers")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Providers page not found"}


@app.get("/diagnostics")
async def diagnostics_page():
    page_path = get_page_index("diagnostics")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Diagnostics page not found"}


@app.get("/api-explorer")
async def api_explorer_page():
    page_path = get_page_index("api-explorer")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "API Explorer page not found"}


@app.get("/crypto-api-hub")
async def crypto_api_hub_page():
    page_path = get_page_index("crypto-api-hub")
    if page_path:
        return FileResponse(str(page_path))
    return {"error": "Crypto API Hub page not found"}


# Legacy routes
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
    admin_file = WORKSPACE_ROOT / "admin_improved.html"
    if admin_file.exists():
        return FileResponse(str(admin_file))
    admin_file = WORKSPACE_ROOT / "admin.html"
    if admin_file.exists():
        return FileResponse(str(admin_file))
    return {"error": "Admin page not found"}


@app.get("/api/pages")
async def list_pages():
    """List all available pages"""
    pages = []
    if PAGES_DIR.exists():
        for page_dir in PAGES_DIR.iterdir():
            if page_dir.is_dir() and (page_dir / "index.html").exists():
                pages.append({
                    "name": page_dir.name,
                    "route": f"/{page_dir.name}",
                    "dashboard_route": f"/dashboard/{page_dir.name}",
                })
    return {"total_pages": len(pages), "pages": pages}


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
