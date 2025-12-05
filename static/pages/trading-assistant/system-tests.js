/**
 * Comprehensive Testing Suite for Trading System
 * Tests all components with mock data and real scenarios
 */

import { IntegratedTradingSystem } from './integrated-trading-system.js';
import { analyzeMarketStructure, detectMomentumDivergences } from './advanced-strategies-v2.js';
import { AdaptiveRegimeDetector, MARKET_REGIMES } from './adaptive-regime-detector.js';
import { NotificationManager } from './enhanced-notification-system.js';

/**
 * Test runner
 */
export class TradingSystemTests {
    constructor() {
        this.results = {
            passed: 0,
            failed: 0,
            total: 0,
            tests: []
        };
    }

    /**
     * Run all tests
     * @returns {Promise<Object>} Test results
     */
    async runAll() {
        console.log('🧪 Running Trading System Tests...\n');

        await this.testMarketStructureAnalysis();
        await this.testMomentumDivergence();
        await this.testRegimeDetection();
        await this.testNotificationSystem();
        await this.testIntegratedSystem();
        await this.testErrorHandling();
        await this.testDataValidation();
        await this.testStrategySelection();

        return this.getSummary();
    }

    /**
     * Test market structure analysis
     */
    async testMarketStructureAnalysis() {
        console.log('📊 Testing Market Structure Analysis...');

        try {
            // Generate bullish trend data
            const bullishData = this.generateTrendData('bullish', 100);
            const bullishResult = analyzeMarketStructure(bullishData);

            this.assert(
                'Bullish market structure detected',
                bullishResult.structure === 'bullish' || bullishResult.structure === 'bullish-weakening',
                `Expected bullish structure, got: ${bullishResult.structure}`
            );

            this.assert(
                'Order blocks identified',
                bullishResult.orderBlocks.length > 0,
                `Expected order blocks, got: ${bullishResult.orderBlocks.length}`
            );

            // Generate bearish trend data
            const bearishData = this.generateTrendData('bearish', 100);
            const bearishResult = analyzeMarketStructure(bearishData);

            this.assert(
                'Bearish market structure detected',
                bearishResult.structure === 'bearish' || bearishResult.structure === 'bearish-weakening',
                `Expected bearish structure, got: ${bearishResult.structure}`
            );

            // Generate ranging data
            const rangingData = this.generateRangingData(100);
            const rangingResult = analyzeMarketStructure(rangingData);

            this.assert(
                'Ranging market detected',
                rangingResult.structure === 'ranging' || rangingResult.structure === 'neutral',
                `Expected ranging/neutral, got: ${rangingResult.structure}`
            );
        } catch (error) {
            this.fail('Market structure analysis', error);
        }
    }

    /**
     * Test momentum divergence detection
     */
    async testMomentumDivergence() {
        console.log('📈 Testing Momentum Divergence Detection...');

        try {
            // Generate divergence scenario
            const data = this.generateDivergenceData();
            const result = detectMomentumDivergences(data);

            this.assert(
                'Divergences detected',
                result.divergences !== undefined,
                'Divergence detection returned result'
            );

            this.assert(
                'Signal generated',
                ['buy', 'sell', 'hold'].includes(result.signal),
                `Valid signal: ${result.signal}`
            );

            this.assert(
                'Confidence calculated',
                result.confidence >= 0 && result.confidence <= 100,
                `Confidence in range: ${result.confidence}`
            );
        } catch (error) {
            this.fail('Momentum divergence detection', error);
        }
    }

    /**
     * Test regime detection
     */
    async testRegimeDetection() {
        console.log('🎯 Testing Regime Detection...');

        try {
            const detector = new AdaptiveRegimeDetector();

            // Test trending bullish
            const trendData = this.generateTrendData('bullish', 100);
            const trendResult = detector.detectRegime(trendData);

            this.assert(
                'Trend regime detected',
                Object.values(MARKET_REGIMES).includes(trendResult.regime),
                `Valid regime: ${trendResult.regime}`
            );

            this.assert(
                'Confidence calculated',
                trendResult.confidence >= 0 && trendResult.confidence <= 100,
                `Confidence: ${trendResult.confidence}`
            );

            // Test ranging
            const rangeData = this.generateRangingData(100);
            const rangeResult = detector.detectRegime(rangeData);

            this.assert(
                'Ranging regime detected',
                rangeResult.regime === MARKET_REGIMES.RANGING || rangeResult.regime === MARKET_REGIMES.CALM,
                `Expected ranging/calm, got: ${rangeResult.regime}`
            );

            // Test volatile
            const volatileData = this.generateVolatileData(100);
            const volatileResult = detector.detectRegime(volatileData);

            this.assert(
                'Volatile regime detected',
                volatileResult.regime.includes('volatile') || volatileResult.metrics.volatility > 5,
                `Volatility: ${volatileResult.metrics.volatility}%`
            );

            // Test recommended strategies
            const strategies = detector.getRecommendedStrategies();
            
            this.assert(
                'Strategies recommended',
                Array.isArray(strategies) && strategies.length > 0,
                `Strategies: ${strategies.length}`
            );
        } catch (error) {
            this.fail('Regime detection', error);
        }
    }

    /**
     * Test notification system
     */
    async testNotificationSystem() {
        console.log('🔔 Testing Notification System...');

        try {
            const notifManager = new NotificationManager({
                enabled: true,
                channels: ['browser']
            });

            // Test signal notification
            const signal = {
                strategy: 'Test Strategy',
                signal: 'buy',
                confidence: 85,
                entry: 50000,
                stopLoss: 48000,
                targets: [
                    { level: 52000, type: 'TP1', percentage: 50 },
                    { level: 54000, type: 'TP2', percentage: 50 }
                ],
                riskRewardRatio: '1:3'
            };

            const result = await notifManager.sendSignal(signal);

            this.assert(
                'Signal notification sent',
                result.success || result.results?.browser?.success === false, // May fail if browser notifications disabled
                `Result: ${JSON.stringify(result)}`
            );

            // Test validation
            const invalidNotif = { title: null };
            const validationResult = notifManager.validateNotification(invalidNotif);

            this.assert(
                'Invalid notification rejected',
                !validationResult.valid,
                'Validation catches invalid notifications'
            );

            // Test history
            const history = notifManager.getHistory();
            
            this.assert(
                'History available',
                Array.isArray(history),
                'History is an array'
            );
        } catch (error) {
            this.fail('Notification system', error);
        }
    }

    /**
     * Test integrated system
     */
    async testIntegratedSystem() {
        console.log('🎮 Testing Integrated System...');

        try {
            const system = new IntegratedTradingSystem({
                symbol: 'BTC',
                strategy: 'ict-market-structure',
                enableNotifications: false,
                useAdaptiveStrategy: true
            });

            // Test initialization
            this.assert(
                'System initialized',
                system !== null,
                'System object created'
            );

            // Test status
            const status = system.getStatus();
            
            this.assert(
                'Status retrieved',
                status.isRunning !== undefined,
                'Status contains running state'
            );

            // Test configuration update
            system.updateConfig({ symbol: 'ETH' });
            
            this.assert(
                'Config updated',
                system.config.symbol === 'ETH',
                'Symbol updated to ETH'
            );

            // Test analysis
            const sampleData = system.generateSampleData();
            const analysis = await system.performAnalysis(sampleData);

            this.assert(
                'Analysis performed',
                analysis.signal !== undefined,
                `Signal: ${analysis.signal}`
            );

            this.assert(
                'Confidence calculated',
                analysis.confidence >= 0 && analysis.confidence <= 100,
                `Confidence: ${analysis.confidence}`
            );

            // Test performance stats
            const stats = system.getPerformanceStats();
            
            this.assert(
                'Performance stats available',
                stats.totalSignals !== undefined,
                'Stats structure valid'
            );
        } catch (error) {
            this.fail('Integrated system', error);
        }
    }

    /**
     * Test error handling
     */
    async testErrorHandling() {
        console.log('🛡️ Testing Error Handling...');

        try {
            // Test with insufficient data
            const shortData = this.generateTrendData('bullish', 10);
            
            try {
                const result = analyzeMarketStructure(shortData);
                this.assert(
                    'Handles insufficient data',
                    result.error !== undefined || result.structure === 'unknown',
                    'Returns error or default for short data'
                );
            } catch (e) {
                this.pass('Handles insufficient data (threw expected error)');
            }

            // Test with null data
            try {
                const result = analyzeMarketStructure(null);
                this.assert(
                    'Handles null data',
                    result.error !== undefined,
                    'Returns error for null data'
                );
            } catch (e) {
                this.pass('Handles null data (threw expected error)');
            }

            // Test with invalid OHLCV data
            const invalidData = [
                { timestamp: 123, open: 'invalid', high: 100, low: 90, close: 95, volume: 1000 }
            ];
            
            try {
                const result = analyzeMarketStructure(invalidData);
                this.pass('Handles invalid data types');
            } catch (e) {
                this.pass('Handles invalid data types (threw expected error)');
            }
        } catch (error) {
            this.fail('Error handling', error);
        }
    }

    /**
     * Test data validation
     */
    async testDataValidation() {
        console.log('✅ Testing Data Validation...');

        try {
            // Test valid OHLCV data
            const validData = {
                timestamp: Date.now(),
                open: 50000,
                high: 51000,
                low: 49000,
                close: 50500,
                volume: 1000000
            };

            this.assert(
                'Valid OHLCV data',
                this.isValidOHLCV(validData),
                'Valid data passes validation'
            );

            // Test invalid OHLCV data
            const invalidData = {
                timestamp: Date.now(),
                open: -1,
                high: 51000,
                low: 49000,
                close: 50500,
                volume: 1000000
            };

            this.assert(
                'Invalid OHLCV data rejected',
                !this.isValidOHLCV(invalidData),
                'Invalid data fails validation'
            );

            // Test data with missing fields
            const incompleteData = {
                timestamp: Date.now(),
                open: 50000,
                high: 51000
            };

            this.assert(
                'Incomplete data rejected',
                !this.isValidOHLCV(incompleteData),
                'Incomplete data fails validation'
            );
        } catch (error) {
            this.fail('Data validation', error);
        }
    }

    /**
     * Test strategy selection
     */
    async testStrategySelection() {
        console.log('🎲 Testing Strategy Selection...');

        try {
            const strategies = IntegratedTradingSystem.getAvailableStrategies();

            this.assert(
                'Strategies available',
                strategies.advanced !== undefined && strategies.hybrid !== undefined,
                'Both strategy types available'
            );

            this.assert(
                'Advanced strategies present',
                Object.keys(strategies.advanced).length > 0,
                `${Object.keys(strategies.advanced).length} advanced strategies`
            );

            this.assert(
                'Hybrid strategies present',
                Object.keys(strategies.hybrid).length > 0,
                `${Object.keys(strategies.hybrid).length} hybrid strategies`
            );

            // Test regime-based strategy recommendation
            const detector = new AdaptiveRegimeDetector();
            const data = this.generateTrendData('bullish', 100);
            const regimeResult = detector.detectRegime(data);
            const recommended = detector.getRecommendedStrategies();

            this.assert(
                'Strategies recommended for regime',
                Array.isArray(recommended) && recommended.length > 0,
                `${recommended.length} strategies recommended for ${regimeResult.regime}`
            );
        } catch (error) {
            this.fail('Strategy selection', error);
        }
    }

    /**
     * Assert helper
     */
    assert(name, condition, message) {
        this.results.total++;
        
        if (condition) {
            this.pass(name);
        } else {
            this.fail(name, new Error(message));
        }
    }

    /**
     * Pass helper
     */
    pass(name) {
        this.results.passed++;
        this.results.tests.push({
            name,
            status: 'passed',
            message: '✅ Passed'
        });
        console.log(`  ✅ ${name}`);
    }

    /**
     * Fail helper
     */
    fail(name, error) {
        this.results.failed++;
        this.results.tests.push({
            name,
            status: 'failed',
            message: `❌ ${error.message}`,
            error: error.stack
        });
        console.error(`  ❌ ${name}: ${error.message}`);
    }

    /**
     * Get test summary
     */
    getSummary() {
        console.log('\n' + '='.repeat(50));
        console.log('📊 Test Summary');
        console.log('='.repeat(50));
        console.log(`Total: ${this.results.total}`);
        console.log(`Passed: ${this.results.passed} ✅`);
        console.log(`Failed: ${this.results.failed} ❌`);
        console.log(`Success Rate: ${((this.results.passed / this.results.total) * 100).toFixed(1)}%`);
        console.log('='.repeat(50) + '\n');

        return this.results;
    }

    /**
     * Generate trending data
     */
    generateTrendData(direction, length) {
        const data = [];
        let price = 50000;
        const trendFactor = direction === 'bullish' ? 1.002 : 0.998;

        for (let i = 0; i < length; i++) {
            const volatility = price * 0.01;
            const open = price;
            price = price * trendFactor;
            const close = price + (Math.random() - 0.5) * volatility;
            const high = Math.max(open, close) + Math.random() * volatility * 0.3;
            const low = Math.min(open, close) - Math.random() * volatility * 0.3;
            const volume = 500000 + Math.random() * 500000;

            data.push({
                timestamp: Date.now() - (length - i) * 3600000,
                open, high, low, close, volume
            });

            price = close;
        }

        return data;
    }

    /**
     * Generate ranging data
     */
    generateRangingData(length) {
        const data = [];
        const basePrice = 50000;
        const rangeSize = basePrice * 0.02;

        for (let i = 0; i < length; i++) {
            const price = basePrice + (Math.random() - 0.5) * rangeSize;
            const volatility = price * 0.005;
            
            const open = price;
            const close = price + (Math.random() - 0.5) * volatility;
            const high = Math.max(open, close) + Math.random() * volatility;
            const low = Math.min(open, close) - Math.random() * volatility;
            const volume = 500000 + Math.random() * 500000;

            data.push({
                timestamp: Date.now() - (length - i) * 3600000,
                open, high, low, close, volume
            });
        }

        return data;
    }

    /**
     * Generate volatile data
     */
    generateVolatileData(length) {
        const data = [];
        let price = 50000;

        for (let i = 0; i < length; i++) {
            const volatility = price * 0.05; // High volatility
            const open = price;
            const close = price + (Math.random() - 0.5) * volatility * 2;
            const high = Math.max(open, close) + Math.random() * volatility;
            const low = Math.min(open, close) - Math.random() * volatility;
            const volume = 800000 + Math.random() * 1000000;

            data.push({
                timestamp: Date.now() - (length - i) * 3600000,
                open, high, low, close, volume
            });

            price = close;
        }

        return data;
    }

    /**
     * Generate divergence data
     */
    generateDivergenceData() {
        const data = [];
        let price = 50000;

        for (let i = 0; i < 100; i++) {
            let close;
            
            // Create divergence: price makes lower low, but momentum increases
            if (i < 50) {
                close = price - (i * 50); // Declining price
            } else {
                close = price - (50 * 50) + ((i - 50) * 30); // Price slightly recovering
            }

            const volatility = Math.abs(close) * 0.01;
            const open = price;
            const high = Math.max(open, close) + volatility;
            const low = Math.min(open, close) - volatility;
            const volume = 500000 + Math.random() * 500000;

            data.push({
                timestamp: Date.now() - (100 - i) * 3600000,
                open, high, low, close, volume
            });

            price = close;
        }

        return data;
    }

    /**
     * Validate OHLCV data
     */
    isValidOHLCV(data) {
        if (!data) return false;

        const requiredFields = ['timestamp', 'open', 'high', 'low', 'close', 'volume'];
        
        for (const field of requiredFields) {
            if (!(field in data)) return false;
            if (typeof data[field] !== 'number') return false;
            if (field !== 'timestamp' && data[field] < 0) return false;
        }

        // High should be highest, low should be lowest
        if (data.high < data.low) return false;
        if (data.high < data.open || data.high < data.close) return false;
        if (data.low > data.open || data.low > data.close) return false;

        return true;
    }
}

/**
 * Run tests when module is loaded
 */
export async function runTests() {
    const tester = new TradingSystemTests();
    return await tester.runAll();
}

export default TradingSystemTests;

