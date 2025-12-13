#!/usr/bin/env python3
"""
Test Trading & Backtesting System
Tests smart exchange integration with Binance & KuCoin
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.trading_backtesting_service import (
    get_trading_service,
    get_backtesting_service
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingSystemTester:
    """Test the trading and backtesting system"""
    
    def __init__(self, enable_proxy: bool = False):
        self.enable_proxy = enable_proxy
        self.trading_service = get_trading_service(enable_proxy=enable_proxy)
        self.backtest_service = get_backtesting_service()
        self.test_results = []
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if details:
            logger.info(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    async def test_binance_price(self):
        """Test 1: Get Bitcoin price from Binance"""
        try:
            result = await self.trading_service.get_trading_price(
                symbol="BTCUSDT",
                exchange="binance"
            )
            
            success = (
                result.get("success") and
                result.get("price", 0) > 0
            )
            
            details = f"BTC price: ${result.get('price', 0):,.2f}, method: {result.get('method', 'unknown')}"
            self.log_test_result("Binance - Get BTC Price", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Binance - Get BTC Price", False, str(e))
            return False
    
    async def test_kucoin_price(self):
        """Test 2: Get Bitcoin price from KuCoin"""
        try:
            result = await self.trading_service.get_trading_price(
                symbol="BTC-USDT",
                exchange="kucoin"
            )
            
            success = (
                result.get("success") and
                result.get("price", 0) > 0
            )
            
            details = f"BTC price: ${result.get('price', 0):,.2f}, method: {result.get('method', 'unknown')}"
            self.log_test_result("KuCoin - Get BTC Price", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("KuCoin - Get BTC Price", False, str(e))
            return False
    
    async def test_binance_ohlcv(self):
        """Test 3: Get OHLCV data from Binance"""
        try:
            result = await self.trading_service.get_trading_ohlcv(
                symbol="BTCUSDT",
                timeframe="1h",
                limit=10,
                exchange="binance"
            )
            
            success = (
                result.get("success") and
                len(result.get("candles", [])) > 0
            )
            
            candles_count = len(result.get("candles", []))
            details = f"Fetched {candles_count} candles for BTC 1h"
            self.log_test_result("Binance - Get OHLCV", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Binance - Get OHLCV", False, str(e))
            return False
    
    async def test_kucoin_ohlcv(self):
        """Test 4: Get OHLCV data from KuCoin"""
        try:
            result = await self.trading_service.get_trading_ohlcv(
                symbol="BTC-USDT",
                timeframe="1h",
                limit=10,
                exchange="kucoin"
            )
            
            success = (
                result.get("success") and
                len(result.get("candles", [])) > 0
            )
            
            candles_count = len(result.get("candles", []))
            details = f"Fetched {candles_count} candles for BTC 1h"
            self.log_test_result("KuCoin - Get OHLCV", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("KuCoin - Get OHLCV", False, str(e))
            return False
    
    async def test_binance_orderbook(self):
        """Test 5: Get order book from Binance"""
        try:
            result = await self.trading_service.get_orderbook(
                symbol="BTCUSDT",
                exchange="binance",
                limit=5
            )
            
            success = (
                result.get("success") and
                len(result.get("bids", [])) > 0 and
                len(result.get("asks", [])) > 0
            )
            
            bids_count = len(result.get("bids", []))
            asks_count = len(result.get("asks", []))
            details = f"Orderbook: {bids_count} bids, {asks_count} asks"
            self.log_test_result("Binance - Get Orderbook", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Binance - Get Orderbook", False, str(e))
            return False
    
    async def test_binance_24h_stats(self):
        """Test 6: Get 24h statistics from Binance"""
        try:
            result = await self.trading_service.get_24h_stats(
                symbol="BTCUSDT",
                exchange="binance"
            )
            
            success = result.get("success")
            
            change_percent = result.get("change_percent", 0)
            volume = result.get("volume", 0)
            details = f"24h change: {change_percent:.2f}%, volume: {volume:.2f} BTC"
            self.log_test_result("Binance - Get 24h Stats", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Binance - Get 24h Stats", False, str(e))
            return False
    
    async def test_historical_data_fetch(self):
        """Test 7: Fetch historical data for backtesting"""
        try:
            df = await self.backtest_service.fetch_historical_data(
                symbol="BTCUSDT",
                timeframe="1h",
                days=7,  # 7 days for faster test
                exchange="binance"
            )
            
            success = not df.empty
            
            details = f"Fetched {len(df)} candles for 7 days"
            self.log_test_result("Backtesting - Fetch Historical Data", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Backtesting - Fetch Historical Data", False, str(e))
            return False
    
    async def test_backtest_sma_crossover(self):
        """Test 8: Backtest SMA Crossover strategy"""
        try:
            result = await self.backtest_service.run_backtest(
                symbol="BTCUSDT",
                strategy="sma_crossover",
                timeframe="1h",
                days=7,  # 7 days for faster test
                exchange="binance",
                initial_capital=10000.0
            )
            
            success = result.get("success")
            
            total_return = result.get("total_return", 0)
            profit = result.get("profit", 0)
            trades = result.get("trades", 0)
            details = f"Return: {total_return:.2f}%, Profit: ${profit:.2f}, Trades: {trades}"
            self.log_test_result("Backtesting - SMA Crossover", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Backtesting - SMA Crossover", False, str(e))
            return False
    
    async def test_backtest_rsi(self):
        """Test 9: Backtest RSI strategy"""
        try:
            result = await self.backtest_service.run_backtest(
                symbol="BTCUSDT",
                strategy="rsi",
                timeframe="1h",
                days=7,
                exchange="binance",
                initial_capital=10000.0
            )
            
            success = result.get("success")
            
            total_return = result.get("total_return", 0)
            profit = result.get("profit", 0)
            trades = result.get("trades", 0)
            details = f"Return: {total_return:.2f}%, Profit: ${profit:.2f}, Trades: {trades}"
            self.log_test_result("Backtesting - RSI", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Backtesting - RSI", False, str(e))
            return False
    
    async def test_backtest_macd(self):
        """Test 10: Backtest MACD strategy"""
        try:
            result = await self.backtest_service.run_backtest(
                symbol="BTCUSDT",
                strategy="macd",
                timeframe="1h",
                days=7,
                exchange="binance",
                initial_capital=10000.0
            )
            
            success = result.get("success")
            
            total_return = result.get("total_return", 0)
            profit = result.get("profit", 0)
            trades = result.get("trades", 0)
            details = f"Return: {total_return:.2f}%, Profit: ${profit:.2f}, Trades: {trades}"
            self.log_test_result("Backtesting - MACD", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Backtesting - MACD", False, str(e))
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("=" * 80)
        logger.info("STARTING TRADING & BACKTESTING SYSTEM TEST SUITE")
        logger.info(f"Proxy Enabled: {self.enable_proxy}")
        logger.info("=" * 80)
        logger.info("")
        
        tests = [
            self.test_binance_price,
            self.test_kucoin_price,
            self.test_binance_ohlcv,
            self.test_kucoin_ohlcv,
            self.test_binance_orderbook,
            self.test_binance_24h_stats,
            self.test_historical_data_fetch,
            self.test_backtest_sma_crossover,
            self.test_backtest_rsi,
            self.test_backtest_macd
        ]
        
        for i, test in enumerate(tests, 1):
            logger.info(f"\n[Test {i}/{len(tests)}] Running {test.__name__}...")
            await test()
            # Small delay between tests
            await asyncio.sleep(1)
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("TEST SUITE COMPLETED")
        logger.info("=" * 80)
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"\nTotal Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            logger.info("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"  - {result['test']}: {result['details']}")
        
        logger.info("")
        
        return passed_tests == total_tests


async def main():
    """Main test function"""
    # You can enable proxy if needed
    enable_proxy = False  # Set to True if you need proxy
    
    tester = TradingSystemTester(enable_proxy=enable_proxy)
    all_passed = await tester.run_all_tests()
    
    if all_passed:
        logger.info("🎉 ALL TESTS PASSED! Trading & Backtesting system is fully functional.")
        return 0
    else:
        logger.error("⚠️ SOME TESTS FAILED! Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
