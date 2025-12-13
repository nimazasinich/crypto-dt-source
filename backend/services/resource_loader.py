"""
CRITICAL: Load ALL 305 resources from consolidated_crypto_resources.json
NO LIMITATIONS! USE EVERYTHING AVAILABLE!
"""

import json
import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ResourceLoader:
    """Load and manage ALL 305+ crypto resources - NO FILTERING!"""
    
    def __init__(self):
        self.resources = []
        self.resources_by_category = {}
        self.total_loaded = 0
        self.load_all_resources()
    
    def load_all_resources(self):
        """Load ALL 305 resources from JSON file - NO FILTERS!"""
        json_path = "cursor-instructions/consolidated_crypto_resources.json"
        
        if not os.path.exists(json_path):
            logger.error(f"❌ CRITICAL: {json_path} not found!")
            return
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load all resources WITHOUT ANY FILTERING
            if isinstance(data, list):
                self.resources = data
            elif isinstance(data, dict) and 'resources' in data:
                self.resources = data['resources']
            else:
                logger.error(f"⚠️ Unexpected JSON structure in {json_path}")
                return
            
            self.total_loaded = len(self.resources)
            
            # Categorize resources
            for resource in self.resources:
                category = resource.get('category', 'unknown')
                if category not in self.resources_by_category:
                    self.resources_by_category[category] = []
                self.resources_by_category[category].append(resource)
            
            logger.info("=" * 80)
            logger.info(f"✅ LOADED {self.total_loaded} RESOURCES FROM JSON")
            logger.info("=" * 80)
            logger.info(f"📊 Categories found: {len(self.resources_by_category)}")
            
            # Print detailed breakdown
            for category, items in sorted(self.resources_by_category.items(), key=lambda x: len(x[1]), reverse=True):
                logger.info(f"   • {category}: {len(items)} resources")
            
            # Verify we have all expected resources
            if self.total_loaded < 305:
                logger.warning("=" * 80)
                logger.warning(f"⚠️  WARNING: Expected 305 resources, loaded {self.total_loaded}")
                logger.warning(f"   Missing {305 - self.total_loaded} resources!")
                logger.warning("=" * 80)
            else:
                logger.info("=" * 80)
                logger.info(f"✅ SUCCESS: All {self.total_loaded} resources loaded!")
                logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR loading resources: {e}")
            import traceback
            traceback.print_exc()
    
    def get_all_resources(self) -> List[Dict[str, Any]]:
        """Get ALL resources - NO FILTERING, NO LIMITS!"""
        return self.resources
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all resources in a specific category"""
        return self.resources_by_category.get(category, [])
    
    def get_market_data_apis(self) -> List[Dict[str, Any]]:
        """Get ALL Market Data APIs (should be 38+)"""
        # Check multiple category names
        results = []
        for cat in ['Market Data', 'Market Data APIs', 'market_data_apis', 'market_data']:
            results.extend(self.get_by_category(cat))
        return results
    
    def get_news_apis(self) -> List[Dict[str, Any]]:
        """Get ALL News APIs (should be 19+)"""
        results = []
        for cat in ['News', 'News APIs', 'news_apis', 'news']:
            results.extend(self.get_by_category(cat))
        return results
    
    def get_sentiment_apis(self) -> List[Dict[str, Any]]:
        """Get ALL Sentiment APIs (should be 15+)"""
        results = []
        for cat in ['Sentiment', 'Sentiment APIs', 'sentiment_apis', 'sentiment']:
            results.extend(self.get_by_category(cat))
        return results
    
    def get_block_explorers(self) -> List[Dict[str, Any]]:
        """Get ALL Block Explorers (should be 40+)"""
        results = []
        for cat in ['Block Explorer', 'Block Explorers', 'block_explorers']:
            results.extend(self.get_by_category(cat))
        return results
    
    def get_rpc_nodes(self) -> List[Dict[str, Any]]:
        """Get ALL RPC Nodes (should be 24+)"""
        results = []
        for cat in ['RPC Nodes', 'rpc_nodes', 'rpc']:
            results.extend(self.get_by_category(cat))
        return results
    
    def get_whale_tracking(self) -> List[Dict[str, Any]]:
        """Get ALL Whale Tracking APIs (should be 11+)"""
        results = []
        for cat in ['Whale-Tracking', 'Whale Tracking', 'whale_tracking_apis', 'whale_tracking']:
            results.extend(self.get_by_category(cat))
        return results
    
    def get_onchain_analytics(self) -> List[Dict[str, Any]]:
        """Get ALL On-Chain Analytics (should be 15+)"""
        results = []
        for cat in ['On-Chain', 'On-chain Analytics', 'onchain_analytics_apis', 'onchain']:
            results.extend(self.get_by_category(cat))
        return results
    
    def get_local_backend(self) -> List[Dict[str, Any]]:
        """Get ALL Local Backend Routes (should be 106+)"""
        return self.get_by_category('local_backend_routes')
    
    def get_free_only(self) -> List[Dict[str, Any]]:
        """Get only free resources (no API key required)"""
        return [r for r in self.resources if r.get('is_free', True)]
    
    def get_with_api_keys(self) -> List[Dict[str, Any]]:
        """Get resources that have API keys configured"""
        return [r for r in self.resources if r.get('api_key') or r.get('key')]
    
    def get_websocket_enabled(self) -> List[Dict[str, Any]]:
        """Get resources with WebSocket support"""
        return [r for r in self.resources if r.get('websocket_support', False)]
    
    def get_resource_count(self) -> int:
        """Get total resource count - should return 305!"""
        return self.total_loaded
    
    def verify_all_loaded(self) -> bool:
        """Verify that ALL 305 resources are loaded"""
        expected = 305
        actual = self.total_loaded
        
        if actual < expected:
            logger.warning("=" * 80)
            logger.warning(f"⚠️  VERIFICATION FAILED:")
            logger.warning(f"   Expected: {expected} resources")
            logger.warning(f"   Loaded: {actual} resources")
            logger.warning(f"   Missing: {expected - actual} resources")
            logger.warning("=" * 80)
            return False
        
        logger.info("=" * 80)
        logger.info(f"✅ VERIFICATION PASSED: All {actual} resources loaded!")
        logger.info("=" * 80)
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics about loaded resources"""
        stats = {
            'total_resources': self.total_loaded,
            'expected_resources': 305,
            'verification_passed': self.total_loaded >= 305,
            'categories': len(self.resources_by_category),
            'category_breakdown': {},
            'free_resources': len(self.get_free_only()),
            'paid_resources': len([r for r in self.resources if not r.get('is_free', True)]),
            'websocket_enabled': len(self.get_websocket_enabled()),
            'with_api_keys': len(self.get_with_api_keys()),
        }
        
        for category, items in self.resources_by_category.items():
            stats['category_breakdown'][category] = len(items)
        
        return stats


# Global instance
_resource_loader = None


def get_resource_loader() -> ResourceLoader:
    """Get global resource loader instance"""
    global _resource_loader
    if _resource_loader is None:
        _resource_loader = ResourceLoader()
        _resource_loader.verify_all_loaded()  # Verify on first load
    return _resource_loader


def print_resource_stats():
    """Print detailed resource statistics"""
    loader = get_resource_loader()
    stats = loader.get_statistics()
    
    print("=" * 80)
    print("📊 RESOURCE STATISTICS")
    print("=" * 80)
    print(f"Total Resources: {stats['total_resources']}/{stats['expected_resources']}")
    print(f"Verification: {'✅ PASSED' if stats['verification_passed'] else '❌ FAILED'}")
    print(f"Categories: {stats['categories']}")
    print(f"Free Resources: {stats['free_resources']}")
    print(f"Paid/Limited: {stats['paid_resources']}")
    print(f"WebSocket Enabled: {stats['websocket_enabled']}")
    print(f"With API Keys: {stats['with_api_keys']}")
    print()
    print("Category Breakdown:")
    for category, count in sorted(stats['category_breakdown'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {category}: {count}")
    print("=" * 80)


if __name__ == "__main__":
    # Test the loader
    print_resource_stats()
