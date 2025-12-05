"""
All page-specific testers in one file for efficiency.
Each class tests a specific page of the application.
"""
import time
from typing import List
from .base_tester import BasePageTester
from browser_testing.utils.browser_utils import TestResult


class MarketTester(BasePageTester):
    """Tests for the market page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_market_table())
        return results
    
    async def test_market_table(self) -> TestResult:
        start_time = time.time()
        has_table = self.browser.check_element_exists('.market-table')
        duration = time.time() - start_time
        return TestResult(
            test_name="Market: Table loaded",
            status='passed' if has_table else 'failed',
            duration=duration,
            details="Market table check"
        )


class ModelsTester(BasePageTester):
    """Tests for the AI models page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_models_list())
        return results
    
    async def test_models_list(self) -> TestResult:
        start_time = time.time()
        has_models = self.browser.check_element_exists('.models-list')
        duration = time.time() - start_time
        return TestResult(
            test_name="Models: List loaded",
            status='passed' if has_models else 'failed',
            duration=duration,
            details="Models list check"
        )


class SentimentTester(BasePageTester):
    """Tests for the sentiment analysis page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_tabs())
        results.append(await self.test_analyze_button())
        return results
    
    async def test_tabs(self) -> TestResult:
        start_time = time.time()
        has_tabs = self.browser.check_element_exists('.tabs')
        duration = time.time() - start_time
        return TestResult(
            test_name="Sentiment: Tabs present",
            status='passed' if has_tabs else 'failed',
            duration=duration,
            details="Sentiment tabs check"
        )
    
    async def test_analyze_button(self) -> TestResult:
        return self.browser.click_button('#analyze-asset', 'Analyze Asset')


class AIAnalystTester(BasePageTester):
    """Tests for the AI analyst page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_analyst_panel())
        return results
    
    async def test_analyst_panel(self) -> TestResult:
        start_time = time.time()
        has_panel = self.browser.check_element_exists('.analyst-panel')
        duration = time.time() - start_time
        return TestResult(
            test_name="AI Analyst: Panel loaded",
            status='passed' if has_panel else 'failed',
            duration=duration,
            details="AI analyst panel check"
        )


class TradingAssistantTester(BasePageTester):
    """Tests for the trading assistant page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_signals_button())
        return results
    
    async def test_signals_button(self) -> TestResult:
        return self.browser.click_button('#get-signals-btn', 'Get Signals')


class NewsTester(BasePageTester):
    """Tests for the news page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_news_feed())
        return results
    
    async def test_news_feed(self) -> TestResult:
        start_time = time.time()
        has_feed = self.browser.check_element_exists('.news-feed')
        duration = time.time() - start_time
        return TestResult(
            test_name="News: Feed loaded",
            status='passed' if has_feed else 'failed',
            duration=duration,
            details="News feed check"
        )


class ProvidersTester(BasePageTester):
    """Tests for the providers page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_providers_list())
        return results
    
    async def test_providers_list(self) -> TestResult:
        start_time = time.time()
        has_list = self.browser.check_element_exists('.providers-list')
        duration = time.time() - start_time
        return TestResult(
            test_name="Providers: List loaded",
            status='passed' if has_list else 'failed',
            duration=duration,
            details="Providers list check"
        )


class DiagnosticsTester(BasePageTester):
    """Tests for the diagnostics page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_diagnostics_panel())
        return results
    
    async def test_diagnostics_panel(self) -> TestResult:
        start_time = time.time()
        has_panel = self.browser.check_element_exists('.diagnostics-panel')
        duration = time.time() - start_time
        return TestResult(
            test_name="Diagnostics: Panel loaded",
            status='passed' if has_panel else 'failed',
            duration=duration,
            details="Diagnostics panel check"
        )


class APIExplorerTester(BasePageTester):
    """Tests for the API explorer page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_api_explorer())
        return results
    
    async def test_api_explorer(self) -> TestResult:
        start_time = time.time()
        has_explorer = self.browser.check_element_exists('.api-explorer')
        duration = time.time() - start_time
        return TestResult(
            test_name="API Explorer: Interface loaded",
            status='passed' if has_explorer else 'failed',
            duration=duration,
            details="API explorer check"
        )


class CryptoAPIHubTester(BasePageTester):
    """Tests for the crypto API hub page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_api_hub())
        return results
    
    async def test_api_hub(self) -> TestResult:
        start_time = time.time()
        has_hub = self.browser.check_element_exists('.api-hub')
        duration = time.time() - start_time
        return TestResult(
            test_name="Crypto API Hub: Hub loaded",
            status='passed' if has_hub else 'failed',
            duration=duration,
            details="API hub check"
        )


class TechnicalAnalysisTester(BasePageTester):
    """Tests for the technical analysis page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_chart_tools())
        return results
    
    async def test_chart_tools(self) -> TestResult:
        start_time = time.time()
        has_tools = self.browser.check_element_exists('.chart-tools')
        duration = time.time() - start_time
        return TestResult(
            test_name="Technical Analysis: Tools loaded",
            status='passed' if has_tools else 'failed',
            duration=duration,
            details="Chart tools check"
        )


class DataSourcesTester(BasePageTester):
    """Tests for the data sources page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_sources_list())
        return results
    
    async def test_sources_list(self) -> TestResult:
        start_time = time.time()
        has_list = self.browser.check_element_exists('.sources-list')
        duration = time.time() - start_time
        return TestResult(
            test_name="Data Sources: List loaded",
            status='passed' if has_list else 'failed',
            duration=duration,
            details="Data sources list check"
        )


class AIToolsTester(BasePageTester):
    """Tests for the AI tools page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_tools_panel())
        return results
    
    async def test_tools_panel(self) -> TestResult:
        start_time = time.time()
        has_panel = self.browser.check_element_exists('.tools-panel')
        duration = time.time() - start_time
        return TestResult(
            test_name="AI Tools: Panel loaded",
            status='passed' if has_panel else 'failed',
            duration=duration,
            details="AI tools panel check"
        )


class HelpTester(BasePageTester):
    """Tests for the help page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_help_content())
        return results
    
    async def test_help_content(self) -> TestResult:
        start_time = time.time()
        has_content = self.browser.check_element_exists('.help-content')
        duration = time.time() - start_time
        return TestResult(
            test_name="Help: Content loaded",
            status='passed' if has_content else 'failed',
            duration=duration,
            details="Help content check"
        )


class SettingsTester(BasePageTester):
    """Tests for the settings page"""
    async def run_specific_tests(self) -> List[TestResult]:
        results = []
        results.append(await self.test_settings_form())
        return results
    
    async def test_settings_form(self) -> TestResult:
        start_time = time.time()
        has_form = self.browser.check_element_exists('.settings-form')
        duration = time.time() - start_time
        return TestResult(
            test_name="Settings: Form loaded",
            status='passed' if has_form else 'failed',
            duration=duration,
            details="Settings form check"
        )

