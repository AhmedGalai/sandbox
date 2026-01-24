#!/bin/bash

# Ollama Multi-Agent System Setup Script
# This script sets up the environment and pulls required models

set -e

echo "======================================"
echo "Ollama Multi-Agent System Setup"
echo "======================================"
echo ""

# Check if Ollama is installed
echo "Checking for Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found!"
    echo "Please install Ollama from: https://ollama.ai"
    echo ""
    echo "Installation commands:"
    echo "  macOS/Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "  Windows: Download from https://ollama.ai/download"
    exit 1
fi
echo "✓ Ollama found"

# Check if Ollama is running
echo "Checking if Ollama is running..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama is not running!"
    echo "Please start Ollama:"
    echo "  Run: ollama serve"
    exit 1
fi
echo "✓ Ollama is running"

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION found"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p ~/.ollama_agents
mkdir -p logs
echo "✓ Directories created"

# Copy environment template
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
OLLAMA_HOST=http://localhost:11434
MAX_CONCURRENT_AGENTS=3
DEFAULT_MODEL=llama3.2:3b
REQUEST_TIMEOUT=120
LOG_LEVEL=INFO
EOF
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

# Pull required models
echo ""
echo "======================================"
echo "Downloading Required Models"
echo "======================================"
echo "This may take a while depending on your internet speed..."
echo ""

MODELS=("llama3.2:3b" "qwen2.5:7b" "llava:7b")

for model in "${MODELS[@]}"; do
    echo "Checking model: $model"
    if ollama list | grep -q "$model"; then
        echo "✓ $model already installed"
    else
        echo "Downloading $model..."
        ollama pull "$model"
        echo "✓ $model installed"
    fi
done

# Run tests (optional)
echo ""
echo "======================================"
echo "Running Tests (Optional)"
echo "======================================"
read -p "Would you like to run the test suite? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pytest tests/ -v
fi

echo ""
echo "======================================"
echo "Setup Complete! 🎉"
echo "======================================"
echo ""
echo "To start the system, run:"
echo "  python main.py"
echo ""
echo "For help, type /help in the CLI or read:"
echo "  - README.md - Overview and quick start"
echo "  - docs/CLI_GUIDE.md - Complete command reference"
echo "  - docs/QUICK_START_CLI.md - 5-minute tutorial"
echo ""
echo "Available agents:"
echo "  - Researcher (qwen2.5:7b) - Research and information synthesis"
echo "  - Developer (llama3.2:3b) - Code generation and technical help"
echo "  - Planner (qwen2.5:7b) - Project planning and strategy"
echo "  - Vision (llava:7b) - Image analysis and understanding"
echo ""
