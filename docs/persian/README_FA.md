# 🚀 Crypto Monitor ULTIMATE - نسخه توسعه‌یافته

یک سیستم مانیتورینگ و تحلیل کریپتوکارنسی قدرتمند با پشتیبانی از **100+ ارائه‌دهنده API رایگان** و سیستم پیشرفته **Provider Pool Management**.

## ✨ ویژگی‌های کلیدی

### 🎯 مدیریت ارائه‌دهندگان (Provider Management)
- ✅ **100+ ارائه‌دهنده API رایگان** از دسته‌بندی‌های مختلف
- 🔄 **سیستم Pool با استراتژی‌های چرخش مختلف**
  - Round Robin
  - Priority-based
  - Weighted Random
  - Least Used
  - Fastest Response
- 🛡️ **Circuit Breaker** برای جلوگیری از درخواست‌های مکرر به سرویس‌های خراب
- ⚡ **Rate Limiting هوشمند** برای هر ارائه‌دهنده
- 📊 **آمارگیری دقیق** از عملکرد هر ارائه‌دهنده
- 🔍 **Health Check خودکار** و دوره‌ای

### 📈 دسته‌بندی ارائه‌دهندگان

#### 💰 بازار و قیمت‌گذاری (Market Data)
- CoinGecko, CoinPaprika, CoinCap
- CryptoCompare, Nomics, Messari
- LiveCoinWatch, Cryptorank, CoinLore, CoinCodex

#### 🔗 اکسپلورر‌های بلاکچین (Blockchain Explorers)
- Etherscan, BscScan, PolygonScan
- Arbiscan, Optimistic Etherscan
- Blockchair, Blockchain.info, Ethplorer

#### 🏦 دیفای (DeFi Protocols)
- DefiLlama, Aave, Compound
- Uniswap V3, PancakeSwap, SushiSwap
- Curve Finance, 1inch, Yearn Finance

#### 🖼️ NFT
- OpenSea, Rarible, Reservoir, NFTPort

#### 📰 اخبار و شبکه‌های اجتماعی (News & Social)
- CryptoPanic, NewsAPI
- CoinDesk RSS, Cointelegraph RSS, Bitcoinist RSS
- Reddit Crypto, LunarCrush

#### 💭 تحلیل احساسات (Sentiment Analysis)
- Alternative.me (Fear & Greed Index)
- Santiment, LunarCrush

#### 📊 تحلیل و آنالیتیکس (Analytics)
- Glassnode, IntoTheBlock
- Coin Metrics, Kaiko

#### 💱 صرافی‌ها (Exchanges)
- Binance, Kraken, Coinbase
- Bitfinex, Huobi, KuCoin
- OKX, Gate.io, Bybit

#### 🤗 Hugging Face Models
- مدل‌های تحلیل احساسات (Sentiment Analysis)
- مدل‌های دسته‌بندی متن (Text Classification)
- مدل‌های Zero-Shot Classification

## 🏗️ معماری سیستم

```
┌─────────────────────────────────────────────────┐
│           Unified Dashboard (HTML/JS)           │
│  📊 نمایش داده‌ها | 🔄 مدیریت Pools | 📈 آمار │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│         FastAPI Server (Python)                 │
│  🌐 REST API | WebSocket | Background Tasks    │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│         Provider Manager (Core Logic)           │
│  🔄 Rotation | 🛡️ Circuit Breaker | 📊 Stats   │
└────────────────────┬────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
┌─────────┐    ┌─────────┐    ┌─────────┐
│ Pool 1  │    │ Pool 2  │    │ Pool N  │
│ Market  │    │  DeFi   │    │   NFT   │
└────┬────┘    └────┬────┘    └────┬────┘
     │              │              │
     └──────┬───────┴──────┬───────┘
            ▼              ▼
    ┌──────────────┐  ┌──────────────┐
    │  Provider 1  │  │  Provider N  │
    │ (CoinGecko)  │  │  (Binance)   │
    └──────────────┘  └──────────────┘
```

## 📦 نصب و راه‌اندازی

### پیش‌نیازها
```bash
Python 3.8+
pip
```

### نصب وابستگی‌ها
```bash
pip install fastapi uvicorn aiohttp pydantic
```

### اجرای سرور
```bash
# روش 1: مستقیم
python api_server_extended.py

# روش 2: با uvicorn
uvicorn api_server_extended:app --reload --host 0.0.0.0 --port 8000
```

### دسترسی به داشبورد
```
http://localhost:8000
```

## 🔧 استفاده از API

### 🌐 Endpoints اصلی

#### **وضعیت سیستم**
```http
GET /health
GET /api/status
GET /api/stats
```

#### **مدیریت ارائه‌دهندگان**
```http
GET    /api/providers                    # لیست همه
GET    /api/providers/{provider_id}      # جزئیات یک ارائه‌دهنده
POST   /api/providers/{provider_id}/health-check
GET    /api/providers/category/{category}
```

#### **مدیریت Pool‌ها**
```http
GET    /api/pools                        # لیست همه Pool‌ها
GET    /api/pools/{pool_id}              # جزئیات یک Pool
POST   /api/pools                        # ایجاد Pool جدید
DELETE /api/pools/{pool_id}              # حذف Pool

POST   /api/pools/{pool_id}/members      # افزودن عضو
DELETE /api/pools/{pool_id}/members/{provider_id}
POST   /api/pools/{pool_id}/rotate       # چرخش دستی
GET    /api/pools/history                # تاریخچه چرخش‌ها
```

### 📝 نمونه‌های استفاده

#### ایجاد Pool جدید
```bash
curl -X POST http://localhost:8000/api/pools \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Market Pool",
    "category": "market_data",
    "rotation_strategy": "weighted",
    "description": "Pool for market data providers"
  }'
```

#### افزودن ارائه‌دهنده به Pool
```bash
curl -X POST http://localhost:8000/api/pools/my_market_pool/members \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": "coingecko",
    "priority": 10,
    "weight": 100
  }'
```

#### چرخش Pool
```bash
curl -X POST http://localhost:8000/api/pools/my_market_pool/rotate \
  -H "Content-Type: application/json" \
  -d '{"reason": "manual rotation"}'
```

## 🎮 استفاده از Python API

```python
import asyncio
from provider_manager import ProviderManager

async def main():
    # ایجاد مدیر
    manager = ProviderManager()
    
    # بررسی سلامت همه
    await manager.health_check_all()
    
    # دریافت ارائه‌دهنده از Pool
    provider = manager.get_next_from_pool("primary_market_data_pool")
    if provider:
        print(f"Selected: {provider.name}")
        print(f"Success Rate: {provider.success_rate}%")
    
    # آمار کلی
    stats = manager.get_all_stats()
    print(f"Total Providers: {stats['summary']['total_providers']}")
    print(f"Online: {stats['summary']['online']}")
    
    # صادرکردن آمار
    manager.export_stats("my_stats.json")
    
    await manager.close_session()

asyncio.run(main())
```

## 📊 استراتژی‌های چرخش Pool

### 1️⃣ Round Robin
هر بار به ترتیب یک ارائه‌دهنده انتخاب می‌شود.
```python
rotation_strategy = "round_robin"
```

### 2️⃣ Priority-Based
ارائه‌دهنده با بالاترین اولویت انتخاب می‌شود.
```python
rotation_strategy = "priority"
# Provider with priority=10 selected over priority=5
```

### 3️⃣ Weighted Random
انتخاب تصادفی با وزن‌دهی.
```python
rotation_strategy = "weighted"
# Provider with weight=100 has 2x chance vs weight=50
```

### 4️⃣ Least Used
ارائه‌دهنده‌ای که کمتر استفاده شده انتخاب می‌شود.
```python
rotation_strategy = "least_used"
```

### 5️⃣ Fastest Response
ارائه‌دهنده با سریع‌ترین زمان پاسخ انتخاب می‌شود.
```python
rotation_strategy = "fastest_response"
```

## 🛡️ Circuit Breaker

سیستم Circuit Breaker به‌طور خودکار ارائه‌دهندگان مشکل‌دار را غیرفعال می‌کند:

- **آستانه**: 5 خطای متوالی
- **مدت زمان قطع**: 60 ثانیه
- **بازیابی خودکار**: پس از اتمام timeout

```python
# Circuit Breaker خودکار در Provider
if provider.consecutive_failures >= 5:
    provider.circuit_breaker_open = True
    provider.circuit_breaker_open_until = time.time() + 60
```

## 📈 مانیتورینگ و لاگ

### بررسی سلامت دوره‌ای
سیستم هر 30 ثانیه به‌طور خودکار سلامت همه ارائه‌دهندگان را بررسی می‌کند.

### آمارگیری
- **تعداد کل درخواست‌ها**
- **درخواست‌های موفق/ناموفق**
- **نرخ موفقیت (Success Rate)**
- **میانگین زمان پاسخ**
- **تعداد چرخش‌های Pool**

### صادرکردن آمار
```python
manager.export_stats("stats_export.json")
```

## 🔐 مدیریت API Key

برای ارائه‌دهندگانی که نیاز به API Key دارند:

1. فایل `.env` بسازید:
```env
# Market Data
COINMARKETCAP_API_KEY=your_key_here
CRYPTOCOMPARE_API_KEY=your_key_here

# Blockchain Data
ALCHEMY_API_KEY=your_key_here
INFURA_API_KEY=your_key_here

# News
NEWSAPI_KEY=your_key_here

# Analytics
GLASSNODE_API_KEY=your_key_here
```

2. در کد خود از `python-dotenv` استفاده کنید:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("COINMARKETCAP_API_KEY")
```

## 🎨 داشبورد وب

داشبورد شامل تب‌های زیر است:

### 📊 Market
- آمار کلی بازار
- لیست کریپتوکارنسی‌های برتر
- نمودارها (Dominance, Fear & Greed)
- ترندینگ و DeFi

### 📡 API Monitor
- وضعیت همه ارائه‌دهندگان
- زمان پاسخ
- آخرین بررسی سلامت
- تحلیل احساسات (HuggingFace)

### ⚡ Advanced
- لیست API‌ها
- اکسپورت JSON/CSV
- پشتیبان‌گیری
- پاک‌سازی Cache
- لاگ فعالیت‌ها

### ⚙️ Admin
- افزودن API جدید
- تنظیمات
- آمار کلی

### 🤗 HuggingFace
- وضعیت سلامت
- لیست مدل‌ها و دیتاست‌ها
- جستجو در Registry
- تحلیل احساسات آنلاین

### 🔄 Pools
- مدیریت Pool‌ها
- افزودن/حذف اعضا
- چرخش دستی
- تاریخچه چرخش‌ها
- آمار تفصیلی

## 🧪 تست

```bash
# تست Provider Manager
python provider_manager.py

# تست سرور API
python api_server_extended.py
```

## 📄 فایل‌های پروژه

```
crypto-monitor-hf-full-fixed-v4-realapis/
├── unified_dashboard.html           # داشبورد وب اصلی
├── providers_config_extended.json   # تنظیمات 100+ ارائه‌دهنده
├── provider_manager.py              # هسته مدیریت Provider & Pool
├── api_server_extended.py           # سرور FastAPI
├── README_FA.md                     # راهنمای فارسی (این فایل)
└── .env.example                     # نمونه متغیرهای محیطی
```

## 🚀 ویژگی‌های آینده

- [ ] پشتیبانی از WebSocket برای داده‌های Realtime
- [ ] سیستم صف (Queue) برای درخواست‌های سنگین
- [ ] Cache با Redis
- [ ] Dashboard پیشرفته با React/Vue
- [ ] Alerting System (Telegram/Email)
- [ ] Machine Learning برای پیش‌بینی بهترین Provider
- [ ] Multi-tenant Support
- [ ] Docker & Kubernetes Support

## 🤝 مشارکت

برای مشارکت:
1. Fork کنید
2. یک branch جدید بسازید: `git checkout -b feature/amazing-feature`
3. تغییرات را commit کنید: `git commit -m 'Add amazing feature'`
4. Push کنید: `git push origin feature/amazing-feature`
5. Pull Request ایجاد کنید

## 📝 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است.

## 💬 پشتیبانی

در صورت بروز مشکل یا سوال:
- Issue در GitHub باز کنید
- به بخش Discussions مراجعه کنید

## 🙏 تشکر

از تمام ارائه‌دهندگان API رایگان که این پروژه را ممکن کردند:
- CoinGecko, CoinPaprika, CoinCap
- Etherscan, BscScan و تمام Block Explorers
- DefiLlama, OpenSea و...
- Hugging Face برای مدل‌های ML

---

**ساخته شده با ❤️ برای جامعه کریپتو**

