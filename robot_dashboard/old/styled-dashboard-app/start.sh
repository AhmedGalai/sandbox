#!/bin/bash

# Startup script for Styled Dashboard App
# Runs both Node.js and Python servers concurrently

echo "🚀 Starting Styled Dashboard App..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Warning: Ollama is not running. Chat functionality will be limited."
    echo "   Start Ollama with: ollama serve"
    echo ""
fi

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
    echo ""
fi

# Install Python dependencies if needed
if ! python3 -c "import fastapi" 2> /dev/null; then
    echo "📦 Installing Python dependencies..."
    cd api
    pip install -r requirements.txt
    cd ..
    echo ""
fi

echo "✅ Dependencies checked"
echo ""
echo "🌐 Starting servers..."
echo "   - Node.js server: http://localhost:3000"
echo "   - Python API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill 0
}

trap cleanup EXIT

# Start Python API in background
cd api
python3 main.py &
PYTHON_PID=$!
cd ..

# Wait a moment for Python server to start
sleep 2

# Start Node.js server in background
npm start &
NODE_PID=$!

# Wait for both processes
wait $PYTHON_PID $NODE_PID
