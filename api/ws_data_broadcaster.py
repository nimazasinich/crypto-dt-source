"""
WebSocket Data Broadcaster
Broadcasts real-time cryptocurrency data from database to connected clients
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

from backend.services.ws_service_manager import ServiceType, ws_manager
from database.db_manager import db_manager
from utils.logger import setup_logger

logger = setup_logger("ws_data_broadcaster")


class DataBroadcaster:
    """
    Broadcasts cryptocurrency data updates to WebSocket clients
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
            self.broadcast_whales(),
            self.broadcast_gas_prices(),
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
                prices = db_manager.get_latest_prices(limit=50)

                if prices:
                    # Format data for broadcast
                    data = {
                        "type": "market_data",
                        "data": {
                            "prices": {p.symbol: p.price_usd for p in prices},
                            "volumes": {p.symbol: p.volume_24h for p in prices if p.volume_24h},
                            "market_caps": {p.symbol: p.market_cap for p in prices if p.market_cap},
                            "price_changes": {
                                p.symbol: p.price_change_24h for p in prices if p.price_change_24h
                            },
                        },
                        "count": len(prices),
                        "timestamp": datetime.utcnow().isoformat(),
                    }

                    # Broadcast to subscribed clients
                    await ws_manager.broadcast_to_service(ServiceType.MARKET_DATA, data)
                    logger.debug(f"Broadcasted {len(prices)} price updates")

            except Exception as e:
                logger.error(f"Error broadcasting market data: {e}", exc_info=True)

            await asyncio.sleep(self.broadcast_interval)

    async def broadcast_news(self):
        """Broadcast news updates"""
        logger.info("Starting news broadcast...")
        last_news_id = 0

        while self.is_running:
            try:
                news = db_manager.get_latest_news(limit=10)

                if news and (not last_news_id or news[0].id != last_news_id):
                    # New news available
                    last_news_id = news[0].id

                    data = {
                        "type": "news",
                        "data": {
                            "articles": [
                                {
                                    "id": article.id,
                                    "title": article.title,
                                    "source": article.source,
                                    "url": article.url,
                                    "published_at": article.published_at.isoformat(),
                                    "sentiment": article.sentiment,
                                }
                                for article in news[:5]  # Only send 5 latest
                            ]
                        },
                        "count": len(news[:5]),
                        "timestamp": datetime.utcnow().isoformat(),
                    }

                    await ws_manager.broadcast_to_service(ServiceType.NEWS, data)
                    logger.info(f"Broadcasted {len(news[:5])} news articles")

            except Exception as e:
                logger.error(f"Error broadcasting news: {e}", exc_info=True)

            await asyncio.sleep(30)  # Check every 30 seconds

    async def broadcast_sentiment(self):
        """Broadcast sentiment updates"""
        logger.info("Starting sentiment broadcast...")
        last_sentiment_value = None

        while self.is_running:
            try:
                sentiment = db_manager.get_latest_sentiment()

                if sentiment and sentiment.value != last_sentiment_value:
                    last_sentiment_value = sentiment.value

                    data = {
                        "type": "sentiment",
                        "data": {
                            "fear_greed_index": sentiment.value,
                            "classification": sentiment.classification,
                            "metric_name": sentiment.metric_name,
                            "source": sentiment.source,
                            "timestamp": sentiment.timestamp.isoformat(),
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    }

                    await ws_manager.broadcast_to_service(ServiceType.SENTIMENT, data)
                    logger.info(
                        f"Broadcasted sentiment: {sentiment.value} ({sentiment.classification})"
                    )

            except Exception as e:
                logger.error(f"Error broadcasting sentiment: {e}", exc_info=True)

            await asyncio.sleep(60)  # Check every minute

    async def broadcast_whales(self):
        """Broadcast whale transaction updates"""
        logger.info("Starting whale transaction broadcast...")
        last_whale_id = 0

        while self.is_running:
            try:
                whales = db_manager.get_whale_transactions(limit=5)

                if whales and (not last_whale_id or whales[0].id != last_whale_id):
                    last_whale_id = whales[0].id

                    data = {
                        "type": "whale_transaction",
                        "data": {
                            "transactions": [
                                {
                                    "id": tx.id,
                                    "blockchain": tx.blockchain,
                                    "amount_usd": tx.amount_usd,
                                    "from_address": tx.from_address[:20] + "...",
                                    "to_address": tx.to_address[:20] + "...",
                                    "timestamp": tx.timestamp.isoformat(),
                                }
                                for tx in whales
                            ]
                        },
                        "count": len(whales),
                        "timestamp": datetime.utcnow().isoformat(),
                    }

                    await ws_manager.broadcast_to_service(ServiceType.WHALE_TRACKING, data)
                    logger.info(f"Broadcasted {len(whales)} whale transactions")

            except Exception as e:
                logger.error(f"Error broadcasting whales: {e}", exc_info=True)

            await asyncio.sleep(15)  # Check every 15 seconds

    async def broadcast_gas_prices(self):
        """Broadcast gas price updates"""
        logger.info("Starting gas price broadcast...")

        while self.is_running:
            try:
                gas_prices = db_manager.get_latest_gas_prices()

                if gas_prices:
                    data = {
                        "type": "gas_prices",
                        "data": gas_prices,
                        "timestamp": datetime.utcnow().isoformat(),
                    }

                    # Broadcast to RPC_NODES service type (gas prices are blockchain-related)
                    await ws_manager.broadcast_to_service(ServiceType.RPC_NODES, data)
                    logger.debug("Broadcasted gas prices")

            except Exception as e:
                logger.error(f"Error broadcasting gas prices: {e}", exc_info=True)

            await asyncio.sleep(30)  # Every 30 seconds


# Global broadcaster instance
broadcaster = DataBroadcaster()
