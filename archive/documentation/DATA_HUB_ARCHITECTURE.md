# 🌐 Data Hub Architecture

## معماری هاب داده / Data Hub Architecture

این سند معماری کامل هاب داده رمزارزی را توضیح می‌دهد که تمام داده‌ها از APIهای خارجی ابتدا در HuggingFace Datasets بارگذاری شده و سپس به کلاینت‌ها سرو می‌شوند.

This document explains the complete cryptocurrency data hub architecture where all data from external APIs is first uploaded to HuggingFace Datasets and then served to clients.

---

## 📊 جریان کامل داده / Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                         │
│  (CoinGecko, Binance, News APIs, Blockchain RPCs, etc.)         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              │ FREE APIs (No API keys needed)
                              │ Real-time data every 60 seconds
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      BACKGROUND WORKERS                          │
│                                                                  │
│  • MarketDataWorker  → Polls CoinGecko every 60s                │
│  • OHLCDataWorker    → Polls Binance every 60s                  │
│  • Validates & processes real data                              │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              │ Validated real data
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   LOCAL SQLite DATABASE                          │
│                      (Quick Access Cache)                        │
│                                                                  │
│  • cached_market_data table (latest prices)                     │
│  • cached_ohlc table (candlestick data)                         │
│  • Fast queries for recent data                                 │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              │ Cache saved
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│             🤗 HUGGINGFACE DATASETS (Cloud Storage)              │
│                                                                  │
│  • {username}/crypto-market-data                                │
│     ├─ Real-time prices, volumes, market caps                   │
│     ├─ Updated every 60 seconds                                 │
│     └─ Public access (no auth for read)                         │
│                                                                  │
│  • {username}/crypto-ohlc-data                                  │
│     ├─ OHLC candlestick data (1h, 4h, 1d intervals)            │
│     ├─ Historical data from Binance                             │
│     └─ Public access (no auth for read)                         │
│                                                                  │
│  ✅ All data is REAL (no mock/fake data)                        │
│  ✅ Automatically versioned and tracked                          │
│  ✅ Globally accessible via HuggingFace Hub                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              │ Public datasets
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     DATA HUB API ENDPOINTS                       │
│                     (/api/hub/* routes)                          │
│                                                                  │
│  GET  /api/hub/status        → Hub status & dataset info        │
│  GET  /api/hub/market        → Market data FROM HuggingFace     │
│  GET  /api/hub/ohlc          → OHLC data FROM HuggingFace       │
│  GET  /api/hub/dataset-info  → Detailed dataset information     │
│  GET  /api/hub/health        → Health check                     │
│                                                                  │
│  🔒 Authentication: Required (HF_TOKEN)                          │
│  📊 Data Source: HuggingFace Datasets ONLY                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              │ JSON responses
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENTS                                 │
│                                                                  │
│  • Web browsers (via Swagger docs)                              │
│  • API clients (curl, requests, httpx)                          │
│  • Third-party applications                                     │
│  • Data scientists & researchers                                │
│  • Trading bots & analytics tools                               │
│                                                                  │
│  Access: Public datasets via HuggingFace Hub                    │
│          OR via Data Hub API endpoints                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 اهداف کلیدی / Key Objectives

### ✅ هدف اصلی / Main Goal
**تمام داده‌ها باید ابتدا در HuggingFace Datasets بارگذاری شوند و سپس از آنجا به کلاینت‌ها سرو شوند.**

**All data must first be uploaded to HuggingFace Datasets and then served from there to clients.**

### ✅ مزایا / Benefits

1. **📦 ذخیره‌سازی مرکزی / Centralized Storage**
   - تمام داده‌ها در یک مکان مرکزی (HuggingFace)
   - نسخه‌بندی خودکار و ردیابی تغییرات
   - دسترسی جهانی و عمومی

2. **🔄 به‌روزرسانی خودکار / Automatic Updates**
   - Worker ها هر 60 ثانیه داده جدید دریافت می‌کنند
   - به‌طور خودکار به HuggingFace آپلود می‌شوند
   - همیشه داده‌های تازه در دسترس است

3. **🌍 دسترسی عمومی / Public Access**
   - هر کسی می‌تواند dataset ها را بخواند (بدون احراز هویت)
   - قابل استفاده در تحقیقات و پروژه‌های شخصی
   - شفافیت کامل در داده‌ها

4. **✅ فقط داده واقعی / Real Data Only**
   - هیچ داده جعلی یا mock وجود ندارد
   - تمام داده‌ها از APIهای معتبر (CoinGecko, Binance)
   - قابل اعتماد برای تصمیم‌گیری

---

## 🔧 پیاده‌سازی / Implementation

### 1. ماژول آپلود به HuggingFace / HuggingFace Upload Module

**فایل:** `hf_dataset_uploader.py`

این ماژول مسئول آپلود داده‌ها به HuggingFace Datasets است:

```python
from hf_dataset_uploader import get_dataset_uploader

# Create uploader
uploader = get_dataset_uploader()

# Upload market data
await uploader.upload_market_data(market_data_list, append=True)

# Upload OHLC data
await uploader.upload_ohlc_data(ohlc_data_list, append=True)
```

**قابلیت‌ها:**
- ایجاد خودکار dataset ها اگر وجود نداشته باشند
- حالت append (افزودن به داده‌های موجود)
- حذف رکوردهای تکراری
- متادیتا و README خودکار

### 2. یکپارچه‌سازی با Worker ها / Integration with Workers

**فایل:** `workers/market_data_worker.py`

Worker بازار به‌طور خودکار داده‌ها را به HuggingFace آپلود می‌کند:

```python
async def save_market_data_to_cache(market_data):
    # Step 1: Save to SQLite (local cache)
    for data in market_data:
        cache.save_market_data(...)

    # Step 2: Upload to HuggingFace Datasets
    if HF_UPLOAD_ENABLED:
        await hf_uploader.upload_market_data(market_data, append=True)
```

**فایل:** `workers/ohlc_data_worker.py`

Worker OHLC هم به همین صورت عمل می‌کند:

```python
async def save_ohlc_data_to_cache(ohlc_data):
    # Step 1: Save to SQLite
    for data in ohlc_data:
        cache.save_ohlc_candle(...)

    # Step 2: Upload to HuggingFace
    if HF_UPLOAD_ENABLED:
        await hf_uploader.upload_ohlc_data(ohlc_data, append=True)
```

### 3. API Endpoints جدید / New API Endpoints

**فایل:** `api/hf_data_hub_endpoints.py`

این endpoint ها داده‌ها را **فقط از HuggingFace** سرو می‌کنند:

#### 📍 دریافت داده بازار / Get Market Data

```http
GET /api/hub/market?symbols=BTC,ETH&limit=100
Authorization: Bearer {HF_TOKEN}
```

**پاسخ:**
```json
[
  {
    "symbol": "BTC",
    "price": 45000.50,
    "market_cap": 850000000000.0,
    "volume_24h": 25000000000.0,
    "change_24h": 2.5,
    "provider": "coingecko",
    "timestamp": "2025-11-25T10:30:00Z"
  }
]
```

#### 📍 دریافت داده OHLC / Get OHLC Data

```http
GET /api/hub/ohlc?symbol=BTCUSDT&interval=1h&limit=500
Authorization: Bearer {HF_TOKEN}
```

**پاسخ:**
```json
[
  {
    "symbol": "BTCUSDT",
    "interval": "1h",
    "timestamp": "2025-11-25T10:00:00Z",
    "open": 44500.0,
    "high": 45000.0,
    "low": 44300.0,
    "close": 44800.0,
    "volume": 1250000.0,
    "provider": "binance"
  }
]
```

#### 📍 وضعیت هاب / Hub Status

```http
GET /api/hub/status
```

**پاسخ:**
```json
{
  "status": "healthy",
  "message": "Data Hub operational",
  "market_dataset": {
    "available": true,
    "records": 1250,
    "url": "https://huggingface.co/datasets/{username}/crypto-market-data"
  },
  "ohlc_dataset": {
    "available": true,
    "records": 45000,
    "url": "https://huggingface.co/datasets/{username}/crypto-ohlc-data"
  }
}
```

---

## ⚙️ تنظیمات / Configuration

### متغیرهای محیطی / Environment Variables

```bash
# Required for HuggingFace upload
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx

# Optional - defaults to detected username
HF_USERNAME=your-username

# Feature flags
USE_MOCK_DATA=false  # CRITICAL: Always false
```

### فعال‌سازی آپلود به HuggingFace / Enable HuggingFace Upload

1. **دریافت Token از HuggingFace:**
   - برو به https://huggingface.co/settings/tokens
   - یک token جدید با دسترسی write بساز
   - Token را کپی کن

2. **تنظیم متغیر محیطی:**
   ```bash
   export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxx"
   export HF_USERNAME="your-username"
   ```

3. **اجرای برنامه:**
   ```bash
   python hf_space_api.py
   ```

4. **بررسی لاگ‌ها:**
   ```
   ✅ HuggingFace Dataset upload ENABLED
   📤 Uploading 20 market records to HuggingFace Datasets...
   ✅ Successfully uploaded market data to HuggingFace Datasets
   ```

---

## 🧪 تست / Testing

### اجرای تست کامل / Run Complete Test

```bash
python test_complete_data_hub.py
```

این تست موارد زیر را بررسی می‌کند:

1. ✅ اتصال به APIهای خارجی (CoinGecko, Binance)
2. ✅ ذخیره‌سازی در SQLite cache
3. ✅ آپلود به HuggingFace Datasets
4. ✅ دریافت داده از HuggingFace توسط کلاینت
5. ✅ API endpoint های جدید

### تست دستی با curl / Manual Testing with curl

```bash
# Get hub status
curl http://localhost:7860/api/hub/status

# Get market data (requires auth)
curl -H "Authorization: Bearer YOUR_HF_TOKEN" \
     "http://localhost:7860/api/hub/market?symbols=BTC,ETH&limit=10"

# Get OHLC data (requires auth)
curl -H "Authorization: Bearer YOUR_HF_TOKEN" \
     "http://localhost:7860/api/hub/ohlc?symbol=BTCUSDT&interval=1h&limit=100"
```

### استفاده مستقیم از HuggingFace / Direct HuggingFace Access

```python
from datasets import load_dataset

# Load market data
dataset = load_dataset(
    "your-username/crypto-market-data",
    split="train"
)

# Convert to pandas
df = dataset.to_pandas()
print(df.head())
```

---

## 📊 Datasets عمومی / Public Datasets

### Crypto Market Data

**نام:** `{username}/crypto-market-data`
**لینک:** https://huggingface.co/datasets/{username}/crypto-market-data

**محتوا:**
- قیمت‌های real-time ارزهای دیجیتال
- حجم معاملات 24 ساعته
- مارکت کپ
- تغییرات قیمت
- بالاترین و پایین‌ترین قیمت

**به‌روزرسانی:** هر 60 ثانیه
**منبع:** CoinGecko API (رایگان)

### Crypto OHLC Data

**نام:** `{username}/crypto-ohlc-data`
**لینک:** https://huggingface.co/datasets/{username}/crypto-ohlc-data

**محتوا:**
- داده‌های کندل استیک (OHLC)
- بازه‌های مختلف: 1h, 4h, 1d
- حجم معاملات
- داده‌های تاریخی

**به‌روزرسانی:** هر 60 ثانیه
**منبع:** Binance API (رایگان)

---

## 🔒 امنیت / Security

### احراز هویت / Authentication

- **API Endpoints:** نیاز به HF_TOKEN دارند
- **Public Datasets:** خواندن عمومی، نوشتن فقط با token
- **Token Storage:** در متغیرهای محیطی (نه در کد)

### دسترسی‌ها / Permissions

```
Read Access (عمومی):
  ✅ هر کسی می‌تواند dataset ها را بخواند
  ✅ دانلود رایگان از HuggingFace Hub
  ✅ استفاده در پروژه‌های شخصی

Write Access (محدود):
  🔒 فقط با HF_TOKEN معتبر
  🔒 فقط worker ها می‌توانند آپلود کنند
  🔒 API endpoints نیاز به احراز هویت دارند
```

---

## 📈 نظارت / Monitoring

### لاگ‌های Worker / Worker Logs

```bash
# Market data worker
[market_worker] Fetching REAL data from CoinGecko API...
[market_worker] Successfully fetched 20 coins from CoinGecko
[market_worker] Saved 20 REAL market records from CoinGecko
[market_worker] 📤 Uploading 20 market records to HuggingFace Datasets...
[market_worker] ✅ Successfully uploaded market data to HuggingFace Datasets
```

### Health Check Endpoints

```bash
# Check data hub health
curl http://localhost:7860/api/hub/health

# Check system health
curl http://localhost:7860/api/health
```

---

## 🚀 استقرار / Deployment

### استقرار روی HuggingFace Spaces / Deploy on HuggingFace Spaces

1. **ایجاد Space جدید:**
   - برو به https://huggingface.co/new-space
   - نام: `crypto-data-hub`
   - SDK: `Docker` یا `Gradio`

2. **تنظیم Secrets:**
   ```
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
   HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
   ```

3. **Push کردن کد:**
   ```bash
   git remote add hf https://huggingface.co/spaces/{username}/crypto-data-hub
   git push hf main
   ```

4. **بررسی لاگ‌ها:**
   - Worker ها باید شروع به کار کنند
   - داده‌ها باید هر 60 ثانیه به‌روز شوند
   - Dataset ها باید در HuggingFace ظاهر شوند

---

## 🎓 مثال‌های استفاده / Usage Examples

### Python Client

```python
import requests

# Get market data
response = requests.get(
    "https://your-space.hf.space/api/hub/market",
    headers={"Authorization": f"Bearer {HF_TOKEN}"},
    params={"symbols": "BTC,ETH", "limit": 10}
)
data = response.json()

for item in data:
    print(f"{item['symbol']}: ${item['price']:.2f}")
```

### JavaScript Client

```javascript
const response = await fetch(
  'https://your-space.hf.space/api/hub/market?symbols=BTC,ETH',
  {
    headers: {
      'Authorization': `Bearer ${HF_TOKEN}`
    }
  }
);

const data = await response.json();
console.log(data);
```

### Direct Dataset Access

```python
from datasets import load_dataset
import pandas as pd

# Load dataset
dataset = load_dataset("username/crypto-market-data", split="train")

# Convert to DataFrame
df = dataset.to_pandas()

# Analyze
btc_data = df[df['symbol'] == 'BTC']
print(f"BTC Price: ${btc_data['price'].iloc[0]:.2f}")
```

---

## ✅ خلاصه / Summary

### قبل از پیاده‌سازی / Before Implementation

```
External APIs → SQLite → HuggingFace Space API → Clients
```

- داده‌ها فقط محلی ذخیره می‌شدند
- کلاینت‌ها از SQLite محلی می‌خواندند
- هیچ dataset عمومی وجود نداشت

### بعد از پیاده‌سازی / After Implementation

```
External APIs → SQLite → HuggingFace Datasets → Clients
                  ↓
            (Quick Cache)
```

- ✅ داده‌ها در HuggingFace Datasets بارگذاری می‌شوند
- ✅ کلاینت‌ها از HuggingFace می‌خوانند
- ✅ Dataset های عمومی و قابل دسترس
- ✅ نسخه‌بندی خودکار
- ✅ دسترسی جهانی

---

## 📞 پشتیبانی / Support

اگر سوال یا مشکلی دارید:

1. لاگ‌های worker را بررسی کنید
2. Health check endpoint ها را تست کنید
3. Dataset ها را در HuggingFace Hub بررسی کنید
4. Token ها و دسترسی‌ها را چک کنید

---

**تاریخ:** 2025-11-25
**نسخه:** 1.0.0
**وضعیت:** ✅ پیاده‌سازی کامل
