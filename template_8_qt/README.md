# Robot Simulator Dashboard - PyQt Version

A desktop application for robot control and monitoring, built with PyQt6. This is a PyQt conversion of the original web-based template_7 application.

## Features

- **Multi-Robot Control**: Monitor and control multiple robots simultaneously
- **Real-Time Visualization**: Interactive canvas showing robot positions, obstacles, and work points using QPainter
- **AI Chat Assistant**: Chat-based interface for controlling robots with natural language
- **Path Planning**: Visual path planning with A* algorithm and obstacle avoidance
- **Task Management**: Create, save, and execute multi-step tasks
- **Dark/Light Theme**: Toggle between dark and light UI themes with Qt styling
- **Robot Status Monitoring**: Real-time status updates for position, heading, tasks, and errors
- **Documentation Viewer**: Built-in documentation browser
- **Native Desktop UI**: Built with PyQt6 for Windows, macOS, and Linux

## Architecture

```
template_8_qt/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── ui/
│   ├── main_window.py      # Main window with tabs and menu
│   ├── login_dialog.py     # Login authentication dialog
│   ├── dashboard_tab.py    # Main dashboard with simulator
│   ├── robot_canvas.py     # Robot visualization canvas (QPainter)
│   ├── chat_widget.py      # Chat interface widget
│   ├── systems_tab.py      # AI task planning display
│   ├── docs_tab.py         # Documentation viewer
│   └── settings_dialog.py  # Settings dialog
├── utils/
│   └── theme.py            # Theme manager (light/dark)
├── api/
│   └── main.py             # FastAPI backend (from template_7)
└── data/                   # Local data storage
```

## Prerequisites

1. **Python 3.8+**
2. **PyQt6**
3. **Ollama** (optional, for AI features)

## Installation

### Install Python Dependencies

```bash
cd template_8_qt
pip install -r requirements.txt
```

### Optional: Install Ollama for AI Features

Download from [https://ollama.ai](https://ollama.ai), then:

```bash
ollama pull qwen3:latest
ollama serve
```

## Running the Application

### Quick Start (PyQt Only)

```bash
python main.py
```

### With Backend API (for AI features)

**Terminal 1 - Backend API:**
```bash
cd api
python main.py
```

**Terminal 2 - PyQt Application:**
```bash
python main.py
```

## Usage

### Login
- **Username**: `admin`
- **Password**: `admin`
- Your username is remembered between sessions

### Main Interface

**Dashboard Tab**:
- Robot simulator with interactive canvas
- Multi-robot selection (hold Ctrl)
- Real-time robot and map status
- Task control panel
- Task builder for multi-step operations
- Chat interface for natural language commands

**Systems Tab**:
- AI task planning visualization
- Execution status monitoring

**Docs Tab**:
- Built-in documentation viewer

### Theme Toggle
- Click 🌙/☀️ button in header
- Or use menu: View → Toggle Theme
- Or press Ctrl+T

### Robot Control

**Via Chat**:
- Type natural language commands
- "Move robot to point A"
- "Go to charging station"

**Via Task Control**:
1. Select robots (hold Ctrl for multiple)
2. Choose point (A, B, C, CHARGE, STANDBY)
3. Select action (Go, Lift, Wait)
4. Click "Execute Task"

**Via Task Builder**:
- Add multiple steps
- Save/load tasks as JSON
- Execute complex sequences

## How It Works

### Data Generation Flow

1. **User Input**: User chats with AI assistant
2. **AI Processing**: Ollama LLM (qwen3:latest) processes the request
3. **Tool Detection**: AI identifies when to use tools (create_data_card, modify_json_file)
4. **Tool Execution**: Backend executes the tool and generates data
5. **Data Formatting**:
   - For tables: Generates columns and rows
   - For charts: Generates labels and values, then creates chart image using matplotlib
6. **Storage**: Data saved to `data/` directory as JSON with topic metadata
7. **Display**: Data rendered as interactive cards with view-switching capability
8. **Topic Management**: Cards are organized by topic and filterable

### API Endpoints

**Python API (port 8000):**
- `POST /api/generate-data` - Generate data from prompt
- `GET /api/data/{data_id}` - Retrieve specific dataset
- `GET /api/data/list` - List all saved datasets
- `DELETE /api/data/{data_id}` - Delete a dataset
- `POST /api/chat` - Chat with AI assistant (with tool support)
- `POST /api/modify-json` - Modify existing JSON data files
- `WS /ws/{topic}` - WebSocket for real-time updates

**Node.js API (port 3000):**
- `POST /api/login` - User authentication
- `POST /api/logout` - User logout
- `GET /api/check-auth` - Check authentication status
- `POST /api/save-settings` - Save user settings

## Data Storage Format

Generated data is stored in `data/` as JSON files:

**Table Format:**
```json
{
  "type": "table",
  "title": "Monthly Sales Data",
  "topic": "Sales",
  "columns": ["Month", "Revenue", "Units"],
  "rows": [
    ["January", "$50,000", "1,200"],
    ["February", "$55,000", "1,350"]
  ],
  "created": "2024-01-15T10:30:00"
}
```

**Chart Format:**
```json
{
  "type": "chart",
  "chart_type": "line",
  "title": "Revenue Trend",
  "topic": "Finance",
  "labels": ["Jan", "Feb", "Mar", "Apr"],
  "values": [50, 55, 60, 58],
  "image": "data:image/png;base64,...",
  "created": "2024-01-15T10:30:00"
}
```

## Customization

### Changing the AI Model

Edit `api/main.py`:
```python
OLLAMA_MODEL = "your-model:latest"
```

### Adding New Chart Types

1. Update `api/main.py` - Add to `generate_chart_from_data()`
2. Update `views/index.html` - Add option to chartType select
3. Update chart generation logic in matplotlib

### Styling

Modify `public/css/style.css` or add custom styles in `views/index.html`

## Troubleshooting

### "Failed to generate data"
- Ensure Ollama is running: `ollama serve`
- Verify the Python API is running on port 8000
- Check if qwen3:latest model is installed: `ollama list`

### "AI service is not available"
- Start Ollama: `ollama serve`
- Verify Ollama is accessible at http://localhost:11434

### Charts not displaying
- Check Python matplotlib installation: `pip install matplotlib`
- Verify PIL/Pillow is installed: `pip install Pillow`

### Port conflicts
- Change Node.js port in `server.js`: `const PORT = 3001`
- Change Python port in `api/main.py`: `uvicorn.run(app, port=8001)`
- Update `public/js/app.js` with new API URL

## Security Notes

⚠️ This is a development application with basic authentication:
- Default credentials are hardcoded (admin/admin)
- No password hashing
- Session secret is static
- CORS is fully open

For production use:
- Implement proper authentication
- Use environment variables for secrets
- Add input validation and sanitization
- Implement rate limiting
- Use HTTPS
- Add proper error handling

## License

This project is provided as-is for development and learning purposes.

## Support

For issues or questions, please check:
1. Ollama is running and accessible
2. Both servers are started
3. All dependencies are installed
4. Port 3000 and 8000 are available
