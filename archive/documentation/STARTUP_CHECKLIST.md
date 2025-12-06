# 🚀 Startup Checklist

Complete checklist before running the application.

## ✅ Pre-Installation

- [ ] Python 3.11+ installed
- [ ] pip updated (`pip install --upgrade pip`)
- [ ] Git installed
- [ ] Docker installed (for deployment)
- [ ] HuggingFace account created
- [ ] Minimum 4GB RAM available
- [ ] Minimum 10GB disk space

## ✅ Installation

- [ ] Repository cloned
- [ ] Dependencies installed (`pip install -r requirements_hf.txt`)
- [ ] Environment file created (`.env`)
- [ ] API keys configured:
  - [ ] ALPHA_VANTAGE_API_KEY=40XS7GQ6AU9NB6Y4
  - [ ] MASSIVE_API_KEY=PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE
  - [ ] HF_TOKEN (optional, for auth)
- [ ] Database directory created (`data/database/`)
- [ ] Logs directory created (`logs/`)

## ✅ Configuration

- [ ] All HTML pages updated with API config (`python3 UPDATE_ALL_PAGES.py`)
- [ ] Resources file validated (`cursor-instructions/consolidated_crypto_resources.json`)
- [ ] Static files accessible (`static/` directory)
- [ ] Pages directory accessible (`static/pages/`)
- [ ] JavaScript files present (`static/js/api-config.js`)
- [ ] CSS files present (`static/css/*.css`)

## ✅ Verification

Run verification script:

```bash
python3 verify_installation.py
```

Check for:
- [ ] All checks passed (0 failures)
- [ ] All warnings reviewed
- [ ] 305+ resources loaded
- [ ] All dependencies installed
- [ ] All required files present

## ✅ First Run

### Local Development

```bash
# Start server
uvicorn hf_space_api:app --reload --host 0.0.0.0 --port 7860

# Check startup logs for:
```

- [ ] ✅ Database tables created successfully
- [ ] ✅ Loaded X AI models successfully
- [ ] ✅ Market Data Worker started successfully
- [ ] ✅ OHLC Data Worker started successfully
- [ ] ✅ Comprehensive Data Worker started successfully
- [ ] ✅ Smart Data Collection Agent started
- [ ] ✅ Collecting from 305+ FREE resources
- [ ] ✅ Static files mounted at /static
- [ ] ✅ Alpha Vantage router loaded
- [ ] ✅ Massive.com router loaded
- [ ] ✅ Smart Fallback router loaded (305+ resources)
- [ ] 🚀 Application startup complete!

### Docker

```bash
# Build image
docker build -t crypto-intelligence-hub .

# Check build:
```

- [ ] Build completed successfully
- [ ] No errors in build logs
- [ ] Image size reasonable (<5GB)

```bash
# Run container
docker run -p 7860:7860 \
  -e ALPHA_VANTAGE_API_KEY=40XS7GQ6AU9NB6Y4 \
  -e MASSIVE_API_KEY=PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE \
  crypto-intelligence-hub

# Check logs:
```

- [ ] Container started
- [ ] All workers started
- [ ] No critical errors
- [ ] Server listening on 0.0.0.0:7860

## ✅ Testing

### API Endpoints

```bash
# Test root
curl http://localhost:7860/

# Test smart fallback
curl http://localhost:7860/api/smart/health-report

# Test market data
curl http://localhost:7860/api/smart/market?limit=10

# Test news
curl http://localhost:7860/api/smart/news?limit=5
```

- [ ] Root returns HTML or JSON
- [ ] Health report shows resource status
- [ ] Market data returns real data
- [ ] News returns real articles
- [ ] No 404 errors
- [ ] Response times < 5 seconds

### UI Pages

Open in browser: `http://localhost:7860`

- [ ] Main page loads
- [ ] Dashboard loads (`/static/pages/dashboard/index.html`)
- [ ] Market page loads and shows data
- [ ] Trading assistant loads
- [ ] Technical analysis loads
- [ ] News page loads and shows articles
- [ ] Sentiment page loads
- [ ] Models page shows status
- [ ] API Explorer works
- [ ] Diagnostics page works
- [ ] All pages have API client loaded
- [ ] No console errors (check browser console)

### Resource Rotation

```bash
# Get stats
curl http://localhost:7860/api/smart/stats
```

Check output:
- [ ] `total_resources` >= 305
- [ ] `available_resources` > 0
- [ ] `collection_stats.successful_fetches` > 0
- [ ] Multiple categories present

### Background Agent

Wait 2 minutes, then check:

```bash
# Get stats again
curl http://localhost:7860/api/smart/stats
```

- [ ] `successful_fetches` increased
- [ ] `last_collection` timestamp recent
- [ ] Agent still running (check logs)

## ✅ Production Deployment

### HuggingFace Space

- [ ] Space created on HuggingFace
- [ ] Secrets configured:
  - [ ] HF_TOKEN
  - [ ] ALPHA_VANTAGE_API_KEY
  - [ ] MASSIVE_API_KEY
- [ ] Code pushed to HF Space
- [ ] Build completed
- [ ] Space running
- [ ] Public URL accessible

### Post-Deployment

- [ ] Test public URL
- [ ] All pages accessible
- [ ] API endpoints work
- [ ] Resource rotation active
- [ ] No errors in HF logs
- [ ] Performance acceptable (<5s responses)
- [ ] Memory usage stable
- [ ] CPU usage reasonable

## ✅ Monitoring

### First Hour

- [ ] Check logs every 15 minutes
- [ ] Monitor resource health (`/api/smart/health-report`)
- [ ] Watch for errors
- [ ] Verify data collection
- [ ] Check memory usage
- [ ] Verify all pages working

### First Day

- [ ] Check logs 3-4 times
- [ ] Monitor system stats (`/api/smart/stats`)
- [ ] Verify background agent running
- [ ] Check database growth
- [ ] Monitor API rate limits
- [ ] Verify resource rotation
- [ ] Test from different locations

### First Week

- [ ] Daily health checks
- [ ] Review error logs
- [ ] Monitor resource failures
- [ ] Check cache hit rates
- [ ] Verify data freshness
- [ ] Test all features
- [ ] User feedback review

## ✅ Maintenance

### Daily

- [ ] Check health report
- [ ] Review error logs
- [ ] Monitor resource count
- [ ] Verify background agent

### Weekly

- [ ] Backup database
- [ ] Review failed resources
- [ ] Update resources if needed
- [ ] Check disk usage
- [ ] Review performance metrics
- [ ] Test new features

### Monthly

- [ ] Rotate API keys (if needed)
- [ ] Update dependencies
- [ ] Review and optimize caching
- [ ] Clean old logs
- [ ] Performance optimization
- [ ] Security audit

## 🚨 Troubleshooting

### Application won't start

1. Check Python version: `python3 --version`
2. Check dependencies: `pip list`
3. Check port: `lsof -i :7860`
4. Check logs: `tail -f logs/hf_space_api.log`

### No data from APIs

1. Check API keys in `.env`
2. Test providers: `python3 test_new_apis.py`
3. Check health: `curl http://localhost:7860/api/smart/health-report`
4. Review worker logs

### 404 Errors

1. Use smart endpoints: `/api/smart/*`
2. Check resource health
3. Verify background agent running
4. Check logs for errors

### High memory usage

1. Reduce workers: Use `--workers 1`
2. Check for memory leaks in logs
3. Restart application
4. Monitor with `htop`

### Slow responses

1. Check resource health
2. Review cache settings
3. Monitor API rate limits
4. Check network connectivity
5. Review background tasks

## 📚 Reference

- [Installation Guide](INSTALLATION_GUIDE.md)
- [Routing Guide](COMPLETE_ROUTING_GUIDE.md)
- [Smart Fallback System](SMART_FALLBACK_SYSTEM.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [API Documentation](DIRECT_API_DOCUMENTATION.md)

## 🎯 Quick Commands

```bash
# Verify installation
python3 verify_installation.py

# Update pages
python3 UPDATE_ALL_PAGES.py

# Start development server
uvicorn hf_space_api:app --reload

# Test routing
python3 test_complete_routing.py

# Test providers
python3 test_new_apis.py

# Check health
curl http://localhost:7860/api/smart/health-report | jq

# Check stats
curl http://localhost:7860/api/smart/stats | jq

# View logs
tail -f logs/hf_space_api.log

# Build Docker
docker build -t crypto-hub .

# Run Docker
docker run -p 7860:7860 crypto-hub
```

---

**Last Updated**: December 5, 2025
**Version**: 2.0.0
**Status**: ✅ Ready for Production

## 🎉 Next Steps

Once all checks pass:

1. ✅ Start the application
2. ✅ Open browser to http://localhost:7860
3. ✅ Test all pages and features
4. ✅ Deploy to HuggingFace Space
5. ✅ Monitor and enjoy!

**🚀 Happy Coding!**
