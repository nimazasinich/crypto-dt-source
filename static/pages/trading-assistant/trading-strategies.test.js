/**
 * Unit Tests for Trading Strategies
 */

import { analyzeWithStrategy, HYBRID_STRATEGIES } from './trading-strategies.js';

describe('Trading Strategies', () => {
  const mockMarketData = {
    price: 50000,
    volume: 1000000,
    high24h: 52000,
    low24h: 48000,
  };

  test('should analyze with trend-rsi-macd strategy', () => {
    const result = analyzeWithStrategy('BTC', 'trend-rsi-macd', mockMarketData);
    
    expect(result).toHaveProperty('strategy');
    expect(result).toHaveProperty('signal');
    expect(result).toHaveProperty('confidence');
    expect(result).toHaveProperty('indicators');
    expect(result).toHaveProperty('levels');
    expect(result).toHaveProperty('riskReward');
    expect(['buy', 'sell', 'hold']).toContain(result.signal);
  });

  test('should calculate support and resistance levels', () => {
    const result = analyzeWithStrategy('BTC', 'trend-rsi-macd', mockMarketData);
    
    expect(result.levels).toHaveProperty('resistance');
    expect(result.levels).toHaveProperty('support');
    expect(result.levels.resistance.length).toBeGreaterThan(0);
    expect(result.levels.support.length).toBeGreaterThan(0);
  });

  test('should calculate take profit levels', () => {
    const result = analyzeWithStrategy('BTC', 'trend-rsi-macd', mockMarketData);
    
    if (result.signal !== 'hold') {
      expect(result.takeProfitLevels).toBeDefined();
      expect(result.takeProfitLevels.length).toBeGreaterThan(0);
      expect(result.stopLoss).toBeDefined();
    }
  });

  test('should handle all strategy types', () => {
    Object.keys(HYBRID_STRATEGIES).forEach(strategyKey => {
      const result = analyzeWithStrategy('BTC', strategyKey, mockMarketData);
      expect(result).toBeDefined();
      expect(result.strategy).toBe(HYBRID_STRATEGIES[strategyKey].name);
    });
  });

  test('should throw error for unknown strategy', () => {
    expect(() => {
      analyzeWithStrategy('BTC', 'unknown-strategy', mockMarketData);
    }).toThrow();
  });
});

