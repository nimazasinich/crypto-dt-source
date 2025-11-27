"""
REST API Data Providers for HuggingFace Space Backend

This module provides direct REST API integrations for:
- Blockchain data (Etherscan, BscScan, TronScan)
- Market data (CoinMarketCap)
- News aggregation (NewsAPI)
- AI sentiment analysis (HuggingFace models)

All providers use async HTTP with httpx, 10-second timeouts,
and optional 30-second in-memory caching.
"""

from .etherscan_provider import EtherscanProvider
from .bscscan_provider import BscscanProvider
from .tronscan_provider import TronscanProvider
from .coinmarketcap_provider import CoinMarketCapProvider
from .news_provider import NewsProvider
from .hf_sentiment_provider import HFSentimentProvider

__all__ = [
    "EtherscanProvider",
    "BscscanProvider",
    "TronscanProvider",
    "CoinMarketCapProvider",
    "NewsProvider",
    "HFSentimentProvider",
]
