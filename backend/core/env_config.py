#!/usr/bin/env python3
"""
Environment Configuration Handler
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULES:
- Use environment variables for ALL configuration
- If variable is missing: log warning and disable only affected feature
- Continue running safely with fallback values
- Reference .env.example for expected variable names
"""

import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file if it exists
load_dotenv()

# Load .env.example as reference
ENV_EXAMPLE_PATH = Path(__file__).resolve().parent.parent.parent / ".env.example"


class EnvConfig:
    """
    Safe environment configuration with fallback handling
    """
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._missing_vars: List[str] = []
        self._load_config()
    
    def _load_config(self):
        """Load all configuration from environment"""
        logger.info("📋 Loading environment configuration...")
        
        # Market Data APIs
        self._config["COINMARKETCAP_KEYS"] = self._get_list_var("COINMARKETCAP_KEY_1", "COINMARKETCAP_KEY_2")
        self._config["CRYPTOCOMPARE_KEY"] = self._get_var("CRYPTOCOMPARE_KEY")
        self._config["NOMICS_KEY"] = self._get_var("NOMICS_KEY")
        
        # Blockchain APIs
        self._config["ALCHEMY_KEY"] = self._get_var("ALCHEMY_KEY")
        self._config["BSCSCAN_KEY"] = self._get_var("BSCSCAN_KEY")
        self._config["ETHERSCAN_KEYS"] = self._get_list_var("ETHERSCAN_KEY_1", "ETHERSCAN_KEY_2")
        self._config["INFURA_PROJECT_ID"] = self._get_var("INFURA_PROJECT_ID")
        self._config["TRONSCAN_KEY"] = self._get_var("TRONSCAN_KEY")
        
        # News APIs
        self._config["CRYPTOPANIC_TOKEN"] = self._get_var("CRYPTOPANIC_TOKEN")
        self._config["NEWSAPI_KEY"] = self._get_var("NEWSAPI_KEY")
        
        # Sentiment APIs
        self._config["GLASSNODE_KEY"] = self._get_var("GLASSNODE_KEY")
        self._config["LUNARCRUSH_KEY"] = self._get_var("LUNARCRUSH_KEY")
        self._config["SANTIMENT_KEY"] = self._get_var("SANTIMENT_KEY")
        self._config["THETIE_KEY"] = self._get_var("THETIE_KEY")
        
        # On-Chain APIs
        self._config["COVALENT_KEY"] = self._get_var("COVALENT_KEY")
        self._config["DUNE_KEY"] = self._get_var("DUNE_KEY")
        self._config["MORALIS_KEY"] = self._get_var("MORALIS_KEY")
        self._config["NANSEN_KEY"] = self._get_var("NANSEN_KEY")
        
        # Whale Tracking
        self._config["ARKHAM_KEY"] = self._get_var("ARKHAM_KEY")
        self._config["WHALE_ALERT_KEY"] = self._get_var("WHALE_ALERT_KEY")
        
        # HuggingFace
        self._config["HF_TOKEN"] = self._get_var("HF_TOKEN")
        
        # Server Configuration
        self._config["HOST"] = os.getenv("HOST", "0.0.0.0")
        self._config["PORT"] = int(os.getenv("PORT", os.getenv("HF_PORT", "7860")))
        self._config["DEBUG"] = os.getenv("DEBUG", "false").lower() == "true"
        
        # Log summary
        total_vars = len(self._config)
        missing_count = len(self._missing_vars)
        configured_count = total_vars - missing_count
        
        logger.info(f"✅ Environment config loaded: {configured_count}/{total_vars} variables configured")
        
        if self._missing_vars:
            logger.warning(
                f"⚠️ Missing {missing_count} environment variables (features will be disabled):\n"
                f"   {', '.join(self._missing_vars[:10])}"
                + (f" ...and {len(self._missing_vars) - 10} more" if len(self._missing_vars) > 10 else "")
            )
    
    def _get_var(self, var_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with fallback
        
        Args:
            var_name: Name of environment variable
            default: Default value if not set
        
        Returns:
            Variable value or default
        """
        value = os.getenv(var_name, default)
        
        # Check if value is placeholder or empty
        if not value or value in ["your_key_here", "null", "None", ""]:
            if var_name not in self._missing_vars:
                self._missing_vars.append(var_name)
            return None
        
        return value
    
    def _get_list_var(self, *var_names: str) -> List[str]:
        """
        Get multiple environment variables as a list (e.g., multiple API keys)
        
        Returns:
            List of non-empty values
        """
        values = []
        for var_name in var_names:
            value = self._get_var(var_name)
            if value:
                values.append(value)
        return values
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled (has required configuration)
        
        Args:
            feature: Feature name (e.g., "COINMARKETCAP", "ETHERSCAN")
        
        Returns:
            True if feature is enabled
        """
        feature_upper = feature.upper()
        
        # Check for keys or key lists
        if feature_upper in self._config:
            value = self._config[feature_upper]
            if isinstance(value, list):
                return len(value) > 0
            return value is not None
        
        # Check for key patterns (e.g., "ETHERSCAN_KEYS")
        key_variants = [
            feature_upper,
            f"{feature_upper}_KEY",
            f"{feature_upper}_KEYS",
            f"{feature_upper}_TOKEN",
            f"{feature_upper}_API_KEY"
        ]
        
        for variant in key_variants:
            if variant in self._config:
                value = self._config[variant]
                if isinstance(value, list):
                    return len(value) > 0
                return value is not None
        
        return False
    
    def get_feature_config(self, feature: str) -> Dict[str, Any]:
        """
        Get all configuration for a specific feature
        
        Returns:
            Dictionary with feature configuration
        """
        feature_upper = feature.upper()
        result = {}
        
        for key, value in self._config.items():
            if key.startswith(feature_upper):
                result[key] = value
        
        return {
            "enabled": self.is_feature_enabled(feature),
            "config": result
        }
    
    def get_all_features(self) -> Dict[str, bool]:
        """
        Get status of all features
        
        Returns:
            Dictionary mapping feature names to enabled status
        """
        # Extract unique feature names from config keys
        features = set()
        for key in self._config.keys():
            # Remove suffixes to get base feature name
            base = key.replace("_KEY", "").replace("_KEYS", "").replace("_TOKEN", "").replace("_API_KEY", "")
            features.add(base)
        
        return {
            feature: self.is_feature_enabled(feature)
            for feature in sorted(features)
        }
    
    def get_missing_vars(self) -> List[str]:
        """Get list of missing environment variables"""
        return self._missing_vars.copy()
    
    def reload(self):
        """Reload configuration from environment"""
        self._config.clear()
        self._missing_vars.clear()
        load_dotenv(override=True)
        self._load_config()
        logger.info("🔄 Environment configuration reloaded")


# Global configuration instance
env_config = EnvConfig()


# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return env_config.get(key, default)


def is_feature_enabled(feature: str) -> bool:
    """Check if feature is enabled"""
    return env_config.is_feature_enabled(feature)


def get_feature_config(feature: str) -> Dict[str, Any]:
    """Get feature configuration"""
    return env_config.get_feature_config(feature)


# Export
__all__ = [
    "EnvConfig",
    "env_config",
    "get_config",
    "is_feature_enabled",
    "get_feature_config"
]
