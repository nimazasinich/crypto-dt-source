# UI Structure Usage Script / Guide

## How to Use the Application's UI Structure

This document provides step-by-step instructions on how to work with the multi-page architecture, shared components, and layout system.

---

## Part 1: Understanding the Structure

### Architecture Overview

The application follows a **modular multi-page architecture**:

1. **Pages** (`/static/pages/`) - Standalone page modules
2. **Shared Components** (`/static/shared/`) - Reusable layouts, utilities, components
3. **Layout Manager** - Dynamically injects header, sidebar, footer
4. **API Client** - Centralized HTTP client with caching
5. **Component System** - Toast, Modal, Table, Chart, Loading

### Key Principles

- Each page is self-contained but shares common layouts
- Layouts are injected dynamically (not hardcoded in each page)
- All API calls go through the centralized API client
- Components are reusable across pages
- Theme system (dark/light) is managed globally

---

## Part 2: Creating a New Page

### Step-by-Step Process

#### Step 1: Create Directory Structure

```
Location: /static/pages/your-page-name/
Files needed:
  - index.html (required)
  - your-page-name.css (optional, for page-specific styles)
  - your-page-name.js (optional, for page-specific logic)
```

#### Step 2: Create the HTML Template

**Template Structure:**

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <!-- Meta tags -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Page Title | Crypto Hub</title>
  
  <!-- Shared CSS (always include these) -->
  <link rel="stylesheet" href="/static/shared/css/design-system.css">
  <link rel="stylesheet" href="/static/shared/css/layout.css">
  <link rel="stylesheet" href="/static/shared/css/components.css">
  <link rel="stylesheet" href="/static/shared/css/utilities.css">
  
  <!-- Page-specific CSS -->
  <link rel="stylesheet" href="/static/pages/your-page-name/your-page-name.css">
  
  <!-- Error suppressor (suppresses browser warnings) -->
  <script src="/static/shared/js/utils/error-suppressor.js"></script>
</head>
<body>
  <!-- App Container (required structure) -->
  <div class="app-container">
    
    <!-- Sidebar Container (LayoutManager will inject sidebar here) -->
    <aside id="sidebar-container"></aside>
    
    <!-- Main Content Area -->
    <main class="main-content">
      
      <!-- Header Container (LayoutManager will inject header here) -->
      <header id="header-container"></header>
      
      <!-- Your Page Content -->
      <div class="page-content">
        <!-- Your page-specific content goes here -->
        <h1>Your Page Title</h1>
        <div id="your-content-container">
          <!-- Content -->
        </div>
      </div>
      
    </main>
  </div>
  
  <!-- Scripts (at end of body) -->
  <script type="module">
    // Import LayoutManager (required)
    import LayoutManager from '/static/shared/js/core/layout-manager.js';
    
    // Import API Client (if you need API calls)
    import { ApiClient } from '/static/shared/js/core/api-client.js';
    
    // Import components you need
    import { Toast } from '/static/shared/js/components/toast.js';
    import { Loading } from '/static/shared/js/components/loading.js';
    
    // Initialize Layout Manager (this injects header, sidebar, footer)
    await LayoutManager.init('your-page-name');
    
    // Your page initialization code
    async function initPage() {
      // Show loading state
      Loading.show();
      
      try {
        // Fetch data using API client
        const client = new ApiClient();
        const data = await client.get('/api/your-endpoint');
        
        // Update UI with data
        updateUI(data);
        
        // Show success message
        Toast.success('Data loaded successfully');
      } catch (error) {
        // Show error message
        Toast.error('Failed to load data: ' + error.message);
      } finally {
        // Hide loading state
        Loading.hide();
      }
    }
    
    // Call initialization
    initPage();
  </script>
</body>
</html>
```

#### Step 3: Register the Page

**A. Add to Sidebar Navigation**

Edit: `/static/shared/layouts/sidebar.html`

Add navigation link:

```html
<li>
  <a href="/static/pages/your-page-name/index.html" 
     class="nav-link" 
     data-page="your-page-name">
    <span class="icon">📊</span>
    <span>Your Page Name</span>
  </a>
</li>
```

**B. Register in Config**

Edit: `/static/shared/js/core/config.js`

Add to `PAGE_METADATA` array:

```javascript
export const PAGE_METADATA = [
  // ... existing pages
  { 
    page: 'your-page-name', 
    title: 'Your Page Title | Crypto Hub', 
    icon: 'star' 
  }
];
```

---

## Part 3: Using Shared Components

### Layout Manager

**Purpose:** Manages shared layouts (header, sidebar, footer)

**Basic Usage:**

```javascript
import LayoutManager from '/static/shared/js/core/layout-manager.js';

// Initialize (injects layouts, sets active page)
await LayoutManager.init('page-name');

// Set active page in navigation
LayoutManager.setActivePage('dashboard');

// Update API status badge
LayoutManager.updateApiStatus('online', '✓ System Active');
LayoutManager.updateApiStatus('offline', '✗ Offline');
LayoutManager.updateApiStatus('degraded', '⚠ Degraded');

// Toggle theme
LayoutManager.toggleTheme();

// Get current theme
const theme = document.documentElement.getAttribute('data-theme');
```

### API Client

**Purpose:** Centralized HTTP client with caching and error handling

**Basic Usage:**

```javascript
import { ApiClient } from '/static/shared/js/core/api-client.js';

const client = new ApiClient();

// GET request with caching
const data = await client.get('/api/market/top', {
  cache: true,
  ttl: 30000 // Cache for 30 seconds
});

// POST request
const result = await client.post('/api/sentiment/analyze', {
  text: 'Bitcoin is bullish!'
});

// PUT request
await client.put('/api/settings', { theme: 'dark' });

// DELETE request
await client.delete('/api/resource/123');

// With error handling
try {
  const data = await client.get('/api/endpoint');
} catch (error) {
  console.error('API Error:', error);
  Toast.error('Failed to fetch data');
}
```

### Polling Manager

**Purpose:** Auto-refresh data with smart pause/resume

**Usage:**

```javascript
import { PollingManager } from '/static/shared/js/core/polling-manager.js';

// Create poller
const poller = new PollingManager({
  interval: 5000,        // Poll every 5 seconds
  pauseOnHidden: true,   // Pause when tab is hidden
  maxRetries: 3          // Max retries on failure
});

// Start polling
poller.start(async () => {
  const client = new ApiClient();
  const data = await client.get('/api/market/top');
  updateMarketData(data);
});

// Stop polling
poller.stop();

// Pause temporarily
poller.pause();

// Resume
poller.resume();
```

### Toast Notifications

**Purpose:** User feedback messages

**Usage:**

```javascript
import { Toast } from '/static/shared/js/components/toast.js';

// Success message
Toast.success('Operation completed successfully');

// Error message
Toast.error('Failed to save changes');

// Info message
Toast.info('Processing your request...');

// Warning message
Toast.warning('Please check your input');

// Custom message
Toast.show('Custom message', 'info', 5000); // message, type, duration
```

### Modal Dialogs

**Purpose:** Popup dialogs for confirmations, forms, etc.

**Usage:**

```javascript
import { Modal } from '/static/shared/js/components/modal.js';

// Simple modal
const modal = new Modal({
  title: 'Confirm Action',
  content: '<p>Are you sure you want to proceed?</p>',
  buttons: [
    {
      text: 'Cancel',
      class: 'btn-secondary',
      action: () => modal.close()
    },
    {
      text: 'Confirm',
      class: 'btn-primary',
      action: () => {
        // Perform action
        performAction();
        modal.close();
      }
    }
  ]
});
modal.show();

// Modal with form
const formModal = new Modal({
  title: 'Add Item',
  content: `
    <form id="add-form">
      <input type="text" name="name" placeholder="Name" required>
      <button type="submit">Add</button>
    </form>
  `,
  onClose: () => console.log('Modal closed')
});
formModal.show();
```

### Loading Component

**Purpose:** Show/hide loading states

**Usage:**

```javascript
import { Loading } from '/static/shared/js/components/loading.js';

// Show loading overlay
Loading.show('Loading data...');

// Hide loading
Loading.hide();

// Show loading in specific container
Loading.showIn('#my-container', 'Loading...');

// Hide loading in container
Loading.hideIn('#my-container');
```

### Table Component

**Purpose:** Data tables with sorting and filtering

**Usage:**

```javascript
import { DataTable } from '/static/shared/js/components/table.js';

const table = new DataTable('#table-container', {
  columns: [
    { key: 'name', label: 'Name', sortable: true },
    { key: 'price', label: 'Price', sortable: true, formatter: (val) => `$${val}` },
    { key: 'change', label: 'Change', sortable: true }
  ],
  data: marketData,
  searchable: true,
  pagination: true,
  pageSize: 10
});

// Update data
table.updateData(newData);

// Refresh
table.refresh();
```

### Chart Component

**Purpose:** Chart.js wrapper for data visualization

**Usage:**

```javascript
import { Chart } from '/static/shared/js/components/chart.js';

const chart = new Chart('#chart-container', {
  type: 'line',
  data: {
    labels: dates,
    datasets: [{
      label: 'Price',
      data: prices,
      borderColor: '#8B5CF6'
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false
  }
});

// Update chart data
chart.updateData(newData);
```

---

## Part 4: Common Patterns

### Pattern 1: Page with Data Fetching

```javascript
import LayoutManager from '/static/shared/js/core/layout-manager.js';
import { ApiClient } from '/static/shared/js/core/api-client.js';
import { Toast } from '/static/shared/js/components/toast.js';
import { Loading } from '/static/shared/js/components/loading.js';

// Initialize
await LayoutManager.init('my-page');

// Fetch and display data
async function loadData() {
  Loading.show('Loading data...');
  
  try {
    const client = new ApiClient();
    const data = await client.get('/api/endpoint');
    
    renderData(data);
    Toast.success('Data loaded');
  } catch (error) {
    Toast.error('Failed to load: ' + error.message);
  } finally {
    Loading.hide();
  }
}

function renderData(data) {
  const container = document.getElementById('data-container');
  container.innerHTML = data.map(item => `
    <div class="data-item">
      <h3>${item.name}</h3>
      <p>${item.description}</p>
    </div>
  `).join('');
}

// Load on page load
loadData();
```

### Pattern 2: Page with Auto-Refresh

```javascript
import LayoutManager from '/static/shared/js/core/layout-manager.js';
import { ApiClient } from '/static/shared/js/core/api-client.js';
import { PollingManager } from '/static/shared/js/core/polling-manager.js';

await LayoutManager.init('my-page');

const client = new ApiClient();
const poller = new PollingManager({ interval: 10000 });

async function refreshData() {
  try {
    const data = await client.get('/api/endpoint', { cache: false });
    updateUI(data);
  } catch (error) {
    console.error('Refresh failed:', error);
  }
}

// Start auto-refresh
poller.start(refreshData);

// Initial load
refreshData();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  poller.stop();
});
```

### Pattern 3: Form Submission

```javascript
import { ApiClient } from '/static/shared/js/core/api-client.js';
import { Toast } from '/static/shared/js/components/toast.js';
import { Loading } from '/static/shared/js/components/loading.js';

document.getElementById('my-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData);
  
  Loading.show('Submitting...');
  
  try {
    const client = new ApiClient();
    const result = await client.post('/api/submit', data);
    
    Toast.success('Submitted successfully!');
    e.target.reset();
  } catch (error) {
    Toast.error('Submission failed: ' + error.message);
  } finally {
    Loading.hide();
  }
});
```

### Pattern 4: Interactive Table with Actions

```javascript
import { DataTable } from '/static/shared/js/components/table.js';
import { Modal } from '/static/shared/js/components/modal.js';
import { ApiClient } from '/static/shared/js/core/api-client.js';

const table = new DataTable('#table-container', {
  columns: [
    { key: 'name', label: 'Name' },
    { key: 'status', label: 'Status' },
    { 
      key: 'actions', 
      label: 'Actions',
      render: (row) => `
        <button onclick="editItem(${row.id})">Edit</button>
        <button onclick="deleteItem(${row.id})">Delete</button>
      `
    }
  ],
  data: items
});

async function deleteItem(id) {
  const modal = new Modal({
    title: 'Confirm Delete',
    content: '<p>Are you sure?</p>',
    buttons: [
      { text: 'Cancel', action: () => modal.close() },
      {
        text: 'Delete',
        action: async () => {
          const client = new ApiClient();
          await client.delete(`/api/items/${id}`);
          table.refresh();
          modal.close();
        }
      }
    ]
  });
  modal.show();
}
```

---

## Part 5: File Paths Reference

### Absolute Paths (Recommended)

```
/static/shared/js/core/layout-manager.js
/static/shared/css/design-system.css
/static/pages/dashboard/index.html
```

### Relative Paths (From Page Directory)

```
../../shared/js/core/layout-manager.js
../../shared/css/design-system.css
../dashboard/index.html
```

### Import Statements

```javascript
// ES6 Modules (recommended)
import LayoutManager from '/static/shared/js/core/layout-manager.js';
import { ApiClient } from '/static/shared/js/core/api-client.js';

// Dynamic imports
const { Toast } = await import('/static/shared/js/components/toast.js');
```

---

## Part 6: Best Practices Checklist

### ✅ Do's

- Always use `LayoutManager.init()` in every page
- Use `ApiClient` for all API calls (don't use raw `fetch()`)
- Show loading states with `Loading` component
- Provide user feedback with `Toast` notifications
- Handle errors gracefully with try/catch
- Use shared CSS classes from design system
- Follow the page template structure
- Register new pages in config and sidebar
- Use absolute paths for imports
- Clean up polling/intervals on page unload

### ❌ Don'ts

- Don't hardcode layouts in pages (use LayoutManager)
- Don't use raw `fetch()` for API calls
- Don't create duplicate components (use shared ones)
- Don't forget error handling
- Don't use inline styles (use CSS classes)
- Don't forget to register pages in navigation
- Don't use relative paths that break on different routes
- Don't forget to stop polling/intervals

---

## Part 7: Troubleshooting

### Layout Not Showing

- Check that `LayoutManager.init()` is called
- Verify containers exist: `#sidebar-container`, `#header-container`
- Check browser console for errors
- Verify file paths are correct

### API Calls Failing

- Check that `ApiClient` is imported correctly
- Verify endpoint URLs are correct
- Check network tab for actual requests
- Verify CORS settings if calling external APIs

### Components Not Working

- Check that component scripts are imported
- Verify component initialization code
- Check browser console for errors
- Ensure CSS is loaded

### Navigation Not Highlighting

- Verify page name matches `data-page` attribute
- Check that `LayoutManager.setActivePage()` is called
- Verify page is registered in `PAGE_METADATA`

---

## Part 8: Quick Reference

### Required Imports for Every Page

```javascript
import LayoutManager from '/static/shared/js/core/layout-manager.js';
await LayoutManager.init('page-name');
```

### Common Component Imports

```javascript
import { ApiClient } from '/static/shared/js/core/api-client.js';
import { Toast } from '/static/shared/js/components/toast.js';
import { Loading } from '/static/shared/js/components/loading.js';
import { Modal } from '/static/shared/js/components/modal.js';
import { PollingManager } from '/static/shared/js/core/polling-manager.js';
```

### Required HTML Structure

```html
<div class="app-container">
  <aside id="sidebar-container"></aside>
  <header id="header-container"></header>
  <main class="main-content">
    <div class="page-content">
      <!-- Your content -->
    </div>
  </main>
</div>
```

### Required CSS Imports

```html
<link rel="stylesheet" href="/static/shared/css/design-system.css">
<link rel="stylesheet" href="/static/shared/css/layout.css">
<link rel="stylesheet" href="/static/shared/css/components.css">
```

---

This guide provides the complete framework for working with the UI structure. Follow these patterns and practices to maintain consistency and leverage the shared component system effectively.
