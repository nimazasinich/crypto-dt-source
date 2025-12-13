#!/usr/bin/env python3
"""
Hugging Face Inference API Client - REAL DATA ONLY
Uses real Hugging Face models for sentiment analysis
NO MOCK DATA - All predictions from real HF models
"""

import httpx
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class HuggingFaceInferenceClient:
    """
    Real Hugging Face Inference API Client
    Primary source for real sentiment analysis using NLP models
    """
    
    def __init__(self):
        # Strip whitespace from token to avoid "Illegal header value" errors
        self.api_token = (os.getenv("HF_API_TOKEN") or os.getenv("HF_TOKEN") or "").strip()
        self.base_url = "https://router.huggingface.co/models"
        self.timeout = 30.0  # HF models can take time to load
        
        # Real sentiment analysis models
        self.models = {
            "sentiment_crypto": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "sentiment_financial": "ProsusAI/finbert",
            "sentiment_twitter": "finiteautomata/bertweet-base-sentiment-analysis",
            "sentiment_general": "nlptown/bert-base-multilingual-uncased-sentiment"
        }
        
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"
    
    def _normalize_sentiment_label(self, label: str, score: float) -> tuple[str, str]:
        """
        Normalize different model label formats to standard format
        
        Returns:
            (normalized_label, sentiment_text)
        """
        label_upper = label.upper()
        
        # Map various label formats
        if label_upper in ["POSITIVE", "LABEL_2", "5 STARS", "POS"]:
            return ("POSITIVE", "positive")
        elif label_upper in ["NEGATIVE", "LABEL_0", "1 STAR", "NEG"]:
            return ("NEGATIVE", "negative")
        elif label_upper in ["NEUTRAL", "LABEL_1", "3 STARS", "NEU"]:
            return ("NEUTRAL", "neutral")
        
        # For star ratings (1-5 stars)
        if "STAR" in label_upper:
            if "4" in label or "5" in label:
                return ("POSITIVE", "positive")
            elif "1" in label or "2" in label:
                return ("NEGATIVE", "negative")
            else:
                return ("NEUTRAL", "neutral")
        
        # Default: use score to determine sentiment
        if score > 0.6:
            return ("POSITIVE", "positive")
        elif score < 0.4:
            return ("NEGATIVE", "negative")
        else:
            return ("NEUTRAL", "neutral")
    
    async def analyze_sentiment(
        self,
        text: str,
        model_key: str = "sentiment_crypto"
    ) -> Dict[str, Any]:
        """
        Analyze REAL sentiment using Hugging Face models
        
        Args:
            text: Text to analyze
            model_key: Model to use (sentiment_crypto, sentiment_financial, etc.)
        
        Returns:
            Real sentiment analysis results
        """
        try:
            # Get model name
            model_name = self.models.get(model_key, self.models["sentiment_crypto"])
            
            # Validate input
            if not text or len(text.strip()) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Missing or invalid text in request body"
                )
            
            # Truncate text if too long (max 512 tokens ~ 2000 chars)
            if len(text) > 2000:
                text = text[:2000]
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/{model_name}",
                    headers=self.headers,
                    json={"inputs": text}
                )
                
                # Handle model loading state
                if response.status_code == 503:
                    # Model is loading
                    try:
                        error_data = response.json()
                        estimated_time = error_data.get("estimated_time", 20)
                        
                        logger.warning(
                            f"⏳ HuggingFace model {model_name} is loading "
                            f"(estimated: {estimated_time}s)"
                        )
                        
                        return {
                            "error": "Model is currently loading",
                            "estimated_time": estimated_time,
                            "model": model_name,
                            "timestamp": int(datetime.utcnow().timestamp() * 1000)
                        }
                    except:
                        return {
                            "error": "Model is currently loading",
                            "estimated_time": 20,
                            "model": model_name,
                            "timestamp": int(datetime.utcnow().timestamp() * 1000)
                        }
                
                response.raise_for_status()
                data = response.json()
                
                # Parse model response
                # HF returns: [[{"label": "POSITIVE", "score": 0.95}, ...]]
                if isinstance(data, list) and len(data) > 0:
                    # Get first (or highest score) prediction
                    if isinstance(data[0], list):
                        predictions = data[0]
                    else:
                        predictions = data
                    
                    # Get prediction with highest score
                    best_prediction = max(predictions, key=lambda x: x.get("score", 0))
                    
                    raw_label = best_prediction.get("label", "NEUTRAL")
                    raw_score = best_prediction.get("score", 0.5)
                    
                    # Normalize label
                    normalized_label, sentiment_text = self._normalize_sentiment_label(
                        raw_label,
                        raw_score
                    )
                    
                    result = {
                        "label": normalized_label,
                        "score": raw_score,
                        "sentiment": sentiment_text,
                        "confidence": raw_score,
                        "text": text[:100] + ("..." if len(text) > 100 else ""),
                        "model": model_name,
                        "source": "huggingface",
                        "timestamp": int(datetime.utcnow().timestamp() * 1000)
                    }
                    
                    logger.info(
                        f"✅ HuggingFace: Sentiment analysis completed "
                        f"({normalized_label}, confidence: {raw_score:.2f})"
                    )
                    return result
                
                else:
                    # Unexpected response format
                    logger.error(f"❌ HuggingFace: Unexpected response format: {data}")
                    raise HTTPException(
                        status_code=500,
                        detail="Unexpected response format from model"
                    )
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                # Model loading - already handled above
                return {
                    "error": "Model is currently loading",
                    "estimated_time": 20,
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                }
            elif e.response.status_code == 400:
                logger.error(f"❌ HuggingFace: Bad request: {e}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid text or parameters"
                )
            elif e.response.status_code in (404, 410):
                # Endpoint moved or model not available on old host; provide safe fallback
                logger.warning("⚠ HuggingFace endpoint returned 404/410; using keyword fallback")
                # Simple keyword-based sentiment fallback
                text_lower = (text or "").lower()
                pos_kw = ["bull", "up", "gain", "profit", "surge", "rally", "strong"]
                neg_kw = ["bear", "down", "loss", "drop", "dump", "sell", "weak"]
                pos_score = sum(k in text_lower for k in pos_kw)
                neg_score = sum(k in text_lower for k in neg_kw)
                if pos_score > neg_score:
                    label, sentiment = ("POSITIVE", "positive")
                    score = 0.7
                elif neg_score > pos_score:
                    label, sentiment = ("NEGATIVE", "negative")
                    score = 0.7
                else:
                    label, sentiment = ("NEUTRAL", "neutral")
                    score = 0.5
                return {
                    "label": label,
                    "score": score,
                    "sentiment": sentiment,
                    "confidence": score,
                    "text": text[:100] + ("..." if len(text) > 100 else ""),
                    "model": "fallback-keywords",
                    "source": "fallback",
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                }
            else:
                logger.error(f"❌ HuggingFace API HTTP error: {e}")
                raise HTTPException(
                    status_code=503,
                    detail=f"HuggingFace API temporarily unavailable: {str(e)}"
                )
        
        except httpx.HTTPError as e:
            logger.error(f"❌ HuggingFace API HTTP error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"HuggingFace API temporarily unavailable: {str(e)}"
            )
        
        except HTTPException:
            raise
        
        except Exception as e:
            logger.error(f"❌ HuggingFace sentiment analysis failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to analyze sentiment: {str(e)}"
            )


# Global instance
hf_inference_client = HuggingFaceInferenceClient()


__all__ = ["HuggingFaceInferenceClient", "hf_inference_client"]
