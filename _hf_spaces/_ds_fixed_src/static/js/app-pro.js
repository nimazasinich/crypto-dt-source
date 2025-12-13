/**
 * Professional Dashboard Application
 * Advanced cryptocurrency analytics with dynamic features
 */

// Global State
const AppState = {
    coins: [],
    selectedCoin: null,
    selectedTimeframe: 7,
    selectedColorScheme: 'blue',
    charts: {},
    lastUpdate: null
};

// Color Schemes
const ColorSchemes = {
    blue: {
        primary: '#3B82F6',
        secondary: '#06B6D4',
        gradient: ['#3B82F6', '#06B6D4']
    },
    purple: {
        primary: '#8B5CF6',
        secondary: '#EC4899',
        gradient: ['#8B5CF6', '#EC4899']
    },
    green: {
        primary: '#10B981',
        secondary: '#34D399',
        gradient: ['#10B981', '#34D399']
    },
    orange: {
        primary: '#F97316',
        secondary: '#FBBF24',
        gradient: ['#F97316', '#FBBF24']
    },
    rainbow: {
        primary: '#3B82F6',
        secondary: '#EC4899',
        gradient: ['#3B82F6', '#8B5CF6', '#EC4899', '#F97316']
    }
};

// Chart.js Global Configuration
Chart.defaults.color = '#E2E8F0';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
Chart.defaults.font.family = "'Manrope', 'Inter', sans-serif";
Chart.defaults.font.size = 13;
Chart.defaults.font.weight = 500;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initCombobox();
    initChartControls();
    initColorSchemeSelector();
    loadInitialData();
    startAutoRefresh();
});

// Navigation
function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-button');
    const pages = document.querySelectorAll('.page');
    
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetPage = button.dataset.nav;
            
            // Update active states
            navButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Show target page
            pages.forEach(page => {
                page.classList.toggle('active', page.id === targetPage);
            });
        });
    });
}

// Combobox for Coin Selection
function initCombobox() {
    const input = document.getElementById('coinSelector');
    const dropdown = document.getElementById('coinDropdown');
    
    if (!input || !dropdown) return;
    
    input.addEventListener('focus', () => {
        dropdown.classList.add('active');
        if (AppState.coins.length === 0) {
            loadCoinsForCombobox();
        }
    });
    
    input.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        filterComboboxOptions(searchTerm);
    });
    
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('active');
        }
    });
}

async function loadCoinsForCombobox() {
    try {
        const response = await fetch('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1');
        const coins = await response.json();
        AppState.coins = coins;
        renderComboboxOptions(coins);
    } catch (error) {
        console.error('Error loading coins:', error);
    }
}

function renderComboboxOptions(coins) {
    const dropdown = document.getElementById('coinDropdown');
    if (!dropdown) return;
    
    dropdown.innerHTML = coins.map(coin => `
        <div class="combobox-option" data-coin-id="${coin.id}">
            <img src="${coin.image}" alt="${coin.name}" class="combobox-option-icon">
            <div class="combobox-option-text">
                <div class="combobox-option-name">${coin.name}</div>
                <div class="combobox-option-symbol">${coin.symbol}</div>
            </div>
            <div class="combobox-option-price">$${formatNumber(coin.current_price)}</div>
        </div>
    `).join('');
    
    // Add click handlers
    dropdown.querySelectorAll('.combobox-option').forEach(option => {
        option.addEventListener('click', () => {
            const coinId = option.dataset.coinId;
            selectCoin(coinId);
            dropdown.classList.remove('active');
        });
    });
}

function filterComboboxOptions(searchTerm) {
    const options = document.querySelectorAll('.combobox-option');
    options.forEach(option => {
        const name = option.querySelector('.combobox-option-name').textContent.toLowerCase();
        const symbol = option.querySelector('.combobox-option-symbol').textContent.toLowerCase();
        const matches = name.includes(searchTerm) || symbol.includes(searchTerm);
        option.style.display = matches ? 'flex' : 'none';
    });
}

function selectCoin(coinId) {
    const coin = AppState.coins.find(c => c.id === coinId);
    if (!coin) return;
    
    AppState.selectedCoin = coin;
    document.getElementById('coinSelector').value = `${coin.name} (${coin.symbol.toUpperCase()})`;
    
    // Update chart
    loadCoinChart(coinId, AppState.selectedTimeframe);
}

// Chart Controls
function initChartControls() {
    // Timeframe buttons
    const timeframeButtons = document.querySelectorAll('[data-timeframe]');
    timeframeButtons.forEach(button => {
        button.addEventListener('click', () => {
            timeframeButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            AppState.selectedTimeframe = parseInt(button.dataset.timeframe);
            
            if (AppState.selectedCoin) {
                loadCoinChart(AppState.selectedCoin.id, AppState.selectedTimeframe);
            }
        });
    });
}

// Color Scheme Selector
function initColorSchemeSelector() {
    const schemeOptions = document.querySelectorAll('.color-scheme-option');
    schemeOptions.forEach(option => {
        option.addEventListener('click', () => {
            schemeOptions.forEach(opt => opt.classList.remove('active'));
            option.classList.add('active');
            
            AppState.selectedColorScheme = option.dataset.scheme;
            
            if (AppState.selectedCoin) {
                loadCoinChart(AppState.selectedCoin.id, AppState.selectedTimeframe);
            }
        });
    });
}

// Load Initial Data
async function loadInitialData() {
    try {
        await Promise.all([
            loadMarketStats(),
            loadTopCoins(),
            loadMainChart()
        ]);
        
        AppState.lastUpdate = new Date();
        updateLastUpdateTime();
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

// Load Market Stats
async function loadMarketStats() {
    try {
        const response = await fetch('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1');
        const coins = await response.json();
        
        // Calculate totals
        const totalMarketCap = coins.reduce((sum, coin) => sum + coin.market_cap, 0);
        const totalVolume = coins.reduce((sum, coin) => sum + coin.total_volume, 0);
        const btc = coins.find(c => c.id === 'bitcoin');
        const eth = coins.find(c => c.id === 'ethereum');
        
        // Update stats grid
        const statsGrid = document.getElementById('statsGrid');
        if (statsGrid) {
            statsGrid.innerHTML = `
                ${createStatCard('Total Market Cap', formatCurrency(totalMarketCap), '+2.5%', 'positive', '#3B82F6')}
                ${createStatCard('24h Volume', formatCurrency(totalVolume), '+5.2%', 'positive', '#06B6D4')}
                ${createStatCard('Bitcoin', formatCurrency(btc?.current_price || 0), `${btc?.price_change_percentage_24h?.toFixed(2) || 0}%`, btc?.price_change_percentage_24h >= 0 ? 'positive' : 'negative', '#F7931A')}
                ${createStatCard('Ethereum', formatCurrency(eth?.current_price || 0), `${eth?.price_change_percentage_24h?.toFixed(2) || 0}%`, eth?.price_change_percentage_24h >= 0 ? 'positive' : 'negative', '#627EEA')}
            `;
        }
        
        // Update sidebar stats
        document.getElementById('sidebarMarketCap').textContent = formatCurrency(totalMarketCap);
        document.getElementById('sidebarVolume').textContent = formatCurrency(totalVolume);
        document.getElementById('sidebarBTC').textContent = formatCurrency(btc?.current_price || 0);
        document.getElementById('sidebarETH').textContent = formatCurrency(eth?.current_price || 0);
        
        // Update sidebar BTC/ETH colors
        const btcElement = document.getElementById('sidebarBTC');
        const ethElement = document.getElementById('sidebarETH');
        
        if (btc?.price_change_percentage_24h >= 0) {
            btcElement.classList.add('positive');
            btcElement.classList.remove('negative');
        } else {
            btcElement.classList.add('negative');
            btcElement.classList.remove('positive');
        }
        
        if (eth?.price_change_percentage_24h >= 0) {
            ethElement.classList.add('positive');
            ethElement.classList.remove('negative');
        } else {
            ethElement.classList.add('negative');
            ethElement.classList.remove('positive');
        }
        
    } catch (error) {
        console.error('Error loading market stats:', error);
    }
}

function createStatCard(label, value, change, changeType, color) {
    const changeIcon = changeType === 'positive' 
        ? '<path d="M12 19V5M5 12l7-7 7 7" stroke="currentColor" stroke-width="2"/>'
        : '<path d="M12 5v14M19 12l-7 7-7-7" stroke="currentColor" stroke-width="2"/>';
    
    return `
        <div class="glass-card stat-card">
            <div class="stat-header">
                <div class="stat-icon" style="background: linear-gradient(135deg, ${color}, ${color}CC); box-shadow: 0 0 20px ${color}66;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="white" stroke-width="2"/>
                    </svg>
                </div>
                <h3>${label}</h3>
            </div>
            <div class="stat-value-wrapper">
                <div class="stat-value">${value}</div>
                <div class="stat-change ${changeType}">
                    <div class="change-icon-wrapper ${changeType}">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                            ${changeIcon}
                        </svg>
                    </div>
                    <span class="change-value">${change}</span>
                </div>
            </div>
        </div>
    `;
}

// Load Top Coins
async function loadTopCoins() {
    try {
        const response = await fetch('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=20&page=1&sparkline=true');
        const coins = await response.json();
        
        const table = document.getElementById('topCoinsTable');
        if (!table) return;
        
        table.innerHTML = coins.map((coin, index) => {
            const change24h = coin.price_change_percentage_24h || 0;
            const change7d = coin.price_change_percentage_7d_in_currency || 0;
            
            return `
                <tr>
                    <td>${index + 1}</td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <img src="${coin.image}" alt="${coin.name}" style="width: 32px; height: 32px; border-radius: 50%;">
                            <div>
                                <div style="font-weight: 600;">${coin.name}</div>
                                <div style="font-size: 12px; color: var(--text-muted);">${coin.symbol.toUpperCase()}</div>
                            </div>
                        </div>
                    </td>
                    <td style="font-weight: 600;">$${formatNumber(coin.current_price)}</td>
                    <td>
                        <span class="badge ${change24h >= 0 ? 'badge-success' : 'badge-danger'}">
                            ${change24h >= 0 ? '↑' : '↓'} ${Math.abs(change24h).toFixed(2)}%
                        </span>
                    </td>
                    <td>
                        <span class="badge ${change7d >= 0 ? 'badge-success' : 'badge-danger'}">
                            ${change7d >= 0 ? '↑' : '↓'} ${Math.abs(change7d).toFixed(2)}%
                        </span>
                    </td>
                    <td>$${formatNumber(coin.market_cap)}</td>
                    <td>$${formatNumber(coin.total_volume)}</td>
                    <td>
                        <canvas id="spark-${coin.id}" width="100" height="30"></canvas>
                    </td>
                </tr>
            `;
        }).join('');
        
        // Create sparklines
        setTimeout(() => {
            coins.forEach(coin => {
                if (coin.sparkline_in_7d && coin.sparkline_in_7d.price) {
                    createSparkline(`spark-${coin.id}`, coin.sparkline_in_7d.price, coin.price_change_percentage_24h >= 0);
                }
            });
        }, 100);
        
    } catch (error) {
        console.error('Error loading top coins:', error);
    }
}

// Create Sparkline
function createSparkline(canvasId, data, isPositive) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const color = isPositive ? '#10B981' : '#EF4444';
    
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: data.map((_, i) => i),
            datasets: [{
                data: data,
                borderColor: color,
                backgroundColor: color + '20',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
            scales: { x: { display: false }, y: { display: false } }
        }
    });
}

// Load Main Chart
async function loadMainChart() {
    try {
        const response = await fetch('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=true');
        const coins = await response.json();
        
        const canvas = document.getElementById('mainChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        if (AppState.charts.main) {
            AppState.charts.main.destroy();
        }
        
        const colors = ['#3B82F6', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#F97316', '#14B8A6', '#6366F1'];
        
        const datasets = coins.slice(0, 10).map((coin, index) => ({
            label: coin.name,
            data: coin.sparkline_in_7d.price,
            borderColor: colors[index],
            backgroundColor: colors[index] + '20',
            borderWidth: 3,
            fill: false,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: colors[index],
            pointHoverBorderColor: '#fff',
            pointHoverBorderWidth: 2
        }));
        
        AppState.charts.main = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array.from({length: 168}, (_, i) => i),
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 15,
                            font: { size: 12, weight: 600 }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        titleColor: '#fff',
                        bodyColor: '#E2E8F0',
                        borderColor: 'rgba(6, 182, 212, 0.5)',
                        borderWidth: 1,
                        padding: 16,
                        displayColors: true,
                        boxPadding: 8,
                        usePointStyle: true
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { display: false }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94A3B8',
                            callback: function(value) {
                                return '$' + formatNumber(value);
                            }
                        }
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('Error loading main chart:', error);
    }
}

// Load Coin Chart
async function loadCoinChart(coinId, days) {
    try {
        const response = await fetch(`https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=usd&days=${days}`);
        const data = await response.json();
        
        const scheme = ColorSchemes[AppState.selectedColorScheme];
        
        // Update chart title and badges
        const coin = AppState.selectedCoin;
        document.getElementById('chartTitle').textContent = `${coin.name} (${coin.symbol.toUpperCase()}) Price Chart`;
        document.getElementById('chartPrice').textContent = `$${formatNumber(coin.current_price)}`;
        
        const change = coin.price_change_percentage_24h;
        const changeElement = document.getElementById('chartChange');
        changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
        changeElement.className = `badge ${change >= 0 ? 'badge-success' : 'badge-danger'}`;
        
        // Price Chart
        const priceCanvas = document.getElementById('priceChart');
        if (priceCanvas) {
            const ctx = priceCanvas.getContext('2d');
            
            if (AppState.charts.price) {
                AppState.charts.price.destroy();
            }
            
            const labels = data.prices.map(p => new Date(p[0]));
            const prices = data.prices.map(p => p[1]);
            
            AppState.charts.price = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Price (USD)',
                        data: prices,
                        borderColor: scheme.primary,
                        backgroundColor: scheme.primary + '20',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 8,
                        pointHoverBackgroundColor: scheme.primary,
                        pointHoverBorderColor: '#fff',
                        pointHoverBorderWidth: 3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(15, 23, 42, 0.95)',
                            padding: 16,
                            displayColors: false,
                            callbacks: {
                                label: function(context) {
                                    return 'Price: $' + formatNumber(context.parsed.y);
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: days <= 1 ? 'hour' : days <= 7 ? 'day' : days <= 30 ? 'day' : 'week'
                            },
                            grid: { display: false },
                            ticks: { color: '#94A3B8', maxRotation: 0, autoSkip: true, maxTicksLimit: 8 }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                            ticks: {
                                color: '#94A3B8',
                                callback: function(value) {
                                    return '$' + formatNumber(value);
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Volume Chart
        const volumeCanvas = document.getElementById('volumeChart');
        if (volumeCanvas) {
            const ctx = volumeCanvas.getContext('2d');
            
            if (AppState.charts.volume) {
                AppState.charts.volume.destroy();
            }
            
            const volumeLabels = data.total_volumes.map(v => new Date(v[0]));
            const volumes = data.total_volumes.map(v => v[1]);
            
            AppState.charts.volume = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: volumeLabels,
                    datasets: [{
                        label: 'Volume',
                        data: volumes,
                        backgroundColor: scheme.secondary + '80',
                        borderColor: scheme.secondary,
                        borderWidth: 2,
                        borderRadius: 6,
                        borderSkipped: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(15, 23, 42, 0.95)',
                            padding: 16,
                            callbacks: {
                                label: function(context) {
                                    return 'Volume: $' + formatNumber(context.parsed.y);
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: days <= 1 ? 'hour' : days <= 7 ? 'day' : days <= 30 ? 'day' : 'week'
                            },
                            grid: { display: false },
                            ticks: { color: '#94A3B8', maxRotation: 0, autoSkip: true, maxTicksLimit: 8 }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                            ticks: {
                                color: '#94A3B8',
                                callback: function(value) {
                                    return '$' + formatNumber(value);
                                }
                            }
                        }
                    }
                }
            });
        }
        
    } catch (error) {
        console.error('Error loading coin chart:', error);
    }
}

// Auto Refresh
function startAutoRefresh() {
    setInterval(() => {
        loadMarketStats();
        AppState.lastUpdate = new Date();
        updateLastUpdateTime();
    }, 60000); // Every minute
}

function updateLastUpdateTime() {
    const element = document.getElementById('lastUpdate');
    if (!element) return;
    
    const now = new Date();
    const diff = Math.floor((now - AppState.lastUpdate) / 1000);
    
    if (diff < 60) {
        element.textContent = 'Just now';
    } else if (diff < 3600) {
        element.textContent = `${Math.floor(diff / 60)}m ago`;
    } else {
        element.textContent = `${Math.floor(diff / 3600)}h ago`;
    }
}

// Refresh Data
window.refreshData = function() {
    loadInitialData();
};

// Utility Functions
function formatNumber(num) {
    if (num === null || num === undefined || isNaN(num)) {
        return '0.00';
    }
    num = Number(num);
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toFixed(2);
}

function formatCurrency(num) {
    return '$' + formatNumber(num);
}

// Export for global access
window.AppState = AppState;
window.selectCoin = selectCoin;
