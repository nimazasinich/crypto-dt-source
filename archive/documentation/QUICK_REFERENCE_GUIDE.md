# Quick Reference Guide: Crypto-DT-Source Implementation

**Quick lookup for common tasks during implementation**

---

## 🚀 Start Here

### Launch Development Server
```bash
cd /home/user/crypto-dt-source
python api_server_extended.py
# Opens on http://localhost:8000
```

### Access Documentation
```
Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/api/health | jq

# Real-time prices
curl 'http://localhost:8000/api/prices?symbols=BTC,ETH' | jq

# Trending coins
curl http://localhost:8000/api/trending | jq

# Sentiment analysis
curl -X POST http://localhost:8000/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Bitcoin price is going up"}'
```

---

## 📁 Key Files to Modify

### API Endpoints
- **`api_server_extended.py`** - Main FastAPI application + all endpoints
- **`api/endpoints.py`** - Additional endpoint definitions
- **`api/websocket.py`** - WebSocket handling

### Data Collection
- **`collectors/market_data_extended.py`** - Price data fetching
- **`collectors/sentiment_extended.py`** - Sentiment analysis
- **`collectors/news.py`** - News aggregation

### Database
- **`database/db_manager.py`** - Database connection
- **`database/models.py`** - Table definitions
- **`database/migrations.py`** - Schema setup

### AI Models
- **`ai_models.py`** - HuggingFace model loading

### Utilities
- **`utils/auth.py`** - Authentication
- **`utils/rate_limiter_enhanced.py`** - Rate limiting
- **`log_manager.py`** - Logging

---

## 💻 Common Commands

### Database Operations
```bash
# Initialize database
python -c "from database.db_manager import DBManager; \
  import asyncio; \
  asyncio.run(DBManager().initialize())"

# Check database
sqlite3 data/crypto_aggregator.db ".tables"

# Backup database
cp data/crypto_aggregator.db data/crypto_aggregator.db.backup

# Clear old data (keep 90 days)
sqlite3 data/crypto_aggregator.db \
  "DELETE FROM prices WHERE timestamp < datetime('now', '-90 days')"
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env

# Essential variables:
PORT=8000
JWT_SECRET_KEY=your-secret-key
ENABLE_AUTO_DISCOVERY=true
ENABLE_SENTIMENT_ANALYSIS=true
ENABLE_BACKGROUND_TASKS=true
DATABASE_URL=sqlite:///data/crypto_aggregator.db
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest --cov=.

# Test specific endpoint
pytest tests/ -k "test_prices"
```

### Deployment
```bash
# Build Docker image
docker build -t crypto-dt-source .

# Run Docker container
docker run -p 8000:8000 crypto-dt-source

# Push to HuggingFace Spaces
git remote add spaces https://huggingface.co/spaces/your-username/crypto-dt-source
git push spaces main
```

---

## 🔑 Configuration Quick Reference

### Rate Limiting Tiers
```python
# In .env or code
FREE_TIER_LIMIT = "30/minute"      # 30 req/min, 1000/day
PRO_TIER_LIMIT = "300/minute"      # 300 req/min, 50000/day
ADMIN_TIER = None                  # Unlimited
```

### Cache TTLs
```python
CACHE_TTL = {
    "prices": 300,          # 5 minutes
    "ohlcv": 900,           # 15 minutes
    "defi": 3600,           # 1 hour
    "trending": 600,        # 10 minutes
    "news": 1800,           # 30 minutes
}
```

### Background Task Schedules
```python
SCHEDULE = {
    "collect_prices": "*/5 * * * *",      # Every 5 min
    "fetch_news": "*/30 * * * *",         # Every 30 min
    "analyze_sentiment": "0 * * * *",     # Hourly
    "collect_defi": "0 */4 * * *",        # Every 4 hours
    "health_check": "*/5 * * * *",        # Every 5 min
    "backup_database": "0 2 * * *",       # Daily 2 AM
    "cleanup_logs": "0 3 * * *",          # Daily 3 AM
}
```

---

## 🐛 Debugging

### View Logs
```bash
# Recent logs
tail -f logs/app.log

# Specific log level
grep "ERROR" logs/app.log

# By provider
grep "coingecko" logs/app.log

# Tail real-time
tail -f logs/*.log | grep ERROR
```

### API Diagnostics
```bash
# Full diagnostic report
curl http://localhost:8000/api/diagnostics/run?auto_fix=false | jq

# Provider status
curl http://localhost:8000/api/providers | jq '.[] | {name, status}'

# System metrics
curl http://localhost:8000/api/metrics | jq

# WebSocket sessions
curl http://localhost:8000/api/sessions | jq
```

### Database Inspection
```bash
# Open database
sqlite3 data/crypto_aggregator.db

# View schema
.schema

# Check table sizes
SELECT name, COUNT(*) as rows FROM sqlite_master
WHERE type='table' GROUP BY name;

# View recent prices
SELECT * FROM prices ORDER BY timestamp DESC LIMIT 10;

# View sentiment scores
SELECT * FROM news ORDER BY timestamp DESC LIMIT 5;
```

---

## ✅ Pre-Deployment Checklist

```
FUNCTIONALITY
[ ] All 50+ endpoints return real data (not mock)
[ ] Database storing all collected data
[ ] Sentiment analysis works with HuggingFace models
[ ] WebSocket streaming real-time updates
[ ] Background tasks running continuously

CONFIGURATION
[ ] .env file configured correctly
[ ] JWT_SECRET_KEY set to secure value
[ ] Rate limits configured for tiers
[ ] Cache TTLs optimized
[ ] Database path valid

SECURITY
[ ] Authentication required on protected endpoints
[ ] Rate limiting enforced
[ ] API key validation working
[ ] No hardcoded secrets in code
[ ] HTTPS configured (for production)

PERFORMANCE
[ ] API response time < 500ms
[ ] Sentiment analysis < 2s
[ ] WebSocket latency < 1s
[ ] Database queries < 100ms
[ ] Memory usage < 1GB
[ ] CPU usage < 50%

TESTING
[ ] All unit tests pass
[ ] Integration tests pass
[ ] Manual endpoint testing successful
[ ] Load testing acceptable (100+ req/s)
[ ] WebSocket tested with multiple clients

DEPLOYMENT
[ ] Docker builds successfully
[ ] Container runs without errors
[ ] Health check endpoint returns OK
[ ] All endpoints accessible
[ ] Logs writing correctly
[ ] Database initializing
[ ] Background tasks started
```

---

## 🆘 Common Issues & Solutions

### Issue: Models not loading
```
Error: RuntimeError: Unable to load model
Solution:
  1. Check torch/transformers installed: pip list | grep torch
  2. Check disk space: df -h
  3. Try smaller model: distilbert instead of bert
  4. Check HF token: huggingface-cli login
```

### Issue: Database locked
```
Error: sqlite3.OperationalError: database is locked
Solution:
  1. Restart server
  2. Close other connections
  3. Use WAL mode: PRAGMA journal_mode=WAL;
```

### Issue: Rate limit too strict
```
Error: 429 Too Many Requests
Solution:
  1. Check tier: GET /api/sessions/stats
  2. Increase limit: FREE_TIER_LIMIT=50/minute
  3. Get API key: POST /api/auth/token
```

### Issue: WebSocket not updating
```
Error: No new messages in WebSocket
Solution:
  1. Check background tasks: curl /api/health
  2. Verify WebSocket connection: ws://localhost:8000/ws
  3. Check logs: tail -f logs/app.log
```

### Issue: Sentiment analysis fails
```
Error: Model not found or OutOfMemory
Solution:
  1. Check available memory: free -h
  2. Reduce batch size in sentiment pipeline
  3. Use quantized model (smaller)
  4. Disable sentiment: ENABLE_SENTIMENT_ANALYSIS=false
```

### Issue: High memory usage
```
Error: Server crashes with OutOfMemory
Solution:
  1. Reduce cache size
  2. Implement memory limits
  3. Reduce WebSocket connection limit
  4. Archive old database entries
  5. Use lighter models
```

---

## 📊 Monitoring Commands

### System Health
```bash
# One-liner health check
curl http://localhost:8000/api/health | jq '.components | to_entries[] | "\(.key): \(.value.status)"'

# Monitor in real-time
watch -n 5 'curl -s http://localhost:8000/api/metrics | jq "."'

# Provider status
watch -n 10 'curl -s http://localhost:8000/api/providers | jq ".[] | {name, status, health_score}"'
```

### Performance Monitoring
```bash
# Response times
curl -w "\nTime: %{time_total}s\n" http://localhost:8000/api/prices

# Concurrent connections
curl http://localhost:8000/api/sessions/stats | jq '.total_connections'

# Database size
du -h data/crypto_aggregator.db

# Log file size
du -h logs/
```

### Continuous Monitoring
```bash
# Dashboard-style monitoring
while true; do
    echo "=== System Status ==="
    curl -s http://localhost:8000/api/health | jq .status
    echo "=== Active Connections ==="
    curl -s http://localhost:8000/api/sessions/stats | jq .total_connections
    echo "=== Provider Status ==="
    curl -s http://localhost:8000/api/stats | jq '{online, offline, degraded}'
    sleep 5
done
```

---

## 📚 Reference Links

### Code References
- **API Endpoints:** `api_server_extended.py:1-100`
- **Provider Manager:** `provider_manager.py` (global instance)
- **Database Setup:** `database/db_manager.py:50-150`
- **Sentiment Analysis:** `ai_models.py:200-300`
- **WebSocket Handling:** `api_server_extended.py:WebSocket endpoint`

### Documentation
- Deployment Guide: `HUGGINGFACE_DEPLOYMENT_PROMPT.md`
- Implementation Timeline: `IMPLEMENTATION_ROADMAP.md`
- Audit Report: See audit in conversation history

### External Resources
- CoinGecko API: https://docs.coingecko.com/
- Binance API: https://binance-docs.github.io/
- HuggingFace Models: https://huggingface.co/models
- FastAPI Documentation: https://fastapi.tiangolo.com/

---

## 🎯 Next Steps

1. **Review** `HUGGINGFACE_DEPLOYMENT_PROMPT.md` (comprehensive guide)
2. **Follow** `IMPLEMENTATION_ROADMAP.md` (step-by-step timeline)
3. **Use** this guide for quick lookup during implementation
4. **Track** progress with provided checklist
5. **Test** each phase before moving to next
6. **Deploy** to HF Spaces when all items completed

---

**Last Updated:** 2025-11-15
**Version:** 1.0
**Quick Questions?** Check this guide first!
