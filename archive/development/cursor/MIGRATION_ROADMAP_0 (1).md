# 🗺️ COMPLETE MIGRATION ROADMAP: Single-Page to Multi-Page Architecture

## 📌 PROJECT OVERVIEW

**Project Name**: Crypto Monitor ULTIMATE  
**Current State**: Monolithic single-page application (6000+ lines HTML, 27 JS files, 14 CSS files)  
**Target State**: Modular multi-page architecture with separated concerns  
**Environment**: Docker HuggingFace Space, FastAPI backend, Vanilla JavaScript frontend  
**Key Constraint**: NO WEBSOCKET - Use HTTP polling only

---

## 🎯 MIGRATION OBJECTIVES

1. ✅ Transform single HTML file into 10 separate page modules
2. ✅ Remove all WebSocket dependencies, implement polling system
3. ✅ Consolidate 27 JavaScript files into organized structure
4. ✅ Reorganize 14 CSS files into shared + page-specific
5. ✅ Create reusable component library
6. ✅ Update FastAPI backend for multi-page serving
7. ✅ Maintain all existing functionality
8. ✅ Improve performance and maintainability
9. ✅ Deploy to HuggingFace Space

---

## 📊 ARCHITECTURE COMPARISON

### BEFORE (Current State)
```
project/
├── main.py
├── static/
│   ├── index.html (6000+ lines - MONOLITHIC)
│   ├── js/ (27 files, 8500+ lines - COUPLED)
│   │   ├── app.js (2500+ lines)
│   │   ├── websocket-client.js ❌
│   │   ├── ws-client.js ❌
│   │   ├── wsClient.js ❌
│   │   └── [24 other files]
│   └── css/ (14 files, 4500+ lines - OVERLAPPING)
└── requirements.txt
```

### AFTER (Target State)
```
project/
├── main.py (UPDATED - multi-page routes)
├── static/
│   ├── pages/ (10 SEPARATE PAGES)
│   │   ├── dashboard/
│   │   │   ├── index.html
│   │   │   ├── dashboard.js
│   │   │   └── dashboard.css
│   │   ├── market/
│   │   ├── models/
│   │   ├── sentiment/
│   │   ├── ai-analyst/
│   │   ├── trading-assistant/
│   │   ├── news/
│   │   ├── providers/
│   │   ├── diagnostics/
│   │   └── api-explorer/
│   ├── shared/ (MODULAR ARCHITECTURE)
│   │   ├── js/
│   │   │   ├── core/
│   │   │   │   ├── api-client.js (NO WEBSOCKET)
│   │   │   │   ├── polling-manager.js (NEW)
│   │   │   │   ├── config.js (NEW)
│   │   │   │   └── layout-manager.js (NEW)
│   │   │   ├── components/
│   │   │   │   ├── toast.js
│   │   │   │   ├── modal.js
│   │   │   │   ├── table.js
│   │   │   │   ├── chart.js
│   │   │   │   └── loading.js
│   │   │   └── utils/
│   │   │       ├── formatters.js
│   │   │       └── helpers.js
│   │   ├── css/
│   │   │   ├── design-system.css
│   │   │   ├── global.css
│   │   │   ├── components.css
│   │   │   ├── layout.css
│   │   │   └── utilities.css
│   │   └── layouts/
│   │       ├── header.html
│   │       ├── sidebar.html
│   │       └── footer.html
│   └── assets/
├── requirements.txt
└── Dockerfile
```

---

# PHASE 1: INFRASTRUCTURE SETUP

## 🎯 PHASE 1.1: Create Base Folder Structure

**Objective**: Set up the complete folder hierarchy for the new architecture.

### Tasks:
1. Create all necessary directories
2. Add documentation files
3. Set up proper permissions

### Folder Structure to Create:

```bash
# Create main directories
mkdir -p static/pages/{dashboard,market,models,sentiment,ai-analyst,trading-assistant,news,providers,diagnostics,api-explorer}
mkdir -p static/shared/js/{core,components,utils}
mkdir -p static/shared/css
mkdir -p static/shared/layouts
mkdir -p static/assets/{icons,images}

# Add .gitkeep to preserve empty directories
find static -type d -empty -exec touch {}/.gitkeep \;
```

### Documentation File: `static/STRUCTURE.md`

Create this file to document folder purposes:

```markdown
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
```

### Success Criteria:
- ✅ All 10 page directories created in `/pages/`
- ✅ All shared subdirectories exist
- ✅ Documentation file `STRUCTURE.md` created
- ✅ No errors when listing directory tree

---

## 🎯 PHASE 1.2: Create Central Configuration

**Objective**: Define all configuration in one place for easy maintenance.

### File: `/static/shared/js/core/config.js`

```javascript
/**
 * Central Configuration for Crypto Monitor ULTIMATE
 * All constants, API endpoints, and settings in one place
 */

// ============================================================================
// API CONFIGURATION
// ============================================================================

export const CONFIG = {
  // Base API URL (relative to current origin)
  API_BASE_URL: window.location.origin + '/api',
  
  // Polling intervals (milliseconds)
  POLLING_INTERVALS: {
    dashboard: 30000,      // 30 seconds
    market: 30000,         // 30 seconds
    providers: 60000,      // 1 minute
    news: 120000,          // 2 minutes
    diagnostics: 0,        // Manual refresh only
  },
  
  // Cache configuration
  CACHE_TTL: 60000,        // Default cache TTL: 1 minute
  MAX_RETRIES: 3,          // Max retry attempts for failed requests
  RETRY_DELAY: 3000,       // Delay between retries (ms)
  
  // Pagination
  PAGINATION: {
    defaultLimit: 50,
    maxLimit: 100,
  },
  
  // Chart timeframes
  TIMEFRAMES: ['1D', '7D', '30D', '1Y'],
  
  // Theme options
  THEMES: {
    DARK: 'dark',
    LIGHT: 'light',
    SYSTEM: 'system',
  },
  
  // LocalStorage keys
  STORAGE_KEYS: {
    THEME: 'crypto_monitor_theme',
    PREFERENCES: 'crypto_monitor_preferences',
    CACHE_PREFIX: 'cm_cache_',
  },
  
  // Toast notification defaults
  TOAST: {
    DEFAULT_DURATION: 5000,
    ERROR_DURATION: 7000,
    MAX_VISIBLE: 5,
  },
};

// ============================================================================
// ROUTE DEFINITIONS
// ============================================================================

export const ROUTES = {
  DASHBOARD: '/',
  MARKET: '/market',
  MODELS: '/models',
  SENTIMENT: '/sentiment',
  AI_ANALYST: '/ai-analyst',
  TRADING: '/trading-assistant',
  NEWS: '/news',
  PROVIDERS: '/providers',
  DIAGNOSTICS: '/diagnostics',
  API_EXPLORER: '/api-explorer',
};

// ============================================================================
// API ENDPOINTS
// ============================================================================

export const API_ENDPOINTS = {
  // Health & Status
  HEALTH: '/health',
  STATUS: '/status',
  STATS: '/stats',
  
  // Market Data
  MARKET: '/market',
  TRENDING: '/trending',
  SENTIMENT: '/sentiment',
  DEFI: '/defi',
  COINS_TOP: '/coins/top',
  COIN_DETAILS: (symbol) => `/coins/${symbol}`,
  COIN_HISTORY: (symbol) => `/coins/${symbol}/history`,
  
  // Charts
  PRICE_CHART: (symbol) => `/charts/price/${symbol}`,
  ANALYZE_CHART: '/charts/analyze',
  
  // News
  NEWS_LATEST: '/news/latest',
  NEWS_ANALYZE: '/news/analyze',
  NEWS_SUMMARIZE: '/news/summarize',
  
  // AI/ML Models
  MODELS_LIST: '/models/list',
  MODELS_STATUS: '/models/status',
  MODELS_STATS: '/models/data/stats',
  MODELS_TEST: '/models/test',
  
  // Sentiment Analysis
  SENTIMENT_ANALYZE: '/sentiment/analyze',
  SENTIMENT_GLOBAL: '/sentiment/global',
  
  // AI Advisor
  AI_DECISION: '/ai/decision',
  AI_SIGNALS: '/ai/signals',
  
  // Datasets
  DATASETS_LIST: '/datasets/list',
  DATASET_PREVIEW: (name) => `/datasets/${name}/preview`,
  
  // Providers
  PROVIDERS: '/providers',
  PROVIDER_DETAILS: (id) => `/providers/${id}`,
  PROVIDER_HEALTH: (id) => `/providers/${id}/health-check`,
  PROVIDERS_CONFIG: '/providers/config',
  
  // Resources
  RESOURCES: '/resources',
  RESOURCES_DISCOVERY: '/resources/discovery/run',
  
  // Pools
  POOLS: '/pools',
  POOL_DETAILS: (id) => `/pools/${id}`,
  POOL_CREATE: '/pools',
  POOL_ROTATE: (id) => `/pools/${id}/rotate`,
  
  // Logs & Diagnostics
  LOGS: '/logs',
  LOGS_RECENT: '/logs/recent',
  LOGS_ERRORS: '/logs/errors',
  LOGS_CLEAR: '/logs',
  
  // HuggingFace Integration
  HF_HEALTH: '/hf/health',
  HF_RUN_SENTIMENT: '/hf/run-sentiment',
  
  // Feature Flags
  FEATURE_FLAGS: '/feature-flags',
  FEATURE_FLAG_UPDATE: (name) => `/feature-flags/${name}`,
  FEATURE_FLAGS_RESET: '/feature-flags/reset',
};

// ============================================================================
// PAGE METADATA
// ============================================================================

export const PAGE_METADATA = [
  {
    path: '/',
    page: 'dashboard',
    title: 'Dashboard | Crypto Monitor ULTIMATE',
    icon: '📊',
    description: 'System overview and statistics',
    polling: true,
    interval: 30000,
  },
  {
    path: '/market',
    page: 'market',
    title: 'Market | Crypto Monitor ULTIMATE',
    icon: '📈',
    description: 'Real-time market data and charts',
    polling: true,
    interval: 30000,
  },
  {
    path: '/models',
    page: 'models',
    title: 'AI Models | Crypto Monitor ULTIMATE',
    icon: '🤖',
    description: 'Machine learning models status',
    polling: false,
    interval: 0,
  },
  {
    path: '/sentiment',
    page: 'sentiment',
    title: 'Sentiment Analysis | Crypto Monitor ULTIMATE',
    icon: '💬',
    description: 'AI-powered sentiment analysis',
    polling: false,
    interval: 0,
  },
  {
    path: '/ai-analyst',
    page: 'ai-analyst',
    title: 'AI Analyst | Crypto Monitor ULTIMATE',
    icon: '🧠',
    description: 'AI trading advisor and decision support',
    polling: false,
    interval: 0,
  },
  {
    path: '/trading-assistant',
    page: 'trading-assistant',
    title: 'Trading Assistant | Crypto Monitor ULTIMATE',
    icon: '📊',
    description: 'Trading signals and recommendations',
    polling: false,
    interval: 0,
  },
  {
    path: '/news',
    page: 'news',
    title: 'News | Crypto Monitor ULTIMATE',
    icon: '📰',
    description: 'Curated cryptocurrency news',
    polling: true,
    interval: 120000,
  },
  {
    path: '/providers',
    page: 'providers',
    title: 'Providers | Crypto Monitor ULTIMATE',
    icon: '🔌',
    description: 'API provider management',
    polling: true,
    interval: 60000,
  },
  {
    path: '/diagnostics',
    page: 'diagnostics',
    title: 'Diagnostics | Crypto Monitor ULTIMATE',
    icon: '🔍',
    description: 'System diagnostics and logs',
    polling: false,
    interval: 0,
  },
  {
    path: '/api-explorer',
    page: 'api-explorer',
    title: 'API Explorer | Crypto Monitor ULTIMATE',
    icon: '🧪',
    description: 'Interactive API testing tool',
    polling: false,
    interval: 0,
  },
];

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get page metadata by path
 */
export function getPageMetadata(path) {
  return PAGE_METADATA.find(p => p.path === path) || PAGE_METADATA[0];
}

/**
 * Get polling interval for current page
 */
export function getPollingInterval(pageName) {
  const metadata = PAGE_METADATA.find(p => p.page === pageName);
  return metadata?.polling ? metadata.interval : 0;
}

/**
 * Build full API URL
 */
export function buildApiUrl(endpoint) {
  return `${CONFIG.API_BASE_URL}${endpoint}`;
}

/**
 * Get cache key for endpoint
 */
export function getCacheKey(endpoint) {
  return `${CONFIG.STORAGE_KEYS.CACHE_PREFIX}${endpoint}`;
}

// Export as default for convenience
export default {
  CONFIG,
  ROUTES,
  API_ENDPOINTS,
  PAGE_METADATA,
  getPageMetadata,
  getPollingInterval,
  buildApiUrl,
  getCacheKey,
};
```

### Success Criteria:
- ✅ `config.js` created with all constants
- ✅ ES6 module exports used
- ✅ All 10 pages defined in metadata
- ✅ All API endpoints mapped
- ✅ Helper functions included

---

## 🎯 PHASE 1.3: Create Shared Layout Components

**Objective**: Build reusable HTML templates for header, sidebar, and footer.

### File 1: `/static/shared/layouts/header.html`

```html
<header class="app-header" role="banner">
  <div class="header-left">
    <!-- Logo and Title -->
    <div class="logo-container">
      <div class="logo-icon">🚀</div>
      <div class="logo-text">
        <h1 class="app-title">Crypto Monitor</h1>
        <span class="app-subtitle">ULTIMATE</span>
      </div>
    </div>
  </div>

  <div class="header-center">
    <!-- API Status Badge -->
    <div class="status-badge" id="api-status-badge" data-status="checking">
      <span class="status-dot"></span>
      <span class="status-text">Checking...</span>
    </div>

    <!-- Live Indicator -->
    <div class="live-indicator" id="live-indicator">
      <span class="live-dot"></span>
      <span class="live-text">LIVE</span>
    </div>
  </div>

  <div class="header-right">
    <!-- Last Update Time -->
    <div class="last-update" id="header-last-update">
      <span class="update-icon">🕐</span>
      <span class="update-text">Just now</span>
    </div>

    <!-- Theme Toggle -->
    <button 
      class="btn-icon theme-toggle" 
      id="theme-toggle-btn" 
      aria-label="Toggle theme"
      title="Switch theme">
      <span class="theme-icon">🌙</span>
    </button>

    <!-- Settings Button -->
    <button 
      class="btn-icon" 
      id="settings-btn" 
      aria-label="Settings"
      title="Settings">
      <span class="icon">⚙️</span>
    </button>
  </div>
</header>
```

### File 2: `/static/shared/layouts/sidebar.html`

```html
<aside class="sidebar" role="navigation" aria-label="Main navigation">
  <!-- Mobile Toggle Button -->
  <button class="sidebar-toggle" id="sidebar-toggle" aria-label="Toggle sidebar">
    <span class="toggle-icon">☰</span>
  </button>

  <!-- Navigation Menu -->
  <nav class="nav-menu">
    <ul class="nav-list">
      <!-- Dashboard -->
      <li class="nav-item">
        <a href="/" class="nav-link" data-page="dashboard">
          <span class="nav-icon">📊</span>
          <span class="nav-label">Dashboard</span>
        </a>
      </li>

      <!-- Market -->
      <li class="nav-item">
        <a href="/market" class="nav-link" data-page="market">
          <span class="nav-icon">📈</span>
          <span class="nav-label">Market</span>
        </a>
      </li>

      <!-- AI Models -->
      <li class="nav-item">
        <a href="/models" class="nav-link" data-page="models">
          <span class="nav-icon">🤖</span>
          <span class="nav-label">AI Models</span>
        </a>
      </li>

      <!-- Sentiment -->
      <li class="nav-item">
        <a href="/sentiment" class="nav-link" data-page="sentiment">
          <span class="nav-icon">💬</span>
          <span class="nav-label">Sentiment</span>
        </a>
      </li>

      <!-- AI Analyst -->
      <li class="nav-item">
        <a href="/ai-analyst" class="nav-link" data-page="ai-analyst">
          <span class="nav-icon">🧠</span>
          <span class="nav-label">AI Analyst</span>
        </a>
      </li>

      <!-- Trading Assistant -->
      <li class="nav-item">
        <a href="/trading-assistant" class="nav-link" data-page="trading-assistant">
          <span class="nav-icon">💼</span>
          <span class="nav-label">Trading</span>
        </a>
      </li>

      <!-- News -->
      <li class="nav-item">
        <a href="/news" class="nav-link" data-page="news">
          <span class="nav-icon">📰</span>
          <span class="nav-label">News</span>
        </a>
      </li>

      <!-- Providers -->
      <li class="nav-item">
        <a href="/providers" class="nav-link" data-page="providers">
          <span class="nav-icon">🔌</span>
          <span class="nav-label">Providers</span>
        </a>
      </li>

      <!-- Diagnostics -->
      <li class="nav-item">
        <a href="/diagnostics" class="nav-link" data-page="diagnostics">
          <span class="nav-icon">🔍</span>
          <span class="nav-label">Diagnostics</span>
        </a>
      </li>

      <!-- API Explorer -->
      <li class="nav-item">
        <a href="/api-explorer" class="nav-link" data-page="api-explorer">
          <span class="nav-icon">🧪</span>
          <span class="nav-label">API Explorer</span>
        </a>
      </li>
    </ul>
  </nav>

  <!-- Sidebar Footer -->
  <div class="sidebar-footer">
    <div class="keyboard-hint">
      <kbd>Ctrl</kbd> + <kbd>K</kbd> for search
    </div>
  </div>
</aside>
```

### File 3: `/static/shared/layouts/footer.html`

```html
<footer class="app-footer" role="contentinfo">
  <div class="footer-content">
    <div class="footer-left">
      <p class="copyright">
        © 2025 Crypto Monitor ULTIMATE
      </p>
      <p class="version">
        Version 2.0.0
      </p>
    </div>

    <div class="footer-center">
      <nav class="footer-links">
        <a href="/api-explorer" class="footer-link">API Docs</a>
        <span class="separator">•</span>
        <a href="#" class="footer-link" id="help-link">Help</a>
        <span class="separator">•</span>
        <a href="#" class="footer-link" id="about-link">About</a>
      </nav>
    </div>

    <div class="footer-right">
      <p class="status-text">
        All systems operational
      </p>
    </div>
  </div>
</footer>
```

### File 4: `/static/shared/js/core/layout-manager.js`

```javascript
/**
 * Layout Manager
 * Handles injection and management of shared layout components
 */

import { PAGE_METADATA } from './config.js';

export class LayoutManager {
  static layoutsInjected = false;

  /**
   * Inject all layouts (header, sidebar, footer) into current page
   */
  static async injectLayouts() {
    if (this.layoutsInjected) {
      console.log('[LayoutManager] Layouts already injected');
      return;
    }

    try {
      // Inject sidebar
      await this.injectSidebar();

      // Inject header
      await this.injectHeader();

      // Inject footer (if container exists)
      const footerContainer = document.getElementById('footer-container');
      if (footerContainer) {
        await this.injectFooter();
      }

      // Setup event listeners
      this.setupEventListeners();

      // Mark as injected
      this.layoutsInjected = true;

      console.log('[LayoutManager] All layouts injected successfully');
    } catch (error) {
      console.error('[LayoutManager] Failed to inject layouts:', error);
      throw error;
    }
  }

  /**
   * Inject sidebar HTML
   */
  static async injectSidebar() {
    const container = document.getElementById('sidebar-container');
    if (!container) {
      console.warn('[LayoutManager] Sidebar container not found');
      return;
    }

    const response = await fetch('/static/shared/layouts/sidebar.html');
    const html = await response.text();
    container.innerHTML = html;
  }

  /**
   * Inject header HTML
   */
  static async injectHeader() {
    const container = document.getElementById('header-container');
    if (!container) {
      console.warn('[LayoutManager] Header container not found');
      return;
    }

    const response = await fetch('/static/shared/layouts/header.html');
    const html = await response.text();
    container.innerHTML = html;

    // Update API status
    this.updateApiStatus('checking');
  }

  /**
   * Inject footer HTML
   */
  static async injectFooter() {
    const container = document.getElementById('footer-container');
    if (!container) return;

    const response = await fetch('/static/shared/layouts/footer.html');
    const html = await response.text();
    container.innerHTML = html;
  }

  /**
   * Set active navigation item based on current page
   */
  static setActiveNav(pageName) {
    // Remove active class from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.remove('active');
    });

    // Add active class to current page
    const activeLink = document.querySelector(`.nav-link[data-page="${pageName}"]`);
    if (activeLink) {
      activeLink.classList.add('active');
      activeLink.setAttribute('aria-current', 'page');
    }

    // Update page title
    const metadata = PAGE_METADATA.find(p => p.page === pageName);
    if (metadata) {
      document.title = metadata.title;
    }
  }

  /**
   * Update API status badge in header
   */
  static updateApiStatus(status, message = '') {
    const badge = document.getElementById('api-status-badge');
    if (!badge) return;

    badge.setAttribute('data-status', status);

    const statusText = badge.querySelector('.status-text');
    if (statusText) {
      statusText.textContent = message || this.getStatusText(status);
    }
  }

  /**
   * Get status text for badge
   */
  static getStatusText(status) {
    const statusMap = {
      'online': '✅ System Active',
      'offline': '❌ Connection Failed',
      'checking': '⏳ Checking...',
      'degraded': '⚠️ Degraded',
    };
    return statusMap[status] || 'Unknown';
  }

  /**
   * Update last update timestamp in header
   */
  static updateLastUpdate(text) {
    const el = document.getElementById('header-last-update');
    if (!el) return;

    const textEl = el.querySelector('.update-text');
    if (textEl) {
      textEl.textContent = text;
    }
  }

  /**
   * Setup event listeners for layout interactions
   */
  static setupEventListeners() {
    // Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', () => {
        this.toggleSidebar();
      });
    }

    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle-btn');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        this.toggleTheme();
      });
    }

    // Close sidebar on mobile when clicking a link
    if (window.innerWidth <= 768) {
      document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
          this.closeSidebar();
        });
      });
    }
  }

  /**
   * Toggle sidebar visibility (mobile)
   */
  static toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      sidebar.classList.toggle('open');
    }
  }

  /**
   * Close sidebar (mobile)
   */
  static closeSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      sidebar.classList.remove('open');
    }
  }

  /**
   * Toggle theme (dark/light)
   */
  static toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('crypto_monitor_theme', newTheme);

    // Update icon
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
      themeIcon.textContent = newTheme === 'dark' ? '🌙' : '☀️';
    }

    console.log('[LayoutManager] Theme switched to:', newTheme);
  }

  /**
   * Initialize theme from localStorage
   */
  static initTheme() {
    const savedTheme = localStorage.getItem('crypto_monitor_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    // Update icon if header is loaded
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
      themeIcon.textContent = savedTheme === 'dark' ? '🌙' : '☀️';
    }
  }
}

// Initialize theme immediately
LayoutManager.initTheme();

export default LayoutManager;
```

### Success Criteria:
- ✅ All 3 HTML layout files created
- ✅ `layout-manager.js` created with injection logic
- ✅ Active navigation highlighting works
- ✅ Theme toggle functionality implemented
- ✅ Mobile sidebar toggle prepared

---

# PHASE 2: CORE JAVASCRIPT REFACTORING

## 🎯 PHASE 2.1: Create HTTP-Only API Client (NO WEBSOCKET)

**Objective**: Build a simple, robust API client using only HTTP fetch. Remove all WebSocket dependencies.

### File: `/static/shared/js/core/api-client.js`

```javascript
/**
 * API Client for Crypto Monitor ULTIMATE
 * 
 * Features:
 * - Pure HTTP/Fetch API (NO WEBSOCKET)
 * - Simple caching mechanism
 * - Automatic retry logic
 * - Request/error logging
 * - ES6 module exports
 */

import { CONFIG, API_ENDPOINTS, buildApiUrl, getCacheKey } from './config.js';

/**
 * Base API Client with caching and retry
 */
class APIClient {
  constructor(baseURL = CONFIG.API_BASE_URL) {
    this.baseURL = baseURL;
    this.cache = new Map();
    this.cacheTTL = CONFIG.CACHE_TTL;
    this.maxRetries = CONFIG.MAX_RETRIES;
    this.retryDelay = CONFIG.RETRY_DELAY;
    this.requestLog = [];
    this.errorLog = [];
    this.maxLogSize = 100;
  }

  /**
   * Core request method with retry logic
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const method = options.method || 'GET';
    const startTime = performance.now();

    // Check cache for GET requests
    if (method === 'GET' && !options.skipCache) {
      const cached = this._getFromCache(endpoint);
      if (cached) {
        console.log(`[APIClient] Cache hit: ${endpoint}`);
        return cached;
      }
    }

    // Retry logic
    let lastError;
    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      try {
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
          body: options.body ? JSON.stringify(options.body) : undefined,
          signal: options.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        const duration = performance.now() - startTime;

        // Cache successful GET responses
        if (method === 'GET') {
          this._saveToCache(endpoint, data);
        }

        // Log successful request
        this._logRequest({
          method,
          endpoint,
          status: response.status,
          duration: Math.round(duration),
          timestamp: Date.now(),
        });

        return data;

      } catch (error) {
        lastError = error;
        console.warn(`[APIClient] Attempt ${attempt}/${this.maxRetries} failed for ${endpoint}:`, error.message);

        if (attempt < this.maxRetries) {
          await this._sleep(this.retryDelay);
        }
      }
    }

    // All retries failed
    const duration = performance.now() - startTime;
    this._logError({
      method,
      endpoint,
      message: lastError.message,
      duration: Math.round(duration),
      timestamp: Date.now(),
    });

    throw new Error(`Failed after ${this.maxRetries} attempts: ${lastError.message}`);
  }

  /**
   * GET request
   */
  async get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }

  /**
   * POST request
   */
  async post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: data,
    });
  }

  /**
   * PUT request
   */
  async put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: data,
    });
  }

  /**
   * DELETE request
   */
  async delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }

  // ========================================================================
  // CACHE MANAGEMENT
  // ========================================================================

  /**
   * Get data from cache if not expired
   */
  _getFromCache(key) {
    const cacheKey = getCacheKey(key);
    const cached = this.cache.get(cacheKey);

    if (!cached) return null;

    const now = Date.now();
    if (now - cached.timestamp > this.cacheTTL) {
      this.cache.delete(cacheKey);
      return null;
    }

    return cached.data;
  }

  /**
   * Save data to cache with timestamp
   */
  _saveToCache(key, data) {
    const cacheKey = getCacheKey(key);
    this.cache.set(cacheKey, {
      data,
      timestamp: Date.now(),
    });
  }

  /**
   * Clear all cache
   */
  clearCache() {
    this.cache.clear();
    console.log('[APIClient] Cache cleared');
  }

  /**
   * Clear specific cache entry
   */
  clearCacheEntry(key) {
    const cacheKey = getCacheKey(key);
    this.cache.delete(cacheKey);
  }

  // ========================================================================
  // LOGGING
  // ========================================================================

  /**
   * Log successful request
   */
  _logRequest(entry) {
    this.requestLog.unshift(entry);
    if (this.requestLog.length > this.maxLogSize) {
      this.requestLog.pop();
    }
  }

  /**
   * Log error
   */
  _logError(entry) {
    this.errorLog.unshift(entry);
    if (this.errorLog.length > this.maxLogSize) {
      this.errorLog.pop();
    }
  }

  /**
   * Get request logs
   */
  getRequestLogs(limit = 20) {
    return this.requestLog.slice(0, limit);
  }

  /**
   * Get error logs
   */
  getErrorLogs(limit = 20) {
    return this.errorLog.slice(0, limit);
  }

  // ========================================================================
  // UTILITY
  // ========================================================================

  /**
   * Sleep utility for retry delays
   */
  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Crypto Monitor API Client with pre-configured endpoints
 */
export class CryptoMonitorAPI extends APIClient {
  // ========================================================================
  // HEALTH & STATUS
  // ========================================================================

  async getHealth() {
    return this.get(API_ENDPOINTS.HEALTH);
  }

  async getStatus() {
    return this.get(API_ENDPOINTS.STATUS);
  }

  async getStats() {
    return this.get(API_ENDPOINTS.STATS);
  }

  async getResources() {
    return this.get(API_ENDPOINTS.RESOURCES);
  }

  // ========================================================================
  // MARKET DATA
  // ========================================================================

  async getMarket() {
    return this.get(API_ENDPOINTS.MARKET);
  }

  async getTrending() {
    return this.get(API_ENDPOINTS.TRENDING);
  }

  async getSentiment() {
    return this.get(API_ENDPOINTS.SENTIMENT);
  }

  async getDefi() {
    return this.get(API_ENDPOINTS.DEFI);
  }

  async getTopCoins(limit = 50) {
    return this.get(`${API_ENDPOINTS.COINS_TOP}?limit=${limit}`);
  }

  async getCoinDetails(symbol) {
    return this.get(API_ENDPOINTS.COIN_DETAILS(symbol));
  }

  // ========================================================================
  // CHARTS
  // ========================================================================

  async getPriceChart(symbol, timeframe = '7D') {
    return this.get(`${API_ENDPOINTS.PRICE_CHART(symbol)}?timeframe=${timeframe}`);
  }

  async analyzeChart(symbol, timeframe, indicators) {
    return this.post(API_ENDPOINTS.ANALYZE_CHART, {
      symbol,
      timeframe,
      indicators,
    });
  }

  // ========================================================================
  // NEWS
  // ========================================================================

  async getLatestNews(limit = 40) {
    return this.get(`${API_ENDPOINTS.NEWS_LATEST}?limit=${limit}`);
  }

  async analyzeNews(title, content) {
    return this.post(API_ENDPOINTS.NEWS_ANALYZE, { title, content });
  }

  async summarizeNews(title, content) {
    return this.post(API_ENDPOINTS.NEWS_SUMMARIZE, { title, content });
  }

  // ========================================================================
  // AI/ML MODELS
  // ========================================================================

  async getModelsList() {
    return this.get(API_ENDPOINTS.MODELS_LIST);
  }

  async getModelsStatus() {
    return this.get(API_ENDPOINTS.MODELS_STATUS);
  }

  async getModelsStats() {
    return this.get(API_ENDPOINTS.MODELS_STATS);
  }

  async testModel(modelName, input) {
    return this.post(API_ENDPOINTS.MODELS_TEST, {
      model: modelName,
      input,
    });
  }

  // ========================================================================
  // SENTIMENT ANALYSIS
  // ========================================================================

  async analyzeSentiment(text, mode = 'crypto', model = null) {
    return this.post(API_ENDPOINTS.SENTIMENT_ANALYZE, {
      text,
      mode,
      model,
    });
  }

  async getGlobalSentiment() {
    return this.get(API_ENDPOINTS.SENTIMENT_GLOBAL);
  }

  // ========================================================================
  // AI ADVISOR
  // ========================================================================

  async getAIDecision(symbol, horizon, riskTolerance, context, model) {
    return this.post(API_ENDPOINTS.AI_DECISION, {
      symbol,
      horizon,
      risk_tolerance: riskTolerance,
      context,
      model,
    });
  }

  async getAISignals(symbol) {
    return this.get(`${API_ENDPOINTS.AI_SIGNALS}?symbol=${symbol}`);
  }

  // ========================================================================
  // DATASETS
  // ========================================================================

  async getDatasetsList() {
    return this.get(API_ENDPOINTS.DATASETS_LIST);
  }

  async previewDataset(name, limit = 10) {
    return this.get(`${API_ENDPOINTS.DATASET_PREVIEW(name)}?limit=${limit}`);
  }

  // ========================================================================
  // PROVIDERS
  // ========================================================================

  async getProviders() {
    return this.get(API_ENDPOINTS.PROVIDERS);
  }

  async getProviderDetails(id) {
    return this.get(API_ENDPOINTS.PROVIDER_DETAILS(id));
  }

  async checkProviderHealth(id) {
    return this.get(API_ENDPOINTS.PROVIDER_HEALTH(id));
  }

  async getProvidersConfig() {
    return this.get(API_ENDPOINTS.PROVIDERS_CONFIG);
  }

  // ========================================================================
  // LOGS & DIAGNOSTICS
  // ========================================================================

  async getLogs() {
    return this.get(API_ENDPOINTS.LOGS);
  }

  async getRecentLogs(limit = 50) {
    return this.get(`${API_ENDPOINTS.LOGS_RECENT}?limit=${limit}`);
  }

  async getErrorLogs(limit = 50) {
    return this.get(`${API_ENDPOINTS.LOGS_ERRORS}?limit=${limit}`);
  }

  async clearLogs() {
    return this.delete(API_ENDPOINTS.LOGS_CLEAR);
  }

  // ========================================================================
  // RESOURCES
  // ========================================================================

  async runResourceDiscovery() {
    return this.post(API_ENDPOINTS.RESOURCES_DISCOVERY);
  }

  // ========================================================================
  // HUGGINGFACE INTEGRATION
  // ========================================================================

  async getHFHealth() {
    return this.get(API_ENDPOINTS.HF_HEALTH);
  }

  async runHFSentiment(text) {
    return this.post(API_ENDPOINTS.HF_RUN_SENTIMENT, { text });
  }

  // ========================================================================
  // FEATURE FLAGS
  // ========================================================================

  async getFeatureFlags() {
    return this.get(API_ENDPOINTS.FEATURE_FLAGS);
  }

  async updateFeatureFlag(name, value) {
    return this.put(API_ENDPOINTS.FEATURE_FLAG_UPDATE(name), { value });
  }

  async resetFeatureFlags() {
    return this.post(API_ENDPOINTS.FEATURE_FLAGS_RESET);
  }
}

// ============================================================================
// EXPORT SINGLETON INSTANCE
// ============================================================================

export const api = new CryptoMonitorAPI();
export default api;

console.log('[APIClient] Initialized (HTTP-only, no WebSocket)');
```

### Success Criteria:
- ✅ `api-client.js` created with all endpoints
- ✅ NO WebSocket code anywhere
- ✅ Caching mechanism works
- ✅ Retry logic handles failures
- ✅ Logging tracks requests and errors
- ✅ Singleton instance exported

---

## 🎯 PHASE 2.2: Create Polling Manager

**Objective**: Build a polling system to replace WebSocket for auto-refresh functionality.

### File: `/static/shared/js/core/polling-manager.js`

```javascript
/**
 * Polling Manager
 * Replaces WebSocket with intelligent HTTP polling
 * 
 * Features:
 * - Multiple concurrent polls with different intervals
 * - Auto-pause when page is hidden (Page Visibility API)
 * - Manual start/stop control
 * - Last update timestamp tracking
 * - Error handling and retry
 */

export class PollingManager {
  constructor() {
    this.polls = new Map();
    this.lastUpdates = new Map();
    this.isVisible = !document.hidden;
    this.updateCallbacks = new Map();
    
    // Listen to page visibility changes
    document.addEventListener('visibilitychange', () => {
      this.isVisible = !document.hidden;
      console.log(`[PollingManager] Page visibility changed: ${this.isVisible ? 'visible' : 'hidden'}`);
      
      if (this.isVisible) {
        this.resumeAll();
      } else {
        this.pauseAll();
      }
    });

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
      this.stopAll();
    });

    console.log('[PollingManager] Initialized');
  }

  /**
   * Start polling an endpoint
   * @param {string} key - Unique identifier for this poll
   * @param {Function} fetchFunction - Async function that fetches data
   * @param {Function} callback - Function to call with fetched data
   * @param {number} interval - Polling interval in milliseconds
   */
  start(key, fetchFunction, callback, interval) {
    // Stop existing poll if any
    this.stop(key);

    const poll = {
      fetchFunction,
      callback,
      interval,
      timerId: null,
      isPaused: false,
      errorCount: 0,
      consecutiveErrors: 0,
      maxConsecutiveErrors: 5,
    };

    // Initial fetch (don't wait for interval)
    this._executePoll(key, poll);

    // Setup recurring interval
    poll.timerId = setInterval(() => {
      if (!poll.isPaused && this.isVisible) {
        this._executePoll(key, poll);
      }
    }, interval);

    this.polls.set(key, poll);
    console.log(`[PollingManager] Started polling: ${key} every ${interval}ms`);
  }

  /**
   * Execute a single poll
   */
  async _executePoll(key, poll) {
    try {
      console.log(`[PollingManager] Fetching: ${key}`);
      const data = await poll.fetchFunction();
      
      // Reset error count on success
      poll.consecutiveErrors = 0;
      
      // Update timestamp
      this.lastUpdates.set(key, Date.now());
      
      // Call success callback
      poll.callback(data, null);
      
      // Notify update callbacks
      this._notifyUpdateCallbacks(key);

    } catch (error) {
      poll.consecutiveErrors++;
      poll.errorCount++;
      
      console.error(`[PollingManager] Error in ${key} (${poll.consecutiveErrors}/${poll.maxConsecutiveErrors}):`, error);
      
      // Call error callback
      poll.callback(null, error);
      
      // Stop polling after too many consecutive errors
      if (poll.consecutiveErrors >= poll.maxConsecutiveErrors) {
        console.error(`[PollingManager] Too many consecutive errors, stopping ${key}`);
        this.stop(key);
      }
    }
  }

  /**
   * Stop polling for a specific key
   */
  stop(key) {
    const poll = this.polls.get(key);
    if (poll && poll.timerId) {
      clearInterval(poll.timerId);
      this.polls.delete(key);
      this.lastUpdates.delete(key);
      console.log(`[PollingManager] Stopped polling: ${key}`);
    }
  }

  /**
   * Pause a specific poll (keeps in memory, stops fetching)
   */
  pause(key) {
    const poll = this.polls.get(key);
    if (poll) {
      poll.isPaused = true;
      console.log(`[PollingManager] Paused: ${key}`);
    }
  }

  /**
   * Resume a specific poll
   */
  resume(key) {
    const poll = this.polls.get(key);
    if (poll) {
      poll.isPaused = false;
      // Immediate fetch on resume
      this._executePoll(key, poll);
      console.log(`[PollingManager] Resumed: ${key}`);
    }
  }

  /**
   * Pause all active polls (e.g., when page is hidden)
   */
  pauseAll() {
    console.log('[PollingManager] Pausing all polls');
    for (const [key, poll] of this.polls) {
      poll.isPaused = true;
    }
  }

  /**
   * Resume all paused polls (e.g., when page becomes visible)
   */
  resumeAll() {
    console.log('[PollingManager] Resuming all polls');
    for (const [key, poll] of this.polls) {
      if (poll.isPaused) {
        poll.isPaused = false;
        // Immediate fetch on resume
        this._executePoll(key, poll);
      }
    }
  }

  /**
   * Stop all polls and clear
   */
  stopAll() {
    console.log('[PollingManager] Stopping all polls');
    for (const key of this.polls.keys()) {
      this.stop(key);
    }
  }

  /**
   * Get last update timestamp for a poll
   */
  getLastUpdate(key) {
    return this.lastUpdates.get(key) || null;
  }

  /**
   * Get formatted "last updated" string
   */
  getLastUpdateText(key) {
    const timestamp = this.getLastUpdate(key);
    if (!timestamp) return 'Never';
    
    const seconds = Math.floor((Date.now() - timestamp) / 1000);
    
    if (seconds < 5) return 'Just now';
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  }

  /**
   * Check if a poll is active
   */
  isActive(key) {
    return this.polls.has(key);
  }

  /**
   * Check if a poll is paused
   */
  isPaused(key) {
    const poll = this.polls.get(key);
    return poll ? poll.isPaused : false;
  }

  /**
   * Get all active poll keys
   */
  getActivePolls() {
    return Array.from(this.polls.keys());
  }

  /**
   * Get poll info
   */
  getPollInfo(key) {
    const poll = this.polls.get(key);
    if (!poll) return null;

    return {
      key,
      interval: poll.interval,
      isPaused: poll.isPaused,
      errorCount: poll.errorCount,
      consecutiveErrors: poll.consecutiveErrors,
      lastUpdate: this.getLastUpdateText(key),
      isActive: true,
    };
  }

  /**
   * Register callback for last update changes
   * Returns unsubscribe function
   */
  onLastUpdate(callback) {
    const id = Date.now() + Math.random();
    this.updateCallbacks.set(id, callback);
    
    // Return unsubscribe function
    return () => this.updateCallbacks.delete(id);
  }

  /**
   * Notify all update callbacks
   */
  _notifyUpdateCallbacks(key) {
    const text = this.getLastUpdateText(key);
    for (const callback of this.updateCallbacks.values()) {
      try {
        callback(key, text);
      } catch (error) {
        console.error('[PollingManager] Error in update callback:', error);
      }
    }
  }

  /**
   * Update all UI elements showing "last updated"
   * Call this in an interval (e.g., every second)
   */
  updateAllLastUpdateTexts() {
    for (const key of this.polls.keys()) {
      this._notifyUpdateCallbacks(key);
    }
  }
}

// ============================================================================
// EXPORT SINGLETON INSTANCE
// ============================================================================

export const pollingManager = new PollingManager();

// Auto-update "last updated" text every second
setInterval(() => {
  pollingManager.updateAllLastUpdateTexts();
}, 1000);

export default pollingManager;
```

### Success Criteria:
- ✅ `polling-manager.js` created
- ✅ Multiple concurrent polls supported
- ✅ Page Visibility API integration works
- ✅ Last update tracking functional
- ✅ Error handling prevents infinite loops
- ✅ Singleton instance exported

---

## 🎯 PHASE 2.3: Extract Shared UI Components

**Objective**: Create reusable UI components (toast, modal, table, loading, chart).

### File 1: `/static/shared/js/components/toast.js`

```javascript
/**
 * Toast Notification System
 * Displays temporary notification messages
 */

import { CONFIG } from '../core/config.js';

export class Toast {
  static container = null;
  static toasts = [];
  static maxToasts = CONFIG.TOAST.MAX_VISIBLE;

  /**
   * Initialize toast container
   */
  static init() {
    if (this.container) return;

    this.container = document.getElementById('toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  }

  /**
   * Show a toast notification
   */
  static show(message, type = 'info', options = {}) {
    this.init();

    const toast = {
      id: Date.now() + Math.random(),
      message,
      type,
      duration: options.duration || (type === 'error' ? CONFIG.TOAST.ERROR_DURATION : CONFIG.TOAST.DEFAULT_DURATION),
      dismissible: options.dismissible !== false,
      action: options.action || null,
    };

    // Remove oldest toast if at max
    if (this.toasts.length >= this.maxToasts) {
      const oldest = this.toasts.shift();
      this.dismiss(oldest.id);
    }

    this.toasts.push(toast);
    this.render(toast);

    // Auto-dismiss
    if (toast.duration > 0) {
      setTimeout(() => this.dismiss(toast.id), toast.duration);
    }

    return toast.id;
  }

  /**
   * Render toast element
   */
  static render(toast) {
    const el = document.createElement('div');
    el.className = `toast toast-${toast.type}`;
    el.setAttribute('data-toast-id', toast.id);
    el.setAttribute('role', 'alert');
    el.setAttribute('aria-live', 'polite');

    const icon = this.getIcon(toast.type);

    el.innerHTML = `
      <div class="toast-icon">${icon}</div>
      <div class="toast-content">
        <div class="toast-message">${this.escapeHtml(toast.message)}</div>
        ${toast.action ? `<button class="toast-action">${toast.action.label}</button>` : ''}
      </div>
      ${toast.dismissible ? '<button class="toast-close" aria-label="Close">&times;</button>' : ''}
      ${toast.duration > 0 ? `<div class="toast-progress" style="animation-duration: ${toast.duration}ms"></div>` : ''}
    `;

    // Close button handler
    if (toast.dismissible) {
      const closeBtn = el.querySelector('.toast-close');
      closeBtn.addEventListener('click', () => this.dismiss(toast.id));
    }

    // Action button handler
    if (toast.action) {
      const actionBtn = el.querySelector('.toast-action');
      actionBtn.addEventListener('click', () => {
        toast.action.callback();
        this.dismiss(toast.id);
      });
    }

    this.container.appendChild(el);

    // Trigger animation
    setTimeout(() => el.classList.add('toast-show'), 10);
  }

  /**
   * Dismiss a toast
   */
  static dismiss(toastId) {
    const el = this.container.querySelector(`[data-toast-id="${toastId}"]`);
    if (!el) return;

    el.classList.remove('toast-show');
    el.classList.add('toast-hide');

    setTimeout(() => {
      if (el.parentNode) {
        el.parentNode.removeChild(el);
      }
    }, 300);

    // Remove from array
    this.toasts = this.toasts.filter(t => t.id !== toastId);
  }

  /**
   * Dismiss all toasts
   */
  static dismissAll() {
    this.toasts.forEach(toast => this.dismiss(toast.id));
  }

  /**
   * Convenience methods
   */
  static success(message, options = {}) {
    return this.show(message, 'success', options);
  }

  static error(message, options = {}) {
    return this.show(message, 'error', options);
  }

  static warning(message, options = {}) {
    return this.show(message, 'warning', options);
  }

  static info(message, options = {}) {
    return this.show(message, 'info', options);
  }

  /**
   * Get icon for toast type
   */
  static getIcon(type) {
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️',
    };
    return icons[type] || 'ℹ️';
  }

  /**
   * Escape HTML
   */
  static escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

export default Toast;
```

### File 2: `/static/shared/js/components/modal.js`

```javascript
/**
 * Modal Dialog Component
 */

export class Modal {
  constructor(options = {}) {
    this.id = options.id || `modal-${Date.now()}`;
    this.title = options.title || '';
    this.content = options.content || '';
    this.size = options.size || 'medium'; // small, medium, large
    this.closeOnBackdrop = options.closeOnBackdrop !== false;
    this.closeOnEscape = options.closeOnEscape !== false;
    this.onClose = options.onClose || null;
    this.element = null;
    this.backdrop = null;
  }

  /**
   * Show the modal
   */
  show() {
    if (this.element) {
      console.warn('[Modal] Modal already open');
      return;
    }

    // Create backdrop
    this.backdrop = document.createElement('div');
    this.backdrop.className = 'modal-backdrop';
    if (this.closeOnBackdrop) {
      this.backdrop.addEventListener('click', () => this.hide());
    }

    // Create modal
    this.element = document.createElement('div');
    this.element.className = `modal modal-${this.size}`;
    this.element.setAttribute('role', 'dialog');
    this.element.setAttribute('aria-modal', 'true');
    this.element.setAttribute('aria-labelledby', `${this.id}-title`);

    this.element.innerHTML = `
      <div class="modal-dialog">
        <div class="modal-header">
          <h2 class="modal-title" id="${this.id}-title">${this.escapeHtml(this.title)}</h2>
          <button class="modal-close" aria-label="Close modal">&times;</button>
        </div>
        <div class="modal-body">
          ${this.content}
        </div>
      </div>
    `;

    // Close button handler
    const closeBtn = this.element.querySelector('.modal-close');
    closeBtn.addEventListener('click', () => this.hide());

    // Escape key handler
    if (this.closeOnEscape) {
      this.escapeHandler = (e) => {
        if (e.key === 'Escape') this.hide();
      };
      document.addEventListener('keydown', this.escapeHandler);
    }

    // Append to body
    document.body.appendChild(this.backdrop);
    document.body.appendChild(this.element);

    // Trigger animation
    setTimeout(() => {
      this.backdrop.classList.add('show');
      this.element.classList.add('show');
    }, 10);

    // Prevent body scroll
    document.body.style.overflow = 'hidden';

    // Focus first focusable element
    this.trapFocus();
  }

  /**
   * Hide the modal
   */
  hide() {
    if (!this.element) return;

    // Remove animations
    this.backdrop.classList.remove('show');
    this.element.classList.remove('show');

    // Remove after animation
    setTimeout(() => {
      if (this.backdrop && this.backdrop.parentNode) {
        this.backdrop.parentNode.removeChild(this.backdrop);
      }
      if (this.element && this.element.parentNode) {
        this.element.parentNode.removeChild(this.element);
      }
      this.backdrop = null;
      this.element = null;

      // Restore body scroll
      document.body.style.overflow = '';

      // Remove escape handler
      if (this.escapeHandler) {
        document.removeEventListener('keydown', this.escapeHandler);
      }

      // Call onClose callback
      if (this.onClose) {
        this.onClose();
      }
    }, 300);
  }

  /**
   * Update modal content
   */
  setContent(html) {
    if (!this.element) return;
    const body = this.element.querySelector('.modal-body');
    if (body) {
      body.innerHTML = html;
    }
  }

  /**
   * Trap focus inside modal
   */
  trapFocus() {
    const focusable = this.element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusable.length === 0) return;

    const firstFocusable = focusable[0];
    const lastFocusable = focusable[focusable.length - 1];

    firstFocusable.focus();

    this.element.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey && document.activeElement === firstFocusable) {
          lastFocusable.focus();
          e.preventDefault();
        } else if (!e.shiftKey && document.activeElement === lastFocusable) {
          firstFocusable.focus();
          e.preventDefault();
        }
      }
    });
  }

  /**
   * Escape HTML
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Create confirmation dialog
   */
  static confirm(message, onConfirm, onCancel) {
    const modal = new Modal({
      title: 'Confirm',
      content: `
        <p>${message}</p>
        <div class="modal-actions">
          <button class="btn btn-secondary" id="modal-cancel">Cancel</button>
          <button class="btn btn-primary" id="modal-confirm">Confirm</button>
        </div>
      `,
      size: 'small',
    });

    modal.show();

    // Bind buttons
    setTimeout(() => {
      const confirmBtn = document.getElementById('modal-confirm');
      const cancelBtn = document.getElementById('modal-cancel');

      if (confirmBtn) {
        confirmBtn.addEventListener('click', () => {
          modal.hide();
          if (onConfirm) onConfirm();
        });
      }

      if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
          modal.hide();
          if (onCancel) onCancel();
        });
      }
    }, 50);

    return modal;
  }
}

export default Modal;
```

### File 3: `/static/shared/js/components/loading.js`

```javascript
/**
 * Loading States Component
 * Provides loading spinners and skeleton screens
 */

export class Loading {
  /**
   * Show loading spinner in container
   */
  static show(containerId, message = 'Loading...') {
    const container = document.getElementById(containerId);
    if (!container) {
      console.warn(`[Loading] Container not found: ${containerId}`);
      return;
    }

    const spinner = document.createElement('div');
    spinner.className = 'loading-container';
    spinner.innerHTML = `
      <div class="spinner"></div>
      <p class="loading-text">${message}</p>
    `;

    container.innerHTML = '';
    container.appendChild(spinner);
  }

  /**
   * Hide loading spinner
   */
  static hide(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const spinner = container.querySelector('.loading-container');
    if (spinner) {
      spinner.remove();
    }
  }

  /**
   * Generate skeleton rows for tables
   */
  static skeletonRows(count = 5, columns = 5) {
    let html = '';
    for (let i = 0; i < count; i++) {
      html += '<tr class="skeleton-row">';
      for (let j = 0; j < columns; j++) {
        html += '<td><div class="skeleton-box"></div></td>';
      }
      html += '</tr>';
    }
    return html;
  }

  /**
   * Generate skeleton cards
   */
  static skeletonCards(count = 4) {
    let html = '';
    for (let i = 0; i < count; i++) {
      html += `
        <div class="skeleton-card">
          <div class="skeleton-box skeleton-title"></div>
          <div class="skeleton-box skeleton-text"></div>
          <div class="skeleton-box skeleton-text"></div>
        </div>
      `;
    }
    return html;
  }

  /**
   * Add skeleton class to elements
   */
  static addSkeleton(selector) {
    document.querySelectorAll(selector).forEach(el => {
      el.classList.add('skeleton');
    });
  }

  /**
   * Remove skeleton class
   */
  static removeSkeleton(selector) {
    document.querySelectorAll(selector).forEach(el => {
      el.classList.remove('skeleton');
    });
  }
}

export default Loading;
```

### File 4: `/static/shared/js/components/chart.js`

```javascript
/**
 * Chart Component
 * Wrapper for Chart.js with common configurations
 */

// Chart.js will be loaded from CDN in pages that need it

export class ChartComponent {
  constructor(canvasId, type = 'line', options = {}) {
    this.canvasId = canvasId;
    this.canvas = document.getElementById(canvasId);
    this.type = type;
    this.options = options;
    this.chart = null;

    if (!this.canvas) {
      console.error(`[Chart] Canvas not found: ${canvasId}`);
    }
  }

  /**
   * Create chart with data
   */
  async create(data, customOptions = {}) {
    if (!this.canvas) return;

    // Ensure Chart.js is loaded
    if (typeof Chart === 'undefined') {
      console.error('[Chart] Chart.js not loaded');
      return;
    }

    // Destroy existing chart
    this.destroy();

    const config = {
      type: this.type,
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        ...this.getDefaultOptions(this.type),
        ...this.options,
        ...customOptions,
      },
    };

    this.chart = new Chart(this.canvas, config);
  }

  /**
   * Update chart data
   */
  update(data) {
    if (!this.chart) {
      console.warn('[Chart] Chart not initialized');
      return;
    }

    this.chart.data = data;
    this.chart.update();
  }

  /**
   * Destroy chart
   */
  destroy() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  }

  /**
   * Get default options by chart type
   */
  getDefaultOptions(type) {
    const common = {
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            color: 'var(--text-normal)',
            font: {
              family: 'var(--font-family-base)',
            },
          },
        },
        tooltip: {
          backgroundColor: 'var(--surface-glass)',
          titleColor: 'var(--text-strong)',
          bodyColor: 'var(--text-normal)',
          borderColor: 'var(--border-default)',
          borderWidth: 1,
        },
      },
    };

    const typeDefaults = {
      line: {
        scales: {
          x: {
            grid: {
              color: 'var(--border-subtle)',
            },
            ticks: {
              color: 'var(--text-soft)',
            },
          },
          y: {
            grid: {
              color: 'var(--border-subtle)',
            },
            ticks: {
              color: 'var(--text-soft)',
            },
          },
        },
      },
      bar: {
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              color: 'var(--text-soft)',
            },
          },
          y: {
            grid: {
              color: 'var(--border-subtle)',
            },
            ticks: {
              color: 'var(--text-soft)',
            },
          },
        },
      },
      doughnut: {
        plugins: {
          legend: {
            position: 'right',
          },
        },
      },
    };

    return {
      ...common,
      ...(typeDefaults[type] || {}),
    };
  }
}

/**
 * Load Chart.js from CDN if not already loaded
 */
export async function loadChartJS() {
  if (typeof Chart !== 'undefined') {
    return Promise.resolve();
  }

  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js';
    script.onload = () => {
      console.log('[Chart] Chart.js loaded from CDN');
      resolve();
    };
    script.onerror = () => {
      console.error('[Chart] Failed to load Chart.js');
      reject(new Error('Failed to load Chart.js'));
    };
    document.head.appendChild(script);
  });
}

export default ChartComponent;
```

### File 5: `/static/shared/js/utils/formatters.js`

```javascript
/**
 * Utility functions for formatting numbers, currency, dates, etc.
 */

/**
 * Format large numbers with suffixes (K, M, B, T)
 */
export function formatNumber(num, decimals = 2) {
  if (num === null || num === undefined) return '--';
  if (num === 0) return '0';

  const abs = Math.abs(num);
  
  if (abs >= 1e12) {
    return (num / 1e12).toFixed(decimals) + 'T';
  }
  if (abs >= 1e9) {
    return (num / 1e9).toFixed(decimals) + 'B';
  }
  if (abs >= 1e6) {
    return (num / 1e6).toFixed(decimals) + 'M';
  }
  if (abs >= 1e3) {
    return (num / 1e3).toFixed(decimals) + 'K';
  }
  
  return num.toFixed(decimals);
}

/**
 * Format currency (USD)
 */
export function formatCurrency(value, decimals = 2) {
  if (value === null || value === undefined) return '--';
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format percentage
 */
export function formatPercent(value, decimals = 2) {
  if (value === null || value === undefined) return '--';
  
  const sign = value >= 0 ? '+' : '';
  return sign + value.toFixed(decimals) + '%';
}

/**
 * Format date/time
 */
export function formatDate(timestamp, options = {}) {
  if (!timestamp) return '--';
  
  const date = new Date(timestamp);
  
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    ...options,
  }).format(date);
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(timestamp) {
  if (!timestamp) return '--';
  
  const now = Date.now();
  const diff = now - timestamp;
  const seconds = Math.floor(diff / 1000);
  
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

/**
 * Escape HTML to prevent XSS
 */
export function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text, maxLength = 50) {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

export default {
  formatNumber,
  formatCurrency,
  formatPercent,
  formatDate,
  formatRelativeTime,
  escapeHtml,
  truncate,
};
```

### Success Criteria:
- ✅ All 5 component files created
- ✅ Toast notification system works
- ✅ Modal dialogs function correctly
- ✅ Loading states display properly
- ✅ Chart wrapper ready for Chart.js
- ✅ Utility formatters implemented

---

# PHASE 3: CSS REORGANIZATION

## 🎯 PHASE 3.1: Consolidate Core CSS Files

**Objective**: Reorganize 14 CSS files into a clean, maintainable structure.

### Task 1: Keep Design System As-Is

**File**: `/static/shared/css/design-system.css`

This file (364 lines) is already well-structured with CSS variables. **Do not modify it.** It contains:
- Color tokens
- Typography scale
- Spacing system
- Shadows and effects
- Z-index scale
- Breakpoints

### Task 2: Create Global CSS

**File**: `/static/shared/css/global.css`

Consolidate these existing files:
- `base.css` (300 lines)
- Parts of `main.css` (1025 lines - extract only global styles)
- `accessibility.css` (150 lines)

```css
/**
 * Global Styles
 * Base styles, resets, typography, and accessibility
 */

/* ============================================================================
   CSS RESET
   ============================================================================ */

*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
  color: var(--text-normal);
  background: var(--bg-primary);
  overflow-x: hidden;
}

/* ============================================================================
   TYPOGRAPHY
   ============================================================================ */

h1, h2, h3, h4, h5, h6 {
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-tight);
  color: var(--text-strong);
  margin-bottom: var(--space-4);
}

h1 { font-size: var(--font-size-3xl); }
h2 { font-size: var(--font-size-2xl); }
h3 { font-size: var(--font-size-xl); }
h4 { font-size: var(--font-size-lg); }
h5 { font-size: var(--font-size-base); }
h6 { font-size: var(--font-size-sm); }

p {
  margin-bottom: var(--space-4);
}

a {
  color: var(--color-primary);
  text-decoration: none;
  transition: color 0.2s;
}

a:hover {
  color: var(--color-primary-light);
  text-decoration: underline;
}

code, pre {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
}

pre {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  overflow-x: auto;
}

/* ============================================================================
   LAYOUT
   ============================================================================ */

.app-container {
  display: flex;
  min-height: 100vh;
  background: var(--bg-primary);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: var(--sidebar-width, 250px);
}

.page-content {
  flex: 1;
  padding: var(--space-6);
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* ============================================================================
   SCROLLBAR
   ============================================================================ */

::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--border-strong);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

/* ============================================================================
   ACCESSIBILITY
   ============================================================================ */

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.using-mouse :focus-visible {
  outline: none;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* ============================================================================
   LIGHT THEME OVERRIDES
   ============================================================================ */

[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --text-strong: #1a1a1a;
  --text-normal: #333333;
  --text-soft: #666666;
  --text-muted: #999999;
  --border-subtle: #e5e5e5;
  --border-default: #d4d4d4;
}

/* ============================================================================
   RESPONSIVE
   ============================================================================ */

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }

  .page-content {
    padding: var(--space-4);
  }
}
```

### Task 3: Create Components CSS

**File**: `/static/shared/css/components.css`

Consolidate:
- `components.css` (400 lines)
- `enterprise-components.css` (350 lines)
- `toast.css` (100 lines)
- Modal styles
- Button styles
- Card styles
- Form styles
- Table styles

```css
/**
 * Reusable UI Components
 * Buttons, cards, forms, tables, modals, toasts, etc.
 */

/* ============================================================================
   BUTTONS
   ============================================================================ */

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  line-height: 1;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-light);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-strong);
  border: 1px solid var(--border-default);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-tertiary);
}

.btn-icon {
  padding: var(--space-2);
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-normal);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: var(--bg-secondary);
  border-color: var(--border-default);
}

/* ============================================================================
   CARDS
   ============================================================================ */

.card {
  background: var(--surface-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-strong);
  margin: 0;
}

.card-body {
  color: var(--text-normal);
}

/* ============================================================================
   BADGES
   ============================================================================ */

.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-full);
  line-height: 1;
}

.badge-success {
  background: var(--color-success);
  color: white;
}

.badge-error {
  background: var(--color-danger);
  color: white;
}

.badge-warning {
  background: var(--color-warning);
  color: white;
}

.badge-info {
  background: var(--color-info);
  color: white;
}

/* ============================================================================
   FORMS
   ============================================================================ */

.form-group {
  margin-bottom: var(--space-5);
}

.form-label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-strong);
  margin-bottom: var(--space-2);
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: var(--space-3);
  font-size: var(--font-size-base);
  font-family: inherit;
  color: var(--text-strong);
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  transition: all 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-alpha);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

/* ============================================================================
   TABLES
   ============================================================================ */

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--surface-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.data-table thead {
  background: var(--bg-secondary);
}

.data-table th {
  padding: var(--space-4);
  text-align: left;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-strong);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border-default);
}

.data-table td {
  padding: var(--space-4);
  color: var(--text-normal);
  border-bottom: 1px solid var(--border-subtle);
}

.data-table tbody tr {
  transition: background 0.2s;
  cursor: pointer;
}

.data-table tbody tr:hover {
  background: var(--bg-secondary);
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

/* ============================================================================
   MODALS
   ============================================================================ */

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: var(--z-modal-backdrop);
  opacity: 0;
  transition: opacity 0.3s;
}

.modal-backdrop.show {
  opacity: 1;
}

.modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0.9);
  z-index: var(--z-modal);
  opacity: 0;
  transition: all 0.3s;
}

.modal.show {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1);
}

.modal-dialog {
  background: var(--surface-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-2xl);
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
}

.modal-small .modal-dialog { width: 400px; }
.modal-medium .modal-dialog { width: 600px; }
.modal-large .modal-dialog { width: 900px; }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-5);
  border-bottom: 1px solid var(--border-subtle);
}

.modal-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-strong);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: var(--font-size-2xl);
  color: var(--text-muted);
  cursor: pointer;
  line-height: 1;
  transition: color 0.2s;
}

.modal-close:hover {
  color: var(--text-strong);
}

.modal-body {
  padding: var(--space-6);
}

/* ============================================================================
   TOASTS
   ============================================================================ */

.toast-container {
  position: fixed;
  bottom: var(--space-6);
  right: var(--space-6);
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 300px;
  max-width: 500px;
  padding: var(--space-4);
  background: var(--surface-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  pointer-events: all;
  opacity: 0;
  transform: translateX(100%);
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.toast.toast-show {
  opacity: 1;
  transform: translateX(0);
}

.toast.toast-hide {
  opacity: 0;
  transform: translateX(100%);
}

.toast-success { border-left: 4px solid var(--color-success); }
.toast-error { border-left: 4px solid var(--color-danger); }
.toast-warning { border-left: 4px solid var(--color-warning); }
.toast-info { border-left: 4px solid var(--color-info); }

.toast-icon {
  font-size: var(--font-size-xl);
  flex-shrink: 0;
}

.toast-content {
  flex: 1;
}

.toast-message {
  font-size: var(--font-size-sm);
  color: var(--text-strong);
}

.toast-close {
  background: none;
  border: none;
  font-size: var(--font-size-xl);
  color: var(--text-muted);
  cursor: pointer;
  line-height: 1;
  padding: 0;
  margin-left: var(--space-2);
}

.toast-close:hover {
  color: var(--text-strong);
}

.toast-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: var(--color-primary);
  animation: toast-progress linear forwards;
}

@keyframes toast-progress {
  from { width: 100%; }
  to { width: 0%; }
}

/* ============================================================================
   LOADING
   ============================================================================ */

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-subtle);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: var(--space-4);
  font-size: var(--font-size-sm);
  color: var(--text-muted);
}

.skeleton {
  pointer-events: none;
}

.skeleton-box {
  background: linear-gradient(
    90deg,
    var(--border-subtle) 25%,
    var(--border-default) 50%,
    var(--border-subtle) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
  height: 1em;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* ============================================================================
   RESPONSIVE
   ============================================================================ */

@media (max-width: 768px) {
  .modal-dialog {
    width: 95vw !important;
  }

  .toast-container {
    left: var(--space-3);
    right: var(--space-3);
    bottom: var(--space-3);
  }

  .toast {
    min-width: auto;
    width: 100%;
  }
}
```

### Task 4: Create Layout CSS

**File**: `/static/shared/css/layout.css`

Extract from `main.css` and `navigation.css`:

```css
/**
 * Layout Styles
 * Header, sidebar, footer, navigation
 */

/* ============================================================================
   HEADER
   ============================================================================ */

.app-header {
  position: sticky;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-6);
  background: var(--surface-glass);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-subtle);
  z-index: var(--z-header);
}

.header-left,
.header-center,
.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.logo-icon {
  font-size: var(--font-size-2xl);
}

.app-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--text-strong);
  margin: 0;
}

.app-subtitle {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-muted);
}

[data-status="online"] .status-dot {
  background: var(--color-success);
  animation: pulse 2s infinite;
}

[data-status="offline"] .status-dot {
  background: var(--color-danger);
}

[data-status="checking"] .status-dot {
  background: var(--color-warning);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-danger);
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.last-update {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  color: var(--text-soft);
}

/* ============================================================================
   SIDEBAR
   ============================================================================ */

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: var(--sidebar-width, 250px);
  height: 100vh;
  background: var(--surface-glass);
  backdrop-filter: blur(10px);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  z-index: var(--z-sidebar);
  transition: transform 0.3s;
}

.sidebar-toggle {
  display: none;
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  background: none;
  border: none;
  font-size: var(--font-size-xl);
  color: var(--text-normal);
  cursor: pointer;
}

.nav-menu {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
}

.nav-list {
  list-style: none;
}

.nav-item {
  margin-bottom: var(--space-2);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-base);
  color: var(--text-normal);
  border-radius: var(--radius-md);
  transition: all 0.2s;
  text-decoration: none;
}

.nav-link:hover {
  background: var(--bg-secondary);
  color: var(--text-strong);
  text-decoration: none;
}

.nav-link.active {
  background: var(--color-primary);
  color: white;
}

.nav-icon {
  font-size: var(--font-size-lg);
}

.nav-label {
  flex: 1;
}

.sidebar-footer {
  padding: var(--space-4);
  border-top: 1px solid var(--border-subtle);
}

.keyboard-hint {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  text-align: center;
}

.keyboard-hint kbd {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
}

/* ============================================================================
   PAGE LAYOUT
   ============================================================================ */

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
  flex-wrap: wrap;
  gap: var(--space-4);
}

.page-title h1 {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-strong);
  margin: 0;
}

.page-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  margin-top: var(--space-2);
}

.page-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

/* ============================================================================
   RESPONSIVE
   ============================================================================ */

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-toggle {
    display: block;
  }

  .app-header {
    padding: var(--space-3) var(--space-4);
  }

  .header-left .logo-text {
    display: none;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
```

### Task 5: Create Utilities CSS

**File**: `/static/shared/css/utilities.css`

```css
/**
 * Utility Classes
 * Helper classes for common styling needs
 */

/* ============================================================================
   DISPLAY
   ============================================================================ */

.hidden { display: none !important; }
.block { display: block !important; }
.inline-block { display: inline-block !important; }
.flex { display: flex !important; }
.inline-flex { display: inline-flex !important; }
.grid { display: grid !important; }

/* ============================================================================
   FLEX UTILITIES
   ============================================================================ */

.flex-row { flex-direction: row !important; }
.flex-col { flex-direction: column !important; }
.flex-wrap { flex-wrap: wrap !important; }
.flex-nowrap { flex-wrap: nowrap !important; }
.justify-start { justify-content: flex-start !important; }
.justify-center { justify-content: center !important; }
.justify-end { justify-content: flex-end !important; }
.justify-between { justify-content: space-between !important; }
.items-start { align-items: flex-start !important; }
.items-center { align-items: center !important; }
.items-end { align-items: flex-end !important; }
.gap-1 { gap: var(--space-1) !important; }
.gap-2 { gap: var(--space-2) !important; }
.gap-3 { gap: var(--space-3) !important; }
.gap-4 { gap: var(--space-4) !important; }
.gap-6 { gap: var(--space-6) !important; }

/* ============================================================================
   SPACING
   ============================================================================ */

.m-0 { margin: 0 !important; }
.m-1 { margin: var(--space-1) !important; }
.m-2 { margin: var(--space-2) !important; }
.m-3 { margin: var(--space-3) !important; }
.m-4 { margin: var(--space-4) !important; }
.m-6 { margin: var(--space-6) !important; }
.m-8 { margin: var(--space-8) !important; }

.mt-0 { margin-top: 0 !important; }
.mt-2 { margin-top: var(--space-2) !important; }
.mt-4 { margin-top: var(--space-4) !important; }
.mt-6 { margin-top: var(--space-6) !important; }

.mb-0 { margin-bottom: 0 !important; }
.mb-2 { margin-bottom: var(--space-2) !important; }
.mb-4 { margin-bottom: var(--space-4) !important; }
.mb-6 { margin-bottom: var(--space-6) !important; }

.p-0 { padding: 0 !important; }
.p-2 { padding: var(--space-2) !important; }
.p-4 { padding: var(--space-4) !important; }
.p-6 { padding: var(--space-6) !important; }

/* ============================================================================
   TEXT
   ============================================================================ */

.text-left { text-align: left !important; }
.text-center { text-align: center !important; }
.text-right { text-align: right !important; }

.text-xs { font-size: var(--font-size-xs) !important; }
.text-sm { font-size: var(--font-size-sm) !important; }
.text-base { font-size: var(--font-size-base) !important; }
.text-lg { font-size: var(--font-size-lg) !important; }
.text-xl { font-size: var(--font-size-xl) !important; }

.font-normal { font-weight: var(--font-weight-normal) !important; }
.font-medium { font-weight: var(--font-weight-medium) !important; }
.font-semibold { font-weight: var(--font-weight-semibold) !important; }
.font-bold { font-weight: var(--font-weight-bold) !important; }

.text-strong { color: var(--text-strong) !important; }
.text-normal { color: var(--text-normal) !important; }
.text-soft { color: var(--text-soft) !important; }
.text-muted { color: var(--text-muted) !important; }

.uppercase { text-transform: uppercase !important; }
.lowercase { text-transform: lowercase !important; }
.capitalize { text-transform: capitalize !important; }

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ============================================================================
   COLORS
   ============================================================================ */

.bg-primary { background-color: var(--bg-primary) !important; }
.bg-secondary { background-color: var(--bg-secondary) !important; }

.text-success { color: var(--color-success) !important; }
.text-error { color: var(--color-danger) !important; }
.text-warning { color: var(--color-warning) !important; }
.text-info { color: var(--color-info) !important; }

.bg-success { background-color: var(--color-success) !important; }
.bg-error { background-color: var(--color-danger) !important; }
.bg-warning { background-color: var(--color-warning) !important; }
.bg-info { background-color: var(--color-info) !important; }

/* ============================================================================
   BORDERS
   ============================================================================ */

.border { border: 1px solid var(--border-default) !important; }
.border-top { border-top: 1px solid var(--border-default) !important; }
.border-bottom { border-bottom: 1px solid var(--border-default) !important; }

.rounded-none { border-radius: 0 !important; }
.rounded-sm { border-radius: var(--radius-sm) !important; }
.rounded { border-radius: var(--radius-md) !important; }
.rounded-lg { border-radius: var(--radius-lg) !important; }
.rounded-full { border-radius: var(--radius-full) !important; }

/* ============================================================================
   EFFECTS
   ============================================================================ */

.shadow-sm { box-shadow: var(--shadow-sm) !important; }
.shadow { box-shadow: var(--shadow-md) !important; }
.shadow-lg { box-shadow: var(--shadow-lg) !important; }

.opacity-0 { opacity: 0 !important; }
.opacity-50 { opacity: 0.5 !important; }
.opacity-100 { opacity: 1 !important; }

/* ============================================================================
   POSITIONING
   ============================================================================ */

.relative { position: relative !important; }
.absolute { position: absolute !important; }
.fixed { position: fixed !important; }
.sticky { position: sticky !important; }

/* ============================================================================
   RESPONSIVE UTILITIES
   ============================================================================ */

@media (max-width: 768px) {
  .hidden-mobile { display: none !important; }
}

@media (min-width: 769px) {
  .hidden-desktop { display: none !important; }
}
```

### Success Criteria:
- ✅ `design-system.css` kept as-is
- ✅ `global.css` created (consolidating 3 files)
- ✅ `components.css` created (consolidating 4 files)
- ✅ `layout.css` created
- ✅ `utilities.css` created
- ✅ No duplicate styles
- ✅ All WebSocket-related CSS removed (`connection-status.css`)

---

# PHASE 4: BUILD FIRST COMPLETE PAGE (DASHBOARD)

## 🎯 PHASE 4.1: Create Complete Dashboard Page

**Objective**: Build a fully functional Dashboard page as a template for all other pages.

This page will demonstrate:
- Proper HTML structure
- JavaScript with API calls and polling
- Page-specific CSS
- Integration with all shared components

### File 1: `/static/pages/dashboard/index.html`

```html
<!DOCTYPE html>
<html lang="en" dir="ltr" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Crypto Monitor ULTIMATE - System Dashboard">
  <title>Dashboard | Crypto Monitor ULTIMATE</title>
  
  <!-- Favicon -->
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🚀</text></svg>">
  
  <!-- Shared CSS (in order) -->
  <link rel="stylesheet" href="/static/shared/css/design-system.css">
  <link rel="stylesheet" href="/static/shared/css/global.css">
  <link rel="stylesheet" href="/static/shared/css/components.css">
  <link rel="stylesheet" href="/static/shared/css/layout.css">
  <link rel="stylesheet" href="/static/shared/css/utilities.css">
  
  <!-- Page-specific CSS -->
  <link rel="stylesheet" href="./dashboard.css">
  
  <!-- Preload Chart.js (will be loaded by JS when needed) -->
  <link rel="preload" as="script" href="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js">
</head>
<body>
  <div class="app-container">
    <!-- Sidebar Navigation (injected by LayoutManager) -->
    <aside id="sidebar-container"></aside>
    
    <!-- Main Content Area -->
    <main class="main-content">
      <!-- Header (injected by LayoutManager) -->
      <header id="header-container"></header>
      
      <!-- Dashboard Content -->
      <div class="page-content">
        <!-- Page Header -->
        <div class="page-header">
          <div class="page-title">
            <h1>📊 Dashboard</h1>
            <p class="page-subtitle">System Overview & Statistics</p>
          </div>
          <div class="page-actions">
            <button id="refresh-btn" class="btn-icon" title="Refresh data" aria-label="Refresh data">
              <span class="icon">↻</span>
            </button>
            <span id="last-update" class="last-update" aria-live="polite">Loading...</span>
          </div>
        </div>

        <!-- Stats Grid (4 cards) -->
        <div class="stats-grid" id="stats-grid">
          <!-- Loading skeletons (will be replaced by actual data) -->
          <div class="stat-card skeleton">
            <div class="stat-icon">📦</div>
            <div class="stat-content">
              <div class="stat-value">--</div>
              <div class="stat-label">Total Resources</div>
            </div>
          </div>
          <div class="stat-card skeleton">
            <div class="stat-icon">🆓</div>
            <div class="stat-content">
              <div class="stat-value">--</div>
              <div class="stat-label">Free Resources</div>
            </div>
          </div>
          <div class="stat-card skeleton">
            <div class="stat-icon">🤖</div>
            <div class="stat-content">
              <div class="stat-value">--</div>
              <div class="stat-label">AI Models</div>
            </div>
          </div>
          <div class="stat-card skeleton">
            <div class="stat-icon">🔌</div>
            <div class="stat-content">
              <div class="stat-value">--</div>
              <div class="stat-label">Active Providers</div>
            </div>
          </div>
        </div>

        <!-- System Status Alert -->
        <div id="system-alert" class="alert-container" role="region" aria-label="System status"></div>

        <!-- Categories Chart -->
        <div class="chart-container">
          <div class="chart-header">
            <h2>Resources by Category</h2>
          </div>
          <div class="chart-body">
            <canvas id="categories-chart" width="800" height="400" aria-label="Resources by category chart"></canvas>
          </div>
        </div>
      </div>
    </main>
  </div>

  <!-- Toast Container (managed by Toast component) -->
  <div id="toast-container" aria-live="polite" aria-atomic="true"></div>

  <!-- Load page script as ES6 module -->
  <script type="module" src="./dashboard.js"></script>
</body>
</html>
```

### File 2: `/static/pages/dashboard/dashboard.js`

```javascript
/**
 * Dashboard Page Controller
 * Displays system overview, stats, and resource categories
 */

import { api } from '../../shared/js/core/api-client.js';
import { pollingManager } from '../../shared/js/core/polling-manager.js';
import { LayoutManager } from '../../shared/js/core/layout-manager.js';
import { Toast } from '../../shared/js/components/toast.js';
import { Loading } from '../../shared/js/components/loading.js';
import { ChartComponent, loadChartJS } from '../../shared/js/components/chart.js';
import { formatNumber } from '../../shared/js/utils/formatters.js';

/**
 * Dashboard Page Class
 */
class DashboardPage {
  constructor() {
    this.chart = null;
    this.data = null;
    this.isChartJSLoaded = false;
  }

  /**
   * Initialize the dashboard
   */
  async init() {
    try {
      console.log('[Dashboard] Initializing...');

      // Inject shared layouts (header, sidebar, footer)
      await LayoutManager.injectLayouts();
      
      // Set active navigation
      LayoutManager.setActiveNav('dashboard');

      // Update API status in header
      this.updateApiStatus();

      // Bind event listeners
      this.bindEvents();

      // Load Chart.js
      await loadChartJS();
      this.isChartJSLoaded = true;

      // Load initial data
      await this.loadData();

      // Setup auto-refresh polling (30 seconds)
      this.setupPolling();

      // Setup "last updated" UI updates
      this.setupLastUpdateUI();

      console.log('[Dashboard] Initialized successfully');
    } catch (error) {
      console.error('[Dashboard] Initialization error:', error);
      Toast.error('Failed to initialize dashboard');
    }
  }

  /**
   * Bind event listeners
   */
  bindEvents() {
    // Manual refresh button
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        console.log('[Dashboard] Manual refresh triggered');
        this.loadData();
        Toast.info('Refreshing dashboard...');
      });
    }
  }

  /**
   * Fetch data from API
   */
  async fetchData() {
    const [resources, status] = await Promise.all([
      api.getResources(),
      api.getStatus()
    ]);

    return { resources, status };
  }

  /**
   * Load dashboard data
   */
  async loadData() {
    try {
      // Show loading state
      Loading.addSkeleton('.stat-card');

      // Fetch data
      const data = await this.fetchData();
      this.data = data;

      // Render all sections
      this.renderData(data);

      // Remove loading state
      Loading.removeSkeleton('.stat-card');

    } catch (error) {
      console.error('[Dashboard] Load error:', error);
      Toast.error('Failed to load dashboard data');
      Loading.removeSkeleton('.stat-card');
    }
  }

  /**
   * Render all dashboard data
   */
  renderData({ resources, status }) {
    this.renderStatsGrid(resources);
    this.renderSystemAlert(status);
    this.renderCategoriesChart(resources.categories || []);
  }

  /**
   * Render stats grid (4 cards)
   */
  renderStatsGrid(resources) {
    const grid = document.getElementById('stats-grid');
    if (!grid) return;

    grid.innerHTML = `
      <div class="stat-card">
        <div class="stat-icon">📦</div>
        <div class="stat-content">
          <div class="stat-value">${formatNumber(resources.total || 0)}</div>
          <div class="stat-label">Total Resources</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🆓</div>
        <div class="stat-content">
          <div class="stat-value">${formatNumber(resources.free || 0)}</div>
          <div class="stat-label">Free Resources</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🤖</div>
        <div class="stat-content">
          <div class="stat-value">${formatNumber(resources.models || 0)}</div>
          <div class="stat-label">AI Models</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🔌</div>
        <div class="stat-content">
          <div class="stat-value">${formatNumber(resources.providers || 0)}</div>
          <div class="stat-label">Active Providers</div>
        </div>
      </div>
    `;
  }

  /**
   * Render system status alert
   */
  renderSystemAlert(status) {
    const container = document.getElementById('system-alert');
    if (!container) return;

    const alertClass = status.health === 'healthy' ? 'alert-success' :
                       status.health === 'degraded' ? 'alert-warning' : 'alert-error';

    const icon = status.health === 'healthy' ? '✅' :
                 status.health === 'degraded' ? '⚠️' : '❌';

    container.innerHTML = `
      <div class="alert ${alertClass}" role="alert">
        <div class="alert-icon">${icon}</div>
        <div class="alert-content">
          <div class="alert-title">System Status: ${status.health.toUpperCase()}</div>
          <div class="alert-body">
            Online APIs: ${status.online || 0} | 
            Offline: ${status.offline || 0} | 
            ${status.degraded ? `Degraded: ${status.degraded} | ` : ''}
            Avg Response Time: ${status.avg_response_time || 'N/A'}ms
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Render categories chart (Bar chart with Chart.js)
   */
  renderCategoriesChart(categories) {
    if (!this.isChartJSLoaded) {
      console.warn('[Dashboard] Chart.js not loaded yet');
      return;
    }

    if (!categories || categories.length === 0) {
      console.warn('[Dashboard] No categories data');
      return;
    }

    // Create chart if not exists
    if (!this.chart) {
      this.chart = new ChartComponent('categories-chart', 'bar');
    }

    const data = {
      labels: categories.map(c => c.name || 'Unknown'),
      datasets: [{
        label: 'Resource Count',
        data: categories.map(c => c.count || 0),
        backgroundColor: 'rgba(59, 130, 246, 0.6)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      }]
    };

    const options = {
      indexAxis: 'y', // Horizontal bar chart
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    };

    this.chart.create(data, options);
  }

  /**
   * Setup polling for auto-refresh
   */
  setupPolling() {
    pollingManager.start(
      'dashboard-data',
      () => this.fetchData(),
      (data, error) => {
        if (data) {
          console.log('[Dashboard] Polling update received');
          this.renderData(data);
        } else {
          console.error('[Dashboard] Polling error:', error);
          // Don't show toast on polling errors (would be too annoying)
        }
      },
      30000 // 30 seconds
    );

    console.log('[Dashboard] Polling started (30s interval)');
  }

  /**
   * Setup "last updated" UI updates
   */
  setupLastUpdateUI() {
    const el = document.getElementById('last-update');
    if (!el) return;

    pollingManager.onLastUpdate((key, text) => {
      if (key === 'dashboard-data') {
        el.textContent = `Last updated: ${text}`;
      }
    });
  }

  /**
   * Update API status in header
   */
  async updateApiStatus() {
    try {
      const health = await api.getHealth();
      LayoutManager.updateApiStatus('online', '✅ System Active');
    } catch (error) {
      LayoutManager.updateApiStatus('offline', '❌ Connection Failed');
    }
  }

  /**
   * Cleanup on page unload
   */
  destroy() {
    console.log('[Dashboard] Cleaning up...');
    pollingManager.stop('dashboard-data');
    if (this.chart) {
      this.chart.destroy();
    }
  }
}

// ============================================================================
// INITIALIZE ON DOM READY
// ============================================================================

function initDashboard() {
  const page = new DashboardPage();
  page.init();

  // Cleanup on page unload
  window.addEventListener('beforeunload', () => {
    page.destroy();
  });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDashboard);
} else {
  initDashboard();
}
```

### File 3: `/static/pages/dashboard/dashboard.css`

```css
/**
 * Dashboard-specific styles
 * Only styles unique to the dashboard page
 */

/* ============================================================================
   STATS GRID
   ============================================================================ */

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--surface-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.stat-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-strong);
  line-height: 1.2;
  margin-bottom: var(--space-2);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ============================================================================
   SYSTEM ALERT
   ============================================================================ */

.alert-container {
  margin-bottom: var(--space-6);
}

.alert {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  border: 1px solid;
}

.alert-success {
  background: rgba(16, 185, 129, 0.1);
  border-color: var(--color-success);
  color: var(--text-strong);
}

.alert-warning {
  background: rgba(245, 158, 11, 0.1);
  border-color: var(--color-warning);
  color: var(--text-strong);
}

.alert-error {
  background: rgba(239, 68, 68, 0.1);
  border-color: var(--color-danger);
  color: var(--text-strong);
}

.alert-icon {
  font-size: var(--font-size-2xl);
  flex-shrink: 0;
}

.alert-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--space-2);
}

.alert-body {
  font-size: var(--font-size-sm);
  color: var(--text-soft);
}

/* ============================================================================
   CHART CONTAINER
   ============================================================================ */

.chart-container {
  background: var(--surface-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
}

.chart-header {
  margin-bottom: var(--space-4);
}

.chart-header h2 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-strong);
  margin: 0;
}

.chart-body {
  position: relative;
  height: 400px;
  width: 100%;
}

.chart-body canvas {
  max-width: 100%;
  max-height: 100%;
}

/* ============================================================================
   SKELETON LOADING STATE
   ============================================================================ */

.stat-card.skeleton {
  pointer-events: none;
  opacity: 0.6;
}

.stat-card.skeleton .stat-value,
.stat-card.skeleton .stat-label {
  background: linear-gradient(
    90deg,
    var(--border-subtle) 25%,
    var(--border-default) 50%,
    var(--border-subtle) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
  color: transparent;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* ============================================================================
   RESPONSIVE
   ============================================================================ */

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: var(--space-4);
  }

  .stat-icon {
    font-size: 2rem;
  }

  .stat-value {
    font-size: var(--font-size-xl);
  }

  .chart-body {
    height: 300px;
  }
}

@media (max-width: 480px) {
  .page-title h1 {
    font-size: var(--font-size-2xl);
  }

  .chart-container {
    padding: var(--space-4);
  }
}
```

### Success Criteria:
- ✅ Dashboard HTML structure is clean and semantic
- ✅ Dashboard JS initializes without errors
- ✅ API calls fetch data correctly
- ✅ Stats cards render with real data
- ✅ System alert displays correctly
- ✅ Chart renders with Chart.js
- ✅ Polling starts automatically (30s interval)
- ✅ Manual refresh button works
- ✅ "Last updated" text updates every second
- ✅ Page is responsive (mobile-friendly)
- ✅ No console errors
- ✅ No WebSocket code anywhere

---

# PHASE 5: UPDATE FASTAPI BACKEND

## 🎯 PHASE 5.1: Configure FastAPI for Multi-Page Serving

**Objective**: Modify `main.py` to serve each page as a separate route.

### File to Modify: `/workspace/main.py`

```python
"""
Crypto Monitor ULTIMATE - FastAPI Backend
Serves multi-page frontend and API endpoints
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Crypto Monitor ULTIMATE",
    version="2.0.0",
    description="Advanced cryptocurrency monitoring system with AI-powered analysis"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Base directory for pages
PAGES_DIR = Path("static/pages")

# ============================================================================
# PAGE ROUTES
# ============================================================================

def serve_page(page_name: str):
    """Helper function to serve page HTML"""
    page_path = PAGES_DIR / page_name / "index.html"
    if page_path.exists():
        return FileResponse(page_path)
    else:
        logger.error(f"Page not found: {page_name}")
        return HTMLResponse(
            content=f"<h1>404 - Page Not Found</h1><p>Page '{page_name}' does not exist.</p>",
            status_code=404
        )

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Dashboard page"""
    return serve_page("dashboard")

@app.get("/market", response_class=HTMLResponse)
async def market():
    """Market data page"""
    return serve_page("market")

@app.get("/models", response_class=HTMLResponse)
async def models():
    """AI Models page"""
    return serve_page("models")

@app.get("/sentiment", response_class=HTMLResponse)
async def sentiment():
    """Sentiment Analysis page"""
    return serve_page("sentiment")

@app.get("/ai-analyst", response_class=HTMLResponse)
async def ai_analyst():
    """AI Analyst page"""
    return serve_page("ai-analyst")

@app.get("/trading-assistant", response_class=HTMLResponse)
async def trading_assistant():
    """Trading Assistant page"""
    return serve_page("trading-assistant")

@app.get("/news", response_class=HTMLResponse)
async def news():
    """News page"""
    return serve_page("news")

@app.get("/providers", response_class=HTMLResponse)
async def providers():
    """Providers page"""
    return serve_page("providers")

@app.get("/diagnostics", response_class=HTMLResponse)
async def diagnostics():
    """Diagnostics page"""
    return serve_page("diagnostics")

@app.get("/api-explorer", response_class=HTMLResponse)
async def api_explorer():
    """API Explorer page"""
    return serve_page("api-explorer")

# ============================================================================
# API ENDPOINTS
# ============================================================================

# Health & Status
@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "crypto-monitor",
        "version": "2.0.0"
    }

@app.get("/api/status")
async def status():
    """System status"""
    # TODO: Implement real status check
    return {
        "health": "healthy",
        "online": 15,
        "offline": 2,
        "degraded": 1,
        "avg_response_time": 245
    }

@app.get("/api/resources")
async def resources():
    """Resource statistics"""
    # TODO: Implement real resource counting
    return {
        "total": 150,
        "free": 87,
        "models": 42,
        "providers": 18,
        "categories": [
            {"name": "Market Data", "count": 45},
            {"name": "Blockchain Explorers", "count": 30},
            {"name": "News", "count": 25},
            {"name": "Sentiment", "count": 20},
            {"name": "DeFi", "count": 15},
            {"name": "Whale Tracking", "count": 15}
        ]
    }

# Market Data
@app.get("/api/market")
async def market_data():
    """Market data"""
    # TODO: Implement real market data fetching
    return {
        "coins": [
            {
                "rank": 1,
                "name": "Bitcoin",
                "symbol": "BTC",
                "price": 45000.00,
                "change_24h": 2.5,
                "volume_24h": 28500000000,
                "market_cap": 850000000000
            },
            # ... more coins
        ]
    }

@app.get("/api/trending")
async def trending():
    """Trending coins"""
    return {
        "trending": [
            {"rank": 1, "name": "Bitcoin", "score": 95},
            {"rank": 2, "name": "Ethereum", "score": 88},
            {"rank": 3, "name": "Solana", "score": 76}
        ]
    }

@app.get("/api/sentiment")
async def global_sentiment():
    """Global market sentiment"""
    return {
        "sentiment": "bullish",
        "score": 65,
        "fear_greed_index": 62
    }

# AI/ML
@app.get("/api/models/list")
async def models_list():
    """List available AI models"""
    return {
        "models": [
            {
                "id": "bert-sentiment",
                "name": "BERT Sentiment Analysis",
                "task": "sentiment-analysis",
                "status": "available"
            },
            # ... more models
        ]
    }

@app.get("/api/models/status")
async def models_status():
    """Models status"""
    return {
        "hf_mode": "api",
        "models_loaded": 5,
        "models_failed": 0,
        "transformers_available": True
    }

# News
@app.get("/api/news/latest")
async def news_latest(limit: int = 40):
    """Latest news"""
    return {
        "news": [
            {
                "id": 1,
                "title": "Bitcoin reaches new milestone",
                "source": "CoinDesk",
                "published": "2025-01-15T10:30:00Z",
                "symbols": ["BTC"],
                "sentiment": "bullish"
            },
            # ... more news
        ]
    }

@app.post("/api/news/summarize")
async def news_summarize(request: dict):
    """Summarize news article"""
    title = request.get("title", "")
    content = request.get("content", "")
    
    # TODO: Implement AI summarization
    return {
        "summary": f"Summary of: {title}",
        "key_points": ["Point 1", "Point 2", "Point 3"]
    }

# Sentiment Analysis
@app.post("/api/sentiment/analyze")
async def analyze_sentiment(request: dict):
    """Analyze text sentiment"""
    text = request.get("text", "")
    mode = request.get("mode", "crypto")
    
    # TODO: Implement real sentiment analysis
    return {
        "sentiment": "bullish",
        "confidence": 0.85,
        "score": 0.7
    }

# Providers
@app.get("/api/providers")
async def providers_list():
    """List API providers"""
    return {
        "providers": [
            {
                "id": "coingecko",
                "name": "CoinGecko",
                "category": "market_data",
                "status": "healthy",
                "latency": 120
            },
            # ... more providers
        ]
    }

# Logs
@app.get("/api/logs/recent")
async def logs_recent(limit: int = 50):
    """Recent logs"""
    return {
        "logs": [
            {
                "timestamp": "2025-01-15T10:30:00Z",
                "level": "info",
                "message": "API call successful"
            },
            # ... more logs
        ]
    }

# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 Crypto Monitor ULTIMATE started")
    logger.info("📊 Frontend: Multi-page architecture")
    logger.info("🔌 WebSocket: Disabled (polling-based)")
    logger.info("✅ Ready to serve requests")

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")
```

### Success Criteria:
- ✅ All 10 page routes created and working
- ✅ Static files mount correctly
- ✅ All API endpoints respond (even with mock data)
- ✅ No WebSocket endpoints present
- ✅ Server starts without errors
- ✅ Pages load in browser

---

**END OF PHASE 5**

Due to character limits, I'll provide the remaining phases (6-9) as a continuation. Would you like me to:
1. Continue with the remaining phases in a second file?
2. Or would you like me to create a condensed version covering phases 6-9?

Please let me know how you'd like to proceed!