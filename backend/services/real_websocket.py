#!/usr/bin/env python3
"""
Real WebSocket Service - ZERO MOCK DATA
All WebSocket data is REAL from external APIs
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Set

from fastapi import WebSocket, WebSocketDisconnect

from backend.services.real_api_clients import blockchain_client, cmc_client, news_client

logger = logging.getLogger(__name__)


class RealWebSocketManager:
    """
    Real-time WebSocket Manager
    Broadcasts REAL data only - NO MOCK DATA
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # client_id -> set of channels
        self.update_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """
        Connect new WebSocket client
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()

        logger.info(f"✅ WebSocket client connected: {client_id}")

        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connected",
                "client_id": client_id,
                "message": "Connected to Real Data WebSocket",
                "timestamp": datetime.utcnow().isoformat(),
            },
            client_id,
        )

    async def disconnect(self, client_id: str):
        """
        Disconnect WebSocket client
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        if client_id in self.subscriptions:
            del self.subscriptions[client_id]

        # Cancel any running update tasks for this client
        if client_id in self.update_tasks:
            self.update_tasks[client_id].cancel()
            del self.update_tasks[client_id]

        logger.info(f"❌ WebSocket client disconnected: {client_id}")

    async def subscribe(self, client_id: str, channels: list):
        """
        Subscribe client to channels for REAL data updates
        """
        if client_id not in self.subscriptions:
            self.subscriptions[client_id] = set()

        for channel in channels:
            self.subscriptions[client_id].add(channel)

        logger.info(f"✅ Client {client_id} subscribed to: {channels}")

        # Start sending real data for subscribed channels
        await self.send_initial_data(client_id, channels)

        # Start real-time updates
        if client_id not in self.update_tasks:
            self.update_tasks[client_id] = asyncio.create_task(
                self.send_realtime_updates(client_id)
            )

    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """
        Send message to specific client
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"❌ Failed to send message to {client_id}: {e}")
                await self.disconnect(client_id)

    async def broadcast(self, channel: str, data: Dict[str, Any]):
        """
        Broadcast REAL data to all subscribers of a channel
        """
        message = {
            "type": "update",
            "channel": channel,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        disconnected_clients = []

        for client_id, channels in self.subscriptions.items():
            if channel in channels and client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_json(message)
                except Exception as e:
                    logger.error(f"❌ Failed to broadcast to {client_id}: {e}")
                    disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)

    async def send_initial_data(self, client_id: str, channels: list):
        """
        Send initial REAL data for subscribed channels
        """
        for channel in channels:
            try:
                data = await self.fetch_real_data_for_channel(channel)
                await self.send_personal_message(
                    {
                        "type": "initial_data",
                        "channel": channel,
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    client_id,
                )
            except Exception as e:
                logger.error(f"❌ Failed to fetch initial data for {channel}: {e}")

    async def send_realtime_updates(self, client_id: str):
        """
        Send real-time REAL data updates to client
        """
        try:
            while client_id in self.active_connections:
                # Get subscribed channels
                channels = self.subscriptions.get(client_id, set())

                # Fetch and send real data for each channel
                for channel in channels:
                    try:
                        data = await self.fetch_real_data_for_channel(channel)
                        await self.send_personal_message(
                            {
                                "type": "update",
                                "channel": channel,
                                "data": data,
                                "timestamp": datetime.utcnow().isoformat(),
                            },
                            client_id,
                        )
                    except Exception as e:
                        logger.error(f"❌ Update failed for {channel}: {e}")

                # Wait before next update (adjust based on channel type)
                await asyncio.sleep(30)  # Update every 30 seconds

        except asyncio.CancelledError:
            logger.info(f"Update task cancelled for client {client_id}")
        except Exception as e:
            logger.error(f"❌ Update task error for {client_id}: {e}")

    async def fetch_real_data_for_channel(self, channel: str) -> Dict[str, Any]:
        """
        Fetch REAL data for a WebSocket channel
        NO FAKE DATA ALLOWED
        """
        if channel.startswith("market."):
            # Market data channel
            symbol = channel.split(".")[1] if len(channel.split(".")) > 1 else None

            if symbol:
                # Get real quote for specific symbol
                quotes = await cmc_client.get_quotes([symbol])
                quote_data = quotes.get("data", {}).get(symbol, {})

                if quote_data:
                    usd_quote = quote_data.get("quote", {}).get("USD", {})
                    return {
                        "symbol": symbol,
                        "price": usd_quote.get("price", 0),
                        "change_24h": usd_quote.get("percent_change_24h", 0),
                        "volume_24h": usd_quote.get("volume_24h", 0),
                        "market_cap": usd_quote.get("market_cap", 0),
                        "source": "coinmarketcap",
                    }
            else:
                # Get top market data
                market_data = await cmc_client.get_latest_listings(limit=10)
                return {"tickers": market_data.get("data", []), "source": "coinmarketcap"}

        elif channel.startswith("news."):
            # News channel
            symbol = channel.split(".")[1] if len(channel.split(".")) > 1 else "crypto"
            news_data = await news_client.get_crypto_news(symbol=symbol, limit=5)
            return {"articles": news_data.get("articles", []), "source": "newsapi"}

        elif channel.startswith("blockchain."):
            # Blockchain data channel
            chain = channel.split(".")[1] if len(channel.split(".")) > 1 else "ethereum"

            if chain == "ethereum":
                tx_data = await blockchain_client.get_ethereum_transactions(limit=10)
            elif chain == "bsc":
                tx_data = await blockchain_client.get_bsc_transactions(limit=10)
            elif chain == "tron":
                tx_data = await blockchain_client.get_tron_transactions(limit=10)
            else:
                tx_data = {"transactions": [], "source": "unknown"}

            return tx_data

        elif channel == "system.status":
            # System status channel
            return {
                "status": "operational",
                "active_connections": len(self.active_connections),
                "timestamp": datetime.utcnow().isoformat(),
            }

        else:
            # Unknown channel
            return {
                "error": f"Unknown channel: {channel}",
                "timestamp": datetime.utcnow().isoformat(),
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get WebSocket manager statistics
        """
        return {
            "active_connections": len(self.active_connections),
            "total_subscriptions": sum(len(subs) for subs in self.subscriptions.values()),
            "channels": list(set().union(*self.subscriptions.values())),
            "timestamp": datetime.utcnow().isoformat(),
        }


# Global instance
ws_manager = RealWebSocketManager()


# Export
__all__ = ["RealWebSocketManager", "ws_manager"]
