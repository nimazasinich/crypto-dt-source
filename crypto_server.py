#!/usr/bin/env python3
"""
Cryptocurrency Server - HTTP (GET, POST) and WebSocket Support
Implements comprehensive API endpoints for cryptocurrency data with real-time updates
"""

import asyncio
import logging
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Set
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
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request, status
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
    """Request model for sentiment analysis"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to analyze")


class SentimentAnalysisResponse(BaseModel):
    """Response model for sentiment analysis"""
    sentiment: str = Field(..., description="Detected sentiment (Bullish, Bearish, Neutral)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    keywords: Dict[str, int] = Field(default_factory=dict, description="Detected keywords")


class MarketPriceResponse(BaseModel):
    """Response model for market price"""
    symbol: str
    price: float
    timestamp: int
    source: str = "binance"


class OHLCDataPoint(BaseModel):
    """Single OHLC data point"""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class OHLCResponse(BaseModel):
    """Response model for OHLC data"""
    symbol: str
    timeframe: str
    ohlc: list[OHLCDataPoint]


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list[float]] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True
    
    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client"""
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
    """Manages WebSocket connections and subscriptions"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)  # {symbol: {client_ids}}
        self.client_subscriptions: Dict[str, Set[str]] = defaultdict(set)  # {client_id: {symbols}}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"✅ WebSocket client connected: {client_id} (Total: {len(self.active_connections)})")
    
    def disconnect(self, client_id: str):
        """Disconnect and clean up a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # Clean up subscriptions
        for symbol in self.client_subscriptions.get(client_id, set()).copy():
            self.unsubscribe(client_id, symbol)
        
        if client_id in self.client_subscriptions:
            del self.client_subscriptions[client_id]
        
        logger.info(f"❌ WebSocket client disconnected: {client_id} (Total: {len(self.active_connections)})")
    
    def subscribe(self, client_id: str, symbol: str):
        """Subscribe a client to a specific symbol"""
        self.subscriptions[symbol].add(client_id)
        self.client_subscriptions[client_id].add(symbol)
        logger.info(f"📡 Client {client_id} subscribed to {symbol}")
    
    def unsubscribe(self, client_id: str, symbol: str):
        """Unsubscribe a client from a specific symbol"""
        self.subscriptions[symbol].discard(client_id)
        self.client_subscriptions[client_id].discard(symbol)
        
        # Clean up empty sets
        if not self.subscriptions[symbol]:
            del self.subscriptions[symbol]
        
        logger.info(f"📴 Client {client_id} unsubscribed from {symbol}")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast_to_symbol(self, symbol: str, message: Dict[str, Any]):
        """Broadcast a message to all clients subscribed to a symbol"""
        disconnected = []
        
        for client_id in self.subscriptions.get(symbol, set()).copy():
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "total_subscriptions": sum(len(subs) for subs in self.subscriptions.values()),
            "symbols_tracked": list(self.subscriptions.keys())
        }


# ============================================================================
# SENTIMENT ANALYZER
# ============================================================================

class SentimentAnalyzer:
    """Simple keyword-based sentiment analyzer"""
    
    def __init__(self):
        self.bullish_keywords = {
            'bullish', 'bull', 'buy', 'moon', 'pump', 'surge', 'rally', 'gain', 'profit',
            'up', 'rise', 'growth', 'strong', 'breakthrough', 'milestone', 'success',
            'positive', 'uptrend', 'breakout', 'all-time high', 'ath', 'recovery'
        }
        
        self.bearish_keywords = {
            'bearish', 'bear', 'sell', 'dump', 'crash', 'drop', 'fall', 'decline', 'loss',
            'down', 'weak', 'correction', 'resistance', 'fear', 'panic', 'warning',
            'negative', 'downtrend', 'breakdown', 'support', 'capitulation'
        }
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        if not text:
            return {
                "sentiment": "Neutral",
                "confidence": 0.5,
                "keywords": {}
            }
        
        text_lower = text.lower()
        words = text_lower.split()
        
        # Count keyword occurrences
        bullish_count = sum(1 for word in words if any(kw in word for kw in self.bullish_keywords))
        bearish_count = sum(1 for word in words if any(kw in word for kw in self.bearish_keywords))
        
        total_keywords = bullish_count + bearish_count
        
        # Determine sentiment
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
            "keywords": {
                "bullish": bullish_count,
                "bearish": bearish_count,
                "total": total_keywords
            }
        }


# ============================================================================
# MARKET DATA FETCHER
# ============================================================================

class MarketDataFetcher:
    """Fetches real market data from external APIs"""
    
    def __init__(self):
        self.binance_base_url = "https://api.binance.com/api/v3"
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.timeout = 10.0
        
        self.timeframe_map = {
            "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w"
        }
    
    def _normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol to Binance format"""
        symbol = symbol.upper().strip()
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        return symbol
    
    async def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """Fetch current price for a symbol"""
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
                elif response.status_code == 400:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Symbol not found: {symbol}"
                    )
                else:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Binance API error: HTTP {response.status_code}"
                    )
        
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Request timeout - Binance API is not responding"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch price data: {str(e)}"
            )
    
    async def get_ohlc_data(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """Fetch OHLC data for a symbol"""
        binance_symbol = self._normalize_symbol(symbol)
        binance_interval = self.timeframe_map.get(timeframe, "1h")
        limit = min(limit, 1000)  # Binance max limit
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.binance_base_url}/klines",
                    params={
                        "symbol": binance_symbol,
                        "interval": binance_interval,
                        "limit": limit
                    }
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
                    
                    return {
                        "symbol": symbol.upper().replace("USDT", ""),
                        "timeframe": timeframe,
                        "ohlc": ohlc_data
                    }
                
                elif response.status_code == 400:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Invalid symbol or timeframe: {symbol} / {timeframe}"
                    )
                else:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Binance API error: HTTP {response.status_code}"
                    )
        
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Request timeout - Binance API is not responding"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching OHLC for {symbol}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch OHLC data: {str(e)}"
            )


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Cryptocurrency Data Server",
    description="HTTP (GET, POST) and WebSocket API for cryptocurrency data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
ws_manager = WebSocketConnectionManager()
sentiment_analyzer = SentimentAnalyzer()
market_data_fetcher = MarketDataFetcher()


# ============================================================================
# MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Skip rate limiting for health check
    if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Get client identifier
    client_id = request.client.host if request.client else "unknown"
    
    # Check rate limit
    if not rate_limiter.is_allowed(client_id):
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": "Too many requests. Please try again later.",
                "retry_after": 60
            }
        )
    
    # Add rate limit headers
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(rate_limiter.get_remaining(client_id))
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + rate_limiter.window_seconds))
    
    return response


# ============================================================================
# HTTP ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Cryptocurrency Data Server",
        "version": "1.0.0",
        "endpoints": {
            "price": "GET /api/market/price?symbol=BTC",
            "ohlc": "GET /api/market/ohlc?symbol=ETH&timeframe=1h",
            "sentiment": "POST /api/sentiment/analyze",
            "websocket": "WS /ws"
        },
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "websocket_connections": len(ws_manager.active_connections)
    }


@app.get("/api/market/price", response_model=MarketPriceResponse)
async def get_market_price(symbol: str):
    """
    Fetch the current market price of a specific cryptocurrency
    
    - **symbol**: Cryptocurrency symbol (e.g., BTC, ETH, BNB)
    
    Returns current price with timestamp
    """
    if not symbol or len(symbol) > 20:
        raise HTTPException(
            status_code=400,
            detail="Invalid symbol parameter"
        )
    
    try:
        result = await market_data_fetcher.get_current_price(symbol)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_market_price: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/api/market/ohlc", response_model=OHLCResponse)
async def get_market_ohlc(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 100
):
    """
    Fetch historical OHLC (Open, High, Low, Close) data
    
    - **symbol**: Cryptocurrency symbol (e.g., BTC, ETH)
    - **timeframe**: Time interval (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
    - **limit**: Number of data points (max 1000)
    
    Returns historical OHLC data
    """
    if not symbol or len(symbol) > 20:
        raise HTTPException(
            status_code=400,
            detail="Invalid symbol parameter"
        )
    
    if timeframe not in ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid timeframe: {timeframe}. Must be one of: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w"
        )
    
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 1000"
        )
    
    try:
        result = await market_data_fetcher.get_ohlc_data(symbol, timeframe, limit)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_market_ohlc: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.post("/api/sentiment/analyze", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(request: SentimentAnalysisRequest):
    """
    Analyze the sentiment of a given text
    
    - **text**: Text to analyze for sentiment (Bullish, Bearish, Neutral)
    
    Returns sentiment analysis result
    """
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )
    
    try:
        result = sentiment_analyzer.analyze(request.text)
        return result
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze sentiment"
        )


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time cryptocurrency data updates
    
    Clients can send subscription messages:
    ```json
    {
        "type": "subscribe",
        "symbol": "BTC"
    }
    ```
    
    Server will stream real-time price updates:
    ```json
    {
        "symbol": "BTC",
        "price": 50000.50,
        "timestamp": 1633659200,
        "type": "price_update"
    }
    ```
    """
    client_id = str(uuid.uuid4())
    
    try:
        await ws_manager.connect(websocket, client_id)
        
        # Send welcome message
        await ws_manager.send_personal_message({
            "type": "connected",
            "client_id": client_id,
            "message": "Connected to cryptocurrency data stream",
            "timestamp": datetime.utcnow().isoformat()
        }, client_id)
        
        # Message handling loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "subscribe":
                    symbol = data.get("symbol", "").upper()
                    
                    if not symbol:
                        await ws_manager.send_personal_message({
                            "type": "error",
                            "error": "Symbol is required for subscription"
                        }, client_id)
                        continue
                    
                    # Subscribe to symbol
                    ws_manager.subscribe(client_id, symbol)
                    
                    # Send confirmation
                    await ws_manager.send_personal_message({
                        "type": "subscribed",
                        "symbol": symbol,
                        "message": f"Subscribed to {symbol} updates"
                    }, client_id)
                    
                    # Send initial price
                    try:
                        price_data = await market_data_fetcher.get_current_price(symbol)
                        await ws_manager.send_personal_message({
                            "type": "price_update",
                            **price_data
                        }, client_id)
                    except Exception as e:
                        await ws_manager.send_personal_message({
                            "type": "error",
                            "error": f"Failed to fetch price for {symbol}: {str(e)}"
                        }, client_id)
                
                elif message_type == "unsubscribe":
                    symbol = data.get("symbol", "").upper()
                    
                    if symbol:
                        ws_manager.unsubscribe(client_id, symbol)
                        await ws_manager.send_personal_message({
                            "type": "unsubscribed",
                            "symbol": symbol,
                            "message": f"Unsubscribed from {symbol} updates"
                        }, client_id)
                
                elif message_type == "ping":
                    await ws_manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, client_id)
                
                elif message_type == "get_subscriptions":
                    subscriptions = list(ws_manager.client_subscriptions.get(client_id, set()))
                    await ws_manager.send_personal_message({
                        "type": "subscriptions",
                        "subscriptions": subscriptions
                    }, client_id)
                
                else:
                    await ws_manager.send_personal_message({
                        "type": "error",
                        "error": f"Unknown message type: {message_type}"
                    }, client_id)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await ws_manager.send_personal_message({
                    "type": "error",
                    "error": "Failed to process message"
                }, client_id)
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        ws_manager.disconnect(client_id)


# ============================================================================
# BACKGROUND TASK: PRICE STREAMING
# ============================================================================

async def price_streaming_task():
    """Background task to stream price updates to subscribed clients"""
    logger.info("🔄 Starting price streaming background task")
    
    while True:
        try:
            # Get all symbols that have active subscriptions
            symbols = list(ws_manager.subscriptions.keys())
            
            if symbols:
                # Fetch prices for all subscribed symbols
                for symbol in symbols:
                    try:
                        price_data = await market_data_fetcher.get_current_price(symbol)
                        
                        # Broadcast to subscribers
                        await ws_manager.broadcast_to_symbol(symbol, {
                            "type": "price_update",
                            **price_data
                        })
                    except Exception as e:
                        logger.error(f"Error fetching price for {symbol}: {e}")
            
            # Wait before next update (5 seconds)
            await asyncio.sleep(5)
        
        except asyncio.CancelledError:
            logger.info("Price streaming task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in price streaming task: {e}")
            await asyncio.sleep(10)


@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    logger.info("🚀 Starting Cryptocurrency Data Server")
    
    # Start price streaming task
    asyncio.create_task(price_streaming_task())
    
    logger.info("✅ Server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("🛑 Shutting down server")
    
    # Disconnect all WebSocket clients
    for client_id in list(ws_manager.active_connections.keys()):
        ws_manager.disconnect(client_id)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import os
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🌟 Starting server on {host}:{port}")
    logger.info("📚 API Documentation available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "crypto_server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
