"""
FastAPI Dashboard Data Publisher - Template 0
Generates data from user prompts, saves to local files, and streams to Node.js server
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
import random
from datetime import datetime
import httpx
import base64
import io
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

app = FastAPI(title="Dashboard Data Publisher API - Template 1")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen3:latest"

# Data storage configuration
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, topic: str):
        await websocket.accept()
        if topic not in self.active_connections:
            self.active_connections[topic] = []
        self.active_connections[topic].append(websocket)

    def disconnect(self, websocket: WebSocket, topic: str):
        if topic in self.active_connections:
            self.active_connections[topic].remove(websocket)

    async def broadcast(self, topic: str, message: dict):
        if topic in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[topic]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.append(connection)

            # Remove dead connections
            for conn in dead_connections:
                self.active_connections[topic].remove(conn)

manager = ConnectionManager()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    context: Optional[List[Dict[str, str]]] = []

class ModifyJsonRequest(BaseModel):
    data_id: str
    data: dict

class GenerateDataRequest(BaseModel):
    prompt: str
    display_type: str  # 'table' or 'chart'
    data_id: str  # unique identifier for the data
    chart_type: Optional[str] = 'line'  # 'line', 'bar', 'pie'

class Settings(BaseModel):
    displayName: str
    email: str
    theme: str
    notifications: bool
    language: str
    timezone: str

# Data storage functions
def save_data_to_file(data_id: str, data: dict):
    """Save generated data to local file"""
    file_path = DATA_DIR / f"{data_id}.json"
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    return file_path

def load_data_from_file(data_id: str) -> Optional[dict]:
    """Load data from local file"""
    file_path = DATA_DIR / f"{data_id}.json"
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

def list_saved_data() -> List[dict]:
    """List all saved data files"""
    files = []
    for file_path in DATA_DIR.glob("*.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                files.append({
                    "id": file_path.stem,
                    "title": data.get("title", file_path.stem),
                    "type": data.get("type", "unknown"),
                    "created": data.get("created", "unknown")
                })
        except:
            pass
    return files

# AI-powered data generation
async def generate_data_from_prompt(prompt: str, display_type: str, chart_type: str = 'line') -> dict:
    """Use Ollama to generate data based on user prompt"""

    # Create a system message to guide the AI
    if display_type == 'table':
        system_prompt = """You are a data generation assistant. Based on the user's request, generate structured table data in JSON format.

Your response MUST be ONLY valid JSON in this exact format:
{
  "title": "Title of the table",
  "columns": ["Column1", "Column2", "Column3"],
  "rows": [
    ["value1", "value2", "value3"],
    ["value4", "value5", "value6"]
  ]
}

Generate realistic data that matches the user's request. Include 5-10 rows of data."""
    else:
        system_prompt = """You are a data generation assistant. Based on the user's request, generate numerical data for charts in JSON format.

Your response MUST be ONLY valid JSON in this exact format:
{
  "title": "Title of the chart",
  "labels": ["Label1", "Label2", "Label3", "Label4", "Label5"],
  "values": [10, 25, 15, 30, 20]
}

Generate realistic numerical data that matches the user's request. Include 5-12 data points."""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }

            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result["message"]["content"]

                # Extract JSON from the response
                try:
                    # Try to parse the entire response as JSON
                    data = json.loads(ai_response)
                except json.JSONDecodeError:
                    # Try to find JSON within the response
                    import re
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group())
                    else:
                        raise ValueError("Could not extract JSON from AI response")

                # Add metadata
                data["type"] = display_type
                data["created"] = datetime.now().isoformat()
                data["prompt"] = prompt

                if display_type == 'chart':
                    data["chart_type"] = chart_type

                return data
            else:
                # Fallback: generate sample data
                return generate_fallback_data(prompt, display_type, chart_type)

    except Exception as e:
        print(f"Error generating data from AI: {e}")
        return generate_fallback_data(prompt, display_type, chart_type)

def generate_fallback_data(prompt: str, display_type: str, chart_type: str) -> dict:
    """Generate fallback data when AI is unavailable"""
    if display_type == 'table':
        return {
            "type": "table",
            "title": f"Data: {prompt[:50]}",
            "columns": ["Item", "Value", "Status"],
            "rows": [
                [f"Item {i+1}", f"{random.randint(100, 999)}", random.choice(["Active", "Pending", "Complete"])]
                for i in range(5)
            ],
            "created": datetime.now().isoformat(),
            "prompt": prompt
        }
    else:
        return {
            "type": "chart",
            "title": f"Chart: {prompt[:50]}",
            "chart_type": chart_type,
            "labels": [f"Point {i+1}" for i in range(6)],
            "values": [random.randint(10, 100) for _ in range(6)],
            "created": datetime.now().isoformat(),
            "prompt": prompt
        }

def generate_chart_from_data(data: dict) -> str:
    """Generate chart image from data and return as base64"""
    plt.figure(figsize=(8, 5))

    chart_type = data.get('chart_type', 'line')
    labels = data.get('labels', [])
    values = data.get('values', [])
    title = data.get('title', 'Chart')

    if chart_type == 'line':
        plt.plot(labels, values, marker='o', linewidth=2, color='#667eea')
        plt.fill_between(range(len(values)), values, alpha=0.3, color='#667eea')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)

    elif chart_type == 'bar':
        plt.bar(labels, values, color='#764ba2')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3, axis='y')

    elif chart_type == 'pie':
        colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b']
        plt.pie(values, labels=labels, colors=colors[:len(values)], autopct='%1.1f%%', startangle=90)

    plt.title(title)
    plt.tight_layout()

    # Save to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()

    # Encode to base64
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

# REST API endpoints
@app.get("/")
async def root():
    return {
        "message": "Dashboard Data Publisher API - Template 1",
        "version": "2.0.0",
        "endpoints": {
            "websocket": "/ws/{topic}",
            "generate_data": "/api/generate-data",
            "get_data": "/api/data/{data_id}",
            "list_data": "/api/data/list",
            "delete_data": "/api/data/{data_id}",
            "chat": "/api/chat",
            "settings": "/api/settings"
        }
    }

@app.post("/api/generate-data")
async def generate_data(request: GenerateDataRequest):
    """Generate data from user prompt and save to file"""
    try:
        # Generate data using AI
        data = await generate_data_from_prompt(
            request.prompt,
            request.display_type,
            request.chart_type
        )

        # If it's a chart, generate the image
        if request.display_type == 'chart':
            data['image'] = generate_chart_from_data(data)

        # Save to file
        file_path = save_data_to_file(request.data_id, data)

        # Broadcast to WebSocket subscribers
        await manager.broadcast(request.data_id, data)

        return {
            "success": True,
            "message": "Data generated and saved successfully",
            "data_id": request.data_id,
            "file_path": str(file_path),
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate data: {str(e)}")

@app.get("/api/data/{data_id}")
async def get_data(data_id: str):
    """Get data from local file"""
    data = load_data_from_file(data_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Data not found")

    # If it's a chart and doesn't have an image, generate it
    if data.get('type') == 'chart' and 'image' not in data:
        data['image'] = generate_chart_from_data(data)

    return data

@app.get("/api/data/list")
async def list_data():
    """List all saved data"""
    return {
        "data": list_saved_data()
    }

@app.delete("/api/data/{data_id}")
async def delete_data(data_id: str):
    """Delete saved data"""
    file_path = DATA_DIR / f"{data_id}.json"
    if file_path.exists():
        file_path.unlink()
        return {
            "success": True,
            "message": f"Data {data_id} deleted successfully"
        }
    raise HTTPException(status_code=404, detail="Data not found")

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Chat endpoint using Ollama with tool support"""
    try:
        # System message with tool instructions
        system_message = {
            "role": "system",
            "content": """You are a helpful AI assistant that can create and manage data visualizations. You have access to the following tools:

1. create_data_card: Create a new data card (table or chart)
   - Parameters: title (string), type (string: "table" or "chart"), data (object), topic (string, optional)
   - For tables: data should have {columns: [...], rows: [[...], ...]}
   - For charts: data should have {chart_type: "line/bar/pie", labels: [...], values: [...]}
   - Available topics: Sales, Marketing, Finance, Operations, HR, or custom topic

2. modify_json_file: Modify an existing JSON data file
   - Parameters: data_id (string), updates (object)

When a user asks you to create data or visualizations, use these tools by responding with a JSON object in this format:
{"tool": "tool_name", "parameters": {...}}

After using a tool, provide a friendly response to the user explaining what you did."""
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "messages": [system_message] + message.context + [{"role": "user", "content": message.message}],
                "stream": False
            }

            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result["message"]["content"]

                # Check if the response contains a tool call
                tool_result = None
                try:
                    # Try to find JSON tool call in the response
                    import re
                    json_match = re.search(r'\{[^{}]*"tool"[^{}]*\}', ai_response)
                    if json_match:
                        tool_call = json.loads(json_match.group())
                        if tool_call.get("tool") == "create_data_card":
                            tool_result = await handle_create_data_card(tool_call["parameters"])
                        elif tool_call.get("tool") == "modify_json_file":
                            tool_result = await handle_modify_json(tool_call["parameters"])
                except:
                    pass

                return {
                    "response": ai_response,
                    "model": OLLAMA_MODEL,
                    "timestamp": datetime.now().isoformat(),
                    "tool_result": tool_result
                }
            else:
                return {
                    "response": "I'm currently unable to connect to the AI service. Please make sure Ollama is running with the qwen3:latest model installed.",
                    "model": "fallback",
                    "timestamp": datetime.now().isoformat(),
                    "error": f"Ollama returned status code {response.status_code}"
                }

    except httpx.ConnectError:
        return {
            "response": "AI service is not available. Please ensure Ollama is running on http://localhost:11434",
            "model": "fallback",
            "timestamp": datetime.now().isoformat(),
            "error": "Connection to Ollama failed"
        }
    except Exception as e:
        return {
            "response": f"An error occurred: {str(e)}",
            "model": "fallback",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

async def handle_create_data_card(params: dict):
    """Handle the create_data_card tool call"""
    try:
        data_id = 'data_' + str(int(datetime.now().timestamp() * 1000))

        card_data = {
            "title": params.get("title", "Generated Data"),
            "type": params.get("type", "table"),
            "topic": params.get("topic", "General"),
            "created": datetime.now().isoformat()
        }

        if params.get("type") == "table":
            card_data["columns"] = params["data"].get("columns", [])
            card_data["rows"] = params["data"].get("rows", [])
        elif params.get("type") == "chart":
            card_data["chart_type"] = params["data"].get("chart_type", "line")
            card_data["labels"] = params["data"].get("labels", [])
            card_data["values"] = params["data"].get("values", [])
            card_data["image"] = generate_chart_from_data(card_data)

        # Save to file
        save_data_to_file(data_id, card_data)

        return {
            "success": True,
            "data_id": data_id,
            "data": card_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def handle_modify_json(params: dict):
    """Handle the modify_json_file tool call"""
    try:
        data_id = params.get("data_id")
        updates = params.get("updates", {})

        # Load existing data
        existing_data = load_data_from_file(data_id)
        if not existing_data:
            return {
                "success": False,
                "error": "Data file not found"
            }

        # Apply updates
        existing_data.update(updates)

        # Regenerate chart if it's a chart type
        if existing_data.get("type") == "chart":
            existing_data["image"] = generate_chart_from_data(existing_data)

        # Save back
        save_data_to_file(data_id, existing_data)

        return {
            "success": True,
            "data_id": data_id,
            "data": existing_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/modify-json")
async def modify_json(request: ModifyJsonRequest):
    """Direct endpoint to modify JSON files"""
    result = await handle_modify_json({
        "data_id": request.data_id,
        "updates": request.data
    })
    return result

@app.post("/api/settings")
async def save_settings(settings: Settings):
    """Save user settings"""
    print(f"Settings saved: {settings.dict()}")

    return {
        "success": True,
        "message": "Settings saved successfully",
        "settings": settings.dict(),
        "timestamp": datetime.now().isoformat()
    }

# WebSocket endpoints
@app.websocket("/ws/{topic}")
async def websocket_endpoint(websocket: WebSocket, topic: str):
    """WebSocket endpoint for real-time data streaming"""
    await manager.connect(websocket, topic)

    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
            except asyncio.TimeoutError:
                pass

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        manager.disconnect(websocket, topic)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, topic)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
