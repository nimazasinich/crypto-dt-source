# 🚀 Deployment Guide - HuggingFace Space Update

**Project:** Dreammaker Crypto Trading Platform  
**Update Type:** API Integration Enhancement  
**Date:** December 5, 2025  
**Status:** Ready for Deployment

---

## 📋 What's New

This update adds two major API integrations to the HuggingFace Space:

1. **Alpha Vantage API** - Stock and cryptocurrency data
2. **Massive.com (APIBricks)** - Financial data including dividends, splits, quotes, trades

### New Endpoints Added

#### Alpha Vantage (`/api/alphavantage/*`)
- Health check
- Crypto prices
- OHLCV candlestick data
- Market status
- Crypto ratings (FCAS)
- Global quotes

#### Massive.com (`/api/massive/*`)
- Health check
- Dividends data
- Stock splits
- Real-time quotes
- Recent trades
- OHLCV aggregates
- Ticker details
- Market status

---

## 🔧 Pre-Deployment Checklist

### 1. Environment Variables
Ensure these variables are set in HuggingFace Space settings:

```bash
# Required - Alpha Vantage
ALPHA_VANTAGE_API_KEY=40XS7GQ6AU9NB6Y4

# Required - Massive.com
MASSIVE_API_KEY=PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE

# Existing variables (keep these)
HF_API_TOKEN=your_hf_token_here
HF_SPACE_BASE_URL=your_space_url
COINMARKETCAP_API_KEY=your_key
NEWSAPI_API_KEY=your_key
# ... other existing variables
```

### 2. Files to Deploy
These files must be pushed to HuggingFace Space:

**New Files:**
- `hf-data-engine/providers/alphavantage_provider.py`
- `hf-data-engine/providers/massive_provider.py`
- `api/alphavantage_endpoints.py`
- `api/massive_endpoints.py`
- `NEW_API_INTEGRATIONS.md`
- `DEPLOYMENT_GUIDE.md` (this file)
- `test_new_apis.py`

**Modified Files:**
- `hf_space_api.py` (includes new routers)
- `hf-data-engine/providers/__init__.py` (exports new providers)
- `.env.example` (documents new API keys)

### 3. Dependencies
No new Python packages required! All dependencies are already in `requirements.txt`:
- ✅ `fastapi` - Already installed
- ✅ `httpx` - Already installed
- ✅ `aiohttp` - Already installed

---

## 📦 Deployment Steps

### Step 1: Backup Current Version
```bash
# Clone current version (if not already done)
git clone https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE
cd YOUR-SPACE
git branch backup-$(date +%Y%m%d)
```

### Step 2: Copy New Files
```bash
# Copy all new and modified files to your HF Space repo
# From your local workspace:
cp hf-data-engine/providers/alphavantage_provider.py YOUR-SPACE/hf-data-engine/providers/
cp hf-data-engine/providers/massive_provider.py YOUR-SPACE/hf-data-engine/providers/
cp api/alphavantage_endpoints.py YOUR-SPACE/api/
cp api/massive_endpoints.py YOUR-SPACE/api/
cp hf_space_api.py YOUR-SPACE/
cp hf-data-engine/providers/__init__.py YOUR-SPACE/hf-data-engine/providers/
cp .env.example YOUR-SPACE/
cp NEW_API_INTEGRATIONS.md YOUR-SPACE/
cp DEPLOYMENT_GUIDE.md YOUR-SPACE/
cp test_new_apis.py YOUR-SPACE/
```

### Step 3: Configure Environment Variables
In HuggingFace Space Settings → Repository Secrets, add:

```
ALPHA_VANTAGE_API_KEY = 40XS7GQ6AU9NB6Y4
MASSIVE_API_KEY = PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE
```

### Step 4: Commit and Push
```bash
cd YOUR-SPACE
git add .
git commit -m "✨ Add Alpha Vantage and Massive.com API integrations

- Added AlphaVantageProvider for stock and crypto data
- Added MassiveProvider for financial data (dividends, splits, quotes)
- Created /api/alphavantage/* endpoints
- Created /api/massive/* endpoints
- Updated main app to include new routers
- All new endpoints require HF_TOKEN authentication
- Comprehensive error handling and circuit breaker implemented
"
git push
```

### Step 5: Monitor Deployment
1. Watch HuggingFace Space build logs
2. Wait for "Running" status
3. Check application logs for any errors

---

## ✅ Post-Deployment Verification

### 1. Check Space is Running
Visit your HuggingFace Space URL:
```
https://YOUR-SPACE.hf.space
```

You should see the updated API information showing new data sources.

### 2. Test Health Endpoints
```bash
# Set your HF token
export HF_TOKEN="your_hf_token_here"

# Test Alpha Vantage health
curl -H "Authorization: Bearer $HF_TOKEN" \
  "https://YOUR-SPACE.hf.space/api/alphavantage/health"

# Test Massive.com health
curl -H "Authorization: Bearer $HF_TOKEN" \
  "https://YOUR-SPACE.hf.space/api/massive/health"
```

Expected response (for both):
```json
{
  "success": true,
  "provider": "alphavantage|massive",
  "status": "online",
  "latency": null,
  "last_check": "2025-12-05T...",
  "error": null,
  "timestamp": 1733432100000
}
```

### 3. Test Alpha Vantage Endpoints
```bash
# Test crypto prices
curl -H "Authorization: Bearer $HF_TOKEN" \
  "https://YOUR-SPACE.hf.space/api/alphavantage/prices?symbols=BTC,ETH"

# Test OHLCV data
curl -H "Authorization: Bearer $HF_TOKEN" \
  "https://YOUR-SPACE.hf.space/api/alphavantage/ohlcv?symbol=BTC&interval=1d&limit=5"
```

### 4. Test Massive.com Endpoints
```bash
# Test dividends
curl -H "Authorization: Bearer $HF_TOKEN" \
  "https://YOUR-SPACE.hf.space/api/massive/dividends?ticker=AAPL&limit=5"

# Test quotes
curl -H "Authorization: Bearer $HF_TOKEN" \
  "https://YOUR-SPACE.hf.space/api/massive/quotes/AAPL"
```

### 5. Check API Documentation
Visit the interactive docs:
```
https://YOUR-SPACE.hf.space/docs
```

You should see two new sections:
- `alphavantage` - Alpha Vantage endpoints
- `massive` - Massive.com endpoints

---

## 🔍 Monitoring

### Check Logs
In HuggingFace Space → Logs tab, look for:
```
✅ Alpha Vantage router loaded
✅ Massive.com router loaded
```

### Monitor for Errors
Watch for these potential issues:
- ❌ API key authentication errors
- ❌ Rate limit errors (Alpha Vantage: 5 req/min)
- ⚠️ Circuit breaker activations
- ⚠️ Timeout errors (20 second limit)

### Health Monitoring
Set up periodic health checks (every 5 minutes):
```bash
# Create monitoring script
cat > monitor_apis.sh << 'EOF'
#!/bin/bash
HF_TOKEN="your_token_here"
SPACE_URL="https://YOUR-SPACE.hf.space"

echo "Checking Alpha Vantage..."
curl -s -H "Authorization: Bearer $HF_TOKEN" "$SPACE_URL/api/alphavantage/health" | jq .

echo "Checking Massive.com..."
curl -s -H "Authorization: Bearer $HF_TOKEN" "$SPACE_URL/api/massive/health" | jq .
EOF

chmod +x monitor_apis.sh
```

---

## 🐛 Troubleshooting

### Issue: "Provider not available" Error
**Cause:** Provider initialization failed  
**Solution:**
1. Check API keys are set in HF Space settings
2. Check logs for detailed error message
3. Verify API keys are correct

### Issue: Rate Limit Reached (Alpha Vantage)
**Symptom:** "Alpha Vantage API rate limit reached"  
**Solution:**
- Free tier: 5 requests/minute
- Wait 60 seconds between requests
- Consider upgrading to premium tier

### Issue: Circuit Breaker Open
**Symptom:** "Circuit breaker open for alphavantage"  
**Solution:**
- Circuit breaker opens after 5 consecutive failures
- Automatically resets after 60 seconds
- Check API service status

### Issue: Authentication Error (Massive.com)
**Symptom:** 401 Unauthorized  
**Solution:**
- Verify MASSIVE_API_KEY is set correctly
- Check API key hasn't expired
- Test with curl directly

### Issue: Import Error
**Symptom:** "ModuleNotFoundError: No module named 'hf_data_engine'"  
**Solution:**
- Ensure all provider files are in correct directories
- Check `__init__.py` files are present
- Verify file permissions

---

## 📊 Performance Expectations

### Response Times
- Health checks: < 50ms
- Price queries: 500-2000ms (depends on API)
- OHLCV queries: 1000-3000ms
- Dividend queries: 500-1500ms

### Rate Limits
- **Alpha Vantage:** 5 requests/minute (free tier)
- **Massive.com:** Check your plan limits
- **Circuit Breaker:** Opens after 5 failures, resets after 60s

### Caching
- Providers implement local caching
- Circuit breaker prevents cascading failures
- Automatic retry with exponential backoff

---

## 🔄 Rollback Procedure

If issues occur, rollback to previous version:

```bash
cd YOUR-SPACE
git log --oneline  # Find commit hash before update
git revert <commit-hash>
git push
```

Or restore from backup branch:
```bash
git checkout backup-YYYYMMDD
git push -f origin main
```

---

## 📈 Success Metrics

After 24 hours, verify:
- [ ] Both providers show "online" status
- [ ] No circuit breaker activations
- [ ] < 1% error rate
- [ ] Response times within expectations
- [ ] No authentication errors
- [ ] All endpoints returning valid data

---

## 📚 Additional Resources

- **API Documentation:** https://YOUR-SPACE.hf.space/docs
- **New Integrations Guide:** [NEW_API_INTEGRATIONS.md](./NEW_API_INTEGRATIONS.md)
- **Alpha Vantage Docs:** https://www.alphavantage.co/documentation/
- **Massive.com Docs:** https://api.massive.com/docs
- **Test Script:** `python test_new_apis.py`

---

## 🎯 Next Steps After Deployment

1. **Monitor for 24 hours**
   - Check logs regularly
   - Monitor error rates
   - Track response times

2. **Update Frontend**
   - Add new API endpoints to frontend code
   - Update data fetching logic
   - Test end-to-end integration

3. **Documentation**
   - Update API documentation
   - Add usage examples
   - Create integration guides

4. **Performance Tuning**
   - Monitor rate limits
   - Adjust caching if needed
   - Optimize query patterns

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] All new files copied
- [ ] Environment variables configured
- [ ] Code tested locally
- [ ] Backup created

### Deployment
- [ ] Files committed to git
- [ ] Pushed to HuggingFace Space
- [ ] Build completed successfully
- [ ] Space is running

### Post-Deployment
- [ ] Health checks passing
- [ ] Sample requests working
- [ ] API docs showing new endpoints
- [ ] No errors in logs
- [ ] Monitoring set up

---

**Deployment Date:** _____________  
**Deployed By:** _____________  
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Completed | ⬜ Rolled Back

---

**Version:** 1.0.0  
**Last Updated:** December 5, 2025  
**Project:** Dreammaker Crypto Trading Platform
