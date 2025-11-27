# Direct API Documentation

## Complete Cryptocurrency Data API with Direct Model Loading

This API provides comprehensive cryptocurrency data with **direct HuggingFace model loading** (NO PIPELINES) and seamless integration with external data sources.

---

## 🚀 Features

✅ **Direct Model Loading** - NO PIPELINES, only direct inference using AutoModel  
✅ **External API Integration** - CoinGecko, Binance, Alternative.me, Reddit, RSS feeds  
✅ **Dataset Loading** - Direct access to CryptoCoin and WinkingFace datasets  
✅ **Rate Limiting** - Built-in rate limiting with per-endpoint controls  
✅ **Real-time Data** - Market prices, news, sentiment, blockchain data  
✅ **Comprehensive Error Handling** - Detailed error messages and status codes  

---

## 📋 Table of Contents

1. [Base URL](#base-url)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Endpoints](#endpoints)
   - [CoinGecko](#coingecko-endpoints)
   - [Binance](#binance-endpoints)
   - [Alternative.me](#alternativeme-endpoints)
   - [Reddit](#reddit-endpoints)
   - [RSS Feeds](#rss-feed-endpoints)
   - [News Aggregation](#news-aggregation-endpoints)
   - [HuggingFace Models](#huggingface-model-endpoints)
   - [HuggingFace Datasets](#huggingface-dataset-endpoints)
   - [System Status](#system-status)
5. [Response Format](#response-format)
6. [Error Codes](#error-codes)
7. [Examples](#examples)

---

## Base URL

```
http://localhost:8000
```

or for production:

```
https://your-domain.com
```

---

## Authentication

Most endpoints are **public** and do not require authentication. However, some external APIs may require API keys configured as environment variables:

- `NEWSAPI_KEY` - For NewsAPI integration
- `CRYPTOPANIC_TOKEN` - For CryptoPanic integration
- `HF_API_TOKEN` - For HuggingFace API (optional, for higher rate limits)

---

## Rate Limiting

Rate limits are applied per client IP address:

| Endpoint Type | Limit | Window |
|--------------|-------|---------|
| Default | 60 requests | 1 minute |
| Sentiment Analysis | 30 requests | 1 minute |
| Model Loading | 5 requests | 1 minute |
| Dataset Loading | 5 requests | 1 minute |
| External APIs | 100 requests | 1 minute |

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640000000
```

When rate limited, you'll receive a `429` status code with retry information.

---

## Endpoints

### CoinGecko Endpoints

#### Get Cryptocurrency Prices

```http
GET /api/v1/coingecko/price
```

**Query Parameters:**
- `symbols` (optional): Comma-separated symbols (e.g., "BTC,ETH")
- `limit` (optional): Maximum number of coins (default: 100)

**Example:**
```bash
curl "http://localhost:8000/api/v1/coingecko/price?symbols=BTC,ETH"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "BTC",
      "name": "Bitcoin",
      "price": 50000.0,
      "change24h": 2.5,
      "volume24h": 50000000.0,
      "marketCap": 1000000000.0,
      "source": "coingecko"
    }
  ],
  "source": "coingecko",
  "timestamp": "2025-11-27T12:00:00"
}
```

#### Get Trending Coins

```http
GET /api/v1/coingecko/trending
```

**Query Parameters:**
- `limit` (optional): Number of trending coins (default: 10)

---

### Binance Endpoints

#### Get OHLCV Klines (Candlestick Data)

```http
GET /api/v1/binance/klines
```

**Query Parameters:**
- `symbol` (required): Symbol (e.g., "BTC", "BTCUSDT")
- `timeframe` (optional): Timeframe (1m, 5m, 15m, 1h, 4h, 1d) (default: "1h")
- `limit` (optional): Number of candles (max: 1000) (default: 1000)

**Example:**
```bash
curl "http://localhost:8000/api/v1/binance/klines?symbol=BTC&timeframe=1h&limit=100"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": 1640000000000,
      "open": 50000.0,
      "high": 51000.0,
      "low": 49500.0,
      "close": 50500.0,
      "volume": 1000000.0
    }
  ],
  "source": "binance",
  "symbol": "BTC",
  "timeframe": "1h",
  "count": 100,
  "timestamp": "2025-11-27T12:00:00"
}
```

#### Get 24h Ticker Data

```http
GET /api/v1/binance/ticker
```

**Query Parameters:**
- `symbol` (required): Symbol (e.g., "BTC")

---

### Alternative.me Endpoints

#### Get Fear & Greed Index

```http
GET /api/v1/alternative/fng
```

**Query Parameters:**
- `limit` (optional): Number of historical data points (default: 1)

**Example:**
```bash
curl "http://localhost:8000/api/v1/alternative/fng?limit=30"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "value": 75,
      "value_classification": "Greed",
      "timestamp": 1640000000,
      "time_until_update": "12h",
      "source": "alternative.me"
    }
  ],
  "metadata": {},
  "source": "alternative.me",
  "timestamp": "2025-11-27T12:00:00"
}
```

---

### Reddit Endpoints

#### Get Top Posts

```http
GET /api/v1/reddit/top
```

**Query Parameters:**
- `subreddit` (optional): Subreddit name (default: "cryptocurrency")
- `time_filter` (optional): Time filter (hour, day, week, month) (default: "day")
- `limit` (optional): Number of posts (default: 25)

**Example:**
```bash
curl "http://localhost:8000/api/v1/reddit/top?subreddit=cryptocurrency&time_filter=day&limit=25"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "abc123",
      "title": "Bitcoin reaches new high",
      "author": "crypto_enthusiast",
      "score": 1500,
      "upvote_ratio": 0.95,
      "num_comments": 200,
      "url": "https://reddit.com/...",
      "permalink": "https://reddit.com/r/cryptocurrency/...",
      "created_utc": 1640000000,
      "selftext": "Bitcoin has reached...",
      "subreddit": "cryptocurrency",
      "source": "reddit"
    }
  ],
  "subreddit": "cryptocurrency",
  "time_filter": "day",
  "count": 25,
  "source": "reddit",
  "timestamp": "2025-11-27T12:00:00"
}
```

#### Get New Posts

```http
GET /api/v1/reddit/new
```

**Query Parameters:**
- `subreddit` (optional): Subreddit name (default: "cryptocurrency")
- `limit` (optional): Number of posts (default: 25)

---

### RSS Feed Endpoints

#### Get Specific RSS Feed

```http
GET /api/v1/rss/feed
```

**Query Parameters:**
- `feed_name` (required): Feed name (coindesk, cointelegraph, bitcoinmagazine, decrypt, theblock)
- `limit` (optional): Number of articles (default: 20)

**Available Feeds:**
- `coindesk` - CoinDesk RSS feed
- `cointelegraph` - CoinTelegraph RSS feed
- `bitcoinmagazine` - Bitcoin Magazine RSS feed
- `decrypt` - Decrypt RSS feed
- `theblock` - The Block RSS feed

**Example:**
```bash
curl "http://localhost:8000/api/v1/rss/feed?feed_name=coindesk&limit=20"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "title": "Bitcoin reaches new high",
      "link": "https://coindesk.com/...",
      "summary": "Bitcoin has reached...",
      "author": "John Doe",
      "published": 1640000000,
      "source": "coindesk",
      "feed_url": "https://www.coindesk.com/arc/outboundfeeds/rss/"
    }
  ],
  "feed_name": "coindesk",
  "feed_url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
  "count": 20,
  "source": "rss",
  "timestamp": "2025-11-27T12:00:00"
}
```

#### Get All RSS Feeds

```http
GET /api/v1/rss/all
```

**Query Parameters:**
- `limit_per_feed` (optional): Articles per feed (default: 10)

#### CoinDesk RSS Direct

```http
GET /api/v1/coindesk/rss
```

**Direct endpoint:** https://www.coindesk.com/arc/outboundfeeds/rss/

#### CoinTelegraph RSS Direct

```http
GET /api/v1/cointelegraph/rss
```

**Direct endpoint:** https://cointelegraph.com/rss

---

### News Aggregation Endpoints

#### Get Latest News (Aggregated)

```http
GET /api/v1/news/latest
```

**Query Parameters:**
- `limit` (optional): Number of articles (default: 20)

This endpoint aggregates news from:
- NewsAPI (if API key configured)
- CryptoPanic (if token configured)
- RSS feeds (fallback)

---

### HuggingFace Model Endpoints

#### Sentiment Analysis (NO PIPELINE)

```http
POST /api/v1/hf/sentiment
```

**Request Body:**
```json
{
  "text": "Bitcoin price is surging to new heights!",
  "model_key": "cryptobert_elkulako"
}
```

**Available Models:**
- `cryptobert_elkulako` (default): ElKulako/cryptobert
- `cryptobert_kk08`: kk08/CryptoBERT
- `finbert`: ProsusAI/finbert
- `twitter_sentiment`: cardiffnlp/twitter-roberta-base-sentiment

**Response:**
```json
{
  "success": true,
  "text": "Bitcoin price is surging...",
  "sentiment": "positive",
  "label": "positive",
  "score": 0.95,
  "confidence": 0.95,
  "all_scores": {
    "negative": 0.02,
    "neutral": 0.03,
    "positive": 0.95
  },
  "model": "cryptobert_elkulako",
  "model_id": "ElKulako/cryptobert",
  "inference_type": "direct_no_pipeline",
  "device": "cuda",
  "timestamp": "2025-11-27T12:00:00"
}
```

#### Batch Sentiment Analysis

```http
POST /api/v1/hf/sentiment/batch
```

**Request Body:**
```json
{
  "texts": [
    "Bitcoin is mooning!",
    "Ethereum looks bearish today",
    "Market is neutral"
  ],
  "model_key": "cryptobert_elkulako"
}
```

**Response:**
```json
{
  "success": true,
  "count": 3,
  "results": [
    {
      "text": "Bitcoin is mooning!",
      "sentiment": "positive",
      "label": "positive",
      "score": 0.98,
      "confidence": 0.98
    },
    {
      "text": "Ethereum looks bearish today",
      "sentiment": "negative",
      "label": "negative",
      "score": 0.85,
      "confidence": 0.85
    },
    {
      "text": "Market is neutral",
      "sentiment": "neutral",
      "label": "neutral",
      "score": 0.92,
      "confidence": 0.92
    }
  ],
  "model": "cryptobert_elkulako",
  "model_id": "ElKulako/cryptobert",
  "inference_type": "direct_batch_no_pipeline",
  "device": "cuda",
  "timestamp": "2025-11-27T12:00:00"
}
```

#### Get Loaded Models

```http
GET /api/v1/hf/models
```

**Response:**
```json
{
  "success": true,
  "total_configured": 4,
  "total_loaded": 2,
  "device": "cuda",
  "models": [
    {
      "model_key": "cryptobert_elkulako",
      "model_id": "ElKulako/cryptobert",
      "task": "sentiment-analysis",
      "description": "CryptoBERT by ElKulako for crypto sentiment",
      "loaded": true,
      "device": "cuda"
    }
  ],
  "timestamp": "2025-11-27T12:00:00"
}
```

#### Load Specific Model

```http
POST /api/v1/hf/models/load?model_key=cryptobert_elkulako
```

**Response:**
```json
{
  "success": true,
  "model_key": "cryptobert_elkulako",
  "model_id": "ElKulako/cryptobert",
  "status": "loaded",
  "device": "cuda",
  "task": "sentiment-analysis"
}
```

#### Load All Models

```http
POST /api/v1/hf/models/load-all
```

---

### HuggingFace Dataset Endpoints

#### Get Loaded Datasets

```http
GET /api/v1/hf/datasets
```

**Response:**
```json
{
  "success": true,
  "total_configured": 5,
  "total_loaded": 2,
  "datasets": [
    {
      "dataset_key": "cryptocoin",
      "dataset_id": "linxy/CryptoCoin",
      "description": "CryptoCoin dataset by Linxy",
      "loaded": true,
      "num_rows": 50000
    }
  ],
  "timestamp": "2025-11-27T12:00:00"
}
```

#### Load Specific Dataset

```http
POST /api/v1/hf/datasets/load?dataset_key=cryptocoin&split=train
```

**Available Datasets:**
- `cryptocoin`: linxy/CryptoCoin
- `bitcoin_btc_usdt`: WinkingFace/CryptoLM-Bitcoin-BTC-USDT
- `ethereum_eth_usdt`: WinkingFace/CryptoLM-Ethereum-ETH-USDT
- `solana_sol_usdt`: WinkingFace/CryptoLM-Solana-SOL-USDT
- `ripple_xrp_usdt`: WinkingFace/CryptoLM-Ripple-XRP-USDT

#### Load All Datasets

```http
POST /api/v1/hf/datasets/load-all?streaming=false
```

#### Get Dataset Sample

```http
GET /api/v1/hf/datasets/sample?dataset_key=cryptocoin&num_samples=10
```

#### Query Dataset

```http
POST /api/v1/hf/datasets/query
```

**Request Body:**
```json
{
  "dataset_key": "bitcoin_btc_usdt",
  "filters": {"price": 50000},
  "limit": 100
}
```

#### Get Dataset Statistics

```http
GET /api/v1/hf/datasets/stats?dataset_key=cryptocoin
```

---

### System Status

#### Get System Status

```http
GET /api/v1/status
```

**Response:**
```json
{
  "success": true,
  "status": "operational",
  "models": {
    "total_configured": 4,
    "total_loaded": 2,
    "device": "cuda"
  },
  "datasets": {
    "total_configured": 5,
    "total_loaded": 2
  },
  "external_apis": {
    "coingecko": "available",
    "binance": "available",
    "alternative_me": "available",
    "reddit": "available",
    "rss_feeds": "available"
  },
  "timestamp": "2025-11-27T12:00:00"
}
```

---

## Response Format

All endpoints return standardized JSON responses:

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "source": "api_name",
  "timestamp": "2025-11-27T12:00:00"
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "status_code": 400
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - External API error |

---

## Examples

### Python Example

```python
import requests

# Get Bitcoin price from CoinGecko
response = requests.get(
    "http://localhost:8000/api/v1/coingecko/price",
    params={"symbols": "BTC"}
)
data = response.json()
print(f"Bitcoin price: ${data['data'][0]['price']}")

# Analyze sentiment
response = requests.post(
    "http://localhost:8000/api/v1/hf/sentiment",
    json={
        "text": "Bitcoin is going to the moon!",
        "model_key": "cryptobert_elkulako"
    }
)
sentiment = response.json()
print(f"Sentiment: {sentiment['sentiment']} ({sentiment['confidence']})")
```

### cURL Examples

```bash
# Get Fear & Greed Index
curl "http://localhost:8000/api/v1/alternative/fng"

# Get Binance klines
curl "http://localhost:8000/api/v1/binance/klines?symbol=BTC&timeframe=1h&limit=100"

# Get Reddit top posts
curl "http://localhost:8000/api/v1/reddit/top?subreddit=cryptocurrency&limit=10"

# Analyze sentiment
curl -X POST "http://localhost:8000/api/v1/hf/sentiment" \
  -H "Content-Type: application/json" \
  -d '{"text": "Bitcoin is mooning!", "model_key": "cryptobert_elkulako"}'

# Load all models
curl -X POST "http://localhost:8000/api/v1/hf/models/load-all"
```

---

## 🔑 Key Features Summary

### ✅ No Pipelines
- **Direct model loading** using `AutoModel` and `AutoTokenizer`
- **Direct inference** with PyTorch operations
- **No pipeline abstraction** - full control over model inference

### ✅ Complete External API Coverage
- **CoinGecko**: Real-time prices and trending coins
- **Binance**: OHLCV candlestick data
- **Alternative.me**: Fear & Greed Index
- **Reddit**: Cryptocurrency discussions
- **RSS Feeds**: News from multiple sources

### ✅ HuggingFace Integration
- **Models**: CryptoBERT, FinBERT, Twitter sentiment
- **Datasets**: CryptoCoin, WinkingFace crypto data
- **Direct loading**: No pipeline overhead

### ✅ Production Ready
- **Rate limiting**: Per-endpoint limits
- **Error handling**: Comprehensive error messages
- **CORS enabled**: Cross-origin support
- **Documentation**: Swagger UI at `/docs`

---

## 📖 Additional Resources

- **Swagger UI**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/api/health
- **System Status**: http://localhost:8000/api/v1/status

---

## 🚀 Getting Started

1. **Install dependencies**:
```bash
pip install fastapi uvicorn httpx transformers torch datasets feedparser
```

2. **Run the server**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

3. **Access API**:
```
http://localhost:8000
```

4. **View documentation**:
```
http://localhost:8000/docs
```

---

## 📝 Notes

- All models are loaded directly without pipelines
- External APIs are called directly via HTTP
- Rate limiting is applied per client IP
- CUDA is used if available, otherwise CPU
- Datasets can be loaded in streaming mode for large files

---

## 🤝 Support

For issues or questions, please refer to the documentation or check the system status endpoint.
