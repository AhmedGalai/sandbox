"""
Configuration module for the Ollama multi-agent system.

Provides:
- Settings: Centralized configuration management using Pydantic
- get_settings(): Get or create global settings instance
"""

from .settings import Settings, get_settings, reset_settings

__all__ = [
    "Settings",
    "get_settings",
    "reset_settings",
]
