# Data Source Quick Reference

**Last Updated:** 2025-11-28

Quick reference guide for all data sources used in the Crypto Intelligence Hub.

---

## API Endpoints Summary

### Production Server (`production_server.py`)

Base URL: `http://localhost:7860/api`

| Endpoint | Method | Purpose | Data Source | Cache |
|----------|--------|---------|-------------|-------|
| `/status` | GET | System status | Real API checks | 30s |
| `/providers` | GET | Provider list | api_loader | 30s |
| `/resources` | GET | Resource stats | api_loader | 30s |
| `/trending` | GET | Trending coins | Mock/Real | 30s |
| `/sentiment/global` | GET | Global sentiment | Mock | 30s |
| `/news/latest` | GET | Latest news | Mock | 5m |
| `/models/list` | GET | AI models list | Static | - |
| `/ai/decision` | POST | AI decision | AI models | - |

### Data Hub API (`data_hub_api.py`)

Base URL: `http://localhost:7860/api/v2/data-hub`

| Endpoint | Method | Purpose | Data Source | Cache |
|----------|--------|---------|-------------|-------|
| `/market/prices` | GET | Market prices | HF→CMC→CG→BIN | 30s |
| `/market/ohlcv` | GET | OHLCV data | BIN→CMC→HF | 60s |
| `/sentiment/fear-greed` | GET | Fear & Greed | Alternative.me | 1h |
| `/sentiment/analyze` | POST | Sentiment AI | HF AI models | - |
| `/news` | GET | Crypto news | NewsAPI→Reddit | 5m |
| `/trending` | GET | Trending coins | CoinGecko | 3m |
| `/blockchain/{chain}` | GET | Blockchain data | Explorer APIs | 60s |
| `/whales` | GET | Whale activity | HF Space | 30s |
| `/social/{platform}` | GET | Social data | Reddit | 2m |
| `/ai/predict/{symbol}` | GET | AI prediction | HF AI models | - |
| `/dashboard` | GET | Dashboard data | Multiple | Varies |
| `/health` | GET | System health | All sources | - |

### Real Data API (`real_data_api.py`)

Base URL: `http://localhost:7860/api`

| Endpoint | Method | Purpose | Data Source | Cache |
|----------|--------|---------|-------------|-------|
| `/market` | GET | Market snapshot | HF→CMC | 30s |
| `/market/pairs` | GET | Trading pairs | HF→CMC | 5m |
| `/market/ohlc` | GET | OHLC data | CMC→BIN | 2m |
| `/market/tickers` | GET | Sorted tickers | CMC | 60s |
| `/news` | GET | Crypto news | NewsAPI | 5m |
| `/blockchain/transactions` | GET | Blockchain txs | Explorers | 60s |
| `/blockchain/gas` | GET | Gas prices | Explorers | 60s |
| `/models/{key}/predict` | POST | AI prediction | HF AI | - |
| `/sentiment/analyze` | POST | Sentiment AI | HF AI | - |

### Unified Service API (`unified_service_api.py`)

Base URL: `http://localhost:7860/api/service`

| Endpoint | Method | Purpose | Data Source | Cache |
|----------|--------|---------|-------------|-------|
| `/rate` | GET | Single rate | HF→WS→Fallback | 10s |
| `/rate/batch` | GET | Batch rates | Multiple | 10s |
| `/pair/{pair}` | GET | Pair metadata | HF→Fallback | - |
| `/sentiment` | GET | Sentiment | HF AI | - |
| `/econ-analysis` | POST | Econ analysis | HF AI | - |
| `/history` | GET | Historical OHLC | HF→BIN | 60s |
| `/market-status` | GET | Market overview | HF | 30s |
| `/top` | GET | Top N coins | HF | 60s |
| `/whales` | GET | Whale txs | HF | 60s |
| `/onchain` | GET | On-chain data | Explorers | 60s |
| `/query` | POST | Generic query | Routes to above | Varies |

---

## External Data Sources

### 1. Hugging Face Space (Primary)

**URL:** `https://really-amin-datasourceforcryptocurrency.hf.space`  
**Authentication:** Bearer token (HF_API_TOKEN)  
**Rate Limit:** N/A (self-hosted)  
**Priority:** 1 (Primary for most endpoints)

**Capabilities:**
- Market data aggregation
- AI model inference (sentiment, prediction)
- Historical OHLCV data
- News aggregation
- Whale transaction tracking
- Blockchain statistics

**Endpoints Used:**
- `GET /api/market` - Market data
- `GET /api/market/history` - OHLCV
- `POST /api/sentiment/analyze` - Sentiment
- `GET /api/news` - News
- `GET /api/crypto/whales/transactions` - Whales
- `GET /api/health` - Health check

### 2. CoinMarketCap

**URL:** `https://pro-api.coinmarketcap.com/v1`  
**API Key:** `a35ffaec-c66c-4f16-81e3-41a717e4822f`  
**Rate Limit:** 333 calls/minute  
**Priority:** 2 (Fallback for market data)

**Endpoints Used:**
- `/cryptocurrency/listings/latest` - Top cryptos
- `/cryptocurrency/quotes/latest` - Specific quotes
- `/cryptocurrency/quotes/historical` - Historical data

**Cost:** Paid API (Basic plan)

### 3. CoinGecko

**URL:** `https://api.coingecko.com/api/v3`  
**API Key:** None (Free)  
**Rate Limit:** 50 calls/minute  
**Priority:** 3 (Second fallback for market data)

**Endpoints Used:**
- `/simple/price` - Simple prices
- `/coins/markets` - Market data with details
- `/search/trending` - Trending coins

**Cost:** Free

### 4. Binance

**URL:** `https://api.binance.com/api/v3`  
**API Key:** None (Public API)  
**Rate Limit:** 1200 calls/minute  
**Priority:** 1 for OHLCV, 4 for market data

**Endpoints Used:**
- `/klines` - OHLCV candlestick data (PRIMARY for historical)
- `/ticker/24hr` - 24-hour ticker data

**Cost:** Free

### 5. NewsAPI

**URL:** `https://newsapi.org/v2`  
**API Key:** `968a5e25552b4cb5ba3280361d8444ab`  
**Rate Limit:** 500 calls/hour  
**Priority:** 1 for news

**Endpoints Used:**
- `/everything` - Search crypto news
- `/top-headlines` - Top headlines

**Cost:** Paid API (Developer plan)

### 6. Etherscan

**URL:** `https://api.etherscan.io/api`  
**API Key:** `T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45`  
**Rate Limit:** 5 calls/second  
**Priority:** 1 for Ethereum data

**Endpoints Used:**
- `?module=account&action=txlist` - Transactions
- `?module=account&action=balance` - Balance
- `?module=gastracker&action=gasoracle` - Gas prices

**Cost:** Free

### 7. BSCScan

**URL:** `https://api.bscscan.com/api`  
**API Key:** `K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT`  
**Rate Limit:** 5 calls/second  
**Priority:** 1 for BSC data

**Endpoints Used:**
- `?module=account&action=txlist` - Transactions
- `?module=account&action=balance` - Balance

**Cost:** Free

### 8. Tronscan

**URL:** `https://apilist.tronscan.org/api`  
**API Key:** `7ae72726-bffe-4e74-9c33-97b761eeea21`  
**Rate Limit:** 10 calls/second  
**Priority:** 1 for Tron data

**Endpoints Used:**
- `/transaction` - Recent transactions
- `/account/{address}` - Account info

**Cost:** Free

### 9. Alternative.me

**URL:** `https://api.alternative.me`  
**API Key:** None (Free)  
**Rate Limit:** N/A  
**Priority:** Exclusive for Fear & Greed

**Endpoints Used:**
- `/fng/` - Fear & Greed Index

**Cost:** Free

### 10. Reddit

**URL:** `https://www.reddit.com/r`  
**API Key:** None (Public)  
**Rate Limit:** ~60 requests/minute  
**Priority:** 2 for news, 1 for social

**Subreddits Monitored:**
- r/CryptoCurrency
- r/Bitcoin
- r/ethereum
- r/defi

**Cost:** Free

---

## Fallback Chains

### Market Data
1. Hugging Face Space
2. CoinMarketCap (with API key)
3. CoinGecko (free)
4. Binance (free)

### OHLCV Historical Data
1. Binance (PRIMARY - best free source)
2. CoinMarketCap
3. Hugging Face Space

### News
1. NewsAPI (with API key)
2. Reddit (free)
3. Hugging Face Space aggregation

### Blockchain Data
1. Chain-specific explorer (Etherscan/BSCScan/Tronscan)
2. Hugging Face Space

### Sentiment Analysis
1. Hugging Face AI models (EXCLUSIVE)
2. No fallback (real-time AI only)

### Fear & Greed Index
1. Alternative.me (EXCLUSIVE)
2. No fallback

---

## Cache TTL Summary

| Data Type | Frontend | Backend | Database | Reason |
|-----------|----------|---------|----------|--------|
| Market Prices | 30s | 30s | 60s | Fast-changing |
| OHLCV Data | 60s | 60s | 300s | Historical, stable |
| News | 300s | 300s | 1800s | Rarely changes |
| Sentiment | 0s | 0s | 60s | Real-time |
| Fear & Greed | 300s | 3600s | 7200s | Updated hourly |
| Blockchain | 60s | 60s | 300s | Moderate changes |
| Trending | 180s | 180s | 600s | Updates often |
| Provider Status | 30s | 30s | N/A | Real-time monitor |

---

## Frontend API Client Methods

**File:** `/workspace/static/shared/js/core/api-client.js`

```javascript
// System
api.getHealth()
api.getStatus()
api.getStats()
api.getResources()

// Market
api.getMarket()
api.getTrending()
api.getTopCoins(limit)
api.getCoinDetails(symbol)
api.getPriceChart(symbol, timeframe)

// News
api.getLatestNews(limit)
api.analyzeNews(title, content)
api.summarizeNews(title, content)

// AI/ML
api.getModelsList()
api.getModelsStatus()
api.testModel(modelName, input)
api.analyzeSentiment(text, mode, model)
api.getGlobalSentiment()
api.getAIDecision(symbol, horizon, risk, context, model)

// Providers
api.getProviders()
api.getProviderDetails(id)
api.checkProviderHealth(id)

// Diagnostics
api.getLogs()
api.getRecentLogs(limit)
api.getErrorLogs(limit)
```

---

## Database Models

**File:** `/workspace/database/models.py`

### CachedMarketData
- id (primary key)
- symbol (varchar)
- price (float)
- market_cap (float)
- volume_24h (float)
- change_24h (float)
- provider (varchar)
- fetched_at (datetime)

### CachedOHLC
- id (primary key)
- symbol (varchar)
- interval (varchar)
- timestamp (bigint)
- open (float)
- high (float)
- low (float)
- close (float)
- volume (float)
- provider (varchar)

### SentimentMetric
- id (primary key)
- metric_name (varchar)
- value (float)
- classification (varchar)
- source (varchar)
- created_at (datetime)

### WhaleTransaction
- id (primary key)
- blockchain (varchar)
- transaction_hash (varchar)
- from_address (varchar)
- to_address (varchar)
- amount (float)
- amount_usd (float)
- timestamp (datetime)
- source (varchar)

### NewsArticle
- id (primary key)
- title (text)
- content (text)
- url (varchar)
- source (varchar)
- published_at (datetime)
- sentiment_score (float)

### GasPrice
- id (primary key)
- blockchain (varchar)
- safe_price (float)
- standard_price (float)
- fast_price (float)
- unit (varchar)
- fetched_at (datetime)

### BlockchainStat
- id (primary key)
- blockchain (varchar)
- metric_name (varchar)
- value (float)
- fetched_at (datetime)

---

## Environment Variables

Required environment variables for the application:

```bash
# Hugging Face
HF_API_TOKEN=<your_token>
HF_SPACE_BASE_URL=https://really-amin-datasourceforcryptocurrency.hf.space

# Market Data
COINMARKETCAP_API_KEY=a35ffaec-c66c-4f16-81e3-41a717e4822f

# News
NEWSAPI_API_KEY=968a5e25552b4cb5ba3280361d8444ab

# Blockchain Explorers
ETHERSCAN_API_KEY=T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45
BSCSCAN_API_KEY=K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT
TRONSCAN_API_KEY=7ae72726-bffe-4e74-9c33-97b761eeea21

# Database
DATABASE_URL=sqlite:///./crypto_data.db  # or PostgreSQL URL

# Server
PORT=7860
HOST=0.0.0.0
```

---

## Page Data Sources Summary

| Page | Primary Endpoints | Data Sources | Refresh |
|------|------------------|--------------|---------|
| Dashboard | `/api/resources`, `/api/status`, `/api/trending` | Production Server → Multiple | 30s |
| Market | `/api/market`, `/api/market/ohlcv` | HF→CMC→CG→BIN | 30s |
| News | `/api/news` | NewsAPI, Reddit | 5m |
| Sentiment | `/api/sentiment/fear-greed`, `/api/sentiment/analyze` | Alternative.me, HF AI | 1h/RT |
| Models | `/api/models/list` | Static/AI Registry | - |
| AI Analyst | `/api/ai/decision`, `/api/ai/predict` | HF AI Models | RT |
| Trading Assistant | `/api/trading/signal` | HF AI Models | RT |
| Providers | `/api/providers` | Production Server → Health Checks | 30s |
| Diagnostics | `/api/health`, `/api/logs` | All Sources | RT |

**Legend:**
- RT = Real-time (no cache)
- HF = Hugging Face Space
- CMC = CoinMarketCap
- CG = CoinGecko
- BIN = Binance

---

## AI Models Available

**Source:** Hugging Face Space

1. **sentiment-crypto** - Crypto-specific sentiment analysis
   - Input: Text
   - Output: Label (positive/negative/neutral), Score (0-1)

2. **sentiment-financial** - Financial news sentiment
   - Input: Text
   - Output: Label, Score, Confidence

3. **sentiment-twitter** - Social media sentiment
   - Input: Tweet text
   - Output: Label, Score

4. **price-prediction** - Price prediction model
   - Input: Symbol, timeframe
   - Output: Predicted price, confidence

5. **trading-signals** - Trading signal generator
   - Input: Symbol, context
   - Output: Signal (BUY/SELL/HOLD), confidence, reasoning

---

## Common Response Format

All API responses follow this standard format:

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "source": "huggingface",
    "generated_at": "2025-11-28T12:00:00Z",
    "cache_ttl_seconds": 30,
    "attempted": ["hf", "coinmarketcap"]
  }
}
```

Error response:

```json
{
  "success": false,
  "error": "Description of error",
  "attempted": ["hf", "coinmarketcap", "coingecko"],
  "timestamp": "2025-11-28T12:00:00Z"
}
```

---

## Monitoring & Health Checks

### System Health Endpoint

`GET /api/health` or `GET /api/v2/data-hub/health`

Returns health status of all data sources:

```json
{
  "success": true,
  "status": {
    "coinmarketcap": "operational",
    "newsapi": "operational",
    "etherscan": "operational",
    "huggingface": "operational",
    "coingecko": "operational",
    "binance": "operational"
  },
  "operational_count": 6,
  "total_sources": 6,
  "timestamp": "2025-11-28T12:00:00Z"
}
```

### Provider Monitoring

Production server checks all providers every 30 seconds:
- Online/Offline/Degraded status
- Response time tracking
- Error logging
- Historical uptime data

---

## Troubleshooting

### Common Issues

1. **No data returned**
   - Check API keys in environment variables
   - Verify external APIs are online
   - Check rate limits haven't been exceeded
   - Review logs for error messages

2. **Slow response times**
   - Check if cache is working
   - Verify network connection
   - Check external API response times
   - Consider increasing cache TTL

3. **Stale data**
   - Verify cache TTL settings
   - Check if data sources are updating
   - Clear cache manually if needed
   - Check timestamp in response metadata

4. **Authentication errors**
   - Verify API keys are correct
   - Check if keys have expired
   - Verify token format (Bearer, X-API-Key, etc.)
   - Check rate limits

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Frontend console logging:

```javascript
console.log('[APIClient] Request:', endpoint);
console.log('[APIClient] Response:', data);
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-28
