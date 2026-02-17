"""
Task Alert Manager

Implements deadline-aware notifications with progressive urgency.
Handles task deadline alerts, overdue escalation, and daily digests.

Phase 4.3 Feature: Progressive Urgency Algorithm
- 24 hours before: LOW priority (Email digest)
- 4 hours before: MEDIUM priority (Web Push)
- 1 hour before: HIGH priority (Priority Push)
- Overdue: CRITICAL priority (Email + Push)

Reference:
- Phase 4.3 Research Document: Deadline Management
- InTime Widget: Progressive urgency visual rendering
"""

from datetime import datetime, timedelta, date, time
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import threading

from brain.notifications.models import (
    Notification,
    NotificationType,
    NotificationPriority,
    NotificationStatus,
    NotificationChannel,
)
from brain.notifications.engine import NotificationEngine, get_engine

logger = logging.getLogger(__name__)


# ==========================================
# Urgency Levels for Task Alerts
# ==========================================

class TaskUrgency(str, Enum):
    """Urgency levels for task deadline alerts."""
    LOW = "low"           # > 24 hours remaining
    MEDIUM = "medium"     # 4-24 hours remaining
    HIGH = "high"         # 1-4 hours remaining
    CRITICAL = "critical" # < 1 hour or overdue


class TaskStatus(str, Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


# ==========================================
# Data Classes
# ==========================================

@dataclass
class TaskAlert:
    """
    Represents an alert for a task deadline.
    
    Tracks the task details and alert configuration
    for progressive urgency notifications.
    """
    id: str
    task_id: str
    title: str
    due_date: datetime
    status: TaskStatus = TaskStatus.PENDING
    urgency_level: TaskUrgency = TaskUrgency.LOW
    reminder_config: Dict[str, str] = field(default_factory=lambda: {
        "24h": "email",    # 24 hours before - email
        "4h": "push",      # 4 hours before - push
        "1h": "push_high", # 1 hour before - high priority push
        "overdue": "both"  # Overdue - email + push
    })
    alerts_sent: List[str] = field(default_factory=list)  # List of alert types sent
    snoozed_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'title': self.title,
            'due_date': self.due_date.isoformat(),
            'status': self.status.value,
            'urgency_level': self.urgency_level.value,
            'reminder_config': self.reminder_config,
            'alerts_sent': self.alerts_sent,
            'snoozed_until': self.snoozed_until.isoformat() if self.snoozed_until else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskAlert':
        """Create instance from dictionary."""
        return cls(
            id=data.get('id', ''),
            task_id=data.get('task_id', ''),
            title=data.get('title', ''),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else datetime.now(),
            status=TaskStatus(data.get('status', 'pending')),
            urgency_level=TaskUrgency(data.get('urgency_level', 'low')),
            reminder_config=data.get('reminder_config', {}),
            alerts_sent=data.get('alerts_sent', []),
            snoozed_until=datetime.fromisoformat(data['snoozed_until']) if data.get('snoozed_until') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
        )
    
    def calculate_urgency(self) -> TaskUrgency:
        """Calculate current urgency based on time remaining."""
        now = datetime.now()
        
        if self.status == TaskStatus.COMPLETED or self.status == TaskStatus.CANCELLED:
            return TaskUrgency.LOW
        
        if now > self.due_date:
            return TaskUrgency.CRITICAL
        
        time_remaining = self.due_date - now
        hours_remaining = time_remaining.total_seconds() / 3600
        
        if hours_remaining <= 1:
            return TaskUrgency.CRITICAL
        elif hours_remaining <= 4:
            return TaskUrgency.HIGH
        elif hours_remaining <= 24:
            return TaskUrgency.MEDIUM
        else:
            return TaskUrgency.LOW
    
    def get_time_remaining(self) -> timedelta:
        """Get time remaining until deadline."""
        return self.due_date - datetime.now()
    
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        return datetime.now() > self.due_date and self.status != TaskStatus.COMPLETED


@dataclass
class DailyDigest:
    """
    Daily digest of tasks and reminders.
    
    Aggregates low-urgency items into a single morning briefing
    to prevent notification spam.
    """
    id: str
    user_id: str
    digest_date: date
    tasks_due: List[Dict[str, Any]] = field(default_factory=list)
    tasks_overdue: List[Dict[str, Any]] = field(default_factory=list)
    habits_pending: List[Dict[str, Any]] = field(default_factory=list)
    goals_progress: List[Dict[str, Any]] = field(default_factory=list)
    sent_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'digest_date': self.digest_date.isoformat(),
            'tasks_due': self.tasks_due,
            'tasks_overdue': self.tasks_overdue,
            'habits_pending': self.habits_pending,
            'goals_progress': self.goals_progress,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DailyDigest':
        """Create instance from dictionary."""
        return cls(
            id=data.get('id', ''),
            user_id=data.get('user_id', ''),
            digest_date=date.fromisoformat(data['digest_date']) if data.get('digest_date') else date.today(),
            tasks_due=data.get('tasks_due', []),
            tasks_overdue=data.get('tasks_overdue', []),
            habits_pending=data.get('habits_pending', []),
            goals_progress=data.get('goals_progress', []),
            sent_at=datetime.fromisoformat(data['sent_at']) if data.get('sent_at') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
        )
    
    def has_content(self) -> bool:
        """Check if digest has any content."""
        return bool(self.tasks_due or self.tasks_overdue or self.habits_pending or self.goals_progress)
    
    def generate_summary(self) -> str:
        """Generate a text summary of the digest."""
        parts = []
        
        if self.tasks_due:
            parts.append(f"📋 {len(self.tasks_due)} task(s) due today")
        
        if self.tasks_overdue:
            parts.append(f"⚠️ {len(self.tasks_overdue)} overdue task(s)")
        
        if self.habits_pending:
            parts.append(f"✅ {len(self.habits_pending)} habit(s) to complete")
        
        if self.goals_progress:
            parts.append(f"🎯 {len(self.goals_progress)} goal(s) in progress")
        
        if not parts:
            return "Good morning! You have no pending items for today."
        
        return "Good morning! Here's your daily briefing:\n\n" + "\n".join(f"• {p}" for p in parts)


# ==========================================
# Task Alert Manager
# ==========================================

class TaskAlertManager:
    """
    Manages task deadline alerts with progressive urgency.
    
    Phase 4.3 Feature: Cascade Scheduling
    
    When a Task is created, the manager schedules a cascade of jobs:
    - 24-hour warning (LOW urgency)
    - 4-hour warning (MEDIUM urgency)
    - 1-hour warning (HIGH urgency)
    - Overdue alert (CRITICAL urgency)
    
    Reference:
    - Phase 4.3 Research Document, Section 6: Deadline Management
    """
    
    # Urgency thresholds (hours)
    LOW_THRESHOLD = 24.0
    MEDIUM_THRESHOLD = 4.0
    HIGH_THRESHOLD = 1.0
    
    # Default digest time
    DIGEST_HOUR = 7  # 7 AM
    
    def __init__(self, db=None, engine: Optional[NotificationEngine] = None):
        """
        Initialize task alert manager.
        
        Args:
            db: Database instance
            engine: Notification engine for dispatch
        """
        self._db = db
        self._engine = engine
        self._scheduler = None
    
    @property
    def db(self):
        """Get database instance."""
        if self._db is None:
            from tracking_app.database import get_db
            self._db = get_db()
        return self._db
    
    @property
    def engine(self) -> NotificationEngine:
        """Get notification engine."""
        if self._engine is None:
            self._engine = get_engine()
        return self._engine
    
    # ==========================================
    # Task Alert Scheduling
    # ==========================================
    
    def schedule_task_alerts(self, task: TaskAlert) -> bool:
        """
        Schedule cascade of alerts for a task.
        
        Creates multiple scheduled jobs based on the task's
        due date and reminder configuration.
        
        Args:
            task: TaskAlert to schedule
            
        Returns:
            True if scheduling successful
        """
        now = datetime.now()
        
        # Schedule 24-hour warning
        t_minus_24 = task.due_date - timedelta(hours=24)
        if t_minus_24 > now:
            self._schedule_alert(task, "24h", t_minus_24, TaskUrgency.LOW)
        
        # Schedule 4-hour warning
        t_minus_4 = task.due_date - timedelta(hours=4)
        if t_minus_4 > now:
            self._schedule_alert(task, "4h", t_minus_4, TaskUrgency.MEDIUM)
        
        # Schedule 1-hour warning
        t_minus_1 = task.due_date - timedelta(hours=1)
        if t_minus_1 > now:
            self._schedule_alert(task, "1h", t_minus_1, TaskUrgency.HIGH)
        
        # Schedule overdue alert (1 hour after deadline)
        t_overdue = task.due_date + timedelta(hours=1)
        self._schedule_alert(task, "overdue", t_overdue, TaskUrgency.CRITICAL)
        
        # Store task alert
        self._store_task_alert(task)
        
        logger.info(f"Scheduled alerts for task {task.task_id}: {task.title}")
        return True
    
    def _schedule_alert(
        self,
        task: TaskAlert,
        alert_type: str,
        trigger_time: datetime,
        urgency: TaskUrgency
    ) -> None:
        """
        Schedule a single alert.
        
        Args:
            task: TaskAlert instance
            alert_type: Type of alert (24h, 4h, 1h, overdue)
            trigger_time: When to trigger the alert
            urgency: Urgency level for the alert
        """
        # Store scheduled alert in database
        self.db.execute(
            """INSERT INTO scheduled_task_alerts 
               (id, task_id, alert_type, trigger_time, urgency, status, created_at)
               VALUES (?, ?, ?, ?, ?, 'pending', ?)""",
            (
                f"alert_{task.task_id}_{alert_type}",
                task.task_id,
                alert_type,
                trigger_time.isoformat(),
                urgency.value,
                datetime.now().isoformat()
            )
        )
    
    def cancel_task_alerts(self, task_id: str) -> bool:
        """
        Cancel all pending alerts for a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            True if cancellation successful
        """
        self.db.execute(
            """UPDATE scheduled_task_alerts 
               SET status = 'cancelled', cancelled_at = ?
               WHERE task_id = ? AND status = 'pending'""",
            (datetime.now().isoformat(), task_id)
        )
        
        logger.info(f"Cancelled alerts for task {task_id}")
        return True
    
    def process_pending_alerts(self) -> int:
        """
        Process all pending alerts that are due.
        
        Called by the scheduler to send alerts.
        
        Returns:
            Number of alerts processed
        """
        now = datetime.now().isoformat()
        
        rows = self.db.fetch_all(
            """SELECT * FROM scheduled_task_alerts 
               WHERE status = 'pending' AND trigger_time <= ?""",
            (now,)
        )
        
        processed = 0
        for row in rows:
            try:
                self._send_alert(dict(row))
                self.db.execute(
                    """UPDATE scheduled_task_alerts 
                       SET status = 'sent', sent_at = ?
                       WHERE id = ?""",
                    (datetime.now().isoformat(), row['id'])
                )
                processed += 1
            except Exception as e:
                logger.error(f"Failed to send alert {row['id']}: {e}")
                self.db.execute(
                    """UPDATE scheduled_task_alerts 
                       SET status = 'failed', error = ?
                       WHERE id = ?""",
                    (str(e), row['id'])
                )
        
        return processed
    
    def _send_alert(self, alert_data: Dict[str, Any]) -> None:
        """
        Send a task alert notification.
        
        Args:
            alert_data: Alert data from database
        """
        task_id = alert_data['task_id']
        alert_type = alert_data['alert_type']
        urgency = TaskUrgency(alert_data['urgency'])
        
        # Get task details
        task = self._get_task_details(task_id)
        if not task:
            logger.warning(f"Task {task_id} not found for alert")
            return
        
        # Check if task is already completed
        if task.get('status') == 'completed':
            logger.debug(f"Task {task_id} already completed, skipping alert")
            return
        
        # Generate notification content
        title, message = self._generate_alert_content(task, alert_type, urgency)
        
        # Determine priority and channels
        priority = self._urgency_to_priority(urgency)
        channels = self._get_channels_for_urgency(urgency)
        
        # Create notification
        notification = Notification(
            type=NotificationType.TASK_DUE,
            title=title,
            message=message,
            priority=priority,
            entity_type="task",
            entity_id=task_id,
            metadata={
                'alert_type': alert_type,
                'urgency': urgency.value,
                'due_date': task.get('due_date'),
            }
        )
        
        # Dispatch notification
        self.engine.dispatch(notification, channels=channels)
        
        logger.info(f"Sent {alert_type} alert for task {task_id}")
    
    def _generate_alert_content(
        self,
        task: Dict[str, Any],
        alert_type: str,
        urgency: TaskUrgency
    ) -> Tuple[str, str]:
        """
        Generate notification title and message.
        
        Args:
            task: Task details
            alert_type: Type of alert
            urgency: Urgency level
            
        Returns:
            Tuple of (title, message)
        """
        title = task.get('title', 'Unknown Task')
        
        if alert_type == "24h":
            return (
                f"📋 Reminder: {title}",
                f"Heads up: '{title}' is due tomorrow."
            )
        elif alert_type == "4h":
            return (
                f"⏰ Don't forget: {title}",
                f"'{title}' is due in about 4 hours."
            )
        elif alert_type == "1h":
            return (
                f"🚨 Urgent: {title}",
                f"'{title}' is due in 1 hour! Don't forget to complete it."
            )
        elif alert_type == "overdue":
            return (
                f"⚠️ OVERDUE: {title}",
                f"'{title}' was due earlier and is now overdue. Please complete it as soon as possible."
            )
        
        return (f"Task Reminder: {title}", f"Don't forget to complete '{title}'.")
    
    def _urgency_to_priority(self, urgency: TaskUrgency) -> NotificationPriority:
        """Convert task urgency to notification priority."""
        mapping = {
            TaskUrgency.LOW: NotificationPriority.LOW,
            TaskUrgency.MEDIUM: NotificationPriority.MEDIUM,
            TaskUrgency.HIGH: NotificationPriority.HIGH,
            TaskUrgency.CRITICAL: NotificationPriority.URGENT,
        }
        return mapping.get(urgency, NotificationPriority.MEDIUM)
    
    def _get_channels_for_urgency(self, urgency: TaskUrgency) -> List[NotificationChannel]:
        """Get notification channels based on urgency."""
        if urgency == TaskUrgency.LOW:
            return [NotificationChannel.EMAIL]
        elif urgency == TaskUrgency.MEDIUM:
            return [NotificationChannel.WEB_PUSH]
        elif urgency == TaskUrgency.HIGH:
            return [NotificationChannel.WEB_PUSH, NotificationChannel.DESKTOP]
        else:  # CRITICAL
            return [NotificationChannel.EMAIL, NotificationChannel.WEB_PUSH, NotificationChannel.DESKTOP]
    
    # ==========================================
    # Daily Digest
    # ==========================================
    
    def generate_daily_digest(self, user_id: str = "default") -> Optional[DailyDigest]:
        """
        Generate a daily digest for a user.
        
        Aggregates all tasks due today, overdue tasks,
        and other pending items into a single briefing.
        
        Args:
            user_id: User ID to generate digest for
            
        Returns:
            DailyDigest instance or None if no content
        """
        today = date.today()
        
        # Get tasks due today
        tasks_due = self._get_tasks_due_today(user_id)
        
        # Get overdue tasks
        tasks_overdue = self._get_overdue_tasks(user_id)
        
        # Get pending habits (if available)
        habits_pending = self._get_pending_habits(user_id)
        
        # Get goal progress (if available)
        goals_progress = self._get_goal_progress(user_id)
        
        digest = DailyDigest(
            id=f"digest_{user_id}_{today.isoformat()}",
            user_id=user_id,
            digest_date=today,
            tasks_due=tasks_due,
            tasks_overdue=tasks_overdue,
            habits_pending=habits_pending,
            goals_progress=goals_progress,
        )
        
        if not digest.has_content():
            return None
        
        # Store digest
        self._store_digest(digest)
        
        return digest
    
    def send_daily_digest(self, user_id: str = "default") -> bool:
        """
        Generate and send daily digest.
        
        Args:
            user_id: User ID to send digest to
            
        Returns:
            True if digest sent successfully
        """
        digest = self.generate_daily_digest(user_id)
        
        if not digest:
            logger.debug(f"No digest content for user {user_id}")
            return False
        
        # Create notification
        notification = Notification(
            type=NotificationType.DAILY_DIGEST,
            title="📋 Your Daily Briefing",
            message=digest.generate_summary(),
            priority=NotificationPriority.LOW,
            entity_type="digest",
            entity_id=digest.id,
            metadata={'digest_date': digest.digest_date.isoformat()}
        )
        
        # Send via email
        self.engine.dispatch(notification, channels=[NotificationChannel.EMAIL])
        
        # Mark as sent
        digest.sent_at = datetime.now()
        self._update_digest_sent(digest)
        
        logger.info(f"Sent daily digest to user {user_id}")
        return True
    
    # ==========================================
    # Database Operations
    # ==========================================
    
    def _store_task_alert(self, task: TaskAlert) -> None:
        """Store task alert in database."""
        self.db.execute(
            """INSERT OR REPLACE INTO task_alerts 
               (id, task_id, title, due_date, status, urgency_level, 
                reminder_config, alerts_sent, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task.id,
                task.task_id,
                task.title,
                task.due_date.isoformat(),
                task.status.value,
                task.urgency_level.value,
                str(task.reminder_config),
                str(task.alerts_sent),
                task.created_at.isoformat(),
                task.updated_at.isoformat(),
            )
        )
    
    def _get_task_details(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task details from database."""
        row = self.db.fetch_one(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        )
        return dict(row) if row else None
    
    def _get_tasks_due_today(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all tasks due today for a user."""
        today = date.today().isoformat()
        rows = self.db.fetch_all(
            """SELECT * FROM tasks 
               WHERE user_id = ? AND DATE(due_date) = ? AND status != 'completed'""",
            (user_id, today)
        )
        return [dict(row) for row in rows]
    
    def _get_overdue_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all overdue tasks for a user."""
        now = datetime.now().isoformat()
        rows = self.db.fetch_all(
            """SELECT * FROM tasks 
               WHERE user_id = ? AND due_date < ? AND status != 'completed'""",
            (user_id, now)
        )
        return [dict(row) for row in rows]
    
    def _get_pending_habits(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending habits for today."""
        today = date.today().isoformat()
        rows = self.db.fetch_all(
            """SELECT h.* FROM habits h
               LEFT JOIN habit_entries he ON h.id = he.habit_id AND he.entry_date = ?
               WHERE h.user_id = ? AND he.id IS NULL""",
            (today, user_id)
        )
        return [dict(row) for row in rows]
    
    def _get_goal_progress(self, user_id: str) -> List[Dict[str, Any]]:
        """Get goal progress for user."""
        rows = self.db.fetch_all(
            """SELECT * FROM goals WHERE user_id = ? AND status = 'in_progress'""",
            (user_id,)
        )
        return [dict(row) for row in rows]
    
    def _store_digest(self, digest: DailyDigest) -> None:
        """Store digest in database."""
        self.db.execute(
            """INSERT OR REPLACE INTO daily_digests 
               (id, user_id, digest_date, tasks_due, tasks_overdue, 
                habits_pending, goals_progress, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                digest.id,
                digest.user_id,
                digest.digest_date.isoformat(),
                str(digest.tasks_due),
                str(digest.tasks_overdue),
                str(digest.habits_pending),
                str(digest.goals_progress),
                digest.created_at.isoformat(),
            )
        )
    
    def _update_digest_sent(self, digest: DailyDigest) -> None:
        """Update digest as sent."""
        self.db.execute(
            """UPDATE daily_digests SET sent_at = ? WHERE id = ?""",
            (digest.sent_at.isoformat() if digest.sent_at else None, digest.id)
        )
    
    # ==========================================
    # Utility Methods
    # ==========================================
    
    def get_task_alert(self, task_id: str) -> Optional[TaskAlert]:
        """Get task alert by task ID."""
        row = self.db.fetch_one(
            "SELECT * FROM task_alerts WHERE task_id = ?",
            (task_id,)
        )
        return TaskAlert.from_dict(dict(row)) if row else None
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """
        Update task status and handle alerts accordingly.
        
        Args:
            task_id: Task ID to update
            status: New status
            
        Returns:
            True if update successful
        """
        # Cancel alerts if task completed
        if status == TaskStatus.COMPLETED or status == TaskStatus.CANCELLED:
            self.cancel_task_alerts(task_id)
        
        # Update task alert
        self.db.execute(
            """UPDATE task_alerts SET status = ?, updated_at = ? 
               WHERE task_id = ?""",
            (status.value, datetime.now().isoformat(), task_id)
        )
        
        return True


# Singleton instance
_task_alert_manager: Optional[TaskAlertManager] = None
_task_alert_lock = threading.Lock()


def get_task_alert_manager() -> TaskAlertManager:
    """Get the global TaskAlertManager instance."""
    global _task_alert_manager
    
    if _task_alert_manager is None:
        with _task_alert_lock:
            if _task_alert_manager is None:
                _task_alert_manager = TaskAlertManager()
    
    return _task_alert_manager