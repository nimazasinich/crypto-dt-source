import os

import pytest

from ai_models import (
    analyze_crypto_sentiment,
    analyze_financial_sentiment,
    analyze_market_text,
    analyze_social_sentiment,
    registry_status,
)
from config import get_settings

settings = get_settings()


pytestmark = pytest.mark.skipif(
    not os.getenv("HF_TOKEN") and not os.getenv("HF_TOKEN_ENCODED"),
    reason="HF token not configured",
)


@pytest.mark.skipif(
    not registry_status()["transformers_available"], reason="transformers not available"
)
def test_crypto_sentiment_structure() -> None:
    result = analyze_crypto_sentiment("Bitcoin continues its bullish momentum")
    assert "label" in result
    assert "score" in result


@pytest.mark.skipif(
    not registry_status()["transformers_available"], reason="transformers not available"
)
def test_multi_model_sentiments() -> None:
    financial = analyze_financial_sentiment("Equities rallied on strong earnings")
    social = analyze_social_sentiment("The community on twitter is excited about ETH")
    assert "label" in financial
    assert "label" in social


@pytest.mark.skipif(
    not registry_status()["transformers_available"], reason="transformers not available"
)
def test_market_text_router() -> None:
    response = analyze_market_text("Summarize Bitcoin market sentiment today")
    assert "summary" in response
    assert "signals" in response
    assert "crypto" in response["signals"]
