"""
Brain AI Chat Session - Session Management

Provides chat session management for the AI Assistant.
Handles message storage, context windowing, and session persistence.

Usage:
    from brain.ai.chat_session import ChatSession, MessageRole
    
    session = ChatSession(session_id="my-session")
    session.add_message(MessageRole.USER, "Hello!")
    session.add_message(MessageRole.ASSISTANT, "Hi there!")
    
    messages = session.get_messages_for_llm()
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import json
import sqlite3
from pathlib import Path


class MessageRole(Enum):
    """Role of a chat message."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    """
    Single message in a chat session.
    
    Attributes:
        role: Who sent the message (user, assistant, system)
        content: The message text
        created_at: Timestamp of creation
        tokens: Approximate token count (optional)
        metadata: Additional metadata (sources, etc.)
    """
    role: MessageRole
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "role": self.role.value,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "tokens": self.tokens,
            "metadata": self.metadata
        }
    
    def to_llm_format(self) -> Dict[str, str]:
        """Format for LLM API (simplified)."""
        return {"role": self.role.value, "content": self.content}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """Create from dictionary."""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"]),
            tokens=data.get("tokens", 0),
            metadata=data.get("metadata", {})
        )


@dataclass
class ChatSession:
    """
    Chat session with message history.
    
    Manages conversation history with:
    - Message storage and retrieval
    - Context window limiting
    - Token counting
    - Serialization for persistence
    
    Attributes:
        session_id: Unique identifier for the session
        messages: List of chat messages
        created_at: Session creation time
        updated_at: Last update time
        metadata: Session metadata (title, tags, etc.)
    """
    session_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(
        self, 
        role: MessageRole, 
        content: str, 
        tokens: int = 0,
        **metadata
    ) -> ChatMessage:
        """
        Add a message to the session.
        
        Args:
            role: Who sent the message
            content: The message text
            tokens: Approximate token count
            **metadata: Additional metadata
            
        Returns:
            The created ChatMessage
        """
        message = ChatMessage(
            role=role,
            content=content,
            tokens=tokens,
            metadata=metadata
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def add_user_message(self, content: str, **metadata) -> ChatMessage:
        """Add a user message."""
        return self.add_message(MessageRole.USER, content, **metadata)
    
    def add_assistant_message(self, content: str, **metadata) -> ChatMessage:
        """Add an assistant message."""
        return self.add_message(MessageRole.ASSISTANT, content, **metadata)
    
    def add_system_message(self, content: str, **metadata) -> ChatMessage:
        """Add a system message."""
        return self.add_message(MessageRole.SYSTEM, content, **metadata)
    
    def get_messages_for_llm(self, max_messages: int = 20) -> List[Dict[str, str]]:
        """
        Get messages formatted for LLM API.
        
        Args:
            max_messages: Maximum number of recent messages
            
        Returns:
            List of message dictionaries
        """
        messages = self.messages[-max_messages:] if max_messages else self.messages
        return [msg.to_llm_format() for msg in messages]
    
    def get_context_window(self, max_messages: int = 20) -> List[ChatMessage]:
        """
        Get recent messages within context window.
        
        Args:
            max_messages: Maximum number of messages
            
        Returns:
            List of recent ChatMessage objects
        """
        return self.messages[-max_messages:] if max_messages else self.messages
    
    def get_token_count(self) -> int:
        """
        Get total token count for the session.
        
        Returns:
            Sum of tokens across all messages
        """
        return sum(msg.tokens for msg in self.messages)
    
    def clear_messages(self) -> None:
        """Clear all messages from the session."""
        self.messages = []
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatSession":
        """Create from dictionary."""
        return cls(
            session_id=data["session_id"],
            messages=[ChatMessage.from_dict(msg) for msg in data["messages"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {})
        )


class ChatSessionManager:
    """
    Manages multiple chat sessions with SQLite persistence.
    
    Features:
    - Create, load, and delete sessions
    - Persist sessions to SQLite
    - List recent sessions
    
    Usage:
        manager = ChatSessionManager()
        session = manager.create_session()
        manager.save_session(session)
        loaded = manager.load_session(session.session_id)
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the session manager.
        
        Args:
            db_path: Path to SQLite database. Uses default if None.
        """
        if db_path is None:
            # Use project's data directory
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "chat_sessions.db")
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                metadata JSON
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP,
                tokens INTEGER,
                metadata JSON,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_id: Optional[str] = None, **metadata) -> ChatSession:
        """
        Create a new chat session.
        
        Args:
            session_id: Optional custom session ID
            **metadata: Session metadata
            
        Returns:
            New ChatSession instance
        """
        import uuid
        session = ChatSession(
            session_id=session_id or str(uuid.uuid4()),
            metadata=metadata
        )
        return session
    
    def save_session(self, session: ChatSession) -> bool:
        """
        Save a session to the database.
        
        Args:
            session: ChatSession to save
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or update session
            cursor.execute("""
                INSERT OR REPLACE INTO chat_sessions 
                (session_id, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?)
            """, (
                session.session_id,
                session.created_at.isoformat(),
                session.updated_at.isoformat(),
                json.dumps(session.metadata)
            ))
            
            # Delete existing messages for this session
            cursor.execute(
                "DELETE FROM chat_messages WHERE session_id = ?",
                (session.session_id,)
            )
            
            # Insert messages
            for msg in session.messages:
                cursor.execute("""
                    INSERT INTO chat_messages 
                    (session_id, role, content, created_at, tokens, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    msg.role.value,
                    msg.content,
                    msg.created_at.isoformat(),
                    msg.tokens,
                    json.dumps(msg.metadata)
                ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Load a session from the database.
        
        Args:
            session_id: Session ID to load
            
        Returns:
            ChatSession if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load session
            cursor.execute(
                "SELECT created_at, updated_at, metadata FROM chat_sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                conn.close()
                return None
            
            created_at, updated_at, metadata = row
            session = ChatSession(
                session_id=session_id,
                created_at=datetime.fromisoformat(created_at),
                updated_at=datetime.fromisoformat(updated_at),
                metadata=json.loads(metadata) if metadata else {}
            )
            
            # Load messages
            cursor.execute("""
                SELECT role, content, created_at, tokens, metadata 
                FROM chat_messages 
                WHERE session_id = ?
                ORDER BY created_at ASC
            """, (session_id,))
            
            for row in cursor.fetchall():
                role, content, msg_created_at, tokens, msg_metadata = row
                session.messages.append(ChatMessage(
                    role=MessageRole(role),
                    content=content,
                    created_at=datetime.fromisoformat(msg_created_at),
                    tokens=tokens or 0,
                    metadata=json.loads(msg_metadata) if msg_metadata else {}
                ))
            
            conn.close()
            return session
            
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from the database.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List recent sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session summaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, created_at, updated_at, metadata
                FROM chat_sessions
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,))
            
            sessions = []
            for row in cursor.fetchall():
                session_id, created_at, updated_at, metadata = row
                sessions.append({
                    "session_id": session_id,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "metadata": json.loads(metadata) if metadata else {}
                })
            
            conn.close()
            return sessions
            
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []


# Convenience functions
def create_session(session_id: Optional[str] = None) -> ChatSession:
    """Create a new chat session."""
    import uuid
    return ChatSession(session_id=session_id or str(uuid.uuid4()))