# Specialized Agents Implementation Guide

This document describes the specialized agent implementations and vision capabilities added to the Ollama multi-agent system.

## Overview

The agents module provides specialized agent implementations for different task domains:

1. **ResearcherAgent** - Information synthesis and research tasks
2. **DeveloperAgent** - Code generation and development guidance
3. **PlannerAgent** - Strategic planning and project management
4. **VisionAgent** - Image analysis and visual understanding

## Files Created

### 1. `/home/ag/Desktop/sandbox/ollama/agents/researcher_agent.py`
- **Class**: `ResearcherAgent`
- **Model**: `qwen2.5:7b`
- **Purpose**: Research and information synthesis
- **Context Fields**:
  - Topic
  - Key Questions
  - Known Information
  - Sources to Prioritize
  - Desired Output Format
  - task (instruction)

**Features**:
- Loads prompts from `agent_builtin_researcher.md`
- Async execution with streaming support
- Context validation and placeholder replacement
- Comprehensive error handling

### 2. `/home/ag/Desktop/sandbox/ollama/agents/developer_agent.py`
- **Class**: `DeveloperAgent`
- **Model**: `llama3.2:3b`
- **Purpose**: Code generation and development tasks
- **Context Fields**:
  - Project Name
  - Technology Stack
  - Codebase Style
  - Architectural Patterns
  - Testing Framework
  - task (instruction)

**Features**:
- Loads prompts from `agent_builtin_developer.md`
- Optimized for efficient code generation
- Full async/streaming support
- Context validation

### 3. `/home/ag/Desktop/sandbox/ollama/agents/planner_agent.py`
- **Class**: `PlannerAgent`
- **Model**: `qwen2.5:7b`
- **Purpose**: Strategic planning and project management
- **Context Fields**:
  - Project Name
  - Project Goals
  - Available Resources
  - Timeline
  - Key Milestones
  - task (instruction)

**Features**:
- Loads prompts from `agent_builtin_planner.md`
- Structured planning output (nested steps)
- Full async support
- Context validation

### 4. `/home/ag/Desktop/sandbox/ollama/agents/vision_agent.py`
- **Class**: `VisionAgent`
- **Model**: `llava:7b`
- **Purpose**: Image analysis and visual understanding
- **Context Fields**:
  - Image Path
  - Analysis Focus
  - Specific Questions
  - Expected Output
  - Detail Level
  - task (instruction)

**Features**:
- Image loading and validation
- Base64 encoding for transmission
- Automatic image preprocessing and resizing
- Support for PNG, JPEG, GIF, WEBP formats
- Integrated with `OllamaClient.vision_generate()`
- Async image preprocessing
- File size checking (>2MB auto-resize with PIL/Pillow)

**Image Handling**:
```python
# Supported formats
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB

# Automatic resizing if over limit
# Uses PIL/Pillow for image compression
# Falls back gracefully if PIL not available
```

### 5. `/home/ag/Desktop/sandbox/ollama/agents/__init__.py`
- Exports all agent classes
- Provides `AGENT_REGISTRY` dictionary
- Clean import interface

### 6. `/home/ag/Desktop/sandbox/ollama/agents/agent_factory.py`
- **Class**: `AgentFactory`
- **Purpose**: Dynamic agent creation and management

**Methods**:
- `create_agent(agent_type, config)` - Create agents dynamically
- `get_available_agents()` - List all registered agents
- `register_agent(agent_type, agent_class, model)` - Register custom agents
- `discover_agents(agents_dir)` - Discover agents from directory
- `close()` - Cleanup resources

**Features**:
- Built-in registry with 4 default agents
- Default model mappings
- Custom agent registration
- Configuration management
- Comprehensive error handling
- Logging throughout

## Usage Examples

### Direct Agent Creation

```python
from agents import ResearcherAgent, DeveloperAgent, PlannerAgent, VisionAgent

# Create a researcher agent
researcher = ResearcherAgent()
result = await researcher.execute({
    "Topic": "Machine Learning",
    "Key Questions": "What are the latest ML techniques?",
    "Known Information": "General ML background",
    "Sources to Prioritize": "Academic papers, arXiv",
    "Desired Output Format": "Structured summary with citations",
    "task": "Research the latest advances in transformer architectures"
})

# Create a developer agent
developer = DeveloperAgent()
code = await developer.execute({
    "Project Name": "MyApp",
    "Technology Stack": "Python, FastAPI",
    "Codebase Style": "PEP 8",
    "Architectural Patterns": "MVC",
    "Testing Framework": "pytest",
    "task": "Generate a REST API endpoint for user authentication"
})

# Create a planner agent
planner = PlannerAgent()
plan = await planner.execute({
    "Project Name": "Data Pipeline",
    "Project Goals": "Process 1M records daily",
    "Available Resources": "2 engineers, AWS",
    "Timeline": "3 months",
    "Key Milestones": "MVP in 6 weeks",
    "task": "Create a project roadmap"
})

# Create a vision agent
vision = VisionAgent()
analysis = await vision.execute({
    "Image Path": "/path/to/image.jpg",
    "Analysis Focus": "Text extraction",
    "Specific Questions": "What text is visible in the image?",
    "Expected Output": "Plain text of visible content",
    "Detail Level": "High",
    "task": "Extract all visible text from the image"
})

# Or use the simple analyze_image method
analysis = await vision.analyze_image(
    "/path/to/image.jpg",
    "Describe what you see in this image"
)
```

### Using the Factory

```python
from agents import AgentFactory

# Create factory
factory = AgentFactory()

# List available agents
agents = factory.get_available_agents()
for agent_type, info in agents.items():
    print(f"{agent_type}: {info['model']} - {info['description']}")

# Create an agent dynamically
agent = factory.create_agent("researcher", config={
    "model": "qwen2.5:7b",
    "name": "my_researcher"
})

# Use the agent
result = await agent.execute({
    "Topic": "AI Ethics",
    "Key Questions": "What are the main concerns?",
    "Known Information": "Basic AI knowledge",
    "Sources to Prioritize": "Recent publications",
    "Desired Output Format": "Executive summary",
    "task": "Research current AI ethics debates"
})

# Register custom agent
from core.agent import BaseAgent

class CustomAgent(BaseAgent):
    async def _execute_internal(self, context):
        # Custom implementation
        pass

factory.register_agent("custom", CustomAgent, "custom-model:7b")

# Create and use custom agent
custom = factory.create_agent("custom")

# Cleanup
await factory.close()
```

### Streaming Responses

```python
# Get streaming response from any agent
async for chunk in researcher.handle_streaming(context):
    print(chunk, end='', flush=True)
```

## Architecture Details

### Inheritance Hierarchy

```
BaseAgent (core.agent)
    ├── ResearcherAgent
    ├── DeveloperAgent
    ├── PlannerAgent
    └── VisionAgent
```

All agents inherit from `BaseAgent` which provides:
- Async execution framework
- Prompt loading from markdown files
- Context placeholder replacement
- State tracking
- Streaming support
- Error handling

### Prompt Template Format

All agents load prompts from markdown files with this format:

```markdown
# AGENT: Agent Name

## ROLE
Description of the agent's role and expertise...

## CONTEXT
Agent context with placeholders like:
**Field Name:** `___`
**Another Field:** `___`

Your current task is: `___`
```

Placeholders are replaced using the `format_context()` method with context dictionary keys.

### Error Handling

All agents implement comprehensive error handling:
- File not found errors for missing prompts
- Context validation errors
- Model execution errors
- Vision-specific image processing errors
- Logging at all levels (info, debug, warning, error)

### Model Specifications

| Agent | Model | Parameters | Use Case |
|-------|-------|-----------|----------|
| Researcher | qwen2.5:7b | 7B | Research, synthesis |
| Developer | llama3.2:3b | 3B | Code generation |
| Planner | qwen2.5:7b | 7B | Strategic planning |
| Vision | llava:7b | 7B | Image analysis |

## Vision Agent Features

### Image Validation
- Checks file existence
- Validates format (PNG, JPEG, GIF, WEBP)
- Checks for empty files
- Validates file size

### Automatic Image Preprocessing
- Detects oversized images (>2MB)
- Automatically resizes using PIL/Pillow if available
- Maintains aspect ratio
- Optimizes quality and compression
- Falls back gracefully if PIL not available

### Image Analysis Methods

```python
# Full context method
result = await vision.execute(context_dict)

# Simplified method
result = await vision.analyze_image(image_path, question)

# With streaming
async for chunk in vision.handle_streaming(context_dict):
    print(chunk, end='')
```

## Configuration

### Default Models
```python
{
    "researcher": "qwen2.5:7b",
    "developer": "llama3.2:3b",
    "planner": "qwen2.5:7b",
    "vision": "llava:7b",
}
```

### Custom Configuration
```python
agent = factory.create_agent("researcher", config={
    "model": "custom-model:7b",
    "name": "custom_researcher",
    "temperature": 0.6,
    "top_k": 40,
    "top_p": 0.9,
})
```

## Logging

All agents include comprehensive logging:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("agents")

# All agent operations are logged:
# - Initialization
# - Execution start/completion
# - Context validation
# - Prompt loading
# - Errors with tracebacks
# - Debug information
```

## Testing

The agents are fully compatible with the existing test framework:

```python
import pytest
from agents import ResearcherAgent

@pytest.mark.asyncio
async def test_researcher_agent():
    agent = ResearcherAgent()
    result = await agent.execute({
        "Topic": "Test",
        "Key Questions": "Test question",
        "Known Information": "Test info",
        "Sources to Prioritize": "Test sources",
        "Desired Output Format": "Plain text",
        "task": "Test task"
    })
    assert isinstance(result, str)
    assert len(result) > 0
```

## Dependencies

### Required
- Python 3.8+
- httpx (async HTTP client)
- Ollama API endpoint

### Optional
- Pillow/PIL (for image preprocessing)

### Installed with Project
- pydantic
- pydantic_settings
- asyncio (standard library)

## Best Practices

1. **Always use async/await** with agent execution
2. **Provide complete context** for better results
3. **Use streaming for long operations** for real-time feedback
4. **Cleanup resources** with `agent.close()` or `factory.close()`
5. **Log at appropriate levels** for debugging
6. **Validate context** before execution
7. **Handle AgentExecutionError** for comprehensive error recovery

## Extending the Framework

### Creating a Custom Agent

```python
from core.agent import BaseAgent
from core.ollama_client import OllamaClient
from pathlib import Path
from typing import Any, Dict, Optional

class CustomAgent(BaseAgent):
    def __init__(
        self,
        name: str = "custom",
        model: str = "llama3.2:3b",
        prompts_dir: Optional[Path] = None,
        client: Optional[OllamaClient] = None,
    ):
        super().__init__(name, model, prompts_dir, client)

    async def _execute_internal(self, context: Dict[str, Any]) -> str:
        template = self.load_prompt("default")
        prompt = self.format_context(template, context)
        response = await self.client.generate(
            model=self.model,
            prompt=prompt,
        )
        return response
```

### Registering with Factory

```python
factory = AgentFactory()
factory.register_agent("custom", CustomAgent, "custom-model:7b")
agent = factory.create_agent("custom")
```

## Performance Considerations

- **Temperature**: Lower (0.5) for deterministic tasks, higher (0.8) for creative
- **Model Size**: Larger models (7B) for complex tasks, smaller (3B) for efficiency
- **Streaming**: Use for long operations to provide real-time feedback
- **Caching**: Factory maintains single OllamaClient for connection pooling

## Troubleshooting

### Import Errors
- Ensure you're importing from the `ollama` package root
- Check that all dependencies are installed
- Verify Python path includes the project directory

### Vision Processing Errors
- Ensure image file exists and is readable
- Check image format is supported
- If over 2MB, ensure PIL/Pillow is installed for auto-resize
- Check Ollama vision model is pulled: `ollama pull llava:7b`

### Model Not Found
- Ensure model is pulled with Ollama: `ollama pull model-name`
- Check Ollama endpoint is running and accessible
- Verify model name matches exactly

### Context Errors
- Provide all required context fields
- Use exact field names from agent documentation
- Ensure task field is included
- Validate placeholder values are appropriate

## Integration with Orchestrator

These agents work seamlessly with the `Orchestrator` class for coordinated multi-agent workflows:

```python
from core.orchestrator import Orchestrator
from agents import ResearcherAgent, DeveloperAgent

orchestrator = Orchestrator()
orchestrator.register_agent("researcher", ResearcherAgent())
orchestrator.register_agent("developer", DeveloperAgent())

result = await orchestrator.execute_workflow({
    "agents": ["researcher", "developer"],
    "context": {...}
})
```

## Performance Metrics

Expected performance (with typical hardware):
- ResearcherAgent: 30-60 seconds for comprehensive research
- DeveloperAgent: 15-45 seconds for code generation
- PlannerAgent: 20-50 seconds for project planning
- VisionAgent: 10-30 seconds for image analysis (varies by image size)

## Future Enhancements

Potential improvements for future versions:
- Agent memory/persistence
- Multi-turn conversations
- Agent-to-agent communication
- Parallel agent execution
- Advanced prompt optimization
- Token usage tracking
- Model fine-tuning support
- Caching of common results
