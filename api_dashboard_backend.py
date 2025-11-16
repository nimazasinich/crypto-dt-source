#!/usr/bin/env python3
"""
Professional Crypto Dashboard Backend API
Supports user queries, real-time updates, and comprehensive cryptocurrency data
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Crypto Intelligence Dashboard API",
    description="Professional API for cryptocurrency market analysis and intelligence",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


# ==================== Helper Functions ====================

def load_providers_config() -> Dict[str, Any]:
    """Load providers configuration"""
    try:
        config_path = Path(__file__).parent / "providers_config_extended.json"
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"providers": {}}

def parse_query(query: str) -> Dict[str, Any]:
    """Parse natural language query into structured format"""
    query_lower = query.lower().strip()
    
    # Query patterns
    patterns = {
        'price': [r'price of (\w+)', r'(\w+) price', r'how much is (\w+)'],
        'top_coins': [r'top (\d+)', r'best (\d+)', r'top coins'],
        'market_cap': [r'market cap of (\w+)', r'(\w+) market cap'],
        'trend': [r'trend of (\w+)', r'(\w+) trend'],
        'sentiment': [r'sentiment', r'market feeling', r'bullish', r'bearish'],
        'defi': [r'defi', r'tvl', r'total value locked'],
        'nft': [r'nft', r'non fungible'],
        'gas': [r'gas price', r'transaction fee'],
        'news': [r'news', r'latest updates'],
    }
    
    # Check each pattern
    for query_type, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, query_lower)
            if match:
                return {
                    'type': query_type,
                    'params': match.groups() if match.groups() else [],
                    'original_query': query
                }
    
    # Default fallback
    return {
        'type': 'general',
        'params': [],
        'original_query': query
    }

def generate_mock_coin_data(count: int = 10) -> List[Dict[str, Any]]:
    """Generate mock cryptocurrency data"""
    coins = [
        {'name': 'Bitcoin', 'symbol': 'BTC', 'price': 43250.50, 'change_24h': 2.34, 'market_cap': 845e9, 'volume_24h': 25e9},
        {'name': 'Ethereum', 'symbol': 'ETH', 'price': 2280.25, 'change_24h': 1.82, 'market_cap': 274e9, 'volume_24h': 12e9},
        {'name': 'BNB', 'symbol': 'BNB', 'price': 315.80, 'change_24h': -0.52, 'market_cap': 48e9, 'volume_24h': 1.2e9},
        {'name': 'Solana', 'symbol': 'SOL', 'price': 98.45, 'change_24h': 5.23, 'market_cap': 42e9, 'volume_24h': 2.1e9},
        {'name': 'Cardano', 'symbol': 'ADA', 'price': 0.52, 'change_24h': -1.15, 'market_cap': 18e9, 'volume_24h': 450e6},
        {'name': 'XRP', 'symbol': 'XRP', 'price': 0.58, 'change_24h': 3.21, 'market_cap': 31e9, 'volume_24h': 1.5e9},
        {'name': 'Polkadot', 'symbol': 'DOT', 'price': 7.25, 'change_24h': -2.10, 'market_cap': 9.5e9, 'volume_24h': 320e6},
        {'name': 'Dogecoin', 'symbol': 'DOGE', 'price': 0.082, 'change_24h': 4.56, 'market_cap': 11.8e9, 'volume_24h': 680e6},
        {'name': 'Polygon', 'symbol': 'MATIC', 'price': 0.85, 'change_24h': 2.87, 'market_cap': 8.2e9, 'volume_24h': 420e6},
        {'name': 'Avalanche', 'symbol': 'AVAX', 'price': 36.20, 'change_24h': -1.45, 'market_cap': 13.5e9, 'volume_24h': 580e6},
    ]
    return coins[:count]

def generate_mock_news() -> List[Dict[str, Any]]:
    """Generate mock news data"""
    return [
        {
            'title': 'Bitcoin ETF applications surge as institutional interest grows',
            'source': 'CoinDesk',
            'time': '2 hours ago',
            'url': 'https://www.coindesk.com',
            'sentiment': 'positive'
        },
        {
            'title': 'Ethereum network upgrade successfully deployed',
            'source': 'Cointelegraph',
            'time': '4 hours ago',
            'url': 'https://cointelegraph.com',
            'sentiment': 'positive'
        },
        {
            'title': 'DeFi protocols see record Total Value Locked',
            'source': 'DeFi Pulse',
            'time': '6 hours ago',
            'url': 'https://defipulse.com',
            'sentiment': 'positive'
        },
        {
            'title': 'Major exchange introduces new security features',
            'source': 'CryptoNews',
            'time': '8 hours ago',
            'url': 'https://cryptonews.com',
            'sentiment': 'neutral'
        },
        {
            'title': 'Regulatory clarity expected in Q1 2024',
            'source': 'Bloomberg Crypto',
            'time': '10 hours ago',
            'url': 'https://bloomberg.com',
            'sentiment': 'neutral'
        }
    ]

def generate_market_stats() -> Dict[str, Any]:
    """Generate mock market statistics"""
    return {
        'total_market_cap': 2.1e12,
        'total_volume_24h': 89.5e9,
        'btc_dominance': 48.2,
        'eth_dominance': 17.5,
        'altcoin_market_cap': 0.72e12,
        'defi_tvl': 45.2e9,
        'nft_volume_24h': 125e6,
        'fear_greed_index': 65,
        'fear_greed_label': 'Greed',
        'active_cryptocurrencies': 10523,
        'active_markets': 847,
        'market_cap_change_24h': 3.2,
        'volume_change_24h': 5.8
    }


# ==================== REST API Endpoints ====================

@app.get("/")
async def root():
    """Serve main dashboard"""
    return FileResponse("crypto_dashboard_pro.html")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Crypto Intelligence Dashboard API",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/coins/top")
async def get_top_coins(limit: int = 10):
    """Get top cryptocurrencies by market cap"""
    try:
        coins = generate_mock_coin_data(limit)
        return {
            "success": True,
            "coins": coins,
            "count": len(coins),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching top coins: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/coins/{symbol}")
async def get_coin_detail(symbol: str):
    """Get detailed information about a specific cryptocurrency"""
    try:
        coins = generate_mock_coin_data()
        coin = next((c for c in coins if c['symbol'].lower() == symbol.lower()), None)
        
        if not coin:
            raise HTTPException(status_code=404, detail=f"Coin {symbol} not found")
        
        # Add additional details
        coin['circulating_supply'] = coin['market_cap'] / coin['price']
        coin['max_supply'] = coin['circulating_supply'] * 1.2  # Mock value
        coin['ath'] = coin['price'] * 1.5  # Mock ATH
        coin['atl'] = coin['price'] * 0.1  # Mock ATL
        
        return {
            "success": True,
            "coin": coin,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching coin detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/stats")
async def get_market_stats():
    """Get overall market statistics"""
    try:
        stats = generate_market_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching market stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/latest")
async def get_latest_news(limit: int = 10):
    """Get latest cryptocurrency news"""
    try:
        news = generate_mock_news()[:limit]
        return {
            "success": True,
            "news": news,
            "count": len(news),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def process_query(payload: Dict[str, str]):
    """Process natural language cryptocurrency queries"""
    try:
        query = payload.get('query', '').strip()
        
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Parse query
        parsed = parse_query(query)
        logger.info(f"Processed query: {query} -> {parsed}")
        
        # Handle different query types
        if parsed['type'] == 'price':
            coin_name = parsed['params'][0] if parsed['params'] else 'bitcoin'
            coins = generate_mock_coin_data()
            coin = next((c for c in coins if coin_name.lower() in c['name'].lower() or 
                        coin_name.lower() in c['symbol'].lower()), None)
            
            if coin:
                return {
                    "success": True,
                    "type": "price",
                    "coin": coin['name'],
                    "symbol": coin['symbol'],
                    "price": coin['price'],
                    "change_24h": coin['change_24h'],
                    "message": f"{coin['name']} ({coin['symbol']}) is currently ${coin['price']:,.2f}"
                }
        
        elif parsed['type'] == 'top_coins':
            count = int(parsed['params'][0]) if parsed['params'] else 10
            coins = generate_mock_coin_data(count)
            return {
                "success": True,
                "type": "list",
                "data": coins,
                "message": f"Showing top {count} cryptocurrencies"
            }
        
        elif parsed['type'] == 'sentiment':
            return {
                "success": True,
                "type": "info",
                "message": "Current market sentiment: Greed (65/100). Market shows bullish indicators.",
                "data": {
                    "sentiment_score": 65,
                    "label": "Greed",
                    "bullish_percentage": 45,
                    "neutral_percentage": 30,
                    "bearish_percentage": 25
                }
            }
        
        elif parsed['type'] == 'defi':
            return {
                "success": True,
                "type": "info",
                "message": "Total Value Locked in DeFi: $45.2B (+8.3% this week)",
                "data": {
                    "tvl": 45.2e9,
                    "change_7d": 8.3,
                    "top_protocols": ["Aave", "Uniswap", "Curve", "MakerDAO"]
                }
            }
        
        elif parsed['type'] == 'nft':
            return {
                "success": True,
                "type": "info",
                "message": "NFT 24h volume: $125M. Top collection: Bored Ape Yacht Club",
                "data": {
                    "volume_24h": 125e6,
                    "sales_24h": 12500,
                    "top_collection": "Bored Ape Yacht Club"
                }
            }
        
        elif parsed['type'] == 'gas':
            return {
                "success": True,
                "type": "info",
                "message": "Current Ethereum gas price: 25 Gwei (Standard: ~$2.50)",
                "data": {
                    "slow": 20,
                    "standard": 25,
                    "fast": 30,
                    "rapid": 35
                }
            }
        
        else:
            # General query response
            return {
                "success": True,
                "type": "info",
                "message": f"Query '{query}' processed. Showing relevant cryptocurrency data.",
                "data": generate_mock_coin_data(5)
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/providers")
async def get_providers():
    """Get configured API providers"""
    try:
        config = load_providers_config()
        providers = config.get("providers", {})
        
        result = []
        for provider_id, provider_data in providers.items():
            result.append({
                "provider_id": provider_id,
                "name": provider_data.get("name", provider_id),
                "category": provider_data.get("category", "unknown"),
                "status": "validated" if provider_data.get("validated") else "unvalidated",
                "response_time_ms": provider_data.get("response_time_ms")
            })
        
        return {
            "success": True,
            "providers": result,
            "total": len(result)
        }
    except Exception as e:
        logger.error(f"Error fetching providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/charts/price/{symbol}")
async def get_price_chart(symbol: str, timeframe: str = "7d"):
    """Get price chart data for a cryptocurrency"""
    try:
        # Generate mock price data
        days = {
            "1d": 24,
            "7d": 168,
            "30d": 720,
            "90d": 2160
        }.get(timeframe, 168)
        
        base_price = 43250 if symbol.lower() == 'btc' else 2280
        data = []
        
        for i in range(days):
            timestamp = datetime.now() - timedelta(hours=days-i)
            price = base_price * (1 + (i % 10 - 5) / 100)  # Simulate price changes
            data.append({
                "timestamp": timestamp.isoformat(),
                "price": round(price, 2)
            })
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "data": data
        }
    except Exception as e:
        logger.error(f"Error generating chart data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WebSocket Endpoint ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Crypto Intelligence Dashboard",
            "timestamp": datetime.now().isoformat()
        })
        
        # Start background task for price updates
        update_task = asyncio.create_task(send_price_updates(websocket))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                # Handle client messages if needed
                logger.info(f"Received from client: {data}")
            except WebSocketDisconnect:
                break
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
    finally:
        try:
            update_task.cancel()
        except:
            pass

async def send_price_updates(websocket: WebSocket):
    """Send periodic price updates to connected clients"""
    while True:
        try:
            # Wait 10 seconds between updates
            await asyncio.sleep(10)
            
            # Generate updated price data
            coins = generate_mock_coin_data(5)
            
            # Send update
            await websocket.send_json({
                "type": "price_update",
                "payload": coins,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error sending price update: {e}")
            break


# ==================== Startup Event ====================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("="*60)
    logger.info("Crypto Intelligence Dashboard API Starting...")
    logger.info("="*60)
    logger.info("Service: Crypto Intelligence Dashboard")
    logger.info("Version: 1.0.0")
    logger.info("Features:")
    logger.info("  ✓ REST API for cryptocurrency data")
    logger.info("  ✓ Natural language query processing")
    logger.info("  ✓ WebSocket real-time updates")
    logger.info("  ✓ Market statistics and analysis")
    logger.info("  ✓ News aggregation")
    logger.info("  ✓ Provider integration")
    logger.info("="*60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
