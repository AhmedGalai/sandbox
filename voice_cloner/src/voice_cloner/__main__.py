"""CLI entry point for voice cloner."""

import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import assistant as assistant_module
from . import config
from .core.audio import save_audio
from .core.cloner import XTTSVoiceCloner
from .llm.ollama_client import OllamaClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

console = Console()


@click.group()
@click.version_option("1.0.0")
def cli():
    """Voice Cloner - AI-powered voice cloning with XTTS v2 and Ollama integration."""
    pass


@cli.command()
@click.argument("voice_name")
@click.argument("audio_file", type=click.Path(exists=True))
@click.option(
    "--force/--no-force",
    default=False,
    help="Overwrite existing voice sample.",
)
def clone(voice_name: str, audio_file: str, force: bool):
    """Register a new voice sample."""
    try:
        voice_path = config.get_voice_path(voice_name)

        # Check if voice already exists
        if voice_path.exists() and not force:
            console.print(
                f"[yellow]Voice '{voice_name}' already exists. Use --force to overwrite.[/yellow]"
            )
            return

        # Copy voice sample
        import shutil

        shutil.copy2(audio_file, voice_path)
        console.print(f"[green]✓ Voice '{voice_name}' registered successfully![/green]")
        console.print(f"  Location: {voice_path}")

    except Exception as e:
        console.print(f"[red]Error registering voice: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("text")
@click.option(
    "--voice",
    required=True,
    help="Voice name to use for synthesis.",
)
@click.option(
    "--speed",
    type=float,
    default=1.0,
    help="Speech speed multiplier (0.5-2.0).",
)
@click.option(
    "--temperature",
    type=float,
    default=0.75,
    help="Voice variation temperature (0.0-1.0).",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Save output to file.",
)
@click.option(
    "--no-play",
    is_flag=True,
    default=False,
    help="Do not play the audio.",
)
def speak(
    text: str,
    voice: str,
    speed: float,
    temperature: float,
    output: str,
    no_play: bool,
):
    """Speak text using a cloned voice."""
    try:
        # Validate voice exists
        if not config.voice_exists(voice):
            available = ", ".join(config.list_voices()) if config.list_voices() else "none"
            console.print(f"[red]Voice '{voice}' not found.[/red]")
            console.print(f"Available voices: {available}")
            sys.exit(1)

        voice_path = config.get_voice_path(voice)

        # Determine output path
        output_path = None
        if output:
            output_path = output
        else:
            output_path = config.get_output_path(f"output_{len(list(config.OUTPUT_DIR.glob('*.wav')))}")

        with console.status("[bold green]Initializing model...", spinner="dots"):
            cloner = XTTSVoiceCloner()

        with console.status("[bold green]Synthesizing speech...", spinner="dots"):
            audio = cloner.synthesize(
                text=text,
                voice_sample_path=voice_path,
                speed=speed,
                temperature=temperature,
                output_file=output_path,
            )

        if not no_play:
            with console.status("[bold green]Playing audio...", spinner="dots"):
                from .core.audio import play_audio

                play_audio(audio)

        console.print(f"[green]✓ Synthesis complete![/green]")
        console.print(f"  Duration: {len(audio) / 24000:.2f}s")
        console.print(f"  Saved to: {output_path}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--voice",
    required=True,
    help="Voice name to use for responses.",
)
@click.option(
    "--model",
    default="qwen3",
    help="Ollama model to use.",
)
@click.option(
    "--system",
    type=str,
    help="System prompt to set assistant behavior.",
)
@click.option(
    "--temperature",
    type=float,
    default=0.7,
    help="LLM temperature (0.0-1.0).",
)
@click.option(
    "--no-play",
    is_flag=True,
    default=False,
    help="Do not play responses.",
)
@click.option(
    "--save-responses",
    is_flag=True,
    default=False,
    help="Save all responses to files.",
)
def chat(
    voice: str,
    model: str,
    system: str,
    temperature: float,
    no_play: bool,
    save_responses: bool,
):
    """Interactive chat with voice output (requires Ollama)."""
    try:
        # Validate voice exists
        if not config.voice_exists(voice):
            available = ", ".join(config.list_voices()) if config.list_voices() else "none"
            console.print(f"[red]Voice '{voice}' not found.[/red]")
            console.print(f"Available voices: {available}")
            sys.exit(1)

        voice_path = config.get_voice_path(voice)

        # Check Ollama
        ollama = OllamaClient(base_url=config.OLLAMA_BASE_URL)
        if not ollama.is_running():
            console.print("[red]Ollama is not running![/red]")
            console.print("Start it with: [yellow]ollama serve[/yellow]")
            sys.exit(1)

        # Check model
        available_models = ollama.list_models()
        if model not in available_models:
            available_str = ", ".join(available_models) if available_models else "none"
            console.print(f"[red]Model '{model}' not found.[/red]")
            console.print(f"Available models: {available_str}")
            sys.exit(1)

        # Initialize assistant
        with console.status("[bold green]Initializing...", spinner="dots"):
            asst = assistant_module.VoiceAssistant(
                voice_name=voice,
                voice_sample_path=voice_path,
                ollama_model=model,
                enable_playback=not no_play,
            )

        console.print(
            Panel(
                "[bold cyan]Voice Chat Assistant[/bold cyan]\n"
                f"Voice: {voice}\n"
                f"Model: {model}\n\n"
                "[yellow]Type 'exit' or 'quit' to exit[/yellow]\n"
                "[yellow]Type 'clear' to clear history[/yellow]",
                border_style="cyan",
            )
        )

        response_count = 0

        while True:
            try:
                user_input = console.input("[bold cyan]You:[/bold cyan] ")

                if user_input.lower() in ["exit", "quit"]:
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                if user_input.lower() == "clear":
                    asst.clear_history()
                    console.print("[yellow]Chat history cleared.[/yellow]")
                    continue

                if not user_input.strip():
                    continue

                # Generate response
                output_file = None
                if save_responses:
                    output_file = config.get_output_path(f"response_{response_count}")
                    response_count += 1

                with console.status("[bold green]Thinking...", spinner="dots"):
                    response = asst.chat(
                        user_input=user_input,
                        system_prompt=system,
                        temperature=temperature,
                        speak_response=not no_play,
                        output_file=output_file,
                    )

                console.print(f"[bold magenta]Assistant:[/bold magenta] {response}\n")

            except KeyboardInterrupt:
                console.print("\n[yellow]Chat interrupted.[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

        asst.close()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
def list_voices():
    """List all registered voice samples."""
    try:
        voices = config.list_voices()

        if not voices:
            console.print("[yellow]No voices registered yet.[/yellow]")
            console.print(f"Add voices with: [cyan]python -m voice_cloner clone <name> <audio_file>[/cyan]")
            return

        table = Table(title="Registered Voices", show_header=True, header_style="bold cyan")
        table.add_column("Voice Name", style="green")
        table.add_column("File Path", style="blue")
        table.add_column("Size (MB)", justify="right", style="yellow")

        for voice in voices:
            voice_path = config.get_voice_path(voice)
            size_mb = voice_path.stat().st_size / 1024 / 1024
            table.add_row(voice, str(voice_path), f"{size_mb:.2f}")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--url",
    default=config.OLLAMA_BASE_URL,
    help="Ollama server URL.",
)
def list_models(url: str):
    """List available Ollama models."""
    try:
        ollama = OllamaClient(base_url=url)

        if not ollama.is_running():
            console.print("[red]Ollama is not running![/red]")
            console.print(f"Server URL: {url}")
            console.print("Start it with: [yellow]ollama serve[/yellow]")
            sys.exit(1)

        models = ollama.list_models()

        if not models:
            console.print("[yellow]No models found in Ollama.[/yellow]")
            console.print("Pull a model with: [cyan]ollama pull qwen3[/cyan]")
            return

        table = Table(title="Available Ollama Models", show_header=True, header_style="bold cyan")
        table.add_column("Model Name", style="green")
        table.add_column("Status", style="cyan")

        for model in models:
            table.add_row(model, "Ready")

        console.print(table)
        console.print(f"\n[yellow]Total: {len(models)} model(s)[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
def info():
    """Show system and configuration information."""
    try:
        from .core.cloner import XTTSVoiceCloner

        cloner = XTTSVoiceCloner()
        info_dict = cloner.get_info()

        # Check Ollama
        ollama = OllamaClient(base_url=config.OLLAMA_BASE_URL)
        ollama_running = ollama.is_running()
        ollama_models = len(ollama.list_models()) if ollama_running else 0

        # Count voices
        voices = config.list_voices()

        panel_text = (
            f"[bold cyan]XTTS v2 Configuration:[/bold cyan]\n"
            f"  Model: {info_dict['model']}\n"
            f"  Device: {info_dict['device']}\n"
            f"  Language: {info_dict['language']}\n"
            f"  Sample Rate: {info_dict['sample_rate']} Hz\n\n"
            f"[bold cyan]Ollama:[/bold cyan]\n"
            f"  Status: {'[green]Running[/green]' if ollama_running else '[red]Not Running[/red]'}\n"
            f"  URL: {config.OLLAMA_BASE_URL}\n"
            f"  Models: {ollama_models}\n\n"
            f"[bold cyan]Voice Samples:[/bold cyan]\n"
            f"  Registered: {len(voices)}\n"
            f"  Location: {config.VOICES_DIR}\n\n"
            f"[bold cyan]Output:[/bold cyan]\n"
            f"  Location: {config.OUTPUT_DIR}"
        )

        console.print(Panel(panel_text, border_style="cyan", title="Voice Cloner Info"))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
