"""
Habit Difficulty Model - User-rated difficulty tracking.

Based on behavioral science research on habit formation:

1. Difficulty Ratings:
   - Too Easy: Habit scope should be increased
   - Just Right: Optimal challenge level
   - Too Hard: Habit should be made easier (tiny version)

2. Adjustment Tracking:
   - Records when users adjust habit difficulty
   - Tracks adjustment history for analytics
   - Suggests evidence-based modifications

3. Research Basis:
   - BJ Fogg's Tiny Habits: Start small, scale gradually
   - 2-Minute Rule: Habits should take < 2 minutes initially
   - Flow Theory: Optimal challenge between boredom and anxiety

References:
- Fogg, B.J. (2019). "Tiny Habits"
- Csikszentmihalyi, M. (1990). "Flow: The Psychology of Optimal Experience"
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, Any, List
import uuid


class DifficultyRating(str, Enum):
    """
    User-rated difficulty levels for habits.

    Each rating corresponds to a recommended action:
    - TOO_EASY: Increase target by 10-20%
    - JUST_RIGHT: Maintain current scope
    - TOO_HARD: Reduce to "tiny version" (< 2 min)
    """
    TOO_EASY = "too_easy"
    JUST_RIGHT = "just_right"
    TOO_HARD = "too_hard"


class AdjustmentType(str, Enum):
    """
    Types of difficulty adjustments.

    These represent the actions taken in response to
    difficulty ratings.
    """
    INCREASE_TARGET = "increase_target"  # +10-20% target
    DECREASE_TARGET = "decrease_target"  # -50% target (tiny version)
    CHANGE_FREQUENCY = "change_frequency"  # daily → weekly
    ADD_SUPPORT = "add_support"  # Add reminders, environmental cues
    NO_CHANGE = "no_change"  # User chose not to adjust


@dataclass
class DifficultyRatingEntry:
    """
    A single difficulty rating for a habit.

    Attributes:
        id: Unique identifier
        habit_id: ID of the rated habit
        user_id: ID of the user
        rating: The difficulty rating
        notes: Optional user notes about difficulty
        rated_at: Timestamp of rating
        adjustment_made: Whether an adjustment was made
        adjustment_type: Type of adjustment (if any)
        adjustment_details: Details of the adjustment
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    habit_id: str = ""
    user_id: str = ""
    rating: DifficultyRating = DifficultyRating.JUST_RIGHT
    notes: str = ""
    rated_at: datetime = field(default_factory=datetime.now)
    adjustment_made: bool = False
    adjustment_type: Optional[AdjustmentType] = None
    adjustment_details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "user_id": self.user_id,
            "rating": self.rating.value,
            "notes": self.notes,
            "rated_at": self.rated_at.isoformat(),
            "adjustment_made": self.adjustment_made,
            "adjustment_type": self.adjustment_type.value if self.adjustment_type else None,
            "adjustment_details": self.adjustment_details
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DifficultyRatingEntry":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            habit_id=data.get("habit_id", ""),
            user_id=data.get("user_id", ""),
            rating=DifficultyRating(data.get("rating", "just_right")),
            notes=data.get("notes", ""),
            rated_at=datetime.fromisoformat(data["rated_at"]) if "rated_at" in data else datetime.now(),
            adjustment_made=data.get("adjustment_made", False),
            adjustment_type=AdjustmentType(data["adjustment_type"]) if data.get("adjustment_type") else None,
            adjustment_details=data.get("adjustment_details")
        )

    def __str__(self) -> str:
        """String representation."""
        emoji = {
            DifficultyRating.TOO_EASY: "📈",
            DifficultyRating.JUST_RIGHT: "✅",
            DifficultyRating.TOO_HARD: "📉",
        }.get(self.rating, "⚪")
        
        return f"{emoji} Difficulty: {self.rating.value.replace('_', ' ')}"


@dataclass
class DifficultyAdjustment:
    """
    A difficulty adjustment for a habit.

    Records when a habit's scope, target, or frequency
    was modified in response to difficulty feedback.

    Attributes:
        id: Unique identifier
        habit_id: ID of the adjusted habit
        user_id: ID of the user
        adjustment_type: Type of adjustment made
        old_value: Previous value (target, frequency, etc.)
        new_value: New value after adjustment
        reason: User's reason for adjustment
        adjusted_at: Timestamp of adjustment
        effectiveness: User-rated effectiveness (1-5 stars)
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    habit_id: str = ""
    user_id: str = ""
    adjustment_type: AdjustmentType = AdjustmentType.NO_CHANGE
    old_value: Any = None
    new_value: Any = None
    reason: str = ""
    adjusted_at: datetime = field(default_factory=datetime.now)
    effectiveness: Optional[int] = None  # 1-5 stars

    def __post_init__(self):
        """Validate effectiveness rating."""
        if self.effectiveness is not None:
            self.effectiveness = max(1, min(5, self.effectiveness))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "user_id": self.user_id,
            "adjustment_type": self.adjustment_type.value,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "reason": self.reason,
            "adjusted_at": self.adjusted_at.isoformat(),
            "effectiveness": self.effectiveness
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DifficultyAdjustment":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            habit_id=data.get("habit_id", ""),
            user_id=data.get("user_id", ""),
            adjustment_type=AdjustmentType(data.get("adjustment_type", "no_change")),
            old_value=data.get("old_value"),
            new_value=data.get("new_value"),
            reason=data.get("reason", ""),
            adjusted_at=datetime.fromisoformat(data["adjusted_at"]) if "adjusted_at" in data else datetime.now(),
            effectiveness=data.get("effectiveness")
        )

    def __str__(self) -> str:
        """String representation."""
        emoji = {
            AdjustmentType.INCREASE_TARGET: "⬆️",
            AdjustmentType.DECREASE_TARGET: "⬇️",
            AdjustmentType.CHANGE_FREQUENCY: "🔄",
            AdjustmentType.ADD_SUPPORT: "➕",
            AdjustmentType.NO_CHANGE: "⏸️",
        }.get(self.adjustment_type, "⚪")
        
        return f"{emoji} Adjustment: {self.adjustment_type.value.replace('_', ' ')}"


@dataclass
class DifficultySuggestion:
    """
    A suggested difficulty adjustment.

    Generated based on user ratings and performance data.

    Attributes:
        habit_id: ID of the habit
        suggestion_type: Type of suggested adjustment
        title: Short title for the suggestion
        description: Detailed description
        current_value: Current habit parameter
        suggested_value: Suggested new value
        reason: Why this adjustment is suggested
        confidence: Confidence score (0.0-1.0)
    """
    habit_id: str = ""
    suggestion_type: AdjustmentType = AdjustmentType.NO_CHANGE
    title: str = ""
    description: str = ""
    current_value: Any = None
    suggested_value: Any = None
    reason: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "habit_id": self.habit_id,
            "suggestion_type": self.suggestion_type.value,
            "title": self.title,
            "description": self.description,
            "current_value": self.current_value,
            "suggested_value": self.suggested_value,
            "reason": self.reason,
            "confidence": self.confidence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DifficultySuggestion":
        """Create from dictionary."""
        return cls(
            habit_id=data.get("habit_id", ""),
            suggestion_type=AdjustmentType(data.get("suggestion_type", "no_change")),
            title=data.get("title", ""),
            description=data.get("description", ""),
            current_value=data.get("current_value"),
            suggested_value=data.get("suggested_value"),
            reason=data.get("reason", ""),
            confidence=data.get("confidence", 0.0)
        )

    def get_action_text(self) -> str:
        """Get action button text."""
        actions = {
            AdjustmentType.INCREASE_TARGET: "Increase Target",
            AdjustmentType.DECREASE_TARGET: "Make It Tiny",
            AdjustmentType.CHANGE_FREQUENCY: "Reduce Frequency",
            AdjustmentType.ADD_SUPPORT: "Add Support",
            AdjustmentType.NO_CHANGE: "Keep as Is",
        }
        return actions.get(self.suggestion_type, "Review")


# Suggestion templates for common scenarios
SUGGESTION_TEMPLATES = {
    DifficultyRating.TOO_EASY: {
        "title": "Ready for a challenge? 📈",
        "description": "This habit feels too easy. Consider increasing the target.",
        "adjustment_type": AdjustmentType.INCREASE_TARGET,
        "increase_percentage": 0.15,  # 15% increase
    },
    DifficultyRating.TOO_HARD: {
        "title": "Let's make it tiny! 🐜",
        "description": "This habit feels too hard. Scale it down to a 2-minute version.",
        "adjustment_type": AdjustmentType.DECREASE_TARGET,
        "decrease_percentage": 0.50,  # 50% reduction
    },
}


__all__ = [
    "DifficultyRating",
    "AdjustmentType",
    "DifficultyRatingEntry",
    "DifficultyAdjustment",
    "DifficultySuggestion",
    "SUGGESTION_TEMPLATES",
]
