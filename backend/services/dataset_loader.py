#!/usr/bin/env python3
"""
HuggingFace Dataset Loader - Direct Loading
Loads cryptocurrency datasets directly from Hugging Face
"""

import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import datasets
try:
    from datasets import load_dataset, Dataset, DatasetDict
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False
    logger.error("❌ Datasets library not available. Install with: pip install datasets")


class CryptoDatasetLoader:
    """
    Direct Cryptocurrency Dataset Loader
    Loads crypto datasets from Hugging Face without using pipelines
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize Dataset Loader
        
        Args:
            cache_dir: Directory to cache datasets (default: ~/.cache/huggingface/datasets)
        """
        if not DATASETS_AVAILABLE:
            raise ImportError("Datasets library is required. Install with: pip install datasets")
        
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/huggingface/datasets")
        self.datasets = {}
        
        logger.info(f"🚀 Crypto Dataset Loader initialized")
        logger.info(f"   Cache directory: {self.cache_dir}")
        
        # Dataset configurations
        self.dataset_configs = {
            "cryptocoin": {
                "dataset_id": "linxy/CryptoCoin",
                "description": "CryptoCoin dataset by Linxy",
                "loaded": False
            },
            "bitcoin_btc_usdt": {
                "dataset_id": "WinkingFace/CryptoLM-Bitcoin-BTC-USDT",
                "description": "Bitcoin BTC-USDT market data",
                "loaded": False
            },
            "ethereum_eth_usdt": {
                "dataset_id": "WinkingFace/CryptoLM-Ethereum-ETH-USDT",
                "description": "Ethereum ETH-USDT market data",
                "loaded": False
            },
            "solana_sol_usdt": {
                "dataset_id": "WinkingFace/CryptoLM-Solana-SOL-USDT",
                "description": "Solana SOL-USDT market data",
                "loaded": False
            },
            "ripple_xrp_usdt": {
                "dataset_id": "WinkingFace/CryptoLM-Ripple-XRP-USDT",
                "description": "Ripple XRP-USDT market data",
                "loaded": False
            }
        }
    
    async def load_dataset(
        self,
        dataset_key: str,
        split: Optional[str] = None,
        streaming: bool = False
    ) -> Dict[str, Any]:
        """
        Load a specific dataset directly
        
        Args:
            dataset_key: Key of the dataset to load
            split: Dataset split to load (train, test, validation, etc.)
            streaming: Whether to stream the dataset
            
        Returns:
            Status dict with dataset info
        """
        if dataset_key not in self.dataset_configs:
            raise ValueError(f"Unknown dataset: {dataset_key}")
        
        config = self.dataset_configs[dataset_key]
        
        # Check if already loaded
        if dataset_key in self.datasets:
            logger.info(f"✅ Dataset {dataset_key} already loaded")
            config["loaded"] = True
            return {
                "success": True,
                "dataset_key": dataset_key,
                "dataset_id": config["dataset_id"],
                "status": "already_loaded",
                "num_rows": len(self.datasets[dataset_key]) if hasattr(self.datasets[dataset_key], "__len__") else "unknown"
            }
        
        try:
            logger.info(f"📥 Loading dataset: {config['dataset_id']}")
            
            # Load dataset directly
            dataset = load_dataset(
                config["dataset_id"],
                split=split,
                cache_dir=self.cache_dir,
                streaming=streaming
            )
            
            # Store dataset
            self.datasets[dataset_key] = dataset
            config["loaded"] = True
            
            # Get dataset info
            if isinstance(dataset, Dataset):
                num_rows = len(dataset)
                columns = dataset.column_names
            elif isinstance(dataset, DatasetDict):
                num_rows = {split: len(dataset[split]) for split in dataset.keys()}
                columns = list(dataset[list(dataset.keys())[0]].column_names)
            else:
                num_rows = "unknown"
                columns = []
            
            logger.info(f"✅ Dataset loaded successfully: {config['dataset_id']}")
            
            return {
                "success": True,
                "dataset_key": dataset_key,
                "dataset_id": config["dataset_id"],
                "status": "loaded",
                "num_rows": num_rows,
                "columns": columns,
                "streaming": streaming
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to load dataset {dataset_key}: {e}")
            raise Exception(f"Failed to load dataset {dataset_key}: {str(e)}")
    
    async def load_all_datasets(self, streaming: bool = False) -> Dict[str, Any]:
        """
        Load all configured datasets
        
        Args:
            streaming: Whether to stream the datasets
            
        Returns:
            Status dict with all datasets
        """
        results = []
        success_count = 0
        
        for dataset_key in self.dataset_configs.keys():
            try:
                result = await self.load_dataset(dataset_key, streaming=streaming)
                results.append(result)
                if result["success"]:
                    success_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to load {dataset_key}: {e}")
                results.append({
                    "success": False,
                    "dataset_key": dataset_key,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "total_datasets": len(self.dataset_configs),
            "loaded_datasets": success_count,
            "failed_datasets": len(self.dataset_configs) - success_count,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_dataset_sample(
        self,
        dataset_key: str,
        num_samples: int = 10,
        split: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get sample rows from a dataset
        
        Args:
            dataset_key: Key of the dataset
            num_samples: Number of samples to return
            split: Dataset split to sample from
            
        Returns:
            Sample data
        """
        # Ensure dataset is loaded
        if dataset_key not in self.datasets:
            await self.load_dataset(dataset_key, split=split)
        
        try:
            dataset = self.datasets[dataset_key]
            
            # Handle different dataset types
            if isinstance(dataset, DatasetDict):
                # Get first split if not specified
                split_to_use = split or list(dataset.keys())[0]
                dataset = dataset[split_to_use]
            
            # Get samples
            samples = dataset.select(range(min(num_samples, len(dataset))))
            
            # Convert to list of dicts
            samples_list = [dict(sample) for sample in samples]
            
            logger.info(f"✅ Retrieved {len(samples_list)} samples from {dataset_key}")
            
            return {
                "success": True,
                "dataset_key": dataset_key,
                "dataset_id": self.dataset_configs[dataset_key]["dataset_id"],
                "num_samples": len(samples_list),
                "samples": samples_list,
                "columns": list(samples_list[0].keys()) if samples_list else [],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to get samples from {dataset_key}: {e}")
            raise Exception(f"Failed to get samples: {str(e)}")
    
    async def query_dataset(
        self,
        dataset_key: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Query dataset with filters
        
        Args:
            dataset_key: Key of the dataset
            filters: Dictionary of column filters
            limit: Maximum number of results
            
        Returns:
            Filtered data
        """
        # Ensure dataset is loaded
        if dataset_key not in self.datasets:
            await self.load_dataset(dataset_key)
        
        try:
            dataset = self.datasets[dataset_key]
            
            # Handle DatasetDict
            if isinstance(dataset, DatasetDict):
                dataset = dataset[list(dataset.keys())[0]]
            
            # Apply filters if provided
            if filters:
                for column, value in filters.items():
                    dataset = dataset.filter(lambda x: x[column] == value)
            
            # Limit results
            result_dataset = dataset.select(range(min(limit, len(dataset))))
            
            # Convert to list of dicts
            results = [dict(row) for row in result_dataset]
            
            logger.info(f"✅ Query returned {len(results)} results from {dataset_key}")
            
            return {
                "success": True,
                "dataset_key": dataset_key,
                "filters_applied": filters or {},
                "count": len(results),
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to query dataset {dataset_key}: {e}")
            raise Exception(f"Failed to query dataset: {str(e)}")
    
    async def get_dataset_stats(self, dataset_key: str) -> Dict[str, Any]:
        """
        Get statistics about a dataset
        
        Args:
            dataset_key: Key of the dataset
            
        Returns:
            Dataset statistics
        """
        # Ensure dataset is loaded
        if dataset_key not in self.datasets:
            await self.load_dataset(dataset_key)
        
        try:
            dataset = self.datasets[dataset_key]
            
            # Handle DatasetDict
            if isinstance(dataset, DatasetDict):
                splits_info = {}
                for split_name, split_dataset in dataset.items():
                    splits_info[split_name] = {
                        "num_rows": len(split_dataset),
                        "columns": split_dataset.column_names,
                        "features": str(split_dataset.features)
                    }
                
                return {
                    "success": True,
                    "dataset_key": dataset_key,
                    "dataset_id": self.dataset_configs[dataset_key]["dataset_id"],
                    "type": "DatasetDict",
                    "splits": splits_info,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": True,
                    "dataset_key": dataset_key,
                    "dataset_id": self.dataset_configs[dataset_key]["dataset_id"],
                    "type": "Dataset",
                    "num_rows": len(dataset),
                    "columns": dataset.column_names,
                    "features": str(dataset.features),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            logger.error(f"❌ Failed to get stats for {dataset_key}: {e}")
            raise Exception(f"Failed to get dataset stats: {str(e)}")
    
    def get_loaded_datasets(self) -> Dict[str, Any]:
        """
        Get list of loaded datasets
        
        Returns:
            Dict with loaded datasets info
        """
        datasets_info = []
        for dataset_key, config in self.dataset_configs.items():
            info = {
                "dataset_key": dataset_key,
                "dataset_id": config["dataset_id"],
                "description": config["description"],
                "loaded": dataset_key in self.datasets
            }
            
            # Add size info if loaded
            if dataset_key in self.datasets:
                dataset = self.datasets[dataset_key]
                if isinstance(dataset, DatasetDict):
                    info["num_rows"] = {split: len(dataset[split]) for split in dataset.keys()}
                elif hasattr(dataset, "__len__"):
                    info["num_rows"] = len(dataset)
                else:
                    info["num_rows"] = "unknown"
            
            datasets_info.append(info)
        
        return {
            "success": True,
            "total_configured": len(self.dataset_configs),
            "total_loaded": len(self.datasets),
            "datasets": datasets_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def unload_dataset(self, dataset_key: str) -> Dict[str, Any]:
        """
        Unload a specific dataset from memory
        
        Args:
            dataset_key: Key of the dataset to unload
            
        Returns:
            Status dict
        """
        if dataset_key not in self.datasets:
            return {
                "success": False,
                "dataset_key": dataset_key,
                "message": "Dataset not loaded"
            }
        
        try:
            # Remove dataset
            del self.datasets[dataset_key]
            
            # Update config
            self.dataset_configs[dataset_key]["loaded"] = False
            
            logger.info(f"✅ Dataset unloaded: {dataset_key}")
            
            return {
                "success": True,
                "dataset_key": dataset_key,
                "message": "Dataset unloaded successfully"
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to unload dataset {dataset_key}: {e}")
            return {
                "success": False,
                "dataset_key": dataset_key,
                "error": str(e)
            }


# Global instance
crypto_dataset_loader = CryptoDatasetLoader()


# Export
__all__ = ["CryptoDatasetLoader", "crypto_dataset_loader"]
