"""
Data Normalization Functions
Convert provider-specific responses to canonical format
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DataNormalizer:
    """Normalizes data from different providers to canonical format"""

    @staticmethod
    def normalize_market_data(data: Any, provider: str) -> Dict[str, Any]:
        """
        Normalize market data to canonical format

        Canonical format:
        {
            "last_updated": "ISO timestamp",
            "items": [
                {
                    "symbol": "BTC",
                    "name": "Bitcoin",
                    "price": 45000.0,
                    "change_24h": 2.5,
                    "volume_24h": 25000000000,
                    "market_cap": 880000000000,
                    "rank": 1,
                    "source": "provider_name"
                }
            ]
        }
        """
        try:
            if provider == "coingecko":
                return DataNormalizer._normalize_coingecko_market(data)
            elif provider == "binance":
                return DataNormalizer._normalize_binance_market(data)
            elif provider == "coincap":
                return DataNormalizer._normalize_coincap_market(data)
            elif provider.startswith("coinmarketcap"):
                return DataNormalizer._normalize_cmc_market(data)
            else:
                logger.warning(f"Unknown provider for market data: {provider}")
                return {"last_updated": datetime.utcnow().isoformat(), "items": []}

        except Exception as e:
            logger.error(f"Error normalizing market data from {provider}: {e}")
            return {"last_updated": datetime.utcnow().isoformat(), "items": []}

    @staticmethod
    def _normalize_coingecko_market(data: Any) -> Dict[str, Any]:
        """Normalize CoinGecko market data"""
        items = []

        if isinstance(data, list):
            for coin in data:
                items.append(
                    {
                        "symbol": coin.get("symbol", "").upper(),
                        "name": coin.get("name", ""),
                        "price": float(coin.get("current_price", 0)),
                        "change_24h": float(coin.get("price_change_percentage_24h", 0)),
                        "volume_24h": float(coin.get("total_volume", 0)),
                        "market_cap": float(coin.get("market_cap", 0)),
                        "rank": int(coin.get("market_cap_rank", 0)),
                        "source": "coingecko",
                    }
                )

        return {"last_updated": datetime.utcnow().isoformat() + "Z", "items": items}

    @staticmethod
    def _normalize_binance_market(data: Any) -> Dict[str, Any]:
        """Normalize Binance market data"""
        items = []

        if isinstance(data, list):
            for ticker in data:
                symbol = ticker.get("symbol", "")
                # Extract base symbol (e.g., BTCUSDT -> BTC)
                base_symbol = symbol.replace("USDT", "").replace("BUSD", "").replace("USDC", "")

                items.append(
                    {
                        "symbol": base_symbol,
                        "name": base_symbol,
                        "price": float(ticker.get("lastPrice", 0)),
                        "change_24h": float(ticker.get("priceChangePercent", 0)),
                        "volume_24h": float(ticker.get("quoteVolume", 0)),
                        "market_cap": None,
                        "rank": None,
                        "source": "binance",
                    }
                )

        return {"last_updated": datetime.utcnow().isoformat() + "Z", "items": items}

    @staticmethod
    def _normalize_coincap_market(data: Any) -> Dict[str, Any]:
        """Normalize CoinCap market data"""
        items = []

        if isinstance(data, dict) and "data" in data:
            for asset in data["data"]:
                items.append(
                    {
                        "symbol": asset.get("symbol", "").upper(),
                        "name": asset.get("name", ""),
                        "price": float(asset.get("priceUsd", 0)),
                        "change_24h": float(asset.get("changePercent24Hr", 0)),
                        "volume_24h": float(asset.get("volumeUsd24Hr", 0)),
                        "market_cap": float(asset.get("marketCapUsd", 0)),
                        "rank": int(asset.get("rank", 0)),
                        "source": "coincap",
                    }
                )

        return {"last_updated": datetime.utcnow().isoformat() + "Z", "items": items}

    @staticmethod
    def _normalize_cmc_market(data: Any) -> Dict[str, Any]:
        """Normalize CoinMarketCap market data"""
        items = []

        if isinstance(data, dict) and "data" in data:
            for coin_id, coin in data["data"].items():
                items.append(
                    {
                        "symbol": coin.get("symbol", "").upper(),
                        "name": coin.get("name", ""),
                        "price": float(coin.get("quote", {}).get("USD", {}).get("price", 0)),
                        "change_24h": float(
                            coin.get("quote", {}).get("USD", {}).get("percent_change_24h", 0)
                        ),
                        "volume_24h": float(
                            coin.get("quote", {}).get("USD", {}).get("volume_24h", 0)
                        ),
                        "market_cap": float(
                            coin.get("quote", {}).get("USD", {}).get("market_cap", 0)
                        ),
                        "rank": int(coin.get("cmc_rank", 0)),
                        "source": "coinmarketcap",
                    }
                )

        return {"last_updated": datetime.utcnow().isoformat() + "Z", "items": items}

    @staticmethod
    def normalize_pairs(data: Any, provider: str) -> Dict[str, Any]:
        """
        Normalize trading pairs data

        Canonical format:
        {
            "pairs": [
                {
                    "pair": "BTCUSDT",
                    "base": "BTC",
                    "quote": "USDT",
                    "tick_size": 0.01,
                    "min_qty": 0.00001,
                    "source": "provider"
                }
            ],
            "total": 100,
            "page": 1
        }
        """
        try:
            if provider == "coingecko":
                # CoinGecko doesn't have direct pairs endpoint
                # Generate pairs from market data
                pairs = []
                if isinstance(data, list):
                    for coin in data[:100]:  # Limit to 100
                        symbol = coin.get("symbol", "").upper()
                        pairs.append(
                            {
                                "pair": f"{symbol}USD",
                                "base": symbol,
                                "quote": "USD",
                                "tick_size": 0.01,
                                "min_qty": 0.00001,
                                "source": "coingecko",
                            }
                        )

                return {"pairs": pairs, "total": len(pairs), "page": 1}

            elif provider == "binance":
                # Binance exchange info
                pairs = []
                if isinstance(data, dict) and "symbols" in data:
                    for symbol_info in data["symbols"]:
                        pairs.append(
                            {
                                "pair": symbol_info.get("symbol", ""),
                                "base": symbol_info.get("baseAsset", ""),
                                "quote": symbol_info.get("quoteAsset", ""),
                                "tick_size": float(
                                    symbol_info.get("filters", [{}])[0].get("tickSize", 0.01)
                                ),
                                "min_qty": float(
                                    symbol_info.get("filters", [{}])[1].get("minQty", 0.00001)
                                ),
                                "source": "binance",
                            }
                        )

                return {"pairs": pairs, "total": len(pairs), "page": 1}

            else:
                return {"pairs": [], "total": 0, "page": 1}

        except Exception as e:
            logger.error(f"Error normalizing pairs from {provider}: {e}")
            return {"pairs": [], "total": 0, "page": 1}

    @staticmethod
    def normalize_ohlc(data: Any, provider: str, symbol: str, interval: int) -> Dict[str, Any]:
        """
        Normalize OHLC data

        Canonical format:
        {
            "symbol": "BTC",
            "interval": 60,
            "items": [
                {
                    "ts": "ISO timestamp",
                    "open": 45000.0,
                    "high": 45500.0,
                    "low": 44800.0,
                    "close": 45200.0,
                    "volume": 1000.0
                }
            ]
        }
        """
        try:
            items = []

            if provider == "coingecko":
                # CoinGecko market_chart format
                if isinstance(data, dict) and "prices" in data:
                    for i, price_point in enumerate(data["prices"]):
                        timestamp_ms, price = price_point

                        # Try to get volume
                        volume = 0
                        if "total_volumes" in data and i < len(data["total_volumes"]):
                            volume = data["total_volumes"][i][1]

                        items.append(
                            {
                                "ts": datetime.fromtimestamp(timestamp_ms / 1000).isoformat() + "Z",
                                "open": price,
                                "high": price,
                                "low": price,
                                "close": price,
                                "volume": volume,
                            }
                        )

            elif provider == "binance":
                # Binance klines format
                if isinstance(data, list):
                    for candle in data:
                        items.append(
                            {
                                "ts": datetime.fromtimestamp(candle[0] / 1000).isoformat() + "Z",
                                "open": float(candle[1]),
                                "high": float(candle[2]),
                                "low": float(candle[3]),
                                "close": float(candle[4]),
                                "volume": float(candle[5]),
                            }
                        )

            return {"symbol": symbol.upper(), "interval": interval, "items": items}

        except Exception as e:
            logger.error(f"Error normalizing OHLC from {provider}: {e}")
            return {"symbol": symbol, "interval": interval, "items": []}

    @staticmethod
    def normalize_news(data: Any, provider: str) -> Dict[str, Any]:
        """
        Normalize news data

        Canonical format:
        {
            "articles": [
                {
                    "id": "unique_id",
                    "title": "News title",
                    "url": "https://...",
                    "summary": "Brief summary",
                    "source": "Source name",
                    "published_at": "ISO timestamp",
                    "sentiment": {
                        "label": "positive",
                        "score": 0.8
                    }
                }
            ],
            "total": 10
        }
        """
        try:
            articles = []

            if provider == "cryptopanic":
                if isinstance(data, dict) and "results" in data:
                    for post in data["results"]:
                        articles.append(
                            {
                                "id": str(post.get("id", "")),
                                "title": post.get("title", ""),
                                "url": post.get("url", ""),
                                "summary": post.get("title", "")[:200],
                                "source": post.get("source", {}).get("title", "CryptoPanic"),
                                "published_at": post.get(
                                    "published_at", datetime.utcnow().isoformat()
                                ),
                                "sentiment": None,
                            }
                        )

            elif provider == "reddit_crypto":
                if isinstance(data, dict) and "data" in data:
                    for post in data["data"].get("children", []):
                        post_data = post.get("data", {})
                        articles.append(
                            {
                                "id": post_data.get("id", ""),
                                "title": post_data.get("title", ""),
                                "url": f"https://reddit.com{post_data.get('permalink', '')}",
                                "summary": post_data.get("selftext", "")[:200],
                                "source": "Reddit",
                                "published_at": datetime.fromtimestamp(
                                    post_data.get("created_utc", 0)
                                ).isoformat()
                                + "Z",
                                "sentiment": None,
                            }
                        )

            return {"articles": articles, "total": len(articles)}

        except Exception as e:
            logger.error(f"Error normalizing news from {provider}: {e}")
            return {"articles": [], "total": 0}

    @staticmethod
    def normalize_sentiment(data: Any, provider: str) -> Dict[str, Any]:
        """
        Normalize sentiment data

        Canonical format:
        {
            "data": {
                "value": 45,
                "classification": "Fear",
                "timestamp": "ISO timestamp"
            }
        }
        """
        try:
            if provider == "alternative_me":
                if isinstance(data, dict) and "data" in data:
                    fng_data = data["data"][0] if data["data"] else {}
                    return {
                        "data": {
                            "value": int(fng_data.get("value", 50)),
                            "classification": fng_data.get("value_classification", "Neutral"),
                            "timestamp": datetime.fromtimestamp(
                                int(fng_data.get("timestamp", 0))
                            ).isoformat()
                            + "Z",
                        }
                    }

            return {
                "data": {
                    "value": 50,
                    "classification": "Neutral",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
            }

        except Exception as e:
            logger.error(f"Error normalizing sentiment from {provider}: {e}")
            return {
                "data": {
                    "value": 50,
                    "classification": "Neutral",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
            }

    @staticmethod
    def normalize_whale_transactions(data: Any, provider: str) -> Dict[str, Any]:
        """
        Normalize whale transaction data

        Canonical format:
        {
            "items": [
                {
                    "id": "unique_id",
                    "tx_hash": "0x...",
                    "chain": "ethereum",
                    "from": "address",
                    "to": "address",
                    "amount_usd": 1000000.0,
                    "token": "ETH",
                    "block": 12345678,
                    "tx_at": "ISO timestamp"
                }
            ]
        }
        """
        try:
            items = []

            if provider == "clankapp":
                # ClankApp format (assumed)
                if isinstance(data, list):
                    for tx in data:
                        items.append(
                            {
                                "id": tx.get("id", ""),
                                "tx_hash": tx.get("hash", ""),
                                "chain": tx.get("blockchain", "unknown").lower(),
                                "from": tx.get("from", ""),
                                "to": tx.get("to", ""),
                                "amount_usd": float(tx.get("amount_usd", 0)),
                                "token": tx.get("symbol", ""),
                                "block": int(tx.get("block_number", 0)),
                                "tx_at": tx.get("timestamp", datetime.utcnow().isoformat() + "Z"),
                            }
                        )

            return {"items": items}

        except Exception as e:
            logger.error(f"Error normalizing whale transactions from {provider}: {e}")
            return {"items": []}

    @staticmethod
    def normalize_gas_price(data: Any, provider: str, chain: str) -> Dict[str, Any]:
        """
        Normalize gas price data

        Canonical format:
        {
            "chain": "ethereum",
            "fast": 50.0,
            "standard": 40.0,
            "slow": 30.0,
            "unit": "Gwei"
        }
        """
        try:
            if provider.startswith("etherscan"):
                if isinstance(data, dict) and "result" in data:
                    result = data["result"]
                    return {
                        "chain": chain,
                        "fast": float(result.get("FastGasPrice", 0)),
                        "standard": float(result.get("ProposeGasPrice", 0)),
                        "slow": float(result.get("SafeGasPrice", 0)),
                        "unit": "Gwei",
                    }

            return {"chain": chain, "fast": 0, "standard": 0, "slow": 0, "unit": "Gwei"}

        except Exception as e:
            logger.error(f"Error normalizing gas price from {provider}: {e}")
            return {"chain": chain, "fast": 0, "standard": 0, "slow": 0, "unit": "Gwei"}


# Global normalizer instance
normalizer = DataNormalizer()
