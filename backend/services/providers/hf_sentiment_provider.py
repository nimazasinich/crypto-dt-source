"""
HuggingFace Sentiment Provider - AI-powered text analysis

Provides:
- Sentiment analysis using transformer models
- Text summarization
- Named entity recognition
- Zero-shot classification

Uses HuggingFace Inference API for model inference.
API Documentation: https://huggingface.co/docs/api-inference/
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

import os

from .base import BaseProvider, create_success_response, create_error_response


class HFSentimentProvider(BaseProvider):
    """HuggingFace Inference API provider for AI-powered analysis"""
    # Never hardcode secrets. Configure via environment (HF_TOKEN).
    DEFAULT_API_KEY = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN") or ""
    
    # Default models for each task (using stable, available models)
    MODELS = {
        "sentiment": "distilbert-base-uncased-finetuned-sst-2-english",
        "sentiment_financial": "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis",
        "summarization": "sshleifer/distilbart-cnn-12-6",
        "ner": "dslim/bert-base-NER",
        "classification": "facebook/bart-large-mnli",
        "text_generation": "gpt2"
    }
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="huggingface",
            base_url="https://router.huggingface.co/hf-inference/models",
            api_key=api_key if api_key is not None else self.DEFAULT_API_KEY,
            timeout=15.0,  # HF inference can be slower
            cache_ttl=60.0  # Cache AI results for 60 seconds
        )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get headers with HuggingFace authorization"""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    async def analyze_sentiment(
        self,
        text: str,
        model: Optional[str] = None,
        use_financial_model: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of text using HuggingFace models.
        
        Args:
            text: Text to analyze
            model: Custom model to use (optional)
            use_financial_model: Use FinBERT for financial text
        
        Returns:
            Standardized response with sentiment analysis
        """
        if not text or len(text.strip()) < 3:
            return create_error_response(
                self.name,
                "Invalid text",
                "Text must be at least 3 characters"
            )
        
        # Truncate text if too long (HF has limits)
        text = text[:1000]
        
        # Select model
        if model:
            model_id = model
        elif use_financial_model:
            model_id = self.MODELS["sentiment_financial"]
        else:
            model_id = self.MODELS["sentiment"]
        
        # Build endpoint
        endpoint = f"{model_id}"
        
        response = await self.post(endpoint, json_data={"inputs": text})
        
        if not response.get("success"):
            return response
        
        data = response.get("data", [])
        
        # Handle model loading state
        if isinstance(data, dict) and data.get("error"):
            error_msg = data.get("error", "Model error")
            if "loading" in error_msg.lower():
                return create_error_response(
                    self.name,
                    "Model is loading",
                    "Please retry in a few seconds"
                )
            return create_error_response(self.name, error_msg)
        
        # Parse sentiment results
        results = self._parse_sentiment_results(data, model_id)
        
        return create_success_response(
            self.name,
            {
                "text": text[:100] + "..." if len(text) > 100 else text,
                "model": model_id,
                "sentiment": results
            }
        )
    
    def _parse_sentiment_results(self, data: Any, model_id: str) -> Dict[str, Any]:
        """Parse sentiment results from different model formats"""
        if not data:
            return {"label": "unknown", "score": 0.0}
        
        # Handle nested list format [[{label, score}, ...]]
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], list):
                data = data[0]
            
            # Find highest scoring label
            best = max(data, key=lambda x: x.get("score", 0))
            
            # Normalize label
            label = best.get("label", "unknown").lower()
            score = best.get("score", 0.0)
            
            # Map common labels
            label_map = {
                "label_0": "negative",
                "label_1": "neutral", 
                "label_2": "positive",
                "negative": "negative",
                "neutral": "neutral",
                "positive": "positive",
                "pos": "positive",
                "neg": "negative",
                "neu": "neutral"
            }
            
            normalized_label = label_map.get(label, label)
            
            return {
                "label": normalized_label,
                "score": round(score, 4),
                "allScores": [
                    {"label": item.get("label"), "score": round(item.get("score", 0), 4)}
                    for item in data
                ]
            }
        
        return {"label": "unknown", "score": 0.0}
    
    async def summarize_text(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 30,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Summarize text using HuggingFace summarization model.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length
            min_length: Minimum summary length
            model: Custom model to use
        """
        if not text or len(text.strip()) < 50:
            return create_error_response(
                self.name,
                "Text too short",
                "Text must be at least 50 characters for summarization"
            )
        
        # Truncate very long text
        text = text[:3000]
        
        model_id = model or self.MODELS["summarization"]
        
        payload = {
            "inputs": text,
            "parameters": {
                "max_length": max_length,
                "min_length": min_length,
                "do_sample": False
            }
        }
        
        response = await self.post(model_id, json_data=payload)
        
        if not response.get("success"):
            return response
        
        data = response.get("data", [])
        
        # Handle model loading
        if isinstance(data, dict) and data.get("error"):
            error_msg = data.get("error", "Model error")
            if "loading" in error_msg.lower():
                return create_error_response(
                    self.name,
                    "Model is loading",
                    "Please retry in a few seconds"
                )
            return create_error_response(self.name, error_msg)
        
        # Parse summary
        summary = ""
        if isinstance(data, list) and len(data) > 0:
            summary = data[0].get("summary_text", "")
        elif isinstance(data, dict):
            summary = data.get("summary_text", "")
        
        return create_success_response(
            self.name,
            {
                "originalLength": len(text),
                "summaryLength": len(summary),
                "model": model_id,
                "summary": summary
            }
        )
    
    async def extract_entities(
        self,
        text: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract named entities from text.
        
        Args:
            text: Text to analyze
            model: Custom NER model to use
        """
        if not text or len(text.strip()) < 3:
            return create_error_response(
                self.name,
                "Invalid text",
                "Text must be at least 3 characters"
            )
        
        text = text[:1000]
        model_id = model or self.MODELS["ner"]
        
        response = await self.post(model_id, json_data={"inputs": text})
        
        if not response.get("success"):
            return response
        
        data = response.get("data", [])
        
        if isinstance(data, dict) and data.get("error"):
            error_msg = data.get("error", "Model error")
            if "loading" in error_msg.lower():
                return create_error_response(
                    self.name,
                    "Model is loading",
                    "Please retry in a few seconds"
                )
            return create_error_response(self.name, error_msg)
        
        # Parse entities
        entities = []
        if isinstance(data, list):
            for entity in data:
                entities.append({
                    "word": entity.get("word"),
                    "entity": entity.get("entity_group") or entity.get("entity"),
                    "score": round(entity.get("score", 0), 4),
                    "start": entity.get("start"),
                    "end": entity.get("end")
                })
        
        return create_success_response(
            self.name,
            {
                "text": text[:100] + "..." if len(text) > 100 else text,
                "model": model_id,
                "entities": entities,
                "count": len(entities)
            }
        )
    
    async def classify_text(
        self,
        text: str,
        candidate_labels: List[str],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Zero-shot text classification.
        
        Args:
            text: Text to classify
            candidate_labels: List of possible labels
            model: Custom classification model
        """
        if not text or len(text.strip()) < 3:
            return create_error_response(
                self.name,
                "Invalid text",
                "Text must be at least 3 characters"
            )
        
        if not candidate_labels or len(candidate_labels) < 2:
            return create_error_response(
                self.name,
                "Invalid labels",
                "At least 2 candidate labels required"
            )
        
        text = text[:500]
        model_id = model or self.MODELS["classification"]
        
        payload = {
            "inputs": text,
            "parameters": {
                "candidate_labels": candidate_labels[:10]  # Limit labels
            }
        }
        
        response = await self.post(model_id, json_data=payload)
        
        if not response.get("success"):
            return response
        
        data = response.get("data", {})
        
        if isinstance(data, dict) and data.get("error"):
            error_msg = data.get("error", "Model error")
            if "loading" in error_msg.lower():
                return create_error_response(
                    self.name,
                    "Model is loading",
                    "Please retry in a few seconds"
                )
            return create_error_response(self.name, error_msg)
        
        # Parse classification results
        labels = data.get("labels", [])
        scores = data.get("scores", [])
        
        classifications = []
        for label, score in zip(labels, scores):
            classifications.append({
                "label": label,
                "score": round(score, 4)
            })
        
        return create_success_response(
            self.name,
            {
                "text": text[:100] + "..." if len(text) > 100 else text,
                "model": model_id,
                "classifications": classifications,
                "bestLabel": labels[0] if labels else None,
                "bestScore": round(scores[0], 4) if scores else 0.0
            }
        )
    
    async def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models for each task"""
        return create_success_response(
            self.name,
            {
                "models": self.MODELS,
                "tasks": list(self.MODELS.keys())
            }
        )
