# 📝 خلاصه سرویس‌های موجود

## 🌐 آدرس
```
https://really-amin-datasourceforcryptocurrency-2.hf.space
```

---

## 🚀 سرویس‌های اصلی

### 1. قیمت ارزها
```bash
# قیمت 50 ارز برتر
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/smart/market?limit=50
```

### 2. نمودار قیمت
```bash
# 100 شمع 1 ساعته بیت کوین
curl "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/market/history?symbol=BTCUSDT&interval=1h&limit=100"
```

### 3. تحلیل احساسات
```bash
curl -X POST https://really-amin-datasourceforcryptocurrency-2.hf.space/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Bitcoin is pumping!"}'
```

### 4. اخبار
```bash
# 20 خبر آخر
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/smart/news?limit=20
```

### 5. سلامت سیستم
```bash
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/health
```

---

## 📊 آمار

- **305+** منبع داده
- **45+** مدل AI
- **9** صفحه UI کامل
- **300** ارز در لیست
- **24/7** جمع‌آوری خودکار

---

## 🎯 ویژگی‌های کلیدی

1. **Smart Fallback** - هیچوقت 404 نمیده
2. **Real-time WebSocket** - داده لحظه‌ای
3. **45+ AI Models** - تحلیل احساسات پیشرفته
4. **305+ Data Sources** - بیشترین تنوع
5. **Background Workers** - به‌روزرسانی خودکار

---

## 📚 مستندات

### کامل و تعاملی
```
https://really-amin-datasourceforcryptocurrency-2.hf.space/docs
```

### فایل‌های راهنما
- `📖_راهنمای_نهایی_کامل.md` - همه چیز در یک فایل
- `🚀_سرویس‌های_موجود_فارسی.md` - لیست تمام سرویس‌ها
- `شروع_سریع_با_مثال.md` - مثال‌های عملی
- `راهنمای_استفاده_API_فارسی.md` - راهنمای کامل فارسی
- `API_USAGE_GUIDE_COMPLETE.md` - راهنمای کامل انگلیسی
- `API_ENDPOINTS_QUICK_REFERENCE.md` - مرجع سریع

---

## 🎨 صفحات UI

1. **Dashboard** - `/static/pages/dashboard/index.html`
2. **Market** - `/static/pages/market/index.html`
3. **Trading Assistant** - `/static/pages/trading-assistant/index.html`
4. **Sentiment** - `/static/pages/sentiment/index.html`
5. **News** - `/static/pages/news/index.html`
6. **Technical Analysis** - `/static/pages/technical-analysis/index.html`
7. **Models** - `/static/pages/models/index.html`
8. **API Explorer** - `/static/pages/api-explorer/index.html`
9. **Diagnostics** - `/static/pages/diagnostics/index.html`

---

## 💻 مثال سریع (JavaScript)

```javascript
// گرفتن قیمت 10 ارز برتر
async function getPrices() {
  const url = 'https://really-amin-datasourceforcryptocurrency-2.hf.space/api/smart/market?limit=10';
  const response = await fetch(url);
  const data = await response.json();
  
  data.items.forEach(coin => {
    console.log(`${coin.name}: $${coin.current_price}`);
  });
}

getPrices();
```

---

## 🐍 مثال سریع (Python)

```python
import requests

# گرفتن قیمت‌ها
url = "https://really-amin-datasourceforcryptocurrency-2.hf.space/api/smart/market?limit=10"
response = requests.get(url)
data = response.json()

for coin in data['items']:
    print(f"{coin['name']}: ${coin['current_price']}")
```

---

## 🔥 بهترین سرویس‌ها برای شروع

### 1. قیمت با Fallback
```
GET /api/smart/market?limit=50
```
✅ **بهترین**: خودکار از 21 منبع می‌گیره

### 2. اخبار با Fallback
```
GET /api/smart/news?limit=20
```
✅ **بهترین**: خودکار از 15 منبع خبری می‌گیره

### 3. احساسات بازار
```
GET /api/smart/sentiment
```
✅ **بهترین**: Fear & Greed Index + Social Sentiment

### 4. نمودار شمعی
```
GET /api/market/history?symbol=BTCUSDT&interval=1h&limit=100
```
✅ **بهترین**: داده تاریخی برای نمودار

### 5. تحلیل متن
```
POST /api/sentiment/analyze
Body: {"text": "..."}
```
✅ **بهترین**: 45+ مدل AI

---

## ⚡ نکات سریع

1. **همیشه** از `/api/smart/*` استفاده کنید → Fallback خودکار
2. **WebSocket** برای real-time → `wss://...hf.space/ws`
3. **Cache** کنید → قیمت‌ها 30 ثانیه
4. **Error handling** → همیشه try-catch

---

## 🎉 آماده استفاده!

**همه چیز آماده است. فقط endpoint ها رو صدا بزنید!**

برای جزئیات بیشتر:
- `📖_راهنمای_نهایی_کامل.md` - راهنمای جامع
- `/docs` - مستندات تعاملی
