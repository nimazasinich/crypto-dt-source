#!/usr/bin/env python3
"""
Resource Manager - مدیریت منابع API با قابلیت Import/Export
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil


class ResourceManager:
    """مدیریت منابع API"""
    
    def __init__(self, config_file: str = "providers_config_ultimate.json"):
        self.config_file = Path(config_file)
        self.resources: Dict[str, Any] = {}
        self.load_resources()
    
    def load_resources(self):
        """بارگذاری منابع از فایل"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.resources = json.load(f)
                print(f"✅ Loaded resources from {self.config_file}")
            except Exception as e:
                print(f"❌ Error loading resources: {e}")
                self.resources = {"providers": {}, "schema_version": "3.0.0"}
        else:
            self.resources = {"providers": {}, "schema_version": "3.0.0"}
    
    def save_resources(self):
        """ذخیره منابع در فایل"""
        try:
            # Backup فایل قبلی
            if self.config_file.exists():
                backup_file = self.config_file.parent / f"{self.config_file.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                shutil.copy2(self.config_file, backup_file)
                print(f"✅ Backup created: {backup_file}")
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.resources, f, indent=2, ensure_ascii=False)
            print(f"✅ Resources saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Error saving resources: {e}")
    
    def add_provider(self, provider_data: Dict[str, Any]):
        """افزودن provider جدید"""
        provider_id = provider_data.get('id') or provider_data.get('name', '').lower().replace(' ', '_')
        
        if 'providers' not in self.resources:
            self.resources['providers'] = {}
        
        self.resources['providers'][provider_id] = provider_data
        
        # به‌روزرسانی تعداد کل
        if 'total_providers' in self.resources:
            self.resources['total_providers'] = len(self.resources['providers'])
        
        print(f"✅ Provider added: {provider_id}")
        return provider_id
    
    def remove_provider(self, provider_id: str):
        """حذف provider"""
        if provider_id in self.resources.get('providers', {}):
            del self.resources['providers'][provider_id]
            self.resources['total_providers'] = len(self.resources['providers'])
            print(f"✅ Provider removed: {provider_id}")
            return True
        return False
    
    def update_provider(self, provider_id: str, updates: Dict[str, Any]):
        """به‌روزرسانی provider"""
        if provider_id in self.resources.get('providers', {}):
            self.resources['providers'][provider_id].update(updates)
            print(f"✅ Provider updated: {provider_id}")
            return True
        return False
    
    def get_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """دریافت provider"""
        return self.resources.get('providers', {}).get(provider_id)
    
    def get_all_providers(self) -> Dict[str, Any]:
        """دریافت همه providers"""
        return self.resources.get('providers', {})
    
    def get_providers_by_category(self, category: str) -> List[Dict[str, Any]]:
        """دریافت providers بر اساس category"""
        return [
            {**provider, 'id': pid}
            for pid, provider in self.resources.get('providers', {}).items()
            if provider.get('category') == category
        ]
    
    def export_to_json(self, filepath: str, include_metadata: bool = True):
        """صادرکردن به JSON"""
        export_data = {}
        
        if include_metadata:
            export_data['metadata'] = {
                'exported_at': datetime.now().isoformat(),
                'total_providers': len(self.resources.get('providers', {})),
                'schema_version': self.resources.get('schema_version', '3.0.0')
            }
        
        export_data['providers'] = self.resources.get('providers', {})
        export_data['fallback_strategy'] = self.resources.get('fallback_strategy', {})
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported {len(export_data['providers'])} providers to {filepath}")
    
    def export_to_csv(self, filepath: str):
        """صادرکردن به CSV"""
        providers = self.resources.get('providers', {})
        
        if not providers:
            print("⚠️  No providers to export")
            return
        
        fieldnames = [
            'id', 'name', 'category', 'base_url', 'requires_auth',
            'priority', 'weight', 'free', 'docs_url', 'rate_limit'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for provider_id, provider in providers.items():
                row = {
                    'id': provider_id,
                    'name': provider.get('name', ''),
                    'category': provider.get('category', ''),
                    'base_url': provider.get('base_url', ''),
                    'requires_auth': str(provider.get('requires_auth', False)),
                    'priority': str(provider.get('priority', 5)),
                    'weight': str(provider.get('weight', 50)),
                    'free': str(provider.get('free', True)),
                    'docs_url': provider.get('docs_url', ''),
                    'rate_limit': json.dumps(provider.get('rate_limit', {}))
                }
                writer.writerow(row)
        
        print(f"✅ Exported {len(providers)} providers to {filepath}")
    
    def import_from_json(self, filepath: str, merge: bool = True):
        """وارد کردن از JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # تشخیص ساختار فایل
            if 'providers' in import_data:
                imported_providers = import_data['providers']
            elif 'registry' in import_data:
                # ساختار crypto_resources_unified
                imported_providers = self._convert_unified_format(import_data['registry'])
            else:
                imported_providers = import_data
            
            if not isinstance(imported_providers, dict):
                print("❌ Invalid JSON structure")
                return False
            
            if merge:
                # ادغام با منابع موجود
                if 'providers' not in self.resources:
                    self.resources['providers'] = {}
                
                for provider_id, provider_data in imported_providers.items():
                    if provider_id in self.resources['providers']:
                        # به‌روزرسانی provider موجود
                        self.resources['providers'][provider_id].update(provider_data)
                    else:
                        # افزودن provider جدید
                        self.resources['providers'][provider_id] = provider_data
            else:
                # جایگزینی کامل
                self.resources['providers'] = imported_providers
            
            self.resources['total_providers'] = len(self.resources['providers'])
            
            print(f"✅ Imported {len(imported_providers)} providers from {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Error importing from JSON: {e}")
            return False
    
    def _convert_unified_format(self, registry_data: Dict[str, Any]) -> Dict[str, Any]:
        """تبدیل فرمت unified به فرمت استاندارد"""
        converted = {}
        
        # تبدیل RPC nodes
        for rpc in registry_data.get('rpc_nodes', []):
            provider_id = rpc.get('id', rpc['name'].lower().replace(' ', '_'))
            converted[provider_id] = {
                'id': provider_id,
                'name': rpc['name'],
                'category': 'rpc',
                'chain': rpc.get('chain', ''),
                'base_url': rpc['base_url'],
                'requires_auth': rpc['auth']['type'] != 'none',
                'docs_url': rpc.get('docs_url'),
                'notes': rpc.get('notes', ''),
                'free': True
            }
        
        # تبدیل Block Explorers
        for explorer in registry_data.get('block_explorers', []):
            provider_id = explorer.get('id', explorer['name'].lower().replace(' ', '_'))
            converted[provider_id] = {
                'id': provider_id,
                'name': explorer['name'],
                'category': 'blockchain_explorer',
                'chain': explorer.get('chain', ''),
                'base_url': explorer['base_url'],
                'requires_auth': explorer['auth']['type'] != 'none',
                'api_keys': [explorer['auth']['key']] if explorer['auth'].get('key') else [],
                'auth_type': explorer['auth'].get('type', 'none'),
                'docs_url': explorer.get('docs_url'),
                'endpoints': explorer.get('endpoints', {}),
                'free': explorer['auth']['type'] == 'none'
            }
        
        # تبدیل Market Data APIs
        for market in registry_data.get('market_data_apis', []):
            provider_id = market.get('id', market['name'].lower().replace(' ', '_'))
            converted[provider_id] = {
                'id': provider_id,
                'name': market['name'],
                'category': 'market_data',
                'base_url': market['base_url'],
                'requires_auth': market['auth']['type'] != 'none',
                'api_keys': [market['auth']['key']] if market['auth'].get('key') else [],
                'auth_type': market['auth'].get('type', 'none'),
                'docs_url': market.get('docs_url'),
                'endpoints': market.get('endpoints', {}),
                'free': market.get('role', '').endswith('_free') or market['auth']['type'] == 'none'
            }
        
        # تبدیل News APIs
        for news in registry_data.get('news_apis', []):
            provider_id = news.get('id', news['name'].lower().replace(' ', '_'))
            converted[provider_id] = {
                'id': provider_id,
                'name': news['name'],
                'category': 'news',
                'base_url': news['base_url'],
                'requires_auth': news['auth']['type'] != 'none',
                'api_keys': [news['auth']['key']] if news['auth'].get('key') else [],
                'docs_url': news.get('docs_url'),
                'endpoints': news.get('endpoints', {}),
                'free': True
            }
        
        # تبدیل Sentiment APIs
        for sentiment in registry_data.get('sentiment_apis', []):
            provider_id = sentiment.get('id', sentiment['name'].lower().replace(' ', '_'))
            converted[provider_id] = {
                'id': provider_id,
                'name': sentiment['name'],
                'category': 'sentiment',
                'base_url': sentiment['base_url'],
                'requires_auth': sentiment['auth']['type'] != 'none',
                'docs_url': sentiment.get('docs_url'),
                'endpoints': sentiment.get('endpoints', {}),
                'free': True
            }
        
        return converted
    
    def import_from_csv(self, filepath: str):
        """وارد کردن از CSV"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                imported = 0
                for row in reader:
                    provider_id = row.get('id', row.get('name', '').lower().replace(' ', '_'))
                    
                    provider_data = {
                        'id': provider_id,
                        'name': row.get('name', ''),
                        'category': row.get('category', ''),
                        'base_url': row.get('base_url', ''),
                        'requires_auth': row.get('requires_auth', 'False').lower() == 'true',
                        'priority': int(row.get('priority', 5)),
                        'weight': int(row.get('weight', 50)),
                        'free': row.get('free', 'True').lower() == 'true',
                        'docs_url': row.get('docs_url', '')
                    }
                    
                    if row.get('rate_limit'):
                        try:
                            provider_data['rate_limit'] = json.loads(row['rate_limit'])
                        except:
                            pass
                    
                    self.add_provider(provider_data)
                    imported += 1
                
                print(f"✅ Imported {imported} providers from CSV")
                return True
                
        except Exception as e:
            print(f"❌ Error importing from CSV: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """آمار منابع"""
        providers = self.resources.get('providers', {})
        
        stats = {
            'total_providers': len(providers),
            'by_category': {},
            'by_auth': {'requires_auth': 0, 'no_auth': 0},
            'by_free': {'free': 0, 'paid': 0}
        }
        
        for provider in providers.values():
            category = provider.get('category', 'unknown')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            if provider.get('requires_auth'):
                stats['by_auth']['requires_auth'] += 1
            else:
                stats['by_auth']['no_auth'] += 1
            
            if provider.get('free', True):
                stats['by_free']['free'] += 1
            else:
                stats['by_free']['paid'] += 1
        
        return stats
    
    def validate_provider(self, provider_data: Dict[str, Any]) -> tuple[bool, str]:
        """اعتبارسنجی provider"""
        required_fields = ['name', 'category', 'base_url']
        
        for field in required_fields:
            if field not in provider_data:
                return False, f"Missing required field: {field}"
        
        if not isinstance(provider_data.get('base_url'), str) or not provider_data['base_url'].startswith(('http://', 'https://')):
            return False, "Invalid base_url format"
        
        return True, "Valid"
    
    def backup(self, backup_dir: str = "backups"):
        """پشتیبان‌گیری از منابع"""
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_path / f"resources_backup_{timestamp}.json"
        
        self.export_to_json(str(backup_file), include_metadata=True)
        
        return str(backup_file)


# تست
if __name__ == "__main__":
    print("🧪 Testing Resource Manager...\n")
    
    manager = ResourceManager()
    
    # آمار
    stats = manager.get_statistics()
    print("📊 Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Export
    manager.export_to_json("test_export.json")
    manager.export_to_csv("test_export.csv")
    
    # Backup
    backup_file = manager.backup()
    print(f"✅ Backup created: {backup_file}")
    
    print("\n✅ Resource Manager test completed")

