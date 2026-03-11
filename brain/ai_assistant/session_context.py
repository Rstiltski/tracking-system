"""
Session Context Manager for AI Assistant

Manages active session state, sliding window for recent interactions,
and context compression for long conversations.

Based on AI agent research (2024-2025):
- Sliding window for recent interactions
- Context summarization for older interactions
- Session persistence across conversations

Usage:
    from brain.ai_assistant.session_context import SessionContext
    
    context = SessionContext()
    
    # Add interactions to sliding window
    context.add_interaction(role="user", content="Add new feature")
    context.add_interaction(role="assistant", content="Analyzing...")
    
    # Get compressed context for next turn
    compressed = context.get_compressed_context()
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class Interaction:
    """A single interaction in the conversation."""
    id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Interaction':
        return cls(
            id=data['id'],
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']) if isinstance(data['timestamp'], str) else data['timestamp'],
            metadata=data.get('metadata', {})
        )


@dataclass
class SessionState:
    """Current session state."""
    session_id: str
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    total_interactions: int = 0
    active_file: Optional[str] = None
    current_task: Optional[str] = None
    user_intent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SessionContext:
    """
    Manages session context with sliding window and compression.
    
    Features:
    - Sliding window for recent interactions (keeps last N active)
    - Summarization of older interactions
    - Session persistence across conversations
    - Context compression for token efficiency
    """
    
    def __init__(self, session_file: Optional[str] = None,
                 sliding_window_size: int = 10,
                 summary_threshold: int = 50):
        """
        Initialize session context.
        
        Args:
            session_file: Path to session state file
            sliding_window_size: Number of interactions to keep in active memory
            summary_threshold: Interactions beyond this are summarized
        """
        if session_file is None:
            session_file = str(Path(__file__).parent / "session_state.json")
        self.session_file = session_file
        
        self.sliding_window_size = sliding_window_size
        self.summary_threshold = summary_threshold
        
        # Session state
        self.state: Optional[SessionState] = None
        
        # Interaction history
        self.interactions: List[Interaction] = []
        
        # Summarized history (for older interactions)
        self.summaries: List[str] = []
        
        # Load existing session
        self._load_session()
    
    def _load_session(self) -> None:
        """Load session from file."""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load session state
                if 'state' in data:
                    state_data = data['state']
                    self.state = SessionState(
                        session_id=state_data['session_id'],
                        started_at=datetime.fromisoformat(state_data['started_at']),
                        last_activity=datetime.fromisoformat(state_data['last_activity']),
                        total_interactions=state_data.get('total_interactions', 0),
                        active_file=state_data.get('active_file'),
                        current_task=state_data.get('current_task'),
                        user_intent=state_data.get('user_intent'),
                        metadata=state_data.get('metadata', {})
                    )
                
                # Load interactions
                self.interactions = [
                    Interaction.from_dict(i) for i in data.get('interactions', [])
                ]
                
                # Load summaries
                self.summaries = data.get('summaries', [])
                
        except Exception as e:
            print(f"Warning: Could not load session: {e}")
            # Initialize new session
            self._create_new_session()
    
    def _save_session(self) -> None:
        """Save session to file."""
        try:
            data = {
                'state': asdict(self.state) if self.state else {},
                'interactions': [i.to_dict() for i in self.interactions],
                'summaries': self.summaries,
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Warning: Could not save session: {e}")
    
    def _create_new_session(self) -> None:
        """Create a new session."""
        import uuid
        self.state = SessionState(
            session_id=str(uuid.uuid4())[:8]
        )
        self.interactions = []
        self.summaries = []
        self._save_session()
    
    def add_interaction(self, role: str, content: str,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an interaction to the session.
        
        Args:
            role: "user" or "assistant"
            content: Interaction content
            metadata: Optional metadata
            
        Returns:
            Interaction ID
        """
        interaction_id = f"int_{len(self.interactions) + 1:04d}"
        
        interaction = Interaction(
            id=interaction_id,
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        self.interactions.append(interaction)
        
        # Update session state
        if self.state:
            self.state.total_interactions += 1
            self.state.last_activity = datetime.now()
        
        # Apply sliding window if needed
        self._apply_sliding_window()
        
        # Save session
        self._save_session()
        
        return interaction_id
    
    def _apply_sliding_window(self) -> None:
        """Apply sliding window to keep only recent interactions active."""
        if len(self.interactions) <= self.sliding_window_size:
            return
        
        # Move oldest interactions to summary
        interactions_to_summarize = self.interactions[:-self.sliding_window_size]
        
        if interactions_to_summarize:
            # Create summary
            summary = self._create_summary(interactions_to_summarize)
            self.summaries.append(summary)
            
            # Keep only recent interactions
            self.interactions = self.interactions[-self.sliding_window_size:]
    
    def _create_summary(self, interactions: List[Interaction]) -> str:
        """
        Create a summary of interactions.
        
        Args:
            interactions: List of interactions to summarize
            
        Returns:
            Summary string
        """
        if not interactions:
            return ""
        
        # Simple summarization (can be enhanced with LLM)
        user_count = sum(1 for i in interactions if i.role == "user")
        assistant_count = sum(1 for i in interactions if i.role == "assistant")
        
        # Extract key topics from first and last interactions
        first_content = interactions[0].content[:100] if interactions else ""
        last_content = interactions[-1].content[:100] if interactions else ""
        
        summary = (
            f"[{len(interactions)} earlier interactions: "
            f"{user_count} user messages, {assistant_count} assistant responses. "
            f"Started with: {first_content}... "
            f"Ended with: {last_content}...]"
        )
        
        return summary
    
    def get_compressed_context(self) -> str:
        """
        Get compressed context for next turn.
        
        Returns:
            Compressed context string including summaries and recent interactions
        """
        parts = []
        
        # Add summaries of older interactions
        if self.summaries:
            parts.append("## Previous Context")
            for i, summary in enumerate(self.summaries[-5:]):  # Last 5 summaries
                parts.append(f"{summary}")
        
        # Add recent interactions (sliding window)
        if self.interactions:
            parts.append("\n## Recent Interactions")
            for interaction in self.interactions:
                role_label = "User" if interaction.role == "user" else "Assistant"
                parts.append(f"\n### {role_label}:\n{interaction.content[:500]}")  # Truncate long content
        
        # Add session metadata
        if self.state:
            parts.append("\n## Session Info")
            parts.append(f"Session ID: {self.state.session_id}")
            parts.append(f"Current Task: {self.state.current_task or 'None'}")
            parts.append(f"Active File: {self.state.active_file or 'None'}")
        
        return "\n".join(parts)
    
    def get_active_context(self) -> List[Interaction]:
        """
        Get interactions in the active sliding window.
        
        Returns:
            List of recent interactions
        """
        return self.interactions[-self.sliding_window_size:]
    
    def set_active_file(self, file_path: str) -> None:
        """
        Set the currently active file being worked on.
        
        Args:
            file_path: Path to the active file
        """
        if self.state:
            self.state.active_file = file_path
            self._save_session()
    
    def set_current_task(self, task: str) -> None:
        """
        Set the current task being worked on.
        
        Args:
            task: Task description
        """
        if self.state:
            self.state.current_task = task
            self._save_session()
    
    def set_user_intent(self, intent: str) -> None:
        """
        Set the recognized user intent.
        
        Args:
            intent: Recognized intent
        """
        if self.state:
            self.state.user_intent = intent
            self._save_session()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current session.
        
        Returns:
            Session summary dictionary
        """
        if not self.state:
            return {}
        
        return {
            'session_id': self.state.session_id,
            'started_at': self.state.started_at.isoformat(),
            'last_activity': self.state.last_activity.isoformat(),
            'total_interactions': self.state.total_interactions,
            'active_file': self.state.active_file,
            'current_task': self.state.current_task,
            'user_intent': self.state.user_intent,
            'recent_summaries': self.summaries[-3:],
            'active_interactions': len(self.interactions)
        }
    
    def clear_session(self) -> None:
        """Clear the current session and start fresh."""
        self._create_new_session()
    
    def export_session(self, output_file: Optional[str] = None) -> str:
        """
        Export the full session to a file.
        
        Args:
            output_file: Output file path (default: session_export_{timestamp}.json)
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"session_export_{timestamp}.json"
        
        try:
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'session': asdict(self.state) if self.state else {},
                'interactions': [i.to_dict() for i in self.interactions],
                'summaries': self.summaries
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            return output_file
            
        except Exception as e:
            print(f"Error exporting session: {e}")
            return ""
    
    def compress_old_interactions(self, threshold_hours: int = 1) -> int:
        """
        Compress interactions older than a threshold.
        
        Args:
            threshold_hours: Age threshold in hours
            
        Returns:
            Number of interactions compressed
        """
        cutoff = datetime.now() - timedelta(hours=threshold_hours)
        
        # Find old interactions
        old_interactions = [
            i for i in self.interactions
            if i.timestamp < cutoff
        ]
        
        if not old_interactions:
            return 0
        
        # Create summary
        summary = self._create_summary(old_interactions)
        self.summaries.append(summary)
        
        # Remove old interactions
        self.interactions = [
            i for i in self.interactions
            if i.timestamp >= cutoff
        ]
        
        # Save session
        self._save_session()
        
        return len(old_interactions)


# Convenience functions
def get_session_context() -> SessionContext:
    """Get a SessionContext instance."""
    return SessionContext()


def add_interaction(role: str, content: str) -> str:
    """Quick add interaction."""
    context = SessionContext()
    return context.add_interaction(role, content)


def get_context() -> str:
    """Get compressed context."""
    context = SessionContext()
    return context.get_compressed_context()


__all__ = [
    "SessionContext",
    "Interaction",
    "SessionState",
    "get_session_context",
    "add_interaction",
    "get_context",
]
