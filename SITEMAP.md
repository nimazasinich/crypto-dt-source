# Complete Site Map - Crypto Monitor ULTIMATE

## 📋 Table of Contents
1. [Frontend Pages & Routes](#frontend-pages--routes)
2. [Backend API Endpoints](#backend-api-endpoints)
3. [Static Assets](#static-assets)
4. [Backend Services](#backend-services)
5. [Database Files](#database-files)
6. [Configuration Files](#configuration-files)
7. [System Monitor Components](#system-monitor-components)

---

## 🌐 Frontend Pages & Routes

### Main Application Pages

| Route | File Path | Description | Access URL |
|-------|-----------|-------------|------------|
| `/` | `static/pages/dashboard/index.html` | Main Dashboard | `http://localhost:7860/` |
| `/dashboard` | `static/pages/dashboard/index.html` | Dashboard Page | `http://localhost:7860/dashboard` |
| `/market` | `static/pages/market/index.html` | Market Data Page | `http://localhost:7860/market` |
| `/models` | `static/pages/models/index.html` | AI Models Page | `http://localhost:7860/models` |
| `/sentiment` | `static/pages/sentiment/index.html` | Sentiment Analysis | `http://localhost:7860/sentiment` |
| `/ai-analyst` | `static/pages/ai-analyst/index.html` | AI Analyst Tool | `http://localhost:7860/ai-analyst` |
| `/technical-analysis` | `static/pages/technical-analysis/index.html` | Technical Analysis | `http://localhost:7860/technical-analysis` |
| `/trading-assistant` | `static/pages/trading-assistant/index.html` | Trading Assistant | `http://localhost:7860/trading-assistant` |
| `/news` | `static/pages/news/index.html` | Crypto News | `http://localhost:7860/news` |
| `/providers` | `static/pages/providers/index.html` | Data Providers | `http://localhost:7860/providers` |
| `/system-monitor` | `static/pages/system-monitor/index.html` | **System Monitor** | `http://localhost:7860/system-monitor` |
| `/help` | `static/pages/help/index.html` | Help & Documentation | `http://localhost:7860/help` |
| `/api-explorer` | `static/pages/api-explorer/index.html` | API Explorer | `http://localhost:7860/api-explorer` |
| `/crypto-api-hub` | `static/pages/crypto-api-hub/index.html` | Crypto API Hub | `http://localhost:7860/crypto-api-hub` |
| `/diagnostics` | `static/pages/diagnostics/index.html` | System Diagnostics | `http://localhost:7860/diagnostics` |

### Static File Structure

```
static/
├── pages/
│   ├── dashboard/
│   │   ├── index.html
│   │   ├── dashboard.js
│   │   └── dashboard.css
│   ├── system-monitor/          ⭐ System Monitor
│   │   ├── index.html           → Main page HTML
│   │   ├── system-monitor.js   → JavaScript logic
│   │   ├── system-monitor.css  → Styling
│   │   └── README.md           → Documentation
│   ├── market/
│   ├── models/
│   ├── sentiment/
│   ├── ai-analyst/
│   ├── technical-analysis/
│   ├── trading-assistant/
│   ├── news/
│   ├── providers/
│   ├── help/
│   ├── api-explorer/
│   └── crypto-api-hub/
├── shared/
│   ├── layouts/
│   │   ├── sidebar.html         → Main sidebar (includes System Monitor link)
│   │   └── sidebar-modern.html  → Modern sidebar variant
│   ├── js/
│   │   ├── core/
│   │   │   ├── layout-manager.js → Loads sidebar/header
│   │   │   ├── api-client.js     → API client
│   │   │   └── models-client.js  → Models API client
│   │   └── sidebar-manager.js
│   └── css/
│       ├── design-system.css
│       ├── global.css
│       ├── components.css
│       └── layout.css
└── assets/
    └── icons/
        └── crypto-icons.js      → Crypto SVG icons
```

---

## 🔌 Backend API Endpoints

### System Monitor API Endpoints

| Endpoint | Method | File Location | Description |
|----------|--------|---------------|-------------|
| `/api/monitoring/status` | GET | `backend/routers/realtime_monitoring_api.py:40` | Get comprehensive system status |
| `/api/monitoring/ws` | WebSocket | `backend/routers/realtime_monitoring_api.py:188` | Real-time WebSocket updates |
| `/api/monitoring/sources/detailed` | GET | `backend/routers/realtime_monitoring_api.py:138` | Get detailed source information |
| `/api/monitoring/requests/recent` | GET | `backend/routers/realtime_monitoring_api.py:171` | Get recent API requests |
| `/api/monitoring/requests/log` | POST | `backend/routers/realtime_monitoring_api.py:181` | Log an API request |

### Core API Endpoints

| Endpoint | Method | File Location | Description |
|----------|--------|---------------|-------------|
| `/api/health` | GET | `hf_unified_server.py` | Health check |
| `/api/status` | GET | `hf_unified_server.py` | System status |
| `/api/models/summary` | GET | `hf_unified_server.py:1226` | Models summary with categories |
| `/api/models/status` | GET | `hf_unified_server.py:814` | Models status |
| `/api/models/list` | GET | `hf_unified_server.py:786` | List all models |
| `/api/resources` | GET | `hf_unified_server.py` | Resources statistics |
| `/api/resources/summary` | GET | `hf_unified_server.py` | Resources summary |
| `/api/resources/categories` | GET | `hf_unified_server.py` | Resources by category |

### Router Endpoints

All routers are included in `hf_unified_server.py`:

1. **Unified Service API** (`backend/routers/unified_service_api.py`)
   - `/api/service/rate`
   - `/api/service/rate/batch`
   - `/api/service/pair/{pair}`
   - `/api/service/sentiment`
   - `/api/service/history`
   - `/api/service/market-status`

2. **Real Data API** (`backend/routers/real_data_api.py`)
   - `/api/models/list`
   - `/api/models/initialize`
   - `/api/sentiment/analyze`
   - `/api/providers`

3. **Direct API** (`backend/routers/direct_api.py`)
   - `/api/v1/coingecko/price`
   - `/api/v1/binance/klines`
   - `/api/v1/hf/sentiment`
   - `/api/v1/hf/models`

4. **Crypto API Hub** (`backend/routers/crypto_api_hub_router.py`)
   - `/api/crypto-hub/*`

5. **AI API** (`backend/routers/ai_api.py`)
   - `/api/ai/*`

6. **Market API** (`backend/routers/market_api.py`)
   - `/api/market/*`

7. **Technical Analysis API** (`backend/routers/technical_analysis_api.py`)
   - `/api/technical/*`

8. **Real-Time Monitoring API** (`backend/routers/realtime_monitoring_api.py`) ⭐
   - `/api/monitoring/*` - **System Monitor endpoints**

---

## 🎨 Static Assets

### CSS Files

| File | Path | Used By |
|------|------|---------|
| Design System | `static/shared/css/design-system.css` | All pages |
| Global Styles | `static/shared/css/global.css` | All pages |
| Components | `static/shared/css/components.css` | All pages |
| Layout | `static/shared/css/layout.css` | All pages |
| Dashboard | `static/pages/dashboard/dashboard.css` | Dashboard page |
| **System Monitor** | `static/pages/system-monitor/system-monitor.css` | **System Monitor page** |

### JavaScript Files

| File | Path | Purpose |
|------|------|---------|
| Layout Manager | `static/shared/js/core/layout-manager.js` | Loads sidebar/header |
| API Client | `static/shared/js/core/api-client.js` | API communication |
| Models Client | `static/shared/js/core/models-client.js` | Models API client |
| **System Monitor** | `static/pages/system-monitor/system-monitor.js` | **System Monitor logic** |
| Crypto Icons | `static/assets/icons/crypto-icons.js` | SVG icons library |

---

## ⚙️ Backend Services

### Service Files

| Service | File Path | Used By |
|---------|-----------|---------|
| AI Models Monitor | `backend/services/ai_models_monitor.py` | System Monitor, Models API |
| Source Pool Manager | `monitoring/source_pool_manager.py` | System Monitor |
| Database Manager | `database/db_manager.py` | All services |
| Backtesting Service | `backend/services/backtesting_service.py` | Trading API |
| ML Training Service | `backend/services/ml_training_service.py` | AI API |

### Main Application File

| File | Path | Purpose |
|------|------|---------|
| FastAPI Server | `hf_unified_server.py` | Main application entry point |
| Server Runner | `main.py` | Start server with uvicorn |
| AI Models Registry | `ai_models.py` | Model management |

---

## 💾 Database Files

| Database | Path | Purpose |
|----------|------|---------|
| AI Models DB | `data/ai_models.db` | AI models monitoring data |
| Main Database | SQLite via `database/db_manager.py` | Providers, sources, pools |

### Database Models

| Model | File Path | Description |
|-------|-----------|-------------|
| Provider | `database/models.py` | Data provider information |
| SourcePool | `database/models.py` | Source pool management |
| PoolMember | `database/models.py` | Pool member details |

---

## 📁 Configuration Files

| File | Path | Purpose |
|------|------|---------|
| Environment | `.env` | Environment variables |
| Config | `config.py` | Application configuration |
| Requirements | `requirements.txt` | Python dependencies |
| Package | `package.json` | Node.js dependencies (if any) |

---

## 🎯 System Monitor Components

### Frontend Components

#### HTML Structure
```
static/pages/system-monitor/index.html
├── <head>
│   ├── Meta tags
│   ├── Theme CSS (design-system, global, components, layout)
│   └── System Monitor CSS
├── <body>
│   ├── app-container
│   │   ├── sidebar-container (injected by LayoutManager)
│   │   └── main-content
│   │       ├── header-container (injected by LayoutManager)
│   │       └── page-content
│   │           ├── page-header (title, status badge, refresh button)
│   │           ├── stats-grid (4 stat cards)
│   │           │   ├── Database Status Card
│   │           │   ├── AI Models Card
│   │           │   ├── Data Sources Card
│   │           │   └── Active Requests Card
│   │           └── network-section
│   │               ├── section-header (title + legend)
│   │               └── network-canvas-container
│   │                   └── #network-canvas
│   ├── connection-status (fixed bottom-right)
│   └── toast-container
└── <script>
    └── LayoutManager.init('system-monitor')
    └── SystemMonitor class initialization
```

#### JavaScript Class Structure
```
static/pages/system-monitor/system-monitor.js
└── SystemMonitor class
    ├── constructor()
    ├── init()
    ├── setupCanvas()
    ├── connectWebSocket() → /api/monitoring/ws
    ├── startPolling() → /api/monitoring/status
    ├── fetchSystemStatus()
    ├── updateSystemStatus(data)
    ├── updateHeader()
    ├── updateDatabaseStatus()
    ├── updateAIModels()
    ├── updateDataSources()
    ├── updateRequests()
    ├── updateNetworkNodes()
    ├── createPacket()
    ├── startAnimation()
    ├── draw() (canvas rendering)
    └── destroy()
```

#### CSS Structure
```
static/pages/system-monitor/system-monitor.css
├── Page Header Styles
├── Stats Grid Layout
├── Stat Cards
├── Status Indicators
├── Network Section
├── Canvas Container
├── Connection Status
└── Responsive Media Queries
```

### Backend Components

#### API Router
```
backend/routers/realtime_monitoring_api.py
├── Router: APIRouter(prefix="/api/monitoring")
├── Endpoints:
│   ├── GET /status → get_system_status()
│   ├── GET /sources/detailed → get_detailed_sources()
│   ├── GET /requests/recent → get_recent_requests()
│   ├── POST /requests/log → log_request()
│   └── WebSocket /ws → websocket_endpoint()
└── Dependencies:
    ├── ai_models_db (AI models database)
    ├── db_manager (Main database)
    └── SourcePoolManager (Source pool management)
```

#### Data Flow
```
Frontend (system-monitor.js)
    ↓
    ├─→ WebSocket: /api/monitoring/ws
    │   └─→ Real-time updates every 2 seconds
    │
    └─→ HTTP Polling: /api/monitoring/status
        └─→ Fallback if WebSocket fails
        
Backend (realtime_monitoring_api.py)
    ↓
    ├─→ AI Models Monitor Service
    │   └─→ Get models status, health, metrics
    │
    ├─→ Database Manager
    │   └─→ Get providers, sources, pools
    │
    └─→ Request Log (in-memory)
        └─→ Recent API requests tracking
```

---

## 🔄 Execution Flow

### Server Startup

1. **Entry Point**: `main.py`
   ```bash
   python main.py
   ```

2. **Server File**: `hf_unified_server.py`
   - Loads all routers
   - Includes `realtime_monitoring_router`
   - Sets up middleware
   - Starts uvicorn server on port 7860

3. **Routes Registered**:
   - All page routes (`/system-monitor`, `/dashboard`, etc.)
   - All API routes (`/api/*`)
   - WebSocket routes (`/api/monitoring/ws`)

### System Monitor Page Load

1. **User navigates to**: `http://localhost:7860/system-monitor`

2. **FastAPI serves**: `static/pages/system-monitor/index.html`

3. **HTML loads**:
   - LayoutManager initializes
   - Sidebar injected from `static/shared/layouts/sidebar.html`
   - Header injected
   - System Monitor CSS loaded

4. **JavaScript executes**:
   - `SystemMonitor` class instantiated
   - Canvas setup
   - WebSocket connection to `/api/monitoring/ws`
   - HTTP polling to `/api/monitoring/status` (every 2s)

5. **Data updates**:
   - Backend gathers status from:
     - AI Models Monitor DB
     - Main Database (providers, sources)
     - Request log
   - Returns JSON to frontend
   - Frontend updates UI and canvas animation

---

## 📂 Complete File Tree

```
crypto-dt-source-main/
├── hf_unified_server.py          → Main FastAPI application
├── main.py                        → Server entry point
├── ai_models.py                   → AI models registry
├── config.py                      → Configuration
├── requirements.txt               → Dependencies
│
├── static/
│   ├── pages/
│   │   ├── system-monitor/       ⭐ System Monitor
│   │   │   ├── index.html
│   │   │   ├── system-monitor.js
│   │   │   ├── system-monitor.css
│   │   │   └── README.md
│   │   ├── dashboard/
│   │   ├── market/
│   │   ├── models/
│   │   └── ... (other pages)
│   │
│   ├── shared/
│   │   ├── layouts/
│   │   │   ├── sidebar.html       → Includes System Monitor link
│   │   │   └── sidebar-modern.html
│   │   ├── js/
│   │   │   ├── core/
│   │   │   │   ├── layout-manager.js
│   │   │   │   ├── api-client.js
│   │   │   │   └── models-client.js
│   │   │   └── sidebar-manager.js
│   │   └── css/
│   │       ├── design-system.css
│   │       ├── global.css
│   │       ├── components.css
│   │       └── layout.css
│   │
│   └── assets/
│       └── icons/
│           └── crypto-icons.js
│
├── backend/
│   ├── routers/
│   │   ├── realtime_monitoring_api.py  ⭐ System Monitor API
│   │   ├── unified_service_api.py
│   │   ├── real_data_api.py
│   │   ├── direct_api.py
│   │   ├── ai_api.py
│   │   ├── market_api.py
│   │   └── ... (other routers)
│   │
│   └── services/
│       ├── ai_models_monitor.py   → Used by System Monitor
│       ├── backtesting_service.py
│       └── ml_training_service.py
│
├── database/
│   ├── db_manager.py             → Used by System Monitor
│   └── models.py                  → Provider, SourcePool, etc.
│
├── monitoring/
│   └── source_pool_manager.py    → Used by System Monitor
│
└── data/
    └── ai_models.db               → AI models monitoring database
```

---

## 🚀 Quick Reference

### Access System Monitor
- **URL**: `http://localhost:7860/system-monitor`
- **Route Handler**: `hf_unified_server.py:409` → `system_monitor_page()`
- **HTML File**: `static/pages/system-monitor/index.html`

### API Endpoints
- **Status**: `GET http://localhost:7860/api/monitoring/status`
- **WebSocket**: `WS ws://localhost:7860/api/monitoring/ws`
- **Recent Requests**: `GET http://localhost:7860/api/monitoring/requests/recent`

### Key Files
- **Frontend**: `static/pages/system-monitor/index.html`
- **JavaScript**: `static/pages/system-monitor/system-monitor.js`
- **CSS**: `static/pages/system-monitor/system-monitor.css`
- **Backend API**: `backend/routers/realtime_monitoring_api.py`
- **Sidebar**: `static/shared/layouts/sidebar.html` (line ~157)

---

## 📝 Notes

- All paths are relative to project root: `crypto-dt-source-main/`
- Server runs on port **7860** by default (configurable via `PORT` env var)
- System Monitor uses both WebSocket and HTTP polling for reliability
- Sidebar is injected by `LayoutManager` on page load
- Theme is applied via CSS variables defined in `design-system.css`

---

**Last Updated**: 2025-12-08  
**Version**: 2.0

