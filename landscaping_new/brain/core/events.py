"""
Events System for Brain

Handles event emission and subscription for the brain system.
"""
from __future__ import annotations
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Initialize logger
logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Represents an event in the system."""
    name: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str = ""

class EventListener:
    """A listener that can handle events."""
    
    def __init__(self, callback: Callable[[Event], None], event_types: Optional[List[str]] = None):
        self.callback = callback
        self.event_types = set(event_types) if event_types else None
    
    def can_handle(self, event_name: str) -> bool:
        """Check if this listener can handle the given event type."""
        if self.event_types is None:
            return True
        return event_name in self.event_types
    
    def handle(self, event: Event) -> None:
        """Handle an event."""
        try:
            self.callback(event)
        except Exception as e:
            logger.error(f"Error in event listener: {e}")

class EventManager:
    """
    Manages events and listeners in the brain system.
    
    Provides a pub/sub mechanism for emitting and listening to events.
    """
    
    def __init__(self):
        self.listeners: List[EventListener] = []
        logger.info("EventManager initialized")
    
    def subscribe(self, callback: Callable[[Event], None], event_types: Optional[List[str]] = None) -> None:
        """
        Subscribe to events.
        
        Args:
            callback: Function to call when event occurs
            event_types: List of event types to listen for (None means all events)
        """
        listener = EventListener(callback, event_types)
        self.listeners.append(listener)
        logger.debug(f"Subscribed to events: {event_types or 'all'}")
    
    def unsubscribe(self, callback: Callable[[Event], None]) -> bool:
        """
        Unsubscribe from events.
        
        Args:
            callback: The callback function to unsubscribe
            
        Returns:
            True if unsubscribed, False if not found
        """
        for i, listener in enumerate(self.listeners):
            if listener.callback == callback:
                del self.listeners[i]
                logger.debug("Unsubscribed from events")
                return True
        return False
    
    def emit(self, event_name: str, data: Dict[str, Any], source: str = "") -> None:
        """
        Emit an event to all interested listeners.
        
        Args:
            event_name: Name/type of the event
            data: Event data
            source: Source of the event
        """
        event = Event(
            name=event_name,
            data=data,
            timestamp=datetime.now(),
            source=source
        )
        
        # Notify all listeners that can handle this event
        for listener in self.listeners:
            if listener.can_handle(event_name):
                try:
                    listener.handle(event)
                except Exception as e:
                    logger.error(f"Error in event listener: {e}")
        
        logger.debug(f"Emitted event: {event_name} from {source}")
    
    def get_listener_count(self) -> int:
        """Get the number of registered listeners."""
        return len(self.listeners)
    
    def clear_listeners(self) -> None:
        """Remove all listeners."""
        self.listeners.clear()
        logger.debug("Cleared all event listeners")