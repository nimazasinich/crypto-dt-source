---
title: Crypto Intelligence Hub API
sdk: docker
app_port: 7860
---

## Description
FastAPI service that provides **real cryptocurrency market/news/sentiment data** with provider rotation, caching, and failover (no mock/random market data fallbacks).

## Usage
- **Health**: `GET /health` (also `GET /api/health`)
- **Docs**: `GET /docs`

### Core endpoints (HF router)
- `GET /api/market`
- `GET /api/market/ohlc?symbol=BTC&interval=60&limit=100`
- `GET /api/news`
- `GET /api/sentiment/global`
- `GET /api/crypto/blockchain/gas`
- `GET /api/status`

## Environment variables
Set these in **Hugging Face Spaces → Settings → Secrets** (optional but recommended):
- `COINGECKO_PRO_API_KEY`
- `CRYPTOPANIC_API_KEY`
- `NEWS_API_KEY`
- `ETHERSCAN_API_KEY`
- `ETHERSCAN_API_KEY_2`

## Notes
- Startup is optimized for Spaces: background workers/monitors/models are disabled by default.
- Binance OHLC can be geo-blocked (HTTP 451); the service automatically fails over to CoinGecko OHLC and cools down the failing provider.
