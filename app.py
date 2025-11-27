#!/usr/bin/env python3
"""
Crypto Intelligence Hub - Hugging Face Space Application
یکپارچه‌سازی کامل بک‌اند و فرانت‌اند برای جمع‌آوری داده‌های رمز ارز
Hub کامل با منابع رایگان و مدل‌های Hugging Face

پشتیبانی از دو حالت:
1. Gradio UI (پیش‌فرض)
2. FastAPI + HTML (در صورت تنظیم USE_FASTAPI_HTML=true)
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import httpx

# Import backend services
try:
    from api_server_extended import app as fastapi_app
    from ai_models import ModelRegistry, MODEL_SPECS, get_model_info, registry_status

    FASTAPI_AVAILABLE = True
except ImportError as e:
    logging.warning(f"FastAPI not available: {e}")
    FASTAPI_AVAILABLE = False
    ModelRegistry = None
    MODEL_SPECS = {}
    get_model_info = None
    registry_status = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment detection
IS_DOCKER = (
    os.path.exists("/.dockerenv")
    or os.path.exists("/app")
    or os.getenv("DOCKER_CONTAINER") == "true"
)
# Default to FastAPI+HTML in Docker, Gradio otherwise
USE_FASTAPI_HTML = os.getenv("USE_FASTAPI_HTML", "true" if IS_DOCKER else "false").lower() == "true"
USE_GRADIO = os.getenv("USE_GRADIO", "false" if IS_DOCKER else "true").lower() == "true"

# Global state
WORKSPACE_ROOT = Path("/app" if Path("/app").exists() else Path("."))
RESOURCES_JSON = WORKSPACE_ROOT / "api-resources" / "crypto_resources_unified_2025-11-11.json"
ALL_APIS_JSON = WORKSPACE_ROOT / "all_apis_merged_2025.json"

# Fallback paths
if not RESOURCES_JSON.exists():
    RESOURCES_JSON = WORKSPACE_ROOT / "all_apis_merged_2025.json"
if not ALL_APIS_JSON.exists():
    ALL_APIS_JSON = WORKSPACE_ROOT / "all_apis_merged_2025.json"

# Initialize model registry
model_registry = ModelRegistry() if ModelRegistry else None


class CryptoDataHub:
    """مرکز داده‌های رمز ارز با پشتیبانی از منابع رایگان و مدل‌های Hugging Face"""

    def __init__(self):
        self.resources = {}
        self.models_loaded = False
        self.load_resources()
        self.initialize_models()

    def load_resources(self):
        """بارگذاری منابع از فایل‌های JSON"""
        try:
            # Load unified resources
            if RESOURCES_JSON.exists():
                with open(RESOURCES_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.resources["unified"] = data
                    logger.info(f"✅ Loaded unified resources: {RESOURCES_JSON}")

            # Load all APIs merged
            if ALL_APIS_JSON.exists():
                with open(ALL_APIS_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.resources["all_apis"] = data
                    logger.info(f"✅ Loaded all APIs: {ALL_APIS_JSON}")

            logger.info(f"📊 Total resource files loaded: {len(self.resources)}")
        except Exception as e:
            logger.error(f"❌ Error loading resources: {e}")

    def initialize_models(self):
        """بارگذاری مدل‌های Hugging Face"""
        if not model_registry:
            logger.warning("Model registry not available")
            return

        try:
            # Initialize available models
            result = model_registry.initialize_models()
            self.models_loaded = result.get("status") == "ok"
            logger.info(f"✅ Hugging Face models initialized: {result}")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize all models: {e}")

    def get_market_data_sources(self) -> List[Dict]:
        """دریافت منابع داده‌های بازار"""
        sources = []

        # Try unified resources first
        if "unified" in self.resources:
            registry = self.resources["unified"].get("registry", {})

            # Market data APIs
            market_apis = registry.get("market_data", [])
            for api in market_apis:
                sources.append(
                    {
                        "name": api.get("name", "Unknown"),
                        "category": "market",
                        "base_url": api.get("base_url", ""),
                        "free": api.get("free", False),
                        "auth_required": bool(api.get("auth", {}).get("key")),
                    }
                )

        # Try all_apis structure
        if "all_apis" in self.resources:
            data = self.resources["all_apis"]

            # Check for discovered_keys which indicates market data sources
            if "discovered_keys" in data:
                for provider, keys in data["discovered_keys"].items():
                    if provider in ["coinmarketcap", "cryptocompare"]:
                        sources.append(
                            {
                                "name": provider.upper(),
                                "category": "market",
                                "base_url": (
                                    f"https://api.{provider}.com"
                                    if provider == "coinmarketcap"
                                    else f"https://min-api.{provider}.com"
                                ),
                                "free": False,
                                "auth_required": True,
                            }
                        )

            # Check raw_files for API configurations
            if "raw_files" in data:
                for file_info in data["raw_files"]:
                    content = file_info.get("content", "")
                    if "CoinGecko" in content or "coingecko" in content.lower():
                        sources.append(
                            {
                                "name": "CoinGecko",
                                "category": "market",
                                "base_url": "https://api.coingecko.com/api/v3",
                                "free": True,
                                "auth_required": False,
                            }
                        )
                    if "Binance" in content or "binance" in content.lower():
                        sources.append(
                            {
                                "name": "Binance Public",
                                "category": "market",
                                "base_url": "https://api.binance.com/api/v3",
                                "free": True,
                                "auth_required": False,
                            }
                        )

        # Remove duplicates
        seen = set()
        unique_sources = []
        for source in sources:
            key = source["name"]
            if key not in seen:
                seen.add(key)
                unique_sources.append(source)

        return unique_sources

    def get_available_models(self) -> List[Dict]:
        """دریافت لیست مدل‌های در دسترس"""
        models = []

        if MODEL_SPECS:
            for key, spec in MODEL_SPECS.items():
                models.append(
                    {
                        "key": key,
                        "name": spec.model_id,
                        "task": spec.task,
                        "category": spec.category,
                        "requires_auth": spec.requires_auth,
                    }
                )

        return models

    async def analyze_sentiment(
        self, text: str, model_key: str = "crypto_sent_0", use_backend: bool = False
    ) -> Dict:
        """تحلیل احساسات با استفاده از مدل‌های Hugging Face"""
        # Try backend API first if requested and available
        if use_backend and FASTAPI_AVAILABLE:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "http://localhost:7860/api/hf/run-sentiment",
                        json={"texts": [text]},
                        headers={"Content-Type": "application/json"},
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("results"):
                            result = data["results"][0]
                            return {
                                "sentiment": result.get("label", "unknown"),
                                "confidence": result.get("confidence", 0.0),
                                "model": "backend_api",
                                "text": text[:100],
                                "vote": result.get("vote", 0.0),
                            }
            except Exception as e:
                logger.warning(f"Backend API call failed, falling back to direct model: {e}")

        # Direct model access
        if not model_registry or not self.models_loaded:
            return {"error": "Models not available", "sentiment": "unknown", "confidence": 0.0}

        try:
            pipeline = model_registry.get_pipeline(model_key)
            result = pipeline(text)

            # Handle different result formats
            if isinstance(result, list) and len(result) > 0:
                result = result[0]

            return {
                "sentiment": result.get("label", "unknown"),
                "confidence": result.get("score", 0.0),
                "model": model_key,
                "text": text[:100],
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"error": str(e), "sentiment": "error", "confidence": 0.0}

    def get_resource_summary(self) -> Dict:
        """خلاصه منابع موجود"""
        summary = {
            "total_resources": 0,
            "categories": {},
            "free_resources": 0,
            "models_available": len(self.get_available_models()),
        }

        if "unified" in self.resources:
            registry = self.resources["unified"].get("registry", {})

            for category, items in registry.items():
                if isinstance(items, list):
                    count = len(items)
                    summary["total_resources"] += count
                    summary["categories"][category] = count

                    # Count free resources
                    free_count = sum(1 for item in items if item.get("free", False))
                    summary["free_resources"] += free_count

        # Add market sources
        market_sources = self.get_market_data_sources()
        if market_sources:
            summary["total_resources"] += len(market_sources)
            summary["categories"]["market_data"] = len(market_sources)
            summary["free_resources"] += sum(1 for s in market_sources if s.get("free", False))

        return summary


# Initialize global hub
hub = CryptoDataHub()


# =============================================================================
# Gradio Interface Functions
# =============================================================================


def get_dashboard_summary():
    """نمایش خلاصه داشبورد"""
    summary = hub.get_resource_summary()

    html = f"""
    <div style="padding: 20px; font-family: Arial, sans-serif;">
        <h2>📊 خلاصه منابع و مدل‌ها</h2>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white;">
                <h3>منابع کل</h3>
                <p style="font-size: 32px; margin: 10px 0; font-weight: bold;">{summary['total_resources']}</p>
            </div>
            
            <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 20px; border-radius: 10px; color: white;">
                <h3>منابع رایگان</h3>
                <p style="font-size: 32px; margin: 10px 0; font-weight: bold;">{summary['free_resources']}</p>
            </div>
            
            <div style="background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%); padding: 20px; border-radius: 10px; color: white;">
                <h3>مدل‌های AI</h3>
                <p style="font-size: 32px; margin: 10px 0; font-weight: bold;">{summary['models_available']}</p>
            </div>
            
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; color: white;">
                <h3>دسته‌بندی‌ها</h3>
                <p style="font-size: 32px; margin: 10px 0; font-weight: bold;">{len(summary['categories'])}</p>
            </div>
        </div>
        
        <h3>دسته‌بندی منابع:</h3>
        <ul>
    """

    for category, count in summary["categories"].items():
        html += f"<li><strong>{category}:</strong> {count} منبع</li>"

    html += """
        </ul>
    </div>
    """

    return html


def get_resources_table():
    """جدول منابع"""
    sources = hub.get_market_data_sources()

    if not sources:
        return pd.DataFrame({"پیام": ["هیچ منبعی یافت نشد. لطفاً فایل‌های JSON را بررسی کنید."]})

    df_data = []
    for source in sources[:100]:  # Limit to 100 for display
        df_data.append(
            {
                "نام": source["name"],
                "دسته": source["category"],
                "رایگان": "✅" if source["free"] else "❌",
                "نیاز به کلید": "✅" if source["auth_required"] else "❌",
                "URL پایه": (
                    source["base_url"][:60] + "..."
                    if len(source["base_url"]) > 60
                    else source["base_url"]
                ),
            }
        )

    return pd.DataFrame(df_data)


def get_models_table():
    """جدول مدل‌ها"""
    models = hub.get_available_models()

    if not models:
        return pd.DataFrame({"پیام": ["هیچ مدلی یافت نشد. مدل‌ها در حال بارگذاری هستند..."]})

    df_data = []
    for model in models:
        df_data.append(
            {
                "کلید": model["key"],
                "نام مدل": model["name"],
                "نوع کار": model["task"],
                "دسته": model["category"],
                "نیاز به احراز هویت": "✅" if model["requires_auth"] else "❌",
            }
        )

    return pd.DataFrame(df_data)


def analyze_text_sentiment(text: str, model_selection: str, use_backend: bool = False):
    """تحلیل احساسات متن"""
    if not text.strip():
        return "⚠️ لطفاً متنی وارد کنید", ""

    try:
        # Extract model key from dropdown selection
        if model_selection and " - " in model_selection:
            model_key = model_selection.split(" - ")[0]
        else:
            model_key = model_selection if model_selection else "crypto_sent_0"

        result = asyncio.run(hub.analyze_sentiment(text, model_key, use_backend=use_backend))

        if "error" in result:
            return f"❌ خطا: {result['error']}", ""

        sentiment_emoji = {
            "POSITIVE": "📈",
            "NEGATIVE": "📉",
            "NEUTRAL": "➡️",
            "LABEL_0": "📈",
            "LABEL_1": "📉",
            "LABEL_2": "➡️",
            "positive": "📈",
            "negative": "📉",
            "neutral": "➡️",
            "bullish": "📈",
            "bearish": "📉",
        }.get(result["sentiment"], "❓")

        confidence_pct = (
            result["confidence"] * 100 if result["confidence"] <= 1.0 else result["confidence"]
        )

        vote_info = ""
        if "vote" in result:
            vote_emoji = "📈" if result["vote"] > 0 else "📉" if result["vote"] < 0 else "➡️"
            vote_info = f"\n**رأی مدل:** {vote_emoji} {result['vote']:.2f}"

        result_text = f"""
## نتیجه تحلیل احساسات

**احساسات:** {sentiment_emoji} {result['sentiment']}
**اعتماد:** {confidence_pct:.2f}%
**مدل استفاده شده:** {result['model']}
**متن تحلیل شده:** {result['text']}
{vote_info}
        """

        result_json = json.dumps(result, indent=2, ensure_ascii=False)

        return result_text, result_json
    except Exception as e:
        return f"❌ خطا در تحلیل: {str(e)}", ""


def create_category_chart():
    """نمودار دسته‌بندی منابع"""
    summary = hub.get_resource_summary()

    categories = list(summary["categories"].keys())
    counts = list(summary["categories"].values())

    if not categories:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
        )
        return fig

    fig = go.Figure(
        data=[
            go.Bar(
                x=categories, y=counts, marker_color="lightblue", text=counts, textposition="auto"
            )
        ]
    )

    fig.update_layout(
        title="توزیع منابع بر اساس دسته‌بندی",
        xaxis_title="دسته‌بندی",
        yaxis_title="تعداد منابع",
        template="plotly_white",
        height=400,
    )

    return fig


def get_model_status():
    """وضعیت مدل‌ها"""
    if not registry_status:
        return "❌ Model registry not available"

    status = registry_status()

    html = f"""
    <div style="padding: 20px;">
        <h3>وضعیت مدل‌ها</h3>
        <p><strong>وضعیت:</strong> {'✅ فعال' if status.get('ok') else '❌ غیرفعال'}</p>
        <p><strong>مدل‌های بارگذاری شده:</strong> {status.get('pipelines_loaded', 0)}</p>
        <p><strong>مدل‌های در دسترس:</strong> {len(status.get('available_models', []))}</p>
        <p><strong>حالت Hugging Face:</strong> {status.get('hf_mode', 'unknown')}</p>
        <p><strong>Transformers موجود:</strong> {'✅' if status.get('transformers_available') else '❌'}</p>
    </div>
    """

    return html


# =============================================================================
# Build Gradio Interface
# =============================================================================


def create_gradio_interface():
    """ایجاد رابط کاربری Gradio"""

    # Get available models for dropdown
    models = hub.get_available_models()
    model_choices = (
        [f"{m['key']} - {m['name']}" for m in models] if models else ["crypto_sent_0 - CryptoBERT"]
    )
    model_keys = [m["key"] for m in models] if models else ["crypto_sent_0"]

    with gr.Blocks(
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="purple"),
        title="Crypto Intelligence Hub - مرکز هوش رمز ارز",
        css="""
        .gradio-container {
            max-width: 1400px !important;
        }
        """,
    ) as app:

        gr.Markdown(
            """
        # 🚀 Crypto Intelligence Hub
        ## مرکز هوش مصنوعی و جمع‌آوری داده‌های رمز ارز
        
        **منابع رایگان | مدل‌های Hugging Face | رابط کاربری کامل**
        
        این برنامه یک رابط کامل برای دسترسی به منابع رایگان داده‌های رمز ارز و استفاده از مدل‌های هوش مصنوعی Hugging Face است.
        """
        )

        # Tab 1: Dashboard
        with gr.Tab("📊 داشبورد"):
            dashboard_summary = gr.HTML()
            refresh_dashboard_btn = gr.Button("🔄 به‌روزرسانی", variant="primary")

            refresh_dashboard_btn.click(fn=get_dashboard_summary, outputs=dashboard_summary)

            app.load(fn=get_dashboard_summary, outputs=dashboard_summary)

        # Tab 2: Resources
        with gr.Tab("📚 منابع داده"):
            gr.Markdown("### منابع رایگان برای جمع‌آوری داده‌های رمز ارز")

            resources_table = gr.DataFrame(label="لیست منابع", wrap=True)

            refresh_resources_btn = gr.Button("🔄 به‌روزرسانی", variant="primary")

            refresh_resources_btn.click(fn=get_resources_table, outputs=resources_table)

            app.load(fn=get_resources_table, outputs=resources_table)

            category_chart = gr.Plot(label="نمودار دسته‌بندی")

            refresh_resources_btn.click(fn=create_category_chart, outputs=category_chart)

        # Tab 3: AI Models
        with gr.Tab("🤖 مدل‌های AI"):
            gr.Markdown("### مدل‌های Hugging Face برای تحلیل احساسات و هوش مصنوعی")

            model_status_html = gr.HTML()

            models_table = gr.DataFrame(label="لیست مدل‌ها", wrap=True)

            refresh_models_btn = gr.Button("🔄 به‌روزرسانی", variant="primary")

            refresh_models_btn.click(fn=get_models_table, outputs=models_table)

            refresh_models_btn.click(fn=get_model_status, outputs=model_status_html)

            app.load(fn=get_models_table, outputs=models_table)

            app.load(fn=get_model_status, outputs=model_status_html)

        # Tab 4: Sentiment Analysis
        with gr.Tab("💭 تحلیل احساسات"):
            gr.Markdown("### تحلیل احساسات متن با استفاده از مدل‌های Hugging Face")

            with gr.Row():
                sentiment_text = gr.Textbox(
                    label="متن برای تحلیل",
                    placeholder="مثال: Bitcoin price is rising rapidly! The market shows strong bullish momentum.",
                    lines=5,
                )

            with gr.Row():
                model_dropdown = gr.Dropdown(
                    choices=model_choices,
                    value=model_choices[0] if model_choices else None,
                    label="انتخاب مدل",
                )
                use_backend_check = gr.Checkbox(
                    label="استفاده از بک‌اند API (در صورت موجود بودن)", value=False
                )
                analyze_btn = gr.Button("🔍 تحلیل", variant="primary")

            with gr.Row():
                sentiment_result = gr.Markdown(label="نتیجه")
                sentiment_json = gr.Code(label="JSON خروجی", language="json")

            def analyze_with_selected_model(text, model_choice, use_backend):
                return analyze_text_sentiment(text, model_choice, use_backend=use_backend)

            analyze_btn.click(
                fn=analyze_with_selected_model,
                inputs=[sentiment_text, model_dropdown, use_backend_check],
                outputs=[sentiment_result, sentiment_json],
            )

            # Example texts
            gr.Markdown(
                """
            ### مثال‌های متن:
            - "Bitcoin is showing strong bullish momentum"
            - "Market crash expected due to regulatory concerns"
            - "Ethereum network upgrade successful"
            - "Crypto market sentiment is very positive today"
            """
            )

        # Tab 5: API Integration
        with gr.Tab("🔌 یکپارچه‌سازی API"):
            gr.Markdown(
                """
            ### اتصال به بک‌اند FastAPI
            
            این بخش به سرویس‌های بک‌اند متصل می‌شود که از منابع JSON استفاده می‌کنند.
            
            **وضعیت:** {'✅ فعال' if FASTAPI_AVAILABLE else '❌ غیرفعال'}
            """
            )

            if FASTAPI_AVAILABLE:
                gr.Markdown(
                    """
                **API Endpoints در دسترس:**
                - `/api/market-data` - داده‌های بازار
                - `/api/sentiment` - تحلیل احساسات
                - `/api/news` - اخبار رمز ارز
                - `/api/resources` - لیست منابع
                """
                )

            # Show resource summary
            resource_info = gr.Markdown()

            def get_resource_info():
                summary = hub.get_resource_summary()
                return f"""
                ## اطلاعات منابع
                
                - **کل منابع:** {summary['total_resources']}
                - **منابع رایگان:** {summary['free_resources']}
                - **مدل‌های AI:** {summary['models_available']}
                - **دسته‌بندی‌ها:** {len(summary['categories'])}
                
                ### دسته‌بندی‌های موجود:
                {', '.join(summary['categories'].keys()) if summary['categories'] else 'هیچ دسته‌ای یافت نشد'}
                """

            app.load(fn=get_resource_info, outputs=resource_info)

        # Footer
        gr.Markdown(
            """
        ---
        ### 📝 اطلاعات
        - **منابع:** از فایل‌های JSON بارگذاری شده
        - **مدل‌ها:** Hugging Face Transformers
        - **بک‌اند:** FastAPI (در صورت موجود بودن)
        - **فرانت‌اند:** Gradio
        - **محیط:** Hugging Face Spaces (Docker)
        """
        )

    return app


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    logger.info("🚀 Starting Crypto Intelligence Hub...")
    logger.info(f"📁 Workspace: {WORKSPACE_ROOT}")
    logger.info(f"🐳 Docker detected: {IS_DOCKER}")
    logger.info(f"🌐 Use FastAPI+HTML: {USE_FASTAPI_HTML}")
    logger.info(f"🎨 Use Gradio: {USE_GRADIO}")
    logger.info(f"📊 Resources loaded: {len(hub.resources)}")
    logger.info(f"🤖 Models available: {len(hub.get_available_models())}")
    logger.info(f"🔌 FastAPI available: {FASTAPI_AVAILABLE}")

    # Choose mode based on environment variables
    if USE_FASTAPI_HTML and FASTAPI_AVAILABLE:
        # Run FastAPI with HTML interface
        logger.info("🌐 Starting FastAPI server with HTML interface...")
        import uvicorn

        port = int(os.getenv("PORT", "7860"))
        uvicorn.run(fastapi_app, host="0.0.0.0", port=port, log_level="info")
    elif USE_GRADIO:
        # Run Gradio interface (default)
        logger.info("🎨 Starting Gradio interface...")
        app = create_gradio_interface()
        app.launch(
            server_name="0.0.0.0",
            server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
            share=False,
            show_error=True,
        )
    elif FASTAPI_AVAILABLE:
        # Fallback to FastAPI if Gradio is disabled but FastAPI is available
        logger.info("🌐 Starting FastAPI server (fallback)...")
        import uvicorn

        port = int(os.getenv("PORT", "7860"))
        uvicorn.run(fastapi_app, host="0.0.0.0", port=port, log_level="info")
    else:
        # No UI mode available
        logger.error("❌ No UI mode available (FastAPI unavailable and Gradio disabled). Exiting.")
        raise SystemExit(1)
