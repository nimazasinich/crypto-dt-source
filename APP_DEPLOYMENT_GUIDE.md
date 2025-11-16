# Crypto Admin Dashboard - Deployment Guide

## Overview

This is a **REAL-DATA-ONLY** Gradio admin dashboard for the Crypto Data Aggregator platform. It provides comprehensive monitoring and management capabilities through a clean web interface.

## Features

### 7 Main Tabs

1. **📊 Status** - System health overview, database stats, quick diagnostics
2. **🔌 Providers** - API provider management with filtering and reload
3. **📈 Market Data** - Live cryptocurrency prices, charts, and market data
4. **🔍 APL Scanner** - Auto Provider Loader for discovering and validating providers
5. **🤖 HF Models** - HuggingFace model status and testing interface
6. **🔧 Diagnostics** - Full system diagnostics with auto-repair capabilities
7. **📋 Logs** - System logs viewer with filtering

### Key Principles

- **NO MOCK DATA**: All data comes from real sources (database, APIs, files)
- **Real-time**: Live updates from actual collectors and services
- **Error Handling**: Graceful degradation with clear error messages
- **HuggingFace Ready**: Designed to run as a Gradio Space

## Installation

### Local Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Ensure database is initialized
python -c "import database; db = database.get_database()"

# 3. Run the app
python app.py
```

The dashboard will be available at: `http://localhost:7860`

### HuggingFace Space Deployment

1. Create a new Space on HuggingFace
2. Choose **Space SDK**: Gradio
3. Upload all necessary files:
   - `app.py` (main entrypoint)
   - `config.py`
   - `database.py`
   - `collectors.py`
   - `ai_models.py`
   - `auto_provider_loader.py`
   - `provider_validator.py`
   - `requirements.txt`
   - `providers_config_extended.json`
   - Backend services (if needed)

4. HuggingFace will automatically detect `app.py` and launch the Gradio app

## Data Sources

### Tab 1: Status
- **Database**: `db.get_database_stats()` - real-time DB metrics
- **Providers**: `providers_config_extended.json` - actual provider count
- **Market**: `db.get_latest_prices(3)` - live top 3 coins

### Tab 2: Providers
- **Source**: `providers_config_extended.json`
- **Categories**: Dynamically extracted from provider configs
- **Operations**: Real file reload, category filtering

### Tab 3: Market Data
- **Prices**: `db.get_latest_prices(100)` - real database records
- **Refresh**: `collectors.collect_price_data()` - live API calls to CoinGecko/CoinCap
- **Charts**: `db.get_price_history(symbol, hours)` - historical data from DB
- **Plotly**: Interactive charts with real price data

### Tab 4: APL Scanner
- **Scan**: `auto_provider_loader.AutoProviderLoader().run()` - actual APL execution
- **Results**: Real validation results from HTTP providers and HF models
- **Report**: Reads actual `PROVIDER_AUTO_DISCOVERY_REPORT.md`

### Tab 5: HF Models
- **Status**: `ai_models.get_model_info()` - real model loading status
- **Test**: `ai_models.analyze_sentiment()`, `ai_models.summarize_text()` - actual HF inference
- **Initialize**: `ai_models.initialize_models()` - loads real transformers models

### Tab 6: Diagnostics
- **Run**: `backend.services.diagnostics_service.DiagnosticsService().run_full_diagnostics()`
- **Checks**: Real dependency checks, network tests, file system validation
- **Auto-fix**: Actually installs packages, creates directories

### Tab 7: Logs
- **Source**: `config.LOG_FILE` - actual log file
- **Filters**: Real-time filtering of ERROR/WARNING/INFO
- **Clear**: Actually clears log file (with backup)

## Testing Checklist

### ✅ Pre-Flight Checks

```bash
# 1. Verify Python version
python --version  # Should be 3.10+

# 2. Install dependencies
pip install -r requirements.txt

# 3. Check database exists
ls -lh data/database/crypto_aggregator.db

# 4. Check config files
ls -lh providers_config_extended.json
ls -lh config.py
```

### ✅ Tab-by-Tab Testing

#### Tab 1: Status
- [ ] Click "Refresh Status" - should show real DB stats
- [ ] Click "Run Quick Diagnostics" - should show actual issues (if any)
- [ ] Verify market snapshot shows real BTC/ETH/BNB prices (if available)
- [ ] Check database stats JSON shows actual record counts

#### Tab 2: Providers
- [ ] View providers table - should load from JSON file
- [ ] Change category filter - should filter providers
- [ ] Click "Reload Providers" - should show success message
- [ ] Verify provider count matches file

#### Tab 3: Market Data
- [ ] View market data table - should show real prices from DB
- [ ] Enter search term (e.g., "Bitcoin") - should filter results
- [ ] Click "Refresh Prices" - should collect new data from APIs
- [ ] Enter symbol "BTC" and click "Plot" - should show price chart (if Plotly installed)
- [ ] Verify no mock/hardcoded data

#### Tab 4: APL Scanner
- [ ] View last report - should show previous scan or "no report"
- [ ] Click "Run APL Scan" - **WARNING: This runs a full scan**
  - Should validate HTTP providers
  - Should check HF models
  - Should update `providers_config_extended.json`
- [ ] Click "View Last Report" - should show markdown report

#### Tab 5: HF Models
- [ ] View models table - should show configured models
- [ ] Click "Initialize Models" - should load transformers (if installed)
- [ ] Select "sentiment", enter text "Bitcoin is great!", click "Run Test"
  - Should show real sentiment analysis results
- [ ] Try "summarization" with longer text

#### Tab 6: Diagnostics
- [ ] Click "Run Diagnostics" - should check:
  - Dependencies (Python packages)
  - Configuration (env vars, files)
  - Network (API connectivity)
  - Services (provider status)
  - Models (HF model availability)
  - Filesystem (directories, files)
- [ ] Click "Run with Auto-Fix" - **WARNING: May install packages**
  - Should attempt to fix issues automatically

#### Tab 7: Logs
- [ ] Select "recent" - should show last 100 log lines
- [ ] Select "errors" - should show only ERROR lines
- [ ] Click "Refresh Logs" - should update display
- [ ] Click "Clear Logs" - **WARNING: Clears log file**
  - Should create backup first

### ✅ Error Handling Tests

```python
# Test with no data
# 1. Empty database
python -c "import database; db = database.get_database(); import os; os.remove(str(db.db_path))"

# 2. Run app - should show "No data available" messages, not crash

# Test with missing config
# 1. Rename providers config
mv providers_config_extended.json providers_config_extended.json.bak

# 2. Run app - should show error messages, not crash

# Test with no internet
# 1. Disconnect network
# 2. Click "Refresh Prices" - should show connection errors, not crash
```

## Configuration

### Environment Variables

Optional environment variables for enhanced functionality:

```bash
# HuggingFace API token (for model access)
export HF_TOKEN="your_hf_token_here"

# API keys (optional)
export CMC_API_KEY="your_coinmarketcap_key"
export ETHERSCAN_KEY="your_etherscan_key"
```

### Config.py Settings

Key settings in `config.py`:

```python
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
AUTO_REFRESH_INTERVAL = 30  # seconds
GRADIO_SERVER_NAME = "0.0.0.0"
GRADIO_SERVER_PORT = 7860
```

## Troubleshooting

### Issue: "gradio not installed"
```bash
pip install gradio
```

### Issue: "No market data available"
```bash
# Collect initial data
python -c "import collectors; collectors.collect_price_data()"
```

### Issue: "Plotly not available"
```bash
pip install plotly
# Charts will work after restart
```

### Issue: "Transformers not available"
```bash
pip install transformers torch
# HF model features will work after restart
```

### Issue: "Log file not found"
```bash
# Ensure logs directory exists
mkdir -p logs
# Run any collector to create log
python -c "import collectors; collectors.collect_price_data()"
```

## Performance Notes

- **Initial Load**: First load may be slow as models initialize
- **APL Scan**: Can take 30-60 seconds to validate all providers
- **Diagnostics**: Full scan takes ~5-10 seconds
- **Charts**: Rendering large datasets may take a few seconds

## Security Notes

- **Database Queries**: Only SELECT queries allowed in DB Explorer
- **Log Clearing**: Creates backup before clearing
- **Auto-Fix**: Only installs packages and creates directories
- **No Shell Access**: No direct shell command execution

## Development

### Adding New Tabs

```python
with gr.Tab("🆕 New Tab"):
    gr.Markdown("### New Feature")
    
    # Your components here
    output = gr.Markdown()
    
    def new_function():
        # MUST use real data only
        return "Real data result"
    
    demo.load(
        fn=new_function,
        outputs=output
    )
```

### Adding New Data Sources

1. Add function to fetch real data (no mock data!)
2. Wire function to Gradio component
3. Add error handling
4. Test with missing/unavailable data

## License

Part of the Crypto Data Aggregator project.

---

**Last Updated**: 2025-11-16
**Version**: 1.0.0
**Maintainer**: Crypto DT Source Team
