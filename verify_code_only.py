#!/usr/bin/env python3
"""
Basic verification WITHOUT external dependencies
Just checks if code structure is correct
"""

import ast
import os


def verify_file(filepath):
    """Verify a Python file has valid syntax and structure"""
    print(f"\n{'='*60}")
    print(f"Checking: {filepath}")
    print("=" * 60)

    if not os.path.exists(filepath):
        print(f"❌ File not found!")
        return False

    try:
        with open(filepath, "r") as f:
            code = f.read()

        # Parse syntax
        tree = ast.parse(code)
        print(f"✅ Syntax is valid")

        # Count functions
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        async_functions = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef)
        ]
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        print(f"📊 Stats:")
        print(f"   - Lines: {len(code.splitlines())}")
        print(f"   - Classes: {len(classes)}")
        print(f"   - Functions: {len(functions)}")
        print(f"   - Async functions: {len(async_functions)}")

        if classes:
            print(f"   - Class names: {', '.join(classes[:5])}")
        if async_functions:
            print(f"   - Async functions: {', '.join(async_functions[:5])}")

        # Check for key patterns
        patterns = {
            "HTTP requests": "httpx" in code or "AsyncClient" in code,
            "Error handling": "try:" in code and "except" in code,
            "Async/await": "async def" in code and "await" in code,
            "Type hints": ": str" in code or ": int" in code or "-> " in code,
            "Docstrings": '"""' in code,
        }

        print(f"✅ Code patterns found:")
        for pattern, found in patterns.items():
            status = "✅" if found else "⚠️"
            print(f"   {status} {pattern}")

        return True

    except SyntaxError as e:
        print(f"❌ Syntax Error at line {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("CODE VERIFICATION (Without Running Server)")
    print("=" * 60)
    print("\n⚠️ NOTE: This only checks syntax and structure")
    print("⚠️ Cannot test actual HTTP requests without dependencies\n")

    files = [
        "crypto_data_engine_server.py",
        "backend/services/coingecko_client.py",
        "backend/services/binance_client.py",
        "backend/services/huggingface_inference_client.py",
        "backend/services/crypto_news_client.py",
        "backend/routers/crypto_data_engine_api.py",
    ]

    results = {}
    for filepath in files:
        results[filepath] = verify_file(filepath)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for filepath, result in results.items():
        status = "✅ VALID" if result else "❌ INVALID"
        print(f"{status}: {filepath}")

    print("=" * 60)
    print(f"Result: {passed}/{total} files are syntactically valid")

    if passed == total:
        print("\n✅ All files have valid Python code")
        print("⚠️  But cannot test actual functionality without:")
        print("   1. Installing: pip install httpx fastapi feedparser")
        print("   2. Setting: export HF_API_TOKEN=xxx")
        print("   3. Running: python3 crypto_data_engine_server.py")

    print("=" * 60)


if __name__ == "__main__":
    main()
