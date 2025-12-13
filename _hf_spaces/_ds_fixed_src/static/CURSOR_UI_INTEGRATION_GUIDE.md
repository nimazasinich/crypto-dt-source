# Cursor-Inspired UI Integration Guide

## 🎨 Overview

This guide explains how to integrate the new Cursor-inspired flat+modern design system into your crypto trading platform pages.

---

## 📦 New CSS Files Created

### Core Design System
1. **`/static/shared/css/design-system-cursor.css`** (Required - Load First)
   - Design tokens (colors, typography, spacing, shadows)
   - Base reset and typography
   - CSS variables for the entire system
   - Inter font family loading

2. **`/static/shared/css/layout-cursor.css`** (Required)
   - App container structure
   - Sidebar navigation (240px, collapsible to 60px)
   - Header (56px sleek design)
   - Main content area
   - Mobile responsive breakpoints

3. **`/static/shared/css/components-cursor.css`** (Required)
   - Buttons (primary, secondary, ghost, danger, success)
   - Cards (with hover lift effect)
   - Forms (inputs, selects, textareas)
   - Tables (clean, minimal borders)
   - Badges, pills, alerts
   - Modals, tooltips, dropdowns
   - Skeleton loaders, progress bars

4. **`/static/shared/css/animations-cursor.css`** (Optional but Recommended)
   - Keyframe animations (fade, slide, scale)
   - Hover effects (lift, scale, glow)
   - Loading states (spinners, dots)
   - Page transitions
   - Scroll reveal animations
   - Utility animation classes

---

## 🚀 Quick Start - Update Your Pages

### Step 1: Update HTML `<head>` Section

Replace your existing CSS imports with the new Cursor design system:

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Page Title - Crypto Monitor</title>

  <!-- ✅ NEW: Cursor-Inspired Design System (Load in Order) -->
  <link rel="stylesheet" href="/static/shared/css/design-system-cursor.css">
  <link rel="stylesheet" href="/static/shared/css/layout-cursor.css">
  <link rel="stylesheet" href="/static/shared/css/components-cursor.css">
  <link rel="stylesheet" href="/static/shared/css/animations-cursor.css">

  <!-- Optional: Page-specific CSS -->
  <link rel="stylesheet" href="./your-page.css">
</head>
<body>
  <!-- Your content here -->
</body>
</html>
```

### Step 2: Update HTML Structure

Use the new layout structure:

```html
<body>
  <!-- App Container -->
  <div class="app-container">
    <!-- Sidebar (Injected or Imported) -->
    <div id="sidebar-container"></div>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Header (Injected or Imported) -->
      <div id="header-container"></div>

      <!-- Page Content -->
      <div class="page-content">
        <div class="page-header">
          <h1 class="page-title">Your Page Title</h1>
          <p class="page-description">Optional description text</p>
        </div>

        <!-- Your page content goes here -->
      </div>
    </main>
  </div>
</body>
```

### Step 3: Load Header and Sidebar

If using the LayoutManager (recommended):

```javascript
import { LayoutManager } from '/static/shared/js/core/layout-manager.js';

// Initialize layout with header and sidebar
await LayoutManager.init('yourPageName');
```

Or manually inject:

```javascript
// Load sidebar
const sidebarResponse = await fetch('/static/shared/layouts/sidebar.html');
const sidebarHtml = await sidebarResponse.text();
document.getElementById('sidebar-container').innerHTML = sidebarHtml;

// Load header
const headerResponse = await fetch('/static/shared/layouts/header.html');
const headerHtml = await headerResponse.text();
document.getElementById('header-container').innerHTML = headerHtml;
```

---

## 🎨 Design System Reference

### Color Palette

**Backgrounds:**
- `--bg-primary: #0A0A0A` - Deep dark background
- `--bg-secondary: #121212` - Secondary background
- `--bg-tertiary: #1A1A1A` - Tertiary background

**Surfaces (Cards, Panels):**
- `--surface-primary: #1E1E1E` - Primary surface
- `--surface-secondary: #252525` - Secondary surface
- `--surface-tertiary: #2A2A2A` - Tertiary surface

**Text:**
- `--text-primary: #EFEFEF` - Primary text (high contrast)
- `--text-secondary: #A0A0A0` - Secondary text
- `--text-tertiary: #666666` - Tertiary text (muted)

**Accent Colors:**
- `--accent-purple: #8B5CF6` - Primary accent (Cursor-style)
- `--accent-purple-gradient: linear-gradient(135deg, #8B5CF6, #6D28D9)`
- `--accent-blue: #3B82F6` - Secondary accent
- `--color-success: #10B981` - Success green
- `--color-warning: #F59E0B` - Warning amber
- `--color-danger: #EF4444` - Danger red
- `--color-info: #06B6D4` - Info cyan

### Typography

**Font Stack:**
- Primary: `'Inter', -apple-system, system-ui, sans-serif`
- Monospace: `'JetBrains Mono', 'Fira Code', Consolas`

**Font Sizes:**
```css
--text-xs: 11px      /* Labels, captions */
--text-sm: 13px      /* Small text */
--text-base: 15px    /* Body text (default) */
--text-lg: 17px      /* Emphasized */
--text-xl: 20px      /* H3 */
--text-2xl: 24px     /* H2 */
--text-3xl: 30px     /* H1 */
--text-4xl: 36px     /* Hero */
```

**Font Weights:**
```css
--weight-normal: 400
--weight-medium: 500
--weight-semibold: 600
--weight-bold: 700
```

### Spacing

4px base grid system:

```css
--space-1: 4px
--space-2: 8px
--space-3: 12px
--space-4: 16px
--space-5: 20px
--space-6: 24px    /* Standard card padding */
--space-8: 32px
--space-12: 48px
--space-16: 64px   /* Section spacing */
```

### Border Radius

```css
--radius-sm: 6px       /* Subtle */
--radius-md: 8px       /* Standard buttons, inputs */
--radius-lg: 12px      /* Cards */
--radius-xl: 16px      /* Large cards */
--radius-full: 9999px  /* Perfect circles */
```

### Shadows

```css
--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12)    /* Subtle */
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1)     /* Default */
--shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.15)   /* Elevated */
--shadow-purple: 0 4px 12px rgba(139, 92, 246, 0.3)  /* Purple glow */
```

### Animations

```css
--duration-fast: 150ms         /* Quick interactions */
--duration-normal: 200ms       /* Default (Cursor-style) */
--duration-medium: 300ms       /* Slower transitions */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)  /* Material Design */
```

---

## 📚 Component Examples

### Buttons

```html
<!-- Primary Button (Purple Gradient) -->
<button class="btn btn-primary">
  Primary Action
</button>

<!-- Secondary Button (Flat) -->
<button class="btn btn-secondary">
  Secondary Action
</button>

<!-- Ghost Button (Transparent) -->
<button class="btn btn-ghost">
  Cancel
</button>

<!-- Icon Button -->
<button class="btn btn-icon">
  <svg>...</svg>
</button>

<!-- Button with Icon and Text -->
<button class="btn btn-primary">
  <svg width="16" height="16">...</svg>
  <span>Add Item</span>
</button>
```

### Cards

```html
<!-- Basic Card -->
<div class="card">
  <h3>Card Title</h3>
  <p>Card content goes here.</p>
</div>

<!-- Card with Header and Footer -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Title</h3>
    <button class="btn btn-ghost btn-sm">Action</button>
  </div>
  <div class="card-body">
    <p>Content here...</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-secondary">Cancel</button>
    <button class="btn btn-primary">Save</button>
  </div>
</div>

<!-- Stat Card -->
<div class="stat-card">
  <div class="stat-icon">
    <svg>...</svg>
  </div>
  <div class="stat-value">$12,345</div>
  <div class="stat-label">Total Volume</div>
  <div class="stat-change positive">
    ↑ +12.5%
  </div>
</div>
```

### Form Inputs

```html
<!-- Text Input -->
<div class="input-group">
  <label class="input-label">Email Address</label>
  <input type="email" class="input" placeholder="you@example.com" />
  <span class="input-hint">We'll never share your email.</span>
</div>

<!-- Input with Error -->
<div class="input-group">
  <label class="input-label">Password</label>
  <input type="password" class="input error" placeholder="••••••••" />
  <span class="input-error">Password must be at least 8 characters.</span>
</div>

<!-- Select -->
<select class="select">
  <option>Choose an option</option>
  <option>Option 1</option>
  <option>Option 2</option>
</select>

<!-- Textarea -->
<textarea class="textarea" placeholder="Enter your message..."></textarea>
```

### Tables

```html
<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>Name</th>
        <th>Price</th>
        <th class="text-right">24h Change</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Bitcoin</td>
        <td>$45,123</td>
        <td class="text-right text-success">+5.2%</td>
      </tr>
      <tr>
        <td>Ethereum</td>
        <td>$2,345</td>
        <td class="text-right text-danger">-2.1%</td>
      </tr>
    </tbody>
  </table>
</div>
```

### Badges

```html
<span class="badge badge-primary">New</span>
<span class="badge badge-success">Active</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-danger">Error</span>
<span class="badge badge-info">Info</span>

<!-- Pills (Rounded) -->
<span class="badge badge-primary pill">Live</span>
```

### Alerts

```html
<div class="alert alert-info">
  <svg class="alert-icon" width="20" height="20">...</svg>
  <div class="alert-content">
    <div class="alert-title">Information</div>
    <div class="alert-message">This is an informational message.</div>
  </div>
</div>
```

### Modal

```html
<div class="modal-backdrop">
  <div class="modal">
    <div class="modal-header">
      <h3 class="modal-title">Modal Title</h3>
      <button class="modal-close">×</button>
    </div>
    <div class="modal-body">
      <p>Modal content goes here...</p>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary">Cancel</button>
      <button class="btn btn-primary">Confirm</button>
    </div>
  </div>
</div>
```

---

## 🎭 Animation Classes

### Entrance Animations

```html
<!-- Fade In -->
<div class="animate-fade-in">Content fades in</div>

<!-- Fade In Up -->
<div class="animate-fade-in-up">Content slides up and fades in</div>

<!-- Scale In -->
<div class="animate-scale-in">Content scales in</div>

<!-- Stagger Children -->
<div class="stagger-fade-in">
  <div>Item 1 (delay: 0ms)</div>
  <div>Item 2 (delay: 50ms)</div>
  <div>Item 3 (delay: 100ms)</div>
</div>
```

### Hover Effects

```html
<!-- Lift on Hover -->
<div class="card hover-lift">Lifts up 2px on hover</div>

<!-- Scale on Hover -->
<div class="card hover-scale">Scales to 102% on hover</div>

<!-- Glow on Hover -->
<div class="card hover-glow">Glows with purple shadow on hover</div>
```

### Loading States

```html
<!-- Spinner -->
<div class="spinner"></div>

<!-- Dots Loader -->
<div class="dots-loader">
  <span></span>
  <span></span>
  <span></span>
</div>

<!-- Skeleton Loader -->
<div class="skeleton skeleton-text" style="width: 200px;"></div>
<div class="skeleton skeleton-title" style="width: 300px;"></div>
```

---

## 📱 Mobile Responsive

The design system is mobile-first and responsive:

### Breakpoints

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Automatic Responsive Behavior

- **Sidebar**: Slides in as overlay on mobile (<1024px)
- **Header Search**: Hidden on mobile (<1024px)
- **Cards**: Full-width with reduced padding on mobile
- **Tables**: Horizontal scroll on mobile

### Mobile-Specific Classes

```html
<!-- Show mobile menu button on tablets/mobile -->
<button class="mobile-menu-btn" id="mobile-menu-toggle">☰</button>

<!-- Responsive grid -->
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: var(--space-4);">
  <div class="card">Card 1</div>
  <div class="card">Card 2</div>
  <div class="card">Card 3</div>
</div>
```

---

## ✅ Migration Checklist

When updating an existing page:

- [ ] Replace CSS imports with new Cursor design system files
- [ ] Update `<html>` tag: Add `data-theme="dark"` attribute
- [ ] Wrap content in `.app-container` → `.main-content` → `.page-content`
- [ ] Replace old button classes with `.btn .btn-primary` etc.
- [ ] Replace old card classes with `.card`
- [ ] Update form inputs to use `.input`, `.select`, `.textarea`
- [ ] Replace old table wrappers with `.table-container .table`
- [ ] Add animation classes where appropriate
- [ ] Test mobile responsiveness (< 768px)
- [ ] Verify sidebar collapse/expand works
- [ ] Check theme toggle functionality

---

## 🎯 Best Practices

1. **Always load CSS in order:**
   ```
   design-system-cursor.css → layout-cursor.css → components-cursor.css → animations-cursor.css
   ```

2. **Use CSS variables for consistency:**
   ```css
   /* Good */
   padding: var(--space-4);
   color: var(--text-secondary);

   /* Avoid */
   padding: 16px;
   color: #A0A0A0;
   ```

3. **Use animation classes instead of custom CSS:**
   ```html
   <!-- Good -->
   <div class="card hover-lift animate-fade-in">

   <!-- Avoid -->
   <div class="card" style="transition: all 0.3s; animation: fadeIn 0.5s;">
   ```

4. **Follow the 200ms animation standard:**
   - All transitions should use `--duration-normal: 200ms`
   - This matches Cursor's snappy feel

5. **Maintain dark theme by default:**
   - Use `data-theme="dark"` on `<html>`
   - Support light theme with theme toggle

---

## 🔧 Customization

To customize the design system, override CSS variables in your page-specific CSS:

```css
/* your-page.css */
:root {
  /* Change primary accent from purple to blue */
  --accent-purple: #3B82F6;
  --accent-purple-gradient: linear-gradient(135deg, #3B82F6, #1E40AF);

  /* Adjust spacing */
  --space-6: 32px;  /* Increase card padding */

  /* Custom durations */
  --duration-normal: 250ms;  /* Slightly slower */
}
```

---

## 📞 Support

For issues or questions:
1. Check the design system CSS files for available classes
2. Review this integration guide
3. Test in both desktop and mobile viewports
4. Verify all CSS files are loaded in correct order

---

## 🚀 Quick Links

- [Design System CSS](./shared/css/design-system-cursor.css)
- [Layout CSS](./shared/css/layout-cursor.css)
- [Components CSS](./shared/css/components-cursor.css)
- [Animations CSS](./shared/css/animations-cursor.css)
- [Header Layout](./shared/layouts/header.html)
- [Sidebar Layout](./shared/layouts/sidebar.html)

---

**Last Updated:** 2025-12-10
**Version:** 1.0.0
**Design System:** Cursor-Inspired Flat + Modern
