"""Example usage of the voice_cloner package."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from voice_cloner.core.cloner import XTTSVoiceCloner
from voice_cloner.core.audio import play_audio, save_audio
from voice_cloner.assistant import VoiceAssistant
from voice_cloner.llm.ollama_client import OllamaClient
from voice_cloner import config


def example_1_basic_synthesis():
    """Example 1: Basic voice synthesis."""
    print("\n=== Example 1: Basic Voice Synthesis ===\n")

    # This example assumes you have a voice sample registered as 'my_voice'
    # First, register a voice with: python -m voice_cloner clone my_voice /path/to/sample.wav

    try:
        # Initialize the cloner
        cloner = XTTSVoiceCloner(language="en")

        # Synthesize text
        voice_path = config.get_voice_path("my_voice")

        if not voice_path.exists():
            print("Please register a voice first:")
            print("  python -m voice_cloner clone my_voice /path/to/voice_sample.wav")
            return

        audio = cloner.synthesize(
            text="Hello, this is an example of voice cloning with XTTS v2!",
            voice_sample_path=voice_path,
            speed=1.0,
            temperature=0.75,
            output_file=config.get_output_path("example_1")
        )

        print(f"Synthesis complete! Duration: {len(audio) / 24000:.2f}s")
        print(f"Playing audio...")
        play_audio(audio)

        print("✓ Example complete!")

    except Exception as e:
        print(f"Error: {e}")


def example_2_different_temperatures():
    """Example 2: Different voice temperatures."""
    print("\n=== Example 2: Different Voice Temperatures ===\n")

    try:
        cloner = XTTSVoiceCloner(language="en")
        voice_path = config.get_voice_path("my_voice")

        if not voice_path.exists():
            print("Please register a voice first")
            return

        temperatures = [0.3, 0.7, 1.0]
        text = "This is a test with different voice variations."

        for temp in temperatures:
            print(f"Synthesizing with temperature={temp}...")
            audio = cloner.synthesize(
                text=text,
                voice_sample_path=voice_path,
                temperature=temp,
                output_file=config.get_output_path(f"temp_{temp}")
            )
            print(f"  Duration: {len(audio) / 24000:.2f}s")

        print("✓ Example complete!")

    except Exception as e:
        print(f"Error: {e}")


def example_3_speech_speeds():
    """Example 3: Different speech speeds."""
    print("\n=== Example 3: Different Speech Speeds ===\n")

    try:
        cloner = XTTSVoiceCloner(language="en")
        voice_path = config.get_voice_path("my_voice")

        if not voice_path.exists():
            print("Please register a voice first")
            return

        speeds = [0.8, 1.0, 1.2, 1.5]
        text = "This is a test with different speaking speeds."

        for speed in speeds:
            print(f"Synthesizing with speed={speed}...")
            audio = cloner.synthesize(
                text=text,
                voice_sample_path=voice_path,
                speed=speed,
                output_file=config.get_output_path(f"speed_{speed}")
            )
            print(f"  Duration: {len(audio) / 24000:.2f}s")

        print("✓ Example complete!")

    except Exception as e:
        print(f"Error: {e}")


def example_4_check_ollama():
    """Example 4: Check Ollama status."""
    print("\n=== Example 4: Check Ollama Status ===\n")

    try:
        client = OllamaClient(base_url=config.OLLAMA_BASE_URL)

        if client.is_running():
            print("✓ Ollama is running!")

            models = client.list_models()
            print(f"✓ Found {len(models)} model(s):")
            for model in models:
                print(f"  - {model}")
        else:
            print("✗ Ollama is not running")
            print("Start it with: ollama serve")

    except Exception as e:
        print(f"Error: {e}")


def example_5_text_generation():
    """Example 5: Generate text with Ollama."""
    print("\n=== Example 5: Text Generation with Ollama ===\n")

    try:
        client = OllamaClient(base_url=config.OLLAMA_BASE_URL)

        if not client.is_running():
            print("Ollama is not running. Start it with: ollama serve")
            return

        models = client.list_models()
        if not models:
            print("No models found. Pull one with: ollama pull qwen3")
            return

        model = models[0]
        print(f"Using model: {model}\n")

        prompt = "Tell me a short joke about programming."
        print(f"Prompt: {prompt}")
        print("\nGenerating response...")

        response = client.generate(prompt=prompt, model=model, temperature=0.7)
        print(f"\nResponse:\n{response}")

    except Exception as e:
        print(f"Error: {e}")


def example_6_voice_assistant():
    """Example 6: Voice assistant with chat."""
    print("\n=== Example 6: Voice Assistant ===\n")

    try:
        voice_path = config.get_voice_path("my_voice")

        if not voice_path.exists():
            print("Please register a voice first")
            return

        client = OllamaClient(base_url=config.OLLAMA_BASE_URL)
        if not client.is_running():
            print("Ollama is not running. Start it with: ollama serve")
            return

        models = client.list_models()
        if not models:
            print("No models found. Pull one with: ollama pull qwen3")
            return

        print(f"Initializing assistant with voice and model {models[0]}...\n")

        # Initialize assistant (set enable_playback=False for non-interactive mode)
        assistant = VoiceAssistant(
            voice_name="my_voice",
            voice_sample_path=voice_path,
            ollama_model=models[0],
            enable_playback=False  # Don't play audio automatically
        )

        # Just speak text
        print("Speaking a test message...")
        assistant.speak(
            text="Hello! I am your voice assistant. How can I help you today?",
            output_file=config.get_output_path("assistant_greeting")
        )

        # Chat without audio (for demonstration)
        print("\nGenerating chat response...")
        response = assistant.chat(
            user_input="What is the capital of France?",
            speak_response=False
        )
        print(f"Response: {response}")

        assistant.close()
        print("\n✓ Example complete!")

    except Exception as e:
        print(f"Error: {e}")


def example_7_batch_processing():
    """Example 7: Batch processing multiple texts."""
    print("\n=== Example 7: Batch Processing ===\n")

    try:
        cloner = XTTSVoiceCloner(language="en")
        voice_path = config.get_voice_path("my_voice")

        if not voice_path.exists():
            print("Please register a voice first")
            return

        texts = [
            "Welcome to the voice cloning demo.",
            "This is the first message.",
            "This is the second message.",
            "This is the third message.",
            "Thank you for using our application!"
        ]

        print(f"Processing {len(texts)} texts...\n")

        for i, text in enumerate(texts):
            print(f"Processing {i+1}/{len(texts)}: '{text[:30]}...'")

            audio = cloner.synthesize(
                text=text,
                voice_sample_path=voice_path,
                output_file=config.get_output_path(f"batch_{i:02d}")
            )

            print(f"  Duration: {len(audio) / 24000:.2f}s")

        print("\n✓ Batch processing complete!")
        print(f"Output saved to: {config.OUTPUT_DIR}")

    except Exception as e:
        print(f"Error: {e}")


def example_8_system_info():
    """Example 8: Display system information."""
    print("\n=== Example 8: System Information ===\n")

    try:
        from voice_cloner.core.cloner import XTTSVoiceCloner

        cloner = XTTSVoiceCloner()
        info = cloner.get_info()

        print("XTTS Configuration:")
        for key, value in info.items():
            print(f"  {key}: {value}")

        print("\nVoice Samples:")
        voices = config.list_voices()
        if voices:
            for voice in voices:
                voice_path = config.get_voice_path(voice)
                size_mb = voice_path.stat().st_size / 1024 / 1024
                print(f"  - {voice}: {size_mb:.2f} MB")
        else:
            print("  No voices registered")

        print("\nOllama Status:")
        client = OllamaClient(base_url=config.OLLAMA_BASE_URL)
        if client.is_running():
            models = client.list_models()
            print(f"  Status: Running")
            print(f"  Models: {len(models)}")
            for model in models[:3]:
                print(f"    - {model}")
            if len(models) > 3:
                print(f"    ... and {len(models) - 3} more")
        else:
            print("  Status: Not running")

        print("\nDirectories:")
        print(f"  Voices: {config.VOICES_DIR}")
        print(f"  Output: {config.OUTPUT_DIR}")

    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run examples."""
    print("\n" + "="*60)
    print("Voice Cloner - Examples")
    print("="*60)

    examples = [
        ("1", "Basic synthesis", example_1_basic_synthesis),
        ("2", "Different temperatures", example_2_different_temperatures),
        ("3", "Different speeds", example_3_speech_speeds),
        ("4", "Check Ollama status", example_4_check_ollama),
        ("5", "Text generation", example_5_text_generation),
        ("6", "Voice assistant", example_6_voice_assistant),
        ("7", "Batch processing", example_7_batch_processing),
        ("8", "System information", example_8_system_info),
        ("q", "Quit", None),
    ]

    while True:
        print("\nAvailable Examples:")
        for num, desc, _ in examples:
            if num != "q":
                print(f"  {num}. {desc}")
            else:
                print(f"  {num}. {desc}")

        choice = input("\nSelect example (1-8, q to quit): ").strip().lower()

        for num, _, func in examples:
            if choice == num:
                if func:
                    try:
                        func()
                    except KeyboardInterrupt:
                        print("\n✗ Interrupted by user")
                    except Exception as e:
                        print(f"\n✗ Error: {e}")
                else:
                    print("Goodbye!")
                    return
                break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
