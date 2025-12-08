/**
 * Real-Time System Monitor
 * Animated dashboard with live network visualization
 * Enhanced with SVG icons and beautiful animations
 */

class SystemMonitor {
    constructor() {
        this.canvas = document.getElementById('network-canvas');
        if (this.canvas) {
            this.ctx = this.canvas.getContext('2d');
        } else {
            console.error('[SystemMonitor] Canvas element not found');
            this.ctx = null;
        }
        this.ws = null;
        this.updateInterval = null;
        this.animationFrame = null;
        this.lastPing = null;
        
        // Network visualization data
        this.nodes = [];
        this.packets = [];
        this.serverNode = null;
        this.databaseNode = null;
        this.clientNodes = [];
        this.aiModelNodes = [];
        
        // System state
        this.systemStatus = null;
        this.lastUpdate = null;
        
        // Animation state
        this.time = 0;
        this.particleEffects = [];
        
        // SVG Icons cache
        this.icons = {};
        
        // Initialize
        this.init();
    }
    
    async init() {
        console.log('[SystemMonitor] Initializing...');
        
        // Show loading state
        this.showLoadingState();
        
        try {
            this.loadIcons();
            console.log('[SystemMonitor] Icons loaded');
        } catch (error) {
            console.error('[SystemMonitor] Icons loading failed:', error);
        }
        
        try {
            this.setupCanvas();
            console.log('[SystemMonitor] Canvas setup complete');
        } catch (error) {
            console.error('[SystemMonitor] Canvas setup failed:', error);
        }
        
        try {
            this.setupEventListeners();
            console.log('[SystemMonitor] Event listeners setup complete');
        } catch (error) {
            console.error('[SystemMonitor] Event listeners setup failed:', error);
        }
        
        try {
            this.startAnimation();
            console.log('[SystemMonitor] Animation started');
        } catch (error) {
            console.error('[SystemMonitor] Animation failed:', error);
        }
        
        // Connect WebSocket and start polling
        try {
            this.connectWebSocket();
            console.log('[SystemMonitor] WebSocket connection initiated');
        } catch (error) {
            console.error('[SystemMonitor] WebSocket connection failed:', error);
        }
        
        try {
            this.startPolling();
            console.log('[SystemMonitor] Polling started');
        } catch (error) {
            console.error('[SystemMonitor] Polling failed:', error);
        }
        
        // Hide loading state after initial data load
        setTimeout(() => {
            this.hideLoadingState();
        }, 1000);
        
        console.log('[SystemMonitor] Initialization complete');
    }
    
    showLoadingState() {
        const statsGrid = document.getElementById('stats-grid');
        if (!statsGrid) return;
        
        // Add loading class to cards
        statsGrid.querySelectorAll('.stat-card').forEach(card => {
            const details = card.querySelector('.stat-details, .models-list, .sources-summary, .requests-list');
            if (details) {
                details.innerHTML = '<div class="loading-spinner-small"></div>';
            }
        });
    }
    
    hideLoadingState() {
        // Loading states will be replaced by actual data
    }
    
    loadIcons() {
        // SVG icon definitions as data URIs
        this.icons = {
            server: this.createServerIcon(),
            database: this.createDatabaseIcon(),
            client: this.createClientIcon(),
            source: this.createSourceIcon(),
            aiModel: this.createAIModelIcon()
        };
    }
    
    createServerIcon() {
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2">
            <rect x="2" y="2" width="20" height="8" rx="2" ry="2"/>
            <rect x="2" y="14" width="20" height="8" rx="2" ry="2"/>
            <line x1="6" y1="6" x2="6.01" y2="6"/>
            <line x1="6" y1="18" x2="6.01" y2="18"/>
        </svg>`;
        return 'data:image/svg+xml;base64,' + btoa(svg);
    }
    
    createDatabaseIcon() {
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2">
            <ellipse cx="12" cy="5" rx="9" ry="3"/>
            <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
        </svg>`;
        return 'data:image/svg+xml;base64,' + btoa(svg);
    }
    
    createClientIcon() {
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
            <line x1="8" y1="21" x2="16" y2="21"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
        </svg>`;
        return 'data:image/svg+xml;base64,' + btoa(svg);
    }
    
    createSourceIcon() {
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <circle cx="12" cy="12" r="6"/>
            <circle cx="12" cy="12" r="2"/>
        </svg>`;
        return 'data:image/svg+xml;base64,' + btoa(svg);
    }
    
    createAIModelIcon() {
        const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#ec4899" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
        </svg>`;
        return 'data:image/svg+xml;base64,' + btoa(svg);
    }
    
    setupCanvas() {
        if (!this.canvas) {
            console.warn('[SystemMonitor] Canvas not available, skipping setup');
            return;
        }
        
        const resizeCanvas = () => {
            if (!this.canvas) return;
            const rect = this.canvas.getBoundingClientRect();
            this.canvas.width = rect.width;
            this.canvas.height = rect.height;
            this.draw();
        };
        
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // Use /api/monitoring/ws (from realtime_monitoring_api router)
        const wsUrl = `${protocol}//${window.location.host}/api/monitoring/ws`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('[SystemMonitor] WebSocket connected');
                this.updateConnectionStatus(true);
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'heartbeat') {
                        return;
                    }
                    this.updateSystemStatus(data);
                } catch (error) {
                    console.error('[SystemMonitor] Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('[SystemMonitor] WebSocket error:', error);
                this.updateConnectionStatus(false);
            };
            
            this.ws.onclose = () => {
                console.log('[SystemMonitor] WebSocket disconnected');
                this.updateConnectionStatus(false);
                // Reconnect after 3 seconds
                setTimeout(() => this.connectWebSocket(), 3000);
            };
        } catch (error) {
            console.error('[SystemMonitor] Failed to connect WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }
    
    startPolling() {
        // Poll every 5 seconds to avoid rate limiting (429 errors)
        // Clear any existing interval first
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        this.updateInterval = setInterval(() => {
            this.fetchSystemStatus();
        }, 5000); // 5 seconds instead of 2
        
        // Initial fetch
        this.fetchSystemStatus();
    }
    
    async fetchSystemStatus() {
        try {
            console.log('[SystemMonitor] Fetching system status...');
            // Use /api/monitoring/status (from realtime_monitoring_api router)
            const response = await fetch('/api/monitoring/status', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                },
                signal: AbortSignal.timeout(10000) // 10 second timeout
            });
            
            console.log(`[SystemMonitor] Response status: ${response.status}`);
            
            if (!response.ok) {
                if (response.status === 429) {
                    // Rate limited - increase interval
                    console.warn('[SystemMonitor] Rate limited, increasing poll interval');
                    if (this.updateInterval) {
                        clearInterval(this.updateInterval);
                        this.updateInterval = setInterval(() => {
                            this.fetchSystemStatus();
                        }, 10000); // 10 seconds on rate limit
                    }
                    this.showToast('Rate limited - slowing updates', 'warning');
                    return;
                }
                const errorText = await response.text();
                console.error(`[SystemMonitor] HTTP ${response.status}: ${errorText}`);
                throw new Error(`HTTP ${response.status}: ${errorText.substring(0, 100)}`);
            }
            
            const data = await response.json();
            console.log('[SystemMonitor] Data received:', data);
            
            // Handle different response formats
            if (data.success === false) {
                console.warn('[SystemMonitor] API returned success=false:', data.error);
                this.showToast(data.error || 'API returned error', 'error');
                return;
            }
            
            this.updateSystemStatus(data);
            this.updateConnectionStatus(true);
            this.lastUpdate = new Date();
        } catch (error) {
            console.error('[SystemMonitor] Failed to fetch system status:', error);
            this.updateConnectionStatus(false);
            
            // Show error in UI
            const statusText = document.getElementById('overall-status-text');
            if (statusText) {
                statusText.textContent = 'Error';
            }
            const statusDot = document.getElementById('status-dot');
            if (statusDot) {
                statusDot.className = 'status-dot offline';
            }
            
            // Show toast for network errors
            if (error.name === 'AbortError' || error.message.includes('fetch')) {
                this.showToast('Connection timeout - check your network', 'error');
            }
        }
    }
    
    updateSystemStatus(data) {
        // Handle both success flag and direct data
        if (data && data.success === false) {
            console.warn('[SystemMonitor] API returned success=false:', data.error);
            this.showToast(data.error || 'API returned error', 'error');
            return;
        }
        
        if (!data) {
            console.warn('[SystemMonitor] No data received');
            this.showToast('No data received from server', 'warning');
            return;
        }
        
        this.systemStatus = data;
        this.lastUpdate = new Date(data.timestamp || new Date().toISOString());
        
        // Update UI - API returns: ai_models, data_sources, database, recent_requests, stats
        try {
            this.updateHeader();
            this.updateDatabaseStatus(data.database || {});
            this.updateAIModels(data.ai_models || {});
            this.updateDataSources(data.data_sources || {});
            this.updateRequests(data.recent_requests || [], data.stats || {});
            
            // Update network visualization
            this.updateNetworkNodes(data);
            
            // Hide loading states
            this.hideLoadingState();
        } catch (error) {
            console.error('[SystemMonitor] Error updating UI:', error);
            this.showToast('Error updating display', 'error');
        }
        
        // Send ping to WebSocket (less frequently)
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            if (!this.lastPing || Date.now() - this.lastPing > 10000) {
                this.ws.send(JSON.stringify({ type: 'ping' }));
                this.lastPing = Date.now();
            }
        }
    }
    
    updateHeader() {
        const statusBadge = document.getElementById('overall-status-badge');
        const statusText = document.getElementById('overall-status-text');
        const statusDot = document.getElementById('status-dot');
        const updateEl = document.getElementById('last-update');
        
        if (this.systemStatus) {
            const stats = this.systemStatus.stats || {};
            const totalSources = stats.total_sources || this.systemStatus.data_sources?.total || 0;
            const activeSources = stats.active_sources || this.systemStatus.data_sources?.active || 0;
            const health = totalSources > 0 ? (activeSources / totalSources) * 100 : 100;
            
            if (health >= 80) {
                statusText.textContent = 'Healthy';
                statusDot.className = 'status-dot online';
            } else if (health >= 50) {
                statusText.textContent = 'Degraded';
                statusDot.className = 'status-dot degraded';
            } else {
                statusText.textContent = 'Unhealthy';
                statusDot.className = 'status-dot offline';
            }
        }
        
        if (this.lastUpdate) {
            const secondsAgo = Math.floor((Date.now() - this.lastUpdate.getTime()) / 1000);
            updateEl.textContent = secondsAgo < 60 ? `${secondsAgo}s ago` : `${Math.floor(secondsAgo / 60)}m ago`;
        }
    }
    
    updateDatabaseStatus(db) {
        const statusEl = document.getElementById('db-status');
        const detailsEl = document.getElementById('db-details');
        
        if (!statusEl) return;
        
        const dot = statusEl.querySelector('.status-dot');
        const text = statusEl.querySelector('.status-text');
        
        if (db && db.online) {
            if (dot) dot.className = 'status-dot online';
            if (text) text.textContent = 'Online';
            
            // Add details
            if (detailsEl) {
                const dbPath = db.path || db.file_path || 'N/A';
                const dbSize = db.size ? this.formatBytes(db.size) : 'N/A';
                const dbTables = db.tables || db.table_count || 'N/A';
                detailsEl.innerHTML = `
                    <div class="stat-detail-item">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                            <circle cx="12" cy="10" r="3"/>
                        </svg>
                        <span>Path: ${dbPath.length > 30 ? dbPath.substring(0, 30) + '...' : dbPath}</span>
                    </div>
                    <div class="stat-detail-item">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                        </svg>
                        <span>Size: ${dbSize}</span>
                    </div>
                    ${dbTables !== 'N/A' ? `
                    <div class="stat-detail-item">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                            <line x1="3" y1="9" x2="21" y2="9"/>
                            <line x1="9" y1="21" x2="9" y2="9"/>
                        </svg>
                        <span>Tables: ${dbTables}</span>
                    </div>
                    ` : ''}
                `;
            }
        } else {
            if (dot) dot.className = 'status-dot offline';
            if (text) text.textContent = 'Offline';
            if (detailsEl) {
                detailsEl.innerHTML = `
                    <div class="stat-detail-item error">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"/>
                            <line x1="12" y1="8" x2="12" y2="12"/>
                            <line x1="12" y1="16" x2="12.01" y2="16"/>
                        </svg>
                        <span>Database connection failed</span>
                    </div>
                `;
            }
        }
    }
    
    updateAIModels(models) {
        const total = models.total || 0;
        const available = models.available || 0;
        const failed = models.failed || 0;
        
        const totalEl = document.getElementById('models-total');
        const availableEl = document.getElementById('models-available');
        const failedEl = document.getElementById('models-failed');
        
        if (totalEl) totalEl.textContent = total;
        if (availableEl) availableEl.textContent = available;
        if (failedEl) failedEl.textContent = failed;
        
        const listEl = document.getElementById('models-list');
        if (!listEl) return;
        
        listEl.innerHTML = '';
        
        const modelsList = models.models || [];
        if (modelsList.length === 0) {
            listEl.innerHTML = '<div class="empty-message">No models loaded</div>';
            return;
        }
        
        modelsList.slice(0, 5).forEach(model => {
            const item = document.createElement('div');
            item.className = 'model-item';
            const modelId = model.id || model.model_id || 'Unknown';
            const modelName = modelId.split('/').pop();
            const status = model.status || 'unknown';
            const statusClass = (status === 'available' || status === 'healthy') ? 'available' : 'failed';
            item.innerHTML = `
                <span class="model-name">${modelName}</span>
                <span class="model-status ${statusClass}">${status}</span>
            `;
            listEl.appendChild(item);
        });
    }
    
    updateDataSources(sources) {
        const total = sources.total || 0;
        const active = sources.active || 0;
        const pools = sources.pools || 0;
        
        const totalEl = document.getElementById('sources-total');
        const activeEl = document.getElementById('sources-active');
        const poolsEl = document.getElementById('sources-pools');
        
        if (totalEl) totalEl.textContent = total;
        if (activeEl) activeEl.textContent = active;
        if (poolsEl) poolsEl.textContent = pools;
        
        const summaryEl = document.getElementById('sources-summary');
        if (!summaryEl) return;
        
        summaryEl.innerHTML = '';
        
        const categories = sources.categories || {};
        if (Object.keys(categories).length === 0) {
            summaryEl.innerHTML = '<div class="empty-message">No source categories available</div>';
            return;
        }
        
        Object.entries(categories).forEach(([category, data]) => {
            const item = document.createElement('div');
            item.className = 'source-category';
            const activeCount = data.active || 0;
            const totalCount = data.total || 0;
            const isHealthy = activeCount > 0;
            item.innerHTML = `
                <span class="category-name">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <circle cx="12" cy="12" r="6"/>
                        <circle cx="12" cy="12" r="2"/>
                    </svg>
                    ${category}
                </span>
                <span class="category-count ${isHealthy ? 'success' : 'error'}">${activeCount}/${totalCount}</span>
            `;
            summaryEl.appendChild(item);
        });
    }
    
    updateRequests(requests, stats) {
        const minuteCount = stats?.requests_last_minute || stats?.requests_per_minute || 0;
        const hourCount = stats?.requests_last_hour || stats?.requests_per_hour || 0;
        
        const minuteEl = document.getElementById('requests-minute');
        const hourEl = document.getElementById('requests-hour');
        
        if (minuteEl) minuteEl.textContent = minuteCount;
        if (hourEl) hourEl.textContent = hourCount;
        
        const listEl = document.getElementById('requests-list');
        if (!listEl) return;
        
        listEl.innerHTML = '';
        
        if (!Array.isArray(requests)) {
            requests = [];
        }
        
        if (requests.length === 0) {
            listEl.innerHTML = '<div class="empty-message">No recent requests</div>';
            return;
        }
        
        requests.slice(0, 5).forEach(request => {
            const item = document.createElement('div');
            item.className = 'request-item';
            const timestamp = request.timestamp || new Date().toISOString();
            const time = new Date(timestamp);
            const timeStr = `${String(time.getHours()).padStart(2, '0')}:${String(time.getMinutes()).padStart(2, '0')}:${String(time.getSeconds()).padStart(2, '0')}`;
            const endpoint = request.endpoint || request.path || request.method || 'Request';
            const method = request.method || 'GET';
            item.innerHTML = `
                <div class="request-info">
                    <span class="request-method">${method}</span>
                    <span class="request-endpoint">${endpoint}</span>
                </div>
                <span class="request-time">${timeStr}</span>
            `;
            listEl.appendChild(item);
            
            // Create packet animation for new requests
            if (endpoint && endpoint !== 'Request') {
                this.createPacket(request);
            }
        });
    }
    
    updateNetworkNodes(data) {
        if (!this.canvas || this.canvas.width === 0) return;
        
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        
        // Server node (center)
        this.serverNode = {
            x: centerX,
            y: centerY,
            radius: 40,
            label: 'API Server',
            status: 'online',
            color: '#22c55e',
            icon: 'server',
            type: 'server'
        };
        
        // Database node (right of server)
        this.databaseNode = {
            x: centerX + 200,
            y: centerY,
            radius: 35,
            label: 'Database',
            status: data.database?.online ? 'online' : 'offline',
            color: data.database?.online ? '#3b82f6' : '#ef4444',
            icon: 'database',
            type: 'database'
        };
        
        // Client nodes (bottom - multiple clients)
        this.clientNodes = [];
        const numClients = 3;
        const clientSpacing = 150;
        const clientStartX = centerX - (clientSpacing * (numClients - 1)) / 2;
        
        for (let i = 0; i < numClients; i++) {
            this.clientNodes.push({
                x: clientStartX + i * clientSpacing,
                y: this.canvas.height - 80,
                radius: 30,
                label: `Client ${i + 1}`,
                status: 'active',
                color: '#8b5cf6',
                icon: 'client',
                type: 'client'
            });
        }
        
        // Source nodes (top - data sources in a circle)
        this.nodes = [];
        const sources = data.data_sources?.sources || [];
        const numSources = Math.max(sources.length, 4);
        const angleStep = Math.PI / (numSources + 1);
        const sourceRadius = 250;
        
        sources.forEach((source, index) => {
            const angle = Math.PI + angleStep * (index + 1);
            const x = centerX + Math.cos(angle) * sourceRadius;
            const y = centerY + Math.sin(angle) * sourceRadius;
            
            const status = source.status || 'active';
            this.nodes.push({
                x,
                y,
                radius: 30,
                label: source.name || source.id || `Source ${index + 1}`,
                status: status === 'active' ? 'online' : 'offline',
                color: status === 'active' ? '#f59e0b' : '#ef4444',
                icon: 'source',
                type: 'source',
                endpoint: source.endpoint || source.endpoint_url
            });
        });
        
        // AI Model nodes (left side)
        this.aiModelNodes = [];
        const models = data.ai_models?.models || [];
        const numModels = Math.min(models.length, 4);
        const modelSpacing = 80;
        const modelStartY = centerY - (modelSpacing * (numModels - 1)) / 2;
        
        models.slice(0, 4).forEach((model, index) => {
            const status = model.status || 'unknown';
            this.aiModelNodes.push({
                x: 80,
                y: modelStartY + index * modelSpacing,
                radius: 25,
                label: (model.id || model.model_id || 'Model').split('/').pop().substring(0, 15),
                status: status === 'available' || status === 'healthy' ? 'online' : 'offline',
                color: status === 'available' || status === 'healthy' ? '#ec4899' : '#ef4444',
                icon: 'aiModel',
                type: 'aiModel'
            });
        });
    }
    
    createPacket(request) {
        if (!this.serverNode) return;
        
        // Determine packet flow based on request type
        const endpoint = request.endpoint || request.path || '';
        let fromNode, toNode, returnNode;
        
        // Client request to server
        if (this.clientNodes.length > 0) {
            fromNode = this.clientNodes[Math.floor(Math.random() * this.clientNodes.length)];
            toNode = this.serverNode;
            
            // Determine next hop based on endpoint
            if (endpoint.includes('models') || endpoint.includes('sentiment')) {
                returnNode = this.aiModelNodes[0] || this.databaseNode;
            } else if (endpoint.includes('database') || endpoint.includes('history')) {
                returnNode = this.databaseNode;
            } else if (this.nodes.length > 0) {
                returnNode = this.nodes[Math.floor(Math.random() * this.nodes.length)];
            }
        }
        
        // Create request packet (client → server)
        const requestPacket = {
            x: fromNode.x,
            y: fromNode.y,
            startX: fromNode.x,
            startY: fromNode.y,
            targetX: toNode.x,
            targetY: toNode.y,
            progress: 0,
            speed: 0.015,
            color: '#8b5cf6',
            size: 6,
            label: endpoint.split('/').pop() || 'Request',
            type: 'request',
            trail: []
        };
        
        this.packets.push(requestPacket);
        
        // Create processing packet (server → data source/AI/DB)
        if (returnNode) {
            setTimeout(() => {
                const processingPacket = {
                    x: toNode.x,
                    y: toNode.y,
                    startX: toNode.x,
                    startY: toNode.y,
                    targetX: returnNode.x,
                    targetY: returnNode.y,
                    progress: 0,
                    speed: 0.02,
                    color: '#22d3ee',
                    size: 5,
                    label: 'Processing',
                    type: 'processing',
                    trail: []
                };
                this.packets.push(processingPacket);
                
                // Create response packet (data source/AI/DB → server)
                setTimeout(() => {
                    const responsePacket = {
                        x: returnNode.x,
                        y: returnNode.y,
                        startX: returnNode.x,
                        startY: returnNode.y,
                        targetX: toNode.x,
                        targetY: toNode.y,
                        progress: 0,
                        speed: 0.02,
                        color: '#22c55e',
                        size: 5,
                        label: 'Data',
                        type: 'response',
                        trail: []
                    };
                    this.packets.push(responsePacket);
                    
                    // Create final response (server → client)
                    setTimeout(() => {
                        const finalPacket = {
                            x: toNode.x,
                            y: toNode.y,
                            startX: toNode.x,
                            startY: toNode.y,
                            targetX: fromNode.x,
                            targetY: fromNode.y,
                            progress: 0,
                            speed: 0.015,
                            color: '#10b981',
                            size: 6,
                            label: 'Response',
                            type: 'final',
                            trail: []
                        };
                        this.packets.push(finalPacket);
                        
                        // Particle effect on client receive
                        setTimeout(() => {
                            this.createParticleEffect(fromNode.x, fromNode.y, '#10b981');
                        }, 1000);
                    }, 800);
                }, 800);
            }, 500);
        }
        
        // Cleanup old packets
        setTimeout(() => {
            this.packets = this.packets.filter(p => p.progress < 1.5);
        }, 5000);
    }
    
    createParticleEffect(x, y, color) {
        const numParticles = 12;
        for (let i = 0; i < numParticles; i++) {
            const angle = (Math.PI * 2 * i) / numParticles;
            this.particleEffects.push({
                x,
                y,
                vx: Math.cos(angle) * 2,
                vy: Math.sin(angle) * 2,
                life: 1,
                color,
                size: 3
            });
        }
    }
    
    startAnimation() {
        const animate = () => {
            this.update();
            this.draw();
            this.animationFrame = requestAnimationFrame(animate);
        };
        animate();
        
        // Generate demo packets periodically
        this.demoPacketInterval = setInterval(() => {
            if (this.clientNodes.length > 0 && this.serverNode) {
                const demoEndpoints = [
                    '/api/market/price',
                    '/api/models/sentiment',
                    '/api/service/rate',
                    '/api/monitoring/status',
                    '/api/database/query'
                ];
                
                const randomEndpoint = demoEndpoints[Math.floor(Math.random() * demoEndpoints.length)];
                this.createPacket({ endpoint: randomEndpoint });
            }
        }, 3000); // Create a demo packet every 3 seconds
    }
    
    update() {
        this.time += 0.016; // ~60fps
        
        // Update packet positions with smooth easing
        this.packets.forEach(packet => {
            packet.progress += packet.speed;
            
            // Easing function for smooth movement
            const easeProgress = packet.progress < 0.5
                ? 2 * packet.progress * packet.progress
                : 1 - Math.pow(-2 * packet.progress + 2, 2) / 2;
            
            // Calculate position
            const newX = packet.startX + (packet.targetX - packet.startX) * easeProgress;
            const newY = packet.startY + (packet.targetY - packet.startY) * easeProgress;
            
            // Add to trail
            if (packet.trail) {
                packet.trail.push({ x: packet.x, y: packet.y });
                if (packet.trail.length > 10) {
                    packet.trail.shift();
                }
            }
            
            packet.x = newX;
            packet.y = newY;
        });
        
        // Remove completed packets
        this.packets = this.packets.filter(p => p.progress < 1.2);
        
        // Update particle effects
        this.particleEffects.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.life -= 0.02;
            particle.vx *= 0.95;
            particle.vy *= 0.95;
        });
        
        // Remove dead particles
        this.particleEffects = this.particleEffects.filter(p => p.life > 0);
    }
    
    draw() {
        if (!this.canvas || !this.ctx || this.canvas.width === 0 || this.canvas.height === 0) {
            return;
        }
        
        // Clear canvas with gradient background
        const gradient = this.ctx.createLinearGradient(0, 0, 0, this.canvas.height);
        gradient.addColorStop(0, '#0f172a');
        gradient.addColorStop(1, '#1e293b');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid pattern
        this.drawGrid();
        
        // Draw connections
        if (this.serverNode) {
            // Server to database
            if (this.databaseNode) {
                this.drawConnection(this.serverNode, this.databaseNode, this.databaseNode.status === 'online');
            }
            
            // Server to sources
            this.nodes.forEach(node => {
                this.drawConnection(this.serverNode, node, node.status === 'online');
            });
            
            // Server to clients
            this.clientNodes.forEach(client => {
                this.drawConnection(this.serverNode, client, true);
            });
            
            // Server to AI models
            this.aiModelNodes.forEach(model => {
                this.drawConnection(this.serverNode, model, model.status === 'online');
            });
        }
        
        // Draw packet trails
        this.packets.forEach(packet => {
            if (packet.trail && packet.trail.length > 1) {
                this.drawTrail(packet.trail, packet.color);
            }
        });
        
        // Draw packets
        this.packets.forEach(packet => {
            this.drawPacket(packet);
        });
        
        // Draw particle effects
        this.particleEffects.forEach(particle => {
            this.drawParticle(particle);
        });
        
        // Draw nodes with icons
        if (this.serverNode) {
            this.drawNodeWithIcon(this.serverNode);
        }
        
        if (this.databaseNode) {
            this.drawNodeWithIcon(this.databaseNode);
        }
        
        this.clientNodes.forEach(node => {
            this.drawNodeWithIcon(node);
        });
        
        this.nodes.forEach(node => {
            this.drawNodeWithIcon(node);
        });
        
        this.aiModelNodes.forEach(node => {
            this.drawNodeWithIcon(node);
        });
        
        // Draw legend
        this.drawLegend();
    }
    
    drawGrid() {
        this.ctx.strokeStyle = 'rgba(148, 163, 184, 0.05)';
        this.ctx.lineWidth = 1;
        
        const gridSize = 40;
        
        // Vertical lines
        for (let x = 0; x < this.canvas.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y < this.canvas.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }
    
    drawTrail(trail, color) {
        if (trail.length < 2) return;
        
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 2;
        this.ctx.globalAlpha = 0.3;
        
        this.ctx.beginPath();
        this.ctx.moveTo(trail[0].x, trail[0].y);
        
        for (let i = 1; i < trail.length; i++) {
            this.ctx.lineTo(trail[i].x, trail[i].y);
        }
        
        this.ctx.stroke();
        this.ctx.globalAlpha = 1;
    }
    
    drawParticle(particle) {
        this.ctx.globalAlpha = particle.life;
        this.ctx.fillStyle = particle.color;
        this.ctx.beginPath();
        this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.globalAlpha = 1;
    }
    
    drawLegend() {
        const legends = [
            { label: 'Request', color: '#8b5cf6' },
            { label: 'Processing', color: '#22d3ee' },
            { label: 'Response', color: '#22c55e' }
        ];
        
        const startX = 20;
        const startY = 20;
        const spacing = 120;
        
        legends.forEach((legend, index) => {
            const x = startX + index * spacing;
            
            // Draw color indicator
            this.ctx.fillStyle = legend.color;
            this.ctx.beginPath();
            this.ctx.arc(x, startY, 6, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Draw label
            this.ctx.fillStyle = '#e2e8f0';
            this.ctx.font = '12px Arial';
            this.ctx.textAlign = 'left';
            this.ctx.fillText(legend.label, x + 12, startY + 4);
        });
        
        // Draw stats overlay (top right)
        if (this.systemStatus) {
            const stats = this.systemStatus.stats || {};
            const overlayX = this.canvas.width - 200;
            const overlayY = 20;
            
            // Background
            this.ctx.fillStyle = 'rgba(30, 41, 59, 0.9)';
            this.ctx.fillRect(overlayX, overlayY, 180, 120);
            
            // Border
            this.ctx.strokeStyle = '#22c55e';
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(overlayX, overlayY, 180, 120);
            
            // Title
            this.ctx.fillStyle = '#22c55e';
            this.ctx.font = 'bold 14px Arial';
            this.ctx.textAlign = 'left';
            this.ctx.fillText('System Stats', overlayX + 10, overlayY + 25);
            
            // Stats
            const statsList = [
                { label: 'Active Packets:', value: this.packets.length },
                { label: 'Data Sources:', value: stats.active_sources || 0 },
                { label: 'AI Models:', value: this.aiModelNodes.length },
                { label: 'Clients:', value: this.clientNodes.length }
            ];
            
            this.ctx.font = '11px Arial';
            this.ctx.fillStyle = '#cbd5e1';
            
            statsList.forEach((stat, index) => {
                const y = overlayY + 50 + index * 20;
                this.ctx.fillText(stat.label, overlayX + 10, y);
                
                this.ctx.fillStyle = '#22d3ee';
                this.ctx.textAlign = 'right';
                this.ctx.fillText(String(stat.value), overlayX + 170, y);
                
                this.ctx.fillStyle = '#cbd5e1';
                this.ctx.textAlign = 'left';
            });
        }
    }
    
    drawConnection(from, to, active) {
        // Animated dashed line for active connections
        const dashOffset = active ? -this.time * 20 : 0;
        
        this.ctx.strokeStyle = active ? 'rgba(34, 197, 94, 0.4)' : 'rgba(239, 68, 68, 0.2)';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash(active ? [10, 5] : [5, 5]);
        this.ctx.lineDashOffset = dashOffset;
        
        this.ctx.beginPath();
        this.ctx.moveTo(from.x, from.y);
        this.ctx.lineTo(to.x, to.y);
        this.ctx.stroke();
        
        this.ctx.setLineDash([]);
    }
    
    drawNodeWithIcon(node) {
        // Pulsing glow effect
        const pulseScale = 1 + Math.sin(this.time * 2) * 0.1;
        const glowRadius = node.radius * 2.5 * pulseScale;
        
        const gradient = this.ctx.createRadialGradient(
            node.x, node.y, 0,
            node.x, node.y, glowRadius
        );
        gradient.addColorStop(0, node.color + '80');
        gradient.addColorStop(0.5, node.color + '20');
        gradient.addColorStop(1, 'transparent');
        
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(node.x, node.y, glowRadius, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Node background circle
        this.ctx.fillStyle = '#1e293b';
        this.ctx.beginPath();
        this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Node border with gradient
        const borderGradient = this.ctx.createLinearGradient(
            node.x - node.radius, node.y - node.radius,
            node.x + node.radius, node.y + node.radius
        );
        borderGradient.addColorStop(0, node.color);
        borderGradient.addColorStop(1, node.color + '80');
        
        this.ctx.strokeStyle = borderGradient;
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
        
        // Draw icon (simplified SVG representation)
        this.drawNodeIcon(node);
        
        // Node label with background
        const labelY = node.y + node.radius + 20;
        const labelText = node.label.substring(0, 15);
        
        this.ctx.font = 'bold 11px Arial';
        this.ctx.textAlign = 'center';
        const textWidth = this.ctx.measureText(labelText).width;
        
        // Label background
        this.ctx.fillStyle = 'rgba(30, 41, 59, 0.8)';
        this.ctx.fillRect(node.x - textWidth / 2 - 6, labelY - 12, textWidth + 12, 18);
        
        // Label text
        this.ctx.fillStyle = '#e2e8f0';
        this.ctx.fillText(labelText, node.x, labelY);
        
        // Status indicator
        if (node.status === 'online') {
            this.ctx.fillStyle = '#22c55e';
            this.ctx.beginPath();
            this.ctx.arc(node.x + node.radius - 8, node.y - node.radius + 8, 5, 0, Math.PI * 2);
            this.ctx.fill();
        } else if (node.status === 'offline') {
            this.ctx.fillStyle = '#ef4444';
            this.ctx.beginPath();
            this.ctx.arc(node.x + node.radius - 8, node.y - node.radius + 8, 5, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
    
    drawNodeIcon(node) {
        const iconSize = node.radius * 0.8;
        this.ctx.strokeStyle = node.color;
        this.ctx.fillStyle = node.color;
        this.ctx.lineWidth = 2;
        
        switch (node.type) {
            case 'server':
                // Server icon (stacked rectangles)
                this.ctx.strokeRect(node.x - iconSize / 2, node.y - iconSize / 2, iconSize, iconSize / 3);
                this.ctx.strokeRect(node.x - iconSize / 2, node.y - iconSize / 6, iconSize, iconSize / 3);
                this.ctx.strokeRect(node.x - iconSize / 2, node.y + iconSize / 6, iconSize, iconSize / 3);
                break;
                
            case 'database':
                // Database icon (cylinder)
                this.ctx.beginPath();
                this.ctx.ellipse(node.x, node.y - iconSize / 3, iconSize / 2, iconSize / 6, 0, 0, Math.PI * 2);
                this.ctx.stroke();
                this.ctx.beginPath();
                this.ctx.moveTo(node.x - iconSize / 2, node.y - iconSize / 3);
                this.ctx.lineTo(node.x - iconSize / 2, node.y + iconSize / 3);
                this.ctx.moveTo(node.x + iconSize / 2, node.y - iconSize / 3);
                this.ctx.lineTo(node.x + iconSize / 2, node.y + iconSize / 3);
                this.ctx.stroke();
                this.ctx.beginPath();
                this.ctx.ellipse(node.x, node.y + iconSize / 3, iconSize / 2, iconSize / 6, 0, 0, Math.PI * 2);
                this.ctx.stroke();
                break;
                
            case 'client':
                // Client icon (monitor)
                this.ctx.strokeRect(node.x - iconSize / 2, node.y - iconSize / 2, iconSize, iconSize * 0.7);
                this.ctx.beginPath();
                this.ctx.moveTo(node.x - iconSize / 4, node.y + iconSize / 2);
                this.ctx.lineTo(node.x + iconSize / 4, node.y + iconSize / 2);
                this.ctx.stroke();
                break;
                
            case 'source':
                // Source icon (radio waves)
                this.ctx.beginPath();
                this.ctx.arc(node.x, node.y, iconSize / 4, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.beginPath();
                this.ctx.arc(node.x, node.y, iconSize / 2, 0, Math.PI * 2);
                this.ctx.stroke();
                this.ctx.beginPath();
                this.ctx.arc(node.x, node.y, iconSize * 0.75, 0, Math.PI * 2);
                this.ctx.stroke();
                break;
                
            case 'aiModel':
                // AI Model icon (neural network)
                const nodeRadius = 3;
                this.ctx.fillStyle = node.color;
                // Input layer
                this.ctx.beginPath();
                this.ctx.arc(node.x - iconSize / 3, node.y - iconSize / 4, nodeRadius, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.beginPath();
                this.ctx.arc(node.x - iconSize / 3, node.y + iconSize / 4, nodeRadius, 0, Math.PI * 2);
                this.ctx.fill();
                // Hidden layer
                this.ctx.beginPath();
                this.ctx.arc(node.x, node.y - iconSize / 3, nodeRadius, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.beginPath();
                this.ctx.arc(node.x, node.y, nodeRadius, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.beginPath();
                this.ctx.arc(node.x, node.y + iconSize / 3, nodeRadius, 0, Math.PI * 2);
                this.ctx.fill();
                // Output layer
                this.ctx.beginPath();
                this.ctx.arc(node.x + iconSize / 3, node.y - iconSize / 4, nodeRadius, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.beginPath();
                this.ctx.arc(node.x + iconSize / 3, node.y + iconSize / 4, nodeRadius, 0, Math.PI * 2);
                this.ctx.fill();
                break;
        }
    }
    
    drawPacket(packet) {
        // Packet glow with pulsing effect
        const pulseScale = 1 + Math.sin(this.time * 5 + packet.progress * 10) * 0.2;
        const glowRadius = packet.size * 4 * pulseScale;
        
        const gradient = this.ctx.createRadialGradient(
            packet.x, packet.y, 0,
            packet.x, packet.y, glowRadius
        );
        gradient.addColorStop(0, packet.color);
        gradient.addColorStop(0.5, packet.color + '40');
        gradient.addColorStop(1, 'transparent');
        
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(packet.x, packet.y, glowRadius, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Packet core
        this.ctx.fillStyle = packet.color;
        this.ctx.beginPath();
        this.ctx.arc(packet.x, packet.y, packet.size, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Packet border
        this.ctx.strokeStyle = '#ffffff';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        
        // Packet type indicator (small icon)
        if (packet.type === 'request') {
            this.ctx.fillStyle = '#ffffff';
            this.ctx.font = 'bold 8px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('→', packet.x, packet.y + 3);
        } else if (packet.type === 'response') {
            this.ctx.fillStyle = '#ffffff';
            this.ctx.font = 'bold 8px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('✓', packet.x, packet.y + 3);
        }
    }
    
    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connection-status');
        if (!statusEl) return;
        
        const dot = statusEl.querySelector('.connection-dot');
        const text = statusEl.querySelector('.connection-text');
        
        if (connected) {
            if (dot) dot.className = 'connection-dot connected';
            if (text) text.textContent = 'Connected';
            statusEl.classList.remove('disconnected');
            statusEl.classList.add('connected');
        } else {
            if (dot) dot.className = 'connection-dot disconnected';
            if (text) text.textContent = 'Disconnected';
            statusEl.classList.remove('connected');
            statusEl.classList.add('disconnected');
        }
    }
    
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                console.log('[SystemMonitor] Manual refresh triggered');
                refreshBtn.disabled = true;
                refreshBtn.style.opacity = '0.6';
                this.fetchSystemStatus().finally(() => {
                    setTimeout(() => {
                        refreshBtn.disabled = false;
                        refreshBtn.style.opacity = '1';
                    }, 1000);
                });
            });
        }
        
        // Handle visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Pause updates when tab is hidden
                if (this.updateInterval) {
                    clearInterval(this.updateInterval);
                }
                if (this.animationFrame) {
                    cancelAnimationFrame(this.animationFrame);
                    this.animationFrame = null;
                }
            } else {
                // Resume updates when tab is visible
                this.startPolling();
                if (!this.animationFrame) {
                    this.startAnimation();
                }
            }
        });
    }
    
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    ${type === 'error' ? '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>' : ''}
                    ${type === 'success' ? '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>' : ''}
                    ${type === 'warning' ? '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>' : ''}
                    ${type === 'info' ? '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>' : ''}
                </svg>
                <span>${message}</span>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Animate in
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Remove after delay
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    destroy() {
        if (this.ws) {
            this.ws.close();
        }
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        if (this.demoPacketInterval) {
            clearInterval(this.demoPacketInterval);
        }
    }
}

// Export as default for ES6 modules
export default SystemMonitor;

// Also make available globally for non-module usage
if (typeof window !== 'undefined') {
    window.SystemMonitor = SystemMonitor;
}

