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

class Settings:
    """Application settings."""
    def __init__(self):
        self.hf_token: Optional[str] = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")

_settings = Settings()

def get_settings() -> Settings:
    """Get application settings instance."""
    return _settings

