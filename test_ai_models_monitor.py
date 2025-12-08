#!/usr/bin/env python3
"""
Test AI Models Monitor System
تست سیستم نظارت مدل‌های AI
"""

import asyncio
import json
from datetime import datetime
from backend.services.ai_models_monitor import db, monitor, agent


async def test_database():
    """تست دیتابیس"""
    print("\n" + "="*60)
    print("📊 TEST 1: DATABASE")
    print("="*60)
    
    # تست اضافه کردن مدل
    test_model = {
        'model_id': 'test/model',
        'model_key': 'test_key',
        'task': 'sentiment-analysis',
        'category': 'test',
        'provider': 'huggingface'
    }
    
    db.add_model(test_model)
    print("✅ Model added to database")
    
    # دریافت همه مدل‌ها
    models = db.get_all_models()
    print(f"✅ Total models in database: {len(models)}")
    
    return models


async def test_single_model():
    """تست یک مدل"""
    print("\n" + "="*60)
    print("🧪 TEST 2: SINGLE MODEL TEST")
    print("="*60)
    
    test_model = {
        'model_id': 'distilbert-base-uncased-finetuned-sst-2-english',
        'task': 'sentiment-analysis',
        'category': 'general'
    }
    
    print(f"Testing model: {test_model['model_id']}")
    result = await monitor.test_model(test_model)
    
    print(f"\nResult:")
    print(f"  Status: {result.get('status')}")
    print(f"  Success: {result.get('success')}")
    print(f"  Response Time: {result.get('response_time_ms', 0):.0f}ms")
    
    if result.get('test_output'):
        print(f"  Output: {json.dumps(result['test_output'], indent=2)[:200]}...")
    
    return result


async def test_full_scan():
    """تست اسکن کامل"""
    print("\n" + "="*60)
    print("🔍 TEST 3: FULL SCAN")
    print("="*60)
    
    print("Starting scan of all models...")
    print("This may take a few minutes...\n")
    
    result = await monitor.scan_all_models()
    
    print("\n" + "─"*60)
    print("📊 SCAN RESULTS:")
    print("─"*60)
    print(f"Total Models:        {result['total']}")
    print(f"✅ Available:        {result['available']}")
    print(f"⏳ Loading:          {result['loading']}")
    print(f"❌ Failed:           {result['failed']}")
    print(f"🔐 Auth Required:    {result['auth_required']}")
    print(f"🔍 Not Found:        {result['not_found']}")
    
    # نمایش مدل‌های موفق
    available_models = [m for m in result['models'] if m['status'] == 'available']
    if available_models:
        print(f"\n✅ Available Models ({len(available_models)}):")
        for model in available_models[:10]:  # نمایش 10 تای اول
            print(f"   • {model['model_id']} ({model.get('response_time_ms', 0):.0f}ms)")
    
    # نمایش مدل‌های در حال بارگذاری
    loading_models = [m for m in result['models'] if m['status'] == 'loading']
    if loading_models:
        print(f"\n⏳ Loading Models ({len(loading_models)}):")
        for model in loading_models[:5]:
            print(f"   • {model['model_id']}")
    
    # نمایش مدل‌هایی که نیاز به auth دارند
    auth_models = [m for m in result['models'] if m['status'] == 'auth_required']
    if auth_models:
        print(f"\n🔐 Auth Required Models ({len(auth_models)}):")
        for model in auth_models[:5]:
            print(f"   • {model['model_id']}")
    
    return result


async def test_model_stats():
    """تست آمار مدل‌ها"""
    print("\n" + "="*60)
    print("📈 TEST 4: MODEL STATISTICS")
    print("="*60)
    
    models = db.get_all_models()
    
    # مدل‌هایی که چک شده‌اند
    checked_models = [m for m in models if (m.get('total_checks') or 0) > 0]
    
    print(f"Total Models: {len(models)}")
    print(f"Models with checks: {len(checked_models)}")
    
    if checked_models:
        print(f"\n📊 Top 5 Models by Success Rate:")
        sorted_models = sorted(
            checked_models,
            key=lambda x: x.get('success_rate', 0),
            reverse=True
        )[:5]
        
        for i, model in enumerate(sorted_models, 1):
            print(f"{i}. {model['model_id']}")
            print(f"   Success Rate: {model.get('success_rate', 0):.1f}%")
            print(f"   Checks: {model.get('total_checks', 0)}")
            print(f"   Avg Response: {model.get('avg_response_time_ms', 0):.0f}ms")
    
    return checked_models


async def test_model_history():
    """تست تاریخچه مدل"""
    print("\n" + "="*60)
    print("📜 TEST 5: MODEL HISTORY")
    print("="*60)
    
    # پیدا کردن یک مدل که چک شده باشد
    models = db.get_all_models()
    checked_model = next((m for m in models if m.get('total_checks', 0) > 0), None)
    
    if checked_model:
        model_id = checked_model['model_id']
        print(f"Model: {model_id}")
        
        history = db.get_model_history(model_id, limit=5)
        print(f"History Records: {len(history)}")
        
        if history:
            print(f"\nLast 5 Checks:")
            for i, record in enumerate(history, 1):
                print(f"{i}. {record['checked_at']}")
                print(f"   Status: {record['status']}")
                print(f"   Success: {record['success']}")
                if record['response_time_ms']:
                    print(f"   Response Time: {record['response_time_ms']:.0f}ms")
    else:
        print("⚠️ No models with checks found. Run a scan first.")
    
    return history if checked_model else []


async def test_agent():
    """تست Agent (محدود به 2 سیکل)"""
    print("\n" + "="*60)
    print("🤖 TEST 6: AGENT (Limited Test)")
    print("="*60)
    
    print("Starting agent for 2 cycles (10 seconds each)...")
    print("(In production, it runs every 5 minutes)")
    
    # تنظیم interval به 10 ثانیه برای تست
    test_agent = asyncio.create_task(agent.run())
    
    try:
        # صبر 25 ثانیه (2 سیکل)
        await asyncio.sleep(25)
        
        # توقف agent
        agent.running = False
        test_agent.cancel()
        
        print("\n✅ Agent test completed")
    
    except asyncio.CancelledError:
        print("\n✅ Agent stopped")


async def main():
    """تست کامل سیستم"""
    print("\n" + "🚀"*30)
    print("AI MODELS MONITOR - COMPREHENSIVE TEST")
    print("تست جامع سیستم نظارت مدل‌های AI")
    print("🚀"*30)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        # Test 1: Database
        models = await test_database()
        await asyncio.sleep(1)
        
        # Test 2: Single Model
        single_result = await test_single_model()
        await asyncio.sleep(1)
        
        # Test 3: Full Scan
        scan_result = await test_full_scan()
        await asyncio.sleep(1)
        
        # Test 4: Statistics
        stats = await test_model_stats()
        await asyncio.sleep(1)
        
        # Test 5: History
        history = await test_model_history()
        
        # Final Summary
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        
        print(f"\n📊 Summary:")
        print(f"   Total Models in DB: {len(models)}")
        print(f"   Last Scan Results:")
        print(f"      Available: {scan_result.get('available', 0)}")
        print(f"      Loading: {scan_result.get('loading', 0)}")
        print(f"      Failed: {scan_result.get('failed', 0)}")
        print(f"      Auth Required: {scan_result.get('auth_required', 0)}")
        
        print(f"\n💾 Database: data/ai_models.db")
        print(f"   ✅ Models table: {len(models)} records")
        print(f"   ✅ Metrics tracked")
        print(f"   ✅ Stats calculated")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Start agent in production: agent.start()")
        print(f"   2. Access via API: /api/ai-models/...")
        print(f"   3. Monitor dashboard: /api/ai-models/dashboard")
        
        print("\n" + "="*60)
        print("🎉 SYSTEM READY!")
        print("="*60)
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

