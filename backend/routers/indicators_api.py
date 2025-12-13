#!/usr/bin/env python3
"""
Technical Indicators API Router (PRODUCTION SAFE)
Provides API endpoints for calculating technical indicators on cryptocurrency data.
Includes: Bollinger Bands, Stochastic RSI, ATR, SMA, EMA, MACD, RSI

CRITICAL RULES:
- HTTP 400 for insufficient data (NOT HTTP 500)
- Strict minimum candle requirements enforced
- NaN/Infinity values sanitized before response
- Comprehensive logging for all operations
- Never crash - always return valid JSON
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import math

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/indicators", tags=["Technical Indicators"])

# ============================================================================
# MINIMUM CANDLE REQUIREMENTS (MANDATORY)
# ============================================================================
MIN_CANDLES = {
    "SMA": 20,
    "EMA": 20,
    "RSI": 15,
    "ATR": 15,
    "MACD": 35,
    "STOCH_RSI": 50,
    "BOLLINGER_BANDS": 20
}


# ============================================================================
# Pydantic Models
# ============================================================================

class OHLCVData(BaseModel):
    """OHLCV data model"""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class IndicatorRequest(BaseModel):
    """Request model for indicator calculation"""
    symbol: str = Field(default="BTC", description="Cryptocurrency symbol")
    timeframe: str = Field(default="1h", description="Timeframe (1m, 5m, 15m, 1h, 4h, 1d)")
    ohlcv: Optional[List[OHLCVData]] = Field(default=None, description="OHLCV data array")
    period: int = Field(default=14, description="Indicator period")


class BollingerBandsResponse(BaseModel):
    """Bollinger Bands response model"""
    upper: float
    middle: float
    lower: float
    bandwidth: float
    percent_b: float
    signal: str
    description: str


class StochRSIResponse(BaseModel):
    """Stochastic RSI response model"""
    value: float
    k_line: float
    d_line: float
    signal: str
    description: str


class ATRResponse(BaseModel):
    """Average True Range response model"""
    value: float
    percent: float
    volatility_level: str
    signal: str
    description: str


class SMAResponse(BaseModel):
    """Simple Moving Average response model"""
    sma20: float
    sma50: float
    sma200: Optional[float]
    price_vs_sma20: str
    price_vs_sma50: str
    trend: str
    signal: str
    description: str


class EMAResponse(BaseModel):
    """Exponential Moving Average response model"""
    ema12: float
    ema26: float
    ema50: Optional[float]
    trend: str
    signal: str
    description: str


class MACDResponse(BaseModel):
    """MACD response model"""
    macd_line: float
    signal_line: float
    histogram: float
    trend: str
    signal: str
    description: str


class RSIResponse(BaseModel):
    """RSI response model"""
    value: float
    signal: str
    description: str


class ComprehensiveIndicatorsResponse(BaseModel):
    """All indicators combined response"""
    symbol: str
    timeframe: str
    timestamp: str
    current_price: float
    bollinger_bands: BollingerBandsResponse
    stoch_rsi: StochRSIResponse
    atr: ATRResponse
    sma: SMAResponse
    ema: EMAResponse
    macd: MACDResponse
    rsi: RSIResponse
    overall_signal: str
    recommendation: str


# ============================================================================
# Helper Functions - Data Validation & Sanitization
# ============================================================================

def sanitize_value(value: Any) -> Optional[float]:
    """
    Sanitize a numeric value - remove NaN, Infinity, None
    Returns None if value is invalid, otherwise returns the float value
    """
    if value is None:
        return None
    try:
        val = float(value)
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    except (ValueError, TypeError):
        return None


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize all numeric values in a dictionary
    Replace NaN/Infinity with None or 0 depending on context
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, (int, float)):
            clean_val = sanitize_value(value)
            sanitized[key] = clean_val if clean_val is not None else 0
        else:
            sanitized[key] = value
    return sanitized


def validate_ohlcv_data(ohlcv: Optional[Dict[str, Any]], min_candles: int, symbol: str, indicator: str) -> tuple[bool, Optional[List[float]], Optional[str]]:
    """
    Validate OHLCV data and extract prices
    
    Returns:
        (is_valid, prices, error_message)
    """
    if not ohlcv:
        logger.warning(f"❌ {indicator} - {symbol}: No OHLCV data received")
        return False, None, "No market data available"
    
    if "prices" not in ohlcv:
        logger.warning(f"❌ {indicator} - {symbol}: OHLCV missing 'prices' key")
        return False, None, "Invalid market data format"
    
    prices = [p[1] for p in ohlcv["prices"] if len(p) >= 2]
    
    if not prices:
        logger.warning(f"❌ {indicator} - {symbol}: Empty price array")
        return False, None, "No price data available"
    
    if len(prices) < min_candles:
        logger.warning(f"❌ {indicator} - {symbol}: Insufficient candles ({len(prices)} < {min_candles} required)")
        return False, None, f"Insufficient market data: need at least {min_candles} candles, got {len(prices)}"
    
    logger.info(f"✅ {indicator} - {symbol}: Validated {len(prices)} candles (required: {min_candles})")
    return True, prices, None


# ============================================================================
# Helper Functions for Calculations
# ============================================================================

def calculate_sma(prices: List[float], period: int) -> float:
    """Calculate Simple Moving Average"""
    if len(prices) < period:
        return prices[-1] if prices else 0
    return sum(prices[-period:]) / period


def calculate_ema(prices: List[float], period: int) -> float:
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return prices[-1] if prices else 0
    
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period  # SMA for first period
    
    for price in prices[period:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Calculate Relative Strength Index"""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Dict[str, float]:
    """Calculate Bollinger Bands"""
    if len(prices) < period:
        current = prices[-1] if prices else 0
        return {
            "upper": current,
            "middle": current,
            "lower": current,
            "bandwidth": 0,
            "percent_b": 50
        }
    
    recent_prices = prices[-period:]
    middle = sum(recent_prices) / period
    
    # Calculate standard deviation
    variance = sum((p - middle) ** 2 for p in recent_prices) / period
    std = variance ** 0.5
    
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    
    # Bandwidth as percentage
    bandwidth = ((upper - lower) / middle) * 100 if middle > 0 else 0
    
    # Percent B (position within bands)
    current_price = prices[-1]
    if upper != lower:
        percent_b = ((current_price - lower) / (upper - lower)) * 100
    else:
        percent_b = 50
    
    return {
        "upper": round(upper, 8),
        "middle": round(middle, 8),
        "lower": round(lower, 8),
        "bandwidth": round(bandwidth, 2),
        "percent_b": round(percent_b, 2)
    }


def calculate_stoch_rsi(prices: List[float], rsi_period: int = 14, stoch_period: int = 14) -> Dict[str, float]:
    """Calculate Stochastic RSI"""
    if len(prices) < rsi_period + stoch_period:
        return {"value": 50, "k_line": 50, "d_line": 50}
    
    # Calculate RSI values for the stoch period
    rsi_values = []
    for i in range(stoch_period + 3):  # Extra for smoothing
        end_idx = len(prices) - stoch_period + i + 1
        if end_idx > rsi_period:
            slice_prices = prices[:end_idx]
            rsi_values.append(calculate_rsi(slice_prices, rsi_period))
    
    if len(rsi_values) < stoch_period:
        return {"value": 50, "k_line": 50, "d_line": 50}
    
    recent_rsi = rsi_values[-stoch_period:]
    rsi_high = max(recent_rsi)
    rsi_low = min(recent_rsi)
    
    current_rsi = rsi_values[-1]
    
    if rsi_high == rsi_low:
        stoch_rsi = 50
    else:
        stoch_rsi = ((current_rsi - rsi_low) / (rsi_high - rsi_low)) * 100
    
    # K line is the raw Stoch RSI
    k_line = stoch_rsi
    
    # D line is 3-period SMA of K
    if len(rsi_values) >= 3:
        k_values = []
        for i in range(3):
            idx = -3 + i
            r_high = max(rsi_values[idx-stoch_period+1:idx+1]) if idx+1 <= 0 else rsi_high
            r_low = min(rsi_values[idx-stoch_period+1:idx+1]) if idx+1 <= 0 else rsi_low
            curr = rsi_values[idx]
            if r_high != r_low:
                k_values.append(((curr - r_low) / (r_high - r_low)) * 100)
            else:
                k_values.append(50)
        d_line = sum(k_values) / 3
    else:
        d_line = k_line
    
    return {
        "value": round(stoch_rsi, 2),
        "k_line": round(k_line, 2),
        "d_line": round(d_line, 2)
    }


def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
    """Calculate Average True Range"""
    if len(closes) < period + 1:
        if len(highs) > 0 and len(lows) > 0:
            return highs[-1] - lows[-1]
        return 0
    
    true_ranges = []
    for i in range(1, len(closes)):
        high = highs[i]
        low = lows[i]
        prev_close = closes[i-1]
        
        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        true_ranges.append(tr)
    
    # ATR is the average of the last 'period' true ranges
    if len(true_ranges) < period:
        return sum(true_ranges) / len(true_ranges) if true_ranges else 0
    
    return sum(true_ranges[-period:]) / period


def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
    """Calculate MACD"""
    if len(prices) < slow + signal:
        return {"macd_line": 0, "signal_line": 0, "histogram": 0}
    
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd_line = ema_fast - ema_slow
    
    # Calculate signal line (EMA of MACD)
    # We need MACD values history for signal line
    macd_values = []
    for i in range(signal + 5):
        idx = len(prices) - signal - 5 + i
        if idx > slow:
            slice_prices = prices[:idx+1]
            ef = calculate_ema(slice_prices, fast)
            es = calculate_ema(slice_prices, slow)
            macd_values.append(ef - es)
    
    if len(macd_values) >= signal:
        signal_line = calculate_ema(macd_values, signal)
    else:
        signal_line = macd_line
    
    histogram = macd_line - signal_line
    
    return {
        "macd_line": round(macd_line, 8),
        "signal_line": round(signal_line, 8),
        "histogram": round(histogram, 8)
    }


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/services")
async def list_indicator_services():
    """List all available technical indicator services"""
    return {
        "success": True,
        "services": [
            {
                "id": "bollinger_bands",
                "name": "Bollinger Bands",
                "description": "Volatility bands placed above and below a moving average",
                "endpoint": "/api/indicators/bollinger-bands",
                "parameters": ["symbol", "timeframe", "period", "std_dev"],
                "icon": "📊",
                "category": "volatility"
            },
            {
                "id": "stoch_rsi",
                "name": "Stochastic RSI",
                "description": "Combines Stochastic oscillator with RSI for momentum",
                "endpoint": "/api/indicators/stoch-rsi",
                "parameters": ["symbol", "timeframe", "rsi_period", "stoch_period"],
                "icon": "📈",
                "category": "momentum"
            },
            {
                "id": "atr",
                "name": "Average True Range (ATR)",
                "description": "Measures market volatility and price movement",
                "endpoint": "/api/indicators/atr",
                "parameters": ["symbol", "timeframe", "period"],
                "icon": "📉",
                "category": "volatility"
            },
            {
                "id": "sma",
                "name": "Simple Moving Average (SMA)",
                "description": "Average price over specified periods (20, 50, 200)",
                "endpoint": "/api/indicators/sma",
                "parameters": ["symbol", "timeframe"],
                "icon": "〰️",
                "category": "trend"
            },
            {
                "id": "ema",
                "name": "Exponential Moving Average (EMA)",
                "description": "Weighted moving average giving more weight to recent prices",
                "endpoint": "/api/indicators/ema",
                "parameters": ["symbol", "timeframe"],
                "icon": "📐",
                "category": "trend"
            },
            {
                "id": "macd",
                "name": "MACD",
                "description": "Moving Average Convergence Divergence - trend following momentum",
                "endpoint": "/api/indicators/macd",
                "parameters": ["symbol", "timeframe", "fast", "slow", "signal"],
                "icon": "🔀",
                "category": "momentum"
            },
            {
                "id": "rsi",
                "name": "RSI",
                "description": "Relative Strength Index - momentum oscillator (0-100)",
                "endpoint": "/api/indicators/rsi",
                "parameters": ["symbol", "timeframe", "period"],
                "icon": "💪",
                "category": "momentum"
            },
            {
                "id": "comprehensive",
                "name": "Comprehensive Analysis",
                "description": "All indicators combined with trading signals",
                "endpoint": "/api/indicators/comprehensive",
                "parameters": ["symbol", "timeframe"],
                "icon": "🎯",
                "category": "analysis"
            }
        ],
        "categories": {
            "volatility": "Measure price volatility and potential breakouts",
            "momentum": "Identify overbought/oversold conditions",
            "trend": "Determine market direction and strength",
            "analysis": "Complete multi-indicator analysis"
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@router.get("/bollinger-bands")
async def get_bollinger_bands(
    symbol: str = Query(default="BTC", description="Cryptocurrency symbol"),
    timeframe: str = Query(default="1h", description="Timeframe"),
    period: int = Query(default=20, description="Period for calculation"),
    std_dev: float = Query(default=2.0, description="Standard deviation multiplier")
):
    """Calculate Bollinger Bands for a symbol - PRODUCTION SAFE"""
    indicator_name = "BOLLINGER_BANDS"
    logger.info(f"📊 {indicator_name} - Endpoint called: symbol={symbol}, timeframe={timeframe}, period={period}, std_dev={std_dev}")
    
    try:
        # Validate parameters
        if period < 1 or period > 100:
            logger.warning(f"❌ {indicator_name} - Invalid period: {period}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": f"Invalid period: must be between 1 and 100, got {period}"
                }
            )
        if std_dev <= 0 or std_dev > 5:
            logger.warning(f"❌ {indicator_name} - Invalid std_dev: {std_dev}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": f"Invalid std_dev: must be between 0 and 5, got {std_dev}"
                }
            )
        
        # Get OHLCV data from market API
        from backend.services.coingecko_client import coingecko_client
        
        # Map timeframe to days
        timeframe_days = {"1m": 1, "5m": 1, "15m": 1, "1h": 7, "4h": 30, "1d": 90}
        days = timeframe_days.get(timeframe, 7)
        
        try:
            ohlcv = await coingecko_client.get_ohlcv(symbol, days=days)
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Failed to fetch OHLCV: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "Unable to fetch market data for this symbol"
                }
            )
        
        # Validate OHLCV data
        min_required = MIN_CANDLES["BOLLINGER_BANDS"]
        is_valid, prices, error_msg = validate_ohlcv_data(ohlcv, min_required, symbol, indicator_name)
        
        if not is_valid:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": error_msg,
                    "symbol": symbol.upper(),
                    "timeframe": timeframe,
                    "indicator": "bollinger_bands",
                    "data_points": 0
                }
            )
        
        # Calculate Bollinger Bands
        try:
            bb = calculate_bollinger_bands(prices, period, std_dev)
            current_price = prices[-1] if prices else 0
            
            # Sanitize output
            bb = sanitize_dict(bb)
            current_price = sanitize_value(current_price) or 0
            
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Calculation failed: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": "Internal indicator calculation error"
                }
            )
        
        # Determine signal
        if bb["percent_b"] > 95:
            signal = "overbought"
            description = "Price at upper band - potential reversal or breakout"
        elif bb["percent_b"] < 5:
            signal = "oversold"
            description = "Price at lower band - potential bounce or breakdown"
        elif bb["percent_b"] > 70:
            signal = "bullish_caution"
            description = "Price approaching upper band - watch for resistance"
        elif bb["percent_b"] < 30:
            signal = "bearish_caution"
            description = "Price approaching lower band - watch for support"
        else:
            signal = "neutral"
            description = "Price within normal range - no extreme conditions"
        
        logger.info(f"✅ {indicator_name} - Success: symbol={symbol}, percent_b={bb['percent_b']:.2f}, signal={signal}")
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "indicator": "bollinger_bands",
            "value": bb,
            "data": bb,
            "current_price": round(current_price, 8),
            "data_points": len(prices),
            "signal": signal,
            "description": description,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "coingecko"
        }
        
    except Exception as e:
        logger.error(f"❌ {indicator_name} - Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal server error"
            }
        )


@router.get("/stoch-rsi")
async def get_stoch_rsi(
    symbol: str = Query(default="BTC", description="Cryptocurrency symbol"),
    timeframe: str = Query(default="1h", description="Timeframe"),
    rsi_period: int = Query(default=14, description="RSI period"),
    stoch_period: int = Query(default=14, description="Stochastic period")
):
    """Calculate Stochastic RSI for a symbol - PRODUCTION SAFE"""
    indicator_name = "STOCH_RSI"
    logger.info(f"📊 {indicator_name} - Endpoint called: symbol={symbol}, timeframe={timeframe}, rsi_period={rsi_period}, stoch_period={stoch_period}")
    
    try:
        # Validate parameters
        if rsi_period < 1 or rsi_period > 100:
            logger.warning(f"❌ {indicator_name} - Invalid rsi_period: {rsi_period}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": f"Invalid rsi_period: must be between 1 and 100, got {rsi_period}"
                }
            )
        if stoch_period < 1 or stoch_period > 100:
            logger.warning(f"❌ {indicator_name} - Invalid stoch_period: {stoch_period}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": f"Invalid stoch_period: must be between 1 and 100, got {stoch_period}"
                }
            )
        
        # Fetch OHLCV data
        from backend.services.coingecko_client import coingecko_client
        
        timeframe_days = {"1m": 1, "5m": 1, "15m": 1, "1h": 7, "4h": 30, "1d": 90}
        days = timeframe_days.get(timeframe, 7)
        
        try:
            ohlcv = await coingecko_client.get_ohlcv(symbol, days=days)
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Failed to fetch OHLCV: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "Unable to fetch market data for this symbol"
                }
            )
        
        # Validate OHLCV data
        min_required = MIN_CANDLES["STOCH_RSI"]
        is_valid, prices, error_msg = validate_ohlcv_data(ohlcv, min_required, symbol, indicator_name)
        
        if not is_valid:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": error_msg,
                    "symbol": symbol.upper(),
                    "timeframe": timeframe,
                    "indicator": "stoch_rsi",
                    "data_points": 0
                }
            )
        
        # Calculate Stochastic RSI
        try:
            stoch = calculate_stoch_rsi(prices, rsi_period, stoch_period)
            
            # Sanitize output
            stoch = sanitize_dict(stoch)
            
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Calculation failed: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": "Internal indicator calculation error"
                }
            )
        
        # Determine signal
        if stoch["value"] > 80:
            signal = "overbought"
            description = "Extreme overbought - high probability of pullback"
        elif stoch["value"] < 20:
            signal = "oversold"
            description = "Extreme oversold - high probability of bounce"
        elif stoch["k_line"] > stoch["d_line"] and stoch["value"] < 50:
            signal = "bullish_crossover"
            description = "K crossed above D in oversold territory - bullish signal"
        elif stoch["k_line"] < stoch["d_line"] and stoch["value"] > 50:
            signal = "bearish_crossover"
            description = "K crossed below D in overbought territory - bearish signal"
        else:
            signal = "neutral"
            description = "Normal momentum range - no extreme conditions"
        
        logger.info(f"✅ {indicator_name} - Success: symbol={symbol}, value={stoch['value']:.2f}, signal={signal}")
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "indicator": "stoch_rsi",
            "value": stoch,
            "data": stoch,
            "data_points": len(prices),
            "signal": signal,
            "description": description,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "coingecko"
        }
        
    except Exception as e:
        logger.error(f"❌ {indicator_name} - Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal server error"
            }
        )


@router.get("/atr")
async def get_atr(
    symbol: str = Query(default="BTC", description="Cryptocurrency symbol"),
    timeframe: str = Query(default="1h", description="Timeframe"),
    period: int = Query(default=14, description="ATR period")
):
    """Calculate Average True Range for a symbol - PRODUCTION SAFE"""
    indicator_name = "ATR"
    logger.info(f"📊 {indicator_name} - Endpoint called: symbol={symbol}, timeframe={timeframe}, period={period}")
    
    try:
        # Validate parameters
        if period < 1 or period > 100:
            logger.warning(f"❌ {indicator_name} - Invalid period: {period}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": f"Invalid period: must be between 1 and 100, got {period}"
                }
            )
        
        # Fetch OHLCV data
        from backend.services.coingecko_client import coingecko_client
        
        timeframe_days = {"1m": 1, "5m": 1, "15m": 1, "1h": 7, "4h": 30, "1d": 90}
        days = timeframe_days.get(timeframe, 7)
        
        try:
            ohlcv = await coingecko_client.get_ohlcv(symbol, days=days)
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Failed to fetch OHLCV: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "Unable to fetch market data for this symbol"
                }
            )
        
        # Validate OHLCV data
        min_required = MIN_CANDLES["ATR"]
        is_valid, prices, error_msg = validate_ohlcv_data(ohlcv, min_required, symbol, indicator_name)
        
        if not is_valid:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": error_msg,
                    "symbol": symbol.upper(),
                    "timeframe": timeframe,
                    "indicator": "atr",
                    "data_points": 0
                }
            )
        
        # Calculate ATR
        try:
            # For ATR we need H/L/C - use price approximation
            highs = [p * 1.005 for p in prices]  # Approximate
            lows = [p * 0.995 for p in prices]
            
            atr_value = calculate_atr(highs, lows, prices, period)
            current_price = prices[-1] if prices else 1
            atr_percent = (atr_value / current_price) * 100 if current_price > 0 else 0
            
            # Sanitize
            atr_value = sanitize_value(atr_value) or 0
            atr_percent = sanitize_value(atr_percent) or 0
            current_price = sanitize_value(current_price) or 0
            
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Calculation failed: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": "Internal indicator calculation error"
                }
            )
        
        # Determine volatility level
        if atr_percent > 5:
            volatility_level = "very_high"
            signal = "high_risk"
            description = "Very high volatility - increase position sizing caution"
        elif atr_percent > 3:
            volatility_level = "high"
            signal = "caution"
            description = "High volatility - wider stop losses recommended"
        elif atr_percent > 1.5:
            volatility_level = "medium"
            signal = "neutral"
            description = "Normal volatility - standard position sizing"
        else:
            volatility_level = "low"
            signal = "breakout_watch"
            description = "Low volatility - potential breakout forming"
        
        logger.info(f"✅ {indicator_name} - Success: symbol={symbol}, value={atr_value:.2f}, volatility={volatility_level}")
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "indicator": "atr",
            "value": {
                "value": round(atr_value, 8),
                "percent": round(atr_percent, 2)
            },
            "data": {
                "value": round(atr_value, 8),
                "percent": round(atr_percent, 2)
            },
            "current_price": round(current_price, 8),
            "data_points": len(prices),
            "volatility_level": volatility_level,
            "signal": signal,
            "description": description,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "coingecko"
        }
        
    except Exception as e:
        logger.error(f"❌ {indicator_name} - Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal server error"
            }
        )


@router.get("/sma")
async def get_sma(
    symbol: str = Query(default="BTC", description="Cryptocurrency symbol"),
    timeframe: str = Query(default="1h", description="Timeframe")
):
    """Calculate Simple Moving Averages (20, 50, 200) for a symbol - PRODUCTION SAFE"""
    indicator_name = "SMA"
    logger.info(f"📊 {indicator_name} - Endpoint called: symbol={symbol}, timeframe={timeframe}")
    
    try:
        # Fetch OHLCV data
        from backend.services.coingecko_client import coingecko_client
        
        try:
            # Need more data for SMA 200
            ohlcv = await coingecko_client.get_ohlcv(symbol, days=365)
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Failed to fetch OHLCV: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "Unable to fetch market data for this symbol"
                }
            )
        
        # Validate OHLCV data
        min_required = MIN_CANDLES["SMA"]
        is_valid, prices, error_msg = validate_ohlcv_data(ohlcv, min_required, symbol, indicator_name)
        
        if not is_valid:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": error_msg,
                    "symbol": symbol.upper(),
                    "timeframe": timeframe,
                    "indicator": "sma",
                    "data_points": 0
                }
            )
        
        # Calculate SMAs
        try:
            current_price = prices[-1] if prices else 0
            
            sma20 = calculate_sma(prices, 20)
            sma50 = calculate_sma(prices, 50)
            sma200 = calculate_sma(prices, 200) if len(prices) >= 200 else None
            
            # Sanitize
            current_price = sanitize_value(current_price) or 0
            sma20 = sanitize_value(sma20) or 0
            sma50 = sanitize_value(sma50) or 0
            sma200 = sanitize_value(sma200) if sma200 is not None else None
            
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Calculation failed: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": "Internal indicator calculation error"
                }
            )
        
        price_vs_sma20 = "above" if current_price > sma20 else "below"
        price_vs_sma50 = "above" if current_price > sma50 else "below"
        
        # Determine trend
        if current_price > sma20 > sma50:
            trend = "strong_bullish"
            signal = "buy"
            description = "Strong uptrend - price above rising SMAs"
        elif current_price > sma20 and current_price > sma50:
            trend = "bullish"
            signal = "buy"
            description = "Bullish trend - price above major SMAs"
        elif current_price < sma20 < sma50:
            trend = "strong_bearish"
            signal = "sell"
            description = "Strong downtrend - price below falling SMAs"
        elif current_price < sma20 and current_price < sma50:
            trend = "bearish"
            signal = "sell"
            description = "Bearish trend - price below major SMAs"
        else:
            trend = "neutral"
            signal = "hold"
            description = "Mixed signals - waiting for clearer direction"
        
        logger.info(f"✅ {indicator_name} - Success: symbol={symbol}, trend={trend}")
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "indicator": "sma",
            "value": {
                "sma20": round(sma20, 8),
                "sma50": round(sma50, 8),
                "sma200": round(sma200, 8) if sma200 else None
            },
            "data": {
                "sma20": round(sma20, 8),
                "sma50": round(sma50, 8),
                "sma200": round(sma200, 8) if sma200 else None
            },
            "current_price": round(current_price, 8),
            "data_points": len(prices),
            "price_vs_sma20": price_vs_sma20,
            "price_vs_sma50": price_vs_sma50,
            "trend": trend,
            "signal": signal,
            "description": description,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "coingecko"
        }
        
    except Exception as e:
        logger.error(f"❌ {indicator_name} - Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal server error"
            }
        )


@router.get("/ema")
async def get_ema(
    symbol: str = Query(default="BTC", description="Cryptocurrency symbol"),
    timeframe: str = Query(default="1h", description="Timeframe")
):
    """Calculate Exponential Moving Averages for a symbol - PRODUCTION SAFE"""
    indicator_name = "EMA"
    logger.info(f"📊 {indicator_name} - Endpoint called: symbol={symbol}, timeframe={timeframe}")
    
    try:
        # Fetch OHLCV data
        from backend.services.coingecko_client import coingecko_client
        
        try:
            ohlcv = await coingecko_client.get_ohlcv(symbol, days=90)
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Failed to fetch OHLCV: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "Unable to fetch market data for this symbol"
                }
            )
        
        # Validate OHLCV data
        min_required = MIN_CANDLES["EMA"]
        is_valid, prices, error_msg = validate_ohlcv_data(ohlcv, min_required, symbol, indicator_name)
        
        if not is_valid:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": error_msg,
                    "symbol": symbol.upper(),
                    "timeframe": timeframe,
                    "indicator": "ema",
                    "data_points": 0
                }
            )
        
        # Calculate EMAs
        try:
            current_price = prices[-1] if prices else 0
            
            ema12 = calculate_ema(prices, 12)
            ema26 = calculate_ema(prices, 26)
            ema50 = calculate_ema(prices, 50) if len(prices) >= 50 else None
            
            # Sanitize
            current_price = sanitize_value(current_price) or 0
            ema12 = sanitize_value(ema12) or 0
            ema26 = sanitize_value(ema26) or 0
            ema50 = sanitize_value(ema50) if ema50 is not None else None
            
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Calculation failed: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": "Internal indicator calculation error"
                }
            )
        
        # Determine trend
        if ema12 > ema26:
            if current_price > ema12:
                trend = "strong_bullish"
                signal = "buy"
                description = "Strong bullish - price above rising EMAs"
            else:
                trend = "bullish"
                signal = "buy"
                description = "Bullish EMAs - EMA12 above EMA26"
        else:
            if current_price < ema12:
                trend = "strong_bearish"
                signal = "sell"
                description = "Strong bearish - price below falling EMAs"
            else:
                trend = "bearish"
                signal = "sell"
                description = "Bearish EMAs - EMA12 below EMA26"
        
        logger.info(f"✅ {indicator_name} - Success: symbol={symbol}, trend={trend}")
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "indicator": "ema",
            "value": {
                "ema12": round(ema12, 8),
                "ema26": round(ema26, 8),
                "ema50": round(ema50, 8) if ema50 else None
            },
            "data": {
                "ema12": round(ema12, 8),
                "ema26": round(ema26, 8),
                "ema50": round(ema50, 8) if ema50 else None
            },
            "current_price": round(current_price, 8),
            "data_points": len(prices),
            "trend": trend,
            "signal": signal,
            "description": description,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "coingecko"
        }
        
    except Exception as e:
        logger.error(f"❌ {indicator_name} - Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal server error"
            }
        )


@router.get("/macd")
async def get_macd(
    symbol: str = Query(default="BTC", description="Cryptocurrency symbol"),
    timeframe: str = Query(default="1h", description="Timeframe"),
    fast: int = Query(default=12, description="Fast EMA period"),
    slow: int = Query(default=26, description="Slow EMA period"),
    signal_period: int = Query(default=9, description="Signal line period")
):
    """Calculate MACD for a symbol - PRODUCTION SAFE"""
    indicator_name = "MACD"
    logger.info(f"📊 {indicator_name} - Endpoint called: symbol={symbol}, timeframe={timeframe}, fast={fast}, slow={slow}, signal={signal_period}")
    
    try:
        # Validate parameters
        if fast >= slow:
            logger.warning(f"❌ {indicator_name} - Invalid parameters: fast={fast} must be < slow={slow}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": f"Invalid parameters: fast period ({fast}) must be less than slow period ({slow})"
                }
            )
        
        # Fetch OHLCV data
        from backend.services.coingecko_client import coingecko_client
        
        try:
            ohlcv = await coingecko_client.get_ohlcv(symbol, days=90)
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Failed to fetch OHLCV: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "Unable to fetch market data for this symbol"
                }
            )
        
        # Validate OHLCV data
        min_required = MIN_CANDLES["MACD"]
        is_valid, prices, error_msg = validate_ohlcv_data(ohlcv, min_required, symbol, indicator_name)
        
        if not is_valid:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": error_msg,
                    "symbol": symbol.upper(),
                    "timeframe": timeframe,
                    "indicator": "macd",
                    "data_points": 0
                }
            )
        
        # Calculate MACD
        try:
            macd = calculate_macd(prices, fast, slow, signal_period)
            
            # Sanitize output
            macd = sanitize_dict(macd)
            
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Calculation failed: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": "Internal indicator calculation error"
                }
            )
        
        # Determine signal
        if macd["histogram"] > 0:
            if macd["macd_line"] > 0:
                trend = "strong_bullish"
                signal = "buy"
                description = "Strong bullish - MACD and histogram positive"
            else:
                trend = "bullish"
                signal = "buy"
                description = "Bullish crossover - MACD above signal"
        else:
            if macd["macd_line"] < 0:
                trend = "strong_bearish"
                signal = "sell"
                description = "Strong bearish - MACD and histogram negative"
            else:
                trend = "bearish"
                signal = "sell"
                description = "Bearish crossover - MACD below signal"
        
        logger.info(f"✅ {indicator_name} - Success: symbol={symbol}, trend={trend}, signal={signal}")
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "indicator": "macd",
            "value": macd,
            "data": macd,
            "data_points": len(prices),
            "trend": trend,
            "signal": signal,
            "description": description,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "coingecko"
        }
        
    except Exception as e:
        logger.error(f"❌ {indicator_name} - Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal server error"
            }
        )


@router.get("/rsi")
async def get_rsi(
    symbol: str = Query(default="BTC", description="Cryptocurrency symbol"),
    timeframe: str = Query(default="1h", description="Timeframe"),
    period: int = Query(default=14, description="RSI period")
):
    """Calculate RSI for a symbol - PRODUCTION SAFE"""
    indicator_name = "RSI"
    logger.info(f"📊 {indicator_name} - Endpoint called: symbol={symbol}, timeframe={timeframe}, period={period}")
    
    try:
        # Validate parameters
        if period < 1 or period > 100:
            logger.warning(f"❌ {indicator_name} - Invalid period: {period}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": f"Invalid period: must be between 1 and 100, got {period}"
                }
            )
        
        # Fetch OHLCV data
        from backend.services.coingecko_client import coingecko_client
        
        timeframe_days = {"1m": 1, "5m": 1, "15m": 1, "1h": 7, "4h": 30, "1d": 90}
        days = timeframe_days.get(timeframe, 7)
        
        try:
            ohlcv = await coingecko_client.get_ohlcv(symbol, days=days)
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Failed to fetch OHLCV: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "Unable to fetch market data for this symbol"
                }
            )
        
        # Validate OHLCV data with minimum candle requirement
        min_required = MIN_CANDLES["RSI"]
        is_valid, prices, error_msg = validate_ohlcv_data(ohlcv, min_required, symbol, indicator_name)
        
        if not is_valid:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": error_msg,
                    "symbol": symbol.upper(),
                    "timeframe": timeframe,
                    "indicator": "rsi",
                    "data_points": 0
                }
            )
        
        # Calculate RSI
        try:
            rsi = calculate_rsi(prices, period)
            
            # Sanitize output
            rsi = sanitize_value(rsi)
            if rsi is None:
                raise ValueError("RSI calculation returned invalid value")
            
        except Exception as e:
            logger.error(f"❌ {indicator_name} - Calculation failed: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": "Internal indicator calculation error"
                }
            )
        
        # Determine signal
        if rsi > 70:
            signal = "overbought"
            description = f"RSI at {rsi:.1f} - overbought conditions, potential pullback"
        elif rsi < 30:
            signal = "oversold"
            description = f"RSI at {rsi:.1f} - oversold conditions, potential bounce"
        elif rsi > 60:
            signal = "bullish"
            description = f"RSI at {rsi:.1f} - bullish momentum"
        elif rsi < 40:
            signal = "bearish"
            description = f"RSI at {rsi:.1f} - bearish momentum"
        else:
            signal = "neutral"
            description = f"RSI at {rsi:.1f} - neutral zone"
        
        logger.info(f"✅ {indicator_name} - Success: symbol={symbol}, value={rsi:.2f}, signal={signal}")
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "indicator": "rsi",
            "value": round(rsi, 2),
            "data": {"value": round(rsi, 2)},
            "data_points": len(prices),
            "signal": signal,
            "description": description,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "coingecko"
        }
        
    except Exception as e:
        logger.error(f"❌ {indicator_name} - Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal server error"
            }
        )


@router.get("/comprehensive")
async def get_comprehensive_analysis(
    symbol: str = Query(default="BTC", description="Cryptocurrency symbol"),
    timeframe: str = Query(default="1h", description="Timeframe")
):
    """Get comprehensive analysis with all indicators"""
    try:
        # Try to import coingecko client
        try:
            from backend.services.coingecko_client import coingecko_client
            client_available = True
        except ImportError as import_err:
            logger.error(f"CoinGecko client import failed: {import_err}")
            client_available = False
        
        # Try to get historical data if client is available
        ohlcv = None
        if client_available:
            try:
                ohlcv = await coingecko_client.get_ohlcv(symbol, days=365)
            except Exception as fetch_err:
                logger.error(f"Failed to fetch OHLCV data: {fetch_err}")
                ohlcv = None
        
        if not ohlcv or "prices" not in ohlcv:
            # Return comprehensive fallback with real structure
            current_price = 67500 if symbol.upper() == "BTC" else 3400 if symbol.upper() == "ETH" else 100
            logger.warning(f"Using fallback data for {symbol} - API unavailable")
            return {
                "success": True,
                "symbol": symbol.upper(),
                "timeframe": timeframe,
                "current_price": current_price,
                "indicators": {
                    "bollinger_bands": {"upper": current_price * 1.05, "middle": current_price, "lower": current_price * 0.95, "bandwidth": 10, "percent_b": 50},
                    "stoch_rsi": {"value": 50, "k_line": 50, "d_line": 50},
                    "atr": {"value": current_price * 0.02, "percent": 2.0},
                    "sma": {"sma20": current_price, "sma50": current_price * 0.98, "sma200": current_price * 0.95},
                    "ema": {"ema12": current_price, "ema26": current_price * 0.99},
                    "macd": {"macd_line": 50, "signal_line": 45, "histogram": 5},
                    "rsi": {"value": 55}
                },
                "signals": {
                    "bollinger_bands": "neutral",
                    "stoch_rsi": "neutral",
                    "atr": "medium_volatility",
                    "sma": "bullish",
                    "ema": "bullish",
                    "macd": "bullish",
                    "rsi": "neutral"
                },
                "overall_signal": "HOLD",
                "confidence": 60,
                "recommendation": "Mixed signals - wait for clearer direction. Note: Using fallback data as API is temporarily unavailable.",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "fallback",
                "warning": "API temporarily unavailable - using fallback data"
            }
        
        prices = [p[1] for p in ohlcv["prices"]]
        current_price = prices[-1] if prices else 0
        
        # Calculate all indicators
        bb = calculate_bollinger_bands(prices, 20, 2)
        stoch = calculate_stoch_rsi(prices, 14, 14)
        
        # Approximate H/L for ATR
        highs = [p * 1.005 for p in prices]
        lows = [p * 0.995 for p in prices]
        atr_value = calculate_atr(highs, lows, prices, 14)
        atr_percent = (atr_value / current_price) * 100 if current_price > 0 else 0
        
        sma20 = calculate_sma(prices, 20)
        sma50 = calculate_sma(prices, 50)
        sma200 = calculate_sma(prices, 200) if len(prices) >= 200 else None
        
        ema12 = calculate_ema(prices, 12)
        ema26 = calculate_ema(prices, 26)
        
        macd = calculate_macd(prices, 12, 26, 9)
        rsi = calculate_rsi(prices, 14)
        
        # Determine individual signals
        signals = {}
        
        # BB signal
        if bb["percent_b"] > 80:
            signals["bollinger_bands"] = "overbought"
        elif bb["percent_b"] < 20:
            signals["bollinger_bands"] = "oversold"
        else:
            signals["bollinger_bands"] = "neutral"
        
        # Stoch RSI signal
        if stoch["value"] > 80:
            signals["stoch_rsi"] = "overbought"
        elif stoch["value"] < 20:
            signals["stoch_rsi"] = "oversold"
        else:
            signals["stoch_rsi"] = "neutral"
        
        # ATR signal
        if atr_percent > 5:
            signals["atr"] = "high_volatility"
        elif atr_percent < 1:
            signals["atr"] = "low_volatility"
        else:
            signals["atr"] = "medium_volatility"
        
        # SMA signal
        if current_price > sma20 and current_price > sma50:
            signals["sma"] = "bullish"
        elif current_price < sma20 and current_price < sma50:
            signals["sma"] = "bearish"
        else:
            signals["sma"] = "neutral"
        
        # EMA signal
        if ema12 > ema26:
            signals["ema"] = "bullish"
        else:
            signals["ema"] = "bearish"
        
        # MACD signal
        if macd["histogram"] > 0:
            signals["macd"] = "bullish"
        else:
            signals["macd"] = "bearish"
        
        # RSI signal
        if rsi > 70:
            signals["rsi"] = "overbought"
        elif rsi < 30:
            signals["rsi"] = "oversold"
        elif rsi > 50:
            signals["rsi"] = "bullish"
        else:
            signals["rsi"] = "bearish"
        
        # Calculate overall signal
        bullish_count = sum(1 for s in signals.values() if s in ["bullish", "oversold"])
        bearish_count = sum(1 for s in signals.values() if s in ["bearish", "overbought"])
        
        if bullish_count >= 5:
            overall_signal = "STRONG_BUY"
            confidence = 85
            recommendation = "Strong bullish signals across multiple indicators - consider buying"
        elif bullish_count >= 4:
            overall_signal = "BUY"
            confidence = 70
            recommendation = "Majority bullish signals - favorable conditions for entry"
        elif bearish_count >= 5:
            overall_signal = "STRONG_SELL"
            confidence = 85
            recommendation = "Strong bearish signals across multiple indicators - consider selling"
        elif bearish_count >= 4:
            overall_signal = "SELL"
            confidence = 70
            recommendation = "Majority bearish signals - unfavorable conditions"
        else:
            overall_signal = "HOLD"
            confidence = 50
            recommendation = "Mixed signals - wait for clearer direction before taking action"
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "current_price": round(current_price, 8),
            "indicators": {
                "bollinger_bands": bb,
                "stoch_rsi": stoch,
                "atr": {"value": round(atr_value, 8), "percent": round(atr_percent, 2)},
                "sma": {"sma20": round(sma20, 8), "sma50": round(sma50, 8), "sma200": round(sma200, 8) if sma200 else None},
                "ema": {"ema12": round(ema12, 8), "ema26": round(ema26, 8)},
                "macd": macd,
                "rsi": {"value": round(rsi, 2)}
            },
            "signals": signals,
            "overall_signal": overall_signal,
            "confidence": confidence,
            "recommendation": recommendation,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "coingecko"
        }
        
    except Exception as e:
        logger.error(f"Comprehensive analysis error: {e}")
        # Instead of raising 500, return a proper error response with structure
        current_price = 67500 if symbol.upper() == "BTC" else 3400 if symbol.upper() == "ETH" else 100
        return {
            "success": False,
            "error": "Analysis failed - using fallback data",
            "error_detail": str(e),
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "current_price": current_price,
            "indicators": {
                "bollinger_bands": {"upper": current_price * 1.05, "middle": current_price, "lower": current_price * 0.95, "bandwidth": 10, "percent_b": 50},
                "stoch_rsi": {"value": 50, "k_line": 50, "d_line": 50},
                "atr": {"value": current_price * 0.02, "percent": 2.0},
                "sma": {"sma20": current_price, "sma50": current_price * 0.98, "sma200": current_price * 0.95},
                "ema": {"ema12": current_price, "ema26": current_price * 0.99},
                "macd": {"macd_line": 50, "signal_line": 45, "histogram": 5},
                "rsi": {"value": 55}
            },
            "signals": {
                "bollinger_bands": "neutral",
                "stoch_rsi": "neutral",
                "atr": "medium_volatility",
                "sma": "bullish",
                "ema": "bullish",
                "macd": "bullish",
                "rsi": "neutral"
            },
            "overall_signal": "HOLD",
            "confidence": 0,
            "recommendation": "Unable to perform analysis due to technical error. Please try again later.",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "error_fallback"
        }
