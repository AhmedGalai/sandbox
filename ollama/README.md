# Ollama Multi-Agent System

A production-ready, asynchronous multi-agent LLM system powered by Ollama models. This system features specialized AI agents that can work concurrently on research, development, planning, and vision tasks.

## Features

- **Multi-Agent Architecture**: Specialized agents for different tasks (Researcher, Developer, Planner, Vision)
- **Async Execution**: Full async/await support for concurrent agent operations
- **Vision Capabilities**: Built-in image analysis using Llava vision models
- **Rich CLI**: Beautiful command-line interface with formatted output
- **Conversation Management**: Persistent conversation history with export capabilities
- **Model Management**: Easy switching between different Ollama models
- **Extensible**: Plugin system for custom agents

## Quick Start

### Prerequisites

1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai)
2. **Pull Required Models**:
```bash
ollama pull llama3.2:3b
ollama pull qwen2.5:7b
ollama pull llava:7b
```

### Installation

```bash
cd /home/ag/Desktop/sandbox/ollama
pip install -r requirements.txt
```

### Run the CLI

```bash
python main.py
```

## Available Commands

### System Commands
- `/help` - Display all available commands
- `/clear` - Clear console and conversation history
- `/exit`, `/quit` - Exit the application

### Agent Commands
- `/agents` - List all available agents with their status
- `/researcher <query>` - Invoke the research agent
- `/developer <task>` - Invoke the development agent
- `/planner <project>` - Invoke the planning agent
- `/vision <image_path> [question]` - Analyze an image

### Model Commands
- `/models` - List all available Ollama models
- `/use <model>` - Switch to a different default model
- `/pull <model>` - Download a new model from Ollama

### Utility Commands
- `/history` - View conversation history
- `/export <format>` - Export conversation (json/markdown)
- `/settings` - View and modify settings

## Agent Capabilities

### Researcher Agent
- Model: `qwen2.5:7b`
- Use for: Information synthesis, research tasks, knowledge gathering
- Example: `/researcher "AI agents architecture patterns"`

### Developer Agent
- Model: `llama3.2:3b`
- Use for: Code generation, debugging, technical guidance
- Example: `/developer "create a Python async function for API calls"`

### Planner Agent
- Model: `qwen2.5:7b`
- Use for: Project planning, task breakdown, strategic thinking
- Example: `/planner "plan a web application with user auth"`

### Vision Agent
- Model: `llava:7b`
- Use for: Image analysis, OCR, visual understanding
- Example: `/vision screenshot.png "what elements are in this UI?"`

## Project Structure

```
ollama/
├── main.py                 # Main CLI application
├── requirements.txt        # Python dependencies
├── config/
│   ├── settings.py        # Configuration management
│   └── models.yaml        # Model assignments
├── core/
│   ├── agent.py           # Base agent class
│   ├── ollama_client.py   # Async Ollama API client
│   ├── orchestrator.py    # Multi-agent orchestration
│   ├── conversation.py    # Conversation management
│   └── exceptions.py      # Custom exceptions
├── agents/
│   ├── researcher_agent.py
│   ├── developer_agent.py
│   ├── planner_agent.py
│   ├── vision_agent.py
│   ├── agent_factory.py   # Agent creation
│   └── agent_builtin_*.md # Agent prompts
├── commands/
│   ├── help.py
│   ├── agents.py
│   ├── vision.py
│   ├── models.py
│   ├── utils.py
│   └── settings.py
├── examples/              # Usage examples
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## Configuration

Configuration is managed through:
1. Environment variables (`.env` file)
2. YAML configuration (`config/models.yaml`)
3. Pydantic settings (`config/settings.py`)

### Environment Variables

```bash
OLLAMA_HOST=http://localhost:11434
MAX_CONCURRENT_AGENTS=3
DEFAULT_MODEL=llama3.2:3b
REQUEST_TIMEOUT=120
```

### Model Assignments

Edit `config/models.yaml` to change agent-to-model mappings:

```yaml
agents:
  researcher: qwen2.5:7b
  developer: llama3.2:3b
  planner: qwen2.5:7b
  vision: llava:7b
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Adding Custom Agents

1. Create agent prompt file: `agents/agent_builtin_myagent.md`
2. Create agent class: `agents/myagent_agent.py`
3. Register in `agents/__init__.py`

Example agent class:

```python
from core.agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, client, config):
        super().__init__(
            name="myagent",
            model=config.agents.get("myagent", "llama3.2:3b"),
            client=client
        )
        self.prompt_file = "agents/agent_builtin_myagent.md"
```

## Architecture

### Async Execution Flow

```
User Input → Command Parser → Agent Selector
                ↓
          Orchestrator (manages concurrency)
                ↓
    ┌───────────┴───────────┬──────────┐
    ↓                       ↓          ↓
ResearcherAgent      DeveloperAgent  PlannerAgent
    ↓                       ↓          ↓
OllamaClient (async HTTP) → Ollama API
    ↓
Streaming Response → Rich Display
```

### Key Components

- **OllamaClient**: Async HTTP client with retry logic and connection pooling
- **BaseAgent**: Abstract class for all agents with prompt loading and context management
- **AgentOrchestrator**: Manages concurrent agent execution with semaphore-based rate limiting
- **ConversationManager**: Tracks conversation history with persistence
- **CommandRegistry**: Maps slash commands to handlers

## Performance

- **Concurrent Execution**: Up to 3 agents can run simultaneously
- **Streaming Responses**: Real-time output as models generate text
- **Connection Pooling**: Reused HTTP connections for better performance
- **Caching**: LRU cache for repeated queries (optional)

## Troubleshooting

### Ollama Not Running
```
Error: Could not connect to Ollama
Solution: Start Ollama service: ollama serve
```

### Model Not Found
```
Error: Model 'llama3.2:3b' not found
Solution: Pull the model: ollama pull llama3.2:3b
```

### Vision Analysis Fails
```
Error: VisionProcessingError
Solution: Ensure image is valid format (PNG/JPEG/GIF/WEBP) and <10MB
```

## Documentation

- [CLI Guide](docs/CLI_GUIDE.md) - Complete command reference
- [Quick Start](docs/QUICK_START_CLI.md) - Get started in 5 minutes
- [Architecture](docs/COMMAND_SYSTEM_ARCHITECTURE.md) - Technical details
- [API Reference](docs/API_REFERENCE.md) - Developer reference

## Examples

### Research and Plan Workflow

```python
# In CLI:
/researcher "modern web frameworks 2025"
# Agent provides research summary

/planner "build a web app with the recommended framework"
# Agent creates project plan
```

### Image Analysis

```python
/vision screenshot.png "identify all UI components"
# Vision agent analyzes image and lists components
```

### Parallel Execution

```python
# Multiple agents can work concurrently
# Start researcher in background, then query developer
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/`
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Credits

Built with:
- [Ollama](https://ollama.ai) - Local LLM runtime
- [Rich](https://github.com/Textualize/rich) - Terminal formatting
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [Pydantic](https://pydantic.dev/) - Data validation

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/ollama-agents/issues)
- Documentation: See `docs/` directory

---

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-11-27
