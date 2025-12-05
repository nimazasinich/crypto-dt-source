# 🚀 Crypto Resources - Quick Reference Card

## 📦 What You Have

### Database Files
```
consolidated_crypto_resources.json  (186 KB) - Full JSON database
consolidated_crypto_resources.csv   (78 KB)  - Excel/Sheets compatible
consolidated_crypto_resources.db    (172 KB) - SQLite with indexes
```

### Python Scripts
```
resource_manager.py            - Query resources (Python library)
websocket_integrator.py        - WebSocket client for real-time data
consolidated_resource_service.py - FastAPI integration
consolidate_resources.py       - Regenerate database (if needed)
```

## 🎯 Quick Start (Copy & Paste)

### 1. Query Resources in Python
```python
from backend.services.consolidated_resource_service import get_resource_service

service = get_resource_service()

# Get free market data APIs
market_apis = service.get_all_market_data_sources(free_only=True)
print(f"Found {len(market_apis)} market data sources")

# Get WebSocket sources
websockets = service.get_all_websocket_sources()
print(f"Found {len(websockets)} WebSocket sources")

# Search for Bitcoin APIs
bitcoin = service.search_resources('bitcoin')
print(f"Found {len(bitcoin)} Bitcoin-related APIs")
```

### 2. Query with SQL
```bash
sqlite3 /workspace/cursor-instructions/consolidated_crypto_resources.db
```
```sql
-- Get all free market data APIs
SELECT name, base_url FROM resources 
WHERE category = 'market_data_apis' AND is_free = 1;

-- Get WebSocket resources
SELECT name, base_url FROM resources 
WHERE websocket_support = 1;

-- Count by category
SELECT category, COUNT(*) as count 
FROM resources GROUP BY category 
ORDER BY count DESC;
```

### 3. Use WebSockets
```python
import asyncio
from websocket_integrator import WebSocketManager

async def main():
    manager = WebSocketManager()
    await manager.connect_all_websockets()
    print(f"Connected: {len(manager.get_connected_clients())} sources")

asyncio.run(main())
```

### 4. Add to FastAPI
```python
from backend.services.consolidated_resource_service import create_resource_router

app.include_router(create_resource_router())

# Access at:
# GET /api/consolidated-resources/market-data
# GET /api/consolidated-resources/export
```

## 🔑 Ready-to-Use API Keys

```python
ETHERSCAN_KEY = "SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2"  # 5 calls/sec
BSCSCAN_KEY = "K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT"   # 5 calls/sec
TRONSCAN_KEY = "7ae72726-bffe-4e74-9c33-97b761eeea21"
CMC_KEY = "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c"     # 333/day
CRYPTOCOMPARE_KEY = "e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f"  # 100K/month
```

## 📊 What's Inside

- **305 unique resources** (256 free, 49 paid)
- **18 WebSocket streams** for real-time data
- **106 local backend endpoints** already in your project
- **24 RPC nodes** for blockchain data
- **40 block explorers** (Ethereum, BSC, Tron, etc.)
- **38 market data APIs** for prices & charts
- **19 news sources** for crypto news
- **15 sentiment APIs** for market mood
- **11 whale tracking** for large transactions

## 💡 Common Use Cases

### Get Bitcoin Price
```python
service = get_resource_service()
apis = service.get_resource_pool('market_data_apis', count=3)

for api in apis:
    try:
        # Use api['base_url'], api['api_key'], etc.
        price = fetch_price(api)
        break
    except:
        continue  # Try next API
```

### Monitor Real-Time Data
```python
from websocket_integrator import WebSocketClient
from resource_manager import ResourceManager

manager = ResourceManager()
with manager:
    ws_resource = manager.get_resource_by_id('local_ws_market_data')
    client = WebSocketClient(ws_resource)
    await client.connect()
    client.add_callback(lambda data: print(f"Price: {data}"))
    await client.receive_loop()
```

### Load Balance Requests
```python
import random

service = get_resource_service()
pool = service.get_resource_pool('market_data_apis', count=5)

# Round-robin or random selection
api = random.choice(pool)
# or: api = pool[request_count % len(pool)]
```

## 🛠️ Useful Commands

### Regenerate Database
```bash
cd /workspace/cursor-instructions
python3 consolidate_resources.py
```

### Test Integration
```bash
python3 /workspace/backend/services/consolidated_resource_service.py
```

### View Statistics
```python
from backend.services.consolidated_resource_service import get_resource_service
stats = get_resource_service().get_statistics()
print(stats)
```

### Export for Frontend
```python
service = get_resource_service()
config = service.export_for_frontend()
# Returns structured config with all resources
```

## 📁 File Locations

```
📂 cursor-instructions/
├── 📄 consolidated_crypto_resources.json   ← Main database
├── 📄 consolidated_crypto_resources.csv    ← Excel format
├── 📄 consolidated_crypto_resources.db     ← SQL database
├── 🐍 resource_manager.py                  ← Python library
├── 🐍 websocket_integrator.py              ← WebSocket client
├── 📖 CONSOLIDATED_RESOURCES_README.md     ← Full docs
├── 📖 IMPLEMENTATION_SUMMARY.md            ← Overview
└── 📖 QUICK_REFERENCE.md                   ← This file

📂 backend/services/
└── 🐍 consolidated_resource_service.py     ← FastAPI service
```

## 🔗 Categories

| Category | Free | Total | WebSocket |
|----------|------|-------|-----------|
| Local Endpoints | 106 | 106 | 16 |
| RPC Nodes | 24 | 24 | 1 |
| Block Explorers | 29 | 40 | 0 |
| Market Data | 32 | 38 | 0 |
| News | 19 | 19 | 0 |
| Sentiment | 15 | 15 | 0 |
| On-Chain | 8 | 13 | 0 |
| Whale Track | 9 | 11 | 0 |

## ⚡ Top Free APIs

### Market Data (No Auth Required)
- CoinGecko: `https://api.coingecko.com/api/v3`
- Binance: `https://api.binance.com/api/v3`
- CoinCap: `https://api.coincap.io/v2`

### Block Explorers (Open Source)
- BlockScout: `https://eth.blockscout.com/api`
- Blockchair: `https://api.blockchair.com` (1440/day)

### News (Free)
- CryptoPanic: `https://cryptopanic.com/api/v1`
- Reddit: `https://reddit.com/r/CryptoCurrency/hot.json`

### Sentiment (Free)
- Alternative.me: `https://api.alternative.me/fng/` (Fear & Greed)

## 🎓 Next Steps

1. **Read Full Docs**: `CONSOLIDATED_RESOURCES_README.md`
2. **Review Examples**: Code samples in Python scripts
3. **Test SQL Queries**: Practice with SQLite database
4. **Add to FastAPI**: Include resource router in main app
5. **Build Features**: Use resources for market data, news, etc.

## 📞 Need Help?

- **Full Documentation**: CONSOLIDATED_RESOURCES_README.md
- **Implementation Guide**: IMPLEMENTATION_SUMMARY.md
- **Code Examples**: resource_manager.py, websocket_integrator.py
- **Database Schema**: Check consolidated_crypto_resources.db

---

**305 Resources** | **256 Free** | **18 WebSockets** | **3 Formats** | **Ready to Use** 🚀
