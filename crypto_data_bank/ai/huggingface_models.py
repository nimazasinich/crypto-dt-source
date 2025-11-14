#!/usr/bin/env python3
"""
ادغام مدل‌های HuggingFace برای تحلیل هوش مصنوعی
HuggingFace Models Integration for AI Analysis
"""

import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("⚠️ transformers not installed. AI features will be limited.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HuggingFaceAnalyzer:
    """
    تحلیل‌گر هوش مصنوعی با استفاده از مدل‌های HuggingFace
    AI Analyzer using HuggingFace models
    """

    def __init__(self):
        self.models_loaded = False
        self.sentiment_analyzer = None
        self.zero_shot_classifier = None

        if TRANSFORMERS_AVAILABLE:
            self._load_models()

    def _load_models(self):
        """بارگذاری مدل‌های HuggingFace"""
        try:
            logger.info("🤗 Loading HuggingFace models...")

            # Sentiment Analysis Model - FinBERT (specialized for financial text)
            try:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="ProsusAI/finbert",
                    tokenizer="ProsusAI/finbert"
                )
                logger.info("✅ Loaded FinBERT for sentiment analysis")
            except Exception as e:
                logger.warning(f"⚠️ Could not load FinBERT: {e}")
                # Fallback to general sentiment model
                try:
                    self.sentiment_analyzer = pipeline(
                        "sentiment-analysis",
                        model="distilbert-base-uncased-finetuned-sst-2-english"
                    )
                    logger.info("✅ Loaded DistilBERT for sentiment analysis (fallback)")
                except Exception as e2:
                    logger.error(f"❌ Could not load sentiment model: {e2}")

            # Zero-shot Classification (for categorizing news/tweets)
            try:
                self.zero_shot_classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli"
                )
                logger.info("✅ Loaded BART for zero-shot classification")
            except Exception as e:
                logger.warning(f"⚠️ Could not load zero-shot classifier: {e}")

            self.models_loaded = True
            logger.info("🎉 HuggingFace models loaded successfully!")

        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            self.models_loaded = False

    async def analyze_news_sentiment(self, news_text: str) -> Dict[str, Any]:
        """
        تحلیل احساسات یک خبر
        Analyze sentiment of a news article
        """
        if not self.models_loaded or not self.sentiment_analyzer:
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "error": "Model not available"
            }

        try:
            # Truncate text to avoid token limit
            max_length = 512
            text = news_text[:max_length]

            # Run sentiment analysis
            result = self.sentiment_analyzer(text)[0]

            # Map FinBERT labels to standard format
            label_map = {
                "positive": "bullish",
                "negative": "bearish",
                "neutral": "neutral"
            }

            sentiment = label_map.get(result['label'].lower(), result['label'].lower())

            return {
                "sentiment": sentiment,
                "confidence": round(result['score'], 4),
                "raw_label": result['label'],
                "text_analyzed": text[:100] + "...",
                "model": "finbert",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Sentiment analysis error: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "error": str(e)
            }

    async def analyze_news_batch(self, news_list: List[Dict]) -> List[Dict]:
        """
        تحلیل دسته‌ای احساسات اخبار
        Batch sentiment analysis for news
        """
        results = []

        for news in news_list:
            text = f"{news.get('title', '')} {news.get('description', '')}"

            sentiment_result = await self.analyze_news_sentiment(text)

            results.append({
                **news,
                "ai_sentiment": sentiment_result['sentiment'],
                "ai_confidence": sentiment_result['confidence'],
                "ai_analysis": sentiment_result
            })

            # Small delay to avoid overloading
            await asyncio.sleep(0.1)

        return results

    async def categorize_news(self, news_text: str) -> Dict[str, Any]:
        """
        دسته‌بندی اخبار با zero-shot classification
        Categorize news using zero-shot classification
        """
        if not self.models_loaded or not self.zero_shot_classifier:
            return {
                "category": "general",
                "confidence": 0.0,
                "error": "Model not available"
            }

        try:
            # Define categories
            categories = [
                "price_movement",
                "regulation",
                "technology",
                "adoption",
                "security",
                "defi",
                "nft",
                "exchange",
                "mining",
                "general"
            ]

            # Truncate text
            text = news_text[:512]

            # Run classification
            result = self.zero_shot_classifier(text, categories)

            return {
                "category": result['labels'][0],
                "confidence": round(result['scores'][0], 4),
                "all_categories": [
                    {"label": label, "score": round(score, 4)}
                    for label, score in zip(result['labels'][:3], result['scores'][:3])
                ],
                "model": "bart-mnli",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Categorization error: {e}")
            return {
                "category": "general",
                "confidence": 0.0,
                "error": str(e)
            }

    async def calculate_aggregated_sentiment(
        self,
        news_list: List[Dict],
        symbol: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        محاسبه احساسات جمعی از چندین خبر
        Calculate aggregated sentiment from multiple news items
        """
        if not news_list:
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 0.0,
                "confidence": 0.0,
                "news_count": 0
            }

        # Filter by symbol if provided
        if symbol:
            news_list = [
                n for n in news_list
                if symbol.upper() in [c.upper() for c in n.get('coins', [])]
            ]

        if not news_list:
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 0.0,
                "confidence": 0.0,
                "news_count": 0,
                "note": f"No news found for {symbol}"
            }

        # Analyze each news item
        analyzed_news = await self.analyze_news_batch(news_list[:20])  # Limit to 20

        # Calculate weighted sentiment
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        total_confidence = 0.0

        for news in analyzed_news:
            sentiment = news.get('ai_sentiment', 'neutral')
            confidence = news.get('ai_confidence', 0.0)

            if sentiment == 'bullish':
                bullish_count += confidence
            elif sentiment == 'bearish':
                bearish_count += confidence
            else:
                neutral_count += confidence

            total_confidence += confidence

        # Calculate overall sentiment score (-100 to +100)
        if total_confidence > 0:
            sentiment_score = ((bullish_count - bearish_count) / total_confidence) * 100
        else:
            sentiment_score = 0.0

        # Determine overall classification
        if sentiment_score > 30:
            overall = "bullish"
        elif sentiment_score < -30:
            overall = "bearish"
        else:
            overall = "neutral"

        return {
            "overall_sentiment": overall,
            "sentiment_score": round(sentiment_score, 2),
            "confidence": round(total_confidence / len(analyzed_news), 2) if analyzed_news else 0.0,
            "news_count": len(analyzed_news),
            "bullish_weight": round(bullish_count, 2),
            "bearish_weight": round(bearish_count, 2),
            "neutral_weight": round(neutral_count, 2),
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        }

    async def predict_price_direction(
        self,
        symbol: str,
        recent_news: List[Dict],
        current_price: float,
        historical_prices: List[float]
    ) -> Dict[str, Any]:
        """
        پیش‌بینی جهت قیمت بر اساس اخبار و روند قیمت
        Predict price direction based on news sentiment and price trend
        """
        # Get news sentiment
        news_sentiment = await self.calculate_aggregated_sentiment(recent_news, symbol)

        # Calculate price trend
        if len(historical_prices) >= 2:
            price_change = ((current_price - historical_prices[0]) / historical_prices[0]) * 100
        else:
            price_change = 0.0

        # Combine signals
        # News sentiment weight: 60%
        # Price momentum weight: 40%
        news_score = news_sentiment['sentiment_score'] * 0.6
        momentum_score = min(50, max(-50, price_change * 10)) * 0.4

        combined_score = news_score + momentum_score

        # Determine prediction
        if combined_score > 20:
            prediction = "bullish"
            direction = "up"
        elif combined_score < -20:
            prediction = "bearish"
            direction = "down"
        else:
            prediction = "neutral"
            direction = "sideways"

        # Calculate confidence
        confidence = min(1.0, abs(combined_score) / 100)

        return {
            "symbol": symbol,
            "prediction": prediction,
            "direction": direction,
            "confidence": round(confidence, 2),
            "combined_score": round(combined_score, 2),
            "news_sentiment_score": round(news_score / 0.6, 2),
            "price_momentum_score": round(momentum_score / 0.4, 2),
            "current_price": current_price,
            "price_change_pct": round(price_change, 2),
            "news_analyzed": news_sentiment['news_count'],
            "timestamp": datetime.now().isoformat(),
            "model": "combined_analysis"
        }


class SimpleHuggingFaceAnalyzer:
    """
    نسخه ساده برای زمانی که transformers نصب نیست
    Simplified version when transformers is not available
    Uses simple keyword-based sentiment
    """

    async def analyze_news_sentiment(self, news_text: str) -> Dict[str, Any]:
        """Simple keyword-based sentiment"""
        text_lower = news_text.lower()

        # Bullish keywords
        bullish_keywords = [
            'bullish', 'surge', 'rally', 'gain', 'rise', 'soar',
            'adoption', 'breakthrough', 'positive', 'growth', 'boom'
        ]

        # Bearish keywords
        bearish_keywords = [
            'bearish', 'crash', 'plunge', 'drop', 'fall', 'decline',
            'regulation', 'ban', 'hack', 'scam', 'negative', 'crisis'
        ]

        bullish_count = sum(1 for word in bullish_keywords if word in text_lower)
        bearish_count = sum(1 for word in bearish_keywords if word in text_lower)

        if bullish_count > bearish_count:
            sentiment = "bullish"
            confidence = min(0.8, bullish_count * 0.2)
        elif bearish_count > bullish_count:
            sentiment = "bearish"
            confidence = min(0.8, bearish_count * 0.2)
        else:
            sentiment = "neutral"
            confidence = 0.5

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "method": "keyword_based",
            "timestamp": datetime.now().isoformat()
        }


# Factory function
def get_analyzer() -> Any:
    """Get appropriate analyzer based on availability"""
    if TRANSFORMERS_AVAILABLE:
        return HuggingFaceAnalyzer()
    else:
        logger.warning("⚠️ Using simple analyzer (transformers not available)")
        return SimpleHuggingFaceAnalyzer()


async def main():
    """Test HuggingFace models"""
    print("\n" + "="*70)
    print("🤗 Testing HuggingFace AI Models")
    print("="*70)

    analyzer = get_analyzer()

    # Test sentiment analysis
    test_news = [
        "Bitcoin surges past $50,000 as institutional adoption accelerates",
        "SEC delays decision on crypto ETF, causing market uncertainty",
        "Ethereum network upgrade successfully completed without issues"
    ]

    print("\n📊 Testing Sentiment Analysis:")
    for i, news in enumerate(test_news, 1):
        result = await analyzer.analyze_news_sentiment(news)
        print(f"\n{i}. {news[:60]}...")
        print(f"   Sentiment: {result['sentiment']}")
        print(f"   Confidence: {result['confidence']:.2%}")

    # Test if advanced features available
    if isinstance(analyzer, HuggingFaceAnalyzer) and analyzer.models_loaded:
        print("\n\n🎯 Testing News Categorization:")
        categorization = await analyzer.categorize_news(test_news[0])
        print(f"   Category: {categorization['category']}")
        print(f"   Confidence: {categorization['confidence']:.2%}")

        print("\n\n📈 Testing Aggregated Sentiment:")
        mock_news = [
            {"title": news, "description": "", "coins": ["BTC"]}
            for news in test_news
        ]
        agg_sentiment = await analyzer.calculate_aggregated_sentiment(mock_news, "BTC")
        print(f"   Overall: {agg_sentiment['overall_sentiment']}")
        print(f"   Score: {agg_sentiment['sentiment_score']}/100")
        print(f"   Confidence: {agg_sentiment['confidence']:.2%}")


if __name__ == "__main__":
    asyncio.run(main())
