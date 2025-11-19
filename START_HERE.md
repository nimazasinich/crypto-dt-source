# 🚀 شروع سریع - START HERE

## یک دستور برای اجرای کامل! ⚡

```powershell
.\run_server.ps1
```

این دستور:
- ✅ توکن HF را تنظیم می‌کند
- ✅ تست‌ها را اجرا می‌کند
- ✅ سرور را شروع می‌کند

---

## یا به صورت مرحله‌ای:

### مرحله 1: تنظیم Environment Variables
```powershell
.\set_env.ps1
```

### مرحله 2: تست سیستم
```powershell
python test_fixes.py
```

### مرحله 3: اجرای سرور
```powershell
python api_server_extended.py
```

---

## دسترسی به برنامه:

پس از اجرا، به این آدرس‌ها بروید:

- 🏠 **صفحه اصلی:** http://localhost:7860/
- 🤖 **AI Tools:** http://localhost:7860/ai-tools
- 📚 **API Docs:** http://localhost:7860/docs
- 💚 **Health Check:** http://localhost:7860/health

---

## نتیجه تست شما:

```
✅ File Existence - PASS
✅ Trading Pairs - PASS
✅ Index.html Links - PASS
✅ AI Models Config - PASS
⚠️  Environment Variables - FAIL (حل می‌شود با run_server.ps1)
✅ App.js Functions - PASS

Score: 5/6 (83.3%)
```

---

## حل مشکل Environment Variables:

### گزینه 1: استفاده از اسکریپت (توصیه می‌شود)
```powershell
.\run_server.ps1
```

### گزینه 2: دستی
```powershell
$env:HF_TOKEN="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"
$env:HF_MODE="public"
python api_server_extended.py
```

### گزینه 3: دائمی (در System Environment Variables)
1. Win + R → `sysdm.cpl`
2. Advanced → Environment Variables
3. New → Name: `HF_TOKEN`, Value: `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`
4. New → Name: `HF_MODE`, Value: `public`

---

## 🎯 توصیه:

**ساده‌ترین راه:**
```powershell
.\run_server.ps1
```

این همه چیز را برای شما انجام می‌دهد! ✨

---

## 📖 راهنماهای بیشتر:

- `QUICK_START_FA.md` - راهنمای سریع فارسی
- `FINAL_FIXES_SUMMARY.md` - اطلاعات کامل تغییرات
- `SET_HF_TOKEN.md` - راهنمای تنظیم توکن

---

**حالا فقط یک دستور فاصله دارید! 🚀**

```powershell
.\run_server.ps1
```

