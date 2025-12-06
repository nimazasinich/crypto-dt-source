#!/usr/bin/env python3
"""
Simple smoke test for the Help page route.

Run this after starting the server (hf_unified_server or production_server)
to verify that the /help route is available and serving HTML.
"""

import sys
from typing import Tuple

import requests


BASE_URL = "http://127.0.0.1:7860"


def test_help_endpoint() -> Tuple[bool, str]:
    """Check that GET /help returns 200 and HTML content."""
    try:
        response = requests.get(f"{BASE_URL}/help", timeout=10)
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}"

        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return False, f"Unexpected content-type: {content_type}"

        return True, "OK"
    except Exception as exc:  # pragma: no cover - simple smoke test
        return False, str(exc)


def main() -> int:
    """Entry point for manual execution."""
    ok, status = test_help_endpoint()
    print("Testing GET /help ...")
    if ok:
        print(f"  ✅ {status}")
        return 0
    print(f"  ❌ {status}")
    return 1


if __name__ == "__main__":
    sys.exit(main())


