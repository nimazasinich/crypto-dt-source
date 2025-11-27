#!/usr/bin/env python3
"""
🚀 Crypto Monitor ULTIMATE - Launcher Script
اسکریپت راه‌انداز سریع برای سرور
"""

import os
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """بررسی وابستگی‌های لازم"""
    print("🔍 بررسی وابستگی‌ها...")

    required_packages = ["fastapi", "uvicorn", "aiohttp", "pydantic"]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"  ❌ {package} - نصب نشده")

    if missing:
        print(f"\n⚠️  {len(missing)} پکیج نصب نشده است!")
        response = input("آیا می‌خواهید الان نصب شوند? (y/n): ")
        if response.lower() == "y":
            install_dependencies()
        else:
            print("❌ بدون نصب وابستگی‌ها، سرور نمی‌تواند اجرا شود.")
            sys.exit(1)
    else:
        print("✅ همه وابستگی‌ها نصب شده‌اند\n")


def install_dependencies():
    """نصب وابستگی‌ها از requirements.txt"""
    print("\n📦 در حال نصب وابستگی‌ها...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ همه وابستگی‌ها با موفقیت نصب شدند\n")
    except subprocess.CalledProcessError:
        print("❌ خطا در نصب وابستگی‌ها")
        sys.exit(1)


def check_config_files():
    """بررسی فایل‌های پیکربندی"""
    print("🔍 بررسی فایل‌های پیکربندی...")

    config_file = Path("providers_config_extended.json")
    if not config_file.exists():
        print(f"  ❌ {config_file} یافت نشد!")
        print("     لطفاً این فایل را از مخزن دانلود کنید.")
        sys.exit(1)
    else:
        print(f"  ✅ {config_file}")

    dashboard_file = Path("unified_dashboard.html")
    if not dashboard_file.exists():
        print(f"  ⚠️  {dashboard_file} یافت نشد - داشبورد در دسترس نخواهد بود")
    else:
        print(f"  ✅ {dashboard_file}")

    print()


def show_banner():
    """نمایش بنر استارت"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        🚀  Crypto Monitor ULTIMATE  🚀                   ║
    ║                                                           ║
    ║   نسخه توسعه‌یافته با ۱۰۰+ ارائه‌دهنده API رایگان      ║
    ║   + سیستم پیشرفته Provider Pool Management              ║
    ║                                                           ║
    ║   Version: 2.0.0                                          ║
    ║   Author: Crypto Monitor Team                             ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def show_menu():
    """نمایش منوی انتخاب"""
    print("\n📋 انتخاب کنید:")
    print("  1️⃣  اجرای سرور (Production Mode)")
    print("  2️⃣  اجرای سرور (Development Mode - با Auto Reload)")
    print("  3️⃣  تست Provider Manager")
    print("  4️⃣  نمایش آمار ارائه‌دهندگان")
    print("  5️⃣  نصب/بروزرسانی وابستگی‌ها")
    print("  0️⃣  خروج")
    print()


def run_server_production():
    """اجرای سرور در حالت Production"""
    print("\n🚀 راه‌اندازی سرور در حالت Production...")
    print("📡 آدرس: http://localhost:8000")
    print("📊 داشبورد: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("\n⏸️  برای توقف سرور Ctrl+C را فشار دهید\n")

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "api_server_extended:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--log-level",
                "info",
            ]
        )
    except KeyboardInterrupt:
        print("\n\n🛑 سرور متوقف شد")


def run_server_development():
    """اجرای سرور در حالت Development"""
    print("\n🔧 راه‌اندازی سرور در حالت Development (Auto Reload)...")
    print("📡 آدرس: http://localhost:8000")
    print("📊 داشبورد: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("\n⏸️  برای توقف سرور Ctrl+C را فشار دهید")
    print("♻️  تغییرات فایل‌ها به‌طور خودکار اعمال می‌شود\n")

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "api_server_extended:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload",
                "--log-level",
                "debug",
            ]
        )
    except KeyboardInterrupt:
        print("\n\n🛑 سرور متوقف شد")


def test_provider_manager():
    """تست Provider Manager"""
    print("\n🧪 اجرای تست Provider Manager...\n")
    try:
        subprocess.run([sys.executable, "provider_manager.py"])
    except FileNotFoundError:
        print("❌ فایل provider_manager.py یافت نشد")
    except KeyboardInterrupt:
        print("\n\n🛑 تست متوقف شد")


def show_stats():
    """نمایش آمار ارائه‌دهندگان"""
    print("\n📊 نمایش آمار ارائه‌دهندگان...\n")
    try:
        from provider_manager import ProviderManager

        manager = ProviderManager()
        stats = manager.get_all_stats()

        summary = stats["summary"]
        print("=" * 60)
        print(f"📈 آمار کلی سیستم")
        print("=" * 60)
        print(f"  کل ارائه‌دهندگان:     {summary['total_providers']}")
        print(f"  آنلاین:              {summary['online']}")
        print(f"  آفلاین:              {summary['offline']}")
        print(f"  Degraded:            {summary['degraded']}")
        print(f"  کل درخواست‌ها:       {summary['total_requests']}")
        print(f"  درخواست‌های موفق:    {summary['successful_requests']}")
        print(f"  نرخ موفقیت:          {summary['overall_success_rate']:.2f}%")
        print("=" * 60)

        print(f"\n🔄 Pool‌های موجود: {len(stats['pools'])}")
        for pool_id, pool_data in stats["pools"].items():
            print(f"\n  📦 {pool_data['pool_name']}")
            print(f"     دسته: {pool_data['category']}")
            print(f"     استراتژی: {pool_data['rotation_strategy']}")
            print(f"     اعضا: {pool_data['total_providers']}")
            print(f"     در دسترس: {pool_data['available_providers']}")

        print("\n✅ برای جزئیات بیشتر، سرور را اجرا کرده و به داشبورد مراجعه کنید")

    except ImportError:
        print("❌ خطا: provider_manager.py یافت نشد یا وابستگی‌ها نصب نشده‌اند")
    except Exception as e:
        print(f"❌ خطا: {e}")


def main():
    """تابع اصلی"""
    show_banner()

    # بررسی وابستگی‌ها
    check_dependencies()

    # بررسی فایل‌های پیکربندی
    check_config_files()

    # حلقه منو
    while True:
        show_menu()
        choice = input("انتخاب شما: ").strip()

        if choice == "1":
            run_server_production()
            break
        elif choice == "2":
            run_server_development()
            break
        elif choice == "3":
            test_provider_manager()
            input("\n⏎ Enter را برای بازگشت به منو فشار دهید...")
        elif choice == "4":
            show_stats()
            input("\n⏎ Enter را برای بازگشت به منو فشار دهید...")
        elif choice == "5":
            install_dependencies()
            input("\n⏎ Enter را برای بازگشت به منو فشار دهید...")
        elif choice == "0":
            print("\n👋 خداحافظ!")
            sys.exit(0)
        else:
            print("\n❌ انتخاب نامعتبر! لطفاً دوباره تلاش کنید.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 برنامه متوقف شد")
        sys.exit(0)
