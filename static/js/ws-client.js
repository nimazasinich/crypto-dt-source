/**
 * WebSocket Client - Real-time Updates with Proper Cleanup
 * Crypto Monitor HF - Enterprise Edition
 */

class CryptoWebSocketClient {
    constructor(url = null) {
        this.url = url || `ws://${window.location.host}/ws`;
        this.ws = null;
        this.sessionId = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.reconnectTimer = null;
        this.heartbeatTimer = null;

        // Event handlers stored for cleanup
        this.messageHandlers = new Map();
        this.connectionCallbacks = [];

        // Auto-connect
        this.connect();
    }

    /**
     * Connect to WebSocket server
     */
    connect() {
        // Clean up existing connection
        this.disconnect();

        try {
            console.log('[WebSocket] Connecting to:', this.url);
            this.ws = new WebSocket(this.url);

            // Bind event handlers
            this.ws.onopen = this.handleOpen.bind(this);
            this.ws.onmessage = this.handleMessage.bind(this);
            this.ws.onerror = this.handleError.bind(this);
            this.ws.onclose = this.handleClose.bind(this);

        } catch (error) {
            console.error('[WebSocket] Connection error:', error);
            this.scheduleReconnect();
        }
    }

    /**
     * Disconnect and cleanup
     */
    disconnect() {
        // Clear timers
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }

        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }

        // Close WebSocket
        if (this.ws) {
            this.ws.onopen = null;
            this.ws.onmessage = null;
            this.ws.onerror = null;
            this.ws.onclose = null;

            if (this.ws.readyState === WebSocket.OPEN) {
                this.ws.close();
            }

            this.ws = null;
        }

        this.isConnected = false;
        this.sessionId = null;
    }

    /**
     * Handle WebSocket open event
     */
    handleOpen(event) {
        console.log('[WebSocket] Connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;

        // Notify connection callbacks
        this.notifyConnection(true);

        // Update UI
        this.updateConnectionStatus(true);

        // Start heartbeat
        this.startHeartbeat();
    }

    /**
     * Handle WebSocket message event
     */
    handleMessage(event) {
        try {
            const message = JSON.parse(event.data);
            const type = message.type;

            console.log('[WebSocket] Received message type:', type);

            // Handle system messages
            switch (type) {
                case 'welcome':
                    this.sessionId = message.session_id;
                    console.log('[WebSocket] Session ID:', this.sessionId);
                    break;

                case 'heartbeat':
                    this.send({ type: 'pong' });
                    break;

                case 'stats_update':
                    this.handleStatsUpdate(message.data);
                    break;

                case 'provider_stats':
                    this.handleProviderStats(message.data);
                    break;

                case 'market_update':
                    this.handleMarketUpdate(message.data);
                    break;

                case 'price_update':
                    this.handlePriceUpdate(message.data);
                    break;

                case 'alert':
                    this.handleAlert(message.data);
                    break;
            }

            // Call registered handler if exists
            const handler = this.messageHandlers.get(type);
            if (handler) {
                handler(message);
            }

        } catch (error) {
            console.error('[WebSocket] Error processing message:', error);
        }
    }

    /**
     * Handle WebSocket error event
     */
    handleError(error) {
        console.error('[WebSocket] Error:', error);
        this.isConnected = false;
        this.updateConnectionStatus(false);
    }

    /**
     * Handle WebSocket close event
     */
    handleClose(event) {
        console.log('[WebSocket] Disconnected');
        this.isConnected = false;
        this.sessionId = null;

        // Notify connection callbacks
        this.notifyConnection(false);

        // Update UI
        this.updateConnectionStatus(false);

        // Stop heartbeat
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }

        // Schedule reconnect
        this.scheduleReconnect();
    }

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`[WebSocket] Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            this.reconnectTimer = setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        } else {
            console.error('[WebSocket] Max reconnection attempts reached');
            this.showReconnectButton();
        }
    }

    /**
     * Start heartbeat to keep connection alive
     */
    startHeartbeat() {
        // Send ping every 30 seconds
        this.heartbeatTimer = setInterval(() => {
            if (this.isConnected) {
                this.send({ type: 'ping' });
            }
        }, 30000);
    }

    /**
     * Send message to server
     */
    send(data) {
        if (this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('[WebSocket] Cannot send - not connected');
        }
    }

    /**
     * Subscribe to message group
     */
    subscribe(group) {
        this.send({
            type: 'subscribe',
            group: group
        });
    }

    /**
     * Unsubscribe from message group
     */
    unsubscribe(group) {
        this.send({
            type: 'unsubscribe',
            group: group
        });
    }

    /**
     * Request stats update
     */
    requestStats() {
        this.send({
            type: 'get_stats'
        });
    }

    /**
     * Register message handler (with cleanup support)
     */
    on(type, handler) {
        this.messageHandlers.set(type, handler);

        // Return cleanup function
        return () => {
            this.messageHandlers.delete(type);
        };
    }

    /**
     * Remove message handler
     */
    off(type) {
        this.messageHandlers.delete(type);
    }

    /**
     * Register connection callback
     */
    onConnection(callback) {
        this.connectionCallbacks.push(callback);

        // Return cleanup function
        return () => {
            const index = this.connectionCallbacks.indexOf(callback);
            if (index > -1) {
                this.connectionCallbacks.splice(index, 1);
            }
        };
    }

    /**
     * Notify connection callbacks
     */
    notifyConnection(connected) {
        this.connectionCallbacks.forEach(callback => {
            try {
                callback(connected);
            } catch (error) {
                console.error('[WebSocket] Error in connection callback:', error);
            }
        });
    }

    // ===== Message Handlers =====

    handleStatsUpdate(data) {
        const activeConnections = data.active_connections || 0;
        const totalSessions = data.total_sessions || 0;

        this.updateOnlineUsers(activeConnections, totalSessions);

        if (data.client_types) {
            this.updateClientTypes(data.client_types);
        }
    }

    handleProviderStats(data) {
        if (window.dashboardApp && window.dashboardApp.updateProviderStats) {
            window.dashboardApp.updateProviderStats(data);
        }
    }

    handleMarketUpdate(data) {
        if (window.dashboardApp && window.dashboardApp.updateMarketData) {
            window.dashboardApp.updateMarketData(data);
        }
    }

    handlePriceUpdate(data) {
        if (window.dashboardApp && window.dashboardApp.updatePrice) {
            window.dashboardApp.updatePrice(data.symbol, data.price, data.change_24h);
        }
    }

    handleAlert(data) {
        this.showAlert(data.message, data.severity);
    }

    // ===== UI Updates =====

    updateConnectionStatus(connected) {
        const statusBar = document.querySelector('.connection-status-bar');
        const statusDot = document.getElementById('ws-status-dot');
        const statusText = document.getElementById('ws-status-text');

        if (statusBar) {
            if (connected) {
                statusBar.classList.remove('disconnected');
            } else {
                statusBar.classList.add('disconnected');
            }
        }

        if (statusDot) {
            statusDot.className = connected ? 'status-dot status-online' : 'status-dot status-offline';
        }

        if (statusText) {
            statusText.textContent = connected ? 'Connected' : 'Disconnected';
        }
    }

    updateOnlineUsers(active, total) {
        const activeEl = document.getElementById('active-users-count');
        const totalEl = document.getElementById('total-sessions-count');

        if (activeEl) {
            activeEl.textContent = active;
            activeEl.classList.add('count-updated');
            setTimeout(() => activeEl.classList.remove('count-updated'), 500);
        }

        if (totalEl) {
            totalEl.textContent = total;
        }
    }

    updateClientTypes(types) {
        // Delegated to dashboard app if needed
        if (window.dashboardApp && window.dashboardApp.updateClientTypes) {
            window.dashboardApp.updateClientTypes(types);
        }
    }

    showAlert(message, severity = 'info') {
        const alertContainer = document.getElementById('alerts-container') || document.body;

        const alert = document.createElement('div');
        alert.className = `alert alert-${severity}`;
        alert.innerHTML = `
            <strong>${severity === 'error' ? '❌' : severity === 'warning' ? '⚠️' : 'ℹ️'}</strong>
            ${message}
        `;

        alertContainer.appendChild(alert);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    showReconnectButton() {
        const statusBar = document.querySelector('.connection-status-bar');
        if (statusBar && !document.getElementById('ws-reconnect-btn')) {
            const button = document.createElement('button');
            button.id = 'ws-reconnect-btn';
            button.className = 'btn btn-sm btn-secondary';
            button.textContent = '🔄 Reconnect';
            button.onclick = () => {
                this.reconnectAttempts = 0;
                this.connect();
                button.remove();
            };
            statusBar.appendChild(button);
        }
    }

    /**
     * Cleanup method to be called when app is destroyed
     */
    destroy() {
        console.log('[WebSocket] Destroying client');
        this.disconnect();
        this.messageHandlers.clear();
        this.connectionCallbacks = [];
    }
}

// Create global instance
window.wsClient = null;

// Auto-initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.wsClient = new CryptoWebSocketClient();
        console.log('[WebSocket] Client initialized');
    } catch (error) {
        console.error('[WebSocket] Initialization error:', error);
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.wsClient) {
        window.wsClient.destroy();
    }
});

console.log('[WebSocket] Module loaded');
