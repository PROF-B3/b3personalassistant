/**
 * B3 Personal Assistant - Enhanced Terminal UI Application
 *
 * Complete implementation with markdown, themes, search, export,
 * keyboard shortcuts, notifications, and all advanced features.
 */

class B3Assistant {
    constructor() {
        this.ws = null;
        this.reconnectInterval = null;
        this.currentView = 'chat';
        this.agentLogs = [];
        this.performanceData = [];
        this.messages = [];
        this.messageHistory = [];
        this.historyIndex = -1;
        this.metrics = {
            contextItems: 0,
            indexedItems: 0,
            messages: 0,
            actions: 0
        };
        this.settings = this.loadSettings();
        this.chatHistory = this.loadChatHistory();

        // Initialize marked for markdown rendering
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (e) {
                            console.error('Highlight error:', e);
                        }
                    }
                    return code;
                },
                breaks: true,
                gfm: true
            });
        }

        this.init();
    }

    init() {
        console.log('🚀 Initializing B3 Assistant...');
        this.applySettings();
        this.showWelcomeMessage();
        this.setupWebSocket();
        this.setupEventListeners();
        this.setupPanelResizers();
        this.setupCommandPalette();
        this.setupKeyboardShortcuts();
        this.startPerformanceMonitoring();
        this.updateSystemTime();
        this.loadInitialData();
        this.requestNotificationPermission();
        this.restoreChatHistory();
    }

    // ==================== Settings & LocalStorage ====================

    loadSettings() {
        const defaultSettings = {
            theme: 'matrix',
            fontSize: '1em',
            notificationsEnabled: true,
            soundEnabled: false,
            reduceMotion: false,
            highContrast: false,
            debugMode: false,
            autoScroll: true,
            panelSizes: { nav: 250, monitor: 350 }
        };

        try {
            const saved = localStorage.getItem('b3_settings');
            return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
        } catch (e) {
            console.error('Failed to load settings:', e);
            return defaultSettings;
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('b3_settings', JSON.stringify(this.settings));
        } catch (e) {
            console.error('Failed to save settings:', e);
        }
    }

    applySettings() {
        // Apply theme
        document.body.className = '';
        if (this.settings.theme !== 'matrix') {
            document.body.classList.add(`theme-${this.settings.theme}`);
        }

        // Apply font size
        document.body.style.fontSize = this.settings.fontSize;

        // Apply reduce motion
        if (this.settings.reduceMotion) {
            document.body.classList.add('reduce-motion');
        }

        // Apply high contrast
        if (this.settings.highContrast) {
            document.body.classList.add('high-contrast');
        }
    }

    loadChatHistory() {
        try {
            const saved = localStorage.getItem('b3_chat_history');
            return saved ? JSON.parse(saved) : [];
        } catch (e) {
            console.error('Failed to load chat history:', e);
            return [];
        }
    }

    saveChatHistory() {
        try {
            // Keep last 100 messages
            const history = this.messages.slice(-100);
            localStorage.setItem('b3_chat_history', JSON.stringify(history));
        } catch (e) {
            console.error('Failed to save chat history:', e);
        }
    }

    restoreChatHistory() {
        if (this.chatHistory.length > 0) {
            this.chatHistory.forEach(msg => {
                this.addMessage(msg.content, msg.sender, false);
            });
        }
    }

    // ==================== Welcome & UI Setup ====================

    showWelcomeMessage() {
        const messagesContainer = document.getElementById('messages');
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'message system-message';

        const asciiArt = `
 ____  _____   ____                                   _      _            _     _              _
| __ )|___ /  |  _ \\ ___ _ __ ___  ___  _ __   __ _| |    / \\   ___ ___(_)___| |_ __ _ _ __ | |_
|  _ \\  |_ \\  | |_) / _ \\ '__/ __|/ _ \\| '_ \\ / _\` | |   / _ \\ / __/ __| / __| __/ _\` | '_ \\| __|
| |_) |___) | |  __/  __/ |  \\__ \\ (_) | | | | (_| | |  / ___ \\\\__ \\__ \\ \\__ \\ || (_| | | | | |_
|____/|____/  |_|   \\___|_|  |___/\\___/|_| |_|\\__,_|_| /_/   \\_\\___/___/_|___/\\__\\__,_|_| |_|\\__|

╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║  Welcome to B3 Personal Assistant - Your Intelligent Terminal Interface                     ║
║                                                                                              ║
║  ⚡ Three powerful panels at your command                                                   ║
║  🧠 Context-aware assistance with semantic search                                           ║
║  🤖 Proactive agents monitoring your workflow                                               ║
║  🔧 Integrated email, calendar, and voice capabilities                                      ║
║                                                                                              ║
║  💡 Tips:                                                                                    ║
║     • Press Ctrl+K to open command palette                                                  ║
║     • Press Ctrl+, to open settings                                                         ║
║     • Press Ctrl+F to search messages                                                       ║
║     • Click navigation items to switch views                                                ║
║     • Drag panel edges to resize                                                            ║
║     • Click suggestions to auto-fill your message                                           ║
║                                                                                              ║
║  Type your message below to get started...                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
`;

        welcomeDiv.innerHTML = `<pre class="ascii-art">${asciiArt}</pre>`;
        messagesContainer.appendChild(welcomeDiv);
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

        updateTime();
        setInterval(updateTime, 1000);
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
            this.showNotification('Connected', 'WebSocket connection established', 'success');
            if (this.reconnectInterval) {
                clearInterval(this.reconnectInterval);
                this.reconnectInterval = null;
            }
        };

        this.ws.onclose = () => {
            console.log('❌ WebSocket disconnected');
            this.updateStatus('disconnected');
            this.addSystemMessage('Disconnected. Attempting to reconnect...');
            this.showNotification('Disconnected', 'Connection lost. Reconnecting...', 'warning');
            this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('error');
            this.showNotification('Connection Error', 'Failed to connect to server', 'error');
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
                this.hideTypingIndicator();
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
            case 'typing':
                if (data.typing) {
                    this.showTypingIndicator();
                } else {
                    this.hideTypingIndicator();
                }
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

    showTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.classList.add('active');
            this.scrollToBottom();
        }
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.classList.remove('active');
        }
    }

    // ==================== Message Handling with Markdown ====================

    addMessage(content, sender = 'user', save = true) {
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

        // Render markdown for assistant messages
        let renderedContent;
        if (sender === 'assistant' && typeof marked !== 'undefined') {
            renderedContent = marked.parse(content);
        } else {
            renderedContent = this.escapeHtml(content);
        }

        messageDiv.innerHTML = `
            <span class="message-prefix">${prefix}</span>
            <span class="message-sender">${label}</span>
            <span class="message-time">[${timestamp}]</span>
            <div class="message-content">${renderedContent}</div>
            <div class="message-actions">
                <button class="message-btn" onclick="window.b3.copyMessage(this)">📋 Copy</button>
                <button class="message-btn" onclick="window.b3.deleteMessage(this)">🗑️ Delete</button>
            </div>
        `;

        // Add code block buttons
        messageDiv.querySelectorAll('pre code').forEach((block, index) => {
            const pre = block.parentElement;
            const wrapper = document.createElement('div');
            wrapper.style.position = 'relative';

            const header = document.createElement('div');
            header.className = 'code-block-header';
            header.innerHTML = `
                <span class="code-language">${block.className.replace('language-', '') || 'code'}</span>
                <div class="code-actions">
                    <button class="code-btn" onclick="window.b3.copyCode(this)">Copy</button>
                    <button class="code-btn" onclick="window.b3.downloadCode(this)">Download</button>
                </div>
            `;

            pre.parentNode.insertBefore(wrapper, pre);
            wrapper.appendChild(header);
            wrapper.appendChild(pre);
        });

        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        // Update metrics and save
        this.metrics.messages++;
        this.updateMetricDisplay('messages', this.metrics.messages);

        if (save) {
            this.messages.push({ content, sender, timestamp: Date.now() });
            this.saveChatHistory();
        }
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
        this.scrollToBottom();
    }

    sendMessage(content) {
        if (!content.trim()) return;

        // Add to history
        this.messageHistory.unshift(content);
        if (this.messageHistory.length > 50) {
            this.messageHistory.pop();
        }
        this.historyIndex = -1;

        // Display user message
        this.addMessage(content, 'user');

        // Show typing indicator
        this.showTypingIndicator();

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
            this.showLoading('Sending message...');

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: content })
            });

            this.hideLoading();
            this.hideTypingIndicator();

            if (response.ok) {
                const data = await response.json();
                this.addMessage(data.response, 'assistant');
            } else {
                this.addSystemMessage('Error: Failed to send message');
                this.showNotification('Error', 'Failed to send message', 'error');
            }
        } catch (error) {
            this.hideLoading();
            this.hideTypingIndicator();
            console.error('API request failed:', error);
            this.addSystemMessage('Error: Connection failed');
            this.showNotification('Connection Failed', 'Unable to reach server', 'error');
        }
    }

    copyMessage(button) {
        const message = button.closest('.message');
        const content = message.querySelector('.message-content').innerText;
        this.copyToClipboard(content);
        this.showNotification('Copied', 'Message copied to clipboard', 'success');
    }

    deleteMessage(button) {
        const message = button.closest('.message');
        message.style.opacity = '0';
        setTimeout(() => message.remove(), 300);
        this.showNotification('Deleted', 'Message removed', 'info');
    }

    copyCode(button) {
        const wrapper = button.closest('div').parentElement;
        const code = wrapper.querySelector('code').innerText;
        this.copyToClipboard(code);

        button.textContent = 'Copied!';
        setTimeout(() => button.textContent = 'Copy', 2000);
    }

    downloadCode(button) {
        const wrapper = button.closest('div').parentElement;
        const code = wrapper.querySelector('code').innerText;
        const lang = wrapper.querySelector('.code-language').textContent;

        const blob = new Blob([code], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `code.${lang || 'txt'}`;
        a.click();
        URL.revokeObjectURL(url);

        this.showNotification('Downloaded', 'Code snippet saved', 'success');
    }

    scrollToBottom() {
        if (this.settings.autoScroll) {
            const container = document.getElementById('messages');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
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

        this.agentLogs.unshift(log);
        if (this.agentLogs.length > 100) {
            this.agentLogs.pop();
        }

        this.updateAgentLogDisplay();
    }

    updateAgentLogDisplay() {
        const logContainer = document.getElementById('agentLog');
        if (!logContainer) return;

        logContainer.innerHTML = '';

        const visibleLogs = this.agentLogs.slice(0, 50);

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
        // Add initial system boot log with ASCII art
        this.addAgentLog('success', '╔════════════════════════════╗', 'SYSTEM');
        this.addAgentLog('success', '║   B3 SYSTEMS ONLINE ✓     ║', 'SYSTEM');
        this.addAgentLog('success', '╚════════════════════════════╝', 'SYSTEM');
        this.addAgentLog('info', 'Initializing agent subsystems...', 'SYSTEM');
        this.addAgentLog('success', '► ProactiveAgent loaded', 'ProactiveAgent');
        this.addAgentLog('success', '► WorkflowEngine loaded', 'WorkflowEngine');
        this.addAgentLog('success', '► SemanticSearch loaded', 'SemanticSearch');
        this.addAgentLog('success', '► ContextManager loaded', 'ContextManager');
        this.addAgentLog('info', '⚡ All systems operational', 'SYSTEM');

        // Simulate performance data updates
        setInterval(() => {
            const value = Math.random() * 100 + 50;
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
            'Generating suggestion',
            'Cache hit on recent query',
            'Indexing new document',
            'Pattern match detected',
            'Workflow step completed',
            'Context window optimized',
            'Semantic embedding cached'
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
        if (!suggestionsContainer) return;

        const suggestionDiv = document.createElement('div');
        suggestionDiv.className = 'suggestion-item';
        suggestionDiv.textContent = `💡 ${suggestion}`;
        suggestionDiv.onclick = () => {
            document.getElementById('messageInput').value = suggestion;
            document.getElementById('messageInput').focus();
        };

        suggestionsContainer.insertBefore(suggestionDiv, suggestionsContainer.firstChild);

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
        if (header) {
            header.textContent = viewNames[view] || view;
        }

        // Add system message with ASCII decoration
        const asciiHeaders = {
            'chat': '━━━━━━━━━━━━━━━━━━━━━━━━━\n  💬 CHAT MODE ACTIVATED\n━━━━━━━━━━━━━━━━━━━━━━━━━',
            'context': '━━━━━━━━━━━━━━━━━━━━━━━━━\n  🧠 CONTEXT MANAGER\n━━━━━━━━━━━━━━━━━━━━━━━━━',
            'search': '━━━━━━━━━━━━━━━━━━━━━━━━━\n  🔍 SEMANTIC SEARCH\n━━━━━━━━━━━━━━━━━━━━━━━━━',
            'workflows': '━━━━━━━━━━━━━━━━━━━━━━━━━\n  ⚙️  WORKFLOW ENGINE\n━━━━━━━━━━━━━━━━━━━━━━━━━',
            'email': '━━━━━━━━━━━━━━━━━━━━━━━━━\n  📧 EMAIL INTEGRATION\n━━━━━━━━━━━━━━━━━━━━━━━━━',
            'calendar': '━━━━━━━━━━━━━━━━━━━━━━━━━\n  📅 CALENDAR SYNC\n━━━━━━━━━━━━━━━━━━━━━━━━━',
            'voice': '━━━━━━━━━━━━━━━━━━━━━━━━━\n  🎤 VOICE INTERFACE\n━━━━━━━━━━━━━━━━━━━━━━━━━'
        };

        if (asciiHeaders[view]) {
            const messagesContainer = document.getElementById('messages');
            const headerDiv = document.createElement('div');
            headerDiv.className = 'message system-message';
            headerDiv.innerHTML = `<pre class="ascii-art">${asciiHeaders[view]}</pre>`;
            messagesContainer.appendChild(headerDiv);
            this.scrollToBottom();
        } else {
            this.addSystemMessage(`Switched to ${view} view`);
        }

        // Add agent log
        this.addAgentLog('info', `View changed to ${view}`, 'SYSTEM');

        // Load view-specific data
        this.loadViewData(view);
    }

    async loadViewData(view) {
        this.showLoading(`Loading ${view} data...`);

        try {
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
        } catch (error) {
            console.error(`Failed to load ${view} data:`, error);
            this.showNotification('Error', `Failed to load ${view} data`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async loadContextData() {
        try {
            const response = await fetch('/api/context/all');
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

                panel = resizer.previousElementSibling;
                startWidth = panel.offsetWidth;

                document.body.style.cursor = 'col-resize';
                e.preventDefault();
            });

            document.addEventListener('mousemove', (e) => {
                if (!isResizing) return;

                const delta = e.clientX - startX;
                const newWidth = startWidth + delta;

                if (newWidth >= 200 && newWidth <= 600) {
                    panel.style.width = `${newWidth}px`;
                    panel.style.flexBasis = `${newWidth}px`;
                }
            });

            document.addEventListener('mouseup', () => {
                if (isResizing) {
                    isResizing = false;
                    document.body.style.cursor = 'default';

                    // Save panel size
                    if (panel.id === 'navPanel') {
                        this.settings.panelSizes.nav = panel.offsetWidth;
                    } else if (panel.id === 'monitorPanel') {
                        this.settings.panelSizes.monitor = panel.offsetWidth;
                    }
                    this.saveSettings();
                }
            });
        });

        // Restore panel sizes
        const navPanel = document.getElementById('navPanel');
        const monitorPanel = document.getElementById('monitorPanel');

        if (navPanel && this.settings.panelSizes.nav) {
            navPanel.style.width = `${this.settings.panelSizes.nav}px`;
        }
        if (monitorPanel && this.settings.panelSizes.monitor) {
            monitorPanel.style.width = `${this.settings.panelSizes.monitor}px`;
        }
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
            { name: 'Switch to Voice', action: () => this.switchView('voice') },
            { name: 'Open Settings', action: () => this.openSettings() },
            { name: 'Open Search', action: () => this.openSearch() },
            { name: 'Clear Chat', action: () => this.clearChat() },
            { name: 'Export Chat', action: () => this.exportChat() },
            { name: 'Toggle Nav Panel', action: () => this.togglePanel('navPanel') },
            { name: 'Toggle Monitor Panel', action: () => this.togglePanel('monitorPanel') },
            { name: 'Refresh Data', action: () => this.loadInitialData() },
            { name: 'Toggle Debug Mode', action: () => this.toggleDebugMode() }
        ];

        // Close on background click
        palette.addEventListener('click', (e) => {
            if (e.target === palette) {
                this.closeCommandPalette();
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
                    this.closeCommandPalette();
                };
                results.appendChild(item);
            });
        });

        // Trigger initial filter
        input.dispatchEvent(new Event('input'));
    }

    openCommandPalette() {
        const palette = document.getElementById('commandPalette');
        const input = document.getElementById('commandInput');
        palette.style.display = 'flex';
        input.focus();
        input.select();
    }

    closeCommandPalette() {
        const palette = document.getElementById('commandPalette');
        const input = document.getElementById('commandInput');
        palette.style.display = 'none';
        input.value = '';
    }

    // ==================== Keyboard Shortcuts ====================

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd+K - Command Palette
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.openCommandPalette();
            }

            // Ctrl/Cmd+L - Clear Chat
            if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
                e.preventDefault();
                this.clearChat();
            }

            // Ctrl/Cmd+E - Export Chat
            if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
                e.preventDefault();
                this.exportChat();
            }

            // Ctrl/Cmd+F - Search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                this.openSearch();
            }

            // Ctrl/Cmd+/ - Show Shortcuts
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                e.preventDefault();
                this.openSettings();
            }

            // Ctrl/Cmd+, - Settings
            if ((e.ctrlKey || e.metaKey) && e.key === ',') {
                e.preventDefault();
                this.openSettings();
            }

            // Escape - Close Modals
            if (e.key === 'Escape') {
                this.closeCommandPalette();
                this.closeSettings();
                this.closeSearch();
            }

            // Alt+1-9 - Quick View Switch
            if (e.altKey && e.key >= '1' && e.key <= '9') {
                e.preventDefault();
                const views = ['chat', 'context', 'search', 'workflows', 'suggestions', 'patterns', 'email', 'calendar', 'voice'];
                const index = parseInt(e.key) - 1;
                if (views[index]) {
                    this.switchView(views[index]);
                }
            }

            // Up/Down Arrow - Message History
            if (document.activeElement.id === 'messageInput') {
                if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    if (this.historyIndex < this.messageHistory.length - 1) {
                        this.historyIndex++;
                        document.getElementById('messageInput').value = this.messageHistory[this.historyIndex];
                    }
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    if (this.historyIndex > 0) {
                        this.historyIndex--;
                        document.getElementById('messageInput').value = this.messageHistory[this.historyIndex];
                    } else if (this.historyIndex === 0) {
                        this.historyIndex = -1;
                        document.getElementById('messageInput').value = '';
                    }
                }
            }
        });
    }

    // ==================== Settings Panel ====================

    openSettings() {
        const modal = document.getElementById('settingsModal');
        modal.classList.add('active');

        // Set current values
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === this.settings.theme);
        });

        document.getElementById('fontSize').value = this.settings.fontSize;
        document.getElementById('notificationsEnabled').checked = this.settings.notificationsEnabled;
        document.getElementById('soundEnabled').checked = this.settings.soundEnabled;
        document.getElementById('reduceMotion').checked = this.settings.reduceMotion;
        document.getElementById('highContrast').checked = this.settings.highContrast;
        document.getElementById('debugMode').checked = this.settings.debugMode;
        document.getElementById('autoScroll').checked = this.settings.autoScroll;

        // Setup theme buttons
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.onclick = () => {
                this.setTheme(btn.dataset.theme);
            };
        });

        // Setup setting toggles
        document.getElementById('fontSize').onchange = (e) => {
            this.settings.fontSize = e.target.value;
            this.saveSettings();
            this.applySettings();
        };

        document.getElementById('notificationsEnabled').onchange = (e) => {
            this.settings.notificationsEnabled = e.target.checked;
            this.saveSettings();
            if (e.target.checked) {
                this.requestNotificationPermission();
            }
        };

        document.getElementById('soundEnabled').onchange = (e) => {
            this.settings.soundEnabled = e.target.checked;
            this.saveSettings();
        };

        document.getElementById('reduceMotion').onchange = (e) => {
            this.settings.reduceMotion = e.target.checked;
            this.saveSettings();
            this.applySettings();
        };

        document.getElementById('highContrast').onchange = (e) => {
            this.settings.highContrast = e.target.checked;
            this.saveSettings();
            this.applySettings();
        };

        document.getElementById('debugMode').onchange = (e) => {
            this.settings.debugMode = e.target.checked;
            this.saveSettings();
            this.toggleDebugMode();
        };

        document.getElementById('autoScroll').onchange = (e) => {
            this.settings.autoScroll = e.target.checked;
            this.saveSettings();
        };
    }

    closeSettings() {
        const modal = document.getElementById('settingsModal');
        modal.classList.remove('active');
    }

    setTheme(theme) {
        this.settings.theme = theme;
        this.saveSettings();
        this.applySettings();

        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === theme);
        });

        this.showNotification('Theme Changed', `Switched to ${theme} theme`, 'success');
    }

    toggleDebugMode() {
        if (this.settings.debugMode) {
            console.log('Debug mode enabled');
            console.log('Settings:', this.settings);
            console.log('Messages:', this.messages);
            console.log('Agent Logs:', this.agentLogs);
            this.addAgentLog('info', 'Debug mode enabled', 'SYSTEM');
        } else {
            this.addAgentLog('info', 'Debug mode disabled', 'SYSTEM');
        }
    }

    // ==================== Search ====================

    openSearch() {
        const modal = document.getElementById('searchModal');
        const input = document.getElementById('searchInput');
        modal.classList.add('active');
        input.focus();

        input.oninput = (e) => {
            this.performSearch(e.target.value);
        };
    }

    closeSearch() {
        const modal = document.getElementById('searchModal');
        modal.classList.remove('active');
        document.getElementById('searchInput').value = '';
    }

    performSearch(query) {
        if (!query.trim()) {
            document.getElementById('searchResults').innerHTML = '';
            return;
        }

        const results = [];
        const searchMessages = document.getElementById('searchMessages').checked;
        const searchLogs = document.getElementById('searchLogs').checked;

        // Search messages
        if (searchMessages) {
            this.messages.forEach((msg, index) => {
                if (msg.content.toLowerCase().includes(query.toLowerCase())) {
                    results.push({
                        type: 'Message',
                        content: msg.content,
                        index: index
                    });
                }
            });
        }

        // Search agent logs
        if (searchLogs) {
            this.agentLogs.forEach((log, index) => {
                if (log.message.toLowerCase().includes(query.toLowerCase())) {
                    results.push({
                        type: `Agent Log (${log.agent})`,
                        content: log.message,
                        index: index
                    });
                }
            });
        }

        this.displaySearchResults(results, query);
    }

    displaySearchResults(results, query) {
        const container = document.getElementById('searchResults');
        container.innerHTML = '';

        if (results.length === 0) {
            container.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-muted);">No results found</div>';
            return;
        }

        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'search-result-item';

            const highlighted = result.content.replace(
                new RegExp(this.escapeRegex(query), 'gi'),
                match => `<span class="search-highlight">${match}</span>`
            );

            item.innerHTML = `
                <div class="search-result-type">${result.type}</div>
                <div class="search-result-content">${highlighted}</div>
            `;

            container.appendChild(item);
        });
    }

    // ==================== Export ====================

    clearChat() {
        if (confirm('Are you sure you want to clear all messages?')) {
            document.getElementById('messages').innerHTML = '';
            this.messages = [];
            this.saveChatHistory();
            this.showWelcomeMessage();
            this.showNotification('Chat Cleared', 'All messages removed', 'info');
        }
    }

    clearChatHistory() {
        if (confirm('This will clear your chat history. Continue?')) {
            this.clearChat();
            this.closeSettings();
        }
    }

    exportChat() {
        const format = prompt('Export format? (markdown/json/text)', 'markdown');

        if (format === 'markdown') {
            this.exportAsMarkdown();
        } else if (format === 'json') {
            this.exportAsJSON();
        } else if (format === 'text') {
            this.exportAsText();
        }
    }

    exportAsMarkdown() {
        let content = '# B3 Personal Assistant - Chat Export\n\n';
        content += `**Exported:** ${new Date().toLocaleString()}\n\n`;
        content += '---\n\n';

        this.messages.forEach(msg => {
            const timestamp = new Date(msg.timestamp).toLocaleString();
            content += `### ${msg.sender.toUpperCase()} - ${timestamp}\n\n`;
            content += `${msg.content}\n\n`;
            content += '---\n\n';
        });

        this.downloadFile(content, 'b3-chat-export.md', 'text/markdown');
        this.showNotification('Exported', 'Chat exported as Markdown', 'success');
    }

    exportAsJSON() {
        const data = {
            exported: new Date().toISOString(),
            messages: this.messages,
            metrics: this.metrics,
            agentLogs: this.agentLogs.slice(0, 100)
        };

        const content = JSON.stringify(data, null, 2);
        this.downloadFile(content, 'b3-chat-export.json', 'application/json');
        this.showNotification('Exported', 'Chat exported as JSON', 'success');
    }

    exportAsText() {
        let content = 'B3 Personal Assistant - Chat Export\n';
        content += `Exported: ${new Date().toLocaleString()}\n`;
        content += '='.repeat(60) + '\n\n';

        this.messages.forEach(msg => {
            const timestamp = new Date(msg.timestamp).toLocaleString();
            content += `[${timestamp}] ${msg.sender.toUpperCase()}:\n`;
            content += `${msg.content}\n\n`;
            content += '-'.repeat(60) + '\n\n';
        });

        this.downloadFile(content, 'b3-chat-export.txt', 'text/plain');
        this.showNotification('Exported', 'Chat exported as Text', 'success');
    }

    exportAllData() {
        const data = {
            version: '1.0',
            exported: new Date().toISOString(),
            settings: this.settings,
            messages: this.messages,
            messageHistory: this.messageHistory,
            metrics: this.metrics,
            agentLogs: this.agentLogs,
            performanceData: this.performanceData
        };

        const content = JSON.stringify(data, null, 2);
        this.downloadFile(content, 'b3-full-export.json', 'application/json');
        this.showNotification('Exported', 'All data exported successfully', 'success');
    }

    resetAllSettings() {
        if (confirm('This will reset all settings to defaults. Continue?')) {
            localStorage.removeItem('b3_settings');
            localStorage.removeItem('b3_chat_history');
            location.reload();
        }
    }

    // ==================== Notifications ====================

    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    showNotification(title, message, type = 'info') {
        const container = document.getElementById('notificationContainer');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;

        const icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        };

        notification.innerHTML = `
            <div class="notification-icon">${icons[type]}</div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;

        container.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 5000);

        // Browser notification
        if (this.settings.notificationsEnabled && 'Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/icon.png'
            });
        }

        // Sound effect
        if (this.settings.soundEnabled) {
            this.playNotificationSound();
        }
    }

    playNotificationSound() {
        // Create a simple beep sound
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
    }

    // ==================== Loading States ====================

    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loadingOverlay');
        const text = overlay.querySelector('.loading-text');
        text.textContent = message;
        overlay.style.display = 'flex';
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'none';
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
                const view = e.target.dataset.view || e.target.parentElement.dataset.view;
                if (view) {
                    this.switchView(view);
                }
            });
        });
    }

    // ==================== Utilities ====================

    togglePanel(panelId) {
        const panel = document.getElementById(panelId);
        if (panel.style.display === 'none') {
            panel.style.display = 'flex';
        } else {
            panel.style.display = 'none';
        }
    }

    copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
        } else {
            // Fallback
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }

    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    escapeRegex(text) {
        return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 Starting B3 Personal Assistant...');
    window.b3 = new B3Assistant();
    console.log('✅ B3 Assistant ready!');
});
