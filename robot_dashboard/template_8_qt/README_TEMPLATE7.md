# Robot Simulator Dashboard - Template 7

## 🚀 What's New in Template 7

### **Intelligent Task Understanding**
- 🧠 **Embedding-based intent classification** using `mxbai-embed-large:latest`
- 🎯 **Semantic understanding** - AI knows if you're asking vs commanding
- 📊 **Confidence scoring** for intent classification

### **Plan-Then-Execute Workflow**
- 📋 AI creates detailed plans before execution
- ✅ Step-by-step verification
- 👁️ **Systems tab** shows planning process in real-time

### **Real Robot Movement**
- ✅ **FIXED**: Robot positions now update during movement (not just paths!)
- 🤖 Multiple robots move simultaneously
- 📍 Smooth animated transitions between cells
- 🧭 Auto-calculated headings

### **Better Query Responses**
AI now **prefers answering questions** over executing tasks:
```
❌ Before: "where is robot?" → tries to move robot
✅ Now: "where is robot?" → returns position info
```

## Quick Start

```bash
# Install embedding model (REQUIRED for Template 7)
ollama pull mxbai-embed-large:latest

# Terminal 1: Node.js server
cd template_7
npm start

# Terminal 2: Python API
cd template_7/api
python main.py
```

Visit http://localhost:3000 and login with **admin/admin**

## Example Commands

### Information Queries (NEW - Works Great!)
```
"where are all the robots?"
"show me map status"
"how do I run tests?"
"check robot errors"
"what points are available?"
```

### Simple Tasks
```
"go to point A"
"send robot to charge"
"move to standby"
```

### Complex Multi-Step Tasks
```
"go to A, then B, then charge"
"send robot to charge and check for errors"
"visit all points"
```

## Systems Tab (NEW!)

Go to **Systems** tab to see:
- 🧠 **Current Task Plan** - AI's planning steps
- ⚡ **Execution Status** - Real-time progress
- 🕒 **Timestamps** - When each step happens

Perfect for debugging and understanding what the AI is doing!

## Key Improvements Over Template 6

| Feature | Template 6 | Template 7 |
|---------|-----------|------------|
| **Query Understanding** | Keyword matching | Embedding-based semantic |
| **Intent Classification** | None | 5 categories with confidence |
| **Information Queries** | Often tries to execute | Correctly identifies and answers |
| **Robot Movement** | Path only | ✅ Real position updates |
| **Task Planning** | Implicit | Explicit plan-then-execute |
| **Monitoring** | None | Systems tab with real-time status |
| **Multi-robot Movement** | Buggy | ✅ Fixed and smooth |

## Architecture

```
User Query
    ↓
[Embedding Model] - Get semantic vector
    ↓
[Intent Classifier] - Classify intent (query vs task)
    ↓
[Task Planner] - Create execution plan
    ↓
[Confirmation Modal] - Show plan to user
    ↓
[Executor] - Execute step-by-step
    ↓
[Monitor] - Update Systems tab
    ↓
Result + Verification
```

## Intent Categories

The AI classifies queries into:

1. **query_status** - "where is robot X?" → Returns info
2. **query_map** - "how many obstacles?" → Returns map data
3. **query_docs** - "how do I...?" → Searches documentation
4. **task_navigation** - "go to A" → Executes movement
5. **task_complex** - "go to A then B" → Multi-step execution

## Requirements

### New in Template 7:
- **Ollama**: mxbai-embed-large:latest (REQUIRED)
- All Template 6 requirements

### Check if embedding model is installed:
```bash
ollama list | grep mxbai-embed-large
```

## Configuration

The system automatically uses:
- **LLM**: qwen3:latest (or set via `OLLAMA_MODEL`)
- **Embeddings**: mxbai-embed-large:latest (hardcoded)
- **Embedding endpoint**: `http://localhost:11434/api/embeddings`

## Files Changed from Template 6

```
views/index.html          → Added Systems page
public/js/app.js          → Robot movement system, status updates
api/main.py              → Embeddings, intent classification
TEMPLATE7_FEATURES.md    → Comprehensive documentation
```

## Performance

- **Embedding generation**: ~100-200ms
- **Intent classification**: ~500-1000ms
- **Total response time**: 2-4 seconds for complex tasks
- **Robot movement**: 300ms per grid cell

**Tip**: First query takes longer (embedding model loading)

## Common Issues

### "Robot not moving"
✅ **Fixed in Template 7!** Robots now move smoothly with position updates

### "AI executes instead of answering"
✅ **Fixed in Template 7!** Intent classification detects queries correctly

### "Embeddings slow/not working"
- Check if model is pulled: `ollama pull mxbai-embed-large:latest`
- System falls back to keyword matching if embeddings fail

### "Systems tab empty"
- Send a command first
- Tab updates in real-time during execution
- Check browser console for errors

## Testing Intent Classification

Try these to see the AI correctly identify intent:

**Queries (should NOT execute):**
- "where is ROB-001?"
- "show me the map"
- "what's the robot status?"

**Tasks (should execute):**
- "go to A"
- "send robot to charge"
- "move to B then C"

Watch the Systems tab to see detected intent!

## For More Details

See **TEMPLATE7_FEATURES.md** for:
- Complete technical documentation
- Embedding system details
- API endpoint changes
- Code examples
- Troubleshooting guide

## Upgrade Path

From Template 6 → Template 7:
1. ✅ Backward compatible (no breaking changes)
2. Pull embedding model: `ollama pull mxbai-embed-large:latest`
3. Restart Python API
4. Try information queries to see improvements!

## What's Next?

Future enhancements:
- Embedding caching for faster responses
- Learning from user feedback
- More sophisticated multi-robot coordination
- Integration with real robot hardware APIs

## License

MIT License - Free to use and extend!

---

**Template 7** = Template 6 + Embeddings + Intent Classification + Real Movement + Better Understanding 🚀
