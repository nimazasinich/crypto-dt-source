#!/usr/bin/env python3
"""
Auto Provider Loader (APL)
Automatically discovers, validates, and integrates crypto API providers
"""

import json
import asyncio
import os
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

from provider_validator import ProviderValidator, ValidationResult, ValidationStatus


@dataclass
class ProviderCandidate:
    """A candidate provider discovered from scanning"""
    provider_id: str
    name: str
    category: str
    base_url: str
    endpoints: Dict[str, Any]
    requires_auth: bool = False
    priority: int = 5
    weight: int = 50
    rate_limit: Dict[str, Any] = field(default_factory=dict)
    api_keys: List[str] = field(default_factory=list)
    auth_type: str = "query"
    auth_param: str = "apikey"
    auth_header: str = "Authorization"
    source_file: str = ""
    
    def to_provider_dict(self) -> Dict[str, Any]:
        """Convert to provider config format"""
        return {
            "name": self.name,
            "category": self.category,
            "base_url": self.base_url,
            "endpoints": self.endpoints,
            "rate_limit": self.rate_limit,
            "requires_auth": self.requires_auth,
            "priority": self.priority,
            "weight": self.weight,
            "api_keys": self.api_keys,
            "auth_type": self.auth_type,
            "auth_param": self.auth_param,
            "auth_header": self.auth_header
        }


class AutoProviderLoader:
    """
    Automatically discovers and validates crypto API providers
    """
    
    def __init__(
        self,
        scan_directories: List[str] = None,
        config_path: str = "providers_config_extended.json",
        validator_timeout: int = 10,
        validator_concurrency: int = 5
    ):
        self.scan_directories = scan_directories or ["api-resources", "."]
        self.config_path = config_path
        self.validator = ProviderValidator(
            timeout=validator_timeout,
            max_concurrent=validator_concurrency
        )
        
        self.discovered_providers: Dict[str, ProviderCandidate] = {}
        self.existing_providers: Set[str] = set()
        self.validation_results: Dict[str, ValidationResult] = {}
        
        # Statistics
        self.stats = {
            "files_scanned": 0,
            "candidates_discovered": 0,
            "duplicates_skipped": 0,
            "valid_providers": 0,
            "invalid_providers": 0,
            "providers_added": 0
        }
    
    def load_existing_config(self):
        """Load existing provider config to avoid duplicates"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            providers = config.get('providers', {})
            self.existing_providers = set(providers.keys())
            
            print(f"✅ Loaded existing config: {len(self.existing_providers)} providers")
        
        except FileNotFoundError:
            print(f"⚠️ Config file not found: {self.config_path}, will create new one")
        except Exception as e:
            print(f"❌ Error loading config: {e}")
    
    def scan_for_provider_files(self) -> List[Path]:
        """Scan designated directories for JSON files with provider definitions"""
        provider_files = []
        
        for directory in self.scan_directories:
            dir_path = Path(directory)
            
            if not dir_path.exists():
                print(f"⚠️ Directory not found: {directory}")
                continue
            
            # Find all JSON files
            json_files = list(dir_path.glob("*.json"))
            
            # Also check subdirectories
            if dir_path.is_dir():
                for subdir in dir_path.iterdir():
                    if subdir.is_dir():
                        json_files.extend(subdir.glob("*.json"))
            
            provider_files.extend(json_files)
        
        # Filter out the main config file itself
        provider_files = [f for f in provider_files if f.name != Path(self.config_path).name]
        
        print(f"📂 Found {len(provider_files)} JSON files to scan")
        return provider_files
    
    def _normalize_category(self, category: str) -> str:
        """Normalize category names"""
        category = category.lower().strip()
        
        # Mapping of various category names to standard ones
        mapping = {
            "market": "market_data",
            "price": "market_data",
            "prices": "market_data",
            "exchange": "exchange",
            "explorer": "blockchain_explorers",
            "block_explorer": "blockchain_explorers",
            "blockchain_explorer": "blockchain_explorers",
            "blockchain": "blockchain_data",
            "defi": "defi",
            "nft": "nft",
            "news": "news",
            "social": "social",
            "sentiment": "sentiment",
            "analytics": "analytics",
            "onchain": "analytics",
            "on-chain": "analytics",
            "whale": "whale_tracking",
            "whales": "whale_tracking",
            "whale_tracking": "whale_tracking",
            "rpc": "rpc",
            "websocket": "rpc",
            "ml_model": "ml_model"
        }
        
        return mapping.get(category, category)
    
    def _parse_ultimate_crypto_pipeline(self, data: Dict, source_file: str):
        """Parse ultimate_crypto_pipeline_2025_NZasinich.json format"""
        files = data.get('files', [])
        
        for file_entry in files:
            content = file_entry.get('content', {})
            resources = content.get('resources', [])
            
            for resource in resources:
                # Extract provider info
                provider_id = resource.get('name', '').lower().replace(' ', '_').replace('(', '').replace(')', '')
                if not provider_id:
                    continue
                
                # Skip if already exists
                if provider_id in self.existing_providers or provider_id in self.discovered_providers:
                    self.stats["duplicates_skipped"] += 1
                    continue
                
                name = resource.get('name', provider_id)
                category = self._normalize_category(resource.get('category', 'generic'))
                base_url = resource.get('url', '')
                
                if not base_url:
                    continue
                
                # Parse endpoint
                endpoint_path = resource.get('endpoint', '')
                endpoints = {}
                if endpoint_path:
                    endpoints['default'] = endpoint_path
                
                # Check for API key
                api_key = resource.get('key', '')
                requires_auth = bool(api_key) and api_key != ""
                api_keys = [api_key] if requires_auth else []
                
                # Rate limit
                rate_limit = {}
                if 'rateLimit' in resource:
                    rate_limit_str = resource['rateLimit']
                    # Try to parse rate limit (e.g., "1440/day", "3/sec")
                    if '/' in rate_limit_str:
                        try:
                            count, period = rate_limit_str.split('/')
                            count = int(count.strip())
                            period = period.strip().lower()
                            
                            if 'sec' in period:
                                rate_limit['requests_per_second'] = count
                            elif 'min' in period:
                                rate_limit['requests_per_minute'] = count
                            elif 'hour' in period:
                                rate_limit['requests_per_hour'] = count
                            elif 'day' in period:
                                rate_limit['requests_per_day'] = count
                        except:
                            pass
                
                # Create candidate
                candidate = ProviderCandidate(
                    provider_id=provider_id,
                    name=name,
                    category=category,
                    base_url=base_url,
                    endpoints=endpoints,
                    requires_auth=requires_auth,
                    api_keys=api_keys,
                    rate_limit=rate_limit,
                    source_file=source_file
                )
                
                self.discovered_providers[provider_id] = candidate
                self.stats["candidates_discovered"] += 1
    
    def _parse_crypto_resources_unified(self, data: Dict, source_file: str):
        """Parse crypto_resources_unified_2025-11-11.json format"""
        registry = data.get('registry', {})
        
        # Parse different sections
        sections = ['rpc_nodes', 'market_data', 'block_explorers', 
                   'defi', 'news', 'sentiment', 'analytics']
        
        for section in sections:
            items = registry.get(section, [])
            
            for item in items:
                provider_id = item.get('id', '')
                if not provider_id:
                    continue
                
                # Skip if already exists
                if provider_id in self.existing_providers or provider_id in self.discovered_providers:
                    self.stats["duplicates_skipped"] += 1
                    continue
                
                name = item.get('name', provider_id)
                base_url = item.get('base_url', '')
                
                if not base_url:
                    continue
                
                # Determine category
                category = self._normalize_category(item.get('category', section))
                if 'chain' in item:
                    category = 'blockchain_explorers'
                if 'role' in item and item['role'] == 'rpc':
                    category = 'rpc'
                
                # Parse endpoints
                endpoints = item.get('endpoints', {})
                if isinstance(endpoints, str):
                    endpoints = {'default': endpoints}
                
                # Parse auth
                auth_info = item.get('auth', {})
                requires_auth = auth_info.get('type') in ['apiKey', 'apiKeyPath', 'header']
                api_key = auth_info.get('key', '')
                api_keys = [api_key] if api_key else []
                
                # Rate limit
                rate_limit = item.get('rate_limit', {})
                
                # Create candidate
                candidate = ProviderCandidate(
                    provider_id=provider_id,
                    name=name,
                    category=category,
                    base_url=base_url,
                    endpoints=endpoints,
                    requires_auth=requires_auth,
                    api_keys=api_keys,
                    rate_limit=rate_limit,
                    source_file=source_file
                )
                
                self.discovered_providers[provider_id] = candidate
                self.stats["candidates_discovered"] += 1
    
    def _parse_providers_config_format(self, data: Dict, source_file: str):
        """Parse providers_config format (extended/ultimate)"""
        providers = data.get('providers', {})
        
        for provider_id, provider_data in providers.items():
            # Skip if already exists
            if provider_id in self.existing_providers or provider_id in self.discovered_providers:
                self.stats["duplicates_skipped"] += 1
                continue
            
            # Extract data
            name = provider_data.get('name', provider_id)
            category = self._normalize_category(provider_data.get('category', 'generic'))
            base_url = provider_data.get('base_url', '')
            
            if not base_url:
                continue
            
            endpoints = provider_data.get('endpoints', {})
            requires_auth = provider_data.get('requires_auth', False)
            rate_limit = provider_data.get('rate_limit', {})
            priority = provider_data.get('priority', 5)
            weight = provider_data.get('weight', 50)
            
            # API keys
            api_keys = provider_data.get('api_keys', [])
            if isinstance(api_keys, str):
                api_keys = [api_keys]
            
            # Create candidate
            candidate = ProviderCandidate(
                provider_id=provider_id,
                name=name,
                category=category,
                base_url=base_url,
                endpoints=endpoints,
                requires_auth=requires_auth,
                api_keys=api_keys,
                rate_limit=rate_limit,
                priority=priority,
                weight=weight,
                source_file=source_file
            )
            
            self.discovered_providers[provider_id] = candidate
            self.stats["candidates_discovered"] += 1
    
    def parse_provider_file(self, file_path: Path):
        """Parse a JSON file and extract provider definitions"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.stats["files_scanned"] += 1
            
            # Detect format and parse accordingly
            if 'project' in data and 'Ultimate Free Crypto Data Pipeline' in data.get('project', ''):
                self._parse_ultimate_crypto_pipeline(data, str(file_path))
            
            elif 'registry' in data:
                self._parse_crypto_resources_unified(data, str(file_path))
            
            elif 'providers' in data:
                self._parse_providers_config_format(data, str(file_path))
            
            else:
                # Try to detect other formats
                print(f"  ⚠️ Unknown format: {file_path.name}")
        
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON in {file_path.name}: {e}")
        except Exception as e:
            print(f"  ❌ Error parsing {file_path.name}: {e}")
    
    def discover_providers(self):
        """Main discovery process: scan files and extract provider candidates"""
        print("\n" + "="*80)
        print("PHASE 1: PROVIDER DISCOVERY")
        print("="*80 + "\n")
        
        # Load existing config
        self.load_existing_config()
        
        # Scan for files
        provider_files = self.scan_for_provider_files()
        
        # Parse each file
        print("\n📖 Parsing provider files...")
        for file_path in provider_files:
            print(f"  Processing: {file_path.name}")
            self.parse_provider_file(file_path)
        
        print(f"\n✅ Discovery complete:")
        print(f"   - Files scanned: {self.stats['files_scanned']}")
        print(f"   - Candidates discovered: {self.stats['candidates_discovered']}")
        print(f"   - Duplicates skipped: {self.stats['duplicates_skipped']}")
    
    async def validate_providers(self):
        """Validate discovered providers with real HTTP calls"""
        print("\n" + "="*80)
        print("PHASE 2: PROVIDER VALIDATION")
        print("="*80 + "\n")
        
        if not self.discovered_providers:
            print("⚠️ No providers to validate")
            return
        
        print(f"🔍 Validating {len(self.discovered_providers)} providers...")
        print(f"   (timeout={self.validator.timeout}s, concurrency={self.validator.max_concurrent})")
        print()
        
        # Prepare providers for validation
        providers_to_validate = {
            pid: candidate.to_provider_dict()
            for pid, candidate in self.discovered_providers.items()
        }
        
        # Progress callback
        def progress(current, total, provider_id):
            result = self.validation_results.get(provider_id)
            status_icon = "✅" if result and result.status == ValidationStatus.VALID else "❌"
            print(f"  [{current}/{total}] {status_icon} {provider_id}")
        
        # Validate
        self.validation_results = await self.validator.validate_providers(
            providers_to_validate,
            progress
        )
        
        # Update stats
        for result in self.validation_results.values():
            if result.status == ValidationStatus.VALID:
                self.stats["valid_providers"] += 1
            else:
                self.stats["invalid_providers"] += 1
        
        # Get validation statistics
        validation_stats = self.validator.get_statistics(self.validation_results)
        
        print(f"\n📊 Validation Statistics:")
        print(f"   - Total: {validation_stats['total']}")
        print(f"   - Valid: {validation_stats['valid']} ({validation_stats['validation_rate']:.1f}%)")
        print(f"   - Invalid: {validation_stats['invalid']}")
        print(f"   - Requires Auth: {validation_stats['requires_auth']}")
        print(f"   - Timeout: {validation_stats['timeout']}")
        print(f"   - Rate Limited: {validation_stats['rate_limited']}")
        print(f"   - Avg Response Time: {validation_stats['avg_response_time_ms']:.2f}ms")
        
        await self.validator.close_session()
    
    def integrate_valid_providers(self):
        """Integrate valid providers into main config"""
        print("\n" + "="*80)
        print("PHASE 3: INTEGRATION")
        print("="*80 + "\n")
        
        # Load current config
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {
                "providers": {},
                "pool_configurations": [],
                "fallback_strategy": {
                    "max_retries": 3,
                    "retry_delay_seconds": 2,
                    "circuit_breaker_threshold": 5,
                    "circuit_breaker_timeout_seconds": 60
                }
            }
        
        providers_section = config.get('providers', {})
        pools_section = config.get('pool_configurations', [])
        
        # Add valid providers
        providers_added = 0
        
        for provider_id, result in self.validation_results.items():
            if result.status == ValidationStatus.VALID:
                candidate = self.discovered_providers[provider_id]
                
                # Add to providers section
                providers_section[provider_id] = candidate.to_provider_dict()
                providers_added += 1
                
                print(f"  ✅ Added: {provider_id} ({candidate.category})")
        
        # Update pools
        # Group new providers by category
        category_providers = {}
        for provider_id, result in self.validation_results.items():
            if result.status == ValidationStatus.VALID:
                candidate = self.discovered_providers[provider_id]
                category = candidate.category
                
                if category not in category_providers:
                    category_providers[category] = []
                category_providers[category].append(provider_id)
        
        # Update existing pools or create new ones
        existing_pool_categories = {pool['category']: pool for pool in pools_section}
        
        for category, provider_list in category_providers.items():
            if category in existing_pool_categories:
                # Add to existing pool
                pool = existing_pool_categories[category]
                existing_providers = set(pool.get('providers', []))
                new_providers = [p for p in provider_list if p not in existing_providers]
                
                if new_providers:
                    pool['providers'].extend(new_providers)
                    print(f"  🔄 Updated pool '{pool['pool_name']}': +{len(new_providers)} providers")
            else:
                # Create new pool
                pool_name = f"{category.replace('_', ' ').title()} Pool"
                new_pool = {
                    "pool_name": pool_name,
                    "category": category,
                    "rotation_strategy": "priority",
                    "providers": provider_list
                }
                pools_section.append(new_pool)
                print(f"  ➕ Created pool '{pool_name}': {len(provider_list)} providers")
        
        # Save updated config
        config['providers'] = providers_section
        config['pool_configurations'] = pools_section
        
        # Backup existing config
        backup_path = f"{self.config_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if os.path.exists(self.config_path):
            os.rename(self.config_path, backup_path)
            print(f"\n  💾 Backed up existing config to: {backup_path}")
        
        # Write new config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.stats["providers_added"] = providers_added
        
        print(f"\n✅ Integration complete:")
        print(f"   - Providers added: {providers_added}")
        print(f"   - Config updated: {self.config_path}")
    
    def generate_report(self, report_path: str = "PROVIDER_AUTO_DISCOVERY_REPORT.md"):
        """Generate comprehensive discovery and validation report"""
        print("\n" + "="*80)
        print("PHASE 4: REPORT GENERATION")
        print("="*80 + "\n")
        
        report_lines = []
        
        # Header
        report_lines.append("# Provider Auto Discovery Report")
        report_lines.append("")
        report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Summary
        report_lines.append("## Summary")
        report_lines.append("")
        report_lines.append(f"- **Files Scanned:** {self.stats['files_scanned']}")
        report_lines.append(f"- **Candidate Providers Discovered:** {self.stats['candidates_discovered']}")
        report_lines.append(f"- **Duplicates Skipped:** {self.stats['duplicates_skipped']}")
        report_lines.append(f"- **Valid Providers:** {self.stats['valid_providers']}")
        report_lines.append(f"- **Invalid Providers:** {self.stats['invalid_providers']}")
        report_lines.append(f"- **Providers Added to Config:** {self.stats['providers_added']}")
        report_lines.append("")
        
        # Valid Providers
        report_lines.append("## Valid Providers")
        report_lines.append("")
        report_lines.append("These providers passed validation and were added to the configuration:")
        report_lines.append("")
        report_lines.append("| Provider ID | Name | Category | Base URL | Response Time (ms) |")
        report_lines.append("|------------|------|----------|----------|-------------------|")
        
        for provider_id, result in sorted(self.validation_results.items()):
            if result.status == ValidationStatus.VALID:
                candidate = self.discovered_providers[provider_id]
                response_time = f"{result.response_time_ms:.2f}" if result.response_time_ms else "N/A"
                report_lines.append(f"| `{provider_id}` | {candidate.name} | {candidate.category} | {candidate.base_url} | {response_time} |")
        
        report_lines.append("")
        
        # Invalid Providers
        report_lines.append("## Invalid Providers")
        report_lines.append("")
        report_lines.append("These providers failed validation and were NOT added:")
        report_lines.append("")
        report_lines.append("| Provider ID | Name | Category | Base URL | Error |")
        report_lines.append("|------------|------|----------|----------|-------|")
        
        for provider_id, result in sorted(self.validation_results.items()):
            if result.status != ValidationStatus.VALID:
                candidate = self.discovered_providers[provider_id]
                error = result.error_message or result.status.value
                error_short = error[:100] + "..." if len(error) > 100 else error
                report_lines.append(f"| `{provider_id}` | {candidate.name} | {candidate.category} | {candidate.base_url} | {error_short} |")
        
        report_lines.append("")
        
        # Integration Notes
        report_lines.append("## Integration Notes")
        report_lines.append("")
        report_lines.append(f"- **Config File Updated:** `{self.config_path}`")
        report_lines.append(f"- **Backup Created:** `{self.config_path}.backup_*`")
        report_lines.append("")
        report_lines.append("### Pool Assignments")
        report_lines.append("")
        
        # List pools updated/created
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for pool in config.get('pool_configurations', []):
                pool_name = pool['pool_name']
                pool_category = pool['category']
                pool_providers = pool.get('providers', [])
                
                # Check which providers are new
                new_providers = [p for p in pool_providers if p in self.validation_results 
                                and self.validation_results[p].status == ValidationStatus.VALID]
                
                if new_providers:
                    report_lines.append(f"- **{pool_name}** ({pool_category}): {len(pool_providers)} total providers, {len(new_providers)} new")
        except:
            pass
        
        report_lines.append("")
        
        # Validation Details
        report_lines.append("## Detailed Validation Results")
        report_lines.append("")
        
        for provider_id, result in sorted(self.validation_results.items()):
            candidate = self.discovered_providers[provider_id]
            
            report_lines.append(f"### `{provider_id}`")
            report_lines.append("")
            report_lines.append(f"- **Name:** {candidate.name}")
            report_lines.append(f"- **Category:** {candidate.category}")
            report_lines.append(f"- **Base URL:** {candidate.base_url}")
            report_lines.append(f"- **Status:** {result.status.value}")
            report_lines.append(f"- **HTTP Status:** {result.http_status if result.http_status else 'N/A'}")
            report_lines.append(f"- **Response Time:** {result.response_time_ms:.2f}ms" if result.response_time_ms else "- **Response Time:** N/A")
            report_lines.append(f"- **Test Endpoint:** `{result.test_endpoint}`")
            
            if result.error_message:
                report_lines.append(f"- **Error:** {result.error_message}")
            
            if result.response_sample:
                report_lines.append(f"- **Response Sample:** {result.response_sample}")
            
            report_lines.append(f"- **Source File:** {candidate.source_file}")
            report_lines.append("")
        
        # Write report
        report_content = "\n".join(report_lines)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ Report generated: {report_path}")
    
    async def run(self):
        """Run the complete APL process"""
        print("\n" + "="*80)
        print("AUTO PROVIDER LOADER (APL)")
        print("="*80)
        
        start_time = datetime.now()
        
        # Phase 1: Discovery
        self.discover_providers()
        
        # Phase 2: Validation
        await self.validate_providers()
        
        # Phase 3: Integration
        if self.stats["valid_providers"] > 0:
            self.integrate_valid_providers()
        else:
            print("\n⚠️ No valid providers found, skipping integration")
        
        # Phase 4: Report
        self.generate_report()
        
        # Final summary
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print("\n" + "="*80)
        print("APL PROCESS COMPLETE")
        print("="*80)
        print(f"\n⏱️  Total time: {elapsed:.2f}s")
        print(f"📊 Final Statistics:")
        for key, value in self.stats.items():
            print(f"   - {key.replace('_', ' ').title()}: {value}")
        
        # Final status
        if self.stats["providers_added"] > 0:
            print("\n" + "="*80)
            print("STATUS: APL PROVIDER INTEGRATION COMPLETE ✅")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("STATUS: APL PROVIDER INTEGRATION NOT READY")
            print("REASON: No valid providers were added")
            print("="*80)


async def main():
    """Main entry point"""
    # Initialize APL
    apl = AutoProviderLoader(
        scan_directories=["api-resources", "."],
        config_path="providers_config_extended.json",
        validator_timeout=10,
        validator_concurrency=5
    )
    
    # Run discovery, validation, and integration
    await apl.run()


if __name__ == "__main__":
    asyncio.run(main())
