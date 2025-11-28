"""
Command system for the Ollama CLI.
Provides command routing, registry, and handlers for all CLI commands.
"""

from typing import Callable, Dict

from .agents import AgentsCommand, DeveloperCommand, PlannerCommand, ResearcherCommand
from .help import HelpCommand
from .models import ModelsCommand, PullCommand, UseCommand
from .settings import SettingsCommand
from .utils import ClearCommand, ExportCommand, HistoryCommand
from .vision import VisionCommand

__all__ = [
    "HelpCommand",
    "AgentsCommand",
    "ResearcherCommand",
    "DeveloperCommand",
    "PlannerCommand",
    "VisionCommand",
    "ModelsCommand",
    "UseCommand",
    "PullCommand",
    "ClearCommand",
    "HistoryCommand",
    "ExportCommand",
    "SettingsCommand",
    "COMMAND_REGISTRY",
]

# Command registry mapping command names to command classes
COMMAND_REGISTRY: Dict[str, type] = {
    # Help and information
    "help": HelpCommand,
    # Agents
    "agents": AgentsCommand,
    "researcher": ResearcherCommand,
    "developer": DeveloperCommand,
    "planner": PlannerCommand,
    # Vision
    "vision": VisionCommand,
    # Models
    "models": ModelsCommand,
    "use": UseCommand,
    "pull": PullCommand,
    # Utilities
    "clear": ClearCommand,
    "history": HistoryCommand,
    "export": ExportCommand,
    # Settings
    "settings": SettingsCommand,
}

# Quick aliases
COMMAND_ALIASES: Dict[str, str] = {
    "?": "help",
    "h": "help",
    "cls": "clear",
    "quit": "exit",
    "q": "exit",
}
