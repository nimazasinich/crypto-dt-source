"""
UI module for Gradio dashboard components
Refactored from monolithic app.py into modular components
"""

from .dashboard_ai import get_ai_analysis_history, run_ai_analysis
from .dashboard_charts import export_chart, get_available_cryptocurrencies, get_historical_chart
from .dashboard_db import export_query_results, run_custom_query, run_predefined_query
from .dashboard_live import get_live_dashboard, refresh_price_data
from .dashboard_news import get_news_and_sentiment, get_sentiment_distribution, refresh_news_data
from .dashboard_status import get_collection_logs, get_data_sources_status, refresh_single_source
from .interface import create_gradio_interface

__all__ = [
    # Live Dashboard
    "get_live_dashboard",
    "refresh_price_data",
    # Charts
    "get_historical_chart",
    "get_available_cryptocurrencies",
    "export_chart",
    # News & Sentiment
    "get_news_and_sentiment",
    "refresh_news_data",
    "get_sentiment_distribution",
    # AI Analysis
    "run_ai_analysis",
    "get_ai_analysis_history",
    # Database
    "run_predefined_query",
    "run_custom_query",
    "export_query_results",
    # Status
    "get_data_sources_status",
    "refresh_single_source",
    "get_collection_logs",
    # Interface
    "create_gradio_interface",
]
