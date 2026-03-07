"""
Timing Decorators - Performance Monitoring for Storage Layer

Provides timing decorators that automatically record performance metrics
for storage operations. Integrates with the performance monitoring system.

Usage:
    from tracking_app.utils.timing_decorators import timed_operation
    
    @timed_operation
    def get_habits():
        # Storage operation
        return storage.get_habits()
"""

import time
import functools
import logging
from typing import Any, Callable, Optional, TypeVar, Union
from brain.utils.performance_monitor import get_performance_monitor

logger = logging.getLogger(__name__)

# Type variable for decorator
F = TypeVar('F', bound=Callable[..., Any])


def timed_operation(
    operation_name: Optional[str] = None,
    category: str = "storage",
    threshold_ms: float = 10.0
) -> Callable[[F], F]:
    """
    Decorator to time operations and record performance metrics.
    
    Args:
        operation_name: Custom name for the operation (auto-generated if None)
        category: Category for the operation (e.g., "storage", "database", "brain")
        threshold_ms: Log warning if operation takes longer than this threshold
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate operation name
            op_name = operation_name or f"{category}.{func.__name__}"
            
            # Start timing
            start_time = time.perf_counter()
            start_memory = _get_memory_usage()
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Calculate duration
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                # Record performance metric
                monitor = get_performance_monitor()
                monitor.record_operation(op_name, duration_ms)
                
                # Log slow operations
                if duration_ms > threshold_ms:
                    logger.warning(
                        f"Slow operation detected: {op_name} took {duration_ms:.2f}ms "
                        f"(threshold: {threshold_ms}ms)"
                    )
                
                return result
                
            except Exception as e:
                # Calculate duration even on error
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                # Record the failed operation
                monitor = get_performance_monitor()
                monitor.record_operation(f"{op_name}_error", duration_ms)
                
                logger.error(f"Operation {op_name} failed after {duration_ms:.2f}ms: {e}")
                raise
                
        return wrapper  # type: ignore
    return decorator


def timed_context(operation_name: str, category: str = "storage") -> "TimingContext":
    """
    Context manager for timing operations.
    
    Args:
        operation_name: Name of the operation
        category: Category for the operation
        
    Returns:
        TimingContext instance
    """
    return TimingContext(operation_name, category)


class TimingContext:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str, category: str = "storage"):
        self.operation_name = f"{category}.{operation_name}"
        self.start_time = 0.0
        self.start_memory = 0.0
        
    def __enter__(self) -> "TimingContext":
        self.start_time = time.perf_counter()
        self.start_memory = _get_memory_usage()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        end_time = time.perf_counter()
        duration_ms = (end_time - self.start_time) * 1000
        
        # Record performance metric
        monitor = get_performance_monitor()
        op_name = self.operation_name
        if exc_type is not None:
            op_name = f"{op_name}_error"
        
        monitor.record_operation(op_name, duration_ms)
        
        if exc_type is None:
            logger.debug(f"Operation {self.operation_name} completed in {duration_ms:.2f}ms")
        else:
            logger.error(f"Operation {self.operation_name} failed after {duration_ms:.2f}ms")


def batch_timing(
    operation_name: str = "batch_operation",
    category: str = "storage"
) -> Callable[[F], F]:
    """
    Decorator for timing batch operations that process multiple items.
    
    Args:
        operation_name: Name of the batch operation
        category: Category for the operation
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                
                # Calculate duration
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                # Record performance metric
                monitor = get_performance_monitor()
                monitor.record_operation(operation_name, duration_ms)
                
                # Log performance info
                if hasattr(result, '__len__'):
                    count = len(result)
                    avg_time_per_item = duration_ms / count if count > 0 else 0
                    logger.info(
                        f"Batch operation {operation_name} processed {count} items "
                        f"in {duration_ms:.2f}ms ({avg_time_per_item:.2f}ms per item)"
                    )
                
                return result
                
            except Exception as e:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                monitor = get_performance_monitor()
                monitor.record_operation(f"{operation_name}_error", duration_ms)
                
                logger.error(f"Batch operation {operation_name} failed after {duration_ms:.2f}ms: {e}")
                raise
                
        return wrapper  # type: ignore
    return decorator


def memory_monitor(operation_name: str, category: str = "storage") -> Callable[[F], F]:
    """
    Decorator to monitor memory usage of operations.
    
    Args:
        operation_name: Name of the operation
        category: Category for the operation
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            op_name = f"{category}.{operation_name}"
            
            # Get memory before
            memory_before = _get_memory_usage()
            
            try:
                result = func(*args, **kwargs)
                
                # Get memory after
                memory_after = _get_memory_usage()
                memory_delta = memory_after - memory_before
                
                # Record performance metric with memory info
                monitor = get_performance_monitor()
                # Note: This would need enhancement to the monitor to track memory delta
                
                # Log memory usage
                if memory_delta > 10:  # Log if memory usage increased by more than 10MB
                    logger.warning(
                        f"Operation {op_name} used {memory_delta:.2f}MB of memory "
                        f"(before: {memory_before:.2f}MB, after: {memory_after:.2f}MB)"
                    )
                
                return result
                
            except Exception as e:
                memory_after = _get_memory_usage()
                logger.error(f"Operation {op_name} failed. Memory before: {memory_before:.2f}MB, after: {memory_after:.2f}MB")
                raise
                
        return wrapper  # type: ignore
    return decorator


def _get_memory_usage() -> float:
    """
    Get current memory usage in MB.
    
    Returns:
        Memory usage in MB
    """
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        return memory_info.rss / 1024 / 1024  # Convert to MB
    except ImportError:
        return 0.0
    except Exception:
        return 0.0


# Convenience decorators for common operations
def timed_storage_operation(operation_name: Optional[str] = None) -> Callable[[F], F]:
    """Decorator for storage operations."""
    return timed_operation(operation_name, category="storage", threshold_ms=50.0)


def timed_database_operation(operation_name: Optional[str] = None) -> Callable[[F], F]:
    """Decorator for database operations."""
    return timed_operation(operation_name, category="database", threshold_ms=100.0)


def timed_brain_operation(operation_name: Optional[str] = None) -> Callable[[F], F]:
    """Decorator for Brain system operations."""
    return timed_operation(operation_name, category="brain", threshold_ms=200.0)


def timed_ui_operation(operation_name: Optional[str] = None) -> Callable[[F], F]:
    """Decorator for UI operations."""
    return timed_operation(operation_name, category="ui", threshold_ms=100.0)


# Export
__all__ = [
    'timed_operation',
    'timed_context',
    'batch_timing',
    'memory_monitor',
    'timed_storage_operation',
    'timed_database_operation',
    'timed_brain_operation',
    'timed_ui_operation',
    'TimingContext'
]