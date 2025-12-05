#!/usr/bin/env python3
"""
Additional API Endpoints for Frontend Integration
Ensures all required endpoints are available and properly integrated
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["integration"])

@router.get("/models/summary")
async def get_models_summary() -> Dict[str, Any]:
    """
    Get AI models summary for frontend display with detailed diagnostics
    """
    try:
        from ai_models import registry_status, MODEL_SPECS, get_model_health_registry, HF_MODE, TRANSFORMERS_AVAILABLE, HF_TOKEN_ENV
        
        status = registry_status()
        health_registry = get_model_health_registry()
        
        # Get actual loaded models from registry
        from ai_models import _registry
        loaded_models = list(_registry._pipelines.keys())
        failed_models = list(_registry._failed_models.keys())
        
        # Group models by category
        categories = {}
        for key, spec in MODEL_SPECS.items():
            cat = spec.category
            if cat not in categories:
                categories[cat] = []
            
            # Find health info for this model
            health_info = next((h for h in health_registry if h['key'] == key), None)
            
            # Check if model is actually loaded
            is_loaded = key in loaded_models
            is_failed = key in failed_models
            failure_reason = _registry._failed_models.get(key) if is_failed else None
            
            categories[cat].append({
                "key": key,
                "name": spec.model_id,
                "task": spec.task,
                "loaded": is_loaded,
                "failed": is_failed,
                "failure_reason": failure_reason[:200] if failure_reason else None,
                "status": health_info.get('status', 'unknown') if health_info else ('failed' if is_failed else 'not_loaded'),
                "error_count": health_info.get('error_count', 0) if health_info else (1 if is_failed else 0),
                "requires_auth": spec.requires_auth,
                "last_success": health_info.get('last_success') if health_info else None,
                "last_error": health_info.get('last_error') if health_info else None
            })
        
        # Calculate accurate counts
        total_models = len(MODEL_SPECS)
        loaded_count = len(loaded_models)
        failed_count = len(failed_models)
        
        return {
            "ok": True,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_models": total_models,
                "loaded_models": loaded_count,
                "failed_models": failed_count,
                "not_loaded_models": total_models - loaded_count - failed_count,
                "hf_mode": HF_MODE,
                "transformers_available": TRANSFORMERS_AVAILABLE,
                "hf_token_available": bool(HF_TOKEN_ENV),
                "initialized": status.get('initialized', False),
                "status": status.get('status', 'unknown')
            },
            "categories": categories,
            "health_registry": health_registry,
            "loaded_model_keys": loaded_models[:50],  # Show first 50
            "failed_model_keys": failed_models[:50],  # Show first 50
            "diagnostics": {
                "hf_mode": HF_MODE,
                "transformers_available": TRANSFORMERS_AVAILABLE,
                "hf_token_set": bool(HF_TOKEN_ENV),
                "hf_token_length": len(HF_TOKEN_ENV) if HF_TOKEN_ENV else 0,
                "registry_initialized": status.get('initialized', False),
                "registry_status": status.get('status', 'unknown'),
                "total_specs": total_models,
                "pipelines_loaded": loaded_count,
                "pipelines_failed": failed_count
            }
        }
    except Exception as e:
        logger.error(f"Error getting models summary: {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "summary": {
                "total_models": 0, "loaded_models": 0, "failed_models": 0,
                "hf_mode": "error", "transformers_available": False
            },
            "categories": {},
            "health_registry": [],
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/models/diagnostics")
async def get_models_diagnostics() -> Dict[str, Any]:
    """
    Get detailed diagnostics about model loading status and issues
    """
    try:
        from ai_models import (
            _registry, MODEL_SPECS, HF_MODE, TRANSFORMERS_AVAILABLE, 
            HF_TOKEN_ENV, registry_status, get_model_health_registry
        )
        
        status = registry_status()
        health_registry = get_model_health_registry()
        
        loaded_models = list(_registry._pipelines.keys())
        failed_models = list(_registry._failed_models.keys())
        
        # Analyze why models aren't loading
        issues = []
        recommendations = []
        
        if HF_MODE == "off":
            issues.append("HF_MODE is set to 'off' - models are disabled")
            recommendations.append("Set HF_MODE=public or HF_MODE=auth in environment variables")
        
        if not TRANSFORMERS_AVAILABLE:
            issues.append("Transformers library is not installed")
            recommendations.append("Install transformers: pip install transformers torch")
        
        if not HF_TOKEN_ENV and HF_MODE == "auth":
            issues.append("HF_TOKEN not set but HF_MODE=auth requires authentication")
            recommendations.append("Set HF_TOKEN environment variable for authenticated models")
        
        if len(loaded_models) == 0 and len(failed_models) > 0:
            issues.append(f"No models loaded, {len(failed_models)} models failed")
            recommendations.append("Check failed_models list for specific error messages")
            recommendations.append("Verify model IDs exist on Hugging Face Hub")
            recommendations.append("Check network connectivity to huggingface.co")
        
        if len(loaded_models) == 0 and len(failed_models) == 0:
            issues.append("No models loaded and no failures recorded - models may not have been initialized")
            recommendations.append("Call /api/models/reinit-all to force initialization")
            recommendations.append("Check server startup logs for initialization errors")
        
        # Get sample failed model errors
        failed_samples = []
        for key in failed_models[:5]:
            error_msg = _registry._failed_models.get(key, "Unknown error")
            spec = MODEL_SPECS.get(key)
            failed_samples.append({
                "key": key,
                "model_id": spec.model_id if spec else key,
                "error": error_msg[:300]
            })
        
        return {
            "ok": True,
            "timestamp": datetime.utcnow().isoformat(),
            "environment": {
                "hf_mode": HF_MODE,
                "transformers_available": TRANSFORMERS_AVAILABLE,
                "hf_token_set": bool(HF_TOKEN_ENV),
                "hf_token_length": len(HF_TOKEN_ENV) if HF_TOKEN_ENV else 0,
                "python_version": __import__('sys').version.split()[0]
            },
            "registry_status": {
                "initialized": _registry._initialized,
                "total_specs": len(MODEL_SPECS),
                "pipelines_loaded": len(loaded_models),
                "pipelines_failed": len(failed_models),
                "status": status.get('status', 'unknown')
            },
            "loaded_models": loaded_models[:20],
            "failed_models": failed_models[:20],
            "failed_samples": failed_samples,
            "issues": issues,
            "recommendations": recommendations,
            "health_registry_summary": {
                "total_entries": len(health_registry),
                "healthy": len([h for h in health_registry if h.get('status') == 'healthy']),
                "unhealthy": len([h for h in health_registry if h.get('status') == 'unhealthy']),
                "unknown": len([h for h in health_registry if h.get('status') == 'unknown'])
            }
        }
    except Exception as e:
        logger.error(f"Error getting models diagnostics: {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/models/initialize-batch")
async def initialize_models_batch(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize multiple models at once with detailed progress tracking
    """
    try:
        from ai_models import _registry, MODEL_SPECS, initialize_models
        
        max_models = request.get("max_models", None)
        force_reload = request.get("force_reload", False)
        category_filter = request.get("category", None)  # Optional category filter
        
        logger.info(f"Batch initialization requested: max_models={max_models}, force_reload={force_reload}, category={category_filter}")
        
        # Initialize with parameters
        result = initialize_models(force_reload=force_reload, max_models=max_models)
        
        # Get current status
        from ai_models import registry_status
        registry_info = registry_status()
        
        return {
            "ok": True,
            "timestamp": datetime.utcnow().isoformat(),
            "initialization_result": result,
            "registry_status": registry_info,
            "message": f"Initialized {result.get('models_loaded', 0)} model(s)"
        }
    except Exception as e:
        logger.error(f"Error in batch initialization: {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/resources/count")
async def get_resources_count() -> Dict[str, Any]:
    """
    Get count of API resources and keys
    """
    try:
        import json
        from pathlib import Path
        
        # Try to load from all_apis_merged_2025.json
        api_registry_path = Path("all_apis_merged_2025.json")
        if not api_registry_path.exists():
            api_registry_path = Path("api-resources") / "all_apis_merged_2025.json"
        
        if api_registry_path.exists():
            with open(api_registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Count resources
            total_resources = len(data.get("apis", []))
            free_resources = len([api for api in data.get("apis", []) if api.get("free", False)])
            
            # Count API keys
            total_api_keys = 0
            for api in data.get("apis", []):
                keys = api.get("keys", [])
                if isinstance(keys, list):
                    total_api_keys += len(keys)
                elif isinstance(keys, dict):
                    total_api_keys += len(keys)
            
            return {
                "ok": True,
                "timestamp": datetime.utcnow().isoformat(),
                "total_resources": total_resources,
                "free_resources": free_resources,
                "total_api_keys": total_api_keys
            }
        else:
            logger.warning(f"API registry file not found: {api_registry_path}")
            return {
                "ok": False,
                "error": "API registry file not found",
                "timestamp": datetime.utcnow().isoformat(),
                "total_resources": 0,
                "free_resources": 0,
                "total_api_keys": 0
            }
    except Exception as e:
        logger.error(f"Error getting resources count: {e}", exc_info=True)
        return {
            "ok": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.utcnow().isoformat(),
            "total_resources": 0,
            "free_resources": 0,
            "total_api_keys": 0
        }
