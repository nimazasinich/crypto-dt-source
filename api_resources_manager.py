#!/usr/bin/env python3
"""
API Resources Manager
Loads and manages all API resources from JSON files
Provides unified interface for accessing 200+ crypto data sources
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class APIResourcesManager:
    """Manages all API resources from unified JSON files"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.unified_resources: Dict[str, Any] = {}
        self.hub_services: Dict[str, Any] = {}
        self._load_resources()
    
    def _load_resources(self) -> None:
        """Load all resource JSON files"""
        try:
            # Load unified resources (200+ entries)
            unified_path = self.workspace_root / "crypto_resources_unified_2025-11-11.json"
            if unified_path.exists():
                with open(unified_path, 'r', encoding='utf-8') as f:
                    self.unified_resources = json.load(f)
                logger.info(f"✅ Loaded unified resources: {self.unified_resources.get('registry', {}).get('metadata', {}).get('total_entries', 0)} entries")
            
            # Load hub services (74 services)
            hub_path = self.workspace_root / "crypto_api_hub_services.json"
            if hub_path.exists():
                with open(hub_path, 'r', encoding='utf-8') as f:
                    self.hub_services = json.load(f)
                logger.info(f"✅ Loaded hub services: {self.hub_services.get('metadata', {}).get('total_services', 0)} services")
        
        except Exception as e:
            logger.error(f"❌ Error loading resources: {e}")
    
    @lru_cache(maxsize=128)
    def get_rpc_nodes(self, chain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get RPC nodes, optionally filtered by chain"""
        nodes = self.unified_resources.get('registry', {}).get('rpc_nodes', [])
        if chain:
            return [n for n in nodes if n.get('chain', '').lower() == chain.lower()]
        return nodes
    
    @lru_cache(maxsize=128)
    def get_block_explorers(self, chain: Optional[str] = None, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get block explorers, optionally filtered by chain and role"""
        explorers = self.unified_resources.get('registry', {}).get('block_explorers', [])
        
        if chain:
            explorers = [e for e in explorers if e.get('chain', '').lower() == chain.lower()]
        
        if role:
            explorers = [e for e in explorers if e.get('role', '').lower() == role.lower()]
        
        return explorers
    
    @lru_cache(maxsize=128)
    def get_market_data_apis(self, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get market data APIs, optionally filtered by role"""
        apis = self.unified_resources.get('registry', {}).get('market_data_apis', [])
        
        if role:
            apis = [a for a in apis if role.lower() in a.get('role', '').lower()]
        
        return apis
    
    @lru_cache(maxsize=128)
    def get_news_apis(self) -> List[Dict[str, Any]]:
        """Get all news APIs"""
        return self.unified_resources.get('registry', {}).get('news_apis', [])
    
    @lru_cache(maxsize=128)
    def get_sentiment_apis(self) -> List[Dict[str, Any]]:
        """Get sentiment analysis APIs"""
        return self.unified_resources.get('registry', {}).get('sentiment_apis', [])
    
    @lru_cache(maxsize=128)
    def get_onchain_analytics_apis(self) -> List[Dict[str, Any]]:
        """Get on-chain analytics APIs"""
        return self.unified_resources.get('registry', {}).get('onchain_analytics_apis', [])
    
    @lru_cache(maxsize=128)
    def get_whale_tracking_apis(self) -> List[Dict[str, Any]]:
        """Get whale tracking APIs"""
        return self.unified_resources.get('registry', {}).get('whale_tracking_apis', [])
    
    @lru_cache(maxsize=128)
    def get_hf_resources(self, resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get Hugging Face resources (models and datasets)
        
        Args:
            resource_type: 'model' or 'dataset' to filter
        """
        resources = self.unified_resources.get('registry', {}).get('hf_resources', [])
        
        if resource_type:
            resources = [r for r in resources if r.get('type', '').lower() == resource_type.lower()]
        
        return resources
    
    @lru_cache(maxsize=128)
    def get_free_http_endpoints(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get free HTTP endpoints, optionally filtered by category"""
        endpoints = self.unified_resources.get('registry', {}).get('free_http_endpoints', [])
        
        if category:
            endpoints = [e for e in endpoints if e.get('category', '').lower() == category.lower()]
        
        return endpoints
    
    def get_service_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific service by name from hub services"""
        for category_data in self.hub_services.get('categories', {}).values():
            for service in category_data.get('services', []):
                if service.get('name', '').lower() == name.lower():
                    return service
        return None
    
    def get_services_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all services in a category"""
        return self.hub_services.get('categories', {}).get(category, {}).get('services', [])
    
    def get_all_categories(self) -> List[str]:
        """Get list of all service categories"""
        return list(self.hub_services.get('categories', {}).keys())
    
    def get_api_keys(self) -> Dict[str, str]:
        """Extract all API keys from hub services"""
        keys = {}
        for category_data in self.hub_services.get('categories', {}).values():
            for service in category_data.get('services', []):
                key = service.get('key', '').strip()
                if key:
                    keys[service['name']] = key
        return keys
    
    def get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific resource by ID from unified resources"""
        registry = self.unified_resources.get('registry', {})
        
        # Search in all resource categories
        for category in ['rpc_nodes', 'block_explorers', 'market_data_apis', 
                        'news_apis', 'sentiment_apis', 'onchain_analytics_apis',
                        'whale_tracking_apis', 'hf_resources', 'free_http_endpoints']:
            for resource in registry.get(category, []):
                if resource.get('id') == resource_id:
                    return resource
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded resources"""
        registry = self.unified_resources.get('registry', {})
        
        return {
            "unified_resources": {
                "total": registry.get('metadata', {}).get('total_entries', 0),
                "rpc_nodes": len(registry.get('rpc_nodes', [])),
                "block_explorers": len(registry.get('block_explorers', [])),
                "market_apis": len(registry.get('market_data_apis', [])),
                "news_apis": len(registry.get('news_apis', [])),
                "sentiment_apis": len(registry.get('sentiment_apis', [])),
                "onchain_apis": len(registry.get('onchain_analytics_apis', [])),
                "whale_apis": len(registry.get('whale_tracking_apis', [])),
                "hf_resources": len(registry.get('hf_resources', [])),
                "free_endpoints": len(registry.get('free_http_endpoints', []))
            },
            "hub_services": {
                "total": self.hub_services.get('metadata', {}).get('total_services', 0),
                "categories": len(self.hub_services.get('categories', {})),
                "with_keys": len(self.get_api_keys())
            }
        }
    
    def search_resources(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search resources by name or description"""
        results = []
        query_lower = query.lower()
        registry = self.unified_resources.get('registry', {})
        
        # Search in all categories
        for category in ['rpc_nodes', 'block_explorers', 'market_data_apis', 
                        'news_apis', 'sentiment_apis', 'onchain_analytics_apis',
                        'whale_tracking_apis', 'hf_resources']:
            for resource in registry.get(category, []):
                name = resource.get('name', '').lower()
                notes = resource.get('notes', '').lower() if resource.get('notes') else ''
                
                if query_lower in name or query_lower in notes:
                    results.append({
                        **resource,
                        'category': category
                    })
                    
                    if len(results) >= limit:
                        return results
        
        return results


# Global instance
_resources_manager: Optional[APIResourcesManager] = None


def get_resources_manager(workspace_root: Path = Path(".")) -> APIResourcesManager:
    """Get or create the global resources manager instance"""
    global _resources_manager
    if _resources_manager is None:
        _resources_manager = APIResourcesManager(workspace_root)
    return _resources_manager


def main():
    """Test the resources manager"""
    manager = get_resources_manager()
    stats = manager.get_stats()
    
    print("📊 API Resources Statistics:")
    print(json.dumps(stats, indent=2))
    
    print("\n🔍 Sample Resources:")
    print(f"Market APIs: {len(manager.get_market_data_apis())}")
    print(f"News APIs: {len(manager.get_news_apis())}")
    print(f"HF Models: {len(manager.get_hf_resources('model'))}")
    print(f"HF Datasets: {len(manager.get_hf_resources('dataset'))}")
    
    print("\n🔑 API Keys Available:")
    keys = manager.get_api_keys()
    for name, key in list(keys.items())[:5]:
        masked_key = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
        print(f"  {name}: {masked_key}")
    
    print(f"\n✅ Total API Keys: {len(keys)}")


if __name__ == "__main__":
    main()

