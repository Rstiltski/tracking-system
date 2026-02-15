"""
Frequency Model - Defines how often a habit should be performed.

Based on Loop Habit Tracker's frequency system:
- Daily: Perform every day
- Weekly: Perform X times per week
- Custom: Perform X times every Y days

The frequency value is used in the score calculation to determine
how quickly scores decay and how they're computed.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Tuple


class FrequencyType(str, Enum):
    """Types of habit frequencies."""
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


@dataclass
class Frequency:
    """
    Defines how often a habit should be performed.
    
    The frequency is expressed as a ratio: numerator / denominator
    - Daily: 1/1 (once per day)
    - Weekly 3x: 3/7 (three times per week)
    - Custom: X/Y (X times every Y days)
    
    This ratio is used in the exponential smoothing formula to
    calibrate the score decay rate.
    
    Attributes:
        numerator: Number of times to perform the habit
        denominator: Number of days in the period
        freq_type: The type of frequency (daily, weekly, custom)
    
    Example:
        >>> daily = Frequency.daily()
        >>> daily.value
        1.0
        >>> weekly = Frequency.weekly(times=3)
        >>> weekly.value
        0.42857142857142855  # 3/7
    """
    numerator: int
    denominator: int
    freq_type: FrequencyType = FrequencyType.DAILY
    
    @classmethod
    def daily(cls) -> "Frequency":
        """Create a daily frequency (once per day)."""
        return cls(numerator=1, denominator=1, freq_type=FrequencyType.DAILY)
    
    @classmethod
    def weekly(cls, times: int = 1) -> "Frequency":
        """
        Create a weekly frequency.
        
        Args:
            times: Number of times per week (default: 1)
        
        Returns:
            Frequency with times/7 ratio
        """
        return cls(numerator=times, denominator=7, freq_type=FrequencyType.WEEKLY)
    
    @classmethod
    def custom(cls, times: int, period_days: int) -> "Frequency":
        """
        Create a custom frequency.
        
        Args:
            times: Number of times to perform
            period_days: Number of days in the period
        
        Returns:
            Frequency with times/period_days ratio
        """
        return cls(numerator=times, denominator=period_days, freq_type=FrequencyType.CUSTOM)
    
    @property
    def value(self) -> float:
        """
        Get the frequency as a decimal value.
        
        This is used in the score calculation formula.
        Higher values mean more frequent habits.
        
        Returns:
            Frequency ratio as float (numerator / denominator)
        """
        if self.denominator == 0:
            return 0.0
        return self.numerator / self.denominator
    
    def __str__(self) -> str:
        """Human-readable frequency description."""
        if self.freq_type == FrequencyType.DAILY:
            return "Daily"
        elif self.freq_type == FrequencyType.WEEKLY:
            if self.numerator == 1:
                return "Once a week"
            elif self.numerator == 7:
                return "Every day"
            return f"{self.numerator} times per week"
        else:
            return f"{self.numerator} times every {self.denominator} days"
    
    def to_tuple(self) -> Tuple[int, int]:
        """Convert to tuple for serialization."""
        return (self.numerator, self.denominator)
    
    @classmethod
    def from_tuple(cls, data: Tuple[int, int]) -> "Frequency":
        """Create from tuple (for deserialization)."""
        num, denom = data
        if denom == 1:
            return cls.daily()
        elif denom == 7:
            return cls.weekly(times=num)
        else:
            return cls.custom(times=num, period_days=denom)