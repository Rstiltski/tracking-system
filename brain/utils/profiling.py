"""
Performance Profiling Utilities

Provides performance logging, timing, and profiling capabilities.
Following PROJECT_RULES.md:
- Python-first implementation
- Minimal overhead
- Configurable logging levels
"""
from __future__ import annotations

import time
import threading
import functools
import cProfile
import pstats
import io
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """A single performance metric."""
    name: str
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
            "category": self.category,
            "metadata": self.metadata
        }


class PerformanceLogger:
    """
    Thread-safe performance logger for tracking operation durations.
    
    Features:
    - Track operation durations
    - Identify slow operations
    - Performance statistics
    - Export metrics
    
    Usage:
        perf = PerformanceLogger()
        
        # Context manager
        with perf.measure("database_query"):
            result = db.execute(query)
        
        # Decorator
        @perf.timed("habit_score_calc")
        def calculate_score(habit_id):
            ...
        
        # Get slow operations
        slow = perf.get_slow_operations(threshold_ms=100)
    """
    
    def __init__(
        self,
        max_metrics: int = 10000,
        slow_threshold_ms: float = 100.0
    ):
        """
        Initialize performance logger.
        
        Args:
            max_metrics: Maximum metrics to keep in memory
            slow_threshold_ms: Threshold for slow operation warnings
        """
        self._metrics: List[PerformanceMetric] = []
        self._lock = threading.Lock()
        self.max_metrics = max_metrics
        self.slow_threshold_ms = slow_threshold_ms
        
        # Category aggregations
        self._category_stats: Dict[str, Dict[str, Any]] = {}
    
    def measure(
        self,
        name: str,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for measuring operation duration.
        
        Args:
            name: Operation name
            category: Operation category
            metadata: Additional metadata
            
        Yields:
            None
            
        Example:
            with perf.measure("db_query", category="database"):
                result = db.execute(query)
        """
        return self._MeasureContext(self, name, category, metadata or {})
    
    class _MeasureContext:
        """Context manager for timing operations."""
        
        def __init__(
            self,
            perf_logger: "PerformanceLogger",
            name: str,
            category: str,
            metadata: Dict[str, Any]
        ):
            self.perf_logger = perf_logger
            self.name = name
            self.category = category
            self.metadata = metadata
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.perf_counter()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            end_time = time.perf_counter()
            duration_ms = (end_time - self.start_time) * 1000
            
            self.perf_logger.record(
                self.name,
                duration_ms,
                category=self.category,
                metadata=self.metadata
            )
            
            return False
    
    def record(
        self,
        name: str,
        duration_ms: float,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a performance metric.
        
        Args:
            name: Operation name
            duration_ms: Duration in milliseconds
            category: Operation category
            metadata: Additional metadata
        """
        metric = PerformanceMetric(
            name=name,
            duration_ms=duration_ms,
            category=category,
            metadata=metadata or {}
        )
        
        with self._lock:
            self._metrics.append(metric)
            
            # Update category stats
            if category not in self._category_stats:
                self._category_stats[category] = {
                    "count": 0,
                    "total_ms": 0.0,
                    "min_ms": float('inf'),
                    "max_ms": 0.0,
                    "avg_ms": 0.0
                }
            
            stats = self._category_stats[category]
            stats["count"] += 1
            stats["total_ms"] += duration_ms
            stats["min_ms"] = min(stats["min_ms"], duration_ms)
            stats["max_ms"] = max(stats["max_ms"], duration_ms)
            stats["avg_ms"] = stats["total_ms"] / stats["count"]
            
            # Trim if over max
            if len(self._metrics) > self.max_metrics:
                self._metrics = self._metrics[-self.max_metrics:]
        
        # Log slow operations
        if duration_ms > self.slow_threshold_ms:
            logger.warning(
                f"Slow operation: {name} took {duration_ms:.2f}ms "
                f"(threshold: {self.slow_threshold_ms}ms)"
            )
    
    def timed(
        self,
        name: Optional[str] = None,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Callable:
        """
        Decorator for timing function execution.
        
        Args:
            name: Operation name (uses function name if None)
            category: Operation category
            metadata: Additional metadata
            
        Returns:
            Decorated function
            
        Example:
            @perf.timed(category="database")
            def get_habits():
                return storage.get_habits()
        """
        def decorator(func: Callable) -> Callable:
            operation_name = name or func.__name__
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    self.record(operation_name, duration_ms, category, metadata)
            
            return wrapper
        
        return decorator
    
    def get_slow_operations(
        self,
        threshold_ms: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get operations slower than threshold.
        
        Args:
            threshold_ms: Threshold in ms (uses default if None)
            limit: Maximum results to return
            
        Returns:
            List of slow operation metrics
        """
        threshold = threshold_ms or self.slow_threshold_ms
        
        with self._lock:
            slow = [
                m.to_dict() for m in self._metrics
                if m.duration_ms > threshold
            ]
            return sorted(slow, key=lambda x: x["duration_ms"], reverse=True)[:limit]
    
    def get_stats(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary with stats
        """
        with self._lock:
            if category:
                return self._category_stats.get(category, {})
            
            return {
                "total_metrics": len(self._metrics),
                "max_metrics": self.max_metrics,
                "slow_threshold_ms": self.slow_threshold_ms,
                "categories": dict(self._category_stats)
            }
    
    def get_recent_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent metrics.
        
        Args:
            limit: Maximum results
            
        Returns:
            List of recent metrics
        """
        with self._lock:
            return [m.to_dict() for m in self._metrics[-limit:]]
    
    def clear(self) -> None:
        """Clear all metrics."""
        with self._lock:
            self._metrics.clear()
            self._category_stats.clear()
    
    def export_metrics(self) -> str:
        """
        Export metrics as JSON string.
        
        Returns:
            JSON string of all metrics
        """
        with self._lock:
            return json.dumps({
                "exported_at": datetime.now().isoformat(),
                "stats": self.get_stats(),
                "metrics": [m.to_dict() for m in self._metrics]
            }, indent=2)


# Global performance logger
_perf_logger: Optional[PerformanceLogger] = None


def get_performance_logger() -> PerformanceLogger:
    """Get the global performance logger instance."""
    global _perf_logger
    if _perf_logger is None:
        _perf_logger = PerformanceLogger()
    return _perf_logger


# Convenience functions
def profile(
    name: Optional[str] = None,
    category: str = "general"
) -> Callable:
    """
    Decorator for profiling function execution.
    
    Args:
        name: Operation name
        category: Operation category
        
    Returns:
        Decorated function
    """
    return get_performance_logger().timed(name, category)


@contextmanager
def timed(
    name: str,
    category: str = "general",
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Context manager for timing operations.
    
    Args:
        name: Operation name
        category: Operation category
        metadata: Additional metadata
        
    Yields:
        None
        
    Example:
        with timed("database_query", category="database"):
            result = db.execute(query)
    """
    with get_performance_logger().measure(name, category, metadata):
        yield


class Profiler:
    """
    Detailed profiler using cProfile for in-depth analysis.
    
    Usage:
        profiler = Profiler()
        
        profiler.start()
        # ... code to profile ...
        profiler.stop()
        
        # Print stats
        profiler.print_stats()
        
        # Get top functions by time
        top = profiler.get_top_functions(limit=10)
    """
    
    def __init__(self):
        self._profiler: Optional[cProfile.Profile] = None
        self._stats: Optional[pstats.Stats] = None
    
    def start(self) -> None:
        """Start profiling."""
        self._profiler = cProfile.Profile()
        self._profiler.enable()
    
    def stop(self) -> None:
        """Stop profiling."""
        if self._profiler:
            self._profiler.disable()
            self._stats = pstats.Stats(self._profiler)
    
    def print_stats(self, sort_by: str = "cumulative", limit: int = 20) -> None:
        """
        Print profiling statistics.
        
        Args:
            sort_by: Sort field (cumulative, time, calls)
            limit: Number of functions to show
        """
        if self._stats:
            self._stats.sort_stats(sort_by)
            self._stats.print_stats(limit)
    
    def get_top_functions(
        self,
        sort_by: str = "cumulative",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get top functions by specified metric.
        
        Args:
            sort_by: Sort field
            limit: Number of functions
            
        Returns:
            List of function stats
        """
        if not self._stats:
            return []
        
        # Capture stats output
        output = io.StringIO()
        ps = pstats.Stats(self._profiler, stream=output)
        ps.sort_stats(sort_by)
        ps.print_stats(limit)
        
        return [{"raw": output.getvalue()}]


# Export
__all__ = [
    "PerformanceLogger",
    "PerformanceMetric",
    "get_performance_logger",
    "profile",
    "timed",
    "Profiler",
]