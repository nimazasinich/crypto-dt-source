#!/usr/bin/env python3
"""
استخراج منابع استفاده نشده و ایجاد سیستم fallback سلسله‌مراتبی
Extract unused resources and create hierarchical fallback system
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

def load_json_resources():
    """بارگذاری فایل‌های JSON منابع"""
    base_path = Path(__file__).parent.parent / "api-resources"
    
    with open(base_path / "crypto_resources_unified_2025-11-11.json", 'r') as f:
        unified_resources = json.load(f)
    
    # فایل ultimate دارای یک خط اضافی در ابتدا است
    with open(base_path / "ultimate_crypto_pipeline_2025_NZasinich.json", 'r') as f:
        lines = f.readlines()
        # حذف خط اول (نام فایل) و parse JSON
        json_content = ''.join(lines[1:])
        ultimate_resources = json.loads(json_content)
    
    return unified_resources, ultimate_resources

def extract_all_resources(unified_data):
    """استخراج تمام منابع از فایل unified"""
    registry = unified_data['registry']
    
    all_resources = {
        'rpc_nodes': registry.get('rpc_nodes', []),
        'block_explorers': registry.get('block_explorers', []),
        'market_data_apis': registry.get('market_data_apis', []),
        'news_apis': registry.get('news_apis', []),
        'sentiment_apis': registry.get('sentiment_apis', []),
        'onchain_analytics_apis': registry.get('onchain_analytics_apis', []),
        'whale_tracking_apis': registry.get('whale_tracking_apis', []),
        'hf_resources': registry.get('hf_resources', []),
        'cors_proxies': registry.get('cors_proxies', []),
    }
    
    return all_resources

def extract_used_resources_from_project():
    """استخراج منابع استفاده شده در پروژه"""
    used_urls = set()
    used_names = set()
    used_models = set()
    
    # بررسی فایل‌های مختلف
    files_to_check = [
        'backend/services/hierarchical_fallback_config.py',
        'ai_models.py',
        'collectors/market_data.py',
        'collectors/news.py',
        'collectors/sentiment.py',
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                
                # استخراج URLها
                if 'api.coingecko.com' in content:
                    used_names.add('CoinGecko')
                if 'api.binance.com' in content:
                    used_names.add('Binance')
                if 'pro-api.coinmarketcap.com' in content:
                    used_names.add('CoinMarketCap')
                if 'api.etherscan.io' in content:
                    used_names.add('Etherscan')
                if 'api.bscscan.com' in content:
                    used_names.add('BscScan')
                if 'tronscan' in content.lower():
                    used_names.add('TronScan')
                if 'alternative.me' in content:
                    used_names.add('Alternative.me')
                if 'cryptopanic' in content.lower():
                    used_names.add('CryptoPanic')
                
                # استخراج مدل‌های HuggingFace
                if 'cardiffnlp' in content:
                    used_models.add('cardiffnlp/twitter-roberta-base-sentiment-latest')
                if 'ProsusAI/finbert' in content:
                    used_models.add('ProsusAI/finbert')
                if 'ElKulako/cryptobert' in content:
                    used_models.add('ElKulako/cryptobert')
    
    return {
        'urls': used_urls,
        'names': used_names,
        'models': used_models
    }

def categorize_unused_resources(all_resources, used_data):
    """دسته‌بندی منابع استفاده نشده"""
    unused = {}
    
    for category, resources in all_resources.items():
        unused[category] = []
        
        for resource in resources:
            name = resource.get('name', '')
            base_url = resource.get('base_url', '')
            
            # بررسی اینکه آیا استفاده شده یا نه
            is_used = False
            for used_name in used_data['names']:
                if used_name.lower() in name.lower():
                    is_used = True
                    break
            
            if not is_used:
                unused[category].append(resource)
    
    return unused

def main():
    """تابع اصلی"""
    print("=" * 80)
    print("🔍 استخراج منابع استفاده نشده")
    print("=" * 80)
    print()
    
    # بارگذاری منابع
    print("📥 بارگذاری فایل‌های JSON...")
    unified_data, ultimate_data = load_json_resources()
    
    # استخراج تمام منابع
    print("📊 استخراج تمام منابع...")
    all_resources = extract_all_resources(unified_data)
    
    # بررسی منابع استفاده شده
    print("🔎 بررسی منابع استفاده شده در پروژه...")
    used_data = extract_used_resources_from_project()
    
    print(f"\n✅ منابع استفاده شده:")
    print(f"  - Names: {len(used_data['names'])}")
    print(f"  - Models: {len(used_data['models'])}")
    
    for name in sorted(used_data['names']):
        print(f"    ✓ {name}")
    
    # دسته‌بندی استفاده نشده
    print("\n🔍 دسته‌بندی منابع استفاده نشده...")
    unused_resources = categorize_unused_resources(all_resources, used_data)
    
    # نمایش خلاصه
    print("\n📊 خلاصه منابع استفاده نشده:\n")
    
    total_unused = 0
    for category, resources in unused_resources.items():
        if resources:
            print(f"  {category}: {len(resources)} منبع")
            total_unused += len(resources)
    
    print(f"\n  📈 جمع کل: {total_unused} منبع استفاده نشده")
    
    # ذخیره نتایج
    output_path = Path(__file__).parent.parent / "data" / "unused_resources.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        'summary': {
            'total_unused': total_unused,
            'used_services': list(used_data['names']),
            'used_models': list(used_data['models']),
            'categories': {k: len(v) for k, v in unused_resources.items() if v}
        },
        'unused_by_category': unused_resources,
        'all_resources_count': sum(len(v) for v in all_resources.values())
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 نتایج ذخیره شد در: {output_path}")
    
    # ایجاد فایل گزارش
    report_path = Path(__file__).parent.parent / "UNUSED_RESOURCES_REPORT.md"
    create_report(output_data, report_path, all_resources)
    
    print(f"📄 گزارش کامل: {report_path}")
    print("\n✅ اتمام!")

def create_report(data, report_path, all_resources):
    """ایجاد گزارش Markdown"""
    with open(report_path, 'w') as f:
        f.write("# 📊 گزارش منابع استفاده نشده\n\n")
        f.write(f"**تاریخ:** {time.strftime('%Y-%m-%d')}\n\n")
        
        f.write("## 📋 خلاصه\n\n")
        f.write(f"- **منابع کل:** {data['all_resources_count']}\n")
        f.write(f"- **استفاده شده:** {len(data['summary']['used_services'])} سرویس + {len(data['summary']['used_models'])} مدل\n")
        f.write(f"- **استفاده نشده:** {data['summary']['total_unused']}\n\n")
        
        f.write("## ✅ منابع استفاده شده\n\n")
        for name in sorted(data['summary']['used_services']):
            f.write(f"- ✓ {name}\n")
        
        f.write("\n## 🤖 مدل‌های استفاده شده\n\n")
        for model in sorted(data['summary']['used_models']):
            f.write(f"- ✓ {model}\n")
        
        f.write("\n## 📊 منابع استفاده نشده به تفکیک دسته\n\n")
        
        for category, count in data['summary']['categories'].items():
            if count > 0:
                f.write(f"\n### {category} ({count} منبع)\n\n")
                
                resources = data['unused_by_category'].get(category, [])
                for resource in resources[:10]:  # نمایش 10 اولی
                    name = resource.get('name', 'Unknown')
                    url = resource.get('base_url', '')
                    free = resource.get('auth', {}).get('type', 'none')
                    f.write(f"- **{name}**\n")
                    f.write(f"  - URL: `{url}`\n")
                    f.write(f"  - Auth: {free}\n")
                
                if len(resources) > 10:
                    f.write(f"\n*... و {len(resources) - 10} منبع دیگر*\n")
        
        f.write("\n## 💡 توصیه‌ها\n\n")
        f.write("1. اضافه کردن منابع رایگان به سیستم fallback\n")
        f.write("2. تست و validation منابع جدید\n")
        f.write("3. اولویت‌بندی براساس rate limit و قابلیت اعتماد\n")
        f.write("4. استفاده از CORS proxies برای منابع محدود\n")

if __name__ == '__main__':
    main()
