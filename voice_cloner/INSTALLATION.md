# Installation Guide

Complete installation instructions for Voice Cloner on different platforms.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 10 GB free disk space (for models)
- 8 GB RAM minimum (16 GB recommended)

## System-Specific Requirements

### Linux (Ubuntu/Debian)

```bash
# Update package manager
sudo apt-get update

# Install audio libraries
sudo apt-get install -y \
    libsndfile1 \
    libsndfile1-dev \
    libasound2-dev \
    pulseaudio

# For GPU support (NVIDIA)
# Follow: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/

# For GPU support (AMD)
# Install ROCm: https://rocmdocs.amd.com/
```

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install audio libraries
brew install libsndfile pulseaudio

# Python (if not installed)
brew install python@3.11
```

### Windows

1. Install Python from https://www.python.org (3.8+)
   - **Important**: Check "Add Python to PATH"

2. Install Visual C++ Build Tools from:
   https://visualstudio.microsoft.com/visual-cpp-build-tools/

3. For GPU support (NVIDIA):
   - Install CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
   - Install cuDNN: https://developer.nvidia.com/cudnn

## Installation Steps

### 1. Clone or Navigate to the Project

```bash
cd /home/ag/Desktop/sandbox/voice_cloner
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

#### Option A: Using pip (Recommended)

```bash
pip install -r requirements.txt
```

#### Option B: Using setup.py

```bash
pip install -e .
```

#### Option C: Using Makefile

```bash
make install
```

### 4. Verify Installation

```bash
# Check version
python -m voice_cloner --version

# Show system info
python -m voice_cloner info

# List available voices (empty initially)
python -m voice_cloner list-voices
```

## GPU Setup (Optional but Recommended)

### NVIDIA GPUs

```bash
# Verify CUDA installation
nvidia-smi

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify CUDA support in PyTorch
python -c "import torch; print(torch.cuda.is_available())"
```

### AMD GPUs

```bash
# Install PyTorch with ROCm support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7

# Verify ROCm support
python -c "import torch; print(torch.cuda.is_available())"
```

### Apple Silicon (M1/M2/M3)

```bash
# PyTorch automatically uses Metal Performance Shaders
pip install torch torchvision torchaudio

# Verify MPS support
python -c "import torch; print(torch.backends.mps.is_available())"
```

## Install Optional Dependencies

### For Ollama Integration

```bash
# Download and install Ollama from https://ollama.ai
# Follow the installation instructions for your OS

# Verify installation
ollama --version

# Pull a model
ollama pull qwen3
```

### For Development

```bash
# Install development tools
pip install black pylint flake8 pytest

# Or using Makefile
make install-dev
```

## Post-Installation Setup

### 1. Create Voice Sample Directory

```bash
mkdir -p voices
```

### 2. Prepare a Voice Sample

Create or download an audio file (WAV or MP3, 5-30 seconds).

### 3. Register Voice

```bash
python -m voice_cloner clone my_voice /path/to/voice_sample.wav
```

## Troubleshooting Installation

### ImportError: No module named 'torch'

```bash
# Reinstall PyTorch
pip uninstall torch -y
pip install torch

# Or with CUDA support
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### CUDA out of memory

```bash
# Use CPU instead
# Edit src/voice_cloner/config.py and set:
# XTTS_GPU_RUN = False
```

### Audio playback issues

```bash
# Ubuntu/Debian - reinstall audio libraries
sudo apt-get install --reinstall pulseaudio alsa-utils

# Reinstall sounddevice
pip install --upgrade sounddevice
```

### Model download fails

```bash
# Check internet connection
# Ensure 10GB free disk space
# Try manual download:
python -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-speaker/xtts_v2')"
```

### RuntimeError: CUDA device not found

```bash
# Verify NVIDIA drivers
nvidia-smi

# Reinstall CUDA support
pip install torch --force-reinstall --index-url https://download.pytorch.org/whl/cu118
```

## Verify Installation

Run all verification steps:

```bash
# 1. Check Python version
python --version

# 2. Check installed packages
pip list | grep -E "TTS|torch|ollama|click|rich"

# 3. Check configuration
python -m voice_cloner info

# 4. Try a simple synthesis (requires voice sample)
python -m voice_cloner speak "Hello" --voice my_voice
```

## Environment Variables

You can customize behavior with environment variables:

```bash
# Set Ollama URL
export OLLAMA_BASE_URL=http://localhost:11434

# Set default model
export OLLAMA_DEFAULT_MODEL=qwen3

# Use CPU for TTS (helpful for troubleshooting)
export CUDA_VISIBLE_DEVICES=""
```

## Docker Installation (Optional)

If you prefer containerized setup:

```dockerfile
FROM pytorch/pytorch:2.1.0-cuda11.8-runtime-ubuntu22.04

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    libsndfile1-dev \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Set entrypoint
ENTRYPOINT ["python", "-m", "voice_cloner"]
```

Build and run:
```bash
docker build -t voice-cloner .
docker run --gpus all voice-cloner --version
```

## Performance Testing

After installation, test performance:

```bash
python -c "
from voice_cloner.core.cloner import XTTSVoiceCloner
import time

cloner = XTTSVoiceCloner()
print(f'Device: {cloner.device}')

# This will download and cache the model
start = time.time()
cloner._load_model()
elapsed = time.time() - start
print(f'Model load time: {elapsed:.2f}s')
"
```

## Uninstallation

To remove Voice Cloner:

```bash
# Uninstall package
pip uninstall voice-cloner -y

# Remove cached models (optional)
rm -rf ~/.cache/torch/
rm -rf ~/.cache/tts_models/
rm -rf ~/.cache/huggingface/

# Remove project directory
rm -rf /home/ag/Desktop/sandbox/voice_cloner/
```

## Update Installation

To update to latest version:

```bash
cd /home/ag/Desktop/sandbox/voice_cloner
pip install -e . --upgrade
```

## Support & Help

If you encounter issues:

1. Check [Troubleshooting](README.md#troubleshooting)
2. Enable debug logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```
3. Check system requirements
4. Review error messages carefully

## Next Steps

After successful installation:

1. Read [Quick Start](QUICKSTART.md)
2. Prepare a voice sample
3. Register the voice
4. Start synthesizing!

For advanced usage, see [README.md](README.md)

---

**Installation Complete!** Enjoy voice cloning! 🎤
