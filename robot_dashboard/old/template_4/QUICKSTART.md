# Quick Start Guide

Get your dashboard up and running in 5 minutes!

## Prerequisites

Before you begin, make sure you have:

1. **Node.js** (v14+) - [Download here](https://nodejs.org/)
2. **Python** (v3.8+) - [Download here](https://www.python.org/)
3. **Ollama** (for AI chat) - [Download here](https://ollama.ai/)

## Installation

### Step 1: Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
cd api
pip install -r requirements.txt
cd ..
```

### Step 2: Setup Ollama (AI Chat)

```bash
# Pull the AI model
ollama pull qwen2.5:latest

# Start Ollama (in a separate terminal)
ollama serve
```

## Running the App

### Option 1: Use Startup Script (Recommended)

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

### Option 2: Manual Start

**Terminal 1 - Python API:**
```bash
cd api
python main.py
```

**Terminal 2 - Node.js Server:**
```bash
npm start
```

## Access the App

1. Open your browser to: **http://localhost:3000**
2. Login with:
   - Username: `admin`
   - Password: `admin`

## What You'll See

- **Dashboard** with 6 real-time updating cards
- **AI Chatbot** in the sidebar (powered by Ollama)
- **Settings** page for customization
- **Live data** updating every 5 seconds via WebSocket

## API Documentation

View the interactive API docs at: **http://localhost:8000/docs**

## Troubleshooting

### Python API won't start
- Make sure port 8000 is not in use
- Check that all dependencies are installed: `pip install -r api/requirements.txt`

### Chat not working
- Ensure Ollama is running: `ollama serve`
- Verify the model is installed: `ollama list`
- The model should show: `qwen2.5:latest`

### WebSocket connection fails
- Make sure the Python API is running on port 8000
- Check browser console for errors
- The app will automatically fall back to polling mode

### Data not updating
- Verify both servers are running
- Check browser console (F12) for errors
- Check terminal for server errors

## Quick Commands

```bash
# Test Python API
curl http://localhost:8000/

# Test analytics endpoint
curl http://localhost:8000/api/data/analytics

# Test chat (if Ollama is running)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Next Steps

- Explore the [README.md](README.md) for detailed documentation
- Customize cards by editing `public/js/app.js`
- Add new data endpoints in `api/main.py`
- Modify styling in `public/css/style.css`

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- Look at the troubleshooting section above
- Review the API docs at http://localhost:8000/docs

Happy dashboarding! 🚀
