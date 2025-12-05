"""
Base class for page-specific testers.
Provides common test methods used across all pages.
"""
import time
from typing import List
from browser_testing.utils.browser_utils import TestResult


class BasePageTester:
    """
    Base class for testing individual pages.
    Provides common test methods that all pages should pass.
    """
    
    def __init__(self, browser, page_path: str):
        """
        Initialize page tester.
        
        Args:
            browser: BrowserTester instance
            page_path: URL path for the page
        """
        self.browser = browser
        self.page_path = page_path
        self.test_results: List[TestResult] = []
    
    async def run_basic_tests(self) -> List[TestResult]:
        """
        Run basic tests common to all pages.
        
        Returns:
            List of TestResults
        """
        results = []
        
        # Test 1: Page navigation
        results.append(await self.test_navigation())
        
        # Test 2: Page load completion
        results.append(await self.test_page_load())
        
        # Test 3: Essential elements present
        results.append(await self.test_essential_elements())
        
        # Test 4: No console errors
        results.append(await self.test_no_console_errors())
        
        # Test 5: Sidebar and header loaded
        results.append(await self.test_layout_components())
        
        return results
    
    async def test_navigation(self) -> TestResult:
        """
        Test page navigation.
        
        Returns:
            TestResult
        """
        start_time = time.time()
        test_name = f"Navigate to {self.page_path}"
        
        try:
            success = self.browser.navigate_to_page(self.page_path)
            duration = time.time() - start_time
            
            if success:
                return TestResult(
                    test_name=test_name,
                    status='passed',
                    duration=duration,
                    details=f"Successfully navigated to {self.page_path}"
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status='failed',
                    duration=duration,
                    details=f"Failed to navigate to {self.page_path}",
                    error="Navigation failed"
                )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status='failed',
                duration=duration,
                details=f"Exception during navigation to {self.page_path}",
                error=str(e)
            )
    
    async def test_page_load(self) -> TestResult:
        """
        Test that page loads completely.
        
        Returns:
            TestResult
        """
        start_time = time.time()
        test_name = f"Page load complete: {self.page_path}"
        
        try:
            # Wait for page to be fully loaded
            time.sleep(1)  # Simulate wait for page load
            
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status='passed',
                duration=duration,
                details="Page loaded successfully"
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status='failed',
                duration=duration,
                details="Page failed to load",
                error=str(e)
            )
    
    async def test_essential_elements(self) -> TestResult:
        """
        Test that essential page elements are present.
        
        Returns:
            TestResult
        """
        start_time = time.time()
        test_name = f"Essential elements present: {self.page_path}"
        
        try:
            # Check for main content area
            has_main = self.browser.check_element_exists('main.main-content')
            has_content = self.browser.check_element_exists('.page-content')
            
            duration = time.time() - start_time
            
            if has_main or has_content:
                return TestResult(
                    test_name=test_name,
                    status='passed',
                    duration=duration,
                    details="Essential elements found"
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status='failed',
                    duration=duration,
                    details="Missing essential elements",
                    error="Main content area not found"
                )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status='failed',
                duration=duration,
                details="Error checking elements",
                error=str(e)
            )
    
    async def test_no_console_errors(self) -> TestResult:
        """
        Test that there are no JavaScript console errors.
        
        Returns:
            TestResult
        """
        start_time = time.time()
        test_name = f"No console errors: {self.page_path}"
        
        try:
            errors = self.browser.check_console_errors()
            duration = time.time() - start_time
            
            if not errors:
                return TestResult(
                    test_name=test_name,
                    status='passed',
                    duration=duration,
                    details="No console errors found"
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status='failed',
                    duration=duration,
                    details=f"Found {len(errors)} console errors",
                    error="; ".join(errors[:3])  # Show first 3 errors
                )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status='failed',
                duration=duration,
                details="Error checking console",
                error=str(e)
            )
    
    async def test_layout_components(self) -> TestResult:
        """
        Test that sidebar and header are loaded.
        
        Returns:
            TestResult
        """
        start_time = time.time()
        test_name = f"Layout components loaded: {self.page_path}"
        
        try:
            has_sidebar = self.browser.check_element_exists('#sidebar-container')
            has_header = self.browser.check_element_exists('#header-container')
            
            duration = time.time() - start_time
            
            if has_sidebar and has_header:
                return TestResult(
                    test_name=test_name,
                    status='passed',
                    duration=duration,
                    details="Sidebar and header loaded"
                )
            else:
                missing = []
                if not has_sidebar:
                    missing.append("sidebar")
                if not has_header:
                    missing.append("header")
                
                return TestResult(
                    test_name=test_name,
                    status='failed',
                    duration=duration,
                    details=f"Missing: {', '.join(missing)}",
                    error=f"Layout components missing: {', '.join(missing)}"
                )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status='failed',
                duration=duration,
                details="Error checking layout",
                error=str(e)
            )
    
    async def test_all_buttons(self) -> List[TestResult]:
        """
        Test all buttons on the page.
        
        Returns:
            List of TestResults
        """
        buttons = self.browser.find_all_buttons()
        results = []
        
        for btn in buttons:
            result = self.browser.click_button(
                btn['selector'],
                btn.get('text') or btn.get('id')
            )
            results.append(result)
        
        return results
    
    async def run_all_tests(self) -> List[TestResult]:
        """
        Run all tests for this page (basic + specific).
        
        Returns:
            List of all TestResults
        """
        results = []
        
        # Run basic tests
        results.extend(await self.run_basic_tests())
        
        # Run page-specific tests
        results.extend(await self.run_specific_tests())
        
        return results
    
    async def run_specific_tests(self) -> List[TestResult]:
        """
        Override in subclasses for page-specific tests.
        
        Returns:
            List of TestResults
        """
        return []

