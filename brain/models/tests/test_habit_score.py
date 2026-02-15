"""
Unit Tests for Habit Score Algorithm.

Tests the exponential smoothing algorithm based on Loop Habit Tracker
and behavioral science research.

Run with: pytest brain/models/tests/test_habit_score.py -v
"""
import pytest
from datetime import date, timedelta
from math import isclose

from brain.models.frequency import Frequency
from brain.models.entry import Entry, EntryList, EntryType
from brain.models.habit import Habit, HabitScore, ScoreList, HabitType
from brain.models.streak import StreakFreeze


class TestHabitScore:
    """Tests for the HabitScore class."""
    
    def test_score_initialization(self):
        """Test that a score can be initialized."""
        score = HabitScore(value=0.75, trend=0.01)
        
        assert score.value == 0.75
        assert score.trend == 0.01
        assert score.percentage == 75
    
    def test_score_percentage_clamping(self):
        """Test that percentage is clamped to 0-100."""
        # Value above 1.0
        score = HabitScore(value=1.5)
        assert score.percentage == 100
        
        # Value below 0.0
        score = HabitScore(value=-0.5)
        assert score.percentage == 0
    
    def test_score_categories(self):
        """Test score category classification."""
        test_cases = [
            (0.90, "Excellent", "🌟"),
            (0.85, "Excellent", "🌟"),
            (0.75, "Strong", "💪"),
            (0.70, "Strong", "💪"),
            (0.60, "Developing", "🌱"),
            (0.50, "Developing", "🌱"),
            (0.40, "Building", "🔧"),
            (0.30, "Building", "🔧"),
            (0.20, "Starting", "🆕"),
            (0.0, "Starting", "🆕"),
        ]
        
        for value, expected_label, expected_emoji in test_cases:
            score = HabitScore(value=value)
            category = score.get_category()
            assert category["label"] == expected_label, f"Failed for value {value}"
            assert category["emoji"] == expected_emoji, f"Failed for value {value}"
    
    def test_compute_score_daily_habit_first_day(self):
        """Test computing score for first day of a daily habit."""
        # First completion should give a small positive score
        score = HabitScore.compute(
            frequency=1.0,  # Daily
            previous_score=0.0,
            checkmark_value=1.0  # Completed
        )
        
        # Score should be positive but small (building up)
        assert score.value > 0
        assert score.value < 0.1  # First day shouldn't give high score
        assert score.trend >= 0  # Positive momentum
    
    def test_compute_score_decay_on_miss(self):
        """Test that score decays gradually on miss, not reset to zero."""
        # Start with a high score
        previous_score = 0.90
        
        # Miss a day
        score = HabitScore.compute(
            frequency=1.0,  # Daily
            previous_score=previous_score,
            checkmark_value=0.0  # Missed
        )
        
        # Score should decay but not reset to zero
        assert score.value < previous_score  # Decreased
        assert score.value > 0.5  # Still substantial (not reset to 0)
        assert score.trend < 0  # Negative momentum
    
    def test_compute_score_66_day_mastery(self):
        """Test that 66 consecutive days reaches ~97% score."""
        score_value = 0.0
        trend = 0.0
        
        # Simulate 66 consecutive days of completion
        for day in range(66):
            new_score = HabitScore.compute(
                frequency=1.0,
                previous_score=score_value,
                checkmark_value=1.0,
                previous_trend=trend
            )
            score_value = new_score.value
            trend = new_score.trend
        
        # After 66 days, should be close to mastery (97%)
        assert score_value >= 0.95, f"Expected >= 0.95 after 66 days, got {score_value}"
        assert score_value <= 1.0
    
    def test_compute_score_weekly_habit(self):
        """Test that weekly habits have different decay rate."""
        # Weekly habit (once per week = 1/7 ≈ 0.143)
        weekly_freq = 1.0 / 7.0
        
        score = HabitScore.compute(
            frequency=weekly_freq,
            previous_score=0.5,
            checkmark_value=1.0
        )
        
        # Should still work, just with different multiplier
        assert score.value > 0.5  # Increased
        assert score.value < 1.0
    
    def test_score_string_representation(self):
        """Test string representation of score."""
        score = HabitScore(value=0.75, trend=0.01)
        string_repr = str(score)
        
        assert "75%" in string_repr
        assert "Strong" in string_repr
        assert "💪" in string_repr


class TestFrequency:
    """Tests for the Frequency class."""
    
    def test_daily_frequency(self):
        """Test daily frequency creation."""
        freq = Frequency.daily()
        
        assert freq.value == 1.0
        assert str(freq) == "Daily"
    
    def test_weekly_frequency(self):
        """Test weekly frequency creation."""
        freq = Frequency.weekly(times=3)
        
        assert freq.value == 3.0 / 7.0
        assert "3 times per week" in str(freq)
    
    def test_custom_frequency(self):
        """Test custom frequency creation."""
        freq = Frequency.custom(times=5, period_days=14)
        
        assert freq.value == 5.0 / 14.0
        assert "5 times every 14 days" in str(freq)
    
    def test_frequency_tuple_conversion(self):
        """Test converting frequency to/from tuple."""
        freq = Frequency.weekly(times=3)
        tuple_data = freq.to_tuple()
        
        assert tuple_data == (3, 7)
        
        restored = Frequency.from_tuple(tuple_data)
        assert restored.value == freq.value


class TestEntry:
    """Tests for the Entry class."""
    
    def test_entry_creation(self):
        """Test creating an entry."""
        entry = Entry(
            date=date.today(),
            value=EntryType.YES_MANUAL
        )
        
        assert entry.is_completed
        assert not entry.is_skip
        assert not entry.is_failure
    
    def test_entry_types(self):
        """Test different entry types."""
        # Completed
        entry = Entry(date=date.today(), value=EntryType.YES_MANUAL)
        assert entry.is_completed
        assert entry.numeric_value == 1.0
        
        # Skipped
        entry = Entry(date=date.today(), value=EntryType.SKIP)
        assert entry.is_skip
        assert entry.numeric_value == -1  # Special marker
        
        # Failed
        entry = Entry(date=date.today(), value=EntryType.NO)
        assert entry.is_failure
        assert entry.numeric_value == 0.0
        
        # Unknown
        entry = Entry(date=date.today(), value=EntryType.UNKNOWN)
        assert not entry.is_completed
        assert entry.numeric_value == 0.0


class TestEntryList:
    """Tests for the EntryList class."""
    
    def test_entry_list_operations(self):
        """Test adding and retrieving entries."""
        entries = EntryList(habit_id="test")
        
        # Add entry
        entry = entries.mark_completed(date.today())
        
        assert len(entries) == 1
        assert entries.get(date.today()).is_completed
    
    def test_entry_list_gap_filling(self):
        """Test that get_by_interval fills gaps with UNKNOWN."""
        entries = EntryList(habit_id="test")
        
        # Add one entry
        entries.mark_completed(date.today())
        
        # Get interval including yesterday
        from_date = date.today() - timedelta(days=1)
        interval_entries = entries.get_by_interval(from_date, date.today())
        
        # Should have 2 entries (yesterday UNKNOWN, today completed)
        assert len(interval_entries) == 2
        assert interval_entries[0].is_completed  # Today (newest first)
        assert interval_entries[1].value == EntryType.UNKNOWN  # Yesterday
    
    def test_entry_list_count_completions(self):
        """Test counting completions."""
        entries = EntryList(habit_id="test")
        
        # Add 3 completions
        for i in range(3):
            entries.mark_completed(date.today() - timedelta(days=i))
        
        assert entries.count_completions() == 3


class TestHabit:
    """Tests for the Habit class."""
    
    def test_habit_creation(self):
        """Test creating a habit."""
        habit = Habit(
            name="Morning Exercise",
            frequency=Frequency.daily(),
            icon="🏃"
        )
        
        assert habit.name == "Morning Exercise"
        assert habit.frequency.value == 1.0
        assert habit.icon == "🏃"
        assert habit.habit_type == HabitType.BOOLEAN
    
    def test_habit_mark_completed(self):
        """Test marking a habit as completed."""
        habit = Habit(name="Test", frequency=Frequency.daily())
        
        # Mark completed
        habit.mark_completed(date.today())
        
        assert habit.entries.get(date.today()).is_completed
        assert habit.streak_count == 1
    
    def test_habit_streak_calculation(self):
        """Test streak calculation."""
        habit = Habit(name="Test", frequency=Frequency.daily())
        
        # Complete 5 days in a row
        for i in range(5):
            habit.mark_completed(date.today() - timedelta(days=4-i))
        
        assert habit.streak_count == 5
    
    def test_habit_streak_broken(self):
        """Test that streak breaks on missed day."""
        habit = Habit(name="Test", frequency=Frequency.daily())
        
        # Complete 3 days
        habit.mark_completed(date.today() - timedelta(days=3))
        habit.mark_completed(date.today() - timedelta(days=2))
        # Skip yesterday
        habit.mark_completed(date.today())
        
        # Streak should be 1 (only today)
        assert habit.streak_count == 1
    
    def test_habit_score_recomputation(self):
        """Test that score is recomputed after marking."""
        habit = Habit(name="Test", frequency=Frequency.daily())
        
        # Initial score should be 0
        assert habit.score.value == 0
        
        # Mark completed
        habit.mark_completed(date.today())
        
        # Score should now be positive
        assert habit.score.value > 0
    
    def test_habit_serialization(self):
        """Test habit serialization to dict."""
        habit = Habit(
            name="Test Habit",
            frequency=Frequency.weekly(times=3),
            icon="📚"
        )
        
        data = habit.to_dict()
        
        assert data["name"] == "Test Habit"
        assert data["frequency"] == (3, 7)
        assert data["icon"] == "📚"
        
        # Restore from dict
        restored = Habit.from_dict(data)
        assert restored.name == habit.name
        assert restored.frequency.value == habit.frequency.value


class TestStreakFreeze:
    """Tests for the StreakFreeze class."""
    
    def test_freeze_initialization(self):
        """Test streak freeze initialization."""
        freeze = StreakFreeze(count=3)
        
        assert freeze.count == 3
        assert freeze.is_available
        assert not freeze.is_maxed
    
    def test_freeze_usage(self):
        """Test using a streak freeze."""
        freeze = StreakFreeze(count=1)
        
        result = freeze.use_freeze("habit-1", date.today())
        
        assert result
        assert freeze.count == 0
        assert not freeze.is_available
    
    def test_freeze_purchase(self):
        """Test purchasing a streak freeze."""
        freeze = StreakFreeze(count=0, xp_cost=100)
        
        success, new_xp = freeze.purchase_freeze(150)
        
        assert success
        assert freeze.count == 1
        assert new_xp == 50
    
    def test_freeze_purchase_insufficient_xp(self):
        """Test purchasing with insufficient XP."""
        freeze = StreakFreeze(count=0, xp_cost=100)
        
        success, new_xp = freeze.purchase_freeze(50)
        
        assert not success
        assert freeze.count == 0
        assert new_xp == 50  # Unchanged
    
    def test_freeze_max_capacity(self):
        """Test max capacity limit."""
        freeze = StreakFreeze(count=10, max_freezes=10)
        
        success, _ = freeze.purchase_freeze(1000)
        
        assert not success  # Can't purchase when at max
    
    def test_freeze_award(self):
        """Test awarding a free freeze."""
        freeze = StreakFreeze(count=0)
        
        result = freeze.award_freeze("7-day streak")
        
        assert result
        assert freeze.count == 1


class TestScoreList:
    """Tests for the ScoreList class."""
    
    def test_score_list_recompute(self):
        """Test recomputing scores from entries."""
        scores = ScoreList()
        entries = EntryList(habit_id="test")
        frequency = Frequency.daily()
        
        # Add 10 days of completions
        for i in range(10):
            entries.mark_completed(date.today() - timedelta(days=9-i))
        
        # Recompute scores
        from_date = date.today() - timedelta(days=9)
        scores.recompute(
            frequency=frequency,
            entries=entries,
            from_date=from_date,
            to_date=date.today()
        )
        
        # Should have 10 scores
        assert len(scores.scores) == 10
        
        # Latest score should be positive
        assert scores.current.value > 0
    
    def test_score_list_current(self):
        """Test getting current score."""
        scores = ScoreList()
        
        # Add a score for today
        scores.scores[date.today()] = HabitScore(value=0.75)
        
        assert scores.current.value == 0.75


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])