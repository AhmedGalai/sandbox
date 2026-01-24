# Voice Cloner - Complete Documentation Index

Welcome to Voice Cloner! This index helps you navigate the project.

## Getting Started

### For First-Time Users
1. **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in 5 minutes
   - Installation steps
   - Register a voice
   - Speak text
   - Try interactive chat

2. **[INSTALLATION.md](INSTALLATION.md)** - Detailed setup instructions
   - Platform-specific guides (Linux, macOS, Windows)
   - GPU setup (NVIDIA, AMD, Apple Silicon)
   - Troubleshooting
   - Docker setup

### For Developers
1. **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development guide
   - Project structure
   - Code organization
   - Development workflow
   - Common tasks
   - Testing

2. **[examples.py](examples.py)** - Interactive examples
   - 8 different usage examples
   - Run with: `python examples.py`

## Complete Documentation

### Main Documentation
- **[README.md](README.md)** - Full documentation
  - Features overview
  - CLI command reference
  - Python API documentation
  - Configuration guide
  - Troubleshooting (detailed)
  - Advanced usage patterns
  - Performance optimization

### Project Information
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview
  - What was created
  - Key features
  - Technical highlights
  - Statistics
  - Performance metrics

## Quick Reference

### Installation Methods

**Option 1: Using pip**
```bash
pip install -r requirements.txt
```

**Option 2: Using setup.py**
```bash
pip install -e .
```

**Option 3: Using Makefile**
```bash
make install
```

### Basic Usage

**Register a voice:**
```bash
python -m voice_cloner clone my_voice voice_sample.wav
```

**Speak text:**
```bash
python -m voice_cloner speak "Hello world" --voice my_voice
```

**Interactive chat (requires Ollama):**
```bash
python -m voice_cloner chat --voice my_voice --model qwen3
```

**List voices:**
```bash
python -m voice_cloner list-voices
```

**Show system info:**
```bash
python -m voice_cloner info
```

## CLI Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `clone` | Register voice | `clone my_voice sample.wav` |
| `speak` | Speak text | `speak "Hello" --voice my_voice` |
| `chat` | Chat with voice | `chat --voice my_voice --model qwen3` |
| `list-voices` | Show voices | `list-voices` |
| `list-models` | Show Ollama models | `list-models` |
| `info` | System information | `info` |

See [README.md](README.md#cli-commands) for full details.

## Python API

### Basic Synthesis
```python
from voice_cloner.core.cloner import XTTSVoiceCloner
from voice_cloner.core.audio import play_audio

cloner = XTTSVoiceCloner()
audio = cloner.synthesize("Hello", "voices/my_voice.wav")
play_audio(audio)
```

### Voice Assistant
```python
from voice_cloner.assistant import VoiceAssistant

assistant = VoiceAssistant("my_voice", "voices/my_voice.wav")
response = assistant.chat("Tell me a joke!")
assistant.close()
```

### Ollama Integration
```python
from voice_cloner.llm.ollama_client import OllamaClient

client = OllamaClient()
if client.is_running():
    response = client.generate("What is Python?", model="qwen3")
    print(response)
```

See [README.md](README.md#python-api) for complete examples.

## Project Structure

```
voice_cloner/
├── src/voice_cloner/          # Main package
│   ├── __main__.py           # CLI entry point
│   ├── config.py             # Configuration
│   ├── assistant.py          # Voice assistant
│   ├── core/                 # Core modules
│   │   ├── cloner.py        # XTTS wrapper
│   │   └── audio.py         # Audio I/O
│   └── llm/                  # LLM integration
│       └── ollama_client.py # Ollama client
├── voices/                   # Voice samples
├── output/                   # Generated audio
├── requirements.txt          # Dependencies
├── setup.py                  # Package setup
├── Makefile                  # Dev commands
├── examples.py               # Examples
├── README.md                 # Full docs
├── QUICKSTART.md             # Quick start
├── INSTALLATION.md           # Installation
├── DEVELOPMENT.md            # Dev guide
├── PROJECT_SUMMARY.md        # Project info
└── INDEX.md                  # This file
```

## Features at a Glance

- **Voice Cloning**: XTTS v2 model for high-quality voice synthesis
- **Text-to-Speech**: Convert text to speech with cloned voices
- **Voice Chat**: Interactive conversations with voice output (Ollama integration)
- **CLI Interface**: Easy-to-use command-line interface
- **Python API**: Programmatic access to all features
- **Batch Processing**: Process multiple texts efficiently
- **GPU Acceleration**: Automatic GPU detection and usage
- **Audio Management**: Register, store, and manage voice samples

## Common Tasks

### Task: Clone Your Own Voice
See [QUICKSTART.md](QUICKSTART.md#step-3-register-your-voice)

### Task: Create Audio Content
See [QUICKSTART.md](QUICKSTART.md#2-create-audio-content)

### Task: Set Up Voice Assistant
See [QUICKSTART.md](QUICKSTART.md#use-chat-with-ollama-optional)

### Task: Use as Python Library
See [README.md](README.md#python-api)

### Task: Batch Process Texts
See [README.md](README.md#batch-processing)

## Troubleshooting

- **Installation issues** → See [INSTALLATION.md](INSTALLATION.md#troubleshooting-installation)
- **Runtime errors** → See [README.md](README.md#troubleshooting)
- **Ollama not running** → See [README.md](README.md#troubleshooting)
- **Audio playback fails** → See [README.md](README.md#troubleshooting)
- **Out of memory** → See [README.md](README.md#troubleshooting)

## Performance

| Aspect | Performance |
|--------|-------------|
| Model Load | 5-15s (first), <1s (cached) |
| Synthesis (GPU) | 2-5s per 30s audio |
| Synthesis (CPU) | 15-30s per 30s audio |
| Memory | 2-4GB (GPU), 1-2GB (CPU) |
| Model Size | ~3GB |

See [README.md](README.md#performance) for details.

## System Requirements

- Python 3.8+
- 8GB RAM (16GB recommended)
- 10GB free disk space
- Optional: GPU (NVIDIA, AMD, or Apple Silicon)

See [INSTALLATION.md](INSTALLATION.md#prerequisites) for details.

## Dependencies

- **TTS** (Coqui Text-to-Speech)
- **PyTorch** (Deep learning)
- **Ollama** (LLM integration - optional)
- **Click** (CLI framework)
- **Rich** (Terminal UI)

See [requirements.txt](requirements.txt) for versions.

## Examples

Run interactive examples:
```bash
python examples.py
```

Available examples:
1. Basic synthesis
2. Different temperatures
3. Different speeds
4. Check Ollama
5. Text generation
6. Voice assistant
7. Batch processing
8. System info

## Development

### Setting Up Development
```bash
make install-dev
```

### Code Style
```bash
make lint
make format
```

### Running Tests
```bash
pytest tests/ -v
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for details.

## File Summary

| File | Purpose | Lines |
|------|---------|-------|
| cloner.py | XTTS wrapper | 294 |
| audio.py | Audio I/O | 198 |
| ollama_client.py | Ollama client | 234 |
| assistant.py | Voice assistant | 172 |
| __main__.py | CLI interface | 464 |
| config.py | Configuration | 67 |
| examples.py | Examples | 345 |
| Total Code | Production code | ~1,800 |
| Documentation | Guides & docs | ~2,000 |

## Quick Links

### Documentation
- [Full README](README.md)
- [Quick Start](QUICKSTART.md)
- [Installation Guide](INSTALLATION.md)
- [Development Guide](DEVELOPMENT.md)
- [Project Summary](PROJECT_SUMMARY.md)

### Code
- [Main Package](src/voice_cloner/)
- [Examples](examples.py)
- [Setup](setup.py)

### External Resources
- [XTTS GitHub](https://github.com/coqui-ai/TTS)
- [PyTorch](https://pytorch.org)
- [Ollama](https://ollama.ai)
- [Click Documentation](https://click.palletsprojects.com/)

## Support

### Getting Help

1. **Installation issues** → Check [INSTALLATION.md](INSTALLATION.md)
2. **Usage questions** → Check [README.md](README.md)
3. **Development help** → Check [DEVELOPMENT.md](DEVELOPMENT.md)
4. **Code examples** → Run `python examples.py`
5. **Error messages** → Check [README.md](README.md#troubleshooting)

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Roadmap

Potential future features:
- Real-time streaming
- Voice style transfer
- Multi-speaker support
- Audio effects
- Web UI
- Advanced caching
- Model quantization

## License & Credits

Built with:
- [Coqui TTS](https://github.com/coqui-ai/TTS) - Voice synthesis
- [PyTorch](https://pytorch.org) - Deep learning
- [Ollama](https://ollama.ai) - LLM integration
- [Click](https://click.palletsprojects.com/) - CLI
- [Rich](https://rich.readthedocs.io/) - Terminal UI

## Quick Tips

1. **First run is slow** - Model downloads and caches (~3GB)
2. **Use GPU** - Much faster if available (5x-10x speedup)
3. **Voice quality** - Better with 5-30 second samples, clear speech
4. **Batch processing** - Process multiple texts efficiently
5. **Chat requires Ollama** - Optional but needed for interactive chat

## What's Next?

1. Read [QUICKSTART.md](QUICKSTART.md)
2. Prepare a voice sample
3. Register your voice
4. Start synthesizing!
5. Explore advanced features

---

**Voice Cloner v1.0.0**
**Last Updated**: 2026-01-24

For the latest information, see [README.md](README.md)
