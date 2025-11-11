"""
Collectors Package
Data collection modules for cryptocurrency APIs

Modules:
- market_data: CoinGecko, CoinMarketCap, Binance market data
- explorers: Etherscan, BscScan, TronScan blockchain explorers
- news: CryptoPanic, NewsAPI news aggregation
- sentiment: Alternative.me Fear & Greed Index
- onchain: The Graph, Blockchair on-chain analytics (placeholder)
"""

from collectors.market_data import (
    get_coingecko_simple_price,
    get_coinmarketcap_quotes,
    get_binance_ticker,
    collect_market_data
)

from collectors.explorers import (
    get_etherscan_gas_price,
    get_bscscan_bnb_price,
    get_tronscan_stats,
    collect_explorer_data
)

from collectors.news import (
    get_cryptopanic_posts,
    get_newsapi_headlines,
    collect_news_data
)

from collectors.sentiment import (
    get_fear_greed_index,
    collect_sentiment_data
)

from collectors.onchain import (
    get_the_graph_data,
    get_blockchair_data,
    get_glassnode_metrics,
    collect_onchain_data
)

__all__ = [
    # Market Data
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
]
