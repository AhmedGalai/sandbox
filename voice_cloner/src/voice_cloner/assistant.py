"""Voice assistant combining voice cloning and LLM integration."""

import logging
from pathlib import Path
from typing import Optional, Union

from .core.audio import AudioPlayer, save_audio
from .core.cloner import XTTSVoiceCloner
from .llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class VoiceAssistant:
    """Voice assistant that combines voice cloning with LLM responses."""

    def __init__(
        self,
        voice_name: str,
        voice_sample_path: Optional[Union[str, Path]] = None,
        ollama_base_url: str = "http://localhost:11434",
        ollama_model: str = "qwen3",
        enable_playback: bool = True,
        language: str = "en",
    ):
        """
        Initialize the voice assistant.

        Args:
            voice_name: Name identifier for the voice
            voice_sample_path: Path to the voice sample for cloning
            ollama_base_url: Base URL for Ollama API
            ollama_model: Model to use for text generation
            enable_playback: Whether to enable audio playback
            language: Language code for TTS
        """
        self.voice_name = voice_name
        self.voice_sample_path = Path(voice_sample_path) if voice_sample_path else None
        self.ollama_model = ollama_model
        self.enable_playback = enable_playback
        self.language = language

        # Initialize components
        self.cloner = XTTSVoiceCloner(language=language)
        self.ollama = OllamaClient(base_url=ollama_base_url)
        self.player = AudioPlayer(sample_rate=24000) if enable_playback else None

        # Chat history for context
        self.chat_history = []

        logger.info(f"VoiceAssistant initialized with voice: {voice_name}")

    def speak(
        self,
        text: str,
        speed: float = 1.0,
        temperature: float = 0.75,
        output_file: Optional[Union[str, Path]] = None,
        play: bool = True,
    ) -> bytes:
        """
        Speak text using the cloned voice.

        Args:
            text: Text to speak
            speed: Speech speed multiplier
            temperature: Temperature for voice variation
            output_file: Optional file to save the audio
            play: Whether to play the audio

        Returns:
            Audio data as numpy array
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if not self.voice_sample_path or not self.voice_sample_path.exists():
            raise RuntimeError(f"Voice sample not found: {self.voice_sample_path}")

        try:
            # Synthesize speech
            audio = self.cloner.synthesize(
                text=text,
                voice_sample_path=self.voice_sample_path,
                speed=speed,
                temperature=temperature,
                output_file=output_file,
            )

            # Play audio if enabled
            if play and self.enable_playback and self.player:
                self.player.play(audio, blocking=True)

            return audio

        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            raise RuntimeError(f"Could not speak text: {e}") from e

    def chat(
        self,
        user_input: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        speak_response: bool = True,
        output_file: Optional[Union[str, Path]] = None,
    ) -> str:
        """
        Chat with the assistant and get a spoken response.

        Args:
            user_input: User's input text
            system_prompt: System prompt to set assistant behavior
            temperature: Temperature for LLM generation
            speak_response: Whether to speak the response
            output_file: Optional file to save the response audio

        Returns:
            The assistant's response text
        """
        if not user_input or not user_input.strip():
            raise ValueError("User input cannot be empty")

        try:
            # Build messages for chat
            messages = []

            # Add system message if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Add chat history
            messages.extend(self.chat_history)

            # Add current user message
            messages.append({"role": "user", "content": user_input})

            logger.info(f"Chat input: {user_input[:100]}")

            # Get response from LLM
            response_text = self.ollama.chat(
                messages=messages,
                model=self.ollama_model,
                temperature=temperature,
                stream=False,
            )

            # Add to chat history
            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": response_text})

            # Keep history reasonable size (last 20 messages)
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]

            logger.info(f"Chat response: {response_text[:100]}")

            # Speak the response if requested
            if speak_response:
                self.speak(
                    text=response_text,
                    temperature=0.75,
                    output_file=output_file,
                    play=self.enable_playback,
                )

            return response_text

        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise RuntimeError(f"Could not complete chat: {e}") from e

    def clear_history(self) -> None:
        """Clear chat history."""
        self.chat_history = []
        logger.info("Chat history cleared")

    def get_history(self) -> list[dict]:
        """Get current chat history."""
        return self.chat_history.copy()

    def close(self) -> None:
        """Close and cleanup resources."""
        try:
            if self.player:
                self.player.stop()
            self.ollama.close()
            self.cloner.clear_model()
            logger.info("VoiceAssistant closed")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
