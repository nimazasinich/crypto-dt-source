---
title: Crypto API Monitor
emoji: 🔐
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
tags:
  - cryptocurrency
  - api-monitoring
  - real-time
  - fastapi
  - websocket
  - blockchain
---

# 🔐 Crypto API Monitoring System

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Real-time Cryptocurrency API Resource Monitoring & Health Tracking**

[Live Demo](#) | [Documentation](#features) | [API Docs](#api-endpoints)

</div>

---

## 📋 Overview

A comprehensive, production-ready monitoring system for cryptocurrency APIs. Track health, performance, rate limits, and data freshness across 21+ crypto data sources in real-time.

### ✨ Key Features

- 🔄 **Real-time Monitoring**: WebSocket-based live updates
- 📊 **21+ Data Sources**: Market data, blockchain explorers, news, sentiment
- 🎯 **Health Tracking**: Automated checks every 5 minutes
- 📈 **Performance Metrics**: Response times, success rates, uptime
- ⚡ **Rate Limit Management**: Per-provider tracking and alerts
- 🗄️ **Historical Data**: SQLite-based persistence
- 🎨 **Modern UI**: Responsive dashboard with real-time charts
- 🔌 **RESTful API**: 16+ comprehensive endpoints
- 🌐 **WebSocket Streams**: Multiple specialized channels
- 📅 **Smart Scheduling**: APScheduler for automated tasks

---

## 🚀 Quick Start

### Option 1: Hugging Face Spaces (Recommended)

1. **Clone this Space** or **Duplicate** it
2. **Add your API keys** in Space Settings → Repository Secrets:
   ```
   ETHERSCAN_KEY_1=your_key_here
   COINMARKETCAP_KEY_1=your_key_here
   NEWSAPI_KEY=your_key_here
   ```
3. **Restart the Space** - Your monitor will be live!

### Option 2: Local Docker

```bash
# Clone the repository
git clone https://github.com/nimazasinich/crypto-dt-source.git
cd crypto-dt-source

# Copy environment file
cp .env.example .env
# Edit .env and add your API keys

# Run with Docker Compose
docker-compose up -d

# Access at http://localhost:7860
```

### Option 3: Local Python

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ETHERSCAN_KEY_1=your_key_here
export COINMARKETCAP_KEY_1=your_key_here

# Run the application
uvicorn app:app --host 0.0.0.0 --port 7860
```

---

## 📊 Data Sources

### 🔸 Market Data (6 sources)
- **CoinGecko** - Free, 50 req/min
- **CoinMarketCap** - Requires API key
- **CryptoCompare** - Requires API key
- **Binance** - Public API
- **Coinbase** - Public API
- **Kraken** - Public API

### 🔸 Blockchain Explorers (3 sources)
- **Etherscan** - Ethereum (Requires API key)
- **BscScan** - BSC (Requires API key)
- **TronScan** - Tron (Requires API key)

### 🔸 News Sources (4 sources)
- **CryptoPanic** - Free aggregator
- **NewsAPI** - Requires API key
- **CoinTelegraph** - RSS feed
- **Bitcoin.com** - RSS feed

### 🔸 RPC Nodes (4 sources)
- Ethereum Mainnet
- BSC Mainnet
- Polygon
- Arbitrum

### 🔸 Others (4 sources)
- **AlternativeMe** - Fear & Greed Index
- **Whale Alert** - Large transactions
- **The Graph** - On-chain analytics
- **Blockchair** - Multi-blockchain explorer

**Total: 21 Data Sources**

---

## 🎨 Dashboard Features

### 📈 Real-time Metrics
- Total APIs tracked
- Online/Offline status
- Average response time
- System health score

### 📊 Interactive Charts
- 24-hour health history
- Rate limit usage trends
- Data freshness timeline
- Error distribution analysis

### 🗂️ Multiple Views
- **Dashboard**: Overview with KPI cards
- **Provider Inventory**: Detailed provider list
- **Rate Limits**: Usage tracking per provider
- **Connection Logs**: Recent API calls
- **Schedule Status**: Task execution timeline
- **Data Freshness**: Staleness monitoring
- **Failure Analysis**: Error tracking & remediation
- **Configuration**: API key management

---

## 🔌 API Endpoints

### Status & Monitoring
```http
GET /api/status              # System overview
GET /api/health              # Health check
GET /api/providers           # Provider list
GET /api/categories          # Category statistics
```

### Logs & History
```http
GET /api/logs                # Connection attempts
GET /api/failures            # Failure analysis
GET /api/schedule            # Schedule status
GET /api/freshness           # Data staleness
```

### Charts & Analytics
```http
GET /api/charts/health-history      # 24h success rate
GET /api/charts/compliance          # Schedule compliance
GET /api/charts/rate-limit-history  # Rate limit usage
GET /api/charts/freshness-history   # Data age trends
```

### WebSocket Streams
```
ws://host/ws/live            # Real-time updates
ws://host/ws/market_data     # Market data stream
ws://host/ws/health          # Health check stream
ws://host/ws/master          # Master stream with subscriptions
```

---

## 🔧 Configuration

### Required API Keys

Only 3 providers **require** API keys for full functionality:

1. **Etherscan** (Ethereum Explorer)
   - Get at: https://etherscan.io/myapikey
   - Free tier: 5 calls/second

2. **CoinMarketCap** (Market Data)
   - Get at: https://pro.coinmarketcap.com/signup
   - Free tier: 333 calls/day

3. **NewsAPI** (News Aggregation)
   - Get at: https://newsapi.org/register
   - Free tier: 100 requests/day

### Optional API Keys

For extended functionality:
- **BscScan**, **TronScan** - Additional blockchain explorers
- **CryptoCompare** - Enhanced market data
- **Hugging Face** - AI/ML features

### Environment Variables

```bash
# Core Settings
APP_ENV=production
LOG_LEVEL=info
PORT=7860

# Required Keys
ETHERSCAN_KEY_1=your_key
COINMARKETCAP_KEY_1=your_key
NEWSAPI_KEY=your_key

# Optional Keys
BSCSCAN_KEY=your_key
CRYPTOCOMPARE_KEY=your_key
HUGGINGFACE_KEY=your_token
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                 Frontend (HTML/JS)               │
│  • Real-time Dashboard                           │
│  • WebSocket Client                              │
│  • Chart.js Visualizations                       │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│           FastAPI Backend (Python)               │
│  • REST API (16 endpoints)                       │
│  • WebSocket Server (8 channels)                 │
│  • Background Schedulers                         │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
┌───────▼────┐ ┌──▼──────┐ ┌─▼────────────┐
│ Collectors │ │Database │ │ Rate Limiter │
│ (21 APIs)  │ │(SQLite) │ │              │
└────────────┘ └─────────┘ └──────────────┘
```

---

## 📦 Tech Stack

- **Backend**: FastAPI 0.104, Python 3.10+
- **Database**: SQLAlchemy + SQLite
- **Scheduling**: APScheduler 3.10
- **WebSocket**: Native FastAPI WebSockets
- **HTTP Client**: httpx + aiohttp
- **Charts**: Chart.js 4.4
- **Frontend**: Vanilla JavaScript + HTML5/CSS3

---

## 🐳 Docker Deployment

### Quick Start
```bash
docker-compose up -d
```

### Custom Configuration
```bash
# Build image
docker build -t crypto-monitor .

# Run container
docker run -d \
  -p 7860:7860 \
  -v $(pwd)/data:/app/data \
  -e ETHERSCAN_KEY_1=your_key \
  crypto-monitor
```

---

## 📈 Performance

- **Startup Time**: ~5-10 seconds
- **API Response**: <100ms average
- **WebSocket Latency**: <50ms
- **Memory Usage**: ~200-400MB
- **Database Size**: ~10-50MB after 24h

---

## 🔒 Security

- ✅ Non-root Docker user
- ✅ API key masking in logs
- ✅ Rate limiting on endpoints
- ✅ CORS configuration
- ✅ Health checks
- ✅ No hardcoded secrets

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/nimazasinich/crypto-dt-source/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nimazasinich/crypto-dt-source/discussions)

---

<div align="center">

**Made with ❤️ for the Crypto Community**

⭐ Star this repo if you find it useful!

</div>
