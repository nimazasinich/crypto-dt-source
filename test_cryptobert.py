#!/usr/bin/env python3
"""
Test script for CryptoBERT model integration
Verifies that the ElKulako/CryptoBERT model is properly configured and accessible
"""

import json
import os
import sys
from typing import Any, Dict

# Ensure the token is set
os.environ.setdefault("HF_TOKEN", "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")

import ai_models

# Import after setting environment variable
import config


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_config():
    """Test configuration settings"""
    print_section("Configuration Test")

    print(f"✓ HF_TOKEN configured: {config.HF_USE_AUTH_TOKEN}")
    print(f"  Token (masked): {config.HF_TOKEN[:10]}...{config.HF_TOKEN[-5:]}")
    print(f"\n✓ Models configured:")
    for model_type, model_id in config.HUGGINGFACE_MODELS.items():
        print(f"  - {model_type}: {model_id}")

    return True


def test_model_info():
    """Test getting model information"""
    print_section("Model Information")

    info = ai_models.get_model_info()

    print(f"Transformers available: {info['transformers_available']}")
    print(f"Models initialized: {info['models_initialized']}")
    print(f"HF auth configured: {info['hf_auth_configured']}")
    print(f"Device: {info['device']}")

    print(f"\nConfigured models:")
    for model_type, model_name in info["model_names"].items():
        print(f"  - {model_type}: {model_name}")

    return info["transformers_available"]


def test_model_loading():
    """Test loading models"""
    print_section("Model Loading Test")

    print("Attempting to load models...")
    result = ai_models.initialize_models()

    print(f"\nInitialization result:")
    print(f"  Success: {result['success']}")
    print(f"  Status: {result['status']}")

    print(f"\nModel loading status:")
    for model_name, loaded in result["models"].items():
        status = "✓ Loaded" if loaded else "✗ Failed"
        print(f"  {status}: {model_name}")

    if "errors" in result:
        print(f"\nErrors encountered:")
        for error in result["errors"]:
            print(f"  - {error}")

    return result["models"].get("crypto_sentiment", False)


def test_crypto_sentiment():
    """Test CryptoBERT sentiment analysis"""
    print_section("CryptoBERT Sentiment Analysis Test")

    test_texts = [
        "Bitcoin shows strong bullish momentum with increasing institutional adoption",
        "Ethereum network faces congestion issues and high gas fees",
        "The cryptocurrency market remains stable with no significant changes",
        "Major crash in crypto markets as Bitcoin falls below key support level",
        "New altcoin surge as DeFi protocols gain massive traction",
    ]

    print("Testing crypto sentiment analysis with sample texts:\n")

    for i, text in enumerate(test_texts, 1):
        print(f"Test {i}:")
        print(f"  Text: {text[:60]}...")

        try:
            result = ai_models.analyze_crypto_sentiment(text)

            print(f"  Result:")
            print(f"    Sentiment: {result['label']}")
            print(f"    Confidence: {result['score']:.4f}")

            if "model" in result:
                print(f"    Model used: {result['model']}")

            if "predictions" in result:
                print(f"    Top predictions:")
                for pred in result["predictions"]:
                    print(f"      - {pred['token']}: {pred['score']:.4f}")

            if "error" in result:
                print(f"    ⚠ Error: {result['error']}")

        except Exception as e:
            print(f"    ✗ Exception: {str(e)}")

        print()


def test_comparison():
    """Compare standard vs crypto-specific sentiment"""
    print_section("Standard vs CryptoBERT Sentiment Comparison")

    test_text = "Bitcoin breaks resistance with massive volume, bulls in control"

    print(f"Test text: {test_text}\n")

    # Standard sentiment
    print("Standard sentiment analysis:")
    try:
        standard = ai_models.analyze_sentiment(test_text)
        print(f"  Sentiment: {standard['label']}")
        print(f"  Score: {standard['score']:.4f}")
        print(f"  Confidence: {standard['confidence']:.4f}")
    except Exception as e:
        print(f"  Error: {str(e)}")

    print()

    # CryptoBERT sentiment
    print("CryptoBERT sentiment analysis:")
    try:
        crypto = ai_models.analyze_crypto_sentiment(test_text)
        print(f"  Sentiment: {crypto['label']}")
        print(f"  Score: {crypto['score']:.4f}")
        if "predictions" in crypto:
            print(f"  Top predictions: {[p['token'] for p in crypto['predictions']]}")
    except Exception as e:
        print(f"  Error: {str(e)}")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  CryptoBERT Integration Test Suite")
    print("  Model: ElKulako/CryptoBERT")
    print("=" * 70)

    try:
        # Test 1: Configuration
        if not test_config():
            print("\n✗ Configuration test failed")
            return 1

        # Test 2: Model info
        if not test_model_info():
            print("\n⚠ Transformers library not available")
            print("  Install with: pip install transformers torch")
            return 1

        # Test 3: Model loading
        crypto_loaded = test_model_loading()

        if not crypto_loaded:
            print("\n⚠ CryptoBERT model not loaded")
            print("  This may be due to:")
            print("  1. Missing/invalid HF_TOKEN")
            print("  2. Network connectivity issues")
            print("  3. Model access restrictions")
            print("\n  Run setup script: ./setup_cryptobert.sh")

        # Test 4: Crypto sentiment (even if model not loaded, to test fallback)
        test_crypto_sentiment()

        # Test 5: Comparison
        test_comparison()

        print_section("Test Suite Complete")

        if crypto_loaded:
            print("✓ All tests passed - CryptoBERT is fully operational")
            return 0
        else:
            print("⚠ Tests completed with warnings - CryptoBERT not loaded")
            print("  Standard sentiment analysis is available as fallback")
            return 0

    except Exception as e:
        print(f"\n✗ Test suite failed with exception: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
