"""
Notification Engine

Core engine for creating, scheduling, and dispatching notifications.
Implements the Strategy Pattern for channel selection and fallback logic.

Reference:
- Phase 4.1 Research Document, Section 5: NotificationEngine Class
- PROJECT_RULES.md: All operations through Tools pattern
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Callable
import logging
import json

from brain.notifications.models import (
    Notification,
    NotificationType,
    NotificationPriority,
    NotificationStatus,
    NotificationChannel,
    ReminderSchedule,
    PushSubscription,
    NotificationLog,
    NotificationPreferences,
    CompletionHistory,
)
from brain.notifications.channels import (
    NotificationChannelBase,
    InAppChannel,
    WebPushChannel,
    EmailChannel,
    DesktopChannel,
    ChannelResult,
    get_channel,
)
from brain.notifications.templates import NotificationTemplates, render_notification

logger = logging.getLogger(__name__)


class NotificationEngine:
    """
    Main engine for managing notifications.
    
    Coordinates the creation, storage, and delivery of notifications
    across multiple channels with fallback logic.
    
    Example:
        engine = NotificationEngine()
        
        # Create a notification
        notification = engine.create_notification(
            type=NotificationType.HABIT_REMINDER,
            title="Time to hydrate!",
            message="Don't forget to drink water",
            entity_type="habit",
            entity_id="habit-123"
        )
        
        # Dispatch via appropriate channels
        result = engine.dispatch(notification)
    """
    
    def __init__(self, db=None):
        """
        Initialize the notification engine.
        
        Args:
            db: Database instance (optional, uses global if not provided)
        """
        self._db = db
        self._channels: Dict[NotificationChannel, NotificationChannelBase] = {}
        self._templates = NotificationTemplates()
        self._callbacks: Dict[str, List[Callable]] = {}
        
        # Initialize default channels
        self._init_channels()
    
    @property
    def db(self):
        """Get database instance."""
        if self._db is None:
            from tracking_app.database import get_db
            self._db = get_db()
        return self._db
    
    def _init_channels(self) -> None:
        """Initialize notification channels."""
        # In-app channel is always available
        self._channels[NotificationChannel.IN_APP] = InAppChannel(db=self._db)
        
        # Web Push channel (requires VAPID config)
        self._channels[NotificationChannel.WEB_PUSH] = WebPushChannel(db=self._db)
        
        # Email channel (requires SMTP config)
        self._channels[NotificationChannel.EMAIL] = EmailChannel(db=self._db)
        
        # Desktop channel
        self._channels[NotificationChannel.DESKTOP] = DesktopChannel()
    
    def get_channel(self, channel_type: NotificationChannel) -> Optional[NotificationChannelBase]:
        """Get a channel instance by type."""
        return self._channels.get(channel_type)
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """
        Register a callback for notification events.
        
        Args:
            event: Event name ('created', 'sent', 'delivered', 'failed', 'clicked')
            callback: Function to call with (notification, **kwargs)
        """
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)
    
    def _trigger_callbacks(self, event: str, notification: Notification, **kwargs) -> None:
        """Trigger registered callbacks for an event."""
        callbacks = self._callbacks.get(event, [])
        for callback in callbacks:
            try:
                callback(notification, **kwargs)
            except Exception as e:
                logger.error(f"Callback error for {event}: {e}")
    
    # ==========================================
    # Notification CRUD Operations
    # ==========================================
    
    def create_notification(
        self,
        type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        scheduled_for: Optional[datetime] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        action_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        persist: bool = True,
    ) -> Notification:
        """
        Create a new notification.
        
        Args:
            type: Type of notification
            title: Notification title
            message: Notification message
            priority: Priority level
            scheduled_for: When to send (None = immediate)
            entity_type: Related entity type (habit, task, goal)
            entity_id: Related entity ID
            action_url: URL to open when clicked
            metadata: Additional metadata
            persist: Whether to save to database
            
        Returns:
            Created Notification object
        """
        notification = Notification(
            type=type,
            title=title,
            message=message,
            priority=priority,
            scheduled_for=scheduled_for,
            entity_type=entity_type,
            entity_id=entity_id,
            action_url=action_url,
            metadata=metadata or {},
        )
        
        if persist:
            self._save_notification(notification)
        
        self._trigger_callbacks('created', notification)
        
        logger.info(f"Created notification: {notification.id} - {title}")
        
        return notification
    
    def _save_notification(self, notification: Notification) -> None:
        """Save notification to database."""
        data = notification.to_dict()
        
        self.db.execute(
            """INSERT INTO notifications 
               (id, type, title, message, priority, status, scheduled_for,
                entity_type, entity_id, action_url, metadata, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data['id'], data['type'], data['title'], data['message'],
                data['priority'], data['status'], data['scheduled_for'],
                data['entity_type'], data['entity_id'], data['action_url'],
                data['metadata'], data['created_at'], data['updated_at']
            )
        )
    
    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get a notification by ID."""
        row = self.db.fetch_one(
            "SELECT * FROM notifications WHERE id = ?",
            (notification_id,)
        )
        
        return Notification.from_dict(row) if row else None
    
    def get_pending_notifications(self, limit: int = 100) -> List[Notification]:
        """Get all pending notifications."""
        rows = self.db.fetch_all(
            """SELECT * FROM notifications 
               WHERE status = 'pending' 
               ORDER BY priority DESC, scheduled_for ASC 
               LIMIT ?""",
            (limit,)
        )
        
        return [Notification.from_dict(row) for row in rows]
    
    def get_due_notifications(self) -> List[Notification]:
        """Get notifications that are due to be sent."""
        now = datetime.now().isoformat()
        
        rows = self.db.fetch_all(
            """SELECT * FROM notifications 
               WHERE status IN ('pending', 'scheduled')
               AND (scheduled_for IS NULL OR scheduled_for <= ?)
               ORDER BY priority DESC""",
            (now,)
        )
        
        return [Notification.from_dict(row) for row in rows]
    
    def update_notification_status(
        self, 
        notification_id: str, 
        status: NotificationStatus
    ) -> bool:
        """Update notification status."""
        try:
            self.db.execute(
                """UPDATE notifications 
                   SET status = ?, updated_at = ? 
                   WHERE id = ?""",
                (status.value, datetime.now().isoformat(), notification_id)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update notification status: {e}")
            return False
    
    def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification."""
        try:
            self.db.execute(
                "DELETE FROM notifications WHERE id = ?",
                (notification_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete notification: {e}")
            return False
    
    # ==========================================
    # Dispatch Operations
    # ==========================================
    
    def dispatch(
        self,
        notification: Notification,
        channels: Optional[List[NotificationChannel]] = None,
        user_id: str = "default",
        preferences: Optional[NotificationPreferences] = None,
    ) -> Dict[NotificationChannel, ChannelResult]:
        """
        Dispatch a notification through appropriate channels.
        
        Implements fallback logic:
        1. Try Web Push if available and enabled
        2. Fall back to Email for high priority or if push fails
        3. Always store as In-App notification
        
        Args:
            notification: Notification to dispatch
            channels: Specific channels to use (None = auto-select)
            user_id: User ID for preferences
            preferences: User notification preferences
            
        Returns:
            Dictionary mapping channels to their results
        """
        results: Dict[NotificationChannel, ChannelResult] = {}
        
        # Load preferences if not provided
        if preferences is None:
            preferences = self.get_preferences(user_id)
        
        # Check if notifications are enabled
        if not preferences.enabled:
            logger.info(f"Notifications disabled for user {user_id}")
            return results
        
        # Check quiet hours
        if preferences.is_quiet_hours():
            # Only send urgent notifications during quiet hours
            if notification.priority != NotificationPriority.URGENT:
                logger.info(f"Quiet hours active, skipping notification {notification.id}")
                return results
        
        # Check if this notification type is enabled
        if not preferences.is_type_enabled(notification.type):
            logger.info(f"Notification type {notification.type} disabled")
            return results
        
        # Determine channels to use
        if channels is None:
            channels = self._select_channels(notification, preferences)
        
        # Track if any channel succeeded
        any_success = False
        
        # Dispatch to each channel
        for channel_type in channels:
            channel = self._channels.get(channel_type)
            
            if channel is None or not channel.is_available():
                logger.warning(f"Channel {channel_type} not available")
                continue
            
            # Get recipient for this channel
            recipient = self._get_recipient(channel_type, user_id, preferences)
            
            if not recipient and channel_type not in [NotificationChannel.IN_APP, NotificationChannel.DESKTOP]:
                logger.warning(f"No recipient for channel {channel_type}")
                continue
            
            # Send via channel
            result = channel.send(notification, recipient)
            results[channel_type] = result
            
            if result.success:
                any_success = True
                self._log_dispatch(notification, result)
                self._trigger_callbacks('sent', notification, channel=channel_type)
            else:
                self._log_dispatch(notification, result)
                self._trigger_callbacks('failed', notification, channel=channel_type, error=result.error)
        
        # Update notification status
        if any_success:
            notification.mark_sent()
            self.update_notification_status(notification.id, NotificationStatus.SENT)
        else:
            notification.mark_failed()
            self.update_notification_status(notification.id, NotificationStatus.FAILED)
        
        return results
    
    def _select_channels(
        self,
        notification: Notification,
        preferences: NotificationPreferences
    ) -> List[NotificationChannel]:
        """
        Select appropriate channels based on notification and preferences.
        
        Priority-based channel selection:
        - URGENT: Web Push + Email + In-App
        - HIGH: Web Push + In-App (Email fallback)
        - MEDIUM/LOW: Web Push + In-App
        """
        channels = []
        
        # Always include in-app
        channels.append(NotificationChannel.IN_APP)
        
        # Web Push if enabled
        if preferences.browser_notifications_enabled:
            channels.append(NotificationChannel.WEB_PUSH)
        
        # Email for high priority or if enabled
        if notification.priority in [NotificationPriority.HIGH, NotificationPriority.URGENT]:
            if preferences.email_notifications_enabled and preferences.email_address:
                channels.append(NotificationChannel.EMAIL)
        
        return channels
    
    def _get_recipient(
        self,
        channel_type: NotificationChannel,
        user_id: str,
        preferences: NotificationPreferences
    ) -> Optional[str]:
        """Get recipient identifier for a channel."""
        if channel_type == NotificationChannel.EMAIL:
            return preferences.email_address
        
        if channel_type == NotificationChannel.WEB_PUSH:
            # Return the first active subscription
            subscriptions = self.get_active_subscriptions(user_id)
            return subscriptions[0].id if subscriptions else None
        
        return user_id
    
    def _log_dispatch(self, notification: Notification, result: ChannelResult) -> None:
        """Log a dispatch attempt."""
        log_entry = result.to_log(notification.id)
        data = log_entry.to_dict()
        
        self.db.execute(
            """INSERT INTO notification_logs 
               (id, notification_id, channel, status, error_message, 
                response_code, dispatched_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                data['id'], data['notification_id'], data['channel'],
                data['status'], data['error_message'], data['response_code'],
                data['dispatched_at']
            )
        )
    
    # ==========================================
    # Template-based Creation
    # ==========================================
    
    def create_from_template(
        self,
        template_id: str,
        context: Dict[str, Any],
        type: NotificationType = NotificationType.SYSTEM,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        **kwargs
    ) -> Optional[Notification]:
        """
        Create a notification from a template.
        
        Args:
            template_id: Template identifier
            context: Variables for template rendering
            type: Notification type
            priority: Priority level
            **kwargs: Additional notification parameters
            
        Returns:
            Created Notification or None if template not found
        """
        title, message = self._templates.render(template_id, context)
        
        if title is None:
            return None
        
        return self.create_notification(
            type=type,
            title=title,
            message=message,
            priority=priority,
            **kwargs
        )
    
    # ==========================================
    # Reminder Schedule Operations
    # ==========================================
    
    def create_reminder_schedule(
        self,
        entity_type: str,
        entity_id: str,
        reminder_time: str,  # HH:MM format
        days_of_week: Optional[List[int]] = None,
        channels: Optional[List[NotificationChannel]] = None,
        is_smart: bool = False,
        user_id: str = "default",
    ) -> ReminderSchedule:
        """
        Create a reminder schedule.
        
        Args:
            entity_type: Type of entity (habit, task, goal)
            entity_id: ID of the entity
            reminder_time: Time to send reminder (HH:MM)
            days_of_week: Days to send (0=Monday, 6=Sunday)
            channels: Notification channels to use
            is_smart: Enable smart scheduling
            user_id: User ID
            
        Returns:
            Created ReminderSchedule
        """
        from datetime import time as dt_time
        
        schedule = ReminderSchedule(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            reminder_time=dt_time.fromisoformat(reminder_time),
            days_of_week=days_of_week or list(range(7)),
            channels=channels or [NotificationChannel.IN_APP],
            is_smart=is_smart,
        )
        
        self._save_schedule(schedule)
        
        return schedule
    
    def _save_schedule(self, schedule: ReminderSchedule) -> None:
        """Save reminder schedule to database."""
        data = schedule.to_dict()
        
        self.db.execute(
            """INSERT INTO reminder_schedules 
               (id, user_id, entity_type, entity_id, reminder_time, 
                days_of_week, enabled, snooze_minutes, max_snoozes, 
                current_snoozes, is_smart, smart_time, channels, 
                created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data['id'], data['user_id'], data['entity_type'],
                data['entity_id'], data['reminder_time'], data['days_of_week'],
                data['enabled'], data['snooze_minutes'], data['max_snoozes'],
                data['current_snoozes'], data['is_smart'], data['smart_time'],
                data['channels'], data['created_at'], data['updated_at']
            )
        )
    
    def get_reminder_schedule(self, entity_type: str, entity_id: str) -> Optional[ReminderSchedule]:
        """Get reminder schedule for an entity."""
        row = self.db.fetch_one(
            """SELECT * FROM reminder_schedules 
               WHERE entity_type = ? AND entity_id = ?""",
            (entity_type, entity_id)
        )
        
        return ReminderSchedule.from_dict(row) if row else None
    
    def get_active_schedules(self) -> List[ReminderSchedule]:
        """Get all active reminder schedules."""
        rows = self.db.fetch_all(
            "SELECT * FROM reminder_schedules WHERE enabled = 1"
        )
        
        return [ReminderSchedule.from_dict(row) for row in rows]
    
    def update_schedule(self, schedule: ReminderSchedule) -> bool:
        """Update a reminder schedule."""
        try:
            data = schedule.to_dict()
            self.db.execute(
                """UPDATE reminder_schedules 
                   SET reminder_time = ?, days_of_week = ?, enabled = ?,
                       is_smart = ?, smart_time = ?, channels = ?, updated_at = ?
                   WHERE id = ?""",
                (
                    data['reminder_time'], data['days_of_week'], data['enabled'],
                    data['is_smart'], data['smart_time'], data['channels'],
                    data['updated_at'], data['id']
                )
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update schedule: {e}")
            return False
    
    # ==========================================
    # Push Subscription Operations
    # ==========================================
    
    def register_push_subscription(
        self,
        user_id: str,
        endpoint: str,
        p256dh: str,
        auth: str,
        user_agent: str = "",
        device_name: str = "",
    ) -> PushSubscription:
        """
        Register a Web Push subscription.
        
        Args:
            user_id: User ID
            endpoint: Push service endpoint URL
            p256dh: Public encryption key
            auth: Authentication secret
            user_agent: Browser user agent
            device_name: Friendly device name
            
        Returns:
            Created PushSubscription
        """
        # Check if subscription already exists
        existing = self.db.fetch_one(
            "SELECT id FROM push_subscriptions WHERE endpoint = ?",
            (endpoint,)
        )
        
        if existing:
            # Update existing subscription
            self.db.execute(
                """UPDATE push_subscriptions 
                   SET user_id = ?, p256dh = ?, auth = ?, user_agent = ?,
                       device_name = ?, last_active = ?, is_active = 1
                   WHERE endpoint = ?""",
                (user_id, p256dh, auth, user_agent, device_name, 
                 datetime.now().isoformat(), endpoint)
            )
            
            return PushSubscription(
                id=existing['id'],
                user_id=user_id,
                endpoint=endpoint,
                p256dh=p256dh,
                auth=auth,
                user_agent=user_agent,
                device_name=device_name,
                last_active=datetime.now(),
            )
        
        # Create new subscription
        subscription = PushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
            user_agent=user_agent,
            device_name=device_name,
        )
        
        data = subscription.to_dict()
        self.db.execute(
            """INSERT INTO push_subscriptions 
               (id, user_id, endpoint, p256dh, auth, user_agent, 
                device_name, last_active, is_active, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data['id'], data['user_id'], data['endpoint'],
                data['p256dh'], data['auth'], data['user_agent'],
                data['device_name'], data['last_active'], 1, data['created_at']
            )
        )
        
        logger.info(f"Registered push subscription for user {user_id}")
        
        return subscription
    
    def get_active_subscriptions(self, user_id: str) -> List[PushSubscription]:
        """Get all active push subscriptions for a user."""
        rows = self.db.fetch_all(
            """SELECT * FROM push_subscriptions 
               WHERE user_id = ? AND is_active = 1""",
            (user_id,)
        )
        
        return [PushSubscription.from_dict(row) for row in rows]
    
    def deactivate_subscription(self, subscription_id: str) -> bool:
        """Deactivate a push subscription."""
        try:
            self.db.execute(
                "UPDATE push_subscriptions SET is_active = 0 WHERE id = ?",
                (subscription_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to deactivate subscription: {e}")
            return False
    
    # ==========================================
    # Preferences Operations
    # ==========================================
    
    def get_preferences(self, user_id: str = "default") -> NotificationPreferences:
        """Get notification preferences for a user."""
        row = self.db.fetch_one(
            "SELECT * FROM notification_preferences WHERE user_id = ?",
            (user_id,)
        )
        
        if row:
            return NotificationPreferences.from_dict(row)
        
        # Return default preferences
        return NotificationPreferences(user_id=user_id)
    
    def save_preferences(self, preferences: NotificationPreferences) -> bool:
        """Save notification preferences."""
        try:
            data = preferences.to_dict()
            
            self.db.execute(
                """INSERT OR REPLACE INTO notification_preferences 
                   (user_id, enabled, quiet_hours_start, quiet_hours_end,
                    default_sound, vibration_enabled, habit_reminders_enabled,
                    task_reminders_enabled, goal_reminders_enabled,
                    achievement_notifications_enabled, streak_warnings_enabled,
                    daily_digest_enabled, browser_notifications_enabled,
                    email_notifications_enabled, email_address,
                    smart_scheduling_enabled, min_reminder_lead_minutes,
                    created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data['user_id'], data['enabled'], data['quiet_hours_start'],
                    data['quiet_hours_end'], data['default_sound'],
                    data['vibration_enabled'], data['habit_reminders_enabled'],
                    data['task_reminders_enabled'], data['goal_reminders_enabled'],
                    data['achievement_notifications_enabled'],
                    data['streak_warnings_enabled'], data['daily_digest_enabled'],
                    data['browser_notifications_enabled'],
                    data['email_notifications_enabled'], data['email_address'],
                    data['smart_scheduling_enabled'], data['min_reminder_lead_minutes'],
                    data['created_at'], data['updated_at']
                )
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
            return False
    
    # ==========================================
    # Completion History (for Smart Scheduling)
    # ==========================================
    
    def record_completion(
        self,
        entity_type: str,
        entity_id: str,
        completed_at: Optional[datetime] = None,
        scheduled_for: Optional[datetime] = None,
        reminder_sent: bool = False,
        snooze_count: int = 0,
        user_id: str = "default",
    ) -> CompletionHistory:
        """
        Record a completion for smart scheduling analysis.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            completed_at: When completed (default: now)
            scheduled_for: When it was scheduled
            reminder_sent: Whether a reminder was sent
            snooze_count: Number of snoozes
            user_id: User ID
            
        Returns:
            CompletionHistory record
        """
        completed_at = completed_at or datetime.now()
        
        history = CompletionHistory(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            completed_at=completed_at,
            scheduled_for=scheduled_for,
            reminder_sent=reminder_sent,
            snooze_count=snooze_count,
        )
        
        data = history.to_dict()
        self.db.execute(
            """INSERT INTO completion_history 
               (id, user_id, entity_type, entity_id, completed_at,
                scheduled_for, variance_seconds, reminder_sent, 
                snooze_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data['id'], data['user_id'], data['entity_type'],
                data['entity_id'], data['completed_at'], data['scheduled_for'],
                data['variance_seconds'], data['reminder_sent'],
                data['snooze_count'], data['created_at']
            )
        )
        
        return history
    
    def get_completion_history(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 30
    ) -> List[CompletionHistory]:
        """Get completion history for an entity."""
        rows = self.db.fetch_all(
            """SELECT * FROM completion_history 
               WHERE entity_type = ? AND entity_id = ?
               ORDER BY completed_at DESC LIMIT ?""",
            (entity_type, entity_id, limit)
        )
        
        return [CompletionHistory.from_dict(row) for row in rows]
    
    # ==========================================
    # Analytics
    # ==========================================
    
    def get_notification_stats(self, user_id: str = "default") -> Dict[str, Any]:
        """Get notification statistics."""
        # Count by status
        status_counts = self.db.fetch_all(
            """SELECT status, COUNT(*) as count 
               FROM notifications GROUP BY status"""
        )
        
        # Count by type
        type_counts = self.db.fetch_all(
            """SELECT type, COUNT(*) as count 
               FROM notifications GROUP BY type"""
        )
        
        # Delivery success rate
        delivery_stats = self.db.fetch_all(
            """SELECT channel, 
                   SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
               FROM notification_logs GROUP BY channel"""
        )
        
        return {
            'by_status': {row['status']: row['count'] for row in status_counts},
            'by_type': {row['type']: row['count'] for row in type_counts},
            'delivery': {
                row['channel']: {
                    'sent': row['sent'],
                    'failed': row['failed'],
                    'success_rate': row['sent'] / (row['sent'] + row['failed']) 
                        if (row['sent'] + row['failed']) > 0 else 0
                }
                for row in delivery_stats
            }
        }


# Singleton instance
_engine: Optional[NotificationEngine] = None


def get_engine() -> NotificationEngine:
    """Get the global notification engine instance."""
    global _engine
    if _engine is None:
        _engine = NotificationEngine()
    return _engine