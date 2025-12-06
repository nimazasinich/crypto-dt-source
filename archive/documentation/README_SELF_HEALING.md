# 🔄 Crypto API Hub - Self-Healing System

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-red.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

**Intelligent, Automatic API Recovery and Monitoring System**

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Examples](#examples) • [Contributing](#contributing)

</div>

---

## 🌟 Overview

The **Crypto API Hub Self-Healing System** is an advanced, production-ready framework that automatically detects, recovers from, and monitors API failures across 74+ cryptocurrency data sources. Built with FastAPI and modern JavaScript, it ensures maximum uptime and reliability for your crypto applications.

### Why Self-Healing?

In the volatile world of cryptocurrency APIs:
- **APIs go down unexpectedly** 🚨
- **Rate limits get hit** ⏱️
- **Response times vary wildly** 🐌
- **Data quality fluctuates** 📊

This system **automatically handles all of these issues** without any manual intervention!

## ✨ Features

### Core Capabilities

- 🔄 **Automatic Recovery**: Detects and recovers from failures automatically
- 🔁 **Intelligent Retry**: Exponential backoff with configurable attempts
- 📊 **Health Monitoring**: Real-time monitoring of all endpoints
- 💾 **Smart Caching**: Intelligent caching for offline resilience
- 🎯 **Fallback System**: Automatic fallback to alternative sources
- 🔌 **Backend Proxy**: Last-resort proxy when direct calls fail
- 📈 **Real-time Stats**: Comprehensive monitoring and analytics
- 🚨 **Alert System**: Automatic alerts for critical issues

### Advanced Features

- **Multi-Strategy Recovery**: Multiple recovery approaches
- **Response Time Tracking**: Monitor and optimize performance
- **Failure Pattern Detection**: Identify recurring issues
- **Stale Data Recovery**: Use cached data as last resort
- **Self-Cleanup**: Automatic maintenance and optimization

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd workspace

# Install dependencies
pip install -r requirements.txt
```

### Start the Server

```bash
python hf_unified_server.py
```

### Access the Dashboard

Open your browser and navigate to:

```
http://localhost:8000/api/crypto-hub/
```

### Test Self-Healing

Try testing an endpoint - watch it automatically retry and recover from failures!

## 📖 Documentation

- **[Quick Start Guide](docs/CRYPTO_HUB_QUICK_START.md)**: Get up and running in 5 minutes
- **[Complete Guide](docs/CRYPTO_HUB_SELF_HEALING_GUIDE.md)**: Comprehensive documentation
- **[API Reference](docs/CRYPTO_HUB_SELF_HEALING_GUIDE.md#api-reference)**: Complete API documentation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Frontend Layer                      │
│  • crypto-api-hub-stunning.html                     │
│  • crypto-api-hub-self-healing.js                   │
│  • Automatic retry & fallback                       │
│  • Client-side caching                              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                  Backend Layer                       │
│  • FastAPI Router (crypto_api_hub_self_healing.py)  │
│  • Monitoring Service (crypto_hub_monitoring.py)    │
│  • Proxy & health checks                            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│             External APIs (74+ sources)              │
│  CoinGecko • Etherscan • Binance • CoinMarketCap   │
│  BscScan • CryptoPanic • And many more...           │
└─────────────────────────────────────────────────────┘
```

## 💡 Usage Examples

### Basic Self-Healing Fetch

```javascript
const selfHealing = new SelfHealingAPIHub({
    backendUrl: '/api/crypto-hub',
    retryAttempts: 3,
    enableCaching: true
});

const result = await selfHealing.fetchWithRecovery(
    'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
);

if (result.success) {
    console.log('Bitcoin Price:', result.data.bitcoin.usd);
    console.log('Data source:', result.source);
}
```

### Health Check

```javascript
const health = selfHealing.getHealthStatus();
console.log(`System Health: ${health.healthPercentage}%`);
```

### Backend Proxy

```bash
curl -X POST http://localhost:8000/api/crypto-hub/proxy \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
    "method": "GET"
  }'
```

### Monitor Health

```bash
curl http://localhost:8000/api/crypto-hub/health-status
```

## 📊 Self-Healing Flow

When an API call is made:

```
1. Primary Endpoint
   ├─ ✅ Success → Return data
   └─ ❌ Failure → Retry (3x with exponential backoff)
   
2. Retry Attempts
   ├─ ✅ Success → Return data
   └─ ❌ All failed → Try fallback endpoints
   
3. Fallback Endpoints
   ├─ ✅ Success → Return data (source: 'fallback')
   └─ ❌ All failed → Try backend proxy
   
4. Backend Proxy
   ├─ ✅ Success → Return data (source: 'backend-proxy')
   └─ ❌ Failed → Use stale cache
   
5. Stale Cache
   ├─ ✅ Available → Return cached data (with warning)
   └─ ❌ Not available → Return error + recovery suggestions
```

## 🔧 Configuration

### Frontend

```javascript
const config = {
    backendUrl: '/api/crypto-hub',
    enableAutoRecovery: true,
    enableCaching: true,
    retryAttempts: 3,
    retryDelay: 1000,
    healthCheckInterval: 60000,
    cacheExpiry: 300000
};
```

### Backend

```python
monitor = CryptoHubMonitor(
    check_interval=60,
    timeout=10,
    max_retries=3,
    alert_threshold=5
)
```

## 📈 Monitoring

### Real-Time Dashboard

Access the monitoring dashboard at:
```
http://localhost:8000/api/crypto-hub/
```

### Health API

```bash
# Get health status
curl http://localhost:8000/api/crypto-hub/health-status

# Get detailed diagnostics
curl http://localhost:8000/api/crypto-hub/diagnostics

# Export report
curl http://localhost:8000/api/crypto-hub/diagnostics > report.json
```

## 🧪 Testing

### Test Self-Healing

```javascript
// Test with failing endpoint
const result = await selfHealing.fetchWithRecovery(
    'https://invalid-api.example.com/data'
);
// Watch automatic retry, fallback, and recovery attempts
```

### Test Cache

```javascript
// First call - hits API
const result1 = await selfHealing.fetchWithRecovery(url);

// Second call - uses cache (faster)
const result2 = await selfHealing.fetchWithRecovery(url);
```

### Manual Recovery

```bash
curl -X POST http://localhost:8000/api/crypto-hub/recover \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "https://api.example.com"}'
```

## 🛠️ Components

### Frontend
- **crypto-api-hub-stunning.html**: Beautiful UI with 74+ services
- **crypto-api-hub-self-healing.js**: Self-healing JavaScript module

### Backend
- **crypto_api_hub_self_healing.py**: FastAPI router with proxy & health checks
- **crypto_hub_monitoring.py**: Background monitoring service

## 📝 API Reference

### Frontend Methods

- `fetchWithRecovery(url, options)`: Fetch with automatic recovery
- `performHealthChecks()`: Run health checks
- `getHealthStatus()`: Get system health
- `getDiagnostics()`: Get detailed diagnostics
- `triggerRecovery(endpoint)`: Manually trigger recovery

### Backend Endpoints

- `GET /api/crypto-hub/`: Serve dashboard
- `POST /api/crypto-hub/proxy`: Proxy requests
- `GET /api/crypto-hub/health-status`: Health status
- `POST /api/crypto-hub/health-check`: Run health check
- `POST /api/crypto-hub/recover`: Trigger recovery
- `GET /api/crypto-hub/diagnostics`: Get diagnostics

## 🌐 Supported APIs

The system monitors and provides self-healing for 74+ crypto APIs:

- **Explorers**: Etherscan, BscScan, TronScan, Blockchair, etc.
- **Market Data**: CoinGecko, CoinMarketCap, Binance, CryptoCompare, etc.
- **News**: CryptoPanic, NewsAPI, CoinDesk, CoinTelegraph, etc.
- **Sentiment**: Fear & Greed Index, LunarCrush, Santiment, etc.
- **Analytics**: Whale Alert, Glassnode, Nansen, DeBank, etc.

## 🔒 Security

- **API Keys**: Securely managed, never exposed in frontend
- **CORS**: Properly configured
- **Rate Limiting**: Built-in protection
- **Input Validation**: All inputs validated
- **Logging**: Security events logged

## 🚦 Status

- ✅ **Production Ready**: Fully tested and battle-hardened
- ✅ **Well Documented**: Comprehensive documentation
- ✅ **Actively Maintained**: Regular updates and improvements
- ✅ **Performance Optimized**: Fast and efficient

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [HTTPX](https://www.python-httpx.org/)
- Modern JavaScript (ES6+)

## 📞 Support

- **Documentation**: See [docs/](docs/)
- **Issues**: Open a GitHub issue
- **Questions**: Contact the development team

---

<div align="center">

**Made with ❤️ for the crypto community**

[⬆ Back to Top](#-crypto-api-hub---self-healing-system)

</div>
