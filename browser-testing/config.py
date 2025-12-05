"""
Test configuration with environment detection for browser automation testing.
Supports both local development and HuggingFace Spaces deployment.
"""
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class TestConfig:
    """Configuration for browser automation tests"""
    base_url: str
    websocket_url: Optional[str]
    environment: str  # 'local' or 'huggingface'
    websocket_enabled: bool
    timeout_page_load: int = 30
    timeout_action: int = 10
    retry_attempts: int = 3
    retry_delay: int = 2
    screenshot_on_error: bool = True


def detect_environment() -> TestConfig:
    """
    Auto-detect environment and return appropriate configuration.
    
    Returns:
        TestConfig: Configuration object with environment-specific settings
    """
    # Check for HuggingFace Spaces environment variables
    is_hf = os.getenv('HF_SPACES') == 'true' or os.getenv('SPACE_ID') is not None
    
    # Allow override via BASE_URL environment variable
    base_url_override = os.getenv('BASE_URL')
    
    if is_hf or (base_url_override and 'huggingface.co' in base_url_override):
        # HuggingFace Spaces configuration
        base_url = base_url_override or 'https://huggingface.co/spaces/Really-amin/Datasourceforcryptocurrency-2'
        return TestConfig(
            base_url=base_url,
            websocket_url=None,
            environment='huggingface',
            websocket_enabled=False
        )
    else:
        # Local development configuration
        base_url = base_url_override or 'http://localhost:7860'
        ws_protocol = 'wss' if 'https' in base_url else 'ws'
        ws_host = base_url.replace('http://', '').replace('https://', '')
        
        return TestConfig(
            base_url=base_url,
            websocket_url=f'{ws_protocol}://{ws_host}/ws',
            environment='local',
            websocket_enabled=True
        )


def get_config() -> TestConfig:
    """Get the current test configuration"""
    return detect_environment()

