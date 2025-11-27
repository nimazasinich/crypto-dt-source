"""
Crypto API Hub Backend Service
Handles all API requests for the Crypto API Hub Dashboard
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
from fastapi import HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class APIRequest(BaseModel):
    """Model for API proxy requests"""
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = None


class CryptoAPIHubService:
    """Service for managing Crypto API Hub operations"""

    def __init__(self):
        self.services_file = Path(__file__).parent / "crypto_api_hub_services.json"
        self.services = self._load_services()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Crypto-API-Hub/1.0'
        })

    def _load_services(self) -> Dict[str, Any]:
        """Load services from JSON file"""
        try:
            if self.services_file.exists():
                with open(self.services_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data.get('services', {}))} service categories")
                    return data
            else:
                logger.warning(f"Services file not found: {self.services_file}")
                return self._get_default_services()
        except Exception as e:
            logger.error(f"Error loading services: {e}")
            return self._get_default_services()

    def _get_default_services(self) -> Dict[str, Any]:
        """Return default services structure"""
        return {
            "metadata": {
                "version": "1.0.0",
                "last_updated": "2025-11-27",
                "total_services": 74,
                "total_categories": 5
            },
            "services": {
                "explorer": [],
                "market": [],
                "news": [],
                "sentiment": [],
                "analytics": []
            }
        }

    async def get_services(self) -> Dict[str, Any]:
        """Get all services"""
        return self.services

    async def get_services_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get services by category"""
        services = self.services.get("services", {})
        return services.get(category, [])

    async def search_services(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Search services by name, URL, or category"""
        query_lower = query.lower()
        results = {}

        for category, services in self.services.get("services", {}).items():
            filtered = [
                service for service in services
                if query_lower in service.get("name", "").lower()
                or query_lower in service.get("url", "").lower()
                or query_lower in category.lower()
            ]
            if filtered:
                results[category] = filtered

        return results

    async def test_endpoint(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Test an API endpoint through a proxy to avoid CORS issues
        """
        try:
            # Prepare request
            request_headers = headers or {}
            request_body = None

            if body and (method in ["POST", "PUT"]):
                try:
                    request_body = json.loads(body) if isinstance(body, str) else body
                except json.JSONDecodeError:
                    request_body = body

            # Make request
            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                json=request_body if isinstance(request_body, dict) else None,
                data=request_body if isinstance(request_body, str) else None,
                timeout=30,
                allow_redirects=True
            )

            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {
                    "text": response.text,
                    "status_code": response.status_code
                }

            return {
                "success": True,
                "status_code": response.status_code,
                "data": response_data,
                "headers": dict(response.headers)
            }

        except requests.Timeout:
            logger.error(f"Timeout testing endpoint: {url}")
            return {
                "success": False,
                "error": "Request timeout",
                "details": f"The request to {url} timed out after 30 seconds"
            }

        except requests.RequestException as e:
            logger.error(f"HTTP error testing endpoint {url}: {e}")
            return {
                "success": False,
                "error": "HTTP error",
                "details": str(e)
            }

        except Exception as e:
            logger.error(f"Error testing endpoint {url}: {e}")
            return {
                "success": False,
                "error": "Unexpected error",
                "details": str(e)
            }

    async def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics about all services"""
        services = self.services.get("services", {})

        total_services = sum(len(svc_list) for svc_list in services.values())
        total_endpoints = 0
        total_keys = 0

        for category_services in services.values():
            for service in category_services:
                total_endpoints += len(service.get("endpoints", []))
                if service.get("key"):
                    total_keys += 1

        category_stats = {
            category: len(svc_list)
            for category, svc_list in services.items()
        }

        return {
            "total_services": total_services,
            "total_endpoints": total_endpoints,
            "total_keys": total_keys,
            "categories": category_stats,
            "metadata": self.services.get("metadata", {})
        }

    async def validate_service(self, service_name: str) -> Dict[str, Any]:
        """
        Validate a service by testing its endpoints
        """
        services = self.services.get("services", {})

        # Find the service
        found_service = None
        found_category = None

        for category, category_services in services.items():
            for service in category_services:
                if service.get("name", "").lower() == service_name.lower():
                    found_service = service
                    found_category = category
                    break
            if found_service:
                break

        if not found_service:
            raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

        # Test endpoints
        results = []
        base_url = found_service.get("url", "")
        api_key = found_service.get("key", "")

        for endpoint in found_service.get("endpoints", [])[:3]:  # Test first 3 endpoints
            full_url = base_url + endpoint
            if api_key:
                full_url = full_url.replace("{KEY}", api_key).replace("{key}", api_key)

            # Replace placeholder addresses with test addresses
            full_url = full_url.replace("{address}", "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb")

            test_result = await self.test_endpoint(full_url)
            results.append({
                "endpoint": endpoint,
                "full_url": full_url,
                "result": test_result
            })

        return {
            "service": found_service.get("name"),
            "category": found_category,
            "url": base_url,
            "has_key": bool(api_key),
            "total_endpoints": len(found_service.get("endpoints", [])),
            "tested_endpoints": len(results),
            "test_results": results
        }

    async def close(self):
        """Close HTTP session"""
        self.session.close()


# Global instance
crypto_hub_service = CryptoAPIHubService()
