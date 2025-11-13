# 🚀 Crypto Monitor ULTIMATE - Extended Edition

A powerful cryptocurrency monitoring and analysis system with support for **100+ free API providers** and advanced **Provider Pool Management** system.

[🇮🇷 نسخه فارسی (Persian Version)](README_FA.md)

## 📁 Project Structure

**📖 برای مشاهده ساختار کامل پروژه:**
- [🌳 ساختار کامل پروژه (فارسی)](PROJECT_STRUCTURE_FA.md) - توضیحات کامل و تفصیلی
- [⚡ مرجع سریع (فارسی)](QUICK_REFERENCE_FA.md) - فهرست سریع فایل‌های فعال
- [🌲 ساختار درختی بصری](TREE_STRUCTURE.txt) - نمایش درختی ASCII art

**🎯 فایل‌های اصلی:**
- `api_server_extended.py` - سرور اصلی FastAPI
- `unified_dashboard.html` - داشبورد اصلی
- `providers_config_extended.json` - پیکربندی ProviderManager
- `providers_config_ultimate.json` - پیکربندی ResourceManager

## ✨ Key Features

### 🎯 Provider Management
- ✅ **100+ Free API Providers** across multiple categories
- 🔄 **Pool System with Multiple Rotation Strategies**
  - Round Robin
  - Priority-based
  - Weighted Random
  - Least Used
  - Fastest Response
- 🛡️ **Circuit Breaker** to prevent repeated requests to failed services
- ⚡ **Smart Rate Limiting** for each provider
- 📊 **Detailed Performance Statistics** for every provider
- 🔍 **Automatic Health Checks** with periodic monitoring

### 📈 Provider Categories

#### 💰 Market Data
- CoinGecko, CoinPaprika, CoinCap
- CryptoCompare, Nomics, Messari
- LiveCoinWatch, Cryptorank, CoinLore, CoinCodex

#### 🔗 Blockchain Explorers
- Etherscan, BscScan, PolygonScan
- Arbiscan, Optimistic Etherscan
- Blockchair, Blockchain.info, Ethplorer

#### 🏦 DeFi Protocols
- DefiLlama, Aave, Compound
- Uniswap V3, PancakeSwap, SushiSwap
- Curve Finance, 1inch, Yearn Finance

#### 🖼️ NFT
- OpenSea, Rarible, Reservoir, NFTPort

#### 📰 News & Social
- CryptoPanic, NewsAPI
- CoinDesk RSS, Cointelegraph RSS, Bitcoinist RSS
- Reddit Crypto, LunarCrush

#### 💭 Sentiment Analysis
- Alternative.me (Fear & Greed Index)
- Santiment, LunarCrush

#### 📊 Analytics
- Glassnode, IntoTheBlock
- Coin Metrics, Kaiko

#### 💱 Exchanges
- Binance, Kraken, Coinbase
- Bitfinex, Huobi, KuCoin
- OKX, Gate.io, Bybit

#### 🤗 Hugging Face Models
- Sentiment Analysis models
- Text Classification models
- Zero-Shot Classification models

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│        Unified Dashboard (HTML/JS)              │
│  📊 Data Display | 🔄 Pool Management | 📈 Stats│
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│         FastAPI Server (Python)                 │
│  🌐 REST API | WebSocket | Background Tasks    │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│      Provider Manager (Core Logic)              │
│  🔄 Rotation | 🛡️ Circuit Breaker | 📊 Stats   │
└────────────────────┬────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
┌─────────┐    ┌─────────┐    ┌─────────┐
│ Pool 1  │    │ Pool 2  │    │ Pool N  │
│ Market  │    │  DeFi   │    │   NFT   │
└────┬────┘    └────┬────┘    └────┬────┘
     │              │              │
     └──────┬───────┴──────┬───────┘
            ▼              ▼
    ┌──────────────┐  ┌──────────────┐
    │  Provider 1  │  │  Provider N  │
    │ (CoinGecko)  │  │  (Binance)   │
    └──────────────┘  └──────────────┘
```

## 📦 Installation

### Prerequisites
```bash
Python 3.8+
pip
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Quick Start
```bash
# Method 1: Direct run
python api_server_extended.py

# Method 2: Using launcher script
python start_server.py

# Method 3: With uvicorn
uvicorn api_server_extended:app --reload --host 0.0.0.0 --port 8000

# Method 4: Using Docker
docker-compose up -d
```

### Access Dashboard
```
http://localhost:8000
```

## 🔧 API Usage

### 🌐 Main Endpoints

#### **System Status**
```http
GET /health
GET /api/status
GET /api/stats
```

#### **Provider Management**
```http
GET    /api/providers                     # List all
GET    /api/providers/{provider_id}       # Get details
POST   /api/providers/{provider_id}/health-check
GET    /api/providers/category/{category}
```

#### **Pool Management**
```http
GET    /api/pools                        # List all pools
GET    /api/pools/{pool_id}              # Get pool details
POST   /api/pools                        # Create new pool
DELETE /api/pools/{pool_id}              # Delete pool

POST   /api/pools/{pool_id}/members      # Add member
DELETE /api/pools/{pool_id}/members/{provider_id}
POST   /api/pools/{pool_id}/rotate       # Manual rotation
GET    /api/pools/history                # Rotation history
```

### 📝 Usage Examples

#### Create New Pool
```bash
curl -X POST http://localhost:8000/api/pools \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Market Pool",
    "category": "market_data",
    "rotation_strategy": "weighted",
    "description": "Pool for market data providers"
  }'
```

#### Add Provider to Pool
```bash
curl -X POST http://localhost:8000/api/pools/my_market_pool/members \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": "coingecko",
    "priority": 10,
    "weight": 100
  }'
```

#### Rotate Pool
```bash
curl -X POST http://localhost:8000/api/pools/my_market_pool/rotate \
  -H "Content-Type: application/json" \
  -d '{"reason": "manual rotation"}'
```

## 🎮 Python API Usage

```python
import asyncio
from provider_manager import ProviderManager

async def main():
    # Create manager
    manager = ProviderManager()
    
    # Health check all providers
    await manager.health_check_all()
    
    # Get provider from pool
    provider = manager.get_next_from_pool("primary_market_data_pool")
    if provider:
        print(f"Selected: {provider.name}")
        print(f"Success Rate: {provider.success_rate}%")
    
    # Get overall stats
    stats = manager.get_all_stats()
    print(f"Total Providers: {stats['summary']['total_providers']}")
    print(f"Online: {stats['summary']['online']}")
    
    # Export stats
    manager.export_stats("my_stats.json")
    
    await manager.close_session()

asyncio.run(main())
```

## 📊 Pool Rotation Strategies

### 1️⃣ Round Robin
Each provider is selected in turn.
```python
rotation_strategy = "round_robin"
```

### 2️⃣ Priority-Based
Provider with highest priority is selected.
```python
rotation_strategy = "priority"
# Provider with priority=10 selected over priority=5
```

### 3️⃣ Weighted Random
Random selection with weights.
```python
rotation_strategy = "weighted"
# Provider with weight=100 has 2x chance vs weight=50
```

### 4️⃣ Least Used
Provider with least usage is selected.
```python
rotation_strategy = "least_used"
```

### 5️⃣ Fastest Response
Provider with fastest response time is selected.
```python
rotation_strategy = "fastest_response"
```

## 🛡️ Circuit Breaker

The Circuit Breaker system automatically disables problematic providers:

- **Threshold**: 5 consecutive failures
- **Timeout**: 60 seconds
- **Auto Recovery**: After timeout expires

```python
# Automatic Circuit Breaker in Provider
if provider.consecutive_failures >= 5:
    provider.circuit_breaker_open = True
    provider.circuit_breaker_open_until = time.time() + 60
```

## 📈 Monitoring & Logging

### Periodic Health Checks
The system automatically checks all provider health every 30 seconds.

### Statistics
- **Total Requests**
- **Successful/Failed Requests**
- **Success Rate**
- **Average Response Time**
- **Pool Rotation Count**

### Export Stats
```python
manager.export_stats("stats_export.json")
```

## 🔐 API Key Management

For providers requiring API keys:

1. Create `.env` file (copy from `.env.example`):
```env
# Market Data
COINMARKETCAP_API_KEY=your_key_here
CRYPTOCOMPARE_API_KEY=your_key_here

# Blockchain Data
ALCHEMY_API_KEY=your_key_here
INFURA_API_KEY=your_key_here

# News
NEWSAPI_KEY=your_key_here

# Analytics
GLASSNODE_API_KEY=your_key_here
```

2. Use in your code with `python-dotenv`:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("COINMARKETCAP_API_KEY")
```

## 🎨 Web Dashboard

The dashboard includes these tabs:

### 📊 Market
- Global market stats
- Top cryptocurrencies list
- Charts (Dominance, Fear & Greed)
- Trending & DeFi protocols

### 📡 API Monitor
- All provider status
- Response times
- Last health check
- Sentiment analysis (HuggingFace)

### ⚡ Advanced
- API list
- Export JSON/CSV
- Backup creation
- Cache clearing
- Activity logs

### ⚙️ Admin
- Add new APIs
- Settings management
- Overall statistics

### 🤗 HuggingFace
- Health status
- Models & datasets list
- Registry search
- Online sentiment analysis

### 🔄 Pools
- Pool management
- Add/remove members
- Manual rotation
- Rotation history
- Detailed statistics

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f crypto-monitor

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build
```

## 🧪 Testing

```bash
# Test Provider Manager
python provider_manager.py

# Run test suite
python test_providers.py

# Test API server
python api_server_extended.py
```

## 📄 Project Files

```
crypto-monitor-hf-full-fixed-v4-realapis/
├── unified_dashboard.html           # Main web dashboard
├── providers_config_extended.json   # 100+ provider configs
├── provider_manager.py              # Core Provider & Pool logic
├── api_server_extended.py           # FastAPI server
├── start_server.py                  # Launcher script
├── test_providers.py                # Test suite
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker configuration
├── docker-compose.yml               # Docker Compose setup
├── README.md                        # This file (English)
└── README_FA.md                     # Persian documentation
```

## ✅ Latest Features

### 📡 Real-time WebSocket Support
- **Full WebSocket API** for instant data updates
- **Session Management** with client tracking
- **Live connection counter** showing online users
- **Auto-reconnection** with heartbeat monitoring
- **Subscribe/Unsubscribe** to different data channels
- **Beautiful UI components** for connection status

[📖 Read WebSocket Guide](WEBSOCKET_GUIDE.md) | [🧪 Test Page](http://localhost:8000/test_websocket.html)

### 🔍 Auto-Discovery Service
- **Intelligent search** for new free APIs
- **HuggingFace integration** for smart filtering
- **Automatic validation** and integration
- **Background scheduling** with configurable intervals

### 🛡️ Startup Validation
- **Pre-flight checks** for all critical resources
- **Network connectivity** validation
- **Provider health** verification
- **Graceful failure handling**

## 🚀 Future Features

- [ ] Queue system for heavy requests
- [ ] Redis caching
- [ ] Advanced dashboard with React/Vue
- [ ] Alerting system (Telegram/Email)
- [ ] ML-based provider selection
- [ ] Multi-tenant support
- [ ] Kubernetes deployment

## 🤝 Contributing

To contribute:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 💬 Support

For issues or questions:
- Open an issue on GitHub
- Visit the Discussions section

## 🙏 Acknowledgments

Thanks to all free API providers that made this project possible:
- CoinGecko, CoinPaprika, CoinCap
- Etherscan, BscScan and all Block Explorers
- DefiLlama, OpenSea and more
- Hugging Face for ML models

---

**Made with ❤️ for the Crypto Community**
