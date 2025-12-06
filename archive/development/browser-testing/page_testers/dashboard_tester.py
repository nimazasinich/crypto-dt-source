"""Dashboard page specific tests"""
import time
from typing import List
from .base_tester import BasePageTester
from browser_testing.utils.browser_utils import TestResult


class DashboardTester(BasePageTester):
    """Tests for the main dashboard page"""
    
    async def run_specific_tests(self) -> List[TestResult]:
        """Run dashboard-specific tests"""
        results = []
        
        results.append(await self.test_refresh_button())
        results.append(await self.test_stats_cards())
        results.append(await self.test_market_data())
        
        return results
    
    async def test_refresh_button(self) -> TestResult:
        """Test the refresh button functionality"""
        start_time = time.time()
        test_name = "Dashboard: Refresh button"
        
        try:
            result = self.browser.click_button('button#refresh-btn', 'Refresh')
            return result
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status='failed',
                duration=duration,
                details="Failed to click refresh button",
                error=str(e)
            )
    
    async def test_stats_cards(self) -> TestResult:
        """Verify stats cards load with data"""
        start_time = time.time()
        test_name = "Dashboard: Stats cards loaded"
        
        try:
            has_stats = self.browser.check_element_exists('.stats-grid')
            duration = time.time() - start_time
            
            if has_stats:
                return TestResult(
                    test_name=test_name,
                    status='passed',
                    duration=duration,
                    details="Stats cards found and loaded"
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status='failed',
                    duration=duration,
                    details="Stats cards not found",
                    error="Missing .stats-grid element"
                )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status='failed',
                duration=duration,
                details="Error checking stats cards",
                error=str(e)
            )
    
    async def test_market_data(self) -> TestResult:
        """Test market data section"""
        start_time = time.time()
        test_name = "Dashboard: Market data section"
        
        try:
            has_market = self.browser.check_element_exists('.dashboard-section')
            duration = time.time() - start_time
            
            if has_market:
                return TestResult(
                    test_name=test_name,
                    status='passed',
                    duration=duration,
                    details="Market data section found"
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status='failed',
                    duration=duration,
                    details="Market data section not found",
                    error="Missing dashboard section"
                )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status='failed',
                duration=duration,
                details="Error checking market data",
                error=str(e)
            )

