#!/usr/bin/env python3
"""
Hugging Face Synchronization Service
Handles HuggingFace models and datasets synchronization
"""

import os
import logging
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class HuggingFaceSyncService:
    """
    Service for synchronizing with Hugging Face Hub
    """
    
    def __init__(self):
        self.hf_api_key = os.getenv("HF_API_KEY", os.getenv("HF_API_TOKEN", ""))
        self.base_url = "https://huggingface.co"
        self.api_url = "https://huggingface.co/api"
        self.timeout = 60.0
        
        self.headers = {
            "User-Agent": "CryptoDataHub-Sync/1.0"
        }
        
        if self.hf_api_key:
            self.headers["Authorization"] = f"Bearer {self.hf_api_key}"
        
        # Models to sync
        self.models_to_sync = [
            "ElKulako/cryptobert",
            "kk08/CryptoBERT",
            "ProsusAI/finbert",
            "cardiffnlp/twitter-roberta-base-sentiment"
        ]
        
        # Datasets to sync
        self.datasets_to_sync = [
            "linxy/CryptoCoin",
            "WinkingFace/CryptoLM-Bitcoin-BTC-USDT",
            "WinkingFace/CryptoLM-Ethereum-ETH-USDT",
            "WinkingFace/CryptoLM-Solana-SOL-USDT",
            "WinkingFace/CryptoLM-Ripple-XRP-USDT"
        ]
        
        logger.info(f"🤗 Hugging Face Sync Service initialized")
        logger.info(f"   Models: {len(self.models_to_sync)}")
        logger.info(f"   Datasets: {len(self.datasets_to_sync)}")
        logger.info(f"   Auth: {'✅ API key configured' if self.hf_api_key else '❌ No API key'}")
    
    async def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get model information from Hugging Face
        
        Args:
            model_id: Model identifier (e.g., "ElKulako/cryptobert")
            
        Returns:
            Model information
        """
        try:
            url = f"{self.api_url}/models/{model_id}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                model_data = response.json()
            
            # Parse model info
            model_info = {
                "id": model_data.get("id", model_id),
                "author": model_data.get("author", ""),
                "modelId": model_data.get("modelId", model_id),
                "pipeline_tag": model_data.get("pipeline_tag", ""),
                "tags": model_data.get("tags", []),
                "downloads": model_data.get("downloads", 0),
                "likes": model_data.get("likes", 0),
                "library_name": model_data.get("library_name", ""),
                "created_at": model_data.get("createdAt", ""),
                "last_modified": model_data.get("lastModified", ""),
                "private": model_data.get("private", False),
                "sha": model_data.get("sha", ""),
                "url": f"{self.base_url}/{model_id}"
            }
            
            logger.info(f"✅ Fetched model info: {model_id}")
            
            return {
                "success": True,
                "model": model_info,
                "model_id": model_id
            }
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HF API error for {model_id}: {e.response.status_code}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}",
                "model_id": model_id
            }
        except Exception as e:
            logger.error(f"❌ Failed to fetch model {model_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "model_id": model_id
            }
    
    async def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get dataset information from Hugging Face
        
        Args:
            dataset_id: Dataset identifier (e.g., "linxy/CryptoCoin")
            
        Returns:
            Dataset information
        """
        try:
            url = f"{self.api_url}/datasets/{dataset_id}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                dataset_data = response.json()
            
            # Parse dataset info
            dataset_info = {
                "id": dataset_data.get("id", dataset_id),
                "author": dataset_data.get("author", ""),
                "sha": dataset_data.get("sha", ""),
                "created_at": dataset_data.get("createdAt", ""),
                "last_modified": dataset_data.get("lastModified", ""),
                "private": dataset_data.get("private", False),
                "downloads": dataset_data.get("downloads", 0),
                "likes": dataset_data.get("likes", 0),
                "tags": dataset_data.get("tags", []),
                "card_data": dataset_data.get("cardData", {}),
                "url": f"{self.base_url}/datasets/{dataset_id}"
            }
            
            logger.info(f"✅ Fetched dataset info: {dataset_id}")
            
            return {
                "success": True,
                "dataset": dataset_info,
                "dataset_id": dataset_id
            }
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HF API error for {dataset_id}: {e.response.status_code}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}",
                "dataset_id": dataset_id
            }
        except Exception as e:
            logger.error(f"❌ Failed to fetch dataset {dataset_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "dataset_id": dataset_id
            }
    
    async def sync_models(self) -> Dict[str, Any]:
        """
        Sync all configured models
        
        Returns:
            Sync results for all models
        """
        logger.info(f"🔄 Syncing {len(self.models_to_sync)} models from Hugging Face...")
        
        results = []
        successful = 0
        failed = 0
        
        for model_id in self.models_to_sync:
            result = await self.get_model_info(model_id)
            results.append(result)
            
            if result["success"]:
                successful += 1
            else:
                failed += 1
        
        return {
            "success": failed == 0,
            "models": results,
            "total": len(self.models_to_sync),
            "successful": successful,
            "failed": failed,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def sync_datasets(self) -> Dict[str, Any]:
        """
        Sync all configured datasets
        
        Returns:
            Sync results for all datasets
        """
        logger.info(f"🔄 Syncing {len(self.datasets_to_sync)} datasets from Hugging Face...")
        
        results = []
        successful = 0
        failed = 0
        
        for dataset_id in self.datasets_to_sync:
            result = await self.get_dataset_info(dataset_id)
            results.append(result)
            
            if result["success"]:
                successful += 1
            else:
                failed += 1
        
        return {
            "success": failed == 0,
            "datasets": results,
            "total": len(self.datasets_to_sync),
            "successful": successful,
            "failed": failed,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def sync_all(self) -> Dict[str, Any]:
        """
        Sync all models and datasets
        
        Returns:
            Complete sync results
        """
        logger.info(f"🚀 Starting complete Hugging Face synchronization...")
        
        start_time = datetime.utcnow()
        
        # Sync models
        models_result = await self.sync_models()
        
        # Sync datasets
        datasets_result = await self.sync_datasets()
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        result = {
            "success": models_result["success"] and datasets_result["success"],
            "models": models_result,
            "datasets": datasets_result,
            "summary": {
                "total_models": models_result["total"],
                "successful_models": models_result["successful"],
                "failed_models": models_result["failed"],
                "total_datasets": datasets_result["total"],
                "successful_datasets": datasets_result["successful"],
                "failed_datasets": datasets_result["failed"]
            },
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
        if result["success"]:
            logger.info(f"✅ Hugging Face synchronization completed successfully in {duration:.2f}s")
        else:
            logger.error(f"❌ Hugging Face synchronization completed with errors in {duration:.2f}s")
        
        return result
    
    def save_sync_data(self, sync_result: Dict[str, Any], output_dir: str = "/workspace/sync_data") -> str:
        """
        Save sync data to file
        
        Args:
            sync_result: Sync result data
            output_dir: Output directory
            
        Returns:
            Path to saved file
        """
        try:
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"hf_sync_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            # Save data
            with open(filepath, 'w') as f:
                json.dump(sync_result, f, indent=2)
            
            logger.info(f"✅ Saved sync data to: {filepath}")
            
            return filepath
        
        except Exception as e:
            logger.error(f"❌ Failed to save sync data: {e}")
            return ""


# Global instance
huggingface_sync_service = HuggingFaceSyncService()


# Export
__all__ = ["HuggingFaceSyncService", "huggingface_sync_service"]
