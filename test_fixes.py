#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify all fixes are working correctly
"""

import os
import sys
from pathlib import Path


def test_files_exist():
    """Test if required files exist"""
    print("[*] Testing file existence...")

    required_files = [
        "index.html",
        "static/css/main.css",
        "static/js/app.js",
        "static/js/trading-pairs-loader.js",
        "trading_pairs.txt",
        "ai_models.py",
        "api_server_extended.py",
        "config.py",
        "HF_SETUP_GUIDE.md",
        "CHANGES_SUMMARY_FA.md",
    ]

    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
            print(f"  [X] Missing: {file_path}")
        else:
            print(f"  [OK] Found: {file_path}")

    if missing:
        print(f"\n[FAIL] {len(missing)} files are missing!")
        return False
    else:
        print(f"\n[PASS] All {len(required_files)} required files exist!")
        return True


def test_trading_pairs():
    """Test trading pairs file"""
    print("\n[*] Testing trading pairs file...")

    try:
        with open("trading_pairs.txt", "r") as f:
            pairs = [line.strip() for line in f if line.strip()]

        print(f"  [OK] Found {len(pairs)} trading pairs")
        print(f"  First 5: {pairs[:5]}")

        if len(pairs) < 10:
            print("  [WARN] Warning: Less than 10 pairs found")
            return False

        return True
    except Exception as e:
        print(f"  [X] Error reading trading pairs: {e}")
        return False


def test_index_html_links():
    """Test index.html links"""
    print("\n[*] Testing index.html links...")

    try:
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()

        checks = {
            "Chart.js CDN": "chart.js" in content.lower(),
            "main.css": "/static/css/main.css" in content,
            "trading-pairs-loader.js": "/static/js/trading-pairs-loader.js" in content,
            "app.js": "/static/js/app.js" in content,
        }

        all_good = True
        for check_name, passed in checks.items():
            if passed:
                print(f"  [OK] {check_name} linked correctly")
            else:
                print(f"  [X] {check_name} NOT found")
                all_good = False

        # Check script load order
        loader_pos = content.find("trading-pairs-loader.js")
        app_pos = content.find('src="/static/js/app.js"')

        if loader_pos > 0 and app_pos > 0 and loader_pos < app_pos:
            print(f"  [OK] Scripts load in correct order")
        else:
            print(f"  [WARN] Warning: Script load order may be incorrect")
            all_good = False

        return all_good
    except Exception as e:
        print(f"  [X] Error reading index.html: {e}")
        return False


def test_ai_models_config():
    """Test AI models configuration"""
    print("\n[*] Testing AI models configuration...")

    try:
        # Import modules
        from ai_models import HF_MODE, TRANSFORMERS_AVAILABLE, MODEL_SPECS, LINKED_MODEL_IDS

        print(f"  HF_MODE: {HF_MODE}")
        print(f"  Transformers available: {TRANSFORMERS_AVAILABLE}")
        print(f"  Total model specs: {len(MODEL_SPECS)}")
        print(f"  Linked models: {len(LINKED_MODEL_IDS)}")

        # Check essential models
        essential_models = [
            "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "ProsusAI/finbert",
            "kk08/CryptoBERT",
        ]

        all_good = True
        for model_id in essential_models:
            if model_id in LINKED_MODEL_IDS:
                print(f"  [OK] Essential model linked: {model_id}")
            else:
                print(f"  [WARN] Essential model NOT linked: {model_id}")
                all_good = False

        return all_good
    except Exception as e:
        print(f"  [X] Error importing ai_models: {e}")
        return False


def test_environment_variables():
    """Test environment variables"""
    print("\n[*] Testing environment variables...")

    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    hf_mode = os.getenv("HF_MODE", "not set")

    print(f"  HF_TOKEN: {'[OK] Set' if hf_token else '[X] Not set'}")
    print(f"  HF_MODE: {hf_mode}")

    if not hf_token:
        print("  [WARN] Warning: HF_TOKEN not set - models may not load")
        print("  [INFO] Set it with: export HF_TOKEN='hf_your_token_here'")
        return False

    if hf_mode not in ["public", "auth"]:
        print(f"  [WARN] Warning: HF_MODE should be 'public' or 'auth', not '{hf_mode}'")
        return False

    print("  [OK] Environment variables configured correctly")
    return True


def test_app_js_functions():
    """Test app.js functions"""
    print("\n[*] Testing app.js functions...")

    try:
        with open("static/js/app.js", "r", encoding="utf-8") as f:
            content = f.read()

        required_functions = [
            "initTradingPairSelectors",
            "createCategoriesChart",
            "loadSentimentModels",
            "loadSentimentHistory",
            "analyzeAssetSentiment",
            "analyzeSentiment",
            "loadMarketData",
        ]

        all_good = True
        for func_name in required_functions:
            if f"function {func_name}" in content or f"{func_name}:" in content:
                print(f"  [OK] Function exists: {func_name}")
            else:
                print(f"  [X] Function NOT found: {func_name}")
                all_good = False

        # Check event listener for tradingPairsLoaded
        if "tradingPairsLoaded" in content:
            print(f"  [OK] Trading pairs event listener exists")
        else:
            print(f"  [X] Trading pairs event listener NOT found")
            all_good = False

        return all_good
    except Exception as e:
        print(f"  [X] Error reading app.js: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("[TEST] Testing All Fixes")
    print("=" * 60)

    tests = [
        ("File Existence", test_files_exist),
        ("Trading Pairs", test_trading_pairs),
        ("Index.html Links", test_index_html_links),
        ("AI Models Config", test_ai_models_config),
        ("Environment Variables", test_environment_variables),
        ("App.js Functions", test_app_js_functions),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n[X] {test_name} crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("[RESULTS] Test Results Summary")
    print("=" * 60)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "[PASS]" if passed_test else "[FAIL]"
        print(f"  {status} - {test_name}")

    print(f"\n{'='*60}")
    print(f"Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*60}")

    if passed == total:
        print("\n[SUCCESS] All tests passed! System is ready to use!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
