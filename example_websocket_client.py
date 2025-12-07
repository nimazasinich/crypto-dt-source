#!/usr/bin/env python3
"""
Example WebSocket Client for Cryptocurrency Server
Demonstrates how to connect and receive real-time price updates
"""

import asyncio
import json
import sys

try:
    import websockets
except ImportError:
    print("❌ Missing websockets package")
    print("Install: pip install websockets")
    sys.exit(1)


async def crypto_websocket_client(symbols: list[str], duration: int = 60):
    """
    Connect to cryptocurrency WebSocket server and receive price updates
    
    Args:
        symbols: List of cryptocurrency symbols (e.g., ["BTC", "ETH"])
        duration: How long to run in seconds (default: 60)
    """
    uri = "ws://localhost:8000/ws"
    
    print(f"🔌 Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to server\n")
            
            # Wait for welcome message
            welcome_msg = await websocket.recv()
            welcome = json.loads(welcome_msg)
            print(f"Server: {welcome.get('message')}")
            print(f"Client ID: {welcome.get('client_id')}\n")
            
            # Subscribe to symbols
            print(f"📡 Subscribing to: {', '.join(symbols)}\n")
            for symbol in symbols:
                subscribe_msg = {
                    "type": "subscribe",
                    "symbol": symbol
                }
                await websocket.send(json.dumps(subscribe_msg))
            
            # Receive messages
            print("=" * 60)
            print("Real-time Price Updates")
            print("=" * 60)
            
            import time
            start_time = time.time()
            
            while time.time() - start_time < duration:
                try:
                    message = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=2.0
                    )
                    data = json.loads(message)
                    
                    msg_type = data.get("type")
                    
                    if msg_type == "subscribed":
                        symbol = data.get("symbol")
                        print(f"✅ Subscribed to {symbol}")
                    
                    elif msg_type == "price_update":
                        symbol = data.get("symbol")
                        price = data.get("price")
                        source = data.get("source")
                        timestamp = data.get("timestamp")
                        
                        print(f"💰 {symbol}: ${price:,.2f} (Source: {source})")
                    
                    elif msg_type == "error":
                        error = data.get("error")
                        print(f"⚠️  Error: {error}")
                    
                    elif msg_type == "pong":
                        print("🏓 Pong received")
                
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    await websocket.send(json.dumps({"type": "ping"}))
            
            print("\n" + "=" * 60)
            print(f"✅ Completed. Ran for {duration} seconds")
            print("=" * 60)
            
            # Unsubscribe from all symbols
            print("\n📴 Unsubscribing from all symbols...")
            for symbol in symbols:
                unsubscribe_msg = {
                    "type": "unsubscribe",
                    "symbol": symbol
                }
                await websocket.send(json.dumps(unsubscribe_msg))
                
                # Wait for confirmation
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                confirm = json.loads(response)
                if confirm.get("type") == "unsubscribed":
                    print(f"✅ Unsubscribed from {confirm.get('symbol')}")
    
    except websockets.exceptions.ConnectionClosed:
        print("⚠️  Connection closed by server")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def interactive_client():
    """Interactive WebSocket client"""
    uri = "ws://localhost:8000/ws"
    
    print("=" * 60)
    print("Interactive Cryptocurrency WebSocket Client")
    print("=" * 60)
    print("\nCommands:")
    print("  subscribe <SYMBOL>  - Subscribe to a symbol (e.g., subscribe BTC)")
    print("  unsubscribe <SYMBOL> - Unsubscribe from a symbol")
    print("  list - List current subscriptions")
    print("  ping - Send ping to server")
    print("  quit - Exit")
    print("=" * 60 + "\n")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to server\n")
            
            # Wait for welcome message
            welcome_msg = await websocket.recv()
            welcome = json.loads(welcome_msg)
            print(f"Client ID: {welcome.get('client_id')}\n")
            
            # Start receiving messages in background
            async def receive_messages():
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        msg_type = data.get("type")
                        
                        if msg_type == "price_update":
                            symbol = data.get("symbol")
                            price = data.get("price")
                            print(f"💰 {symbol}: ${price:,.2f}")
                        elif msg_type == "subscribed":
                            print(f"✅ Subscribed to {data.get('symbol')}")
                        elif msg_type == "unsubscribed":
                            print(f"📴 Unsubscribed from {data.get('symbol')}")
                        elif msg_type == "subscriptions":
                            subs = data.get("subscriptions", [])
                            print(f"Current subscriptions: {', '.join(subs) if subs else 'None'}")
                        elif msg_type == "pong":
                            print("🏓 Pong")
                        elif msg_type == "error":
                            print(f"⚠️  {data.get('error')}")
                    
                    except websockets.exceptions.ConnectionClosed:
                        break
            
            # Start background task
            receive_task = asyncio.create_task(receive_messages())
            
            # Interactive command loop
            print("Enter commands (type 'help' for list):")
            
            while True:
                try:
                    # Read command from user
                    cmd = await asyncio.get_event_loop().run_in_executor(
                        None, input, "> "
                    )
                    
                    cmd = cmd.strip()
                    
                    if not cmd:
                        continue
                    
                    parts = cmd.split()
                    command = parts[0].lower()
                    
                    if command == "quit" or command == "exit":
                        print("Exiting...")
                        break
                    
                    elif command == "subscribe" and len(parts) > 1:
                        symbol = parts[1].upper()
                        await websocket.send(json.dumps({
                            "type": "subscribe",
                            "symbol": symbol
                        }))
                    
                    elif command == "unsubscribe" and len(parts) > 1:
                        symbol = parts[1].upper()
                        await websocket.send(json.dumps({
                            "type": "unsubscribe",
                            "symbol": symbol
                        }))
                    
                    elif command == "list":
                        await websocket.send(json.dumps({
                            "type": "get_subscriptions"
                        }))
                    
                    elif command == "ping":
                        await websocket.send(json.dumps({
                            "type": "ping"
                        }))
                    
                    elif command == "help":
                        print("\nCommands:")
                        print("  subscribe <SYMBOL>  - Subscribe to a symbol")
                        print("  unsubscribe <SYMBOL> - Unsubscribe from a symbol")
                        print("  list - List current subscriptions")
                        print("  ping - Send ping to server")
                        print("  quit - Exit\n")
                    
                    else:
                        print(f"Unknown command: {command}")
                        print("Type 'help' for available commands")
                
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
            
            # Cancel background task
            receive_task.cancel()
    
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Run with specific symbols from command line
        symbols = [s.upper() for s in sys.argv[1:]]
        duration = 30  # Run for 30 seconds
        
        print(f"Running WebSocket client for symbols: {', '.join(symbols)}")
        print(f"Duration: {duration} seconds\n")
        
        asyncio.run(crypto_websocket_client(symbols, duration))
    else:
        # Run interactive mode
        asyncio.run(interactive_client())


if __name__ == "__main__":
    main()
