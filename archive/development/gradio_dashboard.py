#!/usr/bin/env python3
"""
Comprehensive Gradio Dashboard for Crypto Data Sources
Monitors health, accessibility, and functionality of all data sources
"""

import gradio as gr
import httpx
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))


class CryptoResourceMonitor:
    """Monitor and test all crypto data sources"""

    def __init__(self):
        self.api_resources = self.load_api_resources()
        self.health_cache = {}
        self.last_check_time = None
        self.fastapi_url = "http://localhost:7860"
        self.hf_engine_url = "http://localhost:8000"

    def load_api_resources(self) -> Dict:
        """Load all API resources from api-resources folder"""
        resources = {
            "unified": {},
            "pipeline": {},
            "merged": {}
        }

        try:
            # Load unified resources
            unified_path = Path("api-resources/crypto_resources_unified_2025-11-11.json")
            if unified_path.exists():
                with open(unified_path) as f:
                    resources["unified"] = json.load(f)

            # Load pipeline
            pipeline_path = Path("api-resources/ultimate_crypto_pipeline_2025_NZasinich.json")
            if pipeline_path.exists():
                with open(pipeline_path) as f:
                    resources["pipeline"] = json.load(f)

            # Load merged APIs
            merged_path = Path("all_apis_merged_2025.json")
            if merged_path.exists():
                with open(merged_path) as f:
                    resources["merged"] = json.load(f)

        except Exception as e:
            print(f"Error loading resources: {e}")

        return resources

    async def check_endpoint_health(self, url: str, timeout: int = 5) -> Tuple[bool, float, str]:
        """Check if an endpoint is accessible"""
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                latency = (time.time() - start_time) * 1000
                return response.status_code < 400, latency, f"Status: {response.status_code}"
        except httpx.TimeoutException:
            return False, timeout * 1000, "Timeout"
        except Exception as e:
            return False, 0, str(e)[:100]

    def check_fastapi_server(self) -> Tuple[bool, str]:
        """Check if main FastAPI server is running"""
        try:
            response = httpx.get(f"{self.fastapi_url}/health", timeout=5)
            return True, f"✅ Online (Status: {response.status_code})"
        except:
            return False, "❌ Offline"

    def check_hf_data_engine(self) -> Tuple[bool, str]:
        """Check if HF Data Engine is running"""
        try:
            response = httpx.get(f"{self.hf_engine_url}/api/health", timeout=5)
            data = response.json()
            providers = len(data.get("providers", []))
            uptime = data.get("uptime", 0)
            return True, f"✅ Online ({providers} providers, uptime: {uptime}s)"
        except:
            return False, "❌ Offline"

    def get_system_overview(self) -> str:
        """Get overview of all systems"""
        fastapi_ok, fastapi_msg = self.check_fastapi_server()
        hf_ok, hf_msg = self.check_hf_data_engine()

        overview = f"""
# 🚀 Crypto Data Sources - System Overview

**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 🖥️ Main Systems

### FastAPI Backend ({self.fastapi_url})
{fastapi_msg}

### HF Data Engine ({self.hf_engine_url})
{hf_msg}

## 📊 Loaded Resources

- **Unified Resources:** {len(self.api_resources.get('unified', {}).get('registry', {}))} sources
- **Pipeline Resources:** {len(self.api_resources.get('pipeline', {}))} sources
- **Merged APIs:** {len(self.api_resources.get('merged', {}))} sources

## 📁 Resource Categories

"""

        # Count categories from unified resources
        if 'registry' in self.api_resources.get('unified', {}):
            categories = {}
            for source in self.api_resources['unified']['registry'].values():
                for item in source:
                    cat = item.get('category', item.get('chain', item.get('role', 'unknown')))
                    categories[cat] = categories.get(cat, 0) + 1

            for cat, count in sorted(categories.items()):
                overview += f"- **{cat}:** {count} sources\n"

        return overview

    async def test_all_sources(self, progress=gr.Progress()) -> Tuple[str, pd.DataFrame]:
        """Test all data sources for accessibility"""
        results = []

        progress(0, desc="Loading resources...")

        # Test unified resources
        if 'registry' in self.api_resources.get('unified', {}):
            registry = self.api_resources['unified']['registry']
            total = sum(len(sources) for sources in registry.values())
            current = 0

            for source_type, sources in registry.items():
                for source in sources:
                    current += 1
                    progress(current / total, desc=f"Testing {source.get('name', 'Unknown')}...")

                    name = source.get('name', 'Unknown')
                    base_url = source.get('base_url', '')
                    category = source.get('category', source.get('chain', source.get('role', 'unknown')))

                    if base_url:
                        is_healthy, latency, message = await self.check_endpoint_health(base_url)
                        status = "✅ Online" if is_healthy else "❌ Offline"
                        results.append({
                            "Name": name,
                            "Category": category,
                            "Status": status,
                            "Latency (ms)": f"{latency:.0f}" if is_healthy else "-",
                            "URL": base_url[:50] + "..." if len(base_url) > 50 else base_url,
                            "Message": message
                        })

                    await asyncio.sleep(0.1)  # Rate limiting

        df = pd.DataFrame(results) if results else pd.DataFrame()

        summary = f"""
# ✅ Health Check Complete

**Total Sources Tested:** {len(results)}
**Online:** {len([r for r in results if '✅' in r['Status']])}
**Offline:** {len([r for r in results if '❌' in r['Status']])}
**Average Latency:** {sum(float(r['Latency (ms)']) for r in results if r['Latency (ms)'] != '-') / max(1, len([r for r in results if r['Latency (ms)'] != '-'])):.0f} ms
**Completed:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

        return summary, df

    def test_fastapi_endpoints(self) -> Tuple[str, pd.DataFrame]:
        """Test all FastAPI endpoints"""
        endpoints = [
            ("/health", "GET", "Health Check"),
            ("/api/status", "GET", "System Status"),
            ("/api/providers", "GET", "Provider List"),
            ("/api/pools", "GET", "Pool Management"),
            ("/api/hf/health", "GET", "HuggingFace Health"),
            ("/api/feature-flags", "GET", "Feature Flags"),
        ]

        results = []
        for endpoint, method, description in endpoints:
            try:
                url = f"{self.fastapi_url}{endpoint}"
                response = httpx.get(url, timeout=5)
                status = "✅ Working" if response.status_code < 400 else "⚠️ Error"
                results.append({
                    "Endpoint": endpoint,
                    "Method": method,
                    "Description": description,
                    "Status": status,
                    "Status Code": response.status_code,
                    "Response Time": f"{response.elapsed.total_seconds() * 1000:.0f} ms"
                })
            except Exception as e:
                results.append({
                    "Endpoint": endpoint,
                    "Method": method,
                    "Description": description,
                    "Status": "❌ Failed",
                    "Status Code": "-",
                    "Response Time": str(e)[:50]
                })

        df = pd.DataFrame(results)
        summary = f"**Tested {len(results)} endpoints** - {len([r for r in results if '✅' in r['Status']])} working"
        return summary, df

    def test_hf_engine_endpoints(self) -> Tuple[str, pd.DataFrame]:
        """Test HF Data Engine endpoints"""
        endpoints = [
            ("/api/health", "Health Check"),
            ("/api/prices?symbols=BTC,ETH", "Prices"),
            ("/api/ohlcv?symbol=BTC&interval=1h&limit=10", "OHLCV Data"),
            ("/api/sentiment", "Sentiment"),
            ("/api/market/overview", "Market Overview"),
        ]

        results = []
        for endpoint, description in endpoints:
            try:
                url = f"{self.hf_engine_url}{endpoint}"
                start = time.time()
                response = httpx.get(url, timeout=30)
                latency = (time.time() - start) * 1000

                status = "✅ Working" if response.status_code < 400 else "⚠️ Error"

                # Get data preview
                try:
                    data = response.json()
                    preview = str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
                except:
                    preview = "N/A"

                results.append({
                    "Endpoint": endpoint.split("?")[0],
                    "Description": description,
                    "Status": status,
                    "Latency": f"{latency:.0f} ms",
                    "Preview": preview
                })
            except Exception as e:
                results.append({
                    "Endpoint": endpoint.split("?")[0],
                    "Description": description,
                    "Status": "❌ Failed",
                    "Latency": "-",
                    "Preview": str(e)[:100]
                })

        df = pd.DataFrame(results)
        working = len([r for r in results if '✅' in r['Status']])
        summary = f"**Tested {len(results)} endpoints** - {working}/{len(results)} working"
        return summary, df

    def get_resource_details(self, resource_name: str) -> str:
        """Get detailed information about a specific resource"""
        details = f"# 📋 Resource Details: {resource_name}\n\n"

        # Search in all resource files
        if 'registry' in self.api_resources.get('unified', {}):
            for source_type, sources in self.api_resources['unified']['registry'].items():
                for source in sources:
                    if source.get('name') == resource_name:
                        details += f"## Source Type: {source_type}\n\n"
                        details += f"```json\n{json.dumps(source, indent=2)}\n```\n"
                        return details

        return f"Resource '{resource_name}' not found"

    def get_statistics(self) -> str:
        """Get comprehensive statistics"""
        stats = "# 📊 Comprehensive Statistics\n\n"

        # Count all resources
        total_unified = 0
        if 'registry' in self.api_resources.get('unified', {}):
            for sources in self.api_resources['unified']['registry'].values():
                total_unified += len(sources)

        total_pipeline = len(self.api_resources.get('pipeline', {}))
        total_merged = len(self.api_resources.get('merged', {}))

        stats += f"""
## Total Resources
- **Unified Resources:** {total_unified}
- **Pipeline Resources:** {total_pipeline}
- **Merged APIs:** {total_merged}
- **Grand Total:** {total_unified + total_pipeline + total_merged}

## By Category (Unified Resources)
"""

        # Count by category
        if 'registry' in self.api_resources.get('unified', {}):
            categories = {}
            for sources in self.api_resources['unified']['registry'].values():
                for source in sources:
                    cat = source.get('category', source.get('chain', source.get('role', 'unknown')))
                    categories[cat] = categories.get(cat, 0) + 1

            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                stats += f"- **{cat}:** {count}\n"

        return stats


# Initialize monitor
monitor = CryptoResourceMonitor()


# Build Gradio Interface
with gr.Blocks(title="Crypto Data Sources Monitor", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
# 🚀 Crypto Data Sources - Comprehensive Monitor

**Monitor health, accessibility, and functionality of all data sources**

This dashboard provides real-time monitoring and testing of:
- 200+ Free Crypto APIs and Data Sources
- FastAPI Backend Server
- HuggingFace Data Engine
- All endpoints and providers
    """)

    # Tab 1: System Overview
    with gr.Tab("🏠 System Overview"):
        overview_md = gr.Markdown(monitor.get_system_overview())
        refresh_overview_btn = gr.Button("🔄 Refresh Overview", variant="primary")
        refresh_overview_btn.click(
            fn=lambda: monitor.get_system_overview(),
            outputs=[overview_md]
        )

    # Tab 2: Health Check
    with gr.Tab("🏥 Health Check"):
        gr.Markdown("### Test all data sources for accessibility")
        test_all_btn = gr.Button("🧪 Test All Sources", variant="primary", size="lg")
        health_summary = gr.Markdown()
        health_table = gr.Dataframe(
            headers=["Name", "Category", "Status", "Latency (ms)", "URL", "Message"],
            wrap=True
        )
        test_all_btn.click(
            fn=monitor.test_all_sources,
            outputs=[health_summary, health_table]
        )

    # Tab 3: FastAPI Endpoints
    with gr.Tab("⚡ FastAPI Endpoints"):
        gr.Markdown("### Test main application endpoints")
        test_fastapi_btn = gr.Button("🧪 Test FastAPI Endpoints", variant="primary")
        fastapi_summary = gr.Markdown()
        fastapi_table = gr.Dataframe(wrap=True)
        test_fastapi_btn.click(
            fn=monitor.test_fastapi_endpoints,
            outputs=[fastapi_summary, fastapi_table]
        )

    # Tab 4: HF Data Engine
    with gr.Tab("🤗 HF Data Engine"):
        gr.Markdown("### Test HuggingFace Data Engine")
        test_hf_btn = gr.Button("🧪 Test HF Engine", variant="primary")
        hf_summary = gr.Markdown()
        hf_table = gr.Dataframe(wrap=True)
        test_hf_btn.click(
            fn=monitor.test_hf_engine_endpoints,
            outputs=[hf_summary, hf_table]
        )

    # Tab 5: Resource Explorer
    with gr.Tab("🔍 Resource Explorer"):
        gr.Markdown("### Explore API resources")

        # Get list of all resource names
        resource_names = []
        if 'registry' in monitor.api_resources.get('unified', {}):
            for sources in monitor.api_resources['unified']['registry'].values():
                for source in sources:
                    resource_names.append(source.get('name', 'Unknown'))

        resource_dropdown = gr.Dropdown(
            choices=sorted(resource_names),
            label="Select Resource",
            interactive=True
        )
        resource_details = gr.Markdown()
        resource_dropdown.change(
            fn=monitor.get_resource_details,
            inputs=[resource_dropdown],
            outputs=[resource_details]
        )

    # Tab 6: Statistics
    with gr.Tab("📊 Statistics"):
        stats_md = gr.Markdown(monitor.get_statistics())
        refresh_stats_btn = gr.Button("🔄 Refresh Statistics", variant="primary")
        refresh_stats_btn.click(
            fn=lambda: monitor.get_statistics(),
            outputs=[stats_md]
        )

    # Tab 7: API Testing
    with gr.Tab("🧪 API Testing"):
        gr.Markdown("### Interactive API Testing")

        with gr.Row():
            with gr.Column():
                api_url = gr.Textbox(
                    label="API URL",
                    placeholder="http://localhost:7860/api/status",
                    value="http://localhost:7860/api/status"
                )
                api_method = gr.Radio(
                    choices=["GET", "POST"],
                    label="Method",
                    value="GET"
                )
                test_api_btn = gr.Button("🚀 Test API", variant="primary")

            with gr.Column():
                api_response = gr.JSON(label="Response")

        def test_custom_api(url: str, method: str):
            try:
                if method == "GET":
                    response = httpx.get(url, timeout=30)
                else:
                    response = httpx.post(url, timeout=30)

                return {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text[:1000]
                }
            except Exception as e:
                return {"error": str(e)}

        test_api_btn.click(
            fn=test_custom_api,
            inputs=[api_url, api_method],
            outputs=[api_response]
        )

    # Footer
    gr.Markdown("""
---
**Crypto Data Sources Monitor** | Built with Gradio | Last Updated: 2024-11-14
    """)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True
    )
