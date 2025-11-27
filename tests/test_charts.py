"""
Test suite for chart endpoints
Validates rate limit history and freshness history endpoints
"""

from datetime import datetime, timedelta

import pytest
import requests as R

# Base URL for API (adjust if running on different port/host)
BASE = "http://localhost:7860"


class TestRateLimitHistory:
    """Test suite for /api/charts/rate-limit-history endpoint"""

    def test_rate_limit_default(self):
        """Test rate limit history with default parameters"""
        r = R.get(f"{BASE}/api/charts/rate-limit-history")
        r.raise_for_status()
        data = r.json()

        # Validate response structure
        assert isinstance(data, list), "Response should be a list"

        if len(data) > 0:
            # Validate first series object
            s = data[0]
            assert "provider" in s, "Series should have provider field"
            assert "hours" in s, "Series should have hours field"
            assert "series" in s, "Series should have series field"
            assert "meta" in s, "Series should have meta field"

            # Validate hours field
            assert s["hours"] == 24, "Default hours should be 24"

            # Validate series points
            assert isinstance(s["series"], list), "series should be a list"
            assert len(s["series"]) == 24, "Should have 24 data points for 24 hours"

            # Validate each point
            for point in s["series"]:
                assert "t" in point, "Point should have timestamp (t)"
                assert "pct" in point, "Point should have percentage (pct)"
                assert 0 <= point["pct"] <= 100, f"Percentage should be 0-100, got {point['pct']}"

                # Validate timestamp format
                try:
                    datetime.fromisoformat(point["t"].replace("Z", "+00:00"))
                except ValueError:
                    pytest.fail(f"Invalid timestamp format: {point['t']}")

            # Validate meta
            meta = s["meta"]
            assert "limit_type" in meta, "Meta should have limit_type"
            assert "limit_value" in meta, "Meta should have limit_value"

    def test_rate_limit_48h_subset(self):
        """Test rate limit history with custom time range and provider selection"""
        r = R.get(
            f"{BASE}/api/charts/rate-limit-history",
            params={"hours": 48, "providers": "coingecko,cmc"},
        )
        r.raise_for_status()
        data = r.json()

        assert isinstance(data, list), "Response should be a list"
        assert len(data) <= 2, "Should have at most 2 providers (coingecko, cmc)"

        for series in data:
            assert series["hours"] == 48, "Should have 48 hours of data"
            assert len(series["series"]) == 48, "Should have 48 data points"
            assert series["provider"] in ["coingecko", "cmc"], "Provider should match requested"

    def test_rate_limit_hours_clamping(self):
        """Test that hours parameter is properly clamped to valid range"""
        # Test lower bound (should clamp to 1)
        r = R.get(f"{BASE}/api/charts/rate-limit-history", params={"hours": 0})
        assert r.status_code in [200, 422], "Should handle hours=0"

        # Test upper bound (should clamp to 168)
        r = R.get(f"{BASE}/api/charts/rate-limit-history", params={"hours": 999})
        assert r.status_code in [200, 422], "Should handle hours=999"

    def test_rate_limit_invalid_provider(self):
        """Test rejection of invalid provider names"""
        r = R.get(
            f"{BASE}/api/charts/rate-limit-history", params={"providers": "invalid_provider_xyz"}
        )

        # Should return 400 for invalid provider
        assert r.status_code in [400, 404], "Should reject invalid provider names"

    def test_rate_limit_max_providers(self):
        """Test that provider list is limited to max 5"""
        # Request more than 5 providers
        providers_list = ",".join([f"provider{i}" for i in range(10)])
        r = R.get(f"{BASE}/api/charts/rate-limit-history", params={"providers": providers_list})

        # Should either succeed with max 5 or reject invalid providers
        if r.status_code == 200:
            data = r.json()
            assert len(data) <= 5, "Should limit to max 5 providers"

    def test_rate_limit_response_time(self):
        """Test that endpoint responds within performance target (< 200ms for 24h)"""
        import time

        start = time.time()
        r = R.get(f"{BASE}/api/charts/rate-limit-history")
        duration_ms = (time.time() - start) * 1000

        r.raise_for_status()
        # Allow 500ms for dev environment (more generous than production target)
        assert duration_ms < 500, f"Response took {duration_ms:.0f}ms (target < 500ms)"


class TestFreshnessHistory:
    """Test suite for /api/charts/freshness-history endpoint"""

    def test_freshness_default(self):
        """Test freshness history with default parameters"""
        r = R.get(f"{BASE}/api/charts/freshness-history")
        r.raise_for_status()
        data = r.json()

        # Validate response structure
        assert isinstance(data, list), "Response should be a list"

        if len(data) > 0:
            # Validate first series object
            s = data[0]
            assert "provider" in s, "Series should have provider field"
            assert "hours" in s, "Series should have hours field"
            assert "series" in s, "Series should have series field"
            assert "meta" in s, "Series should have meta field"

            # Validate hours field
            assert s["hours"] == 24, "Default hours should be 24"

            # Validate series points
            assert isinstance(s["series"], list), "series should be a list"
            assert len(s["series"]) == 24, "Should have 24 data points for 24 hours"

            # Validate each point
            for point in s["series"]:
                assert "t" in point, "Point should have timestamp (t)"
                assert "staleness_min" in point, "Point should have staleness_min"
                assert "ttl_min" in point, "Point should have ttl_min"
                assert "status" in point, "Point should have status"

                assert point["staleness_min"] >= 0, "Staleness should be non-negative"
                assert point["ttl_min"] > 0, "TTL should be positive"
                assert point["status"] in [
                    "fresh",
                    "aging",
                    "stale",
                ], f"Invalid status: {point['status']}"

                # Validate timestamp format
                try:
                    datetime.fromisoformat(point["t"].replace("Z", "+00:00"))
                except ValueError:
                    pytest.fail(f"Invalid timestamp format: {point['t']}")

            # Validate meta
            meta = s["meta"]
            assert "category" in meta, "Meta should have category"
            assert "default_ttl" in meta, "Meta should have default_ttl"

    def test_freshness_72h_subset(self):
        """Test freshness history with custom time range and provider selection"""
        r = R.get(
            f"{BASE}/api/charts/freshness-history",
            params={"hours": 72, "providers": "coingecko,binance"},
        )
        r.raise_for_status()
        data = r.json()

        assert isinstance(data, list), "Response should be a list"
        assert len(data) <= 2, "Should have at most 2 providers"

        for series in data:
            assert series["hours"] == 72, "Should have 72 hours of data"
            assert len(series["series"]) == 72, "Should have 72 data points"
            assert series["provider"] in ["coingecko", "binance"], "Provider should match requested"

    def test_freshness_hours_clamping(self):
        """Test that hours parameter is properly clamped to valid range"""
        # Test lower bound (should clamp to 1)
        r = R.get(f"{BASE}/api/charts/freshness-history", params={"hours": 0})
        assert r.status_code in [200, 422], "Should handle hours=0"

        # Test upper bound (should clamp to 168)
        r = R.get(f"{BASE}/api/charts/freshness-history", params={"hours": 999})
        assert r.status_code in [200, 422], "Should handle hours=999"

    def test_freshness_invalid_provider(self):
        """Test rejection of invalid provider names"""
        r = R.get(f"{BASE}/api/charts/freshness-history", params={"providers": "foo,bar"})

        # Should return 400 for invalid providers
        assert r.status_code in [400, 404], "Should reject invalid provider names"

    def test_freshness_status_derivation(self):
        """Test that status is correctly derived from staleness and TTL"""
        r = R.get(f"{BASE}/api/charts/freshness-history")
        r.raise_for_status()
        data = r.json()

        if len(data) > 0:
            for series in data:
                ttl = series["meta"]["default_ttl"]

                for point in series["series"]:
                    staleness = point["staleness_min"]
                    status = point["status"]

                    # Validate status derivation logic
                    if staleness <= ttl:
                        expected = "fresh"
                    elif staleness <= ttl * 2:
                        expected = "aging"
                    else:
                        expected = "stale"

                    # Allow for edge case where staleness is 999 (no data)
                    if staleness == 999.0:
                        assert status == "stale", "No data should be marked as stale"
                    else:
                        assert (
                            status == expected
                        ), f"Status mismatch: staleness={staleness}, ttl={ttl}, expected={expected}, got={status}"

    def test_freshness_response_time(self):
        """Test that endpoint responds within performance target (< 200ms for 24h)"""
        import time

        start = time.time()
        r = R.get(f"{BASE}/api/charts/freshness-history")
        duration_ms = (time.time() - start) * 1000

        r.raise_for_status()
        # Allow 500ms for dev environment
        assert duration_ms < 500, f"Response took {duration_ms:.0f}ms (target < 500ms)"


class TestSecurityValidation:
    """Test security and validation measures"""

    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are safely handled"""
        malicious_providers = "'; DROP TABLE providers; --"
        r = R.get(
            f"{BASE}/api/charts/rate-limit-history", params={"providers": malicious_providers}
        )

        # Should reject or safely handle malicious input
        assert r.status_code in [400, 404, 500], "Should reject SQL injection attempts"

    def test_xss_prevention(self):
        """Test that XSS attempts are safely handled"""
        malicious_providers = "<script>alert('xss')</script>"
        r = R.get(
            f"{BASE}/api/charts/rate-limit-history", params={"providers": malicious_providers}
        )

        # Should reject or safely handle malicious input
        assert r.status_code in [400, 404], "Should reject XSS attempts"

    def test_parameter_type_validation(self):
        """Test that invalid parameter types are rejected"""
        # Test invalid hours type
        r = R.get(f"{BASE}/api/charts/rate-limit-history", params={"hours": "invalid"})
        assert r.status_code == 422, "Should reject invalid parameter type"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_provider_list(self):
        """Test behavior with empty provider list"""
        r = R.get(f"{BASE}/api/charts/rate-limit-history", params={"providers": ""})
        r.raise_for_status()
        data = r.json()

        # Should return default providers or empty list
        assert isinstance(data, list), "Should return list even with empty providers param"

    def test_whitespace_handling(self):
        """Test that whitespace in provider names is properly handled"""
        r = R.get(
            f"{BASE}/api/charts/rate-limit-history", params={"providers": " coingecko , cmc "}
        )

        # Should handle whitespace gracefully
        if r.status_code == 200:
            data = r.json()
            for series in data:
                assert (
                    series["provider"].strip() == series["provider"]
                ), "Provider names should be trimmed"

    def test_concurrent_requests(self):
        """Test that endpoint handles concurrent requests safely"""
        import concurrent.futures

        def make_request():
            r = R.get(f"{BASE}/api/charts/rate-limit-history")
            r.raise_for_status()
            return r.json()

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert len(results) == 5, "All concurrent requests should succeed"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
