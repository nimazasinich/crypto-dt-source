#!/usr/bin/env python3
"""
Hugging Face Inference API Client
استفاده از API به جای بارگذاری مستقیم مدل‌ها
"""

import aiohttp
import os
from typing import Dict, List, Optional, Any
import asyncio
import logging
from collections import Counter

logger = logging.getLogger(__name__)


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
        self.api_token = api_token or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        self.base_url = "https://api-inference.huggingface.co/models"
        self.session = None
        
        # مدل‌های تأیید شده که در HF API کار می‌کنند
        self.verified_models = {
            "crypto_sentiment": "kk08/CryptoBERT",
            "social_sentiment": "ElKulako/cryptobert",
            "financial_sentiment": "ProsusAI/finbert",
            "twitter_sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "fintwit_sentiment": "StephanAkkerman/FinTwitBERT-sentiment",
            "crypto_gen": "OpenC/crypto-gpt-o3-mini",
            "crypto_trader": "agarkovv/CryptoTrader-LM",
        }
        
        # Cache برای نتایج (برای کاهش تعداد درخواست‌ها)
        self._cache = {}
        self._cache_ttl = 300  # 5 دقیقه
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_cache_key(self, text: str, model_key: str) -> str:
        """ایجاد کلید cache"""
        return f"{model_key}:{text[:100]}"
    
    def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """بررسی cache"""
        if cache_key in self._cache:
            cached_result, timestamp = self._cache[cache_key]
            if asyncio.get_event_loop().time() - timestamp < self._cache_ttl:
                return cached_result
            else:
                del self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, result: Dict[str, Any]):
        """ذخیره در cache"""
        self._cache[cache_key] = (result, asyncio.get_event_loop().time())
    
    async def analyze_sentiment(
        self, 
        text: str, 
        model_key: str = "crypto_sentiment",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        تحلیل sentiment با استفاده از HF Inference API
        
        Args:
            text: متن برای تحلیل
            model_key: کلید مدل (crypto_sentiment, social_sentiment, ...)
            use_cache: استفاده از cache
        
        Returns:
            Dict شامل label, confidence, و اطلاعات دیگر
        """
        # بررسی cache
        if use_cache:
            cache_key = self._get_cache_key(text, model_key)
            cached = self._check_cache(cache_key)
            if cached:
                cached["from_cache"] = True
                return cached
        
        model_id = self.verified_models.get(model_key)
        if not model_id:
            return {
                "status": "error",
                "error": f"Unknown model key: {model_key}. Available: {list(self.verified_models.keys())}"
            }
        
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
                        "message": "Model is loading, please retry in 20 seconds",
                        "model": model_id
                    }
                
                if response.status == 429:
                    # محدودیت rate limit
                    return {
                        "status": "rate_limited",
                        "error": "Rate limit exceeded. Please try again later.",
                        "model": model_id
                    }
                
                if response.status == 401:
                    return {
                        "status": "error",
                        "error": "Authentication required. Please set HF_TOKEN environment variable.",
                        "model": model_id
                    }
                
                if response.status == 200:
                    data = await response.json()
                    
                    # استخراج نتیجه
                    if isinstance(data, list) and len(data) > 0:
                        if isinstance(data[0], list):
                            # برخی مدل‌ها لیستی از لیست‌ها برمی‌گردانند
                            result = data[0][0] if data[0] else {}
                        else:
                            result = data[0]
                        
                        # استانداردسازی خروجی
                        label = result.get("label", "NEUTRAL").upper()
                        score = result.get("score", 0.5)
                        
                        # تبدیل به فرمت استاندارد
                        mapped = self._map_label(label)
                        
                        response_data = {
                            "status": "success",
                            "label": mapped,
                            "confidence": score,
                            "score": score,
                            "raw_label": label,
                            "model": model_id,
                            "model_key": model_key,
                            "engine": "hf_inference_api",
                            "available": True,
                            "from_cache": False
                        }
                        
                        # ذخیره در cache
                        if use_cache:
                            cache_key = self._get_cache_key(text, model_key)
                            self._set_cache(cache_key, response_data)
                        
                        return response_data
                
                error_text = await response.text()
                logger.warning(f"HF API error: HTTP {response.status}: {error_text[:200]}")
                
                return {
                    "status": "error",
                    "error": f"HTTP {response.status}: {error_text[:200]}",
                    "model": model_id
                }
                
        except asyncio.TimeoutError:
            logger.error(f"HF API timeout for model {model_id}")
            return {
                "status": "error",
                "error": "Request timeout after 30 seconds",
                "model": model_id
            }
        except Exception as e:
            logger.error(f"HF API exception for model {model_id}: {e}")
            return {
                "status": "error",
                "error": str(e)[:200],
                "model": model_id
            }
    
    def _map_label(self, label: str) -> str:
        """تبدیل برچسب‌های مختلف به فرمت استاندارد"""
        label_upper = label.upper()
        
        # Positive/Bullish mapping
        if any(x in label_upper for x in ["POSITIVE", "BULLISH", "LABEL_2", "BUY"]):
            return "bullish"
        
        # Negative/Bearish mapping
        elif any(x in label_upper for x in ["NEGATIVE", "BEARISH", "LABEL_0", "SELL"]):
            return "bearish"
        
        # Neutral/Hold mapping
        else:
            return "neutral"
    
    async def ensemble_sentiment(
        self, 
        text: str, 
        models: Optional[List[str]] = None,
        min_models: int = 2
    ) -> Dict[str, Any]:
        """
        استفاده از چندین مدل به صورت همزمان (ensemble)
        
        Args:
            text: متن برای تحلیل
            models: لیست کلیدهای مدل (None = استفاده از مدل‌های پیش‌فرض)
            min_models: حداقل تعداد مدل‌های موفق برای نتیجه معتبر
        
        Returns:
            Dict شامل نتیجه ensemble
        """
        if models is None:
            # مدل‌های پیش‌فرض برای ensemble
            models = ["crypto_sentiment", "social_sentiment", "financial_sentiment"]
        
        # فراخوانی موازی مدل‌ها
        tasks = [self.analyze_sentiment(text, model) for model in models]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # جمع‌آوری نتایج موفق
        successful_results = []
        failed_models = []
        loading_models = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_models.append({
                    "model": models[i],
                    "error": str(result)[:100]
                })
                continue
            
            if isinstance(result, dict):
                if result.get("status") == "success":
                    successful_results.append(result)
                elif result.get("status") == "loading":
                    loading_models.append(result.get("model"))
                else:
                    failed_models.append({
                        "model": models[i],
                        "error": result.get("error", "Unknown error")[:100]
                    })
        
        # اگر همه مدل‌ها در حال بارگذاری هستند
        if loading_models and not successful_results:
            return {
                "status": "loading",
                "message": f"{len(loading_models)} model(s) are loading",
                "loading_models": loading_models
            }
        
        # اگر تعداد مدل‌های موفق کمتر از حداقل باشد
        if len(successful_results) < min_models:
            return {
                "status": "insufficient_models",
                "error": f"Only {len(successful_results)} models succeeded (min: {min_models})",
                "successful": len(successful_results),
                "failed": len(failed_models),
                "failed_models": failed_models[:3],  # نمایش 3 خطای اول
                "fallback": True
            }
        
        # رای‌گیری بین نتایج
        labels = [r["label"] for r in successful_results]
        confidences = [r["confidence"] for r in successful_results]
        
        # شمارش آرا
        label_counts = Counter(labels)
        final_label = label_counts.most_common(1)[0][0]
        
        # محاسبه اعتماد وزنی
        # مدل‌هایی که با اکثریت موافق هستند، وزن بیشتری دارند
        weighted_confidence = sum(
            r["confidence"] for r in successful_results 
            if r["label"] == final_label
        ) / len([r for r in successful_results if r["label"] == final_label])
        
        # میانگین کل
        avg_confidence = sum(confidences) / len(confidences)
        
        # آماره‌های تفصیلی
        scores_breakdown = {
            "bullish": 0.0,
            "bearish": 0.0,
            "neutral": 0.0
        }
        
        for result in successful_results:
            label = result["label"]
            confidence = result["confidence"]
            scores_breakdown[label] += confidence
        
        # نرمال‌سازی
        total_score = sum(scores_breakdown.values())
        if total_score > 0:
            scores_breakdown = {
                k: v / total_score 
                for k, v in scores_breakdown.items()
            }
        
        return {
            "status": "success",
            "label": final_label,
            "confidence": weighted_confidence,
            "avg_confidence": avg_confidence,
            "score": weighted_confidence,
            "scores": scores_breakdown,
            "model_count": len(successful_results),
            "votes": dict(label_counts),
            "consensus": label_counts[final_label] / len(successful_results),
            "models_used": [r["model"] for r in successful_results],
            "engine": "hf_inference_api_ensemble",
            "available": True,
            "failed_count": len(failed_models),
            "failed_models": failed_models[:3] if failed_models else []
        }
    
    async def analyze_with_fallback(
        self, 
        text: str, 
        primary_model: str = "crypto_sentiment",
        fallback_models: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        تحلیل با fallback خودکار
        
        اگر مدل اصلی موفق نشد، از مدل‌های fallback استفاده می‌کند
        """
        if fallback_models is None:
            fallback_models = ["social_sentiment", "financial_sentiment", "twitter_sentiment"]
        
        # تلاش با مدل اصلی
        result = await self.analyze_sentiment(text, primary_model)
        
        if result.get("status") == "success":
            result["used_fallback"] = False
            return result
        
        # تلاش با مدل‌های fallback
        for fallback_model in fallback_models:
            result = await self.analyze_sentiment(text, fallback_model)
            
            if result.get("status") == "success":
                result["used_fallback"] = True
                result["fallback_model"] = fallback_model
                result["primary_model_failed"] = primary_model
                return result
        
        # همه مدل‌ها ناموفق بودند
        return {
            "status": "all_failed",
            "error": "All models failed",
            "primary_model": primary_model,
            "fallback_models": fallback_models
        }
    
    def get_available_models(self) -> Dict[str, Any]:
        """
        دریافت لیست مدل‌های موجود
        """
        return {
            "total": len(self.verified_models),
            "models": [
                {
                    "key": key,
                    "model_id": model_id,
                    "provider": "HuggingFace",
                    "type": "sentiment" if "sentiment" in key else ("generation" if "gen" in key else "trading")
                }
                for key, model_id in self.verified_models.items()
            ]
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        آمار cache
        """
        return {
            "cache_size": len(self._cache),
            "cache_ttl": self._cache_ttl
        }


# ===== توابع کمکی برای استفاده آسان =====

async def analyze_crypto_sentiment_via_api(
    text: str, 
    use_ensemble: bool = True
) -> Dict[str, Any]:
    """
    تحلیل sentiment کریپتو با استفاده از HF Inference API
    
    Args:
        text: متن برای تحلیل
        use_ensemble: استفاده از ensemble (چند مدل)
    
    Returns:
        Dict شامل نتیجه تحلیل
    """
    async with HFInferenceAPIClient() as client:
        if use_ensemble:
            return await client.ensemble_sentiment(text)
        else:
            return await client.analyze_sentiment(text, "crypto_sentiment")


async def quick_sentiment(text: str) -> str:
    """
    تحلیل سریع sentiment - فقط برچسب را برمی‌گرداند
    
    Args:
        text: متن برای تحلیل
    
    Returns:
        str: "bullish", "bearish", یا "neutral"
    """
    result = await analyze_crypto_sentiment_via_api(text, use_ensemble=False)
    return result.get("label", "neutral")


# ===== مثال استفاده =====
if __name__ == "__main__":
    async def test_client():
        """تست کلاینت"""
        print("🧪 Testing HF Inference API Client...")
        
        test_texts = [
            "Bitcoin is showing strong bullish momentum!",
            "Major exchange hacked, prices crashing",
            "Market consolidating, waiting for direction"
        ]
        
        async with HFInferenceAPIClient() as client:
            # تست تک مدل
            print("\n1️⃣ Single Model Test:")
            for text in test_texts:
                result = await client.analyze_sentiment(text, "crypto_sentiment")
                print(f"   Text: {text[:50]}...")
                print(f"   Result: {result.get('label')} ({result.get('confidence', 0):.2%})")
            
            # تست ensemble
            print("\n2️⃣ Ensemble Test:")
            text = "Bitcoin breaking new all-time highs!"
            result = await client.ensemble_sentiment(text)
            print(f"   Text: {text}")
            print(f"   Result: {result.get('label')} ({result.get('confidence', 0):.2%})")
            print(f"   Votes: {result.get('votes')}")
            print(f"   Models: {result.get('model_count')}")
            
            # تست fallback
            print("\n3️⃣ Fallback Test:")
            result = await client.analyze_with_fallback(text)
            print(f"   Used fallback: {result.get('used_fallback', False)}")
            print(f"   Result: {result.get('label')} ({result.get('confidence', 0):.2%})")
            
            # لیست مدل‌ها
            print("\n4️⃣ Available Models:")
            models = client.get_available_models()
            for model in models["models"][:5]:
                print(f"   - {model['key']}: {model['model_id']}")
        
        print("\n✅ Testing complete!")
    
    import asyncio
    asyncio.run(test_client())
