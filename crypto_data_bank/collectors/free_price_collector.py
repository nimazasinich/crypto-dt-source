#!/usr/bin/env python3
"""
جمع‌آوری قیمت‌های رایگان بدون نیاز به API Key
Free Price Collectors - NO API KEY REQUIRED
"""

import asyncio
import httpx
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FreePriceCollector:
    """جمع‌آوری قیمت‌های رایگان از منابع بدون کلید API"""

    def __init__(self):
        self.timeout = httpx.Timeout(15.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }

    async def collect_from_coincap(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """
        CoinCap.io - Completely FREE, no API key needed
        https://coincap.io - Public API
        """
        try:
            url = "https://api.coincap.io/v2/assets"
            params = {"limit": 100}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()
                    assets = data.get("data", [])

                    results = []
                    for asset in assets:
                        if symbols and asset['symbol'].upper() not in [s.upper() for s in symbols]:
                            continue

                        results.append({
                            "symbol": asset['symbol'],
                            "name": asset['name'],
                            "price": float(asset['priceUsd']),
                            "priceUsd": float(asset['priceUsd']),
                            "change24h": float(asset.get('changePercent24Hr', 0)),
                            "volume24h": float(asset.get('volumeUsd24Hr', 0)),
                            "marketCap": float(asset.get('marketCapUsd', 0)),
                            "rank": int(asset.get('rank', 0)),
                            "source": "coincap.io",
                            "timestamp": datetime.now().isoformat()
                        })

                    logger.info(f"✅ CoinCap: Collected {len(results)} prices")
                    return results
                else:
                    logger.warning(f"⚠️ CoinCap returned status {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"❌ CoinCap error: {e}")
            return []

    async def collect_from_coingecko(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """
        CoinGecko - FREE tier, no API key for basic requests
        Rate limit: 10-30 calls/minute (free tier)
        """
        try:
            # Map common symbols to CoinGecko IDs
            symbol_to_id = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "SOL": "solana",
                "BNB": "binancecoin",
                "XRP": "ripple",
                "ADA": "cardano",
                "DOGE": "dogecoin",
                "MATIC": "matic-network",
                "DOT": "polkadot",
                "AVAX": "avalanche-2"
            }

            # Get coin IDs
            if symbols:
                coin_ids = [symbol_to_id.get(s.upper(), s.lower()) for s in symbols]
            else:
                coin_ids = list(symbol_to_id.values())[:10]  # Top 10

            ids_param = ",".join(coin_ids)

            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": ids_param,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true",
                "include_market_cap": "true"
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()

                    results = []
                    id_to_symbol = {v: k for k, v in symbol_to_id.items()}

                    for coin_id, coin_data in data.items():
                        symbol = id_to_symbol.get(coin_id, coin_id.upper())

                        results.append({
                            "symbol": symbol,
                            "name": coin_id.replace("-", " ").title(),
                            "price": coin_data.get('usd', 0),
                            "priceUsd": coin_data.get('usd', 0),
                            "change24h": coin_data.get('usd_24h_change', 0),
                            "volume24h": coin_data.get('usd_24h_vol', 0),
                            "marketCap": coin_data.get('usd_market_cap', 0),
                            "source": "coingecko.com",
                            "timestamp": datetime.now().isoformat()
                        })

                    logger.info(f"✅ CoinGecko: Collected {len(results)} prices")
                    return results
                else:
                    logger.warning(f"⚠️ CoinGecko returned status {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"❌ CoinGecko error: {e}")
            return []

    async def collect_from_binance_public(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """
        Binance PUBLIC API - NO API KEY NEEDED
        Only public market data endpoints
        """
        try:
            # Get 24h ticker for all symbols
            url = "https://api.binance.com/api/v3/ticker/24hr"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()

                    results = []
                    for ticker in data:
                        symbol = ticker['symbol']

                        # Filter for USDT pairs only
                        if not symbol.endswith('USDT'):
                            continue

                        base_symbol = symbol.replace('USDT', '')

                        # Filter by requested symbols
                        if symbols and base_symbol not in [s.upper() for s in symbols]:
                            continue

                        results.append({
                            "symbol": base_symbol,
                            "name": base_symbol,
                            "price": float(ticker['lastPrice']),
                            "priceUsd": float(ticker['lastPrice']),
                            "change24h": float(ticker['priceChangePercent']),
                            "volume24h": float(ticker['quoteVolume']),
                            "high24h": float(ticker['highPrice']),
                            "low24h": float(ticker['lowPrice']),
                            "source": "binance.com",
                            "timestamp": datetime.now().isoformat()
                        })

                    logger.info(f"✅ Binance Public: Collected {len(results)} prices")
                    return results[:100]  # Limit to top 100
                else:
                    logger.warning(f"⚠️ Binance returned status {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"❌ Binance error: {e}")
            return []

    async def collect_from_kraken_public(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """
        Kraken PUBLIC API - NO API KEY NEEDED
        """
        try:
            # Get ticker for major pairs
            pairs = ["XXBTZUSD", "XETHZUSD", "SOLUSD", "ADAUSD", "DOTUSD"]

            url = "https://api.kraken.com/0/public/Ticker"
            params = {"pair": ",".join(pairs)}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()

                    if data.get('error') and data['error']:
                        logger.warning(f"⚠️ Kraken API error: {data['error']}")
                        return []

                    result_data = data.get('result', {})
                    results = []

                    # Map Kraken pairs to standard symbols
                    pair_to_symbol = {
                        "XXBTZUSD": "BTC",
                        "XETHZUSD": "ETH",
                        "SOLUSD": "SOL",
                        "ADAUSD": "ADA",
                        "DOTUSD": "DOT"
                    }

                    for pair_name, ticker in result_data.items():
                        # Find matching pair
                        symbol = None
                        for kraken_pair, sym in pair_to_symbol.items():
                            if kraken_pair in pair_name:
                                symbol = sym
                                break

                        if not symbol:
                            continue

                        if symbols and symbol not in [s.upper() for s in symbols]:
                            continue

                        last_price = float(ticker['c'][0])
                        volume_24h = float(ticker['v'][1])

                        results.append({
                            "symbol": symbol,
                            "name": symbol,
                            "price": last_price,
                            "priceUsd": last_price,
                            "volume24h": volume_24h,
                            "high24h": float(ticker['h'][1]),
                            "low24h": float(ticker['l'][1]),
                            "source": "kraken.com",
                            "timestamp": datetime.now().isoformat()
                        })

                    logger.info(f"✅ Kraken Public: Collected {len(results)} prices")
                    return results
                else:
                    logger.warning(f"⚠️ Kraken returned status {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"❌ Kraken error: {e}")
            return []

    async def collect_from_cryptocompare(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        """
        CryptoCompare - FREE tier available
        Min-API with no registration needed
        """
        try:
            if not symbols:
                symbols = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "MATIC", "DOT", "AVAX"]

            fsyms = ",".join([s.upper() for s in symbols])

            url = "https://min-api.cryptocompare.com/data/pricemultifull"
            params = {
                "fsyms": fsyms,
                "tsyms": "USD"
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()

                    if "RAW" not in data:
                        return []

                    results = []
                    for symbol, currency_data in data["RAW"].items():
                        usd_data = currency_data.get("USD", {})

                        results.append({
                            "symbol": symbol,
                            "name": symbol,
                            "price": usd_data.get("PRICE", 0),
                            "priceUsd": usd_data.get("PRICE", 0),
                            "change24h": usd_data.get("CHANGEPCT24HOUR", 0),
                            "volume24h": usd_data.get("VOLUME24HOURTO", 0),
                            "marketCap": usd_data.get("MKTCAP", 0),
                            "high24h": usd_data.get("HIGH24HOUR", 0),
                            "low24h": usd_data.get("LOW24HOUR", 0),
                            "source": "cryptocompare.com",
                            "timestamp": datetime.now().isoformat()
                        })

                    logger.info(f"✅ CryptoCompare: Collected {len(results)} prices")
                    return results
                else:
                    logger.warning(f"⚠️ CryptoCompare returned status {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"❌ CryptoCompare error: {e}")
            return []

    async def collect_all_free_sources(self, symbols: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """
        جمع‌آوری از همه منابع رایگان به صورت همزمان
        Collect from ALL free sources simultaneously
        """
        logger.info("🚀 Starting collection from ALL free sources...")

        tasks = [
            self.collect_from_coincap(symbols),
            self.collect_from_coingecko(symbols),
            self.collect_from_binance_public(symbols),
            self.collect_from_kraken_public(symbols),
            self.collect_from_cryptocompare(symbols),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "coincap": results[0] if not isinstance(results[0], Exception) else [],
            "coingecko": results[1] if not isinstance(results[1], Exception) else [],
            "binance": results[2] if not isinstance(results[2], Exception) else [],
            "kraken": results[3] if not isinstance(results[3], Exception) else [],
            "cryptocompare": results[4] if not isinstance(results[4], Exception) else [],
        }

    def aggregate_prices(self, all_sources: Dict[str, List[Dict]]) -> List[Dict]:
        """
        ترکیب قیمت‌ها از منابع مختلف
        Aggregate prices from multiple sources (take average, median, or most recent)
        """
        symbol_prices = {}

        for source_name, prices in all_sources.items():
            for price_data in prices:
                symbol = price_data['symbol']

                if symbol not in symbol_prices:
                    symbol_prices[symbol] = []

                symbol_prices[symbol].append({
                    "source": source_name,
                    "price": price_data.get('price', 0),
                    "data": price_data
                })

        # Calculate aggregated prices
        aggregated = []
        for symbol, price_list in symbol_prices.items():
            if not price_list:
                continue

            prices = [p['price'] for p in price_list if p['price'] > 0]
            if not prices:
                continue

            # Use median price for better accuracy
            sorted_prices = sorted(prices)
            median_price = sorted_prices[len(sorted_prices) // 2]

            # Get most complete data entry
            best_data = max(price_list, key=lambda x: len(x['data']))['data']
            best_data['price'] = median_price
            best_data['priceUsd'] = median_price
            best_data['sources_count'] = len(price_list)
            best_data['sources'] = [p['source'] for p in price_list]
            best_data['aggregated'] = True

            aggregated.append(best_data)

        logger.info(f"📊 Aggregated {len(aggregated)} unique symbols from multiple sources")
        return aggregated


async def main():
    """Test the free collectors"""
    collector = FreePriceCollector()

    print("\n" + "="*70)
    print("🧪 Testing FREE Price Collectors (No API Keys)")
    print("="*70)

    # Test individual sources
    symbols = ["BTC", "ETH", "SOL"]

    print("\n1️⃣ Testing CoinCap...")
    coincap_data = await collector.collect_from_coincap(symbols)
    print(f"   Got {len(coincap_data)} prices from CoinCap")

    print("\n2️⃣ Testing CoinGecko...")
    coingecko_data = await collector.collect_from_coingecko(symbols)
    print(f"   Got {len(coingecko_data)} prices from CoinGecko")

    print("\n3️⃣ Testing Binance Public API...")
    binance_data = await collector.collect_from_binance_public(symbols)
    print(f"   Got {len(binance_data)} prices from Binance")

    print("\n4️⃣ Testing Kraken Public API...")
    kraken_data = await collector.collect_from_kraken_public(symbols)
    print(f"   Got {len(kraken_data)} prices from Kraken")

    print("\n5️⃣ Testing CryptoCompare...")
    cryptocompare_data = await collector.collect_from_cryptocompare(symbols)
    print(f"   Got {len(cryptocompare_data)} prices from CryptoCompare")

    # Test all sources at once
    print("\n\n" + "="*70)
    print("🚀 Testing ALL Sources Simultaneously")
    print("="*70)

    all_data = await collector.collect_all_free_sources(symbols)

    total = sum(len(v) for v in all_data.values())
    print(f"\n✅ Total prices collected: {total}")
    for source, data in all_data.items():
        print(f"   {source}: {len(data)} prices")

    # Test aggregation
    print("\n" + "="*70)
    print("📊 Testing Price Aggregation")
    print("="*70)

    aggregated = collector.aggregate_prices(all_data)
    print(f"\n✅ Aggregated to {len(aggregated)} unique symbols")

    for price in aggregated[:5]:
        print(f"   {price['symbol']}: ${price['price']:,.2f} (from {price['sources_count']} sources)")


if __name__ == "__main__":
    asyncio.run(main())
