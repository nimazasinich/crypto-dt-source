# راهنمای تنظیم Hugging Face Models

## مشکلات احتمالی و راه‌حل‌ها

### 1. مدل‌ها لود نمی‌شوند

**علت**: توکن Hugging Face تنظیم نشده یا `HF_MODE` غلط است.

**راه‌حل**:

#### روی Hugging Face Spaces:
1. به تب **Settings** مخزن خود بروید
2. در بخش **Repository secrets** یک secret جدید اضافه کنید:
   - Name: `HF_TOKEN`
   - Value: توکن شخصی شما از https://huggingface.co/settings/tokens
3. یک secret دیگر اضافه کنید:
   - Name: `HF_MODE`
   - Value: `public` (یا `auth` برای مدل‌های خصوصی)

#### روی Local:
```bash
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxx"
export HF_MODE="public"
python api_server_extended.py
```

#### روی Docker:
```bash
docker run -e HF_TOKEN="hf_xxx" -e HF_MODE="public" ...
```

### 2. خطای "Invalid model identifier"

**علت**: مدل در LINKED_MODEL_IDS نیست یا توکن نیاز است.

**راه‌حل**: 
- مدل‌های زیر در Space شما باید linked شوند:
  - cardiffnlp/twitter-roberta-base-sentiment-latest
  - ProsusAI/finbert
  - mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis
  - kk08/CryptoBERT
  - burakutf/finetuned-finbert-crypto

### 3. چارت‌ها نمایش داده نمی‌شوند

**علت**: Chart.js لود نشده است.

**راه‌حل**: مطمئن شوید که این خط در `index.html` وجود دارد:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

### 4. جفت ارزها نمایش داده نمی‌شوند

**علت**: فایل `trading_pairs.txt` در دسترس نیست یا `trading-pairs-loader.js` لود نشده.

**راه‌حل**:
1. مطمئن شوید فایل `trading_pairs.txt` در root پروژه وجود دارد
2. مطمئن شوید این خط در `index.html` قبل از `app.js` وجود دارد:
```html
<script src="/static/js/trading-pairs-loader.js" defer></script>
```

## تنظیمات پیشنهادی

### برای HF Spaces (توصیه شده):
```env
HF_MODE=public
HF_TOKEN=hf_your_token_here
PORT=7860
```

### برای Local Development:
```env
HF_MODE=public
HF_TOKEN=hf_your_token_here
PORT=7860
USE_MOCK_DATA=false
```

## بررسی وضعیت مدل‌ها

پس از راه‌اندازی، به این آدرس‌ها بروید:

1. **صفحه اصلی**: http://localhost:7860/
2. **AI Tools Page**: http://localhost:7860/ai-tools
3. **API Status**: http://localhost:7860/api/models/status
4. **API Docs**: http://localhost:7860/docs

### پاسخ موفق از /api/models/status:
```json
{
  "success": true,
  "status": "ok",
  "hf_mode": "public",
  "models_loaded": 4,
  "models_failed": 0,
  "transformers_available": true
}
```

### پاسخ مشکل‌دار:
```json
{
  "success": true,
  "status": "no_models_loaded",
  "hf_mode": "off",
  "models_loaded": 0,
  "models_failed": 0
}
```
**راه‌حل**: HF_MODE را روی `public` تنظیم کنید.

## Fallback System

اگر مدل‌های HF در دسترس نباشند، سیستم به صورت خودکار به sentiment analysis مبتنی بر keyword fallback می‌کند:

- **Bullish keywords**: rally, surge, pump, moon, gain, etc.
- **Bearish keywords**: dump, crash, selloff, panic, loss, etc.
- **Confidence**: 0.6-0.9 بسته به تعداد کلمات

## دیباگ کردن

### 1. بررسی لاگ‌ها:
```bash
tail -f logs/*.log
```

### 2. بررسی در Python REPL:
```python
import os
print("HF_TOKEN:", "Yes" if os.getenv("HF_TOKEN") else "No")
print("HF_MODE:", os.getenv("HF_MODE", "not set"))

from ai_models import initialize_models
result = initialize_models()
print(result)
```

### 3. بررسی در Browser Console:
```javascript
fetch('/api/models/status')
  .then(r => r.json())
  .then(d => console.log(d));
```

## سوالات متداول

**Q: مدل‌ها چقدر طول می‌کشد تا لود شوند؟**  
A: اولین بار 30-60 ثانیه. بارهای بعدی از cache استفاده می‌کنند (< 5 ثانیه).

**Q: آیا می‌توانم بدون توکن استفاده کنم؟**  
A: بله، اما ممکن است rate limit شوید. برای استفاده بدون محدودیت، توکن لازم است.

**Q: چگونه می‌فهمم مدل‌ها کار می‌کنند؟**  
A: به `/ai-tools` بروید و در sentiment playground تست کنید.

**Q: آیا می‌توانم مدل‌های خودم را اضافه کنم؟**  
A: بله، در `ai_models.py` در لیست‌های مربوطه اضافه کنید و مدل را به LINKED_MODEL_IDS اضافه کنید.

## Support

برای گزارش مشکل یا سوال، به issues مخزن GitHub مراجعه کنید.

