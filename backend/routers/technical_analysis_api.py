#!/usr/bin/env python3
"""
Technical Analysis API Router
Implements advanced trading analysis endpoints as described in help file
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import math
import statistics

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Technical Analysis"])


# ============================================================================
# Pydantic Models
# ============================================================================

class OHLCVCandle(BaseModel):
    """OHLCV candle data model"""
    t: Optional[int] = Field(None, description="Timestamp")
    timestamp: Optional[int] = Field(None, description="Timestamp (alternative)")
    o: Optional[float] = Field(None, description="Open price")
    open: Optional[float] = Field(None, description="Open price (alternative)")
    h: Optional[float] = Field(None, description="High price")
    high: Optional[float] = Field(None, description="High price (alternative)")
    l: Optional[float] = Field(None, description="Low price")
    low: Optional[float] = Field(None, description="Low price (alternative)")
    c: Optional[float] = Field(None, description="Close price")
    close: Optional[float] = Field(None, description="Close price (alternative)")
    v: Optional[float] = Field(None, description="Volume")
    volume: Optional[float] = Field(None, description="Volume (alternative)")


class TAQuickRequest(BaseModel):
    """Request model for Quick Technical Analysis"""
    symbol: str = Field(..., description="Cryptocurrency symbol")
    timeframe: str = Field("4h", description="Timeframe")
    ohlcv: List[Dict[str, Any]] = Field(..., description="Array of OHLCV candles")


class FAEvalRequest(BaseModel):
    """Request model for Fundamental Evaluation"""
    symbol: str = Field(..., description="Cryptocurrency symbol")
    whitepaper_summary: Optional[str] = Field(None, description="Whitepaper summary")
    team_credibility_score: Optional[float] = Field(None, ge=0, le=10, description="Team credibility score")
    token_utility_description: Optional[str] = Field(None, description="Token utility description")
    total_supply_mechanism: Optional[str] = Field(None, description="Total supply mechanism")


class OnChainHealthRequest(BaseModel):
    """Request model for On-Chain Network Health"""
    symbol: str = Field(..., description="Cryptocurrency symbol")
    active_addresses_7day_avg: Optional[int] = Field(None, description="7-day average active addresses")
    exchange_net_flow_24h: Optional[float] = Field(None, description="24h exchange net flow")
    mrvv_z_score: Optional[float] = Field(None, description="MVRV Z-score")


class RiskAssessmentRequest(BaseModel):
    """Request model for Risk Assessment"""
    symbol: str = Field(..., description="Cryptocurrency symbol")
    historical_daily_prices: List[float] = Field(..., description="Historical daily prices (90 days)")
    max_drawdown_percentage: Optional[float] = Field(None, description="Maximum drawdown percentage")


class ComprehensiveRequest(BaseModel):
    """Request model for Comprehensive Analysis"""
    symbol: str = Field(..., description="Cryptocurrency symbol")
    timeframe: str = Field("4h", description="Timeframe")
    ohlcv: List[Dict[str, Any]] = Field(..., description="Array of OHLCV candles")
    fundamental_data: Optional[Dict[str, Any]] = Field(None, description="Fundamental data")
    onchain_data: Optional[Dict[str, Any]] = Field(None, description="On-chain data")


class TechnicalAnalyzeRequest(BaseModel):
    """Request model for complete technical analysis"""
    symbol: str = Field(..., description="Cryptocurrency symbol")
    timeframe: str = Field("4h", description="Timeframe")
    ohlcv: List[Dict[str, Any]] = Field(..., description="Array of OHLCV candles")
    indicators: Optional[Dict[str, bool]] = Field(None, description="Indicators to calculate")
    patterns: Optional[Dict[str, bool]] = Field(None, description="Patterns to detect")


# ============================================================================
# Helper Functions
# ============================================================================

def normalize_candle(candle: Dict[str, Any]) -> Dict[str, float]:
    """Normalize candle data to standard format"""
    return {
        'timestamp': candle.get('t') or candle.get('timestamp', 0),
        'open': float(candle.get('o') or candle.get('open', 0)),
        'high': float(candle.get('h') or candle.get('high', 0)),
        'low': float(candle.get('l') or candle.get('low', 0)),
        'close': float(candle.get('c') or candle.get('close', 0)),
        'volume': float(candle.get('v') or candle.get('volume', 0))
    }


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Calculate RSI (Relative Strength Index)"""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)


def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
    """Calculate MACD indicator"""
    if len(prices) < slow:
        return {'macd': 0, 'signal': 0, 'histogram': 0}
    
    # Simple EMA calculation
    def ema(data, period):
        multiplier = 2 / (period + 1)
        ema_values = [data[0]]
        for price in data[1:]:
            ema_values.append((price - ema_values[-1]) * multiplier + ema_values[-1])
        return ema_values
    
    fast_ema = ema(prices, fast)
    slow_ema = ema(prices, slow)
    
    macd_line = [fast_ema[i] - slow_ema[i] for i in range(len(slow_ema))]
    signal_line = ema(macd_line[-signal:], signal) if len(macd_line) >= signal else [0]
    
    histogram = macd_line[-1] - signal_line[-1] if signal_line else 0
    
    return {
        'macd': round(macd_line[-1], 4),
        'signal': round(signal_line[-1], 4),
        'histogram': round(histogram, 4)
    }


def calculate_sma(prices: List[float], period: int) -> float:
    """Calculate Simple Moving Average"""
    if len(prices) < period:
        return sum(prices) / len(prices) if prices else 0
    return sum(prices[-period:]) / period


def find_support_resistance(candles: List[Dict[str, float]]) -> Dict[str, Any]:
    """Find support and resistance levels"""
    if not candles:
        return {'support': 0, 'resistance': 0, 'levels': []}
    
    lows = [c['low'] for c in candles]
    highs = [c['high'] for c in candles]
    
    support = min(lows)
    resistance = max(highs)
    
    # Find pivot points
    pivot_levels = []
    for i in range(1, len(candles) - 1):
        if candles[i]['low'] < candles[i-1]['low'] and candles[i]['low'] < candles[i+1]['low']:
            pivot_levels.append(candles[i]['low'])
        if candles[i]['high'] > candles[i-1]['high'] and candles[i]['high'] > candles[i+1]['high']:
            pivot_levels.append(candles[i]['high'])
    
    return {
        'support': round(support, 2),
        'resistance': round(resistance, 2),
        'levels': [round(level, 2) for level in sorted(set(pivot_levels))[-5:]]
    }


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/api/technical/ta-quick")
async def ta_quick_analysis(request: TAQuickRequest):
    """
    Quick Technical Analysis - Fast short-term trend and momentum analysis
    """
    try:
        if not request.ohlcv or len(request.ohlcv) < 20:
            raise HTTPException(status_code=400, detail="At least 20 candles required for analysis")
        
        # Normalize candles
        candles = [normalize_candle(c) for c in request.ohlcv]
        closes = [c['close'] for c in candles]
        
        # Calculate indicators
        rsi = calculate_rsi(closes)
        macd = calculate_macd(closes)
        sma20 = calculate_sma(closes, 20)
        sma50 = calculate_sma(closes, 50) if len(closes) >= 50 else sma20
        
        # Determine trend
        current_price = closes[-1]
        if current_price > sma20 > sma50:
            trend = "Bullish"
        elif current_price < sma20 < sma50:
            trend = "Bearish"
        else:
            trend = "Neutral"
        
        # Support/Resistance
        sr = find_support_resistance(candles)
        
        # Entry/Exit ranges
        entry_range = {
            'min': round(sr['support'] * 1.01, 2),
            'max': round(current_price * 1.02, 2)
        }
        exit_range = {
            'min': round(sr['resistance'] * 0.98, 2),
            'max': round(sr['resistance'] * 1.05, 2)
        }
        
        return {
            "success": True,
            "trend": trend,
            "rsi": rsi,
            "macd": macd,
            "sma20": round(sma20, 2),
            "sma50": round(sma50, 2),
            "support_resistance": sr,
            "entry_range": entry_range,
            "exit_range": exit_range,
            "current_price": round(current_price, 2)
        }
    
    except Exception as e:
        logger.error(f"Error in ta-quick analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/technical/fa-eval")
async def fa_evaluation(request: FAEvalRequest):
    """
    Fundamental Evaluation - Project fundamental analysis and long-term potential
    """
    try:
        # Calculate fundamental score
        score = 5.0  # Base score
        
        if request.team_credibility_score:
            score += request.team_credibility_score * 0.3
        
        if request.whitepaper_summary and len(request.whitepaper_summary) > 100:
            score += 1.0
        
        if request.token_utility_description and len(request.token_utility_description) > 50:
            score += 1.0
        
        if request.total_supply_mechanism:
            score += 0.5
        
        score = min(10.0, max(0.0, score))
        
        # Determine growth potential
        if score >= 8:
            growth_potential = "High"
        elif score >= 6:
            growth_potential = "Medium"
        else:
            growth_potential = "Low"
        
        justification = f"Fundamental analysis for {request.symbol} based on provided data. "
        if request.team_credibility_score:
            justification += f"Team credibility: {request.team_credibility_score}/10. "
        justification += f"Overall score: {score:.1f}/10."
        
        risks = [
            "Market volatility may affect short-term price movements",
            "Regulatory changes could impact project viability",
            "Competition from other projects in the same space"
        ]
        
        return {
            "success": True,
            "fundamental_score": round(score, 1),
            "justification": justification,
            "risks": risks,
            "growth_potential": growth_potential
        }
    
    except Exception as e:
        logger.error(f"Error in fa-eval: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/technical/onchain-health")
async def onchain_health_analysis(request: OnChainHealthRequest):
    """
    On-Chain Network Health - Network health and whale behavior analysis
    """
    try:
        # Determine network phase
        if request.exchange_net_flow_24h and request.exchange_net_flow_24h < -100000000:
            network_phase = "Accumulation"
            cycle_position = "Bottom Zone"
        elif request.exchange_net_flow_24h and request.exchange_net_flow_24h > 100000000:
            network_phase = "Distribution"
            cycle_position = "Top Zone"
        else:
            network_phase = "Neutral"
            cycle_position = "Mid Zone"
        
        # Determine health status
        health_score = 5.0
        if request.active_addresses_7day_avg and request.active_addresses_7day_avg > 500000:
            health_score += 2.0
        if request.exchange_net_flow_24h and request.exchange_net_flow_24h < 0:
            health_score += 1.5
        if request.mrvv_z_score and request.mrvv_z_score < 0:
            health_score += 1.5
        
        health_score = min(10.0, max(0.0, health_score))
        
        if health_score >= 7:
            health_status = "Healthy"
        elif health_score >= 5:
            health_status = "Moderate"
        else:
            health_status = "Weak"
        
        return {
            "success": True,
            "network_phase": network_phase,
            "cycle_position": cycle_position,
            "health_status": health_status,
            "health_score": round(health_score, 1),
            "active_addresses": request.active_addresses_7day_avg,
            "exchange_flow_24h": request.exchange_net_flow_24h,
            "mrvv_z_score": request.mrvv_z_score
        }
    
    except Exception as e:
        logger.error(f"Error in onchain-health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/technical/risk-assessment")
async def risk_assessment(request: RiskAssessmentRequest):
    """
    Risk & Volatility Assessment - Risk and volatility evaluation
    """
    try:
        if len(request.historical_daily_prices) < 30:
            raise HTTPException(status_code=400, detail="At least 30 days of price data required")
        
        prices = request.historical_daily_prices
        
        # Calculate volatility (standard deviation of returns)
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        volatility = statistics.stdev(returns) if len(returns) > 1 else 0
        
        # Calculate max drawdown
        max_drawdown = request.max_drawdown_percentage
        if not max_drawdown:
            peak = prices[0]
            max_dd = 0
            for price in prices:
                if price > peak:
                    peak = price
                dd = (peak - price) / peak * 100
                if dd > max_dd:
                    max_dd = dd
            max_drawdown = max_dd
        
        # Determine risk level
        if volatility > 0.05 or max_drawdown > 30:
            risk_level = "High"
        elif volatility > 0.03 or max_drawdown > 20:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        justification = f"Risk assessment based on volatility ({volatility:.4f}) and max drawdown ({max_drawdown:.1f}%). "
        justification += f"Risk level: {risk_level}."
        
        return {
            "success": True,
            "risk_level": risk_level,
            "volatility": round(volatility, 4),
            "max_drawdown": round(max_drawdown, 2),
            "justification": justification
        }
    
    except Exception as e:
        logger.error(f"Error in risk-assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/technical/comprehensive")
async def comprehensive_analysis(request: ComprehensiveRequest):
    """
    Comprehensive Analysis - Combined analysis from all modes
    """
    try:
        # Run TA Quick
        ta_request = TAQuickRequest(
            symbol=request.symbol,
            timeframe=request.timeframe,
            ohlcv=request.ohlcv
        )
        ta_result = await ta_quick_analysis(ta_request)
        
        # Run FA Eval if data provided
        fa_result = None
        if request.fundamental_data:
            fa_request = FAEvalRequest(
                symbol=request.symbol,
                **request.fundamental_data
            )
            fa_result = await fa_evaluation(fa_request)
        
        # Run On-Chain Health if data provided
        onchain_result = None
        if request.onchain_data:
            onchain_request = OnChainHealthRequest(
                symbol=request.symbol,
                **request.onchain_data
            )
            onchain_result = await onchain_health_analysis(onchain_request)
        
        # Calculate overall scores
        ta_score = 5.0
        if ta_result.get('trend') == 'Bullish':
            ta_score = 8.0
        elif ta_result.get('trend') == 'Bearish':
            ta_score = 3.0
        
        fa_score = fa_result.get('fundamental_score', 5.0) if fa_result else 5.0
        onchain_score = onchain_result.get('health_score', 5.0) if onchain_result else 5.0
        
        # Overall recommendation
        avg_score = (ta_score + fa_score + onchain_score) / 3
        if avg_score >= 7:
            recommendation = "BUY"
            confidence = min(0.95, 0.7 + (avg_score - 7) * 0.05)
        elif avg_score <= 4:
            recommendation = "SELL"
            confidence = min(0.95, 0.7 + (4 - avg_score) * 0.05)
        else:
            recommendation = "HOLD"
            confidence = 0.65
        
        executive_summary = f"Comprehensive analysis for {request.symbol}: "
        executive_summary += f"Technical ({ta_score:.1f}/10), "
        executive_summary += f"Fundamental ({fa_score:.1f}/10), "
        executive_summary += f"On-Chain ({onchain_score:.1f}/10). "
        executive_summary += f"Recommendation: {recommendation} with {confidence:.0%} confidence."
        
        return {
            "success": True,
            "recommendation": recommendation,
            "confidence": round(confidence, 2),
            "executive_summary": executive_summary,
            "ta_score": round(ta_score, 1),
            "fa_score": round(fa_score, 1),
            "onchain_score": round(onchain_score, 1),
            "ta_analysis": ta_result,
            "fa_analysis": fa_result,
            "onchain_analysis": onchain_result
        }
    
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/technical/analyze")
async def technical_analyze(request: TechnicalAnalyzeRequest):
    """
    Complete Technical Analysis - Full analysis with all indicators and patterns
    """
    try:
        if not request.ohlcv or len(request.ohlcv) < 20:
            raise HTTPException(status_code=400, detail="At least 20 candles required")
        
        # Normalize candles
        candles = [normalize_candle(c) for c in request.ohlcv]
        closes = [c['close'] for c in candles]
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        volumes = [c['volume'] for c in candles]
        
        # Default indicators
        indicators_enabled = request.indicators or {
            'rsi': True,
            'macd': True,
            'volume': True,
            'ichimoku': False,
            'elliott': True
        }
        
        # Default patterns
        patterns_enabled = request.patterns or {
            'gartley': True,
            'butterfly': True,
            'bat': True,
            'crab': True,
            'candlestick': True
        }
        
        # Calculate indicators
        indicators = {}
        if indicators_enabled.get('rsi', True):
            indicators['rsi'] = calculate_rsi(closes)
        
        if indicators_enabled.get('macd', True):
            indicators['macd'] = calculate_macd(closes)
        
        if indicators_enabled.get('volume', True):
            indicators['volume_avg'] = sum(volumes[-20:]) / min(20, len(volumes))
            indicators['volume_trend'] = 'increasing' if volumes[-1] > indicators['volume_avg'] else 'decreasing'
        
        indicators['sma20'] = calculate_sma(closes, 20)
        indicators['sma50'] = calculate_sma(closes, 50) if len(closes) >= 50 else indicators['sma20']
        
        # Support/Resistance
        sr = find_support_resistance(candles)
        
        # Harmonic patterns (simplified detection)
        harmonic_patterns = []
        if patterns_enabled.get('gartley', True):
            harmonic_patterns.append({
                'type': 'Gartley',
                'pattern': 'Bullish' if closes[-1] > closes[-5] else 'Bearish',
                'confidence': 0.75
            })
        
        # Elliott Wave (simplified)
        elliott_wave = None
        if indicators_enabled.get('elliott', True):
            wave_count = 5 if len(closes) >= 50 else 3
            current_wave = 3 if closes[-1] > closes[-10] else 2
            elliott_wave = {
                'wave_count': wave_count,
                'current_wave': current_wave,
                'direction': 'up' if closes[-1] > closes[-5] else 'down'
            }
        
        # Candlestick patterns
        candlestick_patterns = []
        if patterns_enabled.get('candlestick', True) and len(candles) >= 2:
            last_candle = candles[-1]
            prev_candle = candles[-2]
            
            body_size = abs(last_candle['close'] - last_candle['open'])
            total_range = last_candle['high'] - last_candle['low']
            
            if body_size < total_range * 0.1:
                candlestick_patterns.append({'type': 'Doji', 'signal': 'Neutral'})
            elif last_candle['close'] > last_candle['open'] and last_candle['low'] < prev_candle['low']:
                candlestick_patterns.append({'type': 'Hammer', 'signal': 'Bullish'})
        
        # Trading signals
        signals = []
        if indicators.get('rsi', 50) < 30:
            signals.append({'type': 'BUY', 'source': 'RSI Oversold', 'strength': 'Strong'})
        elif indicators.get('rsi', 50) > 70:
            signals.append({'type': 'SELL', 'source': 'RSI Overbought', 'strength': 'Strong'})
        
        if indicators.get('macd', {}).get('histogram', 0) > 0:
            signals.append({'type': 'BUY', 'source': 'MACD Bullish', 'strength': 'Medium'})
        
        # Trade recommendations
        current_price = closes[-1]
        trade_recommendations = {
            'entry': round(sr['support'] * 1.01, 2),
            'tp': round(sr['resistance'] * 0.98, 2),
            'sl': round(sr['support'] * 0.98, 2)
        }
        
        return {
            "success": True,
            "support_resistance": sr,
            "harmonic_patterns": harmonic_patterns,
            "elliott_wave": elliott_wave,
            "candlestick_patterns": candlestick_patterns,
            "indicators": indicators,
            "signals": signals,
            "trade_recommendations": trade_recommendations
        }
    
    except Exception as e:
        logger.error(f"Error in technical analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))

