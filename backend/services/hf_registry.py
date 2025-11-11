from __future__ import annotations
import os
import time
import random
from typing import Dict, Any, List, Literal, Optional
import httpx

HF_API_MODELS = "https://huggingface.co/api/models"
HF_API_DATASETS = "https://huggingface.co/api/datasets"

REFRESH_INTERVAL_SEC = int(os.getenv("HF_REGISTRY_REFRESH_SEC", "21600"))  # 6h
HTTP_TIMEOUT = float(os.getenv("HF_HTTP_TIMEOUT", "8.0"))

_SEED_MODELS = [
    "ElKulako/cryptobert",
    "kk08/CryptoBERT",
]
_SEED_DATASETS = [
    "linxy/CryptoCoin",
    "WinkingFace/CryptoLM-Bitcoin-BTC-USDT",
    "WinkingFace/CryptoLM-Ethereum-ETH-USDT",
    "WinkingFace/CryptoLM-Solana-SOL-USDT",
    "WinkingFace/CryptoLM-Ripple-XRP-USDT",
]


class HFRegistry:
    def __init__(self) -> None:
        self.models: Dict[str, Dict[str, Any]] = {}
        self.datasets: Dict[str, Dict[str, Any]] = {}
        self.last_refresh: float = 0.0
        self.fail_reason: Optional[str] = None

    async def _hf_json(self, url: str, params: Dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            return r.json()

    async def refresh(self) -> Dict[str, Any]:
        try:
            for name in _SEED_MODELS:
                self.models.setdefault(name, {"id": name, "source": "seed", "pipeline_tag": "sentiment-analysis"})
            for name in _SEED_DATASETS:
                self.datasets.setdefault(name, {"id": name, "source": "seed"})

            q_crypto = {"search": "crypto", "limit": 50}
            q_sent = {"pipeline_tag": "sentiment-analysis", "search": "crypto", "limit": 50}

            models = await self._hf_json(HF_API_MODELS, q_sent)
            for m in models or []:
                mid = m.get("modelId") or m.get("id") or m.get("name")
                if not mid: continue
                self.models[mid] = {
                    "id": mid,
                    "pipeline_tag": m.get("pipeline_tag"),
                    "likes": m.get("likes"),
                    "downloads": m.get("downloads"),
                    "tags": m.get("tags") or [],
                    "source": "hub",
                }

            datasets = await self._hf_json(HF_API_DATASETS, q_crypto)
            for d in datasets or []:
                did = d.get("id") or d.get("name")
                if not did: continue
                self.datasets[did] = {
                    "id": did,
                    "likes": d.get("likes"),
                    "downloads": d.get("downloads"),
                    "tags": d.get("tags") or [],
                    "source": "hub",
                }

            self.last_refresh = time.time()
            self.fail_reason = None
            return {"ok": True, "models": len(self.models), "datasets": len(self.datasets)}
        except Exception as e:
            self.fail_reason = str(e)
            return {"ok": False, "error": self.fail_reason, "models": len(self.models), "datasets": len(self.datasets)}

    def list(self, kind: Literal["models","datasets"]="models") -> List[Dict[str, Any]]:
        return list(self.models.values()) if kind == "models" else list(self.datasets.values())

    def health(self) -> Dict[str, Any]:
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


async def periodic_refresh(loop_sleep: int = REFRESH_INTERVAL_SEC) -> None:
    await REGISTRY.refresh()
    await _sleep(int(loop_sleep * random.uniform(0.5, 0.9)))
    while True:
        await REGISTRY.refresh()
        await _sleep(loop_sleep)


async def _sleep(sec: int) -> None:
    import asyncio
    try:
        await asyncio.sleep(sec)
    except Exception:
        pass
