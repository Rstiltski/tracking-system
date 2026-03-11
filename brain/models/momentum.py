"""
Momentum Model - 4-Day Momentum Principle Implementation

Implements research-backed 4-day momentum threshold for habits:
- Day 1-2: Novelty, conscious effort
- Day 3: Critical point (most drop off)
- Day 4: Momentum threshold crossed - CELEBRATION!
- Day 5+: Habit becoming automatic

Based on research from:
- "The Algorithmic Self" - behavioral psychology insights
- Habit formation science (Lally et al.)
- DECISION_037, DECISION_038 research documentation
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, Optional, List
from enum import Enum


# =============================================================================
# CONSTANTS
# =============================================================================

# The magic number - Day 4 is when momentum threshold is crossed
MOMENTUM_THRESHOLD_DAY = 4

# Buffer days after a miss before momentum resets (psychological safety net)
MOMENTUM_BUFFER_DAYS = 1

# Messages for each day of momentum build-up
MOMENTUM_MESSAGES: Dict[int, str] = {
    1: "Day 1 - You've started! Every journey begins with a single step.",
    2: "Day 2 - Great progress! You're building the foundation.",
    3: "Day 3 - CRITICAL POINT! Most people quit here. You're stronger!",
    4: "🎉 DAY 4 - MOMENTUM ACHIEVED! You've crossed the threshold!",
    5: "Day 5 - Momentum is carrying you now. Almost automatic!",
    6: "Day 6 - Your brain is adapting. Keep the flow going!",
    7: "Day 7 - One week strong! You're building a real habit.",
}

# Celebration messages for milestones
MOMENTUM_CELEBRATIONS: Dict[int, str] = {
    4: "🚀 MOMENTUM MASTERED! You've crossed the critical threshold!",
    7: "💪 WEEK WARRIOR! One full week of consistency!",
    14: "🌟 DOUBLE WEEK! Two weeks of unstoppable momentum!",
    30: "🏆 MONTH LEGEND! A full month of dedication!",
    60: "👑 TWO-MONTH TITAN! You've made this习惯 a lifestyle!",
    90: "🎖️ QUARTER CHAMPION! 90 days of incredible commitment!",
}


# =============================================================================
# ENUMS
# =============================================================================

class MomentumPhase(Enum):
    """The phase of momentum a habit is in."""
    NOT_STARTED = "not_started"
    NOVELTY = "novelty"           # Days 1-2
    CRITICAL = "critical"         # Day 3
    MOMENTUM = "momentum"         # Day 4+
    ESTABLISHED = "established"    # Day 7+


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class MomentumData:
    """
    Momentum tracking data for a single habit.
    
    Attributes:
        habit_id: The unique identifier of the habit
        current_day: Current momentum day (1-4+, resets on breaks)
        momentum_start_date: When the current momentum sequence started
        last_milestone: The last milestone day achieved (4, 7, 14, etc.)
        has_seen_milestone: Whether user has seen the Day 4 celebration
        consecutive_completions: Raw streak count (used for calculations)
    """
    habit_id: str = ""
    current_day: int = 0
    momentum_start_date: Optional[date] = None
    last_milestone: int = 0
    has_seen_milestone: bool = False
    consecutive_completions: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "habit_id": self.habit_id,
            "current_day": self.current_day,
            "momentum_start_date": self.momentum_start_date.isoformat() if self.momentum_start_date else None,
            "last_milestone": self.last_milestone,
            "has_seen_milestone": self.has_seen_milestone,
            "consecutive_completions": self.consecutive_completions,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MomentumData":
        """Create instance from dictionary."""
        return cls(
            habit_id=data.get("habit_id", ""),
            current_day=data.get("current_day", 0),
            momentum_start_date=date.fromisoformat(data["momentum_start_date"]) if data.get("momentum_start_date") else None,
            last_milestone=data.get("last_milestone", 0),
            has_seen_milestone=data.get("has_seen_milestone", False),
            consecutive_completions=data.get("consecutive_completions", 0),
        )


# =============================================================================
# MOMENTUM TRACKER
# =============================================================================

class MomentumTracker:
    """
    Tracks and calculates momentum for habits.
    
    The 4-Day Momentum Principle:
    - Day 1-2: Novelty phase - conscious effort required
    - Day 3: Critical point - highest drop-off risk
    - Day 4+: Momentum achieved - habit becoming automatic
    
    This creates a psychological "buffer" that helps users push through
    the critical Day 3 point.
    """
    
    def __init__(self):
        """Initialize the momentum tracker."""
        self._momentum_data: Dict[str, MomentumData] = {}
    
    def get_momentum(self, habit_id: str) -> MomentumData:
        """Get momentum data for a habit, creating if needed."""
        if habit_id not in self._momentum_data:
            self._momentum_data[habit_id] = MomentumData(habit_id=habit_id)
        return self._momentum_data[habit_id]
    
    def update_on_completion(self, habit_id: str, completion_date: date = None) -> MomentumData:
        """
        Update momentum when a habit is completed.
        
        Args:
            habit_id: The habit being completed
            completion_date: The date of completion (default: today)
            
        Returns:
            Updated MomentumData with new momentum state
        """
        if completion_date is None:
            completion_date = date.today()
        
        momentum = self.get_momentum(habit_id)
        
        # Check if this is a new day of completion
        if momentum.momentum_start_date is None:
            # First ever completion
            momentum.momentum_start_date = completion_date
            momentum.current_day = 1
            momentum.consecutive_completions = 1
        else:
            # Check if this is consecutive (or within buffer)
            days_diff = (completion_date - momentum.momentum_start_date).days
            
            if days_diff <= momentum.consecutive_completions + MOMENTUM_BUFFER_DAYS:
                # Consecutive or within buffer - continue momentum
                momentum.consecutive_completions += 1
                momentum.current_day = min(momentum.consecutive_completions, MOMENTUM_THRESHOLD_DAY + 3)
            else:
                # Gap too large - reset momentum
                momentum.momentum_start_date = completion_date
                momentum.current_day = 1
                momentum.consecutive_completions = 1
                momentum.has_seen_milestone = False
        
        # Check for milestone achievements
        self._check_milestones(momentum)
        
        return momentum
    
    def _check_milestones(self, momentum: MomentumData) -> Optional[int]:
        """
        Check if a milestone has been reached.
        
        Returns:
            The milestone day achieved, or None if no milestone
        """
        current = momentum.current_day
        last = momentum.last_milestone
        
        # Check for Day 4 (the main momentum threshold)
        if current >= MOMENTUM_THRESHOLD_DAY and last < MOMENTUM_THRESHOLD_DAY:
            momentum.last_milestone = MOMENTUM_THRESHOLD_DAY
            momentum.has_seen_milestone = True
            return MOMENTUM_THRESHOLD_DAY
        
        # Check for week milestones
        for milestone in [7, 14, 30, 60, 90]:
            if current >= milestone and last < milestone:
                momentum.last_milestone = milestone
                return milestone
        
        return None
    
    def get_phase(self, momentum: MomentumData) -> MomentumPhase:
        """
        Get the current momentum phase based on streak.
        
        Returns:
            The current MomentumPhase
        """
        day = momentum.current_day
        
        if day == 0:
            return MomentumPhase.NOT_STARTED
        elif day <= 2:
            return MomentumPhase.NOVELTY
        elif day == 3:
            return MomentumPhase.CRITICAL
        elif day >= 4 and day < 7:
            return MomentumPhase.MOMENTUM
        else:
            return MomentumPhase.ESTABLISHED
    
    def get_message(self, momentum: MomentumData) -> str:
        """
        Get the appropriate momentum message for the current day.
        
        Returns:
            Motivational message for the current momentum day
        """
        day = momentum.current_day
        
        if day == 0:
            return "Start your momentum journey today!"
        
        # Use specific message if available, otherwise use Day 5+ template
        if day in MOMENTUM_MESSAGES:
            return MOMENTUM_MESSAGES[day]
        else:
            return f"Day {day} - You've built an amazing habit! Keep going!"
    
    def get_celebration(self, momentum: MomentumData) -> Optional[str]:
        """
        Get celebration message if a milestone was just achieved.
        
        Returns:
            Celebration message, or None if no new milestone
        """
        milestone = momentum.last_milestone
        
        if milestone in MOMENTUM_CELEBRATIONS:
            return MOMENTUM_CELEBRATIONS[milestone]
        
        return None
    
    def is_momentum_achieved(self, momentum: MomentumData) -> bool:
        """Check if momentum threshold (Day 4) has been achieved."""
        return momentum.current_day >= MOMENTUM_THRESHOLD_DAY
    
    def get_progress_to_momentum(self, momentum: MomentumData) -> float:
        """
        Get progress toward momentum threshold as a percentage.
        
        Returns:
            Float between 0.0 and 1.0
        """
        if momentum.current_day >= MOMENTUM_THRESHOLD_DAY:
            return 1.0
        
        return momentum.current_day / MOMENTUM_THRESHOLD_DAY
    
    def reset_momentum(self, habit_id: str) -> None:
        """Reset momentum for a habit (e.g., after extended break)."""
        if habit_id in self._momentum_data:
            self._momentum_data[habit_id] = MomentumData(habit_id=habit_id)
    
    def get_all_momentum(self) -> List[MomentumData]:
        """Get all momentum data."""
        return list(self._momentum_data.values())
    
    def load_from_dict(self, data: Dict[str, Dict]) -> None:
        """Load momentum data from a dictionary."""
        self._momentum_data = {
            hid: MomentumData.from_dict(d) 
            for hid, d in data.items()
        }
    
    def to_dict(self) -> Dict[str, Dict]:
        """Convert all momentum data to dictionary for storage."""
        return {
            hid: momentum.to_dict() 
            for hid, momentum in self._momentum_data.items()
        }


# =============================================================================
# STREAK INTEGRATION
# =============================================================================

def calculate_momentum_from_streak(streak_count: int) -> int:
    """
    Calculate momentum day from a raw streak count.
    
    Args:
        streak_count: The consecutive day streak
        
    Returns:
        The momentum day (capped at reasonable max for display)
    """
    if streak_count == 0:
        return 0
    elif streak_count <= MOMENTUM_THRESHOLD_DAY:
        return streak_count
    else:
        # For Day 5+, return capped value for display purposes
        return min(streak_count, MOMENTUM_THRESHOLD_DAY + 3)


# =============================================================================
# FACTORY
# =============================================================================

def create_momentum_tracker() -> MomentumTracker:
    """Factory function to create a new MomentumTracker."""
    return MomentumTracker()
