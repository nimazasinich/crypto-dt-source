"""
Crypto Resources Manager
Provides easy access to consolidated crypto resources with WebSocket support
"""

import json
import sqlite3
import random
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ResourceCategory(Enum):
    """Resource categories"""
    RPC_NODES = 'rpc_nodes'
    BLOCK_EXPLORERS = 'block_explorers'
    MARKET_DATA = 'market_data_apis'
    NEWS = 'news_apis'
    SENTIMENT = 'sentiment_apis'
    WHALE_TRACKING = 'whale_tracking_apis'
    ONCHAIN_ANALYTICS = 'onchain_analytics_apis'
    WEBSOCKET = 'websocket'


@dataclass
class CryptoResource:
    """Crypto resource data class"""
    id: str
    name: str
    category: str
    base_url: str
    auth_type: str = 'none'
    api_key: str = ''
    is_free: bool = True
    websocket_support: bool = False
    rate_limit: str = ''
    docs_url: str = ''
    endpoints: str = ''
    notes: str = ''
    data_types: List[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'base_url': self.base_url,
            'auth_type': self.auth_type,
            'api_key': self.api_key,
            'is_free': self.is_free,
            'websocket_support': self.websocket_support,
            'rate_limit': self.rate_limit,
            'docs_url': self.docs_url,
            'endpoints': self.endpoints,
            'notes': self.notes,
            'data_types': self.data_types or []
        }


class ResourceManager:
    """Manages crypto resources from consolidated database"""
    
    def __init__(self, db_path: str = "/workspace/cursor-instructions/consolidated_crypto_resources.db"):
        self.db_path = db_path
        self.conn = None
        self.cache = {}
        
    def connect(self):
        """Connect to database"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def get_resource_by_id(self, resource_id: str) -> Optional[CryptoResource]:
        """Get resource by ID"""
        self.connect()
        cursor = self.conn.cursor()
        
        result = cursor.execute(
            'SELECT * FROM resources WHERE id = ?',
            (resource_id,)
        ).fetchone()
        
        if not result:
            return None
        
        # Get data types
        data_types = cursor.execute(
            'SELECT data_type FROM data_types WHERE resource_id = ?',
            (resource_id,)
        ).fetchall()
        
        return CryptoResource(
            id=result['id'],
            name=result['name'],
            category=result['category'],
            base_url=result['base_url'],
            auth_type=result['auth_type'],
            api_key=result['api_key'],
            is_free=bool(result['is_free']),
            websocket_support=bool(result['websocket_support']),
            rate_limit=result['rate_limit'],
            docs_url=result['docs_url'],
            endpoints=result['endpoints'],
            notes=result['notes'],
            data_types=[dt['data_type'] for dt in data_types]
        )
    
    def get_resources_by_category(self, category: str, free_only: bool = True) -> List[CryptoResource]:
        """Get resources by category"""
        self.connect()
        cursor = self.conn.cursor()
        
        query = 'SELECT * FROM resources WHERE category = ?'
        params = [category]
        
        if free_only:
            query += ' AND is_free = 1'
        
        results = cursor.execute(query, params).fetchall()
        
        resources = []
        for result in results:
            # Get data types
            data_types = cursor.execute(
                'SELECT data_type FROM data_types WHERE resource_id = ?',
                (result['id'],)
            ).fetchall()
            
            resources.append(CryptoResource(
                id=result['id'],
                name=result['name'],
                category=result['category'],
                base_url=result['base_url'],
                auth_type=result['auth_type'],
                api_key=result['api_key'],
                is_free=bool(result['is_free']),
                websocket_support=bool(result['websocket_support']),
                rate_limit=result['rate_limit'],
                docs_url=result['docs_url'],
                endpoints=result['endpoints'],
                notes=result['notes'],
                data_types=[dt['data_type'] for dt in data_types]
            ))
        
        return resources
    
    def get_websocket_resources(self) -> List[CryptoResource]:
        """Get all WebSocket-enabled resources"""
        self.connect()
        cursor = self.conn.cursor()
        
        results = cursor.execute(
            'SELECT * FROM resources WHERE websocket_support = 1'
        ).fetchall()
        
        resources = []
        for result in results:
            resources.append(CryptoResource(
                id=result['id'],
                name=result['name'],
                category=result['category'],
                base_url=result['base_url'],
                auth_type=result['auth_type'],
                api_key=result['api_key'],
                is_free=bool(result['is_free']),
                websocket_support=True,
                rate_limit=result['rate_limit'],
                docs_url=result['docs_url'],
                endpoints=result['endpoints'],
                notes=result['notes']
            ))
        
        return resources
    
    def get_free_resources(self, limit: Optional[int] = None) -> List[CryptoResource]:
        """Get all free resources"""
        self.connect()
        cursor = self.conn.cursor()
        
        query = 'SELECT * FROM resources WHERE is_free = 1'
        if limit:
            query += f' LIMIT {limit}'
        
        results = cursor.execute(query).fetchall()
        
        resources = []
        for result in results:
            resources.append(CryptoResource(
                id=result['id'],
                name=result['name'],
                category=result['category'],
                base_url=result['base_url'],
                auth_type=result['auth_type'],
                api_key=result['api_key'],
                is_free=True,
                websocket_support=bool(result['websocket_support']),
                rate_limit=result['rate_limit'],
                docs_url=result['docs_url'],
                endpoints=result['endpoints'],
                notes=result['notes']
            ))
        
        return resources
    
    def get_random_resource(self, category: str = None, free_only: bool = True) -> Optional[CryptoResource]:
        """Get random resource for load balancing"""
        if category:
            resources = self.get_resources_by_category(category, free_only)
        else:
            resources = self.get_free_resources() if free_only else self.get_all_resources()
        
        if not resources:
            return None
        
        return random.choice(resources)
    
    def get_all_resources(self) -> List[CryptoResource]:
        """Get all resources"""
        self.connect()
        cursor = self.conn.cursor()
        
        results = cursor.execute('SELECT * FROM resources').fetchall()
        
        resources = []
        for result in results:
            resources.append(CryptoResource(
                id=result['id'],
                name=result['name'],
                category=result['category'],
                base_url=result['base_url'],
                auth_type=result['auth_type'],
                api_key=result['api_key'],
                is_free=bool(result['is_free']),
                websocket_support=bool(result['websocket_support']),
                rate_limit=result['rate_limit'],
                docs_url=result['docs_url'],
                endpoints=result['endpoints'],
                notes=result['notes']
            ))
        
        return resources
    
    def search_resources(self, query: str) -> List[CryptoResource]:
        """Search resources by name or category"""
        self.connect()
        cursor = self.conn.cursor()
        
        results = cursor.execute(
            '''SELECT * FROM resources 
               WHERE name LIKE ? OR category LIKE ? OR notes LIKE ?''',
            (f'%{query}%', f'%{query}%', f'%{query}%')
        ).fetchall()
        
        resources = []
        for result in results:
            resources.append(CryptoResource(
                id=result['id'],
                name=result['name'],
                category=result['category'],
                base_url=result['base_url'],
                auth_type=result['auth_type'],
                api_key=result['api_key'],
                is_free=bool(result['is_free']),
                websocket_support=bool(result['websocket_support']),
                rate_limit=result['rate_limit'],
                docs_url=result['docs_url'],
                endpoints=result['endpoints'],
                notes=result['notes']
            ))
        
        return resources
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get resource statistics"""
        self.connect()
        cursor = self.conn.cursor()
        
        total = cursor.execute('SELECT COUNT(*) as count FROM resources').fetchone()['count']
        free = cursor.execute('SELECT COUNT(*) as count FROM resources WHERE is_free = 1').fetchone()['count']
        websocket = cursor.execute('SELECT COUNT(*) as count FROM resources WHERE websocket_support = 1').fetchone()['count']
        
        categories = cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM resources 
            GROUP BY category 
            ORDER BY count DESC
        ''').fetchall()
        
        return {
            'total_resources': total,
            'free_resources': free,
            'paid_resources': total - free,
            'websocket_enabled': websocket,
            'categories': [{'category': cat['category'], 'count': cat['count']} for cat in categories]
        }


def export_to_project():
    """Export resources to project database"""
    manager = ResourceManager()
    
    with manager:
        resources = manager.get_all_resources()
        
        # Export to JSON for easy access
        output = {
            'total': len(resources),
            'resources': [r.to_dict() for r in resources]
        }
        
        with open('/workspace/data/crypto_resources.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✅ Exported {len(resources)} resources to /workspace/data/crypto_resources.json")


# Example usage
if __name__ == "__main__":
    manager = ResourceManager()
    
    with manager:
        # Get statistics
        stats = manager.get_statistics()
        print("\n📊 Resource Statistics:")
        print(f"   Total: {stats['total_resources']}")
        print(f"   Free: {stats['free_resources']}")
        print(f"   WebSocket: {stats['websocket_enabled']}")
        
        print("\n📁 Categories:")
        for cat in stats['categories'][:10]:
            print(f"   {cat['category']}: {cat['count']}")
        
        # Get WebSocket resources
        ws_resources = manager.get_websocket_resources()
        print(f"\n🔌 WebSocket Resources: {len(ws_resources)}")
        for ws in ws_resources[:5]:
            print(f"   - {ws.name}: {ws.base_url}")
        
        # Get market data resources
        market = manager.get_resources_by_category('market_data_apis')
        print(f"\n💰 Market Data APIs: {len(market)}")
        for m in market[:5]:
            print(f"   - {m.name}: {m.base_url} (Free: {m.is_free})")
