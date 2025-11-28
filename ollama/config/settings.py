"""
Configuration management using Pydantic BaseSettings.
Loads settings from environment variables and YAML config files.
"""

import logging
from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # API Configuration
    ollama_host: str = Field(default="http://localhost:11434", alias="OLLAMA_HOST")
    timeout: float = Field(default=120.0, alias="TIMEOUT")

    # Concurrency Configuration
    max_concurrent_agents: int = Field(default=3, alias="MAX_CONCURRENT_AGENTS")

    # Model Configuration
    default_model: str = Field(default="llama3.2:3b", alias="DEFAULT_MODEL")
    model_mappings: Dict[str, str] = Field(default_factory=dict)

    # Logging Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        alias="LOG_FORMAT"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **data):
        """Initialize settings and load model mappings from YAML."""
        super().__init__(**data)
        self._load_model_mappings()

    def _load_model_mappings(self) -> None:
        """Load model mappings from models.yaml configuration file."""
        config_path = Path(__file__).parent / "models.yaml"

        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f) or {}
                    self.model_mappings = config.get("models", {})
                    logger.info(f"Loaded model mappings from {config_path}")
            except Exception as e:
                logger.warning(
                    f"Failed to load model mappings from {config_path}: {e}"
                )
        else:
            logger.debug(f"Model mappings file not found at {config_path}")

    def get_model_for_agent(self, agent_name: str) -> str:
        """
        Get the model assigned to a specific agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Model name for the agent, or default model if not configured
        """
        return self.model_mappings.get(agent_name, self.default_model)

    def validate_settings(self) -> bool:
        """
        Validate that all required settings are properly configured.

        Returns:
            True if all settings are valid

        Raises:
            ValueError: If required settings are invalid
        """
        if not self.ollama_host:
            raise ValueError("OLLAMA_HOST must be configured")

        if self.timeout <= 0:
            raise ValueError("TIMEOUT must be greater than 0")

        if self.max_concurrent_agents < 1:
            raise ValueError("MAX_CONCURRENT_AGENTS must be at least 1")

        logger.info("Settings validation passed")
        return True


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create the global settings instance.

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.validate_settings()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (useful for testing)."""
    global _settings
    _settings = None
