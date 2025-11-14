# 🚀 HuggingFace Cryptocurrency Data Engine

A production-ready cryptocurrency data aggregator that consolidates multiple data sources into unified APIs. Designed to serve as a reliable data provider for the Dreammaker Crypto Signal & Trader application.

**HuggingFace Space:** `Really-amin/Datasourceforcryptocurrency`
**Local URL:** `http://localhost:8000`

## 🎯 Features

### Core Functionality
- ✅ **Multi-Provider OHLCV Data** - Binance, Kraken with automatic fallback
- ✅ **Real-Time Prices** - Aggregated from CoinGecko, CoinCap, Binance
- ✅ **Market Sentiment** - Fear & Greed Index from Alternative.me
- ✅ **Market Overview** - Global market statistics from CoinGecko
- ✅ **Provider Health Monitoring** - Real-time status of all data sources

### Technical Features
- 🔄 **Automatic Fallback** - Seamless provider switching on failure
- ⚡ **In-Memory Caching** - Configurable TTL for optimal performance
- 🛡️ **Circuit Breaker** - Prevents repeated requests to failed services
- 📊 **Rate Limiting** - IP-based throttling for API protection
- 🔍 **Comprehensive Logging** - Detailed request and error tracking
- 📖 **OpenAPI Documentation** - Interactive API docs at `/docs`

## 📊 Supported Data

### Cryptocurrencies (14+)
BTC, ETH, SOL, XRP, BNB, ADA, DOT, LINK, LTC, BCH, MATIC, AVAX, XLM, TRX

### Timeframes
- `1m` - 1 minute
- `5m` - 5 minutes
- `15m` - 15 minutes
- `1h` - 1 hour
- `4h` - 4 hours
- `1d` - 1 day
- `1w` - 1 week

## 🚀 Quick Start

### Docker (Recommended)

```bash
# Build and run
docker build -t hf-crypto-engine .
docker run -p 8000:8000 hf-crypto-engine

# Access the API
curl http://localhost:8000/api/health
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Run the server
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access Points

- **API Root:** http://localhost:8000/
- **Health Check:** http://localhost:8000/api/health
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📡 API Endpoints

### 1️⃣ Health Check

Get service status and provider health.

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "uptime": 3600,
  "version": "1.0.0",
  "providers": [
    {
      "name": "binance",
      "status": "online",
      "latency": 120,
      "lastCheck": "2024-01-15T10:30:00Z"
    }
  ],
  "cache": {
    "size": 1250,
    "hitRate": 0.78
  }
}
```

### 2️⃣ OHLCV Data

Get candlestick (OHLCV) data with automatic provider fallback.

```http
GET /api/ohlcv?symbol=BTCUSDT&interval=1h&limit=100
```

**Parameters:**
- `symbol` (required): Symbol (e.g., `BTC`, `BTCUSDT`, `BTC/USDT`)
- `interval` (optional): Timeframe - `1m`, `5m`, `15m`, `1h`, `4h`, `1d`, `1w` (default: `1h`)
- `limit` (optional): Number of candles 1-1000 (default: `100`)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": 1699920000000,
      "open": 43250.50,
      "high": 43500.00,
      "low": 43100.25,
      "close": 43420.75,
      "volume": 125.45
    }
  ],
  "symbol": "BTCUSDT",
  "interval": "1h",
  "count": 100,
  "source": "binance",
  "timestamp": 1699920000000
}
```

**Fallback Order:** Binance → Kraken

**Cache TTL:** 5 minutes (configurable)

### 3️⃣ Real-Time Prices

Get current prices for multiple cryptocurrencies with multi-provider aggregation.

```http
GET /api/prices?symbols=BTC,ETH,SOL
```

**Parameters:**
- `symbols` (optional): Comma-separated symbols (default: all supported)
- `convert` (optional): Currency conversion - `USD`, `USDT` (default: `USDT`)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "BTC",
      "name": "Bitcoin",
      "price": 43420.75,
      "priceUsd": 43420.75,
      "change1h": 0.25,
      "change24h": 2.15,
      "change7d": -1.50,
      "volume24h": 28500000000,
      "marketCap": 850000000000,
      "rank": 1,
      "lastUpdate": "2024-01-15T10:30:00Z"
    }
  ],
  "timestamp": 1699920000000,
  "source": "coingecko+coincap+binance"
}
```

**Data Sources:** CoinGecko, CoinCap, Binance (aggregated)

**Cache TTL:** 30 seconds (configurable)

### 4️⃣ Market Sentiment

Get market sentiment indicators including Fear & Greed Index.

```http
GET /api/sentiment
```

**Response:**
```json
{
  "success": true,
  "data": {
    "fearGreed": {
      "value": 65,
      "classification": "Greed",
      "timestamp": "2024-01-15T10:00:00Z"
    },
    "news": {
      "bullish": 0,
      "bearish": 0,
      "neutral": 0,
      "total": 0
    },
    "overall": {
      "sentiment": "bullish",
      "score": 65,
      "confidence": 0.8
    }
  },
  "timestamp": 1699920000000
}
```

**Data Source:** Alternative.me Fear & Greed Index

**Cache TTL:** 10 minutes (configurable)

### 5️⃣ Market Overview

Get global market statistics and metrics.

```http
GET /api/market/overview
```

**Response:**
```json
{
  "success": true,
  "data": {
    "totalMarketCap": 1650000000000,
    "totalVolume24h": 95000000000,
    "btcDominance": 51.5,
    "ethDominance": 17.2,
    "activeCoins": 12500,
    "topGainers": [],
    "topLosers": [],
    "trending": []
  },
  "timestamp": 1699920000000
}
```

**Data Source:** CoinGecko Global API

**Cache TTL:** 5 minutes (configurable)

### 6️⃣ Cache Management

Clear cached data and view statistics.

```http
POST /api/cache/clear
GET /api/cache/stats
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Server
PORT=8000
HOST=0.0.0.0
ENV=production

# Cache TTL (seconds)
CACHE_TTL_PRICES=30
CACHE_TTL_OHLCV=300
CACHE_TTL_SENTIMENT=600

# Rate Limits (requests per minute)
RATE_LIMIT_PRICES=120
RATE_LIMIT_OHLCV=60
RATE_LIMIT_SENTIMENT=30

# Optional API Keys
COINGECKO_API_KEY=your_key_here
```

### Supported Symbols

Edit `SUPPORTED_SYMBOLS` in `.env`:

```bash
SUPPORTED_SYMBOLS=BTC,ETH,SOL,XRP,BNB,ADA,DOT,LINK,LTC,BCH,MATIC,AVAX,XLM,TRX
```

## 🐳 HuggingFace Spaces Deployment

### 1. Create README.md for HF Space

```yaml
---
title: Crypto Data Engine
emoji: 📊
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
---
```

### 2. Deploy Files

Upload these files to your HuggingFace Space:
- `Dockerfile`
- `requirements.txt`
- `main.py`
- All `core/` and `providers/` directories
- `.env.example` (rename to `.env` if setting variables)

### 3. Configure Secrets (Optional)

In Space settings, add:
- `COINGECKO_API_KEY` - For higher rate limits
- Other API keys as needed

### 4. Access Your Space

```
https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
```

## 📊 Performance

### Response Times

| Endpoint | Target | Maximum | Cache |
|----------|--------|---------|-------|
| `/api/prices` | <1s | 3s | 30s |
| `/api/ohlcv` (50 bars) | <2s | 5s | 5min |
| `/api/ohlcv` (200 bars) | <5s | 15s | 5min |
| `/api/sentiment` | <3s | 10s | 10min |
| `/api/health` | <100ms | 500ms | None |

### Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/api/prices` | 120 req/min |
| `/api/ohlcv` | 60 req/min |
| `/api/sentiment` | 30 req/min |
| `/api/health` | Unlimited |

## 🔧 Integration with Dreammaker

### Backend Configuration (.env)

```bash
HF_ENGINE_BASE_URL=http://localhost:8000
# or
HF_ENGINE_BASE_URL=https://really-amin-datasourceforcryptocurrency.hf.space

HF_ENGINE_ENABLED=true
HF_ENGINE_TIMEOUT=30000
PRIMARY_DATA_SOURCE=huggingface
```

### TypeScript Client Example

```typescript
import axios from 'axios';

const hfClient = axios.create({
  baseURL: process.env.HF_ENGINE_BASE_URL,
  timeout: 30000,
});

// Fetch OHLCV
const ohlcv = await hfClient.get('/api/ohlcv', {
  params: { symbol: 'BTCUSDT', interval: '1h', limit: 200 }
});

// Fetch Prices
const prices = await hfClient.get('/api/prices', {
  params: { symbols: 'BTC,ETH,SOL' }
});

// Fetch Sentiment
const sentiment = await hfClient.get('/api/sentiment');
```

## 🛡️ Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "PROVIDER_ERROR",
    "message": "All data providers are currently unavailable",
    "details": {
      "binance": "HTTP 403",
      "kraken": "Timeout"
    },
    "retryAfter": 60
  },
  "timestamp": 1699920000000
}
```

### Error Codes

- `INVALID_SYMBOL` - Unknown cryptocurrency symbol
- `INVALID_INTERVAL` - Unsupported timeframe
- `PROVIDER_ERROR` - All providers failed
- `RATE_LIMITED` - Too many requests
- `INTERNAL_ERROR` - Server error

## 📈 Monitoring

### Logs

All requests and errors are logged:

```
2024-01-15 10:30:00 - INFO - Trying binance for OHLCV data: BTCUSDT 1h
2024-01-15 10:30:00 - INFO - Successfully fetched 100 candles from binance
```

### Health Monitoring

Monitor provider status via `/api/health`:
- `online` - Provider working normally
- `degraded` - Recent errors but still functional
- `offline` - Circuit breaker open, provider unavailable

## 🧪 Testing

### Manual Testing

```bash
# Health check
curl http://localhost:8000/api/health

# OHLCV data
curl "http://localhost:8000/api/ohlcv?symbol=BTC&interval=1h&limit=10"

# Prices
curl "http://localhost:8000/api/prices?symbols=BTC,ETH"

# Sentiment
curl http://localhost:8000/api/sentiment

# Market overview
curl http://localhost:8000/api/market/overview
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/prices?symbols=BTC

# Using k6
k6 run loadtest.js
```

## 📝 Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│  ┌────────────────────────────────────┐ │
│  │  Rate Limiter (SlowAPI)            │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │  Cache Layer (In-Memory)           │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │  Data Aggregator                   │ │
│  │  ┌──────────┬──────────┬─────────┐ │ │
│  │  │ Binance  │ Kraken   │CoinGecko│ │ │
│  │  └──────────┴──────────┴─────────┘ │ │
│  │  ┌──────────────────────────────┐  │ │
│  │  │  Circuit Breaker             │  │ │
│  │  └──────────────────────────────┘  │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Binance** - Primary OHLCV data source
- **CoinGecko** - Price and market data
- **Alternative.me** - Fear & Greed Index
- **CoinCap** - Real-time price data
- **Kraken** - Backup OHLCV provider

---

**Made with ❤️ for the Crypto Community**

**Version:** 1.0.0
**Last Updated:** 2024-01-15
