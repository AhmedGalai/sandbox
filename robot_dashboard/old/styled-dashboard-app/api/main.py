"""
FastAPI Dashboard Data Publisher
Publishes dashboard data to frontend via WebSocket and REST endpoints
Integrates Ollama for AI chat and handles settings management
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
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

app = FastAPI(title="Dashboard Data Publisher API")

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
OLLAMA_MODEL = "qwen2.5:latest"

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

class Settings(BaseModel):
    displayName: str
    email: str
    theme: str
    notifications: bool
    language: str
    timezone: str

# Data generation functions
def generate_analytics_data():
    """Generate analytics table data"""
    metrics = ["Visitors", "Page Views", "Bounce Rate", "Avg. Session"]
    data = []
    for metric in metrics:
        if "Rate" in metric:
            value = f"{random.randint(20, 50)}%"
            change = f"{random.randint(-10, 10)}%"
        elif "Session" in metric:
            value = f"{random.randint(2, 5)}m {random.randint(10, 59)}s"
            change = f"{random.randint(-5, 15)}%"
        else:
            value = f"{random.randint(5000, 50000):,}"
            change = f"{random.randint(-10, 25)}%"

        data.append({
            "metric": metric,
            "value": value,
            "change": change
        })

    return {
        "type": "table",
        "title": "Website Analytics",
        "columns": ["Metric", "Value", "Change"],
        "rows": [[d["metric"], d["value"], d["change"]] for d in data]
    }

def generate_user_stats():
    """Generate user statistics"""
    total = random.randint(10000, 15000)
    active = int(total * random.uniform(0.75, 0.85))
    growth = random.randint(10, 25)

    return {
        "type": "stats",
        "title": "User Statistics",
        "data": {
            "total_users": f"{total:,}",
            "active_users": f"{active:,}",
            "growth_rate": f"{growth}% MoM"
        }
    }

def generate_revenue_data():
    """Generate revenue table data"""
    periods = ["This Month", "Last Month", "Quarter"]
    data = []

    for period in periods:
        target = random.randint(80000, 150000)
        actual = random.randint(int(target * 0.85), int(target * 1.15))
        status = "✓ On Track" if actual >= target * 0.95 else "⚠ Behind"

        data.append({
            "period": period,
            "target": f"${target:,}",
            "actual": f"${actual:,}",
            "status": status
        })

    return {
        "type": "table",
        "title": "Revenue Overview",
        "columns": ["Period", "Target", "Actual", "Status"],
        "rows": [[d["period"], d["target"], d["actual"], d["status"]] for d in data]
    }

def generate_tasks_data():
    """Generate task list data"""
    task_templates = [
        "Review quarterly reports",
        "Update documentation",
        "Client meeting preparation",
        "Code review for PR #",
        "System maintenance check",
        "Team sync meeting",
        "Deploy to production",
        "Security audit review"
    ]

    num_tasks = random.randint(4, 6)
    tasks = random.sample(task_templates, num_tasks)
    completed = random.randint(1, num_tasks - 1)

    task_list = []
    for i, task in enumerate(tasks):
        task_list.append({
            "task": task + str(random.randint(100, 999)) if "#" in task else task,
            "completed": i < completed
        })

    return {
        "type": "tasks",
        "title": "Daily Tasks",
        "data": {
            "tasks": task_list,
            "completed": completed,
            "total": num_tasks
        }
    }

def generate_performance_data():
    """Generate system performance metrics"""
    return {
        "type": "metrics",
        "title": "System Performance",
        "data": {
            "cpu_usage": f"{random.randint(30, 80)}%",
            "memory": f"{random.uniform(2.0, 6.5):.1f}GB / 8GB",
            "disk_io": f"{random.randint(50, 200)} MB/s",
            "network": f"{random.randint(20, 100)} Mbps",
            "status": "Operational"
        }
    }

def generate_activity_log():
    """Generate activity log entries"""
    activities = [
        "New user registration: user{}@example.com",
        "Order #ORD-{} placed (${})",
        "Server {} restarted successfully",
        "Backup completed: {} GB",
        "Payment processed: Invoice #INV-{}",
        "User {} logged in from {}",
        "API rate limit reached for client {}",
        "Database optimization completed"
    ]

    log_entries = []
    for _ in range(random.randint(4, 7)):
        activity_template = random.choice(activities)

        if "{}" in activity_template:
            placeholders = activity_template.count("{}")
            if "user" in activity_template and "@" in activity_template:
                activity = activity_template.format(random.randint(1000, 9999))
            elif "Order" in activity_template:
                activity = activity_template.format(
                    random.randint(10000, 99999),
                    random.randint(50, 500)
                )
            elif "Server" in activity_template:
                activity = activity_template.format(f"srv-{random.randint(1, 5)}")
            elif "Backup" in activity_template:
                activity = activity_template.format(random.randint(10, 100))
            elif "Invoice" in activity_template or "client" in activity_template:
                activity = activity_template.format(random.randint(1000, 9999))
            elif "logged in" in activity_template:
                cities = ["New York", "London", "Tokyo", "Paris", "Sydney"]
                activity = activity_template.format(
                    f"user{random.randint(100, 999)}",
                    random.choice(cities)
                )
            else:
                activity = activity_template
        else:
            activity = activity_template

        log_entries.append(activity)

    return {
        "type": "log",
        "title": "Recent Activity",
        "data": {
            "entries": log_entries,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

def generate_chart_image(chart_type: str = "line"):
    """Generate chart image and return as base64"""
    plt.figure(figsize=(8, 5))

    if chart_type == "line":
        x = np.linspace(0, 10, 50)
        y = np.sin(x) * np.exp(-x/10) * 50 + 50 + np.random.normal(0, 2, 50)
        plt.plot(x, y, linewidth=2, color='#667eea')
        plt.fill_between(x, y, alpha=0.3, color='#667eea')
        plt.title("Performance Trend")
        plt.xlabel("Time (hours)")
        plt.ylabel("Response Time (ms)")
        plt.grid(True, alpha=0.3)

    elif chart_type == "bar":
        categories = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        values = [random.randint(50, 100) for _ in categories]
        plt.bar(categories, values, color='#764ba2')
        plt.title("Daily Activity")
        plt.xlabel("Day")
        plt.ylabel("Events")
        plt.grid(True, alpha=0.3, axis='y')

    elif chart_type == "pie":
        labels = ['Desktop', 'Mobile', 'Tablet', 'Other']
        sizes = [45, 35, 15, 5]
        colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe']
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title("Traffic Sources")

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
        "message": "Dashboard Data Publisher API",
        "version": "1.0.0",
        "endpoints": {
            "websocket": "/ws/{topic}",
            "analytics": "/api/data/analytics",
            "users": "/api/data/users",
            "revenue": "/api/data/revenue",
            "tasks": "/api/data/tasks",
            "performance": "/api/data/performance",
            "activity": "/api/data/activity",
            "chart": "/api/data/chart/{type}",
            "chat": "/api/chat",
            "settings": "/api/settings"
        }
    }

@app.get("/api/data/analytics")
async def get_analytics():
    """Get analytics table data"""
    return generate_analytics_data()

@app.get("/api/data/users")
async def get_users():
    """Get user statistics"""
    return generate_user_stats()

@app.get("/api/data/revenue")
async def get_revenue():
    """Get revenue data"""
    return generate_revenue_data()

@app.get("/api/data/tasks")
async def get_tasks():
    """Get tasks data"""
    return generate_tasks_data()

@app.get("/api/data/performance")
async def get_performance():
    """Get performance metrics"""
    return generate_performance_data()

@app.get("/api/data/activity")
async def get_activity():
    """Get activity log"""
    return generate_activity_log()

@app.get("/api/data/chart/{chart_type}")
async def get_chart(chart_type: str):
    """Generate and return chart image as base64"""
    if chart_type not in ["line", "bar", "pie"]:
        raise HTTPException(status_code=400, detail="Invalid chart type")

    return {
        "type": "chart",
        "chart_type": chart_type,
        "image": generate_chart_image(chart_type)
    }

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Chat endpoint using Ollama"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "messages": message.context + [{"role": "user", "content": message.message}],
                "stream": False
            }

            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "response": result["message"]["content"],
                    "model": OLLAMA_MODEL,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Fallback response if Ollama is not available
                return {
                    "response": "I'm currently unable to connect to the AI service. Please make sure Ollama is running with the qwen2.5:latest model installed.",
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

@app.post("/api/settings")
async def save_settings(settings: Settings):
    """Save user settings"""
    # In production, save to database
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
            # Wait for client messages (optional, for ping/pong)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                # Echo back or handle client messages if needed
            except asyncio.TimeoutError:
                pass

            # Keep connection alive
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        manager.disconnect(websocket, topic)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, topic)

# Background task to publish data periodically
async def publish_data_periodically():
    """Background task to publish data to WebSocket subscribers"""
    while True:
        await asyncio.sleep(5)  # Publish every 5 seconds

        # Publish to different topics
        await manager.broadcast("analytics", generate_analytics_data())
        await manager.broadcast("users", generate_user_stats())
        await manager.broadcast("revenue", generate_revenue_data())
        await manager.broadcast("tasks", generate_tasks_data())
        await manager.broadcast("performance", generate_performance_data())
        await manager.broadcast("activity", generate_activity_log())

@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    asyncio.create_task(publish_data_periodically())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
