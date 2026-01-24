# Getting Started with Voice Cloner

Welcome! This guide will help you get started with Voice Cloner in the fastest way possible.

## 60-Second Setup

### Step 1: Install Dependencies (2 minutes)
```bash
cd /home/ag/Desktop/sandbox/voice_cloner
pip install -r requirements.txt
```

### Step 2: Verify Installation (30 seconds)
```bash
python3 -c "import sys; sys.path.insert(0, 'src'); from voice_cloner import VoiceAssistant; print('✓ Installation successful!')"
```

### Step 3: You're Ready!
All done! Proceed to "First Use" below.

## First Use

### Prerequisites
You need an audio file with a voice sample (5-30 seconds):
- A recording of someone speaking
- WAV, MP3, or other common format
- Clear speech with minimal background noise

### Step 1: Register Your Voice
```bash
# Replace sample.wav with your file
PYTHONPATH=src python3 -c "
import sys
sys.path.insert(0, 'src')
import shutil
from voice_cloner import config

# Copy your voice sample
shutil.copy2('sample.wav', str(config.get_voice_path('my_voice')))
print('✓ Voice registered as \"my_voice\"')
"
```

Or use the CLI (once you install the package):
```bash
python -m voice_cloner clone my_voice sample.wav
```

### Step 2: Synthesize Text
```bash
PYTHONPATH=src python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

from voice_cloner.core.cloner import XTTSVoiceCloner
from voice_cloner import config

cloner = XTTSVoiceCloner()
audio = cloner.synthesize(
    text="Hello! This is my cloned voice!",
    voice_sample_path=str(config.get_voice_path("my_voice")),
    output_file=str(config.get_output_path("output"))
)
print("✓ Audio synthesized and saved!")
EOF
```

### Step 3: Try Interactive Examples
```bash
PYTHONPATH=src python3 examples.py
```

Choose example 1 to test basic synthesis.

## Common Commands

### Using Python API

**Basic Synthesis:**
```python
import sys
sys.path.insert(0, 'src')
from voice_cloner.core.cloner import XTTSVoiceCloner
from voice_cloner.core.audio import play_audio

cloner = XTTSVoiceCloner()
audio = cloner.synthesize("Hello world", "voices/my_voice.wav")
play_audio(audio)
```

**Voice Assistant:**
```python
import sys
sys.path.insert(0, 'src')
from voice_cloner.assistant import VoiceAssistant

assistant = VoiceAssistant("my_voice", "voices/my_voice.wav")
assistant.speak("Hello from the voice assistant!")
assistant.close()
```

### Using the CLI

After installing with `pip install -e .`:

```bash
# Register a voice
python -m voice_cloner clone my_voice voice_sample.wav

# Speak text
python -m voice_cloner speak "Hello world" --voice my_voice

# List voices
python -m voice_cloner list-voices

# Show system info
python -m voice_cloner info
```

## Interactive Chat (Optional)

To use the chat feature, you need Ollama:

### 1. Install Ollama
Download from https://ollama.ai

### 2. Start Ollama Server
```bash
ollama serve
```

### 3. Pull a Model (in another terminal)
```bash
ollama pull qwen3
```

### 4. Chat with Voice Response
```bash
python -m voice_cloner chat --voice my_voice --model qwen3
```

Type messages and get voice responses!

## Troubleshooting First Use

### Import Error: "No module named voice_cloner"
Use `PYTHONPATH=src python3` when running scripts directly.

### Audio Not Playing
- Check if you have audio libraries installed
- On Ubuntu: `sudo apt-get install pulseaudio`
- Try with `--no-play` flag first

### Model Download Fails
- Check internet connection
- Ensure 10GB free disk space
- On first run, it will download ~3GB

### Ollama Connection Fails
- Ensure Ollama is running: `ollama serve`
- Check URL with: `curl http://localhost:11434/api/tags`

## What's Next?

1. **Learn the CLI**: Read [QUICKSTART.md](QUICKSTART.md)
2. **Full API**: Check [README.md](README.md)
3. **Examples**: Run `python examples.py`
4. **Advanced**: See [DEVELOPMENT.md](DEVELOPMENT.md)

## Directory Structure

After setup, you'll see:
```
voice_cloner/
├── voices/           # Your voice samples go here
├── output/           # Generated audio files
└── src/voice_cloner/ # Source code
```

## Performance Tips

1. **First run is slow** - Model downloads and initializes (~3GB)
2. **Use GPU** - Much faster if available (5-10x speedup)
3. **Batch processing** - Process multiple texts efficiently
4. **Cache clearing** - Clear cache if having issues

## Quick Reference

| Task | Command |
|------|---------|
| Install | `pip install -r requirements.txt` |
| Test Import | `python3 -c "import sys; sys.path.insert(0, 'src'); from voice_cloner import VoiceAssistant"` |
| Run Examples | `PYTHONPATH=src python3 examples.py` |
| Install Package | `pip install -e .` |
| System Info | `python -m voice_cloner info` (after install) |

## Getting Help

1. Check [README.md](README.md) for detailed documentation
2. Review [INSTALLATION.md](INSTALLATION.md) for setup help
3. Run [examples.py](examples.py) for usage examples
4. Check error messages - they include helpful info

## Feature Overview

What you can do with Voice Cloner:

- Clone any voice from a 5-30 second sample
- Generate speech in the cloned voice
- Save audio to files
- Play audio in real-time
- Chat interactively (with Ollama)
- Register multiple voices
- Batch process texts
- Use as Python library

## System Requirements

- Python 3.8+
- 8GB RAM (16GB recommended)
- 10GB free disk space
- Optional: NVIDIA/AMD GPU

## Installing as Python Package

```bash
cd /home/ag/Desktop/sandbox/voice_cloner
pip install -e .

# Now you can use:
python -m voice_cloner --version
python -m voice_cloner clone ...
python -m voice_cloner speak ...
python -m voice_cloner chat ...
```

## Next Steps

1. Prepare a 5-30 second voice sample
2. Register it with Voice Cloner
3. Generate speech in that voice
4. Explore advanced features

Happy voice cloning!

---

**Need help?** Start with [QUICKSTART.md](QUICKSTART.md) or [README.md](README.md)
