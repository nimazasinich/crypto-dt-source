/**
 * Utility functions for formatting numbers, currency, dates, etc.
 */

/**
 * Format number with K/M/B suffix
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '—';
  
  const absNum = Math.abs(num);
  
  if (absNum >= 1e9) {
    return (num / 1e9).toFixed(2) + 'B';
  }
  if (absNum >= 1e6) {
    return (num / 1e6).toFixed(2) + 'M';
  }
  if (absNum >= 1e3) {
    return (num / 1e3).toFixed(2) + 'K';
  }
  
  return num.toFixed(0);
}

/**
 * Format as currency (USD)
 */
export function formatCurrency(num, decimals = 2) {
  if (num === null || num === undefined) return '$—';
  
  const absNum = Math.abs(num);
  
  if (absNum >= 1e9) {
    return '$' + (num / 1e9).toFixed(2) + 'B';
  }
  if (absNum >= 1e6) {
    return '$' + (num / 1e6).toFixed(2) + 'M';
  }
  if (absNum >= 1e3) {
    return '$' + (num / 1e3).toFixed(2) + 'K';
  }
  
  return '$' + num.toFixed(decimals);
}

/**
 * Format as percentage
 */
export function formatPercentage(num, decimals = 2) {
  if (num === null || num === undefined) return '—%';
  return (num >= 0 ? '+' : '') + num.toFixed(decimals) + '%';
}

/**
 * Format date
 */
export function formatDate(date) {
  if (!date) return '—';
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

/**
 * Format time
 */
export function formatTime(date) {
  if (!date) return '—';
  const d = new Date(date);
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date) {
  if (!date) return '—';
  
  const now = new Date();
  const d = new Date(date);
  const diffMs = now - d;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  
  if (diffSec < 60) return 'just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHour < 24) return `${diffHour}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  
  return formatDate(date);
}
