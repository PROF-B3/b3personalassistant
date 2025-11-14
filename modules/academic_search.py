"""
Academic Search Module for B3PersonalAssistant.

Provides web search capabilities for academic papers across multiple sources:
- Google Scholar
- arXiv
- CrossRef
- Semantic Scholar
"""

import logging
import requests
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import time

logger = logging.getLogger(__name__)


@dataclass
class AcademicPaper:
    """Represents an academic paper from search results."""
    title: str
    authors: List[str]
    year: Optional[int] = None
    abstract: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    source: str = "unknown"  # scholar, arxiv, crossref, semantic_scholar
    citation_count: int = 0
    pdf_url: Optional[str] = None
    venue: Optional[str] = None  # Journal/Conference name
    arxiv_id: Optional[str] = None

    def to_bibtex(self, cite_key: Optional[str] = None) -> str:
        """Generate BibTeX entry for this paper."""
        if not cite_key:
            # Generate cite key: FirstAuthorYearFirstWord
            first_author = self.authors[0].split()[-1] if self.authors else "Unknown"
            first_word = self.title.split()[0] if self.title else "Paper"
            cite_key = f"{first_author}{self.year or 'XXXX'}{first_word}"

        # Determine entry type
        entry_type = "article" if self.venue else "misc"

        bibtex = f"@{entry_type}{{{cite_key},\n"
        bibtex += f"  title = {{{self.title}}},\n"

        if self.authors:
            authors_str = " and ".join(self.authors)
            bibtex += f"  author = {{{authors_str}}},\n"

        if self.year:
            bibtex += f"  year = {{{self.year}}},\n"

        if self.venue:
            bibtex += f"  journal = {{{self.venue}}},\n"

        if self.doi:
            bibtex += f"  doi = {{{self.doi}}},\n"

        if self.url:
            bibtex += f"  url = {{{self.url}}},\n"

        bibtex += "}\n"
        return bibtex

    def to_apa(self) -> str:
        """Generate APA citation."""
        citation = ""

        # Authors
        if self.authors:
            if len(self.authors) == 1:
                citation += f"{self.authors[0]}"
            elif len(self.authors) == 2:
                citation += f"{self.authors[0]} & {self.authors[1]}"
            else:
                citation += f"{self.authors[0]} et al."

        # Year
        if self.year:
            citation += f" ({self.year}). "
        else:
            citation += " (n.d.). "

        # Title
        citation += f"{self.title}. "

        # Venue
        if self.venue:
            citation += f"{self.venue}. "

        # DOI or URL
        if self.doi:
            citation += f"https://doi.org/{self.doi}"
        elif self.url:
            citation += self.url

        return citation


class AcademicSearchEngine:
    """
    Multi-source academic search engine.

    Searches across multiple academic databases and aggregates results.
    """

    def __init__(self):
        """Initialize academic search engine."""
        self.logger = logging.getLogger("academic_search")

    def search(
        self,
        query: str,
        sources: List[str] = ["arxiv", "crossref"],
        limit: int = 10
    ) -> List[AcademicPaper]:
        """
        Search for academic papers across multiple sources.

        Args:
            query: Search query
            sources: List of sources to search (arxiv, crossref, semantic_scholar)
            limit: Maximum results per source

        Returns:
            List of AcademicPaper objects
        """
        results = []

        if "arxiv" in sources:
            results.extend(self._search_arxiv(query, limit))

        if "crossref" in sources:
            results.extend(self._search_crossref(query, limit))

        if "semantic_scholar" in sources:
            results.extend(self._search_semantic_scholar(query, limit))

        # Sort by citation count (descending)
        results.sort(key=lambda p: p.citation_count, reverse=True)

        return results[:limit]

    def _search_arxiv(self, query: str, limit: int = 10) -> List[AcademicPaper]:
        """
        Search arXiv for papers.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of AcademicPaper objects
        """
        try:
            import urllib.parse

            # arXiv API endpoint
            base_url = "http://export.arxiv.org/api/query"
            encoded_query = urllib.parse.quote(query)
            url = f"{base_url}?search_query=all:{encoded_query}&start=0&max_results={limit}"

            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                self.logger.warning(f"arXiv search failed: {response.status_code}")
                return []

            # Parse arXiv XML response
            papers = self._parse_arxiv_xml(response.text)

            self.logger.info(f"Found {len(papers)} papers on arXiv for '{query}'")
            return papers

        except Exception as e:
            self.logger.error(f"arXiv search error: {e}")
            return []

    def _parse_arxiv_xml(self, xml_text: str) -> List[AcademicPaper]:
        """Parse arXiv XML response."""
        import xml.etree.ElementTree as ET

        papers = []

        try:
            root = ET.fromstring(xml_text)

            # arXiv namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}

            for entry in root.findall('atom:entry', ns):
                # Extract fields
                title = entry.find('atom:title', ns)
                title_text = title.text.strip().replace('\n', ' ') if title is not None else "Unknown"

                # Authors
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns)
                    if name is not None:
                        authors.append(name.text)

                # Published date
                published = entry.find('atom:published', ns)
                year = None
                if published is not None:
                    try:
                        year = int(published.text[:4])
                    except:
                        pass

                # Abstract
                summary = entry.find('atom:summary', ns)
                abstract = summary.text.strip() if summary is not None else None

                # Links
                pdf_url = None
                page_url = None
                for link in entry.findall('atom:link', ns):
                    if link.get('title') == 'pdf':
                        pdf_url = link.get('href')
                    elif link.get('rel') == 'alternate':
                        page_url = link.get('href')

                # arXiv ID
                arxiv_id = None
                id_elem = entry.find('atom:id', ns)
                if id_elem is not None:
                    arxiv_id = id_elem.text.split('/')[-1]

                paper = AcademicPaper(
                    title=title_text,
                    authors=authors,
                    year=year,
                    abstract=abstract,
                    url=page_url,
                    pdf_url=pdf_url,
                    source="arxiv",
                    arxiv_id=arxiv_id
                )

                papers.append(paper)

        except Exception as e:
            self.logger.error(f"Error parsing arXiv XML: {e}")

        return papers

    def _search_crossref(self, query: str, limit: int = 10) -> List[AcademicPaper]:
        """
        Search CrossRef for papers.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of AcademicPaper objects
        """
        try:
            # CrossRef API endpoint
            base_url = "https://api.crossref.org/works"
            params = {
                'query': query,
                'rows': limit,
                'select': 'title,author,published,DOI,abstract,container-title,is-referenced-by-count,URL'
            }

            response = requests.get(base_url, params=params, timeout=10)

            if response.status_code != 200:
                self.logger.warning(f"CrossRef search failed: {response.status_code}")
                return []

            data = response.json()
            papers = self._parse_crossref_json(data)

            self.logger.info(f"Found {len(papers)} papers on CrossRef for '{query}'")
            return papers

        except Exception as e:
            self.logger.error(f"CrossRef search error: {e}")
            return []

    def _parse_crossref_json(self, data: Dict) -> List[AcademicPaper]:
        """Parse CrossRef JSON response."""
        papers = []

        try:
            items = data.get('message', {}).get('items', [])

            for item in items:
                # Title
                title_list = item.get('title', ['Unknown'])
                title = title_list[0] if title_list else "Unknown"

                # Authors
                authors = []
                for author in item.get('author', []):
                    given = author.get('given', '')
                    family = author.get('family', '')
                    full_name = f"{given} {family}".strip()
                    if full_name:
                        authors.append(full_name)

                # Year
                year = None
                published = item.get('published', {})
                if 'date-parts' in published:
                    date_parts = published['date-parts'][0]
                    if date_parts:
                        year = date_parts[0]

                # DOI
                doi = item.get('DOI')

                # URL
                url = item.get('URL')

                # Venue (journal/conference)
                container_title = item.get('container-title', [])
                venue = container_title[0] if container_title else None

                # Citation count
                citation_count = item.get('is-referenced-by-count', 0)

                # Abstract (often not available in CrossRef)
                abstract = item.get('abstract')

                paper = AcademicPaper(
                    title=title,
                    authors=authors,
                    year=year,
                    abstract=abstract,
                    doi=doi,
                    url=url,
                    source="crossref",
                    venue=venue,
                    citation_count=citation_count
                )

                papers.append(paper)

        except Exception as e:
            self.logger.error(f"Error parsing CrossRef JSON: {e}")

        return papers

    def _search_semantic_scholar(self, query: str, limit: int = 10) -> List[AcademicPaper]:
        """
        Search Semantic Scholar for papers.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of AcademicPaper objects
        """
        try:
            # Semantic Scholar API endpoint
            base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                'query': query,
                'limit': limit,
                'fields': 'title,authors,year,abstract,citationCount,url,venue,externalIds'
            }

            response = requests.get(base_url, params=params, timeout=10)

            if response.status_code != 200:
                self.logger.warning(f"Semantic Scholar search failed: {response.status_code}")
                return []

            data = response.json()
            papers = self._parse_semantic_scholar_json(data)

            self.logger.info(f"Found {len(papers)} papers on Semantic Scholar for '{query}'")
            return papers

        except Exception as e:
            self.logger.error(f"Semantic Scholar search error: {e}")
            return []

    def _parse_semantic_scholar_json(self, data: Dict) -> List[AcademicPaper]:
        """Parse Semantic Scholar JSON response."""
        papers = []

        try:
            items = data.get('data', [])

            for item in items:
                # Title
                title = item.get('title', 'Unknown')

                # Authors
                authors = []
                for author in item.get('authors', []):
                    name = author.get('name')
                    if name:
                        authors.append(name)

                # Year
                year = item.get('year')

                # Abstract
                abstract = item.get('abstract')

                # URL
                url = item.get('url')

                # Venue
                venue = item.get('venue')

                # Citation count
                citation_count = item.get('citationCount', 0)

                # External IDs (DOI, arXiv)
                external_ids = item.get('externalIds', {})
                doi = external_ids.get('DOI')
                arxiv_id = external_ids.get('ArXiv')

                paper = AcademicPaper(
                    title=title,
                    authors=authors,
                    year=year,
                    abstract=abstract,
                    doi=doi,
                    url=url,
                    source="semantic_scholar",
                    venue=venue,
                    citation_count=citation_count,
                    arxiv_id=arxiv_id
                )

                papers.append(paper)

        except Exception as e:
            self.logger.error(f"Error parsing Semantic Scholar JSON: {e}")

        return papers


def create_academic_search() -> AcademicSearchEngine:
    """Convenience function to create academic search engine."""
    return AcademicSearchEngine()
