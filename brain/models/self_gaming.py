"""
Self-Gaming Detection

Detect when users game the system.

Based on Task 11.3.6 from PHASE_11_INTEGRATION_ROADMAP.md

Detect when users game the system - marking done without doing.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class GamingPattern(Enum):
    """Types of self-gaming patterns."""
    RAPID_COMPLETION = "rapid_completion"  # Too fast to be real
    BACKDATING = "backdating"  # Marking past dates
    STREAK_GAMING = "streak_gaming"  # Just maintaining streak
    PERFECTIONISM = "perfectionism"  # Never missing
    SELECTIVE_REPORTING = "selective_reporting"  # Only easy habits
    CONSISTENCY_ANOMALY = "consistency_anomaly"  # Too perfect


class RiskLevel(Enum):
    """Risk level of gaming behavior."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class GamingIndicator:
    """An indicator of potential gaming."""
    id: str
    user_id: str
    habit_id: str
    
    # Detection
    pattern: GamingPattern
    detected_at: datetime
    
    # Evidence
    evidence: str
    confidence: float  # 0-1
    
    # Risk
    risk_level: RiskLevel = RiskLevel.NONE
    
    # Response
    user_notified: bool = False
    intervention_applied: bool = False


@dataclass
class HabitCompletion:
    """A habit completion record for analysis."""
    habit_id: str
    user_id: str
    timestamp: datetime
    completed: bool
    
    # Context
    time_of_day: str
    day_of_week: str
    
    # Metrics
    seconds_since_previous: Optional[float] = None


# =============================================================================
# SELF-GAMING DETECTOR
# =============================================================================

class SelfGamingDetector:
    """
    Detect self-gaming behavior.
    
    Features:
    - Pattern detection
    - Risk assessment
    - Interventions
    - User feedback
    """
    
    def __init__(self):
        """Initialize the detector."""
        self.indicators: List[GamingIndicator] = []
        self.completions: Dict[str, List[HabitCompletion]] = {}
        self.interventions: Dict[str, str] = {}
    
    def record_completion(
        self,
        habit_id: str,
        user_id: str,
        timestamp: datetime,
        completed: bool = True
    ) -> Optional[GamingIndicator]:
        """Record a completion and check for gaming."""
        import uuid
        
        time_of_day = timestamp.strftime("%H:%M")
        day_of_week = timestamp.strftime("%A")
        
        completion = HabitCompletion(
            habit_id=habit_id,
            user_id=user_id,
            timestamp=timestamp,
            completed=completed,
            time_of_day=time_of_day,
            day_of_week=day_of_week
        )
        
        # Store in history
        key = f"{user_id}_{habit_id}"
        if key not in self.completions:
            self.completions[key] = []
        
        # Calculate time since previous
        if self.completions[key]:
            prev = self.completions[key][-1]
            diff = (timestamp - prev.timestamp).total_seconds()
            completion.seconds_since_previous = diff
        
        self.completions[key].append(completion)
        
        # Check for gaming patterns
        return self._check_patterns(completion)
    
    def _check_patterns(
        self,
        completion: HabitCompletion
    ) -> Optional[GamingIndicator]:
        """Check for gaming patterns."""
        import uuid
        
        key = f"{completion.user_id}_{completion.habit_id}"
        history = self.completions.get(key, [])
        
        # Need at least 3 completions to detect patterns
        if len(history) < 3:
            return None
        
        indicators = []
        
        # Check rapid completion (less than 10 seconds)
        if completion.seconds_since_previous is not None:
            if completion.seconds_since_previous < 10:
                indicators.append(GamingIndicator(
                    id=str(uuid.uuid4()),
                    user_id=completion.user_id,
                    habit_id=completion.habit_id,
                    pattern=GamingPattern.RAPID_COMPLETION,
                    detected_at=datetime.now(),
                    evidence=f"Completed in {completion.seconds_since_previous:.1f}s",
                    confidence=0.9,
                    risk_level=RiskLevel.MODERATE
                ))
        
        # Check consistency anomaly (too perfect)
        if len(history) >= 7:
            times = [c.timestamp.hour for c in history[-7:]]
            if len(set(times)) <= 2:  # Same time every day
                indicators.append(GamingIndicator(
                    id=str(uuid.uuid4()),
                    user_id=completion.user_id,
                    habit_id=completion.habit_id,
                    pattern=GamingPattern.CONSISTENCY_ANOMALY,
                    detected_at=datetime.now(),
                    evidence=f"Same time every day: {times[0]}:00",
                    confidence=0.6,
                    risk_level=RiskLevel.LOW
                ))
        
        # Check perfectionism (never missing over 30 days)
        if len(history) >= 30:
            # This would need actual date analysis
            pass
        
        # Store indicators
        for ind in indicators:
            self.indicators.append(ind)
        
        return indicators[0] if indicators else None
    
    def get_risk_assessment(self, user_id: str) -> Dict:
        """Get overall risk assessment for a user."""
        user_indicators = [
            i for i in self.indicators
            if i.user_id == user_id
        ]
        
        if not user_indicators:
            return {
                "risk_level": "none",
                "total_indicators": 0,
                "patterns": [],
                "recommendation": "No gaming detected"
            }
        
        # Calculate risk
        high_count = sum(1 for i in user_indicators if i.risk_level == RiskLevel.HIGH)
        mod_count = sum(1 for i in user_indicators if i.risk_level == RiskLevel.MODERATE)
        
        if high_count > 0:
            risk = "high"
            rec = "Consider having a conversation about tracking honestly"
        elif mod_count > 2:
            risk = "moderate"
            rec = "Gaming patterns detected - focus on process over streaks"
        elif mod_count > 0:
            risk = "low"
            rec = "Minor patterns - monitor closely"
        else:
            risk = "minimal"
            rec = "Keep tracking honestly"
        
        patterns = list(set(i.pattern.value for i in user_indicators))
        
        return {
            "risk_level": risk,
            "total_indicators": len(user_indicators),
            "patterns": patterns,
            "recommendation": rec
        }
    
    def get_intervention(self, pattern: GamingPattern) -> str:
        """Get an intervention message for a pattern."""
        interventions = {
            GamingPattern.RAPID_COMPLETION:
                "Take your time - this is about real change, not speed.",
            GamingPattern.BACKDATING:
                "Focus on today - past days are done. What can you do now?",
            GamingPattern.STREAK_GAMING:
                "Streaks are for motivation, not the goal itself.",
            GamingPattern.PERFECTIONISM:
                "Missing a day doesn't erase progress. Consistency matters more than perfection.",
            GamingPattern.SELECTIVE_REPORTING:
                "Every habit counts - even the hard ones matter.",
            GamingPattern.CONSISTENCY_ANOMALY:
                "Your consistency is great! But variety can help too."
        }
        return interventions.get(pattern, "Focus on the process, not the numbers.")


def create_detector() -> SelfGamingDetector:
    """Factory function."""
    return SelfGamingDetector()
