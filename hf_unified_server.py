#!/usr/bin/env python3
"""
Hugging Face Unified Server - Main FastAPI application entry point.
This module creates the unified API server with all service endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

# Import routers
from backend.routers.unified_service_api import router as service_router
from backend.routers.real_data_api import router as real_data_router

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

# Include routers
app.include_router(service_router)  # Main unified service
app.include_router(real_data_router, prefix="/real")  # Existing real data endpoints

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
        "service": "Unified Query Service API",
        "version": "1.0.0",
        "endpoints": {
            "rate": "/api/service/rate",
            "batch_rates": "/api/service/rate/batch",
            "pair_info": "/api/service/pair/{pair}",
            "sentiment": "/api/service/sentiment",
            "economic_analysis": "/api/service/econ-analysis",
            "history": "/api/service/history",
            "market_status": "/api/service/market-status",
            "top_coins": "/api/service/top",
            "whales": "/api/service/whales",
            "onchain": "/api/service/onchain",
            "generic_query": "/api/service/query",
            "websocket": "/ws",
            "docs": "/docs",
            "openapi": "/openapi.json"
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

logger.info("✅ Unified Service API Server initialized")

__all__ = ["app"]

