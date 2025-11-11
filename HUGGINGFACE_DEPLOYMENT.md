# 🤗 HuggingFace Spaces Deployment Guide

This guide explains how to deploy the Crypto API Monitoring System to HuggingFace Spaces.

## Overview

The application is fully optimized for HuggingFace Spaces deployment with:
- **Docker-based deployment** using the standard HF Spaces port (7860)
- **Automatic environment detection** for frontend API calls
- **HuggingFace ML integration** for crypto sentiment analysis
- **WebSocket support** for real-time data streaming
- **Persistent data storage** with SQLite

## Prerequisites

1. A HuggingFace account ([sign up here](https://huggingface.co/join))
2. Git installed on your local machine
3. Basic familiarity with Docker and HuggingFace Spaces

## Deployment Steps

### 1. Create a New Space

1. Go to [HuggingFace Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Configure your Space:
   - **Name**: `Datasourceforcryptocurrency` (or your preferred name)
   - **License**: Choose appropriate license (e.g., MIT)
   - **SDK**: Select **Docker**
   - **Visibility**: Public or Private (your choice)
4. Click "Create Space"

### 2. Clone Your Space Repository

```bash
# Clone your newly created space
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME
```

### 3. Copy Application Files

Copy all files from this repository to your Space directory:

```bash
# Copy all files (adjust paths as needed)
cp -r /path/to/crypto-dt-source/* .
```

**Essential files for HuggingFace Spaces:**
- `Dockerfile` - Docker configuration optimized for HF Spaces
- `requirements.txt` - Python dependencies including transformers
- `app.py` - Main FastAPI application
- `config.js` - Frontend configuration with environment detection
- `*.html` - UI files (index.html, hf_console.html, etc.)
- All backend directories (`api/`, `backend/`, `monitoring/`, etc.)

### 4. Configure Environment Variables (Optional but Recommended)

In your HuggingFace Space settings, add these secrets:

**Required:**
- `HUGGINGFACE_TOKEN` - Your HF token for accessing models (optional if using public models)

**Optional API Keys (for enhanced data collection):**
- `ETHERSCAN_KEY_1` - Etherscan API key
- `COINMARKETCAP_KEY_1` - CoinMarketCap API key
- `NEWSAPI_KEY` - NewsAPI key
- `CRYPTOCOMPARE_KEY` - CryptoCompare API key

**HuggingFace Configuration:**
- `ENABLE_SENTIMENT=true` - Enable sentiment analysis
- `SENTIMENT_SOCIAL_MODEL=ElKulako/cryptobert` - Social sentiment model
- `SENTIMENT_NEWS_MODEL=kk08/CryptoBERT` - News sentiment model
- `HF_REGISTRY_REFRESH_SEC=21600` - Registry refresh interval (6 hours)

### 5. Push to HuggingFace

```bash
# Add all files
git add .

# Commit changes
git commit -m "Initial deployment of Crypto API Monitor"

# Push to HuggingFace
git push
```

### 6. Wait for Build

HuggingFace Spaces will automatically:
1. Build your Docker image (takes 5-10 minutes)
2. Download required ML models
3. Start the application on port 7860
4. Run health checks

Monitor the build logs in your Space's "Logs" tab.

### 7. Access Your Application

Once deployed, your application will be available at:
```
https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
```

## Features Available in HuggingFace Spaces

### 🎯 Real-Time Dashboard
- Access the main dashboard at the root URL
- Real-time WebSocket updates for all metrics
- Provider health monitoring
- System status and analytics

### 🤗 HuggingFace Console
- Access at `/hf_console.html`
- Test HF model registry
- Run sentiment analysis
- Search crypto-related models and datasets

### 📊 API Documentation
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- API Info: `/api-info`

### 🔌 WebSocket Endpoints
All WebSocket endpoints are available for real-time data:
- `/ws` - Master WebSocket endpoint
- `/ws/market_data` - Market data updates
- `/ws/news` - News updates
- `/ws/sentiment` - Sentiment analysis updates
- `/ws/health` - Health monitoring
- `/ws/huggingface` - HF integration updates

## Local Development & Testing

### Using Docker Compose

```bash
# Build and start the application
docker-compose up --build

# Access at http://localhost:7860
```

### Using Docker Directly

```bash
# Build the image
docker build -t crypto-api-monitor .

# Run the container
docker run -p 7860:7860 \
  -e HUGGINGFACE_TOKEN=your_token \
  -e ENABLE_SENTIMENT=true \
  -v $(pwd)/data:/app/data \
  crypto-api-monitor
```

### Using Python Directly

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ENABLE_SENTIMENT=true
export HUGGINGFACE_TOKEN=your_token

# Run the application
python app.py
```

## Configuration

### Frontend Configuration (`config.js`)

The frontend automatically detects the environment:
- **HuggingFace Spaces**: Uses relative URLs with Space origin
- **Localhost**: Uses `http://localhost:7860`
- **Custom Deployment**: Uses current window origin

No manual configuration needed!

### Backend Configuration

Edit `.env` or set environment variables:

```bash
# HuggingFace
HUGGINGFACE_TOKEN=your_token_here
ENABLE_SENTIMENT=true
SENTIMENT_SOCIAL_MODEL=ElKulako/cryptobert
SENTIMENT_NEWS_MODEL=kk08/CryptoBERT
HF_REGISTRY_REFRESH_SEC=21600
HF_HTTP_TIMEOUT=8.0

# API Keys (optional)
ETHERSCAN_KEY_1=your_key
COINMARKETCAP_KEY_1=your_key
NEWSAPI_KEY=your_key
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│         HuggingFace Spaces (Docker)             │
├─────────────────────────────────────────────────┤
│                                                  │
│  Frontend (HTML/JS)                             │
│  ├── config.js (auto-detects environment)      │
│  ├── index.html (main dashboard)               │
│  └── hf_console.html (HF integration UI)       │
│                                                  │
│  Backend (FastAPI)                              │
│  ├── app.py (main application)                 │
│  ├── WebSocket Manager (real-time updates)     │
│  ├── HF Integration (sentiment analysis)       │
│  ├── Data Collectors (200+ APIs)               │
│  └── SQLite Database (persistent storage)      │
│                                                  │
│  ML Models (HuggingFace Transformers)          │
│  ├── ElKulako/cryptobert                       │
│  └── kk08/CryptoBERT                           │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Troubleshooting

### Build Fails

1. Check Docker logs in HF Spaces
2. Verify `requirements.txt` has all dependencies
3. Ensure Dockerfile uses Python 3.10
4. Check for syntax errors in Python files

### Application Won't Start

1. Check health endpoint: `https://your-space-url/health`
2. Review application logs in HF Spaces
3. Verify port 7860 is exposed in Dockerfile
4. Check environment variables are set correctly

### WebSocket Connections Fail

1. Ensure your Space URL uses HTTPS
2. WebSockets automatically upgrade to WSS on HTTPS
3. Check browser console for connection errors
4. Verify CORS settings in `app.py`

### Sentiment Analysis Not Working

1. Set `HUGGINGFACE_TOKEN` in Space secrets
2. Verify models are accessible: `ElKulako/cryptobert`, `kk08/CryptoBERT`
3. Check HF console at `/hf_console.html`
4. Review logs for model download errors

### Performance Issues

1. Increase Space hardware tier (if available)
2. Reduce number of concurrent API monitors
3. Adjust `HF_REGISTRY_REFRESH_SEC` to longer interval
4. Consider disabling sentiment analysis if not needed

## Resource Requirements

**Minimum (Free Tier):**
- 2 CPU cores
- 2GB RAM
- 1GB disk space

**Recommended:**
- 4 CPU cores
- 4GB RAM
- 2GB disk space
- For better ML model performance

## Updating Your Space

```bash
# Pull latest changes
git pull

# Make your modifications
# ...

# Commit and push
git add .
git commit -m "Update: description of changes"
git push
```

HuggingFace will automatically rebuild and redeploy.

## Security Best Practices

1. **Use HF Secrets** for sensitive data (API keys, tokens)
2. **Don't commit** `.env` files with actual keys
3. **Review API keys** permissions (read-only when possible)
4. **Monitor usage** of external APIs to avoid rate limits
5. **Keep dependencies updated** for security patches

## Advanced Configuration

### Custom ML Models

To use custom sentiment analysis models:

```bash
# Set environment variables in HF Spaces
SENTIMENT_SOCIAL_MODEL=your-username/your-model
SENTIMENT_NEWS_MODEL=your-username/another-model
```

### Custom Port (Not Recommended for HF Spaces)

HuggingFace Spaces requires port 7860. Don't change unless deploying elsewhere.

### Multiple Workers

Edit Dockerfile CMD:
```dockerfile
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "2"]
```

**Note**: More workers = more memory usage. Adjust based on Space tier.

## Support & Resources

- **HuggingFace Docs**: https://huggingface.co/docs/hub/spaces
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Transformers Docs**: https://huggingface.co/docs/transformers/
- **Project Issues**: https://github.com/nimazasinich/crypto-dt-source/issues

## License

[Specify your license here]

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting PRs.

---

**Need help?** Open an issue or contact the maintainers.

**Enjoy your crypto monitoring dashboard on HuggingFace Spaces! 🚀**
