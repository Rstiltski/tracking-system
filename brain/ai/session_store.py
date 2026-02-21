"""
Session Store Module

SQLite-based persistence for chat sessions.
Enables saving, loading, and managing AI chat sessions.
"""

import sqlite3
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class ChatMessage:
    """Represents a single chat message."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """Create from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class ChatSession:
    """Represents a chat session."""
    id: str
    title: str
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    provider: str = "ollama"
    model: str = "llama3"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """Add a message to the session."""
        message = ChatMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "provider": self.provider,
            "model": self.model,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatSession":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            messages=[ChatMessage.from_dict(m) for m in data.get("messages", [])],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            provider=data.get("provider", "ollama"),
            model=data.get("model", "llama3"),
            metadata=data.get("metadata", {})
        )


class SessionStore:
    """SQLite-based session storage."""
    
    def __init__(self, db_path: str = "sessions.db"):
        """
        Initialize session store.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                messages TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                provider TEXT DEFAULT 'ollama',
                model TEXT DEFAULT 'llama3',
                metadata TEXT DEFAULT '{}'
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_sessions_updated 
            ON sessions(updated_at DESC)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_session(self, session: ChatSession) -> bool:
        """
        Save a chat session.
        
        Args:
            session: The session to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sessions 
                (id, title, messages, created_at, updated_at, provider, model, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.id,
                session.title,
                json.dumps([m.to_dict() for m in session.messages]),
                session.created_at.isoformat(),
                session.updated_at.isoformat(),
                session.provider,
                session.model,
                json.dumps(session.metadata)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Load a chat session by ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            The session if found, None otherwise
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, messages, created_at, updated_at, provider, model, metadata
                FROM sessions WHERE id = ?
            ''', (session_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return ChatSession(
                    id=row[0],
                    title=row[1],
                    messages=[ChatMessage.from_dict(m) for m in json.loads(row[2])],
                    created_at=datetime.fromisoformat(row[3]),
                    updated_at=datetime.fromisoformat(row[4]),
                    provider=row[5],
                    model=row[6],
                    metadata=json.loads(row[7])
                )
            return None
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def list_sessions(self, limit: int = 50, offset: int = 0) -> List[ChatSession]:
        """
        List all sessions, ordered by most recent.
        
        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            
        Returns:
            List of sessions (without full message content)
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, messages, created_at, updated_at, provider, model, metadata
                FROM sessions
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            conn.close()
            
            sessions = []
            for row in rows:
                messages = json.loads(row[2])
                # Only include message count, not full content for list view
                session = ChatSession(
                    id=row[0],
                    title=row[1],
                    messages=[],  # Empty for list view
                    created_at=datetime.fromisoformat(row[3]),
                    updated_at=datetime.fromisoformat(row[4]),
                    provider=row[5],
                    model=row[6],
                    metadata={**json.loads(row[7]), "message_count": len(messages)}
                )
                sessions.append(session)
            
            return sessions
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: The session ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return deleted
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def search_sessions(self, query: str, limit: int = 20) -> List[ChatSession]:
        """
        Search sessions by title or content.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching sessions
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, messages, created_at, updated_at, provider, model, metadata
                FROM sessions
                WHERE title LIKE ? OR messages LIKE ?
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            sessions = []
            for row in rows:
                session = ChatSession(
                    id=row[0],
                    title=row[1],
                    messages=[ChatMessage.from_dict(m) for m in json.loads(row[2])],
                    created_at=datetime.fromisoformat(row[3]),
                    updated_at=datetime.fromisoformat(row[4]),
                    provider=row[5],
                    model=row[6],
                    metadata=json.loads(row[7])
                )
                sessions.append(session)
            
            return sessions
        except Exception as e:
            print(f"Error searching sessions: {e}")
            return []
    
    def get_session_count(self) -> int:
        """Get total number of sessions."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM sessions')
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
        except Exception as e:
            print(f"Error getting session count: {e}")
            return 0
    
    def clear_old_sessions(self, days: int = 30) -> int:
        """
        Delete sessions older than specified days.
        
        Args:
            days: Number of days threshold
            
        Returns:
            Number of sessions deleted
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM sessions 
                WHERE updated_at < datetime('now', ?)
            ''', (f'-{days} days',))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted
        except Exception as e:
            print(f"Error clearing old sessions: {e}")
            return 0


# Convenience functions
_store_instance: Optional[SessionStore] = None


def get_session_store(db_path: str = "sessions.db") -> SessionStore:
    """Get or create the session store singleton."""
    global _store_instance
    if _store_instance is None:
        _store_instance = SessionStore(db_path)
    return _store_instance


def create_session(title: str, provider: str = "ollama", model: str = "llama3") -> ChatSession:
    """Create a new chat session."""
    import uuid
    return ChatSession(
        id=str(uuid.uuid4()),
        title=title,
        provider=provider,
        model=model
    )