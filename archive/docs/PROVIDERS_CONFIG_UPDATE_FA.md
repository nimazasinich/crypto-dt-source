# 📋 گزارش بروزرسانی providers_config_extended.json

## ✅ خلاصه تغییرات

**تاریخ**: 2025-11-17  
**فایل**: `providers_config_extended.json`  
**پرووایدرهای قبلی**: 93  
**پرووایدرهای جدید**: +2  
**کل پرووایدرها**: **95**

---

## 🆕 پرووایدرهای اضافه شده

### 1. huggingface_space_api
**دسته**: `market_data`  
**URL پایه**: `https://really-amin-datasourceforcryptocurrency.hf.space`

#### Endpoint‌های موجود (20 endpoint):

| # | Endpoint Key | مسیر URL | توضیحات |
|---|-------------|----------|---------|
| 1 | `health` | `/health` | بررسی سلامت سیستم |
| 2 | `info` | `/info` | اطلاعات سیستم |
| 3 | `providers` | `/api/providers` | لیست پرووایدرها |
| 4 | `ohlcv` | `/api/ohlcv` | داده OHLCV/Candlestick |
| 5 | `crypto_prices_top` | `/api/crypto/prices/top` | قیمت‌های برتر |
| 6 | `crypto_price_single` | `/api/crypto/price/{symbol}` | قیمت تکی |
| 7 | `market_overview` | `/api/crypto/market-overview` | بررسی کلی بازار |
| 8 | `market_prices` | `/api/market/prices` | قیمت‌های چندتایی |
| 9 | `market_data_prices` | `/api/market-data/prices` | داده‌های بازار |
| 10 | `analysis_signals` | `/api/analysis/signals` | سیگنال‌های معاملاتی |
| 11 | `analysis_smc` | `/api/analysis/smc` | تحلیل SMC |
| 12 | `scoring_snapshot` | `/api/scoring/snapshot` | امتیازدهی |
| 13 | `all_signals` | `/api/signals` | تمام سیگنال‌ها |
| 14 | `sentiment` | `/api/sentiment` | احساسات بازار |
| 15 | `system_status` | `/api/system/status` | وضعیت سیستم |
| 16 | `system_config` | `/api/system/config` | تنظیمات سیستم |
| 17 | `categories` | `/api/categories` | دسته‌بندی‌ها |
| 18 | `rate_limits` | `/api/rate-limits` | محدودیت‌های درخواست |
| 19 | `logs` | `/api/logs` | لاگ‌ها |
| 20 | `alerts` | `/api/alerts` | هشدارها |

#### مشخصات:
```json
{
  "rate_limit": {
    "requests_per_minute": 1200,
    "requests_per_hour": 60000
  },
  "requires_auth": false,
  "priority": 10,
  "weight": 100,
  "validated": true
}
```

#### ویژگی‌ها:
- ✅ داده OHLCV
- ✅ قیمت‌های real-time
- ✅ سیگنال‌های معاملاتی
- ✅ تحلیل SMC
- ✅ تحلیل احساسات
- ✅ بررسی کلی بازار
- ✅ نظارت سیستم

---

### 2. huggingface_space_hf_integration
**دسته**: `hf-model`  
**URL پایه**: `https://really-amin-datasourceforcryptocurrency.hf.space`

#### Endpoint‌های موجود (5 endpoint):

| # | Endpoint Key | مسیر URL | توضیحات |
|---|-------------|----------|---------|
| 1 | `hf_health` | `/api/hf/health` | سلامت یکپارچه‌سازی HF |
| 2 | `hf_refresh` | `/api/hf/refresh` | بروزرسانی داده HF |
| 3 | `hf_registry` | `/api/hf/registry` | رجیستری مدل‌ها |
| 4 | `hf_run_sentiment` | `/api/hf/run-sentiment` | اجرای تحلیل احساسات |
| 5 | `hf_sentiment` | `/api/hf/sentiment` | تحلیل احساسات (جایگزین) |

#### مشخصات:
```json
{
  "rate_limit": {
    "requests_per_minute": 60,
    "requests_per_hour": 3600
  },
  "requires_auth": false,
  "priority": 10,
  "weight": 100,
  "validated": true
}
```

#### ویژگی‌ها:
- ✅ تحلیل احساسات
- ✅ رجیستری مدل
- ✅ بررسی سلامت مدل
- ✅ بروزرسانی داده

---

## 📊 آمار نهایی

```
📌 کل پرووایدرها: 95
📌 پرووایدرهای جدید: 2
📌 کل endpoint‌های جدید: 25
📌 دسته‌های درگیر: market_data, hf-model
```

### توزیع پرووایدرها بر اساس دسته (به‌روز شده):
```
market_data:           11 (+1) ✨
hf-model:               3 (+1) ✨
blockchain_explorers:   9
exchange:               9
defi:                  11
blockchain_data:        6
news:                   5
hf-dataset:             5
analytics:              4
nft:                    4
social:                 3
sentiment:              2
دیگر موارد:            23
```

---

## 🔗 نحوه استفاده از endpoint‌های جدید

### 1. دریافت داده OHLCV
```python
import requests

response = requests.get(
    "https://really-amin-datasourceforcryptocurrency.hf.space/api/ohlcv",
    params={
        "symbol": "BTCUSDT",
        "interval": "1h",
        "limit": 100
    }
)
data = response.json()
print(f"Got {data['count']} candles")
```

### 2. دریافت قیمت‌های برتر
```python
response = requests.get(
    "https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/prices/top",
    params={"limit": 10}
)
prices = response.json()
print(f"Top {prices['count']} cryptocurrencies")
```

### 3. دریافت سیگنال‌های معاملاتی
```python
response = requests.get(
    "https://really-amin-datasourceforcryptocurrency.hf.space/api/analysis/signals",
    params={"symbol": "BTCUSDT", "timeframe": "1h"}
)
signals = response.json()
print(f"Signal: {signals['signal']}, Trend: {signals['trend']}")
```

### 4. تحلیل احساسات با HuggingFace
```python
response = requests.post(
    "https://really-amin-datasourceforcryptocurrency.hf.space/api/hf/sentiment",
    json={"texts": ["Bitcoin is going to the moon!"]}
)
sentiment = response.json()
print(sentiment)
```

---

## 🎯 یکپارچه‌سازی با سیستم موجود

این پرووایدرها به طور خودکار در سیستم موجود یکپارچه می‌شوند:

### 1. در Gradio Dashboard (app.py):
```python
# پرووایدرها به طور خودکار load می‌شوند
providers = get_providers_table("All")
# شامل 95 پرووایدر (از جمله 2 پرووایدر جدید)
```

### 2. در API Monitoring:
```python
# سیستم monitoring به طور خودکار پرووایدرهای جدید را شناسایی می‌کند
from provider_manager import ProviderManager
manager = ProviderManager()
stats = manager.get_all_stats()
# شامل آمار 95 پرووایدر
```

### 3. در Collectors:
```python
# Collectors می‌توانند از endpoint‌های جدید استفاده کنند
import collectors
success, count = collectors.collect_from_provider('huggingface_space_api')
```

---

## 🧪 تست endpoint‌های جدید

### تست دستی:
```bash
# تست health
curl https://really-amin-datasourceforcryptocurrency.hf.space/health

# تست OHLCV
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/ohlcv?symbol=BTCUSDT&interval=1h&limit=10"

# تست top prices
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/prices/top?limit=5"

# تست signals
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/analysis/signals?symbol=BTCUSDT"

# تست HF health
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/hf/health"
```

### تست خودکار:
```bash
# استفاده از اسکریپت تست
chmod +x TEST_ENDPOINTS.sh
./TEST_ENDPOINTS.sh
```

---

## 📂 فایل‌های مربوطه

### فایل‌های به‌روز شده:
- ✅ `providers_config_extended.json` - اضافه شدن 2 پرووایدر جدید
- ✅ `providers_config_extended.backup.json` - نسخه پشتیبان

### فایل‌های مرتبط:
- `hf_unified_server.py` - سرور API که endpoint‌ها را ارائه می‌دهد
- `app.py` - Gradio dashboard که پرووایدرها را نمایش می‌دهد
- `main.py` - Entry point اصلی

---

## 🔄 نحوه بازگرداندن تغییرات (در صورت نیاز)

اگر نیاز به بازگرداندن تغییرات داشتید:

```bash
# بازگرداندن از backup
cp providers_config_extended.backup.json providers_config_extended.json
```

یا استفاده از git:
```bash
git checkout providers_config_extended.json
```

---

## ✅ چک‌لیست تأیید

- [x] فایل JSON معتبر است
- [x] هیچ syntax error ندارد
- [x] 2 پرووایدر جدید اضافه شد
- [x] 25 endpoint جدید قابل دسترس است
- [x] backup از فایل قبلی گرفته شد
- [x] مستندات کامل ایجاد شد
- [x] نمونه کدها آماده است

---

## 🎉 نتیجه

✅ **موفق!** فایل `providers_config_extended.json` با موفقیت به‌روز شد.

### قبل از بروزرسانی:
- 93 پرووایدر
- هیچ endpoint مستقیم به HuggingFace Space نداشتیم

### بعد از بروزرسانی:
- **95 پرووایدر** (+2)
- **25 endpoint جدید**
- دسترسی مستقیم به HuggingFace Space
- یکپارچه‌سازی کامل با سیستم موجود

---

**نسخه**: 3.2.0  
**تاریخ**: 2025-11-17  
**وضعیت**: ✅ تکمیل شده و آماده استفاده

🚀 حالا سیستم شما می‌تواند از تمام endpoint‌های HuggingFace Space استفاده کند!
