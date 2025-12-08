/**
 * Adaptive Market Regime Detection System
 * Identifies market conditions and adapts strategies accordingly
 * Regimes: Trending, Ranging, Volatile, Calm, Bullish, Bearish
 */

/**
 * Market regimes
 */
export const MARKET_REGIMES = {
    TRENDING_BULLISH: 'trending-bullish',
    TRENDING_BEARISH: 'trending-bearish',
    RANGING: 'ranging',
    VOLATILE_BULLISH: 'volatile-bullish',
    VOLATILE_BEARISH: 'volatile-bearish',
    CALM: 'calm',
    BREAKDOWN: 'breakdown',
    BREAKOUT: 'breakout',
    ACCUMULATION: 'accumulation',
    DISTRIBUTION: 'distribution'
};

/**
 * Regime characteristics
 */
const REGIME_CHARACTERISTICS = {
    [MARKET_REGIMES.TRENDING_BULLISH]: {
        name: 'Trending Bullish',
        description: 'Strong upward trend with consistent higher highs and higher lows',
        bestStrategies: ['ict-market-structure', 'momentum-divergence-hunter', 'supply-demand-zones'],
        riskLevel: 'medium',
        profitPotential: 'high'
    },
    [MARKET_REGIMES.TRENDING_BEARISH]: {
        name: 'Trending Bearish',
        description: 'Strong downward trend with consistent lower highs and lower lows',
        bestStrategies: ['ict-market-structure', 'liquidity-sweep-reversal'],
        riskLevel: 'high',
        profitPotential: 'high'
    },
    [MARKET_REGIMES.RANGING]: {
        name: 'Ranging',
        description: 'Sideways movement between support and resistance',
        bestStrategies: ['supply-demand-zones', 'liquidity-sweep-reversal', 'mean-reversion-momentum'],
        riskLevel: 'low',
        profitPotential: 'medium'
    },
    [MARKET_REGIMES.VOLATILE_BULLISH]: {
        name: 'Volatile Bullish',
        description: 'Upward movement with high volatility and large swings',
        bestStrategies: ['volatility-breakout-pro', 'fair-value-gap-strategy'],
        riskLevel: 'very-high',
        profitPotential: 'very-high'
    },
    [MARKET_REGIMES.VOLATILE_BEARISH]: {
        name: 'Volatile Bearish',
        description: 'Downward movement with high volatility',
        bestStrategies: ['volatility-breakout-pro', 'liquidity-sweep-reversal'],
        riskLevel: 'very-high',
        profitPotential: 'very-high'
    },
    [MARKET_REGIMES.CALM]: {
        name: 'Calm',
        description: 'Low volatility with minimal price movement',
        bestStrategies: ['ranging', 'supply-demand-zones'],
        riskLevel: 'very-low',
        profitPotential: 'low'
    },
    [MARKET_REGIMES.BREAKOUT]: {
        name: 'Breakout',
        description: 'Price breaking above resistance',
        bestStrategies: ['volatility-breakout-pro', 'ict-market-structure', 'momentum-divergence-hunter'],
        riskLevel: 'high',
        profitPotential: 'very-high'
    },
    [MARKET_REGIMES.BREAKDOWN]: {
        name: 'Breakdown',
        description: 'Price breaking below support',
        bestStrategies: ['liquidity-sweep-reversal', 'ict-market-structure'],
        riskLevel: 'high',
        profitPotential: 'high'
    },
    [MARKET_REGIMES.ACCUMULATION]: {
        name: 'Accumulation',
        description: 'Smart money accumulating positions',
        bestStrategies: ['wyckoff-accumulation', 'supply-demand-zones', 'market-maker-profile'],
        riskLevel: 'medium',
        profitPotential: 'very-high'
    },
    [MARKET_REGIMES.DISTRIBUTION]: {
        name: 'Distribution',
        description: 'Smart money distributing positions',
        bestStrategies: ['wyckoff-accumulation', 'liquidity-sweep-reversal'],
        riskLevel: 'high',
        profitPotential: 'medium'
    }
};

/**
 * Adaptive Regime Detector
 */
export class AdaptiveRegimeDetector {
    constructor(config = {}) {
        this.lookbackPeriod = config.lookbackPeriod || 100;
        this.volatilityPeriod = config.volatilityPeriod || 20;
        this.trendPeriod = config.trendPeriod || 50;
        this.currentRegime = null;
        this.regimeHistory = [];
        this.confidence = 0;
    }

    /**
     * Detect current market regime
     * @param {Array<Object>} ohlcvData - OHLCV data
     * @returns {Object} Regime detection results
     */
    detectRegime(ohlcvData) {
        if (!ohlcvData || ohlcvData.length < this.lookbackPeriod) {
            return {
                regime: MARKET_REGIMES.CALM,
                confidence: 0,
                error: 'Insufficient data'
            };
        }

        const metrics = this.calculateMetrics(ohlcvData);
        const regime = this.classifyRegime(metrics);
        const confidence = this.calculateConfidence(metrics, regime);

        // Update history
        this.currentRegime = regime;
        this.confidence = confidence;
        this.regimeHistory.push({
            regime,
            confidence,
            timestamp: Date.now(),
            metrics
        });

        // Keep only recent history
        if (this.regimeHistory.length > 50) {
            this.regimeHistory.shift();
        }

        return {
            regime,
            confidence,
            characteristics: REGIME_CHARACTERISTICS[regime],
            metrics,
            transition: this.detectRegimeTransition(),
            timestamp: Date.now()
        };
    }

    /**
     * Calculate market metrics
     * @param {Array<Object>} ohlcvData - OHLCV data
     * @returns {Object} Metrics
     */
    calculateMetrics(ohlcvData) {
        const closes = ohlcvData.map(c => c.close);
        const highs = ohlcvData.map(c => c.high);
        const lows = ohlcvData.map(c => c.low);
        const volumes = ohlcvData.map(c => c.volume);

        return {
            volatility: this.calculateVolatility(closes),
            trend: this.calculateTrend(closes),
            trendStrength: this.calculateTrendStrength(highs, lows, closes),
            momentum: this.calculateMomentum(closes),
            volume: this.analyzeVolume(volumes),
            range: this.calculateRange(highs, lows, closes),
            structure: this.analyzeMarketStructure(highs, lows),
            phase: this.detectWyckoffPhase(ohlcvData)
        };
    }

    /**
     * Calculate volatility (ATR-based)
     * @param {Array<number>} closes - Close prices
     * @returns {number} Volatility percentage
     */
    calculateVolatility(closes) {
        const period = Math.min(this.volatilityPeriod, closes.length - 1);
        const returns = [];

        for (let i = 1; i <= period; i++) {
            const ret = (closes[closes.length - i] - closes[closes.length - i - 1]) / closes[closes.length - i - 1];
            returns.push(ret);
        }

        const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
        const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length;
        const stdDev = Math.sqrt(variance);

        return stdDev * 100; // Convert to percentage
    }

    /**
     * Calculate trend direction
     * @param {Array<number>} closes - Close prices
     * @returns {Object} Trend info
     */
    calculateTrend(closes) {
        const period = Math.min(this.trendPeriod, closes.length);
        const recentPrices = closes.slice(-period);

        // Linear regression
        const { slope, r2 } = this.linearRegression(recentPrices);

        let direction = 'neutral';
        if (slope > 0.001) direction = 'up';
        else if (slope < -0.001) direction = 'down';

        return {
            direction,
            slope,
            strength: r2 * 100 // R² as percentage
        };
    }

    /**
     * Linear regression
     * @param {Array<number>} values - Values
     * @returns {Object} Slope and R²
     */
    linearRegression(values) {
        const n = values.length;
        const indices = Array.from({ length: n }, (_, i) => i);

        const sumX = indices.reduce((a, b) => a + b, 0);
        const sumY = values.reduce((a, b) => a + b, 0);
        const sumXY = indices.reduce((sum, x, i) => sum + x * values[i], 0);
        const sumX2 = indices.reduce((sum, x) => sum + x * x, 0);
        const sumY2 = values.reduce((sum, y) => sum + y * y, 0);

        const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        const intercept = (sumY - slope * sumX) / n;

        // Calculate R²
        const meanY = sumY / n;
        const ssTotal = values.reduce((sum, y) => sum + Math.pow(y - meanY, 2), 0);
        const ssResidual = values.reduce((sum, y, i) => {
            const predicted = slope * i + intercept;
            return sum + Math.pow(y - predicted, 2);
        }, 0);

        const r2 = 1 - (ssResidual / ssTotal);

        return { slope, intercept, r2: Math.max(0, r2) };
    }

    /**
     * Calculate trend strength (ADX-like)
     * @param {Array<number>} highs - High prices
     * @param {Array<number>} lows - Low prices
     * @param {Array<number>} closes - Close prices
     * @returns {number} Trend strength (0-100)
     */
    calculateTrendStrength(highs, lows, closes) {
        const period = Math.min(14, closes.length - 1);
        let plusDM = 0;
        let minusDM = 0;

        for (let i = closes.length - period; i < closes.length; i++) {
            const highDiff = highs[i] - highs[i - 1];
            const lowDiff = lows[i - 1] - lows[i];

            if (highDiff > lowDiff && highDiff > 0) {
                plusDM += highDiff;
            } else if (lowDiff > highDiff && lowDiff > 0) {
                minusDM += lowDiff;
            }
        }

        const totalDM = plusDM + minusDM;
        if (totalDM === 0) return 0;

        const dx = Math.abs(plusDM - minusDM) / totalDM * 100;
        return Math.min(100, dx);
    }

    /**
     * Calculate momentum
     * @param {Array<number>} closes - Close prices
     * @returns {Object} Momentum info
     */
    calculateMomentum(closes) {
        const period = 10;
        const current = closes[closes.length - 1];
        const past = closes[closes.length - period];
        const momentum = ((current - past) / past) * 100;

        let state = 'neutral';
        if (momentum > 2) state = 'strong-positive';
        else if (momentum > 0.5) state = 'positive';
        else if (momentum < -2) state = 'strong-negative';
        else if (momentum < -0.5) state = 'negative';

        return { value: momentum, state };
    }

    /**
     * Analyze volume
     * @param {Array<number>} volumes - Volume data
     * @returns {Object} Volume analysis
     */
    analyzeVolume(volumes) {
        const period = 20;
        const recentVolumes = volumes.slice(-period);
        const avgVolume = recentVolumes.reduce((a, b) => a + b, 0) / recentVolumes.length;
        const currentVolume = volumes[volumes.length - 1];

        const ratio = currentVolume / avgVolume;

        let state = 'normal';
        if (ratio > 2) state = 'very-high';
        else if (ratio > 1.5) state = 'high';
        else if (ratio < 0.5) state = 'very-low';
        else if (ratio < 0.75) state = 'low';

        return {
            current: currentVolume,
            average: avgVolume,
            ratio,
            state
        };
    }

    /**
     * Calculate price range
     * @param {Array<number>} highs - High prices
     * @param {Array<number>} lows - Low prices
     * @param {Array<number>} closes - Close prices
     * @returns {Object} Range info
     */
    calculateRange(highs, lows, closes) {
        const period = 20;
        const recentHighs = highs.slice(-period);
        const recentLows = lows.slice(-period);
        
        const highestHigh = Math.max(...recentHighs);
        const lowestLow = Math.min(...recentLows);
        const currentPrice = closes[closes.length - 1];

        const rangeSize = highestHigh - lowestLow;
        const rangePercent = (rangeSize / currentPrice) * 100;
        const position = (currentPrice - lowestLow) / rangeSize;

        let state = 'ranging';
        if (rangePercent < 3) state = 'tight';
        else if (rangePercent > 10) state = 'wide';

        return {
            high: highestHigh,
            low: lowestLow,
            size: rangeSize,
            percent: rangePercent,
            position,
            state
        };
    }

    /**
     * Analyze market structure
     * @param {Array<number>} highs - High prices
     * @param {Array<number>} lows - Low prices
     * @returns {Object} Structure analysis
     */
    analyzeMarketStructure(highs, lows) {
        const swingPeriod = 5;
        const recentHighs = highs.slice(-20);
        const recentLows = lows.slice(-20);

        // Find swing points
        const swingHighIndices = [];
        const swingLowIndices = [];

        for (let i = swingPeriod; i < recentHighs.length - swingPeriod; i++) {
            let isSwingHigh = true;
            let isSwingLow = true;

            for (let j = i - swingPeriod; j <= i + swingPeriod; j++) {
                if (j !== i) {
                    if (recentHighs[j] >= recentHighs[i]) isSwingHigh = false;
                    if (recentLows[j] <= recentLows[i]) isSwingLow = false;
                }
            }

            if (isSwingHigh) swingHighIndices.push(i);
            if (isSwingLow) swingLowIndices.push(i);
        }

        // Analyze structure
        let structure = 'neutral';
        
        if (swingHighIndices.length >= 2 && swingLowIndices.length >= 2) {
            const lastTwoHighs = swingHighIndices.slice(-2).map(i => recentHighs[i]);
            const lastTwoLows = swingLowIndices.slice(-2).map(i => recentLows[i]);

            const higherHighs = lastTwoHighs[1] > lastTwoHighs[0];
            const higherLows = lastTwoLows[1] > lastTwoLows[0];
            const lowerHighs = lastTwoHighs[1] < lastTwoHighs[0];
            const lowerLows = lastTwoLows[1] < lastTwoLows[0];

            if (higherHighs && higherLows) structure = 'bullish';
            else if (lowerHighs && lowerLows) structure = 'bearish';
            else if (higherHighs && lowerLows) structure = 'distribution';
            else if (lowerHighs && higherLows) structure = 'accumulation';
        }

        return {
            structure,
            swingHighs: swingHighIndices.length,
            swingLows: swingLowIndices.length
        };
    }

    /**
     * Detect Wyckoff phase
     * @param {Array<Object>} ohlcvData - OHLCV data
     * @returns {string} Wyckoff phase
     */
    detectWyckoffPhase(ohlcvData) {
        const volumes = ohlcvData.map(c => c.volume);
        const closes = ohlcvData.map(c => c.close);
        const highs = ohlcvData.map(c => c.high);
        const lows = ohlcvData.map(c => c.low);

        const priceRange = Math.max(...highs.slice(-20)) - Math.min(...lows.slice(-20));
        const priceRangePercent = (priceRange / closes[closes.length - 1]) * 100;
        
        const avgVolume = volumes.slice(-20).reduce((a, b) => a + b, 0) / 20;
        const recentVolume = volumes.slice(-5).reduce((a, b) => a + b, 0) / 5;
        const volumeRatio = recentVolume / avgVolume;

        const priceChange = ((closes[closes.length - 1] - closes[closes.length - 20]) / closes[closes.length - 20]) * 100;

        // Accumulation: Low range + High volume + Flat price
        if (priceRangePercent < 5 && volumeRatio > 1.2 && Math.abs(priceChange) < 3) {
            return 'accumulation';
        }

        // Distribution: Low range + High volume + Flat/Declining price
        if (priceRangePercent < 5 && volumeRatio > 1.2 && priceChange < 0) {
            return 'distribution';
        }

        // Markup: Rising price + Increasing volume
        if (priceChange > 5 && volumeRatio > 1) {
            return 'markup';
        }

        // Markdown: Falling price + Increasing volume
        if (priceChange < -5 && volumeRatio > 1) {
            return 'markdown';
        }

        return 'neutral';
    }

    /**
     * Classify regime based on metrics
     * @param {Object} metrics - Market metrics
     * @returns {string} Market regime
     */
    classifyRegime(metrics) {
        const { volatility, trend, trendStrength, momentum, volume, range, structure, phase } = metrics;

        // Wyckoff phases take priority
        if (phase === 'accumulation') {
            return MARKET_REGIMES.ACCUMULATION;
        }
        if (phase === 'distribution') {
            return MARKET_REGIMES.DISTRIBUTION;
        }

        // Volatile regimes
        if (volatility > 5) {
            if (trend.direction === 'up' || momentum.state.includes('positive')) {
                return MARKET_REGIMES.VOLATILE_BULLISH;
            }
            if (trend.direction === 'down' || momentum.state.includes('negative')) {
                return MARKET_REGIMES.VOLATILE_BEARISH;
            }
        }

        // Breakout/Breakdown
        if (range.position > 0.95 && volume.state === 'high' && momentum.state.includes('positive')) {
            return MARKET_REGIMES.BREAKOUT;
        }
        if (range.position < 0.05 && volume.state === 'high' && momentum.state.includes('negative')) {
            return MARKET_REGIMES.BREAKDOWN;
        }

        // Trending regimes
        if (trendStrength > 40 && trend.strength > 60) {
            if (trend.direction === 'up' || structure.structure === 'bullish') {
                return MARKET_REGIMES.TRENDING_BULLISH;
            }
            if (trend.direction === 'down' || structure.structure === 'bearish') {
                return MARKET_REGIMES.TRENDING_BEARISH;
            }
        }

        // Ranging
        if (range.state === 'tight' || range.percent < 5) {
            if (volatility < 2) {
                return MARKET_REGIMES.CALM;
            }
            return MARKET_REGIMES.RANGING;
        }

        // Calm market
        if (volatility < 2 && trendStrength < 20) {
            return MARKET_REGIMES.CALM;
        }

        // Default to ranging
        return MARKET_REGIMES.RANGING;
    }

    /**
     * Calculate confidence in regime classification
     * @param {Object} metrics - Market metrics
     * @param {string} regime - Classified regime
     * @returns {number} Confidence (0-100)
     */
    calculateConfidence(metrics, regime) {
        let confidence = 50; // Base confidence

        const { volatility, trend, trendStrength, volume, range } = metrics;

        // Adjust based on trend strength
        confidence += trendStrength * 0.3;

        // Adjust based on trend R²
        confidence += trend.strength * 0.2;

        // Adjust based on volume confirmation
        if (volume.state === 'high' || volume.state === 'very-high') {
            confidence += 10;
        }

        // Adjust based on range clarity
        if (range.state === 'tight') {
            confidence += 5;
        }

        // Regime-specific adjustments
        switch (regime) {
            case MARKET_REGIMES.TRENDING_BULLISH:
            case MARKET_REGIMES.TRENDING_BEARISH:
                if (trendStrength > 60) confidence += 15;
                break;
            case MARKET_REGIMES.RANGING:
            case MARKET_REGIMES.CALM:
                if (volatility < 2) confidence += 10;
                break;
            case MARKET_REGIMES.BREAKOUT:
            case MARKET_REGIMES.BREAKDOWN:
                if (volume.state === 'very-high') confidence += 20;
                break;
        }

        return Math.min(100, Math.max(0, confidence));
    }

    /**
     * Detect regime transitions
     * @returns {Object|null} Transition info
     */
    detectRegimeTransition() {
        if (this.regimeHistory.length < 2) {
            return null;
        }

        const current = this.regimeHistory[this.regimeHistory.length - 1];
        const previous = this.regimeHistory[this.regimeHistory.length - 2];

        if (current.regime !== previous.regime) {
            return {
                from: previous.regime,
                to: current.regime,
                timestamp: current.timestamp,
                significance: this.calculateTransitionSignificance(previous.regime, current.regime)
            };
        }

        return null;
    }

    /**
     * Calculate significance of regime transition
     * @param {string} from - Previous regime
     * @param {string} to - Current regime
     * @returns {string} Significance level
     */
    calculateTransitionSignificance(from, to) {
        const highImpact = [
            [MARKET_REGIMES.ACCUMULATION, MARKET_REGIMES.BREAKOUT],
            [MARKET_REGIMES.DISTRIBUTION, MARKET_REGIMES.BREAKDOWN],
            [MARKET_REGIMES.RANGING, MARKET_REGIMES.TRENDING_BULLISH],
            [MARKET_REGIMES.RANGING, MARKET_REGIMES.TRENDING_BEARISH]
        ];

        for (const [fromRegime, toRegime] of highImpact) {
            if (from === fromRegime && to === toRegime) {
                return 'high';
            }
        }

        return 'medium';
    }

    /**
     * Get recommended strategies for current regime
     * @returns {Array<string>} Recommended strategies
     */
    getRecommendedStrategies() {
        if (!this.currentRegime) {
            return ['ict-market-structure'];
        }

        return REGIME_CHARACTERISTICS[this.currentRegime]?.bestStrategies || ['ict-market-structure'];
    }

    /**
     * Get regime history
     * @param {number} limit - Number of items
     * @returns {Array<Object>} Regime history
     */
    getHistory(limit = 20) {
        return this.regimeHistory.slice(-limit);
    }
}

export default AdaptiveRegimeDetector;

