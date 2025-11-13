# 🚀 Quick Start Guide - Crypto API Monitor with HuggingFace Integration

## ✅ Server is Running!

Your application is now live at: **http://localhost:7860**

## 📱 Access Points

### 1. Main Dashboard (Full Features)
**URL:** http://localhost:7860/index.html

Features:
- Real-time API monitoring
- Provider inventory
- Rate limit tracking
- Connection logs
- Schedule management
- Data freshness monitoring
- Failure analysis
- **🤗 HuggingFace Tab** (NEW!)

### 2. HuggingFace Console (Standalone)
**URL:** http://localhost:7860/hf_console.html

Features:
- HF Health Status
- Models Registry Browser
- Datasets Registry Browser
- Local Search (snapshot)
- Sentiment Analysis (local pipeline)

### 3. API Documentation
**URL:** http://localhost:7860/docs

Interactive API documentation with all endpoints

## 🤗 HuggingFace Features

### Available Endpoints:

1. **Health Check**
   ```
   GET /api/hf/health
   ```
   Returns: Registry health, last refresh time, model/dataset counts

2. **Force Refresh Registry**
   ```
   POST /api/hf/refresh
   ```
   Manually trigger registry update from HuggingFace Hub

3. **Get Models Registry**
   ```
   GET /api/hf/registry?kind=models
   ```
   Returns: List of all cached crypto-related models

4. **Get Datasets Registry**
   ```
   GET /api/hf/registry?kind=datasets
   ```
   Returns: List of all cached crypto-related datasets

5. **Search Registry**
   ```
   GET /api/hf/search?q=crypto&kind=models
   ```
   Search local snapshot for models or datasets

6. **Run Sentiment Analysis**
   ```
   POST /api/hf/run-sentiment
   Body: {"texts": ["BTC strong", "ETH weak"]}
   ```
   Analyze crypto sentiment using local transformers

## 🎯 How to Use

### Option 1: Main Dashboard
1. Open http://localhost:7860/index.html in your browser
2. Click on the **"🤗 HuggingFace"** tab at the top
3. Explore:
   - Health status
   - Models and datasets registries
   - Search functionality
   - Sentiment analysis

### Option 2: Standalone HF Console
1. Open http://localhost:7860/hf_console.html
2. All HF features in a clean, focused interface
3. Perfect for testing and development

## 🧪 Test the Integration

### Test 1: Check Health
```powershell
Invoke-WebRequest -Uri "http://localhost:7860/api/hf/health" -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Test 2: Refresh Registry
```powershell
Invoke-WebRequest -Uri "http://localhost:7860/api/hf/refresh" -Method POST -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Test 3: Get Models
```powershell
Invoke-WebRequest -Uri "http://localhost:7860/api/hf/registry?kind=models" -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Test 4: Run Sentiment Analysis
```powershell
$body = @{texts = @("BTC strong breakout", "ETH looks weak")} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:7860/api/hf/run-sentiment" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing | Select-Object -ExpandProperty Content
```

## 📊 What's Included

### Seed Models (Always Available):
- ElKulako/cryptobert
- kk08/CryptoBERT

### Seed Datasets (Always Available):
- linxy/CryptoCoin
- WinkingFace/CryptoLM-Bitcoin-BTC-USDT
- WinkingFace/CryptoLM-Ethereum-ETH-USDT
- WinkingFace/CryptoLM-Solana-SOL-USDT
- WinkingFace/CryptoLM-Ripple-XRP-USDT

### Auto-Discovery:
- Searches HuggingFace Hub for crypto-related models
- Searches for sentiment-analysis models
- Auto-refreshes every 6 hours (configurable)

## ⚙️ Configuration

Edit `.env` file to customize:

```env
# HuggingFace Token (optional, for higher rate limits)
HUGGINGFACE_TOKEN=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

# Enable/disable local sentiment analysis
ENABLE_SENTIMENT=true

# Model selection
SENTIMENT_SOCIAL_MODEL=ElKulako/cryptobert
SENTIMENT_NEWS_MODEL=kk08/CryptoBERT

# Refresh interval (seconds)
HF_REGISTRY_REFRESH_SEC=21600

# HTTP timeout (seconds)
HF_HTTP_TIMEOUT=8.0
```

## 🛑 Stop the Server

Press `CTRL+C` in the terminal where the server is running

Or use the process manager to stop process ID 6

## 🔄 Restart the Server

```bash
# Production server (recommended)
python app.py

# Or use the convenient launcher
python start_server.py
```

## 📝 Notes

- **First Load**: The first sentiment analysis may take 30-60 seconds as models download
- **Registry**: Auto-refreshes every 6 hours, or manually via the UI
- **Free Resources**: All endpoints use free HuggingFace APIs
- **No API Key Required**: Works without authentication (with rate limits)
- **Local Inference**: Sentiment analysis runs locally using transformers

## 🎉 You're All Set!

The application is running and ready to use. Open your browser and explore!

**Main Dashboard:** http://localhost:7860/index.html
**HF Console:** http://localhost:7860/hf_console.html
