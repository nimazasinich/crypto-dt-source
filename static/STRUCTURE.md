# Static Folder Structure

## `/pages/`
Each subdirectory represents a standalone page with its own HTML, JS, and CSS.

- **dashboard/**: System overview, stats, resource categories
- **market/**: Market data table, trending coins, price charts
- **models/**: AI models list, status, statistics
- **sentiment/**: Multi-form sentiment analysis (global, asset, news, custom)
- **ai-analyst/**: AI trading advisor with decision support
- **trading-assistant/**: Trading signals and recommendations
- **news/**: News feed with filtering and AI summarization
- **providers/**: API provider management and health monitoring
- **diagnostics/**: System diagnostics, logs, health checks
- **api-explorer/**: Interactive API testing tool

## `/shared/`
Reusable code and assets shared across all pages.

### `/shared/js/core/`
Core application logic:
- `api-client.js`: HTTP client with caching (NO WebSocket)
- `polling-manager.js`: Auto-refresh system with smart pause/resume
- `config.js`: Central configuration (API endpoints, intervals, etc.)
- `layout-manager.js`: Injects shared layouts (header, sidebar, footer)

### `/shared/js/components/`
Reusable UI components:
- `toast.js`: Notification system
- `modal.js`: Modal dialogs
- `table.js`: Data tables with sort/filter
- `chart.js`: Chart.js wrapper
- `loading.js`: Loading states and skeletons

### `/shared/js/utils/`
Utility functions:
- `formatters.js`: Number, currency, date formatting
- `helpers.js`: DOM manipulation, validation, etc.

### `/shared/css/`
Global stylesheets:
- `design-system.css`: CSS variables, design tokens
- `global.css`: Base styles, resets, typography
- `components.css`: Reusable component styles
- `layout.css`: Header, sidebar, grid layouts
- `utilities.css`: Utility classes

### `/shared/layouts/`
HTML templates for shared UI:
- `header.html`: App header with logo, status, theme toggle
- `sidebar.html`: Navigation sidebar with page links
- `footer.html`: Footer content

## `/assets/`
Static assets:
- `/icons/`: SVG icons
- `/images/`: Images and graphics
