# Syntax Error Fix Guide

## Error: "Uncaught SyntaxError: Unexpected identifier 'http'"

This error occurs when the browser tries to parse a URL as JavaScript code. Here are the common causes and fixes:

## Common Causes

### 1. **Missing Quotes in HTML Attributes**
```html
<!-- WRONG -->
<script src=http://example.com/script.js></script>

<!-- CORRECT -->
<script src="http://example.com/script.js"></script>
```

### 2. **Incorrect Module Import**
```javascript
// WRONG
import something from http://example.com/module.js;

// CORRECT
import something from 'http://example.com/module.js';
```

### 3. **Data URI Issues**
```html
<!-- Can cause issues if not properly encoded -->
<link rel="icon" href="data:image/svg+xml,<svg>...</svg>">

<!-- Better approach -->
<link rel="icon" href="/static/assets/icons/favicon.svg">
```

## Quick Fixes

### Fix 1: Check Browser Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for the exact file causing the error
4. Check the line number

### Fix 2: Disable Config Helper Temporarily
If the config helper is causing issues, comment it out:

**In `static/shared/layouts/header.html`:**
```html
<!-- Temporarily comment out -->
<!-- <button class="header-btn" id="config-helper-btn">...</button> -->
```

**In `static/shared/js/core/layout-manager.js`:**
```javascript
// Comment out the config helper section
/*
const configHelperBtn = document.getElementById('config-helper-btn');
if (configHelperBtn) {
  // ... config helper code
}
*/
```

### Fix 3: Check Market Page Imports
**In `static/pages/market/index.html`:**

Make sure the script import is correct:
```html
<!-- Check this line -->
<script type="module">
  import { LayoutManager } from '/static/shared/js/core/layout-manager.js';
  await LayoutManager.init('market');
  await import('./market-improved.js');
</script>
```

If `market-improved.js` doesn't exist or has errors, revert to:
```html
<script type="module">
  import { LayoutManager } from '/static/shared/js/core/layout-manager.js';
  await LayoutManager.init('market');
  await import('./market.js');
</script>
```

### Fix 4: Validate JavaScript Files

Check these files for syntax errors:
1. `static/shared/components/config-helper-modal.js`
2. `static/pages/market/market-improved.js`
3. `static/pages/dashboard/dashboard-fear-greed-fix.js`

Run a syntax check:
```bash
# If you have Node.js installed
node --check static/shared/components/config-helper-modal.js
node --check static/pages/market/market-improved.js
```

## Step-by-Step Debugging

### Step 1: Identify the Problem File
1. Open browser DevTools (F12)
2. Go to Sources tab
3. Look for the file with the error
4. Check the line number

### Step 2: Check for Common Issues
- Missing quotes around URLs
- Unclosed template literals (backticks)
- Missing semicolons
- Incorrect import statements

### Step 3: Temporary Rollback
If you can't find the issue, rollback recent changes:

**Revert market page:**
```html
<!-- In static/pages/market/index.html -->
<!-- Change this: -->
await import('./market-improved.js');

<!-- Back to this: -->
await import('./market.js');
```

**Remove improvements CSS:**
```html
<!-- In static/pages/market/index.html -->
<!-- Comment out: -->
<!-- <link rel="stylesheet" href="/static/pages/market/market-improvements.css"> -->
```

### Step 4: Clear Browser Cache
1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

## Specific Fixes for This Project

### Fix the Config Helper Modal

If the config helper is causing issues, here's a safe version:

**Create: `static/shared/components/config-helper-modal-safe.js`**
```javascript
export class ConfigHelperModal {
  constructor() {
    this.modal = null;
  }

  show() {
    alert('Config Helper - Coming Soon!');
  }

  hide() {
    // Do nothing
  }
}
```

Then update the import in `layout-manager.js`:
```javascript
const { ConfigHelperModal } = await import('/static/shared/components/config-helper-modal-safe.js');
```

### Fix the Market Page

If market improvements are causing issues:

**Option 1: Use original market.js**
```html
<!-- In static/pages/market/index.html -->
<script type="module">
  import { LayoutManager } from '/static/shared/js/core/layout-manager.js';
  await LayoutManager.init('market');
  await import('./market.js'); <!-- Use original -->
</script>
```

**Option 2: Check market-improved.js exists**
```bash
# Check if file exists
ls static/pages/market/market-improved.js
```

## Prevention

### 1. Always Use Quotes
```javascript
// Good
const url = 'http://example.com';
import module from './module.js';

// Bad
const url = http://example.com;
import module from ./module.js;
```

### 2. Validate Before Committing
```bash
# Check JavaScript syntax
find . -name "*.js" -exec node --check {} \;
```

### 3. Use Linter
Install ESLint to catch errors early:
```bash
npm install -g eslint
eslint static/**/*.js
```

## Emergency Rollback

If nothing works, rollback all changes:

### 1. Remove Config Helper
```bash
# Delete or rename the files
mv static/shared/components/config-helper-modal.js static/shared/components/config-helper-modal.js.bak
```

### 2. Revert Header Changes
Edit `static/shared/layouts/header.html` and remove the config helper button.

### 3. Revert Layout Manager
Edit `static/shared/js/core/layout-manager.js` and remove the config helper event listener.

### 4. Revert Market Page
Edit `static/pages/market/index.html`:
- Remove `market-improvements.css`
- Change import back to `market.js`

## Testing After Fix

1. Clear browser cache
2. Reload page (Ctrl+Shift+R or Cmd+Shift+R)
3. Check console for errors
4. Test each feature individually

## Need Help?

If the error persists:
1. Check the exact error message in console
2. Note which file and line number
3. Check that file for syntax errors
4. Look for missing quotes, brackets, or semicolons

---

**Quick Fix Command:**
```bash
# Revert to working state
git checkout static/pages/market/index.html
git checkout static/shared/layouts/header.html
git checkout static/shared/js/core/layout-manager.js
```
