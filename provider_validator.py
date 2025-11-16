#!/usr/bin/env python3
"""
Provider Validator - Real HTTP validation for crypto API providers
Validates each provider by making actual HTTP calls and checking responses
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ValidationStatus(Enum):
    """Validation result status"""
    VALID = "valid"
    INVALID = "invalid"
    REQUIRES_AUTH = "requires_auth"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ValidationResult:
    """Result of provider validation"""
    provider_id: str
    status: ValidationStatus
    response_time_ms: Optional[float] = None
    http_status: Optional[int] = None
    error_message: Optional[str] = None
    test_endpoint: Optional[str] = None
    response_sample: Optional[Dict] = None
    validated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "provider_id": self.provider_id,
            "status": self.status.value,
            "response_time_ms": self.response_time_ms,
            "http_status": self.http_status,
            "error_message": self.error_message,
            "test_endpoint": self.test_endpoint,
            "response_sample": self.response_sample,
            "validated_at": self.validated_at.isoformat()
        }


class ProviderValidator:
    """
    Validates crypto API providers with real HTTP calls
    """
    
    def __init__(
        self,
        timeout: int = 10,
        max_concurrent: int = 5,
        user_agent: str = "CryptoProviderValidator/1.0"
    ):
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.user_agent = user_agent
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore: Optional[asyncio.Semaphore] = None
        
    async def init_session(self):
        """Initialize HTTP session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={"User-Agent": self.user_agent}
            )
        if not self.semaphore:
            self.semaphore = asyncio.Semaphore(self.max_concurrent)
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _select_test_endpoint(self, provider_data: Dict) -> Optional[Tuple[str, Dict]]:
        """
        Select the best endpoint to test for a provider
        Returns (endpoint_path, params_dict) or None
        """
        endpoints = provider_data.get('endpoints', {})
        
        if not endpoints:
            return None
        
        # Priority list of endpoint names (prefer simple GET endpoints)
        priority_names = [
            'ping', 'status', 'health', 'info',
            'global', 'stats', 'assets', 'tickers', 
            'coins', 'coins_list', 'protocols', 'chains',
            'simple_price', 'ticker_price', 'exchange_info',
            'feed', 'posts', 'fear_greed', 'fng'
        ]
        
        # Try priority endpoints first
        for name in priority_names:
            if name in endpoints:
                endpoint = endpoints[name]
                if isinstance(endpoint, str):
                    return (endpoint, {})
                elif isinstance(endpoint, dict):
                    return (endpoint.get('path', ''), endpoint.get('sampleParams', {}))
        
        # Otherwise use the first endpoint
        first_key = list(endpoints.keys())[0]
        first_endpoint = endpoints[first_key]
        
        if isinstance(first_endpoint, str):
            return (first_endpoint, {})
        elif isinstance(first_endpoint, dict):
            return (first_endpoint.get('path', ''), first_endpoint.get('sampleParams', {}))
        
        return None
    
    def _build_url(self, base_url: str, endpoint_path: str, params: Dict) -> str:
        """Build full URL with parameters"""
        # Clean base URL
        base_url = base_url.rstrip('/')
        endpoint_path = endpoint_path.lstrip('/')
        
        # Handle template variables in endpoint path (e.g., {id})
        # For now, just remove them or use default values
        endpoint_path = endpoint_path.replace('{id}', 'bitcoin')
        endpoint_path = endpoint_path.replace('{symbol}', 'BTCUSDT')
        endpoint_path = endpoint_path.replace('{address}', '0x0000000000000000000000000000000000000000')
        endpoint_path = endpoint_path.replace('{pair}', 'BTCUSD')
        endpoint_path = endpoint_path.replace('{ids}', 'bitcoin')
        endpoint_path = endpoint_path.replace('{currencies}', 'usd')
        endpoint_path = endpoint_path.replace('{fiats}', 'usd')
        endpoint_path = endpoint_path.replace('{coins}', 'ethereum:0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2')
        
        # Build URL
        url = f"{base_url}/{endpoint_path}"
        
        # Add query params if any
        if params:
            if '?' in url:
                separator = '&'
            else:
                separator = '?'
            
            param_strs = [f"{k}={v}" for k, v in params.items()]
            url += separator + '&'.join(param_strs)
        
        return url
    
    def _is_valid_json_response(self, data: Any) -> bool:
        """Check if response is valid JSON with data"""
        if data is None:
            return False
        
        if isinstance(data, dict):
            # Check for common error fields
            if 'error' in data and data['error']:
                return False
            # Must have some data
            return len(data) > 0
        
        if isinstance(data, list):
            return len(data) > 0
        
        # For other types (str, int, etc.), consider valid if not empty
        return data != "" and data != 0
    
    async def validate_provider(self, provider_id: str, provider_data: Dict) -> ValidationResult:
        """
        Validate a single provider by making a real HTTP call
        
        Args:
            provider_id: Unique provider identifier
            provider_data: Provider configuration dict with base_url, endpoints, etc.
        
        Returns:
            ValidationResult with status and details
        """
        await self.init_session()
        
        # Extract provider info
        base_url = provider_data.get('base_url')
        requires_auth = provider_data.get('requires_auth', False)
        
        if not base_url:
            return ValidationResult(
                provider_id=provider_id,
                status=ValidationStatus.INVALID,
                error_message="Missing base_url"
            )
        
        # Select test endpoint
        endpoint_info = self._select_test_endpoint(provider_data)
        if not endpoint_info:
            return ValidationResult(
                provider_id=provider_id,
                status=ValidationStatus.INVALID,
                error_message="No testable endpoints found"
            )
        
        endpoint_path, params = endpoint_info
        test_url = self._build_url(base_url, endpoint_path, params)
        
        # Prepare headers
        headers = {}
        
        # Add auth if available and required
        api_keys = provider_data.get('api_keys', [])
        auth_type = provider_data.get('auth_type', 'query')
        
        if api_keys and requires_auth:
            api_key = api_keys[0] if isinstance(api_keys, list) else api_keys
            
            if auth_type == 'header':
                auth_header = provider_data.get('auth_header', 'Authorization')
                headers[auth_header] = api_key
            elif auth_type == 'query':
                auth_param = provider_data.get('auth_param', 'apikey')
                separator = '&' if '?' in test_url else '?'
                test_url += f"{separator}{auth_param}={api_key}"
        
        # Make HTTP request with concurrency control
        async with self.semaphore:
            start_time = time.time()
            
            try:
                async with self.session.get(test_url, headers=headers, allow_redirects=True) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    # Check status code
                    if response.status == 401 or response.status == 403:
                        return ValidationResult(
                            provider_id=provider_id,
                            status=ValidationStatus.REQUIRES_AUTH,
                            http_status=response.status,
                            response_time_ms=response_time_ms,
                            test_endpoint=test_url,
                            error_message=f"Authentication required (HTTP {response.status})"
                        )
                    
                    if response.status == 429:
                        return ValidationResult(
                            provider_id=provider_id,
                            status=ValidationStatus.RATE_LIMITED,
                            http_status=response.status,
                            response_time_ms=response_time_ms,
                            test_endpoint=test_url,
                            error_message="Rate limit exceeded"
                        )
                    
                    if response.status != 200:
                        text = await response.text()
                        return ValidationResult(
                            provider_id=provider_id,
                            status=ValidationStatus.INVALID,
                            http_status=response.status,
                            response_time_ms=response_time_ms,
                            test_endpoint=test_url,
                            error_message=f"HTTP {response.status}: {text[:200]}"
                        )
                    
                    # Try to parse JSON
                    try:
                        data = await response.json()
                        
                        # Validate JSON structure
                        if not self._is_valid_json_response(data):
                            return ValidationResult(
                                provider_id=provider_id,
                                status=ValidationStatus.INVALID,
                                http_status=response.status,
                                response_time_ms=response_time_ms,
                                test_endpoint=test_url,
                                error_message="Invalid or empty JSON response"
                            )
                        
                        # Success!
                        # Sample response (truncate if too large)
                        sample = str(data)[:500] if data else None
                        
                        return ValidationResult(
                            provider_id=provider_id,
                            status=ValidationStatus.VALID,
                            http_status=response.status,
                            response_time_ms=response_time_ms,
                            test_endpoint=test_url,
                            response_sample={"preview": sample}
                        )
                    
                    except Exception as json_err:
                        # Not JSON, check if it's XML/RSS
                        text = await response.text()
                        
                        # If it's RSS/XML and looks valid, accept it
                        if 'xml' in response.headers.get('content-type', '').lower():
                            if '<rss' in text.lower() or '<feed' in text.lower():
                                return ValidationResult(
                                    provider_id=provider_id,
                                    status=ValidationStatus.VALID,
                                    http_status=response.status,
                                    response_time_ms=response_time_ms,
                                    test_endpoint=test_url,
                                    response_sample={"format": "xml/rss", "preview": text[:200]}
                                )
                        
                        return ValidationResult(
                            provider_id=provider_id,
                            status=ValidationStatus.INVALID,
                            http_status=response.status,
                            response_time_ms=response_time_ms,
                            test_endpoint=test_url,
                            error_message=f"Invalid JSON: {str(json_err)}"
                        )
            
            except asyncio.TimeoutError:
                response_time_ms = (time.time() - start_time) * 1000
                return ValidationResult(
                    provider_id=provider_id,
                    status=ValidationStatus.TIMEOUT,
                    response_time_ms=response_time_ms,
                    test_endpoint=test_url,
                    error_message=f"Request timeout after {self.timeout}s"
                )
            
            except Exception as e:
                response_time_ms = (time.time() - start_time) * 1000
                return ValidationResult(
                    provider_id=provider_id,
                    status=ValidationStatus.UNKNOWN_ERROR,
                    response_time_ms=response_time_ms,
                    test_endpoint=test_url,
                    error_message=f"{type(e).__name__}: {str(e)}"
                )
    
    async def validate_providers(
        self,
        providers: Dict[str, Dict],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, ValidationResult]:
        """
        Validate multiple providers concurrently
        
        Args:
            providers: Dict of provider_id -> provider_data
            progress_callback: Optional callback(current, total, provider_id)
        
        Returns:
            Dict of provider_id -> ValidationResult
        """
        await self.init_session()
        
        total = len(providers)
        results = {}
        
        # Create tasks
        tasks = []
        provider_ids = []
        
        for provider_id, provider_data in providers.items():
            task = self.validate_provider(provider_id, provider_data)
            tasks.append(task)
            provider_ids.append(provider_id)
        
        # Execute with progress tracking
        for i, task in enumerate(asyncio.as_completed(tasks)):
            result = await task
            results[result.provider_id] = result
            
            if progress_callback:
                progress_callback(i + 1, total, result.provider_id)
        
        return results
    
    def get_statistics(self, results: Dict[str, ValidationResult]) -> Dict[str, Any]:
        """Get validation statistics"""
        total = len(results)
        valid = sum(1 for r in results.values() if r.status == ValidationStatus.VALID)
        invalid = sum(1 for r in results.values() if r.status == ValidationStatus.INVALID)
        requires_auth = sum(1 for r in results.values() if r.status == ValidationStatus.REQUIRES_AUTH)
        timeout = sum(1 for r in results.values() if r.status == ValidationStatus.TIMEOUT)
        rate_limited = sum(1 for r in results.values() if r.status == ValidationStatus.RATE_LIMITED)
        unknown = sum(1 for r in results.values() if r.status == ValidationStatus.UNKNOWN_ERROR)
        
        # Calculate avg response time for valid providers
        valid_times = [r.response_time_ms for r in results.values() 
                       if r.status == ValidationStatus.VALID and r.response_time_ms]
        avg_response_time = sum(valid_times) / len(valid_times) if valid_times else 0
        
        return {
            "total": total,
            "valid": valid,
            "invalid": invalid,
            "requires_auth": requires_auth,
            "timeout": timeout,
            "rate_limited": rate_limited,
            "unknown_error": unknown,
            "validation_rate": (valid / total * 100) if total > 0 else 0,
            "avg_response_time_ms": round(avg_response_time, 2)
        }


# Test function
async def test_validator():
    """Test the validator with some providers"""
    test_providers = {
        "coingecko": {
            "name": "CoinGecko",
            "category": "market_data",
            "base_url": "https://api.coingecko.com/api/v3",
            "endpoints": {
                "ping": "/ping",
                "simple_price": "/simple/price?ids=bitcoin&vs_currencies=usd"
            },
            "requires_auth": False
        },
        "binance": {
            "name": "Binance",
            "category": "exchange",
            "base_url": "https://api.binance.com/api/v3",
            "endpoints": {
                "ping": "/ping",
                "ticker_price": "/ticker/price?symbol=BTCUSDT"
            },
            "requires_auth": False
        },
        "invalid_provider": {
            "name": "Invalid Provider",
            "category": "test",
            "base_url": "https://invalid-api-that-does-not-exist-12345.com",
            "endpoints": {
                "test": "/test"
            },
            "requires_auth": False
        }
    }
    
    validator = ProviderValidator(timeout=10, max_concurrent=3)
    
    print("Testing provider validation...\n")
    
    def progress(current, total, provider_id):
        print(f"[{current}/{total}] Validating: {provider_id}")
    
    results = await validator.validate_providers(test_providers, progress)
    
    print("\nResults:")
    print("=" * 80)
    
    for provider_id, result in results.items():
        print(f"\nProvider: {provider_id}")
        print(f"  Status: {result.status.value}")
        print(f"  HTTP Status: {result.http_status}")
        print(f"  Response Time: {result.response_time_ms:.2f}ms" if result.response_time_ms else "  Response Time: N/A")
        print(f"  Test URL: {result.test_endpoint}")
        if result.error_message:
            print(f"  Error: {result.error_message}")
    
    stats = validator.get_statistics(results)
    print("\nStatistics:")
    print("=" * 80)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    await validator.close_session()


if __name__ == "__main__":
    asyncio.run(test_validator())
