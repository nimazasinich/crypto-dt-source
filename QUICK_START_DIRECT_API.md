# Quick Start Guide - Direct API Implementation

## 🚀 Getting Started in 5 Minutes

This guide will help you get the complete cryptocurrency data API running with direct model loading and external API integration.

---

## 1️⃣ Install Dependencies

```bash
# Install all required packages
pip install fastapi uvicorn httpx transformers torch datasets feedparser pydantic
```

Or install from requirements:

```bash
pip install -r requirements.txt
```

---

## 2️⃣ Start the Server

```bash
# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     ✅ Unified Service API Server initialized
INFO:     Application startup complete.
```

---

## 3️⃣ Test the API

### Check System Status

```bash
curl http://localhost:8000/api/v1/status
```

### Get CoinGecko Prices

```bash
curl "http://localhost:8000/api/v1/coingecko/price?symbols=BTC,ETH"
```

### Get Binance Klines

```bash
curl "http://localhost:8000/api/v1/binance/klines?symbol=BTC&timeframe=1h&limit=10"
```

### Get Fear & Greed Index

```bash
curl "http://localhost:8000/api/v1/alternative/fng"
```

### Analyze Sentiment (Direct Model - NO PIPELINE)

```bash
curl -X POST "http://localhost:8000/api/v1/hf/sentiment" \
  -H "Content-Type: application/json" \
  -d '{"text": "Bitcoin is going to the moon!", "model_key": "cryptobert_elkulako"}'
```

---

## 4️⃣ Load Models and Datasets

### Load a Specific Model

```bash
curl -X POST "http://localhost:8000/api/v1/hf/models/load?model_key=cryptobert_elkulako"
```

### Load All Models

```bash
curl -X POST "http://localhost:8000/api/v1/hf/models/load-all"
```

### Get Loaded Models

```bash
curl "http://localhost:8000/api/v1/hf/models"
```

### Load a Dataset

```bash
curl -X POST "http://localhost:8000/api/v1/hf/datasets/load?dataset_key=bitcoin_btc_usdt"
```

### Get Dataset Sample

```bash
curl "http://localhost:8000/api/v1/hf/datasets/sample?dataset_key=bitcoin_btc_usdt&num_samples=5"
```

---

## 5️⃣ View Documentation

Open your browser and navigate to:

- **Swagger UI**: http://localhost:8000/docs
- **Root Info**: http://localhost:8000/

---

## 📖 Complete API Examples

### Python Examples

```python
import requests

# Get Bitcoin price
response = requests.get(
    "http://localhost:8000/api/v1/coingecko/price",
    params={"symbols": "BTC"}
)
print(response.json())

# Get Binance klines
response = requests.get(
    "http://localhost:8000/api/v1/binance/klines",
    params={"symbol": "BTC", "timeframe": "1h", "limit": 100}
)
print(response.json())

# Get Fear & Greed Index
response = requests.get("http://localhost:8000/api/v1/alternative/fng")
print(response.json())

# Analyze sentiment (NO PIPELINE)
response = requests.post(
    "http://localhost:8000/api/v1/hf/sentiment",
    json={
        "text": "Ethereum is looking bullish!",
        "model_key": "cryptobert_elkulako"
    }
)
print(response.json())

# Get Reddit posts
response = requests.get(
    "http://localhost:8000/api/v1/reddit/top",
    params={"subreddit": "cryptocurrency", "limit": 10}
)
print(response.json())

# Get RSS feed
response = requests.get(
    "http://localhost:8000/api/v1/rss/feed",
    params={"feed_name": "coindesk", "limit": 10}
)
print(response.json())
```

---

## 🔧 Configuration (Optional)

Add environment variables for enhanced features:

```bash
# .env file
NEWSAPI_KEY=your_newsapi_key
CRYPTOPANIC_TOKEN=your_cryptopanic_token
HF_API_TOKEN=your_huggingface_token
```

---

## 📊 Available Endpoints

### External APIs

| Service | Endpoint | Description |
|---------|----------|-------------|
| CoinGecko | `/api/v1/coingecko/price` | Get cryptocurrency prices |
| CoinGecko | `/api/v1/coingecko/trending` | Get trending coins |
| Binance | `/api/v1/binance/klines` | Get OHLCV candlestick data |
| Binance | `/api/v1/binance/ticker` | Get 24h ticker data |
| Alternative.me | `/api/v1/alternative/fng` | Get Fear & Greed Index |
| Reddit | `/api/v1/reddit/top` | Get top posts |
| Reddit | `/api/v1/reddit/new` | Get new posts |
| RSS | `/api/v1/rss/feed` | Get RSS feed articles |
| RSS | `/api/v1/coindesk/rss` | CoinDesk RSS feed |
| RSS | `/api/v1/cointelegraph/rss` | CoinTelegraph RSS feed |
| News | `/api/v1/news/latest` | Aggregated news |

### HuggingFace Models (NO PIPELINE)

| Endpoint | Description |
|----------|-------------|
| `/api/v1/hf/sentiment` | Sentiment analysis (direct inference) |
| `/api/v1/hf/sentiment/batch` | Batch sentiment analysis |
| `/api/v1/hf/models` | List loaded models |
| `/api/v1/hf/models/load` | Load specific model |
| `/api/v1/hf/models/load-all` | Load all models |

### HuggingFace Datasets

| Endpoint | Description |
|----------|-------------|
| `/api/v1/hf/datasets` | List loaded datasets |
| `/api/v1/hf/datasets/load` | Load specific dataset |
| `/api/v1/hf/datasets/load-all` | Load all datasets |
| `/api/v1/hf/datasets/sample` | Get dataset samples |
| `/api/v1/hf/datasets/query` | Query dataset with filters |
| `/api/v1/hf/datasets/stats` | Get dataset statistics |

---

## 🎯 Key Features

### ✅ Direct Model Loading (NO PIPELINES)

- Models loaded using `AutoModel` and `AutoTokenizer`
- Direct inference with PyTorch
- No pipeline overhead
- Full control over model inference

### ✅ External API Integration

- **CoinGecko**: Real-time cryptocurrency prices
- **Binance**: OHLCV candlestick data
- **Alternative.me**: Fear & Greed Index
- **Reddit**: Cryptocurrency discussions
- **RSS Feeds**: News from multiple sources

### ✅ Rate Limiting

- Automatic rate limiting per client IP
- Rate limit headers in responses
- Per-endpoint configurations

### ✅ Error Handling

- Comprehensive error messages
- Standard HTTP status codes
- Fallback mechanisms

---

## 🧪 Run Tests

```bash
# Install pytest
pip install pytest pytest-asyncio

# Run tests
pytest test_direct_api.py -v
```

---

## 📚 Full Documentation

For complete API documentation, see:
- **Full API Docs**: `/workspace/DIRECT_API_DOCUMENTATION.md`
- **Implementation Summary**: `/workspace/IMPLEMENTATION_SUMMARY.md`
- **Swagger UI**: http://localhost:8000/docs

---

## 🚀 Production Deployment

### Using Docker (Recommended)

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t crypto-api .
docker run -p 8000:8000 crypto-api
```

### Using Systemd

```ini
# /etc/systemd/system/crypto-api.service
[Unit]
Description=Cryptocurrency Data API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/workspace
ExecStart=/usr/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable crypto-api
sudo systemctl start crypto-api
```

---

## 🔍 Troubleshooting

### Models not loading?

Make sure you have transformers and torch installed:

```bash
pip install transformers torch
```

### External APIs failing?

Check your internet connection and API rate limits. Some APIs may require authentication.

### CUDA not available?

The system will automatically fall back to CPU. To use GPU:

```bash
pip install torch --extra-index-url https://download.pytorch.org/whl/cu118
```

---

## 📞 Support

- **Documentation**: `/workspace/DIRECT_API_DOCUMENTATION.md`
- **Swagger UI**: http://localhost:8000/docs
- **System Status**: http://localhost:8000/api/v1/status

---

## ✅ You're Ready!

Your complete cryptocurrency data API is now running with:
- ✅ Direct model loading (NO PIPELINES)
- ✅ External API integration
- ✅ Dataset loading
- ✅ Rate limiting
- ✅ Comprehensive documentation

**Happy coding! 🚀**
