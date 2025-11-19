# تنظیم توکن Hugging Face

## توکن شما:
```
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
```

## روش‌های تنظیم:

### 1. روی Hugging Face Space (توصیه شده):

1. به Space خود بروید
2. بروید به **Settings** → **Repository secrets**
3. دو secret اضافه کنید:

**Secret 1:**
- Name: `HF_TOKEN`
- Value: `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`

**Secret 2:**
- Name: `HF_MODE`
- Value: `public`

4. Space را Restart کنید

---

### 2. روی Windows (Local):

در PowerShell:
```powershell
$env:HF_TOKEN="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"
$env:HF_MODE="public"
python api_server_extended.py
```

یا برای دائمی کردن، در System Environment Variables:
1. Win + R → `sysdm.cpl` → Advanced → Environment Variables
2. در User variables، New کنید:
   - Name: `HF_TOKEN`
   - Value: `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`
3. یکی دیگر:
   - Name: `HF_MODE`
   - Value: `public`

---

### 3. روی Linux/Mac (Local):

در terminal:
```bash
export HF_TOKEN="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"
export HF_MODE="public"
python api_server_extended.py
```

یا در `~/.bashrc` یا `~/.zshrc` اضافه کنید:
```bash
export HF_TOKEN="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"
export HF_MODE="public"
```

---

### 4. با فایل .env:

فایل `.env` در root پروژه ایجاد کنید:
```
HF_TOKEN=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
HF_MODE=public
PORT=7860
```

سپس در PowerShell قبل از اجرا:
```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}
python api_server_extended.py
```

---

## بررسی تنظیمات:

پس از تنظیم، بررسی کنید:
```powershell
python -c "import os; print('HF_TOKEN:', 'SET' if os.getenv('HF_TOKEN') else 'NOT SET'); print('HF_MODE:', os.getenv('HF_MODE', 'not set'))"
```

یا با تست:
```powershell
python test_fixes.py
```

---

## نکته امنیتی:
⚠️ **این توکن را public نکنید!**
- در git commit نکنید
- در GitHub/GitLab share نکنید
- فقط در Secrets استفاده کنید

