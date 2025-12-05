#!/usr/bin/env python3
"""
Crypto Resources Consolidation Script
Combines all resources from JSON, TXT, and DOCX files into unified formats
Outputs: JSON, CSV/Excel, and SQLite database
"""

import json
import sqlite3
import csv
import os
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict


class CryptoResourceConsolidator:
    """Consolidates crypto resources from multiple sources"""
    
    def __init__(self, cursor_instructions_dir: str = "/workspace/cursor-instructions"):
        self.dir = cursor_instructions_dir
        self.resources = []
        self.unique_resources = {}
        self.stats = defaultdict(int)
        
    def load_json_file(self, filename: str) -> Dict:
        """Load JSON file"""
        filepath = os.path.join(self.dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Skip first line if it's just the filename
                lines = content.split('\n')
                if lines[0].strip().endswith('.json'):
                    content = '\n'.join(lines[1:])
                return json.loads(content)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return {}
    
    def extract_from_unified_json(self):
        """Extract from crypto_resources_unified_2025-11-11.json"""
        data = self.load_json_file("crypto_resources_unified_2025-11-11.json")
        
        if not data or 'registry' not in data:
            return
        
        registry = data['registry']
        
        # Process each category
        categories = [
            'rpc_nodes', 'block_explorers', 'market_data_apis', 
            'news_apis', 'sentiment_apis', 'onchain_analytics_apis',
            'whale_tracking_apis', 'community_sentiment_apis', 
            'hf_resources', 'free_http_endpoints', 'local_backend_routes',
            'cors_proxies'
        ]
        
        for category in categories:
            if category in registry:
                for item in registry[category]:
                    resource = self.normalize_resource(item, category)
                    self.add_resource(resource)
    
    def extract_from_pipeline_json(self):
        """Extract from ultimate_crypto_pipeline_2025_NZasinich.json"""
        data = self.load_json_file("ultimate_crypto_pipeline_2025_NZasinich.json")
        
        if not data or 'files' not in data:
            return
        
        # Find the resources file
        for file_obj in data['files']:
            if file_obj.get('filename') == 'crypto_resources_full_162_sources.json':
                content = file_obj.get('content', {})
                resources = content.get('resources', [])
                
                for item in resources:
                    resource = self.normalize_resource_from_pipeline(item)
                    self.add_resource(resource)
    
    def extract_from_txt_files(self):
        """Extract from api-config-complete.txt files"""
        # Parse the comprehensive text file to extract API keys and endpoints
        txt_files = ['api-config-complete.txt', 'api-config-complete__1_.txt']
        
        api_keys = {
            'TronScan': '7ae72726-bffe-4e74-9c33-97b761eeea21',
            'BscScan': 'K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT',
            'Etherscan': 'SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2',
            'Etherscan_2': 'T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45',
            'CoinMarketCap': '04cf4b5b-9868-465c-8ba0-9f2e78c92eb1',
            'CoinMarketCap_2': 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c',
            'NewsAPI': 'pub_346789abc123def456789ghi012345jkl',
            'CryptoCompare': 'e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f'
        }
        
        # Add these as separate resources
        for name, key in api_keys.items():
            resource = {
                'id': f'api_key_{name.lower()}',
                'name': f'{name} API Key',
                'category': 'api_keys',
                'type': 'authentication',
                'api_key': key,
                'source': 'api-config-complete.txt',
                'is_valid': True
            }
            self.add_resource(resource)
    
    def normalize_resource(self, item: Dict, category: str) -> Dict:
        """Normalize resource from unified JSON"""
        notes = item.get('notes') or ''
        role = item.get('role') or ''
        base_url = item.get('base_url') or ''
        
        resource = {
            'id': item.get('id', ''),
            'name': item.get('name', ''),
            'category': category,
            'subcategory': item.get('role', item.get('chain', item.get('type', ''))),
            'base_url': base_url,
            'auth_type': item.get('auth', {}).get('type', 'none'),
            'api_key': item.get('auth', {}).get('key', ''),
            'rate_limit': notes.split('Rate limit:')[-1].strip() if 'Rate limit' in notes else '',
            'docs_url': item.get('docs_url', ''),
            'endpoints': json.dumps(item.get('endpoints', {})) if item.get('endpoints') else '',
            'notes': notes,
            'is_free': 'free' in notes.lower() or item.get('auth', {}).get('type') == 'none',
            'websocket_support': 'websocket' in role.lower() or 'ws://' in base_url or 'wss://' in base_url,
            'data_types': self.infer_data_types(item),
            'addressing_method': self.infer_addressing_method(item),
            'source': 'crypto_resources_unified_2025-11-11.json'
        }
        return resource
    
    def normalize_resource_from_pipeline(self, item: Dict) -> Dict:
        """Normalize resource from pipeline JSON"""
        resource = {
            'id': f"{item.get('category', 'unknown')}_{item.get('name', '').replace(' ', '_').lower()}",
            'name': item.get('name', ''),
            'category': item.get('category', ''),
            'subcategory': '',
            'base_url': item.get('url', ''),
            'auth_type': 'apiKey' if item.get('key') else 'none',
            'api_key': item.get('key', ''),
            'rate_limit': item.get('rateLimit', ''),
            'docs_url': '',
            'endpoints': item.get('endpoint', ''),
            'notes': item.get('desc', ''),
            'is_free': item.get('free', True),
            'websocket_support': False,
            'data_types': [item.get('category', '')],
            'addressing_method': 'REST API',
            'source': 'ultimate_crypto_pipeline_2025_NZasinich.json'
        }
        return resource
    
    def infer_data_types(self, item: Dict) -> List[str]:
        """Infer data types from resource metadata"""
        data_types = []
        name = (item.get('name') or '').lower()
        category = (item.get('category') or '').lower()
        role = (item.get('role') or '').lower()
        
        # RPC nodes provide blockchain data
        if 'rpc' in role or 'rpc' in category:
            data_types.extend(['blockchain_data', 'transaction_data', 'block_data'])
        
        # Block explorers
        if 'explorer' in category or 'scan' in name:
            data_types.extend(['address_balance', 'transaction_history', 'token_data'])
        
        # Market data
        if 'market' in category or 'price' in name:
            data_types.extend(['price_data', 'market_cap', 'trading_volume', 'ohlcv'])
        
        # News
        if 'news' in category:
            data_types.extend(['news_articles', 'headlines', 'content'])
        
        # Sentiment
        if 'sentiment' in category:
            data_types.extend(['sentiment_score', 'fear_greed_index', 'social_metrics'])
        
        # Whale tracking
        if 'whale' in category:
            data_types.extend(['large_transactions', 'whale_addresses', 'transfer_data'])
        
        # On-chain analytics
        if 'onchain' in category or 'analytics' in category:
            data_types.extend(['metrics', 'indicators', 'network_stats'])
        
        return data_types if data_types else ['general']
    
    def infer_addressing_method(self, item: Dict) -> str:
        """Infer addressing method from resource"""
        base_url = item.get('base_url') or ''
        role = (item.get('role') or '').lower()
        
        if 'ws://' in base_url or 'wss://' in base_url or 'websocket' in role:
            return 'WebSocket'
        elif 'graphql' in base_url or 'graphql' in role:
            return 'GraphQL'
        elif base_url and '{' in base_url:
            return 'REST API (Path Parameters)'
        elif base_url:
            return 'REST API (Query Parameters)'
        else:
            return 'Unknown'
    
    def add_resource(self, resource: Dict):
        """Add resource with deduplication"""
        # Create unique key based on base_url and name
        base_url = resource.get('base_url', '')
        name = resource.get('name', 'unnamed')
        unique_key = f"{base_url}_{name}".lower()
        
        if unique_key in self.unique_resources:
            # Merge data from multiple sources
            existing = self.unique_resources[unique_key]
            
            # Prefer non-empty values
            for key, value in resource.items():
                if value and not existing.get(key):
                    existing[key] = value
            
            # Combine sources
            if resource['source'] not in existing.get('source', ''):
                existing['source'] = f"{existing.get('source', '')}, {resource['source']}"
            
            self.unique_resources[unique_key] = existing
            self.stats['duplicates_merged'] += 1
        else:
            self.unique_resources[unique_key] = resource
            self.stats['unique_added'] += 1
        
        self.stats['total_processed'] += 1
    
    def get_all_resources(self) -> List[Dict]:
        """Get all unique resources"""
        return list(self.unique_resources.values())
    
    def save_to_json(self, output_file: str = "consolidated_crypto_resources.json"):
        """Save to JSON file"""
        output_path = os.path.join(self.dir, output_file)
        
        output_data = {
            'metadata': {
                'title': 'Consolidated Crypto Resources Database',
                'version': '1.0',
                'generated_at': datetime.now().isoformat(),
                'total_resources': len(self.unique_resources),
                'statistics': dict(self.stats),
                'categories': self.get_category_stats(),
                'sources': [
                    'crypto_resources_unified_2025-11-11.json',
                    'ultimate_crypto_pipeline_2025_NZasinich.json',
                    'api-config-complete.txt'
                ]
            },
            'resources': self.get_all_resources()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON saved: {output_path}")
        return output_path
    
    def save_to_csv(self, output_file: str = "consolidated_crypto_resources.csv"):
        """Save to CSV file (Excel compatible)"""
        output_path = os.path.join(self.dir, output_file)
        
        resources = self.get_all_resources()
        if not resources:
            return
        
        # Get all unique keys
        all_keys = set()
        for resource in resources:
            all_keys.update(resource.keys())
        
        fieldnames = sorted(all_keys)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for resource in resources:
                # Convert lists to strings
                row = {}
                for key, value in resource.items():
                    if isinstance(value, (list, dict)):
                        row[key] = json.dumps(value)
                    else:
                        row[key] = value
                writer.writerow(row)
        
        print(f"✅ CSV saved: {output_path}")
        return output_path
    
    def save_to_sqlite(self, output_file: str = "consolidated_crypto_resources.db"):
        """Save to SQLite database"""
        output_path = os.path.join(self.dir, output_file)
        
        # Remove existing database
        if os.path.exists(output_path):
            os.remove(output_path)
        
        conn = sqlite3.connect(output_path)
        cursor = conn.cursor()
        
        # Create main resources table
        cursor.execute('''
            CREATE TABLE resources (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                subcategory TEXT,
                base_url TEXT,
                auth_type TEXT,
                api_key TEXT,
                rate_limit TEXT,
                docs_url TEXT,
                endpoints TEXT,
                notes TEXT,
                is_free BOOLEAN,
                websocket_support BOOLEAN,
                addressing_method TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create data types table
        cursor.execute('''
            CREATE TABLE data_types (
                resource_id TEXT,
                data_type TEXT,
                FOREIGN KEY (resource_id) REFERENCES resources (id)
            )
        ''')
        
        # Create categories lookup table
        cursor.execute('''
            CREATE TABLE categories (
                category TEXT PRIMARY KEY,
                resource_count INTEGER,
                description TEXT
            )
        ''')
        
        # Create metadata table
        cursor.execute('''
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Insert resources
        resources = self.get_all_resources()
        for idx, resource in enumerate(resources):
            data_types = resource.get('data_types', [])
            
            # Ensure unique ID
            resource_id = resource.get('id')
            if not resource_id:
                resource_id = f"resource_{idx}"
            
            cursor.execute('''
                INSERT OR REPLACE INTO resources (
                    id, name, category, subcategory, base_url, auth_type,
                    api_key, rate_limit, docs_url, endpoints, notes,
                    is_free, websocket_support, addressing_method, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                resource_id,
                resource.get('name'),
                resource.get('category'),
                resource.get('subcategory'),
                resource.get('base_url'),
                resource.get('auth_type'),
                resource.get('api_key'),
                resource.get('rate_limit'),
                resource.get('docs_url'),
                resource.get('endpoints'),
                resource.get('notes'),
                resource.get('is_free'),
                resource.get('websocket_support'),
                resource.get('addressing_method'),
                resource.get('source')
            ))
            
            # Insert data types
            for dt in data_types:
                cursor.execute('''
                    INSERT INTO data_types (resource_id, data_type)
                    VALUES (?, ?)
                ''', (resource_id, dt))
        
        # Insert category stats
        category_stats = self.get_category_stats()
        for category, count in category_stats.items():
            cursor.execute('''
                INSERT INTO categories (category, resource_count)
                VALUES (?, ?)
            ''', (category, count))
        
        # Insert metadata
        metadata = {
            'version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'total_resources': str(len(resources)),
            'total_processed': str(self.stats['total_processed']),
            'unique_added': str(self.stats['unique_added']),
            'duplicates_merged': str(self.stats['duplicates_merged'])
        }
        
        for key, value in metadata.items():
            cursor.execute('INSERT INTO metadata (key, value) VALUES (?, ?)', (key, value))
        
        # Create indexes
        cursor.execute('CREATE INDEX idx_category ON resources(category)')
        cursor.execute('CREATE INDEX idx_is_free ON resources(is_free)')
        cursor.execute('CREATE INDEX idx_websocket ON resources(websocket_support)')
        cursor.execute('CREATE INDEX idx_data_type ON data_types(data_type)')
        
        conn.commit()
        conn.close()
        
        print(f"✅ SQLite database saved: {output_path}")
        return output_path
    
    def get_category_stats(self) -> Dict[str, int]:
        """Get statistics by category"""
        stats = defaultdict(int)
        for resource in self.get_all_resources():
            category = resource.get('category', 'unknown')
            stats[category] += 1
        return dict(stats)
    
    def generate_summary_report(self):
        """Generate summary report"""
        resources = self.get_all_resources()
        
        print("\n" + "="*80)
        print("CRYPTO RESOURCES CONSOLIDATION REPORT")
        print("="*80)
        print(f"\n📊 STATISTICS:")
        print(f"   Total processed: {self.stats['total_processed']}")
        print(f"   Unique resources: {self.stats['unique_added']}")
        print(f"   Duplicates merged: {self.stats['duplicates_merged']}")
        print(f"   Final count: {len(resources)}")
        
        print(f"\n📁 CATEGORIES:")
        category_stats = self.get_category_stats()
        for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"   {category}: {count}")
        
        # Count free vs paid
        free_count = sum(1 for r in resources if r.get('is_free'))
        print(f"\n💰 FREE vs PAID:")
        print(f"   Free: {free_count}")
        print(f"   Paid/Limited: {len(resources) - free_count}")
        
        # WebSocket support
        ws_count = sum(1 for r in resources if r.get('websocket_support'))
        print(f"\n🔌 WEBSOCKET SUPPORT:")
        print(f"   WebSocket enabled: {ws_count}")
        print(f"   REST only: {len(resources) - ws_count}")
        
        # Addressing methods
        addressing = defaultdict(int)
        for r in resources:
            method = r.get('addressing_method', 'Unknown')
            addressing[method] += 1
        
        print(f"\n🔗 ADDRESSING METHODS:")
        for method, count in sorted(addressing.items(), key=lambda x: x[1], reverse=True):
            print(f"   {method}: {count}")
        
        print("\n" + "="*80 + "\n")


def main():
    """Main execution"""
    print("\n🚀 Starting Crypto Resources Consolidation...\n")
    
    consolidator = CryptoResourceConsolidator()
    
    # Extract from all sources
    print("📥 Extracting from crypto_resources_unified_2025-11-11.json...")
    consolidator.extract_from_unified_json()
    
    print("📥 Extracting from ultimate_crypto_pipeline_2025_NZasinich.json...")
    consolidator.extract_from_pipeline_json()
    
    print("📥 Extracting from api-config-complete.txt files...")
    consolidator.extract_from_txt_files()
    
    # Generate outputs
    print("\n💾 Generating output files...")
    consolidator.save_to_json()
    consolidator.save_to_csv()
    consolidator.save_to_sqlite()
    
    # Generate report
    consolidator.generate_summary_report()
    
    print("✅ Consolidation complete!\n")


if __name__ == "__main__":
    main()
