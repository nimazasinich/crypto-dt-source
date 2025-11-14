"""
Live Dashboard Tab - Real-time cryptocurrency price monitoring
Refactored from app.py with improved type hints and structure
"""

import pandas as pd
import logging
import traceback
from typing import Tuple

import database
import collectors
import utils

# Setup logging
logger = utils.setup_logging()

# Initialize database
db = database.get_database()


def get_live_dashboard(search_filter: str = "") -> pd.DataFrame:
    """
    Get live dashboard data with top 100 cryptocurrencies

    Args:
        search_filter: Search/filter text for cryptocurrencies (searches name and symbol)

    Returns:
        DataFrame with formatted cryptocurrency data including:
        - Rank, Name, Symbol
        - Price (USD), 24h Change (%)
        - Volume, Market Cap
    """
    try:
        logger.info("Fetching live dashboard data...")

        # Get latest prices from database
        prices = db.get_latest_prices(100)

        if not prices:
            logger.warning("No price data available")
            return _empty_dashboard_dataframe()

        # Convert to DataFrame with filtering
        df_data = []
        for price in prices:
            # Apply search filter if provided
            if search_filter and not _matches_filter(price, search_filter):
                continue

            df_data.append(_format_price_row(price))

        df = pd.DataFrame(df_data)

        if df.empty:
            logger.warning("No data matches filter criteria")
            return _empty_dashboard_dataframe()

        # Sort by rank
        df = df.sort_values('Rank')

        logger.info(f"Dashboard loaded with {len(df)} cryptocurrencies")
        return df

    except Exception as e:
        logger.error(f"Error in get_live_dashboard: {e}\n{traceback.format_exc()}")
        return pd.DataFrame({
            "Error": [f"Failed to load dashboard: {str(e)}"]
        })


def refresh_price_data() -> Tuple[pd.DataFrame, str]:
    """
    Manually trigger price data collection and refresh dashboard

    Returns:
        Tuple of (updated DataFrame, status message string)
    """
    try:
        logger.info("Manual refresh triggered...")

        # Collect fresh price data
        success, count = collectors.collect_price_data()

        if success:
            message = f"✅ Successfully refreshed! Collected {count} price records."
        else:
            message = f"⚠️ Refresh completed with warnings. Collected {count} records."

        # Return updated dashboard
        df = get_live_dashboard()

        return df, message

    except Exception as e:
        logger.error(f"Error in refresh_price_data: {e}")
        return get_live_dashboard(), f"❌ Refresh failed: {str(e)}"


# ==================== PRIVATE HELPER FUNCTIONS ====================


def _empty_dashboard_dataframe() -> pd.DataFrame:
    """Create empty DataFrame with proper column structure"""
    return pd.DataFrame({
        "Rank": [],
        "Name": [],
        "Symbol": [],
        "Price (USD)": [],
        "24h Change (%)": [],
        "Volume": [],
        "Market Cap": []
    })


def _matches_filter(price: dict, search_filter: str) -> bool:
    """
    Check if price record matches search filter

    Args:
        price: Price data dictionary
        search_filter: Search text

    Returns:
        True if matches, False otherwise
    """
    search_lower = search_filter.lower()
    name_lower = (price.get('name') or '').lower()
    symbol_lower = (price.get('symbol') or '').lower()

    return search_lower in name_lower or search_lower in symbol_lower


def _format_price_row(price: dict) -> dict:
    """
    Format price data for dashboard display

    Args:
        price: Raw price data dictionary

    Returns:
        Formatted dictionary with display-friendly values
    """
    return {
        "Rank": price.get('rank', 999),
        "Name": price.get('name', 'Unknown'),
        "Symbol": price.get('symbol', 'N/A').upper(),
        "Price (USD)": f"${price.get('price_usd', 0):,.2f}" if price.get('price_usd') else "N/A",
        "24h Change (%)": f"{price.get('percent_change_24h', 0):+.2f}%" if price.get('percent_change_24h') is not None else "N/A",
        "Volume": utils.format_number(price.get('volume_24h', 0)),
        "Market Cap": utils.format_number(price.get('market_cap', 0))
    }
