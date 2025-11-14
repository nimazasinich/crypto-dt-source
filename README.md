# Crypto-DT-Source

<div align="center">

**Production-Ready Cryptocurrency Data Aggregator**

*Real-time data collection • AI-powered analysis • Enterprise-grade security*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Quick Start](#-quick-start) • [Features](#-features) • [Documentation](#-documentation) • [فارسی](docs/persian/README_FA.md)

</div>

---

## 🚀 Quick Start

Get up and running in 3 simple steps:

```bash
# 1. Clone the repository
git clone https://github.com/nimazasinich/crypto-dt-source.git
cd crypto-dt-source

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python app.py
```

Open your browser to **http://localhost:7860** 🎉

> **Need more help?** See the [complete Quick Start guide](QUICK_START.md) or [Installation Guide](docs/deployment/INSTALL.md)

---

## ✨ Features

### 🔥 Core Capabilities

- **Real-Time Data** - Monitor 100+ cryptocurrencies with live price updates
- **AI-Powered Analysis** - Sentiment analysis using HuggingFace transformers
- **200+ Free Data Sources** - No API keys required for basic features
- **Interactive Dashboards** - 6-tab Gradio interface + 10+ HTML dashboards
- **WebSocket Streaming** - Real-time data streaming via WebSocket API
- **REST API** - 20+ endpoints for programmatic access
- **SQLite Database** - Persistent storage with automatic migrations

### 🆕 Production Features (Nov 2024)

- ✅ **Authentication & Authorization** - JWT tokens + API key management
- ✅ **Rate Limiting** - Multi-tier protection (30/min, 1000/hour)
- ✅ **Async Architecture** - 5x faster data collection
- ✅ **Database Migrations** - Version-controlled schema updates
- ✅ **Testing Suite** - pytest with 60%+ coverage
- ✅ **CI/CD Pipeline** - Automated testing & deployment
- ✅ **Code Quality Tools** - black, flake8, mypy, pylint
- ✅ **Security Scanning** - Automated vulnerability checks

> **See what's new:** [Implementation Fixes](IMPLEMENTATION_FIXES.md) • [Fixes Summary](FIXES_SUMMARY.md)

---

## 📊 Data Sources

### Price & Market Data
- **CoinGecko** - Top 100+ cryptocurrencies, market cap rankings
- **CoinCap** - Real-time prices, backup data source
- **Binance** - Trading volumes, OHLCV data
- **Kraken** - Historical price data
- **Messari** - Advanced analytics

### News & Sentiment
- **RSS Feeds** - CoinDesk, Cointelegraph, Bitcoin Magazine, Decrypt
- **CryptoPanic** - Aggregated crypto news
- **Reddit** - r/cryptocurrency, r/bitcoin, r/ethtrader
- **Alternative.me** - Fear & Greed Index

### Blockchain Data
- **Etherscan** - Ethereum blockchain (optional key)
- **BscScan** - Binance Smart Chain
- **TronScan** - Tron blockchain
- **Blockchair** - Multi-chain explorer

**All basic features work without API keys!** 🎁

---

## 🏗️ Architecture

```
crypto-dt-source/
├── 📱 UI Layer
│   ├── app.py                    # Main Gradio dashboard
│   ├── ui/                       # Modular UI components (NEW)
│   │   ├── dashboard_live.py     # Live price dashboard
│   │   ├── dashboard_charts.py   # Historical charts
│   │   ├── dashboard_news.py     # News & sentiment
│   │   └── ...
│   └── *.html                    # 10+ HTML dashboards
│
├── 🔌 API Layer
│   ├── api/
│   │   ├── endpoints.py          # 20+ REST endpoints
│   │   ├── websocket.py          # WebSocket streaming
│   │   ├── data_endpoints.py     # Data delivery
│   │   └── pool_endpoints.py     # Provider management
│   └── api_server_extended.py    # FastAPI server
│
├── 💾 Data Layer
│   ├── database.py               # SQLite manager
│   ├── database/
│   │   ├── db_manager.py         # Connection pooling
│   │   ├── migrations.py         # Schema migrations (NEW)
│   │   └── models.py             # Data models
│   └── collectors/
│       ├── market_data.py        # Price collection
│       ├── news.py               # News aggregation
│       ├── sentiment.py          # Sentiment analysis
│       └── ...
│
├── 🤖 AI Layer
│   ├── ai_models.py              # HuggingFace integration
│   └── crypto_data_bank/ai/      # Alternative AI engine
│
├── 🛠️ Utilities
│   ├── utils.py                  # General utilities
│   ├── utils/
│   │   ├── async_api_client.py   # Async HTTP client (NEW)
│   │   ├── auth.py               # Authentication (NEW)
│   │   └── rate_limiter_enhanced.py  # Rate limiting (NEW)
│   └── monitoring/
│       ├── health_monitor.py     # Health checks
│       └── scheduler.py          # Background tasks
│
├── 🧪 Testing
│   ├── tests/
│   │   ├── test_database.py      # Database tests (NEW)
│   │   ├── test_async_api_client.py  # Async tests (NEW)
│   │   └── ...
│   └── pytest.ini                # Test configuration
│
├── ⚙️ Configuration
│   ├── config.py                 # Application config
│   ├── .env.example              # Environment template
│   ├── requirements.txt          # Production deps
│   ├── requirements-dev.txt      # Dev dependencies (NEW)
│   ├── pyproject.toml            # Tool config (NEW)
│   └── .flake8                   # Linting config (NEW)
│
└── 📚 Documentation
    ├── README.md                 # This file
    ├── CHANGELOG.md              # Version history
    ├── QUICK_START.md            # Quick start guide
    ├── IMPLEMENTATION_FIXES.md   # Latest improvements (NEW)
    ├── FIXES_SUMMARY.md          # Fixes summary (NEW)
    └── docs/                     # Organized documentation (NEW)
        ├── INDEX.md              # Documentation index
        ├── deployment/           # Deployment guides
        ├── components/           # Component docs
        ├── reports/              # Analysis reports
        ├── guides/               # How-to guides
        ├── persian/              # Persian/Farsi docs
        └── archive/              # Historical docs
```

---

## 🎯 Use Cases

### For Traders
- Real-time price monitoring across 100+ coins
- AI sentiment analysis from news and social media
- Technical indicators (RSI, MACD, Moving Averages)
- Fear & Greed Index tracking

### For Developers
- REST API for building crypto applications
- WebSocket streaming for real-time updates
- 200+ free data sources aggregated
- Well-documented, modular codebase

### For Researchers
- Historical price data and analysis
- Sentiment analysis on crypto news
- Database of aggregated market data
- Export data to CSV for analysis

### For DevOps
- Docker containerization ready
- HuggingFace Spaces deployment
- Health monitoring endpoints
- Automated testing and CI/CD

---

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- 4GB+ RAM (for AI models)
- Internet connection

### Basic Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest --cov=.

# Format code
black .
isort .

# Lint
flake8 .
mypy .
```

### Production Deployment

```bash
# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
python -c "from database.migrations import auto_migrate; auto_migrate('data/database/crypto_aggregator.db')"

# Enable authentication
export ENABLE_AUTH=true
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Start application
python app.py
```

### Docker Deployment

```bash
# Build image
docker build -t crypto-dt-source .

# Run container
docker run -p 7860:7860 -v $(pwd)/data:/app/data crypto-dt-source

# Or use docker-compose
docker-compose up -d
```

> **Detailed guides:** [Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md) • [Production Guide](docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md) • [HuggingFace Spaces](docs/deployment/HUGGINGFACE_DEPLOYMENT.md)

---

## 📖 Documentation

### Getting Started
- 📘 [Quick Start Guide](QUICK_START.md) - Get running in 3 steps
- 📘 [Installation Guide](docs/deployment/INSTALL.md) - Detailed installation
- 📘 [راهنمای فارسی](docs/persian/README_FA.md) - Persian/Farsi guide

### Core Documentation
- 📗 [Implementation Fixes](IMPLEMENTATION_FIXES.md) - Latest production improvements
- 📗 [Fixes Summary](FIXES_SUMMARY.md) - Quick reference
- 📗 [Changelog](CHANGELOG.md) - Version history

### Component Documentation
- 📙 [WebSocket API](docs/components/WEBSOCKET_API_DOCUMENTATION.md) - Real-time streaming
- 📙 [Data Collectors](docs/components/COLLECTORS_README.md) - Data collection system
- 📙 [Gradio Dashboard](docs/components/GRADIO_DASHBOARD_README.md) - UI documentation
- 📙 [Backend Services](docs/components/README_BACKEND.md) - Backend architecture

### Deployment & DevOps
- 📕 [Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md) - General deployment
- 📕 [Production Guide](docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md) - Production setup
- 📕 [HuggingFace Deployment](docs/deployment/HUGGINGFACE_DEPLOYMENT.md) - Cloud deployment

### Reports & Analysis
- 📔 [Project Analysis](docs/reports/PROJECT_ANALYSIS_COMPLETE.md) - 40,600+ line analysis
- 📔 [Production Audit](docs/reports/PRODUCTION_AUDIT_COMPREHENSIVE.md) - Security audit
- 📔 [System Capabilities](docs/reports/SYSTEM_CAPABILITIES_REPORT.md) - Feature overview

### Complete Index
📚 **[Full Documentation Index](docs/INDEX.md)** - Browse all 60+ documentation files

---

## 🔐 Security & Authentication

### Authentication (Optional)

Enable authentication for production deployments:

```bash
# .env configuration
ENABLE_AUTH=true
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-password
ACCESS_TOKEN_EXPIRE_MINUTES=60
API_KEYS=key1,key2,key3
```

**Features:**
- JWT token authentication
- API key management
- Password hashing (SHA-256)
- Token expiration
- Usage tracking

> **Learn more:** [Authentication Guide](IMPLEMENTATION_FIXES.md#3-authentication--authorization-system)

### Rate Limiting

Protect your API from abuse:

- **30 requests/minute** per client
- **1,000 requests/hour** per client
- **Burst protection** up to 10 requests

> **Learn more:** [Rate Limiting Guide](IMPLEMENTATION_FIXES.md#4-enhanced-rate-limiting-system)

---

## 🧪 Testing

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_database.py -v

# Run integration tests
pytest tests/test_integration.py
```

**Test Coverage:** 60%+ (target: 80%)

> **Learn more:** [Testing Guide](IMPLEMENTATION_FIXES.md#6-comprehensive-testing-suite)

---

## 🚢 CI/CD Pipeline

Automated testing on every push:

- ✅ Code quality checks (black, flake8, mypy)
- ✅ Tests on Python 3.8, 3.9, 3.10, 3.11
- ✅ Security scanning (bandit, safety)
- ✅ Docker build verification
- ✅ Integration tests
- ✅ Performance benchmarks

> **See:** [.github/workflows/ci.yml](.github/workflows/ci.yml)

---

## 📊 Performance

### Optimizations Implemented
- ⚡ **5x faster** data collection (async parallel requests)
- ⚡ **3x faster** database queries (optimized indices)
- ⚡ **10x reduced** API calls (TTL-based caching)
- ⚡ **Better resource** utilization (async I/O)

### Benchmarks
- Data collection: ~30 seconds for 100 coins
- Database queries: <10ms average
- WebSocket latency: <100ms
- Memory usage: ~500MB (with AI models loaded)

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with tests
4. **Run** quality checks (`black . && flake8 . && pytest`)
5. **Commit** with descriptive message
6. **Push** to your branch
7. **Open** a Pull Request

**Guidelines:**
- Follow code style (black, isort)
- Add tests for new features
- Update documentation
- Check [Pull Request Checklist](docs/guides/PR_CHECKLIST.md)

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### AI Models
- [HuggingFace](https://huggingface.co/) - Transformers library
- [Cardiff NLP](https://huggingface.co/cardiffnlp) - Twitter sentiment model
- [ProsusAI](https://huggingface.co/ProsusAI) - FinBERT model
- [Facebook](https://huggingface.co/facebook) - BART summarization

### Data Sources
- [CoinGecko](https://www.coingecko.com/) - Free crypto API
- [CoinCap](https://coincap.io/) - Real-time data
- [Binance](https://www.binance.com/) - Trading data
- [Alternative.me](https://alternative.me/) - Fear & Greed Index

### Frameworks & Libraries
- [Gradio](https://gradio.app/) - Web UI framework
- [FastAPI](https://fastapi.tiangolo.com/) - REST API
- [Plotly](https://plotly.com/) - Interactive charts
- [PyTorch](https://pytorch.org/) - Deep learning

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/nimazasinich/crypto-dt-source/issues)
- **Documentation:** [docs/](docs/INDEX.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## 🗺️ Roadmap

### Short-term (Q4 2024)
- [x] Modular UI architecture
- [x] Authentication system
- [x] Rate limiting
- [x] Database migrations
- [x] Testing suite
- [x] CI/CD pipeline
- [ ] 80%+ test coverage
- [ ] GraphQL API

### Medium-term (Q1 2025)
- [ ] Microservices architecture
- [ ] Message queue (Redis/RabbitMQ)
- [ ] Database replication
- [ ] Multi-tenancy support
- [ ] Advanced ML models

### Long-term (2025)
- [ ] Kubernetes deployment
- [ ] Multi-region support
- [ ] Premium data sources
- [ ] Enterprise features
- [ ] Mobile app

---

<div align="center">

**Made with ❤️ for the crypto community**

⭐ **Star us on GitHub** if you find this project useful!

[Documentation](docs/INDEX.md) • [Quick Start](QUICK_START.md) • [فارسی](docs/persian/README_FA.md) • [Changelog](CHANGELOG.md)

</div>
