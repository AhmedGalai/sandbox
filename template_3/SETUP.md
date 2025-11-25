# Template 2 - Robot Simulator Dashboard

## Setup Instructions

### 1. Logo Setup
Copy your logo file to the correct location:
```bash
cp "C:\Users\Ahmed\Desktop\ef\Logo 1.jpg" template_2/public/images/logo.jpg
```

Or from WSL:
```bash
cp "/mnt/c/Users/Ahmed/Desktop/ef/Logo 1.jpg" template_2/public/images/logo.jpg
```

### 2. Install Dependencies
```bash
cd template_2
npm install
```

### 3. Start the Application

**Start both servers:**
```bash
# On Windows
start.bat

# On Linux/Mac
./start.sh
```

**Or start them separately:**

Terminal 1 - Node.js server:
```bash
node server.js
```

Terminal 2 - Python API:
```bash
cd api
python main.py
```

### 4. Access the Application
Open your browser to: http://localhost:3000

Default login: admin/admin

## Features

- **Robot Simulator Map**: 2D grid-based visualization showing:
  - Robot position and heading (red circle with white arrow)
  - Obstacles/borders (gray cells)
  - Work points with labels (green cells: A, B, C)
  - Grid lines for navigation
  - White empty tiles

- **Robot Control**: Send tasks to the robot via the chatbot
- **Real-time Updates**: Map polls robot pose every 500ms
- **Accent Colors**: Pink (#F51A61) to dark gray (#282226) gradient

## API Endpoints

### Robot Endpoints
- `GET /api/robot/pose` - Get current robot position and heading
- `POST /api/robot/pose` - Update robot pose (for testing)
- `POST /api/robot/task` - Send task command to robot

### Robot Pose Format
```json
{
  "x": 5,
  "y": 5,
  "heading": 0
}
```

Where:
- `x`, `y`: Grid coordinates (0-19)
- `heading`: Angle in degrees (0 = right, 90 = up, 180 = left, 270 = down)
