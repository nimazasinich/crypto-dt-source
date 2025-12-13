/**
 * ═══════════════════════════════════════════════════════════════════
 * TRADINGVIEW STYLE CHARTS
 * Professional Trading Charts with Advanced Features
 * ═══════════════════════════════════════════════════════════════════
 */

// Chart instances storage
const tradingViewCharts = {};

/**
 * Create TradingView-style candlestick chart
 */
export function createCandlestickChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    // Destroy existing chart
    if (tradingViewCharts[canvasId]) {
        tradingViewCharts[canvasId].destroy();
    }

    const {
        symbol = 'BTC',
        timeframe = '1D',
        showVolume = true,
        showIndicators = true
    } = options;

    // Process candlestick data
    const labels = data.map(d => new Date(d.time).toLocaleDateString());
    const opens = data.map(d => d.open);
    const highs = data.map(d => d.high);
    const lows = data.map(d => d.low);
    const closes = data.map(d => d.close);
    const volumes = data.map(d => d.volume || 0);

    // Determine colors based on price movement
    const colors = data.map((d, i) => {
        if (i === 0) return closes[i] >= opens[i] ? '#10B981' : '#EF4444';
        return closes[i] >= closes[i - 1] ? '#10B981' : '#EF4444';
    });

    const datasets = [
        {
            label: 'Price',
            data: closes,
            borderColor: '#00D4FF',
            backgroundColor: 'rgba(0, 212, 255, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.1,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: '#00D4FF',
            pointHoverBorderColor: '#fff',
            pointHoverBorderWidth: 2,
            yAxisID: 'y'
        }
    ];

    if (showVolume) {
        datasets.push({
            label: 'Volume',
            data: volumes,
            type: 'bar',
            backgroundColor: colors.map(c => c + '40'),
            borderColor: colors,
            borderWidth: 1,
            yAxisID: 'y1',
            order: 2
        });
    }

    tradingViewCharts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    align: 'end',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 12,
                            weight: 600,
                            family: "'Manrope', sans-serif"
                        },
                        color: '#E2E8F0'
                    }
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(15, 23, 42, 0.98)',
                    titleColor: '#00D4FF',
                    bodyColor: '#E2E8F0',
                    borderColor: 'rgba(0, 212, 255, 0.5)',
                    borderWidth: 1,
                    padding: 16,
                    displayColors: true,
                    boxPadding: 8,
                    usePointStyle: true,
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            if (context.datasetIndex === 0) {
                                return `Price: $${context.parsed.y.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                            } else {
                                return `Volume: ${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#94A3B8',
                        font: {
                            size: 11,
                            family: "'Manrope', sans-serif"
                        },
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 12
                    },
                    border: {
                        display: false
                    }
                },
                y: {
                    type: 'linear',
                    position: 'left',
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94A3B8',
                        font: {
                            size: 11,
                            family: "'Manrope', sans-serif"
                        },
                        callback: function(value) {
                            return '$' + value.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 });
                        }
                    }
                },
                y1: showVolume ? {
                    type: 'linear',
                    position: 'right',
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        display: false
                    }
                } : undefined
            }
        }
    });

    return tradingViewCharts[canvasId];
}

/**
 * Create advanced line chart with indicators
 */
export function createAdvancedLineChart(canvasId, priceData, indicators = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    if (tradingViewCharts[canvasId]) {
        tradingViewCharts[canvasId].destroy();
    }

    const labels = priceData.map(d => new Date(d.time || d.timestamp).toLocaleDateString());
    const prices = priceData.map(d => d.price || d.value);

    // Calculate indicators
    const ma20 = indicators.ma20 || calculateMA(prices, 20);
    const ma50 = indicators.ma50 || calculateMA(prices, 50);
    const rsi = indicators.rsi || calculateRSI(prices, 14);

    const datasets = [
        {
            label: 'Price',
            data: prices,
            borderColor: '#00D4FF',
            backgroundColor: 'rgba(0, 212, 255, 0.1)',
            borderWidth: 2.5,
            fill: true,
            tension: 0.1,
            pointRadius: 0,
            pointHoverRadius: 6,
            yAxisID: 'y',
            order: 1
        }
    ];

    if (indicators.showMA20) {
        datasets.push({
            label: 'MA 20',
            data: ma20,
            borderColor: '#8B5CF6',
            backgroundColor: 'transparent',
            borderWidth: 1.5,
            borderDash: [5, 5],
            fill: false,
            tension: 0.1,
            pointRadius: 0,
            yAxisID: 'y',
            order: 2
        });
    }

    if (indicators.showMA50) {
        datasets.push({
            label: 'MA 50',
            data: ma50,
            borderColor: '#EC4899',
            backgroundColor: 'transparent',
            borderWidth: 1.5,
            borderDash: [5, 5],
            fill: false,
            tension: 0.1,
            pointRadius: 0,
            yAxisID: 'y',
            order: 3
        });
    }

    tradingViewCharts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    align: 'end',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 12,
                            weight: 600,
                            family: "'Manrope', sans-serif"
                        },
                        color: '#E2E8F0'
                    }
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(15, 23, 42, 0.98)',
                    titleColor: '#00D4FF',
                    bodyColor: '#E2E8F0',
                    borderColor: 'rgba(0, 212, 255, 0.5)',
                    borderWidth: 1,
                    padding: 16,
                    displayColors: true,
                    boxPadding: 8
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#94A3B8',
                        font: {
                            size: 11,
                            family: "'Manrope', sans-serif"
                        },
                        maxRotation: 0,
                        autoSkip: true
                    },
                    border: {
                        display: false
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94A3B8',
                        font: {
                            size: 11,
                            family: "'Manrope', sans-serif"
                        },
                        callback: function(value) {
                            return '$' + value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                        }
                    }
                }
            }
        }
    });

    return tradingViewCharts[canvasId];
}

/**
 * Calculate Moving Average
 */
function calculateMA(data, period) {
    const result = [];
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
            result.push(null);
        } else {
            const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
            result.push(sum / period);
        }
    }
    return result;
}

/**
 * Calculate RSI (Relative Strength Index)
 */
function calculateRSI(data, period = 14) {
    const result = [];
    const gains = [];
    const losses = [];

    for (let i = 1; i < data.length; i++) {
        const change = data[i] - data[i - 1];
        gains.push(change > 0 ? change : 0);
        losses.push(change < 0 ? Math.abs(change) : 0);
    }

    for (let i = 0; i < data.length; i++) {
        if (i < period) {
            result.push(null);
        } else {
            const avgGain = gains.slice(i - period, i).reduce((a, b) => a + b, 0) / period;
            const avgLoss = losses.slice(i - period, i).reduce((a, b) => a + b, 0) / period;
            const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
            const rsi = 100 - (100 / (1 + rs));
            result.push(rsi);
        }
    }

    return result;
}

/**
 * Create volume chart
 */
export function createVolumeChart(canvasId, volumeData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    if (tradingViewCharts[canvasId]) {
        tradingViewCharts[canvasId].destroy();
    }

    const labels = volumeData.map(d => new Date(d.time).toLocaleDateString());
    const volumes = volumeData.map(d => d.volume);
    const colors = volumeData.map((d, i) => {
        if (i === 0) return '#10B981';
        return volumes[i] >= volumes[i - 1] ? '#10B981' : '#EF4444';
    });

    tradingViewCharts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Volume',
                data: volumes,
                backgroundColor: colors.map(c => c + '60'),
                borderColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.98)',
                    titleColor: '#00D4FF',
                    bodyColor: '#E2E8F0',
                    borderColor: 'rgba(0, 212, 255, 0.5)',
                    borderWidth: 1,
                    padding: 12
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#94A3B8',
                        font: {
                            size: 10,
                            family: "'Manrope', sans-serif"
                        }
                    },
                    border: {
                        display: false
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94A3B8',
                        font: {
                            size: 10,
                            family: "'Manrope', sans-serif"
                        },
                        callback: function(value) {
                            if (value >= 1e9) return (value / 1e9).toFixed(2) + 'B';
                            if (value >= 1e6) return (value / 1e6).toFixed(2) + 'M';
                            if (value >= 1e3) return (value / 1e3).toFixed(2) + 'K';
                            return value;
                        }
                    }
                }
            }
        }
    });

    return tradingViewCharts[canvasId];
}

/**
 * Destroy chart
 */
export function destroyChart(canvasId) {
    if (tradingViewCharts[canvasId]) {
        tradingViewCharts[canvasId].destroy();
        delete tradingViewCharts[canvasId];
    }
}

/**
 * Update chart data
 */
export function updateChart(canvasId, newData) {
    if (tradingViewCharts[canvasId]) {
        tradingViewCharts[canvasId].data = newData;
        tradingViewCharts[canvasId].update();
    }
}

