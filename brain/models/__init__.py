"""
Brain Models - Domain Models for TrackLife

This package contains the core domain models for the TrackLife habit tracking system.
Based on research from Loop Habit Tracker (uhabits) and behavioral science.

Key Models:
- Habit: A habit entity with scoring capabilities
- HabitScore: Exponential smoothing score (0.0-1.0) with trend tracking
- Entry: A completion record for a habit on a specific date
- Frequency: How often a habit should be performed
- Streak: Consecutive completion tracking with freeze support

Usage:
    from brain.models import Habit, HabitScore, Entry, Frequency
    
    # Create a daily habit
    habit = Habit(name="Morning Exercise", frequency=Frequency.daily())
    
    # Calculate score after some completions
    score = HabitScore.compute(
        frequency=habit.frequency.value,
        previous_score=0.75,
        checkmark_value=1.0  # Completed today
    )
    print(f"Score: {score.percentage}%")  # e.g., "Score: 76%"
"""

from brain.models.frequency import Frequency, FrequencyType
from brain.models.entry import Entry, EntryType, EntryList
from brain.models.habit import Habit, HabitType, HabitScore, ScoreList
from brain.models.streak import Streak, StreakList, StreakFreeze

__all__ = [
    # Frequency
    "Frequency",
    "FrequencyType",
    
    # Entry
    "Entry",
    "EntryType",
    "EntryList",
    
    # Habit
    "Habit",
    "HabitType",
    "HabitScore",
    "ScoreList",
    
    # Streak
    "Streak",
    "StreakList",
    "StreakFreeze",
]