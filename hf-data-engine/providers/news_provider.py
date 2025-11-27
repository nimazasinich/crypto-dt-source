"""
News Provider - Cryptocurrency and financial news aggregation

Provides:
- Latest crypto news from NewsAPI
- Keyword-based news search
- News sentiment analysis (basic)

API Documentation: https://newsapi.org/docs
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .base import BaseProvider, create_error_response, create_success_response


class NewsProvider(BaseProvider):
    """NewsAPI REST API provider for cryptocurrency news"""

    # API Key (temporary hardcoded - will be secured later)
    API_KEY = "968a5e25552b4cb5ba3280361d8444ab"

    # Default crypto-related keywords
    CRYPTO_KEYWORDS = [
        "bitcoin",
        "ethereum",
        "cryptocurrency",
        "crypto",
        "blockchain",
        "defi",
        "nft",
        "web3",
    ]

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="newsapi",
            base_url="https://newsapi.org/v2",
            api_key=api_key or self.API_KEY,
            timeout=10.0,
            cache_ttl=60.0,  # Cache news for 60 seconds
        )

    def _get_default_headers(self) -> Dict[str, str]:
        """Get headers with NewsAPI authorization"""
        return {"Accept": "application/json", "X-Api-Key": self.api_key}

    async def get_latest_news(
        self,
        query: Optional[str] = None,
        page_size: int = 20,
        page: int = 1,
        language: str = "en",
        sort_by: str = "publishedAt",
    ) -> Dict[str, Any]:
        """
        Get latest cryptocurrency news.

        Args:
            query: Search query (default: crypto keywords)
            page_size: Number of articles per page (max 100)
            page: Page number
            language: Language filter (en, es, fr, etc.)
            sort_by: Sort order (publishedAt, relevancy, popularity)

        Returns:
            Standardized response with news articles
        """
        # Use default crypto keywords if no query provided
        search_query = query or " OR ".join(self.CRYPTO_KEYWORDS[:5])

        # Calculate date range (last 7 days for free tier)
        from_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

        params = {
            "q": search_query,
            "pageSize": min(page_size, 100),
            "page": page,
            "language": language,
            "sortBy": sort_by,
            "from": from_date,
        }

        response = await self.get("everything", params=params)

        if not response.get("success"):
            return response

        data = response.get("data", {})

        if data.get("status") != "ok":
            error_msg = data.get("message", "Unknown error")
            return create_error_response(self.name, error_msg, data.get("code"))

        articles = data.get("articles", [])
        total_results = data.get("totalResults", 0)

        return create_success_response(
            self.name,
            {
                "articles": self._format_articles(articles),
                "count": len(articles),
                "totalResults": total_results,
                "query": search_query,
                "page": page,
                "pageSize": page_size,
            },
        )

    def _format_articles(self, articles: List[Dict]) -> List[Dict]:
        """Format news articles for clean output"""
        formatted = []
        for article in articles:
            formatted.append(
                {
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "content": article.get("content"),
                    "author": article.get("author"),
                    "source": {
                        "id": article.get("source", {}).get("id"),
                        "name": article.get("source", {}).get("name"),
                    },
                    "url": article.get("url"),
                    "urlToImage": article.get("urlToImage"),
                    "publishedAt": article.get("publishedAt"),
                    "sentiment": self._basic_sentiment(
                        article.get("title", "") + " " + (article.get("description") or "")
                    ),
                }
            )
        return formatted

    def _basic_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Basic sentiment analysis using keyword matching.
        For advanced sentiment, use HFSentimentProvider.
        """
        text_lower = text.lower()

        positive_words = [
            "surge",
            "soar",
            "rally",
            "gain",
            "bullish",
            "growth",
            "rise",
            "breakthrough",
            "record",
            "milestone",
            "adoption",
            "success",
            "profit",
            "up",
            "high",
            "positive",
            "boost",
            "moon",
        ]

        negative_words = [
            "crash",
            "plunge",
            "drop",
            "fall",
            "bearish",
            "decline",
            "loss",
            "hack",
            "scam",
            "fraud",
            "ban",
            "regulation",
            "lawsuit",
            "risk",
            "down",
            "low",
            "negative",
            "warning",
            "concern",
            "fear",
        ]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        total = positive_count + negative_count
        if total == 0:
            return {"label": "neutral", "score": 0.5}

        positive_ratio = positive_count / total

        if positive_ratio > 0.6:
            return {"label": "positive", "score": positive_ratio}
        elif positive_ratio < 0.4:
            return {"label": "negative", "score": 1 - positive_ratio}
        else:
            return {"label": "neutral", "score": 0.5}

    async def get_top_headlines(
        self, category: str = "business", country: str = "us", page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Get top headlines from news sources.

        Args:
            category: Category (business, technology, etc.)
            country: Country code (us, gb, etc.)
            page_size: Number of articles
        """
        params = {"category": category, "country": country, "pageSize": min(page_size, 100)}

        response = await self.get("top-headlines", params=params)

        if not response.get("success"):
            return response

        data = response.get("data", {})

        if data.get("status") != "ok":
            error_msg = data.get("message", "Unknown error")
            return create_error_response(self.name, error_msg, data.get("code"))

        articles = data.get("articles", [])

        return create_success_response(
            self.name,
            {
                "articles": self._format_articles(articles),
                "count": len(articles),
                "category": category,
                "country": country,
            },
        )

    async def search_news(
        self, keywords: List[str], page_size: int = 20, language: str = "en"
    ) -> Dict[str, Any]:
        """
        Search news by multiple keywords.

        Args:
            keywords: List of keywords to search
            page_size: Number of results
            language: Language filter
        """
        if not keywords:
            return create_error_response(
                self.name, "Missing keywords", "At least one keyword is required"
            )

        # Build OR query for keywords
        query = " OR ".join(f'"{k}"' for k in keywords[:5])

        return await self.get_latest_news(query=query, page_size=page_size, language=language)

    async def get_crypto_news(self, page_size: int = 20) -> Dict[str, Any]:
        """
        Convenience method to get latest crypto-specific news.
        """
        return await self.get_latest_news(
            query="cryptocurrency OR bitcoin OR ethereum OR crypto",
            page_size=page_size,
            sort_by="publishedAt",
        )

    async def get_news_sources(self, category: str = "business") -> Dict[str, Any]:
        """Get available news sources"""
        params = {"category": category, "language": "en"}

        response = await self.get("top-headlines/sources", params=params)

        if not response.get("success"):
            return response

        data = response.get("data", {})

        if data.get("status") != "ok":
            error_msg = data.get("message", "Unknown error")
            return create_error_response(self.name, error_msg)

        sources = data.get("sources", [])

        formatted_sources = []
        for source in sources:
            formatted_sources.append(
                {
                    "id": source.get("id"),
                    "name": source.get("name"),
                    "description": source.get("description"),
                    "url": source.get("url"),
                    "category": source.get("category"),
                    "language": source.get("language"),
                    "country": source.get("country"),
                }
            )

        return create_success_response(
            self.name,
            {"sources": formatted_sources, "count": len(formatted_sources), "category": category},
        )
