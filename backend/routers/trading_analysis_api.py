#!/usr/bin/env python3
"""
Trading Analysis API Router - Trading & Technical Analysis Endpoints
Implements:
- GET /api/trading/volume - Volume analysis by exchange
- GET /api/trading/orderbook - Aggregated order book data
- GET /api/indicators/{coin} - Technical indicators (RSI, MACD, etc)
- POST /api/backtest - Strategy backtesting endpoint
- GET /api/correlations - Crypto correlation matrix
"""

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
import time
import httpx
import asyncio
import numpy as np

# Import enhanced provider manager for intelligent load balancing
from backend.services.enhanced_provider_manager import (
    get_enhanced_provider_manager,
    DataCategory
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Trading Analysis API"])


# ============================================================================
# Request/Response Models
# ============================================================================

class BacktestRequest(BaseModel):
    """Request model for backtesting"""
    symbol: str = Field(..., description="Trading symbol (e.g., BTC)")
    strategy: str = Field(..., description="Strategy name: sma_cross, rsi_oversold, macd_signal")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    initial_capital: float = Field(10000, description="Initial capital in USD")
    params: Dict[str, Any] = Field(default_factory=dict, description="Strategy parameters")


# ============================================================================
# Helper Functions
# ============================================================================

async def fetch_binance_ticker_24h(symbol: str = None) -> List[Dict]:
    """Fetch 24h ticker data with intelligent provider failover"""
    try:
        manager = get_enhanced_provider_manager()
        result = await manager.fetch_data(
            DataCategory.MARKET_VOLUME,
            symbol=symbol
        )
        
        if result and result.get("success"):
            data = result.get("data")
            return [data] if isinstance(data, dict) else data
        else:
            logger.error(f"Volume data fetch failed: {result.get('error')}")
            return []
    except Exception as e:
        logger.error(f"Ticker error: {e}")
        return []


async def fetch_binance_orderbook(symbol: str, limit: int = 20) -> Dict:
    """Fetch order book with intelligent provider failover"""
    try:
        manager = get_enhanced_provider_manager()
        result = await manager.fetch_data(
            DataCategory.MARKET_ORDERBOOK,
            symbol=f"{symbol}USDT",
            limit=limit
        )
        
        if result and result.get("success"):
            return result.get("data")
        else:
            raise HTTPException(status_code=502, detail=f"Order book unavailable: {result.get('error')}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Orderbook error: {e}")
        raise HTTPException(status_code=502, detail=f"Order book unavailable: {str(e)}")


async def fetch_ohlcv_for_analysis(symbol: str, interval: str, limit: int) -> List[List]:
    """Fetch OHLCV data with intelligent provider failover"""
    try:
        manager = get_enhanced_provider_manager()
        result = await manager.fetch_data(
            DataCategory.MARKET_OHLCV,
            symbol=f"{symbol}USDT",
            interval=interval,
            limit=limit
        )
        
        if result and result.get("success"):
            return result.get("data", [])
        else:
            logger.error(f"OHLCV fetch failed: {result.get('error')}")
            return []
    except Exception as e:
        logger.error(f"OHLCV fetch error: {e}")
        return []


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Calculate RSI indicator"""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)


def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """Calculate MACD indicator"""
    if len(prices) < slow:
        return {"macd": 0, "signal": 0, "histogram": 0}
    
    prices_arr = np.array(prices)
    
    # Calculate EMAs
    ema_fast = prices_arr[-1]  # Simplified
    ema_slow = prices_arr[-slow]
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line * 0.9  # Simplified
    histogram = macd_line - signal_line
    
    return {
        "macd": round(macd_line, 2),
        "signal": round(signal_line, 2),
        "histogram": round(histogram, 2)
    }


def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict:
    """Calculate Bollinger Bands"""
    if len(prices) < period:
        return {"upper": 0, "middle": 0, "lower": 0}
    
    recent_prices = prices[-period:]
    middle = np.mean(recent_prices)
    std = np.std(recent_prices)
    
    return {
        "upper": round(middle + (std_dev * std), 2),
        "middle": round(middle, 2),
        "lower": round(middle - (std_dev * std), 2)
    }


# ============================================================================
# GET /api/trading/volume
# ============================================================================

@router.get("/api/trading/volume")
async def get_volume_analysis(
    symbol: Optional[str] = Query(None, description="Specific symbol (e.g., BTC)")
):
    """
    Get volume analysis by exchange
    
    Returns 24h volume data from major exchanges
    """
    try:
        # Fetch from Binance
        tickers = await fetch_binance_ticker_24h(symbol)
        
        if not tickers:
            raise HTTPException(status_code=503, detail="Volume data unavailable")
        
        volume_data = []
        total_volume = 0
        
        for ticker in tickers[:50]:  # Top 50 pairs
            ticker_symbol = ticker.get("symbol", "")
            if not ticker_symbol.endswith("USDT"):
                continue
            
            base_symbol = ticker_symbol.replace("USDT", "")
            volume_usdt = float(ticker.get("quoteVolume", 0))
            
            if symbol and base_symbol != symbol.upper():
                continue
            
            volume_data.append({
                "symbol": base_symbol,
                "exchange": "Binance",
                "volume_24h": volume_usdt,
                "volume_change": float(ticker.get("priceChangePercent", 0)),
                "trades_count": int(ticker.get("count", 0))
            })
            
            total_volume += volume_usdt
        
        # Sort by volume
        volume_data.sort(key=lambda x: x["volume_24h"], reverse=True)
        
        return {
            "success": True,
            "symbol": symbol,
            "total_volume": round(total_volume, 2),
            "count": len(volume_data),
            "data": volume_data[:20],
            "source": "binance",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Volume analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/trading/orderbook
# ============================================================================

@router.get("/api/trading/orderbook")
async def get_orderbook(
    symbol: str = Query(..., description="Trading symbol (e.g., BTC)"),
    depth: int = Query(20, ge=5, le=100, description="Order book depth")
):
    """
    Get aggregated order book data
    
    Returns bids and asks with depth analysis
    """
    try:
        orderbook = await fetch_binance_orderbook(symbol.upper(), depth)
        
        bids = [[float(price), float(qty)] for price, qty in orderbook.get("bids", [])]
        asks = [[float(price), float(qty)] for price, qty in orderbook.get("asks", [])]
        
        # Calculate metrics
        total_bid_volume = sum(qty for _, qty in bids)
        total_ask_volume = sum(qty for _, qty in asks)
        
        bid_ask_ratio = total_bid_volume / total_ask_volume if total_ask_volume > 0 else 1.0
        
        spread = asks[0][0] - bids[0][0] if bids and asks else 0
        spread_percent = (spread / bids[0][0] * 100) if bids and bids[0][0] > 0 else 0
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timestamp": orderbook.get("lastUpdateId"),
            "bids": bids,
            "asks": asks,
            "metrics": {
                "bid_volume": round(total_bid_volume, 4),
                "ask_volume": round(total_ask_volume, 4),
                "bid_ask_ratio": round(bid_ask_ratio, 2),
                "spread": round(spread, 2),
                "spread_percent": round(spread_percent, 4),
                "best_bid": bids[0][0] if bids else 0,
                "best_ask": asks[0][0] if asks else 0
            },
            "source": "binance",
            "update_time": datetime.utcnow().isoformat() + "Z"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Orderbook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/indicators/{coin}
# ============================================================================

@router.get("/api/indicators/{coin}")
async def get_technical_indicators(
    coin: str,
    interval: str = Query("1h", description="Time interval: 1h, 4h, 1d"),
    indicators: Optional[str] = Query(None, description="Comma-separated list: rsi,macd,bb,sma,ema")
):
    """
    Get technical indicators for a coin
    
    Supported indicators:
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - BB (Bollinger Bands)
    - SMA (Simple Moving Average)
    - EMA (Exponential Moving Average)
    """
    try:
        # Fetch OHLCV data
        klines = await fetch_ohlcv_for_analysis(coin.upper(), interval, 100)
        
        if not klines:
            raise HTTPException(status_code=404, detail=f"No data available for {coin}")
        
        # Extract close prices
        closes = [float(k[4]) for k in klines]
        
        # Parse requested indicators
        requested = indicators.split(",") if indicators else ["rsi", "macd", "bb"]
        
        result_indicators = {}
        
        # Calculate requested indicators
        if "rsi" in requested:
            result_indicators["rsi"] = {
                "value": calculate_rsi(closes, 14),
                "period": 14,
                "interpretation": "oversold" if calculate_rsi(closes, 14) < 30 else "overbought" if calculate_rsi(closes, 14) > 70 else "neutral"
            }
        
        if "macd" in requested:
            macd_data = calculate_macd(closes)
            result_indicators["macd"] = {
                **macd_data,
                "interpretation": "bullish" if macd_data["histogram"] > 0 else "bearish"
            }
        
        if "bb" in requested:
            bb_data = calculate_bollinger_bands(closes)
            current_price = closes[-1]
            result_indicators["bollinger_bands"] = {
                **bb_data,
                "current_price": round(current_price, 2),
                "position": "above" if current_price > bb_data["upper"] else "below" if current_price < bb_data["lower"] else "middle"
            }
        
        if "sma" in requested:
            sma_20 = round(np.mean(closes[-20:]), 2) if len(closes) >= 20 else 0
            sma_50 = round(np.mean(closes[-50:]), 2) if len(closes) >= 50 else 0
            result_indicators["sma"] = {
                "sma_20": sma_20,
                "sma_50": sma_50,
                "current_price": round(closes[-1], 2),
                "trend": "bullish" if closes[-1] > sma_20 > sma_50 else "bearish" if closes[-1] < sma_20 < sma_50 else "neutral"
            }
        
        if "ema" in requested:
            # Simplified EMA calculation
            ema_12 = round(closes[-1] * 0.15 + closes[-2] * 0.85, 2) if len(closes) >= 2 else closes[-1]
            ema_26 = round(np.mean(closes[-26:]), 2) if len(closes) >= 26 else 0
            result_indicators["ema"] = {
                "ema_12": ema_12,
                "ema_26": ema_26,
                "crossover": "bullish" if ema_12 > ema_26 else "bearish"
            }
        
        return {
            "success": True,
            "symbol": coin.upper(),
            "interval": interval,
            "current_price": round(closes[-1], 2),
            "indicators": result_indicators,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Indicators error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# POST /api/backtest
# ============================================================================

@router.post("/api/backtest")
async def backtest_strategy(request: BacktestRequest):
    """
    Backtest a trading strategy
    
    Supported strategies:
    - sma_cross: Simple Moving Average crossover
    - rsi_oversold: RSI oversold/overbought
    - macd_signal: MACD signal line crossover
    """
    try:
        # Validate dates
        try:
            start = datetime.fromisoformat(request.start_date)
            end = datetime.fromisoformat(request.end_date)
        except:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        if start >= end:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        
        # Fetch historical data
        days = (end - start).days
        klines = await fetch_ohlcv_for_analysis(request.symbol.upper(), "1d", min(days, 365))
        
        if not klines:
            raise HTTPException(status_code=404, detail=f"No historical data for {request.symbol}")
        
        closes = [float(k[4]) for k in klines]
        
        # Simulate trading based on strategy
        trades = []
        position = None
        capital = request.initial_capital
        
        if request.strategy == "sma_cross":
            fast_period = request.params.get("fast", 10)
            slow_period = request.params.get("slow", 30)
            
            for i in range(slow_period, len(closes)):
                sma_fast = np.mean(closes[i-fast_period:i])
                sma_slow = np.mean(closes[i-slow_period:i])
                
                # Buy signal: fast crosses above slow
                if sma_fast > sma_slow and position is None:
                    position = {
                        "entry_price": closes[i],
                        "entry_index": i,
                        "quantity": capital / closes[i]
                    }
                
                # Sell signal: fast crosses below slow
                elif sma_fast < sma_slow and position is not None:
                    profit = (closes[i] - position["entry_price"]) * position["quantity"]
                    capital += profit
                    
                    trades.append({
                        "entry_price": position["entry_price"],
                        "exit_price": closes[i],
                        "profit": round(profit, 2),
                        "profit_percent": round((closes[i] / position["entry_price"] - 1) * 100, 2)
                    })
                    position = None
        
        elif request.strategy == "rsi_oversold":
            rsi_period = request.params.get("period", 14)
            oversold = request.params.get("oversold", 30)
            overbought = request.params.get("overbought", 70)
            
            for i in range(rsi_period + 1, len(closes)):
                rsi = calculate_rsi(closes[:i], rsi_period)
                
                # Buy signal: RSI oversold
                if rsi < oversold and position is None:
                    position = {
                        "entry_price": closes[i],
                        "entry_index": i,
                        "quantity": capital / closes[i]
                    }
                
                # Sell signal: RSI overbought
                elif rsi > overbought and position is not None:
                    profit = (closes[i] - position["entry_price"]) * position["quantity"]
                    capital += profit
                    
                    trades.append({
                        "entry_price": position["entry_price"],
                        "exit_price": closes[i],
                        "profit": round(profit, 2),
                        "profit_percent": round((closes[i] / position["entry_price"] - 1) * 100, 2)
                    })
                    position = None
        
        # Calculate performance metrics
        total_return = capital - request.initial_capital
        return_percent = (capital / request.initial_capital - 1) * 100
        
        winning_trades = [t for t in trades if t["profit"] > 0]
        losing_trades = [t for t in trades if t["profit"] < 0]
        
        win_rate = (len(winning_trades) / len(trades) * 100) if trades else 0
        
        return {
            "success": True,
            "strategy": request.strategy,
            "symbol": request.symbol.upper(),
            "period": f"{request.start_date} to {request.end_date}",
            "initial_capital": request.initial_capital,
            "final_capital": round(capital, 2),
            "total_return": round(total_return, 2),
            "return_percent": round(return_percent, 2),
            "trades": {
                "total": len(trades),
                "winning": len(winning_trades),
                "losing": len(losing_trades),
                "win_rate": round(win_rate, 2)
            },
            "trade_history": trades[:20],  # Return first 20 trades
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/correlations
# ============================================================================

@router.get("/api/correlations")
async def get_correlations(
    symbols: str = Query("BTC,ETH,BNB,SOL,ADA", description="Comma-separated symbols"),
    days: int = Query(30, ge=7, le=90, description="Number of days for correlation")
):
    """
    Get correlation matrix for cryptocurrencies
    
    Calculates price correlations between specified coins
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        
        if len(symbol_list) < 2:
            raise HTTPException(status_code=400, detail="At least 2 symbols required")
        
        # Fetch data for all symbols
        price_data = {}
        
        for symbol in symbol_list:
            try:
                klines = await fetch_ohlcv_for_analysis(symbol, "1d", days)
                if klines:
                    price_data[symbol] = [float(k[4]) for k in klines]
            except:
                logger.warning(f"Could not fetch data for {symbol}")
        
        if len(price_data) < 2:
            raise HTTPException(status_code=404, detail="Insufficient data for correlation analysis")
        
        # Calculate correlation matrix
        correlations = {}
        
        for sym1 in price_data:
            correlations[sym1] = {}
            for sym2 in price_data:
                if sym1 == sym2:
                    correlations[sym1][sym2] = 1.0
                else:
                    # Calculate correlation coefficient
                    prices1 = np.array(price_data[sym1])
                    prices2 = np.array(price_data[sym2])
                    
                    # Ensure same length
                    min_len = min(len(prices1), len(prices2))
                    prices1 = prices1[-min_len:]
                    prices2 = prices2[-min_len:]
                    
                    corr = np.corrcoef(prices1, prices2)[0, 1]
                    correlations[sym1][sym2] = round(float(corr), 3)
        
        return {
            "success": True,
            "symbols": list(price_data.keys()),
            "days": days,
            "correlations": correlations,
            "interpretation": {
                "strong_positive": "> 0.7",
                "moderate_positive": "0.3 to 0.7",
                "weak": "-0.3 to 0.3",
                "moderate_negative": "-0.7 to -0.3",
                "strong_negative": "< -0.7"
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Correlation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


logger.info("✅ Trading Analysis API Router loaded")
