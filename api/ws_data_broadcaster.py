import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from backend.orchestration.provider_manager import provider_manager
from backend.services.ws_service_manager import ws_manager, ServiceType
from utils.logger import setup_logger

logger = setup_logger("ws_data_broadcaster")

class DataBroadcaster:
    """
    Broadcasts cryptocurrency data updates to WebSocket clients
    using the Provider Orchestrator for data fetching.
    """

    def __init__(self):
        """Initialize the broadcaster"""
        self.last_broadcast = {}
        self.broadcast_interval = 5  # seconds for price updates
        self.is_running = False
        logger.info("DataBroadcaster initialized")

    async def start_broadcasting(self):
        """Start all broadcast tasks"""
        logger.info("Starting WebSocket data broadcaster...")

        self.is_running = True

        tasks = [
            self.broadcast_market_data(),
            self.broadcast_news(),
            self.broadcast_sentiment(),
            self.broadcast_gas_prices()
        ]

        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in broadcasting tasks: {e}", exc_info=True)
        finally:
            self.is_running = False

    async def stop_broadcasting(self):
        """Stop broadcasting"""
        logger.info("Stopping WebSocket data broadcaster...")
        self.is_running = False

    async def broadcast_market_data(self):
        """Broadcast market price updates"""
        logger.info("Starting market data broadcast...")

        while self.is_running:
            try:
                # Use Orchestrator to fetch market data
                # Using 30s TTL to prevent provider spam, but broadcast often
                response = await provider_manager.fetch_data(
                    "market",
                    params={"ids": "bitcoin,ethereum,tron,solana,binancecoin,ripple", "vs_currency": "usd"},
                    use_cache=True,
                    ttl=10 # Short TTL for live prices if provider allows
                )

                if response["success"] and response["data"]:
                    coins = response["data"]
                    
                    # Format data for broadcast
                    prices = {}
                    price_changes = {}
                    volumes = {}
                    market_caps = {}
                    
                    for coin in coins:
                        symbol = coin.get("symbol", "").upper()
                        prices[symbol] = coin.get("current_price")
                        price_changes[symbol] = coin.get("price_change_percentage_24h")
                        volumes[symbol] = coin.get("total_volume")
                        market_caps[symbol] = coin.get("market_cap")

                    data = {
                        "type": "market_data",
                        "data": {
                            "prices": prices,
                            "volumes": volumes,
                            "market_caps": market_caps,
                            "price_changes": price_changes
                        },
                        "count": len(coins),
                        "timestamp": datetime.utcnow().isoformat(),
                        "source": response["source"]
                    }

                    # Diff check could be here (optimization)

                    # Broadcast to subscribed clients
                    await ws_manager.broadcast_to_service(ServiceType.MARKET_DATA, data)
                    logger.debug(f"Broadcasted {len(coins)} price updates from {response['source']}")

            except Exception as e:
                logger.error(f"Error broadcasting market data: {e}", exc_info=True)

            await asyncio.sleep(self.broadcast_interval)

    async def broadcast_news(self):
        """Broadcast news updates"""
        logger.info("Starting news broadcast...")
        
        while self.is_running:
            try:
                response = await provider_manager.fetch_data(
                    "news",
                    params={"filter": "hot"},
                    use_cache=True,
                    ttl=300
                )

                if response["success"] and response["data"]:
                    # Transform/Normalize
                    data = response["data"]
                    articles = []
                    
                    if "results" in data: # CryptoPanic
                        for post in data.get('results', [])[:5]:
                            articles.append({
                                "id": str(post.get('id')),
                                "title": post.get('title', ''),
                                "source": post.get('source', {}).get('title', 'Unknown'),
                                "url": post.get('url', ''),
                                "published_at": post.get('published_at', datetime.now().isoformat())
                            })
                    elif "articles" in data: # NewsAPI
                        for post in data.get('articles', [])[:5]:
                            articles.append({
                                "id": str(hash(post.get('url', ''))),
                                "title": post.get('title', ''),
                                "source": post.get('source', {}).get('name', 'Unknown'),
                                "url": post.get('url', ''),
                                "published_at": post.get('publishedAt', datetime.now().isoformat())
                            })

                    if articles:
                        payload = {
                            "type": "news",
                            "data": {"articles": articles},
                            "count": len(articles),
                            "timestamp": datetime.utcnow().isoformat(),
                            "source": response["source"]
                        }

                        await ws_manager.broadcast_to_service(ServiceType.NEWS, payload)
                        logger.info(f"Broadcasted {len(articles)} news articles from {response['source']}")

            except Exception as e:
                logger.error(f"Error broadcasting news: {e}", exc_info=True)

            await asyncio.sleep(60)

    async def broadcast_sentiment(self):
        """Broadcast sentiment updates"""
        logger.info("Starting sentiment broadcast...")

        while self.is_running:
            try:
                response = await provider_manager.fetch_data(
                    "sentiment",
                    params={"limit": 1},
                    use_cache=True,
                    ttl=3600
                )

                if response["success"] and response["data"]:
                    data = response["data"]
                    fng_value = 50
                    classification = "Neutral"
                    
                    if data.get('data'):
                        item = data['data'][0]
                        fng_value = int(item.get('value', 50))
                        classification = item.get('value_classification', 'Neutral')

                    payload = {
                        "type": "sentiment",
                        "data": {
                            "fear_greed_index": fng_value,
                            "classification": classification,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                        "source": response["source"]
                    }

                    await ws_manager.broadcast_to_service(ServiceType.SENTIMENT, payload)
                    logger.info(f"Broadcasted sentiment: {fng_value} from {response['source']}")

            except Exception as e:
                logger.error(f"Error broadcasting sentiment: {e}", exc_info=True)

            await asyncio.sleep(60)

    async def broadcast_gas_prices(self):
        """Broadcast gas price updates"""
        logger.info("Starting gas price broadcast...")

        while self.is_running:
            try:
                response = await provider_manager.fetch_data(
                    "onchain",
                    params={},
                    use_cache=True,
                    ttl=15
                )

                if response["success"] and response["data"]:
                    data = response["data"]
                    result = data.get("result", {})
                    
                    if result:
                        payload = {
                            "type": "gas_prices",
                            "data": {
                                "fast": result.get("FastGasPrice"),
                                "standard": result.get("ProposeGasPrice"),
                                "slow": result.get("SafeGasPrice")
                            },
                            "timestamp": datetime.utcnow().isoformat(),
                            "source": response["source"]
                        }

                        # Broadcast to RPC_NODES service type (gas prices are blockchain-related)
                        await ws_manager.broadcast_to_service(ServiceType.RPC_NODES, payload)
                        logger.debug(f"Broadcasted gas prices from {response['source']}")

            except Exception as e:
                logger.error(f"Error broadcasting gas prices: {e}", exc_info=True)

            await asyncio.sleep(30)


# Global broadcaster instance
broadcaster = DataBroadcaster()
