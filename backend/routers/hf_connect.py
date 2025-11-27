from __future__ import annotations

from typing import List, Literal

from fastapi import APIRouter, Body, Query

from backend.services.hf_client import run_sentiment
from backend.services.hf_registry import REGISTRY

router = APIRouter(prefix="/api/hf", tags=["huggingface"])


@router.get("/health")
async def hf_health():
    return REGISTRY.health()


@router.post("/refresh")
async def hf_refresh():
    return await REGISTRY.refresh()


@router.get("/registry")
async def hf_registry(kind: Literal["models", "datasets"] = "models"):
    return {"kind": kind, "items": REGISTRY.list(kind)}


@router.get("/search")
async def hf_search(q: str = Query("crypto"), kind: Literal["models", "datasets"] = "models"):
    hay = REGISTRY.list(kind)
    ql = q.lower()
    res = [
        x
        for x in hay
        if ql
        in (x.get("id", "").lower() + " " + " ".join([str(t) for t in x.get("tags", [])]).lower())
    ]
    return {"query": q, "kind": kind, "count": len(res), "items": res[:50]}


@router.post("/run-sentiment")
async def hf_run_sentiment(
    texts: List[str] = Body(..., embed=True), model: str | None = Body(default=None)
):
    return run_sentiment(texts, model=model)
