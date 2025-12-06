#!/usr/bin/env python3
"""
Trading & Backtesting API Router
Smart exchange integration for trading and backtesting
Binance & KuCoin with advanced features
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import logging

from backend.services.trading_backtesting_service import (
    get_trading_service,
    get_backtesting_service
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trading", tags=["Trading & Backtesting"])


# ========== Trading Endpoints ==========

@router.get("/price/{symbol}")
async def get_trading_price(
    symbol: str,
    exchange: str = Query("binance", description="Exchange (binance/kucoin)"),
    enable_proxy: bool = Query(False, description="Enable proxy for geo-restricted access"),
    use_fallback: bool = Query(True, description="Use multi-source fallback if primary fails")
):
    """
    Get current trading price from smart exchange client
    
    **Features:**
    - Smart routing with geo-block bypass
    - DNS over HTTPS (DoH)
    - Multi-layer proxies (optional)
    - Auto-fallback to multi-source system
    
    **Exchanges:**
    - `binance`: Symbol format: BTCUSDT, ETHUSDT, etc.
    - `kucoin`: Symbol format: BTC-USDT, ETH-USDT, etc.
    
    **Example:**
    ```
    GET /api/trading/price/BTCUSDT?exchange=binance
    GET /api/trading/price/BTC-USDT?exchange=kucoin&enable_proxy=true
    ```
    """
    try:
        service = get_trading_service(enable_proxy=enable_proxy)
        
        result = await service.get_trading_price(
            symbol=symbol,
            exchange=exchange,
            use_fallback=use_fallback
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to get price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ohlcv/{symbol}")
async def get_trading_ohlcv(
    symbol: str,
    timeframe: str = Query("1h", description="Timeframe (1m, 5m, 15m, 1h, 4h, 1d, etc.)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles"),
    exchange: str = Query("binance", description="Exchange (binance/kucoin)"),
    start_time: Optional[int] = Query(None, description="Start timestamp (milliseconds)"),
    end_time: Optional[int] = Query(None, description="End timestamp (milliseconds)"),
    enable_proxy: bool = Query(False, description="Enable proxy")
):
    """
    Get OHLCV candlestick data for trading/backtesting
    
    **Features:**
    - Up to 1000 candles per request
    - Smart client with geo-block bypass
    - Historical data with timestamps
    
    **Timeframes:**
    - Binance: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
    - KuCoin: 1min, 3min, 5min, 15min, 30min, 1hour, 2hour, 4hour, 6hour, 8hour, 12hour, 1day, 1week
    
    **Response:**
    ```json
    {
      "success": true,
      "exchange": "binance",
      "symbol": "BTCUSDT",
      "timeframe": "1h",
      "candles": [
        {
          "timestamp": 1733491200000,
          "open": 43200.00,
          "high": 43300.00,
          "low": 43150.00,
          "close": 43250.50,
          "volume": 1234.56
        }
      ],
      "count": 100
    }
    ```
    """
    try:
        service = get_trading_service(enable_proxy=enable_proxy)
        
        result = await service.get_trading_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
            exchange=exchange,
            start_time=start_time,
            end_time=end_time
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to get OHLCV for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orderbook/{symbol}")
async def get_orderbook(
    symbol: str,
    exchange: str = Query("binance", description="Exchange (binance/kucoin)"),
    limit: int = Query(100, ge=1, le=5000, description="Depth limit"),
    enable_proxy: bool = Query(False, description="Enable proxy")
):
    """
    Get order book for trading
    
    **Features:**
    - Real-time bid/ask prices
    - Market depth analysis
    - Up to 5000 levels (Binance)
    
    **Response:**
    ```json
    {
      "success": true,
      "exchange": "binance",
      "symbol": "BTCUSDT",
      "bids": [
        [43250.50, 1.234],
        [43249.00, 0.567]
      ],
      "asks": [
        [43251.00, 0.890],
        [43252.50, 1.456]
      ]
    }
    ```
    """
    try:
        service = get_trading_service(enable_proxy=enable_proxy)
        
        result = await service.get_orderbook(
            symbol=symbol,
            exchange=exchange,
            limit=limit
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to get orderbook for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/24h/{symbol}")
async def get_24h_stats(
    symbol: str,
    exchange: str = Query("binance", description="Exchange (binance/kucoin)"),
    enable_proxy: bool = Query(False, description="Enable proxy")
):
    """
    Get 24-hour trading statistics
    
    **Metrics:**
    - Current price
    - 24h change (amount and percentage)
    - 24h high/low
    - 24h volume
    - Number of trades (Binance only)
    
    **Example:**
    ```
    GET /api/trading/stats/24h/BTCUSDT?exchange=binance
    ```
    
    **Response:**
    ```json
    {
      "success": true,
      "exchange": "binance",
      "symbol": "BTCUSDT",
      "price": 43250.50,
      "change": 850.25,
      "change_percent": 2.01,
      "high": 43500.00,
      "low": 42800.00,
      "volume": 12345.67,
      "trades": 987654
    }
    ```
    """
    try:
        service = get_trading_service(enable_proxy=enable_proxy)
        
        result = await service.get_24h_stats(
            symbol=symbol,
            exchange=exchange
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to get 24h stats for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== Backtesting Endpoints ==========

@router.get("/backtest/historical/{symbol}")
async def fetch_historical_data(
    symbol: str,
    timeframe: str = Query("1h", description="Timeframe"),
    days: int = Query(30, ge=1, le=365, description="Days of historical data"),
    exchange: str = Query("binance", description="Exchange (binance/kucoin)"),
    enable_proxy: bool = Query(False, description="Enable proxy")
):
    """
    Fetch historical data for backtesting
    
    **Features:**
    - Automatic chunking for large datasets
    - Up to 365 days of historical data
    - Returns DataFrame-ready format
    
    **Note:** This may take some time for large datasets due to API rate limits.
    
    **Example:**
    ```
    GET /api/trading/backtest/historical/BTCUSDT?timeframe=1h&days=30
    ```
    
    **Response:**
    ```json
    {
      "success": true,
      "symbol": "BTCUSDT",
      "exchange": "binance",
      "timeframe": "1h",
      "days": 30,
      "candles": [...],
      "count": 720
    }
    ```
    """
    try:
        service = get_trading_service(enable_proxy=enable_proxy)
        backtest_service = get_backtesting_service()
        
        df = await backtest_service.fetch_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            days=days,
            exchange=exchange
        )
        
        if df.empty:
            return {
                "success": False,
                "error": "No historical data available",
                "symbol": symbol,
                "exchange": exchange
            }
        
        # Convert DataFrame to dict
        df_reset = df.reset_index()
        candles = df_reset.to_dict('records')
        
        return {
            "success": True,
            "symbol": symbol,
            "exchange": exchange,
            "timeframe": timeframe,
            "days": days,
            "candles": candles,
            "count": len(candles)
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtest/run/{symbol}")
async def run_backtest(
    symbol: str,
    strategy: str = Query(..., description="Strategy name (sma_crossover, rsi, macd)"),
    timeframe: str = Query("1h", description="Timeframe"),
    days: int = Query(30, ge=1, le=365, description="Historical data period"),
    exchange: str = Query("binance", description="Exchange (binance/kucoin)"),
    initial_capital: float = Query(10000.0, ge=100, description="Initial capital"),
    enable_proxy: bool = Query(False, description="Enable proxy")
):
    """
    Run backtesting with a trading strategy
    
    **Available Strategies:**
    
    1. **sma_crossover**: Simple Moving Average Crossover
       - Buy when fast SMA (10) crosses above slow SMA (30)
       - Sell when fast SMA crosses below slow SMA
    
    2. **rsi**: Relative Strength Index
       - Buy when RSI < 30 (oversold)
       - Sell when RSI > 70 (overbought)
    
    3. **macd**: Moving Average Convergence Divergence
       - Buy when MACD crosses above signal line
       - Sell when MACD crosses below signal line
    
    **Example:**
    ```
    GET /api/trading/backtest/run/BTCUSDT?strategy=sma_crossover&days=30&initial_capital=10000
    ```
    
    **Response:**
    ```json
    {
      "success": true,
      "symbol": "BTCUSDT",
      "exchange": "binance",
      "strategy": "sma_crossover",
      "timeframe": "1h",
      "days": 30,
      "initial_capital": 10000.0,
      "final_capital": 10567.89,
      "profit": 567.89,
      "total_return": 5.68,
      "trades": 12,
      "candles_analyzed": 720
    }
    ```
    """
    try:
        backtest_service = get_backtesting_service()
        
        result = await backtest_service.run_backtest(
            symbol=symbol,
            strategy=strategy,
            timeframe=timeframe,
            days=days,
            exchange=exchange,
            initial_capital=initial_capital
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Failed to run backtest for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exchanges/status")
async def get_exchanges_status(
    enable_proxy: bool = Query(False, description="Enable proxy")
):
    """
    Get status of smart exchange clients
    
    **Features:**
    - Test connection to Binance and KuCoin
    - Show proxy status
    - Show DoH status
    
    **Response:**
    ```json
    {
      "success": true,
      "exchanges": {
        "binance": {
          "available": true,
          "endpoints": 5,
          "proxy_enabled": false,
          "doh_enabled": true
        },
        "kucoin": {
          "available": true,
          "endpoints": 2,
          "proxy_enabled": false,
          "doh_enabled": true
        }
      }
    }
    ```
    """
    try:
        service = get_trading_service(enable_proxy=enable_proxy)
        
        # Test Binance
        binance_available = False
        try:
            await service.binance.ping()
            binance_available = True
        except:
            pass
        
        # Test KuCoin
        kucoin_available = False
        try:
            await service.kucoin.get_ticker_price("BTC-USDT")
            kucoin_available = True
        except:
            pass
        
        return {
            "success": True,
            "exchanges": {
                "binance": {
                    "available": binance_available,
                    "endpoints": len(service.binance.endpoints),
                    "current_endpoint": service.binance.endpoints[service.binance.current_endpoint_index],
                    "proxy_enabled": service.binance.enable_proxy,
                    "doh_enabled": service.binance.enable_doh
                },
                "kucoin": {
                    "available": kucoin_available,
                    "endpoints": len(service.kucoin.endpoints),
                    "current_endpoint": service.kucoin.endpoints[service.kucoin.current_endpoint_index],
                    "proxy_enabled": service.kucoin.enable_proxy,
                    "doh_enabled": service.kucoin.enable_doh
                }
            },
            "timestamp": "2025-12-06T00:00:00Z"
        }
    
    except Exception as e:
        logger.error(f"Failed to get exchanges status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
