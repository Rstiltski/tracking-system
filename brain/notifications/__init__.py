"""
Brain Notifications Module

Implements a comprehensive notification and reminder system for the tracking application.
Based on Phase 4.1 of the roadmap.

Key Components:
- NotificationEngine: Core engine for creating and dispatching notifications
- ReminderScheduler: APScheduler-based temporal orchestration
- Notification Channels: Web Push and Email delivery strategies
- Smart Scheduling: Adaptive timing based on user behavior patterns

Architecture:
    Presentation Layer (Streamlit UI)
              │
              ▼
    Logic Layer (NotificationEngine + ReminderScheduler)
              │
              ▼
    Persistence Layer (SQLite with WAL mode)

Reference:
- Phase 4.1 Research Document (Python Notification Engine Repo Search.docx)
- phases/PHASE_4_NOTIFICATIONS.md
"""

from brain.notifications.models import (
    Notification,
    NotificationType,
    NotificationPriority,
    NotificationStatus,
    NotificationChannel,
    ReminderSchedule,
    PushSubscription,
    NotificationLog,
    CompletionHistory,
    NotificationPreferences,
    VAPIDConfig,
)
from brain.notifications.engine import NotificationEngine, get_engine
from brain.notifications.scheduler import ReminderScheduler, get_scheduler, SmartScheduler
from brain.notifications.channels import (
    NotificationChannelBase,
    WebPushChannel,
    EmailChannel,
    InAppChannel,
    DesktopChannel,
    ChannelResult,
    get_channel,
)
from brain.notifications.templates import (
    NotificationTemplates,
    NotificationTemplate,
    render_notification,
    get_habit_reminder_context,
    get_task_reminder_context,
    get_achievement_context,
    get_reward_context,
)

__all__ = [
    # Models
    "Notification",
    "NotificationType",
    "NotificationPriority",
    "NotificationStatus",
    "NotificationChannel",
    "ReminderSchedule",
    "PushSubscription",
    "NotificationLog",
    "CompletionHistory",
    "NotificationPreferences",
    "VAPIDConfig",
    # Engine
    "NotificationEngine",
    "get_engine",
    # Scheduler
    "ReminderScheduler",
    "get_scheduler",
    "SmartScheduler",
    # Channels
    "NotificationChannelBase",
    "WebPushChannel",
    "EmailChannel",
    "InAppChannel",
    "DesktopChannel",
    "ChannelResult",
    "get_channel",
    # Templates
    "NotificationTemplates",
    "NotificationTemplate",
    "render_notification",
    "get_habit_reminder_context",
    "get_task_reminder_context",
    "get_achievement_context",
    "get_reward_context",
]
