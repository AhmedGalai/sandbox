# Ollama Multi-Agent System - Core Infrastructure

## Overview

This module provides a production-ready async infrastructure for building multi-agent systems with Ollama. It includes:

- **OllamaClient**: Async HTTP client with connection pooling, retry logic, and streaming support
- **BaseAgent**: Abstract agent class with prompt loading and context formatting
- **AgentOrchestrator**: Orchestration engine with concurrency control and task management
- **Settings**: Configuration management using Pydantic

## Architecture

### Module Structure

```
core/
├── __init__.py                 # Public API exports
├── exceptions.py               # Custom exception classes
├── ollama_client.py            # Async Ollama API client
├── agent.py                    # Agent base classes
└── orchestrator.py             # Task orchestration engine

config/
├── __init__.py                 # Configuration exports
├── settings.py                 # Settings management
└── models.yaml                 # Model assignments

tests/                          # Comprehensive test suite
requirements.txt                # Python dependencies
```

## Components

### 1. OllamaClient

Async HTTP client for Ollama API with advanced features.

**Features:**
- HTTP/2 connection pooling via httpx
- Automatic exponential backoff retry logic
- Streaming response support
- Vision model support
- Type hints throughout

**Key Methods:**

```python
# Text generation
response = await client.generate(
    model="llama3.2:3b",
    prompt="What is AI?",
    temperature=0.7
)

# Streaming generation
async for chunk in client.generate_stream(
    model="llama3.2:3b",
    prompt="Write a story..."
):
    print(chunk, end="", flush=True)

# Vision processing
analysis = await client.vision_generate(
    model="llava:7b",
    image_path="/path/to/image.png",
    prompt="Describe this image"
)

# List available models
models = await client.list_models()

# Get model info
info = await client.get_model_info("llama3.2:3b")
```

**Configuration:**

```python
from core import OllamaClient
from config import get_settings

settings = get_settings()

# Uses settings from environment/config
client = OllamaClient(
    host=settings.ollama_host,  # "http://localhost:11434"
    timeout=settings.timeout,   # 120.0
)
```

### 2. BaseAgent and Agent Implementations

Abstract base class and concrete implementations for agents.

**Agent State Machine:**

```
IDLE → BUSY → COMPLETED
  ↓
ERROR → IDLE
```

**Key Features:**
- Async execution with state tracking
- Prompt loading from markdown files
- Context placeholder replacement
- Error handling and recovery
- Optional streaming support

**Concrete Implementations:**

```python
from core import SimpleAgent, StreamingAgent

# Simple agent - generates complete response
agent = SimpleAgent(
    name="researcher",
    model="qwen2.5:7b",
    prompts_dir=Path("./prompts")
)

# Streaming agent - yields chunks as generated
streaming_agent = StreamingAgent(
    name="writer",
    model="llama3.2:3b"
)
```

**Usage Example:**

```python
# Execute agent with context
response = await agent.execute({
    "prompt_name": "research_query",
    "topic": "Machine Learning",
    "length": "brief"
})

# With streaming
async for chunk in streaming_agent.handle_streaming({
    "prompt_name": "story",
    "theme": "adventure"
}):
    print(chunk, end="", flush=True)
```

**Prompt Template Format:**

Prompts are markdown files in `prompts/{agent_name}/` directory:

```markdown
# Research Query

Please research the following topic: ___topic___

Provide a ___length___ response covering:
- Key concepts
- Current trends
- Notable examples
```

Context placeholders use the format `___key___` where `key` must match a context dictionary key.

### 3. AgentOrchestrator

Manages multi-agent execution with concurrency control.

**Features:**
- Task queue with priority support
- Concurrency limiting (Semaphore)
- Parallel and sequential execution modes
- Result aggregation
- Failure handling callbacks
- Execution metrics

**Usage Examples:**

```python
from core import AgentOrchestrator, TaskPriority

orchestrator = AgentOrchestrator(max_concurrent=3)

# Parallel execution
agents_and_contexts = [
    (researcher_agent, {"topic": "AI"}),
    (developer_agent, {"task": "implement"}),
    (planner_agent, {"goal": "product"}),
]

results = await orchestrator.run_agents_parallel(agents_and_contexts)

# Sequential execution
results = await orchestrator.run_sequential(
    agents_and_contexts,
    stop_on_failure=True
)

# Manual task dispatch
task_id = await orchestrator.dispatch_task(
    agent=my_agent,
    context={"key": "value"},
    priority=TaskPriority.HIGH
)

# Retrieve results
result = orchestrator.get_result(task_id)

# Get summary statistics
summary = orchestrator.get_summary()
print(f"Success rate: {summary['success_rate']:.1%}")
print(f"Avg time: {summary['avg_execution_time']:.2f}s")
```

**Result Handling:**

```python
for result in results:
    if result.success:
        print(f"{result.agent_name}: {result.result}")
    else:
        print(f"{result.agent_name} failed: {result.error}")
        orchestrator.handle_agent_failure(
            result.task_id,
            error_callback=my_error_handler
        )
```

### 4. Settings

Configuration management with environment variable support.

**Environment Variables:**

```bash
OLLAMA_HOST=http://localhost:11434
TIMEOUT=120.0
MAX_CONCURRENT_AGENTS=3
DEFAULT_MODEL=llama3.2:3b
LOG_LEVEL=INFO
```

**Model Mappings (models.yaml):**

```yaml
models:
  researcher: qwen2.5:7b
  developer: llama3.2:3b
  planner: qwen2.5:7b
  vision: llava:7b
  default: llama3.2:3b
```

**Usage:**

```python
from config import get_settings

settings = get_settings()

# Access settings
host = settings.ollama_host
timeout = settings.timeout
max_agents = settings.max_concurrent_agents

# Get model for agent
model = settings.get_model_for_agent("researcher")
# Returns: "qwen2.5:7b"

# Validate configuration
settings.validate_settings()  # Raises ValueError if invalid
```

## Exception Handling

```python
from core.exceptions import (
    OllamaException,           # Base exception
    OllamaConnectionError,     # Connection failures
    AgentExecutionError,       # Agent failures
    AgentTimeoutError,         # Timeout errors
    InvalidModelError,         # Model not found
    VisionProcessingError,     # Vision model errors
    ConfigurationError,        # Config issues
)

try:
    response = await client.generate("llama3.2:3b", "test")
except InvalidModelError:
    print("Model not available, pull it with: ollama pull llama3.2:3b")
except OllamaConnectionError:
    print("Cannot connect to Ollama. Is it running?")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Complete Example

```python
import asyncio
import logging
from pathlib import Path

from core import (
    SimpleAgent,
    AgentOrchestrator,
    OllamaClient,
)
from config import get_settings

logging.basicConfig(level=logging.INFO)

async def main():
    settings = get_settings()

    # Create agents
    researcher = SimpleAgent(
        name="researcher",
        model=settings.get_model_for_agent("researcher"),
        prompts_dir=Path("./prompts")
    )

    developer = SimpleAgent(
        name="developer",
        model=settings.get_model_for_agent("developer"),
        prompts_dir=Path("./prompts")
    )

    # Create orchestrator
    orchestrator = AgentOrchestrator(
        max_concurrent=settings.max_concurrent_agents
    )

    try:
        # Run agents in parallel
        tasks = [
            (researcher, {"topic": "Python async"}),
            (developer, {"language": "Python"}),
        ]

        results = await orchestrator.run_agents_parallel(tasks)

        # Process results
        for result in results:
            if result.success:
                print(f"{result.agent_name}:\n{result.result}\n")
            else:
                print(f"{result.agent_name} failed: {result.error}")

        # Get summary
        summary = orchestrator.get_summary()
        print(f"Executed {summary['total_tasks']} tasks in parallel")

    finally:
        # Cleanup
        await researcher.close()
        await developer.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing

Comprehensive test suite included:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ollama_client.py -v

# Run with coverage
pytest tests/ --cov=core --cov=config

# Run async tests with markers
pytest tests/ -m asyncio
```

**Test Files:**
- `test_ollama_client.py`: HTTP client tests
- `test_agent.py`: Agent behavior tests
- `test_orchestrator.py`: Orchestration tests
- `test_settings.py`: Configuration tests

## Logging

All modules use Python's standard logging:

```python
import logging

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Adjust log levels
logging.getLogger("core.ollama_client").setLevel(logging.DEBUG)
```

## Performance Considerations

1. **Connection Pooling**: OllamaClient reuses HTTP connections via httpx
2. **Concurrency Control**: Semaphore limits concurrent agents (default: 3)
3. **Streaming**: Use `generate_stream()` for large responses
4. **Backoff**: Exponential backoff prevents thundering herd
5. **Timeouts**: All operations have configurable timeouts

## Error Recovery

The system handles failures gracefully:

1. **Connection Errors**: Automatic exponential backoff retry
2. **Agent Failures**: Tracked state, error logging, recovery
3. **Timeouts**: Configurable per operation
4. **Resource Cleanup**: Proper async cleanup with context managers

```python
async with OllamaClient() as client:
    # Automatic cleanup
    response = await client.generate("model", "prompt")

# Or manual cleanup
client = OllamaClient()
try:
    response = await client.generate("model", "prompt")
finally:
    await client.close()
```

## Production Deployment

Recommendations:

1. **Settings**: Use environment variables for configuration
2. **Logging**: Configure structured logging for monitoring
3. **Timeouts**: Adjust based on model response times
4. **Concurrency**: Set `max_concurrent_agents` based on Ollama resources
5. **Error Handling**: Implement custom error callbacks for monitoring
6. **Health Checks**: Periodically verify Ollama connectivity

## Future Extensions

The infrastructure supports:

- Custom agent implementations by extending `BaseAgent`
- Tool/plugin system for agents
- Caching layer for repeated requests
- Metrics/monitoring integration
- Distributed orchestration
- Model fine-tuning pipelines
