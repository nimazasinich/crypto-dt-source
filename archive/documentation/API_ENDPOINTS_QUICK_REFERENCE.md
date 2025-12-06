# 🚀 Quick Reference - تمام Endpoint ها

**Base URL**: `https://really-amin-datasourceforcryptocurrency-2.hf.space`

---

## 📊 Market Data APIs

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/market` | لیست قیمت‌های بازار | `limit`, `vs_currency` |
| GET | `/api/market/price/{symbol}` | قیمت یک ارز خاص | - |
| GET | `/api/market/history` | داده‌های OHLCV | `symbol`, `interval`, `limit` |
| GET | `/api/market/ticker/{symbol}` | اطلاعات کامل ticker | - |
| GET | `/api/market/volume` | حجم معاملات | `limit` |
| GET | `/api/market/gainers` | بیشترین رشدها | `limit` |
| GET | `/api/market/losers` | بیشترین افت‌ها | `limit` |
| GET | `/api/market/trending` | ترندینگ‌ها | `limit` |

---

## 🧠 Sentiment Analysis APIs

| Method | Endpoint | Description | Body/Parameters |
|--------|----------|-------------|-----------------|
| POST | `/api/sentiment/analyze` | تحلیل احساسات متن | `{"text": "...", "mode": "crypto"}` |
| GET | `/api/sentiment/global` | احساسات کل بازار (Fear & Greed) | - |
| GET | `/api/sentiment/asset/{symbol}` | احساسات یک ارز | - |
| POST | `/api/sentiment/batch` | تحلیل چند متن | `{"texts": [...]}` |
| GET | `/api/sentiment/history/{symbol}` | تاریخچه احساسات | `interval`, `limit` |

---

## 🤖 AI Models APIs

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/models/list` | لیست تمام مدل‌ها (45+) | `category` |
| GET | `/api/models/status` | وضعیت مدل‌ها | - |
| GET | `/api/models/summary` | خلاصه وضعیت | - |
| GET | `/api/models/categories` | دسته‌بندی مدل‌ها | - |
| POST | `/api/models/load/{model_id}` | بارگذاری یک مدل | - |
| POST | `/api/models/unload/{model_id}` | تخلیه یک مدل | - |

---

## 📰 News APIs

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/news` | آخرین اخبار | `limit`, `category` |
| GET | `/api/news/{symbol}` | اخبار یک ارز | `limit` |
| GET | `/api/news/trending` | اخبار ترند | `limit` |
| GET | `/api/news/search` | جستجوی اخبار | `q`, `limit` |
| GET | `/api/news/sources` | منابع خبری | - |

---

## 📈 Technical Analysis APIs

| Method | Endpoint | Description | Body/Parameters |
|--------|----------|-------------|-----------------|
| POST | `/api/technical/indicators` | محاسبه اندیکاتورها | `{"symbol": "...", "indicators": [...]}` |
| POST | `/api/technical/signals` | سیگنال خرید/فروش | `{"symbol": "...", "strategy": "..."}` |
| GET | `/api/technical/strategies` | لیست استراتژی‌ها | - |
| POST | `/api/technical/backtest` | بک‌تست استراتژی | `{"symbol": "...", "strategy": "...", "period": "..."}` |
| GET | `/api/technical/support-resistance/{symbol}` | سطوح حمایت/مقاومت | - |

---

## 🔗 Blockchain APIs

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/blockchain/{chain}/info` | اطلاعات زنجیره | - |
| GET | `/api/blockchain/{chain}/address/{address}` | اطلاعات آدرس | - |
| GET | `/api/blockchain/{chain}/transaction/{txid}` | اطلاعات تراکنش | - |
| GET | `/api/blockchain/{chain}/block/{block}` | اطلاعات بلوک | - |
| GET | `/api/blockchain/{chain}/gas` | Gas price | - |
| GET | `/api/blockchain/networks` | لیست شبکه‌ها | - |

**Supported Chains**: ethereum, bitcoin, binance-smart-chain, polygon, solana, avalanche, arbitrum, optimism

---

## 🎯 Smart Fallback APIs (305+ Resources)

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/smart/market` | داده بازار با Fallback | `limit` |
| GET | `/api/smart/news` | اخبار با Fallback | `limit` |
| GET | `/api/smart/sentiment` | احساسات با Fallback | - |
| GET | `/api/smart/price/{symbol}` | قیمت با Fallback | - |
| GET | `/api/smart/health-report` | گزارش سلامت منابع | - |
| GET | `/api/smart/resources` | لیست تمام منابع | `category` |
| GET | `/api/smart/resource-stats` | آمار منابع | - |

---

## 🔍 Search & Discovery APIs

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/search/coins` | جستجوی ارزها | `q`, `limit` |
| GET | `/api/search/global` | جستجوی کلی | `q` |
| GET | `/api/discover/trending` | ارزهای ترند | `limit` |
| GET | `/api/discover/new` | ارزهای جدید | `limit` |

---

## 📊 Analytics & Stats APIs

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/analytics/market-overview` | نمای کلی بازار | - |
| GET | `/api/analytics/dominance` | Market Dominance | - |
| GET | `/api/analytics/market-cap-history` | تاریخچه Market Cap | `days` |
| GET | `/api/analytics/volume-history` | تاریخچه حجم معاملات | `days` |
| GET | `/api/analytics/correlation` | همبستگی بازارها | `symbols` |

---

## 🎲 DeFi APIs

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/defi/protocols` | لیست پروتکل‌های DeFi | `limit` |
| GET | `/api/defi/tvl` | Total Value Locked | `protocol` |
| GET | `/api/defi/yields` | نرخ بازده | `protocol` |
| GET | `/api/defi/pools/{protocol}` | استخرهای نقدینگی | - |

---

## 💱 Exchange APIs

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/exchange/list` | لیست صرافی‌ها | - |
| GET | `/api/exchange/{exchange}/pairs` | جفت ارزهای یک صرافی | - |
| GET | `/api/exchange/{exchange}/volume` | حجم معاملات صرافی | - |
| GET | `/api/exchange/compare` | مقایسه صرافی‌ها | `symbols` |

---

## 📱 Social Media APIs

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/social/twitter/{symbol}` | داده‌های توییتر | `limit` |
| GET | `/api/social/reddit/{symbol}` | داده‌های ردیت | `limit` |
| GET | `/api/social/sentiment/{platform}` | احساسات شبکه‌های اجتماعی | `symbol` |
| GET | `/api/social/trending` | هشتگ‌های ترند | - |

---

## 🏦 Financial APIs (Alpha Vantage)

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/alphavantage/prices` | قیمت‌ها | `symbol` |
| GET | `/api/alphavantage/ohlcv` | داده‌های OHLCV | `symbol`, `interval` |
| GET | `/api/alphavantage/forex` | نرخ ارز | `from`, `to` |
| GET | `/api/alphavantage/commodities` | کالاها | `commodity` |

---

## 💼 Massive.com APIs

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/massive/quotes` | قیمت سهام | `symbol` |
| GET | `/api/massive/indices` | شاخص‌های بورس | - |
| GET | `/api/massive/market-status` | وضعیت بازار | - |

---

## 🔐 Authentication APIs (Optional)

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | ثبت‌نام | `{"username": "...", "password": "..."}` |
| POST | `/api/auth/login` | ورود | `{"username": "...", "password": "..."}` |
| POST | `/api/auth/refresh` | Refresh Token | `{"refresh_token": "..."}` |
| POST | `/api/auth/logout` | خروج | - |

---

## 🏥 System Health APIs

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/health` | بررسی سلامت سیستم | - |
| GET | `/api/health/database` | سلامت دیتابیس | - |
| GET | `/api/health/models` | سلامت مدل‌ها | - |
| GET | `/api/health/workers` | سلامت worker ها | - |
| GET | `/api/metrics` | متریک‌های سیستم | - |
| GET | `/api/version` | نسخه API | - |

---

## 🌐 WebSocket Channels

**URL**: `wss://really-amin-datasourceforcryptocurrency-2.hf.space/ws`

### Available Channels:

| Channel | Description | Subscribe Message |
|---------|-------------|-------------------|
| `prices` | قیمت‌های لحظه‌ای | `{"action": "subscribe", "channel": "prices", "symbols": ["BTCUSDT"]}` |
| `news` | اخبار جدید | `{"action": "subscribe", "channel": "news"}` |
| `sentiment` | تغییرات احساسات | `{"action": "subscribe", "channel": "sentiment"}` |
| `signals` | سیگنال‌های معاملاتی | `{"action": "subscribe", "channel": "signals", "symbols": ["BTCUSDT"]}` |
| `orderbook` | Order Book | `{"action": "subscribe", "channel": "orderbook", "symbol": "BTCUSDT"}` |
| `trades` | معاملات | `{"action": "subscribe", "channel": "trades", "symbol": "BTCUSDT"}` |

### WebSocket Actions:

| Action | Description | Format |
|--------|-------------|--------|
| subscribe | عضویت در کانال | `{"action": "subscribe", "channel": "..."}` |
| unsubscribe | لغو عضویت | `{"action": "unsubscribe", "channel": "..."}` |
| ping | بررسی اتصال | `{"action": "ping"}` |

---

## 📚 Documentation Endpoints

| URL | Description |
|-----|-------------|
| `/docs` | Swagger UI (تعاملی) |
| `/redoc` | ReDoc (خواناتر) |
| `/openapi.json` | OpenAPI Schema |
| `/api/endpoints` | لیست تمام endpoint ها |

---

## 🎨 Static Pages

| URL | Description |
|-----|-------------|
| `/` | صفحه اصلی |
| `/dashboard` | داشبورد اصلی |
| `/pages/sentiment/` | تحلیل احساسات |
| `/pages/trading-assistant/` | دستیار معاملات |
| `/pages/market-data/` | داده‌های بازار |
| `/pages/news/` | اخبار |
| `/pages/technical-analysis/` | تحلیل تکنیکال |
| `/pages/portfolio/` | مدیریت پورتفولیو |
| `/pages/signals/` | سیگنال‌ها |
| `/pages/models/` | مدل‌های AI |
| `/pages/settings/` | تنظیمات |

---

## 🔥 Most Popular Endpoints

### برای شروع سریع:

```bash
# 1. قیمت بیت کوین
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market/price/bitcoin

# 2. تحلیل احساسات
curl -X POST https://really-amin-datasourceforcryptocurrency-2.hf.space/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Bitcoin to the moon!", "mode": "crypto"}'

# 3. سیگنال خرید/فروش
curl -X POST https://really-amin-datasourceforcryptocurrency-2.hf.space/api/technical/signals \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "strategy": "trend-rsi-macd"}'

# 4. آخرین اخبار
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/news?limit=10

# 5. بررسی سلامت
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/health
```

---

## 📊 Response Format

همه endpoint ها یک فرمت یکسان برمی‌گردونند:

### Success Response:
```json
{
  "success": true,
  "data": { /* ... */ },
  "timestamp": 1733472000000,
  "source": "provider_name"
}
```

### Error Response:
```json
{
  "success": false,
  "error": "خطایی رخ داد",
  "message": "توضیحات بیشتر",
  "code": "ERROR_CODE",
  "timestamp": 1733472000000
}
```

---

## 🎯 Categories Summary

| Category | Count | Description |
|----------|-------|-------------|
| Market Data APIs | 21+ | قیمت، OHLCV، Volume |
| Sentiment APIs | 12+ | تحلیل احساسات |
| News APIs | 15+ | اخبار کریپتو |
| Technical APIs | 8+ | اندیکاتورها، سیگنال‌ها |
| Blockchain APIs | 40+ | Block Explorer ها |
| AI Models | 45+ | مدل‌های HuggingFace |
| DeFi APIs | 6+ | TVL، Yields، Pools |
| Social APIs | 5+ | Twitter، Reddit |
| RPC Nodes | 24+ | Ethereum، Bitcoin، ... |
| Smart Fallback | 305+ | تمام منابع |

**Total**: 400+ endpoints و resources

---

## 💡 Tips

1. **همیشه از Smart endpoints استفاده کنید** (`/api/smart/*`) برای Reliability بهتر
2. **WebSocket را برای real-time** ترجیح دهید
3. **Cache کردن** برای کاهش بار سرور
4. **Error handling** برای تجربه بهتر کاربر

---

**🚀 Ready to use!**
