#!/usr/bin/env python3
"""
ULTIMATE Gradio Dashboard for Crypto Data Sources
Advanced monitoring with force testing, auto-healing, and real-time status
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
import threading
from collections import defaultdict

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))


class UltimateCryptoMonitor:
    """Ultimate monitoring system with force testing and auto-healing"""

    def __init__(self):
        self.api_resources = self.load_all_resources()
        self.health_status = {}
        self.auto_heal_enabled = False
        self.monitoring_active = False
        self.fastapi_url = "http://localhost:7860"
        self.hf_engine_url = "http://localhost:8000"
        self.test_results = []
        self.force_test_results = {}

    def load_all_resources(self) -> Dict:
        """Load ALL API resources from all JSON files"""
        resources = {}

        json_files = [
            "api-resources/crypto_resources_unified_2025-11-11.json",
            "api-resources/ultimate_crypto_pipeline_2025_NZasinich.json",
            "all_apis_merged_2025.json",
            "providers_config_extended.json",
            "providers_config_ultimate.json",
        ]

        for json_file in json_files:
            try:
                path = Path(json_file)
                if path.exists():
                    with open(path) as f:
                        data = json.load(f)
                        resources[path.stem] = data
                        print(f"✅ Loaded: {json_file}")
            except Exception as e:
                print(f"❌ Error loading {json_file}: {e}")

        return resources

    async def force_test_endpoint(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict] = None,
        retry_count: int = 3,
        timeout: int = 10,
    ) -> Dict:
        """Force test an endpoint with retries and detailed results"""
        results = {
            "url": url,
            "method": method,
            "attempts": [],
            "success": False,
            "total_time": 0,
            "final_status": "Failed",
        }

        for attempt in range(retry_count):
            attempt_result = {
                "attempt": attempt + 1,
                "timestamp": datetime.now().isoformat(),
                "success": False,
            }

            start_time = time.time()

            try:
                async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                    if method == "GET":
                        response = await client.get(url, headers=headers or {})
                    else:
                        response = await client.post(url, headers=headers or {})

                    elapsed = (time.time() - start_time) * 1000

                    attempt_result.update(
                        {
                            "success": response.status_code < 400,
                            "status_code": response.status_code,
                            "latency_ms": elapsed,
                            "response_size": len(response.content),
                            "headers": dict(response.headers),
                        }
                    )

                    if response.status_code < 400:
                        results["success"] = True
                        results["final_status"] = "Success"
                        results["attempts"].append(attempt_result)
                        break

            except httpx.TimeoutException:
                attempt_result["error"] = "Timeout"
                attempt_result["latency_ms"] = timeout * 1000
            except httpx.ConnectError:
                attempt_result["error"] = "Connection refused"
            except Exception as e:
                attempt_result["error"] = str(e)[:200]

            results["attempts"].append(attempt_result)
            results["total_time"] = (time.time() - start_time) * 1000

            if attempt < retry_count - 1:
                await asyncio.sleep(1)  # Wait before retry

        return results

    def get_comprehensive_overview(self) -> str:
        """Get ultra-comprehensive system overview"""
        overview = f"""
# 🚀 ULTIMATE Crypto Data Sources Monitor

**Current Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Monitoring Status:** {'🟢 Active' if self.monitoring_active else '🔴 Inactive'}
**Auto-Heal:** {'✅ Enabled' if self.auto_heal_enabled else '❌ Disabled'}

---

## 🖥️ Core Systems Status

"""

        # Check FastAPI
        try:
            response = httpx.get(f"{self.fastapi_url}/health", timeout=5)
            overview += f"### ✅ FastAPI Backend - ONLINE\n"
            overview += f"- URL: `{self.fastapi_url}`\n"
            overview += f"- Status: {response.status_code}\n"
            overview += f"- Response Time: {response.elapsed.total_seconds() * 1000:.0f}ms\n\n"
        except:
            overview += f"### ❌ FastAPI Backend - OFFLINE\n"
            overview += f"- URL: `{self.fastapi_url}`\n"
            overview += f"- Status: Not accessible\n\n"

        # Check HF Data Engine
        try:
            response = httpx.get(f"{self.hf_engine_url}/api/health", timeout=5)
            data = response.json()
            overview += f"### ✅ HF Data Engine - ONLINE\n"
            overview += f"- URL: `{self.hf_engine_url}`\n"
            overview += f"- Providers: {len(data.get('providers', []))}\n"
            overview += f"- Uptime: {data.get('uptime', 0)}s\n"
            overview += f"- Cache Hit Rate: {data.get('cache', {}).get('hitRate', 0):.2%}\n\n"
        except:
            overview += f"### ❌ HF Data Engine - OFFLINE\n"
            overview += f"- URL: `{self.hf_engine_url}`\n"
            overview += f"- Status: Not accessible\n\n"

        # Resource statistics
        overview += "## 📊 Loaded Resources\n\n"
        for name, data in self.api_resources.items():
            if isinstance(data, dict):
                if "registry" in data:
                    count = sum(
                        len(v) if isinstance(v, list) else 1 for v in data["registry"].values()
                    )
                elif "providers" in data:
                    count = len(data["providers"])
                else:
                    count = len(data)
            elif isinstance(data, list):
                count = len(data)
            else:
                count = 1

            overview += f"- **{name}:** {count} items\n"

        return overview

    async def force_test_all_sources(self, progress=gr.Progress()) -> Tuple[str, pd.DataFrame]:
        """Force test ALL sources with retries"""
        all_results = []
        total_sources = 0

        # Count total sources
        for resource_name, resource_data in self.api_resources.items():
            if isinstance(resource_data, dict) and "registry" in resource_data:
                for sources in resource_data["registry"].values():
                    if isinstance(sources, list):
                        total_sources += len(sources)

        progress(0, desc="Initializing force test...")
        current = 0

        # Test unified resources with force
        for resource_name, resource_data in self.api_resources.items():
            if isinstance(resource_data, dict) and "registry" in resource_data:
                registry = resource_data["registry"]

                for source_type, sources in registry.items():
                    if not isinstance(sources, list):
                        continue

                    for source in sources:
                        current += 1
                        name = source.get("name", source.get("id", "Unknown"))
                        progress(current / max(total_sources, 1), desc=f"Force testing {name}...")

                        base_url = source.get("base_url", source.get("url", ""))
                        if not base_url:
                            continue

                        # Force test with retries
                        result = await self.force_test_endpoint(base_url, retry_count=2, timeout=8)

                        status = "✅ ONLINE" if result["success"] else "❌ OFFLINE"
                        best_latency = min(
                            [
                                a.get("latency_ms", 99999)
                                for a in result["attempts"]
                                if a.get("success")
                            ],
                            default=None,
                        )

                        all_results.append(
                            {
                                "Name": name,
                                "Source": resource_name,
                                "Category": source.get(
                                    "category", source.get("chain", source.get("role", "unknown"))
                                ),
                                "Status": status,
                                "Attempts": len(result["attempts"]),
                                "Best Latency": f"{best_latency:.0f}ms" if best_latency else "-",
                                "URL": base_url[:60] + "..." if len(base_url) > 60 else base_url,
                                "Final Result": result["final_status"],
                            }
                        )

                        self.force_test_results[name] = result
                        await asyncio.sleep(0.2)  # Rate limiting

        df = pd.DataFrame(all_results) if all_results else pd.DataFrame()

        online = len([r for r in all_results if "✅" in r["Status"]])
        offline = len([r for r in all_results if "❌" in r["Status"]])

        summary = f"""
# 🧪 FORCE TEST COMPLETE

**Total Sources Tested:** {len(all_results)}
**✅ Online:** {online} ({online/max(len(all_results), 1)*100:.1f}%)
**❌ Offline:** {offline} ({offline/max(len(all_results), 1)*100:.1f}%)
**⏱️ Average Response Time:** {sum(float(r['Best Latency'].replace('ms', '')) for r in all_results if r['Best Latency'] != '-') / max(1, len([r for r in all_results if r['Best Latency'] != '-'])):.0f}ms
**🕐 Completed:** {datetime.now().strftime("%H:%M:%S")}

**Success Rate:** {online/max(len(all_results), 1)*100:.1f}%
"""

        return summary, df

    def test_with_auto_heal(self, endpoints: List[str]) -> Tuple[str, List[Dict]]:
        """Test endpoints and attempt auto-healing for failures"""
        results = []

        for endpoint in endpoints:
            result = {"endpoint": endpoint, "attempts": []}

            # First attempt
            try:
                response = httpx.get(endpoint, timeout=10)
                result["attempts"].append(
                    {
                        "status": "success" if response.status_code < 400 else "error",
                        "code": response.status_code,
                        "time": response.elapsed.total_seconds(),
                    }
                )

                if response.status_code >= 400 and self.auto_heal_enabled:
                    # Attempt auto-heal: retry with different strategies
                    for strategy in ["with_headers", "different_timeout", "follow_redirects"]:
                        time.sleep(1)

                        if strategy == "with_headers":
                            headers = {"User-Agent": "Mozilla/5.0"}
                            response = httpx.get(endpoint, headers=headers, timeout=10)
                        elif strategy == "different_timeout":
                            response = httpx.get(endpoint, timeout=30)
                        else:
                            response = httpx.get(endpoint, timeout=10, follow_redirects=True)

                        result["attempts"].append(
                            {
                                "strategy": strategy,
                                "status": "success" if response.status_code < 400 else "error",
                                "code": response.status_code,
                                "time": response.elapsed.total_seconds(),
                            }
                        )

                        if response.status_code < 400:
                            break

            except Exception as e:
                result["attempts"].append({"status": "failed", "error": str(e)})

            results.append(result)

        summary = f"Tested {len(endpoints)} endpoints with auto-heal"
        return summary, results

    def get_detailed_resource_info(self, resource_name: str) -> str:
        """Get ultra-detailed resource information"""
        info = f"# 📋 Detailed Resource Analysis: {resource_name}\n\n"

        found = False
        for source_file, data in self.api_resources.items():
            if isinstance(data, dict) and "registry" in data:
                for source_type, sources in data["registry"].items():
                    if not isinstance(sources, list):
                        continue

                    for source in sources:
                        if source.get("name") == resource_name or source.get("id") == resource_name:
                            found = True
                            info += f"## Source File: `{source_file}`\n"
                            info += f"## Source Type: `{source_type}`\n\n"
                            info += "### Configuration\n```json\n"
                            info += json.dumps(source, indent=2)
                            info += "\n```\n\n"

                            # Force test results
                            if resource_name in self.force_test_results:
                                test_result = self.force_test_results[resource_name]
                                info += "### Force Test Results\n\n"
                                info += f"- **Success:** {test_result['success']}\n"
                                info += f"- **Final Status:** {test_result['final_status']}\n"
                                info += f"- **Total Attempts:** {len(test_result['attempts'])}\n\n"

                                info += "#### Attempt Details\n"
                                for attempt in test_result["attempts"]:
                                    info += f"\n**Attempt {attempt['attempt']}:**\n"
                                    info += f"- Success: {attempt.get('success', False)}\n"
                                    if "latency_ms" in attempt:
                                        info += f"- Latency: {attempt['latency_ms']:.0f}ms\n"
                                    if "status_code" in attempt:
                                        info += f"- Status Code: {attempt['status_code']}\n"
                                    if "error" in attempt:
                                        info += f"- Error: {attempt['error']}\n"

                            return info

        if not found:
            info += f"❌ Resource '{resource_name}' not found in any loaded files.\n"

        return info

    def export_results_csv(self) -> str:
        """Export test results to CSV"""
        if not self.test_results:
            return "No test results to export"

        df = pd.DataFrame(self.test_results)
        csv_path = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_path, index=False)

        return f"✅ Results exported to: {csv_path}"


# Initialize monitor
monitor = UltimateCryptoMonitor()


# Build ULTIMATE Gradio Interface
with gr.Blocks(
    title="ULTIMATE Crypto Monitor",
    theme=gr.themes.Base(
        primary_hue="blue",
        secondary_hue="cyan",
    ),
    css="""
    .gradio-container {
        font-family: 'Inter', sans-serif;
    }
    .output-markdown h1 {
        color: #2563eb;
    }
    .output-markdown h2 {
        color: #3b82f6;
    }
    """,
) as demo:

    gr.Markdown(
        """
# 🚀 ULTIMATE Crypto Data Sources Monitor

**Advanced Real-Time Monitoring with Force Testing & Auto-Healing**

Monitor, test, and auto-heal 200+ cryptocurrency data sources, APIs, and backends.

---
    """
    )

    # Global settings
    with gr.Row():
        auto_heal_toggle = gr.Checkbox(label="🔧 Enable Auto-Heal", value=False)
        monitoring_toggle = gr.Checkbox(label="📡 Enable Real-Time Monitoring", value=False)

    def toggle_auto_heal(enabled):
        monitor.auto_heal_enabled = enabled
        return f"✅ Auto-heal {'enabled' if enabled else 'disabled'}"

    def toggle_monitoring(enabled):
        monitor.monitoring_active = enabled
        return f"✅ Monitoring {'enabled' if enabled else 'disabled'}"

    auto_heal_status = gr.Markdown()
    monitoring_status = gr.Markdown()

    auto_heal_toggle.change(
        fn=toggle_auto_heal, inputs=[auto_heal_toggle], outputs=[auto_heal_status]
    )
    monitoring_toggle.change(
        fn=toggle_monitoring, inputs=[monitoring_toggle], outputs=[monitoring_status]
    )

    # Main Tabs
    with gr.Tabs():
        # Tab 1: Dashboard
        with gr.Tab("🏠 Dashboard"):
            overview_md = gr.Markdown(monitor.get_comprehensive_overview())
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh", variant="primary", size="sm")
                export_btn = gr.Button("💾 Export Report", variant="secondary", size="sm")

            refresh_btn.click(
                fn=lambda: monitor.get_comprehensive_overview(), outputs=[overview_md]
            )

        # Tab 2: Force Test All
        with gr.Tab("🧪 Force Test"):
            gr.Markdown(
                """
            ### 💪 Force Test All Sources
            Test all data sources with multiple retry attempts and detailed diagnostics.
            This will test **every single API endpoint** with force retries.
            """
            )

            force_test_btn = gr.Button("⚡ START FORCE TEST", variant="primary", size="lg")
            force_summary = gr.Markdown()
            force_table = gr.Dataframe(wrap=True, interactive=False)

            force_test_btn.click(
                fn=monitor.force_test_all_sources, outputs=[force_summary, force_table]
            )

        # Tab 3: Resource Explorer
        with gr.Tab("🔍 Resource Explorer"):
            gr.Markdown("### Explore and analyze individual resources")

            # Get all resource names
            all_names = []
            for resource_data in monitor.api_resources.values():
                if isinstance(resource_data, dict) and "registry" in resource_data:
                    for sources in resource_data["registry"].values():
                        if isinstance(sources, list):
                            for source in sources:
                                name = source.get("name", source.get("id"))
                                if name:
                                    all_names.append(name)

            resource_search = gr.Dropdown(
                choices=sorted(set(all_names)),
                label="🔎 Search Resource",
                interactive=True,
                allow_custom_value=True,
            )
            resource_detail = gr.Markdown()

            resource_search.change(
                fn=monitor.get_detailed_resource_info,
                inputs=[resource_search],
                outputs=[resource_detail],
            )

        # Tab 4: FastAPI Monitor
        with gr.Tab("⚡ FastAPI Status"):
            gr.Markdown("### Real-time FastAPI Backend Monitoring")

            fastapi_test_btn = gr.Button("🧪 Test All Endpoints", variant="primary")

            def test_fastapi_full():
                endpoints = [
                    "/health",
                    "/api/status",
                    "/api/providers",
                    "/api/pools",
                    "/api/hf/health",
                    "/api/feature-flags",
                    "/api/data/market",
                    "/api/data/news",
                ]

                results = []
                for endpoint in endpoints:
                    try:
                        url = f"{monitor.fastapi_url}{endpoint}"
                        response = httpx.get(url, timeout=10)
                        results.append(
                            {
                                "Endpoint": endpoint,
                                "Status": "✅ Working" if response.status_code < 400 else "⚠️ Error",
                                "Code": response.status_code,
                                "Time": f"{response.elapsed.total_seconds() * 1000:.0f}ms",
                                "Size": f"{len(response.content)} bytes",
                            }
                        )
                    except Exception as e:
                        results.append(
                            {
                                "Endpoint": endpoint,
                                "Status": "❌ Failed",
                                "Code": "-",
                                "Time": "-",
                                "Size": str(e)[:50],
                            }
                        )

                df = pd.DataFrame(results)
                working = len([r for r in results if "✅" in r["Status"]])
                summary = f"**{working}/{len(results)} endpoints working**"
                return summary, df

            fastapi_summary = gr.Markdown()
            fastapi_df = gr.Dataframe()

            fastapi_test_btn.click(fn=test_fastapi_full, outputs=[fastapi_summary, fastapi_df])

        # Tab 5: HF Engine Monitor
        with gr.Tab("🤗 HF Data Engine"):
            gr.Markdown("### HuggingFace Data Engine Status")

            hf_test_btn = gr.Button("🧪 Test All Endpoints", variant="primary")

            def test_hf_full():
                endpoints = [
                    ("/api/health", "Health"),
                    ("/api/prices?symbols=BTC,ETH,SOL", "Prices"),
                    ("/api/ohlcv?symbol=BTC&interval=1h&limit=5", "OHLCV"),
                    ("/api/sentiment", "Sentiment"),
                    ("/api/market/overview", "Market"),
                    ("/api/cache/stats", "Cache Stats"),
                ]

                results = []
                for endpoint, name in endpoints:
                    try:
                        url = f"{monitor.hf_engine_url}{endpoint}"
                        start = time.time()
                        response = httpx.get(url, timeout=30)
                        latency = (time.time() - start) * 1000

                        results.append(
                            {
                                "Endpoint": name,
                                "URL": endpoint.split("?")[0],
                                "Status": "✅ Working" if response.status_code < 400 else "⚠️ Error",
                                "Latency": f"{latency:.0f}ms",
                                "Size": f"{len(response.content)} bytes",
                            }
                        )
                    except Exception as e:
                        results.append(
                            {
                                "Endpoint": name,
                                "URL": endpoint.split("?")[0],
                                "Status": "❌ Failed",
                                "Latency": "-",
                                "Size": str(e)[:50],
                            }
                        )

                df = pd.DataFrame(results)
                working = len([r for r in results if "✅" in r["Status"]])
                summary = f"**{working}/{len(results)} endpoints working**"
                return summary, df

            hf_summary = gr.Markdown()
            hf_df = gr.Dataframe()

            hf_test_btn.click(fn=test_hf_full, outputs=[hf_summary, hf_df])

        # Tab 6: Custom API Test
        with gr.Tab("🎯 Custom Test"):
            gr.Markdown("### Test Any API Endpoint")

            with gr.Row():
                with gr.Column():
                    custom_url = gr.Textbox(
                        label="URL", placeholder="https://api.example.com/endpoint", lines=1
                    )
                    custom_method = gr.Radio(
                        choices=["GET", "POST", "PUT", "DELETE"], label="Method", value="GET"
                    )
                    custom_headers = gr.Textbox(
                        label="Headers (JSON)",
                        placeholder='{"Authorization": "Bearer token"}',
                        lines=3,
                    )
                    custom_retry = gr.Slider(
                        minimum=1, maximum=5, value=3, step=1, label="Retry Attempts"
                    )
                    custom_test_btn = gr.Button("🚀 Test", variant="primary", size="lg")

                with gr.Column():
                    custom_result = gr.JSON(label="Result")

            async def test_custom(url, method, headers_str, retries):
                try:
                    headers = json.loads(headers_str) if headers_str else None
                except:
                    headers = None

                result = await monitor.force_test_endpoint(
                    url, method=method, headers=headers, retry_count=int(retries)
                )
                return result

            custom_test_btn.click(
                fn=test_custom,
                inputs=[custom_url, custom_method, custom_headers, custom_retry],
                outputs=[custom_result],
            )

        # Tab 7: Statistics & Analytics
        with gr.Tab("📊 Analytics"):
            gr.Markdown("### Comprehensive Analytics")

            def get_analytics():
                total_resources = 0
                by_category = defaultdict(int)
                by_source_file = {}

                for filename, data in monitor.api_resources.items():
                    file_count = 0

                    if isinstance(data, dict) and "registry" in data:
                        for sources in data["registry"].values():
                            if isinstance(sources, list):
                                file_count += len(sources)
                                for source in sources:
                                    cat = source.get(
                                        "category",
                                        source.get("chain", source.get("role", "unknown")),
                                    )
                                    by_category[cat] += 1

                    by_source_file[filename] = file_count
                    total_resources += file_count

                analytics = f"""
# 📊 Analytics Dashboard

## Resource Summary

**Total Resources:** {total_resources}

### By Source File
"""
                for filename, count in sorted(
                    by_source_file.items(), key=lambda x: x[1], reverse=True
                ):
                    analytics += f"- **{filename}:** {count} resources\n"

                analytics += "\n### By Category\n"
                for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
                    analytics += f"- **{cat}:** {count} resources\n"

                # Create DataFrame
                df_data = [
                    {"Metric": "Total Resources", "Value": total_resources},
                    {"Metric": "Source Files", "Value": len(by_source_file)},
                    {"Metric": "Categories", "Value": len(by_category)},
                    {
                        "Metric": "Avg per File",
                        "Value": f"{total_resources / max(len(by_source_file), 1):.0f}",
                    },
                ]

                return analytics, pd.DataFrame(df_data)

            analytics_md = gr.Markdown()
            analytics_df = gr.Dataframe()

            refresh_analytics_btn = gr.Button("🔄 Refresh Analytics", variant="primary")
            refresh_analytics_btn.click(fn=get_analytics, outputs=[analytics_md, analytics_df])

            # Auto-load on tab open
            demo.load(fn=get_analytics, outputs=[analytics_md, analytics_df])

    # Footer
    gr.Markdown(
        """
---
**ULTIMATE Crypto Data Sources Monitor** • v2.0 • Built with ❤️ using Gradio
    """
    )


if __name__ == "__main__":
    print("🚀 Starting ULTIMATE Crypto Monitor Dashboard...")
    print(f"📊 Loaded {len(monitor.api_resources)} resource files")

    demo.launch(server_name="0.0.0.0", server_port=7861, share=False, show_error=True, quiet=False)
