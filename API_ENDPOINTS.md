# 🚀 CryptoOne API Documentation

## Base URL
```
https://really-amin-datasourceforcryptocurrency-2.hf.space
```

**Last Updated:** December 13, 2025  
**API Version:** 2.0.0  
**Total Endpoints:** 60+

---

## 📊 Table of Contents

1. [Market Data Endpoints](#market-data-endpoints) (15 endpoints)
2. [Trading & Analysis Endpoints](#trading--analysis-endpoints) (5 endpoints)
3. [AI & Prediction Endpoints](#ai--prediction-endpoints) (4 endpoints)
4. [News & Social Endpoints](#news--social-endpoints) (4 endpoints)
5. [Portfolio & Alerts Endpoints](#portfolio--alerts-endpoints) (3 endpoints)
6. [System & Metadata Endpoints](#system--metadata-endpoints) (3 endpoints)
7. [Legacy Endpoints](#legacy-endpoints) (Still Active)
8. [Response Format](#response-format)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)

---

## 🎯 Market Data Endpoints

### 1. Search Coins
**`POST /api/coins/search`**

Search cryptocurrencies by name or symbol.

**Request Body:**
```json
{
  "q": "bitcoin",
  "limit": 20
}
```

**Response:**
```json
{
  "success": true,
  "query": "bitcoin",
  "count": 5,
  "results": [
    {
      "id": "bitcoin",
      "symbol": "BTC",
      "name": "Bitcoin",
      "image": "https://...",
      "current_price": 67850.00,
      "market_cap": 1280000000000,
      "market_cap_rank": 1,
      "price_change_24h": 2.5,
      "total_volume": 35000000000
    }
  ],
  "source": "coingecko",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 2. Get Coin Details
**`GET /api/coins/{coin_id}/details`**

Get comprehensive information about a specific cryptocurrency.

**Example:** `/api/coins/bitcoin/details`

**Response:**
```json
{
  "success": true,
  "id": "bitcoin",
  "symbol": "BTC",
  "name": "Bitcoin",
  "description": "Bitcoin is the first...",
  "image": "https://...",
  "categories": ["Cryptocurrency", "Store of Value"],
  "market_data": {
    "current_price": 67850.00,
    "market_cap": 1280000000000,
    "market_cap_rank": 1,
    "total_volume": 35000000000,
    "high_24h": 68200.00,
    "low_24h": 67100.00,
    "price_change_24h": 2.5,
    "price_change_7d": 5.2,
    "price_change_30d": 12.8,
    "circulating_supply": 19500000,
    "total_supply": 21000000,
    "max_supply": 21000000,
    "ath": 69000,
    "ath_date": "2021-11-10T00:00:00Z",
    "atl": 67.81,
    "atl_date": "2013-07-06T00:00:00Z"
  },
  "links": {
    "homepage": ["https://bitcoin.org"],
    "blockchain_site": ["https://blockchain.com"],
    "twitter": "bitcoin",
    "telegram": "bitcoin"
  },
  "source": "coingecko",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 3. Get Historical Data
**`GET /api/coins/{coin_id}/history`**

Get historical price data (OHLCV) for a cryptocurrency.

**Query Parameters:**
- `days` (int, 1-365): Number of days of history (default: 30)
- `interval` (string): Data interval - `daily` or `hourly` (default: `daily`)

**Example:** `/api/coins/bitcoin/history?days=30&interval=daily`

**Response:**
```json
{
  "success": true,
  "coin_id": "bitcoin",
  "days": 30,
  "interval": "daily",
  "count": 30,
  "data": [
    {
      "timestamp": 1701388800000,
      "date": "2025-11-13T00:00:00Z",
      "price": 65000.00,
      "volume": 32000000000,
      "market_cap": 1250000000000
    }
  ],
  "source": "coingecko",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 4. Get Chart Data
**`GET /api/coins/{coin_id}/chart`**

Get optimized chart data for frontend display.

**Query Parameters:**
- `timeframe` (string): `1h`, `24h`, `7d`, `30d`, `1y` (default: `24h`)

**Example:** `/api/coins/bitcoin/chart?timeframe=7d`

**Response:**
```json
{
  "success": true,
  "coin_id": "bitcoin",
  "timeframe": "7d",
  "chart": {
    "labels": ["2025-12-06 00:00", "2025-12-07 00:00", ...],
    "prices": [65000, 65500, 66000, ...]
  },
  "stats": {
    "high": 68000,
    "low": 64500,
    "avg": 66250,
    "change": 4.2
  },
  "source": "coingecko",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 5. Get Market Categories
**`GET /api/market/categories`**

Get cryptocurrency market categories (DeFi, NFT, Gaming, etc.).

**Response:**
```json
{
  "success": true,
  "count": 50,
  "categories": [
    {
      "id": "decentralized-finance-defi",
      "name": "Decentralized Finance (DeFi)",
      "market_cap": 98000000000,
      "market_cap_change_24h": 2.5,
      "volume_24h": 8500000000,
      "top_3_coins": ["ethereum", "binancecoin", "cardano"]
    }
  ],
  "source": "coingecko",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 6. Get Top Gainers
**`GET /api/market/gainers`**

Get top gaining cryptocurrencies in the last 24 hours.

**Query Parameters:**
- `limit` (int, 1-100): Number of gainers (default: 10)

**Response:**
```json
{
  "success": true,
  "count": 10,
  "gainers": [
    {
      "id": "solana",
      "symbol": "SOL",
      "name": "Solana",
      "image": "https://...",
      "current_price": 145.50,
      "price_change_24h": 15.8,
      "market_cap": 65000000000,
      "volume_24h": 4200000000
    }
  ],
  "source": "coingecko",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 7. Get Top Losers
**`GET /api/market/losers`**

Get top losing cryptocurrencies in the last 24 hours.

**Query Parameters:**
- `limit` (int, 1-100): Number of losers (default: 10)

**Response:**
```json
{
  "success": true,
  "count": 10,
  "losers": [
    {
      "id": "cardano",
      "symbol": "ADA",
      "name": "Cardano",
      "image": "https://...",
      "current_price": 0.58,
      "price_change_24h": -8.5,
      "market_cap": 21000000000,
      "volume_24h": 850000000
    }
  ],
  "source": "coingecko",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 8. Get Top Cryptocurrencies
**`GET /api/coins/top`**

Get top cryptocurrencies by market capitalization.

**Query Parameters:**
- `limit` (int, 1-250): Number of coins (default: 50)

**Response:** (See existing documentation)

---

### 9. Get Trending Coins
**`GET /api/trending`** or **`GET /api/market/trending`**

Get currently trending cryptocurrencies.

**Response:** (See existing documentation)

---

### 10. Get Market Overview
**`GET /api/market`**

Get global market overview data.

**Response:** (See existing documentation)

---

## ⚙️ Trading & Analysis Endpoints

### 1. Volume Analysis
**`GET /api/trading/volume`**

Get 24h volume analysis across exchanges.

**Query Parameters:**
- `symbol` (optional): Filter by specific coin (e.g., BTC)

**Response:**
```json
{
  "success": true,
  "symbol": "BTC",
  "total_volume": 35000000000,
  "count": 20,
  "data": [
    {
      "symbol": "BTC",
      "exchange": "Binance",
      "volume_24h": 12500000000,
      "volume_change": 5.2,
      "trades_count": 2500000
    }
  ],
  "source": "binance",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 2. Order Book Data
**`GET /api/trading/orderbook`**

Get real-time order book data with depth analysis.

**Query Parameters:**
- `symbol` (required): Trading symbol (e.g., BTC)
- `depth` (int, 5-100): Order book depth (default: 20)

**Response:**
```json
{
  "success": true,
  "symbol": "BTC",
  "timestamp": 123456789,
  "bids": [[67850.00, 1.5], [67840.00, 2.3], ...],
  "asks": [[67860.00, 1.2], [67870.00, 1.8], ...],
  "metrics": {
    "bid_volume": 125.5,
    "ask_volume": 110.2,
    "bid_ask_ratio": 1.14,
    "spread": 10.00,
    "spread_percent": 0.0147,
    "best_bid": 67850.00,
    "best_ask": 67860.00
  },
  "source": "binance",
  "update_time": "2025-12-13T13:40:00Z"
}
```

---

### 3. Technical Indicators
**`GET /api/indicators/{coin}`**

Get technical analysis indicators for a cryptocurrency.

**Query Parameters:**
- `interval` (string): `1h`, `4h`, `1d` (default: `1h`)
- `indicators` (optional): Comma-separated list: `rsi,macd,bb,sma,ema`

**Example:** `/api/indicators/BTC?interval=1h&indicators=rsi,macd,bb`

**Response:**
```json
{
  "success": true,
  "symbol": "BTC",
  "interval": "1h",
  "current_price": 67850.00,
  "indicators": {
    "rsi": {
      "value": 58.5,
      "period": 14,
      "interpretation": "neutral"
    },
    "macd": {
      "macd": 250.5,
      "signal": 245.2,
      "histogram": 5.3,
      "interpretation": "bullish"
    },
    "bollinger_bands": {
      "upper": 69000.00,
      "middle": 67500.00,
      "lower": 66000.00,
      "current_price": 67850.00,
      "position": "middle"
    }
  },
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 4. Strategy Backtesting
**`POST /api/backtest`**

Backtest trading strategies on historical data.

**Request Body:**
```json
{
  "symbol": "BTC",
  "strategy": "sma_cross",
  "start_date": "2025-10-01",
  "end_date": "2025-12-01",
  "initial_capital": 10000,
  "params": {
    "fast": 10,
    "slow": 30
  }
}
```

**Supported Strategies:**
- `sma_cross`: Simple Moving Average crossover
- `rsi_oversold`: RSI oversold/overbought
- `macd_signal`: MACD signal line crossover

**Response:**
```json
{
  "success": true,
  "strategy": "sma_cross",
  "symbol": "BTC",
  "period": "2025-10-01 to 2025-12-01",
  "initial_capital": 10000,
  "final_capital": 11250.50,
  "total_return": 1250.50,
  "return_percent": 12.5,
  "trades": {
    "total": 15,
    "winning": 9,
    "losing": 6,
    "win_rate": 60.0
  },
  "trade_history": [
    {
      "entry_price": 65000,
      "exit_price": 66500,
      "profit": 150.25,
      "profit_percent": 2.3
    }
  ],
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 5. Correlation Matrix
**`GET /api/correlations`**

Get price correlations between cryptocurrencies.

**Query Parameters:**
- `symbols` (string): Comma-separated symbols (default: "BTC,ETH,BNB,SOL,ADA")
- `days` (int, 7-90): Analysis period (default: 30)

**Response:**
```json
{
  "success": true,
  "symbols": ["BTC", "ETH", "BNB", "SOL", "ADA"],
  "days": 30,
  "correlations": {
    "BTC": {"BTC": 1.0, "ETH": 0.85, "BNB": 0.72, "SOL": 0.68, "ADA": 0.65},
    "ETH": {"BTC": 0.85, "ETH": 1.0, "BNB": 0.78, "SOL": 0.75, "ADA": 0.70}
  },
  "interpretation": {
    "strong_positive": "> 0.7",
    "moderate_positive": "0.3 to 0.7",
    "weak": "-0.3 to 0.3",
    "moderate_negative": "-0.7 to -0.3",
    "strong_negative": "< -0.7"
  },
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

## 🤖 AI & Prediction Endpoints

### 1. Price Predictions
**`GET /api/ai/predictions/{coin}`**

Get AI-powered price predictions.

**Query Parameters:**
- `days` (int, 1-30): Prediction period (default: 7)

**Example:** `/api/ai/predictions/BTC?days=7`

**Response:**
```json
{
  "success": true,
  "symbol": "BTC",
  "prediction_period": 7,
  "current_price": 67850.00,
  "predictions": [
    {
      "day": 1,
      "date": "2025-12-14",
      "predicted_price": 68200.00,
      "confidence": 0.80
    }
  ],
  "trend": "upward",
  "trend_strength": 3.5,
  "methodology": "Trend analysis with machine learning",
  "disclaimer": "Predictions are for informational purposes only.",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 2. Coin-Specific Sentiment
**`GET /api/ai/sentiment/{coin}`**

Get AI-powered sentiment analysis for a specific cryptocurrency.

**Example:** `/api/ai/sentiment/BTC`

**Response:**
```json
{
  "success": true,
  "symbol": "BTC",
  "current_price": 67850.00,
  "overall_sentiment": "bullish",
  "overall_score": 0.65,
  "confidence": 0.85,
  "breakdown": {
    "news": {
      "sentiment": "bullish",
      "confidence": 0.85,
      "factors": ["Positive news coverage", "Increasing adoption"]
    },
    "social_media": {
      "sentiment": "bullish",
      "confidence": 0.80,
      "sources": ["Twitter", "Reddit", "Telegram"]
    },
    "market_momentum": {
      "sentiment": "bullish",
      "indicators": ["RSI", "MACD", "Volume Analysis"]
    }
  },
  "recommendation": {
    "action": "buy",
    "confidence": 0.825,
    "risk_level": "medium"
  },
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 3. Custom AI Analysis
**`POST /api/ai/analyze`**

Perform custom AI analysis on a cryptocurrency.

**Request Body:**
```json
{
  "symbol": "BTC",
  "analysis_type": "risk_assessment",
  "timeframe": "30d",
  "custom_params": {}
}
```

**Analysis Types:**
- `sentiment`: Sentiment analysis
- `price_prediction`: Price forecasting
- `risk_assessment`: Risk evaluation
- `trend`: Trend identification

**Response:**
```json
{
  "success": true,
  "analysis_type": "risk_assessment",
  "symbol": "BTC",
  "result": {
    "risk_level": "medium",
    "volatility": 45.5,
    "volatility_percentile": 68,
    "risk_factors": [
      "Historical volatility: 45.5%",
      "Market cap: High",
      "Liquidity: High"
    ],
    "recommendation": "Suitable for moderate investors"
  },
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 4. AI Models Information
**`GET /api/ai/models`**

Get information about available AI models and their capabilities.

**Response:**
```json
{
  "success": true,
  "total_models": 5,
  "active_models": 4,
  "models": [
    {
      "id": "sentiment_analyzer_v1",
      "name": "Crypto Sentiment Analyzer",
      "type": "sentiment_analysis",
      "status": "active",
      "accuracy": 0.85,
      "languages": ["en"],
      "data_sources": ["news", "social_media", "forums"],
      "update_frequency": "real-time",
      "description": "Deep learning model trained on 100K+ crypto-related texts"
    }
  ],
  "capabilities": {
    "sentiment_analysis": true,
    "price_prediction": true,
    "trend_analysis": true,
    "risk_assessment": true,
    "anomaly_detection": true
  },
  "statistics": {
    "total_analyses": 250000,
    "daily_predictions": 10000,
    "avg_accuracy": 0.78,
    "uptime": "99.7%"
  },
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

## 📰 News & Social Endpoints

### 1. Coin-Specific News
**`GET /api/news/{coin}`**

Get news articles specific to a cryptocurrency.

**Query Parameters:**
- `limit` (int, 1-100): Number of articles (default: 20)

**Example:** `/api/news/BTC?limit=20`

**Response:**
```json
{
  "success": true,
  "coin": "BTC",
  "count": 20,
  "articles": [
    {
      "id": "article_123",
      "title": "Bitcoin Reaches New Milestone",
      "summary": "Bitcoin price surges to...",
      "content": "Full article content...",
      "url": "https://...",
      "image": "https://...",
      "published_at": "2025-12-13T10:00:00Z",
      "source": "CoinDesk",
      "categories": ["Market", "Bitcoin"],
      "tags": ["BTC", "price", "analysis"]
    }
  ],
  "sources": ["CoinDesk", "CoinTelegraph", "CryptoCompare"],
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 2. Social Media Trends
**`GET /api/social/trending`**

Get trending topics from social media platforms.

**Query Parameters:**
- `limit` (int, 1-50): Number of trending topics (default: 10)

**Response:**
```json
{
  "success": true,
  "trending_topics": [
    {
      "rank": 1,
      "topic": "Bitcoin",
      "mention_count": 85000,
      "sentiment": "bullish",
      "sentiment_score": 0.72,
      "trending_since": "2025-12-13T08:00:00Z",
      "related_coins": ["BTC", "ETH", "SOL"]
    }
  ],
  "statistics": {
    "total_mentions": 500000,
    "bullish_topics": 6,
    "bearish_topics": 2,
    "neutral_topics": 2,
    "market_sentiment": "bullish"
  },
  "sources": {
    "twitter": "active",
    "reddit": "active",
    "telegram": "active",
    "discord": "active"
  },
  "update_frequency": "Every 5 minutes",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 3. Social Sentiment Analysis
**`GET /api/social/sentiment`**

Get comprehensive social media sentiment analysis.

**Query Parameters:**
- `coin` (optional): Specific coin symbol
- `timeframe` (string): `1h`, `24h`, `7d` (default: `24h`)

**Response:**
```json
{
  "success": true,
  "coin": "BTC",
  "timeframe": "24h",
  "overall_sentiment": "bullish",
  "overall_score": 0.68,
  "emoji": "📈",
  "confidence": 0.85,
  "by_platform": {
    "twitter": {
      "sentiment": "bullish",
      "sentiment_score": 0.70,
      "mention_count": 45000,
      "engagement_rate": 0.055,
      "top_influencers": ["@cryptowhale", "@btcmaximalist"]
    }
  },
  "historical": [
    {
      "timestamp": "2025-12-13T00:00:00Z",
      "sentiment_score": 0.65
    }
  ],
  "key_topics": ["price movement", "adoption news", "regulations"],
  "methodology": "AI-powered sentiment analysis using NLP",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 4. Upcoming Events
**`GET /api/events`**

Get upcoming cryptocurrency events.

**Query Parameters:**
- `coin` (optional): Filter by coin
- `type` (optional): Filter by event type
- `days` (int, 1-90): Days ahead (default: 30)

**Response:**
```json
{
  "success": true,
  "count": 15,
  "filters": {
    "coin": null,
    "type": null,
    "days_ahead": 30
  },
  "events": [
    {
      "id": "event_1",
      "title": "BTC Mainnet Upgrade",
      "type": "Mainnet Upgrade",
      "coin": "BTC",
      "date": "2025-12-25",
      "time": "14:00 UTC",
      "description": "Important mainnet upgrade event for BTC",
      "source": "Official",
      "importance": "high",
      "url": "https://..."
    }
  ],
  "by_importance": {
    "high": 5,
    "medium": 7,
    "low": 3
  },
  "upcoming_highlights": [],
  "event_types": ["Conference", "Token Launch", "Mainnet Upgrade"],
  "sources": ["CoinMarketCal", "CoinGecko", "Official Announcements"],
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

## 💼 Portfolio & Alerts Endpoints

### 1. Portfolio Simulation
**`POST /api/portfolio/simulate`**

Simulate portfolio performance over time.

**Request Body:**
```json
{
  "holdings": [
    {"symbol": "BTC", "amount": 0.5},
    {"symbol": "ETH", "amount": 5.0}
  ],
  "initial_investment": 10000,
  "strategy": "hodl",
  "period_days": 30
}
```

**Strategies:**
- `hodl`: Hold all assets
- `rebalance`: Rebalance monthly
- `dca`: Dollar-cost averaging

**Response:**
```json
{
  "success": true,
  "strategy": "hodl",
  "period_days": 30,
  "initial_investment": 10000,
  "initial_portfolio": {
    "total_value": 10000,
    "allocations": {
      "BTC": {
        "amount": 0.5,
        "price": 67850,
        "value": 33925,
        "percentage": 50.0
      }
    }
  },
  "simulation_results": {
    "final_value": 11250.50,
    "total_return": 1250.50,
    "return_percent": 12.5,
    "annualized_return": 152.5,
    "volatility": 35.2,
    "max_drawdown": 8.5,
    "sharpe_ratio": 3.14
  },
  "portfolio_history": [
    {
      "day": 0,
      "date": "2025-12-13",
      "value": 10000
    }
  ],
  "disclaimer": "Simulation based on historical patterns.",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 2. Price Alerts
**`GET /api/alerts/prices`**

Get intelligent price alert recommendations.

**Query Parameters:**
- `symbols` (optional): Comma-separated symbols
- `type` (string): `breakout`, `support`, `resistance`, `all` (default: `all`)

**Response:**
```json
{
  "success": true,
  "count": 5,
  "alerts": [
    {
      "symbol": "BTC",
      "type": "resistance",
      "priority": "high",
      "current_price": 67850.00,
      "target_price": 68500.00,
      "distance_percent": 0.96,
      "message": "BTC approaching resistance at $68500.00",
      "recommendation": "Watch for breakout or rejection",
      "created_at": "2025-12-13T13:40:00Z"
    }
  ],
  "summary": {
    "high_priority": 2,
    "medium_priority": 3,
    "low_priority": 0
  },
  "recommendation": "Set up alerts for high-priority items",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 3. Watchlist Management
**`POST /api/watchlist`**

Manage cryptocurrency watchlists.

**Request Body:**
```json
{
  "action": "add",
  "symbols": ["BTC", "ETH", "SOL"],
  "name": "default"
}
```

**Actions:**
- `add`: Add symbols
- `remove`: Remove symbols
- `list`: List all symbols
- `clear`: Clear watchlist

**Response (add/list):**
```json
{
  "success": true,
  "action": "add",
  "watchlist": "default",
  "added_symbols": ["BTC", "ETH", "SOL"],
  "total_symbols": 3,
  "watchlist_data": [
    {
      "symbol": "BTC",
      "price": 67850.00,
      "added_at": "2025-12-13T13:40:00Z"
    }
  ],
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

## 🔧 System & Metadata Endpoints

### 1. Supported Exchanges
**`GET /api/exchanges`**

Get list of supported cryptocurrency exchanges.

**Query Parameters:**
- `limit` (int, 1-200): Number of exchanges (default: 50)
- `verified_only` (boolean): Only verified exchanges (default: false)

**Response:**
```json
{
  "success": true,
  "count": 50,
  "exchanges": [
    {
      "id": "binance",
      "name": "Binance",
      "year_established": 2017,
      "country": "Cayman Islands",
      "url": "https://www.binance.com/",
      "trust_score": 10,
      "trust_score_rank": 1,
      "trade_volume_24h_btc": 125000,
      "has_trading_incentive": false,
      "centralized": true,
      "image": "https://..."
    }
  ],
  "statistics": {
    "total_exchanges": 50,
    "verified_exchanges": 35,
    "total_volume_24h_btc": 250000,
    "average_trust_score": 8.5,
    "centralized_exchanges": 45,
    "decentralized_exchanges": 5
  },
  "top_by_volume": [],
  "source": "coingecko",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 2. Coins Metadata
**`GET /api/metadata/coins`**

Get comprehensive metadata for all cryptocurrencies.

**Query Parameters:**
- `search` (optional): Search term
- `platform` (optional): Filter by platform (ethereum, binance-smart-chain, etc.)
- `limit` (int, 1-5000): Number of coins (default: 100)

**Response:**
```json
{
  "success": true,
  "count": 100,
  "filters": {
    "search": null,
    "platform": null
  },
  "coins": [
    {
      "id": "bitcoin",
      "symbol": "BTC",
      "name": "Bitcoin",
      "platforms": {},
      "contract_addresses": {},
      "is_token": false,
      "native_platform": null
    }
  ],
  "statistics": {
    "total_coins": 100,
    "native_coins": 45,
    "tokens": 55,
    "platforms_supported": 15,
    "top_platforms": {
      "ethereum": 35,
      "binance-smart-chain": 12,
      "polygon-pos": 8
    }
  },
  "source": "coingecko",
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

### 3. Cache Statistics
**`GET /api/cache/stats`**

Get cache performance statistics and metrics.

**Response:**
```json
{
  "success": true,
  "cache_enabled": true,
  "overall_statistics": {
    "total_requests": 55000,
    "cache_hits": 45000,
    "cache_misses": 10000,
    "hit_rate_percent": 81.82,
    "miss_rate_percent": 18.18,
    "cache_size_mb": 55.5,
    "total_entries": 1250
  },
  "performance": {
    "avg_cache_latency_ms": 5,
    "avg_api_latency_ms": 500,
    "time_saved_seconds": 22275,
    "time_saved_hours": 6.19,
    "estimated_cost_savings_usd": 4.50
  },
  "cache_breakdown": {
    "market_data": {
      "entries": 250,
      "size_mb": 12.5,
      "hit_rate": 88.5
    }
  },
  "cache_config": {
    "max_size_mb": 500,
    "default_ttl_seconds": 300,
    "ttl_by_type": {
      "market_data": 60,
      "ohlcv_data": 300,
      "news": 900,
      "sentiment": 600
    },
    "eviction_policy": "LRU",
    "compression_enabled": true
  },
  "timestamps": {
    "oldest_entry": "2025-12-12T13:40:00Z",
    "newest_entry": "2025-12-13T13:40:00Z",
    "last_cleared": "2025-12-06T13:40:00Z",
    "next_cleanup": "2025-12-13T19:40:00Z"
  },
  "recommendations": [
    {
      "type": "optimization",
      "message": "Cache hit rate is good. Consider increasing cache size."
    }
  ],
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

## 📜 Legacy Endpoints (Still Active)

The following endpoints from the original API remain fully functional:

- `GET /api/health` - Health check
- `GET /api/status` - System status
- `GET /api/sentiment/global` - Global market sentiment (Fear & Greed Index)
- `GET /api/sentiment/analyze` - Text sentiment analysis
- `POST /api/sentiment/analyze` - Text sentiment analysis
- `GET /api/news` - Latest crypto news
- `GET /api/providers` - Data providers status
- `GET /api/resources` - Resource statistics
- `GET /api/models/*` - AI model endpoints
- `GET /api/ohlcv/{symbol}` - OHLCV data
- Plus 30+ other existing endpoints

---

## 📋 Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "source": "provider_name",
    "cached": true,
    "cache_age": 120
  },
  "timestamp": "2025-12-13T13:40:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { ... }
  },
  "timestamp": "2025-12-13T13:40:00Z"
}
```

---

## ⚠️ Error Handling

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (coin/resource not found)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `502` - Bad Gateway (external API error)
- `503` - Service Unavailable

### Common Error Codes

- `INVALID_PARAMETER` - Invalid query parameter
- `RESOURCE_NOT_FOUND` - Requested resource not found
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `EXTERNAL_API_ERROR` - External data source error
- `INTERNAL_ERROR` - Server internal error

---

## 🚦 Rate Limiting

### Rate Limits by Endpoint Type

- **Default**: 100 requests/minute
- **Market Data**: 60 requests/minute
- **AI/Sentiment**: 30 requests/minute
- **Trading Analysis**: 30 requests/minute

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701388800
```

### Handling Rate Limits

When rate limit is exceeded, the API returns:

```json
{
  "error": "Rate limit exceeded",
  "detail": "Too many requests. Please try again in 42 seconds.",
  "rate_limit_info": {
    "limit": 100,
    "requests_remaining": 0,
    "reset_at": 1701388800,
    "retry_after": 42
  }
}
```

---

## 🔑 Authentication

Currently, most endpoints are **publicly accessible** without authentication. Some advanced endpoints may require API keys in the future.

---

## 📊 Data Sources

The API aggregates data from multiple sources:

### Primary Sources
- **CoinGecko** - Market data, coin information
- **Binance** - Real-time prices, OHLCV data, order books
- **CryptoCompare** - News aggregation
- **Alternative.me** - Fear & Greed Index

### Fallback Sources
- **CoinPaprika** - Market data backup
- **CoinCap** - Market data backup
- **CoinDesk** - News backup (RSS)

---

## 📚 Example Usage

### JavaScript (Fetch API)
```javascript
// Search for Bitcoin
const searchCoins = async () => {
  const response = await fetch('https://really-amin-datasourceforcryptocurrency-2.hf.space/api/coins/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      q: 'bitcoin',
      limit: 10
    })
  });
  const data = await response.json();
  console.log(data);
};

// Get price predictions
const getPredictions = async () => {
  const response = await fetch('https://really-amin-datasourceforcryptocurrency-2.hf.space/api/ai/predictions/BTC?days=7');
  const data = await response.json();
  console.log(data);
};
```

### Python (Requests)
```python
import requests

# Search for coins
response = requests.post(
    'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/coins/search',
    json={'q': 'bitcoin', 'limit': 10}
)
data = response.json()
print(data)

# Get technical indicators
response = requests.get(
    'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/indicators/BTC',
    params={'interval': '1h', 'indicators': 'rsi,macd,bb'}
)
data = response.json()
print(data)
```

### cURL
```bash
# Get coin details
curl "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/coins/bitcoin/details"

# Backtest strategy
curl -X POST "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC",
    "strategy": "sma_cross",
    "start_date": "2025-10-01",
    "end_date": "2025-12-01",
    "initial_capital": 10000
  }'
```

---

## 📞 Support

For issues, questions, or feature requests:
- **GitHub Issues**: [Repository Link]
- **Documentation**: [Full Docs Link]
- **Email**: support@cryptoapi.example.com

---

## 🔄 Changelog

### Version 2.0.0 (December 13, 2025)

**Added:**
- 26+ new API endpoints across 6 categories
- Enhanced caching system with statistics
- Fallback provider support for reliability
- Comprehensive error handling
- Technical indicators (RSI, MACD, Bollinger Bands, SMA, EMA)
- Strategy backtesting capabilities
- AI-powered price predictions
- Social media sentiment analysis
- Portfolio simulation
- Watchlist management
- Price alert recommendations
- Correlation matrix analysis
- Upcoming events calendar
- Exchange and coin metadata

**Maintained:**
- All existing endpoints (backward compatible)
- Response format structure
- Authentication flow
- Rate limiting

---

## ⚡ Quick Reference

| Category | Endpoints | Base Path |
|----------|-----------|-----------|
| Market Data | 15 | `/api/coins/*`, `/api/market/*` |
| Trading & Analysis | 5 | `/api/trading/*`, `/api/indicators/*`, `/api/backtest`, `/api/correlations` |
| AI & Predictions | 4 | `/api/ai/*` |
| News & Social | 4 | `/api/news/*`, `/api/social/*`, `/api/events` |
| Portfolio & Alerts | 3 | `/api/portfolio/*`, `/api/alerts/*`, `/api/watchlist` |
| System & Metadata | 3 | `/api/exchanges`, `/api/metadata/*`, `/api/cache/*` |
| Legacy Endpoints | 30+ | Various paths |

---

**Total API Coverage:** 60+ endpoints providing complete cryptocurrency data infrastructure

---

*Last Updated: December 13, 2025*  
*API Version: 2.0.0*  
*Documentation Version: 1.0*
