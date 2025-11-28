# Quick Start - Ollama Multi-Agent CLI

## Installation & Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run the CLI
python main.py

# With custom Ollama host
OLLAMA_HOST=http://remote-host:11434 python main.py
```

## First Steps

### 1. Check Available Commands
```bash
/help
```

### 2. See What Agents Are Available
```bash
/agents
```

### 3. List Downloaded Models
```bash
/models
```

### 4. Download a New Model (if needed)
```bash
/pull llama3.2:3b
```

## Common Tasks

### Research a Topic
```bash
/researcher "explain quantum computing"
/researcher "latest AI breakthroughs" --context "machine learning"
```

### Generate Code
```bash
/developer "write a Python function to sort a list"
/developer "create a REST API endpoint" --language javascript
```

### Plan a Project
```bash
/planner "create a roadmap for a web app"
/planner "organize team workflow" --scope "team"
```

### Analyze an Image
```bash
/vision /path/to/image.jpg
/vision image.png "What objects are in this image?"
```

### Manage Settings
```bash
/settings                    # View all settings
/settings agents            # View agent assignments
/use qwen2.5:7b            # Switch default model
```

### Manage History
```bash
/history                    # Show last 20 messages
/history 100               # Show last 100 messages
/export my_conversation    # Export to markdown
/export data --format json # Export to JSON
```

### Clean Up
```bash
/clear                      # Clear screen and history
```

### Exit
```bash
/exit
/quit
/q
```

## Quick Reference

| Task | Command |
|------|---------|
| Help | `/help` or `/?` |
| List agents | `/agents` |
| Use researcher | `/researcher "query"` |
| Use developer | `/developer "task"` |
| Use planner | `/planner "task"` |
| Analyze image | `/vision image.jpg "question"` |
| List models | `/models` |
| Switch model | `/use modelname` |
| Get a model | `/pull modelname` |
| View history | `/history` |
| Export conversation | `/export filename` |
| View settings | `/settings` |
| Clear screen | `/clear` |
| Exit CLI | `/exit` |

## Agents Quick Guide

### Researcher Agent
Best for: Information gathering, research, analysis
```bash
/researcher "What are microservices?"
/researcher "How do transformers work?" --context "deep learning"
```

### Developer Agent
Best for: Code generation, debugging, implementation
```bash
/developer "Create a login function"
/developer "Fix this bug" --language python
```

### Planner Agent
Best for: Planning, strategy, roadmaps, organization
```bash
/planner "Create a project plan"
/planner "Design workflow" --scope "development"
```

### Vision Agent
Best for: Image analysis, description, object detection
```bash
/vision photo.jpg
/vision diagram.png "Describe the architecture"
```

## Model Selection

### Quick Models (Fast, Lower Quality)
```bash
/use llama3.2:3b
/pull llama3.2:3b
```

### Balanced Models (Good Speed & Quality)
```bash
/use qwen2.5:7b
/pull qwen2.5:7b
```

### Advanced Models (Slower, Higher Quality)
```bash
/use mistral:latest
/pull mistral:latest
```

### Vision Models
```bash
/pull llava:7b
/use llava:7b
```

## Configuration

Create `.env` file in project root:

```env
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=llama3.2:3b
MAX_CONCURRENT_AGENTS=3
TIMEOUT=120
LOG_LEVEL=INFO
```

## File Locations

- **Config**: `.env`
- **History**: `~/.ollama_agents/history.json`
- **Exports**: `~/.ollama_agents/exports/`
- **Logs**: Console output (configurable)

## Common Issues & Solutions

### "Cannot connect to Ollama"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve
```

### "Model not found"
```bash
# See available models
/models

# Download a model
/pull llama3.2:3b
```

### "Unknown command"
```bash
# Check command spelling
/help

# Get help for specific command
/help agents
```

### "No conversation history"
```bash
# History is auto-saved after each interaction
# It appears in ~/.ollama_agents/history.json
# Use /history to view it
/history 50
```

## Tips & Tricks

### 1. Use Quotes for Arguments with Spaces
```bash
/researcher "how does machine learning work"
/developer "create a function that does X"
```

### 2. Add Context to Queries
```bash
/researcher "AI trends" --context "2024"
/developer "API design" --language typescript
```

### 3. Switch Models Per Command
```bash
/researcher "topic" --model mistral:latest
/developer "task" --model llama3.2:3b
```

### 4. Run Multiple Agents Sequentially
```bash
/researcher "plan details"
/developer "implementation"
/planner "next steps"
```

### 5. Export Before Important Work
```bash
/export session_backup
# ... do important work ...
/history 1000  # View extended history
```

### 6. Use Aliases for Speed
```bash
/?              # /help
/h              # /help
/cls            # /clear
/q              # /quit
```

## Keyboard Shortcuts

- `Ctrl+C` - Show prompt to exit (use `/exit` to quit)
- `Ctrl+D` - Exit immediately
- `Tab` - Command completion (coming soon)
- `↑/↓` - Command history (coming soon)

## Example Workflow

```bash
# 1. Check what agents are available
/agents

# 2. Research a topic
/researcher "machine learning basics"

# 3. Get code for it
/developer "create a simple ML example"

# 4. Plan how to use it
/planner "create a learning roadmap"

# 5. View what we discussed
/history 50

# 6. Save the conversation
/export ml_discussion

# 7. Exit
/exit
```

## Help & Documentation

- **CLI Guide**: `CLI_GUIDE.md` - Complete user guide
- **Architecture**: `COMMAND_SYSTEM_ARCHITECTURE.md` - Technical details
- **Implementation**: `COMMAND_SYSTEM_IMPLEMENTATION.md` - What's included
- **In-CLI Help**: `/help` command

## Getting Help

```bash
# Show all available commands
/help

# Get help for a specific command
/help researchers
/help vision
/help models

# Show agent information
/agents

# Check current settings
/settings
```

## Troubleshooting Commands

```bash
# Test Ollama connection
/models

# List available agents
/agents

# View system settings
/settings

# Check conversation history
/history

# Test with a simple query
/researcher "hello"
```

## Performance Tips

1. **Use smaller models for speed**: `llama3.2:3b`
2. **Use larger models for quality**: `mistral:latest`
3. **Run agents sequentially for consistency**: One at a time
4. **Limit history size**: `/history 20` instead of `/history 1000`
5. **Export large conversations**: Keep history files small

## Next Steps

1. Try `/researcher "example query"`
2. Try `/developer "example task"`
3. Try `/vision image.jpg` with an image
4. Check `/history` to see what was saved
5. Use `/export` to save your work
6. Explore other commands with `/help`

## Advanced Usage

### Programmatic Access (Python)
```python
from core.conversation import ConversationManager
from core.orchestrator import AgentOrchestrator
from agents.agent_factory import AgentFactory

# Use the classes programmatically
factory = AgentFactory()
agent = factory.create_agent("researcher")
```

### Custom Commands
```python
# Add to commands/ directory
# See COMMAND_SYSTEM_ARCHITECTURE.md for details
```

### Integration with Scripts
```bash
# Run CLI with logging
LOG_LEVEL=DEBUG python main.py

# Monitor performance
# Check ~/.ollama_agents/exports/ for saved conversations
```

## Resources

- **Ollama**: https://ollama.ai
- **Models**: https://ollama.ai/library
- **Documentation**: See included .md files

## Summary

The CLI is ready to use! Start with `/help` to see all commands, then:
1. Check agents: `/agents`
2. Try a command: `/researcher "something"`
3. View results: `/history`
4. Export: `/export`

Enjoy exploring the power of multi-agent AI!
