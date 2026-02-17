"""
Goal Alert Manager

Implements milestone detection and celebration notifications for goals.
Handles progress tracking, milestone celebrations, and deadline warnings.

Phase 4.3 Feature: Milestone Detection & Celebration
- 25%: "Quarter way there!"
- 50%: "Halfway done!"
- 75%: "Almost there!"
- 100%: "Goal completed! 🎉"

Reference:
- Phase 4.3 Research Document: Goal Tracking & Milestone Celebrations
"""

from datetime import datetime, timedelta, date, time
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import threading
import math

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
# Goal Status and Milestone Enums
# ==========================================

class GoalStatus(str, Enum):
    """Status of a goal."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class Milestone(str, Enum):
    """Milestone percentages for goal progress."""
    QUARTER = 25    # 25%
    HALF = 50       # 50%
    THREE_QUARTER = 75  # 75%
    COMPLETE = 100  # 100%
    
    @classmethod
    def get_milestone_for_progress(cls, progress_percent: float) -> Optional['Milestone']:
        """
        Get the milestone that was just crossed for a given progress percentage.
        
        Returns the highest milestone that the progress has reached or exceeded.
        """
        if progress_percent >= 100:
            return cls.COMPLETE
        elif progress_percent >= 75:
            return cls.THREE_QUARTER
        elif progress_percent >= 50:
            return cls.HALF
        elif progress_percent >= 25:
            return cls.QUARTER
        return None
    
    def get_message(self, goal_title: str) -> Tuple[str, str]:
        """Get celebration message for this milestone."""
        messages = {
            Milestone.QUARTER: (
                f"🎯 Quarter way there!",
                f"You've reached 25% on '{goal_title}'. Keep up the great progress!"
            ),
            Milestone.HALF: (
                f"🌟 Halfway done!",
                f"You're 50% of the way to completing '{goal_title}'! You've got this!"
            ),
            Milestone.THREE_QUARTER: (
                f"🚀 Almost there!",
                f"75% complete on '{goal_title}'! The finish line is in sight!"
            ),
            Milestone.COMPLETE: (
                f"🎉 Goal Completed!",
                f"Congratulations! You've achieved your goal: '{goal_title}'!"
            ),
        }
        return messages.get(self, ("Progress Update", f"Progress on '{goal_title}'"))


# ==========================================
# Data Classes
# ==========================================

@dataclass
class GoalAlert:
    """
    Represents an alert configuration for a goal.
    
    Tracks progress, milestones reached, and deadline information
    for celebration and warning notifications.
    """
    id: str
    goal_id: str
    title: str
    target_value: float
    current_value: float
    unit: str = ""
    status: GoalStatus = GoalStatus.NOT_STARTED
    deadline: Optional[datetime] = None
    milestones_reached: List[int] = field(default_factory=list)  # [25, 50, 75, 100]
    last_progress_update: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'goal_id': self.goal_id,
            'title': self.title,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'unit': self.unit,
            'status': self.status.value,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'milestones_reached': self.milestones_reached,
            'last_progress_update': self.last_progress_update.isoformat() if self.last_progress_update else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GoalAlert':
        """Create instance from dictionary."""
        return cls(
            id=data.get('id', ''),
            goal_id=data.get('goal_id', ''),
            title=data.get('title', ''),
            target_value=float(data.get('target_value', 0)),
            current_value=float(data.get('current_value', 0)),
            unit=data.get('unit', ''),
            status=GoalStatus(data.get('status', 'not_started')),
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
            milestones_reached=data.get('milestones_reached', []),
            last_progress_update=datetime.fromisoformat(data['last_progress_update']) if data.get('last_progress_update') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
        )
    
    def calculate_progress_percent(self) -> float:
        """Calculate progress as a percentage."""
        if self.target_value == 0:
            return 0.0
        return min(100.0, (self.current_value / self.target_value) * 100)
    
    def get_new_milestone(self, previous_value: float) -> Optional[Milestone]:
        """
        Check if a new milestone was crossed.
        
        Args:
            previous_value: The previous current_value before update
            
        Returns:
            Milestone if a new one was crossed, None otherwise
        """
        previous_percent = (previous_value / self.target_value) * 100 if self.target_value else 0
        current_percent = self.calculate_progress_percent()
        
        # Check each milestone
        for milestone in [Milestone.QUARTER, Milestone.HALF, Milestone.THREE_QUARTER, Milestone.COMPLETE]:
            threshold = milestone.value
            if previous_percent < threshold <= current_percent:
                if threshold not in self.milestones_reached:
                    return milestone
        
        return None
    
    def is_deadline_approaching(self, days_threshold: int = 7) -> bool:
        """Check if deadline is approaching within threshold days."""
        if not self.deadline:
            return False
        time_remaining = self.deadline - datetime.now()
        return timedelta(days=0) < time_remaining <= timedelta(days=days_threshold)
    
    def is_behind_schedule(self) -> bool:
        """Check if goal is behind schedule based on linear projection."""
        if not self.deadline or self.status != GoalStatus.IN_PROGRESS:
            return False
        
        # Calculate expected progress
        created = self.created_at
        deadline = self.deadline
        now = datetime.now()
        
        if now >= deadline:
            return self.current_value < self.target_value
        
        total_duration = (deadline - created).total_seconds()
        elapsed = (now - created).total_seconds()
        
        if total_duration <= 0:
            return False
        
        expected_progress = elapsed / total_duration
        actual_progress = self.current_value / self.target_value if self.target_value else 0
        
        # Behind if actual is more than 10% below expected
        return actual_progress < (expected_progress - 0.1)


@dataclass
class MilestoneCelebration:
    """
    Record of a milestone celebration notification.
    
    Tracks when milestones were reached and celebrated.
    """
    id: str
    goal_id: str
    milestone: Milestone
    progress_at_time: float
    celebrated_at: datetime = field(default_factory=datetime.now)
    notification_sent: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'goal_id': self.goal_id,
            'milestone': self.milestone.value,
            'progress_at_time': self.progress_at_time,
            'celebrated_at': self.celebrated_at.isoformat(),
            'notification_sent': self.notification_sent,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MilestoneCelebration':
        """Create instance from dictionary."""
        return cls(
            id=data.get('id', ''),
            goal_id=data.get('goal_id', ''),
            milestone=Milestone(data.get('milestone', 25)),
            progress_at_time=float(data.get('progress_at_time', 0)),
            celebrated_at=datetime.fromisoformat(data['celebrated_at']) if data.get('celebrated_at') else datetime.now(),
            notification_sent=bool(data.get('notification_sent', False)),
        )


# ==========================================
# Goal Alert Manager
# ==========================================

class GoalAlertManager:
    """
    Manages goal progress alerts and milestone celebrations.
    
    Phase 4.3 Feature: Milestone Detection & Celebration
    
    When a user updates goal progress, the manager:
    1. Calculates the new progress percentage
    2. Checks if a milestone threshold was crossed
    3. Triggers celebration notifications for new milestones
    4. Sends deadline warnings if goal is behind schedule
    
    Reference:
    - Phase 4.3 Research Document, Section 7: Goal Tracking
    """
    
    # Milestone thresholds (percentage)
    MILESTONES = [25, 50, 75, 100]
    
    # Deadline warning thresholds (days)
    DEADLINE_WARNING_DAYS = [7, 3, 1]
    
    def __init__(self, db=None, engine: Optional[NotificationEngine] = None):
        """
        Initialize goal alert manager.
        
        Args:
            db: Database instance
            engine: Notification engine for dispatch
        """
        self._db = db
        self._engine = engine
    
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
    # Progress Update & Milestone Detection
    # ==========================================
    
    def update_progress(
        self,
        goal_id: str,
        new_value: float,
        user_id: str = "default"
    ) -> Optional[Milestone]:
        """
        Update goal progress and check for milestone crossings.
        
        This is the main entry point for progress updates.
        
        Args:
            goal_id: ID of the goal
            new_value: New current value
            user_id: User ID
            
        Returns:
            Milestone if a new one was crossed, None otherwise
        """
        # Get existing goal alert
        goal_alert = self.get_goal_alert(goal_id)
        
        if not goal_alert:
            # Create new goal alert
            goal_alert = self._create_goal_alert_from_db(goal_id)
            if not goal_alert:
                logger.warning(f"Goal {goal_id} not found")
                return None
        
        # Store previous value
        previous_value = goal_alert.current_value
        
        # Update value
        goal_alert.current_value = new_value
        goal_alert.last_progress_update = datetime.now()
        goal_alert.updated_at = datetime.now()
        
        # Update status if needed
        if new_value >= goal_alert.target_value:
            goal_alert.status = GoalStatus.COMPLETED
        elif new_value > 0 and goal_alert.status == GoalStatus.NOT_STARTED:
            goal_alert.status = GoalStatus.IN_PROGRESS
        
        # Check for new milestone
        new_milestone = goal_alert.get_new_milestone(previous_value)
        
        if new_milestone:
            # Record milestone
            goal_alert.milestones_reached.append(new_milestone.value)
            
            # Create celebration
            self._celebrate_milestone(goal_alert, new_milestone)
        
        # Save updates
        self._store_goal_alert(goal_alert)
        
        # Update original goal in database
        self._update_goal_progress(goal_id, new_value)
        
        logger.info(f"Updated goal {goal_id} progress: {new_value}/{goal_alert.target_value}")
        return new_milestone
    
    def _celebrate_milestone(self, goal: GoalAlert, milestone: Milestone) -> None:
        """
        Create celebration notification for a milestone.
        
        Args:
            goal: GoalAlert instance
            milestone: Milestone that was reached
        """
        title, message = milestone.get_message(goal.title)
        
        # Create celebration record
        celebration = MilestoneCelebration(
            id=f"celebration_{goal.goal_id}_{milestone.value}",
            goal_id=goal.goal_id,
            milestone=milestone,
            progress_at_time=goal.calculate_progress_percent(),
            notification_sent=True
        )
        
        # Store celebration
        self._store_celebration(celebration)
        
        # Create notification
        notification = Notification(
            type=NotificationType.ACHIEVEMENT,
            title=title,
            message=message,
            priority=NotificationPriority.HIGH if milestone == Milestone.COMPLETE else NotificationPriority.MEDIUM,
            entity_type="goal",
            entity_id=goal.goal_id,
            metadata={
                'milestone': milestone.value,
                'progress_percent': goal.calculate_progress_percent(),
                'target_value': goal.target_value,
                'current_value': goal.current_value,
            }
        )
        
        # Dispatch notification
        channels = [NotificationChannel.IN_APP, NotificationChannel.WEB_PUSH]
        if milestone == Milestone.COMPLETE:
            channels.append(NotificationChannel.EMAIL)
        
        self.engine.dispatch(notification, channels=channels)
        
        logger.info(f"Celebrated {milestone.value}% milestone for goal {goal.goal_id}")
    
    # ==========================================
    # Deadline Warnings
    # ==========================================
    
    def check_deadline_warnings(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """
        Check all goals for deadline warnings.
        
        Sends warnings for goals that are approaching deadline
        or behind schedule.
        
        Args:
            user_id: User ID to check
            
        Returns:
            List of warnings sent
        """
        warnings = []
        
        # Get all active goals
        goals = self._get_active_goals(user_id)
        
        for goal_data in goals:
            goal = GoalAlert.from_dict(goal_data)
            
            # Check if deadline approaching
            if goal.is_deadline_approaching(days_threshold=7):
                if goal.deadline is None:
                    continue
                time_remaining = goal.deadline - datetime.now()
                days_remaining = time_remaining.days
                
                # Only warn at specific thresholds
                if days_remaining in self.DEADLINE_WARNING_DAYS:
                    warning = self._send_deadline_warning(goal, days_remaining)
                    warnings.append(warning)
            
            # Check if behind schedule
            elif goal.is_behind_schedule():
                warning = self._send_behind_schedule_warning(goal)
                warnings.append(warning)
        
        return warnings
    
    def _send_deadline_warning(self, goal: GoalAlert, days_remaining: int) -> Dict[str, Any]:
        """Send deadline warning notification."""
        progress = goal.calculate_progress_percent()
        
        title = f"⏰ Goal Deadline: {goal.title}"
        message = f"'{goal.title}' is due in {days_remaining} day(s). You're at {progress:.1f}% progress."
        
        if progress < 75:
            message += " You might want to pick up the pace!"
        
        notification = Notification(
            type=NotificationType.GOAL_DEADLINE,
            title=title,
            message=message,
            priority=NotificationPriority.HIGH if days_remaining <= 3 else NotificationPriority.MEDIUM,
            entity_type="goal",
            entity_id=goal.goal_id,
            metadata={
                'days_remaining': days_remaining,
                'progress_percent': progress,
                'deadline': goal.deadline.isoformat() if goal.deadline else None,
            }
        )
        
        self.engine.dispatch(notification, channels=[NotificationChannel.WEB_PUSH, NotificationChannel.IN_APP])
        
        return {
            'goal_id': goal.goal_id,
            'type': 'deadline_warning',
            'days_remaining': days_remaining,
            'progress': progress,
        }
    
    def _send_behind_schedule_warning(self, goal: GoalAlert) -> Dict[str, Any]:
        """Send behind schedule warning notification."""
        progress = goal.calculate_progress_percent()
        
        title = f"📉 Behind Schedule: {goal.title}"
        message = f"'{goal.title}' appears to be behind schedule. You're at {progress:.1f}% progress."
        
        notification = Notification(
            type=NotificationType.GOAL_DEADLINE,
            title=title,
            message=message,
            priority=NotificationPriority.MEDIUM,
            entity_type="goal",
            entity_id=goal.goal_id,
            metadata={
                'type': 'behind_schedule',
                'progress_percent': progress,
            }
        )
        
        self.engine.dispatch(notification, channels=[NotificationChannel.IN_APP])
        
        return {
            'goal_id': goal.goal_id,
            'type': 'behind_schedule',
            'progress': progress,
        }
    
    # ==========================================
    # Goal Alert Management
    # ==========================================
    
    def create_goal_alert(
        self,
        goal_id: str,
        title: str,
        target_value: float,
        unit: str = "",
        deadline: Optional[datetime] = None
    ) -> GoalAlert:
        """
        Create a new goal alert configuration.
        
        Args:
            goal_id: ID of the goal
            title: Goal title
            target_value: Target value to reach
            unit: Unit of measurement
            deadline: Optional deadline
            
        Returns:
            Created GoalAlert instance
        """
        goal_alert = GoalAlert(
            id=f"goal_alert_{goal_id}",
            goal_id=goal_id,
            title=title,
            target_value=target_value,
            current_value=0,
            unit=unit,
            status=GoalStatus.NOT_STARTED,
            deadline=deadline,
        )
        
        self._store_goal_alert(goal_alert)
        
        logger.info(f"Created goal alert for {goal_id}: {title}")
        return goal_alert
    
    def get_goal_alert(self, goal_id: str) -> Optional[GoalAlert]:
        """Get goal alert by goal ID."""
        row = self.db.fetch_one(
            "SELECT * FROM goal_alerts WHERE goal_id = ?",
            (goal_id,)
        )
        return GoalAlert.from_dict(dict(row)) if row else None
    
    def delete_goal_alert(self, goal_id: str) -> bool:
        """Delete goal alert."""
        self.db.execute(
            "DELETE FROM goal_alerts WHERE goal_id = ?",
            (goal_id,)
        )
        return True
    
    # ==========================================
    # Statistics & Analytics
    # ==========================================
    
    def get_goal_statistics(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Get statistics about goal progress and milestones.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with goal statistics
        """
        goals = self._get_all_goals(user_id)
        
        total = len(goals)
        completed = sum(1 for g in goals if g.get('status') == 'completed')
        in_progress = sum(1 for g in goals if g.get('status') == 'in_progress')
        
        # Calculate average progress
        progress_values = []
        for g in goals:
            target = float(g.get('target_value', 0))
            current = float(g.get('current_value', 0))
            if target > 0:
                progress_values.append((current / target) * 100)
        
        avg_progress = sum(progress_values) / len(progress_values) if progress_values else 0
        
        # Get milestone counts
        milestone_counts = {25: 0, 50: 0, 75: 0, 100: 0}
        celebrations = self.db.fetch_all(
            "SELECT milestone, COUNT(*) as count FROM milestone_celebrations WHERE goal_id IN (SELECT goal_id FROM goal_alerts) GROUP BY milestone"
        )
        for row in celebrations:
            milestone_counts[row['milestone']] = row['count']
        
        return {
            'total_goals': total,
            'completed': completed,
            'in_progress': in_progress,
            'not_started': total - completed - in_progress,
            'average_progress': round(avg_progress, 1),
            'milestones_celebrated': milestone_counts,
            'completion_rate': round((completed / total) * 100, 1) if total > 0 else 0,
        }
    
    # ==========================================
    # Database Operations
    # ==========================================
    
    def _store_goal_alert(self, goal: GoalAlert) -> None:
        """Store goal alert in database."""
        self.db.execute(
            """INSERT OR REPLACE INTO goal_alerts 
               (id, goal_id, title, target_value, current_value, unit, 
                status, deadline, milestones_reached, last_progress_update, 
                created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                goal.id,
                goal.goal_id,
                goal.title,
                goal.target_value,
                goal.current_value,
                goal.unit,
                goal.status.value,
                goal.deadline.isoformat() if goal.deadline else None,
                str(goal.milestones_reached),
                goal.last_progress_update.isoformat() if goal.last_progress_update else None,
                goal.created_at.isoformat(),
                goal.updated_at.isoformat(),
            )
        )
    
    def _store_celebration(self, celebration: MilestoneCelebration) -> None:
        """Store milestone celebration in database."""
        self.db.execute(
            """INSERT OR REPLACE INTO milestone_celebrations 
               (id, goal_id, milestone, progress_at_time, celebrated_at, notification_sent)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                celebration.id,
                celebration.goal_id,
                celebration.milestone.value,
                celebration.progress_at_time,
                celebration.celebrated_at.isoformat(),
                1 if celebration.notification_sent else 0,
            )
        )
    
    def _create_goal_alert_from_db(self, goal_id: str) -> Optional[GoalAlert]:
        """Create GoalAlert from existing goal in database."""
        row = self.db.fetch_one(
            "SELECT * FROM goals WHERE id = ?",
            (goal_id,)
        )
        
        if not row:
            return None
        
        data = dict(row)
        return GoalAlert(
            id=f"goal_alert_{goal_id}",
            goal_id=goal_id,
            title=data.get('title', ''),
            target_value=float(data.get('target_value', 0)),
            current_value=float(data.get('current_value', 0)),
            unit=data.get('unit', ''),
            status=GoalStatus(data.get('status', 'not_started')),
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
        )
    
    def _update_goal_progress(self, goal_id: str, new_value: float) -> None:
        """Update progress in original goals table."""
        self.db.execute(
            """UPDATE goals SET current_value = ?, updated_at = ? 
               WHERE id = ?""",
            (new_value, datetime.now().isoformat(), goal_id)
        )
    
    def _get_active_goals(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active goals for a user."""
        rows = self.db.fetch_all(
            """SELECT * FROM goals 
               WHERE user_id = ? AND status = 'in_progress'""",
            (user_id,)
        )
        return [dict(row) for row in rows]
    
    def _get_all_goals(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all goals for a user."""
        rows = self.db.fetch_all(
            "SELECT * FROM goals WHERE user_id = ?",
            (user_id,)
        )
        return [dict(row) for row in rows]


# Singleton instance
_goal_alert_manager: Optional[GoalAlertManager] = None
_goal_alert_lock = threading.Lock()


def get_goal_alert_manager() -> GoalAlertManager:
    """Get the global GoalAlertManager instance."""
    global _goal_alert_manager
    
    if _goal_alert_manager is None:
        with _goal_alert_lock:
            if _goal_alert_manager is None:
                _goal_alert_manager = GoalAlertManager()
    
    return _goal_alert_manager