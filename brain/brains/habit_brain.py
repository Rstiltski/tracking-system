"""
HabitBrain - Brain for habit tracking operations.

This brain handles all habit-related operations following the
7-Lobe Cortical Model architecture pattern used in the brain system.

Responsibilities:
- Create, update, delete habits
- Track habit completions
- Calculate and manage habit scores
- Manage streak freezes
- Provide habit analytics
- Emit events for all operations (Event Sourcing)

Usage:
    from brain.brains.habit_brain import HabitBrain
    
    brain = HabitBrain()
    
    # Create a habit
    habit = brain.create_habit("Morning Exercise", frequency="daily")
    
    # Mark as completed
    brain.mark_completed(habit.id)
    
    # Get score
    score = brain.get_score(habit.id)
    print(f"Score: {score.percentage}%")
"""
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import json

from brain.models import (
    Habit, HabitType, HabitScore, ScoreList,
    Entry, EntryType, EntryList,
    Frequency, FrequencyType,
    Streak, StreakList, StreakFreeze, UserInventory
)
from brain.core.result import Result
from brain.audit.habit_events import (
    HabitCreated, HabitUpdated, HabitCompleted, HabitUnmarked,
    HabitSkipped, HabitArchived, HabitDeleted,
    StreakFreezeUsed, StreakFreezePurchased, StreakFreezeAwarded,
    ScoreRecomputed
)
from brain.audit.event_store import get_event_publisher, get_event_store


@dataclass
class HabitBrain:
    """
    Brain for habit tracking operations.
    
    Follows the brain architecture pattern with:
    - State management (habits list)
    - Operations (CRUD + scoring)
    - Analytics (score history, streaks)
    
    Attributes:
        habits: Dictionary of habits by ID
        inventory: User inventory (XP, streak freezes)
    """
    habits: Dict[str, Habit] = field(default_factory=dict)
    inventory: UserInventory = field(default_factory=UserInventory)
    
    # === Habit CRUD Operations ===
    
    def create_habit(
        self,
        name: str,
        frequency: str = "daily",
        times_per_week: int = 1,
        times_per_period: int = 1,
        period_days: int = 1,
        description: str = "",
        icon: str = "🎯",
        color: str = "#6366f1",
        habit_type: str = "boolean"
    ) -> Result[Habit]:
        """
        Create a new habit.
        
        Args:
            name: Habit name
            frequency: "daily", "weekly", or "custom"
            times_per_week: For weekly habits, how many times per week
            times_per_period: For custom habits, how many times
            period_days: For custom habits, over how many days
            description: Optional description
            icon: Emoji icon
            color: Hex color
            habit_type: "boolean" or "numerical"
        
        Returns:
            Result with the created habit
        """
        try:
            # Create frequency
            if frequency == "daily":
                freq = Frequency.daily()
            elif frequency == "weekly":
                freq = Frequency.weekly(times=times_per_week)
            else:
                freq = Frequency.custom(times=times_per_period, period_days=period_days)
            
            # Create habit
            habit = Habit(
                name=name,
                description=description,
                frequency=freq,
                icon=icon,
                color=color,
                habit_type=HabitType(habit_type)
            )
            
            self.habits[habit.id] = habit
            
            # Emit HABIT_CREATED event
            try:
                event = HabitCreated.create(
                    habit_id=habit.id,
                    name=name,
                    frequency=(freq.numerator, freq.denominator),
                    description=description,
                    habit_type=habit_type,
                    color=color,
                    icon=icon
                )
                get_event_publisher().publish(event)
            except Exception:
                pass  # Don't fail if event emission fails
            
            return Result.success(
                habit,
                f"Created habit: {name}"
            )
        except Exception as e:
            return Result.failure(f"Failed to create habit: {str(e)}")
    
    def get_habit(self, habit_id: str) -> Optional[Habit]:
        """Get a habit by ID."""
        return self.habits.get(habit_id)
    
    def get_all_habits(self, include_archived: bool = False) -> List[Habit]:
        """
        Get all habits.
        
        Args:
            include_archived: Whether to include archived habits
        
        Returns:
            List of habits
        """
        habits = list(self.habits.values())
        if not include_archived:
            habits = [h for h in habits if not h.is_archived]
        return habits
    
    def update_habit(
        self,
        habit_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        frequency: Optional[str] = None,
        times_per_week: Optional[int] = None
    ) -> Result[Habit]:
        """
        Update a habit.
        
        Args:
            habit_id: ID of habit to update
            Other args: Fields to update
        
        Returns:
            Result with updated habit
        """
        habit = self.habits.get(habit_id)
        if not habit:
            return Result.failure(f"Habit not found: {habit_id}")
        
        try:
            if name is not None:
                habit.name = name
            if description is not None:
                habit.description = description
            if icon is not None:
                habit.icon = icon
            if color is not None:
                habit.color = color
            if frequency is not None:
                if frequency == "daily":
                    habit.frequency = Frequency.daily()
                elif frequency == "weekly":
                    habit.frequency = Frequency.weekly(times=times_per_week or 1)
            
            # Recompute scores with new frequency
            habit._recompute_scores()
            
            # Emit HABIT_UPDATED event
            changes = {}
            if name is not None:
                changes["name"] = name
            if description is not None:
                changes["description"] = description
            if icon is not None:
                changes["icon"] = icon
            if color is not None:
                changes["color"] = color
            if frequency is not None:
                changes["frequency"] = frequency
            
            try:
                event = HabitUpdated.create(habit_id=habit_id, changes=changes)
                get_event_publisher().publish(event)
            except Exception:
                pass
            
            return Result.success(habit, f"Updated habit: {habit.name}")
        except Exception as e:
            return Result.failure(f"Failed to update habit: {str(e)}")
    
    def delete_habit(self, habit_id: str) -> Result[bool]:
        """
        Delete a habit.
        
        Args:
            habit_id: ID of habit to delete
        
        Returns:
            Result indicating success
        """
        if habit_id not in self.habits:
            return Result.failure(f"Habit not found: {habit_id}")
        
        # Emit HABIT_DELETED event before deletion
        try:
            event = HabitDeleted.create(habit_id=habit_id)
            get_event_publisher().publish(event)
        except Exception:
            pass
        
        del self.habits[habit_id]
        return Result.success(True, "Habit deleted")
    
    def archive_habit(self, habit_id: str) -> Result[Habit]:
        """Archive a habit (soft delete)."""
        habit = self.habits.get(habit_id)
        if not habit:
            return Result.failure(f"Habit not found: {habit_id}")
        
        habit.is_archived = True
        
        # Emit HABIT_ARCHIVED event
        try:
            event = HabitArchived.create(habit_id=habit_id)
            get_event_publisher().publish(event)
        except Exception:
            pass
        
        return Result.success(habit, f"Archived habit: {habit.name}")
    
    # === Completion Operations ===
    
    def mark_completed(
        self,
        habit_id: str,
        entry_date: Optional[date] = None,
        notes: str = ""
    ) -> Result[Entry]:
        """
        Mark a habit as completed for a date.
        
        Args:
            habit_id: ID of the habit
            entry_date: Date to mark (default: today)
            notes: Optional notes
        
        Returns:
            Result with the created entry
        """
        habit = self.habits.get(habit_id)
        if not habit:
            return Result.failure(f"Habit not found: {habit_id}")
        
        entry_date = entry_date or date.today()
        entry = habit.mark_completed(entry_date, notes)
        
        # Award XP for completion
        self.inventory.add_xp(10)
        
        # Emit HABIT_COMPLETED event
        try:
            event = HabitCompleted.create(
                habit_id=habit_id,
                completion_date=entry_date,
                notes=notes,
                xp_earned=10
            )
            get_event_publisher().publish(event)
        except Exception:
            pass
        
        # Check for streak achievements
        streak = habit.streak_count
        if streak == 7:
            self.inventory.streak_freezes.award_freeze("7-day streak")
        elif streak == 30:
            self.inventory.streak_freezes.award_freeze("30-day streak")
        
        return Result.success(entry, f"Marked {habit.name} complete for {entry_date}")
    
    def mark_skipped(
        self,
        habit_id: str,
        entry_date: Optional[date] = None,
        notes: str = ""
    ) -> Result[Entry]:
        """
        Mark a habit as skipped for a date.
        
        Skipped days don't affect the score.
        
        Args:
            habit_id: ID of the habit
            entry_date: Date to mark (default: today)
            notes: Optional notes
        
        Returns:
            Result with the created entry
        """
        habit = self.habits.get(habit_id)
        if not habit:
            return Result.failure(f"Habit not found: {habit_id}")
        
        entry_date = entry_date or date.today()
        entry = habit.mark_skipped(entry_date, notes)
        
        # Emit HABIT_SKIPPED event
        try:
            event = HabitSkipped.create(
                habit_id=habit_id,
                skip_date=entry_date,
                reason=notes
            )
            get_event_publisher().publish(event)
        except Exception:
            pass
        
        return Result.success(entry, f"Skipped {habit.name} for {entry_date}")
    
    def unmark(
        self,
        habit_id: str,
        entry_date: Optional[date] = None
    ) -> Result[bool]:
        """
        Remove a completion mark for a date.
        
        Args:
            habit_id: ID of the habit
            entry_date: Date to unmark (default: today)
        
        Returns:
            Result indicating success
        """
        habit = self.habits.get(habit_id)
        if not habit:
            return Result.failure(f"Habit not found: {habit_id}")
        
        entry_date = entry_date or date.today()
        habit.unmark(entry_date)
        
        # Emit HABIT_UNMARKED event
        try:
            event = HabitUnmarked.create(
                habit_id=habit_id,
                entry_date=entry_date
            )
            get_event_publisher().publish(event)
        except Exception:
            pass
        
        return Result.success(True, f"Unmarked {habit.name} for {entry_date}")
    
    def is_completed_today(self, habit_id: str) -> bool:
        """Check if a habit is completed today."""
        habit = self.habits.get(habit_id)
        if not habit:
            return False
        return habit.entries.get(date.today()).is_completed
    
    # === Score Operations ===
    
    def get_score(self, habit_id: str) -> Optional[HabitScore]:
        """Get the current score for a habit."""
        habit = self.habits.get(habit_id)
        if not habit:
            return None
        return habit.score
    
    def get_score_history(
        self,
        habit_id: str,
        days: int = 30
    ) -> List[HabitScore]:
        """
        Get score history for a habit.
        
        Args:
            habit_id: ID of the habit
            days: Number of days of history
        
        Returns:
            List of scores (newest first)
        """
        habit = self.habits.get(habit_id)
        if not habit:
            return []
        
        to_date = date.today()
        from_date = to_date - timedelta(days=days)
        
        return habit.scores.get_by_interval(from_date, to_date)
    
    def get_all_scores(self) -> Dict[str, HabitScore]:
        """Get current scores for all habits."""
        return {
            habit_id: habit.score
            for habit_id, habit in self.habits.items()
            if not habit.is_archived
        }
    
    # === Streak Operations ===
    
    def get_streak(self, habit_id: str) -> int:
        """Get the current streak for a habit."""
        habit = self.habits.get(habit_id)
        if not habit:
            return 0
        return habit.streak_count
    
    def get_all_streaks(self) -> Dict[str, int]:
        """Get current streaks for all habits."""
        return {
            habit_id: habit.streak_count
            for habit_id, habit in self.habits.items()
            if not habit.is_archived
        }
    
    # === Streak Freeze Operations ===
    
    def get_freeze_count(self) -> int:
        """Get the number of available streak freezes."""
        return self.inventory.streak_freezes.count
    
    def purchase_freeze(self) -> Result[bool]:
        """
        Purchase a streak freeze with XP.
        
        Returns:
            Result indicating success
        """
        success, new_xp = self.inventory.streak_freezes.purchase_freeze(
            self.inventory.total_xp
        )
        
        if success:
            self.inventory.total_xp = new_xp
            
            # Emit STREAK_FREEZE_PURCHASED event
            try:
                event = StreakFreezePurchased.create(
                    xp_cost=100,
                    xp_remaining=new_xp,
                    freezes_count=self.inventory.streak_freezes.count
                )
                get_event_publisher().publish(event)
            except Exception:
                pass
            
            return Result.success(True, "Purchased a Streak Freeze!")
        else:
            return Result.failure("Cannot purchase freeze (not enough XP or at max capacity)")
    
    def use_freeze(
        self,
        habit_id: str,
        freeze_date: date
    ) -> Result[bool]:
        """
        Use a streak freeze for a habit on a specific date.
        
        Args:
            habit_id: ID of the habit
            freeze_date: The date to freeze
        
        Returns:
            Result indicating success
        """
        habit = self.habits.get(habit_id)
        if not habit:
            return Result.failure(f"Habit not found: {habit_id}")
        
        if not self.inventory.streak_freezes.can_preserve_streak(habit_id, freeze_date):
            return Result.failure("Cannot use freeze (none available or already frozen)")
        
        success = self.inventory.streak_freezes.use_freeze(habit_id, freeze_date)
        
        if success:
            # Mark as skipped to preserve streak
            habit.mark_skipped(freeze_date, "Streak Freeze used")
            return Result.success(True, f"Used Streak Freeze for {habit.name}")
        
        return Result.failure("Failed to use Streak Freeze")
    
    # === Analytics ===
    
    def get_habits_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all habits.
        
        Returns:
            Dictionary with summary statistics
        """
        habits = self.get_all_habits()
        
        if not habits:
            return {
                "total_habits": 0,
                "average_score": 0,
                "total_streak": 0,
                "completed_today": 0
            }
        
        scores = [h.score.percentage for h in habits]
        streaks = [h.streak_count for h in habits]
        completed_today = sum(1 for h in habits if self.is_completed_today(h.id))
        
        return {
            "total_habits": len(habits),
            "average_score": sum(scores) / len(scores) if scores else 0,
            "total_streak": sum(streaks),
            "completed_today": completed_today,
            "inventory": {
                "xp": self.inventory.total_xp,
                "level": self.inventory.level,
                "freezes": self.inventory.streak_freezes.count
            }
        }
    
    def get_completion_rate(
        self,
        habit_id: str,
        days: int = 7
    ) -> float:
        """
        Get the completion rate for a habit over a period.
        
        Args:
            habit_id: ID of the habit
            days: Number of days to analyze
        
        Returns:
            Completion rate as a decimal (0.0 to 1.0)
        """
        habit = self.habits.get(habit_id)
        if not habit:
            return 0.0
        
        to_date = date.today()
        from_date = to_date - timedelta(days=days)
        
        completions = habit.entries.count_completions(from_date, to_date)
        return completions / days if days > 0 else 0.0
    
    # === Serialization ===
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "habits": {
                habit_id: habit.to_dict()
                for habit_id, habit in self.habits.items()
            },
            "inventory": self.inventory.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HabitBrain":
        """Create from dictionary."""
        brain = cls()
        
        # Load habits
        habits_data = data.get("habits", {})
        for habit_id, habit_data in habits_data.items():
            habit = Habit.from_dict(habit_data)
            brain.habits[habit_id] = habit
        
        # Load inventory
        inventory_data = data.get("inventory", {})
        brain.inventory = UserInventory.from_dict(inventory_data)
        
        return brain
    
    def save_to_file(self, filepath: str) -> bool:
        """Save to a JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "HabitBrain":
        """Load from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except FileNotFoundError:
            return cls()
        except Exception as e:
            print(f"Error loading: {e}")
            return cls()


# Convenience functions for quick access
def create_habit_brain() -> HabitBrain:
    """Create a new HabitBrain instance."""
    return HabitBrain()


def quick_habit(name: str, frequency: str = "daily") -> tuple[HabitBrain, Habit]:
    """
    Quick create a habit and return brain + habit.
    
    Usage:
        brain, habit = quick_habit("Exercise")
        print(f"Created: {habit.name}")
    """
    brain = HabitBrain()
    result = brain.create_habit(name, frequency=frequency)
    return brain, result.data