# تأیید پورت 7860 در همه جا / Port 7860 Verification

## ✅ بررسی کامل پورت 7860

### فایل‌های Backend:

1. **`api_server_extended.py`**
   - ✅ خط 54: `PORT = int(os.getenv("PORT", "7860"))`
   - ✅ خط 5383: `port = int(os.getenv("PORT", os.getenv("HF_PORT", "7860")))`
   - ✅ استفاده از متغیر محیطی PORT (که Hugging Face تنظیم می‌کند)

2. **`Dockerfile`**
   - ✅ خط 25: `# ENV PORT=7860  # Commented out - Hugging Face sets this`
   - ✅ خط 34: `EXPOSE 7860`
   - ✅ خط 38: Health check از `localhost:7860` استفاده می‌کند

3. **`docker-compose.yml`**
   - ✅ خط 9: `- "7860:7860"`
   - ✅ خط 12: `- PORT=7860`
   - ✅ خط 28: Health check از `localhost:7860` استفاده می‌کند

### فایل‌های Hugging Face:

4. **`.huggingface.yml`**
   - ✅ خط 2: `app_port: 7860`
   - ✅ خط 20: `PORT: 7860`

5. **`Spacefile`**
   - ✅ خط 15: `app_port: 7860`

### فایل‌های Frontend/Public:

6. **`config.js`** (Root)
   - ✅ خط 25: `return 'http://localhost:7860';`
   - ✅ خط 35: `const host = isLocalhost ? 'localhost:7860' : window.location.host;`

7. **`static/shared/js/core/config.js`**
   - ✅ خط 12: `API_BASE_URL: window.location.origin + '/api'`
   - ✅ استفاده از `window.location.origin` (خودکار - از پورت فعلی استفاده می‌کند)

### فایل‌های Documentation:

8. **`static/pages/news/examples/README.md`**
   - ✅ اصلاح شد: از 8000 به 7860 تغییر یافت

---

## 📋 خلاصه:

✅ **همه فایل‌های مهم از پورت 7860 استفاده می‌کنند**

- Backend: ✅ 7860
- Docker: ✅ 7860
- Hugging Face Config: ✅ 7860
- Frontend Config: ✅ 7860 (یا از window.location.origin استفاده می‌کند)
- Documentation: ✅ 7860

---

## 🔍 نکات مهم:

1. **Hugging Face Spaces**: پورت را به صورت خودکار تنظیم می‌کند
   - فایل `.huggingface.yml` و `Spacefile` پورت 7860 را مشخص می‌کنند
   - Hugging Face این پورت را به متغیر محیطی `PORT` تبدیل می‌کند
   - اپلیکیشن از `os.getenv("PORT", "7860")` استفاده می‌کند

2. **Frontend**: از `window.location.origin` استفاده می‌کند
   - این یعنی frontend خودکار از پورت فعلی استفاده می‌کند
   - برای localhost: از `config.js` که 7860 را hardcode کرده استفاده می‌شود

3. **Docker**: پورت 7860 expose شده و در docker-compose هم 7860 است

---

**وضعیت**: ✅ **همه جا از پورت 7860 استفاده می‌شود**

**تاریخ**: 2025-12-02

