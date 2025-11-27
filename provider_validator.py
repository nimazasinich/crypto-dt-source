#!/usr/bin/env python3
"""
Provider Validator - REAL DATA ONLY
Validates HTTP providers and HF model services with actual test calls.
NO MOCK DATA. NO FAKE RESPONSES.
"""

import asyncio
import json
import os
import time
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

import httpx


class ProviderType(Enum):
    """Provider types"""

    HTTP_JSON = "http_json"
    HTTP_RPC = "http_rpc"
    WEBSOCKET = "websocket"
    HF_MODEL = "hf_model"


class ValidationStatus(Enum):
    """Validation status"""

    VALID = "VALID"
    INVALID = "INVALID"
    CONDITIONALLY_AVAILABLE = "CONDITIONALLY_AVAILABLE"
    SKIPPED = "SKIPPED"


@dataclass
class ValidationResult:
    """Result of provider validation"""

    provider_id: str
    provider_name: str
    provider_type: str
    category: str
    status: str
    response_time_ms: Optional[float] = None
    error_reason: Optional[str] = None
    requires_auth: bool = False
    auth_env_var: Optional[str] = None
    test_endpoint: Optional[str] = None
    response_sample: Optional[str] = None
    validated_at: float = 0.0

    def __post_init__(self):
        if self.validated_at == 0.0:
            self.validated_at = time.time()


class ProviderValidator:
    """
    Validates providers with REAL test calls.
    NO MOCK DATA. NO FAKE RESPONSES.
    """

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.results: List[ValidationResult] = []

    async def validate_http_provider(
        self, provider_id: str, provider_data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate an HTTP provider with a real test call.
        """
        name = provider_data.get("name", provider_id)
        category = provider_data.get("category", "unknown")
        base_url = provider_data.get("base_url", "")

        # Check for auth requirements
        auth_info = provider_data.get("auth", {})
        requires_auth = auth_info.get("type") not in [None, "", "none"]
        auth_env_var = None

        if requires_auth:
            # Try to find env var
            param_name = auth_info.get("param_name", "")
            if param_name:
                auth_env_var = f"{provider_id.upper()}_API_KEY"
                if not os.getenv(auth_env_var):
                    return ValidationResult(
                        provider_id=provider_id,
                        provider_name=name,
                        provider_type=ProviderType.HTTP_JSON.value,
                        category=category,
                        status=ValidationStatus.CONDITIONALLY_AVAILABLE.value,
                        error_reason=f"Requires API key via {auth_env_var} env var",
                        requires_auth=True,
                        auth_env_var=auth_env_var,
                    )

        # Determine test endpoint
        endpoints = provider_data.get("endpoints", {})
        test_endpoint = None

        if isinstance(endpoints, dict) and endpoints:
            # Use first endpoint
            test_endpoint = list(endpoints.values())[0]
        elif isinstance(endpoints, str):
            test_endpoint = endpoints
        elif provider_data.get("endpoint"):
            test_endpoint = provider_data.get("endpoint")
        else:
            # Try base_url as-is
            test_endpoint = ""

        # Build full URL
        if base_url.startswith("ws://") or base_url.startswith("wss://"):
            return ValidationResult(
                provider_id=provider_id,
                provider_name=name,
                provider_type=ProviderType.WEBSOCKET.value,
                category=category,
                status=ValidationStatus.SKIPPED.value,
                error_reason="WebSocket providers require separate validation",
            )

        # Check if it's an RPC endpoint
        is_rpc = "rpc" in category.lower() or "rpc" in provider_data.get("role", "").lower()

        if "{" in base_url and "}" in base_url:
            # URL has placeholders
            if requires_auth:
                return ValidationResult(
                    provider_id=provider_id,
                    provider_name=name,
                    provider_type=(
                        ProviderType.HTTP_RPC.value if is_rpc else ProviderType.HTTP_JSON.value
                    ),
                    category=category,
                    status=ValidationStatus.CONDITIONALLY_AVAILABLE.value,
                    error_reason=f"URL has placeholders and requires auth",
                    requires_auth=True,
                )
            else:
                return ValidationResult(
                    provider_id=provider_id,
                    provider_name=name,
                    provider_type=(
                        ProviderType.HTTP_RPC.value if is_rpc else ProviderType.HTTP_JSON.value
                    ),
                    category=category,
                    status=ValidationStatus.INVALID.value,
                    error_reason="URL has placeholders but no auth mechanism defined",
                )

        # Construct test URL
        if test_endpoint and test_endpoint.startswith("http"):
            test_url = test_endpoint
        else:
            test_url = (
                f"{base_url.rstrip('/')}/{test_endpoint.lstrip('/')}" if test_endpoint else base_url
            )

        # Make test call
        try:
            start = time.time()

            if is_rpc:
                # RPC call
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        test_url,
                        json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                    )
                    elapsed_ms = (time.time() - start) * 1000

                    if response.status_code == 200:
                        data = response.json()
                        if "result" in data or "error" not in data:
                            return ValidationResult(
                                provider_id=provider_id,
                                provider_name=name,
                                provider_type=ProviderType.HTTP_RPC.value,
                                category=category,
                                status=ValidationStatus.VALID.value,
                                response_time_ms=elapsed_ms,
                                test_endpoint=test_url,
                                response_sample=json.dumps(data)[:200],
                            )
                        else:
                            return ValidationResult(
                                provider_id=provider_id,
                                provider_name=name,
                                provider_type=ProviderType.HTTP_RPC.value,
                                category=category,
                                status=ValidationStatus.INVALID.value,
                                error_reason=f"RPC error: {data.get('error', 'Unknown')}",
                            )
                    else:
                        return ValidationResult(
                            provider_id=provider_id,
                            provider_name=name,
                            provider_type=ProviderType.HTTP_RPC.value,
                            category=category,
                            status=ValidationStatus.INVALID.value,
                            error_reason=f"HTTP {response.status_code}",
                        )
            else:
                # Regular HTTP JSON call
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(test_url)
                    elapsed_ms = (time.time() - start) * 1000

                    if response.status_code == 200:
                        # Try to parse as JSON
                        try:
                            data = response.json()
                            return ValidationResult(
                                provider_id=provider_id,
                                provider_name=name,
                                provider_type=ProviderType.HTTP_JSON.value,
                                category=category,
                                status=ValidationStatus.VALID.value,
                                response_time_ms=elapsed_ms,
                                test_endpoint=test_url,
                                response_sample=(
                                    json.dumps(data)[:200]
                                    if isinstance(data, dict)
                                    else str(data)[:200]
                                ),
                            )
                        except:
                            # Not JSON but 200 OK
                            return ValidationResult(
                                provider_id=provider_id,
                                provider_name=name,
                                provider_type=ProviderType.HTTP_JSON.value,
                                category=category,
                                status=ValidationStatus.VALID.value,
                                response_time_ms=elapsed_ms,
                                test_endpoint=test_url,
                                response_sample=response.text[:200],
                            )
                    elif response.status_code in [401, 403]:
                        return ValidationResult(
                            provider_id=provider_id,
                            provider_name=name,
                            provider_type=ProviderType.HTTP_JSON.value,
                            category=category,
                            status=ValidationStatus.CONDITIONALLY_AVAILABLE.value,
                            error_reason=f"HTTP {response.status_code} - Requires authentication",
                            requires_auth=True,
                        )
                    else:
                        return ValidationResult(
                            provider_id=provider_id,
                            provider_name=name,
                            provider_type=ProviderType.HTTP_JSON.value,
                            category=category,
                            status=ValidationStatus.INVALID.value,
                            error_reason=f"HTTP {response.status_code}",
                        )

        except Exception as e:
            return ValidationResult(
                provider_id=provider_id,
                provider_name=name,
                provider_type=(
                    ProviderType.HTTP_RPC.value if is_rpc else ProviderType.HTTP_JSON.value
                ),
                category=category,
                status=ValidationStatus.INVALID.value,
                error_reason=f"Exception: {str(e)[:100]}",
            )

    async def validate_hf_model(
        self, model_id: str, model_name: str, pipeline_tag: str = "sentiment-analysis"
    ) -> ValidationResult:
        """
        Validate a Hugging Face model using HF Hub API (lightweight check).
        Does NOT download or load the full model to save time and resources.
        """
        # First check if model exists via HF API
        try:
            start = time.time()

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"https://huggingface.co/api/models/{model_id}")
                elapsed_ms = (time.time() - start) * 1000

                if response.status_code == 200:
                    model_info = response.json()

                    # Model exists and is accessible
                    return ValidationResult(
                        provider_id=model_id,
                        provider_name=model_name,
                        provider_type=ProviderType.HF_MODEL.value,
                        category="hf_model",
                        status=ValidationStatus.VALID.value,
                        response_time_ms=elapsed_ms,
                        response_sample=json.dumps(
                            {
                                "modelId": model_info.get("modelId", model_id),
                                "pipeline_tag": model_info.get("pipeline_tag"),
                                "downloads": model_info.get("downloads"),
                                "likes": model_info.get("likes"),
                            }
                        )[:200],
                    )
                elif response.status_code == 401 or response.status_code == 403:
                    # Requires authentication
                    return ValidationResult(
                        provider_id=model_id,
                        provider_name=model_name,
                        provider_type=ProviderType.HF_MODEL.value,
                        category="hf_model",
                        status=ValidationStatus.CONDITIONALLY_AVAILABLE.value,
                        error_reason="Model requires authentication (HF_TOKEN)",
                        requires_auth=True,
                        auth_env_var="HF_TOKEN",
                    )
                elif response.status_code == 404:
                    return ValidationResult(
                        provider_id=model_id,
                        provider_name=model_name,
                        provider_type=ProviderType.HF_MODEL.value,
                        category="hf_model",
                        status=ValidationStatus.INVALID.value,
                        error_reason="Model not found on Hugging Face Hub",
                    )
                else:
                    return ValidationResult(
                        provider_id=model_id,
                        provider_name=model_name,
                        provider_type=ProviderType.HF_MODEL.value,
                        category="hf_model",
                        status=ValidationStatus.INVALID.value,
                        error_reason=f"HTTP {response.status_code}",
                    )

        except Exception as e:
            return ValidationResult(
                provider_id=model_id,
                provider_name=model_name,
                provider_type=ProviderType.HF_MODEL.value,
                category="hf_model",
                status=ValidationStatus.INVALID.value,
                error_reason=f"Exception: {str(e)[:100]}",
            )

    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary"""
        by_status = {}
        by_type = {}

        for result in self.results:
            # Count by status
            status = result.status
            by_status[status] = by_status.get(status, 0) + 1

            # Count by type
            ptype = result.provider_type
            by_type[ptype] = by_type.get(ptype, 0) + 1

        return {
            "total": len(self.results),
            "by_status": by_status,
            "by_type": by_type,
            "valid_count": by_status.get(ValidationStatus.VALID.value, 0),
            "invalid_count": by_status.get(ValidationStatus.INVALID.value, 0),
            "conditional_count": by_status.get(ValidationStatus.CONDITIONALLY_AVAILABLE.value, 0),
        }


if __name__ == "__main__":
    # Test with a simple provider
    async def test():
        validator = ProviderValidator()

        # Test CoinGecko
        result = await validator.validate_http_provider(
            "coingecko",
            {
                "name": "CoinGecko",
                "category": "market_data",
                "base_url": "https://api.coingecko.com/api/v3",
                "endpoints": {"ping": "/ping"},
            },
        )
        validator.results.append(result)

        print(json.dumps(asdict(result), indent=2))
        print("\nSummary:")
        print(json.dumps(validator.get_summary(), indent=2))

    asyncio.run(test())
