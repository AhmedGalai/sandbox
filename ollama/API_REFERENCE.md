# API Reference - Ollama Multi-Agent System

Complete API reference for all core components.

## OllamaClient

Async HTTP client for Ollama API.

### Initialization

```python
OllamaClient(
    host: str = "http://localhost:11434",
    timeout: float = 120.0,
    max_retries: int = 3,
    initial_backoff: float = 1.0
)
```

**Parameters:**
- `host`: Ollama API endpoint
- `timeout`: Request timeout in seconds
- `max_retries`: Number of retry attempts on connection failure
- `initial_backoff`: Initial backoff delay for exponential backoff

**Returns:** OllamaClient instance

**Example:**
```python
client = OllamaClient(
    host="http://localhost:11434",
    timeout=60.0
)
```

### Methods

#### `async generate(model, prompt, system=None, temperature=0.7, top_k=40, top_p=0.9) -> str`

Generate text completion for a prompt.

**Parameters:**
- `model` (str): Model name
- `prompt` (str): Input prompt
- `system` (str, optional): System message
- `temperature` (float): Sampling temperature (0.0-1.0), default: 0.7
- `top_k` (int): Top-k sampling, default: 40
- `top_p` (float): Top-p sampling, default: 0.9

**Returns:** Generated text response

**Raises:**
- `InvalidModelError`: Model not found
- `OllamaConnectionError`: Connection failed

**Example:**
```python
response = await client.generate(
    model="llama3.2:3b",
    prompt="What is AI?",
    temperature=0.5
)
print(response)
```

#### `async generate_stream(model, prompt, system=None, temperature=0.7, top_k=40, top_p=0.9) -> AsyncGenerator[str, None]`

Generate text with streaming response.

**Parameters:** Same as `generate()`

**Yields:** Text chunks as they are generated

**Raises:** Same as `generate()`

**Example:**
```python
async for chunk in client.generate_stream(
    model="llama3.2:3b",
    prompt="Write a story..."
):
    print(chunk, end="", flush=True)
```

#### `async vision_generate(model, image_path, prompt, system=None) -> str`

Process image with vision model.

**Parameters:**
- `model` (str): Vision model name
- `image_path` (str): Path to image file
- `prompt` (str): Question about image
- `system` (str, optional): System message

**Returns:** Model's analysis

**Raises:**
- `VisionProcessingError`: Image processing failed
- `InvalidModelError`: Model not found

**Example:**
```python
analysis = await client.vision_generate(
    model="llava:7b",
    image_path="photo.jpg",
    prompt="Describe what you see"
)
print(analysis)
```

#### `async get_model_info(model) -> dict`

Get information about a specific model.

**Parameters:**
- `model` (str): Model name

**Returns:** Model information dictionary

**Raises:**
- `InvalidModelError`: Model not found
- `OllamaConnectionError`: Connection failed

**Example:**
```python
info = await client.get_model_info("llama3.2:3b")
print(info)
```

#### `async list_models() -> list`

List all available models.

**Returns:** List of model information dictionaries

**Raises:**
- `OllamaConnectionError`: Connection failed

**Example:**
```python
models = await client.list_models()
for model in models:
    print(model["name"])
```

#### `async close() -> None`

Close client and cleanup resources.

**Example:**
```python
await client.close()

# Or use context manager (preferred)
async with OllamaClient() as client:
    response = await client.generate("model", "prompt")
    # Auto-cleanup on exit
```

---

## BaseAgent

Abstract base class for agents.

### Initialization

```python
class MyAgent(BaseAgent):
    async def _execute_internal(self, context: Dict[str, Any]) -> str:
        # Implementation required
        pass

agent = MyAgent(
    name: str,
    model: str,
    prompts_dir: Path = None,
    client: OllamaClient = None
)
```

**Parameters:**
- `name` (str): Agent identifier
- `model` (str): Ollama model name
- `prompts_dir` (Path, optional): Directory with prompt templates
- `client` (OllamaClient, optional): Custom client instance

### Methods

#### `async execute(context: Dict[str, Any]) -> str`

Execute agent with context.

**Parameters:**
- `context` (dict): Execution context with parameters

**Returns:** Agent response

**Raises:**
- `AgentExecutionError`: Execution failed

**Example:**
```python
response = await agent.execute({
    "topic": "Python",
    "length": "brief"
})
```

#### `async handle_streaming(context: Dict[str, Any]) -> AsyncGenerator[str, None]`

Get streaming response from agent.

**Parameters:**
- `context` (dict): Execution context

**Yields:** Text chunks

**Example:**
```python
async for chunk in agent.handle_streaming(context):
    print(chunk, end="", flush=True)
```

#### `load_prompt(prompt_name: str) -> str`

Load prompt template from file.

**Parameters:**
- `prompt_name` (str): Prompt name (filename without .md)

**Returns:** Prompt template content

**Raises:**
- `FileNotFoundError`: Prompt file not found

**Notes:** Looks for `prompts/{agent_name}/{prompt_name}.md`

**Example:**
```python
template = agent.load_prompt("research")
```

#### `format_context(template: str, placeholders: Dict[str, Any]) -> str`

Replace context placeholders in template.

**Parameters:**
- `template` (str): Template with `___key___` placeholders
- `placeholders` (dict): Values to substitute

**Returns:** Formatted string

**Example:**
```python
template = "Topic: ___topic___\nStyle: ___style___"
result = agent.format_context(template, {
    "topic": "AI",
    "style": "academic"
})
# Result: "Topic: AI\nStyle: academic"
```

#### `get_state() -> AgentState`

Get current agent state.

**Returns:** AgentState enum (IDLE, BUSY, ERROR, COMPLETED)

#### `get_status() -> Dict[str, Any]`

Get comprehensive agent status.

**Returns:** Status dictionary with name, model, state, last_error

**Example:**
```python
status = agent.get_status()
print(f"Agent: {status['name']}")
print(f"State: {status['state']}")
```

#### `async close() -> None`

Close agent and cleanup resources.

---

## SimpleAgent

Concrete agent implementation for basic text generation.

```python
from core import SimpleAgent

agent = SimpleAgent(
    name="researcher",
    model="qwen2.5:7b"
)
```

Inherits all methods from `BaseAgent`. Uses prompt files and context formatting.

---

## StreamingAgent

Agent with streaming response support.

```python
from core import StreamingAgent

agent = StreamingAgent(
    name="writer",
    model="llama3.2:3b"
)

# Streams chunks
async for chunk in agent.handle_streaming(context):
    print(chunk, end="", flush=True)
```

Inherits all methods from `BaseAgent`.

---

## AgentOrchestrator

Manages multi-agent execution with concurrency control.

### Initialization

```python
orchestrator = AgentOrchestrator(max_concurrent: int = 3)
```

**Parameters:**
- `max_concurrent` (int): Max concurrent agents (default: 3)

### Methods

#### `async dispatch_task(agent, context, priority=TaskPriority.NORMAL) -> str`

Dispatch task for execution.

**Parameters:**
- `agent` (BaseAgent): Agent to execute
- `context` (dict): Execution context
- `priority` (TaskPriority): Task priority

**Returns:** Task ID for tracking

**Example:**
```python
task_id = await orchestrator.dispatch_task(
    agent=my_agent,
    context={"key": "value"},
    priority=TaskPriority.HIGH
)
```

#### `async run_agents_parallel(agent_tasks, timeout=None) -> List[ExecutionResult]`

Run multiple agents in parallel.

**Parameters:**
- `agent_tasks` (list): List of (agent, context) tuples
- `timeout` (float, optional): Overall timeout in seconds

**Returns:** List of ExecutionResult objects

**Raises:**
- `asyncio.TimeoutError`: Timeout exceeded
- `ValueError`: agent_tasks is empty

**Example:**
```python
results = await orchestrator.run_agents_parallel([
    (agent1, {"input": "..."}),
    (agent2, {"input": "..."}),
], timeout=60.0)
```

#### `async run_sequential(agent_tasks, stop_on_failure=False) -> List[ExecutionResult]`

Run agents sequentially.

**Parameters:**
- `agent_tasks` (list): List of (agent, context) tuples
- `stop_on_failure` (bool): Stop on first failure

**Returns:** List of ExecutionResult objects

**Example:**
```python
results = await orchestrator.run_sequential(
    agent_tasks,
    stop_on_failure=True
)
```

#### `get_result(task_id: str) -> Optional[ExecutionResult]`

Get result for specific task.

**Parameters:**
- `task_id` (str): Task ID

**Returns:** ExecutionResult or None

#### `get_all_results() -> Dict[str, ExecutionResult]`

Get all execution results.

**Returns:** Dictionary of task_id -> ExecutionResult

#### `get_summary() -> Dict[str, Any]`

Get execution summary statistics.

**Returns:** Dictionary with:
- `total_tasks` (int)
- `successful` (int)
- `failed` (int)
- `success_rate` (float)
- `avg_execution_time` (float)
- `min_execution_time` (float)
- `max_execution_time` (float)

**Example:**
```python
summary = orchestrator.get_summary()
print(f"Success rate: {summary['success_rate']:.0%}")
```

#### `handle_agent_failure(task_id, error_callback=None) -> Optional[ExecutionResult]`

Handle task failure with optional callback.

**Parameters:**
- `task_id` (str): Task ID
- `error_callback` (callable, optional): Callback function(task_id, error)

**Returns:** ExecutionResult

**Example:**
```python
def on_error(task_id, error):
    print(f"Task {task_id} failed: {error}")

orchestrator.handle_agent_failure(task_id, on_error)
```

#### `reset() -> None`

Reset all state and results.

---

## ExecutionResult

Result from a single agent execution.

**Attributes:**
```python
ExecutionResult(
    task_id: str,
    agent_name: str,
    success: bool,
    result: Optional[str] = None,
    error: Optional[str] = None,
    execution_time: Optional[float] = None,
    metadata: Dict[str, Any] = {}
)
```

**Example:**
```python
result = results[0]
if result.success:
    print(f"{result.agent_name}: {result.result}")
    print(f"Time: {result.execution_time:.2f}s")
else:
    print(f"Error: {result.error}")
```

---

## Task

Represents a task in the queue.

**Attributes:**
```python
Task(
    agent_name: str,
    agent: BaseAgent,
    context: Dict[str, Any],
    priority: TaskPriority = TaskPriority.NORMAL,
    task_id: Optional[str] = None,
    created_at: datetime = datetime.now(),
    result: Optional[str] = None,
    error: Optional[str] = None,
    completed_at: Optional[datetime] = None
)
```

**Methods:**
- `get_execution_time() -> Optional[float]`: Get execution time if completed

---

## TaskPriority

Enumeration for task priorities.

```python
from core import TaskPriority

TaskPriority.LOW      # Priority 3 (lowest)
TaskPriority.NORMAL   # Priority 2 (default)
TaskPriority.HIGH     # Priority 1 (highest)
```

---

## AgentState

Enumeration for agent execution states.

```python
from core import AgentState

AgentState.IDLE       # Waiting for work
AgentState.BUSY       # Currently executing
AgentState.ERROR      # Error occurred
AgentState.COMPLETED  # Task completed
```

---

## Settings

Configuration management.

### Initialization

```python
from config import Settings, get_settings

# Get global settings (singleton)
settings = get_settings()

# Create new instance (for testing)
settings = Settings()
```

### Attributes

```python
settings.ollama_host: str                  # API endpoint
settings.timeout: float                    # Request timeout
settings.max_concurrent_agents: int        # Max concurrent agents
settings.default_model: str                # Default model
settings.model_mappings: Dict[str, str]    # Agent -> model mapping
settings.log_level: str                    # Logging level
settings.log_format: str                   # Log format
```

### Methods

#### `get_model_for_agent(agent_name: str) -> str`

Get model assigned to agent.

**Parameters:**
- `agent_name` (str): Agent name

**Returns:** Model name

**Example:**
```python
model = settings.get_model_for_agent("researcher")
# Returns: "qwen2.5:7b"
```

#### `validate_settings() -> bool`

Validate configuration.

**Returns:** True if valid

**Raises:** ValueError if invalid

---

## Exceptions

All inherit from `OllamaException`.

### OllamaConnectionError

Raised when connection to Ollama fails.

### InvalidModelError

Raised when model is not found or invalid.

### AgentExecutionError

Raised when agent execution fails.

### AgentTimeoutError

Raised when operation times out.

### VisionProcessingError

Raised when vision model processing fails.

### ConfigurationError

Raised when configuration is invalid.

**Example:**
```python
from core.exceptions import InvalidModelError, OllamaConnectionError

try:
    response = await client.generate("invalid:model", "prompt")
except InvalidModelError as e:
    print(f"Model not found: {e}")
except OllamaConnectionError as e:
    print(f"Connection failed: {e}")
```

---

## Constants

### Default Values

```python
# OllamaClient defaults
DEFAULT_HOST = "http://localhost:11434"
DEFAULT_TIMEOUT = 120.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_INITIAL_BACKOFF = 1.0

# Settings defaults
DEFAULT_MAX_CONCURRENT_AGENTS = 3
DEFAULT_MODEL = "llama3.2:3b"
DEFAULT_LOG_LEVEL = "INFO"
```

### Model Assignments (models.yaml)

```yaml
models:
  researcher: qwen2.5:7b
  developer: llama3.2:3b
  planner: qwen2.5:7b
  vision: llava:7b
  default: llama3.2:3b
```

---

## Type Hints

Complete type hints throughout:

```python
from typing import Dict, Any, Optional, List, AsyncGenerator
from pathlib import Path
import asyncio

# All functions properly typed
async def example():
    client: OllamaClient = OllamaClient()
    response: str = await client.generate("model", "prompt")
    models: list = await client.list_models()

    agent: BaseAgent = SimpleAgent("name", "model")
    result: str = await agent.execute({"key": "value"})

    orch: AgentOrchestrator = AgentOrchestrator(3)
    results: List[ExecutionResult] = await orch.run_agents_parallel(tasks)
```
