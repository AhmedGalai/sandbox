#!/bin/bash

echo "========================================="
echo "Template 7 Setup Verification"
echo "========================================="
echo ""

# Check if Ollama is running
echo "1. Checking Ollama service..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama is running"
else
    echo "   ❌ Ollama is not running"
    echo "   Start with: ollama serve"
fi

# Check for main model
echo ""
echo "2. Checking main model (qwen3:latest)..."
if ollama list | grep -q "qwen3"; then
    echo "   ✅ qwen3 model found"
else
    echo "   ❌ qwen3 model not found"
    echo "   Install with: ollama pull qwen3:latest"
fi

# Check for embedding model
echo ""
echo "3. Checking embedding model (mxbai-embed-large)..."
if ollama list | grep -q "mxbai-embed-large"; then
    echo "   ✅ mxbai-embed-large model found"
else
    echo "   ❌ mxbai-embed-large model NOT found (REQUIRED for Template 7)"
    echo "   Install with: ollama pull mxbai-embed-large:latest"
fi

# Check Node.js
echo ""
echo "4. Checking Node.js..."
if command -v node > /dev/null 2>&1; then
    NODE_VERSION=$(node --version)
    echo "   ✅ Node.js installed: $NODE_VERSION"
else
    echo "   ❌ Node.js not found"
fi

# Check Python
echo ""
echo "5. Checking Python..."
if command -v python3 > /dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ Python installed: $PYTHON_VERSION"
else
    echo "   ❌ Python not found"
fi

# Check dependencies
echo ""
echo "6. Checking npm dependencies..."
if [ -d "node_modules" ]; then
    echo "   ✅ node_modules found"
else
    echo "   ⚠️  node_modules not found"
    echo "   Run: npm install"
fi

echo ""
echo "========================================="
echo "Setup Status Summary"
echo "========================================="
echo ""
echo "Ready to start Template 7!"
echo ""
echo "Terminal 1: npm start"
echo "Terminal 2: cd api && python main.py"
echo ""
echo "Then visit: http://localhost:3000"
echo "Login: admin / admin"
echo ""
