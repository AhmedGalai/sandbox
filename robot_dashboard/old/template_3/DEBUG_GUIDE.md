# Debugging Guide - Tool Calling Issues

## Problem

When you ask: **"generate sales data in the form of y = x+2"**
You get: **"an error occurred"**

## What I've Added

I've added extensive logging to help diagnose the issue. The Python API server now logs:

1. **Raw AI Response**: The exact response from Ollama
2. **JSON Parsing**: Whether it found a tool call
3. **Tool Execution**: Parameters passed and result
4. **Errors**: Full stack traces for debugging

## How to See the Logs

### Start the Servers

```bash
cd /home/ag/Desktop/sandbox/template_1

# Terminal 1: Start Node server
node server.js

# Terminal 2: Start Python server (with logs visible)
cd api
python3 main.py
```

Now when you test in the UI, you'll see detailed logs in Terminal 2.

## What to Look For

When you send: `"generate sales data in the form of y = x+2"`

**In the Python terminal, you should see:**

```
=== AI Response ===
Raw response: {...
==================

Response is not valid JSON: ...
(or)
Successfully parsed tool call: create_data_card

=== Executing Tool: create_data_card ===
Parameters: {...}
Creating data card with params: {...}
Created table with X columns and Y rows
Data saved to: /path/to/data_123.json
Tool result: {'success': True, ...}
```

## Common Issues

### Issue 1: AI Responds with Text Instead of JSON

**Logs show:**
```
=== AI Response ===
Raw response: Here's the sales data: ...
==================
No JSON found in response
No valid tool call detected - passing through AI response
```

**Solution**: The AI didn't understand it should use a tool. Try more explicit prompts:
- ✅ "Create a table with sales data where y = x+2 for the Sales topic"
- ✅ "Generate a sales table using the formula y = x+2"

### Issue 2: JSON Parsing Fails

**Logs show:**
```
=== AI Response ===
Raw response: {"tool": "create_data_card", "parameters": ...
==================
Response is not valid JSON: Expecting property name enclosed in double quotes
```

**Solution**: The AI generated malformed JSON. Check the raw response in the logs.

### Issue 3: Tool Execution Fails

**Logs show:**
```
=== Executing Tool: create_data_card ===
Parameters: {'title': '...', 'type': 'table', 'data': {}}
ERROR: 'columns'
Tool result: {'success': False, 'error': "'columns'"}
```

**Solution**: The AI didn't provide required fields. The data needs:
- For tables: `columns` and `rows`
- For charts: `chart_type`, `labels`, and `values`

### Issue 4: Generic "An Error Occurred"

**Logs show:**
```
!!! EXCEPTION in tool parsing !!!
Error: ...
Full response: ...
```

**Solution**: There's a Python exception. Check the full traceback in the logs.

## Testing with Curl

You can test the API directly:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "generate sales data in the form of y = x+2",
    "context": []
  }' | python3 -m json.tool
```

This will show you the exact response from the API.

## Expected Behavior

**Good Request:**
```
User: "Create a sales table for Q1 2024 for the Sales topic"
```

**Logs:**
```
=== AI Response ===
Raw response: {"tool": "create_data_card", ...
==================
Successfully parsed tool call: create_data_card
=== Executing Tool: create_data_card ===
Parameters: {'title': 'Q1 2024 Sales', 'type': 'table', ...}
Creating data card with params: ...
Created table with 3 columns and 4 rows
Data saved to: .../data/data_1234567890.json
Tool result: {'success': True, 'data_id': 'data_1234567890', ...}
```

**UI Shows:**
```
✅ I've created a new table card titled 'Q1 2024 Sales' for the Sales topic. You can see it on your dashboard!
```

## Mathematical Formula Request

For your specific request: `"generate sales data in the form of y = x+2"`

The AI needs to:
1. Understand you want a data card
2. Generate x values (e.g., 1, 2, 3, 4, 5)
3. Calculate y values (e.g., 3, 4, 5, 6, 7)
4. Format as a tool call

**Better Prompt:**
```
Create a table showing x and y values where y = x + 2, with x from 1 to 10, for the Sales topic
```

Or:
```
Generate a line chart with the equation y = x + 2 for x values 1 through 10
```

## Next Steps

1. Start both servers as shown above
2. Open http://localhost:3000
3. Login (admin/admin)
4. Try the mathematical formula request
5. Watch the Python terminal for detailed logs
6. Share the logs with me if there's still an issue

The logs will tell us exactly what's happening!
