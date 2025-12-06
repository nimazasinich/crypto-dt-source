# 📘 راهنمای سیستم یکپارچه (Unified System Guide)

## 🎯 معرفی

این سیستم یک **پلتفرم یکپارچه** برای دسترسی به داده‌های ارزهای دیجیتال است که از یک **فایل JSON مرجع** استفاده می‌کند.

---

## 🏗️ معماری سیستم

```
crypto_resources_unified_2025-11-11.json  ← منبع داده مرجع (200+ API)
                ↓
    unified_resource_loader.py            ← بارگذاری و مدیریت منابع
                ↓
    unified_api_service.py                ← APIRouter با endpoints
                ↓
        app_unified.py                    ← FastAPI App + Static UI
                ↓
    Docker Container / HF Space           ← استقرار
```

---

## 📦 فایل‌های کلیدی

### 1. **crypto_resources_unified_2025-11-11.json**
فایل JSON مرجع شامل تمام منابع داده:
- ✅ 24 RPC Node
- ✅ 18 Block Explorer
- ✅ 23 Market Data API
- ✅ 15 News API
- ✅ 12 Sentiment API
- ✅ 12 On-chain Analytics
- ✅ 9 Whale Tracking
- ✅ 7 CORS Proxy
- ✅ HuggingFace Models & Datasets

**مجموع: 137 منبع داده**

### 2. **unified_resource_loader.py**
کلاس `UnifiedResourceLoader` که:
- JSON را می‌خواند و parse می‌کند
- منابع را به دسته‌بندی می‌کند
- API keys را مدیریت می‌کند
- query methods فراهم می‌کند

### 3. **unified_api_service.py**
FastAPI Router با endpoints:
```
/api/resources/*       - مدیریت منابع
/api/market/*          - قیمت و بازار
/api/news              - اخبار
/api/sentiment/*       - احساسات
/api/trading-pairs     - جفت ارزها
/api/providers/status  - وضعیت providerها
```

### 4. **app_unified.py**
برنامه اصلی FastAPI که:
- API Router را include می‌کند
- Static files را serve می‌کند
- HTML pages را برمی‌گرداند

---

## 🚀 راه‌اندازی

### روش 1: اجرای مستقیم
```bash
python app_unified.py
```
سپس: http://localhost:7860

### روش 2: با Uvicorn
```bash
uvicorn app_unified:app --host 0.0.0.0 --port 7860
```

### روش 3: در Docker
```bash
docker build -t crypto-hub .
docker run -p 7860:7860 crypto-hub
```

---

## 📡 API Endpoints

### منابع (Resources)
```
GET /api/resources/stats              - آمار کلی منابع
GET /api/resources/categories         - لیست دسته‌بندی‌ها
GET /api/resources/category/{cat}     - منابع یک دسته
GET /api/resources/search?q=bitcoin   - جستجو در منابع
GET /api/resources/{id}               - جزئیات یک منبع
```

### بازار (Market Data)
```
GET /api/market/price/{symbol}               - قیمت فعلی
GET /api/market/prices?symbols=btc,eth       - قیمت چندین ارز
GET /api/market/historical/{symbol}?days=7   - داده‌های تاریخی
GET /api/market/trending                     - ارزهای ترند
GET /api/market/global                       - داده‌های جهانی
```

### اخبار (News)
```
GET /api/news?limit=10                       - آخرین اخبار
```

### احساسات (Sentiment)
```
GET /api/sentiment/fear-greed                - شاخص Fear & Greed
GET /api/sentiment/social/{symbol}           - احساسات شبکه‌های اجتماعی
```

### دیگر
```
GET /api/trading-pairs                       - جفت ارزهای معاملاتی
GET /api/providers/status                    - وضعیت providerها
GET /api/health                              - بررسی سلامت
```

---

## 🔑 مدیریت API Keys

API keys در فایل JSON ذخیره شده‌اند اما می‌توانید با متغیرهای محیطی override کنید:

```bash
export ETHERSCAN_API_KEY="your-key"
export BSCSCAN_API_KEY="your-key"
export COINMARKETCAP_API_KEY="your-key"
```

---

## 💡 مثال‌های استفاده

### Python
```python
from unified_resource_loader import get_loader

# بارگذاری منابع
loader = get_loader()

# دریافت یک منبع خاص
coingecko = loader.get_resource("coingecko")
print(f"URL: {coingecko.base_url}")
print(f"Requires auth: {coingecko.requires_auth()}")

# جستجو
results = loader.search_resources("binance")
print(f"Found {len(results)} resources")

# دریافت منابع رایگان
free_apis = loader.get_free_resources("market_data")
print(f"Free market APIs: {len(free_apis)}")
```

### JavaScript (Frontend)
```javascript
// دریافت قیمت Bitcoin
fetch('/api/market/price/bitcoin')
  .then(res => res.json())
  .then(data => console.log(data));

// دریافت اخبار
fetch('/api/news?limit=5')
  .then(res => res.json())
  .then(data => console.log(data.news));

// دریافت Fear & Greed Index
fetch('/api/sentiment/fear-greed')
  .then(res => res.json())
  .then(data => console.log(data));
```

### cURL
```bash
# قیمت Ethereum
curl http://localhost:7860/api/market/price/ethereum

# داده‌های تاریخی Bitcoin (7 روز)
curl "http://localhost:7860/api/market/historical/bitcoin?days=7"

# آمار منابع
curl http://localhost:7860/api/resources/stats
```

---

## 📊 ساختار داده JSON

هر منبع در JSON شامل:

```json
{
  "id": "coingecko",
  "name": "CoinGecko",
  "base_url": "https://api.coingecko.com/api/v3",
  "auth": {
    "type": "none"
  },
  "endpoints": {
    "simple_price": "/simple/price?ids={ids}&vs_currencies={fiats}"
  },
  "docs_url": "https://www.coingecko.com/en/api/documentation",
  "notes": "Rate limit: 10-50 calls/min (free)"
}
```

**انواع احراز هویت:**
- `none` - بدون نیاز به کلید
- `apiKeyQuery` - کلید در query parameter
- `apiKeyHeader` - کلید در header
- `apiKeyPath` - کلید در مسیر URL

---

## 🔧 افزودن منبع جدید

برای افزودن API جدید:

1. **به فایل JSON اضافه کنید:**
```json
{
  "registry": {
    "market_data_apis": [
      {
        "id": "my_new_api",
        "name": "My New API",
        "base_url": "https://api.example.com",
        "auth": {"type": "none"},
        "endpoints": {...},
        "docs_url": "https://docs.example.com"
      }
    ]
  }
}
```

2. **سرور را restart کنید** - بدون نیاز به تغییر کد!

---

## 🐛 عیب‌یابی

### Loader بارگذاری نمی‌شود
```bash
# بررسی وجود فایل JSON
ls -la crypto_resources_unified_2025-11-11.json

# تست مستقیم loader
python unified_resource_loader.py
```

### API Key کار نمی‌کند
```bash
# بررسی متغیرهای محیطی
env | grep API

# نمایش منابع با کلید
python -c "from unified_resource_loader import get_loader; \
           loader = get_loader(); \
           resources = [r for r in loader.resources.values() if r.api_key]; \
           print(f'Resources with keys: {len(resources)}')"
```

### Port در حال استفاده است
```bash
# تغییر port
PORT=8080 python app_unified.py

# یا
uvicorn app_unified:app --port 8080
```

---

## 📈 آمار سیستم

تعداد منابع در هر دسته:
```
rpc_nodes              : 24
block_explorers        : 18
market_data            : 23
news                   : 15
sentiment              : 12
onchain_analytics      : 12
whale_tracking         : 9
community_sentiment    : 1
hf_model              : 2
hf_dataset            : 10
cors_proxy            : 7
free_endpoint         : 4
───────────────────────────
TOTAL                 : 137
```

منابع رایگان: **89 (65%)**
منابع با کلید: **48 (35%)**

---

## 🎨 UI Pages

- **/** - صفحه اصلی (index.html)
- **/ai-tools** - ابزارهای هوش مصنوعی
- **/admin** - پنل مدیریت
- **/docs** - مستندات API (Swagger)

---

## 🔄 تفاوت با سیستم قدیم

### قبل ❌
- چندین فایل JSON مختلف
- Hardcoded API URLs در کد Python
- نیاز به تغییر کد برای افزودن API جدید
- پراکندگی API keys

### بعد ✅
- **یک فایل JSON مرجع**
- خواندن پویا از JSON
- افزودن API جدید = ویرایش JSON
- مدیریت متمرکز keys

---

## 🚀 استقرار در Production

### HuggingFace Space
1. فایل `app_unified.py` را به عنوان `app.py` کپی کنید
2. در `Dockerfile`:
   ```dockerfile
   CMD ["python", "app.py"]
   ```
3. فایل JSON را در root قرار دهید
4. Environment variables را در Settings تنظیم کنید

### Docker Compose
```yaml
version: '3.8'
services:
  crypto-hub:
    build: .
    ports:
      - "7860:7860"
    environment:
      - ETHERSCAN_API_KEY=${ETHERSCAN_API_KEY}
      - BSCSCAN_API_KEY=${BSCSCAN_API_KEY}
    volumes:
      - ./crypto_resources_unified_2025-11-11.json:/app/crypto_resources_unified_2025-11-11.json
```

---

## 📝 لیست چک قبل از Deploy

- [ ] فایل JSON موجود است
- [ ] Dependencies نصب شده (`pip install -r requirements.txt`)
- [ ] API Keys تنظیم شده
- [ ] Port در دسترس است
- [ ] Static files موجودند (index.html, etc.)
- [ ] تست health check: `curl localhost:7860/api/health`

---

## 🤝 کمک و پشتیبانی

- 📖 API Docs: http://localhost:7860/docs
- 🔍 Resource Stats: http://localhost:7860/api/resources/stats
- 💚 Health Check: http://localhost:7860/api/health
- 📊 System Info: http://localhost:7860/info

---

**ساخته شده با ❤️ برای جامعه کریپتو**
**Version: 2.0.0**
**Last Updated: 2025-11-24**
