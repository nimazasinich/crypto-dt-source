#!/usr/bin/env python3
"""
جمع‌آوری احساسات بازار از منابع رایگان
Free Market Sentiment Collectors - NO API KEY
"""

import asyncio
import httpx
from typing import Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentCollector:
    """جمع‌آوری احساسات بازار از منابع رایگان"""

    def __init__(self):
        self.timeout = httpx.Timeout(15.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }

    async def collect_fear_greed_index(self) -> Optional[Dict]:
        """
        Alternative.me Crypto Fear & Greed Index
        FREE - No API key needed
        """
        try:
            url = "https://api.alternative.me/fng/"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()

                    if "data" in data and data["data"]:
                        fng = data["data"][0]

                        result = {
                            "fear_greed_value": int(fng.get("value", 50)),
                            "fear_greed_classification": fng.get("value_classification", "Neutral"),
                            "timestamp_fng": fng.get("timestamp"),
                            "source": "alternative.me",
                            "timestamp": datetime.now().isoformat()
                        }

                        logger.info(f"✅ Fear & Greed: {result['fear_greed_value']} ({result['fear_greed_classification']})")
                        return result
                    else:
                        logger.warning("⚠️ Fear & Greed API returned no data")
                        return None
                else:
                    logger.warning(f"⚠️ Fear & Greed returned status {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"❌ Fear & Greed error: {e}")
            return None

    async def collect_bitcoin_dominance(self) -> Optional[Dict]:
        """
        Bitcoin Dominance from CoinCap
        FREE - No API key needed
        """
        try:
            url = "https://api.coincap.io/v2/assets"
            params = {"limit": 10}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()
                    assets = data.get("data", [])

                    if not assets:
                        return None

                    # Calculate total market cap
                    total_market_cap = sum(
                        float(asset.get("marketCapUsd", 0))
                        for asset in assets
                        if asset.get("marketCapUsd")
                    )

                    # Get Bitcoin market cap
                    btc = next((a for a in assets if a["symbol"] == "BTC"), None)
                    if not btc:
                        return None

                    btc_market_cap = float(btc.get("marketCapUsd", 0))

                    # Calculate dominance
                    btc_dominance = (btc_market_cap / total_market_cap * 100) if total_market_cap > 0 else 0

                    result = {
                        "btc_dominance": round(btc_dominance, 2),
                        "btc_market_cap": btc_market_cap,
                        "total_market_cap": total_market_cap,
                        "source": "coincap.io",
                        "timestamp": datetime.now().isoformat()
                    }

                    logger.info(f"✅ BTC Dominance: {result['btc_dominance']}%")
                    return result
                else:
                    logger.warning(f"⚠️ CoinCap returned status {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"❌ BTC Dominance error: {e}")
            return None

    async def collect_global_market_stats(self) -> Optional[Dict]:
        """
        Global Market Statistics from CoinGecko
        FREE - No API key for this endpoint
        """
        try:
            url = "https://api.coingecko.com/api/v3/global"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()
                    global_data = data.get("data", {})

                    if not global_data:
                        return None

                    result = {
                        "total_market_cap_usd": global_data.get("total_market_cap", {}).get("usd", 0),
                        "total_volume_24h_usd": global_data.get("total_volume", {}).get("usd", 0),
                        "btc_dominance": global_data.get("market_cap_percentage", {}).get("btc", 0),
                        "eth_dominance": global_data.get("market_cap_percentage", {}).get("eth", 0),
                        "active_cryptocurrencies": global_data.get("active_cryptocurrencies", 0),
                        "markets": global_data.get("markets", 0),
                        "market_cap_change_24h": global_data.get("market_cap_change_percentage_24h_usd", 0),
                        "source": "coingecko.com",
                        "timestamp": datetime.now().isoformat()
                    }

                    logger.info(f"✅ Global Stats: ${result['total_market_cap_usd']:,.0f} market cap")
                    return result
                else:
                    logger.warning(f"⚠️ CoinGecko global returned status {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"❌ Global Stats error: {e}")
            return None

    async def calculate_market_sentiment(
        self,
        fear_greed: Optional[Dict],
        btc_dominance: Optional[Dict],
        global_stats: Optional[Dict]
    ) -> Dict:
        """
        محاسبه احساسات کلی بازار
        Calculate overall market sentiment from multiple indicators
        """
        sentiment_score = 50  # Neutral default
        confidence = 0.0
        indicators_count = 0

        sentiment_signals = []

        # Fear & Greed contribution (40% weight)
        if fear_greed:
            fg_value = fear_greed.get("fear_greed_value", 50)
            sentiment_score += (fg_value - 50) * 0.4
            confidence += 0.4
            indicators_count += 1

            sentiment_signals.append({
                "indicator": "fear_greed",
                "value": fg_value,
                "signal": fear_greed.get("fear_greed_classification")
            })

        # BTC Dominance contribution (30% weight)
        if btc_dominance:
            dom_value = btc_dominance.get("btc_dominance", 45)

            # Higher BTC dominance = more fearful (people moving to "safe" crypto)
            # Lower BTC dominance = more greedy (people buying altcoins)
            dom_score = 100 - dom_value  # Inverse relationship
            sentiment_score += (dom_score - 50) * 0.3
            confidence += 0.3
            indicators_count += 1

            sentiment_signals.append({
                "indicator": "btc_dominance",
                "value": dom_value,
                "signal": "Defensive" if dom_value > 50 else "Risk-On"
            })

        # Market Cap Change contribution (30% weight)
        if global_stats:
            mc_change = global_stats.get("market_cap_change_24h", 0)

            # Positive change = bullish, negative = bearish
            mc_score = 50 + (mc_change * 5)  # Scale: -10% change = 0, +10% = 100
            mc_score = max(0, min(100, mc_score))  # Clamp to 0-100

            sentiment_score += (mc_score - 50) * 0.3
            confidence += 0.3
            indicators_count += 1

            sentiment_signals.append({
                "indicator": "market_cap_change_24h",
                "value": mc_change,
                "signal": "Bullish" if mc_change > 0 else "Bearish"
            })

        # Normalize sentiment score to 0-100
        sentiment_score = max(0, min(100, sentiment_score))

        # Determine overall classification
        if sentiment_score >= 75:
            classification = "Extreme Greed"
        elif sentiment_score >= 60:
            classification = "Greed"
        elif sentiment_score >= 45:
            classification = "Neutral"
        elif sentiment_score >= 25:
            classification = "Fear"
        else:
            classification = "Extreme Fear"

        return {
            "overall_sentiment": classification,
            "sentiment_score": round(sentiment_score, 2),
            "confidence": round(confidence, 2),
            "indicators_used": indicators_count,
            "signals": sentiment_signals,
            "fear_greed_value": fear_greed.get("fear_greed_value") if fear_greed else None,
            "fear_greed_classification": fear_greed.get("fear_greed_classification") if fear_greed else None,
            "btc_dominance": btc_dominance.get("btc_dominance") if btc_dominance else None,
            "market_cap_change_24h": global_stats.get("market_cap_change_24h") if global_stats else None,
            "source": "aggregated",
            "timestamp": datetime.now().isoformat()
        }

    async def collect_all_sentiment_data(self) -> Dict:
        """
        جمع‌آوری همه داده‌های احساسات
        Collect ALL sentiment data and calculate overall sentiment
        """
        logger.info("🚀 Starting collection of sentiment data...")

        # Collect all data in parallel
        fear_greed, btc_dom, global_stats = await asyncio.gather(
            self.collect_fear_greed_index(),
            self.collect_bitcoin_dominance(),
            self.collect_global_market_stats(),
            return_exceptions=True
        )

        # Handle exceptions
        fear_greed = fear_greed if not isinstance(fear_greed, Exception) else None
        btc_dom = btc_dom if not isinstance(btc_dom, Exception) else None
        global_stats = global_stats if not isinstance(global_stats, Exception) else None

        # Calculate overall sentiment
        overall_sentiment = await self.calculate_market_sentiment(
            fear_greed,
            btc_dom,
            global_stats
        )

        return {
            "fear_greed": fear_greed,
            "btc_dominance": btc_dom,
            "global_stats": global_stats,
            "overall_sentiment": overall_sentiment
        }


async def main():
    """Test the sentiment collectors"""
    collector = SentimentCollector()

    print("\n" + "="*70)
    print("🧪 Testing FREE Sentiment Collectors")
    print("="*70)

    # Test individual collectors
    print("\n1️⃣ Testing Fear & Greed Index...")
    fg = await collector.collect_fear_greed_index()
    if fg:
        print(f"   Value: {fg['fear_greed_value']}/100")
        print(f"   Classification: {fg['fear_greed_classification']}")

    print("\n2️⃣ Testing Bitcoin Dominance...")
    btc_dom = await collector.collect_bitcoin_dominance()
    if btc_dom:
        print(f"   BTC Dominance: {btc_dom['btc_dominance']}%")
        print(f"   BTC Market Cap: ${btc_dom['btc_market_cap']:,.0f}")

    print("\n3️⃣ Testing Global Market Stats...")
    global_stats = await collector.collect_global_market_stats()
    if global_stats:
        print(f"   Total Market Cap: ${global_stats['total_market_cap_usd']:,.0f}")
        print(f"   24h Volume: ${global_stats['total_volume_24h_usd']:,.0f}")
        print(f"   24h Change: {global_stats['market_cap_change_24h']:.2f}%")

    # Test comprehensive sentiment
    print("\n\n" + "="*70)
    print("📊 Testing Comprehensive Sentiment Analysis")
    print("="*70)

    all_data = await collector.collect_all_sentiment_data()

    overall = all_data["overall_sentiment"]
    print(f"\n✅ Overall Market Sentiment: {overall['overall_sentiment']}")
    print(f"   Sentiment Score: {overall['sentiment_score']}/100")
    print(f"   Confidence: {overall['confidence']:.0%}")
    print(f"   Indicators Used: {overall['indicators_used']}")

    print("\n📊 Individual Signals:")
    for signal in overall.get("signals", []):
        print(f"   • {signal['indicator']}: {signal['value']} ({signal['signal']})")


if __name__ == "__main__":
    asyncio.run(main())
