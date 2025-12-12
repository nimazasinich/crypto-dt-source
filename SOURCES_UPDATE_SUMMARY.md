# Data Sources Update Summary

## Overview

This update adds comprehensive sentiment/news sources, database management for data sources, configurable collection intervals, and real-time monitoring capabilities.

## Changes Made

### 1. New Sentiment & News Sources Registry
**File:** `backend/providers/sentiment_news_providers.py`

Added 25+ new data sources including:

#### Sentiment APIs
- Fear & Greed Index (free, no key)
- LunarCrush (social sentiment)
- Santiment (on-chain + social)
- Augmento (social media analysis)
- The TIE (enterprise sentiment)
- CryptoQuant Sentiment
- Glassnode Sentiment

#### News Sources
- CryptoPanic (aggregated news)
- NewsAPI
- CryptoCompare News
- Messari News
- RSS Feeds:
  - Bitcoin Magazine
  - Decrypt
  - CryptoSlate
  - The Block
  - CoinTelegraph
  - CoinDesk

#### Social Sources
- Reddit r/CryptoCurrency
- Reddit r/Bitcoin

#### Historical Data
- CoinGecko Historical
- Binance Historical
- CryptoCompare Historical

#### Aggregated Sources
- CoinCap Real-time
- CoinPaprika
- DefiLlama

---

### 2. Database Model for Data Sources
**File:** `database/data_sources_model.py`

New database tables:

#### DataSource Table
```python
class DataSource(Base):
    __tablename__ = 'data_sources'
    
    # Basic Info
    source_id = Column(String(100), unique=True)
    name = Column(String(255))
    source_type = Column(String(50))
    description = Column(Text)
    
    # Connection Info
    base_url = Column(String(500))
    
    # Authentication
    requires_api_key = Column(Boolean)
    api_key_env_var = Column(String(100))
    
    # Collection Settings
    collection_interval = Column(String(20))  # "15m", "30m"
    supports_realtime = Column(Boolean)
    
    # Status
    is_active = Column(Boolean, default=True)
    status = Column(String(50))  # "active", "error", "rate_limited"
    
    # Statistics
    total_requests = Column(Integer)
    successful_requests = Column(Integer)
    avg_response_time_ms = Column(Float)
```

#### DataCollectionLog Table
Tracks collection history for each source.

#### CollectionSchedule Table
Manages scheduled collection times.

---

### 3. Updated Services Configuration
**File:** `static/data/services.json`

Updated to include all 40+ providers organized by category:
- Market Data (8 providers)
- News (9 sources)
- Sentiment (4 providers)
- Analytics (4 providers)
- DeFi (3 providers)
- Technical Analysis
- AI Models
- Block Explorers (4 providers)

---

### 4. Data Collection Worker
**File:** `workers/data_collection_worker.py`

Configurable collection intervals:

```python
COLLECTION_INTERVALS = {
    "market": 15,      # 15 minutes
    "news": 15,        # 15 minutes
    "sentiment": 15,   # 15 minutes
    "social": 30,      # 30 minutes
    "onchain": 30,     # 30 minutes
    "historical": 30,  # 30 minutes
    "defi": 15,        # 15 minutes
    "technical": 15,   # 15 minutes
}
```

Features:
- **Bulk Collection:** Every 15-30 minutes (configurable per data type)
- **Real-time Fetching:** On-demand when client requests data
- **Caching:** Smart caching with configurable TTL
- **Multi-Source Fallback:** Automatic fallback to backup providers

---

### 5. Real-Time Monitoring
**File:** `api/realtime_monitoring.py`

WebSocket channels for real-time updates:

```
Channels:
- market_data      : Real-time market prices
- price_updates    : Individual price changes
- news             : Latest news articles
- sentiment        : Sentiment changes
- whale_alerts     : Large transaction alerts
- collection_status: Data collection progress
- system_health    : System health monitoring
```

WebSocket endpoints:
- `/ws/realtime` - Main endpoint (subscribe to any channel)
- `/ws/prices` - Dedicated price updates
- `/ws/alerts` - Whale and sentiment alerts

---

### 6. Updated Help Modal
**File:** `static/shared/components/config-helper-modal.js`

Updated to show all available services with examples:
- Unified Service API
- Market Data API
- News Aggregator API
- Sentiment Analysis API
- On-Chain Analytics API
- Technical Analysis API
- AI Models API
- DeFi Data API
- Resources & Monitoring API
- WebSocket API

---

## Collection Strategy

### Bulk Data (15-30 minute intervals)
Used for data that doesn't change frequently:
- Market overview data
- News articles
- On-chain statistics
- DeFi TVL data

### Real-time Data (on-demand)
Fetched immediately when client requests:
- Current prices (Binance, CoinGecko)
- OHLCV candlestick data
- Fear & Greed Index
- Whale transactions

### Caching Strategy
```python
CACHE_TTL = {
    "market": 60,        # 1 minute
    "news": 300,         # 5 minutes
    "sentiment": 300,    # 5 minutes
    "ohlcv": 60,         # 1 minute
    "fear_greed": 3600,  # 1 hour
    "whale": 300,        # 5 minutes
}
```

---

## API Endpoints Reference

### Unified Service API
```
GET /api/service/rate?pair=BTC/USDT
GET /api/service/rate/batch?pairs=BTC/USDT,ETH/USDT
GET /api/service/market-status
GET /api/service/top?n=10
GET /api/service/sentiment?symbol=BTC
GET /api/service/whales?chain=ethereum&min_amount_usd=1000000
```

### Market Data
```
GET /api/market?limit=100
GET /api/ohlcv?symbol=BTC&timeframe=1h&limit=500
GET /api/coins/top?limit=50
```

### News
```
GET /api/news?limit=20
GET /api/news/latest?symbol=BTC&limit=10
```

### Sentiment
```
GET /api/sentiment/global
GET /api/fear-greed
POST /api/sentiment/analyze
```

### Real-Time WebSocket
```javascript
const ws = new WebSocket('wss://host/ws/realtime');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    channels: ['market_data', 'price_updates', 'whale_alerts']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data.channel, data.data);
};
```

---

## Usage Examples

### Python - Fetch Market Data
```python
import requests

# Get prices
response = requests.get('https://your-api/api/service/rate/batch?pairs=BTC/USDT,ETH/USDT')
data = response.json()
for rate in data['data']:
    print(f"{rate['pair']}: ${rate['price']}")
```

### JavaScript - Real-time Updates
```javascript
const ws = new WebSocket('wss://your-api/ws/realtime');

ws.onopen = () => {
  // Subscribe to price updates
  ws.send(JSON.stringify({
    action: 'subscribe',
    channels: ['price_updates']
  }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.channel === 'price_updates') {
    console.log(`${msg.data.symbol}: $${msg.data.price}`);
  }
};
```

---

## Files Modified/Created

1. `backend/providers/sentiment_news_providers.py` - NEW
2. `database/data_sources_model.py` - NEW
3. `workers/data_collection_worker.py` - NEW
4. `api/realtime_monitoring.py` - NEW
5. `static/data/services.json` - UPDATED
6. `static/shared/components/config-helper-modal.js` - UPDATED

---

## Notes

- All new sources are configured with appropriate rate limits
- Database model supports tracking active/inactive status
- Collection intervals are configurable per data type
- Real-time WebSocket provides push updates, not just polling
- HTTP endpoints remain available as fallback
