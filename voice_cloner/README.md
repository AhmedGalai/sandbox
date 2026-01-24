# Voice Cloner

A complete, production-ready voice cloning application powered by XTTS v2 and optional Ollama integration for text generation.

## Features

- **Voice Cloning**: Clone any voice using Coqui's XTTS v2 model
- **Text-to-Speech**: Convert text to speech with cloned voices
- **Voice Chat**: Interactive chat with voice responses (requires Ollama)
- **LLM Integration**: Optional integration with Ollama for intelligent responses
- **GPU Acceleration**: Automatic GPU detection and acceleration
- **Audio Playback**: Built-in audio playback support
- **CLI Interface**: Easy-to-use command-line interface
- **Voice Management**: Register and manage multiple voice samples

## Requirements

- Python 3.8+
- PyTorch 2.1.0+
- CUDA 11.8+ (optional, for GPU acceleration)
- Ollama (optional, for chat functionality)

## Installation

### 1. Clone the repository

```bash
cd /home/ag/Desktop/sandbox/voice_cloner
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install system dependencies (Ubuntu/Debian)

```bash
# For audio support
sudo apt-get install libsndfile1 libsoundfile-dev

# For GPU support (CUDA)
# Follow https://pytorch.org/get-started/locally/
```

### 4. Install Ollama (optional, for chat)

```bash
# Download and install from https://ollama.ai
ollama pull qwen3  # or command-r7b
```

## Quick Start

### Register a Voice

```bash
# Register a voice sample
python -m voice_cloner clone my_voice /path/to/voice_sample.wav

# List registered voices
python -m voice_cloner list-voices
```

### Speak Text

```bash
# Speak text with cloned voice
python -m voice_cloner speak "Hello, this is my cloned voice!" --voice my_voice

# Save to file without playing
python -m voice_cloner speak "Hello" --voice my_voice --output output.wav --no-play

# Adjust speed and voice variation
python -m voice_cloner speak "Hello" --voice my_voice --speed 0.8 --temperature 0.5
```

### Interactive Chat

```bash
# Start chat with voice output (requires Ollama)
python -m voice_cloner chat --voice my_voice --model qwen3

# With custom system prompt
python -m voice_cloner chat --voice my_voice --model qwen3 --system "You are a helpful assistant"

# Save all responses to files
python -m voice_cloner chat --voice my_voice --model qwen3 --save-responses
```

### View System Info

```bash
# Show configuration and status
python -m voice_cloner info

# List available Ollama models
python -m voice_cloner list-models
```

## CLI Commands

### clone
Register a new voice sample.

```bash
Usage: python -m voice_cloner clone [OPTIONS] VOICE_NAME AUDIO_FILE

Options:
  --force/--no-force    Overwrite existing voice sample
```

### speak
Speak text using a cloned voice.

```bash
Usage: python -m voice_cloner speak [OPTIONS] TEXT

Options:
  --voice TEXT              Voice name to use (required)
  --speed FLOAT            Speech speed multiplier (0.5-2.0, default: 1.0)
  --temperature FLOAT      Voice variation (0.0-1.0, default: 0.75)
  --output PATH            Save to file
  --no-play                Don't play the audio
```

### chat
Interactive chat with voice output (requires Ollama).

```bash
Usage: python -m voice_cloner chat [OPTIONS]

Options:
  --voice TEXT            Voice name to use (required)
  --model TEXT            Ollama model (default: qwen3)
  --system TEXT           System prompt
  --temperature FLOAT     LLM temperature (default: 0.7)
  --no-play               Don't play responses
  --save-responses        Save responses to files
```

### list-voices
List all registered voice samples.

```bash
Usage: python -m voice_cloner list-voices
```

### list-models
List available Ollama models.

```bash
Usage: python -m voice_cloner list-models [OPTIONS]

Options:
  --url TEXT    Ollama server URL
```

### info
Show system and configuration information.

```bash
Usage: python -m voice_cloner info
```

## Python API

You can also use Voice Cloner as a Python library:

### Voice Cloning

```python
from voice_cloner.core.cloner import XTTSVoiceCloner
from voice_cloner.core.audio import play_audio

# Initialize cloner
cloner = XTTSVoiceCloner(language="en")

# Synthesize speech
audio = cloner.synthesize(
    text="Hello, this is a test",
    voice_sample_path="voices/my_voice.wav",
    speed=1.0,
    temperature=0.75,
    output_file="output/test.wav"
)

# Play the audio
play_audio(audio)
```

### Voice Assistant

```python
from voice_cloner.assistant import VoiceAssistant

# Initialize assistant
assistant = VoiceAssistant(
    voice_name="my_voice",
    voice_sample_path="voices/my_voice.wav",
    ollama_model="qwen3",
    enable_playback=True
)

# Speak text
assistant.speak("Hello world!")

# Chat with voice response
response = assistant.chat(
    user_input="Tell me a joke",
    speak_response=True
)

# Cleanup
assistant.close()
```

### Ollama Integration

```python
from voice_cloner.llm.ollama_client import OllamaClient

# Initialize client
client = OllamaClient(base_url="http://localhost:11434")

# Check status
if client.is_running():
    # List models
    models = client.list_models()
    print(f"Available models: {models}")

    # Generate text
    response = client.generate(
        prompt="What is Python?",
        model="qwen3",
        temperature=0.7
    )
    print(response)

    # Streaming generation
    for chunk in client.generate(
        prompt="Tell me a story",
        model="qwen3",
        stream=True
    ):
        print(chunk, end="", flush=True)
```

## Configuration

Edit `src/voice_cloner/config.py` to customize:

- `XTTS_MODEL_NAME`: XTTS model identifier
- `XTTS_GPU_RUN`: Enable/disable GPU
- `XTTS_LANGUAGE`: Default language
- `OLLAMA_BASE_URL`: Ollama server URL
- `OLLAMA_DEFAULT_MODEL`: Default Ollama model
- `SAMPLE_RATE`: Audio sample rate (default: 24000 Hz)
- `DEVICE`: Compute device (cuda/cpu)

## Voice Sample Requirements

For best results, voice samples should:

- Be 5-30 seconds long
- Contain clear speech
- Have minimal background noise
- Be in WAV, MP3, or other common audio format
- Represent the desired voice characteristics

## Performance

- **GPU (NVIDIA)**: ~2-5 seconds for 30 seconds of audio
- **GPU (AMD/other)**: ~3-8 seconds
- **CPU**: ~15-30 seconds

## Troubleshooting

### CUDA not found
```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Ollama not running
```bash
# Start Ollama server
ollama serve

# In another terminal, pull a model
ollama pull qwen3
```

### Audio playback issues
```bash
# Install audio libraries (Ubuntu)
sudo apt-get install pulseaudio libasound2-dev

# Reinstall sounddevice
pip install --upgrade sounddevice
```

### Out of memory
- Reduce audio length
- Use CPU instead of GPU
- Clear model cache: `cloner.clear_model()`

## Project Structure

```
voice_cloner/
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── src/
│   └── voice_cloner/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # CLI entry point
│       ├── config.py            # Configuration
│       ├── assistant.py         # Voice assistant orchestrator
│       ├── core/
│       │   ├── __init__.py
│       │   ├── cloner.py        # XTTS voice cloning
│       │   └── audio.py         # Audio playback/saving
│       └── llm/
│           ├── __init__.py
│           └── ollama_client.py # Ollama API wrapper
├── voices/                      # Registered voice samples
│   └── .gitkeep
└── output/                      # Generated audio files
    └── .gitkeep
```

## Advanced Usage

### Custom Voice Profiles

```python
from voice_cloner.core.cloner import XTTSVoiceCloner

cloner = XTTSVoiceCloner(language="en")

# Different voice characteristics
profiles = {
    "enthusiastic": {"temperature": 0.9, "speed": 1.1},
    "calm": {"temperature": 0.5, "speed": 0.9},
    "fast": {"temperature": 0.7, "speed": 1.5},
}

for profile_name, params in profiles.items():
    audio = cloner.synthesize(
        text="Hello",
        voice_sample_path="voices/my_voice.wav",
        **params
    )
```

### Batch Processing

```python
from pathlib import Path
from voice_cloner.core.cloner import XTTSVoiceCloner
from voice_cloner import config

cloner = XTTSVoiceCloner()

texts = [
    "First message",
    "Second message",
    "Third message"
]

for i, text in enumerate(texts):
    cloner.synthesize(
        text=text,
        voice_sample_path="voices/my_voice.wav",
        output_file=config.get_output_path(f"batch_{i}")
    )
```

## Supported Languages

XTTS v2 supports:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Polish (pl)
- Turkish (tr)
- Russian (ru)
- Dutch (nl)
- Chinese (zh)
- Japanese (ja)
- Arabic (ar)
- Hindi (hi)
- And many more...

## License

This project uses:
- XTTS v2: Under the XTTS license
- Ollama: Under Apache 2.0 license
- Other dependencies: See respective licenses

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs (enable DEBUG logging)
3. Check GitHub issues
4. Create a new issue with:
   - Python version
   - CUDA version (if applicable)
   - Error message and traceback
   - Steps to reproduce

## Future Enhancements

- [ ] Real-time speech input
- [ ] Voice style transfer
- [ ] Multi-speaker support
- [ ] Audio effects and processing
- [ ] Web UI
- [ ] Docker support
- [ ] Streaming audio output
- [ ] Custom model support

## Credits

Built with:
- [Coqui TTS](https://github.com/coqui-ai/TTS)
- [Ollama](https://ollama.ai)
- [PyTorch](https://pytorch.org)
- [Click](https://click.palletsprojects.com)
- [Rich](https://rich.readthedocs.io)

---

**Version**: 1.0.0
**Last Updated**: 2026-01-24
