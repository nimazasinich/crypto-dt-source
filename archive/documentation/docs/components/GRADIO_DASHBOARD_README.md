# 🚀 Gradio Dashboard for Crypto Data Sources

## Overview

Comprehensive Gradio-based monitoring dashboard that provides real-time health checking, force testing, and auto-healing capabilities for all crypto data sources in the project.

## ✨ Features

### 1. **System Overview Dashboard**
- Real-time status of FastAPI backend
- HF Data Engine health monitoring
- Loaded resources statistics
- System uptime tracking

### 2. **Force Testing**
- Test ALL 200+ data sources with retries
- Detailed latency measurements
- Success/failure tracking
- Automatic retry on failures

### 3. **Resource Explorer**
- Browse all API resources
- Detailed configuration view
- Force test results per resource
- JSON configuration display

### 4. **FastAPI Endpoint Monitor**
- Test all backend endpoints
- Response time tracking
- Status code monitoring
- Automatic health checks

### 5. **HF Data Engine Monitor**
- Test OHLCV endpoints
- Price feed monitoring
- Sentiment analysis checks
- Cache statistics

### 6. **Custom API Testing**
- Test any URL with custom headers
- Configurable retry attempts
- Multiple HTTP methods (GET, POST, PUT, DELETE)
- Detailed response analysis

### 7. **Analytics Dashboard**
- Resource statistics by category
- Source file breakdowns
- Performance metrics
- Success rate tracking

### 8. **Auto-Healing**
- Automatic retry with different strategies
- Header modification attempts
- Timeout adjustments
- Redirect following

## 🚀 Quick Start

### Option 1: Using Startup Script

```bash
# Make script executable (first time only)
chmod +x start_gradio_dashboard.sh

# Start dashboard
./start_gradio_dashboard.sh
```

### Option 2: Manual Start

```bash
# Install requirements
pip install -r requirements_gradio.txt

# Start dashboard
python gradio_ultimate_dashboard.py
```

### Option 3: Direct Python

```bash
python3 gradio_ultimate_dashboard.py
```

## 🌐 Access

Once started, the dashboard is available at:

**URL:** http://localhost:7861

You can also access it from other devices on your network using your machine's IP address:

**Network URL:** http://YOUR_IP:7861

## 📊 Dashboard Tabs

### 🏠 Dashboard
- System overview
- Core systems status (FastAPI, HF Engine)
- Resource statistics
- Quick health summary

### 🧪 Force Test
- Comprehensive testing of ALL sources
- Multiple retry attempts per source
- Detailed success/failure tracking
- Performance metrics

**How to use:**
1. Click "⚡ START FORCE TEST" button
2. Wait for completion (may take 2-5 minutes for all sources)
3. Review results table
4. Check individual resource details

### 🔍 Resource Explorer
- Search and explore all API resources
- View complete configuration
- See force test results
- Analyze individual sources

**How to use:**
1. Select resource from dropdown
2. View detailed configuration
3. Check test results
4. Copy configuration if needed

### ⚡ FastAPI Status
- Monitor main backend server
- Test all API endpoints
- Check response times
- Verify functionality

**Tested Endpoints:**
- `/health` - Health check
- `/api/status` - System status
- `/api/providers` - Provider list
- `/api/pools` - Pool management
- `/api/hf/health` - HuggingFace health
- `/api/feature-flags` - Feature flags
- `/api/data/market` - Market data
- `/api/data/news` - News data

### 🤗 HF Data Engine
- Monitor HuggingFace Data Engine
- Test all data endpoints
- Check provider status
- Verify cache performance

**Tested Endpoints:**
- `/api/health` - Engine health
- `/api/prices` - Price data
- `/api/ohlcv` - Candlestick data
- `/api/sentiment` - Market sentiment
- `/api/market/overview` - Market overview
- `/api/cache/stats` - Cache statistics

### 🎯 Custom Test
- Test any API endpoint
- Custom headers support
- Configurable retries
- All HTTP methods

**Features:**
- URL input
- Method selection (GET, POST, PUT, DELETE)
- Custom headers (JSON format)
- Retry attempts (1-5)
- Detailed response display

### 📊 Analytics
- Comprehensive resource statistics
- Category breakdowns
- Source file analysis
- Performance metrics

## 🔧 Configuration

### Enable Auto-Heal
Toggle the "🔧 Enable Auto-Heal" checkbox at the top of the dashboard to enable automatic retry with different strategies when a source fails.

**Auto-Heal Strategies:**
1. Add custom headers (User-Agent, etc.)
2. Increase timeout duration
3. Follow redirects automatically

### Enable Real-Time Monitoring
Toggle "📡 Enable Real-Time Monitoring" to activate continuous background monitoring (coming in future update).

## 📁 Files

### Main Dashboard Files
- `gradio_ultimate_dashboard.py` - Advanced dashboard with all features
- `gradio_dashboard.py` - Basic dashboard (simpler version)

### Configuration
- `requirements_gradio.txt` - Python dependencies
- `start_gradio_dashboard.sh` - Startup script

### Data Sources
- `api-resources/crypto_resources_unified_2025-11-11.json` - Unified resources (200+ sources)
- `api-resources/ultimate_crypto_pipeline_2025_NZasinich.json` - Pipeline resources (162 sources)
- `all_apis_merged_2025.json` - Merged APIs
- `providers_config_extended.json` - Extended provider configs
- `providers_config_ultimate.json` - Ultimate provider configs

## 🧪 Testing Workflow

### Complete System Test

1. **Start All Services:**
   ```bash
   # Terminal 1: Main FastAPI backend
   python app.py

   # Terminal 2: HF Data Engine
   cd hf-data-engine && python main.py

   # Terminal 3: Gradio Dashboard
   ./start_gradio_dashboard.sh
   ```

2. **Verify Systems:**
   - Open dashboard: http://localhost:7861
   - Check Dashboard tab for system status
   - Verify both FastAPI and HF Engine show "✅ ONLINE"

3. **Run Force Test:**
   - Go to "🧪 Force Test" tab
   - Click "⚡ START FORCE TEST"
   - Wait for completion
   - Review results

4. **Test Individual Endpoints:**
   - Go to "⚡ FastAPI Status" tab
   - Click "🧪 Test All Endpoints"
   - Check all endpoints are working

5. **Test HF Engine:**
   - Go to "🤗 HF Data Engine" tab
   - Click "🧪 Test All Endpoints"
   - Verify data is returned

6. **Explore Resources:**
   - Go to "🔍 Resource Explorer" tab
   - Browse different data sources
   - View configurations

7. **Check Analytics:**
   - Go to "📊 Analytics" tab
   - Review statistics
   - Check resource distribution

## 🚨 Troubleshooting

### Dashboard won't start

**Problem:** Import errors

**Solution:**
```bash
pip install -r requirements_gradio.txt
```

### Can't connect to FastAPI/HF Engine

**Problem:** Services not running

**Solution:**
```bash
# Check if services are running
curl http://localhost:7860/health
curl http://localhost:8000/api/health

# Start if needed
python app.py  # FastAPI
cd hf-data-engine && python main.py  # HF Engine
```

### Force test shows all offline

**Problem:** Network/firewall issues or services not started

**Solution:**
1. Verify services are running (see above)
2. Check if you're behind a restrictive firewall
3. Try testing individual endpoints first
4. Enable auto-heal for retry attempts

### Slow performance

**Problem:** Testing too many sources

**Solution:**
- Test only specific categories instead of all
- Increase timeout values
- Test during off-peak hours
- Use caching for repeated tests

## 💡 Tips & Best Practices

### 1. Test Incrementally
Don't run force test on all sources at once during development. Start with:
- FastAPI endpoints only
- HF Engine endpoints only
- Small subset of resources

### 2. Use Auto-Heal Wisely
Enable auto-heal when testing external APIs that might have temporary issues. Disable for internal services.

### 3. Monitor Regularly
Schedule regular health checks:
- Every hour: FastAPI and HF Engine
- Every 6 hours: All external sources
- Daily: Full force test

### 4. Export Results
After force testing, export results for:
- Historical tracking
- Performance analysis
- Downtime investigation

### 5. Custom Testing
Use the custom test tab to:
- Debug specific endpoints
- Test new APIs before adding to system
- Verify authentication
- Test with different headers

## 📊 Metrics & KPIs

The dashboard tracks:

- **Uptime:** Percentage of time services are available
- **Response Time:** Average latency for requests
- **Success Rate:** Percentage of successful requests
- **Error Rate:** Percentage of failed requests
- **Resource Coverage:** Number of working vs total resources

## 🔄 Integration

### With Existing Systems

The dashboard integrates with:

1. **FastAPI Backend** (app.py)
   - Monitors all endpoints
   - Tests provider health
   - Checks feature flags

2. **HF Data Engine** (hf-data-engine/)
   - Tests all data endpoints
   - Monitors provider status
   - Checks cache performance

3. **API Resources** (api-resources/)
   - Loads all resource configurations
   - Tests each resource
   - Tracks availability

### API Endpoints Used

The dashboard calls these endpoints:

**FastAPI:**
- `GET /health`
- `GET /api/status`
- `GET /api/providers`
- `GET /api/hf/health`

**HF Engine:**
- `GET /api/health`
- `GET /api/prices`
- `GET /api/ohlcv`
- `GET /api/sentiment`

## 📈 Future Enhancements

Planned features:

- [ ] Real-time monitoring with auto-refresh
- [ ] Alert system for downtimes
- [ ] Historical data tracking
- [ ] Performance graphs and charts
- [ ] Email notifications
- [ ] Slack/Discord integration
- [ ] Automated daily reports
- [ ] Resource availability heatmap
- [ ] Comparative analytics
- [ ] Export to multiple formats (PDF, Excel)

## 🤝 Contributing

To add new features:

1. Fork the dashboard code
2. Add new tab or functionality
3. Test thoroughly
4. Submit pull request

## 📝 License

Same as main project

## 🙏 Acknowledgments

Built using:
- **Gradio** - UI framework
- **httpx** - HTTP client
- **pandas** - Data analysis
- **FastAPI** - Backend server

---

**Version:** 2.0
**Last Updated:** 2024-11-14
**Status:** ✅ Production Ready
