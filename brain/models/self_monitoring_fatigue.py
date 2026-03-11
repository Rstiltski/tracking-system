"""
Self-Monitoring Fatigue Detection

Detect and address self-monitoring fatigue before it leads to abandonment.

Based on Task 11.2.11 from PHASE_11_INTEGRATION_ROADMAP.md

Critical for retention - helps users before they quit!
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class FatigueLevel(Enum):
    """Level of self-monitoring fatigue."""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class InterventionType(Enum):
    """Types of interventions for fatigue."""
    REDUCE_TRACKING = "reduce_tracking"
    TAKE_BREAK = "take_break"
    SIMPLIFY = "simplify"
    CELEBRATE = "celebrate"
    SWITCH_FOCUS = "switch_focus"
    REFLECT = "reflect"


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class FatigueSignal:
    """A signal of self-monitoring fatigue."""
    id: str
    user_id: str
    timestamp: datetime
    signal_type: str  # declining_completion, skipped_days, etc.
    value: float
    severity: int  # 1-5


@dataclass
class Intervention:
    """An intervention applied."""
    id: str
    user_id: str
    timestamp: datetime
    intervention_type: InterventionType
    description: str
    effectiveness: Optional[int] = None  # 1-5 rating


# =============================================================================
# SELF-MONITORING FATIGUE ENGINE
# =============================================================================

class SelfMonitoringFatigueEngine:
    """
    Detects and addresses self-monitoring fatigue.
    
    Features:
    - Signal detection (declining completion, skipped days, etc.)
    - Fatigue level calculation
    - Intervention suggestions
    - Recovery tracking
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.signals: List[FatigueSignal] = []
        self.interventions: List[Intervention] = []
        
        # Thresholds
        self.thresholds = {
            "completion_decline": 0.3,  # 30% decline triggers
            "skip_days": 3,  # 3+ skipped days
            "fatigue_score": 70,  # Score threshold for intervention
        }
    
    def record_signal(
        self,
        user_id: str,
        signal_type: str,
        value: float,
        severity: int = 3
    ) -> FatigueSignal:
        """Record a fatigue signal."""
        import uuid
        
        signal = FatigueSignal(
            id=str(uuid.uuid4()),
            user_id=user_id,
            timestamp=datetime.now(),
            signal_type=signal_type,
            value=value,
            severity=severity
        )
        
        self.signals.append(signal)
        return signal
    
    def calculate_fatigue_level(
        self,
        user_id: str,
        completion_history: List[float]
    ) -> FatigueLevel:
        """
        Calculate fatigue level based on completion history.
        
        Args:
            user_id: User ID
            completion_history: List of daily completion rates (0.0 to 1.0)
            
        Returns:
            FatigueLevel enum
        """
        if len(completion_history) < 7:
            return FatigueLevel.NONE
        
        # Calculate trend (simple)
        recent = completion_history[-7:]
        earlier = completion_history[-14:-7] if len(completion_history) >= 14 else []
        
        avg_recent = sum(recent) / len(recent)
        avg_earlier = sum(earlier) / len(earlier) if earlier else avg_recent
        
        # Decline percentage
        decline = (avg_earlier - avg_recent) / max(avg_earlier, 0.1)
        
        # Check skipped days
        skipped = sum(1 for c in recent if c == 0)
        
        # Calculate score (0-100)
        score = 0
        
        # Decline contributes up to 50 points
        if decline > 0.1:
            score += min(decline * 100, 50)
        
        # Skipped days contribute up to 30 points
        score += skipped * 10
        
        # Check for consecutive zeros
        consecutive_zeros = 0
        for c in reversed(recent):
            if c == 0:
                consecutive_zeros += 1
            else:
                break
        score += consecutive_zeros * 5
        
        # Determine level
        if score >= 80:
            return FatigueLevel.CRITICAL
        elif score >= 60:
            return FatigueLevel.SEVERE
        elif score >= 40:
            return FatigueLevel.MODERATE
        elif score >= 20:
            return FatigueLevel.MILD
        else:
            return FatigueLevel.NONE
    
    def get_interventions(self, fatigue_level: FatigueLevel) -> List[Dict]:
        """Get intervention suggestions for fatigue level."""
        interventions = {
            FatigueLevel.NONE: [
                {"type": InterventionType.CELEBRATE, "desc": "Keep up the great work!"}
            ],
            FatigueLevel.MILD: [
                {"type": InterventionType.SWITCH_FOCUS, "desc": "Try tracking a different area"},
                {"type": InterventionType.CELEBRATE, "desc": "Acknowledge your progress"}
            ],
            FatigueLevel.MODERATE: [
                {"type": InterventionType.REDUCE_TRACKING, "desc": "Focus on just 1-2 habits"},
                {"type": InterventionType.TAKE_BREAK, "desc": "Take a 1-day tracking break"}
            ],
            FatigueLevel.SEVERE: [
                {"type": InterventionType.TAKE_BREAK, "desc": "Take a 3-5 day tracking break"},
                {"type": InterventionType.SIMPLIFY, "desc": "Simplify to essential habits only"}
            ],
            FatigueLevel.CRITICAL: [
                {"type": InterventionType.TAKE_BREAK, "desc": "Take a 1-week break from tracking"},
                {"type": InterventionType.SIMPLIFY, "desc": "Focus on just ONE habit"},
                {"type": InterventionType.REFLECT, "desc": "Reflect on why you started"}
            ]
        }
        
        return interventions.get(fatigue_level, [])
    
    def apply_intervention(
        self,
        user_id: str,
        intervention_type: InterventionType,
        description: str
    ) -> Intervention:
        """Apply an intervention."""
        import uuid
        
        intervention = Intervention(
            id=str(uuid.uuid4()),
            user_id=user_id,
            timestamp=datetime.now(),
            intervention_type=intervention_type,
            description=description
        )
        
        self.interventions.append(intervention)
        return intervention
    
    def get_recovery_plan(self, user_id: str) -> Dict:
        """Get a recovery plan for the user."""
        # Get recent signals
        recent_signals = [
            s for s in self.signals
            if s.user_id == user_id and s.timestamp >= datetime.now() - timedelta(days=7)
        ]
        
        # Get recent interventions
        recent_interventions = [
            i for i in self.interventions
            if i.user_id == user_id and i.timestamp >= datetime.now() - timedelta(days=7)
        ]
        
        return {
            "recent_signals": len(recent_signals),
            "recent_interventions": len(recent_interventions),
            "recommendation": "Take a break" if len(recent_signals) > 3 else "Keep going"
        }


def create_engine() -> SelfMonitoringFatigueEngine:
    """Factory function."""
    return SelfMonitoringFatigueEngine()
