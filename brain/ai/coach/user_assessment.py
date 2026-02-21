"""
Brain AI Coach - User Assessment

Evaluates user state across multiple dimensions for the Digital Coach.
Provides burnout risk, streak health, goal progress, and engagement metrics.

Usage:
    from brain.ai.coach.user_assessment import UserAssessment, UserState
    
    assessment = UserAssessment()
    state = assessment.assess(user_data)
    print(state.burnout_risk)  # 0-100
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum


class RiskLevel(Enum):
    """Risk level classification."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class EngagementLevel(Enum):
    """User engagement classification."""
    DORMANT = "dormant"      # No activity for extended period
    LOW = "low"              # Minimal interaction
    NORMAL = "normal"        # Regular usage
    HIGH = "high"            # Active daily usage
    INTENSIVE = "intensive"  # Heavy usage, potential overuse


@dataclass
class UserState:
    """
    Represents the current state of the user.
    
    Attributes:
        burnout_risk: Risk score (0-100)
        burnout_level: Categorical risk level
        streak_health: Overall streak consistency (0-100)
        goal_progress: Goal completion rate (0-100)
        engagement_level: User engagement classification
        last_active: When user was last active
        habits_assessment: Per-habit assessment data
        mood_trend: Trend in mood over recent period
        sleep_trend: Trend in sleep quality
        task_completion_rate: Recent task completion percentage
        warnings: List of active warnings
        recommendations: List of recommendation keys
    """
    burnout_risk: int = 0
    burnout_level: RiskLevel = RiskLevel.LOW
    streak_health: int = 100
    goal_progress: int = 0
    engagement_level: EngagementLevel = EngagementLevel.NORMAL
    last_active: Optional[datetime] = None
    habits_assessment: Dict[str, Any] = field(default_factory=dict)
    mood_trend: str = "stable"  # "improving", "declining", "stable"
    sleep_trend: str = "stable"
    task_completion_rate: float = 0.0
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "burnout_risk": self.burnout_risk,
            "burnout_level": self.burnout_level.value,
            "streak_health": self.streak_health,
            "goal_progress": self.goal_progress,
            "engagement_level": self.engagement_level.value,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "habits_assessment": self.habits_assessment,
            "mood_trend": self.mood_trend,
            "sleep_trend": self.sleep_trend,
            "task_completion_rate": self.task_completion_rate,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "assessed_at": self.assessed_at.isoformat()
        }


class UserAssessment:
    """
    Evaluates user state across multiple dimensions.
    
    Assessments include:
    - Burnout risk (sleep, mood, task completion)
    - Streak health (habit consistency)
    - Goal progress (on-track status)
    - Engagement level (activity frequency)
    
    Usage:
        assessment = UserAssessment()
        state = assessment.assess(user_data)
    """
    
    # Thresholds for burnout calculation
    SLEEP_MIN_THRESHOLD = 6.0  # Hours
    SLEEP_OPTIMAL = 7.5
    TASK_COMPLETION_WARNING = 0.5  # 50%
    STREAK_BREAK_THRESHOLD = 2  # Days missed
    
    def __init__(self, lookback_days: int = 14):
        """
        Initialize the assessment engine.
        
        Args:
            lookback_days: Number of days to analyze
        """
        self.lookback_days = lookback_days
    
    def assess(self, user_data: Dict[str, Any]) -> UserState:
        """
        Perform comprehensive user assessment.
        
        Args:
            user_data: Dictionary containing user tracking data
                - habits: List of habit data
                - tasks: List of task data
                - health: Health entries (sleep, mood)
                - goals: Goal progress data
                - activity_log: Login/usage timestamps
                
        Returns:
            UserState with assessment results
        """
        state = UserState()
        
        # Assess burnout risk
        state.burnout_risk = self._calculate_burnout_risk(user_data)
        state.burnout_level = self._classify_risk(state.burnout_risk)
        
        # Assess streak health
        state.streak_health = self._calculate_streak_health(user_data)
        
        # Assess goal progress
        state.goal_progress = self._calculate_goal_progress(user_data)
        
        # Assess engagement
        state.engagement_level = self._assess_engagement(user_data)
        state.last_active = self._get_last_active(user_data)
        
        # Assess habits individually
        state.habits_assessment = self._assess_habits(user_data)
        
        # Calculate trends
        state.mood_trend = self._calculate_mood_trend(user_data)
        state.sleep_trend = self._calculate_sleep_trend(user_data)
        state.task_completion_rate = self._calculate_task_completion(user_data)
        
        # Generate warnings and recommendations
        state.warnings = self._generate_warnings(state)
        state.recommendations = self._generate_recommendations(state)
        
        return state
    
    def _calculate_burnout_risk(self, user_data: Dict[str, Any]) -> int:
        """
        Calculate burnout risk score (0-100).
        
        Factors:
        - Sleep quality and duration (40%)
        - Task completion rate (25%)
        - Mood trend (20%)
        - Streak breaks (15%)
        """
        score = 0
        
        # Sleep factor (40 points max)
        sleep_data = user_data.get("health", {}).get("sleep", [])
        if sleep_data:
            avg_sleep = self._average(sleep_data[-7:]) if len(sleep_data) >= 7 else self._average(sleep_data)
            if avg_sleep < self.SLEEP_MIN_THRESHOLD:
                score += 40
            elif avg_sleep < self.SLEEP_OPTIMAL:
                score += 20
            elif avg_sleep >= self.SLEEP_OPTIMAL:
                score -= 10  # Bonus for good sleep
        
        # Task completion factor (25 points max)
        tasks = user_data.get("tasks", [])
        if tasks:
            completion_rate = self._calculate_task_completion(user_data)
            if completion_rate < 0.5:
                score += 25
            elif completion_rate < 0.7:
                score += 10
        
        # Mood factor (20 points max)
        mood_data = user_data.get("health", {}).get("mood", [])
        if mood_data:
            avg_mood = self._average(mood_data[-7:]) if len(mood_data) >= 7 else self._average(mood_data)
            if avg_mood < 3:  # Assuming 1-5 scale
                score += 20
            elif avg_mood < 4:
                score += 10
        
        # Streak break factor (15 points max)
        habits = user_data.get("habits", [])
        streak_breaks = sum(1 for h in habits if h.get("streak_broken_recently", False))
        if streak_breaks >= 3:
            score += 15
        elif streak_breaks >= 1:
            score += 8
        
        return min(100, max(0, score))
    
    def _classify_risk(self, score: int) -> RiskLevel:
        """Classify numeric risk score into category."""
        if score >= 71:
            return RiskLevel.CRITICAL
        elif score >= 51:
            return RiskLevel.HIGH
        elif score >= 31:
            return RiskLevel.MODERATE
        return RiskLevel.LOW
    
    def _calculate_streak_health(self, user_data: Dict[str, Any]) -> int:
        """
        Calculate overall streak health (0-100).
        
        Based on:
        - Number of active streaks
        - Average streak length
        - Recent streak breaks
        """
        habits = user_data.get("habits", [])
        if not habits:
            return 100  # No habits = no streak issues
        
        total_habits = len(habits)
        active_streaks = sum(1 for h in habits if h.get("streak", 0) > 0)
        avg_streak = sum(h.get("streak", 0) for h in habits) / total_habits
        recent_breaks = sum(1 for h in habits if h.get("streak_broken_recently", False))
        
        # Calculate health score
        active_ratio = active_streaks / total_habits
        streak_bonus = min(avg_streak / 30, 1) * 20  # Up to 20 points for long streaks
        break_penalty = recent_breaks * 10
        
        health = int((active_ratio * 80) + streak_bonus - break_penalty)
        return min(100, max(0, health))
    
    def _calculate_goal_progress(self, user_data: Dict[str, Any]) -> int:
        """Calculate overall goal progress percentage."""
        goals = user_data.get("goals", [])
        if not goals:
            return 0
        
        total_progress = sum(g.get("progress", 0) for g in goals)
        return int(total_progress / len(goals))
    
    def _assess_engagement(self, user_data: Dict[str, Any]) -> EngagementLevel:
        """
        Assess user engagement level.
        
        Based on login frequency and feature usage.
        """
        activity_log = user_data.get("activity_log", [])
        if not activity_log:
            return EngagementLevel.DORMANT
        
        # Count activity days in lookback period
        recent_activity = [
            a for a in activity_log
            if datetime.fromisoformat(a.get("timestamp", "2000-01-01")) > 
               datetime.now() - timedelta(days=self.lookback_days)
        ]
        
        unique_days = len(set(
            datetime.fromisoformat(a.get("timestamp", "")).date()
            for a in recent_activity
        ))
        
        # Classify
        daily_ratio = unique_days / self.lookback_days
        
        if daily_ratio == 0:
            return EngagementLevel.DORMANT
        elif daily_ratio < 0.3:
            return EngagementLevel.LOW
        elif daily_ratio < 0.7:
            return EngagementLevel.NORMAL
        elif daily_ratio < 0.9:
            return EngagementLevel.HIGH
        return EngagementLevel.INTENSIVE
    
    def _get_last_active(self, user_data: Dict[str, Any]) -> Optional[datetime]:
        """Get the timestamp of last user activity."""
        activity_log = user_data.get("activity_log", [])
        if not activity_log:
            return None
        
        timestamps = [
            datetime.fromisoformat(a.get("timestamp", "2000-01-01"))
            for a in activity_log
        ]
        return max(timestamps) if timestamps else None
    
    def _assess_habits(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess each habit individually."""
        habits = user_data.get("habits", [])
        assessment = {}
        
        for habit in habits:
            habit_id = habit.get("id", "unknown")
            streak = habit.get("streak", 0)
            best_streak = habit.get("best_streak", 0)
            completion_rate = habit.get("completion_rate", 0)
            
            # Determine habit health
            if streak >= 21:
                health = "established"
            elif streak >= 7:
                health = "developing"
            elif streak > 0:
                health = "building"
            else:
                health = "needs_attention"
            
            assessment[habit_id] = {
                "name": habit.get("name", "Unknown"),
                "streak": streak,
                "best_streak": best_streak,
                "completion_rate": completion_rate,
                "health": health,
                "needs_intervention": streak == 0 or completion_rate < 0.5
            }
        
        return assessment
    
    def _calculate_mood_trend(self, user_data: Dict[str, Any]) -> str:
        """Calculate mood trend over recent period."""
        mood_data = user_data.get("health", {}).get("mood", [])
        if len(mood_data) < 7:
            return "stable"
        
        recent = mood_data[-7:]
        previous = mood_data[-14:-7] if len(mood_data) >= 14 else mood_data[:-7]
        
        if not previous:
            return "stable"
        
        recent_avg = self._average(recent)
        previous_avg = self._average(previous)
        
        diff = recent_avg - previous_avg
        if diff > 0.3:
            return "improving"
        elif diff < -0.3:
            return "declining"
        return "stable"
    
    def _calculate_sleep_trend(self, user_data: Dict[str, Any]) -> str:
        """Calculate sleep trend over recent period."""
        sleep_data = user_data.get("health", {}).get("sleep", [])
        if len(sleep_data) < 7:
            return "stable"
        
        recent = sleep_data[-7:]
        previous = sleep_data[-14:-7] if len(sleep_data) >= 14 else sleep_data[:-7]
        
        if not previous:
            return "stable"
        
        recent_avg = self._average(recent)
        previous_avg = self._average(previous)
        
        diff = recent_avg - previous_avg
        if diff > 0.5:
            return "improving"
        elif diff < -0.5:
            return "declining"
        return "stable"
    
    def _calculate_task_completion(self, user_data: Dict[str, Any]) -> float:
        """Calculate recent task completion rate."""
        tasks = user_data.get("tasks", [])
        if not tasks:
            return 0.0
        
        completed = sum(1 for t in tasks if t.get("completed", False))
        return completed / len(tasks)
    
    def _generate_warnings(self, state: UserState) -> List[str]:
        """Generate warning messages based on state."""
        warnings = []
        
        if state.burnout_level == RiskLevel.CRITICAL:
            warnings.append("critical_burnout_risk")
        elif state.burnout_level == RiskLevel.HIGH:
            warnings.append("high_burnout_risk")
        
        if state.streak_health < 50:
            warnings.append("low_streak_health")
        
        if state.mood_trend == "declining":
            warnings.append("declining_mood")
        
        if state.sleep_trend == "declining":
            warnings.append("declining_sleep")
        
        if state.engagement_level == EngagementLevel.DORMANT:
            warnings.append("user_dormant")
        
        return warnings
    
    def _generate_recommendations(self, state: UserState) -> List[str]:
        """Generate recommendation keys based on state."""
        recommendations = []
        
        if state.burnout_risk >= 50:
            recommendations.append("reduce_load")
            recommendations.append("prioritize_rest")
        
        if state.streak_health < 70:
            recommendations.append("focus_on_consistency")
        
        if state.mood_trend == "declining":
            recommendations.append("check_in_on_mood")
        
        if state.sleep_trend == "declining":
            recommendations.append("improve_sleep_hygiene")
        
        if state.engagement_level in [EngagementLevel.DORMANT, EngagementLevel.LOW]:
            recommendations.append("gentle_reengagement")
        
        return recommendations
    
    def _average(self, values: List[float]) -> float:
        """Calculate average of a list of values."""
        if not values:
            return 0.0
        return sum(values) / len(values)