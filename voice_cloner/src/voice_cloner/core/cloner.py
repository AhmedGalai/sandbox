"""XTTS v2 voice cloning module."""

import logging
from pathlib import Path
from typing import Optional, Union

import numpy as np
import torch
import torchaudio

logger = logging.getLogger(__name__)


class XTTSVoiceCloner:
    """Voice cloning using XTTS v2 model."""

    def __init__(
        self,
        model_name: str = "tts_models/multilingual/multi-speaker/xtts_v2",
        gpu_run: bool = True,
        language: str = "en",
    ):
        """
        Initialize the XTTS voice cloner.

        Args:
            model_name: The model identifier for XTTS v2
            gpu_run: Whether to use GPU if available
            language: Language code for TTS
        """
        self.model_name = model_name
        self.language = language
        self.gpu_run = gpu_run and self._is_cuda_available()
        self.device = "cuda" if self.gpu_run else "cpu"

        self.model = None
        self.is_initialized = False

        logger.info(f"XTTSVoiceCloner initialized. Device: {self.device}")

    def _is_cuda_available(self) -> bool:
        """Check if CUDA is available."""
        try:
            return torch.cuda.is_available()
        except Exception as e:
            logger.warning(f"Could not check CUDA availability: {e}")
            return False

    def _load_model(self) -> None:
        """Lazy load the XTTS v2 model."""
        if self.is_initialized:
            return

        try:
            from TTS.api import TTS

            logger.info(f"Loading XTTS model: {self.model_name}")
            self.model = TTS(model_name=self.model_name, gpu=self.gpu_run, in_memory=True)
            self.is_initialized = True
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load XTTS model: {e}")
            raise RuntimeError(f"Could not load XTTS model: {e}") from e

    def _load_voice_sample(self, voice_sample_path: Union[str, Path]) -> np.ndarray:
        """
        Load a voice sample from file.

        Args:
            voice_sample_path: Path to the voice sample file

        Returns:
            Audio waveform as numpy array
        """
        voice_path = Path(voice_sample_path)

        if not voice_path.exists():
            raise FileNotFoundError(f"Voice sample not found: {voice_path}")

        try:
            # Load with torchaudio
            waveform, sample_rate = torchaudio.load(str(voice_path))

            # Resample to 24kHz if needed
            if sample_rate != 24000:
                resampler = torchaudio.transforms.Resample(sample_rate, 24000)
                waveform = resampler(waveform)

            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)

            # Convert to numpy
            audio_data = waveform.squeeze().numpy()

            logger.info(f"Loaded voice sample: {voice_path} ({len(audio_data)} samples)")
            return audio_data

        except Exception as e:
            logger.error(f"Failed to load voice sample: {e}")
            raise RuntimeError(f"Could not load voice sample: {e}") from e

    def synthesize(
        self,
        text: str,
        voice_sample_path: Union[str, Path],
        speed: float = 1.0,
        temperature: float = 0.75,
        top_p: float = 0.85,
        top_k: int = 50,
        output_file: Optional[Union[str, Path]] = None,
    ) -> np.ndarray:
        """
        Synthesize speech using a cloned voice.

        Args:
            text: The text to synthesize
            voice_sample_path: Path to the voice sample for cloning
            speed: Speech speed multiplier (0.5 to 2.0)
            temperature: Temperature for generation (0.0 to 1.0)
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            output_file: Optional path to save the output

        Returns:
            Audio waveform as numpy array (24kHz)
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if speed <= 0 or speed > 2.0:
            raise ValueError("Speed must be between 0 and 2.0")

        if temperature < 0 or temperature > 1.0:
            raise ValueError("Temperature must be between 0 and 1.0")

        # Lazy load model
        self._load_model()

        try:
            # Load voice sample
            voice_audio = self._load_voice_sample(voice_sample_path)

            logger.info(f"Synthesizing: '{text[:50]}...'")

            # Synthesize speech
            wav = self.model.tts(
                text=text,
                speaker_wav=voice_audio,
                language=self.language,
                speed=speed,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
            )

            # Convert to numpy array if needed
            if isinstance(wav, torch.Tensor):
                wav = wav.cpu().numpy()

            # Ensure output is float32
            if wav.dtype != np.float32:
                wav = wav.astype(np.float32)

            logger.info(f"Synthesis complete. Duration: {len(wav) / 24000:.2f}s")

            # Save to file if requested
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Convert to 16-bit PCM for saving
                wav_int16 = (wav * 32767).astype(np.int16)

                import soundfile as sf
                sf.write(str(output_path), wav_int16, 24000)
                logger.info(f"Saved to: {output_path}")

            return wav

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            raise RuntimeError(f"Could not synthesize speech: {e}") from e

    def clear_model(self) -> None:
        """Clear the loaded model from memory."""
        if self.model is not None:
            try:
                del self.model
                if self.gpu_run:
                    torch.cuda.empty_cache()
                self.is_initialized = False
                logger.info("Model cleared from memory")
            except Exception as e:
                logger.warning(f"Could not properly clear model: {e}")

    def get_info(self) -> dict:
        """Get information about the current configuration."""
        return {
            "model": self.model_name,
            "device": self.device,
            "language": self.language,
            "initialized": self.is_initialized,
            "sample_rate": 24000,
        }
