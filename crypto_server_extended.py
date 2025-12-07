#!/usr/bin/env python3
"""
Extended Cryptocurrency Server - Support for ALL Client Endpoints
Handles all requests from client applications with full compatibility
"""

import asyncio
import logging
import sys
import time
import uuid
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Set, List
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request, status, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    import httpx
    import uvicorn
except ImportError as e:
    logger.error(f"❌ Missing required packages: {e}")
    logger.error("Please install: pip install fastapi uvicorn httpx pydantic")
    sys.exit(1)


# ============================================================================
# MODELS
# ============================================================================

class SentimentAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

class PredictRequest(BaseModel):
    symbol: str
    timeframe: Optional[str] = "1h"
    features: Optional[Dict[str, Any]] = None


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list[float]] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        self.requests[client_id].append(now)
        return True
    
    def get_remaining(self, client_id: str) -> int:
        now = time.time()
        window_start = now - self.window_seconds
        recent_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        return max(0, self.max_requests - len(recent_requests))


# ============================================================================
# WEBSOCKET CONNECTION MANAGER
# ============================================================================

class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self.client_subscriptions: Dict[str, Set[str]] = defaultdict(set)
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"✅ WebSocket client connected: {client_id}")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        for symbol in self.client_subscriptions.get(client_id, set()).copy():
            self.unsubscribe(client_id, symbol)
        if client_id in self.client_subscriptions:
            del self.client_subscriptions[client_id]
        logger.info(f"❌ WebSocket client disconnected: {client_id}")
    
    def subscribe(self, client_id: str, symbol: str):
        self.subscriptions[symbol].add(client_id)
        self.client_subscriptions[client_id].add(symbol)
    
    def unsubscribe(self, client_id: str, symbol: str):
        self.subscriptions[symbol].discard(client_id)
        self.client_subscriptions[client_id].discard(symbol)
        if not self.subscriptions[symbol]:
            del self.subscriptions[symbol]
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast_to_symbol(self, symbol: str, message: Dict[str, Any]):
        disconnected = []
        for client_id in self.subscriptions.get(symbol, set()).copy():
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected.append(client_id)
        for client_id in disconnected:
            self.disconnect(client_id)


# ============================================================================
# MARKET DATA FETCHER
# ============================================================================

class MarketDataFetcher:
    def __init__(self):
        self.binance_base_url = "https://api.binance.com/api/v3"
        self.timeout = 10.0
        self.timeframe_map = {
            "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w"
        }
    
    def _normalize_symbol(self, symbol: str) -> str:
        symbol = symbol.upper().strip().replace("/", "")
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        return symbol
    
    async def get_current_price(self, symbol: str) -> Dict[str, Any]:
        binance_symbol = self._normalize_symbol(symbol)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.binance_base_url}/ticker/price",
                    params={"symbol": binance_symbol}
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "symbol": symbol.upper().replace("USDT", ""),
                        "price": float(data["price"]),
                        "timestamp": int(time.time() * 1000),
                        "source": "binance"
                    }
                else:
                    raise HTTPException(status_code=404, detail=f"Symbol not found: {symbol}")
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to fetch price: {str(e)}")
    
    async def get_ohlc_data(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> List[Dict[str, Any]]:
        binance_symbol = self._normalize_symbol(symbol)
        binance_interval = self.timeframe_map.get(timeframe, "1h")
        limit = min(limit, 1000)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.binance_base_url}/klines",
                    params={"symbol": binance_symbol, "interval": binance_interval, "limit": limit}
                )
                if response.status_code == 200:
                    klines = response.json()
                    ohlc_data = []
                    for kline in klines:
                        if float(kline[1]) > 0 and float(kline[4]) > 0:
                            ohlc_data.append({
                                "timestamp": int(kline[0]),
                                "open": float(kline[1]),
                                "high": float(kline[2]),
                                "low": float(kline[3]),
                                "close": float(kline[4]),
                                "volume": float(kline[5])
                            })
                    return ohlc_data
                else:
                    raise HTTPException(status_code=404, detail=f"Invalid symbol or timeframe")
        except Exception as e:
            logger.error(f"Error fetching OHLC for {symbol}: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to fetch OHLC: {str(e)}")
    
    async def get_24h_ticker(self, symbol: str) -> Dict[str, Any]:
        binance_symbol = self._normalize_symbol(symbol)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.binance_base_url}/ticker/24hr",
                    params={"symbol": binance_symbol}
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "symbol": symbol.upper().replace("USDT", ""),
                        "price": float(data.get("lastPrice", 0)),
                        "change24h": float(data.get("priceChange", 0)),
                        "changePercent24h": float(data.get("priceChangePercent", 0)),
                        "volume24h": float(data.get("volume", 0)),
                        "high24h": float(data.get("highPrice", 0)),
                        "low24h": float(data.get("lowPrice", 0)),
                        "timestamp": int(time.time() * 1000)
                    }
                else:
                    raise HTTPException(status_code=404, detail=f"Symbol not found")
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to fetch ticker")


# ============================================================================
# SENTIMENT ANALYZER
# ============================================================================

class SentimentAnalyzer:
    def __init__(self):
        self.bullish_keywords = {
            'bullish', 'bull', 'buy', 'moon', 'pump', 'surge', 'rally', 'gain', 'profit',
            'up', 'rise', 'growth', 'strong', 'breakthrough', 'milestone', 'success',
            'positive', 'uptrend', 'breakout', 'ath', 'recovery'
        }
        self.bearish_keywords = {
            'bearish', 'bear', 'sell', 'dump', 'crash', 'drop', 'fall', 'decline', 'loss',
            'down', 'weak', 'correction', 'resistance', 'fear', 'panic', 'warning',
            'negative', 'downtrend', 'breakdown', 'support', 'capitulation'
        }
    
    def analyze(self, text: str) -> Dict[str, Any]:
        if not text:
            return {"sentiment": "Neutral", "confidence": 0.5, "keywords": {}}
        
        text_lower = text.lower()
        words = text_lower.split()
        bullish_count = sum(1 for word in words if any(kw in word for kw in self.bullish_keywords))
        bearish_count = sum(1 for word in words if any(kw in word for kw in self.bearish_keywords))
        total_keywords = bullish_count + bearish_count
        
        if total_keywords == 0:
            sentiment = "Neutral"
            confidence = 0.5
        elif bullish_count > bearish_count:
            sentiment = "Bullish"
            confidence = min(0.5 + (bullish_count / max(len(words), 1)) * 2, 0.95)
        elif bearish_count > bullish_count:
            sentiment = "Bearish"
            confidence = min(0.5 + (bearish_count / max(len(words), 1)) * 2, 0.95)
        else:
            sentiment = "Neutral"
            confidence = 0.6
        
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "keywords": {"bullish": bullish_count, "bearish": bearish_count, "total": total_keywords}
        }


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Extended Cryptocurrency Data Server",
    description="Complete API for cryptocurrency data with all client endpoints",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
ws_manager = WebSocketConnectionManager()
sentiment_analyzer = SentimentAnalyzer()
market_data_fetcher = MarketDataFetcher()


# ============================================================================
# MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    client_id = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(client_id):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "retry_after": 60}
        )
    
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(rate_limiter.get_remaining(client_id))
    return response


# ============================================================================
# BASIC ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "Extended Cryptocurrency Data Server",
        "version": "2.0.0",
        "status": "online",
        "endpoints": {
            "market": "/api/market, /market",
            "ohlcv": "/api/ohlcv, /ohlcv",
            "stats": "/api/stats, /stats",
            "websocket": "/ws",
            "ai": "/api/ai/*",
            "analysis": "/analysis/*",
            "trading": "/api/trading/*"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "websocket_connections": len(ws_manager.active_connections)
    }


# ============================================================================
# MARKET ENDPOINTS (with and without /api prefix)
# ============================================================================

@app.get("/api/market")
@app.get("/market")
async def get_market(
    limit: int = Query(100, ge=1, le=200),
    symbol: Optional[str] = None
):
    """Get market data for multiple symbols"""
    try:
        symbols = []
        if symbol:
            symbols = [s.strip().upper() for s in symbol.split(",")]
        else:
            symbols = ["BTC", "ETH", "BNB", "SOL", "ADA", "XRP", "DOT", "LINK", "MATIC", "AVAX"]
        
        symbols = symbols[:limit]
        market_data = []
        
        for sym in symbols:
            try:
                ticker = await market_data_fetcher.get_24h_ticker(sym)
                market_data.append(ticker)
            except:
                pass
        
        return {
            "data": market_data,
            "count": len(market_data),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Market endpoint error: {e}")
        return {"data": [], "count": 0, "error": str(e)}


@app.get("/api/market/history")
async def get_market_history(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 200
):
    """Get historical market data"""
    try:
        clean_symbol = symbol.replace("/", "")
        ohlc_data = await market_data_fetcher.get_ohlc_data(clean_symbol, timeframe, limit)
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": ohlc_data,
            "count": len(ohlc_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/price")
async def get_price(symbol: str):
    """Get current price"""
    result = await market_data_fetcher.get_current_price(symbol)
    return result


# ============================================================================
# OHLCV ENDPOINTS (with and without /api prefix)
# ============================================================================

@app.get("/api/ohlcv")
@app.get("/ohlcv")
async def get_ohlcv(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 100
):
    """Get OHLCV data"""
    try:
        ohlc_data = await market_data_fetcher.get_ohlc_data(symbol, timeframe, limit)
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": ohlc_data,
            "count": len(ohlc_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/ohlc")
async def get_market_ohlc(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 100
):
    """Get OHLC data (alternative endpoint)"""
    return await get_ohlcv(symbol, timeframe, limit)


# ============================================================================
# STATS ENDPOINT (with and without /api prefix)
# ============================================================================

@app.get("/api/stats")
@app.get("/stats")
async def get_stats():
    """Get market statistics"""
    try:
        # Get data for major coins
        symbols = ["BTC", "ETH", "BNB"]
        tickers = []
        
        for sym in symbols:
            try:
                ticker = await market_data_fetcher.get_24h_ticker(sym)
                tickers.append(ticker)
            except:
                pass
        
        # Calculate aggregate stats
        total_volume = sum(t.get("volume24h", 0) for t in tickers)
        avg_change = sum(t.get("changePercent24h", 0) for t in tickers) / len(tickers) if tickers else 0
        
        return {
            "total_volume_24h": total_volume,
            "average_change_24h": round(avg_change, 2),
            "total_coins": len(tickers),
            "timestamp": datetime.utcnow().isoformat(),
            "top_coins": tickers
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {
            "total_volume_24h": 0,
            "average_change_24h": 0,
            "total_coins": 0,
            "error": str(e)
        }


# ============================================================================
# SENTIMENT ANALYSIS
# ============================================================================

@app.post("/api/sentiment/analyze")
async def analyze_sentiment(request: SentimentAnalysisRequest):
    """Analyze text sentiment"""
    result = sentiment_analyzer.analyze(request.text)
    return result


@app.get("/analysis/sentiment")
async def get_sentiment(symbol: str):
    """Get sentiment for a symbol"""
    # Generate mock sentiment based on price action
    try:
        ticker = await market_data_fetcher.get_24h_ticker(symbol)
        change = ticker.get("changePercent24h", 0)
        
        if change > 5:
            sentiment = "very_bullish"
            score = 0.8
        elif change > 2:
            sentiment = "bullish"
            score = 0.65
        elif change < -5:
            sentiment = "very_bearish"
            score = 0.2
        elif change < -2:
            sentiment = "bearish"
            score = 0.35
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "symbol": symbol,
            "sentiment": sentiment,
            "score": score,
            "change_24h": change,
            "timestamp": datetime.utcnow().isoformat()
        }
    except:
        return {
            "symbol": symbol,
            "sentiment": "neutral",
            "score": 0.5,
            "error": "Could not fetch data"
        }


# ============================================================================
# AI ENDPOINTS
# ============================================================================

@app.get("/api/ai/signals")
async def get_ai_signals(limit: int = 10):
    """Get AI trading signals"""
    try:
        symbols = ["BTC", "ETH", "BNB", "SOL", "ADA"][:limit]
        signals = []
        
        for symbol in symbols:
            try:
                ticker = await market_data_fetcher.get_24h_ticker(symbol)
                change = ticker.get("changePercent24h", 0)
                
                if change > 3:
                    signal = "BUY"
                    strength = "strong"
                elif change > 1:
                    signal = "BUY"
                    strength = "moderate"
                elif change < -3:
                    signal = "SELL"
                    strength = "strong"
                elif change < -1:
                    signal = "SELL"
                    strength = "moderate"
                else:
                    signal = "HOLD"
                    strength = "weak"
                
                signals.append({
                    "symbol": symbol,
                    "signal": signal,
                    "strength": strength,
                    "price": ticker.get("price", 0),
                    "change_24h": change,
                    "confidence": round(0.5 + abs(change) / 20, 2)
                })
            except:
                pass
        
        return {
            "signals": signals,
            "count": len(signals),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"AI signals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/predict")
async def predict_price(request: PredictRequest):
    """AI price prediction"""
    try:
        ticker = await market_data_fetcher.get_24h_ticker(request.symbol)
        current_price = ticker.get("price", 0)
        change = ticker.get("changePercent24h", 0)
        
        # Simple prediction based on trend
        prediction_1h = current_price * (1 + (change / 100) * 0.1)
        prediction_4h = current_price * (1 + (change / 100) * 0.4)
        prediction_24h = current_price * (1 + (change / 100))
        
        return {
            "symbol": request.symbol,
            "current_price": current_price,
            "predictions": {
                "1h": round(prediction_1h, 2),
                "4h": round(prediction_4h, 2),
                "24h": round(prediction_24h, 2)
            },
            "confidence": 0.75,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# TRADING ENDPOINTS
# ============================================================================

@app.get("/api/trading/portfolio")
@app.get("/api/portfolio")
async def get_portfolio():
    """Get portfolio data"""
    return {
        "total_value": 10000.0,
        "available_balance": 5000.0,
        "positions": [
            {"symbol": "BTC", "amount": 0.1, "value": 5000, "pnl": 500, "pnl_percent": 10},
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/professional-risk/metrics")
async def get_risk_metrics():
    """Get professional risk metrics"""
    return {
        "var_95": 250.0,
        "cvar_95": 350.0,
        "sharpe_ratio": 1.5,
        "sortino_ratio": 2.0,
        "max_drawdown": -15.5,
        "win_rate": 0.65,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# FUTURES ENDPOINTS (mock data)
# ============================================================================

@app.get("/api/futures/positions")
async def get_futures_positions():
    """Get futures positions"""
    return {
        "positions": [],
        "total_pnl": 0.0,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/futures/orders")
async def get_futures_orders():
    """Get futures orders"""
    return {
        "orders": [],
        "count": 0,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/futures/balance")
async def get_futures_balance():
    """Get futures balance"""
    return {
        "balance": 10000.0,
        "available": 10000.0,
        "margin_used": 0.0,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/futures/orderbook")
async def get_futures_orderbook(symbol: str):
    """Get futures orderbook"""
    return {
        "symbol": symbol,
        "bids": [[50000, 1.5], [49900, 2.0]],
        "asks": [[50100, 1.5], [50200, 2.0]],
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================

@app.get("/analysis/harmonic")
async def get_harmonic_analysis():
    """Harmonic pattern analysis"""
    return {
        "patterns": [
            {"type": "Gartley", "status": "forming", "completion": 75}
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/analysis/elliott")
async def get_elliott_analysis():
    """Elliott Wave analysis"""
    return {
        "wave": "Wave 3",
        "trend": "bullish",
        "targets": [52000, 55000, 60000],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/analysis/smc")
async def get_smc_analysis():
    """Smart Money Concept analysis"""
    return {
        "order_blocks": [{"price": 49500, "type": "bullish"}],
        "liquidity_zones": [{"price": 51000, "type": "sell_side"}],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/analysis/whale")
async def get_whale_analysis(symbol: str):
    """Whale activity analysis"""
    return {
        "symbol": symbol,
        "large_transactions": 15,
        "whale_sentiment": "accumulating",
        "net_flow": 1500000,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# OTHER ENDPOINTS
# ============================================================================

@app.get("/api/training-metrics")
async def get_training_metrics():
    """Get AI training metrics"""
    return {
        "accuracy": 0.85,
        "loss": 0.15,
        "epochs": 100,
        "last_trained": datetime.utcnow().isoformat()
    }


@app.get("/api/scoring/snapshot")
async def get_scoring_snapshot(symbol: str, tfs: List[str] = Query(["1h", "4h"])):
    """Get scoring snapshot"""
    return {
        "symbol": symbol,
        "timeframes": {tf: {"score": 75, "signal": "bullish"} for tf in tfs},
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/entry-plan")
async def get_entry_plan(
    symbol: str,
    accountBalance: float = 1000,
    riskPercent: float = 2
):
    """Get entry plan"""
    risk_amount = accountBalance * (riskPercent / 100)
    return {
        "symbol": symbol,
        "entry_price": 50000,
        "stop_loss": 49000,
        "take_profit": [51000, 52000, 53000],
        "position_size": risk_amount / 1000,
        "risk_amount": risk_amount,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/strategies/pipeline/run")
async def run_strategy_pipeline():
    """Run strategy pipeline"""
    return {
        "status": "completed",
        "signals_generated": 5,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    client_id = str(uuid.uuid4())
    
    try:
        await ws_manager.connect(websocket, client_id)
        
        await ws_manager.send_personal_message({
            "type": "connected",
            "client_id": client_id,
            "message": "Connected to cryptocurrency data stream",
            "timestamp": datetime.utcnow().isoformat()
        }, client_id)
        
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "subscribe":
                    symbol = data.get("symbol", "").upper()
                    if symbol:
                        ws_manager.subscribe(client_id, symbol)
                        await ws_manager.send_personal_message({
                            "type": "subscribed",
                            "symbol": symbol
                        }, client_id)
                        
                        try:
                            price_data = await market_data_fetcher.get_current_price(symbol)
                            await ws_manager.send_personal_message({
                                "type": "price_update",
                                **price_data
                            }, client_id)
                        except:
                            pass
                
                elif message_type == "unsubscribe":
                    symbol = data.get("symbol", "").upper()
                    if symbol:
                        ws_manager.unsubscribe(client_id, symbol)
                        await ws_manager.send_personal_message({
                            "type": "unsubscribed",
                            "symbol": symbol
                        }, client_id)
                
                elif message_type == "ping":
                    await ws_manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, client_id)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"WebSocket message error: {e}")
                await ws_manager.send_personal_message({
                    "type": "error",
                    "error": str(e)
                }, client_id)
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        ws_manager.disconnect(client_id)


# ============================================================================
# BACKGROUND TASK
# ============================================================================

async def price_streaming_task():
    """Background task for streaming prices"""
    logger.info("🔄 Starting price streaming")
    
    while True:
        try:
            symbols = list(ws_manager.subscriptions.keys())
            
            if symbols:
                for symbol in symbols:
                    try:
                        price_data = await market_data_fetcher.get_current_price(symbol)
                        await ws_manager.broadcast_to_symbol(symbol, {
                            "type": "price_update",
                            **price_data
                        })
                    except:
                        pass
            
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Price streaming error: {e}")
            await asyncio.sleep(10)


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Extended Cryptocurrency Server")
    asyncio.create_task(price_streaming_task())
    logger.info("✅ Server started")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down")
    for client_id in list(ws_manager.active_connections.keys()):
        ws_manager.disconnect(client_id)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🌟 Starting server on {host}:{port}")
    
    uvicorn.run(
        "crypto_server_extended:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
