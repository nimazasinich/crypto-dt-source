# 🚀 Crypto Data Source API - HuggingFace Space Deployment

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Production_Ready-success?style=flat)]()

Complete cryptocurrency data aggregation and AI analysis platform with integrated UI framework.

---

## 📋 Quick Links

- 📖 **[Quick Start Guide](./QUICK_START.md)** - Get started in 5 minutes
- 🚀 **[Deployment Guide](./HUGGINGFACE_DEPLOYMENT_COMPLETE.md)** - Complete deployment documentation
- 📡 **[API Reference](./WORKING_ENDPOINTS.md)** - All 40+ endpoints with examples
- ✅ **[Implementation Summary](./IMPLEMENTATION_SUMMARY.md)** - What was built and verified

---

## ✨ Features

### 🎨 Complete UI Framework
- **10 Interactive Pages**: Dashboard, Market, Models, Sentiment, AI Analyst, Trading Assistant, News, Providers, Diagnostics, API Explorer
- **Responsive Design**: Mobile-friendly, modern UI with dark/light themes
- **Real-time Updates**: Auto-refreshing data with configurable polling
- **Smart Caching**: Optimized performance with TTL-based caching

### 📡 Comprehensive Backend API
- **40+ Endpoints**: Health, Market Data, Sentiment, AI, News, Models, Trading, Resources
- **Real Data Sources**: CoinGecko, Binance, Alternative.me, CryptoCompare, RSS feeds
- **AI Integration**: Sentiment analysis, trading signals, decision support
- **Fallback System**: Graceful degradation with multi-source support

### 🧠 AI & Machine Learning
- **Sentiment Analysis**: CryptoBERT, FinBERT models
- **Trading Signals**: AI-powered buy/sell/hold signals
- **Market Analysis**: Technical indicators, risk assessment
- **News Sentiment**: Automatic news article sentiment detection

### 📊 Data Features
- **Market Data**: Real-time prices, OHLC, volume, market cap
- **Historical Data**: Time-series data with configurable intervals
- **News Aggregation**: Multiple sources with filtering
- **Provider Monitoring**: Health checks, uptime tracking

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Server
```bash
python hf_unified_server.py
```

Server starts on **http://localhost:7860**

### 3. Verify Deployment
```bash
# Automated testing
python verify_deployment.py

# Or open interactive test suite
open http://localhost:7860/test_api_integration.html
```

### 4. Access UI
- **Dashboard**: http://localhost:7860/
- **Market Data**: http://localhost:7860/market
- **AI Models**: http://localhost:7860/models
- **API Explorer**: http://localhost:7860/api-explorer

---

## 📡 API Examples

### Health Check
```bash
curl http://localhost:7860/api/health
```

### Market Data
```bash
# Get market overview
curl http://localhost:7860/api/market

# Get top cryptocurrencies
curl "http://localhost:7860/api/coins/top?limit=10"

# Get specific rate
curl "http://localhost:7860/api/service/rate?pair=BTC/USDT"
```

### Sentiment Analysis
```bash
# Global sentiment
curl "http://localhost:7860/api/sentiment/global?timeframe=1D"

# Asset sentiment
curl http://localhost:7860/api/sentiment/asset/BTC

# Analyze text
curl -X POST http://localhost:7860/api/service/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text":"Bitcoin is bullish!","mode":"crypto"}'
```

### AI Trading Signals
```bash
# Get signals
curl "http://localhost:7860/api/ai/signals?symbol=BTC"

# Get AI decision
curl -X POST http://localhost:7860/api/ai/decision \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTC","horizon":"swing","risk_tolerance":"moderate"}'
```

---

## 🏗️ Architecture

### Project Structure
```
workspace/
├── hf_unified_server.py     # Main entry point (FastAPI)
├── requirements.txt          # Python dependencies
├── static/                   # UI framework (263 files)
│   ├── pages/                # 10 page modules
│   └── shared/               # Shared components
├── backend/                  # Backend services
│   ├── routers/              # 28 API routers
│   └── services/             # 70 service modules
├── database/                 # Database layer
├── utils/                    # Utilities
├── test_api_integration.html # Interactive test suite
└── verify_deployment.py      # Automated tests
```

### Technology Stack
- **Backend**: FastAPI, Python 3.10+
- **Frontend**: Vanilla JavaScript (ES6+), CSS3
- **Database**: SQLAlchemy, SQLite/PostgreSQL
- **AI/ML**: HuggingFace Transformers (optional)
- **Data Sources**: CoinGecko, Binance, Alternative.me, RSS

---

## 🧪 Testing

### Automated Testing
```bash
python verify_deployment.py
```

**Output:**
```
=================================================================================
  HuggingFace Space Deployment Verification
=================================================================================

✓ Server is responding

Health & Status
---------------
  ✓ GET  /api/health                                           45ms
  ✓ GET  /api/status                                          120ms
  ✓ GET  /api/routers                                          35ms

Market Data
-----------
  ✓ GET  /api/market                                          450ms
  ✓ GET  /api/coins/top?limit=10                              380ms
  ...

=================================================================================
Summary
=================================================================================

Overall:
  Total Tests: 40
  Passed: 40
  Failed: 0

✓ DEPLOYMENT VERIFICATION PASSED
```

### Interactive Testing
Open in browser: **http://localhost:7860/test_api_integration.html**

Features:
- Visual test interface
- One-click test all endpoints
- Real-time status updates
- JSON response viewer
- Pass/fail tracking

---

## 🎨 UI Pages

### 1. Dashboard
Real-time market overview, sentiment, and top coins

### 2. Market Data
Comprehensive market data viewer with charts and tables

### 3. AI Models
AI model management, status monitoring, and testing

### 4. Sentiment Analysis
Global and asset-specific sentiment analysis

### 5. AI Analyst
AI-powered trading advisor with decision support

### 6. Trading Assistant
Trading signals, strategies, and backtesting

### 7. News
Crypto news aggregator with sentiment analysis

### 8. Providers
API provider management and health monitoring

### 9. Diagnostics
System diagnostics and performance monitoring

### 10. API Explorer
Interactive API testing tool

---

## 🔧 Configuration

### Environment Variables
```bash
# Server
PORT=7860                           # Server port
HOST=0.0.0.0                        # Host address

# Database
DATABASE_URL=sqlite+aiosqlite:///./crypto.db

# Optional: API Keys
COINGECKO_API_KEY=your_key_here
BINANCE_API_KEY=your_key_here
```

### Cache Configuration
Edit `static/shared/js/core/config.js`:
```javascript
export const CACHE_TTL = {
  health: 10000,      // 10 seconds
  market: 30000,      // 30 seconds
  sentiment: 60000,   // 1 minute
  news: 300000,       // 5 minutes
};
```

---

## 📊 Performance

### Response Times
- Health check: < 100ms
- Market data: < 500ms
- News: < 1s
- AI models: < 2s

### Optimizations
- Request deduplication
- Response caching with TTL
- Lazy loading of components
- CSS async loading
- Fallback data for failed requests

---

## 🔐 Security

### Implemented
- ✅ CORS properly configured
- ✅ Rate limiting middleware
- ✅ API key masking in logs
- ✅ Input validation
- ✅ Error message sanitization
- ✅ Permissions-Policy headers

---

## 🚀 HuggingFace Space Deployment

### Step 1: Prepare Repository
```bash
# Ensure all files are committed
git add .
git commit -m "Complete HuggingFace Space integration"
git push origin main
```

### Step 2: Create Space
1. Go to [HuggingFace Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Select "Docker" or "Gradio" SDK
4. Link your repository

### Step 3: Configure Space
- **Port**: 7860 (automatic)
- **Python**: 3.10
- **Entry Point**: `hf_unified_server.py`

### Step 4: Deploy
HuggingFace will automatically:
1. Pull your code
2. Install dependencies
3. Start the server
4. Expose port 7860

### Step 5: Verify
```bash
# Test health endpoint
curl https://your-space-name.hf.space/api/health

# Open UI
open https://your-space-name.hf.space
```

---

## 📚 Documentation

### Core Documentation
- **[QUICK_START.md](./QUICK_START.md)** - Quick start guide
- **[HUGGINGFACE_DEPLOYMENT_COMPLETE.md](./HUGGINGFACE_DEPLOYMENT_COMPLETE.md)** - Complete deployment guide
- **[WORKING_ENDPOINTS.md](./WORKING_ENDPOINTS.md)** - API reference with examples
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - Implementation details

### API Documentation
- **Swagger UI**: http://localhost:7860/docs
- **ReDoc**: http://localhost:7860/redoc
- **OpenAPI Spec**: http://localhost:7860/openapi.json

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port is in use
lsof -ti:7860

# Kill process if needed
kill -9 $(lsof -ti:7860)
```

### API calls failing
1. Check server logs
2. Verify CORS configuration
3. Test with curl
4. Check rate limiting

### Database errors
Database is lazy-initialized and non-critical. Server will start even if database fails.

### UI not loading
1. Verify static files are mounted
2. Check browser console for errors
3. Clear browser cache
4. Test with incognito mode

---

## 📈 Monitoring

### Health Checks
```bash
# System health
curl http://localhost:7860/api/health

# System status
curl http://localhost:7860/api/status

# Router status
curl http://localhost:7860/api/routers
```

### Logs
Server logs include:
- Request/response logging
- Error tracking
- Performance metrics
- Health check results

---

## 🤝 Contributing

### Code Style
- Python: PEP 8
- JavaScript: ES6+
- CSS: BEM methodology

### Testing
- Run automated tests before commit
- Test all modified endpoints
- Verify UI changes in browser

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [CoinGecko](https://www.coingecko.com/) - Crypto data
- [Binance](https://www.binance.com/) - Exchange data
- [Alternative.me](https://alternative.me/) - Fear & Greed Index
- [HuggingFace](https://huggingface.co/) - AI models

---

## 📞 Support

### Resources
- 📖 [Documentation](./HUGGINGFACE_DEPLOYMENT_COMPLETE.md)
- 🧪 [Test Suite](http://localhost:7860/test_api_integration.html)
- 📡 [API Reference](./WORKING_ENDPOINTS.md)
- ✅ [Verification Script](./verify_deployment.py)

### Debugging
1. Check server logs
2. Run verification script
3. Test endpoints manually
4. Review documentation

---

## ✅ Status

**🎉 Production Ready!**

- ✅ All endpoints tested and working
- ✅ UI framework fully integrated
- ✅ Error handling implemented
- ✅ Performance optimized
- ✅ Security configured
- ✅ Documentation complete

**Ready for HuggingFace Space deployment!**

---

**Last Updated:** December 12, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

