# Development Guide

Guide for developers extending and maintaining Voice Cloner.

## Project Structure

```
voice_cloner/
├── src/voice_cloner/              # Main package
│   ├── __init__.py               # Package exports
│   ├── __main__.py               # CLI entry point
│   ├── config.py                 # Configuration & utilities
│   ├── assistant.py              # Voice assistant orchestrator
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── cloner.py            # XTTS voice cloning
│   │   └── audio.py             # Audio I/O and playback
│   └── llm/                      # LLM integration
│       ├── __init__.py
│       └── ollama_client.py      # Ollama API wrapper
├── voices/                       # Voice samples storage
├── output/                       # Generated audio storage
├── examples.py                   # Example usage
├── setup.py                      # Package configuration
├── requirements.txt              # Dependencies
├── Makefile                      # Development commands
├── .gitignore                    # Git ignore patterns
├── README.md                     # User documentation
├── QUICKSTART.md                 # Quick start guide
├── INSTALLATION.md               # Installation guide
├── DEVELOPMENT.md                # This file
└── PROJECT_SUMMARY.md            # Project overview
```

## Code Organization

### Core Modules

#### `voice_cloner/core/cloner.py` - XTTS Voice Cloning
- Main class: `XTTSVoiceCloner`
- Responsibilities:
  - Load XTTS v2 model (lazy loading)
  - Load and prepare voice samples
  - Synthesize speech from text
  - Save audio to files
  - Manage GPU/CPU resources

Key methods:
```python
synthesize(text, voice_sample_path, speed, temperature, output_file)
_load_model()
_load_voice_sample(path)
clear_model()
get_info()
```

#### `voice_cloner/core/audio.py` - Audio Management
- Main class: `AudioPlayer`
- Responsibilities:
  - Play audio with sounddevice
  - Save audio to WAV files
  - Load and reprocess audio
  - Handle different sample rates and bit depths

Key functions:
```python
AudioPlayer.play(audio_data, blocking)
save_audio(audio_data, output_path, sample_rate, bit_depth)
play_audio(audio_data, sample_rate, blocking)
load_audio(audio_path)
```

#### `voice_cloner/llm/ollama_client.py` - Ollama Integration
- Main class: `OllamaClient`
- Responsibilities:
  - Connect to Ollama API
  - Generate text with LLM
  - Support streaming responses
  - List available models
  - Check service status

Key methods:
```python
is_running()
list_models()
generate(prompt, model, temperature, stream)
chat(messages, model, temperature, stream)
```

#### `voice_cloner/assistant.py` - Voice Assistant
- Main class: `VoiceAssistant`
- Responsibilities:
  - Combine voice cloning + LLM
  - Manage chat conversations
  - Orchestrate synthesis and playback
  - Handle resource cleanup

Key methods:
```python
speak(text, speed, temperature, output_file, play)
chat(user_input, system_prompt, temperature, speak_response)
clear_history()
get_history()
close()
```

#### `voice_cloner/__main__.py` - CLI Interface
- Main function: `cli()`
- Commands:
  - `clone` - Register voice sample
  - `speak` - Synthesize text to speech
  - `chat` - Interactive conversation
  - `list-voices` - Show registered voices
  - `list-models` - Show Ollama models
  - `info` - System information

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
cd /home/ag/Desktop/sandbox/voice_cloner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install black pylint flake8 pytest

# Or use Makefile
make install-dev
```

### Code Style

Follow PEP 8:
```bash
# Format code
black src/voice_cloner --line-length=100

# Lint code
pylint src/voice_cloner
flake8 src/voice_cloner --max-line-length=100
```

### Testing

Create tests in a `tests/` directory:
```python
# tests/test_cloner.py
import pytest
from voice_cloner.core.cloner import XTTSVoiceCloner

def test_initialization():
    cloner = XTTSVoiceCloner()
    assert cloner.device in ["cuda", "cpu"]
    assert not cloner.is_initialized

def test_load_model():
    cloner = XTTSVoiceCloner()
    cloner._load_model()
    assert cloner.is_initialized
```

Run tests:
```bash
pytest tests/ -v
```

### Logging

Enable logging for debugging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

## Common Development Tasks

### Adding a New CLI Command

1. Add function in `src/voice_cloner/__main__.py`:
```python
@cli.command()
@click.argument("arg_name")
@click.option("--option-name", default="default")
def new_command(arg_name, option_name):
    """Command description."""
    try:
        # Implementation
        console.print("[green]Success![/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
```

2. Update help text in README.md
3. Test the new command
4. Update QUICKSTART.md if needed

### Adding a New Module

1. Create module file in appropriate directory:
```
src/voice_cloner/new_module/
├── __init__.py
└── implementation.py
```

2. Add to `src/voice_cloner/__init__.py`:
```python
from .new_module import NewClass
__all__ = [..., "NewClass"]
```

3. Update documentation

### Extending XTTSVoiceCloner

```python
# In src/voice_cloner/core/cloner.py

class XTTSVoiceCloner:
    def new_method(self, param):
        """New functionality."""
        if not self.is_initialized:
            self._load_model()

        # Implementation
        logger.info("New method executed")
        return result
```

### Adding Configuration Options

1. Update `src/voice_cloner/config.py`:
```python
NEW_OPTION = os.getenv("NEW_OPTION", "default_value")
```

2. Document in README.md Configuration section

### Testing Audio Output

```python
# Manual testing
from voice_cloner.core.audio import play_audio
import numpy as np

# Generate test tone
test_audio = np.sin(2 * np.pi * 440 * np.arange(24000) / 24000).astype(np.float32)
play_audio(test_audio)
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.getLogger("voice_cloner").setLevel(logging.DEBUG)
```

### Common Issues

1. **Model not loading**
   ```python
   cloner = XTTSVoiceCloner(gpu_run=False)  # Force CPU
   ```

2. **Audio playback fails**
   ```python
   import sounddevice as sd
   print(sd.query_devices())  # Check available devices
   ```

3. **Ollama connection fails**
   ```bash
   curl http://localhost:11434/api/tags  # Check if Ollama is running
   ```

## Performance Optimization

### Memory Usage

```python
# Clear model cache after use
cloner.clear_model()

# Process in batches for long texts
texts = text.split(".")
for chunk in texts:
    audio = cloner.synthesize(chunk, voice_path)
```

### GPU Optimization

```python
# Enable GPU
cloner = XTTSVoiceCloner(gpu_run=True)

# Clear GPU cache
import torch
torch.cuda.empty_cache()
```

## Documentation Updates

1. Update README.md for user-facing changes
2. Update QUICKSTART.md for common tasks
3. Update INSTALLATION.md for setup changes
4. Add docstrings to new functions
5. Update this file for developer changes

## Release Process

1. Update version in `setup.py`
2. Update README.md and documentation
3. Add entry to CHANGELOG
4. Run full test suite
5. Tag release in git
6. Build distribution: `python setup.py sdist bdist_wheel`

## Contributing Guidelines

1. Keep commits focused and atomic
2. Write clear commit messages
3. Update documentation with code changes
4. Test thoroughly before submitting
5. Follow code style guidelines
6. Add docstrings to functions
7. Handle errors gracefully

## Architecture Decisions

### Why Lazy Loading?
- Model is large (~3GB)
- Not needed until first synthesis
- Reduces startup time
- Allows GPU memory to be freed

### Why Separate Modules?
- Clear separation of concerns
- Easy to extend independently
- Testable in isolation
- Reusable components

### Why Click for CLI?
- Simple and intuitive
- Automatic help generation
- Good error handling
- Active maintenance

### Why Rich for UI?
- Beautiful terminal output
- Colors and formatting
- Progress indicators
- Table rendering

## Future Architecture Improvements

1. **Streaming Output**
   - Real-time audio generation
   - Reduce latency
   - Better UX

2. **Multiple Voices**
   - Voice blending
   - Style transfer
   - Advanced effects

3. **Web Interface**
   - REST API
   - Web UI
   - Broader accessibility

4. **Caching**
   - Cache synthesized text
   - Reduce computation
   - Improve performance

5. **Advanced Audio Processing**
   - Noise reduction
   - EQ/compression
   - Effects chain

## Dependencies Management

Update dependencies carefully:
```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade TTS

# Update all (not recommended)
pip install --upgrade -r requirements.txt
```

## Troubleshooting Development

### Import errors
```bash
# Reinstall in editable mode
pip install -e .
```

### Model cache issues
```bash
# Clear PyTorch cache
rm -rf ~/.cache/torch/

# Clear TTS cache
rm -rf ~/.cache/tts_models/
```

### GPU issues
```python
# Test CUDA availability
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
```

## Performance Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
cloner = XTTSVoiceCloner()
audio = cloner.synthesize("Hello", voice_path)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(10)
```

## Code Review Checklist

- [ ] Code follows PEP 8
- [ ] Docstrings added for functions
- [ ] Error handling implemented
- [ ] Logging added
- [ ] Type hints included
- [ ] Tests written
- [ ] Documentation updated
- [ ] No hardcoded values
- [ ] Security considered
- [ ] Performance acceptable

## Resources

- [XTTS Documentation](https://github.com/coqui-ai/TTS)
- [PyTorch Guide](https://pytorch.org/docs/stable/index.html)
- [Click Documentation](https://click.palletsprojects.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)

## Contact & Support

For development questions:
1. Check existing code and comments
2. Review documentation
3. Check issue tracker
4. Create detailed bug reports

---

**Last Updated**: 2026-01-24
**Version**: 1.0.0
