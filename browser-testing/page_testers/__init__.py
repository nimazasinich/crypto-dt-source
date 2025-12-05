"""
Page-specific test suites for all application pages.
"""
from .base_tester import BasePageTester
from .dashboard_tester import DashboardTester
from .market_tester import MarketTester
from .models_tester import ModelsTester
from .sentiment_tester import SentimentTester
from .ai_analyst_tester import AIAnalystTester
from .trading_assistant_tester import TradingAssistantTester
from .news_tester import NewsTester
from .providers_tester import ProvidersTester
from .diagnostics_tester import DiagnosticsTester
from .api_explorer_tester import APIExplorerTester
from .crypto_api_hub_tester import CryptoAPIHubTester
from .technical_analysis_tester import TechnicalAnalysisTester
from .data_sources_tester import DataSourcesTester
from .ai_tools_tester import AIToolsTester
from .help_tester import HelpTester
from .settings_tester import SettingsTester

__all__ = [
    'BasePageTester',
    'DashboardTester',
    'MarketTester',
    'ModelsTester',
    'SentimentTester',
    'AIAnalystTester',
    'TradingAssistantTester',
    'NewsTester',
    'ProvidersTester',
    'DiagnosticsTester',
    'APIExplorerTester',
    'CryptoAPIHubTester',
    'TechnicalAnalysisTester',
    'DataSourcesTester',
    'AIToolsTester',
    'HelpTester',
    'SettingsTester'
]

