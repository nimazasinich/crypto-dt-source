# 🚀 Quick Start Guide

Get your Crypto Intelligence Hub running in 5 minutes!

---

## ⚡ Super Quick Start (3 Commands)

```bash
# 1. Install dependencies
pip install -r requirements_hf.txt

# 2. Verify installation
python3 verify_installation.py

# 3. Start server
uvicorn hf_space_api:app --reload --host 0.0.0.0 --port 7860
```

**Open browser:** http://localhost:7860

---

## 📋 Step-by-Step (5 Minutes)

### 1. Prerequisites ✅
```bash
# Check Python (needs 3.11+)
python3 --version

# Check pip
pip --version
```

### 2. Install Dependencies (2 min) 📦
```bash
# Install all required packages
pip install -r requirements_hf.txt
```

### 3. Configure API Keys (1 min) 🔑

Create `.env` file:
```bash
# Copy example
cp .env.example .env

# Add your keys (optional but recommended)
ALPHA_VANTAGE_API_KEY=40XS7GQ6AU9NB6Y4
MASSIVE_API_KEY=PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE
```

### 4. Verify Installation (30 sec) ✅
```bash
python3 verify_installation.py
```

Look for:
- ✅ All checks passed
- ✅ 305 resources loaded
- ✅ All pages updated

### 5. Start Application (10 sec) 🚀
```bash
uvicorn hf_space_api:app --reload --host 0.0.0.0 --port 7860
```

**Wait for:**
```
✅ Database tables created successfully
✅ Smart Data Collection Agent started
✅ Collecting from 305+ FREE resources
🚀 Application startup complete!
```

### 6. Test (30 sec) 🧪

Open browser: **http://localhost:7860**

You should see the beautiful landing page!

**Test API:**
```bash
# Health check
curl http://localhost:7860/api/smart/health-report

# Market data
curl http://localhost:7860/api/smart/market?limit=10

# System stats
curl http://localhost:7860/api/smart/stats
```

---

## 🎨 Available Pages

Once running, visit these pages:

| Page | URL | Description |
|------|-----|-------------|
| **Home** | http://localhost:7860 | Landing page |
| **Dashboard** | /static/pages/dashboard/index.html | Overview |
| **Market** | /static/pages/market/index.html | Live market data |
| **Trading** | /static/pages/trading-assistant/index.html | AI assistant |
| **News** | /static/pages/news/index.html | Crypto news |
| **Sentiment** | /static/pages/sentiment/index.html | AI sentiment |
| **API Explorer** | /static/pages/api-explorer/index.html | Test APIs |
| **Diagnostics** | /static/pages/diagnostics/index.html | System health |
| **API Docs** | /docs | FastAPI Swagger |

---

## 🔄 Smart Fallback in Action

The system automatically uses **305+ resources** with rotation:

```javascript
// In browser console (F12)
const client = window.apiClient;

// Get market data (tries 21 different APIs if needed)
const market = await client.getMarketData(100);
console.log(market);

// Get news (tries 15 different APIs if needed)
const news = await client.getNews(20);
console.log(news);

// Get sentiment
const sentiment = await client.getSentiment('bitcoin');
console.log(sentiment);
```

**Never returns 404!** ✅

---

## 🐳 Docker Quick Start

```bash
# Build
docker build -t crypto-hub .

# Run
docker run -p 7860:7860 \
  -e ALPHA_VANTAGE_API_KEY=40XS7GQ6AU9NB6Y4 \
  -e MASSIVE_API_KEY=PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE \
  crypto-hub

# Open browser
http://localhost:7860
```

---

## 🌐 HuggingFace Space Quick Deploy

```bash
# 1. Create Space on HuggingFace
# Go to: https://huggingface.co/new-space
# Select: Docker template

# 2. Add secrets in Space settings
HF_TOKEN = your_token
ALPHA_VANTAGE_API_KEY = 40XS7GQ6AU9NB6Y4
MASSIVE_API_KEY = PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE

# 3. Push code
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE
git push hf main

# 4. Wait for build (2-3 minutes)
# 5. Visit your space URL
```

---

## 🚨 Troubleshooting

### Application won't start
```bash
# Check Python version (must be 3.11+)
python3 --version

# Reinstall dependencies
pip install -r requirements_hf.txt --upgrade

# Check port availability
lsof -i :7860
```

### Dependencies not installing
```bash
# Update pip first
pip install --upgrade pip setuptools wheel

# Try again
pip install -r requirements_hf.txt
```

### No data from APIs
```bash
# Check API keys
cat .env

# Test providers
python3 test_new_apis.py

# Check health
curl http://localhost:7860/api/smart/health-report
```

### Pages not loading
```bash
# Update pages with API config
python3 UPDATE_ALL_PAGES.py

# Restart server
# Ctrl+C then restart
uvicorn hf_space_api:app --reload
```

### 404 Errors
```bash
# Use smart endpoints instead
curl http://localhost:7860/api/smart/market?limit=10

# These NEVER return 404!
```

---

## 📊 Verify Everything Works

### Run Complete Tests
```bash
# 1. Verification
python3 verify_installation.py

# 2. Routing test
python3 test_complete_routing.py

# 3. Provider test
python3 test_new_apis.py
```

### Check Health
```bash
# Get health report
curl http://localhost:7860/api/smart/health-report | jq

# Expected output:
# {
#   "total_resources": 305,
#   "available": 290+,
#   "failed": <10,
#   "categories": {...}
# }
```

### Check Stats
```bash
# Get system stats
curl http://localhost:7860/api/smart/stats | jq

# Expected output:
# {
#   "collection_stats": {
#     "successful_fetches": >0,
#     "failed_fetches": <10,
#     "total_fetches": >0
#   }
# }
```

---

## ✅ Success Checklist

- [ ] Python 3.11+ installed
- [ ] Dependencies installed
- [ ] Server starts without errors
- [ ] Browser shows landing page
- [ ] API returns data (test with curl)
- [ ] Pages load correctly
- [ ] No errors in console (F12)
- [ ] Health report shows 305 resources
- [ ] Background agent running (check logs)

---

## 📚 Next Steps

### Learn More
1. [Complete Routing Guide](COMPLETE_ROUTING_GUIDE.md)
2. [Installation Guide](INSTALLATION_GUIDE.md)
3. [Startup Checklist](STARTUP_CHECKLIST.md)
4. [Project Summary](PROJECT_COMPLETE_SUMMARY.md)

### Explore Features
1. Browse all pages
2. Test API Explorer
3. Check Diagnostics
4. View system health
5. Monitor resource rotation

### Deploy
1. Test locally first
2. Deploy to Docker (optional)
3. Deploy to HuggingFace Space
4. Share with users!

---

## 🎉 You're Ready!

If all checks pass, you have:

✅ **305+ Resources** working  
✅ **Smart Fallback** active  
✅ **Resource Rotation** enabled  
✅ **Zero 404s** guaranteed  
✅ **24/7 Data Collection** running  
✅ **Beautiful UI** ready  
✅ **Complete API** functional  

**Congratulations! 🎊**

---

## 💡 Pro Tips

1. **Use Smart Endpoints**
   - Always prefer `/api/smart/*`
   - They never fail
   - Automatic rotation

2. **Monitor Health**
   - Check `/api/smart/health-report` daily
   - Watch for failed resources
   - Clean up periodically

3. **Optimize Performance**
   - Enable caching (already done)
   - Use background collection (already running)
   - Monitor response times

4. **Keep Updated**
   - Update dependencies monthly
   - Add new resources as discovered
   - Review failed resources weekly

---

## 🆘 Need Help?

### Check Logs
```bash
# View logs
tail -f logs/hf_space_api.log

# Filter errors
grep ERROR logs/hf_space_api.log
```

### Common Issues
- **404**: Use `/api/smart/*` endpoints
- **Slow**: Check health report
- **Auth**: Set HF_TOKEN in .env
- **No Data**: Check API keys

### Documentation
- Full API docs: http://localhost:7860/docs
- ReDoc: http://localhost:7860/redoc
- Guides: See markdown files in project root

---

**Happy Coding! 🚀**

---

**Version**: 2.0.0  
**Last Updated**: December 5, 2025  
**Status**: ✅ Production Ready
