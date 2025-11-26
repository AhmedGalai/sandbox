# Template 4 - Multi-Robot Fleet Management

## New Features in Template 4

### 1. Improved Dark Mode Colors
**Easier on the eyes with softer tones:**
- Background: `#2b2d42` (was `#1a1a2e`)
- Card Background: `#3a3d5c` (was `#16213e`)
- Accents: `#4a4d6c` (was `#0f3460`)
- Provides better contrast and reduced eye strain

### 2. Draggable Cards
- **Drag from card header** to rearrange
- Visual feedback: cursor changes to grab/grabbing
- Cards become semi-transparent while dragging
- Smooth repositioning in grid layout
- Works with all cards (Map, Robot Status, Map Status, Task Control)

### 3. Card Visibility Control
- **Multiselect dropdown** at top of Simulator page
- 100% width for easy access
- Shows all available cards:
  - Map
  - Robot Status
  - Map Status
  - Task Control
- Hold Ctrl/Cmd to select multiple
- Cards instantly show/hide based on selection

### 4. Renamed Navigation
- **Dashboard Tab**: New dedicated dashboard
- **Simulator Tab**: Replaces old "Dashboard" (main simulator view)
- **"Simulator" Card → "Map" Card**: Clearer naming

### 5. Dashboard Tab (New)
Features business-level controls:
- **Business Name Field**: "ACME Robotics Corp" (hardcoded, disabled)
- **Robot Selection Dropdown**: Multiselect for fleet
  - ROB-001 through ROB-005
  - Shows robot status (Active, Idle, Charging, Maintenance)
  - Filtered by business name (simulated)

### 6. Multi-Robot Display
**Map shows multiple robots simultaneously:**
- Each robot has unique color:
  - ROB-001: Pink (#F51A61)
  - ROB-002: Blue (#2196F3)
  - ROB-003: Green (#4CAF50)
  - ROB-004: Orange (#FF9800)
  - ROB-005: Purple (#9C27B0)
- Robot ID displayed inside circle (e.g., "001")
- Individual heading arrows for each
- Different starting positions and states

### 7. Robot Fleet Data (Placeholder)
```javascript
'ROB-001': Active at (5,5) heading 0°
'ROB-002': Idle at (12,8) heading 90°
'ROB-003': Charging at (2,18) heading 0°
'ROB-004': Active at (15,15) heading 180°
'ROB-005': Maintenance at (10,5) heading 270°
```

### 8. Enhanced Chatbot
The chatbot now properly:
- Returns detailed information when queried
- Responds to position/status questions with exact data
- Shows robot information directly in chat conversation
- Examples:
  - "where is the robot" → "Robot is at (5,5) facing 0°"
  - "give me information" → Returns full status
  - "what is the robot X position" → "X position is 5"

## Usage

### Card Management
1. **Rearrange**: Drag cards by their headers
2. **Show/Hide**: Use "Visible Cards" dropdown
3. **Select Multiple**: Hold Ctrl/Cmd while clicking

### Robot Fleet
1. Go to **Dashboard** tab
2. View business name: "ACME Robotics Corp"
3. Select robots from dropdown (multi-select)
4. Go to **Simulator** tab to see selected robots on map
5. Each robot appears with its unique color

### Multi-Robot View
- Select multiple robots in Dashboard
- Switch to Simulator tab
- Map shows all selected robots
- Each robot has:
  - Colored circle (unique per robot)
  - ID label inside circle
  - Direction arrow
  - Independent paths (when moving)

## Technical Details

### Drag and Drop
- Uses HTML5 Drag and Drop API
- Event listeners on card headers
- Grid reordering with `insertBefore()`
- Visual feedback via `.dragging` class

### Robot State Management
```javascript
robots = {
    'ROB-001': { x, y, heading, status, color, ... },
    'ROB-002': { ... },
    ...
}
selectedRobots = ['ROB-001']  // Active selections
activeRobot = 'ROB-001'       // Primary control target
```

### Card Visibility
- Controlled via `display: block/none`
- Preserves card state when hidden
- Instant toggle without reload

## Color Scheme

### Robot Colors
- ROB-001: #F51A61 (Pink)
- ROB-002: #2196F3 (Blue)
- ROB-003: #4CAF50 (Green)
- ROB-004: #FF9800 (Orange)
- ROB-005: #9C27B0 (Purple)

### Dark Mode (New)
- Background: #2b2d42
- Cards: #3a3d5c
- Accents: #4a4d6c
- Text: #eaeaea

## API Compatibility
All template_3 API endpoints still work. The chatbot endpoint now returns more detailed responses for information queries.

## Setup
Same as previous templates:
1. Copy logo to `public/images/logo.jpg`
2. Run `./start.sh` or `start.bat`
3. Access at http://localhost:3000
4. Login: admin/admin

## Keyboard Shortcuts
- **Ctrl/Cmd + Click**: Multi-select in dropdowns
- **Drag Header**: Rearrange cards
- **Enter in Chat**: Send message
