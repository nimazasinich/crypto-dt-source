# 📡 راهنمای کامل استفاده از API - فارسی

## 🌐 آدرس اسپیس شما روی هاگینگ فیس

```
آدرس اصلی: https://really-amin-datasourceforcryptocurrency-2.hf.space
API پایه: https://really-amin-datasourceforcryptocurrency-2.hf.space/api
WebSocket: wss://really-amin-datasourceforcryptocurrency-2.hf.space/ws
```

**⚠️ توجه مهم**: وقتی پروژه روی Hugging Face بارگذاری شد، دیگه از `localhost` استفاده نکنید! فقط از آدرس بالا استفاده کنید.

---

## 📊 همه سرویس‌هایی که برای کاربران فراهم کردیم

### 1️⃣ دریافت قیمت ارزهای دیجیتال

#### گرفتن قیمت تمام ارزها
```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market
```

**با JavaScript:**
```javascript
const response = await fetch('https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market');
const data = await response.json();
console.log(data);
```

**جواب برمی‌گردونه:**
```json
{
  "success": true,
  "data": [
    {
      "name": "Bitcoin",
      "symbol": "BTC",
      "current_price": 43250,
      "price_change_percentage_24h": 2.5
    }
  ]
}
```

#### گرفتن قیمت یک ارز خاص (مثلاً بیت کوین)
```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market/price/bitcoin
```

---

### 2️⃣ نمودارهای قیمت (OHLCV - شمعی)

```bash
curl "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market/history?symbol=BTCUSDT&interval=1h&limit=100"
```

**با JavaScript:**
```javascript
async function getChart() {
  const symbol = 'BTCUSDT';
  const interval = '1h'; // 1m, 5m, 15m, 1h, 4h, 1d
  
  const url = `https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market/history?symbol=${symbol}&interval=${interval}&limit=100`;
  
  const response = await fetch(url);
  const data = await response.json();
  
  // حالا می‌تونی نمودار بکشی
  data.data.forEach(candle => {
    console.log(`Open: ${candle.open}, Close: ${candle.close}`);
  });
}
```

---

### 3️⃣ تحلیل احساسات (Sentiment Analysis)

#### تحلیل یک متن
```bash
curl -X POST https://really-amin-datasourceforcryptocurrency-2.hf.space/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "بیت کوین داره خیلی خوب میره بالا",
    "mode": "crypto"
  }'
```

**با JavaScript:**
```javascript
async function analyzeSentiment(text) {
  const response = await fetch(
    'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/sentiment/analyze',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: text,
        mode: 'crypto'
      })
    }
  );
  
  const result = await response.json();
  console.log(`احساسات: ${result.sentiment}`);
  console.log(`امتیاز: ${result.score}`);
}

analyzeSentiment('Bitcoin is going to the moon!');
```

**جواب:**
```json
{
  "success": true,
  "sentiment": "positive",
  "score": 0.87,
  "label": "BULLISH"
}
```

#### احساسات کل بازار (Fear & Greed)
```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/sentiment/global
```

**جواب:**
```json
{
  "fear_greed_index": 65,
  "sentiment": "Greed",
  "market_trend": "bullish"
}
```

---

### 4️⃣ اخبار

#### گرفتن آخرین اخبار
```bash
curl "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/news?limit=20"
```

**با JavaScript:**
```javascript
async function getNews() {
  const response = await fetch(
    'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/news?limit=10'
  );
  const data = await response.json();
  
  data.news.forEach(article => {
    console.log(article.title);
    console.log(article.sentiment); // احساسات خبر
  });
}
```

#### اخبار یک ارز خاص
```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/news/bitcoin
```

---

### 5️⃣ تحلیل تکنیکال (Technical Analysis)

#### گرفتن اندیکاتورها (RSI, MACD, EMA, ...)
```bash
curl -X POST https://really-amin-datasourceforcryptocurrency-2.hf.space/api/technical/indicators \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "interval": "1h",
    "indicators": ["RSI", "MACD", "EMA", "BB"]
  }'
```

**با Python:**
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

print(f"RSI: {data['indicators']['RSI']}")
print(f"MACD: {data['indicators']['MACD']}")
```

**جواب:**
```json
{
  "success": true,
  "indicators": {
    "RSI": 65.5,
    "MACD": {
      "value": 125.3,
      "signal": 120.1
    },
    "EMA_20": 43100
  }
}
```

#### سیگنال خرید یا فروش
```bash
curl -X POST https://really-amin-datasourceforcryptocurrency-2.hf.space/api/technical/signals \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "strategy": "trend-rsi-macd"
  }'
```

**جواب:**
```json
{
  "signal": "BUY",
  "strength": 0.85,
  "reasons": [
    "RSI oversold",
    "MACD bullish crossover"
  ],
  "entry_price": 43250,
  "stop_loss": 42500,
  "take_profit": 44500
}
```

---

### 6️⃣ مدل‌های هوش مصنوعی (45+ Model)

#### لیست تمام مدل‌ها
```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/models/list
```

**جواب:**
```json
{
  "success": true,
  "models": [
    {
      "name": "kk08/CryptoBERT",
      "category": "sentiment_crypto",
      "status": "loaded"
    }
  ],
  "total": 45
}
```

#### وضعیت مدل‌ها
```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/models/status
```

---

### 7️⃣ سیستم Fallback هوشمند (305+ منبع داده)

**ویژگی خاص**: اگر یک API خراب شد، خودکار از منابع دیگه می‌گیره. **هیچوقت خطا نمیده!**

#### قیمت با Fallback
```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/smart/market
```

#### اخبار با Fallback
```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/smart/news
```

#### احساسات با Fallback
```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/smart/sentiment
```

#### گزارش سلامت 305 منبع
```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/smart/health-report
```

**جواب:**
```json
{
  "total_resources": 305,
  "healthy_resources": 287,
  "failed_resources": 3,
  "categories": {
    "market_data_apis": 21,
    "news_apis": 15,
    "block_explorers": 40
  }
}
```

---

### 8️⃣ WebSocket - داده لحظه‌ای (Real-time)

**آدرس**: `wss://really-amin-datasourceforcryptocurrency-2.hf.space/ws`

**با JavaScript:**
```javascript
const ws = new WebSocket('wss://really-amin-datasourceforcryptocurrency-2.hf.space/ws');

// وقتی وصل شد
ws.onopen = () => {
  console.log('وصل شد!');
  
  // عضویت در کانال قیمت‌ها
  ws.send(JSON.stringify({
    action: 'subscribe',
    channel: 'prices',
    symbols: ['BTCUSDT', 'ETHUSDT']
  }));
};

// دریافت پیام
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.channel === 'prices') {
    console.log(`${data.symbol}: $${data.price}`);
    // اینجا می‌تونی صفحه رو به‌روز کنی
    document.getElementById('price').textContent = data.price;
  }
};
```

**با Python:**
```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"{data['symbol']}: ${data['price']}")

def on_open(ws):
    # عضویت
    ws.send(json.dumps({
        'action': 'subscribe',
        'channel': 'prices',
        'symbols': ['BTCUSDT']
    }))

ws = websocket.WebSocketApp(
    "wss://really-amin-datasourceforcryptocurrency-2.hf.space/ws",
    on_message=on_message,
    on_open=on_open
)

ws.run_forever()
```

**کانال‌های موجود:**
- `prices` - قیمت‌های لحظه‌ای
- `news` - اخبار جدید
- `sentiment` - تغییرات احساسات
- `signals` - سیگنال‌های معاملاتی

---

### 9️⃣ اطلاعات بلاکچین (On-Chain)

#### اطلاعات یک زنجیره
```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/blockchain/ethereum/info
```

**زنجیره‌های پشتیبانی شده:**
- ethereum
- bitcoin
- binance-smart-chain
- polygon
- solana

#### اطلاعات آدرس والت
```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/blockchain/ethereum/address/0x123...
```

---

### 🔟 بررسی سلامت سیستم

```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/health
```

**جواب:**
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "models": "healthy",
    "workers": "healthy"
  },
  "uptime": 3600
}
```

---

## 💡 مثال‌های کاربردی

### مثال 1: داشبورد قیمت ساده

```html
<!DOCTYPE html>
<html>
<head>
  <title>داشبورد قیمت</title>
</head>
<body>
  <h1>قیمت ارزها</h1>
  <div id="prices"></div>
  
  <script>
    async function updatePrices() {
      const response = await fetch(
        'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market?limit=10'
      );
      const data = await response.json();
      
      const container = document.getElementById('prices');
      container.innerHTML = '';
      
      data.data.forEach(coin => {
        const div = document.createElement('div');
        div.textContent = `${coin.name}: $${coin.current_price.toLocaleString()}`;
        container.appendChild(div);
      });
    }
    
    // اجرای اولیه
    updatePrices();
    
    // به‌روزرسانی هر 10 ثانیه
    setInterval(updatePrices, 10000);
  </script>
</body>
</html>
```

---

### مثال 2: ربات تحلیلگر احساسات

```python
import requests
import time

def check_sentiment():
    # گرفتن اخبار
    news_url = "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/news?limit=5"
    news = requests.get(news_url).json()
    
    positive_count = 0
    negative_count = 0
    
    for article in news['news']:
        # تحلیل احساسات
        sentiment_url = "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/sentiment/analyze"
        payload = {
            'text': article['title'],
            'mode': 'crypto'
        }
        
        result = requests.post(sentiment_url, json=payload).json()
        
        if result['sentiment'] == 'positive':
            positive_count += 1
        else:
            negative_count += 1
        
        print(f"خبر: {article['title']}")
        print(f"احساسات: {result['sentiment']}\n")
    
    print(f"مثبت: {positive_count}, منفی: {negative_count}")
    
    if positive_count > negative_count:
        print("✅ بازار خوشبین است!")
    else:
        print("⚠️ بازار بدبین است!")

# اجرا
check_sentiment()
```

---

### مثال 3: ربات معاملاتی ساده

```javascript
async function tradingBot() {
  // گرفتن قیمت بیت کوین
  const priceResponse = await fetch(
    'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market/price/bitcoin'
  );
  const priceData = await priceResponse.json();
  
  // گرفتن سیگنال
  const signalResponse = await fetch(
    'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/technical/signals',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbol: 'BTCUSDT',
        strategy: 'trend-rsi-macd'
      })
    }
  );
  const signalData = await signalResponse.json();
  
  // گرفتن احساسات بازار
  const sentimentResponse = await fetch(
    'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/sentiment/global'
  );
  const sentimentData = await sentimentResponse.json();
  
  // تصمیم‌گیری
  console.log('=== تحلیل بازار ===');
  console.log(`قیمت: $${priceData.current_price}`);
  console.log(`سیگنال: ${signalData.signal}`);
  console.log(`قدرت: ${signalData.strength}`);
  console.log(`احساسات: ${sentimentData.sentiment}`);
  
  if (signalData.signal === 'BUY' && 
      sentimentData.fear_greed_index > 40 &&
      signalData.strength > 0.7) {
    console.log('✅ فرصت خرید خوب!');
    console.log(`نقطه ورود: $${signalData.entry_price}`);
    console.log(`حد ضرر: $${signalData.stop_loss}`);
    console.log(`حد سود: $${signalData.take_profit}`);
  } else {
    console.log('⏸️ منتظر فرصت بهتر بمانید');
  }
}

// اجرا هر 5 دقیقه
setInterval(tradingBot, 5 * 60 * 1000);
tradingBot(); // اجرای اولیه
```

---

### مثال 4: نظارت Portfolio

```python
import requests
import time

def monitor_portfolio():
    # سبد شما
    portfolio = {
        'bitcoin': 0.5,      # نصف بیت کوین
        'ethereum': 5,       # 5 اتریوم
        'solana': 100        # 100 سولانا
    }
    
    base_url = "https://really-amin-datasourceforcryptocurrency-2.hf.space"
    
    while True:
        print("\n" + "="*50)
        print("📊 ارزش سبد شما:")
        print("="*50)
        
        total_value = 0
        
        for coin_id, amount in portfolio.items():
            # گرفتن قیمت
            url = f"{base_url}/api/market/price/{coin_id}"
            response = requests.get(url)
            data = response.json()
            
            price = data['current_price']
            value = price * amount
            total_value += value
            
            print(f"{data['name']}: ${price:,.2f} x {amount} = ${value:,.2f}")
        
        print("="*50)
        print(f"💰 مجموع: ${total_value:,.2f}")
        print("="*50)
        
        # صبر 60 ثانیه
        time.sleep(60)

# اجرا
monitor_portfolio()
```

---

### مثال 5: اعلان سیگنال با WebSocket

```javascript
const ws = new WebSocket('wss://really-amin-datasourceforcryptocurrency-2.hf.space/ws');

ws.onopen = () => {
  console.log('✅ متصل شد');
  
  // عضویت در سیگنال‌ها
  ws.send(JSON.stringify({
    action: 'subscribe',
    channel: 'signals',
    symbols: ['BTCUSDT', 'ETHUSDT']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.channel === 'signals') {
    // نمایش اعلان
    if (Notification.permission === 'granted') {
      new Notification('سیگنال جدید!', {
        body: `${data.symbol}: ${data.signal} (قدرت: ${data.strength})`,
        icon: '/icon.png'
      });
    }
    
    console.log(`🔔 سیگنال: ${data.symbol} - ${data.signal}`);
  }
};
```

---

## 🔥 ویژگی‌های خاص

### 1. Smart Fallback System
- **305+ منبع داده**
- خودکار Failover
- هیچوقت خطا نمیده
- همیشه بهترین کیفیت رو میده

### 2. مدل‌های AI
- **45+ مدل** از HuggingFace
- تحلیل احساسات
- تولید متن
- خلاصه‌سازی
- سیگنال معاملاتی

### 3. Real-time با WebSocket
- قیمت لحظه‌ای
- اخبار آنی
- سیگنال‌های زنده
- بدون تأخیر

### 4. منابع داده
- **21** API داده بازار
- **15** API خبری
- **12** API احساسات
- **40** Block Explorer
- **24** RPC Node
- و خیلی بیشتر...

---

## 📖 مستندات تکمیلی

### Swagger UI (مستندات تعاملی)
```
https://really-amin-datasourceforcryptocurrency-2.hf.space/docs
```

### ReDoc (مستندات خواناتر)
```
https://really-amin-datasourceforcryptocurrency-2.hf.space/redoc
```

---

## ⚠️ نکات مهم

1. **همیشه از آدرس Space استفاده کنید**:
   ```
   https://really-amin-datasourceforcryptocurrency-2.hf.space
   ```
   نه `localhost` یا آدرس محلی!

2. **Smart Endpoints را ترجیح بدید** (`/api/smart/*`):
   - خودکار Fallback دارن
   - هیچوقت خطا نمیدن
   - از همه منابع استفاده میکنن

3. **برای Real-time از WebSocket استفاده کنید**:
   - سریع‌تر
   - مصرف کمتر
   - داده لحظه‌ای

4. **Cache کردن**:
   - قیمت‌ها: 10-30 ثانیه
   - اخبار: 5-10 دقیقه
   - اندیکاتورها: 1-5 دقیقه

5. **Error Handling**:
   همیشه خطاها رو بررسی کنید:
   ```javascript
   try {
     const response = await fetch(url);
     if (!response.ok) throw new Error('خطا');
     const data = await response.json();
   } catch (error) {
     console.error('مشکل:', error);
   }
   ```

---

## 🎯 خلاصه سرویس‌ها

✅ **داده بازار**
- قیمت لحظه‌ای 100+ ارز
- نمودار OHLCV
- Market Cap و Volume
- تغییرات 24 ساعته

✅ **احساسات**
- تحلیل متن با 45+ مدل
- Fear & Greed Index
- احساسات هر ارز
- احساسات اخبار

✅ **اخبار**
- 15+ منبع خبری
- تحلیل خودکار
- دسته‌بندی
- جستجو

✅ **تحلیل تکنیکال**
- 20+ اندیکاتور
- سیگنال خرید/فروش
- 4 استراتژی
- Entry/Stop/Target

✅ **بلاکچین**
- اطلاعات زنجیره
- تراکنش‌ها
- آدرس والت
- Gas Price

✅ **WebSocket**
- قیمت لحظه‌ای
- اخبار زنده
- سیگنال‌ها
- Portfolio Tracking

✅ **Smart Fallback**
- 305+ منبع
- Failover خودکار
- بدون خطا
- بهترین کیفیت

---

## 🚀 آماده استفاده!

**همه چیز رایگان و بدون محدودیت در اختیار شماست.**

برای شروع، فقط یکی از مثال‌های بالا رو امتحان کنید!
