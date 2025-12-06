# 🌳 ساختار پروژه Crypto Monitor - نقشه کامل

## 📋 فهرست مطالب
1. [ساختار کلی پروژه](#ساختار-کلی-پروژه)
2. [فایل‌های اصلی و مسئولیت‌ها](#فایل‌های-اصلی-و-مسئولیت‌ها)
3. [فایل‌های پیکربندی](#فایل‌های-پیکربندی)
4. [سرویس‌ها و ماژول‌ها](#سرویس‌ها-و-ماژول‌ها)
5. [رابط کاربری](#رابط-کاربری)
6. [نحوه استفاده از فایل‌های Config](#نحوه-استفاده-از-فایل‌های-config)

---

## 🌲 ساختار کلی پروژه

```
crypto-monitor-hf-full-fixed-v4-realapis/
│
├── 📄 فایل‌های اصلی سرور
│   ├── api_server_extended.py          ⭐ سرور اصلی FastAPI (استفاده می‌شود)
│   ├── main.py                         ⚠️ قدیمی - استفاده نمی‌شود
│   ├── app.py                          ⚠️ قدیمی - استفاده نمی‌شود
│   ├── enhanced_server.py              ⚠️ قدیمی - استفاده نمی‌شود
│   ├── production_server.py            ⚠️ قدیمی - استفاده نمی‌شود
│   ├── real_server.py                  ⚠️ قدیمی - استفاده نمی‌شود
│   └── simple_server.py                ⚠️ قدیمی - استفاده نمی‌شود
│
├── 📦 فایل‌های پیکربندی (Config Files)
│   ├── providers_config_extended.json     ✅ استفاده می‌شود (ProviderManager)
│   ├── providers_config_ultimate.json      ✅ استفاده می‌شود (ResourceManager)
│   ├── crypto_resources_unified_2025-11-11.json  ✅ استفاده می‌شود (UnifiedConfigLoader)
│   ├── all_apis_merged_2025.json          ✅ استفاده می‌شود (UnifiedConfigLoader)
│   └── ultimate_crypto_pipeline_2025_NZasinich.json  ✅ استفاده می‌شود (UnifiedConfigLoader)
│
├── 🎨 رابط کاربری (Frontend)
│   ├── unified_dashboard.html             ⭐ داشبورد اصلی (استفاده می‌شود)
│   ├── index.html                         ⚠️ قدیمی
│   ├── dashboard.html                     ⚠️ قدیمی
│   ├── enhanced_dashboard.html            ⚠️ قدیمی
│   ├── admin.html                         ⚠️ قدیمی
│   ├── pool_management.html               ⚠️ قدیمی
│   └── hf_console.html                    ⚠️ قدیمی
│
├── 🧩 ماژول‌های اصلی (Core Modules)
│   ├── provider_manager.py                ✅ مدیریت Providerها و Poolها
│   ├── resource_manager.py                ✅ مدیریت منابع API
│   ├── log_manager.py                     ✅ مدیریت لاگ‌ها
│   ├── config.py                          ⚠️ قدیمی - استفاده نمی‌شود
│   └── scheduler.py                       ⚠️ قدیمی - استفاده نمی‌شود
│
├── 🔧 سرویس‌های بکند (Backend Services)
│   └── backend/
│       ├── services/
│       │   ├── auto_discovery_service.py      ✅ جستجوی خودکار منابع رایگان
│       │   ├── connection_manager.py          ✅ مدیریت اتصالات WebSocket
│       │   ├── diagnostics_service.py        ✅ اشکال‌یابی و تعمیر خودکار
│       │   ├── unified_config_loader.py       ✅ بارگذاری یکپارچه Configها
│       │   ├── scheduler_service.py           ✅ زمان‌بندی پیشرفته
│       │   ├── persistence_service.py         ✅ ذخیره‌سازی داده‌ها
│       │   ├── websocket_service.py           ✅ سرویس WebSocket
│       │   ├── ws_service_manager.py          ✅ مدیریت سرویس‌های WebSocket
│       │   ├── hf_client.py                   ✅ کلاینت HuggingFace
│       │   ├── hf_registry.py                 ✅ رجیستری مدل‌های HuggingFace
│       │   └── __init__.py
│       │
│       └── routers/
│           ├── integrated_api.py              ✅ APIهای یکپارچه
│           ├── hf_connect.py                  ✅ اتصال HuggingFace
│           └── __init__.py
│
├── 📡 API Endpoints
│   └── api/
│       ├── endpoints.py                       ⚠️ قدیمی
│       ├── pool_endpoints.py                  ⚠️ قدیمی
│       ├── websocket.py                       ⚠️ قدیمی
│       └── ... (سایر فایل‌های قدیمی)
│
├── 🎯 Collectors (جمع‌آوری داده)
│   └── collectors/
│       ├── market_data.py                     ⚠️ قدیمی
│       ├── market_data_extended.py            ⚠️ قدیمی
│       ├── news.py                            ⚠️ قدیمی
│       ├── sentiment.py                       ⚠️ قدیمی
│       └── ... (سایر collectors قدیمی)
│
├── 🎨 فایل‌های استاتیک (Static Files)
│   └── static/
│       ├── css/
│       │   └── connection-status.css          ✅ استایل وضعیت اتصال
│       └── js/
│           └── websocket-client.js            ✅ کلاینت WebSocket
│
├── 📚 مستندات (Documentation)
│   ├── README.md                              ✅ مستندات اصلی
│   ├── README_FA.md                           ✅ مستندات فارسی
│   ├── WEBSOCKET_GUIDE.md                     ✅ راهنمای WebSocket
│   ├── REALTIME_FEATURES_FA.md                ✅ ویژگی‌های بلادرنگ
│   └── ... (سایر فایل‌های مستندات)
│
├── 🧪 تست‌ها (Tests)
│   ├── test_websocket.html                    ✅ صفحه تست WebSocket
│   ├── test_websocket_dashboard.html          ✅ صفحه تست Dashboard
│   ├── test_providers.py                      ⚠️ تست قدیمی
│   └── tests/                                 ⚠️ تست‌های قدیمی
│
├── 📁 دایرکتوری‌های داده
│   ├── data/                                  ✅ ذخیره داده‌ها
│   ├── logs/                                  ✅ ذخیره لاگ‌ها
│   └── database/                              ⚠️ قدیمی
│
└── 📦 سایر فایل‌ها
    ├── requirements.txt                       ✅ وابستگی‌های Python
    ├── start.bat                              ✅ اسکریپت راه‌اندازی
    ├── docker-compose.yml                     ✅ Docker Compose
    └── Dockerfile                             ✅ Dockerfile
```

---

## 📄 فایل‌های اصلی و مسئولیت‌ها

### ⭐ فایل‌های فعال (در حال استفاده)

#### 1. `api_server_extended.py` - سرور اصلی
**مسئولیت:**
- سرور FastAPI اصلی برنامه
- مدیریت تمام endpointها
- یکپارچه‌سازی تمام سرویس‌ها
- مدیریت WebSocket
- Startup validation

**وابستگی‌ها:**
- `provider_manager.py` → `providers_config_extended.json`
- `resource_manager.py` → `providers_config_ultimate.json`
- `backend/services/auto_discovery_service.py`
- `backend/services/connection_manager.py`
- `backend/services/diagnostics_service.py`

**نحوه اجرا:**
```bash
python api_server_extended.py
# یا
uvicorn api_server_extended:app --host 0.0.0.0 --port 8000
```

---

#### 2. `provider_manager.py` - مدیریت Providerها
**مسئولیت:**
- مدیریت Providerهای API
- مدیریت Poolها و استراتژی‌های چرخش
- Health check
- Rate limiting
- Circuit breaker

**فایل Config استفاده شده:**
- `providers_config_extended.json` (پیش‌فرض)

**ساختار فایل Config:**
```json
{
  "providers": {
    "coingecko": { ... },
    "binance": { ... }
  },
  "pool_configurations": [ ... ]
}
```

---

#### 3. `resource_manager.py` - مدیریت منابع
**مسئولیت:**
- مدیریت منابع API
- Import/Export منابع
- Validation منابع
- Backup/Restore

**فایل Config استفاده شده:**
- `providers_config_ultimate.json` (پیش‌فرض)

**ساختار فایل Config:**
```json
{
  "providers": {
    "coingecko": { ... }
  },
  "schema_version": "3.0.0"
}
```

---

#### 4. `unified_dashboard.html` - داشبورد اصلی
**مسئولیت:**
- رابط کاربری اصلی
- نمایش داده‌های بازار
- مدیریت Providerها
- گزارشات و اشکال‌یابی
- اتصال WebSocket

**وابستگی‌ها:**
- `static/css/connection-status.css`
- `static/js/websocket-client.js`
- API endpoints از `api_server_extended.py`

---

### ⚠️ فایل‌های قدیمی (استفاده نمی‌شوند)

این فایل‌ها برای مرجع نگه داشته شده‌اند اما در حال حاضر استفاده نمی‌شوند:

- `main.py`, `app.py`, `enhanced_server.py` → جایگزین شده با `api_server_extended.py`
- `index.html`, `dashboard.html` → جایگزین شده با `unified_dashboard.html`
- `config.py`, `scheduler.py` → جایگزین شده با سرویس‌های جدید در `backend/services/`

---

## 📦 فایل‌های پیکربندی

### ✅ فایل‌های فعال

#### 1. `providers_config_extended.json`
**استفاده شده توسط:** `provider_manager.py`
**محتوای اصلی:**
- لیست Providerها با endpointها
- Pool configurations
- HuggingFace models
- Fallback strategy

**نحوه استفاده:**
```python
from provider_manager import ProviderManager

manager = ProviderManager(config_path="providers_config_extended.json")
```

---

#### 2. `providers_config_ultimate.json`
**استفاده شده توسط:** `resource_manager.py`
**محتوای اصلی:**
- لیست Providerها (فرمت متفاوت)
- Schema version
- Metadata

**نحوه استفاده:**
```python
from resource_manager import ResourceManager

manager = ResourceManager(config_file="providers_config_ultimate.json")
```

---

#### 3. `crypto_resources_unified_2025-11-11.json`
**استفاده شده توسط:** `backend/services/unified_config_loader.py`
**محتوای اصلی:**
- RPC nodes
- Block explorers
- Market data APIs
- DeFi protocols

**نحوه استفاده:**
```python
from backend.services.unified_config_loader import UnifiedConfigLoader

loader = UnifiedConfigLoader()
# به صورت خودکار این فایل را load می‌کند
```

---

#### 4. `all_apis_merged_2025.json`
**استفاده شده توسط:** `backend/services/unified_config_loader.py`
**محتوای اصلی:**
- APIs merged از منابع مختلف

---

#### 5. `ultimate_crypto_pipeline_2025_NZasinich.json`
**استفاده شده توسط:** `backend/services/unified_config_loader.py`
**محتوای اصلی:**
- Pipeline configuration
- API sources

---

### 🔄 تفاوت بین فایل‌های Config

| فایل | استفاده شده توسط | فرمت | تعداد Provider |
|------|------------------|------|----------------|
| `providers_config_extended.json` | ProviderManager | `{providers: {}, pool_configurations: []}` | ~100 |
| `providers_config_ultimate.json` | ResourceManager | `{providers: {}, schema_version: "3.0.0"}` | ~200 |
| `crypto_resources_unified_2025-11-11.json` | UnifiedConfigLoader | `{registry: {rpc_nodes: [], ...}}` | 200+ |
| `all_apis_merged_2025.json` | UnifiedConfigLoader | Merged format | متغیر |
| `ultimate_crypto_pipeline_2025_NZasinich.json` | UnifiedConfigLoader | Pipeline format | متغیر |

---

## 🔧 سرویس‌ها و ماژول‌ها

### Backend Services (`backend/services/`)

#### 1. `auto_discovery_service.py`
**مسئولیت:**
- جستجوی خودکار منابع API رایگان
- استفاده از DuckDuckGo برای جستجو
- استفاده از HuggingFace برای تحلیل
- اضافه کردن منابع جدید به ResourceManager

**API Endpoints:**
- `GET /api/resources/discovery/status`
- `POST /api/resources/discovery/run`

---

#### 2. `connection_manager.py`
**مسئولیت:**
- مدیریت اتصالات WebSocket
- Tracking sessions
- Broadcasting messages
- Heartbeat management

**API Endpoints:**
- `GET /api/sessions`
- `GET /api/sessions/stats`
- `POST /api/broadcast`
- `WebSocket /ws`

---

#### 3. `diagnostics_service.py`
**مسئولیت:**
- اشکال‌یابی خودکار سیستم
- بررسی وابستگی‌ها
- بررسی تنظیمات
- بررسی شبکه
- تعمیر خودکار مشکلات

**API Endpoints:**
- `POST /api/diagnostics/run?auto_fix=true/false`
- `GET /api/diagnostics/last`

---

#### 4. `unified_config_loader.py`
**مسئولیت:**
- بارگذاری یکپارچه تمام فایل‌های Config
- Merge کردن منابع از فایل‌های مختلف
- مدیریت API keys
- Setup CORS proxies

**فایل‌های Load شده:**
- `crypto_resources_unified_2025-11-11.json`
- `all_apis_merged_2025.json`
- `ultimate_crypto_pipeline_2025_NZasinich.json`

---

## 🎨 رابط کاربری

### `unified_dashboard.html` - داشبورد اصلی

**تب‌ها:**
1. **Market** - داده‌های بازار
2. **API Monitor** - مانیتورینگ Providerها
3. **Advanced** - عملیات پیشرفته
4. **Admin** - مدیریت
5. **HuggingFace** - مدل‌های HuggingFace
6. **Pools** - مدیریت Poolها
7. **Logs** - مدیریت لاگ‌ها
8. **Resources** - مدیریت منابع
9. **Reports** - گزارشات و اشکال‌یابی

**ویژگی‌ها:**
- اتصال WebSocket برای داده‌های بلادرنگ
- نمایش تعداد کاربران آنلاین
- گزارشات Auto-Discovery
- گزارشات مدل‌های HuggingFace
- اشکال‌یابی خودکار

---

## 🔄 نحوه استفاده از فایل‌های Config

### سناریو 1: استفاده از ProviderManager
```python
from provider_manager import ProviderManager

# استفاده از providers_config_extended.json
manager = ProviderManager(config_path="providers_config_extended.json")

# دریافت Provider
provider = manager.get_provider("coingecko")

# استفاده از Pool
pool = manager.get_pool("primary_market_data_pool")
result = await pool.get_data("coins_markets")
```

---

### سناریو 2: استفاده از ResourceManager
```python
from resource_manager import ResourceManager

# استفاده از providers_config_ultimate.json
manager = ResourceManager(config_file="providers_config_ultimate.json")

# اضافه کردن Provider جدید
manager.add_provider({
    "id": "new_api",
    "name": "New API",
    "category": "market_data",
    "base_url": "https://api.example.com",
    "requires_auth": False
})

# ذخیره
manager.save_resources()
```

---

### سناریو 3: استفاده از UnifiedConfigLoader
```python
from backend.services.unified_config_loader import UnifiedConfigLoader

# به صورت خودکار تمام فایل‌ها را load می‌کند
loader = UnifiedConfigLoader()

# دریافت تمام APIs
all_apis = loader.get_all_apis()

# دریافت APIs بر اساس category
market_apis = loader.get_apis_by_category('market_data')
```

---

## 📊 جریان داده (Data Flow)

```
1. Startup
   └── api_server_extended.py
       ├── ProviderManager.load_config()
       │   └── providers_config_extended.json
       ├── ResourceManager.load_resources()
       │   └── providers_config_ultimate.json
       └── UnifiedConfigLoader.load_all_configs()
           ├── crypto_resources_unified_2025-11-11.json
           ├── all_apis_merged_2025.json
           └── ultimate_crypto_pipeline_2025_NZasinich.json

2. Runtime
   └── API Request
       ├── ProviderManager.get_provider()
       ├── ProviderPool.get_data()
       └── Response

3. WebSocket
   └── ConnectionManager
       ├── Connect client
       ├── Broadcast updates
       └── Heartbeat

4. Auto-Discovery
   └── AutoDiscoveryService
       ├── Search (DuckDuckGo)
       ├── Analyze (HuggingFace)
       └── Add to ResourceManager
```

---

## 🎯 توصیه‌ها

### ✅ فایل‌های پیشنهادی برای استفاده

1. **برای مدیریت Providerها:**
   - استفاده از `provider_manager.py` با `providers_config_extended.json`

2. **برای مدیریت منابع:**
   - استفاده از `resource_manager.py` با `providers_config_ultimate.json`

3. **برای بارگذاری یکپارچه:**
   - استفاده از `UnifiedConfigLoader` که تمام فایل‌ها را merge می‌کند

### ⚠️ فایل‌های قدیمی

- فایل‌های قدیمی را می‌توانید نگه دارید برای مرجع
- اما برای توسعه جدید از فایل‌های جدید استفاده کنید

---

## 📝 خلاصه

| کامپوننت | فایل اصلی | فایل Config | وضعیت |
|----------|-----------|-------------|-------|
| سرور | `api_server_extended.py` | - | ✅ فعال |
| مدیریت Provider | `provider_manager.py` | `providers_config_extended.json` | ✅ فعال |
| مدیریت منابع | `resource_manager.py` | `providers_config_ultimate.json` | ✅ فعال |
| بارگذاری یکپارچه | `unified_config_loader.py` | `crypto_resources_unified_2025-11-11.json` + 2 فایل دیگر | ✅ فعال |
| داشبورد | `unified_dashboard.html` | - | ✅ فعال |
| Auto-Discovery | `auto_discovery_service.py` | - | ✅ فعال |
| WebSocket | `connection_manager.py` | - | ✅ فعال |
| Diagnostics | `diagnostics_service.py` | - | ✅ فعال |

---

**آخرین به‌روزرسانی:** 2025-01-XX
**نسخه:** 4.0

