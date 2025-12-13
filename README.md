---
title: Unified Crypto Data Platform
sdk: docker
app_port: 7860
---

# Unified Crypto Data Platform 🚀

**Version**: 2.0.0 (Production Ready)
**Port**: 7860
**Status**: 🟢 Active

## 📖 Project Overview

The **Unified Crypto Data Platform** is a high-performance, real-time cryptocurrency data aggregation engine designed for production environments. It replaces all mock/simulated data with real-world feeds from top-tier providers, orchestrated by an intelligent rotation and caching system.

This platform provides a unified API interface for:
- **Market Data**: Live prices, OHLCV candles, 24h stats.
- **News Aggregation**: Real-time crypto news from multiple sources.
- **Sentiment Analysis**: Fear & Greed index and AI-driven sentiment scoring.
- **On-Chain Metrics**: Gas prices and blockchain statistics.

## 🏗️ Architecture

The system is built on a robust 3-layer architecture designed for reliability and speed:

### 1. **Provider Orchestrator** (`backend/orchestration`)
The heart of the system. It manages all external API interactions.
- **Round-Robin Rotation**: Distributes load across multiple providers (e.g., CoinGecko Free -> CoinGecko Pro -> Binance).
- **Auto-Failover**: Instantly detects API failures (429, 500, timeouts) and switches to the next healthy provider.
- **Circuit Breaker**: "Cools down" failed providers to prevent cascading failures.
- **Rate Limiting**: Enforces strict per-provider request limits to avoid bans.

### 2. **Caching Layer** (`backend/cache`)
An asynchronous, in-memory TTL (Time-To-Live) cache.
- **Deduplication**: Identical requests within the TTL window (default 60s) return cached data instantly.
- **Latency Reduction**: Reduces API calls by up to 90% under heavy load.

### 3. **Unified API Gateway** (`hf_unified_server.py`)
FastAPI-based server exposing clean, standardized endpoints.
- **Standardized Responses**: Regardless of the underlying provider (Binance vs CoinGecko), the API returns data in a consistent JSON format.
- **Metadata**: Responses include source information (`coingecko_pro`, `binance`) and latency metrics.

## 🔌 Real Data Resources

The platform is integrated with the following real-time data sources:

| Category | Primary Provider | Fallback Provider | Data Points |
|----------|------------------|-------------------|-------------|
| **Market** | **CoinGecko Pro** | Binance, CoinGecko Free | Prices, Vol, Mkt Cap |
| **OHLCV** | **Binance** | CoinGecko | Candlesticks (1m-1d) |
| **News** | **CryptoPanic** | NewsAPI | Headlines, Source, Sentiment |
| **Sentiment**| **Alternative.me** | - | Fear & Greed Index |
| **On-Chain** | **Etherscan** | Backup Etherscan Key | Gas Prices (Fast/Std/Slow) |

## 🆕 Newly Integrated Data Sources (Dec 2025)

### 1. **Crypto API Clean** - Resource Database
- **URL**: https://really-amin-crypto-api-clean-fixed.hf.space
- **Resources**: 281+ cryptocurrency resources
- **Categories**: 12 comprehensive categories
- **Priority**: 2 (High)
- **Features**:
  - 24 RPC Nodes (Ethereum, Polygon, BSC, Arbitrum, etc.)
  - 33 Block Explorers (Etherscan, BscScan, PolygonScan, etc.)
  - 33 Market Data APIs
  - 17 News APIs  
  - 14 Sentiment APIs
  - 14 On-Chain Analytics APIs
  - 10 Whale Tracking APIs
  - 9 HuggingFace Resources
  - 13 Free HTTP Endpoints
  - 7 CORS Proxies
  - 106 Local Backend Routes
  - 1 Community Sentiment API
- **Endpoints**: `/api/new-sources/crypto-api-clean/*`

### 2. **Crypto DT Source** - Unified Data API v2.0.0
- **URL**: https://crypto-dt-source.onrender.com
- **Description**: Unified cryptocurrency data API with AI models
- **Priority**: 2 (High)
- **Features**:
  - **4 AI Sentiment Models**:
    - kk08/CryptoBERT
    - cardiffnlp/twitter-roberta-base-sentiment-latest
    - ProsusAI/finbert
    - ElKulako/cryptobert
  - **5 Crypto Datasets**:
    - linxy/CryptoCoin
    - WinkingFace/CryptoLM-Bitcoin-BTC-USDT
    - WinkingFace/CryptoLM-Ethereum-ETH-USDT
    - WinkingFace/CryptoLM-Solana-SOL-USDT
    - WinkingFace/CryptoLM-Ripple-XRP-USDT
  - **Real-Time Data**:
    - CoinGecko prices (100+ cryptocurrencies)
    - Binance candlestick/OHLCV data
    - Fear & Greed Index (Alternative.me)
    - Reddit posts (r/cryptocurrency)
    - RSS news feeds (5 sources)
- **Endpoints**: `/api/new-sources/crypto-dt-source/*`

### Combined Resources
- **Total Resources**: 283+ (281 new + 2 base)
- **AI Models**: 4 sentiment analysis models
- **Datasets**: 5 comprehensive crypto datasets
- **New API Endpoints**: 20+
- **Automatic Fallback**: Integrated with health tracking

## 🚀 Installation & Usage

### 1. Prerequisites
- Python 3.9+
- `pip`

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file (optional, defaults provided for free tiers):
```env
# Server Config
PORT=7860
HOST=0.0.0.0

# API Keys (Optional - Free tiers used by default)
COINGECKO_PRO_API_KEY=your_key
CRYPTOPANIC_API_KEY=your_key
ETHERSCAN_API_KEY=your_key
NEWS_API_KEY=your_key
```

### 4. Run the Server
```bash
python run_server.py
```
The server will start at **http://0.0.0.0:7860**

## 📡 API Endpoints

### Market Data
- **Snapshot**: `GET /api/market`
  - Returns top coins with prices, changes, and volume.
- **OHLCV**: `GET /api/market/ohlc?symbol=BTC&interval=1h`
  - Returns historical candlestick data.

### Intelligence
- **News**: `GET /api/news?filter=hot`
  - Returns latest crypto news articles.
- **Sentiment**: `GET /api/sentiment/global`
  - Returns current market sentiment (Fear/Greed).

### Infrastructure
- **Gas Prices**: `GET /api/crypto/blockchain/gas`
  - Returns current Ethereum gas fees.
- **System Status**: `GET /api/status`
  - Returns provider health, cache stats, and rotation metrics.

## 🧪 Verification & Monitoring

### Check Provider Health
```bash
curl http://localhost:7860/api/status
```
Look for `"status": "active"` for registered providers.

### Verify Rotation
Run the market endpoint multiple times to see the `source` field change (if load requires rotation):
```bash
curl http://localhost:7860/api/market
```

### Logs
System logs track rotation events, failures, and recoveries:
- `logs/provider_rotation.log`
- `logs/provider_failures.log`
- `logs/provider_health.log`

## 🛠 Work Accomplished (Report)

1.  **Mock Data Elimination**: Removed all static JSON files and random number generators (`hf_space_api.py`, `ohlcv_service.py`).
2.  **Provider Orchestrator**: Implemented `backend/orchestration/provider_manager.py` to handle intelligent routing and failover.
3.  **Real Implementations**:
    - Created `backend/live_data/providers.py` with specific fetchers for CoinGecko, Binance, CryptoPanic, etc.
    - Updated API routers to use the Orchestrator instead of direct logic.
4.  **Performance Optimization**:
    - Added `TTLCache` to prevent API rate-limiting.
    - Implemented request batching where supported.
5.  **Robustness**:
    - Added global exception handling and standardized error responses.
    - Configured automatic retries and cooldowns for unstable providers.

---
*Built for reliability and scale.*
