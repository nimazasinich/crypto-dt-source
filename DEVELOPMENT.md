# Developer Guide

## Quick Start

### Local Development

```bash
# 1. Clone the repository
git clone <repository-url>
cd workspace

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements_hf.txt

# 4. Run the application
python app.py

# 5. Open browser
# Navigate to http://localhost:7860
```

### Docker Development

```bash
# Build and run
docker build -t crypto-monitor .
docker run -p 7860:7860 crypto-monitor

# Or use docker-compose (if available)
docker-compose up
```

## Project Structure

```
/workspace/
├── static/
│   ├── pages/              # Multi-page architecture
│   │   ├── dashboard/      # Each page is a self-contained module
│   │   │   ├── index.html  # Page HTML
│   │   │   ├── dashboard.js # Page JavaScript
│   │   │   └── dashboard.css # Page-specific styles
│   │   └── [other pages]/
│   └── shared/             # Shared resources
│       ├── js/core/        # Core utilities
│       ├── js/components/  # Reusable UI components
│       ├── css/            # Stylesheets
│       └── layouts/        # HTML templates
├── api_server_extended.py  # FastAPI server
├── app.py                  # Entry point
└── requirements_hf.txt     # Dependencies
```

## Adding a New Page

### Step 1: Create Page Directory
```bash
mkdir -p static/pages/my-page
```

### Step 2: Create Page Files

**index.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Page | Crypto Monitor</title>
  
  <!-- Shared CSS -->
  <link rel="stylesheet" href="/static/shared/css/design-system.css">
  <link rel="stylesheet" href="/static/shared/css/global.css">
  <link rel="stylesheet" href="/static/shared/css/components.css">
  <link rel="stylesheet" href="/static/shared/css/layout.css">
  <link rel="stylesheet" href="/static/shared/css/utilities.css">
  
  <!-- Page-specific CSS -->
  <link rel="stylesheet" href="./my-page.css">
</head>
<body>
  <!-- Layout placeholders (injected by LayoutManager) -->
  <header id="header-placeholder"></header>
  <div class="app-layout">
    <aside id="sidebar-placeholder"></aside>
    <main id="main-content" class="main-content">
      <h1>My Page Title</h1>
      <!-- Page content here -->
    </main>
  </div>
  
  <!-- Shared scripts (as modules) -->
  <script type="module" src="./my-page.js"></script>
</body>
</html>
```

**my-page.js**
```javascript
import { APIClient } from '/static/shared/js/core/api-client.js';
import { PollingManager } from '/static/shared/js/core/polling-manager.js';
import { LayoutManager } from '/static/shared/js/core/layout-manager.js';
import { Toast } from '/static/shared/js/components/toast.js';
import { getIcon } from '/static/shared/js/components/icons.js';

// Initialize layout
const layout = new LayoutManager();

// Initialize API client
const api = new APIClient();

// State
let data = null;

// DOM Elements
const container = document.getElementById('my-container');

// Load data function
async function loadData() {
  try {
    data = await api.get('/api/my-endpoint');
    renderData();
  } catch (error) {
    console.error('Failed to load data:', error);
    Toast.error('Failed to load data');
  }
}

// Render function
function renderData() {
  if (!data) return;
  
  container.innerHTML = `
    <div class="card">
      ${getIcon('checkCircle')}
      <span>${data.message}</span>
    </div>
  `;
}

// Initialize page
document.addEventListener('DOMContentLoaded', async () => {
  await layout.init();
  loadData();
});
```

**my-page.css**
```css
/* Page-specific styles only */
#my-container {
  display: grid;
  gap: var(--spacing-4);
}

/* Use design system variables */
.my-custom-card {
  background: var(--surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--spacing-4);
}
```

### Step 3: Add Route in Backend

In `api_server_extended.py`:
```python
@app.get("/my-page", response_class=HTMLResponse)
async def my_page():
    """Serve my-page"""
    return serve_page("my-page")
```

### Step 4: Add to Navigation

In `/static/shared/js/core/config.js`, add to PAGE_METADATA:
```javascript
{
  path: '/my-page',
  page: 'my-page',
  title: 'My Page | Crypto Monitor',
  icon: 'my-icon',  // Must exist in icons.js
  description: 'Description of my page',
  polling: true,
  interval: 30000
}
```

### Step 5: Update Sidebar

In `/static/shared/layouts/sidebar.html`, add navigation item:
```html
<a href="/my-page" class="nav-item" data-page="my-page">
  <span class="nav-icon"><!-- SVG icon --></span>
  <span class="nav-text">My Page</span>
</a>
```

## API Development

### Adding a New Endpoint

In `api_server_extended.py`:

```python
from pydantic import BaseModel

# Request model
class MyRequest(BaseModel):
    param1: str
    param2: int = 10

# Response model (optional but recommended)
class MyResponse(BaseModel):
    success: bool
    data: dict

@app.post("/api/my-endpoint")
async def my_endpoint(request: MyRequest):
    """My endpoint description"""
    try:
        result = process_data(request.param1, request.param2)
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Using the API Client

```javascript
import { APIClient } from '/static/shared/js/core/api-client.js';

const api = new APIClient();

// GET request
const data = await api.get('/api/market');

// POST request
const result = await api.post('/api/sentiment/analyze', {
  text: 'Bitcoin is rising!'
});
```

## Component Usage

### Toast Notifications

```javascript
import { Toast } from '/static/shared/js/components/toast.js';

Toast.success('Operation successful!');
Toast.error('Something went wrong');
Toast.warning('Proceed with caution');
Toast.info('Here is some information');
```

### Modal Dialogs

```javascript
import { Modal } from '/static/shared/js/components/modal.js';

const modal = new Modal({
  title: 'Confirm Action',
  content: '<p>Are you sure?</p>',
  onConfirm: () => console.log('Confirmed'),
  onCancel: () => console.log('Cancelled')
});

modal.open();
```

### SVG Icons

```javascript
import { getIcon, createIconElement } from '/static/shared/js/components/icons.js';

// Get icon as HTML string
const iconHtml = getIcon('dashboard');

// Get icon as DOM element
const iconEl = createIconElement('market');
container.appendChild(iconEl);
```

### Loading States

```javascript
import { showLoading, hideLoading } from '/static/shared/js/components/loading.js';

showLoading(container);  // Show spinner in container
// ... fetch data ...
hideLoading(container);  // Remove spinner
```

### Charts

```javascript
import { loadChartJS, createChart } from '/static/shared/js/components/chart.js';

async function renderChart() {
  await loadChartJS();
  
  const chart = createChart('chart-canvas', {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed'],
      datasets: [{
        label: 'Price',
        data: [100, 120, 110],
        borderColor: 'var(--accent-primary)'
      }]
    }
  });
}
```

### Polling

```javascript
import { PollingManager } from '/static/shared/js/core/polling-manager.js';

const polling = new PollingManager();

// Start polling
polling.start({
  key: 'market-data',
  interval: 30000,
  callback: async () => {
    await loadData();
  }
});

// Stop polling
polling.stop('market-data');
```

## CSS Guidelines

### Use Design System Variables

```css
/* Colors */
color: var(--text-primary);
background: var(--surface);
border-color: var(--border-color);

/* Spacing (4px base) */
padding: var(--spacing-4);  /* 16px */
gap: var(--spacing-2);      /* 8px */

/* Border radius */
border-radius: var(--radius-md);

/* Shadows */
box-shadow: var(--shadow-sm);

/* Transitions */
transition: var(--transition-fast);
```

### Responsive Design

```css
/* Desktop first, then responsive */
.my-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-4);
}

@media (max-width: 1024px) {
  .my-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .my-grid {
    grid-template-columns: 1fr;
  }
}
```

## Testing

### Manual Testing
See `TESTING.md` for comprehensive testing checklist.

### API Testing
```bash
# Health check
curl http://localhost:7860/api/health

# Market data
curl http://localhost:7860/api/market

# Sentiment analysis
curl -X POST http://localhost:7860/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Bitcoin is rising!"}'
```

### Browser Console Testing
```javascript
// Check if modules loaded
import('/static/shared/js/core/api-client.js')
  .then(m => console.log('APIClient loaded:', m));

// Test API call
fetch('/api/health')
  .then(r => r.json())
  .then(console.log);
```

## Common Issues

### CORS Errors
The FastAPI server has CORS enabled for all origins. If you see CORS errors:
1. Check that the API server is running
2. Verify the URL matches the server address

### Module Import Errors
Ensure all imports use:
- Absolute paths from root: `/static/shared/js/...`
- Relative paths: `./my-file.js`
- File extensions: `.js`

### Styles Not Applying
1. Check CSS file is linked in HTML
2. Verify CSS variables exist in design-system.css
3. Check for specificity conflicts

### API Returning 404
1. Check route exists in api_server_extended.py
2. Verify HTTP method (GET vs POST)
3. Check for typos in URL

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 7860 | Server port |
| USE_MOCK_DATA | false | Enable mock data |
| USE_FASTAPI_HTML | true | Use FastAPI+HTML mode |
| USE_GRADIO | false | Use Gradio mode |
| DOCKER_CONTAINER | false | Docker detection |

---

**Version**: 2.0.0  
**Last Updated**: 2025-01-15
