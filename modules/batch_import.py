"""
Batch Import and Folder Monitoring for Zettelkasten.

Provides utilities for batch processing documents and monitoring folders
for automatic ingestion into the knowledge base.
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
import json

from modules.document_processing import DocumentProcessor, DocumentToZettelConverter, DocumentContent
from modules.knowledge import KnowledgeManager

logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    """Result of importing a document."""
    file_path: str
    success: bool
    note_ids: List[str]
    error_message: Optional[str] = None
    tags: List[str] = None


class BatchImporter:
    """
    Batch import documents into Zettelkasten.

    Processes multiple documents at once with progress tracking and error handling.
    """

    def __init__(
        self,
        knowledge_manager: KnowledgeManager,
        ollama_client=None
    ):
        """
        Initialize batch importer.

        Args:
            knowledge_manager: KnowledgeManager for Zettelkasten operations
            ollama_client: Optional Ollama client for AI enhancements
        """
        self.knowledge_manager = knowledge_manager
        self.doc_processor = DocumentProcessor()
        self.doc_converter = DocumentToZettelConverter(ollama_client)
        self.logger = logging.getLogger("batch_importer")

    def import_directory(
        self,
        directory: Path,
        pattern: str = "*.pdf",
        strategy: str = "single",
        use_ai: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> List[ImportResult]:
        """
        Import all matching documents from a directory.

        Args:
            directory: Directory to process
            pattern: File pattern to match (e.g., "*.pdf", "**/*.docx")
            strategy: Conversion strategy ("single", "sections", "atomic")
            use_ai: Use AI for enhanced note creation
            progress_callback: Optional callback function(current, total, filename)

        Returns:
            List of ImportResult objects
        """
        if not directory.is_dir():
            self.logger.error(f"Not a directory: {directory}")
            return []

        # Find all matching files
        files = list(directory.glob(pattern))
        total_files = len(files)

        self.logger.info(f"Found {total_files} files matching '{pattern}' in {directory}")

        results = []

        for i, file_path in enumerate(files, 1):
            if progress_callback:
                progress_callback(i, total_files, file_path.name)

            result = self.import_file(file_path, strategy=strategy, use_ai=use_ai)
            results.append(result)

            if result.success:
                self.logger.info(f"✓ [{i}/{total_files}] {file_path.name}: {len(result.note_ids)} notes created")
            else:
                self.logger.error(f"✗ [{i}/{total_files}] {file_path.name}: {result.error_message}")

        return results

    def import_file(
        self,
        file_path: Path,
        strategy: str = "single",
        use_ai: bool = True
    ) -> ImportResult:
        """
        Import a single file into Zettelkasten.

        Args:
            file_path: Path to the file
            strategy: Conversion strategy
            use_ai: Use AI for enhancement

        Returns:
            ImportResult object
        """
        try:
            # Process document
            doc = self.doc_processor.process_document(file_path)

            if not doc:
                return ImportResult(
                    file_path=str(file_path),
                    success=False,
                    note_ids=[],
                    error_message="Failed to process document (unsupported format or error)"
                )

            # Convert to notes
            notes_data = self.doc_converter.convert_to_notes(doc, strategy=strategy, use_ai=use_ai)

            # Create notes in Zettelkasten
            note_ids = []
            for note_data in notes_data:
                note_id = self.knowledge_manager.zettelkasten.create_zettel(**note_data)
                note_ids.append(note_id)

            return ImportResult(
                file_path=str(file_path),
                success=True,
                note_ids=note_ids,
                tags=doc.suggested_tags
            )

        except Exception as e:
            self.logger.error(f"Error importing {file_path}: {e}", exc_info=True)
            return ImportResult(
                file_path=str(file_path),
                success=False,
                note_ids=[],
                error_message=str(e)
            )

    def generate_report(self, results: List[ImportResult]) -> Dict:
        """
        Generate a summary report of import results.

        Args:
            results: List of ImportResult objects

        Returns:
            Dictionary with statistics and summary
        """
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        total_notes = sum(len(r.note_ids) for r in results)

        # Collect all tags
        all_tags = []
        for r in results:
            if r.tags:
                all_tags.extend(r.tags)

        # Count tag frequencies
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        report = {
            'total_files': total,
            'successful': successful,
            'failed': failed,
            'total_notes_created': total_notes,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'top_tags': top_tags,
            'errors': [
                {'file': r.file_path, 'error': r.error_message}
                for r in results if not r.success
            ]
        }

        return report

    def save_report(self, results: List[ImportResult], output_path: Path):
        """
        Save import report to JSON file.

        Args:
            results: List of ImportResult objects
            output_path: Path to save the report
        """
        report = self.generate_report(results)

        # Convert results to serializable format
        report['results'] = [
            {
                'file_path': r.file_path,
                'success': r.success,
                'note_ids': r.note_ids,
                'error_message': r.error_message,
                'tags': r.tags
            }
            for r in results
        ]

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Report saved to {output_path}")


class FolderMonitor:
    """
    Monitor a folder for new documents and automatically import them.

    Watches a directory for new files and processes them as they arrive.
    """

    def __init__(
        self,
        watch_directory: Path,
        knowledge_manager: KnowledgeManager,
        ollama_client=None,
        processed_log: Optional[Path] = None
    ):
        """
        Initialize folder monitor.

        Args:
            watch_directory: Directory to monitor
            knowledge_manager: KnowledgeManager instance
            ollama_client: Optional Ollama client
            processed_log: Path to log of processed files
        """
        self.watch_directory = watch_directory
        self.knowledge_manager = knowledge_manager
        self.batch_importer = BatchImporter(knowledge_manager, ollama_client)
        self.processed_log = processed_log or (watch_directory / ".processed_files.json")
        self.processed_files = self._load_processed_log()
        self.logger = logging.getLogger("folder_monitor")

    def _load_processed_log(self) -> Dict[str, Dict]:
        """Load log of previously processed files."""
        if self.processed_log.exists():
            try:
                with open(self.processed_log, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load processed log: {e}")
                return {}
        return {}

    def _save_processed_log(self):
        """Save log of processed files."""
        try:
            with open(self.processed_log, 'w') as f:
                json.dump(self.processed_files, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save processed log: {e}")

    def _get_file_signature(self, file_path: Path) -> str:
        """Get a signature for a file (path + modification time)."""
        import hashlib
        stat = file_path.stat()
        signature = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
        return hashlib.md5(signature.encode()).hexdigest()

    def scan_and_process(
        self,
        pattern: str = "*.pdf",
        strategy: str = "single",
        use_ai: bool = True
    ) -> List[ImportResult]:
        """
        Scan directory for new files and process them.

        Args:
            pattern: File pattern to match
            strategy: Conversion strategy
            use_ai: Use AI for enhancement

        Returns:
            List of ImportResult for newly processed files
        """
        if not self.watch_directory.exists():
            self.logger.error(f"Watch directory does not exist: {self.watch_directory}")
            return []

        # Find all matching files
        all_files = list(self.watch_directory.glob(pattern))
        new_files = []

        # Check which files are new or modified
        for file_path in all_files:
            signature = self._get_file_signature(file_path)
            file_key = str(file_path)

            if file_key not in self.processed_files or self.processed_files[file_key] != signature:
                new_files.append(file_path)

        if not new_files:
            self.logger.info("No new files to process")
            return []

        self.logger.info(f"Found {len(new_files)} new files to process")

        # Process new files
        results = []
        for file_path in new_files:
            result = self.batch_importer.import_file(file_path, strategy=strategy, use_ai=use_ai)
            results.append(result)

            # Mark as processed if successful
            if result.success:
                signature = self._get_file_signature(file_path)
                self.processed_files[str(file_path)] = signature

        # Save processed log
        self._save_processed_log()

        return results

    def watch(
        self,
        interval: int = 60,
        pattern: str = "*.pdf",
        strategy: str = "single",
        use_ai: bool = True,
        callback: Optional[Callable] = None
    ):
        """
        Continuously watch directory for new files.

        Args:
            interval: Check interval in seconds
            pattern: File pattern to match
            strategy: Conversion strategy
            use_ai: Use AI for enhancement
            callback: Optional callback function(results) called after each scan

        Note: This is a blocking operation. Use in a separate thread or process.
        """
        self.logger.info(f"Starting folder monitor for {self.watch_directory}")
        self.logger.info(f"Checking every {interval} seconds for pattern: {pattern}")

        try:
            while True:
                results = self.scan_and_process(pattern=pattern, strategy=strategy, use_ai=use_ai)

                if results:
                    self.logger.info(f"Processed {len(results)} new files")
                    if callback:
                        callback(results)

                time.sleep(interval)

        except KeyboardInterrupt:
            self.logger.info("Folder monitor stopped by user")
        except Exception as e:
            self.logger.error(f"Folder monitor error: {e}", exc_info=True)


def create_batch_importer(knowledge_manager: KnowledgeManager, ollama_client=None) -> BatchImporter:
    """
    Convenience function to create a BatchImporter.

    Args:
        knowledge_manager: KnowledgeManager instance
        ollama_client: Optional Ollama client

    Returns:
        BatchImporter instance
    """
    return BatchImporter(knowledge_manager, ollama_client)


def create_folder_monitor(
    watch_directory: Path,
    knowledge_manager: KnowledgeManager,
    ollama_client=None
) -> FolderMonitor:
    """
    Convenience function to create a FolderMonitor.

    Args:
        watch_directory: Directory to monitor
        knowledge_manager: KnowledgeManager instance
        ollama_client: Optional Ollama client

    Returns:
        FolderMonitor instance
    """
    return FolderMonitor(watch_directory, knowledge_manager, ollama_client)


if __name__ == "__main__":
    # Example usage
    from modules.knowledge import create_knowledge_system

    km = create_knowledge_system()
    importer = create_batch_importer(km)

    # Test batch import
    test_dir = Path("test_documents")
    if test_dir.exists():
        results = importer.import_directory(test_dir, pattern="*.pdf")
        report = importer.generate_report(results)
        print(f"Imported {report['successful']}/{report['total_files']} files")
        print(f"Created {report['total_notes_created']} notes")
