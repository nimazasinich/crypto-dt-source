# 🚀 راهنمای سریع شروع

## مرحله 1: تنظیم توکن (فقط یک بار)

### روی Hugging Face Space:
1. به Space خود بروید
2. `Settings` → `Repository secrets`
3. دو secret اضافه کنید:
   ```
   HF_TOKEN = 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
   HF_MODE = public
   ```
4. Space را Restart کنید

### روی Windows Local:
```powershell
$env:HF_TOKEN="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"
$env:HF_MODE="public"
```

---

## مرحله 2: اجرای سرور

```bash
python api_server_extended.py
```

منتظر بمانید تا:
```
✓ AI Models initialized
✓ Server ready on port 7860
```

---

## مرحله 3: مرور برنامه

1. **صفحه اصلی:** http://localhost:7860/
2. **AI Tools:** http://localhost:7860/ai-tools

---

## تست سریع

### Sentiment Analysis:
1. به `http://localhost:7860/ai-tools` بروید
2. متن وارد کنید: "Bitcoin price is surging!"
3. روی "Analyze Sentiment" کلیک کنید
4. نتیجه: **BULLISH/POSITIVE** ✅

### Trading Pairs:
1. به صفحه اصلی بروید
2. تب "Sentiment" → "Per-Asset Sentiment"
3. dropdown را باز کنید
4. باید 300 جفت ارز را ببینید ✅

---

## عیب‌یابی سریع

### مشکل: مدل‌ها لود نمی‌شوند
```powershell
# بررسی توکن
$env:HF_TOKEN
$env:HF_MODE

# تنظیم مجدد
$env:HF_TOKEN="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"
$env:HF_MODE="public"
```

### مشکل: خبرها نمایش داده نمی‌شوند
- ابتدا یک خبر را از تب Sentiment → News Analysis اضافه کنید
- سپس به تب News بروید

---

## فایل‌های مهم

- `SET_HF_TOKEN.md` - راهنمای کامل تنظیم توکن
- `FINAL_FIXES_SUMMARY.md` - خلاصه کامل تغییرات
- `test_fixes.py` - تست خودکار

---

**همین! برنامه شما آماده است! 🎉**

