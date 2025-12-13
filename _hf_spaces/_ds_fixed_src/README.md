---
title: Crypto Resources API
emoji: 🚀
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: mit
---

# 🚀 Crypto Resources API

یک API جامع برای دسترسی به **281+ منبع داده کریپتوکارنسی** با رابط کاربری زیبا و WebSocket support.

## ✨ ویژگی‌ها

- 📊 **281+ منبع داده**: RPC Nodes, Block Explorers, Market Data, News, Sentiment, Analytics
- 🎨 **رابط کاربری زیبا**: داشبورد تعاملی با نمایش آمار لحظه‌ای
- 🔌 **WebSocket**: بروزرسانی خودکار و real-time
- 📚 **API کامل**: RESTful API با OpenAPI/Swagger docs
- 🆓 **رایگان**: بدون نیاز به API key

## 🚀 استفاده سریع

### API Endpoints

```bash
# Health Check
GET /health

# آمار کلی منابع
GET /api/resources/stats

# لیست تمام منابع
GET /api/resources/list

# لیست دسته‌بندی‌ها
GET /api/categories

# منابع یک دسته خاص
GET /api/resources/category/{category}
```

### مثال با cURL

```bash
# دریافت آمار
curl https://YOUR_USERNAME-crypto-resources-api.hf.space/api/resources/stats

# دریافت RPC Nodes
curl https://YOUR_USERNAME-crypto-resources-api.hf.space/api/resources/category/rpc_nodes
```

### مثال با Python

```python
import requests

# دریافت آمار
response = requests.get("https://YOUR_USERNAME-crypto-resources-api.hf.space/api/resources/stats")
stats = response.json()
print(f"Total resources: {stats['total_resources']}")

# دریافت منابع یک دسته
response = requests.get("https://YOUR_USERNAME-crypto-resources-api.hf.space/api/resources/category/market_data")
resources = response.json()
print(f"Market data sources: {len(resources['resources'])}")
```

### WebSocket

```javascript
const ws = new WebSocket('wss://YOUR_USERNAME-crypto-resources-api.hf.space/ws');

ws.onopen = () => {
    console.log('Connected to WebSocket');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Update:', data);
};
```

## 📦 دسته‌بندی منابع

- **RPC Nodes** (24): Ethereum, BSC, Polygon, Arbitrum, Optimism, ...
- **Block Explorers** (9): Etherscan, BscScan, Polygonscan, ...
- **Market Data** (15): CoinGecko, CoinMarketCap, Binance, ...
- **News** (10): CoinDesk, CoinTelegraph, Decrypt, ...
- **Sentiment** (7): LunarCrush, Santiment, ...
- **Analytics** (17): Glassnode, Nansen, Dune Analytics, ...
- **Hugging Face** (7): Datasets & Models
- و بیشتر...

## 🛠️ نصب لوکال

```bash
# Clone repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/crypto-resources-api
cd crypto-resources-api

# نصب dependencies
pip install -r requirements.txt

# اجرای سرور
python -m uvicorn app:app --host 0.0.0.0 --port 7860

# یا با Docker
docker build -t crypto-api .
docker run -p 7860:7860 crypto-api
```

سرور در `http://localhost:7860` در دسترس خواهد بود.

## 📚 مستندات

- **API Docs**: `/docs` - Swagger UI
- **ReDoc**: `/redoc` - Alternative documentation
- **OpenAPI**: `/openapi.json` - OpenAPI specification

## 🔧 تنظیمات

### متغیرهای محیطی (اختیاری)

```bash
# برای آپلود داده به Hugging Face Datasets
HF_TOKEN=your_token_here

# برای استفاده از API های خارجی
COINGECKO_API_KEY=your_key_here
BINANCE_API_KEY=your_key_here
```

## 🤝 مشارکت

این پروژه open-source است و از مشارکت شما استقبال می‌کنیم!

## 📄 لایسنس

MIT License - استفاده آزاد در پروژه‌های شخصی و تجاری

## 🙏 تشکر

از تمام منابع داده و API هایی که این پروژه را ممکن کرده‌اند، تشکر می‌کنیم.

---

💜 ساخته شده با عشق برای جامعه کریپتو
