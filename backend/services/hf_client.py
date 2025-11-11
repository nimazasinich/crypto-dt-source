from __future__ import annotations
from typing import List, Dict, Any, Optional
import os
from functools import lru_cache
from datetime import datetime
from collections import deque

ENABLE_SENTIMENT = os.getenv("ENABLE_SENTIMENT", "true").lower() in ("1","true","yes")
SOCIAL_MODEL = os.getenv("SENTIMENT_SOCIAL_MODEL", "ElKulako/cryptobert")
NEWS_MODEL = os.getenv("SENTIMENT_NEWS_MODEL", "kk08/CryptoBERT")


@lru_cache(maxsize=4)
def _pl(model_name: str):
    if not ENABLE_SENTIMENT:
        return None
    from transformers import pipeline
    return pipeline("sentiment-analysis", model=model_name)


def _label_to_score(lbl: str) -> float:
    l = (lbl or "").lower()
    if "bear" in l or "neg" in l or "label_0" in l: return -1.0
    if "bull" in l or "pos" in l or "label_1" in l: return 1.0
    return 0.0


def run_sentiment(texts: List[str], model: str | None = None) -> Dict[str, Any]:
    if not ENABLE_SENTIMENT:
        return {"enabled": False, "vote": 0.0, "samples": []}
    name = model or SOCIAL_MODEL
    pl = _pl(name)
    if not pl:
        return {"enabled": False, "vote": 0.0, "samples": []}
    preds = pl(texts)
    scores = [_label_to_score(p.get("label","")) * float(p.get("score",0)) for p in preds]
    vote = sum(scores) / max(1, len(scores))
    return {"enabled": True, "model": name, "vote": vote, "samples": preds}


class HFClient:
    """
    HuggingFace Client for sentiment analysis and model management
    Wraps the standalone sentiment analysis functions and provides
    usage tracking and result caching
    """

    def __init__(self, max_history: int = 100):
        """
        Initialize the HuggingFace client

        Args:
            max_history: Maximum number of results to keep in history
        """
        self.enabled = ENABLE_SENTIMENT
        self.social_model = SOCIAL_MODEL
        self.news_model = NEWS_MODEL

        # Usage statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.latencies = deque(maxlen=100)  # Store last 100 latencies
        self.model_usage: Dict[str, int] = {}

        # Recent results cache
        self.recent_results = deque(maxlen=max_history)

    def analyze_sentiment(self, texts: List[str], model: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze sentiment of text samples

        Args:
            texts: List of text samples to analyze
            model: Optional model name to use (defaults to SOCIAL_MODEL)

        Returns:
            Dict with sentiment analysis results
        """
        start_time = datetime.now()
        self.total_requests += 1

        model_name = model or self.social_model

        # Track model usage
        self.model_usage[model_name] = self.model_usage.get(model_name, 0) + 1

        try:
            result = run_sentiment(texts, model)

            # Track latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.latencies.append(latency_ms)

            # Track success
            if result.get("enabled", False):
                self.successful_requests += 1
            else:
                self.failed_requests += 1

            # Cache result
            result_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "model": model_name,
                "vote": result.get("vote", 0.0),
                "sample_count": len(texts),
                "latency_ms": latency_ms,
                "success": result.get("enabled", False)
            }
            self.recent_results.append(result_entry)

            return result

        except Exception as e:
            self.failed_requests += 1
            return {
                "enabled": False,
                "vote": 0.0,
                "samples": [],
                "error": str(e)
            }

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics for the HuggingFace client

        Returns:
            Dict with usage statistics
        """
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0

        return {
            "enabled": self.enabled,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (
                self.successful_requests / self.total_requests
                if self.total_requests > 0 else 0
            ),
            "average_latency": avg_latency,
            "model_usage": dict(self.model_usage),
            "configured_models": {
                "social": self.social_model,
                "news": self.news_model
            }
        }

    def get_recent_results(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent sentiment analysis results

        Args:
            limit: Optional limit on number of results to return

        Returns:
            List of recent result entries
        """
        results = list(self.recent_results)
        if limit:
            results = results[-limit:]
        return results

    def clear_history(self):
        """Clear recent results history"""
        self.recent_results.clear()

    def reset_stats(self):
        """Reset usage statistics"""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.latencies.clear()
        self.model_usage.clear()
