#!/usr/bin/env python3
"""
Configuration Manager with Hot Reload
======================================
مدیریت فایل‌های پیکربندی با قابلیت reload خودکار در صورت تغییر
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import threading
import time

logger = logging.getLogger(__name__)


class ConfigFileHandler(FileSystemEventHandler):
    """Handler for config file changes."""

    def __init__(self, config_manager: 'ConfigManager'):
        """
        Initialize config file handler.
        
        Args:
            config_manager: Reference to ConfigManager instance
        """
        self.config_manager = config_manager
        self.last_modified = {}

    def on_modified(self, event: FileModifiedEvent):
        """Handle file modification event."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if this is a config file we're watching
        if file_path in self.config_manager.config_files:
            # Prevent multiple reloads for the same file
            current_time = time.time()
            last_time = self.last_modified.get(file_path, 0)

            # Debounce: ignore if modified within last 2 seconds
            if current_time - last_time < 2.0:
                return

            self.last_modified[file_path] = current_time

            logger.info(f"Config file modified: {file_path}")
            self.config_manager.reload_config(file_path)


class ConfigManager:
    """Manager for configuration files with hot reload support."""

    def __init__(self, config_dir: str = "config"):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory containing config files
        """
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.config_files: Dict[Path, str] = {}
        self.observers: Dict[str, Observer] = {}
        self.reload_callbacks: Dict[str, list] = {}
        self.lock = threading.Lock()

        # Define config files to watch
        self._setup_config_files()

        # Load initial configs
        self.load_all_configs()

        # Start file watchers
        self.start_watching()

    def _setup_config_files(self):
        """Setup config file paths."""
        self.config_files = {
            self.config_dir / "scoring.config.json": "scoring",
            self.config_dir / "strategy.config.json": "strategy"
        }

    def load_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a configuration file.
        
        Args:
            config_name: Name of the config (e.g., "scoring", "strategy")
        
        Returns:
            Config dictionary or None if not found
        """
        config_path = None
        for path, name in self.config_files.items():
            if name == config_name:
                config_path = path
                break

        if not config_path or not config_path.exists():
            logger.warning(f"Config file not found: {config_name}")
            return None

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            with self.lock:
                self.configs[config_name] = config
            
            logger.info(f"Loaded config: {config_name}")
            return config

        except Exception as e:
            logger.error(f"Error loading config {config_name}: {e}", exc_info=True)
            return None

    def load_all_configs(self):
        """Load all configuration files."""
        logger.info("Loading all configuration files...")

        for config_path, config_name in self.config_files.items():
            self.load_config(config_name)

        logger.info(f"Loaded {len(self.configs)} configuration files")

    def reload_config(self, config_path: Path):
        """
        Reload a specific configuration file.
        
        Args:
            config_path: Path to the config file
        """
        if config_path not in self.config_files:
            return

        config_name = self.config_files[config_path]
        logger.info(f"Reloading config: {config_name}")

        old_config = self.configs.get(config_name)
        new_config = self.load_config(config_name)

        if new_config and new_config != old_config:
            logger.info(f"Config {config_name} reloaded successfully")

            # Call registered callbacks
            if config_name in self.reload_callbacks:
                for callback in self.reload_callbacks[config_name]:
                    try:
                        callback(new_config, old_config)
                    except Exception as e:
                        logger.error(f"Error in reload callback: {e}", exc_info=True)

    def get_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a configuration by name.
        
        Args:
            config_name: Name of the config
        
        Returns:
            Config dictionary or None
        """
        with self.lock:
            return self.configs.get(config_name)

    def register_reload_callback(
        self,
        config_name: str,
        callback: Callable[[Dict[str, Any], Optional[Dict[str, Any]]], None]
    ):
        """
        Register a callback to be called when config is reloaded.
        
        Args:
            config_name: Name of the config
            callback: Callback function (new_config, old_config) -> None
        """
        if config_name not in self.reload_callbacks:
            self.reload_callbacks[config_name] = []

        self.reload_callbacks[config_name].append(callback)
        logger.info(f"Registered reload callback for {config_name}")

    def start_watching(self):
        """Start watching config files for changes."""
        if not self.config_dir.exists():
            logger.warning(f"Config directory does not exist: {self.config_dir}")
            return

        event_handler = ConfigFileHandler(self)

        # Create observer for each config file's directory
        watched_dirs = set(path.parent for path in self.config_files.keys())

        try:
            for watch_dir in watched_dirs:
                observer = Observer()
                observer.schedule(event_handler, str(watch_dir), recursive=False)
                observer.start()

                self.observers[str(watch_dir)] = observer
                logger.info(f"Started watching directory: {watch_dir}")
        except Exception as e:
            logger.warning(f"Failed to start file watcher (hot reload disabled): {e}")
            # Continue without watching - hot reload won't work but server will run

    def stop_watching(self):
        """Stop watching config files."""
        for observer in self.observers.values():
            observer.stop()
            observer.join()

        self.observers.clear()
        logger.info("Stopped watching config files")

    def manual_reload(self, config_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Manually reload configuration files.
        
        Args:
            config_name: Optional specific config to reload (reloads all if None)
        
        Returns:
            Dict with reload status
        """
        if config_name:
            config_path = None
            for path, name in self.config_files.items():
                if name == config_name:
                    config_path = path
                    break

            if config_path:
                self.reload_config(config_path)
                return {
                    "success": True,
                    "message": f"Config {config_name} reloaded",
                    "config": config_name
                }
            else:
                return {
                    "success": False,
                    "message": f"Config {config_name} not found"
                }
        else:
            # Reload all configs
            for config_name in self.config_files.values():
                self.load_config(config_name)

            return {
                "success": True,
                "message": "All configs reloaded",
                "configs": list(self.config_files.values())
            }

    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all loaded configurations."""
        with self.lock:
            return self.configs.copy()


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_dir: str = "config") -> ConfigManager:
    """
    Get or create global config manager instance.
    
    Args:
        config_dir: Config directory path
    
    Returns:
        ConfigManager instance
    """
    global _config_manager

    if _config_manager is None:
        _config_manager = ConfigManager(config_dir)

    return _config_manager

