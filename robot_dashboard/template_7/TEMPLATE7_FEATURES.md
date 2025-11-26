# Template 7 Features

## Overview
Template 7 introduces advanced AI-powered task planning with embedding-based intent classification, plan-then-execute workflow, and real-time robot position updates.

## 🆕 Major New Features

### 1. **Embedding-Based Intent Classification**
- Uses **mxbai-embed-large:latest** for semantic understanding
- Classifies user queries into intents:
  - `query_status` - Questions about robot position/status
  - `query_map` - Questions about map/obstacles
  - `query_docs` - Documentation/help requests
  - `task_navigation` - Simple movement commands
  - `task_complex` - Multi-step task plans
- **Cosine similarity** matching with example embeddings
- Fallback to keyword matching if embeddings unavailable
- **Confidence scores** for each classification

### 2. **Advanced Plan-Then-Execute Workflow**
The AI now follows a structured process:

```
1. UNDERSTAND → Classify intent using embeddings
2. PLAN → Create detailed execution plan
3. CONFIRM → Present plan to user (if confirmation enabled)
4. EXECUTE → Run plan step-by-step
5. MONITOR → Track progress and check for errors
```

#### Example Workflow:
```
User: "send robot to charge and check if it has errors"

STEP 1 - UNDERSTAND:
→ Intent: task_complex (confidence: 0.85)
→ Requires: navigation + status check

STEP 2 - PLAN:
1. Navigate ROB-001 to CHARGE point
2. Wait for arrival
3. Check robot for errors
4. Report status

STEP 3 - EXECUTE:
→ Moving ROB-001 to CHARGE...
→ Arrived at CHARGE
→ Checking errors: None
→ Task complete!
```

### 3. **Real-Time Robot Position Updates**
- **Per-robot movement intervals** - each robot moves independently
- **Animated movement** - smooth transitions between grid cells
- **Position updates** - x, y coordinates change in real-time
- **Heading calculations** - robot faces movement direction
- **Path visualization** - shows planned route
- **Multiple robots moving simultaneously**

**Fixed Issues:**
- ✅ Map now updates robot positions during movement
- ✅ Not just path changes - actual x/y coordinates update
- ✅ Works for all selected robots in parallel

### 4. **Systems Tab**
New dedicated tab for monitoring AI task planning:

**AI Task Planner Card:**
- **Current Task Plan** - Shows the AI's planning steps
- **Execution Status** - Real-time progress updates
- **Timestamps** - Track when each step occurs
- **Error monitoring** - Displays any issues

### 5. **Enhanced System Prompts**

#### For Queries (Information Requests):
```
Role: Robot Fleet Information Assistant
Task: Answer questions about robots, map, and documentation
Context: Full fleet status, map data, relevant docs
Output: Clear, factual answers (1-2 sentences)
```

#### For Tasks (Action Requests):
```
Role: Task Planning and Execution Agent
Task: Create detailed step-by-step plans
Context: Robot status, map layout, capabilities
Output: Structured execution plan with verification steps
```

### 6. **Improved Query Understanding**

The AI now **prefers providing information** over executing tasks when appropriate:

**Before (Template 6):**
```
User: "where is the robot?"
AI: → Tries to send robot somewhere ❌
```

**After (Template 7):**
```
User: "where is the robot?"
AI: → Intent: query_status
    → Provides: "ROB-001 is at position (5,5),
       heading 0°, status Active" ✅
```

## Technical Implementation

### Embedding System
```python
# Get embedding for text
embedding = await get_embedding("user query text")

# Compare with intent examples
similarity = cosine_similarity(query_emb, example_emb)

# Classify based on highest similarity
intent = best_matching_intent
confidence = similarity_score
```

### Intent Examples Database
```python
INTENT_EXAMPLES = {
    "query_status": [
        "where is the robot",
        "what is the robot status",
        "check robot errors",
        ...
    ],
    "query_map": [...],
    "query_docs": [...],
    "task_navigation": [...],
    "task_complex": [...]
}
```

### Robot Movement System
```javascript
// Per-robot movement intervals
robotMovementIntervals[robotId] = setInterval(() => {
    // Update position
    robot.x = nextPos.x;
    robot.y = nextPos.y;

    // Update heading
    robot.heading = calculateHeading(current, next);

    // Redraw map
    drawRobotMap();
}, 300); // 300ms per step
```

### Multi-Step Execution with Waiting
```javascript
for (const step of steps) {
    await sendRobotToPoint(robotId, step.poi);
    await waitForRobotToFinish(robotId); // ✅ Waits for completion
}
```

## Configuration

### Required Ollama Models
```bash
# Main language model
ollama pull qwen3:latest

# Embedding model (NEW in Template 7)
ollama pull mxbai-embed-large:latest
```

### Environment Variables
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:latest
# EMBEDDING_MODEL is hardcoded to mxbai-embed-large:latest
```

## Usage Examples

### 1. Information Queries

**Robot Status:**
```
"where are all the robots?"
→ ROB-001: (5,5) Active, ROB-002: (12,8) Idle, ROB-003: (2,18) Charging
```

**Map Information:**
```
"how many obstacles are on the map?"
→ The map has 50 obstacle cells on a 20x20 grid
```

**Documentation:**
```
"how do I run the tests?"
→ From TESTING_GUIDE.md: Run `npm test` for frontend tests...
```

### 2. Simple Navigation
```
"go to point A"
→ Plan: Navigate to A(18,3)
→ Execute: ROB-001 moving... Complete!
```

### 3. Complex Multi-Step Tasks
```
"go to A, then B, then charge"

PLAN:
1. Navigate to A(18,3)
2. Navigate to B(7,12)
3. Navigate to CHARGE(2,18)

EXECUTE:
→ Step 1/3: Moving to A... ✓
→ Step 2/3: Moving to B... ✓
→ Step 3/3: Moving to CHARGE... ✓
```

### 4. Task with Verification
```
"send robot to charge and check for errors"

PLAN:
1. Navigate to CHARGE
2. Verify arrival
3. Check error status
4. Report findings

EXECUTE:
→ Moving to CHARGE...
→ Arrived at (2,18)
→ Error check: None
→ Status: Ready
```

## API Changes

### New Functions
- `get_embedding(text)` - Get embedding vector
- `cosine_similarity(v1, v2)` - Calculate similarity
- `classify_intent(query)` - Classify user intent
- `startRobotMovementForRobot(robotId)` - Animate movement
- `waitForRobotToFinish(robotId)` - Wait for completion
- `updateTaskPlan(text)` - Update Systems card
- `updateExecutionStatus(text)` - Update execution display

### Enhanced Endpoints
- `POST /api/robot/task` - Now uses embeddings and planning

## Files Changed from Template 6

### Frontend
- `views/index.html` - Added Systems tab and monitoring card
- `public/js/app.js` - Robot movement system, systems card updates

### Backend
- `api/main.py` - Embedding classification, intent system, enhanced prompts

## Performance Notes

- **Embedding calls**: ~100-200ms per query
- **Intent classification**: ~500-1000ms (multiple embeddings)
- **Robot movement**: 300ms per grid cell
- **Plan generation**: 1-3 seconds depending on complexity
- **Overall response time**: 2-4 seconds for complex tasks

## Migration from Template 6

**Breaking Changes:** None - fully backward compatible

**New Requirements:**
- Ollama must have `mxbai-embed-large:latest` installed
- If embedding model unavailable, falls back to keyword matching

**Recommendations:**
1. Pull embedding model before starting: `ollama pull mxbai-embed-large:latest`
2. Visit Systems tab to monitor AI planning
3. Try information queries to see improved understanding

## Future Enhancements

- Cache embeddings for common queries
- Learn from user corrections
- Multi-robot coordination plans
- Obstacle avoidance in planning
- Voice command support
- Natural language task templates
- Integration with real robot APIs

## Troubleshooting

**Embeddings not working?**
```bash
# Check if model is available
ollama list | grep mxbai-embed-large

# Pull if missing
ollama pull mxbai-embed-large:latest
```

**Robot not moving?**
- Check browser console for errors
- Verify robot is selected in dropdown
- Check Systems tab for execution status

**AI gives wrong type of response?**
- Check Systems tab to see detected intent
- Intent classification may need more examples
- Falls back to keyword matching if embeddings fail

**Systems card not updating?**
- Navigate to Systems tab after sending command
- Check if JavaScript console shows errors
- Updates happen in real-time during execution

## License
MIT License - Free to use and modify!
