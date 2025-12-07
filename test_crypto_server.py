#!/usr/bin/env python3
"""
Test script for Cryptocurrency Server
Tests HTTP endpoints and WebSocket connections
"""

import asyncio
import json
import time
from typing import Dict, Any

try:
    import httpx
    import websockets
except ImportError:
    print("❌ Missing required packages")
    print("Please install: pip install httpx websockets")
    exit(1)


class CryptoServerTester:
    """Test client for cryptocurrency server"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
    
    async def test_health_check(self):
        """Test health check endpoint"""
        print("\n" + "="*60)
        print("TEST: Health Check")
        print("="*60)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            assert response.status_code == 200
            print("✅ Health check passed")
    
    async def test_get_price(self, symbol: str = "BTC"):
        """Test GET /api/market/price endpoint"""
        print("\n" + "="*60)
        print(f"TEST: Get Current Price for {symbol}")
        print("="*60)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/market/price",
                params={"symbol": symbol}
            )
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                print(f"✅ Successfully fetched price: ${data['price']:,.2f}")
            else:
                print(f"❌ Error: {response.json()}")
    
    async def test_get_ohlc(self, symbol: str = "ETH", timeframe: str = "1h", limit: int = 10):
        """Test GET /api/market/ohlc endpoint"""
        print("\n" + "="*60)
        print(f"TEST: Get OHLC Data for {symbol} ({timeframe})")
        print("="*60)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/market/ohlc",
                params={
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "limit": limit
                }
            )
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Symbol: {data['symbol']}")
                print(f"Timeframe: {data['timeframe']}")
                print(f"Data Points: {len(data['ohlc'])}")
                
                if data['ohlc']:
                    print("\nFirst 3 candles:")
                    for candle in data['ohlc'][:3]:
                        print(f"  Timestamp: {candle['timestamp']}")
                        print(f"  Open: {candle['open']}, High: {candle['high']}, "
                              f"Low: {candle['low']}, Close: {candle['close']}")
                        print(f"  Volume: {candle['volume']}")
                        print()
                
                print(f"✅ Successfully fetched {len(data['ohlc'])} OHLC data points")
            else:
                print(f"❌ Error: {response.json()}")
    
    async def test_sentiment_analysis(self, text: str):
        """Test POST /api/sentiment/analyze endpoint"""
        print("\n" + "="*60)
        print("TEST: Sentiment Analysis")
        print("="*60)
        print(f"Text: {text}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/sentiment/analyze",
                json={"text": text}
            )
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                print(f"✅ Sentiment: {data['sentiment']} (Confidence: {data['confidence']:.2%})")
            else:
                print(f"❌ Error: {response.json()}")
    
    async def test_websocket(self, symbol: str = "BTC", duration: int = 20):
        """Test WebSocket connection and data streaming"""
        print("\n" + "="*60)
        print(f"TEST: WebSocket Connection (subscribing to {symbol})")
        print("="*60)
        
        try:
            async with websockets.connect(f"{self.ws_url}/ws") as websocket:
                print("✅ Connected to WebSocket")
                
                # Wait for welcome message
                welcome = await websocket.recv()
                print(f"Server: {welcome}")
                
                # Subscribe to symbol
                subscribe_msg = {
                    "type": "subscribe",
                    "symbol": symbol
                }
                await websocket.send(json.dumps(subscribe_msg))
                print(f"📡 Sent subscription request for {symbol}")
                
                # Receive messages for specified duration
                end_time = time.time() + duration
                message_count = 0
                
                while time.time() < end_time:
                    try:
                        message = await asyncio.wait_for(
                            websocket.recv(),
                            timeout=2.0
                        )
                        data = json.loads(message)
                        message_count += 1
                        
                        msg_type = data.get("type")
                        
                        if msg_type == "subscribed":
                            print(f"✅ Subscribed to {data.get('symbol')}")
                        elif msg_type == "price_update":
                            print(f"💰 Price Update: {data.get('symbol')} = ${data.get('price'):,.2f} "
                                  f"(Source: {data.get('source')})")
                        elif msg_type == "error":
                            print(f"⚠️ Error: {data.get('error')}")
                        else:
                            print(f"📨 Message: {json.dumps(data, indent=2)}")
                    
                    except asyncio.TimeoutError:
                        # Send ping to keep connection alive
                        await websocket.send(json.dumps({"type": "ping"}))
                
                # Unsubscribe
                unsubscribe_msg = {
                    "type": "unsubscribe",
                    "symbol": symbol
                }
                await websocket.send(json.dumps(unsubscribe_msg))
                
                # Wait for confirmation
                response = await websocket.recv()
                print(f"Server: {response}")
                
                print(f"\n✅ WebSocket test completed. Received {message_count} messages")
        
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
    
    async def test_error_handling(self):
        """Test error handling"""
        print("\n" + "="*60)
        print("TEST: Error Handling")
        print("="*60)
        
        async with httpx.AsyncClient() as client:
            # Test invalid symbol
            print("\n1. Testing invalid symbol...")
            response = await client.get(
                f"{self.base_url}/api/market/price",
                params={"symbol": "INVALID_SYMBOL_123"}
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            assert response.status_code == 404
            print("✅ 404 error handled correctly")
            
            # Test invalid timeframe
            print("\n2. Testing invalid timeframe...")
            response = await client.get(
                f"{self.base_url}/api/market/ohlc",
                params={
                    "symbol": "BTC",
                    "timeframe": "invalid_timeframe"
                }
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            assert response.status_code == 400
            print("✅ 400 error handled correctly")
            
            # Test empty sentiment text
            print("\n3. Testing empty sentiment text...")
            response = await client.post(
                f"{self.base_url}/api/sentiment/analyze",
                json={"text": ""}
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            assert response.status_code in [400, 422]
            print("✅ Empty text error handled correctly")
    
    async def test_rate_limiting(self):
        """Test rate limiting"""
        print("\n" + "="*60)
        print("TEST: Rate Limiting")
        print("="*60)
        
        async with httpx.AsyncClient() as client:
            print("Sending 105 requests rapidly...")
            
            success_count = 0
            rate_limited_count = 0
            
            for i in range(105):
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited_count += 1
                    if rate_limited_count == 1:
                        print(f"\n⚠️ Rate limit hit after {success_count} requests")
                        print(f"Response: {json.dumps(response.json(), indent=2)}")
                
                # Small delay to avoid connection issues
                await asyncio.sleep(0.01)
            
            print(f"\nResults:")
            print(f"  Successful: {success_count}")
            print(f"  Rate Limited: {rate_limited_count}")
            
            if rate_limited_count > 0:
                print("✅ Rate limiting is working correctly")
            else:
                print("⚠️ Rate limiting might not be working as expected")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("🧪 CRYPTOCURRENCY SERVER TEST SUITE")
        print("="*60)
        
        try:
            # Basic tests
            await self.test_health_check()
            await self.test_get_price("BTC")
            await self.test_get_price("ETH")
            await self.test_get_ohlc("ETH", "1h", 10)
            await self.test_get_ohlc("BTC", "4h", 5)
            
            # Sentiment analysis tests
            await self.test_sentiment_analysis(
                "Bitcoin is surging! Great bullish momentum. Buy now!"
            )
            await self.test_sentiment_analysis(
                "Market crash incoming. Bearish sentiment everywhere. Time to sell."
            )
            await self.test_sentiment_analysis(
                "The price is stable. No major changes expected."
            )
            
            # Error handling tests
            await self.test_error_handling()
            
            # Rate limiting test
            await self.test_rate_limiting()
            
            # WebSocket test (shorter duration for testing)
            await self.test_websocket("BTC", duration=15)
            
            print("\n" + "="*60)
            print("✅ ALL TESTS COMPLETED")
            print("="*60)
        
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main function"""
    import sys
    
    # Parse command line arguments
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"Testing server at: {base_url}")
    
    tester = CryptoServerTester(base_url)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
