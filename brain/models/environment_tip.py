"""
Environment Tip Model - Environmental design suggestions for habit success.

Based on Atomic Habits research by James Clear:

1. Cue Design:
   - Make cues obvious and visible
   - Environment shapes behavior more than motivation
   - Implementation intentions work better with environmental cues

2. Friction Reduction:
   - Reduce friction for good habits
   - Increase friction for bad habits
   - 20-second rule: Make habits easy to start

3. Implementation Intentions:
   - Specific time and location
   - "When situation X arises, I will perform response Y"
   - Environment-based triggers

References:
- Clear, J. (2018). "Atomic Habits"
- Gollwitzer, P.M. (1999). "Implementation intentions"
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


class TipCategory(str, Enum):
    """Categories for environment tips."""
    CUE_DESIGN = "cue_design"  # Make cues obvious
    FRICTION_REDUCTION = "friction_reduction"  # Reduce barriers
    IMPLEMENTATION = "implementation"  # When/where planning
    SOCIAL = "social"  # Social environment
    PHYSICAL = "physical"  # Physical space design
    DIGITAL = "digital"  # Digital environment


class HabitType(str, Enum):
    """Habit types for tip matching."""
    EXERCISE = "exercise"
    MEDITATION = "meditation"
    READING = "reading"
    WRITING = "writing"
    SLEEP = "sleep"
    NUTRITION = "nutrition"
    PRODUCTIVITY = "productivity"
    LEARNING = "learning"
    HYGIENE = "hygiene"
    GENERAL = "general"


@dataclass
class EnvironmentTip:
    """
    An environmental design tip.

    Attributes:
        id: Unique identifier
        category: Tip category
        habit_type: Applicable habit type
        title: Short title
        description: Detailed description
        example: Concrete example
        difficulty: Implementation difficulty
        effectiveness: Research-backed effectiveness rating
        tags: Search tags
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    category: TipCategory = TipCategory.CUE_DESIGN
    habit_type: HabitType = HabitType.GENERAL
    title: str = ""
    description: str = ""
    example: str = ""
    difficulty: str = "easy"  # easy, medium, hard
    effectiveness: float = 0.0  # 1-5 scale
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "category": self.category.value,
            "habit_type": self.habit_type.value,
            "title": self.title,
            "description": self.description,
            "example": self.example,
            "difficulty": self.difficulty,
            "effectiveness": self.effectiveness,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnvironmentTip":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            category=TipCategory(data.get("category", "cue_design")),
            habit_type=HabitType(data.get("habit_type", "general")),
            title=data.get("title", ""),
            description=data.get("description", ""),
            example=data.get("example", ""),
            difficulty=data.get("difficulty", "easy"),
            effectiveness=data.get("effectiveness", 0.0),
            tags=data.get("tags", [])
        )

    def get_difficulty_emoji(self) -> str:
        """Get emoji for difficulty level."""
        emojis = {
            "easy": "🟢",
            "medium": "🟡",
            "hard": "🔴",
        }
        return emojis.get(self.difficulty, "⚪")

    def get_effectiveness_stars(self) -> str:
        """Get star rating for effectiveness."""
        stars = round(self.effectiveness)
        return "⭐" * stars


@dataclass
class UserTipInteraction:
    """
    Record of user interaction with a tip.

    Attributes:
        id: Unique identifier
        tip_id: Tip ID
        user_id: User ID
        habit_id: Habit ID
        action: User action (viewed, tried, helpful, not_helpful)
        notes: User notes
        created_at: Interaction timestamp
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tip_id: str = ""
    user_id: str = ""
    habit_id: str = ""
    action: str = "viewed"
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "tip_id": self.tip_id,
            "user_id": self.user_id,
            "habit_id": self.habit_id,
            "action": self.action,
            "notes": self.notes,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserTipInteraction":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            tip_id=data.get("tip_id", ""),
            user_id=data.get("user_id", ""),
            habit_id=data.get("habit_id", ""),
            action=data.get("action", "viewed"),
            notes=data.get("notes", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        )


# Pre-defined environment tips library
DEFAULT_TIPS: List[EnvironmentTip] = [
    # Cue Design Tips
    EnvironmentTip(
        id="tip_cue_1",
        category=TipCategory.CUE_DESIGN,
        habit_type=HabitType.EXERCISE,
        title="Place Workout Clothes Visible",
        description="Lay out your workout clothes the night before in a visible location.",
        example="Place gym clothes next to your bed or by the bedroom door.",
        difficulty="easy",
        effectiveness=4.5,
        tags=["exercise", "morning", "clothes", "visible"]
    ),
    EnvironmentTip(
        id="tip_cue_2",
        category=TipCategory.CUE_DESIGN,
        habit_type=HabitType.READING,
        title="Book on Pillow",
        description="Place your book on your pillow during the day.",
        example="Put your reading book on your bed pillow so you see it at bedtime.",
        difficulty="easy",
        effectiveness=4.2,
        tags=["reading", "bedtime", "book", "visible"]
    ),
    EnvironmentTip(
        id="tip_cue_3",
        category=TipCategory.CUE_DESIGN,
        habit_type=HabitType.NUTRITION,
        title="Pre-cut Vegetables",
        description="Pre-cut vegetables and store them at eye level in the fridge.",
        example="Spend Sunday cutting carrots, celery, and peppers. Store in clear containers at eye level.",
        difficulty="medium",
        effectiveness=4.7,
        tags=["nutrition", "vegetables", "prep", "visible"]
    ),

    # Friction Reduction Tips
    EnvironmentTip(
        id="tip_friction_1",
        category=TipCategory.FRICTION_REDUCTION,
        habit_type=HabitType.MEDITATION,
        title="Create Dedicated Space",
        description="Set up a dedicated meditation corner with cushion ready.",
        example="Keep a meditation cushion in a quiet corner, always ready to use.",
        difficulty="easy",
        effectiveness=4.3,
        tags=["meditation", "space", "cushion", "ready"]
    ),
    EnvironmentTip(
        id="tip_friction_2",
        category=TipCategory.FRICTION_REDUCTION,
        habit_type=HabitType.EXERCISE,
        title="Keep Equipment Accessible",
        description="Keep exercise equipment in plain sight and easily accessible.",
        example="Keep yoga mat unrolled or dumbbells next to the TV.",
        difficulty="easy",
        effectiveness=4.4,
        tags=["exercise", "equipment", "accessible", "visible"]
    ),
    EnvironmentTip(
        id="tip_friction_3",
        category=TipCategory.FRICTION_REDUCTION,
        habit_type=HabitType.WRITING,
        title="Open Document Ready",
        description="Keep your writing document open on your computer.",
        example="Leave your writing app open with cursor positioned where you left off.",
        difficulty="easy",
        effectiveness=4.0,
        tags=["writing", "computer", "document", "ready"]
    ),

    # Implementation Tips
    EnvironmentTip(
        id="tip_impl_1",
        category=TipCategory.IMPLEMENTATION,
        habit_type=HabitType.GENERAL,
        title="Specific Time & Location",
        description="Assign a specific time and location for your habit.",
        example="I will meditate at 7:00 AM in my bedroom corner.",
        difficulty="easy",
        effectiveness=4.8,
        tags=["implementation", "time", "location", "specific"]
    ),
    EnvironmentTip(
        id="tip_impl_2",
        category=TipCategory.IMPLEMENTATION,
        habit_type=HabitType.PRODUCTIVITY,
        title="After-Then Planning",
        description="Use 'After I [current habit], then I will [new habit]' format.",
        example="After I pour my morning coffee, then I will plan my top 3 tasks.",
        difficulty="easy",
        effectiveness=4.6,
        tags=["implementation", "planning", "after-then", "stacking"]
    ),

    # Social Tips
    EnvironmentTip(
        id="tip_social_1",
        category=TipCategory.SOCIAL,
        habit_type=HabitType.EXERCISE,
        title="Workout Buddy",
        description="Find a workout partner for accountability.",
        example="Schedule regular workout sessions with a friend.",
        difficulty="medium",
        effectiveness=4.5,
        tags=["social", "accountability", "partner", "exercise"]
    ),

    # Physical Space Tips
    EnvironmentTip(
        id="tip_physical_1",
        category=TipCategory.PHYSICAL,
        habit_type=HabitType.SLEEP,
        title="Phone Outside Bedroom",
        description="Charge your phone outside the bedroom to improve sleep hygiene.",
        example="Use a traditional alarm clock and charge phone in kitchen.",
        difficulty="medium",
        effectiveness=4.7,
        tags=["sleep", "phone", "bedroom", "hygiene"]
    ),

    # Digital Environment Tips
    EnvironmentTip(
        id="tip_digital_1",
        category=TipCategory.DIGITAL,
        habit_type=HabitType.PRODUCTIVITY,
        title="Website Blockers",
        description="Use website blockers during focus time.",
        example="Install Freedom or Cold Turkey to block distracting websites.",
        difficulty="easy",
        effectiveness=4.2,
        tags=["digital", "blocker", "focus", "productivity"]
    ),
]


def get_tips_by_category(
    category: TipCategory,
    tips: Optional[List[EnvironmentTip]] = None
) -> List[EnvironmentTip]:
    """
    Get tips by category.

    Args:
        category: Category to filter by
        tips: Optional list to search

    Returns:
        List of matching tips
    """
    if tips is None:
        tips = DEFAULT_TIPS

    return [t for t in tips if t.category == category]


def get_tips_by_habit_type(
    habit_type: HabitType,
    tips: Optional[List[EnvironmentTip]] = None
) -> List[EnvironmentTip]:
    """
    Get tips by habit type.

    Args:
        habit_type: Habit type to filter by
        tips: Optional list to search

    Returns:
        List of matching tips
    """
    if tips is None:
        tips = DEFAULT_TIPS

    # Return tips for specific habit type OR general tips
    return [
        t for t in tips
        if t.habit_type == habit_type or t.habit_type == HabitType.GENERAL
    ]


def search_tips(
    query: str,
    tips: Optional[List[EnvironmentTip]] = None
) -> List[EnvironmentTip]:
    """
    Search tips by text.

    Args:
        query: Search query
        tips: Optional list to search

    Returns:
        List of matching tips
    """
    if tips is None:
        tips = DEFAULT_TIPS

    query_lower = query.lower()
    results = []

    for tip in tips:
        # Search in title
        if query_lower in tip.title.lower():
            results.append(tip)
            continue

        # Search in description
        if query_lower in tip.description.lower():
            results.append(tip)
            continue

        # Search in tags
        if any(query_lower in tag.lower() for tag in tip.tags):
            results.append(tip)
            continue

    return results


__all__ = [
    "TipCategory",
    "HabitType",
    "EnvironmentTip",
    "UserTipInteraction",
    "DEFAULT_TIPS",
    "get_tips_by_category",
    "get_tips_by_habit_type",
    "search_tips",
]
