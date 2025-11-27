from __future__ import annotations
import os, time, random
from typing import Dict, Any, List, Literal, Optional
import httpx

HF_API_MODELS = "https://huggingface.co/api/models"
HF_API_DATASETS = "https://huggingface.co/api/datasets"
REFRESH_INTERVAL_SEC = int(os.getenv("HF_REGISTRY_REFRESH_SEC", "21600"))
HTTP_TIMEOUT = float(os.getenv("HF_HTTP_TIMEOUT", "8.0"))

# Curated Crypto Datasets
CRYPTO_DATASETS = {
    "price": [
        "paperswithbacktest/Cryptocurrencies-Daily-Price",
        "linxy/CryptoCoin",
        "sebdg/crypto_data",
        "Farmaanaa/bitcoin_price_timeseries",
        "WinkingFace/CryptoLM-Bitcoin-BTC-USDT",
        "WinkingFace/CryptoLM-Ethereum-ETH-USDT",
        "WinkingFace/CryptoLM-Ripple-XRP-USDT",
    ],
    "news_raw": [
        "flowfree/crypto-news-headlines",
        "edaschau/bitcoin_news",
    ],
    "news_labeled": [
        "SahandNZ/cryptonews-articles-with-price-momentum-labels",
        "tahamajs/bitcoin-individual-news-dataset",
        "tahamajs/bitcoin-enhanced-prediction-dataset-with-comprehensive-news",
        "tahamajs/bitcoin-prediction-dataset-with-local-news-summaries",
        "arad1367/Crypto_Semantic_News",
    ],
}

_SEED_MODELS = ["ElKulako/cryptobert", "kk08/CryptoBERT"]
_SEED_DATASETS = []
for cat in CRYPTO_DATASETS.values():
    _SEED_DATASETS.extend(cat)


class HFRegistry:
    def __init__(self):
        self.models: Dict[str, Dict[str, Any]] = {}
        self.datasets: Dict[str, Dict[str, Any]] = {}
        self.last_refresh = 0.0
        self.fail_reason: Optional[str] = None

    async def _hf_json(self, url: str, params: Dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            return r.json()

    async def refresh(self) -> Dict[str, Any]:
        try:
            # Seed models
            for name in _SEED_MODELS:
                self.models.setdefault(
                    name, {"id": name, "source": "seed", "pipeline_tag": "sentiment-analysis"}
                )

            # Seed datasets with category metadata
            for category, dataset_list in CRYPTO_DATASETS.items():
                for name in dataset_list:
                    self.datasets.setdefault(
                        name,
                        {
                            "id": name,
                            "source": "seed",
                            "category": category,
                            "tags": ["crypto", category],
                        },
                    )

            # Fetch from HF Hub
            q_sent = {"pipeline_tag": "sentiment-analysis", "search": "crypto", "limit": 50}
            models = await self._hf_json(HF_API_MODELS, q_sent)
            for m in models or []:
                mid = m.get("modelId") or m.get("id") or m.get("name")
                if not mid:
                    continue
                self.models[mid] = {
                    "id": mid,
                    "pipeline_tag": m.get("pipeline_tag"),
                    "likes": m.get("likes"),
                    "downloads": m.get("downloads"),
                    "tags": m.get("tags") or [],
                    "source": "hub",
                }

            q_crypto = {"search": "crypto", "limit": 100}
            datasets = await self._hf_json(HF_API_DATASETS, q_crypto)
            for d in datasets or []:
                did = d.get("id") or d.get("name")
                if not did:
                    continue
                # Infer category from tags or name
                category = "other"
                tags_str = " ".join(d.get("tags") or []).lower()
                name_lower = did.lower()
                if "price" in tags_str or "ohlc" in tags_str or "price" in name_lower:
                    category = "price"
                elif "news" in tags_str or "news" in name_lower:
                    if "label" in tags_str or "sentiment" in tags_str:
                        category = "news_labeled"
                    else:
                        category = "news_raw"

                self.datasets[did] = {
                    "id": did,
                    "likes": d.get("likes"),
                    "downloads": d.get("downloads"),
                    "tags": d.get("tags") or [],
                    "category": category,
                    "source": "hub",
                }

            self.last_refresh = time.time()
            self.fail_reason = None
            return {"ok": True, "models": len(self.models), "datasets": len(self.datasets)}
        except Exception as e:
            self.fail_reason = str(e)
            return {
                "ok": False,
                "error": self.fail_reason,
                "models": len(self.models),
                "datasets": len(self.datasets),
            }

    def list(
        self, kind: Literal["models", "datasets"] = "models", category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        items = list(self.models.values()) if kind == "models" else list(self.datasets.values())
        if category and kind == "datasets":
            items = [d for d in items if d.get("category") == category]
        return items

    def health(self):
        age = time.time() - (self.last_refresh or 0)
        return {
            "ok": self.last_refresh > 0 and (self.fail_reason is None),
            "last_refresh_epoch": self.last_refresh,
            "age_sec": age,
            "fail_reason": self.fail_reason,
            "counts": {"models": len(self.models), "datasets": len(self.datasets)},
            "interval_sec": REFRESH_INTERVAL_SEC,
        }


REGISTRY = HFRegistry()


async def periodic_refresh(loop_sleep: int = REFRESH_INTERVAL_SEC):
    await REGISTRY.refresh()
    await _sleep(int(loop_sleep * random.uniform(0.5, 0.9)))
    while True:
        await REGISTRY.refresh()
        await _sleep(loop_sleep)


async def _sleep(sec: int):
    import asyncio

    try:
        await asyncio.sleep(sec)
    except:
        pass
