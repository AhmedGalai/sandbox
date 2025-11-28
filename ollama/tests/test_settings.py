"""
Tests for configuration settings.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from config.settings import Settings, get_settings, reset_settings


def test_settings_defaults():
    """Test default settings."""
    settings = Settings()

    assert settings.ollama_host == "http://localhost:11434"
    assert settings.timeout == 120.0
    assert settings.max_concurrent_agents == 3
    assert settings.default_model == "llama3.2:3b"


def test_settings_from_env(monkeypatch):
    """Test settings from environment variables."""
    monkeypatch.setenv("OLLAMA_HOST", "http://example.com:11434")
    monkeypatch.setenv("TIMEOUT", "60")
    monkeypatch.setenv("MAX_CONCURRENT_AGENTS", "5")

    reset_settings()
    settings = Settings()

    assert settings.ollama_host == "http://example.com:11434"
    assert settings.timeout == 60.0
    assert settings.max_concurrent_agents == 5


def test_settings_validation():
    """Test settings validation."""
    settings = Settings()
    assert settings.validate_settings() is True


def test_settings_validation_invalid_host():
    """Test validation with invalid host."""
    with patch.object(Settings, "_load_model_mappings"):
        with pytest.raises(ValueError):
            Settings(ollama_host="")


def test_settings_validation_invalid_timeout():
    """Test validation with invalid timeout."""
    with patch.object(Settings, "_load_model_mappings"):
        with pytest.raises(ValueError):
            Settings(timeout=-1)


def test_settings_validation_invalid_concurrency():
    """Test validation with invalid max_concurrent_agents."""
    with patch.object(Settings, "_load_model_mappings"):
        with pytest.raises(ValueError):
            Settings(max_concurrent_agents=0)


def test_get_model_for_agent():
    """Test getting model for specific agent."""
    settings = Settings()
    settings.model_mappings = {
        "researcher": "qwen2.5:7b",
        "developer": "llama3.2:3b",
    }

    assert settings.get_model_for_agent("researcher") == "qwen2.5:7b"
    assert settings.get_model_for_agent("developer") == "llama3.2:3b"
    # Unknown agent should return default
    assert settings.get_model_for_agent("unknown") == "llama3.2:3b"


def test_load_model_mappings_from_yaml():
    """Test loading model mappings from YAML file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path = Path(tmpdir) / "models.yaml"
        yaml_path.write_text("""
models:
  researcher: qwen2.5:7b
  developer: llama3.2:3b
""")

        with patch("config.settings.Path") as mock_path:
            mock_path.return_value = yaml_path
            settings = Settings()
            assert "researcher" in settings.model_mappings


def test_get_settings_singleton():
    """Test that get_settings returns singleton instance."""
    reset_settings()
    settings1 = get_settings()
    settings2 = get_settings()

    assert settings1 is settings2


def test_reset_settings():
    """Test resetting global settings."""
    reset_settings()
    settings = get_settings()
    assert settings is not None

    reset_settings()
    reset_settings()  # Should not raise
