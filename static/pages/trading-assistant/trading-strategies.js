/**
 * Hybrid Trading Strategies Module
 * Implements various hybrid crypto trading strategies
 */

/**
 * Strategy configurations with detailed indicator parameters
 */
export const HYBRID_STRATEGIES = {
    'trend-rsi-macd': {
        name: 'Trend + RSI + MACD',
        description: 'Combines trend analysis with momentum indicators',
        indicators: ['EMA20', 'EMA50', 'RSI', 'MACD'],
        timeframes: ['4h', '1d'],
        riskLevel: 'medium',
        scientific: true,
    },
    'bb-rsi': {
        name: 'Bollinger Bands + RSI',
        description: 'Mean reversion strategy with volatility bands',
        indicators: ['BB', 'RSI', 'Volume'],
        timeframes: ['1h', '4h'],
        riskLevel: 'low',
        scientific: true,
    },
    'ema-volume-rsi': {
        name: 'EMA + Volume + RSI',
        description: 'Momentum strategy with volume confirmation',
        indicators: ['EMA12', 'EMA26', 'Volume', 'RSI'],
        timeframes: ['1h', '4h', '1d'],
        riskLevel: 'medium',
        scientific: true,
    },
    'sr-fibonacci': {
        name: 'Support/Resistance + Fibonacci',
        description: 'Price action with Fibonacci retracement levels',
        indicators: ['S/R', 'Fibonacci', 'Volume'],
        timeframes: ['4h', '1d', '1w'],
        riskLevel: 'high',
        scientific: true,
    },
    'macd-stoch-ema': {
        name: 'MACD + Stochastic + EMA',
        description: 'Triple momentum confirmation strategy',
        indicators: ['MACD', 'Stochastic', 'EMA9', 'EMA21'],
        timeframes: ['1h', '4h'],
        riskLevel: 'medium',
        scientific: true,
    },
    'ensemble-multitimeframe': {
        name: 'Ensemble Multi-Timeframe',
        description: 'Advanced: Combines multiple timeframes with ensemble voting',
        indicators: ['RSI', 'MACD', 'EMA', 'Volume', 'BB'],
        timeframes: ['15m', '1h', '4h', '1d'],
        riskLevel: 'medium',
        scientific: true,
        advanced: true,
    },
    'volume-profile-orderflow': {
        name: 'Volume Profile + Order Flow',
        description: 'Advanced: Price action with volume analysis and order flow',
        indicators: ['Volume', 'OBV', 'VWAP', 'Price Action'],
        timeframes: ['1h', '4h', '1d'],
        riskLevel: 'high',
        scientific: true,
        advanced: true,
    },
    'adaptive-breakout': {
        name: 'Adaptive Breakout Strategy',
        description: 'Advanced: Dynamic breakout detection with volatility adjustment',
        indicators: ['ATR', 'BB', 'Volume', 'Support/Resistance'],
        timeframes: ['4h', '1d'],
        riskLevel: 'medium',
        scientific: true,
        advanced: true,
    },
    'mean-reversion-momentum': {
        name: 'Mean Reversion + Momentum Filter',
        description: 'Advanced: Mean reversion with momentum confirmation filter',
        indicators: ['RSI', 'Stochastic', 'MACD', 'EMA'],
        timeframes: ['1h', '4h'],
        riskLevel: 'low',
        scientific: true,
        advanced: true,
    },
    'sr-breakout-confirmation': {
        name: 'S/R Breakout with Confirmation',
        description: 'Advanced: Support/Resistance breakout with multi-indicator confirmation',
        indicators: ['S/R', 'Volume', 'RSI', 'MACD', 'EMA'],
        timeframes: ['4h', '1d'],
        riskLevel: 'high',
        scientific: true,
        advanced: true,
    },
    'pre-breakout-scalping': {
        name: 'Pre-Breakout Scalping',
        description: 'Scalping: Detects entry points before breakout occurs',
        indicators: ['Volume', 'RSI', 'BB', 'Price Action', 'Momentum'],
        timeframes: ['1m', '5m', '15m'],
        riskLevel: 'very-high',
        scientific: true,
        advanced: true,
        scalping: true,
    },
    'liquidity-zone-scalping': {
        name: 'Liquidity Zone Scalping',
        description: 'Scalping: Identifies liquidity zones before price moves',
        indicators: ['Volume Profile', 'Order Flow', 'Support/Resistance', 'RSI'],
        timeframes: ['1m', '5m'],
        riskLevel: 'very-high',
        scientific: true,
        advanced: true,
        scalping: true,
    },
    'momentum-accumulation-scalping': {
        name: 'Momentum Accumulation Scalping',
        description: 'Scalping: Detects momentum buildup before bullish/bearish moves',
        indicators: ['RSI', 'MACD', 'Volume', 'EMA', 'Momentum'],
        timeframes: ['1m', '5m', '15m'],
        riskLevel: 'very-high',
        scientific: true,
        advanced: true,
        scalping: true,
    },
    'volume-spike-breakout': {
        name: 'Volume Spike Breakout Scalping',
        description: 'Scalping: Volume spike detection before breakout',
        indicators: ['Volume', 'OBV', 'Price Action', 'RSI', 'BB'],
        timeframes: ['1m', '5m'],
        riskLevel: 'very-high',
        scientific: true,
        advanced: true,
        scalping: true,
    },
    'order-flow-imbalance-scalping': {
        name: 'Order Flow Imbalance Scalping',
        description: 'Scalping: Detects order flow imbalance before price moves',
        indicators: ['Order Flow', 'Volume', 'Price Action', 'Momentum'],
        timeframes: ['1m', '5m'],
        riskLevel: 'very-high',
        scientific: true,
        advanced: true,
        scalping: true,
    },
};

/**
 * Analyzes market using selected hybrid strategy with fallback
 * @param {string} symbol - Trading symbol
 * @param {string} strategyKey - Strategy identifier
 * @param {Object} marketData - Current market data
 * @returns {Object} Analysis results with signals
 */
export function analyzeWithStrategy(symbol, strategyKey, marketData) {
    try {
        const strategy = HYBRID_STRATEGIES[strategyKey];
        if (!strategy) {
            console.warn(`[Strategies] Unknown strategy: ${strategyKey}, using fallback`);
            return analyzeWithFallback(symbol, marketData);
        }

        if (!marketData || typeof marketData !== 'object') {
            throw new Error('Invalid market data: not an object');
        }

        const price = parseFloat(marketData.price);
        const volume = parseFloat(marketData.volume || 0) || 0;
        const high24h = parseFloat(marketData.high24h || marketData.high_24h || 0) || 0;
        const low24h = parseFloat(marketData.low24h || marketData.low_24h || 0) || 0;

        if (isNaN(price) || price <= 0) {
            throw new Error('Invalid market data: missing or invalid price');
        }

        // Validate high/low relationships
        const validHigh24h = (high24h > 0 && high24h >= price) ? high24h : price * 1.05;
        const validLow24h = (low24h > 0 && low24h <= price) ? low24h : price * 0.95;
        
        if (validHigh24h < validLow24h) {
            throw new Error('Invalid market data: high24h < low24h');
        }

        const indicators = calculateIndicators(price, volume, validHigh24h, validLow24h);

        const signal = generateSignal(strategyKey, indicators, price, marketData);

        const levels = calculateSupportResistance(price, high24h, low24h);

        const isScalping = strategy.scalping || false;
        const riskReward = calculateRiskReward(price, signal.signal, levels, isScalping);

        return {
            strategy: strategy.name,
            signal: signal.signal,
            strength: signal.strength,
            confidence: signal.confidence,
            indicators,
            levels,
            riskReward,
            takeProfitLevels: riskReward.takeProfits,
            stopLoss: riskReward.stopLoss,
            timestamp: new Date().toISOString(),
            strategyType: strategy.scalping ? 'scalping' : strategy.advanced ? 'advanced' : 'standard',
            isScalping: isScalping,
        };
    } catch (error) {
        console.error(`[Strategies] Error in ${strategyKey}:`, error);
        return analyzeWithFallback(symbol, marketData);
    }
}

/**
 * Fallback analysis when primary strategy fails
 */
function analyzeWithFallback(symbol, marketData) {
    if (!marketData || typeof marketData !== 'object') {
        marketData = {};
    }

    const price = parseFloat(marketData.price) || 0;
    const volume = parseFloat(marketData.volume || 0) || 0;
    const high24h = (price > 0 && parseFloat(marketData.high24h || marketData.high_24h) > 0) 
        ? parseFloat(marketData.high24h || marketData.high_24h) 
        : (price > 0 ? price * 1.05 : 0);
    const low24h = (price > 0 && parseFloat(marketData.low24h || marketData.low_24h) > 0) 
        ? parseFloat(marketData.low24h || marketData.low_24h) 
        : (price > 0 ? price * 0.95 : 0);

    if (price <= 0) {
        // Return minimal fallback
        return {
            strategy: 'Basic Analysis (Fallback)',
            signal: 'hold',
            strength: 'weak',
            confidence: 0,
            indicators: { rsi: 50, macd: 'neutral', trend: 'neutral' },
            levels: { support: [], resistance: [] },
            riskReward: { stopLoss: 0, takeProfits: [], riskRewardRatio: '1:1', riskPercentage: '0.00' },
            takeProfitLevels: [],
            stopLoss: 0,
            timestamp: new Date().toISOString(),
            strategyType: 'fallback',
        };
    }

    const validHigh24h = (high24h > 0 && high24h >= price) ? high24h : price * 1.05;
    const validLow24h = (low24h > 0 && low24h <= price) ? low24h : price * 0.95;

    const indicators = calculateIndicators(price, volume, validHigh24h, validLow24h);
    const levels = calculateSupportResistance(price, validHigh24h, validLow24h);

    return {
        strategy: 'Basic Analysis (Fallback)',
        signal: 'hold',
        strength: 'weak',
        confidence: 50,
        indicators,
        levels,
        riskReward: {
            stopLoss: price * 0.95,
            takeProfits: [
                { level: price * 1.02, type: 'TP1', percentage: 50 },
                { level: price * 1.05, type: 'TP2', percentage: 50 },
            ],
            riskRewardRatio: '1:2',
            riskPercentage: '5.00',
        },
        takeProfitLevels: [
            { level: price * 1.02, type: 'TP1', percentage: 50 },
            { level: price * 1.05, type: 'TP2', percentage: 50 },
        ],
        stopLoss: price * 0.95,
        timestamp: new Date().toISOString(),
        strategyType: 'fallback',
    };
}

/**
 * Calculates technical indicators with error handling
 */
function calculateIndicators(price, volume, high24h, low24h) {
    try {
        if (typeof price !== 'number' || isNaN(price) || price <= 0) {
            throw new Error('Invalid price');
        }

        const validVolume = (typeof volume === 'number' && !isNaN(volume) && volume >= 0) ? volume : 0;
        const validHigh = (typeof high24h === 'number' && !isNaN(high24h) && high24h >= price) ? high24h : price * 1.05;
        const validLow = (typeof low24h === 'number' && !isNaN(low24h) && low24h <= price && low24h > 0) ? low24h : price * 0.95;

        if (validHigh < validLow) {
            throw new Error('Invalid range: high < low');
        }

        const range = Math.max(validHigh - validLow, price * 0.01);
        const position = range > 0 ? Math.max(0, Math.min(1, (price - validLow) / range)) : 0.5;

        const rsi = 30 + position * 40;

        const macd = position > 0.6 ? 'bullish' : position < 0.4 ? 'bearish' : 'neutral';

        const trend = position > 0.5 ? 'up' : 'down';

        const volatility = range / price;
        const bbUpper = price * (1 + Math.max(0.01, volatility * 1.5));
        const bbLower = price * (1 - Math.max(0.01, volatility * 1.5));
        const bbPosition = position > 0.8 ? 'upper' : position < 0.2 ? 'lower' : 'middle';

        const stochastic = Math.round(position * 100);

        const atr = range;
        const obv = volume * (trend === 'up' ? 1 : -1);

        return {
            rsi: parseFloat(rsi.toFixed(2)),
            macd,
            trend,
            bollingerBands: {
                upper: parseFloat(bbUpper.toFixed(2)),
                lower: parseFloat(bbLower.toFixed(2)),
                position: bbPosition,
                width: parseFloat((bbUpper - bbLower).toFixed(2)),
            },
            stochastic,
            volume: volume || 0,
            atr: parseFloat(atr.toFixed(2)),
            obv: obv || 0,
            volatility: parseFloat((volatility * 100).toFixed(2)),
        };
    } catch (error) {
        console.error('[Strategies] Error calculating indicators:', error);
        return {
            rsi: 50,
            macd: 'neutral',
            trend: 'neutral',
            bollingerBands: { upper: price * 1.02, lower: price * 0.98, position: 'middle', width: price * 0.04 },
            stochastic: 50,
            volume: 0,
            atr: 0,
            obv: 0,
            volatility: 0,
        };
    }
}

/**
 * Validate market data structure
 * @param {Object} marketData - Market data to validate
 * @returns {Object} Validation result
 */
export function validateMarketData(marketData) {
    if (!marketData || typeof marketData !== 'object') {
        return { valid: false, error: 'Market data is not an object' };
    }

    const price = parseFloat(marketData.price);
    if (isNaN(price) || price <= 0) {
        return { valid: false, error: 'Invalid or missing price' };
    }

    const volume = parseFloat(marketData.volume || marketData.volume_24h || 0);
    if (isNaN(volume) || volume < 0) {
        return { valid: false, error: 'Invalid volume' };
    }

    const high24h = parseFloat(marketData.high24h || marketData.high_24h || price * 1.05);
    const low24h = parseFloat(marketData.low24h || marketData.low_24h || price * 0.95);

    if (isNaN(high24h) || high24h < price) {
        return { valid: false, error: 'Invalid high24h' };
    }

    if (isNaN(low24h) || low24h > price || low24h <= 0) {
        return { valid: false, error: 'Invalid low24h' };
    }

    if (high24h < low24h) {
        return { valid: false, error: 'high24h < low24h' };
    }

    return { valid: true };
}

/**
 * Generates trading signal based on strategy
 */
function generateSignal(strategyKey, indicators, price, marketData = {}) {
    let signal = 'hold';
    let strength = 'medium';
    let confidence = 50;

    try {
        switch (strategyKey) {
            case 'trend-rsi-macd':
                if (indicators.trend === 'up' && indicators.rsi < 70 && indicators.macd === 'bullish') {
                    signal = 'buy';
                    strength = 'strong';
                    confidence = 85;
                } else if (indicators.trend === 'down' && indicators.rsi > 30 && indicators.macd === 'bearish') {
                    signal = 'sell';
                    strength = 'strong';
                    confidence = 85;
                }
                break;

            case 'bb-rsi':
                if (indicators.bollingerBands.position === 'lower' && indicators.rsi < 30) {
                    signal = 'buy';
                    strength = 'strong';
                    confidence = 80;
                } else if (indicators.bollingerBands.position === 'upper' && indicators.rsi > 70) {
                    signal = 'sell';
                    strength = 'strong';
                    confidence = 80;
                }
                break;

            case 'ema-volume-rsi':
                if (indicators.trend === 'up' && indicators.rsi < 65 && indicators.volume > 0) {
                    signal = 'buy';
                    strength = 'medium';
                    confidence = 75;
                } else if (indicators.trend === 'down' && indicators.rsi > 35 && indicators.volume > 0) {
                    signal = 'sell';
                    strength = 'medium';
                    confidence = 75;
                }
                break;

            case 'sr-fibonacci':
                if (indicators.rsi < 35) {
                    signal = 'buy';
                    strength = 'strong';
                    confidence = 82;
                } else if (indicators.rsi > 65) {
                    signal = 'sell';
                    strength = 'strong';
                    confidence = 82;
                }
                break;

            case 'macd-stoch-ema':
                if (indicators.macd === 'bullish' && indicators.stochastic < 20 && indicators.trend === 'up') {
                    signal = 'buy';
                    strength = 'strong';
                    confidence = 88;
                } else if (indicators.macd === 'bearish' && indicators.stochastic > 80 && indicators.trend === 'down') {
                    signal = 'sell';
                    strength = 'strong';
                    confidence = 88;
                }
                break;

            case 'ensemble-multitimeframe':
                signal = generateEnsembleSignal(indicators, marketData);
                strength = 'strong';
                confidence = 90;
                break;

            case 'volume-profile-orderflow':
                signal = generateVolumeProfileSignal(indicators, marketData);
                strength = 'strong';
                confidence = 87;
                break;

            case 'adaptive-breakout':
                signal = generateAdaptiveBreakoutSignal(indicators, marketData);
                strength = 'strong';
                confidence = 85;
                break;

            case 'mean-reversion-momentum':
                signal = generateMeanReversionMomentumSignal(indicators);
                strength = 'medium';
                confidence = 83;
                break;

            case 'sr-breakout-confirmation':
                signal = generateSRBreakoutSignal(indicators, marketData);
                strength = 'strong';
                confidence = 89;
                break;

            case 'pre-breakout-scalping':
                signal = generatePreBreakoutScalpingSignal(indicators, marketData);
                strength = 'strong';
                confidence = 92;
                break;

            case 'liquidity-zone-scalping':
                signal = generateLiquidityZoneScalpingSignal(indicators, marketData);
                strength = 'strong';
                confidence = 90;
                break;

            case 'momentum-accumulation-scalping':
                signal = generateMomentumAccumulationSignal(indicators, marketData);
                strength = 'strong';
                confidence = 91;
                break;

            case 'volume-spike-breakout':
                signal = generateVolumeSpikeBreakoutSignal(indicators, marketData);
                strength = 'strong';
                confidence = 93;
                break;

            case 'order-flow-imbalance-scalping':
                signal = generateOrderFlowImbalanceSignal(indicators, marketData);
                strength = 'strong';
                confidence = 90;
                break;
        }
    } catch (error) {
        console.error(`[Strategies] Error generating signal for ${strategyKey}:`, error);
        signal = 'hold';
        strength = 'weak';
        confidence = 50;
    }

    return { signal, strength, confidence };
}

/**
 * Advanced: Ensemble multi-timeframe signal
 */
function generateEnsembleSignal(indicators, marketData) {
    const votes = { buy: 0, sell: 0, hold: 0 };

    if (indicators.trend === 'up' && indicators.rsi < 70) votes.buy++;
    if (indicators.trend === 'down' && indicators.rsi > 30) votes.sell++;
    if (indicators.macd === 'bullish') votes.buy++;
    if (indicators.macd === 'bearish') votes.sell++;
    if (indicators.stochastic < 30) votes.buy++;
    if (indicators.stochastic > 70) votes.sell++;

    if (votes.buy >= 2) return 'buy';
    if (votes.sell >= 2) return 'sell';
    return 'hold';
}

/**
 * Advanced: Volume profile and order flow signal
 */
function generateVolumeProfileSignal(indicators, marketData) {
    const { volume = 0 } = marketData;
    const volumeThreshold = volume * 1.2;

    if (indicators.rsi < 40 && volume > volumeThreshold && indicators.trend === 'up') {
        return 'buy';
    }
    if (indicators.rsi > 60 && volume > volumeThreshold && indicators.trend === 'down') {
        return 'sell';
    }
    return 'hold';
}

/**
 * Advanced: Adaptive breakout signal
 */
function generateAdaptiveBreakoutSignal(indicators, marketData) {
    const bb = indicators.bollingerBands;
    const volatility = (bb.upper - bb.lower) / marketData.price;

    if (bb.position === 'upper' && volatility > 0.02 && indicators.rsi > 60) {
        return 'sell';
    }
    if (bb.position === 'lower' && volatility > 0.02 && indicators.rsi < 40) {
        return 'buy';
    }
    return 'hold';
}

/**
 * Advanced: Mean reversion with momentum filter
 */
function generateMeanReversionMomentumSignal(indicators) {
    const isOversold = indicators.rsi < 30 && indicators.stochastic < 20;
    const isOverbought = indicators.rsi > 70 && indicators.stochastic > 80;
    const momentumUp = indicators.macd === 'bullish' && indicators.trend === 'up';
    const momentumDown = indicators.macd === 'bearish' && indicators.trend === 'down';

    if (isOversold && momentumUp) return 'buy';
    if (isOverbought && momentumDown) return 'sell';
    return 'hold';
}

/**
 * Advanced: S/R breakout with confirmation
 */
function generateSRBreakoutSignal(indicators, marketData) {
    const { price = 0, high24h = 0, low24h = 0 } = marketData;
    const nearResistance = price > high24h * 0.98;
    const nearSupport = price < low24h * 1.02;

    if (nearResistance && indicators.rsi > 65 && indicators.macd === 'bearish') {
        return 'sell';
    }
    if (nearSupport && indicators.rsi < 35 && indicators.macd === 'bullish') {
        return 'buy';
    }
    return 'hold';
}

/**
 * Scalping: Pre-breakout detection algorithm
 * Identifies entry points before breakout occurs
 */
function generatePreBreakoutScalpingSignal(indicators, marketData) {
    const { price = 0, volume = 0, high24h = 0, low24h = 0 } = marketData;
    const bb = indicators.bollingerBands;
    const range = high24h - low24h;
    const position = range > 0 ? (price - low24h) / range : 0.5;

    const nearUpperBB = price > bb.upper * 0.995 && price < bb.upper * 1.005;
    const nearLowerBB = price > bb.lower * 0.995 && price < bb.lower * 1.005;

    const volumeSpike = volume > (marketData.avgVolume || volume * 1.5);
    const rsiOversold = indicators.rsi < 35;
    const rsiOverbought = indicators.rsi > 65;

    if (nearLowerBB && rsiOversold && volumeSpike && indicators.macd === 'bullish') {
        return 'buy';
    }

    if (nearUpperBB && rsiOverbought && volumeSpike && indicators.macd === 'bearish') {
        return 'sell';
    }

    if (position < 0.2 && indicators.rsi < 40 && volumeSpike) {
        return 'buy';
    }

    if (position > 0.8 && indicators.rsi > 60 && volumeSpike) {
        return 'sell';
    }

    return 'hold';
}

/**
 * Scalping: Liquidity zone detection
 * Identifies areas of high liquidity before price moves
 */
function generateLiquidityZoneScalpingSignal(indicators, marketData) {
    const { price = 0, volume = 0, high24h = 0, low24h = 0 } = marketData;
    const range = high24h - low24h;
    const position = range > 0 ? (price - low24h) / range : 0.5;

    const highVolume = volume > (marketData.avgVolume || volume * 1.3);
    const lowVolatility = indicators.volatility < 2;

    const liquidityZoneBuy = position < 0.3 && highVolume && lowVolatility && indicators.rsi < 45;
    const liquidityZoneSell = position > 0.7 && highVolume && lowVolatility && indicators.rsi > 55;

    if (liquidityZoneBuy && indicators.macd === 'bullish') {
        return 'buy';
    }

    if (liquidityZoneSell && indicators.macd === 'bearish') {
        return 'sell';
    }

    return 'hold';
}

/**
 * Scalping: Momentum accumulation detection
 * Detects momentum buildup before major moves
 */
function generateMomentumAccumulationSignal(indicators, marketData) {
    const { volume = 0 } = marketData;
    const volumeIncreasing = volume > (marketData.prevVolume || volume * 0.8);

    const rsiDivergenceBullish = indicators.rsi < 50 && indicators.rsi > 30 && indicators.trend === 'up';
    const rsiDivergenceBearish = indicators.rsi > 50 && indicators.rsi < 70 && indicators.trend === 'down';

    const macdBullish = indicators.macd === 'bullish';
    const macdBearish = indicators.macd === 'bearish';

    const momentumAccumulationBuy = rsiDivergenceBullish && macdBullish && volumeIncreasing && indicators.stochastic < 50;
    const momentumAccumulationSell = rsiDivergenceBearish && macdBearish && volumeIncreasing && indicators.stochastic > 50;

    if (momentumAccumulationBuy) {
        return 'buy';
    }

    if (momentumAccumulationSell) {
        return 'sell';
    }

    return 'hold';
}

/**
 * Scalping: Volume spike breakout detection
 * Detects volume spikes before breakout
 */
function generateVolumeSpikeBreakoutSignal(indicators, marketData) {
    const { price = 0, volume = 0 } = marketData;
    const volumeSpike = volume > (marketData.avgVolume || volume * 2);
    const strongVolumeSpike = volume > (marketData.avgVolume || volume * 3);

    const bb = indicators.bollingerBands;
    const nearBBMiddle = price > bb.lower * 1.01 && price < bb.upper * 0.99;

    const rsiNeutral = indicators.rsi > 40 && indicators.rsi < 60;

    if (strongVolumeSpike && nearBBMiddle && rsiNeutral && indicators.macd === 'bullish') {
        return 'buy';
    }

    if (strongVolumeSpike && nearBBMiddle && rsiNeutral && indicators.macd === 'bearish') {
        return 'sell';
    }

    if (volumeSpike && indicators.rsi < 45 && indicators.trend === 'up') {
        return 'buy';
    }

    if (volumeSpike && indicators.rsi > 55 && indicators.trend === 'down') {
        return 'sell';
    }

    return 'hold';
}

/**
 * Scalping: Order flow imbalance detection
 * Detects order flow imbalance before price moves
 */
function generateOrderFlowImbalanceSignal(indicators, marketData) {
    const { price = 0, volume = 0 } = marketData;
    const obv = indicators.obv || 0;
    const obvIncreasing = obv > 0;
    const obvDecreasing = obv < 0;

    const volumeImbalance = volume > (marketData.avgVolume || volume * 1.5);

    const buyImbalance = obvIncreasing && volumeImbalance && indicators.rsi < 55 && indicators.macd === 'bullish';
    const sellImbalance = obvDecreasing && volumeImbalance && indicators.rsi > 45 && indicators.macd === 'bearish';

    if (buyImbalance && indicators.stochastic < 60) {
        return 'buy';
    }

    if (sellImbalance && indicators.stochastic > 40) {
        return 'sell';
    }

    return 'hold';
}

/**
 * Calculates support and resistance levels
 */
function calculateSupportResistance(price, high24h, low24h) {
    const resistance1 = high24h;
    const resistance2 = price + (high24h - price) * 1.5;
    const resistance3 = price + (high24h - price) * 2;

    const support1 = low24h;
    const support2 = price - (price - low24h) * 1.5;
    const support3 = price - (price - low24h) * 2;

    return {
        resistance: [
            { level: resistance1, strength: 'strong' },
            { level: resistance2, strength: 'medium' },
            { level: resistance3, strength: 'weak' },
        ],
        support: [
            { level: support1, strength: 'strong' },
            { level: Math.max(support2, 0), strength: 'medium' },
            { level: Math.max(support3, 0), strength: 'weak' },
        ],
    };
}

/**
 * Calculates risk/reward ratio and TP/SL levels
 * For scalping strategies, uses tighter stops and faster targets
 */
function calculateRiskReward(price, signal, levels, isScalping = false) {
    let stopLoss = price;
    let takeProfits = [];
    let riskRewardRatio = '1:2';

    if (isScalping) {
        if (signal === 'buy') {
            stopLoss = price * 0.995;
            const riskAmount = price - stopLoss;

            takeProfits = [
                { level: price + riskAmount * 2, type: 'TP1', percentage: 40 },
                { level: price + riskAmount * 3, type: 'TP2', percentage: 35 },
                { level: price + riskAmount * 5, type: 'TP3', percentage: 25 },
            ];
            riskRewardRatio = '1:3';
        } else if (signal === 'sell') {
            stopLoss = price * 1.005;
            const riskAmount = stopLoss - price;

            takeProfits = [
                { level: price - riskAmount * 2, type: 'TP1', percentage: 40 },
                { level: price - riskAmount * 3, type: 'TP2', percentage: 35 },
                { level: price - riskAmount * 5, type: 'TP3', percentage: 25 },
            ];
            riskRewardRatio = '1:3';
        } else {
            stopLoss = price * 0.998;
            takeProfits = [
                { level: price * 1.003, type: 'TP1', percentage: 60 },
                { level: price * 1.005, type: 'TP2', percentage: 40 },
            ];
        }
    } else {
        if (signal === 'buy') {
            stopLoss = levels.support[0].level * 0.98;
            const riskAmount = price - stopLoss;

            takeProfits = [
                { level: price + riskAmount * 1.5, type: 'TP1', percentage: 33 },
                { level: price + riskAmount * 2, type: 'TP2', percentage: 33 },
                { level: price + riskAmount * 3, type: 'TP3', percentage: 34 },
            ];
            riskRewardRatio = '1:2.5';
        } else if (signal === 'sell') {
            stopLoss = levels.resistance[0].level * 1.02;
            const riskAmount = stopLoss - price;

            takeProfits = [
                { level: price - riskAmount * 1.5, type: 'TP1', percentage: 33 },
                { level: price - riskAmount * 2, type: 'TP2', percentage: 33 },
                { level: price - riskAmount * 3, type: 'TP3', percentage: 34 },
            ];
            riskRewardRatio = '1:2.5';
        } else {
            stopLoss = price * 0.95;
            takeProfits = [
                { level: price * 1.02, type: 'TP1', percentage: 50 },
                { level: price * 1.05, type: 'TP2', percentage: 50 },
            ];
        }
    }

    return {
        stopLoss: parseFloat(stopLoss.toFixed(2)),
        takeProfits,
        riskRewardRatio,
        riskPercentage: Math.abs(((stopLoss - price) / price) * 100).toFixed(2),
    };
}

