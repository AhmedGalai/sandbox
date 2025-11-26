# Robot Simulator Dashboard - Template 6

## Quick Summary of Changes

Template 6 extends Template 5 with these major improvements:

### 🆕 Key Features

1. **📚 Documentation Tab**
   - Full-width accordion layout for all markdown docs
   - Searchable by the chatbot
   - Dark theme support

2. **🤖 Multi-Robot Task Execution**
   - All selected robots receive and execute tasks
   - Map displays all selected robots regardless of selection order
   - Parallel task execution

3. **💬 Enhanced Chatbot**
   - Answers questions about robot status, map, and documentation
   - Multi-step task parsing: "go to A, then B, then charge"
   - Context-aware responses with fleet status
   - Documentation search integration

4. **✅ Task Confirmation System**
   - Confirmation modal before executing tasks
   - Toggle on/off in Settings tab
   - Saves preference to localStorage

5. **🎯 Improved Task Control & Builder**
   - Works with all selected robots
   - Confirmation prompts for all actions
   - Parallel execution support

## Quick Start

```bash
# Terminal 1: Start Node.js server
cd template_6
npm install
npm start
# Opens on http://localhost:3000

# Terminal 2: Start Python API (optional, for AI features)
cd template_6/api
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8000
```

**Login**: admin / admin

## Usage Examples

### Multi-Robot Control
```
1. Select ROB-001, ROB-002, ROB-003 from dropdown
2. Chat: "go to point A"
3. Confirm in modal
4. All three robots navigate to A
```

### Multi-Step Tasks
```
Chat: "go to A, then B, then charge"
→ Creates 3-step task for selected robots
```

### Information Queries
```
"where are all the robots?" → Shows positions
"what's the map status?" → Shows grid info
"how do I run tests?" → Searches documentation
```

## New Settings

Go to **Settings** tab:
- ✅ **Confirm Before Executing Tasks** - Show confirmation modal (default: ON)
- ✅ **Enable Simulator** - Run simulator mode

## Files Changed from Template 5

- `views/index.html` - Added docs tab, confirmation modal, settings checkbox
- `public/css/style.css` - Added accordion and modal styles
- `public/js/app.js` - Enhanced chat, confirmation system, docs loading, multi-robot support
- `server.js` - Added `/docs/:filename` endpoint
- `api/main.py` - Enhanced `/api/robot/task` with context data and multi-step parsing

## Architecture

```
Frontend (Browser)
  ↓ Chat message with context
Python API (port 8000)
  - Receives robot/map/docs context
  - Calls Ollama AI for response
  - Parses multi-step tasks
  - Returns structured response
  ↓
Frontend
  - Shows confirmation modal
  - Executes task on all selected robots
  - Updates map visualization
```

## Embedding Support (Ready for Future)

The system is prepared to use **ollama/mxbai-embed-large:latest** for semantic document search. Currently using keyword-based search, but infrastructure is in place for embedding integration.

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile: ⚠️ Responsive, but desktop recommended

## For More Details

See **TEMPLATE6_FEATURES.md** for complete feature documentation.

## Troubleshooting

**Docs tab not loading?**
- Check that markdown files exist in template_6/ directory
- Check browser console for errors
- Ensure Node.js server is running

**Chatbot not responding?**
- Python API must be running on port 8000
- Check if Ollama is installed and running
- Verify OLLAMA_MODEL is available

**Confirmation modal not showing?**
- Check Settings → "Confirm Before Executing Tasks" is enabled
- Clear localStorage and refresh: `localStorage.clear()`

**Map not showing robots?**
- At least one robot must be selected
- Try reloading the page
- Check browser console for errors

## License

MIT License - Feel free to modify and extend!
