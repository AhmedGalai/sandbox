# Styled Dashboard App

A feature-rich full-stack web application with a modern dashboard interface, AI-powered chatbot, real-time data streaming, and draggable card system.

## Architecture

This application uses a **dual-server architecture**:

1. **Node.js Server** (Port 3000): Authentication, session management, and serving the frontend
2. **Python FastAPI Server** (Port 8000): Real-time data publishing, AI chat (Ollama), and data processing

### Data Flow

```
Frontend (Browser)
    ↓
    ├── Authentication & Sessions → Node.js Server (Port 3000)
    ├── Real-time Data (WebSocket) → Python API (Port 8000)
    ├── REST API Polling → Python API (Port 8000)
    └── AI Chat (Ollama) → Python API (Port 8000)
```

## Features

### Core Features
- **Authentication**: Secure login modal with credentials (username: `admin`, password: `admin`)
- **Horizontal Navbar**: Navigation between Dashboard and Settings pages
- **Sidebar Chatbot**: AI-powered chat assistant using Ollama (qwen2.5:latest model)
- **Card Grid System**: Responsive grid displaying various data cards
- **Multi-Select Filter**: Toggle card visibility using a multi-select dropdown
- **Drag & Drop**: Rearrange cards by dragging them to new positions
- **Save Layout**: Persist your card arrangement
- **Settings Page**: Customizable user preferences with multiple input fields
- **Markdown Support**: Cards can render markdown including tables, text formatting, lists, code blocks, and images

### Real-time Data Features
- **WebSocket Subscriptions**: Real-time data streaming to dashboard cards
- **Automatic Polling Fallback**: Falls back to REST API polling if WebSocket unavailable
- **Topic-based Updates**: Each card subscribes to specific data topics
- **Dynamic Data Generation**: Auto-generated analytics, user stats, revenue, tasks, performance metrics, and activity logs

### AI Chat Features
- **Ollama Integration**: Uses qwen2.5:latest model for intelligent responses
- **Context-Aware**: Maintains conversation context (last 20 messages)
- **Markdown Support**: Chat responses support markdown formatting
- **Typing Indicator**: Visual feedback while AI generates responses
- **Fallback Messages**: Graceful degradation if Ollama is unavailable

## Installation

### Prerequisites

1. **Node.js** (v14 or higher)
2. **Python** (v3.8 or higher)
3. **Ollama** (for AI chat functionality)
   ```bash
   # Install Ollama from https://ollama.ai/
   # Then pull the model:
   ollama pull qwen2.5:latest
   ```

### Setup

1. Navigate to the project directory:
```bash
cd styled-dashboard-app
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Install Python dependencies:
```bash
cd api
pip install -r requirements.txt
```

## Running the Application

You need to run **both servers** for full functionality:

### 1. Start the Python API Server

```bash
cd api
python main.py
```

The Python API will be available at: `http://localhost:8000`

You can view the API documentation at: `http://localhost:8000/docs`

### 2. Start the Node.js Server

In a new terminal:

```bash
npm start
```

The frontend will be available at: `http://localhost:3000`

### 3. Ensure Ollama is Running

```bash
ollama serve
```

Then verify the model is available:
```bash
ollama run qwen2.5:latest
```

## Usage

1. **Login**: When you first open the app, you'll see a login modal. Use:
   - Username: `admin`
   - Password: `admin`

2. **Dashboard**: After logging in, you'll see the main dashboard with:
   - 6 cards showing real-time data (updated every 5 seconds)
   - Analytics table with website metrics
   - User statistics
   - Revenue overview
   - Task list with completion tracking
   - System performance metrics
   - Recent activity log
   - Multi-select dropdown to show/hide specific cards
   - Drag cards to rearrange them
   - Click "Save Layout" to save your arrangement

3. **Chatbot**: Use the sidebar chatbot to:
   - Ask questions about your dashboard data
   - Get AI-powered assistance
   - Have natural conversations (powered by Ollama)
   - View markdown-formatted responses

4. **Settings**: Click "Settings" in the navbar to:
   - Update display name and email
   - Change theme preferences (Light/Dark)
   - Configure notifications
   - Set language (EN/ES/FR)
   - Set timezone (UTC/EST/PST)
   - Settings are saved to both servers

5. **Logout**: Click the "Logout" button in the navbar to return to the login screen

## Project Structure

```
styled-dashboard-app/
├── api/
│   ├── main.py                # Python FastAPI server
│   └── requirements.txt       # Python dependencies
├── public/
│   ├── css/
│   │   └── style.css         # All styling
│   └── js/
│       └── app.js            # Client-side JavaScript with WebSocket & API integration
├── views/
│   └── index.html            # Main HTML template
├── server.js                 # Node.js Express server
├── package.json              # Node.js dependencies
└── README.md                 # This file
```

## Technologies Used

### Backend
- **Node.js**: Express.js, Express-Session
- **Python**: FastAPI, Uvicorn
- **WebSocket**: Real-time bidirectional communication
- **Ollama**: AI chat model integration (qwen2.5:latest)
- **Data Visualization**: Matplotlib (chart generation)
- **Image Processing**: Pillow

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with Flexbox and Grid
- **Markdown**: Marked.js (loaded from CDN)
- **Drag & Drop**: HTML5 Drag and Drop API
- **WebSocket API**: Native browser WebSocket support

## API Endpoints

### Node.js Server (Port 3000)

- `POST /api/login` - Authenticate user
- `POST /api/logout` - End user session
- `POST /api/save-layout` - Save card layout
- `POST /api/save-settings` - Save user settings
- `GET /api/check-auth` - Check authentication status

### Python FastAPI Server (Port 8000)

#### REST Endpoints
- `GET /` - API information and endpoint list
- `GET /api/data/analytics` - Get analytics table data
- `GET /api/data/users` - Get user statistics
- `GET /api/data/revenue` - Get revenue data
- `GET /api/data/tasks` - Get tasks data
- `GET /api/data/performance` - Get performance metrics
- `GET /api/data/activity` - Get activity log
- `GET /api/data/chart/{type}` - Generate chart image (line/bar/pie)
- `POST /api/chat` - Send message to AI chatbot (Ollama)
- `POST /api/settings` - Save user settings

#### WebSocket Endpoints
- `WS /ws/{topic}` - Subscribe to real-time data updates for a specific topic
  - Topics: `analytics`, `users`, `revenue`, `tasks`, `performance`, `activity`
  - Data is broadcast every 5 seconds to all subscribers

### API Documentation

View interactive API documentation at: `http://localhost:8000/docs`

## Data Topics & Card Mapping

| Card | Topic | Data Type | Update Frequency |
|------|-------|-----------|------------------|
| Analytics | `analytics` | Table | Every 5 seconds |
| User Stats | `users` | Statistics | Every 5 seconds |
| Revenue | `revenue` | Table | Every 5 seconds |
| Tasks | `tasks` | Task List | Every 5 seconds |
| Performance | `performance` | Metrics | Every 5 seconds |
| Activity | `activity` | Log Entries | Every 5 seconds |

## Customization

### Adding New Cards

1. **Update Frontend** (`/public/js/app.js`):
```javascript
{
    id: 'card7',
    title: 'Your Title',
    icon: '🎨',
    topic: 'your-topic',
    content: `## Loading...`
}
```

2. **Add Python API Endpoint** (`/api/main.py`):
```python
@app.get("/api/data/your-topic")
async def get_your_topic():
    return {
        "type": "table",  # or "stats", "metrics", "log", "tasks"
        "title": "Your Title",
        "data": {...}
    }
```

3. **Add to WebSocket Broadcasting**:
```python
async def publish_data_periodically():
    while True:
        await asyncio.sleep(5)
        await manager.broadcast("your-topic", generate_your_data())
```

### Styling

Modify `/public/css/style.css` to change colors, layouts, or add new styles.

### Configuring Data Update Frequency

Edit `/api/main.py`, line with `await asyncio.sleep(5)` to change update interval (in seconds).

### Changing AI Model

Edit `/api/main.py`:
```python
OLLAMA_MODEL = "qwen2.5:latest"  # Change to any Ollama model
```

Available models:
- `qwen2.5:latest` (Default, fast and capable)
- `llama3:latest` (Meta's Llama 3)
- `mistral:latest` (Mistral AI)
- `codellama:latest` (Code-specialized)

Pull models with: `ollama pull <model-name>`

## Configuration

### Frontend API URLs

Edit `/public/js/app.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';  // Python API
const WS_BASE_URL = 'ws://localhost:8000';     // WebSocket
```

### Toggle WebSocket vs Polling

Edit `/public/js/app.js`:
```javascript
let useWebSocket = true;  // Set to false to use polling instead
```

### Server Ports

**Node.js Server**: Edit `server.js`:
```javascript
const PORT = process.env.PORT || 3000;
```

**Python API**: Edit `/api/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Troubleshooting

### WebSocket Connection Fails
- Ensure Python API is running on port 8000
- Check browser console for connection errors
- App will automatically fallback to polling mode

### Ollama Chat Not Working
- Verify Ollama is running: `ollama list`
- Check model is installed: `ollama pull qwen2.5:latest`
- Ensure Ollama is accessible at `http://localhost:11434`
- The app will show fallback messages if Ollama is unavailable

### CORS Errors
- Python API has CORS enabled for all origins
- If issues persist, check browser console and API logs

### Data Not Updating
- Check both servers are running
- Open browser DevTools → Network tab
- Verify WebSocket connections or API polling requests
- Check Python API logs for errors

## Development

### Running Python API in Development Mode

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing API Endpoints

Using curl:
```bash
# Test analytics endpoint
curl http://localhost:8000/api/data/analytics

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Test settings endpoint
curl -X POST http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"displayName": "Test", "email": "test@example.com", "theme": "dark", "notifications": true, "language": "en", "timezone": "UTC"}'
```

### WebSocket Testing

Use a WebSocket client or browser console:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/analytics');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

*Note: WebSocket support is required for real-time updates. All modern browsers support WebSocket.*

## Performance

- **WebSocket Connections**: 6 concurrent connections (one per card topic)
- **Data Update Interval**: 5 seconds (configurable)
- **Chat Context**: Maintains last 20 messages
- **Automatic Reconnection**: WebSocket auto-reconnects on disconnect

## Security Notes

- Default credentials (`admin`/`admin`) are for **development only**
- Session secret should be changed in production (`server.js`)
- Implement proper authentication and authorization for production use
- Enable HTTPS in production
- Validate and sanitize all user inputs
- Implement rate limiting for API endpoints

## License

ISC

## Contributing

Feel free to submit issues and enhancement requests!

## Credits

- Built with FastAPI, Express.js, and modern web technologies
- AI powered by Ollama
- Charts generated with Matplotlib
- UI styled with custom CSS
