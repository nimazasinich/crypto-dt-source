from __future__ import annotations
from typing import List, Dict, Any
import os
from functools import lru_cache

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
    """HuggingFace client for AI/ML operations"""

    def __init__(self):
        self.enabled = ENABLE_SENTIMENT
        self.social_model = SOCIAL_MODEL
        self.news_model = NEWS_MODEL

    def analyze_sentiment(self, texts: List[str], model: str | None = None) -> Dict[str, Any]:
        """Analyze sentiment of texts"""
        return run_sentiment(texts, model)

    def get_status(self) -> Dict[str, Any]:
        """Get HuggingFace client status"""
        return {
            "enabled": self.enabled,
            "social_model": self.social_model,
            "news_model": self.news_model
        }
