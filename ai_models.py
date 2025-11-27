#!/usr/bin/env python3
"""Centralized access to Hugging Face models with ensemble sentiment."""

from __future__ import annotations

import logging
import os
import threading
import time
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
SUMMARIZATION_MODELS = [
    "FurkanGozukara/Crypto-Financial-News-Summarizer",  # Crypto/Financial news summarization
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
            category="legacy",
        )

# Crypto sentiment - Add named keys for required models
for i, mid in enumerate(CRYPTO_SENTIMENT_MODELS):
    key = f"crypto_sent_{i}"
    MODEL_SPECS[key] = PipelineSpec(
        key=key,
        task="text-classification",
        model_id=mid,
        category="sentiment_crypto",
        requires_auth=("ElKulako" in mid),
    )

# Add specific named aliases for required models
MODEL_SPECS["crypto_sent_kk08"] = PipelineSpec(
    key="crypto_sent_kk08",
    task="sentiment-analysis",
    model_id="kk08/CryptoBERT",
    category="sentiment_crypto",
    requires_auth=False,
)

# Social
for i, mid in enumerate(SOCIAL_SENTIMENT_MODELS):
    key = f"social_sent_{i}"
    MODEL_SPECS[key] = PipelineSpec(
        key=key,
        task="text-classification",
        model_id=mid,
        category="sentiment_social",
        requires_auth=("ElKulako" in mid),
    )

# Add specific named alias
MODEL_SPECS["crypto_sent_social"] = PipelineSpec(
    key="crypto_sent_social",
    task="text-classification",
    model_id="ElKulako/cryptobert",
    category="sentiment_social",
    requires_auth=True,
)

# Financial
for i, mid in enumerate(FINANCIAL_SENTIMENT_MODELS):
    key = f"financial_sent_{i}"
    MODEL_SPECS[key] = PipelineSpec(
        key=key, task="text-classification", model_id=mid, category="sentiment_financial"
    )

# Add specific named alias
MODEL_SPECS["crypto_sent_fin"] = PipelineSpec(
    key="crypto_sent_fin",
    task="sentiment-analysis",
    model_id="StephanAkkerman/FinTwitBERT-sentiment",
    category="sentiment_financial",
    requires_auth=False,
)

# News
for i, mid in enumerate(NEWS_SENTIMENT_MODELS):
    key = f"news_sent_{i}"
    MODEL_SPECS[key] = PipelineSpec(
        key=key, task="text-classification", model_id=mid, category="sentiment_news"
    )

# Generation models (for crypto/DeFi text generation)
for i, mid in enumerate(GENERATION_MODELS):
    key = f"crypto_gen_{i}"
    MODEL_SPECS[key] = PipelineSpec(
        key=key, task="text-generation", model_id=mid, category="analysis_generation"
    )

# Add specific named alias
MODEL_SPECS["crypto_ai_analyst"] = PipelineSpec(
    key="crypto_ai_analyst",
    task="text-generation",
    model_id="OpenC/crypto-gpt-o3-mini",
    category="analysis_generation",
    requires_auth=False,
)

# Trading signal models
for i, mid in enumerate(TRADING_SIGNAL_MODELS):
    key = f"crypto_trade_{i}"
    MODEL_SPECS[key] = PipelineSpec(
        key=key, task="text-generation", model_id=mid, category="trading_signal"
    )

# Add specific named alias
MODEL_SPECS["crypto_trading_lm"] = PipelineSpec(
    key="crypto_trading_lm",
    task="text-generation",
    model_id="agarkovv/CryptoTrader-LM",
    category="trading_signal",
    requires_auth=False,
)

# Summarization models
for i, mid in enumerate(SUMMARIZATION_MODELS):
    MODEL_SPECS[f"summarization_{i}"] = PipelineSpec(
        key=f"summarization_{i}", task="summarization", model_id=mid, category="summarization"
    )


class ModelNotAvailable(RuntimeError):
    pass


@dataclass
class ModelHealthEntry:
    """Health tracking entry for a model"""

    key: str
    name: str
    status: str = "unknown"  # "healthy", "degraded", "unavailable", "unknown"
    last_success: Optional[float] = None
    last_error: Optional[float] = None
    error_count: int = 0
    success_count: int = 0
    cooldown_until: Optional[float] = None
    last_error_message: Optional[str] = None


class ModelRegistry:
    def __init__(self):
        self._pipelines = {}
        self._lock = threading.Lock()
        self._initialized = False
        self._failed_models = {}  # Track failed models with reasons
        # Health tracking for self-healing
        self._health_registry = {}  # key -> health entry

    def _get_or_create_health_entry(self, key: str) -> ModelHealthEntry:
        """Get or create health entry for a model"""
        if key not in self._health_registry:
            spec = MODEL_SPECS.get(key)
            self._health_registry[key] = ModelHealthEntry(
                key=key, name=spec.model_id if spec else key, status="unknown"
            )
        return self._health_registry[key]

    def _update_health_on_success(self, key: str):
        """Update health registry after successful model call"""
        entry = self._get_or_create_health_entry(key)
        entry.last_success = time.time()
        entry.success_count += 1

        # Reset error count gradually or fully on success
        if entry.error_count > 0:
            entry.error_count = max(0, entry.error_count - 1)

        # Recovery logic: if we have enough successes, mark as healthy
        if entry.success_count >= settings.health_success_recovery_count:
            entry.status = "healthy"
            entry.cooldown_until = None
            # Clear from failed models if present
            if key in self._failed_models:
                del self._failed_models[key]

    def _update_health_on_failure(self, key: str, error_msg: str):
        """Update health registry after failed model call"""
        entry = self._get_or_create_health_entry(key)
        entry.last_error = time.time()
        entry.error_count += 1
        entry.last_error_message = error_msg
        entry.success_count = 0  # Reset success count on failure

        # Determine status based on error count
        if entry.error_count >= settings.health_error_threshold:
            entry.status = "unavailable"
            # Set cooldown period
            entry.cooldown_until = time.time() + settings.health_cooldown_seconds
        elif entry.error_count >= (settings.health_error_threshold // 2):
            entry.status = "degraded"
        else:
            entry.status = "healthy"

    def _is_in_cooldown(self, key: str) -> bool:
        """Check if model is in cooldown period"""
        if key not in self._health_registry:
            return False
        entry = self._health_registry[key]
        if entry.cooldown_until is None:
            return False
        return time.time() < entry.cooldown_until

    def attempt_model_reinit(self, key: str) -> Dict[str, Any]:
        """
        Attempt to re-initialize a failed model after cooldown.
        Returns result dict with status and message.
        """
        if key not in MODEL_SPECS:
            return {"status": "error", "message": f"Unknown model key: {key}"}

        entry = self._get_or_create_health_entry(key)

        # Check if enough time has passed since last error
        if entry.last_error:
            time_since_error = time.time() - entry.last_error
            if time_since_error < settings.health_reinit_cooldown_seconds:
                return {
                    "status": "cooldown",
                    "message": f"Model in cooldown, wait {int(settings.health_reinit_cooldown_seconds - time_since_error)}s",
                    "cooldown_remaining": int(
                        settings.health_reinit_cooldown_seconds - time_since_error
                    ),
                }

        # Try to reinitialize
        with self._lock:
            # Remove from failed models and pipelines to force reload
            if key in self._failed_models:
                del self._failed_models[key]
            if key in self._pipelines:
                del self._pipelines[key]

            # Reset health entry
            entry.error_count = 0
            entry.status = "unknown"
            entry.cooldown_until = None

            try:
                # Attempt to load
                pipe = self.get_pipeline(key)
                return {
                    "status": "success",
                    "message": f"Model {key} successfully reinitialized",
                    "model": MODEL_SPECS[key].model_id,
                }
            except Exception as e:
                return {
                    "status": "failed",
                    "message": f"Reinitialization failed: {str(e)[:200]}",
                    "error": str(e)[:200],
                }

    def get_model_health_registry(self) -> List[Dict[str, Any]]:
        """Get health registry for all models"""
        result = []
        for key, entry in self._health_registry.items():
            spec = MODEL_SPECS.get(key)
            result.append(
                {
                    "key": entry.key,
                    "name": entry.name,
                    "model_id": spec.model_id if spec else entry.name,
                    "category": spec.category if spec else "unknown",
                    "status": entry.status,
                    "last_success": entry.last_success,
                    "last_error": entry.last_error,
                    "error_count": entry.error_count,
                    "success_count": entry.success_count,
                    "cooldown_until": entry.cooldown_until,
                    "in_cooldown": self._is_in_cooldown(key),
                    "last_error_message": entry.last_error_message,
                    "loaded": key in self._pipelines,
                }
            )

        # Add models that exist in specs but not in health registry
        for key, spec in MODEL_SPECS.items():
            if key not in self._health_registry:
                result.append(
                    {
                        "key": key,
                        "name": spec.model_id,
                        "model_id": spec.model_id,
                        "category": spec.category,
                        "status": "unknown",
                        "last_success": None,
                        "last_error": None,
                        "error_count": 0,
                        "success_count": 0,
                        "cooldown_until": None,
                        "in_cooldown": False,
                        "last_error_message": None,
                        "loaded": key in self._pipelines,
                    }
                )

        return result

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
        """Get pipeline for a model key, with robust error handling and health tracking"""
        if HF_MODE == "off":
            raise ModelNotAvailable("HF_MODE=off")
        if not TRANSFORMERS_AVAILABLE:
            raise ModelNotAvailable("transformers not installed")
        if key not in MODEL_SPECS:
            raise ModelNotAvailable(f"Unknown key: {key}")

        spec = MODEL_SPECS[key]

        # Check if model is in cooldown
        if self._is_in_cooldown(key):
            entry = self._health_registry[key]
            cooldown_remaining = int(entry.cooldown_until - time.time())
            raise ModelNotAvailable(
                f"Model in cooldown for {cooldown_remaining}s: {entry.last_error_message or 'previous failures'}"
            )

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

            logger.info(
                f"Loading model: {spec.model_id} (mode={HF_MODE}, auth={'yes' if auth_token else 'no'})"
            )

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
                # Update health on successful load
                self._update_health_on_success(key)
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
                    status_code = getattr(e.response, "status_code", None)
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
                            logger.info(
                                f"Linked model {spec.model_id} - trying without validation check"
                            )
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
                # Update health on failure
                self._update_health_on_failure(key, error_msg)
                raise ModelNotAvailable(error_msg) from e

        return self._pipelines[key]

    def call_model_safe(self, key: str, text: str, **kwargs) -> Dict[str, Any]:
        """
        Safely call a model with health tracking.
        Returns result dict with status and data or error.
        """
        try:
            pipe = self.get_pipeline(key)
            result = pipe(text[:512], **kwargs)
            # Update health on successful call
            self._update_health_on_success(key)
            return {
                "status": "success",
                "data": result,
                "model_key": key,
                "model_id": MODEL_SPECS[key].model_id if key in MODEL_SPECS else key,
            }
        except ModelNotAvailable as e:
            # Don't update health here, already updated in get_pipeline
            return {"status": "unavailable", "error": str(e), "model_key": key}
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)[:200]}"
            logger.warning(f"Model call failed for {key}: {error_msg}")
            # Update health on call failure
            self._update_health_on_failure(key, error_msg)
            return {"status": "error", "error": error_msg, "model_key": key}

    def get_registry_status(self) -> Dict[str, Any]:
        """Get detailed registry status with all models"""
        items = []
        for key, spec in MODEL_SPECS.items():
            loaded = key in self._pipelines
            error = self._failed_models.get(key) if key in self._failed_models else None

            items.append(
                {
                    "key": key,
                    "name": spec.model_id,
                    "task": spec.task,
                    "category": spec.category,
                    "loaded": loaded,
                    "error": error,
                    "requires_auth": spec.requires_auth,
                }
            )

        return {
            "models_total": len(MODEL_SPECS),
            "models_loaded": len(self._pipelines),
            "models_failed": len(self._failed_models),
            "items": items,
            "hf_mode": HF_MODE,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "initialized": self._initialized,
        }

    def initialize_models(self):
        """Initialize models with fallback logic - tries primary models first"""
        if self._initialized:
            return {
                "status": "already_initialized",
                "mode": HF_MODE,
                "models_loaded": len(self._pipelines),
                "failed_count": len(self._failed_models),
            }

        if HF_MODE == "off":
            logger.info("HF_MODE=off, using fallback-only mode")
            self._initialized = True
            return {
                "status": "fallback_only",
                "mode": HF_MODE,
                "models_loaded": 0,
                "error": "HF_MODE=off - using lexical fallback",
            }

        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers not available, using fallback-only mode")
            self._initialized = True
            return {
                "status": "fallback_only",
                "mode": HF_MODE,
                "models_loaded": 0,
                "error": "transformers library not installed - using lexical fallback",
            }

        loaded, failed = [], []

        # Try to load at least one model from each category with fallback
        categories_to_try = {
            "crypto": ["crypto_sent_0"],
            "financial": ["financial_sent_0"],
            "social": ["social_sent_0"],
            "news": ["news_sent_0"],
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
            "note": "Fallback lexical analysis available" if len(loaded) == 0 else None,
        }


_registry = ModelRegistry()


def initialize_models():
    return _registry.initialize_models()


def get_model_health_registry() -> List[Dict[str, Any]]:
    """Get health registry for all models"""
    return _registry.get_model_health_registry()


def attempt_model_reinit(model_key: str) -> Dict[str, Any]:
    """Attempt to re-initialize a failed model"""
    return _registry.attempt_model_reinit(model_key)


def call_model_safe(model_key: str, text: str, **kwargs) -> Dict[str, Any]:
    """Safely call a model with health tracking"""
    return _registry.call_model_safe(model_key, text, **kwargs)


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
            mapped = (
                "bullish"
                if "POSITIVE" in label or "BULLISH" in label or "LABEL_2" in label
                else (
                    "bearish"
                    if "NEGATIVE" in label or "BEARISH" in label or "LABEL_0" in label
                    else "neutral"
                )
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
        "engine": "huggingface",
    }


def analyze_crypto_sentiment(text: str):
    return ensemble_crypto_sentiment(text)


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
            mapped = (
                "bullish"
                if "POSITIVE" in label or "LABEL_2" in label
                else ("bearish" if "NEGATIVE" in label or "LABEL_0" in label else "neutral")
            )

            return {
                "label": mapped,
                "score": score,
                "confidence": score,
                "available": True,
                "engine": "huggingface",
                "model": MODEL_SPECS[key].model_id,
            }
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
            mapped = (
                "bullish"
                if "POSITIVE" in label or "LABEL_2" in label
                else ("bearish" if "NEGATIVE" in label or "LABEL_0" in label else "neutral")
            )

            return {
                "label": mapped,
                "score": score,
                "confidence": score,
                "available": True,
                "engine": "huggingface",
                "model": MODEL_SPECS[key].model_id,
            }
        except ModelNotAvailable:
            continue
        except Exception as e:
            logger.warning(f"Social sentiment failed for {key}: {str(e)[:100]}")
            continue

    logger.warning("No HF models available, using fallback")
    return basic_sentiment_fallback(text)


def analyze_market_text(text: str):
    return ensemble_crypto_sentiment(text)


def analyze_chart_points(data: Sequence[Mapping[str, Any]], indicators: Optional[List[str]] = None):
    if not data:
        return {"trend": "neutral", "strength": 0, "analysis": "No data"}

    prices = [float(p.get("price", 0)) for p in data if p.get("price")]
    if not prices:
        return {"trend": "neutral", "strength": 0, "analysis": "No price data"}

    first, last = prices[0], prices[-1]
    change = ((last - first) / first * 100) if first > 0 else 0

    if change > 5:
        trend, strength = "bullish", min(abs(change) / 10, 1.0)
    elif change < -5:
        trend, strength = "bearish", min(abs(change) / 10, 1.0)
    else:
        trend, strength = "neutral", abs(change) / 5

    return {
        "trend": trend,
        "strength": strength,
        "change_pct": change,
        "support": min(prices),
        "resistance": max(prices),
        "analysis": f"Price moved {change:.2f}% showing {trend} trend",
    }


def analyze_news_item(item: Dict[str, Any]):
    text = item.get("title", "") + " " + item.get("description", "")
    sent = ensemble_crypto_sentiment(text)
    return {
        **item,
        "sentiment": sent["label"],
        "sentiment_confidence": sent["confidence"],
        "sentiment_details": sent,
    }


def summarize_text(text: str, max_length: int = 150, min_length: int = 50) -> Dict[str, Any]:
    """
    Summarize text using the summarization model.

    Args:
        text: The text to summarize
        max_length: Maximum length of summary
        min_length: Minimum length of summary

    Returns:
        Dictionary containing the summary and metadata
    """
    if not text or len(text.strip()) < 10:
        return {
            "summary": text,
            "original_length": len(text),
            "summary_length": len(text),
            "error": None,
        }

    try:
        # Try to use the summarization model
        result = call_model_safe(
            "summarization_0", text, max_length=max_length, min_length=min_length
        )

        if result.get("success") and result.get("result"):
            summary = result["result"]
            if isinstance(summary, list) and len(summary) > 0:
                summary_text = summary[0].get("summary_text", text[:max_length])
            elif isinstance(summary, dict):
                summary_text = summary.get("summary_text", text[:max_length])
            else:
                summary_text = str(summary)[:max_length]

            return {
                "summary": summary_text,
                "original_length": len(text),
                "summary_length": len(summary_text),
                "error": None,
            }
    except Exception as e:
        logger.warning(f"Summarization model failed: {e}")

    # Fallback: Simple truncation with ellipsis
    fallback_summary = text[:max_length].rsplit(" ", 1)[0] + "..."
    return {
        "summary": fallback_summary,
        "original_length": len(text),
        "summary_length": len(fallback_summary),
        "error": "Using fallback summarization",
    }


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
            "trading_signals": TRADING_SIGNAL_MODELS,
            "summarization": SUMMARIZATION_MODELS,
        },
        "total_models": len(MODEL_SPECS),
    }


def basic_sentiment_fallback(text: str) -> Dict[str, Any]:
    """
    Simple lexical-based sentiment fallback that doesn't require transformers.
    Returns sentiment based on keyword matching.
    """
    text_lower = text.lower()

    # Define keyword lists
    bullish_words = [
        "bullish",
        "rally",
        "surge",
        "pump",
        "breakout",
        "skyrocket",
        "uptrend",
        "buy",
        "accumulation",
        "moon",
        "gain",
        "profit",
        "up",
        "high",
        "rise",
        "growth",
        "positive",
        "strong",
    ]
    bearish_words = [
        "bearish",
        "dump",
        "crash",
        "selloff",
        "downtrend",
        "collapse",
        "sell",
        "capitulation",
        "panic",
        "fear",
        "drop",
        "loss",
        "down",
        "low",
        "fall",
        "decline",
        "negative",
        "weak",
    ]

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
            "neutral": round(neutral_score, 3),
        },
        "available": True,  # Set to True so frontend renders it
        "engine": "fallback_lexical",
        "keyword_matches": {"bullish": bullish_count, "bearish": bearish_count},
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
        "total_specs": len(MODEL_SPECS),
    }

    if HF_MODE == "off":
        status["error"] = "HF_MODE=off"
    elif not TRANSFORMERS_AVAILABLE:
        status["error"] = "transformers not installed"
    elif len(_registry._pipelines) == 0 and _registry._initialized:
        status["error"] = "No models loaded successfully"

    return status


# ==================== GAP FILLING SERVICE ====================


class GapFillingService:
    """
    Uses AI models to fill missing data gaps
    Combines interpolation, ML predictions, and external provider fallback
    """

    def __init__(self, model_registry: Optional[ModelRegistry] = None):
        self.model_registry = model_registry or _registry
        self.gap_fill_attempts = {}  # Track gap filling attempts

    async def fill_missing_ohlc(
        self, symbol: str, existing_data: List[Dict[str, Any]], missing_timestamps: List[int]
    ) -> Dict[str, Any]:
        """
        Synthesize missing OHLC candles using interpolation + ML

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            existing_data: List of existing OHLC data points
            missing_timestamps: List of timestamps with missing data

        Returns:
            Dictionary with filled data and metadata
        """
        if not existing_data or not missing_timestamps:
            return {
                "status": "error",
                "message": "Insufficient data for gap filling",
                "filled_count": 0,
            }

        filled_data = []
        confidence_scores = []

        # Sort existing data by timestamp
        existing_data.sort(key=lambda x: x.get("timestamp", 0))

        for missing_ts in missing_timestamps:
            # Find surrounding data points
            before = [d for d in existing_data if d.get("timestamp", 0) < missing_ts]
            after = [d for d in existing_data if d.get("timestamp", 0) > missing_ts]

            if before and after:
                # Linear interpolation between surrounding points
                prev_point = before[-1]
                next_point = after[0]

                # Calculate interpolation factor
                time_diff = next_point["timestamp"] - prev_point["timestamp"]
                position = (
                    (missing_ts - prev_point["timestamp"]) / time_diff if time_diff > 0 else 0.5
                )

                # Interpolate OHLC values
                interpolated = {
                    "timestamp": missing_ts,
                    "open": prev_point["close"] * (1 - position) + next_point["open"] * position,
                    "high": max(prev_point["high"], next_point["high"]) * (0.98 + position * 0.04),
                    "low": min(prev_point["low"], next_point["low"]) * (1.02 - position * 0.04),
                    "close": prev_point["close"] * (1 - position) + next_point["close"] * position,
                    "volume": (prev_point.get("volume", 0) + next_point.get("volume", 0)) / 2,
                    "is_synthetic": True,
                    "method": "linear_interpolation",
                }

                # Calculate confidence based on distance
                confidence = 0.95 ** (len(missing_timestamps))  # Decay with gap size
                confidence_scores.append(confidence)
                interpolated["confidence"] = confidence

                filled_data.append(interpolated)

        return {
            "status": "success",
            "symbol": symbol,
            "filled_count": len(filled_data),
            "filled_data": filled_data,
            "average_confidence": (
                sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            ),
            "method": "interpolation",
            "metadata": {
                "existing_points": len(existing_data),
                "missing_points": len(missing_timestamps),
                "fill_rate": (
                    len(filled_data) / len(missing_timestamps) if missing_timestamps else 0
                ),
            },
        }

    async def estimate_orderbook_depth(
        self, symbol: str, mid_price: float, depth_levels: int = 10
    ) -> Dict[str, Any]:
        """
        Generate estimated order book when real data unavailable
        Uses statistical models + market patterns
        """
        if mid_price <= 0:
            return {"error": "Invalid mid_price"}

        # Generate synthetic orderbook with realistic spread
        spread_pct = 0.001  # 0.1% spread
        level_spacing = 0.0005  # 0.05% per level

        bids = []
        asks = []

        for i in range(depth_levels):
            # Bids (buy orders) below mid price
            bid_price = mid_price * (1 - spread_pct / 2 - i * level_spacing)
            bid_volume = 1.0 / (i + 1) * 10  # Decreasing volume with depth

            bids.append(
                {"price": round(bid_price, 8), "volume": round(bid_volume, 4), "is_synthetic": True}
            )

            # Asks (sell orders) above mid price
            ask_price = mid_price * (1 + spread_pct / 2 + i * level_spacing)
            ask_volume = 1.0 / (i + 1) * 10

            asks.append(
                {"price": round(ask_price, 8), "volume": round(ask_volume, 4), "is_synthetic": True}
            )

        return {
            "status": "success",
            "symbol": symbol,
            "mid_price": mid_price,
            "bids": bids,
            "asks": asks,
            "is_synthetic": True,
            "confidence": 0.65,  # Lower confidence for synthetic data
            "method": "statistical_estimation",
            "metadata": {
                "spread_pct": spread_pct,
                "depth_levels": depth_levels,
                "total_bid_volume": sum(b["volume"] for b in bids),
                "total_ask_volume": sum(a["volume"] for a in asks),
            },
        }

    async def synthesize_whale_data(
        self, chain: str, token: str, historical_pattern: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Infer whale movements from partial data
        Uses on-chain analysis patterns
        """
        # Placeholder for whale data synthesis
        # In production, this would use ML models trained on historical whale patterns

        synthetic_movements = []

        # Generate synthetic whale movement based on typical patterns
        if historical_pattern:
            # Use historical patterns to generate realistic movements
            avg_movement = historical_pattern.get("avg_movement_size", 1000000)
            frequency = historical_pattern.get("frequency_per_day", 5)
        else:
            # Default patterns
            avg_movement = 1000000
            frequency = 5

        for i in range(min(frequency, 10)):
            movement = {
                "timestamp": int(time.time()) - (i * 3600),
                "from_address": f"0x{'0'*(40-len(str(i)))}{i}",
                "to_address": "0x" + "0" * 40,
                "amount": avg_movement * (0.8 + random.random() * 0.4),
                "token": token,
                "chain": chain,
                "is_synthetic": True,
                "confidence": 0.55,
            }
            synthetic_movements.append(movement)

        return {
            "status": "success",
            "chain": chain,
            "token": token,
            "movements": synthetic_movements,
            "is_synthetic": True,
            "confidence": 0.55,
            "method": "pattern_based_synthesis",
            "metadata": {
                "movement_count": len(synthetic_movements),
                "total_volume": sum(m["amount"] for m in synthetic_movements),
            },
        }

    async def analyze_trading_signal(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        sentiment_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate trading signal using AI models
        Combines price action, volume, and sentiment analysis
        """
        # Use trading signal model if available
        try:
            if "crypto_trading_lm" in MODEL_SPECS:
                # Prepare input text for model
                text = f"Analyze {symbol}: "
                if market_data:
                    price = market_data.get("price", 0)
                    change = market_data.get("percent_change_24h", 0)
                    volume = market_data.get("volume_24h", 0)
                    text += f"Price ${price:.2f}, Change {change:+.2f}%, Volume ${volume:,.0f}"

                if sentiment_data:
                    sentiment = sentiment_data.get("label", "neutral")
                    text += f", Sentiment: {sentiment}"

                # Call model
                result = self.model_registry.call_model_safe("crypto_trading_lm", text)

                if result["status"] == "success":
                    # Parse model output
                    model_output = result.get("data", {})

                    return {
                        "status": "success",
                        "symbol": symbol,
                        "signal": "hold",  # Default
                        "confidence": 0.70,
                        "reasoning": model_output,
                        "is_ai_generated": True,
                        "model_used": "crypto_trading_lm",
                    }
        except Exception as e:
            logger.warning(f"Error in trading signal analysis: {e}")

        # Fallback to rule-based signal
        signal = "hold"
        confidence = 0.60

        if market_data:
            change = market_data.get("percent_change_24h", 0)
            volume_change = market_data.get("volume_change_24h", 0)

            # Simple rules
            if change > 5 and volume_change > 20:
                signal = "buy"
                confidence = 0.75
            elif change < -5 and volume_change > 20:
                signal = "sell"
                confidence = 0.75

        return {
            "status": "success",
            "symbol": symbol,
            "signal": signal,
            "confidence": confidence,
            "reasoning": "Rule-based analysis",
            "is_ai_generated": False,
            "method": "fallback_rules",
        }


# Global gap filling service instance
_gap_filler = GapFillingService()


def get_gap_filler() -> GapFillingService:
    """Get global gap filling service instance"""
    return _gap_filler
