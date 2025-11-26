# Testing Intent Classification - Template 7

## How to Test

1. Start the servers:
```bash
# Terminal 1
npm start

# Terminal 2
cd api && python main.py
```

2. Open http://localhost:3000 and login (admin/admin)

3. Navigate to the **Systems** tab to watch intent classification in real-time

4. Try the test queries below in the chatbot

## Test Cases

### ✅ Query Intents (Should NOT Execute - Just Answer)

#### Test 1: Robot Status Query
```
Input: "give info about robot status"
Expected Intent: query_status
Expected Behavior: Returns robot position, heading, status info
Should NOT: Try to move robot or show confirmation modal
```

#### Test 2: Robot Location
```
Input: "where is the robot?"
Expected Intent: query_status
Expected Behavior: Returns current position
Should NOT: Execute any movement
```

#### Test 3: Map Information
```
Input: "show me map status"
Expected Intent: query_map
Expected Behavior: Returns grid size, obstacles, work points
Should NOT: Change anything on map
```

#### Test 4: Documentation Query
```
Input: "how do I run tests?"
Expected Intent: query_docs
Expected Behavior: Searches documentation and returns answer
Should NOT: Execute any commands
```

### ✅ Task Intents (Should Execute with Confirmation)

#### Test 5: Simple Navigation
```
Input: "go to B"
Expected Intent: task_navigation
Expected Behavior:
- Shows confirmation modal
- Executes movement to Point B after confirmation
```

#### Test 6: Multi-Step Task
```
Input: "GO TO b THEN TO c"
Expected Intent: task_complex
Expected Behavior:
- Parses 2 steps (B, then C)
- Shows confirmation for multi-step task
- Executes sequentially after confirmation
```

## What to Watch in Systems Tab

The Systems tab should show:
```
Intent: query_status (confidence: 85%)
Query: "give info about robot status"
```

or

```
Intent: task_navigation (confidence: 92%)
Query: "go to B"
```

## Expected Console Output

When you send "give info about robot status", Python console should show:
```
Robot task received: give info about robot status
Context data available: True
Intent classified: query_status (confidence: 0.75)
```

## Debugging

### If all queries execute as tasks:

1. Check Python console - is intent classification working?
2. Check browser console for errors
3. Verify embedding model is loaded: `ollama list | grep mxbai`
4. Check Systems tab - what intent is detected?

### If embeddings are slow:

First query will be slow (model loading). Subsequent queries should be faster.

### If intent is always wrong:

- Confidence might be low
- Embedding model might not be running
- Falls back to keyword matching

## Confidence Thresholds

- **High confidence** (>0.7): Intent is very likely correct
- **Medium confidence** (0.5-0.7): Intent is probable
- **Low confidence** (<0.5): Falls back to keyword matching

## Success Criteria

✅ "give info about robot status" → Returns info, does NOT execute
✅ "where is the robot" → Returns position, does NOT show confirmation
✅ "go to B" → Shows confirmation, then executes
✅ "GO TO b THEN TO c" → Multi-step confirmation, then executes both
✅ Systems tab shows correct intent classification
✅ Confidence scores appear in Systems tab

## Common Issues

**All queries treated as tasks:**
- Frontend not checking `isQueryIntent`
- API not returning `intent` field
- Check both are updated

**Confirmation shown for queries:**
- Check `isQueryIntent` condition in frontend
- Verify `data.intent.startsWith('query_')`

**Wrong intent detected:**
- Embedding model might not be loaded
- Try pulling again: `ollama pull mxbai-embed-large:latest`
- Check fallback keyword matching is working
