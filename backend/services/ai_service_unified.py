#!/usr/bin/env python3
"""
Unified AI Service
سرویس یکپارچه AI که از هر دو روش پشتیبانی می‌کند:
1. Local model loading (ai_models.py)
2. HuggingFace Inference API (hf_inference_api_client.py)
"""

import os
import sys
from typing import Dict, Any, Optional
import logging
import asyncio

# اضافه کردن مسیر root به sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)

# Import local model manager
try:
    from ai_models import (
        ensemble_crypto_sentiment as local_ensemble,
        analyze_financial_sentiment as local_financial,
        analyze_social_sentiment as local_social,
        basic_sentiment_fallback,
        registry_status,
        get_model_health_registry,
        initialize_models
    )
    LOCAL_MODELS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Local models not available: {e}")
    LOCAL_MODELS_AVAILABLE = False

# Import HF Inference API client
try:
    from backend.services.hf_inference_api_client import HFInferenceAPIClient
    HF_API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"HF API client not available: {e}")
    HF_API_AVAILABLE = False


class UnifiedAIService:
    """
    سرویس یکپارچه AI که بر اساس محیط و تنظیمات، بهترین روش را انتخاب می‌کند
    
    حالت‌های کاری:
    1. HF_SPACE + USE_HF_API=true  → استفاده از Inference API (پیش‌فرض در HF Space)
    2. Local + USE_HF_API=false    → بارگذاری مستقیم مدل‌ها
    3. HF_SPACE + USE_HF_API=false → بارگذاری مستقیم (اگر RAM کافی باشد)
    4. Local + USE_HF_API=true     → استفاده از API (برای تست)
    """
    
    def __init__(self):
        # تشخیص محیط
        self.is_hf_space = bool(os.getenv("SPACE_ID"))
        self.use_api = os.getenv("USE_HF_API", "true" if self.is_hf_space else "false").lower() == "true"
        
        # کلاینت‌ها
        self.hf_client = None
        self.local_initialized = False
        
        # آمار
        self.stats = {
            "total_requests": 0,
            "api_requests": 0,
            "local_requests": 0,
            "fallback_requests": 0,
            "errors": 0
        }
        
        logger.info(f"UnifiedAIService initialized - Environment: {'HF Space' if self.is_hf_space else 'Local'}, Mode: {'API' if self.use_api else 'Local Models'}")
    
    async def initialize(self):
        """
        مقداردهی اولیه سرویس
        """
        # اگر از API استفاده می‌کنیم، کلاینت را آماده کن
        if self.use_api and HF_API_AVAILABLE:
            if self.hf_client is None:
                self.hf_client = HFInferenceAPIClient()
                await self.hf_client.__aenter__()
                logger.info("HF API client initialized")
        
        # اگر از local استفاده می‌کنیم، مدل‌ها را بارگذاری کن
        if not self.use_api and LOCAL_MODELS_AVAILABLE:
            if not self.local_initialized:
                result = initialize_models()
                self.local_initialized = True
                logger.info(f"Local models initialized: {result}")
    
    async def analyze_sentiment(
        self, 
        text: str,
        category: str = "crypto",
        use_ensemble: bool = True
    ) -> Dict[str, Any]:
        """
        تحلیل sentiment با انتخاب خودکار روش بهینه
        
        Args:
            text: متن برای تحلیل
            category: دسته‌بندی (crypto, financial, social)
            use_ensemble: استفاده از ensemble
        
        Returns:
            Dict شامل نتیجه تحلیل
        """
        self.stats["total_requests"] += 1
        
        # اگر متن خالی است
        if not text or len(text.strip()) == 0:
            return {
                "status": "error",
                "error": "Empty text",
                "label": "neutral",
                "confidence": 0.0
            }
        
        try:
            # انتخاب روش بر اساس تنظیمات
            if self.use_api and HF_API_AVAILABLE:
                result = await self._analyze_via_api(text, category, use_ensemble)
                self.stats["api_requests"] += 1
            elif LOCAL_MODELS_AVAILABLE:
                result = await self._analyze_via_local(text, category)
                self.stats["local_requests"] += 1
            else:
                # fallback به تحلیل لغوی
                result = self._fallback_analysis(text)
                self.stats["fallback_requests"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error in analyze_sentiment: {e}")
            self.stats["errors"] += 1
            
            # fallback در صورت خطا
            return self._fallback_analysis(text)
    
    async def _analyze_via_api(
        self, 
        text: str, 
        category: str,
        use_ensemble: bool
    ) -> Dict[str, Any]:
        """
        تحلیل با استفاده از HF Inference API
        """
        if self.hf_client is None:
            await self.initialize()
        
        try:
            if use_ensemble:
                # استفاده از ensemble
                models = self._get_models_for_category(category)
                result = await self.hf_client.ensemble_sentiment(text, models)
            else:
                # استفاده از تک مدل
                model_key = self._get_primary_model_for_category(category)
                result = await self.hf_client.analyze_sentiment(text, model_key)
            
            # اگر نتیجه موفق بود
            if result.get("status") == "success":
                return result
            
            # اگر مدل در حال بارگذاری است
            elif result.get("status") == "loading":
                # تلاش با مدل دیگر
                fallback_key = self._get_fallback_model(category)
                result = await self.hf_client.analyze_sentiment(text, fallback_key)
                
                if result.get("status") == "success":
                    result["used_fallback"] = True
                    return result
            
            # در غیر این صورت، fallback
            return self._fallback_analysis(text)
            
        except Exception as e:
            logger.error(f"API analysis failed: {e}")
            return self._fallback_analysis(text)
    
    async def _analyze_via_local(
        self, 
        text: str, 
        category: str
    ) -> Dict[str, Any]:
        """
        تحلیل با استفاده از مدل‌های local
        """
        if not self.local_initialized:
            await self.initialize()
        
        try:
            # انتخاب تابع بر اساس category
            if category == "crypto":
                result = local_ensemble(text)
            elif category == "financial":
                result = local_financial(text)
            elif category == "social":
                result = local_social(text)
            else:
                result = local_ensemble(text)
            
            # اطمینان از وجود فیلدهای مورد نیاز
            if not isinstance(result, dict):
                result = self._fallback_analysis(text)
            elif "label" not in result:
                result = self._fallback_analysis(text)
            
            return result
            
        except Exception as e:
            logger.error(f"Local analysis failed: {e}")
            return self._fallback_analysis(text)
    
    def _fallback_analysis(self, text: str) -> Dict[str, Any]:
        """
        تحلیل fallback (لغوی)
        """
        if LOCAL_MODELS_AVAILABLE:
            return basic_sentiment_fallback(text)
        else:
            # تحلیل ساده لغوی
            return self._simple_lexical_analysis(text)
    
    def _simple_lexical_analysis(self, text: str) -> Dict[str, Any]:
        """
        تحلیل لغوی ساده (برای زمانی که هیچ مدلی در دسترس نیست)
        """
        text_lower = text.lower()
        
        bullish_words = ["bullish", "rally", "surge", "pump", "moon", "buy", "up", "high", "gain", "profit"]
        bearish_words = ["bearish", "dump", "crash", "sell", "down", "low", "loss", "drop", "fall", "decline"]
        
        bullish_count = sum(1 for word in bullish_words if word in text_lower)
        bearish_count = sum(1 for word in bearish_words if word in text_lower)
        
        if bullish_count > bearish_count:
            label = "bullish"
            confidence = min(0.6 + (bullish_count - bearish_count) * 0.05, 0.9)
        elif bearish_count > bullish_count:
            label = "bearish"
            confidence = min(0.6 + (bearish_count - bullish_count) * 0.05, 0.9)
        else:
            label = "neutral"
            confidence = 0.5
        
        return {
            "status": "success",
            "label": label,
            "confidence": confidence,
            "score": confidence,
            "engine": "simple_lexical",
            "available": True
        }
    
    def _get_models_for_category(self, category: str) -> list:
        """
        دریافت لیست مدل‌ها بر اساس category
        """
        if category == "crypto":
            return ["crypto_sentiment", "social_sentiment"]
        elif category == "financial":
            return ["financial_sentiment", "fintwit_sentiment"]
        elif category == "social":
            return ["social_sentiment", "twitter_sentiment"]
        else:
            return ["crypto_sentiment", "financial_sentiment"]
    
    def _get_primary_model_for_category(self, category: str) -> str:
        """
        دریافت مدل اصلی بر اساس category
        """
        mapping = {
            "crypto": "crypto_sentiment",
            "financial": "financial_sentiment",
            "social": "social_sentiment",
            "twitter": "twitter_sentiment"
        }
        return mapping.get(category, "crypto_sentiment")
    
    def _get_fallback_model(self, category: str) -> str:
        """
        دریافت مدل fallback
        """
        if category == "crypto":
            return "twitter_sentiment"
        elif category == "financial":
            return "crypto_sentiment"
        else:
            return "crypto_sentiment"
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        اطلاعات سرویس
        """
        info = {
            "environment": "HF Space" if self.is_hf_space else "Local",
            "mode": "Inference API" if self.use_api else "Local Models",
            "hf_api_available": HF_API_AVAILABLE,
            "local_models_available": LOCAL_MODELS_AVAILABLE,
            "initialized": self.local_initialized or (self.hf_client is not None),
            "stats": self.stats.copy()
        }
        
        # اضافه کردن اطلاعات مدل‌های local
        if LOCAL_MODELS_AVAILABLE and not self.use_api:
            try:
                info["local_status"] = registry_status()
            except Exception as e:
                info["local_status_error"] = str(e)
        
        return info
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        وضعیت سلامت سرویس
        """
        health = {
            "status": "healthy",
            "checks": {
                "api_available": HF_API_AVAILABLE,
                "local_available": LOCAL_MODELS_AVAILABLE,
                "client_initialized": self.hf_client is not None,
                "local_initialized": self.local_initialized
            }
        }
        
        # بررسی وضعیت مدل‌های local
        if LOCAL_MODELS_AVAILABLE and not self.use_api:
            try:
                model_health = get_model_health_registry()
                health["model_health"] = {
                    "total_models": len(model_health),
                    "healthy": sum(1 for m in model_health if m.get("status") == "healthy"),
                    "degraded": sum(1 for m in model_health if m.get("status") == "degraded"),
                    "unavailable": sum(1 for m in model_health if m.get("status") == "unavailable")
                }
            except Exception as e:
                health["model_health_error"] = str(e)
        
        # تعیین وضعیت کلی
        if not HF_API_AVAILABLE and not LOCAL_MODELS_AVAILABLE:
            health["status"] = "degraded"
            health["warning"] = "No AI services available, using fallback"
        elif self.use_api and not HF_API_AVAILABLE:
            health["status"] = "degraded"
            health["warning"] = "API mode enabled but client not available"
        
        return health
    
    async def close(self):
        """
        بستن سرویس و آزادسازی منابع
        """
        if self.hf_client:
            await self.hf_client.__aexit__(None, None, None)
            self.hf_client = None
            logger.info("HF API client closed")


# ===== توابع کمکی سراسری =====

# سرویس سراسری (Singleton)
_unified_service = None

async def get_unified_service() -> UnifiedAIService:
    """
    دریافت سرویس یکپارچه (Singleton)
    """
    global _unified_service
    
    if _unified_service is None:
        _unified_service = UnifiedAIService()
        await _unified_service.initialize()
    
    return _unified_service


async def analyze_text(
    text: str,
    category: str = "crypto",
    use_ensemble: bool = True
) -> Dict[str, Any]:
    """
    تحلیل سریع متن
    
    Args:
        text: متن برای تحلیل
        category: دسته‌بندی
        use_ensemble: استفاده از ensemble
    
    Returns:
        Dict شامل نتیجه
    """
    service = await get_unified_service()
    return await service.analyze_sentiment(text, category, use_ensemble)


# ===== مثال استفاده =====
if __name__ == "__main__":
    async def test_service():
        """تست سرویس یکپارچه"""
        print("🧪 Testing Unified AI Service...")
        
        service = await get_unified_service()
        
        # نمایش اطلاعات سرویس
        print("\n1️⃣ Service Info:")
        info = service.get_service_info()
        print(f"   Environment: {info['environment']}")
        print(f"   Mode: {info['mode']}")
        print(f"   API Available: {info['hf_api_available']}")
        print(f"   Local Available: {info['local_models_available']}")
        
        # بررسی سلامت
        print("\n2️⃣ Health Status:")
        health = service.get_health_status()
        print(f"   Status: {health['status']}")
        print(f"   Checks: {health['checks']}")
        
        # تست تحلیل
        print("\n3️⃣ Sentiment Analysis Tests:")
        
        test_texts = [
            ("Bitcoin is showing strong bullish momentum!", "crypto"),
            ("Market crash incoming, sell everything!", "crypto"),
            ("Institutional investors are accumulating", "financial"),
        ]
        
        for text, category in test_texts:
            print(f"\n   Text: {text}")
            print(f"   Category: {category}")
            
            result = await service.analyze_sentiment(text, category, use_ensemble=True)
            
            if result.get("status") == "success":
                print(f"   ✅ Sentiment: {result['label']}")
                print(f"   📊 Confidence: {result['confidence']:.2%}")
                print(f"   🤖 Engine: {result.get('engine', 'unknown')}")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown')}")
        
        # نمایش آمار
        print("\n4️⃣ Service Statistics:")
        stats = service.stats
        print(f"   Total requests: {stats['total_requests']}")
        print(f"   API requests: {stats['api_requests']}")
        print(f"   Local requests: {stats['local_requests']}")
        print(f"   Fallback requests: {stats['fallback_requests']}")
        print(f"   Errors: {stats['errors']}")
        
        # بستن سرویس
        await service.close()
        
        print("\n✅ Testing complete!")
    
    import asyncio
    asyncio.run(test_service())
