# Quick Reference: Specialized Agents

## Installation

All agents are included in the project. Just import them:

```python
from agents import ResearcherAgent, DeveloperAgent, PlannerAgent, VisionAgent, AgentFactory
```

## Quick Start Examples

### 1. Researcher Agent (qwen2.5:7b)

```python
from agents import ResearcherAgent

agent = ResearcherAgent()

context = {
    "Topic": "Machine Learning",
    "Key Questions": "What are latest trends?",
    "Known Information": "Basic ML knowledge",
    "Sources to Prioritize": "Recent papers",
    "Desired Output Format": "Summary with points",
    "task": "Research latest ML trends"
}

result = await agent.execute(context)
print(result)
```

### 2. Developer Agent (llama3.2:3b)

```python
from agents import DeveloperAgent

agent = DeveloperAgent()

context = {
    "Project Name": "MyAPI",
    "Technology Stack": "Python, FastAPI",
    "Codebase Style": "PEP 8",
    "Architectural Patterns": "MVC",
    "Testing Framework": "pytest",
    "task": "Generate user login endpoint"
}

result = await agent.execute(context)
print(result)
```

### 3. Planner Agent (qwen2.5:7b)

```python
from agents import PlannerAgent

agent = PlannerAgent()

context = {
    "Project Name": "DataPipeline",
    "Project Goals": "Process 1M records daily",
    "Available Resources": "2 engineers, AWS",
    "Timeline": "3 months",
    "Key Milestones": "MVP in 6 weeks",
    "task": "Create detailed project roadmap"
}

result = await agent.execute(context)
print(result)
```

### 4. Vision Agent (llava:7b)

```python
from agents import VisionAgent

agent = VisionAgent()

# Method 1: Simple analysis
result = await agent.analyze_image(
    "/path/to/image.jpg",
    "Describe what you see"
)

# Method 2: Full context
context = {
    "Image Path": "/path/to/image.jpg",
    "Analysis Focus": "Text extraction",
    "Specific Questions": "What text is present?",
    "Expected Output": "Plain text",
    "Detail Level": "High",
    "task": "Extract all text from image"
}

result = await agent.execute(context)
print(result)
```

## Using the Factory

```python
from agents import AgentFactory

factory = AgentFactory()

# List available agents
agents = factory.get_available_agents()

# Create any agent dynamically
researcher = factory.create_agent("researcher")
developer = factory.create_agent("developer")
planner = factory.create_agent("planner")
vision = factory.create_agent("vision")

# With custom config
custom_agent = factory.create_agent(
    "researcher",
    config={"name": "my_researcher", "model": "qwen2.5:7b"}
)

# Cleanup
await factory.close()
```

## Context Fields Reference

### ResearcherAgent
- `Topic` - What to research
- `Key Questions` - Main questions
- `Known Information` - Background info
- `Sources to Prioritize` - Preferred sources
- `Desired Output Format` - Expected format
- `task` - The research instruction

### DeveloperAgent
- `Project Name` - Project identifier
- `Technology Stack` - Languages/frameworks
- `Codebase Style` - Code standards
- `Architectural Patterns` - Design patterns
- `Testing Framework` - Test framework name
- `task` - Development instruction

### PlannerAgent
- `Project Name` - Project identifier
- `Project Goals` - Goals/objectives
- `Available Resources` - Team/tools available
- `Timeline` - Project duration
- `Key Milestones` - Important dates
- `task` - Planning instruction

### VisionAgent
- `Image Path` - Path to image file
- `Analysis Focus` - What to focus on
- `Specific Questions` - Questions about image
- `Expected Output` - Expected response format
- `Detail Level` - Level of detail (low/medium/high)
- `task` - Analysis instruction

## Streaming Responses

```python
async for chunk in agent.handle_streaming(context):
    print(chunk, end="", flush=True)
```

## Error Handling

```python
from core.exceptions import AgentExecutionError, VisionProcessingError

try:
    result = await agent.execute(context)
except VisionProcessingError as e:
    print(f"Image processing error: {e}")
except AgentExecutionError as e:
    print(f"Agent execution error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    await agent.close()
```

## Models Available

| Agent | Model | Size | Best For |
|-------|-------|------|----------|
| Researcher | qwen2.5:7b | 7B | Complex research, synthesis |
| Developer | llama3.2:3b | 3B | Code generation, efficiency |
| Planner | qwen2.5:7b | 7B | Strategic planning, detailed plans |
| Vision | llava:7b | 7B | Image analysis, visual understanding |

## Vision Agent Features

### Supported Image Formats
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- WebP (.webp)

### Image Size Handling
- Maximum recommended: 2MB
- Auto-resize if larger (requires PIL/Pillow)
- Quality preserved at 85% JPEG quality

### Image Analysis Methods

```python
# Simple one-liner
result = await vision.analyze_image(path, question)

# Full context with more control
result = await agent.execute(context)

# Stream results
async for chunk in vision.handle_streaming(context):
    print(chunk, end="")

# Validate image manually
await vision.preprocess_image(path)
```

## Configuration Options

```python
# Temperature (0-1): Lower = deterministic, Higher = creative
config = {
    "temperature": 0.5,  # For focused tasks
    # "temperature": 0.8,  # For creative tasks
}

# Top-K and Top-P sampling
config = {
    "top_k": 40,  # Reduce to most likely tokens
    "top_p": 0.9,  # Nucleus sampling
}

# Use with factory
agent = factory.create_agent("researcher", config=config)

# Or directly with execute
result = await agent.execute({
    **context,
    "temperature": 0.6,
    "top_k": 40,
    "top_p": 0.9,
})
```

## Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Get logger for agents
logger = logging.getLogger("agents")

# Your code will now produce detailed logs
```

## Common Patterns

### Chain Multiple Agents

```python
# First research the topic
researcher = ResearcherAgent()
research = await researcher.execute({
    "Topic": "REST APIs",
    "Key Questions": "Best practices?",
    "Known Information": "Basic HTTP",
    "Sources to Prioritize": "Industry standards",
    "Desired Output Format": "Structured",
    "task": "Research REST API design patterns"
})

# Then use for development
developer = DeveloperAgent()
code = await developer.execute({
    "Project Name": "API",
    "Technology Stack": "Python, FastAPI",
    "Codebase Style": "PEP 8",
    "Architectural Patterns": research,  # Use research output
    "Testing Framework": "pytest",
    "task": "Generate API implementation"
})
```

### Batch Processing with Factory

```python
factory = AgentFactory()
agents = {
    "researcher": factory.create_agent("researcher"),
    "developer": factory.create_agent("developer"),
    "planner": factory.create_agent("planner"),
}

tasks = [
    ("researcher", context1),
    ("developer", context2),
    ("planner", context3),
]

results = []
for agent_type, context in tasks:
    result = await agents[agent_type].execute(context)
    results.append(result)
```

### Image Analysis Pipeline

```python
vision = VisionAgent()

images = [
    "/path/to/image1.jpg",
    "/path/to/image2.png",
    "/path/to/image3.gif",
]

for image_path in images:
    try:
        result = await vision.analyze_image(
            image_path,
            "Describe the contents"
        )
        print(f"{image_path}: {result}")
    except Exception as e:
        print(f"Error analyzing {image_path}: {e}")
```

## Full Async Pattern

```python
import asyncio

async def main():
    # Create agents
    researcher = ResearcherAgent()
    developer = DeveloperAgent()

    # Execute concurrently
    results = await asyncio.gather(
        researcher.execute(research_context),
        developer.execute(dev_context),
        return_exceptions=True
    )

    # Cleanup
    await researcher.close()
    await developer.close()

    return results

# Run
results = asyncio.run(main())
```

## Custom Agents

```python
from core.agent import BaseAgent
from agents import AgentFactory

class AnalystAgent(BaseAgent):
    async def _execute_internal(self, context):
        template = self.load_prompt("default")
        prompt = self.format_context(template, context)
        response = await self.client.generate(
            model=self.model,
            prompt=prompt,
        )
        return response

# Register with factory
factory = AgentFactory()
factory.register_agent("analyst", AnalystAgent, "qwen2.5:7b")

# Use it
analyst = factory.create_agent("analyst")
result = await analyst.execute(context)
```

## Troubleshooting

### "Model not found" error
```bash
# Make sure model is pulled
ollama pull qwen2.5:7b
ollama pull llama3.2:3b
ollama pull llava:7b
```

### Vision image processing fails
```bash
# Install PIL/Pillow for image preprocessing
pip install pillow
```

### Context validation errors
```python
# Make sure all required fields are present
context = {
    "Topic": "...",  # Required
    "Key Questions": "...",  # Required
    "Known Information": "...",  # Required
    "Sources to Prioritize": "...",  # Required
    "Desired Output Format": "...",  # Required
    "task": "...",  # Required
}
```

### Connection errors
```bash
# Check Ollama is running
ollama serve

# Or specify custom host
from agents import AgentFactory
from core.ollama_client import OllamaClient

client = OllamaClient(host="http://localhost:11434")
factory = AgentFactory(client=client)
```

## Best Practices

1. **Always use async/await** - All agent operations are async
2. **Close agents** - Call `await agent.close()` when done
3. **Validate context** - Provide all required fields
4. **Handle exceptions** - Wrap in try-except blocks
5. **Stream long tasks** - Use `handle_streaming()` for real-time feedback
6. **Use factory** - For managing multiple agents
7. **Log errors** - Enable logging for debugging
8. **Preprocess images** - Call `preprocess_image()` before analysis

## References

- Full documentation: `AGENTS_IMPLEMENTATION.md`
- Examples: `examples/agents_example.py`
- Summary: `SPECIALIZED_AGENTS_SUMMARY.md`
