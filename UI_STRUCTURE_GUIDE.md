# Crypto Intelligence Hub - UI Structure Guide

## Overview

The application uses a **multi-page architecture** with shared components and a dynamic layout injection system. Each page is standalone but shares common layouts, utilities, and components.

## Architecture

### 1. **Page Structure** (`/static/pages/`)

Each page is a self-contained module in its own directory:

```
static/pages/
├── dashboard/          # Main dashboard with stats
├── market/            # Market data and prices
├── models/            # AI models status
├── sentiment/         # Sentiment analysis
├── ai-analyst/        # AI trading advisor
├── trading-assistant/  # Trading signals
├── news/              # News feed
├── providers/         # API provider management
├── diagnostics/       # System diagnostics
└── api-explorer/     # API testing tool
```

**Page Template Structure:**

```html
<!DOCTYPE html>
<html>
<head>
  <!-- Meta, CSS imports -->
  <!-- Shared CSS: design-system, layout, components -->
  <!-- Page-specific CSS -->
</head>
<body>
  <div class="app-container">
    <!-- Layout containers (injected by LayoutManager) -->
    <aside id="sidebar-container"></aside>
    <header id="header-container"></header>
    
    <!-- Page-specific content -->
    <main class="main-content">
      <div class="page-content">
        <!-- Your page content here -->
      </div>
    </main>
  </div>
  
  <!-- Scripts -->
  <script type="module">
    // Initialize LayoutManager
    import LayoutManager from '/static/shared/js/core/layout-manager.js';
    await LayoutManager.init('page-name');
    
    // Your page logic here
  </script>
</body>
</html>
```

### 2. **Shared Components** (`/static/shared/`)

#### **Layouts** (`/shared/layouts/`)

- `header.html` - App header with status badge
- `sidebar.html` - Navigation sidebar
- `footer.html` - Footer content

#### **Core JavaScript** (`/shared/js/core/`)

- `layout-manager.js` - Injects layouts, manages navigation
- `api-client.js` - HTTP client with caching
- `polling-manager.js` - Auto-refresh system
- `config.js` - Central configuration

#### **Components** (`/shared/js/components/`)

- `toast.js` - Notification system
- `modal.js` - Modal dialogs
- `table.js` - Data tables
- `chart.js` - Chart.js wrapper
- `loading.js` - Loading states

#### **CSS** (`/shared/css/`)

- `design-system.css` - CSS variables, tokens
- `global.css` - Base styles
- `layout.css` - Layout styles
- `components.css` - Component styles

### 3. **NewResourceApi** (`/NewResourceApi/`)

Protobuf-based API structure for resource management:

- `api.py` - API definitions
- `api_pb2.py` - Generated protobuf code
- `test_api.py` - API testing utilities

## Key Systems

### Layout Manager

**Purpose:** Dynamically injects shared layouts (header, sidebar, footer) into pages.

**Usage:**

```javascript
import LayoutManager from '/static/shared/js/core/layout-manager.js';

// Initialize layouts (injects header, sidebar, footer)
await LayoutManager.init('dashboard'); // 'dashboard' = active page name

// Set active page in navigation
LayoutManager.setActivePage('market');

// Update API status badge
LayoutManager.updateApiStatus('online', '✓ System Active');
```

**Features:**

- Automatic layout injection
- API health monitoring
- Theme management (dark/light)
- Mobile-responsive sidebar
- Fallback layouts if files fail to load

### API Client

**Purpose:** Centralized HTTP client with caching and error handling.

**Usage:**

```javascript
import { ApiClient } from '/static/shared/js/core/api-client.js';

const client = new ApiClient();

// GET request with caching
const data = await client.get('/api/market/top', {
  cache: true,
  ttl: 30000 // 30 seconds
});

// POST request
const result = await client.post('/api/sentiment/analyze', {
  text: 'Bitcoin is bullish!'
});
```

### Polling Manager

**Purpose:** Auto-refresh data with smart pause/resume.

**Usage:**

```javascript
import { PollingManager } from '/static/shared/js/core/polling-manager.js';

const poller = new PollingManager({
  interval: 5000, // 5 seconds
  pauseOnHidden: true // Pause when tab is hidden
});

// Start polling
poller.start(async () => {
  const data = await fetch('/api/market/top').then(r => r.json());
  updateUI(data);
});

// Stop polling
poller.stop();
```

### Component System

**Toast Notifications:**

```javascript
import { Toast } from '/static/shared/js/components/toast.js';

Toast.success('Data loaded successfully');
Toast.error('Failed to fetch data');
Toast.info('Processing...');
```

**Modal Dialogs:**

```javascript
import { Modal } from '/static/shared/js/components/modal.js';

const modal = new Modal({
  title: 'Confirm Action',
  content: '<p>Are you sure?</p>',
  buttons: [
    { text: 'Cancel', action: () => modal.close() },
    { text: 'Confirm', action: () => { /* ... */ } }
  ]
});
modal.show();
```

## Page Development Workflow

### Step 1: Create Page Directory

```
static/pages/my-page/
├── index.html
├── my-page.css
└── my-page.js (optional)
```

### Step 2: Create HTML Structure

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Page | Crypto Hub</title>
  
  <!-- Shared CSS -->
  <link rel="stylesheet" href="/static/shared/css/design-system.css">
  <link rel="stylesheet" href="/static/shared/css/layout.css">
  <link rel="stylesheet" href="/static/shared/css/components.css">
  
  <!-- Page CSS -->
  <link rel="stylesheet" href="/static/pages/my-page/my-page.css">
</head>
<body>
  <div class="app-container">
    <aside id="sidebar-container"></aside>
    <header id="header-container"></header>
    
    <main class="main-content">
      <div class="page-content">
        <h1>My Page</h1>
        <!-- Your content -->
      </div>
    </main>
  </div>
  
  <script type="module">
    import LayoutManager from '/static/shared/js/core/layout-manager.js';
    import { ApiClient } from '/static/shared/js/core/api-client.js';
    
    // Initialize layout
    await LayoutManager.init('my-page');
    
    // Your page logic
    const client = new ApiClient();
    const data = await client.get('/api/endpoint');
    // ... update UI
  </script>
</body>
</html>
```

### Step 3: Add to Navigation

Update `/static/shared/layouts/sidebar.html`:

```html
<li>
  <a href="/static/pages/my-page/index.html" 
     class="nav-link" 
     data-page="my-page">
    My Page
  </a>
</li>
```

### Step 4: Register in Config

Update `/static/shared/js/core/config.js`:

```javascript
export const PAGE_METADATA = [
  // ... existing pages
  { page: 'my-page', title: 'My Page | Crypto Hub', icon: 'star' }
];
```

## Best Practices

1. **Always use LayoutManager.init()** - Ensures layouts are injected
2. **Use shared components** - Don't reinvent toast, modal, etc.
3. **Follow naming conventions** - Page name matches directory name
4. **Use API client** - Don't use raw fetch() for API calls
5. **Handle loading states** - Use Loading component
6. **Responsive design** - Test on mobile (sidebar auto-hides)
7. **Error handling** - Use Toast for user feedback
8. **Cache API calls** - Use ApiClient caching for performance

## File Paths

**Absolute paths (recommended):**

- `/static/shared/js/core/layout-manager.js`
- `/static/pages/dashboard/index.html`

**Relative paths (from page directory):**

- `../../shared/js/core/layout-manager.js`
- `../dashboard/index.html`

## Theme System

The app supports dark/light themes:

```javascript
// Toggle theme
LayoutManager.toggleTheme();

// Get current theme
const theme = document.documentElement.getAttribute('data-theme');
```

Theme is persisted in `localStorage` as `crypto_monitor_theme`.

## API Status Monitoring

LayoutManager automatically monitors API health:

- Checks `/api/health` every 30 seconds
- Updates status badge in header
- Pauses when tab is hidden
- Enters offline mode after 3 failures

## Mobile Support

- Sidebar auto-hides on screens < 1024px
- Hamburger menu in header toggles sidebar
- Touch-friendly components
- Responsive grid layouts
