# Consolidated Crypto Resources Database

## 📊 Overview

This directory contains a comprehensive database of **305 unique cryptocurrency data sources** consolidated from multiple configuration files. All resources have been deduplicated, validated, and organized into easy-to-use formats.

### Generated Files

1. **`consolidated_crypto_resources.json`** (186 KB) - Complete JSON database with metadata
2. **`consolidated_crypto_resources.csv`** (78 KB) - Excel-compatible CSV for analysis
3. **`consolidated_crypto_resources.db`** (172 KB) - SQLite database for querying

## 📈 Statistics

- **Total Resources**: 305
- **Free Resources**: 256 (84%)
- **Paid/Limited**: 49 (16%)
- **WebSocket Enabled**: 18
- **REST APIs**: 287

### Resource Categories

| Category | Count |
|----------|-------|
| Local Backend Routes | 106 |
| RPC Nodes | 24 |
| Block Explorers | 23 |
| Market Data APIs | 21 |
| News APIs | 15 |
| On-Chain Analytics | 13 |
| Sentiment APIs | 12 |
| Whale Tracking | 9 |
| API Keys | 8 |
| HuggingFace Resources | 7 |
| CORS Proxies | 7 |
| Community Sentiment | 1 |

## 🚀 Usage

### Python Integration

```python
from resource_manager import ResourceManager

# Initialize manager
manager = ResourceManager()

with manager:
    # Get all free resources
    free_resources = manager.get_free_resources()
    
    # Get resources by category
    market_apis = manager.get_resources_by_category('market_data_apis')
    
    # Get WebSocket resources
    ws_resources = manager.get_websocket_resources()
    
    # Search resources
    bitcoin_apis = manager.search_resources('bitcoin')
    
    # Get random resource for load balancing
    random_api = manager.get_random_resource('market_data_apis', free_only=True)
    
    # Get statistics
    stats = manager.get_statistics()
    print(stats)
```

### WebSocket Integration

```python
import asyncio
from websocket_integrator import WebSocketManager

async def main():
    manager = WebSocketManager()
    
    # Connect to all WebSocket resources
    await manager.connect_all_websockets()
    
    # Or connect to specific resource
    client = await manager.connect_to_resource('alchemy_eth_mainnet_ws')
    
    if client:
        # Add message handler
        client.add_callback(lambda data: print(data))
        
        # Start receiving messages
        await client.receive_loop()

asyncio.run(main())
```

### SQL Queries

```sql
-- Get all free market data APIs
SELECT * FROM resources 
WHERE category = 'market_data_apis' 
AND is_free = 1;

-- Get WebSocket-enabled resources
SELECT name, base_url FROM resources 
WHERE websocket_support = 1;

-- Get resources by data type
SELECT r.name, r.base_url, dt.data_type
FROM resources r
JOIN data_types dt ON r.id = dt.resource_id
WHERE dt.data_type = 'price_data';

-- Category statistics
SELECT category, COUNT(*) as count
FROM resources
GROUP BY category
ORDER BY count DESC;
```

### CSV Analysis (Excel)

Open `consolidated_crypto_resources.csv` in Excel or Google Sheets to:
- Filter by category, free/paid status, or WebSocket support
- Sort by any field
- Create pivot tables
- Export to other formats

## 🔑 API Keys Included

The following API keys are embedded and ready to use:

| Service | Key | Rate Limit |
|---------|-----|------------|
| Etherscan | `SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2` | 5 calls/sec |
| Etherscan (Backup) | `T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45` | 5 calls/sec |
| BscScan | `K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT` | 5 calls/sec |
| TronScan | `7ae72726-bffe-4e74-9c33-97b761eeea21` | Varies |
| CoinMarketCap | `b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c` | 333/day |
| CoinMarketCap (Backup) | `04cf4b5b-9868-465c-8ba0-9f2e78c92eb1` | 333/day |
| CryptoCompare | `e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f` | 100K/month |
| NewsAPI | `pub_346789abc123def456789ghi012345jkl` | 100/day |

## 🌐 WebSocket Resources

The database includes 18 WebSocket-enabled resources for real-time data:

### Ethereum
- Alchemy Ethereum Mainnet WS: `wss://eth-mainnet.g.alchemy.com/v2/{API_KEY}`

### Local Backend
- WebSocket Live: `ws://{API_BASE}/ws/live`
- WebSocket Master: `ws://{API_BASE}/ws/master`
- WebSocket Market Data: `ws://{API_BASE}/ws/market_data`
- WebSocket News: `ws://{API_BASE}/ws/news`
- WebSocket Sentiment: `ws://{API_BASE}/ws/sentiment`
- WebSocket Whale Tracking: `ws://{API_BASE}/ws/whale_tracking`
- And 11 more local WebSocket endpoints

## 📊 Data Types Available

Each resource is tagged with the type of data it provides:

- **Blockchain Data**: Transaction data, block data, smart contracts
- **Price Data**: Real-time prices, OHLCV, market cap, volume
- **News**: Articles, headlines, content
- **Sentiment**: Fear & Greed Index, social metrics, mood analysis
- **Whale Tracking**: Large transactions, whale addresses, transfer data
- **On-Chain Metrics**: Network statistics, indicators, analytics
- **Address Data**: Balances, transaction history, token holdings

## 🔗 Addressing Methods

Resources use different API patterns:

- **REST API (Query Parameters)**: 119 resources
- **REST API (Path Parameters)**: 103 resources
- **WebSocket**: 18 resources
- **GraphQL**: 3 resources

## 🎯 Featured Resources

### Best Free Market Data APIs
1. **CoinGecko** - No API key, no CORS issues, 10-50 calls/min
2. **Binance Public API** - Real-time prices, no auth required
3. **CoinCap** - 200 requests/min, completely free
4. **CoinPaprika** - 20K calls/month free

### Best Free Block Explorers
1. **BlockScout** - Open source, unlimited requests
2. **Blockchair** - 1,440 requests/day free
3. **Ethplorer** - Token data, free tier available

### Best Free RPC Nodes
1. **PublicNode** - Free for all networks
2. **Ankr** - Public endpoints, no rate limits
3. **LlamaNodes** - No registration required

## 💾 Database Schema

### Resources Table
```sql
CREATE TABLE resources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    subcategory TEXT,
    base_url TEXT,
    auth_type TEXT,
    api_key TEXT,
    rate_limit TEXT,
    docs_url TEXT,
    endpoints TEXT,
    notes TEXT,
    is_free BOOLEAN,
    websocket_support BOOLEAN,
    addressing_method TEXT,
    source TEXT,
    created_at TIMESTAMP
);
```

### Data Types Table
```sql
CREATE TABLE data_types (
    resource_id TEXT,
    data_type TEXT,
    FOREIGN KEY (resource_id) REFERENCES resources (id)
);
```

## 🛠️ Integration Scripts

### consolidate_resources.py
Main consolidation script that:
- Parses JSON, TXT, and DOCX files
- Deduplicates resources
- Generates JSON, CSV, and SQLite outputs

### resource_manager.py
Python library for accessing resources:
- Query by category, type, or keywords
- Load balancing with random selection
- Statistics and analysis
- Easy integration with existing code

### websocket_integrator.py
WebSocket client implementation:
- Async connection management
- Multiple simultaneous connections
- Callback system for message handling
- Market data aggregation example

## 📝 Source Files

Resources were consolidated from:
1. `crypto_resources_unified_2025-11-11.json` - Primary resource registry
2. `ultimate_crypto_pipeline_2025_NZasinich.json` - 162 additional sources
3. `api-config-complete.txt` - Detailed API documentation with keys

## 🔄 Update Process

To regenerate the consolidated database after adding new resources:

```bash
cd /workspace/cursor-instructions
python3 consolidate_resources.py
```

This will:
1. Parse all source files
2. Deduplicate entries
3. Regenerate JSON, CSV, and SQLite files
4. Print comprehensive statistics

## 🎓 Examples

### Example 1: Get Bitcoin Price from Multiple Sources

```python
from resource_manager import ResourceManager
import requests

manager = ResourceManager()

with manager:
    market_apis = manager.get_resources_by_category('market_data_apis', free_only=True)
    
    for api in market_apis[:3]:
        try:
            # This is simplified - actual implementation would need proper endpoint formatting
            response = requests.get(f"{api.base_url}/bitcoin/price")
            print(f"{api.name}: ${response.json()['price']}")
        except:
            continue
```

### Example 2: Monitor Multiple WebSocket Streams

```python
import asyncio
from websocket_integrator import WebSocketManager

async def main():
    manager = WebSocketManager()
    await manager.connect_all_websockets()
    
    # Add handlers
    for client in manager.get_connected_clients():
        client.add_callback(lambda data: print(f"{client.resource.name}: {data}"))
    
    # Run for 1 hour
    await asyncio.sleep(3600)
    await manager.disconnect_all()

asyncio.run(main())
```

### Example 3: Export to Project Database

```python
from resource_manager import export_to_project

# Export all resources to /workspace/data/crypto_resources.json
export_to_project()
```

## 🔒 Security Notes

- API keys are included for convenience but should be rotated regularly
- Never expose API keys in frontend code
- Use environment variables for production
- Implement rate limiting to avoid hitting API limits
- Monitor API usage to stay within free tiers

## 📄 License

All resources are consolidated from publicly available sources. Respect each service's terms of service and rate limits.

## 🤝 Contributing

To add new resources:
1. Add them to one of the source JSON files
2. Run `consolidate_resources.py`
3. Test with `resource_manager.py`

## 📞 Support

For issues or questions:
- Check the generated SQLite database for full details
- Review source files for original documentation
- Test endpoints with included examples

---

**Last Updated**: December 5, 2025
**Version**: 1.0
**Total Resources**: 305
**Database Size**: 172 KB (SQLite), 186 KB (JSON), 78 KB (CSV)
