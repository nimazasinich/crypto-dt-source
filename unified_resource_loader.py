#!/usr/bin/env python3
"""
Unified Resource Loader
Loads all crypto data sources from crypto_resources_unified_2025-11-11.json
Single source of truth for all API endpoints, keys, and configurations.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class APIResource:
    """Represents a single API resource"""

    id: str
    name: str
    category: str
    base_url: str
    auth_type: str
    api_key: Optional[str] = None
    auth_param: Optional[str] = None
    auth_header: Optional[str] = None
    endpoints: Optional[Dict[str, str]] = None
    docs_url: Optional[str] = None
    notes: Optional[str] = None
    priority: int = 3

    def requires_auth(self) -> bool:
        """Check if this resource requires authentication"""
        return self.auth_type not in ["none", None]

    def get_full_url(self, endpoint: str = "") -> str:
        """Get full URL with endpoint"""
        base = self.base_url.rstrip("/")
        if endpoint:
            endpoint = endpoint.lstrip("/")
            return f"{base}/{endpoint}"
        return base

    def get_headers(self) -> Dict[str, str]:
        """Get headers for API request"""
        headers = {}
        if self.auth_type == "apiKeyHeader" and self.api_key and self.auth_header:
            headers[self.auth_header] = self.api_key
        elif self.auth_type == "apiKeyHeaderOptional" and self.api_key and self.auth_header:
            headers[self.auth_header] = f"Bearer {self.api_key}"
        return headers

    def get_query_params(self) -> Dict[str, str]:
        """Get query parameters for API request"""
        params = {}
        if (
            self.auth_type in ["apiKeyQuery", "apiKeyQueryOptional"]
            and self.api_key
            and self.auth_param
        ):
            params[self.auth_param] = self.api_key
        return params


class UnifiedResourceLoader:
    """
    Unified Resource Loader - Single source of truth for all crypto data sources
    Loads from crypto_resources_unified_2025-11-11.json
    """

    def __init__(self, config_file: str = "crypto_resources_unified_2025-11-11.json"):
        self.config_file = Path(config_file)
        self.resources: Dict[str, APIResource] = {}
        self.categories: Dict[str, List[str]] = {}
        self.registry_data: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.loaded = False

    def load(self) -> bool:
        """Load and parse the unified resource configuration"""
        try:
            if not self.config_file.exists():
                print(f"❌ Config file not found: {self.config_file}")
                return False

            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract registry
            if "registry" not in data:
                print("❌ Invalid config format: missing 'registry' key")
                return False

            self.registry_data = data["registry"]

            # Extract metadata
            self.metadata = self.registry_data.get("metadata", {})

            # Process each section
            self._process_rpc_nodes()
            self._process_block_explorers()
            self._process_market_data_apis()
            self._process_news_apis()
            self._process_sentiment_apis()
            self._process_onchain_analytics_apis()
            self._process_whale_tracking_apis()
            self._process_community_sentiment_apis()
            self._process_hf_resources()
            self._process_free_http_endpoints()
            self._process_cors_proxies()

            # Build category index
            self._build_category_index()

            self.loaded = True

            print(
                f"✅ Loaded {len(self.resources)} resources from {len(self.categories)} categories"
            )

            return True

        except Exception as e:
            print(f"❌ Error loading config: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _parse_auth(self, auth_data: Dict[str, Any]) -> tuple:
        """Parse authentication data"""
        auth_type = auth_data.get("type", "none")
        api_key = auth_data.get("key")
        auth_param = auth_data.get("param_name")
        auth_header = auth_data.get("header_name")

        # Try to get from environment if not embedded
        if not api_key and auth_param:
            env_var = auth_param.upper()
            api_key = os.getenv(env_var)

        return auth_type, api_key, auth_param, auth_header

    def _process_rpc_nodes(self):
        """Process RPC nodes section"""
        rpc_nodes = self.registry_data.get("rpc_nodes", [])
        for item in rpc_nodes:
            auth_type, api_key, auth_param, auth_header = self._parse_auth(item.get("auth", {}))

            resource = APIResource(
                id=item["id"],
                name=item["name"],
                category="rpc_nodes",
                base_url=item["base_url"],
                auth_type=auth_type,
                api_key=api_key,
                auth_param=auth_param,
                auth_header=auth_header,
                docs_url=item.get("docs_url"),
                notes=item.get("notes"),
                priority=1,
            )
            self.resources[resource.id] = resource

    def _process_block_explorers(self):
        """Process block explorers section"""
        explorers = self.registry_data.get("block_explorers", [])
        for item in explorers:
            auth_type, api_key, auth_param, auth_header = self._parse_auth(item.get("auth", {}))

            # Determine priority based on role
            priority = 1 if item.get("role") == "primary" else 2

            resource = APIResource(
                id=item["id"],
                name=item["name"],
                category="block_explorers",
                base_url=item["base_url"],
                auth_type=auth_type,
                api_key=api_key,
                auth_param=auth_param,
                auth_header=auth_header,
                endpoints=item.get("endpoints", {}),
                docs_url=item.get("docs_url"),
                notes=item.get("notes"),
                priority=priority,
            )
            self.resources[resource.id] = resource

    def _process_market_data_apis(self):
        """Process market data APIs section"""
        market_apis = self.registry_data.get("market_data_apis", [])
        for item in market_apis:
            auth_type, api_key, auth_param, auth_header = self._parse_auth(item.get("auth", {}))

            # Determine priority
            role = item.get("role", "")
            if "primary" in role or "free" in role:
                priority = 1
            elif "fallback" in role:
                priority = 2
            else:
                priority = 3

            resource = APIResource(
                id=item["id"],
                name=item["name"],
                category="market_data",
                base_url=item["base_url"],
                auth_type=auth_type,
                api_key=api_key,
                auth_param=auth_param,
                auth_header=auth_header,
                endpoints=item.get("endpoints", {}),
                docs_url=item.get("docs_url"),
                notes=item.get("notes"),
                priority=priority,
            )
            self.resources[resource.id] = resource

    def _process_news_apis(self):
        """Process news APIs section"""
        news_apis = self.registry_data.get("news_apis", [])
        for item in news_apis:
            auth_type, api_key, auth_param, auth_header = self._parse_auth(item.get("auth", {}))

            role = item.get("role", "")
            priority = 1 if "primary" in role else 2

            resource = APIResource(
                id=item["id"],
                name=item["name"],
                category="news",
                base_url=item["base_url"],
                auth_type=auth_type,
                api_key=api_key,
                auth_param=auth_param,
                auth_header=auth_header,
                endpoints=item.get("endpoints", {}),
                docs_url=item.get("docs_url"),
                notes=item.get("notes"),
                priority=priority,
            )
            self.resources[resource.id] = resource

    def _process_sentiment_apis(self):
        """Process sentiment APIs section"""
        sentiment_apis = self.registry_data.get("sentiment_apis", [])
        for item in sentiment_apis:
            auth_type, api_key, auth_param, auth_header = self._parse_auth(item.get("auth", {}))

            role = item.get("role", "")
            priority = 1 if "primary" in role else 2

            resource = APIResource(
                id=item["id"],
                name=item["name"],
                category="sentiment",
                base_url=item["base_url"],
                auth_type=auth_type,
                api_key=api_key,
                auth_param=auth_param,
                auth_header=auth_header,
                endpoints=item.get("endpoints", {}),
                docs_url=item.get("docs_url"),
                notes=item.get("notes"),
                priority=priority,
            )
            self.resources[resource.id] = resource

    def _process_onchain_analytics_apis(self):
        """Process on-chain analytics APIs section"""
        onchain_apis = self.registry_data.get("onchain_analytics_apis", [])
        for item in onchain_apis:
            auth_type, api_key, auth_param, auth_header = self._parse_auth(item.get("auth", {}))

            resource = APIResource(
                id=item["id"],
                name=item["name"],
                category="onchain_analytics",
                base_url=item["base_url"],
                auth_type=auth_type,
                api_key=api_key,
                auth_param=auth_param,
                auth_header=auth_header,
                endpoints=item.get("endpoints", {}),
                docs_url=item.get("docs_url"),
                notes=item.get("notes"),
                priority=2,
            )
            self.resources[resource.id] = resource

    def _process_whale_tracking_apis(self):
        """Process whale tracking APIs section"""
        whale_apis = self.registry_data.get("whale_tracking_apis", [])
        for item in whale_apis:
            auth_type, api_key, auth_param, auth_header = self._parse_auth(item.get("auth", {}))

            role = item.get("role", "")
            priority = 1 if "primary" in role else 2

            resource = APIResource(
                id=item["id"],
                name=item["name"],
                category="whale_tracking",
                base_url=item["base_url"],
                auth_type=auth_type,
                api_key=api_key,
                auth_param=auth_param,
                auth_header=auth_header,
                endpoints=item.get("endpoints", {}),
                docs_url=item.get("docs_url"),
                notes=item.get("notes"),
                priority=priority,
            )
            self.resources[resource.id] = resource

    def _process_community_sentiment_apis(self):
        """Process community sentiment APIs section"""
        community_apis = self.registry_data.get("community_sentiment_apis", [])
        for item in community_apis:
            auth_type, api_key, auth_param, auth_header = self._parse_auth(item.get("auth", {}))

            resource = APIResource(
                id=item["id"],
                name=item["name"],
                category="community_sentiment",
                base_url=item["base_url"],
                auth_type=auth_type,
                api_key=api_key,
                auth_param=auth_param,
                auth_header=auth_header,
                endpoints=item.get("endpoints", {}),
                docs_url=item.get("docs_url"),
                notes=item.get("notes"),
                priority=2,
            )
            self.resources[resource.id] = resource

    def _process_hf_resources(self):
        """Process Hugging Face resources section"""
        hf_resources = self.registry_data.get("hf_resources", [])
        for item in hf_resources:
            auth_type, api_key, auth_param, auth_header = self._parse_auth(item.get("auth", {}))

            resource_type = item.get("type", "model")

            resource = APIResource(
                id=item["id"],
                name=item["name"],
                category=f"hf_{resource_type}",
                base_url=item["base_url"],
                auth_type=auth_type,
                api_key=api_key,
                auth_param=auth_param,
                auth_header=auth_header,
                endpoints=item.get("endpoints", {}),
                docs_url=item.get("docs_url"),
                notes=item.get("notes"),
                priority=1,
            )
            self.resources[resource.id] = resource

    def _process_free_http_endpoints(self):
        """Process free HTTP endpoints section"""
        free_endpoints = self.registry_data.get("free_http_endpoints", [])
        for item in free_endpoints:
            auth_type, api_key, auth_param, auth_header = self._parse_auth(item.get("auth", {}))

            category = item.get("category", "free_endpoint")

            resource = APIResource(
                id=item["id"],
                name=item["name"],
                category=category,
                base_url=item["base_url"],
                auth_type=auth_type,
                api_key=api_key,
                auth_param=auth_param,
                auth_header=auth_header,
                docs_url=item.get("docs_url"),
                notes=item.get("notes"),
                priority=1,
            )
            self.resources[resource.id] = resource

    def _process_cors_proxies(self):
        """Process CORS proxies section"""
        cors_proxies = self.registry_data.get("cors_proxies", [])
        for item in cors_proxies:
            resource = APIResource(
                id=item["id"],
                name=item["name"],
                category="cors_proxy",
                base_url=item["base_url"],
                auth_type="none",
                docs_url=item.get("docs_url"),
                notes=item.get("notes"),
                priority=2,
            )
            self.resources[resource.id] = resource

    def _build_category_index(self):
        """Build index of resources by category"""
        self.categories = {}
        for resource_id, resource in self.resources.items():
            if resource.category not in self.categories:
                self.categories[resource.category] = []
            self.categories[resource.category].append(resource_id)

    # Query methods

    def get_resource(self, resource_id: str) -> Optional[APIResource]:
        """Get a specific resource by ID"""
        return self.resources.get(resource_id)

    def get_resources_by_category(self, category: str) -> List[APIResource]:
        """Get all resources in a category"""
        resource_ids = self.categories.get(category, [])
        return [self.resources[rid] for rid in resource_ids]

    def get_available_categories(self) -> List[str]:
        """Get list of all available categories"""
        return list(self.categories.keys())

    def get_primary_resources(self, category: str) -> List[APIResource]:
        """Get primary (priority 1) resources in a category"""
        resources = self.get_resources_by_category(category)
        return [r for r in resources if r.priority == 1]

    def get_free_resources(self, category: str) -> List[APIResource]:
        """Get resources that don't require authentication"""
        resources = self.get_resources_by_category(category)
        return [r for r in resources if not r.requires_auth()]

    def search_resources(self, query: str) -> List[APIResource]:
        """Search resources by name or ID"""
        query = query.lower()
        results = []
        for resource in self.resources.values():
            if query in resource.id.lower() or query in resource.name.lower():
                results.append(resource)
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded resources"""
        stats = {
            "total_resources": len(self.resources),
            "total_categories": len(self.categories),
            "categories": {},
            "auth_required": 0,
            "free_resources": 0,
        }

        for category, resource_ids in self.categories.items():
            stats["categories"][category] = len(resource_ids)

        for resource in self.resources.values():
            if resource.requires_auth():
                stats["auth_required"] += 1
            else:
                stats["free_resources"] += 1

        return stats

    def export_summary(self, output_file: str = "resource_summary.json"):
        """Export a summary of all loaded resources"""
        summary = {
            "generated_at": datetime.now().isoformat(),
            "metadata": self.metadata,
            "stats": self.get_stats(),
            "categories": list(self.categories.keys()),
            "resources": {
                resource_id: {
                    "name": resource.name,
                    "category": resource.category,
                    "base_url": resource.base_url,
                    "requires_auth": resource.requires_auth(),
                    "priority": resource.priority,
                }
                for resource_id, resource in self.resources.items()
            },
        }

        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"✅ Exported summary to {output_file}")


# Global instance
_loader = None


def get_loader() -> UnifiedResourceLoader:
    """Get global loader instance (singleton)"""
    global _loader
    if _loader is None:
        _loader = UnifiedResourceLoader()
        _loader.load()
    return _loader


if __name__ == "__main__":
    # Test the loader
    loader = UnifiedResourceLoader()
    if loader.load():
        print("\n📊 Statistics:")
        stats = loader.get_stats()
        print(f"  Total Resources: {stats['total_resources']}")
        print(f"  Total Categories: {stats['total_categories']}")
        print(f"  Free Resources: {stats['free_resources']}")
        print(f"  Auth Required: {stats['auth_required']}")

        print("\n📁 Categories:")
        for cat, count in stats["categories"].items():
            print(f"  - {cat}: {count} resources")

        # Export summary
        loader.export_summary()
