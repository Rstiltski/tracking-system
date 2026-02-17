"""
Reminder Scheduler

Implements APScheduler-based temporal orchestration for notifications.
Handles recurring reminders, smart scheduling, and snooze functionality.

Phase 4.2 Enhancements:
- Windowed Adaptive Mean with IQR outlier rejection
- K-Means clustering for bimodal schedules
- Streak protection with urgency escalation
- Intelligent snooze with day-boundary awareness

Reference:
- Phase 4.2 Research Document: Intelligent Behavioral Modification Systems
- PROJECT_RULES.md: Singleton pattern for Streamlit compatibility
"""

from datetime import datetime, timedelta, date, time
from typing import Optional, List, Dict, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import threading
import statistics
import math

from brain.notifications.models import (
    Notification,
    NotificationType,
    NotificationPriority,
    NotificationStatus,
    ReminderSchedule,
    CompletionHistory,
    NotificationChannel,
)
from brain.notifications.engine import NotificationEngine, get_engine
from brain.behavioral.habit_stacking import (
    HabitStack,
    StackItem,
    HabitStackingEngine,
    AnchorCategory,
)

logger = logging.getLogger(__name__)


# ==========================================
# Phase 4.2: Urgency Levels for Streak Protection
# ==========================================

class UrgencyLevel(str, Enum):
    """Urgency levels for streak protection escalation."""
    LOW = "low"           # Routine reminder, >8 hours remaining
    MEDIUM = "medium"     # Follow-up, 4-8 hours remaining
    HIGH = "high"         # Risk of breaking streak, 2-4 hours remaining
    CRITICAL = "critical" # Last chance, <2 hours remaining


@dataclass
class TimingCluster:
    """Represents a cluster of completion times for K-Means."""
    center: float  # Center in minutes from midnight
    members: List[float] = field(default_factory=list)
    
    def update_center(self) -> None:
        """Update cluster center based on members."""
        if self.members:
            self.center = statistics.mean(self.members)


@dataclass
class SmartTimingResult:
    """Result from smart timing calculation."""
    optimal_time: time
    confidence: float  # 0.0 - 1.0
    sample_size: int
    outlier_count: int
    clusters_found: int


@dataclass
class StreakProtectionState:
    """Tracks streak protection state for an entity."""
    entity_type: str
    entity_id: str
    current_streak: int
    urgency_level: UrgencyLevel
    hours_remaining: float
    reminder_count: int
    last_reminder_time: Optional[datetime] = None
    next_reminder_time: Optional[datetime] = None
    
    def should_send_reminder(self) -> bool:
        """Determine if a reminder should be sent now."""
        if self.urgency_level == UrgencyLevel.LOW:
            # Only send if no reminder in last 4 hours
            if self.last_reminder_time:
                elapsed = datetime.now() - self.last_reminder_time
                return elapsed.total_seconds() >= 4 * 3600
            return True
        
        elif self.urgency_level == UrgencyLevel.MEDIUM:
            # Send if no reminder in last 2 hours
            if self.last_reminder_time:
                elapsed = datetime.now() - self.last_reminder_time
                return elapsed.total_seconds() >= 2 * 3600
            return True
        
        elif self.urgency_level == UrgencyLevel.HIGH:
            # Send if no reminder in last hour
            if self.last_reminder_time:
                elapsed = datetime.now() - self.last_reminder_time
                return elapsed.total_seconds() >= 3600
            return True
        
        elif self.urgency_level == UrgencyLevel.CRITICAL:
            # Send every 30 minutes
            if self.last_reminder_time:
                elapsed = datetime.now() - self.last_reminder_time
                return elapsed.total_seconds() >= 1800
            return True
        
        return False


@dataclass
class SnoozeConfig:
    """Configuration for intelligent snooze behavior."""
    max_snoozes: int = 3
    snooze_durations: List[int] = field(default_factory=lambda: [5, 10, 15, 30])
    escalate_after_snoozes: int = 2
    respect_day_boundary: bool = True
    max_snooze_time: time = field(default_factory=lambda: time(23, 0))  # Don't snooze past 11 PM


# Try to import APScheduler
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.date import DateTrigger
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
    from apscheduler.executors.pool import ThreadPoolExecutor
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    logger.warning("APScheduler not installed. Run: pip install apscheduler")


class SmartScheduler:
    """
    Implements adaptive scheduling algorithms.
    
    Phase 4.2 Enhanced with:
    - Windowed Adaptive Mean with IQR outlier rejection
    - K-Means clustering for bimodal schedules (morning/evening)
    - Dampening factor to prevent oscillation
    
    Reference:
    - Phase 4.2 Research Document, Section 6: Smart Timing Algorithm Implementation
    """
    
    # Configuration constants
    DEFAULT_MIN_SAMPLES = 10
    DEFAULT_LEAD_MINUTES = 15
    DAMPENING_FACTOR = 0.5  # Prevents oscillation in time adjustments
    MAX_ADJUSTMENT_MINUTES = 60  # Cap on single adjustment
    
    def __init__(self, db=None):
        """Initialize smart scheduler."""
        self._db = db
    
    @property
    def db(self):
        """Get database instance."""
        if self._db is None:
            from tracking_app.database import get_db
            self._db = get_db()
        return self._db
    
    def calculate_optimal_time(
        self,
        entity_type: str,
        entity_id: str,
        min_samples: int = 5,
        lead_minutes: int = 15
    ) -> Optional[time]:
        """
        Calculate optimal reminder time based on completion history.
        
        Uses the "Rolling Average" algorithm:
        1. Get last N completion records
        2. Convert to minutes from midnight
        3. Filter outliers (beyond 2 standard deviations)
        4. Calculate mean
        5. Subtract lead time
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            min_samples: Minimum samples required
            lead_minutes: Minutes before typical completion time
            
        Returns:
            Optimal reminder time or None if insufficient data
        """
        result = self.calculate_optimal_time_advanced(
            entity_type, entity_id, min_samples, lead_minutes
        )
        return result.optimal_time if result else None
    
    def calculate_optimal_time_advanced(
        self,
        entity_type: str,
        entity_id: str,
        min_samples: int = DEFAULT_MIN_SAMPLES,
        lead_minutes: int = DEFAULT_LEAD_MINUTES,
        num_clusters: int = 1
    ) -> Optional[SmartTimingResult]:
        """
        Advanced smart timing with IQR outlier rejection and K-Means clustering.
        
        Phase 4.2 Enhancement: Windowed Adaptive Mean Algorithm
        
        Algorithm Steps:
        1. Data Ingestion: Fetch last N completion logs
        2. Outlier Rejection: IQR method (Q1 - 1.5*IQR, Q3 + 1.5*IQR)
        3. Clustering: K-Means for bimodal schedules
        4. Offset Calculation: Median delta with dampening
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            min_samples: Minimum samples required (default 10)
            lead_minutes: Minutes before typical completion time
            num_clusters: Number of clusters for K-Means (1 or 2)
            
        Returns:
            SmartTimingResult with optimal time and metadata
        """
        # Get completion history
        rows = self.db.fetch_all(
            """SELECT completed_at, scheduled_for 
               FROM completion_history 
               WHERE entity_type = ? AND entity_id = ?
               ORDER BY completed_at DESC LIMIT 50""",
            (entity_type, entity_id)
        )
        
        if len(rows) < min_samples:
            logger.debug(f"Insufficient samples ({len(rows)}) for smart scheduling")
            return None
        
        # Extract completion times (minutes from midnight)
        completion_minutes = []
        scheduled_minutes = []
        
        for row in rows:
            completed_at = datetime.fromisoformat(row['completed_at'])
            completion_minutes.append(completed_at.hour * 60 + completed_at.minute)
            
            # Get scheduled time if available
            if row['scheduled_for']:
                scheduled = datetime.fromisoformat(row['scheduled_for'])
                scheduled_minutes.append(scheduled.hour * 60 + scheduled.minute)
        
        if not completion_minutes:
            return None
        
        original_count = len(completion_minutes)
        
        # Step 2: IQR Outlier Rejection
        filtered_minutes, outlier_count = self._filter_outliers_iqr(completion_minutes)
        
        if not filtered_minutes:
            filtered_minutes = completion_minutes
            outlier_count = 0
        
        # Step 3: K-Means Clustering (if bimodal data expected)
        clusters_found = 1
        optimal_minutes = 0
        
        if num_clusters > 1 and len(filtered_minutes) >= 20:
            # Try clustering for bimodal schedules
            clusters = self._kmeans_cluster(filtered_minutes, num_clusters)
            clusters_found = len([c for c in clusters if c.members])
            
            # Use the largest cluster
            largest_cluster = max(clusters, key=lambda c: len(c.members))
            optimal_minutes = int(largest_cluster.center)
        else:
            # Use median for robustness against skew
            optimal_minutes = int(statistics.median(filtered_minutes))
        
        # Step 4: Calculate offset from scheduled time (if available)
        if scheduled_minutes:
            # Calculate median delay
            deltas = []
            for i, (comp, sched) in enumerate(zip(completion_minutes, scheduled_minutes)):
                delta = comp - sched
                # Handle day boundary
                if delta > 720:  # More than 12 hours
                    delta -= 1440
                elif delta < -720:
                    delta += 1440
                deltas.append(delta)
            
            if deltas:
                median_delay = statistics.median(deltas)
                
                # Apply dampening factor to prevent oscillation
                adjustment = int(median_delay * self.DAMPENING_FACTOR)
                
                # Cap adjustment
                adjustment = max(-self.MAX_ADJUSTMENT_MINUTES, 
                               min(self.MAX_ADJUSTMENT_MINUTES, adjustment))
                
                # Apply adjustment
                optimal_minutes = int(statistics.median(scheduled_minutes)) + adjustment
        
        # Subtract lead time
        optimal_minutes -= lead_minutes
        
        # Handle day boundary
        if optimal_minutes < 0:
            optimal_minutes += 24 * 60
        elif optimal_minutes >= 24 * 60:
            optimal_minutes -= 24 * 60
        
        # Convert to time
        hours = optimal_minutes // 60
        minutes = optimal_minutes % 60
        
        # Calculate confidence based on sample size and variance
        confidence = min(1.0, len(filtered_minutes) / 30.0)
        if len(filtered_minutes) >= 5:
            std_dev = statistics.stdev(filtered_minutes)
            # Lower variance = higher confidence
            confidence *= max(0.3, 1.0 - (std_dev / 360.0))  # 360 mins = 6 hours std dev
        
        return SmartTimingResult(
            optimal_time=time(hours, minutes),
            confidence=confidence,
            sample_size=len(filtered_minutes),
            outlier_count=outlier_count,
            clusters_found=clusters_found
        )
    
    def _filter_outliers_iqr(self, data: List[float]) -> Tuple[List[float], int]:
        """
        Filter outliers using Interquartile Range (IQR) method.
        
        Values outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR] are considered outliers.
        
        Args:
            data: List of values
            
        Returns:
            Tuple of (filtered_data, outlier_count)
        """
        if len(data) < 4:
            return data, 0
        
        # Calculate quartiles
        sorted_data = sorted(data)
        n = len(sorted_data)
        
        q1_idx = n // 4
        q3_idx = (3 * n) // 4
        
        q1 = sorted_data[q1_idx]
        q3 = sorted_data[q3_idx]
        iqr = q3 - q1
        
        # Calculate fences
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        
        # Filter data
        filtered = [x for x in data if lower_fence <= x <= upper_fence]
        outlier_count = len(data) - len(filtered)
        
        if outlier_count > 0:
            logger.debug(f"IQR filtering removed {outlier_count} outliers")
        
        return filtered, outlier_count
    
    def _kmeans_cluster(self, data: List[float], k: int = 2, max_iterations: int = 10) -> List[TimingCluster]:
        """
        Perform K-Means clustering on time data.
        
        Used to identify bimodal patterns (e.g., morning and evening habits).
        
        Args:
            data: List of time values (minutes from midnight)
            k: Number of clusters
            max_iterations: Maximum iterations
            
        Returns:
            List of TimingCluster objects
        """
        if not data:
            return []
        
        # Initialize clusters with evenly spaced centers
        # For time data, use 6am and 6pm as initial centers for k=2
        if k == 2:
            initial_centers = [360, 1080]  # 6:00 AM, 6:00 PM
        else:
            # Spread evenly across 24 hours
            initial_centers = [i * 1440 // k for i in range(k)]
        
        clusters = [TimingCluster(center=c) for c in initial_centers[:k]]
        
        for iteration in range(max_iterations):
            # Clear members
            for cluster in clusters:
                cluster.members = []
            
            # Assign points to nearest cluster
            for point in data:
                # Handle circular distance (time wraps at midnight)
                distances = []
                for cluster in clusters:
                    dist = abs(point - cluster.center)
                    # Handle wrap-around
                    dist = min(dist, 1440 - dist)
                    distances.append(dist)
                
                nearest_idx = distances.index(min(distances))
                clusters[nearest_idx].members.append(point)
            
            # Update centers
            old_centers = [c.center for c in clusters]
            for cluster in clusters:
                cluster.update_center()
            
            # Check convergence
            new_centers = [c.center for c in clusters]
            if old_centers == new_centers:
                break
        
        return clusters
    
    def update_smart_times(self) -> int:
        """
        Update smart times for all schedules with smart scheduling enabled.
        
        Returns:
            Number of schedules updated
        """
        engine = get_engine()
        schedules = engine.get_active_schedules()
        
        updated = 0
        for schedule in schedules:
            if not schedule.is_smart:
                continue
            
            result = self.calculate_optimal_time_advanced(
                schedule.entity_type,
                schedule.entity_id
            )
            
            if result and result.optimal_time != schedule.smart_time:
                schedule.smart_time = result.optimal_time
                engine.update_schedule(schedule)
                updated += 1
                logger.debug(
                    f"Updated smart time for {schedule.entity_id}: "
                    f"{result.optimal_time} (confidence: {result.confidence:.2f})"
                )
        
        logger.info(f"Updated smart times for {updated} schedules")
        return updated


class StreakProtector:
    """
    Implements streak protection with urgency escalation.
    
    Phase 4.2 Feature: Prevents streak breaks through intelligent
    reminder escalation based on time remaining in the day.
    
    Algorithm:
    1. Monitor active habits with streaks
    2. Calculate hours remaining until "day end" (default: midnight)
    3. Escalate urgency as time window shrinks
    4. Increase reminder frequency at higher urgency levels
    
    Reference:
    - Phase 4.2 Research Document, Section 3: Streak Protection System
    """
    
    # Urgency thresholds (hours remaining)
    LOW_THRESHOLD = 8.0
    MEDIUM_THRESHOLD = 4.0
    HIGH_THRESHOLD = 2.0
    
    def __init__(self, db=None, day_end_hour: int = 24):
        """
        Initialize streak protector.
        
        Args:
            db: Database instance
            day_end_hour: Hour when the "day" ends (default: midnight = 24)
        """
        self._db = db
        self.day_end_hour = day_end_hour
        self._state_cache: Dict[str, StreakProtectionState] = {}
    
    @property
    def db(self):
        """Get database instance."""
        if self._db is None:
            from tracking_app.database import get_db
            self._db = get_db()
        return self._db
    
    def get_urgency_level(self, hours_remaining: float) -> UrgencyLevel:
        """
        Determine urgency level based on hours remaining.
        
        Args:
            hours_remaining: Hours until day end
            
        Returns:
            UrgencyLevel enum value
        """
        if hours_remaining <= self.HIGH_THRESHOLD:
            return UrgencyLevel.CRITICAL
        elif hours_remaining <= self.MEDIUM_THRESHOLD:
            return UrgencyLevel.HIGH
        elif hours_remaining <= self.LOW_THRESHOLD:
            return UrgencyLevel.MEDIUM
        else:
            return UrgencyLevel.LOW
    
    def calculate_hours_remaining(self) -> float:
        """
        Calculate hours remaining until day end.
        
        Returns:
            Hours remaining as float
        """
        now = datetime.now()
        day_end = now.replace(hour=self.day_end_hour % 24, minute=0, second=0, microsecond=0)
        
        if self.day_end_hour > 24:
            # Day end is tomorrow
            day_end += timedelta(days=1)
        elif now.hour >= self.day_end_hour:
            # Already past day end, use tomorrow
            day_end += timedelta(days=1)
        
        delta = day_end - now
        return delta.total_seconds() / 3600
    
    def get_protection_state(self, entity_type: str, entity_id: str) -> StreakProtectionState:
        """
        Get streak protection state for an entity.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            
        Returns:
            StreakProtectionState for the entity
        """
        cache_key = f"{entity_type}:{entity_id}"
        
        if cache_key in self._state_cache:
            return self._state_cache[cache_key]
        
        # Get streak info
        streak = self._get_current_streak(entity_type, entity_id)
        
        # Get reminder history for today
        reminder_count = self._get_todays_reminder_count(entity_type, entity_id)
        last_reminder = self._get_last_reminder_time(entity_type, entity_id)
        
        # Calculate urgency
        hours_remaining = self.calculate_hours_remaining()
        urgency = self.get_urgency_level(hours_remaining)
        
        state = StreakProtectionState(
            entity_type=entity_type,
            entity_id=entity_id,
            current_streak=streak,
            urgency_level=urgency,
            hours_remaining=hours_remaining,
            reminder_count=reminder_count,
            last_reminder_time=last_reminder
        )
        
        self._state_cache[cache_key] = state
        return state
    
    def should_send_streak_reminder(self, entity_type: str, entity_id: str) -> Tuple[bool, UrgencyLevel]:
        """
        Determine if a streak protection reminder should be sent.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            
        Returns:
            Tuple of (should_send, urgency_level)
        """
        state = self.get_protection_state(entity_type, entity_id)
        
        # Check if already completed today
        if self._is_completed_today(entity_type, entity_id):
            return False, state.urgency_level
        
        # Check if streak is at risk (streak > 0)
        if state.current_streak == 0:
            return False, state.urgency_level
        
        # Check if should send based on urgency
        should_send = state.should_send_reminder()
        
        return should_send, state.urgency_level
    
    def get_escalated_message(self, urgency: UrgencyLevel, streak: int, habit_name: str) -> Tuple[str, str]:
        """
        Get escalated notification message based on urgency level.
        
        Args:
            urgency: Current urgency level
            streak: Current streak count
            habit_name: Name of the habit
            
        Returns:
            Tuple of (title, message)
        """
        if urgency == UrgencyLevel.LOW:
            return (
                f"Time for {habit_name}",
                f"Keep your {streak}-day streak going! 🎯"
            )
        elif urgency == UrgencyLevel.MEDIUM:
            return (
                f"Don't forget: {habit_name}",
                f"Your {streak}-day streak is counting on you! 💪"
            )
        elif urgency == UrgencyLevel.HIGH:
            return (
                f"⚠️ Streak Alert: {habit_name}",
                f"Only a few hours left! Protect your {streak}-day streak! 🔥"
            )
        else:  # CRITICAL
            return (
                f"🚨 LAST CHANCE: {habit_name}",
                f"Final hours! Your {streak}-day streak is at risk! Act now! ⚡"
            )
    
    def _get_current_streak(self, entity_type: str, entity_id: str) -> int:
        """Get current streak for an entity."""
        if entity_type != "habit":
            return 0
        
        rows = self.db.fetch_all(
            """SELECT entry_date FROM habit_entries 
               WHERE habit_id = ? AND skipped = 0
               ORDER BY entry_date DESC LIMIT 100""",
            (entity_id,)
        )
        
        if not rows:
            return 0
        
        streak = 0
        prev_date = None
        
        for row in rows:
            entry_date = date.fromisoformat(row['entry_date'])
            
            if prev_date is None:
                today = date.today()
                if entry_date == today or entry_date == today - timedelta(days=1):
                    streak = 1
                    prev_date = entry_date
            else:
                if entry_date == prev_date - timedelta(days=1):
                    streak += 1
                    prev_date = entry_date
                else:
                    break
        
        return streak
    
    def _get_todays_reminder_count(self, entity_type: str, entity_id: str) -> int:
        """Get number of reminders sent today for this entity."""
        today = date.today().isoformat()
        
        row = self.db.fetch_one(
            """SELECT COUNT(*) as count FROM notification_log 
               WHERE entity_type = ? AND entity_id = ? 
               AND DATE(sent_at) = ?""",
            (entity_type, entity_id, today)
        )
        
        return row['count'] if row else 0
    
    def _get_last_reminder_time(self, entity_type: str, entity_id: str) -> Optional[datetime]:
        """Get the time of the last reminder for this entity."""
        row = self.db.fetch_one(
            """SELECT sent_at FROM notification_log 
               WHERE entity_type = ? AND entity_id = ? 
               ORDER BY sent_at DESC LIMIT 1""",
            (entity_type, entity_id)
        )
        
        if row:
            return datetime.fromisoformat(row['sent_at'])
        return None
    
    def _is_completed_today(self, entity_type: str, entity_id: str) -> bool:
        """Check if entity is completed today."""
        if entity_type != "habit":
            return False
        
        today = date.today().isoformat()
        row = self.db.fetch_one(
            """SELECT id FROM habit_entries 
               WHERE habit_id = ? AND entry_date = ? AND skipped = 0""",
            (entity_id, today)
        )
        
        return row is not None
    
    def clear_cache(self) -> None:
        """Clear the state cache."""
        self._state_cache.clear()


class IntelligentSnoozer:
    """
    Implements intelligent snooze with day-boundary awareness.
    
    Phase 4.2 Feature: Smart snooze that respects user patterns
    and prevents late-night reminders.
    
    Features:
    - Configurable snooze durations
    - Day boundary awareness (no snooze past cutoff time)
    - Escalation after multiple snoozes
    - Learns optimal snooze duration from user behavior
    
    Reference:
    - Phase 4.2 Research Document, Section 5: Intelligent Snooze
    """
    
    def __init__(self, db=None, config: Optional[SnoozeConfig] = None):
        """
        Initialize intelligent snoozer.
        
        Args:
            db: Database instance
            config: Snooze configuration
        """
        self._db = db
        self.config = config or SnoozeConfig()
    
    @property
    def db(self):
        """Get database instance."""
        if self._db is None:
            from tracking_app.database import get_db
            self._db = get_db()
        return self._db
    
    def get_snooze_options(self, current_time: Optional[time] = None) -> List[int]:
        """
        Get available snooze durations based on current time.
        
        Respects day boundary - won't offer snooze durations that
        would push the reminder past the cutoff time.
        
        Args:
            current_time: Current time (defaults to now)
            
        Returns:
            List of available snooze durations in minutes
        """
        now = current_time or datetime.now().time()
        cutoff = self.config.max_snooze_time
        
        # Convert to minutes for easier calculation
        now_minutes = now.hour * 60 + now.minute
        cutoff_minutes = cutoff.hour * 60 + cutoff.minute
        
        # Handle day boundary
        if cutoff_minutes < now_minutes:
            # Cutoff is tomorrow (e.g., 2 AM cutoff, currently 11 PM)
            minutes_until_cutoff = (24 * 60 - now_minutes) + cutoff_minutes
        else:
            minutes_until_cutoff = cutoff_minutes - now_minutes
        
        # Filter snooze durations
        available = []
        for duration in self.config.snooze_durations:
            if duration <= minutes_until_cutoff:
                available.append(duration)
        
        # If no durations available, offer short snooze anyway
        if not available and self.config.snooze_durations:
            available = [min(5, self.config.snooze_durations[0])]
        
        return available
    
    def calculate_snooze_time(
        self,
        current_snoozes: int,
        current_time: Optional[time] = None
    ) -> Tuple[Optional[time], bool]:
        """
        Calculate the next snooze time.
        
        Args:
            current_snoozes: Number of snoozes already used
            current_time: Current time (defaults to now)
            
        Returns:
            Tuple of (snooze_time, is_escalated)
        """
        if current_snoozes >= self.config.max_snoozes:
            logger.info("Max snoozes reached")
            return None, False
        
        now = current_time or datetime.now().time()
        available = self.get_snooze_options(now)
        
        if not available:
            return None, False
        
        # Select snooze duration
        # After escalation threshold, use shorter snoozes
        is_escalated = current_snoozes >= self.config.escalate_after_snoozes
        
        if is_escalated:
            # Use shortest available duration
            duration = min(available)
        else:
            # Use learned or default duration
            duration = self._get_learned_snooze_duration(available)
        
        # Calculate new time
        now_minutes = now.hour * 60 + now.minute
        new_minutes = now_minutes + duration
        
        # Handle day boundary
        if new_minutes >= 24 * 60:
            new_minutes -= 24 * 60
        
        return time(new_minutes // 60, new_minutes % 60), is_escalated
    
    def record_snooze_choice(self, duration: int) -> None:
        """
        Record a snooze choice for learning.
        
        Args:
            duration: Chosen snooze duration in minutes
        """
        # Store in database for learning
        self.db.execute(
            """INSERT INTO snooze_history (duration_minutes, chosen_at)
               VALUES (?, ?)""",
            (duration, datetime.now().isoformat())
        )
    
    def _get_learned_snooze_duration(self, available: List[int]) -> int:
        """
        Get the learned optimal snooze duration.
        
        Args:
            available: List of available durations
            
        Returns:
            Most commonly used duration from available options
        """
        # Get most common snooze duration from history
        row = self.db.fetch_one(
            """SELECT duration_minutes, COUNT(*) as count 
               FROM snooze_history 
               WHERE chosen_at >= datetime('now', '-30 days')
               GROUP BY duration_minutes 
               ORDER BY count DESC LIMIT 1"""
        )
        
        if row and row['duration_minutes'] in available:
            return row['duration_minutes']
        
        # Default to middle option
        return available[len(available) // 2] if available else 10


@dataclass
class StackTriggerConfig:
    """Configuration for stack-triggered reminders."""
    delay_after_previous: int = 60  # Seconds to wait after previous habit
    reminder_timeout: int = 300  # Max seconds to wait before giving up
    max_reminders_per_stack: int = 3  # Don't spam if stack isn't progressing


class StackTriggeredReminder:
    """
    Manages reminders triggered by habit stack completion.
    
    Phase 4.2 Feature: When a user completes a habit in a stack,
    this triggers a reminder for the next habit in the sequence.
    
    This implements the "stack-triggered" reminder type from the
    Phase 4.2 research document.
    
    Example:
        User completes "drink water" (position 0 in stack)
        → System triggers reminder for "take vitamins" (position 1)
        → After delay, if not completed, sends follow-up
    """
    
    def __init__(self, db=None, config: Optional[StackTriggerConfig] = None):
        """
        Initialize stack-triggered reminder manager.
        
        Args:
            db: Database instance
            config: Stack trigger configuration
        """
        self._db = db
        self.config = config or StackTriggerConfig()
        self._stack_engine: Optional[HabitStackingEngine] = None
    
    @property
    def db(self):
        """Get database instance."""
        if self._db is None:
            from tracking_app.database import get_db
            self._db = get_db()
        return self._db
    
    @property
    def stack_engine(self) -> HabitStackingEngine:
        """Get or create the habit stacking engine."""
        if self._stack_engine is None:
            self._stack_engine = HabitStackingEngine()
        return self._stack_engine
    
    def on_habit_completed(
        self,
        habit_id: str,
        user_id: str = "default"
    ) -> Optional[Dict[str, Any]]:
        """
        Handle habit completion event.
        
        Called when a habit is completed. Checks if the habit
        is part of a stack and triggers reminder for next habit.
        
        Args:
            habit_id: ID of the completed habit
            user_id: User who completed the habit
            
        Returns:
            Dict with next habit info and reminder details, or None
        """
        # Find stacks containing this habit
        stacks = self._get_stacks_containing_habit(habit_id, user_id)
        
        if not stacks:
            return None
        
        results = []
        for stack in stacks:
            # Find position of completed habit
            position = self._get_habit_position_in_stack(stack, habit_id)
            
            if position is None:
                continue
            
            # Check if there's a next habit
            next_position = position + 1
            next_item = stack.get_habit_at_position(next_position)
            
            if not next_item:
                # End of stack reached
                results.append({
                    'stack_id': stack.id,
                    'stack_name': stack.name,
                    'completed_position': position,
                    'is_stack_complete': True,
                    'message': f"🎉 You completed the entire '{stack.name}' stack!"
                })
                continue
            
            # Get next habit details
            next_habit = self._get_habit_details(next_item.habit_id)
            
            if not next_habit:
                continue
            
            # Calculate reminder time based on delay
            reminder_time = datetime.now() + timedelta(seconds=next_item.delay_seconds or self.config.delay_after_previous)
            
            # Schedule the reminder
            self._schedule_stack_reminder(
                stack=stack,
                next_habit_id=next_item.habit_id,
                reminder_time=reminder_time,
                user_id=user_id
            )
            
            results.append({
                'stack_id': stack.id,
                'stack_name': stack.name,
                'completed_position': position,
                'is_stack_complete': False,
                'next_habit_id': next_item.habit_id,
                'next_habit_name': next_habit.get('name', 'Unknown'),
                'reminder_time': reminder_time.isoformat(),
                'delay_seconds': next_item.delay_seconds or self.config.delay_after_previous
            })
        
        return results[0] if len(results) == 1 else {'stacks': results}
    
    def _get_stacks_containing_habit(self, habit_id: str, user_id: str) -> List[HabitStack]:
        """Get all stacks that contain a specific habit."""
        user_stacks = self.stack_engine.get_user_stacks(user_id)
        containing = []
        
        for stack in user_stacks:
            for item in stack.items:
                if item.habit_id == habit_id:
                    containing.append(stack)
                    break
        
        return containing
    
    def _get_habit_position_in_stack(self, stack: HabitStack, habit_id: str) -> Optional[int]:
        """Get the position of a habit in a stack."""
        for item in stack.items:
            if item.habit_id == habit_id:
                return item.position_index
        return None
    
    def _get_habit_details(self, habit_id: str) -> Optional[Dict[str, Any]]:
        """Get habit details from database."""
        row = self.db.fetch_one(
            "SELECT id, name, description FROM habits WHERE id = ?",
            (habit_id,)
        )
        return dict(row) if row else None
    
    def _schedule_stack_reminder(
        self,
        stack: HabitStack,
        next_habit_id: str,
        reminder_time: datetime,
        user_id: str
    ) -> None:
        """Schedule a reminder for the next habit in a stack."""
        # Store the pending reminder
        self.db.execute(
            """INSERT INTO stack_reminders 
               (id, stack_id, habit_id, reminder_time, user_id, status, created_at)
               VALUES (?, ?, ?, ?, ?, 'pending', ?)""",
            (
                f"sr_{stack.id}_{next_habit_id}_{datetime.now().timestamp()}",
                stack.id,
                next_habit_id,
                reminder_time.isoformat(),
                user_id,
                datetime.now().isoformat()
            )
        )
        
        logger.info(f"Scheduled stack reminder for habit {next_habit_id} at {reminder_time}")
    
    def get_pending_stack_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all pending stack reminders for a user."""
        rows = self.db.fetch_all(
            """SELECT * FROM stack_reminders 
               WHERE user_id = ? AND status = 'pending' 
               AND reminder_time <= ?""",
            (user_id, datetime.now().isoformat())
        )
        
        return [dict(row) for row in rows]
    
    def mark_reminder_sent(self, reminder_id: str) -> None:
        """Mark a stack reminder as sent."""
        self.db.execute(
            """UPDATE stack_reminders 
               SET status = 'sent', sent_at = ? 
               WHERE id = ?""",
            (datetime.now().isoformat(), reminder_id)
        )
    
    def cancel_stack_reminders(self, stack_id: str, habit_id: str) -> None:
        """Cancel pending reminders for a habit (e.g., if user completes it)."""
        self.db.execute(
            """UPDATE stack_reminders 
               SET status = 'cancelled', cancelled_at = ? 
               WHERE stack_id = ? AND habit_id = ? AND status = 'pending'""",
            (datetime.now().isoformat(), stack_id, habit_id)
        )


class ReminderScheduler:
    """
    Main scheduler class that coordinates all reminder functionality.
    
    Integrates:
    - APScheduler for temporal orchestration
    - SmartScheduler for adaptive timing
    - StreakProtector for streak preservation
    - IntelligentSnoozer for smart snooze behavior
    - StackTriggeredReminder for habit stack chaining
    
    Singleton pattern for Streamlit compatibility.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern for Streamlit compatibility."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, engine: Optional[NotificationEngine] = None):
        """Initialize the reminder scheduler."""
        # Prevent re-initialization
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.engine = engine or get_engine()
        self.smart_scheduler = SmartScheduler(db=self.engine.db)
        self.streak_protector = StreakProtector(db=self.engine.db)
        self.snoozer = IntelligentSnoozer(db=self.engine.db)
        self.stack_reminder = StackTriggeredReminder(db=self.engine.db)
        
        self._scheduler = None
        self._initialized = True
        
        if APSCHEDULER_AVAILABLE:
            self._init_apscheduler()
    
    def _init_apscheduler(self) -> None:
        """Initialize APScheduler with SQLite job store."""
        jobstores = {
            'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
        }
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        
        self._scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            timezone='local'
        )
        
        self._scheduler.start()
        logger.info("APScheduler started")
    
    # ==========================================
    # Schedule Management
    # ==========================================
    
    def schedule_reminder(
        self,
        entity_type: str,
        entity_id: str,
        reminder_time: time,
        days_of_week: Optional[List[int]] = None,
        channels: Optional[List[NotificationChannel]] = None,
        is_smart: bool = False,
        user_id: str = "default"
    ) -> Optional[ReminderSchedule]:
        """
        Schedule a recurring reminder.
        
        Args:
            entity_type: Type of entity (habit, task, goal)
            entity_id: ID of the entity
            reminder_time: Time to send reminder
            days_of_week: Days to send (0=Monday, 6=Sunday), None = every day
            channels: Notification channels to use
            is_smart: Whether to use smart timing
            user_id: User ID for multi-user support
            
        Returns:
            Created ReminderSchedule or None if failed
        """
        # Check for existing schedule
        existing = self.engine.get_reminder_schedule(entity_type, entity_id)
        if existing:
            logger.info(f"Schedule already exists for {entity_type}/{entity_id}")
            return existing
        
        # Convert time to HH:MM string format for engine
        reminder_time_str = reminder_time.strftime("%H:%M")
        
        # Create schedule in database
        schedule = self.engine.create_reminder_schedule(
            entity_type=entity_type,
            entity_id=entity_id,
            reminder_time=reminder_time_str,
            days_of_week=days_of_week,
            channels=channels,
            is_smart=is_smart,
            user_id=user_id
        )
        
        # Add to APScheduler
        if self._scheduler:
            self._add_scheduler_job(schedule)
        
        return schedule
    
    def _add_scheduler_job(self, schedule: ReminderSchedule) -> None:
        """Add a job to APScheduler for a schedule."""
        if not self._scheduler:
            return
        
        job_id = f"reminder_{schedule.id}"
        
        # Parse time
        reminder_time = schedule.get_effective_time()
        if not reminder_time:
            return
        
        # Build cron expression
        day_names = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        
        if schedule.days_of_week:
            cron_days = ','.join(day_names[d] for d in schedule.days_of_week)
        else:
            cron_days = '*'
        
        # Create cron trigger
        trigger = CronTrigger(
            hour=reminder_time.hour,
            minute=reminder_time.minute,
            day_of_week=cron_days,
            timezone='local'
        )
        
        # Add job
        self._scheduler.add_job(
            self._send_reminder,
            trigger=trigger,
            id=job_id,
            args=[schedule.id],
            replace_existing=True
        )
        
        logger.debug(f"Scheduled job {job_id} for {reminder_time} on {cron_days}")
    
    def _send_reminder(self, schedule_id: str) -> None:
        """Send a reminder (called by APScheduler)."""
        row = self.engine.db.fetch_one(
            "SELECT * FROM reminder_schedules WHERE id = ?",
            (schedule_id,)
        )
        
        if not row:
            logger.warning(f"Schedule {schedule_id} not found")
            return
        
        schedule = ReminderSchedule.from_dict(row)
        
        if not schedule.should_trigger_today():
            logger.debug(f"Schedule {schedule_id} not triggered today")
            return
        
        entity_name = self._get_entity_name(
            schedule.entity_type,
            schedule.entity_id
        )
        
        # Check streak protection
        should_send, urgency = self.streak_protector.should_send_streak_reminder(
            schedule.entity_type,
            schedule.entity_id
        )
        
        if should_send:
            # Use escalated message
            streak = self.streak_protector._get_current_streak(
                schedule.entity_type,
                schedule.entity_id
            )
            title, message = self.streak_protector.get_escalated_message(
                urgency, streak, entity_name
            )
        else:
            title = f"Reminder: {entity_name}"
            message = f"Time to complete {entity_name.lower()}"
        
        # Create notification
        notification = self.engine.create_from_template(
            template_id="habit_reminder_smart" if schedule.is_smart else "habit_reminder",
            context={
                "habit_name": entity_name,
                "habit_action": entity_name.lower(),
                "streak": self._get_streak(schedule.entity_type, schedule.entity_id),
                "completion_rate": self._get_completion_rate(
                    schedule.entity_type,
                    schedule.entity_id
                ),
                "custom_title": title,
                "custom_message": message,
            },
            type=NotificationType.HABIT_REMINDER,
            entity_type=schedule.entity_type,
            entity_id=schedule.entity_id,
        )
        
        if notification:
            self.engine.dispatch(
                notification,
                channels=schedule.channels,
                user_id=schedule.user_id
            )
    
    def _get_entity_name(self, entity_type: str, entity_id: str) -> str:
        """Get the name of an entity for notification."""
        if entity_type == "habit":
            row = self.engine.db.fetch_one(
                "SELECT name FROM habits WHERE id = ?",
                (entity_id,)
            )
            return row['name'] if row else "Unknown Habit"
        
        elif entity_type == "task":
            row = self.engine.db.fetch_one(
                "SELECT title FROM tasks WHERE id = ?",
                (entity_id,)
            )
            return row['title'] if row else "Unknown Task"
        
        elif entity_type == "goal":
            row = self.engine.db.fetch_one(
                "SELECT title FROM goals WHERE id = ?",
                (entity_id,)
            )
            return row['title'] if row else "Unknown Goal"
        
        return "Unknown"
    
    def _get_streak(self, entity_type: str, entity_id: str) -> int:
        """Get current streak for an entity."""
        return self.streak_protector._get_current_streak(entity_type, entity_id)
    
    def _get_completion_rate(self, entity_type: str, entity_id: str) -> float:
        """Get completion rate for an entity (0.0 - 1.0)."""
        if entity_type != "habit":
            return 0.0
        
        rows = self.engine.db.fetch_all(
            """SELECT COUNT(*) as total,
                      SUM(CASE WHEN skipped = 0 THEN 1 ELSE 0 END) as completed
               FROM habit_entries 
               WHERE habit_id = ?
               AND entry_date >= date('now', '-30 days')""",
            (entity_id,)
        )
        
        if not rows or rows[0]['total'] == 0:
            return 0.0
        
        return rows[0]['completed'] / rows[0]['total']
    
    def unschedule_reminder(self, entity_type: str, entity_id: str) -> bool:
        """Remove a scheduled reminder."""
        schedule = self.engine.get_reminder_schedule(entity_type, entity_id)
        
        if not schedule:
            return False
        
        if self._scheduler:
            job_id = f"reminder_{schedule.id}"
            self._scheduler.remove_job(job_id)
        
        schedule.enabled = False
        self.engine.update_schedule(schedule)
        
        return True
    
    def snooze_reminder(
        self,
        entity_type: str,
        entity_id: str,
        snooze_minutes: Optional[int] = None
    ) -> Optional[datetime]:
        """Snooze a reminder."""
        schedule = self.engine.get_reminder_schedule(entity_type, entity_id)
        
        if not schedule:
            return None
        
        if not schedule.can_snooze():
            logger.info("Cannot snooze - max snoozes reached")
            return None
        
        new_time = schedule.snooze()
        
        if new_time:
            self.engine.update_schedule(schedule)
            
            if self._scheduler:
                snooze_datetime = datetime.combine(date.today(), new_time)
                
                self._scheduler.add_job(
                    self._send_reminder,
                    trigger=DateTrigger(run_date=snooze_datetime),
                    id=f"snooze_{schedule.id}_{schedule.current_snoozes}",
                    args=[schedule.id]
                )
            
            return datetime.combine(date.today(), new_time)
        
        return None
    
    def load_schedules(self) -> int:
        """Load all active schedules into APScheduler."""
        if not self._scheduler:
            return 0
        
        schedules = self.engine.get_active_schedules()
        
        loaded = 0
        for schedule in schedules:
            self._add_scheduler_job(schedule)
            loaded += 1
        
        logger.info(f"Loaded {loaded} reminder schedules")
        return loaded
    
    # ==========================================
    # One-time Notifications
    # ==========================================
    
    def schedule_notification(
        self,
        notification: Notification,
        scheduled_for: datetime
    ) -> bool:
        """Schedule a one-time notification."""
        if not self._scheduler:
            return False
        
        notification.status = NotificationStatus.SCHEDULED
        notification.scheduled_for = scheduled_for
        
        self._scheduler.add_job(
            self._send_scheduled_notification,
            trigger=DateTrigger(run_date=scheduled_for),
            id=f"notification_{notification.id}",
            args=[notification.id],
            replace_existing=True
        )
        
        return True
    
    def _send_scheduled_notification(self, notification_id: str) -> None:
        """Send a scheduled notification (called by APScheduler)."""
        notification = self.engine.get_notification(notification_id)
        
        if not notification:
            logger.warning(f"Notification {notification_id} not found")
            return
        
        self.engine.dispatch(notification)
    
    # ==========================================
    # Utility Methods
    # ==========================================
    
    def get_next_run_time(self, entity_type: str, entity_id: str) -> Optional[datetime]:
        """Get the next scheduled run time for a reminder."""
        schedule = self.engine.get_reminder_schedule(entity_type, entity_id)
        
        if not schedule or not schedule.enabled:
            return None
        
        if not self._scheduler:
            return None
        
        job_id = f"reminder_{schedule.id}"
        job = self._scheduler.get_job(job_id)
        
        if job and job.next_run_time:
            return job.next_run_time
        
        return None
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all scheduled jobs."""
        if not self._scheduler:
            return []
        
        jobs = []
        for job in self._scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger),
            })
        
        return jobs
    
    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self._scheduler:
            self._scheduler.shutdown()
            logger.info("Scheduler shutdown")


def get_scheduler() -> ReminderScheduler:
    """Get the global scheduler instance."""
    return ReminderScheduler()