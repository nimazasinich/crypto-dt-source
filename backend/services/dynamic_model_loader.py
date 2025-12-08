#!/usr/bin/env python3
"""
Dynamic Model Loader - Intelligent Model Detection & Registration
سیستم هوشمند بارگذاری و تشخیص مدل‌های AI

Features:
- Auto-detect API type (HuggingFace, OpenAI, REST, GraphQL, etc.)
- Intelligent endpoint detection
- Automatic initialization
- Persistent storage in database
- Cross-page availability
"""

import httpx
import json
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class DynamicModelLoader:
    """
    هوشمند: تشخیص خودکار نوع API و مدل
    """
    
    def __init__(self, db_path: str = "data/dynamic_models.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        
        # Patterns for API type detection
        self.api_patterns = {
            'huggingface': [
                r'huggingface\.co',
                r'api-inference\.huggingface\.co',
                r'hf\.co',
                r'hf_[a-zA-Z0-9]+',  # HF token pattern
            ],
            'openai': [
                r'openai\.com',
                r'api\.openai\.com',
                r'sk-[a-zA-Z0-9]+',  # OpenAI key pattern
            ],
            'anthropic': [
                r'anthropic\.com',
                r'claude',
                r'sk-ant-',
            ],
            'rest': [
                r'/api/v\d+/',
                r'/rest/',
                r'application/json',
            ],
            'graphql': [
                r'/graphql',
                r'query.*\{',
                r'mutation.*\{',
            ],
            'websocket': [
                r'ws://',
                r'wss://',
            ]
        }
    
    def init_database(self):
        """ایجاد جداول دیتابیس"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول مدل‌های dynamic
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dynamic_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id TEXT UNIQUE NOT NULL,
                model_name TEXT,
                api_type TEXT,
                base_url TEXT,
                api_key TEXT,
                config JSON,
                endpoints JSON,
                is_active BOOLEAN DEFAULT 1,
                auto_detected BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP,
                use_count INTEGER DEFAULT 0
            )
        ''')
        
        # جدول تاریخچه استفاده
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_usage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id TEXT NOT NULL,
                endpoint_used TEXT,
                response_time_ms REAL,
                success BOOLEAN,
                error_message TEXT,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES dynamic_models(model_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Dynamic Models database initialized: {self.db_path}")
    
    async def detect_api_type(self, config: Dict[str, Any]) -> str:
        """
        تشخیص هوشمند نوع API
        
        Args:
            config: تنظیمات ورودی (url, key, headers, etc.)
        
        Returns:
            نوع API (huggingface, openai, rest, graphql, etc.)
        """
        config_str = json.dumps(config).lower()
        
        # Check each pattern
        scores = {}
        for api_type, patterns in self.api_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, config_str, re.IGNORECASE):
                    score += 1
            scores[api_type] = score
        
        # Return type with highest score
        if max(scores.values()) > 0:
            detected_type = max(scores, key=scores.get)
            logger.info(f"🔍 Detected API type: {detected_type} (score: {scores[detected_type]})")
            return detected_type
        
        # Default to REST
        logger.info("🔍 No specific type detected, defaulting to REST")
        return 'rest'
    
    async def auto_discover_endpoints(self, base_url: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        کشف خودکار endpoints
        
        Args:
            base_url: URL پایه
            api_key: کلید API (اختیاری)
        
        Returns:
            لیست endpoints کشف شده
        """
        discovered = {
            'endpoints': [],
            'methods': [],
            'schemas': {}
        }
        
        # Common endpoint patterns to try
        common_paths = [
            '',
            '/docs',
            '/openapi.json',
            '/swagger.json',
            '/api-docs',
            '/health',
            '/status',
            '/models',
            '/v1/models',
            '/api/v1',
        ]
        
        headers = {}
        if api_key:
            # Try different auth patterns
            headers['Authorization'] = f'Bearer {api_key}'
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for path in common_paths:
                try:
                    url = f"{base_url.rstrip('/')}{path}"
                    response = await client.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        discovered['endpoints'].append({
                            'path': path,
                            'url': url,
                            'status': 200,
                            'content_type': response.headers.get('content-type', '')
                        })
                        
                        # If it's JSON, try to parse schema
                        if 'json' in response.headers.get('content-type', ''):
                            try:
                                data = response.json()
                                discovered['schemas'][path] = data
                            except:
                                pass
                
                except Exception as e:
                    logger.debug(f"Failed to discover {path}: {e}")
                    continue
        
        logger.info(f"🔍 Discovered {len(discovered['endpoints'])} endpoints")
        return discovered
    
    async def test_model_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        تست اتصال به مدل
        
        Args:
            config: تنظیمات مدل
        
        Returns:
            نتیجه تست
        """
        api_type = config.get('api_type', 'rest')
        base_url = config.get('base_url', '')
        api_key = config.get('api_key')
        
        result = {
            'success': False,
            'api_type': api_type,
            'response_time_ms': 0,
            'error': None,
            'detected_capabilities': []
        }
        
        start_time = datetime.now()
        
        try:
            # Test based on API type
            if api_type == 'huggingface':
                result = await self._test_huggingface(base_url, api_key)
            elif api_type == 'openai':
                result = await self._test_openai(base_url, api_key)
            elif api_type == 'rest':
                result = await self._test_rest(base_url, api_key)
            elif api_type == 'graphql':
                result = await self._test_graphql(base_url, api_key)
            else:
                result = await self._test_generic(base_url, api_key)
            
            end_time = datetime.now()
            result['response_time_ms'] = (end_time - start_time).total_seconds() * 1000
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"❌ Test failed: {e}")
        
        return result
    
    async def _test_huggingface(self, url: str, api_key: Optional[str]) -> Dict[str, Any]:
        """تست مدل HuggingFace"""
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        # Test with simple input
        test_payload = {'inputs': 'Test'}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=test_payload)
            
            return {
                'success': response.status_code in [200, 503],  # 503 = model loading
                'status_code': response.status_code,
                'detected_capabilities': ['text-classification', 'sentiment-analysis']
                if response.status_code == 200 else ['loading']
            }
    
    async def _test_openai(self, url: str, api_key: Optional[str]) -> Dict[str, Any]:
        """تست API سازگار با OpenAI"""
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        # Test with simple completion
        test_payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': 'Test'}],
            'max_tokens': 5
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{url.rstrip('/')}/v1/chat/completions",
                headers=headers,
                json=test_payload
            )
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'detected_capabilities': ['chat', 'completion', 'embeddings']
            }
    
    async def _test_rest(self, url: str, api_key: Optional[str]) -> Dict[str, Any]:
        """تست REST API عمومی"""
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'detected_capabilities': ['rest-api']
            }
    
    async def _test_graphql(self, url: str, api_key: Optional[str]) -> Dict[str, Any]:
        """تست GraphQL API"""
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        # Introspection query
        query = {'query': '{ __schema { types { name } } }'}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=query)
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'detected_capabilities': ['graphql']
            }
    
    async def _test_generic(self, url: str, api_key: Optional[str]) -> Dict[str, Any]:
        """تست عمومی"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'detected_capabilities': ['unknown']
            }
    
    async def register_model(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        ثبت مدل جدید
        
        Args:
            config: {
                'model_id': 'unique-id',
                'model_name': 'My Model',
                'base_url': 'https://...',
                'api_key': 'xxx',
                'api_type': 'huggingface' (optional, auto-detected),
                'endpoints': {...} (optional, auto-discovered),
                'custom_config': {...} (optional)
            }
        
        Returns:
            نتیجه ثبت
        """
        # Auto-detect API type if not provided
        if 'api_type' not in config:
            config['api_type'] = await self.detect_api_type(config)
        
        # Auto-discover endpoints if not provided
        if 'endpoints' not in config:
            discovered = await self.auto_discover_endpoints(
                config.get('base_url', ''),
                config.get('api_key')
            )
            config['endpoints'] = discovered
        
        # Test connection
        test_result = await self.test_model_connection(config)
        
        if not test_result['success']:
            return {
                'success': False,
                'error': f"Connection test failed: {test_result.get('error', 'Unknown error')}",
                'test_result': test_result
            }
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO dynamic_models
                (model_id, model_name, api_type, base_url, api_key, config, endpoints, auto_detected)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                config.get('model_id'),
                config.get('model_name'),
                config.get('api_type'),
                config.get('base_url'),
                config.get('api_key'),
                json.dumps(config.get('custom_config', {})),
                json.dumps(config.get('endpoints', {})),
                True
            ))
            
            conn.commit()
            
            logger.info(f"✅ Model registered: {config.get('model_id')}")
            
            return {
                'success': True,
                'model_id': config.get('model_id'),
                'api_type': config.get('api_type'),
                'test_result': test_result,
                'message': 'Model registered successfully'
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to register model: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            conn.close()
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """دریافت همه مدل‌های ثبت شده"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM dynamic_models
            WHERE is_active = 1
            ORDER BY use_count DESC, created_at DESC
        ''')
        
        models = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Parse JSON fields
        for model in models:
            model['config'] = json.loads(model.get('config', '{}'))
            model['endpoints'] = json.loads(model.get('endpoints', '{}'))
        
        return models
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """دریافت یک مدل خاص"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM dynamic_models
            WHERE model_id = ? AND is_active = 1
        ''', (model_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            model = dict(row)
            model['config'] = json.loads(model.get('config', '{}'))
            model['endpoints'] = json.loads(model.get('endpoints', '{}'))
            return model
        
        return None
    
    async def use_model(self, model_id: str, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        استفاده از یک مدل ثبت شده
        
        Args:
            model_id: شناسه مدل
            endpoint: endpoint مورد نظر
            payload: داده‌های ورودی
        
        Returns:
            خروجی مدل
        """
        model = self.get_model(model_id)
        
        if not model:
            return {
                'success': False,
                'error': f'Model not found: {model_id}'
            }
        
        # Update usage count
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE dynamic_models
            SET use_count = use_count + 1, last_used_at = CURRENT_TIMESTAMP
            WHERE model_id = ?
        ''', (model_id,))
        conn.commit()
        conn.close()
        
        # Prepare request
        api_type = model['api_type']
        base_url = model['base_url']
        api_key = model['api_key']
        
        headers = {'Content-Type': 'application/json'}
        if api_key:
            if api_type == 'huggingface':
                headers['Authorization'] = f'Bearer {api_key}'
            elif api_type == 'openai':
                headers['Authorization'] = f'Bearer {api_key}'
            else:
                headers['Authorization'] = api_key
        
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        start_time = datetime.now()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                # Log usage
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO model_usage_history
                    (model_id, endpoint_used, response_time_ms, success)
                    VALUES (?, ?, ?, ?)
                ''', (model_id, endpoint, response_time, response.status_code == 200))
                conn.commit()
                conn.close()
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'data': response.json(),
                        'response_time_ms': response_time
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}: {response.text[:200]}'
                    }
        
        except Exception as e:
            logger.error(f"❌ Model usage failed: {e}")
            
            # Log error
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO model_usage_history
                (model_id, endpoint_used, success, error_message)
                VALUES (?, ?, ?, ?)
            ''', (model_id, endpoint, False, str(e)))
            conn.commit()
            conn.close()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_model(self, model_id: str) -> bool:
        """حذف یک مدل"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE dynamic_models
            SET is_active = 0
            WHERE model_id = ?
        ''', (model_id,))
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0


# Global instance
dynamic_loader = DynamicModelLoader()

__all__ = ['DynamicModelLoader', 'dynamic_loader']

