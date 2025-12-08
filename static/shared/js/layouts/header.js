/**
 * Header Loader
 * Loads and initializes the header component
 * This is a wrapper that uses the LayoutManager
 */

import { LayoutManager } from '../core/layout-manager.js';

// Auto-initialize when this script loads
(async function initHeader() {
  try {
    // Only inject header if not already injected
    if (!LayoutManager.layoutsInjected) {
      await LayoutManager.injectHeader();
    }
  } catch (error) {
    console.error('[Header] Failed to load header:', error);
  }
})();

export default LayoutManager;

