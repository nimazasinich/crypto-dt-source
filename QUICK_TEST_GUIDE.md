# 🚀 تست سریع API

## تست آنلاین (فوری)

همین الان می‌توانید API را تست کنید:

### 1. در مرورگر
برو به:
```
https://really-amin-datasourceforcryptocurrency.hf.space/health
```

### 2. با curl در Terminal

```bash
# Health Check
curl https://really-amin-datasourceforcryptocurrency.hf.space/health

# System Info
curl https://really-amin-datasourceforcryptocurrency.hf.space/info

# OHLCV Data (نمودار شمعی بیت‌کوین)
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/ohlcv?symbol=BTCUSDT&interval=1h&limit=50"

# قیمت 5 ارز برتر
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/prices/top?limit=5"

# بررسی کلی بازار
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/market-overview"

# سیگنال‌های معاملاتی
curl "https://really-amin-datasourceforcryptocurrency.hf.space/api/analysis/signals?symbol=BTCUSDT"
```

### 3. تست خودکار همه Endpoint‌ها

```bash
# در workspace خود
chmod +x TEST_ENDPOINTS.sh
./TEST_ENDPOINTS.sh
```

یا:

```bash
bash TEST_ENDPOINTS.sh
```

## نتیجه مورد انتظار

✅ همه endpoint‌ها باید HTTP 200 برگردانند  
✅ داده‌های JSON معتبر  
✅ زمان پاسخ کمتر از 1 ثانیه  

## اگر خطا دیدی

1. **چک کن که Space روشن باشه**:
   ```
   https://really-amin-datasourceforcryptocurrency.hf.space/health
   ```

2. **مستندات تعاملی را ببین**:
   ```
   https://really-amin-datasourceforcryptocurrency.hf.space/docs
   ```

3. **Log‌ها را بررسی کن**:
   ```
   curl https://really-amin-datasourceforcryptocurrency.hf.space/api/logs
   ```

## استفاده در کد

### Python
```python
import requests

# Simple
r = requests.get("https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/prices/top?limit=5")
print(r.json())

# With error handling
try:
    r = requests.get(
        "https://really-amin-datasourceforcryptocurrency.hf.space/api/ohlcv",
        params={"symbol": "BTCUSDT", "interval": "1h", "limit": 100},
        timeout=10
    )
    r.raise_for_status()
    data = r.json()
    print(f"Got {data['count']} candles")
except Exception as e:
    print(f"Error: {e}")
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

// Simple
axios.get('https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/prices/top?limit=5')
  .then(res => console.log(res.data));

// With async/await
async function getOHLCV() {
  try {
    const response = await axios.get(
      'https://really-amin-datasourceforcryptocurrency.hf.space/api/ohlcv',
      {
        params: {
          symbol: 'BTCUSDT',
          interval: '1h',
          limit: 100
        }
      }
    );
    console.log(`Got ${response.data.count} candles`);
    return response.data;
  } catch (error) {
    console.error('Error:', error.message);
  }
}
```

## مثال کاربردی: نمایش قیمت BTC

```python
import requests
import time

def get_btc_price():
    r = requests.get("https://really-amin-datasourceforcryptocurrency.hf.space/api/crypto/price/BTC")
    data = r.json()
    
    if 'price' in data:
        price_data = data['price']
        return price_data.get('price', 0)
    return None

# نمایش قیمت هر 10 ثانیه
while True:
    price = get_btc_price()
    if price:
        print(f"BTC Price: ${price:,.2f}")
    time.sleep(10)
```

## چک‌لیست تست

- [ ] `/health` - سلامت سیستم
- [ ] `/info` - اطلاعات API
- [ ] `/api/ohlcv` - داده OHLCV
- [ ] `/api/crypto/prices/top` - قیمت‌های برتر
- [ ] `/api/crypto/price/{symbol}` - قیمت تکی
- [ ] `/api/crypto/market-overview` - بررسی بازار
- [ ] `/api/market/prices` - قیمت‌های چندتایی
- [ ] `/api/analysis/signals` - سیگنال‌های معاملاتی
- [ ] `/api/analysis/smc` - تحلیل SMC
- [ ] `/api/scoring/snapshot` - امتیازدهی
- [ ] `/api/sentiment` - احساسات بازار

---

✅ **همه چیز آماده است!**  
🎉 **API شما در HuggingFace Space فعال و کار می‌کند!**

📖 برای جزئیات بیشتر: [HUGGINGFACE_API_GUIDE.md](./HUGGINGFACE_API_GUIDE.md)
