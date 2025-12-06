"""
Main test runner orchestrating all tests.
Runs comprehensive browser automation tests for all pages.
"""
import asyncio
import sys
from typing import List
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from browser_testing.config import detect_environment
from browser_testing.utils.browser_utils import BrowserTester, TestResult
from browser_testing.utils.api_tester import APITester
from browser_testing.utils.websocket_tester import WebSocketTester
from browser_testing.utils.report_generator import ReportGenerator
from browser_testing.page_testers import (
    DashboardTester,
    MarketTester,
    ModelsTester,
    SentimentTester,
    AIAnalystTester,
    TradingAssistantTester,
    NewsTester,
    ProvidersTester,
    DiagnosticsTester,
    APIExplorerTester,
    CryptoAPIHubTester,
    TechnicalAnalysisTester,
    DataSourcesTester,
    AIToolsTester,
    HelpTester,
    SettingsTester
)


class TestRunner:
    """
    Main test runner that orchestrates all browser automation tests.
    """
    
    def __init__(self):
        """Initialize test runner with environment detection"""
        self.config = detect_environment()
        self.browser = BrowserTester(self.config)
        self.api_tester = APITester(self.config.base_url)
        self.ws_tester = WebSocketTester(self.config.websocket_url) if self.config.websocket_enabled else None
        self.all_results: List[TestResult] = []
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print("=" * 70)
        print("🚀 CRYPTO MONITOR - BROWSER AUTOMATION TEST SUITE")
        print("=" * 70)
        print(f"Environment: {self.config.environment.upper()}")
        print(f"Base URL: {self.config.base_url}")
        print(f"WebSocket: {'Enabled' if self.config.websocket_enabled else 'Disabled'}")
        print("=" * 70)
        
        # Phase 1: API Health Check
        print("\n📡 Phase 1: API Health Check")
        print("-" * 70)
        api_results = await self.api_tester.test_all_endpoints()
        self.all_results.extend(api_results)
        
        passed = sum(1 for r in api_results if r.status == 'passed')
        failed = sum(1 for r in api_results if r.status == 'failed')
        print(f"  API Tests: ✅ {passed} passed | ❌ {failed} failed")
        
        # Phase 2: WebSocket Tests (if enabled)
        if self.ws_tester:
            print("\n🔌 Phase 2: WebSocket Tests")
            print("-" * 70)
            ws_result = await self.ws_tester.test_connection()
            self.all_results.append(ws_result)
            
            if ws_result.status == 'passed':
                print(f"  ✓ {ws_result.test_name}: {ws_result.details}")
            else:
                print(f"  ✗ {ws_result.test_name}: {ws_result.error}")
        
        # Phase 3: Page Tests
        print("\n📄 Phase 3: Page-by-Page Tests")
        print("-" * 70)
        
        page_testers = [
            ('Dashboard', DashboardTester(self.browser, '/')),
            ('Market', MarketTester(self.browser, '/market')),
            ('Models', ModelsTester(self.browser, '/models')),
            ('Sentiment', SentimentTester(self.browser, '/sentiment')),
            ('AI Analyst', AIAnalystTester(self.browser, '/ai-analyst')),
            ('Trading Assistant', TradingAssistantTester(self.browser, '/trading-assistant')),
            ('News', NewsTester(self.browser, '/news')),
            ('Providers', ProvidersTester(self.browser, '/providers')),
            ('Diagnostics', DiagnosticsTester(self.browser, '/diagnostics')),
            ('API Explorer', APIExplorerTester(self.browser, '/api-explorer')),
            ('Crypto API Hub', CryptoAPIHubTester(self.browser, '/crypto-api-hub')),
            ('Technical Analysis', TechnicalAnalysisTester(self.browser, '/technical-analysis')),
            ('Data Sources', DataSourcesTester(self.browser, '/data-sources')),
            ('AI Tools', AIToolsTester(self.browser, '/ai-tools')),
            ('Help', HelpTester(self.browser, '/help')),
            ('Settings', SettingsTester(self.browser, '/settings')),
        ]
        
        for page_name, tester in page_testers:
            print(f"\n  Testing: {page_name} ({tester.page_path})")
            results = await tester.run_all_tests()
            self.all_results.extend(results)
            
            # Print summary for this page
            passed = sum(1 for r in results if r.status == 'passed')
            failed = sum(1 for r in results if r.status == 'failed')
            skipped = sum(1 for r in results if r.status == 'skipped')
            
            status_str = f"✅ {passed} passed"
            if failed > 0:
                status_str += f" | ❌ {failed} failed"
            if skipped > 0:
                status_str += f" | ⏭️  {skipped} skipped"
            
            print(f"    {status_str}")
        
        # Phase 4: Generate Report
        print("\n📊 Phase 4: Generating Reports")
        print("-" * 70)
        report_gen = ReportGenerator(self.all_results, self.config)
        json_path = report_gen.generate_json_report()
        html_path = report_gen.generate_html_report()
        
        # Print final summary
        self.print_summary()
        
        print("\n" + "=" * 70)
        print("✨ Test suite completed!")
        print("=" * 70)
        
        return self.all_results
    
    def print_summary(self):
        """Print comprehensive test summary"""
        total = len(self.all_results)
        passed = sum(1 for r in self.all_results if r.status == 'passed')
        failed = sum(1 for r in self.all_results if r.status == 'failed')
        skipped = sum(1 for r in self.all_results if r.status == 'skipped')
        
        total_duration = sum(r.duration for r in self.all_results)
        
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests:     {total}")
        print(f"✅ Passed:        {passed} ({passed/total*100:.1f}%)")
        print(f"❌ Failed:        {failed} ({failed/total*100:.1f}%)")
        print(f"⏭️  Skipped:       {skipped} ({skipped/total*100:.1f}%)")
        print(f"⏱️  Duration:      {total_duration:.2f}s")
        print("=" * 70)
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.all_results:
                if result.status == 'failed':
                    print(f"  - {result.test_name}")
                    if result.error:
                        print(f"    Error: {result.error}")
        
        # Success rate indicator
        pass_rate = (passed / total * 100) if total > 0 else 0
        if pass_rate >= 90:
            print("\n🎉 Excellent! Pass rate >= 90%")
        elif pass_rate >= 75:
            print("\n👍 Good! Pass rate >= 75%")
        elif pass_rate >= 50:
            print("\n⚠️  Warning: Pass rate < 75%")
        else:
            print("\n🚨 Critical: Pass rate < 50%")


async def main():
    """Main entry point"""
    try:
        runner = TestRunner()
        await runner.run_all_tests()
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Test suite interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

