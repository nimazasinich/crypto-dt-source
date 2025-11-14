/**
 * Theme Manager - Dark/Light Mode Toggle
 * Crypto Monitor HF - Enterprise Edition
 */

class ThemeManager {
    constructor() {
        this.storageKey = 'crypto_monitor_theme';
        this.currentTheme = 'light';
        this.listeners = [];
    }

    /**
     * Initialize theme system
     */
    init() {
        // Load saved theme or detect system preference
        this.currentTheme = this.getSavedTheme() || this.getSystemPreference();

        // Apply theme
        this.applyTheme(this.currentTheme, false);

        // Set up theme toggle button
        this.setupToggleButton();

        // Listen for system theme changes
        this.listenToSystemChanges();

        console.log(`[ThemeManager] Initialized with theme: ${this.currentTheme}`);
    }

    /**
     * Get saved theme from localStorage
     */
    getSavedTheme() {
        try {
            return localStorage.getItem(this.storageKey);
        } catch (error) {
            console.warn('[ThemeManager] localStorage not available:', error);
            return null;
        }
    }

    /**
     * Save theme to localStorage
     */
    saveTheme(theme) {
        try {
            localStorage.setItem(this.storageKey, theme);
        } catch (error) {
            console.warn('[ThemeManager] Could not save theme:', error);
        }
    }

    /**
     * Get system theme preference
     */
    getSystemPreference() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    /**
     * Apply theme to document
     */
    applyTheme(theme, save = true) {
        const body = document.body;

        // Remove existing theme classes
        body.classList.remove('theme-light', 'theme-dark');

        // Add new theme class
        body.classList.add(`theme-${theme}`);

        // Update current theme
        this.currentTheme = theme;

        // Save to localStorage
        if (save) {
            this.saveTheme(theme);
        }

        // Update toggle button
        this.updateToggleButton(theme);

        // Notify listeners
        this.notifyListeners(theme);

        // Announce to screen readers
        this.announceThemeChange(theme);

        console.log(`[ThemeManager] Applied theme: ${theme}`);
    }

    /**
     * Toggle between light and dark themes
     */
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    /**
     * Set specific theme
     */
    setTheme(theme) {
        if (theme !== 'light' && theme !== 'dark') {
            console.warn(`[ThemeManager] Invalid theme: ${theme}`);
            return;
        }
        this.applyTheme(theme);
    }

    /**
     * Get current theme
     */
    getTheme() {
        return this.currentTheme;
    }

    /**
     * Set up theme toggle button
     */
    setupToggleButton() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.toggleTheme();
            });

            // Keyboard support
            toggleBtn.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggleTheme();
                }
            });

            // Initial state
            this.updateToggleButton(this.currentTheme);
        }
    }

    /**
     * Update toggle button appearance
     */
    updateToggleButton(theme) {
        const toggleBtn = document.getElementById('theme-toggle');
        const toggleIcon = document.getElementById('theme-toggle-icon');

        if (toggleBtn && toggleIcon) {
            if (theme === 'dark') {
                toggleIcon.textContent = '☀️';
                toggleBtn.setAttribute('aria-label', 'Switch to light mode');
                toggleBtn.setAttribute('title', 'Light Mode');
            } else {
                toggleIcon.textContent = '🌙';
                toggleBtn.setAttribute('aria-label', 'Switch to dark mode');
                toggleBtn.setAttribute('title', 'Dark Mode');
            }
        }
    }

    /**
     * Listen for system theme changes
     */
    listenToSystemChanges() {
        if (window.matchMedia) {
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

            // Modern browsers
            if (darkModeQuery.addEventListener) {
                darkModeQuery.addEventListener('change', (e) => {
                    // Only auto-change if user hasn't manually set a preference
                    if (!this.getSavedTheme()) {
                        const newTheme = e.matches ? 'dark' : 'light';
                        this.applyTheme(newTheme, false);
                    }
                });
            }
            // Older browsers
            else if (darkModeQuery.addListener) {
                darkModeQuery.addListener((e) => {
                    if (!this.getSavedTheme()) {
                        const newTheme = e.matches ? 'dark' : 'light';
                        this.applyTheme(newTheme, false);
                    }
                });
            }
        }
    }

    /**
     * Register change listener
     */
    onChange(callback) {
        this.listeners.push(callback);
        return () => {
            const index = this.listeners.indexOf(callback);
            if (index > -1) {
                this.listeners.splice(index, 1);
            }
        };
    }

    /**
     * Notify all listeners
     */
    notifyListeners(theme) {
        this.listeners.forEach(callback => {
            try {
                callback(theme);
            } catch (error) {
                console.error('[ThemeManager] Error in listener:', error);
            }
        });
    }

    /**
     * Announce theme change to screen readers
     */
    announceThemeChange(theme) {
        const liveRegion = document.getElementById('sr-live-region');
        if (liveRegion) {
            liveRegion.textContent = `Theme changed to ${theme} mode`;
        }
    }

    /**
     * Reset to system preference
     */
    resetToSystem() {
        try {
            localStorage.removeItem(this.storageKey);
        } catch (error) {
            console.warn('[ThemeManager] Could not remove saved theme:', error);
        }

        const systemTheme = this.getSystemPreference();
        this.applyTheme(systemTheme, false);
    }
}

// Create global instance
window.themeManager = new ThemeManager();

// Auto-initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager.init();
});

console.log('[ThemeManager] Module loaded');
