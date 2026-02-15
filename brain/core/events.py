"""
Brain Event System

Provides a simple event bus for decoupled communication between Brain components.
Events are used for audit logging, notifications, and cross-component signaling.

Usage:
    from brain.core.events import EventBus, Event

    # Subscribe to events
    def on_job_created(event: Event):
        print(f"Job {event.data['job_id']} created")

    EventBus.subscribe("job.created", on_job_created)

    # Publish events
    EventBus.publish(Event(
        event_type="job.created",
        entity_type="job",
        entity_id=123,
        data={"job_id": 123, "customer_id": 456}
    ))
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """
    Represents a domain event in the Brain system.

    Attributes:
        event_type: Type of event (e.g., "job.created", "invoice.sent")
        entity_type: Type of entity involved (e.g., "job", "customer", "invoice")
        entity_id: ID of the affected entity (optional)
        data: Additional event data payload
        timestamp: When the event occurred
        user_id: ID of user who triggered the event (optional)
        company_id: ID of company context (optional)
    """
    event_type: str
    entity_type: str
    entity_id: Optional[int] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[int] = None
    company_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_type": self.event_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "company_id": self.company_id,
        }


# Type alias for event handlers
EventHandler = Callable[[Event], None]


class EventBusClass:
    """
    Simple in-memory event bus for Brain component communication.

    This is a singleton that provides pub/sub functionality for domain events.
    Events are processed synchronously in the same thread.

    For production use, consider replacing with a message queue (Redis, RabbitMQ)
    for async processing and durability.
    """

    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._global_handlers: List[EventHandler] = []
        self._lock = threading.RLock()

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Subscribe a handler to a specific event type.

        Args:
            event_type: Event type to subscribe to (supports wildcards like "job.*")
            handler: Callback function to invoke when event occurs
        """
        with self._lock:
            self._handlers[event_type].append(handler)
        logger.debug(f"Handler subscribed to event type: {event_type}")

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Unsubscribe a handler from an event type.

        Args:
            event_type: Event type to unsubscribe from
            handler: Handler to remove
        """
        with self._lock:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
        logger.debug(f"Handler unsubscribed from event type: {event_type}")

    def subscribe_global(self, handler: EventHandler) -> None:
        """
        Subscribe a handler to all events.

        Args:
            handler: Callback function to invoke for every event
        """
        with self._lock:
            self._global_handlers.append(handler)
        logger.debug("Global handler subscribed")

    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribed handlers.

        Args:
            event: Event to publish

        Note:
            Handlers are called synchronously. Errors in handlers are logged
            but don't prevent other handlers from being called.
        """
        logger.debug(f"Publishing event: {event.event_type}")
        # Get handlers inside lock
        with self._lock:
            exact_handlers = self._handlers.get(event.event_type, []).copy()
            global_handlers = self._global_handlers.copy()
            wildcard_handlers = []
            if "." in event.event_type:
                event_prefix = event.event_type.rsplit(".", 1)[0]
                wildcard_key = f"{event_prefix}.*"
                wildcard_handlers = self._handlers.get(wildcard_key, []).copy()
        # Call handlers outside lock
        for handler in exact_handlers:
            self._safe_call(handler, event)
        for handler in wildcard_handlers:
            self._safe_call(handler, event)
        for handler in global_handlers:
            self._safe_call(handler, event)

    def _safe_call(self, handler: EventHandler, event: Event) -> None:
        """Safely call a handler, catching and logging any exceptions."""
        try:
            handler(event)
        except Exception as e:
            logger.error(
                f"Error in event handler for {event.event_type}: {e}",
                exc_info=True
            )

    def clear(self) -> None:
        """Clear all subscriptions (mainly for testing)."""
        with self._lock:
            self._handlers.clear()
            self._global_handlers.clear()
        logger.debug("Event bus cleared")


# Singleton instance
EventBus = EventBusClass()


# Common event type constants
class EventTypes:
    """Constants for common event types."""

    # Job events
    JOB_CREATED = "job.created"
    JOB_UPDATED = "job.updated"
    JOB_DELETED = "job.deleted"
    JOB_STATUS_CHANGED = "job.status_changed"
    JOB_COMPLETED = "job.completed"

    # Customer events
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_DELETED = "customer.deleted"

    # Invoice events
    INVOICE_CREATED = "invoice.created"
    INVOICE_SENT = "invoice.sent"
    INVOICE_PAID = "invoice.paid"
    INVOICE_VOIDED = "invoice.voided"

    # Quote events
    QUOTE_CREATED = "quote.created"
    QUOTE_SENT = "quote.sent"
    QUOTE_ACCEPTED = "quote.accepted"
    QUOTE_DECLINED = "quote.declined"

    # Payment events
    PAYMENT_RECEIVED = "payment.received"
    PAYMENT_REFUNDED = "payment.refunded"

    # User events
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_CREATED = "user.created"

    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"


def create_event(
    event_type: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    user_id: Optional[int] = None,
    company_id: Optional[int] = None,
    **data: Any
) -> Event:
    """
    Convenience function to create and return an Event.

    Args:
        event_type: Type of event
        entity_type: Type of entity
        entity_id: ID of entity (optional)
        user_id: ID of user (optional)
        company_id: ID of company (optional)
        **data: Additional event data

    Returns:
        Configured Event instance
    """
    return Event(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        data=data,
        user_id=user_id,
        company_id=company_id,
    )


def publish_event(
    event_type: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    user_id: Optional[int] = None,
    company_id: Optional[int] = None,
    **data: Any
) -> None:
    """
    Convenience function to create and publish an event in one call.

    Args:
        event_type: Type of event
        entity_type: Type of entity
        entity_id: ID of entity (optional)
        user_id: ID of user (optional)
        company_id: ID of company (optional)
        **data: Additional event data
    """
    event = create_event(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        company_id=company_id,
        **data
    )
    EventBus.publish(event)
