"""
Blockchain REST API Router

Endpoints:
- GET /api/v1/blockchain/eth/transactions - Ethereum transactions
- GET /api/v1/blockchain/bsc/transactions - BSC transactions  
- GET /api/v1/blockchain/tron/transactions - TRON transactions
- GET /api/v1/blockchain/{chain}/balance - Account balance

All endpoints return standardized JSON with {success, source, data} format.
No WebSockets - pure REST API.
"""

from __future__ import annotations
import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from providers.etherscan_provider import EtherscanProvider
from providers.bscscan_provider import BscscanProvider
from providers.tronscan_provider import TronscanProvider

# Configure logging
logger = logging.getLogger("routers.blockchain")

# Create router
router = APIRouter(prefix="/api/v1/blockchain", tags=["Blockchain"])

# Provider instances (singleton pattern)
_eth_provider: Optional[EtherscanProvider] = None
_bsc_provider: Optional[BscscanProvider] = None
_tron_provider: Optional[TronscanProvider] = None


def get_eth_provider() -> EtherscanProvider:
    """Get or create Etherscan provider instance"""
    global _eth_provider
    if _eth_provider is None:
        _eth_provider = EtherscanProvider()
    return _eth_provider


def get_bsc_provider() -> BscscanProvider:
    """Get or create BscScan provider instance"""
    global _bsc_provider
    if _bsc_provider is None:
        _bsc_provider = BscscanProvider()
    return _bsc_provider


def get_tron_provider() -> TronscanProvider:
    """Get or create TronScan provider instance"""
    global _tron_provider
    if _tron_provider is None:
        _tron_provider = TronscanProvider()
    return _tron_provider


# ============================================================================
# ETHEREUM ENDPOINTS
# ============================================================================

@router.get("/eth/transactions")
async def get_eth_transactions(
    address: str = Query(..., description="Ethereum address (0x...)"),
    page: int = Query(1, ge=1, description="Page number"),
    offset: int = Query(50, ge=1, le=100, description="Results per page (max 100)")
):
    """
    Get Ethereum transaction history for an address.
    
    Returns list of transactions with:
    - Transaction hash, block, timestamp
    - From/to addresses
    - Value in Wei and ETH
    - Gas used and fees
    - Contract interactions
    """
    provider = get_eth_provider()
    
    try:
        result = await provider.get_transactions(
            address=address,
            page=page,
            offset=offset
        )
        return result
    except Exception as e:
        logger.error(f"ETH transactions error: {e}")
        return {
            "success": False,
            "source": "etherscan",
            "error": "Failed to fetch Ethereum transactions",
            "details": str(e)
        }


@router.get("/eth/tokens")
async def get_eth_token_transfers(
    address: str = Query(..., description="Ethereum address"),
    contract: Optional[str] = Query(None, description="Token contract address filter"),
    page: int = Query(1, ge=1),
    offset: int = Query(50, ge=1, le=100)
):
    """
    Get ERC-20 token transfer events for an Ethereum address.
    
    Returns token transfers with:
    - Token name, symbol, decimals
    - Transfer amount (raw and formatted)
    - From/to addresses
    - Contract address
    """
    provider = get_eth_provider()
    
    try:
        result = await provider.get_token_transfers(
            address=address,
            contract_address=contract,
            page=page,
            offset=offset
        )
        return result
    except Exception as e:
        logger.error(f"ETH token transfers error: {e}")
        return {
            "success": False,
            "source": "etherscan",
            "error": "Failed to fetch token transfers",
            "details": str(e)
        }


@router.get("/eth/balance")
async def get_eth_balance(
    address: str = Query(..., description="Ethereum address")
):
    """Get ETH balance for an address"""
    provider = get_eth_provider()
    
    try:
        result = await provider.get_balance(address)
        return result
    except Exception as e:
        logger.error(f"ETH balance error: {e}")
        return {
            "success": False,
            "source": "etherscan",
            "error": "Failed to fetch balance",
            "details": str(e)
        }


@router.get("/eth/gas")
async def get_eth_gas_price():
    """Get current Ethereum gas prices (safe, standard, fast)"""
    provider = get_eth_provider()
    
    try:
        result = await provider.get_gas_price()
        return result
    except Exception as e:
        logger.error(f"ETH gas price error: {e}")
        return {
            "success": False,
            "source": "etherscan",
            "error": "Failed to fetch gas prices",
            "details": str(e)
        }


# ============================================================================
# BSC (BINANCE SMART CHAIN) ENDPOINTS
# ============================================================================

@router.get("/bsc/transactions")
async def get_bsc_transactions(
    address: str = Query(..., description="BSC address (0x...)"),
    page: int = Query(1, ge=1),
    offset: int = Query(50, ge=1, le=100)
):
    """
    Get BSC transaction history for an address.
    
    Returns list of transactions with value in Wei and BNB.
    """
    provider = get_bsc_provider()
    
    try:
        result = await provider.get_transactions(
            address=address,
            page=page,
            offset=offset
        )
        return result
    except Exception as e:
        logger.error(f"BSC transactions error: {e}")
        return {
            "success": False,
            "source": "bscscan",
            "error": "Failed to fetch BSC transactions",
            "details": str(e)
        }


@router.get("/bsc/tokens")
async def get_bsc_token_transfers(
    address: str = Query(..., description="BSC address"),
    contract: Optional[str] = Query(None, description="Token contract address filter"),
    page: int = Query(1, ge=1),
    offset: int = Query(50, ge=1, le=100)
):
    """Get BEP-20 token transfer events for a BSC address"""
    provider = get_bsc_provider()
    
    try:
        result = await provider.get_bep20_transfers(
            address=address,
            contract_address=contract,
            page=page,
            offset=offset
        )
        return result
    except Exception as e:
        logger.error(f"BSC token transfers error: {e}")
        return {
            "success": False,
            "source": "bscscan",
            "error": "Failed to fetch BEP-20 transfers",
            "details": str(e)
        }


@router.get("/bsc/balance")
async def get_bsc_balance(
    address: str = Query(..., description="BSC address")
):
    """Get BNB balance for a BSC address"""
    provider = get_bsc_provider()
    
    try:
        result = await provider.get_balance(address)
        return result
    except Exception as e:
        logger.error(f"BSC balance error: {e}")
        return {
            "success": False,
            "source": "bscscan",
            "error": "Failed to fetch BNB balance",
            "details": str(e)
        }


@router.get("/bsc/gas")
async def get_bsc_gas_price():
    """Get current BSC gas prices"""
    provider = get_bsc_provider()
    
    try:
        result = await provider.get_gas_price()
        return result
    except Exception as e:
        logger.error(f"BSC gas price error: {e}")
        return {
            "success": False,
            "source": "bscscan",
            "error": "Failed to fetch BSC gas prices",
            "details": str(e)
        }


# ============================================================================
# TRON ENDPOINTS
# ============================================================================

@router.get("/tron/transactions")
async def get_tron_transactions(
    address: str = Query(..., description="TRON address (starts with T)"),
    start: int = Query(0, ge=0, description="Starting index"),
    limit: int = Query(50, ge=1, le=50, description="Results limit (max 50)")
):
    """
    Get TRON transaction history for an address.
    
    Returns list of transactions with:
    - Transaction hash, block, timestamp
    - Owner and recipient addresses
    - Amount in SUN and TRX
    - Contract type and data
    """
    provider = get_tron_provider()
    
    try:
        result = await provider.get_transactions(
            address=address,
            start=start,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"TRON transactions error: {e}")
        return {
            "success": False,
            "source": "tronscan",
            "error": "Failed to fetch TRON transactions",
            "details": str(e)
        }


@router.get("/tron/tokens")
async def get_tron_token_transfers(
    address: str = Query(..., description="TRON address"),
    contract: Optional[str] = Query(None, description="Token contract address"),
    start: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=50)
):
    """Get TRC-20 token transfer events for a TRON address"""
    provider = get_tron_provider()
    
    try:
        result = await provider.get_trc20_transfers(
            address=address,
            start=start,
            limit=limit,
            contract_address=contract
        )
        return result
    except Exception as e:
        logger.error(f"TRON token transfers error: {e}")
        return {
            "success": False,
            "source": "tronscan",
            "error": "Failed to fetch TRC-20 transfers",
            "details": str(e)
        }


@router.get("/tron/account")
async def get_tron_account(
    address: str = Query(..., description="TRON address")
):
    """
    Get TRON account information including:
    - TRX balance
    - Bandwidth and energy
    - Token holdings
    - Transaction count
    """
    provider = get_tron_provider()
    
    try:
        result = await provider.get_account_info(address)
        return result
    except Exception as e:
        logger.error(f"TRON account error: {e}")
        return {
            "success": False,
            "source": "tronscan",
            "error": "Failed to fetch TRON account",
            "details": str(e)
        }


@router.get("/tron/tokens/list")
async def get_tron_token_list(
    limit: int = Query(20, ge=1, le=50, description="Number of tokens")
):
    """Get list of top TRC-20 tokens by volume"""
    provider = get_tron_provider()
    
    try:
        result = await provider.get_token_list(limit=limit)
        return result
    except Exception as e:
        logger.error(f"TRON token list error: {e}")
        return {
            "success": False,
            "source": "tronscan",
            "error": "Failed to fetch token list",
            "details": str(e)
        }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def blockchain_health():
    """Check health status of all blockchain providers"""
    eth = get_eth_provider()
    bsc = get_bsc_provider()
    tron = get_tron_provider()
    
    return {
        "success": True,
        "providers": {
            "etherscan": {
                "name": eth.name,
                "baseUrl": eth.base_url,
                "timeout": eth.timeout
            },
            "bscscan": {
                "name": bsc.name,
                "baseUrl": bsc.base_url,
                "timeout": bsc.timeout
            },
            "tronscan": {
                "name": tron.name,
                "baseUrl": tron.base_url,
                "timeout": tron.timeout
            }
        },
        "endpoints": [
            "/api/v1/blockchain/eth/transactions",
            "/api/v1/blockchain/eth/tokens",
            "/api/v1/blockchain/eth/balance",
            "/api/v1/blockchain/eth/gas",
            "/api/v1/blockchain/bsc/transactions",
            "/api/v1/blockchain/bsc/tokens",
            "/api/v1/blockchain/bsc/balance",
            "/api/v1/blockchain/bsc/gas",
            "/api/v1/blockchain/tron/transactions",
            "/api/v1/blockchain/tron/tokens",
            "/api/v1/blockchain/tron/account",
            "/api/v1/blockchain/tron/tokens/list"
        ]
    }
