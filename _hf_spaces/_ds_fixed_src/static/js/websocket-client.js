/**
 * WebSocket Client برای اتصال بلادرنگ به سرور
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
        this.messageHandlers = {};
        this.connectionCallbacks = [];
        
        this.connect();
    }
    
    connect() {
        try {
            console.log('🔌 اتصال به WebSocket:', this.url);
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = this.onOpen.bind(this);
            this.ws.onmessage = this.onMessage.bind(this);
            this.ws.onerror = this.onError.bind(this);
            this.ws.onclose = this.onClose.bind(this);
            
        } catch (error) {
            console.error('❌ خطا در اتصال WebSocket:', error);
            this.scheduleReconnect();
        }
    }
    
    onOpen(event) {
        console.log('✅ WebSocket متصل شد');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        
        // فراخوانی callback‌ها
        this.connectionCallbacks.forEach(cb => cb(true));
        
        // نمایش وضعیت اتصال
        this.updateConnectionStatus(true);
    }
    
    onMessage(event) {
        try {
            const message = JSON.parse(event.data);
            const type = message.type;
            
            // مدیریت پیام‌های سیستمی
            if (type === 'welcome') {
                this.sessionId = message.session_id;
                console.log('📝 Session ID:', this.sessionId);
            }
            
            else if (type === 'stats_update') {
                this.handleStatsUpdate(message.data);
            }
            
            else if (type === 'provider_stats') {
                this.handleProviderStats(message.data);
            }
            
            else if (type === 'market_update') {
                this.handleMarketUpdate(message.data);
            }
            
            else if (type === 'price_update') {
                this.handlePriceUpdate(message.data);
            }
            
            else if (type === 'alert') {
                this.handleAlert(message.data);
            }
            
            else if (type === 'heartbeat') {
                // پاسخ به heartbeat
                this.send({ type: 'pong' });
            }
            
            // فراخوانی handler سفارشی
            if (this.messageHandlers[type]) {
                this.messageHandlers[type](message);
            }
            
        } catch (error) {
            console.error('❌ خطا در پردازش پیام:', error);
        }
    }
    
    onError(error) {
        console.error('❌ خطای WebSocket:', error);
        this.isConnected = false;
        this.updateConnectionStatus(false);
    }
    
    onClose(event) {
        console.log('🔌 WebSocket قطع شد');
        this.isConnected = false;
        this.sessionId = null;
        
        this.connectionCallbacks.forEach(cb => cb(false));
        this.updateConnectionStatus(false);
        
        // تلاش مجدد برای اتصال
        this.scheduleReconnect();
    }
    
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 تلاش مجدد برای اتصال (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        } else {
            console.error('❌ تعداد تلاش‌های اتصال به پایان رسید');
            this.showReconnectButton();
        }
    }
    
    send(data) {
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('⚠️ WebSocket متصل نیست');
        }
    }
    
    subscribe(group) {
        this.send({
            type: 'subscribe',
            group: group
        });
    }
    
    unsubscribe(group) {
        this.send({
            type: 'unsubscribe',
            group: group
        });
    }
    
    requestStats() {
        this.send({
            type: 'get_stats'
        });
    }
    
    on(type, handler) {
        this.messageHandlers[type] = handler;
    }
    
    onConnection(callback) {
        this.connectionCallbacks.push(callback);
    }
    
    // ===== Handlers برای انواع پیام‌ها =====
    
    handleStatsUpdate(data) {
        // به‌روزرسانی نمایش تعداد کاربران
        const activeConnections = data.active_connections || 0;
        const totalSessions = data.total_sessions || 0;
        
        // به‌روزرسانی UI
        this.updateOnlineUsers(activeConnections, totalSessions);
        
        // آپدیت سایر آمار
        if (data.client_types) {
            this.updateClientTypes(data.client_types);
        }
    }
    
    handleProviderStats(data) {
        // به‌روزرسانی آمار Provider
        const summary = data.summary || {};
        
        // آپدیت نمایش
        if (window.updateProviderStats) {
            window.updateProviderStats(summary);
        }
    }
    
    handleMarketUpdate(data) {
        if (window.updateMarketData) {
            window.updateMarketData(data);
        }
    }
    
    handlePriceUpdate(data) {
        if (window.updatePrice) {
            window.updatePrice(data.symbol, data.price, data.change_24h);
        }
    }
    
    handleAlert(data) {
        this.showAlert(data.message, data.severity);
    }
    
    // ===== UI Updates =====
    
    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('ws-connection-status');
        const statusDot = document.getElementById('ws-status-dot');
        const statusText = document.getElementById('ws-status-text');
        
        if (statusEl && statusDot && statusText) {
            if (connected) {
                statusDot.className = 'status-dot status-dot-online';
                statusText.textContent = 'متصل';
                statusEl.classList.add('connected');
                statusEl.classList.remove('disconnected');
            } else {
                statusDot.className = 'status-dot status-dot-offline';
                statusText.textContent = 'قطع شده';
                statusEl.classList.add('disconnected');
                statusEl.classList.remove('connected');
            }
        }
    }
    
    updateOnlineUsers(active, total) {
        const activeEl = document.getElementById('active-users-count');
        const totalEl = document.getElementById('total-sessions-count');
        const badgeEl = document.getElementById('online-users-badge');
        
        if (activeEl) {
            activeEl.textContent = active;
            // انیمیشن تغییر
            activeEl.classList.add('count-updated');
            setTimeout(() => activeEl.classList.remove('count-updated'), 500);
        }
        
        if (totalEl) {
            totalEl.textContent = total;
        }
        
        if (badgeEl) {
            badgeEl.textContent = active;
            badgeEl.classList.add('pulse');
            setTimeout(() => badgeEl.classList.remove('pulse'), 1000);
        }
    }
    
    updateClientTypes(types) {
        const listEl = document.getElementById('client-types-list');
        if (listEl && types) {
            const html = Object.entries(types).map(([type, count]) => 
                `<div class="client-type-item">
                    <span class="client-type-name">${type}</span>
                    <span class="client-type-count">${count}</span>
                </div>`
            ).join('');
            listEl.innerHTML = html;
        }
    }
    
    showAlert(message, severity = 'info') {
        // ساخت alert
        const alert = document.createElement('div');
        alert.className = `alert alert-${severity} alert-dismissible fade show`;
        alert.innerHTML = `
            <strong>${severity === 'error' ? '❌' : severity === 'warning' ? '⚠️' : 'ℹ️'}</strong>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.getElementById('alerts-container') || document.body;
        container.appendChild(alert);
        
        // حذف خودکار بعد از 5 ثانیه
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    }
    
    showReconnectButton() {
        const button = document.createElement('button');
        button.className = 'btn btn-warning reconnect-btn';
        button.innerHTML = '🔄 اتصال مجدد';
        button.onclick = () => {
            this.reconnectAttempts = 0;
            this.connect();
            button.remove();
        };
        
        const statusEl = document.getElementById('ws-connection-status');
        if (statusEl) {
            statusEl.appendChild(button);
        }
    }
    
    close() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// ایجاد instance سراسری
window.wsClient = null;

// اتصال خودکار
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.wsClient = new CryptoWebSocketClient();
        console.log('✅ WebSocket Client آماده است');
    } catch (error) {
        console.error('❌ خطا در راه‌اندازی WebSocket Client:', error);
    }
});

