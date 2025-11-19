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

