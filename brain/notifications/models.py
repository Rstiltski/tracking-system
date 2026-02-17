"""
Notification Models

Data models for the notification system using Python dataclasses.
Follows PROJECT_RULES.md patterns for data modeling.

Reference:
- Phase 4.1 Research Document, Section 4: Data Model
- PROJECT_RULES.md: Use dataclasses for models
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid
import json


class NotificationType(Enum):
    """Types of notifications in the system."""
    HABIT_REMINDER = "habit_reminder"
    TASK_DUE = "task_due"
    GOAL_DEADLINE = "goal_deadline"
    STREAK_WARNING = "streak_warning"
    ACHIEVEMENT = "achievement"
    SYSTEM = "system"
    REWARD = "reward"
    DAILY_DIGEST = "daily_digest"


class NotificationPriority(Enum):
    """Priority levels for notifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    
    @property
    def level(self) -> int:
        """Get numeric priority level (higher = more important)."""
        levels = {
            NotificationPriority.LOW: 1,
            NotificationPriority.MEDIUM: 2,
            NotificationPriority.HIGH: 3,
            NotificationPriority.URGENT: 4,
        }
        return levels[self]


class NotificationStatus(Enum):
    """Status of a notification."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"
    CLICKED = "clicked"


class NotificationChannel(Enum):
    """Available notification delivery channels."""
    WEB_PUSH = "web_push"
    EMAIL = "email"
    IN_APP = "in_app"
    DESKTOP = "desktop"


@dataclass
class Notification:
    """
    A notification to be sent to the user.
    
    Represents a single notification with all its metadata,
    scheduling information, and delivery status.
    
    Example:
        notification = Notification(
            type=NotificationType.HABIT_REMINDER,
            title="Time to hydrate!",
            message="Don't forget to drink water",
            entity_type="habit",
            entity_id="habit-123"
        )
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: NotificationType = NotificationType.SYSTEM
    title: str = ""
    message: str = ""
    priority: NotificationPriority = NotificationPriority.MEDIUM
    status: NotificationStatus = NotificationStatus.PENDING
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read: bool = False
    entity_type: Optional[str] = None  # 'habit', 'task', 'goal'
    entity_id: Optional[str] = None
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'type': self.type.value,
            'title': self.title,
            'message': self.message,
            'priority': self.priority.value,
            'status': self.status.value,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'read': self.read,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action_url': self.action_url,
            'metadata': json.dumps(self.metadata) if self.metadata else '{}',
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """Create instance from dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            type=NotificationType(data.get('type', 'system')),
            title=data.get('title', ''),
            message=data.get('message', ''),
            priority=NotificationPriority(data.get('priority', 'medium')),
            status=NotificationStatus(data.get('status', 'pending')),
            scheduled_for=datetime.fromisoformat(data['scheduled_for']) if data.get('scheduled_for') else None,
            sent_at=datetime.fromisoformat(data['sent_at']) if data.get('sent_at') else None,
            delivered_at=datetime.fromisoformat(data['delivered_at']) if data.get('delivered_at') else None,
            read=bool(data.get('read', 0)),
            entity_type=data.get('entity_type'),
            entity_id=data.get('entity_id'),
            action_url=data.get('action_url'),
            metadata=json.loads(data.get('metadata', '{}')),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
        )
    
    def mark_sent(self) -> None:
        """Mark notification as sent."""
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.now()
        self.updated_at = datetime.now()
    
    def mark_delivered(self) -> None:
        """Mark notification as delivered."""
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = datetime.now()
        self.updated_at = datetime.now()
    
    def mark_failed(self) -> None:
        """Mark notification as failed."""
        self.status = NotificationStatus.FAILED
        self.updated_at = datetime.now()
    
    def mark_read(self) -> None:
        """Mark notification as read."""
        self.read = True
        self.updated_at = datetime.now()


@dataclass
class ReminderSchedule:
    """
    Schedule for recurring reminders.
    
    Defines when and how often a reminder should be sent
    for a specific entity (habit, task, goal).
    
    Example:
        schedule = ReminderSchedule(
            entity_type="habit",
            entity_id="habit-123",
            reminder_time=time(8, 0),  # 8:00 AM
            days_of_week=[0, 1, 2, 3, 4]  # Weekdays
        )
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    entity_type: str = ""  # 'habit', 'task', 'goal'
    entity_id: str = ""
    reminder_time: Optional[time] = None
    days_of_week: List[int] = field(default_factory=list)  # 0=Monday, 6=Sunday
    enabled: bool = True
    snooze_minutes: int = 5
    max_snoozes: int = 3
    current_snoozes: int = 0
    is_smart: bool = False  # Enable adaptive scheduling
    smart_time: Optional[time] = None  # Calculated optimal time
    channels: List[NotificationChannel] = field(default_factory=lambda: [NotificationChannel.IN_APP])
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'reminder_time': self.reminder_time.strftime('%H:%M') if self.reminder_time else None,
            'days_of_week': json.dumps(self.days_of_week),
            'enabled': self.enabled,
            'snooze_minutes': self.snooze_minutes,
            'max_snoozes': self.max_snoozes,
            'current_snoozes': self.current_snoozes,
            'is_smart': self.is_smart,
            'smart_time': self.smart_time.strftime('%H:%M') if self.smart_time else None,
            'channels': json.dumps([c.value for c in self.channels]),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReminderSchedule':
        """Create instance from dictionary."""
        channels_data = json.loads(data.get('channels', '["in_app"]'))
        channels = [NotificationChannel(c) for c in channels_data]
        
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            entity_type=data.get('entity_type', ''),
            entity_id=data.get('entity_id', ''),
            reminder_time=time.fromisoformat(data['reminder_time']) if data.get('reminder_time') else None,
            days_of_week=json.loads(data.get('days_of_week', '[]')),
            enabled=bool(data.get('enabled', 1)),
            snooze_minutes=data.get('snooze_minutes', 5),
            max_snoozes=data.get('max_snoozes', 3),
            current_snoozes=data.get('current_snoozes', 0),
            is_smart=bool(data.get('is_smart', 0)),
            smart_time=time.fromisoformat(data['smart_time']) if data.get('smart_time') else None,
            channels=channels,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
        )
    
    def should_trigger_today(self, check_date: Optional[date] = None) -> bool:
        """Check if reminder should trigger on a specific date."""
        if not self.enabled:
            return False
        
        check_date = check_date or date.today()
        weekday = check_date.weekday()  # 0=Monday, 6=Sunday
        
        # If no days specified, trigger every day
        if not self.days_of_week:
            return True
        
        return weekday in self.days_of_week
    
    def get_effective_time(self) -> Optional[time]:
        """Get the effective reminder time (smart or fixed)."""
        if self.is_smart and self.smart_time:
            return self.smart_time
        return self.reminder_time
    
    def can_snooze(self) -> bool:
        """Check if reminder can be snoozed."""
        return self.current_snoozes < self.max_snoozes
    
    def snooze(self) -> Optional[time]:
        """Snooze the reminder and return new time."""
        if not self.can_snooze():
            return None
        
        self.current_snoozes += 1
        self.updated_at = datetime.now()
        
        # Calculate new time
        current = self.get_effective_time()
        if current:
            from datetime import timedelta
            new_datetime = datetime.combine(date.today(), current) + timedelta(minutes=self.snooze_minutes)
            return new_datetime.time()
        return None
    
    def reset_snoozes(self) -> None:
        """Reset snooze counter (call after reminder is handled)."""
        self.current_snoozes = 0
        self.updated_at = datetime.now()


@dataclass
class PushSubscription:
    """
    Web Push subscription data.
    
    Stores the endpoint and keys needed to send push notifications
    to a specific browser/device.
    
    Reference:
    - Web Push API specification
    - Phase 4.1 Research Document, Section 4.2.2
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    endpoint: str = ""  # Unique URL from push service
    p256dh: str = ""    # Public encryption key (Base64)
    auth: str = ""      # Authentication secret (Base64)
    user_agent: str = ""  # Browser/OS metadata
    device_name: str = ""  # User-friendly device name
    last_active: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'endpoint': self.endpoint,
            'p256dh': self.p256dh,
            'auth': self.auth,
            'user_agent': self.user_agent,
            'device_name': self.device_name,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PushSubscription':
        """Create instance from dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            endpoint=data.get('endpoint', ''),
            p256dh=data.get('p256dh', ''),
            auth=data.get('auth', ''),
            user_agent=data.get('user_agent', ''),
            device_name=data.get('device_name', ''),
            last_active=datetime.fromisoformat(data['last_active']) if data.get('last_active') else None,
            is_active=bool(data.get('is_active', 1)),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
        )
    
    def to_subscription_info(self) -> Dict[str, Any]:
        """
        Convert to format expected by pywebpush.
        
        Returns:
            Dictionary with endpoint and keys for Web Push API.
        """
        return {
            "endpoint": self.endpoint,
            "keys": {
                "p256dh": self.p256dh,
                "auth": self.auth
            }
        }
    
    def mark_active(self) -> None:
        """Mark subscription as recently active."""
        self.last_active = datetime.now()
        self.is_active = True


@dataclass
class NotificationLog:
    """
    Log entry for notification delivery attempts.
    
    Tracks the success/failure of notification delivery
    for debugging and analytics.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    notification_id: str = ""
    channel: NotificationChannel = NotificationChannel.IN_APP
    status: str = "pending"  # 'sent', 'failed', 'delivered', 'clicked'
    error_message: Optional[str] = None
    response_code: Optional[int] = None  # HTTP status code for Web Push
    dispatched_at: datetime = field(default_factory=datetime.now)
    delivered_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'notification_id': self.notification_id,
            'channel': self.channel.value,
            'status': self.status,
            'error_message': self.error_message,
            'response_code': self.response_code,
            'dispatched_at': self.dispatched_at.isoformat(),
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificationLog':
        """Create instance from dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            notification_id=data.get('notification_id', ''),
            channel=NotificationChannel(data.get('channel', 'in_app')),
            status=data.get('status', 'pending'),
            error_message=data.get('error_message'),
            response_code=data.get('response_code'),
            dispatched_at=datetime.fromisoformat(data['dispatched_at']) if data.get('dispatched_at') else datetime.now(),
            delivered_at=datetime.fromisoformat(data['delivered_at']) if data.get('delivered_at') else None,
            clicked_at=datetime.fromisoformat(data['clicked_at']) if data.get('clicked_at') else None,
        )


@dataclass
class CompletionHistory:
    """
    Record of when a task/habit was completed vs when it was scheduled.
    
    Used for smart scheduling algorithm to calculate optimal reminder times.
    
    Reference:
    - Phase 4.1 Research Document, Section 6.1: Adaptive Scheduling
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    entity_type: str = ""  # 'habit', 'task', 'goal'
    entity_id: str = ""
    completed_at: datetime = field(default_factory=datetime.now)
    scheduled_for: Optional[datetime] = None
    variance_seconds: Optional[int] = None  # Delta from scheduled time
    reminder_sent: bool = False
    snooze_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate variance if not set."""
        if self.scheduled_for and self.variance_seconds is None:
            delta = self.completed_at - self.scheduled_for
            self.variance_seconds = int(delta.total_seconds())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'completed_at': self.completed_at.isoformat(),
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'variance_seconds': self.variance_seconds,
            'reminder_sent': self.reminder_sent,
            'snooze_count': self.snooze_count,
            'created_at': self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompletionHistory':
        """Create instance from dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            entity_type=data.get('entity_type', ''),
            entity_id=data.get('entity_id', ''),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else datetime.now(),
            scheduled_for=datetime.fromisoformat(data['scheduled_for']) if data.get('scheduled_for') else None,
            variance_seconds=data.get('variance_seconds'),
            reminder_sent=bool(data.get('reminder_sent', 0)),
            snooze_count=data.get('snooze_count', 0),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
        )


@dataclass
class NotificationPreferences:
    """
    User preferences for notifications.
    
    Controls global notification settings, quiet hours,
    and per-type notification preferences.
    """
    user_id: str = ""
    enabled: bool = True
    quiet_hours_start: Optional[time] = None  # e.g., 22:00
    quiet_hours_end: Optional[time] = None    # e.g., 07:00
    default_sound: str = "default"
    vibration_enabled: bool = True
    
    # Per-type settings
    habit_reminders_enabled: bool = True
    task_reminders_enabled: bool = True
    goal_reminders_enabled: bool = True
    achievement_notifications_enabled: bool = True
    streak_warnings_enabled: bool = True
    daily_digest_enabled: bool = False
    
    # Channel preferences
    browser_notifications_enabled: bool = True
    email_notifications_enabled: bool = False
    email_address: Optional[str] = None
    
    # Smart scheduling
    smart_scheduling_enabled: bool = True
    min_reminder_lead_minutes: int = 15  # Minutes before scheduled time
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'user_id': self.user_id,
            'enabled': self.enabled,
            'quiet_hours_start': self.quiet_hours_start.strftime('%H:%M') if self.quiet_hours_start else None,
            'quiet_hours_end': self.quiet_hours_end.strftime('%H:%M') if self.quiet_hours_end else None,
            'default_sound': self.default_sound,
            'vibration_enabled': self.vibration_enabled,
            'habit_reminders_enabled': self.habit_reminders_enabled,
            'task_reminders_enabled': self.task_reminders_enabled,
            'goal_reminders_enabled': self.goal_reminders_enabled,
            'achievement_notifications_enabled': self.achievement_notifications_enabled,
            'streak_warnings_enabled': self.streak_warnings_enabled,
            'daily_digest_enabled': self.daily_digest_enabled,
            'browser_notifications_enabled': self.browser_notifications_enabled,
            'email_notifications_enabled': self.email_notifications_enabled,
            'email_address': self.email_address,
            'smart_scheduling_enabled': self.smart_scheduling_enabled,
            'min_reminder_lead_minutes': self.min_reminder_lead_minutes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificationPreferences':
        """Create instance from dictionary."""
        return cls(
            user_id=data.get('user_id', ''),
            enabled=bool(data.get('enabled', 1)),
            quiet_hours_start=time.fromisoformat(data['quiet_hours_start']) if data.get('quiet_hours_start') else None,
            quiet_hours_end=time.fromisoformat(data['quiet_hours_end']) if data.get('quiet_hours_end') else None,
            default_sound=data.get('default_sound', 'default'),
            vibration_enabled=bool(data.get('vibration_enabled', 1)),
            habit_reminders_enabled=bool(data.get('habit_reminders_enabled', 1)),
            task_reminders_enabled=bool(data.get('task_reminders_enabled', 1)),
            goal_reminders_enabled=bool(data.get('goal_reminders_enabled', 1)),
            achievement_notifications_enabled=bool(data.get('achievement_notifications_enabled', 1)),
            streak_warnings_enabled=bool(data.get('streak_warnings_enabled', 1)),
            daily_digest_enabled=bool(data.get('daily_digest_enabled', 0)),
            browser_notifications_enabled=bool(data.get('browser_notifications_enabled', 1)),
            email_notifications_enabled=bool(data.get('email_notifications_enabled', 0)),
            email_address=data.get('email_address'),
            smart_scheduling_enabled=bool(data.get('smart_scheduling_enabled', 1)),
            min_reminder_lead_minutes=data.get('min_reminder_lead_minutes', 15),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
        )
    
    def is_quiet_hours(self, check_time: Optional[time] = None) -> bool:
        """
        Check if current time is within quiet hours.
        
        Args:
            check_time: Time to check (defaults to current time)
            
        Returns:
            True if within quiet hours, False otherwise
        """
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        check_time = check_time or datetime.now().time()
        
        # Handle overnight quiet hours (e.g., 22:00 - 07:00)
        if self.quiet_hours_start > self.quiet_hours_end:
            # Quiet hours span midnight
            return check_time >= self.quiet_hours_start or check_time <= self.quiet_hours_end
        else:
            # Quiet hours within same day
            return self.quiet_hours_start <= check_time <= self.quiet_hours_end
    
    def is_type_enabled(self, notification_type: NotificationType) -> bool:
        """Check if a specific notification type is enabled."""
        type_mapping = {
            NotificationType.HABIT_REMINDER: self.habit_reminders_enabled,
            NotificationType.TASK_DUE: self.task_reminders_enabled,
            NotificationType.GOAL_DEADLINE: self.goal_reminders_enabled,
            NotificationType.ACHIEVEMENT: self.achievement_notifications_enabled,
            NotificationType.STREAK_WARNING: self.streak_warnings_enabled,
            NotificationType.DAILY_DIGEST: self.daily_digest_enabled,
            NotificationType.REWARD: self.achievement_notifications_enabled,
            NotificationType.SYSTEM: True,  # System notifications always enabled
        }
        return type_mapping.get(notification_type, True)


# VAPID Configuration for Web Push
@dataclass
class VAPIDConfig:
    """
    VAPID (Voluntary Application Server Identification) configuration.
    
    Required for Web Push API authentication.
    Generated once and stored securely.
    """
    subject: str = ""  # mailto: email or URL
    public_key: str = ""
    private_key: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'subject': self.subject,
            'public_key': self.public_key,
            'private_key': self.private_key,
            'created_at': self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VAPIDConfig':
        """Create instance from dictionary."""
        return cls(
            subject=data.get('subject', ''),
            public_key=data.get('public_key', ''),
            private_key=data.get('private_key', ''),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
        )