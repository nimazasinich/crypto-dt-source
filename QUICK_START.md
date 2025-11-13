# 🚀 راهنمای سریع شروع - Quick Start Guide

## ⚡ نصب و راه‌اندازی سریع

### 1️⃣ نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### 2️⃣ Import منابع از فایل‌های JSON
```bash
python import_resources.py
```
این اسکریپت به‌طور خودکار همه منابع را از فایل‌های JSON موجود import می‌کند.

### 3️⃣ راه‌اندازی سرور
```bash
# روش 1: استفاده از اسکریپت راه‌انداز
python start_server.py

# روش 2: مستقیم
python api_server_extended.py

# روش 3: با uvicorn
uvicorn api_server_extended:app --reload --host 0.0.0.0 --port 8000
```

### 4️⃣ دسترسی به داشبورد
```
http://localhost:8000
```

## 📋 تب‌های داشبورد

### 📊 Market
- آمار کلی بازار
- لیست کریپتوکارنسی‌ها
- نمودارها و ترندینگ

### 📡 API Monitor
- وضعیت همه ارائه‌دهندگان
- زمان پاسخ
- Health Check

### ⚡ Advanced
- Export JSON/CSV
- Backup
- Clear Cache
- Activity Logs

### ⚙️ Admin
- افزودن API جدید
- تنظیمات
- آمار کلی

### 🤗 HuggingFace
- مدل‌های Sentiment Analysis
- Datasets
- جستجو در Registry

### 🔄 Pools
- مدیریت Pool‌ها
- افزودن/حذف اعضا
- چرخش دستی

### 📋 Logs (جدید!)
- نمایش لاگ‌ها با فیلتر
- Export به JSON/CSV
- جستجو و آمار

### 📦 Resources (جدید!)
- مدیریت منابع API
- Import/Export
- Backup
- فیلتر بر اساس Category

## 🔧 استفاده از API

### دریافت لاگ‌ها
```bash
# همه لاگ‌ها
curl http://localhost:8000/api/logs

# فیلتر بر اساس Level
curl http://localhost:8000/api/logs?level=error

# جستجو
curl http://localhost:8000/api/logs?search=timeout
```

### Export لاگ‌ها
```bash
# Export به JSON
curl http://localhost:8000/api/logs/export/json?level=error

# Export به CSV
curl http://localhost:8000/api/logs/export/csv
```

### مدیریت منابع
```bash
# دریافت همه منابع
curl http://localhost:8000/api/resources

# Export منابع
curl http://localhost:8000/api/resources/export/json

# Backup
curl -X POST http://localhost:8000/api/resources/backup

# Import
curl -X POST "http://localhost:8000/api/resources/import/json?file_path=api-resources/crypto_resources_unified_2025-11-11.json&merge=true"
```

## 📝 مثال‌های استفاده

### افزودن Provider جدید
```python
from resource_manager import ResourceManager

manager = ResourceManager()

provider = {
    "id": "my_new_api",
    "name": "My New API",
    "category": "market_data",
    "base_url": "https://api.example.com",
    "requires_auth": False,
    "priority": 5,
    "weight": 50,
    "free": True
}

manager.add_provider(provider)
manager.save_resources()
```

### ثبت لاگ
```python
from log_manager import log_info, log_error, LogCategory

# لاگ Info
log_info(LogCategory.PROVIDER, "Provider health check completed", 
         provider_id="coingecko", response_time=234.5)

# لاگ Error
log_error(LogCategory.PROVIDER, "Provider failed", 
          provider_id="etherscan", error="Timeout")
```

### استفاده از Provider Manager
```python
from provider_manager import ProviderManager
import asyncio

async def main():
    manager = ProviderManager()
    
    # Health Check
    await manager.health_check_all()
    
    # دریافت Provider از Pool
    provider = manager.get_next_from_pool("primary_market_data_pool")
    if provider:
        print(f"Selected: {provider.name}")
    
    await manager.close_session()

asyncio.run(main())
```

## 🐳 استفاده با Docker

```bash
# Build
docker build -t crypto-monitor .

# Run
docker run -p 8000:8000 crypto-monitor

# یا با docker-compose
docker-compose up -d
```

## 🔍 عیب‌یابی

### مشکل: Port در حال استفاده است
```bash
# تغییر پورت
uvicorn api_server_extended:app --port 8001
```

### مشکل: فایل‌های JSON یافت نشد
```bash
# بررسی وجود فایل‌ها
ls -la api-resources/
ls -la providers_config*.json
```

### مشکل: Import منابع ناموفق
```bash
# بررسی ساختار JSON
python -m json.tool api-resources/crypto_resources_unified_2025-11-11.json | head -20
```

## 📚 مستندات بیشتر

- [README.md](README.md) - مستندات کامل انگلیسی
- [README_FA.md](README_FA.md) - مستندات کامل فارسی
- [api-resources/README.md](api-resources/README.md) - راهنمای منابع API

## 🆘 پشتیبانی

در صورت بروز مشکل:
1. لاگ‌ها را بررسی کنید: `logs/app.log`
2. از تب Logs در داشبورد استفاده کنید
3. آمار سیستم را بررسی کنید: `/api/status`

---

**موفق باشید! 🚀**
