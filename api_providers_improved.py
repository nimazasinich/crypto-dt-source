#!/usr/bin/env python3
"""
Improved Provider API Endpoint with intelligent categorization and validation
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Crypto Monitor API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_providers_config() -> Dict[str, Any]:
    """Load providers configuration from JSON file"""
    try:
        config_path = Path(__file__).parent / "providers_config_extended.json"
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("providers_config_extended.json not found")
        return {"providers": {}}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        return {"providers": {}}


def intelligently_categorize(provider_data: Dict[str, Any], provider_id: str) -> str:
    """
    Intelligently determine provider category based on URL, name, and ID
    """
    category = provider_data.get("category", "unknown")

    # If already categorized, return it
    if category != "unknown":
        return category

    # Check base_url for hints
    if "base_url" in provider_data:
        url = provider_data["base_url"].lower()

        # Market data providers
        if any(
            x in url
            for x in [
                "coingecko",
                "coincap",
                "coinpaprika",
                "coinlore",
                "coinrank",
                "coinmarketcap",
                "cryptocompare",
                "nomics",
            ]
        ):
            return "market_data"

        # Blockchain explorers
        if any(
            x in url
            for x in [
                "etherscan",
                "bscscan",
                "polygonscan",
                "arbiscan",
                "blockchair",
                "blockchain",
                "blockscout",
            ]
        ):
            return "blockchain_explorers"

        # DeFi protocols
        if any(
            x in url
            for x in [
                "defillama",
                "uniswap",
                "aave",
                "compound",
                "curve",
                "pancakeswap",
                "sushiswap",
                "1inch",
                "debank",
            ]
        ):
            return "defi"

        # NFT marketplaces
        if any(x in url for x in ["opensea", "rarible", "nftport", "reservoir"]):
            return "nft"

        # News sources
        if any(
            x in url
            for x in [
                "news",
                "rss",
                "feed",
                "cryptopanic",
                "coindesk",
                "cointelegraph",
                "decrypt",
                "bitcoinist",
            ]
        ):
            return "news"

        # Social media
        if any(x in url for x in ["reddit", "twitter", "lunarcrush"]):
            return "social"

        # Sentiment analysis
        if any(x in url for x in ["alternative.me", "santiment"]):
            return "sentiment"

        # Exchange APIs
        if any(
            x in url
            for x in [
                "binance",
                "coinbase",
                "kraken",
                "bitfinex",
                "huobi",
                "kucoin",
                "okx",
                "bybit",
            ]
        ):
            return "exchange"

        # Analytics platforms
        if any(x in url for x in ["glassnode", "intotheblock", "coinmetrics", "kaiko", "messari"]):
            return "analytics"

        # RPC nodes
        if any(x in url for x in ["rpc", "publicnode", "llamanodes", "oneinch"]):
            return "rpc"

    # Check provider_id for hints
    pid_lower = provider_id.lower()
    if "hf_model" in pid_lower:
        return "hf-model"
    elif "hf_ds" in pid_lower:
        return "hf-dataset"
    elif any(x in pid_lower for x in ["news", "rss", "feed"]):
        return "news"
    elif any(x in pid_lower for x in ["scan", "explorer", "blockchair"]):
        return "blockchain_explorers"

    return "unknown"


def intelligently_detect_type(provider_data: Dict[str, Any]) -> str:
    """
    Intelligently determine provider type based on URL and other data
    """
    provider_type = provider_data.get("type", "unknown")

    # If already typed, return it
    if provider_type != "unknown":
        return provider_type

    # Check base_url for type hints
    if "base_url" in provider_data:
        url = provider_data["base_url"].lower()

        # RPC endpoints
        if any(
            x in url
            for x in [
                "rpc",
                "infura",
                "alchemy",
                "quicknode",
                "publicnode",
                "llamanodes",
                "ethereum",
            ]
        ):
            return "http_rpc"

        # GraphQL endpoints
        if "graphql" in url or "graph" in url:
            return "graphql"

        # WebSocket endpoints
        if "ws://" in url or "wss://" in url:
            return "websocket"

        # Default to HTTP JSON
        if "http" in url:
            return "http_json"

    # Check for query_type field
    if provider_data.get("query_type") == "graphql":
        return "graphql"

    return "http_json"  # Default fallback


@app.get("/")
async def root():
    """Root endpoint"""
    return FileResponse("admin_improved.html")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0", "service": "Crypto Monitor API"}


@app.get("/api/providers")
async def get_providers(
    category: Optional[str] = None, status: Optional[str] = None, search: Optional[str] = None
):
    """
    Get all providers with intelligent categorization and filtering

    Query parameters:
    - category: Filter by category (e.g., market_data, defi, nft)
    - status: Filter by status (validated or unvalidated)
    - search: Search in provider name or ID
    """
    config = load_providers_config()
    providers = config.get("providers", {})

    result = []

    for provider_id, provider_data in providers.items():
        # Intelligent categorization
        detected_category = intelligently_categorize(provider_data, provider_id)
        detected_type = intelligently_detect_type(provider_data)

        # Determine validation status
        is_validated = bool(
            provider_data.get("validated")
            or provider_data.get("validated_at")
            or provider_data.get("response_time_ms")
        )

        # Build provider object
        provider_obj = {
            "provider_id": provider_id,
            "name": provider_data.get("name", provider_id.replace("_", " ").title()),
            "category": detected_category,
            "type": detected_type,
            "status": "validated" if is_validated else "unvalidated",
            "validated": is_validated,
            "validated_at": provider_data.get("validated_at"),
            "response_time_ms": provider_data.get("response_time_ms"),
            "base_url": provider_data.get("base_url"),
            "requires_auth": provider_data.get("requires_auth", False),
            "priority": provider_data.get("priority"),
            "added_by": provider_data.get("added_by", "manual"),
        }

        # Apply filters
        if category and detected_category != category:
            continue

        if status and provider_obj["status"] != status:
            continue

        if search:
            search_lower = search.lower()
            if not (
                search_lower in provider_id.lower()
                or search_lower in provider_obj["name"].lower()
                or search_lower in detected_category.lower()
            ):
                continue

        result.append(provider_obj)

    # Sort: validated first, then by name
    result.sort(key=lambda x: (x["status"] != "validated", x["name"]))

    # Calculate statistics
    validated_count = sum(1 for p in result if p["validated"])
    unvalidated_count = len(result) - validated_count

    # Category breakdown
    categories = {}
    for p in result:
        cat = p["category"]
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "providers": result,
        "total": len(result),
        "validated": validated_count,
        "unvalidated": unvalidated_count,
        "categories": categories,
        "source": "providers_config_extended.json",
    }


@app.get("/api/providers/{provider_id}")
async def get_provider_detail(provider_id: str):
    """Get specific provider details"""
    config = load_providers_config()
    providers = config.get("providers", {})

    if provider_id not in providers:
        raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")

    provider_data = providers[provider_id]

    return {
        "provider_id": provider_id,
        "name": provider_data.get("name", provider_id),
        "category": intelligently_categorize(provider_data, provider_id),
        "type": intelligently_detect_type(provider_data),
        **provider_data,
    }


@app.get("/api/providers/category/{category}")
async def get_providers_by_category(category: str):
    """Get providers by category"""
    providers_data = await get_providers(category=category)
    return {
        "category": category,
        "providers": providers_data["providers"],
        "count": len(providers_data["providers"]),
    }


@app.get("/api/stats")
async def get_stats():
    """Get overall statistics"""
    config = load_providers_config()
    providers = config.get("providers", {})

    total = len(providers)
    validated = sum(1 for p in providers.values() if p.get("validated") or p.get("validated_at"))
    unvalidated = total - validated

    # Calculate average response time
    response_times = [
        p.get("response_time_ms", 0) for p in providers.values() if p.get("response_time_ms")
    ]
    avg_response = sum(response_times) / len(response_times) if response_times else 0

    # Count by category
    categories = {}
    for provider_id, provider_data in providers.items():
        cat = intelligently_categorize(provider_data, provider_id)
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total_providers": total,
        "validated": validated,
        "unvalidated": unvalidated,
        "avg_response_time_ms": round(avg_response, 2),
        "categories": categories,
        "validation_percentage": round((validated / total * 100) if total > 0 else 0, 2),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
