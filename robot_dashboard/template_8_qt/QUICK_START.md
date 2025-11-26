# Quick Start Guide - Robot Simulator Dashboard (PyQt)

## Installation (1 minute)

```bash
cd template_8_qt
pip install PyQt6
```

## Run (5 seconds)

```bash
python main.py
```

Or use the convenience script:
```bash
./run.sh          # Linux/Mac
run.bat           # Windows
```

## Login

- **Username**: admin
- **Password**: admin

## First Steps

1. **See the robots**: Look at the map canvas showing multiple robots
2. **Select robots**: Hold Ctrl and click multiple robots in the list
3. **Move a robot**:
   - Select "Point A" from dropdown
   - Click "Execute Task"
4. **Try chat**: Type "Move robot to point B" in the chat box
5. **Toggle theme**: Click the 🌙 or ☀️ button

## Keyboard Shortcuts

- **Ctrl+T**: Toggle theme
- **Ctrl+Q**: Quit
- **Enter**: Send chat message (when in chat input)

## What You'll See

### Dashboard Tab (Default)
- Left: Chat interface for robot commands
- Center: Robot simulator map with grid
- Right: Task controls and task builder

### Systems Tab
- AI task planning display
- Execution status

### Docs Tab
- Built-in documentation

## Optional: Enable AI Features

If you want full AI chat capabilities:

```bash
# Terminal 1 - Start backend API
cd api
python main.py

# Terminal 2 - Start PyQt app
cd ..
python main.py
```

This enables natural language processing for robot commands.

## Troubleshooting

**Problem**: App won't start
- **Solution**: Make sure PyQt6 is installed: `pip install PyQt6`

**Problem**: Can't see robots
- **Solution**: The canvas should show robots immediately. Try resizing the window.

**Problem**: Theme button doesn't work
- **Solution**: Click it again, the theme should toggle immediately.

## What's Next?

- Explore the task builder to create multi-step robot tasks
- Try controlling multiple robots simultaneously
- Save and load task sequences
- Check out the documentation in the Docs tab

## Need Help?

- Check README.md for detailed documentation
- See PYQT_VERSION.md for technical details about the conversion
- All source code is in `ui/` directory - easy to modify!
