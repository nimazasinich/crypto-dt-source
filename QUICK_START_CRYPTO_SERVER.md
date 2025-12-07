# Quick Start Guide - Cryptocurrency Server

Get your cryptocurrency data server running in **3 simple steps**!

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
pip install fastapi uvicorn httpx pydantic websockets
```

Or use the requirements file:

```bash
pip install -r requirements_crypto_server.txt
```

### Step 2: Start the Server

```bash
python crypto_server.py
```

Or use the startup script:

```bash
./start_crypto_server.sh
```

### Step 3: Test the API

Open your browser and visit:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 Usage Examples

### Test HTTP Endpoints (Terminal)

```bash
# Get BTC price
curl "http://localhost:8000/api/market/price?symbol=BTC"

# Get ETH OHLC data
curl "http://localhost:8000/api/market/ohlc?symbol=ETH&timeframe=1h&limit=10"

# Analyze sentiment
curl -X POST "http://localhost:8000/api/sentiment/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Bitcoin is bullish!"}'
```

### Test with Python Client

**HTTP Client:**
```bash
python example_http_client.py
```

Interactive commands:
- `price BTC` - Get Bitcoin price
- `ohlc ETH 1h 10` - Get Ethereum OHLC data
- `sentiment Bitcoin is going to the moon!` - Analyze sentiment
- `health` - Check server health
- `demo` - Run full demo

**WebSocket Client:**
```bash
python example_websocket_client.py BTC ETH
```

Or interactive mode:
```bash
python example_websocket_client.py
```

Commands:
- `subscribe BTC` - Subscribe to Bitcoin updates
- `unsubscribe BTC` - Unsubscribe
- `list` - Show subscriptions
- `ping` - Test connection

### Test Everything

Run the comprehensive test suite:

```bash
python test_crypto_server.py
```

This tests:
- ✅ Health check
- ✅ Price endpoints
- ✅ OHLC data
- ✅ Sentiment analysis
- ✅ Error handling
- ✅ Rate limiting
- ✅ WebSocket connections

## 🌟 Available Endpoints

### HTTP Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Server info |
| GET | `/health` | Health check |
| GET | `/api/market/price` | Get current price |
| GET | `/api/market/ohlc` | Get OHLC data |
| POST | `/api/sentiment/analyze` | Analyze sentiment |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| WS `/ws` | Real-time price streaming |

## 🎯 Common Use Cases

### 1. Monitor Multiple Cryptocurrencies

```python
import asyncio
import websockets
import json

async def monitor():
    async with websockets.connect("ws://localhost:8000/ws") as ws:
        # Subscribe to multiple symbols
        for symbol in ["BTC", "ETH", "BNB"]:
            await ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))
        
        # Receive updates
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data["type"] == "price_update":
                print(f"{data['symbol']}: ${data['price']}")

asyncio.run(monitor())
```

### 2. Get Historical Data

```python
import requests

response = requests.get(
    "http://localhost:8000/api/market/ohlc",
    params={"symbol": "BTC", "timeframe": "1d", "limit": 30}
)

data = response.json()
for candle in data["ohlc"]:
    print(f"Close: ${candle['close']}")
```

### 3. Analyze News Sentiment

```python
import requests

news_text = "Bitcoin breaks $100K! Bull run continues with strong momentum."

response = requests.post(
    "http://localhost:8000/api/sentiment/analyze",
    json={"text": news_text}
)

result = response.json()
print(f"Sentiment: {result['sentiment']}")
print(f"Confidence: {result['confidence']:.1%}")
```

## 🔧 Configuration

### Environment Variables

```bash
# Custom host and port
HOST=0.0.0.0 PORT=8080 python crypto_server.py
```

### Production Deployment

```bash
# Using Uvicorn with multiple workers
uvicorn crypto_server:app --host 0.0.0.0 --port 8000 --workers 4

# Using Gunicorn
gunicorn crypto_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## ❓ Troubleshooting

### Server won't start

1. Check if port 8000 is available:
   ```bash
   lsof -i :8000
   ```

2. Use a different port:
   ```bash
   PORT=8080 python crypto_server.py
   ```

### Dependencies missing

```bash
pip install --upgrade -r requirements_crypto_server.txt
```

### Rate limiting issues

The server limits to 100 requests per minute per client. Wait 60 seconds or restart the server.

### WebSocket connection fails

Make sure the server is running and accessible. Try the health check first:

```bash
curl http://localhost:8000/health
```

## 📚 Learn More

- **Full Documentation**: [CRYPTO_SERVER_README.md](./CRYPTO_SERVER_README.md)
- **API Docs**: http://localhost:8000/docs (when server is running)
- **Test Suite**: `python test_crypto_server.py`

## 🎉 You're Ready!

Your cryptocurrency data server is now running. You can:

1. ✅ Fetch real-time prices
2. ✅ Get historical OHLC data
3. ✅ Analyze sentiment
4. ✅ Stream live updates via WebSocket

**Happy coding! 🚀**
