# 🚀 راهنمای سیستم Fallback نهایی

**تاریخ:** 2025-12-08  
**نسخه:** 1.0.0

## 📋 خلاصه

سیستم **Ultimate Fallback** یک راه‌حل جامع برای مدیریت **137 منبع داده** است که به صورت هوشمند از تمام منابع موجود استفاده می‌کند و **حداقل 10 جایگزین برای هر درخواست** فراهم می‌آورد.

### ✨ ویژگی‌های کلیدی

- ✅ **137 منبع داده** شامل:
  - 20 منبع Market Data
  - 15 منبع News
  - 12 منبع Sentiment
  - 18 منبع Blockchain Explorers
  - 12 منبع On-Chain Analytics
  - 8 منبع Whale Tracking
  - 23 منبع RPC Nodes
  - 18 مدل HuggingFace
  - 5 Dataset HuggingFace
  - 6 CORS Proxy

- ✅ **حداقل 10 fallback** برای هر category
- ✅ **Auto-rotation** و Load Balancing
- ✅ **Rate limit handling** هوشمند
- ✅ **Cooldown management** خودکار
- ✅ **متغیرهای محیطی** برای کلیدهای API
- ✅ **اولویت‌بندی** براساس سرعت و قابلیت اعتماد

---

## 📦 منابع موجود

### 🔥 Market Data (20 منبع)

**CRITICAL Priority:**
- Binance Public API
- CoinGecko

**HIGH Priority:**
- CoinMarketCap (2 کلید)
- CryptoCompare

**MEDIUM Priority:**
- CoinPaprika
- CoinCap
- Messari
- CoinLore
- DefiLlama
- CoinStats

**LOW Priority:**
- DIA Data
- Nomics
- FreeCryptoAPI
- CoinDesk
- Mobula

**EMERGENCY Priority:**
- CoinAPI.io
- Kaiko
- BraveNewCoin
- Token Metrics

---

### 📰 News (15 منبع)

**CRITICAL Priority:**
- CryptoPanic

**HIGH Priority:**
- NewsAPI.org
- CryptoControl

**MEDIUM Priority:**
- CoinDesk API
- CoinTelegraph API
- CryptoSlate
- The Block
- CoinStats News

**LOW Priority:**
- CoinDesk RSS
- CoinTelegraph RSS
- Bitcoin Magazine RSS
- Decrypt RSS
- و 3 منبع دیگر

---

### 💭 Sentiment (12 منبع)

**CRITICAL Priority:**
- Alternative.me Fear & Greed

**HIGH Priority:**
- CFGI API v1
- CFGI Legacy
- LunarCrush

**MEDIUM Priority:**
- Santiment
- TheTie.io
- CryptoQuant
- Glassnode Social
- Augmento

**LOW Priority:**
- CoinGecko Community
- Messari Social
- Reddit r/cryptocurrency

---

### 🔍 Blockchain Explorers (18 منبع)

**استفاده شده فعلی + 13 منبع جدید:**
- Etherscan (2 کلید)
- BscScan
- TronScan
- Blockscout
- Blockchair
- Ethplorer
- Etherchain
- و 10 منبع دیگر

---

### ⛓️ On-Chain Analytics (12 منبع)

- The Graph
- Glassnode
- IntoTheBlock
- Nansen
- Dune Analytics
- Covalent
- Moralis
- Alchemy NFT API
- و 4 منبع دیگر

---

### 🐋 Whale Tracking (8 منبع)

- Whale Alert
- Arkham Intelligence
- ClankApp
- BitQuery Whales
- Nansen Smart Money
- DeBank
- Zerion
- Whalemap

---

### 🌐 RPC Nodes (23 منبع)

**Ethereum (10 منبع):**
- Ankr, PublicNode, Cloudflare, LlamaNodes, 1RPC, dRPC
- Infura, Alchemy, Alchemy WS

**BSC (6 منبع):**
- BSC Official (3 endpoints)
- Ankr, PublicNode, Nodereal

**TRON (3 منبع):**
- TronGrid, TronStack, Nile Testnet

**Polygon (4 منبع):**
- Official, Mumbai, Ankr, PublicNode

---

### 🤖 HuggingFace Models (18 مدل)

**Crypto Sentiment:**
- ElKulako/CryptoBERT ⭐
- kk08/CryptoBERT ⭐
- mayurjadhav/crypto-sentiment-model
- mathugo/crypto_news_bert
- burakutf/finetuned-finbert-crypto

**Financial Sentiment:**
- ProsusAI/finbert ⭐
- StephanAkkerman/FinTwitBERT-sentiment
- yiyanghkust/finbert-tone
- mrm8488/distilroberta-finetuned-financial-news

**Social Sentiment:**
- cardiffnlp/twitter-roberta-base-sentiment-latest ⭐
- finiteautomata/bertweet-base-sentiment-analysis
- nlptown/bert-base-multilingual-uncased-sentiment

**Trading Signals:**
- agarkovv/CryptoTrader-LM (Buy/Sell/Hold)

**Generation:**
- OpenC/crypto-gpt-o3-mini

**Summarization:**
- FurkanGozukara/Crypto-Financial-News-Summarizer
- facebook/bart-large-cnn
- facebook/bart-large-mnli

**General (Fallback):**
- distilbert-base-uncased-finetuned-sst-2-english

> ⭐ = استفاده شده فعلی در پروژه

---

### 📊 HuggingFace Datasets (5 dataset)

**OHLCV Data:**
- linxy/CryptoCoin (26 symbols × 7 timeframes = 182 CSV)
- WinkingFace/CryptoLM-Bitcoin-BTC-USDT
- WinkingFace/CryptoLM-Ethereum-ETH-USDT
- WinkingFace/CryptoLM-Solana-SOL-USDT
- WinkingFace/CryptoLM-Ripple-XRP-USDT

---

### 🔄 CORS Proxies (6 منبع)

- AllOrigins (بدون محدودیت)
- CORS.SH
- Corsfix (60 req/min)
- CodeTabs
- ThingProxy (10 req/sec)
- Crossorigin.me

---

## 🛠️ نحوه استفاده

### 1. نصب و راه‌اندازی

```bash
# کپی کردن فایل محیطی
cp .env.example .env

# ویرایش کلیدهای API (اختیاری - کلیدهای موجود از قبل تنظیم شده‌اند)
nano .env
```

### 2. استفاده در کد Python

```python
from backend.services.ultimate_fallback_system import (
    fetch_with_fallback,
    ultimate_fallback,
    get_statistics
)

# مثال 1: درخواست با fallback خودکار
success, data, source = await fetch_with_fallback(
    category='market_data',
    endpoint='/simple/price',
    params={'ids': 'bitcoin', 'vs_currencies': 'usd'},
    max_attempts=10  # تا 10 منبع مختلف امتحان می‌شود
)

if success:
    print(f"✅ داده از {source} دریافت شد")
    print(data)
else:
    print("❌ تمام منابع شکست خوردند")

# مثال 2: دریافت زنجیره fallback
fallback_chain = ultimate_fallback.get_fallback_chain(
    category='market_data',
    count=15  # 15 منبع اول
)

for i, resource in enumerate(fallback_chain, 1):
    print(f"{i}. {resource.name} ({resource.priority.name})")

# مثال 3: دریافت آمار
stats = get_statistics()
print(f"منابع کل: {stats['total_resources']}")
print(f"منابع در دسترس Market Data: {stats['by_category']['market_data']['available']}")
```

### 3. استفاده مستقیم از منابع

```python
# دریافت منبع بعدی با الگوریتم هوشمند
resource = ultimate_fallback.get_next_resource(
    category='market_data',
    exclude_ids=['binance_primary']  # نادیده گرفتن منابع خاص
)

if resource:
    print(f"منبع انتخابی: {resource.name}")
    print(f"URL: {resource.base_url}")
    print(f"نیاز به احراز هویت: {resource.requires_auth}")
    
    # دریافت کلید API (از env variable یا مقدار پیش‌فرض)
    api_key = resource.get_api_key()
```

### 4. مدیریت نتایج

```python
# ثبت موفقیت
ultimate_fallback.mark_result(
    resource_id='binance_primary',
    category='market_data',
    success=True
)

# ثبت شکست (با rate limit)
ultimate_fallback.mark_result(
    resource_id='coingecko_primary',
    category='market_data',
    success=False,
    error_type='rate_limit'  # منبع برای 60 دقیقه cooldown می‌شود
)
```

---

## 🔑 مدیریت کلیدهای API

### کلیدهای موجود (از قبل تنظیم شده)

فایل `.env.example` شامل کلیدهای زیر است:

```bash
# Market Data
COINMARKETCAP_KEY_1=04cf4b5b-9868-465c-8ba0-9f2e78c92eb1
COINMARKETCAP_KEY_2=b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c
CRYPTOCOMPARE_KEY=e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f

# Blockchain
ETHERSCAN_KEY_1=SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2
ETHERSCAN_KEY_2=T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45
BSCSCAN_KEY=K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT
TRONSCAN_KEY=7ae72726-bffe-4e74-9c33-97b761eeea21

# News
NEWSAPI_KEY=pub_346789abc123def456789ghi012345jkl

# HuggingFace
HF_TOKEN=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
```

### دریافت کلیدهای اضافی (اختیاری)

برای استفاده کامل از تمام منابع، می‌توانید کلیدهای رایگان دریافت کنید:

| سرویس | لینک ثبت‌نام | محدودیت رایگان |
|-------|-------------|----------------|
| Infura | https://infura.io | 100K req/day |
| Alchemy | https://alchemy.com | 300M units/month |
| LunarCrush | https://lunarcrush.com | 500 req/day |
| Glassnode | https://glassnode.com | محدود |
| CryptoQuant | https://cryptoquant.com | محدود |
| HuggingFace | https://huggingface.co/settings/tokens | نامحدود |

---

## 🎯 الگوریتم Fallback

### اولویت‌بندی

منابع در 5 سطح اولویت دسته‌بندی شده‌اند:

1. **CRITICAL** - سریع‌ترین و قابل اعتمادترین
2. **HIGH** - کیفیت بالا
3. **MEDIUM** - استاندارد
4. **LOW** - پشتیبان
5. **EMERGENCY** - آخرین راه‌حل

### انتخاب هوشمند

سیستم براساس موارد زیر منبع بعدی را انتخاب می‌کند:

- **80% احتمال**: بهترین منبع موجود (اولویت بالاتر)
- **20% احتمال**: Load balancing با منابع دیگر

```python
def get_next_resource(self, category, exclude_ids=None):
    resources = self.get_available_resources(category)
    
    # مرتب‌سازی براساس:
    # 1. اولویت (CRITICAL > HIGH > ...)
    # 2. نرخ موفقیت (success_count / total_attempts)
    # 3. زمان استفاده اخیر (کمتر استفاده شده = اولویت بیشتر)
    
    if random.random() < 0.8:
        return resources[0]  # بهترین منبع
    else:
        return random.choice(resources[:3])  # load balancing
```

### Cooldown Management

- **3 شکست متوالی** → Cooldown 5 دقیقه
- **Rate Limit (429)** → Cooldown 60 دقیقه
- **موفقیت** → reset fail counter, بازگشت به AVAILABLE

---

## 📊 مانیتورینگ و آمار

### دریافت آمار کامل

```python
stats = get_statistics()

# نمونه خروجی:
{
    'total_resources': 137,
    'by_category': {
        'market_data': {
            'total': 20,
            'available': 18,
            'rate_limited': 2,
            'failed': 0,
            'success_rate': 95.5
        },
        'news': {
            'total': 15,
            'available': 15,
            'rate_limited': 0,
            'failed': 0,
            'success_rate': 100.0
        },
        # ...
    }
}
```

### لاگ‌گذاری

سیستم به صورت خودکار تمام رویدادها را لاگ می‌کند:

```
✅ Binance Public API: Success (total: 150)
⏳ CoinGecko API: Rate limited for 60 min
❌ CoinMarketCap Key 1: Failed (count: 2)
🔄 Trying CoinCap (HIGH)
```

---

## 🚀 مثال‌های کاربردی

### مثال 1: دریافت قیمت با 15 fallback

```python
async def get_crypto_price(symbol: str) -> Optional[float]:
    """دریافت قیمت با 15 منبع fallback"""
    
    success, data, source = await fetch_with_fallback(
        category='market_data',
        endpoint=f'/simple/price',
        params={'ids': symbol, 'vs_currencies': 'usd'},
        max_attempts=15
    )
    
    if success:
        logger.info(f"قیمت {symbol} از {source}: ${data['price']}")
        return data['price']
    
    logger.error(f"همه 15 منبع برای {symbol} شکست خوردند")
    return None
```

### مثال 2: آنالیز احساسات با 10 مدل مختلف

```python
async def analyze_sentiment_ensemble(text: str) -> Dict:
    """آنالیز احساسات با 10 مدل HuggingFace"""
    
    models = ultimate_fallback.get_fallback_chain('hf_models', count=10)
    results = []
    
    for model in models:
        if not model.is_available():
            continue
        
        try:
            # استفاده از مدل
            result = await call_hf_model(model, text)
            results.append(result)
            
            ultimate_fallback.mark_result(model.id, 'hf_models', True)
            
            # اگر 5 مدل موفق شدند، کافی است
            if len(results) >= 5:
                break
        except Exception as e:
            ultimate_fallback.mark_result(model.id, 'hf_models', False)
            continue
    
    # میانگین‌گیری از نتایج
    if results:
        return {
            'sentiment': aggregate_sentiments(results),
            'models_used': len(results),
            'confidence': calculate_confidence(results)
        }
    
    return {'sentiment': 'neutral', 'models_used': 0, 'confidence': 0}
```

### مثال 3: Whale Tracking با 8 منبع

```python
async def track_whale_transactions(min_usd: float = 1000000) -> List[Dict]:
    """ردیابی تراکنش‌های نهنگ با 8 منبع"""
    
    all_transactions = []
    
    for resource in ultimate_fallback.get_fallback_chain('whales', count=8):
        if not resource.is_available():
            continue
        
        try:
            txs = await fetch_whale_transactions(resource, min_usd)
            all_transactions.extend(txs)
            
            ultimate_fallback.mark_result(resource.id, 'whales', True)
            
            # اگر 100 تراکنش پیدا کردیم، کافی است
            if len(all_transactions) >= 100:
                break
        except Exception:
            ultimate_fallback.mark_result(resource.id, 'whales', False)
            continue
    
    # حذف تکراری‌ها
    unique_txs = deduplicate_by_txhash(all_transactions)
    return unique_txs
```

---

## ⚡ بهینه‌سازی عملکرد

### 1. Caching

```python
from functools import lru_cache
from datetime import timedelta

@lru_cache(maxsize=1000)
def get_cached_resource(category: str, resource_id: str):
    """کش کردن منابع برای سرعت بیشتر"""
    return ultimate_fallback.get_next_resource(category)
```

### 2. Parallel Requests

```python
import asyncio

async def fetch_from_multiple_sources(category: str, count: int = 5):
    """درخواست همزمان از چند منبع"""
    
    resources = ultimate_fallback.get_fallback_chain(category, count=count)
    
    tasks = [
        fetch_with_resource(resource)
        for resource in resources[:count]
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # استفاده از اولین نتیجه موفق
    for result in results:
        if not isinstance(result, Exception):
            return result
    
    return None
```

### 3. Smart Retry

```python
async def fetch_with_smart_retry(
    category: str,
    max_attempts: int = 10,
    initial_delay: float = 1.0
):
    """Retry با exponential backoff"""
    
    delay = initial_delay
    
    for attempt in range(max_attempts):
        success, data, source = await fetch_with_fallback(
            category=category,
            max_attempts=1
        )
        
        if success:
            return data
        
        # Exponential backoff
        await asyncio.sleep(delay)
        delay *= 2
    
    return None
```

---

## 📚 مستندات API

### کلاس‌ها

#### `UltimateFallbackSystem`

**Methods:**

- `get_resources_by_category(category, limit=None, only_available=True)` → List[Resource]
- `get_next_resource(category, exclude_ids=None)` → Optional[Resource]
- `get_fallback_chain(category, count=10)` → List[Resource]
- `mark_result(resource_id, category, success, error_type=None)` → None
- `get_statistics()` → Dict
- `export_env_template()` → str

#### `Resource`

**Properties:**

- `id: str` - شناسه منبع
- `name: str` - نام نمایشی
- `base_url: str` - URL پایه
- `category: str` - دسته
- `priority: Priority` - اولویت
- `auth_type: str` - نوع احراز هویت
- `api_key: str` - کلید API
- `status: ResourceStatus` - وضعیت فعلی

**Methods:**

- `get_api_key()` → Optional[str]
- `is_available()` → bool
- `mark_success()` → None
- `mark_failure()` → None
- `mark_rate_limited(duration_minutes)` → None

---

## 🔧 عیب‌یابی

### مشکل: تمام منابع Rate Limited شده‌اند

**راه‌حل:**

1. چک کردن تعداد درخواست‌ها
2. استفاده از کلیدهای API بیشتر
3. افزایش cooldown duration
4. استفاده از CORS proxies

```python
# چک کردن وضعیت
stats = get_statistics()
for cat, data in stats['by_category'].items():
    if data['rate_limited'] > data['available']:
        print(f"⚠️ {cat}: نیاز به کلید API بیشتر")
```

### مشکل: عملکرد کند

**راه‌حل:**

1. استفاده از parallel requests
2. کاهش max_attempts
3. فعال کردن caching
4. اولویت‌بندی منابع سریع‌تر

### مشکل: کلید API کار نمی‌کند

**راه‌حل:**

1. بررسی `.env` file
2. restart سرویس
3. چک کردن format کلید

```bash
# بررسی متغیرهای محیطی
python3 -c "import os; print(os.getenv('HF_TOKEN'))"
```

---

## 📝 تغییرات آینده

### نسخه 1.1.0 (برنامه‌ریزی شده)

- [ ] افزودن metrics برای Prometheus
- [ ] Dashboard وب برای مانیتورینگ
- [ ] Auto-scaling براساس بار
- [ ] ML-based resource selection
- [ ] گزارش‌دهی خودکار

### نسخه 1.2.0 (برنامه‌ریزی شده)

- [ ] پشتیبانی از WebSocket sources
- [ ] Real-time fallback switching
- [ ] A/B testing for resources
- [ ] Cost optimization

---

## 🤝 مشارکت

برای افزودن منابع جدید:

1. فایل `ultimate_fallback_system.py` را ویرایش کنید
2. منبع جدید را به دسته مربوطه اضافه کنید
3. اولویت مناسب را تعیین کنید
4. env variable لازم را به `.env.example` اضافه کنید
5. تست کنید

---

## 📞 پشتیبانی

برای سوالات و مشکلات:

1. ✅ مستندات را بررسی کنید
2. ✅ لاگ‌ها را چک کنید
3. ✅ آمار سیستم را بررسی کنید
4. ✅ Issue در GitHub ایجاد کنید

---

## 📜 لایسنس

MIT License - استفاده آزاد در پروژه‌های تجاری و غیرتجاری

---

**ساخته شده با ❤️ برای جامعه Crypto**

*نسخه 1.0.0 - دسامبر 2025*
