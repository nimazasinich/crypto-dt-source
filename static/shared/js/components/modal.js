/**
 * Modal Dialog Component
 */

export class Modal {
  constructor(options = {}) {
    this.id = options.id || `modal-${Date.now()}`;
    this.title = options.title || '';
    this.content = options.content || '';
    this.size = options.size || 'medium'; // small, medium, large
    this.closeOnBackdrop = options.closeOnBackdrop !== false;
    this.closeOnEscape = options.closeOnEscape !== false;
    this.onClose = options.onClose || null;
    this.element = null;
    this.backdrop = null;
  }

  /**
   * Show the modal
   */
  show() {
    if (this.element) {
      console.warn('[Modal] Modal already open');
      return;
    }

    // Create backdrop
    this.backdrop = document.createElement('div');
    this.backdrop.className = 'modal-backdrop';
    if (this.closeOnBackdrop) {
      this.backdrop.addEventListener('click', () => this.hide());
    }

    // Create modal
    this.element = document.createElement('div');
    this.element.className = `modal modal-${this.size}`;
    this.element.setAttribute('role', 'dialog');
    this.element.setAttribute('aria-modal', 'true');
    this.element.setAttribute('aria-labelledby', `${this.id}-title`);

    this.element.innerHTML = `
      <div class="modal-dialog">
        <div class="modal-header">
          <h2 class="modal-title" id="${this.id}-title">${this.escapeHtml(this.title)}</h2>
          <button class="modal-close" aria-label="Close modal">&times;</button>
        </div>
        <div class="modal-body">
          ${this.content}
        </div>
      </div>
    `;

    // Close button handler
    const closeBtn = this.element.querySelector('.modal-close');
    closeBtn.addEventListener('click', () => this.hide());

    // Escape key handler
    if (this.closeOnEscape) {
      this.escapeHandler = (e) => {
        if (e.key === 'Escape') this.hide();
      };
      document.addEventListener('keydown', this.escapeHandler);
    }

    // Append to body
    document.body.appendChild(this.backdrop);
    document.body.appendChild(this.element);

    // Trigger animation
    setTimeout(() => {
      this.backdrop.classList.add('show');
      this.element.classList.add('show');
    }, 10);

    // Prevent body scroll
    document.body.style.overflow = 'hidden';

    // Focus first focusable element
    this.trapFocus();
  }

  /**
   * Hide the modal
   */
  hide() {
    if (!this.element) return;

    // Remove animations
    this.backdrop.classList.remove('show');
    this.element.classList.remove('show');

    // Remove after animation
    setTimeout(() => {
      if (this.backdrop && this.backdrop.parentNode) {
        this.backdrop.parentNode.removeChild(this.backdrop);
      }
      if (this.element && this.element.parentNode) {
        this.element.parentNode.removeChild(this.element);
      }
      this.backdrop = null;
      this.element = null;

      // Restore body scroll
      document.body.style.overflow = '';

      // Remove escape handler
      if (this.escapeHandler) {
        document.removeEventListener('keydown', this.escapeHandler);
      }

      // Call onClose callback
      if (this.onClose) {
        this.onClose();
      }
    }, 300);
  }

  /**
   * Update modal content
   */
  setContent(html) {
    if (!this.element) return;
    const body = this.element.querySelector('.modal-body');
    if (body) {
      body.innerHTML = html;
    }
  }

  /**
   * Trap focus inside modal
   */
  trapFocus() {
    const focusable = this.element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    if (focusable.length === 0) return;

    const firstFocusable = focusable[0];
    const lastFocusable = focusable[focusable.length - 1];

    firstFocusable.focus();

    this.element.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey && document.activeElement === firstFocusable) {
          lastFocusable.focus();
          e.preventDefault();
        } else if (!e.shiftKey && document.activeElement === lastFocusable) {
          firstFocusable.focus();
          e.preventDefault();
        }
      }
    });
  }

  /**
   * Escape HTML
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Create confirmation dialog
   */
  static confirm(message, onConfirm, onCancel) {
    const modal = new Modal({
      title: 'Confirm',
      content: `
        <p>${message}</p>
        <div class="modal-actions">
          <button class="btn btn-secondary" id="modal-cancel">Cancel</button>
          <button class="btn btn-primary" id="modal-confirm">Confirm</button>
        </div>
      `,
      size: 'small',
    });

    modal.show();

    // Bind buttons
    setTimeout(() => {
      const confirmBtn = document.getElementById('modal-confirm');
      const cancelBtn = document.getElementById('modal-cancel');

      if (confirmBtn) {
        confirmBtn.addEventListener('click', () => {
          modal.hide();
          if (onConfirm) onConfirm();
        });
      }

      if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
          modal.hide();
          if (onCancel) onCancel();
        });
      }
    }, 50);

    return modal;
  }
}

export default Modal;
