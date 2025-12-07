# 🚀 Extended Cryptocurrency Server - Complete Guide

## ✅ تمام Endpoints مورد نیاز کلاینت پشتیبانی می‌شوند

سرور حالا از **تمام** endpoints زیر پشتیبانی می‌کند:

---

## 📡 WebSocket Endpoints

### `/ws` - Real-time Data Streaming
✅ **WORKING** - WebSocket connection for real-time price updates

**Connection:**
```javascript
const ws = new WebSocket('wss://your-server.hf.space/ws');
```

**Subscribe to symbol:**
```json
{
  "type": "subscribe",
  "symbol": "BTC"
}
```

---

## 📊 Market Data Endpoints

### 1. `/api/market` و `/market`
✅ Get market data for multiple symbols

```bash
GET /api/market?limit=100
GET /api/market?limit=3&symbol=BTC,ETH,SOL
GET /market?limit=100
```

**Response:**
```json
{
  "data": [
    {
      "symbol": "BTC",
      "price": 50000.50,
      "change24h": 1500,
      "changePercent24h": 3.1,
      "volume24h": 25000000000,
      "high24h": 51000,
      "low24h": 49000
    }
  ],
  "count": 3
}
```

### 2. `/api/market/history`
✅ Get historical market data

```bash
GET /api/market/history?symbol=BTC/USDT&timeframe=1h&limit=200
```

### 3. `/api/market/price`
✅ Get current price

```bash
GET /api/market/price?symbol=BTC
```

### 4. `/api/ohlcv` و `/ohlcv`
✅ Get OHLCV candlestick data

```bash
GET /api/ohlcv?symbol=BTC&timeframe=1h&limit=100
GET /ohlcv?symbol=BTC&timeframe=1h&limit=100
```

**Response:**
```json
{
  "symbol": "BTC",
  "timeframe": "1h",
  "data": [
    {
      "timestamp": 1633659200000,
      "open": 50000,
      "high": 51000,
      "low": 49500,
      "close": 50500,
      "volume": 1234567
    }
  ]
}
```

### 5. `/api/stats` و `/stats`
✅ Get market statistics

```bash
GET /api/stats
GET /stats
```

**Response:**
```json
{
  "total_volume_24h": 75000000000,
  "average_change_24h": 2.5,
  "total_coins": 10,
  "top_coins": [...]
}
```

---

## 🤖 AI Endpoints

### 1. `/api/ai/signals`
✅ Get AI trading signals

```bash
GET /api/ai/signals?limit=10
```

**Response:**
```json
{
  "signals": [
    {
      "symbol": "BTC",
      "signal": "BUY",
      "strength": "strong",
      "price": 50000,
      "change_24h": 3.5,
      "confidence": 0.85
    }
  ]
}
```

### 2. `/api/ai/predict`
✅ AI price prediction

```bash
POST /api/ai/predict
{
  "symbol": "BTC",
  "timeframe": "1h"
}
```

**Response:**
```json
{
  "symbol": "BTC",
  "current_price": 50000,
  "predictions": {
    "1h": 50250,
    "4h": 51000,
    "24h": 52500
  },
  "confidence": 0.75
}
```

---

## 💼 Trading & Portfolio Endpoints

### 1. `/api/trading/portfolio` و `/api/portfolio`
✅ Get portfolio data

```bash
GET /api/trading/portfolio
GET /api/portfolio
```

**Response:**
```json
{
  "total_value": 10000.0,
  "available_balance": 5000.0,
  "positions": [
    {
      "symbol": "BTC",
      "amount": 0.1,
      "value": 5000,
      "pnl": 500,
      "pnl_percent": 10
    }
  ]
}
```

### 2. `/api/professional-risk/metrics`
✅ Professional risk metrics

```bash
GET /api/professional-risk/metrics
```

**Response:**
```json
{
  "var_95": 250.0,
  "cvar_95": 350.0,
  "sharpe_ratio": 1.5,
  "sortino_ratio": 2.0,
  "max_drawdown": -15.5,
  "win_rate": 0.65
}
```

---

## 📈 Futures Trading Endpoints

### 1. `/api/futures/positions`
✅ Get futures positions

```bash
GET /api/futures/positions
```

### 2. `/api/futures/orders`
✅ Get futures orders

```bash
GET /api/futures/orders
```

### 3. `/api/futures/balance`
✅ Get futures balance

```bash
GET /api/futures/balance
```

### 4. `/api/futures/orderbook`
✅ Get orderbook

```bash
GET /api/futures/orderbook?symbol=BTCUSDT
```

---

## 📊 Technical Analysis Endpoints

### 1. `/analysis/harmonic`
✅ Harmonic pattern analysis

```bash
GET /analysis/harmonic
```

**Response:**
```json
{
  "patterns": [
    {
      "type": "Gartley",
      "status": "forming",
      "completion": 75
    }
  ]
}
```

### 2. `/analysis/elliott`
✅ Elliott Wave analysis

```bash
GET /analysis/elliott
```

### 3. `/analysis/smc`
✅ Smart Money Concept analysis

```bash
GET /analysis/smc
```

### 4. `/analysis/sentiment`
✅ Sentiment analysis for symbol

```bash
GET /analysis/sentiment?symbol=BTC
```

**Response:**
```json
{
  "symbol": "BTC",
  "sentiment": "bullish",
  "score": 0.75,
  "change_24h": 3.5
}
```

### 5. `/analysis/whale`
✅ Whale activity analysis

```bash
GET /analysis/whale?symbol=BTC
```

**Response:**
```json
{
  "symbol": "BTC",
  "large_transactions": 15,
  "whale_sentiment": "accumulating",
  "net_flow": 1500000
}
```

---

## 🎯 Strategy & Scoring Endpoints

### 1. `/api/scoring/snapshot`
✅ Get scoring snapshot

```bash
GET /api/scoring/snapshot?symbol=BTCUSDT&tfs=15m&tfs=1h&tfs=4h
```

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "timeframes": {
    "15m": {"score": 75, "signal": "bullish"},
    "1h": {"score": 80, "signal": "bullish"},
    "4h": {"score": 70, "signal": "bullish"}
  }
}
```

### 2. `/api/entry-plan`
✅ Get entry plan

```bash
GET /api/entry-plan?symbol=BTCUSDT&accountBalance=1000&riskPercent=2
```

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "entry_price": 50000,
  "stop_loss": 49000,
  "take_profit": [51000, 52000, 53000],
  "position_size": 0.02,
  "risk_amount": 20
}
```

### 3. `/api/strategies/pipeline/run`
✅ Run strategy pipeline

```bash
POST /api/strategies/pipeline/run
```

---

## 🧠 Training & Metrics

### `/api/training-metrics`
✅ Get AI training metrics

```bash
GET /api/training-metrics
```

**Response:**
```json
{
  "accuracy": 0.85,
  "loss": 0.15,
  "epochs": 100,
  "last_trained": "2025-12-07T..."
}
```

---

## 🔍 Sentiment Analysis

### `/api/sentiment/analyze`
✅ Analyze text sentiment

```bash
POST /api/sentiment/analyze
{
  "text": "Bitcoin is surging to new highs!"
}
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

---

## 🚀 Usage Examples

### Example 1: Get Market Data for Multiple Symbols

```javascript
fetch('https://your-server.hf.space/api/market?limit=3&symbol=BTC,ETH,SOL')
  .then(res => res.json())
  .then(data => console.log(data));
```

### Example 2: Connect to WebSocket

```javascript
const ws = new WebSocket('wss://your-server.hf.space/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    symbol: 'BTC'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

### Example 3: Get AI Signals

```javascript
fetch('https://your-server.hf.space/api/ai/signals?limit=10')
  .then(res => res.json())
  .then(data => console.log(data.signals));
```

### Example 4: Get OHLCV Data

```bash
curl "https://your-server.hf.space/api/ohlcv?symbol=BTC&timeframe=1h&limit=100"
```

---

## 📋 Complete Endpoint List

### ✅ Supported (All Working):

1. ✅ `/ws` - WebSocket
2. ✅ `/api/market` & `/market`
3. ✅ `/api/market/history`
4. ✅ `/api/market/price`
5. ✅ `/api/ohlcv` & `/ohlcv`
6. ✅ `/api/stats` & `/stats`
7. ✅ `/api/ai/signals`
8. ✅ `/api/ai/predict`
9. ✅ `/api/trading/portfolio`
10. ✅ `/api/portfolio`
11. ✅ `/api/professional-risk/metrics`
12. ✅ `/api/futures/positions`
13. ✅ `/api/futures/orders`
14. ✅ `/api/futures/balance`
15. ✅ `/api/futures/orderbook`
16. ✅ `/analysis/harmonic`
17. ✅ `/analysis/elliott`
18. ✅ `/analysis/smc`
19. ✅ `/analysis/sentiment`
20. ✅ `/analysis/whale`
21. ✅ `/api/training-metrics`
22. ✅ `/api/scoring/snapshot`
23. ✅ `/api/entry-plan`
24. ✅ `/api/strategies/pipeline/run`
25. ✅ `/api/sentiment/analyze`

**Total: 25+ endpoints - ALL WORKING! ✅**

---

## 🔧 Deployment on Hugging Face Space

### 1. Create `app.py`:

```python
from crypto_server import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
```

### 2. Create `requirements.txt`:

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.25.0
pydantic>=2.4.0
websockets>=12.0
```

### 3. Upload to Hugging Face Space

The server will automatically handle all the client requests!

---

## 🎉 Success!

**تمام endpoints مورد نیاز کلاینت اکنون پشتیبانی می‌شوند!**

All 404 errors should now be resolved. The server now supports:
- ✅ All market data endpoints
- ✅ WebSocket real-time streaming
- ✅ AI prediction & signals
- ✅ Trading & portfolio
- ✅ Futures trading
- ✅ Technical analysis
- ✅ Sentiment analysis
- ✅ Risk metrics
- ✅ And more!

**The server is ready for deployment! 🚀**
