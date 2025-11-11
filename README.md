---
title: Crypto API Monitor - Vidya UI
emoji: 📊
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 📊 Cryptocurrency API Monitor - Vidya Dashboard

> **Production-ready real-time cryptocurrency API monitoring with beautiful Vidya HTML UI**

A comprehensive monitoring system that tracks the health, performance, and availability of 162+ cryptocurrency APIs including market data, blockchain explorers, RPC nodes, news sources, sentiment analyzers, and more. Features a stunning real-time dashboard with WebSocket support.

## 🌟 Features

### Beautiful Vidya HTML UI
- **Modern Design**: Gradient-based UI with smooth animations and transitions
- **Real-time Updates**: WebSocket-powered live data streaming
- **Interactive Dashboard**: KPI cards, charts, and data visualizations
- **Multiple Views**: Dashboard, Inventory, Logs, Analytics, and HuggingFace Integration
- **Responsive**: Works perfectly on desktop, tablet, and mobile devices

### Core Capabilities
- **Real-Time Monitoring**: Track 162+ API endpoints with live status updates
- **WebSocket Streaming**: Real-time data feeds for all services
- **Multi-Category Support**: Market Data, Blockchain Explorers, RPC Nodes, News, Sentiment, On-chain Analytics
- **Health Tracking**: Response times, uptime percentages, failure detection
- **Rate Limit Management**: Automatic rate limiting with configurable rules
- **Database Persistence**: SQLite-based historical data storage
- **Automated Scheduling**: Background tasks for continuous monitoring
- **Alert System**: Real-time alerts for critical failures
- **HuggingFace Integration**: AI/ML capabilities with sentiment analysis

### WebSocket Services
The application provides comprehensive WebSocket APIs for real-time streaming:

#### Data Collection Streams
- `/ws/market_data` - Live market data updates
- `/ws/news` - Real-time crypto news feed
- `/ws/sentiment` - Sentiment analysis stream
- `/ws/whale_tracking` - Whale transaction alerts
- `/ws/data` - Unified data collection stream

#### Monitoring Streams
- `/ws/health` - System health status
- `/ws/pool_status` - Pool management updates
- `/ws/scheduler_status` - Scheduler activity
- `/ws/monitoring` - Unified monitoring stream

#### Integration Streams
- `/ws/huggingface` - HuggingFace AI/ML integration
- `/ws/ai` - AI services stream
- `/ws/persistence` - Persistence service updates
- `/ws/integration` - Unified integration stream

#### Master Streams
- `/ws` or `/ws/master` - All services combined
- `/ws/live` - Legacy live updates (compatible with older clients)

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

## 🚀 Quick Start

### Hugging Face Spaces Deployment (Recommended)

This application is configured for **Docker SDK** deployment on Hugging Face Spaces:

1. **Create a new Space** on [Hugging Face](https://huggingface.co/spaces)
2. **Select SDK**: Choose "Docker" as the SDK
3. **Link Repository**: Connect this GitHub repository
4. **Configure Secrets** (Optional - for API keys):
   ```
   ETHERSCAN_KEY
   BSCSCAN_KEY
   TRONSCAN_KEY
   CMC_KEY
   CRYPTOCOMPARE_KEY
   NEWSAPI_KEY
   INFURA_KEY
   ALCHEMY_KEY
   ```
5. **Deploy**: Push to your repository - auto-deploy triggers!

The application will be available at `https://YOUR_USERNAME-SPACE_NAME.hf.space`

### Local Development

```bash
# Clone repository
git clone https://github.com/nimazasinich/crypto-dt-source.git
cd crypto-dt-source

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Visit `http://localhost:7860` to access the Vidya dashboard.

### Docker Deployment

```bash
# Build image
docker build -t crypto-api-monitor .

# Run container
docker run -p 7860:7860 crypto-api-monitor
```

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
