#!/usr/bin/env python3
"""
Direct Model Loader Service - NO PIPELINES
Loads Hugging Face models directly using AutoModel and AutoTokenizer
NO PIPELINE USAGE - Direct model inference only
"""

import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import torch
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import transformers
try:
    from transformers import (
        AutoTokenizer, 
        AutoModelForSequenceClassification,
        AutoModelForCausalLM,
        BertTokenizer,
        BertForSequenceClassification
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.error("❌ Transformers library not available. Install with: pip install transformers torch")


class DirectModelLoader:
    """
    Direct Model Loader - NO PIPELINES
    Loads models directly and performs inference without using Hugging Face pipelines
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize Direct Model Loader
        
        Args:
            cache_dir: Directory to cache models (default: ~/.cache/huggingface)
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers library is required. Install with: pip install transformers torch")
        
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/huggingface")
        self.models = {}
        self.tokenizers = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"🚀 Direct Model Loader initialized")
        logger.info(f"   Device: {self.device}")
        logger.info(f"   Cache directory: {self.cache_dir}")
        
        # Model configurations - DIRECT LOADING ONLY
        self.model_configs = {
            "cryptobert_elkulako": {
                "model_id": "ElKulako/cryptobert",
                "model_class": "BertForSequenceClassification",
                "task": "sentiment-analysis",
                "description": "CryptoBERT by ElKulako for crypto sentiment",
                "loaded": False
            },
            "cryptobert_kk08": {
                "model_id": "kk08/CryptoBERT",
                "model_class": "BertForSequenceClassification",
                "task": "sentiment-analysis",
                "description": "CryptoBERT by KK08 for crypto sentiment",
                "loaded": False
            },
            "finbert": {
                "model_id": "ProsusAI/finbert",
                "model_class": "AutoModelForSequenceClassification",
                "task": "sentiment-analysis",
                "description": "FinBERT for financial sentiment",
                "loaded": False
            },
            "twitter_sentiment": {
                "model_id": "cardiffnlp/twitter-roberta-base-sentiment",
                "model_class": "AutoModelForSequenceClassification",
                "task": "sentiment-analysis",
                "description": "Twitter RoBERTa for sentiment analysis",
                "loaded": False
            }
        }
    
    async def load_model(self, model_key: str) -> Dict[str, Any]:
        """
        Load a specific model directly (NO PIPELINE)
        
        Args:
            model_key: Key of the model to load
            
        Returns:
            Status dict with model info
        """
        if model_key not in self.model_configs:
            raise ValueError(f"Unknown model: {model_key}")
        
        config = self.model_configs[model_key]
        
        # Check if already loaded
        if model_key in self.models and model_key in self.tokenizers:
            logger.info(f"✅ Model {model_key} already loaded")
            config["loaded"] = True
            return {
                "success": True,
                "model_key": model_key,
                "model_id": config["model_id"],
                "status": "already_loaded",
                "device": self.device
            }
        
        try:
            logger.info(f"📥 Loading model: {config['model_id']} (NO PIPELINE)")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                config["model_id"],
                cache_dir=self.cache_dir
            )
            
            # Load model based on class
            if config["model_class"] == "BertForSequenceClassification":
                model = BertForSequenceClassification.from_pretrained(
                    config["model_id"],
                    cache_dir=self.cache_dir
                )
            elif config["model_class"] == "AutoModelForSequenceClassification":
                model = AutoModelForSequenceClassification.from_pretrained(
                    config["model_id"],
                    cache_dir=self.cache_dir
                )
            elif config["model_class"] == "AutoModelForCausalLM":
                model = AutoModelForCausalLM.from_pretrained(
                    config["model_id"],
                    cache_dir=self.cache_dir
                )
            else:
                raise ValueError(f"Unknown model class: {config['model_class']}")
            
            # Move model to device
            model.to(self.device)
            model.eval()  # Set to evaluation mode
            
            # Store model and tokenizer
            self.models[model_key] = model
            self.tokenizers[model_key] = tokenizer
            config["loaded"] = True
            
            logger.info(f"✅ Model loaded successfully: {config['model_id']}")
            
            return {
                "success": True,
                "model_key": model_key,
                "model_id": config["model_id"],
                "status": "loaded",
                "device": self.device,
                "task": config["task"]
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to load model {model_key}: {e}")
            raise Exception(f"Failed to load model {model_key}: {str(e)}")
    
    async def load_all_models(self) -> Dict[str, Any]:
        """
        Load all configured models
        
        Returns:
            Status dict with all models
        """
        results = []
        success_count = 0
        
        for model_key in self.model_configs.keys():
            try:
                result = await self.load_model(model_key)
                results.append(result)
                if result["success"]:
                    success_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to load {model_key}: {e}")
                results.append({
                    "success": False,
                    "model_key": model_key,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "total_models": len(self.model_configs),
            "loaded_models": success_count,
            "failed_models": len(self.model_configs) - success_count,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def predict_sentiment(
        self,
        text: str,
        model_key: str = "cryptobert_elkulako",
        max_length: int = 512
    ) -> Dict[str, Any]:
        """
        Predict sentiment directly (NO PIPELINE)
        
        Args:
            text: Input text
            model_key: Model to use
            max_length: Maximum sequence length
            
        Returns:
            Sentiment prediction
        """
        # Ensure model is loaded
        if model_key not in self.models:
            await self.load_model(model_key)
        
        try:
            model = self.models[model_key]
            tokenizer = self.tokenizers[model_key]
            
            # Tokenize input - NO PIPELINE
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=max_length
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Forward pass - Direct inference
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
            
            # Get predictions - Direct calculation
            probs = torch.softmax(logits, dim=1)
            predicted_class = torch.argmax(probs, dim=1).item()
            confidence = probs[0][predicted_class].item()
            
            # Map class to label (standard 3-class sentiment)
            label_map = {0: "negative", 1: "neutral", 2: "positive"}
            
            # Try to get actual labels from model config
            if hasattr(model.config, "id2label"):
                label = model.config.id2label.get(predicted_class, label_map.get(predicted_class, "unknown"))
            else:
                label = label_map.get(predicted_class, "unknown")
            
            # Get all class probabilities
            all_probs = {
                label_map.get(i, f"class_{i}"): probs[0][i].item()
                for i in range(probs.shape[1])
            }
            
            logger.info(f"✅ Sentiment predicted: {label} (confidence: {confidence:.4f})")
            
            return {
                "success": True,
                "text": text[:100] + "..." if len(text) > 100 else text,
                "sentiment": label,
                "label": label,
                "score": confidence,
                "confidence": confidence,
                "all_scores": all_probs,
                "model": model_key,
                "model_id": self.model_configs[model_key]["model_id"],
                "inference_type": "direct_no_pipeline",
                "device": self.device,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Sentiment prediction failed: {e}")
            raise Exception(f"Sentiment prediction failed: {str(e)}")
    
    async def batch_predict_sentiment(
        self,
        texts: List[str],
        model_key: str = "cryptobert_elkulako",
        max_length: int = 512
    ) -> Dict[str, Any]:
        """
        Batch sentiment prediction (NO PIPELINE)
        
        Args:
            texts: List of input texts
            model_key: Model to use
            max_length: Maximum sequence length
            
        Returns:
            Batch predictions
        """
        # Ensure model is loaded
        if model_key not in self.models:
            await self.load_model(model_key)
        
        try:
            model = self.models[model_key]
            tokenizer = self.tokenizers[model_key]
            
            # Tokenize all inputs - NO PIPELINE
            inputs = tokenizer(
                texts,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=max_length
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Forward pass - Direct inference
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
            
            # Get predictions - Direct calculation
            probs = torch.softmax(logits, dim=1)
            predicted_classes = torch.argmax(probs, dim=1).cpu().numpy()
            confidences = probs.max(dim=1).values.cpu().numpy()
            
            # Map classes to labels
            label_map = {0: "negative", 1: "neutral", 2: "positive"}
            
            # Build results
            results = []
            for i, text in enumerate(texts):
                predicted_class = predicted_classes[i]
                confidence = confidences[i]
                
                if hasattr(model.config, "id2label"):
                    label = model.config.id2label.get(predicted_class, label_map.get(predicted_class, "unknown"))
                else:
                    label = label_map.get(predicted_class, "unknown")
                
                results.append({
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "sentiment": label,
                    "label": label,
                    "score": float(confidence),
                    "confidence": float(confidence)
                })
            
            logger.info(f"✅ Batch sentiment predicted for {len(texts)} texts")
            
            return {
                "success": True,
                "count": len(results),
                "results": results,
                "model": model_key,
                "model_id": self.model_configs[model_key]["model_id"],
                "inference_type": "direct_batch_no_pipeline",
                "device": self.device,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Batch sentiment prediction failed: {e}")
            raise Exception(f"Batch sentiment prediction failed: {str(e)}")
    
    def get_loaded_models(self) -> Dict[str, Any]:
        """
        Get list of loaded models
        
        Returns:
            Dict with loaded models info
        """
        models_info = []
        for model_key, config in self.model_configs.items():
            models_info.append({
                "model_key": model_key,
                "model_id": config["model_id"],
                "task": config["task"],
                "description": config["description"],
                "loaded": model_key in self.models,
                "device": self.device if model_key in self.models else None
            })
        
        return {
            "success": True,
            "total_configured": len(self.model_configs),
            "total_loaded": len(self.models),
            "device": self.device,
            "models": models_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def unload_model(self, model_key: str) -> Dict[str, Any]:
        """
        Unload a specific model from memory
        
        Args:
            model_key: Key of the model to unload
            
        Returns:
            Status dict
        """
        if model_key not in self.models:
            return {
                "success": False,
                "model_key": model_key,
                "message": "Model not loaded"
            }
        
        try:
            # Remove model and tokenizer
            del self.models[model_key]
            del self.tokenizers[model_key]
            
            # Update config
            self.model_configs[model_key]["loaded"] = False
            
            # Clear CUDA cache if using GPU
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            logger.info(f"✅ Model unloaded: {model_key}")
            
            return {
                "success": True,
                "model_key": model_key,
                "message": "Model unloaded successfully"
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to unload model {model_key}: {e}")
            return {
                "success": False,
                "model_key": model_key,
                "error": str(e)
            }


# Global instance
direct_model_loader = DirectModelLoader()


# Export
__all__ = ["DirectModelLoader", "direct_model_loader"]
