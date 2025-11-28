"""
Tests for OllamaClient async HTTP client.
"""

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from core.ollama_client import OllamaClient
from core.exceptions import (
    OllamaConnectionError,
    InvalidModelError,
    VisionProcessingError,
)


@pytest.fixture
def client():
    """Create OllamaClient instance for testing."""
    return OllamaClient(host="http://localhost:11434", timeout=10.0)


@pytest.mark.asyncio
async def test_client_initialization(client):
    """Test OllamaClient initialization."""
    assert client.host == "http://localhost:11434"
    assert client.timeout == 10.0
    assert client.max_retries == 3


@pytest.mark.asyncio
async def test_client_context_manager(client):
    """Test OllamaClient as async context manager."""
    async with client as c:
        assert c is client


@pytest.mark.asyncio
async def test_get_client(client):
    """Test _get_client returns httpx.AsyncClient."""
    http_client = await client._get_client()
    assert isinstance(http_client, httpx.AsyncClient)

    # Verify subsequent calls return same instance
    http_client2 = await client._get_client()
    assert http_client is http_client2

    await client.close()


@pytest.mark.asyncio
async def test_close(client):
    """Test client cleanup."""
    await client._get_client()
    assert client._client is not None

    await client.close()
    assert client._client is None


@pytest.mark.asyncio
async def test_generate_success(client):
    """Test successful text generation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Test response"}
    mock_response.raise_for_status.return_value = None

    with patch.object(client, "_get_client") as mock_get_client:
        mock_http_client = AsyncMock()
        mock_http_client.post.return_value = mock_response
        mock_get_client.return_value = mock_http_client

        result = await client.generate("llama3.2:3b", "Test prompt")
        assert result == "Test response"
        mock_http_client.post.assert_called_once()

    await client.close()


@pytest.mark.asyncio
async def test_generate_model_not_found(client):
    """Test generate with invalid model."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not found", request=MagicMock(), response=mock_response
    )

    with patch.object(client, "_get_client") as mock_get_client:
        mock_http_client = AsyncMock()
        mock_http_client.post.return_value = mock_response
        mock_get_client.return_value = mock_http_client

        with pytest.raises(InvalidModelError):
            await client.generate("nonexistent:model", "Test prompt")

    await client.close()


@pytest.mark.asyncio
async def test_generate_connection_error_with_retry(client):
    """Test generate handles connection errors with retry."""
    client.max_retries = 1

    with patch.object(client, "_get_client") as mock_get_client:
        mock_http_client = AsyncMock()
        mock_http_client.post.side_effect = httpx.ConnectError("Connection failed")
        mock_get_client.return_value = mock_http_client

        with pytest.raises(OllamaConnectionError):
            await client.generate("llama3.2:3b", "Test prompt")

    await client.close()


@pytest.mark.asyncio
async def test_list_models(client):
    """Test listing available models."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "models": [
            {"name": "llama3.2:3b"},
            {"name": "qwen2.5:7b"},
        ]
    }
    mock_response.raise_for_status.return_value = None

    with patch.object(client, "_get_client") as mock_get_client:
        mock_http_client = AsyncMock()
        mock_http_client.get.return_value = mock_response
        mock_get_client.return_value = mock_http_client

        models = await client.list_models()
        assert len(models) == 2
        assert models[0]["name"] == "llama3.2:3b"

    await client.close()


@pytest.mark.asyncio
async def test_vision_generate_file_not_found(client):
    """Test vision_generate with missing image file."""
    with pytest.raises(VisionProcessingError):
        await client.vision_generate(
            "llava:7b",
            "/nonexistent/image.png",
            "Describe this image"
        )

    await client.close()
