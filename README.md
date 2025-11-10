# Crypto Resource Aggregator

A centralized API aggregator for cryptocurrency resources hosted on Hugging Face Spaces.

## Overview

This aggregator consolidates multiple cryptocurrency data sources including:
- **Block Explorers**: Etherscan, BscScan, TronScan
- **Market Data**: CoinGecko, CoinMarketCap, CryptoCompare
- **RPC Endpoints**: Ethereum, BSC, Tron, Polygon
- **News APIs**: Crypto news and sentiment analysis
- **Whale Tracking**: Large transaction monitoring
- **On-chain Analytics**: Blockchain data analysis

## Features

### ✅ Real-Time Monitoring
- Continuous health checks for all resources
- Automatic status updates (online/offline)
- Response time tracking
- Consecutive failure counting

### 📊 History Tracking
- Complete query history with timestamps
- Resource usage statistics
- Success/failure rates
- Average response times

### 🔄 No Mock Data
- All responses return real data from actual APIs
- Error status returned when resources are unavailable
- Transparent error messaging

### 🚀 Fallback Support
- Automatic fallback to alternative resources
- Multiple API keys for rate limit management
- CORS proxy support for browser access

## API Endpoints

### Resource Management

#### `GET /`
Root endpoint with API information and available endpoints.

#### `GET /resources`
List all available resource categories and their counts.

**Response:**
```json
{
  "total_categories": 7,
  "resources": {
    "block_explorers": ["etherscan", "bscscan", "tronscan"],
    "market_data": ["coingecko", "coinmarketcap"],
    "rpc_endpoints": [...],
    ...
  },
  "timestamp": "2025-11-10T..."
}
```

#### `GET /resources/{category}`
Get all resources in a specific category.

**Example:** `/resources/market_data`

### Query Resources

#### `POST /query`
Query a specific resource with parameters.

**Request Body:**
```json
{
  "resource_type": "market_data",
  "resource_name": "coingecko",
  "endpoint": "/simple/price",
  "params": {
    "ids": "bitcoin,ethereum",
    "vs_currencies": "usd"
  }
}
```

**Response:**
```json
{
  "success": true,
  "resource_type": "market_data",
  "resource_name": "coingecko",
  "data": {
    "bitcoin": {"usd": 45000},
    "ethereum": {"usd": 3000}
  },
  "response_time": 0.234,
  "timestamp": "2025-11-10T..."
}
```

### Status Monitoring

#### `GET /status`
Get real-time status of all resources.

**Response:**
```json
{
  "total_resources": 15,
  "online": 13,
  "offline": 2,
  "resources": [
    {
      "resource": "block_explorers.etherscan",
      "status": "online",
      "response_time": 0.123,
      "error": null,
      "timestamp": "2025-11-10T..."
    },
    ...
  ],
  "timestamp": "2025-11-10T..."
}
```

#### `GET /status/{category}/{name}`
Check status of a specific resource.

**Example:** `/status/market_data/coingecko`

### History & Analytics

#### `GET /history`
Get query history (default: last 100 queries).

**Query Parameters:**
- `limit` (optional): Number of records to return (default: 100)
- `resource_type` (optional): Filter by resource type

**Response:**
```json
{
  "count": 100,
  "history": [
    {
      "id": 1,
      "timestamp": "2025-11-10T10:30:00",
      "resource_type": "market_data",
      "resource_name": "coingecko",
      "endpoint": "https://api.coingecko.com/...",
      "status": "success",
      "response_time": 0.234,
      "error_message": null
    },
    ...
  ]
}
```

#### `GET /history/stats`
Get aggregated statistics from query history.

**Response:**
```json
{
  "total_queries": 1523,
  "successful_queries": 1487,
  "success_rate": 97.6,
  "most_queried_resources": [
    {"resource": "coingecko", "count": 456},
    {"resource": "etherscan", "count": 234}
  ],
  "average_response_time": 0.345,
  "timestamp": "2025-11-10T..."
}
```

#### `GET /health`
System health check endpoint.

## Usage Examples

### JavaScript/TypeScript

```javascript
// Get Bitcoin price from CoinGecko
const response = await fetch('https://your-space.hf.space/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    resource_type: 'market_data',
    resource_name: 'coingecko',
    endpoint: '/simple/price',
    params: {
      ids: 'bitcoin',
      vs_currencies: 'usd'
    }
  })
});

const data = await response.json();
console.log('BTC Price:', data.data.bitcoin.usd);

// Check Ethereum balance
const balanceResponse = await fetch('https://your-space.hf.space/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    resource_type: 'block_explorers',
    resource_name: 'etherscan',
    endpoint: '',
    params: {
      module: 'account',
      action: 'balance',
      address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
      tag: 'latest'
    }
  })
});

const balanceData = await balanceResponse.json();
console.log('ETH Balance:', balanceData.data.result / 1e18);
```

### Python

```python
import requests

# Query CoinGecko for multiple coins
response = requests.post('https://your-space.hf.space/query', json={
    'resource_type': 'market_data',
    'resource_name': 'coingecko',
    'endpoint': '/simple/price',
    'params': {
        'ids': 'bitcoin,ethereum,tron',
        'vs_currencies': 'usd,eur'
    }
})

data = response.json()
if data['success']:
    print('Prices:', data['data'])
else:
    print('Error:', data['error'])

# Get resource status
status = requests.get('https://your-space.hf.space/status')
print(f"Resources online: {status.json()['online']}/{status.json()['total_resources']}")
```

### cURL

```bash
# List all resources
curl https://your-space.hf.space/resources

# Query a resource
curl -X POST https://your-space.hf.space/query \
  -H "Content-Type: application/json" \
  -d '{
    "resource_type": "market_data",
    "resource_name": "coingecko",
    "endpoint": "/simple/price",
    "params": {
      "ids": "bitcoin",
      "vs_currencies": "usd"
    }
  }'

# Get status
curl https://your-space.hf.space/status

# Get history
curl https://your-space.hf.space/history?limit=50
```

## Resource Categories

### Block Explorers
- **Etherscan**: Ethereum blockchain explorer with API key
- **BscScan**: BSC blockchain explorer with API key
- **TronScan**: Tron blockchain explorer with API key

### Market Data
- **CoinGecko**: Free, no API key required
- **CoinMarketCap**: Requires API key, 333 calls/day free tier
- **CryptoCompare**: 100K calls/month free tier

### RPC Endpoints
- Ethereum (Infura, Alchemy, Ankr)
- Binance Smart Chain
- Tron
- Polygon

## Database Schema

### query_history
Tracks all API queries made through the aggregator.

```sql
CREATE TABLE query_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    resource_type TEXT NOT NULL,
    resource_name TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    status TEXT NOT NULL,
    response_time REAL,
    error_message TEXT
);
```

### resource_status
Tracks the health status of each resource.

```sql
CREATE TABLE resource_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_name TEXT NOT NULL UNIQUE,
    last_check DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    consecutive_failures INTEGER DEFAULT 0,
    last_success DATETIME,
    last_error TEXT
);
```

## Error Handling

The aggregator returns structured error responses:

```json
{
  "success": false,
  "resource_type": "market_data",
  "resource_name": "coinmarketcap",
  "error": "HTTP 429 - Rate limit exceeded",
  "response_time": 0.156,
  "timestamp": "2025-11-10T..."
}
```

## Deployment on Hugging Face

1. Create a new Space on Hugging Face
2. Select "Gradio" as the SDK (we'll use FastAPI which is compatible)
3. Upload the following files:
   - `app.py`
   - `requirements.txt`
   - `all_apis_merged_2025.json`
   - `README.md`
4. The Space will automatically deploy

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access the API
# Documentation: http://localhost:7860/docs
# API: http://localhost:7860
```

## Integration with Your Main App

```javascript
// Create a client wrapper
class CryptoAggregator {
  constructor(baseUrl = 'https://your-space.hf.space') {
    this.baseUrl = baseUrl;
  }

  async query(resourceType, resourceName, endpoint = '', params = {}) {
    const response = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resource_type: resourceType,
        resource_name: resourceName,
        endpoint: endpoint,
        params: params
      })
    });
    return await response.json();
  }

  async getStatus() {
    const response = await fetch(`${this.baseUrl}/status`);
    return await response.json();
  }

  async getHistory(limit = 100) {
    const response = await fetch(`${this.baseUrl}/history?limit=${limit}`);
    return await response.json();
  }
}

// Usage
const aggregator = new CryptoAggregator();

// Get Bitcoin price
const price = await aggregator.query('market_data', 'coingecko', '/simple/price', {
  ids: 'bitcoin',
  vs_currencies: 'usd'
});

// Check system status
const status = await aggregator.getStatus();
console.log(`${status.online}/${status.total_resources} resources online`);
```

## Monitoring & Maintenance

- Check `/status` regularly to ensure resources are online
- Monitor `/history/stats` for usage patterns and success rates
- Review consecutive failures in the database
- Update API keys when needed

## License

This aggregator is built for educational and development purposes.
API keys should be kept secure and rate limits respected.

## Support

For issues or questions:
1. Check the `/health` endpoint
2. Review `/history` for error patterns
3. Verify resource status with `/status`
4. Check individual resource documentation

---

Built with FastAPI and deployed on Hugging Face Spaces
