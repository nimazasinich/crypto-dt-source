# ⚡ مرجع سریع - فایل‌های فعال

## 🎯 فایل‌های اصلی (فقط این‌ها استفاده می‌شوند!)

### 📄 سرور
```
✅ api_server_extended.py  ← سرور اصلی (این را اجرا کنید!)
```

### 📦 Config Files
```
✅ providers_config_extended.json      ← ProviderManager استفاده می‌کند
✅ providers_config_ultimate.json       ← ResourceManager استفاده می‌کند
✅ crypto_resources_unified_2025-11-11.json  ← UnifiedConfigLoader استفاده می‌کند
```

### 🎨 Frontend
```
✅ unified_dashboard.html  ← داشبورد اصلی
✅ static/css/connection-status.css
✅ static/js/websocket-client.js
```

### 🔧 Core Modules
```
✅ provider_manager.py     ← مدیریت Providerها
✅ resource_manager.py      ← مدیریت منابع
✅ log_manager.py           ← مدیریت لاگ‌ها
```

### 🛠️ Backend Services
```
✅ backend/services/auto_discovery_service.py
✅ backend/services/connection_manager.py
✅ backend/services/diagnostics_service.py
✅ backend/services/unified_config_loader.py
```

---

## ❌ فایل‌های قدیمی (استفاده نمی‌شوند)

```
❌ main.py
❌ app.py
❌ enhanced_server.py
❌ production_server.py
❌ real_server.py
❌ simple_server.py

❌ index.html
❌ dashboard.html
❌ enhanced_dashboard.html
❌ admin.html

❌ config.py
❌ scheduler.py
```

---

## 🚀 راه‌اندازی سریع

```bash
# 1. نصب وابستگی‌ها
pip install -r requirements.txt

# 2. اجرای سرور
python api_server_extended.py

# 3. باز کردن مرورگر
http://localhost:8000/unified_dashboard.html
```

---

## 📊 ساختار ساده

```
api_server_extended.py (سرور اصلی)
    │
    ├── ProviderManager → providers_config_extended.json
    ├── ResourceManager → providers_config_ultimate.json
    ├── UnifiedConfigLoader → crypto_resources_unified_2025-11-11.json
    ├── AutoDiscoveryService
    ├── ConnectionManager (WebSocket)
    └── DiagnosticsService

unified_dashboard.html (داشبورد)
    │
    ├── static/css/connection-status.css
    └── static/js/websocket-client.js
```

---

## 🔍 کدام فایل Config برای چه کاری؟

| کار | استفاده از |
|-----|------------|
| مدیریت Providerها و Poolها | `providers_config_extended.json` |
| مدیریت منابع API | `providers_config_ultimate.json` |
| بارگذاری یکپارچه همه منابع | `crypto_resources_unified_2025-11-11.json` |

---

**💡 نکته:** اگر می‌خواهید Provider جدید اضافه کنید:
- برای ProviderManager → `providers_config_extended.json` را ویرایش کنید
- برای ResourceManager → `providers_config_ultimate.json` را ویرایش کنید
- یا از API endpoints استفاده کنید: `/api/resources` یا `/api/pools`

