"""
Conversation Management System
A comprehensive system for managing AI conversations with learning and analysis capabilities.
"""

import sqlite3
import json
import datetime
import re
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from datetime import datetime, timedelta
import hashlib
import uuid

from core.exceptions import DatabaseException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Sentiment(Enum):
    """Conversation sentiment levels."""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class QualityScore(Enum):
    """Conversation quality levels."""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


@dataclass
class ConversationMessage:
    """Represents a single message in a conversation."""
    id: int
    session_id: str
    agent_name: str
    user_message: str
    agent_response: str
    timestamp: str
    context: Dict[str, Any]
    message_type: str  # "user", "agent", "system"
    metadata: Dict[str, Any]


@dataclass
class ConversationSession:
    """Represents a conversation session."""
    session_id: str
    topic: str
    start_time: str
    end_time: Optional[str]
    agent_name: str
    sentiment: Sentiment
    quality_score: QualityScore
    user_satisfaction: Optional[int]  # 1-5 scale
    context_summary: str
    metadata: Dict[str, Any]


@dataclass
class UserPreference:
    """Represents a learned user preference."""
    id: int
    preference_type: str  # "communication_style", "topic_interest", "response_length", etc.
    preference_key: str
    preference_value: str
    confidence_score: float  # 0.0 to 1.0
    evidence_count: int
    last_updated: str
    metadata: Dict[str, Any]


class ConversationManager:
    """Main conversation management system."""
    
    def __init__(self, db_path: str = "databases/conversations.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with all required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    context TEXT,  -- JSON object
                    message_type TEXT DEFAULT 'user',
                    metadata TEXT,  -- JSON object
                    FOREIGN KEY (session_id) REFERENCES conversation_metadata (session_id)
                )
            """)
            
            # Create conversation metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_metadata (
                    session_id TEXT PRIMARY KEY,
                    topic TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    agent_name TEXT NOT NULL,
                    sentiment TEXT DEFAULT 'neutral',
                    quality_score TEXT DEFAULT 'good',
                    user_satisfaction INTEGER,
                    context_summary TEXT,
                    metadata TEXT,  -- JSON object
                    message_count INTEGER DEFAULT 0
                )
            """)
            
            # Create user preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_type TEXT NOT NULL,
                    preference_key TEXT NOT NULL,
                    preference_value TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.5,
                    evidence_count INTEGER DEFAULT 1,
                    last_updated TEXT NOT NULL,
                    metadata TEXT,  -- JSON object
                    UNIQUE(preference_type, preference_key)
                )
            """)
            
            # Create conversation search index
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS conversation_search 
                USING fts5(session_id, user_message, agent_response, topic)
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_agent ON conversations(agent_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metadata_agent ON conversation_metadata(agent_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metadata_sentiment ON conversation_metadata(sentiment)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_preferences_type ON user_preferences(preference_type)")
            
            conn.commit()
    
    def start_conversation_session(self, agent_name: str, topic: str = "", 
                                 context: Optional[Dict[str, Any]] = None) -> str:
        """Start a new conversation session."""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        context = context or {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO conversation_metadata 
                (session_id, topic, start_time, agent_name, sentiment, quality_score, 
                 context_summary, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, topic, now, agent_name, Sentiment.NEUTRAL.value,
                QualityScore.GOOD.value, "", json.dumps(context)
            ))
            
            conn.commit()
        
        logger.info(f"Started conversation session {session_id} with {agent_name}")
        return session_id
    
    def add_message(self, session_id: str, agent_name: str, user_message: str, 
                   agent_response: str, context: Optional[Dict[str, Any]] = None,
                   message_type: str = "user", metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """Add a message to a conversation session."""
        now = datetime.now().isoformat()
        context = context or {}
        metadata = metadata or {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Add message
            cursor.execute("""
                INSERT INTO conversations 
                (session_id, agent_name, user_message, agent_response, timestamp, 
                 context, message_type, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, agent_name, user_message, agent_response, now,
                json.dumps(context), message_type, json.dumps(metadata)
            ))
            
            message_id = cursor.lastrowid
            
            # Update search index
            cursor.execute("""
                INSERT INTO conversation_search (session_id, user_message, agent_response, topic)
                VALUES (?, ?, ?, (SELECT topic FROM conversation_metadata WHERE session_id = ?))
            """, (session_id, user_message, agent_response, session_id))
            
            # Update message count
            cursor.execute("""
                UPDATE conversation_metadata 
                SET message_count = message_count + 1 
                WHERE session_id = ?
            """, (session_id,))
            
            conn.commit()
        
        logger.info(f"Added message {message_id} to session {session_id}")
        return message_id
    
    def end_conversation_session(self, session_id: str, sentiment: Optional[Sentiment] = None,
                               quality_score: Optional[QualityScore] = None,
                               user_satisfaction: Optional[int] = None,
                               context_summary: str = "") -> bool:
        """End a conversation session with optional feedback."""
        now = datetime.now().isoformat()

        # Whitelist of allowed update fields for security
        ALLOWED_UPDATE_FIELDS = {'end_time', 'sentiment', 'quality_score', 'user_satisfaction', 'context_summary'}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                update_fields = ["end_time = ?"]
                params = [now]

                if sentiment:
                    if 'sentiment' not in ALLOWED_UPDATE_FIELDS:
                        raise ValueError("Invalid field: sentiment")
                    update_fields.append("sentiment = ?")
                    params.append(sentiment.value)

                if quality_score:
                    if 'quality_score' not in ALLOWED_UPDATE_FIELDS:
                        raise ValueError("Invalid field: quality_score")
                    update_fields.append("quality_score = ?")
                    params.append(quality_score.value)

                if user_satisfaction is not None:
                    if 'user_satisfaction' not in ALLOWED_UPDATE_FIELDS:
                        raise ValueError("Invalid field: user_satisfaction")
                    update_fields.append("user_satisfaction = ?")
                    params.append(str(user_satisfaction))

                if context_summary is None:
                    context_summary = ""
                if 'context_summary' not in ALLOWED_UPDATE_FIELDS:
                    raise ValueError("Invalid field: context_summary")
                update_fields.append("context_summary = ?")
                params.append(context_summary)

                params.append(session_id)

                cursor.execute(f"""
                    UPDATE conversation_metadata
                    SET {', '.join(update_fields)}
                    WHERE session_id = ?
                """, params)

                conn.commit()

            logger.info(f"Ended conversation session {session_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Database error ending conversation session {session_id}: {e}")
            raise DatabaseException(f"Failed to end conversation session: {e}") from e
        except ValueError as e:
            logger.error(f"Invalid field in update: {e}")
            raise
    
    def get_conversation_session(self, session_id: str) -> Optional[ConversationSession]:
        """Retrieve a conversation session with all metadata."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, topic, start_time, end_time, agent_name, sentiment,
                       quality_score, user_satisfaction, context_summary, metadata
                FROM conversation_metadata WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return ConversationSession(
                session_id=row[0], topic=row[1], start_time=row[2], end_time=row[3],
                agent_name=row[4], sentiment=Sentiment(row[5]), quality_score=QualityScore(row[6]),
                user_satisfaction=row[7], context_summary=row[8],
                metadata=json.loads(row[9]) if row[9] else {}
            )
    
    def get_session_messages(self, session_id: str, limit: int = 100) -> List[ConversationMessage]:
        """Get all messages in a conversation session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, session_id, agent_name, user_message, agent_response,
                       timestamp, context, message_type, metadata
                FROM conversations 
                WHERE session_id = ? 
                ORDER BY timestamp ASC 
                LIMIT ?
            """, (session_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                messages.append(ConversationMessage(
                    id=row[0], session_id=row[1], agent_name=row[2],
                    user_message=row[3], agent_response=row[4], timestamp=row[5],
                    context=json.loads(row[6]) if row[6] else {},
                    message_type=row[7], metadata=json.loads(row[8]) if row[8] else {}
                ))
            
            return messages
    
    def search_conversations(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search conversations using full-text search."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, user_message, agent_response, topic
                FROM conversation_search 
                WHERE conversation_search MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))
            
            results = []
            for row in cursor.fetchall():
                session_data = self.get_conversation_session(row[0])
                if session_data:
                    results.append({
                        "session": session_data,
                        "user_message": row[1],
                        "agent_response": row[2],
                        "topic": row[3]
                    })
            
            return results
    
    def get_conversations_by_agent(self, agent_name: str, limit: int = 50) -> List[ConversationSession]:
        """Get all conversations with a specific agent."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, topic, start_time, end_time, agent_name, sentiment,
                       quality_score, user_satisfaction, context_summary, metadata
                FROM conversation_metadata 
                WHERE agent_name = ? 
                ORDER BY start_time DESC 
                LIMIT ?
            """, (agent_name, limit))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append(ConversationSession(
                    session_id=row[0], topic=row[1], start_time=row[2], end_time=row[3],
                    agent_name=row[4], sentiment=Sentiment(row[5]), quality_score=QualityScore(row[6]),
                    user_satisfaction=row[7], context_summary=row[8],
                    metadata=json.loads(row[9]) if row[9] else {}
                ))
            
            return sessions
    
    def get_recent_conversations(self, days: int = 7, limit: int = 50) -> List[ConversationSession]:
        """Get recent conversations within the last N days."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, topic, start_time, end_time, agent_name, sentiment,
                       quality_score, user_satisfaction, context_summary, metadata
                FROM conversation_metadata 
                WHERE start_time >= ? 
                ORDER BY start_time DESC 
                LIMIT ?
            """, (cutoff_date, limit))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append(ConversationSession(
                    session_id=row[0], topic=row[1], start_time=row[2], end_time=row[3],
                    agent_name=row[4], sentiment=Sentiment(row[5]), quality_score=QualityScore(row[6]),
                    user_satisfaction=row[7], context_summary=row[8],
                    metadata=json.loads(row[9]) if row[9] else {}
                ))
            
            return sessions
    
    def analyze_sentiment(self, text: str) -> Sentiment:
        """Analyze sentiment of text (simplified implementation)."""
        text_lower = text.lower()
        
        # Simple keyword-based sentiment analysis
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "happy", "love", "like", "thanks", "thank you"]
        negative_words = ["bad", "terrible", "awful", "hate", "dislike", "angry", "frustrated", "disappointed"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count * 2:
            return Sentiment.VERY_POSITIVE
        elif positive_count > negative_count:
            return Sentiment.POSITIVE
        elif negative_count > positive_count * 2:
            return Sentiment.VERY_NEGATIVE
        elif negative_count > positive_count:
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL
    
    def learn_user_preferences(self, session_id: str) -> List[UserPreference]:
        """Learn user preferences from a conversation session."""
        session = self.get_conversation_session(session_id)
        messages = self.get_session_messages(session_id)
        
        if not session or not messages:
            return []
        
        preferences = []
        
        # Analyze communication style
        avg_response_length = sum(len(msg.agent_response) for msg in messages) / len(messages)
        if avg_response_length > 500:
            preferences.append(self._create_preference(
                "communication_style", "response_length", "detailed", 0.8
            ))
        elif avg_response_length < 100:
            preferences.append(self._create_preference(
                "communication_style", "response_length", "concise", 0.8
            ))
        
        # Analyze topic interests
        topic_keywords = self._extract_topic_keywords(messages)
        for topic, frequency in topic_keywords.items():
            if frequency > 2:  # Mentioned more than twice
                preferences.append(self._create_preference(
                    "topic_interest", topic, "high", min(frequency / 5.0, 1.0)
                ))
        
        # Analyze interaction patterns
        user_message_count = len([msg for msg in messages if msg.message_type == "user"])
        if user_message_count > 10:
            preferences.append(self._create_preference(
                "interaction_style", "engagement_level", "high", 0.9
            ))
        
        # Save preferences
        for preference in preferences:
            self._save_user_preference(preference)
        
        return preferences
    
    def _create_preference(self, preference_type: str, key: str, value: str, 
                          confidence: float) -> UserPreference:
        """Create a user preference object."""
        return UserPreference(
            id=0,  # Will be set by database
            preference_type=preference_type,
            preference_key=key,
            preference_value=value,
            confidence_score=confidence,
            evidence_count=1,
            last_updated=datetime.now().isoformat(),
            metadata={}
        )
    
    def _extract_topic_keywords(self, messages: List[ConversationMessage]) -> Dict[str, int]:
        """Extract topic keywords from messages."""
        # Simple keyword extraction (in a real implementation, you'd use NLP)
        common_topics = [
            "work", "project", "task", "meeting", "deadline",
            "health", "exercise", "diet", "medical",
            "finance", "money", "budget", "investment",
            "learning", "study", "course", "education",
            "technology", "computer", "software", "programming",
            "family", "friends", "relationship", "social"
        ]
        
        topic_counts = {}
        all_text = " ".join([msg.user_message + " " + msg.agent_response for msg in messages]).lower()
        
        for topic in common_topics:
            count = all_text.count(topic)
            if count > 0:
                topic_counts[topic] = count
        
        return topic_counts
    
    def _save_user_preference(self, preference: UserPreference):
        """Save or update a user preference."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if preference already exists
            cursor.execute("""
                SELECT id, confidence_score, evidence_count 
                FROM user_preferences 
                WHERE preference_type = ? AND preference_key = ?
            """, (preference.preference_type, preference.preference_key))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing preference
                old_id, old_confidence, old_evidence = existing
                new_evidence = old_evidence + 1
                new_confidence = (old_confidence + preference.confidence_score) / 2
                
                cursor.execute("""
                    UPDATE user_preferences 
                    SET preference_value = ?, confidence_score = ?, evidence_count = ?, last_updated = ?
                    WHERE id = ?
                """, (preference.preference_value, new_confidence, new_evidence, 
                     preference.last_updated, old_id))
            else:
                # Insert new preference
                cursor.execute("""
                    INSERT INTO user_preferences 
                    (preference_type, preference_key, preference_value, confidence_score, 
                     evidence_count, last_updated, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    preference.preference_type, preference.preference_key, preference.preference_value,
                    preference.confidence_score, preference.evidence_count, preference.last_updated,
                    json.dumps(preference.metadata)
                ))
            
            conn.commit()
    
    def get_user_preferences(self, preference_type: Optional[str] = None) -> List[UserPreference]:
        """Get user preferences, optionally filtered by type."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if preference_type is not None:
                cursor.execute("""
                    SELECT id, preference_type, preference_key, preference_value, confidence_score,
                           evidence_count, last_updated, metadata
                    FROM user_preferences 
                    WHERE preference_type = ?
                    ORDER BY confidence_score DESC
                """, (str(preference_type),))
            else:
                cursor.execute("""
                    SELECT id, preference_type, preference_key, preference_value, confidence_score,
                           evidence_count, last_updated, metadata
                    FROM user_preferences 
                    ORDER BY confidence_score DESC
                """)
            
            preferences = []
            for row in cursor.fetchall():
                preferences.append(UserPreference(
                    id=row[0], preference_type=row[1], preference_key=row[2],
                    preference_value=row[3], confidence_score=row[4], evidence_count=row[5],
                    last_updated=row[6], metadata=json.loads(row[7]) if row[7] else {}
                ))
            
            return preferences
    
    def export_conversation(self, session_id: str, format: str = "json") -> str:
        """Export a conversation in various formats."""
        session = self.get_conversation_session(session_id)
        messages = self.get_session_messages(session_id)
        
        if not session:
            return ""
        
        def enum_to_value(obj):
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, dict):
                return {k: enum_to_value(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [enum_to_value(i) for i in obj]
            return obj
        
        if format == "json":
            export_data = {
                "session": enum_to_value(asdict(session)),
                "messages": [enum_to_value(asdict(msg)) for msg in messages]
            }
            return json.dumps(export_data, indent=2)
        
        elif format == "text":
            lines = [
                f"Conversation Session: {session.session_id}",
                f"Agent: {session.agent_name}",
                f"Topic: {session.topic}",
                f"Start Time: {session.start_time}",
                f"End Time: {session.end_time or 'Ongoing'}",
                f"Sentiment: {session.sentiment.value}",
                f"Quality Score: {session.quality_score.value}",
                f"User Satisfaction: {session.user_satisfaction or 'Not rated'}",
                "",
                "Messages:",
                "=" * 50
            ]
            
            for msg in messages:
                lines.extend([
                    f"[{msg.timestamp}] {msg.agent_name}:",
                    f"User: {msg.user_message}",
                    f"Agent: {msg.agent_response}",
                    ""
                ])
            
            return "\n".join(lines)
        
        elif format == "markdown":
            lines = [
                f"# Conversation Session: {session.session_id}",
                "",
                f"**Agent:** {session.agent_name}",
                f"**Topic:** {session.topic}",
                f"**Start Time:** {session.start_time}",
                f"**End Time:** {session.end_time or 'Ongoing'}",
                f"**Sentiment:** {session.sentiment.value}",
                f"**Quality Score:** {session.quality_score.value}",
                f"**User Satisfaction:** {session.user_satisfaction or 'Not rated'}",
                "",
                "## Messages",
                ""
            ]
            
            for i, msg in enumerate(messages, 1):
                lines.extend([
                    f"### Message {i}",
                    f"**Time:** {msg.timestamp}",
                    f"**Agent:** {msg.agent_name}",
                    "",
                    "**User:**",
                    f"{msg.user_message}",
                    "",
                    "**Agent Response:**",
                    f"{msg.agent_response}",
                    ""
                ])
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_conversation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive conversation statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total conversations
            cursor.execute("SELECT COUNT(*) FROM conversation_metadata")
            total_conversations = cursor.fetchone()[0]
            
            # Conversations by agent
            cursor.execute("""
                SELECT agent_name, COUNT(*) FROM conversation_metadata 
                GROUP BY agent_name ORDER BY COUNT(*) DESC
            """)
            by_agent = dict(cursor.fetchall())
            
            # Conversations by sentiment
            cursor.execute("""
                SELECT sentiment, COUNT(*) FROM conversation_metadata 
                GROUP BY sentiment ORDER BY COUNT(*) DESC
            """)
            by_sentiment = dict(cursor.fetchall())
            
            # Total messages
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_messages = cursor.fetchone()[0]
            
            # Average messages per conversation
            avg_messages = total_messages / total_conversations if total_conversations > 0 else 0
            
            # Recent activity (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM conversation_metadata 
                WHERE start_time >= ?
            """, (week_ago,))
            recent_conversations = cursor.fetchone()[0]
            
            return {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "avg_messages_per_conversation": avg_messages,
                "conversations_by_agent": by_agent,
                "conversations_by_sentiment": by_sentiment,
                "recent_conversations_7d": recent_conversations
            }
    
    def get_context_for_agent(self, agent_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get relevant conversation context for an agent."""
        # Get recent conversations with this agent
        recent_sessions = self.get_conversations_by_agent(agent_name, limit=limit)
        
        context_data = []
        for session in recent_sessions:
            messages = self.get_session_messages(session.session_id, limit=5)
            
            context_data.append({
                "session_id": session.session_id,
                "topic": session.topic,
                "sentiment": session.sentiment.value,
                "quality_score": session.quality_score.value,
                "user_satisfaction": session.user_satisfaction,
                "recent_messages": [
                    {
                        "user_message": msg.user_message,
                        "agent_response": msg.agent_response,
                        "timestamp": msg.timestamp
                    }
                    for msg in messages[-3:]  # Last 3 messages
                ]
            })
        
        return context_data


# Convenience functions
def create_conversation_manager(db_path: str = "databases/conversations.db") -> ConversationManager:
    """Create and return a conversation manager instance."""
    return ConversationManager(db_path)


if __name__ == "__main__":
    # Test the conversation management system
    cm = create_conversation_manager("test_conversations.db")
    
    # Start a conversation session
    session_id = cm.start_conversation_session("Alpha", "AI System Discussion")
    
    # Add some messages
    cm.add_message(session_id, "Alpha", "Hello, how are you?", "I'm doing well, thank you for asking!")
    cm.add_message(session_id, "Alpha", "Can you help me with a project?", "Of course! I'd be happy to help you with your project.")
    cm.add_message(session_id, "Alpha", "This is great, thanks!", "You're welcome! I'm glad I could help.")
    
    # End the session
    cm.end_conversation_session(session_id, Sentiment.POSITIVE, QualityScore.EXCELLENT, 5)
    
    # Learn preferences
    preferences = cm.learn_user_preferences(session_id)
    print(f"Learned {len(preferences)} user preferences")
    
    # Get statistics
    stats = cm.get_conversation_statistics()
    print(f"Conversation statistics: {stats}")
    
    # Export conversation
    export = cm.export_conversation(session_id, "json")
    print(f"Exported conversation: {len(export)} characters") 