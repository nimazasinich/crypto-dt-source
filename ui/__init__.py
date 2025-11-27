"""
UI module for Gradio dashboard components
Refactored from monolithic app.py into modular components
"""

from .dashboard_live import get_live_dashboard, refresh_price_data
from .dashboard_charts import get_historical_chart, get_available_cryptocurrencies, export_chart
from .dashboard_news import get_news_and_sentiment, refresh_news_data, get_sentiment_distribution
from .dashboard_ai import run_ai_analysis, get_ai_analysis_history
from .dashboard_db import run_predefined_query, run_custom_query, export_query_results
from .dashboard_status import get_data_sources_status, refresh_single_source, get_collection_logs
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
