/**
 * Loading Helper Functions
 * Simple wrapper around Loading class for easy usage
 */

import Loading from './loading.js';

/**
 * Show loading state
 */
export function showLoading(containerId, message = 'Loading...') {
  return Loading.show(containerId, message);
}

/**
 * Hide loading state
 */
export function hideLoading(containerId) {
  return Loading.hide(containerId);
}

/**
 * Show skeleton loader
 */
export function showSkeleton(containerId, type = 'cards', count = 4) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  if (type === 'cards') {
    container.innerHTML = Loading.skeletonCards(count);
  } else if (type === 'rows') {
    container.innerHTML = Loading.skeletonRows(count);
  }
}

export default {
  showLoading,
  hideLoading,
  showSkeleton
};
