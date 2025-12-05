# API Helper Utilities

## Overview

The `APIHelper` class provides a comprehensive set of utilities for making API requests, handling authentication, and managing common operations across the application.

## Features

- ✅ **Token Management**: Automatic JWT expiration checking
- ✅ **API Requests**: Simplified fetch with error handling
- ✅ **Data Extraction**: Smart array extraction from various response formats
- ✅ **Health Monitoring**: Periodic API health checks
- ✅ **UI Helpers**: Toast notifications, formatting utilities
- ✅ **Performance**: Debounce and throttle functions

---

## Usage

### Basic Import

```javascript
import { APIHelper } from '../../shared/js/utils/api-helper.js';
```

---

## API Methods

### Authentication

#### `getHeaders()`
Returns headers with optional Authorization token. Automatically checks token expiration.

```javascript
const headers = APIHelper.getHeaders();
// Returns: { 'Content-Type': 'application/json', 'Authorization': 'Bearer <token>' }
```

#### `isTokenExpired(token)`
Checks if a JWT token is expired.

```javascript
const expired = APIHelper.isTokenExpired(token);
// Returns: boolean
```

---

### API Requests

#### `fetchAPI(url, options)`
Fetch data with automatic authorization and error handling.

```javascript
// GET request
const data = await APIHelper.fetchAPI('/api/market/top?limit=10');

// POST request
const result = await APIHelper.fetchAPI('/api/sentiment/analyze', {
  method: 'POST',
  body: JSON.stringify({ text: 'Bitcoin is great!' })
});
```

---

### Data Processing

#### `extractArray(data, keys)`
Intelligently extract arrays from various response formats.

```javascript
// Works with direct arrays
const arr1 = APIHelper.extractArray([1, 2, 3]);

// Works with nested data
const arr2 = APIHelper.extractArray({ markets: [...] }, ['markets', 'data']);

// Works with objects
const arr3 = APIHelper.extractArray({ item1: {}, item2: {} });
```

---

### Health Monitoring

#### `checkHealth()`
Check API health status.

```javascript
const health = await APIHelper.checkHealth();
// Returns: { status: 'online', healthy: true, data: {...} }
```

#### `monitorHealth(callback, interval)`
Setup periodic health monitoring.

```javascript
const intervalId = APIHelper.monitorHealth((health) => {
  console.log('API Status:', health.status);
  if (!health.healthy) {
    console.warn('API is down!');
  }
}, 30000); // Check every 30 seconds

// Later, stop monitoring
clearInterval(intervalId);
```

---

### UI Utilities

#### `showToast(message, type, duration)`
Display toast notifications.

```javascript
APIHelper.showToast('Operation successful!', 'success');
APIHelper.showToast('Something went wrong', 'error');
APIHelper.showToast('Please wait...', 'info');
APIHelper.showToast('Check your input', 'warning');
```

#### `formatCurrency(amount, currency)`
Format numbers as currency.

```javascript
const formatted = APIHelper.formatCurrency(1234.56);
// Returns: "$1,234.56"
```

#### `formatPercentage(value, decimals)`
Format values as percentages.

```javascript
const percent = APIHelper.formatPercentage(2.5);
// Returns: "+2.50%"
```

#### `formatNumber(num, options)`
Format numbers with locale settings.

```javascript
const formatted = APIHelper.formatNumber(1000000);
// Returns: "1,000,000"
```

---

### Performance Utilities

#### `debounce(func, wait)`
Debounce function calls.

```javascript
const debouncedSearch = APIHelper.debounce((query) => {
  console.log('Searching:', query);
}, 300);

// Call multiple times, only executes once after 300ms
debouncedSearch('bitcoin');
debouncedSearch('ethereum');
debouncedSearch('solana');
```

#### `throttle(func, limit)`
Throttle function calls.

```javascript
const throttledScroll = APIHelper.throttle(() => {
  console.log('Scroll event');
}, 100);

window.addEventListener('scroll', throttledScroll);
```

---

## Complete Example: Building a Page

```javascript
import { APIHelper } from '../../shared/js/utils/api-helper.js';

class YourPage {
  constructor() {
    this.data = [];
    this.healthMonitor = null;
  }

  async init() {
    // Setup health monitoring
    this.healthMonitor = APIHelper.monitorHealth((health) => {
      console.log('API Health:', health.status);
    });

    // Load data
    await this.loadData();

    // Setup event listeners
    this.bindEvents();
  }

  async loadData() {
    try {
      // Fetch data using APIHelper
      const response = await APIHelper.fetchAPI('/api/your-endpoint');
      
      // Extract array safely
      this.data = APIHelper.extractArray(response, ['data', 'items']);
      
      // Render
      this.render();
      
      // Show success
      APIHelper.showToast('Data loaded successfully!', 'success');
    } catch (error) {
      console.error('Load error:', error);
      
      // Use fallback data
      this.data = this.getDemoData();
      this.render();
      
      // Show error
      APIHelper.showToast('Using demo data', 'warning');
    }
  }

  bindEvents() {
    // Debounced search
    const searchInput = document.getElementById('search');
    const debouncedSearch = APIHelper.debounce((query) => {
      this.filterData(query);
    }, 300);
    
    searchInput?.addEventListener('input', (e) => {
      debouncedSearch(e.target.value);
    });
  }

  render() {
    // Render your data
    this.data.forEach(item => {
      const price = APIHelper.formatCurrency(item.price);
      const change = APIHelper.formatPercentage(item.change);
      console.log(`${item.name}: ${price} (${change})`);
    });
  }

  getDemoData() {
    return [
      { name: 'Bitcoin', price: 50000, change: 2.5 },
      { name: 'Ethereum', price: 3000, change: -1.2 }
    ];
  }

  destroy() {
    // Cleanup
    if (this.healthMonitor) {
      clearInterval(this.healthMonitor);
    }
  }
}

// Initialize
const page = new YourPage();
page.init();
```

---

## Best Practices

### 1. Always Use APIHelper for Fetch Requests
```javascript
// ✅ Good
const data = await APIHelper.fetchAPI('/api/endpoint');

// ❌ Avoid
const response = await fetch('/api/endpoint');
const data = await response.json();
```

### 2. Extract Arrays Safely
```javascript
// ✅ Good
const items = APIHelper.extractArray(response, ['items', 'data']);

// ❌ Avoid (can fail)
const items = response.items;
```

### 3. Use Debounce for User Input
```javascript
// ✅ Good
const debouncedHandler = APIHelper.debounce(handler, 300);
input.addEventListener('input', debouncedHandler);

// ❌ Avoid (too many calls)
input.addEventListener('input', handler);
```

### 4. Monitor API Health
```javascript
// ✅ Good
APIHelper.monitorHealth((health) => {
  updateUI(health.status);
});

// ❌ Avoid (no health awareness)
// Just hope the API is up
```

---

## Token Expiration

The `APIHelper` automatically checks JWT token expiration:

1. **On Every Request**: Before adding Authorization header
2. **Automatic Removal**: Expired tokens are removed from localStorage
3. **Graceful Degradation**: Requests continue without auth if token expired

```javascript
// Token is checked automatically
const data = await APIHelper.fetchAPI('/api/protected-route');
// If token expired, it's removed and request proceeds without auth
```

---

## Error Handling

All `APIHelper` methods handle errors gracefully:

```javascript
try {
  const data = await APIHelper.fetchAPI('/api/endpoint');
  // Use data
} catch (error) {
  // Error is already logged by APIHelper
  // Use fallback data
  const data = getDemoData();
}
```

---

## Browser Compatibility

- ✅ Modern browsers (ES6+ modules)
- ✅ Chrome 61+
- ✅ Firefox 60+
- ✅ Safari 11+
- ✅ Edge 16+

---

## License

Part of Crypto Monitor ULTIMATE project.

