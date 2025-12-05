/**
 * WebSocket Client (OPTIONAL)
 * 
 * IMPORTANT: WebSocket is completely optional. All data can be retrieved via HTTP REST API.
 * This WebSocket client is provided as an alternative method for users who prefer real-time streaming.
 * If WebSocket is unavailable or you prefer HTTP, use the HTTP endpoints instead.
 * 
 * The application automatically falls back to HTTP polling if WebSocket fails.
 */
class WSClient {
    constructor() {
        this.socket = null;
        this.status = 'disconnected';
        this.statusSubscribers = new Set();
        this.globalSubscribers = new Set();
        this.typeSubscribers = new Map();
        this.eventLog = [];
        this.backoff = 1000;
        this.maxBackoff = 16000;
        this.shouldReconnect = true;
        this.isOptional = true; // Mark as optional feature
    }

    get url() {
        const { protocol, host } = window.location;
        const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';
        // For HuggingFace Space: wss://Really-amin-Datasourceforcryptocurrency-2.hf.space/ws
        return `${wsProtocol}//${host}/ws`;
    }

    logEvent(event) {
        const entry = { ...event, time: new Date().toISOString() };
        this.eventLog.push(entry);
        this.eventLog = this.eventLog.slice(-100);
    }

    onStatusChange(callback) {
        this.statusSubscribers.add(callback);
        callback(this.status);
        return () => this.statusSubscribers.delete(callback);
    }

    onMessage(callback) {
        this.globalSubscribers.add(callback);
        return () => this.globalSubscribers.delete(callback);
    }

    subscribe(type, callback) {
        if (!this.typeSubscribers.has(type)) {
            this.typeSubscribers.set(type, new Set());
        }
        const set = this.typeSubscribers.get(type);
        set.add(callback);
        return () => set.delete(callback);
    }

    updateStatus(newStatus) {
        this.status = newStatus;
        this.statusSubscribers.forEach((cb) => cb(newStatus));
    }

    /**
     * Connect to WebSocket (OPTIONAL - HTTP endpoints work fine)
     * This is just an alternative method for real-time updates.
     * If connection fails, use HTTP polling instead.
     */
    connect() {
        if (this.socket && (this.status === 'connecting' || this.status === 'connected')) {
            return;
        }

        console.log('[WebSocket] Attempting optional WebSocket connection (HTTP endpoints are recommended)');
        this.updateStatus('connecting');
        this.socket = new WebSocket(this.url);
        this.logEvent({ type: 'status', status: 'connecting', note: 'optional' });

        this.socket.addEventListener('open', () => {
            this.backoff = 1000;
            this.updateStatus('connected');
            this.logEvent({ type: 'status', status: 'connected' });
        });

        this.socket.addEventListener('message', (event) => {
            try {
                const data = JSON.parse(event.data);
                this.logEvent({ type: 'message', messageType: data.type || 'unknown' });
                this.globalSubscribers.forEach((cb) => cb(data));
                if (data.type && this.typeSubscribers.has(data.type)) {
                    this.typeSubscribers.get(data.type).forEach((cb) => cb(data));
                }
            } catch (error) {
                console.error('WS message parse error', error);
            }
        });

        this.socket.addEventListener('close', () => {
            this.updateStatus('disconnected');
            this.logEvent({ type: 'status', status: 'disconnected', note: 'optional - use HTTP if needed' });
            // Don't auto-reconnect aggressively - WebSocket is optional
            // Users can use HTTP endpoints instead
            if (this.shouldReconnect && this.backoff < this.maxBackoff) {
                const delay = this.backoff;
                this.backoff = Math.min(this.backoff * 2, this.maxBackoff);
                console.log(`[WebSocket] Optional reconnection in ${delay}ms (or use HTTP endpoints)`);
                setTimeout(() => this.connect(), delay);
            } else if (this.shouldReconnect) {
                console.log('[WebSocket] Max reconnection attempts reached. Use HTTP endpoints instead.');
            }
        });

        this.socket.addEventListener('error', (error) => {
            console.warn('[WebSocket] Optional WebSocket error (non-critical):', error);
            console.info('[WebSocket] Tip: Use HTTP REST API endpoints instead - they work perfectly');
            this.logEvent({ 
                type: 'error', 
                details: error.message || 'unknown',
                timestamp: new Date().toISOString(),
                note: 'optional - HTTP endpoints available'
            });
            this.updateStatus('error');
            
            // Don't close immediately - let close event handle cleanup
            // This allows for proper reconnection logic
        });
    }

    disconnect() {
        this.shouldReconnect = false;
        if (this.socket) {
            this.socket.close();
        }
    }

    getEvents() {
        return [...this.eventLog];
    }
}

const wsClient = new WSClient();
export default wsClient;
