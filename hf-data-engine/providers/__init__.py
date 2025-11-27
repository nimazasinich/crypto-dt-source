"""
Data Providers for HuggingFace Crypto Data Engine

This module exports:
1. Original market data providers (Binance, CoinGecko, Kraken, CoinCap)
2. New REST API providers for blockchain, news, and AI services

All providers use async HTTP with httpx.
"""

# Base provider utilities
from .base import BaseProvider as RestBaseProvider
from .base import create_error_response, create_success_response

# Original market data providers
from .binance_provider import BinanceProvider
from .bscscan_provider import BscscanProvider
from .coincap_provider import CoinCapProvider
from .coingecko_provider import CoinGeckoProvider
from .coinmarketcap_provider import CoinMarketCapProvider

# New REST API providers (no WebSockets)
from .etherscan_provider import EtherscanProvider
from .hf_sentiment_provider import HFSentimentProvider
from .kraken_provider import KrakenProvider
from .news_provider import NewsProvider
from .tronscan_provider import TronscanProvider

__all__ = [
    # Original providers
    "BinanceProvider",
    "CoinGeckoProvider",
    "KrakenProvider",
    "CoinCapProvider",
    # New REST providers
    "EtherscanProvider",
    "BscscanProvider",
    "TronscanProvider",
    "CoinMarketCapProvider",
    "NewsProvider",
    "HFSentimentProvider",
    # Utilities
    "RestBaseProvider",
    "create_success_response",
    "create_error_response",
]
