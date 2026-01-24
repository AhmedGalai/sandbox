"""Configuration module for voice cloner."""

import os
from pathlib import Path
from typing import Optional

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent.parent
VOICES_DIR = PROJECT_ROOT / "voices"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Ensure directories exist
VOICES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Model configuration
XTTS_MODEL_NAME = "tts_models/multilingual/multi-speaker/xtts_v2"
XTTS_GPU_RUN = True  # Will auto-detect
XTTS_LANGUAGE = "en"

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", "qwen3")
OLLAMA_TIMEOUT = 300  # 5 minutes

# Audio configuration
SAMPLE_RATE = 24000  # XTTS v2 expects 24kHz
DEFAULT_SPEED = 1.0
DEFAULT_TEMPERATURE = 0.75


def _is_cuda_available() -> bool:
    """Check if CUDA is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def _is_pytorch_available() -> bool:
    """Check if PyTorch is available."""
    try:
        import torch
        return True
    except ImportError:
        return False


# Device configuration (set after function definitions)
DEVICE = "cuda" if _is_cuda_available() else "cpu" if _is_pytorch_available() else "cpu"


def get_voice_path(voice_name: str) -> Path:
    """Get the path for a voice sample."""
    return VOICES_DIR / f"{voice_name}.wav"


def get_output_path(output_name: str) -> Path:
    """Get the path for output audio."""
    return OUTPUT_DIR / f"{output_name}.wav"


def list_voices() -> list[str]:
    """List all available voice samples."""
    if not VOICES_DIR.exists():
        return []

    voices = []
    for wav_file in VOICES_DIR.glob("*.wav"):
        voices.append(wav_file.stem)

    return sorted(voices)


def voice_exists(voice_name: str) -> bool:
    """Check if a voice sample exists."""
    return get_voice_path(voice_name).exists()
