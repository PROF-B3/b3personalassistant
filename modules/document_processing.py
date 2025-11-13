"""
Document Processing Module for B3PersonalAssistant.

Handles extraction of text and metadata from various document formats
(PDF, DOCX, TXT, MD) and prepares them for Zettelkasten ingestion.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class DocumentContent:
    """Extracted content from a document."""
    file_path: str
    file_type: str
    title: str
    content: str
    metadata: Dict
    suggested_tags: List[str]
    sections: List[Dict]  # For structured documents
    checksum: str


class DocumentProcessor:
    """
    Process various document formats and extract content.

    Supports: PDF, DOCX, TXT, MD
    """

    def __init__(self):
        """Initialize document processor."""
        self.logger = logging.getLogger("document_processor")

        # Try to import PDF processing libraries
        self.pdf_available = self._check_pdf_support()
        self.docx_available = self._check_docx_support()

    def _check_pdf_support(self) -> bool:
        """Check if PDF processing is available."""
        try:
            import PyPDF2
            self.logger.info("PyPDF2 available for PDF processing")
            return True
        except ImportError:
            try:
                import pdfplumber
                self.logger.info("pdfplumber available for PDF processing")
                return True
            except ImportError:
                self.logger.warning("No PDF processing library available. Install PyPDF2 or pdfplumber.")
                return False

    def _check_docx_support(self) -> bool:
        """Check if DOCX processing is available."""
        try:
            import docx
            self.logger.info("python-docx available for DOCX processing")
            return True
        except ImportError:
            self.logger.warning("python-docx not available. Install python-docx for DOCX support.")
            return False

    def process_document(self, file_path: Path) -> Optional[DocumentContent]:
        """
        Process a document and extract content.

        Args:
            file_path: Path to the document

        Returns:
            DocumentContent object or None if processing failed
        """
        if not file_path.exists():
            self.logger.error(f"File not found: {file_path}")
            return None

        file_type = file_path.suffix.lower()

        try:
            if file_type == '.pdf':
                return self._process_pdf(file_path)
            elif file_type == '.docx':
                return self._process_docx(file_path)
            elif file_type in ['.txt', '.md', '.markdown']:
                return self._process_text(file_path)
            else:
                self.logger.error(f"Unsupported file type: {file_type}")
                return None
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}", exc_info=True)
            return None

    def _process_pdf(self, file_path: Path) -> Optional[DocumentContent]:
        """Extract content from PDF file."""
        if not self.pdf_available:
            self.logger.error("PDF processing not available. Install PyPDF2 or pdfplumber.")
            return None

        try:
            # Try PyPDF2 first
            import PyPDF2
            return self._process_pdf_pypdf2(file_path)
        except ImportError:
            try:
                # Fall back to pdfplumber
                import pdfplumber
                return self._process_pdf_pdfplumber(file_path)
            except ImportError:
                self.logger.error("No PDF library available")
                return None
        except Exception as e:
            self.logger.error(f"Error processing PDF with PyPDF2: {e}")
            # Try pdfplumber as fallback
            try:
                import pdfplumber
                return self._process_pdf_pdfplumber(file_path)
            except Exception as e2:
                self.logger.error(f"Error processing PDF with pdfplumber: {e2}")
                return None

    def _process_pdf_pypdf2(self, file_path: Path) -> DocumentContent:
        """Process PDF using PyPDF2."""
        import PyPDF2

        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)

            # Extract metadata
            metadata = {}
            if reader.metadata:
                metadata = {
                    'author': reader.metadata.get('/Author', ''),
                    'title': reader.metadata.get('/Title', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', ''),
                }

            # Extract text from all pages
            content_parts = []
            sections = []

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    content_parts.append(page_text)
                    sections.append({
                        'page': i + 1,
                        'content': page_text[:500],  # Preview
                        'length': len(page_text)
                    })

            content = '\n\n'.join(content_parts)

            # Generate title from metadata or filename
            title = metadata.get('title', '') or file_path.stem

            # Generate checksum
            checksum = hashlib.md5(content.encode()).hexdigest()

            # Extract suggested tags
            suggested_tags = self._extract_tags(content, title)

            return DocumentContent(
                file_path=str(file_path),
                file_type='pdf',
                title=title,
                content=content,
                metadata=metadata,
                suggested_tags=suggested_tags,
                sections=sections,
                checksum=checksum
            )

    def _process_pdf_pdfplumber(self, file_path: Path) -> DocumentContent:
        """Process PDF using pdfplumber."""
        import pdfplumber

        with pdfplumber.open(file_path) as pdf:
            # Extract metadata
            metadata = pdf.metadata or {}

            # Extract text from all pages
            content_parts = []
            sections = []

            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    content_parts.append(page_text)
                    sections.append({
                        'page': i + 1,
                        'content': page_text[:500],
                        'length': len(page_text)
                    })

            content = '\n\n'.join(content_parts)

            # Generate title
            title = metadata.get('Title', '') or file_path.stem

            # Generate checksum
            checksum = hashlib.md5(content.encode()).hexdigest()

            # Extract suggested tags
            suggested_tags = self._extract_tags(content, title)

            return DocumentContent(
                file_path=str(file_path),
                file_type='pdf',
                title=title,
                content=content,
                metadata=metadata,
                suggested_tags=suggested_tags,
                sections=sections,
                checksum=checksum
            )

    def _process_docx(self, file_path: Path) -> Optional[DocumentContent]:
        """Extract content from DOCX file."""
        if not self.docx_available:
            self.logger.error("DOCX processing not available. Install python-docx.")
            return None

        try:
            import docx

            doc = docx.Document(file_path)

            # Extract metadata
            metadata = {
                'author': doc.core_properties.author or '',
                'title': doc.core_properties.title or '',
                'subject': doc.core_properties.subject or '',
                'keywords': doc.core_properties.keywords or '',
                'created': str(doc.core_properties.created) if doc.core_properties.created else '',
                'modified': str(doc.core_properties.modified) if doc.core_properties.modified else '',
            }

            # Extract text
            content_parts = []
            sections = []

            for i, para in enumerate(doc.paragraphs):
                if para.text.strip():
                    content_parts.append(para.text)

                    # Detect section headers (larger font or bold)
                    if para.style.name.startswith('Heading'):
                        sections.append({
                            'heading': para.text,
                            'level': para.style.name,
                            'index': i
                        })

            content = '\n\n'.join(content_parts)

            # Generate title
            title = metadata.get('title', '') or file_path.stem

            # Generate checksum
            checksum = hashlib.md5(content.encode()).hexdigest()

            # Extract suggested tags
            suggested_tags = self._extract_tags(content, title)
            if metadata.get('keywords'):
                suggested_tags.extend([k.strip() for k in metadata['keywords'].split(',')])

            return DocumentContent(
                file_path=str(file_path),
                file_type='docx',
                title=title,
                content=content,
                metadata=metadata,
                suggested_tags=list(set(suggested_tags)),  # Remove duplicates
                sections=sections,
                checksum=checksum
            )
        except Exception as e:
            self.logger.error(f"Error processing DOCX: {e}", exc_info=True)
            return None

    def _process_text(self, file_path: Path) -> DocumentContent:
        """Extract content from plain text or markdown file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title from first line or filename
        lines = content.split('\n')
        title = file_path.stem

        # For markdown, try to extract title from first heading
        if file_path.suffix.lower() in ['.md', '.markdown']:
            for line in lines[:10]:
                if line.startswith('# '):
                    title = line.lstrip('# ').strip()
                    break

        # Extract sections (markdown headings)
        sections = []
        if file_path.suffix.lower() in ['.md', '.markdown']:
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    sections.append({
                        'heading': line.lstrip('#').strip(),
                        'level': len(line) - len(line.lstrip('#')),
                        'line': i
                    })

        # Generate checksum
        checksum = hashlib.md5(content.encode()).hexdigest()

        # Extract suggested tags
        suggested_tags = self._extract_tags(content, title)

        # Extract tags from markdown if present
        if file_path.suffix.lower() in ['.md', '.markdown']:
            tag_matches = re.findall(r'#(\w+)', content)
            suggested_tags.extend([tag.lower() for tag in tag_matches])

        metadata = {
            'filename': file_path.name,
            'size': len(content)
        }

        return DocumentContent(
            file_path=str(file_path),
            file_type=file_path.suffix.lower().lstrip('.'),
            title=title,
            content=content,
            metadata=metadata,
            suggested_tags=list(set(suggested_tags)),
            sections=sections,
            checksum=checksum
        )

    def _extract_tags(self, content: str, title: str) -> List[str]:
        """
        Extract suggested tags from content and title.

        Uses simple keyword extraction based on frequency and title words.
        """
        tags = []

        # Add significant words from title
        title_words = re.findall(r'\b\w{4,}\b', title.lower())
        tags.extend(title_words[:3])  # First 3 significant words

        # Extract potential keywords (words that appear frequently)
        words = re.findall(r'\b\w{5,}\b', content.lower())
        word_freq = {}
        for word in words:
            # Skip common words
            if word in ['which', 'there', 'their', 'these', 'those', 'where',
                       'would', 'could', 'should', 'about', 'other']:
                continue
            word_freq[word] = word_freq.get(word, 0) + 1

        # Get top 5 most frequent words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        tags.extend([word for word, freq in top_words if freq >= 2])

        return list(set(tags))  # Remove duplicates

    def batch_process(self, directory: Path, pattern: str = "*.*") -> List[DocumentContent]:
        """
        Process all matching documents in a directory.

        Args:
            directory: Directory to process
            pattern: File pattern to match (default: all files)

        Returns:
            List of DocumentContent objects
        """
        if not directory.is_dir():
            self.logger.error(f"Not a directory: {directory}")
            return []

        results = []

        for file_path in directory.glob(pattern):
            if file_path.is_file():
                self.logger.info(f"Processing {file_path.name}...")
                doc = self.process_document(file_path)
                if doc:
                    results.append(doc)
                    self.logger.info(f"✓ Processed {file_path.name}")
                else:
                    self.logger.warning(f"✗ Failed to process {file_path.name}")

        return results


class DocumentToZettelConverter:
    """
    Convert processed documents to Zettelkasten notes.

    Uses AI to analyze content, suggest connections, and create well-structured notes.
    """

    def __init__(self, ollama_client=None):
        """
        Initialize converter.

        Args:
            ollama_client: Optional Ollama client for AI analysis
        """
        self.ollama_client = ollama_client
        self.logger = logging.getLogger("doc_to_zettel")

    def convert_to_notes(
        self,
        doc: DocumentContent,
        strategy: str = "single",
        use_ai: bool = True
    ) -> List[Dict]:
        """
        Convert document to one or more Zettelkasten notes.

        Args:
            doc: Document content to convert
            strategy: Conversion strategy:
                - "single": One note for entire document
                - "sections": One note per major section
                - "atomic": Break into atomic concepts (requires AI)
            use_ai: Use AI to enhance note creation

        Returns:
            List of note dictionaries ready for Zettelkasten.create_zettel()
        """
        if strategy == "single":
            return [self._create_single_note(doc, use_ai)]
        elif strategy == "sections" and doc.sections:
            return self._create_section_notes(doc, use_ai)
        elif strategy == "atomic" and use_ai and self.ollama_client:
            return self._create_atomic_notes(doc)
        else:
            # Default to single note
            return [self._create_single_note(doc, use_ai)]

    def _create_single_note(self, doc: DocumentContent, use_ai: bool) -> Dict:
        """Create a single note from entire document."""
        # Prepare note content
        content = doc.content

        # Enhance with AI if available
        if use_ai and self.ollama_client:
            enhanced_data = self._ai_enhance_note(doc)
            tags = enhanced_data.get('tags', doc.suggested_tags)
            summary = enhanced_data.get('summary', '')

            # Add summary at the top if available
            if summary:
                content = f"## Summary\n\n{summary}\n\n## Full Content\n\n{content}"
        else:
            tags = doc.suggested_tags

        return {
            'title': doc.title,
            'content': content,
            'category': '2',  # Secondary topics
            'tags': tags,
            'metadata': {
                'source_file': doc.file_path,
                'file_type': doc.file_type,
                'checksum': doc.checksum,
                **doc.metadata
            }
        }

    def _create_section_notes(self, doc: DocumentContent, use_ai: bool) -> List[Dict]:
        """Create multiple notes from document sections."""
        notes = []

        # Create main note
        main_note = {
            'title': doc.title,
            'content': f"Main document: {doc.title}\n\nSee section notes for details.",
            'category': '2',
            'tags': doc.suggested_tags + ['index-note'],
            'metadata': {
                'source_file': doc.file_path,
                'file_type': doc.file_type,
                'checksum': doc.checksum,
                'note_type': 'index'
            }
        }
        notes.append(main_note)

        # Create notes for each section
        for i, section in enumerate(doc.sections[:10]):  # Limit to 10 sections
            section_title = section.get('heading', f"Section {i+1}")

            note = {
                'title': f"{doc.title} - {section_title}",
                'content': section.get('content', ''),
                'category': '2',
                'tags': doc.suggested_tags,
                'metadata': {
                    'source_file': doc.file_path,
                    'section': i + 1,
                    'parent_note': doc.title
                }
            }
            notes.append(note)

        return notes

    def _create_atomic_notes(self, doc: DocumentContent) -> List[Dict]:
        """Use AI to break document into atomic concept notes."""
        if not self.ollama_client:
            return [self._create_single_note(doc, False)]

        try:
            # Ask AI to identify atomic concepts
            prompt = f"""Analyze this document and identify distinct atomic concepts that could be separate notes.

Title: {doc.title}

Content (first 2000 chars):
{doc.content[:2000]}

Return a JSON list of concepts, each with:
- concept_title: Brief title
- key_points: 2-3 key points about this concept
- related_to: Other concepts it relates to

Format: {{"concepts": [...]}}"""

            response = self.ollama_client.chat(
                model="llama3.2:3b",
                messages=[{"role": "user", "content": prompt}],
                format="json"
            )

            import json
            result = json.loads(response['message']['content'])

            notes = []
            for concept in result.get('concepts', [])[:10]:  # Max 10 concepts
                note = {
                    'title': concept['concept_title'],
                    'content': '\n'.join(concept.get('key_points', [])),
                    'category': '1',  # Main topics
                    'tags': doc.suggested_tags + [concept['concept_title'].lower()],
                    'metadata': {
                        'source_file': doc.file_path,
                        'extraction_method': 'ai_atomic',
                        'related_concepts': concept.get('related_to', [])
                    }
                }
                notes.append(note)

            return notes if notes else [self._create_single_note(doc, False)]

        except Exception as e:
            self.logger.error(f"AI atomic note creation failed: {e}")
            return [self._create_single_note(doc, False)]

    def _ai_enhance_note(self, doc: DocumentContent) -> Dict:
        """Use AI to enhance note with summary and better tags."""
        if not self.ollama_client:
            return {'tags': doc.suggested_tags, 'summary': ''}

        try:
            prompt = f"""Analyze this document and provide:
1. A concise summary (2-3 sentences)
2. 5-7 relevant tags

Title: {doc.title}
Content (first 1500 chars): {doc.content[:1500]}

Format as JSON: {{"summary": "...", "tags": [...]}}"""

            response = self.ollama_client.chat(
                model="llama3.2:3b",
                messages=[{"role": "user", "content": prompt}],
                format="json"
            )

            import json
            return json.loads(response['message']['content'])

        except Exception as e:
            self.logger.error(f"AI enhancement failed: {e}")
            return {'tags': doc.suggested_tags, 'summary': ''}


if __name__ == "__main__":
    # Test document processing
    processor = DocumentProcessor()
    print(f"PDF support: {processor.pdf_available}")
    print(f"DOCX support: {processor.docx_available}")
