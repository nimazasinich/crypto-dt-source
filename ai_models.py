#!/usr/bin/env python3
"""Centralized access to Hugging Face models used by the dashboard."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

from config import HUGGINGFACE_MODELS, get_settings

try:  # pragma: no cover - optional dependency
    from transformers import pipeline

    TRANSFORMERS_AVAILABLE = True
except ImportError:  # pragma: no cover - handled by callers
    TRANSFORMERS_AVAILABLE = False


logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass(frozen=True)
class PipelineSpec:
    """Description of a lazily-loaded transformers pipeline."""

    key: str
    task: str
    model_id: str
    requires_auth: bool = False


MODEL_SPECS: Dict[str, PipelineSpec] = {
    "sentiment_twitter": PipelineSpec(
        key="sentiment_twitter",
        task="sentiment-analysis",
        model_id=HUGGINGFACE_MODELS["sentiment_twitter"],
    ),
    "sentiment_financial": PipelineSpec(
        key="sentiment_financial",
        task="sentiment-analysis",
        model_id=HUGGINGFACE_MODELS["sentiment_financial"],
    ),
    "summarization": PipelineSpec(
        key="summarization",
        task="summarization",
        model_id=HUGGINGFACE_MODELS["summarization"],
    ),
    "crypto_sentiment": PipelineSpec(
        key="crypto_sentiment",
        task="fill-mask",
        model_id=HUGGINGFACE_MODELS["crypto_sentiment"],
        requires_auth=True,
    ),
}


class ModelNotAvailable(RuntimeError):
    """Raised when a transformers pipeline cannot be loaded."""


class ModelRegistry:
    """Lazy-loading container for all model pipelines."""

    def __init__(self) -> None:
        self._pipelines: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def get_pipeline(self, key: str):
        if not TRANSFORMERS_AVAILABLE:
            raise ModelNotAvailable("transformers library is not installed")

        spec = MODEL_SPECS[key]
        if key in self._pipelines:
            return self._pipelines[key]

        with self._lock:
            if key in self._pipelines:
                return self._pipelines[key]

            auth_token: Optional[str] = None
            if spec.requires_auth and settings.hf_token:
                auth_token = settings.hf_token

            logger.info("Loading Hugging Face model: %s", spec.model_id)
            try:
                self._pipelines[key] = pipeline(
                    spec.task,
                    model=spec.model_id,
                    tokenizer=spec.model_id,
                    use_auth_token=auth_token,
                )
            except Exception as exc:  # pragma: no cover - network heavy
                logger.exception("Failed to load model %s", spec.model_id)
                raise ModelNotAvailable(str(exc)) from exc

        return self._pipelines[key]

    def status(self) -> Dict[str, Any]:
        return {
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "models_initialized": list(self._pipelines.keys()),
            "hf_auth_configured": bool(settings.hf_token),
        }


_registry = ModelRegistry()


def get_model_info() -> Dict[str, Any]:
    """Return a lightweight description of the registry state."""

    info = _registry.status()
    info["model_names"] = {k: spec.model_id for k, spec in MODEL_SPECS.items()}
    return info


def initialize_models() -> Dict[str, Any]:
    """Pre-load every configured pipeline and report status."""

    loaded: Dict[str, bool] = {}
    for key in MODEL_SPECS:
        try:
            _registry.get_pipeline(key)
            loaded[key] = True
        except ModelNotAvailable as exc:
            loaded[key] = False
            logger.warning("Model %s unavailable: %s", key, exc)

    success = any(loaded.values())
    return {"success": success, "models": loaded}


def _validate_text(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("Text input must be a string")
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Text input cannot be empty")
    return cleaned[:512]


def _format_sentiment(label: str, score: float, model_key: str) -> Dict[str, Any]:
    return {
        "label": label.lower(),
        "score": round(float(score), 4),
        "model": MODEL_SPECS[model_key].model_id,
    }


def analyze_social_sentiment(text: str) -> Dict[str, Any]:
    """Run the Twitter-specific sentiment model."""

    try:
        payload = _validate_text(text)
    except ValueError as exc:
        return {"label": "neutral", "score": 0.0, "error": str(exc)}

    try:
        pipe = _registry.get_pipeline("sentiment_twitter")
    except ModelNotAvailable as exc:
        return {"label": "neutral", "score": 0.0, "error": str(exc)}

    try:
        result = pipe(payload)[0]
        return _format_sentiment(result["label"], result["score"], "sentiment_twitter")
    except Exception as exc:  # pragma: no cover - inference heavy
        logger.exception("Social sentiment analysis failed")
        return {"label": "neutral", "score": 0.0, "error": str(exc)}


def analyze_financial_sentiment(text: str) -> Dict[str, Any]:
    """Run FinBERT style sentiment analysis."""

    try:
        payload = _validate_text(text)
    except ValueError as exc:
        return {"label": "neutral", "score": 0.0, "error": str(exc)}

    try:
        pipe = _registry.get_pipeline("sentiment_financial")
    except ModelNotAvailable as exc:
        return {"label": "neutral", "score": 0.0, "error": str(exc)}

    try:
        result = pipe(payload)[0]
        return _format_sentiment(result["label"], result["score"], "sentiment_financial")
    except Exception as exc:  # pragma: no cover - inference heavy
        logger.exception("Financial sentiment analysis failed")
        return {"label": "neutral", "score": 0.0, "error": str(exc)}


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Combine social and financial sentiment signals."""

    social = analyze_social_sentiment(text)
    financial = analyze_financial_sentiment(text)

    scores = [entry["score"] if entry.get("label", "").startswith("pos") else -entry["score"]
              for entry in (social, financial) if "error" not in entry]

    if not scores:
        return {"label": "neutral", "score": 0.0, "details": {"social": social, "financial": financial}}

    avg_score = sum(scores) / len(scores)
    label = "positive" if avg_score > 0.15 else "negative" if avg_score < -0.15 else "neutral"
    return {
        "label": label,
        "score": round(avg_score, 4),
        "details": {"social": social, "financial": financial},
    }


def analyze_crypto_sentiment(text: str, mask_token: str = "[MASK]") -> Dict[str, Any]:
    """Use CryptoBERT to infer crypto-native sentiment."""

    try:
        payload = _validate_text(text)
    except ValueError as exc:
        return {"label": "neutral", "score": 0.0, "error": str(exc)}

    try:
        pipe = _registry.get_pipeline("crypto_sentiment")
    except ModelNotAvailable as exc:
        logger.warning("CryptoBERT unavailable: %s", exc)
        return analyze_sentiment(text)

    masked = f"{payload} Overall sentiment is {mask_token}."
    try:
        predictions = pipe(masked, top_k=5)
    except Exception as exc:  # pragma: no cover
        logger.exception("CryptoBERT inference failed")
        return analyze_sentiment(text)

    keywords = {
        "positive": ["bullish", "positive", "optimistic", "strong", "good"],
        "negative": ["bearish", "negative", "weak", "bad", "sell"],
        "neutral": ["neutral", "flat", "balanced", "stable"],
    }
    sentiment_scores = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    for prediction in predictions:
        token = prediction.get("token_str", "").strip().lower()
        score = float(prediction.get("score", 0.0))
        for label, values in keywords.items():
            if any(value in token for value in values):
                sentiment_scores[label] += score
                break

    label = max(sentiment_scores, key=sentiment_scores.get)
    confidence = sentiment_scores[label]
    if confidence == 0.0:
        return analyze_sentiment(text)

    return {
        "label": label,
        "score": round(confidence, 4),
        "predictions": [
            {"token": pred.get("token_str"), "score": round(float(pred.get("score", 0.0)), 4)}
            for pred in predictions[:3]
        ],
        "model": MODEL_SPECS["crypto_sentiment"].model_id,
    }


def summarize_text(text: str, max_length: int = 200, min_length: int = 40) -> Dict[str, Any]:
    """Summarize long-form content using the configured BART model."""

    if not isinstance(text, str) or not text.strip():
        return {"summary": "", "model": MODEL_SPECS["summarization"].model_id}

    payload = text.strip()
    if len(payload) < min_length:
        return {"summary": payload, "model": MODEL_SPECS["summarization"].model_id}

    try:
        pipe = _registry.get_pipeline("summarization")
    except ModelNotAvailable as exc:
        return {"summary": payload[:max_length], "model": "unavailable", "error": str(exc)}

    try:
        result = pipe(payload, max_length=max_length, min_length=min_length, do_sample=False)
        summary = result[0]["summary_text"].strip()
    except Exception as exc:  # pragma: no cover - inference heavy
        logger.exception("Summarization failed")
        summary = payload[:max_length]
        return {"summary": summary, "model": MODEL_SPECS["summarization"].model_id, "error": str(exc)}

    return {"summary": summary, "model": MODEL_SPECS["summarization"].model_id}


def analyze_news_item(item: Mapping[str, Any]) -> Dict[str, Any]:
    """Summarize a news item and attach sentiment metadata."""

    text_parts = [
        item.get("title", ""),
        item.get("body") or item.get("content") or item.get("description") or "",
    ]
    combined = ". ".join(part for part in text_parts if part).strip()
    summary = summarize_text(combined or item.get("title", ""))
    sentiment = analyze_crypto_sentiment(combined or item.get("title", ""))

    return {
        "title": item.get("title"),
        "summary": summary.get("summary"),
        "sentiment": sentiment,
        "source": item.get("source"),
        "published_at": item.get("published_at") or item.get("date"),
    }


def analyze_market_text(query: str) -> Dict[str, Any]:
    """High-level helper used by the /api/query endpoint."""

    summary = summarize_text(query, max_length=120)
    crypto = analyze_crypto_sentiment(query)
    fin = analyze_financial_sentiment(query)
    social = analyze_social_sentiment(query)

    classification = "sentiment"
    lowered = query.lower()
    if any(word in lowered for word in ("price", "buy", "sell", "support", "resistance")):
        classification = "market"
    elif any(word in lowered for word in ("news", "headline", "update")):
        classification = "news"

    return {
        "summary": summary,
        "signals": {
            "crypto": crypto,
            "financial": fin,
            "social": social,
        },
        "classification": classification,
    }


def registry_status() -> Dict[str, Any]:
    """Expose registry information for health checks."""

    info = get_model_info()
    info["loaded_models"] = _registry.status()["models_initialized"]
    return info


__all__ = [
    "initialize_models",
    "get_model_info",
    "registry_status",
    "analyze_sentiment",
    "analyze_crypto_sentiment",
    "analyze_social_sentiment",
    "analyze_financial_sentiment",
    "summarize_text",
    "analyze_news_item",
    "analyze_market_text",
]
