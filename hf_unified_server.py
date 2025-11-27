#!/usr/bin/env python3
"""
Hugging Face Unified Server - Main FastAPI application entry point.
This module creates the unified API server with all service endpoints.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import time

# Import routers
from backend.routers.unified_service_api import router as service_router
from backend.routers.real_data_api import router as real_data_router
from backend.routers.direct_api import router as direct_api_router

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

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Unified Cryptocurrency Data API",
        "version": "2.0.0",
        "description": "Complete cryptocurrency data API with direct model loading and external API integration",
        "features": {
            "direct_model_loading": "NO PIPELINES - Direct HuggingFace model inference",
            "external_apis": "CoinGecko, Binance, Alternative.me, Reddit, RSS feeds",
            "datasets": "CryptoCoin, WinkingFace crypto datasets",
            "rate_limiting": "Enabled with per-endpoint limits",
            "real_time_data": "Market prices, news, sentiment, blockchain data"
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

logger.info("✅ Unified Service API Server initialized")

__all__ = ["app"]

