#!/usr/bin/env python3
"""
Fix absolute paths to relative paths in all HTML files
"""

import os
import re
from pathlib import Path

def fix_html_file(file_path):
    """Fix paths in a single HTML file"""
    print(f"Processing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace absolute paths with relative paths
    replacements = [
        (r'href="/static/assets/', r'href="../../assets/'),
        (r'href="/static/shared/css/', r'href="../../shared/css/'),
        (r'href="/static/shared/js/', r'href="../../shared/js/'),
        (r'src="/static/assets/', r'src="../../assets/'),
        (r'src="/static/shared/js/', r'src="../../shared/js/'),
        (r'href="/static/pages/dashboard/dashboard.css"', r'href="./dashboard.css"'),
        (r'src="/static/pages/dashboard/dashboard.js"', r'src="./dashboard.js"'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Fixed: {file_path}")
        return True
    else:
        print(f"  - No changes needed: {file_path}")
        return False

def main():
    """Main function to process all HTML files"""
    print("=" * 60)
    print("Fixing absolute paths to relative paths in HTML files")
    print("=" * 60)
    print()
    
    # Get the static/pages directory
    script_dir = Path(__file__).parent
    pages_dir = script_dir / 'static' / 'pages'
    
    if not pages_dir.exists():
        print(f"ERROR: Pages directory not found: {pages_dir}")
        return
    
    # Find all index.html files
    html_files = list(pages_dir.rglob('index.html'))
    
    print(f"Found {len(html_files)} HTML files to process")
    print()
    
    fixed_count = 0
    for html_file in html_files:
        if fix_html_file(html_file):
            fixed_count += 1
    
    print()
    print("=" * 60)
    print(f"Summary: Fixed {fixed_count} out of {len(html_files)} files")
    print("=" * 60)

if __name__ == '__main__':
    main()

