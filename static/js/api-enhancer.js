// Enhanced API Client with Caching, Retry Logic, and Better Error Handling
class EnhancedAPIClient {
    constructor() {
        this.cache = new Map();
        this.cacheExpiry = new Map();
        this.defaultCacheDuration = 30000; // 30 seconds
        this.maxRetries = 3;
        this.retryDelay = 1000; // 1 second
    }

    /**
     * Fetch with automatic retry and exponential backoff
     */
    async fetchWithRetry(url, options = {}, retries = this.maxRetries) {
        try {
            const response = await fetch(url, options);

            // If response is ok, return it
            if (response.ok) {
                return response;
            }

            // If we get a 429 (rate limit) or 5xx error, retry
            if ((response.status === 429 || response.status >= 500) && retries > 0) {
                const delay = this.retryDelay * (this.maxRetries - retries + 1);
                console.warn(`Request failed with status ${response.status}, retrying in ${delay}ms... (${retries} retries left)`);
                await this.sleep(delay);
                return this.fetchWithRetry(url, options, retries - 1);
            }

            // Otherwise throw error
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        } catch (error) {
            // Network error - retry if we have retries left
            if (retries > 0 && error.name === 'TypeError') {
                const delay = this.retryDelay * (this.maxRetries - retries + 1);
                console.warn(`Network error, retrying in ${delay}ms... (${retries} retries left)`);
                await this.sleep(delay);
                return this.fetchWithRetry(url, options, retries - 1);
            }

            throw error;
        }
    }

    /**
     * Get data with caching support
     */
    async get(url, options = {}) {
        const cacheKey = url + JSON.stringify(options);
        const cacheDuration = options.cacheDuration || this.defaultCacheDuration;

        // Check cache
        if (options.cache !== false && this.isCacheValid(cacheKey)) {
            console.log(`📦 Cache hit for ${url}`);
            return this.cache.get(cacheKey);
        }

        try {
            const response = await this.fetchWithRetry(url, {
                ...options,
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            const data = await response.json();

            // Store in cache
            if (options.cache !== false) {
                this.cache.set(cacheKey, data);
                this.cacheExpiry.set(cacheKey, Date.now() + cacheDuration);
            }

            return data;
        } catch (error) {
            console.error(`❌ GET request failed for ${url}:`, error);
            throw error;
        }
    }

    /**
     * Post data without caching
     */
    async post(url, body = {}, options = {}) {
        try {
            const response = await this.fetchWithRetry(url, {
                ...options,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: JSON.stringify(body)
            });

            return await response.json();
        } catch (error) {
            console.error(`❌ POST request failed for ${url}:`, error);
            throw error;
        }
    }

    /**
     * Check if cache is valid
     */
    isCacheValid(key) {
        if (!this.cache.has(key)) return false;

        const expiry = this.cacheExpiry.get(key);
        if (!expiry || Date.now() > expiry) {
            this.cache.delete(key);
            this.cacheExpiry.delete(key);
            return false;
        }

        return true;
    }

    /**
     * Clear all cache
     */
    clearCache() {
        this.cache.clear();
        this.cacheExpiry.clear();
        console.log('🗑️ Cache cleared');
    }

    /**
     * Clear specific cache entry
     */
    clearCacheEntry(url) {
        const keysToDelete = [];
        for (const key of this.cache.keys()) {
            if (key.startsWith(url)) {
                keysToDelete.push(key);
            }
        }
        keysToDelete.forEach(key => {
            this.cache.delete(key);
            this.cacheExpiry.delete(key);
        });
    }

    /**
     * Sleep utility
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Batch requests with rate limiting
     */
    async batchRequest(urls, options = {}) {
        const batchSize = options.batchSize || 5;
        const delay = options.delay || 100;
        const results = [];

        for (let i = 0; i < urls.length; i += batchSize) {
            const batch = urls.slice(i, i + batchSize);
            const batchPromises = batch.map(url => this.get(url, options));
            const batchResults = await Promise.allSettled(batchPromises);

            results.push(...batchResults);

            // Delay between batches
            if (i + batchSize < urls.length) {
                await this.sleep(delay);
            }
        }

        return results;
    }
}

// Create global instance
window.apiClient = new EnhancedAPIClient();

// Enhanced notification system with toast-style notifications
class NotificationManager {
    constructor() {
        this.container = null;
        this.createContainer();
    }

    createContainer() {
        if (document.getElementById('notification-container')) return;

        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        `;
        document.body.appendChild(container);
        this.container = container;
    }

    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `notification-toast notification-${type}`;

        const icons = {
            success: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
            error: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`,
            warning: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
            info: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`
        };

        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <div class="notification-icon">${icons[type] || icons.info}</div>
                <div class="notification-message">${message}</div>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
        `;

        toast.style.cssText = `
            min-width: 300px;
            max-width: 500px;
            padding: 16px 20px;
            background: rgba(17, 24, 39, 0.95);
            backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid ${this.getBorderColor(type)};
            border-left: 4px solid ${this.getBorderColor(type)};
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            color: var(--text-primary);
            animation: slideInRight 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            pointer-events: all;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        `;

        this.container.appendChild(toast);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                toast.style.animation = 'slideOutRight 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
    }

    getBorderColor(type) {
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        return colors[type] || colors.info;
    }
}

// Create global notification manager
window.notificationManager = new NotificationManager();

// Enhanced show functions
window.showSuccess = (message) => window.notificationManager.show(message, 'success');
window.showError = (message) => window.notificationManager.show(message, 'error');
window.showWarning = (message) => window.notificationManager.show(message, 'warning');
window.showInfo = (message) => window.notificationManager.show(message, 'info');

// Add notification styles
const style = document.createElement('style');
style.textContent = `
@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(100px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes slideOutRight {
    from {
        opacity: 1;
        transform: translateX(0);
    }
    to {
        opacity: 0;
        transform: translateX(100px);
    }
}

.notification-toast:hover {
    transform: translateX(-4px);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5);
}

.notification-close {
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.2s;
}

.notification-close:hover {
    background: rgba(255, 255, 255, 0.1);
    color: var(--text-primary);
}

.notification-icon {
    display: flex;
    align-items: center;
    justify-content: center;
}

.notification-message {
    flex: 1;
    font-size: 14px;
    line-height: 1.5;
}

.notification-success .notification-icon {
    color: #10b981;
}

.notification-error .notification-icon {
    color: #ef4444;
}

.notification-warning .notification-icon {
    color: #f59e0b;
}

.notification-info .notification-icon {
    color: #3b82f6;
}
`;
document.head.appendChild(style);

console.log('✅ Enhanced API Client and Notification Manager loaded');
