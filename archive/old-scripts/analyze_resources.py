#!/usr/bin/env python3
"""
اسکریپت آنالیز منابع
تحلیل و مقایسه منابع موجود و جدید
"""
import json
from pathlib import Path
from typing import Dict, List, Set, Any

def analyze_unified_resources():
    """آنالیز فایل crypto_resources_unified_2025-11-11.json"""
    print("=" * 80)
    print("📊 تحلیل منابع موجود (crypto_resources_unified_2025-11-11.json)")
    print("=" * 80)
    
    file_path = Path("api-resources/crypto_resources_unified_2025-11-11.json")
    
    if not file_path.exists():
        print(f"❌ فایل پیدا نشد: {file_path}")
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    registry = data.get('registry', {})
    metadata = registry.get('metadata', {})
    
    print(f"\n📝 Metadata:")
    print(f"   Version: {metadata.get('version')}")
    print(f"   Updated: {metadata.get('updated')}")
    print(f"   Total entries: {metadata.get('total_entries')}")
    print(f"   Local backend routes: {metadata.get('local_backend_routes_count')}")
    
    print(f"\n📦 دسته‌بندی منابع:")
    
    categories_count = {}
    all_ids = set()
    
    for key, value in registry.items():
        if isinstance(value, list) and key != 'metadata':
            count = len(value)
            categories_count[key] = count
            print(f"   {key}: {count} items")
            
            # جمع‌آوری IDها
            for item in value:
                if isinstance(item, dict) and 'id' in item:
                    all_ids.add(item['id'])
    
    print(f"\n✅ مجموع منابع یونیک: {len(all_ids)}")
    
    return {
        'all_ids': all_ids,
        'categories': categories_count,
        'metadata': metadata
    }


def analyze_ultimate_pipeline():
    """آنالیز فایل ultimate_crypto_pipeline_2025_NZasinich.json"""
    print("\n" + "=" * 80)
    print("📊 تحلیل منابع جدید (ultimate_crypto_pipeline_2025_NZasinich.json)")
    print("=" * 80)
    
    file_path = Path("api-resources/ultimate_crypto_pipeline_2025_NZasinich.json")
    
    if not file_path.exists():
        print(f"❌ فایل پیدا نشد: {file_path}")
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # خواندن محتوا و حذف خط اول اگر نام فایل باشد
        content = f.read()
        lines = content.split('\n')
        if lines and not lines[0].strip().startswith('{'):
            # حذف خط اول
            content = '\n'.join(lines[1:])
        data = json.loads(content)
    
    print(f"\n📝 Project Info:")
    print(f"   Project: {data.get('project')}")
    print(f"   User: {data.get('user', {}).get('handle')}")
    print(f"   Total sources: {data.get('total_sources')}")
    
    # استخراج منابع
    files = data.get('files', [])
    all_resources = []
    
    if files and isinstance(files, list) and len(files) > 0:
        content = files[0].get('content', {})
        resources = content.get('resources', [])
        all_resources = resources
    
    print(f"\n📦 تعداد منابع: {len(all_resources)}")
    
    # دسته‌بندی
    categories = {}
    names = set()
    urls = set()
    free_resources = []
    
    for r in all_resources:
        cat = r.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
        
        name = r.get('name', '').strip()
        url = r.get('url', '').strip()
        
        if name:
            names.add(name)
        if url:
            urls.add(url)
        
        if r.get('free', False):
            free_resources.append(r)
    
    print(f"\n📊 دسته‌بندی منابع:")
    for cat, count in sorted(categories.items()):
        print(f"   {cat}: {count} items")
    
    print(f"\n✅ نام‌های یونیک: {len(names)}")
    print(f"✅ URLهای یونیک: {len(urls)}")
    print(f"✅ منابع رایگان: {len(free_resources)}")
    
    return {
        'resources': all_resources,
        'names': names,
        'urls': urls,
        'categories': categories,
        'free_count': len(free_resources)
    }


def find_new_resources(unified_data, ultimate_data):
    """یافتن منابع جدید"""
    print("\n" + "=" * 80)
    print("🔍 یافتن منابع جدید")
    print("=" * 80)
    
    existing_ids = unified_data.get('all_ids', set())
    new_resources = ultimate_data.get('resources', [])
    
    # منابع جدید بر اساس نام و URL
    potential_new = []
    
    for resource in new_resources:
        name = resource.get('name', '').strip().lower()
        url = resource.get('url', '').strip()
        
        # چک کنیم آیا این منبع در سیستم فعلی وجود دارد؟
        is_new = True
        
        # فقط منابع رایگان را در نظر بگیریم
        if not resource.get('free', False):
            continue
        
        # اگر URL تکراری نیست
        if url:
            potential_new.append({
                'name': resource.get('name'),
                'category': resource.get('category'),
                'url': url,
                'free': resource.get('free'),
                'rate_limit': resource.get('rateLimit', 'Unknown'),
                'description': resource.get('desc', ''),
                'endpoint': resource.get('endpoint', ''),
                'key_required': bool(resource.get('key'))
            })
    
    print(f"\n✅ منابع بالقوه جدید (رایگان): {len(potential_new)}")
    
    # نمایش نمونه
    if potential_new:
        print(f"\n📋 نمونه منابع جدید (10 مورد اول):")
        for i, r in enumerate(potential_new[:10], 1):
            print(f"\n{i}. {r['name']}")
            print(f"   Category: {r['category']}")
            print(f"   URL: {r['url']}")
            print(f"   Free: {r['free']}")
            print(f"   Rate Limit: {r['rate_limit']}")
            if r['description']:
                print(f"   Description: {r['description']}")
    
    return potential_new


def main():
    """تابع اصلی"""
    print("\n🚀 شروع تحلیل منابع API\n")
    
    # آنالیز منابع موجود
    unified_data = analyze_unified_resources()
    
    # آنالیز منابع جدید
    ultimate_data = analyze_ultimate_pipeline()
    
    # یافتن منابع جدید
    new_resources = find_new_resources(unified_data, ultimate_data)
    
    # ذخیره نتایج
    output_file = Path("new_resources_analysis.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': 'Generated',
            'existing_count': len(unified_data.get('all_ids', set())),
            'potential_new_count': len(new_resources),
            'new_resources': new_resources
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n💾 نتایج ذخیره شد در: {output_file}")
    print(f"\n✅ تحلیل کامل شد!")
    print(f"   منابع موجود: {len(unified_data.get('all_ids', set()))}")
    print(f"   منابع بالقوه جدید: {len(new_resources)}")


if __name__ == "__main__":
    main()
