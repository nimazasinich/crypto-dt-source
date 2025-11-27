# REST API Implementation for HuggingFace Space

## Overview

This document describes the REST API implementation for the HuggingFace Space crypto data gateway.
All endpoints are **pure REST HTTP** - no WebSockets are used anywhere.

## ✅ Implementation Checklist

| Component | Status | Description |
|-----------|--------|-------------|
| Provider Base | ✅ | `providers/base.py` with caching, timeouts, error handling |
| Etherscan Provider | ✅ | ETH blockchain transactions, balances, gas prices |
| BscScan Provider | ✅ | BSC blockchain transactions, balances, BEP-20 transfers |
| TronScan Provider | ✅ | TRON transactions, TRC-20 transfers, account info |
| CoinMarketCap Provider | ✅ | Market data, prices, global metrics |
| News Provider | ✅ | Crypto news, sentiment, topic search |
| HF Sentiment Provider | ✅ | AI sentiment analysis, summarization, NER |
| Blockchain Router | ✅ | 13 endpoints for ETH/BSC/TRON |
| Market Router | ✅ | 9 endpoints for market data |
| News Router | ✅ | 11 endpoints for news |
| HF Inference Router | ✅ | 9 endpoints for AI models |
| Error Logging | ✅ | `logs/provider_errors.log` |

## API Endpoints

### Blockchain Data (`/api/v1/blockchain/`)

```
GET /api/v1/blockchain/eth/transactions?address=0x...
GET /api/v1/blockchain/eth/tokens?address=0x...
GET /api/v1/blockchain/eth/balance?address=0x...
GET /api/v1/blockchain/eth/gas

GET /api/v1/blockchain/bsc/transactions?address=0x...
GET /api/v1/blockchain/bsc/tokens?address=0x...
GET /api/v1/blockchain/bsc/balance?address=0x...
GET /api/v1/blockchain/bsc/gas

GET /api/v1/blockchain/tron/transactions?address=T...
GET /api/v1/blockchain/tron/tokens?address=T...
GET /api/v1/blockchain/tron/account?address=T...
GET /api/v1/blockchain/tron/tokens/list

GET /api/v1/blockchain/health
```

### Market Data (`/api/v1/market/`)

```
GET /api/v1/market/latest?limit=50
GET /api/v1/market/quotes?symbols=BTC,ETH
GET /api/v1/market/global
GET /api/v1/market/ohlcv?symbol=BTC&interval=1h
GET /api/v1/market/map
GET /api/v1/market/top?count=10
GET /api/v1/market/price/{symbol}
GET /api/v1/market/health
```

### News & Sentiment (`/api/v1/news/`)

```
GET /api/v1/news/latest
GET /api/v1/news/crypto
GET /api/v1/news/search?keywords=bitcoin,eth
GET /api/v1/news/headlines?category=technology
GET /api/v1/news/sources
GET /api/v1/news/sentiment?text=...
GET /api/v1/news/bitcoin
GET /api/v1/news/ethereum
GET /api/v1/news/defi
GET /api/v1/news/nft
GET /api/v1/news/health
```

### HuggingFace AI (`/api/v1/hf/`)

```
POST /api/v1/hf/sentiment      {"text": "...", "use_financial": true}
GET  /api/v1/hf/sentiment?text=...
POST /api/v1/hf/summarize      {"text": "...", "max_length": 150}
POST /api/v1/hf/entities       {"text": "..."}
POST /api/v1/hf/classify       {"text": "...", "labels": ["a", "b"]}
POST /api/v1/hf/analyze        {"text": "..."}
GET  /api/v1/hf/crypto-sentiment?text=...
GET  /api/v1/hf/models
GET  /api/v1/hf/health
```

## Response Format

All endpoints return standardized JSON:

### Success Response
```json
{
  "success": true,
  "source": "provider_name",
  "data": { ... },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "source": "provider_name",
  "error": "Error description",
  "details": "Additional details...",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## Provider Features

All providers include:
- ✅ Async HTTP via `httpx.AsyncClient`
- ✅ 10-second timeout control
- ✅ 30-second in-memory caching
- ✅ Standardized JSON responses
- ✅ Error handling with try/except
- ✅ Logging to `logs/provider_errors.log`

## API Keys

The following API keys are hardcoded (to be secured later):

| Provider | Status |
|----------|--------|
| Etherscan | ⚠️ May need verification |
| BscScan | ⚠️ May need verification |
| TronScan | ✅ Working |
| CoinMarketCap | ✅ Working |
| NewsAPI | ✅ Working |
| HuggingFace | ⚠️ Token expired - needs new token |

## Running the Server

```bash
cd hf-data-engine
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then access:
- API docs: http://localhost:8000/docs
- Root: http://localhost:8000/

## Testing

```bash
cd hf-data-engine
python3 test_rest_api.py
```

## Notes

1. **No WebSockets** - All data fetched via direct HTTP GET/POST
2. **HuggingFace Space Compatible** - Works on HF Space environment
3. **Rate Limiting** - Inherits from existing app rate limiter
4. **CORS Enabled** - Allows all origins for frontend access

## File Structure

```
hf-data-engine/
├── providers/
│   ├── __init__.py
│   ├── base.py                    # Base provider with caching
│   ├── etherscan_provider.py      # Ethereum blockchain
│   ├── bscscan_provider.py        # BSC blockchain
│   ├── tronscan_provider.py       # TRON blockchain
│   ├── coinmarketcap_provider.py  # Market data
│   ├── news_provider.py           # News aggregation
│   └── hf_sentiment_provider.py   # AI sentiment
├── routers/
│   ├── __init__.py
│   ├── blockchain.py              # /api/v1/blockchain/*
│   ├── market.py                  # /api/v1/market/*
│   ├── news.py                    # /api/v1/news/*
│   └── hf_inference.py            # /api/v1/hf/*
├── logs/
│   └── provider_errors.log
├── main.py                        # FastAPI app with routers
├── test_rest_api.py               # Test script
└── REST_API_IMPLEMENTATION.md     # This document
```
