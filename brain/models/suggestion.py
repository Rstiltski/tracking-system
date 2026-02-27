"""
Suggestion Model - Smart habit suggestions.

Based on user patterns and behavioral science:

1. Suggestion Types:
   - Pattern-based: Based on user behavior patterns
   - Predictive: Anticipating future needs
   - Gap-based: Identifying missing elements
   - Optimization: Improving existing habits

2. Priority Levels:
   - High: Immediate action needed
   - Medium: Should consider soon
   - Low: Nice to have

References:
- Persuasive technology research
- Behavior change intervention design
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


class SuggestionType(str, Enum):
    """Types of suggestions."""
    PATTERN = "pattern"  # Based on user patterns
    PREDICTIVE = "predictive"  # Anticipating needs
    GAP = "gap"  # Missing elements
    OPTIMIZATION = "optimization"  # Improvements
    ENCOURAGEMENT = "encouragement"  # Positive reinforcement


class SuggestionPriority(str, Enum):
    """Priority levels for suggestions."""
    HIGH = "high"  # Immediate action
    MEDIUM = "medium"  # Consider soon
    LOW = "low"  # Nice to have


@dataclass
class Suggestion:
    """
    A smart suggestion for habit improvement.

    Attributes:
        id: Unique identifier
        habit_id: Associated habit ID (optional)
        user_id: User ID
        suggestion_type: Type of suggestion
        priority: Priority level
        title: Short title
        description: Detailed description
        action: Suggested action
        metadata: Additional data
        created_at: When created
        dismissed: Whether dismissed by user
        acted_upon: Whether user acted on it
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    habit_id: Optional[str] = None
    user_id: str = ""
    suggestion_type: SuggestionType = SuggestionType.PATTERN
    priority: SuggestionPriority = SuggestionPriority.MEDIUM
    title: str = ""
    description: str = ""
    action: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    dismissed: bool = False
    acted_upon: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "user_id": self.user_id,
            "suggestion_type": self.suggestion_type.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "action": self.action,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "dismissed": self.dismissed,
            "acted_upon": self.acted_upon
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Suggestion":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            habit_id=data.get("habit_id"),
            user_id=data.get("user_id", ""),
            suggestion_type=SuggestionType(data.get("suggestion_type", "pattern")),
            priority=SuggestionPriority(data.get("priority", "medium")),
            title=data.get("title", ""),
            description=data.get("description", ""),
            action=data.get("action", ""),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            dismissed=data.get("dismissed", False),
            acted_upon=data.get("acted_upon", False)
        )

    def get_type_emoji(self) -> str:
        """Get emoji for suggestion type."""
        emojis = {
            SuggestionType.PATTERN: "📊",
            SuggestionType.PREDICTIVE: "🔮",
            SuggestionType.GAP: "🧩",
            SuggestionType.OPTIMIZATION: "⚡",
            SuggestionType.ENCOURAGEMENT: "🌟",
        }
        return emojis.get(self.suggestion_type, "💡")

    def get_priority_color(self) -> str:
        """Get color for priority level."""
        colors = {
            SuggestionPriority.HIGH: "#F44336",
            SuggestionPriority.MEDIUM: "#FF9800",
            SuggestionPriority.LOW: "#4CAF50",
        }
        return colors.get(self.priority, "#808080")


@dataclass
class SuggestionFeedback:
    """
    User feedback on a suggestion.

    Attributes:
        id: Unique identifier
        suggestion_id: Suggestion ID
        user_id: User ID
        helpful: Whether suggestion was helpful
        notes: Optional feedback notes
        created_at: When feedback was given
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    suggestion_id: str = ""
    user_id: str = ""
    helpful: bool = False
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "suggestion_id": self.suggestion_id,
            "user_id": self.user_id,
            "helpful": self.helpful,
            "notes": self.notes,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuggestionFeedback":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            suggestion_id=data.get("suggestion_id", ""),
            user_id=data.get("user_id", ""),
            helpful=data.get("helpful", False),
            notes=data.get("notes", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        )


# Suggestion templates for common patterns
SUGGESTION_TEMPLATES = {
    "declining_streak": {
        "type": SuggestionType.PATTERN,
        "priority": SuggestionPriority.HIGH,
        "title": "Streak Declining",
        "description": "Your streak on {habit_name} is at risk",
        "action": "Consider using a streak freeze or reducing difficulty"
    },
    "perfect_week": {
        "type": SuggestionType.ENCOURAGEMENT,
        "priority": SuggestionPriority.LOW,
        "title": "Perfect Week!",
        "description": "You completed {habit_name} every day this week",
        "action": "Keep up the great work!"
    },
    "low_completion": {
        "type": SuggestionType.GAP,
        "priority": SuggestionPriority.MEDIUM,
        "title": "Low Completion Rate",
        "description": "{habit_name} completion rate is below 50%",
        "action": "Try making the habit easier or changing the time"
    },
    "ready_for_challenge": {
        "type": SuggestionType.OPTIMIZATION,
        "priority": SuggestionPriority.MEDIUM,
        "title": "Ready for More?",
        "description": "You've mastered {habit_name} with 90%+ completion",
        "action": "Consider increasing the challenge"
    },
}


__all__ = [
    "SuggestionType",
    "SuggestionPriority",
    "Suggestion",
    "SuggestionFeedback",
    "SUGGESTION_TEMPLATES",
]
