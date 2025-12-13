/**
 * Enhanced Charts Module
 * Modern, Beautiful, Responsive Charts with Chart.js
 */

// Chart.js Global Configuration
Chart.defaults.color = '#e2e8f0';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
Chart.defaults.font.family = "'Manrope', 'Inter', sans-serif";
Chart.defaults.font.size = 13;
Chart.defaults.font.weight = 500;

// Chart Instances Storage
const chartInstances = {};

/**
 * Initialize Market Overview Chart
 * Shows top 5 cryptocurrencies price trends
 */
export function initMarketOverviewChart(data) {
    const ctx = document.getElementById('market-overview-chart');
    if (!ctx) return;

    // Destroy existing chart
    if (chartInstances.marketOverview) {
        chartInstances.marketOverview.destroy();
    }

    const topCoins = data.slice(0, 5);
    const labels = Array.from({length: 24}, (_, i) => `${i}:00`);
    
    const colors = [
        { border: '#8f88ff', bg: 'rgba(143, 136, 255, 0.1)' },
        { border: '#16d9fa', bg: 'rgba(22, 217, 250, 0.1)' },
        { border: '#4ade80', bg: 'rgba(74, 222, 128, 0.1)' },
        { border: '#f472b6', bg: 'rgba(244, 114, 182, 0.1)' },
        { border: '#facc15', bg: 'rgba(250, 204, 21, 0.1)' }
    ];

    const datasets = topCoins.map((coin, index) => ({
        label: coin.name,
        data: coin.sparkline_in_7d?.price?.slice(-24) || [],
        borderColor: colors[index].border,
        backgroundColor: colors[index].bg,
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: colors[index].border,
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2
    }));

    chartInstances.marketOverview = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
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
                        padding: 20,
                        font: {
                            size: 13,
                            weight: 600
                        },
                        color: '#e2e8f0'
                    }
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#fff',
                    bodyColor: '#e2e8f0',
                    borderColor: 'rgba(143, 136, 255, 0.5)',
                    borderWidth: 1,
                    padding: 16,
                    displayColors: true,
                    boxPadding: 8,
                    usePointStyle: true,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            size: 11
                        },
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create Mini Sparkline Chart for Table
 */
export function createSparkline(canvasId, data, color = '#8f88ff') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    new Chart(ctx, {
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
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            scales: {
                x: { display: false },
                y: { display: false }
            }
        }
    });
}

/**
 * Initialize Price Chart with Advanced Features
 */
export function initPriceChart(coinId, days = 7) {
    const ctx = document.getElementById('price-chart');
    if (!ctx) return;

    // Destroy existing
    if (chartInstances.price) {
        chartInstances.price.destroy();
    }

    // Fetch data and create chart
    fetch(`https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=usd&days=${days}`)
        .then(res => res.json())
        .then(data => {
            const labels = data.prices.map(p => new Date(p[0]).toLocaleDateString());
            const prices = data.prices.map(p => p[1]);

            chartInstances.price = new Chart(ctx, {
                type: 'line',
                data: {
                    labels,
                    datasets: [{
                        label: 'Price (USD)',
                        data: prices,
                        borderColor: '#8f88ff',
                        backgroundColor: 'rgba(143, 136, 255, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 8,
                        pointHoverBackgroundColor: '#8f88ff',
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
                            titleColor: '#fff',
                            bodyColor: '#e2e8f0',
                            borderColor: 'rgba(143, 136, 255, 0.5)',
                            borderWidth: 1,
                            padding: 16,
                            displayColors: false,
                            callbacks: {
                                label: function(context) {
                                    return 'Price: $' + context.parsed.y.toLocaleString();
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: {
                                color: '#94a3b8',
                                maxRotation: 0,
                                autoSkip: true,
                                maxTicksLimit: 8
                            }
                        },
                        y: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                color: '#94a3b8',
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
        });
}

/**
 * Initialize Volume Chart
 */
export function initVolumeChart(coinId, days = 7) {
    const ctx = document.getElementById('volume-chart');
    if (!ctx) return;

    if (chartInstances.volume) {
        chartInstances.volume.destroy();
    }

    fetch(`https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=usd&days=${days}`)
        .then(res => res.json())
        .then(data => {
            const labels = data.total_volumes.map(v => new Date(v[0]).toLocaleDateString());
            const volumes = data.total_volumes.map(v => v[1]);

            chartInstances.volume = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [{
                        label: 'Volume',
                        data: volumes,
                        backgroundColor: 'rgba(74, 222, 128, 0.6)',
                        borderColor: '#4ade80',
                        borderWidth: 2,
                        borderRadius: 8,
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
                                    return 'Volume: $' + (context.parsed.y / 1000000).toFixed(2) + 'M';
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: {
                                color: '#94a3b8',
                                maxRotation: 0,
                                autoSkip: true,
                                maxTicksLimit: 8
                            }
                        },
                        y: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                color: '#94a3b8',
                                callback: function(value) {
                                    return '$' + (value / 1000000).toFixed(0) + 'M';
                                }
                            }
                        }
                    }
                }
            });
        });
}

/**
 * Initialize Sentiment Doughnut Chart
 */
export function initSentimentChart() {
    const ctx = document.getElementById('sentiment-chart');
    if (!ctx) return;

    if (chartInstances.sentiment) {
        chartInstances.sentiment.destroy();
    }

    chartInstances.sentiment = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Very Bullish', 'Bullish', 'Neutral', 'Bearish', 'Very Bearish'],
            datasets: [{
                data: [25, 35, 20, 15, 5],
                backgroundColor: [
                    '#4ade80',
                    '#16d9fa',
                    '#facc15',
                    '#f472b6',
                    '#ef4444'
                ],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: {
                            size: 13,
                            weight: 600
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    padding: 16,
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed + '%';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize Market Dominance Pie Chart
 */
export function initDominanceChart(data) {
    const ctx = document.getElementById('dominance-chart');
    if (!ctx) return;

    if (chartInstances.dominance) {
        chartInstances.dominance.destroy();
    }

    const btc = data.find(c => c.id === 'bitcoin');
    const eth = data.find(c => c.id === 'ethereum');
    const bnb = data.find(c => c.id === 'binancecoin');
    
    const totalMarketCap = data.reduce((sum, coin) => sum + coin.market_cap, 0);
    const btcDominance = ((btc?.market_cap || 0) / totalMarketCap * 100).toFixed(1);
    const ethDominance = ((eth?.market_cap || 0) / totalMarketCap * 100).toFixed(1);
    const bnbDominance = ((bnb?.market_cap || 0) / totalMarketCap * 100).toFixed(1);
    const othersDominance = (100 - btcDominance - ethDominance - bnbDominance).toFixed(1);

    chartInstances.dominance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Bitcoin', 'Ethereum', 'BNB', 'Others'],
            datasets: [{
                data: [btcDominance, ethDominance, bnbDominance, othersDominance],
                backgroundColor: [
                    '#facc15',
                    '#8f88ff',
                    '#f472b6',
                    '#94a3b8'
                ],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 13,
                            weight: 600
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    padding: 16,
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed + '%';
                        }
                    }
                }
            }
        }
    });
}

// Export chart instances for external access
export { chartInstances };
