 
# 🚀 Cryptocurrency API Resource Monitor

**Comprehensive cryptocurrency market intelligence API resource management system**

Monitor and manage all API resources from blockchain explorers, market data providers, RPC nodes, news feeds, and more. Track online status, validate endpoints, categorize by domain, and maintain availability metrics across all cryptocurrency data sources.
 

## 📋 Table of Contents

- [Features](#-features)
- [Monitored Resources](#-monitored-resources)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [API Categories](#-api-categories)
- [Status Classification](#-status-classification)
- [Alert Conditions](#-alert-conditions)
- [Failover Management](#-failover-management)
- [Dashboard](#-dashboard)
- [Configuration](#-configuration)

 

## ✨ Features

### Core Monitoring
- ✅ **Real-time health checks** for 50+ cryptocurrency APIs
- ✅ **Response time tracking** with millisecond precision
- ✅ **Success/failure rate monitoring** per provider
- ✅ **Automatic status classification** (ONLINE/DEGRADED/SLOW/UNSTABLE/OFFLINE)
- ✅ **SSL certificate validation** and expiration tracking
- ✅ **Rate limit detection** (429, 403 responses)

### Redundancy & Failover
- ✅ **Automatic failover chain building** for each data type
- ✅ **Multi-tier resource prioritization** (TIER-1 critical, TIER-2 high, TIER-3 medium, TIER-4 low)
- ✅ **Single Point of Failure (SPOF) detection**
- ✅ **Backup provider recommendations**
- ✅ **Cross-provider data validation**

### Alerting & Reporting
- ✅ **Critical alert system** for TIER-1 API failures
- ✅ **Performance degradation warnings**
- ✅ **JSON export reports** for integration
- ✅ **Historical uptime statistics**
- ✅ **Real-time web dashboard** with auto-refresh

### Security & Privacy
- ✅ **API key masking** in all outputs (first/last 4 chars only)
- ✅ **Secure credential storage** from registry
- ✅ **Rate limit compliance** with configurable delays
- ✅ **CORS proxy support** for browser compatibility

 
## 🌐 Monitored Resources

### Blockchain Explorers
- **Etherscan** (2 keys): Ethereum blockchain data, transactions, smart contracts
- **BscScan** (1 key): BSC blockchain explorer, BEP-20 tokens
- **TronScan** (1 key): Tron network explorer, TRC-20 tokens

### Market Data Providers
- **CoinGecko**: Real-time prices, market caps, trending coins (FREE)
- **CoinMarketCap** (2 keys): Professional market data
- **CryptoCompare** (1 key): OHLCV data, historical snapshots
- **CoinPaprika**: Comprehensive market information
- **CoinCap**: Asset pricing and exchange rates

### RPC Nodes
**Ethereum:** Ankr, PublicNode, Cloudflare, LlamaNodes
**BSC:** Official BSC, Ankr, PublicNode
**Polygon:** Official, Ankr
**Tron:** TronGrid, TronStack

### News & Sentiment
- **CryptoPanic**: Aggregated news with sentiment scores
- **NewsAPI** (1 key): General crypto news
- **Alternative.me**: Fear & Greed Index
- **Reddit**: r/cryptocurrency JSON feeds

### Additional Resources
- **Whale Tracking**: WhaleAlert API
- **CORS Proxies**: AllOrigins, CORS.SH, Corsfix, ThingProxy
- **On-Chain Analytics**: The Graph, Blockchair

**Total: 50+ monitored endpoints across 7 categories**

 
## 🚀 Quick Start

### Prerequisites
- Node.js 14.0.0 or higher
- Python 3.x (for dashboard server)

### Installation

```bash
# Clone the repository
git clone https://github.com/nimazasinich/crypto-dt-source.git
cd crypto-dt-source

# No dependencies to install - uses Node.js built-in modules!
```

### Run Your First Health Check

```bash
# Run a complete health check
node api-monitor.js

# This will:
# - Load API keys from all_apis_merged_2025.json
# - Check all 50+ endpoints
# - Generate api-monitor-report.json
# - Display status report in terminal
```

### View the Dashboard

 # Start the web server
npm run dashboard

# Open in browser:
# http://localhost:8080/dashboard.html
```

---

## 📖 Usage

### 1. Single Health Check

```bash
node api-monitor.js
```

**Output:**
```
✓ Registry loaded successfully
  Found 7 API key categories

╔════════════════════════════════════════════════════════╗
║  CRYPTOCURRENCY API RESOURCE MONITOR - Health Check   ║
╚════════════════════════════════════════════════════════╝

  Checking blockchainExplorers...
  Checking marketData...
  Checking newsAndSentiment...
  Checking rpcNodes...

╔════════════════════════════════════════════════════════╗
║              RESOURCE STATUS REPORT                    ║
╚════════════════════════════════════════════════════════╝

📁 BLOCKCHAINEXPLORERS
────────────────────────────────────────────────────────
  ✓ Etherscan-1              ONLINE        245ms [TIER-1]
  ✓ Etherscan-2              ONLINE        312ms [TIER-1]
  ✓ BscScan                  ONLINE        189ms [TIER-1]
  ✓ TronScan                 ONLINE        567ms [TIER-2]

📁 MARKETDATA
────────────────────────────────────────────────────────
  ✓ CoinGecko                ONLINE        142ms [TIER-1]
  ✓ CoinGecko-Price          ONLINE        156ms [TIER-1]
  ◐ CoinMarketCap-1          DEGRADED     2340ms [TIER-1]
  ✓ CoinMarketCap-2          ONLINE        487ms [TIER-1]
  ✓ CryptoCompare            ONLINE        298ms [TIER-2]

╔════════════════════════════════════════════════════════╗
║                    SUMMARY                             ║
╚════════════════════════════════════════════════════════╝
  Total Resources:    52
  Online:             48 (92.3%)
  Degraded:           3 (5.8%)
  Offline:            1 (1.9%)
  Overall Health:     92.3%

✓ Report exported to api-monitor-report.json
```

### 2. Continuous Monitoring

```bash
node api-monitor.js --continuous
```

Runs health checks every 5 minutes and continuously updates the report.

### 3. Failover Analysis

```bash
node failover-manager.js
```

**Output:**
```
╔════════════════════════════════════════════════════════╗
║         FAILOVER CHAIN BUILDER                         ║
╚════════════════════════════════════════════════════════╝

📊 ETHEREUMPRICE Failover Chain:
────────────────────────────────────────────────────────
  🎯 [PRIMARY]     CoinGecko                 ONLINE        142ms [TIER-1]
    ↓ [BACKUP]     CoinMarketCap-2           ONLINE        487ms [TIER-1]
    ↓ [BACKUP-2]   CryptoCompare             ONLINE        298ms [TIER-2]
    ↓ [BACKUP-3]   CoinPaprika               ONLINE        534ms [TIER-2]

📊 ETHEREUMEXPLORER Failover Chain:
────────────────────────────────────────────────────────
  🎯 [PRIMARY]     Etherscan-1               ONLINE        245ms [TIER-1]
    ↓ [BACKUP]     Etherscan-2               ONLINE        312ms [TIER-1]

╔════════════════════════════════════════════════════════╗
║       SINGLE POINT OF FAILURE ANALYSIS                ║
╚════════════════════════════════════════════════════════╝

  🟡 [MEDIUM] rpcPolygon: Only two resources available
  🟠 [HIGH] sentiment: Only one resource available (SPOF)

✓ Failover configuration exported to failover-config.json
```

### 4. Launch Complete Dashboard

```bash
npm run full-check
```

Runs monitor → failover analysis → starts web dashboard

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  API REGISTRY JSON                      │
│         (all_apis_merged_2025.json)                     │
│  - Discovered keys (masked)                             │
│  - Raw API configurations                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              CRYPTO API MONITOR                         │
│                (api-monitor.js)                         │
│                                                         │
│  ┌─────────────────────────────────────────┐           │
│  │  Resource Loader                        │           │
│  │  - Parse registry                       │           │
│  │  - Extract API keys                     │           │
│  │  - Build endpoint URLs                  │           │
│  └─────────────────────────────────────────┘           │
│                     │                                   │
│  ┌─────────────────────────────────────────┐           │
│  │  Health Check Engine                    │           │
│  │  - HTTP/HTTPS requests                  │           │
│  │  - Response time measurement            │           │
│  │  - Status code validation               │           │
│  │  - RPC endpoint testing                 │           │
│  └─────────────────────────────────────────┘           │
│                     │                                   │
│  ┌─────────────────────────────────────────┐           │
│  │  Status Classifier                      │           │
│  │  - Success rate calculation             │           │
│  │  - Response time averaging              │           │
│  │  - ONLINE/DEGRADED/OFFLINE              │           │
│  └─────────────────────────────────────────┘           │
│                     │                                   │
│  ┌─────────────────────────────────────────┐           │
│  │  Alert System                           │           │
│  │  - TIER-1 failure detection             │           │
│  │  - Performance warnings                 │           │
│  │  - Critical notifications               │           │
│  └─────────────────────────────────────────┘           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            MONITORING REPORT JSON                       │
│         (api-monitor-report.json)                       │
│  - Summary statistics                                   │
│  - Per-resource status                                  │
│  - Historical data                                      │
│  - Active alerts                                        │
└────────┬──────────────────────────────┬─────────────────┘
         │                              │
         ▼                              ▼
┌─────────────────────┐    ┌──────────────────────────────┐
│  FAILOVER MANAGER   │    │    WEB DASHBOARD             │
│ (failover-manager)  │    │   (dashboard.html)           │
│                     │    │                              │
│ - Build chains      │    │  - Real-time visualization   │
│ - SPOF detection    │    │  - Auto-refresh              │
│ - Redundancy report │    │  - Alert display             │
│ - Export config     │    │  - Health metrics            │
└─────────────────────┘    └──────────────────────────────┘
```

---

## 📊 API Categories

### 1. Blockchain Explorers
**Purpose:** Query blockchain data, transactions, balances, smart contracts

**Resources:**
- Etherscan (Ethereum) - 2 keys
- BscScan (BSC) - 1 key
- TronScan (Tron) - 1 key

**Use Cases:**
- Get wallet balances
- Track transactions
- Monitor token transfers
- Query smart contracts
- Get gas prices

### 2. Market Data
**Purpose:** Real-time cryptocurrency prices, market caps, volume

**Resources:**
- CoinGecko (FREE, no key required) ⭐
- CoinMarketCap - 2 keys
- CryptoCompare - 1 key
- CoinPaprika (FREE)
- CoinCap (FREE)

**Use Cases:**
- Live price feeds
- Historical OHLCV data
- Market cap rankings
- Trading volume
- Trending coins

### 3. RPC Nodes
**Purpose:** Direct blockchain interaction via JSON-RPC

**Resources:**
- **Ethereum:** Ankr, PublicNode, Cloudflare, LlamaNodes
- **BSC:** Official, Ankr, PublicNode
- **Polygon:** Official, Ankr
- **Tron:** TronGrid, TronStack

**Use Cases:**
- Send transactions
- Read smart contracts
- Get block data
- Subscribe to events
- Query state

### 4. News & Sentiment
**Purpose:** Crypto news aggregation and market sentiment

**Resources:**
- CryptoPanic (FREE)
- Alternative.me Fear & Greed Index (FREE)
- NewsAPI - 1 key
- Reddit r/cryptocurrency (FREE)

**Use Cases:**
- News feed aggregation
- Sentiment analysis
- Fear & Greed tracking
- Social signals

### 5. Whale Tracking
**Purpose:** Monitor large cryptocurrency transactions

**Resources:**
- WhaleAlert API

**Use Cases:**
- Track whale movements
- Exchange flow monitoring
- Large transaction alerts

### 6. CORS Proxies
**Purpose:** Bypass CORS restrictions in browser applications

**Resources:**
- AllOrigins (unlimited)
- CORS.SH (fast)
- Corsfix (60 req/min)
- ThingProxy (10 req/sec)

**Use Cases:**
- Browser-based API calls
- Frontend applications
- CORS workarounds

---

## 📈 Status Classification

The monitor automatically classifies each API into one of five states:

| Status | Success Rate | Response Time | Description |
|--------|--------------|---------------|-------------|
| 🟢 **ONLINE** | ≥95% | <2 seconds | Fully operational, optimal performance |
| 🟡 **DEGRADED** | 80-95% | 2-5 seconds | Functional but slower than normal |
| 🟠 **SLOW** | 70-80% | 5-10 seconds | Significant performance issues |
| 🔴 **UNSTABLE** | 50-70% | Any | Frequent failures, unreliable |
| ⚫ **OFFLINE** | <50% | Any | Not responding or completely down |

**Classification Logic:**
- Based on last 10 health checks
- Success rate = successful responses / total attempts
- Response time = average of successful requests only

---

## ⚠️ Alert Conditions

The system triggers alerts for:

### Critical Alerts
- ❌ TIER-1 API offline (Etherscan, CoinGecko, Infura, Alchemy)
- ❌ All providers in a category offline
- ❌ Zero available resources for essential data type

### Warning Alerts
- ⚠️ Response time >5 seconds sustained for 15 minutes
- ⚠️ Success rate dropped below 80%
- ⚠️ Single Point of Failure (only 1 provider available)
- ⚠️ Rate limit reached (>80% consumed)

### Info Alerts
- ℹ️ API key approaching expiration
- ℹ️ SSL certificate expires within 7 days
- ℹ️ New resource added to registry

---

## 🔄 Failover Management

### Automatic Failover Chains

The system builds intelligent failover chains for each data type:

```javascript
// Example: Ethereum Price Failover Chain
const failoverConfig = require('./failover-config.json');

async function getEthereumPrice() {
  const chain = failoverConfig.chains.ethereumPrice;

  for (const resource of chain) {
    try {
      // Try primary first (CoinGecko)
      const response = await fetch(resource.url + '/api/v3/simple/price?ids=ethereum&vs_currencies=usd');
      const data = await response.json();
      return data.ethereum.usd;
    } catch (error) {
      console.log(`${resource.name} failed, trying next in chain...`);
      continue;
    }
  }

  throw new Error('All resources in failover chain failed');
}
```

### Priority Tiers

**TIER-1 (CRITICAL):** Etherscan, BscScan, CoinGecko, Infura, Alchemy
**TIER-2 (HIGH):** CoinMarketCap, CryptoCompare, TronScan, NewsAPI
**TIER-3 (MEDIUM):** Alternative.me, Reddit, CORS proxies, public RPCs
**TIER-4 (LOW):** Experimental APIs, community nodes, backup sources

Failover chains prioritize lower tier numbers first.

---

## 🎨 Dashboard

### Features

- **Real-time monitoring** with auto-refresh every 5 minutes
- **Visual health indicators** with color-coded status
- **Category breakdown** showing all resources by type
- **Alert notifications** prominently displayed
- **Health bar** showing overall system status
- **Response times** for each endpoint
- **Tier badges** showing resource priority

### Screenshots

**Summary Cards:**
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Total Resources │  │     Online      │  │    Degraded     │  │     Offline     │
│       52        │  │  48 (92.3%)     │  │   3 (5.8%)      │  │   1 (1.9%)      │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Resource List:**
```
🔍 BLOCKCHAIN EXPLORERS
───────────────────────────────────────────────────
✓ Etherscan-1    [TIER-1]    ONLINE     245ms
✓ Etherscan-2    [TIER-1]    ONLINE     312ms
✓ BscScan        [TIER-1]    ONLINE     189ms
```

### Access

```bash
npm run dashboard
# Open: http://localhost:8080/dashboard.html
```

---

## ⚙️ Configuration

### Monitor Configuration

Edit `api-monitor.js`:

```javascript
const CONFIG = {
  REGISTRY_FILE: './all_apis_merged_2025.json',
  CHECK_INTERVAL: 5 * 60 * 1000,  // 5 minutes
  TIMEOUT: 10000,                  // 10 seconds
  MAX_RETRIES: 3,
  RETRY_DELAY: 2000,

  THRESHOLDS: {
    ONLINE: { responseTime: 2000, successRate: 0.95 },
    DEGRADED: { responseTime: 5000, successRate: 0.80 },
    SLOW: { responseTime: 10000, successRate: 0.70 },
    UNSTABLE: { responseTime: Infinity, successRate: 0.50 }
  }
};
```

### Adding New Resources

Edit the `API_REGISTRY` object in `api-monitor.js`:

```javascript
marketData: {
  // ... existing resources ...

  newProvider: [
    {
      name: 'MyNewAPI',
      url: 'https://api.example.com',
      testEndpoint: '/health',
      requiresKey: false,
      tier: 3
    }
  ]
}
```

---

## 🔐 Security Notes

- ✅ API keys are **never logged** in full (masked to first/last 4 chars)
- ✅ Registry file should be kept **secure** and not committed to public repos
- ✅ Use **environment variables** for production deployments
- ✅ Rate limits are **automatically respected** with delays
- ✅ SSL/TLS is used for all external API calls

---

## 📝 Output Files

| File | Purpose | Format |
|------|---------|--------|
| `api-monitor-report.json` | Complete health check results | JSON |
| `failover-config.json` | Failover chain configuration | JSON |

### api-monitor-report.json Structure

```json
{
  "timestamp": "2025-11-10T22:30:00.000Z",
  "summary": {
    "totalResources": 52,
    "onlineResources": 48,
    "degradedResources": 3,
    "offlineResources": 1
  },
  "categories": {
    "blockchainExplorers": [...],
    "marketData": [...],
    "rpcNodes": [...]
  },
  "alerts": [
    {
      "severity": "CRITICAL",
      "message": "TIER-1 API offline: Etherscan-1",
      "timestamp": "2025-11-10T22:28:15.000Z"
    }
  ],
  "history": {
    "CoinGecko": [
      {
        "success": true,
        "responseTime": 142,
        "timestamp": "2025-11-10T22:30:00.000Z"
      }
    ]
  }
}
```

---

## 🛠️ Troubleshooting

### "Failed to load registry"

**Cause:** `all_apis_merged_2025.json` not found
**Solution:** Ensure the file exists in the same directory

### "Request timeout" errors

**Cause:** API endpoint is slow or down
**Solution:** Normal behavior, will be classified as SLOW/OFFLINE

### "CORS error" in dashboard

**Cause:** Report JSON not accessible
**Solution:** Run `npm run dashboard` to start local server

### Rate limit errors (429)

**Cause:** Too many requests to API
**Solution:** Increase `CHECK_INTERVAL` or reduce resource list

---

## 📜 License

MIT License - see LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! To add new API resources:

1. Update `API_REGISTRY` in `api-monitor.js`
2. Add test endpoint
3. Classify into appropriate tier
4. Update this README

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review configuration opt

**Built with ❤️ for the cryptocurrency community**

*Monitor smarter, not harder
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
 