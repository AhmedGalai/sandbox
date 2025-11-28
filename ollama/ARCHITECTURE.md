# System Architecture

## Overview

The Ollama Multi-Agent System is a production-ready, asynchronous architecture for orchestrating multiple specialized AI agents powered by local Ollama models. The system follows a modular design with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User (CLI)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      Main CLI (main.py)                     │
│  - Async event loop                                         │
│  - Command parser & router                                  │
│  - Rich console interface                                   │
│  - Signal handling (Ctrl+C)                                 │
└────────────┬───────────────────────────┬────────────────────┘
             │                           │
             ↓                           ↓
┌────────────────────────┐    ┌──────────────────────────────┐
│  Command System        │    │  Conversation Manager        │
│  (/help, /agents, etc) │    │  - Message history           │
│                        │    │  - Persistence               │
└────────┬───────────────┘    │  - Export (JSON/MD)          │
         │                    └──────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│              Agent Orchestrator (orchestrator.py)           │
│  - Task queue (asyncio.Queue)                               │
│  - Concurrency control (asyncio.Semaphore)                  │
│  - Parallel execution (asyncio.gather)                      │
│  - Result aggregation                                       │
└─────────┬───────────────────────────────────────────────────┘
          │
          ↓
┌─────────────────────────────────────────────────────────────┐
│                    Agent Factory                            │
│  - Dynamic agent creation                                   │
│  - Agent registry                                           │
└─────────┬───────────────────────────────────────────────────┘
          │
          ↓
┌─────────┴─────────┬──────────────┬──────────────┬──────────┐
│                   │              │              │          │
↓                   ↓              ↓              ↓          ↓
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐
│Research │  │Developer│  │ Planner │  │Mathema- │  │  Vision  │
│  Agent  │  │  Agent  │  │  Agent  │  │  tician │  │  Agent   │
└────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬─────┘
     │            │            │            │            │
     │            │            │            │            │ (images)
     └────────────┴────────────┴────────────┴────────────┘
                              │
                              ↓
                   ┌──────────────────────┐
                   │   Ollama Client      │
                   │  - Async HTTP client │
                   │  - Retry logic       │
                   │  - Connection pool   │
                   │  - Streaming support │
                   └──────────┬───────────┘
                              │
                              ↓
                   ┌──────────────────────┐
                   │    Ollama API        │
                   │  (localhost:11434)   │
                   └──────────────────────┘
```

## Core Components

### 1. Main CLI (`main.py`)

**Purpose**: Entry point and user interface

**Key Features**:
- Asynchronous event loop using `asyncio`
- Non-blocking input handling with background tasks
- Rich-based UI with colored output, panels, and tables
- Command parsing and routing
- Signal handling for graceful shutdown (Ctrl+C, Ctrl+D)
- Conversation state management

**Flow**:
```python
async def main():
    # Initialize components
    # Start event loop
    while running:
        # Get user input (async)
        # Parse command
        # Route to handler
        # Display response
```

### 2. Command System (`commands/`)

**Purpose**: Handle user commands and dispatch to appropriate agents

**Architecture**:
- `BaseCommand`: Abstract base class for all commands
- Individual command modules: `help.py`, `agents.py`, `vision.py`, etc.
- Command registry: Maps command strings to handler classes
- Argument validation and parsing

**Command Categories**:
1. **System**: `/help`, `/clear`, `/exit`
2. **Agents**: `/researcher`, `/developer`, `/planner`, `/vision`
3. **Models**: `/models`, `/use`, `/pull`
4. **Utilities**: `/history`, `/export`, `/settings`

**Example Command Flow**:
```
User: /vision image.png "describe this"
  ↓
CommandParser extracts: command="vision", args=["image.png", "describe this"]
  ↓
VisionCommand.execute(args)
  ↓
VisionAgent.analyze_image()
  ↓
Result displayed with Rich formatting
```

### 3. Agent Orchestrator (`core/orchestrator.py`)

**Purpose**: Manage agent lifecycle and concurrent execution

**Key Responsibilities**:
- Task queuing with priority support
- Concurrency limiting (max 3 concurrent agents via Semaphore)
- Parallel execution using `asyncio.gather()`
- Sequential execution for dependent tasks
- Error handling and failure recovery
- Performance metrics tracking

**Concurrency Model**:
```python
# Semaphore ensures max 3 concurrent agents
semaphore = asyncio.Semaphore(3)

async with semaphore:
    result = await agent.execute(task)
```

**Task Priority**:
- HIGH: User-facing commands
- NORMAL: Background research
- LOW: Cleanup tasks

### 4. Agent System (`agents/`)

**Base Architecture**:

All agents inherit from `BaseAgent`:

```python
class BaseAgent(ABC):
    - name: str
    - model: str
    - state: AgentState (IDLE, BUSY, ERROR, COMPLETED)
    - prompt_file: str

    @abstractmethod
    async def execute(context: dict) -> str

    def load_prompt() -> str
    def format_context(placeholders: dict) -> str
```

**Specialized Agents**:

1. **ResearcherAgent**
   - Model: `qwen2.5:7b`
   - Use case: Information synthesis, research
   - Context: Topic, Questions, Sources

2. **DeveloperAgent**
   - Model: `llama3.2:3b`
   - Use case: Code generation, debugging
   - Context: Project, Stack, Patterns

3. **PlannerAgent**
   - Model: `qwen2.5:7b`
   - Use case: Strategic planning, task breakdown
   - Context: Goals, Resources, Timeline

4. **VisionAgent**
   - Model: `llava:7b`
   - Use case: Image analysis, OCR
   - Special: Base64 image encoding, format validation

**Agent Prompt System**:

Prompts stored in markdown files:
```markdown
# AGENT: Researcher

## ROLE
You are a meticulous researcher...

## CONTEXT
**Topic:** `___topic___`
**Questions:** `___questions___`
```

Placeholders replaced at runtime:
```python
context = {"topic": "AI", "questions": "How do agents work?"}
prompt = agent.format_context(context)
```

### 5. Ollama Client (`core/ollama_client.py`)

**Purpose**: Async HTTP communication with Ollama API

**Features**:
- Async HTTP client using `httpx`
- HTTP/2 support for better performance
- Connection pooling (reuse connections)
- Exponential backoff retry logic
- Timeout handling
- Streaming response support

**API Methods**:
```python
async def generate(prompt, model, stream=False)
async def generate_stream(prompt, model)
async def vision_generate(prompt, image_b64, model)
async def list_models()
async def pull_model(model_name)
async def get_model_info(model_name)
```

**Retry Logic**:
```python
# Exponential backoff: 1s, 2s, 4s
for attempt in range(max_retries):
    try:
        return await request()
    except:
        await asyncio.sleep(2 ** attempt)
```

**Vision Model Integration**:
```python
# Encode image to base64
image_data = base64.b64encode(image_bytes)

# Send to Ollama with vision model
response = await client.vision_generate(
    prompt="Describe this image",
    image_b64=image_data,
    model="llava:7b"
)
```

### 6. Conversation Manager (`core/conversation.py`)

**Purpose**: Track and persist conversation history

**Features**:
- Message storage with metadata
- Rolling window (last 100 messages)
- Search functionality
- Export to JSON/Markdown
- Auto-save to `~/.ollama_agents/history.json`
- Statistics (message count, agent usage)

**Message Format**:
```python
{
    "timestamp": "2025-11-27T10:30:00",
    "role": "user" | "assistant",
    "agent": "researcher" | "developer" | ...,
    "content": "message text"
}
```

### 7. Configuration System (`config/`)

**Purpose**: Centralized configuration management

**Components**:

1. **settings.py** (Pydantic BaseSettings)
   - Environment variable support
   - YAML file loading
   - Validation
   - Singleton pattern

2. **models.yaml** (Agent-Model Mappings)
   ```yaml
   agents:
     researcher: qwen2.5:7b
     developer: llama3.2:3b
     planner: qwen2.5:7b
     vision: llava:7b
   ```

**Configuration Priority**:
1. Environment variables (highest)
2. `.env` file
3. `models.yaml`
4. Defaults in code (lowest)

## Data Flow

### Simple Query Flow

```
1. User enters: "what is async programming?"
   ↓
2. Main.py receives input
   ↓
3. No slash command → Auto agent selection
   ↓
4. AgentSelector determines → DeveloperAgent
   ↓
5. Orchestrator dispatches task
   ↓
6. DeveloperAgent.execute()
   ↓
7. Load prompt from agent_builtin_developer.md
   ↓
8. Format context with user query
   ↓
9. OllamaClient.generate(prompt, "llama3.2:3b")
   ↓
10. HTTP request to localhost:11434
   ↓
11. Ollama processes with llama3.2:3b
   ↓
12. Stream response back
   ↓
13. Display in Rich panel
   ↓
14. Save to conversation history
```

### Vision Analysis Flow

```
1. User: /vision image.png "describe UI"
   ↓
2. VisionCommand.execute()
   ↓
3. Validate file path and format
   ↓
4. VisionAgent.analyze_image()
   ↓
5. Load image file
   ↓
6. Encode to base64
   ↓
7. Preprocess (resize if >2MB)
   ↓
8. Load vision prompt
   ↓
9. OllamaClient.vision_generate(prompt, image, "llava:7b")
   ↓
10. Ollama processes with Llava model
   ↓
11. Return structured analysis
   ↓
12. Display with Rich formatting
```

### Multi-Agent Parallel Flow

```
1. Orchestrator receives 3 tasks:
   - Research "topic A"
   - Research "topic B"
   - Plan "project C"
   ↓
2. Semaphore allows 3 concurrent (limit)
   ↓
3. asyncio.gather([task1, task2, task3])
   ↓
   ┌───────────┬───────────┬───────────┐
   │ Research  │ Research  │  Planner  │
   │  Agent    │  Agent    │  Agent    │
   │ (qwen2.5) │ (qwen2.5) │ (qwen2.5) │
   └─────┬─────┴─────┬─────┴─────┬─────┘
         │           │           │
         └───────────┴───────────┘
                     │
4. Results aggregated when all complete
   ↓
5. Display combined results
```

## Async Architecture

### Event Loop Management

```python
# Main event loop
async def main():
    # Initialize
    client = OllamaClient()
    orchestrator = AgentOrchestrator(client)

    # Background tasks
    input_task = asyncio.create_task(get_user_input())

    # Main loop
    while running:
        done, pending = await asyncio.wait(
            [input_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Handle completed input
        # Dispatch to agents
```

### Non-Blocking Input

```python
async def async_input(prompt):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)
```

### Concurrent Agent Execution

```python
# Semaphore limits concurrency
async with self.semaphore:
    results = await asyncio.gather(
        agent1.execute(task1),
        agent2.execute(task2),
        agent3.execute(task3),
        return_exceptions=True
    )
```

## Error Handling

### Exception Hierarchy

```
Exception
├── OllamaConnectionError (network issues)
├── AgentTimeoutError (execution timeout)
├── InvalidModelError (model not found)
├── VisionProcessingError (image issues)
├── AgentExecutionError (general agent errors)
└── ConfigurationError (config issues)
```

### Error Handling Strategy

1. **Network Errors**: Retry with exponential backoff (3 attempts)
2. **Timeout Errors**: Cancel task, return partial results
3. **Model Errors**: Fallback to default model
4. **Validation Errors**: Display clear message, don't crash
5. **Unexpected Errors**: Log full traceback, display user-friendly message

### Graceful Degradation

```python
try:
    result = await agent.execute(task)
except AgentTimeoutError:
    result = "Task timed out, try with simpler query"
except OllamaConnectionError:
    result = "Ollama unavailable, check if service is running"
```

## Performance Optimizations

### 1. Connection Pooling

```python
# Reuse HTTP connections
client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_keepalive_connections=5,
        max_connections=10
    )
)
```

### 2. Streaming Responses

```python
# Stream tokens as they're generated
async for chunk in ollama_client.generate_stream():
    display(chunk)  # Show immediately
```

### 3. Concurrent Execution

- Multiple agents run in parallel (up to 3)
- Non-blocking I/O throughout
- Background tasks for cleanup

### 4. Lazy Loading

- Agent prompts loaded on first use
- Models pulled only when needed
- Configuration cached after first load

## Security Considerations

### 1. Input Validation

- File paths validated before reading
- Image formats verified
- Command arguments sanitized

### 2. Resource Limits

- Max concurrent agents (prevent resource exhaustion)
- Request timeouts (prevent hanging)
- File size limits for images (10MB max)

### 3. Error Information

- Stack traces in logs only (not shown to user)
- Sensitive data not logged
- API keys in environment variables only

## Extension Points

### Adding New Agents

1. Create prompt file: `agents/agent_builtin_custom.md`
2. Create agent class inheriting `BaseAgent`
3. Register in `agent_factory.py`
4. Add command in `commands/agents.py`
5. Update `models.yaml` with model assignment

### Adding New Commands

1. Create command class inheriting `BaseCommand`
2. Implement `async execute()` and `get_help_text()`
3. Register in `commands/__init__.py`
4. Update help documentation

### Custom Workflows

1. Define workflow in YAML
2. Create workflow executor
3. Chain agent calls with conditional logic
4. Register workflow command

## Monitoring & Logging

### Log Levels

- **DEBUG**: Detailed execution info (development)
- **INFO**: Important events (default)
- **WARNING**: Unusual but handled situations
- **ERROR**: Errors that don't crash system
- **CRITICAL**: System-breaking errors

### Log Files

```
logs/
├── app.log         # Main application logs
├── agents.log      # Agent-specific logs
└── errors.log      # Error-only logs
```

### Metrics Tracked

- Agent execution time
- Token generation speed
- Error rates by agent
- Command usage frequency
- Concurrent agent count

## Testing Strategy

### Unit Tests

- Individual agent functionality
- Ollama client with mocked responses
- Command parsing
- Configuration loading

### Integration Tests

- End-to-end agent execution
- Multi-agent workflows
- Error handling flows

### Performance Tests

- Concurrent execution limits
- Memory usage under load
- Response time benchmarks

## Deployment Considerations

### Production Checklist

- [ ] Ollama service running and tested
- [ ] All required models pulled
- [ ] Configuration reviewed and validated
- [ ] Logs directory created with proper permissions
- [ ] Tests passing
- [ ] Error handling verified
- [ ] Resource limits configured

### Scaling

For high-load scenarios:
- Increase MAX_CONCURRENT_AGENTS
- Use faster models (smaller parameter counts)
- Implement result caching
- Add load balancing for multiple Ollama instances

---

**Version**: 1.0.0
**Last Updated**: 2025-11-27
