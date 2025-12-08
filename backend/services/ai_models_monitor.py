#!/usr/bin/env python3
"""
AI Models Monitor & Database Manager
سیستم نظارت و مدیریت دیتابیس مدل‌های AI

Features:
- شناسایی تمام مدل‌های AI از Hugging Face
- تست عملکرد هر مدل
- جمع‌آوری metrics (latency, success rate, etc.)
- ذخیره در دیتابیس
- Agent خودکار برای بررسی هر 5 دقیقه
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import httpx
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)


class AIModelsDatabase:
    """
    مدیریت دیتابیس مدل‌های AI
    """
    
    def __init__(self, db_path: str = "data/ai_models.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """ایجاد جداول دیتابیس"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول مدل‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id TEXT UNIQUE NOT NULL,
                model_key TEXT,
                task TEXT,
                category TEXT,
                provider TEXT DEFAULT 'huggingface',
                requires_auth BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول metrics (عملکرد مدل‌ها)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id TEXT NOT NULL,
                status TEXT,  -- 'available', 'loading', 'failed', 'auth_required'
                response_time_ms REAL,
                success BOOLEAN,
                error_message TEXT,
                test_input TEXT,
                test_output TEXT,
                confidence REAL,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES ai_models(model_id)
            )
        ''')
        
        # جدول آمار کلی
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_stats (
                model_id TEXT PRIMARY KEY,
                total_checks INTEGER DEFAULT 0,
                successful_checks INTEGER DEFAULT 0,
                failed_checks INTEGER DEFAULT 0,
                avg_response_time_ms REAL,
                last_success_at TIMESTAMP,
                last_failure_at TIMESTAMP,
                success_rate REAL,
                FOREIGN KEY (model_id) REFERENCES ai_models(model_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Database initialized: {self.db_path}")
    
    def add_model(self, model_info: Dict[str, Any]):
        """اضافه کردن یا بروزرسانی مدل"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO ai_models 
            (model_id, model_key, task, category, provider, requires_auth, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            model_info['model_id'],
            model_info.get('model_key'),
            model_info.get('task'),
            model_info.get('category'),
            model_info.get('provider', 'huggingface'),
            model_info.get('requires_auth', False)
        ))
        
        conn.commit()
        conn.close()
    
    def save_metric(self, metric: Dict[str, Any]):
        """ذخیره metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO model_metrics 
            (model_id, status, response_time_ms, success, error_message, 
             test_input, test_output, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metric['model_id'],
            metric.get('status'),
            metric.get('response_time_ms'),
            metric.get('success', False),
            metric.get('error_message'),
            metric.get('test_input'),
            json.dumps(metric.get('test_output')),
            metric.get('confidence')
        ))
        
        # بروزرسانی آمار کلی
        self._update_model_stats(cursor, metric['model_id'], metric.get('success', False))
        
        conn.commit()
        conn.close()
    
    def _update_model_stats(self, cursor, model_id: str, success: bool):
        """بروزرسانی آمار مدل"""
        # دریافت آمار فعلی
        cursor.execute('''
            SELECT total_checks, successful_checks, failed_checks, avg_response_time_ms
            FROM model_stats WHERE model_id = ?
        ''', (model_id,))
        
        row = cursor.fetchone()
        
        if row:
            total, successful, failed, avg_time = row
            total += 1
            successful += 1 if success else 0
            failed += 0 if success else 1
            
            # محاسبه میانگین زمان پاسخ جدید
            cursor.execute('''
                SELECT AVG(response_time_ms) FROM model_metrics 
                WHERE model_id = ? AND success = 1
            ''', (model_id,))
            avg_time = cursor.fetchone()[0] or 0
            
            success_rate = (successful / total * 100) if total > 0 else 0
            
            cursor.execute('''
                UPDATE model_stats SET
                    total_checks = ?,
                    successful_checks = ?,
                    failed_checks = ?,
                    avg_response_time_ms = ?,
                    success_rate = ?,
                    last_success_at = CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE last_success_at END,
                    last_failure_at = CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE last_failure_at END
                WHERE model_id = ?
            ''', (total, successful, failed, avg_time, success_rate, 
                  success, not success, model_id))
        else:
            # ایجاد رکورد جدید
            cursor.execute('''
                INSERT INTO model_stats 
                (model_id, total_checks, successful_checks, failed_checks, 
                 success_rate, last_success_at, last_failure_at)
                VALUES (?, 1, ?, ?, ?, 
                        CASE WHEN ? THEN CURRENT_TIMESTAMP END,
                        CASE WHEN ? THEN CURRENT_TIMESTAMP END)
            ''', (model_id, 
                  1 if success else 0,
                  0 if success else 1,
                  100.0 if success else 0.0,
                  success, not success))
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """دریافت همه مدل‌ها"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.*, s.total_checks, s.successful_checks, s.success_rate, s.avg_response_time_ms
            FROM ai_models m
            LEFT JOIN model_stats s ON m.model_id = s.model_id
            WHERE m.is_active = 1
        ''')
        
        models = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return models
    
    def get_model_history(self, model_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """دریافت تاریخچه مدل"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM model_metrics 
            WHERE model_id = ?
            ORDER BY checked_at DESC
            LIMIT ?
        ''', (model_id, limit))
        
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return history


class AIModelsMonitor:
    """
    مانیتور مدل‌های AI
    شناسایی، تست، و نظارت بر همه مدل‌ها
    """
    
    def __init__(self, db: AIModelsDatabase):
        self.db = db
        import os
        self.hf_api_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        # استفاده از router endpoint جدید
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # مدل‌های شناخته شده (از کدهای موجود)
        self.known_models = self._load_known_models()
    
    def _load_known_models(self) -> List[Dict[str, Any]]:
        """بارگذاری مدل‌های شناخته شده"""
        models = []
        
        # از real_ai_models.py
        sentiment_models = [
            {"model_id": "ElKulako/cryptobert", "task": "sentiment-analysis", "category": "crypto", "requires_auth": True},
            {"model_id": "kk08/CryptoBERT", "task": "sentiment-analysis", "category": "crypto"},
            {"model_id": "ProsusAI/finbert", "task": "sentiment-analysis", "category": "financial"},
            {"model_id": "cardiffnlp/twitter-roberta-base-sentiment-latest", "task": "sentiment-analysis", "category": "twitter"},
            {"model_id": "StephanAkkerman/FinTwitBERT-sentiment", "task": "sentiment-analysis", "category": "financial"},
            {"model_id": "finiteautomata/bertweet-base-sentiment-analysis", "task": "sentiment-analysis", "category": "twitter"},
            {"model_id": "yiyanghkust/finbert-tone", "task": "sentiment-analysis", "category": "financial"},
            {"model_id": "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis", "task": "sentiment-analysis", "category": "news"},
            {"model_id": "distilbert-base-uncased-finetuned-sst-2-english", "task": "sentiment-analysis", "category": "general"},
            {"model_id": "nlptown/bert-base-multilingual-uncased-sentiment", "task": "sentiment-analysis", "category": "general"},
            {"model_id": "mayurjadhav/crypto-sentiment-model", "task": "sentiment-analysis", "category": "crypto"},
            {"model_id": "mathugo/crypto_news_bert", "task": "sentiment-analysis", "category": "crypto_news"},
            {"model_id": "burakutf/finetuned-finbert-crypto", "task": "sentiment-analysis", "category": "crypto"},
        ]
        
        generation_models = [
            {"model_id": "OpenC/crypto-gpt-o3-mini", "task": "text-generation", "category": "crypto"},
            {"model_id": "agarkovv/CryptoTrader-LM", "task": "text-generation", "category": "trading"},
            {"model_id": "gpt2", "task": "text-generation", "category": "general"},
            {"model_id": "distilgpt2", "task": "text-generation", "category": "general"},
        ]
        
        summarization_models = [
            {"model_id": "facebook/bart-large-cnn", "task": "summarization", "category": "news"},
            {"model_id": "sshleifer/distilbart-cnn-12-6", "task": "summarization", "category": "news"},
            {"model_id": "FurkanGozukara/Crypto-Financial-News-Summarizer", "task": "summarization", "category": "crypto_news"},
        ]
        
        zero_shot_models = [
            {"model_id": "facebook/bart-large-mnli", "task": "zero-shot-classification", "category": "general"},
        ]
        
        models.extend(sentiment_models)
        models.extend(generation_models)
        models.extend(summarization_models)
        models.extend(zero_shot_models)
        
        return models
    
    async def test_model(self, model_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        تست یک مدل
        
        Returns:
            Dict با اطلاعات کامل نتیجه تست
        """
        model_id = model_info['model_id']
        task = model_info.get('task', 'sentiment-analysis')
        
        # متن تست بر اساس task
        test_inputs = {
            'sentiment-analysis': "Bitcoin is showing strong bullish momentum!",
            'text-generation': "The future of cryptocurrency is",
            'summarization': "Bitcoin reached new all-time highs today as institutional investors continue to show strong interest in cryptocurrency markets. Analysts predict further growth in the coming months.",
            'zero-shot-classification': "Bitcoin price surging",
        }
        
        test_input = test_inputs.get(task, "Test input")
        
        url = f"{self.base_url}/{model_id}"
        headers = {"Content-Type": "application/json"}
        
        if self.hf_api_token:
            headers["Authorization"] = f"Bearer {self.hf_api_token}"
        
        # Payload بر اساس task
        if task == 'zero-shot-classification':
            payload = {
                "inputs": test_input,
                "parameters": {"candidate_labels": ["bullish", "bearish", "neutral"]}
            }
        else:
            payload = {"inputs": test_input}
        
        start_time = datetime.now()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000  # ms
                
                result = {
                    'model_id': model_id,
                    'task': task,
                    'category': model_info.get('category'),
                    'test_input': test_input,
                    'response_time_ms': response_time,
                    'http_status': response.status_code
                }
                
                if response.status_code == 200:
                    data = response.json()
                    result['status'] = 'available'
                    result['success'] = True
                    result['test_output'] = data
                    
                    # استخراج confidence
                    if isinstance(data, list) and len(data) > 0:
                        if isinstance(data[0], dict):
                            result['confidence'] = data[0].get('score', 0.0)
                        elif isinstance(data[0], list) and len(data[0]) > 0:
                            result['confidence'] = data[0][0].get('score', 0.0)
                    
                    logger.info(f"✅ {model_id}: {response_time:.0f}ms")
                
                elif response.status_code == 503:
                    result['status'] = 'loading'
                    result['success'] = False
                    result['error_message'] = "Model is loading"
                    logger.warning(f"⏳ {model_id}: Loading...")
                
                elif response.status_code == 401:
                    result['status'] = 'auth_required'
                    result['success'] = False
                    result['error_message'] = "Authentication required"
                    logger.warning(f"🔐 {model_id}: Auth required")
                
                elif response.status_code == 404:
                    result['status'] = 'not_found'
                    result['success'] = False
                    result['error_message'] = "Model not found"
                    logger.error(f"❌ {model_id}: Not found")
                
                else:
                    result['status'] = 'failed'
                    result['success'] = False
                    result['error_message'] = f"HTTP {response.status_code}"
                    logger.error(f"❌ {model_id}: HTTP {response.status_code}")
                
                return result
        
        except asyncio.TimeoutError:
            return {
                'model_id': model_id,
                'task': task,
                'category': model_info.get('category'),
                'status': 'timeout',
                'success': False,
                'error_message': "Request timeout (30s)",
                'test_input': test_input
            }
        
        except Exception as e:
            return {
                'model_id': model_id,
                'task': task,
                'category': model_info.get('category'),
                'status': 'error',
                'success': False,
                'error_message': str(e)[:200],
                'test_input': test_input
            }
    
    async def scan_all_models(self) -> Dict[str, Any]:
        """
        اسکن همه مدل‌ها
        """
        logger.info(f"🔍 Starting scan of {len(self.known_models)} models...")
        
        # اضافه کردن مدل‌ها به دیتابیس
        for model_info in self.known_models:
            self.db.add_model(model_info)
        
        # تست همه مدل‌ها
        tasks = [self.test_model(model_info) for model_info in self.known_models]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # پردازش نتایج
        summary = {
            'total': len(results),
            'available': 0,
            'loading': 0,
            'failed': 0,
            'auth_required': 0,
            'not_found': 0,
            'models': []
        }
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Exception: {result}")
                continue
            
            # ذخیره در دیتابیس
            self.db.save_metric(result)
            
            # آمار
            status = result.get('status', 'unknown')
            if status == 'available':
                summary['available'] += 1
            elif status == 'loading':
                summary['loading'] += 1
            elif status == 'auth_required':
                summary['auth_required'] += 1
            elif status == 'not_found':
                summary['not_found'] += 1
            else:
                summary['failed'] += 1
            
            summary['models'].append({
                'model_id': result['model_id'],
                'status': status,
                'response_time_ms': result.get('response_time_ms'),
                'success': result.get('success', False)
            })
        
        logger.info(f"✅ Scan complete: {summary['available']}/{summary['total']} available")
        
        return summary
    
    def get_models_by_status(self, status: str = None) -> List[Dict[str, Any]]:
        """دریافت مدل‌ها بر اساس وضعیت"""
        models = self.db.get_all_models()
        
        if status:
            # فیلتر بر اساس آخرین وضعیت
            filtered = []
            for model in models:
                history = self.db.get_model_history(model['model_id'], limit=1)
                if history and history[0]['status'] == status:
                    filtered.append(model)
            return filtered
        
        return models


class AIModelsAgent:
    """
    Agent خودکار برای نظارت مدل‌ها
    هر 5 دقیقه یکبار بررسی می‌کند
    """
    
    def __init__(self, monitor: AIModelsMonitor, interval_minutes: int = 5):
        self.monitor = monitor
        self.interval = interval_minutes * 60  # به ثانیه
        self.running = False
        self.task = None
    
    async def run(self):
        """اجرای Agent"""
        self.running = True
        logger.info(f"🤖 AI Models Agent started (interval: {self.interval/60:.0f} minutes)")
        
        while self.running:
            try:
                logger.info(f"🔄 Starting periodic scan...")
                result = await self.monitor.scan_all_models()
                
                logger.info(f"📊 Scan Results:")
                logger.info(f"   Available: {result['available']}")
                logger.info(f"   Loading: {result['loading']}")
                logger.info(f"   Failed: {result['failed']}")
                logger.info(f"   Auth Required: {result['auth_required']}")
                
                # صبر برای interval بعدی
                logger.info(f"⏰ Next scan in {self.interval/60:.0f} minutes...")
                await asyncio.sleep(self.interval)
            
            except Exception as e:
                logger.error(f"❌ Agent error: {e}")
                await asyncio.sleep(60)  # صبر 1 دقیقه در صورت خطا
    
    def start(self):
        """شروع Agent"""
        if not self.task:
            self.task = asyncio.create_task(self.run())
        return self.task
    
    async def stop(self):
        """توقف Agent"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 AI Models Agent stopped")


# Global instances
db = AIModelsDatabase()
monitor = AIModelsMonitor(db)
agent = AIModelsAgent(monitor, interval_minutes=5)


__all__ = ["AIModelsDatabase", "AIModelsMonitor", "AIModelsAgent", "db", "monitor", "agent"]

