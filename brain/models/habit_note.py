"""
Habit Notes Model - Journaling and reflections for habits.

Based on research showing that reflection enhances habit formation:

1. Note Types:
   - Daily reflections (after completion)
   - Milestone notes (achievements)
   - Insight notes (patterns noticed)
   - Struggle notes (challenges)

2. Benefits:
   - Increases self-awareness
   - Helps identify patterns
   - Provides motivation through progress
   - Creates accountability

3. Research Basis:
   - Reflection enhances learning
   - Writing reinforces commitment
   - Pattern recognition improves strategy

References:
- Diaries and self-monitoring in behavior change
- Reflection practices in habit formation
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, Any, List
import uuid


class NoteType(str, Enum):
    """Types of habit notes."""
    DAILY = "daily"  # Daily reflection
    MILESTONE = "milestone"  # Achievement/milestone
    INSIGHT = "insight"  # Pattern or insight
    STRUGGLE = "struggle"  # Challenge or difficulty
    CUSTOM = "custom"  # Custom note


@dataclass
class HabitNote:
    """
    A note/reflection for a habit.

    Attributes:
        id: Unique identifier
        habit_id: ID of the habit
        user_id: ID of the user
        note_type: Type of note
        content: Note content
        mood: Optional mood rating (1-5)
        energy: Optional energy level (1-5)
        tags: Optional tags
        created_at: When note was created
        entry_date: Date the note refers to
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    habit_id: str = ""
    user_id: str = ""
    note_type: NoteType = NoteType.DAILY
    content: str = ""
    mood: Optional[int] = None  # 1-5
    energy: Optional[int] = None  # 1-5
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    entry_date: date = field(default_factory=date.today)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "user_id": self.user_id,
            "note_type": self.note_type.value,
            "content": self.content,
            "mood": self.mood,
            "energy": self.energy,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "entry_date": self.entry_date.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HabitNote":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            habit_id=data.get("habit_id", ""),
            user_id=data.get("user_id", ""),
            note_type=NoteType(data.get("note_type", "daily")),
            content=data.get("content", ""),
            mood=data.get("mood"),
            energy=data.get("energy"),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            entry_date=date.fromisoformat(data["entry_date"]) if data.get("entry_date") else date.today()
        )

    def get_mood_emoji(self) -> str:
        """Get emoji for mood rating."""
        if not self.mood:
            return "😐"
        emojis = {
            1: "😞",
            2: "😕",
            3: "😐",
            4: "🙂",
            5: "😄",
        }
        return emojis.get(self.mood, "😐")

    def get_energy_emoji(self) -> str:
        """Get emoji for energy rating."""
        if not self.energy:
            return "😐"
        emojis = {
            1: "😫",
            2: "😓",
            3: "😐",
            4: "😊",
            5: "⚡",
        }
        return emojis.get(self.energy, "😐")

    def __str__(self) -> str:
        """String representation."""
        type_emoji = {
            NoteType.DAILY: "📝",
            NoteType.MILESTONE: "🎉",
            NoteType.INSIGHT: "💡",
            NoteType.STRUGGLE: "😤",
            NoteType.CUSTOM: "📋",
        }.get(self.note_type, "📝")

        mood_str = f" {self.get_mood_emoji()}" if self.mood else ""
        energy_str = f" {self.get_energy_emoji()}" if self.energy else ""

        return f"{type_emoji} {self.entry_date}: {self.content[:50]}...{mood_str}{energy_str}"


@dataclass
class NoteStats:
    """
    Statistics about habit notes.

    Attributes:
        total_notes: Total number of notes
        notes_by_type: Count by note type
        average_mood: Average mood rating
        average_energy: Average energy level
        most_used_tags: Most frequently used tags
        notes_this_week: Notes created this week
    """
    total_notes: int = 0
    notes_by_type: Dict[str, int] = field(default_factory=dict)
    average_mood: float = 0.0
    average_energy: float = 0.0
    most_used_tags: List[str] = field(default_factory=list)
    notes_this_week: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_notes": self.total_notes,
            "notes_by_type": self.notes_by_type,
            "average_mood": round(self.average_mood, 2),
            "average_energy": round(self.average_energy, 2),
            "most_used_tags": self.most_used_tags,
            "notes_this_week": self.notes_this_week
        }


# Note prompts for different types
NOTE_PROMPTS = {
    NoteType.DAILY: [
        "How did it go today?",
        "What worked well?",
        "What could be improved?",
        "How do you feel after completing this?",
    ],
    NoteType.INSIGHT: [
        "What pattern did you notice?",
        "What did you learn about yourself?",
        "What strategy is working?",
    ],
    NoteType.STRUGGLE: [
        "What made it difficult today?",
        "What support do you need?",
        "How can you make this easier?",
    ],
    NoteType.MILESTONE: [
        "What achievement are you celebrating?",
        "How far have you come?",
        "What made this possible?",
    ],
}


def get_note_prompt(note_type: NoteType) -> str:
    """
    Get a random prompt for a note type.

    Args:
        note_type: Type of note

    Returns:
        Prompt string
    """
    import random
    prompts = NOTE_PROMPTS.get(note_type, NOTE_PROMPTS[NoteType.DAILY])
    return random.choice(prompts)


__all__ = [
    "NoteType",
    "HabitNote",
    "NoteStats",
    "get_note_prompt",
    "NOTE_PROMPTS",
]
