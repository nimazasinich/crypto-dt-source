"""
News REST API Router

Endpoints:
- GET /api/v1/news/latest - Latest cryptocurrency news
- GET /api/v1/news/search - Search news by keywords
- GET /api/v1/news/headlines - Top headlines
- GET /api/v1/news/sentiment - News with sentiment analysis

Data source: NewsAPI
All endpoints return standardized JSON with {success, source, data} format.
"""

from __future__ import annotations
import logging
from typing import Optional, List
from fastapi import APIRouter, Query

from providers.news_provider import NewsProvider

# Configure logging
logger = logging.getLogger("routers.news")

# Create router
router = APIRouter(prefix="/api/v1/news", tags=["News"])

# Provider instance (singleton)
_news_provider: Optional[NewsProvider] = None


def get_news_provider() -> NewsProvider:
    """Get or create NewsAPI provider instance"""
    global _news_provider
    if _news_provider is None:
        _news_provider = NewsProvider()
    return _news_provider


# ============================================================================
# NEWS ENDPOINTS
# ============================================================================


@router.get("/latest")
async def get_latest_news(
    query: Optional[str] = Query(None, description="Search query (default: crypto keywords)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of articles"),
    page: int = Query(1, ge=1, description="Page number"),
    language: str = Query("en", description="Language code (en, es, fr, de, etc.)"),
    sort_by: str = Query("publishedAt", description="Sort by: publishedAt, relevancy, popularity"),
):
    """
    Get latest cryptocurrency and blockchain news.

    If no query is provided, returns news for common crypto keywords
    (bitcoin, ethereum, cryptocurrency, blockchain, defi).

    Returns articles with:
    - Title, description, content
    - Author and source
    - Publication date
    - Image URL
    - Basic sentiment analysis

    Example: /api/v1/news/latest?page_size=10
    """
    provider = get_news_provider()

    try:
        result = await provider.get_latest_news(
            query=query, page_size=page_size, page=page, language=language, sort_by=sort_by
        )
        return result
    except Exception as e:
        logger.error(f"Latest news error: {e}")
        return {
            "success": False,
            "source": "newsapi",
            "error": "Failed to fetch news",
            "details": str(e),
        }


@router.get("/crypto")
async def get_crypto_news(
    page_size: int = Query(20, ge=1, le=100, description="Number of articles")
):
    """
    Convenience endpoint: Get latest crypto-specific news.

    Uses optimized query for cryptocurrency-related articles.
    """
    provider = get_news_provider()

    try:
        result = await provider.get_crypto_news(page_size=page_size)
        return result
    except Exception as e:
        logger.error(f"Crypto news error: {e}")
        return {
            "success": False,
            "source": "newsapi",
            "error": "Failed to fetch crypto news",
            "details": str(e),
        }


@router.get("/search")
async def search_news(
    keywords: str = Query(..., description="Comma-separated keywords (e.g., bitcoin,eth,solana)"),
    page_size: int = Query(20, ge=1, le=100),
    language: str = Query("en"),
):
    """
    Search news by specific keywords.

    Provide comma-separated keywords to search for.

    Example: /api/v1/news/search?keywords=bitcoin,ethereum,defi
    """
    provider = get_news_provider()

    # Parse keywords
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]

    if not keyword_list:
        return {
            "success": False,
            "source": "newsapi",
            "error": "No valid keywords provided",
            "details": "Provide at least one keyword",
        }

    try:
        result = await provider.search_news(
            keywords=keyword_list, page_size=page_size, language=language
        )
        return result
    except Exception as e:
        logger.error(f"Search news error: {e}")
        return {
            "success": False,
            "source": "newsapi",
            "error": "Failed to search news",
            "details": str(e),
        }


@router.get("/headlines")
async def get_top_headlines(
    category: str = Query("business", description="Category: business, technology, general, etc."),
    country: str = Query("us", description="Country code: us, gb, au, etc."),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    Get top headlines from major news sources.

    Categories: business, entertainment, general, health, science, sports, technology

    Example: /api/v1/news/headlines?category=technology&country=us
    """
    provider = get_news_provider()

    try:
        result = await provider.get_top_headlines(
            category=category, country=country, page_size=page_size
        )
        return result
    except Exception as e:
        logger.error(f"Headlines error: {e}")
        return {
            "success": False,
            "source": "newsapi",
            "error": "Failed to fetch headlines",
            "details": str(e),
        }


@router.get("/sources")
async def get_news_sources(category: str = Query("business", description="Category filter")):
    """
    Get list of available news sources.

    Returns sources with:
    - Name and description
    - URL
    - Category and language
    """
    provider = get_news_provider()

    try:
        result = await provider.get_news_sources(category=category)
        return result
    except Exception as e:
        logger.error(f"Sources error: {e}")
        return {
            "success": False,
            "source": "newsapi",
            "error": "Failed to fetch sources",
            "details": str(e),
        }


@router.get("/sentiment")
async def get_news_with_sentiment(
    text: Optional[str] = Query(None, description="Text to analyze for sentiment"),
    query: Optional[str] = Query(None, description="News search query"),
    page_size: int = Query(10, ge=1, le=50),
):
    """
    Get news with sentiment analysis.

    Two modes:
    1. Provide 'text' parameter: Analyze sentiment of provided text
    2. Provide 'query' parameter: Fetch news and analyze sentiment of each article

    Sentiment is basic keyword-based analysis. For advanced AI sentiment,
    use the /api/v1/hf/sentiment endpoint.

    Example: /api/v1/news/sentiment?query=bitcoin
    """
    provider = get_news_provider()

    if text:
        # Analyze provided text
        sentiment = provider._basic_sentiment(text)
        return {
            "success": True,
            "source": "newsapi",
            "data": {
                "text": text[:200] + "..." if len(text) > 200 else text,
                "sentiment": sentiment,
                "method": "keyword_analysis",
            },
        }

    if query:
        # Fetch news and include sentiment
        try:
            result = await provider.get_latest_news(
                query=query, page_size=page_size, sort_by="publishedAt"
            )
            return result
        except Exception as e:
            logger.error(f"Sentiment news error: {e}")
            return {
                "success": False,
                "source": "newsapi",
                "error": "Failed to fetch news with sentiment",
                "details": str(e),
            }

    return {
        "success": False,
        "source": "newsapi",
        "error": "Missing parameter",
        "details": "Provide either 'text' or 'query' parameter",
    }


# ============================================================================
# TOPIC-SPECIFIC ENDPOINTS
# ============================================================================


@router.get("/bitcoin")
async def get_bitcoin_news(page_size: int = Query(15, ge=1, le=50)):
    """Get Bitcoin-specific news"""
    provider = get_news_provider()

    try:
        result = await provider.get_latest_news(
            query="bitcoin OR BTC", page_size=page_size, sort_by="publishedAt"
        )
        return result
    except Exception as e:
        logger.error(f"Bitcoin news error: {e}")
        return {
            "success": False,
            "source": "newsapi",
            "error": "Failed to fetch Bitcoin news",
            "details": str(e),
        }


@router.get("/ethereum")
async def get_ethereum_news(page_size: int = Query(15, ge=1, le=50)):
    """Get Ethereum-specific news"""
    provider = get_news_provider()

    try:
        result = await provider.get_latest_news(
            query="ethereum OR ETH OR vitalik", page_size=page_size, sort_by="publishedAt"
        )
        return result
    except Exception as e:
        logger.error(f"Ethereum news error: {e}")
        return {
            "success": False,
            "source": "newsapi",
            "error": "Failed to fetch Ethereum news",
            "details": str(e),
        }


@router.get("/defi")
async def get_defi_news(page_size: int = Query(15, ge=1, le=50)):
    """Get DeFi-specific news"""
    provider = get_news_provider()

    try:
        result = await provider.get_latest_news(
            query="DeFi OR decentralized finance OR yield farming OR liquidity",
            page_size=page_size,
            sort_by="publishedAt",
        )
        return result
    except Exception as e:
        logger.error(f"DeFi news error: {e}")
        return {
            "success": False,
            "source": "newsapi",
            "error": "Failed to fetch DeFi news",
            "details": str(e),
        }


@router.get("/nft")
async def get_nft_news(page_size: int = Query(15, ge=1, le=50)):
    """Get NFT-specific news"""
    provider = get_news_provider()

    try:
        result = await provider.get_latest_news(
            query="NFT OR non-fungible token OR digital art OR opensea",
            page_size=page_size,
            sort_by="publishedAt",
        )
        return result
    except Exception as e:
        logger.error(f"NFT news error: {e}")
        return {
            "success": False,
            "source": "newsapi",
            "error": "Failed to fetch NFT news",
            "details": str(e),
        }


# ============================================================================
# HEALTH CHECK
# ============================================================================


@router.get("/health")
async def news_health():
    """Check health status of news provider"""
    provider = get_news_provider()

    return {
        "success": True,
        "provider": {
            "name": provider.name,
            "baseUrl": provider.base_url,
            "timeout": provider.timeout,
        },
        "endpoints": [
            "/api/v1/news/latest",
            "/api/v1/news/crypto",
            "/api/v1/news/search",
            "/api/v1/news/headlines",
            "/api/v1/news/sources",
            "/api/v1/news/sentiment",
            "/api/v1/news/bitcoin",
            "/api/v1/news/ethereum",
            "/api/v1/news/defi",
            "/api/v1/news/nft",
        ],
    }
