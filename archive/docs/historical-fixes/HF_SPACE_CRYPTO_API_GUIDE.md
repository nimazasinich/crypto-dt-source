# HuggingFace Space Crypto Resources API - Client Guide

## راهنمای استفاده از API منابع کریپتو

**Base URL:** `https://really-amin-crypto-api-clean.hf.space`  
**Local Proxy:** `http://localhost:7860/api/hf-space`  
**Documentation:** https://really-amin-crypto-api-clean.hf.space/docs

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Market Data Services](#1-market-data-services)
3. [Sentiment Services](#2-sentiment-services)
4. [Resources Database](#3-resources-database)
5. [System Status](#4-system-status)
6. [Python Client Usage](#5-python-client-usage)
7. [Response Format](#6-response-format)

---

## Overview

This API provides:
- **Real-time market data** from CoinGecko
- **Sentiment analysis** (Fear & Greed Index) from Alternative.me
- **Resource database** with 281 crypto data sources across 12 categories
- **No authentication required** - All endpoints are public
- **Unlimited rate limit**

---

## 1. Market Data Services

### 1.1 Top Coins by Market Cap

Get the top cryptocurrencies ranked by market capitalization.

**Endpoint:**
```
GET /api/coins/top
GET /api/hf-space/coins/top (local proxy)
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Number of coins (1-250) |

**Request:**
```bash
# Direct
curl "https://really-amin-crypto-api-clean.hf.space/api/coins/top?limit=10"

# Local Proxy
curl "http://localhost:7860/api/hf-space/coins/top?limit=10"
```

**Response:**
```json
{
  "coins": [
    {
      "id": "bitcoin",
      "symbol": "btc",
      "name": "Bitcoin",
      "image": "https://...",
      "current_price": 90241.00,
      "market_cap": 1800580721557,
      "market_cap_rank": 1,
      "total_volume": 69997758241,
      "high_24h": 93468,
      "low_24h": 89600,
      "price_change_24h": -703.87,
      "price_change_percentage_24h": -0.77,
      "circulating_supply": 19961237.0,
      "ath": 126080,
      "ath_date": "2025-10-06T18:57:42.558Z",
      "last_updated": "2025-12-12T19:22:00.626Z"
    }
  ],
  "total": 10,
  "timestamp": "2025-12-12T19:22:43.023917Z"
}
```

---

### 1.2 Trending Coins

Get currently trending cryptocurrencies.

**Endpoint:**
```
GET /api/trending
GET /api/hf-space/trending (local proxy)
```

**Request:**
```bash
curl "https://really-amin-crypto-api-clean.hf.space/api/trending"
```

**Response:**
```json
{
  "coins": [
    {
      "id": "gala",
      "name": "GALA",
      "symbol": "GALA",
      "market_cap_rank": 206,
      "thumb": "https://...",
      "price_btc": 7.758989661597377e-08
    }
  ],
  "total": 10,
  "timestamp": "2025-12-12T19:22:49.419456Z"
}
```

---

### 1.3 Global Market Overview

Get global cryptocurrency market statistics.

**Endpoint:**
```
GET /api/market
GET /api/hf-space/market (local proxy)
```

**Request:**
```bash
curl "https://really-amin-crypto-api-clean.hf.space/api/market"
```

**Response:**
```json
{
  "total_market_cap": 3152683901788.04,
  "total_volume": 148435101985.29,
  "market_cap_percentage": {
    "btc": 57.09,
    "eth": 11.77,
    "usdt": 5.91,
    "xrp": 3.85,
    "bnb": 3.84
  },
  "market_cap_change_percentage_24h": -1.06,
  "active_cryptocurrencies": 19190,
  "markets": 1440,
  "timestamp": "2025-12-12T19:22:50.922474Z"
}
```

---

## 2. Sentiment Services

### 2.1 Global Sentiment (Fear & Greed Index)

Get the current Fear & Greed Index.

**Endpoint:**
```
GET /api/sentiment/global
GET /api/hf-space/sentiment (local proxy)
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timeframe` | string | "1D" | Timeframe for data |

**Request:**
```bash
curl "https://really-amin-crypto-api-clean.hf.space/api/sentiment/global"
```

**Response:**
```json
{
  "fear_greed_index": 29,
  "sentiment": "fear",
  "market_mood": "bearish",
  "confidence": 0.85,
  "history": [
    {
      "timestamp": 1765497600000,
      "sentiment": 29,
      "classification": "Fear"
    }
  ],
  "timestamp": "2025-12-12T19:22:52.215750Z",
  "source": "alternative.me"
}
```

**Index Classification:**
| Range | Classification |
|-------|----------------|
| 0-24 | Extreme Fear |
| 25-49 | Fear |
| 50-74 | Greed |
| 75-100 | Extreme Greed |

---

### 2.2 Asset-Specific Sentiment

Get sentiment for a specific cryptocurrency.

**Endpoint:**
```
GET /api/sentiment/asset/{symbol}
GET /api/hf-space/sentiment/{symbol} (local proxy)
```

**Request:**
```bash
curl "https://really-amin-crypto-api-clean.hf.space/api/sentiment/asset/BTC"
```

**Response:**
```json
{
  "symbol": "BTC",
  "sentiment": "neutral",
  "score": 50,
  "confidence": 0.5,
  "timestamp": "2025-12-12T19:22:53.614869Z"
}
```

---

## 3. Resources Database

The API provides access to a curated database of **281 crypto data resources** across **12 categories**.

### 3.1 Get Resources Statistics

**Endpoint:**
```
GET /api/resources/stats
GET /api/hf-space/resources/stats (local proxy)
```

**Request:**
```bash
curl "https://really-amin-crypto-api-clean.hf.space/api/resources/stats"
```

**Response:**
```json
{
  "total_resources": 281,
  "total_categories": 12,
  "categories": {
    "rpc_nodes": 24,
    "block_explorers": 33,
    "market_data_apis": 33,
    "news_apis": 17,
    "sentiment_apis": 14,
    "onchain_analytics_apis": 14,
    "whale_tracking_apis": 10,
    "community_sentiment_apis": 1,
    "hf_resources": 9,
    "free_http_endpoints": 13,
    "local_backend_routes": 106,
    "cors_proxies": 7
  },
  "metadata": {
    "version": "1.0",
    "updated": "2025-12-08"
  }
}
```

---

### 3.2 List All Categories

**Endpoint:**
```
GET /api/categories
GET /api/hf-space/resources/categories (local proxy)
```

**Request:**
```bash
curl "https://really-amin-crypto-api-clean.hf.space/api/categories"
```

**Response:**
```json
{
  "total": 12,
  "categories": [
    {
      "name": "rpc_nodes",
      "count": 24,
      "endpoint": "/api/resources/category/rpc_nodes"
    },
    {
      "name": "market_data_apis",
      "count": 33,
      "endpoint": "/api/resources/category/market_data_apis"
    }
  ]
}
```

---

### 3.3 Get Resources by Category

**Endpoint:**
```
GET /api/resources/category/{category}
GET /api/hf-space/resources/category/{category} (local proxy)
```

**Available Categories:**

| Category | Count | Description |
|----------|-------|-------------|
| `rpc_nodes` | 24 | Ethereum, BSC, Polygon RPC endpoints |
| `block_explorers` | 33 | Etherscan, BSCScan, Polygonscan, etc. |
| `market_data_apis` | 33 | CoinGecko, CoinMarketCap, Binance, etc. |
| `news_apis` | 17 | Crypto news sources |
| `sentiment_apis` | 14 | LunarCrush, Santiment, Alternative.me |
| `onchain_analytics_apis` | 14 | Glassnode, CryptoQuant, Nansen |
| `whale_tracking_apis` | 10 | Whale Alert, Arkham, DeBank |
| `hf_resources` | 9 | HuggingFace models & datasets |
| `free_http_endpoints` | 13 | Free API endpoints |
| `local_backend_routes` | 106 | Local backend routes |
| `cors_proxies` | 7 | CORS proxy services |
| `community_sentiment_apis` | 1 | Community sentiment |

**Request:**
```bash
# Get all RPC nodes
curl "https://really-amin-crypto-api-clean.hf.space/api/resources/category/rpc_nodes"

# Get all market data APIs
curl "https://really-amin-crypto-api-clean.hf.space/api/resources/category/market_data_apis"

# Get whale tracking APIs
curl "https://really-amin-crypto-api-clean.hf.space/api/resources/category/whale_tracking_apis"
```

**Response (example: rpc_nodes):**
```json
{
  "category": "rpc_nodes",
  "total": 24,
  "resources": [
    {
      "id": "publicnode_eth_mainnet",
      "name": "PublicNode Ethereum",
      "chain": "ethereum",
      "role": "rpc",
      "base_url": "https://ethereum.publicnode.com",
      "auth": {
        "type": "none"
      },
      "docs_url": "https://www.publicnode.com",
      "notes": "Free, no rate limit"
    },
    {
      "id": "infura_eth_mainnet",
      "name": "Infura Ethereum Mainnet",
      "chain": "ethereum",
      "base_url": "https://mainnet.infura.io/v3/{PROJECT_ID}",
      "auth": {
        "type": "apiKeyPath",
        "param_name": "PROJECT_ID"
      },
      "docs_url": "https://docs.infura.io",
      "notes": "Free tier: 100K req/day"
    }
  ]
}
```

**Response (example: market_data_apis):**
```json
{
  "category": "market_data_apis",
  "total": 33,
  "resources": [
    {
      "id": "coingecko",
      "name": "CoinGecko",
      "role": "primary_free",
      "base_url": "https://api.coingecko.com/api/v3",
      "auth": { "type": "none" },
      "docs_url": "https://www.coingecko.com/en/api/documentation",
      "endpoints": {
        "simple_price": "/simple/price?ids={ids}&vs_currencies={fiats}",
        "coin_data": "/coins/{id}?localization=false",
        "market_chart": "/coins/{id}/market_chart?vs_currency=usd&days=7",
        "global_data": "/global",
        "trending": "/search/trending"
      },
      "notes": "Rate limit: 10-50 calls/min (free)"
    }
  ]
}
```

---

### 3.4 Get All Resources

**Endpoint:**
```
GET /api/resources/list
GET /api/hf-space/resources/all (local proxy)
```

**Request:**
```bash
curl "https://really-amin-crypto-api-clean.hf.space/api/resources/list"
```

---

## 4. System Status

### 4.1 Health Check

**Endpoint:**
```
GET /health
GET /api/hf-space/health (local proxy)
```

**Request:**
```bash
curl "https://really-amin-crypto-api-clean.hf.space/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-12T19:22:38.977664",
  "resources_loaded": true,
  "total_categories": 12,
  "websocket_connections": 0
}
```

---

### 4.2 Data Providers Status

**Endpoint:**
```
GET /api/providers
GET /api/hf-space/providers (local proxy)
```

**Request:**
```bash
curl "https://really-amin-crypto-api-clean.hf.space/api/providers"
```

**Response:**
```json
{
  "providers": [
    {
      "name": "CoinGecko",
      "status": "active",
      "endpoint": "https://api.coingecko.com",
      "latency": 148,
      "success_rate": 97
    },
    {
      "name": "Binance",
      "status": "active",
      "endpoint": "https://api.binance.com",
      "latency": 72,
      "success_rate": 96
    }
  ],
  "total": 3
}
```

---

### 4.3 System Status

**Endpoint:**
```
GET /api/status
GET /api/hf-space/status (local proxy)
```

**Request:**
```bash
curl "https://really-amin-crypto-api-clean.hf.space/api/status"
```

**Response:**
```json
{
  "status": "online",
  "health": "healthy",
  "avg_response_time": 83,
  "cache_hit_rate": 76,
  "active_connections": 6,
  "uptime": "99.9%"
}
```

---

## 5. Python Client Usage

### 5.1 Using the Service (Async)

```python
from backend.services.hf_space_crypto_client import get_hf_space_crypto_service
import asyncio

async def main():
    service = get_hf_space_crypto_service()
    
    # Get top 10 coins
    result = await service.get_top_coins(limit=10)
    if result["success"]:
        for coin in result["data"]["coins"]:
            print(f"{coin['name']}: ${coin['current_price']:,.2f}")
    
    # Get Fear & Greed Index
    fgi = await service.get_fear_greed_index()
    print(f"Fear & Greed Index: {fgi}")
    
    # Get market overview
    result = await service.get_market_overview()
    if result["success"]:
        print(f"Total Market Cap: ${result['data']['total_market_cap']:,.0f}")
    
    # Get resources by category
    result = await service.get_resources_by_category("market_data_apis")
    if result["success"]:
        for resource in result["data"]["resources"][:5]:
            print(f"- {resource['name']}: {resource['base_url']}")
    
    await service.close()

asyncio.run(main())
```

### 5.2 Using the Standalone Client (Sync/Async)

```python
from collectors.hf_crypto_api_client import HFCryptoAPIClient

# Synchronous usage
client = HFCryptoAPIClient()

# Get top coins
coins = client.get_top_coins(limit=10)
for coin in coins.get("coins", []):
    print(f"{coin['name']}: ${coin['current_price']:,.2f}")

# Get Fear & Greed Index
fgi = client.get_fear_greed_index()
print(f"Fear & Greed: {fgi}")

# Get BTC price
btc_price = client.get_btc_price()
print(f"BTC: ${btc_price:,.2f}")

# Get total market cap
mcap = client.get_total_market_cap()
print(f"Market Cap: ${mcap:,.0f}")

# Get RPC nodes
rpc_nodes = client.get_rpc_nodes()
for node in rpc_nodes[:5]:
    print(f"- {node['name']}: {node['base_url']}")

# Get market data APIs
apis = client.get_market_data_apis()
for api in apis[:5]:
    print(f"- {api['name']}: {api['base_url']}")
```

### 5.3 Using from Collectors Package

```python
from collectors import HFCryptoAPIClient, get_hf_crypto_client

# Get singleton client
client = get_hf_crypto_client()

# Use the client
coins = client.get_top_coins(limit=5)
sentiment = client.get_global_sentiment()
resources = client.get_resources_stats()
```

---

## 6. Response Format

All endpoints return JSON with consistent structure:

### Success Response
```json
{
  "data": { ... },
  "total": 10,
  "timestamp": "2025-12-12T19:22:43.023917Z"
}
```

### Error Response (via local proxy)
```json
{
  "detail": "HF Space API unavailable: Request timeout"
}
```

---

## Quick Reference

| Service | Endpoint | Description |
|---------|----------|-------------|
| Top Coins | `GET /api/coins/top?limit=N` | Top N coins by market cap |
| Trending | `GET /api/trending` | Trending coins |
| Market | `GET /api/market` | Global market overview |
| Sentiment | `GET /api/sentiment/global` | Fear & Greed Index |
| Asset Sentiment | `GET /api/sentiment/asset/{symbol}` | Asset-specific sentiment |
| Resources Stats | `GET /api/resources/stats` | Database statistics |
| Categories | `GET /api/categories` | List all categories |
| By Category | `GET /api/resources/category/{cat}` | Resources in category |
| All Resources | `GET /api/resources/list` | All 281 resources |
| Health | `GET /health` | API health check |
| Providers | `GET /api/providers` | Data providers status |
| Status | `GET /api/status` | System status |

---

## Notes

- **No API key required** - All endpoints are public
- **Rate limit** - Unlimited (but be respectful)
- **Data freshness** - Market data updates every few seconds
- **Resources database** - Updated periodically, contains API keys for some services
- **WebSocket** - Available at `wss://really-amin-crypto-api-clean.hf.space/ws` for real-time updates

---

*Last updated: 2025-12-12*
