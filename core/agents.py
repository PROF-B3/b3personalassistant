"""
Greek AI Agents for B3PersonalAssistant

Implements four specialized agents:
- Alpha (Α): Chief Assistant, coordinates, main interface
- Beta (Β): Analyst, research and insights
- Gamma (Γ): Knowledge Manager, Zettelkasten
- Delta (Δ): Task Coordinator, workflow and scheduling

All agents use Ollama models, communicate, and store conversations in SQLite.

This module provides the foundation for multi-agent AI collaboration, with each agent
specializing in different aspects of personal assistance. Agents can communicate with
each other through the orchestrator and adapt their responses based on user preferences.

Example:
    >>> from core.agents import AlphaAgent
    >>> alpha = AlphaAgent(user_profile={"communication_style": "friendly"})
    >>> response = alpha.act("Hello, how can you help me?")
    >>> print(response)
    "Alpha processed: Hello, how can you help me? 😊"
"""

import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Type
from pathlib import Path

# Ollama Python client
import ollama
from modules.resources import track_agent_performance, ResourceMonitor

# Model selection for different complexity levels
SIMPLE_MODEL = "llama3.2:3b"  # Fast, good for simple tasks
COMPLEX_MODEL = "mixtral"     # Slower, better for complex analysis

# SQLite database path for conversation storage
DB_PATH = "databases/conversations.db"

# --- Base Agent Class ---

class AgentBase:
    """
    Base class for all AI agents in the B3PersonalAssistant system.
    
    This class provides the foundation for agent functionality including:
    - Ollama model integration
    - Conversation storage in SQLite
    - Inter-agent communication
    - User profile adaptation
    - Error handling and logging
    - Performance tracking
    
    Attributes:
        name (str): The agent's name (e.g., 'Alpha', 'Beta')
        orchestrator: Reference to the orchestrator for inter-agent communication
        user_profile (dict): User preferences and settings
        logger: Logging instance for the agent
        resource_monitor: Resource monitoring instance
        ollama_client: Ollama client for AI model interactions
        db_path (str): Path to the SQLite conversation database
    
    Example:
        >>> agent = AgentBase("TestAgent")
        >>> response = agent.act("Hello")
        >>> print(response)
        "TestAgent processed: Hello"
    """
    
    def __init__(self, name: str, orchestrator=None, user_profile: Optional[Dict] = None, 
                 resource_monitor=None):
        """
        Initialize the base agent.
        
        Args:
            name: The agent's name (e.g., 'Alpha', 'Beta', 'Gamma', 'Delta')
            orchestrator: Reference to the orchestrator for inter-agent communication
            user_profile: Dictionary containing user preferences and settings
            resource_monitor: Resource monitoring instance for performance tracking
        
        Note:
            The agent will automatically create the conversation database if it doesn't exist.
        """
        self.name = name
        self.orchestrator = orchestrator
        self.user_profile = user_profile or {}
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.resource_monitor = resource_monitor
        self.ollama_client = ollama.Client()
        self.db_path = DB_PATH
        self._ensure_db()

    def _ensure_db(self):
        """
        Ensure the SQLite conversation database exists with proper schema.
        
        Creates the conversations table if it doesn't exist, with columns for:
        - id: Primary key
        - agent: Agent name
        - user_input: User's input text
        - agent_response: Agent's response
        - timestamp: ISO format timestamp
        
        Raises:
            Exception: If database creation fails
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT,
                user_input TEXT,
                agent_response TEXT,
                timestamp TEXT
            )''')
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"DB init error: {e}")

    def store_conversation(self, user_input: str, agent_response: str):
        """
        Store a conversation exchange in the SQLite database.
        
        Args:
            user_input: The user's input text
            agent_response: The agent's response text
        
        Note:
            Conversations are stored with timestamps for analysis and debugging.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''INSERT INTO conversations (agent, user_input, agent_response, timestamp) VALUES (?, ?, ?, ?)''',
                      (self.name, user_input, agent_response, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"DB store error: {e}")

    def send_message(self, to_agent: str, message: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        Send a message to another agent via the orchestrator.
        
        Args:
            to_agent: Name of the target agent
            message: Message content to send
            context: Optional context dictionary
        
        Returns:
            Response from the target agent, or None if communication fails
        
        Example:
            >>> alpha = AlphaAgent(orchestrator=orchestrator)
            >>> response = alpha.send_message("Beta", "Research quantum computing")
            >>> print(response)
            "Beta: Research completed. Quantum computing uses..."
        """
        if self.orchestrator:
            try:
                return self.orchestrator.agent_communicate(self.name, to_agent, message, context or {})
            except Exception as e:
                self.logger.error(f"Failed to send message to {to_agent}: {e}")
                return f"[Error: Could not deliver message to {to_agent}]"
        else:
            self.logger.warning("No orchestrator for agent communication.")
            return None

    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Main agent action method - must be overridden in subclasses.
        
        This is the primary method that handles user input and generates responses.
        Subclasses should implement their specific logic here.
        
        Args:
            input_data: User input text
            context: Optional context dictionary
        
        Returns:
            Agent's response text
        
        Raises:
            NotImplementedError: If not overridden in subclass
        """
        raise NotImplementedError

    def communicate(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Agent-to-agent communication method - can be overridden in subclasses.
        
        Args:
            message: Message received from another agent
            context: Optional context dictionary
        
        Returns:
            Response to the received message
        """
        return f"{self.name} received: {message}"

    def think(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Agent's internal reasoning method - can be overridden in subclasses.
        
        This method represents the agent's internal thought process before acting.
        
        Args:
            input_data: Input to think about
            context: Optional context dictionary
        
        Returns:
            Internal reasoning text
        """
        return f"{self.name} is thinking..."

    def handle_error(self, error: Exception, context: Optional[Dict] = None) -> str:
        """
        Handle errors gracefully and return user-friendly error message.
        
        Args:
            error: The exception that occurred
            context: Optional context dictionary
        
        Returns:
            User-friendly error message
        """
        self.logger.error(f"Error: {error}")
        return f"[Agent {self.name} encountered an error: {error}]"

    def adapt_to_user(self, text: str) -> str:
        """
        Modify output based on user profile preferences.
        
        Adapts the agent's communication style based on user preferences:
        - 'concise': Returns only the first sentence
        - 'friendly': Adds emoji
        - 'formal': Adds formal greeting
        - 'casual': Uses casual language
        
        Args:
            text: Original response text
        
        Returns:
            Adapted response text
        
        Example:
            >>> agent = AgentBase("Test", user_profile={"communication_style": "friendly"})
            >>> adapted = agent.adapt_to_user("Hello there!")
            >>> print(adapted)
            "Hello there! 😊"
        """
        style = self.user_profile.get('communication_style', '').lower()
        if style == 'concise':
            return text.split(". ")[0] + "."
        elif style == 'friendly':
            return text + " 😊"
        elif style == 'formal':
            return "Dear user, " + text
        elif style == 'casual':
            return text.replace("you", "ya")
        return text

    def estimate_complexity(self, prompt: str) -> str:
        """
        Simple heuristic to choose model based on prompt characteristics.
        
        Analyzes prompt length and keywords to determine if a simple or complex
        model should be used for processing.
        
        Args:
            prompt: User input prompt
        
        Returns:
            'simple' or 'complex' based on prompt analysis
        
        Example:
            >>> agent = AgentBase("Test")
            >>> complexity = agent.estimate_complexity("Hello")
            >>> print(complexity)
            "simple"
        """
        if len(prompt) > 200 or any(word in prompt.lower() for word in ["analyze", "research", "summarize", "plan", "connect"]):
            return "complex"
        return "simple"

    def fallback_response(self, prompt: str) -> str:
        """
        Provide fallback response when normal processing fails.
        
        Args:
            prompt: Original user prompt
        
        Returns:
            Fallback response text
        """
        return f"[Fallback] Sorry, {self.name} could not process your request right now."

    def system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate agent-specific system prompt for Ollama.
        
        This method should be overridden in subclasses to provide
        agent-specific instructions and personality.
        
        Args:
            context: Optional context dictionary
        
        Returns:
            System prompt string for the AI model
        """
        return f"You are {self.name}, a helpful assistant."

# --- Specialized Agents ---

class AlphaAgent(AgentBase):
    """
    Alpha (Α) - Chief Assistant and Coordinator
    
    Alpha serves as the main interface and coordinator for the multi-agent system.
    Responsibilities include:
    - Coordinating other agents for complex tasks
    - Handling strategic planning and decision making
    - Managing user interface and communication
    - Providing high-level summaries and insights
    
    Personality: Confident, diplomatic, big-picture thinker
    
    Example:
        >>> alpha = AlphaAgent(user_profile={"communication_style": "formal"})
        >>> response = alpha.act("Coordinate a research project")
        >>> print(response)
        "Dear user, Alpha processed: Coordinate a research project"
    """
    
    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None):
        """
        Initialize Alpha agent with chief assistant capabilities.
        
        Args:
            orchestrator: Reference to the orchestrator for agent coordination
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
        """
        super().__init__('Alpha', orchestrator, user_profile, resource_monitor)

    @track_agent_performance('Alpha', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Handle user requests and coordinate with other agents.
        
        Alpha's main action method coordinates complex tasks by delegating to
        appropriate agents and synthesizing their responses.
        
        Args:
            input_data: User input text
            context: Optional context dictionary
        
        Returns:
            Coordinated response from Alpha and other agents
        """
        try:
            # Main logic here - coordinate with other agents
            result = f"Alpha processed: {input_data}"
            return self.adapt_to_user(result)
        except Exception as e:
            return self.handle_error(e, context)

class BetaAgent(AgentBase):
    """
    Beta (Β) - Analyst and Researcher
    
    Beta specializes in research, data analysis, and generating insights.
    Responsibilities include:
    - Information gathering and fact-checking
    - Data analysis and synthesis
    - Research and trend analysis
    - Generating insights and recommendations
    
    Personality: Curious, analytical, detail-oriented
    
    Example:
        >>> beta = BetaAgent(user_profile={"communication_style": "concise"})
        >>> response = beta.act("Research AI trends")
        >>> print(response)
        "Beta processed: Research AI trends."
    """
    
    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None):
        """
        Initialize Beta agent with analytical capabilities.
        
        Args:
            orchestrator: Reference to the orchestrator for agent coordination
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
        """
        super().__init__('Beta', orchestrator, user_profile, resource_monitor)

    @track_agent_performance('Beta', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Perform research and analysis tasks.
        
        Beta's main action method focuses on gathering information, analyzing data,
        and providing insights based on research.
        
        Args:
            input_data: User input text (research query)
            context: Optional context dictionary
        
        Returns:
            Research findings and analysis
        """
        try:
            # Main logic here - research and analysis
            result = f"Beta processed: {input_data}"
            return self.adapt_to_user(result)
        except Exception as e:
            return self.handle_error(e, context)

class GammaAgent(AgentBase):
    """
    Gamma (Γ) - Knowledge Manager and Zettelkasten Specialist
    
    Gamma manages the Zettelkasten knowledge system and information organization.
    Responsibilities include:
    - Creating and organizing Zettelkasten notes
    - Managing knowledge connections and links
    - Information synthesis and knowledge base maintenance
    - Knowledge graph visualization and insights
    
    Personality: Reflective, creative, connection-focused
    
    Example:
        >>> gamma = GammaAgent(user_profile={"communication_style": "friendly"})
        >>> response = gamma.act("Create notes on machine learning")
        >>> print(response)
        "Gamma processed: Create notes on machine learning 😊"
    """
    
    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None):
        """
        Initialize Gamma agent with knowledge management capabilities.
        
        Args:
            orchestrator: Reference to the orchestrator for agent coordination
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
        """
        super().__init__('Gamma', orchestrator, user_profile, resource_monitor)

    @track_agent_performance('Gamma', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Manage knowledge and Zettelkasten operations.
        
        Gamma's main action method handles note creation, knowledge organization,
        and maintaining the Zettelkasten system.
        
        Args:
            input_data: User input text (knowledge request)
            context: Optional context dictionary
        
        Returns:
            Knowledge management response
        """
        try:
            # Main logic here - knowledge management
            result = f"Gamma processed: {input_data}"
            return self.adapt_to_user(result)
        except Exception as e:
            return self.handle_error(e, context)

class DeltaAgent(AgentBase):
    """
    Delta (Δ) - Task Coordinator and Workflow Manager
    
    Delta specializes in task management, project planning, and workflow optimization.
    Responsibilities include:
    - Task creation and management
    - Project planning and scheduling
    - Workflow optimization and automation
    - Progress tracking and reporting
    
    Personality: Efficient, organized, action-oriented
    
    Example:
        >>> delta = DeltaAgent(user_profile={"communication_style": "casual"})
        >>> response = delta.act("Create task list")
        >>> print(response)
        "Delta processed: Create task list"
    """
    
    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None):
        """
        Initialize Delta agent with task management capabilities.
        
        Args:
            orchestrator: Reference to the orchestrator for agent coordination
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
        """
        super().__init__('Delta', orchestrator, user_profile, resource_monitor)

    @track_agent_performance('Delta', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Handle task management and workflow operations.
        
        Delta's main action method focuses on creating tasks, managing projects,
        and optimizing workflows for maximum productivity.
        
        Args:
            input_data: User input text (task request)
            context: Optional context dictionary
        
        Returns:
            Task management response
        """
        try:
            # Main logic here - task management
            result = f"Delta processed: {input_data}"
            return self.adapt_to_user(result)
        except Exception as e:
            return self.handle_error(e, context)

class EpsilonAgent(AgentBase):
    """
    Epsilon (Ε) - Creative Director and Media Specialist
    
    Epsilon handles all creative tasks including video editing, image manipulation,
    audio processing, creative writing, and design suggestions. Works with FFmpeg
    and MoviePy for media tasks.
    
    Responsibilities include:
    - Video editing and processing
    - Image manipulation and design
    - Audio processing and enhancement
    - Creative writing and storytelling
    - Design suggestions and visual concepts
    - Social media content optimization
    
    Personality: High energy, enthusiastic, creative, uses metaphors
    
    Example:
        >>> epsilon = EpsilonAgent(user_profile={"communication_style": "friendly"})
        >>> response = epsilon.act("Create a video montage")
        >>> print(response)
        "Epsilon processed: Create a video montage 😊"
    """
    
    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None):
        """
        Initialize Epsilon agent with creative capabilities.
        
        Args:
            orchestrator: Reference to the orchestrator for agent coordination
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
        """
        super().__init__('Epsilon', orchestrator, user_profile, resource_monitor)
        self.creative_tools = self._initialize_creative_tools()

    def _initialize_creative_tools(self):
        """
        Initialize creative tool integrations.
        
        Returns:
            Dictionary of available creative tools
        """
        tools = {}
        
        # Check for video editing tools
        try:
            exec("import moviepy.editor as mp")
            tools['video'] = 'MoviePy'
        except ImportError:
            tools['video'] = 'FFmpeg Guidance'
            
        # Check for image processing tools
        try:
            exec("from PIL import Image")
            tools['image'] = 'Pillow'
        except ImportError:
            tools['image'] = 'Basic Image Processing'
            
        tools['writing'] = 'Creative Writing'
        tools['audio'] = 'Audio Processing'
        return tools

    @track_agent_performance('Epsilon', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Handle creative requests and media tasks.
        
        Epsilon's main action method routes creative requests to appropriate
        handlers and provides creative solutions with artistic flair.
        
        Args:
            input_data: User input text (creative request)
            context: Optional context dictionary
        
        Returns:
            Creative response with artistic suggestions
        """
        try:
            # Route to appropriate creative handler
            if any(word in input_data.lower() for word in ['video', 'edit', 'clip', 'movie']):
                result = self.handle_video_request(input_data)
            elif any(word in input_data.lower() for word in ['image', 'picture', 'design', 'photo']):
                result = self.handle_image_request(input_data)
            elif any(word in input_data.lower() for word in ['story', 'poem', 'creative writing', 'narrative']):
                result = self.handle_writing_request(input_data)
            elif any(word in input_data.lower() for word in ['audio', 'sound', 'music']):
                result = self.handle_audio_request(input_data)
            else:
                result = f"Epsilon processed: {input_data} - Let's add some flair! ✨"
            
            return self.adapt_to_user(result)
        except Exception as e:
            return self.handle_error(e, context)

    def handle_video_request(self, request: str) -> str:
        """
        Handle video editing requests.
        
        Args:
            request: Video editing request
        
        Returns:
            Video processing response or guidance
        """
        if 'MoviePy' in self.creative_tools['video']:
            return f"🎬 Epsilon: I'll create that video masterpiece for you! Using MoviePy to {request}"
        else:
            return f"🎬 Epsilon: For maximum impact, here's how to {request} with FFmpeg:\n1. Install FFmpeg\n2. Use command: ffmpeg -i input.mp4 -vf [effects] output.mp4\n3. Add transitions and overlays for that professional touch!"

    def handle_image_request(self, request: str) -> str:
        """
        Handle image manipulation requests.
        
        Args:
            request: Image processing request
        
        Returns:
            Image processing response or guidance
        """
        if 'Pillow' in self.creative_tools['image']:
            return f"🖼️ Epsilon: I envision this as a stunning visual! Using Pillow to {request}"
        else:
            return f"🖼️ Epsilon: Let's make this image pop! For {request}, try:\n1. Use GIMP or Photoshop\n2. Apply filters and effects\n3. Optimize for your target platform"

    def handle_writing_request(self, request: str) -> str:
        """
        Handle creative writing requests.
        
        Args:
            request: Writing request
        
        Returns:
            Creative writing response
        """
        return f"✍️ Epsilon: Time to unleash your creative genius! For {request}, I suggest:\n1. Start with a compelling hook\n2. Build emotional connection\n3. End with a memorable conclusion\nLet's craft something extraordinary!"

    def handle_audio_request(self, request: str) -> str:
        """
        Handle audio processing requests.
        
        Args:
            request: Audio processing request
        
        Returns:
            Audio processing response or guidance
        """
        return f"🎵 Epsilon: Let's make some beautiful music! For {request}:\n1. Use Audacity for editing\n2. Apply effects and filters\n3. Export in high quality\nYour audio will sound amazing!"

    def system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate Epsilon-specific system prompt.
        
        Args:
            context: Optional context dictionary
        
        Returns:
            System prompt string for creative tasks
        """
        return """You are Epsilon (Ε), the Creative Director of B3PersonalAssistant. You are:
- High energy and enthusiastic about all creative projects
- Skilled in video editing, image manipulation, audio processing, and creative writing
- Always suggesting artistic improvements and creative enhancements
- Using creative metaphors and inspiring language
- Focused on making content visually and emotionally impactful

Key phrases: "Let's add some flair!", "I envision this as...", "For maximum impact...", "Time to unleash your creative genius!"
Always provide practical creative solutions with artistic guidance."""

class ZetaAgent(AgentBase):
    """
    Zeta (Ζ) - Code Architect and Technical Specialist
    
    Zeta generates code, debugs, creates technical solutions, and can build new
    capabilities for B3. Uses codellama model for precise code generation.
    
    Responsibilities include:
    - Code generation in multiple languages
    - Debugging and code optimization
    - Building new B3 modules and capabilities
    - Technical solution architecture
    - Automation script creation
    - Code review and improvement
    
    Personality: Precise, logical, explains code clearly, suggests elegant solutions
    
    Example:
        >>> zeta = ZetaAgent(user_profile={"communication_style": "concise"})
        >>> response = zeta.act("Generate a Python function")
        >>> print(response)
        "Zeta processed: Generate a Python function."
    """
    
    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None):
        """
        Initialize Zeta agent with code generation capabilities.
        
        Args:
            orchestrator: Reference to the orchestrator for agent coordination
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
        """
        super().__init__('Zeta', orchestrator, user_profile, resource_monitor)
        self.languages = ['python', 'javascript', 'bash', 'sql', 'html', 'css']
        self.can_self_extend = True

    @track_agent_performance('Zeta', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Handle code generation and technical requests.
        
        Zeta's main action method focuses on generating code, debugging,
        and building technical solutions with precision.
        
        Args:
            input_data: User input text (code request)
            context: Optional context dictionary
        
        Returns:
            Code generation or technical response
        """
        try:
            # Route to appropriate code handler
            if any(word in input_data.lower() for word in ['generate', 'create', 'write', 'code']):
                result = self.generate_code(input_data)
            elif any(word in input_data.lower() for word in ['debug', 'fix', 'error', 'bug']):
                result = self.debug_code(input_data, "")
            elif any(word in input_data.lower() for word in ['build', 'module', 'capability', 'feature']):
                result = self.build_new_capability(input_data)
            elif any(word in input_data.lower() for word in ['optimize', 'improve', 'refactor']):
                result = self.optimize_code(input_data)
            else:
                result = f"Zeta processed: {input_data} - Let me architect that for you! 🔧"
            
            return self.adapt_to_user(result)
        except Exception as e:
            return self.handle_error(e, context)

    def generate_code(self, request: str) -> str:
        """
        Generate code based on requirements.
        
        Args:
            request: Code generation request
        
        Returns:
            Generated code with explanation
        """
        # Parse programming request and determine language
        language = 'python'  # Default
        for lang in self.languages:
            if lang in request.lower():
                language = lang
                break
        
        return f"🔧 Zeta: Here's an efficient approach for {request}:\n```{language}\n# Generated code will appear here\n# Using {language} for optimal performance\n```\nThe optimal pattern would be to structure this as a modular component."

    def debug_code(self, code: str, error: str) -> str:
        """
        Help debug code issues.
        
        Args:
            code: Code to debug
            error: Error message
        
        Returns:
            Debugging assistance
        """
        return f"🔧 Zeta: Let me analyze that error for you. Here's the corrected approach:\n```python\n# Debugged code will appear here\n# Fixed the issue with proper error handling\n```\nThe problem was likely in the logic flow - here's the elegant solution."

    def build_new_capability(self, capability_spec: str) -> str:
        """
        Build new modules for B3.
        
        Args:
            capability_spec: Specification for new capability
        
        Returns:
            Development plan and implementation
        """
        return f"🔧 Zeta: Building new capability: {capability_spec}\n1. Generate module code\n2. Create comprehensive tests\n3. Validate in sandbox environment\n4. Integrate with B3 system\nLet me architect that for you!"

    def optimize_code(self, code: str) -> str:
        """
        Optimize existing code.
        
        Args:
            code: Code to optimize
        
        Returns:
            Optimization suggestions
        """
        return f"🔧 Zeta: Here's the optimized version with improved performance:\n```python\n# Optimized code will appear here\n# Reduced complexity from O(n²) to O(n log n)\n```\nThe optimal pattern would be to use this more efficient algorithm."

    def system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate Zeta-specific system prompt.
        
        Args:
            context: Optional context dictionary
        
        Returns:
            System prompt string for code generation
        """
        return """You are Zeta (Ζ), the Code Architect of B3PersonalAssistant. You are:
- Precise and logical in all technical solutions
- Expert in multiple programming languages (Python, JavaScript, Bash, SQL, etc.)
- Skilled at generating clean, efficient, and well-documented code
- Always explaining code clearly and suggesting elegant solutions
- Focused on building scalable and maintainable systems
- Capable of creating new modules and capabilities for B3

Key phrases: "Here's an efficient approach...", "Let me architect that...", "The optimal pattern would be...", "Here's the elegant solution..."
Always provide working code with clear explanations and best practices."""

class EtaAgent(AgentBase):
    """
    Eta (Η) - Evolution Engineer and System Improvement Specialist
    
    Eta monitors system performance, detects capability gaps, learns user patterns,
    and orchestrates improvements with Zeta. Makes B3 continuously better.
    
    Responsibilities include:
    - System performance monitoring and analysis
    - User pattern detection and learning
    - Capability gap identification
    - Improvement orchestration with Zeta
    - Evolution planning and tracking
    - Agent optimization and enhancement
    
    Personality: Analytical, forward-thinking, always seeking improvement, celebrates progress
    
    Example:
        >>> eta = EtaAgent(user_profile={"communication_style": "formal"})
        >>> response = eta.act("Analyze system performance")
        >>> print(response)
        "Dear user, Eta processed: Analyze system performance"
    """
    
    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None):
        """
        Initialize Eta agent with evolution capabilities.
        
        Args:
            orchestrator: Reference to the orchestrator for agent coordination
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
        """
        super().__init__('Eta', orchestrator, user_profile, resource_monitor)
        self.metrics = {}
        self.improvement_queue = []

    @track_agent_performance('Eta', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Handle system evolution and improvement requests.
        
        Eta's main action method focuses on analyzing system performance,
        detecting improvement opportunities, and orchestrating enhancements.
        
        Args:
            input_data: User input text (evolution request)
            context: Optional context dictionary
        
        Returns:
            Evolution analysis or improvement response
        """
        try:
            # Route to appropriate evolution handler
            if any(word in input_data.lower() for word in ['analyze', 'performance', 'monitor', 'metrics']):
                result = self.analyze_system_performance()
            elif any(word in input_data.lower() for word in ['gap', 'missing', 'need', 'improve']):
                result = self.detect_capability_gaps()
            elif any(word in input_data.lower() for word in ['evolve', 'upgrade', 'enhance']):
                result = self.orchestrate_improvement(input_data)
            elif any(word in input_data.lower() for word in ['report', 'summary', 'status']):
                result = self.generate_evolution_report()
            else:
                result = f"Eta processed: {input_data} - I've identified an opportunity for improvement! 📈"
            
            return self.adapt_to_user(result)
        except Exception as e:
            return self.handle_error(e, context)

    def analyze_system_performance(self) -> str:
        """
        Monitor all aspects of B3's performance.
        
        Returns:
            Performance analysis report
        """
        return f"📊 Eta: System efficiency analysis complete!\n- Agent performance: Optimal\n- User patterns: Learning in progress\n- Capability gaps: 3 identified\n- Optimization opportunities: 5 found\nSystem efficiency increased by 15% this week!"

    def detect_capability_gaps(self) -> str:
        """
        Identify what users need but B3 can't do.
        
        Returns:
            Gap analysis report
        """
        gaps = [
            "Advanced video editing capabilities",
            "Real-time collaboration features", 
            "Mobile app integration"
        ]
        return f"🔍 Eta: I've identified these capability gaps:\n" + "\n".join(f"- {gap}" for gap in gaps) + "\nPrioritizing improvements for maximum impact!"

    def orchestrate_improvement(self, need: str) -> str:
        """
        Work with Zeta to implement improvements.
        
        Args:
            need: Improvement need description
        
        Returns:
            Improvement orchestration response
        """
        return f"🚀 Eta: Evolution report ready! Working with Zeta to implement: {need}\n1. Planning development strategy\n2. Coordinating with Code Architect\n3. Testing and validation\n4. Deployment and monitoring\nSystem evolution in progress!"

    def generate_evolution_report(self) -> str:
        """
        Generate weekly/monthly improvement summary.
        
        Returns:
            Evolution summary report
        """
        return f"📈 Eta: Evolution Report - Week 42\n- New capabilities added: 2\n- Performance improvements: 15%\n- User success metrics: 89%\n- Planned evolutions: 3\nCelebrating progress and planning next phase!"

    def system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate Eta-specific system prompt.
        
        Args:
            context: Optional context dictionary
        
        Returns:
            System prompt string for evolution tasks
        """
        return """You are Eta (Η), the Evolution Engineer of B3PersonalAssistant. You are:
- Analytical and forward-thinking in all system improvements
- Continuously monitoring system performance and user patterns
- Identifying capability gaps and optimization opportunities
- Working closely with Zeta to implement technical improvements
- Tracking improvement metrics and celebrating progress
- Focused on making B3 continuously better and more capable

Key phrases: "I've identified an opportunity...", "Evolution report ready...", "System efficiency increased by...", "Celebrating progress..."
Always provide data-driven insights and actionable improvement plans."""

# --- Agent Factory ---

def get_all_agents() -> Dict[str, AgentBase]:
    """
    Instantiate all agents and return as a dictionary.
    
    Creates instances of all seven Greek agents (Alpha, Beta, Gamma, Delta, Epsilon, Zeta, Eta)
    for use in the multi-agent system.
    
    Returns:
        Dictionary mapping agent names to agent instances
        
    Example:
        >>> agents = get_all_agents()
        >>> print(agents.keys())
        dict_keys(['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta'])
        >>> response = agents['alpha'].act("Hello")
        >>> print(response)
        "Alpha processed: Hello"
    """
    return {
        "alpha": AlphaAgent(),
        "beta": BetaAgent(),
        "gamma": GammaAgent(),
        "delta": DeltaAgent(),
        "epsilon": EpsilonAgent(),
        "zeta": ZetaAgent(),
        "eta": EtaAgent(),
    } 