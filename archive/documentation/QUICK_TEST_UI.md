# راهنمای سریع تست رابط کاربری

## 🚀 تست سریع

### 1. تست با اسکریپت خودکار:
```bash
cd /workspace
python3 test_ui_routing.py
```

**خروجی مورد انتظار:**
```
✅ UI Routing Configuration: COMPLETE
📊 Test Results: 21/21 checks passed (100.0%)
```

---

## 🌐 تست با مرورگر

### دسترسی محلی:
1. سرور را اجرا کنید:
   ```bash
   python3 main.py
   ```

2. مرورگر را باز کنید و به آدرس‌های زیر بروید:
   - `http://localhost:7860/` - صفحه اصلی
   - `http://localhost:7860/dashboard` - داشبورد
   - `http://localhost:7860/admin` - پنل ادمین
   - `http://localhost:7860/console` - کنسول HuggingFace

### دسترسی HuggingFace Space:
- `https://really-amin-datasourceforcryptocurrency.hf.space/`
- `https://really-amin-datasourceforcryptocurrency.hf.space/dashboard`
- `https://really-amin-datasourceforcryptocurrency.hf.space/admin`
- `https://really-amin-datasourceforcryptocurrency.hf.space/console`

---

## 🧪 تست با curl

### تست صفحه اصلی:
```bash
curl -I http://localhost:7860/
# انتظار: HTTP/1.1 200 OK
```

### تست فایل‌های Static:
```bash
# تست CSS
curl -I http://localhost:7860/static/css/dashboard.css
# انتظار: HTTP/1.1 200 OK

# تست JS
curl -I http://localhost:7860/static/js/dashboard.js
# انتظار: HTTP/1.1 200 OK
```

### تست همه صفحات:
```bash
# صفحه اصلی
curl -I http://localhost:7860/

# Dashboard
curl -I http://localhost:7860/dashboard.html
curl -I http://localhost:7860/dashboard

# Admin
curl -I http://localhost:7860/admin.html
curl -I http://localhost:7860/admin

# HF Console
curl -I http://localhost:7860/hf_console.html
curl -I http://localhost:7860/console

# Pool Management
curl -I http://localhost:7860/pool_management.html

# Unified Dashboard
curl -I http://localhost:7860/unified_dashboard.html

# Simple Overview
curl -I http://localhost:7860/simple_overview.html
```

---

## 📊 بررسی Log ها

بعد از اجرای سرور، باید log های زیر را ببینید:

```
======================================================================
🚀 Cryptocurrency Data & Analysis API Starting
======================================================================
✓ FastAPI initialized
✓ CORS configured
✓ Cache initialized
✓ Providers loaded: 95
✓ HuggingFace Space providers: huggingface_space_api, huggingface_space_hf_integration
✓ Data sources: Binance, CoinGecko, providers_config_extended.json
✓ UI files: 4/4 available
======================================================================
📡 API ready at http://0.0.0.0:7860
📖 Docs at http://0.0.0.0:7860/docs
🎨 UI at http://0.0.0.0:7860/ (index.html)
======================================================================
```

---

## ✅ چک‌لیست تست

- [ ] اسکریپت `test_ui_routing.py` با موفقیت اجرا شد
- [ ] همه 21 تست passed شدند
- [ ] صفحه اصلی (/) بدون خطا باز می‌شود
- [ ] Dashboard قابل دسترسی است
- [ ] Admin Panel قابل دسترسی است
- [ ] HF Console قابل دسترسی است
- [ ] فایل‌های CSS از `/static/css/` بارگذاری می‌شوند
- [ ] فایل‌های JS از `/static/js/` بارگذاری می‌شوند
- [ ] لینک‌های بین صفحات کار می‌کنند
- [ ] API Documentation در `/docs` قابل دسترسی است

---

## 🔍 عیب‌یابی

### مشکل: صفحه 404 نمایش داده می‌شود
**راه‌حل:**
1. مطمئن شوید سرور اجرا شده است
2. مسیر URL را بررسی کنید
3. فایل HTML را در `/workspace` بررسی کنید

### مشکل: فایل‌های CSS/JS بارگذاری نمی‌شوند
**راه‌حل:**
1. مطمئن شوید پوشه `static/` وجود دارد
2. مطمئن شوید فایل‌ها در `static/css/` و `static/js/` هستند
3. Console مرورگر را برای خطاها بررسی کنید

### مشکل: سرور start نمی‌شود
**راه‌حل:**
1. dependency ها را نصب کنید: `pip install -r requirements.txt`
2. Port 7860 را بررسی کنید: `lsof -i :7860`
3. Log ها را بررسی کنید

---

## 📞 کمک بیشتر

برای اطلاعات بیشتر، مستندات زیر را ببینید:
- `UI_ROUTING_SUMMARY_FA.md` - گزارش کامل مسیریابی UI
- `ROUTING_CONNECTION_SUMMARY_FA.md` - جزئیات اتصال routing
- `README_HUGGINGFACE_API.md` - مستندات API
