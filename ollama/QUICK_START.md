# Quick Start Guide - Ollama Multi-Agent System

Get up and running in 5 minutes.

## Prerequisites

- Python 3.8+
- Ollama running locally (http://localhost:11434)
- pip or similar package manager

## Installation

```bash
# Navigate to project directory
cd /home/ag/Desktop/sandbox/ollama

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit if needed (defaults work for localhost Ollama)
# nano .env
```

## Verify Setup

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Run tests to verify installation
pytest tests/ -v
```

## 5-Minute Examples

### Example 1: Simple Text Generation

```python
import asyncio
from core import OllamaClient

async def main():
    client = OllamaClient()
    response = await client.generate(
        model="llama3.2:3b",
        prompt="What is async programming?"
    )
    print(response)
    await client.close()

asyncio.run(main())
```

### Example 2: Using an Agent

```python
import asyncio
from core import SimpleAgent

async def main():
    agent = SimpleAgent(
        name="assistant",
        model="llama3.2:3b"
    )

    # Direct generation without prompt files
    response = await agent.client.generate(
        model=agent.model,
        prompt="Explain Python decorators in 2 paragraphs"
    )
    print(response)
    await agent.close()

asyncio.run(main())
```

### Example 3: Parallel Agents

```python
import asyncio
from core import SimpleAgent, AgentOrchestrator

async def main():
    orch = AgentOrchestrator(max_concurrent=2)

    agent1 = SimpleAgent("worker1", "llama3.2:3b")
    agent2 = SimpleAgent("worker2", "llama3.2:3b")

    # Simple sequential example (parallel requires prompts)
    results = await orch.run_sequential([
        (agent1, {}),
        (agent2, {}),
    ])

    for result in results:
        print(f"{result.agent_name}: {result.success}")

asyncio.run(main())
```

### Example 4: Streaming Response

```python
import asyncio
from core import OllamaClient

async def main():
    client = OllamaClient()

    print("Generating... ", end="", flush=True)
    async for chunk in client.generate_stream(
        model="llama3.2:3b",
        prompt="Write a short haiku about programming"
    ):
        print(chunk, end="", flush=True)
    print()

    await client.close()

asyncio.run(main())
```

### Example 5: Configuration

```python
from config import get_settings

settings = get_settings()

print(f"Host: {settings.ollama_host}")
print(f"Timeout: {settings.timeout}s")
print(f"Max Concurrent: {settings.max_concurrent_agents}")

# Get model for agent
model = settings.get_model_for_agent("researcher")
print(f"Researcher model: {model}")
```

## Common Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_ollama_client.py::test_generate_success -v

# Run with coverage
pytest tests/ --cov=core --cov=config

# List available models
python -c "
import asyncio
from core import OllamaClient
async def show_models():
    async with OllamaClient() as c:
        models = await c.list_models()
        for m in models: print(f'  - {m[\"name\"]}')
asyncio.run(show_models())
"

# Check if Ollama is running
curl http://localhost:11434/api/tags
```

## Directory Structure

```
core/               - Core async infrastructure
  ├── exceptions.py - Custom exceptions
  ├── ollama_client.py - HTTP client
  ├── agent.py - Agent framework
  ├── orchestrator.py - Task orchestration
  └── __init__.py - Public API

config/            - Configuration management
  ├── settings.py - Pydantic settings
  ├── models.yaml - Model assignments
  └── __init__.py

tests/             - Test suite (40+ tests)
  ├── test_ollama_client.py
  ├── test_agent.py
  ├── test_orchestrator.py
  └── test_settings.py

examples/          - Usage examples
  └── basic_usage.py

Documentation files:
  ├── README_CORE.md - Full README
  ├── CORE_INFRASTRUCTURE.md - Architecture guide
  ├── API_REFERENCE.md - Complete API docs
  └── QUICK_START.md - This file
```

## Key Classes

| Class | Purpose |
|-------|---------|
| `OllamaClient` | Async HTTP client for Ollama API |
| `BaseAgent` | Abstract agent class (extend for custom agents) |
| `SimpleAgent` | Basic text generation agent |
| `StreamingAgent` | Agent with streaming support |
| `AgentOrchestrator` | Multi-agent orchestration |
| `Settings` | Configuration management |

## Key Methods

```python
# OllamaClient
await client.generate(model, prompt)           # Text generation
await client.generate_stream(model, prompt)    # Streaming
await client.vision_generate(model, image)     # Vision
await client.list_models()                     # List available
await client.close()                           # Cleanup

# BaseAgent
await agent.execute(context)                   # Execute agent
agent.load_prompt(name)                        # Load template
agent.format_context(template, placeholders)   # Replace values
agent.get_state()                              # Get state
agent.get_status()                             # Get status
await agent.close()                            # Cleanup

# AgentOrchestrator
await orch.dispatch_task(agent, context)       # Queue task
await orch.run_agents_parallel(tasks)          # Parallel exec
await orch.run_sequential(tasks)               # Sequential exec
orch.get_result(task_id)                       # Get result
orch.get_summary()                             # Get stats

# Settings
settings.get_model_for_agent(name)             # Get model
settings.validate_settings()                   # Validate config
```

## Troubleshooting

### "Connection refused"
Ollama not running. Start it:
```bash
ollama serve
```

### "Model not found"
Pull the model:
```bash
ollama pull llama3.2:3b
ollama pull qwen2.5:7b
```

### "ModuleNotFoundError"
Install dependencies:
```bash
pip install -r requirements.txt
```

### Tests fail
Ensure Ollama is running and check:
```bash
curl http://localhost:11434/api/tags
```

## Next Steps

1. Read [README_CORE.md](README_CORE.md) for full documentation
2. Check [API_REFERENCE.md](API_REFERENCE.md) for detailed API docs
3. Review [examples/basic_usage.py](examples/basic_usage.py) for working code
4. Explore [CORE_INFRASTRUCTURE.md](CORE_INFRASTRUCTURE.md) for architecture details

## Environment Variables

```bash
OLLAMA_HOST=http://localhost:11434    # Ollama API endpoint
TIMEOUT=120.0                          # Request timeout
MAX_CONCURRENT_AGENTS=3                # Max concurrent agents
DEFAULT_MODEL=llama3.2:3b              # Default model
LOG_LEVEL=INFO                         # Logging level
```

## File Locations

- **Core code**: `/home/ag/Desktop/sandbox/ollama/core/`
- **Config**: `/home/ag/Desktop/sandbox/ollama/config/`
- **Tests**: `/home/ag/Desktop/sandbox/ollama/tests/`
- **Examples**: `/home/ag/Desktop/sandbox/ollama/examples/`
- **Docs**: `/home/ag/Desktop/sandbox/ollama/*.md`

## Features Summary

- Async/await throughout
- Connection pooling & HTTP/2
- Exponential backoff retry
- Task orchestration with priorities
- Concurrency control (semaphore)
- Vision model support
- Streaming responses
- Type hints everywhere
- 40+ tests
- Production-ready error handling
- Comprehensive documentation

Ready to build your multi-agent system!
