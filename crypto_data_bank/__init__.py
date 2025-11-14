"""
بانک اطلاعاتی قدرتمند رمزارز
Crypto Data Bank - Powerful cryptocurrency data aggregation

Features:
- Free data collection from 200+ sources (NO API KEYS)
- Real-time prices from 5+ free providers
- News from 8+ RSS feeds
- Market sentiment analysis
- HuggingFace AI models for analysis
- Intelligent caching and database storage
"""

__version__ = "1.0.0"
__author__ = "Nima Zasinich"
__description__ = "Powerful FREE cryptocurrency data bank"

from .database import CryptoDataBank, get_db
from .orchestrator import DataCollectionOrchestrator, get_orchestrator

__all__ = [
    "CryptoDataBank",
    "get_db",
    "DataCollectionOrchestrator",
    "get_orchestrator",
]
