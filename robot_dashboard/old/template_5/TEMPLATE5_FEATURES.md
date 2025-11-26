# Template 5 - Advanced Task Management System

## All Changes from Template 4

### 1. Fixed Card Drag and Drop
- Cards now properly reorder when dragged
- Improved drag event handling
- Visual feedback during drag operations
- Cards can be dragged anywhere (not just by header)

### 2. Navigation Restructure
**Before:**
- Dashboard (business management)
- Simulator (main view)
- Settings

**After:**
- Dashboard (unified main view)
- Settings (simplified)

### 3. Dashboard Tab Changes
- **Merged** old dashboard inputs into main dashboard
- Business Name and Robot Selection now at top
- Side-by-side layout for inputs
- Card visibility dropdown below inputs
- All simulator content in one place

### 4. Simplified Settings
**Old Settings:**
- Display Name
- Email
- Theme selector
- Notifications
- Language
- Timezone

**New Settings:**
- ☑️ Enable Simulator (checkbox only, default ON)

### 5. Enhanced Task Control Card
**Replaced buttons with dropdown system:**

**POI Dropdown:**
- Point A
- Point B
- Point C
- Charging Station
- **Standby Point** (NEW)

**Action Dropdown:**
- Go to Point
- **Lift** (with Up/Down radio buttons)
- **Wait** (with 1-30 second slider)

**Buttons:**
- Execute Task (runs selected action)
- Go Back to Standby (dedicated button, gray style)

### 6. NEW: Task Builder Card 🔧
**Multi-step task creation system**

**Task Steps List:**
- Displays all added steps
- Shows step number, action, POI, and parameters
- Remove individual steps with ✕ button
- Scrollable list (max 300px height)

**Add Step Section:**
- POI dropdown
- Action dropdown
- Lift parameters (Up/Down radio)
- Wait parameters (seconds slider)
- Add Step button

**Control Buttons:**
- **Clear All**: Remove all steps
- **Execute Task**: Run the multi-step sequence
- **Save Task**: Export to JSON file
- **Load Task**: Import from JSON file

**Features:**
- Build complex multi-step tasks
- Save/load tasks as JSON
- Execute tasks sequentially
- Visual feedback during execution
- Step-by-step progress display

### 7. Standby Point
- New blue cell on map (1, 1)
- Labeled with "S"
- Serves as default return position
- Integrated into all POI dropdowns

### 8. Task JSON Format
```json
{
  "name": "Task_2025-01-25T10-30-00",
  "steps": [
    {
      "poi": "A",
      "action": "go"
    },
    {
      "poi": "A",
      "action": "lift",
      "direction": "up"
    },
    {
      "poi": "B",
      "action": "go"
    },
    {
      "poi": "B",
      "action": "lift",
      "direction": "down"
    },
    {
      "poi": "STANDBY",
      "action": "go"
    },
    {
      "poi": "STANDBY",
      "action": "wait",
      "seconds": "10"
    }
  ],
  "created": "2025-01-25T10:30:00.000Z"
}
```

## Usage Examples

### Single Task Execution
1. Select POI from dropdown (e.g., "Point A")
2. Select action (e.g., "Lift")
3. Configure parameters (e.g., "Up")
4. Click "Execute Task"

### Multi-Step Task Creation
1. Open Task Builder card
2. Select POI (e.g., "Point A")
3. Select action (e.g., "Go to Point")
4. Click "Add Step"
5. Repeat for each step
6. Click "Execute Task" to run
7. Or click "Save Task" to export

### Task Management
**Save Task:**
- Builds task with steps
- Creates JSON file
- Auto-downloads with timestamp name

**Load Task:**
- Click "Load Task" button
- Select .json file
- Steps populate in list
- Ready to execute or modify

**Execute Multi-Step:**
- Runs each step in sequence
- Shows progress (Step X/Y)
- Handles movement, lift, wait actions
- Displays completion message

### Go Back Feature
- Click "Go Back to Standby" anytime
- Robot plans path to standby point
- Returns to (1, 1) position
- Gray button for visual distinction

## Map Additions

### Standby Point (NEW)
- **Location**: (1, 1)
- **Color**: Blue (#2196F3)
- **Label**: "S"
- **Purpose**: Default return position

### All POIs
- Point A: (18, 3) - Green
- Point B: (7, 12) - Green
- Point C: (16, 16) - Green
- Charging: (2, 18) - Yellow with ⚡
- Standby: (1, 1) - Blue with S

## Technical Details

### New Functions
```javascript
toggleActionParams()          // Show/hide lift/wait params
executeTask()                  // Run single task
toggleBuilderActionParams()    // Builder param visibility
addTaskStep()                  // Add step to task list
updateTaskStepsList()          // Refresh visual list
removeTaskStep(index)          // Delete specific step
clearTaskSteps()               // Remove all steps
executeMultiStepTask()         // Run multi-step sequence
saveTask()                     // Export to JSON
loadTaskFromFile(event)        // Import from JSON
```

### Drag and Drop Fix
- Moved dragstart from header to entire card
- Added drop event handlers
- Improved afterElement detection
- Better null checking

### Card Visibility
- Now includes 'taskBuilderCard'
- 5 total cards can be shown/hidden
- Multi-select with Ctrl/Cmd

## Keyboard Shortcuts
- **Ctrl/Cmd + Click**: Multi-select in dropdowns
- **Drag**: Rearrange cards
- **File Upload**: Click "Load Task" → Select .json

## File Operations
- **Save**: Downloads as `Task_YYYY-MM-DDTHH-MM-SS.json`
- **Load**: Accepts `.json` files only
- **Format**: Standard JSON with name, steps, created date

## API Integration
All task actions can be extended to call actual robot APIs:
- Lift commands → `/api/robot/lift`
- Wait commands → Local setTimeout
- Go commands → Existing path planning

## Benefits
1. **Flexible Task Control**: Dropdown vs buttons
2. **Multi-Step Automation**: Build complex workflows
3. **Task Persistence**: Save/load capabilities
4. **Clear Interface**: Simplified, focused design
5. **Standby Management**: Dedicated return point
6. **Parameter Control**: Sliders, radios for precision
