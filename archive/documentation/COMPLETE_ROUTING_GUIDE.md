# Complete Routing Guide

## 🎯 Overview

This document describes the complete routing structure from application startup to static pages and API endpoints.

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HuggingFace Space                         │
│                    Docker Container                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      hf_space_api.py                         │
│                    FastAPI Application                        │
│                   (uvicorn server)                           │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   Static    │ │  API Routes │ │  Workers    │
    │   Files     │ │  /api/*     │ │  Background │
    └─────────────┘ └─────────────┘ └─────────────┘
            │               │               │
            │               │               │
            ▼               ▼               ▼
    /static/pages/*   Smart Fallback   Data Collection
                       305+ Resources   Agent (24/7)
```

## 🚀 Application Startup Flow

### 1. Docker Container Start
```bash
# Dockerfile CMD
uvicorn hf_space_api:app --host 0.0.0.0 --port 7860 --workers 1
```

### 2. FastAPI Application Initialization (`hf_space_api.py`)

#### Phase 1: Database Initialization
```python
# Initialize SQLite database
db_manager.init_database()
```

#### Phase 2: AI Models Loading
```python
# Load HuggingFace models
_registry.load_all_models()
```

#### Phase 3: Background Workers
```python
# Start data collection workers
- Market Data Worker (CoinGecko, Binance)
- OHLC Data Worker
- Comprehensive Data Worker
- Smart Data Collection Agent (305+ resources)
```

#### Phase 4: Static Files & Routes
```python
# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(hf_router)              # Original endpoints
app.include_router(hf_hub_router)          # HF Hub endpoints
app.include_router(alphavantage_router)    # Alpha Vantage
app.include_router(massive_router)         # Massive.com
app.include_router(smart_router)           # Smart Fallback (305+ resources)
```

## 📂 Static Files Routing

### Root URL (`/`)
- **Returns**: `/static/index.html`
- **Description**: Main landing page with beautiful UI
- **Features**: Resource selection, navigation to all pages

### Static Files (`/static/*`)
- **CSS**: `/static/css/*.css`
- **JavaScript**: `/static/js/*.js`
- **Pages**: `/static/pages/*/index.html`
- **Assets**: `/static/assets/*`

### Main UI Pages

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/static/pages/dashboard/index.html` | Overview dashboard with live data |
| Market | `/static/pages/market/index.html` | Real-time market data |
| Trading Assistant | `/static/pages/trading-assistant/index.html` | AI trading assistant |
| Technical Analysis | `/static/pages/technical-analysis/index.html` | Charts and indicators |
| News | `/static/pages/news/index.html` | Crypto news aggregator |
| Sentiment | `/static/pages/sentiment/index.html` | AI sentiment analysis |
| Models | `/static/pages/models/index.html` | AI models status |
| API Explorer | `/static/pages/api-explorer/index.html` | Interactive API testing |
| Diagnostics | `/static/pages/diagnostics/index.html` | System health |
| Data Sources | `/static/pages/data-sources/index.html` | All 305+ resources |
| Providers | `/static/pages/providers/index.html` | Data provider status |
| Settings | `/static/pages/settings/index.html` | App configuration |
| Help | `/static/pages/help/index.html` | Documentation |

## 🔄 API Routing

### Smart Fallback API (305+ Resources, NEVER 404)

```javascript
// Frontend usage
const apiClient = window.apiClient;

// Market data with automatic fallback
const market = await apiClient.getMarketData(100);

// News with automatic fallback
const news = await apiClient.getNews(20);

// Sentiment analysis
const sentiment = await apiClient.getSentiment('bitcoin');

// Whale alerts
const whales = await apiClient.getWhaleAlerts(20);

// Blockchain data
const blockchain = await apiClient.getBlockchainData('ethereum');

// Health report (305+ resources status)
const health = await apiClient.getHealthReport();

// System statistics
const stats = await apiClient.getStats();
```

### API Endpoints

#### Smart Fallback Endpoints (Use these - they never fail!)
- `GET /api/smart/market?limit=100` - Market data
- `GET /api/smart/news?limit=20` - News feed
- `GET /api/smart/sentiment?symbol=bitcoin` - Sentiment analysis
- `GET /api/smart/whale-alerts?limit=20` - Whale tracking
- `GET /api/smart/blockchain/{chain}` - Blockchain data
- `GET /api/smart/health-report` - Resource health
- `GET /api/smart/stats` - System statistics
- `POST /api/smart/cleanup-failed` - Clean dead resources

#### Original Endpoints
- `GET /api/market?limit=100` - Market data (CoinGecko/Binance)
- `GET /api/market/history?symbol=bitcoin&days=7` - Historical data
- `GET /api/sentiment/analyze` - Sentiment analysis
- `GET /api/health` - System health

#### Alpha Vantage Endpoints
- `GET /api/alphavantage/health` - Provider health
- `GET /api/alphavantage/prices?symbols=BTC,ETH` - Crypto prices
- `GET /api/alphavantage/ohlcv?symbol=BTC&interval=5min` - OHLCV data
- `GET /api/alphavantage/market-status` - Market status
- `GET /api/alphavantage/crypto-rating/{symbol}` - Crypto rating
- `GET /api/alphavantage/quote/{symbol}` - Stock quote

#### Massive.com Endpoints
- `GET /api/massive/health` - Provider health
- `GET /api/massive/dividends?limit=20` - Dividend records
- `GET /api/massive/splits?limit=20` - Stock splits
- `GET /api/massive/quotes/{ticker}` - Real-time quotes
- `GET /api/massive/trades/{ticker}` - Trade data
- `GET /api/massive/aggregates/{ticker}` - OHLCV aggregates
- `GET /api/massive/ticker/{ticker}` - Ticker details
- `GET /api/massive/market-status` - Market status

#### Documentation
- `GET /docs` - FastAPI Swagger UI
- `GET /redoc` - FastAPI ReDoc

## 🔧 Frontend Integration

### API Configuration (`/static/js/api-config.js`)

This file provides:
1. **API_CONFIG** - Global configuration object
2. **SmartAPIClient** - Client with automatic fallback
3. **Resource Rotation** - Uses all 305+ resources
4. **Retry Logic** - Automatic retries with exponential backoff
5. **Auth Management** - Token handling

### Usage in Pages

```html
<!-- Include in all pages -->
<script src="/static/js/api-config.js"></script>

<script>
    // Use global API client
    const client = window.apiClient;
    
    // Fetch market data
    async function loadMarketData() {
        try {
            const data = await client.getMarketData(100);
            console.log('Market data:', data);
            // Render data...
        } catch (error) {
            console.error('Failed to load market data:', error);
        }
    }
    
    // Call on page load
    loadMarketData();
</script>
```

## 🛡️ Resource Rotation System

### How It Works

1. **305+ Resources Loaded**: All free resources from `consolidated_crypto_resources.json`
2. **Priority Scoring**: Each resource scored by:
   - Success rate (40%)
   - Response time (30%)
   - Recency (30%)
3. **Smart Selection**: Always picks best available resource
4. **Automatic Fallback**: If one fails, tries next best
5. **Health Monitoring**: Continuous health checks
6. **Auto Cleanup**: Dead resources removed automatically
7. **Proxy Support**: Smart proxy for sanctioned exchanges (e.g., Binance)

### Resource Categories

- **21 Market Data APIs**: CoinGecko, CoinMarketCap, CoinPaprika, etc.
- **40+ Block Explorers**: Etherscan, BscScan, Polygonscan, etc.
- **15 News APIs**: CryptoPanic, CoinDesk, CoinTelegraph, etc.
- **12 Sentiment APIs**: LunarCrush, Santiment, TheTIE, etc.
- **9 Whale Tracking**: Whale Alert, Glassnode, etc.
- **13 On-chain Analytics**: Dune, Nansen, DeFiLlama, etc.
- **24 RPC Nodes**: Infura, Alchemy, QuickNode, etc.
- **106 Local Backend**: Internal caching and processing
- **7 CORS Proxies**: For bypassing CORS restrictions

### Never 404 Promise

The Smart Fallback System **guarantees**:
- ✅ No 404 errors
- ✅ No single point of failure
- ✅ Always returns data (from cache if needed)
- ✅ Automatic resource rotation
- ✅ Proxy support for sanctioned exchanges
- ✅ Self-healing (removes dead resources)

## 🧪 Testing Routing

### Test Script
```bash
# Run complete routing test
python3 test_complete_routing.py

# Test specific URL
TEST_URL=http://localhost:7860 python3 test_complete_routing.py
```

### Manual Testing

1. **Start Application**:
   ```bash
   uvicorn hf_space_api:app --reload
   ```

2. **Test Root**:
   ```bash
   curl http://localhost:7860/
   ```

3. **Test Static Files**:
   ```bash
   curl http://localhost:7860/static/index.html
   ```

4. **Test API**:
   ```bash
   curl http://localhost:7860/api/smart/market?limit=10
   ```

5. **Test Pages** (in browser):
   - http://localhost:7860/static/pages/dashboard/index.html
   - http://localhost:7860/static/pages/market/index.html
   - etc.

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t crypto-intelligence-hub .
```

### Run Container
```bash
docker run -p 7860:7860 \
  -e HF_TOKEN=your_token \
  -e ALPHA_VANTAGE_API_KEY=40XS7GQ6AU9NB6Y4 \
  -e MASSIVE_API_KEY=PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE \
  crypto-intelligence-hub
```

### HuggingFace Space Deployment
```bash
# Push to HF Space
git push hf main
```

## 📊 Resource Usage

### Optimal Usage Pattern

```python
# 1. Use Smart Fallback for critical data
market_data = await smart_api.get_market_data()

# 2. Use specific providers for specialized data
av_data = await alphavantage_api.get_crypto_rating('BTC')

# 3. Cache results in frontend
localStorage.setItem('market_data', JSON.stringify(market_data));

# 4. Implement frontend polling with backoff
setInterval(async () => {
    await refreshData();
}, 30000); // 30 seconds
```

### Resource Limits

- **Smart Fallback**: No limit (305+ resources)
- **CoinGecko Free**: 10-50 calls/minute
- **Binance**: 1200 requests/minute
- **Alpha Vantage**: 5 calls/minute (our key)
- **Massive.com**: Varies by endpoint

## 🎯 Best Practices

1. **Always use Smart Fallback endpoints** - They never fail
2. **Implement caching** - Reduce API calls
3. **Use loading states** - Better UX
4. **Handle errors gracefully** - Show user-friendly messages
5. **Monitor resource health** - Check `/api/smart/health-report`
6. **Rotate resources** - Don't hammer one API
7. **Use WebSocket for real-time** - More efficient than polling
8. **Implement retry logic** - With exponential backoff

## ✅ Checklist

### Before Deployment
- [ ] All static pages load correctly
- [ ] API endpoints return data
- [ ] Smart Fallback working (305+ resources)
- [ ] Resource rotation active
- [ ] Proxy system functional
- [ ] Background agent running
- [ ] Health monitoring active
- [ ] Database initialized
- [ ] AI models loaded
- [ ] Environment variables set

### After Deployment
- [ ] Test all pages in browser
- [ ] Verify API responses
- [ ] Check logs for errors
- [ ] Monitor resource health
- [ ] Test proxy for sanctioned exchanges
- [ ] Verify data collection agent
- [ ] Check database size
- [ ] Monitor memory usage
- [ ] Test mobile responsiveness
- [ ] Verify CORS headers

## 🔗 Related Documents

- `SMART_FALLBACK_SYSTEM.md` - Smart Fallback documentation
- `SMART_SYSTEM_FINAL_SUMMARY.md` - Complete system summary
- `NEW_API_INTEGRATIONS.md` - Alpha Vantage & Massive.com
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `API_DOCUMENTATION.md` - Full API reference

## 🚨 Troubleshooting

### Pages Not Loading
```bash
# Check static files exist
ls -la static/pages/

# Check server logs
docker logs <container_id>
```

### API Returns 404
```bash
# Use Smart Fallback instead
curl http://localhost:7860/api/smart/market?limit=10

# Check health
curl http://localhost:7860/api/smart/health-report
```

### Resource Rotation Not Working
```python
# Check agent status
response = await client.get('/api/smart/stats')
print(response['collection_stats'])
```

### Proxy Issues
```python
# Test proxy health
response = await client.get('/api/smart/health-report')
print(response['proxy_health'])
```

---

**Last Updated**: December 5, 2025
**Version**: 2.0.0
**Status**: ✅ Production Ready
