# Command System Architecture

## Overview

The Ollama CLI uses a modular command system with the following architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    OllamaAgentCLI                           │
│  (Main event loop, input handling, signal management)       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├─► Command Router
                       │   (Parse input, route to commands)
                       │
                       ├─► Command Registry
                       │   (Map names to command classes)
                       │
                       └─► Conversation Manager
                           (History, persistence, export)

┌──────────────────────────────────────────────────────────────┐
│                    Command Classes                           │
├──────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │           BaseCommand (Abstract)                        │ │
│ │  - execute(args, context)                              │ │
│ │  - get_help_text()                                     │ │
│ │  - validate_args()                                     │ │
│ │  - parse_arguments()                                   │ │
│ │  - format_* methods (error, success, info, warning)   │ │
│ └─────────────────────────────────────────────────────────┘ │
│           ▲         ▲         ▲         ▲                   │
│           │         │         │         │                   │
│  ┌────────┴┐  ┌────┴──┐  ┌───┴───┐  ┌─┴──────────┐         │
│  │ Agents  │  │Vision │  │Models │  │ Utilities  │  ...   │
│  │Commands │  │Command│  │Cmds   │  │ Commands   │         │
│  └────────┘  └───────┘  └───────┘  └────────────┘         │
└──────────────────────────────────────────────────────────────┘
```

## File Structure

```
commands/
├── __init__.py              # Command registry and exports
├── base.py                  # BaseCommand abstract class
├── help.py                  # HelpCommand
├── agents.py                # Agent-related commands
│   ├── AgentsCommand        # List agents
│   ├── ResearcherCommand    # Invoke researcher
│   ├── DeveloperCommand     # Invoke developer
│   └── PlannerCommand       # Invoke planner
├── vision.py                # VisionCommand
├── models.py                # Model management commands
│   ├── ModelsCommand        # List models
│   ├── UseCommand           # Switch default model
│   └── PullCommand          # Download model
├── utils.py                 # Utility commands
│   ├── ClearCommand         # Clear screen/history
│   ├── HistoryCommand       # View history
│   └── ExportCommand        # Export conversations
└── settings.py              # SettingsCommand

core/
├── conversation.py          # ConversationManager (NEW)
├── ...other existing files...
```

## Core Components

### 1. BaseCommand (commands/base.py)

Abstract base class for all commands. Provides common functionality:

```python
class BaseCommand(ABC):
    async def execute(args, context) -> (bool, str):
        """Execute the command. Return (success, output)"""

    def get_help_text() -> str:
        """Return formatted help text"""

    def validate_args(min_args, max_args) -> bool:
        """Validate argument count"""

    def parse_arguments(args, named_params) -> (list, dict):
        """Parse positional and named arguments"""
```

### 2. OllamaAgentCLI (main.py)

Main CLI application managing:
- Event loop and async operations
- Command routing and execution
- Signal handling (Ctrl+C, Ctrl+D)
- Conversation management
- Resource cleanup

Key methods:
- `run()` - Main event loop
- `process_input()` - Route commands vs messages
- `_handle_command()` - Execute commands
- `shutdown()` - Graceful cleanup

### 3. ConversationManager (core/conversation.py)

Handles conversation persistence and history:

```python
class ConversationManager:
    async def add_message(role, content, metadata) -> dict
    async def get_history(limit) -> list
    async def get_window() -> list
    async def clear() -> None
    async def export(output_path, format) -> Path
    async def search(query, limit) -> list
    async def get_summary() -> dict
```

## Command Execution Flow

```
User Input
    │
    ▼
parse_input()
    │
    ├─► /command?
    │     │
    │     ▼
    │   _handle_command()
    │     │
    │     ├─► Parse command name
    │     ├─► Check aliases
    │     ├─► Lookup in registry
    │     ├─► Create command instance
    │     ├─► Parse arguments
    │     ├─► Execute with progress
    │     └─► Handle response
    │
    └─► Plain message?
          │
          ▼
        _handle_message()
          (Future: agent inference)
```

## Command Registry

Located in `commands/__init__.py`:

```python
COMMAND_REGISTRY = {
    # Help
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

COMMAND_ALIASES = {
    "?": "help",
    "h": "help",
    "cls": "clear",
    "quit": "exit",
    "q": "exit",
}
```

## Context Dictionary

Passed to all commands, contains:

```python
context = {
    "settings": Settings,              # Application settings
    "ollama_client": OllamaClient,     # Ollama API client
    "agent_factory": AgentFactory,     # Agent creation factory
    "orchestrator": AgentOrchestrator, # Task orchestration
    "conversation_manager": ConversationManager,
    "command_registry": dict,          # Registry mapping
    "cli": OllamaAgentCLI,            # CLI instance
}
```

## Adding a New Command

### Step 1: Create the command file

```python
# commands/mycommand.py
from typing import Any, Dict, List, Tuple
from .base import BaseCommand

class MyCommand(BaseCommand):
    """Description of what the command does."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Execute the command."""
        try:
            # Validate arguments
            self.validate_args(args, min_args=0, max_args=2)

            # Parse arguments
            positional, named = self.parse_arguments(
                args,
                named_params=['option1', 'option2']
            )

            # Get context resources
            factory = context.get("agent_factory")

            # Execute logic
            result = await factory.create_agent("researcher")

            # Return success with output
            return True, "Success message"

        except ValueError as e:
            return False, f"Invalid arguments: {e}"
        except Exception as e:
            return False, f"Error: {e}"

    def get_help_text(self) -> str:
        """Return formatted help text."""
        return """[bold cyan]/mycommand[/bold cyan] [options]

Description of your command.

Usage:
  /mycommand              - Basic usage
  /mycommand arg1 arg2    - With arguments
  /mycommand --option1 value

Options:
  --option1 VALUE    - Description
  --option2 VALUE    - Description
"""
```

### Step 2: Register the command

Edit `commands/__init__.py`:

```python
from .mycommand import MyCommand

COMMAND_REGISTRY = {
    # ... existing commands ...
    "mycommand": MyCommand,
}
```

### Step 3: Update help text

The help system will automatically pick up your command.

## Error Handling

Commands should return `(False, error_message)` for errors:

```python
async def execute(self, args, context):
    try:
        self.validate_args(args, min_args=1)
        # ... command logic ...
        return True, "Success"
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        logger.error(f"Error: {e}")
        return False, f"Command failed: {e}"
```

The CLI handles the response:

```python
success, output = await command.execute(args, context)

if success:
    self.console.print(output)
    await self.conversation_manager.add_message("system", output)
else:
    self.console.print(f"[red]{output}[/red]")
    await self.conversation_manager.add_message(
        "system", output, {"error": True}
    )
```

## Async Patterns

All commands use async/await:

```python
# Pattern 1: Async operation
async def execute(self, args, context):
    result = await some_async_operation()
    return True, result

# Pattern 2: Multiple async operations
async def execute(self, args, context):
    orchestrator = context.get("orchestrator")
    task_id = await orchestrator.dispatch_task(agent, context)
    return True, f"Task {task_id} dispatched"

# Pattern 3: Async context manager
async def execute(self, args, context):
    client = context.get("ollama_client")
    async with client:
        models = await client.list_models()
    return True, str(models)
```

## Testing Commands

Example test structure:

```python
# tests/test_commands.py
import pytest
from commands.mycommand import MyCommand
from rich.console import Console

@pytest.mark.asyncio
async def test_mycommand_success():
    cmd = MyCommand(Console())
    context = {
        "agent_factory": mock_factory,
        "orchestrator": mock_orchestrator,
    }
    success, output = await cmd.execute(["arg1"], context)
    assert success is True
    assert "expected" in output

@pytest.mark.asyncio
async def test_mycommand_invalid_args():
    cmd = MyCommand(Console())
    context = {}
    success, output = await cmd.execute([], context)
    assert success is False
```

## Conversation Persistence

Commands can record interactions:

```python
async def execute(self, args, context):
    conversation_manager = context.get("conversation_manager")

    # Record command execution
    await conversation_manager.add_message(
        "system",
        f"Executed /mycommand with args: {args}",
        {"command": "mycommand"}
    )

    return True, "Done"
```

## Performance Considerations

1. **Long-running operations**: Show progress indicator
```python
with Progress(...) as progress:
    progress.add_task("Processing...", total=None)
    result = await long_operation()
```

2. **Batch operations**: Use orchestrator for parallel execution
```python
results = await orchestrator.run_agents_parallel([
    (agent1, context1),
    (agent2, context2),
])
```

3. **Memory management**: Be mindful of large result sets
```python
# Limit history retrieval
history = await conv_manager.get_history(limit=50)
```

## Best Practices

1. **Input validation**: Always validate arguments
2. **Error handling**: Catch and report errors clearly
3. **Logging**: Use logger for debugging
4. **Documentation**: Provide help text and docstrings
5. **Async consistency**: Always use async/await
6. **Resource cleanup**: Close connections properly
7. **User feedback**: Give clear success/failure messages

## Command Categories

### System Commands
- `/help` - Help system
- `/clear` - Clear screen
- `/exit` - Exit CLI

### Agent Commands
- `/agents` - List agents
- `/researcher`, `/developer`, `/planner` - Invoke agents

### Vision Commands
- `/vision` - Analyze images

### Model Commands
- `/models` - List models
- `/use` - Switch model
- `/pull` - Download model

### Utility Commands
- `/history` - View history
- `/export` - Export conversations

### Settings
- `/settings` - View/modify settings

## Future Enhancements

1. **Command auto-completion**: Tab-completion for commands
2. **Streaming responses**: Real-time output for long operations
3. **Interactive prompts**: Built-in prompts for commands
4. **Script support**: Execute command scripts
5. **Macros**: Define custom command sequences
6. **Remote commands**: SSH/HTTP-based command execution

## Debugging

Enable debug logging:

```bash
LOG_LEVEL=DEBUG python main.py
```

This will show:
- Command parsing details
- Argument validation steps
- Agent execution flow
- Conversation persistence events
