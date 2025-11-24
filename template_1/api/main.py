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
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:latest")

print(f"Ollama configured at: {OLLAMA_BASE_URL}")
print(f"Using model: {OLLAMA_MODEL}")

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
            "content": """You are a helpful AI assistant that can create and manage data visualizations. You MUST use tools when users ask you to create, generate, or modify data.

AVAILABLE TOOLS:

1. create_data_card - Use this when user asks to create/generate data, tables, or charts
   Parameters:
   - title: string (name of the data)
   - type: "table" or "chart"
   - topic: string (Sales, Marketing, Finance, Operations, HR, or custom)
   - data: object
     * For tables: {columns: ["col1", "col2"], rows: [["val1", "val2"], ...]}
     * For charts: {chart_type: "line"|"bar"|"pie", labels: [...], values: [...]}

2. modify_json_file - Use this to modify existing data
   Parameters:
   - data_id: string
   - updates: object

IMPORTANT RULES:
- When user asks to create/generate data, you MUST respond with ONLY the tool call JSON, nothing else
- Format: {"tool": "create_data_card", "parameters": {...}}
- Do NOT include conversational text with the tool call
- After the tool executes, you can explain what you did

EXAMPLES:

User: "Create a sales table for Q1 2024"
You: {"tool": "create_data_card", "parameters": {"title": "Q1 2024 Sales", "type": "table", "topic": "Sales", "data": {"columns": ["Month", "Revenue", "Units"], "rows": [["January", "$50000", "1200"], ["February", "$55000", "1350"], ["March", "$60000", "1500"]]}}}

User: "Generate a bar chart for monthly expenses"
You: {"tool": "create_data_card", "parameters": {"title": "Monthly Expenses", "type": "chart", "topic": "Finance", "data": {"chart_type": "bar", "labels": ["Jan", "Feb", "Mar", "Apr"], "values": [2500, 2800, 2600, 3000]}}}

User: "Show me marketing data"
You: {"tool": "create_data_card", "parameters": {"title": "Marketing Metrics", "type": "table", "topic": "Marketing", "data": {"columns": ["Campaign", "Clicks", "Conversions"], "rows": [["Email", "5000", "250"], ["Social", "8000", "400"], ["PPC", "3000", "180"]]}}}"""
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Add few-shot examples to help AI understand tool format
            examples = []
            if not message.context or len(message.context) == 0:
                examples = [
                    {"role": "user", "content": "Create a sales table for Q1 2024 with the Sales topic"},
                    {"role": "assistant", "content": '{"tool": "create_data_card", "parameters": {"title": "Q1 2024 Sales", "type": "table", "topic": "Sales", "data": {"columns": ["Month", "Revenue", "Units"], "rows": [["January", "$50000", "1200"], ["February", "$55000", "1350"], ["March", "$60000", "1500"]]}}}'},
                    {"role": "user", "content": "Thanks!"},
                    {"role": "assistant", "content": "You're welcome! I've created the sales table for you."}
                ]

            payload = {
                "model": OLLAMA_MODEL,
                "messages": [system_message] + examples + message.context + [{"role": "user", "content": message.message}],
                "stream": False,
                "options": {
                    "temperature": 0.1  # Lower temperature for more consistent tool formatting
                }
            }

            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result["message"]["content"]
                print(f"\n=== AI Response ===")
                print(f"Raw response: {ai_response[:500]}...")  # First 500 chars
                print(f"==================\n")

                # Check if the response contains a tool call
                tool_result = None
                user_message = ai_response

                try:
                    # Try to parse the entire response as JSON first
                    import re

                    # Remove markdown code blocks if present
                    cleaned_response = re.sub(r'```json\s*', '', ai_response)
                    cleaned_response = re.sub(r'```\s*', '', cleaned_response)
                    cleaned_response = cleaned_response.strip()

                    # First, try to parse the entire response as JSON
                    tool_call = None
                    try:
                        tool_call = json.loads(cleaned_response)
                        if not tool_call.get("tool"):
                            print("Response is JSON but doesn't have 'tool' field")
                            tool_call = None
                        else:
                            print(f"Successfully parsed tool call: {tool_call.get('tool')}")
                    except json.JSONDecodeError as je:
                        print(f"Response is not valid JSON: {je}")
                        pass

                    # If that didn't work, try to extract JSON from the response
                    if not tool_call:
                        print("Attempting to extract JSON from response...")
                        # Find JSON by counting braces to handle nested objects
                        start_idx = cleaned_response.find('{')
                        if start_idx != -1:
                            brace_count = 0
                            end_idx = start_idx
                            for i in range(start_idx, len(cleaned_response)):
                                if cleaned_response[i] == '{':
                                    brace_count += 1
                                elif cleaned_response[i] == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        end_idx = i
                                        break

                            if end_idx > start_idx:
                                tool_call_str = cleaned_response[start_idx:end_idx+1]
                                print(f"Extracted JSON: {tool_call_str[:200]}...")
                                try:
                                    tool_call = json.loads(tool_call_str)
                                    if tool_call.get("tool"):
                                        print(f"Successfully extracted tool call: {tool_call.get('tool')}")
                                    else:
                                        print("Extracted JSON but no 'tool' field found")
                                        tool_call = None
                                except Exception as parse_error:
                                    print(f"Failed to parse extracted JSON: {parse_error}")
                                    tool_call = None
                        else:
                            print("No JSON found in response")

                    if tool_call and tool_call.get("tool"):
                        print(f"\n=== Executing Tool: {tool_call.get('tool')} ===")

                        if tool_call.get("tool") == "create_data_card":
                            print(f"Parameters: {tool_call.get('parameters', {})}")
                            tool_result = await handle_create_data_card(tool_call.get("parameters", {}))
                            print(f"Tool result: {tool_result}")

                            if tool_result and tool_result.get("success"):
                                params = tool_call.get("parameters", {})
                                user_message = f"✅ I've created a new {params.get('type', 'data')} card titled '{params.get('title', 'Data')}' for the {params.get('topic', 'General')} topic. You can see it on your dashboard!"
                            else:
                                error_detail = tool_result.get('error', 'Unknown error') if tool_result else 'Tool returned None'
                                user_message = f"❌ I tried to create the data card but encountered an error: {error_detail}"
                                print(f"ERROR: {error_detail}")

                        elif tool_call.get("tool") == "modify_json_file":
                            print(f"Parameters: {tool_call.get('parameters', {})}")
                            tool_result = await handle_modify_json(tool_call.get("parameters", {}))
                            print(f"Tool result: {tool_result}")

                            if tool_result and tool_result.get("success"):
                                user_message = f"✅ I've updated the data file. The changes should be visible on your dashboard!"
                            else:
                                error_detail = tool_result.get('error', 'Unknown error') if tool_result else 'Tool returned None'
                                user_message = f"❌ I tried to modify the data but encountered an error: {error_detail}"
                                print(f"ERROR: {error_detail}")
                    else:
                        print("No valid tool call detected - passing through AI response")
                        # AI responded but didn't use a tool - just pass through the response
                        user_message = ai_response

                except Exception as e:
                    error_msg = str(e)
                    print(f"\n!!! EXCEPTION in tool parsing !!!")
                    print(f"Error: {error_msg}")
                    print(f"Full response: {ai_response}")

                    import traceback
                    traceback.print_exc()

                    # Show the actual error to help debug
                    user_message = f"I received your request but encountered an error: {error_msg}. Please check the server logs for details."

                return {
                    "response": user_message,
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
        print(f"Creating data card with params: {params}")

        data_id = 'data_' + str(int(datetime.now().timestamp() * 1000))

        card_data = {
            "title": params.get("title", "Generated Data"),
            "type": params.get("type", "table"),
            "topic": params.get("topic", "General"),
            "created": datetime.now().isoformat()
        }

        # Get data from params
        data = params.get("data", {})

        if params.get("type") == "table":
            card_data["columns"] = data.get("columns", [])
            card_data["rows"] = data.get("rows", [])
            print(f"Created table with {len(card_data['columns'])} columns and {len(card_data['rows'])} rows")

        elif params.get("type") == "chart":
            card_data["chart_type"] = data.get("chart_type", "line")
            card_data["labels"] = data.get("labels", [])
            card_data["values"] = data.get("values", [])
            print(f"Creating chart with {len(card_data['labels'])} data points")

            # Generate chart image
            try:
                card_data["image"] = generate_chart_from_data(card_data)
                print("Chart image generated successfully")
            except Exception as chart_error:
                print(f"Error generating chart: {chart_error}")
                return {
                    "success": False,
                    "error": f"Failed to generate chart: {str(chart_error)}"
                }

        # Save to file
        file_path = save_data_to_file(data_id, card_data)
        print(f"Data saved to: {file_path}")

        # Broadcast to WebSocket subscribers
        await manager.broadcast(data_id, card_data)

        return {
            "success": True,
            "data_id": data_id,
            "data": card_data
        }
    except Exception as e:
        print(f"Error in handle_create_data_card: {e}")
        import traceback
        traceback.print_exc()
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
