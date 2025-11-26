// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';

// Global state
let generatedCards = [];
let websockets = {};
let chatContext = [];
let availableTopics = ['simulator'];
let cardsByTopic = {};

// Robot simulator state
let robotState = {
    x: 5,
    y: 5,
    heading: 0, // degrees, 0 = right, 90 = up, 180 = left, 270 = down
    gridSize: 20,
    cellSize: 30,
    currentTask: 'Idle',
    status: 'Ready',
    errors: 'None',
    targetPoint: null,
    path: [],
    pathIndex: 0,
    isMoving: false
};

// Map obstacles (gray cells) - increased density
let obstacles = [
    // Top wall
    {x: 0, y: 0}, {x: 1, y: 0}, {x: 2, y: 0}, {x: 3, y: 0}, {x: 4, y: 0},
    // Left wall
    {x: 0, y: 1}, {x: 0, y: 2}, {x: 0, y: 3}, {x: 0, y: 4},
    // Right wall section
    {x: 19, y: 5}, {x: 19, y: 6}, {x: 19, y: 7}, {x: 19, y: 8},
    // Bottom wall section
    {x: 15, y: 19}, {x: 16, y: 19}, {x: 17, y: 19}, {x: 18, y: 19}, {x: 19, y: 19},
    // Interior obstacles
    {x: 10, y: 10}, {x: 11, y: 10}, {x: 12, y: 10}, {x: 13, y: 10},
    {x: 10, y: 11}, {x: 13, y: 11},
    {x: 10, y: 12}, {x: 11, y: 12}, {x: 12, y: 12}, {x: 13, y: 12},
    {x: 15, y: 5}, {x: 15, y: 6}, {x: 15, y: 7}, {x: 16, y: 6},
    {x: 3, y: 15}, {x: 4, y: 15}, {x: 5, y: 15}, {x: 6, y: 15},
    {x: 4, y: 16}, {x: 5, y: 16},
    // More scattered obstacles
    {x: 8, y: 5}, {x: 9, y: 5},
    {x: 18, y: 10}, {x: 18, y: 11},
    {x: 6, y: 8}, {x: 7, y: 8}
];

// Work points (green cells with labels)
let workPoints = [
    {x: 18, y: 3, label: 'A'},
    {x: 7, y: 12, label: 'B'},
    {x: 16, y: 16, label: 'C'}
];

// Charging point (yellow)
let chargingPoint = {x: 2, y: 18, label: 'CHARGE'};

// Polling intervals
let posePollingInterval = null;
let statusPollingInterval = null;
let movementInterval = null;

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    loadThemePreference();
    checkAuthentication();
    initializeEventListeners();
    initializeSimulator();
});

// Initialize simulator
function initializeSimulator() {
    drawRobotMap();
    startPosePolling();
    startStatusPolling();
    updateMapStatus();
}

// Draw the robot map
function drawRobotMap() {
    const canvas = document.getElementById('robotCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const gridSize = robotState.gridSize;
    const cellSize = robotState.cellSize;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 1;

    for (let i = 0; i <= gridSize; i++) {
        // Vertical lines
        ctx.beginPath();
        ctx.moveTo(i * cellSize, 0);
        ctx.lineTo(i * cellSize, gridSize * cellSize);
        ctx.stroke();

        // Horizontal lines
        ctx.beginPath();
        ctx.moveTo(0, i * cellSize);
        ctx.lineTo(gridSize * cellSize, i * cellSize);
        ctx.stroke();
    }

    // Fill empty tiles (white - already default)

    // Draw obstacles (gray)
    ctx.fillStyle = '#888';
    obstacles.forEach(obs => {
        ctx.fillRect(obs.x * cellSize, obs.y * cellSize, cellSize, cellSize);
    });

    // Draw work points (green)
    ctx.fillStyle = '#4CAF50';
    workPoints.forEach(wp => {
        ctx.fillRect(wp.x * cellSize, wp.y * cellSize, cellSize, cellSize);

        // Draw label
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(wp.label, wp.x * cellSize + cellSize / 2, wp.y * cellSize + cellSize / 2);
        ctx.fillStyle = '#4CAF50';
    });

    // Draw charging point (yellow)
    ctx.fillStyle = '#FFC107';
    ctx.fillRect(chargingPoint.x * cellSize, chargingPoint.y * cellSize, cellSize, cellSize);
    ctx.fillStyle = '#333';
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('⚡', chargingPoint.x * cellSize + cellSize / 2, chargingPoint.y * cellSize + cellSize / 2);

    // Draw path if exists
    if (robotState.path && robotState.path.length > 0) {
        ctx.strokeStyle = '#F51A61';
        ctx.lineWidth = 3;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        robotState.path.forEach((point, index) => {
            const pathX = point.x * cellSize + cellSize / 2;
            const pathY = point.y * cellSize + cellSize / 2;
            if (index === 0) {
                ctx.moveTo(pathX, pathY);
            } else {
                ctx.lineTo(pathX, pathY);
            }
        });
        ctx.stroke();
        ctx.setLineDash([]);
    }

    // Draw robot (red circle with arrow)
    const robotX = robotState.x * cellSize + cellSize / 2;
    const robotY = robotState.y * cellSize + cellSize / 2;
    const robotRadius = cellSize * 0.4;

    // Draw robot body
    ctx.fillStyle = '#F51A61';
    ctx.beginPath();
    ctx.arc(robotX, robotY, robotRadius, 0, Math.PI * 2);
    ctx.fill();

    // Draw direction arrow
    ctx.strokeStyle = '#fff';
    ctx.fillStyle = '#fff';
    ctx.lineWidth = 3;

    const headingRad = (robotState.heading - 90) * Math.PI / 180; // Adjust for canvas coords
    const arrowLength = robotRadius;
    const arrowEndX = robotX + Math.cos(headingRad) * arrowLength;
    const arrowEndY = robotY + Math.sin(headingRad) * arrowLength;

    // Arrow line
    ctx.beginPath();
    ctx.moveTo(robotX, robotY);
    ctx.lineTo(arrowEndX, arrowEndY);
    ctx.stroke();

    // Arrow head
    const arrowHeadSize = 8;
    const angle1 = headingRad + Math.PI * 0.8;
    const angle2 = headingRad - Math.PI * 0.8;

    ctx.beginPath();
    ctx.moveTo(arrowEndX, arrowEndY);
    ctx.lineTo(arrowEndX + Math.cos(angle1) * arrowHeadSize, arrowEndY + Math.sin(angle1) * arrowHeadSize);
    ctx.lineTo(arrowEndX + Math.cos(angle2) * arrowHeadSize, arrowEndY + Math.sin(angle2) * arrowHeadSize);
    ctx.closePath();
    ctx.fill();
}

// Start polling robot pose
function startPosePolling() {
    if (posePollingInterval) {
        clearInterval(posePollingInterval);
    }

    posePollingInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/robot/pose`);
            if (response.ok) {
                const data = await response.json();
                if (data.x !== undefined && data.y !== undefined && data.heading !== undefined) {
                    robotState.x = data.x;
                    robotState.y = data.y;
                    robotState.heading = data.heading;
                    drawRobotMap();
                }
            }
        } catch (error) {
            // Silently fail - API might not be running yet
        }
    }, 500); // Poll every 500ms
}

// Stop polling
function stopPosePolling() {
    if (posePollingInterval) {
        clearInterval(posePollingInterval);
        posePollingInterval = null;
    }
}

// A* pathfinding algorithm
function findPath(start, goal) {
    const gridSize = robotState.gridSize;

    // Check if goal is valid
    if (goal.x < 0 || goal.x >= gridSize || goal.y < 0 || goal.y >= gridSize) {
        return null;
    }

    // Check if goal is an obstacle
    if (obstacles.some(obs => obs.x === goal.x && obs.y === goal.y)) {
        return null;
    }

    const openSet = [{x: start.x, y: start.y, g: 0, h: 0, f: 0, parent: null}];
    const closedSet = new Set();

    const heuristic = (a, b) => Math.abs(a.x - b.x) + Math.abs(a.y - b.y);

    while (openSet.length > 0) {
        // Find node with lowest f score
        openSet.sort((a, b) => a.f - b.f);
        const current = openSet.shift();

        // Check if we reached the goal
        if (current.x === goal.x && current.y === goal.y) {
            // Reconstruct path
            const path = [];
            let node = current;
            while (node) {
                path.unshift({x: node.x, y: node.y});
                node = node.parent;
            }
            return path;
        }

        closedSet.add(`${current.x},${current.y}`);

        // Check neighbors (4-directional movement)
        const neighbors = [
            {x: current.x + 1, y: current.y},
            {x: current.x - 1, y: current.y},
            {x: current.x, y: current.y + 1},
            {x: current.x, y: current.y - 1}
        ];

        for (const neighbor of neighbors) {
            // Check if neighbor is valid
            if (neighbor.x < 0 || neighbor.x >= gridSize || neighbor.y < 0 || neighbor.y >= gridSize) {
                continue;
            }

            // Check if neighbor is an obstacle
            if (obstacles.some(obs => obs.x === neighbor.x && obs.y === neighbor.y)) {
                continue;
            }

            // Check if already in closed set
            if (closedSet.has(`${neighbor.x},${neighbor.y}`)) {
                continue;
            }

            const g = current.g + 1;
            const h = heuristic(neighbor, goal);
            const f = g + h;

            // Check if neighbor is already in open set with better score
            const existingIndex = openSet.findIndex(n => n.x === neighbor.x && n.y === neighbor.y);
            if (existingIndex !== -1) {
                if (g < openSet[existingIndex].g) {
                    openSet[existingIndex].g = g;
                    openSet[existingIndex].f = f;
                    openSet[existingIndex].parent = current;
                }
            } else {
                openSet.push({
                    x: neighbor.x,
                    y: neighbor.y,
                    g: g,
                    h: h,
                    f: f,
                    parent: current
                });
            }
        }
    }

    return null; // No path found
}

// Calculate distance between two points
function calculateDistance(p1, p2) {
    return Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
}

// Find nearest label to robot
function findNearestLabel() {
    let nearest = null;
    let minDist = Infinity;

    const allPoints = [...workPoints, chargingPoint];

    for (const point of allPoints) {
        const dist = calculateDistance(robotState, point);
        if (dist < minDist) {
            minDist = dist;
            nearest = point.label;
        }
    }

    return nearest || 'None';
}

// Start status polling
function startStatusPolling() {
    if (statusPollingInterval) {
        clearInterval(statusPollingInterval);
    }

    statusPollingInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/robot/status`);
            if (response.ok) {
                const data = await response.json();
                updateRobotStatus(data);
            } else {
                // Update from local state
                updateRobotStatusLocal();
            }
        } catch (error) {
            // Update from local state
            updateRobotStatusLocal();
        }
    }, 500);
}

// Update robot status from local state
function updateRobotStatusLocal() {
    const nearest = findNearestLabel();
    const distToTarget = robotState.targetPoint ?
        calculateDistance(robotState, robotState.targetPoint).toFixed(2) : 'N/A';

    document.getElementById('status-x').textContent = robotState.x;
    document.getElementById('status-y').textContent = robotState.y;
    document.getElementById('status-heading').textContent = robotState.heading + '°';
    document.getElementById('status-task').textContent = robotState.currentTask;
    document.getElementById('status-status').textContent = robotState.status;
    document.getElementById('status-nearest').textContent = nearest;
    document.getElementById('status-distance').textContent = distToTarget;
    document.getElementById('status-errors').textContent = robotState.errors;
}

// Update robot status from server data
function updateRobotStatus(data) {
    document.getElementById('status-x').textContent = data.x || robotState.x;
    document.getElementById('status-y').textContent = data.y || robotState.y;
    document.getElementById('status-heading').textContent = (data.heading || robotState.heading) + '°';
    document.getElementById('status-task').textContent = data.current_task || robotState.currentTask;
    document.getElementById('status-status').textContent = data.status || robotState.status;
    document.getElementById('status-nearest').textContent = data.nearest_label || findNearestLabel();
    document.getElementById('status-distance').textContent = data.distance_to_target || 'N/A';
    document.getElementById('status-errors').textContent = data.errors || robotState.errors;
}

// Update map status
function updateMapStatus() {
    const totalCells = robotState.gridSize * robotState.gridSize;
    const obstacleCells = obstacles.length;
    const freeCells = totalCells - obstacleCells - workPoints.length - 1; // -1 for charging point

    document.getElementById('map-gridsize').textContent = `${robotState.gridSize} x ${robotState.gridSize}`;
    document.getElementById('map-workpoints').textContent = workPoints.map(wp => `${wp.label}(${wp.x},${wp.y})`).join(', ');
    document.getElementById('map-charging').textContent = `⚡ (${chargingPoint.x},${chargingPoint.y})`;
    document.getElementById('map-obstacles').textContent = `${obstacleCells} cells`;
    document.getElementById('map-freecells').textContent = `${freeCells} cells`;
}

// Move robot along path iteratively
function startRobotMovement(path) {
    if (movementInterval) {
        clearInterval(movementInterval);
    }

    robotState.path = path;
    robotState.pathIndex = 0;
    robotState.isMoving = true;
    robotState.status = 'Moving';

    movementInterval = setInterval(() => {
        if (robotState.pathIndex >= robotState.path.length) {
            // Reached destination
            clearInterval(movementInterval);
            movementInterval = null;
            robotState.isMoving = false;
            robotState.status = 'Ready';
            robotState.currentTask = 'Idle';
            robotState.path = [];
            robotState.targetPoint = null;
            drawRobotMap();
            updateRobotStatusLocal();
            return;
        }

        const nextPos = robotState.path[robotState.pathIndex];

        // Calculate heading to next position
        const dx = nextPos.x - robotState.x;
        const dy = nextPos.y - robotState.y;
        if (dx !== 0 || dy !== 0) {
            robotState.heading = Math.round(Math.atan2(-dy, dx) * 180 / Math.PI);
            if (robotState.heading < 0) robotState.heading += 360;
        }

        // Move to next position
        robotState.x = nextPos.x;
        robotState.y = nextPos.y;
        robotState.pathIndex++;

        // Update display
        drawRobotMap();
        updateRobotStatusLocal();

        // Send update to server
        fetch(`${API_BASE_URL}/api/robot/pose`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                x: robotState.x,
                y: robotState.y,
                heading: robotState.heading
            })
        }).catch(err => console.error('Failed to update server:', err));

    }, 200); // Move every 200ms
}

// Send robot to specific point
async function sendToPoint(pointLabel) {
    let target;

    if (pointLabel === 'CHARGE') {
        target = chargingPoint;
    } else {
        target = workPoints.find(wp => wp.label === pointLabel);
    }

    if (!target) {
        document.getElementById('taskControlStatus').textContent = 'Invalid point!';
        document.getElementById('taskControlStatus').style.color = '#dc3545';
        return;
    }

    // Find path
    const path = findPath(robotState, target);

    if (!path) {
        document.getElementById('taskControlStatus').textContent = 'No path found!';
        document.getElementById('taskControlStatus').style.color = '#dc3545';
        robotState.errors = 'Path planning failed';
        return;
    }

    // Start movement
    robotState.currentTask = `Moving to ${pointLabel}`;
    robotState.targetPoint = target;
    robotState.errors = 'None';
    document.getElementById('taskControlStatus').textContent = `Moving to ${pointLabel}...`;
    document.getElementById('taskControlStatus').style.color = '#28a745';

    startRobotMovement(path);

    // Notify server
    try {
        await fetch(`${API_BASE_URL}/api/robot/task`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                task: `go to ${pointLabel}`,
                context: []
            })
        });
    } catch (error) {
        console.error('Failed to notify server:', error);
    }
}

// Check if user is authenticated
async function checkAuthentication() {
    try {
        const response = await fetch('/api/check-auth');
        const data = await response.json();

        if (data.authenticated) {
            showMainApp();
        } else {
            showLoginModal();
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        showLoginModal();
    }
}

// Show login modal
function showLoginModal() {
    document.getElementById('loginModal').style.display = 'flex';
    document.getElementById('mainContainer').style.display = 'none';

    // Load username from session storage
    const savedUsername = sessionStorage.getItem('username');
    if (savedUsername) {
        document.getElementById('username').value = savedUsername;
    }
}

// Show main application
function showMainApp() {
    document.getElementById('loginModal').style.display = 'none';
    document.getElementById('mainContainer').style.display = 'block';
    initializeTopicFilter();
}

// Initialize all event listeners
function initializeEventListeners() {
    // Login form
    document.getElementById('loginForm').addEventListener('submit', handleLogin);

    // Navigation
    document.querySelectorAll('.navbar-item').forEach(item => {
        item.addEventListener('click', handleNavigation);
    });

    // Logout
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);

    // Chat
    document.getElementById('sendChatBtn').addEventListener('click', sendChatMessage);
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });

    // Settings form
    document.getElementById('settingsForm').addEventListener('submit', handleSettingsSave);

    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);

    // Topic filter
    const topicFilter = document.getElementById('topicFilter');
    if (topicFilter) {
        topicFilter.addEventListener('change', filterCardsByTopic);
    }
}

// Toggle chart type selector visibility
function toggleChartTypeSelector() {
    const displayType = document.getElementById('displayType').value;
    const chartTypeGroup = document.getElementById('chartTypeGroup');
    chartTypeGroup.style.display = displayType === 'chart' ? 'block' : 'none';
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('loginError');

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.success) {
            // Save username to session storage
            sessionStorage.setItem('username', username);
            showMainApp();
        } else {
            errorDiv.textContent = 'Invalid credentials. Try admin/admin';
        }
    } catch (error) {
        errorDiv.textContent = 'Login failed. Please try again.';
        console.error('Login error:', error);
    }
}

// Handle logout
async function handleLogout() {
    try {
        // Close all WebSocket connections
        Object.values(websockets).forEach(ws => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.close();
            }
        });

        // Clear session storage
        sessionStorage.removeItem('username');

        await fetch('/api/logout', { method: 'POST' });
        location.reload();
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// Handle navigation
function handleNavigation(e) {
    e.preventDefault();

    const page = e.target.dataset.page;

    // Update active nav item
    document.querySelectorAll('.navbar-item').forEach(item => {
        item.classList.remove('active');
    });
    e.target.classList.add('active');

    // Show corresponding page
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });
    document.getElementById(page + 'Page').classList.add('active');
}

// Generate data from prompt
async function generateData() {
    const prompt = document.getElementById('dataPrompt').value.trim();
    const displayType = document.getElementById('displayType').value;
    const chartType = document.getElementById('chartType').value;
    const statusDiv = document.getElementById('generateStatus');

    if (!prompt) {
        statusDiv.textContent = 'Please describe the data you want to generate';
        statusDiv.style.color = '#dc3545';
        return;
    }

    // Show loading status
    const generateBtn = document.getElementById('generateDataBtn');
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';
    statusDiv.textContent = 'Generating data, please wait...';
    statusDiv.style.color = '#667eea';

    try {
        // Generate unique ID for this data
        const dataId = 'data_' + Date.now();

        const response = await fetch(`${API_BASE_URL}/api/generate-data`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt,
                display_type: displayType,
                chart_type: chartType,
                data_id: dataId
            })
        });

        const result = await response.json();

        if (result.success) {
            statusDiv.textContent = 'Data generated successfully!';
            statusDiv.style.color = '#28a745';

            // Clear the prompt
            document.getElementById('dataPrompt').value = '';

            // Add card to dashboard
            addDataCard(result.data, dataId);

            // Reload saved data list
            loadSavedData();

            // Reset button
            setTimeout(() => {
                statusDiv.textContent = '';
            }, 3000);
        } else {
            throw new Error(result.message || 'Failed to generate data');
        }

    } catch (error) {
        console.error('Generate data error:', error);
        statusDiv.textContent = 'Failed to generate data. Make sure the Python API is running.';
        statusDiv.style.color = '#dc3545';
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Data';
    }
}

// Load saved data list
async function loadSavedData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/data/list`);
        const result = await response.json();

        const container = document.getElementById('savedDataContainer');

        if (result.data && result.data.length > 0) {
            container.innerHTML = '';
            result.data.forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'saved-data-item';
                itemDiv.innerHTML = `
                    <div class="data-item-info">
                        <strong>${item.title}</strong><br>
                        <small>${item.type}</small>
                    </div>
                    <div class="data-item-actions">
                        <button class="btn btn-small" onclick="loadDataCard('${item.id}')">Load</button>
                        <button class="btn btn-small" onclick="deleteData('${item.id}')">Delete</button>
                    </div>
                `;
                container.appendChild(itemDiv);
            });
        } else {
            container.innerHTML = '<p style="color: #999;">No saved data yet</p>';
        }
    } catch (error) {
        console.error('Load saved data error:', error);
    }
}

// Load a specific data card
async function loadDataCard(dataId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/data/${dataId}`);
        const data = await response.json();

        addDataCard(data, dataId);
    } catch (error) {
        console.error('Load data card error:', error);
        alert('Failed to load data card');
    }
}

// Delete saved data
async function deleteData(dataId) {
    if (!confirm('Are you sure you want to delete this data?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/data/${dataId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            // Remove card from dashboard if it exists
            const cardElement = document.querySelector(`[data-card-id="${dataId}"]`);
            if (cardElement) {
                cardElement.remove();
            }

            // Reload saved data list
            loadSavedData();
        }
    } catch (error) {
        console.error('Delete data error:', error);
        alert('Failed to delete data');
    }
}

// Add data card to dashboard
function addDataCard(data, dataId) {
    const cardGrid = document.getElementById('cardGrid');

    // Check if card already exists
    let existingCard = document.querySelector(`[data-card-id="${dataId}"]`);
    if (existingCard) {
        existingCard.remove();
    }

    // Create card element
    const cardDiv = document.createElement('div');
    cardDiv.className = 'card';
    cardDiv.dataset.cardId = dataId;
    cardDiv.dataset.cardData = JSON.stringify(data);

    let contentHtml = '';
    let currentType = data.type || 'table';

    if (currentType === 'table') {
        contentHtml = formatTableData(data);
    } else if (currentType === 'chart') {
        contentHtml = formatChartData(data);
    }

    const icon = currentType === 'table' ? '📊' : '📈';

    // Add view type dropdown
    const viewTypeDropdown = `
        <select class="card-view-type" onchange="switchCardView('${dataId}', this.value)" style="padding: 5px 10px; border-radius: 5px; border: 1px solid #ddd; background: white; cursor: pointer; font-size: 12px;">
            <option value="table" ${currentType === 'table' ? 'selected' : ''}>📊 Table</option>
            <option value="chart" ${currentType === 'chart' ? 'selected' : ''}>📈 Chart</option>
        </select>
    `;

    cardDiv.innerHTML = `
        <div class="card-header">
            <div class="card-title">${data.title || 'Generated Data'}</div>
            <div style="display: flex; align-items: center; gap: 10px;">
                ${viewTypeDropdown}
                <div class="card-icon">${icon}</div>
            </div>
        </div>
        <div class="card-content" id="card-content-${dataId}">
            ${contentHtml}
            <small style="color: #999; display: block; margin-top: 10px;">
                ${data.created ? new Date(data.created).toLocaleString() : ''}
            </small>
        </div>
    `;

    // Add to grid (insert after welcome card if it exists)
    const welcomeCard = cardGrid.querySelector('.card');
    if (welcomeCard && welcomeCard.querySelector('.card-title')?.textContent === 'Welcome') {
        welcomeCard.after(cardDiv);
    } else {
        cardGrid.appendChild(cardDiv);
    }

    // Update topic filter and placeholders
    const topic = data.topic;
    if (topic && !availableTopics.includes(topic)) {
        availableTopics.push(topic);
    }

    // Remove placeholder for this topic if it exists
    const placeholder = document.querySelector(`.placeholder-card[data-topic="${topic}"]`);
    if (placeholder) {
        placeholder.remove();
    }

    updateCardsByTopic();
}

// Switch between table and chart view
async function switchCardView(dataId, viewType) {
    const cardElement = document.querySelector(`[data-card-id="${dataId}"]`);
    if (!cardElement) return;

    const contentDiv = document.getElementById(`card-content-${dataId}`);
    const data = JSON.parse(cardElement.dataset.cardData);

    let contentHtml = '';

    if (viewType === 'table') {
        // If we have chart data, convert to table
        if (data.labels && data.values) {
            contentHtml = formatTableData({
                columns: ['Label', 'Value'],
                rows: data.labels.map((label, i) => [label, data.values[i]])
            });
        } else if (data.columns && data.rows) {
            contentHtml = formatTableData(data);
        }
    } else if (viewType === 'chart') {
        // If we have table data, try to convert to chart
        if (data.columns && data.rows) {
            // Request chart generation from the API
            try {
                const response = await fetch(`${API_BASE_URL}/api/data/${dataId}`);
                const fullData = await response.json();

                if (fullData.labels && fullData.values) {
                    contentHtml = formatChartData(fullData);
                } else {
                    // Create a simple chart from table data
                    const chartData = {
                        chart_type: 'bar',
                        labels: data.rows.map((row, i) => row[0] || `Item ${i + 1}`),
                        values: data.rows.map(row => parseFloat(row[1]) || 0),
                        title: data.title
                    };

                    // Generate chart
                    const genResponse = await fetch(`${API_BASE_URL}/api/generate-data`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            prompt: `Chart for ${data.title}`,
                            display_type: 'chart',
                            chart_type: 'bar',
                            data_id: dataId + '_chart'
                        })
                    });
                    const genResult = await genResponse.json();
                    if (genResult.success && genResult.data.image) {
                        contentHtml = formatChartData(genResult.data);
                    }
                }
            } catch (error) {
                console.error('Error converting to chart:', error);
                contentHtml = '<p>Unable to generate chart view</p>';
            }
        } else if (data.image || (data.labels && data.values)) {
            contentHtml = formatChartData(data);
        }
    }

    // Update the content
    const timestamp = data.created ? `<small style="color: #999; display: block; margin-top: 10px;">${new Date(data.created).toLocaleString()}</small>` : '';
    contentDiv.innerHTML = contentHtml + timestamp;
}

// Format table data
function formatTableData(data) {
    let html = '<table style="width: 100%; border-collapse: collapse;">';

    // Headers
    html += '<thead><tr>';
    data.columns.forEach(col => {
        html += `<th style="padding: 8px; text-align: left; border-bottom: 2px solid #667eea;">${col}</th>`;
    });
    html += '</tr></thead>';

    // Rows
    html += '<tbody>';
    data.rows.forEach((row, index) => {
        html += `<tr style="${index % 2 === 0 ? 'background: #f8f9fa;' : ''}">`;
        row.forEach(cell => {
            html += `<td style="padding: 8px;">${cell}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';

    return html;
}

// Format chart data
function formatChartData(data) {
    if (data.image) {
        return `<img src="${data.image}" alt="${data.title}" class="chart-image">`;
    } else {
        return '<p>Chart image not available</p>';
    }
}

// Chat functionality
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    addChatMessage(message, 'user');

    // Clear input
    input.value = '';

    // Show typing indicator
    const typingIndicator = addTypingIndicator();

    try {
        // Check if this is a query for specific information
        const lowerMsg = message.toLowerCase();
        const isQuery = lowerMsg.includes('where') || lowerMsg.includes('position') ||
                       lowerMsg.includes('status') || lowerMsg.includes('pose') ||
                       lowerMsg.includes('heading') || lowerMsg.includes('location');

        // Send task to robot
        const response = await fetch(`${API_BASE_URL}/api/robot/task`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                task: message,
                context: chatContext,
                is_query: isQuery
            })
        });

        const data = await response.json();

        // Remove typing indicator
        typingIndicator.remove();

        // Add bot response
        if (data.response) {
            addChatMessage(data.response, 'bot');
        } else if (data.success) {
            addChatMessage('Task sent to robot successfully!', 'bot');
        } else {
            addChatMessage('Failed to send task to robot.', 'bot');
        }

        // If it's a movement command, trigger path planning
        if (data.success && data.target_point) {
            const targetLabel = data.target_point;
            let target;

            if (targetLabel === 'CHARGE') {
                target = chargingPoint;
            } else {
                target = workPoints.find(wp => wp.label === targetLabel);
            }

            if (target) {
                const path = findPath(robotState, target);
                if (path) {
                    robotState.currentTask = `Moving to ${targetLabel}`;
                    robotState.targetPoint = target;
                    robotState.errors = 'None';
                    startRobotMovement(path);
                } else {
                    robotState.errors = 'Path planning failed';
                    addChatMessage('Cannot find a path to that location!', 'bot');
                }
            }
        }

        // Update context
        chatContext.push(
            { role: 'user', content: message },
            { role: 'assistant', content: data.response || 'Task received' }
        );

        // Keep only last 10 messages in context
        if (chatContext.length > 20) {
            chatContext = chatContext.slice(-20);
        }

    } catch (error) {
        console.error('Chat error:', error);
        typingIndicator.remove();
        addChatMessage('Sorry, I encountered an error. Please make sure the Python API is running.', 'bot');
    }
}

function addTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message bot-message typing-indicator';
    typingDiv.innerHTML = '<div class="message-content">Typing...</div>';
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return typingDiv;
}

function addChatMessage(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Support markdown in bot responses
    if (sender === 'bot' && typeof marked !== 'undefined') {
        contentDiv.innerHTML = marked.parse(message);
    } else {
        contentDiv.textContent = message;
    }

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle settings save
async function handleSettingsSave(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const settings = {
        displayName: formData.get('displayName'),
        email: formData.get('email'),
        theme: formData.get('theme'),
        notifications: document.getElementById('notifications').checked,
        language: formData.get('language'),
        timezone: formData.get('timezone')
    };

    try {
        // Send to Python API
        const pythonResponse = await fetch(`${API_BASE_URL}/api/settings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });

        const pythonData = await pythonResponse.json();

        // Also send to Node.js server
        const nodeResponse = await fetch('/api/save-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });

        const nodeData = await nodeResponse.json();

        if (pythonData.success && nodeData.success) {
            const messageDiv = document.getElementById('settingsMessage');
            messageDiv.textContent = 'Settings saved successfully!';
            messageDiv.style.color = '#28a745';

            setTimeout(() => {
                messageDiv.textContent = '';
            }, 3000);
        }
    } catch (error) {
        console.error('Save settings error:', error);
        const messageDiv = document.getElementById('settingsMessage');
        messageDiv.textContent = 'Failed to save settings.';
        messageDiv.style.color = '#dc3545';
    }
}

// Theme management
function loadThemePreference() {
    const theme = localStorage.getItem('theme') || 'light';
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.textContent = '☀️';
        }
    }
}

function toggleTheme() {
    const body = document.body;
    const themeToggle = document.getElementById('themeToggle');

    if (body.classList.contains('dark-theme')) {
        body.classList.remove('dark-theme');
        themeToggle.textContent = '🌙';
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.add('dark-theme');
        themeToggle.textContent = '☀️';
        localStorage.setItem('theme', 'dark');
    }
}

// Initialize topic filter
function initializeTopicFilter() {
    const topicFilter = document.getElementById('topicFilter');
    if (!topicFilter) return;

    // Clear existing options except 'All'
    topicFilter.innerHTML = '<option value="all" selected>All Topics</option>';

    // Add all available topics
    availableTopics.forEach(topic => {
        const option = document.createElement('option');
        option.value = topic;
        option.textContent = topic;
        topicFilter.appendChild(option);
    });

    // Initialize cards by topic
    updateCardsByTopic();

    // Create placeholder cards for topics without data
    createPlaceholderCards();
}

// Update the cards by topic mapping
function updateCardsByTopic() {
    cardsByTopic = {};

    // Initialize all topics with empty arrays
    availableTopics.forEach(topic => {
        cardsByTopic[topic] = [];
    });

    // Get all cards and categorize them
    const allCards = document.querySelectorAll('[data-card-id]');
    allCards.forEach(card => {
        const dataStr = card.dataset.cardData;
        if (dataStr) {
            try {
                const data = JSON.parse(dataStr);
                const topic = data.topic || 'General';

                if (!cardsByTopic[topic]) {
                    cardsByTopic[topic] = [];
                    if (!availableTopics.includes(topic)) {
                        availableTopics.push(topic);
                    }
                }

                cardsByTopic[topic].push(card.dataset.cardId);
            } catch (e) {
                console.error('Error parsing card data:', e);
            }
        }
    });
}

// Create placeholder cards for topics without data
function createPlaceholderCards() {
    const cardGrid = document.getElementById('cardGrid');

    availableTopics.forEach(topic => {
        if (!cardsByTopic[topic] || cardsByTopic[topic].length === 0) {
            // Create placeholder card
            const placeholderCard = document.createElement('div');
            placeholderCard.className = 'card placeholder-card';
            placeholderCard.dataset.topic = topic;
            placeholderCard.style.opacity = '0.6';
            placeholderCard.style.border = '2px dashed #ddd';

            placeholderCard.innerHTML = `
                <div class="card-header">
                    <div class="card-title">${topic}</div>
                    <div class="card-icon">📋</div>
                </div>
                <div class="card-content">
                    <p style="color: #999; font-style: italic;">No data available for this topic yet.</p>
                    <p style="color: #999; font-size: 14px;">Ask the AI assistant to create data for "${topic}"</p>
                </div>
            `;

            cardGrid.appendChild(placeholderCard);
        }
    });
}

// Filter cards by selected topics
function filterCardsByTopic() {
    const topicFilter = document.getElementById('topicFilter');
    const selectedOptions = Array.from(topicFilter.selectedOptions).map(opt => opt.value);

    const allCards = document.querySelectorAll('.card');
    const placeholderCards = document.querySelectorAll('.placeholder-card');

    // If "all" is selected or nothing is selected, show all cards
    if (selectedOptions.includes('all') || selectedOptions.length === 0) {
        allCards.forEach(card => {
            card.style.display = 'block';
        });
        return;
    }

    // Hide all cards first
    allCards.forEach(card => {
        const dataStr = card.dataset.cardData;
        const topic = card.dataset.topic;

        // Show placeholder cards for selected topics
        if (topic && selectedOptions.includes(topic)) {
            card.style.display = 'block';
            return;
        }

        // Show data cards for selected topics
        if (dataStr) {
            try {
                const data = JSON.parse(dataStr);
                const cardTopic = data.topic || 'General';

                if (selectedOptions.includes(cardTopic)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            } catch (e) {
                card.style.display = 'none';
            }
        } else if (card.querySelector('.card-title')?.textContent !== 'Welcome') {
            card.style.display = 'none';
        }
    });
}

// Make functions available globally
window.loadDataCard = loadDataCard;
window.deleteData = deleteData;
window.switchCardView = switchCardView;
window.sendToPoint = sendToPoint;
