"""
Event Replay - Reconstruct state from event history.

This module provides functionality to replay events and reconstruct
the state of habits and other entities from the event store.

Usage:
    from brain.audit.event_replay import EventReplayer
    
    replayer = EventReplayer()
    habit_state = replayer.rebuild_habit(habit_id)
"""
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

from brain.audit.event_store import EventStore, get_event_store
from brain.audit.habit_events import (
    HabitEvent,
    HabitEventType,
)
from brain.models import Habit, Frequency, HabitType, Entry, EntryType

logger = logging.getLogger(__name__)


@dataclass
class ReplayedHabitState:
    """
    Reconstructed state of a habit from event replay.
    
    This represents the habit state at a specific point in time,
    reconstructed by replaying all events up to that point.
    """
    habit_id: str
    name: str = ""
    description: str = ""
    frequency: Frequency = field(default_factory=Frequency.daily)
    icon: str = "🎯"
    color: str = "#6366f1"
    habit_type: HabitType = HabitType.BOOLEAN
    is_archived: bool = False
    is_deleted: bool = False
    
    # Entries reconstructed from events
    entries: Dict[date, Entry] = field(default_factory=dict)
    
    # Computed values
    streak_count: int = 0
    total_completions: int = 0
    
    # Metadata
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    events_replayed: int = 0
    
    def to_habit(self) -> Habit:
        """Convert to a Habit model instance."""
        habit = Habit(
            id=self.habit_id,
            name=self.name,
            description=self.description,
            frequency=self.frequency,
            icon=self.icon,
            color=self.color,
            habit_type=self.habit_type
        )
        habit.is_archived = self.is_archived
        # Add entries to the habit's entry list
        for entry_date, entry in self.entries.items():
            habit.entries.add(entry)
        return habit
    
    def recalculate_streak(self) -> None:
        """Recalculate the streak count from entries."""
        if not self.entries:
            self.streak_count = 0
            return
        
        # Sort dates descending
        sorted_dates = sorted(self.entries.keys(), reverse=True)
        
        streak = 0
        current_date = date.today()
        
        for entry_date in sorted_dates:
            entry = self.entries[entry_date]
            
            # Only completed entries count toward streak
            if not entry.is_completed:
                continue
            
            # Check if this is consecutive
            if entry_date == current_date or entry_date == current_date - timedelta(days=1):
                streak += 1
                current_date = entry_date - timedelta(days=1)
            else:
                break
        
        self.streak_count = streak


class EventReplayer:
    """
    Replays events to reconstruct entity state.
    
    This is the core of event sourcing - the ability to rebuild
    the current state of any entity by replaying its event history.
    """
    
    def __init__(self, event_store: Optional[EventStore] = None):
        """
        Initialize the replayer.
        
        Args:
            event_store: Event store to read from (default: global store)
        """
        self.event_store = event_store or get_event_store()
    
    def rebuild_habit(
        self,
        habit_id: str,
        up_to: Optional[datetime] = None
    ) -> Optional[ReplayedHabitState]:
        """
        Rebuild a habit's state from its events.
        
        Args:
            habit_id: ID of the habit to rebuild
            up_to: Reconstruct state up to this timestamp (default: now)
        
        Returns:
            ReplayedHabitState or None if habit not found
        """
        # Get all events for this habit
        events = self.event_store.get_events(
            entity_type="habit",
            entity_id=habit_id,
            to_timestamp=up_to
        )
        
        if not events:
            return None
        
        state = None
        
        for event in events:
            state = self._apply_event(state, event)
        
        return state
    
    def _apply_event(
        self,
        state: Optional[ReplayedHabitState],
        event: HabitEvent
    ) -> ReplayedHabitState:
        """
        Apply an event to the state.
        
        This is the core event handling logic - each event type
        transforms the state in a specific way.
        """
        event_type = HabitEventType(event.event_type)
        
        # Handle HABIT_CREATED - initializes state
        if event_type == HabitEventType.HABIT_CREATED:
            freq_data = event.payload.get("frequency", (1, 1))
            frequency = Frequency.custom(
                times=freq_data[0],
                period_days=freq_data[1]
            )
            
            habit_type_str = event.payload.get("habit_type", "boolean")
            habit_type = HabitType.BOOLEAN if habit_type_str == "boolean" else HabitType.NUMERICAL
            
            state = ReplayedHabitState(
                habit_id=event.entity_id,
                name=event.payload.get("name", ""),
                description=event.payload.get("description", ""),
                frequency=frequency,
                icon=event.payload.get("icon", "🎯"),
                color=event.payload.get("color", "#6366f1"),
                habit_type=habit_type,
                created_at=event.timestamp,
                last_updated=event.timestamp,
                events_replayed=1
            )
            return state
        
        # All other events require existing state
        if state is None:
            return ReplayedHabitState(habit_id=event.entity_id)
        
        state.events_replayed += 1
        state.last_updated = event.timestamp
        
        # Handle HABIT_UPDATED
        if event_type == HabitEventType.HABIT_UPDATED:
            changes = event.payload.get("changes", {})
            if "name" in changes:
                state.name = changes["name"]
            if "description" in changes:
                state.description = changes["description"]
            if "icon" in changes:
                state.icon = changes["icon"]
            if "color" in changes:
                state.color = changes["color"]
        
        # Handle HABIT_COMPLETED
        elif event_type == HabitEventType.HABIT_COMPLETED:
            completion_date_str = event.payload.get("date")
            if completion_date_str:
                try:
                    completion_date = date.fromisoformat(completion_date_str)
                    entry = Entry(
                        date=completion_date,
                        value=EntryType.YES_MANUAL,
                        notes=event.payload.get("notes", "")
                    )
                    state.entries[completion_date] = entry
                    state.total_completions += 1
                    state.recalculate_streak()
                except ValueError:
                    logger.warning(f"Invalid date format: {completion_date_str}")
        
        # Handle HABIT_UNMARKED
        elif event_type == HabitEventType.HABIT_UNMARKED:
            entry_date_str = event.payload.get("date")
            if entry_date_str:
                try:
                    entry_date = date.fromisoformat(entry_date_str)
                    if entry_date in state.entries:
                        del state.entries[entry_date]
                        state.total_completions -= 1
                        state.recalculate_streak()
                except ValueError:
                    logger.warning(f"Invalid date format: {entry_date_str}")
        
        # Handle HABIT_SKIPPED
        elif event_type == HabitEventType.HABIT_SKIPPED:
            skip_date_str = event.payload.get("date")
            if skip_date_str:
                try:
                    skip_date = date.fromisoformat(skip_date_str)
                    entry = Entry(
                        date=skip_date,
                        value=EntryType.SKIP,
                        notes=event.payload.get("reason", "")
                    )
                    state.entries[skip_date] = entry
                except ValueError:
                    logger.warning(f"Invalid date format: {skip_date_str}")
        
        # Handle HABIT_ARCHIVED
        elif event_type == HabitEventType.HABIT_ARCHIVED:
            state.is_archived = True
        
        # Handle HABIT_UNARCHIVED
        elif event_type == HabitEventType.HABIT_UNARCHIVED:
            state.is_archived = False
        
        # Handle HABIT_DELETED
        elif event_type == HabitEventType.HABIT_DELETED:
            state.is_deleted = True
        
        return state
    
    def rebuild_all_habits(
        self,
        up_to: Optional[datetime] = None
    ) -> Dict[str, ReplayedHabitState]:
        """
        Rebuild all habits from events.
        
        Args:
            up_to: Reconstruct state up to this timestamp
        
        Returns:
            Dictionary of habit_id -> ReplayedHabitState
        """
        # Use the event store's built-in replay
        all_habits = self.event_store.replay_all_habits()
        
        result = {}
        for habit_id, habit_data in all_habits.items():
            # Convert to ReplayedHabitState
            freq_data = habit_data.get("frequency", (1, 1))
            frequency = Frequency.custom(
                times=freq_data[0],
                period_days=freq_data[1]
            )
            
            habit_type_str = habit_data.get("habit_type", "boolean")
            habit_type = HabitType.BOOLEAN if habit_type_str == "boolean" else HabitType.NUMERICAL
            
            state = ReplayedHabitState(
                habit_id=habit_id,
                name=habit_data.get("name", ""),
                description=habit_data.get("description", ""),
                frequency=frequency,
                icon=habit_data.get("icon", "🎯"),
                color=habit_data.get("color", "#6366f1"),
                habit_type=habit_type,
                is_archived=habit_data.get("is_archived", False),
                is_deleted=habit_data.get("is_deleted", False)
            )
            
            # Rebuild entries from completions
            for comp_date, comp_data in habit_data.get("completions", {}).items():
                try:
                    entry_date = date.fromisoformat(comp_date)
                    entry = Entry(
                        date=entry_date,
                        value=EntryType.YES_MANUAL,
                        notes=comp_data.get("notes", "")
                    )
                    state.entries[entry_date] = entry
                    state.total_completions += 1
                except ValueError:
                    pass
            
            state.recalculate_streak()
            result[habit_id] = state
        
        return result
    
    def get_event_history(
        self,
        habit_id: str,
        event_types: Optional[List[str]] = None
    ) -> List[HabitEvent]:
        """
        Get the event history for a habit.
        
        Args:
            habit_id: ID of the habit
            event_types: Filter by event types (optional)
        
        Returns:
            List of events
        """
        all_events = self.event_store.get_events(
            entity_type="habit",
            entity_id=habit_id
        )
        
        if event_types:
            return [e for e in all_events if e.event_type in event_types]
        
        return all_events
    
    def verify_integrity(
        self,
        habit_id: str,
        expected_state: Dict[str, Any]
    ) -> bool:
        """
        Verify that replayed state matches expected state.
        
        This is useful for detecting data corruption or missing events.
        
        Args:
            habit_id: ID of the habit to verify
            expected_state: Expected state values
        
        Returns:
            True if state matches, False otherwise
        """
        state = self.rebuild_habit(habit_id)
        if state is None:
            return False
        
        for key, expected_value in expected_state.items():
            actual_value = getattr(state, key, None)
            if actual_value != expected_value:
                return False
        
        return True


# Singleton instance
_replayer: Optional[EventReplayer] = None


def get_event_replayer() -> EventReplayer:
    """Get the global EventReplayer instance."""
    global _replayer
    if _replayer is None:
        _replayer = EventReplayer()
    return _replayer


# Export
__all__ = [
    "ReplayedHabitState",
    "EventReplayer",
    "get_event_replayer",
]