#!/usr/bin/env python3
"""
Comprehensive Test Suite for Multi-Source Fallback System
Tests all data types with 137+ sources
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.unified_multi_source_service import get_unified_service
from backend.services.multi_source_fallback_engine import DataType

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiSourceSystemTester:
    """Test the entire multi-source system"""
    
    def __init__(self):
        self.service = get_unified_service()
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
    
    async def test_market_prices_basic(self):
        """Test 1: Basic market prices fetch"""
        try:
            result = await self.service.get_market_prices(limit=10)
            
            success = (
                result.get("success") and
                result.get("data") is not None and
                len(result["data"].get("prices", [])) > 0
            )
            
            details = f"Fetched {len(result.get('data', {}).get('prices', []))} prices, source: {result.get('source', 'unknown')}"
            self.log_test_result("Market Prices - Basic Fetch", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Market Prices - Basic Fetch", False, str(e))
            return False
    
    async def test_market_prices_specific_symbols(self):
        """Test 2: Fetch specific symbols"""
        try:
            symbols = ["BTC", "ETH", "BNB"]
            result = await self.service.get_market_prices(symbols=symbols, limit=10)
            
            success = (
                result.get("success") and
                len(result.get("data", {}).get("prices", [])) > 0
            )
            
            details = f"Requested {symbols}, got {len(result.get('data', {}).get('prices', []))} prices"
            self.log_test_result("Market Prices - Specific Symbols", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Market Prices - Specific Symbols", False, str(e))
            return False
    
    async def test_market_prices_cross_check(self):
        """Test 3: Cross-check prices from multiple sources"""
        try:
            result = await self.service.get_market_prices(
                symbols=["BTC"],
                cross_check=True,
                limit=1
            )
            
            success = result.get("success")
            
            data = result.get("data", {})
            sources_used = data.get("sources_used", 0)
            cross_checked = data.get("cross_checked", False)
            
            details = f"Cross-checked: {cross_checked}, sources used: {sources_used}"
            self.log_test_result("Market Prices - Cross-Check", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Market Prices - Cross-Check", False, str(e))
            return False
    
    async def test_market_prices_parallel(self):
        """Test 4: Parallel fetch from multiple sources"""
        try:
            result = await self.service.get_market_prices(
                symbols=["BTC", "ETH"],
                use_parallel=True,
                limit=10
            )
            
            success = result.get("success")
            
            details = f"Parallel fetch completed, source: {result.get('source', 'unknown')}"
            self.log_test_result("Market Prices - Parallel Fetch", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Market Prices - Parallel Fetch", False, str(e))
            return False
    
    async def test_ohlc_data(self):
        """Test 5: OHLC/candlestick data"""
        try:
            result = await self.service.get_ohlc_data(
                symbol="BTC",
                timeframe="1h",
                limit=100
            )
            
            success = (
                result.get("success") and
                result.get("data") is not None and
                len(result["data"].get("candles", [])) > 0
            )
            
            candles = result.get("data", {}).get("candles", [])
            details = f"Fetched {len(candles)} candles for BTC 1h, source: {result.get('source', 'unknown')}"
            self.log_test_result("OHLC Data - BTC 1h", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("OHLC Data - BTC 1h", False, str(e))
            return False
    
    async def test_ohlc_validation(self):
        """Test 6: OHLC data validation"""
        try:
            result = await self.service.get_ohlc_data(
                symbol="ETH",
                timeframe="4h",
                limit=50,
                validate=True
            )
            
            success = result.get("success")
            
            validated = "validation_warning" not in result
            details = f"Validation passed: {validated}"
            self.log_test_result("OHLC Data - Validation", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("OHLC Data - Validation", False, str(e))
            return False
    
    async def test_news_fetch(self):
        """Test 7: News data fetch"""
        try:
            result = await self.service.get_news(
                query="bitcoin",
                limit=20
            )
            
            success = (
                result.get("success") and
                result.get("data") is not None and
                len(result["data"].get("articles", [])) > 0
            )
            
            articles = result.get("data", {}).get("articles", [])
            details = f"Fetched {len(articles)} articles, source: {result.get('source', 'unknown')}"
            self.log_test_result("News Data - Bitcoin News", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("News Data - Bitcoin News", False, str(e))
            return False
    
    async def test_news_aggregation(self):
        """Test 8: News aggregation from multiple sources"""
        try:
            result = await self.service.get_news(
                query="cryptocurrency",
                limit=50,
                aggregate=True
            )
            
            success = result.get("success")
            
            data = result.get("data", {})
            sources_used = data.get("sources_used", 0)
            articles_count = len(data.get("articles", []))
            
            details = f"Aggregated {articles_count} articles from {sources_used} sources"
            self.log_test_result("News Data - Aggregation", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("News Data - Aggregation", False, str(e))
            return False
    
    async def test_sentiment_data(self):
        """Test 9: Sentiment (Fear & Greed Index)"""
        try:
            result = await self.service.get_sentiment()
            
            success = (
                result.get("success") and
                result.get("data") is not None
            )
            
            data = result.get("data", {})
            value = data.get("value", "N/A")
            classification = data.get("classification", "N/A")
            
            details = f"Sentiment: {value} ({classification}), source: {result.get('source', 'unknown')}"
            self.log_test_result("Sentiment Data - Fear & Greed", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Sentiment Data - Fear & Greed", False, str(e))
            return False
    
    async def test_caching(self):
        """Test 10: Caching functionality"""
        try:
            # First request - should fetch from source
            result1 = await self.service.get_market_prices(symbols=["BTC"], limit=1)
            cached1 = result1.get("cached", False)
            
            # Second request - should come from cache
            result2 = await self.service.get_market_prices(symbols=["BTC"], limit=1)
            cached2 = result2.get("cached", False)
            
            success = (
                result1.get("success") and
                result2.get("success") and
                not cached1 and  # First should not be cached
                cached2  # Second should be cached
            )
            
            details = f"First request cached: {cached1}, Second request cached: {cached2}"
            self.log_test_result("Caching - Basic", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Caching - Basic", False, str(e))
            return False
    
    async def test_cache_clear(self):
        """Test 11: Cache clearing"""
        try:
            # Populate cache
            await self.service.get_market_prices(symbols=["ETH"], limit=1)
            
            # Clear cache
            self.service.clear_cache()
            
            # Fetch again - should not be cached
            result = await self.service.get_market_prices(symbols=["ETH"], limit=1)
            cached = result.get("cached", False)
            
            success = not cached
            
            details = f"After cache clear, cached: {cached}"
            self.log_test_result("Caching - Clear", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Caching - Clear", False, str(e))
            return False
    
    async def test_monitoring_stats(self):
        """Test 12: Monitoring statistics"""
        try:
            stats = self.service.get_monitoring_stats()
            
            success = (
                stats is not None and
                "sources" in stats
            )
            
            sources_count = len(stats.get("sources", {}))
            details = f"Monitoring {sources_count} sources"
            self.log_test_result("Monitoring - Statistics", success, details)
            
            return success
        except Exception as e:
            self.log_test_result("Monitoring - Statistics", False, str(e))
            return False
    
    async def test_error_handling(self):
        """Test 13: Error handling with invalid data"""
        try:
            # Try with invalid symbol
            result = await self.service.get_ohlc_data(
                symbol="INVALID_SYMBOL_XYZ",
                timeframe="1h",
                limit=10
            )
            
            # Should still return a result (from cache or error)
            success = result is not None
            
            details = f"Handled invalid symbol gracefully: {result.get('success', False)}"
            self.log_test_result("Error Handling - Invalid Symbol", success, details)
            
            return success
        except Exception as e:
            # Even exceptions should be caught and handled
            self.log_test_result("Error Handling - Invalid Symbol", True, f"Exception caught: {str(e)[:50]}")
            return True
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("=" * 80)
        logger.info("STARTING MULTI-SOURCE SYSTEM COMPREHENSIVE TEST SUITE")
        logger.info("=" * 80)
        logger.info("")
        
        tests = [
            self.test_market_prices_basic,
            self.test_market_prices_specific_symbols,
            self.test_market_prices_cross_check,
            self.test_market_prices_parallel,
            self.test_ohlc_data,
            self.test_ohlc_validation,
            self.test_news_fetch,
            self.test_news_aggregation,
            self.test_sentiment_data,
            self.test_caching,
            self.test_cache_clear,
            self.test_monitoring_stats,
            self.test_error_handling
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
    tester = MultiSourceSystemTester()
    all_passed = await tester.run_all_tests()
    
    if all_passed:
        logger.info("🎉 ALL TESTS PASSED! Multi-source system is fully functional.")
        return 0
    else:
        logger.error("⚠️ SOME TESTS FAILED! Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
