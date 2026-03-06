"""
Lazy Loading Utilities - Performance Optimization

Provides lazy loading patterns for large datasets.
Following PROJECT_RULES.md:
- Python-first implementation
- Memory-efficient iteration
- Works with Storage class
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Generic, Iterator, List, Optional, TypeVar
from functools import wraps
from dataclasses import dataclass
from datetime import date
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class LazyLoader(Generic[T]):
    """
    Lazy loader for datasets that should be loaded on demand.
    
    Delays loading until the data is actually needed, reducing
    memory usage and initial load time.
    
    Usage:
        # Create a lazy loader
        lazy_habits = LazyLoader(lambda: storage.get_habits())
        
        # Data is not loaded yet
        print("Created lazy loader")
        
        # Access triggers loading
        habits = lazy_habits.get()  # Now loads
        habits = lazy_habits.get()  # Uses cached value
        
        # Force reload
        lazy_habits.reload()
    """
    
    def __init__(
        self,
        loader: Callable[[], T],
        auto_reload: bool = False,
        ttl_seconds: Optional[float] = None
    ):
        """
        Initialize lazy loader.
        
        Args:
            loader: Function that loads the data
            auto_reload: Reload on each access
            ttl_seconds: Time-to-live for cached data
        """
        self._loader = loader
        self._auto_reload = auto_reload
        self._ttl_seconds = ttl_seconds
        self._data: Optional[T] = None
        self._loaded = False
        self._loaded_at: Optional[float] = None
    
    def get(self) -> T:
        """Get the data, loading if necessary."""
        import time
        
        # Check if reload needed
        needs_load = (
            not self._loaded or
            self._auto_reload or
            (self._ttl_seconds is not None and self._loaded_at is not None and
             time.time() - self._loaded_at > self._ttl_seconds)
        )
        
        if needs_load:
            self._data = self._loader()
            self._loaded = True
            self._loaded_at = time.time()
        
        return self._data
    
    def reload(self) -> T:
        """Force reload the data."""
        self._loaded = False
        return self.get()
    
    def is_loaded(self) -> bool:
        """Check if data has been loaded."""
        return self._loaded
    
    def clear(self) -> None:
        """Clear cached data."""
        self._data = None
        self._loaded = False
        self._loaded_at = None
    
    def __bool__(self) -> bool:
        """Check if data exists (triggers loading)."""
        data = self.get()
        return bool(data)
    
    def __repr__(self) -> str:
        status = "loaded" if self._loaded else "not loaded"
        return f"LazyLoader({status})"


class LazyIterator(Generic[T]):
    """
    Lazy iterator for processing large datasets in chunks.
    
    Loads data in chunks and yields items one at a time,
    reducing memory usage for large datasets.
    
    Usage:
        # Create lazy iterator
        iterator = LazyIterator(
            chunk_loader=lambda offset, limit: storage.get_habit_entries(
                habit_id="abc",
                start_date=date(2024, 1, offset//limit + 1)
            ),
            chunk_size=100
        )
        
        # Process items one at a time
        for entry in iterator:
            process_entry(entry)
    """
    
    def __init__(
        self,
        chunk_loader: Callable[[int, int], List[T]],
        chunk_size: int = 100,
        max_items: Optional[int] = None
    ):
        """
        Initialize lazy iterator.
        
        Args:
            chunk_loader: Function that loads a chunk (offset, limit) -> items
            chunk_size: Number of items per chunk
            max_items: Maximum total items to yield
        """
        self._chunk_loader = chunk_loader
        self._chunk_size = chunk_size
        self._max_items = max_items
        
        self._current_chunk: List[T] = []
        self._chunk_index = 0
        self._total_yielded = 0
        self._exhausted = False
    
    def __iter__(self) -> Iterator[T]:
        return self
    
    def __next__(self) -> T:
        # Check max items
        if self._max_items is not None and self._total_yielded >= self._max_items:
            raise StopIteration
        
        # Load next chunk if needed
        while not self._current_chunk and not self._exhausted:
            self._load_next_chunk()
        
        if not self._current_chunk:
            raise StopIteration
        
        item = self._current_chunk.pop(0)
        self._total_yielded += 1
        return item
    
    def _load_next_chunk(self) -> None:
        """Load the next chunk of data."""
        offset = self._chunk_index * self._chunk_size
        
        # Calculate limit
        limit = self._chunk_size
        if self._max_items is not None:
            remaining = self._max_items - self._total_yielded
            limit = min(limit, remaining)
        
        if limit <= 0:
            self._exhausted = True
            return
        
        chunk = self._chunk_loader(offset, limit)
        
        if not chunk:
            self._exhausted = True
        else:
            self._current_chunk = chunk
            self._chunk_index += 1
            
            # Check if this was the last chunk
            if len(chunk) < self._chunk_size:
                self._exhausted = True
    
    def reset(self) -> None:
        """Reset the iterator."""
        self._current_chunk = []
        self._chunk_index = 0
        self._total_yielded = 0
        self._exhausted = False


@dataclass
class LazyPage(Generic[T]):
    """A lazily loaded page of data."""
    items: LazyLoader[List[T]]
    page_number: int
    total_pages: LazyLoader[int]
    
    def get_items(self) -> List[T]:
        """Get page items."""
        return self.items.get()
    
    def get_total_pages(self) -> int:
        """Get total page count."""
        return self.total_pages.get()


class LazyHabitEntries:
    """
    Lazy loader specifically for habit entries.
    
    Optimized for the common pattern of loading habit entries
    with date filtering and pagination.
    
    Usage:
        from tracking_app.storage import get_storage
        
        storage = get_storage()
        lazy_entries = LazyHabitEntries(storage, "habit_123")
        
        # Get all entries (loaded on demand)
        all_entries = lazy_entries.all()
        
        # Iterate (memory efficient)
        for entry in lazy_entries.iterate(chunk_size=50):
            process(entry)
        
        # Get entries for specific month
        march_entries = lazy_entries.for_month(2024, 3)
    """
    
    def __init__(
        self,
        storage,
        habit_id: str,
        default_chunk_size: int = 100
    ):
        """
        Initialize lazy habit entries loader.
        
        Args:
            storage: Storage instance
            habit_id: Habit ID
            default_chunk_size: Default chunk size for iteration
        """
        self._storage = storage
        self._habit_id = habit_id
        self._default_chunk_size = default_chunk_size
        
        # Lazy cache
        self._all_entries: Optional[LazyLoader] = None
    
    def all(self) -> List:
        """Get all entries (lazy loaded)."""
        if self._all_entries is None:
            self._all_entries = LazyLoader(
                lambda: self._storage.get_habit_entries(self._habit_id)
            )
        return self._all_entries.get()
    
    def for_date_range(self, start: date, end: date) -> List:
        """Get entries for a date range."""
        return LazyLoader(
            lambda: self._storage.get_habit_entries(
                self._habit_id,
                start_date=start,
                end_date=end
            )
        ).get()
    
    def for_month(self, year: int, month: int) -> List:
        """Get entries for a specific month."""
        from calendar import monthrange
        
        start = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        end = date(year, month, last_day)
        
        return self.for_date_range(start, end)
    
    def iterate(self, chunk_size: Optional[int] = None) -> Iterator:
        """
        Iterate over entries in chunks.
        
        Args:
            chunk_size: Items per chunk
            
        Yields:
            Entry objects
        """
        size = chunk_size or self._default_chunk_size
        
        # For habit entries, we iterate by date
        entries = self.all()
        for entry in entries:
            yield entry


class LazyTaskList:
    """
    Lazy loader for task lists with filtering.
    
    Usage:
        lazy_tasks = LazyTaskList(storage)
        
        # Get pending tasks
        pending = lazy_tasks.pending()
        
        # Get by due date
        today_tasks = lazy_tasks.due_today()
    """
    
    def __init__(self, storage, default_chunk_size: int = 50):
        self._storage = storage
        self._default_chunk_size = default_chunk_size
        self._pending: Optional[LazyLoader] = None
        self._all: Optional[LazyLoader] = None
    
    def all(self) -> List:
        """Get all tasks."""
        if self._all is None:
            self._all = LazyLoader(
                lambda: self._storage.get_tasks(include_completed=True)
            )
        return self._all.get()
    
    def pending(self) -> List:
        """Get pending tasks."""
        if self._pending is None:
            self._pending = LazyLoader(
                lambda: self._storage.get_tasks(include_completed=False)
            )
        return self._pending.get()
    
    def due_today(self) -> List:
        """Get tasks due today."""
        from datetime import date
        today = date.today()
        
        all_pending = self.pending()
        return [
            t for t in all_pending
            if t.due_date and t.due_date.date() == today
        ]
    
    def overdue(self) -> List:
        """Get overdue tasks."""
        from datetime import date
        today = date.today()
        
        all_pending = self.pending()
        return [
            t for t in all_pending
            if t.due_date and t.due_date.date() < today
        ]
    
    def by_priority(self, priority: str) -> List:
        """Get tasks by priority."""
        all_pending = self.pending()
        return [t for t in all_pending if t.priority == priority]
    
    def reload(self) -> None:
        """Clear caches and reload on next access."""
        self._pending = None
        self._all = None


class LazyGoalHistory:
    """
    Lazy loader for goal progress history.
    
    Usage:
        lazy_goals = LazyGoalHistory(storage)
        
        # Get all goals
        goals = lazy_goals.all()
        
        # Get in progress
        in_progress = lazy_goals.in_progress()
    """
    
    def __init__(self, storage):
        self._storage = storage
        self._all: Optional[LazyLoader] = None
        self._in_progress: Optional[LazyLoader] = None
    
    def all(self) -> List:
        """Get all goals."""
        if self._all is None:
            self._all = LazyLoader(
                lambda: self._storage.get_goals(include_completed=True)
            )
        return self._all.get()
    
    def in_progress(self) -> List:
        """Get goals in progress."""
        if self._in_progress is None:
            self._in_progress = LazyLoader(
                lambda: self._storage.get_goals(include_completed=False)
            )
        return self._in_progress.get()
    
    def completed(self) -> List:
        """Get completed goals."""
        all_goals = self.all()
        return [g for g in all_goals if g.completed]
    
    def near_completion(self, threshold: float = 0.8) -> List:
        """Get goals near completion."""
        in_progress = self.in_progress()
        return [
            g for g in in_progress
            if g.target > 0 and g.current / g.target >= threshold
        ]
    
    def reload(self) -> None:
        """Clear caches."""
        self._all = None
        self._in_progress = None


# Convenience decorators
def lazy_property(loader: Callable[[], T]) -> property:
    """
    Create a lazy property that loads on first access.
    
    Usage:
        class MyClass:
            @lazy_property
            def expensive_data(self):
                return load_expensive_data()
    """
    attr_name = f"_lazy_{loader.__name__}"
    
    @wraps(loader)
    def getter(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, LazyLoader(lambda: loader(self)))
        return getattr(self, attr_name).get()
    
    return property(getter)


# Export
__all__ = [
    "LazyLoader",
    "LazyIterator",
    "LazyPage",
    "LazyHabitEntries",
    "LazyTaskList",
    "LazyGoalHistory",
    "lazy_property",
]