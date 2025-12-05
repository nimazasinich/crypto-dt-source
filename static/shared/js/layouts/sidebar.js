/**
 * Sidebar Loader
 * Loads and initializes the sidebar component
 * This is a wrapper that uses the LayoutManager
 */

import { LayoutManager } from '../core/layout-manager.js';

// Auto-initialize when this script loads
(async function initSidebar() {
  try {
    // Only inject sidebar if not already injected
    if (!LayoutManager.layoutsInjected) {
      await LayoutManager.injectSidebar();
    }
  } catch (error) {
    console.error('[Sidebar] Failed to load sidebar:', error);
  }
})();

export default LayoutManager;

