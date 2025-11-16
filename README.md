# Crypto Intelligence Dashboard

> **SDK: Docker** - This application is containerized and designed to run with Docker for easy deployment and scalability.

[![Docker](https://img.shields.io/badge/SDK-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/)

A professional, production-ready cryptocurrency intelligence platform with real-time market analysis, AI-powered sentiment analysis, and comprehensive API provider monitoring.

---

## 🌟 Features

### 🎯 Core Capabilities

- **Real-time Cryptocurrency Data** - Live prices, market cap, volume, and trends
- **Natural Language Queries** - Ask questions like "Bitcoin price" or "Top 10 coins"
- **AI Sentiment Analysis** - CryptoBERT model for crypto-specific sentiment
- **Provider Monitoring** - Track 150+ API providers with health checks
- **Professional Dashboard** - Modern UI with interactive charts and visualizations
- **WebSocket Real-time Updates** - Live data synchronization every 10 seconds
- **News Aggregation** - Latest crypto news from multiple sources
- **Market Analytics** - DeFi TVL, NFT volume, gas prices, Fear & Greed Index

### 🤖 AI & Machine Learning

- **CryptoBERT Integration** - ElKulako/CryptoBERT model with authentication
- **Sentiment Analysis** - Multi-model approach (Twitter, Financial, Crypto-specific)
- **Market Trend Prediction** - Technical analysis with RSI, MA, support/resistance
- **Text Summarization** - Automatic news and report summarization

### 📊 Data Sources

- **150+ API Providers** - CoinGecko, Binance, DeFiLlama, Etherscan, and more
- **Multiple Categories**:
  - Market Data (CoinGecko, CoinCap, CryptoCom pare)
  - DeFi Protocols (DeFiLlama, Aave, Uniswap)
  - Blockchain Explorers (Etherscan, BscScan, PolygonScan)
  - NFT Marketplaces (OpenSea, Rarible, Reservoir)
  - News Sources (CoinDesk, Cointelegraph, CryptoPanic)
  - Social Media (Reddit, Twitter trends)
  - Analytics (Glassnode, IntoTheBlock, Messari)

---

## 🐳 Docker Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Using Docker (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the dashboard
open http://localhost:7860
```

### Using Pre-built Docker Image

```bash
# Pull the image
docker pull your-registry/crypto-dashboard:latest

# Run the container
docker run -d \
  -p 7860:7860 \
  -e HF_TOKEN=your_token_here \
  --name crypto-dashboard \
  your-registry/crypto-dashboard:latest

# View logs
docker logs -f crypto-dashboard
```

---

## 🚀 Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/crypto-dashboard.git
   cd crypto-dashboard
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Build and run**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Dashboard: http://localhost:7860
   - API Docs: http://localhost:7860/docs
   - Admin Panel: http://localhost:7860/admin

### Option 2: Local Development

1. **Install Python 3.10+**
   ```bash
   python --version  # Should be 3.10 or higher
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install AI models dependencies** (Optional)
   ```bash
   pip install transformers torch
   ```

4. **Set environment variables**
   ```bash
   export HF_TOKEN="your_huggingface_token"
   ```

5. **Run the application**
   ```bash
   # Start the professional dashboard
   python3 api_dashboard_backend.py
   
   # Or start the provider monitor
   python3 api_server_extended.py
   ```

### Option 3: Hugging Face Spaces

1. **Fork this repository**

2. **Create a new Space on Hugging Face**
   - Choose "Gradio" or "Docker" SDK
   - Connect your forked repository

3. **Add secrets in Space settings**
   ```
   HF_TOKEN=your_token
   ```

4. **Deploy**
   - Automatic deployment on push

---

## 📖 Usage

### Professional Dashboard

The main dashboard provides a comprehensive view of the cryptocurrency market:

```bash
# Start the professional dashboard
python3 api_dashboard_backend.py

# Access at: http://localhost:7860
```

**Features:**
- 🔍 Natural language query interface
- 📈 Real-time price charts
- 📊 Market statistics cards
- 📰 Latest crypto news
- 😊 Sentiment analysis visualization
- 💹 Top cryptocurrencies table

**Example Queries:**
```
"Bitcoin price"              → Current BTC price
"Top 10 coins"              → List top 10 cryptocurrencies
"Ethereum trend"            → ETH price trend chart
"Market sentiment"          → Bullish/bearish analysis
"DeFi TVL"                  → Total Value Locked in DeFi
"NFT volume"                → Daily NFT trading volume
"Gas prices"                → Current Ethereum gas fees
```

### Provider Monitoring Dashboard

Monitor all API providers and their health status:

```bash
# Start the provider monitor
python3 api_server_extended.py

# Access at: http://localhost:7860
```

**Features:**
- ✅ Real-time provider status (validated/unvalidated)
- 📊 Response time monitoring
- 🔄 Auto-refresh every 30 seconds
- 🏷️ Category-based filtering
- 🔍 Search functionality
- 📈 Statistics dashboard

### API Endpoints

#### REST API

```bash
# Health check
GET /api/health

# Top cryptocurrencies
GET /api/coins/top?limit=10

# Specific coin details
GET /api/coins/{symbol}

# Market statistics
GET /api/market/stats

# Latest news
GET /api/news/latest?limit=10

# Process user query
POST /api/query
{
  "query": "Bitcoin price"
}

# API providers list
GET /api/providers

# Historical price data
GET /api/charts/price/{symbol}?timeframe=7d
```

#### WebSocket

```javascript
// Connect to real-time updates
const ws = new WebSocket('ws://localhost:7860/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### CryptoBERT AI Model

Use the CryptoBERT model for crypto-specific sentiment analysis:

```python
import ai_models

# Initialize models
ai_models.initialize_models()

# Analyze sentiment
text = "Bitcoin shows strong bullish momentum"
result = ai_models.analyze_crypto_sentiment(text)

print(f"Sentiment: {result['label']}")
print(f"Confidence: {result['score']}")
print(f"Predictions: {result['predictions']}")
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ Dashboard UI │  │ Admin Panel  │  │ Charts/Viz  │  │
│  │ (HTML/JS)    │  │ (HTML/JS)    │  │ (Chart.js)  │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────┐
│                    Backend Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ FastAPI      │  │ WebSocket    │  │ Query       │  │
│  │ REST API     │  │ Manager      │  │ Parser      │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────────────┐
│                    Services Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ AI Models    │  │ Provider     │  │ Data        │  │
│  │ (CryptoBERT) │  │ Manager      │  │ Aggregator  │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ SQLite       │  │ Redis Cache  │  │ JSON Config │  │
│  │ Database     │  │ (Optional)   │  │ Files       │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────────────┐
│                External Data Sources                    │
│  CoinGecko • Binance • DeFiLlama • Etherscan           │
│  OpenSea • CryptoPanic • Reddit • Hugging Face         │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
crypto-dashboard/
├── 🐳 Docker Files
│   ├── Dockerfile                 # Main Docker configuration
│   ├── docker-compose.yml         # Docker Compose setup
│   └── .dockerignore             # Docker ignore file
│
├── 🎨 Frontend
│   ├── crypto_dashboard_pro.html  # Professional dashboard
│   ├── admin_improved.html        # Provider monitoring dashboard
│   ├── dashboard_standalone.html  # Standalone dashboard
│   └── static/                    # Static assets (CSS, JS)
│
├── 🔧 Backend
│   ├── api_dashboard_backend.py   # Main API server
│   ├── api_server_extended.py     # Provider monitoring API
│   ├── api/                       # API endpoints
│   ├── backend/                   # Business logic
│   └── monitoring/                # Monitoring services
│
├── 🤖 AI & ML
│   ├── ai_models.py               # AI models integration
│   ├── config.py                  # Configuration (HF models)
│   └── collectors/                # Data collectors
│
├── 💾 Data & Config
│   ├── providers_config_extended.json  # API providers config
│   ├── database/                  # Database modules
│   └── data/                      # Data storage
│
├── 📖 Documentation
│   ├── README.md                  # This file
│   ├── PROFESSIONAL_DASHBOARD_GUIDE.md
│   ├── QUICK_START_PROFESSIONAL.md
│   ├── CRYPTOBERT_INTEGRATION.md
│   ├── PROVIDER_DASHBOARD_GUIDE.md
│   └── docs/                      # Additional documentation
│
├── 🧪 Tests
│   ├── tests/                     # Test files
│   ├── test_cryptobert.py        # CryptoBERT tests
│   └── test_integration.py       # Integration tests
│
└── 📦 Configuration
    ├── requirements.txt           # Python dependencies
    ├── requirements-dev.txt       # Dev dependencies
    ├── .env.example              # Environment variables template
    └── pyproject.toml            # Project metadata
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Hugging Face
HF_TOKEN=your_huggingface_token_here

# API Keys (Optional - for real data)
CMC_API_KEY=your_coinmarketcap_key
ETHERSCAN_KEY=your_etherscan_key
NEWSAPI_KEY=your_newsapi_key

# Application Settings
LOG_LEVEL=INFO
PORT=7860
HOST=0.0.0.0

# Database
DATABASE_PATH=data/crypto_aggregator.db

# Cache (Optional)
REDIS_URL=redis://localhost:6379
CACHE_TTL=300

# AI Models
ENABLE_AI_MODELS=true
```

### Provider Configuration

Edit `providers_config_extended.json` to add/modify API providers:

```json
{
  "providers": {
    "your_provider_id": {
      "name": "Your Provider Name",
      "base_url": "https://api.example.com",
      "category": "market_data",
      "requires_auth": false,
      "priority": 10
    }
  }
}
```

---

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/crypto-dashboard.git
cd crypto-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Run with hot reload
uvicorn api_dashboard_backend:app --reload --port 7860
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_cryptobert.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run integration tests
python3 test_integration.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .

# Security scan
bandit -r .
```

---

## 🚢 Deployment

### Docker Production Deployment

```bash
# Build production image
docker build -t crypto-dashboard:latest .

# Run with production settings
docker run -d \
  -p 80:7860 \
  -e HF_TOKEN=${HF_TOKEN} \
  -e LOG_LEVEL=WARNING \
  --restart unless-stopped \
  --name crypto-dashboard-prod \
  crypto-dashboard:latest
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crypto-dashboard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: crypto-dashboard
  template:
    metadata:
      labels:
        app: crypto-dashboard
    spec:
      containers:
      - name: crypto-dashboard
        image: your-registry/crypto-dashboard:latest
        ports:
        - containerPort: 7860
        env:
        - name: HF_TOKEN
          valueFrom:
            secretKeyRef:
              name: crypto-secrets
              key: hf-token
```

Deploy:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### Hugging Face Spaces

1. Create `README.md` in your Space
2. Add `requirements.txt`
3. Create `app.py`:
   ```python
   from api_dashboard_backend import app
   ```
4. Set secrets in Space settings
5. Push to deploy

### AWS/GCP/Azure

See `docs/DEPLOYMENT_MASTER_GUIDE.md` for detailed cloud deployment instructions.

---

## 📊 API Documentation

### Interactive API Docs

Once the server is running, visit:

- **Swagger UI**: http://localhost:7860/docs
- **ReDoc**: http://localhost:7860/redoc

### API Examples

#### Get Top Cryptocurrencies

```bash
curl http://localhost:7860/api/coins/top?limit=10
```

Response:
```json
{
  "success": true,
  "coins": [
    {
      "name": "Bitcoin",
      "symbol": "BTC",
      "price": 43250.50,
      "change_24h": 2.34,
      "market_cap": 845000000000,
      "volume_24h": 25000000000
    }
  ],
  "count": 10
}
```

#### Process Natural Language Query

```bash
curl -X POST http://localhost:7860/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Bitcoin price"}'
```

Response:
```json
{
  "success": true,
  "type": "price",
  "coin": "Bitcoin",
  "symbol": "BTC",
  "price": 43250.50,
  "message": "Bitcoin (BTC) is currently $43,250.50"
}
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Use type hints
- Add docstrings to functions

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### Technologies Used

- **FastAPI** - Modern web framework for building APIs
- **Hugging Face Transformers** - AI model integration
- **Chart.js** - Interactive charts and visualizations
- **Docker** - Containerization platform
- **Python 3.10+** - Programming language

### Data Providers

- **CoinGecko** - Cryptocurrency market data
- **Binance** - Real-time trading data
- **DeFiLlama** - DeFi protocol analytics
- **Etherscan** - Ethereum blockchain explorer
- **OpenSea** - NFT marketplace data
- **CryptoPanic** - Crypto news aggregation

### AI Models

- **ElKulako/CryptoBERT** - Crypto-specific sentiment analysis
- **cardiffnlp/twitter-roberta-base-sentiment** - Twitter sentiment
- **ProsusAI/finbert** - Financial sentiment analysis
- **facebook/bart-large-cnn** - Text summarization

---

## 📞 Support

### Documentation

- **Quick Start**: [QUICK_START_PROFESSIONAL.md](QUICK_START_PROFESSIONAL.md)
- **Full Guide**: [PROFESSIONAL_DASHBOARD_GUIDE.md](PROFESSIONAL_DASHBOARD_GUIDE.md)
- **CryptoBERT Integration**: [CRYPTOBERT_INTEGRATION.md](docs/CRYPTOBERT_INTEGRATION.md)
- **Provider Dashboard**: [PROVIDER_DASHBOARD_GUIDE.md](PROVIDER_DASHBOARD_GUIDE.md)

### Getting Help

- 📖 Check the documentation
- 🐛 Open an issue on GitHub
- 💬 Join our community discussions
- 📧 Contact: support@example.com

### Troubleshooting

**Dashboard not loading?**
```bash
# Check if server is running
curl http://localhost:7860/api/health

# Check Docker logs
docker logs crypto-dashboard
```

**WebSocket not connecting?**
```bash
# Verify WebSocket endpoint
wscat -c ws://localhost:7860/ws
```

**AI models not loading?**
```bash
# Check HF_TOKEN is set
echo $HF_TOKEN

# Test model loading
python3 test_cryptobert.py
```

---

## 🗺️ Roadmap

### Current Version (v1.0)
- ✅ Professional dashboard
- ✅ Provider monitoring
- ✅ CryptoBERT integration
- ✅ Natural language queries
- ✅ Real-time WebSocket updates
- ✅ Docker containerization

### Planned Features (v1.1)
- [ ] Portfolio tracking
- [ ] Price alerts
- [ ] Advanced charting (candlesticks)
- [ ] Social sentiment analysis
- [ ] Multi-language support
- [ ] Mobile app

### Future Enhancements (v2.0)
- [ ] AI-powered predictions
- [ ] Trading signals
- [ ] Automated trading (with approval)
- [ ] Desktop application
- [ ] Browser extension
- [ ] API marketplace integration

---

## 📈 Statistics

- **150+ API Providers** integrated
- **4 AI Models** for sentiment analysis
- **10+ API Endpoints** available
- **Real-time Updates** every 10 seconds
- **100% Docker** compatible
- **Mobile Responsive** design

---

## 🔒 Security

### Security Features

- ✅ Environment variable configuration
- ✅ CORS protection
- ✅ Input validation
- ✅ Error handling
- ✅ Rate limiting (optional)
- ✅ API key management

### Reporting Security Issues

Please report security vulnerabilities to: security@example.com

**Do not** create public GitHub issues for security vulnerabilities.

---

## 📜 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

### Recent Updates

**v1.0.0** (2025-11-16)
- Initial release
- Professional dashboard with query system
- CryptoBERT AI model integration
- Provider monitoring dashboard
- Docker containerization
- Complete documentation

---

## 🌐 Links

- **Website**: https://your-site.com
- **Documentation**: https://docs.your-site.com
- **GitHub**: https://github.com/yourusername/crypto-dashboard
- **Docker Hub**: https://hub.docker.com/r/yourusername/crypto-dashboard
- **Hugging Face**: https://huggingface.co/spaces/yourusername/crypto-dashboard

---

## ⭐ Star History

If you find this project useful, please consider giving it a star ⭐️

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/crypto-dashboard&type=Date)](https://star-history.com/#yourusername/crypto-dashboard&Date)

---

## 📄 Citation

If you use this project in your research or work, please cite:

```bibtex
@software{crypto_dashboard_2025,
  author = {Your Name},
  title = {Crypto Intelligence Dashboard},
  year = {2025},
  url = {https://github.com/yourusername/crypto-dashboard}
}
```

---

<div align="center">

**Built with ❤️ using Docker, Python, and FastAPI**

[Report Bug](https://github.com/yourusername/crypto-dashboard/issues) · 
[Request Feature](https://github.com/yourusername/crypto-dashboard/issues) · 
[Documentation](https://docs.your-site.com)

</div>
