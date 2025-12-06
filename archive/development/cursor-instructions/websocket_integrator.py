"""
WebSocket Integration for Crypto Resources
Connects to WebSocket-enabled crypto data sources
"""

import asyncio
import websockets
import json
from typing import Dict, List, Callable, Optional
from resource_manager import ResourceManager, CryptoResource


class WebSocketClient:
    """WebSocket client for crypto data streams"""
    
    def __init__(self, resource: CryptoResource):
        self.resource = resource
        self.websocket = None
        self.is_connected = False
        self.callbacks = []
        
    async def connect(self):
        """Connect to WebSocket"""
        try:
            url = self.resource.base_url
            
            # Add API key if required
            if self.resource.api_key and self.resource.auth_type != 'none':
                # Some APIs require key in URL
                if '{API_KEY}' in url:
                    url = url.replace('{API_KEY}', self.resource.api_key)
                elif '{PROJECT_ID}' in url:
                    url = url.replace('{PROJECT_ID}', self.resource.api_key)
            
            self.websocket = await websockets.connect(url)
            self.is_connected = True
            print(f"✅ Connected to {self.resource.name}")
            
        except Exception as e:
            print(f"❌ Failed to connect to {self.resource.name}: {e}")
            self.is_connected = False
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            print(f"🔌 Disconnected from {self.resource.name}")
    
    def add_callback(self, callback: Callable):
        """Add message callback"""
        self.callbacks.append(callback)
    
    async def send(self, message: Dict):
        """Send message to WebSocket"""
        if not self.is_connected or not self.websocket:
            raise ConnectionError("Not connected")
        
        await self.websocket.send(json.dumps(message))
    
    async def receive_loop(self):
        """Receive messages in loop"""
        if not self.is_connected or not self.websocket:
            return
        
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                # Call all callbacks
                for callback in self.callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(data)
                        else:
                            callback(data)
                    except Exception as e:
                        print(f"Callback error: {e}")
                        
        except websockets.exceptions.ConnectionClosed:
            print(f"Connection closed: {self.resource.name}")
            self.is_connected = False
        except Exception as e:
            print(f"Error in receive loop: {e}")
            self.is_connected = False


class WebSocketManager:
    """Manages multiple WebSocket connections"""
    
    def __init__(self):
        self.clients: Dict[str, WebSocketClient] = {}
        self.resource_manager = ResourceManager()
        
    async def connect_to_resource(self, resource_id: str) -> Optional[WebSocketClient]:
        """Connect to a specific resource"""
        with self.resource_manager:
            resource = self.resource_manager.get_resource_by_id(resource_id)
            
            if not resource:
                print(f"Resource not found: {resource_id}")
                return None
            
            if not resource.websocket_support:
                print(f"Resource does not support WebSocket: {resource.name}")
                return None
            
            client = WebSocketClient(resource)
            await client.connect()
            
            if client.is_connected:
                self.clients[resource_id] = client
                return client
            
            return None
    
    async def connect_all_websockets(self):
        """Connect to all available WebSocket resources"""
        with self.resource_manager:
            ws_resources = self.resource_manager.get_websocket_resources()
            
            print(f"\n🔌 Connecting to {len(ws_resources)} WebSocket resources...\n")
            
            for resource in ws_resources:
                client = WebSocketClient(resource)
                await client.connect()
                
                if client.is_connected:
                    self.clients[resource.id] = client
                
                # Small delay between connections
                await asyncio.sleep(0.5)
            
            connected_count = len([c for c in self.clients.values() if c.is_connected])
            print(f"\n✅ Connected to {connected_count}/{len(ws_resources)} WebSocket resources")
    
    async def disconnect_all(self):
        """Disconnect from all WebSockets"""
        for client in self.clients.values():
            if client.is_connected:
                await client.disconnect()
        
        self.clients.clear()
    
    def get_client(self, resource_id: str) -> Optional[WebSocketClient]:
        """Get WebSocket client by resource ID"""
        return self.clients.get(resource_id)
    
    def get_connected_clients(self) -> List[WebSocketClient]:
        """Get all connected clients"""
        return [c for c in self.clients.values() if c.is_connected]


# Example: Real-time market data aggregator
class MarketDataAggregator:
    """Aggregates market data from multiple WebSocket sources"""
    
    def __init__(self):
        self.ws_manager = WebSocketManager()
        self.latest_prices = {}
        
    async def handle_price_update(self, data: Dict):
        """Handle incoming price data"""
        # This would need to be customized based on each API's response format
        if 'price' in data:
            symbol = data.get('symbol', 'UNKNOWN')
            price = data.get('price')
            self.latest_prices[symbol] = price
            print(f"💰 {symbol}: ${price}")
    
    async def start(self):
        """Start aggregating market data"""
        # Connect to WebSocket sources
        await self.ws_manager.connect_all_websockets()
        
        # Add callback to all clients
        for client in self.ws_manager.get_connected_clients():
            client.add_callback(self.handle_price_update)
            
            # Subscribe to price updates (format varies by API)
            try:
                await client.send({
                    "method": "SUBSCRIBE",
                    "params": ["btcusdt@trade"],
                    "id": 1
                })
            except:
                pass  # Some WebSockets don't need subscription
        
        # Run receive loops
        tasks = []
        for client in self.ws_manager.get_connected_clients():
            tasks.append(asyncio.create_task(client.receive_loop()))
        
        # Wait for all tasks
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop(self):
        """Stop aggregation"""
        await self.ws_manager.disconnect_all()


# Example usage
async def demo_websocket_connections():
    """Demo: Connect to available WebSocket resources"""
    manager = WebSocketManager()
    
    try:
        # Connect to all WebSockets
        await manager.connect_all_websockets()
        
        # Keep connections alive
        print("\n⏳ Keeping connections alive for 10 seconds...")
        await asyncio.sleep(10)
        
    finally:
        # Cleanup
        await manager.disconnect_all()


async def demo_market_data():
    """Demo: Real-time market data aggregation"""
    aggregator = MarketDataAggregator()
    
    try:
        print("\n📊 Starting market data aggregation...")
        await asyncio.wait_for(aggregator.start(), timeout=30)
    except asyncio.TimeoutError:
        print("\n⏱️ Demo timeout reached")
    finally:
        await aggregator.stop()


if __name__ == "__main__":
    # Show available WebSocket resources
    manager = ResourceManager()
    
    with manager:
        ws_resources = manager.get_websocket_resources()
        
        print("\n" + "="*80)
        print("AVAILABLE WEBSOCKET RESOURCES")
        print("="*80 + "\n")
        
        for resource in ws_resources:
            print(f"🔌 {resource.name}")
            print(f"   URL: {resource.base_url}")
            print(f"   Category: {resource.category}")
            print(f"   Auth: {resource.auth_type}")
            print(f"   Free: {resource.is_free}")
            print()
        
        print(f"Total WebSocket resources: {len(ws_resources)}\n")
    
    # Run demo
    print("\n🚀 Running WebSocket connection demo...")
    asyncio.run(demo_websocket_connections())
