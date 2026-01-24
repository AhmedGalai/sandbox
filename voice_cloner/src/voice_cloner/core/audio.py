"""Audio playback and saving utilities."""

import logging
from pathlib import Path
from typing import Optional, Union

import numpy as np
import sounddevice as sd
import soundfile as sf

logger = logging.getLogger(__name__)


class AudioPlayer:
    """Audio player for playback with sounddevice."""

    def __init__(self, sample_rate: int = 24000):
        """
        Initialize the audio player.

        Args:
            sample_rate: Sample rate in Hz (default: 24000 for XTTS)
        """
        self.sample_rate = sample_rate
        self.is_playing = False

    def play(self, audio_data: np.ndarray, blocking: bool = True) -> None:
        """
        Play audio data.

        Args:
            audio_data: Audio waveform as numpy array (float32, range -1.0 to 1.0)
            blocking: Whether to block until playback is complete
        """
        if audio_data is None or len(audio_data) == 0:
            raise ValueError("Audio data is empty")

        try:
            # Ensure audio is float32 and in range [-1, 1]
            audio = audio_data.astype(np.float32)

            # Clip to [-1, 1] to prevent distortion
            audio = np.clip(audio, -1.0, 1.0)

            logger.info(f"Playing audio ({len(audio)} samples, {len(audio) / self.sample_rate:.2f}s)")

            self.is_playing = True
            sd.play(audio, self.sample_rate, blocking=blocking)

            if blocking:
                sd.wait()
                self.is_playing = False
                logger.info("Playback complete")

        except Exception as e:
            logger.error(f"Playback error: {e}")
            self.is_playing = False
            raise RuntimeError(f"Could not play audio: {e}") from e

    def stop(self) -> None:
        """Stop audio playback."""
        try:
            sd.stop()
            self.is_playing = False
            logger.info("Playback stopped")
        except Exception as e:
            logger.warning(f"Error stopping playback: {e}")

    def wait(self) -> None:
        """Wait for playback to complete."""
        if self.is_playing:
            sd.wait()
            self.is_playing = False


def save_audio(
    audio_data: np.ndarray,
    output_path: Union[str, Path],
    sample_rate: int = 24000,
    bit_depth: int = 16,
) -> None:
    """
    Save audio data to a WAV file.

    Args:
        audio_data: Audio waveform as numpy array
        output_path: Path where to save the audio
        sample_rate: Sample rate in Hz
        bit_depth: Bit depth (16 or 24)
    """
    output_path = Path(output_path)

    if audio_data is None or len(audio_data) == 0:
        raise ValueError("Audio data is empty")

    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert float32 to proper integer range based on bit depth
        if bit_depth == 16:
            max_val = 32767
            subtype = "PCM_16"
        elif bit_depth == 24:
            max_val = 8388607
            subtype = "PCM_24"
        else:
            raise ValueError(f"Unsupported bit depth: {bit_depth}")

        # Ensure audio is in [-1, 1] range
        audio = np.clip(audio_data.astype(np.float32), -1.0, 1.0)

        # Write to file
        sf.write(str(output_path), audio, sample_rate, subtype=subtype)

        file_size = output_path.stat().st_size
        logger.info(f"Saved audio to {output_path} ({file_size / 1024 / 1024:.2f} MB)")

    except Exception as e:
        logger.error(f"Failed to save audio: {e}")
        raise RuntimeError(f"Could not save audio: {e}") from e


def play_audio(
    audio_data: np.ndarray,
    sample_rate: int = 24000,
    blocking: bool = True,
) -> None:
    """
    Play audio data directly.

    Args:
        audio_data: Audio waveform as numpy array
        sample_rate: Sample rate in Hz
        blocking: Whether to block until playback is complete
    """
    player = AudioPlayer(sample_rate=sample_rate)
    player.play(audio_data, blocking=blocking)


def load_audio(audio_path: Union[str, Path]) -> tuple[np.ndarray, int]:
    """
    Load audio from a file.

    Args:
        audio_path: Path to the audio file

    Returns:
        Tuple of (audio_data, sample_rate)
    """
    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        import torchaudio

        waveform, sample_rate = torchaudio.load(str(audio_path))

        # Convert to mono if stereo
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        # Convert to numpy
        audio_data = waveform.squeeze().numpy().astype(np.float32)

        logger.info(f"Loaded audio from {audio_path} (sample rate: {sample_rate} Hz)")
        return audio_data, sample_rate

    except Exception as e:
        logger.error(f"Failed to load audio: {e}")
        raise RuntimeError(f"Could not load audio: {e}") from e
