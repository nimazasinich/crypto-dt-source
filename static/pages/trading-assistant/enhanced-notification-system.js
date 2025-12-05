/**
 * Enhanced Notification System
 * Multi-channel notifications with retry logic
 * Supports: Telegram, Email, Browser Push, WebSocket
 */

/**
 * Notification priorities
 */
export const NOTIFICATION_PRIORITY = {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
    URGENT: 'urgent'
};

/**
 * Notification channels
 */
export const NOTIFICATION_CHANNELS = {
    TELEGRAM: 'telegram',
    EMAIL: 'email',
    BROWSER: 'browser',
    WEBSOCKET: 'websocket'
};

/**
 * Enhanced Notification Manager
 */
export class NotificationManager {
    constructor(config = {}) {
        this.enabled = config.enabled !== false;
        this.channels = config.channels || ['browser'];
        this.telegramConfig = config.telegram || null;
        this.emailConfig = config.email || null;
        this.retryAttempts = config.retryAttempts || 3;
        this.retryDelay = config.retryDelay || 5000;
        this.queue = [];
        this.processing = false;
        this.sent = [];
        this.failed = [];
        this.rateLimit = {
            maxPerMinute: 10,
            count: 0,
            resetTime: Date.now() + 60000
        };
    }

    /**
     * Send notification to all configured channels
     * @param {Object} notification - Notification object
     * @returns {Promise<Object>} Results from all channels
     */
    async send(notification) {
        if (!this.enabled) {
            console.log('[NotificationManager] Notifications disabled');
            return { success: false, reason: 'disabled' };
        }

        // Check rate limiting
        if (!this.checkRateLimit()) {
            console.warn('[NotificationManager] Rate limit exceeded');
            this.queue.push(notification);
            return { success: false, reason: 'rate_limited', queued: true };
        }

        // Validate notification
        const validated = this.validateNotification(notification);
        if (!validated.valid) {
            return { success: false, reason: validated.error };
        }

        // Enrich notification
        const enriched = this.enrichNotification(notification);

        // Send to all channels
        const results = {};

        for (const channel of this.channels) {
            try {
                results[channel] = await this.sendToChannel(enriched, channel);
            } catch (error) {
                console.error(`[NotificationManager] ${channel} error:`, error);
                results[channel] = { success: false, error: error.message };
            }
        }

        // Log results
        if (Object.values(results).some(r => r.success)) {
            this.sent.push({ ...enriched, timestamp: Date.now(), results });
        } else {
            this.failed.push({ ...enriched, timestamp: Date.now(), results });
        }

        return { success: true, results };
    }

    /**
     * Send trading signal notification
     * @param {Object} signal - Trading signal
     * @returns {Promise<Object>} Send results
     */
    async sendSignal(signal) {
        const priority = this.determineSignalPriority(signal);
        
        const notification = {
            type: 'signal',
            priority,
            title: `🚨 ${signal.strategy} - ${signal.signal.toUpperCase()}`,
            message: this.formatSignalMessage(signal),
            data: signal,
            action: {
                label: 'View Analysis',
                url: `/trading-assistant?symbol=${signal.symbol || 'BTC'}`
            }
        };

        return this.send(notification);
    }

    /**
     * Send error notification
     * @param {Error} error - Error object
     * @param {string} context - Error context
     * @returns {Promise<Object>} Send results
     */
    async sendError(error, context = 'Unknown') {
        const notification = {
            type: 'error',
            priority: NOTIFICATION_PRIORITY.HIGH,
            title: `⚠️ Error: ${context}`,
            message: `${error.message}\n\nTime: ${new Date().toLocaleString()}`,
            data: { error: error.message, stack: error.stack, context }
        };

        return this.send(notification);
    }

    /**
     * Send price alert notification
     * @param {Object} alert - Price alert
     * @returns {Promise<Object>} Send results
     */
    async sendPriceAlert(alert) {
        const notification = {
            type: 'price_alert',
            priority: NOTIFICATION_PRIORITY.MEDIUM,
            title: `💰 Price Alert: ${alert.symbol}`,
            message: `${alert.symbol} reached ${alert.targetPrice}\nCurrent: $${alert.currentPrice.toFixed(2)}`,
            data: alert
        };

        return this.send(notification);
    }

    /**
     * Send to specific channel
     * @param {Object} notification - Notification
     * @param {string} channel - Channel name
     * @returns {Promise<Object>} Channel result
     */
    async sendToChannel(notification, channel) {
        const handlers = {
            [NOTIFICATION_CHANNELS.TELEGRAM]: () => this.sendTelegram(notification),
            [NOTIFICATION_CHANNELS.EMAIL]: () => this.sendEmail(notification),
            [NOTIFICATION_CHANNELS.BROWSER]: () => this.sendBrowser(notification),
            [NOTIFICATION_CHANNELS.WEBSOCKET]: () => this.sendWebSocket(notification)
        };

        const handler = handlers[channel];
        if (!handler) {
            throw new Error(`Unknown channel: ${channel}`);
        }

        return this.retryOperation(() => handler(), this.retryAttempts);
    }

    /**
     * Send via Telegram
     * @param {Object} notification - Notification
     * @returns {Promise<Object>} Result
     */
    async sendTelegram(notification) {
        if (!this.telegramConfig || !this.telegramConfig.botToken || !this.telegramConfig.chatId) {
            return { success: false, error: 'Telegram not configured' };
        }

        const message = this.formatTelegramMessage(notification);
        
        try {
            // Validate Telegram config
            if (!this.telegramConfig.botToken || typeof this.telegramConfig.botToken !== 'string') {
                return { success: false, error: 'Invalid bot token' };
            }
            if (!this.telegramConfig.chatId || (typeof this.telegramConfig.chatId !== 'string' && typeof this.telegramConfig.chatId !== 'number')) {
                return { success: false, error: 'Invalid chat ID' };
            }
            
            const response = await fetch(
                `https://api.telegram.org/bot${this.telegramConfig.botToken}/sendMessage`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        chat_id: this.telegramConfig.chatId,
                        text: message,
                        parse_mode: 'HTML',
                        disable_web_page_preview: true
                    }),
                    signal: AbortSignal.timeout(10000)
                }
            );

            const data = await response.json();

            if (data.ok) {
                return { success: true, messageId: data.result.message_id };
            } else {
                return { success: false, error: data.description };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    /**
     * Send via Email (requires backend)
     * @param {Object} notification - Notification
     * @returns {Promise<Object>} Result
     */
    async sendEmail(notification) {
        if (!this.emailConfig || !this.emailConfig.to) {
            return { success: false, error: 'Email not configured' };
        }

        // Validate email config
        if (typeof this.emailConfig.to !== 'string' || this.emailConfig.to.length === 0) {
            return { success: false, error: 'Invalid email address' };
        }

        const baseUrl = window.location.origin; // Use relative URL for Hugging Face compatibility
        
        try {
            const response = await fetch(`${baseUrl}/api/notifications/email`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    to: this.emailConfig.to,
                    subject: notification.title || 'Notification',
                    body: notification.message || '',
                    data: notification.data || {}
                }),
                signal: AbortSignal.timeout(10000)
            });

            if (response.ok) {
                return { success: true };
            } else {
                return { success: false, error: `HTTP ${response.status}` };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    /**
     * Send browser notification
     * @param {Object} notification - Notification
     * @returns {Promise<Object>} Result
     */
    async sendBrowser(notification) {
        // Check if browser notifications are supported
        if (!('Notification' in window)) {
            return { success: false, error: 'Browser notifications not supported' };
        }

        // Request permission if needed
        if (Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            if (permission !== 'granted') {
                return { success: false, error: 'Permission denied' };
            }
        }

        if (Notification.permission !== 'granted') {
            return { success: false, error: 'Permission denied' };
        }

        try {
            const notif = new Notification(notification.title, {
                body: notification.message,
                icon: '/static/images/logo.png',
                badge: '/static/images/badge.png',
                tag: `${notification.type}-${Date.now()}`,
                requireInteraction: notification.priority === NOTIFICATION_PRIORITY.URGENT,
                silent: notification.priority === NOTIFICATION_PRIORITY.LOW
            });

            if (notification.action) {
                notif.onclick = () => {
                    window.focus();
                    if (notification.action.url) {
                        window.location.href = notification.action.url;
                    }
                    notif.close();
                };
            }

            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    /**
     * Send via WebSocket
     * @param {Object} notification - Notification
     * @returns {Promise<Object>} Result
     */
    async sendWebSocket(notification) {
        // This would connect to a WebSocket server for real-time delivery
        // For now, we'll use window events as a fallback
        try {
            window.dispatchEvent(new CustomEvent('notification', {
                detail: notification
            }));

            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    /**
     * Format Telegram message
     * @param {Object} notification - Notification
     * @returns {string} Formatted message
     */
    formatTelegramMessage(notification) {
        let message = `<b>${this.escapeHtml(notification.title)}</b>\n\n`;
        message += `${this.escapeHtml(notification.message)}\n\n`;

        if (notification.data) {
            if (notification.data.entry) {
                message += `<b>Entry:</b> $${notification.data.entry.toFixed(2)}\n`;
            }
            if (notification.data.stopLoss) {
                message += `<b>Stop Loss:</b> $${notification.data.stopLoss.toFixed(2)}\n`;
            }
            if (notification.data.targets && notification.data.targets.length > 0) {
                message += `<b>Targets:</b>\n`;
                notification.data.targets.forEach((t, i) => {
                    message += `  TP${i + 1}: $${t.level.toFixed(2)} (${t.percentage}%)\n`;
                });
            }
            if (notification.data.confidence) {
                message += `\n<b>Confidence:</b> ${notification.data.confidence.toFixed(0)}%\n`;
            }
        }

        message += `\n<i>${new Date().toLocaleString()}</i>`;

        return message;
    }

    /**
     * Format signal message
     * @param {Object} signal - Trading signal
     * @returns {string} Formatted message
     */
    formatSignalMessage(signal) {
        let message = `Signal: ${signal.signal.toUpperCase()}\n`;
        message += `Strategy: ${signal.strategy}\n`;
        message += `Confidence: ${signal.confidence?.toFixed(0) || 0}%\n\n`;

        if (signal.entry) {
            message += `Entry: $${signal.entry.toFixed(2)}\n`;
        }

        if (signal.stopLoss) {
            message += `Stop Loss: $${signal.stopLoss.toFixed(2)}\n`;
        }

        if (signal.targets && signal.targets.length > 0) {
            message += `\nTargets:\n`;
            signal.targets.forEach((t, i) => {
                message += `  TP${i + 1}: $${t.level.toFixed(2)}\n`;
            });
        }

        if (signal.riskRewardRatio) {
            message += `\nRisk/Reward: ${signal.riskRewardRatio}`;
        }

        return message;
    }

    /**
     * Determine signal priority
     * @param {Object} signal - Trading signal
     * @returns {string} Priority level
     */
    determineSignalPriority(signal) {
        const confidence = signal.confidence || 0;

        if (confidence >= 90 && signal.signal !== 'hold') {
            return NOTIFICATION_PRIORITY.URGENT;
        } else if (confidence >= 75 && signal.signal !== 'hold') {
            return NOTIFICATION_PRIORITY.HIGH;
        } else if (signal.signal !== 'hold') {
            return NOTIFICATION_PRIORITY.MEDIUM;
        } else {
            return NOTIFICATION_PRIORITY.LOW;
        }
    }

    /**
     * Validate notification
     * @param {Object} notification - Notification
     * @returns {Object} Validation result
     */
    validateNotification(notification) {
        if (!notification) {
            return { valid: false, error: 'Notification is null' };
        }

        if (!notification.title || typeof notification.title !== 'string') {
            return { valid: false, error: 'Invalid title' };
        }

        if (!notification.message || typeof notification.message !== 'string') {
            return { valid: false, error: 'Invalid message' };
        }

        return { valid: true };
    }

    /**
     * Enrich notification with metadata
     * @param {Object} notification - Notification
     * @returns {Object} Enriched notification
     */
    enrichNotification(notification) {
        return {
            ...notification,
            id: this.generateId(),
            timestamp: Date.now(),
            priority: notification.priority || NOTIFICATION_PRIORITY.MEDIUM,
            type: notification.type || 'info'
        };
    }

    /**
     * Check rate limiting
     * @returns {boolean} Whether sending is allowed
     */
    checkRateLimit() {
        const now = Date.now();

        if (now >= this.rateLimit.resetTime) {
            this.rateLimit.count = 0;
            this.rateLimit.resetTime = now + 60000;
        }

        if (this.rateLimit.count >= this.rateLimit.maxPerMinute) {
            return false;
        }

        this.rateLimit.count++;
        return true;
    }

    /**
     * Retry operation with exponential backoff
     * @param {Function} operation - Operation to retry
     * @param {number} attempts - Number of attempts
     * @returns {Promise<any>} Operation result
     */
    async retryOperation(operation, attempts) {
        for (let i = 0; i < attempts; i++) {
            try {
                return await operation();
            } catch (error) {
                if (i === attempts - 1) {
                    throw error;
                }
                
                const delay = this.retryDelay * Math.pow(2, i);
                console.log(`[NotificationManager] Retry ${i + 1}/${attempts} after ${delay}ms`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }

    /**
     * Process queued notifications
     */
    async processQueue() {
        if (this.processing || this.queue.length === 0) {
            return;
        }

        this.processing = true;

        while (this.queue.length > 0) {
            if (!this.checkRateLimit()) {
                await new Promise(resolve => setTimeout(resolve, 10000));
                continue;
            }

            const notification = this.queue.shift();
            await this.send(notification);
        }

        this.processing = false;
    }

    /**
     * Escape HTML for Telegram
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    /**
     * Generate unique ID
     * @returns {string} Unique ID
     */
    generateId() {
        return `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Get notification history
     * @param {number} limit - Maximum number of notifications
     * @returns {Array<Object>} Recent notifications
     */
    getHistory(limit = 50) {
        return this.sent.slice(-limit).reverse();
    }

    /**
     * Get failed notifications
     * @returns {Array<Object>} Failed notifications
     */
    getFailed() {
        return this.failed.slice(-20).reverse();
    }

    /**
     * Clear history
     */
    clearHistory() {
        this.sent = [];
        this.failed = [];
    }

    /**
     * Update configuration
     * @param {Object} config - New configuration
     */
    updateConfig(config) {
        if (config.enabled !== undefined) {
            this.enabled = config.enabled;
        }

        if (config.channels) {
            this.channels = config.channels;
        }

        if (config.telegram) {
            this.telegramConfig = config.telegram;
        }

        if (config.email) {
            this.emailConfig = config.email;
        }
    }

    /**
     * Test notification system
     * @returns {Promise<Object>} Test results
     */
    async test() {
        const testNotification = {
            type: 'test',
            priority: NOTIFICATION_PRIORITY.LOW,
            title: '✅ Test Notification',
            message: 'This is a test notification from the Enhanced Notification System',
            data: { test: true, timestamp: Date.now() }
        };

        return this.send(testNotification);
    }
}

export default NotificationManager;

