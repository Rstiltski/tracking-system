"""
Brain AI Coach - Intervention Rules

Defines rules that trigger coaching interventions based on user state.
Each rule has conditions, priority, and intervention type.

Usage:
    from brain.ai.coach.rules import RuleEngine, InterventionRule
    
    engine = RuleEngine()
    triggered = engine.check(user_state)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from enum import Enum


class InterventionType(Enum):
    """Types of interventions the coach can make."""
    BURNOUT_WARNING = "burnout_warning"
    STREAK_BREAK = "streak_break"
    STREAK_CELEBRATION = "streak_celebration"
    MILESTONE_APPROACH = "milestone_approach"
    MILESTONE_CELEBRATION = "milestone_celebration"
    IMPROVEMENT_ENCOURAGEMENT = "improvement_encouragement"
    LOW_ENGAGEMENT = "low_engagement"
    RECOVERY_SUGGESTION = "recovery_suggestion"
    DAILY_CHECK_IN = "daily_check_in"
    HABIT_REMINDER = "habit_reminder"
    GOAL_DEADLINE_WARNING = "goal_deadline_warning"
    PATTERN_DETECTED = "pattern_detected"


class Priority(Enum):
    """Intervention priority levels."""
    CRITICAL = 1   # Immediate attention required
    HIGH = 2       # Important, address soon
    MEDIUM = 3     # Normal priority
    LOW = 4        # Can wait
    INFO = 5       # Informational only


@dataclass
class InterventionRule:
    """
    A rule that triggers an intervention.
    
    Attributes:
        name: Unique rule identifier
        intervention_type: Type of intervention when triggered
        priority: Rule priority (lower = more urgent)
        description: Human-readable description
        condition: Function that checks if rule applies
        cooldown_hours: Hours before same rule can trigger again
        max_triggers_per_day: Maximum times this rule can trigger daily
        enabled: Whether rule is active
    """
    name: str
    intervention_type: InterventionType
    priority: Priority
    description: str
    condition: Callable[[Dict[str, Any]], bool]
    cooldown_hours: int = 24
    max_triggers_per_day: int = 1
    enabled: bool = True
    
    def check(self, user_state: Dict[str, Any]) -> bool:
        """
        Check if this rule triggers for the given state.
        
        Args:
            user_state: User state dictionary
            
        Returns:
            True if rule triggers
        """
        if not self.enabled:
            return False
        return self.condition(user_state)


@dataclass
class TriggeredRule:
    """
    A rule that has been triggered.
    
    Attributes:
        rule: The triggered rule
        triggered_at: When it triggered
        user_state: State at time of trigger
        context: Additional context data
    """
    rule: InterventionRule
    triggered_at: datetime = field(default_factory=datetime.now)
    user_state: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


# Pre-defined rule conditions
def burnout_critical_condition(state: Dict[str, Any]) -> bool:
    """Check for critical burnout risk."""
    return state.get("burnout_risk", 0) >= 71


def burnout_high_condition(state: Dict[str, Any]) -> bool:
    """Check for high burnout risk."""
    return 51 <= state.get("burnout_risk", 0) < 71


def burnout_moderate_condition(state: Dict[str, Any]) -> bool:
    """Check for moderate burnout risk."""
    return 31 <= state.get("burnout_risk", 0) < 51


def streak_break_condition(state: Dict[str, Any]) -> bool:
    """Check if any habit streak was recently broken."""
    habits = state.get("habits_assessment", {})
    return any(
        h.get("health") == "needs_attention" 
        for h in habits.values()
    )


def streak_milestone_condition(days: int) -> Callable[[Dict[str, Any]], bool]:
    """Create condition for streak milestone (7, 21, 30, 100 days)."""
    def condition(state: Dict[str, Any]) -> bool:
        habits = state.get("habits_assessment", {})
        return any(
            h.get("streak") == days 
            for h in habits.values()
        )
    return condition


def goal_milestone_approach_condition(state: Dict[str, Any]) -> bool:
    """Check if any goal is approaching a milestone (90%+ progress)."""
    goals = state.get("goals", [])
    return any(
        90 <= g.get("progress", 0) < 100 
        for g in goals
    )


def goal_completed_condition(state: Dict[str, Any]) -> bool:
    """Check if any goal was recently completed."""
    goals = state.get("goals", [])
    return any(
        g.get("progress", 0) >= 100 and g.get("recently_completed", False)
        for g in goals
    )


def low_engagement_condition(state: Dict[str, Any]) -> bool:
    """Check for low user engagement."""
    engagement = state.get("engagement_level", "normal")
    return engagement in ["dormant", "low"]


def declining_mood_condition(state: Dict[str, Any]) -> bool:
    """Check for declining mood trend."""
    return state.get("mood_trend") == "declining"


def declining_sleep_condition(state: Dict[str, Any]) -> bool:
    """Check for declining sleep trend."""
    return state.get("sleep_trend") == "declining"


def improvement_detected_condition(state: Dict[str, Any]) -> bool:
    """Check if user is showing improvement."""
    return (
        state.get("mood_trend") == "improving" or 
        state.get("sleep_trend") == "improving"
    )


def habit_needs_attention_condition(state: Dict[str, Any]) -> bool:
    """Check if any habit needs attention."""
    habits = state.get("habits_assessment", {})
    return any(
        h.get("needs_intervention", False)
        for h in habits.values()
    )


# Default rules
DEFAULT_RULES: List[InterventionRule] = [
    # Critical burnout - highest priority
    InterventionRule(
        name="burnout_critical",
        intervention_type=InterventionType.BURNOUT_WARNING,
        priority=Priority.CRITICAL,
        description="Critical burnout risk detected",
        condition=burnout_critical_condition,
        cooldown_hours=12,
        max_triggers_per_day=2
    ),
    
    # High burnout risk
    InterventionRule(
        name="burnout_high",
        intervention_type=InterventionType.BURNOUT_WARNING,
        priority=Priority.HIGH,
        description="High burnout risk detected",
        condition=burnout_high_condition,
        cooldown_hours=24,
        max_triggers_per_day=1
    ),
    
    # Moderate burnout risk
    InterventionRule(
        name="burnout_moderate",
        intervention_type=InterventionType.RECOVERY_SUGGESTION,
        priority=Priority.MEDIUM,
        description="Moderate burnout risk - consider rest",
        condition=burnout_moderate_condition,
        cooldown_hours=48,
        max_triggers_per_day=1
    ),
    
    # Streak break
    InterventionRule(
        name="streak_broken",
        intervention_type=InterventionType.STREAK_BREAK,
        priority=Priority.MEDIUM,
        description="A habit streak was broken",
        condition=streak_break_condition,
        cooldown_hours=24,
        max_triggers_per_day=1
    ),
    
    # Streak milestones
    InterventionRule(
        name="streak_7_days",
        intervention_type=InterventionType.STREAK_CELEBRATION,
        priority=Priority.LOW,
        description="7-day streak achieved!",
        condition=streak_milestone_condition(7),
        cooldown_hours=168,  # Once per week per habit
        max_triggers_per_day=3
    ),
    
    InterventionRule(
        name="streak_21_days",
        intervention_type=InterventionType.STREAK_CELEBRATION,
        priority=Priority.MEDIUM,
        description="21-day streak achieved! Habit forming!",
        condition=streak_milestone_condition(21),
        cooldown_hours=168,
        max_triggers_per_day=3
    ),
    
    InterventionRule(
        name="streak_30_days",
        intervention_type=InterventionType.STREAK_CELEBRATION,
        priority=Priority.HIGH,
        description="30-day streak! Amazing dedication!",
        condition=streak_milestone_condition(30),
        cooldown_hours=168,
        max_triggers_per_day=3
    ),
    
    InterventionRule(
        name="streak_100_days",
        intervention_type=InterventionType.STREAK_CELEBRATION,
        priority=Priority.CRITICAL,
        description="100-day streak! Legendary!",
        condition=streak_milestone_condition(100),
        cooldown_hours=168,
        max_triggers_per_day=1
    ),
    
    # Goal milestones
    InterventionRule(
        name="goal_approaching",
        intervention_type=InterventionType.MILESTONE_APPROACH,
        priority=Priority.MEDIUM,
        description="Goal milestone approaching",
        condition=goal_milestone_approach_condition,
        cooldown_hours=48,
        max_triggers_per_day=2
    ),
    
    InterventionRule(
        name="goal_completed",
        intervention_type=InterventionType.MILESTONE_CELEBRATION,
        priority=Priority.HIGH,
        description="Goal completed!",
        condition=goal_completed_condition,
        cooldown_hours=24,
        max_triggers_per_day=5
    ),
    
    # Engagement issues
    InterventionRule(
        name="low_engagement",
        intervention_type=InterventionType.LOW_ENGAGEMENT,
        priority=Priority.MEDIUM,
        description="User engagement is low",
        condition=low_engagement_condition,
        cooldown_hours=72,
        max_triggers_per_day=1
    ),
    
    # Health trends
    InterventionRule(
        name="declining_mood",
        intervention_type=InterventionType.RECOVERY_SUGGESTION,
        priority=Priority.MEDIUM,
        description="Mood trend is declining",
        condition=declining_mood_condition,
        cooldown_hours=48,
        max_triggers_per_day=1
    ),
    
    InterventionRule(
        name="declining_sleep",
        intervention_type=InterventionType.RECOVERY_SUGGESTION,
        priority=Priority.HIGH,
        description="Sleep quality is declining",
        condition=declining_sleep_condition,
        cooldown_hours=48,
        max_triggers_per_day=1
    ),
    
    # Positive reinforcement
    InterventionRule(
        name="improvement_detected",
        intervention_type=InterventionType.IMPROVEMENT_ENCOURAGEMENT,
        priority=Priority.INFO,
        description="User is showing improvement",
        condition=improvement_detected_condition,
        cooldown_hours=24,
        max_triggers_per_day=2
    ),
    
    # Habit needs attention
    InterventionRule(
        name="habit_needs_attention",
        intervention_type=InterventionType.HABIT_REMINDER,
        priority=Priority.MEDIUM,
        description="A habit needs attention",
        condition=habit_needs_attention_condition,
        cooldown_hours=24,
        max_triggers_per_day=3
    ),
]


class RuleEngine:
    """
    Engine for checking intervention rules against user state.
    
    Features:
    - Rule prioritization
    - Cooldown tracking
    - Daily trigger limits
    - Custom rule registration
    
    Usage:
        engine = RuleEngine()
        triggered = engine.check(user_state)
        for t in triggered:
            print(f"Rule triggered: {t.rule.name}")
    """
    
    def __init__(self, rules: Optional[List[InterventionRule]] = None):
        """
        Initialize the rule engine.
        
        Args:
            rules: Custom rules (defaults to DEFAULT_RULES)
        """
        self.rules = rules or DEFAULT_RULES.copy()
        self._trigger_history: Dict[str, List[datetime]] = {}
    
    def add_rule(self, rule: InterventionRule) -> None:
        """Add a custom rule."""
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name."""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                return True
        return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """Enable a rule."""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                return True
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """Disable a rule."""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                return True
        return False
    
    def check(self, user_state: Dict[str, Any]) -> List[TriggeredRule]:
        """
        Check all rules against user state.
        
        Args:
            user_state: Current user state dictionary
            
        Returns:
            List of triggered rules, sorted by priority
        """
        triggered = []
        now = datetime.now()
        
        for rule in self.rules:
            # Check cooldown
            if not self._can_trigger(rule, now):
                continue
            
            # Check if rule triggers
            if rule.check(user_state):
                triggered.append(TriggeredRule(
                    rule=rule,
                    triggered_at=now,
                    user_state=user_state.copy()
                ))
                
                # Record trigger
                self._record_trigger(rule.name, now)
        
        # Sort by priority
        triggered.sort(key=lambda t: t.rule.priority.value)
        
        return triggered
    
    def _can_trigger(self, rule: InterventionRule, now: datetime) -> bool:
        """Check if rule can trigger based on cooldown and daily limit."""
        history = self._trigger_history.get(rule.name, [])
        
        # Check cooldown
        cooldown_cutoff = now - timedelta(hours=rule.cooldown_hours)
        recent_triggers = [t for t in history if t > cooldown_cutoff]
        
        if recent_triggers:
            # Check if cooldown has passed
            last_trigger = max(recent_triggers)
            if now - last_trigger < timedelta(hours=rule.cooldown_hours):
                return False
        
        # Check daily limit
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_triggers = [t for t in history if t >= today_start]
        
        if len(today_triggers) >= rule.max_triggers_per_day:
            return False
        
        return True
    
    def _record_trigger(self, rule_name: str, timestamp: datetime) -> None:
        """Record a rule trigger."""
        if rule_name not in self._trigger_history:
            self._trigger_history[rule_name] = []
        self._trigger_history[rule_name].append(timestamp)
        
        # Cleanup old history (keep last 30 days)
        cutoff = timestamp - timedelta(days=30)
        self._trigger_history[rule_name] = [
            t for t in self._trigger_history[rule_name] if t > cutoff
        ]
    
    def get_rule_by_name(self, name: str) -> Optional[InterventionRule]:
        """Get a rule by name."""
        for rule in self.rules:
            if rule.name == name:
                return rule
        return None
    
    def get_rules_by_type(self, intervention_type: InterventionType) -> List[InterventionRule]:
        """Get all rules of a specific type."""
        return [r for r in self.rules if r.intervention_type == intervention_type]
    
    def get_enabled_rules(self) -> List[InterventionRule]:
        """Get all enabled rules."""
        return [r for r in self.rules if r.enabled]