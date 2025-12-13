# 🔧 راهنمای اصلاح فایل‌های سرور

## 📋 فایل‌هایی که باید اصلاح شوند

### ✅ فایل اصلی: `hf_unified_server.py`

این فایل اصلی است که Space شما از آن استفاده می‌کند (از طریق `main.py`).

**مسیر:** `hf_unified_server.py`

**مشکل:** Router `unified_service_api` ممکن است با خطا load شود یا register نشود.

**راه حل:**

1. **چک کنید router import شده:**
   ```python
   # خط 26 باید این باشد:
   from backend.routers.unified_service_api import router as service_router
   ```

2. **چک کنید router register شده:**
   ```python
   # خط 173-176 باید این باشد:
   try:
       app.include_router(service_router)  # Main unified service
       logger.info("✅ Unified Service API Router loaded")
   except Exception as e:
       logger.error(f"Failed to include service_router: {e}")
       import traceback
       traceback.print_exc()  # اضافه کنید برای debug
   ```

3. **اگر router load نمی‌شود، چک کنید:**
   - آیا فایل `backend/routers/unified_service_api.py` وجود دارد؟
   - آیا dependencies نصب شده‌اند؟
   - آیا import errors وجود دارد؟

---

### ✅ فایل جایگزین: `api_server_extended.py`

اگر Space شما از این فایل استفاده می‌کند:

**مسیر:** `api_server_extended.py`

**مشکل:** Router `unified_service_api` در این فایل register نشده.

**راه حل:**

در فایل `api_server_extended.py`، بعد از خط 825 (بعد از resources_router)، اضافه کنید:

```python
# ===== Include Unified Service API Router =====
try:
    from backend.routers.unified_service_api import router as unified_service_router
    app.include_router(unified_service_router)
    print("✓ ✅ Unified Service API Router loaded")
except Exception as unified_error:
    print(f"⚠ Failed to load Unified Service API Router: {unified_error}")
    import traceback
    traceback.print_exc()
```

---

## 🔍 تشخیص اینکه Space از کدام فایل استفاده می‌کند

### روش 1: چک کردن `main.py`

```python
# main.py را باز کنید
# اگر این خط را دارد:
from hf_unified_server import app
# پس از hf_unified_server.py استفاده می‌کند

# اگر این خط را دارد:
from api_server_extended import app
# پس از api_server_extended.py استفاده می‌کند
```

### روش 2: چک کردن لاگ‌های Space

به Space logs بروید و ببینید:
- اگر می‌گوید: `✅ Loaded hf_unified_server` → از `hf_unified_server.py` استفاده می‌کند
- اگر می‌گوید: `✅ FastAPI app loaded` → از `api_server_extended.py` استفاده می‌کند

---

## 📝 تغییرات دقیق

### تغییر 1: `hf_unified_server.py`

**خط 173-176 را به این تغییر دهید:**

```python
# Include routers
try:
    app.include_router(service_router)  # Main unified service
    logger.info("✅ Unified Service API Router loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to include service_router: {e}")
    import traceback
    traceback.print_exc()  # برای debug
    # اما ادامه دهید - fallback نکنید
```

**نکته:** اگر router load نمی‌شود، خطا را در لاگ ببینید و مشکل را fix کنید.

---

### تغییر 2: `api_server_extended.py` (اگر استفاده می‌شود)

**بعد از خط 825 اضافه کنید:**

```python
# ===== Include Unified Service API Router =====
try:
    from backend.routers.unified_service_api import router as unified_service_router
    app.include_router(unified_service_router)
    print("✓ ✅ Unified Service API Router loaded - /api/service/* endpoints available")
except Exception as unified_error:
    print(f"⚠ Failed to load Unified Service API Router: {unified_error}")
    import traceback
    traceback.print_exc()
```

---

## 🐛 Fix کردن مشکلات HuggingFace Models

### مشکل: مدل‌ها پیدا نمی‌شوند

**فایل:** `backend/services/direct_model_loader.py` یا فایل مشابه

**تغییر:**

```python
# مدل‌های جایگزین
SENTIMENT_MODELS = {
    "cryptobert_elkulako": "ProsusAI/finbert",  # جایگزین
    "default": "cardiffnlp/twitter-roberta-base-sentiment"
}

SUMMARIZATION_MODELS = {
    "bart": "facebook/bart-large",  # جایگزین
    "default": "google/pegasus-xsum"
}
```

یا در فایل config:

```python
# config.py یا ai_models.py
HUGGINGFACE_MODELS = {
    "sentiment_twitter": "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "sentiment_financial": "ProsusAI/finbert",
    "summarization": "facebook/bart-large",  # تغییر از bart-large-cnn
    "crypto_sentiment": "ProsusAI/finbert",  # تغییر از ElKulako/cryptobert
}
```

---

## ✅ چک‌لیست اصلاحات

### مرحله 1: تشخیص فایل اصلی
- [ ] `main.py` را باز کنید
- [ ] ببینید از کدام فایل import می‌کند
- [ ] فایل اصلی را مشخص کنید

### مرحله 2: اصلاح Router Registration
- [ ] فایل اصلی را باز کنید (`hf_unified_server.py` یا `api_server_extended.py`)
- [ ] چک کنید `service_router` import شده
- [ ] چک کنید `app.include_router(service_router)` وجود دارد
- [ ] اگر نیست، اضافه کنید
- [ ] Error handling اضافه کنید

### مرحله 3: Fix کردن Models
- [ ] فایل config مدل‌ها را پیدا کنید
- [ ] مدل‌های جایگزین را تنظیم کنید
- [ ] یا از مدل‌های معتبر استفاده کنید

### مرحله 4: تست
- [ ] Space را restart کنید
- [ ] لاگ‌ها را چک کنید
- [ ] تست کنید: `GET /api/service/rate?pair=BTC/USDT`
- [ ] باید 200 برگرداند (نه 404)

---

## 🔍 Debug Steps

### 1. چک کردن Router Load

در Space logs ببینید:
```
✅ Unified Service API Router loaded successfully
```

اگر این پیام را نمی‌بینید، router load نشده.

### 2. چک کردن Endpointها

بعد از restart، تست کنید:
```bash
curl https://your-space.hf.space/api/service/rate?pair=BTC/USDT
```

اگر 404 می‌دهد، router register نشده.

### 3. چک کردن Import Errors

در لاگ‌ها دنبال این خطاها بگردید:
```
Failed to include service_router: [error]
ImportError: cannot import name 'router' from 'backend.routers.unified_service_api'
```

---

## 📝 مثال کامل تغییرات

### برای `hf_unified_server.py`:

```python
# خط 26 - Import (باید وجود داشته باشد)
from backend.routers.unified_service_api import router as service_router

# خط 173-180 - Registration (به این تغییر دهید)
try:
    app.include_router(service_router)  # Main unified service
    logger.info("✅ Unified Service API Router loaded - /api/service/* endpoints available")
except ImportError as e:
    logger.error(f"❌ Import error for service_router: {e}")
    logger.error("Check if backend/routers/unified_service_api.py exists")
    import traceback
    traceback.print_exc()
except Exception as e:
    logger.error(f"❌ Failed to include service_router: {e}")
    import traceback
    traceback.print_exc()
```

---

## 🚀 بعد از اصلاحات

1. **Space را restart کنید**
2. **لاگ‌ها را چک کنید:**
   - باید ببینید: `✅ Unified Service API Router loaded`
3. **تست کنید:**
   ```bash
   curl https://your-space.hf.space/api/service/rate?pair=BTC/USDT
   ```
4. **اگر هنوز 404 می‌دهد:**
   - لاگ‌ها را دوباره چک کنید
   - مطمئن شوید router import شده
   - مطمئن شوید router register شده

---

## 📞 اگر مشکل حل نشد

1. **لاگ‌های کامل Space را ببینید**
2. **Import errors را پیدا کنید**
3. **Dependencies را چک کنید:**
   ```bash
   pip list | grep fastapi
   pip list | grep backend
   ```
4. **فایل router را چک کنید:**
   - آیا `backend/routers/unified_service_api.py` وجود دارد؟
   - آیا `router = APIRouter(...)` در آن تعریف شده؟

---

**موفق باشید! 🚀**

