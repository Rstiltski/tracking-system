"""
Phase 3: The Nervous System - Event Bus

The Nervous System is the ONLY way the 3 Brains communicate with each other.

Rules:
1. Brains NEVER import each other's code
2. Brains NEVER call each other's functions directly
3. Brains communicate ONLY through events

How it works:
- OpsBrain completes a job → Emits JOB_COMPLETED event
- FinanceBrain listens for JOB_COMPLETED → Creates invoice
- RelationBrain listens for JOB_COMPLETED → Sends thank you SMS

Benefits:
- Loose coupling: Brains can be developed independently
- Resilience: If FinanceBrain crashes, OpsBrain keeps working
- Scalability: Events can be queued for async processing
- Auditability: All communication is logged
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import sqlite3
import json
from typing import Callable, Dict, List, Optional, Any
from collections import defaultdict
from datetime import datetime
from brain.core.contracts import IEvent, EventType

class EventHandler:
    """A registered event handler with metadata"""

    def __init__(self, handler_id: str, event_type: EventType, callback: Callable[[IEvent], None], brain_name: str, priority: int=100):
        self.handler_id = handler_id
        self.event_type = event_type
        self.callback = callback
        self.brain_name = brain_name
        self.priority = priority

class NervousSystem:
    """
    Phase 3: The Nervous System - Decoupled Communication

    This is a Publish/Subscribe event bus that allows brains to communicate
    without knowing about each other.

    Features:
    - Event emission (publish)
    - Event subscription (subscribe)
    - Event persistence (optional, for reliability)
    - Priority handling
    - Error isolation (one handler failing doesn't affect others)

    Usage:
        # In OpsBrain
        nervous_system.emit(Event(
            type=EventType.JOB_COMPLETED,
            caused_by_command_id="cmd-123",
            caused_by_user_id=1,
            payload={"job_id": 42}
        ))

        # In FinanceBrain
        @nervous_system.listen(EventType.JOB_COMPLETED)
        def on_job_completed(event):
            create_invoice(event.payload["job_id"])
    """

    def __init__(self, db_connection: Optional[sqlite3.Connection]=None, persist_events: bool=True):
        """
        Initialize the Nervous System.

        Args:
            db_connection: SQLite connection for event persistence
            persist_events: Whether to persist events to database
        """
        self.db_connection = db_connection
        self.persist_events = persist_events
        self.handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self.event_log: List[IEvent] = []
        self.max_log_size = 1000
        if self.persist_events and self.db_connection:
            self._init_event_table()

    def _init_event_table(self):
        """Create events table for persistence"""
        cursor = self.db_connection.cursor()
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS nervous_system_events (\n                event_id TEXT PRIMARY KEY,\n                event_type TEXT NOT NULL,\n                caused_by_command_id TEXT NOT NULL,\n                caused_by_user_id INTEGER NOT NULL,\n                recorded_at TEXT NOT NULL,\n                entity_type TEXT,\n                entity_id INTEGER,\n                company_id INTEGER NOT NULL,\n                payload TEXT NOT NULL,\n                metadata TEXT,\n                processed BOOLEAN DEFAULT 0,\n                processed_at TEXT\n            )\n        ')
        cursor.execute('\n            CREATE INDEX IF NOT EXISTS idx_events_type ON nervous_system_events(event_type)\n        ')
        cursor.execute('\n            CREATE INDEX IF NOT EXISTS idx_events_processed ON nervous_system_events(processed)\n        ')
        self.db_connection.commit()

    def listen(self, event_type: EventType, brain_name: str='Unknown', priority: int=100):
        """
        Decorator to register an event listener.

        Usage:
            @nervous_system.listen(EventType.JOB_COMPLETED, brain_name="FinanceBrain")
            def on_job_completed(event: IEvent):
                create_invoice(event.payload["job_id"])

        Args:
            event_type: The type of event to listen for
            brain_name: Name of the brain registering the listener
            priority: Handler priority (lower = higher priority)
        """

        def decorator(callback: Callable[[IEvent], None]):
            handler_id = f'{brain_name}_{event_type.value}_{len(self.handlers[event_type])}'
            handler = EventHandler(handler_id=handler_id, event_type=event_type, callback=callback, brain_name=brain_name, priority=priority)
            self.handlers[event_type].append(handler)
            self.handlers[event_type].sort(key=lambda h: h.priority)
            return callback
        return decorator

    def subscribe(self, event_type: EventType, callback: Callable[[IEvent], None], brain_name: str='Unknown', priority: int=100) -> str:
        """
        Programmatically subscribe to an event (alternative to @listen decorator).

        Returns:
            handler_id: Unique ID for this handler (can be used to unsubscribe)
        """
        handler_id = f'{brain_name}_{event_type.value}_{len(self.handlers[event_type])}'
        handler = EventHandler(handler_id=handler_id, event_type=event_type, callback=callback, brain_name=brain_name, priority=priority)
        self.handlers[event_type].append(handler)
        self.handlers[event_type].sort(key=lambda h: h.priority)
        return handler_id

    def unsubscribe(self, handler_id: str):
        """Unsubscribe a handler by ID"""
        for event_type, handlers in self.handlers.items():
            self.handlers[event_type] = [h for h in handlers if h.handler_id != handler_id]

    def emit(self, event: IEvent) -> Dict[str, Any]:
        """
        Emit an event to all registered listeners.

        Args:
            event: The event to emit

        Returns:
            Dict with emission results:
            - event_id: ID of the emitted event
            - listeners_notified: Number of listeners that received the event
            - errors: List of errors (if any handlers failed)
        """
        self.event_log.append(event)
        if len(self.event_log) > self.max_log_size:
            self.event_log = self.event_log[-self.max_log_size:]
        if self.persist_events and self.db_connection:
            self._persist_event(event)
        handlers = self.handlers.get(event.event_type, [])
        results = {'event_id': event.event_id, 'event_type': event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type), 'listeners_notified': 0, 'errors': []}
        for handler in handlers:
            try:
                handler.callback(event)
                results['listeners_notified'] += 1
            except Exception as e:
                error_info = {'handler_id': handler.handler_id, 'brain_name': handler.brain_name, 'error': str(e)}
                results.get('errors', 0).append(error_info)
        return results

    def _persist_event(self, event: IEvent):
        """Persist event to database"""
        cursor = self.db_connection.cursor()
        event_type_str = event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type)
        cursor.execute('\n            INSERT INTO nervous_system_events (\n                event_id, event_type, caused_by_command_id, caused_by_user_id,\n                recorded_at, entity_type, entity_id, company_id, payload, metadata\n            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\n        ', (event.event_id, event_type_str, event.caused_by_command_id, event.caused_by_user_id, event.recorded_at.isoformat(), event.entity_type, event.entity_id, event.company_id, json.dumps(event.payload), json.dumps(event.metadata)))
        self.db_connection.commit()

    def get_recent_events(self, limit: int=100, event_type: Optional[EventType]=None) -> List[IEvent]:
        """
        Get recent events from the in-memory log.

        Args:
            limit: Maximum number of events to return
            event_type: Filter by event type (optional)

        Returns:
            List of recent events (most recent first)
        """
        events = self.event_log
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return list(reversed(events[-limit:]))

    def get_handlers_for_event(self, event_type: EventType) -> List[EventHandler]:
        """Get all registered handlers for an event type"""
        return self.handlers.get(event_type, [])

    def get_all_handlers(self) -> Dict[str, List[str]]:
        """
        Get all registered handlers (for debugging).

        Returns:
            Dict mapping event_type -> list of brain names
        """
        result = {}
        for event_type, handlers in self.handlers.items():
            result[event_type.value] = [f'{h.brain_name} (priority: {h.priority})' for h in handlers]
        return result

    def clear_handlers(self):
        """Clear all registered handlers (for testing)"""
        self.handlers.clear()

    def signal(self, event_type_str: str, **kwargs):
        """
        Simplified event emission (for backward compatibility).

        Usage:
            nervous_system.signal("JOB_DONE", job_id=42)

        This is a convenience method that creates an IEvent and emits it.
        """
        event = IEvent(event_type=EventType(event_type_str), caused_by_command_id=kwargs.pop('command_id', 'system'), caused_by_user_id=kwargs.pop('user_id', 0), payload=kwargs)
        return self.emit(event)
_global_nervous_system: Optional[NervousSystem] = None

def get_nervous_system(db_connection: Optional[sqlite3.Connection]=None) -> NervousSystem:
    """
    Get the global NervousSystem instance.

    This creates a singleton for convenience, but you can also
    create your own instance for testing.
    """
    global _global_nervous_system
    if _global_nervous_system is None:
        _global_nervous_system = NervousSystem(db_connection=db_connection)
    return _global_nervous_system

def reset_nervous_system():
    """Reset the global nervous system (for testing)"""
    global _global_nervous_system
    _global_nervous_system = None