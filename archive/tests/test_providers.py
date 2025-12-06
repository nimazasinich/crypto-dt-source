#!/usr/bin/env python3
"""
🧪 Test Script - تست سریع Provider Manager و Pool System
"""

import asyncio
import time
from provider_manager import ProviderManager, RotationStrategy
from datetime import datetime


async def test_basic_functionality():
    """تست عملکرد پایه"""
    print("\n" + "=" * 70)
    print("🧪 تست عملکرد پایه Provider Manager")
    print("=" * 70)
    
    # ایجاد مدیر
    print("\n📦 ایجاد Provider Manager...")
    manager = ProviderManager()
    
    print(f"✅ تعداد کل ارائه‌دهندگان: {len(manager.providers)}")
    print(f"✅ تعداد کل Pool‌ها: {len(manager.pools)}")
    
    # نمایش دسته‌بندی‌ها
    categories = {}
    for provider in manager.providers.values():
        categories[provider.category] = categories.get(provider.category, 0) + 1
    
    print("\n📊 دسته‌بندی ارائه‌دهندگان:")
    for category, count in sorted(categories.items()):
        print(f"  • {category}: {count} ارائه‌دهنده")
    
    return manager


async def test_health_checks(manager):
    """تست بررسی سلامت"""
    print("\n" + "=" * 70)
    print("🏥 تست بررسی سلامت ارائه‌دهندگان")
    print("=" * 70)
    
    print("\n⏳ در حال بررسی سلامت (ممکن است چند ثانیه طول بکشد)...")
    start_time = time.time()
    
    await manager.health_check_all()
    
    elapsed = time.time() - start_time
    print(f"✅ بررسی سلامت در {elapsed:.2f} ثانیه تکمیل شد")
    
    # آمار
    stats = manager.get_all_stats()
    summary = stats['summary']
    
    print(f"\n📊 نتایج:")
    print(f"  • آنلاین: {summary['online']} ارائه‌دهنده")
    print(f"  • آفلاین: {summary['offline']} ارائه‌دهنده")
    print(f"  • Degraded: {summary['degraded']} ارائه‌دهنده")
    
    # نمایش چند ارائه‌دهنده آنلاین
    print("\n✅ برخی از ارائه‌دهندگان آنلاین:")
    online_count = 0
    for provider_id, provider in manager.providers.items():
        if provider.status.value == "online" and online_count < 5:
            print(f"  • {provider.name} - {provider.avg_response_time:.0f}ms")
            online_count += 1
    
    # نمایش چند ارائه‌دهنده آفلاین
    offline_providers = [p for p in manager.providers.values() if p.status.value == "offline"]
    if offline_providers:
        print(f"\n❌ ارائه‌دهندگان آفلاین ({len(offline_providers)}):")
        for provider in offline_providers[:5]:
            error_msg = provider.last_error or "No error message"
            print(f"  • {provider.name} - {error_msg[:50]}")


async def test_pool_rotation(manager):
    """تست چرخش Pool"""
    print("\n" + "=" * 70)
    print("🔄 تست چرخش Pool")
    print("=" * 70)
    
    # انتخاب یک Pool
    if not manager.pools:
        print("⚠️  هیچ Pool‌ای یافت نشد")
        return
    
    pool_id = list(manager.pools.keys())[0]
    pool = manager.pools[pool_id]
    
    print(f"\n📦 Pool انتخاب شده: {pool.pool_name}")
    print(f"   دسته: {pool.category}")
    print(f"   استراتژی: {pool.rotation_strategy.value}")
    print(f"   تعداد اعضا: {len(pool.providers)}")
    
    if not pool.providers:
        print("⚠️  Pool خالی است")
        return
    
    print(f"\n🔄 تست {pool.rotation_strategy.value} strategy:")
    
    for i in range(5):
        provider = pool.get_next_provider()
        if provider:
            print(f"  Round {i+1}: {provider.name} (priority={provider.priority}, weight={provider.weight})")
        else:
            print(f"  Round {i+1}: هیچ ارائه‌دهنده‌ای در دسترس نیست")


async def test_failover(manager):
    """تست سیستم Failover"""
    print("\n" + "=" * 70)
    print("🛡️ تست سیستم Failover و Circuit Breaker")
    print("=" * 70)
    
    # پیدا کردن یک ارائه‌دهنده آنلاین
    online_provider = None
    for provider in manager.providers.values():
        if provider.is_available:
            online_provider = provider
            break
    
    if not online_provider:
        print("⚠️  هیچ ارائه‌دهنده آنلاین یافت نشد")
        return
    
    print(f"\n🎯 ارائه‌دهنده انتخابی: {online_provider.name}")
    print(f"   وضعیت اولیه: {online_provider.status.value}")
    print(f"   خطاهای متوالی: {online_provider.consecutive_failures}")
    print(f"   Circuit Breaker: {'باز' if online_provider.circuit_breaker_open else 'بسته'}")
    
    print("\n⚠️  شبیه‌سازی خطا...")
    # شبیه‌سازی چند خطای متوالی
    for i in range(6):
        online_provider.record_failure(f"Simulated error {i+1}")
        print(f"   خطای {i+1} ثبت شد - خطاهای متوالی: {online_provider.consecutive_failures}")
        
        if online_provider.circuit_breaker_open:
            print(f"   🛡️ Circuit Breaker باز شد!")
            break
    
    print(f"\n📊 وضعیت نهایی:")
    print(f"   وضعیت: {online_provider.status.value}")
    print(f"   در دسترس: {'خیر' if not online_provider.is_available else 'بله'}")
    print(f"   Circuit Breaker: {'باز' if online_provider.circuit_breaker_open else 'بسته'}")


async def test_statistics(manager):
    """تست سیستم آمارگیری"""
    print("\n" + "=" * 70)
    print("📊 تست سیستم آمارگیری")
    print("=" * 70)
    
    stats = manager.get_all_stats()
    
    print("\n📈 آمار کلی:")
    summary = stats['summary']
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  • {key}: {value:.2f}")
        else:
            print(f"  • {key}: {value}")
    
    print("\n🔄 آمار Pool‌ها:")
    for pool_id, pool_stats in stats['pools'].items():
        print(f"\n  📦 {pool_stats['pool_name']}")
        print(f"     استراتژی: {pool_stats['rotation_strategy']}")
        print(f"     کل اعضا: {pool_stats['total_providers']}")
        print(f"     در دسترس: {pool_stats['available_providers']}")
        print(f"     کل چرخش‌ها: {pool_stats['total_rotations']}")
    
    # صادرکردن آمار
    filepath = f"test_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    manager.export_stats(filepath)
    print(f"\n💾 آمار در {filepath} ذخیره شد")


async def test_performance():
    """تست عملکرد"""
    print("\n" + "=" * 70)
    print("⚡ تست عملکرد")
    print("=" * 70)
    
    manager = ProviderManager()
    
    # تست سرعت دریافت از Pool
    pool = list(manager.pools.values())[0] if manager.pools else None
    
    if pool and pool.providers:
        print(f"\n🔄 تست سرعت چرخش Pool ({pool.pool_name})...")
        
        iterations = 1000
        start_time = time.time()
        
        for _ in range(iterations):
            provider = pool.get_next_provider()
        
        elapsed = time.time() - start_time
        rps = iterations / elapsed
        
        print(f"✅ {iterations} چرخش در {elapsed:.3f} ثانیه")
        print(f"⚡ سرعت: {rps:.0f} چرخش در ثانیه")
    
    await manager.close_session()


async def run_all_tests():
    """اجرای همه تست‌ها"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           🧪 Crypto Monitor - Test Suite 🧪              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    manager = await test_basic_functionality()
    
    await test_health_checks(manager)
    
    await test_pool_rotation(manager)
    
    await test_failover(manager)
    
    await test_statistics(manager)
    
    await test_performance()
    
    await manager.close_session()
    
    print("\n" + "=" * 70)
    print("✅ همه تست‌ها با موفقیت تکمیل شدند")
    print("=" * 70)
    print("\n💡 برای اجرای سرور:")
    print("   python api_server_extended.py")
    print("   یا")
    print("   python start_server.py")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\n⏸️  تست متوقف شد")
    except Exception as e:
        print(f"\n\n❌ خطا در اجرای تست: {e}")
        import traceback
        traceback.print_exc()

