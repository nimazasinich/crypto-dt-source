#!/usr/bin/env python3
"""
تست اتصال به providers_config_extended.json
"""

import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

print("🧪 Testing Routing to providers_config_extended.json")
print("=" * 60)

# Test 1: Load providers config
print("\n1️⃣ Testing providers config loading...")
try:
    from hf_unified_server import PROVIDERS_CONFIG, PROVIDERS_CONFIG_PATH

    print(f"   ✅ Config path: {PROVIDERS_CONFIG_PATH}")
    print(f"   ✅ Config exists: {PROVIDERS_CONFIG_PATH.exists()}")
    print(f"   ✅ Providers loaded: {len(PROVIDERS_CONFIG)}")

    # Check for HuggingFace Space providers
    hf_providers = [p for p in PROVIDERS_CONFIG.keys() if "huggingface_space" in p]
    print(f"   ✅ HuggingFace Space providers: {len(hf_providers)}")
    for provider in hf_providers:
        print(f"      - {provider}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Test app import
print("\n2️⃣ Testing FastAPI app import...")
try:
    from hf_unified_server import app

    print(f"   ✅ App imported successfully")
    print(f"   ✅ App title: {app.title}")
    print(f"   ✅ App version: {app.version}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Test main.py routing
print("\n3️⃣ Testing main.py routing...")
try:
    from main import app as main_app

    print(f"   ✅ main.py imports successfully")
    print(f"   ✅ Routes loaded: {len(main_app.routes)}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Show HuggingFace Space provider details
print("\n4️⃣ HuggingFace Space Provider Details...")
try:
    for provider_id in hf_providers:
        provider_info = PROVIDERS_CONFIG[provider_id]
        print(f"\n   📦 {provider_id}:")
        print(f"      Name: {provider_info.get('name')}")
        print(f"      Category: {provider_info.get('category')}")
        print(f"      Base URL: {provider_info.get('base_url')}")
        print(f"      Endpoints: {len(provider_info.get('endpoints', {}))}")

        # Show first 5 endpoints
        endpoints = list(provider_info.get("endpoints", {}).items())[:5]
        print(f"      First 5 endpoints:")
        for key, path in endpoints:
            print(f"         - {key}: {path}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Routing Test Complete!")
print("\n💡 Next steps:")
print("   1. Start server: python -m uvicorn main:app --host 0.0.0.0 --port 7860")
print("   2. Test endpoint: curl http://localhost:7860/api/providers")
print("   3. Check docs: http://localhost:7860/docs")
