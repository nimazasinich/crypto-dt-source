# HUGGING FACE SPACES DEPLOYMENT INSTRUCTIONS
## Production-Ready Deployment Guide

**Date:** 2025-11-16  
**Platform:** Hugging Face Spaces (Docker Runtime)  
**Status:** Ready after applying fixes

---

## PREREQUISITES

Before deploying, you MUST apply all fixes from the audit report:

### 1. Replace Files with Fixed Versions

```bash
# Backup originals
cp requirements.txt requirements.txt.backup
cp Dockerfile Dockerfile.backup

# Apply fixes
cp requirements_FIXED.txt requirements.txt
cp Dockerfile_FIXED Dockerfile

# Verify new files exist
ls -la provider_fetch_helper.py  # Should exist after fixes
ls -la HUGGINGFACE_DEPLOYMENT_AUDIT_REPORT.md  # Should exist
```

### 2. Verify Fixed Issues Checklist

- [x] requirements.txt has fastapi, uvicorn, pydantic, sqlalchemy
- [x] Dockerfile creates all required directories (logs, data, etc.)
- [x] provider_fetch_helper.py exists with proper logic
- [ ] API endpoints use real data (manual fix needed - see below)
- [ ] USE_MOCK_DATA environment variable implemented (manual fix needed)
- [ ] Database schema initialized on startup

---

## HUGGING FACE SPACE CONFIGURATION

### Space Settings

1. **Create New Space:**
   - Go to https://huggingface.co/new-space
   - Name: `crypto-monitor-api` (or your choice)
   - License: MIT (or your choice)
   - SDK: **Docker**
   - Hardware: CPU basic (free tier)

2. **Space Configuration File** (`README.md` in space root):

```yaml
---
title: Crypto Monitor API
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---
```

---

## ENVIRONMENT VARIABLES

### Required Environment Variables (Set in HF Space Settings)

```bash
# Automatically set by Hugging Face
PORT=7860

# Optional (set in Space Settings > Variables)
USE_MOCK_DATA=false          # Use real data (default)
ENABLE_AUTO_DISCOVERY=false  # Disable auto-discovery in production
LOG_LEVEL=INFO               # Logging level
DATABASE_PATH=/app/data/crypto_monitor.db
```

### How to Set Environment Variables in HF Spaces

1. Go to your Space > Settings > Variables
2. Click "New variable"
3. Add each variable name and value
4. Click "Add variable"

---

## DEPLOYMENT STEPS

### Step 1: Prepare Repository

```bash
# 1. Ensure you're in the workspace directory
cd /workspace

# 2. Apply all fixes (if not already done)
cp requirements_FIXED.txt requirements.txt
cp Dockerfile_FIXED Dockerfile

# 3. Verify critical files exist
ls -la requirements.txt Dockerfile provider_fetch_helper.py

# 4. Test Docker build locally (HIGHLY RECOMMENDED)
docker build -t crypto-monitor-test .

# 5. Test Docker run locally
docker run -p 7860:7860 -e PORT=7860 crypto-monitor-test
```

### Step 2: Initialize Git for HF Spaces

```bash
# Install git-lfs (required for HF)
git lfs install

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit with fixes for HF Spaces deployment"

# Add HF Space as remote (replace USERNAME and SPACENAME)
git remote add hf https://huggingface.co/spaces/USERNAME/SPACENAME
```

### Step 3: Push to Hugging Face

```bash
# Push to HF Space
git push hf main

# Monitor deployment logs in HF Space web interface
# Build typically takes 5-10 minutes
```

### Step 4: Monitor Deployment

1. Go to your Space URL: `https://huggingface.co/spaces/USERNAME/SPACENAME`
2. Click "Logs" tab to monitor build progress
3. Watch for successful startup message:
   ```
   ✅ سرور آماده است
   INFO: Uvicorn running on http://0.0.0.0:7860
   ```

---

## VERIFICATION & TESTING

### Once Deployed, Run These Tests

Replace `YOUR-SPACE-URL` with your actual Space URL (e.g., `https://username-crypto-monitor.hf.space`)

#### 1. Health Check (Should return 200 OK)

```bash
curl -X GET https://YOUR-SPACE-URL/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-16T...",
  "providers_count": 76,
  "online_count": 50,
  "connected_clients": 0,
  "total_sessions": 0
}
```

---

#### 2. Market Data Endpoint

```bash
curl -X GET https://YOUR-SPACE-URL/api/market
```

**CRITICAL:** Should return REAL data (NOT mock data with hardcoded $43,250.50)

**Expected Response (Real Data):**
```json
{
  "cryptocurrencies": [
    {
      "rank": 1,
      "name": "Bitcoin",
      "symbol": "BTC",
      "price": <REAL_CURRENT_PRICE>,  // Should be current market price
      "change_24h": <REAL_CHANGE>,
      "market_cap": <REAL_MARKET_CAP>,
      ...
    }
  ]
}
```

**If you see hardcoded prices** → MOCK DATA STILL ACTIVE → Deployment FAILED requirement

---

#### 3. Sentiment Endpoint (Alternative.me Fear & Greed)

```bash
curl -X GET https://YOUR-SPACE-URL/api/sentiment
```

**Expected Response (Real Data from Alternative.me):**
```json
{
  "fear_greed_index": {
    "value": <REAL_FNG_VALUE>,  // 0-100 from Alternative.me
    "classification": "Fear|Greed|Extreme Fear|Extreme Greed"
  }
}
```

---

#### 4. Trending Endpoint (CoinGecko)

```bash
curl -X GET https://YOUR-SPACE-URL/api/trending
```

**Expected Responses:**

**Option A: Real Data**
```json
{
  "trending": [
    {
      "name": "<REAL_TRENDING_COIN>",
      "symbol": "<SYMBOL>",
      "thumb": "<IMAGE_URL>"
    }
  ]
}
```

**Option B: Not Implemented (503 Error)**
```json
{
  "error": "Service Unavailable",
  "message": "Trending data not available",
  "timestamp": "..."
}
```

---

#### 5. DeFi Endpoint

```bash
curl -X GET https://YOUR-SPACE-URL/api/defi
```

**Expected Response (503 if not implemented):**
```json
{
  "error": "Service Unavailable",
  "message": "DeFi data not available",
  "timestamp": "..."
}
```

**OR Real DefiLlama data if implemented**

---

#### 6. HuggingFace Sentiment Analysis

```bash
curl -X POST https://YOUR-SPACE-URL/api/hf/run-sentiment \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Bitcoin is looking bullish today"]}'
```

**Expected Response (501 if not implemented):**
```json
{
  "error": "Not Implemented",
  "message": "HuggingFace sentiment analysis not yet available",
  "timestamp": "..."
}
```

---

#### 7. Provider Management

```bash
# Get all providers
curl -X GET https://YOUR-SPACE-URL/api/providers

# Get provider pools
curl -X GET https://YOUR-SPACE-URL/api/pools

# Get specific provider
curl -X GET https://YOUR-SPACE-URL/api/providers/coingecko

# Check provider health
curl -X POST https://YOUR-SPACE-URL/api/providers/coingecko/health-check
```

---

#### 8. Market History Endpoint

```bash
curl -X GET https://YOUR-SPACE-URL/api/market/history?symbol=BTC&hours=24
```

**Expected:** Either real historical data OR 404/503 error if not implemented

---

#### 9. System Status

```bash
curl -X GET https://YOUR-SPACE-URL/api/status
```

**Expected Response:**
```json
{
  "status": "operational",
  "timestamp": "...",
  "total_providers": 76,
  "online": 50,
  "offline": 10,
  "degraded": 5,
  "avg_response_time_ms": 150.5,
  "total_requests": 1000,
  "successful_requests": 950,
  "success_rate": 95.0
}
```

---

## DEBUGGING DEPLOYMENT ISSUES

### Issue 1: Container Fails to Start

**Symptom:** Space shows "Building..." then immediately fails

**Causes & Solutions:**

1. **Missing Dependencies:**
   ```bash
   # Check Dockerfile logs for "ModuleNotFoundError"
   # Solution: Verify requirements.txt has all dependencies
   grep -E "fastapi|uvicorn|pydantic" requirements.txt
   ```

2. **Directory Creation Failed:**
   ```bash
   # Check for permission errors
   # Solution: Ensure Dockerfile has:
   RUN mkdir -p logs data data/exports data/database data/backups && \
       chmod -R 777 logs data
   ```

3. **Port Binding Issues:**
   ```bash
   # Ensure using PORT env var
   CMD ["sh", "-c", "python -m uvicorn api_server_extended:app --host 0.0.0.0 --port ${PORT:-7860}"]
   ```

---

### Issue 2: Endpoints Return 404

**Symptom:** `/api/market` returns 404 Not Found

**Cause:** Route not defined or import error

**Solution:**
```bash
# Check logs for import errors
# Verify api_server_extended.py has routes defined
grep -A 5 "@app.get(\"/api/market\")" api_server_extended.py
```

---

### Issue 3: Endpoints Return Mock Data

**Symptom:** `/api/market` returns hardcoded Bitcoin at $43,250.50

**Cause:** Mock endpoints still active

**Solution:**
- Replace mock endpoints with real data integration
- Check USE_MOCK_DATA environment variable
- Review lines 599-677 in api_server_extended.py

---

### Issue 4: Database Errors

**Symptom:** "table not found" or "no such table: prices"

**Cause:** Database schema not initialized

**Solution:**
```python
# Add to startup event in api_server_extended.py
from database import get_database

@app.on_event("startup")
async def startup_event():
    # Initialize database
    db = get_database()
    # Tables will be created automatically by CryptoDatabase.__init__
```

---

### Issue 5: Provider Errors

**Symptom:** "Provider pool not found" or "No available providers"

**Cause:** Provider config files not loaded

**Solution:**
```bash
# Verify config files exist in Docker container
docker exec <container_id> ls -la /app/providers_config_extended.json

# Check provider loading in logs
docker logs <container_id> | grep "بارگذاری موفق"
```

---

## MONITORING & MAINTENANCE

### View Live Logs

```bash
# HF Spaces Web Interface: Go to Logs tab

# Or using HF CLI:
huggingface-cli logs USERNAME/SPACENAME --follow
```

### Check Resource Usage

```bash
# In HF Space > Settings > Hardware
# Monitor CPU and memory usage
# Upgrade to paid tier if needed
```

### Update Deployment

```bash
# Make changes locally
git add .
git commit -m "Update: description"
git push hf main

# HF will automatically rebuild and redeploy
```

---

## PRODUCTION CHECKLIST

Before going live, verify:

- [ ] All verification curl commands return expected results
- [ ] NO mock data in any endpoint (unless USE_MOCK_DATA=true is set)
- [ ] All provider health checks pass (at least 70% online)
- [ ] Database operations work (market history, logs, etc.)
- [ ] WebSocket connections work (if applicable)
- [ ] Error responses have correct format (503, 501, etc.)
- [ ] Logs are being written correctly
- [ ] Health check endpoint returns 200
- [ ] No hardcoded local URLs (localhost, 127.0.0.1)
- [ ] Environment variables are correctly configured
- [ ] Rate limiting is working (if implemented)

---

## ROLLBACK PROCEDURE

If deployment fails:

```bash
# 1. Revert to previous commit
git log --oneline  # Find previous working commit
git reset --hard <commit-hash>

# 2. Push to HF
git push hf main --force

# 3. Monitor logs
# Space will rebuild with previous version
```

---

## SUPPORT & TROUBLESHOOTING

### HuggingFace Documentation
- Spaces Guide: https://huggingface.co/docs/hub/spaces
- Docker Spaces: https://huggingface.co/docs/hub/spaces-sdks-docker

### Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `ModuleNotFoundError: No module named 'fastapi'` | Missing dependency | Add to requirements.txt |
| `Address already in use` | Port conflict | Check PORT env var |
| `Permission denied` | File permissions | Add chmod in Dockerfile |
| `Connection refused` | Service not started | Check startup logs |
| `503 Service Unavailable` | All providers failed | Check provider configs |

---

## FINAL NOTES

1. **Mock Data:** Ensure USE_MOCK_DATA=false in production
2. **API Keys:** No API keys are required for free data sources
3. **Rate Limits:** Free tier providers have rate limits - implement caching
4. **Scaling:** Free CPU basic tier may be slow under load - upgrade if needed
5. **Monitoring:** Set up external monitoring (UptimeRobot, Pingdom, etc.)

---

**Deployment Status:** READY (after applying fixes)  
**Estimated Deployment Time:** 10-15 minutes  
**Support:** Check HUGGINGFACE_DEPLOYMENT_AUDIT_REPORT.md for detailed issues

---

END OF DEPLOYMENT INSTRUCTIONS
