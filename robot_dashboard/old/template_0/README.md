# Template 0 - Custom Data Dashboard

A dynamic dashboard application where users can generate custom data visualizations from natural language prompts. The system uses AI (Ollama) to generate data, saves it to local files, and streams it to a Node.js server for display.

## Features

- **AI-Powered Data Generation**: Describe what data you want in natural language, and the system generates it
- **Flexible Display Options**: Choose to display data as tables or charts (line, bar, or pie)
- **Local Data Storage**: All generated data is saved to local JSON files
- **Real-Time Streaming**: Data is streamed from the Python API to the Node.js server
- **Interactive Chat**: Built-in chat assistant powered by Ollama
- **Data Management**: Load, view, and delete saved data
- **Responsive Design**: Clean, modern UI with smooth interactions

## Architecture

```
template_0/
├── server.js          # Node.js Express server (port 3000)
├── api/
│   └── main.py        # FastAPI Python backend (port 8000)
├── data/              # Local data storage (JSON files)
├── public/
│   ├── js/
│   │   └── app.js     # Frontend JavaScript
│   └── css/
│       └── style.css  # Styles
└── views/
    └── index.html     # Main HTML page
```

## Prerequisites

1. **Node.js** (v14 or higher)
2. **Python 3.8+**
3. **Ollama** (with qwen2.5:latest model)

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
ollama pull qwen2.5:latest
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

2. **Generate Data**:
   - In the sidebar, describe the data you want (e.g., "Generate monthly sales data for 2024")
   - Choose display type: Table or Chart
   - If Chart is selected, choose chart type: Line, Bar, or Pie
   - Click "Generate Data"
   - Your data will appear as a new card on the dashboard

3. **Manage Data**:
   - View all saved data in the sidebar list
   - Click "Load" to display a saved dataset
   - Click "Delete" to remove a dataset

4. **Chat Assistant**:
   - Use the chat for general questions
   - The chat uses Ollama's AI model for responses

## How It Works

### Data Generation Flow

1. **User Input**: User describes data in natural language
2. **AI Processing**: Ollama LLM generates structured data (JSON)
3. **Data Formatting**:
   - For tables: Generates columns and rows
   - For charts: Generates labels and values, then creates chart image using matplotlib
4. **Storage**: Data saved to `data/` directory as JSON
5. **Display**: Data rendered as interactive cards on dashboard

### API Endpoints

**Python API (port 8000):**
- `POST /api/generate-data` - Generate data from prompt
- `GET /api/data/{data_id}` - Retrieve specific dataset
- `GET /api/data/list` - List all saved datasets
- `DELETE /api/data/{data_id}` - Delete a dataset
- `POST /api/chat` - Chat with AI assistant
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
  "columns": ["Month", "Revenue", "Units"],
  "rows": [
    ["January", "$50,000", "1,200"],
    ["February", "$55,000", "1,350"]
  ],
  "created": "2024-01-15T10:30:00",
  "prompt": "Generate monthly sales data"
}
```

**Chart Format:**
```json
{
  "type": "chart",
  "chart_type": "line",
  "title": "Revenue Trend",
  "labels": ["Jan", "Feb", "Mar", "Apr"],
  "values": [50, 55, 60, 58],
  "image": "data:image/png;base64,...",
  "created": "2024-01-15T10:30:00",
  "prompt": "Show revenue trend for Q1"
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
- Check if qwen2.5:latest model is installed: `ollama list`

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
