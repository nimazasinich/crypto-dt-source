# پیاده‌سازی کامل API مستقیم - بدون پایپلاین

## 🎯 خلاصه پروژه

این پیاده‌سازی یک **API کامل برای داده‌های ارزهای دیجیتال** را ارائه می‌دهد که شامل:

✅ **بارگذاری مستقیم مدل‌های HuggingFace** (بدون استفاده از pipeline)  
✅ **ادغام با APIهای خارجی** (CoinGecko, Binance, Alternative.me, Reddit, RSS feeds)  
✅ **بارگذاری Dataset** (CryptoCoin, WinkingFace datasets)  
✅ **محدودیت نرخ درخواست** و مدیریت خطا  
✅ **مستندات جامع** و آزمون‌های کامل  

---

## 📦 فایل‌های جدید ایجاد شده

### 1. سرویس‌های Backend

#### `/workspace/backend/services/direct_model_loader.py`
**سرویس بارگذاری مستقیم مدل - بدون پایپلاین**

- بارگذاری مستقیم مدل‌های HuggingFace با استفاده از `AutoModel` و `AutoTokenizer`
- **بدون استفاده از pipeline** - استنتاج مستقیم با PyTorch
- پشتیبانی از مدل‌های متعدد:
  - `ElKulako/cryptobert`
  - `kk08/CryptoBERT`
  - `ProsusAI/finbert`
  - `cardiffnlp/twitter-roberta-base-sentiment`

#### `/workspace/backend/services/dataset_loader.py`
**بارگذار Dataset های HuggingFace**

- بارگذاری مستقیم dataset ها از HuggingFace
- پشتیبانی از:
  - `linxy/CryptoCoin`
  - `WinkingFace/CryptoLM-Bitcoin-BTC-USDT`
  - `WinkingFace/CryptoLM-Ethereum-ETH-USDT`
  - `WinkingFace/CryptoLM-Solana-SOL-USDT`
  - `WinkingFace/CryptoLM-Ripple-XRP-USDT`

#### `/workspace/backend/services/external_api_clients.py`
**کلاینت‌های API خارجی**

- **Alternative.me**: شاخص ترس و طمع (Fear & Greed Index)
- **Reddit**: پست‌های ارزهای دیجیتال
- **RSS Feed**: اخبار از منابع متعدد (CoinDesk, CoinTelegraph, و غیره)

### 2. روترهای API

#### `/workspace/backend/routers/direct_api.py`
**روتر کامل REST API**

شامل endpoint های زیر:
- CoinGecko: `/api/v1/coingecko/price`, `/api/v1/coingecko/trending`
- Binance: `/api/v1/binance/klines`, `/api/v1/binance/ticker`
- Alternative.me: `/api/v1/alternative/fng`
- Reddit: `/api/v1/reddit/top`, `/api/v1/reddit/new`
- RSS: `/api/v1/rss/feed`, `/api/v1/coindesk/rss`, `/api/v1/cointelegraph/rss`
- HuggingFace Models: `/api/v1/hf/sentiment`, `/api/v1/hf/models`
- HuggingFace Datasets: `/api/v1/hf/datasets`

### 3. ابزارها

#### `/workspace/utils/rate_limiter_simple.py`
**محدودکننده نرخ درخواست**

- محدودسازی نرخ در حافظه
- محدودیت‌های مختلف برای هر endpoint
- سرآیندهای rate limit در پاسخ‌ها

---

## 🚀 راه‌اندازی سریع

### 1. نصب وابستگی‌ها

```bash
pip install fastapi uvicorn httpx transformers torch datasets feedparser
```

یا از فایل requirements:

```bash
pip install -r requirements_direct_api.txt
```

### 2. اجرای سرور

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. تست API

```bash
# وضعیت سیستم
curl http://localhost:8000/api/v1/status

# قیمت Bitcoin از CoinGecko
curl "http://localhost:8000/api/v1/coingecko/price?symbols=BTC"

# داده‌های Binance
curl "http://localhost:8000/api/v1/binance/klines?symbol=BTC&timeframe=1h&limit=10"

# شاخص ترس و طمع
curl "http://localhost:8000/api/v1/alternative/fng"

# تحلیل احساسات (بدون پایپلاین)
curl -X POST "http://localhost:8000/api/v1/hf/sentiment" \
  -H "Content-Type: application/json" \
  -d '{"text": "Bitcoin is going to the moon!", "model_key": "cryptobert_elkulako"}'
```

---

## 📊 Endpointهای موجود

### APIهای خارجی

| سرویس | Endpoint | توضیحات |
|-------|----------|---------|
| CoinGecko | `/api/v1/coingecko/price` | دریافت قیمت ارزها |
| Binance | `/api/v1/binance/klines` | داده‌های OHLCV |
| Alternative.me | `/api/v1/alternative/fng` | شاخص ترس و طمع |
| Reddit | `/api/v1/reddit/top` | پست‌های برتر |
| RSS | `/api/v1/coindesk/rss` | اخبار CoinDesk |
| RSS | `/api/v1/cointelegraph/rss` | اخبار CoinTelegraph |

### مدل‌های HuggingFace (بدون پایپلاین)

| Endpoint | توضیحات |
|----------|---------|
| `/api/v1/hf/sentiment` | تحلیل احساسات مستقیم |
| `/api/v1/hf/sentiment/batch` | تحلیل احساسات دسته‌ای |
| `/api/v1/hf/models` | لیست مدل‌های بارگذاری شده |
| `/api/v1/hf/models/load` | بارگذاری مدل خاص |

### Dataset های HuggingFace

| Endpoint | توضیحات |
|----------|---------|
| `/api/v1/hf/datasets` | لیست dataset های بارگذاری شده |
| `/api/v1/hf/datasets/load` | بارگذاری dataset خاص |
| `/api/v1/hf/datasets/sample` | دریافت نمونه از dataset |
| `/api/v1/hf/datasets/query` | جستجو در dataset |

---

## 🎯 ویژگی‌های کلیدی

### ✅ بارگذاری مستقیم مدل (بدون پایپلاین)

```python
from backend.services.direct_model_loader import direct_model_loader

# بارگذاری مدل
await direct_model_loader.load_model("cryptobert_elkulako")

# پیش‌بینی احساسات - مستقیم بدون pipeline
result = await direct_model_loader.predict_sentiment(
    text="Bitcoin is mooning!",
    model_key="cryptobert_elkulako"
)

# نتیجه شامل:
# - sentiment, label, score, confidence
# - all_scores (احتمالات تمام کلاس‌ها)
# - inference_type: "direct_no_pipeline"
# - device: "cuda" یا "cpu"
```

### ✅ ادغام با APIهای خارجی

همه APIهای خارجی به صورت مستقیم از طریق HTTP فراخوانی می‌شوند:

- **CoinGecko**: قیمت‌های لحظه‌ای ارزها
- **Binance**: داده‌های تاریخی OHLCV
- **Alternative.me**: شاخص ترس و طمع بازار
- **Reddit**: بحث‌های مربوط به ارزهای دیجیتال
- **RSS Feeds**: اخبار از منابع مختلف

### ✅ محدودیت نرخ درخواست

- محدودسازی خودکار بر اساس IP کاربر
- سرآیندهای rate limit در پاسخ‌ها
- تنظیمات مختلف برای هر endpoint

---

## 📚 مستندات

### مستندات کامل API
- **فارسی**: `/workspace/README_PERSIAN.md` (این فایل)
- **انگلیسی**: `/workspace/DIRECT_API_DOCUMENTATION.md`
- **خلاصه پیاده‌سازی**: `/workspace/IMPLEMENTATION_SUMMARY.md`
- **راهنمای سریع**: `/workspace/QUICK_START_DIRECT_API.md`

### مستندات آنلاین
- **Swagger UI**: http://localhost:8000/docs
- **اطلاعات پایه**: http://localhost:8000/

---

## 🧪 اجرای تست‌ها

```bash
# نصب pytest
pip install pytest pytest-asyncio

# اجرای تمام تست‌ها
pytest test_direct_api.py -v

# اجرای تست خاص
pytest test_direct_api.py::TestHuggingFaceModelEndpoints -v
```

---

## 🔧 تنظیمات محیطی (اختیاری)

```bash
# .env file
NEWSAPI_KEY=your_newsapi_key
CRYPTOPANIC_TOKEN=your_cryptopanic_token
HF_API_TOKEN=your_huggingface_token
```

---

## 🎨 معماری سیستم

```
FastAPI Application (hf_unified_server.py)
    ↓
Rate Limiter + CORS
    ↓
API Routers:
    1. Direct API Router (جدید)
       - External APIs
       - HuggingFace Models (بدون پایپلاین)
       - HuggingFace Datasets
    2. Unified Service Router
    3. Real Data Router
    ↓
Services:
    - Direct Model Loader
    - Dataset Loader
    - External API Clients
```

---

## ✅ چک‌لیست پیاده‌سازی

- [x] بارگذار مستقیم مدل (بدون پایپلاین)
- [x] ادغام مدل‌های CryptoBERT
- [x] بارگذار dataset ها
- [x] کلاینت‌های API خارجی
- [x] Endpoint های REST
- [x] Endpoint های استنتاج HF
- [x] محدودیت نرخ و مدیریت خطا
- [x] مستندات جامع
- [x] مجموعه تست

---

## 🚀 استقرار در محیط تولید

### استفاده از Docker

```bash
# ساخت image
docker build -t crypto-api .

# اجرای container
docker run -p 8000:8000 crypto-api
```

### استفاده از Systemd

```bash
sudo systemctl enable crypto-api
sudo systemctl start crypto-api
```

---

## 📈 آمار پیاده‌سازی

- **تعداد فایل‌های جدید**: 9
- **تعداد فایل‌های ویرایش شده**: 1
- **تعداد کل endpoint ها**: 24+
- **تعداد مدل‌های پشتیبانی شده**: 4
- **تعداد dataset های پشتیبانی شده**: 5
- **تعداد API خارجی**: 6
- **پوشش تست**: جامع

---

## 🎯 موارد تکمیل شده

### 1️⃣ بارگذاری مستقیم مدل‌ها
✅ هیچ استفاده از pipeline نیست  
✅ استنتاج مستقیم با PyTorch  
✅ پشتیبانی از CUDA  
✅ بارگذاری/حذف مدل‌ها  

### 2️⃣ ادغام با APIهای خارجی
✅ CoinGecko - قیمت‌های لحظه‌ای  
✅ Binance - داده‌های تاریخی  
✅ Alternative.me - شاخص ترس و طمع  
✅ Reddit - پست‌های کریپتو  
✅ RSS Feeds - اخبار از منابع مختلف  

### 3️⃣ بارگذاری Dataset ها
✅ CryptoCoin dataset  
✅ WinkingFace datasets (BTC, ETH, SOL, XRP)  
✅ نمونه‌برداری و جستجو  
✅ آمارگیری  

### 4️⃣ ویژگی‌های اضافی
✅ محدودیت نرخ درخواست  
✅ مدیریت خطای جامع  
✅ مستندات کامل  
✅ مجموعه تست‌های جامع  

---

## 📞 پشتیبانی

برای سوالات یا مشکلات:
- مستندات API: `/workspace/DIRECT_API_DOCUMENTATION.md`
- Swagger UI: http://localhost:8000/docs
- وضعیت سیستم: http://localhost:8000/api/v1/status

---

## 🎉 خلاصه

**پروژه با موفقیت 100% تکمیل شده است!**

تمام موارد درخواست شده پیاده‌سازی شده:
- ✅ بارگذاری مستقیم مدل‌ها (بدون پایپلاین)
- ✅ ادغام با تمام APIهای خارجی
- ✅ بارگذاری dataset ها
- ✅ محدودیت نرخ و مدیریت خطا
- ✅ مستندات کامل و تست‌های جامع

پروژه آماده استقرار در محیط تولید است! 🚀

---

**تاریخ پیاده‌سازی**: 27 نوامبر 2025  
**نسخه**: 2.0.0  
**وضعیت**: ✅ کامل و آماده برای استفاده
