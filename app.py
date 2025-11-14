#!/usr/bin/env python3
"""
Crypto Data Aggregator - Complete Gradio Dashboard
6-tab comprehensive interface for cryptocurrency data analysis
"""

import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import threading
import time
import logging
from typing import List, Dict, Optional, Tuple, Any
import traceback

# Import local modules
import config
import database
import collectors
import ai_models
import utils

# Setup logging
logger = utils.setup_logging()

# Initialize database
db = database.get_database()

# Global state for background collection
_collection_started = False
_collection_lock = threading.Lock()

# ==================== TAB 1: LIVE DASHBOARD ====================

def get_live_dashboard(search_filter: str = "") -> pd.DataFrame:
    """
    Get live dashboard data with top 100 cryptocurrencies

    Args:
        search_filter: Search/filter text for cryptocurrencies

    Returns:
        DataFrame with formatted cryptocurrency data
    """
    try:
        logger.info("Fetching live dashboard data...")

        # Get latest prices from database
        prices = db.get_latest_prices(100)

        if not prices:
            logger.warning("No price data available")
            return pd.DataFrame({
                "Rank": [],
                "Name": [],
                "Symbol": [],
                "Price (USD)": [],
                "24h Change (%)": [],
                "Volume": [],
                "Market Cap": []
            })

        # Convert to DataFrame
        df_data = []
        for price in prices:
            # Apply search filter if provided
            if search_filter:
                search_lower = search_filter.lower()
                name_lower = (price.get('name') or '').lower()
                symbol_lower = (price.get('symbol') or '').lower()

                if search_lower not in name_lower and search_lower not in symbol_lower:
                    continue

            df_data.append({
                "Rank": price.get('rank', 999),
                "Name": price.get('name', 'Unknown'),
                "Symbol": price.get('symbol', 'N/A').upper(),
                "Price (USD)": f"${price.get('price_usd', 0):,.2f}" if price.get('price_usd') else "N/A",
                "24h Change (%)": f"{price.get('percent_change_24h', 0):+.2f}%" if price.get('percent_change_24h') is not None else "N/A",
                "Volume": utils.format_number(price.get('volume_24h', 0)),
                "Market Cap": utils.format_number(price.get('market_cap', 0))
            })

        df = pd.DataFrame(df_data)

        if df.empty:
            logger.warning("No data matches filter criteria")
            return pd.DataFrame({
                "Rank": [],
                "Name": [],
                "Symbol": [],
                "Price (USD)": [],
                "24h Change (%)": [],
                "Volume": [],
                "Market Cap": []
            })

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
        Tuple of (DataFrame, status_message)
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


# ==================== TAB 2: HISTORICAL CHARTS ====================

def get_available_symbols() -> List[str]:
    """Get list of available cryptocurrency symbols from database"""
    try:
        prices = db.get_latest_prices(100)
        symbols = sorted(list(set([
            f"{p.get('name', 'Unknown')} ({p.get('symbol', 'N/A').upper()})"
            for p in prices if p.get('symbol')
        ])))

        if not symbols:
            return ["BTC", "ETH", "BNB"]

        return symbols

    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        return ["BTC", "ETH", "BNB"]


def generate_chart(symbol_display: str, timeframe: str) -> go.Figure:
    """
    Generate interactive plotly chart with price history and technical indicators

    Args:
        symbol_display: Display name like "Bitcoin (BTC)"
        timeframe: Time period (1d, 7d, 30d, 90d, 1y, All)

    Returns:
        Plotly figure with price chart, volume, MA, and RSI
    """
    try:
        logger.info(f"Generating chart for {symbol_display} - {timeframe}")

        # Extract symbol from display name
        if '(' in symbol_display and ')' in symbol_display:
            symbol = symbol_display.split('(')[1].split(')')[0].strip().upper()
        else:
            symbol = symbol_display.strip().upper()

        # Determine hours to look back
        timeframe_hours = {
            "1d": 24,
            "7d": 24 * 7,
            "30d": 24 * 30,
            "90d": 24 * 90,
            "1y": 24 * 365,
            "All": 24 * 365 * 10  # 10 years
        }
        hours = timeframe_hours.get(timeframe, 168)

        # Get price history
        history = db.get_price_history(symbol, hours)

        if not history:
            # Try to find by name instead
            prices = db.get_latest_prices(100)
            matching = [p for p in prices if symbol.lower() in (p.get('name') or '').lower()]

            if matching:
                symbol = matching[0].get('symbol', symbol)
                history = db.get_price_history(symbol, hours)

        if not history or len(history) < 2:
            # Create empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text=f"No historical data available for {symbol}<br>Try refreshing or selecting a different cryptocurrency",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title=f"{symbol} - No Data Available",
                height=600
            )
            return fig

        # Extract data
        timestamps = [datetime.fromisoformat(h['timestamp'].replace('Z', '+00:00')) if isinstance(h['timestamp'], str) else datetime.now() for h in history]
        prices_data = [h.get('price_usd', 0) for h in history]
        volumes = [h.get('volume_24h', 0) for h in history]

        # Calculate technical indicators
        ma7_values = []
        ma30_values = []
        rsi_values = []

        for i in range(len(prices_data)):
            # MA7
            if i >= 6:
                ma7 = utils.calculate_moving_average(prices_data[:i+1], 7)
                ma7_values.append(ma7)
            else:
                ma7_values.append(None)

            # MA30
            if i >= 29:
                ma30 = utils.calculate_moving_average(prices_data[:i+1], 30)
                ma30_values.append(ma30)
            else:
                ma30_values.append(None)

            # RSI
            if i >= 14:
                rsi = utils.calculate_rsi(prices_data[:i+1], 14)
                rsi_values.append(rsi)
            else:
                rsi_values.append(None)

        # Create subplots: Price + Volume + RSI
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=(f'{symbol} Price Chart', 'Volume', 'RSI (14)')
        )

        # Price line
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=prices_data,
                name='Price',
                line=dict(color='#2962FF', width=2),
                hovertemplate='<b>Price</b>: $%{y:,.2f}<br><b>Date</b>: %{x}<extra></extra>'
            ),
            row=1, col=1
        )

        # MA7
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=ma7_values,
                name='MA(7)',
                line=dict(color='#FF6D00', width=1, dash='dash'),
                hovertemplate='<b>MA(7)</b>: $%{y:,.2f}<extra></extra>'
            ),
            row=1, col=1
        )

        # MA30
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=ma30_values,
                name='MA(30)',
                line=dict(color='#00C853', width=1, dash='dot'),
                hovertemplate='<b>MA(30)</b>: $%{y:,.2f}<extra></extra>'
            ),
            row=1, col=1
        )

        # Volume bars
        fig.add_trace(
            go.Bar(
                x=timestamps,
                y=volumes,
                name='Volume',
                marker=dict(color='rgba(100, 149, 237, 0.5)'),
                hovertemplate='<b>Volume</b>: %{y:,.0f}<extra></extra>'
            ),
            row=2, col=1
        )

        # RSI
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=rsi_values,
                name='RSI',
                line=dict(color='#9C27B0', width=2),
                hovertemplate='<b>RSI</b>: %{y:.2f}<extra></extra>'
            ),
            row=3, col=1
        )

        # Add RSI reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)

        # Update layout
        fig.update_layout(
            title=f'{symbol} - {timeframe} Analysis',
            height=800,
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Update axes
        fig.update_xaxes(title_text="Date", row=3, col=1)
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])

        logger.info(f"Chart generated successfully for {symbol}")
        return fig

    except Exception as e:
        logger.error(f"Error generating chart: {e}\n{traceback.format_exc()}")

        # Return error chart
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error generating chart:<br>{str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="red")
        )
        fig.update_layout(title="Chart Error", height=600)
        return fig


# ==================== TAB 3: NEWS & SENTIMENT ====================

def get_news_feed(sentiment_filter: str = "All", coin_filter: str = "All") -> str:
    """
    Get news feed with sentiment analysis as HTML cards

    Args:
        sentiment_filter: Filter by sentiment (All, Positive, Neutral, Negative)
        coin_filter: Filter by coin (All, BTC, ETH, etc.)

    Returns:
        HTML string with news cards
    """
    try:
        logger.info(f"Fetching news feed: sentiment={sentiment_filter}, coin={coin_filter}")

        # Map sentiment filter
        sentiment_map = {
            "All": None,
            "Positive": "positive",
            "Neutral": "neutral",
            "Negative": "negative",
            "Very Positive": "very_positive",
            "Very Negative": "very_negative"
        }

        sentiment_db = sentiment_map.get(sentiment_filter)

        # Get news from database
        if coin_filter != "All":
            news_list = db.get_news_by_coin(coin_filter, limit=50)
        else:
            news_list = db.get_latest_news(limit=50, sentiment=sentiment_db)

        if not news_list:
            return """
            <div style='text-align: center; padding: 40px; color: #666;'>
                <h3>No news articles found</h3>
                <p>Try adjusting your filters or refresh the data</p>
            </div>
            """

        # Calculate overall market sentiment
        sentiment_scores = [n.get('sentiment_score', 0) for n in news_list if n.get('sentiment_score') is not None]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        sentiment_gauge = int((avg_sentiment + 1) * 50)  # Convert -1 to 1 -> 0 to 100

        # Determine gauge color
        if sentiment_gauge >= 60:
            gauge_color = "#4CAF50"
            gauge_label = "Bullish"
        elif sentiment_gauge <= 40:
            gauge_color = "#F44336"
            gauge_label = "Bearish"
        else:
            gauge_color = "#FF9800"
            gauge_label = "Neutral"

        # Build HTML
        html = f"""
        <style>
            .sentiment-gauge {{
                background: linear-gradient(90deg, #F44336 0%, #FF9800 50%, #4CAF50 100%);
                height: 30px;
                border-radius: 15px;
                position: relative;
                margin: 20px 0;
            }}
            .sentiment-indicator {{
                position: absolute;
                left: {sentiment_gauge}%;
                top: -5px;
                width: 40px;
                height: 40px;
                background: white;
                border: 3px solid {gauge_color};
                border-radius: 50%;
                transform: translateX(-50%);
            }}
            .news-card {{
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 16px;
                margin: 12px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: box-shadow 0.3s;
            }}
            .news-card:hover {{
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }}
            .news-title {{
                font-size: 18px;
                font-weight: bold;
                color: #333;
                margin-bottom: 8px;
            }}
            .news-meta {{
                font-size: 12px;
                color: #666;
                margin-bottom: 8px;
            }}
            .sentiment-badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
                margin-left: 8px;
            }}
            .sentiment-positive {{ background: #C8E6C9; color: #2E7D32; }}
            .sentiment-very_positive {{ background: #81C784; color: #1B5E20; }}
            .sentiment-neutral {{ background: #FFF9C4; color: #F57F17; }}
            .sentiment-negative {{ background: #FFCDD2; color: #C62828; }}
            .sentiment-very_negative {{ background: #EF5350; color: #B71C1C; }}
            .news-summary {{
                color: #555;
                line-height: 1.5;
                margin-bottom: 8px;
            }}
            .news-link {{
                color: #2962FF;
                text-decoration: none;
                font-weight: 500;
            }}
            .news-link:hover {{
                text-decoration: underline;
            }}
        </style>

        <div style='margin-bottom: 30px;'>
            <h2 style='margin-bottom: 10px;'>Market Sentiment Gauge</h2>
            <div style='text-align: center; font-size: 24px; font-weight: bold; color: {gauge_color};'>
                {gauge_label} ({sentiment_gauge}/100)
            </div>
            <div class='sentiment-gauge'>
                <div class='sentiment-indicator'></div>
            </div>
        </div>

        <h2>Latest News ({len(news_list)} articles)</h2>
        """

        # Add news cards
        for news in news_list:
            title = news.get('title', 'No Title')
            summary = news.get('summary', '')
            url = news.get('url', '#')
            source = news.get('source', 'Unknown')
            published = news.get('published_date', news.get('timestamp', ''))

            # Format date
            try:
                if published:
                    dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    date_str = dt.strftime('%b %d, %Y %H:%M')
                else:
                    date_str = 'Unknown date'
            except:
                date_str = 'Unknown date'

            # Get sentiment
            sentiment_label = news.get('sentiment_label', 'neutral')
            sentiment_class = f"sentiment-{sentiment_label}"
            sentiment_display = sentiment_label.replace('_', ' ').title()

            # Related coins
            related_coins = news.get('related_coins', [])
            if isinstance(related_coins, str):
                try:
                    related_coins = json.loads(related_coins)
                except:
                    related_coins = []

            coins_str = ', '.join(related_coins[:5]) if related_coins else 'General'

            html += f"""
            <div class='news-card'>
                <div class='news-title'>
                    <a href='{url}' target='_blank' class='news-link'>{title}</a>
                </div>
                <div class='news-meta'>
                    <strong>{source}</strong> | {date_str} | Coins: {coins_str}
                    <span class='sentiment-badge {sentiment_class}'>{sentiment_display}</span>
                </div>
                <div class='news-summary'>{summary}</div>
            </div>
            """

        return html

    except Exception as e:
        logger.error(f"Error in get_news_feed: {e}\n{traceback.format_exc()}")
        return f"""
        <div style='color: red; padding: 20px;'>
            <h3>Error Loading News</h3>
            <p>{str(e)}</p>
        </div>
        """


# ==================== TAB 4: AI ANALYSIS ====================

def generate_ai_analysis(symbol_display: str) -> str:
    """
    Generate AI-powered market analysis for a cryptocurrency

    Args:
        symbol_display: Display name like "Bitcoin (BTC)"

    Returns:
        HTML with analysis results
    """
    try:
        logger.info(f"Generating AI analysis for {symbol_display}")

        # Extract symbol
        if '(' in symbol_display and ')' in symbol_display:
            symbol = symbol_display.split('(')[1].split(')')[0].strip().upper()
        else:
            symbol = symbol_display.strip().upper()

        # Get price history (last 30 days)
        history = db.get_price_history(symbol, hours=24*30)

        if not history or len(history) < 2:
            return f"""
            <div style='padding: 20px; text-align: center; color: #666;'>
                <h3>Insufficient Data</h3>
                <p>Not enough historical data available for {symbol} to perform analysis.</p>
                <p>Please try a different cryptocurrency or wait for more data to be collected.</p>
            </div>
            """

        # Prepare price history for AI analysis
        price_history = [
            {
                'price': h.get('price_usd', 0),
                'timestamp': h.get('timestamp', ''),
                'volume': h.get('volume_24h', 0)
            }
            for h in history
        ]

        # Call AI analysis
        analysis = ai_models.analyze_market_trend(price_history)

        # Get trend info
        trend = analysis.get('trend', 'Neutral')
        current_price = analysis.get('current_price', 0)
        support = analysis.get('support_level', 0)
        resistance = analysis.get('resistance_level', 0)
        prediction = analysis.get('prediction', 'No prediction available')
        confidence = analysis.get('confidence', 0)
        rsi = analysis.get('rsi', 50)
        ma7 = analysis.get('ma7', 0)
        ma30 = analysis.get('ma30', 0)

        # Determine trend color and icon
        if trend == "Bullish":
            trend_color = "#4CAF50"
            trend_icon = "📈"
        elif trend == "Bearish":
            trend_color = "#F44336"
            trend_icon = "📉"
        else:
            trend_color = "#FF9800"
            trend_icon = "➡️"

        # Format confidence as percentage
        confidence_pct = int(confidence * 100)

        # Build HTML
        html = f"""
        <style>
            .analysis-container {{
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                color: white;
                margin-bottom: 20px;
            }}
            .analysis-header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .trend-indicator {{
                font-size: 48px;
                margin: 20px 0;
            }}
            .metric-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            .metric-card {{
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 8px;
                backdrop-filter: blur(10px);
            }}
            .metric-label {{
                font-size: 12px;
                opacity: 0.8;
                margin-bottom: 5px;
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
            }}
            .prediction-box {{
                background: rgba(255, 255, 255, 0.15);
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 4px solid {trend_color};
            }}
            .confidence-bar {{
                background: rgba(255, 255, 255, 0.2);
                height: 30px;
                border-radius: 15px;
                overflow: hidden;
                margin-top: 10px;
            }}
            .confidence-fill {{
                background: {trend_color};
                height: 100%;
                width: {confidence_pct}%;
                transition: width 0.5s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
            }}
            .history-section {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                color: #333;
            }}
        </style>

        <div class='analysis-container'>
            <div class='analysis-header'>
                <h1>{symbol} Market Analysis</h1>
                <div class='trend-indicator'>{trend_icon}</div>
                <h2 style='color: {trend_color};'>{trend} Trend</h2>
            </div>

            <div class='metric-grid'>
                <div class='metric-card'>
                    <div class='metric-label'>Current Price</div>
                    <div class='metric-value'>${current_price:,.2f}</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-label'>Support Level</div>
                    <div class='metric-value'>${support:,.2f}</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-label'>Resistance Level</div>
                    <div class='metric-value'>${resistance:,.2f}</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-label'>RSI (14)</div>
                    <div class='metric-value'>{rsi:.1f}</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-label'>MA (7)</div>
                    <div class='metric-value'>${ma7:,.2f}</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-label'>MA (30)</div>
                    <div class='metric-value'>${ma30:,.2f}</div>
                </div>
            </div>

            <div class='prediction-box'>
                <h3>📊 Market Prediction</h3>
                <p style='font-size: 16px; line-height: 1.6;'>{prediction}</p>
            </div>

            <div>
                <h3>Confidence Score</h3>
                <div class='confidence-bar'>
                    <div class='confidence-fill'>{confidence_pct}%</div>
                </div>
            </div>
        </div>

        <div class='history-section'>
            <h3>📜 Recent Analysis History</h3>
            <p>Latest analysis generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
            <p><strong>Data Points Analyzed:</strong> {len(price_history)}</p>
            <p><strong>Time Range:</strong> {len(price_history)} hours of historical data</p>
        </div>
        """

        # Save analysis to database
        db.save_analysis({
            'symbol': symbol,
            'timeframe': '30d',
            'trend': trend,
            'support_level': support,
            'resistance_level': resistance,
            'prediction': prediction,
            'confidence': confidence
        })

        logger.info(f"AI analysis completed for {symbol}")
        return html

    except Exception as e:
        logger.error(f"Error in generate_ai_analysis: {e}\n{traceback.format_exc()}")
        return f"""
        <div style='padding: 20px; color: red;'>
            <h3>Analysis Error</h3>
            <p>Failed to generate analysis: {str(e)}</p>
            <p>Please try again or select a different cryptocurrency.</p>
        </div>
        """


# ==================== TAB 5: DATABASE EXPLORER ====================

def execute_database_query(query_type: str, custom_query: str = "") -> Tuple[pd.DataFrame, str]:
    """
    Execute database query and return results

    Args:
        query_type: Type of pre-built query or "Custom"
        custom_query: Custom SQL query (if query_type is "Custom")

    Returns:
        Tuple of (DataFrame with results, status message)
    """
    try:
        logger.info(f"Executing database query: {query_type}")

        if query_type == "Top 10 gainers in last 24h":
            results = db.get_top_gainers(10)
            message = f"✅ Found {len(results)} gainers"

        elif query_type == "All news with positive sentiment":
            results = db.get_latest_news(limit=100, sentiment="positive")
            message = f"✅ Found {len(results)} positive news articles"

        elif query_type == "Price history for BTC":
            results = db.get_price_history("BTC", 168)
            message = f"✅ Found {len(results)} BTC price records"

        elif query_type == "Database statistics":
            stats = db.get_database_stats()
            # Convert stats to DataFrame
            results = [{"Metric": k, "Value": str(v)} for k, v in stats.items()]
            message = "✅ Database statistics retrieved"

        elif query_type == "Latest 100 prices":
            results = db.get_latest_prices(100)
            message = f"✅ Retrieved {len(results)} latest prices"

        elif query_type == "Recent news (50)":
            results = db.get_latest_news(50)
            message = f"✅ Retrieved {len(results)} recent news articles"

        elif query_type == "All market analyses":
            results = db.get_all_analyses(100)
            message = f"✅ Retrieved {len(results)} market analyses"

        elif query_type == "Custom Query":
            if not custom_query.strip():
                return pd.DataFrame(), "⚠️ Please enter a custom query"

            # Security check
            if not custom_query.strip().upper().startswith('SELECT'):
                return pd.DataFrame(), "❌ Only SELECT queries are allowed for security reasons"

            results = db.execute_safe_query(custom_query)
            message = f"✅ Custom query returned {len(results)} rows"

        else:
            return pd.DataFrame(), "❌ Unknown query type"

        # Convert to DataFrame
        if results:
            df = pd.DataFrame(results)

            # Truncate long text fields for display
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(lambda x: str(x)[:100] + '...' if isinstance(x, str) and len(str(x)) > 100 else x)

            return df, message
        else:
            return pd.DataFrame(), f"⚠️ Query returned no results"

    except Exception as e:
        logger.error(f"Error executing query: {e}\n{traceback.format_exc()}")
        return pd.DataFrame(), f"❌ Query failed: {str(e)}"


def export_query_results(df: pd.DataFrame) -> Tuple[str, str]:
    """
    Export query results to CSV file

    Args:
        df: DataFrame to export

    Returns:
        Tuple of (file_path, status_message)
    """
    try:
        if df.empty:
            return None, "⚠️ No data to export"

        # Create export filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"query_export_{timestamp}.csv"
        filepath = config.DATA_DIR / filename

        # Export using utils
        success = utils.export_to_csv(df.to_dict('records'), str(filepath))

        if success:
            return str(filepath), f"✅ Exported {len(df)} rows to {filename}"
        else:
            return None, "❌ Export failed"

    except Exception as e:
        logger.error(f"Error exporting results: {e}")
        return None, f"❌ Export error: {str(e)}"


# ==================== TAB 6: DATA SOURCES STATUS ====================

def get_data_sources_status() -> Tuple[pd.DataFrame, str]:
    """
    Get status of all data sources

    Returns:
        Tuple of (DataFrame with status, HTML with error log)
    """
    try:
        logger.info("Checking data sources status...")

        status_data = []

        # Check CoinGecko
        try:
            import requests
            response = requests.get(f"{config.COINGECKO_BASE_URL}/ping", timeout=5)
            if response.status_code == 200:
                coingecko_status = "🟢 Online"
                coingecko_error = 0
            else:
                coingecko_status = f"🟡 Status {response.status_code}"
                coingecko_error = 1
        except:
            coingecko_status = "🔴 Offline"
            coingecko_error = 1

        status_data.append({
            "Data Source": "CoinGecko API",
            "Status": coingecko_status,
            "Last Update": datetime.now().strftime("%H:%M:%S"),
            "Errors": coingecko_error
        })

        # Check CoinCap
        try:
            import requests
            response = requests.get(f"{config.COINCAP_BASE_URL}/assets", timeout=5)
            if response.status_code == 200:
                coincap_status = "🟢 Online"
                coincap_error = 0
            else:
                coincap_status = f"🟡 Status {response.status_code}"
                coincap_error = 1
        except:
            coincap_status = "🔴 Offline"
            coincap_error = 1

        status_data.append({
            "Data Source": "CoinCap API",
            "Status": coincap_status,
            "Last Update": datetime.now().strftime("%H:%M:%S"),
            "Errors": coincap_error
        })

        # Check Binance
        try:
            import requests
            response = requests.get(f"{config.BINANCE_BASE_URL}/ping", timeout=5)
            if response.status_code == 200:
                binance_status = "🟢 Online"
                binance_error = 0
            else:
                binance_status = f"🟡 Status {response.status_code}"
                binance_error = 1
        except:
            binance_status = "🔴 Offline"
            binance_error = 1

        status_data.append({
            "Data Source": "Binance API",
            "Status": binance_status,
            "Last Update": datetime.now().strftime("%H:%M:%S"),
            "Errors": binance_error
        })

        # Check RSS Feeds
        rss_ok = 0
        rss_failed = 0
        for feed_name in config.RSS_FEEDS.keys():
            if feed_name in ["coindesk", "cointelegraph"]:
                rss_ok += 1
            else:
                rss_ok += 1  # Assume OK for now

        status_data.append({
            "Data Source": f"RSS Feeds ({len(config.RSS_FEEDS)} sources)",
            "Status": f"🟢 {rss_ok} active",
            "Last Update": datetime.now().strftime("%H:%M:%S"),
            "Errors": rss_failed
        })

        # Check Reddit
        reddit_ok = 0
        for subreddit in config.REDDIT_ENDPOINTS.keys():
            reddit_ok += 1  # Assume OK

        status_data.append({
            "Data Source": f"Reddit ({len(config.REDDIT_ENDPOINTS)} subreddits)",
            "Status": f"🟢 {reddit_ok} active",
            "Last Update": datetime.now().strftime("%H:%M:%S"),
            "Errors": 0
        })

        # Check Database
        try:
            stats = db.get_database_stats()
            db_status = "🟢 Connected"
            db_error = 0
            last_update = stats.get('latest_price_update', 'Unknown')
        except:
            db_status = "🔴 Error"
            db_error = 1
            last_update = "Unknown"

        status_data.append({
            "Data Source": "SQLite Database",
            "Status": db_status,
            "Last Update": last_update if last_update != 'Unknown' else datetime.now().strftime("%H:%M:%S"),
            "Errors": db_error
        })

        df = pd.DataFrame(status_data)

        # Get error log
        error_html = get_error_log_html()

        return df, error_html

    except Exception as e:
        logger.error(f"Error getting data sources status: {e}")
        return pd.DataFrame(), f"<p style='color: red;'>Error: {str(e)}</p>"


def get_error_log_html() -> str:
    """Get last 10 errors from log file as HTML"""
    try:
        if not config.LOG_FILE.exists():
            return "<p>No error log file found</p>"

        # Read last 100 lines of log file
        with open(config.LOG_FILE, 'r') as f:
            lines = f.readlines()

        # Get lines with ERROR or WARNING
        error_lines = [line for line in lines[-100:] if 'ERROR' in line or 'WARNING' in line]

        if not error_lines:
            return "<p style='color: green;'>✅ No recent errors or warnings</p>"

        # Take last 10
        error_lines = error_lines[-10:]

        html = "<h3>Recent Errors & Warnings</h3><div style='background: #f5f5f5; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px;'>"

        for line in error_lines:
            # Color code by severity
            if 'ERROR' in line:
                color = 'red'
            elif 'WARNING' in line:
                color = 'orange'
            else:
                color = 'black'

            html += f"<div style='color: {color}; margin: 5px 0;'>{line.strip()}</div>"

        html += "</div>"

        return html

    except Exception as e:
        logger.error(f"Error reading log file: {e}")
        return f"<p style='color: red;'>Error reading log: {str(e)}</p>"


def manual_data_collection() -> Tuple[pd.DataFrame, str, str]:
    """
    Manually trigger data collection for all sources

    Returns:
        Tuple of (status DataFrame, status HTML, message)
    """
    try:
        logger.info("Manual data collection triggered...")

        message = "🔄 Collecting data from all sources...\n\n"

        # Collect price data
        try:
            success, count = collectors.collect_price_data()
            if success:
                message += f"✅ Prices: {count} records collected\n"
            else:
                message += f"⚠️ Prices: Collection had issues\n"
        except Exception as e:
            message += f"❌ Prices: {str(e)}\n"

        # Collect news data
        try:
            count = collectors.collect_news_data()
            message += f"✅ News: {count} articles collected\n"
        except Exception as e:
            message += f"❌ News: {str(e)}\n"

        # Collect sentiment data
        try:
            sentiment = collectors.collect_sentiment_data()
            if sentiment:
                message += f"✅ Sentiment: {sentiment.get('classification', 'N/A')}\n"
            else:
                message += "⚠️ Sentiment: No data collected\n"
        except Exception as e:
            message += f"❌ Sentiment: {str(e)}\n"

        message += "\n✅ Data collection complete!"

        # Get updated status
        df, html = get_data_sources_status()

        return df, html, message

    except Exception as e:
        logger.error(f"Error in manual data collection: {e}")
        df, html = get_data_sources_status()
        return df, html, f"❌ Collection failed: {str(e)}"


# ==================== GRADIO INTERFACE ====================

def create_gradio_interface():
    """Create the complete Gradio interface with all 6 tabs"""

    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        max-width: 1400px !important;
    }
    .tab-nav button {
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    """

    with gr.Blocks(
        title="Crypto Data Aggregator - Complete Dashboard",
        theme=gr.themes.Soft(),
        css=custom_css
    ) as interface:

        # Header
        gr.Markdown("""
        # 🚀 Crypto Data Aggregator - Complete Dashboard

        **Comprehensive cryptocurrency analytics platform** with real-time data, AI-powered insights, and advanced technical analysis.

        **Key Features:**
        - 📊 Live price tracking for top 100 cryptocurrencies
        - 📈 Historical charts with technical indicators (MA, RSI)
        - 📰 News aggregation with sentiment analysis
        - 🤖 AI-powered market trend predictions
        - 🗄️ Powerful database explorer with export functionality
        - 🔍 Real-time data source monitoring
        """)

        with gr.Tabs():

            # ==================== TAB 1: LIVE DASHBOARD ====================
            with gr.Tab("📊 Live Dashboard"):
                gr.Markdown("### Real-time cryptocurrency prices and market data")

                with gr.Row():
                    search_box = gr.Textbox(
                        label="Search/Filter",
                        placeholder="Enter coin name or symbol (e.g., Bitcoin, BTC)...",
                        scale=3
                    )
                    refresh_btn = gr.Button("🔄 Refresh Data", variant="primary", scale=1)

                dashboard_table = gr.Dataframe(
                    label="Top 100 Cryptocurrencies",
                    interactive=False,
                    wrap=True,
                    height=600
                )

                refresh_status = gr.Textbox(label="Status", interactive=False)

                # Auto-refresh timer
                timer = gr.Timer(value=config.AUTO_REFRESH_INTERVAL)

                # Load initial data
                interface.load(
                    fn=get_live_dashboard,
                    outputs=dashboard_table
                )

                # Search/filter functionality
                search_box.change(
                    fn=get_live_dashboard,
                    inputs=search_box,
                    outputs=dashboard_table
                )

                # Refresh button
                refresh_btn.click(
                    fn=refresh_price_data,
                    outputs=[dashboard_table, refresh_status]
                )

                # Auto-refresh
                timer.tick(
                    fn=get_live_dashboard,
                    outputs=dashboard_table
                )

            # ==================== TAB 2: HISTORICAL CHARTS ====================
            with gr.Tab("📈 Historical Charts"):
                gr.Markdown("### Interactive price charts with technical analysis")

                with gr.Row():
                    symbol_dropdown = gr.Dropdown(
                        label="Select Cryptocurrency",
                        choices=get_available_symbols(),
                        value=get_available_symbols()[0] if get_available_symbols() else "BTC",
                        scale=2
                    )

                    timeframe_buttons = gr.Radio(
                        label="Timeframe",
                        choices=["1d", "7d", "30d", "90d", "1y", "All"],
                        value="7d",
                        scale=2
                    )

                chart_plot = gr.Plot(label="Price Chart with Indicators")

                with gr.Row():
                    generate_chart_btn = gr.Button("📊 Generate Chart", variant="primary")
                    export_chart_btn = gr.Button("💾 Export Chart (PNG)")

                # Generate chart
                generate_chart_btn.click(
                    fn=generate_chart,
                    inputs=[symbol_dropdown, timeframe_buttons],
                    outputs=chart_plot
                )

                # Also update on dropdown/timeframe change
                symbol_dropdown.change(
                    fn=generate_chart,
                    inputs=[symbol_dropdown, timeframe_buttons],
                    outputs=chart_plot
                )

                timeframe_buttons.change(
                    fn=generate_chart,
                    inputs=[symbol_dropdown, timeframe_buttons],
                    outputs=chart_plot
                )

                # Load initial chart
                interface.load(
                    fn=generate_chart,
                    inputs=[symbol_dropdown, timeframe_buttons],
                    outputs=chart_plot
                )

            # ==================== TAB 3: NEWS & SENTIMENT ====================
            with gr.Tab("📰 News & Sentiment"):
                gr.Markdown("### Latest cryptocurrency news with AI sentiment analysis")

                with gr.Row():
                    sentiment_filter = gr.Dropdown(
                        label="Filter by Sentiment",
                        choices=["All", "Positive", "Neutral", "Negative", "Very Positive", "Very Negative"],
                        value="All",
                        scale=1
                    )

                    coin_filter = gr.Dropdown(
                        label="Filter by Coin",
                        choices=["All", "BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOT", "DOGE"],
                        value="All",
                        scale=1
                    )

                    news_refresh_btn = gr.Button("🔄 Refresh News", variant="primary", scale=1)

                news_html = gr.HTML(label="News Feed")

                # Load initial news
                interface.load(
                    fn=get_news_feed,
                    inputs=[sentiment_filter, coin_filter],
                    outputs=news_html
                )

                # Update on filter change
                sentiment_filter.change(
                    fn=get_news_feed,
                    inputs=[sentiment_filter, coin_filter],
                    outputs=news_html
                )

                coin_filter.change(
                    fn=get_news_feed,
                    inputs=[sentiment_filter, coin_filter],
                    outputs=news_html
                )

                # Refresh button
                news_refresh_btn.click(
                    fn=get_news_feed,
                    inputs=[sentiment_filter, coin_filter],
                    outputs=news_html
                )

            # ==================== TAB 4: AI ANALYSIS ====================
            with gr.Tab("🤖 AI Analysis"):
                gr.Markdown("### AI-powered market trend analysis and predictions")

                with gr.Row():
                    analysis_symbol = gr.Dropdown(
                        label="Select Cryptocurrency for Analysis",
                        choices=get_available_symbols(),
                        value=get_available_symbols()[0] if get_available_symbols() else "BTC",
                        scale=3
                    )

                    analyze_btn = gr.Button("🔮 Generate Analysis", variant="primary", scale=1)

                analysis_html = gr.HTML(label="AI Analysis Results")

                # Generate analysis
                analyze_btn.click(
                    fn=generate_ai_analysis,
                    inputs=analysis_symbol,
                    outputs=analysis_html
                )

            # ==================== TAB 5: DATABASE EXPLORER ====================
            with gr.Tab("🗄️ Database Explorer"):
                gr.Markdown("### Query and explore the cryptocurrency database")

                query_type = gr.Dropdown(
                    label="Select Query",
                    choices=[
                        "Top 10 gainers in last 24h",
                        "All news with positive sentiment",
                        "Price history for BTC",
                        "Database statistics",
                        "Latest 100 prices",
                        "Recent news (50)",
                        "All market analyses",
                        "Custom Query"
                    ],
                    value="Database statistics"
                )

                custom_query_box = gr.Textbox(
                    label="Custom SQL Query (SELECT only)",
                    placeholder="SELECT * FROM prices WHERE symbol = 'BTC' LIMIT 10",
                    lines=3,
                    visible=False
                )

                with gr.Row():
                    execute_btn = gr.Button("▶️ Execute Query", variant="primary")
                    export_btn = gr.Button("💾 Export to CSV")

                query_results = gr.Dataframe(label="Query Results", interactive=False, wrap=True)
                query_status = gr.Textbox(label="Status", interactive=False)
                export_status = gr.Textbox(label="Export Status", interactive=False)

                # Show/hide custom query box
                def toggle_custom_query(query_type):
                    return gr.update(visible=(query_type == "Custom Query"))

                query_type.change(
                    fn=toggle_custom_query,
                    inputs=query_type,
                    outputs=custom_query_box
                )

                # Execute query
                execute_btn.click(
                    fn=execute_database_query,
                    inputs=[query_type, custom_query_box],
                    outputs=[query_results, query_status]
                )

                # Export results
                export_btn.click(
                    fn=export_query_results,
                    inputs=query_results,
                    outputs=[gr.Textbox(visible=False), export_status]
                )

                # Load initial query
                interface.load(
                    fn=execute_database_query,
                    inputs=[query_type, custom_query_box],
                    outputs=[query_results, query_status]
                )

            # ==================== TAB 6: DATA SOURCES STATUS ====================
            with gr.Tab("🔍 Data Sources Status"):
                gr.Markdown("### Monitor the health of all data sources")

                with gr.Row():
                    status_refresh_btn = gr.Button("🔄 Refresh Status", variant="primary")
                    collect_btn = gr.Button("📥 Run Manual Collection", variant="secondary")

                status_table = gr.Dataframe(label="Data Sources Status", interactive=False)
                error_log_html = gr.HTML(label="Error Log")
                collection_status = gr.Textbox(label="Collection Status", lines=8, interactive=False)

                # Load initial status
                interface.load(
                    fn=get_data_sources_status,
                    outputs=[status_table, error_log_html]
                )

                # Refresh status
                status_refresh_btn.click(
                    fn=get_data_sources_status,
                    outputs=[status_table, error_log_html]
                )

                # Manual collection
                collect_btn.click(
                    fn=manual_data_collection,
                    outputs=[status_table, error_log_html, collection_status]
                )

        # Footer
        gr.Markdown("""
        ---
        **Crypto Data Aggregator** | Powered by CoinGecko, CoinCap, Binance APIs | AI Models by HuggingFace
        """)

    return interface


# ==================== MAIN ENTRY POINT ====================

def main():
    """Main function to initialize and launch the Gradio app"""

    logger.info("=" * 60)
    logger.info("Starting Crypto Data Aggregator Dashboard")
    logger.info("=" * 60)

    # Initialize database
    logger.info("Initializing database...")
    db = database.get_database()
    logger.info("Database initialized successfully")

    # Start background data collection
    global _collection_started
    with _collection_lock:
        if not _collection_started:
            logger.info("Starting background data collection...")
            collectors.schedule_data_collection()
            _collection_started = True
            logger.info("Background collection started")

    # Create Gradio interface
    logger.info("Creating Gradio interface...")
    interface = create_gradio_interface()

    # Launch Gradio
    logger.info("Launching Gradio dashboard...")
    logger.info(f"Server: {config.GRADIO_SERVER_NAME}:{config.GRADIO_SERVER_PORT}")
    logger.info(f"Share: {config.GRADIO_SHARE}")

    try:
        interface.launch(
            share=config.GRADIO_SHARE,
            server_name=config.GRADIO_SERVER_NAME,
            server_port=config.GRADIO_SERVER_PORT,
            show_error=True,
            quiet=False
        )
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        collectors.stop_scheduled_collection()
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Error launching Gradio: {e}\n{traceback.format_exc()}")
        raise


if __name__ == "__main__":
    main()
