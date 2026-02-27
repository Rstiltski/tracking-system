"""
Relapse Prevention Plan Manager - Create and manage implementation intentions.

This manager helps users create, use, and track relapse prevention plans
based on implementation intention research.

Key Features:
1. Plan Creation - From templates or custom
2. Trigger Detection - Identify when plans should activate
3. Usage Tracking - Record plan usage and effectiveness
4. Analytics - Track which plans work best

Usage:
    from brain.behavioral.relapse_plan_manager import RelapsePlanManager
    
    manager = RelapsePlanManager(storage, habit_id)
    plan = manager.create_plan(...)
    manager.record_plan_usage(plan.id, effectiveness=5)
"""
from datetime import date, timedelta, datetime
from typing import List, Dict, Any, Optional, Tuple
import logging

from brain.models.relapse_plan import (
    PlanCategory,
    PlanTrigger,
    RelapsePreventionPlan,
    PlanTemplate,
    PlanUsage,
    DEFAULT_PLAN_TEMPLATES,
)

logger = logging.getLogger(__name__)


class RelapsePlanManager:
    """
    Manages relapse prevention plans for habits.

    Helps users create implementation intentions and track
    their effectiveness in preventing habit abandonment.

    Usage:
        manager = RelapsePlanManager(storage, habit_id)
        plan = manager.create_plan(...)
    """

    # Trigger detection thresholds
    STREAK_WARNING_THRESHOLD = 3  # Warn when streak below 3
    SCORE_WARNING_THRESHOLD = 0.50  # Warn when score below 50%

    def __init__(self, storage: Any, habit_id: str, user_id: str = ""):
        """
        Initialize plan manager.

        Args:
            storage: Storage instance for data access
            habit_id: ID of the habit to protect
            user_id: ID of the user (optional)
        """
        self.storage = storage
        self.habit_id = habit_id
        self.user_id = user_id

    def create_plan(
        self,
        category: PlanCategory,
        if_condition: str,
        then_action: str,
        trigger: PlanTrigger = PlanTrigger.CUSTOM,
        action_type: str = "reduce",
        backup_plan: str = ""
    ) -> RelapsePreventionPlan:
        """
        Create a new relapse prevention plan.

        Args:
            category: Plan category
            if_condition: The "if" part of the plan
            then_action: The "then" part of the plan
            trigger: What triggers this plan
            action_type: Type of action
            backup_plan: Alternative if primary fails

        Returns:
            Created RelapsePreventionPlan
        """
        plan = RelapsePreventionPlan(
            habit_id=self.habit_id,
            user_id=self.user_id,
            category=category,
            trigger=trigger,
            if_condition=if_condition,
            then_action=then_action,
            action_type=action_type,
            backup_plan=backup_plan
        )

        # Save plan
        self.storage.save_relapse_plan(self.habit_id, plan.to_dict())

        logger.info(
            f"Created relapse prevention plan for habit {self.habit_id}: "
            f"{category.value} - {plan.get_if_then_text()}"
        )

        return plan

    def create_plan_from_template(
        self,
        template: PlanTemplate
    ) -> RelapsePreventionPlan:
        """
        Create a plan from a template.

        Args:
            template: Template to use

        Returns:
            Created RelapsePreventionPlan
        """
        return self.create_plan(
            category=template.category,
            if_condition=template.if_condition,
            then_action=template.then_action,
            trigger=template.trigger,
            action_type=template.action_type,
            backup_plan=template.backup_plan
        )

    def get_plans(self, active_only: bool = True) -> List[RelapsePreventionPlan]:
        """
        Get all plans for this habit.

        Args:
            active_only: Whether to return only active plans

        Returns:
            List of RelapsePreventionPlan objects
        """
        plans_data = self.storage.get_relapse_plans(self.habit_id, active_only)
        return [RelapsePreventionPlan.from_dict(p) for p in plans_data]

    def get_active_plans(self) -> List[RelapsePreventionPlan]:
        """
        Get all active plans.

        Returns:
            List of active RelapsePreventionPlan objects
        """
        return self.get_plans(active_only=True)

    def activate_plan(self, plan_id: str) -> bool:
        """
        Activate a plan.

        Args:
            plan_id: ID of the plan to activate

        Returns:
            True if successful
        """
        return self.storage.update_relapse_plan(plan_id, {"is_active": True})

    def deactivate_plan(self, plan_id: str) -> bool:
        """
        Deactivate a plan.

        Args:
            plan_id: ID of the plan to deactivate

        Returns:
            True if successful
        """
        return self.storage.update_relapse_plan(plan_id, {"is_active": False})

    def delete_plan(self, plan_id: str) -> bool:
        """
        Delete a plan.

        Args:
            plan_id: ID of the plan to delete

        Returns:
            True if successful
        """
        return self.storage.delete_relapse_plan(plan_id)

    def record_plan_usage(
        self,
        plan_id: str,
        situation: str = "",
        action_taken: str = "",
        effectiveness: Optional[int] = None,
        notes: str = ""
    ) -> PlanUsage:
        """
        Record that a plan was used.

        Args:
            plan_id: ID of the plan used
            situation: What situation triggered the plan
            action_taken: What action was actually taken
            effectiveness: 1-5 star effectiveness rating
            notes: Additional notes

        Returns:
            Created PlanUsage record
        """
        # Get the plan
        plans = self.get_plans(active_only=False)
        plan = next((p for p in plans if p.id == plan_id), None)

        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        # Create usage record
        usage = PlanUsage(
            plan_id=plan_id,
            habit_id=self.habit_id,
            situation=situation or plan.if_condition,
            action_taken=action_taken or plan.then_action,
            effectiveness=effectiveness,
            notes=notes
        )

        # Save usage
        self.storage.save_relapse_plan_usage(self.habit_id, usage.to_dict())

        # Update plan usage count
        plan.record_usage(effectiveness)
        self.storage.update_relapse_plan(plan_id, {
            "usage_count": plan.usage_count,
            "last_used": plan.last_used.isoformat() if plan.last_used else None,
            "effectiveness": plan.effectiveness
        })

        logger.info(
            f"Recorded usage of relapse plan {plan_id} for habit {self.habit_id}"
        )

        return usage

    def get_plan_usage_history(
        self,
        plan_id: Optional[str] = None,
        limit: int = 20
    ) -> List[PlanUsage]:
        """
        Get plan usage history.

        Args:
            plan_id: Optional specific plan ID
            limit: Maximum number of records

        Returns:
            List of PlanUsage records
        """
        usage_data = self.storage.get_relapse_plan_usage(
            self.habit_id,
            plan_id,
            limit
        )
        return [PlanUsage.from_dict(u) for u in usage_data]

    def get_effectiveness_stats(self) -> Dict[str, Any]:
        """
        Get effectiveness statistics for all plans.

        Returns:
            Dict with statistics
        """
        plans = self.get_plans(active_only=False)
        usage_history = self.get_plan_usage_history(limit=100)

        if not plans:
            return {
                "total_plans": 0,
                "active_plans": 0,
                "total_usage": 0,
                "average_effectiveness": 0.0,
                "most_effective_plan": None,
                "most_used_plan": None
            }

        # Calculate stats
        active_count = sum(1 for p in plans if p.is_active)
        total_usage = sum(p.usage_count for p in plans)

        # Average effectiveness
        effectiveness_ratings = [
            p.effectiveness for p in plans if p.effectiveness is not None
        ]
        avg_effectiveness = (
            sum(effectiveness_ratings) / len(effectiveness_ratings)
            if effectiveness_ratings else 0.0
        )

        # Most effective plan
        most_effective = max(
            [p for p in plans if p.effectiveness is not None],
            key=lambda p: p.effectiveness,
            default=None
        )

        # Most used plan
        most_used = max(plans, key=lambda p: p.usage_count, default=None)

        return {
            "total_plans": len(plans),
            "active_plans": active_count,
            "total_usage": total_usage,
            "average_effectiveness": round(avg_effectiveness, 2),
            "most_effective_plan": most_effective.to_dict() if most_effective else None,
            "most_used_plan": most_used.to_dict() if most_used else None
        }

    def check_triggers(self) -> List[RelapsePreventionPlan]:
        """
        Check if any plan triggers are currently active.

        Analyzes habit data to detect situations where plans
        should be activated.

        Returns:
            List of plans whose triggers are active
        """
        triggered_plans = []
        plans = self.get_active_plans()

        # Get habit data for trigger detection
        habit = self.storage.get_habit(self.habit_id)
        if not habit:
            return []

        # Calculate current metrics
        streak = self._calculate_streak()
        score = self._get_current_score()
        burnout_risk = self._get_burnout_risk()

        for plan in plans:
            trigger_active = self._is_trigger_active(
                plan.trigger,
                streak,
                score,
                burnout_risk
            )

            if trigger_active:
                triggered_plans.append(plan)

        return triggered_plans

    def _is_trigger_active(
        self,
        trigger: PlanTrigger,
        streak: int,
        score: float,
        burnout_risk: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Check if a specific trigger is active.

        Args:
            trigger: Trigger to check
            streak: Current streak
            score: Current score
            burnout_risk: Current burnout risk data

        Returns:
            True if trigger is active
        """
        if trigger == PlanTrigger.MISSED_YESTERDAY:
            return self._missed_yesterday()
        elif trigger == PlanTrigger.STREAK_below_3:
            return streak < self.STREAK_WARNING_THRESHOLD
        elif trigger == PlanTrigger.SCORE_BELOW_50:
            return score < self.SCORE_WARNING_THRESHOLD
        elif trigger == PlanTrigger.BURNOUT_MODERATE:
            return (
                burnout_risk
                and burnout_risk.get("risk_level") == "moderate"
            )
        elif trigger == PlanTrigger.BURNOUT_HIGH:
            return (
                burnout_risk
                and burnout_risk.get("risk_level") in ["high", "critical"]
            )
        # Other triggers require user input
        return False

    def _missed_yesterday(self) -> bool:
        """Check if habit was missed yesterday."""
        yesterday = date.today() - timedelta(days=1)
        entry = self.storage.get_habit_entry(self.habit_id, yesterday)
        return not (entry and hasattr(entry, 'value') and entry.value > 0)

    def _calculate_streak(self) -> int:
        """Calculate current streak."""
        streak = 0
        today = date.today()

        for i in range(365):
            check_date = today - timedelta(days=i)
            entry = self.storage.get_habit_entry(self.habit_id, check_date)
            if entry and hasattr(entry, 'value') and entry.value > 0:
                streak += 1
            else:
                break

        return streak

    def _get_current_score(self) -> float:
        """Get current habit score."""
        if hasattr(self.storage, 'get_habit_score'):
            score = self.storage.get_habit_score(self.habit_id)
            return score.value if score else 0.0
        return 0.0

    def _get_burnout_risk(self) -> Optional[Dict[str, Any]]:
        """Get current burnout risk assessment."""
        if hasattr(self.storage, 'get_burnout_risk'):
            risk = self.storage.get_burnout_risk(self.habit_id)
            return risk.to_dict() if risk else None
        return None

    def get_suggested_plans(self) -> List[PlanTemplate]:
        """
        Get suggested plan templates based on habit data.

        Analyzes habit patterns to recommend relevant plans.

        Returns:
            List of suggested PlanTemplate objects
        """
        suggestions = []

        # Get habit metrics
        streak = self._calculate_streak()
        score = self._get_current_score()
        burnout_risk = self._get_burnout_risk()

        # Suggest based on patterns
        if streak < self.STREAK_WARNING_THRESHOLD:
            suggestions.append(self._get_template_by_category(
                PlanCategory.MISSED_DAY
            ))

        if score < self.SCORE_WARNING_THRESHOLD:
            suggestions.append(self._get_template_by_category(
                PlanCategory.LOW_MOTIVATION
            ))

        if burnout_risk and burnout_risk.get("risk_level") in ["moderate", "high"]:
            suggestions.append(self._get_template_by_category(
                PlanCategory.STRESS
            ))

        # Always suggest time crunch plan (universally useful)
        suggestions.append(self._get_template_by_category(
            PlanCategory.TIME_CRUNCH
        ))

        # Remove duplicates and None values
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s and s.id not in seen:
                seen.add(s.id)
                unique_suggestions.append(s)

        return unique_suggestions

    def _get_template_by_category(
        self,
        category: PlanCategory
    ) -> Optional[PlanTemplate]:
        """
        Get a template by category.

        Args:
            category: Category to find

        Returns:
            PlanTemplate or None
        """
        for template in DEFAULT_PLAN_TEMPLATES:
            if template.category == category:
                return template
        return None


def get_plan_recommendations(
    habit_name: str,
    habit_type: str,
    current_streak: int
) -> List[PlanTemplate]:
    """
    Get personalized plan recommendations.

    Based on habit characteristics and user patterns.

    Args:
        habit_name: Name of the habit
        habit_type: Type (exercise, learning, etc.)
        current_streak: Current streak length

    Returns:
        List of recommended PlanTemplate objects
    """
    recommendations = []
    habit_lower = habit_name.lower()

    # Habit-type specific recommendations
    if any(word in habit_lower for word in ["exercise", "workout", "run", "gym"]):
        recommendations.append(_get_template("template_travel_1"))
        recommendations.append(_get_template("template_stress_1"))

    if any(word in habit_lower for word in ["meditation", "mindfulness", "pray"]):
        recommendations.append(_get_template("template_time_1"))
        recommendations.append(_get_template("template_social_1"))

    if any(word in habit_lower for word in ["read", "study", "learn", "write"]):
        recommendations.append(_get_template("template_motivation_1"))
        recommendations.append(_get_template("template_time_1"))

    # Streak-based recommendations
    if current_streak < 7:
        recommendations.append(_get_template("template_missed_1"))
        recommendations.append(_get_template("template_missed_2"))

    # Remove duplicates
    seen = set()
    unique = []
    for r in recommendations:
        if r and r.id not in seen:
            seen.add(r.id)
            unique.append(r)

    return unique


def _get_template(template_id: str) -> Optional[PlanTemplate]:
    """Get template by ID."""
    for template in DEFAULT_PLAN_TEMPLATES:
        if template.id == template_id:
            return template
    return None


__all__ = [
    "RelapsePlanManager",
    "get_plan_recommendations",
]
