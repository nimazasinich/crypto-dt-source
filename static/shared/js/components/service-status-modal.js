/**
 * Service Status & Discovery Modal
 * Displays comprehensive service status for all discovered services
 */

class ServiceStatusModal {
    constructor() {
        this.services = [];
        this.healthData = {};
        this.categories = {};
        this.selectedCategory = null;
        this.searchQuery = '';
        this.sortBy = 'name'; // name, status, response_time
        this.sortOrder = 'asc';
        this.autoRefresh = true;
        this.refreshInterval = 30000; // 30 seconds
        this.refreshTimer = null;
        
        this.init();
    }
    
    init() {
        this.createModal();
        this.attachEventListeners();
    }
    
    createModal() {
        // Check if modal already exists
        if (document.getElementById('service-status-modal')) {
            return;
        }
        
        const modalHTML = `
            <div id="service-status-modal" class="service-modal" style="display: none;">
                <div class="service-modal-overlay" onclick="serviceStatusModal.close()"></div>
                <div class="service-modal-content">
                    <!-- Header -->
                    <div class="service-modal-header">
                        <h2>
                            <i class="fas fa-network-wired"></i>
                            Service Discovery & Status
                        </h2>
                        <button class="service-modal-close" onclick="serviceStatusModal.close()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <!-- Stats Summary -->
                    <div class="service-stats-summary" id="service-stats-summary">
                        <div class="stat-card">
                            <div class="stat-value" id="total-services">-</div>
                            <div class="stat-label">Total Services</div>
                        </div>
                        <div class="stat-card stat-online">
                            <div class="stat-value" id="online-services">-</div>
                            <div class="stat-label">Online</div>
                        </div>
                        <div class="stat-card stat-degraded">
                            <div class="stat-value" id="degraded-services">-</div>
                            <div class="stat-label">Degraded</div>
                        </div>
                        <div class="stat-card stat-offline">
                            <div class="stat-value" id="offline-services">-</div>
                            <div class="stat-label">Offline</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="avg-response-time">-</div>
                            <div class="stat-label">Avg Response</div>
                        </div>
                    </div>
                    
                    <!-- Controls -->
                    <div class="service-controls">
                        <div class="service-search">
                            <i class="fas fa-search"></i>
                            <input 
                                type="text" 
                                id="service-search-input" 
                                placeholder="Search services..."
                                onkeyup="serviceStatusModal.handleSearch(event)"
                            />
                        </div>
                        
                        <div class="service-filters">
                            <select id="category-filter" onchange="serviceStatusModal.handleCategoryFilter(event)">
                                <option value="">All Categories</option>
                            </select>
                            
                            <select id="status-filter" onchange="serviceStatusModal.handleStatusFilter(event)">
                                <option value="">All Status</option>
                                <option value="online">Online</option>
                                <option value="degraded">Degraded</option>
                                <option value="offline">Offline</option>
                                <option value="unknown">Unknown</option>
                            </select>
                            
                            <select id="sort-by" onchange="serviceStatusModal.handleSort(event)">
                                <option value="name">Sort by Name</option>
                                <option value="status">Sort by Status</option>
                                <option value="response_time">Sort by Response Time</option>
                                <option value="category">Sort by Category</option>
                            </select>
                        </div>
                        
                        <div class="service-actions">
                            <button onclick="serviceStatusModal.refreshData()" class="btn-refresh" title="Refresh Now">
                                <i class="fas fa-sync-alt"></i>
                            </button>
                            <button onclick="serviceStatusModal.toggleAutoRefresh()" class="btn-auto-refresh" id="auto-refresh-btn" title="Auto Refresh: ON">
                                <i class="fas fa-redo-alt"></i>
                            </button>
                            <button onclick="serviceStatusModal.exportData()" class="btn-export" title="Export Data">
                                <i class="fas fa-download"></i>
                            </button>
                        </div>
                    </div>
                    
                    <!-- Services List -->
                    <div class="service-list-container">
                        <div id="service-list-loading" class="loading-indicator">
                            <i class="fas fa-spinner fa-spin"></i> Loading services...
                        </div>
                        <div id="service-list" class="service-list"></div>
                        <div id="service-list-empty" class="empty-state" style="display: none;">
                            <i class="fas fa-inbox"></i>
                            <p>No services found</p>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="service-modal-footer">
                        <div class="last-updated">
                            Last updated: <span id="last-updated-time">Never</span>
                        </div>
                        <div class="footer-actions">
                            <button onclick="serviceStatusModal.checkAllHealth()" class="btn-secondary">
                                <i class="fas fa-heartbeat"></i> Check All Health
                            </button>
                            <button onclick="serviceStatusModal.rediscover()" class="btn-secondary">
                                <i class="fas fa-search"></i> Rediscover Services
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.addStyles();
    }
    
    addStyles() {
        if (document.getElementById('service-status-modal-styles')) {
            return;
        }
        
        const styles = `
            <style id="service-status-modal-styles">
                .service-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    z-index: 9999;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .service-modal-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.75);
                    backdrop-filter: blur(4px);
                }
                
                .service-modal-content {
                    position: relative;
                    background: #1a1a2e;
                    border-radius: 16px;
                    width: 95%;
                    max-width: 1400px;
                    max-height: 90vh;
                    display: flex;
                    flex-direction: column;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                
                .service-modal-header {
                    padding: 24px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .service-modal-header h2 {
                    margin: 0;
                    font-size: 24px;
                    color: #fff;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .service-modal-close {
                    background: transparent;
                    border: none;
                    color: #888;
                    font-size: 24px;
                    cursor: pointer;
                    padding: 8px;
                    border-radius: 8px;
                    transition: all 0.2s;
                }
                
                .service-modal-close:hover {
                    background: rgba(255, 255, 255, 0.1);
                    color: #fff;
                }
                
                .service-stats-summary {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 16px;
                    padding: 24px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
                
                .stat-card {
                    background: rgba(255, 255, 255, 0.05);
                    padding: 16px;
                    border-radius: 12px;
                    text-align: center;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                
                .stat-card.stat-online {
                    background: rgba(16, 185, 129, 0.1);
                    border-color: rgba(16, 185, 129, 0.3);
                }
                
                .stat-card.stat-degraded {
                    background: rgba(251, 191, 36, 0.1);
                    border-color: rgba(251, 191, 36, 0.3);
                }
                
                .stat-card.stat-offline {
                    background: rgba(239, 68, 68, 0.1);
                    border-color: rgba(239, 68, 68, 0.3);
                }
                
                .stat-value {
                    font-size: 32px;
                    font-weight: bold;
                    color: #fff;
                    margin-bottom: 4px;
                }
                
                .stat-label {
                    font-size: 12px;
                    color: #888;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                .service-controls {
                    padding: 16px 24px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    display: flex;
                    gap: 16px;
                    align-items: center;
                    flex-wrap: wrap;
                }
                
                .service-search {
                    flex: 1;
                    min-width: 200px;
                    position: relative;
                }
                
                .service-search i {
                    position: absolute;
                    left: 12px;
                    top: 50%;
                    transform: translateY(-50%);
                    color: #888;
                }
                
                .service-search input {
                    width: 100%;
                    padding: 10px 12px 10px 40px;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    color: #fff;
                    font-size: 14px;
                }
                
                .service-search input:focus {
                    outline: none;
                    border-color: #3b82f6;
                }
                
                .service-filters {
                    display: flex;
                    gap: 8px;
                }
                
                .service-filters select {
                    padding: 8px 12px;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    color: #fff;
                    font-size: 14px;
                    cursor: pointer;
                }
                
                .service-actions {
                    display: flex;
                    gap: 8px;
                }
                
                .service-actions button {
                    padding: 8px 12px;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    color: #fff;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                
                .service-actions button:hover {
                    background: rgba(255, 255, 255, 0.1);
                }
                
                .service-actions button.active {
                    background: #3b82f6;
                    border-color: #3b82f6;
                }
                
                .service-list-container {
                    flex: 1;
                    overflow-y: auto;
                    padding: 24px;
                }
                
                .service-list {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                    gap: 16px;
                }
                
                .service-card {
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 16px;
                    transition: all 0.2s;
                    cursor: pointer;
                }
                
                .service-card:hover {
                    background: rgba(255, 255, 255, 0.08);
                    transform: translateY(-2px);
                }
                
                .service-card-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: start;
                    margin-bottom: 12px;
                }
                
                .service-name {
                    font-size: 16px;
                    font-weight: 600;
                    color: #fff;
                    margin-bottom: 4px;
                }
                
                .service-category {
                    font-size: 11px;
                    color: #888;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                .service-status-badge {
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                .service-status-badge.online {
                    background: rgba(16, 185, 129, 0.2);
                    color: #10b981;
                    border: 1px solid rgba(16, 185, 129, 0.3);
                }
                
                .service-status-badge.degraded {
                    background: rgba(251, 191, 36, 0.2);
                    color: #fbbf24;
                    border: 1px solid rgba(251, 191, 36, 0.3);
                }
                
                .service-status-badge.offline {
                    background: rgba(239, 68, 68, 0.2);
                    color: #ef4444;
                    border: 1px solid rgba(239, 68, 68, 0.3);
                }
                
                .service-status-badge.unknown {
                    background: rgba(107, 114, 128, 0.2);
                    color: #9ca3af;
                    border: 1px solid rgba(107, 114, 128, 0.3);
                }
                
                .service-url {
                    font-size: 12px;
                    color: #3b82f6;
                    margin-bottom: 8px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                
                .service-metrics {
                    display: flex;
                    gap: 16px;
                    margin-top: 12px;
                    padding-top: 12px;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }
                
                .service-metric {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    font-size: 12px;
                    color: #888;
                }
                
                .service-metric i {
                    color: #666;
                }
                
                .service-features {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 6px;
                    margin-top: 12px;
                }
                
                .feature-tag {
                    padding: 2px 8px;
                    background: rgba(59, 130, 246, 0.2);
                    border-radius: 4px;
                    font-size: 10px;
                    color: #3b82f6;
                }
                
                .service-modal-footer {
                    padding: 16px 24px;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .last-updated {
                    font-size: 12px;
                    color: #888;
                }
                
                .footer-actions {
                    display: flex;
                    gap: 8px;
                }
                
                .btn-secondary {
                    padding: 8px 16px;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    color: #fff;
                    cursor: pointer;
                    font-size: 13px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    transition: all 0.2s;
                }
                
                .btn-secondary:hover {
                    background: rgba(255, 255, 255, 0.1);
                }
                
                .loading-indicator {
                    text-align: center;
                    padding: 40px;
                    color: #888;
                }
                
                .empty-state {
                    text-align: center;
                    padding: 60px 20px;
                    color: #888;
                }
                
                .empty-state i {
                    font-size: 48px;
                    margin-bottom: 16px;
                    opacity: 0.5;
                }
                
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                
                .fa-spin {
                    animation: spin 1s linear infinite;
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    attachEventListeners() {
        // Auto-refresh if enabled
        if (this.autoRefresh) {
            this.startAutoRefresh();
        }
    }
    
    async open() {
        const modal = document.getElementById('service-status-modal');
        modal.style.display = 'flex';
        
        // Load data
        await this.loadData();
    }
    
    close() {
        const modal = document.getElementById('service-status-modal');
        modal.style.display = 'none';
        this.stopAutoRefresh();
    }
    
    async loadData() {
        try {
            // Show loading
            document.getElementById('service-list-loading').style.display = 'block';
            document.getElementById('service-list').innerHTML = '';
            
            // Fetch services and health data
            const [servicesRes, healthRes, categoriesRes] = await Promise.all([
                fetch('/api/services/discover'),
                fetch('/api/services/health'),
                fetch('/api/services/categories')
            ]);
            
            const servicesData = await servicesRes.json();
            const healthData = await healthRes.json();
            const categoriesData = await categoriesRes.json();
            
            this.services = servicesData.services || [];
            this.healthData = {};
            
            // Map health data to services
            if (healthData.services) {
                healthData.services.forEach(h => {
                    this.healthData[h.id] = h;
                });
            }
            
            this.categories = categoriesData.categories || {};
            
            // Update UI
            this.updateStats(healthData.summary);
            this.updateCategoryFilter();
            this.renderServices();
            this.updateLastUpdated();
            
            // Hide loading
            document.getElementById('service-list-loading').style.display = 'none';
            
        } catch (error) {
            console.error('Failed to load service data:', error);
            document.getElementById('service-list-loading').innerHTML = 
                `<div style="color: #ef4444;"><i class="fas fa-exclamation-triangle"></i> Failed to load services</div>`;
        }
    }
    
    updateStats(summary) {
        if (!summary) return;
        
        document.getElementById('total-services').textContent = summary.total_services || 0;
        document.getElementById('online-services').textContent = summary.status_counts?.online || 0;
        document.getElementById('degraded-services').textContent = summary.status_counts?.degraded || 0;
        document.getElementById('offline-services').textContent = summary.status_counts?.offline || 0;
        document.getElementById('avg-response-time').textContent = 
            summary.average_response_time_ms ? `${summary.average_response_time_ms}ms` : '-';
    }
    
    updateCategoryFilter() {
        const select = document.getElementById('category-filter');
        select.innerHTML = '<option value="">All Categories</option>';
        
        Object.keys(this.categories).forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = `${this.categories[cat].display_name} (${this.categories[cat].count})`;
            select.appendChild(option);
        });
    }
    
    renderServices() {
        const serviceList = document.getElementById('service-list');
        const emptyState = document.getElementById('service-list-empty');
        
        // Filter services
        let filteredServices = this.services.filter(service => {
            // Category filter
            if (this.selectedCategory && service.category !== this.selectedCategory) {
                return false;
            }
            
            // Search filter
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                return (
                    service.name.toLowerCase().includes(query) ||
                    service.base_url.toLowerCase().includes(query) ||
                    service.category.toLowerCase().includes(query) ||
                    (service.features && service.features.some(f => f.toLowerCase().includes(query)))
                );
            }
            
            return true;
        });
        
        // Sort services
        filteredServices = this.sortServices(filteredServices);
        
        // Render
        if (filteredServices.length === 0) {
            serviceList.innerHTML = '';
            emptyState.style.display = 'block';
            return;
        }
        
        emptyState.style.display = 'none';
        serviceList.innerHTML = filteredServices.map(service => this.renderServiceCard(service)).join('');
    }
    
    renderServiceCard(service) {
        const health = this.healthData[service.id] || {};
        const status = health.status || 'unknown';
        const responseTime = health.response_time_ms ? `${Math.round(health.response_time_ms)}ms` : '-';
        const statusCode = health.status_code || '-';
        
        const features = service.features || [];
        const displayFeatures = features.slice(0, 5);
        
        return `
            <div class="service-card" onclick="serviceStatusModal.showServiceDetails('${service.id}')">
                <div class="service-card-header">
                    <div>
                        <div class="service-name">${service.name}</div>
                        <div class="service-category">${service.category.replace(/_/g, ' ')}</div>
                    </div>
                    <div class="service-status-badge ${status}">${status}</div>
                </div>
                
                <div class="service-url" title="${service.base_url}">${service.base_url}</div>
                
                <div class="service-metrics">
                    <div class="service-metric">
                        <i class="fas fa-clock"></i>
                        <span>${responseTime}</span>
                    </div>
                    <div class="service-metric">
                        <i class="fas fa-code"></i>
                        <span>${statusCode}</span>
                    </div>
                    ${service.requires_auth ? '<div class="service-metric"><i class="fas fa-key"></i><span>Auth</span></div>' : ''}
                </div>
                
                ${displayFeatures.length > 0 ? `
                    <div class="service-features">
                        ${displayFeatures.map(f => `<span class="feature-tag">${f}</span>`).join('')}
                        ${features.length > 5 ? `<span class="feature-tag">+${features.length - 5}</span>` : ''}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    sortServices(services) {
        return services.sort((a, b) => {
            let aValue, bValue;
            
            switch(this.sortBy) {
                case 'status':
                    aValue = this.healthData[a.id]?.status || 'unknown';
                    bValue = this.healthData[b.id]?.status || 'unknown';
                    break;
                case 'response_time':
                    aValue = this.healthData[a.id]?.response_time_ms || 999999;
                    bValue = this.healthData[b.id]?.response_time_ms || 999999;
                    break;
                case 'category':
                    aValue = a.category;
                    bValue = b.category;
                    break;
                case 'name':
                default:
                    aValue = a.name.toLowerCase();
                    bValue = b.name.toLowerCase();
            }
            
            if (aValue < bValue) return this.sortOrder === 'asc' ? -1 : 1;
            if (aValue > bValue) return this.sortOrder === 'asc' ? 1 : -1;
            return 0;
        });
    }
    
    handleSearch(event) {
        this.searchQuery = event.target.value;
        this.renderServices();
    }
    
    handleCategoryFilter(event) {
        this.selectedCategory = event.target.value || null;
        this.renderServices();
    }
    
    handleStatusFilter(event) {
        // Implement status filter logic
        this.renderServices();
    }
    
    handleSort(event) {
        this.sortBy = event.target.value;
        this.renderServices();
    }
    
    async refreshData() {
        await this.loadData();
    }
    
    toggleAutoRefresh() {
        this.autoRefresh = !this.autoRefresh;
        const btn = document.getElementById('auto-refresh-btn');
        
        if (this.autoRefresh) {
            btn.classList.add('active');
            btn.title = 'Auto Refresh: ON';
            this.startAutoRefresh();
        } else {
            btn.classList.remove('active');
            btn.title = 'Auto Refresh: OFF';
            this.stopAutoRefresh();
        }
    }
    
    startAutoRefresh() {
        this.stopAutoRefresh();
        this.refreshTimer = setInterval(() => {
            this.loadData();
        }, this.refreshInterval);
    }
    
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
    
    async checkAllHealth() {
        try {
            document.getElementById('service-list-loading').style.display = 'block';
            await fetch('/api/services/health/check', { method: 'POST' });
            await this.loadData();
        } catch (error) {
            console.error('Failed to check health:', error);
            alert('Failed to check service health');
        }
    }
    
    async rediscover() {
        try {
            document.getElementById('service-list-loading').style.display = 'block';
            await fetch('/api/services/discover?refresh=true');
            await this.loadData();
        } catch (error) {
            console.error('Failed to rediscover services:', error);
            alert('Failed to rediscover services');
        }
    }
    
    async exportData() {
        try {
            const response = await fetch('/api/services/export');
            const data = await response.json();
            
            const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `service-status-${new Date().toISOString()}.json`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Failed to export data:', error);
            alert('Failed to export data');
        }
    }
    
    showServiceDetails(serviceId) {
        const service = this.services.find(s => s.id === serviceId);
        const health = this.healthData[serviceId] || {};
        
        if (!service) return;
        
        const details = `
            <div style="color: #fff; line-height: 1.8;">
                <h3>${service.name}</h3>
                <p><strong>Category:</strong> ${service.category.replace(/_/g, ' ')}</p>
                <p><strong>Base URL:</strong> <a href="${service.base_url}" target="_blank" style="color: #3b82f6;">${service.base_url}</a></p>
                <p><strong>Status:</strong> <span style="color: ${health.status === 'online' ? '#10b981' : '#ef4444'}">${health.status || 'unknown'}</span></p>
                <p><strong>Response Time:</strong> ${health.response_time_ms ? health.response_time_ms + 'ms' : 'N/A'}</p>
                <p><strong>Requires Auth:</strong> ${service.requires_auth ? 'Yes' : 'No'}</p>
                ${service.features && service.features.length > 0 ? `
                    <p><strong>Features:</strong> ${service.features.join(', ')}</p>
                ` : ''}
                ${service.endpoints && service.endpoints.length > 0 ? `
                    <p><strong>Endpoints:</strong></p>
                    <ul>${service.endpoints.map(e => `<li>${e}</li>`).join('')}</ul>
                ` : ''}
                ${service.documentation_url ? `
                    <p><strong>Documentation:</strong> <a href="${service.documentation_url}" target="_blank" style="color: #3b82f6;">View Docs</a></p>
                ` : ''}
            </div>
        `;
        
        alert(details); // Replace with a proper modal if available
    }
    
    updateLastUpdated() {
        const now = new Date().toLocaleTimeString();
        document.getElementById('last-updated-time').textContent = now;
    }
}

// Initialize global instance
const serviceStatusModal = new ServiceStatusModal();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ServiceStatusModal;
}
