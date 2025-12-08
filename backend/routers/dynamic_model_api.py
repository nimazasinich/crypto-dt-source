#!/usr/bin/env python3
"""
Dynamic Model API - REST endpoints for dynamic model loading
API برای بارگذاری هوشمند مدل‌ها
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend.services.dynamic_model_loader import dynamic_loader

router = APIRouter(prefix="/api/dynamic-models", tags=["Dynamic Models"])


# ===== Pydantic Models =====

class ModelConfig(BaseModel):
    """تنظیمات مدل جدید"""
    model_id: str = Field(..., description="Unique identifier for the model")
    model_name: str = Field(..., description="Display name")
    base_url: str = Field(..., description="Base URL of the API")
    api_key: Optional[str] = Field(None, description="API key (if required)")
    api_type: Optional[str] = Field(None, description="API type (auto-detected if not provided)")
    endpoints: Optional[Dict[str, Any]] = Field(None, description="Custom endpoints (auto-discovered if not provided)")
    custom_config: Optional[Dict[str, Any]] = Field(None, description="Additional configuration")


class PasteConfig(BaseModel):
    """
    کپی/پیست تنظیمات از منابع مختلف
    Supports multiple formats
    """
    config_text: str = Field(..., description="Pasted configuration (JSON, YAML, or key-value pairs)")
    auto_detect: bool = Field(True, description="Auto-detect format and API type")


class ModelUsageRequest(BaseModel):
    """درخواست استفاده از مدل"""
    endpoint: str = Field(..., description="Endpoint to call (e.g., '', '/predict', '/generate')")
    payload: Dict[str, Any] = Field(..., description="Request payload")


class DetectionRequest(BaseModel):
    """درخواست تشخیص نوع API"""
    config: Dict[str, Any] = Field(..., description="Configuration to analyze")


# ===== Endpoints =====

@router.post("/register")
async def register_model(config: ModelConfig):
    """
    ثبت مدل جدید
    
    **Usage**:
    ```json
    {
      "model_id": "my-custom-model",
      "model_name": "My Custom Model",
      "base_url": "https://api.example.com/models/my-model",
      "api_key": "sk-xxxxx",
      "api_type": "huggingface"
    }
    ```
    
    **Auto-Detection**:
    - If `api_type` is not provided, it will be auto-detected
    - If `endpoints` are not provided, they will be auto-discovered
    """
    try:
        result = await dynamic_loader.register_model(config.dict())
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Registration failed'))
        
        return {
            "success": True,
            "message": "Model registered successfully",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/paste-config")
async def paste_configuration(paste: PasteConfig):
    """
    کپی/پیست تنظیمات از هر منبعی
    
    **Supported Formats**:
    - JSON
    - YAML
    - Key-value pairs
    - HuggingFace model cards
    - OpenAI config
    - cURL commands
    
    **Example**:
    ```
    {
      "config_text": "{\\"model_id\\": \\"gpt-4\\", \\"base_url\\": \\"https://api.openai.com\\", ...}",
      "auto_detect": true
    }
    ```
    """
    try:
        import json
        import yaml
        
        config_text = paste.config_text.strip()
        parsed_config = None
        
        # Try JSON first
        try:
            parsed_config = json.loads(config_text)
        except:
            pass
        
        # Try YAML
        if not parsed_config:
            try:
                parsed_config = yaml.safe_load(config_text)
            except:
                pass
        
        # Try key-value pairs
        if not parsed_config:
            parsed_config = {}
            for line in config_text.split('\n'):
                if ':' in line or '=' in line:
                    separator = ':' if ':' in line else '='
                    parts = line.split(separator, 1)
                    if len(parts) == 2:
                        key = parts[0].strip().lower().replace(' ', '_')
                        value = parts[1].strip()
                        parsed_config[key] = value
        
        if not parsed_config or not isinstance(parsed_config, dict):
            raise HTTPException(
                status_code=400,
                detail="Could not parse configuration. Please provide valid JSON, YAML, or key-value pairs."
            )
        
        # Ensure required fields
        if 'model_id' not in parsed_config:
            parsed_config['model_id'] = f"pasted-model-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if 'model_name' not in parsed_config:
            parsed_config['model_name'] = parsed_config['model_id']
        
        if 'base_url' not in parsed_config:
            raise HTTPException(
                status_code=400,
                detail="'base_url' is required in configuration"
            )
        
        # Auto-detect if requested
        if paste.auto_detect and 'api_type' not in parsed_config:
            parsed_config['api_type'] = await dynamic_loader.detect_api_type(parsed_config)
        
        # Register the model
        result = await dynamic_loader.register_model(parsed_config)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Registration failed'))
        
        return {
            "success": True,
            "message": "Model registered from pasted configuration",
            "parsed_config": parsed_config,
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process pasted config: {str(e)}")


@router.post("/detect-api-type")
async def detect_api_type(request: DetectionRequest):
    """
    تشخیص خودکار نوع API
    
    **Example**:
    ```json
    {
      "config": {
        "base_url": "https://api-inference.huggingface.co/models/bert-base",
        "api_key": "hf_xxxxx"
      }
    }
    ```
    
    **Returns**: Detected API type (huggingface, openai, rest, graphql, etc.)
    """
    try:
        api_type = await dynamic_loader.detect_api_type(request.config)
        
        return {
            "success": True,
            "api_type": api_type,
            "config": request.config
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@router.post("/test-connection")
async def test_connection(config: ModelConfig):
    """
    تست اتصال به مدل بدون ثبت
    
    **Usage**: Test before registering
    """
    try:
        result = await dynamic_loader.test_model_connection(config.dict())
        
        return {
            "success": True,
            "test_result": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


@router.get("/models")
async def get_all_models():
    """
    دریافت لیست همه مدل‌های ثبت شده
    
    **Returns**: List of all registered dynamic models
    """
    try:
        models = dynamic_loader.get_all_models()
        
        return {
            "success": True,
            "total": len(models),
            "models": models
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


@router.get("/models/{model_id}")
async def get_model(model_id: str):
    """
    دریافت اطلاعات یک مدل خاص
    """
    try:
        model = dynamic_loader.get_model(model_id)
        
        if not model:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        return {
            "success": True,
            "model": model
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model: {str(e)}")


@router.post("/models/{model_id}/use")
async def use_model(model_id: str, usage: ModelUsageRequest):
    """
    استفاده از یک مدل ثبت شده
    
    **Example**:
    ```json
    {
      "endpoint": "",
      "payload": {
        "inputs": "Bitcoin is bullish!"
      }
    }
    ```
    """
    try:
        result = await dynamic_loader.use_model(
            model_id,
            usage.endpoint,
            usage.payload
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Model usage failed'))
        
        return {
            "success": True,
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to use model: {str(e)}")


@router.delete("/models/{model_id}")
async def delete_model(model_id: str):
    """
    حذف یک مدل
    """
    try:
        success = dynamic_loader.delete_model(model_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        return {
            "success": True,
            "message": f"Model {model_id} deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete model: {str(e)}")


@router.post("/auto-configure")
async def auto_configure_from_url(url: str = Body(..., embed=True)):
    """
    تنظیم خودکار کامل از URL
    
    **Usage**: Just provide a URL, everything else is auto-detected
    
    **Example**:
    ```json
    {
      "url": "https://api-inference.huggingface.co/models/bert-base-uncased"
    }
    ```
    
    **Process**:
    1. Auto-detect API type from URL
    2. Auto-discover endpoints
    3. Test connection
    4. Register if successful
    """
    try:
        # Create basic config from URL
        config = {
            'model_id': url.split('/')[-1] or f'auto-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'model_name': url.split('/')[-1] or 'Auto-configured Model',
            'base_url': url
        }
        
        # Auto-detect API type
        api_type = await dynamic_loader.detect_api_type(config)
        config['api_type'] = api_type
        
        # Auto-discover endpoints
        discovered = await dynamic_loader.auto_discover_endpoints(url)
        config['endpoints'] = discovered
        
        # Test connection
        test_result = await dynamic_loader.test_model_connection(config)
        
        if not test_result['success']:
            return {
                "success": False,
                "error": "Connection test failed",
                "test_result": test_result,
                "config": config,
                "message": "Model configuration created but connection failed. You can still register it manually."
            }
        
        # Register
        result = await dynamic_loader.register_model(config)
        
        return {
            "success": True,
            "message": "Model auto-configured and registered successfully",
            "config": config,
            "test_result": test_result,
            "registration": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-configuration failed: {str(e)}")


@router.get("/health")
async def health_check():
    """سلامت سیستم"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

