# Template 1 - Custom Data Dashboard

A dynamic dashboard application where users can generate custom data visualizations through an AI-powered chat interface. The system uses AI (Ollama qwen3:latest) with tool calling to create and manage data visualizations, saves them to local files, and displays them on an interactive dashboard.

## Features

- **AI Chat with Tool Support**: Chat with an AI assistant that can create data cards, modify JSON files, and generate visualizations
- **Flexible View Switching**: Toggle between table and chart views for each data card
- **Dark/Light Theme**: Switch between dark and light themes with persistent preference
- **Session Storage**: Username is remembered during the session for convenient login
- **Topic-Based Organization**: Filter data cards by topics (Sales, Marketing, Finance, Operations, HR)
- **Placeholder Cards**: Empty placeholder cards show topics without data
- **Local Data Storage**: All generated data is saved to local JSON files
- **Real-Time Streaming**: Data is streamed from the Python API to the Node.js server
- **Responsive Design**: Clean, modern UI with smooth interactions and theme support

## Architecture

```
template_1/
├── server.js          # Node.js Express server (port 3000)
├── api/
│   └── main.py        # FastAPI Python backend with tool support (port 8000)
├── data/              # Local data storage (JSON files)
├── public/
│   ├── js/
│   │   └── app.js     # Frontend JavaScript with theme & topic filtering
│   └── css/
│       └── style.css  # Styles with dark theme support
└── views/
    └── index.html     # Main HTML page
```

## Prerequisites

1. **Node.js** (v14 or higher)
2. **Python 3.8+**
3. **Ollama** (with qwen3:latest model)

## Installation

### 1. Install Node.js Dependencies

```bash
npm install
```

### 2. Install Python Dependencies

```bash
cd api
pip install -r requirements.txt
cd ..
```

### 3. Install and Start Ollama

Download Ollama from [https://ollama.ai](https://ollama.ai), then:

```bash
ollama pull qwen3:latest
ollama serve
```

## Running the Application

You need to start both servers:

### Option 1: Using the Start Script (Linux/Mac)

```bash
chmod +x start.sh
./start.sh
```

### Option 2: Using the Start Script (Windows)

```bash
start.bat
```

### Option 3: Manual Start

**Terminal 1 - Python API:**
```bash
cd api
python main.py
# or
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Node.js Server:**
```bash
node server.js
```

## Usage

1. **Login**: Open http://localhost:3000 and login with:
   - Username: `admin`
   - Password: `admin`
   - Your username will be remembered during the session

2. **Theme Toggle**:
   - Click the 🌙/☀️ button in the navbar to switch between dark and light themes
   - Your preference is saved to localStorage

3. **Generate Data via Chat**:
   - Use the chat assistant to create data cards
   - Example: "Create a sales table with Q1 2024 data for the Sales topic"
   - Example: "Generate a bar chart showing monthly revenue for Marketing"
   - The AI will automatically create cards with the data
   - Specify topics (Sales, Marketing, Finance, Operations, HR) to organize data

4. **View and Filter Data**:
   - Use the topic filter dropdown to show only specific topics
   - Select multiple topics to view them together
   - Empty placeholder cards show topics with no data yet
   - Click the dropdown on each card to switch between table and chart views

5. **Chat Assistant Tools**:
   - The AI can create new data cards (tables or charts)
   - The AI can modify existing JSON data files
   - Ask it to create visualizations for specific topics
   - The AI understands natural language requests

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
