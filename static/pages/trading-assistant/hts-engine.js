/**
 * Hybrid Trading System (HTS) Engine
 * Core Algorithm: RSI+MACD (40% weight) + SMC (25%) + Patterns (20%) + Sentiment (10%) + ML (5%)
 * 
 * CRITICAL: RSI+MACD weight is IMMUTABLE at 40%
 */

class HTSEngine {
    constructor() {
        // Base weights (will be adjusted dynamically)
        this.baseWeights = {
            rsiMacd: 0.40,      // Core algorithm - minimum 30%, maximum 50%
            smc: 0.25,          // Smart Money Concepts
            patterns: 0.20,     // Pattern Recognition
            sentiment: 0.10,    // Sentiment Analysis
            ml: 0.05            // Machine Learning
        };

        this.weights = { ...this.baseWeights };

        this.rsiPeriod = 14;
        this.macdFast = 12;
        this.macdSlow = 26;
        this.macdSignal = 9;
        this.atrPeriod = 14;

        this.priceHistory = [];
        this.indicators = {};
        this.smcLevels = {
            orderBlocks: [],
            liquidityZones: [],
            breakerBlocks: []
        };
        this.patterns = [];
        this.sentimentScore = 0;
        this.mlScore = 0;
        this.marketRegime = 'neutral'; // trending, ranging, volatile, neutral
        this.volatility = 0;
    }

    /**
     * Calculate RSI (Relative Strength Index)
     */
    calculateRSI(prices, period = 14) {
        if (prices.length < period + 1) return null;

        const gains = [];
        const losses = [];

        for (let i = 1; i < prices.length; i++) {
            const change = prices[i] - prices[i - 1];
            gains.push(change > 0 ? change : 0);
            losses.push(change < 0 ? Math.abs(change) : 0);
        }

        const avgGain = gains.slice(-period).reduce((a, b) => a + b, 0) / period;
        const avgLoss = losses.slice(-period).reduce((a, b) => a + b, 0) / period;

        if (avgLoss === 0) return 100;

        const rs = avgGain / avgLoss;
        const rsi = 100 - (100 / (1 + rs));

        return rsi;
    }

    /**
     * Calculate EMA (Exponential Moving Average)
     */
    calculateEMA(prices, period) {
        if (prices.length < period) return null;

        const multiplier = 2 / (period + 1);
        let ema = prices.slice(0, period).reduce((a, b) => a + b, 0) / period;

        for (let i = period; i < prices.length; i++) {
            ema = (prices[i] - ema) * multiplier + ema;
        }

        return ema;
    }

    /**
     * Calculate MACD (Moving Average Convergence Divergence)
     */
    calculateMACD(prices) {
        if (prices.length < this.macdSlow + this.macdSignal) return null;

        const fastEMA = this.calculateEMA(prices, this.macdFast);
        const slowEMA = this.calculateEMA(prices, this.macdSlow);

        if (!fastEMA || !slowEMA) return null;

        const macdLine = fastEMA - slowEMA;

        const macdHistory = [];
        for (let i = this.macdSlow; i < prices.length; i++) {
            const fast = this.calculateEMA(prices.slice(0, i + 1), this.macdFast);
            const slow = this.calculateEMA(prices.slice(0, i + 1), this.macdSlow);
            if (fast && slow) {
                macdHistory.push(fast - slow);
            }
        }

        const signalLine = macdHistory.length >= this.macdSignal
            ? this.calculateEMA(macdHistory.slice(-this.macdSignal), this.macdSignal)
            : null;

        const histogram = signalLine !== null ? macdLine - signalLine : null;

        return {
            macd: macdLine,
            signal: signalLine,
            histogram: histogram,
            bullish: histogram !== null && histogram > 0,
            bearish: histogram !== null && histogram < 0
        };
    }

    /**
     * Calculate ATR (Average True Range)
     */
    calculateATR(highs, lows, closes, period = 14) {
        if (highs.length < period + 1) return null;

        const trueRanges = [];
        for (let i = 1; i < highs.length; i++) {
            const tr1 = highs[i] - lows[i];
            const tr2 = Math.abs(highs[i] - closes[i - 1]);
            const tr3 = Math.abs(lows[i] - closes[i - 1]);
            trueRanges.push(Math.max(tr1, tr2, tr3));
        }

        const atr = trueRanges.slice(-period).reduce((a, b) => a + b, 0) / period;
        return atr;
    }

    /**
     * Core RSI+MACD Algorithm (40% weight - IMMUTABLE)
     */
    calculateRSIMACDScore(ohlcvData) {
        if (!ohlcvData || ohlcvData.length < 30) return { score: 0, signal: 'hold', confidence: 0 };

        const closes = ohlcvData.map(c => c.close);
        const rsi = this.calculateRSI(closes, this.rsiPeriod);
        const macd = this.calculateMACD(closes);

        if (!rsi || !macd || macd.histogram === null) {
            return { score: 0, signal: 'hold', confidence: 0 };
        }

        let score = 0;
        let signal = 'hold';
        let confidence = 0;

        // BUY Condition: RSI < 30 AND MACD histogram > 0
        if (rsi < 30 && macd.histogram > 0) {
            const rsiStrength = (30 - rsi) / 30; // 0 to 1, stronger when RSI is lower
            const macdStrength = Math.min(macd.histogram / (macd.macd * 0.1), 1); // Normalized
            score = (rsiStrength * 0.5 + macdStrength * 0.5) * 100;
            signal = 'buy';
            confidence = Math.min(score, 100);
        }
        // SELL Condition: RSI > 70 AND MACD histogram < 0
        else if (rsi > 70 && macd.histogram < 0) {
            const rsiStrength = (rsi - 70) / 30; // 0 to 1, stronger when RSI is higher
            const macdStrength = Math.min(Math.abs(macd.histogram) / (Math.abs(macd.macd) * 0.1), 1);
            score = (rsiStrength * 0.5 + macdStrength * 0.5) * 100;
            signal = 'sell';
            confidence = Math.min(score, 100);
        }
        // HOLD: All other conditions
        else {
            score = 50; // Neutral
            signal = 'hold';
            confidence = 30;
        }

        return {
            score: score,
            signal: signal,
            confidence: confidence,
            rsi: rsi,
            macd: macd,
            details: {
                rsi: rsi.toFixed(2),
                macd: macd.macd.toFixed(4),
                signal: macd.signal ? macd.signal.toFixed(4) : 'N/A',
                histogram: macd.histogram.toFixed(4)
            }
        };
    }

    /**
     * Smart Money Concepts (SMC) Analysis (25% weight)
     */
    calculateSMCScore(ohlcvData) {
        if (!ohlcvData || ohlcvData.length < 50) return { score: 50, signal: 'hold', confidence: 0 };

        const highs = ohlcvData.map(c => c.high);
        const lows = ohlcvData.map(c => c.low);
        const closes = ohlcvData.map(c => c.close);
        const volumes = ohlcvData.map(c => c.volume);

        // Identify Order Blocks (areas of high volume)
        const orderBlocks = this.identifyOrderBlocks(ohlcvData);

        // Identify Liquidity Zones (support/resistance)
        const liquidityZones = this.identifyLiquidityZones(highs, lows, closes);

        // Identify Breaker Blocks (failed support/resistance)
        const breakerBlocks = this.identifyBreakerBlocks(ohlcvData);

        // Current price position relative to SMC levels
        const currentPrice = closes[closes.length - 1];
        let smcScore = 50;
        let smcSignal = 'hold';

        // Check if price is near order block
        const nearOrderBlock = orderBlocks.some(block =>
            currentPrice >= block.low && currentPrice <= block.high
        );

        // Check liquidity zones
        const nearSupport = liquidityZones.some(zone =>
            currentPrice >= zone.level * 0.995 && currentPrice <= zone.level * 1.005 && zone.type === 'support'
        );
        const nearResistance = liquidityZones.some(zone =>
            currentPrice >= zone.level * 0.995 && currentPrice <= zone.level * 1.005 && zone.type === 'resistance'
        );

        if (nearOrderBlock && nearSupport) {
            smcScore = 75;
            smcSignal = 'buy';
        } else if (nearOrderBlock && nearResistance) {
            smcScore = 25;
            smcSignal = 'sell';
        } else if (nearSupport) {
            smcScore = 65;
            smcSignal = 'buy';
        } else if (nearResistance) {
            smcScore = 35;
            smcSignal = 'sell';
        }

        this.smcLevels = {
            orderBlocks: orderBlocks,
            liquidityZones: liquidityZones,
            breakerBlocks: breakerBlocks
        };

        return {
            score: smcScore,
            signal: smcSignal,
            confidence: Math.abs(smcScore - 50) * 2,
            levels: {
                orderBlocks: orderBlocks.length,
                liquidityZones: liquidityZones.length,
                breakerBlocks: breakerBlocks.length
            }
        };
    }

    /**
     * Identify Order Blocks
     */
    identifyOrderBlocks(ohlcvData) {
        const blocks = [];
        const volumes = ohlcvData.map(c => c.volume);
        const avgVolume = volumes.reduce((a, b) => a + b, 0) / volumes.length;

        for (let i = 0; i < ohlcvData.length - 1; i++) {
            if (ohlcvData[i].volume > avgVolume * 1.5) {
                blocks.push({
                    index: i,
                    high: ohlcvData[i].high,
                    low: ohlcvData[i].low,
                    volume: ohlcvData[i].volume,
                    timestamp: ohlcvData[i].timestamp
                });
            }
        }

        return blocks.slice(-10); // Last 10 order blocks
    }

    /**
     * Identify Liquidity Zones (Support/Resistance)
     */
    identifyLiquidityZones(highs, lows, closes) {
        const zones = [];
        const lookback = 20;

        for (let i = lookback; i < closes.length; i++) {
            const recentHighs = highs.slice(i - lookback, i);
            const recentLows = lows.slice(i - lookback, i);
            const maxHigh = Math.max(...recentHighs);
            const minLow = Math.min(...recentLows);

            // Resistance zone
            if (closes[i] < maxHigh * 0.98) {
                zones.push({
                    level: maxHigh,
                    type: 'resistance',
                    strength: this.calculateZoneStrength(highs, maxHigh, i)
                });
            }

            // Support zone
            if (closes[i] > minLow * 1.02) {
                zones.push({
                    level: minLow,
                    type: 'support',
                    strength: this.calculateZoneStrength(lows, minLow, i)
                });
            }
        }

        // Remove duplicates and keep strongest
        const uniqueZones = [];
        const seenLevels = new Set();

        zones.sort((a, b) => b.strength - a.strength);
        for (const zone of zones) {
            const key = Math.round(zone.level * 100) / 100;
            if (!seenLevels.has(key)) {
                seenLevels.add(key);
                uniqueZones.push(zone);
            }
        }

        return uniqueZones.slice(-5); // Top 5 zones
    }

    /**
     * Calculate zone strength
     */
    calculateZoneStrength(prices, level, currentIndex) {
        let touches = 0;
        const tolerance = level * 0.01; // 1% tolerance

        for (let i = Math.max(0, currentIndex - 20); i < currentIndex; i++) {
            if (Math.abs(prices[i] - level) < tolerance) {
                touches++;
            }
        }

        return touches;
    }

    /**
     * Identify Breaker Blocks
     */
    identifyBreakerBlocks(ohlcvData) {
        const breakers = [];
        const closes = ohlcvData.map(c => c.close);

        for (let i = 10; i < closes.length - 5; i++) {
            const recentHigh = Math.max(...closes.slice(i - 10, i));
            const recentLow = Math.min(...closes.slice(i - 10, i));

            // Bullish breaker (resistance broken)
            if (closes[i] > recentHigh * 1.01) {
                breakers.push({
                    type: 'bullish',
                    level: recentHigh,
                    index: i,
                    timestamp: ohlcvData[i].timestamp
                });
            }

            // Bearish breaker (support broken)
            if (closes[i] < recentLow * 0.99) {
                breakers.push({
                    type: 'bearish',
                    level: recentLow,
                    index: i,
                    timestamp: ohlcvData[i].timestamp
                });
            }
        }

        return breakers.slice(-5); // Last 5 breakers
    }

    /**
     * Pattern Recognition (20% weight)
     */
    calculatePatternScore(ohlcvData) {
        if (!ohlcvData || ohlcvData.length < 20) return { score: 50, signal: 'hold', confidence: 0 };

        const patterns = this.detectPatterns(ohlcvData);
        let patternScore = 50;
        let patternSignal = 'hold';

        const bullishPatterns = patterns.filter(p => p.type === 'bullish').length;
        const bearishPatterns = patterns.filter(p => p.type === 'bearish').length;

        if (bullishPatterns > bearishPatterns) {
            patternScore = 50 + (bullishPatterns * 10);
            patternSignal = 'buy';
        } else if (bearishPatterns > bullishPatterns) {
            patternScore = 50 - (bearishPatterns * 10);
            patternSignal = 'sell';
        }

        this.patterns = patterns;

        return {
            score: Math.max(0, Math.min(100, patternScore)),
            signal: patternSignal,
            confidence: Math.abs(patternScore - 50) * 2,
            patterns: patterns.length,
            bullish: bullishPatterns,
            bearish: bearishPatterns
        };
    }

    /**
     * Detect Trading Patterns
     */
    detectPatterns(ohlcvData) {
        const patterns = [];
        const closes = ohlcvData.map(c => c.close);
        const highs = ohlcvData.map(c => c.high);
        const lows = ohlcvData.map(c => c.low);

        // Head and Shoulders
        if (closes.length >= 20) {
            const hns = this.detectHeadAndShoulders(highs, lows);
            if (hns) patterns.push(hns);
        }

        // Double Top/Bottom
        const doublePattern = this.detectDoubleTopBottom(highs, lows);
        if (doublePattern) patterns.push(doublePattern);

        // Triangle Patterns
        const triangle = this.detectTriangle(highs, lows);
        if (triangle) patterns.push(triangle);

        // Candlestick Patterns
        const candlestickPatterns = this.detectCandlestickPatterns(ohlcvData);
        patterns.push(...candlestickPatterns);

        return patterns;
    }

    /**
     * Detect Head and Shoulders Pattern
     */
    detectHeadAndShoulders(highs, lows) {
        if (highs.length < 20) return null;

        const recentHighs = highs.slice(-20);
        const maxIndex = recentHighs.indexOf(Math.max(...recentHighs));

        if (maxIndex > 5 && maxIndex < 15) {
            const leftShoulder = Math.max(...recentHighs.slice(0, maxIndex - 2));
            const head = recentHighs[maxIndex];
            const rightShoulder = Math.max(...recentHighs.slice(maxIndex + 2));

            if (head > leftShoulder * 1.02 && head > rightShoulder * 1.02) {
                return {
                    type: 'bearish',
                    name: 'Head and Shoulders',
                    confidence: 70
                };
            }
        }

        return null;
    }

    /**
     * Detect Double Top/Bottom
     */
    detectDoubleTopBottom(highs, lows) {
        if (highs.length < 15) return null;

        const recentHighs = highs.slice(-15);
        const recentLows = lows.slice(-15);

        const max1 = Math.max(...recentHighs.slice(0, 7));
        const max2 = Math.max(...recentHighs.slice(7));
        const min1 = Math.min(...recentLows.slice(0, 7));
        const min2 = Math.min(...recentLows.slice(7));

        // Double Top
        if (Math.abs(max1 - max2) / max1 < 0.02) {
            return {
                type: 'bearish',
                name: 'Double Top',
                confidence: 65
            };
        }

        // Double Bottom
        if (Math.abs(min1 - min2) / min1 < 0.02) {
            return {
                type: 'bullish',
                name: 'Double Bottom',
                confidence: 65
            };
        }

        return null;
    }

    /**
     * Detect Triangle Patterns
     */
    detectTriangle(highs, lows) {
        if (highs.length < 10) return null;

        const recentHighs = highs.slice(-10);
        const recentLows = lows.slice(-10);

        const highTrend = this.calculateTrend(recentHighs);
        const lowTrend = this.calculateTrend(recentLows);

        // Ascending Triangle
        if (highTrend > -0.001 && lowTrend > 0.001) {
            return {
                type: 'bullish',
                name: 'Ascending Triangle',
                confidence: 60
            };
        }

        // Descending Triangle
        if (highTrend < 0.001 && lowTrend < -0.001) {
            return {
                type: 'bearish',
                name: 'Descending Triangle',
                confidence: 60
            };
        }

        return null;
    }

    /**
     * Calculate Trend
     */
    calculateTrend(values) {
        if (values.length < 2) return 0;
        return (values[values.length - 1] - values[0]) / values.length;
    }

    /**
     * Detect Candlestick Patterns
     */
    detectCandlestickPatterns(ohlcvData) {
        const patterns = [];

        if (ohlcvData.length < 3) return patterns;

        for (let i = 2; i < ohlcvData.length; i++) {
            const current = ohlcvData[i];
            const prev = ohlcvData[i - 1];
            const prev2 = ohlcvData[i - 2];

            // Validate candle data
            if (!current || !prev || !prev2 || 
                typeof current.open !== 'number' || isNaN(current.open) ||
                typeof current.high !== 'number' || isNaN(current.high) ||
                typeof current.low !== 'number' || isNaN(current.low) ||
                typeof current.close !== 'number' || isNaN(current.close) ||
                typeof prev.open !== 'number' || isNaN(prev.open) ||
                typeof prev.close !== 'number' || isNaN(prev.close)) {
                continue; // Skip invalid candles
            }

            // Validate OHLC relationships
            if (current.high < current.low || 
                current.high < Math.max(current.open, current.close) ||
                current.low > Math.min(current.open, current.close)) {
                continue; // Skip invalid OHLC
            }

            // Hammer (Bullish)
            const body = Math.abs(current.close - current.open);
            const lowerShadow = Math.min(current.open, current.close) - current.low;
            const upperShadow = current.high - Math.max(current.open, current.close);

            if (body > 0 && lowerShadow > body * 2 && upperShadow < body * 0.5 && current.close > current.open) {
                patterns.push({
                    type: 'bullish',
                    name: 'Hammer',
                    confidence: 55
                });
            }

            // Shooting Star (Bearish)
            if (body > 0 && upperShadow > body * 2 && lowerShadow < body * 0.5 && current.close < current.open) {
                patterns.push({
                    type: 'bearish',
                    name: 'Shooting Star',
                    confidence: 55
                });
            }

            // Engulfing Pattern
            if (prev.close < prev.open && current.close > current.open &&
                current.open < prev.close && current.close > prev.open) {
                patterns.push({
                    type: 'bullish',
                    name: 'Bullish Engulfing',
                    confidence: 60
                });
            }

            if (prev.close > prev.open && current.close < current.open &&
                current.open > prev.close && current.close < prev.open) {
                patterns.push({
                    type: 'bearish',
                    name: 'Bearish Engulfing',
                    confidence: 60
                });
            }
        }

        return patterns.slice(-5); // Last 5 patterns
    }

    /**
     * Sentiment Analysis (10% weight)
     */
    async calculateSentimentScore(symbol, retries = 2) {
        const baseUrl = window.location.origin;
        const apiUrl = `${baseUrl}/api/ai/sentiment?symbol=${symbol}`;

        for (let attempt = 0; attempt <= retries; attempt++) {
            try {
                if (attempt > 0) {
                    const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }

                const response = await fetch(apiUrl, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    signal: AbortSignal.timeout(10000)
                });

                if (response.ok) {
                    const contentType = response.headers.get('content-type');
                    if (!contentType || !contentType.includes('application/json')) {
                        throw new Error('Invalid response type');
                    }

                    const data = await response.json();
                    
                    if (!data || typeof data !== 'object') {
                        throw new Error('Invalid response format');
                    }
                    
                    if (typeof data.sentiment_score === 'number' && !isNaN(data.sentiment_score)) {
                        const sentimentScore = Math.max(-1, Math.min(1, data.sentiment_score)); // Clamp to -1 to 1
                        this.sentimentScore = sentimentScore;
                        return {
                            score: 50 + (sentimentScore * 50), // Convert -1 to 1 range to 0-100
                            signal: sentimentScore > 0 ? 'buy' : sentimentScore < 0 ? 'sell' : 'hold',
                            confidence: Math.abs(sentimentScore) * 50,
                            sentiment: sentimentScore
                        };
                    }
                } else {
                    if (attempt < retries && response.status >= 500) {
                        continue; // Retry on server errors
                    }
                    console.warn(`[HTS] Sentiment API returned status ${response.status}`);
                }
            } catch (error) {
                if (attempt < retries && (error.name === 'AbortError' || error.message.includes('timeout') || error.message.includes('network'))) {
                    continue; // Retry on network errors
                }
                console.warn('[HTS] Sentiment API unavailable:', error);
                break; // Don't retry on other errors
            }
        }

        // Return neutral sentiment on failure
        return { score: 50, signal: 'hold', confidence: 0, sentiment: 0 };
    }

    /**
     * Machine Learning Score (5% weight)
     */
    calculateMLScore(ohlcvData, rsiMacdScore, smcScore, patternScore, sentimentScore) {
        // Simple ML-like scoring based on ensemble of other indicators
        // In production, this would use a trained model

        const features = {
            rsiMacdStrength: Math.abs(rsiMacdScore.score - 50) / 50,
            smcStrength: Math.abs(smcScore.score - 50) / 50,
            patternStrength: Math.abs(patternScore.score - 50) / 50,
            sentimentStrength: Math.abs(sentimentScore.score - 50) / 50,
            volumeTrend: this.calculateVolumeTrend(ohlcvData),
            priceMomentum: this.calculatePriceMomentum(ohlcvData)
        };

        // Weighted ensemble
        const mlScore = 50 + (
            features.rsiMacdStrength * 20 +
            features.smcStrength * 15 +
            features.patternStrength * 10 +
            features.sentimentStrength * 5 +
            features.volumeTrend * 5 +
            features.priceMomentum * 5
        );

        this.mlScore = mlScore;

        return {
            score: Math.max(0, Math.min(100, mlScore)),
            signal: mlScore > 55 ? 'buy' : mlScore < 45 ? 'sell' : 'hold',
            confidence: Math.abs(mlScore - 50) * 2,
            features: features
        };
    }

    /**
     * Calculate Volume Trend
     */
    calculateVolumeTrend(ohlcvData) {
        if (ohlcvData.length < 10) return 0;

        const volumes = ohlcvData.map(c => c.volume);
        const recentAvg = volumes.slice(-5).reduce((a, b) => a + b, 0) / 5;
        const olderAvg = volumes.slice(-10, -5).reduce((a, b) => a + b, 0) / 5;

        return (recentAvg - olderAvg) / olderAvg; // Percentage change
    }

    /**
     * Calculate Price Momentum
     */
    calculatePriceMomentum(ohlcvData) {
        if (ohlcvData.length < 10) return 0;

        const closes = ohlcvData.map(c => c.close);
        const recent = closes.slice(-5).reduce((a, b) => a + b, 0) / 5;
        const older = closes.slice(-10, -5).reduce((a, b) => a + b, 0) / 5;

        return (recent - older) / older; // Percentage change
    }

    /**
     * Detect Market Regime (Trending, Ranging, Volatile, Neutral)
     */
    detectMarketRegime(ohlcvData) {
        if (!ohlcvData || !Array.isArray(ohlcvData) || ohlcvData.length < 50) return 'neutral';

        const closes = ohlcvData
            .map(c => (c && typeof c.close === 'number' && !isNaN(c.close) && c.close > 0) ? c.close : null)
            .filter(c => c !== null);
        const highs = ohlcvData
            .map(c => (c && typeof c.high === 'number' && !isNaN(c.high) && c.high > 0) ? c.high : null)
            .filter(h => h !== null);
        const lows = ohlcvData
            .map(c => (c && typeof c.low === 'number' && !isNaN(c.low) && c.low > 0) ? c.low : null)
            .filter(l => l !== null);

        if (closes.length < 20 || highs.length < 20 || lows.length < 20) return 'neutral';

        // Calculate volatility (ATR normalized)
        const atr = this.calculateATR(highs, lows, closes, this.atrPeriod);
        const avgPrice = closes.slice(-20).reduce((a, b) => a + b, 0) / 20;
        this.volatility = (atr && avgPrice > 0) ? (atr / avgPrice) * 100 : 0;

        // Calculate trend strength using ADX-like logic
        const trendStrength = this.calculateTrendStrength(ohlcvData);

        // Calculate price range (for ranging detection)
        const recentHigh = Math.max(...highs.slice(-20));
        const recentLow = Math.min(...lows.slice(-20));
        const rangePercent = (avgPrice > 0) ? ((recentHigh - recentLow) / avgPrice) * 100 : 0;

        // Determine regime
        if (this.volatility > 5 && trendStrength > 60) {
            return 'volatile-trending';
        } else if (this.volatility > 5) {
            return 'volatile';
        } else if (trendStrength > 60) {
            return 'trending';
        } else if (rangePercent < 3 && trendStrength < 30) {
            return 'ranging';
        } else {
            return 'neutral';
        }
    }

    /**
     * Calculate Trend Strength (ADX-like)
     */
    calculateTrendStrength(ohlcvData) {
        if (ohlcvData.length < 14) return 0;

        const closes = ohlcvData.map(c => c.close);
        const highs = ohlcvData.map(c => c.high);
        const lows = ohlcvData.map(c => c.low);

        let plusDM = 0;
        let minusDM = 0;

        for (let i = 1; i < closes.length; i++) {
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
     * Adjust weights dynamically based on market regime
     */
    adjustWeightsForMarketRegime(regime, volatility, trendStrength) {
        // Reset to base weights
        this.weights = { ...this.baseWeights };

        switch (regime) {
            case 'trending':
                // In trending markets, increase RSI+MACD and SMC weights
                this.weights.rsiMacd = Math.min(0.50, this.baseWeights.rsiMacd * 1.15);
                this.weights.smc = Math.min(0.30, this.baseWeights.smc * 1.20);
                this.weights.patterns = this.baseWeights.patterns * 0.90;
                this.weights.sentiment = this.baseWeights.sentiment * 0.85;
                break;

            case 'ranging':
                // In ranging markets, increase pattern recognition
                this.weights.rsiMacd = Math.max(0.30, this.baseWeights.rsiMacd * 0.85);
                this.weights.patterns = Math.min(0.30, this.baseWeights.patterns * 1.30);
                this.weights.smc = this.baseWeights.smc * 1.10;
                this.weights.sentiment = this.baseWeights.sentiment * 0.90;
                break;

            case 'volatile':
            case 'volatile-trending':
                // In volatile markets, increase SMC and sentiment
                this.weights.rsiMacd = Math.max(0.30, this.baseWeights.rsiMacd * 0.90);
                this.weights.smc = Math.min(0.35, this.baseWeights.smc * 1.40);
                this.weights.sentiment = Math.min(0.20, this.baseWeights.sentiment * 2.00);
                this.weights.patterns = this.baseWeights.patterns * 0.80;
                break;

            case 'neutral':
            default:
                // Keep base weights
                break;
        }

        // Adjust ML weight based on volatility (higher volatility = more ML)
        if (volatility > 4) {
            this.weights.ml = Math.min(0.10, this.baseWeights.ml * 1.50);
        } else {
            this.weights.ml = this.baseWeights.ml;
        }

        // Normalize weights to sum to 1.0
        const total = Object.values(this.weights).reduce((a, b) => a + b, 0);
        Object.keys(this.weights).forEach(key => {
            this.weights[key] = this.weights[key] / total;
        });

        // Ensure RSI+MACD stays within bounds (30% - 50%)
        if (this.weights.rsiMacd < 0.30) {
            const diff = 0.30 - this.weights.rsiMacd;
            this.weights.rsiMacd = 0.30;
            // Redistribute difference proportionally
            const otherTotal = 1.0 - this.weights.rsiMacd;
            Object.keys(this.weights).forEach(key => {
                if (key !== 'rsiMacd') {
                    this.weights[key] = (this.weights[key] / otherTotal) * (1.0 - this.weights.rsiMacd);
                }
            });
        } else if (this.weights.rsiMacd > 0.50) {
            const diff = this.weights.rsiMacd - 0.50;
            this.weights.rsiMacd = 0.50;
            // Redistribute difference proportionally
            const otherTotal = 1.0 - this.weights.rsiMacd;
            Object.keys(this.weights).forEach(key => {
                if (key !== 'rsiMacd') {
                    this.weights[key] = (this.weights[key] / otherTotal) * (1.0 - this.weights.rsiMacd);
                }
            });
        }
    }

    /**
     * Main Analysis Function - Combines all components with dynamic weight adjustment
     */
    async analyze(ohlcvData, symbol = 'BTC') {
        if (!ohlcvData || ohlcvData.length < 30) {
            throw new Error('Insufficient data for analysis');
        }

        this.priceHistory = ohlcvData;

        // Detect market regime and adjust weights dynamically
        this.marketRegime = this.detectMarketRegime(ohlcvData);
        const trendStrength = this.calculateTrendStrength(ohlcvData);
        this.adjustWeightsForMarketRegime(this.marketRegime, this.volatility, trendStrength);

        // Calculate all components
        const rsiMacdResult = this.calculateRSIMACDScore(ohlcvData);
        const smcResult = this.calculateSMCScore(ohlcvData);
        const patternResult = this.calculatePatternScore(ohlcvData);
        const sentimentResult = await this.calculateSentimentScore(symbol);
        const mlResult = this.calculateMLScore(ohlcvData, rsiMacdResult, smcResult, patternResult, sentimentResult);

        // Calculate final weighted score with dynamic weights
        const finalScore =
            (rsiMacdResult.score * this.weights.rsiMacd) +
            (smcResult.score * this.weights.smc) +
            (patternResult.score * this.weights.patterns) +
            (sentimentResult.score * this.weights.sentiment) +
            (mlResult.score * this.weights.ml);

        // Determine final signal
        let finalSignal = 'hold';
        if (finalScore > 60) {
            finalSignal = 'buy';
        } else if (finalScore < 40) {
            finalSignal = 'sell';
        }

        // Calculate overall confidence
        const confidence = (
            rsiMacdResult.confidence * this.weights.rsiMacd +
            smcResult.confidence * this.weights.smc +
            patternResult.confidence * this.weights.patterns +
            sentimentResult.confidence * this.weights.sentiment +
            mlResult.confidence * this.weights.ml
        );

        // Calculate risk/reward
        const currentPrice = ohlcvData[ohlcvData.length - 1].close;
        const atr = this.calculateATR(
            ohlcvData.map(c => c.high),
            ohlcvData.map(c => c.low),
            ohlcvData.map(c => c.close)
        );

        const stopLoss = finalSignal === 'buy'
            ? currentPrice - (atr * 2)
            : currentPrice + (atr * 2);

        const takeProfit1 = finalSignal === 'buy'
            ? currentPrice + (atr * 1.5)
            : currentPrice - (atr * 1.5);

        const takeProfit2 = finalSignal === 'buy'
            ? currentPrice + (atr * 2.5)
            : currentPrice - (atr * 2.5);

        const takeProfit3 = finalSignal === 'buy'
            ? currentPrice + (atr * 4)
            : currentPrice - (atr * 4);

        const riskReward = atr ? Math.abs(takeProfit1 - currentPrice) / Math.abs(stopLoss - currentPrice) : 0;

        return {
            finalScore: finalScore,
            finalSignal: finalSignal,
            confidence: Math.min(100, confidence),
            currentPrice: currentPrice,
            stopLoss: stopLoss,
            takeProfitLevels: [
                { level: takeProfit1, type: 'TP1', riskReward: riskReward },
                { level: takeProfit2, type: 'TP2', riskReward: riskReward * 1.67 },
                { level: takeProfit3, type: 'TP3', riskReward: riskReward * 2.67 }
            ],
            riskReward: riskReward,
            components: {
                rsiMacd: {
                    score: rsiMacdResult.score,
                    signal: rsiMacdResult.signal,
                    confidence: rsiMacdResult.confidence,
                    weight: this.weights.rsiMacd,
                    details: rsiMacdResult.details
                },
                smc: {
                    score: smcResult.score,
                    signal: smcResult.signal,
                    confidence: smcResult.confidence,
                    weight: this.weights.smc,
                    levels: smcResult.levels
                },
                patterns: {
                    score: patternResult.score,
                    signal: patternResult.signal,
                    confidence: patternResult.confidence,
                    weight: this.weights.patterns,
                    detected: patternResult.patterns,
                    bullish: patternResult.bullish,
                    bearish: patternResult.bearish
                },
                sentiment: {
                    score: sentimentResult.score,
                    signal: sentimentResult.signal,
                    confidence: sentimentResult.confidence,
                    weight: this.weights.sentiment,
                    sentiment: sentimentResult.sentiment
                },
                ml: {
                    score: mlResult.score,
                    signal: mlResult.signal,
                    confidence: mlResult.confidence,
                    weight: this.weights.ml,
                    features: mlResult.features
                }
            },
            indicators: {
                rsi: rsiMacdResult.rsi,
                macd: rsiMacdResult.macd,
                atr: atr
            },
            smcLevels: this.smcLevels,
            patterns: this.patterns
        };
    }
}

export default HTSEngine;

