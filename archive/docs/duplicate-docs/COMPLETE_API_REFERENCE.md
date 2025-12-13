# Complete API Reference - All Available Services

## راهنمای کامل API - تمام سرویس‌های موجود

**Base URL:** `http://localhost:7860`

---

## 📋 Table of Contents

1. [Market Data & Prices](#1-market-data--prices)
2. [OHLCV / Candlestick Data](#2-ohlcv--candlestick-data)
3. [Technical Indicators](#3-technical-indicators)
4. [Sentiment Analysis](#4-sentiment-analysis)
5. [News & Headlines](#5-news--headlines)
6. [Blockchain & On-Chain Data](#6-blockchain--on-chain-data)
7. [Whale Tracking](#7-whale-tracking)
8. [AI & Machine Learning](#8-ai--machine-learning)
9. [HuggingFace Space Crypto API](#9-huggingface-space-crypto-api)
10. [System & Monitoring](#10-system--monitoring)

---

## 1. Market Data & Prices

### 1.1 Get Single Price
```bash
GET /api/market/price?symbol=BTC
```
**Parameters:**
- `symbol` (required): Cryptocurrency symbol (BTC, ETH, etc.)

**Example:**
```bash
curl "http://localhost:7860/api/market/price?symbol=BTC"
```

**Response:**
```json
{
  "symbol": "BTC",
  "price": 90241.00,
  "source": "coingecko",
  "timestamp": 1702406543
}
```

---

### 1.2 Get Multiple Prices (Multi-Source)
```bash
GET /api/multi-source/prices?symbols=BTC,ETH,BNB&limit=100
```
**Parameters:**
- `symbols` (optional): Comma-separated symbols
- `limit` (optional): Max results (1-250, default: 100)
- `cross_check` (optional): Validate across sources (default: true)

**Example:**
```bash
curl "http://localhost:7860/api/multi-source/prices?symbols=BTC,ETH&limit=10"
```

---

### 1.3 Get Top Coins
```bash
GET /api/service/top?limit=100
GET /api/hf-space/coins/top?limit=50
```
**Parameters:**
- `limit` (optional): Number of coins (default: 100)

**Example:**
```bash
curl "http://localhost:7860/api/hf-space/coins/top?limit=10"
```

---

### 1.4 Get Trending Coins
```bash
GET /api/trending
GET /api/hf-space/trending
GET /coingecko/trending
```

**Example:**
```bash
curl "http://localhost:7860/api/hf-space/trending"
```

---

### 1.5 Get Market Overview
```bash
GET /api/market
GET /api/hf-space/market
GET /api/service/market-status
```

**Example:**
```bash
curl "http://localhost:7860/api/hf-space/market"
```

**Response:**
```json
{
  "total_market_cap": 3152683901788,
  "total_volume": 148435101985,
  "market_cap_percentage": {
    "btc": 57.09,
    "eth": 11.77
  },
  "active_cryptocurrencies": 19190
}
```

---

## 2. OHLCV / Candlestick Data

### 2.1 Get OHLCV Data
```bash
GET /api/market/ohlc?symbol=BTC&timeframe=1h
GET /api/multi-source/ohlc/{symbol}?timeframe=1h&limit=1000
GET /api/trading/ohlcv/{symbol}?interval=1h&limit=100
```

**Parameters:**
- `symbol` (required): Cryptocurrency symbol
- `timeframe/interval` (optional): 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w
- `limit` (optional): Number of candles (default: 100-1000)

**Example:**
```bash
# Get 100 hourly candles for BTC
curl "http://localhost:7860/api/multi-source/ohlc/BTC?timeframe=1h&limit=100"

# Get 4-hour candles for ETH
curl "http://localhost:7860/api/market/ohlc?symbol=ETH&timeframe=4h"
```

**Response:**
```json
{
  "symbol": "BTC",
  "timeframe": "1h",
  "data": [
    {
      "timestamp": 1702400000000,
      "open": 90100.00,
      "high": 90500.00,
      "low": 89800.00,
      "close": 90241.00,
      "volume": 1234567890
    }
  ],
  "source": "binance"
}
```

---

### 2.2 Get Historical Data
```bash
GET /api/market/history?symbol=BTC&days=30
GET /api/service/history?symbol=BTC&timeframe=1h
```

**Parameters:**
- `symbol` (required): Cryptocurrency symbol
- `days` (optional): Number of days (default: 30)
- `timeframe` (optional): 1h, 4h, 1d

---

## 3. Technical Indicators

### 3.1 RSI (Relative Strength Index)
```bash
GET /api/indicators/rsi?symbol=BTC&timeframe=1h&period=14
```

**Parameters:**
- `symbol` (optional): Default "BTC"
- `timeframe` (optional): 1m, 5m, 15m, 1h, 4h, 1d
- `period` (optional): RSI period (default: 14)

**Example:**
```bash
curl "http://localhost:7860/api/indicators/rsi?symbol=BTC&timeframe=1h&period=14"
```

**Response:**
```json
{
  "success": true,
  "symbol": "BTC",
  "timeframe": "1h",
  "indicator": "rsi",
  "data": {
    "value": 55.23
  },
  "signal": "neutral",
  "description": "RSI at 55.23 - neutral zone"
}
```

---

### 3.2 MACD
```bash
GET /api/indicators/macd?symbol=BTC&timeframe=1h&fast=12&slow=26&signal_period=9
```

**Parameters:**
- `symbol`, `timeframe`
- `fast` (optional): Fast EMA period (default: 12)
- `slow` (optional): Slow EMA period (default: 26)
- `signal_period` (optional): Signal line period (default: 9)

**Example:**
```bash
curl "http://localhost:7860/api/indicators/macd?symbol=BTC&timeframe=1h"
```

**Response:**
```json
{
  "success": true,
  "symbol": "BTC",
  "indicator": "macd",
  "data": {
    "macd_line": 50.0,
    "signal_line": 45.0,
    "histogram": 5.0
  },
  "trend": "bullish",
  "signal": "buy"
}
```

---

### 3.3 Bollinger Bands
```bash
GET /api/indicators/bollinger-bands?symbol=BTC&timeframe=1h&period=20&std_dev=2
```

**Parameters:**
- `symbol`, `timeframe`
- `period` (optional): Period (default: 20)
- `std_dev` (optional): Standard deviation multiplier (default: 2.0)

**Example:**
```bash
curl "http://localhost:7860/api/indicators/bollinger-bands?symbol=BTC&timeframe=1h"
```

**Response:**
```json
{
  "success": true,
  "symbol": "BTC",
  "indicator": "bollinger_bands",
  "data": {
    "upper": 92500.00,
    "middle": 90241.00,
    "lower": 88000.00,
    "bandwidth": 4.98,
    "percent_b": 50.0
  },
  "signal": "neutral"
}
```

---

### 3.4 SMA (Simple Moving Average)
```bash
GET /api/indicators/sma?symbol=BTC&timeframe=1h
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sma20": 89500.00,
    "sma50": 87200.00,
    "sma200": 75000.00
  },
  "trend": "bullish",
  "signal": "buy"
}
```

---

### 3.5 EMA (Exponential Moving Average)
```bash
GET /api/indicators/ema?symbol=BTC&timeframe=1h
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ema12": 90100.00,
    "ema26": 89500.00,
    "ema50": 87000.00
  },
  "trend": "bullish"
}
```

---

### 3.6 Stochastic RSI
```bash
GET /api/indicators/stoch-rsi?symbol=BTC&timeframe=1h&rsi_period=14&stoch_period=14
```

**Response:**
```json
{
  "success": true,
  "data": {
    "value": 65.5,
    "k_line": 65.5,
    "d_line": 60.2
  },
  "signal": "neutral"
}
```

---

### 3.7 ATR (Average True Range)
```bash
GET /api/indicators/atr?symbol=BTC&timeframe=1h&period=14
```

**Response:**
```json
{
  "success": true,
  "data": {
    "value": 1500.00,
    "percent": 1.66
  },
  "volatility_level": "medium"
}
```

---

### 3.8 Comprehensive Analysis (ALL Indicators)
```bash
GET /api/indicators/comprehensive?symbol=BTC&timeframe=1h
```

**Example:**
```bash
curl "http://localhost:7860/api/indicators/comprehensive?symbol=BTC&timeframe=1h"
```

**Response:**
```json
{
  "success": true,
  "symbol": "BTC",
  "current_price": 90241.00,
  "indicators": {
    "bollinger_bands": {"upper": 92500, "middle": 90241, "lower": 88000},
    "stoch_rsi": {"value": 55, "k_line": 55, "d_line": 52},
    "atr": {"value": 1500, "percent": 1.66},
    "sma": {"sma20": 89500, "sma50": 87200, "sma200": 75000},
    "ema": {"ema12": 90100, "ema26": 89500},
    "macd": {"macd_line": 50, "signal_line": 45, "histogram": 5},
    "rsi": {"value": 55}
  },
  "signals": {
    "bollinger_bands": "neutral",
    "stoch_rsi": "neutral",
    "sma": "bullish",
    "ema": "bullish",
    "macd": "bullish",
    "rsi": "neutral"
  },
  "overall_signal": "BUY",
  "confidence": 70,
  "recommendation": "Majority bullish signals - favorable conditions for entry"
}
```

---

### 3.9 List All Indicator Services
```bash
GET /api/indicators/services
```

---

## 4. Sentiment Analysis

### 4.1 Fear & Greed Index
```bash
GET /api/hf-space/sentiment
GET /api/multi-source/sentiment
GET /api/sentiment/global
GET /alternative/fng
```

**Example:**
```bash
curl "http://localhost:7860/api/hf-space/sentiment"
```

**Response:**
```json
{
  "fear_greed_index": 29,
  "sentiment": "fear",
  "market_mood": "bearish",
  "confidence": 0.85,
  "source": "alternative.me"
}
```

---

### 4.2 Analyze Text Sentiment (AI)
```bash
POST /api/sentiment/analyze
POST /hf/sentiment
```

**Body:**
```json
{
  "text": "Bitcoin is going to the moon! Very bullish!"
}
```

**Example:**
```bash
curl -X POST "http://localhost:7860/api/sentiment/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Bitcoin is going to the moon!"}'
```

**Response:**
```json
{
  "text": "Bitcoin is going to the moon!",
  "sentiment": "bullish",
  "score": 0.92,
  "confidence": 0.87,
  "model": "CryptoBERT"
}
```

---

### 4.3 Bulk Sentiment Analysis
```bash
POST /hf/sentiment/batch
```

**Body:**
```json
{
  "texts": [
    "BTC is going up!",
    "ETH crash incoming",
    "Market looks stable"
  ]
}
```

---

### 4.4 Asset-Specific Sentiment
```bash
GET /api/hf-space/sentiment/{symbol}
GET /api/resources/sentiment/coin/{symbol}
```

**Example:**
```bash
curl "http://localhost:7860/api/hf-space/sentiment/BTC"
```

---

## 5. News & Headlines

### 5.1 Get Latest News
```bash
GET /api/multi-source/news?query=cryptocurrency&limit=50
GET /api/news/latest
GET /api/hf-space/resources/category/news_apis
```

**Parameters:**
- `query` (optional): Search query (default: "cryptocurrency")
- `limit` (optional): Max articles (default: 50)
- `aggregate` (optional): Combine from multiple sources (default: true)

**Example:**
```bash
curl "http://localhost:7860/api/multi-source/news?query=bitcoin&limit=20"
```

**Response:**
```json
{
  "articles": [
    {
      "title": "Bitcoin Reaches New High",
      "description": "...",
      "url": "https://...",
      "source": "CoinDesk",
      "publishedAt": "2025-12-12T10:00:00Z"
    }
  ],
  "total": 20,
  "sources_used": ["coindesk", "cointelegraph", "cryptopanic"]
}
```

---

### 5.2 Get Headlines
```bash
GET /api/news/headlines
```

---

### 5.3 RSS Feeds
```bash
GET /rss/all
GET /rss/feed?url=https://cointelegraph.com/rss
GET /coindesk/rss
GET /cointelegraph/rss
```

**Example:**
```bash
curl "http://localhost:7860/rss/all"
```

---

## 6. Blockchain & On-Chain Data

### 6.1 Gas Prices
```bash
GET /api/blockchain/gas
GET /api/resources/onchain/gas
GET /api/crypto/blockchain/gas
```

**Example:**
```bash
curl "http://localhost:7860/api/blockchain/gas"
```

**Response:**
```json
{
  "chain": "ethereum",
  "gas": {
    "slow": 20,
    "standard": 25,
    "fast": 35,
    "instant": 50
  },
  "unit": "gwei"
}
```

---

### 6.2 Blockchain Stats
```bash
GET /api/blockchain/{chain}
GET /api/blockchain/stats
```

**Parameters:**
- `chain`: ethereum, bsc, tron

**Example:**
```bash
curl "http://localhost:7860/api/blockchain/ethereum"
```

---

### 6.3 Transaction Data
```bash
GET /api/blockchain/transactions?address={address}
GET /api/resources/onchain/transactions?address={address}&chain=ethereum
```

---

### 6.4 Address Balance
```bash
GET /api/resources/onchain/balance?address={address}&chain=ethereum
```

---

## 7. Whale Tracking

### 7.1 Whale Transactions
```bash
GET /api/whales/transactions
GET /api/service/whales
```

**Example:**
```bash
curl "http://localhost:7860/api/service/whales"
```

**Response:**
```json
{
  "transactions": [
    {
      "hash": "0x...",
      "from": "0x...",
      "to": "0x...",
      "value": "1000 BTC",
      "timestamp": "2025-12-12T10:00:00Z"
    }
  ],
  "total": 10
}
```

---

### 7.2 Whale Stats
```bash
GET /api/whales/stats
```

---

## 8. AI & Machine Learning

### 8.1 Available AI Models
```bash
GET /api/models/list
GET /hf/models
GET /api/models/available
```

**Example:**
```bash
curl "http://localhost:7860/api/models/list"
```

---

### 8.2 Load AI Model
```bash
POST /hf/models/load
```

**Body:**
```json
{
  "model_key": "cryptobert"
}
```

---

### 8.3 AI Price Prediction
```bash
GET /api/ai/predict/{symbol}
POST /api/ai/predict
```

---

### 8.4 Trading Signal
```bash
POST /api/trading/signal
```

**Body:**
```json
{
  "symbol": "BTC",
  "timeframe": "1h"
}
```

---

### 8.5 HuggingFace Datasets
```bash
GET /hf/datasets
GET /api/resources/hf/ohlcv?symbol=BTC&timeframe=1h
GET /api/resources/hf/symbols
```

**Example:**
```bash
curl "http://localhost:7860/api/resources/hf/symbols"
```

---

## 9. HuggingFace Space Crypto API

External API providing market data and 281 curated resources.

### 9.1 Market Data
```bash
GET /api/hf-space/coins/top?limit=50
GET /api/hf-space/trending
GET /api/hf-space/market
```

### 9.2 Sentiment
```bash
GET /api/hf-space/sentiment
GET /api/hf-space/sentiment/{symbol}
```

### 9.3 Resources Database (281 resources)
```bash
GET /api/hf-space/resources/stats
GET /api/hf-space/resources/categories
GET /api/hf-space/resources/category/{category}
GET /api/hf-space/resources/all
```

**Available Categories:**
- `rpc_nodes` (24)
- `block_explorers` (33)
- `market_data_apis` (33)
- `news_apis` (17)
- `sentiment_apis` (14)
- `onchain_analytics_apis` (14)
- `whale_tracking_apis` (10)
- `hf_resources` (9)
- `free_http_endpoints` (13)
- `cors_proxies` (7)

**Example:**
```bash
# Get all RPC nodes
curl "http://localhost:7860/api/hf-space/resources/category/rpc_nodes"

# Get all market data APIs
curl "http://localhost:7860/api/hf-space/resources/category/market_data_apis"
```

### 9.4 System Status
```bash
GET /api/hf-space/health
GET /api/hf-space/providers
GET /api/hf-space/status
```

---

## 10. System & Monitoring

### 10.1 Health Check
```bash
GET /health
GET /api/health
GET /api/multi-source/health
```

---

### 10.2 System Status
```bash
GET /api/status
GET /api/monitoring/status
```

---

### 10.3 Source Statistics
```bash
GET /api/multi-source/sources/status
GET /api/multi-source/monitoring/stats
GET /api/providers/stats
```

---

### 10.4 Background Worker
```bash
GET /api/worker/status
GET /api/worker/stats
POST /api/worker/start
POST /api/worker/stop
```

---

## Quick Reference Table

| Service | Endpoint | Method |
|---------|----------|--------|
| **Prices** | `/api/market/price?symbol=BTC` | GET |
| **Multi-Source Prices** | `/api/multi-source/prices` | GET |
| **Top Coins** | `/api/hf-space/coins/top` | GET |
| **Trending** | `/api/hf-space/trending` | GET |
| **Market Overview** | `/api/hf-space/market` | GET |
| **OHLCV** | `/api/multi-source/ohlc/{symbol}` | GET |
| **RSI** | `/api/indicators/rsi?symbol=BTC` | GET |
| **MACD** | `/api/indicators/macd?symbol=BTC` | GET |
| **Bollinger Bands** | `/api/indicators/bollinger-bands` | GET |
| **SMA** | `/api/indicators/sma?symbol=BTC` | GET |
| **EMA** | `/api/indicators/ema?symbol=BTC` | GET |
| **All Indicators** | `/api/indicators/comprehensive` | GET |
| **Fear & Greed** | `/api/hf-space/sentiment` | GET |
| **Sentiment Analysis** | `/api/sentiment/analyze` | POST |
| **News** | `/api/multi-source/news` | GET |
| **Gas Prices** | `/api/blockchain/gas` | GET |
| **Whales** | `/api/service/whales` | GET |
| **AI Models** | `/api/models/list` | GET |
| **Resources DB** | `/api/hf-space/resources/stats` | GET |
| **Health** | `/health` | GET |

---

## Python Usage Examples

```python
import requests

BASE_URL = "http://localhost:7860"

# Get BTC price
price = requests.get(f"{BASE_URL}/api/market/price?symbol=BTC").json()
print(f"BTC: ${price['price']:,.2f}")

# Get RSI
rsi = requests.get(f"{BASE_URL}/api/indicators/rsi?symbol=BTC&timeframe=1h").json()
print(f"RSI: {rsi['data']['value']}")

# Get comprehensive analysis
analysis = requests.get(f"{BASE_URL}/api/indicators/comprehensive?symbol=BTC").json()
print(f"Signal: {analysis['overall_signal']}")

# Get Fear & Greed
sentiment = requests.get(f"{BASE_URL}/api/hf-space/sentiment").json()
print(f"Fear & Greed: {sentiment['fear_greed_index']}")

# Analyze text sentiment
response = requests.post(
    f"{BASE_URL}/api/sentiment/analyze",
    json={"text": "Bitcoin is going to the moon!"}
)
print(f"Sentiment: {response.json()['sentiment']}")

# Get OHLCV candles
ohlcv = requests.get(f"{BASE_URL}/api/multi-source/ohlc/BTC?timeframe=1h&limit=100").json()
print(f"Candles: {len(ohlcv.get('data', []))}")

# Get news
news = requests.get(f"{BASE_URL}/api/multi-source/news?query=bitcoin&limit=10").json()
print(f"Articles: {len(news.get('articles', []))}")
```

---

*Last updated: 2025-12-12*
