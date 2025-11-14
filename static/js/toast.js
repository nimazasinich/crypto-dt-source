/**
 * ============================================
 * TOAST NOTIFICATION SYSTEM
 * Enterprise Edition - Crypto Monitor Ultimate
 * ============================================
 *
 * Beautiful toast notifications with:
 * - Multiple types (success, error, warning, info)
 * - Auto-dismiss
 * - Progress bar
 * - Stack management
 * - Accessibility support
 */

class ToastManager {
    constructor() {
        this.toasts = [];
        this.container = null;
        this.maxToasts = 5;
        this.defaultDuration = 5000;
        this.init();
    }

    /**
     * Initialize toast container
     */
    init() {
        // Create container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            this.container.setAttribute('role', 'region');
            this.container.setAttribute('aria-label', 'Notifications');
            this.container.setAttribute('aria-live', 'polite');
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toast-container');
        }

        console.log('[Toast] Toast manager initialized');
    }

    /**
     * Show a toast notification
     * @param {string} message - Toast message
     * @param {string} type - Toast type (success, error, warning, info)
     * @param {object} options - Additional options
     */
    show(message, type = 'info', options = {}) {
        const {
            duration = this.defaultDuration,
            title = null,
            icon = null,
            dismissible = true,
            action = null
        } = options;

        // Remove oldest toast if max reached
        if (this.toasts.length >= this.maxToasts) {
            this.dismiss(this.toasts[0].id);
        }

        const toast = {
            id: this.generateId(),
            message,
            type,
            title,
            icon: icon || this.getDefaultIcon(type),
            dismissible,
            action,
            duration,
            createdAt: Date.now()
        };

        this.toasts.push(toast);
        this.render(toast);

        // Auto dismiss if duration is set
        if (duration > 0) {
            setTimeout(() => this.dismiss(toast.id), duration);
        }

        return toast.id;
    }

    /**
     * Show success toast
     */
    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    /**
     * Show error toast
     */
    error(message, options = {}) {
        return this.show(message, 'error', { ...options, duration: options.duration || 7000 });
    }

    /**
     * Show warning toast
     */
    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }

    /**
     * Show info toast
     */
    info(message, options = {}) {
        return this.show(message, 'info', options);
    }

    /**
     * Dismiss a toast
     */
    dismiss(toastId) {
        const toastElement = document.getElementById(`toast-${toastId}`);
        if (!toastElement) return;

        // Add exit animation
        toastElement.classList.add('toast-exit');

        setTimeout(() => {
            toastElement.remove();
            this.toasts = this.toasts.filter(t => t.id !== toastId);
        }, 300);
    }

    /**
     * Dismiss all toasts
     */
    dismissAll() {
        const toastIds = this.toasts.map(t => t.id);
        toastIds.forEach(id => this.dismiss(id));
    }

    /**
     * Render a toast
     */
    render(toast) {
        const toastElement = document.createElement('div');
        toastElement.id = `toast-${toast.id}`;
        toastElement.className = `toast toast-${toast.type} glass-effect`;
        toastElement.setAttribute('role', 'alert');
        toastElement.setAttribute('aria-atomic', 'true');

        const iconHtml = window.getIcon
            ? window.getIcon(toast.icon, 24)
            : '';

        const titleHtml = toast.title
            ? `<div class="toast-title">${toast.title}</div>`
            : '';

        const actionHtml = toast.action
            ? `<button class="toast-action" onclick="${toast.action.onClick}">${toast.action.label}</button>`
            : '';

        const closeButton = toast.dismissible
            ? `<button class="toast-close" onclick="window.toastManager.dismiss('${toast.id}')" aria-label="Close notification">
                ${window.getIcon ? window.getIcon('close', 20) : '×'}
            </button>`
            : '';

        const progressBar = toast.duration > 0
            ? `<div class="toast-progress" style="animation-duration: ${toast.duration}ms"></div>`
            : '';

        toastElement.innerHTML = `
            <div class="toast-icon">
                ${iconHtml}
            </div>
            <div class="toast-content">
                ${titleHtml}
                <div class="toast-message">${toast.message}</div>
                ${actionHtml}
            </div>
            ${closeButton}
            ${progressBar}
        `;

        this.container.appendChild(toastElement);

        // Trigger entrance animation
        setTimeout(() => toastElement.classList.add('toast-enter'), 10);
    }

    /**
     * Get default icon for type
     */
    getDefaultIcon(type) {
        const icons = {
            success: 'checkCircle',
            error: 'alertCircle',
            warning: 'alertCircle',
            info: 'info'
        };
        return icons[type] || 'info';
    }

    /**
     * Generate unique ID
     */
    generateId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Show provider error toast
     */
    showProviderError(providerName, error) {
        return this.error(
            `Failed to connect to ${providerName}`,
            {
                title: 'Provider Error',
                duration: 7000,
                action: {
                    label: 'Retry',
                    onClick: `window.providerDiscovery.checkProviderHealth('${providerName}')`
                }
            }
        );
    }

    /**
     * Show provider success toast
     */
    showProviderSuccess(providerName) {
        return this.success(
            `Successfully connected to ${providerName}`,
            {
                title: 'Provider Online',
                duration: 3000
            }
        );
    }

    /**
     * Show API rate limit warning
     */
    showRateLimitWarning(providerName, retryAfter) {
        return this.warning(
            `Rate limit reached for ${providerName}. Retry after ${retryAfter}s`,
            {
                title: 'Rate Limit',
                duration: 6000
            }
        );
    }
}

// Export singleton instance
window.toastManager = new ToastManager();

// Utility shortcuts
window.showToast = (message, type, options) => window.toastManager.show(message, type, options);
window.toast = {
    success: (msg, opts) => window.toastManager.success(msg, opts),
    error: (msg, opts) => window.toastManager.error(msg, opts),
    warning: (msg, opts) => window.toastManager.warning(msg, opts),
    info: (msg, opts) => window.toastManager.info(msg, opts)
};

console.log('[Toast] Toast notification system ready');
