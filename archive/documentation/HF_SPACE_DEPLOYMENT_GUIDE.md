# 🚀 راهنمای استقرار در Hugging Face Space

## 📋 خلاصه

این راهنما نحوه استقرار پروژه در Hugging Face Space با استفاده از **Inference API** را توضیح می‌دهد.

---

## ✅ مزایای استفاده از Inference API

| ویژگی | بارگذاری مستقیم | Inference API |
|-------|------------------|---------------|
| مصرف RAM | 1-4 GB | < 100 MB |
| سرعت | متوسط | بالا (GPU رایگان) |
| محدودیت | RAM محدود | 30K req/month |
| دسترسی به مدل‌های بزرگ | ❌ | ✅ |
| هزینه | رایگان اما محدود | رایگان |

---

## 📦 فایل‌های مورد نیاز

### 1. `requirements.txt` (بهینه شده)

```txt
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
gradio==4.8.0
aiohttp==3.9.1
python-dotenv==1.0.0

# HuggingFace (فقط API و Dataset)
huggingface-hub==0.19.4
datasets==2.15.0

# Data
pandas==2.1.3
numpy==1.26.2

# Optional: فقط برای local testing
# transformers==4.35.2
# torch==2.1.1
```

### 2. `README.md` (برای HF Space)

```markdown
---
title: Crypto AI Analyzer
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.8.0
app_file: app.py
pinned: false
license: mit
---

# 🤖 Crypto AI Analyzer

تحلیل هوش مصنوعی متن‌های کریپتو با استفاده از Hugging Face Inference API.

## Features
- 🎯 Sentiment analysis (Crypto, Social, Financial)
- 🤖 Ensemble learning from multiple models
- 📊 Free access to 30,000 API calls per month
- ⚡ Fast processing with GPU acceleration

## Models Used
- kk08/CryptoBERT
- ElKulako/cryptobert
- ProsusAI/finbert
- cardiffnlp/twitter-roberta-base-sentiment-latest

## API Endpoints
- `POST /api/ai/sentiment` - تحلیل sentiment
- `POST /api/ai/sentiment/bulk` - تحلیل چند متن
- `GET /api/ai/data/prices/quick/{symbol}` - قیمت‌های تاریخی
- `GET /api/ai/data/news` - اخبار کریپتو

## Usage
```python
import requests

response = requests.post(
    "https://YOUR-SPACE.hf.space/api/ai/sentiment",
    json={"text": "Bitcoin to the moon!", "category": "crypto"}
)
print(response.json())
```
```

### 3. `app.py` (نقطه ورود)

```python
#!/usr/bin/env python3
"""
Hugging Face Space - Optimized Entry Point
"""

import gradio as gr
import asyncio
from backend.services.ai_service_unified import get_unified_service

# تنظیم محیط برای HF Space
import os
os.environ["USE_HF_API"] = "true"  # استفاده از Inference API

async def analyze_text_ui(text: str, analysis_type: str):
    """تحلیل متن در UI"""
    if not text:
        return "⚠️ لطفاً متنی وارد کنید"
    
    service = await get_unified_service()
    
    category_map = {
        "Crypto Sentiment": "crypto",
        "Social Sentiment": "social",
        "Financial Sentiment": "financial",
        "Ensemble (All)": "crypto"
    }
    
    category = category_map.get(analysis_type, "crypto")
    use_ensemble = (analysis_type == "Ensemble (All)")
    
    result = await service.analyze_sentiment(text, category, use_ensemble)
    
    if result.get("status") == "success":
        label = result["label"]
        confidence = result["confidence"]
        emoji = "📈" if label == "bullish" else ("📉" if label == "bearish" else "➡️")
        
        output = f"""
{emoji} **Sentiment**: {label.upper()}
🎯 **Confidence**: {confidence:.2%}
🤖 **Engine**: {result.get('engine', 'unknown')}
        """
        
        if result.get("model_count"):
            output += f"\n📊 **Models Used**: {result['model_count']}"
        
        return output.strip()
    
    return f"❌ Error: {result.get('error', 'Unknown')}"

# ایجاد رابط Gradio
with gr.Blocks(title="Crypto AI Analyzer", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown("""
    # 🤖 Crypto AI Analyzer
    ### تحلیل هوش مصنوعی متن‌های کریپتو
    
    از Hugging Face Inference API برای تحلیل sentiment استفاده می‌کند.
    """)
    
    with gr.Tab("💬 Sentiment Analysis"):
        text_input = gr.Textbox(
            label="متن خود را وارد کنید",
            placeholder="Bitcoin is showing strong momentum...",
            lines=3
        )
        
        analysis_type = gr.Radio(
            choices=["Crypto Sentiment", "Social Sentiment", "Financial Sentiment", "Ensemble (All)"],
            value="Ensemble (All)",
            label="نوع تحلیل"
        )
        
        analyze_btn = gr.Button("🔍 Analyze", variant="primary")
        output = gr.Markdown()
        
        analyze_btn.click(
            fn=analyze_text_ui,
            inputs=[text_input, analysis_type],
            outputs=output
        )
    
    with gr.Tab("📊 Models"):
        gr.Markdown("""
        ### مدل‌های استفاده شده
        
        | Model | Task |
        |-------|------|
        | kk08/CryptoBERT | Crypto sentiment |
        | ElKulako/cryptobert | Social sentiment |
        | ProsusAI/finbert | Financial sentiment |
        | cardiffnlp/twitter-roberta | Twitter sentiment |
        """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
```

---

## 🔧 تنظیمات محیطی

در **Settings** مخزن HF Space، متغیرهای زیر را تنظیم کنید:

```bash
# اختیاری: برای دسترسی به مدل‌های private
HF_TOKEN=your_huggingface_token

# اجباری: استفاده از API
USE_HF_API=true

# اختیاری: سطح لاگ
LOG_LEVEL=INFO
```

---

## 📁 ساختار فایل‌های مورد نیاز

```
your-hf-space/
├── app.py                                    # نقطه ورود
├── requirements.txt                          # وابستگی‌ها
├── README.md                                 # توضیحات Space
├── backend/
│   └── services/
│       ├── __init__.py
│       ├── hf_inference_api_client.py       # کلاینت API
│       ├── hf_dataset_loader.py             # Dataset loader
│       └── ai_service_unified.py            # سرویس یکپارچه
```

---

## 🚀 مراحل استقرار

### 1️⃣ ایجاد Space جدید

1. به [huggingface.co/spaces](https://huggingface.co/spaces) بروید
2. **Create new Space** را کلیک کنید
3. نام Space را وارد کنید (مثلاً `crypto-ai-analyzer`)
4. SDK را **Gradio** انتخاب کنید
5. **Create Space** را کلیک کنید

### 2️⃣ آپلود فایل‌ها

```bash
# Clone کردن Space
git clone https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME
cd YOUR-SPACE-NAME

# کپی فایل‌ها
cp /path/to/project/app.py .
cp /path/to/project/requirements.txt .
cp /path/to/project/README.md .

# ایجاد ساختار backend
mkdir -p backend/services
cp /path/to/project/backend/services/*.py backend/services/

# Commit و Push
git add .
git commit -m "Initial deployment"
git push
```

### 3️⃣ تنظیم متغیرهای محیطی

1. به صفحه Space بروید
2. **Settings** → **Repository secrets**
3. افزودن:
   - `HF_TOKEN`: توکن Hugging Face (اختیاری)
   - `USE_HF_API`: `true`

### 4️⃣ بررسی لاگ‌ها

1. به تب **Logs** بروید
2. منتظر بمانید تا Space بارگذاری شود
3. اگر خطایی دیدید، لاگ‌ها را بررسی کنید

---

## 🧪 تست Space

### تست UI
1. به URL Space بروید: `https://YOUR-USERNAME-YOUR-SPACE.hf.space`
2. متنی وارد کنید و دکمه Analyze را بزنید

### تست API
```python
import requests

# URL Space شما
SPACE_URL = "https://YOUR-USERNAME-YOUR-SPACE.hf.space"

# تست sentiment analysis
response = requests.post(
    f"{SPACE_URL}/api/ai/sentiment",
    json={
        "text": "Bitcoin is pumping to the moon!",
        "category": "crypto",
        "use_ensemble": True
    }
)

print(response.json())
```

---

## 📊 محدودیت‌ها و توصیه‌ها

### محدودیت Free Tier HF Space:
- **CPU**: 2 vCPU
- **RAM**: 16 GB
- **Storage**: 50 GB
- **Inference API**: 30,000 req/month

### توصیه‌ها:
1. ✅ استفاده از Inference API (بجای بارگذاری مستقیم)
2. ✅ Cache کردن نتایج برای کاهش درخواست‌ها
3. ✅ استفاده از Dataset‌های HF برای داده تاریخی
4. ✅ نگهداری لاگ‌ها برای debugging

---

## 🐛 عیب‌یابی

### خطا: "Model is loading"
- **دلیل**: مدل در سرور HF در حال بارگذاری است
- **راه حل**: 20 ثانیه صبر کنید و دوباره تلاش کنید

### خطا: "Rate limit exceeded"
- **دلیل**: از محدودیت 30K درخواست عبور کردید
- **راه حل**: استفاده از cache، یا ارتقا به Pro

### خطا: "Authentication required"
- **دلیل**: مدل نیاز به authentication دارد
- **راه حل**: `HF_TOKEN` را در Settings تنظیم کنید

### خطا: "datasets library not available"
- **دلیل**: کتابخانه datasets نصب نیست
- **راه حل**: `datasets` را به `requirements.txt` اضافه کنید

---

## 📚 منابع اضافی

### Documentation:
- [HuggingFace Spaces](https://huggingface.co/docs/hub/spaces)
- [Inference API](https://huggingface.co/docs/api-inference)
- [Datasets](https://huggingface.co/docs/datasets)

### مدل‌های پیشنهادی:
- [kk08/CryptoBERT](https://huggingface.co/kk08/CryptoBERT)
- [ElKulako/cryptobert](https://huggingface.co/ElKulako/cryptobert)
- [ProsusAI/finbert](https://huggingface.co/ProsusAI/finbert)

### Dataset‌های رایگان:
- [linxy/CryptoCoin](https://huggingface.co/datasets/linxy/CryptoCoin)
- [Kwaai/crypto-news](https://huggingface.co/datasets/Kwaai/crypto-news)

---

## ✅ چک‌لیست استقرار

- [ ] فایل `app.py` ایجاد شده
- [ ] فایل `requirements.txt` با وابستگی‌های بهینه
- [ ] فایل `README.md` با metadata صحیح
- [ ] پوشه `backend/services/` با کلاینت‌ها
- [ ] `USE_HF_API=true` در متغیرهای محیطی
- [ ] تست UI با یک متن نمونه
- [ ] تست API با curl یا requests
- [ ] بررسی لاگ‌ها برای خطاهای احتمالی

---

## 🎉 مراحل بعدی

بعد از استقرار موفق:

1. ✅ تست کامل تمام endpoint‌ها
2. ✅ اضافه کردن monitoring و logging
3. ✅ بهینه‌سازی cache برای کاهش درخواست‌ها
4. ✅ اضافه کردن مدل‌های بیشتر
5. ✅ ایجاد dashboard برای آمار

---

**موفق باشید! 🚀**
