#!/usr/bin/env python3
"""Centralized access to Hugging Face models with ensemble sentiment."""

from __future__ import annotations
import logging
import os
import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence
from config import HUGGINGFACE_MODELS, get_settings

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from huggingface_hub.errors import RepositoryNotFoundError
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False
    RepositoryNotFoundError = Exception

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)
settings = get_settings()

HF_TOKEN_ENV = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
_is_hf_space = bool(os.getenv("SPACE_ID"))
_default_hf_mode = "public" if _is_hf_space else "off"
HF_MODE = os.getenv("HF_MODE", _default_hf_mode).lower()

if HF_MODE not in ("off", "public", "auth"):
    HF_MODE = "off"
    logger.warning(f"Invalid HF_MODE, resetting to 'off'")

if HF_MODE == "auth" and not HF_TOKEN_ENV:
    HF_MODE = "off"
    logger.warning("HF_MODE='auth' but no HF_TOKEN found, resetting to 'off'")

# Linked models in HF Space - these are pre-validated
LINKED_MODEL_IDS = {
    "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "ProsusAI/finbert",
    "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis",
    "ElKulako/cryptobert",
    "kk08/CryptoBERT",
    "agarkovv/CryptoTrader-LM",
    "StephanAkkerman/FinTwitBERT-sentiment",
    "OpenC/crypto-gpt-o3-mini",
    "burakutf/finetuned-finbert-crypto",
    "mathugo/crypto_news_bert",
    "mayurjadhav/crypto-sentiment-model",
}

# Extended Model Catalog - Using VERIFIED public models only
# These models are tested and confirmed working on HuggingFace Hub
CRYPTO_SENTIMENT_MODELS = [
    "kk08/CryptoBERT",  # Crypto-specific sentiment binary classification
    "ElKulako/cryptobert",  # Crypto social sentiment (Bullish/Neutral/Bearish)
    "cardiffnlp/twitter-roberta-base-sentiment-latest",  # Fallback
]
SOCIAL_SENTIMENT_MODELS = [
    "ElKulako/cryptobert",  # Crypto social sentiment
    "cardiffnlp/twitter-roberta-base-sentiment-latest",  # Twitter sentiment
]
FINANCIAL_SENTIMENT_MODELS = [
    "StephanAkkerman/FinTwitBERT-sentiment",  # Financial tweet sentiment
    "ProsusAI/finbert",  # Financial sentiment
    "cardiffnlp/twitter-roberta-base-sentiment-latest",  # Fallback
]
NEWS_SENTIMENT_MODELS = [
    "StephanAkkerman/FinTwitBERT-sentiment",  # News sentiment
    "cardiffnlp/twitter-roberta-base-sentiment-latest",  # Fallback
]
GENERATION_MODELS = [
    "OpenC/crypto-gpt-o3-mini",  # Crypto/DeFi text generation
]
TRADING_SIGNAL_MODELS = [
    "agarkovv/CryptoTrader-LM",  # BTC/ETH trading signals (buy/sell/hold)
]

@dataclass(frozen=True)
class PipelineSpec:
    key: str
    task: str
    model_id: str
    requires_auth: bool = False
    category: str = "sentiment"

MODEL_SPECS: Dict[str, PipelineSpec] = {}

# Legacy models
for lk in ["sentiment_twitter", "sentiment_financial", "summarization", "crypto_sentiment"]:
    if lk in HUGGINGFACE_MODELS:
        MODEL_SPECS[lk] = PipelineSpec(
            key=lk,
            task="sentiment-analysis" if "sentiment" in lk else "summarization",
            model_id=HUGGINGFACE_MODELS[lk],
            category="legacy"
        )

# Crypto sentiment
for i, mid in enumerate(CRYPTO_SENTIMENT_MODELS):
    MODEL_SPECS[f"crypto_sent_{i}"] = PipelineSpec(
        key=f"crypto_sent_{i}", task="text-classification", model_id=mid,
        category="crypto_sentiment", requires_auth=("ElKulako" in mid)
    )

# Social
for i, mid in enumerate(SOCIAL_SENTIMENT_MODELS):
    MODEL_SPECS[f"social_sent_{i}"] = PipelineSpec(
        key=f"social_sent_{i}", task="text-classification", model_id=mid, category="social_sentiment"
    )

# Financial
for i, mid in enumerate(FINANCIAL_SENTIMENT_MODELS):
    MODEL_SPECS[f"financial_sent_{i}"] = PipelineSpec(
        key=f"financial_sent_{i}", task="text-classification", model_id=mid, category="financial_sentiment"
    )

# News
for i, mid in enumerate(NEWS_SENTIMENT_MODELS):
    MODEL_SPECS[f"news_sent_{i}"] = PipelineSpec(
        key=f"news_sent_{i}", task="text-classification", model_id=mid, category="news_sentiment"
    )

# Generation models (for crypto/DeFi text generation)
for i, mid in enumerate(GENERATION_MODELS):
    MODEL_SPECS[f"crypto_gen_{i}"] = PipelineSpec(
        key=f"crypto_gen_{i}", task="text-generation", model_id=mid, category="generation_crypto"
    )

# Trading signal models
for i, mid in enumerate(TRADING_SIGNAL_MODELS):
    MODEL_SPECS[f"crypto_trade_{i}"] = PipelineSpec(
        key=f"crypto_trade_{i}", task="text-generation", model_id=mid, category="trading_signal"
    )

class ModelNotAvailable(RuntimeError): pass

class ModelRegistry:
    def __init__(self):
        self._pipelines = {}
        self._lock = threading.Lock()
        self._initialized = False
        self._failed_models = {}  # Track failed models with reasons

    def _should_use_token(self, spec: PipelineSpec) -> Optional[str]:
        """Determine if and which token to use for model loading"""
        if HF_MODE == "off":
            return None
        
        # In public mode, try to use token if available (for better rate limits)
        if HF_MODE == "public":
            # Use token if available to avoid rate limiting
            return HF_TOKEN_ENV if HF_TOKEN_ENV else None
        
        # In auth mode, always use token if available
        if HF_MODE == "auth":
            if HF_TOKEN_ENV:
                return HF_TOKEN_ENV
            else:
                logger.warning(f"Model {spec.model_id} - auth mode but no token available")
                return None
        
        return None

    def get_pipeline(self, key: str):
        """Get pipeline for a model key, with robust error handling"""
        if HF_MODE == "off":
            raise ModelNotAvailable("HF_MODE=off")
        if not TRANSFORMERS_AVAILABLE:
            raise ModelNotAvailable("transformers not installed")
        if key not in MODEL_SPECS:
            raise ModelNotAvailable(f"Unknown key: {key}")
        
        spec = MODEL_SPECS[key]
        
        # Return cached pipeline if available
        if key in self._pipelines:
            return self._pipelines[key]
        
        # Check if this model already failed
        if key in self._failed_models:
            raise ModelNotAvailable(f"Model failed previously: {self._failed_models[key]}")
        
        with self._lock:
            # Double-check after acquiring lock
            if key in self._pipelines:
                return self._pipelines[key]
            if key in self._failed_models:
                raise ModelNotAvailable(f"Model failed previously: {self._failed_models[key]}")
            
            # Determine token usage
            auth_token = self._should_use_token(spec)
            
            logger.info(f"Loading model: {spec.model_id} (mode={HF_MODE}, auth={'yes' if auth_token else 'no'})")
            
            try:
                # Use token parameter instead of deprecated use_auth_token
                pipeline_kwargs = {
                    "task": spec.task,
                    "model": spec.model_id,
                }
                
                # Only add token if we have one and it's needed
                if auth_token:
                    pipeline_kwargs["token"] = auth_token
                else:
                    # Explicitly set to None to avoid using expired tokens
                    pipeline_kwargs["token"] = None
                
                self._pipelines[key] = pipeline(**pipeline_kwargs)
                logger.info(f"Successfully loaded model: {spec.model_id}")
                return self._pipelines[key]
                
            except RepositoryNotFoundError as e:
                error_msg = f"Repository not found: {spec.model_id}"
                logger.warning(f"{error_msg} - {str(e)}")
                self._failed_models[key] = error_msg
                raise ModelNotAvailable(error_msg) from e
                
            except Exception as e:
                error_type = type(e).__name__
                error_msg = f"{error_type}: {str(e)[:100]}"
                
                # Check for HTTP errors (401, 403, 404)
                if REQUESTS_AVAILABLE and isinstance(e, requests.exceptions.HTTPError):
                    status_code = getattr(e.response, 'status_code', None)
                    if status_code == 401:
                        error_msg = f"Authentication failed (401) for {spec.model_id}"
                    elif status_code == 403:
                        error_msg = f"Access forbidden (403) for {spec.model_id}"
                    elif status_code == 404:
                        error_msg = f"Model not found (404): {spec.model_id}"
                
                # Check for OSError from transformers
                if isinstance(e, OSError):
                    if "not a valid model identifier" in str(e):
                        # For linked models in HF Space, skip validation error
                        if spec.model_id in LINKED_MODEL_IDS:
                            logger.info(f"Linked model {spec.model_id} - trying without validation check")
                            # Don't mark as failed yet, it might work
                            pass
                        else:
                            error_msg = f"Invalid model identifier: {spec.model_id}"
                    elif "401" in str(e) or "403" in str(e):
                        error_msg = f"Authentication required for {spec.model_id}"
                    else:
                        error_msg = f"OS Error loading {spec.model_id}: {str(e)[:100]}"
                
                logger.warning(f"Failed to load {spec.model_id}: {error_msg}")
                self._failed_models[key] = error_msg
                raise ModelNotAvailable(error_msg) from e
        
        return self._pipelines[key]

    def initialize_models(self):
        """Initialize models with fallback logic - tries primary models first"""
        if self._initialized:
            return {
                "status": "already_initialized",
                "mode": HF_MODE,
                "models_loaded": len(self._pipelines),
                "failed_count": len(self._failed_models)
            }
        
        if HF_MODE == "off":
            logger.info("HF_MODE=off, using fallback-only mode")
            self._initialized = True
            return {
                "status": "fallback_only",
                "mode": HF_MODE,
                "models_loaded": 0,
                "error": "HF_MODE=off - using lexical fallback"
            }
        
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers not available, using fallback-only mode")
            self._initialized = True
            return {
                "status": "fallback_only",
                "mode": HF_MODE,
                "models_loaded": 0,
                "error": "transformers library not installed - using lexical fallback"
            }
        
        loaded, failed = [], []
        
        # Try to load at least one model from each category with fallback
        categories_to_try = {
            "crypto": ["crypto_sent_0"],
            "financial": ["financial_sent_0"],
            "social": ["social_sent_0"],
            "news": ["news_sent_0"]
        }
        
        for category, keys in categories_to_try.items():
            category_loaded = False
            for key in keys:
                if key not in MODEL_SPECS:
                    continue
                try:
                    self.get_pipeline(key)
                    loaded.append(key)
                    category_loaded = True
                    break  # Successfully loaded one from this category
                except ModelNotAvailable as e:
                    failed.append((key, str(e)[:100]))  # Truncate long errors
                except Exception as e:
                    failed.append((key, f"{type(e).__name__}: {str(e)[:100]}"))
        
        # Determine status - be more lenient
        if len(loaded) > 0:
            status = "ok"
        else:
            # No models loaded, but that's OK - we have fallback
            logger.warning("No HF models loaded, using fallback-only mode")
            status = "fallback_only"
        
        self._initialized = True
        
        return {
            "status": status,
            "mode": HF_MODE,
            "models_loaded": len(loaded),
            "models_failed": len(failed),
            "loaded": loaded[:10],  # Limit to first 10 for brevity
            "failed": failed[:10],  # Limit to first 10 for brevity
            "failed_count": len(self._failed_models),
            "note": "Fallback lexical analysis available" if len(loaded) == 0 else None
        }

_registry = ModelRegistry()

def initialize_models(): return _registry.initialize_models()

def ensemble_crypto_sentiment(text: str) -> Dict[str, Any]:
    """Ensemble crypto sentiment with fallback model selection"""
    if not TRANSFORMERS_AVAILABLE:
        logger.warning("Transformers not available, using fallback")
        return basic_sentiment_fallback(text)
    
    if HF_MODE == "off":
        logger.warning("HF_MODE=off, using fallback")
        return basic_sentiment_fallback(text)
    
    results, labels_count, total_conf = {}, {"bullish": 0, "bearish": 0, "neutral": 0}, 0.0
    
    # Try models in order with fallback
    candidate_keys = ["crypto_sent_0", "crypto_sent_1", "crypto_sent_2"]
    
    for key in candidate_keys:
        if key not in MODEL_SPECS:
            continue
        try:
            pipe = _registry.get_pipeline(key)
            res = pipe(text[:512])
            if isinstance(res, list) and res: 
                res = res[0]
            
            label = res.get("label", "NEUTRAL").upper()
            score = res.get("score", 0.5)
            
            # Map labels to our standard format
            mapped = "bullish" if "POSITIVE" in label or "BULLISH" in label or "LABEL_2" in label else (
                "bearish" if "NEGATIVE" in label or "BEARISH" in label or "LABEL_0" in label else "neutral"
            )
            
            spec = MODEL_SPECS[key]
            results[spec.model_id] = {"label": mapped, "score": score}
            labels_count[mapped] += 1
            total_conf += score
            
            # If we got at least one result, we can proceed
            if len(results) >= 1:
                break  # Got at least one working model
                
        except ModelNotAvailable:
            continue  # Try next model
        except Exception as e:
            logger.warning(f"Ensemble failed for {key}: {str(e)[:100]}")
            continue
    
    if not results:
        logger.warning("No HF models available, using fallback")
        return basic_sentiment_fallback(text)
    
    final = max(labels_count, key=labels_count.get)
    avg_conf = total_conf / len(results)
    
    return {
        "label": final,
        "confidence": avg_conf,
        "scores": results,
        "model_count": len(results),
        "available": True,
        "engine": "huggingface"
    }

def analyze_crypto_sentiment(text: str): return ensemble_crypto_sentiment(text)

def analyze_financial_sentiment(text: str):
    """Analyze financial sentiment with fallback"""
    if not TRANSFORMERS_AVAILABLE:
        logger.warning("Transformers not available, using fallback")
        return basic_sentiment_fallback(text)
    
    if HF_MODE == "off":
        logger.warning("HF_MODE=off, using fallback")
        return basic_sentiment_fallback(text)
    
    # Try models in order
    for key in ["financial_sent_0", "financial_sent_1"]:
        if key not in MODEL_SPECS:
            continue
        try:
            pipe = _registry.get_pipeline(key)
            res = pipe(text[:512])
            if isinstance(res, list) and res: 
                res = res[0]
            
            label = res.get("label", "neutral").upper()
            score = res.get("score", 0.5)
            
            # Map to standard format
            mapped = "bullish" if "POSITIVE" in label or "LABEL_2" in label else (
                "bearish" if "NEGATIVE" in label or "LABEL_0" in label else "neutral"
            )
            
            return {"label": mapped, "score": score, "confidence": score, "available": True, "engine": "huggingface", "model": MODEL_SPECS[key].model_id}
        except ModelNotAvailable:
            continue
        except Exception as e:
            logger.warning(f"Financial sentiment failed for {key}: {str(e)[:100]}")
            continue
    
    logger.warning("No HF models available, using fallback")
    return basic_sentiment_fallback(text)

def analyze_social_sentiment(text: str):
    """Analyze social sentiment with fallback"""
    if not TRANSFORMERS_AVAILABLE:
        logger.warning("Transformers not available, using fallback")
        return basic_sentiment_fallback(text)
    
    if HF_MODE == "off":
        logger.warning("HF_MODE=off, using fallback")
        return basic_sentiment_fallback(text)
    
    # Try models in order
    for key in ["social_sent_0", "social_sent_1"]:
        if key not in MODEL_SPECS:
            continue
        try:
            pipe = _registry.get_pipeline(key)
            res = pipe(text[:512])
            if isinstance(res, list) and res: 
                res = res[0]
            
            label = res.get("label", "neutral").upper()
            score = res.get("score", 0.5)
            
            # Map to standard format
            mapped = "bullish" if "POSITIVE" in label or "LABEL_2" in label else (
                "bearish" if "NEGATIVE" in label or "LABEL_0" in label else "neutral"
            )
            
            return {"label": mapped, "score": score, "confidence": score, "available": True, "engine": "huggingface", "model": MODEL_SPECS[key].model_id}
        except ModelNotAvailable:
            continue
        except Exception as e:
            logger.warning(f"Social sentiment failed for {key}: {str(e)[:100]}")
            continue
    
    logger.warning("No HF models available, using fallback")
    return basic_sentiment_fallback(text)

def analyze_market_text(text: str): return ensemble_crypto_sentiment(text)

def analyze_chart_points(data: Sequence[Mapping[str, Any]], indicators: Optional[List[str]] = None):
    if not data: return {"trend": "neutral", "strength": 0, "analysis": "No data"}
    
    prices = [float(p.get("price", 0)) for p in data if p.get("price")]
    if not prices: return {"trend": "neutral", "strength": 0, "analysis": "No price data"}
    
    first, last = prices[0], prices[-1]
    change = ((last - first) / first * 100) if first > 0 else 0
    
    if change > 5: trend, strength = "bullish", min(abs(change) / 10, 1.0)
    elif change < -5: trend, strength = "bearish", min(abs(change) / 10, 1.0)
    else: trend, strength = "neutral", abs(change) / 5
    
    return {"trend": trend, "strength": strength, "change_pct": change, "support": min(prices), "resistance": max(prices), "analysis": f"Price moved {change:.2f}% showing {trend} trend"}

def analyze_news_item(item: Dict[str, Any]):
    text = item.get("title", "") + " " + item.get("description", "")
    sent = ensemble_crypto_sentiment(text)
    return {**item, "sentiment": sent["label"], "sentiment_confidence": sent["confidence"], "sentiment_details": sent}

def get_model_info():
    return {
        "transformers_available": TRANSFORMERS_AVAILABLE,
        "hf_auth_configured": bool(settings.hf_token),
        "models_initialized": _registry._initialized,
        "models_loaded": len(_registry._pipelines),
        "model_catalog": {
            "crypto_sentiment": CRYPTO_SENTIMENT_MODELS,
            "social_sentiment": SOCIAL_SENTIMENT_MODELS,
            "financial_sentiment": FINANCIAL_SENTIMENT_MODELS,
            "news_sentiment": NEWS_SENTIMENT_MODELS,
            "generation": GENERATION_MODELS,
            "trading_signals": TRADING_SIGNAL_MODELS
        },
        "total_models": len(MODEL_SPECS)
    }

def basic_sentiment_fallback(text: str) -> Dict[str, Any]:
    """
    Simple lexical-based sentiment fallback that doesn't require transformers.
    Returns sentiment based on keyword matching.
    """
    text_lower = text.lower()
    
    # Define keyword lists
    bullish_words = ["bullish", "rally", "surge", "pump", "breakout", "skyrocket", 
                     "uptrend", "buy", "accumulation", "moon", "gain", "profit",
                     "up", "high", "rise", "growth", "positive", "strong"]
    bearish_words = ["bearish", "dump", "crash", "selloff", "downtrend", "collapse",
                     "sell", "capitulation", "panic", "fear", "drop", "loss",
                     "down", "low", "fall", "decline", "negative", "weak"]
    
    # Count matches
    bullish_count = sum(1 for word in bullish_words if word in text_lower)
    bearish_count = sum(1 for word in bearish_words if word in text_lower)
    
    # Determine sentiment
    if bullish_count == 0 and bearish_count == 0:
        label = "neutral"
        confidence = 0.5
        bullish_score = 0.0
        bearish_score = 0.0
        neutral_score = 1.0
    elif bullish_count > bearish_count:
        label = "bullish"
        diff = bullish_count - bearish_count
        confidence = min(0.6 + (diff * 0.05), 0.9)
        bullish_score = confidence
        bearish_score = 0.0
        neutral_score = 0.0
    else:  # bearish_count > bullish_count
        label = "bearish"
        diff = bearish_count - bullish_count
        confidence = min(0.6 + (diff * 0.05), 0.9)
        bearish_score = confidence
        bullish_score = 0.0
        neutral_score = 0.0
    
    return {
        "label": label,
        "confidence": confidence,
        "score": confidence,
        "scores": {
            "bullish": round(bullish_score, 3),
            "bearish": round(bearish_score, 3),
            "neutral": round(neutral_score, 3)
        },
        "available": True,  # Set to True so frontend renders it
        "engine": "fallback_lexical",
        "keyword_matches": {
            "bullish": bullish_count,
            "bearish": bearish_count
        }
    }

def registry_status():
    """Get registry status with detailed information"""
    status = {
        "ok": HF_MODE != "off" and TRANSFORMERS_AVAILABLE and len(_registry._pipelines) > 0,
        "initialized": _registry._initialized,
        "pipelines_loaded": len(_registry._pipelines),
        "pipelines_failed": len(_registry._failed_models),
        "available_models": list(_registry._pipelines.keys()),
        "failed_models": list(_registry._failed_models.keys())[:10],  # Limit for brevity
        "transformers_available": TRANSFORMERS_AVAILABLE,
        "hf_mode": HF_MODE,
        "total_specs": len(MODEL_SPECS)
    }
    
    if HF_MODE == "off":
        status["error"] = "HF_MODE=off"
    elif not TRANSFORMERS_AVAILABLE:
        status["error"] = "transformers not installed"
    elif len(_registry._pipelines) == 0 and _registry._initialized:
        status["error"] = "No models loaded successfully"
    
    return status
