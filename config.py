#!/usr/bin/env python3
"""Configuration module for Hugging Face models."""

import os
from typing import Optional, Dict, Any

HUGGINGFACE_MODELS: Dict[str, str] = {
    "sentiment_twitter": "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "sentiment_financial": "ProsusAI/finbert",
    "summarization": "facebook/bart-large-cnn",
    "crypto_sentiment": "ElKulako/cryptobert",
}

# Self-Healing Configuration
SELF_HEALING_CONFIG = {
    "error_threshold": int(os.getenv("HEALTH_ERROR_THRESHOLD", "3")),  # Failures before degraded
    "cooldown_seconds": int(os.getenv("HEALTH_COOLDOWN_SECONDS", "300")),  # 5 minutes default
    "success_recovery_count": int(os.getenv("HEALTH_RECOVERY_COUNT", "2")),  # Successes to recover
    "enable_auto_reinit": os.getenv("HEALTH_AUTO_REINIT", "true").lower() == "true",
    "reinit_cooldown_seconds": int(os.getenv("HEALTH_REINIT_COOLDOWN", "600")),  # 10 minutes
}

# ==================== REAL API CREDENTIALS (PRIMARY + FALLBACK) ====================
# These are REAL API keys - use them in provider configurations

# Primary HuggingFace Space Configuration (Priority 1)
# IMPORTANT: Set HF_API_TOKEN environment variable with your token
HF_SPACE_PRIMARY = {
    "api_token": os.getenv("HF_API_TOKEN", "").strip() or None,  # Strip whitespace and newlines
    "base_url": os.getenv("HF_SPACE_BASE_URL", "https://really-amin-datasourceforcryptocurrency.hf.space").strip(),
    "ws_url": os.getenv("HF_SPACE_WS_URL", "wss://really-amin-datasourceforcryptocurrency.hf.space/ws").strip(),
    "priority": 1,
    "timeout": 8.0,
    "retry_attempts": 2,
    "enabled": True
}

# External Providers Configuration (Fallback System - Priority 2-3)
EXTERNAL_PROVIDERS = {
    "crypto_api_clean": {
        "enabled": True,
        "api_key": None,  # No auth required
        "base_url": "https://really-amin-crypto-api-clean-fixed.hf.space",
        "timeout": 15.0,
        "priority": 2,
        "category": "resource_database",
        "rate_limit": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000
        },
        "description": "281+ cryptocurrency resources across 12 categories",
        "features": [
            "rpc_nodes",
            "block_explorers",
            "market_data_apis",
            "news_apis",
            "sentiment_apis",
            "onchain_analytics_apis",
            "whale_tracking_apis",
            "hf_resources",
            "free_http_endpoints",
            "cors_proxies"
        ]
    },
    "crypto_dt_source": {
        "enabled": True,
        "api_key": None,  # No auth required
        "base_url": "https://crypto-dt-source.onrender.com",
        "timeout": 20.0,
        "priority": 2,
        "category": "unified_data",
        "rate_limit": {
            "requests_per_minute": 30,
            "requests_per_hour": 500
        },
        "description": "Unified cryptocurrency data API v2.0.0 with AI models",
        "features": [
            "coingecko_prices",
            "binance_klines",
            "fear_greed_index",
            "reddit_posts",
            "rss_feeds",
            "hf_sentiment_models",
            "crypto_datasets"
        ]
    },
    "tronscan": {
        "enabled": True,
        "api_key": os.getenv("TRONSCAN_API_KEY"),  # Set in environment
        "base_url": "https://apilist.tronscan.org/api",
        "timeout": 10.0,
        "priority": 3,
        "category": "blockchain_explorer",
        "rate_limit": {
            "requests_per_second": 5,
            "requests_per_day": 5000
        }
    },
    "bscscan": {
        "enabled": True,
        "api_key": os.getenv("BSCSCAN_API_KEY"),  # Set in environment
        "base_url": "https://api.bscscan.com/api",
        "timeout": 10.0,
        "priority": 3,
        "category": "blockchain_explorer",
        "rate_limit": {
            "requests_per_second": 5,
            "requests_per_day": 10000
        }
    },
    "etherscan": {
        "enabled": True,
        "api_key": os.getenv("ETHERSCAN_API_KEY"),  # Set in environment
        "base_url": "https://api.etherscan.io/api",
        "timeout": 10.0,
        "priority": 3,
        "category": "blockchain_explorer",
        "rate_limit": {
            "requests_per_second": 5,
            "requests_per_day": 100000
        }
    },
    "coinmarketcap": {
        "enabled": True,
        "api_key": os.getenv("COINMARKETCAP_API_KEY"),  # Set in environment
        "base_url": "https://pro-api.coinmarketcap.com/v1",
        "timeout": 15.0,
        "priority": 2,
        "category": "market_data",
        "rate_limit": {
            "requests_per_minute": 30,
            "requests_per_day": 10000
        }
    },
    "newsapi": {
        "enabled": True,
        "api_key": os.getenv("NEWSAPI_KEY"),  # Set in environment
        "base_url": "https://newsapi.org/v2",
        "timeout": 10.0,
        "priority": 2,
        "category": "news",
        "rate_limit": {
            "requests_per_hour": 100,
            "requests_per_day": 1000
        }
    }
}

# Model Configuration
MODEL_CONFIG = {
    "confidence_threshold": float(os.getenv("MODEL_CONFIDENCE_THRESHOLD", "0.70")),
    "gap_fill_enabled": os.getenv("GAP_FILL_ENABLED", "true").lower() == "true",
    "cache_ttl_seconds": int(os.getenv("CACHE_TTL_SECONDS", "30")),
    "batch_prediction_max": int(os.getenv("BATCH_PREDICTION_MAX", "100")),
}

# Gap Filling Configuration
GAP_FILLING_CONFIG = {
    "enabled": os.getenv("GAP_FILL_ENABLED", "true").lower() == "true",
    "max_gap_size": int(os.getenv("MAX_GAP_SIZE", "100")),  # Maximum number of missing data points to fill
    "interpolation_method": os.getenv("INTERPOLATION_METHOD", "linear"),  # linear, cubic, polynomial
    "confidence_decay_factor": float(os.getenv("CONFIDENCE_DECAY_FACTOR", "0.95")),  # Confidence decreases with gap size
    "use_ai_synthesis": os.getenv("USE_AI_SYNTHESIS", "true").lower() == "true",
    "fallback_to_external": os.getenv("FALLBACK_TO_EXTERNAL", "true").lower() == "true",
}

class Settings:
    """Application settings."""
    def __init__(self):
        self.hf_token: Optional[str] = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        # Self-healing settings
        self.health_error_threshold: int = SELF_HEALING_CONFIG["error_threshold"]
        self.health_cooldown_seconds: int = SELF_HEALING_CONFIG["cooldown_seconds"]
        self.health_success_recovery_count: int = SELF_HEALING_CONFIG["success_recovery_count"]
        self.health_enable_auto_reinit: bool = SELF_HEALING_CONFIG["enable_auto_reinit"]
        self.health_reinit_cooldown_seconds: int = SELF_HEALING_CONFIG["reinit_cooldown_seconds"]

_settings = Settings()

def get_settings() -> Settings:
    """Get application settings instance."""
    return _settings

