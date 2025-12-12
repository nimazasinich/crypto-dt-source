"""
Environment Detection Utility
Detects GPU availability, HuggingFace Space environment, and system capabilities
"""

import os
import platform
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class EnvironmentDetector:
    """Detect runtime environment and capabilities"""
    
    def __init__(self):
        self._gpu_available: Optional[bool] = None
        self._is_huggingface: Optional[bool] = None
        self._transformers_available: Optional[bool] = None
        self._torch_available: Optional[bool] = None
        
    def is_huggingface_space(self) -> bool:
        """Detect if running on HuggingFace Space"""
        if self._is_huggingface is None:
            # Check for HF Space environment variables
            self._is_huggingface = bool(
                os.getenv("SPACE_ID") or 
                os.getenv("SPACE_AUTHOR_NAME") or
                os.getenv("SPACE_HOST")
            )
        return self._is_huggingface
    
    def has_gpu(self) -> bool:
        """Detect if GPU is available"""
        if self._gpu_available is None:
            self._gpu_available = False
            
            try:
                import torch
                self._gpu_available = torch.cuda.is_available()
                if self._gpu_available:
                    gpu_name = torch.cuda.get_device_name(0)
                    logger.info(f"✅ GPU detected: {gpu_name}")
                else:
                    logger.info("ℹ️  No GPU detected - using CPU")
            except ImportError:
                logger.info("ℹ️  PyTorch not installed - assuming no GPU")
                self._gpu_available = False
            except Exception as e:
                logger.warning(f"Error detecting GPU: {e}")
                self._gpu_available = False
                
        return self._gpu_available
    
    def is_torch_available(self) -> bool:
        """Check if PyTorch is installed"""
        if self._torch_available is None:
            try:
                import torch
                self._torch_available = True
                logger.info(f"✅ PyTorch {torch.__version__} available")
            except ImportError:
                self._torch_available = False
                logger.info("ℹ️  PyTorch not installed")
        return self._torch_available
    
    def is_transformers_available(self) -> bool:
        """Check if Transformers library is installed"""
        if self._transformers_available is None:
            try:
                import transformers
                self._transformers_available = True
                logger.info(f"✅ Transformers {transformers.__version__} available")
            except ImportError:
                self._transformers_available = False
                logger.info("ℹ️  Transformers not installed")
        return self._transformers_available
    
    def should_use_ai_models(self) -> bool:
        """
        Determine if AI models should be used
        Only use if:
        - Running on HuggingFace Space, OR
        - Transformers is installed AND (GPU available OR explicitly enabled)
        """
        if self.is_huggingface_space():
            logger.info("✅ HuggingFace Space detected - AI models will be used")
            return True
        
        if not self.is_transformers_available():
            logger.info("ℹ️  Transformers not available - using fallback mode")
            return False
        
        # If transformers installed but not HF Space, check GPU or explicit flag
        use_ai = os.getenv("USE_AI_MODELS", "").lower() == "true" or self.has_gpu()
        
        if use_ai:
            logger.info("✅ AI models enabled (GPU or USE_AI_MODELS=true)")
        else:
            logger.info("ℹ️  AI models disabled (no GPU, set USE_AI_MODELS=true to force)")
            
        return use_ai
    
    def get_device(self) -> str:
        """Get the device to use for AI models"""
        if self.has_gpu():
            return "cuda"
        return "cpu"
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get comprehensive environment information"""
        info = {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "is_huggingface_space": self.is_huggingface_space(),
            "torch_available": self.is_torch_available(),
            "transformers_available": self.is_transformers_available(),
            "gpu_available": self.has_gpu(),
            "device": self.get_device() if self.is_torch_available() else "none",
            "should_use_ai": self.should_use_ai_models()
        }
        
        # Add GPU details if available
        if self.has_gpu():
            try:
                import torch
                info["gpu_name"] = torch.cuda.get_device_name(0)
                info["gpu_count"] = torch.cuda.device_count()
                info["cuda_version"] = torch.version.cuda
            except:
                pass
        
        # Add HF Space info if available
        if self.is_huggingface_space():
            info["space_id"] = os.getenv("SPACE_ID", "unknown")
            info["space_author"] = os.getenv("SPACE_AUTHOR_NAME", "unknown")
        
        return info
    
    def log_environment(self):
        """Log environment information"""
        info = self.get_environment_info()
        
        logger.info("=" * 70)
        logger.info("🔍 ENVIRONMENT DETECTION:")
        logger.info(f"   Platform: {info['platform']}")
        logger.info(f"   Python: {info['python_version']}")
        logger.info(f"   HuggingFace Space: {'Yes' if info['is_huggingface_space'] else 'No'}")
        logger.info(f"   PyTorch: {'Yes' if info['torch_available'] else 'No'}")
        logger.info(f"   Transformers: {'Yes' if info['transformers_available'] else 'No'}")
        logger.info(f"   GPU: {'Yes' if info['gpu_available'] else 'No'}")
        if info['gpu_available'] and 'gpu_name' in info:
            logger.info(f"   GPU Name: {info['gpu_name']}")
        logger.info(f"   Device: {info['device']}")
        logger.info(f"   AI Models: {'Enabled' if info['should_use_ai'] else 'Disabled (using fallback)'}")
        logger.info("=" * 70)


# Global instance
_env_detector = EnvironmentDetector()


def get_environment_detector() -> EnvironmentDetector:
    """Get global environment detector instance"""
    return _env_detector


def is_huggingface_space() -> bool:
    """Quick check if running on HuggingFace Space"""
    return _env_detector.is_huggingface_space()


def has_gpu() -> bool:
    """Quick check if GPU is available"""
    return _env_detector.has_gpu()


def should_use_ai_models() -> bool:
    """Quick check if AI models should be used"""
    return _env_detector.should_use_ai_models()


def get_device() -> str:
    """Get device for AI models"""
    return _env_detector.get_device()


__all__ = [
    'EnvironmentDetector',
    'get_environment_detector',
    'is_huggingface_space',
    'has_gpu',
    'should_use_ai_models',
    'get_device'
]
