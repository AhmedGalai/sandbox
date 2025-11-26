# PyQt Version Information

This is **template_8_qt**, a complete PyQt6 desktop conversion of the **template_7** web application.

## What Was Converted

### From Web (template_7) to Desktop (template_8_qt):

| Component | Web Version | PyQt Version |
|-----------|-------------|--------------|
| **UI Framework** | HTML/CSS/JavaScript | PyQt6 Widgets |
| **Server** | Node.js Express | None (standalone desktop app) |
| **Canvas** | HTML5 Canvas | QPainter |
| **Styling** | CSS | Qt Stylesheets |
| **Navigation** | HTML anchors | QTabWidget |
| **Forms** | HTML forms | Qt widgets (QLineEdit, QComboBox, etc.) |
| **Chat** | HTML div + JS | QTextEdit + QLineEdit |
| **Theme** | CSS classes | Qt stylesheets with ThemeManager |
| **Settings** | localStorage | QSettings |
| **Dialogs** | HTML modals | QDialog |
| **Tables** | HTML tables | QTableWidget |
| **Updates** | WebSocket | QTimer (polling) |

## Key Files Created

```
template_8_qt/
├── main.py                     # Entry point (NEW)
├── requirements.txt            # PyQt6 dependencies (NEW)
├── README.md                   # PyQt-specific documentation (UPDATED)
├── run.sh / run.bat           # Quick start scripts (NEW)
│
├── ui/                        # All NEW PyQt UI components
│   ├── main_window.py         # Main window with tabs
│   ├── login_dialog.py        # Login dialog
│   ├── dashboard_tab.py       # Main dashboard
│   ├── robot_canvas.py        # Robot visualization (QPainter)
│   ├── chat_widget.py         # Chat interface
│   ├── systems_tab.py         # Systems monitoring
│   ├── docs_tab.py            # Documentation viewer
│   └── settings_dialog.py     # Settings dialog
│
├── utils/                     # NEW utility modules
│   └── theme.py               # Theme manager (dark/light)
│
└── api/                       # COPIED from template_7
    └── main.py                # FastAPI backend (same as web version)
```

## Features Preserved

✓ Multi-robot control
✓ Robot visualization with path planning
✓ Chat interface
✓ Task control and task builder
✓ Dark/Light theme toggle
✓ Robot and map status displays
✓ Settings management
✓ Documentation viewer
✓ AI integration (via same backend API)

## New Desktop Features

✓ Native window management
✓ Menu bar with keyboard shortcuts
✓ QSettings for persistent configuration
✓ Native file dialogs
✓ Platform-specific styling
✓ Standalone executable (no browser needed)
✓ Better performance (native rendering)

## Running the Application

### Quick Start:
```bash
cd template_8_qt
pip install -r requirements.txt
python main.py
```

### With Backend API:
```bash
# Terminal 1 - Backend
cd template_8_qt/api
python main.py

# Terminal 2 - PyQt App
cd template_8_qt
python main.py
```

## Technical Highlights

### 1. Robot Canvas (robot_canvas.py)
- Uses QPainter for custom drawing
- Renders grid, obstacles, work points, and robots
- Supports multi-robot visualization with different colors
- Real-time path visualization

### 2. Theme System (utils/theme.py)
- Complete light/dark theme implementation
- Qt stylesheet-based
- Persistent theme preference via QSettings
- Covers all widgets and UI elements

### 3. Chat Widget (chat_widget.py)
- HTML-formatted messages in QTextEdit
- Color-coded user/bot messages
- Return key support for sending

### 4. Dashboard Layout (dashboard_tab.py)
- Splitter-based resizable panels
- Multi-robot selection with QListWidget
- Real-time status updates via QTimer
- Task control and task builder panels

### 5. Settings Management
- Uses QSettings for cross-platform persistence
- Stores theme preference, username, and app settings
- Automatic save/load

## Comparison Summary

**Web Version (template_7)**:
- Runs in browser
- Requires Node.js + Python backend
- HTML/CSS/JavaScript frontend
- WebSocket for real-time updates

**PyQt Version (template_8_qt)**:
- Native desktop application
- Python-only (no Node.js)
- PyQt6 widgets
- QTimer for updates
- Better performance
- Offline capable

## Next Steps

To extend or modify:

1. **Add features**: Edit dashboard_tab.py or create new tabs
2. **Modify theme**: Edit utils/theme.py stylesheets
3. **Change robot behavior**: Edit robot_canvas.py
4. **Add API calls**: Import requests/httpx in relevant widgets

## License

Same as template_7 - provided as-is for development and learning purposes.
