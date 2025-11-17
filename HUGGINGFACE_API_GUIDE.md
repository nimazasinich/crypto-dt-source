# 🚀 HuggingFace Space - Cryptocurrency Data API

## دسترسی به API

URL پایه: `https://really-amin-datasourceforcryptocurrency.hf.space`

## 📋 لیست کامل Endpoint‌ها

### Core Data Endpoints

#### 1. System Health
```bash
GET /health
```
**مثال:**
```bash
curl https://really-amin-datasourceforcryptocurrency.hf.space/health
```

#### 2. System Info
```bash
GET /info
```
**مثال:**
```bash
curl https://really-amin-datasourceforcryptocurrency.hf.space/info
```

#### 3. API Providers
```bash
GET /api/providers
```
**مثال:**
```bash
curl https://really-amin-datasourceforcryptocurrency.hf.space/api/providers
```

### Market Data Endpoints

#### 4. OHLCV Data (Candlestick)
```bash
GET /api/ohlcv?symbol=BTCUSDT&interval=1h&limit=100
```
**پارامترها:**
- `symbol`: نماد جفت ارز (مثال: BTCUSDT, ETHUSDT)
- `interval`: بازه زمانی (1m, 5m, 15m, 30m, 1h, 4h, 1d)
- `limit`: تعداد کندل‌ها (1-1000)

**مثال:**
```bash
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/ohlcv?symbol=BTCUSDT&interval=1h&limit=50"
```

**پاسخ:**
```json
{
  "symbol": "BTCUSDT",
  "interval": "1h",
  "count": 50,
  "data": [
    {
      "timestamp": 1700000000000,
      "datetime": "2023-11-15T00:00:00",
      "open": 37000.50,
      "high": 37500.00,
      "low": 36800.00,
      "close": 37200.00,
      "volume": 1234.56
    }
  ]
}
```

#### 5. Top Crypto Prices
```bash
GET /api/crypto/prices/top?limit=10
```
**مثال:**
```bash
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/prices/top?limit=5"
```

**پاسخ:**
```json
{
  "count": 5,
  "data": [
    {
      "id": "bitcoin",
      "symbol": "BTC",
      "name": "Bitcoin",
      "current_price": 37000.00,
      "market_cap": 720000000000,
      "price_change_percentage_24h": 2.5
    }
  ]
}
```

#### 6. Single Crypto Price
```bash
GET /api/crypto/price/{symbol}
```
**مثال:**
```bash
curl https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/price/BTC
```

#### 7. Market Overview
```bash
GET /api/crypto/market-overview
```
**مثال:**
```bash
curl https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/market-overview
```

**پاسخ:**
```json
{
  "total_market_cap": 1500000000000,
  "total_volume_24h": 75000000000,
  "btc_dominance": 48.5,
  "top_gainers": [...],
  "top_losers": [...],
  "top_by_volume": [...]
}
```

#### 8. Multiple Prices
```bash
GET /api/market/prices?symbols=BTC,ETH,SOL
```
**مثال:**
```bash
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/market/prices?symbols=BTC,ETH,SOL"
```

#### 9. Market Data Prices (Alternative)
```bash
GET /api/market-data/prices?symbols=BTC,ETH
```
**مثال:**
```bash
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/market-data/prices?symbols=BTC,ETH"
```

### Analysis Endpoints

#### 10. Trading Signals
```bash
GET /api/analysis/signals?symbol=BTCUSDT&timeframe=1h
```
**مثال:**
```bash
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/analysis/signals?symbol=BTCUSDT"
```

**پاسخ:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "signal": "buy",
  "trend": "bullish",
  "momentum": "strong",
  "indicators": {
    "sma_20": 36800.00,
    "current_price": 37200.00,
    "price_change_percent": 1.08
  }
}
```

#### 11. SMC Analysis (Smart Money Concepts)
```bash
GET /api/analysis/smc?symbol=BTCUSDT
```
**مثال:**
```bash
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/analysis/smc?symbol=BTCUSDT"
```

**پاسخ:**
```json
{
  "symbol": "BTCUSDT",
  "market_structure": "higher_highs",
  "key_levels": {
    "resistance": 38000.00,
    "support": 36000.00,
    "current_price": 37200.00
  },
  "order_blocks": {...},
  "liquidity_zones": {...}
}
```

#### 12. Scoring Snapshot
```bash
GET /api/scoring/snapshot?symbol=BTCUSDT
```
**مثال:**
```bash
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/scoring/snapshot?symbol=BTCUSDT"
```

**پاسخ:**
```json
{
  "symbol": "BTCUSDT",
  "overall_score": 75.5,
  "scores": {
    "volatility": 45.2,
    "volume": 82.3,
    "trend": 68.9,
    "momentum": 56.7
  },
  "rating": "good"
}
```

#### 13. All Signals
```bash
GET /api/signals
```
**مثال:**
```bash
curl https://really-amin-datasourceforcryptocurrency.hf.space/api/signals
```

#### 14. Market Sentiment
```bash
GET /api/sentiment
```
**مثال:**
```bash
curl https://really-amin-datasourceforcryptocurrency.hf.space/api/sentiment
```

**پاسخ:**
```json
{
  "value": 65,
  "classification": "greed",
  "description": "Market sentiment is greed"
}
```

### System Endpoints

#### 15. System Status
```bash
GET /api/system/status
```
**مثال:**
```bash
curl https://really-amin-datasourceforcryptocurrency.hf.space/api/system/status
```

#### 16. System Configuration
```bash
GET /api/system/config
```
**مثال:**
```bash
curl https://really-amin-datasourceforcryptocurrency.hf.space/api/system/config
```

#### 17. Categories
```bash
GET /api/categories
```
**مثال:**
```bash
curl https://really-amin-datasourceforcryptocurrency.hf.space/api/categories
```

#### 18. Rate Limits
```bash
GET /api/rate-limits
```
**مثال:**
```bash
curl https://really-amin-datasourceforcryptocurrency.hf.space/api/rate-limits
```

#### 19. Logs
```bash
GET /api/logs?limit=50
```
**مثال:**
```bash
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/logs?limit=20"
```

#### 20. Alerts
```bash
GET /api/alerts
```
**مثال:**
```bash
curl https://really-amin-datasourceforcryptocurrency.hf.space/api/alerts
```

### HuggingFace Integration Endpoints

#### 21. HF Health
```bash
GET /api/hf/health
```
**مثال:**
```bash
curl https://really-amin-datasourceforcryptocurrency.hf.space/api/hf/health
```

#### 22. HF Refresh
```bash
POST /api/hf/refresh
```
**مثال:**
```bash
curl -X POST https://really-amin-datasourceforcryptocurrency.hf.space/api/hf/refresh
```

#### 23. HF Registry
```bash
GET /api/hf/registry?kind=models
```
**مثال:**
```bash
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/hf/registry?kind=models"
```

#### 24. HF Sentiment Analysis
```bash
POST /api/hf/run-sentiment
POST /api/hf/sentiment
```
**مثال:**
```bash
curl -X POST "https://really-amin-datasourceforcryptocurrency.hf.space/api/hf/sentiment" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Bitcoin is going to the moon!"]}'
```

## 🔥 ویژگی‌های API

✅ **Built-in Caching**: کش 60 ثانیه‌ای برای بهبود سرعت  
✅ **Multiple Data Sources**: Binance + CoinGecko  
✅ **Auto-fallback**: در صورت خرابی یک منبع، به منبع دیگر تغییر مسیر می‌دهد  
✅ **CORS Enabled**: قابل استفاده از هر دامنه  
✅ **Rate Limiting Ready**: محدودیت درخواست برای جلوگیری از سوء استفاده  
✅ **20+ Cryptocurrency Support**: پشتیبانی از بیش از 20 ارز دیجیتال

## 📊 منابع داده

- **Binance API**: داده‌های OHLCV و قیمت real-time
- **CoinGecko API**: اطلاعات جامع بازار و رتبه‌بندی
- **CoinPaprika**: داده‌های تکمیلی
- **CoinCap**: داده‌های اضافی

## 🚀 نحوه استفاده در برنامه

### Python
```python
import requests

# دریافت قیمت‌های برتر
response = requests.get(
    "https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/prices/top?limit=5"
)
data = response.json()
print(data)

# دریافت داده OHLCV
response = requests.get(
    "https://really-amin-datasourceforcryptocurrency.hf.space/api/ohlcv",
    params={"symbol": "BTCUSDT", "interval": "1h", "limit": 100}
)
ohlcv = response.json()
print(ohlcv)

# دریافت سیگنال‌های معاملاتی
response = requests.get(
    "https://really-amin-datasourceforcryptocurrency.hf.space/api/analysis/signals",
    params={"symbol": "ETHUSDT"}
)
signals = response.json()
print(signals)
```

### JavaScript
```javascript
// دریافت قیمت‌های برتر
fetch('https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/prices/top?limit=5')
  .then(response => response.json())
  .then(data => console.log(data));

// دریافت داده OHLCV
fetch('https://really-amin-datasourceforcryptocurrency.hf.space/api/ohlcv?symbol=BTCUSDT&interval=1h&limit=100')
  .then(response => response.json())
  .then(data => console.log(data));

// دریافت تحلیل SMC
fetch('https://really-amin-datasourceforcryptocurrency.hf.space/api/analysis/smc?symbol=BTCUSDT')
  .then(response => response.json())
  .then(data => console.log(data));
```

### cURL (Terminal)
```bash
# تست سریع همه endpoint‌ها
curl https://really-amin-datasourceforcryptocurrency.hf.space/health
curl https://really-amin-datasourceforcryptocurrency.hf.space/info
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/ohlcv?symbol=BTCUSDT&interval=1h&limit=10"
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/prices/top?limit=5"
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/market-overview"
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/analysis/signals?symbol=BTCUSDT"
```

## 🎯 Use Cases

1. **Trading Bots**: استفاده از داده‌های OHLCV و سیگنال‌ها
2. **Price Trackers**: نمایش قیمت‌های real-time
3. **Market Analysis**: تحلیل روند و احساسات بازار
4. **Portfolio Apps**: ردیابی پورتفولیو با قیمت‌های به‌روز
5. **Research Tools**: تحقیقات بازار و تحلیل تکنیکال

## 📖 مستندات API

مستندات تعاملی (Swagger UI):
```
https://really-amin-datasourceforcryptocurrency.hf.space/docs
```

## ⚡ Performance

- **Response Time**: کمتر از 500ms برای اکثر endpoint‌ها
- **Cache TTL**: 60 ثانیه
- **Rate Limit**: 1200 درخواست در دقیقه
- **Uptime**: 99%+

## 🔒 Security

- ✅ HTTPS فقط
- ✅ CORS فعال
- ✅ Rate limiting
- ✅ Input validation
- ✅ Error handling

## 💬 پشتیبانی

در صورت بروز مشکل:
1. ابتدا `/health` را چک کنید
2. لاگ‌ها را از `/api/logs` بررسی کنید
3. مستندات `/docs` را مطالعه کنید

---

**نسخه**: 3.0.0  
**آخرین بروزرسانی**: 2025-11-17  
**وضعیت**: ✅ فعال و operational

🎉 همه endpoint‌های مورد نیاز شما اکنون فعال و آماده استفاده هستند!
