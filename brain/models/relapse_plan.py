"""
Relapse Prevention Plan Model - Implementation intentions for habit persistence.

Based on psychological research on implementation intentions and relapse prevention:

1. Implementation Intentions (Gollwitzer):
   - IF [situation/cue] THEN [behavior]
   - Specific, actionable plans for challenging situations
   - Automates response to triggers

2. Relapse Prevention (Marlatt & Gordon):
   - Identify high-risk situations
   - Develop coping strategies
   - Plan for setbacks without abandonment

3. Research Basis:
   - Implementation intentions increase success by 2-3x
   - Specific plans reduce cognitive load during stress
   - "If-then" format creates automatic responses

References:
- Gollwitzer, P.M. (1999). "Implementation intentions"
- Marlatt, G.A., & Gordon, J.R. (1985). "Relapse Prevention"
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, Any, List
import uuid


class PlanCategory(str, Enum):
    """
    Categories of relapse prevention plans.

    Each category addresses a different type of challenge.
    """
    MISSED_DAY = "missed_day"  # Plan for after missing a day
    TRAVEL = "travel"  # Plan for when traveling
    LOW_MOTIVATION = "low_motivation"  # Plan for low willpower
    TIME_CRUNCH = "time_crunch"  # Plan for busy days
    STRESS = "stress"  # Plan for high-stress periods
    SOCIAL = "social"  # Plan for social situations
    CUSTOM = "custom"  # User-defined plan


class PlanTrigger(str, Enum):
    """
    Triggers that activate a prevention plan.

    These are the "IF" conditions in if-then plans.
    """
    MISSED_YESTERDAY = "missed_yesterday"
    STREAK_below_3 = "streak_below_3"
    SCORE_BELOW_50 = "score_below_50"
    BURNOUT_MODERATE = "burnout_moderate"
    BURNOUT_HIGH = "burnout_high"
    TRAVELING = "traveling"
    TOO_BUSY = "too_busy"
    LOW_ENERGY = "low_energy"
    CUSTOM = "custom"


@dataclass
class RelapsePreventionPlan:
    """
    A relapse prevention plan for a habit.

    Implements implementation intention format:
    IF [trigger] THEN [action]

    Attributes:
        id: Unique identifier
        habit_id: ID of the habit this plan protects
        user_id: ID of the user
        category: Plan category
        trigger: What triggers this plan
        if_condition: Detailed description of the "if" condition
        then_action: Specific action to take
        action_type: Type of action (reduce, skip, substitute, etc.)
        backup_plan: Alternative if primary plan fails
        is_active: Whether this plan is currently active
        created_at: When the plan was created
        last_used: When the plan was last used
        effectiveness: User-rated effectiveness (1-5 stars)
        usage_count: Number of times plan has been used
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    habit_id: str = ""
    user_id: str = ""
    category: PlanCategory = PlanCategory.CUSTOM
    trigger: PlanTrigger = PlanTrigger.CUSTOM
    if_condition: str = ""
    then_action: str = ""
    action_type: str = "reduce"  # reduce, skip, substitute, reschedule
    backup_plan: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    effectiveness: Optional[int] = None  # 1-5 stars
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "user_id": self.user_id,
            "category": self.category.value,
            "trigger": self.trigger.value,
            "if_condition": self.if_condition,
            "then_action": self.then_action,
            "action_type": self.action_type,
            "backup_plan": self.backup_plan,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "effectiveness": self.effectiveness,
            "usage_count": self.usage_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelapsePreventionPlan":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            habit_id=data.get("habit_id", ""),
            user_id=data.get("user_id", ""),
            category=PlanCategory(data.get("category", "custom")),
            trigger=PlanTrigger(data.get("trigger", "custom")),
            if_condition=data.get("if_condition", ""),
            then_action=data.get("then_action", ""),
            action_type=data.get("action_type", "reduce"),
            backup_plan=data.get("backup_plan", ""),
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            last_used=datetime.fromisoformat(data["last_used"]) if data.get("last_used") else None,
            effectiveness=data.get("effectiveness"),
            usage_count=data.get("usage_count", 0)
        )

    def get_if_then_text(self) -> str:
        """
        Get the plan as an if-then statement.

        Returns:
            Formatted if-then statement
        """
        return f"If {self.if_condition}, then I will {self.then_action}"

    def record_usage(self, effectiveness_rating: Optional[int] = None) -> None:
        """
        Record that this plan was used.

        Args:
            effectiveness_rating: Optional 1-5 star rating
        """
        self.usage_count += 1
        self.last_used = datetime.now()
        if effectiveness_rating:
            # Update effectiveness as running average
            if self.effectiveness is None:
                self.effectiveness = effectiveness_rating
            else:
                # Weighted average favoring recent ratings
                self.effectiveness = round(
                    (self.effectiveness * 0.7) + (effectiveness_rating * 0.3)
                )

    def __str__(self) -> str:
        """String representation."""
        emoji = {
            PlanCategory.MISSED_DAY: "📅",
            PlanCategory.TRAVEL: "✈️",
            PlanCategory.LOW_MOTIVATION: "😴",
            PlanCategory.TIME_CRUNCH: "⏰",
            PlanCategory.STRESS: "😰",
            PlanCategory.SOCIAL: "👥",
            PlanCategory.CUSTOM: "📋",
        }.get(self.category, "📋")

        status = "✅" if self.is_active else "⏸️"
        return f"{emoji} {status} {self.category.value.replace('_', ' ').title()} Plan"


@dataclass
class PlanTemplate:
    """
    A pre-defined plan template.

    Provides ready-to-use plans for common situations.

    Attributes:
        id: Unique identifier
        category: Plan category
        name: Display name for the template
        description: Brief description
        trigger: Default trigger
        if_condition: Default if condition
        then_action: Default then action
        action_type: Default action type
        backup_plan: Default backup plan
        effectiveness_rating: Average effectiveness from users
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    category: PlanCategory = PlanCategory.CUSTOM
    name: str = ""
    description: str = ""
    trigger: PlanTrigger = PlanTrigger.CUSTOM
    if_condition: str = ""
    then_action: str = ""
    action_type: str = "reduce"
    backup_plan: str = ""
    effectiveness_rating: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "category": self.category.value,
            "name": self.name,
            "description": self.description,
            "trigger": self.trigger.value,
            "if_condition": self.if_condition,
            "then_action": self.then_action,
            "action_type": self.action_type,
            "backup_plan": self.backup_plan,
            "effectiveness_rating": self.effectiveness_rating
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanTemplate":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            category=PlanCategory(data.get("category", "custom")),
            name=data.get("name", ""),
            description=data.get("description", ""),
            trigger=PlanTrigger(data.get("trigger", "custom")),
            if_condition=data.get("if_condition", ""),
            then_action=data.get("then_action", ""),
            action_type=data.get("action_type", "reduce"),
            backup_plan=data.get("backup_plan", ""),
            effectiveness_rating=data.get("effectiveness_rating", 0.0)
        )


# Pre-defined plan templates based on research
DEFAULT_PLAN_TEMPLATES: List[PlanTemplate] = [
    # Missed day plans
    PlanTemplate(
        id="template_missed_1",
        category=PlanCategory.MISSED_DAY,
        name="The Fresh Start",
        description="Get back on track after missing a day",
        trigger=PlanTrigger.MISSED_YESTERDAY,
        if_condition="I miss a day",
        then_action="Do a tiny 2-minute version the next day",
        action_type="reduce",
        backup_plan="Just show up, even for 30 seconds",
        effectiveness_rating=4.2
    ),
    PlanTemplate(
        id="template_missed_2",
        category=PlanCategory.MISSED_DAY,
        name="Never Miss Twice",
        description="The golden rule of habit tracking",
        trigger=PlanTrigger.MISSED_YESTERDAY,
        if_condition="I miss one day",
        then_action="Make absolutely sure I don't miss the second day",
        action_type="reschedule",
        backup_plan="Set a phone reminder",
        effectiveness_rating=4.5
    ),

    # Travel plans
    PlanTemplate(
        id="template_travel_1",
        category=PlanCategory.TRAVEL,
        name="Travel Mode",
        description="Maintain habits while traveling",
        trigger=PlanTrigger.TRAVELING,
        if_condition="I'm traveling or away from home",
        then_action="Do a simplified version that requires no equipment",
        action_type="reduce",
        backup_plan="Skip without guilt, resume when home",
        effectiveness_rating=3.8
    ),

    # Low motivation plans
    PlanTemplate(
        id="template_motivation_1",
        category=PlanCategory.LOW_MOTIVATION,
        name="The 2-Minute Rule",
        description="For when motivation is at zero",
        trigger=PlanTrigger.LOW_ENERGY,
        if_condition="I have zero motivation",
        then_action="Do just 2 minutes, then I can stop",
        action_type="reduce",
        backup_plan="Just put on my workout clothes / set up my space",
        effectiveness_rating=4.6
    ),
    PlanTemplate(
        id="template_motivation_2",
        category=PlanCategory.LOW_MOTIVATION,
        name="Identity Reminder",
        description="Remember who you're becoming",
        trigger=PlanTrigger.LOW_ENERGY,
        if_condition="I don't feel like it",
        then_action="Remind myself: I'm the type of person who does this",
        action_type="substitute",
        backup_plan="Look at my progress tracker",
        effectiveness_rating=4.0
    ),

    # Time crunch plans
    PlanTemplate(
        id="template_time_1",
        category=PlanCategory.TIME_CRUNCH,
        name="The Minimum Viable Habit",
        description="For extremely busy days",
        trigger=PlanTrigger.TOO_BUSY,
        if_condition="I have less than 5 minutes",
        then_action="Do the absolute minimum version (1 minute)",
        action_type="reduce",
        backup_plan="Schedule it for later today",
        effectiveness_rating=4.3
    ),

    # Stress plans
    PlanTemplate(
        id="template_stress_1",
        category=PlanCategory.STRESS,
        name="Stress Protocol",
        description="Maintain habits during high stress",
        trigger=PlanTrigger.BURNOUT_HIGH,
        if_condition="I'm overwhelmed with stress",
        then_action="Do a calming, gentle version of the habit",
        action_type="substitute",
        backup_plan="Skip today, use a streak freeze",
        effectiveness_rating=3.9
    ),

    # Social plans
    PlanTemplate(
        id="template_social_1",
        category=PlanCategory.SOCIAL,
        name="Social Balance",
        description="Handle social conflicts",
        trigger=PlanTrigger.CUSTOM,
        if_condition="Social events conflict with my habit",
        then_action="Do the habit before or after the event",
        action_type="reschedule",
        backup_plan="Invite friends to join or explain your goal",
        effectiveness_rating=3.7
    ),
]


@dataclass
class PlanUsage:
    """
    Record of a plan being used.

    Tracks when and how effectively plans are used.

    Attributes:
        id: Unique identifier
        plan_id: ID of the plan that was used
        habit_id: ID of the habit
        used_at: When the plan was used
        situation: What situation triggered the plan
        action_taken: What action was actually taken
        effectiveness: How effective it was (1-5 stars)
        notes: Additional notes
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    plan_id: str = ""
    habit_id: str = ""
    used_at: datetime = field(default_factory=datetime.now)
    situation: str = ""
    action_taken: str = ""
    effectiveness: Optional[int] = None  # 1-5 stars
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "habit_id": self.habit_id,
            "used_at": self.used_at.isoformat(),
            "situation": self.situation,
            "action_taken": self.action_taken,
            "effectiveness": self.effectiveness,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanUsage":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            plan_id=data.get("plan_id", ""),
            habit_id=data.get("habit_id", ""),
            used_at=datetime.fromisoformat(data["used_at"]) if "used_at" in data else datetime.now(),
            situation=data.get("situation", ""),
            action_taken=data.get("action_taken", ""),
            effectiveness=data.get("effectiveness"),
            notes=data.get("notes", "")
        )


__all__ = [
    "PlanCategory",
    "PlanTrigger",
    "RelapsePreventionPlan",
    "PlanTemplate",
    "PlanUsage",
    "DEFAULT_PLAN_TEMPLATES",
]
