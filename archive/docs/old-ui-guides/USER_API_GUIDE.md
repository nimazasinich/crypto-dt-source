# راهنمای استفاده از سرویس‌های API

## 🔗 مشخصات HuggingFace Space

**Space URL:** `https://really-amin-datasourceforcryptocurrency.hf.space`  
**WebSocket URL:** `wss://really-amin-datasourceforcryptocurrency.hf.space/ws`  
**API Base:** `https://really-amin-datasourceforcryptocurrency.hf.space/api`

---

## 📋 1. سرویس‌های جفت ارز (Trading Pairs)

### 1.1 دریافت نرخ یک جفت ارز

**Endpoint:** `GET /api/service/rate`

**مثال JavaScript:**
```javascript
// دریافت نرخ BTC/USDT
const response = await fetch(
  'https://really-amin-datasourceforcryptocurrency.hf.space/api/service/rate?pair=BTC/USDT'
);
const data = await response.json();
console.log(data);
// خروجی:
// {
//   "data": {
//     "pair": "BTC/USDT",
//     "price": 50234.12,
//     "quote": "USDT",
//     "ts": "2025-01-15T12:00:00Z"
//   },
//   "meta": {
//     "source": "hf",
//     "generated_at": "2025-01-15T12:00:00Z",
//     "cache_ttl_seconds": 10
//   }
// }
```

**مثال Python:**
```python
import requests

url = "https://really-amin-datasourceforcryptocurrency.hf.space/api/service/rate"
params = {"pair": "BTC/USDT"}

response = requests.get(url, params=params)
data = response.json()
print(f"قیمت BTC/USDT: ${data['data']['price']}")
```

**مثال cURL:**
```bash
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/service/rate?pair=BTC/USDT"
```

---

### 1.2 دریافت نرخ چند جفت ارز (Batch)

**Endpoint:** `GET /api/service/rate/batch`

**مثال JavaScript:**
```javascript
const pairs = "BTC/USDT,ETH/USDT,BNB/USDT";
const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency.hf.space/api/service/rate/batch?pairs=${pairs}`
);
const data = await response.json();
console.log(data.data); // آرایه‌ای از نرخ‌ها
```

**مثال Python:**
```python
import requests

url = "https://really-amin-datasourceforcryptocurrency.hf.space/api/service/rate/batch"
params = {"pairs": "BTC/USDT,ETH/USDT,BNB/USDT"}

response = requests.get(url, params=params)
data = response.json()

for rate in data['data']:
    print(f"{rate['pair']}: ${rate['price']}")
```

---

### 1.3 دریافت اطلاعات کامل یک جفت ارز

**Endpoint:** `GET /api/service/pair/{pair}`

**مثال JavaScript:**
```javascript
const pair = "BTC-USDT"; // یا BTC/USDT
const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency.hf.space/api/service/pair/${pair}`
);
const data = await response.json();
console.log(data);
```

---

### 1.4 دریافت داده‌های OHLC (کندل)

**Endpoint:** `GET /api/market/ohlc`

**مثال JavaScript:**
```javascript
const symbol = "BTC";
const interval = "1h"; // 1m, 5m, 15m, 1h, 4h, 1d
const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency.hf.space/api/market/ohlc?symbol=${symbol}&interval=${interval}`
);
const data = await response.json();
console.log(data.data); // آرایه‌ای از کندل‌ها
```

**مثال Python:**
```python
import requests

url = "https://really-amin-datasourceforcryptocurrency.hf.space/api/market/ohlc"
params = {
    "symbol": "BTC",
    "interval": "1h"
}

response = requests.get(url, params=params)
data = response.json()

for candle in data['data']:
    print(f"Open: {candle['open']}, High: {candle['high']}, Low: {candle['low']}, Close: {candle['close']}")
```

---

### 1.5 دریافت لیست تیکرها

**Endpoint:** `GET /api/market/tickers`

**مثال JavaScript:**
```javascript
const response = await fetch(
  'https://really-amin-datasourceforcryptocurrency.hf.space/api/market/tickers?limit=100&sort=market_cap'
);
const data = await response.json();
console.log(data.data); // لیست 100 ارز برتر
```

---

## 📰 2. سرویس‌های اخبار (News)

### 2.1 دریافت آخرین اخبار

**Endpoint:** `GET /api/news/latest`

**مثال JavaScript:**
```javascript
const symbol = "BTC";
const limit = 10;
const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency.hf.space/api/news/latest?symbol=${symbol}&limit=${limit}`
);
const data = await response.json();
console.log(data.data); // آرایه‌ای از اخبار
```

**مثال Python:**
```python
import requests

url = "https://really-amin-datasourceforcryptocurrency.hf.space/api/news/latest"
params = {
    "symbol": "BTC",
    "limit": 10
}

response = requests.get(url, params=params)
data = response.json()

for article in data['data']:
    print(f"Title: {article['title']}")
    print(f"Source: {article['source']}")
    print(f"URL: {article['url']}\n")
```

---

### 2.2 خلاصه‌سازی اخبار با AI

**Endpoint:** `POST /api/news/summarize`

**مثال JavaScript:**
```javascript
const articleText = "Bitcoin reached new all-time high..."; // متن خبر

const response = await fetch(
  'https://really-amin-datasourceforcryptocurrency.hf.space/api/news/summarize',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text: articleText
    })
  }
);
const data = await response.json();
console.log(data.summary); // خلاصه تولید شده
```

**مثال Python:**
```python
import requests

url = "https://really-amin-datasourceforcryptocurrency.hf.space/api/news/summarize"
payload = {
    "text": "Bitcoin reached new all-time high..."
}

response = requests.post(url, json=payload)
data = response.json()
print(f"خلاصه: {data['summary']}")
```

---

### 2.3 دریافت تیترهای مهم

**Endpoint:** `GET /api/news/headlines`

**مثال JavaScript:**
```javascript
const response = await fetch(
  'https://really-amin-datasourceforcryptocurrency.hf.space/api/news/headlines?limit=10'
);
const data = await response.json();
console.log(data.data);
```

---

## 🐋 3. سرویس‌های نهنگ‌ها (Whale Tracking)

### 3.1 دریافت تراکنش‌های نهنگ‌ها

**Endpoint:** `GET /api/service/whales`

**مثال JavaScript:**
```javascript
const chain = "ethereum";
const minAmount = 1000000; // حداقل 1 میلیون دلار
const limit = 50;

const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency.hf.space/api/service/whales?chain=${chain}&min_amount_usd=${minAmount}&limit=${limit}`
);
const data = await response.json();
console.log(data.data); // لیست تراکنش‌های نهنگ
```

**مثال Python:**
```python
import requests

url = "https://really-amin-datasourceforcryptocurrency.hf.space/api/service/whales"
params = {
    "chain": "ethereum",
    "min_amount_usd": 1000000,
    "limit": 50
}

response = requests.get(url, params=params)
data = response.json()

for tx in data['data']:
    print(f"از: {tx['from']}")
    print(f"به: {tx['to']}")
    print(f"مقدار: ${tx['amount_usd']:,.2f} USD")
    print(f"زمان: {tx['ts']}\n")
```

---

### 3.2 دریافت آمار نهنگ‌ها

**Endpoint:** `GET /api/whales/stats`

**مثال JavaScript:**
```javascript
const hours = 24; // آمار 24 ساعت گذشته
const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency.hf.space/api/whales/stats?hours=${hours}`
);
const data = await response.json();
console.log(data);
// خروجی شامل: تعداد تراکنش‌ها، حجم کل، میانگین و...
```

---

## 💭 4. سرویس‌های تحلیل احساسات (Sentiment)

### 4.1 تحلیل احساسات برای یک ارز

**Endpoint:** `GET /api/service/sentiment`

**مثال JavaScript:**
```javascript
const symbol = "BTC";
const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency.hf.space/api/service/sentiment?symbol=${symbol}`
);
const data = await response.json();
console.log(data);
// خروجی: score (امتیاز), label (مثبت/منفی/خنثی)
```

---

### 4.2 تحلیل احساسات متن

**Endpoint:** `POST /api/sentiment/analyze`

**مثال JavaScript:**
```javascript
const text = "Bitcoin is going to the moon! 🚀";

const response = await fetch(
  'https://really-amin-datasourceforcryptocurrency.hf.space/api/sentiment/analyze',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text: text
    })
  }
);
const data = await response.json();
console.log(`احساسات: ${data.label}, امتیاز: ${data.score}`);
```

**مثال Python:**
```python
import requests

url = "https://really-amin-datasourceforcryptocurrency.hf.space/api/sentiment/analyze"
payload = {
    "text": "Bitcoin is going to the moon! 🚀"
}

response = requests.post(url, json=payload)
data = response.json()
print(f"احساسات: {data['label']}")
print(f"امتیاز: {data['score']}")
```

---

### 4.3 شاخص ترس و طمع (Fear & Greed)

**Endpoint:** `GET /api/v1/alternative/fng`

**مثال JavaScript:**
```javascript
const response = await fetch(
  'https://really-amin-datasourceforcryptocurrency.hf.space/api/v1/alternative/fng'
);
const data = await response.json();
console.log(`شاخص ترس و طمع: ${data.value} (${data.classification})`);
```

---

## ⛓️ 5. سرویس‌های بلاکچین (Blockchain)

### 5.1 دریافت تراکنش‌های یک آدرس

**Endpoint:** `GET /api/service/onchain`

**مثال JavaScript:**
```javascript
const address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb";
const chain = "ethereum";
const limit = 50;

const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency.hf.space/api/service/onchain?address=${address}&chain=${chain}&limit=${limit}`
);
const data = await response.json();
console.log(data.data); // لیست تراکنش‌ها
```

---

### 5.2 دریافت قیمت گس

**Endpoint:** `GET /api/blockchain/gas`

**مثال JavaScript:**
```javascript
const chain = "ethereum";
const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency.hf.space/api/blockchain/gas?chain=${chain}`
);
const data = await response.json();
console.log(data);
// خروجی: slow, standard, fast (در gwei)
```

**مثال Python:**
```python
import requests

url = "https://really-amin-datasourceforcryptocurrency.hf.space/api/blockchain/gas"
params = {"chain": "ethereum"}

response = requests.get(url, params=params)
data = response.json()
print(f"Slow: {data['slow']} gwei")
print(f"Standard: {data['standard']} gwei")
print(f"Fast: {data['fast']} gwei")
```

---

### 5.3 دریافت تراکنش‌های ETH

**Endpoint:** `GET /api/v1/blockchain/eth/transactions`

**مثال JavaScript:**
```javascript
const address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb";
const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency.hf.space/api/v1/blockchain/eth/transactions?address=${address}`
);
const data = await response.json();
console.log(data.data);
```

---

### 5.4 دریافت موجودی ETH

**Endpoint:** `GET /api/v1/blockchain/eth/balance`

**مثال JavaScript:**
```javascript
const address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb";
const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency.hf.space/api/v1/blockchain/eth/balance?address=${address}`
);
const data = await response.json();
console.log(`موجودی: ${data.balance} ETH`);
```

---

## 🤖 6. سرویس‌های AI و مدل‌ها

### 6.1 پیش‌بینی با مدل AI

**Endpoint:** `POST /api/models/{model_key}/predict`

**مثال JavaScript:**
```javascript
const modelKey = "cryptobert_elkulako";
const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency.hf.space/api/models/${modelKey}/predict`,
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      input: "Bitcoin price analysis",
      context: {}
    })
  }
);
const data = await response.json();
console.log(data.prediction);
```

---

### 6.2 دریافت لیست مدل‌های موجود

**Endpoint:** `GET /api/models/list`

**مثال JavaScript:**
```javascript
const response = await fetch(
  'https://really-amin-datasourceforcryptocurrency.hf.space/api/models/list'
);
const data = await response.json();
console.log(data.models); // لیست مدل‌های موجود
```

---

## 📊 7. سرویس‌های عمومی

### 7.1 وضعیت کلی بازار

**Endpoint:** `GET /api/service/market-status`

**مثال JavaScript:**
```javascript
const response = await fetch(
  'https://really-amin-datasourceforcryptocurrency.hf.space/api/service/market-status'
);
const data = await response.json();
console.log(data);
// خروجی: حجم کل بازار، تعداد ارزها، تغییرات و...
```

---

### 7.2 10 ارز برتر

**Endpoint:** `GET /api/service/top`

**مثال JavaScript:**
```javascript
const n = 10; // یا 50
const response = await fetch(
  `https://really-amin-datasourceforcryptocurrency.hf.space/api/service/top?n=${n}`
);
const data = await response.json();
console.log(data.data); // لیست 10 ارز برتر
```

---

### 7.3 سلامت سیستم

**Endpoint:** `GET /api/health`

**مثال JavaScript:**
```javascript
const response = await fetch(
  'https://really-amin-datasourceforcryptocurrency.hf.space/api/health'
);
const data = await response.json();
console.log(data.status); // "healthy" یا "degraded"
```

---

### 7.4 سرویس عمومی (Generic Query)

**Endpoint:** `POST /api/service/query`

**مثال JavaScript:**
```javascript
const response = await fetch(
  'https://really-amin-datasourceforcryptocurrency.hf.space/api/service/query',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      type: "rate", // یا: history, sentiment, econ, whales, onchain, pair
      payload: {
        pair: "BTC/USDT"
      },
      options: {
        prefer_hf: true,
        persist: true
      }
    })
  }
);
const data = await response.json();
console.log(data);
```

---

## 🔌 8. WebSocket (داده‌های Real-time)

### 8.1 اتصال WebSocket

**مثال JavaScript:**
```javascript
const ws = new WebSocket('wss://really-amin-datasourceforcryptocurrency.hf.space/ws');

ws.onopen = () => {
  console.log('متصل شد!');
  
  // Subscribe به داده‌های بازار
  ws.send(JSON.stringify({
    action: "subscribe",
    service: "market_data",
    symbols: ["BTC", "ETH", "BNB"]
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('داده جدید:', data);
  
  // مثال خروجی:
  // {
  //   "type": "update",
  //   "service": "market_data",
  //   "symbol": "BTC",
  //   "data": {
  //     "price": 50234.12,
  //     "volume": 1234567.89,
  //     "change_24h": 2.5
  //   },
  //   "timestamp": "2025-01-15T12:00:00Z"
  // }
};

ws.onerror = (error) => {
  console.error('خطا:', error);
};

ws.onclose = () => {
  console.log('اتصال بسته شد');
};
```

---

### 8.2 Subscribe به اخبار

**مثال JavaScript:**
```javascript
const ws = new WebSocket('wss://really-amin-datasourceforcryptocurrency.hf.space/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: "subscribe",
    service: "news",
    filters: {
      symbols: ["BTC", "ETH"]
    }
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "news") {
    console.log('خبر جدید:', data.article);
  }
};
```

---

### 8.3 Subscribe به نهنگ‌ها

**مثال JavaScript:**
```javascript
const ws = new WebSocket('wss://really-amin-datasourceforcryptocurrency.hf.space/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: "subscribe",
    service: "whale_tracking",
    filters: {
      chain: "ethereum",
      min_amount_usd: 1000000
    }
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "whale_transaction") {
    console.log('تراکنش نهنگ:', data.transaction);
  }
};
```

---

## 📝 نکات مهم

1. **Base URL:** همیشه از `https://really-amin-datasourceforcryptocurrency.hf.space` استفاده کنید
2. **WebSocket:** از `wss://` برای اتصال امن استفاده کنید
3. **Rate Limiting:** درخواست‌ها محدود هستند (حدود 1200 در دقیقه)
4. **Cache:** پاسخ‌ها cache می‌شوند (TTL در فیلد `meta.cache_ttl_seconds`)
5. **Error Handling:** همیشه خطاها را handle کنید

---

## 🔍 مثال کامل (Full Example)

**مثال JavaScript کامل:**
```javascript
class CryptoAPIClient {
  constructor() {
    this.baseURL = 'https://really-amin-datasourceforcryptocurrency.hf.space';
  }

  async getRate(pair) {
    const response = await fetch(`${this.baseURL}/api/service/rate?pair=${pair}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  }

  async getNews(symbol = 'BTC', limit = 10) {
    const response = await fetch(
      `${this.baseURL}/api/news/latest?symbol=${symbol}&limit=${limit}`
    );
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  }

  async getWhales(chain = 'ethereum', minAmount = 1000000) {
    const response = await fetch(
      `${this.baseURL}/api/service/whales?chain=${chain}&min_amount_usd=${minAmount}`
    );
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  }

  async analyzeSentiment(text) {
    const response = await fetch(
      `${this.baseURL}/api/sentiment/analyze`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      }
    );
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  }
}

// استفاده:
const client = new CryptoAPIClient();

// دریافت نرخ
const rate = await client.getRate('BTC/USDT');
console.log(`قیمت BTC: $${rate.data.price}`);

// دریافت اخبار
const news = await client.getNews('BTC', 5);
news.data.forEach(article => {
  console.log(`- ${article.title}`);
});

// دریافت نهنگ‌ها
const whales = await client.getWhales('ethereum', 1000000);
console.log(`تعداد تراکنش‌های نهنگ: ${whales.data.length}`);
```

---

## 🐍 مثال کامل Python

```python
import requests
from typing import Optional, Dict, Any

class CryptoAPIClient:
    def __init__(self):
        self.base_url = "https://really-amin-datasourceforcryptocurrency.hf.space"
    
    def get_rate(self, pair: str) -> Dict[str, Any]:
        """دریافت نرخ یک جفت ارز"""
        url = f"{self.base_url}/api/service/rate"
        params = {"pair": pair}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_news(self, symbol: str = "BTC", limit: int = 10) -> Dict[str, Any]:
        """دریافت اخبار"""
        url = f"{self.base_url}/api/news/latest"
        params = {"symbol": symbol, "limit": limit}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_whales(self, chain: str = "ethereum", min_amount: int = 1000000) -> Dict[str, Any]:
        """دریافت تراکنش‌های نهنگ‌ها"""
        url = f"{self.base_url}/api/service/whales"
        params = {
            "chain": chain,
            "min_amount_usd": min_amount
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """تحلیل احساسات"""
        url = f"{self.base_url}/api/sentiment/analyze"
        payload = {"text": text}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

# استفاده:
client = CryptoAPIClient()

# دریافت نرخ
rate = client.get_rate("BTC/USDT")
print(f"قیمت BTC: ${rate['data']['price']}")

# دریافت اخبار
news = client.get_news("BTC", 5)
for article in news['data']:
    print(f"- {article['title']}")

# دریافت نهنگ‌ها
whales = client.get_whales("ethereum", 1000000)
print(f"تعداد تراکنش‌های نهنگ: {len(whales['data'])}")
```

---

**تمام این سرویس‌ها از HuggingFace Space شما سرو می‌شوند و نیازی به اتصال مستقیم به APIهای خارجی نیست!** 🚀

