"""
Multimodal Agent for B3PersonalAssistant

Handles multiple input types: images, audio, PDFs, and documents.
Provides unified interface for processing different media types.
"""

import logging
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
import mimetypes

logger = logging.getLogger(__name__)


@dataclass
class ProcessedContent:
    """Result of processing multimodal content."""
    content_type: str  # "image", "audio", "pdf", "document"
    extracted_text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    entities: Optional[List[str]] = None
    error: Optional[str] = None


class MultimodalAgent:
    """
    Agent for processing multiple media types.

    Features:
    - Image understanding and description
    - OCR (Optical Character Recognition)
    - Audio transcription
    - PDF text extraction and parsing
    - Document structure analysis
    - Entity extraction
    - Content summarization

    Example:
        >>> agent = MultimodalAgent()
        >>> result = agent.process_image("screenshot.png")
        >>> print(result.extracted_text)
        >>> print(result.summary)
    """

    def __init__(self, ollama_vision_model: str = "llava"):
        """
        Initialize multimodal agent.

        Args:
            ollama_vision_model: Ollama model for vision tasks (e.g., llava, bakllava)
        """
        self.ollama_vision_model = ollama_vision_model
        self._initialize_processors()

    def _initialize_processors(self):
        """Initialize processing libraries."""
        self.processors_available = {
            "PIL": False,
            "pytesseract": False,
            "PyPDF2": False,
            "pdfplumber": False,
            "whisper": False,
            "ollama": False
        }

        # Check PIL (for images)
        try:
            from PIL import Image
            self.processors_available["PIL"] = True
            logger.info("PIL available for image processing")
        except ImportError:
            logger.warning("PIL not available. Install with: pip install Pillow")

        # Check tesseract (for OCR)
        try:
            import pytesseract
            self.processors_available["pytesseract"] = True
            logger.info("Tesseract available for OCR")
        except ImportError:
            logger.warning("pytesseract not available. Install with: pip install pytesseract")

        # Check PDF processors
        try:
            import PyPDF2
            self.processors_available["PyPDF2"] = True
            logger.info("PyPDF2 available for PDF processing")
        except ImportError:
            logger.warning("PyPDF2 not available. Install with: pip install PyPDF2")

        try:
            import pdfplumber
            self.processors_available["pdfplumber"] = True
            logger.info("pdfplumber available for advanced PDF processing")
        except ImportError:
            logger.warning("pdfplumber not available. Install with: pip install pdfplumber")

        # Check whisper (for audio)
        try:
            import whisper
            self.processors_available["whisper"] = True
            logger.info("Whisper available for audio transcription")
        except ImportError:
            logger.warning("whisper not available. Install with: pip install openai-whisper")

        # Check Ollama (for vision)
        try:
            import ollama
            self.processors_available["ollama"] = True
            logger.info(f"Ollama available with vision model: {self.ollama_vision_model}")
        except ImportError:
            logger.warning("ollama not available. Install with: pip install ollama")

    def process_file(self, file_path: Union[str, Path]) -> ProcessedContent:
        """
        Process any file type automatically.

        Args:
            file_path: Path to file

        Returns:
            ProcessedContent with extracted information

        Example:
            >>> result = agent.process_file("document.pdf")
            >>> print(result.extracted_text)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return ProcessedContent(
                content_type="error",
                error=f"File not found: {file_path}"
            )

        # Detect file type
        mime_type, _ = mimetypes.guess_type(str(file_path))

        if mime_type and mime_type.startswith("image/"):
            return self.process_image(file_path)
        elif mime_type and mime_type.startswith("audio/"):
            return self.process_audio(file_path)
        elif mime_type == "application/pdf":
            return self.process_pdf(file_path)
        elif mime_type and mime_type.startswith("text/"):
            return self.process_document(file_path)
        else:
            return ProcessedContent(
                content_type="unknown",
                error=f"Unsupported file type: {mime_type}"
            )

    def process_image(
        self,
        image_path: Union[str, Path],
        extract_text: bool = True,
        describe: bool = True
    ) -> ProcessedContent:
        """
        Process an image file.

        Args:
            image_path: Path to image
            extract_text: Perform OCR
            describe: Generate description using vision model

        Returns:
            ProcessedContent with extracted text and description

        Example:
            >>> result = agent.process_image("receipt.jpg", extract_text=True)
            >>> print(result.extracted_text)  # OCR text
            >>> print(result.summary)  # AI description
        """
        image_path = Path(image_path)
        extracted_text = None
        description = None
        metadata = {}

        try:
            # Get image metadata
            if self.processors_available["PIL"]:
                from PIL import Image
                with Image.open(image_path) as img:
                    metadata = {
                        "format": img.format,
                        "size": img.size,
                        "mode": img.mode
                    }

            # OCR extraction
            if extract_text and self.processors_available["pytesseract"]:
                import pytesseract
                from PIL import Image

                with Image.open(image_path) as img:
                    extracted_text = pytesseract.image_to_string(img)
                    extracted_text = extracted_text.strip()

            # Vision model description
            if describe and self.processors_available["ollama"]:
                import ollama

                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode()

                response = ollama.chat(
                    model=self.ollama_vision_model,
                    messages=[{
                        "role": "user",
                        "content": "Describe this image in detail.",
                        "images": [image_data]
                    }]
                )

                description = response["message"]["content"]

            return ProcessedContent(
                content_type="image",
                extracted_text=extracted_text,
                summary=description,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Failed to process image: {e}")
            return ProcessedContent(
                content_type="image",
                error=str(e)
            )

    def process_audio(self, audio_path: Union[str, Path]) -> ProcessedContent:
        """
        Transcribe audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            ProcessedContent with transcription

        Example:
            >>> result = agent.process_audio("meeting.mp3")
            >>> print(result.extracted_text)  # Transcription
        """
        audio_path = Path(audio_path)

        try:
            if not self.processors_available["whisper"]:
                return ProcessedContent(
                    content_type="audio",
                    error="Whisper not available. Install with: pip install openai-whisper"
                )

            import whisper

            # Load model
            model = whisper.load_model("base")

            # Transcribe
            result = model.transcribe(str(audio_path))

            return ProcessedContent(
                content_type="audio",
                extracted_text=result["text"],
                metadata={
                    "language": result.get("language"),
                    "duration": result.get("duration")
                }
            )

        except Exception as e:
            logger.error(f"Failed to process audio: {e}")
            return ProcessedContent(
                content_type="audio",
                error=str(e)
            )

    def process_pdf(self, pdf_path: Union[str, Path]) -> ProcessedContent:
        """
        Extract text and structure from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            ProcessedContent with extracted text

        Example:
            >>> result = agent.process_pdf("report.pdf")
            >>> print(result.extracted_text)
            >>> print(result.metadata["page_count"])
        """
        pdf_path = Path(pdf_path)
        extracted_text = ""
        metadata = {}

        try:
            # Try pdfplumber first (better for structured PDFs)
            if self.processors_available["pdfplumber"]:
                import pdfplumber

                with pdfplumber.open(pdf_path) as pdf:
                    metadata["page_count"] = len(pdf.pages)

                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            extracted_text += text + "\n\n"

            # Fallback to PyPDF2
            elif self.processors_available["PyPDF2"]:
                import PyPDF2

                with open(pdf_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    metadata["page_count"] = len(reader.pages)

                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            extracted_text += text + "\n\n"

            else:
                return ProcessedContent(
                    content_type="pdf",
                    error="No PDF processor available. Install PyPDF2 or pdfplumber"
                )

            extracted_text = extracted_text.strip()

            # Generate summary if Ollama available
            summary = None
            if self.processors_available["ollama"] and extracted_text:
                try:
                    import ollama

                    # Summarize if text is long
                    if len(extracted_text) > 1000:
                        response = ollama.chat(
                            model="llama2",
                            messages=[{
                                "role": "user",
                                "content": f"Summarize this PDF content in 2-3 paragraphs:\n\n{extracted_text[:4000]}"
                            }]
                        )
                        summary = response["message"]["content"]

                except Exception as e:
                    logger.warning(f"Failed to generate PDF summary: {e}")

            return ProcessedContent(
                content_type="pdf",
                extracted_text=extracted_text,
                summary=summary,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Failed to process PDF: {e}")
            return ProcessedContent(
                content_type="pdf",
                error=str(e)
            )

    def process_document(self, doc_path: Union[str, Path]) -> ProcessedContent:
        """
        Process text document.

        Args:
            doc_path: Path to document

        Returns:
            ProcessedContent with text content
        """
        doc_path = Path(doc_path)

        try:
            with open(doc_path, "r", encoding="utf-8") as f:
                content = f.read()

            metadata = {
                "char_count": len(content),
                "line_count": content.count("\n") + 1,
                "word_count": len(content.split())
            }

            return ProcessedContent(
                content_type="document",
                extracted_text=content,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            return ProcessedContent(
                content_type="document",
                error=str(e)
            )

    def describe_image_with_prompt(
        self,
        image_path: Union[str, Path],
        prompt: str
    ) -> Optional[str]:
        """
        Describe image with custom prompt.

        Args:
            image_path: Path to image
            prompt: Custom prompt for vision model

        Returns:
            Model response

        Example:
            >>> response = agent.describe_image_with_prompt(
            ...     "diagram.png",
            ...     "What is this diagram showing? Explain the relationships."
            ... )
        """
        if not self.processors_available["ollama"]:
            logger.error("Ollama not available")
            return None

        try:
            import ollama

            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()

            response = ollama.chat(
                model=self.ollama_vision_model,
                messages=[{
                    "role": "user",
                    "content": prompt,
                    "images": [image_data]
                }]
            )

            return response["message"]["content"]

        except Exception as e:
            logger.error(f"Failed to describe image: {e}")
            return None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    agent = MultimodalAgent()

    # Example: Process an image
    print("Processing image...")
    result = agent.process_image("example.png", extract_text=True, describe=True)
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(f"OCR Text: {result.extracted_text}")
        print(f"Description: {result.summary}")

    # Example: Process a PDF
    print("\nProcessing PDF...")
    result = agent.process_pdf("document.pdf")
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(f"Pages: {result.metadata.get('page_count')}")
        print(f"Text preview: {result.extracted_text[:200]}...")

    # Example: Auto-detect and process
    print("\nAuto-processing file...")
    result = agent.process_file("unknown_file.pdf")
    print(f"Type: {result.content_type}")
