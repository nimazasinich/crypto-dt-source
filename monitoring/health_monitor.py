"""
Health Monitoring System for API Providers
"""

import asyncio
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from config import config
from database.db import get_db
from database.models import ConnectionAttempt, Provider, ProviderStatusEnum, StatusEnum
from utils.http_client import APIClient

logger = logging.getLogger(__name__)


class HealthMonitor:
    def __init__(self):
        self.running = False

    async def start(self):
        """Start health monitoring loop"""
        self.running = True
        logger.info("Health monitoring started")

        while self.running:
            try:
                await self.check_all_providers()
                await asyncio.sleep(config.HEALTH_CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(10)

    async def check_all_providers(self):
        """Check health of all providers"""
        with get_db() as db:
            providers = db.query(Provider).filter(Provider.priority_tier <= 2).all()

            async with APIClient() as client:
                tasks = [self.check_provider(client, provider, db) for provider in providers]
                await asyncio.gather(*tasks, return_exceptions=True)

    async def check_provider(self, client: APIClient, provider: Provider, db: Session):
        """Check health of a single provider"""
        try:
            # Build health check endpoint
            endpoint = self.get_health_endpoint(provider)
            headers = self.get_headers(provider)

            # Make request
            result = await client.get(endpoint, headers=headers)

            # Determine status
            status = (
                StatusEnum.SUCCESS
                if result["success"] and result["status_code"] == 200
                else StatusEnum.FAILED
            )

            # Log attempt
            attempt = ConnectionAttempt(
                provider_id=provider.id,
                timestamp=datetime.utcnow(),
                endpoint=endpoint,
                status=status,
                response_time_ms=result["response_time_ms"],
                http_status_code=result["status_code"],
                error_type=result["error"]["type"] if result["error"] else None,
                error_message=result["error"]["message"] if result["error"] else None,
                retry_count=0,
            )
            db.add(attempt)

            # Update provider status
            provider.last_response_time_ms = result["response_time_ms"]
            provider.last_check_at = datetime.utcnow()

            # Calculate overall status
            recent_attempts = (
                db.query(ConnectionAttempt)
                .filter(ConnectionAttempt.provider_id == provider.id)
                .order_by(ConnectionAttempt.timestamp.desc())
                .limit(5)
                .all()
            )

            success_count = sum(1 for a in recent_attempts if a.status == StatusEnum.SUCCESS)

            if success_count == 5:
                provider.status = ProviderStatusEnum.ONLINE
            elif success_count >= 3:
                provider.status = ProviderStatusEnum.DEGRADED
            else:
                provider.status = ProviderStatusEnum.OFFLINE

            db.commit()

            logger.info(
                f"Health check for {provider.name}: {status.value} ({result['response_time_ms']}ms)"
            )

        except Exception as e:
            logger.error(f"Health check failed for {provider.name}: {e}")

    def get_health_endpoint(self, provider: Provider) -> str:
        """Get health check endpoint for provider"""
        endpoints = {
            "CoinGecko": f"{provider.endpoint_url}/ping",
            "CoinMarketCap": f"{provider.endpoint_url}/cryptocurrency/map?limit=1",
            "Etherscan": f"{provider.endpoint_url}?module=stats&action=ethsupply&apikey={config.API_KEYS['etherscan'][0] if config.API_KEYS['etherscan'] else ''}",
            "BscScan": f"{provider.endpoint_url}?module=stats&action=bnbsupply&apikey={config.API_KEYS['bscscan'][0] if config.API_KEYS['bscscan'] else ''}",
            "TronScan": f"{provider.endpoint_url}/system/status",
            "CryptoPanic": f"{provider.endpoint_url}/posts/?auth_token=free&public=true",
            "Alternative.me": f"{provider.endpoint_url}/fng/",
            "CryptoCompare": f"{provider.endpoint_url}/price?fsym=BTC&tsyms=USD",
            "Binance": f"{provider.endpoint_url}/ping",
            "NewsAPI": f"{provider.endpoint_url}/news?language=en&category=technology",
            "The Graph": "https://api.thegraph.com/index-node/graphql",
            "Blockchair": f"{provider.endpoint_url}/bitcoin/stats",
        }

        return endpoints.get(provider.name, provider.endpoint_url)

    def get_headers(self, provider: Provider) -> dict:
        """Get headers for provider"""
        headers = {"User-Agent": "CryptoMonitor/1.0"}

        if provider.name == "CoinMarketCap" and config.API_KEYS["coinmarketcap"]:
            headers["X-CMC_PRO_API_KEY"] = config.API_KEYS["coinmarketcap"][0]
        elif provider.name == "TronScan" and config.API_KEYS["tronscan"]:
            headers["TRON-PRO-API-KEY"] = config.API_KEYS["tronscan"][0]
        elif provider.name == "CryptoCompare" and config.API_KEYS["cryptocompare"]:
            headers["authorization"] = f"Apikey {config.API_KEYS['cryptocompare'][0]}"
        elif provider.name == "NewsAPI" and config.API_KEYS["newsapi"]:
            headers["X-ACCESS-KEY"] = config.API_KEYS["newsapi"][0]

        return headers

    def stop(self):
        """Stop health monitoring"""
        self.running = False
        logger.info("Health monitoring stopped")


# Global instance
health_monitor = HealthMonitor()
