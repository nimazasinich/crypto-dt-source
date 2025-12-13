# 🚀 Hugging Face Space Deployment & Update Request

**Project:** Dreammaker Crypto Trading Platform  
**Request Type:** Space Update & API Enhancement  
**Priority:** HIGH  
**Date:** December 5, 2025

---

## 📋 EXECUTIVE SUMMARY

This is an **UPDATE REQUEST** for our existing Hugging Face Space to become the **single source of truth** for all data requirements of the Dreammaker Crypto Platform. We need to consolidate all data APIs into one unified Hugging Face Space endpoint to implement our new Data Highway Architecture.

**Current Issue:** Data requests are scattered across 60+ files using multiple external APIs (Binance, CoinGecko, NewsAPI, etc.)

**Goal:** Centralize ALL data fetching through a single Hugging Face Space with comprehensive API endpoints.

---

## 🎯 REQUIREMENTS OVERVIEW

### What We Need:

1. ✅ **Update existing HF Space** (not create new)
2. ✅ **Deploy comprehensive FastAPI backend** with all endpoints
3. ✅ **Implement data aggregation** from multiple sources
4. ✅ **Add caching layer** for performance
5. ✅ **Provide real-time WebSocket** support
6. ✅ **Include AI/ML models** for predictions
7. ✅ **Comprehensive error handling** and fallbacks

### What Should Be Available:

```
📡 ALL data requests should be served from:
https://[YOUR-SPACE-NAME].hf.space/api/*

Currently supported endpoints:
✅ /api/market (working)
✅ /api/ohlcv (working)
✅ /api/news/latest (working)
✅ /api/sentiment/global (working)
✅ /api/stats (working)
✅ /api/ai/signals (working)

🆕 NEW endpoints needed (see detailed specs below)
```

---

## 🏗️ DETAILED API SPECIFICATIONS

### 1. Market Data Endpoints

#### 1.1 GET `/api/market`
**Purpose:** Get list of top cryptocurrencies with current prices and stats

**Query Parameters:**
```typescript
{
  limit?: number;        // Default: 100, Max: 500
  sort?: string;         // Options: 'rank' | 'volume' | 'price_change'
  currency?: string;     // Default: 'usd'
  category?: string;     // Options: 'all' | 'defi' | 'nft' | 'meme'
}
```

**Response Format:**
```json
{
  "success": true,
  "timestamp": 1733432100000,
  "last_updated": "2025-12-05T20:30:00Z",
  "items": [
    {
      "symbol": "BTC",
      "name": "Bitcoin",
      "rank": 1,
      "price": 42150.25,
      "change_24h": 2.34,
      "change_7d": 5.67,
      "volume_24h": 28500000000,
      "market_cap": 825000000000,
      "circulating_supply": 19500000,
      "total_supply": 21000000,
      "ath": 69000,
      "ath_date": "2021-11-10",
      "atl": 67.81,
      "atl_date": "2013-07-06",
      "last_updated": "2025-12-05T20:30:00Z"
    }
  ]
}
```

**Data Sources (in priority order):**
1. CoinGecko API (primary)
2. Binance API (fallback)
3. CoinMarketCap API (fallback)

---

#### 1.2 GET `/api/price/{symbol}`
**Purpose:** Get current price for a specific symbol

**Path Parameters:**
- `symbol`: String (e.g., "BTC", "ETH", "BTC/USDT")

**Query Parameters:**
```typescript
{
  convert?: string;      // Default: 'usd'
  include_24h?: boolean; // Include 24h stats, Default: true
}
```

**Response Format:**
```json
{
  "success": true,
  "symbol": "BTC",
  "price": 42150.25,
  "change_24h": 2.34,
  "high_24h": 42800.50,
  "low_24h": 40950.00,
  "volume_24h": 28500000000,
  "timestamp": 1733432100000
}
```

---

#### 1.3 GET `/api/ohlcv`
**Purpose:** Get OHLCV (candlestick) data for charting

**Query Parameters:**
```typescript
{
  symbol: string;        // REQUIRED: "BTC/USDT"
  timeframe: string;     // REQUIRED: "1m" | "5m" | "15m" | "1h" | "4h" | "1d" | "1w"
  limit?: number;        // Default: 100, Max: 1000
  since?: number;        // Unix timestamp (ms)
  until?: number;        // Unix timestamp (ms)
}
```

**Response Format:**
```json
{
  "success": true,
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "data": [
    {
      "t": 1733428800000,
      "o": 42100.50,
      "h": 42250.75,
      "l": 42050.25,
      "c": 42150.25,
      "v": 125.45
    }
  ]
}
```

**Data Sources:**
1. Binance API (primary)
2. KuCoin API (fallback)
3. CoinGecko API (fallback, limited timeframes)

---

#### 1.4 GET `/api/ticker/{symbol}`
**Purpose:** Get real-time ticker data

**Response Format:**
```json
{
  "success": true,
  "symbol": "BTC/USDT",
  "bid": 42148.50,
  "ask": 42151.25,
  "last": 42150.25,
  "volume": 28500000000,
  "timestamp": 1733432100000
}
```

---

### 2. News & Sentiment Endpoints

#### 2.1 GET `/api/news/latest`
**Purpose:** Get latest cryptocurrency news

**Query Parameters:**
```typescript
{
  limit?: number;        // Default: 10, Max: 100
  category?: string;     // Options: 'all' | 'bitcoin' | 'ethereum' | 'defi' | 'nft'
  language?: string;     // Default: 'en'
  sentiment?: string;    // Filter by: 'positive' | 'negative' | 'neutral'
}
```

**Response Format:**
```json
{
  "success": true,
  "total": 150,
  "news": [
    {
      "id": "news_12345",
      "title": "Bitcoin Reaches New All-Time High",
      "url": "https://example.com/news/btc-ath",
      "source": "CoinDesk",
      "published_at": "2025-12-05T20:15:00Z",
      "sentiment": "positive",
      "sentiment_score": 0.85,
      "summary": "Bitcoin has surged past $42,000 marking a new milestone...",
      "image_url": "https://example.com/image.jpg",
      "tags": ["bitcoin", "price", "ath"],
      "related_symbols": ["BTC", "ETH"]
    }
  ]
}
```

**Data Sources:**
1. CryptoPanic API
2. NewsAPI.org
3. RSS Feeds (CoinDesk, CoinTelegraph, Decrypt)
4. Twitter API (crypto influencers)

---

#### 2.2 GET `/api/sentiment/global`
**Purpose:** Get global crypto market sentiment

**Response Format:**
```json
{
  "success": true,
  "timestamp": 1733432100000,
  "fearGreedIndex": 65,
  "sentiment": "greed",
  "value_classification": "Greed",
  "components": {
    "volatility": 25,
    "market_momentum": 75,
    "social_media": 60,
    "surveys": 50,
    "dominance": 70,
    "trends": 80
  },
  "description": "Market is showing signs of greed",
  "last_updated": "2025-12-05T20:00:00Z"
}
```

**Data Sources:**
1. Alternative.me Fear & Greed Index
2. Custom sentiment analysis (social media)
3. On-chain metrics

---

#### 2.3 GET `/api/sentiment/symbol/{symbol}`
**Purpose:** Get sentiment for specific cryptocurrency

**Response Format:**
```json
{
  "success": true,
  "symbol": "BTC",
  "sentiment_score": 0.72,
  "sentiment": "positive",
  "social_volume": 15000,
  "social_dominance": 45.2,
  "news_sentiment": 0.68,
  "twitter_sentiment": 0.75,
  "reddit_sentiment": 0.70,
  "timestamp": 1733432100000
}
```

---

### 3. Trading & Portfolio Endpoints

#### 3.1 GET `/api/exchange-info`
**Purpose:** Get available trading pairs and exchange information

**Response Format:**
```json
{
  "success": true,
  "exchange": "binance",
  "symbols": [
    {
      "symbol": "BTC/USDT",
      "base": "BTC",
      "quote": "USDT",
      "active": true,
      "min_amount": 0.0001,
      "max_amount": 9000,
      "min_price": 0.01,
      "max_price": 1000000,
      "maker_fee": 0.001,
      "taker_fee": 0.001
    }
  ]
}
```

---

#### 3.2 GET `/api/orderbook/{symbol}`
**Purpose:** Get order book depth

**Query Parameters:**
```typescript
{
  limit?: number;        // Default: 20, Max: 100
}
```

**Response Format:**
```json
{
  "success": true,
  "symbol": "BTC/USDT",
  "timestamp": 1733432100000,
  "bids": [
    [42150.25, 1.5],
    [42149.50, 2.3]
  ],
  "asks": [
    [42151.75, 1.2],
    [42152.50, 3.1]
  ]
}
```

---

#### 3.3 GET `/api/trades/{symbol}`
**Purpose:** Get recent trades

**Query Parameters:**
```typescript
{
  limit?: number;        // Default: 50, Max: 500
  since?: number;        // Unix timestamp (ms)
}
```

**Response Format:**
```json
{
  "success": true,
  "symbol": "BTC/USDT",
  "trades": [
    {
      "id": "12345678",
      "timestamp": 1733432100000,
      "price": 42150.25,
      "amount": 0.5,
      "side": "buy",
      "type": "market"
    }
  ]
}
```

---

### 4. AI & Prediction Endpoints

#### 4.1 GET `/api/ai/signals`
**Purpose:** Get AI-generated trading signals

**Query Parameters:**
```typescript
{
  symbol?: string;       // Optional filter by symbol
  timeframe?: string;    // "1h" | "4h" | "1d"
  min_confidence?: number; // Filter by confidence (0-1)
  limit?: number;        // Default: 10, Max: 100
}
```

**Response Format:**
```json
{
  "success": true,
  "timestamp": 1733432100000,
  "signals": [
    {
      "id": "signal_12345",
      "symbol": "BTC/USDT",
      "type": "buy",
      "confidence": 0.85,
      "score": 8.5,
      "timeframe": "1h",
      "entry_price": 42150.25,
      "target_price": 43500.00,
      "stop_loss": 41000.00,
      "risk_reward": 3.2,
      "model": "ensemble_v3",
      "reasoning": [
        "Strong bullish momentum on 1h timeframe",
        "RSI showing oversold recovery",
        "Volume spike indicating accumulation"
      ],
      "indicators": {
        "rsi": 65,
        "macd": "bullish_crossover",
        "volume_profile": "accumulation"
      },
      "timestamp": 1733432100000,
      "expires_at": 1733435700000
    }
  ]
}
```

**ML Models Required:**
1. Price prediction model (LSTM/Transformer)
2. Sentiment analysis model (BERT/FinBERT)
3. Pattern recognition model (CNN)
4. Ensemble model combining all

---

#### 4.2 POST `/api/ai/predict`
**Purpose:** Get price prediction for specific symbol

**Request Body:**
```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "horizon": 24,
  "model": "ensemble"
}
```

**Response Format:**
```json
{
  "success": true,
  "symbol": "BTC/USDT",
  "current_price": 42150.25,
  "predictions": [
    {
      "timestamp": 1733432100000,
      "price": 42250.50,
      "confidence": 0.82,
      "lower_bound": 41900.00,
      "upper_bound": 42600.00
    }
  ],
  "model": "ensemble_v3",
  "confidence": 0.82,
  "direction": "bullish",
  "timestamp": 1733432100000
}
```

---

#### 4.3 GET `/api/ai/analysis/{symbol}`
**Purpose:** Get comprehensive AI analysis

**Response Format:**
```json
{
  "success": true,
  "symbol": "BTC/USDT",
  "analysis": {
    "technical": {
      "trend": "bullish",
      "strength": 7.5,
      "support_levels": [41000, 40500, 40000],
      "resistance_levels": [42500, 43000, 43500],
      "key_indicators": {
        "rsi_14": 65,
        "macd": "bullish",
        "moving_averages": "golden_cross",
        "volume": "increasing"
      }
    },
    "fundamental": {
      "market_cap_rank": 1,
      "dominance": 45.2,
      "on_chain_metrics": {
        "active_addresses": "increasing",
        "transaction_volume": "high",
        "exchange_netflow": "negative"
      }
    },
    "sentiment": {
      "overall": "positive",
      "score": 0.72,
      "social_volume": 15000,
      "news_sentiment": 0.68
    },
    "prediction": {
      "short_term": "bullish",
      "medium_term": "neutral",
      "long_term": "bullish",
      "confidence": 0.75
    }
  },
  "timestamp": 1733432100000
}
```

---

### 5. Blockchain & On-Chain Endpoints

#### 5.1 GET `/api/blockchain/transactions/{address}`
**Purpose:** Get transaction history for address

**Query Parameters:**
```typescript
{
  chain?: string;        // "ethereum" | "bsc" | "polygon"
  limit?: number;        // Default: 50, Max: 100
  offset?: number;       // For pagination
}
```

**Response Format:**
```json
{
  "success": true,
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "chain": "ethereum",
  "transactions": [
    {
      "hash": "0x...",
      "timestamp": 1733432100000,
      "from": "0x...",
      "to": "0x...",
      "value": 1.5,
      "token": "ETH",
      "status": "success",
      "gas_used": 21000,
      "gas_price": 50
    }
  ]
}
```

---

#### 5.2 GET `/api/blockchain/whale-alerts`
**Purpose:** Get large transaction alerts (whale activity)

**Query Parameters:**
```typescript
{
  min_value?: number;    // Minimum USD value, Default: 1000000
  chain?: string;        // Filter by blockchain
  limit?: number;        // Default: 20
}
```

**Response Format:**
```json
{
  "success": true,
  "alerts": [
    {
      "id": "whale_12345",
      "timestamp": 1733432100000,
      "hash": "0x...",
      "from": "0x... (Binance)",
      "to": "0x... (Unknown Wallet)",
      "amount": 1500,
      "token": "BTC",
      "usd_value": 63225375,
      "chain": "bitcoin",
      "type": "exchange_outflow"
    }
  ]
}
```

---

### 6. Market Statistics & Metrics

#### 6.1 GET `/api/stats`
**Purpose:** Get global market statistics

**Response Format:**
```json
{
  "success": true,
  "timestamp": 1733432100000,
  "global": {
    "total_market_cap": 1650000000000,
    "total_volume_24h": 85000000000,
    "bitcoin_dominance": 45.2,
    "ethereum_dominance": 18.5,
    "defi_dominance": 6.8,
    "market_cap_change_24h": 2.5,
    "volume_change_24h": 15.3,
    "active_cryptocurrencies": 12500,
    "active_markets": 45000,
    "active_exchanges": 680
  },
  "top_gainers": [
    {
      "symbol": "XYZ",
      "change_24h": 45.5,
      "volume_24h": 1500000000
    }
  ],
  "top_losers": [
    {
      "symbol": "ABC",
      "change_24h": -25.3,
      "volume_24h": 800000000
    }
  ]
}
```

---

#### 6.2 GET `/api/stats/dominance`
**Purpose:** Get market dominance breakdown

**Response Format:**
```json
{
  "success": true,
  "timestamp": 1733432100000,
  "dominance": {
    "BTC": 45.2,
    "ETH": 18.5,
    "BNB": 4.2,
    "XRP": 2.8,
    "ADA": 1.5,
    "others": 27.8
  }
}
```

---

### 7. Historical Data Endpoints

#### 7.1 GET `/api/history/price/{symbol}`
**Purpose:** Get historical price data

**Query Parameters:**
```typescript
{
  from: number;          // REQUIRED: Unix timestamp (ms)
  to: number;            // REQUIRED: Unix timestamp (ms)
  interval?: string;     // "1h" | "1d" | "1w" | "1M"
}
```

**Response Format:**
```json
{
  "success": true,
  "symbol": "BTC",
  "interval": "1d",
  "data": [
    {
      "timestamp": 1733432100000,
      "price": 42150.25,
      "volume": 28500000000,
      "market_cap": 825000000000
    }
  ]
}
```

---

### 8. WebSocket Real-Time Endpoints

#### 8.1 WebSocket `/ws/ticker`
**Purpose:** Real-time price updates

**Subscribe Message:**
```json
{
  "action": "subscribe",
  "channel": "ticker",
  "symbols": ["BTC/USDT", "ETH/USDT"]
}
```

**Update Message:**
```json
{
  "channel": "ticker",
  "data": {
    "symbol": "BTC/USDT",
    "price": 42150.25,
    "change_24h": 2.34,
    "volume_24h": 28500000000,
    "timestamp": 1733432100000
  }
}
```

---

#### 8.2 WebSocket `/ws/trades`
**Purpose:** Real-time trade stream

**Subscribe Message:**
```json
{
  "action": "subscribe",
  "channel": "trades",
  "symbols": ["BTC/USDT"]
}
```

**Trade Message:**
```json
{
  "channel": "trades",
  "data": {
    "symbol": "BTC/USDT",
    "price": 42150.25,
    "amount": 0.5,
    "side": "buy",
    "timestamp": 1733432100000
  }
}
```

---

## 🔧 TECHNICAL REQUIREMENTS

### 1. Backend Framework
```python
# Recommended: FastAPI + Python 3.9+
# File: app.py

from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
from typing import Optional, List
import aioredis

app = FastAPI(
    title="Dreammaker Crypto API",
    description="Unified cryptocurrency data API",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for caching
redis = aioredis.from_url("redis://localhost")

# Example endpoint
@app.get("/api/market")
async def get_market_data(
    limit: int = Query(100, ge=1, le=500),
    sort: Optional[str] = Query("rank"),
    currency: str = Query("usd")
):
    # Check cache first
    cache_key = f"market:{limit}:{sort}:{currency}"
    cached = await redis.get(cache_key)
    
    if cached:
        return JSONResponse(content=cached)
    
    # Fetch from data sources
    data = await fetch_from_coingecko(limit, sort, currency)
    
    # Cache for 60 seconds
    await redis.setex(cache_key, 60, data)
    
    return JSONResponse(content=data)
```

---

### 2. Data Sources Integration

```python
# File: data_sources.py

import aiohttp
from typing import Dict, List, Any

class DataSourceManager:
    def __init__(self):
        self.sources = {
            'coingecko': CoinGeckoAPI(),
            'binance': BinanceAPI(),
            'newsapi': NewsAPI(),
            'cryptopanic': CryptoPanicAPI(),
            'alternative_me': AlternativeMeAPI()
        }
    
    async def fetch_with_fallback(
        self, 
        source_priority: List[str],
        endpoint: str,
        params: Dict[str, Any]
    ):
        """Fetch data with automatic fallback"""
        for source_name in source_priority:
            try:
                source = self.sources[source_name]
                data = await source.fetch(endpoint, params)
                return data
            except Exception as e:
                logger.warning(f"{source_name} failed: {e}")
                continue
        
        raise Exception("All data sources failed")

class CoinGeckoAPI:
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    async def fetch_market_data(self, limit: int = 100):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": limit,
                    "sparkline": False
                }
            ) as response:
                return await response.json()

class BinanceAPI:
    BASE_URL = "https://api.binance.com/api/v3"
    
    async def fetch_ohlcv(self, symbol: str, interval: str, limit: int):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/klines",
                params={
                    "symbol": symbol.replace("/", ""),
                    "interval": interval,
                    "limit": limit
                }
            ) as response:
                data = await response.json()
                return self.transform_ohlcv(data)
    
    def transform_ohlcv(self, raw_data):
        return [
            {
                "t": item[0],
                "o": float(item[1]),
                "h": float(item[2]),
                "l": float(item[3]),
                "c": float(item[4]),
                "v": float(item[5])
            }
            for item in raw_data
        ]
```

---

### 3. Caching Strategy

```python
# File: cache.py

from functools import wraps
import aioredis
import json
from typing import Callable, Optional

class CacheManager:
    def __init__(self):
        self.redis = aioredis.from_url("redis://localhost")
        self.default_ttl = {
            'price': 5,           # 5 seconds
            'ohlcv': 60,          # 1 minute
            'market': 60,         # 1 minute
            'news': 300,          # 5 minutes
            'sentiment': 600,     # 10 minutes
            'ai_signals': 120,    # 2 minutes
            'stats': 300,         # 5 minutes
        }
    
    def cached(self, ttl: Optional[int] = None, key_prefix: str = ""):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
                
                # Try to get from cache
                cached_data = await self.redis.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                cache_ttl = ttl or self.default_ttl.get(key_prefix, 60)
                await self.redis.setex(
                    cache_key, 
                    cache_ttl, 
                    json.dumps(result)
                )
                
                return result
            
            return wrapper
        return decorator

# Usage
cache = CacheManager()

@cache.cached(ttl=60, key_prefix="market")
async def get_market_data(limit: int):
    # Fetch from API
    pass
```

---

### 4. Rate Limiting

```python
# File: rate_limiter.py

from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class RateLimiter:
    def __init__(self):
        self.limits = {
            'coingecko': (50, 60),      # 50 requests per minute
            'binance': (1200, 60),      # 1200 requests per minute
            'newsapi': (100, 86400),    # 100 requests per day
            'cryptopanic': (500, 86400), # 500 requests per day
        }
        self.counters = defaultdict(list)
    
    async def wait_if_needed(self, source: str):
        """Wait if rate limit is reached"""
        max_requests, window = self.limits.get(source, (60, 60))
        now = datetime.now()
        
        # Clean old timestamps
        self.counters[source] = [
            ts for ts in self.counters[source]
            if (now - ts).total_seconds() < window
        ]
        
        # Check if limit reached
        if len(self.counters[source]) >= max_requests:
            oldest = min(self.counters[source])
            wait_time = window - (now - oldest).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # Add current request
        self.counters[source].append(now)
```

---

### 5. AI/ML Models Integration

```python
# File: ai_models.py

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

class AIModelManager:
    def __init__(self):
        # Load sentiment analysis model
        self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
            "ElKulako/cryptobert"
        )
        self.sentiment_tokenizer = AutoTokenizer.from_pretrained(
            "ElKulako/cryptobert"
        )
        
        # Load price prediction model
        self.price_model = self.load_price_model()
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        inputs = self.sentiment_tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True,
            max_length=512
        )
        
        with torch.no_grad():
            outputs = self.sentiment_model(**inputs)
            scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Convert to sentiment
        labels = ['negative', 'neutral', 'positive']
        sentiment_idx = scores.argmax().item()
        confidence = scores[0][sentiment_idx].item()
        
        return {
            'sentiment': labels[sentiment_idx],
            'confidence': confidence,
            'scores': {
                'negative': scores[0][0].item(),
                'neutral': scores[0][1].item(),
                'positive': scores[0][2].item()
            }
        }
    
    async def predict_price(
        self, 
        symbol: str, 
        historical_data: np.ndarray,
        horizon: int = 24
    ) -> Dict[str, Any]:
        """Predict future prices"""
        # Preprocess data
        features = self.preprocess_data(historical_data)
        
        # Make prediction
        with torch.no_grad():
            predictions = self.price_model(features)
        
        return {
            'predictions': predictions.tolist(),
            'confidence': self.calculate_confidence(predictions),
            'direction': 'bullish' if predictions[-1] > features[-1] else 'bearish'
        }
    
    async def generate_signals(self, symbol: str) -> List[Dict[str, Any]]:
        """Generate trading signals"""
        # Fetch historical data
        ohlcv = await fetch_ohlcv(symbol, '1h', 100)
        
        # Calculate technical indicators
        indicators = self.calculate_indicators(ohlcv)
        
        # Analyze sentiment
        news = await fetch_news(symbol)
        sentiment = await self.analyze_bulk_sentiment(news)
        
        # Generate signal
        signal = self.ensemble_signal(indicators, sentiment)
        
        return signal
```

---

### 6. WebSocket Implementation

```python
# File: websocket.py

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
    
    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
    
    async def broadcast(self, channel: str, message: dict):
        if channel in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.add(connection)
            
            # Remove dead connections
            self.active_connections[channel] -= dead_connections

manager = ConnectionManager()

@app.websocket("/ws/ticker")
async def websocket_ticker(websocket: WebSocket):
    await manager.connect(websocket, "ticker")
    try:
        # Send initial data
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "channels": ["ticker"]
        })
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_json()
            
            if data.get("action") == "subscribe":
                symbols = data.get("symbols", [])
                # Subscribe to specific symbols
                await subscribe_to_symbols(websocket, symbols)
            
            elif data.get("action") == "unsubscribe":
                symbols = data.get("symbols", [])
                await unsubscribe_from_symbols(websocket, symbols)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, "ticker")

# Background task to broadcast updates
async def broadcast_ticker_updates():
    """Broadcast ticker updates every second"""
    while True:
        try:
            # Fetch latest prices
            prices = await fetch_all_prices()
            
            # Broadcast to all connected clients
            await manager.broadcast("ticker", {
                "channel": "ticker",
                "data": prices,
                "timestamp": int(datetime.now().timestamp() * 1000)
            })
            
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Broadcast error: {e}")
```

---

## 📦 DEPLOYMENT CONFIGURATION

### 1. requirements.txt
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
aiohttp==3.9.0
aioredis==2.0.1
python-multipart==0.0.6
pydantic==2.5.0
python-dotenv==1.0.0
pandas==2.1.3
numpy==1.26.2
torch==2.1.1
transformers==4.35.2
ccxt==4.1.60
websockets==12.0
asyncpg==0.29.0
sqlalchemy==2.0.23
alembic==1.12.1
celery==5.3.4
redis==5.0.1
```

---

### 2. Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 7860

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

### 3. Environment Variables (.env)
```bash
# API Keys
COINGECKO_API_KEY=your_key_here
BINANCE_API_KEY=your_key_here
BINANCE_SECRET_KEY=your_secret_here
NEWSAPI_KEY=your_key_here
CRYPTOPANIC_KEY=your_key_here
CMC_API_KEY=your_key_here

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Database (optional for persistent storage)
DATABASE_URL=postgresql://user:pass@localhost:5432/crypto_db

# HuggingFace
HF_TOKEN=your_hf_token_here

# Application Settings
CACHE_TTL_DEFAULT=60
MAX_WORKERS=4
DEBUG=false
```

---

### 4. HuggingFace Space Configuration

**README.md for Space:**
```markdown
---
title: Dreammaker Crypto API
emoji: 🚀
colorFrom: purple
colorTo: blue
sdk: docker
pinned: true
app_port: 7860
---

# Dreammaker Crypto Trading API

Unified cryptocurrency data API providing:
- Real-time market data
- OHLCV charts
- News & sentiment analysis
- AI trading signals
- WebSocket real-time streams

## API Documentation

Access interactive API docs at: https://[your-space].hf.space/docs

## Endpoints

- GET /api/market - Market data
- GET /api/ohlcv - Chart data
- GET /api/news/latest - Latest news
- GET /api/sentiment/global - Market sentiment
- GET /api/ai/signals - AI signals
- WS /ws/ticker - Real-time prices

## Authentication

Some endpoints require Bearer token authentication.
```

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Create/Update HuggingFace Space

```bash
# Clone your existing space or create new one
git clone https://huggingface.co/spaces/[YOUR-USERNAME]/[SPACE-NAME]
cd [SPACE-NAME]

# Add all files
cp -r /path/to/api/* .

# Commit and push
git add .
git commit -m "🚀 Update: Complete API with all endpoints"
git push
```

---

### Step 2: Configure Secrets

In HuggingFace Space Settings → Repository secrets, add:

```
COINGECKO_API_KEY=xxx
BINANCE_API_KEY=xxx
BINANCE_SECRET_KEY=xxx
NEWSAPI_KEY=xxx
CRYPTOPANIC_KEY=xxx
CMC_API_KEY=xxx
HF_TOKEN=xxx
REDIS_URL=redis://localhost:6379
```

---

### Step 3: Test Deployment

```bash
# Test locally first
docker build -t crypto-api .
docker run -p 7860:7860 --env-file .env crypto-api

# Test endpoints
curl http://localhost:7860/api/market?limit=10
curl http://localhost:7860/api/ohlcv?symbol=BTC/USDT&timeframe=1h
curl http://localhost:7860/api/news/latest?limit=5
```

---

### Step 4: Monitor & Verify

After deployment, verify all endpoints:

✅ GET https://[your-space].hf.space/api/market  
✅ GET https://[your-space].hf.space/api/ohlcv  
✅ GET https://[your-space].hf.space/api/news/latest  
✅ GET https://[your-space].hf.space/api/sentiment/global  
✅ GET https://[your-space].hf.space/api/ai/signals  
✅ WS wss://[your-space].hf.space/ws/ticker  

---

## 📊 PERFORMANCE REQUIREMENTS

### 1. Response Times
- Price endpoints: < 100ms
- Market data: < 500ms
- News/Sentiment: < 1s
- AI predictions: < 2s

### 2. Caching
- Prices: 5 seconds TTL
- OHLCV: 60 seconds TTL
- News: 5 minutes TTL
- AI signals: 2 minutes TTL

### 3. Rate Limiting
- Per IP: 100 requests/minute
- Per API key: 1000 requests/minute

### 4. WebSocket
- Max connections: 1000
- Heartbeat interval: 30s
- Reconnect timeout: 60s

---

## ✅ VERIFICATION CHECKLIST

After deployment, verify:

- [ ] All API endpoints return valid JSON
- [ ] CORS is properly configured
- [ ] Error responses follow standard format
- [ ] Caching is working (check response times)
- [ ] Rate limiting is enforced
- [ ] WebSocket connections work
- [ ] AI models are loaded and responding
- [ ] Data sources have proper fallbacks
- [ ] Logs are being generated
- [ ] Health check endpoint `/health` works
- [ ] API documentation `/docs` is accessible
- [ ] Authentication is working for protected endpoints

---

## 📝 ADDITIONAL NOTES

### Error Response Format
All errors should follow this format:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "Symbol BTC/INVALID is not supported",
    "details": {
      "symbol": "BTC/INVALID",
      "supported_symbols": ["BTC/USDT", "ETH/USDT", ...]
    }
  },
  "timestamp": 1733432100000
}
```

### Health Check Endpoint
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "version": "2.0.0",
        "uptime": get_uptime_seconds(),
        "services": {
            "redis": await check_redis(),
            "coingecko": await check_coingecko(),
            "binance": await check_binance(),
            "ai_models": await check_ai_models()
        }
    }
```

---

## 🎯 SUCCESS CRITERIA

This update will be considered successful when:

1. ✅ All 30+ API endpoints are working
2. ✅ Response times meet performance requirements
3. ✅ WebSocket real-time updates are stable
4. ✅ AI models are generating accurate signals
5. ✅ 99.9% uptime over 7 days
6. ✅ Frontend successfully migrates to use only HF Space
7. ✅ Zero external API calls from frontend

---

## 📞 SUPPORT & CONTACT

**Project:** Dreammaker Crypto Trading Platform  
**Priority:** HIGH - Critical Infrastructure Update  
**Timeline:** ASAP  
**Status:** Awaiting Implementation  

**This is an UPDATE REQUEST for existing HuggingFace Space to become the unified data source for the entire platform.**

---

**END OF REQUEST**

**Version:** 1.0  
**Date:** December 5, 2025  
**Status:** 🟡 Pending Implementation
