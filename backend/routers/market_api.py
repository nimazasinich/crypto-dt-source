#!/usr/bin/env python3
"""
Market API Router - Implements cryptocurrency market endpoints
Handles GET /api/market/price, GET /api/market/ohlc, POST /api/sentiment/analyze, and WebSocket /ws
"""

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import json
import asyncio
import time
import httpx

# Import services
from backend.services.smart_multi_source_router import smart_router, get_price, get_ohlc  # NEW: Smart multi-source routing
from backend.services.binance_client import BinanceClient
from backend.services.ai_service_unified import UnifiedAIService
from backend.services.market_data_aggregator import market_data_aggregator
from backend.services.sentiment_aggregator import sentiment_aggregator
from backend.services.hf_dataset_aggregator import hf_dataset_aggregator

# DEPRECATED: Direct CoinGecko access (now using smart_router)
# from backend.services.coingecko_client import coingecko_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Market API"])

# WebSocket connection manager
class WebSocketManager:
    """Manages WebSocket connections and subscriptions"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, List[str]] = {}  # client_id -> [symbols]
        self.price_streams: Dict[str, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = []
        logger.info(f"WebSocket client {client_id} connected")
    
    async def disconnect(self, client_id: str):
        """Disconnect WebSocket client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
        if client_id in self.price_streams:
            self.price_streams[client_id].cancel()
            del self.price_streams[client_id]
        logger.info(f"WebSocket client {client_id} disconnected")
    
    async def subscribe(self, client_id: str, symbol: str):
        """Subscribe client to symbol updates"""
        if client_id not in self.subscriptions:
            self.subscriptions[client_id] = []
        if symbol.upper() not in self.subscriptions[client_id]:
            self.subscriptions[client_id].append(symbol.upper())
            logger.info(f"Client {client_id} subscribed to {symbol.upper()}")
    
    async def send_message(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                await self.disconnect(client_id)
    
    async def broadcast_to_subscribers(self, symbol: str, data: Dict[str, Any]):
        """Broadcast data to all clients subscribed to symbol"""
        symbol_upper = symbol.upper()
        for client_id, symbols in self.subscriptions.items():
            if symbol_upper in symbols:
                await self.send_message(client_id, data)

# Global WebSocket manager instance
ws_manager = WebSocketManager()

# Binance client instance
binance_client = BinanceClient()

# AI service instance
ai_service = UnifiedAIService()


# ============================================================================
# GET /api/market/price
# ============================================================================

@router.get("/api/market/price")
async def get_market_price(
    symbol: str = Query(..., description="Cryptocurrency symbol (e.g., BTC, ETH)")
):
    """
    Fetch the current market price of a specific cryptocurrency.
    Uses ALL free market data providers with intelligent fallback:
    CoinGecko, CoinPaprika, CoinCap, Binance, CoinLore, Messari, CoinStats
    
    Returns:
        - If symbol is valid: current price with timestamp
        - If symbol is invalid: 404 error
    """
    try:
        symbol_upper = symbol.upper()
        
        # Use market data aggregator with automatic fallback to ALL free providers
        price_data = await market_data_aggregator.get_price(symbol_upper)
        
        return {
            "symbol": price_data.get("symbol", symbol_upper),
            "price": price_data.get("price", 0),
            "source": price_data.get("source", "unknown"),
            "timestamp": price_data.get("timestamp", int(time.time() * 1000)) // 1000
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Error fetching price data: {str(e)}"
        )


# ============================================================================
# GET /api/market/ohlc
# ============================================================================

@router.get("/api/market/ohlc")
async def get_market_ohlc(
    symbol: str = Query(..., description="Cryptocurrency symbol (e.g., BTC, ETH)"),
    timeframe: str = Query("1h", description="Timeframe (1h, 4h, 1d)")
):
    """
    Fetch historical OHLC (Open, High, Low, Close) data for a cryptocurrency.
    Uses multiple sources with fallback:
    1. Binance Public API (real-time)
    2. HuggingFace Datasets (linxy/CryptoCoin - 26 symbols)
    3. HuggingFace Datasets (WinkingFace/CryptoLM - BTC, ETH, SOL, XRP)
    
    Returns:
        - If symbol and timeframe are valid: OHLC data array
        - If invalid: 404 error
    """
    try:
        symbol_upper = symbol.upper()
        
        # Validate timeframe
        valid_timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]
        if timeframe not in valid_timeframes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid timeframe '{timeframe}'. Valid timeframes: {', '.join(valid_timeframes)}"
            )
        
        # Try Binance first (real-time data)
        try:
            ohlcv_data = await binance_client.get_ohlcv(symbol_upper, timeframe, limit=100)
            
            if ohlcv_data and len(ohlcv_data) > 0:
                # Format response
                ohlc_list = []
                for item in ohlcv_data:
                    ohlc_list.append({
                        "open": item.get("open", 0),
                        "high": item.get("high", 0),
                        "low": item.get("low", 0),
                        "close": item.get("close", 0),
                        "volume": item.get("volume", 0),
                        "timestamp": item.get("timestamp", int(time.time()))
                    })
                
                logger.info(f"✅ Binance: Fetched OHLC for {symbol_upper}/{timeframe}")
                return {
                    "symbol": symbol_upper,
                    "timeframe": timeframe,
                    "ohlc": ohlc_list,
                    "source": "binance"
                }
        except Exception as e:
            logger.warning(f"⚠️ Binance failed for {symbol_upper}/{timeframe}: {e}")
        
        # Fallback to HuggingFace Datasets (historical data)
        try:
            hf_ohlcv_data = await hf_dataset_aggregator.get_ohlcv(symbol_upper, timeframe, limit=100)
            
            if hf_ohlcv_data and len(hf_ohlcv_data) > 0:
                # Format response
                ohlc_list = []
                for item in hf_ohlcv_data:
                    ohlc_list.append({
                        "open": item.get("open", 0),
                        "high": item.get("high", 0),
                        "low": item.get("low", 0),
                        "close": item.get("close", 0),
                        "timestamp": item.get("timestamp", int(time.time()))
                    })
                
                logger.info(f"✅ HuggingFace Datasets: Fetched OHLC for {symbol_upper}/{timeframe}")
                return {
                    "symbol": symbol_upper,
                    "timeframe": timeframe,
                    "ohlc": ohlc_list,
                    "source": "huggingface"
                }
        except Exception as e:
            logger.warning(f"⚠️ HuggingFace Datasets failed for {symbol_upper}/{timeframe}: {e}")

        # Fallback to CryptoCompare (public OHLCV)
        try:
            endpoint = "histohour"
            aggregate = 1
            limit = 100
            if timeframe == "4h":
                endpoint = "histohour"
                aggregate = 4
            elif timeframe == "1d":
                endpoint = "histoday"
                aggregate = 1
            elif timeframe == "1w":
                endpoint = "histoday"
                aggregate = 7

            url = f"https://min-api.cryptocompare.com/data/v2/{endpoint}"
            params = {"fsym": symbol_upper, "tsym": "USD", "limit": limit, "aggregate": aggregate}

            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                payload = resp.json()

            data = payload.get("Data", {}).get("Data", [])
            if isinstance(data, list) and data:
                ohlc_list = [
                    {
                        "open": item.get("open", 0),
                        "high": item.get("high", 0),
                        "low": item.get("low", 0),
                        "close": item.get("close", 0),
                        "volume": item.get("volumeto", item.get("volumefrom", 0)),
                        "timestamp": int(item.get("time", 0)) * 1000,
                    }
                    for item in data
                ]
                logger.info(f"✅ CryptoCompare: Fetched OHLC for {symbol_upper}/{timeframe}")
                return {"symbol": symbol_upper, "timeframe": timeframe, "ohlc": ohlc_list, "source": "cryptocompare"}
        except Exception as e:
            logger.warning(f"⚠️ CryptoCompare failed for {symbol_upper}/{timeframe}: {e}")
        
        # No data found from any source
        raise HTTPException(
            status_code=404,
            detail=f"No OHLC data found for symbol '{symbol}' with timeframe '{timeframe}' from any source (Binance, HuggingFace)"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching OHLC data: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Error fetching OHLC data: {str(e)}"
        )


# ============================================================================
# POST /api/sentiment/analyze
# ============================================================================

class SentimentAnalyzeRequest(BaseModel):
    """Request model for sentiment analysis"""
    text: str = Field(..., description="Text to analyze for sentiment", min_length=1)


@router.post("/api/sentiment/analyze")
async def analyze_sentiment(request: SentimentAnalyzeRequest):
    """
    Analyze the sentiment of a given text (Bullish, Bearish, Neutral).
    
    Returns:
        - If text is valid: sentiment analysis result
        - If text is missing or invalid: 400 error
    """
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Text parameter is required and cannot be empty"
            )
        
        # Use AI service for sentiment analysis
        try:
            result = await ai_service.analyze_sentiment(
                text=request.text,
                category="crypto",
                use_ensemble=True
            )
            
            # Map sentiment to required format
            label = result.get("label", "neutral").lower()
            confidence = result.get("confidence", 0.5)
            
            # Map label to sentiment
            if "bullish" in label or "positive" in label:
                sentiment = "Bullish"
                score = confidence if confidence > 0.5 else 0.6
            elif "bearish" in label or "negative" in label:
                sentiment = "Bearish"
                score = 1 - confidence if confidence < 0.5 else 0.4
            else:
                sentiment = "Neutral"
                score = 0.5
            
            return {
                "sentiment": sentiment,
                "score": score,
                "confidence": confidence
            }
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            # Fallback to simple keyword-based analysis
            text_lower = request.text.lower()
            positive_words = ['bullish', 'buy', 'moon', 'pump', 'up', 'gain', 'profit', 'good', 'great', 'strong']
            negative_words = ['bearish', 'sell', 'dump', 'down', 'loss', 'crash', 'bad', 'fear', 'weak', 'drop']
            
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                sentiment = "Bullish"
            elif neg_count > pos_count:
                sentiment = "Bearish"
            else:
                sentiment = "Neutral"
            
            return {
                "sentiment": sentiment,
                "score": 0.65 if sentiment == "Bullish" else (0.35 if sentiment == "Bearish" else 0.5),
                "confidence": 0.6
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Error analyzing sentiment: {str(e)}"
        )


# ============================================================================
# WebSocket /ws
# ============================================================================

async def stream_price_updates(client_id: str, symbol: str):
    """Stream price updates for a subscribed symbol - USES SMART MULTI-SOURCE ROUTING"""
    symbol_upper = symbol.upper()
    
    while client_id in ws_manager.active_connections:
        try:
            # Get current price using smart router (rotates through all sources)
            try:
                # Use smart router instead of direct CoinGecko
                price_data = await smart_router.get_market_data(symbol_upper, "price")
                price = price_data.get("price", 0)
            except Exception as e:
                logger.warning(f"Error fetching price for {symbol_upper} via smart router: {e}")
                # Emergency fallback to Binance direct
                try:
                    ticker = await binance_client.get_ticker(f"{symbol_upper}USDT")
                    price = float(ticker.get("lastPrice", 0)) if ticker else 0
                except:
                    price = 0
            
            # Send update to client
            await ws_manager.send_message(client_id, {
                "symbol": symbol_upper,
                "price": price,
                "timestamp": int(time.time())
            })
            
            # Wait 5 seconds before next update
            await asyncio.sleep(5)
        
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in price stream for {symbol_upper}: {e}")
            await asyncio.sleep(5)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time cryptocurrency data updates.
    
    Connection:
    - Clients connect to receive real-time data
    - Send subscription messages to subscribe to specific symbols
    
    Subscription Message:
    {
        "type": "subscribe",
        "symbol": "BTC"
    }
    
    Unsubscribe Message:
    {
        "type": "unsubscribe",
        "symbol": "BTC"
    }
    
    Ping Message:
    {
        "type": "ping"
    }
    """
    client_id = f"client_{int(time.time() * 1000)}_{id(websocket)}"
    
    try:
        await ws_manager.connect(websocket, client_id)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "message": "Connected to cryptocurrency data WebSocket",
            "timestamp": int(time.time())
        })
        
        # Handle incoming messages
        while True:
            try:
                # Receive message with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                try:
                    message = json.loads(data)
                    msg_type = message.get("type", "").lower()
                    
                    if msg_type == "subscribe":
                        symbol = message.get("symbol", "").upper()
                        if not symbol:
                            await websocket.send_json({
                                "type": "error",
                                "error": "Symbol is required for subscription",
                                "timestamp": int(time.time())
                            })
                            continue
                        
                        await ws_manager.subscribe(client_id, symbol)
                        
                        # Start price streaming task if not already running
                        task_key = f"{client_id}_{symbol}"
                        if task_key not in ws_manager.price_streams:
                            task = asyncio.create_task(stream_price_updates(client_id, symbol))
                            ws_manager.price_streams[task_key] = task
                        
                        await websocket.send_json({
                            "type": "subscribed",
                            "symbol": symbol,
                            "message": f"Subscribed to {symbol} updates",
                            "timestamp": int(time.time())
                        })
                    
                    elif msg_type == "unsubscribe":
                        symbol = message.get("symbol", "").upper()
                        if symbol in ws_manager.subscriptions.get(client_id, []):
                            ws_manager.subscriptions[client_id].remove(symbol)
                            task_key = f"{client_id}_{symbol}"
                            if task_key in ws_manager.price_streams:
                                ws_manager.price_streams[task_key].cancel()
                                del ws_manager.price_streams[task_key]
                        
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "symbol": symbol,
                            "message": f"Unsubscribed from {symbol} updates",
                            "timestamp": int(time.time())
                        })
                    
                    elif msg_type == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": int(time.time())
                        })
                    
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "error": f"Unknown message type: {msg_type}",
                            "timestamp": int(time.time())
                        })
                
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "error": "Invalid JSON format",
                        "timestamp": int(time.time())
                    })
            
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": int(time.time()),
                    "status": "alive"
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket client {client_id} disconnected normally")
        await ws_manager.disconnect(client_id)
    
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "error": f"Server error: {str(e)}",
                "timestamp": int(time.time())
            })
        except:
            pass
        await ws_manager.disconnect(client_id)
    
    finally:
        await ws_manager.disconnect(client_id)

