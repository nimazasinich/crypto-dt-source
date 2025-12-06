# System Architecture

## Overview

Crypto Monitor ULTIMATE is a multi-page web application built with FastAPI backend and vanilla JavaScript frontend. It provides real-time cryptocurrency monitoring, AI-powered analysis, and comprehensive market data.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                             │
├─────────────────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐        │
│  │ Dashboard │  │  Market   │  │  Models   │  │   News    │  ...   │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘        │
│        │              │              │              │               │
│  ┌─────┴──────────────┴──────────────┴──────────────┴───────┐      │
│  │              Shared JavaScript Modules                    │      │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │      │
│  │  │API Client│  │ Polling  │  │  Config  │  │  Layout  │  │      │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │      │
│  └───────────────────────────────────────────────────────────┘      │
└───────────────────────────────────────┬─────────────────────────────┘
                                        │ HTTP (Fetch API)
                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (Python)                        │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐     ┌─────────────────────┐                │
│  │   Page Routes       │     │    API Routes       │                │
│  │  GET /              │     │  GET /api/health    │                │
│  │  GET /market        │     │  GET /api/market    │                │
│  │  GET /models        │     │  GET /api/providers │                │
│  │  GET /news          │     │  POST /api/sentiment│                │
│  │  ...                │     │  ...                │                │
│  └─────────────────────┘     └──────────┬──────────┘                │
│                                         │                            │
│  ┌──────────────────────────────────────┴───────────────────────┐   │
│  │                     Core Services                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │   │
│  │  │ Database │  │HF Models │  │ Providers│  │  Cache   │      │   │
│  │  │ (SQLite) │  │(AI/ML)   │  │ (APIs)   │  │(In-mem)  │      │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │   │
│  └───────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      External Services                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │CoinGecko │  │ Binance  │  │HuggingFace│  │ News APIs│            │
│  │   API    │  │   API    │  │   Hub    │  │          │            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

## Frontend Architecture

### Page Structure
```
/static/pages/
├── dashboard/           - System overview & stats
├── market/              - Cryptocurrency prices & charts
├── models/              - AI model management
├── sentiment/           - Sentiment analysis tools
├── ai-analyst/          - AI trading advisor
├── trading-assistant/   - Trading signals
├── news/                - Crypto news feed
├── providers/           - API provider management
├── diagnostics/         - System health & logs
└── api-explorer/        - Interactive API testing
```

### Shared Components
```
/static/shared/
├── js/
│   ├── core/
│   │   ├── api-client.js      - HTTP API client (no WebSocket)
│   │   ├── polling-manager.js - Auto-refresh system
│   │   ├── config.js          - Central configuration
│   │   └── layout-manager.js  - Layout injection
│   ├── components/
│   │   ├── toast.js           - Notifications
│   │   ├── modal.js           - Modals
│   │   ├── loading.js         - Loading states
│   │   ├── chart.js           - Chart.js wrapper
│   │   └── icons.js           - SVG icon library
│   └── utils/
│       └── formatters.js      - Utility functions
├── css/
│   ├── design-system.css      - CSS variables & tokens
│   ├── global.css             - Base styles
│   ├── components.css         - Component styles
│   ├── layout.css             - Layout styles
│   └── utilities.css          - Utility classes
└── layouts/
    ├── header.html            - App header
    ├── sidebar.html           - Navigation sidebar
    └── footer.html            - Footer
```

## Backend Architecture

### FastAPI Structure
```
api_server_extended.py
├── Page Routes (/)
│   └── Serve static HTML from /static/pages/
│
├── API Routes (/api/*)
│   ├── Health & Status
│   │   ├── GET /api/health
│   │   └── GET /api/status
│   │
│   ├── Market Data
│   │   ├── GET /api/market
│   │   ├── GET /api/trending
│   │   └── GET /api/coins/top
│   │
│   ├── AI/ML Models
│   │   ├── GET /api/models/list
│   │   ├── GET /api/models/status
│   │   └── POST /api/sentiment/analyze
│   │
│   ├── News
│   │   ├── GET /api/news/latest
│   │   └── POST /api/news/summarize
│   │
│   ├── Providers
│   │   └── GET /api/providers
│   │
│   └── Logs
│       ├── GET /api/logs/recent
│       └── GET /api/logs/errors
│
└── Static Files (/static/*)
    └── Served via StaticFiles middleware
```

## Data Flow

### Page Load Flow
```
1. User navigates to page (e.g., /market)
2. FastAPI serves /static/pages/market/index.html
3. Browser loads CSS and JS modules
4. LayoutManager injects header/sidebar from /shared/layouts/
5. Page-specific JS fetches data from /api/*
6. Data rendered to DOM
7. Polling starts for auto-refresh (if enabled)
```

### API Call Flow
```
1. Page JS calls api.getMarket()
2. APIClient checks in-memory cache
3. If cached and fresh → return cached data
4. If not cached or expired → fetch from /api/market
5. Retry logic (3 attempts with 3s delay)
6. Response cached with TTL
7. Data returned to page JS
8. Page renders data
```

### Polling Flow
```
1. Page starts polling via pollingManager.start()
2. PollingManager sets interval timer
3. Every N seconds, callback executed
4. Callback fetches fresh data via API client
5. On success → update UI, reset error count
6. On error → log error, increment count
7. After 5 consecutive errors → stop polling
8. Page visibility change → pause/resume polling
9. Page unload → stop polling and cleanup
```

## Design Patterns

### Module Pattern
All JavaScript uses ES6 modules with explicit imports/exports for clear dependency management.

### Singleton Pattern
Core services (APIClient, PollingManager, LayoutManager) are singletons exported from their modules.

### Observer Pattern
PollingManager notifies subscribers on data updates via callback functions.

### Component Pattern
UI components (Toast, Modal) are reusable classes with consistent APIs.

## Security

### Frontend
- All user input escaped before rendering
- No `eval()` or `innerHTML` with raw data
- XSS protection via sanitization
- Content-Type headers enforced

### Backend
- CORS configured
- Input validation with Pydantic
- Rate limiting available
- No SQL injection (parameterized queries)

## Performance

### Caching Strategy
- **Client-side**: In-memory cache with 60s default TTL
- **HTTP**: Cache-Control headers for static files
- **API**: Response caching for slow-changing data

### Optimization Techniques
- CSS/JS code splitting (ES6 modules)
- Lazy loading (Chart.js loaded on demand)
- Gzip compression enabled
- Polling with visibility detection
- Exponential backoff on errors

### Polling Intervals
| Page | Interval | Reason |
|------|----------|--------|
| Dashboard | 30s | Real-time overview |
| Market | 30s | Price changes |
| News | 120s | Less frequent updates |
| Providers | 60s | Health monitoring |
| Others | Manual | On-demand data |

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements_hf.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["python", "app.py"]
```

### HuggingFace Space
- SDK: Docker
- Port: 7860
- Auto-deploy from GitHub
- Environment variables for configuration

## File Structure Summary

```
/workspace/
├── app.py                    - Application entry point
├── api_server_extended.py    - FastAPI server
├── static/
│   ├── pages/               - 10 page modules
│   ├── shared/              - Shared JS/CSS/layouts
│   ├── css/                 - Legacy CSS
│   └── js/                  - Legacy JS
├── templates/               - HTML templates
├── data/                    - Database files
├── logs/                    - Application logs
├── requirements_hf.txt      - Python dependencies
├── Dockerfile               - Container config
├── TESTING.md               - Test checklist
├── OPTIMIZATION.md          - Performance guide
├── ARCHITECTURE.md          - This file
└── DEVELOPMENT.md           - Developer guide
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML5, ES6 JavaScript, CSS3 |
| UI Components | Vanilla JS (no frameworks) |
| Charts | Chart.js 4.x |
| Backend | FastAPI (Python 3.11) |
| Database | SQLite |
| AI/ML | HuggingFace Transformers |
| Deployment | Docker, HuggingFace Spaces |
| Version Control | Git |

---

**Version**: 2.0.0  
**Last Updated**: 2025-01-15
