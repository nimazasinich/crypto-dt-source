# Installation Guide

## Quick Install

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Many data sources work without API keys. For full functionality, configure API keys:

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Start the Server

```bash
python app.py
```

Or use the launcher:

```bash
python start_server.py
```

### 4. Access the Application

- **Dashboard:** http://localhost:7860/
- **API Docs:** http://localhost:7860/docs
- **Health Check:** http://localhost:7860/health

## What Gets Created

On first run, the application automatically creates:

- `data/` - Database and persistent storage
- `logs/` - Application logs
- `data/api_monitor.db` - SQLite database

## Docker Installation

### Build and Run

```bash
docker build -t crypto-monitor .
docker run -p 7860:7860 crypto-monitor
```

### With Docker Compose

```bash
docker-compose up -d
```

## Development Setup

For development with auto-reload:

```bash
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 7860
```

## Optional: API Keys

The system works with 160+ free data sources. API keys are optional but provide:

- Higher rate limits
- Access to premium features
- Reduced latency

See `.env.example` for supported API keys:

- Market Data: CoinMarketCap, CryptoCompare, Messari
- Blockchain: Etherscan, BscScan, TronScan
- News: NewsAPI
- RPC: Infura, Alchemy
- AI/ML: HuggingFace

## Verify Installation

Check system health:

```bash
curl http://localhost:7860/health
```

View API documentation:

```bash
open http://localhost:7860/docs
```

## Troubleshooting

### Import Errors

```bash
# Make sure you're in the project directory
cd crypto-dt-source

# Install dependencies
pip install -r requirements.txt
```

### Permission Errors

```bash
# Create directories manually if needed
mkdir -p data logs
chmod 755 data logs
```

### Port Already in Use

Change the port in `app.py`:

```python
# Line ~622
port=7860  # Change to another port like 8000
```

## Next Steps

- See [QUICK_START.md](QUICK_START.md) for usage guide
- See [SERVER_INFO.md](SERVER_INFO.md) for server details
- See [README.md](README.md) for full documentation
