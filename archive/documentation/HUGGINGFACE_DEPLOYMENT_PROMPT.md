# 🚀 Crypto-DT-Source: Complete HuggingFace Deployment Prompt

**Purpose:** Complete guide to activate ALL features in the Crypto-DT-Source project for production deployment on HuggingFace Spaces
**Target Environment:** HuggingFace Spaces + Python 3.11+
**Deployment Season:** Q4 2025
**Status:** Ready for Implementation

---

## 📋 Executive Summary

This prompt provides a **complete roadmap** to transform Crypto-DT-Source from a monitoring platform into a **fully-functional cryptocurrency data aggregation service**. All 50+ endpoints will be connected to real data sources, database persistence will be integrated, AI models will be loaded, and the system will be optimized for HuggingFace Spaces deployment.

**Expected Outcome:**
- ✅ Real crypto market data (live prices, OHLCV, trending coins)
- ✅ Historical data storage in SQLite
- ✅ AI-powered sentiment analysis using HuggingFace transformers
- ✅ Authentication + rate limiting on all endpoints
- ✅ WebSocket real-time streaming
- ✅ Provider health monitoring with intelligent failover
- ✅ Automatic provider discovery
- ✅ Full diagnostic and monitoring capabilities
- ✅ Production-ready Docker deployment to HF Spaces

---

## 🎯 Implementation Priorities (Phase 1-4)

### **Phase 1: Core Data Integration (CRITICAL)**
*Goal: Replace all mock data with real API calls*

#### 1.1 Market Data Endpoints
**Files to modify:**
- `api/endpoints.py` - `/api/market`, `/api/prices`
- `collectors/market_data_extended.py` - Real price fetching
- `api_server_extended.py` - FastAPI endpoints

**Requirements:**
- Remove all hardcoded mock data from endpoints
- Implement real API calls to CoinGecko, CoinCap, Binance
- Use async/await pattern for non-blocking calls
- Implement caching layer (5-minute TTL for prices)
- Add error handling with provider fallback

**Implementation Steps:**
```python
# Example: Replace mock market data with real provider data
GET /api/market
├── Call ProviderManager.get_best_provider('market_data')
├── Execute async request to provider
├── Cache response (5 min TTL)
├── Return real BTC/ETH prices instead of mock
└── Fallback to secondary provider on failure

GET /api/prices?symbols=BTC,ETH,SOL
├── Parse symbol list
├── Call ProviderManager for each symbol
├── Aggregate responses
├── Return real-time price data

GET /api/trending
├── Call CoinGecko trending endpoint
├── Store in database
└── Return top 7 trending coins

GET /api/ohlcv?symbol=BTCUSDT&interval=1h&limit=100
├── Call Binance OHLCV endpoint
├── Validate symbol format
├── Apply caching (15-min TTL)
└── Return historical OHLCV data
```

**Success Criteria:**
- [ ] All endpoints return real data from providers
- [ ] Caching implemented with configurable TTL
- [ ] Provider failover working (when primary fails)
- [ ] Response times < 2 seconds
- [ ] No hardcoded mock data in endpoint responses

---

#### 1.2 DeFi Data Endpoints
**Files to modify:**
- `api_server_extended.py` - `/api/defi` endpoint
- `collectors/` - Add DeFi collector

**Requirements:**
- Fetch TVL data from DeFi Llama API
- Track top DeFi protocols
- Cache for 1 hour (DeFi data updates less frequently)

**Implementation:**
```python
GET /api/defi
├── Call DeFi Llama: GET /protocols
├── Filter top 20 by TVL
├── Parse response (name, TVL, chain, symbol)
├── Store in database (defi_protocols table)
└── Return with timestamp

GET /api/defi/tvl-chart
├── Query historical TVL from database
├── Aggregate by date
└── Return 30-day TVL trend
```

---

#### 1.3 News & Sentiment Integration
**Files to modify:**
- `collectors/sentiment_extended.py`
- `api/endpoints.py` - `/api/sentiment` endpoint

**Requirements:**
- Fetch news from RSS feeds (CoinDesk, Cointelegraph, etc.)
- Implement real HuggingFace sentiment analysis (NOT keyword matching)
- Store sentiment scores in database
- Track Fear & Greed Index

**Implementation:**
```python
GET /api/sentiment
├── Query recent news from database
├── Load HuggingFace model: distilbert-base-uncased-finetuned-sst-2-english
├── Analyze each headline/article
├── Calculate aggregate sentiment score
├── Return: {overall_sentiment, fear_greed_index, top_sentiments}

GET /api/news
├── Fetch from RSS feeds (configurable)
├── Run through sentiment analyzer
├── Store in database (news table with sentiment)
├── Return paginated results

POST /api/analyze/text
├── Accept raw text input
├── Run HuggingFace sentiment model
├── Return: {text, sentiment, confidence, label}
```

---

### **Phase 2: Database Integration (HIGH PRIORITY)**
*Goal: Full persistent storage of all data*

#### 2.1 Database Schema Activation
**Files:**
- `database/models.py` - Define all tables
- `database/migrations.py` - Schema setup
- `database/db_manager.py` - Connection management

**Tables to Activate:**
```sql
-- Core tables
prices (id, symbol, price, timestamp, provider)
ohlcv (id, symbol, open, high, low, close, volume, timestamp)
news (id, title, content, sentiment, source, timestamp)
defi_protocols (id, name, tvl, chain, timestamp)
market_snapshots (id, btc_price, eth_price, market_cap, timestamp)

-- Metadata tables
providers (id, name, status, health_score, last_check)
pools (id, name, strategy, created_at)
api_calls (id, endpoint, provider, response_time, status)
user_requests (id, ip_address, endpoint, timestamp)
```

**Implementation:**
```python
# In api_server_extended.py startup:

@app.on_event("startup")
async def startup_event():
    # Initialize database
    db_manager = DBManager()
    await db_manager.initialize()

    # Run migrations
    await db_manager.run_migrations()

    # Create tables if not exist
    await db_manager.create_all_tables()

    # Verify connectivity
    health = await db_manager.health_check()
    logger.info(f"Database initialized: {health}")
```

#### 2.2 API Endpoints ↔ Database Integration
**Pattern to implement:**

```python
# Write pattern: After fetching real data, store it
async def store_market_snapshot():
    # Fetch real data
    prices = await provider_manager.get_market_data()

    # Store in database
    async with db.session() as session:
        snapshot = MarketSnapshot(
            btc_price=prices['BTC'],
            eth_price=prices['ETH'],
            market_cap=prices['market_cap'],
            timestamp=datetime.now()
        )
        session.add(snapshot)
        await session.commit()

    return prices

# Read pattern: Query historical data
@app.get("/api/prices/history/{symbol}")
async def get_price_history(symbol: str, days: int = 30):
    async with db.session() as session:
        history = await session.query(Price).filter(
            Price.symbol == symbol,
            Price.timestamp >= datetime.now() - timedelta(days=days)
        ).all()

    return [{"price": p.price, "timestamp": p.timestamp} for p in history]
```

**Success Criteria:**
- [ ] All real-time data is persisted to database
- [ ] Historical queries return > 30 days of data
- [ ] Database is queried for price history endpoints
- [ ] Migrations run automatically on startup
- [ ] No data loss on server restart

---

### **Phase 3: AI & Sentiment Analysis (MEDIUM PRIORITY)**
*Goal: Real ML-powered sentiment analysis*

#### 3.1 Load HuggingFace Models
**Files:**
- `ai_models.py` - Model loading and inference
- Update `requirements.txt` with torch, transformers

**Models to Load:**
```python
# Sentiment Analysis
SENTIMENT_MODELS = [
    "distilbert-base-uncased-finetuned-sst-2-english",  # Fast, accurate
    "cardiffnlp/twitter-roberta-base-sentiment-latest",  # Social media optimized
    "ProsusAI/finBERT",  # Financial sentiment
]

# Crypto-specific models
CRYPTO_MODELS = [
    "EleutherAI/gpt-neo-125M",  # General purpose (lightweight)
    "facebook/opt-125m",  # Instruction following
]

# Zero-shot classification for custom sentiment
"facebook/bart-large-mnli"  # Multi-class sentiment (bullish/bearish/neutral)
```

**Implementation:**
```python
# ai_models.py

class AIModelManager:
    def __init__(self):
        self.models = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    async def initialize(self):
        """Load all models on startup"""
        logger.info("Loading HuggingFace models...")

        # Sentiment analysis
        self.models['sentiment'] = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=0 if self.device == "cuda" else -1
        )

        # Zero-shot for crypto sentiment
        self.models['zeroshot'] = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if self.device == "cuda" else -1
        )

        logger.info("Models loaded successfully")

    async def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment of text"""
        if not self.models.get('sentiment'):
            return {"error": "Model not loaded", "sentiment": "unknown"}

        result = self.models['sentiment'](text)[0]

        return {
            "text": text[:100],
            "label": result['label'],
            "score": result['score'],
            "timestamp": datetime.now().isoformat()
        }

    async def analyze_crypto_sentiment(self, text: str) -> dict:
        """Crypto-specific sentiment (bullish/bearish/neutral)"""
        candidate_labels = ["bullish", "bearish", "neutral"]
        result = self.models['zeroshot'](text, candidate_labels)

        return {
            "text": text[:100],
            "sentiment": result['labels'][0],
            "scores": dict(zip(result['labels'], result['scores'])),
            "timestamp": datetime.now().isoformat()
        }

# In api_server_extended.py
ai_manager = AIModelManager()

@app.on_event("startup")
async def startup():
    await ai_manager.initialize()

@app.post("/api/sentiment/analyze")
async def analyze_sentiment(request: AnalyzeRequest):
    """Real sentiment analysis endpoint"""
    result = await ai_manager.analyze_sentiment(request.text)
    return result

@app.post("/api/sentiment/crypto-analysis")
async def crypto_sentiment(request: AnalyzeRequest):
    """Crypto-specific sentiment analysis"""
    result = await ai_manager.analyze_crypto_sentiment(request.text)
    return result
```

#### 3.2 News Sentiment Pipeline
**Implementation:**

```python
# Background task: Analyze news sentiment continuously

async def analyze_news_sentiment():
    """Run every 30 minutes: fetch news and analyze sentiment"""
    while True:
        try:
            # 1. Fetch recent news from feeds
            news_items = await fetch_rss_feeds()

            # 2. Store news items
            for item in news_items:
                # 3. Analyze sentiment
                sentiment = await ai_manager.analyze_sentiment(item['title'])

                # 4. Store in database
                async with db.session() as session:
                    news = News(
                        title=item['title'],
                        content=item['content'],
                        source=item['source'],
                        sentiment=sentiment['label'],
                        confidence=sentiment['score'],
                        timestamp=datetime.now()
                    )
                    session.add(news)

            await session.commit()
            logger.info(f"Analyzed {len(news_items)} news items")

        except Exception as e:
            logger.error(f"News sentiment pipeline error: {e}")

        # Wait 30 minutes
        await asyncio.sleep(1800)

# Start in background on app startup
@app.on_event("startup")
async def startup():
    asyncio.create_task(analyze_news_sentiment())
```

---

### **Phase 4: Security & Production Setup (HIGH PRIORITY)**
*Goal: Production-ready authentication, rate limiting, and monitoring*

#### 4.1 Authentication Implementation
**Files:**
- `utils/auth.py` - JWT token handling
- `api/security.py` - New file for security middleware

**Implementation:**

```python
# utils/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

class AuthManager:
    @staticmethod
    def create_token(user_id: str, hours: int = 24) -> str:
        """Create JWT token"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> str:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("user_id")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

security = HTTPBearer()
auth_manager = AuthManager()

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)):
    """Dependency for protected endpoints"""
    return auth_manager.verify_token(credentials.credentials)

# In api_server_extended.py
@app.post("/api/auth/token")
async def get_token(api_key: str):
    """Issue JWT token for API key"""
    # Validate API key against database
    user = await verify_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    token = auth_manager.create_token(user.id)
    return {"access_token": token, "token_type": "bearer"}

# Protected endpoint example
@app.get("/api/protected-data")
async def protected_endpoint(current_user: str = Depends(get_current_user)):
    """This endpoint requires authentication"""
    return {"user_id": current_user, "data": "sensitive"}
```

#### 4.2 Rate Limiting
**Files:**
- `utils/rate_limiter_enhanced.py` - Enhanced rate limiter

**Implementation:**

```python
# In api_server_extended.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Rate limit configuration
FREE_TIER = "30/minute"  # 30 requests per minute
PRO_TIER = "300/minute"   # 300 requests per minute
ADMIN_TIER = None          # Unlimited

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded", "retry_after": 60}
    )

# Apply to endpoints
@app.get("/api/prices")
@limiter.limit(FREE_TIER)
async def get_prices(request: Request):
    return await prices_handler()

@app.get("/api/sentiment")
@limiter.limit(FREE_TIER)
async def get_sentiment(request: Request):
    return await sentiment_handler()

# Premium endpoints
@app.get("/api/historical-data")
@limiter.limit(PRO_TIER)
async def get_historical_data(request: Request, current_user: str = Depends(get_current_user)):
    return await historical_handler()
```

**Tier Configuration:**
```python
RATE_LIMIT_TIERS = {
    "free": {
        "requests_per_minute": 30,
        "requests_per_day": 1000,
        "max_symbols": 5,
        "data_retention_days": 7
    },
    "pro": {
        "requests_per_minute": 300,
        "requests_per_day": 50000,
        "max_symbols": 100,
        "data_retention_days": 90
    },
    "enterprise": {
        "requests_per_minute": None,  # Unlimited
        "requests_per_day": None,
        "max_symbols": None,
        "data_retention_days": None
    }
}
```

---

#### 4.3 Monitoring & Diagnostics
**Files:**
- `api/endpoints.py` - Diagnostic endpoints
- `monitoring/health_monitor.py` - Health checks

**Implementation:**

```python
@app.get("/api/health")
async def health_check():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": await check_database(),
            "providers": await check_providers(),
            "models": await check_models(),
            "websocket": await check_websocket(),
            "cache": await check_cache()
        },
        "metrics": {
            "uptime_seconds": get_uptime(),
            "active_connections": active_ws_count(),
            "request_count_1h": get_request_count("1h"),
            "average_response_time_ms": get_avg_response_time()
        }
    }

@app.post("/api/diagnostics/run")
async def run_diagnostics(auto_fix: bool = False):
    """Full system diagnostics"""
    issues = []
    fixes = []

    # Check all components
    checks = [
        check_database_integrity(),
        check_provider_health(),
        check_disk_space(),
        check_memory_usage(),
        check_model_availability(),
        check_config_files(),
        check_required_directories(),
        verify_api_connectivity()
    ]

    results = await asyncio.gather(*checks)

    for check in results:
        if check['status'] != 'ok':
            issues.append(check)
            if auto_fix:
                fix = await apply_fix(check)
                fixes.append(fix)

    return {
        "timestamp": datetime.now().isoformat(),
        "total_checks": len(checks),
        "issues_found": len(issues),
        "issues": issues,
        "fixes_applied": fixes if auto_fix else []
    }

@app.get("/api/metrics")
async def get_metrics():
    """System metrics for monitoring"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "database_size_mb": get_database_size() / 1024 / 1024,
        "active_requests": active_request_count(),
        "websocket_connections": active_ws_count(),
        "provider_stats": await get_provider_statistics()
    }
```

---

### **Phase 5: Background Tasks & Auto-Discovery**
*Goal: Continuous operation with automatic provider discovery*

#### 5.1 Background Tasks
**Files:**
- `scheduler.py` - Task scheduling
- `monitoring/scheduler_comprehensive.py` - Enhanced scheduler

**Tasks to Activate:**

```python
# In api_server_extended.py

@app.on_event("startup")
async def start_background_tasks():
    """Start all background tasks"""

    tasks = [
        # Data collection tasks
        asyncio.create_task(collect_prices_every_5min()),
        asyncio.create_task(collect_defi_data_every_hour()),
        asyncio.create_task(fetch_news_every_30min()),
        asyncio.create_task(analyze_sentiment_every_hour()),

        # Health & monitoring tasks
        asyncio.create_task(health_check_every_5min()),
        asyncio.create_task(broadcast_stats_every_5min()),
        asyncio.create_task(cleanup_old_logs_daily()),
        asyncio.create_task(backup_database_daily()),
        asyncio.create_task(send_diagnostics_hourly()),

        # Discovery tasks (optional)
        asyncio.create_task(discover_new_providers_daily()),
    ]

    logger.info(f"Started {len(tasks)} background tasks")

# Scheduled tasks with cron-like syntax
TASK_SCHEDULE = {
    "collect_prices": "*/5 * * * *",  # Every 5 minutes
    "collect_defi": "0 * * * *",      # Hourly
    "fetch_news": "*/30 * * * *",     # Every 30 minutes
    "sentiment_analysis": "0 * * * *", # Hourly
    "health_check": "*/5 * * * *",    # Every 5 minutes
    "backup_database": "0 2 * * *",   # Daily at 2 AM
    "cleanup_logs": "0 3 * * *",      # Daily at 3 AM
}
```

#### 5.2 Auto-Discovery Service
**Files:**
- `backend/services/auto_discovery_service.py` - Discovery logic

**Implementation:**

```python
# Enable in environment
ENABLE_AUTO_DISCOVERY=true
AUTO_DISCOVERY_INTERVAL_HOURS=24

class AutoDiscoveryService:
    """Automatically discover new crypto API providers"""

    async def discover_providers(self) -> List[Provider]:
        """Scan for new providers"""
        discovered = []

        sources = [
            self.scan_github_repositories,
            self.scan_api_directories,
            self.scan_rss_feeds,
            self.query_existing_apis,
        ]

        for source in sources:
            try:
                providers = await source()
                discovered.extend(providers)
                logger.info(f"Discovered {len(providers)} from {source.__name__}")
            except Exception as e:
                logger.error(f"Discovery error in {source.__name__}: {e}")

        # Validate and store
        valid = []
        for provider in discovered:
            if await self.validate_provider(provider):
                await self.store_provider(provider)
                valid.append(provider)

        return valid

    async def scan_github_repositories(self):
        """Search GitHub for crypto API projects"""
        # Query GitHub API for relevant repos
        # Extract API endpoints
        # Return as Provider objects
        pass

    async def validate_provider(self, provider: Provider) -> bool:
        """Test if provider is actually available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    provider.base_url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    return resp.status < 500
        except:
            return False

# Start discovery on demand
@app.post("/api/discovery/run")
async def trigger_discovery(background: bool = True):
    """Trigger provider discovery"""
    discovery_service = AutoDiscoveryService()

    if background:
        asyncio.create_task(discovery_service.discover_providers())
        return {"status": "Discovery started in background"}
    else:
        providers = await discovery_service.discover_providers()
        return {"discovered": len(providers), "providers": providers}
```

---

## 🐳 HuggingFace Spaces Deployment

### Configuration for HF Spaces

**`spaces/app.py` (Entry point):**
```python
import os
import sys

# Set environment for HF Spaces
os.environ['HF_SPACE'] = 'true'
os.environ['PORT'] = '7860'  # HF Spaces default port

# Import and start the main FastAPI app
from api_server_extended import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info"
    )
```

**`spaces/requirements.txt`:**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
aiohttp==3.9.1
pydantic==2.5.3
websockets==12.0
sqlalchemy==2.0.23
torch==2.1.1
transformers==4.35.2
huggingface-hub==0.19.1
slowapi==0.1.9
python-jose==3.3.0
psutil==5.9.6
aiofiles==23.2.1
```

**`spaces/README.md`:**
```markdown
# Crypto-DT-Source on HuggingFace Spaces

Real-time cryptocurrency data aggregation service with 200+ providers.

## Features
- Real-time price data
- AI sentiment analysis
- 50+ REST endpoints
- WebSocket streaming
- Provider health monitoring
- Historical data storage

## API Documentation
- Swagger UI: https://[your-space-url]/docs
- ReDoc: https://[your-space-url]/redoc

## Quick Start
```bash
curl https://[your-space-url]/api/health
curl https://[your-space-url]/api/prices?symbols=BTC,ETH
curl https://[your-space-url]/api/sentiment
```

## WebSocket Connection
```javascript
const ws = new WebSocket('wss://[your-space-url]/ws');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```
```

---

## ✅ Activation Checklist

### Phase 1: Data Integration
- [ ] Modify `/api/market` to return real CoinGecko data
- [ ] Modify `/api/prices` to fetch real provider data
- [ ] Modify `/api/trending` to return live trending coins
- [ ] Implement `/api/ohlcv` with Binance data
- [ ] Implement `/api/defi` with DeFi Llama data
- [ ] Remove all hardcoded mock data
- [ ] Test all endpoints with real data
- [ ] Add caching layer (5-30 min TTL based on endpoint)

### Phase 2: Database
- [ ] Run database migrations
- [ ] Create all required tables
- [ ] Implement write pattern for real data storage
- [ ] Implement read pattern for historical queries
- [ ] Add database health check
- [ ] Test data persistence across restarts
- [ ] Implement cleanup tasks for old data

### Phase 3: AI & Sentiment
- [ ] Install transformers and torch
- [ ] Load HuggingFace sentiment model
- [ ] Implement sentiment analysis endpoint
- [ ] Implement crypto-specific sentiment classification
- [ ] Create news sentiment pipeline
- [ ] Store sentiment scores in database
- [ ] Test model inference latency

### Phase 4: Security
- [ ] Generate JWT secret key
- [ ] Implement authentication middleware
- [ ] Create API key management system
- [ ] Implement rate limiting on all endpoints
- [ ] Add tier-based rate limits (free/pro/enterprise)
- [ ] Create `/api/auth/token` endpoint
- [ ] Test authentication on protected endpoints
- [ ] Set up HTTPS certificate for CORS

### Phase 5: Background Tasks
- [ ] Activate all scheduled tasks
- [ ] Set up price collection (every 5 min)
- [ ] Set up DeFi data collection (hourly)
- [ ] Set up news fetching (every 30 min)
- [ ] Set up sentiment analysis (hourly)
- [ ] Set up health checks (every 5 min)
- [ ] Set up database backup (daily)
- [ ] Set up log cleanup (daily)

### Phase 6: HF Spaces Deployment
- [ ] Create `spaces/` directory
- [ ] Create `spaces/app.py` entry point
- [ ] Create `spaces/requirements.txt`
- [ ] Create `spaces/README.md`
- [ ] Configure environment variables
- [ ] Test locally with Docker
- [ ] Push to HF Spaces
- [ ] Verify all endpoints accessible
- [ ] Monitor logs and metrics
- [ ] Set up auto-restart on failure

---

## 🔧 Environment Variables

```bash
# Core
PORT=7860
ENVIRONMENT=production
LOG_LEVEL=info

# Database
DATABASE_URL=sqlite:///data/crypto_aggregator.db
DATABASE_POOL_SIZE=20

# Security
JWT_SECRET_KEY=your-secret-key-change-in-production
API_KEY_SALT=your-salt-key

# HuggingFace Spaces
HF_SPACE=true
HF_SPACE_URL=https://huggingface.co/spaces/your-username/crypto-dt-source

# Features
ENABLE_AUTO_DISCOVERY=true
ENABLE_SENTIMENT_ANALYSIS=true
ENABLE_BACKGROUND_TASKS=true

# Rate Limiting
FREE_TIER_LIMIT=30/minute
PRO_TIER_LIMIT=300/minute

# Caching
CACHE_TTL_PRICES=300  # 5 minutes
CACHE_TTL_DEFI=3600   # 1 hour
CACHE_TTL_NEWS=1800   # 30 minutes

# Providers (optional API keys)
ETHERSCAN_API_KEY=
BSCSCAN_API_KEY=
COINGECKO_API_KEY=
```

---

## 📊 Expected Performance

After implementation:

| Metric | Target | Current |
|--------|--------|---------|
| Price endpoint response time | < 500ms | N/A |
| Sentiment analysis latency | < 2s | N/A |
| WebSocket update frequency | Real-time | ✅ Working |
| Database query latency | < 100ms | N/A |
| Provider failover time | < 2s | ✅ Working |
| Authentication overhead | < 50ms | N/A |
| Concurrent connections supported | 1000+ | ✅ Tested |

---

## 🚨 Troubleshooting

### Models not loading on HF Spaces
```bash
# HF Spaces has limited disk space
# Use distilbert models (smaller) instead of full models
# Or cache models in requirements
pip install --no-cache-dir transformers torch
```

### Database file too large
```bash
# Implement cleanup task
# Keep only 90 days of data
# Archive old data to S3
```

### Rate limiting too aggressive
```bash
# Adjust limits in environment
FREE_TIER_LIMIT=100/minute
PRO_TIER_LIMIT=500/minute
```

### WebSocket disconnections
```bash
# Increase heartbeat frequency
WEBSOCKET_HEARTBEAT_INTERVAL=10  # seconds
WEBSOCKET_HEARTBEAT_TIMEOUT=30   # seconds
```

---

## 📚 Next Steps

1. **Review Phase 1-2**: Data integration and database
2. **Review Phase 3-4**: AI and security implementations
3. **Review Phase 5-6**: Background tasks and HF deployment
4. **Execute implementation** following the checklist
5. **Test thoroughly** before production deployment
6. **Monitor metrics** and adjust configurations
7. **Collect user feedback** and iterate

---

## 🎯 Success Criteria

Project is **production-ready** when:

✅ All 50+ endpoints return real data
✅ Database stores 90 days of historical data
✅ Sentiment analysis runs on real ML models
✅ Authentication required on all protected endpoints
✅ Rate limiting enforced across all tiers
✅ Background tasks running without errors
✅ Health check returns all components OK
✅ WebSocket clients can stream real-time data
✅ Auto-discovery discovers new providers
✅ Deployed on HuggingFace Spaces successfully
✅ Average response time < 1 second
✅ Zero downtime during operation

---

**Document Version:** 2.0
**Last Updated:** 2025-11-15
**Maintained by:** Claude Code AI
**Status:** Ready for Implementation
