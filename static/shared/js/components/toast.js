/**
 * Toast Notification System
 * Displays temporary notification messages
 */

import { CONFIG } from '../core/config.js';

const TOAST_DEFAULTS = {
  MAX_VISIBLE: 3,
  DEFAULT_DURATION: 3500,
  ERROR_DURATION: 6000,
};

// CONFIG.TOAST is optional in some builds/pages; keep Toast resilient.
const TOAST_CONFIG = {
  ...TOAST_DEFAULTS,
  ...(CONFIG?.TOAST || {}),
};

export class Toast {
  static container = null;
  static toasts = [];
  static maxToasts = TOAST_CONFIG.MAX_VISIBLE;

  /**
   * Initialize toast container
   */
  static init() {
    if (this.container) return;

    this.container = document.getElementById('toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  }

  /**
   * Show a toast notification
   */
  static show(message, type = 'info', options = {}) {
    this.init();

    const toast = {
      id: Date.now() + Math.random(),
      message,
      type,
      duration:
        options.duration ??
        (type === 'error' ? TOAST_CONFIG.ERROR_DURATION : TOAST_CONFIG.DEFAULT_DURATION),
      dismissible: options.dismissible !== false,
      action: options.action || null,
    };

    // Remove oldest toast if at max
    if (this.toasts.length >= this.maxToasts) {
      const oldest = this.toasts.shift();
      this.dismiss(oldest.id);
    }

    this.toasts.push(toast);
    this.render(toast);

    // Auto-dismiss
    if (toast.duration > 0) {
      setTimeout(() => this.dismiss(toast.id), toast.duration);
    }

    return toast.id;
  }

  /**
   * Render toast element
   */
  static render(toast) {
    const el = document.createElement('div');
    el.className = `toast toast-${toast.type}`;
    el.setAttribute('data-toast-id', toast.id);
    el.setAttribute('role', 'alert');
    el.setAttribute('aria-live', 'polite');

    const icon = this.getIcon(toast.type);

    el.innerHTML = `
      <div class="toast-icon">${icon}</div>
      <div class="toast-content">
        <div class="toast-message">${this.escapeHtml(toast.message)}</div>
        ${toast.action ? `<button class="toast-action">${toast.action.label}</button>` : ''}
      </div>
      ${toast.dismissible ? '<button class="toast-close" aria-label="Close">&times;</button>' : ''}
      ${toast.duration > 0 ? `<div class="toast-progress" style="animation-duration: ${toast.duration}ms"></div>` : ''}
    `;

    // Close button handler
    if (toast.dismissible) {
      const closeBtn = el.querySelector('.toast-close');
      closeBtn.addEventListener('click', () => this.dismiss(toast.id));
    }

    // Action button handler
    if (toast.action) {
      const actionBtn = el.querySelector('.toast-action');
      actionBtn.addEventListener('click', () => {
        toast.action.callback();
        this.dismiss(toast.id);
      });
    }

    this.container.appendChild(el);

    // Trigger animation
    setTimeout(() => el.classList.add('toast-show'), 10);
  }

  /**
   * Dismiss a toast
   */
  static dismiss(toastId) {
    const el = this.container.querySelector(`[data-toast-id="${toastId}"]`);
    if (!el) return;

    el.classList.remove('toast-show');
    el.classList.add('toast-hide');

    setTimeout(() => {
      if (el.parentNode) {
        el.parentNode.removeChild(el);
      }
    }, 300);

    // Remove from array
    this.toasts = this.toasts.filter(t => t.id !== toastId);
  }

  /**
   * Dismiss all toasts
   */
  static dismissAll() {
    this.toasts.forEach(toast => this.dismiss(toast.id));
  }

  /**
   * Convenience methods
   */
  static success(message, options = {}) {
    return this.show(message, 'success', options);
  }

  static error(message, options = {}) {
    return this.show(message, 'error', options);
  }

  static warning(message, options = {}) {
    return this.show(message, 'warning', options);
  }

  static info(message, options = {}) {
    return this.show(message, 'info', options);
  }

  /**
   * Get icon for toast type
   */
  static getIcon(type) {
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️',
    };
    return icons[type] || 'ℹ️';
  }

  /**
   * Escape HTML
   */
  static escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

export default Toast;
