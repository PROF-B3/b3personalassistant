/**
 * B3 Personal Assistant - Terminal UI Application
 *
 * Handles WebSocket communication, UI interactions, and real-time updates
 * for the 3-panel terminal interface.
 */

class B3Assistant {
    constructor() {
        this.ws = null;
        this.reconnectInterval = null;
        this.currentView = 'chat';
        this.agentLogs = [];
        this.performanceData = [];
        this.metrics = {
            contextItems: 0,
            indexedItems: 0,
            messages: 0,
            actions: 0
        };

        this.init();
    }

    init() {
        console.log('🚀 Initializing B3 Assistant...');
        this.setupWebSocket();
        this.setupEventListeners();
        this.setupPanelResizers();
        this.setupCommandPalette();
        this.startPerformanceMonitoring();
        this.updateSystemTime();
        this.loadInitialData();
    }

    updateSystemTime() {
        const updateTime = () => {
            const now = new Date();
            const timeString = now.toLocaleTimeString('en-US', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            const timeElement = document.getElementById('systemTime');
            if (timeElement) {
                timeElement.textContent = timeString;
            }
        };

        updateTime(); // Initial update
        setInterval(updateTime, 1000); // Update every second
    }

    // ==================== WebSocket Connection ====================

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        console.log(`Connecting to WebSocket: ${wsUrl}`);
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('✅ WebSocket connected');
            this.updateStatus('connected');
            this.addSystemMessage('Connected to B3 Assistant');
            if (this.reconnectInterval) {
                clearInterval(this.reconnectInterval);
                this.reconnectInterval = null;
            }
        };

        this.ws.onclose = () => {
            console.log('❌ WebSocket disconnected');
            this.updateStatus('disconnected');
            this.addSystemMessage('Disconnected. Attempting to reconnect...');
            this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('error');
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };
    }

    attemptReconnect() {
        if (this.reconnectInterval) return;

        this.reconnectInterval = setInterval(() => {
            console.log('Attempting to reconnect...');
            this.setupWebSocket();
        }, 5000);
    }

    handleWebSocketMessage(data) {
        console.log('📨 Received:', data);

        switch (data.type) {
            case 'message':
                this.addMessage(data.content, data.sender || 'assistant');
                break;
            case 'agent_log':
                this.addAgentLog(data.level, data.message, data.agent);
                break;
            case 'metrics_update':
                this.updateMetrics(data.metrics);
                break;
            case 'suggestion':
                this.addSuggestion(data.suggestion);
                break;
            case 'performance':
                this.updatePerformanceChart(data.value);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    updateStatus(status) {
        const statusDot = document.getElementById('wsStatus');
        const statusText = document.getElementById('wsStatusText');

        statusDot.className = 'status-dot';

        switch (status) {
            case 'connected':
                statusDot.classList.add('online');
                statusText.textContent = 'Connected';
                break;
            case 'disconnected':
                statusDot.classList.add('offline');
                statusText.textContent = 'Disconnected';
                break;
            case 'error':
                statusDot.classList.add('offline');
                statusText.textContent = 'Error';
                break;
        }
    }

    // ==================== Message Handling ====================

    addMessage(content, sender = 'user') {
        const messagesContainer = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const timestamp = new Date().toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit'
        });

        const prefix = sender === 'user' ? '➤' : '◆';
        const label = sender === 'user' ? 'USER' : 'B3';

        messageDiv.innerHTML = `
            <span class="message-prefix">${prefix}</span>
            <span class="message-sender">${label}</span>
            <span class="message-time">[${timestamp}]</span>
            <span class="message-content">${this.escapeHtml(content)}</span>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Update metrics
        this.metrics.messages++;
        this.updateMetricDisplay('messages', this.metrics.messages);
    }

    addSystemMessage(content) {
        const messagesContainer = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system-message';

        const timestamp = new Date().toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit'
        });

        messageDiv.innerHTML = `
            <span class="message-prefix">⚡</span>
            <span class="message-sender">SYSTEM</span>
            <span class="message-time">[${timestamp}]</span>
            <span class="message-content">${this.escapeHtml(content)}</span>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    sendMessage(content) {
        if (!content.trim()) return;

        // Display user message
        this.addMessage(content, 'user');

        // Send via WebSocket if connected
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'message',
                content: content
            }));
        } else {
            // Fallback to REST API
            this.sendMessageViaAPI(content);
        }

        // Clear input
        const input = document.getElementById('messageInput');
        input.value = '';
    }

    async sendMessageViaAPI(content) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: content })
            });

            if (response.ok) {
                const data = await response.json();
                this.addMessage(data.response, 'assistant');
            } else {
                this.addSystemMessage('Error: Failed to send message');
            }
        } catch (error) {
            console.error('API request failed:', error);
            this.addSystemMessage('Error: Connection failed');
        }
    }

    // ==================== Agent Activity Log ====================

    addAgentLog(level, message, agent = 'system') {
        const log = {
            timestamp: new Date(),
            level: level,
            message: message,
            agent: agent
        };

        this.agentLogs.unshift(log); // Add to beginning
        if (this.agentLogs.length > 100) {
            this.agentLogs.pop(); // Keep last 100 logs
        }

        this.updateAgentLogDisplay();
    }

    updateAgentLogDisplay() {
        const logContainer = document.getElementById('agentLog');
        logContainer.innerHTML = '';

        const visibleLogs = this.agentLogs.slice(0, 50); // Show last 50

        visibleLogs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry log-${log.level}`;

            const time = log.timestamp.toLocaleTimeString('en-US', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });

            const icon = {
                'info': 'ℹ',
                'success': '✓',
                'warning': '⚠',
                'error': '✗'
            }[log.level] || '•';

            logEntry.innerHTML = `
                <span class="log-time">[${time}]</span>
                <span class="log-icon">${icon}</span>
                <span class="log-agent">${log.agent}:</span>
                <span class="log-message">${this.escapeHtml(log.message)}</span>
            `;

            logContainer.appendChild(logEntry);
        });
    }

    // ==================== Metrics & Performance ====================

    updateMetrics(metrics) {
        Object.assign(this.metrics, metrics);

        Object.keys(metrics).forEach(key => {
            this.updateMetricDisplay(key, metrics[key]);
        });
    }

    updateMetricDisplay(key, value) {
        const metricMap = {
            'contextItems': 'contextMetric',
            'indexedItems': 'indexedMetric',
            'messages': 'messagesMetric',
            'actions': 'actionsMetric'
        };

        const elementId = metricMap[key];
        if (elementId) {
            const element = document.getElementById(elementId);
            if (element) {
                const valueElement = element.querySelector('.metric-value');
                if (valueElement) {
                    valueElement.textContent = value.toLocaleString();
                }
            }
        }
    }

    updatePerformanceChart(value) {
        this.performanceData.push(value);
        if (this.performanceData.length > 10) {
            this.performanceData.shift();
        }

        this.renderPerformanceChart();
    }

    renderPerformanceChart() {
        const chartContainer = document.querySelector('.chart-bars');
        if (!chartContainer) return;

        chartContainer.innerHTML = '';

        const max = Math.max(...this.performanceData, 1);

        this.performanceData.forEach((value, index) => {
            const bar = document.createElement('div');
            bar.className = 'chart-bar';
            const height = (value / max) * 100;
            bar.style.height = `${height}%`;
            bar.title = `${value}ms`;
            chartContainer.appendChild(bar);
        });
    }

    startPerformanceMonitoring() {
        // Simulate performance data updates
        setInterval(() => {
            const value = Math.random() * 100 + 50; // 50-150ms
            this.updatePerformanceChart(value);
        }, 2000);

        // Add sample agent logs
        const agents = ['ProactiveAgent', 'WorkflowEngine', 'SemanticSearch', 'ContextManager'];
        const messages = [
            'Processing user request',
            'Updating context',
            'Searching indexed content',
            'Executing workflow',
            'Analyzing patterns',
            'Generating suggestion'
        ];
        const levels = ['info', 'success', 'warning'];

        setInterval(() => {
            const agent = agents[Math.floor(Math.random() * agents.length)];
            const message = messages[Math.floor(Math.random() * messages.length)];
            const level = levels[Math.floor(Math.random() * levels.length)];

            this.addAgentLog(level, message, agent);
        }, 3000);
    }

    // ==================== Suggestions ====================

    addSuggestion(suggestion) {
        const suggestionsContainer = document.getElementById('suggestions');

        const suggestionDiv = document.createElement('div');
        suggestionDiv.className = 'suggestion-item';
        suggestionDiv.textContent = `💡 ${suggestion}`;
        suggestionDiv.onclick = () => {
            document.getElementById('messageInput').value = suggestion;
        };

        suggestionsContainer.insertBefore(suggestionDiv, suggestionsContainer.firstChild);

        // Keep only last 5 suggestions
        while (suggestionsContainer.children.length > 5) {
            suggestionsContainer.removeChild(suggestionsContainer.lastChild);
        }
    }

    // ==================== Navigation ====================

    switchView(view) {
        this.currentView = view;

        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        event.target.classList.add('active');

        // Update chat panel header
        const viewNames = {
            'chat': '💬 Chat Interface',
            'context': '🧠 Context Manager',
            'search': '🔍 Semantic Search',
            'workflows': '⚙️ Workflows',
            'suggestions': '💡 Suggestions',
            'patterns': '📊 Patterns',
            'email': '📧 Email',
            'calendar': '📅 Calendar',
            'voice': '🎤 Voice',
            'docs': '📚 API Docs'
        };

        const header = document.querySelector('.chat-panel .panel-header');
        header.textContent = viewNames[view] || view;

        // Add system message
        this.addSystemMessage(`Switched to ${view} view`);

        // Load view-specific data
        this.loadViewData(view);
    }

    async loadViewData(view) {
        // Load data based on current view
        switch (view) {
            case 'context':
                await this.loadContextData();
                break;
            case 'search':
                await this.loadSearchData();
                break;
            case 'workflows':
                await this.loadWorkflowsData();
                break;
            case 'suggestions':
                await this.loadSuggestionsData();
                break;
            case 'patterns':
                await this.loadPatternsData();
                break;
            case 'email':
                await this.loadEmailData();
                break;
            case 'calendar':
                await this.loadCalendarData();
                break;
        }
    }

    async loadContextData() {
        try {
            const response = await fetch('/api/context/list');
            if (response.ok) {
                const data = await response.json();
                this.metrics.contextItems = data.items?.length || 0;
                this.updateMetricDisplay('contextItems', this.metrics.contextItems);
            }
        } catch (error) {
            console.error('Failed to load context data:', error);
        }
    }

    async loadSearchData() {
        try {
            const response = await fetch('/api/search/stats');
            if (response.ok) {
                const data = await response.json();
                this.metrics.indexedItems = data.total_items || 0;
                this.updateMetricDisplay('indexedItems', this.metrics.indexedItems);
            }
        } catch (error) {
            console.error('Failed to load search data:', error);
        }
    }

    async loadWorkflowsData() {
        try {
            const response = await fetch('/api/workflows');
            if (response.ok) {
                const data = await response.json();
                this.addSystemMessage(`Loaded ${data.workflows?.length || 0} workflows`);
            }
        } catch (error) {
            console.error('Failed to load workflows:', error);
        }
    }

    async loadSuggestionsData() {
        try {
            const response = await fetch('/api/proactive/suggestions?limit=10');
            if (response.ok) {
                const data = await response.json();
                data.suggestions?.forEach(s => this.addSuggestion(s.action));
            }
        } catch (error) {
            console.error('Failed to load suggestions:', error);
        }
    }

    async loadPatternsData() {
        try {
            const response = await fetch('/api/proactive/patterns');
            if (response.ok) {
                const data = await response.json();
                this.addSystemMessage(`Identified ${data.patterns?.length || 0} patterns`);
            }
        } catch (error) {
            console.error('Failed to load patterns:', error);
        }
    }

    async loadEmailData() {
        this.addSystemMessage('Email integration - authenticate to access');
    }

    async loadCalendarData() {
        this.addSystemMessage('Calendar integration - authenticate to access');
    }

    async loadInitialData() {
        await this.loadContextData();
        await this.loadSearchData();
        await this.loadSuggestionsData();
    }

    // ==================== Panel Resizing ====================

    setupPanelResizers() {
        const resizers = document.querySelectorAll('.resizer');

        resizers.forEach(resizer => {
            let isResizing = false;
            let startX = 0;
            let startWidth = 0;
            let panel = null;

            resizer.addEventListener('mousedown', (e) => {
                isResizing = true;
                startX = e.clientX;

                // Find which panel to resize
                panel = resizer.previousElementSibling;
                startWidth = panel.offsetWidth;

                document.body.style.cursor = 'col-resize';
                e.preventDefault();
            });

            document.addEventListener('mousemove', (e) => {
                if (!isResizing) return;

                const delta = e.clientX - startX;
                const newWidth = startWidth + delta;

                // Enforce min/max widths
                if (newWidth >= 200 && newWidth <= 600) {
                    panel.style.width = `${newWidth}px`;
                    panel.style.flexBasis = `${newWidth}px`;
                }
            });

            document.addEventListener('mouseup', () => {
                if (isResizing) {
                    isResizing = false;
                    document.body.style.cursor = 'default';
                }
            });
        });
    }

    // ==================== Command Palette ====================

    setupCommandPalette() {
        const palette = document.getElementById('commandPalette');
        const input = document.getElementById('commandInput');
        const results = document.getElementById('commandResults');

        const commands = [
            { name: 'Switch to Chat', action: () => this.switchView('chat') },
            { name: 'Switch to Context', action: () => this.switchView('context') },
            { name: 'Switch to Search', action: () => this.switchView('search') },
            { name: 'Switch to Workflows', action: () => this.switchView('workflows') },
            { name: 'Switch to Email', action: () => this.switchView('email') },
            { name: 'Switch to Calendar', action: () => this.switchView('calendar') },
            { name: 'Clear Chat', action: () => this.clearChat() },
            { name: 'Toggle Nav Panel', action: () => this.togglePanel('navPanel') },
            { name: 'Toggle Monitor Panel', action: () => this.togglePanel('monitorPanel') },
            { name: 'Refresh Data', action: () => this.loadInitialData() }
        ];

        // Open palette with Ctrl+K
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                palette.style.display = 'flex';
                input.focus();
            }

            if (e.key === 'Escape') {
                palette.style.display = 'none';
            }
        });

        // Close on background click
        palette.addEventListener('click', (e) => {
            if (e.target === palette) {
                palette.style.display = 'none';
            }
        });

        // Filter commands
        input.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            results.innerHTML = '';

            const filtered = commands.filter(cmd =>
                cmd.name.toLowerCase().includes(query)
            );

            filtered.slice(0, 8).forEach(cmd => {
                const item = document.createElement('div');
                item.className = 'command-item';
                item.textContent = cmd.name;
                item.onclick = () => {
                    cmd.action();
                    palette.style.display = 'none';
                    input.value = '';
                };
                results.appendChild(item);
            });
        });

        // Trigger initial filter
        input.dispatchEvent(new Event('input'));
    }

    clearChat() {
        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = '';
        this.addSystemMessage('Chat cleared');
    }

    togglePanel(panelId) {
        const panel = document.getElementById(panelId);
        panel.style.display = panel.style.display === 'none' ? 'flex' : 'none';
    }

    // ==================== Event Listeners ====================

    setupEventListeners() {
        // Send message on Enter
        const input = document.getElementById('messageInput');
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage(input.value);
            }
        });

        // Send button
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendMessage(input.value);
        });

        // Navigation items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const view = e.target.dataset.view;
                if (view) {
                    this.switchView(view);
                }
            });
        });
    }

    // ==================== Utilities ====================

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 Starting B3 Personal Assistant...');
    window.b3 = new B3Assistant();
    console.log('✅ B3 Assistant ready!');
});
