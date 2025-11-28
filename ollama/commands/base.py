"""
Base command class for CLI command handlers.
Provides abstract interface and utilities for all commands.
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console


class BaseCommand(ABC):
    """
    Abstract base class for CLI commands.

    All commands should inherit from this class and implement
    execute() and get_help_text() methods.
    """

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize a command.

        Args:
            console: Rich Console instance for output (uses global if not provided)
        """
        self.console = console or Console()
        self.name: str = self.__class__.__name__.replace("Command", "").lower()
        self.description: str = self.__doc__ or ""

    @abstractmethod
    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the command.

        Args:
            args: Command arguments (first element is command name, rest are args)
            context: Shared context with agent factory, orchestrator, etc.

        Returns:
            Tuple of (success: bool, output: str)

        Raises:
            Exception: If command execution fails
        """
        pass

    @abstractmethod
    def get_help_text(self) -> str:
        """
        Get help text for the command.

        Returns:
            Formatted help text with usage and description
        """
        pass

    def validate_args(
        self,
        args: List[str],
        min_args: int = 0,
        max_args: Optional[int] = None,
    ) -> bool:
        """
        Validate command arguments.

        Args:
            args: Arguments to validate (excluding command name)
            min_args: Minimum number of arguments required
            max_args: Maximum number of arguments allowed (None = unlimited)

        Returns:
            True if arguments are valid

        Raises:
            ValueError: If arguments are invalid
        """
        if len(args) < min_args:
            raise ValueError(
                f"Expected at least {min_args} argument(s), got {len(args)}"
            )

        if max_args is not None and len(args) > max_args:
            raise ValueError(
                f"Expected at most {max_args} argument(s), got {len(args)}"
            )

        return True

    def parse_arguments(
        self, args: List[str], named_params: Optional[List[str]] = None
    ) -> Tuple[List[str], Dict[str, str]]:
        """
        Parse command arguments into positional and named parameters.

        Args:
            args: Arguments to parse
            named_params: List of parameter names (e.g., ['model', 'context'])

        Returns:
            Tuple of (positional_args, named_args_dict)

        Example:
            args = ['--model', 'llama3.2:3b', 'query']
            positional, named = parse_arguments(args, ['model'])
            # positional = ['query'], named = {'model': 'llama3.2:3b'}
        """
        positional = []
        named = {}
        named_params = named_params or []

        i = 0
        while i < len(args):
            arg = args[i]

            # Check if this is a named parameter
            if arg.startswith("--"):
                param_name = arg[2:].lower()

                if param_name in named_params:
                    if i + 1 < len(args):
                        named[param_name] = args[i + 1]
                        i += 2
                    else:
                        raise ValueError(f"Parameter --{param_name} requires a value")
                else:
                    raise ValueError(f"Unknown parameter: --{param_name}")
            else:
                positional.append(arg)
                i += 1

        return positional, named

    def extract_command_and_args(self, user_input: str) -> Tuple[str, List[str]]:
        """
        Extract command and arguments from user input.

        Args:
            user_input: Raw user input string

        Returns:
            Tuple of (command_name, args_list)

        Example:
            input: "/agents --model llama3"
            returns: ("agents", ["--model", "llama3"])
        """
        # Remove leading slash and split on whitespace
        cleaned = user_input.lstrip("/").strip()

        if not cleaned:
            return "", []

        parts = cleaned.split(None, 1)
        command = parts[0] if parts else ""

        # Parse arguments (respecting quoted strings)
        args = self._parse_quoted_args(parts[1] if len(parts) > 1 else "")

        return command.lower(), args

    @staticmethod
    def _parse_quoted_args(arg_string: str) -> List[str]:
        """
        Parse command arguments, respecting quoted strings.

        Args:
            arg_string: Argument string to parse

        Returns:
            List of parsed arguments

        Example:
            input: '"path with spaces" unquoted'
            returns: ['path with spaces', 'unquoted']
        """
        # Pattern matches quoted strings or unquoted words
        pattern = r'"([^"]*)"|\S+'
        matches = re.findall(pattern, arg_string)

        # Extract the quoted part if it matched, else the whole match
        args = []
        i = 0
        for match in re.finditer(pattern, arg_string):
            if match.group(1) is not None:
                args.append(match.group(1))  # Quoted string
            else:
                args.append(match.group(0))  # Unquoted word

        return args

    def format_error(self, message: str) -> str:
        """Format an error message with color."""
        return f"[red]Error: {message}[/red]"

    def format_success(self, message: str) -> str:
        """Format a success message with color."""
        return f"[green]{message}[/green]"

    def format_info(self, message: str) -> str:
        """Format an info message with color."""
        return f"[cyan]{message}[/cyan]"

    def format_warning(self, message: str) -> str:
        """Format a warning message with color."""
        return f"[yellow]{message}[/yellow]"
