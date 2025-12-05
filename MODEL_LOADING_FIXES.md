# 🤖 راهنمای کامل بارگذاری و بهینه‌سازی مدل‌های AI

## 📊 تحلیل وضعیت فعلی

### ✅ **نقاط قوت موجود**

```python
# فایل ai_models.py شما شامل:
✓ سیستم مدیریت مدل پیشرفته (ModelRegistry)
✓ Health tracking برای مدل‌ها
✓ Self-healing و retry mechanism
✓ Fallback به تحلیل لغوی
✓ 11 مدل مختلف کریپتو
✓ پشتیبانی از sentiment، trading signals، و generation
```

### ❌ **مشکلات شناسایی شده**

1. **مدل‌های بارگذاری نشده**
   - برخی مدل‌ها نیاز به authentication دارند
   - برخی repository ها پیدا نمی‌شوند
   - محدودیت rate limit در Hugging Face

2. **مصرف منابع**
   - مدل‌ها در RAM بارگذاری می‌شوند (هر کدام 300MB-1GB)
   - در Hugging Face Space محدودیت RAM وجود دارد

3. **نیاز به بهینه‌سازی**
   - استفاده از Inference API بهتر از بارگذاری مستقیم
   - نیاز به caching هوشمندتر
   - استفاده بهینه از منابع محدود

---

## 🚀 **راهکارهای پیشنهادی**

### 1️⃣ **استفاده از Hugging Face Inference API**

به جای بارگذاری مستقیم مدل‌ها، از API استفاده کنید:

```python
# backend/services/hf_inference_api_client.py
import aiohttp
import os
from typing import Dict, List, Optional, Any
import asyncio

class HFInferenceAPIClient:
    """
    کلاینت برای Hugging Face Inference API
    مزایا:
    - نیازی به بارگذاری مدل در RAM نیست
    - دسترسی به مدل‌های بزرگتر
    - پردازش سریعتر (GPU در سرورهای HF)
    - 30,000 درخواست رایگان در ماه
    """
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("HF_TOKEN")
        self.base_url = "https://api-inference.huggingface.co/models"
        self.session = None
        
        # مدل‌های تأیید شده که در HF API کار می‌کنند
        self.verified_models = {
            "crypto_sentiment": "kk08/CryptoBERT",
            "social_sentiment": "ElKulako/cryptobert",
            "financial_sentiment": "ProsusAI/finbert",
            "twitter_sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "crypto_gen": "OpenC/crypto-gpt-o3-mini",
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def analyze_sentiment(
        self, 
        text: str, 
        model_key: str = "crypto_sentiment"
    ) -> Dict[str, Any]:
        """
        تحلیل sentiment با استفاده از HF Inference API
        """
        model_id = self.verified_models.get(model_key)
        if not model_id:
            return {"error": f"Unknown model key: {model_key}"}
        
        url = f"{self.base_url}/{model_id}"
        headers = {}
        
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        
        payload = {"inputs": text[:512]}  # محدودیت طول متن
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(
                url, 
                json=payload, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 503:
                    # مدل در حال بارگذاری است
                    return {
                        "status": "loading",
                        "message": "Model is loading, please retry in 20 seconds"
                    }
                
                if response.status == 200:
                    data = await response.json()
                    
                    # استخراج نتیجه
                    if isinstance(data, list) and len(data) > 0:
                        if isinstance(data[0], list):
                            result = data[0][0]
                        else:
                            result = data[0]
                        
                        # استانداردسازی خروجی
                        label = result.get("label", "NEUTRAL").upper()
                        score = result.get("score", 0.5)
                        
                        # تبدیل به فرمت استاندارد
                        mapped = self._map_label(label)
                        
                        return {
                            "status": "success",
                            "label": mapped,
                            "confidence": score,
                            "raw_label": label,
                            "model": model_id,
                            "engine": "hf_inference_api"
                        }
                
                error_text = await response.text()
                return {
                    "status": "error",
                    "error": f"HTTP {response.status}: {error_text[:200]}"
                }
                
        except asyncio.TimeoutError:
            return {
                "status": "error",
                "error": "Request timeout after 30 seconds"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)[:200]
            }
    
    def _map_label(self, label: str) -> str:
        """تبدیل برچسب‌های مختلف به فرمت استاندارد"""
        label_upper = label.upper()
        
        if any(x in label_upper for x in ["POSITIVE", "BULLISH", "LABEL_2"]):
            return "bullish"
        elif any(x in label_upper for x in ["NEGATIVE", "BEARISH", "LABEL_0"]):
            return "bearish"
        else:
            return "neutral"
    
    async def ensemble_sentiment(
        self, 
        text: str, 
        models: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        استفاده از چندین مدل به صورت همزمان (ensemble)
        """
        if models is None:
            models = ["crypto_sentiment", "social_sentiment", "financial_sentiment"]
        
        # فراخوانی موازی مدل‌ها
        tasks = [self.analyze_sentiment(text, model) for model in models]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # جمع‌آوری نتایج موفق
        successful_results = []
        for result in results:
            if isinstance(result, dict) and result.get("status") == "success":
                successful_results.append(result)
        
        if not successful_results:
            return {
                "status": "error",
                "error": "All models failed",
                "fallback": True
            }
        
        # رای‌گیری بین نتایج
        labels = [r["label"] for r in successful_results]
        confidences = [r["confidence"] for r in successful_results]
        
        # برچسب با بیشترین فراوانی
        from collections import Counter
        label_counts = Counter(labels)
        final_label = label_counts.most_common(1)[0][0]
        
        # میانگین اعتماد
        avg_confidence = sum(confidences) / len(confidences)
        
        return {
            "status": "success",
            "label": final_label,
            "confidence": avg_confidence,
            "model_count": len(successful_results),
            "votes": dict(label_counts),
            "models_used": [r["model"] for r in successful_results],
            "engine": "hf_inference_api_ensemble"
        }


# ===== تابع کمکی برای استفاده آسان =====
async def analyze_crypto_sentiment_via_api(text: str) -> Dict[str, Any]:
    """
    تحلیل sentiment کریپتو با استفاده از HF Inference API
    """
    async with HFInferenceAPIClient() as client:
        return await client.ensemble_sentiment(text)
```

---

### 2️⃣ **استفاده از Dataset‌های رایگان Hugging Face**

```python
# backend/services/hf_dataset_loader.py
from datasets import load_dataset
import pandas as pd
from typing import Dict, List, Optional

class HFDatasetService:
    """
    سرویس برای بارگذاری و استفاده از Dataset‌های رایگان HF
    """
    
    # Dataset‌های معتبر کریپتو
    CRYPTO_DATASETS = {
        "linxy/CryptoCoin": {
            "description": "182 فایل CSV با OHLCV برای 26 کریپتو",
            "symbols": ["BTC", "ETH", "BNB", "SOL", "ADA", "XRP", "DOT", "DOGE"],
            "timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
        },
        "WinkingFace/CryptoLM-Bitcoin-BTC-USDT": {
            "description": "داده تاریخی Bitcoin",
            "timeframes": ["1h"]
        },
        "sebdg/crypto_data": {
            "description": "OHLCV + indicators برای 10 کریپتو",
            "indicators": ["RSI", "MACD", "Bollinger Bands"]
        }
    }
    
    async def load_crypto_ohlcv(
        self, 
        symbol: str = "BTC", 
        timeframe: str = "1h",
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        بارگذاری OHLCV از Dataset
        """
        try:
            # بارگذاری از linxy/CryptoCoin
            dataset_name = f"linxy/CryptoCoin"
            
            # بارگذاری Dataset
            dataset = load_dataset(
                dataset_name,
                split="train",
                streaming=True  # برای صرفه‌جویی در RAM
            )
            
            # تبدیل به DataFrame
            df = pd.DataFrame(dataset.take(limit))
            
            # فیلتر بر اساس symbol
            if "symbol" in df.columns:
                df = df[df["symbol"] == symbol]
            
            return df
            
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return pd.DataFrame()
    
    def get_available_datasets(self) -> Dict[str, Any]:
        """
        لیست Dataset‌های موجود
        """
        return {
            "total": len(self.CRYPTO_DATASETS),
            "datasets": self.CRYPTO_DATASETS
        }
```

---

### 3️⃣ **بهینه‌سازی برای Hugging Face Space**

```python
# hf_space_optimized_app.py
"""
نسخه بهینه شده برای استقرار در Hugging Face Space
"""

import gradio as gr
import asyncio
from backend.services.hf_inference_api_client import HFInferenceAPIClient

# ===== تنظیمات بهینه برای HF Space =====
HF_SPACE_CONFIG = {
    "enable_local_models": False,  # غیرفعال کردن بارگذاری مستقیم
    "use_inference_api": True,      # استفاده از Inference API
    "cache_results": True,          # Cache کردن نتایج
    "max_concurrent": 5,            # حداکثر درخواست همزمان
    "timeout": 30                   # Timeout (ثانیه)
}

# ===== کلاینت سراسری =====
hf_client = None

async def get_hf_client():
    """دریافت کلاینت HF (Singleton)"""
    global hf_client
    if hf_client is None:
        hf_client = HFInferenceAPIClient()
        await hf_client.__aenter__()
    return hf_client

# ===== توابع UI =====
async def analyze_text(text: str, analysis_type: str):
    """
    تحلیل متن با استفاده از HF Inference API
    """
    if not text:
        return "⚠️ لطفاً متنی وارد کنید"
    
    client = await get_hf_client()
    
    if analysis_type == "Crypto Sentiment":
        result = await client.analyze_sentiment(text, "crypto_sentiment")
    elif analysis_type == "Social Sentiment":
        result = await client.analyze_sentiment(text, "social_sentiment")
    elif analysis_type == "Financial Sentiment":
        result = await client.analyze_sentiment(text, "financial_sentiment")
    elif analysis_type == "Ensemble (All Models)":
        result = await client.ensemble_sentiment(text)
    else:
        return "❌ نوع تحلیل نامعتبر"
    
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
        
        if result.get("votes"):
            output += f"\n🗳️ **Votes**: {result['votes']}"
        
        return output.strip()
    
    elif result.get("status") == "loading":
        return "⏳ Model is loading, please try again in 20 seconds..."
    
    else:
        return f"❌ Error: {result.get('error', 'Unknown error')}"

# ===== ایجاد رابط Gradio =====
def create_optimized_interface():
    """
    ایجاد رابط بهینه شده برای HF Space
    """
    
    with gr.Blocks(
        title="Crypto AI Analyzer - Optimized for HF Space",
        theme=gr.themes.Soft()
    ) as demo:
        
        gr.Markdown("""
        # 🤖 Crypto AI Analyzer
        ### تحلیل هوش مصنوعی متن‌های کریپتو
        
        این نسخه بهینه شده برای Hugging Face Space است و از **Inference API** استفاده می‌کند.
        """)
        
        with gr.Tab("💬 Sentiment Analysis"):
            gr.Markdown("### تحلیل احساسات متن")
            
            text_input = gr.Textbox(
                label="متن خود را وارد کنید",
                placeholder="Bitcoin is showing strong bullish momentum...",
                lines=3
            )
            
            analysis_type = gr.Radio(
                choices=[
                    "Crypto Sentiment",
                    "Social Sentiment", 
                    "Financial Sentiment",
                    "Ensemble (All Models)"
                ],
                value="Ensemble (All Models)",
                label="نوع تحلیل"
            )
            
            analyze_btn = gr.Button("🔍 Analyze", variant="primary")
            output = gr.Markdown()
            
            analyze_btn.click(
                fn=analyze_text,
                inputs=[text_input, analysis_type],
                outputs=output
            )
        
        with gr.Tab("📊 Available Models"):
            gr.Markdown("""
            ### مدل‌های موجود
            
            | Model | Description | Provider |
            |-------|-------------|----------|
            | kk08/CryptoBERT | Crypto sentiment (binary) | HuggingFace |
            | ElKulako/cryptobert | Social crypto sentiment | HuggingFace |
            | ProsusAI/finbert | Financial sentiment | HuggingFace |
            | cardiffnlp/twitter-roberta | Twitter sentiment | HuggingFace |
            | OpenC/crypto-gpt-o3-mini | Crypto text generation | HuggingFace |
            
            **مزایا استفاده از Inference API:**
            - ✅ بدون نیاز به RAM زیاد
            - ✅ دسترسی به GPU رایگان
            - ✅ 30,000 درخواست رایگان در ماه
            - ✅ پردازش سریع‌تر
            """)
        
        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
            ### درباره این پروژه
            
            این ابزار از **Hugging Face Inference API** استفاده می‌کند تا:
            1. منابع RAM را حفظ کند
            2. سرعت پردازش را افزایش دهد
            3. به مدل‌های بزرگتر دسترسی داشته باشد
            4. در Hugging Face Space به خوبی کار کند
            
            **منابع:**
            - [Hugging Face Models](https://huggingface.co/models)
            - [Inference API Docs](https://huggingface.co/docs/api-inference)
            - [Free Datasets](https://huggingface.co/datasets)
            """)
    
    return demo

# ===== اجرا =====
if __name__ == "__main__":
    demo = create_optimized_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
```

---

### 4️⃣ **یکپارچه‌سازی با پروژه فعلی**

```python
# backend/services/ai_service_unified.py
"""
سرویس یکپارچه AI که از هر دو روش پشتیبانی می‌کند
"""

import os
from typing import Dict, Any, Optional
from ai_models import ensemble_crypto_sentiment as local_ensemble
from backend.services.hf_inference_api_client import HFInferenceAPIClient

class UnifiedAIService:
    """
    سرویس یکپارچه که بر اساس محیط، بهترین روش را انتخاب می‌کند
    """
    
    def __init__(self):
        self.is_hf_space = bool(os.getenv("SPACE_ID"))
        self.use_api = os.getenv("USE_HF_API", "true").lower() == "true"
        self.hf_client = None
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        تحلیل sentiment با انتخاب خودکار روش بهینه
        """
        # در HF Space یا با USE_HF_API=true، از API استفاده کن
        if self.is_hf_space or self.use_api:
            return await self._analyze_via_api(text)
        else:
            # در local، از مدل‌های بارگذاری شده استفاده کن
            return self._analyze_via_local(text)
    
    async def _analyze_via_api(self, text: str) -> Dict[str, Any]:
        """استفاده از HF Inference API"""
        if self.hf_client is None:
            self.hf_client = HFInferenceAPIClient()
            await self.hf_client.__aenter__()
        
        return await self.hf_client.ensemble_sentiment(text)
    
    def _analyze_via_local(self, text: str) -> Dict[str, Any]:
        """استفاده از مدل‌های local"""
        return local_ensemble(text)
    
    def get_service_info(self) -> Dict[str, Any]:
        """اطلاعات سرویس"""
        return {
            "is_hf_space": self.is_hf_space,
            "using_api": self.use_api,
            "mode": "HF Inference API" if (self.is_hf_space or self.use_api) else "Local Models"
        }
```

---

## 📦 **فایل‌های مورد نیاز برای HF Space**

### `requirements.txt` (بهینه شده)
```txt
# Core dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
gradio==4.8.0
aiohttp==3.9.1
python-dotenv==1.0.0

# HuggingFace (فقط برای API و Dataset)
huggingface-hub==0.19.4
datasets==2.15.0

# Data processing
pandas==2.1.3
numpy==1.26.2

# Optional: فقط اگر می‌خواهید مدل‌ها را local بارگذاری کنید
# transformers==4.35.2
# torch==2.1.1
```

### `README.md` (برای HF Space)
```markdown
---
title: Crypto AI Analyzer
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.8.0
app_file: hf_space_optimized_app.py
pinned: false
license: mit
---

# Crypto AI Analyzer

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

## Usage
Simply enter your text and select the analysis type!
```

---

## 🎯 **مزایای رویکرد پیشنهادی**

### مقایسه روش‌ها

| ویژگی | بارگذاری مستقیم | Inference API |
|-------|------------------|---------------|
| **مصرف RAM** | 1-4 GB | < 100 MB |
| **سرعت** | سریع (بعد از بارگذاری) | سریع (GPU در سرور HF) |
| **محدودیت** | RAM محدود در HF Space | 30K req/month رایگان |
| **دسترسی به مدل‌های بزرگ** | ❌ | ✅ |
| **نیاز به GPU** | ✅ (برای سرعت) | ❌ |
| **هزینه** | رایگان اما محدود | رایگان تا 30K |

---

## 🚀 **مراحل پیاده‌سازی**

### مرحله 1: ایجاد کلاینت API
```bash
# ایجاد فایل
touch backend/services/hf_inference_api_client.py

# کپی کردن کد بالا
```

### مرحله 2: تست کلاینت
```python
import asyncio
from backend.services.hf_inference_api_client import analyze_crypto_sentiment_via_api

async def test():
    text = "Bitcoin is showing strong bullish momentum!"
    result = await analyze_crypto_sentiment_via_api(text)
    print(result)

asyncio.run(test())
```

### مرحله 3: یکپارچه‌سازی با پروژه
```python
# در backend/routers/hf_inference.py
from fastapi import APIRouter
from backend.services.ai_service_unified import UnifiedAIService

router = APIRouter()
ai_service = UnifiedAIService()

@router.post("/api/ai/sentiment")
async def analyze_sentiment(text: str):
    return await ai_service.analyze_sentiment(text)
```

### مرحله 4: استقرار در HF Space
```bash
# 1. ایجاد Space جدید در huggingface.co
# 2. آپلود فایل‌ها:
#    - hf_space_optimized_app.py
#    - requirements.txt  
#    - README.md
# 3. تنظیم متغیرهای محیطی
#    HF_TOKEN=your_token
```

---

## 💰 **منابع رایگان اضافی**

با استفاده از این رویکرد، به منابع زیر دسترسی خواهید داشت:

### 1. **Inference API** (30,000 req/month)
```python
# استفاده رایگان از 1000+ مدل
- Sentiment analysis
- Text generation  
- Question answering
- Translation
- Summarization
```

### 2. **Datasets** (نامحدود)
```python
# دسترسی به 100,000+ dataset رایگان
- Historical crypto prices
- News articles
- Social media data
- Training data
```

### 3. **Spaces** (Free tier)
```python
# هاست رایگان برای اپلیکیشن
- 2 vCPU
- 16 GB RAM
- 50 GB Storage
- پشتیبانی از Gradio/Streamlit/Docker
```

### 4. **Models** (نامحدود)
```python
# استفاده از مدل‌های پیش‌آموزش داده شده
- 400,000+ مدل
- تمام open source
- بدون نیاز به training
```

---

## 📈 **نمونه استفاده واقعی**

```python
# مثال کامل: سیستم تحلیل خبر با AI

import asyncio
from backend.services.hf_inference_api_client import HFInferenceAPIClient
from backend.services.hf_dataset_loader import HFDatasetService

async def analyze_crypto_news():
    """
    سیستم کامل تحلیل خبر:
    1. دریافت داده تاریخی از Dataset
    2. تحلیل sentiment خبرها با AI
    3. ترکیب با قیمت‌ها
    """
    
    # 1. دریافت داده قیمت
    dataset_service = HFDatasetService()
    btc_data = await dataset_service.load_crypto_ohlcv("BTC", "1h", 100)
    print(f"✅ Loaded {len(btc_data)} price records")
    
    # 2. تحلیل sentiment
    async with HFInferenceAPIClient() as client:
        news_items = [
            "Bitcoin breaks all-time high!",
            "Major exchange hacked, millions lost",
            "Institutional adoption growing steadily"
        ]
        
        sentiments = []
        for news in news_items:
            result = await client.analyze_sentiment(news, "crypto_sentiment")
            sentiments.append({
                "news": news,
                "sentiment": result.get("label"),
                "confidence": result.get("confidence")
            })
        
        print(f"✅ Analyzed {len(sentiments)} news items")
    
    # 3. ترکیب و تحلیل
    return {
        "price_data": btc_data.to_dict(),
        "sentiment_analysis": sentiments,
        "summary": {
            "bullish_news": sum(1 for s in sentiments if s["sentiment"] == "bullish"),
            "bearish_news": sum(1 for s in sentiments if s["sentiment"] == "bearish"),
            "avg_confidence": sum(s["confidence"] for s in sentiments) / len(sentiments)
        }
    }

# اجرا
result = asyncio.run(analyze_crypto_news())
print(result["summary"])
```

---

## ✅ **خلاصه و توصیه‌ها**

### 🎯 **توصیه اصلی**
استفاده از **Hugging Face Inference API** به جای بارگذاری مستقیم مدل‌ها:

1. ✅ **صرفه‌جویی منابع**: بدون نیاز به RAM زیاد
2. ✅ **سرعت بیشتر**: GPU رایگان در سرورهای HF
3. ✅ **دسترسی بیشتر**: استفاده از مدل‌های بزرگتر
4. ✅ **رایگان**: 30,000 درخواست در ماه

### 📦 **منابع رایگان اضافی**
- Inference API: 30K req/month
- Datasets: نامحدود
- Spaces: هاست رایگان
- Models: 400K+ مدل

### 🚀 **مراحل بعدی**
1. ایجاد `hf_inference_api_client.py`
2. تست با چند نمونه
3. یکپارچه‌سازی با پروژه فعلی
4. استقرار در HF Space
5. استفاده از Dataset‌ها برای داده تاریخی

---

**با این رویکرد، به صورت کاملاً رایگان می‌توانید:**
- ✅ 30,000 تحلیل sentiment در ماه
- ✅ دسترسی به 100,000+ dataset
- ✅ هاست رایگان اپلیکیشن
- ✅ استفاده از 400,000+ مدل AI
