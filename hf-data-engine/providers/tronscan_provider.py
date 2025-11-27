"""
TronScan Provider - TRON blockchain transaction data

Provides:
- TRON address transaction history
- TRC-20 token transfers
- Account information
- Contract data

API Documentation: https://docs.tronscan.org/
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import BaseProvider, create_error_response, create_success_response


class TronscanProvider(BaseProvider):
    """TronScan REST API provider for TRON blockchain data"""

    # API Key (temporary hardcoded - will be secured later)
    API_KEY = "7ae72726-bffe-4e74-9c33-97b761eeea21"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="tronscan",
            base_url="https://apilist.tronscanapi.com/api",
            api_key=api_key or self.API_KEY,
            timeout=10.0,
            cache_ttl=30.0,
        )

    def _get_default_headers(self) -> Dict[str, str]:
        """Get headers with TronScan API key"""
        return {
            "Accept": "application/json",
            "User-Agent": "HF-Crypto-Data-Engine/1.0",
            "TRON-PRO-API-KEY": self.api_key,
        }

    async def get_transactions(
        self, address: str, start: int = 0, limit: int = 50, sort: str = "-timestamp"
    ) -> Dict[str, Any]:
        """
        Get list of transactions for a TRON address.

        Args:
            address: TRON address (starts with 'T')
            start: Starting index for pagination
            limit: Number of transactions to fetch
            sort: Sort order ('-timestamp' for descending)

        Returns:
            Standardized response with transaction list
        """
        if not address:
            return create_error_response(self.name, "Invalid TRON address", "Address is required")

        # Validate TRON address format (base58, starts with T)
        if not address.startswith("T"):
            return create_error_response(
                self.name, "Invalid TRON address format", "TRON address should start with 'T'"
            )

        params = {"address": address, "start": start, "limit": min(limit, 50), "sort": sort}

        response = await self.get("transaction", params=params)

        if not response.get("success"):
            return response

        data = response.get("data", {})

        # TronScan returns data in different format
        if isinstance(data, dict):
            transactions = data.get("data", [])
            total = data.get("total", 0)
        else:
            transactions = data if isinstance(data, list) else []
            total = len(transactions)

        return create_success_response(
            self.name,
            {
                "address": address,
                "chain": "tron",
                "transactions": self._format_transactions(transactions),
                "count": len(transactions),
                "total": total,
            },
        )

    def _format_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Format TRON transaction data for clean output"""
        formatted = []
        for tx in transactions:
            # Handle amount which could be string or int
            raw_amount = tx.get("amount", 0)
            try:
                amount = int(raw_amount) if raw_amount else 0
            except (ValueError, TypeError):
                amount = 0

            formatted.append(
                {
                    "hash": tx.get("hash") or tx.get("txID"),
                    "block": tx.get("block"),
                    "timestamp": tx.get("timestamp"),
                    "ownerAddress": tx.get("ownerAddress"),
                    "toAddress": tx.get("toAddress"),
                    "contractType": tx.get("contractType"),
                    "confirmed": tx.get("confirmed", False),
                    "result": tx.get("result"),
                    "amount": amount,
                    "amountTrx": amount / 1e6 if amount else 0,
                    "fee": tx.get("fee", 0),
                    "contractData": tx.get("contractData"),
                }
            )
        return formatted

    async def get_trc20_transfers(
        self, address: str, start: int = 0, limit: int = 50, contract_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get TRC-20 token transfer events for a TRON address.

        Args:
            address: TRON address
            start: Starting index
            limit: Number of results
            contract_address: Optional filter by token contract
        """
        if not address or not address.startswith("T"):
            return create_error_response(
                self.name, "Invalid TRON address", "Address must start with 'T'"
            )

        params = {"address": address, "start": start, "limit": min(limit, 50), "sort": "-timestamp"}

        if contract_address:
            params["contract_address"] = contract_address

        response = await self.get("token_trc20/transfers", params=params)

        if not response.get("success"):
            return response

        data = response.get("data", {})

        if isinstance(data, dict):
            transfers = data.get("token_transfers", [])
            total = data.get("total", 0)
        else:
            transfers = data if isinstance(data, list) else []
            total = len(transfers)

        return create_success_response(
            self.name,
            {
                "address": address,
                "chain": "tron",
                "transfers": self._format_token_transfers(transfers),
                "count": len(transfers),
                "total": total,
            },
        )

    def _format_token_transfers(self, transfers: List[Dict]) -> List[Dict]:
        """Format TRC-20 token transfer data"""
        formatted = []
        for tx in transfers:
            decimals = int(tx.get("decimals", 6))
            quant = int(tx.get("quant", 0) or 0)
            formatted.append(
                {
                    "hash": tx.get("transaction_id"),
                    "block": tx.get("block"),
                    "timestamp": tx.get("block_ts"),
                    "from": tx.get("from_address"),
                    "to": tx.get("to_address"),
                    "quant": str(quant),
                    "tokenValue": quant / (10**decimals) if decimals else quant,
                    "tokenName": tx.get("tokenInfo", {}).get("tokenName"),
                    "tokenSymbol": tx.get("tokenInfo", {}).get("tokenAbbr"),
                    "tokenDecimal": decimals,
                    "contractAddress": tx.get("contract_address"),
                    "confirmed": tx.get("confirmed", False),
                }
            )
        return formatted

    async def get_account_info(self, address: str) -> Dict[str, Any]:
        """Get account information and balance for a TRON address"""
        if not address or not address.startswith("T"):
            return create_error_response(
                self.name, "Invalid TRON address", "Address must start with 'T'"
            )

        params = {"address": address}

        response = await self.get("accountv2", params=params)

        if not response.get("success"):
            return response

        data = response.get("data", {})

        if not data:
            return create_error_response(
                self.name, "Account not found", f"No data found for address {address}"
            )

        balance = data.get("balance", 0)
        return create_success_response(
            self.name,
            {
                "address": address,
                "chain": "tron",
                "balance": balance,
                "balance_trx": balance / 1e6,
                "bandwidth": data.get("bandwidth", {}),
                "energy": data.get("energy", {}),
                "totalFrozen": data.get("totalFrozen", 0),
                "totalFrozenV2": data.get("totalFrozenV2", 0),
                "tokens": data.get("withPriceTokens", [])[:10],  # Limit tokens
                "transactions": data.get("transactions", 0),
            },
        )

    async def get_token_list(
        self, start: int = 0, limit: int = 20, order_by: str = "-volume24hInTrx"
    ) -> Dict[str, Any]:
        """Get list of TRC-20 tokens sorted by volume"""
        params = {"start": start, "limit": min(limit, 50), "order": order_by, "filter": "trc20"}

        response = await self.get("tokens/overview", params=params)

        if not response.get("success"):
            return response

        data = response.get("data", {})
        tokens = data.get("tokens", []) if isinstance(data, dict) else data

        formatted_tokens = []
        for token in tokens[:limit]:
            formatted_tokens.append(
                {
                    "name": token.get("name"),
                    "symbol": token.get("abbr"),
                    "contractAddress": token.get("contractAddress"),
                    "price": token.get("priceInTrx"),
                    "priceUsd": token.get("priceInUsd"),
                    "volume24h": token.get("volume24hInTrx"),
                    "holders": token.get("holders"),
                    "marketCap": token.get("marketcap"),
                }
            )

        return create_success_response(
            self.name, {"chain": "tron", "tokens": formatted_tokens, "count": len(formatted_tokens)}
        )
