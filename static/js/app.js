// Crypto Intelligence Hub - Main JavaScript

// Global state
const AppState = {
    currentTab: 'dashboard',
    data: {},
    charts: {}
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    checkAPIStatus();
    loadDashboard();
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        if (AppState.currentTab === 'dashboard') {
            loadDashboard();
        }
    }, 30000);
    
    // Listen for trading pairs loaded event
    document.addEventListener('tradingPairsLoaded', function(e) {
        console.log('Trading pairs loaded:', e.detail.pairs.length);
        initTradingPairSelectors();
    });
});

// Initialize trading pair selectors after pairs are loaded
function initTradingPairSelectors() {
    // Initialize asset symbol selector
    const assetSymbolContainer = document.getElementById('asset-symbol-container');
    if (assetSymbolContainer && window.TradingPairsLoader) {
        const pairs = window.TradingPairsLoader.getTradingPairs();
        if (pairs && pairs.length > 0) {
            assetSymbolContainer.innerHTML = window.TradingPairsLoader.createTradingPairCombobox(
                'asset-symbol',
                'Select or type trading pair',
                'BTCUSDT'
            );
        }
    }
}

// Tab Navigation
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            
            // Update buttons
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update content
            tabContents.forEach(c => c.classList.remove('active'));
            document.getElementById(`tab-${tabId}`).classList.add('active');
            
            AppState.currentTab = tabId;
            
            // Load tab data
            loadTabData(tabId);
        });
    });
}

// Load tab-specific data - synchronized with HTML tabs
function loadTabData(tabId) {
    switch(tabId) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'market':
            loadMarketData();
            break;
        case 'models':
            loadModels();
            break;
        case 'sentiment':
            loadSentimentModels();  // Populate model dropdown
            loadSentimentHistory();  // Load history from localStorage
            break;
        case 'ai-analyst':
            // AI analyst tab is interactive, no auto-load needed
            break;
        case 'trading-assistant':
            // Trading assistant tab is interactive, no auto-load needed
            break;
        case 'news':
            loadNews();
            break;
        case 'providers':
            loadProviders();
            break;
        case 'diagnostics':
            loadDiagnostics();
            break;
        case 'api-explorer':
            loadAPIEndpoints();
            break;
        default:
            console.log('No specific loader for tab:', tabId);
    }
}

// Load available API endpoints
function loadAPIEndpoints() {
    const endpointSelect = document.getElementById('api-endpoint');
    if (!endpointSelect) return;
    
    // Add more endpoints
    const endpoints = [
        { value: '/api/health', text: 'GET /api/health - Health Check' },
        { value: '/api/status', text: 'GET /api/status - System Status' },
        { value: '/api/stats', text: 'GET /api/stats - Statistics' },
        { value: '/api/market', text: 'GET /api/market - Market Data' },
        { value: '/api/trending', text: 'GET /api/trending - Trending Coins' },
        { value: '/api/sentiment', text: 'GET /api/sentiment - Fear & Greed Index' },
        { value: '/api/news', text: 'GET /api/news - Latest News' },
        { value: '/api/news/latest', text: 'GET /api/news/latest - Latest News (Alt)' },
        { value: '/api/resources', text: 'GET /api/resources - Resources Summary' },
        { value: '/api/providers', text: 'GET /api/providers - List Providers' },
        { value: '/api/models/list', text: 'GET /api/models/list - List Models' },
        { value: '/api/models/status', text: 'GET /api/models/status - Models Status' },
        { value: '/api/models/data/stats', text: 'GET /api/models/data/stats - Models Statistics' },
        { value: '/api/analyze/text', text: 'POST /api/analyze/text - AI Text Analysis' },
        { value: '/api/trading/decision', text: 'POST /api/trading/decision - Trading Signal' },
        { value: '/api/sentiment/analyze', text: 'POST /api/sentiment/analyze - Analyze Sentiment' },
        { value: '/api/logs/recent', text: 'GET /api/logs/recent - Recent Logs' },
        { value: '/api/logs/errors', text: 'GET /api/logs/errors - Error Logs' },
        { value: '/api/diagnostics/last', text: 'GET /api/diagnostics/last - Last Diagnostics' },
        { value: '/api/hf/models', text: 'GET /api/hf/models - HF Models' },
        { value: '/api/hf/health', text: 'GET /api/hf/health - HF Health' }
    ];
    
    // Clear existing options except first one
    endpointSelect.innerHTML = '<option value="">Select Endpoint...</option>';
    endpoints.forEach(ep => {
        const option = document.createElement('option');
        option.value = ep.value;
        option.textContent = ep.text;
        endpointSelect.appendChild(option);
    });
}

// Check API Status
async function checkAPIStatus() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        const statusBadge = document.getElementById('api-status');
        if (data.status === 'healthy') {
            statusBadge.className = 'status-badge';
            statusBadge.innerHTML = '<span class="status-dot"></span><span>✅ System Active</span>';
        } else {
            statusBadge.className = 'status-badge error';
            statusBadge.innerHTML = '<span class="status-dot"></span><span>❌ Error</span>';
        }
    } catch (error) {
        const statusBadge = document.getElementById('api-status');
        statusBadge.className = 'status-badge error';
        statusBadge.innerHTML = '<span class="status-dot"></span><span>❌ Connection Failed</span>';
    }
}

// Load Dashboard
async function loadDashboard() {
    // Show loading state
    const statsElements = [
        'stat-total-resources', 'stat-free-resources', 
        'stat-models', 'stat-providers'
    ];
    statsElements.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = '...';
    });
    
    const systemStatusDiv = document.getElementById('system-status');
    if (systemStatusDiv) {
        systemStatusDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Loading system status...</div>';
    }
    
    try {
        // Load resources
        const resourcesRes = await fetch('/api/resources');
        const resourcesData = await resourcesRes.json();
        
        if (resourcesData.success && resourcesData.summary) {
            document.getElementById('stat-total-resources').textContent = resourcesData.summary.total_resources || 0;
            document.getElementById('stat-free-resources').textContent = resourcesData.summary.free_resources || 0;
            document.getElementById('stat-models').textContent = resourcesData.summary.models_available || 0;
        }
        
        // Load system status
        try {
            const statusRes = await fetch('/api/status');
            const statusData = await statusRes.json();
            
            document.getElementById('stat-providers').textContent = statusData.total_apis || statusData.total_providers || 0;
            
            // Display system status
            const systemStatusDiv = document.getElementById('system-status');
            const healthStatus = statusData.system_health || 'unknown';
            const healthClass = healthStatus === 'healthy' ? 'alert-success' : 
                               healthStatus === 'degraded' ? 'alert-warning' : 'alert-error';
            
            systemStatusDiv.innerHTML = `
                <div class="alert ${healthClass}">
                    <strong>System Status:</strong> ${healthStatus}<br>
                    <strong>Online APIs:</strong> ${statusData.online || 0}<br>
                    <strong>Degraded APIs:</strong> ${statusData.degraded || 0}<br>
                    <strong>Offline APIs:</strong> ${statusData.offline || 0}<br>
                    <strong>Avg Response Time:</strong> ${statusData.avg_response_time_ms || 0}ms<br>
                    <strong>Last Update:</strong> ${new Date(statusData.last_update || Date.now()).toLocaleString('en-US')}
                </div>
            `;
        } catch (statusError) {
            console.warn('Status endpoint not available:', statusError);
            document.getElementById('stat-providers').textContent = '-';
        }
        
        // Load categories chart
        if (resourcesData.success && resourcesData.summary.categories) {
            createCategoriesChart(resourcesData.summary.categories);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Failed to load dashboard. Please check the backend is running.');
        
        // Show error state
        const systemStatusDiv = document.getElementById('system-status');
        if (systemStatusDiv) {
            systemStatusDiv.innerHTML = '<div class="alert alert-error">Failed to load dashboard data. Please refresh or check backend status.</div>';
        }
    }
}

// Create Categories Chart
function createCategoriesChart(categories) {
    const ctx = document.getElementById('categories-chart');
    if (!ctx) return;
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        ctx.parentElement.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 20px;">Chart library not loaded</p>';
        return;
    }
    
    if (AppState.charts.categories) {
        AppState.charts.categories.destroy();
    }
    
    AppState.charts.categories = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(categories),
            datasets: [{
                label: 'Total Resources',
                data: Object.values(categories),
                backgroundColor: 'rgba(102, 126, 234, 0.6)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// Load Market Data
async function loadMarketData() {
    // Show loading states
    const marketDiv = document.getElementById('market-data');
    const trendingDiv = document.getElementById('trending-coins');
    const fgDiv = document.getElementById('fear-greed');
    
    if (marketDiv) marketDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Loading market data...</div>';
    if (trendingDiv) trendingDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Loading trending coins...</div>';
    if (fgDiv) fgDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Loading Fear & Greed Index...</div>';
    
    try {
        const response = await fetch('/api/market');
        const data = await response.json();
        
        if (data.cryptocurrencies && data.cryptocurrencies.length > 0) {
            const marketDiv = document.getElementById('market-data');
            marketDiv.innerHTML = `
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Name</th>
                                <th>Price (USD)</th>
                                <th>24h Change</th>
                                <th>24h Volume</th>
                                <th>Market Cap</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.cryptocurrencies.map(coin => `
                                <tr>
                                    <td>${coin.rank || '-'}</td>
                                    <td>
                                        ${coin.image ? `<img src="${coin.image}" style="width: 24px; height: 24px; margin-left: 8px; vertical-align: middle;" />` : ''}
                                        <strong>${coin.symbol}</strong> ${coin.name}
                                    </td>
                                    <td>$${formatNumber(coin.price)}</td>
                                    <td style="color: ${coin.change_24h >= 0 ? 'var(--success)' : 'var(--danger)'}; font-weight: 600;">
                                        ${coin.change_24h >= 0 ? '↑' : '↓'} ${Math.abs(coin.change_24h || 0).toFixed(2)}%
                                    </td>
                                    <td>$${formatNumber(coin.volume_24h)}</td>
                                    <td>$${formatNumber(coin.market_cap)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                ${data.total_market_cap ? `<div style="margin-top: 15px; padding: 15px; background: rgba(102, 126, 234, 0.1); border-radius: 10px;">
                    <strong>Total Market Cap:</strong> $${formatNumber(data.total_market_cap)} | 
                    <strong>BTC Dominance:</strong> ${(data.btc_dominance || 0).toFixed(2)}%
                </div>` : ''}
            `;
        } else {
            document.getElementById('market-data').innerHTML = '<div class="alert alert-warning">No data found</div>';
        }
        
        // Load trending
        try {
            const trendingRes = await fetch('/api/trending');
            const trendingData = await trendingRes.json();
            
            if (trendingData.trending && trendingData.trending.length > 0) {
                const trendingDiv = document.getElementById('trending-coins');
                trendingDiv.innerHTML = `
                    <div style="display: grid; gap: 10px;">
                        ${trendingData.trending.map((coin, index) => `
                            <div style="padding: 15px; background: rgba(31, 41, 55, 0.6); border-radius: 10px; display: flex; justify-content: space-between; align-items: center; border-left: 4px solid var(--primary);">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span style="font-size: 18px; font-weight: 800; color: var(--primary);">#${index + 1}</span>
                                    <div>
                                        <strong>${coin.symbol || coin.id}</strong> - ${coin.name || 'Unknown'}
                                        ${coin.market_cap_rank ? `<div style="font-size: 12px; color: var(--text-secondary);">Market Cap Rank: ${coin.market_cap_rank}</div>` : ''}
                                    </div>
                                </div>
                                <div style="font-size: 20px; font-weight: 700; color: var(--success);">${coin.score ? coin.score.toFixed(2) : 'N/A'}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else {
                document.getElementById('trending-coins').innerHTML = '<div class="alert alert-warning">No data found</div>';
            }
        } catch (trendingError) {
            console.warn('Trending endpoint error:', trendingError);
            document.getElementById('trending-coins').innerHTML = '<div class="alert alert-error">Error loading trending coins</div>';
        }
        
        // Load Fear & Greed
        try {
            const sentimentRes = await fetch('/api/sentiment');
            const sentimentData = await sentimentRes.json();
            
            if (sentimentData.fear_greed_index !== undefined) {
                const fgDiv = document.getElementById('fear-greed');
                const fgValue = sentimentData.fear_greed_index;
                const fgLabel = sentimentData.fear_greed_label || 'Unknown';
                
                // Determine color based on value
                let fgColor = 'var(--warning)';
                if (fgValue >= 75) fgColor = 'var(--success)';
                else if (fgValue >= 50) fgColor = 'var(--info)';
                else if (fgValue >= 25) fgColor = 'var(--warning)';
                else fgColor = 'var(--danger)';
                
                fgDiv.innerHTML = `
                    <div style="text-align: center; padding: 30px;">
                        <div style="font-size: 72px; font-weight: 800; margin-bottom: 10px; color: ${fgColor};">
                            ${fgValue}
                        </div>
                        <div style="font-size: 24px; font-weight: 600; color: var(--text-primary); margin-bottom: 10px;">
                            ${fgLabel}
                        </div>
                        <div style="font-size: 14px; color: var(--text-secondary);">
                            Market Fear & Greed Index
                        </div>
                        ${sentimentData.timestamp ? `<div style="font-size: 12px; color: var(--text-secondary); margin-top: 10px;">
                            Last Update: ${new Date(sentimentData.timestamp).toLocaleString('en-US')}
                        </div>` : ''}
                    </div>
                `;
            } else {
                document.getElementById('fear-greed').innerHTML = '<div class="alert alert-warning">No data found</div>';
            }
        } catch (sentimentError) {
            console.warn('Sentiment endpoint error:', sentimentError);
            document.getElementById('fear-greed').innerHTML = '<div class="alert alert-error">Error loading Fear & Greed Index</div>';
        }
    } catch (error) {
        console.error('Error loading market data:', error);
        showError('Failed to load market data. Please check the backend connection.');
        
        const marketDiv = document.getElementById('market-data');
        if (marketDiv) {
            marketDiv.innerHTML = '<div class="alert alert-error">Failed to load market data. The backend may be offline or the CoinGecko API may be unavailable.</div>';
        }
    }
}

// Format large numbers
function formatNumber(num) {
    if (!num) return '0';
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toLocaleString('en-US', { maximumFractionDigits: 2 });
}

// Load Models
async function loadModels() {
    // Show loading state
    const modelsListDiv = document.getElementById('models-list');
    const statusDiv = document.getElementById('models-status');
    
    if (modelsListDiv) modelsListDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Loading models...</div>';
    if (statusDiv) statusDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Loading status...</div>';
    
    try {
        const response = await fetch('/api/models/list');
        const data = await response.json();
        
        const models = data.models || data || [];
        
        if (models.length > 0) {
            const modelsListDiv = document.getElementById('models-list');
            modelsListDiv.innerHTML = `
                <div style="display: grid; gap: 15px;">
                    ${models.map(model => {
                        const status = model.status || 'unknown';
                        const isAvailable = status === 'available' || status === 'loaded';
                        const statusColor = isAvailable ? 'var(--success)' : 'var(--danger)';
                        const statusBg = isAvailable ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)';
                        
                        return `
                            <div style="padding: 20px; background: rgba(31, 41, 55, 0.6); border-radius: 12px; border-left: 4px solid ${statusColor};">
                                <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 10px;">
                                    <div style="flex: 1;">
                                        <h4 style="margin-bottom: 5px; color: var(--text-primary);">${model.model_id || model.name || 'Unknown'}</h4>
                                        <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 5px;">
                                            ${model.task || model.category || 'N/A'}
                                        </div>
                                        ${model.category ? `<div style="font-size: 11px; color: var(--text-secondary);">Category: ${model.category}</div>` : ''}
                                        ${model.requires_auth !== undefined ? `<div style="font-size: 11px; color: var(--text-secondary);">
                                            ${model.requires_auth ? '🔐 Requires Authentication' : '🔓 No Auth Required'}
                                        </div>` : ''}
                                    </div>
                                    <span style="background: ${statusBg}; color: ${statusColor}; padding: 5px 10px; border-radius: 5px; font-size: 12px; font-weight: 600;">
                                        ${isAvailable ? '✅ Available' : '❌ Unavailable'}
                                    </span>
                                </div>
                                ${model.key ? `<div style="margin-top: 10px; font-size: 11px; color: var(--text-secondary); font-family: monospace;">
                                    Key: ${model.key}
                                </div>` : ''}
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
        } else {
            document.getElementById('models-list').innerHTML = '<div class="alert alert-warning">No models found</div>';
        }
        
        // Load models status
        try {
            const statusRes = await fetch('/api/models/status');
            const statusData = await statusRes.json();
            
            const statusDiv = document.getElementById('models-status');
            if (statusDiv) {
                // Use honest status from backend
                const status = statusData.status || 'unknown';
                const statusMessage = statusData.status_message || 'Unknown status';
                const hfMode = statusData.hf_mode || 'unknown';
                const modelsLoaded = statusData.models_loaded || statusData.pipelines_loaded || 0;
                const modelsFailed = statusData.models_failed || 0;
                
                // Determine status class based on honest status
                let statusClass = 'alert-warning';
                if (status === 'ok') statusClass = 'alert-success';
                else if (status === 'disabled' || status === 'transformers_unavailable') statusClass = 'alert-error';
                else if (status === 'partial') statusClass = 'alert-warning';
                
                statusDiv.innerHTML = `
                    <div class="alert ${statusClass}">
                        <strong>Status:</strong> ${statusMessage}<br>
                        <strong>HF Mode:</strong> ${hfMode}<br>
                        <strong>Models Loaded:</strong> ${modelsLoaded}<br>
                        <strong>Models Failed:</strong> ${modelsFailed}<br>
                        ${statusData.transformers_available !== undefined ? `<strong>Transformers Available:</strong> ${statusData.transformers_available ? '✅ Yes' : '❌ No'}<br>` : ''}
                        ${statusData.initialized !== undefined ? `<strong>Initialized:</strong> ${statusData.initialized ? '✅ Yes' : '❌ No'}<br>` : ''}
                        ${hfMode === 'off' ? `<div style="margin-top: 10px; padding: 10px; background: rgba(239, 68, 68, 0.1); border-radius: 5px; font-size: 12px;">
                            <strong>Note:</strong> HF models are disabled (HF_MODE=off). To enable them, set HF_MODE=public or HF_MODE=auth in the environment.
                        </div>` : ''}
                        ${hfMode !== 'off' && modelsLoaded === 0 && modelsFailed > 0 ? `<div style="margin-top: 10px; padding: 10px; background: rgba(245, 158, 11, 0.1); border-radius: 5px; font-size: 12px;">
                            <strong>Warning:</strong> No models could be loaded. ${modelsFailed} model(s) failed. Check model IDs or HF access.
                        </div>` : ''}
                    </div>
                `;
            }
        } catch (statusError) {
            console.warn('Models status endpoint error:', statusError);
        }
        
        // Load models stats
        try {
            const statsRes = await fetch('/api/models/data/stats');
            const statsData = await statsRes.json();
            
            if (statsData.success && statsData.statistics) {
                const statsDiv = document.getElementById('models-stats');
                statsDiv.innerHTML = `
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        <div style="padding: 15px; background: rgba(102, 126, 234, 0.1); border-radius: 10px;">
                            <div style="font-size: 28px; font-weight: 800; color: var(--primary);">${statsData.statistics.total_analyses || 0}</div>
                            <div style="font-size: 14px; color: var(--text-secondary);">Total Analyses</div>
                        </div>
                        <div style="padding: 15px; background: rgba(16, 185, 129, 0.1); border-radius: 10px;">
                            <div style="font-size: 28px; font-weight: 800; color: var(--success);">${statsData.statistics.unique_symbols || 0}</div>
                            <div style="font-size: 14px; color: var(--text-secondary);">Unique Symbols</div>
                        </div>
                        ${statsData.statistics.most_used_model ? `
                            <div style="padding: 15px; background: rgba(245, 158, 11, 0.1); border-radius: 10px;">
                                <div style="font-size: 18px; font-weight: 800; color: var(--warning);">${statsData.statistics.most_used_model}</div>
                                <div style="font-size: 14px; color: var(--text-secondary);">Most Used Model</div>
                            </div>
                        ` : ''}
                    </div>
                `;
            }
        } catch (statsError) {
            console.warn('Models stats endpoint error:', statsError);
        }
    } catch (error) {
        console.error('Error loading models:', error);
        showError('Failed to load models. Please check the backend connection.');
        
        const modelsListDiv = document.getElementById('models-list');
        if (modelsListDiv) {
            modelsListDiv.innerHTML = '<div class="alert alert-error">Failed to load models. Check backend status.</div>';
        }
    }
}

// Initialize Models
async function initializeModels() {
    try {
        const response = await fetch('/api/models/initialize', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Models loaded successfully');
            loadModels();
        } else {
            showError(data.error || 'Error loading models');
        }
    } catch (error) {
        showError('Error loading models: ' + error.message);
    }
}

// Load Sentiment Models - updated to populate dropdown for sentiment analysis
async function loadSentimentModels() {
    try {
        const response = await fetch('/api/models/list');
        const data = await response.json();
        
        const models = data.models || data || [];
        const select = document.getElementById('sentiment-model');
        if (!select) return;
        
        select.innerHTML = '<option value="">Auto (Mode-based)</option>';
        
        // Filter and add models - only sentiment and generation models
        models.filter(m => {
            const category = m.category || '';
            const task = m.task || '';
            // Include sentiment models and generation/trading models
            return category.includes('sentiment') || 
                   category.includes('generation') || 
                   category.includes('trading') ||
                   task.includes('classification') ||
                   task.includes('generation');
        }).forEach(model => {
            const option = document.createElement('option');
            const modelKey = model.key || model.id;
            const modelName = model.model_id || model.name || modelKey;
            const desc = model.description || model.category || '';
            
            option.value = modelKey;
            // Show model name with short description
            const displayName = modelName.length > 40 ? modelName.substring(0, 37) + '...' : modelName;
            option.textContent = displayName;
            option.title = desc; // Full description on hover
            select.appendChild(option);
        });
        
        // If no models available, show message
        if (select.options.length === 1) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No models available - will use fallback';
            option.disabled = true;
            select.appendChild(option);
        }
        
        console.log(`Loaded ${select.options.length - 1} sentiment models into dropdown`);
    } catch (error) {
        console.error('Error loading sentiment models:', error);
        const select = document.getElementById('sentiment-model');
        if (select) {
            select.innerHTML = '<option value="">Auto (Mode-based)</option>';
        }
    }
}

// Analyze Global Market Sentiment
async function analyzeGlobalSentiment() {
    const resultDiv = document.getElementById('global-sentiment-result');
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Analyzing market sentiment...</div>';
    
    try {
        // Use market text analysis with sample market-related text
        const marketText = "Cryptocurrency market analysis: Bitcoin, Ethereum, and major altcoins showing mixed signals. Market sentiment analysis required.";
        
        const response = await fetch('/api/sentiment/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: marketText, mode: 'crypto' })
        });
        
        const data = await response.json();
        
        if (!data.available) {
            resultDiv.innerHTML = `
                <div class="alert alert-warning">
                    <strong>⚠️ Models Not Available:</strong> ${data.error || 'AI models are currently unavailable'}
                </div>
            `;
            return;
        }
        
        const sentiment = data.sentiment || 'neutral';
        const confidence = data.confidence || 0;
        const sentimentEmoji = sentiment === 'bullish' ? '📈' : sentiment === 'bearish' ? '📉' : '➡️';
        const sentimentColor = sentiment === 'bullish' ? 'var(--success)' : sentiment === 'bearish' ? 'var(--danger)' : 'var(--text-secondary)';
        
        resultDiv.innerHTML = `
            <div class="alert alert-success" style="border-left: 4px solid ${sentimentColor};">
                <h4 style="margin-bottom: 15px;">Global Market Sentiment</h4>
                <div style="display: grid; gap: 10px;">
                    <div style="text-align: center; padding: 20px;">
                        <div style="font-size: 48px; margin-bottom: 10px;">${sentimentEmoji}</div>
                        <div style="font-size: 24px; font-weight: 700; color: ${sentimentColor}; margin-bottom: 5px;">
                            ${sentiment === 'bullish' ? 'Bullish' : sentiment === 'bearish' ? 'Bearish' : 'Neutral'}
                        </div>
                        <div style="color: var(--text-secondary);">
                            Confidence: ${(confidence * 100).toFixed(1)}%
                        </div>
                    </div>
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border);">
                        <strong>Details:</strong>
                        <div style="margin-top: 5px; font-size: 13px; color: var(--text-secondary);">
                            This analysis is based on AI models.
                        </div>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Global sentiment analysis error:', error);
        resultDiv.innerHTML = `<div class="alert alert-error">Analysis Error: ${error.message}</div>`;
        showError('Error analyzing market sentiment');
    }
}

// Analyze Asset Sentiment
async function analyzeAssetSentiment() {
    const symbol = document.getElementById('asset-symbol').value.trim().toUpperCase();
    const text = document.getElementById('asset-sentiment-text').value.trim();
    
    if (!symbol) {
        showError('Please enter a cryptocurrency symbol');
        return;
    }
    
    const resultDiv = document.getElementById('asset-sentiment-result');
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Analyzing...</div>';
    
    try {
        // Use provided text or default text with symbol
        const analysisText = text || `${symbol} market analysis and sentiment`;
        
        const response = await fetch('/api/sentiment/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: analysisText, mode: 'crypto', symbol: symbol })
        });
        
        const data = await response.json();
        
        if (!data.available) {
            resultDiv.innerHTML = `
                <div class="alert alert-warning">
                    <strong>⚠️ Models Not Available:</strong> ${data.error || 'AI models are currently unavailable'}
                </div>
            `;
            return;
        }
        
        const sentiment = data.sentiment || 'neutral';
        const confidence = data.confidence || 0;
        const sentimentEmoji = sentiment === 'bullish' ? '📈' : sentiment === 'bearish' ? '📉' : '➡️';
        const sentimentColor = sentiment === 'bullish' ? 'var(--success)' : sentiment === 'bearish' ? 'var(--danger)' : 'var(--text-secondary)';
        
        resultDiv.innerHTML = `
            <div class="alert alert-success" style="border-left: 4px solid ${sentimentColor};">
                <h4 style="margin-bottom: 15px;">Sentiment Analysis Result for ${symbol}</h4>
                <div style="display: grid; gap: 10px;">
                    <div>
                        <strong>Sentiment:</strong> 
                        <span style="color: ${sentimentColor}; font-weight: 700; font-size: 18px;">
                            ${sentimentEmoji} ${sentiment === 'bullish' ? 'Bullish' : sentiment === 'bearish' ? 'Bearish' : 'Neutral'}
                        </span>
                    </div>
                    <div>
                        <strong>Confidence:</strong> 
                        <span style="color: var(--primary); font-weight: 600;">
                            ${(confidence * 100).toFixed(2)}%
                        </span>
                    </div>
                    ${text ? `
                        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border);">
                            <strong>Analyzed Text:</strong>
                            <div style="margin-top: 5px; padding: 10px; background: rgba(31, 41, 55, 0.6); border-radius: 5px; font-size: 13px; color: var(--text-secondary);">
                                "${text.substring(0, 200)}${text.length > 200 ? '...' : ''}"
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Asset sentiment analysis error:', error);
        resultDiv.innerHTML = `<div class="alert alert-error">Analysis Error: ${error.message}</div>`;
        showError('Error analyzing asset sentiment');
    }
}

// Analyze News Sentiment
async function analyzeNewsSentiment() {
    const title = document.getElementById('news-title').value.trim();
    const content = document.getElementById('news-content').value.trim();
    
    if (!title && !content) {
        showError('Please enter news title or content');
        return;
    }
    
    const resultDiv = document.getElementById('news-sentiment-result');
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Analyzing...</div>';
    
    try {
        const response = await fetch('/api/news/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title, content: content, description: content })
        });
        
        const data = await response.json();
        
        if (!data.available) {
            resultDiv.innerHTML = `
                <div class="alert alert-warning">
                    <strong>⚠️ Models Not Available:</strong> ${data.news?.error || data.error || 'AI models are currently unavailable'}
                </div>
            `;
            return;
        }
        
        const newsData = data.news || {};
        const sentiment = newsData.sentiment || 'neutral';
        const confidence = newsData.confidence || 0;
        const sentimentEmoji = sentiment === 'bullish' || sentiment === 'positive' ? '📈' : 
                              sentiment === 'bearish' || sentiment === 'negative' ? '📉' : '➡️';
        const sentimentColor = sentiment === 'bullish' || sentiment === 'positive' ? 'var(--success)' : 
                              sentiment === 'bearish' || sentiment === 'negative' ? 'var(--danger)' : 'var(--text-secondary)';
        
        resultDiv.innerHTML = `
            <div class="alert alert-success" style="border-left: 4px solid ${sentimentColor};">
                <h4 style="margin-bottom: 15px;">News Sentiment Analysis Result</h4>
                <div style="display: grid; gap: 10px;">
                    <div>
                        <strong>Title:</strong> 
                        <span style="color: var(--text-primary);">${title || 'No title'}</span>
                    </div>
                    <div>
                        <strong>Sentiment:</strong> 
                        <span style="color: ${sentimentColor}; font-weight: 700; font-size: 18px;">
                            ${sentimentEmoji} ${sentiment === 'bullish' || sentiment === 'positive' ? 'Positive' : 
                              sentiment === 'bearish' || sentiment === 'negative' ? 'Negative' : 'Neutral'}
                        </span>
                    </div>
                    <div>
                        <strong>Confidence:</strong> 
                        <span style="color: var(--primary); font-weight: 600;">
                            ${(confidence * 100).toFixed(2)}%
                        </span>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('News sentiment analysis error:', error);
        resultDiv.innerHTML = `<div class="alert alert-error">Analysis Error: ${error.message}</div>`;
        showError('Error analyzing news sentiment');
    }
}

// Summarize News
async function summarizeNews() {
    const title = document.getElementById('summary-news-title').value.trim();
    const content = document.getElementById('summary-news-content').value.trim();
    
    if (!title && !content) {
        showError('Please enter news title or content');
        return;
    }
    
    const resultDiv = document.getElementById('news-summary-result');
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Generating summary...</div>';
    
    try {
        const response = await fetch('/api/news/summarize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title, content: content })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            resultDiv.innerHTML = `
                <div class="alert alert-error">
                    <strong>❌ Summarization Failed:</strong> ${data.error || 'Failed to generate summary'}
                </div>
            `;
            return;
        }
        
        const summary = data.summary || '';
        const model = data.model || 'Unknown';
        const isHFModel = data.available !== false && model !== 'fallback_extractive';
        const modelDisplay = isHFModel ? model : `${model} (Fallback)`;
        
        // Create collapsible card with summary
        resultDiv.innerHTML = `
            <div class="alert alert-success" style="border-left: 4px solid var(--primary);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h4 style="margin: 0;">📝 News Summary</h4>
                    <button class="btn-secondary" onclick="toggleSummaryDetails()" style="padding: 5px 10px; font-size: 12px;">
                        <span id="toggle-summary-icon">▼</span> Details
                    </button>
                </div>
                
                ${title ? `<div style="margin-bottom: 10px;">
                    <strong>Title:</strong> 
                    <span style="color: var(--text-primary);">${title}</span>
                </div>` : ''}
                
                <div style="background: var(--bg-card); padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <strong style="color: var(--primary);">Summary:</strong>
                    <p style="margin-top: 10px; line-height: 1.6; color: var(--text-primary);">
                        ${summary}
                    </p>
                </div>
                
                <div id="summary-details" style="display: none; margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border);">
                    <div style="display: grid; gap: 10px;">
                        <div>
                            <strong>Model:</strong> 
                            <span style="color: var(--text-secondary);">${modelDisplay}</span>
                            ${!isHFModel ? '<span style="color: var(--warning); font-size: 12px; margin-left: 5px;">⚠️ HF model unavailable</span>' : ''}
                        </div>
                        ${data.input_length ? `<div>
                            <strong>Input Length:</strong> 
                            <span style="color: var(--text-secondary);">${data.input_length} characters</span>
                        </div>` : ''}
                        <div>
                            <strong>Timestamp:</strong> 
                            <span style="color: var(--text-secondary);">${new Date(data.timestamp).toLocaleString()}</span>
                        </div>
                        ${data.note ? `<div style="color: var(--warning); font-size: 13px;">
                            <strong>Note:</strong> ${data.note}
                        </div>` : ''}
                    </div>
                </div>
                
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border);">
                    <button class="btn-primary" onclick="copySummaryToClipboard()" style="margin-right: 10px;">
                        📋 Copy Summary
                    </button>
                    <button class="btn-secondary" onclick="clearSummaryForm()">
                        🔄 Clear
                    </button>
                </div>
            </div>
        `;
        
        // Store summary for clipboard
        window.lastSummary = summary;
        
    } catch (error) {
        console.error('News summarization error:', error);
        resultDiv.innerHTML = `<div class="alert alert-error">Summarization Error: ${error.message}</div>`;
        showError('Error summarizing news');
    }
}

// Toggle summary details
function toggleSummaryDetails() {
    const details = document.getElementById('summary-details');
    const icon = document.getElementById('toggle-summary-icon');
    if (details.style.display === 'none') {
        details.style.display = 'block';
        icon.textContent = '▲';
    } else {
        details.style.display = 'none';
        icon.textContent = '▼';
    }
}

// Copy summary to clipboard
async function copySummaryToClipboard() {
    if (!window.lastSummary) {
        showError('No summary to copy');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(window.lastSummary);
        showSuccess('Summary copied to clipboard!');
    } catch (error) {
        console.error('Failed to copy:', error);
        showError('Failed to copy summary');
    }
}

// Clear summary form
function clearSummaryForm() {
    document.getElementById('summary-news-title').value = '';
    document.getElementById('summary-news-content').value = '';
    document.getElementById('news-summary-result').innerHTML = '';
    window.lastSummary = null;
}

// Analyze Sentiment (updated with model_key support)
async function analyzeSentiment() {
    const text = document.getElementById('sentiment-text').value;
    const mode = document.getElementById('sentiment-mode').value;
    const modelKey = document.getElementById('sentiment-model').value;
    
    if (!text.trim()) {
        showError('Please enter text to analyze');
        return;
    }
    
    const resultDiv = document.getElementById('sentiment-result');
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Analyzing...</div>';
    
    try {
        let response;
        
        // Build request body
        const requestBody = { 
            text: text, 
            mode: mode 
        };
        
        // Add model_key if specific model selected
        if (modelKey && modelKey !== '') {
            requestBody.model_key = modelKey;
        }
        
        // Use the sentiment endpoint with mode and optional model_key
        response = await fetch('/api/sentiment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (!data.available) {
            resultDiv.innerHTML = `
                <div class="alert alert-warning">
                    <strong>⚠️ Models Not Available:</strong> ${data.error || 'AI models are currently unavailable'}
                </div>
            `;
            return;
        }
        
        const label = data.sentiment || 'neutral';
        const confidence = data.confidence || 0;
        const result = data.result || {};
        
        // Determine sentiment emoji and color
        const sentimentEmoji = label === 'bullish' || label === 'positive' ? '📈' :
                              label === 'bearish' || label === 'negative' ? '📉' : '➡️';
        const sentimentColor = label === 'bullish' || label === 'positive' ? 'var(--success)' :
                              label === 'bearish' || label === 'negative' ? 'var(--danger)' : 'var(--text-secondary)';
        
        resultDiv.innerHTML = `
            <div class="alert alert-success" style="margin-top: 20px; border-left: 4px solid ${sentimentColor};">
                <h4 style="margin-bottom: 15px;">Sentiment Analysis Result</h4>
                <div style="display: grid; gap: 10px;">
                    <div>
                        <strong>Sentiment:</strong> 
                        <span style="color: ${sentimentColor}; font-weight: 700; font-size: 18px;">
                            ${sentimentEmoji} ${label === 'bullish' || label === 'positive' ? 'Bullish/Positive' : 
                              label === 'bearish' || label === 'negative' ? 'Bearish/Negative' : 'Neutral'}
                        </span>
                    </div>
                    <div>
                        <strong>Confidence:</strong> 
                        <span style="color: var(--primary); font-weight: 600;">
                            ${(confidence * 100).toFixed(2)}%
                        </span>
                    </div>
                    <div>
                        <strong>Analysis Type:</strong> 
                        <span style="color: var(--text-secondary);">${mode}</span>
                    </div>
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border);">
                        <strong>Analyzed Text:</strong>
                        <div style="margin-top: 5px; padding: 10px; background: rgba(31, 41, 55, 0.6); border-radius: 5px; font-size: 13px; color: var(--text-secondary);">
                            "${text.substring(0, 200)}${text.length > 200 ? '...' : ''}"
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Save to history (localStorage)
        saveSentimentToHistory({
            text: text.substring(0, 100),
            label: label,
            confidence: confidence,
            model: mode,
            timestamp: new Date().toISOString()
        });
        
        // Reload history
        loadSentimentHistory();
        
    } catch (error) {
        console.error('Sentiment analysis error:', error);
        resultDiv.innerHTML = `<div class="alert alert-error">Analysis Error: ${error.message}</div>`;
        showError('Error analyzing sentiment');
    }
}

// Save sentiment to history
function saveSentimentToHistory(analysis) {
    try {
        const history = JSON.parse(localStorage.getItem('sentiment_history') || '[]');
        history.unshift(analysis);
        // Keep only last 50
        if (history.length > 50) history = history.slice(0, 50);
        localStorage.setItem('sentiment_history', JSON.stringify(history));
    } catch (e) {
        console.warn('Could not save to history:', e);
    }
}

// Load sentiment history
function loadSentimentHistory() {
    try {
        const history = JSON.parse(localStorage.getItem('sentiment_history') || '[]');
        const historyDiv = document.getElementById('sentiment-history');
        
        if (history.length === 0) {
            historyDiv.innerHTML = '<div class="alert alert-warning">No history available</div>';
            return;
        }
        
        historyDiv.innerHTML = `
            <div style="display: grid; gap: 10px; max-height: 400px; overflow-y: auto;">
                ${history.slice(0, 20).map(item => {
                    const sentimentEmoji = item.label.toUpperCase().includes('POSITIVE') || item.label.toUpperCase().includes('BULLISH') ? '📈' :
                                         item.label.toUpperCase().includes('NEGATIVE') || item.label.toUpperCase().includes('BEARISH') ? '📉' : '➡️';
                    return `
                        <div style="padding: 12px; background: rgba(31, 41, 55, 0.6); border-radius: 8px; border-left: 3px solid var(--primary);">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 5px;">
                                <span style="font-weight: 600;">${sentimentEmoji} ${item.label}</span>
                                <span style="font-size: 11px; color: var(--text-secondary);">${new Date(item.timestamp).toLocaleString('en-US')}</span>
                            </div>
                            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 5px;">${item.text}</div>
                            <div style="font-size: 11px; color: var(--text-secondary);">
                                Confidence: ${(item.confidence * 100).toFixed(0)}% | Model: ${item.model}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    } catch (e) {
        console.warn('Could not load history:', e);
    }
}

// Load News
async function loadNews() {
    // Show loading state
    const newsDiv = document.getElementById('news-list');
    if (newsDiv) {
        newsDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Loading news...</div>';
    }
    
    try {
        // Try /api/news/latest first, fallback to /api/news
        let response;
        try {
            response = await fetch('/api/news/latest?limit=20');
        } catch {
            response = await fetch('/api/news?limit=20');
        }
        
        const data = await response.json();
        
        const newsItems = data.news || data.data || [];
        
        if (newsItems.length > 0) {
            const newsDiv = document.getElementById('news-list');
            newsDiv.innerHTML = `
                <div style="display: grid; gap: 20px;">
                    ${newsItems.map((item, index) => {
                        const sentiment = item.sentiment_label || item.sentiment || 'neutral';
                        const sentimentLower = sentiment.toLowerCase();
                        const sentimentConfidence = item.sentiment_confidence || 0;
                        
                        // Determine sentiment styling
                        let sentimentColor, sentimentBg, sentimentEmoji, sentimentLabel;
                        if (sentimentLower.includes('positive') || sentimentLower.includes('bullish')) {
                            sentimentColor = '#10b981';
                            sentimentBg = 'rgba(16, 185, 129, 0.15)';
                            sentimentEmoji = '📈';
                            sentimentLabel = 'Bullish';
                        } else if (sentimentLower.includes('negative') || sentimentLower.includes('bearish')) {
                            sentimentColor = '#ef4444';
                            sentimentBg = 'rgba(239, 68, 68, 0.15)';
                            sentimentEmoji = '📉';
                            sentimentLabel = 'Bearish';
                        } else {
                            sentimentColor = '#6b7280';
                            sentimentBg = 'rgba(107, 114, 128, 0.15)';
                            sentimentEmoji = '➡️';
                            sentimentLabel = 'Neutral';
                        }
                        
                        const publishedDate = item.published_date || item.published_at || item.analyzed_at;
                        const publishedTime = publishedDate ? new Date(publishedDate).toLocaleString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        }) : 'Unknown date';
                        
                        const content = item.content || item.description || '';
                        const contentPreview = content.length > 250 ? content.substring(0, 250) + '...' : content;
                        
                        return `
                            <div style="padding: 24px; background: rgba(31, 41, 55, 0.6); border-radius: 16px; border-left: 5px solid ${sentimentColor}; transition: transform 0.2s, box-shadow 0.2s; cursor: pointer;" 
                                 onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 10px 25px rgba(0,0,0,0.3)'"
                                 onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'"
                                 onclick="${item.url ? `window.open('${item.url}', '_blank')` : ''}">
                                <div style="display: flex; justify-content: space-between; align-items: start; gap: 15px; margin-bottom: 12px;">
                                    <h4 style="margin: 0; color: var(--text-primary); font-size: 18px; font-weight: 700; line-height: 1.4; flex: 1;">
                                        ${item.title || 'No title'}
                                    </h4>
                                    <div style="padding: 6px 12px; background: ${sentimentBg}; border-radius: 8px; white-space: nowrap;">
                                        <span style="font-size: 16px; margin-right: 4px;">${sentimentEmoji}</span>
                                        <span style="font-size: 12px; font-weight: 600; color: ${sentimentColor};">
                                            ${sentimentLabel}
                                        </span>
                                    </div>
                                </div>
                                
                                ${contentPreview ? `
                                    <p style="color: var(--text-secondary); margin-bottom: 15px; line-height: 1.7; font-size: 14px;">
                                        ${contentPreview}
                                    </p>
                                ` : ''}
                                
                                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                                    <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
                                        <div style="display: flex; align-items: center; gap: 6px;">
                                            <span style="font-size: 12px; color: var(--text-secondary);">📰</span>
                                            <span style="font-size: 12px; color: var(--text-secondary); font-weight: 500;">
                                                ${item.source || 'Unknown Source'}
                                            </span>
                                        </div>
                                        
                                        ${sentimentConfidence > 0 ? `
                                            <div style="display: flex; align-items: center; gap: 6px;">
                                                <span style="font-size: 12px; color: var(--text-secondary);">🎯</span>
                                                <span style="font-size: 12px; color: ${sentimentColor}; font-weight: 600;">
                                                    ${(sentimentConfidence * 100).toFixed(0)}% confidence
                                                </span>
                                            </div>
                                        ` : ''}
                                        
                                        <div style="display: flex; align-items: center; gap: 6px;">
                                            <span style="font-size: 12px; color: var(--text-secondary);">🕒</span>
                                            <span style="font-size: 12px; color: var(--text-secondary);">
                                                ${publishedTime}
                                            </span>
                                        </div>
                                        
                                        ${item.related_symbols && Array.isArray(item.related_symbols) && item.related_symbols.length > 0 ? `
                                            <div style="display: flex; align-items: center; gap: 6px;">
                                                <span style="font-size: 12px; color: var(--text-secondary);">💰</span>
                                                <div style="display: flex; gap: 4px; flex-wrap: wrap;">
                                                    ${item.related_symbols.slice(0, 3).map(symbol => `
                                                        <span style="padding: 2px 8px; background: rgba(59, 130, 246, 0.2); border-radius: 4px; font-size: 11px; color: var(--accent-blue); font-weight: 600;">
                                                            ${symbol}
                                                        </span>
                                                    `).join('')}
                                                    ${item.related_symbols.length > 3 ? `<span style="font-size: 11px; color: var(--text-secondary);">+${item.related_symbols.length - 3}</span>` : ''}
                                                </div>
                                            </div>
                                        ` : ''}
                                    </div>
                                    
                                    ${item.url ? `
                                        <a href="${item.url}" target="_blank" rel="noopener noreferrer" 
                                           style="padding: 8px 16px; background: var(--accent-blue); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 13px; transition: background 0.2s;"
                                           onmouseover="this.style.background='#2563eb'"
                                           onmouseout="this.style.background='var(--accent-blue)'">
                                            Read More →
                                        </a>
                                    ` : ''}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
                <div style="margin-top: 20px; padding: 15px; background: rgba(59, 130, 246, 0.1); border-radius: 10px; text-align: center;">
                    <span style="font-size: 14px; color: var(--text-secondary);">
                        Showing ${newsItems.length} article${newsItems.length !== 1 ? 's' : ''} • 
                        <span style="color: var(--accent-blue); font-weight: 600;">Last updated: ${new Date().toLocaleTimeString('en-US')}</span>
                    </span>
                </div>
            `;
        } else {
            document.getElementById('news-list').innerHTML = `
                <div class="alert alert-warning" style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 15px;">📰</div>
                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 8px;">No news articles found</div>
                    <div style="font-size: 14px; color: var(--text-secondary);">
                        News articles will appear here once they are analyzed and stored in the database.
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading news:', error);
        showError('Error loading news');
        document.getElementById('news-list').innerHTML = `
            <div class="alert alert-error" style="text-align: center; padding: 40px;">
                <div style="font-size: 48px; margin-bottom: 15px;">❌</div>
                <div style="font-size: 18px; font-weight: 600; margin-bottom: 8px;">Error loading news</div>
                <div style="font-size: 14px; color: var(--text-secondary);">
                    ${error.message || 'Failed to fetch news articles. Please try again later.'}
                </div>
            </div>
        `;
    }
}

// Load Providers
async function loadProviders() {
    // Show loading state
    const providersDiv = document.getElementById('providers-list');
    if (providersDiv) {
        providersDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Loading providers...</div>';
    }
    
    try {
        // Load providers and auto-discovery health summary in parallel
        const [providersRes, healthRes] = await Promise.all([
            fetch('/api/providers'),
            fetch('/api/providers/health-summary').catch(() => null) // Optional
        ]);
        
        const providersData = await providersRes.json();
        const providers = providersData.providers || providersData || [];
        
        // Update providers list
        const providersDiv = document.getElementById('providers-list');
        if (providersDiv) {
            if (providers.length > 0) {
                providersDiv.innerHTML = `
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Category</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${providers.map(provider => {
                                    const status = provider.status || 'unknown';
                                    const statusConfig = {
                                        'VALID': { color: 'var(--success)', bg: 'rgba(16, 185, 129, 0.2)', text: '✅ Valid' },
                                        'validated': { color: 'var(--success)', bg: 'rgba(16, 185, 129, 0.2)', text: '✅ Valid' },
                                        'available': { color: 'var(--success)', bg: 'rgba(16, 185, 129, 0.2)', text: '✅ Available' },
                                        'online': { color: 'var(--success)', bg: 'rgba(16, 185, 129, 0.2)', text: '✅ Online' },
                                        'CONDITIONALLY_AVAILABLE': { color: 'var(--warning)', bg: 'rgba(245, 158, 11, 0.2)', text: '⚠️ Conditional' },
                                        'INVALID': { color: 'var(--danger)', bg: 'rgba(239, 68, 68, 0.2)', text: '❌ Invalid' },
                                        'unvalidated': { color: 'var(--warning)', bg: 'rgba(245, 158, 11, 0.2)', text: '⚠️ Unvalidated' },
                                        'not_loaded': { color: 'var(--warning)', bg: 'rgba(245, 158, 11, 0.2)', text: '⚠️ Not Loaded' },
                                        'offline': { color: 'var(--danger)', bg: 'rgba(239, 68, 68, 0.2)', text: '❌ Offline' },
                                        'degraded': { color: 'var(--warning)', bg: 'rgba(245, 158, 11, 0.2)', text: '⚠️ Degraded' }
                                    };
                                    const statusInfo = statusConfig[status] || { color: 'var(--text-secondary)', bg: 'rgba(156, 163, 175, 0.2)', text: '❓ Unknown' };
                                    
                                    return `
                                        <tr>
                                            <td>${provider.provider_id || provider.id || '-'}</td>
                                            <td><strong>${provider.name || 'Unknown'}</strong></td>
                                            <td>${provider.category || '-'}</td>
                                            <td>${provider.type || '-'}</td>
                                            <td>
                                                <span style="padding: 5px 10px; border-radius: 5px; background: ${statusInfo.bg}; color: ${statusInfo.color}; font-size: 12px;">
                                                    ${statusInfo.text}
                                                </span>
                                            </td>
                                            <td>
                                                ${provider.response_time_ms ? `<span style="font-size: 12px; color: var(--text-secondary);">${provider.response_time_ms}ms</span>` : ''}
                                                ${provider.endpoint ? `<a href="${provider.endpoint}" target="_blank" style="color: var(--primary); font-size: 12px;">🔗</a>` : ''}
                                                ${provider.error_reason ? `<span style="font-size: 11px; color: var(--danger);" title="${provider.error_reason}">⚠️</span>` : ''}
                                            </td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                    <div style="margin-top: 15px; padding: 15px; background: rgba(102, 126, 234, 0.1); border-radius: 10px;">
                        <strong>Total Providers:</strong> ${providersData.total || providers.length}
                    </div>
                `;
            } else {
                providersDiv.innerHTML = '<div class="alert alert-warning">No providers found</div>';
            }
        }
        
        // Update health summary if available
        if (healthRes) {
            try {
                const healthData = await healthRes.json();
                const healthSummaryDiv = document.getElementById('providers-health-summary');
                if (healthSummaryDiv && healthData.ok && healthData.summary) {
                    const summary = healthData.summary;
                    healthSummaryDiv.innerHTML = `
                        <div class="card">
                            <h3>Provider Health Summary</h3>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                                <div style="padding: 15px; background: rgba(16, 185, 129, 0.1); border-radius: 10px; border-left: 4px solid var(--success);">
                                    <div style="font-size: 24px; font-weight: bold; color: var(--success);">${summary.total_active_providers || 0}</div>
                                    <div style="font-size: 12px; color: var(--text-secondary);">Total Active</div>
                                </div>
                                <div style="padding: 15px; background: rgba(16, 185, 129, 0.1); border-radius: 10px; border-left: 4px solid var(--success);">
                                    <div style="font-size: 24px; font-weight: bold; color: var(--success);">${summary.http_valid || 0}</div>
                                    <div style="font-size: 12px; color: var(--text-secondary);">HTTP Valid</div>
                                </div>
                                <div style="padding: 15px; background: rgba(239, 68, 68, 0.1); border-radius: 10px; border-left: 4px solid var(--danger);">
                                    <div style="font-size: 24px; font-weight: bold; color: var(--danger);">${summary.http_invalid || 0}</div>
                                    <div style="font-size: 12px; color: var(--text-secondary);">HTTP Invalid</div>
                                </div>
                                <div style="padding: 15px; background: rgba(245, 158, 11, 0.1); border-radius: 10px; border-left: 4px solid var(--warning);">
                                    <div style="font-size: 24px; font-weight: bold; color: var(--warning);">${summary.http_conditional || 0}</div>
                                    <div style="font-size: 12px; color: var(--text-secondary);">Conditional</div>
                                </div>
                            </div>
                        </div>
                    `;
                }
            } catch (e) {
                console.warn('Could not load health summary:', e);
            }
        }
        
    } catch (error) {
        console.error('Error loading providers:', error);
        showError('Error loading providers');
        const providersDiv = document.getElementById('providers-list');
        if (providersDiv) {
            providersDiv.innerHTML = '<div class="alert alert-error">Error loading providers</div>';
        }
    }
}

// Search Resources
async function searchResources() {
    const query = document.getElementById('search-resources').value;
    if (!query.trim()) {
        showError('Please enter a search query');
        return;
    }
    
    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Searching...</div>';
    
    try {
        const response = await fetch(`/api/resources/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success && data.resources && data.resources.length > 0) {
            resultsDiv.innerHTML = `
                <div style="margin-top: 15px;">
                    <div style="margin-bottom: 10px; color: var(--text-secondary);">
                        ${data.count || data.resources.length} result(s) found
                    </div>
                    <div style="display: grid; gap: 10px;">
                        ${data.resources.map(resource => `
                            <div style="padding: 15px; background: rgba(31, 41, 55, 0.6); border-radius: 10px; border-left: 4px solid var(--primary);">
                                <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 10px;">
                                    <div>
                                        <strong style="font-size: 16px;">${resource.name || 'Unknown'}</strong>
                                        <div style="font-size: 12px; color: var(--text-secondary); margin-top: 5px;">
                                            Category: ${resource.category || 'N/A'}
                                        </div>
                                        ${resource.base_url ? `<div style="font-size: 11px; color: var(--text-secondary); margin-top: 3px; font-family: monospace;">
                                            ${resource.base_url}
                                        </div>` : ''}
                                    </div>
                                    ${resource.free !== undefined ? `
                                        <span style="padding: 5px 10px; border-radius: 5px; background: ${resource.free ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)'}; color: ${resource.free ? 'var(--success)' : 'var(--warning)'}; font-size: 12px;">
                                            ${resource.free ? '🆓 Free' : '💰 Paid'}
                                        </span>
                                    ` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } else {
            resultsDiv.innerHTML = '<div class="alert alert-warning" style="margin-top: 15px;">No results found</div>';
        }
    } catch (error) {
        console.error('Search error:', error);
        resultsDiv.innerHTML = '<div class="alert alert-error" style="margin-top: 15px;">Search error</div>';
        showError('Search error');
    }
}

// Load Diagnostics
async function loadDiagnostics() {
    try {
        // Load system status
        try {
            const statusRes = await fetch('/api/status');
            const statusData = await statusRes.json();
            
            const statusDiv = document.getElementById('diagnostics-status');
            const health = statusData.system_health || 'unknown';
            const healthClass = health === 'healthy' ? 'alert-success' : 
                              health === 'degraded' ? 'alert-warning' : 'alert-error';
            
            statusDiv.innerHTML = `
                <div class="alert ${healthClass}">
                    <h4 style="margin-bottom: 10px;">System Status</h4>
                    <div style="display: grid; gap: 5px;">
                        <div><strong>Overall Status:</strong> ${health}</div>
                        <div><strong>Total APIs:</strong> ${statusData.total_apis || 0}</div>
                        <div><strong>Online:</strong> ${statusData.online || 0}</div>
                        <div><strong>Degraded:</strong> ${statusData.degraded || 0}</div>
                        <div><strong>Offline:</strong> ${statusData.offline || 0}</div>
                        <div><strong>Avg Response Time:</strong> ${statusData.avg_response_time_ms || 0}ms</div>
                        ${statusData.last_update ? `<div><strong>Last Update:</strong> ${new Date(statusData.last_update).toLocaleString('en-US')}</div>` : ''}
                    </div>
                </div>
            `;
        } catch (statusError) {
            document.getElementById('diagnostics-status').innerHTML = '<div class="alert alert-error">Error loading system status</div>';
        }
        
        // Load error logs
        try {
            const errorsRes = await fetch('/api/logs/errors');
            const errorsData = await errorsRes.json();
            
            const errors = errorsData.errors || errorsData.error_logs || [];
            const errorsDiv = document.getElementById('error-logs');
            
            if (errors.length > 0) {
                errorsDiv.innerHTML = `
                    <div style="display: grid; gap: 10px;">
                        ${errors.slice(0, 10).map(error => `
                            <div style="padding: 15px; background: rgba(239, 68, 68, 0.1); border-left: 4px solid var(--danger); border-radius: 5px;">
                                <div style="font-weight: 600; color: var(--danger); margin-bottom: 5px;">
                                    ${error.message || error.error_message || error.type || 'Error'}
                                </div>
                                ${error.error_type ? `<div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 3px;">Type: ${error.error_type}</div>` : ''}
                                ${error.provider ? `<div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 3px;">Provider: ${error.provider}</div>` : ''}
                                <div style="font-size: 11px; color: var(--text-secondary); margin-top: 5px;">
                                    ${error.timestamp ? new Date(error.timestamp).toLocaleString('en-US') : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    ${errors.length > 10 ? `<div style="margin-top: 10px; text-align: center; color: var(--text-secondary); font-size: 12px;">
                        Showing ${Math.min(10, errors.length)} of ${errors.length} errors
                    </div>` : ''}
                `;
            } else {
                errorsDiv.innerHTML = '<div class="alert alert-success">No errors found ✅</div>';
            }
        } catch (errorsError) {
            document.getElementById('error-logs').innerHTML = '<div class="alert alert-warning">Error loading error logs</div>';
        }
        
        // Load recent logs
        try {
            const logsRes = await fetch('/api/logs/recent');
            const logsData = await logsRes.json();
            
            const logs = logsData.logs || logsData.recent || [];
            const logsDiv = document.getElementById('recent-logs');
            
            if (logs.length > 0) {
                logsDiv.innerHTML = `
                    <div style="display: grid; gap: 10px; max-height: 400px; overflow-y: auto;">
                        ${logs.slice(0, 20).map(log => {
                            const level = log.level || log.status || 'info';
                            const levelColor = level === 'ERROR' ? 'var(--danger)' : 
                                             level === 'WARNING' ? 'var(--warning)' : 
                                             'var(--text-secondary)';
                            
                            return `
                                <div style="padding: 12px; background: rgba(31, 41, 55, 0.6); border-left: 3px solid ${levelColor}; border-radius: 5px;">
                                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 5px;">
                                        <div style="font-size: 12px; font-weight: 600; color: ${levelColor};">
                                            ${level}
                                        </div>
                                        <div style="font-size: 11px; color: var(--text-secondary);">
                                            ${log.timestamp ? new Date(log.timestamp).toLocaleString('en-US') : ''}
                                        </div>
                                    </div>
                                    <div style="font-size: 13px; color: var(--text-primary);">
                                        ${log.message || log.content || JSON.stringify(log)}
                                    </div>
                                    ${log.provider ? `<div style="font-size: 11px; color: var(--text-secondary); margin-top: 3px;">Provider: ${log.provider}</div>` : ''}
                                </div>
                            `;
                        }).join('')}
                    </div>
                `;
            } else {
                logsDiv.innerHTML = '<div class="alert alert-warning">No logs found</div>';
            }
        } catch (logsError) {
            document.getElementById('recent-logs').innerHTML = '<div class="alert alert-warning">Error loading logs</div>';
        }
    } catch (error) {
        console.error('Error loading diagnostics:', error);
        showError('Error loading diagnostics');
    }
}

// Run Diagnostics
async function runDiagnostics() {
    try {
        const response = await fetch('/api/diagnostics/run', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Diagnostics completed successfully');
            setTimeout(loadDiagnostics, 1000);
        } else {
            showError(data.error || 'Error running diagnostics');
        }
    } catch (error) {
        showError('Error running diagnostics: ' + error.message);
    }
}

// Load Health Diagnostics
async function loadHealthDiagnostics() {
    const resultDiv = document.getElementById('health-diagnostics-result');
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Loading health data...</div>';
    
    try {
        const response = await fetch('/api/diagnostics/health');
        const data = await response.json();
        
        if (data.status !== 'success') {
            resultDiv.innerHTML = `
                <div class="alert alert-error">
                    <strong>Error:</strong> ${data.error || 'Failed to load health diagnostics'}
                </div>
            `;
            return;
        }
        
        const providerSummary = data.providers.summary;
        const modelSummary = data.models.summary;
        const providerEntries = data.providers.entries || [];
        const modelEntries = data.models.entries || [];
        
        // Helper function to get status color
        const getStatusColor = (status) => {
            switch (status) {
                case 'healthy': return 'var(--success)';
                case 'degraded': return 'var(--warning)';
                case 'unavailable': return 'var(--danger)';
                default: return 'var(--text-secondary)';
            }
        };
        
        // Helper function to get status badge
        const getStatusBadge = (status, inCooldown) => {
            const color = getStatusColor(status);
            const icon = status === 'healthy' ? '✅' : 
                        status === 'degraded' ? '⚠️' : 
                        status === 'unavailable' ? '❌' : '❓';
            const cooldownText = inCooldown ? ' (cooldown)' : '';
            return `<span style="padding: 4px 10px; background: ${color}20; color: ${color}; border-radius: 5px; font-size: 12px; font-weight: 600;">${icon} ${status}${cooldownText}</span>`;
        };
        
        resultDiv.innerHTML = `
            <div style="display: grid; gap: 20px;">
                <!-- Summary Cards -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div style="padding: 15px; background: rgba(59, 130, 246, 0.1); border-radius: 10px; border-left: 4px solid var(--accent-blue);">
                        <div style="font-size: 24px; font-weight: 800; color: var(--accent-blue); margin-bottom: 5px;">
                            ${providerSummary.total}
                        </div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Total Providers</div>
                        <div style="margin-top: 8px; display: flex; gap: 8px; font-size: 11px;">
                            <span style="color: var(--success);">✅ ${providerSummary.healthy}</span>
                            <span style="color: var(--warning);">⚠️ ${providerSummary.degraded}</span>
                            <span style="color: var(--danger);">❌ ${providerSummary.unavailable}</span>
                        </div>
                    </div>
                    
                    <div style="padding: 15px; background: rgba(139, 92, 246, 0.1); border-radius: 10px; border-left: 4px solid var(--accent-purple);">
                        <div style="font-size: 24px; font-weight: 800; color: var(--accent-purple); margin-bottom: 5px;">
                            ${modelSummary.total}
                        </div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Total Models</div>
                        <div style="margin-top: 8px; display: flex; gap: 8px; font-size: 11px;">
                            <span style="color: var(--success);">✅ ${modelSummary.healthy}</span>
                            <span style="color: var(--warning);">⚠️ ${modelSummary.degraded}</span>
                            <span style="color: var(--danger);">❌ ${modelSummary.unavailable}</span>
                        </div>
                    </div>
                    
                    <div style="padding: 15px; background: ${data.overall_health.providers_ok && data.overall_health.models_ok ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)'}; border-radius: 10px; border-left: 4px solid ${data.overall_health.providers_ok && data.overall_health.models_ok ? 'var(--success)' : 'var(--warning)'};">
                        <div style="font-size: 32px; margin-bottom: 5px;">
                            ${data.overall_health.providers_ok && data.overall_health.models_ok ? '💚' : '⚠️'}
                        </div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Overall Health</div>
                        <div style="margin-top: 8px; font-size: 14px; font-weight: 600; color: ${data.overall_health.providers_ok && data.overall_health.models_ok ? 'var(--success)' : 'var(--warning)'};">
                            ${data.overall_health.providers_ok && data.overall_health.models_ok ? 'HEALTHY' : 'DEGRADED'}
                        </div>
                    </div>
                </div>
                
                <!-- Providers Health -->
                ${providerEntries.length > 0 ? `
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <h4 style="margin: 0; color: var(--text-primary);">🔌 Provider Health (${providerEntries.length})</h4>
                        </div>
                        <div style="display: grid; gap: 10px; max-height: 300px; overflow-y: auto;">
                            ${providerEntries.map(provider => `
                                <div style="padding: 12px; background: rgba(31, 41, 55, 0.6); border-radius: 8px; border-left: 3px solid ${getStatusColor(provider.status)};">
                                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                        <div style="font-weight: 600; color: var(--text-primary);">${provider.name}</div>
                                        ${getStatusBadge(provider.status, provider.in_cooldown)}
                                    </div>
                                    <div style="font-size: 11px; color: var(--text-secondary); display: grid; gap: 3px;">
                                        <div>Errors: ${provider.error_count} | Successes: ${provider.success_count}</div>
                                        ${provider.last_success ? `<div>Last Success: ${new Date(provider.last_success * 1000).toLocaleString()}</div>` : ''}
                                        ${provider.last_error ? `<div>Last Error: ${new Date(provider.last_error * 1000).toLocaleString()}</div>` : ''}
                                        ${provider.last_error_message ? `<div style="color: var(--danger); margin-top: 5px;">Error: ${provider.last_error_message.substring(0, 100)}${provider.last_error_message.length > 100 ? '...' : ''}</div>` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : '<div class="alert alert-info">No provider health data available yet</div>'}
                
                <!-- Models Health -->
                ${modelEntries.length > 0 ? `
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <h4 style="margin: 0; color: var(--text-primary);">🤖 Model Health (${modelEntries.length})</h4>
                            <button class="btn-secondary" onclick="triggerSelfHeal()" style="padding: 6px 12px; font-size: 12px;">
                                🔧 Auto-Heal Failed Models
                            </button>
                        </div>
                        <div style="display: grid; gap: 10px; max-height: 400px; overflow-y: auto;">
                            ${modelEntries.filter(m => m.loaded || m.status !== 'unknown').slice(0, 20).map(model => `
                                <div style="padding: 12px; background: rgba(31, 41, 55, 0.6); border-radius: 8px; border-left: 3px solid ${getStatusColor(model.status)};">
                                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px; gap: 10px;">
                                        <div>
                                            <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 3px;">${model.model_id}</div>
                                            <div style="font-size: 10px; color: var(--text-secondary);">${model.key} • ${model.category}</div>
                                        </div>
                                        <div style="text-align: right; white-space: nowrap;">
                                            ${getStatusBadge(model.status, model.in_cooldown)}
                                            ${model.status === 'unavailable' && !model.in_cooldown ? `<button class="btn-secondary" onclick="reinitModel('${model.key}')" style="padding: 4px 8px; font-size: 10px; margin-top: 5px;">Reinit</button>` : ''}
                                        </div>
                                    </div>
                                    <div style="font-size: 11px; color: var(--text-secondary); display: grid; gap: 3px;">
                                        <div>Errors: ${model.error_count} | Successes: ${model.success_count} | Loaded: ${model.loaded ? 'Yes' : 'No'}</div>
                                        ${model.last_success ? `<div>Last Success: ${new Date(model.last_success * 1000).toLocaleString()}</div>` : ''}
                                        ${model.last_error ? `<div>Last Error: ${new Date(model.last_error * 1000).toLocaleString()}</div>` : ''}
                                        ${model.last_error_message ? `<div style="color: var(--danger); margin-top: 5px;">Error: ${model.last_error_message.substring(0, 150)}${model.last_error_message.length > 150 ? '...' : ''}</div>` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : '<div class="alert alert-info">No model health data available yet</div>'}
                
                <div style="text-align: center; padding: 15px; background: rgba(31, 41, 55, 0.3); border-radius: 8px; font-size: 11px; color: var(--text-secondary);">
                    Last updated: ${new Date(data.timestamp).toLocaleString()}
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading health diagnostics:', error);
        resultDiv.innerHTML = `
            <div class="alert alert-error">
                <strong>Error:</strong> ${error.message || 'Failed to load health diagnostics'}
            </div>
        `;
    }
}

// Trigger self-heal for all failed models
async function triggerSelfHeal() {
    try {
        const response = await fetch('/api/diagnostics/self-heal', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'completed') {
            const summary = data.summary;
            showSuccess(`Self-heal completed: ${summary.successful}/${summary.total_attempts} successful`);
            // Reload health after a short delay
            setTimeout(loadHealthDiagnostics, 2000);
        } else {
            showError(data.error || 'Self-heal failed');
        }
    } catch (error) {
        showError('Error triggering self-heal: ' + error.message);
    }
}

// Reinitialize specific model
async function reinitModel(modelKey) {
    try {
        const response = await fetch(`/api/diagnostics/self-heal?model_key=${encodeURIComponent(modelKey)}`, { 
            method: 'POST' 
        });
        const data = await response.json();
        
        if (data.status === 'completed' && data.results && data.results.length > 0) {
            const result = data.results[0];
            if (result.status === 'success') {
                showSuccess(`Model ${modelKey} reinitialized successfully`);
            } else {
                showError(`Failed to reinit ${modelKey}: ${result.message || result.error || 'Unknown error'}`);
            }
            // Reload health after a short delay
            setTimeout(loadHealthDiagnostics, 1500);
        } else {
            showError(data.error || 'Reinitialization failed');
        }
    } catch (error) {
        showError('Error reinitializing model: ' + error.message);
    }
}

// Test API
async function testAPI() {
    const endpoint = document.getElementById('api-endpoint').value;
    const method = document.getElementById('api-method').value;
    const bodyText = document.getElementById('api-body').value;
    
    if (!endpoint) {
        showError('Please select an endpoint');
        return;
    }
    
    const resultDiv = document.getElementById('api-result');
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Sending request...</div>';
    
    try {
        const options = { method };
        
        // Parse body if provided
        let body = null;
        if (method === 'POST' && bodyText) {
            try {
                body = JSON.parse(bodyText);
                options.headers = { 'Content-Type': 'application/json' };
            } catch (e) {
                showError('Invalid JSON in body');
                resultDiv.innerHTML = '<div class="alert alert-error">JSON parsing error</div>';
                return;
            }
        }
        
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        const startTime = Date.now();
        const response = await fetch(endpoint, options);
        const responseTime = Date.now() - startTime;
        
        let data;
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = { text: await response.text() };
        }
        
        const statusClass = response.ok ? 'alert-success' : 'alert-error';
        const statusEmoji = response.ok ? '✅' : '❌';
        
        resultDiv.innerHTML = `
            <div style="margin-top: 20px;">
                <div class="alert ${statusClass}" style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                        <div>
                            <strong>${statusEmoji} Status:</strong> ${response.status} ${response.statusText}
                        </div>
                        <div style="font-size: 12px; color: var(--text-secondary);">
                            Response Time: ${responseTime}ms
                        </div>
                    </div>
                </div>
                <div style="padding: 15px; background: rgba(31, 41, 55, 0.6); border-radius: 10px;">
                    <h4 style="margin-bottom: 10px;">Response:</h4>
                    <pre style="background: rgba(0, 0, 0, 0.3); padding: 15px; border-radius: 5px; overflow-x: auto; margin-top: 10px; font-size: 12px; max-height: 500px; overflow-y: auto;">${JSON.stringify(data, null, 2)}</pre>
                </div>
                <div style="margin-top: 10px; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 5px; font-size: 12px; color: var(--text-secondary);">
                    <strong>Endpoint:</strong> ${method} ${endpoint}
                </div>
            </div>
        `;
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="alert alert-error" style="margin-top: 20px;">
                <h4>Error:</h4>
                <p>${error.message}</p>
            </div>
        `;
        showError('API test error: ' + error.message);
    }
}

// Utility Functions
function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-error';
    alert.textContent = message;
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 5000);
}

function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success';
    alert.textContent = message;
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 5000);
}

// Additional tab loaders for HTML tabs
async function loadMonitorData() {
    // Load API monitor data
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        const monitorContainer = document.getElementById('monitor-content');
        if (monitorContainer) {
            monitorContainer.innerHTML = `
                <div class="card">
                    <h3>API Status</h3>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading monitor data:', error);
    }
}

async function loadAdvancedData() {
    // Load advanced/API explorer data
    loadAPIEndpoints();
    loadDiagnostics();
}

async function loadAdminData() {
    // Load admin panel data
    try {
        const [providersRes, modelsRes] = await Promise.all([
            fetch('/api/providers'),
            fetch('/api/models/status')
        ]);
        const providers = await providersRes.json();
        const models = await modelsRes.json();
        
        const adminContainer = document.getElementById('admin-content');
        if (adminContainer) {
            adminContainer.innerHTML = `
                <div class="card">
                    <h3>System Status</h3>
                    <p>Providers: ${providers.total || 0}</p>
                    <p>Models: ${models.models_loaded || 0} loaded</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading admin data:', error);
    }
}

async function loadHFHealth() {
    // Load HF models health status
    try {
        const response = await fetch('/api/models/status');
        const data = await response.json();
        const hfContainer = document.getElementById('hf-status');
        if (hfContainer) {
            hfContainer.innerHTML = `
                <div class="card">
                    <h3>HF Models Status</h3>
                    <p>Mode: ${data.hf_mode || 'unknown'}</p>
                    <p>Loaded: ${data.models_loaded || 0}</p>
                    <p>Failed: ${data.failed_count || 0}</p>
                    <p>Status: ${data.status || 'unknown'}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading HF health:', error);
    }
}

async function loadPools() {
    // Load provider pools
    try {
        const response = await fetch('/api/pools');
        const data = await response.json();
        const poolsContainer = document.getElementById('pools-content');
        if (poolsContainer) {
            poolsContainer.innerHTML = `
                <div class="card">
                    <h3>Provider Pools</h3>
                    <p>${data.message || 'No pools available'}</p>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading pools:', error);
    }
}

async function loadLogs() {
    // Load recent logs
    try {
        const response = await fetch('/api/logs/recent');
        const data = await response.json();
        const logsContainer = document.getElementById('logs-content');
        if (logsContainer) {
            const logsHtml = data.logs && data.logs.length > 0
                ? data.logs.map(log => `<div class="log-entry">${JSON.stringify(log)}</div>`).join('')
                : '<p>No logs available</p>';
            logsContainer.innerHTML = `<div class="card"><h3>Recent Logs</h3>${logsHtml}</div>`;
        }
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

async function loadReports() {
    // Load reports/analytics
    try {
        const response = await fetch('/api/providers/health-summary');
        const data = await response.json();
        const reportsContainer = document.getElementById('reports-content');
        if (reportsContainer) {
            reportsContainer.innerHTML = `
                <div class="card">
                    <h3>Provider Health Report</h3>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading reports:', error);
    }
}

async function loadResources() {
    // Load resources summary
    try {
        const response = await fetch('/api/resources');
        const data = await response.json();
        const resourcesContainer = document.getElementById('resources-summary');
        if (resourcesContainer) {
            const summary = data.summary || {};
            resourcesContainer.innerHTML = `
                <div class="card">
                    <h3>Resources Summary</h3>
                    <p>Total: ${summary.total_resources || 0}</p>
                    <p>Free: ${summary.free_resources || 0}</p>
                    <p>Models: ${summary.models_available || 0}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading resources:', error);
    }
}

async function loadAPIRegistry() {
    // Load API registry from all_apis_merged_2025.json
    try {
        const response = await fetch('/api/resources/apis');
        const data = await response.json();
        
        if (!data.ok) {
            console.warn('API registry not available:', data.error);
            const registryContainer = document.getElementById('api-registry-section');
            if (registryContainer) {
                registryContainer.innerHTML = `
                    <div class="alert alert-warning" style="padding: 30px; text-align: center;">
                        <div style="font-size: 48px; margin-bottom: 15px;">📚</div>
                        <div style="font-size: 18px; font-weight: 600; margin-bottom: 8px;">API Registry Not Available</div>
                        <div style="font-size: 14px; color: var(--text-secondary);">
                            ${data.error || 'API registry file not found'}
                        </div>
                    </div>
                `;
            }
            return;
        }
        
        const registryContainer = document.getElementById('api-registry-section');
        if (registryContainer) {
            const metadata = data.metadata || {};
            const categories = data.categories || [];
            const rawFiles = data.raw_files_preview || [];
            
            registryContainer.innerHTML = `
                <div style="background: rgba(31, 41, 55, 0.6); border-radius: 16px; padding: 24px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px; flex-wrap: wrap; gap: 15px;">
                        <div>
                            <h3 style="margin: 0 0 8px 0; color: var(--text-primary); font-size: 24px; font-weight: 700;">
                                📚 ${metadata.name || 'API Registry'}
                            </h3>
                            <p style="margin: 0; color: var(--text-secondary); font-size: 14px;">
                                ${metadata.description || 'Comprehensive API registry for cryptocurrency data sources'}
                            </p>
                        </div>
                        <div style="padding: 12px 20px; background: rgba(59, 130, 246, 0.15); border-radius: 10px;">
                            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">Version</div>
                            <div style="font-size: 18px; font-weight: 700; color: var(--accent-blue);">${metadata.version || 'N/A'}</div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px;">
                        <div style="padding: 15px; background: rgba(16, 185, 129, 0.1); border-radius: 10px; border-left: 4px solid var(--success);">
                            <div style="font-size: 28px; font-weight: 800; color: var(--success); margin-bottom: 5px;">
                                ${categories.length}
                            </div>
                            <div style="font-size: 12px; color: var(--text-secondary);">Categories</div>
                        </div>
                        <div style="padding: 15px; background: rgba(59, 130, 246, 0.1); border-radius: 10px; border-left: 4px solid var(--accent-blue);">
                            <div style="font-size: 28px; font-weight: 800; color: var(--accent-blue); margin-bottom: 5px;">
                                ${data.total_raw_files || 0}
                            </div>
                            <div style="font-size: 12px; color: var(--text-secondary);">Total Files</div>
                        </div>
                        ${metadata.created_at ? `
                            <div style="padding: 15px; background: rgba(139, 92, 246, 0.1); border-radius: 10px; border-left: 4px solid var(--accent-purple);">
                                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 5px;">Created</div>
                                <div style="font-size: 14px; font-weight: 600; color: var(--accent-purple);">
                                    ${new Date(metadata.created_at).toLocaleDateString('en-US')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                    
                    ${categories.length > 0 ? `
                        <div style="margin-bottom: 25px;">
                            <h4 style="margin: 0 0 15px 0; color: var(--text-primary); font-size: 18px; font-weight: 600;">
                                📂 Categories
                            </h4>
                            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                                ${categories.map(cat => `
                                    <span style="padding: 8px 16px; background: rgba(59, 130, 246, 0.15); border-radius: 8px; font-size: 13px; font-weight: 600; color: var(--accent-blue);">
                                        ${cat.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${rawFiles.length > 0 ? `
                        <div>
                            <h4 style="margin: 0 0 15px 0; color: var(--text-primary); font-size: 18px; font-weight: 600;">
                                📄 Sample Files (${rawFiles.length} of ${data.total_raw_files || 0})
                            </h4>
                            <div style="display: grid; gap: 10px; max-height: 400px; overflow-y: auto;">
                                ${rawFiles.map(file => `
                                    <div style="padding: 15px; background: rgba(17, 24, 39, 0.6); border-radius: 10px; border-left: 3px solid var(--accent-blue);">
                                        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 5px; font-size: 14px;">
                                            ${file.filename || 'Unknown file'}
                                        </div>
                                        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">
                                            Size: ${file.size ? (file.size / 1024).toFixed(1) + ' KB' : file.full_size ? (file.full_size / 1024).toFixed(1) + ' KB' : 'N/A'}
                                        </div>
                                        ${file.preview ? `
                                            <pre style="background: rgba(0, 0, 0, 0.3); padding: 10px; border-radius: 5px; font-size: 11px; color: var(--text-secondary); overflow-x: auto; margin: 0; max-height: 100px; overflow-y: auto;">${file.preview}</pre>
                                        ` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        // Also update metadata container if it exists
        const metadataContainer = document.getElementById('api-registry-metadata');
        if (metadataContainer) {
            metadataContainer.innerHTML = `
                <div style="background: rgba(31, 41, 55, 0.6); border-radius: 16px; padding: 24px;">
                    <h4 style="margin: 0 0 15px 0; color: var(--text-primary); font-size: 18px; font-weight: 600;">Metadata</h4>
                    <pre style="background: rgba(0, 0, 0, 0.3); padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 12px; color: var(--text-secondary);">${JSON.stringify(metadata, null, 2)}</pre>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading API registry:', error);
        const registryContainer = document.getElementById('api-registry-section');
        if (registryContainer) {
            registryContainer.innerHTML = `
                <div class="alert alert-error" style="padding: 30px; text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 15px;">❌</div>
                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 8px;">Error Loading API Registry</div>
                    <div style="font-size: 14px; color: var(--text-secondary);">
                        ${error.message || 'Failed to load API registry data'}
                    </div>
                </div>
            `;
        }
    }
}



// Theme Toggle
function toggleTheme() {
    const body = document.body;
    const themeToggle = document.querySelector('.theme-toggle');

    if (body.classList.contains('light-theme')) {
        body.classList.remove('light-theme');
        localStorage.setItem('theme', 'dark');
        // Update icon to moon (dark mode)
        if (themeToggle) {
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
    } else {
        body.classList.add('light-theme');
        localStorage.setItem('theme', 'light');
        // Update icon to sun (light mode)
        if (themeToggle) {
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }
}

// Load theme preference
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    const themeToggle = document.querySelector('.theme-toggle');

    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        if (themeToggle) {
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }
});

// Update header stats
function updateHeaderStats() {
    const totalResources = document.getElementById('stat-total-resources')?.textContent || '-';
    const totalModels = document.getElementById('stat-models')?.textContent || '-';
    
    const headerResources = document.getElementById('header-resources');
    const headerModels = document.getElementById('header-models');
    
    if (headerResources) headerResources.textContent = totalResources;
    if (headerModels) headerModels.textContent = totalModels;
}

// Call updateHeaderStats after loading dashboard
const originalLoadDashboard = loadDashboard;
loadDashboard = async function() {
    await originalLoadDashboard();
    updateHeaderStats();
};

// ===== AI Analyst Functions =====
async function runAIAnalyst() {
    const prompt = document.getElementById('ai-analyst-prompt').value.trim();
    const mode = document.getElementById('ai-analyst-mode').value;
    const maxLength = parseInt(document.getElementById('ai-analyst-max-length').value);
    
    if (!prompt) {
        showError('Please enter a prompt or question');
        return;
    }
    
    const resultDiv = document.getElementById('ai-analyst-result');
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Generating analysis...</div>';
    
    try {
        const response = await fetch('/api/analyze/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                prompt: prompt, 
                mode: mode,
                max_length: maxLength
            })
        });
        
        const data = await response.json();
        
        if (!data.available) {
            resultDiv.innerHTML = `
                <div class="alert alert-warning">
                    <strong>⚠️ Model Not Available:</strong> ${data.error || 'AI generation model is currently unavailable'}
                    ${data.note ? `<br><small>${data.note}</small>` : ''}
                </div>
            `;
            return;
        }
        
        if (!data.success) {
            resultDiv.innerHTML = `
                <div class="alert alert-error">
                    <strong>❌ Generation Failed:</strong> ${data.error || 'Failed to generate analysis'}
                </div>
            `;
            return;
        }
        
        const generatedText = data.text || '';
        const model = data.model || 'Unknown';
        
        resultDiv.innerHTML = `
            <div class="alert alert-success" style="border-left: 4px solid var(--primary);">
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 15px;">
                    <h4 style="margin: 0;">✨ AI Generated Analysis</h4>
                </div>
                
                <div style="background: var(--bg-card); padding: 20px; border-radius: 8px; margin: 15px 0;">
                    <div style="line-height: 1.8; color: var(--text-primary); white-space: pre-wrap;">
                        ${generatedText}
                    </div>
                </div>
                
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border);">
                    <div style="display: grid; gap: 10px; font-size: 13px;">
                        <div>
                            <strong>Model:</strong> 
                            <span style="color: var(--text-secondary);">${model}</span>
                        </div>
                        <div>
                            <strong>Mode:</strong> 
                            <span style="color: var(--text-secondary);">${mode}</span>
                        </div>
                        <div>
                            <strong>Prompt:</strong> 
                            <span style="color: var(--text-secondary);">"${prompt.substring(0, 100)}${prompt.length > 100 ? '...' : ''}"</span>
                        </div>
                        <div>
                            <strong>Timestamp:</strong> 
                            <span style="color: var(--text-secondary);">${new Date(data.timestamp).toLocaleString()}</span>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border);">
                    <button class="btn-primary" onclick="copyAIAnalystResult()" style="margin-right: 10px;">
                        📋 Copy Analysis
                    </button>
                    <button class="btn-secondary" onclick="clearAIAnalystForm()">
                        🔄 Clear
                    </button>
                </div>
            </div>
        `;
        
        // Store for clipboard
        window.lastAIAnalysis = generatedText;
        
    } catch (error) {
        console.error('AI analyst error:', error);
        resultDiv.innerHTML = `<div class="alert alert-error">Generation Error: ${error.message}</div>`;
        showError('Error generating analysis');
    }
}

function setAIAnalystPrompt(text) {
    document.getElementById('ai-analyst-prompt').value = text;
}

async function copyAIAnalystResult() {
    if (!window.lastAIAnalysis) {
        showError('No analysis to copy');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(window.lastAIAnalysis);
        showSuccess('Analysis copied to clipboard!');
    } catch (error) {
        console.error('Failed to copy:', error);
        showError('Failed to copy analysis');
    }
}

function clearAIAnalystForm() {
    document.getElementById('ai-analyst-prompt').value = '';
    document.getElementById('ai-analyst-result').innerHTML = '';
    window.lastAIAnalysis = null;
}

// ===== Trading Assistant Functions =====
async function runTradingAssistant() {
    const symbol = document.getElementById('trading-symbol').value.trim().toUpperCase();
    const context = document.getElementById('trading-context').value.trim();
    
    if (!symbol) {
        showError('Please enter a trading symbol');
        return;
    }
    
    const resultDiv = document.getElementById('trading-assistant-result');
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Analyzing and generating trading signal...</div>';
    
    try {
        const response = await fetch('/api/trading/decision', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                symbol: symbol,
                context: context
            })
        });
        
        const data = await response.json();
        
        if (!data.available) {
            resultDiv.innerHTML = `
                <div class="alert alert-warning">
                    <strong>⚠️ Model Not Available:</strong> ${data.error || 'Trading signal model is currently unavailable'}
                    ${data.note ? `<br><small>${data.note}</small>` : ''}
                </div>
            `;
            return;
        }
        
        if (!data.success) {
            resultDiv.innerHTML = `
                <div class="alert alert-error">
                    <strong>❌ Analysis Failed:</strong> ${data.error || 'Failed to generate trading signal'}
                </div>
            `;
            return;
        }
        
        const decision = data.decision || 'HOLD';
        const confidence = data.confidence || 0;
        const rationale = data.rationale || '';
        const model = data.model || 'Unknown';
        
        // Determine colors and icons based on decision
        let decisionColor, decisionBg, decisionIcon;
        if (decision === 'BUY') {
            decisionColor = 'var(--success)';
            decisionBg = 'rgba(16, 185, 129, 0.2)';
            decisionIcon = '📈';
        } else if (decision === 'SELL') {
            decisionColor = 'var(--danger)';
            decisionBg = 'rgba(239, 68, 68, 0.2)';
            decisionIcon = '📉';
        } else {
            decisionColor = 'var(--text-secondary)';
            decisionBg = 'rgba(156, 163, 175, 0.2)';
            decisionIcon = '➡️';
        }
        
        resultDiv.innerHTML = `
            <div class="alert alert-success" style="border-left: 4px solid ${decisionColor};">
                <h4 style="margin-bottom: 20px;">🎯 Trading Signal for ${symbol}</h4>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="text-align: center; padding: 30px; background: ${decisionBg}; border-radius: 10px;">
                        <div style="font-size: 48px; margin-bottom: 10px;">${decisionIcon}</div>
                        <div style="font-size: 32px; font-weight: 800; color: ${decisionColor}; margin-bottom: 5px;">
                            ${decision}
                        </div>
                        <div style="font-size: 14px; color: var(--text-secondary);">
                            Decision
                        </div>
                    </div>
                    
                    <div style="text-align: center; padding: 30px; background: rgba(102, 126, 234, 0.1); border-radius: 10px;">
                        <div style="font-size: 48px; font-weight: 800; color: var(--primary); margin-bottom: 10px;">
                            ${(confidence * 100).toFixed(0)}%
                        </div>
                        <div style="font-size: 14px; color: var(--text-secondary);">
                            Confidence
                        </div>
                    </div>
                </div>
                
                <div style="background: var(--bg-card); padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <strong style="color: var(--primary);">AI Rationale:</strong>
                    <p style="margin-top: 10px; line-height: 1.6; color: var(--text-primary); white-space: pre-wrap;">
                        ${rationale}
                    </p>
                </div>
                
                ${context ? `
                    <div style="margin-top: 15px; padding: 15px; background: rgba(31, 41, 55, 0.6); border-radius: 8px;">
                        <strong>Your Context:</strong>
                        <div style="margin-top: 5px; font-size: 13px; color: var(--text-secondary);">
                            "${context.substring(0, 200)}${context.length > 200 ? '...' : ''}"
                        </div>
                    </div>
                ` : ''}
                
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--border);">
                    <div style="display: grid; gap: 10px; font-size: 13px;">
                        <div>
                            <strong>Model:</strong> 
                            <span style="color: var(--text-secondary);">${model}</span>
                        </div>
                        <div>
                            <strong>Timestamp:</strong> 
                            <span style="color: var(--text-secondary);">${new Date(data.timestamp).toLocaleString()}</span>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: rgba(245, 158, 11, 0.1); border-radius: 8px; border-left: 3px solid var(--warning);">
                    <strong style="color: var(--warning);">⚠️ Reminder:</strong>
                    <p style="margin-top: 5px; font-size: 13px; color: var(--text-secondary);">
                        This is an AI-generated signal for informational purposes only. Always do your own research and consider multiple factors before trading.
                    </p>
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Trading assistant error:', error);
        resultDiv.innerHTML = `<div class="alert alert-error">Analysis Error: ${error.message}</div>`;
        showError('Error generating trading signal');
    }
}

// Initialize trading pair selector for trading assistant tab
function initTradingSymbolSelector() {
    const tradingSymbolContainer = document.getElementById('trading-symbol-container');
    if (tradingSymbolContainer && window.TradingPairsLoader) {
        const pairs = window.TradingPairsLoader.getTradingPairs();
        if (pairs && pairs.length > 0) {
            tradingSymbolContainer.innerHTML = window.TradingPairsLoader.createTradingPairCombobox(
                'trading-symbol',
                'Select or type trading pair',
                'BTCUSDT'
            );
        }
    }
}

// Update loadTabData to handle new tabs
const originalLoadTabData = loadTabData;
loadTabData = function(tabId) {
    originalLoadTabData(tabId);
    
    // Additional handlers for new tabs
    if (tabId === 'ai-analyst') {
        // No initialization needed for AI Analyst yet
    } else if (tabId === 'trading-assistant') {
        initTradingSymbolSelector();
    }
};

// Listen for trading pairs loaded event to initialize trading symbol selector
document.addEventListener('tradingPairsLoaded', function(e) {
    initTradingSymbolSelector();
});
