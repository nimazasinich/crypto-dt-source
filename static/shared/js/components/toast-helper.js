/**
 * Toast Helper Functions
 * Simple wrapper around Toast class for easy usage
 */

import Toast from './toast.js';

/**
 * Show toast notification
 */
export function showToast(icon, message, type = 'info') {
  // Initialize toast if needed
  Toast.init();
  
  // Convert icon+message format to standard toast
  const fullMessage = icon ? `${icon} ${message}` : message;
  
  return Toast.show(fullMessage, type);
}

/**
 * Show success toast
 */
export function showSuccess(message) {
  return showToast('✅', message, 'success');
}

/**
 * Show error toast
 */
export function showError(message) {
  return showToast('❌', message, 'error');
}

/**
 * Show warning toast
 */
export function showWarning(message) {
  return showToast('⚠️', message, 'warning');
}

/**
 * Show info toast
 */
export function showInfo(message) {
  return showToast('ℹ️', message, 'info');
}

export default {
  showToast,
  showSuccess,
  showError,
  showWarning,
  showInfo
};
