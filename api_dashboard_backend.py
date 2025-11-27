#!/usr/bin/env python3
"""FastAPI backend for the professional crypto dashboard."""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ai_models import (
    analyze_chart_points,
    analyze_crypto_sentiment,
    analyze_financial_sentiment,
    analyze_market_text,
    analyze_news_item,
    analyze_social_sentiment,
    registry_status,
    summarize_text,
)
from collectors.aggregator import (
    CollectorError,
    MarketDataCollector,
    NewsCollector,
    ProviderStatusCollector,
)
from config import COIN_SYMBOL_MAPPING, get_settings

settings = get_settings()
logger = logging.getLogger("crypto.api")
logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))

app = FastAPI(
    title="Crypto Intelligence Dashboard API",
    version="2.0.0",
    description="Professional API for cryptocurrency intelligence",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

market_collector = MarketDataCollector()
news_collector = NewsCollector()
provider_collector = ProviderStatusCollector()


class CoinSummary(BaseModel):
    name: Optional[str]
    symbol: str
    price: Optional[float]
    change_24h: Optional[float]
    market_cap: Optional[float]
    volume_24h: Optional[float]
    rank: Optional[int]
    last_updated: Optional[datetime]


class CoinDetail(CoinSummary):
    id: Optional[str]
    description: Optional[str]
    homepage: Optional[str]
    circulating_supply: Optional[float]
    total_supply: Optional[float]
    ath: Optional[float]
    atl: Optional[float]


class MarketStats(BaseModel):
    total_market_cap: Optional[float]
    total_volume_24h: Optional[float]
    market_cap_change_percentage_24h: Optional[float]
    btc_dominance: Optional[float]
    eth_dominance: Optional[float]
    active_cryptocurrencies: Optional[int]
    markets: Optional[int]
    updated_at: Optional[int]


class NewsItem(BaseModel):
    id: Optional[str]
    title: str
    body: Optional[str]
    url: Optional[str]
    source: Optional[str]
    categories: Optional[str]
    published_at: Optional[datetime]
    analysis: Optional[Dict[str, Any]] = None


class ProviderInfo(BaseModel):
    provider_id: str
    name: str
    category: Optional[str]
    status: str
    status_code: Optional[int]
    latency_ms: Optional[float]
    error: Optional[str] = None


class ChartDataPoint(BaseModel):
    timestamp: datetime
    price: float


class ChartAnalysisRequest(BaseModel):
    symbol: str = Field(..., min_length=2, max_length=10)
    timeframe: str = Field("7d", pattern=r"^[0-9]+[hdw]$")
    indicators: Optional[List[str]] = None


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=5)
    mode: str = Field("auto", pattern=r"^(auto|crypto|financial|social)$")


class NewsSummaryRequest(BaseModel):
    title: str = Field(..., min_length=5)
    body: Optional[str] = None
    source: Optional[str] = None


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3)
    symbol: Optional[str] = None
    task: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    success: bool
    type: str
    message: str
    data: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, Any]


def _handle_collector_error(exc: CollectorError) -> None:
    raise HTTPException(status_code=503, detail={"error": str(exc), "provider": exc.provider})


@app.get("/")
async def serve_dashboard() -> FileResponse:
    return FileResponse("unified_dashboard.html")


@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    async def _safe_call(coro):
        try:
            await coro
            return {"status": "ok"}
        except Exception as exc:  # pragma: no cover - network heavy
            return {"status": "error", "detail": str(exc)}

    market_task = asyncio.create_task(_safe_call(market_collector.get_top_coins(limit=1)))
    news_task = asyncio.create_task(_safe_call(news_collector.get_latest_news(limit=1)))
    providers_task = asyncio.create_task(_safe_call(provider_collector.get_providers_status()))

    market_status, news_status, providers_status = await asyncio.gather(
        market_task, news_task, providers_task
    )

    ai_status = registry_status()

    return HealthResponse(
        status="ok" if market_status.get("status") == "ok" else "degraded",
        version=app.version,
        timestamp=datetime.utcnow(),
        services={
            "market_data": market_status,
            "news": news_status,
            "providers": providers_status,
            "ai_models": ai_status,
        },
    )


@app.get("/api/coins/top", response_model=Dict[str, Any])
async def get_top_coins(limit: int = 10) -> Dict[str, Any]:
    try:
        coins = await market_collector.get_top_coins(limit=limit)
        return {"success": True, "coins": coins, "count": len(coins)}
    except CollectorError as exc:
        _handle_collector_error(exc)


@app.get("/api/coins/{symbol}", response_model=Dict[str, Any])
async def get_coin_details(symbol: str) -> Dict[str, Any]:
    try:
        coin = await market_collector.get_coin_details(symbol)
        return {"success": True, "coin": coin}
    except CollectorError as exc:
        _handle_collector_error(exc)


@app.get("/api/market/stats", response_model=Dict[str, Any])
async def get_market_statistics() -> Dict[str, Any]:
    try:
        stats = await market_collector.get_market_stats()
        return {"success": True, "stats": stats}
    except CollectorError as exc:
        _handle_collector_error(exc)


@app.get("/api/news/latest", response_model=Dict[str, Any])
async def get_latest_news(limit: int = 10, enrich: bool = False) -> Dict[str, Any]:
    try:
        news = await news_collector.get_latest_news(limit=limit)
        if enrich:
            enriched: List[Dict[str, Any]] = []
            for item in news:
                analysis = analyze_news_item(item)
                enriched.append({**item, "analysis": analysis})
            news = enriched
        return {"success": True, "news": news, "count": len(news)}
    except CollectorError as exc:
        _handle_collector_error(exc)


@app.post("/api/news/summarize", response_model=Dict[str, Any])
async def summarize_news(request: NewsSummaryRequest) -> Dict[str, Any]:
    analysis = analyze_news_item(request.dict())
    return {"success": True, "analysis": analysis}


@app.get("/api/providers", response_model=Dict[str, Any])
async def get_providers() -> Dict[str, Any]:
    providers = await provider_collector.get_providers_status()
    return {"success": True, "providers": providers, "total": len(providers)}


@app.get("/api/charts/price/{symbol}", response_model=Dict[str, Any])
async def get_price_history(symbol: str, timeframe: str = "7d") -> Dict[str, Any]:
    try:
        history = await market_collector.get_price_history(symbol, timeframe)
        return {"success": True, "symbol": symbol.upper(), "timeframe": timeframe, "data": history}
    except CollectorError as exc:
        _handle_collector_error(exc)


@app.post("/api/charts/analyze", response_model=Dict[str, Any])
async def analyze_chart(request: ChartAnalysisRequest) -> Dict[str, Any]:
    try:
        history = await market_collector.get_price_history(request.symbol, request.timeframe)
    except CollectorError as exc:
        _handle_collector_error(exc)

    insights = analyze_chart_points(request.symbol, request.timeframe, history)
    if request.indicators:
        insights["indicators"] = request.indicators

    return {
        "success": True,
        "symbol": request.symbol.upper(),
        "timeframe": request.timeframe,
        "insights": insights,
    }


@app.post("/api/sentiment/analyze", response_model=Dict[str, Any])
async def run_sentiment_analysis(request: SentimentRequest) -> Dict[str, Any]:
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required for sentiment analysis")

    mode = request.mode or "auto"
    if mode == "crypto":
        payload = analyze_crypto_sentiment(text)
    elif mode == "financial":
        payload = analyze_financial_sentiment(text)
    elif mode == "social":
        payload = analyze_social_sentiment(text)
    else:
        payload = analyze_market_text(text)

    response: Dict[str, Any] = {"success": True, "mode": mode, "result": payload}
    if mode == "auto" and isinstance(payload, dict) and payload.get("signals"):
        response["signals"] = payload["signals"]
    return response


def _detect_task(query: str, explicit: Optional[str] = None) -> str:
    if explicit:
        return explicit
    lowered = query.lower()
    if "price" in lowered:
        return "price"
    if "sentiment" in lowered:
        return "sentiment"
    if "summar" in lowered:
        return "summary"
    if any(word in lowered for word in ("should i", "invest", "decision")):
        return "decision"
    return "general"


def _extract_symbol(query: str) -> Optional[str]:
    lowered = query.lower()
    for coin_id, symbol in COIN_SYMBOL_MAPPING.items():
        if coin_id in lowered or symbol.lower() in lowered:
            return symbol

    known_symbols = {symbol.lower() for symbol in COIN_SYMBOL_MAPPING.values()}
    for token in re.findall(r"\b([a-z]{2,5})\b", lowered):
        if token in known_symbols:
            return token.upper()
    return None


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    task = _detect_task(request.query, request.task)
    symbol = request.symbol or _extract_symbol(request.query)

    if task == "price":
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol required for price queries")
        coin = await market_collector.get_coin_details(symbol)
        message = f"{coin['name']} ({coin['symbol']}) latest market data"
        return QueryResponse(success=True, type="price", message=message, data=coin)

    if task == "sentiment":
        sentiment = {
            "crypto": analyze_crypto_sentiment(request.query),
            "financial": analyze_financial_sentiment(request.query),
            "social": analyze_social_sentiment(request.query),
        }
        return QueryResponse(
            success=True, type="sentiment", message="Sentiment analysis", data=sentiment
        )

    if task == "summary":
        summary = summarize_text(request.query)
        return QueryResponse(success=True, type="summary", message="Summarized text", data=summary)

    if task == "decision":
        market_task = asyncio.create_task(market_collector.get_market_stats())
        news_task = asyncio.create_task(news_collector.get_latest_news(limit=3))
        coins_task = asyncio.create_task(market_collector.get_top_coins(limit=5))
        stats, latest_news, coins = await asyncio.gather(market_task, news_task, coins_task)
        sentiment = analyze_market_text(request.query)
        data = {
            "market_stats": stats,
            "top_coins": coins,
            "news": latest_news,
            "analysis": sentiment,
        }
        return QueryResponse(
            success=True, type="decision", message="Composite decision support", data=data
        )

    sentiment = analyze_market_text(request.query)
    return QueryResponse(success=True, type="general", message="General analysis", data=sentiment)


class WebSocketManager:
    def __init__(self) -> None:
        self.connections: Dict[WebSocket, asyncio.Task] = {}
        self.interval = 10

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        sender = asyncio.create_task(self._push_updates(websocket))
        self.connections[websocket] = sender
        await websocket.send_json({"type": "connected", "timestamp": datetime.utcnow().isoformat()})

    async def disconnect(self, websocket: WebSocket) -> None:
        task = self.connections.pop(websocket, None)
        if task:
            task.cancel()
        try:
            await websocket.close()
        except Exception:  # pragma: no cover - connection already closed
            pass

    async def _push_updates(self, websocket: WebSocket) -> None:
        while True:
            try:
                coins = await market_collector.get_top_coins(limit=5)
                stats = await market_collector.get_market_stats()
                news = await news_collector.get_latest_news(limit=3)
                sentiment = analyze_crypto_sentiment(
                    " ".join(item.get("title", "") for item in news)
                )
                payload = {
                    "market_data": coins,
                    "stats": stats,
                    "news": news,
                    "sentiment": sentiment,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                await websocket.send_json({"type": "update", "payload": payload})
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:  # pragma: no cover - task cancellation
                break
            except Exception as exc:  # pragma: no cover - network heavy
                logger.warning("WebSocket send failed: %s", exc)
                break


manager = WebSocketManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    finally:
        await manager.disconnect(websocket)


@app.on_event("startup")
async def startup_event() -> None:  # pragma: no cover - logging only
    logger.info("Starting Crypto Intelligence Dashboard API version %s", app.version)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
