#!/usr/bin/env python3
"""
BSCScan API Client - Binance Smart Chain blockchain explorer
Official API: https://bscscan.com/apis
"""

import httpx
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# BSCScan API Key from .env.example
BSCSCAN_API_KEY = os.getenv("BSCSCAN_KEY", "K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT")


class BSCScanClient:
    """
    BSCScan API Client - BNB Smart Chain data
    """
    
    def __init__(self, api_key: str = BSCSCAN_API_KEY):
        self.base_url = "https://api.bscscan.com/api"
        self.api_key = api_key
        self.timeout = 15.0
    
    async def get_bnb_price(self) -> Dict[str, Any]:
        """
        Get current BNB price in USD
        
        Returns:
            BNB price data
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "module": "stats",
                        "action": "bnbprice",
                        "apikey": self.api_key
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "1":
                    result_data = data.get("result", {})
                    price_usd = float(result_data.get("ethusd", 0))
                    
                    result = {
                        "symbol": "BNB",
                        "price": price_usd,
                        "currency": "USD",
                        "timestamp": result_data.get("ethusd_timestamp", datetime.utcnow().isoformat()),
                        "source": "BSCScan"
                    }
                    
                    logger.info(f"✅ BSCScan: Fetched BNB price: ${price_usd}")
                    return result
                else:
                    error_msg = data.get('message', 'Unknown error')
                    # Log as warning if it's just an API key issue, don't crash
                    # BSCScan API key issues are non-critical - other providers will be used
                    if "NOTOK" in str(data.get('status', '')) or "Invalid API Key" in error_msg:
                        logger.info(f"ℹ️ BSCScan API key not configured or rate limited - using alternative providers")
                        raise Exception(f"BSCScan unavailable")
                    else:
                        raise Exception(f"BSCScan API error: {error_msg}")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ BSCScan API HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ BSCScan API failed: {e}")
            raise
    
    async def get_bsc_supply(self) -> Dict[str, Any]:
        """
        Get BNB total and circulating supply
        
        Returns:
            Supply data
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "module": "stats",
                        "action": "bnbsupply",
                        "apikey": self.api_key
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "1":
                    supply = float(data.get("result", 0))
                    
                    logger.info(f"✅ BSCScan: Fetched BNB supply: {supply}")
                    return {
                        "symbol": "BNB",
                        "supply": supply,
                        "source": "BSCScan",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    raise Exception(f"BSCScan supply error: {data.get('message', 'Unknown error')}")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ BSCScan supply HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ BSCScan supply failed: {e}")
            raise
    
    async def get_gas_oracle(self) -> Dict[str, Any]:
        """
        Get BSC gas oracle (gas prices)
        
        Returns:
            Gas price data
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "module": "gastracker",
                        "action": "gasoracle",
                        "apikey": self.api_key
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "1":
                    result_data = data.get("result", {})
                    
                    logger.info(f"✅ BSCScan: Fetched gas oracle data")
                    return {
                        "safe_gas_price": result_data.get("SafeGasPrice", "0"),
                        "propose_gas_price": result_data.get("ProposeGasPrice", "0"),
                        "fast_gas_price": result_data.get("FastGasPrice", "0"),
                        "suggested_base_fee": result_data.get("suggestBaseFee", "0"),
                        "gas_used_ratio": result_data.get("gasUsedRatio", "0"),
                        "chain": "BSC",
                        "source": "BSCScan",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    raise Exception(f"BSCScan gas oracle error: {data.get('message', 'Unknown error')}")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ BSCScan gas oracle HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ BSCScan gas oracle failed: {e}")
            raise
    
    async def get_token_info(self, contract_address: str) -> Dict[str, Any]:
        """
        Get BEP-20 token information
        
        Args:
            contract_address: Token contract address
        
        Returns:
            Token info
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "module": "token",
                        "action": "tokeninfo",
                        "contractaddress": contract_address,
                        "apikey": self.api_key
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "1":
                    result_data = data.get("result", [{}])[0]
                    
                    logger.info(f"✅ BSCScan: Fetched token info for {contract_address}")
                    return {
                        "contract_address": contract_address,
                        "token_name": result_data.get("tokenName", ""),
                        "symbol": result_data.get("symbol", ""),
                        "decimals": result_data.get("decimals", ""),
                        "total_supply": result_data.get("totalSupply", ""),
                        "source": "BSCScan",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    raise Exception(f"BSCScan token info error: {data.get('message', 'Unknown error')}")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ BSCScan token info HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ BSCScan token info failed: {e}")
            raise


# Global instance
bscscan_client = BSCScanClient()


# Standalone functions
async def fetch_bnb_price() -> float:
    """Get BNB price from BSCScan"""
    try:
        data = await bscscan_client.get_bnb_price()
        return data.get("price", 0)
    except:
        return 0


async def fetch_bsc_gas_prices() -> Dict[str, Any]:
    """Get BSC gas prices"""
    return await bscscan_client.get_gas_oracle()


__all__ = ["BSCScanClient", "bscscan_client", "fetch_bnb_price", "fetch_bsc_gas_prices"]
