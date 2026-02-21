"""
Brain AI Weekly Summary - Automated Weekly Summary Generation

Generates weekly summaries of user progress, insights, and recommendations
using AI analysis.

Usage:
    from brain.ai.weekly_summary import WeeklySummaryGenerator
    
    generator = WeeklySummaryGenerator()
    summary = generator.generate()
    
    print(summary.overview)
    print(summary.recommendations)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import logging

from brain.ai.integration import BrainIntegration, get_integration
from brain.ai.assistant import AIAssistant
from brain.ai.models import ProviderConfig, AIProvider, GenerationResult


logger = logging.getLogger(__name__)


@dataclass
class HabitSummary:
    """Summary of habit performance."""
    name: str
    streak: int
    best_streak: int
    completion_rate: float
    status: str  # "thriving", "stable", "needs_attention"
    trend: str  # "improving", "declining", "stable"


@dataclass
class TaskSummary:
    """Summary of task completion."""
    total: int
    completed: int
    completion_rate: float
    overdue: int
    categories: Dict[str, int]


@dataclass
class GoalSummary:
    """Summary of goal progress."""
    name: str
    progress: float
    status: str  # "on_track", "behind", "completed"
    days_remaining: Optional[int]


@dataclass
class HealthSummary:
    """Summary of health metrics."""
    avg_sleep: Optional[float]
    sleep_trend: str
    avg_mood: Optional[float]
    mood_trend: str
    alerts: List[str]


@dataclass
class WeeklySummary:
    """Complete weekly summary."""
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    
    # Summary sections
    overview: str
    highlights: List[str]
    habit_summaries: List[HabitSummary]
    task_summary: TaskSummary
    goal_summaries: List[GoalSummary]
    health_summary: HealthSummary
    
    # AI-generated content
    insights: List[str]
    recommendations: List[str]
    encouragement: str
    
    # Metadata
    score: float  # Overall weekly score 0-100
    comparison: Optional[str] = None  # Comparison to previous week
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "generated_at": self.generated_at.isoformat(),
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "overview": self.overview,
            "highlights": self.highlights,
            "habits": [
                {
                    "name": h.name,
                    "streak": h.streak,
                    "best_streak": h.best_streak,
                    "completion_rate": h.completion_rate,
                    "status": h.status,
                    "trend": h.trend
                }
                for h in self.habit_summaries
            ],
            "tasks": {
                "total": self.task_summary.total,
                "completed": self.task_summary.completed,
                "completion_rate": self.task_summary.completion_rate,
                "overdue": self.task_summary.overdue,
                "categories": self.task_summary.categories
            },
            "goals": [
                {
                    "name": g.name,
                    "progress": g.progress,
                    "status": g.status,
                    "days_remaining": g.days_remaining
                }
                for g in self.goal_summaries
            ],
            "health": {
                "avg_sleep": self.health_summary.avg_sleep,
                "sleep_trend": self.health_summary.sleep_trend,
                "avg_mood": self.health_summary.avg_mood,
                "mood_trend": self.health_summary.mood_trend,
                "alerts": self.health_summary.alerts
            },
            "insights": self.insights,
            "recommendations": self.recommendations,
            "encouragement": self.encouragement,
            "score": self.score,
            "comparison": self.comparison
        }


class WeeklySummaryGenerator:
    """
    Generates weekly summaries using AI analysis.
    
    Features:
    - Comprehensive data gathering from all modules
    - AI-powered insight generation
    - Personalized recommendations
    - Progress tracking and scoring
    
    Usage:
        generator = WeeklySummaryGenerator()
        summary = generator.generate()
    """
    
    def __init__(
        self,
        integration: Optional[BrainIntegration] = None,
        assistant: Optional[AIAssistant] = None
    ):
        """
        Initialize the summary generator.
        
        Args:
            integration: BrainIntegration instance for data access
            assistant: AIAssistant for AI-powered analysis
        """
        self._integration = integration
        self._assistant = assistant
    
    @property
    def integration(self) -> BrainIntegration:
        """Get the brain integration."""
        if self._integration is None:
            self._integration = get_integration()
        return self._integration
    
    @property
    def assistant(self) -> AIAssistant:
        """Get the AI assistant."""
        if self._assistant is None:
            self._assistant = AIAssistant()
        return self._assistant
    
    def generate(
        self,
        user_id: str = "default",
        include_ai_insights: bool = True
    ) -> WeeklySummary:
        """
        Generate a weekly summary.
        
        Args:
            user_id: User identifier
            include_ai_insights: Whether to include AI-generated insights
            
        Returns:
            WeeklySummary object
        """
        now = datetime.now()
        period_start = now - timedelta(days=7)
        
        # Gather data
        context = self._gather_context(user_id)
        
        # Build summaries
        habit_summaries = self._build_habit_summaries(context)
        task_summary = self._build_task_summary(context)
        goal_summaries = self._build_goal_summaries(context)
        health_summary = self._build_health_summary(context)
        
        # Calculate score
        score = self._calculate_score(
            habit_summaries,
            task_summary,
            goal_summaries,
            health_summary
        )
        
        # Generate highlights
        highlights = self._generate_highlights(
            habit_summaries,
            task_summary,
            goal_summaries,
            health_summary
        )
        
        # Generate overview
        overview = self._generate_overview(
            habit_summaries,
            task_summary,
            goal_summaries,
            health_summary,
            score
        )
        
        # Generate AI insights if enabled
        insights = []
        recommendations = []
        encouragement = "Keep up the great work!"
        
        if include_ai_insights:
            try:
                ai_content = self._generate_ai_insights(context, score)
                insights = ai_content.get("insights", [])
                recommendations = ai_content.get("recommendations", [])
                encouragement = ai_content.get("encouragement", encouragement)
            except Exception as e:
                logger.error(f"Error generating AI insights: {e}")
                insights = ["Unable to generate AI insights at this time."]
        
        return WeeklySummary(
            generated_at=now,
            period_start=period_start,
            period_end=now,
            overview=overview,
            highlights=highlights,
            habit_summaries=habit_summaries,
            task_summary=task_summary,
            goal_summaries=goal_summaries,
            health_summary=health_summary,
            insights=insights,
            recommendations=recommendations,
            encouragement=encouragement,
            score=score
        )
    
    def _gather_context(self, user_id: str) -> Dict[str, Any]:
        """Gather all relevant context data."""
        return self.integration.get_user_context(
            user_id,
            include_types=["habits", "tasks", "goals", "health"]
        )
    
    def _build_habit_summaries(self, context: Dict[str, Any]) -> List[HabitSummary]:
        """Build habit summaries from context."""
        summaries = []
        habits = context.get("data", {}).get("habits", [])
        
        for habit in habits:
            streak = habit.get("streak", 0)
            best_streak = habit.get("best_streak", streak)
            completion_rate = habit.get("completion_rate", 0)
            
            # Determine status
            if completion_rate >= 0.8 and streak > 7:
                status = "thriving"
            elif completion_rate >= 0.5:
                status = "stable"
            else:
                status = "needs_attention"
            
            # Determine trend (simplified - would use historical data in production)
            trend = "stable"
            if completion_rate > 0.7:
                trend = "improving"
            elif completion_rate < 0.3:
                trend = "declining"
            
            summaries.append(HabitSummary(
                name=habit.get("name", "Unknown"),
                streak=streak,
                best_streak=best_streak,
                completion_rate=completion_rate,
                status=status,
                trend=trend
            ))
        
        return summaries
    
    def _build_task_summary(self, context: Dict[str, Any]) -> TaskSummary:
        """Build task summary from context."""
        tasks = context.get("data", {}).get("tasks", [])
        
        total = len(tasks)
        completed = len([t for t in tasks if t.get("completed", False)])
        overdue = len([t for t in tasks if self._is_overdue(t)])
        
        # Group by category
        categories: Dict[str, int] = {}
        for task in tasks:
            category = task.get("category", "uncategorized")
            categories[category] = categories.get(category, 0) + 1
        
        return TaskSummary(
            total=total,
            completed=completed,
            completion_rate=completed / total if total > 0 else 0,
            overdue=overdue,
            categories=categories
        )
    
    def _build_goal_summaries(self, context: Dict[str, Any]) -> List[GoalSummary]:
        """Build goal summaries from context."""
        summaries = []
        goals = context.get("data", {}).get("goals", [])
        
        for goal in goals:
            progress = goal.get("progress", 0)
            target_date = goal.get("target_date")
            
            # Determine status
            if progress >= 100:
                status = "completed"
            elif progress >= 50:
                status = "on_track"
            else:
                status = "behind"
            
            # Calculate days remaining
            days_remaining = None
            if target_date:
                try:
                    target_dt = datetime.fromisoformat(target_date)
                    days_remaining = (target_dt - datetime.now()).days
                except (ValueError, TypeError):
                    pass
            
            summaries.append(GoalSummary(
                name=goal.get("name", "Unknown"),
                progress=progress,
                status=status,
                days_remaining=days_remaining
            ))
        
        return summaries
    
    def _build_health_summary(self, context: Dict[str, Any]) -> HealthSummary:
        """Build health summary from context."""
        health = context.get("data", {}).get("health", {})
        
        sleep_data = health.get("sleep", [])
        mood_data = health.get("mood", [])
        
        # Calculate averages
        avg_sleep = None
        if sleep_data:
            avg_sleep = sum(sleep_data) / len(sleep_data)
        
        avg_mood = None
        if mood_data:
            avg_mood = sum(mood_data) / len(mood_data)
        
        # Determine trends
        sleep_trend = self._calculate_trend(sleep_data)
        mood_trend = self._calculate_trend(mood_data)
        
        # Generate alerts
        alerts = []
        if avg_sleep and avg_sleep < 6:
            alerts.append("Sleep is below recommended levels")
        if avg_mood and avg_mood < 3:
            alerts.append("Mood has been lower than usual")
        
        return HealthSummary(
            avg_sleep=avg_sleep,
            sleep_trend=sleep_trend,
            avg_mood=avg_mood,
            mood_trend=mood_trend,
            alerts=alerts
        )
    
    def _calculate_trend(self, data: List[float]) -> str:
        """Calculate trend from data series."""
        if not data or len(data) < 2:
            return "stable"
        
        # Simple trend: compare first half to second half
        mid = len(data) // 2
        first_half_avg = sum(data[:mid]) / mid if mid > 0 else 0
        second_half_avg = sum(data[mid:]) / (len(data) - mid) if len(data) > mid else 0
        
        diff = second_half_avg - first_half_avg
        
        if diff > 0.5:
            return "improving"
        elif diff < -0.5:
            return "declining"
        return "stable"
    
    def _is_overdue(self, task: Dict[str, Any]) -> bool:
        """Check if a task is overdue."""
        if task.get("completed", False):
            return False
        
        due_date = task.get("due_date")
        if not due_date:
            return False
        
        try:
            due_dt = datetime.fromisoformat(due_date)
            return due_dt < datetime.now()
        except (ValueError, TypeError):
            return False
    
    def _calculate_score(
        self,
        habits: List[HabitSummary],
        tasks: TaskSummary,
        goals: List[GoalSummary],
        health: HealthSummary
    ) -> float:
        """Calculate overall weekly score."""
        score = 0.0
        weights = {
            "habits": 0.35,
            "tasks": 0.25,
            "goals": 0.25,
            "health": 0.15
        }
        
        # Habit score
        if habits:
            habit_score = sum(
                h.completion_rate * (1 + h.streak / 100)  # Bonus for streaks
                for h in habits
            ) / len(habits)
            score += habit_score * 100 * weights["habits"]
        
        # Task score
        score += tasks.completion_rate * 100 * weights["tasks"]
        
        # Goal score
        if goals:
            goal_score = sum(g.progress / 100 for g in goals) / len(goals)
            score += goal_score * 100 * weights["goals"]
        
        # Health score
        health_score = 50  # Default
        if health.avg_sleep:
            # Ideal sleep is 7-9 hours
            sleep_score = 100 - abs(8 - health.avg_sleep) * 10
            health_score = max(0, sleep_score)
        
        if health.avg_mood:
            # Mood on scale of 1-5
            mood_score = health.avg_mood * 20
            health_score = (health_score + mood_score) / 2
        
        score += health_score * weights["health"]
        
        return min(100, max(0, score))
    
    def _generate_highlights(
        self,
        habits: List[HabitSummary],
        tasks: TaskSummary,
        goals: List[GoalSummary],
        health: HealthSummary
    ) -> List[str]:
        """Generate highlight moments from the week."""
        highlights = []
        
        # Habit highlights
        for habit in habits:
            if habit.streak >= 7:
                highlights.append(f"🔥 {habit.streak} day streak on {habit.name}!")
            if habit.streak == habit.best_streak and habit.streak > 0:
                highlights.append(f"🏆 Tied best streak on {habit.name}!")
            if habit.status == "thriving":
                highlights.append(f"✨ {habit.name} is thriving this week!")
        
        # Task highlights
        if tasks.completion_rate >= 0.8:
            highlights.append(f"📋 Completed {tasks.completed} tasks this week!")
        elif tasks.completion_rate >= 0.5:
            highlights.append(f"📝 Good progress on tasks - {tasks.completed} completed")
        
        # Goal highlights
        for goal in goals:
            if goal.status == "completed":
                highlights.append(f"🎯 Completed goal: {goal.name}!")
            elif goal.progress >= 75:
                highlights.append(f"🎯 Almost there on {goal.name}!")
        
        # Health highlights
        if health.avg_sleep and health.avg_sleep >= 7:
            highlights.append(f"😴 Great sleep average: {health.avg_sleep:.1f} hours")
        if health.avg_mood and health.avg_mood >= 4:
            highlights.append(f"😊 Positive mood trend this week!")
        
        return highlights[:5]  # Top 5 highlights
    
    def _generate_overview(
        self,
        habits: List[HabitSummary],
        tasks: TaskSummary,
        goals: List[GoalSummary],
        health: HealthSummary,
        score: float
    ) -> str:
        """Generate a text overview of the week."""
        habit_count = len(habits)
        thriving_habits = len([h for h in habits if h.status == "thriving"])
        
        parts = [
            f"This week you maintained {habit_count} habits",
        ]
        
        if thriving_habits > 0:
            parts.append(f"with {thriving_habits} thriving")
        
        parts.append(f"and completed {int(tasks.completion_rate * 100)}% of your tasks.")
        
        if score >= 80:
            parts.append("Outstanding week!")
        elif score >= 60:
            parts.append("Great progress this week!")
        elif score >= 40:
            parts.append("Steady progress - room for improvement.")
        else:
            parts.append("Challenging week - let's get back on track!")
        
        return " ".join(parts)
    
    def _generate_ai_insights(
        self,
        context: Dict[str, Any],
        score: float
    ) -> Dict[str, Any]:
        """Generate AI-powered insights and recommendations."""
        # Build prompt for the AI
        prompt = self._build_insight_prompt(context, score)
        
        try:
            # Get AI response
            result = self.assistant.chat(prompt)
            
            if result.success:
                # Parse AI response
                return self._parse_ai_response(result.content)
        except Exception as e:
            logger.error(f"Error getting AI insights: {e}")
        
        # Return defaults if AI fails
        return {
            "insights": ["Continue tracking your progress for better insights."],
            "recommendations": ["Focus on consistency in your daily habits."],
            "encouragement": "Keep going - every step counts!"
        }
    
    def _build_insight_prompt(self, context: Dict[str, Any], score: float) -> str:
        """Build the prompt for AI insight generation."""
        return f"""Analyze the following weekly data and provide insights and recommendations.

Weekly Data:
{json.dumps(context.get('data', {}), indent=2, default=str)}

Weekly Score: {score:.0f}/100

Please provide:
1. 2-3 key insights about patterns or trends
2. 2-3 actionable recommendations for improvement
3. A brief encouraging message

Format your response as JSON:
{{
    "insights": ["insight1", "insight2"],
    "recommendations": ["rec1", "rec2"],
    "encouragement": "Your encouraging message here"
}}"""
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured data."""
        try:
            # Try to extract JSON from response
            import re
            
            # Find JSON block
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Return parsed defaults
        return {
            "insights": [response[:200] if len(response) > 200 else response],
            "recommendations": [],
            "encouragement": "Keep up the great work!"
        }


# Convenience functions
def generate_weekly_summary(user_id: str = "default") -> WeeklySummary:
    """
    Generate a weekly summary.
    
    Args:
        user_id: User identifier
        
    Returns:
        WeeklySummary object
    """
    generator = WeeklySummaryGenerator()
    return generator.generate(user_id)


def get_summary_json(user_id: str = "default") -> Dict[str, Any]:
    """
    Get weekly summary as JSON-compatible dictionary.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary representation of the summary
    """
    summary = generate_weekly_summary(user_id)
    return summary.to_dict()