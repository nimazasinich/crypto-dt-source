#!/usr/bin/env python3
"""
Crypto Data Aggregator - Admin Dashboard (Gradio App)
STRICT REAL-DATA-ONLY implementation for Hugging Face Spaces

7 Tabs:
1. Status - System health & overview
2. Providers - API provider management
3. Market Data - Live cryptocurrency data
4. APL Scanner - Auto Provider Loader
5. HF Models - Hugging Face model status
6. Diagnostics - System diagnostics & auto-repair
7. Logs - System logs viewer
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import json
import traceback
import asyncio

# Check for Gradio
try:
    import gradio as gr
except ImportError:
    print("ERROR: gradio not installed. Run: pip install gradio")
    sys.exit(1)

# Check for optional dependencies
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("WARNING: pandas not installed. Some features disabled.")

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("WARNING: plotly not installed. Charts disabled.")

# Import local modules
import config
import database
import collectors

# ==================== INDEPENDENT LOGGING SETUP ====================
# DO NOT use utils.setup_logging() - set up independently

logger = logging.getLogger("app")
if not logger.handlers:
    level_name = getattr(config, "LOG_LEVEL", "INFO")
    level = getattr(logging, level_name.upper(), logging.INFO)
    logger.setLevel(level)
    
    formatter = logging.Formatter(
        getattr(config, "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File handler if log file exists
    try:
        if hasattr(config, 'LOG_FILE'):
            fh = logging.FileHandler(config.LOG_FILE)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")

logger.info("=" * 60)
logger.info("Crypto Admin Dashboard Starting")
logger.info("=" * 60)

# Initialize database
db = database.get_database()


# ==================== TAB 1: STATUS ====================

def get_status_tab() -> Tuple[str, str, str]:
    """
    Get system status overview.
    Returns: (markdown_summary, db_stats_json, system_info_json)
    """
    try:
        # Get database stats
        db_stats = db.get_database_stats()
        
        # Count providers
        providers_config_path = config.BASE_DIR / "providers_config_extended.json"
        provider_count = 0
        if providers_config_path.exists():
            with open(providers_config_path, 'r') as f:
                providers_data = json.load(f)
                provider_count = len(providers_data.get('providers', {}))
        
        # Pool count (from config)
        pool_count = 0
        if providers_config_path.exists():
            with open(providers_config_path, 'r') as f:
                providers_data = json.load(f)
                pool_count = len(providers_data.get('pool_configurations', []))
        
        # Market snapshot
        latest_prices = db.get_latest_prices(3)
        market_snapshot = ""
        if latest_prices:
            for p in latest_prices[:3]:
                symbol = p.get('symbol', 'N/A')
                price = p.get('price_usd', 0)
                change = p.get('percent_change_24h', 0)
                market_snapshot += f"**{symbol}**: ${price:,.2f} ({change:+.2f}%)\n"
        else:
            market_snapshot = "No market data available yet."
        
        # Build summary
        summary = f"""
## 🎯 System Status

**Overall Health**: {"🟢 Operational" if db_stats.get('prices_count', 0) > 0 else "🟡 Initializing"}

### Quick Stats
- **Total Providers**: {provider_count}
- **Active Pools**: {pool_count}
- **Price Records**: {db_stats.get('prices_count', 0):,}
- **News Articles**: {db_stats.get('news_count', 0):,}
- **Unique Symbols**: {db_stats.get('unique_symbols', 0)}

### Market Snapshot (Top 3)
{market_snapshot}

**Last Update**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        # System info
        import platform
        system_info = {
            "Python Version": sys.version.split()[0],
            "Platform": platform.platform(),
            "Working Directory": str(config.BASE_DIR),
            "Database Size": f"{db_stats.get('database_size_mb', 0):.2f} MB",
            "Last Price Update": db_stats.get('latest_price_update', 'N/A'),
            "Last News Update": db_stats.get('latest_news_update', 'N/A')
        }
        
        return summary, json.dumps(db_stats, indent=2), json.dumps(system_info, indent=2)
    
    except Exception as e:
        logger.error(f"Error in get_status_tab: {e}\n{traceback.format_exc()}")
        return f"⚠️ Error loading status: {str(e)}", "{}", "{}"


def run_diagnostics_from_status(auto_fix: bool) -> str:
    """Run diagnostics from status tab"""
    try:
        from backend.services.diagnostics_service import DiagnosticsService
        
        diagnostics = DiagnosticsService()
        
        # Run async in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        report = loop.run_until_complete(diagnostics.run_full_diagnostics(auto_fix=auto_fix))
        loop.close()
        
        # Format output
        output = f"""
# Diagnostics Report

**Timestamp**: {report.timestamp}
**Duration**: {report.duration_ms:.2f}ms

## Summary
- **Total Issues**: {report.total_issues}
- **Critical**: {report.critical_issues}
- **Warnings**: {report.warnings}
- **Info**: {report.info_issues}
- **Fixed**: {len(report.fixed_issues)}

## Issues
"""
        for issue in report.issues:
            emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(issue.severity, "⚪")
            fixed_mark = " ✅ FIXED" if issue.auto_fixed else ""
            output += f"\n### {emoji} [{issue.category.upper()}] {issue.title}{fixed_mark}\n"
            output += f"{issue.description}\n"
            if issue.fixable and not issue.auto_fixed:
                output += f"**Fix**: `{issue.fix_action}`\n"
        
        return output
    
    except Exception as e:
        logger.error(f"Error running diagnostics: {e}")
        return f"❌ Diagnostics failed: {str(e)}"


# ==================== TAB 2: PROVIDERS ====================

def get_providers_table(category_filter: str = "All") -> Any:
    """
    Get providers from providers_config_extended.json
    Returns: DataFrame or dict
    """
    try:
        providers_path = config.BASE_DIR / "providers_config_extended.json"
        
        if not providers_path.exists():
            if PANDAS_AVAILABLE:
                return pd.DataFrame({"Error": ["providers_config_extended.json not found"]})
            return {"error": "providers_config_extended.json not found"}
        
        with open(providers_path, 'r') as f:
            data = json.load(f)
        
        providers = data.get('providers', {})
        
        # Build table data
        table_data = []
        for provider_id, provider_info in providers.items():
            if category_filter != "All":
                if provider_info.get('category', '').lower() != category_filter.lower():
                    continue
            
            table_data.append({
                "ID": provider_id,
                "Name": provider_info.get('name', provider_id),
                "Category": provider_info.get('category', 'unknown'),
                "Type": provider_info.get('type', 'http_json'),
                "Base URL": provider_info.get('base_url', 'N/A'),
                "Requires Auth": provider_info.get('requires_auth', False),
                "Priority": provider_info.get('priority', 'N/A'),
                "Validated": provider_info.get('validated', False)
            })
        
        if PANDAS_AVAILABLE:
            return pd.DataFrame(table_data) if table_data else pd.DataFrame({"Message": ["No providers found"]})
        else:
            return {"providers": table_data} if table_data else {"error": "No providers found"}
    
    except Exception as e:
        logger.error(f"Error loading providers: {e}")
        if PANDAS_AVAILABLE:
            return pd.DataFrame({"Error": [str(e)]})
        return {"error": str(e)}


def reload_providers_config() -> Tuple[Any, str]:
    """Reload providers config and return updated table + message"""
    try:
        # Force reload by re-reading file
        table = get_providers_table("All")
        message = f"✅ Providers reloaded at {datetime.now().strftime('%H:%M:%S')}"
        return table, message
    except Exception as e:
        logger.error(f"Error reloading providers: {e}")
        return get_providers_table("All"), f"❌ Reload failed: {str(e)}"


def get_provider_categories() -> List[str]:
    """Get unique provider categories"""
    try:
        providers_path = config.BASE_DIR / "providers_config_extended.json"
        if not providers_path.exists():
            return ["All"]
        
        with open(providers_path, 'r') as f:
            data = json.load(f)
        
        categories = set()
        for provider in data.get('providers', {}).values():
            cat = provider.get('category', 'unknown')
            categories.add(cat)
        
        return ["All"] + sorted(list(categories))
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return ["All"]


# ==================== TAB 3: MARKET DATA ====================

def get_market_data_table(search_filter: str = "") -> Any:
    """Get latest market data from database"""
    try:
        prices = db.get_latest_prices(100)
        
        if not prices:
            if PANDAS_AVAILABLE:
                return pd.DataFrame({"Message": ["No market data available. Click 'Refresh Prices' to collect data."]})
            return {"error": "No data available"}
        
        # Filter if search provided
        filtered_prices = prices
        if search_filter:
            search_lower = search_filter.lower()
            filtered_prices = [
                p for p in prices
                if search_lower in p.get('name', '').lower() or search_lower in p.get('symbol', '').lower()
            ]
        
        table_data = []
        for p in filtered_prices:
            table_data.append({
                "Rank": p.get('rank', 999),
                "Symbol": p.get('symbol', 'N/A'),
                "Name": p.get('name', 'Unknown'),
                "Price (USD)": f"${p.get('price_usd', 0):,.2f}" if p.get('price_usd') else "N/A",
                "24h Change (%)": f"{p.get('percent_change_24h', 0):+.2f}%" if p.get('percent_change_24h') is not None else "N/A",
                "Volume 24h": f"${p.get('volume_24h', 0):,.0f}" if p.get('volume_24h') else "N/A",
                "Market Cap": f"${p.get('market_cap', 0):,.0f}" if p.get('market_cap') else "N/A"
            })
        
        if PANDAS_AVAILABLE:
            df = pd.DataFrame(table_data)
            return df.sort_values('Rank') if not df.empty else pd.DataFrame({"Message": ["No matching data"]})
        else:
            return {"prices": table_data}
    
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        if PANDAS_AVAILABLE:
            return pd.DataFrame({"Error": [str(e)]})
        return {"error": str(e)}


def refresh_market_data() -> Tuple[Any, str]:
    """Refresh market data by collecting from APIs"""
    try:
        logger.info("Refreshing market data...")
        success, count = collectors.collect_price_data()
        
        if success:
            message = f"✅ Collected {count} price records at {datetime.now().strftime('%H:%M:%S')}"
        else:
            message = f"⚠️ Collection completed with issues. {count} records collected."
        
        # Return updated table
        table = get_market_data_table("")
        return table, message
    
    except Exception as e:
        logger.error(f"Error refreshing market data: {e}")
        return get_market_data_table(""), f"❌ Refresh failed: {str(e)}"


def plot_price_history(symbol: str, timeframe: str) -> Any:
    """Plot price history for a symbol"""
    if not PLOTLY_AVAILABLE:
        return None
    
    try:
        # Parse timeframe
        hours_map = {"24h": 24, "7d": 168, "30d": 720, "90d": 2160}
        hours = hours_map.get(timeframe, 168)
        
        # Get history
        history = db.get_price_history(symbol.upper(), hours)
        
        if not history or len(history) < 2:
            fig = go.Figure()
            fig.add_annotation(
                text=f"No historical data for {symbol}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Extract data
        timestamps = [datetime.fromisoformat(h['timestamp'].replace('Z', '+00:00')) if isinstance(h['timestamp'], str) else datetime.now() for h in history]
        prices = [h.get('price_usd', 0) for h in history]
        
        # Create plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=prices,
            mode='lines',
            name='Price',
            line=dict(color='#2962FF', width=2)
        ))
        
        fig.update_layout(
            title=f"{symbol} - {timeframe}",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    except Exception as e:
        logger.error(f"Error plotting price history: {e}")
        fig = go.Figure()
        fig.add_annotation(text=f"Error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig


# ==================== TAB 4: APL SCANNER ====================

def run_apl_scan() -> str:
    """Run Auto Provider Loader scan"""
    try:
        logger.info("Running APL scan...")
        
        # Import APL
        import auto_provider_loader
        
        # Run scan
        apl = auto_provider_loader.AutoProviderLoader()
        
        # Run async in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(apl.run())
        loop.close()
        
        # Build summary
        stats = apl.stats
        output = f"""
# APL Scan Complete

**Timestamp**: {stats.timestamp}
**Execution Time**: {stats.execution_time_sec:.2f}s

## HTTP Providers
- **Candidates**: {stats.total_http_candidates}
- **Valid**: {stats.http_valid} ✅
- **Invalid**: {stats.http_invalid} ❌
- **Conditional**: {stats.http_conditional} ⚠️

## HuggingFace Models
- **Candidates**: {stats.total_hf_candidates}
- **Valid**: {stats.hf_valid} ✅
- **Invalid**: {stats.hf_invalid} ❌
- **Conditional**: {stats.hf_conditional} ⚠️

## Total Active Providers
**{stats.total_active_providers}** providers are now active.

---

✅ All valid providers have been integrated into `providers_config_extended.json`.

See `PROVIDER_AUTO_DISCOVERY_REPORT.md` for full details.
"""
        
        return output
    
    except Exception as e:
        logger.error(f"Error running APL: {e}\n{traceback.format_exc()}")
        return f"❌ APL scan failed: {str(e)}\n\nCheck logs for details."


def get_apl_report() -> str:
    """Get last APL report"""
    try:
        report_path = config.BASE_DIR / "PROVIDER_AUTO_DISCOVERY_REPORT.md"
        if report_path.exists():
            with open(report_path, 'r') as f:
                return f.read()
        else:
            return "No APL report found. Run a scan first."
    except Exception as e:
        logger.error(f"Error reading APL report: {e}")
        return f"Error reading report: {str(e)}"


# ==================== TAB 5: HF MODELS ====================

def get_hf_models_status() -> Any:
    """Get HuggingFace models status"""
    try:
        import ai_models
        
        model_info = ai_models.get_model_info()
        
        # Build table
        table_data = []
        
        # Check if models are initialized
        if model_info.get('models_initialized'):
            for model_name, loaded in model_info.get('loaded_models', {}).items():
                status = "✅ VALID" if loaded else "❌ INVALID"
                table_data.append({
                    "Model": model_name,
                    "Status": status,
                    "Loaded": loaded
                })
        else:
            table_data.append({
                "Model": "No models initialized",
                "Status": "⚠️ NOT INITIALIZED",
                "Loaded": False
            })
        
        # Add configured models from config
        for model_type, model_id in config.HUGGINGFACE_MODELS.items():
            if not any(m['Model'] == model_type for m in table_data):
                table_data.append({
                    "Model": model_type,
                    "Status": "⚠️ CONFIGURED",
                    "Model ID": model_id
                })
        
        if PANDAS_AVAILABLE:
            return pd.DataFrame(table_data) if table_data else pd.DataFrame({"Message": ["No models configured"]})
        else:
            return {"models": table_data}
    
    except Exception as e:
        logger.error(f"Error getting HF models status: {e}")
        if PANDAS_AVAILABLE:
            return pd.DataFrame({"Error": [str(e)]})
        return {"error": str(e)}


def test_hf_model(model_name: str, test_text: str) -> str:
    """Test a HuggingFace model with text"""
    try:
        if not test_text or not test_text.strip():
            return "⚠️ Please enter test text"
        
        import ai_models
        
        if model_name in ["sentiment_twitter", "sentiment_financial", "sentiment"]:
            # Test sentiment analysis
            result = ai_models.analyze_sentiment(test_text)
            
            output = f"""
## Sentiment Analysis Result

**Input**: {test_text}

**Label**: {result.get('label', 'N/A')}
**Score**: {result.get('score', 0):.4f}
**Confidence**: {result.get('confidence', 0):.4f}

**Details**:
```json
{json.dumps(result.get('details', {}), indent=2)}
```
"""
            return output
        
        elif model_name == "summarization":
            # Test summarization
            summary = ai_models.summarize_text(test_text)
            
            output = f"""
## Summarization Result

**Original** ({len(test_text)} chars):
{test_text}

**Summary** ({len(summary)} chars):
{summary}
"""
            return output
        
        else:
            return f"⚠️ Model '{model_name}' not recognized or not testable"
    
    except Exception as e:
        logger.error(f"Error testing HF model: {e}")
        return f"❌ Model test failed: {str(e)}"


def initialize_hf_models() -> Tuple[Any, str]:
    """Initialize HuggingFace models"""
    try:
        import ai_models
        
        result = ai_models.initialize_models()
        
        if result.get('success'):
            message = f"✅ Models initialized successfully at {datetime.now().strftime('%H:%M:%S')}"
        else:
            message = f"⚠️ Model initialization completed with warnings: {result.get('status')}"
        
        # Return updated table
        table = get_hf_models_status()
        return table, message
    
    except Exception as e:
        logger.error(f"Error initializing HF models: {e}")
        return get_hf_models_status(), f"❌ Initialization failed: {str(e)}"


# ==================== TAB 6: DIAGNOSTICS ====================

def run_full_diagnostics(auto_fix: bool) -> str:
    """Run full system diagnostics"""
    try:
        from backend.services.diagnostics_service import DiagnosticsService
        
        logger.info(f"Running diagnostics (auto_fix={auto_fix})...")
        
        diagnostics = DiagnosticsService()
        
        # Run async in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        report = loop.run_until_complete(diagnostics.run_full_diagnostics(auto_fix=auto_fix))
        loop.close()
        
        # Format detailed output
        output = f"""
# 🔧 System Diagnostics Report

**Generated**: {report.timestamp}
**Duration**: {report.duration_ms:.2f}ms

---

## 📊 Summary

| Metric | Count |
|--------|-------|
| **Total Issues** | {report.total_issues} |
| **Critical** 🔴 | {report.critical_issues} |
| **Warnings** 🟡 | {report.warnings} |
| **Info** 🔵 | {report.info_issues} |
| **Auto-Fixed** ✅ | {len(report.fixed_issues)} |

---

## 🔍 Issues Detected

"""
        
        if not report.issues:
            output += "✅ **No issues detected!** System is healthy.\n"
        else:
            # Group by category
            by_category = {}
            for issue in report.issues:
                cat = issue.category
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(issue)
            
            for category, issues in sorted(by_category.items()):
                output += f"\n### {category.upper()}\n\n"
                
                for issue in issues:
                    emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(issue.severity, "⚪")
                    fixed_mark = " ✅ **AUTO-FIXED**" if issue.auto_fixed else ""
                    
                    output += f"**{emoji} {issue.title}**{fixed_mark}\n\n"
                    output += f"{issue.description}\n\n"
                    
                    if issue.fixable and issue.fix_action and not issue.auto_fixed:
                        output += f"💡 **Fix**: `{issue.fix_action}`\n\n"
                    
                    output += "---\n\n"
        
        # System info
        output += "\n## 💻 System Information\n\n"
        output += "```json\n"
        output += json.dumps(report.system_info, indent=2)
        output += "\n```\n"
        
        return output
    
    except Exception as e:
        logger.error(f"Error running diagnostics: {e}\n{traceback.format_exc()}")
        return f"❌ Diagnostics failed: {str(e)}\n\nCheck logs for details."


# ==================== TAB 7: LOGS ====================

def get_logs(log_type: str = "recent", lines: int = 100) -> str:
    """Get system logs"""
    try:
        log_file = config.LOG_FILE
        
        if not log_file.exists():
            return "⚠️ Log file not found"
        
        # Read log file
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
        
        # Filter based on log_type
        if log_type == "errors":
            filtered_lines = [line for line in all_lines if 'ERROR' in line or 'CRITICAL' in line]
        elif log_type == "warnings":
            filtered_lines = [line for line in all_lines if 'WARNING' in line]
        else:  # recent
            filtered_lines = all_lines
        
        # Get last N lines
        recent_lines = filtered_lines[-lines:] if len(filtered_lines) > lines else filtered_lines
        
        if not recent_lines:
            return f"ℹ️ No {log_type} logs found"
        
        # Format output
        output = f"# {log_type.upper()} Logs (Last {len(recent_lines)} lines)\n\n"
        output += "```\n"
        output += "".join(recent_lines)
        output += "\n```\n"
        
        return output
    
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return f"❌ Error reading logs: {str(e)}"


def clear_logs() -> str:
    """Clear log file"""
    try:
        log_file = config.LOG_FILE
        
        if log_file.exists():
            # Backup first
            backup_path = log_file.parent / f"{log_file.name}.backup.{int(datetime.now().timestamp())}"
            import shutil
            shutil.copy2(log_file, backup_path)
            
            # Clear
            with open(log_file, 'w') as f:
                f.write("")
            
            logger.info("Log file cleared")
            return f"✅ Logs cleared (backup saved to {backup_path.name})"
        else:
            return "⚠️ No log file to clear"
    
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        return f"❌ Error clearing logs: {str(e)}"


# ==================== GRADIO INTERFACE ====================

def build_interface():
    """Build the complete Gradio Blocks interface"""
    
    with gr.Blocks(title="Crypto Admin Dashboard", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("""
# 🚀 Crypto Data Aggregator - Admin Dashboard

**Real-time cryptocurrency data aggregation and analysis platform**

Features: Provider Management | Market Data | Auto Provider Loader | HF Models | System Diagnostics
        """)
        
        with gr.Tabs():
            
            # ==================== TAB 1: STATUS ====================
            with gr.Tab("📊 Status"):
                gr.Markdown("### System Status Overview")
                
                with gr.Row():
                    status_refresh_btn = gr.Button("🔄 Refresh Status", variant="primary")
                    status_diag_btn = gr.Button("🔧 Run Quick Diagnostics")
                
                status_summary = gr.Markdown()
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Database Statistics")
                        db_stats_json = gr.JSON()
                    
                    with gr.Column():
                        gr.Markdown("#### System Information")
                        system_info_json = gr.JSON()
                
                diag_output = gr.Markdown()
                
                # Load initial status
                demo.load(
                    fn=get_status_tab,
                    outputs=[status_summary, db_stats_json, system_info_json]
                )
                
                # Refresh button
                status_refresh_btn.click(
                    fn=get_status_tab,
                    outputs=[status_summary, db_stats_json, system_info_json]
                )
                
                # Quick diagnostics
                status_diag_btn.click(
                    fn=lambda: run_diagnostics_from_status(False),
                    outputs=diag_output
                )
            
            # ==================== TAB 2: PROVIDERS ====================
            with gr.Tab("🔌 Providers"):
                gr.Markdown("### API Provider Management")
                
                with gr.Row():
                    provider_category = gr.Dropdown(
                        label="Filter by Category",
                        choices=get_provider_categories(),
                        value="All"
                    )
                    provider_reload_btn = gr.Button("🔄 Reload Providers", variant="primary")
                
                providers_table = gr.Dataframe(
                    label="Providers",
                    interactive=False,
                    wrap=True
                ) if PANDAS_AVAILABLE else gr.JSON(label="Providers")
                
                provider_status = gr.Textbox(label="Status", interactive=False)
                
                # Load initial providers
                demo.load(
                    fn=lambda: get_providers_table("All"),
                    outputs=providers_table
                )
                
                # Category filter
                provider_category.change(
                    fn=get_providers_table,
                    inputs=provider_category,
                    outputs=providers_table
                )
                
                # Reload button
                provider_reload_btn.click(
                    fn=reload_providers_config,
                    outputs=[providers_table, provider_status]
                )
            
            # ==================== TAB 3: MARKET DATA ====================
            with gr.Tab("📈 Market Data"):
                gr.Markdown("### Live Cryptocurrency Market Data")
                
                with gr.Row():
                    market_search = gr.Textbox(
                        label="Search",
                        placeholder="Search by name or symbol..."
                    )
                    market_refresh_btn = gr.Button("🔄 Refresh Prices", variant="primary")
                
                market_table = gr.Dataframe(
                    label="Market Data",
                    interactive=False,
                    wrap=True,
                    height=400
                ) if PANDAS_AVAILABLE else gr.JSON(label="Market Data")
                
                market_status = gr.Textbox(label="Status", interactive=False)
                
                # Price chart section
                if PLOTLY_AVAILABLE:
                    gr.Markdown("#### Price History Chart")
                    
                    with gr.Row():
                        chart_symbol = gr.Textbox(
                            label="Symbol",
                            placeholder="BTC",
                            value="BTC"
                        )
                        chart_timeframe = gr.Dropdown(
                            label="Timeframe",
                            choices=["24h", "7d", "30d", "90d"],
                            value="7d"
                        )
                        chart_plot_btn = gr.Button("📊 Plot")
                    
                    price_chart = gr.Plot(label="Price History")
                    
                    chart_plot_btn.click(
                        fn=plot_price_history,
                        inputs=[chart_symbol, chart_timeframe],
                        outputs=price_chart
                    )
                
                # Load initial data
                demo.load(
                    fn=lambda: get_market_data_table(""),
                    outputs=market_table
                )
                
                # Search
                market_search.change(
                    fn=get_market_data_table,
                    inputs=market_search,
                    outputs=market_table
                )
                
                # Refresh
                market_refresh_btn.click(
                    fn=refresh_market_data,
                    outputs=[market_table, market_status]
                )
            
            # ==================== TAB 4: APL SCANNER ====================
            with gr.Tab("🔍 APL Scanner"):
                gr.Markdown("### Auto Provider Loader")
                gr.Markdown("Automatically discover, validate, and integrate API providers and HuggingFace models.")
                
                with gr.Row():
                    apl_scan_btn = gr.Button("▶️ Run APL Scan", variant="primary", size="lg")
                    apl_report_btn = gr.Button("📄 View Last Report")
                
                apl_output = gr.Markdown()
                
                apl_scan_btn.click(
                    fn=run_apl_scan,
                    outputs=apl_output
                )
                
                apl_report_btn.click(
                    fn=get_apl_report,
                    outputs=apl_output
                )
                
                # Load last report on startup
                demo.load(
                    fn=get_apl_report,
                    outputs=apl_output
                )
            
            # ==================== TAB 5: HF MODELS ====================
            with gr.Tab("🤖 HF Models"):
                gr.Markdown("### HuggingFace Models Status & Testing")
                
                with gr.Row():
                    hf_init_btn = gr.Button("🔄 Initialize Models", variant="primary")
                    hf_refresh_btn = gr.Button("🔄 Refresh Status")
                
                hf_models_table = gr.Dataframe(
                    label="Models",
                    interactive=False
                ) if PANDAS_AVAILABLE else gr.JSON(label="Models")
                
                hf_status = gr.Textbox(label="Status", interactive=False)
                
                gr.Markdown("#### Test Model")
                
                with gr.Row():
                    test_model_dropdown = gr.Dropdown(
                        label="Model",
                        choices=["sentiment", "sentiment_twitter", "sentiment_financial", "summarization"],
                        value="sentiment"
                    )
                
                test_input = gr.Textbox(
                    label="Test Input",
                    placeholder="Enter text to test the model...",
                    lines=3
                )
                
                test_btn = gr.Button("▶️ Run Test", variant="secondary")
                
                test_output = gr.Markdown(label="Test Output")
                
                # Load initial status
                demo.load(
                    fn=get_hf_models_status,
                    outputs=hf_models_table
                )
                
                # Initialize models
                hf_init_btn.click(
                    fn=initialize_hf_models,
                    outputs=[hf_models_table, hf_status]
                )
                
                # Refresh status
                hf_refresh_btn.click(
                    fn=get_hf_models_status,
                    outputs=hf_models_table
                )
                
                # Test model
                test_btn.click(
                    fn=test_hf_model,
                    inputs=[test_model_dropdown, test_input],
                    outputs=test_output
                )
            
            # ==================== TAB 6: DIAGNOSTICS ====================
            with gr.Tab("🔧 Diagnostics"):
                gr.Markdown("### System Diagnostics & Auto-Repair")
                
                with gr.Row():
                    diag_run_btn = gr.Button("▶️ Run Diagnostics", variant="primary")
                    diag_autofix_btn = gr.Button("🔧 Run with Auto-Fix", variant="secondary")
                
                diagnostics_output = gr.Markdown()
                
                diag_run_btn.click(
                    fn=lambda: run_full_diagnostics(False),
                    outputs=diagnostics_output
                )
                
                diag_autofix_btn.click(
                    fn=lambda: run_full_diagnostics(True),
                    outputs=diagnostics_output
                )
            
            # ==================== TAB 7: LOGS ====================
            with gr.Tab("📋 Logs"):
                gr.Markdown("### System Logs Viewer")
                
                with gr.Row():
                    log_type = gr.Dropdown(
                        label="Log Type",
                        choices=["recent", "errors", "warnings"],
                        value="recent"
                    )
                    log_lines = gr.Slider(
                        label="Lines to Show",
                        minimum=10,
                        maximum=500,
                        value=100,
                        step=10
                    )
                
                with gr.Row():
                    log_refresh_btn = gr.Button("🔄 Refresh Logs", variant="primary")
                    log_clear_btn = gr.Button("🗑️ Clear Logs", variant="secondary")
                
                logs_output = gr.Markdown()
                log_clear_status = gr.Textbox(label="Status", interactive=False, visible=False)
                
                # Load initial logs
                demo.load(
                    fn=lambda: get_logs("recent", 100),
                    outputs=logs_output
                )
                
                # Refresh logs
                log_refresh_btn.click(
                    fn=get_logs,
                    inputs=[log_type, log_lines],
                    outputs=logs_output
                )
                
                # Update when dropdown changes
                log_type.change(
                    fn=get_logs,
                    inputs=[log_type, log_lines],
                    outputs=logs_output
                )
                
                # Clear logs
                log_clear_btn.click(
                    fn=clear_logs,
                    outputs=log_clear_status
                ).then(
                    fn=lambda: get_logs("recent", 100),
                    outputs=logs_output
                )
        
        # Footer
        gr.Markdown("""
---
**Crypto Data Aggregator Admin Dashboard** | Real Data Only | No Mock/Fake Data
        """)
    
    return demo


# ==================== MAIN ENTRY POINT ====================

demo = build_interface()

if __name__ == "__main__":
    logger.info("Launching Gradio dashboard...")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
