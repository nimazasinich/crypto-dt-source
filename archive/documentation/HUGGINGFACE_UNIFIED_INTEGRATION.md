# HuggingFace Unified Integration Guide

## 🎯 هدف

تمرکز **تمام** درخواست‌های داده در HuggingFace Space به‌جای استفاده مستقیم از API های خارجی.

## ✅ قبل و بعد

### ❌ قبل (مشکل):
```
کلاینت → CoinMarketCap API (مستقیم)
کلاینت → NewsAPI (مستقیم)
کلاینت → Etherscan API (مستقیم)
...
```

### ✅ بعد (راه‌حل):
```
کلاینت → HuggingFace Space API → داده‌های واقعی
```

---

## 📦 فایل‌های جدید ایجاد شده

### 1. `backend/services/hf_unified_client.py`

**کلاینت یکپارچه HuggingFace** - مسئول تمام ارتباطات با HuggingFace Space

**ویژگی‌ها:**
- ✅ Singleton Pattern (یک نمونه در کل برنامه)
- ✅ Retry Mechanism (تلاش مجدد در صورت خطا)
- ✅ Caching (کش داده‌ها برای کاهش درخواست‌ها)
- ✅ Error Handling (مدیریت خطاها)
- ✅ Logging (ثبت لاگ برای دیباگ)

**متدهای موجود:**

| متد | توضیحات | Endpoint HF |
|-----|---------|-------------|
| `get_market_prices()` | دریافت قیمت‌های بازار | `GET /api/market` |
| `get_market_history()` | دریافت OHLCV | `GET /api/market/history` |
| `analyze_sentiment()` | تحلیل احساسات | `POST /api/sentiment/analyze` |
| `get_news()` | دریافت اخبار | `GET /api/news` |
| `get_blockchain_gas_prices()` | قیمت گس بلاکچین | `GET /api/crypto/blockchain/gas` |
| `get_blockchain_stats()` | آمار بلاکچین | `GET /api/crypto/blockchain/stats` |
| `get_whale_transactions()` | تراکنش‌های نهنگ | `GET /api/crypto/whales/transactions` |
| `get_whale_stats()` | آمار نهنگ‌ها | `GET /api/crypto/whales/stats` |
| `health_check()` | بررسی سلامت | `GET /api/health` |
| `get_system_status()` | وضعیت سیستم | `GET /api/status` |

**مثال استفاده:**

```python
from backend.services.hf_unified_client import get_hf_client

# دریافت کلاینت (Singleton)
client = get_hf_client()

# دریافت قیمت‌های بازار
result = await client.get_market_prices(
    symbols=["BTC", "ETH", "BNB"],
    limit=100
)

if result.get("success"):
    for item in result.get("data", []):
        print(f"{item['symbol']}: ${item['price']:,.2f}")
```

---

### 2. `backend/routers/real_data_api_unified_hf.py`

**Router یکپارچه** - تمام endpoint های API که **فقط** از HuggingFace استفاده می‌کنند

**Endpoints موجود:**

#### 📊 Market Data
- `GET /api/market` - لیست قیمت‌های بازار
- `GET /api/market/history` - داده‌های OHLCV
- `GET /api/market/pairs` - جفت‌های معاملاتی
- `GET /api/market/tickers` - tickers مرتب‌شده

#### 💭 Sentiment & AI
- `POST /api/sentiment/analyze` - تحلیل احساسات

#### 📰 News
- `GET /api/news` - اخبار کریپتو
- `GET /api/news/latest` - آخرین اخبار

#### ⛓️ Blockchain
- `GET /api/blockchain/gas` - قیمت گس
- `GET /api/blockchain/stats` - آمار بلاکچین

#### 🐋 Whale Tracking
- `GET /api/whales/transactions` - تراکنش‌های نهنگ
- `GET /api/whales/stats` - آمار نهنگ‌ها

#### 🏥 Health & Status
- `GET /api/health` - بررسی سلامت
- `GET /api/status` - وضعیت سیستم
- `GET /api/providers` - لیست ارائه‌دهندگان

---

### 3. `test_hf_unified_integration.py`

**Test Suite کامل** - اعتبارسنجی همه قابلیت‌ها

**Tests موجود:**
1. ✅ Market Prices
2. ✅ OHLCV History
3. ✅ Sentiment Analysis
4. ✅ News
5. ✅ Blockchain Gas
6. ✅ Health Check

**نحوه اجرا:**

```bash
python test_hf_unified_integration.py
```

**خروجی مورد انتظار:**
```
🔬 HuggingFace Unified Integration Test Suite
================================================

🧪 TEST 1: Market Prices
✅ Success: True
📊 Data count: 10
🔖 Source: hf_engine

...

📊 TEST SUMMARY
================================================
✅ PASSED - Market Prices
✅ PASSED - OHLCV History
✅ PASSED - Sentiment Analysis
✅ PASSED - News
✅ PASSED - Blockchain Gas
✅ PASSED - Health Check

📈 Total: 6/6 tests passed (100.0%)
🎉 All tests passed!
```

---

## 🔧 تنظیمات محیط (Environment Variables)

این متغیرها در فایل `.env` تنظیم شوند:

```bash
# HuggingFace Space Configuration
HF_SPACE_BASE_URL=https://really-amin-datasourceforcryptocurrency.hf.space
HF_API_TOKEN=your_hf_token_here

# Optional: Timeout settings
HF_TIMEOUT_SECONDS=30
HF_RETRY_ATTEMPTS=3
```

---

## 📝 نحوه استفاده در پروژه

### قدم 1: Import کلاینت

```python
from backend.services.hf_unified_client import get_hf_client
```

### قدم 2: دریافت نمونه Singleton

```python
client = get_hf_client()
```

### قدم 3: استفاده از متدها

```python
# مثال 1: دریافت قیمت Bitcoin
result = await client.get_market_prices(symbols=["BTC"], limit=1)
btc_price = result['data'][0]['price']

# مثال 2: تحلیل احساسات
sentiment_result = await client.analyze_sentiment(
    text="Bitcoin is going to the moon! 🚀"
)
print(sentiment_result['data']['sentiment'])  # positive

# مثال 3: دریافت OHLCV
ohlcv = await client.get_market_history(
    symbol="BTCUSDT",
    timeframe="1h",
    limit=24
)
print(f"Got {len(ohlcv['data'])} candles")
```

---

## 🔄 تغییرات در router ها

### قبل:

```python
# استفاده مستقیم از API های خارجی
from backend.services.real_api_clients import cmc_client, news_client

@router.get("/api/market")
async def get_market():
    # درخواست مستقیم به CoinMarketCap
    data = await cmc_client.get_latest_listings()
    return data
```

### بعد:

```python
# استفاده از HuggingFace Unified Client
from backend.services.hf_unified_client import get_hf_client

hf_client = get_hf_client()

@router.get("/api/market")
async def get_market():
    # درخواست به HuggingFace Space
    data = await hf_client.get_market_prices()
    return data
```

---

## ⚡ مزایا

### 1. **تمرکز داده‌ها**
- همه درخواست‌ها از یک منبع (HuggingFace)
- مدیریت آسان‌تر
- کاهش پیچیدگی

### 2. **Cache یکپارچه**
- Cache در سطح کلاینت
- کاهش درخواست‌های تکراری
- بهبود سرعت

### 3. **Error Handling بهتر**
- Retry مکانیزم
- لاگ‌گذاری مرکزی
- مدیریت خطا در یک نقطه

### 4. **قابل تست بودن**
- Test Suite کامل
- جداسازی منطق
- Mock کردن آسان‌تر

### 5. **Scalability**
- افزودن endpoint جدید آسان
- تغییر URL بدون تغییر کد
- پشتیبانی از چند Instance

---

## 🛠️ نحوه افزودن Endpoint جدید

### قدم 1: افزودن متد به `hf_unified_client.py`

```python
async def get_custom_data(self, param: str) -> Dict[str, Any]:
    """توضیحات"""
    return await self._request(
        "GET",
        "/api/custom/endpoint",
        params={"param": param},
        cache_type="custom"
    )
```

### قدم 2: افزودن route به `real_data_api_unified_hf.py`

```python
@router.get("/api/custom")
async def get_custom(param: str = Query(...)):
    """توضیحات"""
    try:
        result = await hf_client.get_custom_data(param)
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
```

### قدم 3: افزودن تست به `test_hf_unified_integration.py`

```python
async def test_custom_data():
    """Test Custom Data"""
    client = get_hf_client()
    result = await client.get_custom_data("test")
    print(f"✅ Custom data: {result}")
    return True
```

---

## 🔍 Debugging

### چک کردن لاگ‌ها

```bash
# فیلتر لاگ‌های HuggingFace
tail -f logs/app.log | grep "HF"
```

### لاگ‌های مفید:

```
✅ HF Request: GET /api/market (attempt 1/3)
📦 Cache HIT: abc123 (age: 15.2s)
💾 Cache SET: abc123 (ttl: 30s)
❌ HF Request failed (attempt 1/3): 503 - Service Unavailable
```

---

## 📊 Performance

### Cache TTL (زمان نگهداری در کش):

| نوع داده | TTL | دلیل |
|----------|-----|------|
| Market Prices | 30s | تغییر سریع قیمت |
| OHLCV | 60s | داده‌های تاریخی |
| News | 300s (5min) | محتوای ثابت |
| Sentiment | 0s (No cache) | نیاز به تحلیل هر بار |
| Blockchain Stats | 60s | تغییرات کند |

### Retry Strategy:

- تلاش اول: بلافاصله
- تلاش دوم: بعد از 1 ثانیه
- تلاش سوم: بعد از 2 ثانیه
- بعد از 3 تلاش: خطا

---

## ⚠️ نکات مهم

### 1. **Singleton Pattern**
- فقط یک نمونه از client در کل برنامه
- استفاده از `get_hf_client()` همیشه

```python
# ✅ درست
client = get_hf_client()

# ❌ اشتباه
client = HuggingFaceUnifiedClient()
```

### 2. **Async/Await**
- همه متدها async هستند
- حتماً با `await` استفاده شوند

```python
# ✅ درست
result = await client.get_market_prices()

# ❌ اشتباه (coroutine object برمی‌گرداند)
result = client.get_market_prices()
```

### 3. **Error Handling**
- همیشه در try/except قرار گیرند
- خطاهای مناسب به کاربر برگردانید

```python
try:
    result = await client.get_market_prices()
    if not result.get("success"):
        # Handle HF error
        error_message = result.get("error")
except Exception as e:
    # Handle network/unexpected errors
    logger.error(f"Failed: {e}")
```

---

## 📚 منابع

- **فایل منبع داده**: `crypto_resources_unified_2025-11-11.json`
- **کلاینت یکپارچه**: `backend/services/hf_unified_client.py`
- **Router یکپارچه**: `backend/routers/real_data_api_unified_hf.py`
- **Test Suite**: `test_hf_unified_integration.py`
- **HuggingFace Space**: https://really-amin-datasourceforcryptocurrency.hf.space

---

## ✉️ ارتباط و پشتیبانی

در صورت بروز مشکل:

1. چک کردن لاگ‌ها (`logs/app.log`)
2. اجرای Test Suite (`python test_hf_unified_integration.py`)
3. بررسی متغیرهای محیطی (`.env`)
4. اطمینان از در دسترس بودن HuggingFace Space

---

## 🎯 خلاصه

✅ **تمام** داده‌ها از HuggingFace Space
✅ **بدون** درخواست مستقیم به API های خارجی
✅ **کش** یکپارچه برای بهینه‌سازی
✅ **Retry** برای افزایش قابلیت اطمینان
✅ **Test** کامل برای اعتبارسنجی

---

**نسخه**: 3.0.0-unified-hf
**تاریخ**: 2025-11-25
**وضعیت**: ✅ آماده تولید
