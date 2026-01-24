# Quick Start Guide

Get up and running with Voice Cloner in 5 minutes!

## Step 1: Install Dependencies

```bash
cd /home/ag/Desktop/sandbox/voice_cloner
pip install -r requirements.txt
```

Or use the Makefile:
```bash
make install
```

## Step 2: Prepare a Voice Sample

You need a clear audio sample (5-30 seconds) of the voice you want to clone. This can be:
- A microphone recording
- An audio clip from a video
- A voice assistant response
- Any WAV/MP3 file

Example (using your microphone):
```bash
# On macOS/Linux
ffmpeg -f pulse -i default -t 10 voice_sample.wav

# Or download an example voice online
```

## Step 3: Register Your Voice

```bash
python -m voice_cloner clone my_voice /path/to/voice_sample.wav
```

Verify it was registered:
```bash
python -m voice_cloner list-voices
```

## Step 4: Speak Some Text

```bash
python -m voice_cloner speak "Hello! This is my cloned voice!" --voice my_voice
```

That's it! You're cloning voices!

## Next Steps

### Try Different Parameters

```bash
# Slower speech
python -m voice_cloner speak "Hello" --voice my_voice --speed 0.8

# More variation
python -m voice_cloner speak "Hello" --voice my_voice --temperature 0.9

# Save to file
python -m voice_cloner speak "Hello" --voice my_voice --output hello.wav --no-play
```

### Use Chat with Ollama (Optional)

If you want interactive chat with voice responses:

1. **Install Ollama**: Download from https://ollama.ai

2. **Start Ollama**:
```bash
ollama serve
```

3. **In another terminal, pull a model**:
```bash
ollama pull qwen3
# or
ollama pull command-r7b
```

4. **Start chatting**:
```bash
python -m voice_cloner chat --voice my_voice --model qwen3
```

Type messages and get voice responses!

### List Available Models

```bash
python -m voice_cloner list-models
```

## Common Use Cases

### 1. Create Multiple Voices

```bash
# Register different voices
python -m voice_cloner clone alice alice_sample.wav
python -m voice_cloner clone bob bob_sample.wav
python -m voice_cloner clone charlie charlie_sample.wav

# Use them interchangeably
python -m voice_cloner speak "Hello from Alice" --voice alice
python -m voice_cloner speak "Hello from Bob" --voice bob
```

### 2. Create Audio Content

```bash
# Batch create audio files
for i in {1..10}; do
    python -m voice_cloner speak "This is message number $i" \
        --voice my_voice \
        --output message_$i.wav \
        --no-play
done
```

### 3. Use as Python Library

```python
from voice_cloner.core.cloner import XTTSVoiceCloner
from voice_cloner.core.audio import play_audio

cloner = XTTSVoiceCloner()
audio = cloner.synthesize(
    text="Hello world!",
    voice_sample_path="voices/my_voice.wav"
)
play_audio(audio)
```

### 4. Interactive Voice Assistant

```python
from voice_cloner.assistant import VoiceAssistant

assistant = VoiceAssistant(
    voice_name="my_voice",
    voice_sample_path="voices/my_voice.wav",
    ollama_model="qwen3"
)

# Chat with voice response
response = assistant.chat("Tell me a joke!")

# Cleanup
assistant.close()
```

## Troubleshooting

### "Voice not found"
Make sure you've registered the voice:
```bash
python -m voice_cloner clone my_voice voice_sample.wav
python -m voice_cloner list-voices
```

### "Model loading fails"
First time loading the model will download ~3GB. Make sure you have:
- Sufficient disk space (~10GB)
- Good internet connection
- Enough RAM (8GB+)

### "Ollama not running"
Start it in another terminal:
```bash
ollama serve
```

### "No sound output"
Try forcing to CPU (slower but more compatible):
```python
cloner = XTTSVoiceCloner(gpu_run=False)
```

### "Out of memory"
- Use CPU instead of GPU
- Reduce voice sample length
- Use shorter text for synthesis

## Tips & Tricks

1. **Better voice samples**: Use samples with:
   - Clear speech (no mumbling)
   - Minimal background noise
   - Consistent tone
   - 5-30 seconds duration

2. **Best results**:
   - Temperature: 0.5-0.8 (lower = more consistent)
   - Speed: 0.8-1.2 (closer to original sample speed)

3. **Faster synthesis**: Use CPU for testing, GPU for production

4. **Batch processing**: For many texts, write a simple loop (see Use Cases)

## Examples

Run interactive examples:
```bash
python examples.py
```

Available examples:
1. Basic synthesis
2. Different temperatures
3. Different speeds
4. Check Ollama status
5. Text generation
6. Voice assistant
7. Batch processing
8. System information

## Command Reference

| Command | Purpose | Example |
|---------|---------|---------|
| clone | Register voice sample | `python -m voice_cloner clone alice alice.wav` |
| speak | Speak text | `python -m voice_cloner speak "Hello" --voice alice` |
| chat | Interactive chat | `python -m voice_cloner chat --voice alice --model qwen3` |
| list-voices | Show registered voices | `python -m voice_cloner list-voices` |
| list-models | Show Ollama models | `python -m voice_cloner list-models` |
| info | System information | `python -m voice_cloner info` |

## What's Next?

- Explore the [full documentation](README.md)
- Check out the [examples](examples.py)
- Read the [Python API docs](README.md#python-api)
- Join the community

## Performance Expectations

| Device | Duration | Time |
|--------|----------|------|
| NVIDIA GPU | 30s | 2-5s |
| AMD GPU | 30s | 3-8s |
| CPU | 30s | 15-30s |
| Mac M1/M2 | 30s | 5-10s |

## Need Help?

1. Check the [README](README.md#troubleshooting)
2. Review [examples](examples.py)
3. Check logs with:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

---

**Happy voice cloning!** 🎤
