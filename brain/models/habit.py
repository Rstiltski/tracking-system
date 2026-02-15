"""
Habit Model - Core habit entity with scientific scoring.

Based on Loop Habit Tracker's scoring system with enhancements from
behavioral science research:

1. Exponential Smoothing (Loop's algorithm):
   - Score from 0.0 to 1.0 (displayed as 0-100%)
   - Frequency-aware multiplier: 0.5^(√frequency / 13)
   - Recent days have higher weight
   - Gradual decay on misses, not reset to zero

2. Holt's Linear Trend (enhancement):
   - Tracks momentum (trend) in addition to score
   - Can detect "burnout spirals" before score drops
   - Enables predictive capabilities

3. Calibrated for 66-day mastery:
   - Alpha (α) = 0.052 for level smoothing
   - Beta (β) = 0.01 for trend smoothing
   - After 66 consecutive days, score reaches ~97%

References:
- Loop Habit Tracker: https://github.com/iSoron/uhabits
- Lally et al. (2010): 66 days to habit formation
- Research document: Habit Score Algorithm Research.docx
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from math import sqrt, pow
import uuid

from brain.models.frequency import Frequency
from brain.models.entry import Entry, EntryList, EntryType


class HabitType(str, Enum):
    """Types of habits."""
    BOOLEAN = "boolean"  # Simple yes/no habit
    NUMERICAL = "numerical"  # Track a number (e.g., glasses of water)


class NumericalHabitTarget(str, Enum):
    """Target type for numerical habits."""
    AT_LEAST = "at_least"  # At least X units
    AT_MOST = "at_most"  # At most X units


@dataclass
class HabitScore:
    """
    A habit score with trend tracking.
    
    Uses exponential smoothing with Holt's Linear Trend method.
    
    Attributes:
        value: The score value (0.0 to 1.0)
        trend: The momentum/trend (-1.0 to 1.0)
        timestamp: The date this score was computed for
    """
    value: float = 0.0
    trend: float = 0.0
    timestamp: date = field(default_factory=date.today)
    
    @property
    def percentage(self) -> int:
        """Get score as percentage (0-100)."""
        return round(max(0.0, min(1.0, self.value)) * 100)
    
    @property
    def trend_percentage(self) -> int:
        """Get trend as percentage (-100 to 100)."""
        return round(self.trend * 100)
    
    def get_category(self) -> Dict[str, str]:
        """
        Get the score category for display.
        
        Returns:
            Dict with 'label', 'color', and 'emoji' keys
        """
        if self.value >= 0.85:
            return {"label": "Excellent", "color": "#4CAF50", "emoji": "🌟"}
        elif self.value >= 0.70:
            return {"label": "Strong", "color": "#8BC34A", "emoji": "💪"}
        elif self.value >= 0.50:
            return {"label": "Developing", "color": "#FFC107", "emoji": "🌱"}
        elif self.value >= 0.30:
            return {"label": "Building", "color": "#FF9800", "emoji": "🔧"}
        else:
            return {"label": "Starting", "color": "#F44336", "emoji": "🆕"}
    
    @classmethod
    def compute(
        cls,
        frequency: float,
        previous_score: float,
        checkmark_value: float,
        previous_trend: float = 0.0,
        alpha: float = 0.052,
        beta: float = 0.01,
        timestamp: Optional[date] = None
    ) -> "HabitScore":
        """
        Compute a new habit score using exponential smoothing.
        
        This implements Loop's frequency-aware scoring with Holt's Linear
        Trend enhancement from the research document.
        
        The formula:
        - Multiplier: 0.5^(√frequency / 13)
        - Level: α * checkmark + (1-α) * (prev_level + prev_trend)
        - Trend: β * (level - prev_level) + (1-β) * prev_trend
        
        Args:
            frequency: The habit frequency (repetitions/days), e.g., 1.0 for daily
            previous_score: The previous day's score (0.0-1.0)
            checkmark_value: Today's value (1.0 = done, 0.0 = missed)
            previous_trend: The previous trend value
            alpha: Smoothing factor for level (default: 0.052 for 66-day mastery)
            beta: Smoothing factor for trend (default: 0.01)
            timestamp: The date for this score (default: today)
        
        Returns:
            New HabitScore with updated value and trend
        """
        # Loop's frequency-aware multiplier
        # For daily habits (freq=1.0): multiplier ≈ 0.95
        # For weekly habits (freq=0.14): multiplier ≈ 0.88
        multiplier = pow(0.5, sqrt(frequency) / 13.0)
        
        # Apply the multiplier to get effective alpha
        # This makes less frequent habits decay faster
        effective_alpha = 1 - multiplier
        
        # Holt's Linear Trend Method
        # Level equation: captures the current "height" of the habit
        level = effective_alpha * checkmark_value + multiplier * (previous_score + previous_trend)
        
        # Trend equation: captures the momentum
        trend = beta * (level - previous_score) + (1 - beta) * previous_trend
        
        # Clamp values to valid range
        level = max(0.0, min(1.0, level))
        
        return cls(
            value=level,
            trend=trend,
            timestamp=timestamp or date.today()
        )
    
    def __str__(self) -> str:
        """String representation."""
        category = self.get_category()
        trend_str = "↑" if self.trend > 0.001 else "↓" if self.trend < -0.001 else "→"
        return f"{self.percentage}% {category['emoji']} {category['label']} {trend_str}"


@dataclass
class ScoreList:
    """
    A list of habit scores over time.
    
    Handles recomputing scores based on entries and frequency.
    Based on Loop's ScoreList.kt implementation.
    
    Attributes:
        scores: Dictionary mapping date to HabitScore
    """
    scores: Dict[date, HabitScore] = field(default_factory=dict)
    
    def get(self, score_date: date) -> HabitScore:
        """Get score for a date, returns zero score if not found."""
        if score_date in self.scores:
            return self.scores[score_date]
        return HabitScore(value=0.0, timestamp=score_date)
    
    def get_by_interval(self, from_date: date, to_date: date) -> List[HabitScore]:
        """
        Get all scores in a date interval.
        
        Args:
            from_date: Start date (inclusive)
            to_date: End date (inclusive)
        
        Returns:
            List of scores ordered by date (newest first)
        """
        result = []
        current = to_date
        
        while current >= from_date:
            result.append(self.get(current))
            current -= timedelta(days=1)
        
        return result
    
    def recompute(
        self,
        frequency: Frequency,
        entries: EntryList,
        from_date: date,
        to_date: date,
        is_numerical: bool = False,
        target_value: float = 0.0,
        numerical_target_type: NumericalHabitTarget = NumericalHabitTarget.AT_LEAST
    ) -> None:
        """
        Recompute all scores based on entries.
        
        This is the core algorithm that iterates through each day
        and computes the score using exponential smoothing.
        
        Args:
            frequency: The habit's frequency
            entries: The list of habit entries
            from_date: Start date for computation
            to_date: End date for computation
            is_numerical: Whether this is a numerical habit
            target_value: Target value for numerical habits
            numerical_target_type: Target type for numerical habits
        """
        self.scores.clear()
        
        freq = frequency.value
        
        # For non-daily boolean habits, double numerator and denominator
        # to smooth out irregular schedules (from Loop's implementation)
        numerator = frequency.numerator
        denominator = frequency.denominator
        
        if not is_numerical and freq < 1.0:
            numerator *= 2
            denominator *= 2
        
        # Get all entry values in the interval (oldest first)
        entry_values = entries.get_values_by_interval(from_date, to_date)
        
        # Rolling sum for percentage calculation
        rolling_sum = 0.0
        
        # Initial score
        previous_score = 0.0
        previous_trend = 0.0
        
        # Iterate through each day
        for i, checkmark_value in enumerate(entry_values):
            # Skip entries (value = -1) don't affect the score
            if checkmark_value == -1:
                # Just carry forward the previous score
                current_date = from_date + timedelta(days=i)
                self.scores[current_date] = HabitScore(
                    value=previous_score,
                    trend=previous_trend,
                    timestamp=current_date
                )
                continue
            
            # Update rolling sum for percentage calculation
            if checkmark_value > 0:
                rolling_sum += 1.0
            
            # Remove old value from rolling sum
            if i >= denominator and entry_values[i - denominator] > 0:
                rolling_sum -= 1.0
            
            # Calculate percentage completed
            percentage_completed = min(1.0, rolling_sum / numerator) if numerator > 0 else 0.0
            
            # Compute the new score
            current_date = from_date + timedelta(days=i)
            score = HabitScore.compute(
                frequency=freq,
                previous_score=previous_score,
                checkmark_value=percentage_completed,
                previous_trend=previous_trend,
                timestamp=current_date
            )
            
            self.scores[current_date] = score
            previous_score = score.value
            previous_trend = score.trend
    
    @property
    def current(self) -> HabitScore:
        """Get the most recent score."""
        if not self.scores:
            return HabitScore()
        latest_date = max(self.scores.keys())
        return self.scores[latest_date]
    
    @property
    def average(self) -> float:
        """Get the average score value."""
        if not self.scores:
            return 0.0
        return sum(s.value for s in self.scores.values()) / len(self.scores)


@dataclass
class Habit:
    """
    A habit entity with scoring capabilities.
    
    Attributes:
        id: Unique identifier
        name: Habit name
        description: Optional description
        frequency: How often to perform this habit
        habit_type: Boolean or numerical
        color: Color for display (hex string)
        icon: Emoji icon for display
        target_value: Target for numerical habits
        target_type: Target type for numerical habits
        created_at: Creation date
        is_archived: Whether this habit is archived
        entries: List of completion entries
        scores: Computed scores
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    frequency: Frequency = field(default_factory=Frequency.daily)
    habit_type: HabitType = HabitType.BOOLEAN
    color: str = "#6366f1"
    icon: str = "🎯"
    target_value: float = 0.0
    target_type: NumericalHabitTarget = NumericalHabitTarget.AT_LEAST
    created_at: date = field(default_factory=date.today)
    is_archived: bool = False
    entries: EntryList = field(default_factory=EntryList)
    scores: ScoreList = field(default_factory=ScoreList)
    
    def __post_init__(self):
        """Ensure entries have the habit_id set."""
        self.entries.habit_id = self.id
    
    @property
    def score(self) -> HabitScore:
        """Get the current habit score."""
        return self.scores.current
    
    @property
    def streak_count(self) -> int:
        """Get the current streak count."""
        return self._calculate_streak()
    
    def _calculate_streak(self) -> int:
        """
        Calculate the current streak.
        
        A streak is consecutive days of completion ending today or yesterday.
        """
        streak = 0
        current = date.today()
        
        # Check if completed today, if not start from yesterday
        today_entry = self.entries.get(current)
        if not today_entry.is_completed:
            current -= timedelta(days=1)
        
        # Count consecutive completions
        while True:
            entry = self.entries.get(current)
            if entry.is_completed:
                streak += 1
                current -= timedelta(days=1)
            elif entry.is_skip:
                # Skip days don't break the streak
                current -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def mark_completed(self, entry_date: Optional[date] = None, notes: str = "") -> Entry:
        """
        Mark this habit as completed for a date.
        
        Args:
            entry_date: Date to mark (default: today)
            notes: Optional notes
        
        Returns:
            The created entry
        """
        entry_date = entry_date or date.today()
        entry = self.entries.mark_completed(entry_date, notes)
        self._recompute_scores()
        return entry
    
    def mark_skipped(self, entry_date: Optional[date] = None, notes: str = "") -> Entry:
        """
        Mark this habit as skipped for a date.
        
        Skipped days don't affect the score.
        
        Args:
            entry_date: Date to mark (default: today)
            notes: Optional notes
        
        Returns:
            The created entry
        """
        entry_date = entry_date or date.today()
        entry = self.entries.mark_skipped(entry_date, notes)
        self._recompute_scores()
        return entry
    
    def unmark(self, entry_date: Optional[date] = None) -> None:
        """
        Remove a completion mark for a date.
        
        Args:
            entry_date: Date to unmark (default: today)
        """
        entry_date = entry_date or date.today()
        self.entries.clear(entry_date)
        self._recompute_scores()
    
    def _recompute_scores(self) -> None:
        """Recompute all scores based on current entries."""
        if not self.entries.oldest_date:
            return
        
        from_date = self.entries.oldest_date
        to_date = date.today()
        
        self.scores.recompute(
            frequency=self.frequency,
            entries=self.entries,
            from_date=from_date,
            to_date=to_date,
            is_numerical=self.habit_type == HabitType.NUMERICAL,
            target_value=self.target_value,
            numerical_target_type=self.target_type
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency.to_tuple(),
            "habit_type": self.habit_type.value,
            "color": self.color,
            "icon": self.icon,
            "target_value": self.target_value,
            "target_type": self.target_type.value,
            "created_at": self.created_at.isoformat(),
            "is_archived": self.is_archived,
            "score": self.score.percentage,
            "streak": self.streak_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Habit":
        """Create from dictionary."""
        freq_data = data.get("frequency", (1, 1))
        frequency = Frequency.from_tuple(freq_data) if isinstance(freq_data, tuple) else Frequency.daily()
        
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", ""),
            description=data.get("description", ""),
            frequency=frequency,
            habit_type=HabitType(data.get("habit_type", "boolean")),
            color=data.get("color", "#6366f1"),
            icon=data.get("icon", "🎯"),
            target_value=data.get("target_value", 0.0),
            target_type=NumericalHabitTarget(data.get("target_type", "at_least")),
            created_at=date.fromisoformat(data["created_at"]) if "created_at" in data else date.today(),
            is_archived=data.get("is_archived", False)
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.icon} {self.name}: {self.score}"