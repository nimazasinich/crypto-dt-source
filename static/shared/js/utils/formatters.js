/**
 * Utility functions for formatting numbers, currency, dates, etc.
 */

/**
 * Format large numbers with suffixes (K, M, B, T)
 */
export function formatNumber(num, decimals = 2) {
  if (num === null || num === undefined) return '--';
  if (num === 0) return '0';

  const abs = Math.abs(num);
  
  if (abs >= 1e12) {
    return (num / 1e12).toFixed(decimals) + 'T';
  }
  if (abs >= 1e9) {
    return (num / 1e9).toFixed(decimals) + 'B';
  }
  if (abs >= 1e6) {
    return (num / 1e6).toFixed(decimals) + 'M';
  }
  if (abs >= 1e3) {
    return (num / 1e3).toFixed(decimals) + 'K';
  }
  
  return num.toFixed(decimals);
}

/**
 * Format currency (USD)
 */
export function formatCurrency(value, decimals = 2) {
  if (value === null || value === undefined) return '--';
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format percentage
 */
export function formatPercent(value, decimals = 2) {
  if (value === null || value === undefined) return '--';
  
  const sign = value >= 0 ? '+' : '';
  return sign + value.toFixed(decimals) + '%';
}

/**
 * Format date/time
 */
export function formatDate(timestamp, options = {}) {
  if (!timestamp) return '--';
  
  const date = new Date(timestamp);
  
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    ...options,
  }).format(date);
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(timestamp) {
  if (!timestamp) return '--';
  
  const now = Date.now();
  const diff = now - timestamp;
  const seconds = Math.floor(diff / 1000);
  
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

/**
 * Escape HTML to prevent XSS
 */
export function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text, maxLength = 50) {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

export default {
  formatNumber,
  formatCurrency,
  formatPercent,
  formatDate,
  formatRelativeTime,
  escapeHtml,
  truncate,
};
