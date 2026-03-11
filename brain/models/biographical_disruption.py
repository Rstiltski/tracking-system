"""
Biographical Disruption Framework

Handle major life disruptions.

Based on Task 11.3.7 from PHASE_11_INTEGRATION_ROADMAP.md

Handle major life disruptions - illness, injury, loss.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class DisruptionType(Enum):
    """Types of biographical disruptions."""
    ILLNESS = "illness"
    INJURY = "injury"
    LOSS = "loss"  # Death of loved one
    DIVORCE = "divorce"
    JOB_LOSS = "job_loss"
    ACCIDENT = "accident"
    MENTAL_HEALTH = "mental_health"
    RELOCATION = "relocation"
    NATURAL_DISASTER = "natural_disaster"
    OTHER = "other"


class DisruptionPhase(Enum):
    """Phases of dealing with disruption."""
    ACUTE = "acute"  # Crisis mode
    STABILIZING = "stabilizing"  # Getting back on feet
    ADAPTING = "adapting"  # New normal
    RECOVERING = "recovering"  # Rebuilding


class HabitAdjustment(Enum):
    """Types of habit adjustments."""
    PAUSE = "pause"  # Temporarily stop
    MODIFY = "modify"  # Make easier
    REPLACE = "replace"  # Swap for another
    REDUCE = "reduce"  # Reduce frequency
    MAINTAIN = "maintain"  # Keep going


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class Disruption:
    """A major life disruption."""
    id: str
    user_id: str
    
    # Event
    disruption_type: DisruptionType
    title: str
    description: str
    start_date: datetime
    expected_duration: Optional[str] = None  # e.g., "2 weeks", "ongoing"
    
    # Phase
    current_phase: DisruptionPhase = DisruptionPhase.ACUTE
    
    # Impact
    affected_habits: List[str] = field(default_factory=list)
    impact_severity: int = 5  # 1-10
    
    # Progress
    notes: List[str] = field(default_factory=list)
    milestones: List[str] = field(default_factory=list)


@dataclass
class HabitAdjustmentPlan:
    """A plan to adjust habits during disruption."""
    id: str
    user_id: str
    disruption_id: str
    habit_id: str
    
    # Original
    original_frequency: str
    
    # Adjustment
    adjustment_type: HabitAdjustment
    adjusted_frequency: str
    rationale: str
    
    # Timeline
    start_date: datetime
    review_date: Optional[datetime] = None
    
    # Status
    is_active: bool = True


@dataclass
class RecoveryMilestone:
    """A milestone in recovery."""
    id: str
    user_id: str
    disruption_id: str
    title: str
    achieved: bool = False
    achieved_date: Optional[datetime] = None


# =============================================================================
# BIOGRAPHICAL DISRUPTION ENGINE
# =============================================================================

class BiographicalDisruptionEngine:
    """
    Handle major life disruptions.
    
    Features:
    - Track disruptions
    - Adjust habits
    - Monitor recovery
    - Provide support
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.disruptions: Dict[str, Disruption] = {}
        self.adjustments: Dict[str, List[HabitAdjustmentPlan]] = {}
        self.milestones: Dict[str, List[RecoveryMilestone]] = {}
    
    def create_disruption(
        self,
        user_id: str,
        disruption_type: DisruptionType,
        title: str,
        description: str,
        start_date: datetime,
        expected_duration: Optional[str] = None,
        impact_severity: int = 5
    ) -> Disruption:
        """Create a disruption record."""
        import uuid
        
        disruption = Disruption(
            id=str(uuid.uuid4()),
            user_id=user_id,
            disruption_type=disruption_type,
            title=title,
            description=description,
            start_date=start_date,
            expected_duration=expected_duration,
            impact_severity=impact_severity
        )
        
        self.disruptions[disruption.id] = disruption
        self.adjustments[disruption.id] = []
        self.milestones[disruption.id] = []
        
        return disruption
    
    def update_phase(
        self,
        disruption_id: str,
        new_phase: DisruptionPhase
    ) -> None:
        """Update the disruption phase."""
        disruption = self.disruptions.get(disruption_id)
        if disruption:
            disruption.current_phase = new_phase
    
    def create_habit_adjustment(
        self,
        user_id: str,
        disruption_id: str,
        habit_id: str,
        original_frequency: str,
        adjustment_type: HabitAdjustment,
        adjusted_frequency: str,
        rationale: str,
        review_date: Optional[datetime] = None
    ) -> HabitAdjustmentPlan:
        """Create a habit adjustment plan."""
        import uuid
        
        plan = HabitAdjustmentPlan(
            id=str(uuid.uuid4()),
            user_id=user_id,
            disruption_id=disruption_id,
            habit_id=habit_id,
            original_frequency=original_frequency,
            adjustment_type=adjustment_type,
            adjusted_frequency=adjusted_frequency,
            rationale=rationale,
            start_date=datetime.now(),
            review_date=review_date
        )
        
        self.adjustments[disruption_id].append(plan)
        
        # Update disruption affected habits
        disruption = self.disruptions.get(disruption_id)
        if disruption and habit_id not in disruption.affected_habits:
            disruption.affected_habits.append(habit_id)
        
        return plan
    
    def add_milestone(
        self,
        user_id: str,
        disruption_id: str,
        title: str
    ) -> RecoveryMilestone:
        """Add a recovery milestone."""
        import uuid
        
        milestone = RecoveryMilestone(
            id=str(uuid.uuid4()),
            user_id=user_id,
            disruption_id=disruption_id,
            title=title
        )
        
        self.milestones[disruption_id].append(milestone)
        return milestone
    
    def mark_milestone_achieved(self, milestone_id: str) -> None:
        """Mark a milestone as achieved."""
        for milestones in self.milestones.values():
            for m in milestones:
                if m.id == milestone_id:
                    m.achieved = True
                    m.achieved_date = datetime.now()
                    return
    
    def get_disruption_summary(self, disruption_id: str) -> Dict:
        """Get a summary of the disruption."""
        disruption = self.disruptions.get(disruption_id)
        if not disruption:
            return {}
        
        adjustments = self.adjustments.get(disruption_id, [])
        milestones = self.milestones.get(disruption_id, [])
        
        # Calculate days since start
        days_since = (datetime.now() - disruption.start_date).days
        
        # Milestone progress
        achieved = sum(1 for m in milestones if m.achieved)
        
        # Adjustment status
        active = sum(1 for a in adjustments if a.is_active)
        
        return {
            "title": disruption.title,
            "type": disruption.disruption_type.value,
            "phase": disruption.current_phase.value,
            "days_since": days_since,
            "impact_severity": disruption.impact_severity,
            "affected_habits": len(disruption.affected_habits),
            "active_adjustments": active,
            "milestones_achieved": achieved,
            "total_milestones": len(milestones),
            "progress_pct": (achieved / len(milestones) * 100) if milestones else 0
        }
    
    def get_phase_guidance(self, phase: DisruptionPhase) -> str:
        """Get guidance for a phase."""
        guidance = {
            DisruptionPhase.ACUTE:
                "Focus on survival and self-care. Don't worry about habits right now. "
                "Be gentle with yourself.",
            DisruptionPhase.STABILIZING:
                "Start small. Pick 1-2 habits that matter most. "
                "Lower expectations temporarily.",
            DisruptionPhase.ADAPTING:
                "Create new routines that fit your current reality. "
                "Be creative - habits don't have to look the same.",
            DisruptionPhase.RECOVERING:
                "Gradually rebuild. Increase habit difficulty slowly. "
                "Celebrate progress, not perfection."
        }
        return guidance.get(phase, "Take it one day at a time.")
    
    def get_user_disruptions(self, user_id: str) -> List[Disruption]:
        """Get all disruptions for a user."""
        return [
            d for d in self.disruptions.values()
            if d.user_id == user_id
        ]


def create_engine() -> BiographicalDisruptionEngine:
    """Factory function."""
    return BiographicalDisruptionEngine()
