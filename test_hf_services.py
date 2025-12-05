#!/usr/bin/env python3
"""
اسکریپت تست جامع برای سرویس‌های Hugging Face
"""

import asyncio
import sys
import os

# اضافه کردن مسیر root
sys.path.insert(0, os.path.dirname(__file__))

from backend.services.hf_inference_api_client import HFInferenceAPIClient
from backend.services.hf_dataset_loader import HFDatasetService
from backend.services.ai_service_unified import UnifiedAIService


async def test_inference_api():
    """تست HF Inference API Client"""
    print("\n" + "="*60)
    print("🧪 Test 1: HF Inference API Client")
    print("="*60)
    
    async with HFInferenceAPIClient() as client:
        # تست تک مدل
        print("\n📝 Single Model Test:")
        text = "Bitcoin is breaking new all-time highs!"
        
        result = await client.analyze_sentiment(text, "crypto_sentiment")
        
        if result.get("status") == "success":
            print(f"   ✅ Text: {text}")
            print(f"   📊 Sentiment: {result['label']}")
            print(f"   🎯 Confidence: {result['confidence']:.2%}")
            print(f"   🤖 Model: {result['model']}")
        else:
            print(f"   ❌ Status: {result.get('status')}")
            print(f"   ⚠️  Message: {result.get('error', result.get('message', 'Unknown'))}")
        
        # تست ensemble
        print("\n🔄 Ensemble Test:")
        result = await client.ensemble_sentiment(text)
        
        if result.get("status") == "success":
            print(f"   ✅ Sentiment: {result['label']}")
            print(f"   🎯 Confidence: {result['confidence']:.2%}")
            print(f"   📊 Votes: {result.get('votes', {})}")
            print(f"   🤖 Models used: {result.get('model_count', 0)}")
        else:
            print(f"   ❌ Status: {result.get('status')}")
            print(f"   ⚠️  Error: {result.get('error', 'Unknown')}")
        
        # لیست مدل‌ها
        print("\n📋 Available Models:")
        models = client.get_available_models()
        for model in models["models"][:5]:
            print(f"   - {model['key']}: {model['model_id']}")
        print(f"   ... and {len(models['models']) - 5} more")


async def test_dataset_loader():
    """تست HF Dataset Loader"""
    print("\n" + "="*60)
    print("🧪 Test 2: HF Dataset Loader")
    print("="*60)
    
    service = HFDatasetService()
    
    # بررسی در دسترس بودن
    print(f"\n📦 Library available: {service.is_available()}")
    
    if not service.is_available():
        print("   ⚠️  Install with: pip install datasets")
        return
    
    # نمادهای پشتیبانی شده
    print("\n💰 Supported Symbols:")
    symbols = service.get_supported_symbols()
    print(f"   {', '.join(symbols[:15])}")
    if len(symbols) > 15:
        print(f"   ... and {len(symbols) - 15} more")
    
    # تست بارگذاری قیمت (با محدودیت کم)
    print("\n📈 Loading price data (limited)...")
    try:
        result = await service.get_historical_prices("BTC", days=1, timeframe="1h")
        
        if result["status"] == "success":
            print(f"   ✅ Symbol: {result['symbol']}")
            print(f"   📊 Records: {result['records']}")
            print(f"   💵 Latest price: ${result['latest_price']:,.2f}")
            print(f"   📈 Change: {result['price_change_pct']:+.2f}%")
        else:
            print(f"   ❌ Error: {result.get('error')}")
    except Exception as e:
        print(f"   ⚠️  Exception: {str(e)[:100]}")


async def test_unified_service():
    """تست Unified AI Service"""
    print("\n" + "="*60)
    print("🧪 Test 3: Unified AI Service")
    print("="*60)
    
    service = UnifiedAIService()
    await service.initialize()
    
    # اطلاعات سرویس
    print("\n📋 Service Info:")
    info = service.get_service_info()
    print(f"   Environment: {info['environment']}")
    print(f"   Mode: {info['mode']}")
    print(f"   API Available: {info['hf_api_available']}")
    print(f"   Local Available: {info['local_models_available']}")
    
    # وضعیت سلامت
    print("\n💚 Health Status:")
    health = service.get_health_status()
    print(f"   Status: {health['status']}")
    print(f"   Checks: {health['checks']}")
    
    # تست تحلیل
    print("\n💬 Sentiment Analysis:")
    
    test_cases = [
        "Bitcoin is pumping to the moon! 🚀",
        "Huge crash incoming, everyone panic selling",
        "Market is consolidating, waiting for direction"
    ]
    
    for text in test_cases:
        print(f"\n   Text: {text}")
        
        result = await service.analyze_sentiment(text, category="crypto", use_ensemble=True)
        
        if result.get("status") == "success":
            emoji = "📈" if result["label"] == "bullish" else ("📉" if result["label"] == "bearish" else "➡️")
            print(f"   {emoji} Sentiment: {result['label']}")
            print(f"   🎯 Confidence: {result['confidence']:.2%}")
            print(f"   🤖 Engine: {result.get('engine', 'unknown')}")
        else:
            print(f"   ❌ Status: {result.get('status', 'error')}")
    
    # آمار
    print("\n📊 Statistics:")
    stats = service.stats
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   API requests: {stats['api_requests']}")
    print(f"   Local requests: {stats['local_requests']}")
    print(f"   Fallback requests: {stats['fallback_requests']}")
    print(f"   Errors: {stats['errors']}")
    
    await service.close()


async def run_all_tests():
    """اجرای تمام تست‌ها"""
    print("\n" + "="*60)
    print("🚀 HuggingFace Services - Comprehensive Test Suite")
    print("="*60)
    
    try:
        # تست Inference API
        await test_inference_api()
    except Exception as e:
        print(f"\n❌ Test 1 failed: {e}")
    
    try:
        # تست Dataset Loader
        await test_dataset_loader()
    except Exception as e:
        print(f"\n❌ Test 2 failed: {e}")
    
    try:
        # تست Unified Service
        await test_unified_service()
    except Exception as e:
        print(f"\n❌ Test 3 failed: {e}")
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)


if __name__ == "__main__":
    # اجرای تست‌ها
    asyncio.run(run_all_tests())
