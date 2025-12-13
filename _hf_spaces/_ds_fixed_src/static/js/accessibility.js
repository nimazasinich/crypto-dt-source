/**
 * ============================================
 * ACCESSIBILITY ENHANCEMENTS
 * Keyboard navigation, focus management, announcements
 * ============================================
 */

class AccessibilityManager {
    constructor() {
        this.init();
    }

    init() {
        this.detectInputMethod();
        this.setupKeyboardNavigation();
        this.setupAnnouncements();
        this.setupFocusManagement();
        console.log('[A11y] Accessibility manager initialized');
    }

    /**
     * Detect if user is using keyboard or mouse
     */
    detectInputMethod() {
        // Track mouse usage
        document.addEventListener('mousedown', () => {
            document.body.classList.add('using-mouse');
        });

        // Track keyboard usage
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.remove('using-mouse');
            }
        });
    }

    /**
     * Setup keyboard navigation shortcuts
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K: Focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('[role="searchbox"], input[type="search"]');
                if (searchInput) searchInput.focus();
            }

            // Escape: Close modals/dropdowns
            if (e.key === 'Escape') {
                this.closeAllModals();
                this.closeAllDropdowns();
            }

            // Arrow keys for tab navigation
            if (e.target.getAttribute('role') === 'tab') {
                this.handleTabNavigation(e);
            }
        });
    }

    /**
     * Handle tab navigation with arrow keys
     */
    handleTabNavigation(e) {
        const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
        const currentIndex = tabs.indexOf(e.target);

        let nextIndex;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
            nextIndex = (currentIndex + 1) % tabs.length;
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
        }

        if (nextIndex !== undefined) {
            e.preventDefault();
            tabs[nextIndex].focus();
            tabs[nextIndex].click();
        }
    }

    /**
     * Setup screen reader announcements
     */
    setupAnnouncements() {
        // Create announcement regions if they don't exist
        if (!document.getElementById('aria-live-polite')) {
            const polite = document.createElement('div');
            polite.id = 'aria-live-polite';
            polite.setAttribute('aria-live', 'polite');
            polite.setAttribute('aria-atomic', 'true');
            polite.className = 'sr-only';
            document.body.appendChild(polite);
        }

        if (!document.getElementById('aria-live-assertive')) {
            const assertive = document.createElement('div');
            assertive.id = 'aria-live-assertive';
            assertive.setAttribute('aria-live', 'assertive');
            assertive.setAttribute('aria-atomic', 'true');
            assertive.className = 'sr-only';
            document.body.appendChild(assertive);
        }
    }

    /**
     * Announce message to screen readers
     */
    announce(message, priority = 'polite') {
        const region = document.getElementById(`aria-live-${priority}`);
        if (!region) return;

        // Clear and set new message
        region.textContent = '';
        setTimeout(() => {
            region.textContent = message;
        }, 100);
    }

    /**
     * Setup focus management
     */
    setupFocusManagement() {
        // Trap focus in modals
        document.addEventListener('focusin', (e) => {
            const modal = document.querySelector('.modal-backdrop');
            if (!modal) return;

            const focusableElements = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );

            if (focusableElements.length === 0) return;

            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            if (!modal.contains(e.target)) {
                firstElement.focus();
            }
        });

        // Handle Tab key in modals
        document.addEventListener('keydown', (e) => {
            if (e.key !== 'Tab') return;

            const modal = document.querySelector('.modal-backdrop');
            if (!modal) return;

            const focusableElements = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );

            if (focusableElements.length === 0) return;

            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        });
    }

    /**
     * Close all modals
     */
    closeAllModals() {
        document.querySelectorAll('.modal-backdrop').forEach(modal => {
            modal.remove();
        });
    }

    /**
     * Close all dropdowns
     */
    closeAllDropdowns() {
        document.querySelectorAll('[aria-expanded="true"]').forEach(element => {
            element.setAttribute('aria-expanded', 'false');
        });
    }

    /**
     * Set page title (announces to screen readers)
     */
    setPageTitle(title) {
        document.title = title;
        this.announce(`Page: ${title}`);
    }

    /**
     * Add skip link
     */
    addSkipLink() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-link';
        skipLink.textContent = 'Skip to main content';
        document.body.insertBefore(skipLink, document.body.firstChild);

        // Add id to main content if it doesn't exist
        const mainContent = document.querySelector('.main-content, main');
        if (mainContent && !mainContent.id) {
            mainContent.id = 'main-content';
        }
    }

    /**
     * Mark element as loading
     */
    markAsLoading(element, label = 'Loading') {
        element.setAttribute('aria-busy', 'true');
        element.setAttribute('aria-label', label);
    }

    /**
     * Unmark element as loading
     */
    unmarkAsLoading(element) {
        element.setAttribute('aria-busy', 'false');
        element.removeAttribute('aria-label');
    }
}

// Export singleton
window.a11y = new AccessibilityManager();

// Utility functions
window.announce = (message, priority) => window.a11y.announce(message, priority);
