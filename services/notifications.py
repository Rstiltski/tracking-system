"""
Notifications Service

Provides notification functionality for the tracking system.
"""

import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    HABIT_REMINDER = "habit_reminder"
    TASK_REMINDER = "task_reminder"
    GOAL_REMINDER = "goal_reminder"


@dataclass
class Notification:
    """Represents a notification."""
    title: str
    message: str
    notification_type: NotificationType = NotificationType.INFO
    sound: Optional[str] = None
    urgent: bool = False


class Notifications:
    """
    Notifications service for the tracking system.
    
    Handles desktop notifications, in-app toasts, and reminder scheduling.
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize the notifications service.
        
        Args:
            enabled: Whether notifications are enabled
        """
        self.enabled = enabled
        self._settings: Dict[str, Any] = {
            'desktop_enabled': True,
            'sound': 'default',
            'style': 'standard',
            'habit_reminders': True,
            'task_reminders': True,
            'goal_reminders': True,
        }
        self._handlers: Dict[NotificationType, list] = {}
    
    def send(self, notification: Notification) -> bool:
        """
        Send a notification.
        
        Args:
            notification: The notification to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Notifications disabled, skipping: %s", notification.title)
            return False
        
        # Check if this type of notification is enabled
        if notification.notification_type in (
            NotificationType.HABIT_REMINDER,
            NotificationType.TASK_REMINDER,
            NotificationType.GOAL_REMINDER
        ):
            setting_key = f"{notification.notification_type.value}_enabled"
            if not self._settings.get(setting_key, True):
                return False
        
        # Try to send desktop notification if enabled
        if self._settings.get('desktop_enabled', True):
            try:
                self._send_desktop_notification(notification)
            except Exception as e:
                logger.error("Failed to send desktop notification: %s", e)
        
        # Trigger registered handlers
        handlers = self._handlers.get(notification.notification_type, [])
        for handler in handlers:
            try:
                handler(notification)
            except Exception as e:
                logger.error("Notification handler failed: %s", e)
        
        logger.info("Notification sent: %s", notification.title)
        return True
    
    def _send_desktop_notification(self, notification: Notification) -> None:
        """
        Send a desktop notification using the system's notification API.
        
        Args:
            notification: The notification to send
        """
        # Try using the notify2 library if available
        try:
            import notify2
            notify2.init("Veryfyn")
            n = notify2.Notification(
                notification.title,
                notification.message,
                icon="dialog-information"
            )
            n.show()
            return
        except ImportError:
            pass
        except Exception:
            pass
        
        # Fallback: try using subprocess with notify-send (Linux)
        try:
            import subprocess
            subprocess.run(
                ["notify-send", notification.title, notification.message],
                capture_output=True,
                timeout=5
            )
            return
        except Exception:
            pass
        
        # Last resort: log the notification
        logger.info("Desktop notification: %s - %s", notification.title, notification.message)
    
    def show_toast(self, title: str, message: str, 
                   notification_type: NotificationType = NotificationType.INFO) -> None:
        """
        Show an in-app toast notification.
        
        This is a placeholder - the actual implementation would trigger
        a UI event to display the toast.
        
        Args:
            title: Toast title
            message: Toast message
            notification_type: Type of notification
        """
        notification = Notification(
            title=title,
            message=message,
            notification_type=notification_type
        )
        self.send(notification)
    
    def send_habit_reminder(self, habit_name: str) -> bool:
        """
        Send a habit reminder notification.
        
        Args:
            habit_name: Name of the habit to remind about
            
        Returns:
            True if sent successfully
        """
        notification = Notification(
            title="Habit Reminder",
            message=f"Don't forget to complete: {habit_name}",
            notification_type=NotificationType.HABIT_REMINDER
        )
        return self.send(notification)
    
    def send_task_reminder(self, task_title: str, due_date: Optional[str] = None) -> bool:
        """
        Send a task reminder notification.
        
        Args:
            task_title: Title of the task
            due_date: Optional due date string
            
        Returns:
            True if sent successfully
        """
        message = f"Task due: {task_title}"
        if due_date:
            message += f" (Due: {due_date})"
        
        notification = Notification(
            title="Task Reminder",
            message=message,
            notification_type=NotificationType.TASK_REMINDER
        )
        return self.send(notification)
    
    def send_goal_reminder(self, goal_title: str, progress: float = 0.0) -> bool:
        """
        Send a goal reminder notification.
        
        Args:
            goal_title: Title of the goal
            progress: Current progress percentage
            
        Returns:
            True if sent successfully
        """
        notification = Notification(
            title="Goal Progress",
            message=f"{goal_title}: {progress:.1f}% complete",
            notification_type=NotificationType.GOAL_REMINDER
        )
        return self.send(notification)
    
    def register_handler(self, notification_type: NotificationType, 
                        handler: Callable[[Notification], None]) -> None:
        """
        Register a handler for a specific notification type.
        
        Args:
            notification_type: Type of notifications to handle
            handler: Callback function to invoke
        """
        if notification_type not in self._handlers:
            self._handlers[notification_type] = []
        self._handlers[notification_type].append(handler)
    
    def update_settings(self, settings: Dict[str, Any]) -> None:
        """
        Update notification settings.
        
        Args:
            settings: Dictionary of setting key-value pairs
        """
        self._settings.update(settings)
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current notification settings."""
        return self._settings.copy()


# Default notifications instance
notifications = Notifications(enabled=True)
