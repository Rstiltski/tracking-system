"""
Brain Utilities Package

Provides caching, profiling, pagination, lazy loading, and performance utilities for the tracking system.
"""

from brain.utils.cache import CacheManager, cached, get_cache
from brain.utils.profiling import (
    PerformanceLogger,
    profile,
    timed,
    get_performance_logger
)
from brain.utils.pagination import (
    Page,
    Paginator,
    CursorPage,
    CursorPaginator,
    paginate_query
)
from brain.utils.debounce import (
    Debouncer,
    Throttler,
    RateLimiter,
    debounce,
    throttle,
    st_debounce
)
from brain.utils.lazy import (
    LazyLoader,
    LazyIterator,
    LazyPage,
    LazyHabitEntries,
    LazyTaskList,
    LazyGoalHistory,
    lazy_property
)

__all__ = [
    # Caching
    "CacheManager",
    "cached",
    "get_cache",
    # Profiling
    "PerformanceLogger",
    "profile",
    "timed",
    "get_performance_logger",
    # Pagination
    "Page",
    "Paginator",
    "CursorPage",
    "CursorPaginator",
    "paginate_query",
    # Debouncing
    "Debouncer",
    "Throttler",
    "RateLimiter",
    "debounce",
    "throttle",
    "st_debounce",
    # Lazy Loading
    "LazyLoader",
    "LazyIterator",
    "LazyPage",
    "LazyHabitEntries",
    "LazyTaskList",
    "LazyGoalHistory",
    "lazy_property",
]
