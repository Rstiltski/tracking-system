"""
Entry Model - Habit completion records.

Based on Loop Habit Tracker's Entry system:
- Tracks completion status for each day
- Supports different entry types (YES_MANUAL, YES_AUTO, SKIP, NO)
- Provides entry list for score computation

The EntryList class handles the gap-filling logic needed for
proper score calculation when days are missed.
"""
from enum import IntEnum
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Dict, Optional, Iterator
from collections import defaultdict


class EntryType(IntEnum):
    """
    Types of habit entries.
    
    Based on Loop's entry types:
    - YES_MANUAL: User explicitly marked as done
    - YES_AUTO: Automatically marked (e.g., by skip day)
    - SKIP: Explicitly skipped (doesn't affect score)
    - NO: Not done (explicit failure)
    - UNKNOWN: No data for this day
    """
    NO = 0
    YES_MANUAL = 1
    YES_AUTO = 2
    SKIP = 3
    UNKNOWN = 4


@dataclass
class Entry:
    """
    A single habit entry for a specific date.
    
    Attributes:
        date: The date of this entry
        value: The entry type/value
        habit_id: ID of the habit this entry belongs to
        notes: Optional notes for this entry
    """
    date: date
    value: EntryType = EntryType.UNKNOWN
    habit_id: str = ""
    notes: str = ""
    
    @property
    def is_completed(self) -> bool:
        """Check if this entry represents a completion."""
        return self.value in (EntryType.YES_MANUAL, EntryType.YES_AUTO)
    
    @property
    def is_skip(self) -> bool:
        """Check if this entry is a skip (doesn't affect score)."""
        return self.value == EntryType.SKIP
    
    @property
    def is_failure(self) -> bool:
        """Check if this entry is an explicit failure."""
        return self.value == EntryType.NO
    
    @property
    def numeric_value(self) -> float:
        """
        Get numeric value for score calculation.
        
        Returns:
            1.0 for completed, 0.0 for failure/unknown, skip doesn't count
        """
        if self.is_completed:
            return 1.0
        elif self.is_skip:
            # Skip entries don't affect the score
            return -1  # Special marker
        return 0.0
    
    def __str__(self) -> str:
        """String representation."""
        status = {
            EntryType.YES_MANUAL: "✓",
            EntryType.YES_AUTO: "✓ (auto)",
            EntryType.SKIP: "−",
            EntryType.NO: "✗",
            EntryType.UNKNOWN: "?"
        }.get(self.value, "?")
        return f"{self.date}: {status}"


@dataclass
class EntryList:
    """
    A collection of entries for a habit.
    
    Handles:
    - Storing entries by date
    - Gap filling for missing days
    - Providing entries in order for score calculation
    
    Attributes:
        entries: Dictionary mapping date to Entry
        habit_id: ID of the habit this list belongs to
    """
    entries: Dict[date, Entry] = field(default_factory=dict)
    habit_id: str = ""
    
    def add(self, entry: Entry) -> None:
        """Add or update an entry."""
        self.entries[entry.date] = entry
    
    def get(self, entry_date: date) -> Entry:
        """
        Get entry for a date, creating UNKNOWN if not exists.
        
        Args:
            entry_date: The date to get entry for
        
        Returns:
            Entry for the date (UNKNOWN if not found)
        """
        if entry_date in self.entries:
            return self.entries[entry_date]
        return Entry(date=entry_date, value=EntryType.UNKNOWN, habit_id=self.habit_id)
    
    def get_by_interval(self, from_date: date, to_date: date) -> List[Entry]:
        """
        Get all entries in a date interval, filling gaps with UNKNOWN.
        
        This is crucial for proper score calculation - we need to
        iterate through ALL days in the interval, not just days with
        entries, because missing days should count as failures.
        
        Args:
            from_date: Start date (inclusive)
            to_date: End date (inclusive)
        
        Returns:
            List of entries ordered by date (newest first)
        """
        result = []
        current = to_date
        
        while current >= from_date:
            result.append(self.get(current))
            current -= timedelta(days=1)
        
        return result
    
    def get_values_by_interval(self, from_date: date, to_date: date) -> List[float]:
        """
        Get numeric values for score calculation.
        
        Returns values in order from oldest to newest (for iterative
        score computation).
        
        Args:
            from_date: Start date (inclusive)
            to_date: End date (inclusive)
        
        Returns:
            List of numeric values (1.0, 0.0, or -1 for skip)
        """
        entries = self.get_by_interval(from_date, to_date)
        # Reverse to get oldest first
        entries.reverse()
        return [e.numeric_value for e in entries]
    
    def mark_completed(self, entry_date: date, notes: str = "") -> Entry:
        """
        Mark a date as completed.
        
        Args:
            entry_date: Date to mark
            notes: Optional notes
        
        Returns:
            The created/updated entry
        """
        entry = Entry(
            date=entry_date,
            value=EntryType.YES_MANUAL,
            habit_id=self.habit_id,
            notes=notes
        )
        self.add(entry)
        return entry
    
    def mark_skipped(self, entry_date: date, notes: str = "") -> Entry:
        """
        Mark a date as skipped (doesn't affect score).
        
        Args:
            entry_date: Date to mark
            notes: Optional notes
        
        Returns:
            The created/updated entry
        """
        entry = Entry(
            date=entry_date,
            value=EntryType.SKIP,
            habit_id=self.habit_id,
            notes=notes
        )
        self.add(entry)
        return entry
    
    def mark_failed(self, entry_date: date, notes: str = "") -> Entry:
        """
        Mark a date as explicitly failed.
        
        Args:
            entry_date: Date to mark
            notes: Optional notes
        
        Returns:
            The created/updated entry
        """
        entry = Entry(
            date=entry_date,
            value=EntryType.NO,
            habit_id=self.habit_id,
            notes=notes
        )
        self.add(entry)
        return entry
    
    def clear(self, entry_date: date) -> None:
        """Remove an entry (set back to UNKNOWN)."""
        if entry_date in self.entries:
            del self.entries[entry_date]
    
    @property
    def oldest_date(self) -> Optional[date]:
        """Get the oldest entry date."""
        if not self.entries:
            return None
        return min(self.entries.keys())
    
    @property
    def newest_date(self) -> Optional[date]:
        """Get the newest entry date."""
        if not self.entries:
            return None
        return max(self.entries.keys())
    
    def count_completions(self, from_date: Optional[date] = None, to_date: Optional[date] = None) -> int:
        """
        Count completions in a date range.
        
        Args:
            from_date: Start date (optional, uses oldest if not provided)
            to_date: End date (optional, uses today if not provided)
        
        Returns:
            Number of completed entries
        """
        if not self.entries:
            return 0
        
        start = from_date or self.oldest_date
        end = to_date or date.today()
        
        if start is None:
            return 0
        
        count = 0
        for entry_date, entry in self.entries.items():
            if start <= entry_date <= end and entry.is_completed:
                count += 1
        
        return count
    
    def __len__(self) -> int:
        """Number of entries (excluding UNKNOWN)."""
        return len(self.entries)
    
    def __iter__(self) -> Iterator[Entry]:
        """Iterate over entries sorted by date (newest first)."""
        for entry_date in sorted(self.entries.keys(), reverse=True):
            yield self.entries[entry_date]