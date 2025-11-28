# Ollama Multi-Agent CLI Guide

A full-featured async command-line interface for managing and orchestrating multiple AI agents powered by Ollama.

## Features

- **Async Command System**: Full async/await support throughout the CLI
- **Command Registry**: Extensible command routing system with aliases
- **Conversation Management**: Persistent conversation history with export functionality
- **Agent Orchestration**: Run multiple agents in parallel or sequentially
- **Rich UI**: Beautiful formatted output with tables, panels, and progress indicators
- **Error Handling**: Comprehensive error messages and graceful error recovery
- **Signal Handling**: Proper Ctrl+C handling with graceful shutdown

## Running the CLI

```bash
# Basic startup
python main.py

# With environment variables
OLLAMA_HOST=http://localhost:11434 python main.py

# With default model override
DEFAULT_MODEL=llama3.2:3b python main.py
```

## Available Commands

### Help and Information

#### `/help [command]`
Display all available commands or get detailed help for a specific command.

```bash
/help                  # Show all available commands
/help agents           # Get detailed help for /agents command
/help vision           # Get detailed help for /vision command
/?                     # Alias for /help
/h                     # Alias for /help
```

### Agent Commands

#### `/agents`
List all available agents with their assigned models and descriptions.

```bash
/agents
```

#### `/researcher <query> [options]`
Invoke the researcher agent for information gathering and analysis.

```bash
/researcher "how does photosynthesis work"
/researcher "latest AI trends" --context "technology"
/researcher "climate change impacts" --model llama3.2:3b
```

Options:
- `--model MODEL` - Specify a different model to use
- `--context TEXT` - Provide additional context for the research

#### `/developer <task> [options]`
Invoke the developer agent for code generation and technical tasks.

```bash
/developer "create a REST API endpoint"
/developer "fix this bug in my code" --language javascript
/developer "write unit tests" --model llama3.2:3b
```

Options:
- `--model MODEL` - Specify a different model to use
- `--language LANG` - Programming language (default: python)

#### `/planner <task> [options]`
Invoke the planner agent for planning and strategy tasks.

```bash
/planner "create a project roadmap for next quarter"
/planner "plan a website redesign" --scope "full-site"
/planner "organize team workflow" --model qwen2.5:7b
```

Options:
- `--model MODEL` - Specify a different model to use
- `--scope SCOPE` - Scope of planning (default: project)

### Vision Commands

#### `/vision <image_path> [question] [options]`
Analyze images using the vision agent with optional custom questions.

```bash
/vision /path/to/image.jpg
/vision /path/to/image.png "What's in this image?"
/vision image.jpg "Identify objects" --model llava:7b
```

Arguments:
- `image_path` - Path to the image file (required)
- `question` - Question or instruction about the image (optional)

Options:
- `--question TEXT` - Question to ask about the image
- `--model MODEL` - Specify a different vision model to use

Supported image formats: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`

### Model Management Commands

#### `/models`
List all Ollama models installed locally.

```bash
/models
```

#### `/use <model_name>`
Switch the default model used by agents.

```bash
/use llama3.2:3b
/use qwen2.5:7b
/use mistral:latest
```

#### `/pull <model_name>`
Download a new model from the Ollama repository.

```bash
/pull llama3.2:3b
/pull qwen2.5:7b
/pull mistral:latest
/pull neural-chat:latest
/pull llava:7b
```

Popular models:
- `llama3.2:3b` - Small, fast Llama model
- `qwen2.5:7b` - Qwen 2.5 7B model
- `mistral:latest` - Mistral instruction-tuned model
- `neural-chat:latest` - Neural Chat model
- `llava:7b` - Vision model for image analysis

### Utility Commands

#### `/clear`
Clear the console screen and conversation history.

```bash
/clear
/cls           # Alias
```

#### `/history [limit]`
Display recent conversation history.

```bash
/history           # Show last 20 messages
/history 50        # Show last 50 messages
/history 100       # Show last 100 messages
```

#### `/export [filename] [options]`
Export conversation history to a file (markdown or JSON).

```bash
/export                    # Export to timestamped file
/export my_conversation    # Export to my_conversation.markdown
/export data --format json # Export as JSON format
```

Options:
- `--format FORMAT` - Output format: `markdown` or `json` (default: markdown)

Exports are saved to `~/.ollama_agents/exports/`

### Settings Command

#### `/settings [option]`
View and modify application settings.

```bash
/settings              # Show all settings
/settings view         # Show all settings
/settings agents       # Show agent-specific settings
```

Available options:
- (no option) - Display current settings
- `view` - Display current settings
- `agents` - Show agent model assignments

### System Commands

#### `/exit` or `/quit` or `/q`
Exit the CLI application.

```bash
/exit
/quit
/q
```

## Keyboard Shortcuts

- `Ctrl+C` - Show exit prompt (use `/exit` to quit)
- `Ctrl+D` - Exit the CLI
- `Tab` - Command auto-completion (coming soon)

## Configuration

Configuration is managed through environment variables and the `.env` file.

### Environment Variables

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434

# Model Configuration
DEFAULT_MODEL=llama3.2:3b

# Concurrency Settings
MAX_CONCURRENT_AGENTS=3

# Request Timeout (seconds)
TIMEOUT=120

# Logging
LOG_LEVEL=INFO
```

### Example `.env` file

```env
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=llama3.2:3b
MAX_CONCURRENT_AGENTS=3
TIMEOUT=120
LOG_LEVEL=INFO
```

## Conversation History

Conversations are automatically saved to `~/.ollama_agents/history.json`.

- **Auto-save**: Conversations are saved after each message
- **Persistence**: History persists across sessions
- **Rolling Window**: Last 100 messages are kept in memory
- **Export**: Use `/export` to save conversations to file

## Command Architecture

### Adding New Commands

To add a new command:

1. Create a new file in the `commands/` directory: `mycommand.py`
2. Define a class that inherits from `BaseCommand`
3. Implement `execute()` and `get_help_text()` methods
4. Register in `commands/__init__.py`

Example:

```python
from commands.base import BaseCommand
from typing import Any, Dict, List, Tuple

class MyCommand(BaseCommand):
    """Description of my command."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Execute the command."""
        try:
            # Your command logic here
            return True, "Success message"
        except Exception as e:
            return False, f"Error: {e}"

    def get_help_text(self) -> str:
        """Return help text."""
        return "/mycommand\n\nDescription and usage..."
```

Then register in `commands/__init__.py`:

```python
from .mycommand import MyCommand

COMMAND_REGISTRY = {
    # ... existing commands ...
    "mycommand": MyCommand,
}
```

### BaseCommand Class

The `BaseCommand` abstract base class provides:

- `execute(args, context)` - Main command execution method (must override)
- `get_help_text()` - Help text for the command (must override)
- `validate_args()` - Argument validation utility
- `parse_arguments()` - Parse positional and named arguments
- `extract_command_and_args()` - Extract command from user input
- `_parse_quoted_args()` - Parse quoted arguments
- `format_error()`, `format_success()`, `format_info()`, `format_warning()` - Rich text formatting

## Conversation Manager

The `ConversationManager` class handles:

- **Adding messages**: `await manager.add_message(role, content, metadata)`
- **Retrieving history**: `await manager.get_history(limit=20)`
- **Clearing history**: `await manager.clear()`
- **Exporting**: `await manager.export(output_path, format='json')`
- **Searching**: `await manager.search(query)`
- **Statistics**: `await manager.get_summary()`

Messages are stored with:
- Timestamp (ISO format)
- Role (user, assistant, agent, system)
- Content
- Metadata (agent_name, task_id, etc.)

## Error Handling

The CLI provides comprehensive error handling:

- **Command Errors**: Invalid command or arguments show helpful error messages
- **Agent Errors**: Agent execution failures are caught and reported
- **Connection Errors**: Ollama connection issues are handled gracefully
- **File Errors**: Missing or invalid files are reported clearly
- **Async Errors**: Proper error propagation in async operations

## Logging

Logging is configured to show:
- Timestamp
- Logger name
- Log level
- Message

Set `LOG_LEVEL` environment variable to control verbosity:
- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical error messages

## Performance Considerations

- **Concurrency**: Max 3 agents by default (configurable)
- **Timeout**: 120 seconds per request (configurable)
- **Memory**: Rolling window keeps last 100 messages
- **History File**: Stored in `.ollama_agents/history.json`

## Troubleshooting

### Cannot connect to Ollama
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve
```

### Model not found
```bash
# List available models
/models

# Download a model
/pull llama3.2:3b
```

### Command not working
```bash
# Check command syntax
/help commandname

# Verify arguments
# Use quotes for arguments with spaces: "this is an argument"
```

### History not saving
```bash
# Check directory permissions
ls -la ~/.ollama_agents/

# Check disk space
df -h
```

## Advanced Usage

### Running Multiple Agents in Parallel

The orchestrator automatically runs agents in parallel:

```bash
/researcher "topic A"
/developer "task B"
/planner "plan C"
```

All three will execute concurrently (up to `MAX_CONCURRENT_AGENTS`).

### Custom Model for Agent

Override the model for a specific agent:

```bash
/researcher "query" --model mistral:latest
/developer "task" --model llama3.2:3b
/vision image.jpg --model llava:7b
```

### Exporting for Analysis

Export conversations for further analysis:

```bash
# Export as markdown (human-readable)
/export research_results

# Export as JSON (machine-readable)
/export data --format json
```

## API Reference

See `API_REFERENCE.md` for detailed API documentation.

## Troubleshooting Commands

To verify the CLI is working correctly:

1. Check Ollama connection: `/models`
2. List agents: `/agents`
3. Check settings: `/settings`
4. View history: `/history`

## Contributing

To contribute new commands or improvements:

1. Create a new command class in `commands/`
2. Implement the `BaseCommand` interface
3. Add tests in `tests/`
4. Register in `commands/__init__.py`
5. Update this documentation

## License

Same as the main project.
