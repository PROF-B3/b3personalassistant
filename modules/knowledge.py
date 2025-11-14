"""
Zettelkasten Knowledge Management System
A comprehensive note-taking and knowledge organization system with AI integration.
"""

import os
import sqlite3
import re
import hashlib
import json
import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
import markdown
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Zettel:
    """Represents a single Zettel (note) in the system."""
    id: str
    title: str
    content: str
    tags: List[str]
    category: str
    created_date: str
    modified_date: str
    links_to: List[str]  # IDs of notes this links to
    linked_from: List[str]  # IDs of notes that link to this
    metadata: Dict
    ai_insights: Optional[str] = None


class ZettelkastenSystem:
    """Main Zettelkasten knowledge management system."""

    def __init__(self, base_path: Optional[str] = None):
        # Use configurable path with sensible default
        if base_path is None:
            # Check environment variable first, then use default
            base_path = os.environ.get('B3_ZETTELKASTEN_PATH', 'knowledge_base')

        self.base_path = Path(base_path).resolve()
        self.db_path = self.base_path / "_metadata" / "zettelkasten.db"
        self._ensure_directories()
        self._init_database()
        
    def _ensure_directories(self):
        """Create necessary directory structure."""
        directories = [
            self.base_path / "1",      # Main topics
            self.base_path / "2",      # Secondary topics
            self.base_path / "A",      # Frequently accessed
            self.base_path / "Z",      # Quotes and excerpts
            self.base_path / "_metadata"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def _init_database(self):
        """Initialize SQLite database for metadata."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create main zettels table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS zettels (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,  -- JSON array
                    category TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    modified_date TEXT NOT NULL,
                    links_to TEXT,  -- JSON array
                    linked_from TEXT,  -- JSON array
                    metadata TEXT,  -- JSON object
                    ai_insights TEXT,
                    file_path TEXT NOT NULL
                )
            """)
            
            # Create tags index
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    tag TEXT,
                    zettel_id TEXT,
                    PRIMARY KEY (tag, zettel_id),
                    FOREIGN KEY (zettel_id) REFERENCES zettels (id)
                )
            """)
            
            # Create links table for bidirectional linking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS links (
                    source_id TEXT,
                    target_id TEXT,
                    link_type TEXT DEFAULT 'normal',
                    created_date TEXT,
                    PRIMARY KEY (source_id, target_id),
                    FOREIGN KEY (source_id) REFERENCES zettels (id),
                    FOREIGN KEY (target_id) REFERENCES zettels (id)
                )
            """)
            
            # Create search index
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS search_index 
                USING fts5(id, title, content, tags)
            """)
            
            conn.commit()
    
    def _get_next_id(self, category: str) -> str:
        """Generate next available ID for a category."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get existing IDs in this category
            cursor.execute("""
                SELECT id FROM zettels 
                WHERE category = ? 
                ORDER BY id
            """, (category,))
            
            existing_ids = [row[0] for row in cursor.fetchall()]
            
            if not existing_ids:
                return f"{category}1"
            
            # Find the highest number and increment
            numbers = []
            for zettel_id in existing_ids:
                if zettel_id.startswith(category):
                    suffix = zettel_id[len(category):]
                    if suffix.isdigit():
                        numbers.append(int(suffix))
                    elif suffix and suffix[0].isalpha():
                        # Handle sub-notes like 1a, 1b, etc.
                        base = suffix[0]
                        if len(suffix) > 1 and suffix[1:].isdigit():
                            numbers.append(ord(base) * 1000 + int(suffix[1:]))
                        else:
                            numbers.append(ord(base) * 1000)
            
            if not numbers:
                return f"{category}1"
            
            max_num = max(numbers)
            
            # Generate next ID
            if max_num < 1000:  # Main category numbers
                return f"{category}{max_num + 1}"
            else:  # Sub-notes
                base_char = chr(max_num // 1000)
                sub_num = max_num % 1000
                return f"{category}{base_char}{sub_num + 1}"
    
    def create_zettel(self, title: str, content: str, category: str = "1", 
                     tags: List[str] = None, links_to: List[str] = None,
                     metadata: Dict = None) -> str:
        """Create a new Zettel."""
        zettel_id = self._get_next_id(category)
        now = datetime.datetime.now().isoformat()
        
        # Prepare data
        tags = tags or []
        links_to = links_to or []
        metadata = metadata or {}
        
        # Determine file path
        file_path = self.base_path / category / f"{zettel_id}.md"
        
        # Create markdown file
        markdown_content = self._create_markdown_content(title, content, tags, links_to)
        file_path.write_text(markdown_content, encoding='utf-8')
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO zettels 
                (id, title, content, tags, category, created_date, modified_date, 
                 links_to, linked_from, metadata, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                zettel_id, title, content, json.dumps(tags), category, now, now,
                json.dumps(links_to), json.dumps([]), json.dumps(metadata), str(file_path)
            ))
            
            # Add tags to tags table
            for tag in tags:
                cursor.execute("""
                    INSERT OR IGNORE INTO tags (tag, zettel_id) VALUES (?, ?)
                """, (tag, zettel_id))
            
            # Add links
            for target_id in links_to:
                cursor.execute("""
                    INSERT OR IGNORE INTO links (source_id, target_id, created_date)
                    VALUES (?, ?, ?)
                """, (zettel_id, target_id, now))
                
                # Update linked_from for target
                cursor.execute("SELECT linked_from FROM zettels WHERE id = ?", (target_id,))
                result = cursor.fetchone()
                if result:
                    linked_from = json.loads(result[0]) if result[0] else []
                    if zettel_id not in linked_from:
                        linked_from.append(zettel_id)
                        cursor.execute("""
                            UPDATE zettels SET linked_from = ? WHERE id = ?
                        """, (json.dumps(linked_from), target_id))
            
            # Update search index
            cursor.execute("""
                INSERT INTO search_index (id, title, content, tags)
                VALUES (?, ?, ?, ?)
            """, (zettel_id, title, content, json.dumps(tags)))
            
            conn.commit()
        
        logger.info(f"Created Zettel {zettel_id}: {title}")
        return zettel_id
    
    def _create_markdown_content(self, title: str, content: str, tags: List[str], 
                               links_to: List[str]) -> str:
        """Create markdown content for a Zettel."""
        lines = [
            f"# {title}",
            "",
            content,
            ""
        ]
        
        if tags:
            lines.append(f"**Tags:** {', '.join(tags)}")
            lines.append("")
        
        if links_to:
            lines.append("**Links to:**")
            for link_id in links_to:
                lines.append(f"- [[{link_id}]]")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_zettel(self, zettel_id: str) -> Optional[Zettel]:
        """Retrieve a Zettel by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, content, tags, category, created_date, 
                       modified_date, links_to, linked_from, metadata, ai_insights
                FROM zettels WHERE id = ?
            """, (zettel_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return Zettel(
                id=row[0],
                title=row[1],
                content=row[2],
                tags=json.loads(row[3]) if row[3] else [],
                category=row[4],
                created_date=row[5],
                modified_date=row[6],
                links_to=json.loads(row[7]) if row[7] else [],
                linked_from=json.loads(row[8]) if row[8] else [],
                metadata=json.loads(row[9]) if row[9] else {},
                ai_insights=row[10]
            )
    
    def update_zettel(self, zettel_id: str, title: str = None, content: str = None,
                     tags: List[str] = None, links_to: List[str] = None,
                     metadata: Dict = None) -> bool:
        """Update an existing Zettel."""
        zettel = self.get_zettel(zettel_id)
        if not zettel:
            return False
        
        # Update fields
        if title is not None:
            zettel.title = title
        if content is not None:
            zettel.content = content
        if tags is not None:
            zettel.tags = tags
        if links_to is not None:
            zettel.links_to = links_to
        if metadata is not None:
            zettel.metadata.update(metadata)
        
        zettel.modified_date = datetime.datetime.now().isoformat()
        
        # Update file
        file_path = self.base_path / zettel.category / f"{zettel_id}.md"
        markdown_content = self._create_markdown_content(
            zettel.title, zettel.content, zettel.tags, zettel.links_to
        )
        file_path.write_text(markdown_content, encoding='utf-8')
        
        # Update database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE zettels SET 
                title = ?, content = ?, tags = ?, links_to = ?, 
                modified_date = ?, metadata = ?
                WHERE id = ?
            """, (
                zettel.title, zettel.content, json.dumps(zettel.tags),
                json.dumps(zettel.links_to), zettel.modified_date,
                json.dumps(zettel.metadata), zettel_id
            ))
            
            # Update tags
            cursor.execute("DELETE FROM tags WHERE zettel_id = ?", (zettel_id,))
            for tag in zettel.tags:
                cursor.execute("""
                    INSERT OR IGNORE INTO tags (tag, zettel_id) VALUES (?, ?)
                """, (tag, zettel_id))
            
            # Update search index
            cursor.execute("""
                UPDATE search_index SET 
                title = ?, content = ?, tags = ?
                WHERE id = ?
            """, (zettel.title, zettel.content, json.dumps(zettel.tags), zettel_id))
            
            conn.commit()
        
        logger.info(f"Updated Zettel {zettel_id}")
        return True
    
    def delete_zettel(self, zettel_id: str) -> bool:
        """Delete a Zettel."""
        zettel = self.get_zettel(zettel_id)
        if not zettel:
            return False
        
        # Delete file
        file_path = self.base_path / zettel.category / f"{zettel_id}.md"
        if file_path.exists():
            file_path.unlink()
        
        # Update database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Remove from main table
            cursor.execute("DELETE FROM zettels WHERE id = ?", (zettel_id,))
            
            # Remove tags
            cursor.execute("DELETE FROM tags WHERE zettel_id = ?", (zettel_id,))
            
            # Remove links
            cursor.execute("DELETE FROM links WHERE source_id = ? OR target_id = ?", 
                         (zettel_id, zettel_id))
            
            # Update linked_from for other notes
            for linked_id in zettel.linked_from:
                cursor.execute("SELECT linked_from FROM zettels WHERE id = ?", (linked_id,))
                result = cursor.fetchone()
                if result:
                    linked_from = json.loads(result[0]) if result[0] else []
                    if zettel_id in linked_from:
                        linked_from.remove(zettel_id)
                        cursor.execute("""
                            UPDATE zettels SET linked_from = ? WHERE id = ?
                        """, (json.dumps(linked_from), linked_id))
            
            # Remove from search index
            cursor.execute("DELETE FROM search_index WHERE id = ?", (zettel_id,))
            
            conn.commit()
        
        logger.info(f"Deleted Zettel {zettel_id}")
        return True
    
    def search_zettels(self, query: str, limit: int = 50) -> List[Zettel]:
        """Search Zettels using full-text search."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM search_index 
                WHERE search_index MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))
            
            zettel_ids = [row[0] for row in cursor.fetchall()]
            
            # Get full Zettel objects
            zettels = []
            for zettel_id in zettel_ids:
                zettel = self.get_zettel(zettel_id)
                if zettel:
                    zettels.append(zettel)
            
            return zettels
    
    def get_zettels_by_tag(self, tag: str) -> List[Zettel]:
        """Get all Zettels with a specific tag."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT zettel_id FROM tags WHERE tag = ?
            """, (tag,))
            
            zettel_ids = [row[0] for row in cursor.fetchall()]
            
            zettels = []
            for zettel_id in zettel_ids:
                zettel = self.get_zettel(zettel_id)
                if zettel:
                    zettels.append(zettel)
            
            return zettels
    
    def get_zettels_by_category(self, category: str) -> List[Zettel]:
        """Get all Zettels in a specific category."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM zettels WHERE category = ? ORDER BY id
            """, (category,))
            
            zettel_ids = [row[0] for row in cursor.fetchall()]
            
            zettels = []
            for zettel_id in zettel_ids:
                zettel = self.get_zettel(zettel_id)
                if zettel:
                    zettels.append(zettel)
            
            return zettels
    
    def get_related_zettels(self, zettel_id: str, max_related: int = 10) -> List[Zettel]:
        """Get Zettels related to a given Zettel through links."""
        zettel = self.get_zettel(zettel_id)
        if not zettel:
            return []
        
        related_ids = set(zettel.links_to + zettel.linked_from)
        related_zettels = []
        
        for related_id in list(related_ids)[:max_related]:
            related_zettel = self.get_zettel(related_id)
            if related_zettel:
                related_zettels.append(related_zettel)
        
        return related_zettels
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags in the system."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT tag FROM tags ORDER BY tag")
            return [row[0] for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """Get system statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total zettels
            cursor.execute("SELECT COUNT(*) FROM zettels")
            total_zettels = cursor.fetchone()[0]
            
            # Zettels by category
            cursor.execute("""
                SELECT category, COUNT(*) FROM zettels 
                GROUP BY category ORDER BY category
            """)
            by_category = dict(cursor.fetchall())
            
            # Total tags
            cursor.execute("SELECT COUNT(DISTINCT tag) FROM tags")
            total_tags = cursor.fetchone()[0]
            
            # Total links
            cursor.execute("SELECT COUNT(*) FROM links")
            total_links = cursor.fetchone()[0]
            
            return {
                "total_zettels": total_zettels,
                "by_category": by_category,
                "total_tags": total_tags,
                "total_links": total_links
            }
    
    def create_meta_note(self, topic: str, ai_insights: str = None) -> str:
        """Create a meta-note for a topic with AI insights."""
        # Check if meta-note already exists
        existing = self.search_zettels(f"topic:{topic}")
        if existing:
            return existing[0].id
        
        # Create meta-note
        content = f"# Meta-Note: {topic}\n\n"
        if ai_insights:
            content += f"## AI Insights\n\n{ai_insights}\n\n"
        
        content += "## Related Zettels\n\n"
        
        # Find related zettels
        related = self.search_zettels(topic)
        for zettel in related[:10]:  # Limit to 10 most relevant
            content += f"- [[{zettel.id}]] - {zettel.title}\n"
        
        zettel_id = self.create_zettel(
            title=f"Meta: {topic}",
            content=content,
            category="A",  # Frequently accessed
            tags=["meta-note", "topic", topic.lower()],
            metadata={"type": "meta-note", "topic": topic}
        )
        
        # Add AI insights if provided
        if ai_insights:
            self.add_ai_insights(zettel_id, ai_insights)
        
        return zettel_id
    
    def add_ai_insights(self, zettel_id: str, insights: str):
        """Add AI insights to a Zettel."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE zettels SET ai_insights = ? WHERE id = ?
            """, (insights, zettel_id))
            conn.commit()
    
    def export_zettel(self, zettel_id: str, format: str = "markdown") -> str:
        """Export a Zettel in various formats."""
        zettel = self.get_zettel(zettel_id)
        if not zettel:
            return ""
        
        if format == "markdown":
            return self._create_markdown_content(
                zettel.title, zettel.content, zettel.tags, zettel.links_to
            )
        elif format == "json":
            return json.dumps(asdict(zettel), indent=2)
        elif format == "html":
            md_content = self._create_markdown_content(
                zettel.title, zettel.content, zettel.tags, zettel.links_to
            )
            return markdown.markdown(md_content)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_zettel(self, title: str, content: str, category: str = "1",
                     tags: List[str] = None, links_to: List[str] = None) -> str:
        """Import a Zettel from external source."""
        return self.create_zettel(title, content, category, tags, links_to)
    
    def get_backlinks(self, zettel_id: str) -> List[Zettel]:
        """Get all Zettels that link to the given Zettel."""
        zettel = self.get_zettel(zettel_id)
        if not zettel:
            return []
        
        backlinks = []
        for linked_id in zettel.linked_from:
            linked_zettel = self.get_zettel(linked_id)
            if linked_zettel:
                backlinks.append(linked_zettel)
        
        return backlinks
    
    def get_orphaned_zettels(self) -> List[Zettel]:
        """Get Zettels with no links (orphaned)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM zettels 
                WHERE (links_to IS NULL OR links_to = '[]') 
                AND (linked_from IS NULL OR linked_from = '[]')
            """)
            
            zettel_ids = [row[0] for row in cursor.fetchall()]
            
            zettels = []
            for zettel_id in zettel_ids:
                zettel = self.get_zettel(zettel_id)
                if zettel:
                    zettels.append(zettel)
            
            return zettels


class KnowledgeManager:
    """High-level knowledge management interface for agents."""
    
    def __init__(self, zettelkasten: ZettelkastenSystem):
        self.zettelkasten = zettelkasten
    
    def quick_note(self, content: str, tags: List[str] = None) -> str:
        """Create a quick note in the A (frequently accessed) category."""
        title = content[:50] + "..." if len(content) > 50 else content
        return self.zettelkasten.create_zettel(
            title=title,
            content=content,
            category="A",
            tags=tags or []
        )
    
    def research_topic(self, topic: str, ai_insights: str = None) -> str:
        """Create or update a research topic with AI insights."""
        return self.zettelkasten.create_meta_note(topic, ai_insights)
    
    def link_notes(self, source_id: str, target_id: str):
        """Create a link between two notes."""
        source = self.zettelkasten.get_zettel(source_id)
        target = self.zettelkasten.get_zettel(target_id)
        
        if not source or not target:
            return False
        
        if target_id not in source.links_to:
            source.links_to.append(target_id)
            self.zettelkasten.update_zettel(
                source_id, links_to=source.links_to
            )
        
        return True
    
    def find_connections(self, query: str) -> List[Dict]:
        """Find connections between notes based on a query."""
        results = self.zettelkasten.search_zettels(query)
        connections = []
        
        for zettel in results:
            related = self.zettelkasten.get_related_zettels(zettel.id)
            connections.append({
                "zettel": zettel,
                "related": related,
                "relevance_score": len(related)  # Simple scoring
            })
        
        return sorted(connections, key=lambda x: x["relevance_score"], reverse=True)
    
    def get_knowledge_graph(self, max_nodes: int = 50) -> Dict:
        """Get a knowledge graph representation of the system."""
        with sqlite3.connect(self.zettelkasten.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT source_id, target_id FROM links 
                LIMIT ?
            """, (max_nodes,))
            
            edges = cursor.fetchall()
            
            nodes = set()
            for source_id, target_id in edges:
                nodes.add(source_id)
                nodes.add(target_id)
            
            return {
                "nodes": list(nodes),
                "edges": [{"source": source, "target": target} for source, target in edges]
            }


# Convenience functions for easy access
def create_knowledge_system(base_path: str = "X") -> KnowledgeManager:
    """Create and return a knowledge management system."""
    zettelkasten = ZettelkastenSystem(base_path)
    return KnowledgeManager(zettelkasten)


if __name__ == "__main__":
    # Test the system
    km = create_knowledge_system()
    
    # Create some test notes
    note1_id = km.quick_note("This is a test note about AI", ["ai", "test"])
    note2_id = km.quick_note("Another note about machine learning", ["ml", "ai"])
    
    # Link them
    km.link_notes(note1_id, note2_id)
    
    # Search
    results = km.zettelkasten.search_zettels("AI")
    print(f"Found {len(results)} notes about AI")
    
    # Get statistics
    stats = km.zettelkasten.get_statistics()
    print(f"System statistics: {stats}")
 