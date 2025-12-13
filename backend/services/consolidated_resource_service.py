"""
Consolidated Resource Service
Integrates all crypto resources from consolidated database into the main project
"""

import sys
import os

# Add cursor-instructions to path
sys.path.append('/workspace/cursor-instructions')

from resource_manager import ResourceManager, CryptoResource
from typing import List, Dict, Optional
import json
import asyncio


class ConsolidatedResourceService:
    """Service for accessing consolidated crypto resources"""
    
    def __init__(self):
        self.manager = ResourceManager()
        self.cache = {}
        
    def get_all_market_data_sources(self, free_only: bool = True) -> List[Dict]:
        """Get all market data API sources"""
        with self.manager:
            resources = self.manager.get_resources_by_category('market_data_apis', free_only)
            return [r.to_dict() for r in resources]
    
    def get_all_rpc_nodes(self, free_only: bool = True) -> List[Dict]:
        """Get all RPC node providers"""
        with self.manager:
            resources = self.manager.get_resources_by_category('rpc_nodes', free_only)
            return [r.to_dict() for r in resources]
    
    def get_all_block_explorers(self, free_only: bool = True) -> List[Dict]:
        """Get all block explorer APIs"""
        with self.manager:
            # Get both categories
            explorers1 = self.manager.get_resources_by_category('block_explorers', free_only)
            explorers2 = self.manager.get_resources_by_category('Block Explorer', free_only)
            
            all_explorers = explorers1 + explorers2
            return [r.to_dict() for r in all_explorers]
    
    def get_all_news_sources(self, free_only: bool = True) -> List[Dict]:
        """Get all news API sources"""
        with self.manager:
            resources = self.manager.get_resources_by_category('news_apis', free_only)
            return [r.to_dict() for r in resources]
    
    def get_all_sentiment_sources(self, free_only: bool = True) -> List[Dict]:
        """Get all sentiment analysis sources"""
        with self.manager:
            resources = self.manager.get_resources_by_category('sentiment_apis', free_only)
            return [r.to_dict() for r in resources]
    
    def get_all_whale_tracking_sources(self, free_only: bool = True) -> List[Dict]:
        """Get all whale tracking sources"""
        with self.manager:
            resources = self.manager.get_resources_by_category('whale_tracking_apis', free_only)
            return [r.to_dict() for r in resources]
    
    def get_all_websocket_sources(self) -> List[Dict]:
        """Get all WebSocket-enabled sources"""
        with self.manager:
            resources = self.manager.get_websocket_resources()
            return [r.to_dict() for r in resources]
    
    def get_resource_pool(self, category: str, count: int = 5) -> List[Dict]:
        """Get a pool of resources for load balancing"""
        with self.manager:
            resources = self.manager.get_resources_by_category(category, free_only=True)
            
            # Return up to 'count' resources
            return [r.to_dict() for r in resources[:count]]
    
    def search_resources(self, query: str) -> List[Dict]:
        """Search resources"""
        with self.manager:
            resources = self.manager.search_resources(query)
            return [r.to_dict() for r in resources]
    
    def get_statistics(self) -> Dict:
        """Get resource statistics"""
        with self.manager:
            return self.manager.get_statistics()
    
    def export_for_frontend(self) -> Dict:
        """Export resource configuration for frontend"""
        return {
            'market_data': {
                'primary': self.get_resource_pool('market_data_apis', 3),
                'total_available': len(self.get_all_market_data_sources())
            },
            'block_explorers': {
                'ethereum': [r for r in self.get_all_block_explorers() if 'eth' in r['name'].lower()],
                'bsc': [r for r in self.get_all_block_explorers() if 'bsc' in r['name'].lower()],
                'tron': [r for r in self.get_all_block_explorers() if 'tron' in r['name'].lower()],
                'total_available': len(self.get_all_block_explorers())
            },
            'news': {
                'sources': self.get_resource_pool('news_apis', 5),
                'total_available': len(self.get_all_news_sources())
            },
            'sentiment': {
                'sources': self.get_resource_pool('sentiment_apis', 3),
                'total_available': len(self.get_all_sentiment_sources())
            },
            'websockets': {
                'available': self.get_all_websocket_sources(),
                'total_available': len(self.get_all_websocket_sources())
            },
            'statistics': self.get_statistics()
        }


# Singleton instance
_service_instance = None

def get_resource_service() -> ConsolidatedResourceService:
    """Get consolidated resource service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ConsolidatedResourceService()
    return _service_instance


# FastAPI integration example
def create_resource_router():
    """Create FastAPI router for resources"""
    from fastapi import APIRouter
    
    router = APIRouter(prefix="/api/consolidated-resources", tags=["resources"])
    service = get_resource_service()
    
    @router.get("/market-data")
    async def get_market_data_sources():
        """Get all market data sources"""
        return service.get_all_market_data_sources()
    
    @router.get("/block-explorers")
    async def get_block_explorers():
        """Get all block explorer sources"""
        return service.get_all_block_explorers()
    
    @router.get("/news")
    async def get_news_sources():
        """Get all news sources"""
        return service.get_all_news_sources()
    
    @router.get("/sentiment")
    async def get_sentiment_sources():
        """Get all sentiment sources"""
        return service.get_all_sentiment_sources()
    
    @router.get("/whale-tracking")
    async def get_whale_tracking_sources():
        """Get all whale tracking sources"""
        return service.get_all_whale_tracking_sources()
    
    @router.get("/websockets")
    async def get_websocket_sources():
        """Get all WebSocket sources"""
        return service.get_all_websocket_sources()
    
    @router.get("/search")
    async def search_resources(q: str):
        """Search resources"""
        return service.search_resources(q)
    
    @router.get("/statistics")
    async def get_statistics():
        """Get resource statistics"""
        return service.get_statistics()
    
    @router.get("/export")
    async def export_resources():
        """Export all resources for frontend"""
        return service.export_for_frontend()
    
    return router


# Example usage
if __name__ == "__main__":
    service = get_resource_service()
    
    print("\n" + "="*80)
    print("CONSOLIDATED RESOURCE SERVICE - TEST")
    print("="*80 + "\n")
    
    # Get statistics
    stats = service.get_statistics()
    print(f"📊 Statistics:")
    print(f"   Total Resources: {stats['total_resources']}")
    print(f"   Free Resources: {stats['free_resources']}")
    print(f"   WebSocket Enabled: {stats['websocket_enabled']}")
    
    # Get market data sources
    market_data = service.get_all_market_data_sources()
    print(f"\n💰 Market Data Sources: {len(market_data)}")
    for source in market_data[:3]:
        print(f"   - {source['name']}: {source['base_url']}")
    
    # Get block explorers
    explorers = service.get_all_block_explorers()
    print(f"\n🔍 Block Explorers: {len(explorers)}")
    for explorer in explorers[:3]:
        print(f"   - {explorer['name']}: {explorer['base_url']}")
    
    # Get WebSocket sources
    websockets = service.get_all_websocket_sources()
    print(f"\n🔌 WebSocket Sources: {len(websockets)}")
    for ws in websockets[:3]:
        print(f"   - {ws['name']}: {ws['base_url']}")
    
    # Search example
    bitcoin_resources = service.search_resources('bitcoin')
    print(f"\n🔎 Bitcoin-related Resources: {len(bitcoin_resources)}")
    
    # Export for frontend
    frontend_config = service.export_for_frontend()
    print(f"\n📤 Frontend Export:")
    print(f"   Market Data: {frontend_config['market_data']['total_available']} sources")
    print(f"   Block Explorers: {frontend_config['block_explorers']['total_available']} sources")
    print(f"   News: {frontend_config['news']['total_available']} sources")
    print(f"   WebSockets: {frontend_config['websockets']['total_available']} sources")
    
    print("\n" + "="*80 + "\n")
