#!/usr/bin/env python3
"""
FastAPI Router for Unified AI Services
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging
import sys
import os

# اضافه کردن مسیر root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.services.ai_service_unified import get_unified_service, analyze_text
from backend.services.hf_dataset_loader import HFDatasetService, quick_price_data, quick_crypto_news

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI Services"])


# ===== Models =====

class SentimentRequest(BaseModel):
    """درخواست تحلیل sentiment"""
    text: str = Field(..., description="متن برای تحلیل", min_length=1, max_length=2000)
    category: str = Field("crypto", description="دسته‌بندی: crypto, financial, social")
    use_ensemble: bool = Field(True, description="استفاده از ensemble")


class BulkSentimentRequest(BaseModel):
    """درخواست تحلیل چند متن"""
    texts: List[str] = Field(..., description="لیست متن‌ها", min_items=1, max_items=50)
    category: str = Field("crypto", description="دسته‌بندی")
    use_ensemble: bool = Field(True, description="استفاده از ensemble")


class PriceDataRequest(BaseModel):
    """درخواست داده قیمت"""
    symbol: str = Field("BTC", description="نماد کریپتو")
    days: int = Field(7, description="تعداد روز", ge=1, le=90)
    timeframe: str = Field("1h", description="بازه زمانی")


# ===== Endpoints =====

@router.get("/health")
async def health_check():
    """
    بررسی وضعیت سلامت سرویس AI
    """
    try:
        service = await get_unified_service()
        health = service.get_health_status()
        
        return {
            "status": "ok",
            "service": "AI Unified",
            "health": health
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/info")
async def get_service_info():
    """
    دریافت اطلاعات سرویس
    """
    try:
        service = await get_unified_service()
        info = service.get_service_info()
        
        return {
            "status": "ok",
            "info": info
        }
    except Exception as e:
        logger.error(f"Failed to get service info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment")
async def analyze_sentiment(request: SentimentRequest):
    """
    تحلیل sentiment یک متن
    
    ### مثال:
    ```json
    {
        "text": "Bitcoin is showing strong bullish momentum!",
        "category": "crypto",
        "use_ensemble": true
    }
    ```
    
    ### پاسخ:
    ```json
    {
        "status": "success",
        "label": "bullish",
        "confidence": 0.85,
        "engine": "hf_inference_api_ensemble"
    }
    ```
    """
    try:
        result = await analyze_text(
            text=request.text,
            category=request.category,
            use_ensemble=request.use_ensemble
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment/bulk")
async def analyze_bulk_sentiment(request: BulkSentimentRequest):
    """
    تحلیل sentiment چند متن به صورت همزمان
    
    ### مثال:
    ```json
    {
        "texts": [
            "Bitcoin is pumping!",
            "Market is crashing",
            "Consolidation phase"
        ],
        "category": "crypto",
        "use_ensemble": true
    }
    ```
    """
    try:
        import asyncio
        
        # تحلیل موازی
        tasks = [
            analyze_text(text, request.category, request.use_ensemble)
            for text in request.texts
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # پردازش نتایج
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "text": request.texts[i],
                    "status": "error",
                    "error": str(result)
                })
            else:
                processed_results.append({
                    "text": request.texts[i],
                    **result
                })
        
        # خلاصه
        successful = sum(1 for r in processed_results if r.get("status") == "success")
        
        return {
            "status": "ok",
            "total": len(request.texts),
            "successful": successful,
            "failed": len(request.texts) - successful,
            "results": processed_results
        }
        
    except Exception as e:
        logger.error(f"Bulk sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment/quick")
async def quick_sentiment_analysis(
    text: str = Query(..., description="متن برای تحلیل", min_length=1),
    category: str = Query("crypto", description="دسته‌بندی")
):
    """
    تحلیل سریع sentiment (GET request)
    
    ### مثال:
    ```
    GET /api/ai/sentiment/quick?text=Bitcoin%20to%20the%20moon&category=crypto
    ```
    """
    try:
        result = await analyze_text(text=text, category=category, use_ensemble=False)
        return result
        
    except Exception as e:
        logger.error(f"Quick sentiment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/prices")
async def get_historical_prices(request: PriceDataRequest):
    """
    دریافت داده قیمت تاریخی از HuggingFace Datasets
    
    ### مثال:
    ```json
    {
        "symbol": "BTC",
        "days": 7,
        "timeframe": "1h"
    }
    ```
    """
    try:
        service = HFDatasetService()
        
        if not service.is_available():
            return {
                "status": "error",
                "error": "datasets library not available",
                "installation": "pip install datasets"
            }
        
        result = await service.get_historical_prices(
            symbol=request.symbol,
            days=request.days,
            timeframe=request.timeframe
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get historical prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/prices/quick/{symbol}")
async def quick_historical_prices(
    symbol: str,
    days: int = Query(7, ge=1, le=90)
):
    """
    دریافت سریع داده قیمت
    
    ### مثال:
    ```
    GET /api/ai/data/prices/quick/BTC?days=7
    ```
    """
    try:
        result = await quick_price_data(symbol=symbol.upper(), days=days)
        return result
        
    except Exception as e:
        logger.error(f"Quick price data failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/news")
async def get_crypto_news(
    limit: int = Query(10, ge=1, le=100, description="تعداد خبر")
):
    """
    دریافت اخبار کریپتو از HuggingFace Datasets
    
    ### مثال:
    ```
    GET /api/ai/data/news?limit=10
    ```
    """
    try:
        news = await quick_crypto_news(limit=limit)
        
        return {
            "status": "ok",
            "count": len(news),
            "news": news
        }
        
    except Exception as e:
        logger.error(f"Failed to get crypto news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/available")
async def get_available_datasets():
    """
    لیست Dataset‌های موجود
    """
    try:
        service = HFDatasetService()
        datasets = service.get_available_datasets()
        
        return {
            "status": "ok",
            "datasets": datasets
        }
        
    except Exception as e:
        logger.error(f"Failed to get datasets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/available")
async def get_available_models():
    """
    لیست مدل‌های AI موجود
    """
    try:
        from backend.services.hf_inference_api_client import HFInferenceAPIClient
        
        async with HFInferenceAPIClient() as client:
            models = client.get_available_models()
            
            return {
                "status": "ok",
                "models": models
            }
        
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_service_statistics():
    """
    آمار استفاده از سرویس
    """
    try:
        service = await get_unified_service()
        
        return {
            "status": "ok",
            "stats": service.stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== مثال استفاده در app.py =====
"""
# در فایل app.py یا production_server.py:

from backend.routers.ai_unified import router as ai_router

app = FastAPI()
app.include_router(ai_router)

# حالا endpoint‌های زیر در دسترس هستند:
# - POST /api/ai/sentiment
# - POST /api/ai/sentiment/bulk
# - GET  /api/ai/sentiment/quick
# - POST /api/ai/data/prices
# - GET  /api/ai/data/prices/quick/{symbol}
# - GET  /api/ai/data/news
# - GET  /api/ai/datasets/available
# - GET  /api/ai/models/available
# - GET  /api/ai/health
# - GET  /api/ai/info
# - GET  /api/ai/stats
"""
