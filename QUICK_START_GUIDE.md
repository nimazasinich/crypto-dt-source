# Quick Start Guide - Backend Stability Features

## 🚀 Getting Started

### 1. Start the Server
```bash
python run_server.py
```

### 2. Run Tests
```bash
python test_backend_stability.py
```

### 3. View System Monitor
Open your browser to:
```
http://localhost:7860/system-monitor
```

## 📊 Dashboard URLs

| Feature | URL |
|---------|-----|
| Main Dashboard | http://localhost:7860/ |
| System Monitor | http://localhost:7860/system-monitor |
| API Docs | http://localhost:7860/docs |
| Source Health | http://localhost:7860/api/source-health/status |
| Config Status | http://localhost:7860/api/config/features |

## 🔧 API Testing

### Test Source Health
```bash
curl http://localhost:7860/api/source-health/status | jq
```

### Test Configuration
```bash
curl http://localhost:7860/api/config/features | jq
```

### Test Missing Variables
```bash
curl http://localhost:7860/api/config/missing | jq
```

### Test System Status
```bash
curl http://localhost:7860/api/status | jq
```

## 🎯 Key Features

### 1. Safe HTTP Client
```python
from backend.core.safe_http_client import SafeHTTPClient

client = SafeHTTPClient(
    source_name="my_api",
    base_url="https://api.example.com",
    timeout=15.0
)

# Automatically validates:
# - HTTP status (only 200 accepted)
# - Content-Type (application/json)
# - Empty responses rejected
# - JSON parsing safe
data = await client.get("/endpoint", params={"key": "value"})
```

### 2. Health Tracking
```python
from backend.core.safe_http_client import health_tracker

# Check if source should be used
should_use, reason = health_tracker.should_use_source("my_api")

if should_use:
    # Make request
    pass
else:
    # Use fallback
    logger.warning(f"Skipping my_api: {reason}")
```

### 3. Environment Configuration
```python
from backend.core.env_config import is_feature_enabled, get_config

# Check if feature is enabled
if is_feature_enabled("ETHERSCAN"):
    api_key = get_config("ETHERSCAN_KEYS")[0]
    # Use API
else:
    # Feature disabled - missing API key
    logger.warning("Etherscan disabled")
```

### 4. System Status Widget
```html
<!-- Add to any page -->
<script src="/static/shared/components/system-status-modal.html"></script>
```

## 📝 Environment Setup

### Required Variables (see .env.example)
```bash
# Market Data
COINMARKETCAP_KEY_1=your_key_here
CRYPTOCOMPARE_KEY=your_key_here

# Blockchain
ETHERSCAN_KEY_1=your_key_here
BSCSCAN_KEY=your_key_here

# HuggingFace
HF_TOKEN=your_token_here
```

### Optional Variables
All other variables in `.env.example` are optional. Missing variables will:
1. Log a warning
2. Disable only the affected feature
3. System continues running normally

## 🔍 Monitoring

### Real-Time Dashboard
- Server load, requests/min
- Database usage, queries/sec
- AI models (total, active)
- Data sources (healthy, degraded, offline)
- Network visualization
- Activity log

### Health Metrics
- Source health status
- Success/failure rates
- Response times
- Consecutive failures
- Recovery tracking

### Configuration Status
- Enabled features
- Disabled features
- Missing variables
- Per-feature configuration

## ⚠️ Troubleshooting

### Server won't start
```bash
# Check dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+

# Check for port conflicts
lsof -i :7860
```

### API endpoints return 503
```bash
# Check source health
curl http://localhost:7860/api/source-health/status

# Reset unhealthy source
curl -X POST http://localhost:7860/api/source-health/reset/source_name
```

### Missing API keys
```bash
# Check what's missing
curl http://localhost:7860/api/config/missing

# Set in .env file
echo "ETHERSCAN_KEY_1=your_key" >> .env

# Reload config
curl -X POST http://localhost:7860/api/config/reload
```

## 🎨 UI Components

### System Status Widget
- Compact: Bottom-right floating widget
- Expandable: Click to see full status
- Auto-refresh: Every 10 seconds
- Color-coded: Green/Yellow/Red

### System Monitor Dashboard
- Network visualization
- Real-time stats
- Activity log
- Service health
- Source health breakdown

## 📚 Documentation

- **Full Implementation**: See `BACKEND_STABILITY_COMPLETE.md`
- **API Reference**: http://localhost:7860/docs
- **Code Examples**: Check `test_backend_stability.py`

## ✅ Verification Checklist

- [ ] Server starts without errors
- [ ] System monitor loads at /system-monitor
- [ ] Real data appears (not "Loading...")
- [ ] Browser console is clean (no warnings)
- [ ] API endpoints return 200 status
- [ ] Source health tracking works
- [ ] Configuration status shows features
- [ ] Status widget appears on pages

## 🎉 Success Indicators

When everything works:
- ✅ Green status indicators
- ✅ Real-time data updates
- ✅ No console errors
- ✅ Health tracking active
- ✅ Smart routing working
- ✅ All features operational

---

**System is READY!** 🚀

For detailed documentation, see `BACKEND_STABILITY_COMPLETE.md`
