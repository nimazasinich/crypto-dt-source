#!/usr/bin/env python3
"""
On-Chain Data Aggregator - Uses ALL Free On-Chain Resources
Maximizes usage of all available free blockchain explorers and analytics
"""

import httpx
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class OnChainAggregator:
    """
    Aggregates on-chain data from ALL free sources:
    Block Explorers:
    - Etherscan (with keys)
    - Blockchair (free tier)
    - Blockscout (free, open source)
    - BscScan (with key)
    - TronScan (with key)
    
    Public RPC Nodes:
    - Ankr (ETH, BSC, Polygon)
    - PublicNode (ETH, BSC, Polygon)
    - Cloudflare ETH
    - LlamaNodes
    - 1RPC
    - dRPC
    - BSC Official nodes
    - TronGrid
    - Polygon Official
    """
    
    def __init__(self):
        self.timeout = 15.0
        
        # Block Explorer APIs with keys
        self.explorers = {
            "ethereum": {
                "etherscan": {
                    "base_url": "https://api.etherscan.io/api",
                    "api_key": "SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2",
                    "priority": 1
                },
                "etherscan_backup": {
                    "base_url": "https://api.etherscan.io/api",
                    "api_key": "T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45",
                    "priority": 2
                },
                "blockchair": {
                    "base_url": "https://api.blockchair.com/ethereum",
                    "api_key": None,  # Free tier, no key needed
                    "priority": 3
                },
                "blockscout": {
                    "base_url": "https://eth.blockscout.com/api",
                    "api_key": None,
                    "priority": 4
                }
            },
            "bsc": {
                "bscscan": {
                    "base_url": "https://api.bscscan.com/api",
                    "api_key": "K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT",
                    "priority": 1
                },
                "blockchair": {
                    "base_url": "https://api.blockchair.com/binance-smart-chain",
                    "api_key": None,
                    "priority": 2
                }
            },
            "tron": {
                "tronscan": {
                    "base_url": "https://apilist.tronscanapi.com/api",
                    "api_key": "7ae72726-bffe-4e74-9c33-97b761eeea21",
                    "priority": 1
                },
                "blockchair": {
                    "base_url": "https://api.blockchair.com/tron",
                    "api_key": None,
                    "priority": 2
                }
            }
        }
        
        # Free Public RPC Nodes
        self.rpc_nodes = {
            "ethereum": [
                "https://rpc.ankr.com/eth",
                "https://ethereum.publicnode.com",
                "https://ethereum-rpc.publicnode.com",
                "https://cloudflare-eth.com",
                "https://eth.llamarpc.com",
                "https://1rpc.io/eth",
                "https://eth.drpc.org"
            ],
            "bsc": [
                "https://bsc-dataseed.binance.org",
                "https://bsc-dataseed1.defibit.io",
                "https://bsc-dataseed1.ninicoin.io",
                "https://rpc.ankr.com/bsc",
                "https://bsc-rpc.publicnode.com"
            ],
            "polygon": [
                "https://polygon-rpc.com",
                "https://rpc.ankr.com/polygon",
                "https://polygon-bor-rpc.publicnode.com"
            ],
            "tron": [
                "https://api.trongrid.io",
                "https://api.tronstack.io"
            ]
        }
    
    async def get_address_balance(
        self,
        address: str,
        chain: str = "ethereum"
    ) -> Dict[str, Any]:
        """
        Get address balance from ALL available explorers with fallback
        """
        chain = chain.lower()
        
        if chain not in self.explorers:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported chain: {chain}. Supported: {list(self.explorers.keys())}"
            )
        
        # Try all explorers for the chain
        explorers = sorted(
            self.explorers[chain].items(),
            key=lambda x: x[1]["priority"]
        )
        
        for explorer_name, explorer_config in explorers:
            try:
                if "etherscan" in explorer_name or "bscscan" in explorer_name:
                    balance_data = await self._get_balance_etherscan_like(
                        address, explorer_config
                    )
                elif "blockchair" in explorer_name:
                    balance_data = await self._get_balance_blockchair(
                        address, explorer_config
                    )
                elif "blockscout" in explorer_name:
                    balance_data = await self._get_balance_blockscout(
                        address, explorer_config
                    )
                elif "tronscan" in explorer_name:
                    balance_data = await self._get_balance_tronscan(
                        address, explorer_config
                    )
                else:
                    continue
                
                if balance_data:
                    logger.info(f"✅ {explorer_name.upper()} ({chain}): Successfully fetched balance")
                    return balance_data
                    
            except Exception as e:
                logger.warning(f"⚠️ {explorer_name.upper()} failed: {e}")
                continue
        
        raise HTTPException(
            status_code=503,
            detail=f"All {chain} explorers failed for address {address}"
        )
    
    async def get_gas_price(self, chain: str = "ethereum") -> Dict[str, Any]:
        """
        Get current gas price from explorers or RPC nodes
        """
        chain = chain.lower()
        
        # Try explorer APIs first (Etherscan-like)
        if chain in self.explorers:
            explorers = sorted(
                self.explorers[chain].items(),
                key=lambda x: x[1]["priority"]
            )
            
            for explorer_name, explorer_config in explorers:
                try:
                    if "etherscan" in explorer_name or "bscscan" in explorer_name:
                        gas_data = await self._get_gas_etherscan_like(explorer_config)
                        if gas_data:
                            logger.info(f"✅ {explorer_name.upper()}: Successfully fetched gas price")
                            return gas_data
                except Exception as e:
                    logger.warning(f"⚠️ {explorer_name} gas price failed: {e}")
                    continue
        
        # Try RPC nodes
        if chain in self.rpc_nodes:
            for rpc_url in self.rpc_nodes[chain]:
                try:
                    gas_data = await self._get_gas_rpc(rpc_url, chain)
                    if gas_data:
                        logger.info(f"✅ RPC ({rpc_url}): Successfully fetched gas price")
                        return gas_data
                except Exception as e:
                    logger.warning(f"⚠️ RPC {rpc_url} failed: {e}")
                    continue
        
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch gas price for {chain}"
        )
    
    async def get_transactions(
        self,
        address: str,
        chain: str = "ethereum",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get transaction history for an address
        """
        chain = chain.lower()
        
        if chain not in self.explorers:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported chain: {chain}"
            )
        
        # Try all explorers
        explorers = sorted(
            self.explorers[chain].items(),
            key=lambda x: x[1]["priority"]
        )
        
        for explorer_name, explorer_config in explorers:
            try:
                if "etherscan" in explorer_name or "bscscan" in explorer_name:
                    tx_data = await self._get_transactions_etherscan_like(
                        address, explorer_config, limit
                    )
                elif "tronscan" in explorer_name:
                    tx_data = await self._get_transactions_tronscan(
                        address, explorer_config, limit
                    )
                else:
                    continue
                
                if tx_data:
                    logger.info(f"✅ {explorer_name.upper()}: Fetched {len(tx_data)} transactions")
                    return tx_data
                    
            except Exception as e:
                logger.warning(f"⚠️ {explorer_name} transactions failed: {e}")
                continue
        
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch transactions for {address} on {chain}"
        )
    
    # Etherscan-like API implementations
    async def _get_balance_etherscan_like(
        self,
        address: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get balance from Etherscan-like API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {
                "module": "account",
                "action": "balance",
                "address": address,
                "tag": "latest"
            }
            
            if config["api_key"]:
                params["apikey"] = config["api_key"]
            
            response = await client.get(config["base_url"], params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "1" and data.get("result"):
                # Convert wei to ether (for ETH/BNB)
                balance_wei = int(data["result"])
                balance_ether = balance_wei / 1e18
                
                return {
                    "address": address,
                    "balance": balance_ether,
                    "balance_wei": balance_wei,
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                }
            
            raise Exception(f"API returned error: {data.get('message', 'Unknown error')}")
    
    async def _get_gas_etherscan_like(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get gas price from Etherscan-like API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {
                "module": "gastracker",
                "action": "gasoracle"
            }
            
            if config["api_key"]:
                params["apikey"] = config["api_key"]
            
            response = await client.get(config["base_url"], params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "1" and data.get("result"):
                result = data["result"]
                return {
                    "safe_gas_price": float(result.get("SafeGasPrice", 0)),
                    "propose_gas_price": float(result.get("ProposeGasPrice", 0)),
                    "fast_gas_price": float(result.get("FastGasPrice", 0)),
                    "unit": "gwei",
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                }
            
            raise Exception("Failed to fetch gas price")
    
    async def _get_transactions_etherscan_like(
        self,
        address: str,
        config: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get transactions from Etherscan-like API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "sort": "desc",
                "page": 1,
                "offset": limit
            }
            
            if config["api_key"]:
                params["apikey"] = config["api_key"]
            
            response = await client.get(config["base_url"], params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "1" and data.get("result"):
                transactions = []
                for tx in data["result"]:
                    transactions.append({
                        "hash": tx.get("hash", ""),
                        "from": tx.get("from", ""),
                        "to": tx.get("to", ""),
                        "value": int(tx.get("value", 0)) / 1e18,
                        "gas_used": int(tx.get("gasUsed", 0)),
                        "gas_price": int(tx.get("gasPrice", 0)) / 1e9,
                        "timestamp": int(tx.get("timeStamp", 0)) * 1000,
                        "block_number": int(tx.get("blockNumber", 0)),
                        "status": "success" if tx.get("txreceipt_status") == "1" else "failed"
                    })
                
                return transactions
            
            return []
    
    # Blockchair implementation
    async def _get_balance_blockchair(
        self,
        address: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get balance from Blockchair"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = f"{config['base_url']}/dashboards/address/{address}"
            
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get("data") and address in data["data"]:
                addr_data = data["data"][address]["address"]
                
                return {
                    "address": address,
                    "balance": float(addr_data.get("balance", 0)) / 1e18,
                    "balance_wei": int(addr_data.get("balance", 0)),
                    "transaction_count": addr_data.get("transaction_count", 0),
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                }
            
            raise Exception("Address not found in Blockchair")
    
    # Blockscout implementation
    async def _get_balance_blockscout(
        self,
        address: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get balance from Blockscout"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {
                "module": "account",
                "action": "balance",
                "address": address
            }
            
            response = await client.get(config["base_url"], params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result"):
                balance_wei = int(data["result"])
                
                return {
                    "address": address,
                    "balance": balance_wei / 1e18,
                    "balance_wei": balance_wei,
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                }
            
            raise Exception("Failed to fetch balance from Blockscout")
    
    # TronScan implementation
    async def _get_balance_tronscan(
        self,
        address: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get balance from TronScan"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = f"{config['base_url']}/account"
            params = {"address": address}
            
            if config["api_key"]:
                params["apiKey"] = config["api_key"]
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data:
                balance_sun = data.get("balance", 0)
                
                return {
                    "address": address,
                    "balance": balance_sun / 1e6,  # Convert SUN to TRX
                    "balance_sun": balance_sun,
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                }
            
            raise Exception("Failed to fetch balance from TronScan")
    
    async def _get_transactions_tronscan(
        self,
        address: str,
        config: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get transactions from TronScan"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = f"{config['base_url']}/transaction"
            params = {"address": address, "limit": limit}
            
            if config["api_key"]:
                params["apiKey"] = config["api_key"]
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            transactions = []
            for tx in data.get("data", []):
                transactions.append({
                    "hash": tx.get("hash", ""),
                    "from": tx.get("ownerAddress", ""),
                    "to": tx.get("toAddress", ""),
                    "value": tx.get("amount", 0) / 1e6,
                    "timestamp": tx.get("timestamp", 0),
                    "status": "success" if tx.get("contractRet") == "SUCCESS" else "failed"
                })
            
            return transactions
    
    # RPC implementation
    async def _get_gas_rpc(self, rpc_url: str, chain: str) -> Dict[str, Any]:
        """Get gas price from RPC node"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_gasPrice",
                "params": [],
                "id": 1
            }
            
            response = await client.post(rpc_url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result"):
                gas_price_wei = int(data["result"], 16)
                gas_price_gwei = gas_price_wei / 1e9
                
                return {
                    "gas_price": gas_price_gwei,
                    "unit": "gwei",
                    "chain": chain,
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                }
            
            raise Exception("Failed to fetch gas price from RPC")


# Global instance
onchain_aggregator = OnChainAggregator()

__all__ = ["OnChainAggregator", "onchain_aggregator"]

