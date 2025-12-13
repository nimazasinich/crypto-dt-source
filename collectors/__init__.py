"""Lazy-loading facade for the collectors package.

The historical codebase exposes a large number of helpers from individual
collector modules (market data, news, explorers, etc.). Importing every module
at package import time pulled in optional dependencies such as ``aiohttp`` that
aren't installed in lightweight environments (e.g. CI for this repo).  That
meant a simple ``import collectors`` – even if the caller only needed
``collectors.aggregator`` – would fail before any real work happened.

This module now re-exports the legacy helpers on demand using ``__getattr__`` so
that optional dependencies are only imported when absolutely necessary.  The
FastAPI backend can safely import ``collectors.aggregator`` (which does not rely
on those heavier stacks) without tripping over missing extras.
"""

from __future__ import annotations

import importlib
from typing import Dict, Tuple

__all__ = [
    # Market data
    "get_coingecko_simple_price",
    "get_coinmarketcap_quotes",
    "get_binance_ticker",
    "collect_market_data",
    # Explorers
    "get_etherscan_gas_price",
    "get_bscscan_bnb_price",
    "get_tronscan_stats",
    "collect_explorer_data",
    # News
    "get_cryptopanic_posts",
    "get_newsapi_headlines",
    "collect_news_data",
    # Sentiment
    "get_fear_greed_index",
    "collect_sentiment_data",
    # On-chain
    "get_the_graph_data",
    "get_blockchair_data",
    "get_glassnode_metrics",
    "collect_onchain_data",
    # HuggingFace Space Crypto API
    "HFCryptoAPIClient",
    "get_hf_crypto_client",
]

_EXPORT_MAP: Dict[str, Tuple[str, str]] = {
    "get_coingecko_simple_price": ("collectors.market_data", "get_coingecko_simple_price"),
    "get_coinmarketcap_quotes": ("collectors.market_data", "get_coinmarketcap_quotes"),
    "get_binance_ticker": ("collectors.market_data", "get_binance_ticker"),
    "collect_market_data": ("collectors.market_data", "collect_market_data"),
    "get_etherscan_gas_price": ("collectors.explorers", "get_etherscan_gas_price"),
    "get_bscscan_bnb_price": ("collectors.explorers", "get_bscscan_bnb_price"),
    "get_tronscan_stats": ("collectors.explorers", "get_tronscan_stats"),
    "collect_explorer_data": ("collectors.explorers", "collect_explorer_data"),
    "get_cryptopanic_posts": ("collectors.news", "get_cryptopanic_posts"),
    "get_newsapi_headlines": ("collectors.news", "get_newsapi_headlines"),
    "collect_news_data": ("collectors.news", "collect_news_data"),
    "get_fear_greed_index": ("collectors.sentiment", "get_fear_greed_index"),
    "collect_sentiment_data": ("collectors.sentiment", "collect_sentiment_data"),
    "get_the_graph_data": ("collectors.onchain", "get_the_graph_data"),
    "get_blockchair_data": ("collectors.onchain", "get_blockchair_data"),
    "get_glassnode_metrics": ("collectors.onchain", "get_glassnode_metrics"),
    "collect_onchain_data": ("collectors.onchain", "collect_onchain_data"),
    # HuggingFace Space Crypto API
    "HFCryptoAPIClient": ("collectors.hf_crypto_api_client", "HFCryptoAPIClient"),
    "get_hf_crypto_client": ("collectors.hf_crypto_api_client", "get_hf_crypto_client"),
}


def __getattr__(name: str):  # pragma: no cover - thin wrapper
    if name not in _EXPORT_MAP:
        raise AttributeError(f"module 'collectors' has no attribute '{name}'")

    module_name, attr_name = _EXPORT_MAP[name]
    module = importlib.import_module(module_name)
    attr = getattr(module, attr_name)
    globals()[name] = attr
    return attr


__all__.extend(["__getattr__"])
