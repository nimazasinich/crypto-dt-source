# Enhanced Crypto Data Tracker - New Features

## 🚀 Overview

This document describes the major enhancements added to the crypto data tracking system, including unified configuration management, advanced scheduling, real-time updates via WebSockets, and comprehensive data persistence.

## ✨ New Features

### 1. Unified Configuration Loader

**File:** `backend/services/unified_config_loader.py`

The unified configuration loader automatically imports and manages all API sources from JSON configuration files at the project root.

**Features:**
- Loads from multiple JSON config files:
  - `crypto_resources_unified_2025-11-11.json` (200+ APIs)
  - `all_apis_merged_2025.json`
  - `ultimate_crypto_pipeline_2025_NZasinich.json`
- Automatic API key extraction
- Category-based organization
- Update type classification (realtime, periodic, scheduled)
- Schedule management for each API
- Import/Export functionality

**Usage:**
```python
from backend.services.unified_config_loader import UnifiedConfigLoader

loader = UnifiedConfigLoader()

# Get all APIs
all_apis = loader.get_all_apis()

# Get APIs by category
market_data_apis = loader.get_apis_by_category('market_data')

# Get APIs by update type
realtime_apis = loader.get_realtime_apis()
periodic_apis = loader.get_periodic_apis()

# Add custom API
loader.add_custom_api({
    'id': 'custom_api',
    'name': 'Custom API',
    'category': 'custom',
    'base_url': 'https://api.example.com',
    'update_type': 'periodic',
    'enabled': True
})
```

### 2. Enhanced Scheduling System

**File:** `backend/services/scheduler_service.py`

Advanced scheduler that manages periodic and real-time data updates with automatic error handling and retry logic.

**Features:**
- **Periodic Updates:** Schedule APIs to update at specific intervals
- **Real-time Updates:** WebSocket connections for instant data
- **Scheduled Updates:** Less frequent updates for HuggingFace and other resources
- **Smart Retry:** Automatic interval adjustment on failures
- **Callbacks:** Register callbacks for data updates
- **Force Updates:** Manually trigger immediate updates

**Update Types:**
- `realtime` (0s interval): WebSocket - always connected
- `periodic` (60s interval): Regular polling for market data
- `scheduled` (3600s interval): Hourly updates for HF models/datasets
- `daily` (86400s interval): Once per day

**Usage:**
```python
from backend.services.scheduler_service import SchedulerService

scheduler = SchedulerService(config_loader, db_manager)

# Start scheduler
await scheduler.start()

# Update schedule
scheduler.update_task_schedule('coingecko', interval=120, enabled=True)

# Force update
success = await scheduler.force_update('coingecko')

# Register callback
def on_data_update(api_id, data):
    print(f"Data updated for {api_id}")

scheduler.register_callback('coingecko', on_data_update)

# Get task status
status = scheduler.get_task_status('coingecko')

# Export schedules
scheduler.export_schedules('schedules_backup.json')
```

### 3. Data Persistence Service

**File:** `backend/services/persistence_service.py`

Comprehensive data persistence with multiple export formats and automatic backups.

**Features:**
- In-memory caching for quick access
- Historical data tracking (configurable limit)
- Export to JSON, CSV formats
- Automatic backups
- Database integration (SQLAlchemy)
- Data cleanup utilities

**Usage:**
```python
from backend.services.persistence_service import PersistenceService

persistence = PersistenceService(db_manager)

# Save data
await persistence.save_api_data(
    'coingecko',
    {'price': 50000},
    metadata={'category': 'market_data'}
)

# Get cached data
data = persistence.get_cached_data('coingecko')

# Get history
history = persistence.get_history('coingecko', limit=100)

# Export to JSON
await persistence.export_to_json('export.json', include_history=True)

# Export to CSV
await persistence.export_to_csv('export.csv', flatten=True)

# Create backup
backup_file = await persistence.backup_all_data()

# Restore from backup
await persistence.restore_from_backup(backup_file)

# Cleanup old data (7 days)
removed = await persistence.cleanup_old_data(days=7)
```

### 4. Real-time WebSocket Service

**File:** `backend/services/websocket_service.py`

WebSocket service for real-time bidirectional communication between backend and frontend.

**Features:**
- Connection management with client tracking
- Subscription-based updates (specific APIs or all)
- Real-time notifications for:
  - API data updates
  - System status changes
  - Schedule modifications
- Request-response patterns for data queries
- Heartbeat/ping-pong for connection health

**WebSocket Message Types:**

**Client → Server:**
- `subscribe`: Subscribe to specific API updates
- `subscribe_all`: Subscribe to all updates
- `unsubscribe`: Unsubscribe from API
- `get_data`: Request cached data
- `get_all_data`: Request all cached data
- `get_schedule`: Request schedule information
- `update_schedule`: Update schedule configuration
- `force_update`: Force immediate API update
- `ping`: Heartbeat

**Server → Client:**
- `connected`: Welcome message with client ID
- `api_update`: API data updated
- `status_update`: System status changed
- `schedule_update`: Schedule modified
- `subscribed`: Subscription confirmed
- `data_response`: Data query response
- `schedule_response`: Schedule query response
- `pong`: Heartbeat response
- `error`: Error occurred

**Usage:**

**Frontend JavaScript:**
```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/api/v2/ws');

// Subscribe to all updates
ws.send(JSON.stringify({ type: 'subscribe_all' }));

// Subscribe to specific API
ws.send(JSON.stringify({
    type: 'subscribe',
    api_id: 'coingecko'
}));

// Request data
ws.send(JSON.stringify({
    type: 'get_data',
    api_id: 'coingecko'
}));

// Update schedule
ws.send(JSON.stringify({
    type: 'update_schedule',
    api_id: 'coingecko',
    interval: 120,
    enabled: true
}));

// Force update
ws.send(JSON.stringify({
    type: 'force_update',
    api_id: 'coingecko'
}));

// Handle messages
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);

    switch (message.type) {
        case 'api_update':
            console.log(`${message.api_id} updated:`, message.data);
            break;
        case 'status_update':
            console.log('Status:', message.status);
            break;
    }
};
```

### 5. Integrated Backend API

**File:** `backend/routers/integrated_api.py`

Comprehensive REST API that combines all services.

**Endpoints:**

**Configuration:**
- `GET /api/v2/config/apis` - Get all configured APIs
- `GET /api/v2/config/apis/{api_id}` - Get specific API
- `GET /api/v2/config/categories` - Get all categories
- `GET /api/v2/config/apis/category/{category}` - Get APIs by category
- `POST /api/v2/config/apis` - Add custom API
- `DELETE /api/v2/config/apis/{api_id}` - Remove API
- `GET /api/v2/config/export` - Export configuration

**Scheduling:**
- `GET /api/v2/schedule/tasks` - Get all scheduled tasks
- `GET /api/v2/schedule/tasks/{api_id}` - Get specific task
- `PUT /api/v2/schedule/tasks/{api_id}` - Update schedule
- `POST /api/v2/schedule/tasks/{api_id}/force-update` - Force update
- `GET /api/v2/schedule/export` - Export schedules

**Data:**
- `GET /api/v2/data/cached` - Get all cached data
- `GET /api/v2/data/cached/{api_id}` - Get cached data for API
- `GET /api/v2/data/history/{api_id}` - Get historical data
- `GET /api/v2/data/statistics` - Get storage statistics

**Export/Import:**
- `POST /api/v2/export/json` - Export to JSON
- `POST /api/v2/export/csv` - Export to CSV
- `POST /api/v2/export/history/{api_id}` - Export API history
- `GET /api/v2/download?file={path}` - Download exported file
- `POST /api/v2/backup` - Create backup
- `POST /api/v2/restore` - Restore from backup

**Status:**
- `GET /api/v2/status` - System status
- `GET /api/v2/health` - Health check

**Cleanup:**
- `POST /api/v2/cleanup/cache` - Clear cache
- `POST /api/v2/cleanup/history` - Clear history
- `POST /api/v2/cleanup/old-data` - Remove old data

### 6. Enhanced Server

**File:** `enhanced_server.py`

Production-ready server with all services integrated.

**Features:**
- Automatic service initialization on startup
- Graceful shutdown with final backup
- Comprehensive logging
- CORS support
- Static file serving
- Multiple dashboard routes

**Run the server:**
```bash
python enhanced_server.py
```

**Access points:**
- Main Dashboard: http://localhost:8000/
- Enhanced Dashboard: http://localhost:8000/enhanced_dashboard.html
- API Documentation: http://localhost:8000/docs
- WebSocket: ws://localhost:8000/api/v2/ws

### 7. Enhanced Dashboard UI

**File:** `enhanced_dashboard.html`

Modern, interactive dashboard with real-time updates and full control over the system.

**Features:**
- **Real-time Updates:** WebSocket connection with live data
- **Export Controls:** One-click export to JSON/CSV
- **Backup Management:** Create/restore backups
- **Schedule Configuration:** Adjust update intervals per API
- **Force Updates:** Trigger immediate updates
- **System Statistics:** Live monitoring of system metrics
- **Activity Log:** Real-time activity feed
- **API Management:** View and control all API sources

## 🔧 Installation & Setup

### Prerequisites
```bash
pip install fastapi uvicorn websockets pandas httpx sqlalchemy
```

### Directory Structure
```
crypto-dt-source/
├── backend/
│   ├── routers/
│   │   └── integrated_api.py
│   └── services/
│       ├── unified_config_loader.py
│       ├── scheduler_service.py
│       ├── persistence_service.py
│       └── websocket_service.py
├── database/
│   ├── models.py
│   └── db_manager.py
├── data/
│   ├── exports/
│   └── backups/
├── crypto_resources_unified_2025-11-11.json
├── all_apis_merged_2025.json
├── ultimate_crypto_pipeline_2025_NZasinich.json
├── enhanced_server.py
└── enhanced_dashboard.html
```

### Running the Enhanced Server

1. **Start the server:**
```bash
python enhanced_server.py
```

2. **Access the dashboard:**
   - Open browser to http://localhost:8000/enhanced_dashboard.html

3. **Monitor logs:**
   - Server logs show all activities
   - WebSocket connections
   - Data updates
   - Errors and warnings

## 📊 Configuration

### Scheduling Configuration

Edit schedules via:
1. **Web UI:** Click "Configure Schedule" in enhanced dashboard
2. **API:** Use PUT /api/v2/schedule/tasks/{api_id}
3. **Code:** Call `scheduler.update_task_schedule()`

### Update Types

Configure `update_type` in API configuration:
- `realtime`: WebSocket connection (instant updates)
- `periodic`: Regular polling (default: 60s)
- `scheduled`: Less frequent updates (default: 3600s)
- `daily`: Once per day (default: 86400s)

### Data Retention

Configure in `persistence_service.py`:
```python
max_history_per_api = 1000  # Keep last 1000 records per API
```

Cleanup old data:
```bash
curl -X POST http://localhost:8000/api/v2/cleanup/old-data?days=7
```

## 🔐 Security Notes

- API keys are stored securely in config files
- Keys are masked in exports (shown as ***)
- Database uses SQLite with proper permissions
- CORS configured for security
- WebSocket connections tracked and managed

## 🚀 Performance

- **In-memory caching:** Fast data access
- **Async operations:** Non-blocking I/O
- **Concurrent updates:** Parallel API calls
- **Connection pooling:** Efficient database access
- **Smart retry logic:** Automatic error recovery

## 📝 Examples

### Example 1: Setup and Start
```python
from backend.services.unified_config_loader import UnifiedConfigLoader
from backend.services.scheduler_service import SchedulerService
from backend.services.persistence_service import PersistenceService

# Initialize
config = UnifiedConfigLoader()
persistence = PersistenceService()
scheduler = SchedulerService(config)

# Start scheduler
await scheduler.start()
```

### Example 2: Export Data
```python
# Export all data to JSON
await persistence.export_to_json('all_data.json', include_history=True)

# Export specific APIs to CSV
await persistence.export_to_csv('market_data.csv', api_ids=['coingecko', 'binance'])
```

### Example 3: Custom API
```python
# Add custom API
config.add_custom_api({
    'id': 'my_custom_api',
    'name': 'My Custom API',
    'category': 'custom',
    'base_url': 'https://api.myservice.com/data',
    'auth': {'type': 'apiKey', 'key': 'YOUR_KEY'},
    'update_type': 'periodic',
    'interval': 300
})
```

## 🐛 Troubleshooting

### WebSocket Not Connecting
- Check server is running
- Verify URL: `ws://localhost:8000/api/v2/ws`
- Check browser console for errors
- Ensure no firewall blocking WebSocket

### Data Not Updating
- Check scheduler is running: GET /api/v2/status
- Verify API is enabled in schedule
- Check logs for errors
- Force update: POST /api/v2/schedule/tasks/{api_id}/force-update

### Export Fails
- Ensure `data/exports/` directory exists
- Check disk space
- Verify pandas is installed

## 📚 API Documentation

Full API documentation available at: http://localhost:8000/docs

## 🙏 Credits

Enhanced features developed for comprehensive crypto data tracking with real-time updates, advanced scheduling, and data persistence.
