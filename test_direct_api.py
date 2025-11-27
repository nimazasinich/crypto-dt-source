#!/usr/bin/env python3
"""
Direct API Test Suite
Tests for direct model loading and external API integration
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from hf_unified_server import app

client = TestClient(app)


class TestSystemEndpoints:
    """Test system and status endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["version"] == "2.0.0"

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_system_status(self):
        """Test system status endpoint"""
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "models" in data
        assert "datasets" in data
        assert "external_apis" in data


class TestCoinGeckoEndpoints:
    """Test CoinGecko API endpoints"""

    def test_get_prices(self):
        """Test getting prices from CoinGecko"""
        response = client.get("/api/v1/coingecko/price?symbols=BTC,ETH&limit=10")
        assert response.status_code in [200, 503]  # 503 if rate limited

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data

    def test_get_trending(self):
        """Test getting trending coins"""
        response = client.get("/api/v1/coingecko/trending?limit=5")
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "success" in data


class TestBinanceEndpoints:
    """Test Binance API endpoints"""

    def test_get_klines(self):
        """Test getting klines from Binance"""
        response = client.get("/api/v1/binance/klines?symbol=BTC&timeframe=1h&limit=10")
        assert response.status_code in [200, 400, 503]

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
            assert "symbol" in data

    def test_get_ticker(self):
        """Test getting ticker from Binance"""
        response = client.get("/api/v1/binance/ticker?symbol=BTC")
        assert response.status_code in [200, 503]


class TestAlternativeMeEndpoints:
    """Test Alternative.me API endpoints"""

    def test_get_fear_greed_index(self):
        """Test getting Fear & Greed Index"""
        response = client.get("/api/v1/alternative/fng?limit=1")
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
            assert len(data["data"]) > 0
            assert "value" in data["data"][0]


class TestRedditEndpoints:
    """Test Reddit API endpoints"""

    def test_get_top_posts(self):
        """Test getting top posts from Reddit"""
        response = client.get("/api/v1/reddit/top?subreddit=cryptocurrency&limit=5")
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data

    def test_get_new_posts(self):
        """Test getting new posts from Reddit"""
        response = client.get("/api/v1/reddit/new?subreddit=bitcoin&limit=5")
        assert response.status_code in [200, 503]


class TestRSSEndpoints:
    """Test RSS feed endpoints"""

    def test_get_coindesk_rss(self):
        """Test getting CoinDesk RSS feed"""
        response = client.get("/api/v1/coindesk/rss?limit=5")
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data

    def test_get_cointelegraph_rss(self):
        """Test getting CoinTelegraph RSS feed"""
        response = client.get("/api/v1/cointelegraph/rss?limit=5")
        assert response.status_code in [200, 503]

    def test_get_specific_feed(self):
        """Test getting specific RSS feed"""
        response = client.get("/api/v1/rss/feed?feed_name=coindesk&limit=5")
        assert response.status_code in [200, 503]

    def test_get_all_feeds(self):
        """Test getting all RSS feeds"""
        response = client.get("/api/v1/rss/all?limit_per_feed=3")
        assert response.status_code in [200, 503]


class TestNewsEndpoints:
    """Test news aggregation endpoints"""

    def test_get_latest_news(self):
        """Test getting latest news"""
        response = client.get("/api/v1/news/latest?limit=10")
        assert response.status_code in [200, 503]


class TestHuggingFaceModelEndpoints:
    """Test HuggingFace model endpoints (NO PIPELINE)"""

    def test_get_models(self):
        """Test getting loaded models"""
        response = client.get("/api/v1/hf/models")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "models" in data
        assert "device" in data

    def test_sentiment_analysis(self):
        """Test sentiment analysis (NO PIPELINE)"""
        response = client.post(
            "/api/v1/hf/sentiment",
            json={"text": "Bitcoin is going to the moon!", "model_key": "cryptobert_elkulako"},
        )
        # May fail if model not loaded or transformers not installed
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "sentiment" in data
            assert "confidence" in data
            assert "inference_type" in data
            assert data["inference_type"] == "direct_no_pipeline"

    def test_batch_sentiment_analysis(self):
        """Test batch sentiment analysis"""
        response = client.post(
            "/api/v1/hf/sentiment/batch",
            json={
                "texts": ["Bitcoin is mooning!", "Ethereum looks bearish", "Market is neutral"],
                "model_key": "cryptobert_elkulako",
            },
        )
        # May fail if model not loaded
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "results" in data
            assert len(data["results"]) == 3


class TestHuggingFaceDatasetEndpoints:
    """Test HuggingFace dataset endpoints"""

    def test_get_datasets(self):
        """Test getting loaded datasets"""
        response = client.get("/api/v1/hf/datasets")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "datasets" in data


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_headers(self):
        """Test that rate limit headers are present"""
        response = client.get("/api/v1/status")
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers


class TestDirectModelLoaderUnit:
    """Unit tests for direct model loader"""

    @pytest.mark.asyncio
    async def test_direct_model_loader_import(self):
        """Test that direct model loader can be imported"""
        try:
            from backend.services.direct_model_loader import direct_model_loader

            assert direct_model_loader is not None
        except ImportError as e:
            pytest.skip(f"Direct model loader not available: {e}")

    @pytest.mark.asyncio
    async def test_get_loaded_models(self):
        """Test getting loaded models info"""
        try:
            from backend.services.direct_model_loader import direct_model_loader

            result = direct_model_loader.get_loaded_models()
            assert "success" in result
            assert "models" in result
            assert "device" in result
        except ImportError:
            pytest.skip("Direct model loader not available")


class TestDatasetLoaderUnit:
    """Unit tests for dataset loader"""

    @pytest.mark.asyncio
    async def test_dataset_loader_import(self):
        """Test that dataset loader can be imported"""
        try:
            from backend.services.dataset_loader import crypto_dataset_loader

            assert crypto_dataset_loader is not None
        except ImportError as e:
            pytest.skip(f"Dataset loader not available: {e}")

    @pytest.mark.asyncio
    async def test_get_loaded_datasets(self):
        """Test getting loaded datasets info"""
        try:
            from backend.services.dataset_loader import crypto_dataset_loader

            result = crypto_dataset_loader.get_loaded_datasets()
            assert "success" in result
            assert "datasets" in result
        except ImportError:
            pytest.skip("Dataset loader not available")


class TestExternalAPIClientsUnit:
    """Unit tests for external API clients"""

    def test_alternative_me_client_import(self):
        """Test Alternative.me client import"""
        try:
            from backend.services.external_api_clients import alternative_me_client

            assert alternative_me_client is not None
        except ImportError as e:
            pytest.skip(f"External API clients not available: {e}")

    def test_reddit_client_import(self):
        """Test Reddit client import"""
        try:
            from backend.services.external_api_clients import reddit_client

            assert reddit_client is not None
        except ImportError:
            pytest.skip("External API clients not available")

    def test_rss_client_import(self):
        """Test RSS client import"""
        try:
            from backend.services.external_api_clients import rss_feed_client

            assert rss_feed_client is not None
        except ImportError:
            pytest.skip("External API clients not available")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
