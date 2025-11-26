// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';

// Global state
let generatedCards = [];
let websockets = {};
let chatContext = [];

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
    loadSavedData();
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

    // Data generation
    document.getElementById('generateDataBtn').addEventListener('click', generateData);
    document.getElementById('displayType').addEventListener('change', toggleChartTypeSelector);

    // Chat
    document.getElementById('sendChatBtn').addEventListener('click', sendChatMessage);
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });

    // Settings form
    document.getElementById('settingsForm').addEventListener('submit', handleSettingsSave);
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

    let contentHtml = '';

    if (data.type === 'table') {
        contentHtml = formatTableData(data);
    } else if (data.type === 'chart') {
        contentHtml = formatChartData(data);
    }

    const icon = data.type === 'table' ? '📊' : '📈';

    cardDiv.innerHTML = `
        <div class="card-header">
            <div class="card-title">${data.title || 'Generated Data'}</div>
            <div class="card-icon">${icon}</div>
        </div>
        <div class="card-content">
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

// Make functions available globally
window.loadDataCard = loadDataCard;
window.deleteData = deleteData;
