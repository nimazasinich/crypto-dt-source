/**
 * UI Manager - Complete UI/UX Control
 * Handles all UI interactions, animations, and state management
 */

class UIManager {
  constructor() {
    this.toasts = [];
    this.modals = new Map();
    this.loading = new Set();
    this.init();
  }

  init() {
    this.createToastContainer();
    this.initializeGlobalHandlers();
    this.setupAccessibility();
    console.log('✅ UI Manager initialized');
  }

  /**
   * Create toast container if not exists
   */
  createToastContainer() {
    if (!document.getElementById('toast-container')) {
      const container = document.createElement('div');
      container.id = 'toast-container';
      container.setAttribute('aria-live', 'polite');
      container.setAttribute('aria-atomic', 'true');
      container.style.cssText = `
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
      `;
      document.body.appendChild(container);
    }
  }

  /**
   * Show toast notification
   */
  showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const id = `toast-${Date.now()}-${Math.random()}`;
    toast.id = id;
    toast.className = `toast ${type}`;
    
    // Icon based on type
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    };
    
    toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 1.25rem;">${icons[type] || icons.info}</span>
        <span style="flex: 1;">${this.escapeHtml(message)}</span>
        <button onclick="uiManager.closeToast('${id}')" style="background: none; border: none; color: inherit; cursor: pointer; opacity: 0.7; padding: 0.25rem;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    `;
    
    container.appendChild(toast);
    this.toasts.push(id);
    
    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => this.closeToast(id), duration);
    }
    
    return id;
  }

  /**
   * Close specific toast
   */
  closeToast(id) {
    const toast = document.getElementById(id);
    if (toast) {
      toast.style.animation = 'slideOutRight 0.3s ease-out';
      setTimeout(() => {
        toast.remove();
        this.toasts = this.toasts.filter(t => t !== id);
      }, 300);
    }
  }

  /**
   * Show loading state on element
   */
  showLoading(elementId, text = 'Loading...') {
    const element = document.getElementById(elementId);
    if (!element) return;

    this.loading.add(elementId);
    
    const originalContent = element.innerHTML;
    element.dataset.originalContent = originalContent;
    
    element.innerHTML = `
      <div class="loading-container">
        <div class="spinner"></div>
        <p style="color: var(--text-secondary); margin-top: 1rem;">${this.escapeHtml(text)}</p>
      </div>
    `;
  }

  /**
   * Hide loading state
   */
  hideLoading(elementId, content = null) {
    const element = document.getElementById(elementId);
    if (!element) return;

    this.loading.delete(elementId);
    
    if (content) {
      element.innerHTML = content;
    } else if (element.dataset.originalContent) {
      element.innerHTML = element.dataset.originalContent;
      delete element.dataset.originalContent;
    }
  }

  /**
   * Create and show modal
   */
  showModal(options = {}) {
    const {
      id = `modal-${Date.now()}`,
      title = 'Modal',
      content = '',
      size = 'md', // sm, md, lg, xl
      onClose = null
    } = options;

    // Check if modal already exists
    if (this.modals.has(id)) {
      const existing = this.modals.get(id);
      existing.modal.classList.add('active');
      return id;
    }

    const modal = document.createElement('div');
    modal.id = id;
    modal.className = 'modal active';
    modal.innerHTML = `
      <div class="modal-backdrop" onclick="uiManager.closeModal('${id}')"></div>
      <div class="modal-content modal-${size}">
        <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; padding: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
          <h2 style="margin: 0; font-size: 1.25rem; font-weight: 700;">${this.escapeHtml(title)}</h2>
          <button onclick="uiManager.closeModal('${id}')" class="btn-icon" aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body" style="padding: 1.5rem; overflow-y: auto; max-height: 60vh;">
          ${content}
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    this.modals.set(id, { modal, onClose });

    // Handle Escape key
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        this.closeModal(id);
      }
    };
    document.addEventListener('keydown', handleEscape);
    modal.dataset.escapeHandler = handleEscape;

    return id;
  }

  /**
   * Close modal
   */
  closeModal(id) {
    const modalData = this.modals.get(id);
    if (!modalData) return;

    const { modal, onClose } = modalData;
    
    modal.classList.remove('active');
    setTimeout(() => {
      modal.remove();
      this.modals.delete(id);
      if (onClose) onClose();
    }, 300);

    // Remove escape handler
    if (modal.dataset.escapeHandler) {
      document.removeEventListener('keydown', modal.dataset.escapeHandler);
    }
  }

  /**
   * Show confirmation dialog
   */
  async confirm(message, title = 'Confirm') {
    return new Promise((resolve) => {
      const id = this.showModal({
        title,
        content: `
          <p style="margin-bottom: 1.5rem; color: var(--text-primary);">${this.escapeHtml(message)}</p>
          <div style="display: flex; gap: 0.75rem; justify-content: flex-end;">
            <button class="btn btn-secondary" onclick="uiManager.closeModal('${id}'); window.uiManagerResolve(false);">
              Cancel
            </button>
            <button class="btn btn-primary" onclick="uiManager.closeModal('${id}'); window.uiManagerResolve(true);">
              Confirm
            </button>
          </div>
        `,
        onClose: () => resolve(false)
      });

      window.uiManagerResolve = resolve;
    });
  }

  /**
   * Show error message
   */
  showError(message, details = null) {
    const content = `
      <div style="color: var(--danger);">
        <h3 style="margin-bottom: 0.5rem;">⚠️ Error</h3>
        <p>${this.escapeHtml(message)}</p>
        ${details ? `<pre style="margin-top: 1rem; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 0.5rem; overflow-x: auto; font-size: 0.875rem;">${this.escapeHtml(details)}</pre>` : ''}
      </div>
    `;

    this.showModal({
      title: 'Error',
      content,
      size: 'md'
    });

    this.showToast(message, 'error');
  }

  /**
   * Initialize global event handlers
   */
  initializeGlobalHandlers() {
    // Handle all button clicks for better UX
    document.addEventListener('click', (e) => {
      const button = e.target.closest('button, .btn');
      if (button && !button.classList.contains('unstyled')) {
        // Add ripple effect
        this.createRipple(e, button);
      }
    });

    // Handle form submissions
    document.addEventListener('submit', (e) => {
      const form = e.target;
      if (form.tagName === 'FORM' && !form.classList.contains('no-prevent')) {
        // Could add form validation here
      }
    });

    // Handle loading states for async operations
    window.addEventListener('beforeunload', (e) => {
      if (this.loading.size > 0) {
        e.preventDefault();
        e.returnValue = 'Operations in progress...';
      }
    });
  }

  /**
   * Create ripple effect on button click
   */
  createRipple(event, button) {
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;

    const rect = button.getBoundingClientRect();
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - rect.left - radius}px`;
    circle.style.top = `${event.clientY - rect.top - radius}px`;
    circle.classList.add('ripple');

    const ripple = button.getElementsByClassName('ripple')[0];
    if (ripple) {
      ripple.remove();
    }

    circle.style.cssText += `
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.3);
      transform: scale(0);
      animation: ripple 0.6s ease-out;
      pointer-events: none;
    `;

    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(circle);

    setTimeout(() => circle.remove(), 600);
  }

  /**
   * Setup accessibility features
   */
  setupAccessibility() {
    // Add keyboard navigation for modals
    document.addEventListener('keydown', (e) => {
      // Tab trapping for modals
      if (e.key === 'Tab' && this.modals.size > 0) {
        // Get active modal
        const activeModal = Array.from(this.modals.values())
          .map(m => m.modal)
          .find(m => m.classList.contains('active'));

        if (activeModal) {
          const focusableElements = activeModal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          );
          
          const firstElement = focusableElements[0];
          const lastElement = focusableElements[focusableElements.length - 1];

          if (e.shiftKey && document.activeElement === firstElement) {
            lastElement.focus();
            e.preventDefault();
          } else if (!e.shiftKey && document.activeElement === lastElement) {
            firstElement.focus();
            e.preventDefault();
          }
        }
      }
    });
  }

  /**
   * Escape HTML to prevent XSS
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Animate element entrance
   */
  animateIn(element, animation = 'fadeIn') {
    if (typeof element === 'string') {
      element = document.getElementById(element);
    }
    if (!element) return;

    element.style.animation = `${animation} 0.3s ease-out`;
  }

  /**
   * Smooth scroll to element
   */
  scrollTo(elementId, offset = 0) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const top = element.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({
      top,
      behavior: 'smooth'
    });
  }

  /**
   * Copy text to clipboard
   */
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      this.showToast('Copied to clipboard!', 'success', 2000);
      return true;
    } catch (err) {
      this.showToast('Failed to copy', 'error');
      return false;
    }
  }

  /**
   * Format number with locale
   */
  formatNumber(number, decimals = 2) {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(number);
  }

  /**
   * Format currency
   */
  formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency
    }).format(amount);
  }

  /**
   * Format relative time
   */
  formatRelativeTime(timestamp) {
    const now = Date.now();
    const diff = now - timestamp;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (seconds < 60) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return new Date(timestamp).toLocaleDateString();
  }
}

// Create global instance
const uiManager = new UIManager();

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { UIManager, uiManager };
}

// Make available globally
window.uiManager = uiManager;
window.UIManager = UIManager;

// Add CSS for ripple animation
const style = document.createElement('style');
style.textContent = `
  @keyframes ripple {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(1rem);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes slideOutRight {
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

console.log('✅ UI Manager loaded and ready');
