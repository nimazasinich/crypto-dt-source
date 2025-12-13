#!/usr/bin/env python3
"""
Tronscan API Client - TRON blockchain explorer
Official API: https://tronscan.org/
"""

import httpx
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Tronscan API Key from .env.example
TRONSCAN_API_KEY = os.getenv("TRONSCAN_KEY", "7ae72726-bffe-4e74-9c33-97b761eeea21")


class TronscanClient:
    """
    Tronscan API Client - TRON network data
    """
    
    def __init__(self, api_key: str = TRONSCAN_API_KEY):
        # Updated to correct Tronscan API endpoint
        self.base_url = "https://apilist.tronscanapi.com/api"
        self.fallback_url = "https://api.tronscan.org/api"
        self.api_key = api_key
        self.timeout = 15.0
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key"""
        return {
            "TRON-PRO-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def get_trx_price(self) -> Dict[str, Any]:
        """
        Get current TRX price with fallback endpoints
        
        Returns:
            TRX price data
        """
        # Try multiple endpoints
        endpoints = [
            f"{self.base_url}/market/tokens/trx",
            f"{self.fallback_url}/market/tokens/trx",
            f"{self.base_url}/token/price?token=trx"
        ]
        
        last_error = None
        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(endpoint, headers=self._get_headers())
                    response.raise_for_status()
                    data = response.json()
                
                    # Tronscan returns price data in various formats
                    if isinstance(data, dict):
                        # Try different response formats
                        price_usd = float(
                            data.get("priceInUsd") or 
                            data.get("price_in_usd") or 
                            data.get("price") or 
                            (data.get("data", {}).get("priceInUsd") if isinstance(data.get("data"), dict) else 0) or 
                            0
                        )
                        
                        if price_usd > 0:
                            result = {
                                "symbol": "TRX",
                                "price": price_usd,
                                "currency": "USD",
                                "change_24h": data.get("change24h", 0),
                                "volume_24h": data.get("volume24h", 0),
                                "market_cap": data.get("marketCap", 0),
                                "source": "Tronscan",
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            
                            logger.info(f"✅ Tronscan: Fetched TRX price: ${price_usd}")
                            return result
            
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code} at {endpoint}"
                logger.warning(f"⚠️ Tronscan endpoint failed: {last_error}")
                continue
            except Exception as e:
                last_error = str(e)
                logger.warning(f"⚠️ Tronscan endpoint failed: {last_error}")
                continue
        
        # All endpoints failed
        logger.error(f"❌ Tronscan API failed (all endpoints): {last_error}")
        raise Exception(f"Tronscan API unavailable: {last_error}")
    
    async def get_network_stats(self) -> Dict[str, Any]:
        """
        Get TRON network statistics
        
        Returns:
            Network stats
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/system/status",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ Tronscan: Fetched network stats")
                return {
                    "total_accounts": data.get("totalAccounts", 0),
                    "total_transactions": data.get("totalTransaction", 0),
                    "total_blocks": data.get("totalBlockCount", 0),
                    "tps": data.get("currentTps", 0),
                    "total_nodes": data.get("totalNodes", 0),
                    "chain": "TRON",
                    "source": "Tronscan",
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Tronscan network stats HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ Tronscan network stats failed: {e}")
            raise
    
    async def get_token_info(self, token_address: str) -> Dict[str, Any]:
        """
        Get TRC-20 token information
        
        Args:
            token_address: Token contract address
        
        Returns:
            Token info
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/token",
                    params={"id": token_address},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                
                if isinstance(data, dict) and "data" in data:
                    token_data = data.get("data", [{}])[0] if isinstance(data.get("data"), list) else data.get("data", {})
                    
                    logger.info(f"✅ Tronscan: Fetched token info for {token_address}")
                    return {
                        "address": token_address,
                        "name": token_data.get("name", ""),
                        "symbol": token_data.get("symbol", ""),
                        "decimals": token_data.get("decimals", 0),
                        "total_supply": token_data.get("totalSupply", ""),
                        "holders": token_data.get("nrOfTokenHolders", 0),
                        "source": "Tronscan",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    raise Exception("Tronscan: Token not found")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Tronscan token info HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ Tronscan token info failed: {e}")
            raise


# Global instance
tronscan_client = TronscanClient()


# Standalone functions
async def fetch_trx_price() -> float:
    """Get TRX price from Tronscan"""
    try:
        data = await tronscan_client.get_trx_price()
        return data.get("price", 0)
    except:
        return 0


async def fetch_tron_network_stats() -> Dict[str, Any]:
    """Get TRON network statistics"""
    return await tronscan_client.get_network_stats()


__all__ = ["TronscanClient", "tronscan_client", "fetch_trx_price", "fetch_tron_network_stats"]
