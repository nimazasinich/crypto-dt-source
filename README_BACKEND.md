---
title: Crypto API Monitor Backend
emoji: 📊
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# Crypto API Monitor Backend

Real-time cryptocurrency API monitoring backend service built with FastAPI.

## Features

- **Real-time Health Monitoring**: Automatically monitors 11+ cryptocurrency API providers every 5 minutes
- **WebSocket Support**: Live updates for frontend dashboard integration
- **REST API**: Comprehensive endpoints for status, logs, categories, and analytics
- **SQLite Database**: Persistent storage for connection logs, metrics, and configuration
- **Rate Limit Tracking**: Monitor API usage and rate limits per provider
- **Connection Logging**: Track all API requests with response times and error details
- **Authentication**: Token-based authentication and IP whitelist support

## API Providers Monitored

### Market Data
- CoinGecko (free)
- CoinMarketCap (requires API key)
- CryptoCompare (requires API key)
- Binance (free)

### Blockchain Explorers
- Etherscan (requires API key)
- BscScan (requires API key)
- TronScan (requires API key)

### News & Sentiment
- CryptoPanic (free)
- NewsAPI (requires API key)
- Alternative.me Fear & Greed (free)

### On-chain Analytics
- The Graph (free)
- Blockchair (free)

## API Documentation

Visit `/docs` for interactive API documentation (Swagger UI).
Visit `/redoc` for alternative API documentation (ReDoc).

## Main Endpoints

### Status & Monitoring
- `GET /api/status` - Overall system status
- `GET /api/categories` - Category statistics
- `GET /api/providers` - List all providers with filters
- `GET /api/logs` - Connection logs with pagination
- `GET /api/failures` - Failure analysis
- `GET /api/rate-limits` - Rate limit status

### Configuration
- `GET /api/config/keys` - API key configuration
- `GET /api/schedule` - Schedule configuration
- `POST /api/schedule/trigger` - Manually trigger scheduled task

### Analytics
- `GET /api/charts/health-history` - Health history for charts
- `GET /api/charts/compliance` - Compliance chart data
- `GET /api/freshness` - Data freshness status

### WebSocket
- `WS /ws/live` - Real-time updates

## Environment Variables

Create a `.env` file or set environment variables:

```bash
# Optional: API authentication tokens (comma-separated)
API_TOKENS=token1,token2

# Optional: IP whitelist (comma-separated)
ALLOWED_IPS=192.168.1.1,10.0.0.1

# Optional: Database URL (default: sqlite:///./crypto_monitor.db)
DATABASE_URL=sqlite:///./crypto_monitor.db

# Optional: Server port (default: 7860)
PORT=7860
```

## Deployment to Hugging Face Spaces

### Option 1: Docker SDK

1. Create a new Hugging Face Space
2. Select **Docker** SDK
3. Push this repository to GitHub
4. Connect the GitHub repository to your Space
5. Add environment variables in Space settings:
   - `API_TOKENS=your_secret_token_here`
   - `ALLOWED_IPS=` (optional, leave empty for no restriction)
6. The Space will automatically build and deploy

### Option 2: Local Docker

```bash
# Build Docker image
docker build -t crypto-api-monitor .

# Run container
docker run -p 7860:7860 \
  -e API_TOKENS=your_token_here \
  crypto-api-monitor
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Or with uvicorn
uvicorn app:app --host 0.0.0.0 --port 7860 --reload
```

Visit `http://localhost:7860` to access the API.
Visit `http://localhost:7860/docs` for interactive documentation.

## Database Schema

The application uses SQLite with the following tables:

- **providers**: API provider configurations
- **connection_attempts**: Log of all API connection attempts
- **data_collections**: Data collection records
- **rate_limit_usage**: Rate limit tracking
- **schedule_config**: Scheduled task configuration

## WebSocket Protocol

Connect to `ws://localhost:7860/ws/live` for real-time updates.

### Message Types

**Status Update**
```json
{
  "type": "status_update",
  "data": {
    "total_apis": 11,
    "online": 10,
    "degraded": 1,
    "offline": 0
  }
}
```

**New Log Entry**
```json
{
  "type": "new_log_entry",
  "data": {
    "timestamp": "2025-11-11T00:00:00",
    "provider": "CoinGecko",
    "status": "success",
    "response_time_ms": 120
  }
}
```

**Rate Limit Alert**
```json
{
  "type": "rate_limit_alert",
  "data": {
    "provider": "CoinMarketCap",
    "usage_percentage": 85
  }
}
```

## Frontend Integration

Update your frontend dashboard configuration:

```javascript
// config.js
const config = {
  apiBaseUrl: 'https://YOUR_USERNAME-crypto-api-monitor.hf.space',
  wsUrl: 'wss://YOUR_USERNAME-crypto-api-monitor.hf.space/ws/live',
  authToken: 'your_token_here' // Optional
};
```

## Architecture

```
app.py                          # FastAPI application entry point
config.py                       # Configuration & API registry loader
database/
  ├── db.py                     # Database initialization
  └── models.py                 # SQLAlchemy models
monitoring/
  └── health_monitor.py         # Background health monitoring
api/
  ├── endpoints.py              # REST API endpoints
  ├── websocket.py              # WebSocket handler
  └── auth.py                   # Authentication
utils/
  ├── http_client.py            # Async HTTP client with retry
  ├── logger.py                 # Structured logging
  └── validators.py             # Input validation
```

## API Keys

API keys are loaded from `all_apis_merged_2025.json` in the `discovered_keys` section:

```json
{
  "discovered_keys": {
    "etherscan": ["key1", "key2"],
    "bscscan": ["key1"],
    "coinmarketcap": ["key1", "key2"],
    ...
  }
}
```

## Performance

- Health checks run every 5 minutes
- Response time tracking for all providers
- Automatic retry with exponential backoff
- Connection timeout: 10 seconds
- Database queries optimized with indexes

## Security

- Optional token-based authentication
- IP whitelist support
- API keys masked in logs and responses
- CORS enabled for frontend access
- SQL injection protection via SQLAlchemy ORM

## License

MIT License

## Author

**Nima Zasinich**
- GitHub: [@nimazasinich](https://github.com/nimazasinich)
- Project: Crypto API Monitor Backend

---

**Built for the crypto dev community**
