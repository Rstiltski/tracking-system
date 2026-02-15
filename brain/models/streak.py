"""
Streak Model - Streak tracking with freeze support.

Implements the Streak Freeze mechanic from Phase 1.2:
- Preserves streak on a missed day
- Can be earned through consistent tracking or purchased with XP
- Prevents user churn from broken streaks

Based on research:
- "What-the-hell" effect causes users to abandon habits after breaking streaks
- Streak Freeze provides a "safety net" that reduces anxiety
- Variable rewards (earning freezes) increase engagement
"""
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Dict, Optional
import json


@dataclass
class Streak:
    """
    A streak of consecutive completions.
    
    Attributes:
        start_date: When the streak started
        end_date: When the streak ended (or today if ongoing)
        is_frozen: Whether this streak was preserved by a freeze
    """
    start_date: date
    end_date: date
    is_frozen: bool = False
    
    @property
    def length(self) -> int:
        """Get the length of the streak in days."""
        return (self.end_date - self.start_date).days + 1
    
    def contains(self, check_date: date) -> bool:
        """Check if a date falls within this streak."""
        return self.start_date <= check_date <= self.end_date
    
    def compare_longer(self, other: "Streak") -> int:
        """Compare streaks by length (for sorting)."""
        return self.length - other.length
    
    def compare_newer(self, other: "Streak") -> int:
        """Compare streaks by end date (for sorting)."""
        if self.end_date > other.end_date:
            return 1
        elif self.end_date < other.end_date:
            return -1
        return 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "is_frozen": self.is_frozen
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Streak":
        """Create from dictionary."""
        return cls(
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]),
            is_frozen=data.get("is_frozen", False)
        )


@dataclass
class StreakList:
    """
    A list of streaks for a habit.
    
    Handles computing and storing streak history.
    Based on Loop's StreakList.kt implementation.
    
    Attributes:
        streaks: List of streaks
    """
    streaks: List[Streak] = field(default_factory=list)
    
    def get_best(self, limit: int = 5) -> List[Streak]:
        """
        Get the best streaks sorted by length.
        
        Args:
            limit: Maximum number of streaks to return
        
        Returns:
            List of best streaks sorted by length (descending)
        """
        sorted_streaks = sorted(self.streaks, key=lambda s: s.length, reverse=True)
        return sorted_streaks[:limit]
    
    def get_current(self) -> Optional[Streak]:
        """
        Get the current ongoing streak (if any).
        
        A streak is current if it ends today or yesterday.
        """
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        for streak in self.streaks:
            if streak.end_date >= yesterday:
                return streak
        return None
    
    @property
    def current_length(self) -> int:
        """Get the current streak length."""
        current = self.get_current()
        return current.length if current else 0
    
    @property
    def longest_length(self) -> int:
        """Get the longest streak length."""
        if not self.streaks:
            return 0
        return max(s.length for s in self.streaks)
    
    def recompute(
        self,
        completed_dates: List[date],
        from_date: date,
        to_date: date
    ) -> None:
        """
        Recompute all streaks based on completed dates.
        
        Args:
            completed_dates: List of dates where habit was completed
            from_date: Start date for computation
            to_date: End date for computation
        """
        self.streaks.clear()
        
        if not completed_dates:
            return
        
        # Sort dates
        sorted_dates = sorted(completed_dates)
        
        # Filter to interval
        sorted_dates = [d for d in sorted_dates if from_date <= d <= to_date]
        
        if not sorted_dates:
            return
        
        # Build streaks from consecutive dates
        streak_start = sorted_dates[0]
        streak_end = sorted_dates[0]
        
        for i in range(1, len(sorted_dates)):
            current = sorted_dates[i]
            
            # Check if this date continues the streak
            if current == streak_end + timedelta(days=1):
                streak_end = current
            else:
                # Streak broken, save it and start new one
                self.streaks.append(Streak(start_date=streak_start, end_date=streak_end))
                streak_start = current
                streak_end = current
        
        # Don't forget the last streak
        self.streaks.append(Streak(start_date=streak_start, end_date=streak_end))


@dataclass
class StreakFreeze:
    """
    Streak Freeze inventory and management.
    
    A Streak Freeze is an item that:
    - Preserves streak on a missed day
    - Is consumed automatically when needed
    - Can be earned through consistent tracking or purchased with XP
    
    Attributes:
        count: Current number of freezes available
        max_freezes: Maximum freezes allowed
        xp_cost: XP cost to purchase a freeze
        history: History of freeze usage
    """
    count: int = 0
    max_freezes: int = 10
    xp_cost: int = 100
    earn_threshold: int = 7  # Days of consistency to earn one
    history: List[Dict] = field(default_factory=list)
    
    @property
    def is_available(self) -> bool:
        """Check if a streak freeze is available."""
        return self.count > 0
    
    @property
    def is_maxed(self) -> bool:
        """Check if at maximum freeze capacity."""
        return self.count >= self.max_freezes
    
    def use_freeze(self, habit_id: str, freeze_date: date) -> bool:
        """
        Use a streak freeze for a habit.
        
        Args:
            habit_id: ID of the habit to freeze
            freeze_date: The date to freeze
        
        Returns:
            True if freeze was used, False if none available
        """
        if not self.is_available:
            return False
        
        self.count -= 1
        self.history.append({
            "habit_id": habit_id,
            "date": freeze_date.isoformat(),
            "used_at": date.today().isoformat(),
            "action": "used"
        })
        return True
    
    def purchase_freeze(self, current_xp: int) -> tuple[bool, int]:
        """
        Purchase a streak freeze with XP.
        
        Args:
            current_xp: User's current XP
        
        Returns:
            Tuple of (success, new_xp)
        """
        if current_xp < self.xp_cost:
            return False, current_xp
        
        if self.is_maxed:
            return False, current_xp
        
        new_xp = current_xp - self.xp_cost
        self.count += 1
        self.history.append({
            "action": "purchased",
            "xp_cost": self.xp_cost,
            "date": date.today().isoformat()
        })
        return True, new_xp
    
    def award_freeze(self, reason: str = "consistency") -> bool:
        """
        Award a free streak freeze.
        
        Args:
            reason: Why the freeze was awarded
        
        Returns:
            True if awarded, False if at max capacity
        """
        if self.is_maxed:
            return False
        
        self.count += 1
        self.history.append({
            "action": "awarded",
            "reason": reason,
            "date": date.today().isoformat()
        })
        return True
    
    def get_usage_count(self, habit_id: Optional[str] = None) -> int:
        """
        Get the number of freezes used.
        
        Args:
            habit_id: Optional habit ID to filter by
        
        Returns:
            Number of freezes used
        """
        count = 0
        for entry in self.history:
            if entry.get("action") == "used":
                if habit_id is None or entry.get("habit_id") == habit_id:
                    count += 1
        return count
    
    def can_preserve_streak(self, habit_id: str, missed_date: date) -> bool:
        """
        Check if a streak can be preserved for a missed date.
        
        Args:
            habit_id: ID of the habit
            missed_date: The date that was missed
        
        Returns:
            True if the streak can be preserved
        """
        # Check if we have a freeze available
        if not self.is_available:
            return False
        
        # Check if this date was already frozen
        for entry in self.history:
            if (entry.get("action") == "used" and 
                entry.get("habit_id") == habit_id and
                entry.get("date") == missed_date.isoformat()):
                return False  # Already frozen
        
        return True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "count": self.count,
            "max_freezes": self.max_freezes,
            "xp_cost": self.xp_cost,
            "earn_threshold": self.earn_threshold,
            "history": self.history
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "StreakFreeze":
        """Create from dictionary."""
        return cls(
            count=data.get("count", 0),
            max_freezes=data.get("max_freezes", 10),
            xp_cost=data.get("xp_cost", 100),
            earn_threshold=data.get("earn_threshold", 7),
            history=data.get("history", [])
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"❄️ {self.count}/{self.max_freezes} Streak Freezes"


# User inventory dataclass for storing all user items
@dataclass
class UserInventory:
    """
    User's inventory containing streak freezes and other items.
    
    Attributes:
        streak_freezes: Streak freeze inventory
        total_xp: Total XP earned
        level: Current user level
    """
    streak_freezes: StreakFreeze = field(default_factory=StreakFreeze)
    total_xp: int = 0
    level: int = 1
    
    def add_xp(self, amount: int) -> int:
        """
        Add XP and check for level up.
        
        Returns:
            New total XP
        """
        self.total_xp += amount
        
        # Simple level calculation: level up every 100 XP
        new_level = (self.total_xp // 100) + 1
        if new_level > self.level:
            self.level = new_level
        
        return self.total_xp
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "streak_freezes": self.streak_freezes.to_dict(),
            "total_xp": self.total_xp,
            "level": self.level
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "UserInventory":
        """Create from dictionary."""
        freezes_data = data.get("streak_freezes", {})
        return cls(
            streak_freezes=StreakFreeze.from_dict(freezes_data),
            total_xp=data.get("total_xp", 0),
            level=data.get("level", 1)
        )