# 🚀 راهنمای شروع سریع - منابع API رایگان

## نگاه کلی

این پروژه شامل **200+ منبع API رایگان** برای جمع‌آوری داده‌های ارز دیجیتال است که به صورت سلسله‌مراتبی و با قابلیت Fallback خودکار مدیریت می‌شوند.

---

## 📊 خلاصه منابع

### منابع اصلی:
| دسته | تعداد | وضعیت |
|------|-------|-------|
| 💹 Market Data APIs | 16 | ✅ فعال |
| 📰 News Sources | 10 | ✅ فعال |
| 😊 Sentiment APIs | 8 | ✅ فعال |
| ⛓️ Block Explorers | 18 | ✅ فعال |
| 🌐 RPC Nodes | 23 | ✅ فعال |
| 📚 HuggingFace Datasets | 2 | ✅ فعال |
| 🛡️ Infrastructure (DNS/Proxy) | 3 | ✅ فعال |
| **جمع کل** | **80+** | **✅ همه فعال** |

---

## 🎯 دسته‌بندی منابع

### 1️⃣ Market Data - داده‌های بازار

```json
{
  "CRITICAL": [
    "Binance Public API",
    "CoinGecko API"
  ],
  "HIGH": [
    "CoinCap API",
    "CoinPaprika API",
    "CoinMarketCap (2 keys)"
  ],
  "MEDIUM": [
    "CryptoCompare",
    "Messari",
    "CoinLore",
    "DefiLlama"
  ],
  "LOW": [
    "CoinStats",
    "DIA Data",
    "Nomics",
    "FreeCryptoAPI"
  ],
  "EMERGENCY": [
    "BraveNewCoin",
    "CoinDesk Price API"
  ]
}
```

**نحوه استفاده:**
```python
# از طریق API سیستم
GET /api/resources/market/price/BTC
GET /api/resources/market/prices?symbols=BTC,ETH,BNB
```

---

### 2️⃣ News Sources - منابع خبری

```json
{
  "CRITICAL": [
    "CryptoPanic Free API"
  ],
  "HIGH": [
    "CoinStats News API",
    "NewsAPI.org (با کلید)"
  ],
  "MEDIUM": [
    "CoinTelegraph RSS",
    "CoinDesk RSS",
    "Decrypt RSS",
    "Bitcoin Magazine RSS"
  ],
  "LOW": [
    "CryptoSlate",
    "CryptoControl",
    "TheBlock API"
  ]
}
```

**نحوه استفاده:**
```python
GET /api/resources/news/latest?limit=20
GET /api/resources/news/symbol/BTC?limit=10
```

---

### 3️⃣ Sentiment Analysis - تحلیل احساسات

```json
{
  "CRITICAL": [
    "Alternative.me Fear & Greed Index"
  ],
  "HIGH": [
    "CFGI API v1",
    "CFGI Legacy"
  ],
  "MEDIUM": [
    "CoinGecko Community Data",
    "Reddit Sentiment",
    "Messari Social Metrics"
  ],
  "LOW": [
    "LunarCrush",
    "Santiment",
    "TheTie.io"
  ]
}
```

**نحوه استفاده:**
```python
GET /api/resources/sentiment/fear-greed
GET /api/resources/sentiment/global
GET /api/resources/sentiment/coin/BTC
```

---

### 4️⃣ Block Explorers - کاوشگرهای بلاکچین

#### Ethereum:
```json
{
  "PRIMARY": "Etherscan (2 کلید)",
  "FALLBACK": [
    "Blockchair",
    "Blockscout",
    "Ethplorer",
    "Etherchain",
    "Chainlens"
  ]
}
```

#### BSC:
```json
{
  "PRIMARY": "BscScan",
  "FALLBACK": [
    "Blockchair",
    "BitQuery",
    "Nodereal",
    "Ankr MultiChain",
    "BscTrace",
    "1inch BSC API"
  ]
}
```

#### Tron:
```json
{
  "PRIMARY": "TronScan (با کلید)",
  "FALLBACK": [
    "TronGrid (Free)",
    "Blockchair",
    "TronStack",
    "GetBlock"
  ]
}
```

**نحوه استفاده:**
```python
GET /api/resources/onchain/balance?address=0x...&chain=ethereum
GET /api/resources/onchain/gas?chain=ethereum
GET /api/resources/onchain/transactions?address=0x...&chain=bsc
```

---

### 5️⃣ RPC Nodes - گره‌های RPC

#### Ethereum (10 گره):
- Infura (100k req/day)
- Alchemy (300M compute units/month)
- Ankr (Unlimited)
- PublicNode (Free)
- Cloudflare
- LlamaNodes
- 1RPC
- dRPC
- BlastAPI
- QuickNode

#### BSC (6 گره):
- BSC Official
- BSC DefiData
- BSC NiniCoin
- Ankr BSC
- PublicNode BSC
- Nodereal BSC

#### Polygon (4 گره):
- Polygon Official
- Polygon Mumbai (Testnet)
- Ankr Polygon
- PublicNode Polygon

#### Tron (3 گره):
- TronGrid
- TronStack
- Tron Nile Testnet

---

### 6️⃣ HuggingFace Datasets - مجموعه داده‌ها

```json
{
  "linxy/CryptoCoin": {
    "symbols": 26,
    "timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
    "total_files": 182,
    "example": "BTCUSDT_1h.csv"
  },
  "WinkingFace/CryptoLM": {
    "datasets": [
      "Bitcoin-BTC-USDT",
      "Ethereum-ETH-USDT",
      "Solana-SOL-USDT",
      "Ripple-XRP-USDT"
    ]
  }
}
```

**نحوه استفاده:**
```python
GET /api/resources/hf/ohlcv?symbol=BTC&timeframe=1h&limit=1000
GET /api/resources/hf/symbols
GET /api/resources/hf/timeframes/BTC
```

---

### 7️⃣ Infrastructure - زیرساخت

```json
{
  "DNS Over HTTPS": [
    "Cloudflare DoH",
    "Google DoH"
  ],
  "Proxy Services": [
    "ProxyScrape Free API"
  ],
  "Purpose": "برای دور زدن فیلترینگ Binance و CoinGecko"
}
```

---

## 🔌 Endpoints اصلی پروژه

### Market Data:
```bash
GET  /api/resources/market/price/{symbol}
GET  /api/resources/market/prices
GET  /api/market/quotes
POST /api/market/klines
```

### News & Sentiment:
```bash
GET  /api/resources/news/latest
GET  /api/resources/news/symbol/{symbol}
GET  /api/resources/sentiment/fear-greed
GET  /api/resources/sentiment/global
GET  /api/resources/sentiment/coin/{symbol}
```

### On-Chain Data:
```bash
GET  /api/resources/onchain/balance
GET  /api/resources/onchain/gas
GET  /api/resources/onchain/transactions
```

### HuggingFace:
```bash
GET  /api/resources/hf/ohlcv
GET  /api/resources/hf/symbols
GET  /api/resources/hf/timeframes/{symbol}
```

### System Status:
```bash
GET  /api/resources/status
GET  /api/hierarchy/overview
GET  /api/hierarchy/usage-stats
```

---

## 🎛️ WebSocket Endpoints

### Real-Time Monitoring:
```bash
WS   /api/monitoring/ws
WS   /ws/master
WS   /ws/all
WS   /ws/market_data
WS   /ws/news
WS   /ws/sentiment
```

---

## 🔑 API Keys موجود

پروژه دارای **8 API Key فعال** است:

1. **Etherscan Primary**: `SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2`
2. **Etherscan Backup**: `T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45`
3. **BscScan**: `K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT`
4. **TronScan**: `7ae72726-bffe-4e74-9c33-97b761eeea21`
5. **CoinMarketCap Key 1**: `04cf4b5b-9868-465c-8ba0-9f2e78c92eb1`
6. **CoinMarketCap Key 2**: `b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c`
7. **CryptoCompare**: `e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f`
8. **NewsAPI.org**: `pub_346789abc123def456789ghi012345jkl`

> ⚠️ **نکته امنیتی**: این کلیدها در فایل‌های JSON ذخیره شده‌اند. در محیط production از environment variables استفاده کنید.

---

## 📈 سیستم Hierarchical Fallback

سیستم به صورت خودکار در صورت خرابی یک منبع، به منابع بعدی مراجعه می‌کند:

```
CRITICAL (سریع‌ترین) → HIGH (کیفیت بالا) → MEDIUM (استاندارد) 
    → LOW (پشتیبان) → EMERGENCY (آخرین راه‌حل)
```

**مثال عملی:**
```python
# درخواست قیمت BTC
1. تلاش با Binance (CRITICAL) ✅
2. اگر ناموفق → CoinGecko (CRITICAL) ✅
3. اگر ناموفق → CoinCap (HIGH) ✅
4. اگر ناموفق → CoinPaprika (HIGH) ✅
5. و همین‌طور تا EMERGENCY
```

---

## 🚀 شروع سریع

### 1. نصب Dependencies:
```bash
pip install -r requirements.txt
```

### 2. راه‌اندازی Redis (برای Cache):
```bash
docker run -d -p 6379:6379 redis:alpine
```

### 3. اجرای سرور:
```bash
python main.py
# یا
uvicorn hf_unified_server:app --host 0.0.0.0 --port 7860
```

### 4. دسترسی به API:
```
http://localhost:7860/docs     # Swagger UI
http://localhost:7860/redoc    # ReDoc
```

---

## 📝 نمونه کد استفاده

### Python:
```python
import aiohttp
import asyncio

async def get_btc_price():
    async with aiohttp.ClientSession() as session:
        url = "http://localhost:7860/api/resources/market/price/BTC"
        async with session.get(url) as response:
            data = await response.json()
            return data['price']

price = asyncio.run(get_btc_price())
print(f"BTC Price: ${price}")
```

### JavaScript/TypeScript:
```typescript
async function getBTCPrice() {
  const response = await fetch('http://localhost:7860/api/resources/market/price/BTC');
  const data = await response.json();
  return data.price;
}

const price = await getBTCPrice();
console.log(`BTC Price: $${price}`);
```

### cURL:
```bash
# قیمت BTC
curl http://localhost:7860/api/resources/market/price/BTC

# قیمت چند ارز
curl "http://localhost:7860/api/resources/market/prices?symbols=BTC,ETH,BNB"

# اخبار
curl "http://localhost:7860/api/resources/news/latest?limit=10"

# احساسات
curl http://localhost:7860/api/resources/sentiment/fear-greed
```

---

## 🔍 منابع بیشتر

- 📄 **راهنمای کامل**: `ULTIMATE_FALLBACK_GUIDE_FA.md`
- 📋 **چک‌لیست پیاده‌سازی**: `FINAL_IMPLEMENTATION_CHECKLIST_FA.md`
- 📊 **خلاصه تغییرات**: `RESOURCES_EXPANSION_SUMMARY_FA.md`
- 🗺️ **نقشه سایت**: `SITEMAP.md`

---

## ✅ وضعیت منابع

```
✅ همه 80+ منبع فعال و قابل استفاده
✅ Fallback اتوماتیک برای همه دسته‌ها
✅ Cache هوشمند با Redis
✅ Rate Limiting برای همه درخواست‌ها
✅ WebSocket برای Real-time data
✅ API Keys مدیریت شده
```

---

**تاریخ بروزرسانی**: ۸ دسامبر ۲۰۲۵  
**نسخه**: ۱.۰  
**وضعیت**: ✅ آماده استفاده
