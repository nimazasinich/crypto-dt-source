# 📡 راهنمای کامل استفاده از API و سرویس‌ها

## 🌐 آدرس اسپیس شما

```
Production URL: https://really-amin-datasourceforcryptocurrency-2.hf.space
API Base: https://really-amin-datasourceforcryptocurrency-2.hf.space/api
WebSocket: wss://really-amin-datasourceforcryptocurrency-2.hf.space/ws
```

**⚠️ مهم**: وقتی روی Hugging Face بارگذاری شد، از آدرس بالا استفاده کنید، نه localhost!

---

## 📊 فهرست کامل سرویس‌ها

### 1️⃣ سرویس‌های داده بازار (Market Data)

#### 🔹 دریافت قیمت‌های لحظه‌ای
**Endpoint**: `GET /api/market`

**استفاده**:
```bash
# cURL
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market

# JavaScript
const response = await fetch('https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market');
const data = await response.json();
```

**پاسخ**:
```json
{
  "success": true,
  "data": [
    {
      "id": "bitcoin",
      "symbol": "btc",
      "name": "Bitcoin",
      "current_price": 43250.00,
      "market_cap": 850000000000,
      "price_change_percentage_24h": 2.5,
      "total_volume": 25000000000
    }
  ],
  "source": "CoinGecko",
  "timestamp": 1733472000000
}
```

**پارامترها** (اختیاری):
- `limit`: تعداد ارزها (پیش‌فرض: 50)
- `vs_currency`: ارز مبنا (پیش‌فرض: usd)

```bash
# مثال با پارامتر
curl "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market?limit=100&vs_currency=usd"
```

---

#### 🔹 دریافت داده‌های OHLCV (نمودار شمعی)
**Endpoint**: `GET /api/market/history`

**استفاده**:
```bash
curl "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market/history?symbol=BTCUSDT&interval=1h&limit=100"
```

**JavaScript**:
```javascript
const symbol = 'BTCUSDT';
const interval = '1h'; // 1m, 5m, 15m, 1h, 4h, 1d
const limit = 100;

const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market/history?symbol=${symbol}&interval=${interval}&limit=${limit}`
);
const data = await response.json();
```

**پاسخ**:
```json
{
  "success": true,
  "data": [
    {
      "timestamp": 1733472000000,
      "open": 43100,
      "high": 43300,
      "low": 43050,
      "close": 43250,
      "volume": 1250000000
    }
  ],
  "symbol": "BTCUSDT",
  "interval": "1h",
  "count": 100
}
```

---

#### 🔹 قیمت یک ارز خاص
**Endpoint**: `GET /api/market/price/{symbol}`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market/price/bitcoin
```

**Python**:
```python
import requests

symbol = "bitcoin"
url = f"https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market/price/{symbol}"
response = requests.get(url)
data = response.json()

print(f"{data['name']}: ${data['current_price']}")
```

---

### 2️⃣ سرویس‌های تحلیل احساسات (Sentiment Analysis)

#### 🔹 تحلیل احساسات متن
**Endpoint**: `POST /api/sentiment/analyze`

**استفاده**:
```bash
curl -X POST https://really-amin-datasourceforcryptocurrency-2.hf.space/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bitcoin is showing strong bullish momentum",
    "mode": "crypto"
  }'
```

**JavaScript**:
```javascript
const analyzeSentiment = async (text) => {
  const response = await fetch(
    'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/sentiment/analyze',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: text,
        mode: 'crypto' // crypto, financial, general
      })
    }
  );
  return await response.json();
};

const result = await analyzeSentiment('Bitcoin price surge to $50,000!');
console.log(result);
```

**پاسخ**:
```json
{
  "success": true,
  "sentiment": "positive",
  "score": 0.87,
  "confidence": 0.92,
  "label": "BULLISH",
  "model": "kk08/CryptoBERT",
  "text": "Bitcoin is showing strong bullish momentum"
}
```

**حالت‌های تحلیل** (`mode`):
- `crypto`: تحلیل مخصوص کریپتو
- `financial`: تحلیل مالی عمومی
- `general`: تحلیل عمومی

---

#### 🔹 احساسات بازار جهانی (Fear & Greed)
**Endpoint**: `GET /api/sentiment/global`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/sentiment/global
```

**پاسخ**:
```json
{
  "success": true,
  "fear_greed_index": 65,
  "sentiment": "Greed",
  "market_trend": "bullish",
  "description": "Market sentiment is greedy",
  "timestamp": 1733472000000
}
```

---

#### 🔹 احساسات یک ارز خاص
**Endpoint**: `GET /api/sentiment/asset/{symbol}`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/sentiment/asset/BTC
```

---

### 3️⃣ سرویس‌های مدل‌های هوش مصنوعی

#### 🔹 لیست تمام مدل‌ها (45+ مدل)
**Endpoint**: `GET /api/models/list`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/models/list
```

**پاسخ**:
```json
{
  "success": true,
  "models": [
    {
      "id": "crypto_sent_kk08",
      "name": "kk08/CryptoBERT",
      "category": "sentiment_crypto",
      "status": "loaded",
      "task": "sentiment-analysis"
    }
  ],
  "total": 45
}
```

---

#### 🔹 خلاصه وضعیت مدل‌ها
**Endpoint**: `GET /api/models/summary`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/models/summary
```

**پاسخ**:
```json
{
  "success": true,
  "total_models": 45,
  "loaded_models": 8,
  "failed_models": 2,
  "categories": {
    "sentiment_crypto": 8,
    "sentiment_financial": 6,
    "sentiment_social": 6,
    "summarization": 9
  }
}
```

---

#### 🔹 وضعیت مدل‌ها
**Endpoint**: `GET /api/models/status`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/models/status
```

---

### 4️⃣ سرویس‌های اخبار (News)

#### 🔹 آخرین اخبار کریپتو
**Endpoint**: `GET /api/news`

```bash
curl "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/news?limit=20"
```

**پارامترها**:
- `limit`: تعداد اخبار (پیش‌فرض: 20)
- `category`: دسته‌بندی (bitcoin, ethereum, defi, nft)

**پاسخ**:
```json
{
  "success": true,
  "news": [
    {
      "title": "Bitcoin reaches new all-time high",
      "description": "Bitcoin price surges past $50,000...",
      "url": "https://...",
      "source": "CoinDesk",
      "published_at": "2025-12-06T10:30:00Z",
      "sentiment": "positive"
    }
  ],
  "total": 20
}
```

---

#### 🔹 اخبار یک ارز خاص
**Endpoint**: `GET /api/news/{symbol}`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/news/bitcoin
```

---

### 5️⃣ سرویس‌های تحلیل تکنیکال

#### 🔹 اندیکاتورهای تکنیکال
**Endpoint**: `POST /api/technical/indicators`

```bash
curl -X POST https://really-amin-datasourceforcryptocurrency-2.hf.space/api/technical/indicators \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "interval": "1h",
    "indicators": ["RSI", "MACD", "EMA", "BB"]
  }'
```

**Python**:
```python
import requests

url = "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/technical/indicators"
payload = {
    "symbol": "BTCUSDT",
    "interval": "1h",
    "indicators": ["RSI", "MACD", "EMA", "BB"]
}

response = requests.post(url, json=payload)
data = response.json()
```

**پاسخ**:
```json
{
  "success": true,
  "symbol": "BTCUSDT",
  "indicators": {
    "RSI": 65.5,
    "MACD": {
      "value": 125.3,
      "signal": 120.1,
      "histogram": 5.2
    },
    "EMA_20": 43100,
    "BB": {
      "upper": 43500,
      "middle": 43200,
      "lower": 42900
    }
  }
}
```

---

#### 🔹 سیگنال خرید/فروش
**Endpoint**: `POST /api/technical/signals`

```bash
curl -X POST https://really-amin-datasourceforcryptocurrency-2.hf.space/api/technical/signals \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "strategy": "trend-rsi-macd"
  }'
```

**پاسخ**:
```json
{
  "success": true,
  "symbol": "BTCUSDT",
  "signal": "BUY",
  "strength": 0.85,
  "strategy": "trend-rsi-macd",
  "reasons": [
    "RSI oversold (32)",
    "MACD bullish crossover",
    "Price above EMA 200"
  ],
  "entry_price": 43250,
  "stop_loss": 42500,
  "take_profit": 44500
}
```

---

### 6️⃣ سیستم Smart Fallback (305+ منبع)

#### 🔹 داده بازار با Fallback
**Endpoint**: `GET /api/smart/market`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/smart/market
```

**ویژگی**: اگر یک API کار نکرد، خودکار از منابع دیگر می‌گیرد. **هیچوقت خطا نمی‌دهد!**

---

#### 🔹 اخبار با Fallback
**Endpoint**: `GET /api/smart/news`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/smart/news
```

---

#### 🔹 احساسات با Fallback
**Endpoint**: `GET /api/smart/sentiment`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/smart/sentiment
```

---

#### 🔹 گزارش سلامت منابع
**Endpoint**: `GET /api/smart/health-report`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/smart/health-report
```

**پاسخ**:
```json
{
  "success": true,
  "total_resources": 305,
  "healthy_resources": 287,
  "degraded_resources": 15,
  "failed_resources": 3,
  "categories": {
    "market_data_apis": 21,
    "news_apis": 15,
    "sentiment_apis": 12,
    "block_explorers": 40,
    "rpc_nodes": 24
  }
}
```

---

### 7️⃣ سرویس‌های On-Chain

#### 🔹 اطلاعات بلاکچین
**Endpoint**: `GET /api/blockchain/{chain}/info`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/blockchain/ethereum/info
```

**زنجیره‌های پشتیبانی شده**: ethereum, bitcoin, binance-smart-chain, polygon, solana

---

#### 🔹 آدرس والت
**Endpoint**: `GET /api/blockchain/{chain}/address/{address}`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/blockchain/ethereum/address/0x123...
```

---

### 8️⃣ سرویس سلامت سیستم

#### 🔹 بررسی سلامت
**Endpoint**: `GET /api/health`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/health
```

**پاسخ**:
```json
{
  "status": "healthy",
  "timestamp": 1733472000000,
  "services": {
    "database": "healthy",
    "models": "healthy",
    "workers": "healthy"
  },
  "uptime": 3600,
  "version": "2.0.0"
}
```

---

### 9️⃣ WebSocket - اتصال لحظه‌ای

#### 🔹 اتصال به WebSocket

**URL**: `wss://really-amin-datasourceforcryptocurrency-2.hf.space/ws`

**JavaScript**:
```javascript
const ws = new WebSocket('wss://really-amin-datasourceforcryptocurrency-2.hf.space/ws');

// اتصال برقرار شد
ws.onopen = () => {
  console.log('Connected to WebSocket');
  
  // Subscribe به قیمت‌ها
  ws.send(JSON.stringify({
    action: 'subscribe',
    channel: 'prices',
    symbols: ['BTCUSDT', 'ETHUSDT']
  }));
};

// دریافت پیام
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  
  if (data.channel === 'prices') {
    console.log(`${data.symbol}: $${data.price}`);
  }
};

// خطا
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// قطع اتصال
ws.onclose = () => {
  console.log('Disconnected from WebSocket');
};
```

**Python**:
```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {data}")

def on_open(ws):
    print("Connected to WebSocket")
    ws.send(json.dumps({
        'action': 'subscribe',
        'channel': 'prices',
        'symbols': ['BTCUSDT', 'ETHUSDT']
    }))

ws = websocket.WebSocketApp(
    "wss://really-amin-datasourceforcryptocurrency-2.hf.space/ws",
    on_message=on_message,
    on_open=on_open
)

ws.run_forever()
```

**کانال‌های موجود**:
- `prices` - قیمت‌های لحظه‌ای
- `news` - اخبار جدید
- `sentiment` - تغییرات احساسات
- `signals` - سیگنال‌های معاملاتی

---

### 🔟 API های Alpha Vantage

#### 🔹 قیمت‌های کریپتو
**Endpoint**: `GET /api/alphavantage/prices`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/alphavantage/prices?symbol=BTC
```

---

#### 🔹 OHLCV از Alpha Vantage
**Endpoint**: `GET /api/alphavantage/ohlcv`

```bash
curl "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/alphavantage/ohlcv?symbol=BTC&interval=daily"
```

---

### 1️⃣1️⃣ API های Massive.com

#### 🔹 اطلاعات سهام
**Endpoint**: `GET /api/massive/quotes`

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/massive/quotes?symbol=AAPL
```

---

## 📚 مثال‌های کاربردی

### مثال 1: ساخت Dashboard قیمت

```javascript
// دریافت قیمت‌های لحظه‌ای
async function updatePrices() {
  const response = await fetch(
    'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market?limit=10'
  );
  const data = await response.json();
  
  data.data.forEach(coin => {
    document.getElementById(`price-${coin.symbol}`).textContent = 
      `$${coin.current_price.toLocaleString()}`;
  });
}

// به‌روزرسانی هر 10 ثانیه
setInterval(updatePrices, 10000);
```

---

### مثال 2: تحلیل احساسات اخبار

```python
import requests

def analyze_news_sentiment():
    # دریافت اخبار
    news_url = "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/news?limit=5"
    news_response = requests.get(news_url)
    news_data = news_response.json()
    
    # تحلیل احساسات هر خبر
    sentiment_url = "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/sentiment/analyze"
    
    for article in news_data['news']:
        payload = {
            'text': article['title'] + ' ' + article['description'],
            'mode': 'crypto'
        }
        
        sentiment_response = requests.post(sentiment_url, json=payload)
        sentiment_data = sentiment_response.json()
        
        print(f"News: {article['title']}")
        print(f"Sentiment: {sentiment_data['sentiment']} ({sentiment_data['score']})")
        print("---")

analyze_news_sentiment()
```

---

### مثال 3: ربات معاملاتی ساده

```javascript
async function tradingBot() {
  const symbol = 'BTCUSDT';
  
  // دریافت قیمت
  const priceResponse = await fetch(
    `https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market/price/bitcoin`
  );
  const priceData = await priceResponse.json();
  
  // دریافت سیگنال
  const signalResponse = await fetch(
    'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/technical/signals',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbol: symbol,
        strategy: 'trend-rsi-macd'
      })
    }
  );
  const signalData = await signalResponse.json();
  
  // تحلیل احساسات
  const sentimentResponse = await fetch(
    'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/sentiment/global'
  );
  const sentimentData = await sentimentResponse.json();
  
  // تصمیم‌گیری
  if (signalData.signal === 'BUY' && 
      sentimentData.fear_greed_index > 40 &&
      signalData.strength > 0.7) {
    console.log('✅ BUY Signal!');
    console.log(`Price: $${priceData.current_price}`);
    console.log(`Entry: $${signalData.entry_price}`);
    console.log(`Stop Loss: $${signalData.stop_loss}`);
    console.log(`Take Profit: $${signalData.take_profit}`);
  }
}

// اجرا هر 5 دقیقه
setInterval(tradingBot, 5 * 60 * 1000);
```

---

### مثال 4: نظارت Portfolio

```python
import requests
import time

def monitor_portfolio(coins):
    base_url = "https://really-amin-datasourceforcryptocurrency-2.hf.space"
    
    while True:
        total_value = 0
        
        for coin_id, amount in coins.items():
            # دریافت قیمت
            price_url = f"{base_url}/api/market/price/{coin_id}"
            response = requests.get(price_url)
            data = response.json()
            
            current_price = data['current_price']
            coin_value = current_price * amount
            total_value += coin_value
            
            print(f"{data['name']}: ${current_price} x {amount} = ${coin_value:,.2f}")
        
        print(f"\nTotal Portfolio Value: ${total_value:,.2f}")
        print("=" * 50)
        
        time.sleep(60)  # هر 1 دقیقه

# Portfolio شما
my_portfolio = {
    'bitcoin': 0.5,
    'ethereum': 5,
    'solana': 100
}

monitor_portfolio(my_portfolio)
```

---

## 🔐 Authentication (اختیاری)

برای استفاده در production می‌توانید Authentication اضافه کنید:

```javascript
const headers = {
  'Authorization': 'Bearer YOUR_API_KEY',
  'Content-Type': 'application/json'
};

const response = await fetch(
  'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market',
  { headers }
);
```

---

## 📊 Rate Limits

- **Public endpoints**: 100 requests/minute
- **WebSocket**: 50 subscriptions
- **Smart endpoints**: نامحدود (با Fallback خودکار)

---

## 🆘 Error Handling

همه API ها در صورت خطا، پاسخ یکسانی می‌دهند:

```json
{
  "success": false,
  "error": "خطایی رخ داد",
  "message": "توضیحات بیشتر",
  "code": "ERROR_CODE",
  "timestamp": 1733472000000
}
```

**کدهای خطای رایج**:
- `400`: Bad Request - درخواست نادرست
- `404`: Not Found - یافت نشد
- `429`: Too Many Requests - تعداد درخواست زیاد
- `500`: Internal Server Error - خطای سرور
- `503`: Service Unavailable - سرویس در دسترس نیست

---

## 💡 نکات مهم

1. **همیشه از آدرس Space استفاده کنید**: 
   ```
   https://really-amin-datasourceforcryptocurrency-2.hf.space
   ```

2. **Smart Endpoints را ترجیح دهید** (`/api/smart/*`): 
   - خودکار Fallback دارند
   - هیچوقت خطا نمی‌دهند
   - از 305+ منبع استفاده می‌کنند

3. **WebSocket برای real-time**:
   - مصرف کمتر
   - سریع‌تر
   - داده لحظه‌ای

4. **Cache کردن**:
   - قیمت‌ها: 10-30 ثانیه
   - اخبار: 5-10 دقیقه
   - اندیکاتورها: 1-5 دقیقه

---

## 📖 مستندات بیشتر

- **Swagger UI**: https://really-amin-datasourceforcryptocurrency-2.hf.space/docs
- **ReDoc**: https://really-amin-datasourceforcryptocurrency-2.hf.space/redoc
- **GitHub**: (لینک repository شما)

---

## 🎉 خلاصه سرویس‌های موجود

### ✅ داده بازار
- قیمت‌های لحظه‌ای (100+ ارز)
- OHLCV / Candlestick (تمام timeframe ها)
- Market Cap و Volume
- 24h Changes

### ✅ تحلیل احساسات
- تحلیل متن (45+ مدل AI)
- Fear & Greed Index
- احساسات هر ارز
- احساسات اخبار

### ✅ اخبار
- 15+ منبع خبری
- تحلیل خودکار احساسات
- دسته‌بندی
- جستجو

### ✅ تحلیل تکنیکال
- 20+ اندیکاتور (RSI, MACD, BB, EMA, ...)
- سیگنال خرید/فروش
- 4 استراتژی معاملاتی
- Entry/Stop Loss/Take Profit

### ✅ On-Chain
- اطلاعات بلاکچین
- تراکنش‌ها
- آدرس‌های والت
- Gas Price

### ✅ AI Models
- 45+ مدل HuggingFace
- Sentiment Analysis
- Text Generation
- Summarization
- Trading Signals

### ✅ WebSocket
- Real-time prices
- Live news
- Signal alerts
- Portfolio tracking

### ✅ Smart Fallback
- 305+ منبع داده
- خودکار Failover
- هیچوقت خطا نمی‌دهد
- بهترین کیفیت

---

**🚀 همه چیز آماده استفاده است!**

*این سرویس‌ها رایگان و بدون محدودیت در اختیار شماست.*
