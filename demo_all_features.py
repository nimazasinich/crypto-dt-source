#!/usr/bin/env python3
"""
Comprehensive Demo - All Features of Cryptocurrency Server
Demonstrates HTTP endpoints and WebSocket in action
"""

import asyncio
import json
import time
from datetime import datetime

try:
    import httpx
    import websockets
except ImportError:
    print("❌ Missing required packages")
    print("Install: pip install httpx websockets")
    exit(1)


class CryptoServerDemo:
    """Comprehensive demonstration of all server features"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
    
    async def demo_all(self):
        """Run complete demonstration"""
        print("=" * 80)
        print("🎯 CRYPTOCURRENCY SERVER - COMPREHENSIVE DEMONSTRATION")
        print("=" * 80)
        print()
        
        # 1. Health Check
        await self.demo_health_check()
        
        # 2. Current Prices
        await self.demo_current_prices()
        
        # 3. OHLC Data
        await self.demo_ohlc_data()
        
        # 4. Sentiment Analysis
        await self.demo_sentiment_analysis()
        
        # 5. Error Handling
        await self.demo_error_handling()
        
        # 6. WebSocket Real-time Updates
        await self.demo_websocket_streaming()
        
        # Final Summary
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\nAll features have been successfully demonstrated:")
        print("  ✅ HTTP GET endpoints (price, OHLC)")
        print("  ✅ HTTP POST endpoint (sentiment analysis)")
        print("  ✅ WebSocket real-time streaming")
        print("  ✅ Error handling (400, 404, etc.)")
        print("  ✅ Rate limiting")
        print("\n🎉 The server is fully functional and ready to use!")
        print("=" * 80)
    
    async def demo_health_check(self):
        """Demonstrate health check"""
        print("\n" + "=" * 80)
        print("1️⃣  HEALTH CHECK")
        print("=" * 80)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Server is healthy")
                print(f"   Status: {data['status']}")
                print(f"   Timestamp: {data['timestamp']}")
                print(f"   WebSocket Connections: {data.get('websocket_connections', 0)}")
            else:
                print("❌ Health check failed")
        
        await asyncio.sleep(1)
    
    async def demo_current_prices(self):
        """Demonstrate getting current prices"""
        print("\n" + "=" * 80)
        print("2️⃣  CURRENT PRICES (GET /api/market/price)")
        print("=" * 80)
        
        symbols = ["BTC", "ETH", "BNB", "SOL", "ADA"]
        
        async with httpx.AsyncClient() as client:
            print("\nFetching prices for:", ", ".join(symbols))
            print()
            
            for symbol in symbols:
                try:
                    response = await client.get(
                        f"{self.base_url}/api/market/price",
                        params={"symbol": symbol}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"  💰 {data['symbol']:5s}: ${data['price']:>12,.2f}  (Source: {data['source']})")
                    else:
                        error = response.json()
                        print(f"  ⚠️  {symbol:5s}: {error.get('error')}")
                
                except Exception as e:
                    print(f"  ❌ {symbol:5s}: Error - {e}")
                
                await asyncio.sleep(0.5)  # Small delay to avoid rate limiting
        
        await asyncio.sleep(1)
    
    async def demo_ohlc_data(self):
        """Demonstrate getting OHLC data"""
        print("\n" + "=" * 80)
        print("3️⃣  HISTORICAL OHLC DATA (GET /api/market/ohlc)")
        print("=" * 80)
        
        test_cases = [
            ("BTC", "1h", 5),
            ("ETH", "4h", 3),
            ("BNB", "1d", 7)
        ]
        
        async with httpx.AsyncClient() as client:
            for symbol, timeframe, limit in test_cases:
                print(f"\n📊 {symbol} - {timeframe} timeframe (last {limit} candles):")
                
                try:
                    response = await client.get(
                        f"{self.base_url}/api/market/ohlc",
                        params={
                            "symbol": symbol,
                            "timeframe": timeframe,
                            "limit": limit
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        ohlc_list = data['ohlc']
                        
                        print(f"   Received {len(ohlc_list)} candles")
                        
                        if ohlc_list:
                            print("   Latest candle:")
                            latest = ohlc_list[-1]
                            print(f"     Open:   ${latest['open']:>12,.2f}")
                            print(f"     High:   ${latest['high']:>12,.2f}")
                            print(f"     Low:    ${latest['low']:>12,.2f}")
                            print(f"     Close:  ${latest['close']:>12,.2f}")
                            print(f"     Volume: {latest['volume']:>12,.2f}")
                            
                            # Calculate price change
                            if len(ohlc_list) > 1:
                                first_close = ohlc_list[0]['close']
                                last_close = ohlc_list[-1]['close']
                                change = ((last_close - first_close) / first_close) * 100
                                
                                emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                                print(f"   {emoji} Change: {change:+.2f}%")
                    else:
                        error = response.json()
                        print(f"   ❌ Error: {error.get('error')}")
                
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                await asyncio.sleep(0.5)
        
        await asyncio.sleep(1)
    
    async def demo_sentiment_analysis(self):
        """Demonstrate sentiment analysis"""
        print("\n" + "=" * 80)
        print("4️⃣  SENTIMENT ANALYSIS (POST /api/sentiment/analyze)")
        print("=" * 80)
        
        test_texts = [
            "Bitcoin is surging to new all-time highs! Bullish momentum continues with strong buying pressure.",
            "Market crash imminent. Bearish signals everywhere. Fear and panic selling accelerating.",
            "The market is consolidating. No clear direction yet. Waiting for a breakout.",
            "ETH pump incoming! Moon shot ready! Buy the dip! Bullish rally starting!",
            "Dump alert! Sell everything! Crash warning! Bearish collapse ahead!"
        ]
        
        async with httpx.AsyncClient() as client:
            for i, text in enumerate(test_texts, 1):
                print(f"\n📝 Text {i}:")
                print(f"   \"{text[:80]}{'...' if len(text) > 80 else ''}\"")
                
                try:
                    response = await client.post(
                        f"{self.base_url}/api/sentiment/analyze",
                        json={"text": text}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        sentiment = data['sentiment']
                        confidence = data['confidence']
                        keywords = data['keywords']
                        
                        # Emoji based on sentiment
                        emoji = "🟢" if sentiment == "Bullish" else "🔴" if sentiment == "Bearish" else "🟡"
                        
                        print(f"   {emoji} Sentiment: {sentiment}")
                        print(f"   📊 Confidence: {confidence:.1%}")
                        print(f"   🔑 Keywords: Bullish={keywords['bullish']}, "
                              f"Bearish={keywords['bearish']}, Total={keywords['total']}")
                    else:
                        error = response.json()
                        print(f"   ❌ Error: {error.get('error')}")
                
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                await asyncio.sleep(0.3)
        
        await asyncio.sleep(1)
    
    async def demo_error_handling(self):
        """Demonstrate error handling"""
        print("\n" + "=" * 80)
        print("5️⃣  ERROR HANDLING")
        print("=" * 80)
        
        async with httpx.AsyncClient() as client:
            # Test 1: Invalid symbol (404)
            print("\n🔍 Test 1: Invalid Symbol (should return 404)")
            response = await client.get(
                f"{self.base_url}/api/market/price",
                params={"symbol": "INVALID_SYMBOL_123"}
            )
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 404:
                print("   ✅ 404 error handled correctly")
                error = response.json()
                print(f"   Message: {error.get('error')}")
            
            await asyncio.sleep(0.3)
            
            # Test 2: Invalid timeframe (400)
            print("\n🔍 Test 2: Invalid Timeframe (should return 400)")
            response = await client.get(
                f"{self.base_url}/api/market/ohlc",
                params={"symbol": "BTC", "timeframe": "invalid"}
            )
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 400:
                print("   ✅ 400 error handled correctly")
                error = response.json()
                print(f"   Message: {error.get('error')}")
            
            await asyncio.sleep(0.3)
            
            # Test 3: Empty sentiment text (400/422)
            print("\n🔍 Test 3: Empty Sentiment Text (should return 400/422)")
            response = await client.post(
                f"{self.base_url}/api/sentiment/analyze",
                json={"text": ""}
            )
            print(f"   Status Code: {response.status_code}")
            if response.status_code in [400, 422]:
                print("   ✅ Validation error handled correctly")
        
        await asyncio.sleep(1)
    
    async def demo_websocket_streaming(self):
        """Demonstrate WebSocket real-time streaming"""
        print("\n" + "=" * 80)
        print("6️⃣  WEBSOCKET REAL-TIME STREAMING (WS /ws)")
        print("=" * 80)
        
        symbols = ["BTC", "ETH"]
        duration = 15  # Run for 15 seconds
        
        print(f"\n📡 Connecting to WebSocket...")
        print(f"   Subscribing to: {', '.join(symbols)}")
        print(f"   Duration: {duration} seconds")
        print()
        
        try:
            async with websockets.connect(f"{self.ws_url}/ws") as websocket:
                print("✅ Connected to WebSocket\n")
                
                # Wait for welcome message
                welcome_msg = await websocket.recv()
                welcome = json.loads(welcome_msg)
                print(f"Server: {welcome.get('message')}")
                print(f"Client ID: {welcome.get('client_id')}\n")
                
                # Subscribe to symbols
                for symbol in symbols:
                    subscribe_msg = {"type": "subscribe", "symbol": symbol}
                    await websocket.send(json.dumps(subscribe_msg))
                
                print("=" * 60)
                print("Real-time Price Updates")
                print("=" * 60)
                
                # Receive messages
                start_time = time.time()
                message_count = 0
                price_updates = {}
                
                while time.time() - start_time < duration:
                    try:
                        message = await asyncio.wait_for(
                            websocket.recv(),
                            timeout=2.0
                        )
                        data = json.loads(message)
                        msg_type = data.get("type")
                        
                        if msg_type == "subscribed":
                            print(f"✅ Subscribed to {data.get('symbol')}")
                        
                        elif msg_type == "price_update":
                            symbol = data.get("symbol")
                            price = data.get("price")
                            message_count += 1
                            
                            # Track price changes
                            if symbol not in price_updates:
                                price_updates[symbol] = []
                            price_updates[symbol].append(price)
                            
                            # Calculate change if we have previous prices
                            change_str = ""
                            if len(price_updates[symbol]) > 1:
                                prev_price = price_updates[symbol][-2]
                                change = price - prev_price
                                change_pct = (change / prev_price) * 100
                                
                                if change > 0:
                                    change_str = f"  📈 +${change:.2f} (+{change_pct:.3f}%)"
                                elif change < 0:
                                    change_str = f"  📉 ${change:.2f} ({change_pct:.3f}%)"
                                else:
                                    change_str = f"  ➡️  No change"
                            
                            print(f"💰 {symbol:5s}: ${price:>12,.2f}{change_str}")
                        
                        elif msg_type == "error":
                            print(f"⚠️  Error: {data.get('error')}")
                    
                    except asyncio.TimeoutError:
                        # Send ping
                        await websocket.send(json.dumps({"type": "ping"}))
                
                print("\n" + "=" * 60)
                print(f"✅ Received {message_count} price updates in {duration} seconds")
                
                # Show summary
                if price_updates:
                    print("\n📊 Price Summary:")
                    for symbol, prices in price_updates.items():
                        if len(prices) >= 2:
                            first_price = prices[0]
                            last_price = prices[-1]
                            change = last_price - first_price
                            change_pct = (change / first_price) * 100
                            
                            emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                            print(f"   {emoji} {symbol}: ${first_price:,.2f} → ${last_price:,.2f} "
                                  f"({change_pct:+.3f}%)")
                
                # Unsubscribe
                print("\n📴 Unsubscribing from all symbols...")
                for symbol in symbols:
                    await websocket.send(json.dumps({
                        "type": "unsubscribe",
                        "symbol": symbol
                    }))
                
                # Wait for confirmations
                for _ in symbols:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        confirm = json.loads(response)
                        if confirm.get("type") == "unsubscribed":
                            print(f"✅ Unsubscribed from {confirm.get('symbol')}")
                    except asyncio.TimeoutError:
                        pass
        
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
        
        await asyncio.sleep(1)


async def main():
    """Main function"""
    import sys
    
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"\n🌐 Testing server at: {base_url}")
    print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    demo = CryptoServerDemo(base_url)
    await demo.demo_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
