"""
Alpha Vantage API Endpoints
Provides stock and crypto data from Alpha Vantage API
"""

import time
import logging
import os
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException

from api.hf_auth import verify_hf_token
from utils.logger import setup_logger

logger = setup_logger("alphavantage_endpoints")

router = APIRouter(prefix="/api/alphavantage", tags=["alphavantage"])


# Lazy import of provider
_provider_instance = None

def get_provider():
    """Get or create Alpha Vantage provider instance"""
    global _provider_instance
    if _provider_instance is None:
        try:
            from hf_data_engine.providers.alphavantage_provider import AlphaVantageProvider
            api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "40XS7GQ6AU9NB6Y4")
            _provider_instance = AlphaVantageProvider(api_key=api_key)
            logger.info("✅ Alpha Vantage provider initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Alpha Vantage provider: {e}")
            raise HTTPException(status_code=503, detail="Alpha Vantage provider not available")
    return _provider_instance


@router.get("/health")
async def alphavantage_health(auth: bool = Depends(verify_hf_token)):
    """Check Alpha Vantage provider health"""
    try:
        provider = get_provider()
        health = await provider.get_health()
        
        return {
            "success": True,
            "provider": "alphavantage",
            "status": health.status,
            "latency": health.latency,
            "last_check": health.lastCheck,
            "error": health.errorMessage,
            "timestamp": int(time.time() * 1000)
        }
    except Exception as e:
        logger.error(f"Alpha Vantage health check failed: {e}")
        return {
            "success": False,
            "provider": "alphavantage",
            "error": str(e),
            "timestamp": int(time.time() * 1000)
        }


@router.get("/prices")
async def get_crypto_prices(
    symbols: str = Query(..., description="Comma-separated crypto symbols (e.g., BTC,ETH,SOL)"),
    auth: bool = Depends(verify_hf_token)
):
    """
    Get real-time crypto prices from Alpha Vantage
    
    Args:
        symbols: Comma-separated list of crypto symbols (e.g., "BTC,ETH,SOL")
    
    Returns:
        JSON with current prices for requested symbols
    """
    try:
        provider = get_provider()
        
        # Parse symbols
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        logger.info(f"Fetching Alpha Vantage prices for: {symbol_list}")
        
        # Fetch prices
        prices = await provider.fetch_prices(symbol_list)
        
        return {
            "success": True,
            "source": "alphavantage",
            "count": len(prices),
            "prices": [
                {
                    "symbol": p.symbol,
                    "name": p.name,
                    "price": p.price,
                    "priceUsd": p.priceUsd,
                    "change24h": p.change24h,
                    "volume24h": p.volume24h,
                    "lastUpdate": p.lastUpdate
                }
                for p in prices
            ],
            "timestamp": int(time.time() * 1000)
        }
    
    except Exception as e:
        logger.error(f"Alpha Vantage price fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch prices from Alpha Vantage: {str(e)}"
        )


@router.get("/ohlcv")
async def get_ohlcv_data(
    symbol: str = Query(..., description="Crypto symbol (e.g., BTC, ETH)"),
    interval: str = Query("1h", description="Time interval (1m, 5m, 15m, 1h, 1d, 1w)"),
    limit: int = Query(100, ge=1, le=5000, description="Number of candles"),
    auth: bool = Depends(verify_hf_token)
):
    """
    Get OHLCV (candlestick) data from Alpha Vantage
    
    Args:
        symbol: Crypto symbol (e.g., BTC, ETH)
        interval: Time interval (1m, 5m, 15m, 1h, 1d, 1w)
        limit: Number of candles to return (max 5000)
    
    Returns:
        JSON with OHLCV data
    """
    try:
        provider = get_provider()
        
        logger.info(f"Fetching Alpha Vantage OHLCV: {symbol} {interval} x{limit}")
        
        # Fetch OHLCV data
        ohlcv_data = await provider.fetch_ohlcv(symbol, interval, limit)
        
        return {
            "success": True,
            "source": "alphavantage",
            "symbol": symbol.upper(),
            "interval": interval,
            "count": len(ohlcv_data),
            "data": [
                {
                    "timestamp": candle.timestamp,
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                    "volume": candle.volume
                }
                for candle in ohlcv_data
            ],
            "timestamp": int(time.time() * 1000)
        }
    
    except Exception as e:
        logger.error(f"Alpha Vantage OHLCV fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch OHLCV from Alpha Vantage: {str(e)}"
        )


@router.get("/market-status")
async def get_market_status(auth: bool = Depends(verify_hf_token)):
    """
    Get current market status from Alpha Vantage
    
    Returns:
        JSON with market status information
    """
    try:
        provider = get_provider()
        
        logger.info("Fetching Alpha Vantage market status")
        
        # Fetch market overview
        market_data = await provider.fetch_market_overview()
        
        return {
            "success": True,
            "source": "alphavantage",
            "data": market_data,
            "timestamp": int(time.time() * 1000)
        }
    
    except Exception as e:
        logger.error(f"Alpha Vantage market status fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch market status from Alpha Vantage: {str(e)}"
        )


@router.get("/crypto-rating/{symbol}")
async def get_crypto_rating(
    symbol: str,
    auth: bool = Depends(verify_hf_token)
):
    """
    Get crypto health rating from Alpha Vantage FCAS
    
    Args:
        symbol: Crypto symbol (e.g., BTC, ETH)
    
    Returns:
        JSON with crypto rating information
    """
    try:
        provider = get_provider()
        
        logger.info(f"Fetching Alpha Vantage crypto rating for: {symbol}")
        
        # Fetch crypto rating
        rating_data = await provider.fetch_crypto_rating(symbol)
        
        return {
            "success": True,
            "source": "alphavantage",
            "symbol": symbol.upper(),
            "rating": rating_data,
            "timestamp": int(time.time() * 1000)
        }
    
    except Exception as e:
        logger.error(f"Alpha Vantage crypto rating fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch crypto rating from Alpha Vantage: {str(e)}"
        )


@router.get("/quote/{symbol}")
async def get_global_quote(
    symbol: str,
    auth: bool = Depends(verify_hf_token)
):
    """
    Get global quote for a stock symbol from Alpha Vantage
    
    Args:
        symbol: Stock symbol (e.g., AAPL, TSLA)
    
    Returns:
        JSON with quote information
    """
    try:
        provider = get_provider()
        
        logger.info(f"Fetching Alpha Vantage global quote for: {symbol}")
        
        # Fetch global quote
        quote_data = await provider.fetch_global_quote(symbol)
        
        return {
            "success": True,
            "source": "alphavantage",
            "symbol": symbol.upper(),
            "quote": quote_data,
            "timestamp": int(time.time() * 1000)
        }
    
    except Exception as e:
        logger.error(f"Alpha Vantage global quote fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch quote from Alpha Vantage: {str(e)}"
        )
