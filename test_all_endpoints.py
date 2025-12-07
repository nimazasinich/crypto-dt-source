#!/usr/bin/env python3
"""
Test All Extended Endpoints
Tests all 25+ endpoints to ensure they work correctly
"""

import asyncio
import json
from typing import Dict, Any

try:
    import httpx
    import websockets
except ImportError:
    print("❌ Missing packages. Install: pip install httpx websockets")
    exit(1)


class ExtendedEndpointTester:
    """Test all extended endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        self.passed = 0
        self.failed = 0
    
    async def test_endpoint(self, method: str, path: str, description: str, **kwargs):
        """Test a single endpoint"""
        print(f"\n{'='*70}")
        print(f"TEST: {description}")
        print(f"{method} {path}")
        print('='*70)
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                if method == "GET":
                    response = await client.get(f"{self.base_url}{path}", **kwargs)
                elif method == "POST":
                    response = await client.post(f"{self.base_url}{path}", **kwargs)
                
                print(f"Status: {response.status_code}")
                
                if response.status_code < 400:
                    data = response.json()
                    print(f"✅ SUCCESS")
                    print(f"Response keys: {list(data.keys())}")
                    self.passed += 1
                else:
                    print(f"❌ FAILED: {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    self.failed += 1
        
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            self.failed += 1
    
    async def test_all(self):
        """Test all endpoints"""
        print("\n" + "="*70)
        print("🧪 TESTING ALL EXTENDED ENDPOINTS")
        print("="*70)
        
        # Market endpoints
        await self.test_endpoint("GET", "/api/market?limit=3", "Market data (with /api)")
        await self.test_endpoint("GET", "/market?limit=3", "Market data (without /api)")
        await self.test_endpoint("GET", "/api/market?limit=3&symbol=BTC,ETH,SOL", "Market with symbols")
        await self.test_endpoint("GET", "/api/market/history?symbol=BTC/USDT&timeframe=1h&limit=10", "Market history")
        await self.test_endpoint("GET", "/api/market/price?symbol=BTC", "Current price")
        
        # OHLCV endpoints
        await self.test_endpoint("GET", "/api/ohlcv?symbol=BTC&timeframe=1h&limit=10", "OHLCV (with /api)")
        await self.test_endpoint("GET", "/ohlcv?symbol=BTC&timeframe=1h&limit=10", "OHLCV (without /api)")
        await self.test_endpoint("GET", "/api/market/ohlc?symbol=ETH&timeframe=4h&limit=5", "Market OHLC")
        
        # Stats endpoints
        await self.test_endpoint("GET", "/api/stats", "Stats (with /api)")
        await self.test_endpoint("GET", "/stats", "Stats (without /api)")
        
        # AI endpoints
        await self.test_endpoint("GET", "/api/ai/signals?limit=5", "AI signals")
        await self.test_endpoint("POST", "/api/ai/predict", "AI predict",
                                json={"symbol": "BTC", "timeframe": "1h"})
        
        # Portfolio endpoints
        await self.test_endpoint("GET", "/api/trading/portfolio", "Trading portfolio")
        await self.test_endpoint("GET", "/api/portfolio", "Portfolio (alt)")
        await self.test_endpoint("GET", "/api/professional-risk/metrics", "Risk metrics")
        
        # Futures endpoints
        await self.test_endpoint("GET", "/api/futures/positions", "Futures positions")
        await self.test_endpoint("GET", "/api/futures/orders", "Futures orders")
        await self.test_endpoint("GET", "/api/futures/balance", "Futures balance")
        await self.test_endpoint("GET", "/api/futures/orderbook?symbol=BTCUSDT", "Futures orderbook")
        
        # Analysis endpoints
        await self.test_endpoint("GET", "/analysis/harmonic", "Harmonic analysis")
        await self.test_endpoint("GET", "/analysis/elliott", "Elliott analysis")
        await self.test_endpoint("GET", "/analysis/smc", "SMC analysis")
        await self.test_endpoint("GET", "/analysis/sentiment?symbol=BTC", "Sentiment analysis")
        await self.test_endpoint("GET", "/analysis/whale?symbol=BTC", "Whale analysis")
        
        # Other endpoints
        await self.test_endpoint("GET", "/api/training-metrics", "Training metrics")
        await self.test_endpoint("GET", "/api/scoring/snapshot?symbol=BTCUSDT&tfs=1h&tfs=4h", "Scoring snapshot")
        await self.test_endpoint("GET", "/api/entry-plan?symbol=BTCUSDT&accountBalance=1000&riskPercent=2", "Entry plan")
        await self.test_endpoint("POST", "/api/strategies/pipeline/run", "Strategy pipeline")
        
        # Sentiment analyze
        await self.test_endpoint("POST", "/api/sentiment/analyze", "Sentiment analyze",
                                json={"text": "Bitcoin is bullish!"})
        
        # WebSocket test
        await self.test_websocket()
        
        # Print summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        print("="*70)
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! 🎉\n")
        else:
            print(f"\n⚠️  {self.failed} tests failed\n")
    
    async def test_websocket(self):
        """Test WebSocket connection"""
        print(f"\n{'='*70}")
        print(f"TEST: WebSocket Connection")
        print(f"WS {self.ws_url}/ws")
        print('='*70)
        
        try:
            async with websockets.connect(f"{self.ws_url}/ws", open_timeout=10) as ws:
                # Wait for welcome
                welcome = await asyncio.wait_for(ws.recv(), timeout=5)
                welcome_data = json.loads(welcome)
                print(f"✅ Connected: {welcome_data.get('message')}")
                
                # Subscribe
                await ws.send(json.dumps({"type": "subscribe", "symbol": "BTC"}))
                
                # Wait for confirmation
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                response_data = json.loads(response)
                
                if response_data.get("type") == "subscribed":
                    print(f"✅ Subscribed to {response_data.get('symbol')}")
                    self.passed += 1
                else:
                    print(f"⚠️  Unexpected response: {response_data}")
                    self.failed += 1
        
        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")
            self.failed += 1


async def main():
    """Main function"""
    import sys
    
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"\n🌐 Testing server at: {base_url}\n")
    
    tester = ExtendedEndpointTester(base_url)
    await tester.test_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
