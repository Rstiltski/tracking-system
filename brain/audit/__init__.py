"""
Audit logging and replay functionality
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/06_audit_schema.md
- LLM_AGENT_QUICKSTART.md
"""

from brain.audit.logger import AuditLogger
from brain.audit.schema import ensure_audit_tables, ensure_habit_events_table
from brain.audit.event_store import EventStore, EventPublisher, get_event_store, get_event_publisher
from brain.audit.habit_events import (
    HabitEvent,
    HabitEventType,
    HabitCreated,
    HabitUpdated,
    HabitCompleted,
    HabitMissed,
    HabitUnmarked,
    HabitSkipped,
    HabitArchived,
    HabitUnarchived,
    HabitDeleted,
    StreakFreezeUsed,
    StreakFreezePurchased,
    StreakFreezeAwarded,
    ScoreRecomputed,
    create_event_from_type,
)
from brain.audit.event_replay import EventReplayer, ReplayedHabitState, get_event_replayer

__all__ = [
    # Audit logging
    "AuditLogger",
    "ensure_audit_tables",
    "ensure_habit_events_table",
    
    # Event sourcing
    "EventStore",
    "EventPublisher",
    "get_event_store",
    "get_event_publisher",
    
    # Event types
    "HabitEvent",
    "HabitEventType",
    "HabitCreated",
    "HabitUpdated",
    "HabitCompleted",
    "HabitMissed",
    "HabitUnmarked",
    "HabitSkipped",
    "HabitArchived",
    "HabitUnarchived",
    "HabitDeleted",
    "StreakFreezeUsed",
    "StreakFreezePurchased",
    "StreakFreezeAwarded",
    "ScoreRecomputed",
    "create_event_from_type",
    
    # Event replay
    "EventReplayer",
    "ReplayedHabitState",
    "get_event_replayer",
]
