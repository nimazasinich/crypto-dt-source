"""
Data Providers for HuggingFace Crypto Data Engine

This module exports:
1. Original market data providers (Binance, CoinGecko, Kraken, CoinCap)
2. New REST API providers for blockchain, news, and AI services

All providers use async HTTP with httpx.
"""

# Original market data providers
from .binance_provider import BinanceProvider
from .coingecko_provider import CoinGeckoProvider
from .kraken_provider import KrakenProvider
from .coincap_provider import CoinCapProvider

# New REST API providers (no WebSockets)
from .etherscan_provider import EtherscanProvider
from .bscscan_provider import BscscanProvider
from .tronscan_provider import TronscanProvider
from .coinmarketcap_provider import CoinMarketCapProvider
from .news_provider import NewsProvider
from .hf_sentiment_provider import HFSentimentProvider

# Base provider utilities
from .base import BaseProvider as RestBaseProvider
from .base import create_success_response, create_error_response

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
