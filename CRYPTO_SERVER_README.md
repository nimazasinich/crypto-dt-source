# Cryptocurrency Data Server

A comprehensive HTTP and WebSocket server for cryptocurrency data with real-time updates, rate limiting, and error handling.

## Features

✅ **HTTP GET Endpoints**
- `/api/market/price` - Get current price for any cryptocurrency
- `/api/market/ohlc` - Get historical OHLC candlestick data

✅ **HTTP POST Endpoints**
- `/api/sentiment/analyze` - Analyze sentiment of text (Bullish, Bearish, Neutral)

✅ **WebSocket Support**
- `/ws` - Real-time cryptocurrency price streaming
- Subscribe/unsubscribe to specific symbols
- Automatic price updates every 5 seconds

✅ **Advanced Features**
- Rate limiting (100 requests per minute per client)
- Comprehensive error handling (400, 404, 429, 502, 503, 504)
- CORS support
- Auto-reconnection logic for WebSocket clients
- Real-time data from Binance API

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements_crypto_server.txt
```

Or install manually:

```bash
pip install fastapi uvicorn httpx pydantic websockets
```

### 2. Start the Server

```bash
python crypto_server.py
```

The server will start on `http://localhost:8000` by default.

You can customize the host and port:

```bash
HOST=0.0.0.0 PORT=8080 python crypto_server.py
```

## API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Usage Examples

### 1. GET Current Price

**Request:**
```bash
curl "http://localhost:8000/api/market/price?symbol=BTC"
```

**Response:**
```json
{
  "symbol": "BTC",
  "price": 50000.50,
  "timestamp": 1633659200000,
  "source": "binance"
}
```

### 2. GET OHLC Data

**Request:**
```bash
curl "http://localhost:8000/api/market/ohlc?symbol=ETH&timeframe=1h&limit=10"
```

**Response:**
```json
{
  "symbol": "ETH",
  "timeframe": "1h",
  "ohlc": [
    {
      "timestamp": 1633659200000,
      "open": 2000.0,
      "high": 2100.0,
      "low": 1900.0,
      "close": 2050.0,
      "volume": 1234567.89
    }
  ]
}
```

**Supported Timeframes:**
- `1m` - 1 minute
- `5m` - 5 minutes
- `15m` - 15 minutes
- `30m` - 30 minutes
- `1h` - 1 hour
- `4h` - 4 hours
- `1d` - 1 day
- `1w` - 1 week

### 3. POST Sentiment Analysis

**Request:**
```bash
curl -X POST "http://localhost:8000/api/sentiment/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Bitcoin is surging! Great bullish momentum."}'
```

**Response:**
```json
{
  "sentiment": "Bullish",
  "confidence": 0.85,
  "keywords": {
    "bullish": 2,
    "bearish": 0,
    "total": 2
  }
}
```

### 4. WebSocket Connection

**Python Example:**

```python
import asyncio
import json
import websockets

async def crypto_websocket():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        # Wait for welcome message
        welcome = await websocket.recv()
        print(f"Connected: {welcome}")
        
        # Subscribe to BTC
        await websocket.send(json.dumps({
            "type": "subscribe",
            "symbol": "BTC"
        }))
        
        # Receive price updates
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data["type"] == "price_update":
                print(f"BTC Price: ${data['price']:,.2f}")

asyncio.run(crypto_websocket())
```

**JavaScript Example:**

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Connected to server');
    
    // Subscribe to BTC
    ws.send(JSON.stringify({
        type: 'subscribe',
        symbol: 'BTC'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'price_update') {
        console.log(`${data.symbol} Price: $${data.price}`);
    }
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};
```

## WebSocket Message Types

### Client → Server

**Subscribe to a symbol:**
```json
{
  "type": "subscribe",
  "symbol": "BTC"
}
```

**Unsubscribe from a symbol:**
```json
{
  "type": "unsubscribe",
  "symbol": "BTC"
}
```

**Ping (keepalive):**
```json
{
  "type": "ping"
}
```

**Get subscriptions:**
```json
{
  "type": "get_subscriptions"
}
```

### Server → Client

**Connection confirmation:**
```json
{
  "type": "connected",
  "client_id": "uuid",
  "message": "Connected to cryptocurrency data stream",
  "timestamp": "2025-12-07T..."
}
```

**Subscription confirmation:**
```json
{
  "type": "subscribed",
  "symbol": "BTC",
  "message": "Subscribed to BTC updates"
}
```

**Price update:**
```json
{
  "type": "price_update",
  "symbol": "BTC",
  "price": 50000.50,
  "timestamp": 1633659200000,
  "source": "binance"
}
```

**Error message:**
```json
{
  "type": "error",
  "error": "Error description"
}
```

## Error Handling

The server provides comprehensive error handling with appropriate HTTP status codes:

### 400 Bad Request
Invalid parameters (e.g., invalid timeframe, empty text)

```json
{
  "error": "Invalid timeframe: 2h. Must be one of: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w",
  "timestamp": "2025-12-07T..."
}
```

### 404 Not Found
Symbol not found or doesn't exist

```json
{
  "error": "Symbol not found: INVALID_SYMBOL",
  "timestamp": "2025-12-07T..."
}
```

### 429 Too Many Requests
Rate limit exceeded (100 requests per minute)

```json
{
  "error": "Rate limit exceeded",
  "detail": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

### 502 Bad Gateway
External API error

```json
{
  "error": "Binance API error: HTTP 503",
  "timestamp": "2025-12-07T..."
}
```

### 503 Service Unavailable
Service temporarily unavailable

```json
{
  "error": "Failed to fetch price data: Connection error",
  "timestamp": "2025-12-07T..."
}
```

### 504 Gateway Timeout
Request timeout

```json
{
  "error": "Request timeout - Binance API is not responding",
  "timestamp": "2025-12-07T..."
}
```

## Rate Limiting

The server implements rate limiting to prevent abuse:

- **Limit**: 100 requests per minute per client
- **Identification**: Based on client IP address
- **Response Headers**:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Unix timestamp when the rate limit resets

When rate limit is exceeded, the server returns:
- Status Code: `429 Too Many Requests`
- Retry-After: `60` seconds

## Testing

Run the comprehensive test suite:

```bash
python test_crypto_server.py
```

This will test:
- Health check endpoint
- Price fetching (multiple symbols)
- OHLC data retrieval
- Sentiment analysis
- Error handling
- Rate limiting
- WebSocket connections and streaming

## Architecture

### Components

1. **FastAPI Application**
   - Main web framework
   - Handles HTTP requests
   - Manages WebSocket connections

2. **Rate Limiter**
   - In-memory request tracking
   - Per-client rate limiting
   - Automatic cleanup of old requests

3. **WebSocket Connection Manager**
   - Manages active WebSocket connections
   - Handles subscriptions per symbol
   - Broadcasts price updates to subscribers

4. **Sentiment Analyzer**
   - Keyword-based sentiment analysis
   - Detects Bullish, Bearish, Neutral sentiment
   - Confidence scoring

5. **Market Data Fetcher**
   - Fetches real-time data from Binance API
   - Handles API errors gracefully
   - Normalizes symbol formats

6. **Background Tasks**
   - Price streaming task (updates every 5 seconds)
   - Broadcasts to subscribed WebSocket clients

### Data Flow

```
Client Request → Rate Limiter → FastAPI Endpoint → Market Data Fetcher → Binance API
                                                  ↓
                                        Format Response → Send to Client

WebSocket:
Client → Subscribe Message → Connection Manager → Background Task → Price Updates → Client
```

## Production Deployment

### Using Uvicorn

```bash
uvicorn crypto_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn with Uvicorn Workers

```bash
gunicorn crypto_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_crypto_server.txt .
RUN pip install --no-cache-dir -r requirements_crypto_server.txt

COPY crypto_server.py .

EXPOSE 8000

CMD ["uvicorn", "crypto_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t crypto-server .
docker run -p 8000:8000 crypto-server
```

## Environment Variables

- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)

## Performance Considerations

- **Rate Limiting**: Prevents server overload
- **Connection Pooling**: httpx uses connection pooling for external API calls
- **Async/Await**: All I/O operations are asynchronous
- **Background Tasks**: Price streaming runs in background without blocking requests
- **Timeout Handling**: All external API calls have timeouts (10 seconds)

## Limitations

- Rate limit: 100 requests per minute per client
- OHLC data limit: Maximum 1000 data points per request
- Sentiment analysis: Keyword-based (not AI-powered)
- Data source: Binance API only (can be extended)
- In-memory rate limiting (resets on server restart)

## Future Enhancements

- [ ] Multiple data source support (CoinGecko, Kraken, etc.)
- [ ] Redis-based rate limiting for distributed deployments
- [ ] AI-powered sentiment analysis using transformers
- [ ] Historical data caching
- [ ] User authentication and API keys
- [ ] Custom WebSocket filters and alerts
- [ ] Technical indicators (RSI, MACD, etc.)
- [ ] Real-time order book data

## Support

For issues or questions, please check:
- API Documentation: http://localhost:8000/docs
- Test suite: `python test_crypto_server.py`

## License

This server is provided as-is for educational and development purposes.

---

**Built with FastAPI, WebSockets, and Binance API**
