# 📘 راهنمای سریع API

## 🌐 آدرس پایه
```
Local:  http://localhost:7860
HF:     https://really-amin-datasourceforcryptocurrency-2.hf.space
```

---

## 📊 چه اطلاعاتی میدم؟

### 1. قیمت و بازار
- ✅ قیمت لحظه‌ای (50+ ارز)
- ✅ تغییرات 24 ساعته
- ✅ Market cap و Volume
- ✅ نمودار OHLCV (کندل استیک)
- ✅ جفت ارزها (BTC/USDT, ETH/USDT, ...)

### 2. اخبار
- ✅ آخرین اخبار کریپتو (15+ منبع)
- ✅ فیلتر بر اساس ارز
- ✅ تحلیل احساسات خبر

### 3. احساسات بازار
- ✅ شاخص ترس و طمع (0-100)
- ✅ تحلیل متن (Bullish/Bearish/Neutral)
- ✅ احساسات هر ارز

### 4. مدل‌های AI
- ✅ لیست مدل‌های هوش مصنوعی
- ✅ وضعیت و سلامت مدل‌ها

### 5. منابع و آمار
- ✅ لیست 87+ سرویس
- ✅ آمار fallback ها
- ✅ وضعیت سرویس‌ها

---

## 🚀 نحوه درخواست (HTTP)

### قیمت Top 5 ارز
```bash
GET /api/coins/top?limit=5
```
**پاسخ:**
```json
{
  "data": [
    {"name": "Bitcoin", "symbol": "BTC", "current_price": 43500, "price_change_percentage_24h": 2.3},
    {"name": "Ethereum", "symbol": "ETH", "current_price": 2280, "price_change_percentage_24h": -0.8}
  ]
}
```

### OHLCV (کندل استیک)
```bash
GET /api/ohlcv?symbol=BTC&timeframe=1h&limit=100
```
**پاسخ:**
```json
{
  "success": true,
  "data": [
    {"t": 1733356800000, "o": 43100, "h": 43500, "l": 43000, "c": 43200, "v": 1500000},
    {"t": 1733360400000, "o": 43200, "h": 43600, "l": 43100, "c": 43500, "v": 1800000}
  ],
  "source": "binance"
}
```

### آخرین اخبار
```bash
GET /api/news/latest?limit=10
```
**پاسخ:**
```json
{
  "news": [
    {"title": "Bitcoin Hits New High", "source": "CryptoPanic", "url": "https://...", "published_at": "2025-12-04T10:30:00Z"}
  ]
}
```

### شاخص ترس و طمع
```bash
GET /api/sentiment/global
```
**پاسخ:**
```json
{
  "fear_greed_index": 67,
  "sentiment": "greed",
  "classification": "greed"
}
```

### تحلیل متن (AI)
```bash
POST /api/sentiment/analyze
Content-Type: application/json

{"text": "Bitcoin is going to the moon!", "symbol": "BTC"}
```
**پاسخ:**
```json
{
  "label": "bullish",
  "score": 0.89,
  "confidence": 0.89
}
```

### لیست مدل‌های AI
```bash
GET /api/models/list
```
**پاسخ:**
```json
{
  "models": [
    {"key": "cryptobert", "name": "CryptoBERT", "task": "sentiment-analysis", "status": "demo"}
  ]
}
```

### آمار منابع
```bash
GET /api/v2/sources/statistics
```
**پاسخ:**
```json
{
  "statistics": {
    "total": 87,
    "market_data": 15,
    "news": 15,
    "sentiment": 12,
    "ohlcv": 20
  }
}
```

---

## 📋 لیست کامل Endpoint ها

| Endpoint | Method | پارامترها | خروجی |
|----------|--------|-----------|-------|
| `/api/coins/top` | GET | `limit=50` | لیست ارزها + قیمت |
| `/api/ohlcv` | GET | `symbol=BTC&timeframe=1h&limit=100` | کندل استیک (20 exchange) |
| `/api/ohlcv/{symbol}` | GET | `interval=1h&limit=100` | همان، روش دیگر |
| `/api/news/latest` | GET | `limit=10` | اخبار (15 منبع) |
| `/api/sentiment/global` | GET | `timeframe=1D` | شاخص ترس/طمع (12 منبع) |
| `/api/sentiment/analyze` | POST | `{text, symbol}` | تحلیل متن AI |
| `/api/models/list` | GET | - | لیست مدل‌های AI |
| `/api/models/status` | GET | - | وضعیت مدل‌ها |
| `/api/resources/stats` | GET | - | آمار 87+ منبع |
| `/api/v2/sources/statistics` | GET | - | آمار دقیق با fallback |
| `/api/v2/market/price/{symbol}` | GET | `show_attempts=true` | قیمت با جزئیات |
| `/api/providers` | GET | - | لیست ارائه‌دهندگان |
| `/health` | GET | - | سلامت سرور |

---

## 💡 مثال‌های عملی

### JavaScript
```javascript
// قیمت Bitcoin
const response = await fetch('/api/coins/top?limit=1');
const data = await response.json();
console.log(`BTC: $${data.coins[0].current_price}`);

// OHLCV
const ohlcv = await fetch('/api/ohlcv?symbol=BTC&timeframe=1h&limit=100');
const candles = await ohlcv.json();
console.log(`${candles.data.length} candles from ${candles.source}`);

// تحلیل احساسات
const sentiment = await fetch('/api/sentiment/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: 'Bitcoin to the moon!', symbol: 'BTC'})
});
const result = await sentiment.json();
console.log(`Sentiment: ${result.label}`);
```

### Python
```python
import requests

# قیمت
r = requests.get('http://localhost:7860/api/coins/top?limit=5')
coins = r.json()['coins']
for coin in coins:
    print(f"{coin['name']}: ${coin['current_price']}")

# OHLCV
r = requests.get('http://localhost:7860/api/ohlcv', params={
    'symbol': 'BTC', 'timeframe': '1h', 'limit': 100
})
data = r.json()
print(f"{len(data['data'])} candles from {data['source']}")

# اخبار
r = requests.get('http://localhost:7860/api/news/latest?limit=10')
news = r.json()['news']
for article in news[:3]:
    print(f"- {article['title']}")

# احساسات
r = requests.post('http://localhost:7860/api/sentiment/analyze', json={
    'text': 'Ethereum looks bullish!', 'symbol': 'ETH'
})
result = r.json()
print(f"Sentiment: {result['label']} ({result['score']:.2f})")
```

### cURL
```bash
# قیمت
curl http://localhost:7860/api/coins/top?limit=5

# OHLCV
curl "http://localhost:7860/api/ohlcv?symbol=BTC&timeframe=1h&limit=100"

# اخبار
curl http://localhost:7860/api/news/latest?limit=10

# احساسات
curl http://localhost:7860/api/sentiment/global

# تحلیل متن
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Bitcoin is bullish","symbol":"BTC"}'
```

---

## 🔄 Fallback System (چند منبع)

### هر درخواست از چند منبع تلاش می‌کند:

**قیمت (15 منبع):**
```
CoinGecko → Binance → CoinCap → CoinPaprika → ... (15 تا)
```

**OHLCV (20 منبع):**
```
Binance → CoinGecko → Kraken → Bitfinex → Coinbase → ... (20 تا)
```

**اخبار (15 منبع):**
```
CryptoPanic → CoinDesk → Cointelegraph → Reddit → ... (15 تا)
```

**احساسات (12 منبع):**
```
Alternative.me → CFGI → CoinGecko → Messari → ... (12 تا)
```

### چطور میفهمید کدوم منبع استفاده شد؟
```bash
GET /api/v2/market/price/bitcoin?show_attempts=true
```
**پاسخ نشان می‌دهد:**
```json
{
  "metadata": {
    "source_used": "CoinGecko",
    "attempts_made": 1,
    "total_available": 15
  },
  "attempts": [
    {"service_name": "CoinGecko", "success": true, "response_time_ms": 234}
  ]
}
```

---

## 📱 فرمت‌های پشتیبانی شده

### Symbol (نماد ارز)
```
bitcoin, ethereum, cardano, solana, ripple
BTC, ETH, ADA, SOL, XRP
```

### Timeframe (بازه زمانی)
```
1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w
```

### Trading Pairs (جفت ارزها)
```
BTCUSDT, ETHUSDT, SOLUSDT, ADAUSDT, ...
(در endpoint های OHLCV به صورت خودکار تبدیل می‌شود)
```

---

## 🎯 سناریوهای رایج

### سناریو 1: دریافت قیمت 10 ارز برتر
```bash
GET /api/coins/top?limit=10
```

### سناریو 2: نمودار 1 ساعته Bitcoin (100 کندل)
```bash
GET /api/ohlcv?symbol=BTC&timeframe=1h&limit=100
```

### سناریو 3: آخرین 20 خبر
```bash
GET /api/news/latest?limit=20
```

### سناریو 4: احساسات بازار
```bash
GET /api/sentiment/global
```

### سناریو 5: تحلیل متن دلخواه
```bash
POST /api/sentiment/analyze
{"text": "Solana ecosystem is growing fast", "symbol": "SOL"}
```

---

## 🔌 WebSocket (اختیاری - آخرین گزینه)

⚠️ **توجه**: WebSocket در Hugging Face Spaces غیرفعال است. از HTTP استفاده کنید.

**فقط Local:**
```javascript
// ❌ در HF کار نمی‌کند
const ws = new WebSocket('ws://localhost:7860/ws/market');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Live price:', data);
};
```

**جایگزین (HTTP Polling - همه جا کار می‌کند):**
```javascript
// ✅ در HF و Local کار می‌کند
setInterval(async () => {
  const r = await fetch('/api/coins/top?limit=5');
  const data = await r.json();
  console.log('Updated prices:', data);
}, 10000); // هر 10 ثانیه
```

---

## 📦 همه سرویس‌ها

### Market Data (15 source)
```
/api/coins/top → CoinGecko, Binance, CoinCap, CoinPaprika, CoinLore, 
Messari, DefiLlama, CoinStats, LiveCoinWatch, Mobula, CoinRanking, 
DIA, CryptoCompare, CoinDesk, Kraken
```

### OHLCV (20 source)
```
/api/ohlcv → Binance, CoinGecko, CoinPaprika, CoinCap, Kraken, 
CryptoCompare×3, Bitfinex, Coinbase, Gemini, OKX, KuCoin, Bybit, 
Gate.io, Bitstamp, MEXC, Huobi, DefiLlama, Bitget
```

### News (15 source)
```
/api/news/latest → CryptoPanic, CoinDesk, Cointelegraph, Decrypt, 
Bitcoin Magazine, Reddit, CoinStats, CryptoControl, CryptoSlate, 
NewsBTC, CryptoNews, CoinJournal, Bitcoinist, CoinCodex
```

### Sentiment (12 source)
```
/api/sentiment/global → Alternative.me, CFGI v1, CFGI Legacy, 
CoinGecko Community, Messari, LunarCrush, Santiment, CryptoQuant, 
Glassnode, TheTie, Augmento, Sentiment Investor
```

---

## ⚡ Quick Examples

### دریافت قیمت Bitcoin
```bash
curl http://localhost:7860/api/coins/top?limit=1
```

### کندل 1 ساعته Ethereum
```bash
curl "http://localhost:7860/api/ohlcv?symbol=ETH&timeframe=1h&limit=50"
```

### 5 خبر جدید
```bash
curl http://localhost:7860/api/news/latest?limit=5
```

### تحلیل متن
```bash
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Cardano has great potential","symbol":"ADA"}'
```

---

## ✅ تضمین

- ✅ همیشه پاسخ می‌دهد (با fallback)
- ✅ 10-20 منبع برای هر دسته
- ✅ HTTP فقط (بدون WebSocket اجباری)
- ✅ خودکار تشخیص محیط (Local/HF)
- ✅ Cache برای سرعت

---

**آماده استفاده ✅**

