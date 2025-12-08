#!/usr/bin/env python3
"""
اسکریپت اصلاح مدیریت Session در فایل‌های Python
این اسکریپت تمام موارد استفاده نادرست از db_manager.get_session() را پیدا و اصلاح می‌کند
"""

import re
import os
from pathlib import Path

def fix_session_usage_in_file(file_path):
    """
    اصلاح استفاده نادرست از session در یک فایل
    
    تبدیل:
        session = db_manager.get_session()
        try:
            # code
        finally:
            session.close()
    
    به:
        with db_manager.get_session() as session:
            # code
    """
    print(f"🔍 بررسی فایل: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # الگوی پیدا کردن session = db_manager.get_session()
    # و تبدیل آن به with statement
    
    # این یک کار پیچیده است و نیاز به تجزیه دقیق کد دارد
    # برای سادگی، فقط موارد ساده را اصلاح می‌کنیم
    
    # Pattern 1: ساده‌ترین حالت
    # session = db_manager.get_session()
    # ... کد ...
    # session.close()
    
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # اگر خط شامل session = db_manager.get_session() باشد
        if 'session = db_manager.get_session()' in line and 'with' not in line:
            # پیدا کردن indent
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            # جایگزینی با with statement
            fixed_lines.append(f"{indent_str}with db_manager.get_session() as session:")
            
            # افزودن یک سطح indent به خطوط بعدی تا session.close()
            i += 1
            added_extra_indent = False
            
            while i < len(lines):
                next_line = lines[i]
                
                # اگر خط session.close() بود، آن را حذف کن
                if 'session.close()' in next_line:
                    i += 1
                    break
                
                # اگر خط شامل کد است، یک سطح indent اضافه کن
                if next_line.strip() and not next_line.strip().startswith('#'):
                    # بررسی سطح indent
                    current_indent = len(next_line) - len(next_line.lstrip())
                    
                    if current_indent <= indent:
                        # به انتهای block رسیدیم
                        break
                    
                    if not added_extra_indent:
                        # اولین خط کد، indent اضافه کن
                        extra_indent = '    '
                        added_extra_indent = True
                    
                    # افزودن indent اضافی
                    fixed_lines.append(extra_indent + next_line)
                else:
                    # خط خالی یا کامنت، بدون تغییر
                    fixed_lines.append(next_line)
                
                i += 1
            
            continue
        
        fixed_lines.append(line)
        i += 1
    
    fixed_content = '\n'.join(fixed_lines)
    
    if fixed_content != original_content:
        # ذخیره فایل اصلاح شده
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"  ✅ نسخه پشتیبان ذخیره شد: {backup_path}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"  ✅ فایل اصلاح شد: {file_path}")
        return True
    else:
        print(f"  ⏭️  نیازی به تغییر نیست")
        return False


def find_and_fix_files():
    """پیدا کردن و اصلاح تمام فایل‌های با مشکل"""
    
    files_to_fix = [
        'api/pool_endpoints.py',
        'scripts/init_source_pools.py',
    ]
    
    fixed_count = 0
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_session_usage_in_file(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  فایل یافت نشد: {file_path}")
    
    print(f"\n📊 خلاصه: {fixed_count} فایل اصلاح شد")


if __name__ == '__main__':
    print("=" * 60)
    print("🔧 اصلاح مدیریت Session در فایل‌های Python")
    print("=" * 60)
    print()
    
    find_and_fix_files()
    
    print()
    print("✅ اتمام!")
