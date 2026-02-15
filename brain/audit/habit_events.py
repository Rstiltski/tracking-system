"""
Habit Event Types - Immutable events for habit tracking.

This module defines all event types for the habit tracking system
following the Event Sourcing pattern. Events are immutable records
of things that happened in the system.

Event Sourcing Principles:
1. Events are immutable - once created, never changed
2. Events represent facts that occurred, not commands
3. Current state is derived by replaying events
4. Events are stored in the order they occurred

Usage:
    from brain.audit.habit_events import (
        HabitCreated, HabitCompleted, EventStore
    )
    
    # Create and store an event
    event = HabitCreated(
        habit_id="abc123",
        name="Morning Exercise",
        frequency=(1, 1)
    )
    event_store.append(event)
    
    # Replay events to rebuild state
    events = event_store.get_events("habit", "abc123")
    habit = replay_habit_events(events)
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import uuid
import json


class HabitEventType(str, Enum):
    """Types of habit events."""
    # Lifecycle events
    HABIT_CREATED = "HABIT_CREATED"
    HABIT_UPDATED = "HABIT_UPDATED"
    HABIT_ARCHIVED = "HABIT_ARCHIVED"
    HABIT_UNARCHIVED = "HABIT_UNARCHIVED"
    HABIT_DELETED = "HABIT_DELETED"
    
    # Completion events
    HABIT_COMPLETED = "HABIT_COMPLETED"
    HABIT_MISSED = "HABIT_MISSED"
    HABIT_UNMARKED = "HABIT_UNMARKED"
    HABIT_SKIPPED = "HABIT_SKIPPED"
    
    # Streak freeze events
    STREAK_FREEZE_USED = "STREAK_FREEZE_USED"
    STREAK_FREEZE_PURCHASED = "STREAK_FREEZE_PURCHASED"
    STREAK_FREEZE_AWARDED = "STREAK_FREEZE_AWARDED"
    
    # Score events
    SCORE_RECOMPUTED = "SCORE_RECOMPUTED"


@dataclass(frozen=True)
class HabitEvent:
    """
    Base class for all habit events.
    
    Events are immutable (frozen=True) to ensure they cannot be modified
    after creation, which is a core principle of event sourcing.
    
    Attributes:
        event_id: Unique identifier for this event (UUID v4)
        event_type: Type of event from HabitEventType
        entity_type: Type of entity ("habit", "streak_freeze", etc.)
        entity_id: ID of the affected entity
        timestamp: When the event occurred
        version: Schema version for future compatibility
        payload: Event-specific data as dictionary
        metadata: Optional context (user_id, source, session_id, etc.)
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    entity_type: str = "habit"
    entity_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "payload": self.payload,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HabitEvent":
        """Create event from dictionary."""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif not isinstance(timestamp, datetime):
            timestamp = datetime.now()
        
        return cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            event_type=data.get("event_type", ""),
            entity_type=data.get("entity_type", "habit"),
            entity_id=data.get("entity_id", ""),
            timestamp=timestamp,
            version=data.get("version", "1.0"),
            payload=data.get("payload", {}),
            metadata=data.get("metadata", {})
        )


# === Lifecycle Events ===

@dataclass(frozen=True)
class HabitCreated(HabitEvent):
    """
    Event: A new habit was created.
    
    Payload:
        - id: Habit ID
        - name: Habit name
        - description: Optional description
        - frequency: Tuple of (numerator, denominator)
        - habit_type: "boolean" or "numerical"
        - color: Hex color code
        - icon: Emoji icon
        - target_value: Target for numerical habits
        - target_type: "at_least" or "at_most"
    """
    event_type: str = HabitEventType.HABIT_CREATED.value
    entity_type: str = "habit"
    
    @classmethod
    def create(
        cls,
        habit_id: str,
        name: str,
        frequency: Tuple[int, int] = (1, 1),
        description: str = "",
        habit_type: str = "boolean",
        color: str = "#6366f1",
        icon: str = "🎯",
        target_value: float = 0.0,
        target_type: str = "at_least",
        user_id: Optional[int] = None
    ) -> "HabitCreated":
        """Factory method to create a HabitCreated event."""
        return cls(
            entity_id=habit_id,
            payload={
                "id": habit_id,
                "name": name,
                "description": description,
                "frequency": frequency,
                "habit_type": habit_type,
                "color": color,
                "icon": icon,
                "target_value": target_value,
                "target_type": target_type
            },
            metadata={"user_id": user_id} if user_id else {}
        )


@dataclass(frozen=True)
class HabitUpdated(HabitEvent):
    """
    Event: A habit was updated.
    
    Payload:
        - id: Habit ID
        - changes: Dictionary of field -> new_value
    """
    event_type: str = HabitEventType.HABIT_UPDATED.value
    entity_type: str = "habit"
    
    @classmethod
    def create(
        cls,
        habit_id: str,
        changes: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> "HabitUpdated":
        """Factory method to create a HabitUpdated event."""
        return cls(
            entity_id=habit_id,
            payload={
                "id": habit_id,
                "changes": changes
            },
            metadata={"user_id": user_id} if user_id else {}
        )


@dataclass(frozen=True)
class HabitArchived(HabitEvent):
    """Event: A habit was archived (soft delete)."""
    event_type: str = HabitEventType.HABIT_ARCHIVED.value
    entity_type: str = "habit"
    
    @classmethod
    def create(
        cls,
        habit_id: str,
        user_id: Optional[int] = None
    ) -> "HabitArchived":
        """Factory method to create a HabitArchived event."""
        return cls(
            entity_id=habit_id,
            payload={"id": habit_id},
            metadata={"user_id": user_id} if user_id else {}
        )


@dataclass(frozen=True)
class HabitUnarchived(HabitEvent):
    """Event: A habit was unarchived (restored)."""
    event_type: str = HabitEventType.HABIT_UNARCHIVED.value
    entity_type: str = "habit"
    
    @classmethod
    def create(
        cls,
        habit_id: str,
        user_id: Optional[int] = None
    ) -> "HabitUnarchived":
        """Factory method to create a HabitUnarchived event."""
        return cls(
            entity_id=habit_id,
            payload={"id": habit_id},
            metadata={"user_id": user_id} if user_id else {}
        )


@dataclass(frozen=True)
class HabitDeleted(HabitEvent):
    """Event: A habit was permanently deleted."""
    event_type: str = HabitEventType.HABIT_DELETED.value
    entity_type: str = "habit"
    
    @classmethod
    def create(
        cls,
        habit_id: str,
        user_id: Optional[int] = None
    ) -> "HabitDeleted":
        """Factory method to create a HabitDeleted event."""
        return cls(
            entity_id=habit_id,
            payload={"id": habit_id},
            metadata={"user_id": user_id} if user_id else {}
        )


# === Completion Events ===

@dataclass(frozen=True)
class HabitCompleted(HabitEvent):
    """
    Event: A habit was marked as completed for a date.
    
    Payload:
        - habit_id: ID of the habit
        - date: Date of completion (ISO format)
        - notes: Optional notes
        - xp_earned: XP earned for this completion
    """
    event_type: str = HabitEventType.HABIT_COMPLETED.value
    entity_type: str = "habit"
    
    @classmethod
    def create(
        cls,
        habit_id: str,
        completion_date: date,
        notes: str = "",
        xp_earned: int = 10,
        user_id: Optional[int] = None
    ) -> "HabitCompleted":
        """Factory method to create a HabitCompleted event."""
        return cls(
            entity_id=habit_id,
            payload={
                "habit_id": habit_id,
                "date": completion_date.isoformat(),
                "notes": notes,
                "xp_earned": xp_earned
            },
            metadata={"user_id": user_id} if user_id else {}
        )


@dataclass(frozen=True)
class HabitUnmarked(HabitEvent):
    """
    Event: A habit completion was removed for a date.
    
    Payload:
        - habit_id: ID of the habit
        - date: Date that was unmarked (ISO format)
    """
    event_type: str = HabitEventType.HABIT_UNMARKED.value
    entity_type: str = "habit"
    
    @classmethod
    def create(
        cls,
        habit_id: str,
        entry_date: date,
        user_id: Optional[int] = None
    ) -> "HabitUnmarked":
        """Factory method to create a HabitUnmarked event."""
        return cls(
            entity_id=habit_id,
            payload={
                "habit_id": habit_id,
                "date": entry_date.isoformat()
            },
            metadata={"user_id": user_id} if user_id else {}
        )


@dataclass(frozen=True)
class HabitSkipped(HabitEvent):
    """
    Event: A habit was marked as skipped for a date.
    
    Skipped days don't affect the score but are recorded for history.
    
    Payload:
        - habit_id: ID of the habit
        - date: Date that was skipped (ISO format)
        - reason: Optional reason for skipping
    """
    event_type: str = HabitEventType.HABIT_SKIPPED.value
    entity_type: str = "habit"
    
    @classmethod
    def create(
        cls,
        habit_id: str,
        skip_date: date,
        reason: str = "",
        user_id: Optional[int] = None
    ) -> "HabitSkipped":
        """Factory method to create a HabitSkipped event."""
        return cls(
            entity_id=habit_id,
            payload={
                "habit_id": habit_id,
                "date": skip_date.isoformat(),
                "reason": reason
            },
            metadata={"user_id": user_id} if user_id else {}
        )


@dataclass(frozen=True)
class HabitMissed(HabitEvent):
    """
    Event: A habit was missed (not completed) for a date.
    
    This event is emitted when a day passes without completion.
    
    Payload:
        - habit_id: ID of the habit
        - date: Date that was missed (ISO format)
        - streak_broken: Whether this broke the streak
    """
    event_type: str = HabitEventType.HABIT_MISSED.value
    entity_type: str = "habit"
    
    @classmethod
    def create(
        cls,
        habit_id: str,
        missed_date: date,
        streak_broken: bool = False,
        user_id: Optional[int] = None
    ) -> "HabitMissed":
        """Factory method to create a HabitMissed event."""
        return cls(
            entity_id=habit_id,
            payload={
                "habit_id": habit_id,
                "date": missed_date.isoformat(),
                "streak_broken": streak_broken
            },
            metadata={"user_id": user_id} if user_id else {}
        )


# === Streak Freeze Events ===

@dataclass(frozen=True)
class StreakFreezeUsed(HabitEvent):
    """
    Event: A streak freeze was used to preserve a streak.
    
    Payload:
        - habit_id: ID of the habit
        - date: Date that was frozen (ISO format)
        - freezes_remaining: Number of freezes left after use
    """
    event_type: str = HabitEventType.STREAK_FREEZE_USED.value
    entity_type: str = "streak_freeze"
    
    @classmethod
    def create(
        cls,
        habit_id: str,
        freeze_date: date,
        freezes_remaining: int,
        user_id: Optional[int] = None
    ) -> "StreakFreezeUsed":
        """Factory method to create a StreakFreezeUsed event."""
        return cls(
            entity_id=habit_id,
            payload={
                "habit_id": habit_id,
                "date": freeze_date.isoformat(),
                "freezes_remaining": freezes_remaining
            },
            metadata={"user_id": user_id} if user_id else {}
        )


@dataclass(frozen=True)
class StreakFreezePurchased(HabitEvent):
    """
    Event: A streak freeze was purchased with XP.
    
    Payload:
        - xp_cost: XP spent
        - xp_remaining: XP remaining after purchase
        - freezes_count: Total freezes after purchase
    """
    event_type: str = HabitEventType.STREAK_FREEZE_PURCHASED.value
    entity_type: str = "streak_freeze"
    
    @classmethod
    def create(
        cls,
        xp_cost: int,
        xp_remaining: int,
        freezes_count: int,
        user_id: Optional[int] = None
    ) -> "StreakFreezePurchased":
        """Factory method to create a StreakFreezePurchased event."""
        return cls(
            entity_id="inventory",
            payload={
                "xp_cost": xp_cost,
                "xp_remaining": xp_remaining,
                "freezes_count": freezes_count
            },
            metadata={"user_id": user_id} if user_id else {}
        )


@dataclass(frozen=True)
class StreakFreezeAwarded(HabitEvent):
    """
    Event: A streak freeze was awarded (earned through consistency).
    
    Payload:
        - reason: Why the freeze was awarded
        - freezes_count: Total freezes after award
    """
    event_type: str = HabitEventType.STREAK_FREEZE_AWARDED.value
    entity_type: str = "streak_freeze"
    
    @classmethod
    def create(
        cls,
        reason: str,
        freezes_count: int,
        user_id: Optional[int] = None
    ) -> "StreakFreezeAwarded":
        """Factory method to create a StreakFreezeAwarded event."""
        return cls(
            entity_id="inventory",
            payload={
                "reason": reason,
                "freezes_count": freezes_count
            },
            metadata={"user_id": user_id} if user_id else {}
        )


# === Score Events ===

@dataclass(frozen=True)
class ScoreRecomputed(HabitEvent):
    """
    Event: A habit's score was recomputed.
    
    Payload:
        - habit_id: ID of the habit
        - score_value: New score value (0.0-1.0)
        - score_percentage: Score as percentage (0-100)
        - trend: Trend value
    """
    event_type: str = HabitEventType.SCORE_RECOMPUTED.value
    entity_type: str = "habit"
    
    @classmethod
    def create(
        cls,
        habit_id: str,
        score_value: float,
        score_percentage: int,
        trend: float,
        user_id: Optional[int] = None
    ) -> "ScoreRecomputed":
        """Factory method to create a ScoreRecomputed event."""
        return cls(
            entity_id=habit_id,
            payload={
                "habit_id": habit_id,
                "score_value": score_value,
                "score_percentage": score_percentage,
                "trend": trend
            },
            metadata={"user_id": user_id} if user_id else {}
        )


# === Event Factory ===

def create_event_from_type(
    event_type: str,
    entity_id: str,
    payload: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> HabitEvent:
    """
    Factory function to create an event from type string.
    
    Useful for reconstructing events from storage.
    
    Args:
        event_type: Type of event (from HabitEventType)
        entity_id: ID of the affected entity
        payload: Event-specific data
        metadata: Optional context
    
    Returns:
        Appropriate HabitEvent subclass instance
    """
    event_classes = {
        HabitEventType.HABIT_CREATED.value: HabitCreated,
        HabitEventType.HABIT_UPDATED.value: HabitUpdated,
        HabitEventType.HABIT_ARCHIVED.value: HabitArchived,
        HabitEventType.HABIT_UNARCHIVED.value: HabitUnarchived,
        HabitEventType.HABIT_DELETED.value: HabitDeleted,
        HabitEventType.HABIT_COMPLETED.value: HabitCompleted,
        HabitEventType.HABIT_MISSED.value: HabitMissed,
        HabitEventType.HABIT_UNMARKED.value: HabitUnmarked,
        HabitEventType.HABIT_SKIPPED.value: HabitSkipped,
        HabitEventType.STREAK_FREEZE_USED.value: StreakFreezeUsed,
        HabitEventType.STREAK_FREEZE_PURCHASED.value: StreakFreezePurchased,
        HabitEventType.STREAK_FREEZE_AWARDED.value: StreakFreezeAwarded,
        HabitEventType.SCORE_RECOMPUTED.value: ScoreRecomputed,
    }
    
    event_class = event_classes.get(event_type, HabitEvent)
    
    return event_class(
        event_type=event_type,
        entity_id=entity_id,
        payload=payload,
        metadata=metadata or {}
    )


# Export all event types
__all__ = [
    # Base
    "HabitEventType",
    "HabitEvent",
    
    # Lifecycle events
    "HabitCreated",
    "HabitUpdated",
    "HabitArchived",
    "HabitUnarchived",
    "HabitDeleted",
    
    # Completion events
    "HabitCompleted",
    "HabitMissed",
    "HabitUnmarked",
    "HabitSkipped",
    
    # Streak freeze events
    "StreakFreezeUsed",
    "StreakFreezePurchased",
    "StreakFreezeAwarded",
    
    # Score events
    "ScoreRecomputed",
    
    # Factory
    "create_event_from_type",
]
