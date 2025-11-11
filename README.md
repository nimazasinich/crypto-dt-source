---
title: Crypto API Monitor Backend
emoji: 📊
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Crypto API Monitoring System

A comprehensive, production-ready backend system for monitoring cryptocurrency API health, tracking rate limits, collecting market data, and providing real-time status updates.

## Features

### Real-Time API Health Monitoring
- **Automated Health Checks**: Monitors 9+ cryptocurrency APIs every 5 minutes
- **Smart Status Detection**: Online/Degraded/Offline status based on response times and error rates
- **Failure Tracking**: Detailed logging of all failures with root cause analysis
- **Consecutive Failure Detection**: Automatic offline marking after 3+ failures

### Data Collection
- **Market Data**: CoinGecko, CoinMarketCap, CryptoCompare, Binance
- **Blockchain Explorers**: Etherscan, BscScan, TronScan
- **News**: CryptoPanic, NewsAPI
- **Sentiment**: Alternative.me Fear & Greed Index
- **On-Chain Analytics**: Placeholder support for The Graph, Blockchair, Glassnode

### Rate Limit Management
- **Per-Provider Tracking**: Monitors usage against limits (per_second, per_minute, per_hour, per_day)
- **Auto-Reset**: Automatic counter reset based on limit period
- **Warnings**: Alerts when usage reaches 80%
- **Blocking**: Prevents requests when limit reached

### Schedule Compliance
- **Configurable Schedules**: Different intervals per provider category
  - Market Data: Every 1 minute
  - Explorers: Every 5 minutes
  - News: Every 10 minutes
  - Sentiment: Every 15 minutes
- **Compliance Tracking**: Monitors on-time vs late execution
- **Skip Reasons**: Logs why tasks were skipped (rate limit, provider offline, etc.)

### Data Freshness Validation
- **Timestamp Extraction**: Reads data timestamps from API responses
- **Staleness Calculation**: Measures age in minutes
- **TTL-Based Status**: Fresh/Aging/Stale based on category-specific TTLs
- **Alerts**: Notifications when data is stale despite on-schedule fetching

## API Endpoints

### System Status
- `GET /api/status` - Overall system health
- `GET /api/categories` - Statistics by category
- `GET /api/providers` - List all providers with filtering

### Logs & Analytics
- `GET /api/logs` - Connection logs with pagination
- `GET /api/failures` - Failure analysis with remediation suggestions
- `GET /api/freshness` - Data freshness metrics

### Scheduler
- `GET /api/schedule` - Schedule status and compliance
- `POST /api/schedule/trigger` - Trigger immediate health check

### Rate Limits
- `GET /api/rate-limits` - Current rate limit status for all providers

### Configuration
- `GET /api/config/keys` - API key status (masked)
- `POST /api/config/keys/test` - Test API key validity

### Charts Data
- `GET /api/charts/health-history` - Time series for charts
- `GET /api/charts/compliance` - Compliance trends

## WebSocket Support

Real-time updates at `ws://localhost:7860/ws/live`

### Message Types
- `status_update` - System status every 10 seconds
- `new_log_entry` - Real-time log notifications
- `rate_limit_alert` - Warnings when usage ≥80%
- `provider_status_change` - Provider status changes
- `ping` - Heartbeat every 30 seconds

## Architecture

```
crypto-dt-source/
├── app.py                      # Main FastAPI application
├── config.py                   # Configuration loader
├── monitoring/
│   ├── health_checker.py       # API health monitoring
│   ├── rate_limiter.py         # Rate limit tracking
│   └── scheduler.py            # Task scheduling
├── database/
│   ├── models.py               # SQLAlchemy models
│   └── db_manager.py           # Database operations
├── collectors/
│   ├── market_data.py          # Market data collection
│   ├── explorers.py            # Blockchain explorer data
│   ├── news.py                 # News aggregation
│   ├── sentiment.py            # Sentiment data
│   └── onchain.py              # On-chain analytics
├── api/
│   ├── endpoints.py            # REST API endpoints
│   └── websocket.py            # WebSocket support
└── utils/
    ├── logger.py               # Structured JSON logging
    └── api_client.py           # HTTP client with retry logic
```

## Database Schema

SQLite database at `data/api_monitor.db` with tables:
- **providers** - API provider configurations
- **connection_attempts** - All health check attempts
- **data_collections** - Data collection logs
- **rate_limit_usage** - Rate limit snapshots
- **schedule_config** - Schedule configurations
- **schedule_compliance** - Schedule execution tracking
- **failure_logs** - Detailed failure logs
- **alerts** - System alerts
- **system_metrics** - System-wide metrics

## Environment Variables

Configure API keys via environment variables:

```bash
# Blockchain Explorers
export ETHERSCAN_KEY_1="your_key"
export ETHERSCAN_KEY_2="your_backup_key"
export BSCSCAN_KEY="your_key"
export TRONSCAN_KEY="your_key"

# Market Data
export COINMARKETCAP_KEY_1="your_key"
export COINMARKETCAP_KEY_2="your_backup_key"
export CRYPTOCOMPARE_KEY="your_key"

# News
export NEWSAPI_KEY="your_key"

# Optional
export HUGGINGFACE_KEY="your_key"
```

## Quick Start

### Local Development

```bash
# Clone repository
git clone <repository_url>
cd crypto-dt-source

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
cp .env.example .env
# Edit .env with your API keys

# Run the application
python app.py
```

The application will start on http://localhost:7860

### Docker Deployment

```bash
# Build image
docker build -t crypto-api-monitor .

# Run container
docker run -p 7860:7860 \
  -e ETHERSCAN_KEY_1="your_key" \
  -e COINMARKETCAP_KEY_1="your_key" \
  crypto-api-monitor
```

### Hugging Face Spaces

This app is configured for Hugging Face Spaces deployment:
1. Fork/upload this repository to Hugging Face
2. Set environment variables in Space settings
3. The app will auto-deploy with Docker SDK

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:7860/docs
- **ReDoc**: http://localhost:7860/redoc

## Tech Stack

- **FastAPI** - Modern async web framework
- **SQLAlchemy** - Database ORM
- **APScheduler** - Task scheduling
- **aiohttp** - Async HTTP client
- **WebSockets** - Real-time communication
- **SQLite** - Embedded database

## Features Breakdown

### Health Checking (every 5 minutes)
- CoinGecko: `GET /api/v3/ping`
- CoinMarketCap: `GET /v1/cryptocurrency/map?limit=1`
- Etherscan: `GET /api?module=stats&action=ethsupply`
- BscScan: `GET /api?module=stats&action=bnbsupply`
- TronScan: `GET /api/system/status`
- CryptoPanic: `GET /v1/posts/?auth_token=free`
- Alternative.me: `GET /fng/`
- NewsAPI: `GET /news?category=business`
- CryptoCompare: `GET /data/price?fsym=BTC&tsyms=USD`

### Data Collection Schedules
- **Market Data** (1 min): Price updates for BTC, ETH, BNB
- **Explorers** (5 min): Gas prices, network stats
- **News** (10 min): Latest crypto news posts
- **Sentiment** (15 min): Fear & Greed Index

### Failure Analysis
- Error type distribution (timeout, rate_limit, server_error, auth_error)
- Top 10 failing providers
- Recent failure log with retry results
- Intelligent remediation suggestions

### Retry Logic
- **Timeout**: Retry with timeout +50%, max 3 attempts
- **Rate Limit**: Wait until reset_time + 10s buffer
- **5xx Errors**: Exponential backoff (1min, 2min, 4min), max 5 attempts
- **401 Auth**: No retry, log key_expired alert

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or pull request.

## Monitoring

The system provides comprehensive monitoring:
- Response times in milliseconds
- Success/failure rates
- Rate limit usage percentages
- Data staleness metrics
- Schedule compliance percentages
- System health scores

## Support

For issues, please open a GitHub issue or contact the maintainers.
