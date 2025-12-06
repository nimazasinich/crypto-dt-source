# راهنمای کامل دیپلوی Hugging Face

## 🎯 مشکل فعلی و راه حل

### مشکل
سرور روی پورت 7870 نسخه قدیمی را اجرا می‌کند و endpoint های جدید را ندارد.

### راه حل
باید سرور را **کامل متوقف** کنید و دوباره شروع کنید.

---

## 🔄 راه‌اندازی مجدد سرور (Local)

### روش 1: استفاده از اسکریپت خودکار (توصیه می‌شود)

```powershell
.\restart_server.ps1
```

این اسکریپت:
- ✅ تمام پروسه‌های Python روی پورت 7860 و 7870 را می‌کشد
- ✅ سرور جدید را روی پورت 7860 راه‌اندازی می‌کند
- ✅ خطاها را به خوبی نمایش می‌دهد

### روش 2: دستی

#### گام 1: بستن سرور قدیمی

در terminal که سرور در آن اجرا است:
```
Ctrl + C
```

اگر هنوز پورت مشغول است، پروسه را پیدا و بکشید:

```powershell
# پیدا کردن پروسه روی پورت 7870
Get-NetTCPConnection -LocalPort 7870 | Select-Object OwningProcess

# کشتن پروسه (جایگزین PID را با شماره پروسه کنید)
Stop-Process -Id <PID> -Force
```

#### گام 2: شروع سرور جدید

```powershell
cd C:\Users\Dreammaker\Downloads\final_updated_crypto_dthub_project\crypto-dt-source-main
python run_local.py
```

سرور روی پورت **7860** راه‌اندازی می‌شود.

#### گام 3: تست

مرورگر را باز کنید:
- Dashboard: http://localhost:7860/
- API Docs: http://localhost:7860/docs
- Health Check: http://localhost:7860/api/health

در Console مرورگر، **نباید** خطای 404 ببینید.

---

## 🚀 آپلود به Hugging Face Spaces

### فایل‌های مورد نیاز

شما **از قبل** این فایل‌ها را دارید:

#### 1. `Dockerfile` ✅
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["python", "api_server_extended.py"]
```

#### 2. `Spacefile` ✅
```yaml
sdk: docker
app_port: 7860
```

#### 3. `.huggingface.yml` (اگر ندارید، بسازید)
```yaml
sdk: docker
app_port: 7860
```

### مراحل آپلود

#### روش 1: استفاده از Hugging Face CLI (توصیه می‌شود)

```bash
# نصب Hugging Face Hub CLI
pip install huggingface-hub

# لاگین
huggingface-cli login

# آپلود به Space
cd C:\Users\Dreammaker\Downloads\final_updated_crypto_dthub_project\crypto-dt-source-main
huggingface-cli upload Really-amin/Datasourceforcryptocurrency-2 . --repo-type=space
```

#### روش 2: استفاده از رابط وب

1. برو به: https://huggingface.co/spaces/Really-amin/Datasourceforcryptocurrency-2
2. کلیک کن روی **Files** → **Add file** → **Upload files**
3. فایل‌های زیر را آپلود کن:
   - `Dockerfile`
   - `Spacefile`
   - `requirements.txt`
   - `api_server_extended.py`
   - `simple_server.py`
   - پوشه `static/` (کامل)
   - پوشه `backend/` (کامل)
   - سایر فایل‌های Python

---

## 🔍 تشخیص خودکار محیط

کد شما **از قبل** تشخیص محیط را دارد! ✅

### Frontend (JavaScript)

فایل: `config.js`

```javascript
// تشخیص خودکار Hugging Face
const isHuggingFaceSpaces = window.location.hostname.includes('hf.space') ||
                            window.location.hostname.includes('huggingface.co');

// استفاده از Origin فعلی (خودکار)
const API_BASE = window.location.origin;
```

این به این معنی است که:
- روی Local: `http://localhost:7860`
- روی HF: `https://really-amin-datasourceforcryptocurrency-2.hf.space`

**هیچ تغییری نیاز نیست!** ✅

### Backend (Python)

فایل: `api_server_extended.py`

```python
PORT = int(os.getenv("PORT", "7860"))
```

Hugging Face به صورت خودکار متغیر `PORT` را تنظیم می‌کند.

---

## 📋 چک‌لیست قبل از دیپلوی

- [ ] تمام تست‌ها روی Local پاس شدند
- [ ] API endpoints بدون 404 کار می‌کنند
- [ ] Dashboard به درستی لود می‌شود
- [ ] `Dockerfile` موجود است
- [ ] `Spacefile` موجود است
- [ ] `requirements.txt` کامل است
- [ ] فایل‌های `.env` را آپلود **نکنید** (حاوی کلید‌های API)

---

## 🐛 عیب‌یابی

### مشکل: API endpoints 404 می‌دهند

**علت**: سرور قدیمی هنوز در حال اجرا است

**راه حل**:
```powershell
.\restart_server.ps1
```

### مشکل: پورت مشغول است

**راه حل**:
```powershell
# کشتن تمام پروسه‌های Python روی پورت 7860
Get-NetTCPConnection -LocalPort 7860 | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force
}
```

### مشکل: Hugging Face Space "Building" می‌ماند

**راه حل**:
1. بررسی Logs در Hugging Face:
   - برو به Space → **Logs**
   - خطاهای Build را بررسی کن

2. معمولاً مشکلات:
   - `requirements.txt` ناقص است
   - فایل‌های ضروری آپلود نشده‌اند
   - `Dockerfile` اشتباه است

### مشکل: Static files لود نمی‌شوند

**راه حل**:
- مطمئن شوید پوشه `static/` کامل آپلود شده
- در `simple_server.py` بررسی کنید:

```python
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
```

---

## 📊 تست نهایی

### Local (قبل از دیپلوی)

```bash
# تست Health
curl http://localhost:7860/api/health

# تست API endpoints
curl http://localhost:7860/api/coins/top?limit=5
curl http://localhost:7860/api/resources/summary
curl http://localhost:7860/api/models/status
curl http://localhost:7860/api/news/latest?limit=3
```

### Hugging Face (بعد از دیپلوی)

```bash
# تست Health
curl https://really-amin-datasourceforcryptocurrency-2.hf.space/api/health

# تست Dashboard
# باز کردن در مرورگر:
https://really-amin-datasourceforcryptocurrency-2.hf.space/
```

---

## 🎉 خلاصه

### چیزهایی که درست هستند ✅

1. ✅ کد تشخیص محیط را دارد (Local vs HF)
2. ✅ همه API endpoints پیاده‌سازی شده‌اند
3. ✅ `Dockerfile` و `Spacefile` موجود هستند
4. ✅ Frontend از `window.location.origin` استفاده می‌کند

### چیزی که باید انجام دهید 🎯

1. **الان**: سرور Local را Restart کنید
   ```powershell
   .\restart_server.ps1
   ```

2. **بعد از تست Local**: آپلود به Hugging Face
   ```bash
   huggingface-cli upload Really-amin/Datasourceforcryptocurrency-2 . --repo-type=space
   ```

---

## 🔗 لینک‌های مفید

- **Space شما**: https://huggingface.co/spaces/Really-amin/Datasourceforcryptocurrency-2
- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **Docker on Spaces**: https://huggingface.co/docs/hub/spaces-sdks-docker

---

**آخرین بروزرسانی**: 4 دسامبر 2025
**وضعیت**: ✅ آماده برای دیپلوی

