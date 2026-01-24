"""Voice Cloner - A complete voice cloning solution with XTTS v2 and Ollama integration."""

__version__ = "1.0.0"
__author__ = "Voice Cloner"

from .core.cloner import XTTSVoiceCloner
from .core.audio import AudioPlayer, save_audio
from .assistant import VoiceAssistant

__all__ = [
    "XTTSVoiceCloner",
    "AudioPlayer",
    "save_audio",
    "VoiceAssistant",
]
