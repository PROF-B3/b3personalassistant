"""
Agent Panel

AI agent chat interface with agent selection and quick actions.
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QComboBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QTextCursor, QFont


class AgentWorker(QThread):
    """Worker thread for agent processing to avoid blocking UI."""

    finished = pyqtSignal(str)  # response
    error = pyqtSignal(str)     # error message

    def __init__(self, orchestrator, agent_name: str, message: str, context: Dict):
        super().__init__()
        self.orchestrator = orchestrator
        self.agent_name = agent_name
        self.message = message
        self.context = context

    def run(self):
        """Process message with agent."""
        try:
            # Get agent
            agent = self.orchestrator.agents.get(self.agent_name.lower())

            if agent:
                # Process with specific agent
                response = agent.act(self.message, self.context)
            else:
                # Use orchestrator for general processing
                response = self.orchestrator.process_request(self.message)

            self.finished.emit(response)

        except Exception as e:
            self.error.emit(str(e))


class AgentPanel(QWidget):
    """
    Agent chat panel for interacting with AI agents.

    Features:
    - Agent selector dropdown
    - Chat history display
    - Message input
    - Quick action buttons (context-aware)
    - Async processing to keep UI responsive
    """

    # Signals
    message_sent = pyqtSignal(str, str)  # agent, message
    response_received = pyqtSignal(str, str)  # agent, response

    def __init__(self, orchestrator, parent=None):
        super().__init__(parent)

        self.orchestrator = orchestrator
        self.current_agent = "Alpha"
        self.context = {}
        self.worker = None

        self._create_ui()
        self._setup_agents()

    def _create_ui(self):
        """Create the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()

        header = QLabel("🤖 AI Agents")
        header.setStyleSheet("font-weight: bold; padding: 4px;")
        header_layout.addWidget(header)

        header_layout.addStretch()

        # Agent selector
        self.agent_selector = QComboBox()
        self.agent_selector.setMinimumWidth(120)
        self.agent_selector.currentTextChanged.connect(self._on_agent_changed)
        header_layout.addWidget(self.agent_selector)

        layout.addLayout(header_layout)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(200)

        # Set font
        font = QFont("Consolas, Monaco, monospace", 10)
        self.chat_display.setFont(font)

        layout.addWidget(self.chat_display, stretch=1)

        # Quick actions (context-aware buttons)
        self.quick_actions_frame = QFrame()
        self.quick_actions_layout = QHBoxLayout(self.quick_actions_frame)
        self.quick_actions_layout.setContentsMargins(0, 0, 0, 0)
        self.quick_actions_layout.setSpacing(4)
        layout.addWidget(self.quick_actions_frame)

        # Input area
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message...")
        self.message_input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.message_input, stretch=1)

        self.send_button = QPushButton("Send")
        self.send_button.setProperty("primary", True)
        self.send_button.clicked.connect(self._send_message)
        self.send_button.setMinimumWidth(80)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Welcome message
        self._add_system_message("Welcome! Select an agent and start chatting.")

    def _setup_agents(self):
        """Setup agent list."""
        agents = [
            ("Alpha (Α)", "Chief Coordinator"),
            ("Beta (Β)", "Research Analyst"),
            ("Gamma (Γ)", "Knowledge Manager"),
            ("Delta (Δ)", "Task Coordinator"),
            ("Epsilon (Ε)", "Creative Director"),
            ("Zeta (Ζ)", "Code Architect"),
            ("Eta (Η)", "Evolution Engineer")
        ]

        for name, description in agents:
            self.agent_selector.addItem(name, description)

        self.agent_selector.setCurrentIndex(0)

    def _on_agent_changed(self, agent_text: str):
        """Handle agent selection change."""
        # Extract agent name (remove Greek letter)
        self.current_agent = agent_text.split()[0]
        self._add_system_message(f"Switched to {agent_text}")

        # Update quick actions based on agent
        self._update_quick_actions()

    def _update_quick_actions(self):
        """Update quick action buttons based on current agent and context."""
        # Clear existing buttons
        while self.quick_actions_layout.count():
            item = self.quick_actions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add agent-specific quick actions
        actions = self._get_agent_quick_actions()

        for action_text, action_func in actions:
            btn = QPushButton(action_text)
            btn.clicked.connect(action_func)
            self.quick_actions_layout.addWidget(btn)

        self.quick_actions_layout.addStretch()

    def _get_agent_quick_actions(self):
        """Get quick actions for current agent."""
        agent_name = self.current_agent.lower()

        actions_map = {
            'alpha': [
                ("Help", lambda: self._quick_send("Help me with my current task")),
                ("Status", lambda: self._quick_send("What's my current status?")),
            ],
            'beta': [
                ("Search Papers", lambda: self._quick_send("Search for recent papers")),
                ("Summarize", lambda: self._quick_send("Summarize the current document")),
            ],
            'gamma': [
                ("Create Note", lambda: self._quick_send("Create a note from this")),
                ("Find Related", lambda: self._quick_send("Find related notes")),
            ],
            'delta': [
                ("Show Tasks", lambda: self._quick_send("Show my tasks")),
                ("Create Task", lambda: self._quick_send("Create a new task")),
            ],
            'epsilon': [
                ("Improve Text", lambda: self._quick_send("Improve this text")),
                ("Generate Ideas", lambda: self._quick_send("Generate creative ideas")),
            ],
            'zeta': [
                ("Review Code", lambda: self._quick_send("Review this code")),
                ("Optimize", lambda: self._quick_send("Suggest optimizations")),
            ],
            'eta': [
                ("Analyze", lambda: self._quick_send("Analyze system performance")),
                ("Suggest", lambda: self._quick_send("Suggest improvements")),
            ]
        }

        return actions_map.get(agent_name, [])

    def _quick_send(self, message: str):
        """Send a quick action message."""
        self.message_input.setText(message)
        self._send_message()

    def _send_message(self):
        """Send message to current agent."""
        message = self.message_input.text().strip()
        if not message:
            return

        # Clear input
        self.message_input.clear()

        # Add user message to chat
        self._add_user_message(message)

        # Disable input while processing
        self._set_input_enabled(False)

        # Process with agent in background thread
        self.worker = AgentWorker(
            self.orchestrator,
            self.current_agent,
            message,
            self.context
        )
        self.worker.finished.connect(self._on_response_received)
        self.worker.error.connect(self._on_error)
        self.worker.start()

        # Emit signal
        self.message_sent.emit(self.current_agent, message)

    @pyqtSlot(str)
    def _on_response_received(self, response: str):
        """Handle agent response."""
        self._add_agent_message(response)
        self._set_input_enabled(True)
        self.message_input.setFocus()

        # Emit signal
        self.response_received.emit(self.current_agent, response)

    @pyqtSlot(str)
    def _on_error(self, error_msg: str):
        """Handle error."""
        self._add_error_message(f"Error: {error_msg}")
        self._set_input_enabled(True)

    def _set_input_enabled(self, enabled: bool):
        """Enable/disable input controls."""
        self.message_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        self.agent_selector.setEnabled(enabled)

        if not enabled:
            self.send_button.setText("Processing...")
        else:
            self.send_button.setText("Send")

    def _add_user_message(self, message: str):
        """Add user message to chat display."""
        self.chat_display.append(f'<div style="color: #4A9EFF;"><b>You:</b> {message}</div>')
        self._scroll_to_bottom()

    def _add_agent_message(self, message: str):
        """Add agent message to chat display."""
        agent_name = self.current_agent
        self.chat_display.append(f'<div style="color: #4EC9B0;"><b>{agent_name}:</b> {message}</div>')
        self.chat_display.append("")  # Add spacing
        self._scroll_to_bottom()

    def _add_system_message(self, message: str):
        """Add system message to chat display."""
        self.chat_display.append(f'<div style="color: #858585;"><i>{message}</i></div>')
        self._scroll_to_bottom()

    def _add_error_message(self, message: str):
        """Add error message to chat display."""
        self.chat_display.append(f'<div style="color: #F48771;"><b>Error:</b> {message}</div>')
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        """Scroll chat to bottom."""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def set_context(self, context: Dict[str, Any]):
        """Set context for agent interactions."""
        self.context = context

        # Update quick actions based on new context
        self._update_quick_actions()

    def update_for_mode(self, mode: str):
        """Update panel based on current mode."""
        # Auto-select appropriate agent for mode
        mode_agents = {
            'research': 'Beta',
            'video': 'Epsilon',
            'writing': 'Epsilon'
        }

        suggested_agent = mode_agents.get(mode, 'Alpha')

        # Find and select agent
        for i in range(self.agent_selector.count()):
            if self.agent_selector.itemText(i).startswith(suggested_agent):
                self.agent_selector.setCurrentIndex(i)
                break

    def clear_chat(self):
        """Clear chat history."""
        self.chat_display.clear()
        self._add_system_message("Chat cleared.")

    def focus_input(self):
        """Focus the message input."""
        self.message_input.setFocus()


class CompactAgentPanel(QWidget):
    """
    Compact agent selector for sidebar.

    Just shows agent list with active indicator.
    """

    agent_selected = pyqtSignal(str)  # agent name

    def __init__(self, parent=None):
        super().__init__(parent)

        self._create_ui()

    def _create_ui(self):
        """Create UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # Header
        header = QLabel("Agents")
        header.setStyleSheet("font-weight: bold; padding: 4px;")
        layout.addWidget(header)

        # Agent buttons
        self.agent_buttons = []

        agents = [
            ("Alpha", "Α"),
            ("Beta", "Β"),
            ("Gamma", "Γ"),
            ("Delta", "Δ"),
            ("Epsilon", "Ε"),
            ("Zeta", "Ζ"),
            ("Eta", "Η")
        ]

        for name, symbol in agents:
            btn = QPushButton(f"{symbol} {name}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=name: self._on_agent_clicked(n))
            layout.addWidget(btn)
            self.agent_buttons.append((name, btn))

        # Select first agent by default
        if self.agent_buttons:
            self.agent_buttons[0][1].setChecked(True)

        layout.addStretch()

    def _on_agent_clicked(self, agent_name: str):
        """Handle agent button click."""
        # Uncheck all other buttons
        for name, btn in self.agent_buttons:
            btn.setChecked(name == agent_name)

        self.agent_selected.emit(agent_name)

    def set_active_agent(self, agent_name: str):
        """Set the active agent."""
        for name, btn in self.agent_buttons:
            btn.setChecked(name == agent_name)
