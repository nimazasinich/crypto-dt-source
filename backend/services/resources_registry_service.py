#!/usr/bin/env python3
import asyncio
import httpx
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from unified_resource_loader import get_loader, APIResource


class ResourcesRegistryService:
    """
    Loads unified resources and provides:
    - Listing grouped by category
    - Smart rotation: probe candidates and pick the first healthy
    - Status caching with TTL
    - Accounts view: resources with configured auth vs missing
    """

    def __init__(self, ttl_seconds: int = 300):
        self.loader = get_loader()
        self.ttl = timedelta(seconds=ttl_seconds)
        self.status_cache: Dict[str, Dict[str, Any]] = {}

    def _cache_key(self, resource_id: str) -> str:
        return f"res_status::{resource_id}"

    def list_registry(self) -> Dict[str, Any]:
        stats = self.loader.get_stats()
        categories: Dict[str, Any] = {}
        for cat in self.loader.get_available_categories():
            items: List[APIResource] = self.loader.get_resources_by_category(cat)
            categories[cat] = [
                {
                    "id": r.id,
                    "name": r.name,
                    "base_url": r.base_url,
                    "requires_auth": r.requires_auth(),
                    "priority": r.priority
                }
                for r in items
            ]
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "stats": stats,
            "categories": categories,
        }

    def accounts_summary(self) -> Dict[str, Any]:
        configured: List[Dict[str, Any]] = []
        missing: List[Dict[str, Any]] = []
        for r in self.loader.resources.values():
            has_key = bool(r.api_key)
            target = configured if has_key else missing
            target.append({
                "id": r.id,
                "name": r.name,
                "category": r.category,
                "base_url": r.base_url,
                "requires_auth": r.requires_auth(),
                "priority": r.priority
            })
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "configured": configured,
            "missing": missing
        }

    async def probe(self, resource: APIResource, timeout: float = 5.0) -> Dict[str, Any]:
        """Probe a resource with a simple GET to base_url (best-effort)."""
        key = self._cache_key(resource.id)
        cached = self.status_cache.get(key)
        if cached and datetime.utcnow() - cached["checked_at"] < self.ttl:
            return cached

        params = resource.get_query_params()
        headers = resource.get_headers()
        url = resource.get_full_url()
        status = {
            "id": resource.id,
            "name": resource.name,
            "base_url": url,
            "category": resource.category,
            "requires_auth": resource.requires_auth(),
            "priority": resource.priority,
            "active": False,
            "status_code": None,
            "error": None,
            "checked_at": datetime.utcnow()
        }
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(url, headers=headers, params=params)
                status["status_code"] = resp.status_code
                status["active"] = 200 <= resp.status_code < 400
        except Exception as e:
            status["error"] = str(e)
            status["active"] = False

        self.status_cache[key] = status
        return status

    async def smart_rotate(self, category: str, limit: int = 10, prefer_free: bool = True) -> Dict[str, Any]:
        """Pick first healthy candidate by priority, preferring free resources."""
        candidates: List[APIResource] = self.loader.get_resources_by_category(category)
        if prefer_free:
            # Sort: free and priority asc
            candidates.sort(key=lambda r: (r.requires_auth(), r.priority))
        else:
            candidates.sort(key=lambda r: r.priority)

        results: List[Dict[str, Any]] = []
        chosen: Optional[Dict[str, Any]] = None
        for r in candidates[:limit]:
            st = await self.probe(r)
            results.append(st)
            if st.get("active") and not chosen:
                chosen = st

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "category": category,
            "chosen": chosen,
            "candidates": results
        }


# Singleton accessor
_svc: Optional[ResourcesRegistryService] = None

def get_resources_registry_service() -> ResourcesRegistryService:
    global _svc
    if _svc is None:
        _svc = ResourcesRegistryService(ttl_seconds=300)
    return _svc

