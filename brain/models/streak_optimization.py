"""
Streak Effect Optimization

Optimize streak mechanics for motivation.

Based on Task 11.3.8 from PHASE_11_INTEGRATION_ROADMAP.md

Optimize streak mechanics - when they help vs hurt.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class StreakEffect(Enum):
    """How streaks affect behavior."""
    HELPFUL = "helpful"  # Motivates continuation
    HARMFUL = "harmful"  # Creates pressure/cheating
    NEUTRAL = "neutral"  # No effect


class StreakPhase(Enum):
    """Phases of streak lifecycle."""
    BUILDING = "building"  # Early days, establishing
    MOTIVATING = "motivating"  # Peak motivation
    PRESSURE = "pressure"  # Starting to feel负担
    CRISIS = "crisis"  # At risk of breaking or gaming


class InterventionType(Enum):
    """Types of streak interventions."""
    CELEBRATE = "celebrate"
    NORMALIZE = "normalize"
    ADJUST = "adjust"
    BREAK = "break_intentionally"


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class StreakProfile:
    """Profile for a habit's streak."""
    id: str
    user_id: str
    habit_id: str
    
    # Current streak
    current_streak: int
    longest_streak: int
    
    # Tracking
    start_date: datetime
    last_completion: Optional[datetime] = None
    
    # Effect tracking
    effect_history: List[Dict] = field(default_factory=list)
    crisis_events: int = 0
    
    # Optimization
    optimal_streak_length: int = 30  # When it becomes harmful


@dataclass
class StreakEvent:
    """An event related to streak."""
    id: str
    streak_id: str
    timestamp: datetime
    
    # Event
    event_type: str  # completion, near_miss, break, intervention
    streak_length: int
    
    # Context
    emotional_state: float  # -1 to 1
    note: str = ""


# =============================================================================
# STREAK OPTIMIZER
# =============================================================================

class StreakOptimizer:
    """
    Optimize streak mechanics.
    
    Features:
    - Track streak effects
    - Detect harmful patterns
    - Optimize streak length
    - Suggest interventions
    """
    
    def __init__(self):
        """Initialize the optimizer."""
        self.profiles: Dict[str, StreakProfile] = {}
        self.events: Dict[str, List[StreakEvent]] = {}
    
    def create_streak(
        self,
        user_id: str,
        habit_id: str,
        optimal_length: int = 30
    ) -> StreakProfile:
        """Create a streak profile."""
        import uuid
        
        profile = StreakProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            habit_id=habit_id,
            current_streak=0,
            longest_streak=0,
            start_date=datetime.now(),
            optimal_streak_length=optimal_length
        )
        
        self.profiles[profile.id] = profile
        self.events[profile.id] = []
        return profile
    
    def record_completion(
        self,
        streak_id: str,
        emotional_state: float = 0.0
    ) -> StreakEvent:
        """Record a streak completion."""
        import uuid
        
        profile = self.profiles.get(streak_id)
        if not profile:
            raise ValueError("Streak not found")
        
        now = datetime.now()
        
        # Check if streak continues
        if profile.last_completion:
            days_since = (now - profile.last_completion).days
            if days_since <= 1:
                profile.current_streak += 1
            else:
                profile.current_streak = 1  # Restart
        else:
            profile.current_streak = 1
        
        # Update longest
        if profile.current_streak > profile.longest_streak:
            profile.longest_streak = profile.current_streak
        
        profile.last_completion = now
        
        # Determine effect
        effect = self._calculate_effect(profile)
        
        # Record event
        event = StreakEvent(
            id=str(uuid.uuid4()),
            streak_id=streak_id,
            timestamp=now,
            event_type="completion",
            streak_length=profile.current_streak,
            emotional_state=emotional_state
        )
        
        self.events[streak_id].append(event)
        
        # Record effect
        profile.effect_history.append({
            "date": now,
            "streak": profile.current_streak,
            "effect": effect.value,
            "emotion": emotional_state
        })
        
        return event
    
    def _calculate_effect(self, profile: StreakProfile) -> StreakEffect:
        """Calculate the streak's current effect."""
        current = profile.current_streak
        optimal = profile.optimal_streak_length
        
        # Early streaks are helpful
        if current < optimal * 0.5:
            return StreakEffect.HELPFUL
        # Near optimal - still helpful
        elif current < optimal:
            return StreakEffect.HELPFUL
        # Past optimal - potentially harmful
        elif current < optimal * 1.5:
            profile.crisis_events += 1
            return StreakEffect.NEUTRAL
        else:
            profile.crisis_events += 2
            return StreakEffect.HARMFUL
    
    def get_streak_phase(self, streak_id: str) -> StreakPhase:
        """Get the current streak phase."""
        profile = self.profiles.get(streak_id)
        if not profile:
            return StreakPhase.BUILDING
        
        current = profile.current_streak
        optimal = profile.optimal_streak_length
        
        if current < 7:
            return StreakPhase.BUILDING
        elif current < optimal * 0.7:
            return StreakPhase.MOTIVATING
        elif current < optimal:
            return StreakPhase.PRESSURE
        else:
            return StreakPhase.CRISIS
    
    def suggest_intervention(self, streak_id: str) -> Dict:
        """Suggest an intervention."""
        profile = self.profiles.get(streak_id)
        if not profile:
            return {"type": "none", "message": "No streak found"}
        
        phase = self.get_streak_phase(streak_id)
        
        interventions = {
            StreakPhase.BUILDING: {
                "type": InterventionType.CELEBRATE.value,
                "message": "Great start! Keep building the habit.",
                "priority": "low"
            },
            StreakPhase.MOTIVATING: {
                "type": InterventionType.CELEBRATE.value,
                "message": "You're on fire! Momentum is building.",
                "priority": "low"
            },
            StreakPhase.PRESSURE: {
                "type": InterventionType.NORMALIZE.value,
                "message": "Remember, missing one day doesn't erase your progress.",
                "priority": "medium"
            },
            StreakPhase.CRISIS: {
                "type": InterventionType.ADJUST.value,
                "message": "Consider taking a deliberate break or adjusting the habit. "
                          "Your streak has served its purpose.",
                "priority": "high"
            }
        }
        
        return interventions.get(phase, {"type": "none", "message": "Keep going"})
    
    def get_streak_report(self, streak_id: str) -> Dict:
        """Get a detailed streak report."""
        profile = self.profiles.get(streak_id)
        if not profile:
            return {}
        
        events = self.events.get(streak_id, [])
        phase = self.get_streak_phase(streak_id)
        effect = self._calculate_effect(profile)
        intervention = self.suggest_intervention(streak_id)
        
        # Calculate emotion trend
        if len(events) >= 2:
            emotion_trend = "improving" if events[-1].emotional_state > events[0].emotional_state else "declining"
        else:
            emotion_trend = "stable"
        
        return {
            "current_streak": profile.current_streak,
            "longest_streak": profile.longest_streak,
            "optimal_length": profile.optimal_streak_length,
            "phase": phase.value,
            "effect": effect.value,
            "crisis_events": profile.crisis_events,
            "emotion_trend": emotion_trend,
            "intervention": intervention,
            "recommendation": intervention.get("message", "")
        }


def create_optimizer() -> StreakOptimizer:
    """Factory function."""
    return StreakOptimizer()
