"""
Feature Flags System
Allows dynamic toggling of application modules and features
"""
from typing import Dict, Any
import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FeatureFlagManager:
    """Manage application feature flags"""

    DEFAULT_FLAGS = {
        "enableWhaleTracking": True,
        "enableMarketOverview": True,
        "enableFearGreedIndex": True,
        "enableNewsFeed": True,
        "enableSentimentAnalysis": True,
        "enableMlPredictions": False,  # Disabled by default (requires HF setup)
        "enableProxyAutoMode": True,
        "enableDefiProtocols": True,
        "enableTrendingCoins": True,
        "enableGlobalStats": True,
        "enableProviderRotation": True,
        "enableWebSocketStreaming": True,
        "enableDatabaseLogging": True,
        "enableRealTimeAlerts": False,  # New feature - not yet implemented
        "enableAdvancedCharts": True,
        "enableExportFeatures": True,
        "enableCustomProviders": True,
        "enablePoolManagement": True,
        "enableHFIntegration": True,
    }

    def __init__(self, storage_path: str = "data/feature_flags.json"):
        """
        Initialize feature flag manager

        Args:
            storage_path: Path to persist feature flags
        """
        self.storage_path = Path(storage_path)
        self.flags = self.DEFAULT_FLAGS.copy()
        self.load_flags()

    def load_flags(self):
        """Load feature flags from storage"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    saved_flags = json.load(f)
                # Merge saved flags with defaults (in case new flags were added)
                self.flags.update(saved_flags.get('flags', {}))
                logger.info(f"Loaded feature flags from {self.storage_path}")
            else:
                # Create storage directory if it doesn't exist
                self.storage_path.parent.mkdir(parents=True, exist_ok=True)
                self.save_flags()
                logger.info("Initialized default feature flags")
        except Exception as e:
            logger.error(f"Error loading feature flags: {e}")
            self.flags = self.DEFAULT_FLAGS.copy()

    def save_flags(self):
        """Save feature flags to storage"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'flags': self.flags,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info("Feature flags saved successfully")
        except Exception as e:
            logger.error(f"Error saving feature flags: {e}")

    def get_all_flags(self) -> Dict[str, bool]:
        """Get all feature flags"""
        return self.flags.copy()

    def get_flag(self, flag_name: str) -> bool:
        """
        Get a specific feature flag value

        Args:
            flag_name: Name of the flag

        Returns:
            bool: Flag value (defaults to False if not found)
        """
        return self.flags.get(flag_name, False)

    def set_flag(self, flag_name: str, value: bool) -> bool:
        """
        Set a feature flag value

        Args:
            flag_name: Name of the flag
            value: New value (True/False)

        Returns:
            bool: Success status
        """
        try:
            self.flags[flag_name] = bool(value)
            self.save_flags()
            logger.info(f"Feature flag '{flag_name}' set to {value}")
            return True
        except Exception as e:
            logger.error(f"Error setting feature flag: {e}")
            return False

    def update_flags(self, updates: Dict[str, bool]) -> bool:
        """
        Update multiple flags at once

        Args:
            updates: Dictionary of flag name -> value pairs

        Returns:
            bool: Success status
        """
        try:
            for flag_name, value in updates.items():
                self.flags[flag_name] = bool(value)
            self.save_flags()
            logger.info(f"Updated {len(updates)} feature flags")
            return True
        except Exception as e:
            logger.error(f"Error updating feature flags: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """Reset all flags to default values"""
        try:
            self.flags = self.DEFAULT_FLAGS.copy()
            self.save_flags()
            logger.info("Feature flags reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Error resetting feature flags: {e}")
            return False

    def is_enabled(self, flag_name: str) -> bool:
        """
        Check if a feature is enabled (alias for get_flag)

        Args:
            flag_name: Name of the flag

        Returns:
            bool: True if enabled, False otherwise
        """
        return self.get_flag(flag_name)

    def get_enabled_features(self) -> Dict[str, bool]:
        """Get only enabled features"""
        return {k: v for k, v in self.flags.items() if v is True}

    def get_disabled_features(self) -> Dict[str, bool]:
        """Get only disabled features"""
        return {k: v for k, v in self.flags.items() if v is False}

    def get_flag_count(self) -> Dict[str, int]:
        """Get count of enabled/disabled flags"""
        enabled = sum(1 for v in self.flags.values() if v)
        disabled = len(self.flags) - enabled
        return {
            'total': len(self.flags),
            'enabled': enabled,
            'disabled': disabled
        }

    def get_feature_info(self) -> Dict[str, Any]:
        """Get comprehensive feature flag information"""
        counts = self.get_flag_count()
        return {
            'flags': self.flags,
            'counts': counts,
            'enabled_features': list(self.get_enabled_features().keys()),
            'disabled_features': list(self.get_disabled_features().keys()),
            'storage_path': str(self.storage_path),
            'last_loaded': datetime.now().isoformat()
        }


# Global instance
feature_flags = FeatureFlagManager()


# Convenience functions
def is_feature_enabled(flag_name: str) -> bool:
    """Check if a feature is enabled"""
    return feature_flags.is_enabled(flag_name)


def get_all_feature_flags() -> Dict[str, bool]:
    """Get all feature flags"""
    return feature_flags.get_all_flags()


def set_feature_flag(flag_name: str, value: bool) -> bool:
    """Set a feature flag"""
    return feature_flags.set_flag(flag_name, value)


def update_feature_flags(updates: Dict[str, bool]) -> bool:
    """Update multiple feature flags"""
    return feature_flags.update_flags(updates)
