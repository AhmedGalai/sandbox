# Template 1 - Testing Guide

## Tool Calling System

The AI chat assistant now has proper tool support. When you ask it to create data, it will use the `create_data_card` tool to actually create the data and save it to JSON files.

## How It Works

1. **User Request**: You ask the AI to create data
2. **AI Response**: AI formats a tool call in JSON
3. **Tool Execution**: Backend executes the tool and creates the data
4. **Data Storage**: Data is saved to `data/` directory as JSON
5. **UI Update**: Frontend automatically displays the new card
6. **Confirmation**: AI sends a friendly confirmation message

## Testing Examples

### Test 1: Create a Sales Table

**Chat Input:**
```
Create a sales table for Q1 2024 with monthly revenue and units sold for the Sales topic
```

**Expected Behavior:**
- AI should use the `create_data_card` tool
- A new card should appear on the dashboard
- The card should be tagged with "Sales" topic
- Data should be saved to `data/data_[timestamp].json`
- You'll see a success message like "✅ I've created a new table card titled 'Q1 2024 Sales' for the Sales topic."

### Test 2: Create a Marketing Chart

**Chat Input:**
```
Generate a bar chart showing marketing campaign performance for the Marketing topic
```

**Expected Behavior:**
- AI creates a chart with sample data
- Chart image is generated using matplotlib
- Card appears with a chart view
- Can switch to table view using the dropdown

### Test 3: Create Finance Data

**Chat Input:**
```
Show me a line chart of monthly expenses for Finance
```

**Expected Behavior:**
- Creates a line chart
- Tagged with Finance topic
- Appears in the Finance filter

### Test 4: Multiple Topics

**Chat Input:**
```
Create HR data showing employee headcount by department
```

**Expected Behavior:**
- Creates data for HR topic
- Topic filter updates to include HR if not already there
- Placeholder card for HR is replaced with actual data

## Troubleshooting

### AI Responds with Text Instead of Tool Call

**Symptom:** AI describes the data instead of creating it

**Solution:**
1. Check that Ollama is running with qwen3:latest
2. Make sure the Python API is running (check console for errors)
3. Try restarting the Python API
4. Check the API console logs for "Found tool call:" messages

### Tool Call Found But Data Not Created

**Symptom:** Console shows "Found tool call" but no card appears

**Check:**
1. Look at Python console for error messages
2. Check that `data/` directory exists and is writable
3. Verify the tool_result in the browser console (Network tab)

### Card Appears But Wrong Format

**Symptom:** Card shows but data is incorrect

**Check:**
1. Look at the JSON file in `data/` directory
2. Check that columns/rows or labels/values are correctly formatted
3. Verify the chart image is being generated (for charts)

## Debugging

### Enable Verbose Logging

The Python API already logs:
- Tool call detection
- Data creation steps
- File save locations
- Chart generation status

Check the terminal where you ran `python api/main.py` or `uvicorn main:app`

### Check Generated Files

Look in the `data/` directory:
```bash
ls -la template_1/data/
cat template_1/data/data_*.json
```

### Test the API Directly

You can test the tool execution directly:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a sales table for Q1 2024",
    "context": []
  }'
```

Check the response for:
- `tool_result.success: true`
- `tool_result.data_id`
- Friendly confirmation message

## Expected File Structure

After creating data, you should see:

```
template_1/
├── data/
│   ├── data_1234567890.json  # Sales data
│   ├── data_1234567891.json  # Marketing data
│   └── data_1234567892.json  # Finance data
```

Each JSON file contains:
```json
{
  "title": "Q1 2024 Sales",
  "type": "table",
  "topic": "Sales",
  "columns": ["Month", "Revenue", "Units"],
  "rows": [
    ["January", "$50000", "1200"],
    ["February", "$55000", "1350"],
    ["March", "$60000", "1500"]
  ],
  "created": "2025-01-15T10:30:00"
}
```

## Success Indicators

✅ **Working Correctly:**
- AI responds with tool call JSON (visible in console)
- Backend logs "Found tool call"
- Backend logs "Data saved to: ..."
- Card appears on dashboard immediately
- JSON file created in data/ directory
- Friendly confirmation message shown in chat

❌ **Not Working:**
- AI just describes data without creating it
- No card appears
- No JSON file created
- Error messages in console

## Common Issues

### Issue: "Temperature too low, responses not creative"

This is intentional! We set temperature to 0.1 to make tool formatting consistent. The AI should be deterministic when formatting tool calls.

### Issue: "AI includes extra text with tool call"

The parser handles this. It extracts the JSON even if there's surrounding text. Check console logs to verify.

### Issue: "Topic not appearing in filter"

The topic filter updates when cards are added. If you don't see it:
1. Refresh the page
2. Check that the data has a "topic" field
3. Look for the placeholder card for that topic

## Tips

1. **Be Specific**: Include the topic name in your request
   - ✅ "Create sales data for the Sales topic"
   - ❌ "Create some data"

2. **Specify Type**: Tell the AI if you want table or chart
   - ✅ "Generate a bar chart..."
   - ✅ "Create a table showing..."

3. **Clear Requests**: Simple, direct requests work best
   - ✅ "Show Q1 sales data as a table"
   - ❌ "I was thinking maybe we could look at some sales stuff from earlier this year possibly in a tabular format if that's cool"

4. **Use Examples**: Reference the examples in this guide
