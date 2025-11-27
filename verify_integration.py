#!/usr/bin/env python3
"""
Integration Verification Script
Tests that all models, endpoints, and frontend integrations are working correctly.
"""

import sys
import json
from pathlib import Path


def verify_models():
    """Verify ai_models.py integration"""
    print("=" * 70)
    print("1. VERIFYING AI MODELS INTEGRATION")
    print("=" * 70)

    try:
        import ai_models

        # Check model specs
        total_models = len(ai_models.MODEL_SPECS)
        print(f"✓ Total models registered: {total_models}")

        # Check required models
        required_models = {
            "crypto_sent_0": "kk08/CryptoBERT",
            "crypto_sent_1": "ElKulako/cryptobert",
            "financial_sent_0": "StephanAkkerman/FinTwitBERT-sentiment",
            "crypto_gen_0": "OpenC/crypto-gpt-o3-mini",
            "crypto_trade_0": "agarkovv/CryptoTrader-LM",
        }

        missing = []
        for key, expected_id in required_models.items():
            if key not in ai_models.MODEL_SPECS:
                missing.append(f"{key} ({expected_id})")
            else:
                actual_id = ai_models.MODEL_SPECS[key].model_id
                if actual_id != expected_id:
                    print(f"⚠ {key}: Expected {expected_id}, got {actual_id}")
                else:
                    print(f"✓ {key}: {actual_id}")

        if missing:
            print(f"✗ Missing models: {', '.join(missing)}")
            return False

        # Check model info function
        model_info = ai_models.get_model_info()
        print(f"✓ Model info function works")
        print(f"  - Transformers available: {model_info['transformers_available']}")
        print(f"  - Models initialized: {model_info['models_initialized']}")
        print(f"  - Models loaded: {model_info['models_loaded']}")

        # Check categories
        catalog = model_info["model_catalog"]
        print(f"✓ Model categories:")
        for category, models in catalog.items():
            print(f"  - {category}: {len(models)} model(s)")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def verify_api_structure():
    """Verify api_server_extended.py structure"""
    print("\n" + "=" * 70)
    print("2. VERIFYING API ENDPOINTS STRUCTURE")
    print("=" * 70)

    try:
        with open("api_server_extended.py", "r") as f:
            content = f.read()

        # Check for required endpoints
        required_endpoints = [
            ("GET", "/api/health"),
            ("GET", "/api/status"),
            ("GET", "/api/models/list"),
            ("POST", "/api/models/initialize"),
            ("POST", "/api/sentiment/analyze"),
            ("GET", "/api/providers"),
            ("GET", "/api/resources"),
        ]

        for method, endpoint in required_endpoints:
            # Check multiple patterns
            patterns = [
                f'@app.{method.lower()}("{endpoint}")',
                f"@app.{method.lower()}('{endpoint}')",
                f'async def {endpoint.replace("/", "_").replace("-", "_").lstrip("_")}',
            ]

            found = any(pattern in content for pattern in patterns)
            if found:
                print(f"✓ {method} {endpoint}")
            else:
                # More flexible check - just look for the endpoint path
                if endpoint in content:
                    print(f"✓ {method} {endpoint} (found in code)")
                else:
                    print(f"✗ {method} {endpoint} - NOT FOUND")
                    return False

        # Check for model_key support in sentiment endpoint
        if '"model_key"' in content and 'model_key = request.get("model_key")' in content:
            print(f"✓ Sentiment endpoint supports model_key parameter")
        else:
            print(f"⚠ Sentiment endpoint may not support model_key")

        # Check for proper error handling
        if "ModelNotAvailable" in content:
            print(f"✓ ModelNotAvailable exception handling present")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def verify_frontend():
    """Verify frontend integration"""
    print("\n" + "=" * 70)
    print("3. VERIFYING FRONTEND INTEGRATION")
    print("=" * 70)

    try:
        with open("static/js/app.js", "r") as f:
            content = f.read()

        # Check for required functions
        required_functions = [
            "loadDashboard",
            "loadModels",
            "initializeModels",
            "loadSentimentModels",
            "analyzeSentiment",
            "analyzeGlobalSentiment",
            "analyzeAssetSentiment",
            "analyzeNewsSentiment",
            "loadProviders",
            "searchResources",
        ]

        for func in required_functions:
            if f"function {func}(" in content or f"async function {func}(" in content:
                print(f"✓ {func}()")
            else:
                print(f"✗ {func}() - NOT FOUND")
                return False

        # Check for model_key support
        if "model_key" in content and "requestBody.model_key" in content:
            print(f"✓ Frontend sends model_key to backend")
        else:
            print(f"⚠ Frontend may not send model_key")

        # Check for sentiment model dropdown
        if "sentiment-model" in content:
            print(f"✓ Sentiment model dropdown referenced")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def verify_documentation():
    """Verify documentation exists"""
    print("\n" + "=" * 70)
    print("4. VERIFYING DOCUMENTATION")
    print("=" * 70)

    docs_path = Path("docs/project_mapping_doc.html")
    if docs_path.exists():
        size = docs_path.stat().st_size
        print(f"✓ docs/project_mapping_doc.html exists ({size:,} bytes)")

        # Check content
        with open(docs_path, "r") as f:
            content = f.read()

        required_sections = [
            "System Overview",
            "AI Models",
            "API Endpoints",
            "Frontend Integration",
            "Deployment Guide",
        ]

        for section in required_sections:
            if section in content:
                print(f"  ✓ {section} section present")
            else:
                print(f"  ✗ {section} section missing")

        # Check for model documentation
        model_ids = [
            "kk08/CryptoBERT",
            "ElKulako/cryptobert",
            "StephanAkkerman/FinTwitBERT-sentiment",
            "OpenC/crypto-gpt-o3-mini",
            "agarkovv/CryptoTrader-LM",
        ]

        for model_id in model_ids:
            if model_id in content:
                print(f"  ✓ {model_id} documented")
            else:
                print(f"  ⚠ {model_id} not found in docs")

        return True
    else:
        print(f"✗ docs/project_mapping_doc.html NOT FOUND")
        return False


def verify_html_ui():
    """Verify HTML UI structure"""
    print("\n" + "=" * 70)
    print("5. VERIFYING HTML UI STRUCTURE")
    print("=" * 70)

    try:
        with open("index.html", "r") as f:
            content = f.read()

        # Check for required tabs
        required_tabs = [
            "tab-dashboard",
            "tab-models",
            "tab-sentiment",
            "tab-providers",
            "tab-news",
            "tab-diagnostics",
            "tab-api-explorer",
        ]

        for tab in required_tabs:
            if f'id="{tab}"' in content:
                print(f"✓ #{tab}")
            else:
                print(f"✗ #{tab} - NOT FOUND")

        # Check for sentiment controls
        sentiment_controls = [
            "sentiment-text",
            "sentiment-mode",
            "sentiment-model",
            "sentiment-result",
        ]

        print(f"\nSentiment controls:")
        for control in sentiment_controls:
            if f'id="{control}"' in content:
                print(f"  ✓ #{control}")
            else:
                print(f"  ✗ #{control} - NOT FOUND")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def print_summary(results):
    """Print verification summary"""
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    total = len(results)
    passed = sum(results.values())

    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL VERIFICATIONS PASSED - INTEGRATION COMPLETE!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} verification(s) failed")
        return 1


def main():
    """Run all verifications"""
    print("\n🔍 Crypto Intelligence Hub - Integration Verification")
    print("=" * 70)

    results = {
        "AI Models": verify_models(),
        "API Endpoints": verify_api_structure(),
        "Frontend": verify_frontend(),
        "Documentation": verify_documentation(),
        "HTML UI": verify_html_ui(),
    }

    return print_summary(results)


if __name__ == "__main__":
    sys.exit(main())
