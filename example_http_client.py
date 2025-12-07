#!/usr/bin/env python3
"""
Example HTTP Client for Cryptocurrency Server
Demonstrates how to use the REST API endpoints
"""

import sys
import json

try:
    import requests
except ImportError:
    print("❌ Missing requests package")
    print("Install: pip install requests")
    sys.exit(1)


class CryptoAPIClient:
    """Simple HTTP client for cryptocurrency server"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def get_price(self, symbol: str) -> dict:
        """Get current price for a cryptocurrency"""
        print(f"\n{'='*60}")
        print(f"Getting current price for {symbol}")
        print('='*60)
        
        response = requests.get(
            f"{self.base_url}/api/market/price",
            params={"symbol": symbol}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Symbol: {data['symbol']}")
            print(f"Price: ${data['price']:,.2f}")
            print(f"Source: {data['source']}")
            print(f"Timestamp: {data['timestamp']}")
            return data
        else:
            error = response.json()
            print(f"❌ Error: {error.get('error')}")
            return None
    
    def get_ohlc(self, symbol: str, timeframe: str = "1h", limit: int = 10) -> dict:
        """Get OHLC data for a cryptocurrency"""
        print(f"\n{'='*60}")
        print(f"Getting OHLC data for {symbol} ({timeframe})")
        print('='*60)
        
        response = requests.get(
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
                print(f"\nLatest candle:")
                latest = data['ohlc'][-1]
                print(f"  Open: ${latest['open']:,.2f}")
                print(f"  High: ${latest['high']:,.2f}")
                print(f"  Low: ${latest['low']:,.2f}")
                print(f"  Close: ${latest['close']:,.2f}")
                print(f"  Volume: {latest['volume']:,.2f}")
            
            return data
        else:
            error = response.json()
            print(f"❌ Error: {error.get('error')}")
            return None
    
    def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment of text"""
        print(f"\n{'='*60}")
        print(f"Analyzing sentiment")
        print('='*60)
        print(f"Text: {text}")
        
        response = requests.post(
            f"{self.base_url}/api/sentiment/analyze",
            json={"text": text}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Sentiment: {data['sentiment']}")
            print(f"Confidence: {data['confidence']:.2%}")
            print(f"Keywords: {data['keywords']}")
            return data
        else:
            error = response.json()
            print(f"❌ Error: {error.get('error')}")
            return None
    
    def health_check(self) -> dict:
        """Check server health"""
        print(f"\n{'='*60}")
        print(f"Health Check")
        print('='*60)
        
        response = requests.get(f"{self.base_url}/health")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data['status']}")
            print(f"WebSocket Connections: {data.get('websocket_connections', 0)}")
            return data
        else:
            print(f"❌ Server is not healthy")
            return None


def demo_usage():
    """Demonstrate API usage"""
    print("=" * 60)
    print("Cryptocurrency Server HTTP Client Demo")
    print("=" * 60)
    
    client = CryptoAPIClient()
    
    # Health check
    client.health_check()
    
    # Get prices
    client.get_price("BTC")
    client.get_price("ETH")
    client.get_price("BNB")
    
    # Get OHLC data
    client.get_ohlc("BTC", "1h", 5)
    client.get_ohlc("ETH", "4h", 10)
    
    # Analyze sentiment
    client.analyze_sentiment(
        "Bitcoin is surging to new all-time highs! Bullish momentum continues!"
    )
    
    client.analyze_sentiment(
        "Market crash imminent. Bearish signals everywhere. Time to sell."
    )
    
    client.analyze_sentiment(
        "The market is consolidating. Waiting for a clear direction."
    )
    
    print("\n" + "=" * 60)
    print("✅ Demo completed")
    print("=" * 60)


def interactive_mode():
    """Interactive mode"""
    client = CryptoAPIClient()
    
    print("=" * 60)
    print("Interactive HTTP Client")
    print("=" * 60)
    print("\nCommands:")
    print("  price <SYMBOL> - Get current price")
    print("  ohlc <SYMBOL> [TIMEFRAME] [LIMIT] - Get OHLC data")
    print("  sentiment <TEXT> - Analyze sentiment")
    print("  health - Check server health")
    print("  demo - Run demo")
    print("  quit - Exit")
    print("=" * 60 + "\n")
    
    while True:
        try:
            cmd = input("> ").strip()
            
            if not cmd:
                continue
            
            parts = cmd.split(maxsplit=1)
            command = parts[0].lower()
            
            if command == "quit" or command == "exit":
                print("Goodbye!")
                break
            
            elif command == "demo":
                demo_usage()
            
            elif command == "health":
                client.health_check()
            
            elif command == "price" and len(parts) > 1:
                symbol = parts[1].upper()
                client.get_price(symbol)
            
            elif command == "ohlc" and len(parts) > 1:
                args = parts[1].split()
                symbol = args[0].upper()
                timeframe = args[1] if len(args) > 1 else "1h"
                limit = int(args[2]) if len(args) > 2 else 10
                client.get_ohlc(symbol, timeframe, limit)
            
            elif command == "sentiment" and len(parts) > 1:
                text = parts[1]
                client.analyze_sentiment(text)
            
            elif command == "help":
                print("\nCommands:")
                print("  price <SYMBOL> - Get current price")
                print("  ohlc <SYMBOL> [TIMEFRAME] [LIMIT] - Get OHLC data")
                print("  sentiment <TEXT> - Analyze sentiment")
                print("  health - Check server health")
                print("  demo - Run demo")
                print("  quit - Exit\n")
            
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_usage()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
