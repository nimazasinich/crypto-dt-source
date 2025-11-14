# WebSocket API Documentation

Comprehensive guide to accessing all services via WebSocket connections.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Master Endpoints](#master-endpoints)
- [Data Collection Services](#data-collection-services)
- [Monitoring Services](#monitoring-services)
- [Integration Services](#integration-services)
- [Message Protocol](#message-protocol)
- [Code Examples](#code-examples)
- [Available Services](#available-services)

---

## Overview

The Crypto API Monitoring System provides comprehensive WebSocket APIs for real-time streaming of all services. All WebSocket endpoints support:

- **Subscription-based routing**: Subscribe only to services you need
- **Real-time updates**: Live data streaming at service-specific intervals
- **Bi-directional communication**: Send commands and receive responses
- **Connection management**: Automatic reconnection and heartbeat
- **Multiple connection patterns**: Master endpoint, service-specific endpoints, or auto-subscribe

---

## Quick Start

### Basic Connection

```javascript
// Connect to the master endpoint
const ws = new WebSocket('ws://localhost:7860/ws/master');

ws.onopen = () => {
    console.log('Connected!');

    // Subscribe to market data
    ws.send(JSON.stringify({
        action: 'subscribe',
        service: 'market_data'
    }));
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('Received:', message);
};
```

### Python Example

```python
import asyncio
import websockets
import json

async def connect():
    uri = "ws://localhost:7860/ws/master"
    async with websockets.connect(uri) as websocket:
        # Subscribe to whale tracking
        await websocket.send(json.dumps({
            "action": "subscribe",
            "service": "whale_tracking"
        }))

        # Receive messages
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")

asyncio.run(connect())
```

---

## Master Endpoints

### `/ws` - Default WebSocket Endpoint

The default endpoint with subscription management capabilities.

**Connection URL**: `ws://localhost:7860/ws`

**Features**:
- Access to all services
- Manual subscription management
- Connection status tracking

### `/ws/master` - Master WebSocket Endpoint

Full-featured endpoint with comprehensive service access.

**Connection URL**: `ws://localhost:7860/ws/master`

**Features**:
- Complete service catalog on connection
- Detailed usage instructions
- Real-time statistics

**Initial Message**:
```json
{
    "service": "system",
    "type": "welcome",
    "data": {
        "message": "Connected to master WebSocket endpoint",
        "available_services": {
            "data_collection": [...],
            "monitoring": [...],
            "integration": [...]
        },
        "usage": {
            "subscribe": {"action": "subscribe", "service": "service_name"}
        }
    },
    "timestamp": "2025-11-11T10:30:00.000Z"
}
```

### `/ws/all` - Auto-Subscribe to All Services

Automatically subscribes to all available services upon connection.

**Connection URL**: `ws://localhost:7860/ws/all`

**Features**:
- Instant access to all service updates
- No manual subscription needed
- Comprehensive data streaming

**Use Case**: Monitoring dashboards that need all data

---

## Data Collection Services

### `/ws/data` - Unified Data Collection Endpoint

Unified endpoint for all data collection services with manual subscription.

**Connection URL**: `ws://localhost:7860/ws/data`

**Available Services**:
- `market_data` - Real-time cryptocurrency prices and volumes
- `explorers` - Blockchain explorer data
- `news` - Cryptocurrency news aggregation
- `sentiment` - Market sentiment analysis
- `whale_tracking` - Large transaction monitoring
- `rpc_nodes` - RPC node status and blockchain events
- `onchain` - On-chain analytics and metrics

### `/ws/market_data` - Market Data Only

Dedicated endpoint for market data (auto-subscribed).

**Connection URL**: `ws://localhost:7860/ws/market_data`

**Update Interval**: 5 seconds

**Message Format**:
```json
{
    "service": "market_data",
    "type": "update",
    "data": {
        "prices": {
            "bitcoin": 45000.00,
            "ethereum": 3200.00
        },
        "volumes": {
            "bitcoin": 25000000000,
            "ethereum": 15000000000
        },
        "market_caps": {...},
        "price_changes": {...},
        "source": "coingecko",
        "timestamp": "2025-11-11T10:30:00.000Z"
    },
    "timestamp": "2025-11-11T10:30:00.000Z"
}
```

### `/ws/whale_tracking` - Whale Tracking Only

Dedicated endpoint for whale transaction monitoring (auto-subscribed).

**Connection URL**: `ws://localhost:7860/ws/whale_tracking`

**Update Interval**: 15 seconds

**Message Format**:
```json
{
    "service": "whale_tracking",
    "type": "update",
    "data": {
        "large_transactions": [
            {
                "hash": "0x...",
                "value": 1000000000,
                "from": "0x...",
                "to": "0x...",
                "timestamp": "2025-11-11T10:29:45.000Z"
            }
        ],
        "whale_wallets": [...],
        "total_volume": 5000000000,
        "alert_threshold": 1000000,
        "timestamp": "2025-11-11T10:30:00.000Z"
    },
    "timestamp": "2025-11-11T10:30:00.000Z"
}
```

### `/ws/news` - News Only

Dedicated endpoint for cryptocurrency news (auto-subscribed).

**Connection URL**: `ws://localhost:7860/ws/news`

**Update Interval**: 60 seconds

**Message Format**:
```json
{
    "service": "news",
    "type": "update",
    "data": {
        "articles": [
            {
                "title": "Bitcoin reaches new high",
                "source": "CoinDesk",
                "url": "https://...",
                "published_at": "2025-11-11T10:25:00.000Z"
            }
        ],
        "sources": ["CoinDesk", "CoinTelegraph"],
        "categories": ["Market", "Technology"],
        "timestamp": "2025-11-11T10:30:00.000Z"
    },
    "timestamp": "2025-11-11T10:30:00.000Z"
}
```

### `/ws/sentiment` - Sentiment Analysis Only

Dedicated endpoint for market sentiment (auto-subscribed).

**Connection URL**: `ws://localhost:7860/ws/sentiment`

**Update Interval**: 30 seconds

**Message Format**:
```json
{
    "service": "sentiment",
    "type": "update",
    "data": {
        "overall_sentiment": "bullish",
        "sentiment_score": 0.75,
        "social_volume": 125000,
        "trending_topics": ["Bitcoin", "Ethereum"],
        "sentiment_by_source": {
            "twitter": 0.80,
            "reddit": 0.70
        },
        "timestamp": "2025-11-11T10:30:00.000Z"
    },
    "timestamp": "2025-11-11T10:30:00.000Z"
}
```

---

## Monitoring Services

### `/ws/monitoring` - Unified Monitoring Endpoint

Unified endpoint for all monitoring services with manual subscription.

**Connection URL**: `ws://localhost:7860/ws/monitoring`

**Available Services**:
- `health_checker` - Provider health monitoring
- `pool_manager` - Source pool management and failover
- `scheduler` - Task scheduler status

### `/ws/health` - Health Monitoring Only

Dedicated endpoint for health checks (auto-subscribed).

**Connection URL**: `ws://localhost:7860/ws/health`

**Update Interval**: 30 seconds

**Message Format**:
```json
{
    "service": "health_checker",
    "type": "update",
    "data": {
        "overall_health": "healthy",
        "healthy_count": 45,
        "unhealthy_count": 2,
        "total_providers": 47,
        "providers": {
            "coingecko": {
                "status": "healthy",
                "response_time_ms": 150,
                "last_check": "2025-11-11T10:30:00.000Z"
            }
        },
        "timestamp": "2025-11-11T10:30:00.000Z"
    },
    "timestamp": "2025-11-11T10:30:00.000Z"
}
```

### `/ws/pool_status` - Pool Manager Only

Dedicated endpoint for source pool management (auto-subscribed).

**Connection URL**: `ws://localhost:7860/ws/pool_status`

**Update Interval**: 20 seconds

**Message Format**:
```json
{
    "service": "pool_manager",
    "type": "update",
    "data": {
        "pools": {
            "market_data": {
                "active_source": "coingecko",
                "available_sources": ["coingecko", "coinmarketcap"],
                "health": "healthy"
            }
        },
        "active_sources": ["coingecko", "etherscan"],
        "inactive_sources": ["blockchair"],
        "failover_count": 2,
        "timestamp": "2025-11-11T10:30:00.000Z"
    },
    "timestamp": "2025-11-11T10:30:00.000Z"
}
```

### `/ws/scheduler_status` - Scheduler Only

Dedicated endpoint for task scheduler (auto-subscribed).

**Connection URL**: `ws://localhost:7860/ws/scheduler_status`

**Update Interval**: 15 seconds

**Message Format**:
```json
{
    "service": "scheduler",
    "type": "update",
    "data": {
        "running": true,
        "total_jobs": 10,
        "active_jobs": 3,
        "jobs": [
            {
                "id": "market_data_collection",
                "next_run": "2025-11-11T10:31:00.000Z",
                "status": "running"
            }
        ],
        "timestamp": "2025-11-11T10:30:00.000Z"
    },
    "timestamp": "2025-11-11T10:30:00.000Z"
}
```

---

## Integration Services

### `/ws/integration` - Unified Integration Endpoint

Unified endpoint for all integration services with manual subscription.

**Connection URL**: `ws://localhost:7860/ws/integration`

**Available Services**:
- `huggingface` - HuggingFace AI/ML services
- `persistence` - Data persistence and export services

### `/ws/huggingface` - HuggingFace Services Only

Dedicated endpoint for HuggingFace AI services (auto-subscribed).

**Connection URL**: `ws://localhost:7860/ws/huggingface`

**Aliases**: `/ws/ai`

**Update Interval**: 60 seconds

**Message Format**:
```json
{
    "service": "huggingface",
    "type": "update",
    "data": {
        "total_models": 25,
        "total_datasets": 10,
        "available_models": ["sentiment-model-1", "sentiment-model-2"],
        "available_datasets": ["crypto-tweets", "reddit-posts"],
        "last_refresh": "2025-11-11T10:00:00.000Z",
        "timestamp": "2025-11-11T10:30:00.000Z"
    },
    "timestamp": "2025-11-11T10:30:00.000Z"
}
```

### `/ws/persistence` - Persistence Services Only

Dedicated endpoint for data persistence (auto-subscribed).

**Connection URL**: `ws://localhost:7860/ws/persistence`

**Update Interval**: 30 seconds

**Message Format**:
```json
{
    "service": "persistence",
    "type": "update",
    "data": {
        "storage_location": "/data/crypto-monitoring",
        "total_records": 1500000,
        "storage_size": "2.5 GB",
        "last_save": "2025-11-11T10:29:55.000Z",
        "active_writers": 3,
        "timestamp": "2025-11-11T10:30:00.000Z"
    },
    "timestamp": "2025-11-11T10:30:00.000Z"
}
```

---

## Message Protocol

### Client to Server Messages

#### Subscribe to a Service

```json
{
    "action": "subscribe",
    "service": "market_data"
}
```

**Available Services**: `market_data`, `explorers`, `news`, `sentiment`, `whale_tracking`, `rpc_nodes`, `onchain`, `health_checker`, `pool_manager`, `scheduler`, `huggingface`, `persistence`, `system`, `all`

#### Unsubscribe from a Service

```json
{
    "action": "unsubscribe",
    "service": "market_data"
}
```

#### Get Connection Status

```json
{
    "action": "get_status"
}
```

**Response**:
```json
{
    "service": "system",
    "type": "status",
    "data": {
        "client_id": "client_1_1731324000",
        "connected_at": "2025-11-11T10:30:00.000Z",
        "last_activity": "2025-11-11T10:30:05.000Z",
        "subscriptions": ["market_data", "whale_tracking"],
        "total_clients": 5
    },
    "timestamp": "2025-11-11T10:30:05.000Z"
}
```

#### Ping/Pong

```json
{
    "action": "ping",
    "data": {"custom": "data"}
}
```

**Response**:
```json
{
    "service": "system",
    "type": "pong",
    "data": {"custom": "data"},
    "timestamp": "2025-11-11T10:30:05.000Z"
}
```

### Server to Client Messages

All server messages follow this format:

```json
{
    "service": "service_name",
    "type": "message_type",
    "data": { },
    "timestamp": "2025-11-11T10:30:00.000Z"
}
```

**Message Types**:
- `connection_established` - Initial connection confirmation
- `welcome` - Welcome message with service information
- `update` - Service data update
- `subscription_confirmed` - Subscription confirmation
- `unsubscription_confirmed` - Unsubscription confirmation
- `status` - Connection status response
- `pong` - Ping response
- `error` - Error message

---

## Code Examples

### JavaScript/TypeScript Client

```javascript
class CryptoWebSocketClient {
    constructor(baseUrl = 'ws://localhost:7860') {
        this.baseUrl = baseUrl;
        this.ws = null;
        this.subscriptions = new Set();
    }

    connect(endpoint = '/ws/master') {
        this.ws = new WebSocket(`${this.baseUrl}${endpoint}`);

        this.ws.onopen = () => {
            console.log('Connected to', endpoint);
            this.onConnected();
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('Disconnected');
            this.onDisconnected();
        };
    }

    subscribe(service) {
        this.send({
            action: 'subscribe',
            service: service
        });
        this.subscriptions.add(service);
    }

    unsubscribe(service) {
        this.send({
            action: 'unsubscribe',
            service: service
        });
        this.subscriptions.delete(service);
    }

    getStatus() {
        this.send({ action: 'get_status' });
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    handleMessage(message) {
        console.log('Received:', message);

        switch (message.type) {
            case 'connection_established':
                console.log('Client ID:', message.data.client_id);
                break;
            case 'update':
                this.onUpdate(message.service, message.data);
                break;
            case 'error':
                console.error('Server error:', message.data.message);
                break;
        }
    }

    onConnected() {
        // Override in subclass
    }

    onDisconnected() {
        // Override in subclass
    }

    onUpdate(service, data) {
        // Override in subclass
        console.log(`Update from ${service}:`, data);
    }
}

// Usage
const client = new CryptoWebSocketClient();
client.connect('/ws/master');

client.onConnected = () => {
    client.subscribe('market_data');
    client.subscribe('whale_tracking');
};

client.onUpdate = (service, data) => {
    if (service === 'market_data') {
        console.log('Prices:', data.prices);
    } else if (service === 'whale_tracking') {
        console.log('Whale transactions:', data.large_transactions);
    }
};
```

### Python Client

```python
import asyncio
import websockets
import json
from typing import Callable, Dict, Any

class CryptoWebSocketClient:
    def __init__(self, base_url: str = "ws://localhost:7860"):
        self.base_url = base_url
        self.ws = None
        self.subscriptions = set()
        self.message_handlers = {}

    async def connect(self, endpoint: str = "/ws/master"):
        uri = f"{self.base_url}{endpoint}"
        async with websockets.connect(uri) as websocket:
            self.ws = websocket
            print(f"Connected to {endpoint}")

            # Handle incoming messages
            async for message in websocket:
                data = json.loads(message)
                await self.handle_message(data)

    async def subscribe(self, service: str):
        await self.send({
            "action": "subscribe",
            "service": service
        })
        self.subscriptions.add(service)

    async def unsubscribe(self, service: str):
        await self.send({
            "action": "unsubscribe",
            "service": service
        })
        self.subscriptions.discard(service)

    async def get_status(self):
        await self.send({"action": "get_status"})

    async def send(self, data: Dict[str, Any]):
        if self.ws:
            await self.ws.send(json.dumps(data))

    async def handle_message(self, message: Dict[str, Any]):
        msg_type = message.get("type")
        service = message.get("service")

        if msg_type == "connection_established":
            print(f"Client ID: {message['data']['client_id']}")
            await self.on_connected()
        elif msg_type == "update":
            await self.on_update(service, message["data"])
        elif msg_type == "error":
            print(f"Error: {message['data']['message']}")

    async def on_connected(self):
        # Override in subclass
        pass

    async def on_update(self, service: str, data: Dict[str, Any]):
        # Override in subclass or register handlers
        if service in self.message_handlers:
            await self.message_handlers[service](data)
        else:
            print(f"Update from {service}: {data}")

    def register_handler(self, service: str, handler: Callable):
        self.message_handlers[service] = handler

# Usage
async def main():
    client = CryptoWebSocketClient()

    # Register handlers
    async def handle_market_data(data):
        print(f"Prices: {data.get('prices')}")

    async def handle_whale_tracking(data):
        print(f"Large transactions: {data.get('large_transactions')}")

    client.register_handler('market_data', handle_market_data)
    client.register_handler('whale_tracking', handle_whale_tracking)

    # Connect and subscribe
    async def on_connected():
        await client.subscribe('market_data')
        await client.subscribe('whale_tracking')

    client.on_connected = on_connected

    await client.connect('/ws/master')

asyncio.run(main())
```

### React Hook Example

```typescript
import { useEffect, useState, useCallback } from 'react';

interface WebSocketMessage {
    service: string;
    type: string;
    data: any;
    timestamp: string;
}

export function useWebSocket(endpoint: string = '/ws/master') {
    const [ws, setWs] = useState<WebSocket | null>(null);
    const [connected, setConnected] = useState(false);
    const [messages, setMessages] = useState<WebSocketMessage[]>([]);

    useEffect(() => {
        const websocket = new WebSocket(`ws://localhost:7860${endpoint}`);

        websocket.onopen = () => {
            console.log('WebSocket connected');
            setConnected(true);
        };

        websocket.onmessage = (event) => {
            const message: WebSocketMessage = JSON.parse(event.data);
            setMessages(prev => [...prev, message]);
        };

        websocket.onclose = () => {
            console.log('WebSocket disconnected');
            setConnected(false);
        };

        setWs(websocket);

        return () => {
            websocket.close();
        };
    }, [endpoint]);

    const subscribe = useCallback((service: string) => {
        if (ws && connected) {
            ws.send(JSON.stringify({
                action: 'subscribe',
                service: service
            }));
        }
    }, [ws, connected]);

    const unsubscribe = useCallback((service: string) => {
        if (ws && connected) {
            ws.send(JSON.stringify({
                action: 'unsubscribe',
                service: service
            }));
        }
    }, [ws, connected]);

    return { connected, messages, subscribe, unsubscribe };
}

// Usage in component
function MarketDataComponent() {
    const { connected, messages, subscribe } = useWebSocket('/ws/master');

    useEffect(() => {
        if (connected) {
            subscribe('market_data');
        }
    }, [connected, subscribe]);

    const marketDataMessages = messages.filter(m => m.service === 'market_data');

    return (
        <div>
            <h2>Market Data</h2>
            <p>Status: {connected ? 'Connected' : 'Disconnected'}</p>
            {marketDataMessages.map((msg, idx) => (
                <div key={idx}>
                    <p>Prices: {JSON.stringify(msg.data.prices)}</p>
                </div>
            ))}
        </div>
    );
}
```

---

## Available Services

### Data Collection Services

| Service | Description | Update Interval | Endpoint |
|---------|-------------|-----------------|----------|
| `market_data` | Real-time cryptocurrency prices, volumes, and market caps | 5 seconds | `/ws/market_data` |
| `explorers` | Blockchain explorer data and network statistics | 10 seconds | `/ws/data` |
| `news` | Cryptocurrency news aggregation from multiple sources | 60 seconds | `/ws/news` |
| `sentiment` | Market sentiment analysis and social media trends | 30 seconds | `/ws/sentiment` |
| `whale_tracking` | Large transaction monitoring and whale wallet tracking | 15 seconds | `/ws/whale_tracking` |
| `rpc_nodes` | RPC node status and blockchain events | 20 seconds | `/ws/data` |
| `onchain` | On-chain analytics and smart contract events | 30 seconds | `/ws/data` |

### Monitoring Services

| Service | Description | Update Interval | Endpoint |
|---------|-------------|-----------------|----------|
| `health_checker` | Provider health monitoring and status checks | 30 seconds | `/ws/health` |
| `pool_manager` | Source pool management and automatic failover | 20 seconds | `/ws/pool_status` |
| `scheduler` | Task scheduler status and job execution tracking | 15 seconds | `/ws/scheduler_status` |

### Integration Services

| Service | Description | Update Interval | Endpoint |
|---------|-------------|-----------------|----------|
| `huggingface` | HuggingFace AI model registry and sentiment analysis | 60 seconds | `/ws/huggingface` |
| `persistence` | Data persistence, exports, and backup operations | 30 seconds | `/ws/persistence` |

### System Services

| Service | Description | Endpoint |
|---------|-------------|----------|
| `system` | System messages and connection management | All endpoints |
| `all` | Subscribe to all services at once | `/ws/all` |

---

## REST API Endpoints

### Get WebSocket Statistics

```
GET /ws/stats
```

Returns information about active connections and subscriptions.

**Response**:
```json
{
    "status": "success",
    "data": {
        "total_connections": 5,
        "clients": [
            {
                "client_id": "client_1_1731324000",
                "connected_at": "2025-11-11T10:30:00.000Z",
                "last_activity": "2025-11-11T10:35:00.000Z",
                "subscriptions": ["market_data", "whale_tracking"]
            }
        ],
        "subscription_counts": {
            "market_data": 3,
            "whale_tracking": 2,
            "news": 1
        }
    },
    "timestamp": "2025-11-11T10:35:00.000Z"
}
```

### Get Available Services

```
GET /ws/services
```

Returns a comprehensive list of all available services with descriptions.

### Get WebSocket Endpoints

```
GET /ws/endpoints
```

Returns a list of all WebSocket connection URLs.

---

## Error Handling

### Connection Errors

If a connection fails or is lost, implement exponential backoff:

```javascript
class ReconnectingWebSocket {
    constructor(url) {
        this.url = url;
        this.reconnectDelay = 1000;
        this.maxReconnectDelay = 30000;
        this.connect();
    }

    connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onclose = () => {
            console.log(`Reconnecting in ${this.reconnectDelay}ms...`);
            setTimeout(() => {
                this.reconnectDelay = Math.min(
                    this.reconnectDelay * 2,
                    this.maxReconnectDelay
                );
                this.connect();
            }, this.reconnectDelay);
        };

        this.ws.onopen = () => {
            console.log('Connected');
            this.reconnectDelay = 1000; // Reset delay on successful connection
        };
    }
}
```

### Message Errors

Handle error messages from the server:

```javascript
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);

    if (message.type === 'error') {
        console.error('Server error:', message.data.message);

        // Handle specific errors
        if (message.data.message.includes('Invalid service')) {
            console.log('Available services:', message.data.available_services);
        }
    }
};
```

---

## Best Practices

1. **Subscribe Only to What You Need**: Minimize bandwidth by subscribing only to required services
2. **Implement Reconnection Logic**: Handle network interruptions gracefully
3. **Use Heartbeats**: Implement ping/pong to detect connection issues early
4. **Handle Backpressure**: Process messages efficiently to avoid queue buildup
5. **Clean Up Subscriptions**: Unsubscribe when components unmount or services are no longer needed
6. **Use Service-Specific Endpoints**: For single-service needs, use dedicated endpoints to reduce initial setup
7. **Monitor Connection Status**: Track connection state and subscriptions in your application
8. **Implement Error Boundaries**: Gracefully handle and display connection/data errors

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/nimazasinich/crypto-dt-source/issues
- API Documentation: http://localhost:7860/docs

---

## Version

**API Version**: 2.0.0
**Last Updated**: 2025-11-11
