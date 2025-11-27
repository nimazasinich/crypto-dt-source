#!/usr/bin/env python3
"""
Real AI Models Service - ZERO MOCK DATA
All AI predictions use REAL models from HuggingFace
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

# Try to import transformers - if not available, use HF API
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("⚠ Transformers not available, will use HF API")

import httpx
from backend.services.real_api_clients import RealAPIConfiguration


class RealAIModelsRegistry:
    """
    Real AI Models Registry using HuggingFace models
    NO MOCK PREDICTIONS - Only real model inference
    """

    def __init__(self):
        self.models = {}
        self.loaded = False
        import os

        self.hf_api_token = os.getenv("HF_API_TOKEN", RealAPIConfiguration.HF_API_TOKEN)
        self.hf_api_url = "https://api-inference.huggingface.co/models"

        # Model configurations - REAL HuggingFace models
        self.model_configs = {
            "sentiment_crypto": {
                "model_id": "ElKulako/cryptobert",
                "task": "sentiment-analysis",
                "description": "CryptoBERT for crypto sentiment analysis",
            },
            "sentiment_twitter": {
                "model_id": "cardiffnlp/twitter-roberta-base-sentiment",
                "task": "sentiment-analysis",
                "description": "Twitter sentiment analysis",
            },
            "sentiment_financial": {
                "model_id": "ProsusAI/finbert",
                "task": "sentiment-analysis",
                "description": "FinBERT for financial sentiment",
            },
            "text_generation": {
                "model_id": "OpenC/crypto-gpt-o3-mini",
                "task": "text-generation",
                "description": "Crypto GPT for text generation",
            },
            "trading_signals": {
                "model_id": "agarkovv/CryptoTrader-LM",
                "task": "text-generation",
                "description": "CryptoTrader LM for trading signals",
            },
            "summarization": {
                "model_id": "facebook/bart-large-cnn",
                "task": "summarization",
                "description": "BART for news summarization",
            },
        }

    async def load_models(self):
        """
        Load REAL models from HuggingFace
        """
        if self.loaded:
            return {"status": "already_loaded", "models": len(self.models)}

        logger.info("🤖 Loading REAL AI models from HuggingFace...")

        if TRANSFORMERS_AVAILABLE:
            # Load models locally using transformers
            for model_key, config in self.model_configs.items():
                try:
                    if config["task"] == "sentiment-analysis":
                        self.models[model_key] = pipeline(
                            config["task"],
                            model=config["model_id"],
                            truncation=True,
                            max_length=512,
                        )
                        logger.info(f"✅ Loaded local model: {config['model_id']}")
                    # For text generation, we'll use API to avoid heavy downloads
                except Exception as e:
                    logger.warning(f"⚠ Could not load {model_key} locally: {e}")

        self.loaded = True
        return {
            "status": "loaded",
            "models_local": len(self.models),
            "models_api": len(self.model_configs) - len(self.models),
            "total": len(self.model_configs),
        }

    async def predict_sentiment(
        self, text: str, model_key: str = "sentiment_crypto"
    ) -> Dict[str, Any]:
        """
        Run REAL sentiment analysis using HuggingFace models
        NO FAKE PREDICTIONS
        """
        try:
            # Check if model is loaded locally
            if model_key in self.models:
                # Use local model
                result = self.models[model_key](text)[0]

                return {
                    "success": True,
                    "label": result["label"],
                    "score": result["score"],
                    "model": model_key,
                    "source": "local",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            else:
                # Use HuggingFace API
                return await self._predict_via_api(text, model_key)

        except Exception as e:
            logger.error(f"❌ Sentiment prediction failed: {e}")
            raise Exception(f"Failed to predict sentiment: {str(e)}")

    async def generate_text(
        self, prompt: str, model_key: str = "text_generation", max_length: int = 200
    ) -> Dict[str, Any]:
        """
        Generate REAL text using HuggingFace models
        NO FAKE GENERATION
        """
        try:
            return await self._generate_via_api(prompt, model_key, max_length)
        except Exception as e:
            logger.error(f"❌ Text generation failed: {e}")
            raise Exception(f"Failed to generate text: {str(e)}")

    async def get_trading_signal(
        self, symbol: str, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get REAL trading signal using CryptoTrader-LM
        NO FAKE SIGNALS
        """
        try:
            # Prepare prompt for trading model
            prompt = f"Trading signal for {symbol}."
            if context:
                prompt += f" Context: {context}"

            result = await self._generate_via_api(prompt, "trading_signals", max_length=100)

            # Parse trading signal from generated text
            generated_text = result.get("generated_text", "").upper()

            # Determine signal type
            if "BUY" in generated_text or "BULLISH" in generated_text:
                signal_type = "BUY"
                score = 0.75
            elif "SELL" in generated_text or "BEARISH" in generated_text:
                signal_type = "SELL"
                score = 0.75
            else:
                signal_type = "HOLD"
                score = 0.60

            return {
                "success": True,
                "symbol": symbol,
                "signal": signal_type,
                "score": score,
                "explanation": result.get("generated_text", ""),
                "model": "trading_signals",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Trading signal failed: {e}")
            raise Exception(f"Failed to get trading signal: {str(e)}")

    async def summarize_news(self, text: str) -> Dict[str, Any]:
        """
        Summarize REAL news using BART
        NO FAKE SUMMARIES
        """
        try:
            return await self._summarize_via_api(text)
        except Exception as e:
            logger.error(f"❌ News summarization failed: {e}")
            raise Exception(f"Failed to summarize news: {str(e)}")

    async def _predict_via_api(self, text: str, model_key: str) -> Dict[str, Any]:
        """
        Run REAL inference via HuggingFace API
        """
        config = self.model_configs.get(model_key)
        if not config:
            raise ValueError(f"Unknown model: {model_key}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.hf_api_url}/{config['model_id']}",
                headers={
                    "Authorization": f"Bearer {self.hf_api_token}",
                    "Content-Type": "application/json",
                },
                json={"inputs": text},
            )
            response.raise_for_status()
            result = response.json()

        # Parse result based on task type
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], list):
                result = result[0]

            if isinstance(result[0], dict):
                top_result = result[0]
                return {
                    "success": True,
                    "label": top_result.get("label", "neutral"),
                    "score": top_result.get("score", 0.0),
                    "model": model_key,
                    "source": "hf_api",
                    "timestamp": datetime.utcnow().isoformat(),
                }

        return {
            "success": True,
            "result": result,
            "model": model_key,
            "source": "hf_api",
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _generate_via_api(
        self, prompt: str, model_key: str, max_length: int = 200
    ) -> Dict[str, Any]:
        """
        Generate REAL text via HuggingFace API
        """
        config = self.model_configs.get(model_key)
        if not config:
            raise ValueError(f"Unknown model: {model_key}")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.hf_api_url}/{config['model_id']}",
                headers={
                    "Authorization": f"Bearer {self.hf_api_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_length": max_length,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "do_sample": True,
                    },
                },
            )
            response.raise_for_status()
            result = response.json()

        # Parse result
        if isinstance(result, list) and len(result) > 0:
            generated = result[0].get("generated_text", "")
        else:
            generated = result.get("generated_text", str(result))

        return {
            "success": True,
            "generated_text": generated,
            "model": model_key,
            "source": "hf_api",
            "prompt": prompt,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _summarize_via_api(self, text: str) -> Dict[str, Any]:
        """
        Summarize REAL text via HuggingFace API
        """
        config = self.model_configs["summarization"]

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.hf_api_url}/{config['model_id']}",
                headers={
                    "Authorization": f"Bearer {self.hf_api_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "inputs": text,
                    "parameters": {"max_length": 130, "min_length": 30, "do_sample": False},
                },
            )
            response.raise_for_status()
            result = response.json()

        # Parse result
        if isinstance(result, list) and len(result) > 0:
            summary = result[0].get("summary_text", "")
        else:
            summary = result.get("summary_text", str(result))

        return {
            "success": True,
            "summary": summary,
            "model": "summarization",
            "source": "hf_api",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_models_list(self) -> Dict[str, Any]:
        """
        Get list of available REAL models
        """
        models_list = []
        for key, config in self.model_configs.items():
            models_list.append(
                {
                    "key": key,
                    "model_id": config["model_id"],
                    "task": config["task"],
                    "description": config["description"],
                    "loaded_locally": key in self.models,
                    "available": True,
                }
            )

        return {
            "success": True,
            "models": models_list,
            "total": len(models_list),
            "loaded_locally": len(self.models),
            "timestamp": datetime.utcnow().isoformat(),
        }


# Global instance
ai_registry = RealAIModelsRegistry()


# Export
__all__ = ["RealAIModelsRegistry", "ai_registry"]
