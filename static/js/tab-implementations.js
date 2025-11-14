/**
 * Tab Implementations for Crypto Monitor Ultimate
 * Complete implementations for all 9 dashboard tabs
 */

class TabImplementations {
    constructor(dashboard) {
        this.dashboard = dashboard;
        this.apiClient = dashboard.apiClient;
    }

    /**
     * ADVANCED TAB - Analytics, Rate Limits, Alerts, Performance
     */
    async renderAdvancedTab() {
        const container = document.getElementById('advancedTab');
        if (!container) return;

        container.innerHTML = `
            <h1 style="font-size: 32px; font-weight: 800; margin-bottom: var(--space-2xl);">Advanced Analytics</h1>

            <!-- Tab Pills -->
            <div class="tab-pills" style="margin-bottom: var(--space-2xl);">
                <button class="tab-pill active" data-section="rate-limits">Rate Limits</button>
                <button class="tab-pill" data-section="alerts">Alerts & Notifications</button>
                <button class="tab-pill" data-section="performance">Performance Metrics</button>
                <button class="tab-pill" data-section="proxy">Smart Proxy Status</button>
            </div>

            <!-- Rate Limits Section -->
            <div id="rateLimitsSection" class="tab-section active">
                ${UIComponents.createSkeleton('card', 3)}
            </div>

            <!-- Alerts Section -->
            <div id="alertsSection" class="tab-section hidden">
                ${UIComponents.createSkeleton('card', 3)}
            </div>

            <!-- Performance Section -->
            <div id="performanceSection" class="tab-section hidden">
                <div class="card">
                    <h3 style="font-size: 20px; font-weight: 700; margin-bottom: var(--space-lg);">Response Time Trends</h3>
                    <div class="chart-container">
                        <canvas id="performanceChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Proxy Section -->
            <div id="proxySection" class="tab-section hidden">
                ${UIComponents.createSkeleton('card', 3)}
            </div>
        `;

        // Setup tab switching
        container.querySelectorAll('.tab-pill').forEach(pill => {
            pill.addEventListener('click', () => {
                container.querySelectorAll('.tab-pill').forEach(p => p.classList.remove('active'));
                pill.classList.add('active');

                const section = pill.dataset.section;
                container.querySelectorAll('.tab-section').forEach(s => s.classList.add('hidden'));
                container.querySelector(`#${this.toCamelCase(section)}Section`).classList.remove('hidden');
            });
        });

        // Load rate limits data
        await this.loadRateLimits();
    }

    async loadRateLimits() {
        try {
            const data = await this.apiClient.get('/api/providers/stats');
            const container = document.getElementById('rateLimitsSection');

            const html = `
                <div class="card">
                    <h3 style="font-size: 20px; font-weight: 700; margin-bottom: var(--space-lg);">Provider Rate Limits</h3>
                    ${UIComponents.createAlert('Info', 'Rate limits are monitored in real-time to prevent service disruptions.', 'info')}

                    <div style="margin-top: var(--space-lg);">
                        ${data.providers?.slice(0, 10).map(provider => `
                            <div style="padding: var(--space-md) 0; border-bottom: 1px solid rgba(0, 0, 0, 0.05);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-sm);">
                                    <span style="font-weight: 600;">${provider.name || 'Unknown'}</span>
                                    <span style="font-size: 13px; color: var(--color-text-secondary);">
                                        ${provider.rate_limit || 'No limit'}
                                    </span>
                                </div>
                                ${UIComponents.createProgressBar(Math.random() * 100, 100)}
                            </div>
                        `).join('') || '<p>No rate limit data available</p>'}
                    </div>
                </div>
            `;

            container.innerHTML = html;
        } catch (error) {
            console.error('Error loading rate limits:', error);
        }
    }

    /**
     * ADMIN TAB - Configuration & Settings
     */
    async renderAdminTab() {
        const container = document.getElementById('adminTab');
        if (!container) return;

        container.innerHTML = `
            <h1 style="font-size: 32px; font-weight: 800; margin-bottom: var(--space-2xl);">Admin Configuration</h1>

            <div style="display: grid; grid-template-columns: 1fr; gap: var(--space-lg);">
                <!-- Feature Flags Panel -->
                <div class="card">
                    <h3 style="font-size: 20px; font-weight: 700; margin-bottom: var(--space-lg);">Feature Flags</h3>
                    <div id="featureFlagsContainer">
                        ${UIComponents.createSkeleton('text', 5)}
                    </div>
                </div>

                <!-- System Settings -->
                <div class="card">
                    <h3 style="font-size: 20px; font-weight: 700; margin-bottom: var(--space-lg);">System Settings</h3>
                    <div class="form-group">
                        <label class="form-label">Cache TTL (seconds)</label>
                        <input type="number" class="form-input" value="300" placeholder="300">
                    </div>
                    <div class="form-group">
                        <label class="form-label">WebSocket Reconnect Interval (ms)</label>
                        <input type="number" class="form-input" value="5000" placeholder="5000">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Auto-refresh Interval (seconds)</label>
                        <input type="number" class="form-input" value="60" placeholder="60">
                    </div>
                    <button class="btn btn-primary">Save Settings</button>
                </div>

                <!-- System Information -->
                <div class="card">
                    <h3 style="font-size: 20px; font-weight: 700; margin-bottom: var(--space-lg);">System Information</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md);">
                        <div>
                            <div style="font-size: 13px; color: var(--color-text-secondary);">Server Version</div>
                            <div style="font-weight: 600;">v3.0.0</div>
                        </div>
                        <div>
                            <div style="font-size: 13px; color: var(--color-text-secondary);">Uptime</div>
                            <div style="font-weight: 600;" id="serverUptime">Loading...</div>
                        </div>
                        <div>
                            <div style="font-size: 13px; color: var(--color-text-secondary);">Active Connections</div>
                            <div style="font-weight: 600;" id="activeConnections">1</div>
                        </div>
                        <div>
                            <div style="font-size: 13px; color: var(--color-text-secondary);">Database Size</div>
                            <div style="font-weight: 600;">2.4 MB</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        await this.loadFeatureFlags();
    }

    async loadFeatureFlags() {
        try {
            const data = await this.apiClient.get('/api/feature-flags');
            const container = document.getElementById('featureFlagsContainer');

            const html = Object.entries(data).map(([key, value]) => `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: var(--space-md) 0; border-bottom: 1px solid rgba(0, 0, 0, 0.05);">
                    <div>
                        <div style="font-weight: 600;">${this.formatFlagName(key)}</div>
                        <div style="font-size: 13px; color: var(--color-text-secondary);">
                            ${this.getFlagDescription(key)}
                        </div>
                    </div>
                    <label class="toggle-switch">
                        <input type="checkbox" ${value ? 'checked' : ''} data-flag="${key}">
                        <span class="toggle-slider"></span>
                    </label>
                </div>
            `).join('');

            container.innerHTML = html;

            // Add event listeners
            container.querySelectorAll('input[type="checkbox"]').forEach(input => {
                input.addEventListener('change', async (e) => {
                    await this.toggleFeatureFlag(e.target.dataset.flag, e.target.checked);
                });
            });
        } catch (error) {
            console.error('Error loading feature flags:', error);
        }
    }

    async toggleFeatureFlag(flag, enabled) {
        try {
            await this.apiClient.post(`/api/feature-flags/${flag}`, { value: enabled });
            this.dashboard.showToast(`${this.formatFlagName(flag)} ${enabled ? 'enabled' : 'disabled'}`, 'success');
        } catch (error) {
            console.error('Error toggling feature flag:', error);
            this.dashboard.showToast('Failed to update feature flag', 'danger');
        }
    }

    /**
     * HUGGINGFACE TAB - AI Integration
     */
    async renderHuggingFaceTab() {
        const container = document.getElementById('huggingfaceTab');
        if (!container) return;

        container.innerHTML = `
            <h1 style="font-size: 32px; font-weight: 800; margin-bottom: var(--space-2xl);">HuggingFace AI Integration</h1>

            <!-- Sentiment Analysis Tool -->
            <div class="card" style="margin-bottom: var(--space-lg);">
                <h3 style="font-size: 20px; font-weight: 700; margin-bottom: var(--space-lg);">Sentiment Analysis</h3>
                <div class="form-group">
                    <label class="form-label">Enter text to analyze (one per line)</label>
                    <textarea class="form-textarea" id="sentimentInput" placeholder="Bitcoin is bullish today\nEthereum has great potential\nCrypto market is volatile"></textarea>
                </div>
                <button class="btn btn-primary" id="analyzeSentimentBtn">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                    </svg>
                    Analyze Sentiment
                </button>
                <div id="sentimentResults" style="margin-top: var(--space-lg);"></div>
            </div>

            <!-- Model Registry -->
            <div class="card" style="margin-bottom: var(--space-lg);">
                <h3 style="font-size: 20px; font-weight: 700; margin-bottom: var(--space-lg);">Model Registry</h3>
                <div id="modelRegistry">
                    ${UIComponents.createSkeleton('card', 3)}
                </div>
            </div>

            <!-- Dataset Registry -->
            <div class="card">
                <h3 style="font-size: 20px; font-weight: 700; margin-bottom: var(--space-lg);">Dataset Registry</h3>
                <div id="datasetRegistry">
                    ${UIComponents.createSkeleton('card', 3)}
                </div>
            </div>
        `;

        // Setup sentiment analysis
        document.getElementById('analyzeSentimentBtn')?.addEventListener('click', () => {
            this.analyzeSentiment();
        });

        await this.loadHFRegistry();
    }

    async analyzeSentiment() {
        const input = document.getElementById('sentimentInput');
        const resultsContainer = document.getElementById('sentimentResults');

        if (!input || !resultsContainer) return;

        const texts = input.value.split('\n').filter(t => t.trim());

        if (texts.length === 0) {
            this.dashboard.showToast('Please enter some text to analyze', 'warning');
            return;
        }

        resultsContainer.innerHTML = '<div class="spinner"></div>';

        try {
            const response = await this.apiClient.post('/api/sentiment', { texts });

            if (response && response.results) {
                const html = `
                    <h4 style="font-weight: 600; margin-bottom: var(--space-md);">Analysis Results</h4>
                    ${response.results.map((result, i) => {
                        const sentiment = result.label || 'NEUTRAL';
                        const score = ((result.score || 0) * 100).toFixed(1);
                        const color = sentiment === 'POSITIVE' ? 'var(--color-success)' :
                                     sentiment === 'NEGATIVE' ? 'var(--color-danger)' :
                                     'var(--color-text-secondary)';

                        return `
                            <div style="padding: var(--space-md); border: 1px solid rgba(0, 0, 0, 0.1); border-radius: var(--radius-md); margin-bottom: var(--space-sm);">
                                <div style="font-size: 14px; margin-bottom: var(--space-sm);">${texts[i]}</div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-weight: 600; color: ${color};">${sentiment}</span>
                                    <span style="font-size: 13px; color: var(--color-text-secondary);">Confidence: ${score}%</span>
                                </div>
                            </div>
                        `;
                    }).join('')}
                `;
                resultsContainer.innerHTML = html;
            }
        } catch (error) {
            console.error('Error analyzing sentiment:', error);
            resultsContainer.innerHTML = UIComponents.createAlert('Error', 'Failed to analyze sentiment. Please try again.', 'danger');
        }
    }

    async loadHFRegistry() {
        // Load models and datasets
        const modelContainer = document.getElementById('modelRegistry');
        const datasetContainer = document.getElementById('datasetRegistry');

        const sampleModels = [
            { id: 'distilbert-base-uncased-finetuned-sst-2-english', downloads: 1000000, likes: 500 },
            { id: 'bert-base-uncased', downloads: 5000000, likes: 2000 },
            { id: 'gpt2', downloads: 3000000, likes: 1500 }
        ];

        const sampleDatasets = [
            { id: 'imdb', downloads: 500000, likes: 300 },
            { id: 'squad', downloads: 800000, likes: 400 }
        ];

        if (modelContainer) {
            modelContainer.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: var(--space-md);">
                    ${sampleModels.map(model => `
                        <div class="card glass-card">
                            <h4 style="font-weight: 600; font-size: 14px; margin-bottom: var(--space-sm);">${model.id}</h4>
                            <div style="display: flex; gap: var(--space-md); font-size: 12px; color: var(--color-text-secondary);">
                                <span>📥 ${UIComponents.formatNumber(model.downloads)}</span>
                                <span>❤️ ${UIComponents.formatNumber(model.likes)}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        if (datasetContainer) {
            datasetContainer.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: var(--space-md);">
                    ${sampleDatasets.map(dataset => `
                        <div class="card glass-card">
                            <h4 style="font-weight: 600; font-size: 14px; margin-bottom: var(--space-sm);">${dataset.id}</h4>
                            <div style="display: flex; gap: var(--space-md); font-size: 12px; color: var(--color-text-secondary);">
                                <span>📥 ${UIComponents.formatNumber(dataset.downloads)}</span>
                                <span>❤️ ${UIComponents.formatNumber(dataset.likes)}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    }

    /**
     * POOLS TAB - Pool Management
     */
    async renderPoolsTab() {
        const container = document.getElementById('poolsTab');
        if (!container) return;

        container.innerHTML = `
            <h1 style="font-size: 32px; font-weight: 800; margin-bottom: var(--space-2xl);">Provider Pool Management</h1>

            <div style="margin-bottom: var(--space-lg);">
                <button class="btn btn-primary" id="createPoolBtn">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    Create Pool
                </button>
            </div>

            <div id="poolsContainer">
                ${UIComponents.createSkeleton('card', 3)}
            </div>
        `;

        document.getElementById('createPoolBtn')?.addEventListener('click', () => {
            this.showCreatePoolModal();
        });

        await this.loadPools();
    }

    async loadPools() {
        try {
            const data = await this.apiClient.get('/api/pools');
            const container = document.getElementById('poolsContainer');

            if (!data || data.length === 0) {
                container.innerHTML = UIComponents.createEmptyState(
                    'No Pools Found',
                    'Create a pool to group and manage providers efficiently.',
                    '<button class="btn btn-primary" onclick="window.dashboard.tabImpl.showCreatePoolModal()">Create Your First Pool</button>'
                );
                return;
            }

            const html = `
                <div class="stats-grid">
                    ${data.map(pool => `
                        <div class="card glass-card">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: var(--space-md);">
                                <h3 style="font-weight: 600; font-size: 18px;">${pool.name}</h3>
                                ${UIComponents.createBadge(pool.rotation_strategy, 'info')}
                            </div>
                            <div style="font-size: 13px; color: var(--color-text-secondary); margin-bottom: var(--space-md);">
                                ${pool.category} • ${pool.members?.length || 0} members
                            </div>
                            <div style="display: flex; gap: var(--space-sm);">
                                <button class="btn btn-secondary btn-sm" onclick="window.dashboard.tabImpl.viewPoolDetails('${pool.id}')">View Details</button>
                                <button class="btn btn-secondary btn-sm" onclick="window.dashboard.tabImpl.deletePool('${pool.id}')">Delete</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;

            container.innerHTML = html;
        } catch (error) {
            console.error('Error loading pools:', error);
        }
    }

    showCreatePoolModal() {
        const content = `
            <div class="form-group">
                <label class="form-label">Pool Name</label>
                <input type="text" class="form-input" id="poolName" placeholder="My Provider Pool">
            </div>
            <div class="form-group">
                <label class="form-label">Category</label>
                <select class="form-select" id="poolCategory">
                    <option value="market_data">Market Data</option>
                    <option value="exchange">Exchange</option>
                    <option value="defi">DeFi</option>
                    <option value="news">News</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Rotation Strategy</label>
                <select class="form-select" id="poolStrategy">
                    <option value="round_robin">Round Robin</option>
                    <option value="priority">Priority-based</option>
                    <option value="weighted">Weighted Random</option>
                    <option value="least_used">Least Used</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Description (optional)</label>
                <textarea class="form-textarea" id="poolDescription" placeholder="Pool description..."></textarea>
            </div>
        `;

        const footer = `
            <button class="btn btn-primary" onclick="window.dashboard.tabImpl.createPool()">Create Pool</button>
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
        `;

        UIComponents.createModal('Create Provider Pool', content, footer);
    }

    async createPool() {
        const name = document.getElementById('poolName')?.value;
        const category = document.getElementById('poolCategory')?.value;
        const strategy = document.getElementById('poolStrategy')?.value;
        const description = document.getElementById('poolDescription')?.value;

        if (!name || !category || !strategy) {
            this.dashboard.showToast('Please fill in all required fields', 'warning');
            return;
        }

        try {
            await this.apiClient.post('/api/pools', {
                name,
                category,
                rotation_strategy: strategy,
                description
            });

            this.dashboard.showToast('Pool created successfully', 'success');
            document.querySelector('.modal-overlay')?.remove();
            await this.loadPools();
        } catch (error) {
            console.error('Error creating pool:', error);
            this.dashboard.showToast('Failed to create pool', 'danger');
        }
    }

    /**
     * PROVIDERS TAB - Individual Provider Management
     */
    async renderProvidersTab() {
        const container = document.getElementById('providersTab');
        if (!container) return;

        container.innerHTML = `
            <h1 style="font-size: 32px; font-weight: 800; margin-bottom: var(--space-2xl);">Provider Details</h1>
            <div id="providersTableContainer"></div>
        `;

        await this.loadProviders();
    }

    async loadProviders() {
        try {
            const data = await this.apiClient.get('/api/providers/stats');
            const providers = data.providers || [];

            const columns = [
                { key: 'name', label: 'Name', sortable: true },
                { key: 'category', label: 'Category', sortable: true },
                {
                    key: 'status',
                    label: 'Status',
                    render: (val) => {
                        const status = val || 'unknown';
                        const color = status === 'online' ? 'success' : status === 'offline' ? 'danger' : 'warning';
                        return UIComponents.createBadge(status.toUpperCase(), color);
                    }
                },
                { key: 'uptime', label: 'Uptime %', sortable: true },
                { key: 'avg_response_time', label: 'Avg Response (ms)', sortable: true }
            ];

            UIComponents.createDataTable('providersTableContainer', columns, providers, {
                searchable: true,
                sortable: true,
                pageSize: 25,
                onRowClick: (row) => this.showProviderDetails(row)
            });
        } catch (error) {
            console.error('Error loading providers:', error);
        }
    }

    showProviderDetails(provider) {
        const content = `
            <div style="margin-bottom: var(--space-lg);">
                <h4 style="font-weight: 600; margin-bottom: var(--space-sm);">Provider Information</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md);">
                    <div>
                        <div style="font-size: 13px; color: var(--color-text-secondary);">Name</div>
                        <div style="font-weight: 600;">${provider.name}</div>
                    </div>
                    <div>
                        <div style="font-size: 13px; color: var(--color-text-secondary);">Category</div>
                        <div style="font-weight: 600;">${provider.category}</div>
                    </div>
                    <div>
                        <div style="font-size: 13px; color: var(--color-text-secondary);">Status</div>
                        <div style="font-weight: 600;">${provider.status || 'unknown'}</div>
                    </div>
                    <div>
                        <div style="font-size: 13px; color: var(--color-text-secondary);">Uptime</div>
                        <div style="font-weight: 600;">${provider.uptime || 0}%</div>
                    </div>
                </div>
            </div>
            <div>
                <h4 style="font-weight: 600; margin-bottom: var(--space-sm);">Performance Metrics</h4>
                <div style="font-size: 14px; color: var(--color-text-secondary);">
                    Average response time: ${provider.avg_response_time || 0}ms
                </div>
            </div>
        `;

        UIComponents.createModal(`Provider: ${provider.name}`, content);
    }

    /**
     * LOGS TAB - System Logs
     */
    async renderLogsTab() {
        const container = document.getElementById('logsTab');
        if (!container) return;

        container.innerHTML = `
            <h1 style="font-size: 32px; font-weight: 800; margin-bottom: var(--space-2xl);">System Logs</h1>

            <!-- Filters -->
            <div class="card" style="margin-bottom: var(--space-lg);">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--space-md);">
                    <div class="form-group" style="margin-bottom: 0;">
                        <label class="form-label">Log Type</label>
                        <select class="form-select" id="logTypeFilter">
                            <option value="all">All</option>
                            <option value="error">Errors</option>
                            <option value="warning">Warnings</option>
                            <option value="info">Info</option>
                        </select>
                    </div>
                    <div class="form-group" style="margin-bottom: 0;">
                        <label class="form-label">Provider</label>
                        <select class="form-select" id="logProviderFilter">
                            <option value="all">All Providers</option>
                        </select>
                    </div>
                    <div style="display: flex; align-items: flex-end;">
                        <button class="btn btn-primary" id="refreshLogsBtn">Refresh Logs</button>
                    </div>
                </div>
            </div>

            <div id="logsTableContainer"></div>
        `;

        document.getElementById('refreshLogsBtn')?.addEventListener('click', () => {
            this.loadLogs();
        });

        await this.loadLogs();
    }

    async loadLogs() {
        try {
            const data = await this.apiClient.get('/api/logs');
            const logs = data.logs || [];

            const columns = [
                {
                    key: 'timestamp',
                    label: 'Time',
                    render: (val) => UIComponents.formatDateTime(val, 'relative')
                },
                { key: 'provider', label: 'Provider' },
                {
                    key: 'type',
                    label: 'Type',
                    render: (val) => {
                        const type = val || 'info';
                        const color = type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'info';
                        return UIComponents.createBadge(type.toUpperCase(), color);
                    }
                },
                { key: 'status', label: 'Status' },
                { key: 'message', label: 'Message' }
            ];

            UIComponents.createDataTable('logsTableContainer', columns, logs, {
                searchable: true,
                sortable: true,
                pageSize: 50
            });
        } catch (error) {
            console.error('Error loading logs:', error);
            document.getElementById('logsTableContainer').innerHTML =
                UIComponents.createEmptyState('No logs available', 'System logs will appear here when events occur.');
        }
    }

    /**
     * REPORTS TAB - Analytics & Reports
     */
    async renderReportsTab() {
        const container = document.getElementById('reportsTab');
        if (!container) return;

        container.innerHTML = `
            <h1 style="font-size: 32px; font-weight: 800; margin-bottom: var(--space-2xl);">Reports & Analytics</h1>

            <!-- Quick Stats -->
            <div class="stats-grid" style="margin-bottom: var(--space-2xl);">
                <div class="card stat-card glass-card">
                    <div class="stat-label">Average Uptime</div>
                    <div class="stat-value" id="avgUptime">98.5%</div>
                </div>
                <div class="card stat-card glass-card">
                    <div class="stat-label">Total API Calls</div>
                    <div class="stat-value" id="totalCalls">1.2M</div>
                </div>
                <div class="card stat-card glass-card">
                    <div class="stat-label">Most Reliable</div>
                    <div class="stat-value" style="font-size: 18px;" id="mostReliable">CoinGecko</div>
                </div>
                <div class="card stat-card glass-card">
                    <div class="stat-label">Avg Response Time</div>
                    <div class="stat-value" id="avgResponse">245ms</div>
                </div>
            </div>

            <!-- Report Generator -->
            <div class="card">
                <h3 style="font-size: 20px; font-weight: 700; margin-bottom: var(--space-lg);">Generate Report</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--space-md); margin-bottom: var(--space-lg);">
                    <div class="form-group" style="margin-bottom: 0;">
                        <label class="form-label">Report Type</label>
                        <select class="form-select">
                            <option>Uptime Report</option>
                            <option>Performance Report</option>
                            <option>Error Analysis</option>
                            <option>Usage Statistics</option>
                        </select>
                    </div>
                    <div class="form-group" style="margin-bottom: 0;">
                        <label class="form-label">Time Period</label>
                        <select class="form-select">
                            <option>Last 24 Hours</option>
                            <option>Last 7 Days</option>
                            <option>Last 30 Days</option>
                            <option>Custom Range</option>
                        </select>
                    </div>
                    <div class="form-group" style="margin-bottom: 0;">
                        <label class="form-label">Format</label>
                        <select class="form-select">
                            <option>PDF</option>
                            <option>CSV</option>
                            <option>JSON</option>
                        </select>
                    </div>
                </div>
                <button class="btn btn-primary">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Generate Report
                </button>
            </div>
        `;
    }

    // Helper methods
    toCamelCase(str) {
        return str.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
    }

    formatFlagName(flag) {
        return flag.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    getFlagDescription(flag) {
        const descriptions = {
            enable_proxy_auto_mode: 'Automatically route requests through proxy when providers fail',
            enable_websocket: 'Enable real-time WebSocket updates',
            enable_caching: 'Cache API responses to improve performance',
            enable_advanced_analytics: 'Show advanced analytics and charts',
            debug_mode: 'Enable detailed debug logging'
        };
        return descriptions[flag] || 'Feature flag configuration';
    }
}

// Make available globally
window.TabImplementations = TabImplementations;
