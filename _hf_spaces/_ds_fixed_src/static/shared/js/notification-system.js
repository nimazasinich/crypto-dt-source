/**
 * Enhanced Notification System
 * Beautiful toast notifications with animations and queuing
 */

export class NotificationSystem {
  constructor() {
    this.container = null;
    this.queue = [];
    this.activeToasts = new Set();
    this.maxToasts = 3;
    this.init();
  }

  /**
   * Initialize notification container
   */
  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'notification-container';
      this.container.className = 'notification-container';
      this.container.setAttribute('aria-live', 'polite');
      this.container.setAttribute('aria-atomic', 'true');
      document.body.appendChild(this.container);
    }
  }

  /**
   * Show notification
   * @param {Object} options - Notification options
   */
  show(options = {}) {
    const defaults = {
      type: 'info', // 'success', 'error', 'warning', 'info'
      title: '',
      message: '',
      duration: 4000,
      closable: true,
      icon: null,
      action: null,
      position: 'top-right' // 'top-right', 'top-left', 'bottom-right', 'bottom-left', 'top-center'
    };

    const config = { ...defaults, ...options };

    // Queue if too many active toasts
    if (this.activeToasts.size >= this.maxToasts) {
      this.queue.push(config);
      return;
    }

    this.createToast(config);
  }

  /**
   * Create toast element
   * @param {Object} config - Toast configuration
   */
  createToast(config) {
    const toast = document.createElement('div');
    toast.className = `notification notification-${config.type}`;
    toast.setAttribute('role', 'alert');

    // Icon
    const icon = this.getIcon(config.type, config.icon);

    // Content
    const content = `
      <div class="notification-icon">${icon}</div>
      <div class="notification-content">
        ${config.title ? `<div class="notification-title">${config.title}</div>` : ''}
        <div class="notification-message">${config.message}</div>
        ${config.action ? `
          <button class="notification-action" onclick="${config.action.onClick}">
            ${config.action.label}
          </button>
        ` : ''}
      </div>
      ${config.closable ? `
        <button class="notification-close" aria-label="Close notification">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      ` : ''}
    `;

    toast.innerHTML = content;

    // Progress bar
    if (config.duration > 0) {
      const progress = document.createElement('div');
      progress.className = 'notification-progress';
      progress.style.animationDuration = `${config.duration}ms`;
      toast.appendChild(progress);
    }

    // Add to container
    this.container.appendChild(toast);
    this.activeToasts.add(toast);

    // Animate in
    requestAnimationFrame(() => {
      toast.classList.add('notification-show');
    });

    // Close button
    if (config.closable) {
      const closeBtn = toast.querySelector('.notification-close');
      closeBtn.addEventListener('click', () => this.removeToast(toast));
    }

    // Auto remove
    if (config.duration > 0) {
      setTimeout(() => this.removeToast(toast), config.duration);
    }

    // Pause on hover
    toast.addEventListener('mouseenter', () => {
      const progress = toast.querySelector('.notification-progress');
      if (progress) progress.style.animationPlayState = 'paused';
    });

    toast.addEventListener('mouseleave', () => {
      const progress = toast.querySelector('.notification-progress');
      if (progress) progress.style.animationPlayState = 'running';
    });
  }

  /**
   * Remove toast
   * @param {HTMLElement} toast - Toast element
   */
  removeToast(toast) {
    if (!toast || !this.activeToasts.has(toast)) return;

    toast.classList.remove('notification-show');
    toast.classList.add('notification-hide');

    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
      this.activeToasts.delete(toast);

      // Process queue
      if (this.queue.length > 0) {
        const next = this.queue.shift();
        this.createToast(next);
      }
    }, 300);
  }

  /**
   * Get icon for notification type
   * @param {string} type - Notification type
   * @param {string} customIcon - Custom icon HTML
   * @returns {string} Icon HTML
   */
  getIcon(type, customIcon) {
    if (customIcon) return customIcon;

    const icons = {
      success: `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
      `,
      error: `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="15" y1="9" x2="9" y2="15"></line>
          <line x1="9" y1="9" x2="15" y2="15"></line>
        </svg>
      `,
      warning: `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
          <line x1="12" y1="9" x2="12" y2="13"></line>
          <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
      `,
      info: `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="16" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
      `
    };

    return icons[type] || icons.info;
  }

  /**
   * Shorthand methods
   */
  success(message, title = 'Success', options = {}) {
    this.show({ type: 'success', message, title, ...options });
  }

  error(message, title = 'Error', options = {}) {
    this.show({ type: 'error', message, title, ...options });
  }

  warning(message, title = 'Warning', options = {}) {
    this.show({ type: 'warning', message, title, ...options });
  }

  info(message, title = 'Info', options = {}) {
    this.show({ type: 'info', message, title, ...options });
  }

  /**
   * Clear all notifications
   */
  clearAll() {
    this.activeToasts.forEach(toast => this.removeToast(toast));
    this.queue = [];
  }

  /**
   * Inject styles
   */
  static injectStyles() {
    if (document.querySelector('#notification-system-styles')) return;

    const style = document.createElement('style');
    style.id = 'notification-system-styles';
    style.textContent = `
      .notification-container {
        position: fixed;
        top: 70px;
        right: 20px;
        z-index: 10000;
        display: flex;
        flex-direction: column;
        gap: 12px;
        max-width: 400px;
        pointer-events: none;
      }

      .notification {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 16px;
        background: white;
        border: 1px solid rgba(20, 184, 166, 0.15);
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(13, 115, 119, 0.12);
        pointer-events: all;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
      }

      .notification-show {
        opacity: 1;
        transform: translateX(0);
      }

      .notification-hide {
        opacity: 0;
        transform: translateX(100%);
      }

      .notification-icon {
        flex-shrink: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .notification-success {
        border-left: 4px solid #10b981;
      }

      .notification-success .notification-icon {
        color: #10b981;
      }

      .notification-error {
        border-left: 4px solid #ef4444;
      }

      .notification-error .notification-icon {
        color: #ef4444;
      }

      .notification-warning {
        border-left: 4px solid #f59e0b;
      }

      .notification-warning .notification-icon {
        color: #f59e0b;
      }

      .notification-info {
        border-left: 4px solid #22d3ee;
      }

      .notification-info .notification-icon {
        color: #22d3ee;
      }

      .notification-content {
        flex: 1;
        min-width: 0;
      }

      .notification-title {
        font-size: 14px;
        font-weight: 600;
        color: #0f2926;
        margin-bottom: 4px;
      }

      .notification-message {
        font-size: 13px;
        color: #2a5f5a;
        line-height: 1.5;
      }

      .notification-action {
        margin-top: 8px;
        padding: 4px 12px;
        background: linear-gradient(135deg, #2dd4bf, #22d3ee);
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
      }

      .notification-action:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(20, 184, 166, 0.3);
      }

      .notification-close {
        flex-shrink: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: transparent;
        border: none;
        color: #6bb8ae;
        cursor: pointer;
        border-radius: 6px;
        transition: all 0.2s;
      }

      .notification-close:hover {
        background: rgba(20, 184, 166, 0.1);
        color: #14b8a6;
      }

      .notification-progress {
        position: absolute;
        bottom: 0;
        left: 0;
        height: 3px;
        background: linear-gradient(90deg, #2dd4bf, #22d3ee);
        animation: notificationProgress linear forwards;
      }

      @keyframes notificationProgress {
        from { width: 100%; }
        to { width: 0%; }
      }

      @media (max-width: 768px) {
        .notification-container {
          left: 12px;
          right: 12px;
          max-width: none;
        }

        .notification {
          width: 100%;
        }
      }

      [data-theme="dark"] .notification {
        background: rgba(19, 46, 42, 0.95);
        border-color: rgba(45, 212, 191, 0.25);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
      }

      [data-theme="dark"] .notification-title {
        color: #f0fdfa;
      }

      [data-theme="dark"] .notification-message {
        color: #99f6e4;
      }

      [data-theme="dark"] .notification-close {
        color: #5eead4;
      }

      [data-theme="dark"] .notification-close:hover {
        background: rgba(45, 212, 191, 0.15);
        color: #2dd4bf;
      }
    `;
    document.head.appendChild(style);
  }
}

// Inject styles and create global instance
NotificationSystem.injectStyles();
const notifications = new NotificationSystem();

// Export as default and named
export default notifications;
export { notifications };
