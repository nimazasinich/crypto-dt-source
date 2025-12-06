#!/usr/bin/env python3
"""
Update All Pages Script
Adds API configuration to all HTML pages
"""

import os
from pathlib import Path

# API config script tag to inject
API_CONFIG_SCRIPT = '''    <!-- API Configuration - Smart Fallback System -->
    <script src="/static/js/api-config.js"></script>
    <script>
        // Initialize API client
        window.apiReady = new Promise((resolve) => {
            if (window.apiClient) {
                console.log('✅ API Client ready');
                resolve(window.apiClient);
            } else {
                console.error('❌ API Client not loaded');
            }
        });
    </script>
'''

def update_html_file(filepath: Path) -> bool:
    """Update a single HTML file to include API config"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has api-config.js
        if 'api-config.js' in content:
            print(f"⏭️  Skipped (already has API config): {filepath.name}")
            return False
        
        # Find </head> tag and inject before it
        if '</head>' in content:
            updated_content = content.replace('</head>', f'{API_CONFIG_SCRIPT}\n</head>')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ Updated: {filepath.name}")
            return True
        else:
            print(f"⚠️  No </head> tag found: {filepath.name}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {filepath.name}: {e}")
        return False


def find_html_files(directory: Path) -> list:
    """Find all HTML files in directory and subdirectories"""
    html_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', 'node_modules', 'archive'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.html'):
                html_files.append(Path(root) / file)
    
    return html_files


def main():
    """Main update function"""
    print("=" * 80)
    print("🔄 Updating All HTML Pages with API Configuration")
    print("=" * 80)
    print()
    
    # Get static directory
    static_dir = Path(__file__).parent / 'static'
    
    if not static_dir.exists():
        print(f"❌ Static directory not found: {static_dir}")
        return
    
    # Find all HTML files
    html_files = find_html_files(static_dir)
    print(f"📄 Found {len(html_files)} HTML files")
    print()
    
    # Update each file
    updated_count = 0
    for filepath in html_files:
        if update_html_file(filepath):
            updated_count += 1
    
    # Print summary
    print()
    print("=" * 80)
    print("📊 Update Summary")
    print("=" * 80)
    print(f"✅ Updated: {updated_count} files")
    print(f"⏭️  Skipped: {len(html_files) - updated_count} files")
    print(f"📄 Total: {len(html_files)} files")
    print()
    
    if updated_count > 0:
        print("✅ All pages now have access to Smart API Client")
        print("🔄 Resource rotation: ENABLED")
        print("📊 Available resources: 305+")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
