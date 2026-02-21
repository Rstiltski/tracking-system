"""
Insight Generator Module

Generates structured, actionable insights from user tracking data.
Uses patterns identified from research (perfice, fitbaus) for NLG templates.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
import statistics


class InsightType(Enum):
    """Types of insights that can be generated."""
    CORRELATION = "correlation"
    PATTERN = "pattern"
    TREND = "trend"
    ACHIEVEMENT = "achievement"
    WARNING = "warning"
    RECOMMENDATION = "recommendation"
    MILESTONE = "milestone"
    ANOMALY = "anomaly"


class InsightPriority(Enum):
    """Priority levels for insights."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Insight:
    """Represents a single insight."""
    id: str
    type: InsightType
    priority: InsightPriority
    title: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    dismissed: bool = False
    action_taken: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "message": self.message,
            "details": self.details,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "dismissed": self.dismissed,
            "action_taken": self.action_taken
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Insight":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            type=InsightType(data["type"]),
            priority=InsightPriority(data["priority"]),
            title=data["title"],
            message=data["message"],
            details=data.get("details", {}),
            recommendations=data.get("recommendations", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            dismissed=data.get("dismissed", False),
            action_taken=data.get("action_taken", False)
        )


@dataclass
class CorrelationInsight(Insight):
    """Insight about correlations between metrics."""
    metric_x: str = ""
    metric_y: str = ""
    correlation_coefficient: float = 0.0
    lag_days: int = 0
    sample_size: int = 0
    confidence: float = 0.0


@dataclass
class TrendInsight(Insight):
    """Insight about trends in a metric."""
    metric: str = ""
    direction: str = "stable"  # "improving", "declining", "stable"
    change_percent: float = 0.0
    period_days: int = 7
    previous_value: float = 0.0
    current_value: float = 0.0


@dataclass
class PatternInsight(Insight):
    """Insight about recurring patterns."""
    pattern_type: str = ""  # "weekly", "daily", "monthly"
    pattern_description: str = ""
    occurrences: int = 0
    consistency: float = 0.0


class InsightTemplates:
    """Natural language templates for insights (inspired by perfice)."""
    
    # Correlation templates
    CORRELATION_POSITIVE = "{x} is positively correlated with {y} (r={coef:.2f}). When {x} increases, {y} tends to increase as well."
    CORRELATION_NEGATIVE = "{x} is negatively correlated with {y} (r={coef:.2f}). When {x} increases, {y} tends to decrease."
    CORRELATION_LAGGED = "{x} {lag} days ago predicts {y} (r={coef:.2f}). Consider focusing on {x} today to improve {y} in {lag} days."
    
    # Trend templates
    TREND_IMPROVING = "Your {metric} has improved by {change:.1f}% over the last {period} days. Keep up the great work!"
    TREND_DECLINING = "Your {metric} has declined by {change:.1f}% over the last {period} days. Consider focusing on this area."
    TREND_STABLE = "Your {metric} has remained stable over the last {period} days."
    
    # Pattern templates
    PATTERN_WEEKLY = "You tend to have higher {metric} on {day}s. Consider scheduling important tasks on these days."
    PATTERN_DAILY = "Your {metric} is typically highest around {time}. This might be your optimal time for related activities."
    
    # Achievement templates
    ACHIEVEMENT_STREAK = "🎉 Amazing! You've maintained a {streak}-day streak for {habit}!"
    ACHIEVEMENT_GOAL = "🎯 Congratulations! You've reached your goal of {goal}!"
    ACHIEVEMENT_MILESTONE = "🏆 Milestone reached: {milestone}!"
    
    # Warning templates
    WARNING_STREAK_RISK = "⚠️ Your {streak}-day streak for {habit} is at risk! Don't forget to check in today."
    WARNING_BURNOUT = "⚠️ You've been pushing hard lately. Consider taking a rest day to prevent burnout."
    WARNING_DECLINE = "⚠️ {metric} has been declining for {days} consecutive days. Time to refocus?"
    
    # Recommendation templates
    RECOMMENDATION_HABIT = "Consider adding '{habit}' to your routine. Users with similar goals have found it beneficial."
    RECOMMENDATION_TIMING = "Based on your patterns, {time} might be a better time for {activity}."
    RECOMMENDATION_RECOVERY = "Your recovery metrics suggest taking it easy today. How about a light walk instead of intense exercise?"


class InsightGenerator:
    """Generates structured insights from tracking data."""
    
    def __init__(self):
        self.templates = InsightTemplates()
        self._insight_counter = 0
    
    def _generate_id(self, prefix: str = "insight") -> str:
        """Generate a unique insight ID."""
        self._insight_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}_{timestamp}_{self._insight_counter}"
    
    def generate_correlation_insight(
        self,
        metric_x: str,
        metric_y: str,
        coefficient: float,
        lag_days: int = 0,
        sample_size: int = 0,
        p_value: Optional[float] = None
    ) -> CorrelationInsight:
        """Generate an insight about a correlation between two metrics."""
        
        # Determine priority based on strength and significance
        strength = abs(coefficient)
        if strength > 0.7:
            priority = InsightPriority.HIGH
        elif strength > 0.5:
            priority = InsightPriority.MEDIUM
        else:
            priority = InsightPriority.LOW
        
        # Generate message based on correlation direction and lag
        if lag_days > 0:
            message = self.templates.CORRELATION_LAGGED.format(
                x=metric_x,
                y=metric_y,
                lag=lag_days,
                coef=coefficient
            )
        elif coefficient > 0:
            message = self.templates.CORRELATION_POSITIVE.format(
                x=metric_x,
                y=metric_y,
                coef=coefficient
            )
        else:
            message = self.templates.CORRELATION_NEGATIVE.format(
                x=metric_x,
                y=metric_y,
                coef=abs(coefficient)
            )
        
        # Generate recommendations
        recommendations = self._generate_correlation_recommendations(
            metric_x, metric_y, coefficient, lag_days
        )
        
        return CorrelationInsight(
            id=self._generate_id("corr"),
            type=InsightType.CORRELATION,
            priority=priority,
            title=f"Correlation: {metric_x} ↔ {metric_y}",
            message=message,
            details={
                "strength": "strong" if strength > 0.7 else "moderate" if strength > 0.5 else "weak",
                "direction": "positive" if coefficient > 0 else "negative"
            },
            recommendations=recommendations,
            metric_x=metric_x,
            metric_y=metric_y,
            correlation_coefficient=coefficient,
            lag_days=lag_days,
            sample_size=sample_size,
            confidence=1 - (p_value or 0.5)
        )
    
    def _generate_correlation_recommendations(
        self,
        metric_x: str,
        metric_y: str,
        coefficient: float,
        lag_days: int
    ) -> List[str]:
        """Generate actionable recommendations based on correlation."""
        recommendations = []
        
        if coefficient > 0:
            if lag_days > 0:
                recommendations.append(
                    f"Focus on improving {metric_x} today to see benefits in {metric_y} in {lag_days} days."
                )
            else:
                recommendations.append(
                    f"Consider stacking {metric_x} with {metric_y} for compounded benefits."
                )
        else:
            if lag_days > 0:
                recommendations.append(
                    f"Be mindful that high {metric_x} may negatively impact {metric_y} after {lag_days} days."
                )
            else:
                recommendations.append(
                    f"Monitor the trade-off between {metric_x} and {metric_y} in your routine."
                )
        
        return recommendations
    
    def generate_trend_insight(
        self,
        metric: str,
        values: List[float],
        period_days: int = 7
    ) -> Optional[TrendInsight]:
        """Generate an insight about a trend in a metric."""
        
        if len(values) < 2:
            return None
        
        # Calculate trend
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        prev_avg = statistics.mean(first_half) if first_half else 0
        curr_avg = statistics.mean(second_half) if second_half else 0
        
        if prev_avg == 0:
            change_percent = 100 if curr_avg > 0 else 0
        else:
            change_percent = ((curr_avg - prev_avg) / prev_avg) * 100
        
        # Determine direction
        if change_percent > 5:
            direction = "improving"
        elif change_percent < -5:
            direction = "declining"
        else:
            direction = "stable"
        
        # Generate message
        if direction == "improving":
            message = self.templates.TREND_IMPROVING.format(
                metric=metric,
                change=abs(change_percent),
                period=period_days
            )
            priority = InsightPriority.LOW
        elif direction == "declining":
            message = self.templates.TREND_DECLINING.format(
                metric=metric,
                change=abs(change_percent),
                period=period_days
            )
            priority = InsightPriority.MEDIUM
        else:
            message = self.templates.TREND_STABLE.format(
                metric=metric,
                period=period_days
            )
            priority = InsightPriority.LOW
        
        return TrendInsight(
            id=self._generate_id("trend"),
            type=InsightType.TREND,
            priority=priority,
            title=f"Trend: {metric} {direction}",
            message=message,
            details={"direction": direction},
            recommendations=self._generate_trend_recommendations(metric, direction, change_percent),
            metric=metric,
            direction=direction,
            change_percent=change_percent,
            period_days=period_days,
            previous_value=prev_avg,
            current_value=curr_avg
        )
    
    def _generate_trend_recommendations(
        self,
        metric: str,
        direction: str,
        change_percent: float
    ) -> List[str]:
        """Generate recommendations based on trend."""
        recommendations = []
        
        if direction == "declining":
            recommendations.append(f"Consider reviewing your {metric} habits and identifying blockers.")
            recommendations.append("Set a small, achievable goal to get back on track.")
        elif direction == "improving":
            recommendations.append("Keep up the momentum! Consider increasing your target slightly.")
        
        return recommendations
    
    def generate_pattern_insight(
        self,
        metric: str,
        pattern_type: str,
        pattern_data: Dict[str, Any]
    ) -> Optional[PatternInsight]:
        """Generate an insight about a recurring pattern."""
        
        if pattern_type == "weekly":
            best_day = pattern_data.get("best_day", "Monday")
            occurrences = pattern_data.get("occurrences", 0)
            consistency = pattern_data.get("consistency", 0)
            
            message = self.templates.PATTERN_WEEKLY.format(
                metric=metric,
                day=best_day
            )
            
            return PatternInsight(
                id=self._generate_id("pattern"),
                type=InsightType.PATTERN,
                priority=InsightPriority.LOW,
                title=f"Weekly Pattern: {metric}",
                message=message,
                details={"best_day": best_day},
                recommendations=[
                    f"Schedule important {metric}-related tasks on {best_day}s.",
                    f"Use {best_day}s to maximize your {metric} progress."
                ],
                pattern_type="weekly",
                pattern_description=f"Best day: {best_day}",
                occurrences=occurrences,
                consistency=consistency
            )
        
        elif pattern_type == "daily":
            best_time = pattern_data.get("best_time", "morning")
            occurrences = pattern_data.get("occurrences", 0)
            consistency = pattern_data.get("consistency", 0)
            
            message = self.templates.PATTERN_DAILY.format(
                metric=metric,
                time=best_time
            )
            
            return PatternInsight(
                id=self._generate_id("pattern"),
                type=InsightType.PATTERN,
                priority=InsightPriority.LOW,
                title=f"Daily Pattern: {metric}",
                message=message,
                details={"best_time": best_time},
                recommendations=[
                    f"Consider doing {metric}-related activities around {best_time}.",
                    f"Protect your {best_time} time block for maximum productivity."
                ],
                pattern_type="daily",
                pattern_description=f"Best time: {best_time}",
                occurrences=occurrences,
                consistency=consistency
            )
        
        return None
    
    def generate_achievement_insight(
        self,
        achievement_type: str,
        data: Dict[str, Any]
    ) -> Optional[Insight]:
        """Generate an achievement celebration insight."""
        
        if achievement_type == "streak":
            streak = data.get("streak", 0)
            habit = data.get("habit", "your habit")
            
            message = self.templates.ACHIEVEMENT_STREAK.format(
                streak=streak,
                habit=habit
            )
            
            return Insight(
                id=self._generate_id("achieve"),
                type=InsightType.ACHIEVEMENT,
                priority=InsightPriority.HIGH,
                title=f"🎉 {streak}-Day Streak!",
                message=message,
                details={"streak": streak, "habit": habit},
                recommendations=["Keep the momentum going!"]
            )
        
        elif achievement_type == "goal":
            goal = data.get("goal", "your goal")
            
            message = self.templates.ACHIEVEMENT_GOAL.format(goal=goal)
            
            return Insight(
                id=self._generate_id("achieve"),
                type=InsightType.ACHIEVEMENT,
                priority=InsightPriority.HIGH,
                title=f"🎯 Goal Achieved!",
                message=message,
                details={"goal": goal},
                recommendations=["Set a new goal to continue your progress!"]
            )
        
        return None
    
    def generate_warning_insight(
        self,
        warning_type: str,
        data: Dict[str, Any]
    ) -> Optional[Insight]:
        """Generate a warning insight."""
        
        if warning_type == "streak_risk":
            streak = data.get("streak", 0)
            habit = data.get("habit", "your habit")
            
            message = self.templates.WARNING_STREAK_RISK.format(
                streak=streak,
                habit=habit
            )
            
            return Insight(
                id=self._generate_id("warn"),
                type=InsightType.WARNING,
                priority=InsightPriority.HIGH,
                title="⚠️ Streak at Risk!",
                message=message,
                details={"streak": streak, "habit": habit},
                recommendations=[
                    f"Complete {habit} today to maintain your streak!",
                    "Set a reminder if needed."
                ],
                expires_at=datetime.now() + timedelta(hours=12)
            )
        
        elif warning_type == "burnout":
            message = self.templates.WARNING_BURNOUT
            
            return Insight(
                id=self._generate_id("warn"),
                type=InsightType.WARNING,
                priority=InsightPriority.URGENT,
                title="⚠️ Burnout Risk Detected",
                message=message,
                details=data,
                recommendations=[
                    "Take a rest day or do a lighter version of your routine.",
                    "Prioritize sleep and recovery.",
                    "Consider reducing your daily targets temporarily."
                ]
            )
        
        elif warning_type == "decline":
            metric = data.get("metric", "a metric")
            days = data.get("days", 3)
            
            message = self.templates.WARNING_DECLINE.format(
                metric=metric,
                days=days
            )
            
            return Insight(
                id=self._generate_id("warn"),
                type=InsightType.WARNING,
                priority=InsightPriority.MEDIUM,
                title=f"⚠️ {metric} Declining",
                message=message,
                details=data,
                recommendations=[
                    f"Review your recent {metric} patterns.",
                    "Identify any obstacles and address them.",
                    "Set a small goal to rebuild momentum."
                ]
            )
        
        return None
    
    def generate_recommendation(
        self,
        recommendation_type: str,
        data: Dict[str, Any]
    ) -> Optional[Insight]:
        """Generate a proactive recommendation insight."""
        
        if recommendation_type == "habit":
            habit = data.get("habit", "meditation")
            
            message = self.templates.RECOMMENDATION_HABIT.format(habit=habit)
            
            return Insight(
                id=self._generate_id("rec"),
                type=InsightType.RECOMMENDATION,
                priority=InsightPriority.LOW,
                title=f"💡 Suggestion: Try {habit}",
                message=message,
                details=data,
                recommendations=[
                    f"Start with just 2 minutes of {habit}.",
                    "Attach it to an existing habit for better consistency."
                ]
            )
        
        elif recommendation_type == "timing":
            time = data.get("time", "morning")
            activity = data.get("activity", "exercise")
            
            message = self.templates.RECOMMENDATION_TIMING.format(
                time=time,
                activity=activity
            )
            
            return Insight(
                id=self._generate_id("rec"),
                type=InsightType.RECOMMENDATION,
                priority=InsightPriority.LOW,
                title=f"💡 Timing Suggestion",
                message=message,
                details=data,
                recommendations=[
                    f"Try shifting {activity} to {time}.",
                    "Monitor how the change affects your consistency."
                ]
            )
        
        return None
    
    def generate_all_insights(
        self,
        user_data: Dict[str, Any],
        correlations: List[Dict[str, Any]] = None,
        trends: Dict[str, List[float]] = None,
        patterns: Dict[str, Dict[str, Any]] = None
    ) -> List[Insight]:
        """Generate all applicable insights from user data."""
        
        insights = []
        
        # Process correlations
        if correlations:
            for corr in correlations:
                insight = self.generate_correlation_insight(
                    metric_x=corr.get("metric_x", ""),
                    metric_y=corr.get("metric_y", ""),
                    coefficient=corr.get("coefficient", 0),
                    lag_days=corr.get("lag_days", 0),
                    sample_size=corr.get("sample_size", 0),
                    p_value=corr.get("p_value")
                )
                if insight:
                    insights.append(insight)
        
        # Process trends
        if trends:
            for metric, values in trends.items():
                insight = self.generate_trend_insight(
                    metric=metric,
                    values=values,
                    period_days=len(values)
                )
                if insight:
                    insights.append(insight)
        
        # Process patterns
        if patterns:
            for metric, pattern_data in patterns.items():
                pattern_type = pattern_data.get("type", "weekly")
                insight = self.generate_pattern_insight(
                    metric=metric,
                    pattern_type=pattern_type,
                    pattern_data=pattern_data
                )
                if insight:
                    insights.append(insight)
        
        # Sort by priority
        priority_order = {
            InsightPriority.URGENT: 0,
            InsightPriority.HIGH: 1,
            InsightPriority.MEDIUM: 2,
            InsightPriority.LOW: 3
        }
        insights.sort(key=lambda i: priority_order.get(i.priority, 4))
        
        return insights


# Convenience function
def generate_insights(
    user_data: Dict[str, Any],
    correlations: List[Dict[str, Any]] = None,
    trends: Dict[str, List[float]] = None,
    patterns: Dict[str, Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Generate insights and return as list of dictionaries."""
    generator = InsightGenerator()
    insights = generator.generate_all_insights(user_data, correlations, trends, patterns)
    return [i.to_dict() for i in insights]