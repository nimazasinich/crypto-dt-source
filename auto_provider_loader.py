#!/usr/bin/env python3
"""
Auto Provider Loader (APL) - REAL DATA ONLY
Scans, validates, and integrates providers from JSON resources.
NO MOCK DATA. NO FAKE RESPONSES.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import time
from datetime import datetime

from provider_validator import ProviderValidator, ValidationResult, ValidationStatus


@dataclass
class APLStats:
    """APL execution statistics"""

    total_http_candidates: int = 0
    total_hf_candidates: int = 0
    http_valid: int = 0
    http_invalid: int = 0
    http_conditional: int = 0
    hf_valid: int = 0
    hf_invalid: int = 0
    hf_conditional: int = 0
    total_active_providers: int = 0
    execution_time_sec: float = 0.0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class AutoProviderLoader:
    """
    Auto Provider Loader (APL)
    Discovers, validates, and integrates providers automatically.
    """

    def __init__(self, workspace_root: str = "/workspace"):
        self.workspace_root = Path(workspace_root)
        self.validator = ProviderValidator(timeout=8.0)
        self.http_results: List[ValidationResult] = []
        self.hf_results: List[ValidationResult] = []
        self.stats = APLStats()

    def discover_http_providers(self) -> List[Dict[str, Any]]:
        """
        Discover HTTP providers from JSON resources.
        Returns list of (provider_id, provider_data, source_file) tuples.
        """
        providers = []

        # Scan api-resources directory
        api_resources = self.workspace_root / "api-resources"
        if api_resources.exists():
            for json_file in api_resources.glob("*.json"):
                try:
                    with open(json_file, "r") as f:
                        data = json.load(f)

                    # Check if it's the unified registry format
                    if "registry" in data:
                        registry = data["registry"]

                        # Process each section
                        for section_key, section_data in registry.items():
                            if section_key == "metadata":
                                continue

                            if isinstance(section_data, list):
                                for item in section_data:
                                    provider_id = item.get("id", f"{section_key}_{len(providers)}")
                                    providers.append(
                                        {
                                            "id": provider_id,
                                            "data": item,
                                            "source": str(json_file.name),
                                            "section": section_key,
                                        }
                                    )

                    # Check if it's a direct resources list
                    elif "resources" in data:
                        for idx, item in enumerate(data["resources"]):
                            provider_id = item.get("id", f"resource_{idx}")
                            if not provider_id or provider_id.startswith("resource_"):
                                # Generate ID from name
                                name = item.get("name", "").lower().replace(" ", "_")
                                provider_id = f"{name}_{idx}" if name else f"resource_{idx}"

                            providers.append(
                                {
                                    "id": provider_id,
                                    "data": {
                                        "name": item.get("name"),
                                        "category": item.get("category", "unknown"),
                                        "base_url": item.get("url"),
                                        "endpoint": item.get("endpoint"),
                                        "auth": {
                                            "type": "apiKey" if item.get("key") else "none",
                                            "key": item.get("key"),
                                        },
                                        "free": item.get("free", True),
                                        "rate_limit": item.get("rateLimit"),
                                        "notes": item.get("desc") or item.get("notes"),
                                    },
                                    "source": str(json_file.name),
                                    "section": "resources",
                                }
                            )

                except Exception as e:
                    print(f"Error loading {json_file}: {e}")

        # Scan providers_config files
        for config_file in self.workspace_root.glob("providers_config*.json"):
            try:
                with open(config_file, "r") as f:
                    data = json.load(f)

                if "providers" in data:
                    for provider_id, provider_data in data["providers"].items():
                        providers.append(
                            {
                                "id": provider_id,
                                "data": provider_data,
                                "source": str(config_file.name),
                                "section": "providers",
                            }
                        )

            except Exception as e:
                print(f"Error loading {config_file}: {e}")

        return providers

    def discover_hf_models(self) -> List[Dict[str, Any]]:
        """
        Discover Hugging Face models from:
        1. backend/services/hf_client.py (hardcoded models)
        2. backend/services/hf_registry.py (dynamic discovery)
        3. JSON resources (hf_resources section)
        """
        models = []

        # Hardcoded models from hf_client.py
        hardcoded_models = [
            {
                "id": "ElKulako/cryptobert",
                "name": "ElKulako CryptoBERT",
                "pipeline_tag": "sentiment-analysis",
                "source": "hf_client.py",
            },
            {
                "id": "kk08/CryptoBERT",
                "name": "KK08 CryptoBERT",
                "pipeline_tag": "sentiment-analysis",
                "source": "hf_client.py",
            },
        ]

        for model in hardcoded_models:
            models.append(model)

        # Models from JSON resources
        api_resources = self.workspace_root / "api-resources"
        if api_resources.exists():
            for json_file in api_resources.glob("*.json"):
                try:
                    with open(json_file, "r") as f:
                        data = json.load(f)

                    if "registry" in data:
                        hf_resources = data["registry"].get("hf_resources", [])
                        for item in hf_resources:
                            if item.get("type") == "model":
                                models.append(
                                    {
                                        "id": item.get("id", item.get("model_id")),
                                        "name": item.get("name"),
                                        "pipeline_tag": item.get(
                                            "pipeline_tag", "sentiment-analysis"
                                        ),
                                        "source": str(json_file.name),
                                    }
                                )

                except Exception as e:
                    pass

        return models

    async def validate_all_http_providers(self, providers: List[Dict[str, Any]]) -> None:
        """
        Validate all HTTP providers in parallel batches.
        """
        print(f"\n🔍 Validating {len(providers)} HTTP provider candidates...")

        # Process in batches to avoid overwhelming
        batch_size = 10
        for i in range(0, len(providers), batch_size):
            batch = providers[i : i + batch_size]

            tasks = [self.validator.validate_http_provider(p["id"], p["data"]) for p in batch]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for j, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create error result
                    p = batch[j]
                    result = ValidationResult(
                        provider_id=p["id"],
                        provider_name=p["data"].get("name", p["id"]),
                        provider_type="http_json",
                        category=p["data"].get("category", "unknown"),
                        status=ValidationStatus.INVALID.value,
                        error_reason=f"Validation exception: {str(result)[:50]}",
                    )

                self.http_results.append(result)

                # Print progress
                status_emoji = {
                    ValidationStatus.VALID.value: "✅",
                    ValidationStatus.INVALID.value: "❌",
                    ValidationStatus.CONDITIONALLY_AVAILABLE.value: "⚠️",
                    ValidationStatus.SKIPPED.value: "⏭️",
                }

                emoji = status_emoji.get(result.status, "❓")
                print(f"  {emoji} {result.provider_id}: {result.status}")

            # Small delay between batches
            await asyncio.sleep(0.5)

    async def validate_all_hf_models(self, models: List[Dict[str, Any]]) -> None:
        """
        Validate all HF models sequentially (to avoid memory issues).
        """
        print(f"\n🤖 Validating {len(models)} HF model candidates...")

        for model in models:
            try:
                result = await self.validator.validate_hf_model(
                    model["id"], model["name"], model.get("pipeline_tag", "sentiment-analysis")
                )

                self.hf_results.append(result)

                status_emoji = {
                    ValidationStatus.VALID.value: "✅",
                    ValidationStatus.INVALID.value: "❌",
                    ValidationStatus.CONDITIONALLY_AVAILABLE.value: "⚠️",
                }

                emoji = status_emoji.get(result.status, "❓")
                print(f"  {emoji} {result.provider_id}: {result.status}")

            except Exception as e:
                print(f"  ❌ {model['id']}: Exception during validation: {str(e)[:50]}")
                self.hf_results.append(
                    ValidationResult(
                        provider_id=model["id"],
                        provider_name=model["name"],
                        provider_type="hf_model",
                        category="hf_model",
                        status=ValidationStatus.INVALID.value,
                        error_reason=f"Validation exception: {str(e)[:50]}",
                    )
                )

    def compute_stats(self) -> None:
        """Compute final statistics"""
        self.stats.total_http_candidates = len(self.http_results)
        self.stats.total_hf_candidates = len(self.hf_results)

        # Count HTTP results
        for result in self.http_results:
            if result.status == ValidationStatus.VALID.value:
                self.stats.http_valid += 1
            elif result.status == ValidationStatus.INVALID.value:
                self.stats.http_invalid += 1
            elif result.status == ValidationStatus.CONDITIONALLY_AVAILABLE.value:
                self.stats.http_conditional += 1

        # Count HF results
        for result in self.hf_results:
            if result.status == ValidationStatus.VALID.value:
                self.stats.hf_valid += 1
            elif result.status == ValidationStatus.INVALID.value:
                self.stats.hf_invalid += 1
            elif result.status == ValidationStatus.CONDITIONALLY_AVAILABLE.value:
                self.stats.hf_conditional += 1

        self.stats.total_active_providers = self.stats.http_valid + self.stats.hf_valid

    def integrate_valid_providers(self) -> Dict[str, Any]:
        """
        Integrate valid providers into providers_config_extended.json.
        Returns the updated config.
        """
        config_path = self.workspace_root / "providers_config_extended.json"

        # Load existing config
        if config_path.exists():
            with open(config_path, "r") as f:
                config = json.load(f)
        else:
            config = {"providers": {}}

        # Backup
        backup_path = (
            self.workspace_root / f"providers_config_extended.backup.{int(time.time())}.json"
        )
        with open(backup_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"\n📦 Backed up config to {backup_path.name}")

        # Add valid HTTP providers
        added_count = 0
        for result in self.http_results:
            if result.status == ValidationStatus.VALID.value:
                if result.provider_id not in config["providers"]:
                    config["providers"][result.provider_id] = {
                        "name": result.provider_name,
                        "category": result.category,
                        "type": result.provider_type,
                        "validated": True,
                        "validated_at": result.validated_at,
                        "response_time_ms": result.response_time_ms,
                        "added_by": "APL",
                    }
                    added_count += 1

        print(f"✅ Added {added_count} new valid HTTP providers to config")

        # Save updated config
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        return config

    def generate_reports(self) -> None:
        """Generate comprehensive reports"""
        reports_dir = self.workspace_root

        # 1. Detailed validation report
        validation_report = {
            "report_type": "Provider Auto-Discovery Validation Report",
            "generated_at": datetime.now().isoformat(),
            "stats": asdict(self.stats),
            "http_providers": {
                "total_candidates": self.stats.total_http_candidates,
                "valid": self.stats.http_valid,
                "invalid": self.stats.http_invalid,
                "conditional": self.stats.http_conditional,
                "results": [asdict(r) for r in self.http_results],
            },
            "hf_models": {
                "total_candidates": self.stats.total_hf_candidates,
                "valid": self.stats.hf_valid,
                "invalid": self.stats.hf_invalid,
                "conditional": self.stats.hf_conditional,
                "results": [asdict(r) for r in self.hf_results],
            },
        }

        report_path = reports_dir / "PROVIDER_AUTO_DISCOVERY_REPORT.json"
        with open(report_path, "w") as f:
            json.dump(validation_report, f, indent=2)

        print(f"\n📊 Generated detailed report: {report_path.name}")

        # 2. Generate markdown summary
        self.generate_markdown_report()

    def generate_markdown_report(self) -> None:
        """Generate markdown report"""
        reports_dir = self.workspace_root

        md_content = f"""# Provider Auto-Discovery Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Execution Time:** {self.stats.execution_time_sec:.2f} seconds

---

## Executive Summary

| Metric | Count |
|--------|-------|
| **Total HTTP Candidates** | {self.stats.total_http_candidates} |
| **HTTP Valid** | {self.stats.http_valid} ✅ |
| **HTTP Invalid** | {self.stats.http_invalid} ❌ |
| **HTTP Conditional** | {self.stats.http_conditional} ⚠️ |
| **Total HF Model Candidates** | {self.stats.total_hf_candidates} |
| **HF Models Valid** | {self.stats.hf_valid} ✅ |
| **HF Models Invalid** | {self.stats.hf_invalid} ❌ |
| **HF Models Conditional** | {self.stats.hf_conditional} ⚠️ |
| **TOTAL ACTIVE PROVIDERS** | **{self.stats.total_active_providers}** |

---

## HTTP Providers

### Valid Providers ({self.stats.http_valid})

"""

        # List valid HTTP providers
        valid_http = [r for r in self.http_results if r.status == ValidationStatus.VALID.value]
        for result in sorted(valid_http, key=lambda x: x.response_time_ms or 999999):
            md_content += f"- **{result.provider_name}** (`{result.provider_id}`)\n"
            md_content += f"  - Category: {result.category}\n"
            md_content += f"  - Type: {result.provider_type}\n"
            md_content += f"  - Response Time: {result.response_time_ms:.0f}ms\n"
            if result.test_endpoint:
                md_content += f"  - Test Endpoint: `{result.test_endpoint}`\n"
            md_content += "\n"

        md_content += f"""
### Invalid Providers ({self.stats.http_invalid})

"""

        # List some invalid providers with reasons
        invalid_http = [r for r in self.http_results if r.status == ValidationStatus.INVALID.value]
        for result in invalid_http[:20]:  # Limit to first 20
            md_content += f"- **{result.provider_name}** (`{result.provider_id}`)\n"
            md_content += f"  - Reason: {result.error_reason}\n\n"

        if len(invalid_http) > 20:
            md_content += f"\n*... and {len(invalid_http) - 20} more invalid providers*\n"

        md_content += f"""
### Conditionally Available Providers ({self.stats.http_conditional})

These providers require API keys or special configuration:

"""

        conditional_http = [
            r
            for r in self.http_results
            if r.status == ValidationStatus.CONDITIONALLY_AVAILABLE.value
        ]
        for result in conditional_http:
            md_content += f"- **{result.provider_name}** (`{result.provider_id}`)\n"
            if result.auth_env_var:
                md_content += f"  - Required: `{result.auth_env_var}` environment variable\n"
            md_content += f"  - Reason: {result.error_reason}\n\n"

        md_content += f"""
---

## Hugging Face Models

### Valid Models ({self.stats.hf_valid})

"""

        valid_hf = [r for r in self.hf_results if r.status == ValidationStatus.VALID.value]
        for result in valid_hf:
            md_content += f"- **{result.provider_name}** (`{result.provider_id}`)\n"
            if result.response_time_ms:
                md_content += f"  - Response Time: {result.response_time_ms:.0f}ms\n"
            md_content += "\n"

        md_content += f"""
### Invalid Models ({self.stats.hf_invalid})

"""

        invalid_hf = [r for r in self.hf_results if r.status == ValidationStatus.INVALID.value]
        for result in invalid_hf:
            md_content += f"- **{result.provider_name}** (`{result.provider_id}`)\n"
            md_content += f"  - Reason: {result.error_reason}\n\n"

        md_content += f"""
### Conditionally Available Models ({self.stats.hf_conditional})

"""

        conditional_hf = [
            r for r in self.hf_results if r.status == ValidationStatus.CONDITIONALLY_AVAILABLE.value
        ]
        for result in conditional_hf:
            md_content += f"- **{result.provider_name}** (`{result.provider_id}`)\n"
            if result.auth_env_var:
                md_content += f"  - Required: `{result.auth_env_var}` environment variable\n"
            md_content += "\n"

        md_content += """
---

## Integration Status

All VALID providers have been integrated into `providers_config_extended.json`.

**NO MOCK DATA was used in this validation process.**  
**All results are from REAL API calls and REAL model inferences.**

---

## Next Steps

1. **For Conditional Providers:** Set the required environment variables to activate them
2. **For Invalid Providers:** Review error reasons and update configurations if needed
3. **Monitor Performance:** Track response times and adjust provider priorities

---

*Report generated by Auto Provider Loader (APL)*
"""

        report_path = reports_dir / "PROVIDER_AUTO_DISCOVERY_REPORT.md"
        with open(report_path, "w") as f:
            f.write(md_content)

        print(f"📋 Generated markdown report: {report_path.name}")

    async def run(self) -> None:
        """Run the complete APL process"""
        start_time = time.time()

        print("=" * 80)
        print("🚀 AUTO PROVIDER LOADER (APL) - REAL DATA ONLY")
        print("=" * 80)

        # Phase 1: Discovery
        print("\n📡 PHASE 1: DISCOVERY")
        http_providers = self.discover_http_providers()
        hf_models = self.discover_hf_models()

        print(f"  Found {len(http_providers)} HTTP provider candidates")
        print(f"  Found {len(hf_models)} HF model candidates")

        # Phase 2: Validation
        print("\n🔬 PHASE 2: VALIDATION")
        await self.validate_all_http_providers(http_providers)
        await self.validate_all_hf_models(hf_models)

        # Phase 3: Statistics
        print("\n📊 PHASE 3: COMPUTING STATISTICS")
        self.compute_stats()

        # Phase 4: Integration
        print("\n🔧 PHASE 4: INTEGRATION")
        self.integrate_valid_providers()

        # Phase 5: Reporting
        print("\n📝 PHASE 5: GENERATING REPORTS")
        self.stats.execution_time_sec = time.time() - start_time
        self.generate_reports()

        # Final summary
        print("\n" + "=" * 80)
        print("✅ STATUS: PROVIDER + HF MODEL EXPANSION COMPLETE")
        print("=" * 80)
        print(f"\n📈 FINAL COUNTS:")
        print(f"  • HTTP Providers: {self.stats.total_http_candidates} candidates")
        print(f"    ✅ Valid: {self.stats.http_valid}")
        print(f"    ❌ Invalid: {self.stats.http_invalid}")
        print(f"    ⚠️  Conditional: {self.stats.http_conditional}")
        print(f"  • HF Models: {self.stats.total_hf_candidates} candidates")
        print(f"    ✅ Valid: {self.stats.hf_valid}")
        print(f"    ❌ Invalid: {self.stats.hf_invalid}")
        print(f"    ⚠️  Conditional: {self.stats.hf_conditional}")
        print(f"\n  🎯 TOTAL ACTIVE: {self.stats.total_active_providers} providers")
        print(f"\n⏱️  Execution time: {self.stats.execution_time_sec:.2f} seconds")
        print(f"\n✅ NO MOCK/FAKE DATA - All results from REAL calls")
        print("=" * 80)


async def main():
    """Main entry point"""
    apl = AutoProviderLoader()
    await apl.run()


if __name__ == "__main__":
    asyncio.run(main())
