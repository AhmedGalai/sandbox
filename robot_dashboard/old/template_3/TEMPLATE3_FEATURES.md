# Template 3 - Advanced Robot Simulator

## New Features in Template 3

### 1. Robot Status Card (Topic: rob_status)
- **Position X & Y**: Current robot coordinates
- **Heading**: Direction the robot is facing (0-360°)
- **Current Task**: Active task being executed
- **Status**: Robot state (Ready, Moving, Planning, etc.)
- **Nearest Label**: Closest work point or charging station
- **Distance to Target**: Real-time distance calculation
- **Errors**: Any errors encountered during operation
- **Polling**: Updates every 500ms automatically

### 2. Map Status Card (Topic: map_status)
- **Grid Size**: Map dimensions (20x20)
- **Work Points**: List of all work points with coordinates (A, B, C)
- **Charging Points**: Charging station location
- **Obstacles**: Total number of obstacle cells
- **Free Cells**: Available navigation space

### 3. Task Control Card (Topic: task_control)
- **Manual Point Selection**: Direct buttons to send robot to:
  - Point A (18, 3)
  - Point B (7, 12)
  - Point C (16, 16)
  - Charging Station (2, 18)
- **Status Feedback**: Real-time task execution status

### 4. Path Planning & Navigation
- **A* Algorithm**: Optimal pathfinding around obstacles
- **Iterative Movement**: Robot moves step-by-step along calculated path
- **Path Visualization**: Pink dashed line shows planned route
- **Speed**: 200ms per cell movement
- **Collision Avoidance**: Automatic obstacle detection

### 5. Enhanced Map
- **Increased Obstacle Density**: ~50 obstacle cells including:
  - Partial walls (top, left, right, bottom sections)
  - Interior obstacles forming barriers
  - Scattered obstacles throughout map
- **Charging Point**: Yellow cell with ⚡ symbol at (2, 18)
- **Visual Path**: Route displayed before robot moves

### 6. Intelligent Chatbot
- **Query Detection**: Recognizes status/position questions
- **Information Responses**: Prints robot data directly in chat:
  - "where are you" → "At (5,5) facing 0°"
  - "status" → "Position (5,5), heading 0°, nearest A"
  - "what's your pose" → Returns full status
- **Movement Commands**: Understands natural language:
  - "go to A" → Plans path and executes
  - "move to charging" → Navigates to charging point
  - "take me to B" → Moves to point B
- **Concise Responses**: Limited to under 20 words
- **Context Awareness**: Maintains conversation history

### 7. Real-time Updates
- **Pose Polling**: Every 500ms
- **Status Polling**: Every 500ms
- **Server Sync**: Position updates sent to backend
- **Map Redraw**: Updates during movement

## API Endpoints

### New Endpoints
```
GET  /api/robot/status    - Get comprehensive robot status
POST /api/robot/task      - Send task with movement/query handling
GET  /api/robot/pose      - Get current pose
POST /api/robot/pose      - Update pose
```

### Status Response Format
```json
{
  "x": 5,
  "y": 5,
  "heading": 0,
  "current_task": "Idle",
  "status": "Ready",
  "errors": "None",
  "nearest_label": "A",
  "distance_to_target": "N/A"
}
```

### Task Response Format
```json
{
  "success": true,
  "response": "Moving to A",
  "pose": {...},
  "target_point": "A",
  "timestamp": "2025-01-..."
}
```

## Usage Examples

### Chatbot Commands
```
"go to A"           → Robot plans path and moves to point A
"move to charging"  → Robot navigates to charging station
"where are you"     → "At (5,5) facing 0°"
"status"            → Full status in chat
"what's nearest"    → AI responds with nearest point
```

### Task Control Buttons
- Click "Go to Point A/B/C" for immediate navigation
- Click "Go to Charging" to return to charge station
- Status updates appear below buttons

## Technical Details

### Path Planning
- Algorithm: A* with Manhattan distance heuristic
- Grid: 4-directional movement (up, down, left, right)
- Optimization: Open set sorted by f-score
- Handling: Graceful failure if no path exists

### Movement System
- Interval: 200ms per step
- Heading: Calculated dynamically toward next cell
- Visualization: Robot arrow updates each step
- Cleanup: Intervals cleared on completion

### Obstacle Layout
Total obstacles: ~50 cells strategically placed to create challenging navigation scenarios while maintaining multiple valid paths.

## Setup

Same as template_2:
1. Copy logo to `public/images/logo.jpg`
2. Run `./start.sh` or `start.bat`
3. Access at http://localhost:3000
4. Login: admin/admin

## Color Scheme
- Accent: #F51A61 (pink) → #282226 (dark gray)
- Work Points: #4CAF50 (green)
- Charging: #FFC107 (yellow)
- Obstacles: #888 (gray)
- Robot: #F51A61 (pink/red)
- Path: #F51A61 dashed
