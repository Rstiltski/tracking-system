"""
Habit Template Model - Pre-built habit collections.

Based on research showing that templates reduce friction for habit formation:

1. Template Categories:
   - Morning routines
   - Evening wind-down
   - Productivity boost
   - Health & fitness
   - Mental wellness
   - Learning & growth

2. Benefits:
   - Reduces decision fatigue
   - Provides proven combinations
   - Faster habit stack creation
   - Lower barrier to entry

3. Research Basis:
   - Implementation intentions work better with specific plans
   - Social proof increases adoption
   - Curated collections reduce overwhelm

References:
- Clear, J. (2018). "Atomic Habits" - Habit stacking
- Fogg, B.J. (2019). "Tiny Habits" - Recipe collections
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid


class TemplateCategory(str, Enum):
    """Categories for habit templates."""
    MORNING = "morning"  # Morning routines
    EVENING = "evening"  # Evening wind-down
    PRODUCTIVITY = "productivity"  # Work/productivity
    HEALTH = "health"  # Physical health
    FITNESS = "fitness"  # Exercise/fitness
    MENTAL = "mental"  # Mental wellness
    LEARNING = "learning"  # Learning/growth
    NUTRITION = "nutrition"  # Diet/nutrition
    SOCIAL = "social"  # Relationships
    CUSTOM = "custom"  # User-created


class TemplateDifficulty(str, Enum):
    """Difficulty levels for templates."""
    BEGINNER = "beginner"  # 1-3 habits, < 10 min
    INTERMEDIATE = "intermediate"  # 3-5 habits, < 20 min
    ADVANCED = "advanced"  # 5+ habits, < 30 min


@dataclass
class TemplateHabit:
    """
    A single habit within a template.

    Attributes:
        name: Habit name
        description: Brief description
        icon: Emoji icon
        color: Color hex code
        frequency: How often (daily/weekly)
        habit_type: boolean or numerical
        target_value: Target for numerical habits
        target_type: at_least or at_most
        position: Order in the stack
        duration_minutes: Estimated time in minutes
        category: Habit category
    """
    name: str = ""
    description: str = ""
    icon: str = "🎯"
    color: str = "#6366f1"
    frequency: str = "daily"
    habit_type: str = "boolean"
    target_value: float = 0.0
    target_type: str = "at_least"
    position: int = 0
    duration_minutes: int = 2
    category: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "frequency": self.frequency,
            "habit_type": self.habit_type,
            "target_value": self.target_value,
            "target_type": self.target_type,
            "position": self.position,
            "duration_minutes": self.duration_minutes,
            "category": self.category
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateHabit":
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            icon=data.get("icon", "🎯"),
            color=data.get("color", "#6366f1"),
            frequency=data.get("frequency", "daily"),
            habit_type=data.get("habit_type", "boolean"),
            target_value=data.get("target_value", 0.0),
            target_type=data.get("target_type", "at_least"),
            position=data.get("position", 0),
            duration_minutes=data.get("duration_minutes", 2),
            category=data.get("category", "")
        )


@dataclass
class HabitTemplate:
    """
    A pre-built habit template.

    A collection of habits designed to work together
    for a specific purpose or routine.

    Attributes:
        id: Unique identifier
        name: Template name
        description: What this template is for
        category: Template category
        difficulty: Difficulty level
        habits: List of habits in this template
        total_duration: Total estimated time in minutes
        tags: Search tags
        author: Template creator
        is_public: Whether template is shareable
        usage_count: How many times applied
        rating: User rating (1-5 stars)
        created_at: When template was created
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    category: TemplateCategory = TemplateCategory.CUSTOM
    difficulty: TemplateDifficulty = TemplateDifficulty.BEGINNER
    habits: List[TemplateHabit] = field(default_factory=list)
    total_duration: int = 0
    tags: List[str] = field(default_factory=list)
    author: str = "System"
    is_public: bool = True
    usage_count: int = 0
    rating: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Calculate total duration after initialization."""
        if not self.total_duration and self.habits:
            self.total_duration = sum(h.duration_minutes for h in self.habits)

    def add_habit(self, habit: TemplateHabit) -> None:
        """
        Add a habit to the template.

        Args:
            habit: TemplateHabit to add
        """
        habit.position = len(self.habits)
        self.habits.append(habit)
        self.total_duration = sum(h.duration_minutes for h in self.habits)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "difficulty": self.difficulty.value,
            "habits": [h.to_dict() for h in self.habits],
            "total_duration": self.total_duration,
            "tags": self.tags,
            "author": self.author,
            "is_public": self.is_public,
            "usage_count": self.usage_count,
            "rating": self.rating,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HabitTemplate":
        """Create from dictionary."""
        template = cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=TemplateCategory(data.get("category", "custom")),
            difficulty=TemplateDifficulty(data.get("difficulty", "beginner")),
            habits=[TemplateHabit.from_dict(h) for h in data.get("habits", [])],
            total_duration=data.get("total_duration", 0),
            tags=data.get("tags", []),
            author=data.get("author", "System"),
            is_public=data.get("is_public", True),
            usage_count=data.get("usage_count", 0),
            rating=data.get("rating", 0.0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        )
        return template

    def get_habit_count(self) -> int:
        """Get number of habits in template."""
        return len(self.habits)

    def __str__(self) -> str:
        """String representation."""
        difficulty_emoji = {
            TemplateDifficulty.BEGINNER: "🌱",
            TemplateDifficulty.INTERMEDIATE: "🌿",
            TemplateDifficulty.ADVANCED: "🌳",
        }.get(self.difficulty, "📋")

        return f"{difficulty_emoji} {self.name} ({self.get_habit_count()} habits, {self.total_duration} min)"


# Pre-built template library
DEFAULT_TEMPLATES: List[HabitTemplate] = [
    # Morning Routine - Beginner
    HabitTemplate(
        id="template_morning_beginner",
        name="Morning Starter",
        description="A gentle 5-minute morning routine to start your day right",
        category=TemplateCategory.MORNING,
        difficulty=TemplateDifficulty.BEGINNER,
        tags=["morning", "routine", "quick", "beginner"],
        total_duration=5
    ),
    # Evening Routine - Beginner
    HabitTemplate(
        id="template_evening_beginner",
        name="Evening Wind-Down",
        description="Relaxing evening routine for better sleep",
        category=TemplateCategory.EVENING,
        difficulty=TemplateDifficulty.BEGINNER,
        tags=["evening", "sleep", "relaxation", "beginner"],
        total_duration=10
    ),
    # Productivity - Beginner
    HabitTemplate(
        id="template_productivity_beginner",
        name="Focus Booster",
        description="Simple productivity habits for better work",
        category=TemplateCategory.PRODUCTIVITY,
        difficulty=TemplateDifficulty.BEGINNER,
        tags=["productivity", "focus", "work", "beginner"],
        total_duration=5
    ),
    # Health & Fitness - Beginner
    HabitTemplate(
        id="template_fitness_beginner",
        name="Daily Movement",
        description="Basic fitness habits for beginners",
        category=TemplateCategory.FITNESS,
        difficulty=TemplateDifficulty.BEGINNER,
        tags=["fitness", "health", "exercise", "beginner"],
        total_duration=10
    ),
    # Mental Wellness - Beginner
    HabitTemplate(
        id="template_mental_beginner",
        name="Mindfulness Starter",
        description="Introduction to mindfulness and meditation",
        category=TemplateCategory.MENTAL,
        difficulty=TemplateDifficulty.BEGINNER,
        tags=["mindfulness", "meditation", "mental health", "beginner"],
        total_duration=5
    ),
    # Morning Routine - Intermediate
    HabitTemplate(
        id="template_morning_intermediate",
        name="Power Morning",
        description="Energizing 20-minute morning routine",
        category=TemplateCategory.MORNING,
        difficulty=TemplateDifficulty.INTERMEDIATE,
        tags=["morning", "routine", "energy", "intermediate"],
        total_duration=20
    ),
    # Health & Fitness - Intermediate
    HabitTemplate(
        id="template_fitness_intermediate",
        name="Fitness Foundation",
        description="Build a solid fitness routine",
        category=TemplateCategory.FITNESS,
        difficulty=TemplateDifficulty.INTERMEDIATE,
        tags=["fitness", "strength", "cardio", "intermediate"],
        total_duration=30
    ),
    # Learning - Intermediate
    HabitTemplate(
        id="template_learning_intermediate",
        name="Continuous Learner",
        description="Daily learning habits for growth",
        category=TemplateCategory.LEARNING,
        difficulty=TemplateDifficulty.INTERMEDIATE,
        tags=["learning", "reading", "growth", "intermediate"],
        total_duration=25
    ),
    # Nutrition - Beginner
    HabitTemplate(
        id="template_nutrition_beginner",
        name="Healthy Eating Basics",
        description="Foundation habits for better nutrition",
        category=TemplateCategory.NUTRITION,
        difficulty=TemplateDifficulty.BEGINNER,
        tags=["nutrition", "diet", "health", "beginner"],
        total_duration=5
    ),
    # Complete Morning - Advanced
    HabitTemplate(
        id="template_morning_advanced",
        name="Ultimate Morning",
        description="Comprehensive 30-minute morning mastery routine",
        category=TemplateCategory.MORNING,
        difficulty=TemplateDifficulty.ADVANCED,
        tags=["morning", "routine", "complete", "advanced"],
        total_duration=30
    ),
]


def get_templates_by_category(
    category: TemplateCategory,
    templates: Optional[List[HabitTemplate]] = None
) -> List[HabitTemplate]:
    """
    Get templates by category.

    Args:
        category: Category to filter by
        templates: Optional list to search (uses default if None)

    Returns:
        List of matching templates
    """
    if templates is None:
        templates = DEFAULT_TEMPLATES

    return [t for t in templates if t.category == category]


def get_templates_by_difficulty(
    difficulty: TemplateDifficulty,
    templates: Optional[List[HabitTemplate]] = None
) -> List[HabitTemplate]:
    """
    Get templates by difficulty.

    Args:
        difficulty: Difficulty level to filter by
        templates: Optional list to search

    Returns:
        List of matching templates
    """
    if templates is None:
        templates = DEFAULT_TEMPLATES

    return [t for t in templates if t.difficulty == difficulty]


def search_templates(
    query: str,
    templates: Optional[List[HabitTemplate]] = None
) -> List[HabitTemplate]:
    """
    Search templates by name, description, or tags.

    Args:
        query: Search query
        templates: Optional list to search

    Returns:
        List of matching templates
    """
    if templates is None:
        templates = DEFAULT_TEMPLATES

    query_lower = query.lower()
    results = []

    for template in templates:
        # Search in name
        if query_lower in template.name.lower():
            results.append(template)
            continue

        # Search in description
        if query_lower in template.description.lower():
            results.append(template)
            continue

        # Search in tags
        if any(query_lower in tag.lower() for tag in template.tags):
            results.append(template)
            continue

    return results


def create_custom_template(
    name: str,
    description: str,
    habits: List[Dict[str, Any]],
    category: TemplateCategory = TemplateCategory.CUSTOM,
    difficulty: TemplateDifficulty = TemplateDifficulty.BEGINNER
) -> HabitTemplate:
    """
    Create a custom template from habit definitions.

    Args:
        name: Template name
        description: Template description
        habits: List of habit definitions (dicts)
        category: Template category
        difficulty: Difficulty level

    Returns:
        New HabitTemplate
    """
    template = HabitTemplate(
        name=name,
        description=description,
        category=category,
        difficulty=difficulty,
        author="User"
    )

    for i, habit_data in enumerate(habits):
        habit = TemplateHabit.from_dict(habit_data)
        habit.position = i
        template.add_habit(habit)

    return template


__all__ = [
    "TemplateCategory",
    "TemplateDifficulty",
    "TemplateHabit",
    "HabitTemplate",
    "DEFAULT_TEMPLATES",
    "get_templates_by_category",
    "get_templates_by_difficulty",
    "search_templates",
    "create_custom_template",
]
