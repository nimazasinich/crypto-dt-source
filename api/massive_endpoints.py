"""
Massive.com (APIBricks) API Endpoints
Provides comprehensive financial data from Massive.com API
"""

import time
import logging
import os
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException

from api.hf_auth import verify_hf_token
from utils.logger import setup_logger

logger = setup_logger("massive_endpoints")

router = APIRouter(prefix="/api/massive", tags=["massive"])


# Lazy import of provider
_provider_instance = None

def get_provider():
    """Get or create Massive provider instance"""
    global _provider_instance
    if _provider_instance is None:
        try:
            from hf_data_engine.providers.massive_provider import MassiveProvider
            api_key = os.getenv("MASSIVE_API_KEY", "PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE")
            _provider_instance = MassiveProvider(api_key=api_key)
            logger.info("✅ Massive.com provider initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Massive provider: {e}")
            raise HTTPException(status_code=503, detail="Massive provider not available")
    return _provider_instance


@router.get("/health")
async def massive_health(auth: bool = Depends(verify_hf_token)):
    """Check Massive.com provider health"""
    try:
        provider = get_provider()
        health = await provider.get_health()
        
        return {
            "success": True,
            "provider": "massive",
            "status": health.status,
            "latency": health.latency,
            "last_check": health.lastCheck,
            "error": health.errorMessage,
            "timestamp": int(time.time() * 1000)
        }
    except Exception as e:
        logger.error(f"Massive health check failed: {e}")
        return {
            "success": False,
            "provider": "massive",
            "error": str(e),
            "timestamp": int(time.time() * 1000)
        }


@router.get("/dividends")
async def get_dividends(
    ticker: Optional[str] = Query(None, description="Stock ticker (e.g., AAPL)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records"),
    auth: bool = Depends(verify_hf_token)
):
    """
    Get dividend records from Massive.com API
    
    Example response for AAPL:
    {
      "ticker": "AAPL",
      "cash_amount": 0.25,
      "currency": "USD",
      "declaration_date": "2024-10-31",
      "ex_dividend_date": "2024-11-08",
      "pay_date": "2024-11-14",
      "record_date": "2024-11-11",
      "dividend_type": "CD",
      "frequency": 4
    }
    
    Args:
        ticker: Optional stock ticker to filter
        limit: Number of records to return
    
    Returns:
        JSON with dividend records
    """
    try:
        provider = get_provider()
        
        logger.info(f"Fetching Massive dividends: ticker={ticker}, limit={limit}")
        
        # Fetch dividends
        dividends = await provider.fetch_dividends(ticker=ticker, limit=limit)
        
        return {
            "success": True,
            "source": "massive",
            "count": len(dividends),
            "results": dividends,
            "timestamp": int(time.time() * 1000)
        }
    
    except Exception as e:
        logger.error(f"Massive dividends fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch dividends from Massive: {str(e)}"
        )


@router.get("/splits")
async def get_splits(
    ticker: Optional[str] = Query(None, description="Stock ticker (e.g., AAPL)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records"),
    auth: bool = Depends(verify_hf_token)
):
    """
    Get stock split records from Massive.com API
    
    Args:
        ticker: Optional stock ticker to filter
        limit: Number of records to return
    
    Returns:
        JSON with stock split records
    """
    try:
        provider = get_provider()
        
        logger.info(f"Fetching Massive splits: ticker={ticker}, limit={limit}")
        
        # Fetch splits
        splits = await provider.fetch_splits(ticker=ticker, limit=limit)
        
        return {
            "success": True,
            "source": "massive",
            "count": len(splits),
            "results": splits,
            "timestamp": int(time.time() * 1000)
        }
    
    except Exception as e:
        logger.error(f"Massive splits fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch splits from Massive: {str(e)}"
        )


@router.get("/quotes/{ticker}")
async def get_quotes(
    ticker: str,
    auth: bool = Depends(verify_hf_token)
):
    """
    Get real-time quotes for a ticker from Massive.com API
    
    Args:
        ticker: Stock ticker (e.g., AAPL, TSLA)
    
    Returns:
        JSON with quote data
    """
    try:
        provider = get_provider()
        
        logger.info(f"Fetching Massive quote for: {ticker}")
        
        # Fetch prices (which uses quotes endpoint)
        prices = await provider.fetch_prices([ticker])
        
        if not prices:
            raise HTTPException(status_code=404, detail=f"No quote found for {ticker}")
        
        price = prices[0]
        
        return {
            "success": True,
            "source": "massive",
            "ticker": ticker.upper(),
            "price": price.price,
            "volume": price.volume24h,
            "lastUpdate": price.lastUpdate,
            "timestamp": int(time.time() * 1000)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Massive quote fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch quote from Massive: {str(e)}"
        )


@router.get("/trades/{ticker}")
async def get_trades(
    ticker: str,
    limit: int = Query(100, ge=1, le=5000, description="Number of trades"),
    auth: bool = Depends(verify_hf_token)
):
    """
    Get recent trades for a ticker from Massive.com API
    
    Args:
        ticker: Stock ticker (e.g., AAPL, TSLA)
        limit: Number of trades to return
    
    Returns:
        JSON with trade data
    """
    try:
        provider = get_provider()
        
        logger.info(f"Fetching Massive trades: {ticker} x{limit}")
        
        # Fetch trades
        trades = await provider.fetch_trades(ticker, limit=limit)
        
        return {
            "success": True,
            "source": "massive",
            "ticker": ticker.upper(),
            "count": len(trades),
            "trades": trades,
            "timestamp": int(time.time() * 1000)
        }
    
    except Exception as e:
        logger.error(f"Massive trades fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch trades from Massive: {str(e)}"
        )


@router.get("/aggregates/{ticker}")
async def get_aggregates(
    ticker: str,
    interval: str = Query("1h", description="Time interval (1m, 5m, 15m, 1h, 4h, 1d, 1w)"),
    limit: int = Query(100, ge=1, le=5000, description="Number of candles"),
    auth: bool = Depends(verify_hf_token)
):
    """
    Get OHLCV aggregates (candlestick data) from Massive.com API
    
    Args:
        ticker: Stock ticker (e.g., AAPL, TSLA)
        interval: Time interval (1m, 5m, 15m, 1h, 4h, 1d, 1w)
        limit: Number of candles to return
    
    Returns:
        JSON with OHLCV data
    """
    try:
        provider = get_provider()
        
        logger.info(f"Fetching Massive aggregates: {ticker} {interval} x{limit}")
        
        # Fetch OHLCV data
        ohlcv_data = await provider.fetch_ohlcv(ticker, interval, limit)
        
        return {
            "success": True,
            "source": "massive",
            "ticker": ticker.upper(),
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
        logger.error(f"Massive aggregates fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch aggregates from Massive: {str(e)}"
        )


@router.get("/ticker/{ticker}")
async def get_ticker_details(
    ticker: str,
    auth: bool = Depends(verify_hf_token)
):
    """
    Get detailed information about a ticker from Massive.com API
    
    Args:
        ticker: Stock ticker (e.g., AAPL, TSLA)
    
    Returns:
        JSON with ticker details
    """
    try:
        provider = get_provider()
        
        logger.info(f"Fetching Massive ticker details for: {ticker}")
        
        # Fetch ticker details
        details = await provider.fetch_ticker_details(ticker)
        
        return {
            "success": True,
            "source": "massive",
            "ticker": ticker.upper(),
            "details": details,
            "timestamp": int(time.time() * 1000)
        }
    
    except Exception as e:
        logger.error(f"Massive ticker details fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch ticker details from Massive: {str(e)}"
        )


@router.get("/market-status")
async def get_market_status(auth: bool = Depends(verify_hf_token)):
    """
    Get current market status from Massive.com API
    
    Returns:
        JSON with market status information
    """
    try:
        provider = get_provider()
        
        logger.info("Fetching Massive market status")
        
        # Fetch market status
        status_data = await provider.fetch_market_status()
        
        return {
            "success": True,
            "source": "massive",
            "data": status_data,
            "timestamp": int(time.time() * 1000)
        }
    
    except Exception as e:
        logger.error(f"Massive market status fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch market status from Massive: {str(e)}"
        )
