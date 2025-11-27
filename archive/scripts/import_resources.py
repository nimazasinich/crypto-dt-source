#!/usr/bin/env python3
"""
Import Resources Script - وارد کردن خودکار منابع از فایل‌های JSON موجود
"""

import json
from pathlib import Path
from resource_manager import ResourceManager


def import_all_resources():
    """وارد کردن همه منابع از فایل‌های JSON موجود"""
    print("🚀 شروع وارد کردن منابع...\n")

    manager = ResourceManager()

    # لیست فایل‌های JSON برای import
    json_files = [
        "api-resources/crypto_resources_unified_2025-11-11.json",
        "api-resources/ultimate_crypto_pipeline_2025_NZasinich.json",
        "providers_config_extended.json",
        "providers_config_ultimate.json",
    ]

    imported_count = 0

    for json_file in json_files:
        file_path = Path(json_file)
        if file_path.exists():
            print(f"📂 در حال پردازش: {json_file}")
            try:
                success = manager.import_from_json(str(file_path), merge=True)
                if success:
                    imported_count += 1
                    print(f"  ✅ موفق\n")
                else:
                    print(f"  ⚠️  خطا در import\n")
            except Exception as e:
                print(f"  ❌ خطا: {e}\n")
        else:
            print(f"  ⚠️  فایل یافت نشد: {json_file}\n")

    # ذخیره منابع
    if imported_count > 0:
        manager.save_resources()
        print(f"✅ {imported_count} فایل با موفقیت import شدند")

    # نمایش آمار
    stats = manager.get_statistics()
    print("\n📊 آمار نهایی:")
    print(f"  کل منابع: {stats['total_providers']}")
    print(f"  رایگان: {stats['by_free']['free']}")
    print(f"  پولی: {stats['by_free']['paid']}")
    print(f"  نیاز به Auth: {stats['by_auth']['requires_auth']}")

    print("\n📦 دسته‌بندی:")
    for category, count in sorted(stats["by_category"].items()):
        print(f"  • {category}: {count}")

    print("\n✅ اتمام")


if __name__ == "__main__":
    import_all_resources()
