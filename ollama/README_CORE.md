# Ollama Multi-Agent System - Core Infrastructure

A production-ready async Python framework for building multi-agent systems with Ollama.

## Quick Start

### Installation

```bash
# Clone or download the project
cd ollama

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# OLLAMA_HOST=http://localhost:11434
# TIMEOUT=120.0
# MAX_CONCURRENT_AGENTS=3
```

### Ensure Ollama is Running

```bash
# Start Ollama if not already running
ollama serve

# In another terminal, verify connectivity
curl http://localhost:11434/api/tags
```

## Core Components

### 1. OllamaClient - Async HTTP Client

Async client for Ollama API with connection pooling and retry logic.

```python
from core import OllamaClient

async with OllamaClient() as client:
    # Text generation
    response = await client.generate(
        model="llama3.2:3b",
        prompt="What is Python?",
        temperature=0.7
    )

    # Streaming generation
    async for chunk in client.generate_stream(
        model="llama3.2:3b",
        prompt="Write a poem..."
    ):
        print(chunk, end="", flush=True)

    # Vision processing
    analysis = await client.vision_generate(
        model="llava:7b",
        image_path="image.jpg",
        prompt="What's in this image?"
    )

    # List available models
    models = await client.list_models()
```

### 2. BaseAgent - Agent Framework

Abstract base class for implementing custom agents.

```python
from core import SimpleAgent

# SimpleAgent for basic text generation
agent = SimpleAgent(
    name="researcher",
    model="qwen2.5:7b"
)

response = await agent.execute({
    "topic": "Machine Learning",
    "length": "detailed"
})
```

**Create Custom Agent:**

```python
from core import BaseAgent

class MyAgent(BaseAgent):
    async def _execute_internal(self, context):
        # Custom logic here
        prompt = f"Process: {context.get('input')}"
        return await self.client.generate(
            model=self.model,
            prompt=prompt
        )

agent = MyAgent(name="custom", model="llama3.2:3b")
```

### 3. AgentOrchestrator - Task Management

Orchestrate multiple agents with concurrency control.

```python
from core import AgentOrchestrator, TaskPriority

orchestrator = AgentOrchestrator(max_concurrent=3)

# Parallel execution
agents_and_contexts = [
    (researcher_agent, {"topic": "AI"}),
    (developer_agent, {"task": "code"}),
]

results = await orchestrator.run_agents_parallel(
    agents_and_contexts,
    timeout=60.0
)

for result in results:
    if result.success:
        print(f"{result.agent_name}: {result.result}")
    else:
        print(f"{result.agent_name} failed: {result.error}")
```

### 4. Settings - Configuration Management

Centralized configuration via environment variables and YAML.

```python
from config import get_settings

settings = get_settings()

print(settings.ollama_host)        # http://localhost:11434
print(settings.timeout)            # 120.0
print(settings.max_concurrent_agents)  # 3

model = settings.get_model_for_agent("researcher")
# Returns from models.yaml: "qwen2.5:7b"
```

## File Structure

```
core/
├── exceptions.py       # Custom exception classes
├── ollama_client.py    # Async Ollama API client
├── agent.py            # BaseAgent and implementations
├── orchestrator.py     # AgentOrchestrator for multi-agent orchestration
└── __init__.py        # Public API

config/
├── settings.py         # Pydantic-based configuration
├── models.yaml         # Model assignments
└── __init__.py

tests/
├── test_ollama_client.py
├── test_agent.py
├── test_orchestrator.py
├── test_settings.py
└── __init__.py

examples/
└── basic_usage.py      # Usage examples

requirements.txt        # Python dependencies
pytest.ini             # Pytest configuration
.env.example           # Environment template
CORE_INFRASTRUCTURE.md # Detailed documentation
```

## Exception Handling

```python
from core.exceptions import (
    InvalidModelError,
    OllamaConnectionError,
    AgentExecutionError,
    VisionProcessingError,
)

try:
    response = await client.generate("invalid:model", "prompt")
except InvalidModelError as e:
    print(f"Model not found: {e}")
except OllamaConnectionError as e:
    print(f"Connection failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ollama_client.py -v

# Run with coverage
pytest tests/ --cov=core --cov=config

# Run only async tests
pytest tests/ -m asyncio

# Run specific test
pytest tests/test_agent.py::test_agent_initialization -v
```

## Logging

Configure logging in your application:

```python
import logging

# Basic configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Adjust specific module levels
logging.getLogger("core.ollama_client").setLevel(logging.DEBUG)
logging.getLogger("core.orchestrator").setLevel(logging.INFO)
```

## Common Patterns

### Pattern 1: Simple Sequential Processing

```python
async def process_tasks():
    agent = SimpleAgent(name="worker", model="llama3.2:3b")

    tasks = [
        {"input": "Task 1"},
        {"input": "Task 2"},
        {"input": "Task 3"},
    ]

    for task in tasks:
        result = await agent.execute(task)
        print(result)

    await agent.close()
```

### Pattern 2: Parallel Agent Execution

```python
async def parallel_analysis():
    orchestrator = AgentOrchestrator(max_concurrent=3)

    agents_tasks = [
        (agent1, {"data": "..."}),
        (agent2, {"data": "..."}),
        (agent3, {"data": "..."}),
    ]

    results = await orchestrator.run_agents_parallel(agents_tasks)

    # Process results
    summary = orchestrator.get_summary()
    print(f"Success rate: {summary['success_rate']:.0%}")
```

### Pattern 3: Task Priority

```python
async def priority_dispatch():
    orchestrator = AgentOrchestrator(max_concurrent=2)

    # Dispatch tasks with different priorities
    low_id = await orchestrator.dispatch_task(
        agent, context, priority=TaskPriority.LOW
    )

    high_id = await orchestrator.dispatch_task(
        agent, context, priority=TaskPriority.HIGH
    )

    # High priority tasks execute first
```

### Pattern 4: Error Handling with Callbacks

```python
def handle_failure(task_id, error):
    print(f"Task {task_id} failed: {error}")
    # Send alert, log, retry, etc.

orchestrator.handle_agent_failure(
    task_id,
    error_callback=handle_failure
)
```

## Performance Tips

1. **Connection Pooling**: Reuse OllamaClient instances
2. **Concurrency**: Adjust `max_concurrent_agents` based on Ollama resources
3. **Streaming**: Use `generate_stream()` for large responses
4. **Timeouts**: Set appropriate timeouts for your use case
5. **Batch Processing**: Use orchestrator for parallel execution

## Troubleshooting

### Connection Refused
```
Error: Connection failed to http://localhost:11434
```
**Solution**: Ensure Ollama is running: `ollama serve`

### Model Not Found
```
InvalidModelError: Model 'llama3.2:3b' not found
```
**Solution**: Pull the model: `ollama pull llama3.2:3b`

### Timeout Errors
```
AgentTimeoutError: Operation timed out after 120s
```
**Solution**: Increase timeout in settings or reduce workload

### Import Errors
```
ModuleNotFoundError: No module named 'core'
```
**Solution**: Ensure you're running from project root and have installed requirements

## Architecture Decisions

1. **Async/Await**: Full async support for I/O operations
2. **Type Hints**: Complete type annotations for IDE support
3. **Pydantic Settings**: Flexible configuration management
4. **Connection Pooling**: httpx handles HTTP/2 pooling
5. **Semaphore Concurrency**: Built-in asyncio concurrency control
6. **Priority Queue**: Tasks ordered by priority then creation time

## Security Notes

- All connections to Ollama should be HTTPS in production
- Use environment variables for sensitive configuration
- Validate user inputs before passing to models
- Monitor logs for unusual model activity
- Rate limit if exposing via API

## Contributing

Extend the system by:

1. Creating custom agent classes inheriting from `BaseAgent`
2. Adding specialized orchestration logic
3. Implementing custom error handlers
4. Creating domain-specific prompt templates

## License

[Your license here]

## Support

For issues, questions, or contributions:
- Check CORE_INFRASTRUCTURE.md for detailed documentation
- Review test files for usage examples
- Check examples/basic_usage.py for working code
