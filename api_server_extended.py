#!/usr/bin/env python3
"""
API Server Extended - HuggingFace Spaces Deployment Ready
Real data providers only, no mocks, strict validation
"""

import os
import asyncio
import sqlite3
import httpx
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Environment variables
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
PORT = int(os.getenv("PORT", "7860"))

# Database path
DB_PATH = Path("/app/data/database/crypto_monitor.db")
LOG_DIR = Path("/app/logs")

# Ensure directories exist
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


# ===== Database Setup =====
def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            name TEXT,
            price_usd REAL NOT NULL,
            volume_24h REAL,
            market_cap REAL,
            percent_change_24h REAL,
            rank INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_symbol ON prices(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_timestamp ON prices(timestamp)")

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


def save_price_to_db(price_data: Dict[str, Any]):
    """Save price data to SQLite"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO prices (symbol, name, price_usd, volume_24h, market_cap, percent_change_24h, rank)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            price_data.get("symbol"),
            price_data.get("name"),
            price_data.get("price_usd", 0.0),
            price_data.get("volume_24h"),
            price_data.get("market_cap"),
            price_data.get("percent_change_24h"),
            price_data.get("rank")
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving price to database: {e}")


def get_price_history_from_db(symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get price history from SQLite"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM prices
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (symbol, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching price history: {e}")
        return []


# ===== Real Data Providers =====
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}


async def fetch_coingecko_simple_price() -> Dict[str, Any]:
    """Fetch real price data from CoinGecko API"""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,binancecoin",
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true"
    }

    async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=503, detail=f"CoinGecko API error: HTTP {response.status_code}")
        return response.json()


async def fetch_fear_greed_index() -> Dict[str, Any]:
    """Fetch real Fear & Greed Index from Alternative.me"""
    url = "https://api.alternative.me/fng/"
    params = {"limit": "1", "format": "json"}

    async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=503, detail=f"Alternative.me API error: HTTP {response.status_code}")
        return response.json()


async def fetch_coingecko_trending() -> Dict[str, Any]:
    """Fetch real trending coins from CoinGecko"""
    url = "https://api.coingecko.com/api/v3/search/trending"

    async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=503, detail=f"CoinGecko trending API error: HTTP {response.status_code}")
        return response.json()


# ===== Lifespan Management =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("Starting Crypto Monitor API...")
    init_database()
    print(f"Server ready on port {PORT}")
    yield
    print("Shutting down...")


# ===== FastAPI Application =====
app = FastAPI(
    title="Crypto Monitor API",
    description="Real-time cryptocurrency data API for HuggingFace Spaces",
    version="4.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Health Endpoint =====
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": str(DB_PATH),
        "use_mock_data": USE_MOCK_DATA
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Crypto Monitor API",
        "version": "4.0.0",
        "endpoints": ["/health", "/api/market", "/api/sentiment", "/api/trending", "/api/market/history", "/api/defi", "/api/hf/run-sentiment"]
    }


# ===== Market Data Endpoint =====
@app.get("/api/market")
async def get_market_data():
    """
    Market data from CoinGecko - REAL DATA ONLY
    Returns BTC, ETH, BNB prices with market cap and volume
    """
    try:
        data = await fetch_coingecko_simple_price()

        cryptocurrencies = []
        coin_mapping = {
            "bitcoin": {"name": "Bitcoin", "symbol": "BTC", "rank": 1, "image": "https://assets.coingecko.com/coins/images/1/small/bitcoin.png"},
            "ethereum": {"name": "Ethereum", "symbol": "ETH", "rank": 2, "image": "https://assets.coingecko.com/coins/images/279/small/ethereum.png"},
            "binancecoin": {"name": "BNB", "symbol": "BNB", "rank": 3, "image": "https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png"}
        }

        for coin_id, coin_info in coin_mapping.items():
            if coin_id in data:
                coin_data = data[coin_id]
                crypto_entry = {
                    "rank": coin_info["rank"],
                    "name": coin_info["name"],
                    "symbol": coin_info["symbol"],
                    "price": coin_data.get("usd", 0),
                    "change_24h": coin_data.get("usd_24h_change", 0),
                    "market_cap": coin_data.get("usd_market_cap", 0),
                    "volume_24h": coin_data.get("usd_24h_vol", 0),
                    "image": coin_info["image"]
                }
                cryptocurrencies.append(crypto_entry)

                # Save to database
                save_price_to_db({
                    "symbol": coin_info["symbol"],
                    "name": coin_info["name"],
                    "price_usd": crypto_entry["price"],
                    "volume_24h": crypto_entry["volume_24h"],
                    "market_cap": crypto_entry["market_cap"],
                    "percent_change_24h": crypto_entry["change_24h"],
                    "rank": coin_info["rank"]
                })

        # Calculate dominance
        total_market_cap = sum(c["market_cap"] for c in cryptocurrencies)
        btc_dominance = 0
        eth_dominance = 0
        if total_market_cap > 0:
            btc_data = next((c for c in cryptocurrencies if c["symbol"] == "BTC"), None)
            eth_data = next((c for c in cryptocurrencies if c["symbol"] == "ETH"), None)
            if btc_data:
                btc_dominance = (btc_data["market_cap"] / total_market_cap) * 100
            if eth_data:
                eth_dominance = (eth_data["market_cap"] / total_market_cap) * 100

        return {
            "cryptocurrencies": cryptocurrencies,
            "global": {
                "btc_dominance": round(btc_dominance, 2),
                "eth_dominance": round(eth_dominance, 2)
            },
            "timestamp": datetime.now().isoformat(),
            "provider": "CoinGecko"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail={"error": "Market data service unavailable", "message": str(e)})


# ===== Market History Endpoint =====
@app.get("/api/market/history")
async def get_market_history(symbol: str = "BTC", limit: int = 10):
    """Get price history from SQLite database"""
    history = get_price_history_from_db(symbol, limit)

    if not history:
        return {
            "symbol": symbol,
            "history": [],
            "message": f"No historical data found for {symbol}"
        }

    return {
        "symbol": symbol,
        "history": history,
        "count": len(history)
    }


# ===== Sentiment Endpoint =====
@app.get("/api/sentiment")
async def get_sentiment():
    """
    Market sentiment from Alternative.me Fear & Greed Index - REAL DATA ONLY
    NO mock fallback - returns 503 on failure
    """
    try:
        data = await fetch_fear_greed_index()

        if "data" not in data or not data["data"]:
            raise HTTPException(status_code=503, detail="Invalid response from Alternative.me")

        index_data = data["data"][0]
        index_value = int(index_data.get("value", 50))
        index_classification = index_data.get("value_classification", "neutral")
        timestamp = index_data.get("timestamp")

        return {
            "fear_greed_index": {
                "value": index_value,
                "classification": index_classification
            },
            "timestamp": datetime.now().isoformat(),
            "data_timestamp": timestamp,
            "provider": "Alternative.me"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail={"error": "Sentiment data service unavailable", "message": str(e)})


# ===== Trending Endpoint =====
@app.get("/api/trending")
async def get_trending():
    """
    Trending cryptocurrencies from CoinGecko - REAL DATA ONLY
    Strict validation
    """
    try:
        data = await fetch_coingecko_trending()

        if "coins" not in data:
            raise HTTPException(status_code=503, detail="Invalid response from CoinGecko trending API")

        trending_list = []
        for item in data["coins"][:10]:
            coin = item.get("item", {})
            if not coin.get("name") or not coin.get("symbol"):
                continue
            trending_list.append({
                "name": coin.get("name", ""),
                "symbol": coin.get("symbol", ""),
                "thumb": coin.get("thumb", ""),
                "market_cap_rank": coin.get("market_cap_rank"),
                "price_btc": coin.get("price_btc")
            })

        if not trending_list:
            raise HTTPException(status_code=503, detail="No valid trending coins found")

        return {
            "trending": trending_list,
            "timestamp": datetime.now().isoformat(),
            "provider": "CoinGecko"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail={"error": "Trending data service unavailable", "message": str(e)})


# ===== DeFi Endpoint - NOT IMPLEMENTED =====
@app.get("/api/defi")
async def get_defi():
    """DeFi endpoint - Not implemented"""
    raise HTTPException(status_code=503, detail="DeFi endpoint not implemented")


# ===== HuggingFace ML Sentiment - NOT IMPLEMENTED =====
@app.post("/api/hf/run-sentiment")
async def run_sentiment(data: Dict[str, Any]):
    """ML sentiment analysis - Not implemented"""
    raise HTTPException(status_code=501, detail="ML sentiment not implemented")


# ===== Main Entry Point =====
if __name__ == "__main__":
    import uvicorn
    print(f"Starting server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
