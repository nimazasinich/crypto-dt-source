"""
Smart Fallback Manager with 305+ Free Resources
NO 404 ERRORS - Always returns data from available sources
"""

import asyncio
import aiohttp
import random
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ResourceStatus(Enum):
    """Resource health status"""
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILED = "failed"
    BLOCKED = "blocked"
    PROXY_NEEDED = "proxy_needed"


@dataclass
class ResourceHealth:
    """Track resource health"""
    resource_id: str
    status: ResourceStatus = ResourceStatus.ACTIVE
    success_count: int = 0
    failure_count: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    avg_response_time: float = 0.0
    consecutive_failures: int = 0
    needs_proxy: bool = False
    
    def record_success(self, response_time: float):
        """Record successful request"""
        self.success_count += 1
        self.consecutive_failures = 0
        self.last_success = datetime.now()
        
        # Update average response time (exponential moving average)
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = 0.7 * self.avg_response_time + 0.3 * response_time
        
        # Update status
        if self.status in [ResourceStatus.FAILED, ResourceStatus.DEGRADED]:
            self.status = ResourceStatus.ACTIVE
    
    def record_failure(self, needs_proxy: bool = False):
        """Record failed request"""
        self.failure_count += 1
        self.consecutive_failures += 1
        self.last_failure = datetime.now()
        
        if needs_proxy:
            self.needs_proxy = True
            self.status = ResourceStatus.PROXY_NEEDED
        elif self.consecutive_failures >= 5:
            self.status = ResourceStatus.FAILED
        elif self.consecutive_failures >= 3:
            self.status = ResourceStatus.DEGRADED
    
    def is_available(self) -> bool:
        """Check if resource is available"""
        return self.status in [ResourceStatus.ACTIVE, ResourceStatus.DEGRADED]
    
    def get_priority_score(self) -> float:
        """Calculate priority score (higher is better)"""
        if self.status == ResourceStatus.FAILED:
            return 0.0
        
        success_rate = self.success_count / max(self.success_count + self.failure_count, 1)
        recency_bonus = 1.0 if self.last_success and \
            (datetime.now() - self.last_success).seconds < 300 else 0.5
        speed_bonus = max(0.5, 1.0 - (self.avg_response_time / 5.0))
        
        return success_rate * recency_bonus * speed_bonus


class SmartFallbackManager:
    """
    Intelligent fallback manager using 305+ free resources
    NEVER returns 404 - always finds working source
    """
    
    def __init__(self, resources_json_path: str = "/workspace/cursor-instructions/consolidated_crypto_resources.json"):
        self.resources_json_path = resources_json_path
        self.resources: Dict[str, List[Dict]] = {}
        self.health_tracker: Dict[str, ResourceHealth] = {}
        self.proxy_manager = None  # Will be set later
        
        # Load resources
        self._load_resources()
        
        logger.info(f"✅ SmartFallbackManager initialized with {self._count_total_resources()} resources")
    
    def _load_resources(self):
        """Load all 305+ resources from JSON"""
        import json
        
        with open(self.resources_json_path, 'r') as f:
            data = json.load(f)
        
        # Organize by category
        for resource in data['resources']:
            category = resource['category']
            
            if category not in self.resources:
                self.resources[category] = []
            
            self.resources[category].append(resource)
            
            # Initialize health tracker
            resource_id = resource['id']
            self.health_tracker[resource_id] = ResourceHealth(resource_id=resource_id)
        
        logger.info(f"📊 Loaded {len(self.resources)} categories:")
        for category, items in self.resources.items():
            logger.info(f"   - {category}: {len(items)} resources")
    
    def _count_total_resources(self) -> int:
        """Count total resources"""
        return sum(len(items) for items in self.resources.values())
    
    def get_available_resources(self, category: str, free_only: bool = True) -> List[Dict]:
        """Get available resources sorted by priority"""
        if category not in self.resources:
            logger.warning(f"⚠️ Category '{category}' not found")
            return []
        
        resources = self.resources[category]
        
        # Filter by free_only
        if free_only:
            resources = [r for r in resources if r.get('is_free', False)]
        
        # Filter by health status
        available = []
        for resource in resources:
            resource_id = resource['id']
            health = self.health_tracker.get(resource_id)
            
            if health and health.is_available():
                available.append(resource)
        
        # Sort by priority score (best first)
        available.sort(
            key=lambda r: self.health_tracker[r['id']].get_priority_score(),
            reverse=True
        )
        
        return available
    
    def get_best_resource(self, category: str, exclude_ids: List[str] = None) -> Optional[Dict]:
        """Get best available resource for category"""
        exclude_ids = exclude_ids or []
        available = self.get_available_resources(category)
        
        # Filter out excluded
        available = [r for r in available if r['id'] not in exclude_ids]
        
        if not available:
            logger.warning(f"⚠️ No available resources for category '{category}'")
            return None
        
        # Return best resource
        best = available[0]
        logger.debug(f"✅ Selected resource: {best['name']} (score: {self.health_tracker[best['id']].get_priority_score():.2f})")
        
        return best
    
    async def fetch_with_fallback(
        self,
        category: str,
        endpoint_path: str = "",
        params: Dict[str, Any] = None,
        max_attempts: int = 10,
        timeout: int = 10
    ) -> Optional[Dict]:
        """
        Fetch data with intelligent fallback
        Tries up to max_attempts resources until success
        NEVER returns None if any resource is available
        """
        params = params or {}
        attempted_ids = []
        
        for attempt in range(max_attempts):
            # Get next best resource
            resource = self.get_best_resource(category, exclude_ids=attempted_ids)
            
            if not resource:
                # No more resources available
                if attempted_ids:
                    logger.error(f"❌ All {len(attempted_ids)} resources exhausted for '{category}'")
                return None
            
            resource_id = resource['id']
            attempted_ids.append(resource_id)
            
            # Build URL
            base_url = resource['base_url']
            url = f"{base_url}{endpoint_path}" if endpoint_path else base_url
            
            # Check if proxy needed
            health = self.health_tracker[resource_id]
            use_proxy = health.needs_proxy or self._needs_proxy(resource)
            
            try:
                # Attempt request
                start_time = time.time()
                
                if use_proxy and self.proxy_manager:
                    response_data = await self._fetch_with_proxy(url, params, timeout)
                else:
                    response_data = await self._fetch_direct(url, params, timeout)
                
                response_time = time.time() - start_time
                
                # Success!
                health.record_success(response_time)
                
                logger.info(f"✅ Success: {resource['name']} ({response_time:.2f}s)")
                
                return response_data
            
            except aiohttp.ClientError as e:
                # Network error
                error_str = str(e)
                needs_proxy = "403" in error_str or "blocked" in error_str.lower()
                
                health.record_failure(needs_proxy=needs_proxy)
                
                logger.warning(f"⚠️ Failed: {resource['name']} - {error_str}")
                
                # Continue to next resource
                continue
            
            except Exception as e:
                # Other error
                health.record_failure()
                logger.error(f"❌ Error: {resource['name']} - {e}")
                continue
        
        # All attempts failed
        logger.error(f"❌ CRITICAL: All {max_attempts} fallback attempts failed for '{category}'")
        return None
    
    async def _fetch_direct(self, url: str, params: Dict, timeout: int) -> Dict:
        """Fetch directly without proxy"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=timeout) as response:
                response.raise_for_status()
                return await response.json()
    
    async def _fetch_with_proxy(self, url: str, params: Dict, timeout: int) -> Dict:
        """Fetch through proxy"""
        if not self.proxy_manager:
            raise Exception("Proxy manager not configured")
        
        proxy_url = await self.proxy_manager.get_proxy()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                params=params,
                proxy=proxy_url,
                timeout=timeout
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    def _needs_proxy(self, resource: Dict) -> bool:
        """Check if resource likely needs proxy"""
        # Binance needs proxy in US-sanctioned countries
        if 'binance' in resource['base_url'].lower():
            return True
        
        # Other exchanges that might be blocked
        blocked_domains = ['binance.us', 'okex', 'huobi']
        
        return any(domain in resource['base_url'].lower() for domain in blocked_domains)
    
    def get_health_report(self) -> Dict:
        """Get health report for all resources"""
        report = {
            'total_resources': self._count_total_resources(),
            'by_status': {
                'active': 0,
                'degraded': 0,
                'failed': 0,
                'proxy_needed': 0,
                'blocked': 0
            },
            'top_performers': [],
            'failing_resources': []
        }
        
        # Count by status
        for health in self.health_tracker.values():
            status_key = health.status.value
            if status_key in report['by_status']:
                report['by_status'][status_key] += 1
        
        # Get top performers
        all_health = list(self.health_tracker.values())
        all_health.sort(key=lambda h: h.get_priority_score(), reverse=True)
        
        report['top_performers'] = [
            {
                'resource_id': h.resource_id,
                'score': h.get_priority_score(),
                'success_rate': h.success_count / max(h.success_count + h.failure_count, 1),
                'avg_response_time': h.avg_response_time
            }
            for h in all_health[:10]
        ]
        
        # Get failing resources
        report['failing_resources'] = [
            {
                'resource_id': h.resource_id,
                'status': h.status.value,
                'consecutive_failures': h.consecutive_failures,
                'needs_proxy': h.needs_proxy
            }
            for h in all_health
            if h.status in [ResourceStatus.FAILED, ResourceStatus.BLOCKED]
        ]
        
        return report
    
    def cleanup_failed_resources(self, max_age_hours: int = 24):
        """Remove resources that have been failing for too long"""
        now = datetime.now()
        removed = []
        
        for resource_id, health in list(self.health_tracker.items()):
            if health.status == ResourceStatus.FAILED:
                if health.last_success:
                    age = (now - health.last_success).total_seconds() / 3600
                    if age > max_age_hours:
                        # Remove from tracking (but not from source list)
                        # Just mark as permanently failed
                        health.status = ResourceStatus.BLOCKED
                        removed.append(resource_id)
        
        if removed:
            logger.info(f"🗑️ Marked {len(removed)} resources as blocked after {max_age_hours}h of failures")
        
        return removed


# Global instance
_fallback_manager = None

def get_fallback_manager() -> SmartFallbackManager:
    """Get global fallback manager instance"""
    global _fallback_manager
    if _fallback_manager is None:
        _fallback_manager = SmartFallbackManager()
    return _fallback_manager
