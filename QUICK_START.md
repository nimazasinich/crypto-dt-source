# Quick Start Guide - HuggingFace Space Deployment

## 🚀 Start the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python hf_unified_server.py
```

The server will start on **http://localhost:7860**

## ✅ Verify Deployment

### Option 1: Automated Testing (Recommended)

```bash
# Run verification script
python verify_deployment.py
```

This will test all critical endpoints and provide a detailed report.

### Option 2: Interactive Test Suite

1. Start the server
2. Open in browser: **http://localhost:7860/test_api_integration.html**
3. Click "Run All Tests" button

### Option 3: Manual Testing

```bash
# Test health
curl http://localhost:7860/api/health

# Test market data
curl http://localhost:7860/api/market

# Test sentiment
curl "http://localhost:7860/api/sentiment/global?timeframe=1D"

# Test models
curl http://localhost:7860/api/models/summary
```

## 📊 Expected Results

### Health Check
```json
{
  "status": "healthy",
  "timestamp": "2025-12-12T10:30:00.000000Z",
  "service": "unified_query_service",
  "version": "1.0.0"
}
```

### Market Overview
```json
{
  "total_market_cap": 2450000000000,
  "total_volume": 98500000000,
  "btc_dominance": 52.3,
  "eth_dominance": 17.8,
  "timestamp": "2025-12-12T10:30:00.000000Z"
}
```

## 🌐 Access UI

Once the server is running:

- **Dashboard:** http://localhost:7860/ or http://localhost:7860/dashboard
- **Market Data:** http://localhost:7860/market
- **AI Models:** http://localhost:7860/models
- **Sentiment:** http://localhost:7860/sentiment
- **News:** http://localhost:7860/news
- **API Explorer:** http://localhost:7860/api-explorer
- **Test Suite:** http://localhost:7860/test_api_integration.html

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 7860 is already in use
lsof -ti:7860

# Kill process if needed
kill -9 $(lsof -ti:7860)
```

### Database errors
Database initialization is lazy and non-critical. Server will start even if database fails.

### API endpoints failing
1. Check server logs
2. Verify all routers are loaded (check startup logs)
3. Test with curl to isolate issue
4. Check CORS configuration

## 📦 HuggingFace Space Deployment

### Files Structure
```
workspace/
├── hf_unified_server.py     ← Entry point (REQUIRED)
├── requirements.txt          ← Dependencies (REQUIRED)
├── README.md                 ← Documentation
├── static/                   ← UI files (REQUIRED)
├── backend/                  ← Backend code (REQUIRED)
├── database/                 ← Database code
├── utils/                    ← Utilities
└── ...
```

### Space Configuration

**Dockerfile (optional - for custom setup):**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "hf_unified_server.py"]
```

**Or use default Python SDK:**
- SDK: Gradio (or Docker)
- Python version: 3.10
- Port: 7860 (automatic)

### Environment Variables (Optional)
```
PORT=7860
HOST=0.0.0.0
DATABASE_URL=sqlite+aiosqlite:///./crypto.db
```

## ✅ Pre-Deployment Checklist

- [ ] Server starts without errors
- [ ] All critical endpoints return 200 OK
- [ ] Dashboard loads correctly
- [ ] Static files are accessible
- [ ] No CORS errors in browser console
- [ ] Navigation between pages works
- [ ] API calls from UI connect to backend
- [ ] Verification script passes

## 📚 Documentation

- **Complete Guide:** [HUGGINGFACE_DEPLOYMENT_COMPLETE.md](./HUGGINGFACE_DEPLOYMENT_COMPLETE.md)
- **API Reference:** See documentation in HUGGINGFACE_DEPLOYMENT_COMPLETE.md
- **Test Suite:** Open test_api_integration.html in browser

## 🎉 Ready to Deploy!

Once all tests pass, your application is ready for HuggingFace Space deployment!

---

**Need Help?**
- Check logs: `python hf_unified_server.py` output
- Run verification: `python verify_deployment.py`
- Test endpoints: http://localhost:7860/test_api_integration.html
