"""
Cryptocurrency API Monitor - Gradio Application
Production-ready monitoring dashboard for Hugging Face Spaces
"""

import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import asyncio
import time
import logging
from typing import List, Dict, Optional
import json

# Import local modules
from config import config
from monitor import APIMonitor, HealthStatus, HealthCheckResult
from database import Database
from scheduler import BackgroundScheduler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
db = Database()
monitor = APIMonitor(config)
scheduler = BackgroundScheduler(monitor, db, interval_minutes=5)

# Global state for UI
current_results = []
last_check_time = None


# =============================================================================
# TAB 1: Real-Time Dashboard
# =============================================================================

def refresh_dashboard(category_filter="All", status_filter="All", tier_filter="All"):
    """Refresh the main dashboard with filters"""
    global current_results, last_check_time

    try:
        # Run health checks
        logger.info("Running health checks...")
        current_results = asyncio.run(monitor.check_all())
        last_check_time = datetime.now()

        # Save to database
        db.save_health_checks(current_results)

        # Apply filters
        filtered_results = current_results

        if category_filter != "All":
            filtered_results = [r for r in filtered_results if r.category == category_filter]

        if status_filter != "All":
            filtered_results = [r for r in filtered_results if r.status.value == status_filter.lower()]

        if tier_filter != "All":
            tier_num = int(tier_filter.split()[1])
            tier_resources = config.get_by_tier(tier_num)
            tier_names = [r['name'] for r in tier_resources]
            filtered_results = [r for r in filtered_results if r.provider_name in tier_names]

        # Create DataFrame
        df_data = []
        for result in filtered_results:
            df_data.append({
                'Status': f"{result.get_badge()} {result.status.value.upper()}",
                'Provider': result.provider_name,
                'Category': result.category,
                'Response Time': f"{result.response_time:.0f} ms",
                'Last Check': datetime.fromtimestamp(result.timestamp).strftime('%H:%M:%S'),
                'Code': result.status_code or 'N/A'
            })

        df = pd.DataFrame(df_data)

        # Calculate summary stats
        stats = monitor.get_summary_stats(current_results)

        # Build summary cards HTML
        summary_html = f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white;">
                <h3 style="margin: 0;">📊 Total APIs</h3>
                <p style="font-size: 32px; margin: 10px 0 0 0; font-weight: bold;">{stats['total']}</p>
            </div>
            <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 20px; border-radius: 10px; color: white;">
                <h3 style="margin: 0;">✅ Online %</h3>
                <p style="font-size: 32px; margin: 10px 0 0 0; font-weight: bold;">{stats['online_percentage']}%</p>
            </div>
            <div style="background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%); padding: 20px; border-radius: 10px; color: white;">
                <h3 style="margin: 0;">⚠️ Critical Issues</h3>
                <p style="font-size: 32px; margin: 10px 0 0 0; font-weight: bold;">{stats['critical_issues']}</p>
            </div>
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; color: white;">
                <h3 style="margin: 0;">⚡ Avg Response</h3>
                <p style="font-size: 32px; margin: 10px 0 0 0; font-weight: bold;">{stats['avg_response_time']:.0f} ms</p>
            </div>
        </div>
        <p style="text-align: center; color: #666;">Last updated: {last_check_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        """

        return df, summary_html

    except Exception as e:
        logger.error(f"Error refreshing dashboard: {e}")
        return pd.DataFrame(), f"<p style='color: red;'>Error: {str(e)}</p>"


def export_current_status():
    """Export current status to CSV"""
    global current_results

    if not current_results:
        return None

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"api_status_{timestamp}.csv"
        filepath = f"data/{filename}"

        df_data = []
        for result in current_results:
            df_data.append({
                'Provider': result.provider_name,
                'Category': result.category,
                'Status': result.status.value,
                'Response_Time_ms': result.response_time,
                'Status_Code': result.status_code,
                'Error': result.error_message or '',
                'Timestamp': datetime.fromtimestamp(result.timestamp).isoformat()
            })

        df = pd.DataFrame(df_data)
        df.to_csv(filepath, index=False)

        return filepath

    except Exception as e:
        logger.error(f"Error exporting: {e}")
        return None


# =============================================================================
# TAB 2: Category View
# =============================================================================

def get_category_overview():
    """Get overview of all categories"""
    global current_results

    if not current_results:
        return "No data available. Please refresh the dashboard first."

    category_stats = monitor.get_category_stats(current_results)

    html_output = "<div style='padding: 20px;'>"

    for category, stats in category_stats.items():
        online_pct = stats['online_percentage']

        # Color based on health
        if online_pct >= 80:
            color = "#4CAF50"
        elif online_pct >= 50:
            color = "#FF9800"
        else:
            color = "#F44336"

        html_output += f"""
        <div style="margin-bottom: 30px; border: 2px solid {color}; border-radius: 10px; padding: 20px; background: #f9f9f9;">
            <h2 style="margin-top: 0; color: {color};">📁 {category}</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                <div>
                    <strong>Total:</strong> {stats['total']}
                </div>
                <div>
                    <strong>🟢 Online:</strong> {stats['online']}
                </div>
                <div>
                    <strong>🟡 Degraded:</strong> {stats['degraded']}
                </div>
                <div>
                    <strong>🔴 Offline:</strong> {stats['offline']}
                </div>
                <div>
                    <strong>Availability:</strong> {online_pct}%
                </div>
                <div>
                    <strong>Avg Response:</strong> {stats['avg_response_time']:.0f} ms
                </div>
            </div>
            <div style="margin-top: 15px; background: #e0e0e0; border-radius: 5px; height: 25px; overflow: hidden;">
                <div style="background: {color}; height: 100%; width: {online_pct}%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                    {online_pct}%
                </div>
            </div>
        </div>
        """

    html_output += "</div>"

    return html_output


def get_category_chart():
    """Create category availability chart"""
    global current_results

    if not current_results:
        return go.Figure()

    category_stats = monitor.get_category_stats(current_results)

    categories = list(category_stats.keys())
    online_pcts = [stats['online_percentage'] for stats in category_stats.values()]
    avg_times = [stats['avg_response_time'] for stats in category_stats.values()]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Availability %',
        x=categories,
        y=online_pcts,
        marker_color='lightblue',
        text=[f"{pct:.1f}%" for pct in online_pcts],
        textposition='auto',
        yaxis='y1'
    ))

    fig.add_trace(go.Scatter(
        name='Avg Response Time (ms)',
        x=categories,
        y=avg_times,
        mode='lines+markers',
        marker=dict(size=10, color='red'),
        line=dict(width=2, color='red'),
        yaxis='y2'
    ))

    fig.update_layout(
        title='Category Health Overview',
        xaxis=dict(title='Category'),
        yaxis=dict(title='Availability %', side='left', range=[0, 100]),
        yaxis2=dict(title='Response Time (ms)', side='right', overlaying='y'),
        hovermode='x unified',
        template='plotly_white',
        height=500
    )

    return fig


# =============================================================================
# TAB 3: Health History
# =============================================================================

def get_uptime_chart(provider_name=None, hours=24):
    """Get uptime chart for provider(s)"""
    try:
        # Get data from database
        status_data = db.get_recent_status(provider_name=provider_name, hours=hours)

        if not status_data:
            fig = go.Figure()
            fig.add_annotation(
                text="No historical data available. Data will accumulate over time.",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig

        # Convert to DataFrame
        df = pd.DataFrame(status_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df['uptime_value'] = df['status'].apply(lambda x: 100 if x == 'online' else 0)

        # Group by provider and time
        if provider_name:
            providers = [provider_name]
        else:
            providers = df['provider_name'].unique()[:10]  # Limit to 10 providers

        fig = go.Figure()

        for provider in providers:
            provider_df = df[df['provider_name'] == provider]

            # Resample to hourly average
            provider_df = provider_df.set_index('timestamp')
            resampled = provider_df['uptime_value'].resample('1H').mean()

            fig.add_trace(go.Scatter(
                name=provider,
                x=resampled.index,
                y=resampled.values,
                mode='lines+markers',
                line=dict(width=2),
                marker=dict(size=6)
            ))

        fig.update_layout(
            title=f'Uptime History - Last {hours} Hours',
            xaxis_title='Time',
            yaxis_title='Uptime %',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            yaxis=dict(range=[0, 105])
        )

        return fig

    except Exception as e:
        logger.error(f"Error creating uptime chart: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig


def get_response_time_chart(provider_name=None, hours=24):
    """Get response time trends"""
    try:
        status_data = db.get_recent_status(provider_name=provider_name, hours=hours)

        if not status_data:
            return go.Figure()

        df = pd.DataFrame(status_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

        if provider_name:
            providers = [provider_name]
        else:
            providers = df['provider_name'].unique()[:10]

        fig = go.Figure()

        for provider in providers:
            provider_df = df[df['provider_name'] == provider]

            fig.add_trace(go.Scatter(
                name=provider,
                x=provider_df['timestamp'],
                y=provider_df['response_time'],
                mode='lines',
                line=dict(width=2)
            ))

        fig.update_layout(
            title=f'Response Time Trends - Last {hours} Hours',
            xaxis_title='Time',
            yaxis_title='Response Time (ms)',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )

        return fig

    except Exception as e:
        logger.error(f"Error creating response time chart: {e}")
        return go.Figure()


def get_incident_log(hours=24):
    """Get incident log"""
    try:
        incidents = db.get_incident_history(hours=hours)

        if not incidents:
            return pd.DataFrame({'Message': ['No incidents in the selected period']})

        df_data = []
        for incident in incidents:
            df_data.append({
                'Timestamp': incident['start_time'],
                'Provider': incident['provider_name'],
                'Category': incident['category'],
                'Type': incident['incident_type'],
                'Severity': incident['severity'],
                'Description': incident['description'],
                'Duration': f"{incident.get('duration_seconds', 0)} sec" if incident.get('resolved') else 'Ongoing',
                'Status': '✅ Resolved' if incident.get('resolved') else '⚠️ Active'
            })

        return pd.DataFrame(df_data)

    except Exception as e:
        logger.error(f"Error getting incident log: {e}")
        return pd.DataFrame({'Error': [str(e)]})


# =============================================================================
# TAB 4: Test Endpoint
# =============================================================================

def test_endpoint(provider_name, custom_endpoint="", use_proxy=False):
    """Test a specific endpoint"""
    try:
        resources = config.get_all_resources()
        resource = next((r for r in resources if r['name'] == provider_name), None)

        if not resource:
            return "Provider not found", ""

        # Override endpoint if provided
        if custom_endpoint:
            resource = resource.copy()
            resource['endpoint'] = custom_endpoint

        # Run check
        result = asyncio.run(monitor.check_endpoint(resource, use_proxy=use_proxy))

        # Format response
        status_emoji = result.get_badge()
        status_text = f"""
## Test Results

**Provider:** {result.provider_name}
**Status:** {status_emoji} {result.status.value.upper()}
**Response Time:** {result.response_time:.2f} ms
**Status Code:** {result.status_code or 'N/A'}
**Endpoint:** `{result.endpoint_tested}`

### Details
"""

        if result.error_message:
            status_text += f"\n**Error:** {result.error_message}\n"
        else:
            status_text += "\n✅ Request successful\n"

        # Troubleshooting hints
        if result.status != HealthStatus.ONLINE:
            status_text += "\n### Troubleshooting Hints\n"
            if result.status_code == 403:
                status_text += "- Check API key validity\n- Verify rate limits\n- Try using CORS proxy\n"
            elif result.status_code == 429:
                status_text += "- Rate limit exceeded\n- Wait before retrying\n- Consider using backup provider\n"
            elif result.error_message and "timeout" in result.error_message.lower():
                status_text += "- Connection timeout\n- Service may be slow or down\n- Try increasing timeout\n"
            else:
                status_text += "- Verify endpoint URL\n- Check network connectivity\n- Review API documentation\n"

        return status_text, json.dumps(result.to_dict(), indent=2)

    except Exception as e:
        return f"Error testing endpoint: {str(e)}", ""


def get_example_query(provider_name):
    """Get example query for a provider"""
    resources = config.get_all_resources()
    resource = next((r for r in resources if r['name'] == provider_name), None)

    if not resource:
        return ""

    example = resource.get('example', '')
    if example:
        return f"Example:\n{example}"

    # Generate generic example based on endpoint
    endpoint = resource.get('endpoint', '')
    url = resource.get('url', '')

    if endpoint:
        return f"Example URL:\n{url}{endpoint}"

    return f"Base URL:\n{url}"


# =============================================================================
# TAB 5: Configuration
# =============================================================================

def update_refresh_interval(interval_minutes):
    """Update background refresh interval"""
    try:
        scheduler.update_interval(interval_minutes)
        return f"✅ Refresh interval updated to {interval_minutes} minutes"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def clear_all_cache():
    """Clear all caches"""
    try:
        monitor.clear_cache()
        return "✅ Cache cleared successfully"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_config_info():
    """Get configuration information"""
    stats = config.stats()

    info = f"""
## Configuration Overview

**Total API Resources:** {stats['total_resources']}
**Categories:** {stats['total_categories']}
**Free Resources:** {stats['free_resources']}
**Tier 1 (Critical):** {stats['tier1_count']}
**Tier 2 (Important):** {stats['tier2_count']}
**Tier 3 (Others):** {stats['tier3_count']}
**Configured API Keys:** {stats['api_keys_count']}
**CORS Proxies:** {stats['cors_proxies_count']}

### Categories
{', '.join(stats['categories'])}

### Scheduler Status
**Running:** {scheduler.is_running()}
**Interval:** {scheduler.interval_minutes} minutes
**Last Run:** {scheduler.last_run_time.strftime('%Y-%m-%d %H:%M:%S') if scheduler.last_run_time else 'Never'}
"""

    return info


# =============================================================================
# Build Gradio Interface
# =============================================================================

def build_interface():
    """Build the complete Gradio interface"""

    with gr.Blocks(
        theme=gr.themes.Soft(primary_hue="purple", secondary_hue="blue"),
        title="Crypto API Monitor",
        css="""
        .gradio-container {
            max-width: 1400px !important;
        }
        """
    ) as app:

        gr.Markdown("""
        # 📊 Cryptocurrency API Monitor
        ### Real-time health monitoring for 162+ crypto API endpoints
        *Production-ready | Auto-refreshing | Persistent metrics | Multi-tier monitoring*
        """)

        # TAB 1: Real-Time Dashboard
        with gr.Tab("📊 Real-Time Dashboard"):
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh Now", variant="primary", size="lg")
                export_btn = gr.Button("💾 Export CSV", size="lg")

            with gr.Row():
                category_filter = gr.Dropdown(
                    choices=["All"] + config.get_categories(),
                    value="All",
                    label="Filter by Category"
                )
                status_filter = gr.Dropdown(
                    choices=["All", "Online", "Degraded", "Offline"],
                    value="All",
                    label="Filter by Status"
                )
                tier_filter = gr.Dropdown(
                    choices=["All", "Tier 1", "Tier 2", "Tier 3"],
                    value="All",
                    label="Filter by Tier"
                )

            summary_cards = gr.HTML()
            status_table = gr.DataFrame(
                headers=["Status", "Provider", "Category", "Response Time", "Last Check", "Code"],
                wrap=True
            )
            download_file = gr.File(label="Download CSV", visible=False)

            refresh_btn.click(
                fn=refresh_dashboard,
                inputs=[category_filter, status_filter, tier_filter],
                outputs=[status_table, summary_cards]
            )

            export_btn.click(
                fn=export_current_status,
                outputs=download_file
            )

        # TAB 2: Category View
        with gr.Tab("📁 Category View"):
            gr.Markdown("### API Resources by Category")

            with gr.Row():
                refresh_cat_btn = gr.Button("🔄 Refresh Categories", variant="primary")

            category_overview = gr.HTML()
            category_chart = gr.Plot()

            refresh_cat_btn.click(
                fn=get_category_overview,
                outputs=category_overview
            )

            refresh_cat_btn.click(
                fn=get_category_chart,
                outputs=category_chart
            )

        # TAB 3: Health History
        with gr.Tab("📈 Health History"):
            gr.Markdown("### Historical Performance & Incidents")

            with gr.Row():
                history_provider = gr.Dropdown(
                    choices=["All"] + [r['name'] for r in config.get_all_resources()],
                    value="All",
                    label="Select Provider"
                )
                history_hours = gr.Slider(
                    minimum=1,
                    maximum=168,
                    value=24,
                    step=1,
                    label="Time Range (hours)"
                )
                refresh_history_btn = gr.Button("🔄 Refresh", variant="primary")

            uptime_chart = gr.Plot(label="Uptime History")
            response_chart = gr.Plot(label="Response Time Trends")
            incident_table = gr.DataFrame(label="Incident Log")

            def update_history(provider, hours):
                prov = None if provider == "All" else provider
                uptime = get_uptime_chart(prov, hours)
                response = get_response_time_chart(prov, hours)
                incidents = get_incident_log(hours)
                return uptime, response, incidents

            refresh_history_btn.click(
                fn=update_history,
                inputs=[history_provider, history_hours],
                outputs=[uptime_chart, response_chart, incident_table]
            )

        # TAB 4: Test Endpoint
        with gr.Tab("🔧 Test Endpoint"):
            gr.Markdown("### Test Individual API Endpoints")

            with gr.Row():
                test_provider = gr.Dropdown(
                    choices=[r['name'] for r in config.get_all_resources()],
                    label="Select Provider"
                )
                test_btn = gr.Button("▶️ Run Test", variant="primary")

            with gr.Row():
                custom_endpoint = gr.Textbox(
                    label="Custom Endpoint (optional)",
                    placeholder="/api/endpoint"
                )
                use_proxy_check = gr.Checkbox(label="Use CORS Proxy", value=False)

            example_query = gr.Markdown()
            test_result = gr.Markdown()
            test_json = gr.Code(label="JSON Response", language="json")

            test_provider.change(
                fn=get_example_query,
                inputs=test_provider,
                outputs=example_query
            )

            test_btn.click(
                fn=test_endpoint,
                inputs=[test_provider, custom_endpoint, use_proxy_check],
                outputs=[test_result, test_json]
            )

        # TAB 5: Configuration
        with gr.Tab("⚙️ Configuration"):
            gr.Markdown("### System Configuration & Settings")

            config_info = gr.Markdown()

            with gr.Row():
                refresh_interval = gr.Slider(
                    minimum=1,
                    maximum=60,
                    value=5,
                    step=1,
                    label="Auto-refresh Interval (minutes)"
                )
                update_interval_btn = gr.Button("💾 Update Interval")

            interval_status = gr.Textbox(label="Status", interactive=False)

            with gr.Row():
                clear_cache_btn = gr.Button("🗑️ Clear Cache")
                cache_status = gr.Textbox(label="Cache Status", interactive=False)

            gr.Markdown("### API Keys Management")
            gr.Markdown("""
            API keys are loaded from environment variables in Hugging Face Spaces.
            Go to **Settings > Repository secrets** to add keys:
            - `ETHERSCAN_KEY`
            - `BSCSCAN_KEY`
            - `TRONSCAN_KEY`
            - `CMC_KEY` (CoinMarketCap)
            - `CRYPTOCOMPARE_KEY`
            """)

            # Load config info on tab open
            app.load(fn=get_config_info, outputs=config_info)

            update_interval_btn.click(
                fn=update_refresh_interval,
                inputs=refresh_interval,
                outputs=interval_status
            )

            clear_cache_btn.click(
                fn=clear_all_cache,
                outputs=cache_status
            )

        # Initial load
        app.load(
            fn=refresh_dashboard,
            inputs=[category_filter, status_filter, tier_filter],
            outputs=[status_table, summary_cards]
        )

    return app


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    logger.info("Starting Crypto API Monitor...")

    # Start background scheduler
    scheduler.start()

    # Build and launch app
    app = build_interface()

    # Launch with sharing for HF Spaces
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
