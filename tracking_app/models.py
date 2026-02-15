"""
Models Module - Data Models for the Tracking System

This module defines dataclasses for all entities in the tracking system.
Following PROJECT_RULES.md patterns for data models.

Usage:
    from tracking_app.models import Habit, Task
    
    habit = Habit(name="Morning Exercise", icon="🏃")
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import json


class FrequencyType(str, Enum):
    """Frequency types for habits."""
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class HabitType(str, Enum):
    """Types of habits."""
    BOOLEAN = "boolean"  # Simple yes/no completion
    NUMERICAL = "numerical"  # Track a number (e.g., glasses of water)


class Priority(str, Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TransactionType(str, Enum):
    """Types of financial transactions."""
    INCOME = "income"
    EXPENSE = "expense"


class Mood(str, Enum):
    """Mood options for health entries."""
    GREAT = "great"
    GOOD = "good"
    OKAY = "okay"
    BAD = "bad"


@dataclass
class Habit:
    """
    Represents a habit to track.
    
    Attributes:
        id: Unique identifier (UUID)
        name: Habit name
        description: Optional description
        frequency: Frequency type (daily, weekly, custom)
        frequency_data: Custom frequency data as tuple (numerator, denominator)
        habit_type: Boolean or numerical
        color: Hex color code for display
        icon: Emoji icon
        target_value: Target for numerical habits
        target_type: "at_least" or "at_most"
        archived: Whether habit is archived
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: str = ""
    name: str = ""
    description: str = ""
    frequency: str = FrequencyType.DAILY.value
    frequency_data: Tuple[int, int] = (1, 1)
    habit_type: str = HabitType.BOOLEAN.value
    color: str = "#6366f1"
    icon: str = "🎯"
    target_value: float = 0.0
    target_type: str = "at_least"
    archived: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set defaults after initialization."""
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency,
            "frequency_data": list(self.frequency_data),
            "habit_type": self.habit_type,
            "color": self.color,
            "icon": self.icon,
            "target_value": self.target_value,
            "target_type": self.target_type,
            "archived": self.archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Habit":
        """Create instance from dictionary."""
        freq_data = data.get("frequency_data", (1, 1))
        if isinstance(freq_data, list):
            freq_data = tuple(freq_data)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            frequency=data.get("frequency", FrequencyType.DAILY.value),
            frequency_data=freq_data,
            habit_type=data.get("habit_type", HabitType.BOOLEAN.value),
            color=data.get("color", "#6366f1"),
            icon=data.get("icon", "🎯"),
            target_value=data.get("target_value", 0.0),
            target_type=data.get("target_type", "at_least"),
            archived=data.get("archived", False),
            created_at=created_at,
            updated_at=updated_at,
        )


@dataclass
class HabitEntry:
    """
    Represents a habit completion entry.
    
    Attributes:
        id: Unique identifier
        habit_id: ID of the habit
        entry_date: Date of the entry
        value: Value (1.0 for boolean, actual value for numerical)
        notes: Optional notes
        skipped: Whether this entry was skipped
        created_at: Creation timestamp
    """
    id: str = ""
    habit_id: str = ""
    entry_date: date = None
    value: float = 1.0
    notes: str = ""
    skipped: bool = False
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set defaults after initialization."""
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
        if self.entry_date is None:
            self.entry_date = date.today()
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "entry_date": self.entry_date.isoformat() if self.entry_date else None,
            "value": self.value,
            "notes": self.notes,
            "skipped": self.skipped,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HabitEntry":
        """Create instance from dictionary."""
        entry_date = data.get("entry_date")
        if isinstance(entry_date, str):
            entry_date = date.fromisoformat(entry_date)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            id=data.get("id", ""),
            habit_id=data.get("habit_id", ""),
            entry_date=entry_date,
            value=data.get("value", 1.0),
            notes=data.get("notes", ""),
            skipped=data.get("skipped", False),
            created_at=created_at,
        )


@dataclass
class Task:
    """
    Represents a task/todo item.
    
    Attributes:
        id: Unique identifier
        title: Task title
        description: Optional description
        due_date: Due date (optional)
        priority: Priority level
        category: Category for grouping
        completed: Whether task is completed
        completed_at: Completion timestamp
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: str = ""
    title: str = ""
    description: str = ""
    due_date: Optional[datetime] = None
    priority: str = Priority.MEDIUM.value
    category: str = ""
    completed: bool = False
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set defaults after initialization."""
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority,
            "category": self.category,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create instance from dictionary."""
        due_date = data.get("due_date")
        if isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date)
        
        completed_at = data.get("completed_at")
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            due_date=due_date,
            priority=data.get("priority", Priority.MEDIUM.value),
            category=data.get("category", ""),
            completed=data.get("completed", False),
            completed_at=completed_at,
            created_at=created_at,
            updated_at=updated_at,
        )


@dataclass
class Transaction:
    """
    Represents a financial transaction.
    
    Attributes:
        id: Unique identifier
        description: Transaction description
        amount: Transaction amount
        type: Income or expense
        category: Category for grouping
        trans_date: Transaction date
        created_at: Creation timestamp
    """
    id: str = ""
    description: str = ""
    amount: float = 0.0
    type: str = TransactionType.EXPENSE.value
    category: str = ""
    trans_date: Optional[date] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set defaults after initialization."""
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
        if self.trans_date is None:
            self.trans_date = date.today()
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "type": self.type,
            "category": self.category,
            "trans_date": self.trans_date.isoformat() if self.trans_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        """Create instance from dictionary."""
        trans_date = data.get("trans_date")
        if isinstance(trans_date, str):
            trans_date = date.fromisoformat(trans_date)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            id=data.get("id", ""),
            description=data.get("description", ""),
            amount=data.get("amount", 0.0),
            type=data.get("type", TransactionType.EXPENSE.value),
            category=data.get("category", ""),
            trans_date=trans_date,
            created_at=created_at,
        )


@dataclass
class HealthEntry:
    """
    Represents a health tracking entry.
    
    Attributes:
        id: Unique identifier
        entry_date: Date of the entry
        weight: Weight measurement (optional)
        sleep_hours: Hours of sleep (optional)
        mood: Mood rating
        notes: Optional notes
        created_at: Creation timestamp
    """
    id: str = ""
    entry_date: date = None
    weight: Optional[float] = None
    sleep_hours: Optional[float] = None
    mood: str = Mood.GOOD.value
    notes: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set defaults after initialization."""
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
        if self.entry_date is None:
            self.entry_date = date.today()
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "entry_date": self.entry_date.isoformat() if self.entry_date else None,
            "weight": self.weight,
            "sleep_hours": self.sleep_hours,
            "mood": self.mood,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthEntry":
        """Create instance from dictionary."""
        entry_date = data.get("entry_date")
        if isinstance(entry_date, str):
            entry_date = date.fromisoformat(entry_date)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            id=data.get("id", ""),
            entry_date=entry_date,
            weight=data.get("weight"),
            sleep_hours=data.get("sleep_hours"),
            mood=data.get("mood", Mood.GOOD.value),
            notes=data.get("notes", ""),
            created_at=created_at,
        )


@dataclass
class Goal:
    """
    Represents a goal to track.
    
    Attributes:
        id: Unique identifier
        title: Goal title
        description: Optional description
        target: Target value
        current: Current progress
        unit: Unit of measurement
        deadline: Goal deadline (optional)
        completed: Whether goal is completed
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: str = ""
    title: str = ""
    description: str = ""
    target: float = 0.0
    current: float = 0.0
    unit: str = ""
    deadline: Optional[datetime] = None
    completed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set defaults after initialization."""
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress as percentage."""
        if self.target == 0:
            return 0.0
        return min(100.0, (self.current / self.target) * 100)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "target": self.target,
            "current": self.current,
            "unit": self.unit,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Goal":
        """Create instance from dictionary."""
        deadline = data.get("deadline")
        if isinstance(deadline, str):
            deadline = datetime.fromisoformat(deadline)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            target=data.get("target", 0.0),
            current=data.get("current", 0.0),
            unit=data.get("unit", ""),
            deadline=deadline,
            completed=data.get("completed", False),
            created_at=created_at,
            updated_at=updated_at,
        )


@dataclass
class Achievement:
    """
    Represents an achievement/badge.
    
    Attributes:
        id: Unique identifier
        name: Achievement name
        description: Achievement description
        icon: Emoji icon
        xp_reward: XP awarded when unlocked
        unlocked_at: Unlock timestamp (None if not unlocked)
        created_at: Creation timestamp
    """
    id: str = ""
    name: str = ""
    description: str = ""
    icon: str = "🏆"
    xp_reward: int = 0
    unlocked_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set defaults after initialization."""
        if not self.id:
            import uuid
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def is_unlocked(self) -> bool:
        """Check if achievement is unlocked."""
        return self.unlocked_at is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "xp_reward": self.xp_reward,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Achievement":
        """Create instance from dictionary."""
        unlocked_at = data.get("unlocked_at")
        if isinstance(unlocked_at, str):
            unlocked_at = datetime.fromisoformat(unlocked_at)
        
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            icon=data.get("icon", "🏆"),
            xp_reward=data.get("xp_reward", 0),
            unlocked_at=unlocked_at,
            created_at=created_at,
        )


# Export all models
__all__ = [
    # Enums
    "FrequencyType",
    "HabitType",
    "Priority",
    "TransactionType",
    "Mood",
    # Models
    "Habit",
    "HabitEntry",
    "Task",
    "Transaction",
    "HealthEntry",
    "Goal",
    "Achievement",
]