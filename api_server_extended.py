#!/usr/bin/env python3
"""
API Server Extended - HuggingFace Spaces Deployment
Real data endpoints - NO MOCKS
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import os

# Import real data fetchers
from provider_fetch_helper import (
    fetch_coingecko_market_data,
    fetch_fear_greed_index,
    fetch_trending_coins,
    get_market_history,
    fetch_market_stats
)
from db_helper import get_database

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Crypto Monitor API",
    description="Real-time cryptocurrency data API for HuggingFace Spaces",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Startup/Shutdown Events =====

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("🚀 Starting Crypto Monitor API...")
    logger.info(f"Port: {os.getenv('PORT', '7860')}")
    logger.info(f"Mock Data: {os.getenv('USE_MOCK_DATA', 'false')}")
    
    # Initialize database
    try:
        db = get_database()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    logger.info("✅ API Server ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down API Server...")


# ===== Health Check =====

@app.get("/health")
async def health():
    """
    Health check endpoint
    Returns 200 if service is operational
    """
    try:
        db = get_database()
        stats = db.get_database_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "connected": True,
                "records": stats.get("prices_count", 0)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


# ===== Market Data Endpoint =====

@app.get("/api/market")
async def get_market_data():
    """
    Get REAL market data from CoinGecko
    Uses real API - NO MOCK DATA
    """
    try:
        data = await fetch_coingecko_market_data()
        return data
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch market data: {str(e)}"
        )


# ===== Market Statistics Endpoint =====

@app.get("/api/stats")
async def get_market_stats():
    """
    Get REAL market statistics from CoinGecko
    """
    try:
        data = await fetch_market_stats()
        return data
    except Exception as e:
        logger.error(f"Error fetching market stats: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch market stats: {str(e)}"
        )


# ===== Sentiment Endpoint =====

@app.get("/api/sentiment")
async def get_sentiment():
    """
    Get REAL Fear & Greed Index from Alternative.me
    Uses real API - NO MOCK - Returns 503 on failure
    """
    try:
        data = await fetch_fear_greed_index()
        return data
    except Exception as e:
        logger.error(f"Error fetching sentiment: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch Fear & Greed Index: {str(e)}"
        )


# ===== Trending Endpoint =====

@app.get("/api/trending")
async def get_trending():
    """
    Get REAL trending coins from CoinGecko
    Uses real API with strict validation
    """
    try:
        data = await fetch_trending_coins()
        
        # Strict validation
        if not data.get("trending"):
            raise ValueError("No trending data available")
        
        return data
    except Exception as e:
        logger.error(f"Error fetching trending: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch trending coins: {str(e)}"
        )


# ===== Market History Endpoint =====

@app.get("/api/market/history")
async def get_market_history_endpoint(
    symbol: str = "BTC",
    hours: int = 24
):
    """
    Get REAL market history from SQLite database
    """
    try:
        data = get_market_history(symbol=symbol.upper(), hours=hours)
        return data
    except Exception as e:
        logger.error(f"Error fetching market history: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch market history: {str(e)}"
        )


# ===== DeFi Endpoint (Not Implemented) =====

@app.get("/api/defi")
async def get_defi():
    """
    DeFi endpoint - NOT IMPLEMENTED
    Returns 503 as specified
    """
    raise HTTPException(
        status_code=503,
        detail="DeFi endpoint not implemented"
    )


# ===== HuggingFace Health Endpoint =====

@app.get("/api/hf/health")
async def hf_health():
    """
    HuggingFace service health check
    """
    return {
        "status": "operational",
        "models_available": 0,
        "timestamp": datetime.now().isoformat()
    }


# ===== HuggingFace Sentiment Analysis (Not Implemented) =====

@app.post("/api/hf/run-sentiment")
async def run_sentiment(data: Dict[str, Any]):
    """
    ML sentiment analysis - NOT IMPLEMENTED
    Returns 501 as specified
    """
    raise HTTPException(
        status_code=501,
        detail="ML sentiment not implemented"
    )


# ===== Root Endpoint =====

@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": "Crypto Monitor API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "/health": "Health check",
            "/api/market": "Real market data (CoinGecko)",
            "/api/sentiment": "Real Fear & Greed Index (Alternative.me)",
            "/api/trending": "Real trending coins (CoinGecko)",
            "/api/market/history": "Market history (SQLite)",
            "/api/stats": "Market statistics (CoinGecko)",
            "/api/defi": "503 - Not implemented",
            "/api/hf/run-sentiment": "501 - Not implemented"
        },
        "timestamp": datetime.now().isoformat()
    }


# ===== Main =====

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "7860"))
    
    logger.info(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║   🚀 Crypto Monitor API Server (HuggingFace)             ║
    ║   Version: 1.0.0                                          ║
    ║   Port: {port}                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
