# 🚀 Crypto Resources API

API جامع برای دسترسی به 281+ منبع داده کریپتوکارنسی با WebSocket و رابط کاربری تحت وب

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org/)

## ✨ ویژگی‌ها

- 🎯 **281 منبع داده** در 12 دسته مختلف
- 🔌 **WebSocket** برای بروزرسانی لحظه‌ای
- 🎨 **رابط کاربری زیبا** با طراحی مدرن
- 📚 **مستندات Swagger** کامل و تعاملی
- ⚡ **API سریع** با FastAPI
- 🌐 **CORS** فعال برای دسترسی از هر کلاینت

## 📦 منابع موجود

### دسته‌بندی‌ها
- 🔍 **Block Explorers** (33 منبع) - Etherscan, BscScan, TronScan و...
- 📊 **Market Data APIs** (33 منبع) - CoinGecko, CoinMarketCap, DefiLlama و...
- 📰 **News APIs** (17 منبع) - CryptoPanic, NewsAPI و...
- 💭 **Sentiment APIs** (14 منبع) - Fear & Greed Index, LunarCrush و...
- ⛓️ **On-chain Analytics** (14 منبع) - Glassnode, Dune Analytics و...
- 🐋 **Whale Tracking** (10 منبع) - Whale Alert, Arkham و...
- 🤗 **HuggingFace Resources** (9 منبع) - مدل‌ها و دیتاست‌ها
- 🌐 **RPC Nodes** (24 منبع) - Infura, Alchemy, Ankr و...
- 📡 **Free HTTP Endpoints** (13 منبع)
- 🔧 **CORS Proxies** (7 منبع)

## 🚀 راه‌اندازی سریع

### نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### اجرای سرور
```bash
python app.py
```

یا:
```bash
uvicorn app:app --host 0.0.0.0 --port 7860
```

### دسترسی به API
- 🌐 **رابط کاربری**: http://localhost:7860
- 📚 **مستندات**: http://localhost:7860/docs
- ❤️ **Health Check**: http://localhost:7860/health

## 📡 API Endpoints

### HTTP REST API

#### صفحه اصلی و UI
```bash
GET /
```

#### Health Check
```bash
GET /health
```
پاسخ:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-08T...",
  "resources_loaded": true,
  "total_categories": 12,
  "websocket_connections": 5
}
```

#### آمار کلی منابع
```bash
GET /api/resources/stats
```
پاسخ:
```json
{
  "total_resources": 281,
  "total_categories": 12,
  "categories": {
    "block_explorers": 33,
    "market_data_apis": 33,
    ...
  }
}
```

#### لیست تمام منابع
```bash
GET /api/resources/list
```

#### لیست دسته‌بندی‌ها
```bash
GET /api/categories
```

#### منابع یک دسته خاص
```bash
GET /api/resources/category/{category}
```
مثال:
```bash
GET /api/resources/category/block_explorers
```

### WebSocket

#### اتصال به WebSocket
```javascript
const ws = new WebSocket('ws://localhost:7860/ws');

ws.onopen = () => {
  console.log('✅ Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('📨 Received:', data);
  
  if (data.type === 'stats_update') {
    // بروزرسانی UI با آمار جدید
    updateUI(data.data);
  }
};

// ارسال پیام به سرور
ws.send('ping');
```

#### پیام‌های WebSocket

**دریافت آمار اولیه** (بلافاصله پس از اتصال):
```json
{
  "type": "initial_stats",
  "data": {
    "total_resources": 281,
    "total_categories": 12,
    "categories": {...}
  },
  "timestamp": "2025-12-08T..."
}
```

**بروزرسانی دوره‌ای** (هر 10 ثانیه):
```json
{
  "type": "stats_update",
  "data": {
    "total_resources": 281,
    "total_categories": 12,
    "categories": {...}
  },
  "timestamp": "2025-12-08T..."
}
```

## 💻 استفاده از کلاینت

### Python
```python
import requests

# دریافت آمار
response = requests.get('http://localhost:7860/api/resources/stats')
stats = response.json()
print(f"Total: {stats['total_resources']}")

# دریافت Block Explorers
response = requests.get('http://localhost:7860/api/resources/category/block_explorers')
explorers = response.json()
print(f"Explorers: {explorers['total']}")
```

### JavaScript/TypeScript
```typescript
// Fetch API
const stats = await fetch('http://localhost:7860/api/resources/stats')
  .then(res => res.json());

console.log('Total resources:', stats.total_resources);

// WebSocket
const ws = new WebSocket('ws://localhost:7860/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

### curl
```bash
# Health check
curl http://localhost:7860/health

# آمار
curl http://localhost:7860/api/resources/stats

# دسته‌بندی‌ها
curl http://localhost:7860/api/categories

# Block Explorers
curl http://localhost:7860/api/resources/category/block_explorers
```

## 🤗 آپلود به Hugging Face Spaces

### 1. ایجاد Space جدید
1. به https://huggingface.co/spaces بروید
2. "Create new Space" را کلیک کنید
3. نام Space را وارد کنید
4. SDK را "Docker" انتخاب کنید
5. "Create Space" را کلیک کنید

### 2. آپلود فایل‌ها
فایل‌های زیر را آپلود کنید:
- `app.py` - برنامه اصلی
- `requirements.txt` - وابستگی‌ها
- `api-resources/` - پوشه منابع
- `README.md` - مستندات

### 3. تنظیمات Space
در تنظیمات Space:
- Port: `7860`
- Sleep time: `پس از 48 ساعت`

### 4. اجرای خودکار
Space به صورت خودکار:
1. وابستگی‌ها را نصب می‌کند
2. سرور را اجرا می‌کند
3. رابط کاربری را نمایش می‌دهد

## 📊 ساختار پروژه

```
crypto-resources-api/
├── app.py                      # برنامه اصلی FastAPI
├── requirements.txt            # وابستگی‌ها
├── README.md                   # مستندات
├── api-resources/             # منابع
│   └── crypto_resources_unified_2025-11-11.json
├── SUMMARY_FA.md              # خلاصه پروژه
└── FINAL_TEST_REPORT_FA.md   # گزارش تست
```

## 🧪 تست

### تست سرور
```bash
# راه‌اندازی سرور
python app.py

# در ترمینال دیگر
curl http://localhost:7860/health
```

### تست WebSocket
با مرورگر به `http://localhost:7860` بروید و وضعیت WebSocket را بررسی کنید.

### تست از کلاینت خارجی
```python
import requests
import websockets
import asyncio

# تست HTTP
response = requests.get('http://YOUR_SPACE_URL.hf.space/health')
print(response.json())

# تست WebSocket
async def test_ws():
    async with websockets.connect('ws://YOUR_SPACE_URL.hf.space/ws') as ws:
        msg = await ws.recv()
        print(f"Received: {msg}")

asyncio.run(test_ws())
```

## 🔧 تنظیمات

### Environment Variables (اختیاری)
```bash
# پورت سرور
export PORT=7860

# حالت دیباگ
export DEBUG=false
```

## 📈 Performance

- ⚡ پاسخ‌دهی سریع: < 100ms
- 🔌 WebSocket: بروزرسانی هر 10 ثانیه
- 💾 حافظه: ~100MB
- 👥 همزمانی: تا 100+ کاربر

## 🤝 مشارکت

برای اضافه کردن منابع جدید:
1. فایل JSON را ویرایش کنید
2. اسکریپت `add_new_resources.py` را اجرا کنید
3. سرور را مجدداً راه‌اندازی کنید

## 📝 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است.

## 🙏 تشکر

از تمام منابع و API های استفاده شده:
- CoinGecko, CoinMarketCap, Binance
- Etherscan, BscScan, TronScan
- Infura, Alchemy, Moralis
- و بسیاری دیگر...

## 📞 پشتیبانی

- 📚 مستندات: `/docs`
- 💬 Issues: GitHub Issues
- 📧 ایمیل: support@example.com

---

**ساخته شده با ❤️ برای جامعه کریپتو**

🌟 اگر این پروژه برایتان مفید بود، یک Star بدهید!
