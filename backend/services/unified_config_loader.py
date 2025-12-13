"""
Unified Configuration Loader
Loads all APIs from JSON files at project root with scheduling and persistence support
"""
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class UnifiedConfigLoader:
    """Load and manage all API configurations from JSON files"""

    def __init__(self, config_dir: str = '.'):
        self.config_dir = Path(config_dir)
        self.apis: Dict[str, Dict[str, Any]] = {}
        self.keys: Dict[str, str] = {}
        self.cors_proxies: List[str] = []
        self.schedules: Dict[str, Dict[str, Any]] = {}
        self.config_files = [
            'crypto_resources_unified_2025-11-11.json',
            'all_apis_merged_2025.json',
            'ultimate_crypto_pipeline_2025_NZasinich.json'
        ]
        self.load_all_configs()

    def load_all_configs(self):
        """Load configurations from all JSON files"""
        logger.info("Loading unified configurations...")

        # Load primary unified config
        self.load_unified_config()

        # Load merged APIs
        self.load_merged_apis()

        # Load pipeline config
        self.load_pipeline_config()

        # Setup CORS proxies
        self.setup_cors_proxies()

        # Setup default schedules
        self.setup_default_schedules()

        logger.info(f"✓ Loaded {len(self.apis)} API sources")
        logger.info(f"✓ Found {len(self.keys)} API keys")
        logger.info(f"✓ Configured {len(self.schedules)} schedules")

    def load_unified_config(self):
        """Load crypto_resources_unified_2025-11-11.json"""
        config_path = self.config_dir / 'crypto_resources_unified_2025-11-11.json'

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            registry = data.get('registry', {})

            # Load RPC nodes
            for entry in registry.get('rpc_nodes', []):
                api_id = entry['id']
                self.apis[api_id] = {
                    'id': api_id,
                    'name': entry['name'],
                    'category': entry.get('chain', 'rpc_nodes'),
                    'base_url': entry['base_url'],
                    'auth': entry.get('auth', {}),
                    'docs_url': entry.get('docs_url'),
                    'endpoints': entry.get('endpoints'),
                    'notes': entry.get('notes'),
                    'role': entry.get('role', 'rpc'),
                    'priority': 1,
                    'update_type': 'realtime' if entry.get('role') == 'websocket' else 'periodic',
                    'enabled': True
                }

                # Extract embedded keys
                auth = entry.get('auth', {})
                if auth.get('key'):
                    self.keys[api_id] = auth['key']

            # Load block explorers
            for entry in registry.get('block_explorers', []):
                api_id = entry['id']
                self.apis[api_id] = {
                    'id': api_id,
                    'name': entry['name'],
                    'category': 'blockchain_explorers',
                    'base_url': entry['base_url'],
                    'auth': entry.get('auth', {}),
                    'docs_url': entry.get('docs_url'),
                    'endpoints': entry.get('endpoints'),
                    'notes': entry.get('notes'),
                    'priority': 1,
                    'update_type': 'periodic',
                    'enabled': True
                }

                auth = entry.get('auth', {})
                if auth.get('key'):
                    self.keys[api_id] = auth['key']

            # Load market data sources
            for entry in registry.get('market_data', []):
                api_id = entry['id']
                self.apis[api_id] = {
                    'id': api_id,
                    'name': entry['name'],
                    'category': 'market_data',
                    'base_url': entry['base_url'],
                    'auth': entry.get('auth', {}),
                    'docs_url': entry.get('docs_url'),
                    'endpoints': entry.get('endpoints'),
                    'notes': entry.get('notes'),
                    'priority': 1,
                    'update_type': 'periodic',
                    'enabled': True
                }

                auth = entry.get('auth', {})
                if auth.get('key'):
                    self.keys[api_id] = auth['key']

            # Load news sources
            for entry in registry.get('news', []):
                api_id = entry['id']
                self.apis[api_id] = {
                    'id': api_id,
                    'name': entry['name'],
                    'category': 'news',
                    'base_url': entry['base_url'],
                    'auth': entry.get('auth', {}),
                    'docs_url': entry.get('docs_url'),
                    'endpoints': entry.get('endpoints'),
                    'notes': entry.get('notes'),
                    'priority': 2,
                    'update_type': 'periodic',
                    'enabled': True
                }

            # Load sentiment sources
            for entry in registry.get('sentiment', []):
                api_id = entry['id']
                self.apis[api_id] = {
                    'id': api_id,
                    'name': entry['name'],
                    'category': 'sentiment',
                    'base_url': entry['base_url'],
                    'auth': entry.get('auth', {}),
                    'docs_url': entry.get('docs_url'),
                    'endpoints': entry.get('endpoints'),
                    'notes': entry.get('notes'),
                    'priority': 2,
                    'update_type': 'periodic',
                    'enabled': True
                }

            # Load HuggingFace resources
            for entry in registry.get('huggingface', []):
                api_id = entry['id']
                self.apis[api_id] = {
                    'id': api_id,
                    'name': entry['name'],
                    'category': 'huggingface',
                    'base_url': entry.get('base_url', 'https://huggingface.co'),
                    'auth': entry.get('auth', {}),
                    'docs_url': entry.get('docs_url'),
                    'endpoints': entry.get('endpoints'),
                    'notes': entry.get('notes'),
                    'resource_type': entry.get('resource_type', 'model'),
                    'priority': 2,
                    'update_type': 'scheduled',  # HF should update less frequently
                    'enabled': True
                }

            # Load on-chain analytics
            for entry in registry.get('onchain_analytics', []):
                api_id = entry['id']
                self.apis[api_id] = {
                    'id': api_id,
                    'name': entry['name'],
                    'category': 'onchain_analytics',
                    'base_url': entry['base_url'],
                    'auth': entry.get('auth', {}),
                    'docs_url': entry.get('docs_url'),
                    'endpoints': entry.get('endpoints'),
                    'notes': entry.get('notes'),
                    'priority': 2,
                    'update_type': 'periodic',
                    'enabled': True
                }

            # Load whale tracking
            for entry in registry.get('whale_tracking', []):
                api_id = entry['id']
                self.apis[api_id] = {
                    'id': api_id,
                    'name': entry['name'],
                    'category': 'whale_tracking',
                    'base_url': entry['base_url'],
                    'auth': entry.get('auth', {}),
                    'docs_url': entry.get('docs_url'),
                    'endpoints': entry.get('endpoints'),
                    'notes': entry.get('notes'),
                    'priority': 2,
                    'update_type': 'periodic',
                    'enabled': True
                }

            # Load local backend routes (PRIORITY 0 - highest)
            for entry in registry.get('local_backend_routes', []):
                api_id = entry['id']
                notes = entry.get('notes', '')
                
                # Extract HTTP method from notes
                method = 'GET'  # default
                if notes:
                    notes_lower = notes.lower()
                    if 'post method' in notes_lower:
                        method = 'POST'
                    elif 'websocket' in notes_lower:
                        method = 'WS'
                
                # Determine feature category from base_url
                base_url = entry['base_url'].lower()
                feature_category = 'local'
                if '/market' in base_url:
                    feature_category = 'market_data'
                elif '/sentiment' in base_url:
                    feature_category = 'sentiment'
                elif '/news' in base_url:
                    feature_category = 'news'
                elif '/crypto' in base_url:
                    feature_category = 'crypto_data'
                elif '/models' in base_url or '/hf' in base_url:
                    feature_category = 'ai_models'
                elif '/providers' in base_url or '/pools' in base_url:
                    feature_category = 'monitoring'
                elif '/ws' in base_url or base_url.startswith('ws://'):
                    feature_category = 'websocket'
                
                self.apis[api_id] = {
                    'id': api_id,
                    'name': entry['name'],
                    'category': 'local',
                    'feature_category': feature_category,  # Secondary categorization
                    'base_url': entry['base_url'],
                    'auth': entry.get('auth', {}),
                    'docs_url': entry.get('docs_url'),
                    'endpoints': entry.get('endpoints'),
                    'notes': entry.get('notes'),
                    'method': method,
                    'priority': 0,  # Highest priority - prefer local routes
                    'update_type': 'local',
                    'enabled': True,
                    'is_local': True
                }

            logger.info(f"✓ Loaded unified config with {len(self.apis)} entries")

        except Exception as e:
            logger.error(f"Error loading unified config: {e}")

    def load_merged_apis(self):
        """Load all_apis_merged_2025.json for additional sources"""
        config_path = self.config_dir / 'all_apis_merged_2025.json'

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Process merged data structure (flexible parsing)
            if isinstance(data, dict):
                for category, entries in data.items():
                    if isinstance(entries, list):
                        for entry in entries:
                            self._process_merged_entry(entry, category)
                    elif isinstance(entries, dict):
                        self._process_merged_entry(entries, category)

            logger.info("✓ Loaded merged APIs config")

        except Exception as e:
            logger.error(f"Error loading merged APIs: {e}")

    def _process_merged_entry(self, entry: Dict, category: str):
        """Process a single merged API entry"""
        if not isinstance(entry, dict):
            return

        api_id = entry.get('id', entry.get('name', '')).lower().replace(' ', '_')

        # Skip if already loaded
        if api_id in self.apis:
            return

        self.apis[api_id] = {
            'id': api_id,
            'name': entry.get('name', api_id),
            'category': category,
            'base_url': entry.get('url', entry.get('base_url', '')),
            'auth': entry.get('auth', {}),
            'docs_url': entry.get('docs', entry.get('docs_url')),
            'endpoints': entry.get('endpoints'),
            'notes': entry.get('notes', entry.get('description')),
            'priority': entry.get('priority', 3),
            'update_type': entry.get('update_type', 'periodic'),
            'enabled': entry.get('enabled', True)
        }

    def load_pipeline_config(self):
        """Load ultimate_crypto_pipeline_2025_NZasinich.json"""
        config_path = self.config_dir / 'ultimate_crypto_pipeline_2025_NZasinich.json'

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract pipeline-specific configurations
            pipeline = data.get('pipeline', {})

            # Update scheduling preferences from pipeline
            for stage in pipeline.get('stages', []):
                stage_name = stage.get('name', '')
                interval = stage.get('interval', 300)

                # Map pipeline stages to API categories
                if 'market' in stage_name.lower():
                    self._update_category_schedule('market_data', interval)
                elif 'sentiment' in stage_name.lower():
                    self._update_category_schedule('sentiment', interval)
                elif 'huggingface' in stage_name.lower() or 'hf' in stage_name.lower():
                    self._update_category_schedule('huggingface', interval)

            logger.info("✓ Loaded pipeline config")

        except Exception as e:
            logger.error(f"Error loading pipeline config: {e}")

    def _update_category_schedule(self, category: str, interval: int):
        """Update schedule for all APIs in a category"""
        for api_id, api in self.apis.items():
            if api.get('category') == category:
                if api_id not in self.schedules:
                    self.schedules[api_id] = {}
                self.schedules[api_id]['interval'] = interval

    def setup_cors_proxies(self):
        """Setup CORS proxy list"""
        # Disabled on Hugging Face Spaces (avoid third-party proxy services).
        self.cors_proxies = []

    def setup_default_schedules(self):
        """Setup default schedules based on update_type"""
        schedule_intervals = {
            'realtime': 0,  # WebSocket - always connected
            'periodic': 60,  # Every minute for market data
            'scheduled': 3600,  # Every hour for HuggingFace
            'daily': 86400  # Once per day
        }

        for api_id, api in self.apis.items():
            if api_id not in self.schedules:
                update_type = api.get('update_type', 'periodic')
                interval = schedule_intervals.get(update_type, 300)

                self.schedules[api_id] = {
                    'interval': interval,
                    'enabled': api.get('enabled', True),
                    'last_update': None,
                    'next_update': datetime.now(),
                    'update_type': update_type
                }

    def get_all_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get all configured APIs"""
        return self.apis

    def get_apis_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get APIs filtered by category"""
        return {k: v for k, v in self.apis.items() if v.get('category') == category}
    
    def get_apis_by_feature(self, feature: str) -> List[Dict[str, Any]]:
        """
        Get APIs for a specific feature, prioritizing local routes
        Returns sorted list by priority (0=highest)
        """
        matching_apis = []
        
        for api_id, api in self.apis.items():
            # Check if this API matches the feature
            matches = False
            
            # Local routes: check feature_category
            if api.get('is_local') and api.get('feature_category') == feature:
                matches = True
            # External routes: check category
            elif api.get('category') == feature:
                matches = True
            
            if matches and api.get('enabled', True):
                matching_apis.append(api)
        
        # Sort by priority (0=highest) and then by name
        matching_apis.sort(key=lambda x: (x.get('priority', 999), x.get('name', '')))
        
        return matching_apis
    
    def get_local_routes(self) -> Dict[str, Dict[str, Any]]:
        """Get all local backend routes"""
        return {k: v for k, v in self.apis.items() if v.get('is_local', False)}
    
    def get_external_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get all external (non-local) APIs"""
        return {k: v for k, v in self.apis.items() if not v.get('is_local', False)}

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return list(set(api.get('category', 'unknown') for api in self.apis.values()))

    def get_realtime_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get APIs that support real-time updates (WebSocket)"""
        return {k: v for k, v in self.apis.items() if v.get('update_type') == 'realtime'}

    def get_periodic_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get APIs that need periodic updates"""
        return {k: v for k, v in self.apis.items() if v.get('update_type') == 'periodic'}

    def get_scheduled_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get APIs with scheduled updates (less frequent)"""
        return {k: v for k, v in self.apis.items() if v.get('update_type') == 'scheduled'}

    def get_apis_due_for_update(self) -> Dict[str, Dict[str, Any]]:
        """Get APIs that are due for update based on their schedule"""
        now = datetime.now()
        due_apis = {}

        for api_id, schedule in self.schedules.items():
            if not schedule.get('enabled', True):
                continue

            next_update = schedule.get('next_update')
            if next_update and now >= next_update:
                due_apis[api_id] = self.apis[api_id]

        return due_apis

    def update_schedule(self, api_id: str, interval: int = None, enabled: bool = None):
        """Update schedule for a specific API"""
        if api_id not in self.schedules:
            self.schedules[api_id] = {}

        if interval is not None:
            self.schedules[api_id]['interval'] = interval

        if enabled is not None:
            self.schedules[api_id]['enabled'] = enabled

    def mark_updated(self, api_id: str):
        """Mark an API as updated and calculate next update time"""
        if api_id in self.schedules:
            now = datetime.now()
            interval = self.schedules[api_id].get('interval', 300)

            self.schedules[api_id]['last_update'] = now
            self.schedules[api_id]['next_update'] = now + timedelta(seconds=interval)

    def add_custom_api(self, api_data: Dict[str, Any]) -> bool:
        """Add a custom API source"""
        api_id = api_data.get('id', api_data.get('name', '')).lower().replace(' ', '_')

        if not api_id:
            return False

        self.apis[api_id] = {
            'id': api_id,
            'name': api_data.get('name', api_id),
            'category': api_data.get('category', 'custom'),
            'base_url': api_data.get('base_url', api_data.get('url', '')),
            'auth': api_data.get('auth', {}),
            'docs_url': api_data.get('docs_url'),
            'endpoints': api_data.get('endpoints'),
            'notes': api_data.get('notes'),
            'priority': api_data.get('priority', 3),
            'update_type': api_data.get('update_type', 'periodic'),
            'enabled': api_data.get('enabled', True)
        }

        # Setup schedule
        self.schedules[api_id] = {
            'interval': api_data.get('interval', 300),
            'enabled': True,
            'last_update': None,
            'next_update': datetime.now(),
            'update_type': api_data.get('update_type', 'periodic')
        }

        return True

    def remove_api(self, api_id: str) -> bool:
        """Remove an API source"""
        if api_id in self.apis:
            del self.apis[api_id]

        if api_id in self.schedules:
            del self.schedules[api_id]

        if api_id in self.keys:
            del self.keys[api_id]

        return True

    def export_config(self, filepath: str):
        """Export current configuration to JSON"""
        config = {
            'apis': self.apis,
            'schedules': self.schedules,
            'keys': {k: '***' for k in self.keys.keys()},  # Don't export actual keys
            'cors_proxies': self.cors_proxies,
            'exported_at': datetime.now().isoformat()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, default=str)

        return True

    def import_config(self, filepath: str):
        """Import configuration from JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Merge imported configs
        self.apis.update(config.get('apis', {}))
        self.schedules.update(config.get('schedules', {}))
        self.cors_proxies = config.get('cors_proxies', self.cors_proxies)

        return True


# Global instance
unified_loader = UnifiedConfigLoader()
