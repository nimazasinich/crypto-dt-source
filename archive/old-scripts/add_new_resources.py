#!/usr/bin/env python3
"""
اسکریپت اضافه کردن منابع جدید به سیستم
این اسکریپت منابع جدید را از فایل تحلیل خوانده و به فایل crypto_resources_unified اضافه می‌کند
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def load_new_resources():
    """بارگذاری منابع جدید از فایل تحلیل"""
    analysis_file = Path("new_resources_analysis.json")
    
    if not analysis_file.exists():
        print("❌ فایل تحلیل پیدا نشد. لطفاً ابتدا analyze_resources.py را اجرا کنید.")
        return []
    
    with open(analysis_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('new_resources', [])


def convert_to_unified_format(resource: Dict[str, Any]) -> Dict[str, Any]:
    """تبدیل فرمت منبع به فرمت یکپارچه سیستم"""
    
    # تعیین نوع احراز هویت
    auth_type = "none"
    api_key = None
    param_name = None
    
    if resource.get('key_required'):
        auth_type = "apiKeyQuery"
        param_name = "apiKey"
    
    # تعیین دسته
    category_mapping = {
        'Block Explorer': 'block_explorers',
        'Market Data': 'market_data_apis',
        'News': 'news_apis',
        'Sentiment': 'sentiment_apis',
        'On-Chain': 'onchain_analytics_apis',
        'Whale-Tracking': 'whale_tracking_apis',
        'Dataset': 'hf_resources'
    }
    
    category = category_mapping.get(resource.get('category'), 'free_http_endpoints')
    
    # ساخت ID یونیک
    name_clean = resource['name'].lower().replace(' ', '_').replace('(', '').replace(')', '')
    resource_id = f"new_{name_clean}_{category}"
    
    # ساخت شی منبع در فرمت یکپارچه
    unified_resource = {
        "id": resource_id,
        "name": resource['name'],
        "base_url": resource['url'],
        "auth": {
            "type": auth_type
        },
        "docs_url": None,
        "endpoints": {},
        "notes": resource.get('description', '') + f" | Rate Limit: {resource.get('rate_limit', 'Unknown')}"
    }
    
    if auth_type != "none":
        unified_resource["auth"]["key"] = api_key
        unified_resource["auth"]["param_name"] = param_name
    
    if resource.get('endpoint'):
        unified_resource["endpoints"]["main"] = resource['endpoint']
    
    # اضافه کردن به دسته مناسب
    if category == 'block_explorers':
        unified_resource["chain"] = "multi"
        unified_resource["role"] = "explorer"
    elif category == 'market_data_apis':
        unified_resource["role"] = "market_data"
    elif category == 'news_apis':
        unified_resource["role"] = "news"
    
    return {
        'category': category,
        'resource': unified_resource
    }


def add_resources_to_registry():
    """اضافه کردن منابع جدید به رجیستری"""
    print("=" * 80)
    print("🚀 اضافه کردن منابع جدید به رجیستری")
    print("=" * 80)
    
    # بارگذاری منابع جدید
    new_resources = load_new_resources()
    print(f"\n📦 تعداد منابع جدید: {len(new_resources)}")
    
    # بارگذاری رجیستری فعلی
    registry_file = Path("api-resources/crypto_resources_unified_2025-11-11.json")
    
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry_data = json.load(f)
    
    registry = registry_data.get('registry', {})
    
    # آمار اولیه
    initial_counts = {}
    for category in registry:
        if isinstance(registry[category], list):
            initial_counts[category] = len(registry[category])
    
    print(f"\n📊 آمار اولیه:")
    for cat, count in sorted(initial_counts.items()):
        print(f"   {cat}: {count} items")
    
    # اضافه کردن منابع جدید
    added_count = 0
    skipped_count = 0
    
    for new_res in new_resources:
        try:
            converted = convert_to_unified_format(new_res)
            category = converted['category']
            resource = converted['resource']
            
            # بررسی تکراری بودن
            if category not in registry:
                registry[category] = []
            
            # چک کردن URL تکراری
            existing_urls = [r.get('base_url', '') for r in registry[category] if isinstance(r, dict)]
            
            if resource['base_url'] in existing_urls:
                skipped_count += 1
                continue
            
            # اضافه کردن منبع
            registry[category].append(resource)
            added_count += 1
            
            print(f"✅ اضافه شد: {resource['name']} -> {category}")
            
        except Exception as e:
            print(f"⚠️ خطا در اضافه کردن {new_res.get('name')}: {e}")
            skipped_count += 1
    
    # بروزرسانی metadata
    metadata = registry.get('metadata', {})
    metadata['updated'] = datetime.now().strftime('%Y-%m-%d')
    metadata['total_entries'] = sum(len(v) for v in registry.values() if isinstance(v, list))
    metadata['last_update_note'] = f"Added {added_count} new resources"
    
    registry['metadata'] = metadata
    registry_data['registry'] = registry
    
    # ذخیره نسخه بکاپ
    backup_file = registry_file.parent / f"crypto_resources_unified_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(registry_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 نسخه بکاپ ذخیره شد: {backup_file}")
    
    # ذخیره رجیستری بهروزشده
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry_data, f, indent=2, ensure_ascii=False)
    
    # آمار نهایی
    final_counts = {}
    for category in registry:
        if isinstance(registry[category], list):
            final_counts[category] = len(registry[category])
    
    print(f"\n📊 آمار نهایی:")
    for cat in sorted(set(list(initial_counts.keys()) + list(final_counts.keys()))):
        initial = initial_counts.get(cat, 0)
        final = final_counts.get(cat, 0)
        diff = final - initial
        if diff > 0:
            print(f"   {cat}: {initial} -> {final} (+{diff})")
        else:
            print(f"   {cat}: {final}")
    
    print(f"\n✅ عملیات تکمیل شد!")
    print(f"   منابع اضافه شده: {added_count}")
    print(f"   منابع نادیده گرفته شده (تکراری): {skipped_count}")
    print(f"   مجموع منابع: {metadata['total_entries']}")


def main():
    """تابع اصلی"""
    print("\n🚀 شروع فرآیند اضافه کردن منابع جدید\n")
    
    try:
        add_resources_to_registry()
        print("\n✅ همه چیز با موفقیت انجام شد!")
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
