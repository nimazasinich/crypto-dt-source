"""
Etherscan Provider - Ethereum blockchain transaction data

Provides:
- Address transaction history
- Token transfers
- Contract information
- Account balances

API Documentation: https://docs.etherscan.io/
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .base import BaseProvider, create_success_response, create_error_response


class EtherscanProvider(BaseProvider):
    """Etherscan REST API provider for Ethereum blockchain data"""

    # API Keys (temporary hardcoded - will be secured later)
    API_KEY_PRIMARY = "SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2"
    API_KEY_SECONDARY = "T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="etherscan",
            base_url="https://api.etherscan.io/api",
            api_key=api_key or self.API_KEY_PRIMARY,
            timeout=10.0,
            cache_ttl=30.0,
        )

    def _build_params(self, **kwargs) -> Dict[str, Any]:
        """Build request parameters with API key"""
        params = {"apikey": self.api_key}
        params.update({k: v for k, v in kwargs.items() if v is not None})
        return params

    async def get_transactions(
        self,
        address: str,
        start_block: int = 0,
        end_block: int = 99999999,
        page: int = 1,
        offset: int = 50,
        sort: str = "desc",
    ) -> Dict[str, Any]:
        """
        Get list of transactions for an address.

        Args:
            address: Ethereum address
            start_block: Starting block number
            end_block: Ending block number
            page: Page number for pagination
            offset: Number of transactions per page (max 10000)
            sort: Sort order ('asc' or 'desc')

        Returns:
            Standardized response with transaction list
        """
        if not address or not address.startswith("0x"):
            return create_error_response(
                self.name, "Invalid Ethereum address", "Address must start with '0x'"
            )

        params = self._build_params(
            module="account",
            action="txlist",
            address=address,
            startblock=start_block,
            endblock=end_block,
            page=page,
            offset=min(offset, 100),  # Limit for performance
            sort=sort,
        )

        response = await self.get("", params=params)

        if not response.get("success"):
            return response

        # Parse Etherscan response format
        data = response.get("data", {})
        status = data.get("status")
        message = data.get("message", "")

        # Status "1" means success, "0" can mean no data or error
        if status == "1" or (status == "0" and "No transactions found" in message):
            transactions = data.get("result", []) if status == "1" else []
            if isinstance(transactions, str):
                # API returned an error string instead of list
                return create_error_response(self.name, message, transactions)
            return create_success_response(
                self.name,
                {
                    "address": address,
                    "transactions": self._format_transactions(transactions),
                    "count": len(transactions),
                },
            )
        else:
            error_msg = message or "Unknown error"
            result_msg = data.get("result", "")
            if isinstance(result_msg, str) and result_msg:
                return create_error_response(self.name, error_msg, result_msg)
            return create_error_response(self.name, error_msg)

    def _format_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Format transaction data for clean output"""
        formatted = []
        for tx in transactions:
            formatted.append(
                {
                    "hash": tx.get("hash"),
                    "blockNumber": int(tx.get("blockNumber", 0)),
                    "timestamp": int(tx.get("timeStamp", 0)),
                    "from": tx.get("from"),
                    "to": tx.get("to"),
                    "value": tx.get("value"),
                    "valueEth": float(tx.get("value", 0)) / 1e18,
                    "gas": int(tx.get("gas", 0)),
                    "gasPrice": tx.get("gasPrice"),
                    "gasUsed": int(tx.get("gasUsed", 0)),
                    "isError": tx.get("isError") == "1",
                    "txreceipt_status": tx.get("txreceipt_status"),
                    "contractAddress": tx.get("contractAddress") or None,
                    "functionName": tx.get("functionName") or None,
                }
            )
        return formatted

    async def get_token_transfers(
        self, address: str, contract_address: Optional[str] = None, page: int = 1, offset: int = 50
    ) -> Dict[str, Any]:
        """
        Get ERC-20 token transfer events for an address.

        Args:
            address: Ethereum address
            contract_address: Optional token contract address filter
            page: Page number
            offset: Results per page
        """
        if not address or not address.startswith("0x"):
            return create_error_response(
                self.name, "Invalid Ethereum address", "Address must start with '0x'"
            )

        params = self._build_params(
            module="account",
            action="tokentx",
            address=address,
            page=page,
            offset=min(offset, 100),
            sort="desc",
        )

        if contract_address:
            params["contractaddress"] = contract_address

        response = await self.get("", params=params)

        if not response.get("success"):
            return response

        data = response.get("data", {})
        if data.get("status") == "1":
            transfers = data.get("result", [])
            return create_success_response(
                self.name,
                {
                    "address": address,
                    "transfers": self._format_token_transfers(transfers),
                    "count": len(transfers),
                },
            )
        else:
            error_msg = data.get("message", "Unknown error")
            if error_msg == "No transactions found":
                return create_success_response(
                    self.name, {"address": address, "transfers": [], "count": 0}
                )
            return create_error_response(self.name, error_msg)

    def _format_token_transfers(self, transfers: List[Dict]) -> List[Dict]:
        """Format token transfer data"""
        formatted = []
        for tx in transfers:
            decimals = int(tx.get("tokenDecimal", 18))
            value = int(tx.get("value", 0))
            formatted.append(
                {
                    "hash": tx.get("hash"),
                    "blockNumber": int(tx.get("blockNumber", 0)),
                    "timestamp": int(tx.get("timeStamp", 0)),
                    "from": tx.get("from"),
                    "to": tx.get("to"),
                    "value": str(value),
                    "tokenValue": value / (10**decimals) if decimals else value,
                    "tokenName": tx.get("tokenName"),
                    "tokenSymbol": tx.get("tokenSymbol"),
                    "tokenDecimal": decimals,
                    "contractAddress": tx.get("contractAddress"),
                }
            )
        return formatted

    async def get_balance(self, address: str) -> Dict[str, Any]:
        """Get ETH balance for an address"""
        if not address or not address.startswith("0x"):
            return create_error_response(
                self.name, "Invalid Ethereum address", "Address must start with '0x'"
            )

        params = self._build_params(
            module="account", action="balance", address=address, tag="latest"
        )

        response = await self.get("", params=params)

        if not response.get("success"):
            return response

        data = response.get("data", {})
        if data.get("status") == "1":
            balance_wei = int(data.get("result", 0))
            return create_success_response(
                self.name,
                {
                    "address": address,
                    "balance_wei": str(balance_wei),
                    "balance_eth": balance_wei / 1e18,
                },
            )
        else:
            return create_error_response(self.name, data.get("message", "Unknown error"))

    async def get_gas_price(self) -> Dict[str, Any]:
        """Get current gas price"""
        params = self._build_params(module="gastracker", action="gasoracle")

        response = await self.get("", params=params)

        if not response.get("success"):
            return response

        data = response.get("data", {})
        if data.get("status") == "1":
            result = data.get("result", {})
            return create_success_response(
                self.name,
                {
                    "safeGasPrice": result.get("SafeGasPrice"),
                    "proposeGasPrice": result.get("ProposeGasPrice"),
                    "fastGasPrice": result.get("FastGasPrice"),
                    "suggestBaseFee": result.get("suggestBaseFee"),
                    "gasUsedRatio": result.get("gasUsedRatio"),
                },
            )
        else:
            return create_error_response(self.name, data.get("message", "Unknown error"))
