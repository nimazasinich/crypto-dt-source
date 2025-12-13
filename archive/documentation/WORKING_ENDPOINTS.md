# Working API Endpoints - Complete Reference

## Overview

All backend API endpoints tested and verified working. This document provides examples and expected responses for each endpoint.

**Base URL:** `http://localhost:7860` (or your HuggingFace Space URL)

---

## 🏥 Health & Status Endpoints

### GET /api/health
**Description:** System health check  
**Parameters:** None  
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-12T10:30:00.000000Z",
  "service": "unified_query_service",
  "version": "1.0.0"
}
```
**Test:**
```bash
curl http://localhost:7860/api/health
```

---

### GET /api/status
**Description:** System status with metrics  
**Parameters:** None  
**Response:**
```json
{
  "health": "healthy",
  "online": 2,
  "offline": 0,
  "degraded": 0,
  "avg_response_time": 250,
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl http://localhost:7860/api/status
```

---

### GET /api/routers
**Description:** Get status of all loaded routers  
**Parameters:** None  
**Response:**
```json
{
  "routers": {
    "unified_service_api": "loaded",
    "real_data_api": "loaded",
    "market_api": "loaded",
    "technical_analysis": "loaded",
    "ai_ml": "loaded",
    "multi_source": "loaded"
  },
  "total_loaded": 15,
  "total_available": 15,
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl http://localhost:7860/api/routers
```

---

## 📈 Market Data Endpoints

### GET /api/market
**Description:** Market overview data  
**Parameters:** None  
**Response:**
```json
{
  "total_market_cap": 2450000000000,
  "totalMarketCap": 2450000000000,
  "total_volume": 98500000000,
  "totalVolume": 98500000000,
  "btc_dominance": 52.3,
  "eth_dominance": 17.8,
  "active_coins": 100,
  "timestamp": "2025-12-12T10:30:00.000000Z",
  "source": "coingecko"
}
```
**Test:**
```bash
curl http://localhost:7860/api/market
```

---

### GET /api/coins/top
**Description:** Top cryptocurrencies by market cap  
**Parameters:**
- `limit` (optional): Number of coins to return (default: 50, max: 250)

**Response:**
```json
{
  "coins": [
    {
      "id": "btc",
      "rank": 1,
      "symbol": "BTC",
      "name": "Bitcoin",
      "price": 67850.32,
      "market_cap": 1280000000000,
      "volume_24h": 42500000000,
      "change_24h": 2.45,
      "image": "https://assets.coingecko.com/coins/images/1/small/btc.png"
    }
  ],
  "total": 10,
  "timestamp": "2025-12-12T10:30:00.000000Z",
  "source": "coingecko"
}
```
**Test:**
```bash
curl "http://localhost:7860/api/coins/top?limit=10"
```

---

### GET /api/trending
**Description:** Trending cryptocurrencies  
**Parameters:** None  
**Response:**
```json
{
  "coins": [
    {
      "rank": 1,
      "name": "Bitcoin",
      "symbol": "BTC",
      "price": 67850.32,
      "volume_24h": 42500000000,
      "market_cap": 1280000000000,
      "change_24h": 2.45,
      "image": "https://..."
    }
  ],
  "timestamp": "2025-12-12T10:30:00.000000Z",
  "source": "coingecko_trending"
}
```
**Test:**
```bash
curl http://localhost:7860/api/trending
```

---

### GET /api/service/rate
**Description:** Get rate for a specific trading pair  
**Parameters:**
- `pair` (required): Trading pair (e.g., "BTC/USDT")

**Response:**
```json
{
  "pair": "BTC/USDT",
  "rate": 67850.32,
  "timestamp": "2025-12-12T10:30:00.000000Z",
  "source": "binance"
}
```
**Test:**
```bash
curl "http://localhost:7860/api/service/rate?pair=BTC/USDT"
```

---

### GET /api/service/rate/batch
**Description:** Get rates for multiple trading pairs  
**Parameters:**
- `pairs` (required): Comma-separated list of pairs

**Response:**
```json
{
  "rates": [
    {"pair": "BTC/USDT", "rate": 67850.32},
    {"pair": "ETH/USDT", "rate": 3420.15}
  ],
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl "http://localhost:7860/api/service/rate/batch?pairs=BTC/USDT,ETH/USDT"
```

---

### GET /api/service/history
**Description:** Historical price data  
**Parameters:**
- `symbol` (required): Cryptocurrency symbol
- `interval` (optional): Time interval (1h, 4h, 1d, etc.)
- `limit` (optional): Number of data points

**Response:**
```json
{
  "symbol": "BTC",
  "interval": "1h",
  "data": [
    {"timestamp": 1702380000000, "open": 67800, "high": 67900, "low": 67750, "close": 67850, "volume": 1000}
  ],
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl "http://localhost:7860/api/service/history?symbol=BTC&interval=1h&limit=24"
```

---

## 🧠 Sentiment & AI Endpoints

### GET /api/sentiment/global
**Description:** Global market sentiment  
**Parameters:**
- `timeframe` (optional): "1D", "7D", "30D", "1Y" (default: "1D")

**Response:**
```json
{
  "fear_greed_index": 65,
  "sentiment": "greed",
  "market_mood": "bullish",
  "confidence": 0.85,
  "history": [
    {"timestamp": 1702380000000, "sentiment": 65, "volume": 100000}
  ],
  "timestamp": "2025-12-12T10:30:00.000000Z",
  "source": "alternative.me"
}
```
**Test:**
```bash
curl "http://localhost:7860/api/sentiment/global?timeframe=1D"
```

---

### GET /api/sentiment/asset/{symbol}
**Description:** Sentiment for specific asset  
**Parameters:**
- `symbol` (path): Cryptocurrency symbol (e.g., "BTC")

**Response:**
```json
{
  "symbol": "BTC",
  "sentiment": "positive",
  "sentiment_value": 72,
  "color": "#10b981",
  "social_score": 78,
  "news_score": 65,
  "sources": {
    "twitter": 25000,
    "reddit": 5000,
    "news": 150
  },
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl http://localhost:7860/api/sentiment/asset/BTC
```

---

### POST /api/service/sentiment
**Description:** Analyze text sentiment  
**Body:**
```json
{
  "text": "Bitcoin is showing strong bullish momentum!",
  "mode": "crypto"
}
```
**Response:**
```json
{
  "sentiment": "bullish",
  "score": 0.85,
  "confidence": 0.92,
  "model": "cryptobert",
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl -X POST http://localhost:7860/api/service/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text":"Bitcoin is showing strong bullish momentum!","mode":"crypto"}'
```

---

### GET /api/ai/signals
**Description:** AI trading signals  
**Parameters:**
- `symbol` (optional): Cryptocurrency symbol (default: "BTC")

**Response:**
```json
{
  "symbol": "BTC",
  "signals": [
    {
      "id": "sig_1702380000_0",
      "symbol": "BTC",
      "type": "buy",
      "score": 0.85,
      "model": "cryptobert_elkulako",
      "created_at": "2025-12-12T10:30:00.000000Z",
      "confidence": 0.92
    }
  ],
  "total": 3,
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl "http://localhost:7860/api/ai/signals?symbol=BTC"
```

---

### POST /api/ai/decision
**Description:** AI trading decision  
**Body:**
```json
{
  "symbol": "BTC",
  "horizon": "swing",
  "risk_tolerance": "moderate",
  "context": "Market is showing bullish momentum",
  "model": "cryptobert"
}
```
**Response:**
```json
{
  "decision": "BUY",
  "confidence": 0.78,
  "summary": "Based on recent market conditions and a swing horizon, the AI suggests a BUY stance for BTC with 78% confidence.",
  "signals": [
    {"type": "bullish", "text": "Primary signal indicates BUY bias."}
  ],
  "risks": [
    "Market volatility may increase around major macro events."
  ],
  "targets": {
    "support": 65000,
    "resistance": 70000,
    "target": 72000
  },
  "symbol": "BTC",
  "horizon": "swing",
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl -X POST http://localhost:7860/api/ai/decision \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTC","horizon":"swing","risk_tolerance":"moderate"}'
```

---

## 📰 News Endpoints

### GET /api/news
**Description:** Latest crypto news  
**Parameters:**
- `limit` (optional): Number of articles (default: 50)
- `source` (optional): Filter by source (e.g., "CoinDesk")

**Response:**
```json
{
  "articles": [
    {
      "id": "article-123",
      "title": "Bitcoin Reaches New All-Time High",
      "description": "Bitcoin surpasses $70,000 for the first time...",
      "content": "Full article content...",
      "source": "CoinDesk",
      "published_at": "2025-12-12T10:00:00.000000Z",
      "url": "https://...",
      "sentiment": "positive",
      "sentiment_score": 0.75,
      "tags": ["bitcoin", "price", "ath"]
    }
  ],
  "total": 50,
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl "http://localhost:7860/api/news?limit=10"
```

---

### GET /api/news/latest
**Description:** Alias for /api/news  
**Parameters:** Same as /api/news  
**Response:** Same as /api/news  
**Test:**
```bash
curl "http://localhost:7860/api/news/latest?limit=10"
```

---

## 🤖 AI Models Endpoints

### GET /api/models/list
**Description:** List all AI models  
**Parameters:** None  
**Response:**
```json
{
  "models": [
    {
      "key": "cryptobert_elkulako",
      "id": "cryptobert_elkulako",
      "name": "ElKulako/cryptobert",
      "model_id": "ElKulako/cryptobert",
      "task": "sentiment-analysis",
      "category": "sentiment",
      "requires_auth": false,
      "loaded": true,
      "error": null
    }
  ],
  "total": 4,
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl http://localhost:7860/api/models/list
```

---

### GET /api/models/status
**Description:** Models status summary  
**Parameters:** None  
**Response:**
```json
{
  "status": "operational",
  "models_loaded": 2,
  "models_failed": 0,
  "hf_mode": "on",
  "transformers_available": true,
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl http://localhost:7860/api/models/status
```

---

### GET /api/models/summary
**Description:** Comprehensive models summary  
**Parameters:** None  
**Response:**
```json
{
  "ok": true,
  "success": true,
  "summary": {
    "total_models": 4,
    "loaded_models": 2,
    "failed_models": 0,
    "hf_mode": "on",
    "transformers_available": true
  },
  "categories": {
    "sentiment": [
      {
        "key": "cryptobert_elkulako",
        "model_id": "ElKulako/cryptobert",
        "name": "cryptobert",
        "category": "sentiment",
        "task": "sentiment-analysis",
        "loaded": true,
        "status": "healthy"
      }
    ]
  },
  "health_registry": [],
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl http://localhost:7860/api/models/summary
```

---

### GET /api/models/health
**Description:** Per-model health information  
**Parameters:** None  
**Response:**
```json
{
  "health": {
    "cryptobert_elkulako": {
      "status": "healthy",
      "success_count": 150,
      "error_count": 2,
      "last_success": "2025-12-12T10:29:00.000000Z"
    }
  },
  "total": 4
}
```
**Test:**
```bash
curl http://localhost:7860/api/models/health
```

---

### POST /api/models/test
**Description:** Test a model with input  
**Body:**
```json
{
  "model": "cryptobert",
  "input": "Bitcoin is showing strong momentum"
}
```
**Response:**
```json
{
  "success": true,
  "model": "cryptobert_elkulako",
  "result": {
    "sentiment": "bullish",
    "score": 0.85,
    "confidence": 0.92
  },
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl -X POST http://localhost:7860/api/models/test \
  -H "Content-Type: application/json" \
  -d '{"model":"cryptobert","input":"Bitcoin is showing strong momentum"}'
```

---

### POST /api/models/reinitialize
**Description:** Reinitialize all AI models  
**Body:** None  
**Response:**
```json
{
  "status": "ok",
  "init_result": {
    "initialized": true,
    "models_loaded": 2
  },
  "registry": {
    "status": "operational",
    "models_loaded": 2
  }
}
```
**Test:**
```bash
curl -X POST http://localhost:7860/api/models/reinitialize
```

---

## 📚 Resources Endpoints

### GET /api/resources
**Description:** Resources statistics  
**Parameters:** None  
**Response:**
```json
{
  "total": 248,
  "free": 180,
  "models": 8,
  "providers": 15,
  "categories": [
    {"name": "Market Data", "count": 15},
    {"name": "News", "count": 10}
  ],
  "timestamp": "2025-12-12T10:30:00.000000Z",
  "registry_loaded": true
}
```
**Test:**
```bash
curl http://localhost:7860/api/resources
```

---

### GET /api/resources/summary
**Description:** Detailed resources summary  
**Parameters:** None  
**Response:**
```json
{
  "success": true,
  "summary": {
    "total_resources": 248,
    "free_resources": 180,
    "premium_resources": 68,
    "models_available": 8,
    "local_routes_count": 24,
    "categories": {
      "market_data": {"count": 15, "type": "external"},
      "news": {"count": 10, "type": "external"}
    },
    "by_category": [
      {"name": "Market Data", "count": 15}
    ]
  },
  "timestamp": "2025-12-12T10:30:00.000000Z",
  "registry_loaded": true
}
```
**Test:**
```bash
curl http://localhost:7860/api/resources/summary
```

---

### GET /api/resources/categories
**Description:** List resource categories  
**Parameters:** None  
**Response:**
```json
{
  "categories": [
    {"name": "Market Data", "count": 15},
    {"name": "News", "count": 10},
    {"name": "Sentiment", "count": 7}
  ],
  "total": 248,
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl http://localhost:7860/api/resources/categories
```

---

### GET /api/resources/category/{category_name}
**Description:** Get resources for specific category  
**Parameters:**
- `category_name` (path): Category name

**Response:**
```json
{
  "category": "Market Data",
  "items": [
    {
      "name": "CoinGecko",
      "type": "API",
      "url": "https://api.coingecko.com",
      "free": true
    }
  ],
  "total": 15,
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl http://localhost:7860/api/resources/category/MarketData
```

---

### GET /api/providers
**Description:** List of data providers  
**Parameters:** None  
**Response:**
```json
{
  "providers": [
    {"id": "coingecko", "name": "CoinGecko", "status": "online", "type": "market_data"},
    {"id": "binance", "name": "Binance", "status": "online", "type": "exchange"},
    {"id": "etherscan", "name": "Etherscan", "status": "online", "type": "blockchain"}
  ],
  "total": 6,
  "online": 6,
  "offline": 0,
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```
**Test:**
```bash
curl http://localhost:7860/api/providers
```

---

## 📊 Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters |
| 404 | Not Found | Endpoint or resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## 🔍 Testing Tips

### 1. Use curl with formatting
```bash
curl http://localhost:7860/api/health | jq
```

### 2. Test with timeout
```bash
curl --max-time 10 http://localhost:7860/api/market
```

### 3. Include headers
```bash
curl -H "Accept: application/json" http://localhost:7860/api/health
```

### 4. Save response to file
```bash
curl http://localhost:7860/api/coins/top?limit=10 > response.json
```

### 5. Test POST with data
```bash
curl -X POST http://localhost:7860/api/ai/decision \
  -H "Content-Type: application/json" \
  -d @request.json
```

---

## ✅ Verification

All endpoints have been tested and verified working. Use the provided test suite for automated verification:

```bash
# Automated testing
python verify_deployment.py

# Interactive testing
open http://localhost:7860/test_api_integration.html
```

---

**Last Updated:** December 12, 2025  
**Status:** ✅ All endpoints operational
