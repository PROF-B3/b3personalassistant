"""
Citation Management Module for B3PersonalAssistant.

Provides citation extraction from PDFs, bibliography generation,
and reference formatting in multiple styles.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    """Represents a single citation/reference."""
    cite_key: str  # Unique identifier
    title: str
    authors: List[str]
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    venue: Optional[str] = None  # Journal/Conference
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    entry_type: str = "article"  # article, book, inproceedings, misc

    def to_bibtex(self) -> str:
        """Generate BibTeX entry."""
        bibtex = f"@{self.entry_type}{{{self.cite_key},\n"
        bibtex += f"  title = {{{self.title}}},\n"

        if self.authors:
            authors_str = " and ".join(self.authors)
            bibtex += f"  author = {{{authors_str}}},\n"

        if self.year:
            bibtex += f"  year = {{{self.year}}},\n"

        if self.venue:
            if self.entry_type == "article":
                bibtex += f"  journal = {{{self.venue}}},\n"
            elif self.entry_type == "inproceedings":
                bibtex += f"  booktitle = {{{self.venue}}},\n"
            else:
                bibtex += f"  publisher = {{{self.venue}}},\n"

        if self.volume:
            bibtex += f"  volume = {{{self.volume}}},\n"

        if self.issue:
            bibtex += f"  number = {{{self.issue}}},\n"

        if self.pages:
            bibtex += f"  pages = {{{self.pages}}},\n"

        if self.doi:
            bibtex += f"  doi = {{{self.doi}}},\n"

        if self.url:
            bibtex += f"  url = {{{self.url}}},\n"

        if self.isbn:
            bibtex += f"  isbn = {{{self.isbn}}},\n"

        bibtex += "}\n"
        return bibtex

    def to_apa(self) -> str:
        """Generate APA 7th edition citation."""
        citation = ""

        # Authors
        if self.authors:
            if len(self.authors) == 1:
                citation += f"{self.authors[0]}"
            elif len(self.authors) == 2:
                citation += f"{self.authors[0]}, & {self.authors[1]}"
            elif len(self.authors) <= 20:
                citation += ", ".join(self.authors[:-1]) + f", & {self.authors[-1]}"
            else:
                citation += ", ".join(self.authors[:19]) + ", ... " + self.authors[-1]

        # Year
        if self.year:
            citation += f" ({self.year}). "
        else:
            citation += " (n.d.). "

        # Title
        citation += f"{self.title}. "

        # Venue/Journal
        if self.venue:
            citation += f"*{self.venue}*"

            if self.volume:
                citation += f", *{self.volume}*"

            if self.issue:
                citation += f"({self.issue})"

            if self.pages:
                citation += f", {self.pages}"

            citation += ". "

        # DOI or URL
        if self.doi:
            citation += f"https://doi.org/{self.doi}"
        elif self.url:
            citation += self.url

        return citation

    def to_mla(self) -> str:
        """Generate MLA 9th edition citation."""
        citation = ""

        # Authors
        if self.authors:
            first_author = self.authors[0]
            # Reverse first author: Last, First
            parts = first_author.split()
            if len(parts) >= 2:
                citation += f"{parts[-1]}, {' '.join(parts[:-1])}"
            else:
                citation += first_author

            if len(self.authors) > 1:
                citation += ", et al"

            citation += ". "

        # Title
        citation += f"\"{self.title}.\" "

        # Venue
        if self.venue:
            citation += f"*{self.venue}*, "

        # Volume and issue
        if self.volume:
            citation += f"vol. {self.volume}, "

        if self.issue:
            citation += f"no. {self.issue}, "

        # Year
        if self.year:
            citation += f"{self.year}, "

        # Pages
        if self.pages:
            citation += f"pp. {self.pages}. "

        # DOI or URL
        if self.doi:
            citation += f"https://doi.org/{self.doi}."
        elif self.url:
            citation += f"{self.url}."

        return citation

    def to_chicago(self) -> str:
        """Generate Chicago style citation."""
        citation = ""

        # Authors
        if self.authors:
            first_author = self.authors[0]
            # Reverse first author: Last, First
            parts = first_author.split()
            if len(parts) >= 2:
                citation += f"{parts[-1]}, {' '.join(parts[:-1])}"
            else:
                citation += first_author

            if len(self.authors) > 1:
                citation += " et al"

            citation += ". "

        # Year
        if self.year:
            citation += f"{self.year}. "

        # Title
        citation += f"\"{self.title}.\" "

        # Venue
        if self.venue:
            citation += f"*{self.venue}* "

        # Volume and issue
        if self.volume:
            citation += f"{self.volume} "

        if self.issue:
            citation += f"({self.issue})"

        # Pages
        if self.pages:
            citation += f": {self.pages}. "

        # DOI
        if self.doi:
            citation += f"https://doi.org/{self.doi}."

        return citation


class CitationManager:
    """
    Manages citations and bibliography generation.

    Provides:
    - Citation extraction from PDFs
    - Bibliography storage
    - Reference formatting (BibTeX, APA, MLA, Chicago)
    - Citation key generation
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize citation manager.

        Args:
            storage_path: Path to store bibliography database
        """
        self.logger = logging.getLogger("citation_manager")
        self.storage_path = storage_path or Path("databases/bibliography")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.citations: Dict[str, Citation] = {}
        self._load_citations()

    def extract_from_pdf(self, pdf_path: Path) -> Optional[Citation]:
        """
        Extract citation metadata from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Citation object or None
        """
        try:
            import PyPDF2

            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                metadata = reader.metadata

                if not metadata:
                    self.logger.warning(f"No metadata found in {pdf_path}")
                    return None

                # Extract available fields
                title = metadata.get('/Title', pdf_path.stem)
                author = metadata.get('/Author', 'Unknown')

                # Parse authors
                authors = [a.strip() for a in author.split(',')]

                # Try to extract year from creation date
                year = None
                creation_date = metadata.get('/CreationDate')
                if creation_date:
                    # Format: D:YYYYMMDDHHmmSS
                    match = re.search(r'D:(\d{4})', creation_date)
                    if match:
                        year = int(match.group(1))

                # Generate cite key
                cite_key = self._generate_cite_key(title, authors, year)

                # Try to extract DOI from first page
                doi = self._extract_doi_from_pdf(reader)

                citation = Citation(
                    cite_key=cite_key,
                    title=title,
                    authors=authors,
                    year=year,
                    doi=doi
                )

                # Add to collection
                self.add_citation(citation)

                return citation

        except Exception as e:
            self.logger.error(f"Error extracting citation from {pdf_path}: {e}")
            return None

    def _extract_doi_from_pdf(self, reader) -> Optional[str]:
        """Try to extract DOI from PDF text."""
        try:
            # Check first few pages for DOI
            for page_num in range(min(3, len(reader.pages))):
                text = reader.pages[page_num].extract_text()

                # DOI pattern
                doi_pattern = r'10\.\d{4,}/[^\s]+'
                match = re.search(doi_pattern, text)

                if match:
                    return match.group(0)

        except Exception as e:
            self.logger.error(f"Error extracting DOI: {e}")

        return None

    def add_citation(self, citation: Citation):
        """
        Add citation to bibliography.

        Args:
            citation: Citation object
        """
        self.citations[citation.cite_key] = citation
        self._save_citations()
        self.logger.info(f"Added citation: {citation.cite_key}")

    def get_citation(self, cite_key: str) -> Optional[Citation]:
        """Get citation by key."""
        return self.citations.get(cite_key)

    def remove_citation(self, cite_key: str) -> bool:
        """Remove citation from bibliography."""
        if cite_key in self.citations:
            del self.citations[cite_key]
            self._save_citations()
            return True
        return False

    def search_citations(self, query: str) -> List[Citation]:
        """
        Search citations by title or author.

        Args:
            query: Search query

        Returns:
            List of matching citations
        """
        query_lower = query.lower()
        results = []

        for citation in self.citations.values():
            if query_lower in citation.title.lower():
                results.append(citation)
            elif any(query_lower in author.lower() for author in citation.authors):
                results.append(citation)

        return results

    def generate_bibliography(
        self,
        style: str = "apa",
        cite_keys: Optional[List[str]] = None
    ) -> str:
        """
        Generate bibliography in specified style.

        Args:
            style: Citation style (apa, mla, chicago, bibtex)
            cite_keys: Specific citations to include (None = all)

        Returns:
            Formatted bibliography
        """
        if cite_keys:
            citations = [self.citations[key] for key in cite_keys if key in self.citations]
        else:
            citations = list(self.citations.values())

        # Sort by author last name
        citations.sort(key=lambda c: c.authors[0].split()[-1] if c.authors else "")

        if style.lower() == "bibtex":
            return "\n".join(c.to_bibtex() for c in citations)
        elif style.lower() == "apa":
            return "\n\n".join(c.to_apa() for c in citations)
        elif style.lower() == "mla":
            return "\n\n".join(c.to_mla() for c in citations)
        elif style.lower() == "chicago":
            return "\n\n".join(c.to_chicago() for c in citations)
        else:
            self.logger.warning(f"Unknown style: {style}, using APA")
            return "\n\n".join(c.to_apa() for c in citations)

    def _generate_cite_key(
        self,
        title: str,
        authors: List[str],
        year: Optional[int]
    ) -> str:
        """Generate unique citation key."""
        # Format: FirstAuthorYearFirstWord
        first_author = "Unknown"
        if authors:
            parts = authors[0].split()
            first_author = parts[-1] if parts else authors[0]

        first_word = title.split()[0] if title else "Paper"
        # Remove non-alphanumeric
        first_word = re.sub(r'[^a-zA-Z]', '', first_word)

        year_str = str(year) if year else "XXXX"

        base_key = f"{first_author}{year_str}{first_word}"

        # Ensure uniqueness
        if base_key not in self.citations:
            return base_key

        # Add suffix if duplicate
        counter = 2
        while f"{base_key}_{counter}" in self.citations:
            counter += 1

        return f"{base_key}_{counter}"

    def _save_citations(self):
        """Save citations to JSON file."""
        try:
            citations_file = self.storage_path / "citations.json"

            citations_data = {
                cite_key: asdict(citation)
                for cite_key, citation in self.citations.items()
            }

            with open(citations_file, 'w') as f:
                json.dump(citations_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving citations: {e}")

    def _load_citations(self):
        """Load citations from JSON file."""
        try:
            citations_file = self.storage_path / "citations.json"

            if not citations_file.exists():
                return

            with open(citations_file, 'r') as f:
                citations_data = json.load(f)

            for cite_key, data in citations_data.items():
                self.citations[cite_key] = Citation(**data)

            self.logger.info(f"Loaded {len(self.citations)} citations")

        except Exception as e:
            self.logger.error(f"Error loading citations: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get bibliography statistics."""
        return {
            'total_citations': len(self.citations),
            'by_type': self._count_by_field('entry_type'),
            'by_year': self._count_by_field('year'),
            'citations_with_doi': len([c for c in self.citations.values() if c.doi])
        }

    def _count_by_field(self, field: str) -> Dict:
        """Count citations by field value."""
        counts = {}
        for citation in self.citations.values():
            value = getattr(citation, field, None)
            if value:
                counts[str(value)] = counts.get(str(value), 0) + 1
        return counts


def create_citation_manager(storage_path: Optional[Path] = None) -> CitationManager:
    """Convenience function to create citation manager."""
    return CitationManager(storage_path)
