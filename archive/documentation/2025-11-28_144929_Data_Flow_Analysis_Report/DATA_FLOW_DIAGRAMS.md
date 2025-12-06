# Data Flow Visual Diagrams

**Purpose:** Visual representation of data flows in the Crypto Intelligence Hub

---

## System Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                               │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Frontend SPA (Static HTML/CSS/JS)                           │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │ │
│  │  │Dashboard │ │ Market   │ │   News   │ │ Sentiment│  ...  │ │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │ │
│  │       └────────────┴─────────────┴─────────────┘             │ │
│  │                           │                                   │ │
│  │                  ┌────────▼────────┐                         │ │
│  │                  │   API Client    │                         │ │
│  │                  │ (api-client.js) │                         │ │
│  │                  │  • Caching      │                         │ │
│  │                  │  • Retry Logic  │                         │ │
│  │                  │  • Error Handle │                         │ │
│  │                  └────────┬────────┘                         │ │
│  └───────────────────────────┼──────────────────────────────────┘ │
└────────────────────────────────┼────────────────────────────────────┘
                                 │
                          HTTP/Fetch
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│                      FASTAPI BACKEND                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    API Routers                                │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │  │
│  │  │   Unified    │  │  Data Hub    │  │  Real Data   │      │  │
│  │  │  Service API │  │     API      │  │     API      │      │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │  │
│  │         └──────────────────┴──────────────────┘              │  │
│  └─────────────────────────────┼──────────────────────────────────┘  │
│                                │                                  │
│  ┌─────────────────────────────▼──────────────────────────────┐  │
│  │                     Service Layer                           │  │
│  │  ┌──────────────────┐  ┌──────────────────┐               │  │
│  │  │ HF Unified Client│  │ Data Hub Complete│               │  │
│  │  │   (HF Space)     │  │  (All APIs)      │               │  │
│  │  └────────┬─────────┘  └────────┬─────────┘               │  │
│  │           └────────────────┬─────┘                          │  │
│  └─────────────────────────────┼────────────────────────────────┘  │
│                                │                                  │
│  ┌─────────────────────────────▼──────────────────────────────┐  │
│  │                  Individual API Clients                     │  │
│  │  • CoinMarketCap  • CoinGecko    • Binance                │  │
│  │  • NewsAPI        • Etherscan    • BSCScan                 │  │
│  │  • Tronscan       • Alternative  • Reddit                  │  │
│  └─────────────────────────────┬────────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────────┘
                                 │
                          HTTPS/REST
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│                     EXTERNAL DATA SOURCES                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │  Hugging Face    │  │  Market Data     │  │  Blockchain      │ │
│  │      Space       │  │    Providers     │  │    Explorers     │ │
│  │  • AI Models     │  │  • CoinMarketCap │  │  • Etherscan     │ │
│  │  • Data Engine   │  │  • CoinGecko     │  │  • BSCScan       │ │
│  │  • WebSocket     │  │  • Binance       │  │  • Tronscan      │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │      News        │  │    Sentiment     │  │     Social       │ │
│  │   Providers      │  │    Providers     │  │     Media        │ │
│  │  • NewsAPI       │  │  • Alternative.me│  │  • Reddit        │ │
│  │  • RSS Feeds     │  │  • HF AI Models  │  │  • Twitter       │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow by Category

### 1. Market Data Flow

```
┌──────────────┐
│   Frontend   │
│   Dashboard  │
└──────┬───────┘
       │ GET /api/trending
       │ GET /api/market
       ▼
┌──────────────────────┐
│  Backend Router      │
│  (production_server  │
│   or real_data_api)  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Service Layer       │
│  (data_hub_complete) │
└──────┬───────────────┘
       │
       ├─────► ┌──────────────────┐    ┌─────────────┐
       │       │ Hugging Face     │───►│   Cache     │
       │       │     Space        │◄───│  (30 sec)   │
       │       └──────┬───────────┘    └─────────────┘
       │              │
       │              ▼
       │         ✓ Success → Return
       │              │
       │              ✗ Failed
       │              │
       ├─────► ┌──────────────────┐    ┌─────────────┐
       │       │  CoinMarketCap   │───►│   Cache     │
       │       │  (with API key)  │◄───│  (30 sec)   │
       │       └──────┬───────────┘    └─────────────┘
       │              │
       │              ▼
       │         ✓ Success → Transform & Return
       │              │
       │              ✗ Failed
       │              │
       ├─────► ┌──────────────────┐
       │       │    CoinGecko     │
       │       │      (Free)      │
       │       └──────┬───────────┘
       │              │
       │              ▼
       │         ✓ Success → Transform & Return
       │              │
       │              ✗ Failed
       │              │
       └─────► ┌──────────────────┐
               │     Binance      │
               │      (Free)      │
               └──────┬───────────┘
                      │
                      ▼
                 ✓ Success → Transform & Return
                      │
                      ✗ Failed
                      │
                      ▼
                 ┌──────────────┐
                 │ Return Error │
                 │  + Attempted │
                 │     List     │
                 └──────────────┘
```

### 2. Historical OHLCV Data Flow

```
┌──────────────┐
│   Frontend   │
│  Market Page │
└──────┬───────┘
       │ GET /api/market/ohlcv?symbol=BTC&interval=1h&limit=100
       ▼
┌─────────────────────┐
│  Backend Router     │
│  (data_hub_api)     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐    ┌──────────────┐
│   Binance Client    │───►│    Cache     │
│  (PRIMARY SOURCE)   │◄───│  (60 sec)    │
└──────┬──────────────┘    └──────────────┘
       │
       │ GET /klines?symbol=BTCUSDT&interval=1h&limit=100
       ▼
┌─────────────────────┐
│   Binance API       │
│  (Free, No Key)     │
└──────┬──────────────┘
       │
       ▼
  ✓ Got Klines
       │
       │ Transform Data:
       │ [timestamp, open, high, low, close, volume, ...]
       │         ↓
       │ {timestamp: int, open: float, high: float, ...}
       ▼
┌─────────────────────┐
│  Return OHLCV Array │
│  (100 candles)      │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│    Frontend         │
│  • Render Chart     │
│  • Format Tooltip   │
│  • Calculate Volume │
└─────────────────────┘

If Binance Fails:
       │
       ├─────► Try CoinMarketCap Historical
       │
       ├─────► Try Hugging Face Space
       │
       └─────► Return Error
```

### 3. News Feed Flow

```
┌──────────────┐
│   Frontend   │
│   News Page  │
└──────┬───────┘
       │ GET /api/news?limit=20
       ▼
┌─────────────────────────┐
│  Backend Router         │
│  (data_hub_api)         │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Service Layer          │
│  (data_hub_complete)    │
└──────┬──────────────────┘
       │
       ├────────────────────────────────────────┐
       │                                        │
       ▼                                        ▼
┌──────────────────┐                  ┌──────────────────┐
│    NewsAPI       │                  │      Reddit      │
│  (with API key)  │                  │      (Free)      │
└────────┬─────────┘                  └────────┬─────────┘
         │                                     │
         │ GET /everything?                   │ GET /r/CryptoCurrency/hot.json
         │  q=cryptocurrency&                 │ GET /r/Bitcoin/hot.json
         │  apiKey=***&                       │ GET /r/ethereum/hot.json
         │  language=en&                      │ GET /r/defi/hot.json
         │  sortBy=publishedAt&               │
         │  pageSize=20                       │
         ▼                                     ▼
┌──────────────────┐                  ┌──────────────────┐
│ NewsAPI Response │                  │ Reddit Response  │
│  • title         │                  │  • title         │
│  • description   │                  │  • selftext      │
│  • url           │                  │  • permalink     │
│  • source.name   │                  │  • score         │
│  • publishedAt   │                  │  • num_comments  │
│  • urlToImage    │                  │  • created_utc   │
└────────┬─────────┘                  └────────┬─────────┘
         │                                     │
         │ Transform:                          │ Transform:
         │  - Generate hash ID                 │  - Generate hash ID
         │  - Extract metadata                 │  - Format timestamp
         │  - Validate URLs                    │  - Build Reddit URL
         │                                     │
         └─────────────────┬───────────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  Combine Results │
                  │  • Merge arrays  │
                  │  • Remove dupes  │
                  │  • Sort by date  │
                  │  • Limit to 20   │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐    ┌──────────────┐
                  │  Cache Result    │───►│    Cache     │
                  │                  │    │  (300 sec)   │
                  └────────┬─────────┘    └──────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Return to        │
                  │   Frontend       │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  Display News    │
                  │  • Render cards  │
                  │  • Show images   │
                  │  • Format dates  │
                  └──────────────────┘
```

### 4. Sentiment Analysis Flow

```
┌──────────────┐
│   Frontend   │
│ Sentiment Pg │
└──────┬───────┘
       │ POST /api/sentiment/analyze
       │ Body: {
       │   "text": "Bitcoin is going to the moon!",
       │   "mode": "crypto"
       │ }
       ▼
┌─────────────────────────┐
│  Backend Router         │
│  (data_hub_api or       │
│   real_data_api)        │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Service Layer          │
│  (data_hub_complete)    │
└──────┬──────────────────┘
       │
       │ Choose model based on mode:
       │  • crypto → sentiment_crypto
       │  • financial → sentiment_financial
       │  • social → sentiment_twitter
       ▼
┌─────────────────────────┐
│  Hugging Face Space     │
│  (PRIMARY AI SOURCE)    │
└──────┬──────────────────┘
       │
       │ POST /api/sentiment/analyze
       │ Headers: { "Authorization": "Bearer <token>" }
       │ Body: { "text": "Bitcoin is..." }
       ▼
┌─────────────────────────┐
│  HF Space AI Engine     │
│  ┌───────────────────┐  │
│  │  Load AI Model    │  │
│  │  (sentiment-      │  │
│  │   crypto-bert)    │  │
│  └────────┬──────────┘  │
│           │             │
│           ▼             │
│  ┌───────────────────┐  │
│  │  Tokenize Text    │  │
│  │  • Clean input    │  │
│  │  • Token IDs      │  │
│  └────────┬──────────┘  │
│           │             │
│           ▼             │
│  ┌───────────────────┐  │
│  │  Run Inference    │  │
│  │  • Forward pass   │  │
│  │  • Softmax        │  │
│  └────────┬──────────┘  │
│           │             │
│           ▼             │
│  ┌───────────────────┐  │
│  │  Get Prediction   │  │
│  │  • label: str     │  │
│  │  • score: float   │  │
│  │  • confidence     │  │
│  └────────┬──────────┘  │
└───────────┼─────────────┘
            │
            ▼
   ┌────────────────────┐
   │  Response Data:    │
   │  {                 │
   │    "label":        │
   │      "positive",   │
   │    "score": 0.95,  │
   │    "confidence":   │
   │      0.95,         │
   │    "sentiment":    │
   │      "positive"    │
   │  }                 │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Save to Database  │
   │  (SentimentMetric) │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Return to         │
   │    Frontend        │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Display Result    │
   │  • Show label      │
   │  • Show score      │
   │  • Show confidence │
   │  • Color code      │
   │  • Show chart      │
   └────────────────────┘
```

### 5. Fear & Greed Index Flow

```
┌──────────────┐
│   Frontend   │
│ Sentiment Pg │
└──────┬───────┘
       │ GET /api/v2/data-hub/sentiment/fear-greed
       ▼
┌─────────────────────────┐
│  Backend Router         │
│  (data_hub_api)         │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐    ┌──────────────┐
│  Service Layer          │───►│    Cache     │
│  (data_hub_complete)    │◄───│  (3600 sec)  │
└──────┬──────────────────┘    └──────────────┘
       │
       ▼
┌─────────────────────────┐
│  Alternative.me API     │
│  (EXCLUSIVE SOURCE)     │
└──────┬──────────────────┘
       │
       │ GET https://api.alternative.me/fng/?limit=30&format=json
       ▼
┌─────────────────────────┐
│  Response:              │
│  {                      │
│    "data": [            │
│      {                  │
│        "value": "45",   │
│        "classification":│
│          "Fear",        │
│        "timestamp": ... │
│      },                 │
│      ...                │
│    ]                    │
│  }                      │
└──────┬──────────────────┘
       │
       │ Transform:
       │  • Parse value (0-100)
       │  • Get classification
       │  • Extract 30-day history
       ▼
┌─────────────────────────┐
│  Normalized Data:       │
│  {                      │
│    "current": {         │
│      "value": 45,       │
│      "label": "Fear"    │
│    },                   │
│    "history": [         │
│      {...}, {...}       │
│    ]                    │
│  }                      │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Return to Frontend     │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Display in UI:         │
│  • Gauge chart          │
│  • Color coded zones    │
│  • Historical trend     │
│  • Classification text  │
└─────────────────────────┘

Classification Scale:
0-24:   Extreme Fear (red)
25-49:  Fear (orange)
50:     Neutral (yellow)
51-74:  Greed (light green)
75-100: Extreme Greed (dark green)
```

### 6. Blockchain Data Flow

```
┌──────────────┐
│   Frontend   │
│ Providers Pg │
└──────┬───────┘
       │ GET /api/v2/data-hub/blockchain/ethereum?type=gas
       ▼
┌─────────────────────────┐
│  Backend Router         │
│  (data_hub_api)         │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Service Layer          │
│  (data_hub_complete)    │
└──────┬──────────────────┘
       │
       │ Route by chain:
       ├─────► Ethereum → Etherscan
       ├─────► BSC → BSCScan
       └─────► Tron → Tronscan
       │
       ▼
┌─────────────────────────┐
│  Etherscan API          │
│  (with API key)         │
└──────┬──────────────────┘
       │
       │ GET https://api.etherscan.io/api?
       │  module=gastracker&
       │  action=gasoracle&
       │  apikey=T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45
       ▼
┌─────────────────────────┐
│  Response:              │
│  {                      │
│    "result": {          │
│      "SafeGasPrice":    │
│        "20",            │
│      "ProposeGasPrice": │
│        "25",            │
│      "FastGasPrice":    │
│        "30"             │
│    }                    │
│  }                      │
└──────┬──────────────────┘
       │
       │ Transform to standard format:
       ▼
┌─────────────────────────┐
│  {                      │
│    "chain": "ethereum", │
│    "gas_prices": {      │
│      "safe": 20.0,      │
│      "standard": 25.0,  │
│      "fast": 30.0,      │
│      "unit": "gwei"     │
│    }                    │
│  }                      │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐    ┌──────────────┐
│  Cache Result           │───►│    Cache     │
│                         │    │  (60 sec)    │
└──────┬──────────────────┘    └──────────────┘
       │
       ▼
┌─────────────────────────┐
│  Return to Frontend     │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Display Gas Prices:    │
│  • Safe: 20 gwei        │
│  • Standard: 25 gwei    │
│  • Fast: 30 gwei        │
│  • Color code by price  │
└─────────────────────────┘
```

### 7. AI Trading Decision Flow

```
┌──────────────┐
│   Frontend   │
│ AI Analyst   │
└──────┬───────┘
       │ POST /api/ai/decision
       │ Body: {
       │   "symbol": "BTC",
       │   "horizon": "medium",
       │   "risk_tolerance": "medium",
       │   "context": "market analysis"
       │ }
       ▼
┌─────────────────────────────┐
│  Backend Router             │
│  (production_server or      │
│   real_data_api)            │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Gather Context Data:       │
│  ┌───────────────────────┐  │
│  │ 1. Current Price      │  │
│  │    (from market API)  │  │
│  └────────┬──────────────┘  │
│           │                 │
│  ┌────────▼──────────────┐  │
│  │ 2. Recent News        │  │
│  │    (from news API)    │  │
│  └────────┬──────────────┘  │
│           │                 │
│  ┌────────▼──────────────┐  │
│  │ 3. Sentiment          │  │
│  │    (from sentiment)   │  │
│  └────────┬──────────────┘  │
│           │                 │
│  ┌────────▼──────────────┐  │
│  │ 4. Technical          │  │
│  │    Indicators         │  │
│  └────────┬──────────────┘  │
└───────────┼─────────────────┘
            │
            ▼
┌─────────────────────────────┐
│  AI Decision Engine         │
│  (Hugging Face Space or     │
│   Local AI Model)           │
└──────┬──────────────────────┘
       │
       │ Process:
       │  1. Analyze price trend
       │  2. Evaluate sentiment
       │  3. Consider news impact
       │  4. Calculate risk
       │  5. Generate recommendation
       ▼
┌─────────────────────────────┐
│  Decision Output:           │
│  {                          │
│    "decision": "BUY",       │
│    "confidence": 0.85,      │
│    "factors": [             │
│      {                      │
│        "name": "Technical", │
│        "signal": "BUY",     │
│        "weight": 0.4        │
│      },                     │
│      {                      │
│        "name": "Sentiment", │
│        "signal": "BUY",     │
│        "weight": 0.3        │
│      },                     │
│      {                      │
│        "name": "Market",    │
│        "signal": "HOLD",    │
│        "weight": 0.3        │
│      }                      │
│    ],                       │
│    "reasoning": "...",      │
│    "entry_price": 45000,    │
│    "stop_loss": 43000,      │
│    "take_profit": 48000     │
│  }                          │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Return to Frontend         │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Display Decision:          │
│  • Decision badge           │
│  • Confidence meter         │
│  • Factor breakdown         │
│  • Reasoning text           │
│  • Entry/exit levels        │
│  • Risk warning             │
└─────────────────────────────┘
```

---

## Caching Strategy Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                  MULTI-LAYER CACHING                           │
└────────────────────────────────────────────────────────────────┘

Layer 1: Frontend Cache (Browser Memory)
┌────────────────────────────────────────────────────────────────┐
│  JavaScript Map                                                │
│  • TTL: 30 seconds (configurable)                             │
│  • Storage: Browser memory                                     │
│  • Cleared: Page reload or manual clear                       │
│                                                                │
│  cache = {                                                     │
│    "cache_api_market": {                                       │
│      data: {...},                                              │
│      timestamp: 1700000000000                                  │
│    }                                                           │
│  }                                                             │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
Layer 2: Backend Cache (Python Dictionary)
┌────────────────────────────────────────────────────────────────┐
│  Python Dict in Service Layer                                  │
│  • TTL: Varies by data type (30s-3600s)                       │
│  • Storage: Server memory                                      │
│  • Cleared: Server restart or TTL expiration                   │
│                                                                │
│  cache = {                                                     │
│    "md5_hash_of_endpoint_params": (                            │
│      {"data": ...},                                            │
│      datetime(2025, 11, 28, 12, 0, 0)                         │
│    )                                                           │
│  }                                                             │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
Layer 3: Database Cache (Persistent Storage)
┌────────────────────────────────────────────────────────────────┐
│  SQLite/PostgreSQL Database                                    │
│  • TTL: Varies by data type (60s-7200s)                       │
│  • Storage: Disk (persistent)                                  │
│  • Cleared: Manual deletion or TTL expiration                  │
│                                                                │
│  Tables:                                                       │
│  • CachedMarketData (prices, market_cap, volume)              │
│  • CachedOHLC (historical candles)                            │
│  • NewsArticle (news articles)                                │
│  • SentimentMetric (sentiment analysis results)               │
│  • WhaleTransaction (whale transactions)                      │
│  • GasPrice (blockchain gas prices)                           │
└────────────────────────────────────────────────────────────────┘

Cache Flow:
1. Request → Check Frontend Cache
   ├─► Hit → Return cached data
   └─► Miss → Request from Backend
               │
               └─► Check Backend Cache
                   ├─► Hit → Return cached data
                   └─► Miss → Query External API
                               │
                               ├─► Save to Backend Cache
                               ├─► Save to Database Cache
                               └─► Return data to Frontend
                                   │
                                   └─► Save to Frontend Cache
```

---

## Error Handling & Fallback Flow

```
┌────────────────────────────────────────────────────────────────┐
│                     REQUEST LIFECYCLE                          │
└────────────────────────────────────────────────────────────────┘

Frontend Request
      │
      │ api.getMarket()
      ▼
┌─────────────────────┐
│  Frontend Retry     │
│  Loop (3 attempts)  │
└──────┬──────────────┘
       │
       ▼
  Attempt 1
       │
       ├─► Success ──────────────────────────► Return Data
       │
       └─► Failed
             │
             │ Wait 1 second
             ▼
         Attempt 2
             │
             ├─► Success ──────────────────────► Return Data
             │
             └─► Failed
                   │
                   │ Wait 2 seconds
                   ▼
               Attempt 3
                   │
                   ├─► Success ──────────────► Return Data
                   │
                   └─► Failed (All retries exhausted)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Log Error to Frontend                                      │
│  • Add to errorLog array                                    │
│  • Show toast notification to user                          │
│  • Display error message in UI                              │
└─────────────────────────────────────────────────────────────┘

Backend Request (if frontend reaches backend)
      │
      ▼
┌─────────────────────┐
│  Backend Fallback   │
│  Chain              │
└──────┬──────────────┘
       │
       ├─► Source 1 (Primary: HF Space)
       │     │
       │     ├─► Success ──────────────────────► Return Data
       │     │                                    + meta.source = "hf"
       │     └─► Failed
       │           │
       │           │ Log: attempted.append("hf")
       │           ▼
       ├─► Source 2 (Fallback 1: CoinMarketCap)
       │     │
       │     ├─► Success ──────────────────────► Return Data
       │     │                                    + meta.source = "coinmarketcap"
       │     │                                    + meta.attempted = ["hf"]
       │     └─► Failed
       │           │
       │           │ Log: attempted.append("coinmarketcap")
       │           ▼
       ├─► Source 3 (Fallback 2: CoinGecko)
       │     │
       │     ├─► Success ──────────────────────► Return Data
       │     │                                    + meta.source = "coingecko"
       │     │                                    + meta.attempted = ["hf", "coinmarketcap"]
       │     └─► Failed
       │           │
       │           │ Log: attempted.append("coingecko")
       │           ▼
       └─► Source 4 (Fallback 3: Binance)
             │
             ├─► Success ──────────────────────► Return Data
             │                                    + meta.source = "binance"
             │                                    + meta.attempted = ["hf", "coinmarketcap", "coingecko"]
             └─► Failed (All sources failed)
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Return Error Response:                                     │
│  {                                                          │
│    "success": false,                                        │
│    "error": "All market data sources failed",               │
│    "attempted": ["hf", "coinmarketcap", "coingecko",       │
│                  "binance"],                                │
│    "timestamp": "2025-11-28T12:00:00Z",                    │
│    "meta": {                                                │
│      "source": "none",                                      │
│      "cache_ttl_seconds": 0                                 │
│    }                                                        │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
Frontend Error Handling
       │
       ├─► Display error toast
       ├─► Show error state in UI
       ├─► Offer retry button
       └─► Log to console
```

---

## Database Persistence Flow

```
┌────────────────────────────────────────────────────────────────┐
│           DATA PERSISTENCE TO DATABASE                         │
└────────────────────────────────────────────────────────────────┘

API Request → External Source → Data Received
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  Validate Data   │
                            │  • Check format  │
                            │  • Required flds │
                            │  • Value ranges  │
                            └────────┬─────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  Route by Type   │
                            └────────┬─────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────┐      ┌─────────────────┐       ┌─────────────────┐
│  Market Data    │      │  Sentiment      │       │  Whale Txs      │
│  ┌───────────┐  │      │  ┌───────────┐  │       │  ┌───────────┐  │
│  │ Parse     │  │      │  │ Parse     │  │       │  │ Parse     │  │
│  └─────┬─────┘  │      │  └─────┬─────┘  │       │  └─────┬─────┘  │
│        │        │      │        │        │       │        │        │
│        ▼        │      │        ▼        │       │        ▼        │
│  ┌───────────┐  │      │  ┌───────────┐  │       │  ┌───────────┐  │
│  │ Create    │  │      │  │ Create    │  │       │  │ Create    │  │
│  │ Model     │  │      │  │ Model     │  │       │  │ Model     │  │
│  │ Instance  │  │      │  │ Instance  │  │       │  │ Instance  │  │
│  └─────┬─────┘  │      │  └─────┬─────┘  │       │  └─────┬─────┘  │
│        │        │      │        │        │       │        │        │
│        ▼        │      │        ▼        │       │        ▼        │
│  CachedMarket   │      │  Sentiment      │       │  WhaleTransaction│
│  Data           │      │  Metric         │       │                 │
│  • symbol       │      │  • metric_name  │       │  • blockchain   │
│  • price        │      │  • value        │       │  • tx_hash      │
│  • provider     │      │  • classification│      │  • from_address │
│  • fetched_at   │      │  • source       │       │  • to_address   │
└─────────────────┘      └─────────────────┘       │  • amount       │
                                                    │  • amount_usd   │
                                                    │  • timestamp    │
                                                    └─────────────────┘
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  db.add(model)   │
                            └────────┬─────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │  db.commit()     │
                            └────────┬─────────┘
                                     │
                                     ├─► Success → Log success
                                     │
                                     └─► Failed → Rollback
                                                  └─► Log error

Database Schema (simplified):
┌─────────────────────────────────────────────────────────────┐
│  CachedMarketData                                           │
│  • id (primary key)                                         │
│  • symbol (varchar)                                         │
│  • price (float)                                            │
│  • market_cap (float)                                       │
│  • volume_24h (float)                                       │
│  • change_24h (float)                                       │
│  • provider (varchar)                                       │
│  • fetched_at (datetime)                                    │
│  • created_at (datetime)                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  SentimentMetric                                            │
│  • id (primary key)                                         │
│  • metric_name (varchar)                                    │
│  • value (float)                                            │
│  • classification (varchar)                                 │
│  • source (varchar)                                         │
│  • created_at (datetime)                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  WhaleTransaction                                           │
│  • id (primary key)                                         │
│  • blockchain (varchar)                                     │
│  • transaction_hash (varchar)                               │
│  • from_address (varchar)                                   │
│  • to_address (varchar)                                     │
│  • amount (float)                                           │
│  • amount_usd (float)                                       │
│  • timestamp (datetime)                                     │
│  • source (varchar)                                         │
│  • created_at (datetime)                                    │
└─────────────────────────────────────────────────────────────┘
```

---

**End of Data Flow Diagrams**

These visual diagrams complement the detailed textual analysis in `DATA_FLOW_ANALYSIS.md`.
