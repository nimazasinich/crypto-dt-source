# HuggingFace Space Endpoint Verification Guide

## Overview
This document provides verification steps for all documented endpoints in the cryptocurrency data platform.

## Quick Test

### Local Testing
```bash
# Start the server
python hf_unified_server.py

# In another terminal, run the test script
python test_endpoints_comprehensive.py http://localhost:7860
```

### HuggingFace Space Testing
```bash
python test_endpoints_comprehensive.py https://your-space-name.hf.space
```

## Manual Endpoint Tests

### 1. Health & Status Endpoints

```bash
# Health check
curl http://localhost:7860/api/health

# System status
curl http://localhost:7860/api/status

# Router status
curl http://localhost:7860/api/routers

# List all endpoints
curl http://localhost:7860/api/endpoints
```

### 2. Market Data Endpoints

```bash
# Market overview
curl http://localhost:7860/api/market

# Top coins by market cap
curl http://localhost:7860/api/coins/top?limit=50
curl http://localhost:7860/api/market/top?limit=50

# Trending coins
curl http://localhost:7860/api/trending
curl http://localhost:7860/api/market/trending
```

### 3. Sentiment Analysis Endpoints

```bash
# Global sentiment
curl http://localhost:7860/api/sentiment/global?timeframe=1D

# Asset-specific sentiment
curl http://localhost:7860/api/sentiment/asset/BTC

# Analyze text sentiment
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Bitcoin is pumping! 🚀", "mode": "crypto"}'

# Service sentiment (unified API)
curl -X POST http://localhost:7860/api/service/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "Ethereum looks bullish", "mode": "crypto"}'
```

### 4. News Endpoints

```bash
# Latest news
curl http://localhost:7860/api/news?limit=50

# Latest news (alias)
curl http://localhost:7860/api/news/latest?limit=10

# News by source
curl "http://localhost:7860/api/news?source=CoinDesk"
```

### 5. AI Models Endpoints

```bash
# List available models
curl http://localhost:7860/api/models/list

# Models status
curl http://localhost:7860/api/models/status

# Models summary
curl http://localhost:7860/api/models/summary

# Models health
curl http://localhost:7860/api/models/health

# Test model
curl -X POST http://localhost:7860/api/models/test

# Reinitialize models
curl -X POST http://localhost:7860/api/models/reinitialize
```

### 6. AI Trading Signals

```bash
# Get AI signals for BTC
curl http://localhost:7860/api/ai/signals?symbol=BTC

# Get AI trading decision
curl -X POST http://localhost:7860/api/ai/decision \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC",
    "horizon": "swing",
    "risk_tolerance": "moderate"
  }'
```

### 7. OHLCV Data Endpoints

```bash
# Get OHLCV for single symbol
curl "http://localhost:7860/api/ohlcv/BTC?timeframe=1h&limit=100"

# Get OHLCV for multiple symbols
curl "http://localhost:7860/api/ohlcv/multi?symbols=BTC,ETH&timeframe=1h&limit=100"

# Market OHLC (alternative endpoint)
curl "http://localhost:7860/api/market/ohlc?symbol=BTC&interval=1h&limit=100"
```

### 8. Technical Analysis Endpoints

```bash
# Quick technical analysis
curl http://localhost:7860/api/technical/quick/BTC

# Comprehensive technical analysis
curl http://localhost:7860/api/technical/comprehensive/BTC

# Risk assessment
curl http://localhost:7860/api/technical/risk/BTC
```

### 9. Trading & Backtesting

```bash
# Backtest trading strategy
curl "http://localhost:7860/api/trading/backtest?symbol=BTC"

# Futures positions
curl http://localhost:7860/api/futures/positions
```

### 10. Resources & Providers

```bash
# Resource statistics
curl http://localhost:7860/api/resources

# Resources summary
curl http://localhost:7860/api/resources/summary

# Resource categories
curl http://localhost:7860/api/resources/categories

# Resource stats
curl http://localhost:7860/api/resources/stats

# Data providers list
curl http://localhost:7860/api/providers
```

### 11. Unified Service API (Multi-source with fallback)

```bash
# Get rate with automatic fallback
curl "http://localhost:7860/api/service/rate?pair=BTC/USDT"

# Batch rates
curl "http://localhost:7860/api/service/rate/batch?pairs=BTC/USDT,ETH/USDT"

# Historical data
curl "http://localhost:7860/api/service/history?symbol=BTC&interval=1h&limit=100"

# Market status
curl http://localhost:7860/api/service/market-status

# Pair information
curl http://localhost:7860/api/service/pair/BTC/USDT
```

### 12. Monitoring & System

```bash
# Real-time monitoring status
curl http://localhost:7860/api/monitoring/status

# System resources
curl http://localhost:7860/api/monitoring/resources
```

## Expected Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-12-12T10:00:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "timestamp": "2025-12-12T10:00:00Z"
}
```

## Common Issues & Solutions

### 1. 404 Not Found
- Verify endpoint path is correct
- Check if router is loaded: `curl http://localhost:7860/api/routers`
- Ensure server is running on correct port

### 2. 429 Rate Limited
- External API (like CoinGecko) rate limit reached
- System will automatically fallback to alternative providers
- Wait a few minutes and retry

### 3. 500 Internal Server Error
- Check server logs for detailed error
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure database is initialized

### 4. CORS Errors (Browser)
- CORS is enabled by default for all origins
- If issues persist, check browser console for specific error
- Verify request headers are properly set

### 5. Database Connection Issues
- SQLite database should auto-initialize
- Check `data/` directory exists and is writable
- Review logs for database errors

## Performance Benchmarks

Expected response times:
- Health checks: < 50ms
- Market data: 100-500ms (depends on external API)
- AI model inference: 200-1000ms (depends on model)
- Database queries: < 100ms
- Static files: < 50ms

## Integration Checklist

- [ ] Server starts without errors on port 7860
- [ ] GET `/api/health` returns 200
- [ ] GET `/` serves dashboard UI
- [ ] All documented endpoints respond (not all 404)
- [ ] UI pages load correctly
- [ ] API calls from frontend work
- [ ] No CORS errors in browser console
- [ ] Database initializes without errors
- [ ] Static files serve correctly
- [ ] WebSocket connections work (optional)

## Automated Testing

Run the comprehensive test suite:

```bash
# Test local deployment
python test_endpoints_comprehensive.py

# Test HuggingFace Space
python test_endpoints_comprehensive.py https://your-space.hf.space

# Expected output: 80%+ success rate
```

## Support

If endpoints are failing:
1. Check HuggingFace Space logs for errors
2. Verify all environment variables are set
3. Ensure requirements.txt dependencies are installed
4. Test endpoints individually using curl
5. Check browser console for client-side errors

## Notes

- Some endpoints may return fallback data if external APIs are unavailable
- OHLCV data requires external API access (Binance, HuggingFace datasets)
- AI model endpoints work without models loaded (return mock data)
- Database endpoints gracefully degrade if database is unavailable
