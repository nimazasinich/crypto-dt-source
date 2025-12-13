/**
 * Integrated Trading System V2
 * Combines all components into a unified intelligent trading system
 * Features: Advanced strategies, market monitoring, notifications, regime detection
 */

import { EnhancedMarketMonitor } from './enhanced-market-monitor.js';
import { NotificationManager, NOTIFICATION_PRIORITY } from './enhanced-notification-system.js';
import { AdaptiveRegimeDetector, MARKET_REGIMES } from './adaptive-regime-detector.js';
import { analyzeWithAdvancedStrategy, ADVANCED_STRATEGIES_V2 } from './advanced-strategies-v2.js';
import { analyzeWithStrategy, HYBRID_STRATEGIES } from './trading-strategies.js';

/**
 * Integrated Trading System
 */
export class IntegratedTradingSystem {
    constructor(config = {}) {
        this.config = {
            symbol: config.symbol || 'BTC',
            strategy: config.strategy || 'ict-market-structure',
            useAdaptiveStrategy: config.useAdaptiveStrategy !== false,
            interval: config.interval || 60000,
            enableNotifications: config.enableNotifications !== false,
            notificationChannels: config.notificationChannels || ['browser'],
            telegram: config.telegram || null,
            riskLevel: config.riskLevel || 'medium'
        };

        // Initialize components
        this.monitor = new EnhancedMarketMonitor({
            symbol: this.config.symbol,
            strategy: this.config.strategy,
            interval: this.config.interval,
            useWebSocket: true
        });

        this.notificationManager = new NotificationManager({
            enabled: this.config.enableNotifications,
            channels: this.config.notificationChannels,
            telegram: this.config.telegram
        });

        this.regimeDetector = new AdaptiveRegimeDetector({
            lookbackPeriod: 100,
            volatilityPeriod: 20,
            trendPeriod: 50
        });

        // State
        this.isRunning = false;
        this.currentRegime = null;
        this.lastAnalysis = null;
        this.performanceStats = {
            totalSignals: 0,
            successfulSignals: 0,
            failedSignals: 0,
            avgConfidence: 0,
            startTime: null
        };

        // Setup event handlers
        this.setupEventHandlers();
    }

    /**
     * Start the integrated trading system
     * @returns {Promise<Object>} Start result
     */
    async start() {
        if (this.isRunning) {
            return { success: false, message: 'Already running' };
        }

        console.log('[IntegratedSystem] Starting...');

        try {
            // Start market monitor
            const monitorResult = await this.monitor.start();
            
            if (!monitorResult.success) {
                throw new Error(`Monitor failed to start: ${monitorResult.message}`);
            }

            this.isRunning = true;
            this.performanceStats.startTime = Date.now();

            // Send startup notification
            if (this.config.enableNotifications) {
                await this.notificationManager.send({
                    type: 'system',
                    priority: NOTIFICATION_PRIORITY.LOW,
                    title: '✅ Trading System Started',
                    message: `Monitoring ${this.config.symbol} with ${this.config.strategy} strategy`,
                    data: {
                        symbol: this.config.symbol,
                        strategy: this.config.strategy,
                        adaptive: this.config.useAdaptiveStrategy
                    }
                });
            }

            console.log('[IntegratedSystem] Started successfully');
            return { success: true, message: 'System started successfully' };
        } catch (error) {
            console.error('[IntegratedSystem] Start error:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Stop the integrated trading system
     */
    stop() {
        if (!this.isRunning) return;

        console.log('[IntegratedSystem] Stopping...');
        
        this.monitor.stop();
        this.isRunning = false;

        // Send shutdown notification
        if (this.config.enableNotifications) {
            this.notificationManager.send({
                type: 'system',
                priority: NOTIFICATION_PRIORITY.LOW,
                title: '🛑 Trading System Stopped',
                message: `Stopped monitoring ${this.config.symbol}`,
                data: this.getPerformanceStats()
            });
        }

        console.log('[IntegratedSystem] Stopped');
    }

    /**
     * Setup event handlers for monitor
     */
    setupEventHandlers() {
        // Handle signals from monitor
        this.monitor.on('Signal', async (analysis) => {
            await this.handleSignal(analysis);
        });

        // Handle price updates
        this.monitor.on('PriceUpdate', (priceData) => {
            this.handlePriceUpdate(priceData);
        });

        // Handle errors
        this.monitor.on('Error', (error) => {
            this.handleError(error);
        });

        // Handle connection changes
        this.monitor.on('ConnectionChange', (status) => {
            this.handleConnectionChange(status);
        });
    }

    /**
     * Handle trading signal
     * @param {Object} analysis - Analysis results
     */
    async handleSignal(analysis) {
        try {
            console.log('[IntegratedSystem] Signal received:', analysis);

            // Update stats
            this.performanceStats.totalSignals++;
            this.lastAnalysis = analysis;

            // Filter signals based on risk level
            if (!this.shouldExecuteSignal(analysis)) {
                console.log('[IntegratedSystem] Signal filtered based on risk level');
                return;
            }

            // Send notification
            if (this.config.enableNotifications && analysis.signal !== 'hold') {
                await this.notificationManager.sendSignal(analysis);
            }

            // Emit event for UI
            this.emitEvent('signal', analysis);
        } catch (error) {
            console.error('[IntegratedSystem] Signal handling error:', error);
        }
    }

    /**
     * Handle price updates
     * @param {Object} priceData - Price data
     */
    handlePriceUpdate(priceData) {
        // Emit event for UI
        this.emitEvent('priceUpdate', priceData);
    }

    /**
     * Handle errors
     * @param {Error} error - Error object
     */
    async handleError(error) {
        console.error('[IntegratedSystem] Error:', error);

        // Send error notification for critical errors
        if (this.config.enableNotifications) {
            await this.notificationManager.sendError(error, 'Trading System');
        }

        // Emit event for UI
        this.emitEvent('error', error);
    }

    /**
     * Handle connection status changes
     * @param {Object} status - Connection status
     */
    handleConnectionChange(status) {
        console.log('[IntegratedSystem] Connection change:', status);

        // Emit event for UI
        this.emitEvent('connectionChange', status);

        // Notify on circuit breaker
        if (status.status === 'circuit-breaker-open' && this.config.enableNotifications) {
            this.notificationManager.send({
                type: 'warning',
                priority: NOTIFICATION_PRIORITY.HIGH,
                title: '⚠️ Circuit Breaker Activated',
                message: 'Too many errors detected. System paused temporarily.',
                data: status
            });
        }
    }

    /**
     * Perform analysis with adaptive strategy selection
     * @param {Array<Object>} ohlcvData - OHLCV data
     * @returns {Promise<Object>} Analysis results
     */
    async performAnalysis(ohlcvData) {
        try {
            let strategy = this.config.strategy;

            // Detect market regime if adaptive mode enabled
            if (this.config.useAdaptiveStrategy) {
                const regimeAnalysis = this.regimeDetector.detectRegime(ohlcvData);
                this.currentRegime = regimeAnalysis;

                // Get recommended strategies for this regime
                const recommendedStrategies = this.regimeDetector.getRecommendedStrategies();
                
                // Use first recommended strategy
                if (recommendedStrategies && recommendedStrategies.length > 0) {
                    strategy = recommendedStrategies[0];
                    console.log(`[IntegratedSystem] Regime: ${regimeAnalysis.regime}, Using: ${strategy}`);
                }
            }

            // Perform analysis
            let analysis;
            
            if (ADVANCED_STRATEGIES_V2[strategy]) {
                analysis = await analyzeWithAdvancedStrategy(this.config.symbol, strategy, ohlcvData);
            } else if (HYBRID_STRATEGIES[strategy]) {
                const marketData = {
                    price: ohlcvData[ohlcvData.length - 1].close,
                    volume: ohlcvData[ohlcvData.length - 1].volume,
                    high24h: Math.max(...ohlcvData.slice(-24).map(c => c.high)),
                    low24h: Math.min(...ohlcvData.slice(-24).map(c => c.low))
                };
                analysis = analyzeWithStrategy(this.config.symbol, strategy, marketData);
            } else {
                throw new Error(`Unknown strategy: ${strategy}`);
            }

            // Enrich with regime data
            if (this.currentRegime) {
                analysis.regime = this.currentRegime.regime;
                analysis.regimeConfidence = this.currentRegime.confidence;
            }

            return analysis;
        } catch (error) {
            console.error('[IntegratedSystem] Analysis error:', error);
            throw error;
        }
    }

    /**
     * Determine if signal should be executed based on risk level
     * @param {Object} analysis - Analysis results
     * @returns {boolean} Should execute
     */
    shouldExecuteSignal(analysis) {
        const riskLevels = {
            'very-low': { minConfidence: 50 },
            'low': { minConfidence: 60 },
            'medium': { minConfidence: 70 },
            'high': { minConfidence: 80 },
            'very-high': { minConfidence: 85 }
        };

        const levelConfig = riskLevels[this.config.riskLevel] || riskLevels.medium;
        
        // Don't execute hold signals
        if (analysis.signal === 'hold') {
            return false;
        }

        // Check confidence threshold
        return analysis.confidence >= levelConfig.minConfidence;
    }

    /**
     * Emit custom event
     * @param {string} eventName - Event name
     * @param {*} data - Event data
     */
    emitEvent(eventName, data) {
        window.dispatchEvent(new CustomEvent(`tradingSystem:${eventName}`, {
            detail: data
        }));
    }

    /**
     * Update system configuration
     * @param {Object} newConfig - New configuration
     */
    updateConfig(newConfig) {
        const needsRestart = this.isRunning && (
            newConfig.symbol !== this.config.symbol ||
            newConfig.interval !== this.config.interval
        );

        // Update configuration
        Object.assign(this.config, newConfig);

        // Update components
        if (newConfig.symbol || newConfig.strategy || newConfig.interval) {
            this.monitor.updateConfig({
                symbol: this.config.symbol,
                strategy: this.config.strategy,
                interval: this.config.interval
            });
        }

        if (newConfig.notificationChannels || newConfig.telegram) {
            this.notificationManager.updateConfig({
                channels: this.config.notificationChannels,
                telegram: this.config.telegram
            });
        }

        // Restart if necessary
        if (needsRestart) {
            this.stop();
            this.start();
        }
    }

    /**
     * Get current system status
     * @returns {Object} System status
     */
    getStatus() {
        return {
            isRunning: this.isRunning,
            config: this.config,
            monitorStatus: this.monitor.getStatus(),
            currentRegime: this.currentRegime,
            lastAnalysis: this.lastAnalysis,
            performanceStats: this.getPerformanceStats()
        };
    }

    /**
     * Get performance statistics
     * @returns {Object} Performance stats
     */
    getPerformanceStats() {
        const runtime = this.performanceStats.startTime
            ? Date.now() - this.performanceStats.startTime
            : 0;

        return {
            ...this.performanceStats,
            runtime,
            runtimeFormatted: this.formatDuration(runtime),
            successRate: this.performanceStats.totalSignals > 0
                ? (this.performanceStats.successfulSignals / this.performanceStats.totalSignals) * 100
                : 0
        };
    }

    /**
     * Format duration in milliseconds
     * @param {number} ms - Duration in milliseconds
     * @returns {string} Formatted duration
     */
    formatDuration(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}d ${hours % 24}h`;
        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }

    /**
     * Test all components
     * @returns {Promise<Object>} Test results
     */
    async test() {
        console.log('[IntegratedSystem] Running system test...');

        const results = {
            monitor: false,
            notifications: false,
            regimeDetection: false,
            strategy: false
        };

        try {
            // Test monitor
            const monitorStatus = this.monitor.getStatus();
            results.monitor = !!monitorStatus;

            // Test notifications
            const notifResult = await this.notificationManager.test();
            results.notifications = notifResult.success;

            // Test regime detection with sample data
            const sampleData = this.generateSampleData();
            const regimeResult = this.regimeDetector.detectRegime(sampleData);
            results.regimeDetection = !!regimeResult.regime;

            // Test strategy analysis
            const analysisResult = await this.performAnalysis(sampleData);
            results.strategy = !!analysisResult.signal;

            console.log('[IntegratedSystem] Test results:', results);
            return {
                success: Object.values(results).every(r => r),
                results
            };
        } catch (error) {
            console.error('[IntegratedSystem] Test error:', error);
            return {
                success: false,
                results,
                error: error.message
            };
        }
    }

    /**
     * Generate sample data for testing
     * @returns {Array<Object>} Sample OHLCV data
     */
    generateSampleData() {
        const data = [];
        let price = 50000;

        for (let i = 0; i < 100; i++) {
            const volatility = price * 0.02;
            const open = price + (Math.random() - 0.5) * volatility;
            const close = open + (Math.random() - 0.5) * volatility;
            const high = Math.max(open, close) + Math.random() * volatility * 0.5;
            const low = Math.min(open, close) - Math.random() * volatility * 0.5;
            const volume = Math.random() * 1000000;

            data.push({
                timestamp: Date.now() - (99 - i) * 3600000,
                open, high, low, close, volume
            });

            price = close;
        }

        return data;
    }

    /**
     * Get available strategies
     * @returns {Object} Available strategies
     */
    static getAvailableStrategies() {
        return {
            advanced: ADVANCED_STRATEGIES_V2,
            hybrid: HYBRID_STRATEGIES
        };
    }

    /**
     * Get market regimes
     * @returns {Object} Market regimes
     */
    static getMarketRegimes() {
        return MARKET_REGIMES;
    }
}

export default IntegratedTradingSystem;

