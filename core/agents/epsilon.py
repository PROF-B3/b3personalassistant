"""
Epsilon Agent - Creative Director and Media Specialist

Epsilon handles all creative tasks including video editing, image manipulation,
audio processing, creative writing, and design suggestions.
"""

import re
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from core.agents.base import AgentBase
from core.constants import COMPLEX_MODEL, MAX_CONVERSATION_CONTEXT
from core.exceptions import (
    InputValidationError,
    OllamaConnectionError,
    OllamaTimeoutError,
    CircuitBreakerOpenError,
)
from modules.resources import track_agent_performance, ResourceMonitor


class EpsilonAgent(AgentBase):
    """
    Epsilon (Ε) - Creative Director and Media Specialist

    Epsilon handles all creative tasks including video editing, image manipulation,
    audio processing, creative writing, and design suggestions.

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

        from modules.document_export import create_document_exporter
        self.doc_exporter = create_document_exporter()

    def _initialize_creative_tools(self):
        """
        Initialize creative tool integrations.

        Returns:
            Dictionary of available creative tools
        """
        tools = {}

        try:
            import moviepy.editor as mp  # noqa: F401
            tools['video'] = 'MoviePy'
        except ImportError:
            tools['video'] = 'FFmpeg Guidance'

        try:
            from PIL import Image  # noqa: F401
            tools['image'] = 'Pillow'
        except ImportError:
            tools['image'] = 'Basic Image Processing'

        tools['writing'] = 'Creative Writing'
        tools['audio'] = 'Audio Processing'
        return tools

    def system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate Epsilon-specific system prompt."""
        return """You are Epsilon (Ε), the Creative Director of B3PersonalAssistant. You are:
- High energy and enthusiastic about all creative projects
- Skilled in video editing, image manipulation, audio processing, and creative writing
- Always suggesting artistic improvements and creative enhancements
- Using creative metaphors and inspiring language
- Focused on making content visually and emotionally impactful

Key phrases: "Let's add some flair!", "I envision this as...", "For maximum impact...", "Time to unleash your creative genius!"
Always provide practical creative solutions with artistic guidance."""

    @track_agent_performance('Epsilon', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Handle creative requests and media tasks.

        Args:
            input_data: User input text (creative request)
            context: Optional context dictionary

        Returns:
            Creative response with artistic suggestions
        """
        try:
            validated_input = self.validator.validate_and_sanitize(input_data)
            self.save_conversation('user', validated_input)

            input_lower = validated_input.lower()
            handler_result = None

            if any(kw in input_lower for kw in ['video', 'edit video', 'cut', 'montage', 'movie', 'clip']):
                handler_result = self.handle_video_request(validated_input)
            elif any(kw in input_lower for kw in ['image', 'photo', 'picture', 'resize', 'crop', 'filter']):
                handler_result = self.handle_image_request(validated_input)
            elif any(kw in input_lower for kw in ['audio', 'sound', 'music', 'podcast', 'recording']):
                handler_result = self.handle_audio_request(validated_input)
            elif any(kw in input_lower for kw in ['write', 'story', 'poem', 'script', 'blog', 'article']):
                handler_result = self.handle_writing_request(validated_input)
            elif any(kw in input_lower for kw in ['export to word', 'export to docx', 'export to latex', 'export chapter']):
                handler_result = self._handle_export_request(validated_input, context)

            if handler_result:
                self.save_conversation('assistant', handler_result)
                return self.adapt_to_user(handler_result)

            model = COMPLEX_MODEL
            recent_history = self.get_conversation_history(limit=MAX_CONVERSATION_CONTEXT)

            tools_context = f"\nAvailable creative tools: {', '.join([f'{k}: {v}' for k, v in self.creative_tools.items()])}"

            messages = [{"role": "system", "content": self.system_prompt(context) + tools_context}]

            for msg in recent_history:
                messages.append({
                    "role": "user" if msg['role'] == 'user' else "assistant",
                    "content": msg['message']
                })

            messages.append({"role": "user", "content": validated_input})

            self.logger.info(f"Epsilon creating with model: {model}")
            response = self.call_ollama_with_resilience(
                model=model,
                messages=messages,
                timeout=30.0
            )

            result = response['message']['content']
            self.save_conversation('assistant', result)

            return self.adapt_to_user(result)

        except InputValidationError as e:
            self.logger.warning(f"Epsilon input validation error: {e}")
            return f"I couldn't process your input: {str(e)}. Please try rephrasing your request."

        except CircuitBreakerOpenError as e:
            self.logger.error(f"Epsilon circuit breaker open: {e}")
            return "I'm temporarily unable to process requests due to system issues. Please try again in a moment."

        except (OllamaConnectionError, OllamaTimeoutError) as e:
            self.logger.error(f"Epsilon Ollama error: {e}")
            return "I'm having trouble connecting to my AI backend. Please ensure Ollama is running and try again."

        except Exception as e:
            self.logger.error(f"Epsilon act() error: {e}", exc_info=True)
            fallback = "I encountered an unexpected issue. Let me try to help in a different way."
            self.save_conversation('assistant', fallback)
            return self.handle_error(e, context)

    def handle_video_request(self, request: str) -> str:
        """Handle video editing requests."""
        if 'MoviePy' in self.creative_tools['video']:
            return f"🎬 Epsilon: I'll create that video masterpiece for you! Using MoviePy to {request}"
        else:
            return f"🎬 Epsilon: For maximum impact, here's how to {request} with FFmpeg:\n1. Install FFmpeg\n2. Use command: ffmpeg -i input.mp4 -vf [effects] output.mp4\n3. Add transitions and overlays for that professional touch!"

    def handle_image_request(self, request: str) -> str:
        """Handle image manipulation requests."""
        if 'Pillow' in self.creative_tools['image']:
            return f"🖼️ Epsilon: I envision this as a stunning visual! Using Pillow to {request}"
        else:
            return f"🖼️ Epsilon: Let's make this image pop! For {request}, try:\n1. Use GIMP or Photoshop\n2. Apply filters and effects\n3. Optimize for your target platform"

    def handle_writing_request(self, request: str) -> str:
        """Handle creative writing requests."""
        return f"✍️ Epsilon: Time to unleash your creative genius! For {request}, I suggest:\n1. Start with a compelling hook\n2. Build emotional connection\n3. End with a memorable conclusion\nLet's craft something extraordinary!"

    def handle_audio_request(self, request: str) -> str:
        """Handle audio processing requests."""
        return f"🎵 Epsilon: Let's make some beautiful music! For {request}:\n1. Use Audacity for editing\n2. Apply effects and filters\n3. Export in high quality\nYour audio will sound amazing!"

    def _handle_export_request(self, input_text: str, context: Optional[Dict] = None) -> Optional[str]:
        """Handle document export requests."""
        input_lower = input_text.lower()

        format_type = "word"
        if "latex" in input_lower or ".tex" in input_lower:
            format_type = "latex"
        elif "docx" in input_lower or "word" in input_lower:
            format_type = "word"

        path_match = re.search(r'(?:to|as)[:\s]+([^\s]+)', input_text)
        output_path = None
        if path_match:
            output_path = Path(path_match.group(1).strip())
        else:
            if format_type == "word":
                output_path = Path("exported_document.docx")
            else:
                output_path = Path("exported_document.tex")

        content = ""
        title = None
        author = None

        if context and 'content' in context:
            content = context['content']
            title = context.get('title')
            author = context.get('author')
        else:
            content_match = re.search(r'content[:\s]+(.+)', input_text, re.IGNORECASE)
            if content_match:
                content = content_match.group(1)
            else:
                return """To export, please provide content. Example:
'export to word: # My Chapter\\n\\nThis is the introduction...'

Or provide context with:
- context['content']: The text to export
- context['title']: Document title (optional)
- context['author']: Author name (optional)"""

        try:
            if format_type == "word":
                success = self.doc_exporter.export_to_word(
                    content=content,
                    output_path=output_path,
                    title=title,
                    author=author
                )
            else:
                success = self.doc_exporter.export_to_latex(
                    content=content,
                    output_path=output_path,
                    title=title,
                    author=author
                )

            if success:
                return f"✅ Successfully exported to {output_path}\nFormat: {format_type.upper()}"
            else:
                return f"❌ Export failed. Make sure python-docx is installed for Word export."

        except (OSError, ValueError) as e:
            return f"❌ Export error: {str(e)}"
