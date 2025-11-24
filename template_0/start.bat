@echo off
REM Startup script for Styled Dashboard App (Windows)
REM Runs both Node.js and Python servers concurrently

echo.
echo Starting Styled Dashboard App...
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python first.
    pause
    exit /b 1
)

REM Check if Ollama is running
curl -s http://localhost:11434/api/tags >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Ollama is not running. Chat functionality will be limited.
    echo Start Ollama with: ollama serve
    echo.
)

REM Install Node.js dependencies if needed
if not exist "node_modules\" (
    echo Installing Node.js dependencies...
    call npm install
    echo.
)

REM Install Python dependencies if needed
python -c "import fastapi" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing Python dependencies...
    cd api
    pip install -r requirements.txt
    cd ..
    echo.
)

echo Dependencies checked
echo.
echo Starting servers...
echo   - Node.js server: http://localhost:3000
echo   - Python API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop all servers
echo.

REM Start Python API in new window
start "Python API" cmd /k "cd api && python main.py"

REM Wait a moment for Python server to start
timeout /t 2 /nobreak >nul

REM Start Node.js server in current window
npm start
