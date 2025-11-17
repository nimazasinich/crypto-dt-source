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
    }

    get url() {
        const { protocol, host } = window.location;
        const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';
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

    connect() {
        if (this.socket && (this.status === 'connecting' || this.status === 'connected')) {
            return;
        }

        this.updateStatus('connecting');
        this.socket = new WebSocket(this.url);
        this.logEvent({ type: 'status', status: 'connecting' });

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
            this.logEvent({ type: 'status', status: 'disconnected' });
            if (this.shouldReconnect) {
                const delay = this.backoff;
                this.backoff = Math.min(this.backoff * 2, this.maxBackoff);
                setTimeout(() => this.connect(), delay);
            }
        });

        this.socket.addEventListener('error', (error) => {
            console.error('WebSocket error', error);
            this.logEvent({ type: 'error', details: error.message || 'unknown' });
            if (this.socket) {
                this.socket.close();
            }
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
