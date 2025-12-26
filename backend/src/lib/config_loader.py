"""
Configuration loader module for managing environment variables and application settings.
"""
import os
from typing import Dict, Optional
from dotenv import load_dotenv


def load_config() -> Dict[str, str]:
    """
    Load configuration from environment variables.
    First loads from .env file if it exists, then reads from actual environment.
    """
    # Load from .env file if it exists
    load_dotenv()
    
    # Define required and optional configuration keys
    config = {}
    
    # Required keys
    required_keys = [
        'COHERE_API_KEY',
        'QDRANT_URL',
        'QDRANT_API_KEY',
        'GEMINI_API_KEY'
    ]
    
    # Optional keys with defaults
    optional_defaults = {
        'QDRANT_COLLECTION_NAME': 'documents',
        'TOP_K_DEFAULT': '5',
        'LOG_LEVEL': 'INFO'
    }
    
    # Load required keys
    for key in required_keys:
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Required environment variable {key} is not set")
        config[key] = value
    
    # Load optional keys with defaults
    for key, default_value in optional_defaults.items():
        config[key] = os.getenv(key, default_value)
    
    return config


# Singleton instance if needed
_config_instance: Optional[Dict[str, str]] = None


def get_config() -> Dict[str, str]:
    """
    Get configuration as a singleton instance.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance