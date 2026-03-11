"""
Micro/Macro Hole Response

Handle gaps in tracking.

Based on Task 11.3.9 from PHASE_11_INTEGRATION_ROADMAP.md

Handle gaps - micro-holes (1-3 days) vs macro-holes (week+).
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class HoleType(Enum):
    """Types of tracking gaps."""
    MICRO = "micro"  # 1-3 days
    SMALL = "small"  # 4-7 days
    MACRO = "macro"  # Week or more


class HoleReason(Enum):
    """Reasons for gaps."""
    BUSY = "busy"
    SICK = "sick"
    TRAVEL = "travel"
    STRESS = "stress"
    DISRUPTION = "disruption"
    FORGOT = "forgot"
    MOTIVATION_LOSS = "motivation_loss"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Strategies for recovery."""
    GENTLE_RESTART = "gentle_restart"  # Start small
    FULL_RESET = "full_reset"  # Treat as new
    GRADUAL = "gradual"  # Slowly rebuild
    PARTNER_SUPPORT = "partner_support"  # Get help


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class Hole:
    """A gap in tracking."""
    id: str
    user_id: str
    habit_id: str
    
    # Timing
    start_date: datetime
    end_date: Optional[datetime]
    duration_days: int
    
    # Type
    hole_type: HoleType
    
    # Reason
    reason: HoleReason
    user_reported: bool = False
    
    # Recovery
    recovery_strategy: Optional[RecoveryStrategy] = None
    recovery_completed: bool = False


@dataclass
class RecoveryPlan:
    """Plan for recovering from a hole."""
    id: str
    hole_id: str
    user_id: str
    
    # Strategy
    strategy: RecoveryStrategy
    
    # Steps
    initial_habit: str  # Start with this
    initial_frequency: str
    
    # Timeline
    duration_days: int
    milestones: List[str] = field(default_factory=list)
    
    # Progress
    current_day: int = 0
    is_active: bool = True


# =============================================================================
# HOLE RESPONSE ENGINE
# =============================================================================

class HoleResponseEngine:
    """
    Handle tracking gaps.
    
    Features:
    - Detect holes
    - Classify gap type
    - Generate recovery plans
    - Track recovery
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.holes: Dict[str, Hole] = {}
        self.recovery_plans: Dict[str, RecoveryPlan] = {}
    
    def detect_hole(
        self,
        user_id: str,
        habit_id: str,
        last_completion: datetime,
        current_date: Optional[datetime] = None
    ) -> Optional[Hole]:
        """Detect if there's a hole in tracking."""
        import uuid
        
        current = current_date or datetime.now()
        days_gap = (current - last_completion).days
        
        # Only consider if gap is significant
        if days_gap < 1:
            return None
        
        # Classify hole type
        if days_gap <= 3:
            hole_type = HoleType.MICRO
        elif days_gap <= 7:
            hole_type = HoleType.SMALL
        else:
            hole_type = HoleType.MACRO
        
        hole = Hole(
            id=str(uuid.uuid4()),
            user_id=user_id,
            habit_id=habit_id,
            start_date=last_completion,
            end_date=current,
            duration_days=days_gap,
            hole_type=hole_type,
            reason=HoleReason.UNKNOWN
        )
        
        self.holes[hole.id] = hole
        return hole
    
    def report_reason(
        self,
        hole_id: str,
        reason: HoleReason
    ) -> None:
        """Report the reason for the hole."""
        hole = self.holes.get(hole_id)
        if hole:
            hole.reason = reason
            hole.user_reported = True
    
    def create_recovery_plan(
        self,
        hole_id: str,
        user_id: str,
        strategy: RecoveryStrategy,
        initial_habit: str,
        initial_frequency: str,
        duration_days: int
    ) -> RecoveryPlan:
        """Create a recovery plan."""
        import uuid
        
        hole = self.holes.get(hole_id)
        
        # Default milestones based on type
        milestones = []
        if hole:
            if hole.hole_type == HoleType.MICRO:
                milestones = [
                    "Complete habit 1 time",
                    "Complete habit 2 times",
                    "Return to normal"
                ]
            elif hole.hole_type == HoleType.SMALL:
                milestones = [
                    "Complete once this week",
                    "Complete twice this week",
                    "Establish routine"
                ]
            else:  # MACRO
                milestones = [
                    "Complete once",
                    "Complete 3 times",
                    "Build 3-day streak",
                    "Return to normal"
                ]
        
        plan = RecoveryPlan(
            id=str(uuid.uuid4()),
            hole_id=hole_id,
            user_id=user_id,
            strategy=strategy,
            initial_habit=initial_habit,
            initial_frequency=initial_frequency,
            duration_days=duration_days,
            milestones=milestones
        )
        
        self.recovery_plans[hole_id] = plan
        
        # Update hole
        if hole:
            hole.recovery_strategy = strategy
        
        return plan
    
    def get_recovery_strategy(self, hole_id: str) -> RecoveryStrategy:
        """Get recommended recovery strategy."""
        hole = self.holes.get(hole_id)
        if not hole:
            return RecoveryStrategy.GENTLE_RESTART
        
        # Strategy based on hole type and reason
        if hole.hole_type == HoleType.MICRO:
            return RecoveryStrategy.GENTLE_RESTART
        elif hole.hole_type == HoleType.SMALL:
            return RecoveryStrategy.GRADUAL
        else:  # MACRO
            if hole.reason in [HoleReason.SICK, HoleReason.DISRUPTION]:
                return RecoveryStrategy.GENTLE_RESTART
            elif hole.reason == HoleReason.MOTIVATION_LOSS:
                return RecoveryStrategy.PARTNER_SUPPORT
            else:
                return RecoveryStrategy.FULL_RESET
    
    def update_recovery(
        self,
        hole_id: str,
        completed: bool = False
    ) -> None:
        """Update recovery progress."""
        plan = self.recovery_plans.get(hole_id)
        if plan:
            if completed:
                plan.current_day += 1
                if plan.current_day >= plan.duration_days:
                    plan.is_active = False
                    hole = self.holes.get(hole_id)
                    if hole:
                        hole.recovery_completed = True
    
    def get_hole_summary(self, hole_id: str) -> Dict:
        """Get a summary of a hole."""
        hole = self.holes.get(hole_id)
        if not hole:
            return {}
        
        plan = self.recovery_plans.get(hole_id)
        
        # Determine severity
        if hole.hole_type == HoleType.MICRO:
            severity = "low"
            message = "A small gap - easy to recover from!"
        elif hole.hole_type == HoleType.SMALL:
            severity = "medium"
            message = "A moderate gap - let's get back on track."
        else:
            severity = "high"
            message = "A larger gap - be patient with yourself."
        
        return {
            "duration_days": hole.duration_days,
            "type": hole.hole_type.value,
            "reason": hole.reason.value,
            "user_reported": hole.user_reported,
            "has_recovery_plan": plan is not None,
            "recovery_active": plan.is_active if plan else False,
            "severity": severity,
            "message": message,
            "strategy": plan.strategy.value if plan else None
        }
    
    def get_user_holes(
        self,
        user_id: str,
        active_only: bool = False
    ) -> List[Hole]:
        """Get all holes for a user."""
        holes = [h for h in self.holes.values() if h.user_id == user_id]
        
        if active_only:
            holes = [
                h for h in holes
                if not h.recovery_completed
            ]
        
        return holes


def create_engine() -> HoleResponseEngine:
    """Factory function."""
    return HoleResponseEngine()
