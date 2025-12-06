#!/usr/bin/env python3
"""
Quick test script to verify server setup
"""
from pathlib import Path

print("=" * 70)
print("Checking Server Setup")
print("=" * 70)

# Check files
checks = {
    "Dashboard HTML": Path("static/pages/dashboard/index.html"),
    "Sidebar HTML": Path("static/shared/layouts/sidebar.html"),
    "Header HTML": Path("static/shared/layouts/header.html"),
    "Dashboard JS": Path("static/pages/dashboard/dashboard.js"),
    "Formatters JS": Path("static/shared/js/utils/formatters.js"),
    "API Client JS": Path("static/shared/js/core/api-client.js"),
    "Layout Manager JS": Path("static/shared/js/core/layout-manager.js"),
}

all_ok = True
for name, path in checks.items():
    exists = path.exists()
    status = "✓" if exists else "✗"
    print(f"{status} {name}: {path}")
    if not exists:
        all_ok = False

print("\n" + "=" * 70)
if all_ok:
    print("✓ All required files found!")
    print("\nYou can now run: python simple_server.py")
else:
    print("✗ Some files are missing!")
    print("Please check the file structure.")

