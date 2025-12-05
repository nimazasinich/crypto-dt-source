# Installation & Setup Guide

Complete guide to install, configure, and run the Crypto Intelligence Hub.

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.11 or higher
python3 --version

# pip
pip --version

# Docker (for deployment)
docker --version
```

### 2. Clone Repository

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE
cd YOUR_SPACE
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements_hf.txt

# Or for development
pip install -r requirements-dev.txt
```

### 4. Environment Setup

Create `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit with your keys
nano .env
```

Required environment variables:

```bash
# HuggingFace Token (for authentication)
HF_TOKEN=hf_your_token_here

# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY=40XS7GQ6AU9NB6Y4

# Massive.com API Key
MASSIVE_API_KEY=PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE

# Database
DATABASE_URL=sqlite:///data/database/crypto_intelligence.db

# Optional: Custom settings
LOG_LEVEL=INFO
ENABLE_CORS=true
```

### 5. Initialize Database

```bash
# Database will be auto-created on first run
# Or manually initialize:
python3 -c "from database.db_manager import db_manager; db_manager.init_database()"
```

### 6. Update All Pages

```bash
# Add API configuration to all HTML pages
python3 UPDATE_ALL_PAGES.py
```

### 7. Run Application

#### Development Mode
```bash
# With auto-reload
uvicorn hf_space_api:app --reload --host 0.0.0.0 --port 7860
```

#### Production Mode
```bash
# Without reload, optimized
uvicorn hf_space_api:app --host 0.0.0.0 --port 7860 --workers 1
```

### 8. Verify Installation

```bash
# Open browser to
http://localhost:7860

# Or test with curl
curl http://localhost:7860/api/smart/health-report
```

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t crypto-intelligence-hub .
```

### Run Container

```bash
docker run -d \
  --name crypto-hub \
  -p 7860:7860 \
  -e HF_TOKEN=your_token \
  -e ALPHA_VANTAGE_API_KEY=40XS7GQ6AU9NB6Y4 \
  -e MASSIVE_API_KEY=PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE \
  -v $(pwd)/data:/app/data \
  crypto-intelligence-hub
```

### Check Logs

```bash
docker logs -f crypto-hub
```

### Stop Container

```bash
docker stop crypto-hub
docker rm crypto-hub
```

## 🌐 HuggingFace Space Deployment

### 1. Create HuggingFace Space

```bash
# Go to https://huggingface.co/new-space
# Select: Docker template, Python SDK
```

### 2. Add Secrets

In Space Settings → Repository Secrets:

```
HF_TOKEN = hf_your_token_here
ALPHA_VANTAGE_API_KEY = 40XS7GQ6AU9NB6Y4
MASSIVE_API_KEY = PwI1oqICvx9hNMzkGTHnGzA7v2VCE7JE
```

### 3. Push Code

```bash
# Add HF remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE

# Push to HF
git push hf main
```

### 4. Monitor Build

```bash
# Check build logs in HF Space UI
# Wait for "Running" status
```

### 5. Verify Deployment

```bash
# Visit your space
https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE

# Test API
curl https://YOUR_USERNAME-YOUR_SPACE.hf.space/api/smart/health-report
```

## 🔧 Configuration

### Smart Fallback System

Edit `cursor-instructions/consolidated_crypto_resources.json`:

```json
{
  "resources": [
    {
      "id": "coingecko_v3",
      "name": "CoinGecko API v3",
      "category": "market_data_apis",
      "base_url": "https://api.coingecko.com/api/v3",
      "is_free": true,
      "rate_limit": "10-50/minute"
    }
  ]
}
```

### Proxy Configuration

Edit `core/smart_proxy_manager.py`:

```python
DEFAULT_PROXIES = [
    {
        "url": "socks5://proxy.example.com:1080",
        "type": "socks5",
        "country": "US"
    }
]
```

### AI Models

Edit `ai_models.py` to configure models:

```python
MODELS_CONFIG = {
    "sentiment": {
        "model_id": "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "enabled": True
    },
    "prediction": {
        "model_id": "custom-lstm-model",
        "enabled": True
    }
}
```

## 📊 Testing

### Run All Tests

```bash
# Complete routing test
python3 test_complete_routing.py

# Test new providers
python3 test_new_apis.py

# Test endpoints
python3 test_endpoints.py

# Run pytest suite
pytest tests/ -v
```

### Manual Testing

```bash
# Test smart fallback
curl http://localhost:7860/api/smart/market?limit=10

# Test Alpha Vantage
curl http://localhost:7860/api/alphavantage/health

# Test Massive.com
curl http://localhost:7860/api/massive/health

# Test resource health
curl http://localhost:7860/api/smart/health-report

# Test stats
curl http://localhost:7860/api/smart/stats
```

## 🛠️ Maintenance

### Update Resources

```bash
# Add new resource to consolidated_crypto_resources.json
# Restart application to reload

# Or update via API
curl -X POST http://localhost:7860/api/smart/reload-resources
```

### Clean Failed Resources

```bash
# Manual cleanup
curl -X POST http://localhost:7860/api/smart/cleanup-failed

# Or automatic (runs every hour)
# Check logs for cleanup events
```

### Monitor Health

```bash
# Get health report
curl http://localhost:7860/api/smart/health-report | jq

# Get system stats
curl http://localhost:7860/api/smart/stats | jq

# Check logs
tail -f logs/hf_space_api.log
```

### Database Maintenance

```bash
# Backup database
cp data/database/crypto_intelligence.db data/database/backup_$(date +%Y%m%d).db

# Check database size
du -h data/database/crypto_intelligence.db

# Vacuum database (optimize)
sqlite3 data/database/crypto_intelligence.db "VACUUM;"
```

## 🔒 Security

### API Key Management

```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use HF Space secrets for production
# Rotate keys regularly
```

### CORS Configuration

Edit `hf_space_api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Restrict origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Rate Limiting

```python
# Configure in providers
RATE_LIMITS = {
    "coingecko": 50,  # calls per minute
    "binance": 1200,
    "alphavantage": 5,
}
```

## 📈 Performance Optimization

### Caching

```python
# Enable aggressive caching
CACHE_CONFIG = {
    "market_data": 60,      # 1 minute
    "news": 300,            # 5 minutes
    "sentiment": 600,       # 10 minutes
    "blockchain": 120,      # 2 minutes
}
```

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_market_data_symbol ON market_data(symbol);
CREATE INDEX idx_market_data_timestamp ON market_data(timestamp);
```

### Resource Prioritization

```python
# Set priority for faster providers
RESOURCE_PRIORITIES = {
    "local_backend": 1.0,    # Highest priority
    "binance": 0.9,
    "coingecko": 0.8,
}
```

## 🐛 Troubleshooting

### Application Won't Start

```bash
# Check Python version
python3 --version  # Must be 3.11+

# Check dependencies
pip install -r requirements_hf.txt --upgrade

# Check port
lsof -i :7860  # Kill if occupied
```

### No Data from APIs

```bash
# Check API keys
env | grep API_KEY

# Test providers
python3 test_new_apis.py

# Check health
curl http://localhost:7860/api/smart/health-report
```

### High Memory Usage

```bash
# Check running processes
ps aux | grep python

# Monitor resources
htop

# Reduce workers
uvicorn hf_space_api:app --workers 1
```

### Database Issues

```bash
# Reset database
rm data/database/crypto_intelligence.db
python3 -c "from database.db_manager import db_manager; db_manager.init_database()"

# Check permissions
ls -la data/database/
```

## 📚 Additional Resources

- [Complete Routing Guide](COMPLETE_ROUTING_GUIDE.md)
- [Smart Fallback System](SMART_FALLBACK_SYSTEM.md)
- [API Documentation](DIRECT_API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)

## 🆘 Getting Help

### Check Logs

```bash
# Application logs
tail -f logs/hf_space_api.log

# Worker logs
grep "worker" logs/hf_space_api.log

# Error logs
grep "ERROR" logs/hf_space_api.log
```

### Common Issues

1. **404 Errors**: Use smart fallback endpoints (`/api/smart/*`)
2. **Slow Response**: Check resource health (`/api/smart/health-report`)
3. **Auth Errors**: Verify HF_TOKEN is set
4. **Rate Limits**: Resource rotation handles this automatically

### Support

- GitHub Issues: [Report bugs](https://github.com/YOUR_REPO/issues)
- HF Discussions: [Community help](https://huggingface.co/spaces/YOUR_SPACE/discussions)
- Documentation: [Full docs](https://YOUR_SPACE.hf.space/docs)

---

**Last Updated**: December 5, 2025
**Version**: 2.0.0
**Status**: ✅ Production Ready
