// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';

// Card data with markdown content
let cardData = [
    {
        id: 'card1',
        title: 'Analytics',
        icon: '📊',
        topic: 'analytics',
        content: `## Website Analytics\n\nLoading...`
    },
    {
        id: 'card2',
        title: 'User Stats',
        icon: '👥',
        topic: 'users',
        content: `### User Statistics\n\nLoading...`
    },
    {
        id: 'card3',
        title: 'Revenue',
        icon: '💰',
        topic: 'revenue',
        content: `## Revenue Overview\n\nLoading...`
    },
    {
        id: 'card4',
        title: 'Tasks',
        icon: '✅',
        topic: 'tasks',
        content: `### Today's Tasks\n\nLoading...`
    },
    {
        id: 'card5',
        title: 'Performance',
        icon: '⚡',
        topic: 'performance',
        content: `## System Performance\n\nLoading...`
    },
    {
        id: 'card6',
        title: 'Activity',
        icon: '🔔',
        topic: 'activity',
        content: `### Recent Activity\n\nLoading...`
    }
];

// Global state
let currentLayout = [];
let draggedElement = null;
let draggedIndex = null;
let websockets = {};
let pollingIntervals = {};
let useWebSocket = true; // Toggle between WebSocket and polling
let chatContext = []; // Store chat history for context

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    initializeEventListeners();
});

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
}

// Show main application
function showMainApp() {
    document.getElementById('loginModal').style.display = 'none';
    document.getElementById('mainContainer').style.display = 'block';
    initializeDashboard();
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

    // Save layout
    document.getElementById('saveLayoutBtn').addEventListener('click', saveLayout);

    // Chat
    document.getElementById('sendChatBtn').addEventListener('click', sendChatMessage);
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });

    // Card filter
    document.getElementById('cardFilter').addEventListener('change', filterCards);

    // Settings form
    document.getElementById('settingsForm').addEventListener('submit', handleSettingsSave);
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

        // Clear polling intervals
        Object.values(pollingIntervals).forEach(interval => {
            clearInterval(interval);
        });

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

// Initialize dashboard with cards
function initializeDashboard() {
    currentLayout = [...cardData];
    renderCards();
    subscribeToDataTopics();
}

// Subscribe to data topics
function subscribeToDataTopics() {
    if (useWebSocket) {
        // Use WebSocket for real-time updates
        cardData.forEach(card => {
            connectWebSocket(card.topic);
        });
    } else {
        // Use polling as fallback
        cardData.forEach(card => {
            startPolling(card.topic);
        });
    }
}

// Connect to WebSocket for a specific topic
function connectWebSocket(topic) {
    const ws = new WebSocket(`${WS_BASE_URL}/ws/${topic}`);

    ws.onopen = () => {
        console.log(`WebSocket connected to topic: ${topic}`);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateCardData(topic, data);
    };

    ws.onerror = (error) => {
        console.error(`WebSocket error for ${topic}:`, error);
        // Fallback to polling
        ws.close();
        startPolling(topic);
    };

    ws.onclose = () => {
        console.log(`WebSocket closed for topic: ${topic}`);
        // Attempt reconnection after 5 seconds
        setTimeout(() => {
            if (useWebSocket) {
                connectWebSocket(topic);
            }
        }, 5000);
    };

    websockets[topic] = ws;
}

// Start polling for a specific topic
function startPolling(topic) {
    // Fetch immediately
    fetchTopicData(topic);

    // Then poll every 5 seconds
    const interval = setInterval(() => {
        fetchTopicData(topic);
    }, 5000);

    pollingIntervals[topic] = interval;
}

// Fetch data for a specific topic
async function fetchTopicData(topic) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/data/${topic}`);
        const data = await response.json();
        updateCardData(topic, data);
    } catch (error) {
        console.error(`Error fetching data for ${topic}:`, error);
    }
}

// Update card data based on API response
function updateCardData(topic, data) {
    const cardIndex = cardData.findIndex(card => card.topic === topic);
    if (cardIndex === -1) return;

    let content = '';

    switch (data.type) {
        case 'table':
            content = formatTableData(data);
            break;
        case 'stats':
            content = formatStatsData(data);
            break;
        case 'tasks':
            content = formatTasksData(data);
            break;
        case 'metrics':
            content = formatMetricsData(data);
            break;
        case 'log':
            content = formatLogData(data);
            break;
        default:
            content = JSON.stringify(data, null, 2);
    }

    cardData[cardIndex].content = content;
    currentLayout[cardIndex].content = content;

    // Re-render the specific card
    renderCards();
}

// Format table data as markdown
function formatTableData(data) {
    let markdown = `## ${data.title}\n\n`;
    markdown += `| ${data.columns.join(' | ')} |\n`;
    markdown += `|${data.columns.map(() => '--------').join('|')}|\n`;

    data.rows.forEach(row => {
        markdown += `| ${row.join(' | ')} |\n`;
    });

    return markdown;
}

// Format stats data as markdown
function formatStatsData(data) {
    let markdown = `### ${data.title}\n\n`;

    for (const [key, value] of Object.entries(data.data)) {
        const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        markdown += `- **${label}**: ${value}\n`;
    }

    return markdown;
}

// Format tasks data as markdown
function formatTasksData(data) {
    let markdown = `### ${data.title}\n\n`;

    data.data.tasks.forEach((task, index) => {
        const checkbox = task.completed ? '✓' : ' ';
        markdown += `${index + 1}. [${checkbox}] ${task.task}\n`;
    });

    markdown += `\n**Completed**: ${data.data.completed}/${data.data.total} tasks`;

    return markdown;
}

// Format metrics data as markdown
function formatMetricsData(data) {
    let markdown = `## ${data.title}\n\n\`\`\`\n`;

    for (const [key, value] of Object.entries(data.data)) {
        if (key !== 'status') {
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            markdown += `${label}: ${value}\n`;
        }
    }

    markdown += `\`\`\`\n\n**Status**: ${data.data.status} ✓`;

    return markdown;
}

// Format log data as markdown
function formatLogData(data) {
    let markdown = `### ${data.title}\n\n`;

    data.data.entries.forEach(entry => {
        markdown += `- ${entry}\n`;
    });

    markdown += `\n_Last updated: ${data.data.last_updated}_`;

    return markdown;
}

// Render cards
function renderCards() {
    const cardGrid = document.getElementById('cardGrid');
    cardGrid.innerHTML = '';

    const selectedCards = Array.from(document.getElementById('cardFilter').selectedOptions)
        .map(option => option.value);

    currentLayout.forEach((card, index) => {
        if (selectedCards.includes(card.id)) {
            const cardElement = createCardElement(card, index);
            cardGrid.appendChild(cardElement);
        }
    });
}

// Create card element
function createCardElement(card, index) {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'card';
    cardDiv.draggable = true;
    cardDiv.dataset.index = index;
    cardDiv.dataset.cardId = card.id;

    // Parse markdown content
    const htmlContent = marked.parse(card.content);

    cardDiv.innerHTML = `
        <div class="card-header">
            <div class="card-title">${card.title}</div>
            <div class="card-icon">${card.icon}</div>
        </div>
        <div class="card-content">
            ${htmlContent}
        </div>
    `;

    // Add drag event listeners
    cardDiv.addEventListener('dragstart', handleDragStart);
    cardDiv.addEventListener('dragend', handleDragEnd);
    cardDiv.addEventListener('dragover', handleDragOver);
    cardDiv.addEventListener('drop', handleDrop);

    return cardDiv;
}

// Drag and drop handlers
function handleDragStart(e) {
    draggedElement = e.target;
    draggedIndex = parseInt(e.target.dataset.index);
    e.target.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
    draggedElement = null;
    draggedIndex = null;
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

function handleDrop(e) {
    e.preventDefault();

    if (draggedElement === null) return;

    const dropIndex = parseInt(e.currentTarget.dataset.index);

    if (draggedIndex !== dropIndex) {
        // Reorder the layout array
        const draggedCard = currentLayout[draggedIndex];
        currentLayout.splice(draggedIndex, 1);
        currentLayout.splice(dropIndex, 0, draggedCard);

        // Re-render cards
        renderCards();
    }
}

// Filter cards based on multi-select
function filterCards() {
    renderCards();
}

// Save layout
async function saveLayout() {
    try {
        const response = await fetch('/api/save-layout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ layout: currentLayout })
        });

        const data = await response.json();

        if (data.success) {
            // Show success feedback
            const btn = document.getElementById('saveLayoutBtn');
            const originalText = btn.textContent;
            btn.textContent = '✓ Saved!';
            btn.style.background = '#28a745';

            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '';
            }, 2000);
        }
    } catch (error) {
        console.error('Save layout error:', error);
        alert('Failed to save layout');
    }
}

// Chat functionality with Ollama
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
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                context: chatContext
            })
        });

        const data = await response.json();

        // Remove typing indicator
        typingIndicator.remove();

        // Add bot response
        addChatMessage(data.response, 'bot');

        // Update context
        chatContext.push(
            { role: 'user', content: message },
            { role: 'assistant', content: data.response }
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
    if (sender === 'bot') {
        contentDiv.innerHTML = marked.parse(message);
    } else {
        contentDiv.textContent = message;
    }

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle settings save with Python API
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
            messageDiv.textContent = 'Settings saved successfully to both servers!';
            messageDiv.style.color = '#28a745';

            setTimeout(() => {
                messageDiv.textContent = '';
            }, 3000);
        }
    } catch (error) {
        console.error('Save settings error:', error);
        const messageDiv = document.getElementById('settingsMessage');
        messageDiv.textContent = 'Failed to save settings. Make sure the Python API is running.';
        messageDiv.style.color = '#dc3545';
    }
}
