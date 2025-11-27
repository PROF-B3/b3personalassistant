"""
Gamma Agent - Knowledge Manager and Zettelkasten Specialist

Gamma manages the Zettelkasten knowledge system and information organization.
"""

import re
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from core.agents.base import AgentBase
from core.constants import COMPLEX_MODEL, MAX_CONVERSATION_CONTEXT, DEFAULT_SEARCH_LIMIT
from core.exceptions import (
    InputValidationError,
    OllamaConnectionError,
    OllamaTimeoutError,
    CircuitBreakerOpenError,
)
from modules.resources import track_agent_performance, ResourceMonitor


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
    """

    def __init__(self, orchestrator=None, user_profile=None, resource_monitor=None, knowledge_manager=None):
        """
        Initialize Gamma agent with knowledge management capabilities.

        Args:
            orchestrator: Reference to the orchestrator for agent coordination
            user_profile: User preferences and settings
            resource_monitor: Resource monitoring instance
            knowledge_manager: KnowledgeManager instance for Zettelkasten operations
        """
        super().__init__('Gamma', orchestrator, user_profile, resource_monitor)

        self.knowledge_manager = knowledge_manager
        if self.knowledge_manager is None:
            from modules.knowledge import create_knowledge_system
            self.knowledge_manager = create_knowledge_system()

        from modules.document_processing import DocumentProcessor, DocumentToZettelConverter
        self.doc_processor = DocumentProcessor()
        self.doc_converter = DocumentToZettelConverter(ollama_client=self.ollama_client)

        from modules.citation_manager import create_citation_manager
        self.citation_manager = create_citation_manager()

    def system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate Gamma-specific system prompt."""
        return """You are Gamma (Γ), the Knowledge Manager of B3PersonalAssistant. You are:
- Reflective, creative, and focused on connecting ideas
- Expert at organizing information using the Zettelkasten method
- Skilled at synthesizing knowledge and identifying relationships between concepts
- Focused on building a coherent, interconnected knowledge base
- Thoughtful about knowledge structure and organization

Your role is to help users create, organize, and connect notes in their knowledge base. You excel at identifying patterns, suggesting connections, and maintaining a well-structured Zettelkasten system.

Key phrases: "Let's connect this idea to", "I see a pattern between", "This relates to", "Knowledge is interconnected"
Always help users build a meaningful, well-organized knowledge base."""

    def _handle_knowledge_command(self, input_text: str) -> Optional[str]:
        """
        Handle direct knowledge commands for Zettelkasten operations.

        Args:
            input_text: User input text

        Returns:
            Response string if command was handled, None otherwise
        """
        input_lower = input_text.lower()

        # Command: Create note
        if any(keyword in input_lower for keyword in ['create note', 'make note', 'add note', 'new note']):
            content_match = re.search(r'(?:create|make|add|new) note[:\s]+(.+)', input_text, re.IGNORECASE)
            if content_match:
                content = content_match.group(1).strip()
                note_id = self.knowledge_manager.quick_note(content)
                return f"✓ Created note {note_id}: {content[:50]}..."
            return "Please specify what you'd like to note. Example: 'create note about quantum computing'"

        # Command: Search notes
        elif any(keyword in input_lower for keyword in ['search notes', 'find notes', 'search for']):
            query_match = re.search(r'(?:search|find)(?: notes)?(?: for)?[:\s]+(.+)', input_text, re.IGNORECASE)
            if query_match:
                query = query_match.group(1).strip()
                results = self.knowledge_manager.zettelkasten.search_zettels(query, limit=DEFAULT_SEARCH_LIMIT)
                if results:
                    response = f"Found {len(results)} notes:\n"
                    for zettel in results:
                        response += f"\n• {zettel.id}: {zettel.title}\n  Tags: {', '.join(zettel.tags[:5])}\n"
                    return response
                return f"No notes found for '{query}'"
            return "Please specify what to search for. Example: 'search notes for machine learning'"

        # Command: Import document/PDF
        elif any(keyword in input_lower for keyword in ['import pdf', 'import document', 'ingest pdf', 'process pdf']):
            path_match = re.search(r'(?:import|ingest|process)(?: pdf| document)?[:\s]+([^\s]+)', input_text, re.IGNORECASE)
            if path_match:
                file_path = Path(path_match.group(1).strip())
                return self._import_document(file_path)
            return "Please specify the file path. Example: 'import pdf /path/to/document.pdf'"

        # Command: List notes by tag
        elif 'notes with tag' in input_lower or 'tagged' in input_lower:
            tag_match = re.search(r'(?:with tag|tagged)[:\s]+(\w+)', input_text, re.IGNORECASE)
            if tag_match:
                tag = tag_match.group(1).strip()
                results = self.knowledge_manager.zettelkasten.get_zettels_by_tag(tag)
                if results:
                    response = f"Found {len(results)} notes tagged '{tag}':\n"
                    for zettel in results[:10]:
                        response += f"\n• {zettel.id}: {zettel.title}\n"
                    return response
                return f"No notes found with tag '{tag}'"
            return "Please specify a tag. Example: 'show notes with tag machine-learning'"

        # Command: Show statistics
        elif any(keyword in input_lower for keyword in ['knowledge stats', 'note stats', 'zettelkasten stats']):
            stats = self.knowledge_manager.zettelkasten.get_statistics()
            return f"""📊 Zettelkasten Statistics:
• Total notes: {stats['total_zettels']}
• By category: {stats['by_category']}
• Total tags: {stats['total_tags']}
• Total links: {stats['total_links']}"""

        # Command: Extract citation from PDF
        elif any(keyword in input_lower for keyword in ['extract citation', 'get citation from', 'cite pdf']):
            path_match = re.search(r'(?:from|pdf)[:\s]+([^\s]+)', input_text, re.IGNORECASE)
            if path_match:
                file_path = Path(path_match.group(1).strip())
                if not file_path.exists():
                    return f"❌ File not found: {file_path}"

                citation = self.citation_manager.extract_from_pdf(file_path)
                if citation:
                    return f"""✓ Extracted citation:

**{citation.title}**
Authors: {', '.join(citation.authors)}
Year: {citation.year or 'N/A'}
Cite key: {citation.cite_key}

BibTeX entry added to bibliography."""
                return f"❌ Could not extract citation from {file_path}"
            return "Please specify PDF path. Example: 'extract citation from paper.pdf'"

        # Command: Generate bibliography
        elif any(keyword in input_lower for keyword in ['generate bibliography', 'create bibliography', 'show bibliography']):
            style = "apa"
            if "bibtex" in input_lower:
                style = "bibtex"
            elif "mla" in input_lower:
                style = "mla"
            elif "chicago" in input_lower:
                style = "chicago"

            bibliography = self.citation_manager.generate_bibliography(style=style)
            if bibliography:
                return f"""📚 Bibliography ({style.upper()}):\n\n{bibliography}"""
            return "No citations in bibliography yet. Import PDFs or add citations first."

        # Command: Search citations
        elif any(keyword in input_lower for keyword in ['search citations', 'find citations', 'search refs']):
            query_match = re.search(r'(?:search|find)(?: citations| refs)?[:\s]+(.+)', input_text, re.IGNORECASE)
            if query_match:
                query = query_match.group(1).strip()
                results = self.citation_manager.search_citations(query)
                if results:
                    response = f"Found {len(results)} citations:\n\n"
                    for citation in results[:5]:
                        response += f"• [{citation.cite_key}] {citation.title}\n"
                        response += f"  {', '.join(citation.authors[:3])}, {citation.year or 'n.d.'}\n\n"
                    return response
                return f"No citations found for '{query}'"
            return "Please specify search query. Example: 'search citations for neural networks'"

        return None

    def _import_document(self, file_path: Path) -> str:
        """Import a document into Zettelkasten."""
        if not file_path.exists():
            return f"❌ File not found: {file_path}"

        try:
            self.logger.info(f"Processing document: {file_path}")
            doc = self.doc_processor.process_document(file_path)

            if not doc:
                return f"❌ Failed to process {file_path}. Unsupported format or error occurred."

            notes_data = self.doc_converter.convert_to_notes(doc, strategy="single", use_ai=True)

            created_ids = []
            for note_data in notes_data:
                note_id = self.knowledge_manager.zettelkasten.create_zettel(**note_data)
                created_ids.append(note_id)

            response = f"✓ Successfully imported {file_path.name}\n"
            response += f"Created {len(created_ids)} note(s): {', '.join(created_ids)}\n"
            response += f"Tags: {', '.join(doc.suggested_tags[:5])}"

            return response

        except (OSError, ValueError) as e:
            self.logger.error(f"Error importing document: {e}", exc_info=True)
            return f"❌ Error importing document: {str(e)}"

    @track_agent_performance('Gamma', ResourceMonitor(Path('databases')))
    def act(self, input_data: str, context: Optional[Dict] = None) -> str:
        """
        Manage knowledge and Zettelkasten operations.

        Args:
            input_data: User input text (knowledge request)
            context: Optional context dictionary

        Returns:
            Knowledge management response
        """
        try:
            validated_input = self.validator.validate_and_sanitize(input_data)
            self.save_conversation('user', validated_input)

            command_response = self._handle_knowledge_command(validated_input)
            if command_response:
                self.save_conversation('assistant', command_response)
                return self.adapt_to_user(command_response)

            model = COMPLEX_MODEL
            recent_history = self.get_conversation_history(limit=MAX_CONVERSATION_CONTEXT)

            messages = [{"role": "system", "content": self.system_prompt(context)}]

            for msg in recent_history:
                messages.append({
                    "role": "user" if msg['role'] == 'user' else "assistant",
                    "content": msg['message']
                })

            messages.append({"role": "user", "content": validated_input})

            self.logger.info(f"Gamma managing knowledge with model: {model}")
            response = self.call_ollama_with_resilience(
                model=model,
                messages=messages,
                timeout=30.0
            )

            result = response['message']['content']
            self.save_conversation('assistant', result)

            return self.adapt_to_user(result)

        except InputValidationError as e:
            self.logger.warning(f"Gamma input validation error: {e}")
            return f"I couldn't process your input: {str(e)}. Please try rephrasing your request."

        except CircuitBreakerOpenError as e:
            self.logger.error(f"Gamma circuit breaker open: {e}")
            return "I'm temporarily unable to process requests due to system issues. Please try again in a moment."

        except (OllamaConnectionError, OllamaTimeoutError) as e:
            self.logger.error(f"Gamma Ollama error: {e}")
            return "I'm having trouble connecting to my AI backend. Please ensure Ollama is running and try again."

        except Exception as e:
            self.logger.error(f"Gamma act() error: {e}", exc_info=True)
            fallback = "I encountered an unexpected issue. Let me try to help in a different way."
            self.save_conversation('assistant', fallback)
            return self.handle_error(e, context)
