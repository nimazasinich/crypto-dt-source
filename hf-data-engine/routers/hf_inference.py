"""
HuggingFace Inference REST API Router

Endpoints:
- POST /api/v1/hf/sentiment - Sentiment analysis
- POST /api/v1/hf/summarize - Text summarization
- POST /api/v1/hf/entities - Named entity recognition
- POST /api/v1/hf/classify - Zero-shot classification

Data source: HuggingFace Inference API
All endpoints return standardized JSON with {success, source, data} format.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, Body, Query
from providers.hf_sentiment_provider import HFSentimentProvider
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger("routers.hf_inference")

# Create router
router = APIRouter(prefix="/api/v1/hf", tags=["HuggingFace AI"])

# Provider instance (singleton)
_hf_provider: Optional[HFSentimentProvider] = None


def get_hf_provider() -> HFSentimentProvider:
    """Get or create HuggingFace provider instance"""
    global _hf_provider
    if _hf_provider is None:
        _hf_provider = HFSentimentProvider()
    return _hf_provider


# ============================================================================
# REQUEST MODELS
# ============================================================================


class SentimentRequest(BaseModel):
    """Request model for sentiment analysis"""

    text: str = Field(..., min_length=3, max_length=1000, description="Text to analyze")
    model: Optional[str] = Field(None, description="Custom model ID (optional)")
    use_financial: bool = Field(False, description="Use FinBERT for financial text")


class SummarizeRequest(BaseModel):
    """Request model for text summarization"""

    text: str = Field(..., min_length=50, max_length=5000, description="Text to summarize")
    max_length: int = Field(150, ge=30, le=500, description="Maximum summary length")
    min_length: int = Field(30, ge=10, le=200, description="Minimum summary length")
    model: Optional[str] = Field(None, description="Custom model ID (optional)")


class EntitiesRequest(BaseModel):
    """Request model for entity extraction"""

    text: str = Field(..., min_length=3, max_length=1000, description="Text to analyze")
    model: Optional[str] = Field(None, description="Custom NER model (optional)")


class ClassifyRequest(BaseModel):
    """Request model for zero-shot classification"""

    text: str = Field(..., min_length=3, max_length=500, description="Text to classify")
    labels: List[str] = Field(..., min_items=2, max_items=10, description="Candidate labels")
    model: Optional[str] = Field(None, description="Custom model (optional)")


# ============================================================================
# SENTIMENT ANALYSIS
# ============================================================================


@router.post("/sentiment")
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze sentiment of text using HuggingFace transformer models.

    Uses CardiffNLP RoBERTa model by default, or FinBERT for financial text.

    Returns:
    - Sentiment label (positive, negative, neutral)
    - Confidence score
    - All class scores

    Example request body:
    ```json
    {
        "text": "Bitcoin is surging to new highs!",
        "use_financial": true
    }
    ```
    """
    provider = get_hf_provider()

    try:
        result = await provider.analyze_sentiment(
            text=request.text, model=request.model, use_financial_model=request.use_financial
        )
        return result
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return {
            "success": False,
            "source": "huggingface",
            "error": "Sentiment analysis failed",
            "details": str(e),
        }


@router.get("/sentiment")
async def analyze_sentiment_get(
    text: str = Query(..., min_length=3, max_length=500, description="Text to analyze"),
    financial: bool = Query(False, description="Use financial model"),
):
    """
    GET version of sentiment analysis for simple queries.

    Example: /api/v1/hf/sentiment?text=Bitcoin is bullish today!&financial=true
    """
    provider = get_hf_provider()

    try:
        result = await provider.analyze_sentiment(text=text, use_financial_model=financial)
        return result
    except Exception as e:
        logger.error(f"Sentiment GET error: {e}")
        return {
            "success": False,
            "source": "huggingface",
            "error": "Sentiment analysis failed",
            "details": str(e),
        }


# ============================================================================
# TEXT SUMMARIZATION
# ============================================================================


@router.post("/summarize")
async def summarize_text(request: SummarizeRequest):
    """
    Summarize text using HuggingFace BART model.

    Requires text of at least 50 characters.

    Returns:
    - Original text length
    - Summary length
    - Generated summary

    Example request body:
    ```json
    {
        "text": "Long article text here...",
        "max_length": 150,
        "min_length": 30
    }
    ```
    """
    provider = get_hf_provider()

    try:
        result = await provider.summarize_text(
            text=request.text,
            max_length=request.max_length,
            min_length=request.min_length,
            model=request.model,
        )
        return result
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        return {
            "success": False,
            "source": "huggingface",
            "error": "Summarization failed",
            "details": str(e),
        }


# ============================================================================
# NAMED ENTITY RECOGNITION
# ============================================================================


@router.post("/entities")
async def extract_entities(request: EntitiesRequest):
    """
    Extract named entities from text.

    Returns entities with:
    - Entity text
    - Entity type (PERSON, ORG, LOC, MISC, etc.)
    - Confidence score
    - Position in text

    Example request body:
    ```json
    {
        "text": "Vitalik Buterin announced Ethereum 2.0 in Berlin."
    }
    ```
    """
    provider = get_hf_provider()

    try:
        result = await provider.extract_entities(text=request.text, model=request.model)
        return result
    except Exception as e:
        logger.error(f"Entity extraction error: {e}")
        return {
            "success": False,
            "source": "huggingface",
            "error": "Entity extraction failed",
            "details": str(e),
        }


# ============================================================================
# ZERO-SHOT CLASSIFICATION
# ============================================================================


@router.post("/classify")
async def classify_text(request: ClassifyRequest):
    """
    Zero-shot text classification with custom labels.

    Classify text into any categories without training.

    Returns:
    - Classifications with scores
    - Best matching label

    Example request body:
    ```json
    {
        "text": "The stock market crashed today",
        "labels": ["business", "sports", "technology", "politics"]
    }
    ```
    """
    provider = get_hf_provider()

    try:
        result = await provider.classify_text(
            text=request.text, candidate_labels=request.labels, model=request.model
        )
        return result
    except Exception as e:
        logger.error(f"Classification error: {e}")
        return {
            "success": False,
            "source": "huggingface",
            "error": "Classification failed",
            "details": str(e),
        }


# ============================================================================
# CONVENIENCE ENDPOINTS
# ============================================================================


@router.post("/analyze")
async def full_analysis(text: str = Body(..., embed=True, min_length=10, max_length=1000)):
    """
    Perform full analysis on text: sentiment + entities.

    Convenience endpoint that combines multiple analyses.

    Example request body:
    ```json
    {
        "text": "Elon Musk announced Tesla will accept Bitcoin payments again."
    }
    ```
    """
    provider = get_hf_provider()

    try:
        # Run sentiment and entity extraction
        sentiment_result = await provider.analyze_sentiment(text)
        entities_result = await provider.extract_entities(text)

        return {
            "success": True,
            "source": "huggingface",
            "data": {
                "text": text[:100] + "..." if len(text) > 100 else text,
                "sentiment": (
                    sentiment_result.get("data", {}).get("sentiment")
                    if sentiment_result.get("success")
                    else None
                ),
                "entities": (
                    entities_result.get("data", {}).get("entities")
                    if entities_result.get("success")
                    else None
                ),
                "errors": {
                    "sentiment": (
                        sentiment_result.get("error")
                        if not sentiment_result.get("success")
                        else None
                    ),
                    "entities": (
                        entities_result.get("error") if not entities_result.get("success") else None
                    ),
                },
            },
        }
    except Exception as e:
        logger.error(f"Full analysis error: {e}")
        return {
            "success": False,
            "source": "huggingface",
            "error": "Full analysis failed",
            "details": str(e),
        }


@router.get("/crypto-sentiment")
async def crypto_sentiment(text: str = Query(..., description="Crypto-related text to analyze")):
    """
    Analyze sentiment specifically for cryptocurrency text.

    Uses FinBERT model optimized for financial/crypto content.

    Example: /api/v1/hf/crypto-sentiment?text=Bitcoin breaks $100k resistance
    """
    provider = get_hf_provider()

    try:
        result = await provider.analyze_sentiment(text=text, use_financial_model=True)
        return result
    except Exception as e:
        logger.error(f"Crypto sentiment error: {e}")
        return {
            "success": False,
            "source": "huggingface",
            "error": "Crypto sentiment analysis failed",
            "details": str(e),
        }


# ============================================================================
# MODEL INFO
# ============================================================================


@router.get("/models")
async def get_available_models():
    """
    Get list of available AI models for each task.

    Returns default models used for:
    - Sentiment analysis
    - Summarization
    - Named entity recognition
    - Classification
    """
    provider = get_hf_provider()

    try:
        result = await provider.get_available_models()
        return result
    except Exception as e:
        logger.error(f"Models info error: {e}")
        return {
            "success": False,
            "source": "huggingface",
            "error": "Failed to get models info",
            "details": str(e),
        }


# ============================================================================
# HEALTH CHECK
# ============================================================================


@router.get("/health")
async def hf_health():
    """Check health status of HuggingFace provider"""
    provider = get_hf_provider()

    return {
        "success": True,
        "provider": {
            "name": provider.name,
            "baseUrl": provider.base_url,
            "timeout": provider.timeout,
            "models": provider.MODELS,
        },
        "endpoints": [
            "POST /api/v1/hf/sentiment",
            "GET /api/v1/hf/sentiment",
            "POST /api/v1/hf/summarize",
            "POST /api/v1/hf/entities",
            "POST /api/v1/hf/classify",
            "POST /api/v1/hf/analyze",
            "GET /api/v1/hf/crypto-sentiment",
            "GET /api/v1/hf/models",
        ],
    }
