---
title: Crypto Data Engine
emoji: 📊
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
---

# 🚀 Cryptocurrency Data Engine

A production-ready cryptocurrency data aggregator providing unified APIs for OHLCV data, real-time prices, market sentiment, and more.

## 🎯 Features

- **OHLCV Data** - Historical candlestick data from Binance, Kraken
- **Real-Time Prices** - Aggregated prices from multiple providers
- **Market Sentiment** - Fear & Greed Index and sentiment analysis
- **Market Overview** - Global crypto market statistics
- **Multi-Provider Fallback** - Automatic failover for reliability
- **Caching & Rate Limiting** - Optimized for performance

## 📡 API Endpoints

### Get OHLCV Data
```
GET /api/ohlcv?symbol=BTC&interval=1h&limit=100
```

### Get Real-Time Prices
```
GET /api/prices?symbols=BTC,ETH,SOL
```

### Get Market Sentiment
```
GET /api/sentiment
```

### Get Market Overview
```
GET /api/market/overview
```

### Health Check
```
GET /api/health
```

## 📖 Documentation

Interactive API documentation available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## 🔗 Supported Cryptocurrencies

BTC, ETH, SOL, XRP, BNB, ADA, DOT, LINK, LTC, BCH, MATIC, AVAX, XLM, TRX

## 🕒 Supported Timeframes

1m, 5m, 15m, 1h, 4h, 1d, 1w

## 🛡️ Data Sources

- **Binance** - OHLCV and price data
- **Kraken** - Backup OHLCV provider
- **CoinGecko** - Comprehensive market data
- **CoinCap** - Real-time prices
- **Alternative.me** - Fear & Greed Index

## 📊 Use Cases

Perfect for:
- Trading bots and algorithms
- Market analysis applications
- Portfolio tracking systems
- Educational projects
- Research and backtesting

## 🚀 Getting Started

Try the API right now:

```bash
# Get Bitcoin price
curl https://YOUR_SPACE_URL/api/prices?symbols=BTC

# Get hourly OHLCV data
curl https://YOUR_SPACE_URL/api/ohlcv?symbol=BTCUSDT&interval=1h&limit=10

# Check service health
curl https://YOUR_SPACE_URL/api/health
```

## 📝 Rate Limits

- Prices: 120 requests/minute
- OHLCV: 60 requests/minute
- Sentiment: 30 requests/minute
- Health: Unlimited

## 🤝 Integration

Designed to work seamlessly with the Dreammaker Crypto Signal & Trader application and other cryptocurrency analysis tools.

---

**Version:** 1.0.0
**License:** MIT
