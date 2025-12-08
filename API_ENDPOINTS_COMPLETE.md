# 🔌 API Endpoints - راهنمای کامل

**نسخه:** 2.0.0  
**تاریخ:** 2025-12-08  
**وضعیت:** ✅ Production Ready

---

## 🌐 Base URLs

```
Development: http://localhost:7860
Production:  https://your-space.hf.space
```

---

## 📊 Market Data APIs

### 1. دریافت قیمت تک‌ارز

```http
GET /api/prices/{symbol}
```

**پارامترها:**
- `symbol` (path): نام ارز (مثال: bitcoin, ethereum, BTC, ETH)
- `vs_currency` (query, اختیاری): ارز مقصد (پیش‌فرض: usd)

**نمونه درخواست:**
```bash
curl http://localhost:7860/api/prices/bitcoin?vs_currency=usd
```

**نمونه پاسخ:**
```json
{
  "success": true,
  "data": {
    "symbol": "bitcoin",
    "price": 43250.50,
    "change_24h": 2.5,
    "change_7d": -1.2,
    "volume_24h": 25000000000,
    "market_cap": 850000000000,
    "timestamp": "2025-12-08T10:30:00Z"
  },
  "source": "binance",
  "fallback_level": 1
}
```

### 2. دریافت قیمت چند ارز

```http
GET /api/prices/bulk
```

**پارامترها:**
- `symbols` (query): لیست نام ارزها (جدا شده با کاما)
- `vs_currency` (query, اختیاری): ارز مقصد

**نمونه:**
```bash
curl "http://localhost:7860/api/prices/bulk?symbols=bitcoin,ethereum,solana&vs_currency=usd"
```

### 3. OHLCV Data

```http
GET /api/ohlcv/{symbol}
```

**پارامترها:**
- `symbol` (path): نام ارز
- `interval` (query): بازه زمانی (1m, 5m, 15m, 1h, 4h, 1d, 1w)
- `limit` (query, اختیاری): تعداد کندل (پیش‌فرض: 100)

**نمونه:**
```bash
curl "http://localhost:7860/api/ohlcv/BTC?interval=1h&limit=24"
```

**پاسخ:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2025-12-08T09:00:00Z",
      "open": 43100.00,
      "high": 43250.50,
      "low": 43050.00,
      "close": 43200.00,
      "volume": 1250000000
    }
  ],
  "source": "binance",
  "count": 24
}
```

---

## 📰 News APIs

### 4. دریافت اخبار

```http
GET /api/news
```

**پارامترها:**
- `query` (query, اختیاری): کلیدواژه جستجو (پیش‌فرض: cryptocurrency)
- `limit` (query, اختیاری): تعداد اخبار (پیش‌فرض: 10, max: 50)
- `category` (query, اختیاری): دسته‌بندی (crypto, bitcoin, ethereum, ...)

**نمونه:**
```bash
curl "http://localhost:7860/api/news?query=bitcoin&limit=5"
```

**پاسخ:**
```json
{
  "success": true,
  "data": [
    {
      "title": "Bitcoin Reaches New All-Time High",
      "description": "Bitcoin price surges past $45,000...",
      "url": "https://...",
      "source": "CoinDesk",
      "published_at": "2025-12-08T08:30:00Z",
      "sentiment": "positive",
      "image_url": "https://..."
    }
  ],
  "source": "newsapi",
  "count": 5
}
```

### 5. News Feed (RSS)

```http
GET /api/news/rss/{source}
```

**Sources:** coindesk, cointelegraph, decrypt, bitcoinmagazine

**نمونه:**
```bash
curl http://localhost:7860/api/news/rss/coindesk
```

---

## 💭 Sentiment APIs

### 6. Fear & Greed Index

```http
GET /api/sentiment/fear-greed
```

**پاسخ:**
```json
{
  "success": true,
  "data": {
    "value": 75,
    "classification": "Extreme Greed",
    "timestamp": "2025-12-08T00:00:00Z"
  },
  "source": "alternative.me"
}
```

### 7. Social Sentiment

```http
GET /api/sentiment/social/{symbol}
```

**پارامترها:**
- `symbol` (path): نام ارز
- `platform` (query, اختیاری): twitter, reddit, all

**نمونه:**
```bash
curl http://localhost:7860/api/sentiment/social/bitcoin?platform=twitter
```

**پاسخ:**
```json
{
  "success": true,
  "data": {
    "symbol": "bitcoin",
    "sentiment_score": 0.65,
    "sentiment": "bullish",
    "mentions": 15000,
    "positive": 9750,
    "negative": 5250,
    "timestamp": "2025-12-08T10:00:00Z"
  },
  "source": "lunarcrush"
}
```

---

## 🔍 Blockchain Explorer APIs

### 8. آدرس Wallet

```http
GET /api/explorer/{chain}/address/{address}
```

**Chains:** ethereum, bsc, tron, polygon

**نمونه:**
```bash
curl http://localhost:7860/api/explorer/ethereum/address/0x...
```

**پاسخ:**
```json
{
  "success": true,
  "data": {
    "address": "0x...",
    "balance": "10.5",
    "transactions": 150,
    "tokens": [
      {
        "symbol": "USDT",
        "balance": "5000",
        "price_usd": 1.00
      }
    ]
  },
  "source": "etherscan"
}
```

### 9. تراکنش‌ها

```http
GET /api/explorer/{chain}/tx/{tx_hash}
```

**نمونه:**
```bash
curl http://localhost:7860/api/explorer/ethereum/tx/0x...
```

---

## ⛓️ On-Chain Analytics

### 10. Network Stats

```http
GET /api/onchain/{chain}/stats
```

**نمونه:**
```bash
curl http://localhost:7860/api/onchain/ethereum/stats
```

**پاسخ:**
```json
{
  "success": true,
  "data": {
    "chain": "ethereum",
    "block_height": 18500000,
    "hash_rate": "900 TH/s",
    "difficulty": "58000000000000",
    "avg_block_time": 12.5,
    "active_addresses": 450000,
    "transactions_24h": 1200000,
    "gas_price_gwei": 25
  },
  "source": "the-graph"
}
```

### 11. Token Holders

```http
GET /api/onchain/token/{chain}/{contract}/holders
```

**نمونه:**
```bash
curl http://localhost:7860/api/onchain/token/ethereum/0x.../holders?limit=10
```

---

## 🐋 Whale Tracking APIs

### 12. نقل‌وانتقالات بزرگ

```http
GET /api/whales/transactions
```

**پارامترها:**
- `min_value` (query, اختیاری): حداقل ارزش USD (پیش‌فرض: 1000000)
- `chain` (query, اختیاری): ethereum, bitcoin, all
- `limit` (query, اختیاری): تعداد (پیش‌فرض: 20)

**نمونه:**
```bash
curl "http://localhost:7860/api/whales/transactions?min_value=5000000&limit=10"
```

**پاسخ:**
```json
{
  "success": true,
  "data": [
    {
      "blockchain": "ethereum",
      "symbol": "USDT",
      "amount": 10000000,
      "amount_usd": 10000000,
      "from": "0x...",
      "to": "0x...",
      "tx_hash": "0x...",
      "timestamp": "2025-12-08T09:45:00Z"
    }
  ],
  "source": "whale-alert",
  "count": 10
}
```

---

## 🤖 AI Model APIs

### 13. Sentiment Analysis

```http
POST /api/ai/sentiment
```

**Body:**
```json
{
  "text": "Bitcoin is going to the moon! 🚀",
  "models": ["cryptobert", "finbert"],
  "ensemble": true
}
```

**پاسخ:**
```json
{
  "success": true,
  "data": {
    "sentiment": "positive",
    "confidence": 0.92,
    "score": 0.87,
    "label": "bullish",
    "models_used": ["cryptobert", "finbert"],
    "individual_results": [
      {
        "model": "cryptobert",
        "sentiment": "positive",
        "score": 0.91
      },
      {
        "model": "finbert",
        "sentiment": "positive",
        "score": 0.83
      }
    ]
  }
}
```

### 14. Text Summarization

```http
POST /api/ai/summarize
```

**Body:**
```json
{
  "text": "Long article text...",
  "max_length": 150
}
```

### 15. Trading Signal

```http
POST /api/ai/trading-signal
```

**Body:**
```json
{
  "symbol": "BTC",
  "price": 43250,
  "indicators": {
    "rsi": 65,
    "macd": 150,
    "volume": 1250000000
  }
}
```

**پاسخ:**
```json
{
  "success": true,
  "data": {
    "signal": "buy",
    "confidence": 0.75,
    "reason": "Strong uptrend with high volume",
    "entry": 43250,
    "stop_loss": 42800,
    "take_profit": 44000
  }
}
```

---

## 🌐 RPC Node APIs

### 16. Ethereum RPC

```http
POST /api/rpc/ethereum
```

**Body:**
```json
{
  "jsonrpc": "2.0",
  "method": "eth_blockNumber",
  "params": [],
  "id": 1
}
```

### 17. BSC RPC

```http
POST /api/rpc/bsc
```

### 18. TRON RPC

```http
POST /api/rpc/tron
```

---

## 📊 Monitoring & System APIs

### 19. System Status

```http
GET /api/monitoring/status
```

**پاسخ:**
```json
{
  "success": true,
  "timestamp": "2025-12-08T10:30:00Z",
  "ai_models": {
    "total": 18,
    "available": 18,
    "failed": 0,
    "loading": 0
  },
  "data_sources": {
    "total": 137,
    "active": 137,
    "inactive": 0,
    "categories": {
      "market_data": {"total": 20, "active": 20},
      "news": {"total": 15, "active": 15}
    }
  },
  "database": {
    "online": true,
    "last_check": "2025-12-08T10:30:00Z"
  },
  "stats": {
    "total_sources": 137,
    "active_sources": 137,
    "total_models": 18,
    "requests_last_minute": 50,
    "requests_last_hour": 2500
  }
}
```

### 20. Provider Health

```http
GET /api/monitoring/providers
```

**پاسخ:**
```json
{
  "success": true,
  "data": [
    {
      "id": "binance",
      "name": "Binance API",
      "category": "market_data",
      "status": "active",
      "priority": "CRITICAL",
      "success_rate": 99.8,
      "avg_response_time": 150,
      "last_success": "2025-12-08T10:29:00Z",
      "rate_limited": false
    }
  ]
}
```

### 21. Resource Statistics

```http
GET /api/monitoring/stats
```

**پاسخ:**
```json
{
  "success": true,
  "data": {
    "total_resources": 137,
    "by_category": {
      "market_data": {
        "total": 20,
        "available": 20,
        "rate_limited": 0,
        "success_rate": 99.5
      }
    },
    "by_priority": {
      "CRITICAL": 15,
      "HIGH": 35,
      "MEDIUM": 50,
      "LOW": 30,
      "EMERGENCY": 7
    }
  }
}
```

---

## 🔄 WebSocket APIs

### 22. System Monitor (Real-time)

```javascript
const ws = new WebSocket('ws://localhost:7860/api/monitoring/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('System Status:', data);
};
```

**پیام‌های دریافتی:**
```json
{
  "type": "status_update",
  "timestamp": "2025-12-08T10:30:00Z",
  "ai_models": {...},
  "data_sources": {...},
  "stats": {...}
}
```

### 23. Market Data Stream

```javascript
const ws = new WebSocket('ws://localhost:7860/ws/market_data');

ws.send(JSON.stringify({
  "action": "subscribe",
  "symbols": ["BTC", "ETH", "SOL"]
}));
```

**پیام‌ها:**
```json
{
  "type": "price_update",
  "data": {
    "symbol": "BTC",
    "price": 43250.50,
    "change_24h": 2.5,
    "timestamp": "2025-12-08T10:30:15Z"
  }
}
```

### 24. News Stream

```javascript
const ws = new WebSocket('ws://localhost:7860/ws/news');
```

**پیام‌ها:**
```json
{
  "type": "news",
  "data": {
    "title": "Breaking: Bitcoin...",
    "url": "...",
    "sentiment": "positive"
  }
}
```

### 25. AI Models Status

```javascript
const ws = new WebSocket('ws://localhost:7860/ws/huggingface');
```

---

## 🛡️ Rate Limits

| Endpoint | Rate Limit | Burst |
|----------|------------|-------|
| `/api/prices/*` | 100/min | 20 |
| `/api/ohlcv/*` | 50/min | 10 |
| `/api/news` | 30/min | 5 |
| `/api/sentiment/*` | 20/min | 5 |
| `/api/ai/*` | 10/min | 3 |
| WebSocket | Unlimited | - |

## 🔐 Authentication

### API Key (اختیاری)

```http
GET /api/prices/bitcoin
Authorization: Bearer YOUR_API_KEY
```

### Environment Variables

```bash
HF_TOKEN=your_huggingface_token
COINMARKETCAP_KEY_1=your_cmc_key
NEWSAPI_KEY=your_news_key
```

---

## 📝 Response Codes

| Code | معنی |
|------|------|
| 200 | موفق |
| 400 | درخواست نامعتبر |
| 401 | عدم احراز هویت |
| 404 | یافت نشد |
| 429 | Rate limit exceeded |
| 500 | خطای سرور |
| 503 | سرویس در دسترس نیست |

---

## 🧪 نمونه استفاده

### Python

```python
import requests

# دریافت قیمت
response = requests.get('http://localhost:7860/api/prices/bitcoin')
data = response.json()
print(f"Bitcoin: ${data['data']['price']:,.2f}")

# WebSocket
import websocket

def on_message(ws, message):
    data = json.loads(message)
    print(f"Update: {data}")

ws = websocket.WebSocketApp(
    'ws://localhost:7860/api/monitoring/ws',
    on_message=on_message
)
ws.run_forever()
```

### JavaScript

```javascript
// Fetch API
async function getBitcoin() {
  const response = await fetch('http://localhost:7860/api/prices/bitcoin');
  const data = await response.json();
  console.log(`Bitcoin: $${data.data.price.toLocaleString()}`);
}

// WebSocket
const ws = new WebSocket('ws://localhost:7860/api/monitoring/ws');

ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

### cURL

```bash
# دریافت قیمت
curl http://localhost:7860/api/prices/bitcoin

# با پارامترها
curl "http://localhost:7860/api/news?query=bitcoin&limit=5"

# POST با JSON
curl -X POST http://localhost:7860/api/ai/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "Bitcoin is bullish!", "models": ["cryptobert"]}'
```

---

## 🔧 Testing Endpoints

```bash
# Test script
./test_all_endpoints.sh

# یا manual
python3 -c "
import requests
endpoints = [
    '/api/prices/bitcoin',
    '/api/news',
    '/api/sentiment/fear-greed',
    '/api/monitoring/status'
]
for ep in endpoints:
    try:
        r = requests.get(f'http://localhost:7860{ep}', timeout=5)
        print(f'✅ {ep}: {r.status_code}')
    except Exception as e:
        print(f'❌ {ep}: {e}')
"
```

---

## 📚 مستندات بیشتر

- **راهنمای کامل:** `COMPLETE_RESOURCE_SYSTEM_FA.md`
- **مستندات Fallback:** `ULTIMATE_FALLBACK_GUIDE_FA.md`
- **شروع سریع:** `QUICK_START_RESOURCES_FA.md`

---

**✅ همه Endpoints آماده استفاده هستند!**

*آخرین به‌روزرسانی: 2025-12-08 | نسخه: 2.0.0*
