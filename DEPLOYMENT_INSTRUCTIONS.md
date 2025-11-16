# 🚀 DEPLOYMENT INSTRUCTIONS FOR HUGGING FACE SPACES

## ✅ DEPLOYMENT STATUS: READY FOR PRODUCTION

All critical blockers have been resolved. This application is now ready for deployment to Hugging Face Spaces.

---

## 📋 PRE-DEPLOYMENT CHECKLIST

✅ **Dependencies**: All required packages listed in `requirements.txt` with pinned versions  
✅ **Dockerfile**: Properly configured with directory creation and PORT variable support  
✅ **Mock Data Removed**: All endpoints use real data providers or return explicit error codes  
✅ **USE_MOCK_DATA Flag**: Implemented for optional testing/demo mode  
✅ **Database Integration**: SQLite database properly integrated with price history  
✅ **Provider Management**: Circuit breaker and failover logic implemented  
✅ **Error Handling**: All endpoints return proper HTTP status codes (503/501) on failures  

---

## 🛠️ LOCAL TESTING

### 1. Build Docker Image

```bash
docker build -t crypto-monitor .
```

### 2. Run Container Locally

```bash
# Default mode (real data, port 7860)
docker run -p 7860:7860 crypto-monitor

# With custom port
docker run -p 8000:8000 -e PORT=8000 crypto-monitor

# With mock data enabled (for testing)
docker run -p 7860:7860 -e USE_MOCK_DATA=true crypto-monitor
```

### 3. Test Key Endpoints

```bash
# Health check
curl http://localhost:7860/health

# Market data (real CoinGecko)
curl http://localhost:7860/api/market

# Market history (from database)
curl "http://localhost:7860/api/market/history?symbol=BTC&limit=10"

# Sentiment data (real Alternative.me)
curl http://localhost:7860/api/sentiment

# Trending coins (real CoinGecko)
curl http://localhost:7860/api/trending

# DeFi data (returns 503 - not implemented)
curl http://localhost:7860/api/defi

# HF Sentiment (returns 501 - not implemented)
curl -X POST http://localhost:7860/api/hf/run-sentiment \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Bitcoin is bullish"]}'
```

---

## 🌐 HUGGING FACE SPACES DEPLOYMENT

### Step 1: Create New Space

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Choose:
   - **Space name**: `crypto-data-aggregator`
   - **License**: `MIT`
   - **Space SDK**: `Docker`
   - **Visibility**: `Public` (or Private)

### Step 2: Configure Repository

Push your code to the Hugging Face Space repository:

```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/crypto-data-aggregator
git push hf main
```

### Step 3: Configure Environment Variables (Optional)

In your Space settings, add environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `PORT` | `7860` | **Auto-set by HF Spaces** - Do not override |
| `USE_MOCK_DATA` | `false` | Use real data providers (default) |
| `ENABLE_AUTO_DISCOVERY` | `false` | Disable auto-discovery service |

⚠️ **Important**: Hugging Face Spaces automatically sets `PORT=7860`. Our Dockerfile is configured to use this.

### Step 4: Monitor Deployment

1. Watch the build logs in your Space
2. Wait for "Running" status (typically 2-5 minutes)
3. Access your app at: `https://huggingface.co/spaces/YOUR_USERNAME/crypto-data-aggregator`

---

## 🔍 POST-DEPLOYMENT VERIFICATION

### Automated Health Check

```bash
SPACE_URL="https://YOUR_USERNAME-crypto-data-aggregator.hf.space"

# 1. Health check
curl $SPACE_URL/health | jq

# 2. Market data
curl $SPACE_URL/api/market | jq '.cryptocurrencies[] | {name, symbol, price}'

# 3. Sentiment
curl $SPACE_URL/api/sentiment | jq '.fear_greed_index'

# 4. Trending
curl $SPACE_URL/api/trending | jq '.trending[0:3]'

# 5. Market history
curl "$SPACE_URL/api/market/history?symbol=BTC&limit=5" | jq
```

### Expected Responses

#### ✅ Success Responses:

- `/health`: `{"status": "healthy", "providers_count": N, "online_count": N}`
- `/api/market`: Array of cryptocurrencies with real prices from CoinGecko
- `/api/sentiment`: Fear & Greed Index from Alternative.me
- `/api/trending`: Top trending coins from CoinGecko
- `/api/market/history`: Array of historical price records from database

#### ⚠️ Expected "Not Implemented" Responses:

- `/api/defi`: HTTP 503 with message about requiring DefiLlama integration
- `/api/hf/run-sentiment`: HTTP 501 with message about ML models not loaded

---

## 🐛 TROUBLESHOOTING

### Issue: Container fails to start

**Check:**
```bash
docker logs <container-id>
```

**Common causes:**
- Missing dependencies in `requirements.txt`
- Syntax errors in Python files
- Missing required directories (should be auto-created)

### Issue: Endpoints return 503 errors

**Possible causes:**
1. External API rate limits hit (CoinGecko, Alternative.me)
2. Network connectivity issues
3. Provider configuration errors

**Solution:**
- Check logs: `/api/logs/errors`
- Enable mock mode temporarily: `USE_MOCK_DATA=true`
- Wait 1-2 minutes for circuit breakers to reset

### Issue: Database errors

**Check:**
- Ensure `data/` directory is writable
- Check database file exists: `ls -la data/database/`
- Review database logs in `/api/logs`

---

## 📊 MONITORING & MAINTENANCE

### Key Metrics to Monitor

1. **Provider Health**: `/api/providers` - Check success rates
2. **System Status**: `/api/status` - Overall system health
3. **Error Logs**: `/api/logs/errors` - Recent failures
4. **Database Stats**: Query `/api/market/history` for data freshness

### Regular Maintenance

- **Daily**: Check `/api/status` for provider health
- **Weekly**: Review `/api/logs/stats` for error trends
- **Monthly**: Clean old database records (auto-cleanup configured)

---

## 🔐 SECURITY NOTES

✅ **No API Keys Required**: All data sources use free public endpoints  
✅ **No Authentication Needed**: Public read-only data  
✅ **Rate Limiting**: Implemented in provider management  
✅ **Circuit Breakers**: Automatic failover prevents cascading failures  

---

## 📝 ENVIRONMENT VARIABLES REFERENCE

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `7860` | Server port (set by HF Spaces) |
| `USE_MOCK_DATA` | `false` | Enable mock data mode for testing |
| `ENABLE_AUTO_DISCOVERY` | `false` | Enable automatic resource discovery |
| `PYTHONUNBUFFERED` | `1` | Enable real-time logs |

---

## 🎯 SUCCESS CRITERIA

Your deployment is **SUCCESSFUL** if:

✅ Health endpoint returns `"status": "healthy"`  
✅ Market data shows real Bitcoin/Ethereum prices  
✅ Sentiment shows current Fear & Greed Index  
✅ Trending shows actual trending coins  
✅ No hardcoded mock data in responses (unless `USE_MOCK_DATA=true`)  
✅ DeFi and HF endpoints return proper 503/501 errors  
✅ Database history accumulates over time  

---

## 📞 SUPPORT

If you encounter issues:

1. Check logs: `docker logs <container>` or HF Space logs
2. Review error endpoints: `/api/logs/errors`
3. Run diagnostics: `/api/diagnostics/run`
4. Enable mock mode for testing: `USE_MOCK_DATA=true`

---

## 🎉 DEPLOYMENT COMPLETE

Once all verification steps pass, your crypto data aggregator is **LIVE** and ready for production use!

**Next Steps:**
- Share your Space URL
- Monitor initial usage patterns
- Set up optional monitoring dashboards
- Consider adding more data providers for redundancy
