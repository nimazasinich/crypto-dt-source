#!/usr/bin/env python3
"""
Hugging Face Unified Server - Main FastAPI application entry point.
This module creates the unified API server with all service endpoints.
Multi-page architecture with HTTP polling (no WebSocket).
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
from datetime import datetime
import time

# Import routers
from backend.routers.unified_service_api import router as service_router
from backend.routers.real_data_api import router as real_data_router
from backend.routers.direct_api import router as direct_api_router
from backend.routers.crypto_api_hub_router import router as crypto_hub_router

# Import rate limiter
from utils.rate_limiter_simple import rate_limiter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Unified Query Service API",
    description="Single unified service for all cryptocurrency data needs",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Get client identifier (IP address)
    client_id = request.client.host if request.client else "unknown"
    
    # Determine endpoint type
    endpoint_type = "default"
    if "/hf/sentiment" in request.url.path:
        endpoint_type = "sentiment"
    elif "/hf/models/load" in request.url.path:
        endpoint_type = "model_loading"
    elif "/hf/datasets/load" in request.url.path:
        endpoint_type = "dataset_loading"
    elif any(api in request.url.path for api in ["/coingecko/", "/binance/", "/reddit/", "/rss/"]):
        endpoint_type = "external_api"
    
    # Check rate limit
    is_allowed, info = rate_limiter.is_allowed(client_id, endpoint_type)
    
    if not is_allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": f"Too many requests. Please try again in {int(info['retry_after'])} seconds.",
                "rate_limit_info": info
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["requests_remaining"])
    response.headers["X-RateLimit-Reset"] = str(int(info["reset_at"]))
    
    return response

# Include routers
app.include_router(service_router)  # Main unified service
app.include_router(real_data_router, prefix="/real")  # Existing real data endpoints
app.include_router(direct_api_router)  # NEW: Direct API with external services and HF models
app.include_router(crypto_hub_router)  # Crypto API Hub Dashboard API

# ============================================================================
# STATIC FILES
# ============================================================================
# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Base directory for pages
PAGES_DIR = Path("static/pages")

# ============================================================================
# PAGE ROUTES - Multi-page Architecture
# ============================================================================

def serve_page(page_name: str):
    """Helper function to serve page HTML"""
    page_path = PAGES_DIR / page_name / "index.html"
    if page_path.exists():
        return FileResponse(page_path)
    else:
        logger.error(f"Page not found: {page_name}")
        return HTMLResponse(
            content=f"<h1>404 - Page Not Found</h1><p>Page '{page_name}' does not exist.</p>",
            status_code=404
        )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """Dashboard page"""
    return serve_page("dashboard")

@app.get("/market", response_class=HTMLResponse)
async def market_page():
    """Market data page"""
    return serve_page("market")

@app.get("/models", response_class=HTMLResponse)
async def models_page():
    """AI Models page"""
    return serve_page("models")

@app.get("/sentiment", response_class=HTMLResponse)
async def sentiment_page():
    """Sentiment Analysis page"""
    return serve_page("sentiment")

@app.get("/ai-analyst", response_class=HTMLResponse)
async def ai_analyst_page():
    """AI Analyst page"""
    return serve_page("ai-analyst")

@app.get("/trading-assistant", response_class=HTMLResponse)
async def trading_assistant_page():
    """Trading Assistant page"""
    return serve_page("trading-assistant")

@app.get("/news", response_class=HTMLResponse)
async def news_page():
    """News page"""
    return serve_page("news")

@app.get("/providers", response_class=HTMLResponse)
async def providers_page():
    """Providers page"""
    return serve_page("providers")

@app.get("/diagnostics", response_class=HTMLResponse)
async def diagnostics_page():
    """Diagnostics page"""
    return serve_page("diagnostics")

@app.get("/api-explorer", response_class=HTMLResponse)
async def api_explorer_page():
    """API Explorer page"""
    return serve_page("api-explorer")

@app.get("/crypto-api-hub", response_class=HTMLResponse)
async def crypto_api_hub_page():
    """Crypto API Hub Dashboard page"""
    return serve_page("crypto-api-hub")

# ============================================================================
# API ENDPOINTS FOR FRONTEND
# ============================================================================

@app.get("/api/status")
async def api_status():
    """System status for dashboard"""
    return {
        "health": "healthy",
        "online": 15,
        "offline": 2,
        "degraded": 1,
        "avg_response_time": 245,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/api/resources")
async def api_resources():
    """Resource statistics for dashboard"""
    return {
        "total": 150,
        "free": 87,
        "models": 42,
        "providers": 18,
        "categories": [
            {"name": "Market Data", "count": 45},
            {"name": "Blockchain Explorers", "count": 30},
            {"name": "News Sources", "count": 25},
            {"name": "Sentiment APIs", "count": 20},
            {"name": "DeFi Protocols", "count": 15},
            {"name": "Whale Tracking", "count": 15}
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "unified_query_service",
        "version": "1.0.0"
    }

# Root endpoint - Serve Dashboard as home page
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - serves the dashboard page"""
    return serve_page("dashboard")

# API Root endpoint - Keep for backwards compatibility
@app.get("/api")
async def api_root():
    """API root endpoint with service information"""
    return {
        "service": "Unified Cryptocurrency Data API",
        "version": "2.0.0",
        "description": "Complete cryptocurrency data API with direct model loading and external API integration",
        "features": {
            "direct_model_loading": "NO PIPELINES - Direct HuggingFace model inference",
            "external_apis": "CoinGecko, Binance, Alternative.me, Reddit, RSS feeds",
            "datasets": "CryptoCoin, WinkingFace crypto datasets",
            "rate_limiting": "Enabled with per-endpoint limits",
            "real_time_data": "Market prices, news, sentiment, blockchain data",
            "multi_page_frontend": "10 separate pages with HTTP polling"
        },
        "pages": {
            "dashboard": "/",
            "market": "/market",
            "models": "/models",
            "sentiment": "/sentiment",
            "ai_analyst": "/ai-analyst",
            "trading_assistant": "/trading-assistant",
            "news": "/news",
            "providers": "/providers",
            "diagnostics": "/diagnostics",
            "api_explorer": "/api-explorer"
        },
        "endpoints": {
            "unified_service": {
                "rate": "/api/service/rate",
                "batch_rates": "/api/service/rate/batch",
                "pair_info": "/api/service/pair/{pair}",
                "sentiment": "/api/service/sentiment",
                "history": "/api/service/history",
                "market_status": "/api/service/market-status"
            },
            "direct_api": {
                "coingecko_price": "/api/v1/coingecko/price",
                "binance_klines": "/api/v1/binance/klines",
                "fear_greed": "/api/v1/alternative/fng",
                "reddit_top": "/api/v1/reddit/top",
                "rss_feeds": "/api/v1/rss/feed",
                "hf_sentiment": "/api/v1/hf/sentiment",
                "hf_models": "/api/v1/hf/models",
                "hf_datasets": "/api/v1/hf/datasets",
                "system_status": "/api/v1/status"
            },
            "documentation": {
                "swagger_ui": "/docs",
                "openapi_spec": "/openapi.json"
            }
        },
        "models_available": [
            "ElKulako/cryptobert",
            "kk08/CryptoBERT",
            "ProsusAI/finbert",
            "cardiffnlp/twitter-roberta-base-sentiment"
        ],
        "datasets_available": [
            "linxy/CryptoCoin",
            "WinkingFace/CryptoLM-Bitcoin-BTC-USDT",
            "WinkingFace/CryptoLM-Ethereum-ETH-USDT",
            "WinkingFace/CryptoLM-Solana-SOL-USDT",
            "WinkingFace/CryptoLM-Ripple-XRP-USDT"
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

logger.info("✅ Unified Service API Server initialized (Multi-page architecture, no WebSocket)")

__all__ = ["app"]

