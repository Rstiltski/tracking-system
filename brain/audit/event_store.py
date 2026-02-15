"""
Event Store - Immutable event storage with replay capability.

This module implements the Event Store pattern for event sourcing:
- Append-only storage for events
- Retrieve events by entity, type, or time range
- Replay events to reconstruct state

The Event Store is the source of truth for the system. All state
is derived by replaying events in order.

Usage:
    from brain.audit.event_store import EventStore
    
    store = EventStore()
    
    # Append an event
    event = HabitCreated.create(habit_id="abc", name="Exercise")
    store.append(event)
    
    # Get events for a habit
    events = store.get_events("habit", "abc")
    
    # Replay to rebuild state
    habit = store.replay_habit("abc")
"""
from datetime import datetime, date
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
import json
import logging

from brain.audit.habit_events import (
    HabitEvent,
    HabitEventType,
    HabitCreated,
    HabitUpdated,
    HabitCompleted,
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
from brain.audit.schema import ensure_habit_events_table

logger = logging.getLogger(__name__)


class EventStore:
    """
    Append-only event store for habit events.
    
    This is the core of the event sourcing system. All events are
    stored immutably and can be replayed to reconstruct state.
    
    The store uses SQLite for persistence via the db module.
    """
    
    def __init__(self):
        """Initialize the event store and ensure tables exist."""
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure event store tables exist."""
        try:
            ensure_habit_events_table()
        except Exception as e:
            logger.warning(f"Could not ensure event tables: {e}")
    
    def append(self, event: HabitEvent) -> str:
        """
        Append an event to the store.
        
        Events are immutable and cannot be modified after being stored.
        
        Args:
            event: The event to store
        
        Returns:
            The event ID
        
        Raises:
            ValueError: If event is invalid
        """
        if not event.event_type:
            raise ValueError("Event must have an event_type")
        
        if not event.entity_id:
            raise ValueError("Event must have an entity_id")
        
        try:
            import db
            
            with db.get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO habit_events (
                        id, event_type, entity_type, entity_id,
                        timestamp, version, payload, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.event_type,
                    event.entity_type,
                    event.entity_id,
                    event.timestamp.isoformat(),
                    event.version,
                    json.dumps(event.payload),
                    json.dumps(event.metadata) if event.metadata else None
                ))
                conn.commit()
            
            logger.debug(f"Appended event: {event.event_type} for {event.entity_id}")
            return event.event_id
            
        except Exception as e:
            logger.error(f"Failed to append event: {e}")
            raise
    
    def get_event(self, event_id: str) -> Optional[HabitEvent]:
        """
        Get a single event by ID.
        
        Args:
            event_id: The event's unique ID
        
        Returns:
            The event, or None if not found
        """
        try:
            import db
            
            with db.get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, event_type, entity_type, entity_id,
                           timestamp, version, payload, metadata
                    FROM habit_events
                    WHERE id = ?
                """, (event_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_event(row)
                return None
                
        except Exception as e:
            logger.error(f"Failed to get event {event_id}: {e}")
            return None
    
    def get_events(
        self,
        entity_type: str,
        entity_id: str,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None
    ) -> List[HabitEvent]:
        """
        Get all events for an entity.
        
        Args:
            entity_type: Type of entity ("habit", "streak_freeze", etc.)
            entity_id: ID of the entity
            from_timestamp: Optional start timestamp
            to_timestamp: Optional end timestamp
        
        Returns:
            List of events ordered by timestamp (oldest first)
        """
        try:
            import db
            
            with db.get_conn() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, event_type, entity_type, entity_id,
                           timestamp, version, payload, metadata
                    FROM habit_events
                    WHERE entity_type = ? AND entity_id = ?
                """
                params = [entity_type, entity_id]
                
                if from_timestamp:
                    query += " AND timestamp >= ?"
                    params.append(from_timestamp.isoformat())
                
                if to_timestamp:
                    query += " AND timestamp <= ?"
                    params.append(to_timestamp.isoformat())
                
                query += " ORDER BY timestamp ASC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [self._row_to_event(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get events for {entity_type}/{entity_id}: {e}")
            return []
    
    def get_events_by_type(
        self,
        event_type: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[HabitEvent]:
        """
        Get events by type.
        
        Args:
            event_type: Type of event (from HabitEventType)
            limit: Maximum number of events to return
            offset: Number of events to skip
        
        Returns:
            List of events ordered by timestamp (newest first)
        """
        try:
            import db
            
            with db.get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, event_type, entity_type, entity_id,
                           timestamp, version, payload, metadata
                    FROM habit_events
                    WHERE event_type = ?
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """, (event_type, limit, offset))
                
                rows = cursor.fetchall()
                return [self._row_to_event(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get events by type {event_type}: {e}")
            return []
    
    def get_all_events(
        self,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[HabitEvent]:
        """
        Get all events in the store.
        
        Args:
            from_timestamp: Optional start timestamp
            to_timestamp: Optional end timestamp
            limit: Maximum number of events to return
        
        Returns:
            List of events ordered by timestamp (oldest first)
        """
        try:
            import db
            
            with db.get_conn() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, event_type, entity_type, entity_id,
                           timestamp, version, payload, metadata
                    FROM habit_events
                    WHERE 1=1
                """
                params = []
                
                if from_timestamp:
                    query += " AND timestamp >= ?"
                    params.append(from_timestamp.isoformat())
                
                if to_timestamp:
                    query += " AND timestamp <= ?"
                    params.append(to_timestamp.isoformat())
                
                query += " ORDER BY timestamp ASC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [self._row_to_event(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get all events: {e}")
            return []
    
    def get_event_count(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> int:
        """
        Get the count of events.
        
        Args:
            entity_type: Optional entity type filter
            entity_id: Optional entity ID filter
        
        Returns:
            Number of events
        """
        try:
            import db
            
            with db.get_conn() as conn:
                cursor = conn.cursor()
                
                if entity_type and entity_id:
                    cursor.execute("""
                        SELECT COUNT(*) FROM habit_events
                        WHERE entity_type = ? AND entity_id = ?
                    """, (entity_type, entity_id))
                elif entity_type:
                    cursor.execute("""
                        SELECT COUNT(*) FROM habit_events
                        WHERE entity_type = ?
                    """, (entity_type,))
                else:
                    cursor.execute("SELECT COUNT(*) FROM habit_events")
                
                row = cursor.fetchone()
                return row[0] if row else 0
                
        except Exception as e:
            logger.error(f"Failed to get event count: {e}")
            return 0
    
    # === Replay Methods ===
    
    def replay_habit(self, habit_id: str) -> Optional[Dict[str, Any]]:
        """
        Replay all events for a habit to reconstruct its state.
        
        This is the core of event sourcing - the state is derived
        entirely from the event history.
        
        Args:
            habit_id: ID of the habit to rebuild
        
        Returns:
            Reconstructed habit state, or None if no events
        """
        events = self.get_events("habit", habit_id)
        
        if not events:
            return None
        
        state = {
            "id": habit_id,
            "name": "",
            "description": "",
            "frequency": (1, 1),
            "habit_type": "boolean",
            "color": "#6366f1",
            "icon": "🎯",
            "target_value": 0.0,
            "target_type": "at_least",
            "is_archived": False,
            "is_deleted": False,
            "completions": {},  # date -> completion data
            "skips": [],  # list of skipped dates
        }
        
        for event in events:
            state = self._apply_event(state, event)
        
        return state
    
    def replay_all_habits(self) -> Dict[str, Dict[str, Any]]:
        """
        Replay all events to reconstruct all habit states.
        
        Returns:
            Dictionary mapping habit_id to habit state
        """
        events = self.get_all_events()
        
        habits = {}
        
        for event in events:
            if event.entity_type != "habit":
                continue
            
            habit_id = event.entity_id
            
            if habit_id not in habits:
                habits[habit_id] = {
                    "id": habit_id,
                    "name": "",
                    "description": "",
                    "frequency": (1, 1),
                    "habit_type": "boolean",
                    "color": "#6366f1",
                    "icon": "🎯",
                    "target_value": 0.0,
                    "target_type": "at_least",
                    "is_archived": False,
                    "is_deleted": False,
                    "completions": {},
                    "skips": [],
                }
            
            habits[habit_id] = self._apply_event(habits[habit_id], event)
        
        # Filter out deleted habits
        return {
            hid: state
            for hid, state in habits.items()
            if not state.get("is_deleted", False)
        }
    
    def replay_inventory(self) -> Dict[str, Any]:
        """
        Replay streak freeze events to reconstruct inventory.
        
        Returns:
            Reconstructed inventory state
        """
        events = self.get_events("streak_freeze", "inventory")
        
        state = {
            "streak_freezes": {
                "count": 0,
                "max_freezes": 10,
                "history": []
            },
            "total_xp": 0,
            "level": 1
        }
        
        for event in events:
            state = self._apply_inventory_event(state, event)
        
        return state
    
    def _apply_event(self, state: Dict[str, Any], event: HabitEvent) -> Dict[str, Any]:
        """
        Apply an event to a habit state.
        
        This is a pure function - it returns a new state without
        modifying the original.
        
        Args:
            state: Current habit state
            event: Event to apply
        
        Returns:
            New state with event applied
        """
        import copy
        new_state = copy.deepcopy(state)
        
        event_type = event.event_type
        payload = event.payload
        
        if event_type == HabitEventType.HABIT_CREATED.value:
            new_state["id"] = payload.get("id", new_state["id"])
            new_state["name"] = payload.get("name", "")
            new_state["description"] = payload.get("description", "")
            new_state["frequency"] = payload.get("frequency", (1, 1))
            new_state["habit_type"] = payload.get("habit_type", "boolean")
            new_state["color"] = payload.get("color", "#6366f1")
            new_state["icon"] = payload.get("icon", "🎯")
            new_state["target_value"] = payload.get("target_value", 0.0)
            new_state["target_type"] = payload.get("target_type", "at_least")
        
        elif event_type == HabitEventType.HABIT_UPDATED.value:
            changes = payload.get("changes", {})
            for key, value in changes.items():
                if key in new_state:
                    new_state[key] = value
        
        elif event_type == HabitEventType.HABIT_ARCHIVED.value:
            new_state["is_archived"] = True
        
        elif event_type == HabitEventType.HABIT_UNARCHIVED.value:
            new_state["is_archived"] = False
        
        elif event_type == HabitEventType.HABIT_DELETED.value:
            new_state["is_deleted"] = True
        
        elif event_type == HabitEventType.HABIT_COMPLETED.value:
            completion_date = payload.get("date")
            if completion_date:
                new_state["completions"][completion_date] = {
                    "notes": payload.get("notes", ""),
                    "xp_earned": payload.get("xp_earned", 10)
                }
        
        elif event_type == HabitEventType.HABIT_UNMARKED.value:
            completion_date = payload.get("date")
            if completion_date and completion_date in new_state["completions"]:
                del new_state["completions"][completion_date]
        
        elif event_type == HabitEventType.HABIT_SKIPPED.value:
            skip_date = payload.get("date")
            if skip_date:
                new_state["skips"].append({
                    "date": skip_date,
                    "reason": payload.get("reason", "")
                })
        
        return new_state
    
    def _apply_inventory_event(self, state: Dict[str, Any], event: HabitEvent) -> Dict[str, Any]:
        """Apply an event to inventory state."""
        import copy
        new_state = copy.deepcopy(state)
        
        event_type = event.event_type
        payload = event.payload
        
        if event_type == HabitEventType.STREAK_FREEZE_PURCHASED.value:
            new_state["streak_freezes"]["count"] = payload.get("freezes_count", 0)
            new_state["total_xp"] = payload.get("xp_remaining", 0)
            new_state["streak_freezes"]["history"].append({
                "action": "purchased",
                "xp_cost": payload.get("xp_cost", 100)
            })
        
        elif event_type == HabitEventType.STREAK_FREEZE_AWARDED.value:
            new_state["streak_freezes"]["count"] = payload.get("freezes_count", 0)
            new_state["streak_freezes"]["history"].append({
                "action": "awarded",
                "reason": payload.get("reason", "")
            })
        
        elif event_type == HabitEventType.STREAK_FREEZE_USED.value:
            new_state["streak_freezes"]["count"] = payload.get("freezes_remaining", 0)
            new_state["streak_freezes"]["history"].append({
                "action": "used",
                "habit_id": payload.get("habit_id"),
                "date": payload.get("date")
            })
        
        return new_state
    
    def _row_to_event(self, row: tuple) -> HabitEvent:
        """Convert a database row to an event object."""
        (
            event_id, event_type, entity_type, entity_id,
            timestamp, version, payload, metadata
        ) = row
        
        # Parse timestamp
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        # Parse JSON fields
        if isinstance(payload, str):
            payload = json.loads(payload)
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        return create_event_from_type(
            event_type=event_type,
            entity_id=entity_id,
            payload=payload or {},
            metadata=metadata
        )


# === Event Publisher ===

class EventPublisher:
    """
    Publisher for events with subscriber support.
    
    Allows components to subscribe to specific event types and
    be notified when events are appended.
    """
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self._subscribers: Dict[str, List[Callable[[HabitEvent], None]]] = {}
        self._global_subscribers: List[Callable[[HabitEvent], None]] = []
    
    def subscribe(
        self,
        event_type: str,
        handler: Callable[[HabitEvent], None]
    ) -> None:
        """
        Subscribe to a specific event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Function to call when event occurs
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def subscribe_all(self, handler: Callable[[HabitEvent], None]) -> None:
        """
        Subscribe to all events.
        
        Args:
            handler: Function to call for any event
        """
        self._global_subscribers.append(handler)
    
    def publish(self, event: HabitEvent) -> str:
        """
        Publish an event: store it and notify subscribers.
        
        Args:
            event: Event to publish
        
        Returns:
            Event ID
        """
        # Store the event
        event_id = self.event_store.append(event)
        
        # Notify specific subscribers
        handlers = self._subscribers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")
        
        # Notify global subscribers
        for handler in self._global_subscribers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in global event handler: {e}")
        
        return event_id


# Singleton instances
_event_store: Optional[EventStore] = None
_event_publisher: Optional[EventPublisher] = None


def get_event_store() -> EventStore:
    """Get the singleton EventStore instance."""
    global _event_store
    if _event_store is None:
        _event_store = EventStore()
    return _event_store


def get_event_publisher() -> EventPublisher:
    """Get the singleton EventPublisher instance."""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher(get_event_store())
    return _event_publisher


# Export
__all__ = [
    "EventStore",
    "EventPublisher",
    "get_event_store",
    "get_event_publisher",
]