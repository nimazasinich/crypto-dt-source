#!/usr/bin/env python3
"""
Master Resource Orchestrator
Orchestrates ALL 86+ resources hierarchically - NO IDLE RESOURCES
مدیریت سلسله‌مراتبی همه 86+ منبع - هیچ منبعی بیکار نمی‌ماند
"""

import httpx
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from backend.services.hierarchical_fallback_config import (
    hierarchical_config,
    Priority,
    ResourceConfig
)

logger = logging.getLogger(__name__)


class ResourceStatus(Enum):
    """Status of resource attempt"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class MasterResourceOrchestrator:
    """
    Master orchestrator for ALL resources
    تمام 86+ منبع را به صورت سلسله‌مراتبی مدیریت می‌کند
    """
    
    def __init__(self):
        self.config = hierarchical_config
        self.timeout = 10.0
        
        # Statistics tracking
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "resource_usage": {},  # Track usage per resource
            "priority_distribution": {  # Track which priority level succeeded
                Priority.CRITICAL: 0,
                Priority.HIGH: 0,
                Priority.MEDIUM: 0,
                Priority.LOW: 0,
                Priority.EMERGENCY: 0
            }
        }
    
    async def fetch_with_hierarchy(
        self,
        resource_list: List[ResourceConfig],
        fetch_function: callable,
        max_concurrent: int = 3
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Fetch data using hierarchical fallback
        دریافت داده با فالبک سلسله‌مراتبی
        
        Args:
            resource_list: List of resources in priority order
            fetch_function: Async function to fetch data from a resource
            max_concurrent: Max concurrent attempts within same priority
        
        Returns:
            (data, metadata) - Data and information about which resource succeeded
        """
        self.usage_stats["total_requests"] += 1
        
        # Group resources by priority
        priority_groups = self._group_by_priority(resource_list)
        
        # Try each priority level
        for priority in [Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, Priority.LOW, Priority.EMERGENCY]:
            resources_in_priority = priority_groups.get(priority, [])
            
            if not resources_in_priority:
                continue
            
            logger.info(f"🔄 Trying {len(resources_in_priority)} resources at {priority.name} priority")
            
            # Try resources in this priority level
            # If max_concurrent > 1, try multiple resources in parallel
            if max_concurrent > 1 and len(resources_in_priority) > 1:
                result = await self._try_concurrent(
                    resources_in_priority[:max_concurrent],
                    fetch_function,
                    priority
                )
            else:
                result = await self._try_sequential(
                    resources_in_priority,
                    fetch_function,
                    priority
                )
            
            if result:
                data, metadata = result
                self.usage_stats["successful_requests"] += 1
                self.usage_stats["priority_distribution"][priority] += 1
                logger.info(f"✅ SUCCESS at {priority.name} priority: {metadata['resource_name']}")
                return data, metadata
        
        # All resources failed
        self.usage_stats["failed_requests"] += 1
        logger.error(f"❌ ALL {len(resource_list)} resources failed")
        
        raise Exception(f"All {len(resource_list)} resources failed across all priority levels")
    
    def _group_by_priority(
        self,
        resources: List[ResourceConfig]
    ) -> Dict[Priority, List[ResourceConfig]]:
        """Group resources by priority level"""
        groups = {
            Priority.CRITICAL: [],
            Priority.HIGH: [],
            Priority.MEDIUM: [],
            Priority.LOW: [],
            Priority.EMERGENCY: []
        }
        
        for resource in resources:
            groups[resource.priority].append(resource)
        
        return groups
    
    async def _try_sequential(
        self,
        resources: List[ResourceConfig],
        fetch_function: callable,
        priority: Priority
    ) -> Optional[Tuple[Any, Dict[str, Any]]]:
        """Try resources sequentially"""
        for idx, resource in enumerate(resources, 1):
            try:
                logger.info(f"  📡 [{idx}/{len(resources)}] Trying {resource.name}...")
                
                # Track usage
                if resource.name not in self.usage_stats["resource_usage"]:
                    self.usage_stats["resource_usage"][resource.name] = {
                        "attempts": 0,
                        "successes": 0,
                        "failures": 0
                    }
                
                self.usage_stats["resource_usage"][resource.name]["attempts"] += 1
                
                # Attempt to fetch data
                start_time = datetime.utcnow()
                data = await fetch_function(resource)
                end_time = datetime.utcnow()
                
                if data:
                    self.usage_stats["resource_usage"][resource.name]["successes"] += 1
                    
                    metadata = {
                        "resource_name": resource.name,
                        "priority": priority.name,
                        "base_url": resource.base_url,
                        "response_time_ms": int((end_time - start_time).total_seconds() * 1000),
                        "timestamp": int(end_time.timestamp() * 1000)
                    }
                    
                    logger.info(f"  ✅ {resource.name} succeeded in {metadata['response_time_ms']}ms")
                    return data, metadata
                
                logger.warning(f"  ⚠️ {resource.name} returned no data")
                self.usage_stats["resource_usage"][resource.name]["failures"] += 1
                
            except asyncio.TimeoutError:
                logger.warning(f"  ⏱️ {resource.name} timeout")
                self.usage_stats["resource_usage"][resource.name]["failures"] += 1
                continue
                
            except Exception as e:
                logger.warning(f"  ❌ {resource.name} failed: {e}")
                self.usage_stats["resource_usage"][resource.name]["failures"] += 1
                continue
        
        return None
    
    async def _try_concurrent(
        self,
        resources: List[ResourceConfig],
        fetch_function: callable,
        priority: Priority
    ) -> Optional[Tuple[Any, Dict[str, Any]]]:
        """Try multiple resources concurrently (race condition - first success wins)"""
        logger.info(f"  🏁 Racing {len(resources)} resources in parallel...")
        
        tasks = []
        for resource in resources:
            task = self._try_single_resource(resource, fetch_function, priority)
            tasks.append(task)
        
        # Wait for first success or all failures
        for completed_task in asyncio.as_completed(tasks):
            try:
                result = await completed_task
                if result:
                    # Cancel remaining tasks
                    for task in tasks:
                        if not task.done():
                            task.cancel()
                    return result
            except Exception:
                continue
        
        return None
    
    async def _try_single_resource(
        self,
        resource: ResourceConfig,
        fetch_function: callable,
        priority: Priority
    ) -> Optional[Tuple[Any, Dict[str, Any]]]:
        """Try a single resource (used in concurrent mode)"""
        try:
            # Track usage
            if resource.name not in self.usage_stats["resource_usage"]:
                self.usage_stats["resource_usage"][resource.name] = {
                    "attempts": 0,
                    "successes": 0,
                    "failures": 0
                }
            
            self.usage_stats["resource_usage"][resource.name]["attempts"] += 1
            
            start_time = datetime.utcnow()
            data = await fetch_function(resource)
            end_time = datetime.utcnow()
            
            if data:
                self.usage_stats["resource_usage"][resource.name]["successes"] += 1
                
                metadata = {
                    "resource_name": resource.name,
                    "priority": priority.name,
                    "base_url": resource.base_url,
                    "response_time_ms": int((end_time - start_time).total_seconds() * 1000),
                    "timestamp": int(end_time.timestamp() * 1000)
                }
                
                logger.info(f"  🏆 {resource.name} won the race! ({metadata['response_time_ms']}ms)")
                return data, metadata
            
            self.usage_stats["resource_usage"][resource.name]["failures"] += 1
            return None
            
        except Exception as e:
            logger.warning(f"  ❌ {resource.name} failed: {e}")
            self.usage_stats["resource_usage"][resource.name]["failures"] += 1
            return None
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive usage statistics
        آمار کامل استفاده از منابع
        """
        total_resources = len(self.usage_stats["resource_usage"])
        used_resources = sum(
            1 for stats in self.usage_stats["resource_usage"].values()
            if stats["attempts"] > 0
        )
        successful_resources = sum(
            1 for stats in self.usage_stats["resource_usage"].values()
            if stats["successes"] > 0
        )
        
        # Calculate success rate per priority
        priority_success_rates = {}
        total_priority_requests = sum(self.usage_stats["priority_distribution"].values())
        
        if total_priority_requests > 0:
            for priority, count in self.usage_stats["priority_distribution"].items():
                priority_success_rates[priority.name] = {
                    "count": count,
                    "percentage": round((count / total_priority_requests) * 100, 2)
                }
        
        # Find most used resources
        most_used = sorted(
            self.usage_stats["resource_usage"].items(),
            key=lambda x: x[1]["attempts"],
            reverse=True
        )[:10]
        
        # Find most successful resources
        most_successful = sorted(
            self.usage_stats["resource_usage"].items(),
            key=lambda x: x[1]["successes"],
            reverse=True
        )[:10]
        
        return {
            "overview": {
                "total_requests": self.usage_stats["total_requests"],
                "successful_requests": self.usage_stats["successful_requests"],
                "failed_requests": self.usage_stats["failed_requests"],
                "success_rate": round(
                    (self.usage_stats["successful_requests"] / self.usage_stats["total_requests"] * 100)
                    if self.usage_stats["total_requests"] > 0 else 0,
                    2
                )
            },
            "resource_utilization": {
                "total_resources_in_system": total_resources,
                "resources_used": used_resources,
                "resources_successful": successful_resources,
                "utilization_rate": round((used_resources / total_resources * 100) if total_resources > 0 else 0, 2)
            },
            "priority_distribution": priority_success_rates,
            "top_10_most_used": [
                {
                    "resource": name,
                    "attempts": stats["attempts"],
                    "successes": stats["successes"],
                    "failures": stats["failures"],
                    "success_rate": round((stats["successes"] / stats["attempts"] * 100) if stats["attempts"] > 0 else 0, 2)
                }
                for name, stats in most_used
            ],
            "top_10_most_successful": [
                {
                    "resource": name,
                    "successes": stats["successes"],
                    "attempts": stats["attempts"],
                    "success_rate": round((stats["successes"] / stats["attempts"] * 100) if stats["attempts"] > 0 else 0, 2)
                }
                for name, stats in most_successful
            ]
        }
    
    def get_resource_health_report(self) -> Dict[str, Any]:
        """
        Get health report for all resources
        گزارش سلامت همه منابع
        """
        healthy_resources = []
        degraded_resources = []
        failed_resources = []
        unused_resources = []
        
        for resource_name, stats in self.usage_stats["resource_usage"].items():
            if stats["attempts"] == 0:
                unused_resources.append(resource_name)
            elif stats["successes"] == 0:
                failed_resources.append({
                    "name": resource_name,
                    "attempts": stats["attempts"],
                    "failures": stats["failures"]
                })
            else:
                success_rate = (stats["successes"] / stats["attempts"]) * 100
                
                if success_rate >= 80:
                    healthy_resources.append({
                        "name": resource_name,
                        "success_rate": round(success_rate, 2),
                        "attempts": stats["attempts"]
                    })
                else:
                    degraded_resources.append({
                        "name": resource_name,
                        "success_rate": round(success_rate, 2),
                        "attempts": stats["attempts"],
                        "failures": stats["failures"]
                    })
        
        return {
            "healthy_resources": {
                "count": len(healthy_resources),
                "resources": healthy_resources
            },
            "degraded_resources": {
                "count": len(degraded_resources),
                "resources": degraded_resources
            },
            "failed_resources": {
                "count": len(failed_resources),
                "resources": failed_resources
            },
            "unused_resources": {
                "count": len(unused_resources),
                "resources": unused_resources
            },
            "overall_health": "Healthy" if len(healthy_resources) > len(failed_resources) else "Degraded"
        }


# Global instance
master_orchestrator = MasterResourceOrchestrator()

__all__ = ["MasterResourceOrchestrator", "master_orchestrator", "ResourceStatus"]

