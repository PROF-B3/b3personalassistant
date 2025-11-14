"""
Semantic Search for B3PersonalAssistant

Enables searching by meaning rather than just keywords using embeddings.
Supports knowledge base notes, tasks, conversations, and any text content.
"""

import logging
import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import hashlib
import numpy as np

from core.constants import DB_DIR
from core.exceptions import DatabaseException

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """A semantic search result with relevance score."""
    content: str
    source: str  # "note", "task", "conversation", etc.
    source_id: str
    similarity: float
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "source": self.source,
            "source_id": self.source_id,
            "similarity": round(self.similarity, 4),
            "metadata": self.metadata or {}
        }


class SemanticSearchEngine:
    """
    Semantic search engine using embeddings.

    Features:
    - Search by meaning, not just keywords
    - Find similar content across different sources
    - Automatic embedding generation
    - Fast similarity search using cosine similarity
    - Incremental index updates

    Example:
        >>> search = SemanticSearchEngine()
        >>> search.index_text("Python is a programming language", "note", "note_123")
        >>> results = search.search("What are some coding languages?", top_k=5)
        >>> for result in results:
        ...     print(f"{result.similarity:.2f}: {result.content}")
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        embedding_model: str = "ollama",
        model_name: str = "nomic-embed-text"
    ):
        """
        Initialize semantic search engine.

        Args:
            db_path: Path to embeddings database
            embedding_model: Model type ("ollama", "sentence-transformers", "openai")
            model_name: Specific model name to use
        """
        if db_path is None:
            db_path = f"{DB_DIR}/embeddings.db"

        self.db_path = db_path
        self.embedding_model = embedding_model
        self.model_name = model_name
        self.embedding_dim = 768  # Default for most models

        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
        self._initialize_embedding_model()

    def _initialize_database(self):
        """Create embeddings database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Embeddings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS embeddings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content_hash TEXT UNIQUE NOT NULL,
                        content TEXT NOT NULL,
                        source TEXT NOT NULL,
                        source_id TEXT NOT NULL,
                        embedding BLOB NOT NULL,
                        metadata TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)

                # Indexes
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_source
                    ON embeddings(source)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_source_id
                    ON embeddings(source_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_hash
                    ON embeddings(content_hash)
                """)

                conn.commit()
                logger.info("Embeddings database initialized")

        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to initialize embeddings database: {e}") from e

    def _initialize_embedding_model(self):
        """Initialize the embedding model."""
        if self.embedding_model == "ollama":
            try:
                import ollama
                self.embedder = ollama
                logger.info(f"Initialized Ollama embeddings with model: {self.model_name}")
            except ImportError:
                logger.error("Ollama not installed. Install with: pip install ollama")
                raise

        elif self.embedding_model == "sentence-transformers":
            try:
                from sentence_transformers import SentenceTransformer
                self.embedder = SentenceTransformer(self.model_name)
                self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
                logger.info(f"Initialized SentenceTransformer: {self.model_name}")
            except ImportError:
                logger.error("sentence-transformers not installed. "
                           "Install with: pip install sentence-transformers")
                raise

        elif self.embedding_model == "openai":
            try:
                import openai
                self.embedder = openai
                self.embedding_dim = 1536  # OpenAI ada-002 dimension
                logger.info("Initialized OpenAI embeddings")
            except ImportError:
                logger.error("openai not installed. Install with: pip install openai")
                raise

        else:
            raise ValueError(f"Unknown embedding model: {self.embedding_model}")

    def _generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Numpy array of embedding vector
        """
        try:
            if self.embedding_model == "ollama":
                response = self.embedder.embeddings(
                    model=self.model_name,
                    prompt=text
                )
                return np.array(response["embedding"], dtype=np.float32)

            elif self.embedding_model == "sentence-transformers":
                embedding = self.embedder.encode(text, convert_to_numpy=True)
                return embedding.astype(np.float32)

            elif self.embedding_model == "openai":
                response = self.embedder.Embedding.create(
                    input=text,
                    model=self.model_name
                )
                return np.array(response["data"][0]["embedding"], dtype=np.float32)

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def _compute_content_hash(self, content: str) -> str:
        """Compute hash of content for deduplication."""
        return hashlib.sha256(content.encode()).hexdigest()

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def index_text(
        self,
        content: str,
        source: str,
        source_id: str,
        metadata: Optional[Dict] = None,
        skip_if_exists: bool = True
    ) -> bool:
        """
        Index text content for semantic search.

        Args:
            content: Text content to index
            source: Source type (e.g., "note", "task", "conversation")
            source_id: Unique identifier for the source
            metadata: Optional metadata dictionary
            skip_if_exists: Skip if content hash already exists

        Returns:
            True if indexed successfully

        Example:
            >>> search.index_text(
            ...     content="Machine learning is a subset of AI",
            ...     source="note",
            ...     source_id="zettel_123",
            ...     metadata={"tags": ["AI", "ML"], "author": "user"}
            ... )
        """
        try:
            content_hash = self._compute_content_hash(content)

            # Check if already indexed
            if skip_if_exists:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT id FROM embeddings WHERE content_hash = ?",
                        (content_hash,)
                    )
                    if cursor.fetchone():
                        logger.debug(f"Content already indexed: {content_hash[:8]}...")
                        return True

            # Generate embedding
            embedding = self._generate_embedding(content)

            # Store in database
            from datetime import datetime
            now = datetime.now().isoformat()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO embeddings
                    (content_hash, content, source, source_id, embedding, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    content_hash,
                    content,
                    source,
                    source_id,
                    embedding.tobytes(),
                    json.dumps(metadata) if metadata else None,
                    now,
                    now
                ))
                conn.commit()

            logger.debug(f"Indexed: {source}:{source_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to index text: {e}")
            return False

    def search(
        self,
        query: str,
        top_k: int = 10,
        source_filter: Optional[List[str]] = None,
        min_similarity: float = 0.0
    ) -> List[SearchResult]:
        """
        Perform semantic search.

        Args:
            query: Search query
            top_k: Number of results to return
            source_filter: Filter by source types
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of search results ordered by relevance

        Example:
            >>> results = search.search(
            ...     query="How do I improve my productivity?",
            ...     top_k=5,
            ...     source_filter=["note", "task"],
            ...     min_similarity=0.5
            ... )
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)

            # Fetch all embeddings (in production, use approximate nearest neighbor)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query_sql = """
                    SELECT content, source, source_id, embedding, metadata
                    FROM embeddings
                """
                params = []

                if source_filter:
                    placeholders = ",".join("?" * len(source_filter))
                    query_sql += f" WHERE source IN ({placeholders})"
                    params.extend(source_filter)

                cursor.execute(query_sql, params)

                # Compute similarities
                results = []
                for row in cursor.fetchall():
                    content, source, source_id, embedding_bytes, metadata_json = row

                    # Reconstruct embedding
                    embedding = np.frombuffer(embedding_bytes, dtype=np.float32)

                    # Compute similarity
                    similarity = self._cosine_similarity(query_embedding, embedding)

                    if similarity >= min_similarity:
                        results.append(SearchResult(
                            content=content,
                            source=source,
                            source_id=source_id,
                            similarity=similarity,
                            metadata=json.loads(metadata_json) if metadata_json else None
                        ))

                # Sort by similarity and return top_k
                results.sort(key=lambda x: x.similarity, reverse=True)
                return results[:top_k]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def find_similar(
        self,
        content: str,
        top_k: int = 5,
        exclude_exact: bool = True
    ) -> List[SearchResult]:
        """
        Find similar content to given text.

        Args:
            content: Reference content
            top_k: Number of similar items to return
            exclude_exact: Exclude exact match

        Returns:
            List of similar items

        Example:
            >>> similar = search.find_similar(
            ...     content="I need to learn Python programming",
            ...     top_k=3
            ... )
        """
        results = self.search(content, top_k=top_k + 1 if exclude_exact else top_k)

        if exclude_exact:
            content_hash = self._compute_content_hash(content)
            results = [r for r in results if self._compute_content_hash(r.content) != content_hash]

        return results[:top_k]

    def index_batch(
        self,
        items: List[Tuple[str, str, str, Optional[Dict]]],
        batch_size: int = 100
    ) -> Tuple[int, int]:
        """
        Index multiple items in batches.

        Args:
            items: List of (content, source, source_id, metadata) tuples
            batch_size: Process in batches of this size

        Returns:
            Tuple of (successful, failed) counts

        Example:
            >>> items = [
            ...     ("Text 1", "note", "note_1", {"tag": "AI"}),
            ...     ("Text 2", "note", "note_2", None),
            ... ]
            >>> success, failed = search.index_batch(items)
        """
        successful = 0
        failed = 0

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]

            for content, source, source_id, metadata in batch:
                if self.index_text(content, source, source_id, metadata):
                    successful += 1
                else:
                    failed += 1

            logger.info(f"Indexed batch {i//batch_size + 1}: "
                       f"{successful} successful, {failed} failed")

        return successful, failed

    def delete(self, source: str, source_id: str) -> bool:
        """Delete indexed content by source and ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM embeddings
                    WHERE source = ? AND source_id = ?
                """, (source, source_id))
                conn.commit()

            logger.debug(f"Deleted: {source}:{source_id}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Failed to delete: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total count
                cursor.execute("SELECT COUNT(*) FROM embeddings")
                total = cursor.fetchone()[0]

                # By source
                cursor.execute("""
                    SELECT source, COUNT(*)
                    FROM embeddings
                    GROUP BY source
                """)
                by_source = dict(cursor.fetchall())

                # Database size
                db_size_mb = Path(self.db_path).stat().st_size / (1024 * 1024)

                return {
                    "total_indexed": total,
                    "by_source": by_source,
                    "database_size_mb": round(db_size_mb, 2),
                    "embedding_model": self.embedding_model,
                    "model_name": self.model_name,
                    "embedding_dimension": self.embedding_dim
                }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize search engine
    search = SemanticSearchEngine()

    # Index some sample content
    print("Indexing sample content...")
    search.index_text(
        "Python is a high-level programming language known for its simplicity",
        "note", "note_1",
        metadata={"tags": ["programming", "python"]}
    )
    search.index_text(
        "Machine learning is a subset of artificial intelligence",
        "note", "note_2",
        metadata={"tags": ["AI", "ML"]}
    )
    search.index_text(
        "Remember to buy groceries this weekend",
        "task", "task_1",
        metadata={"priority": "medium"}
    )

    # Perform search
    print("\nSearching for 'what programming languages are easy to learn?'...")
    results = search.search("what programming languages are easy to learn?", top_k=3)

    for i, result in enumerate(results, 1):
        print(f"{i}. [{result.source}] Similarity: {result.similarity:.3f}")
        print(f"   {result.content}\n")

    # Get statistics
    print("Index Statistics:")
    print(json.dumps(search.get_statistics(), indent=2))
