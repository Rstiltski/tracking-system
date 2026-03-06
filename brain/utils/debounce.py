"""
Debouncing Utilities - UI Performance Optimization

Provides debouncing and throttling for UI updates and events.
Following PROJECT_RULES.md:
- Python-first implementation
- Works with Streamlit
- Reduces unnecessary re-renders
"""
from __future__ import annotations

import time
import threading
from functools import wraps
from typing import Any, Callable, Optional, Dict, TypeVar
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Debouncer:
    """
    Debouncer for reducing rapid function calls.
    
    Debouncing ensures a function is only called after a specified
    delay has passed since the last call. Useful for:
    - Search input
    - Auto-save
    - Window resize handlers
    
    Usage:
        debouncer = Debouncer(delay_ms=300)
        
        # Debounce a function call
        debouncer.call(my_function, arg1, arg2)
        
        # Or use as decorator
        @debounce(delay_ms=300)
        def on_search(query):
            perform_search(query)
    """
    
    def __init__(self, delay_ms: int = 300):
        """
        Initialize debouncer.
        
        Args:
            delay_ms: Delay in milliseconds before executing
        """
        self.delay_ms = delay_ms
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        self._pending_args: tuple = ()
        self._pending_kwargs: dict = {}
        self._pending_func: Optional[Callable] = None
    
    def call(self, func: Callable, *args, **kwargs) -> None:
        """
        Debounce a function call.
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
        """
        with self._lock:
            # Cancel existing timer
            if self._timer is not None:
                self._timer.cancel()
            
            # Store pending call
            self._pending_func = func
            self._pending_args = args
            self._pending_kwargs = kwargs
            
            # Create new timer
            self._timer = threading.Timer(
                self.delay_ms / 1000.0,
                self._execute
            )
            self._timer.start()
    
    def _execute(self) -> None:
        """Execute the pending function call."""
        with self._lock:
            if self._pending_func is not None:
                try:
                    self._pending_func(*self._pending_args, **self._pending_kwargs)
                except Exception as e:
                    logger.error(f"Debounced function error: {e}")
                
                self._pending_func = None
                self._pending_args = ()
                self._pending_kwargs = {}
    
    def cancel(self) -> None:
        """Cancel any pending execution."""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
    
    def flush(self) -> None:
        """Immediately execute any pending call."""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            
            if self._pending_func is not None:
                try:
                    self._pending_func(*self._pending_args, **self._pending_kwargs)
                except Exception as e:
                    logger.error(f"Debounced function error on flush: {e}")
                
                self._pending_func = None
    
    def __call__(self, func: Callable) -> Callable:
        """
        Use as decorator.
        
        Args:
            func: Function to debounce
            
        Returns:
            Debounced function
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.call(func, *args, **kwargs)
        
        wrapper.cancel = self.cancel
        wrapper.flush = self.flush
        
        return wrapper


class Throttler:
    """
    Throttler for limiting function call frequency.
    
    Throttling ensures a function is called at most once in a
    specified time period. Useful for:
    - Scroll handlers
    - Resize handlers
    - Continuous input
    
    Usage:
        throttler = Throttler(interval_ms=100)
        
        # Throttle a function call
        throttler.call(my_function, arg1, arg2)
        
        # Or use as decorator
        @throttle(interval_ms=100)
        def on_scroll(position):
            update_position(position)
    """
    
    def __init__(self, interval_ms: int = 100):
        """
        Initialize throttler.
        
        Args:
            interval_ms: Minimum interval between calls in milliseconds
        """
        self.interval_ms = interval_ms
        self._last_call: float = 0
        self._lock = threading.Lock()
        self._pending_timer: Optional[threading.Timer] = None
        self._pending_args: tuple = ()
        self._pending_kwargs: dict = {}
        self._pending_func: Optional[Callable] = None
    
    def call(self, func: Callable, *args, **kwargs) -> None:
        """
        Throttle a function call.
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
        """
        with self._lock:
            now = time.time() * 1000  # Convert to ms
            time_since_last = now - self._last_call
            
            if time_since_last >= self.interval_ms:
                # Execute immediately
                self._last_call = now
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Throttled function error: {e}")
            else:
                # Schedule for later
                self._pending_func = func
                self._pending_args = args
                self._pending_kwargs = kwargs
                
                if self._pending_timer is not None:
                    self._pending_timer.cancel()
                
                remaining = self.interval_ms - time_since_last
                self._pending_timer = threading.Timer(
                    remaining / 1000.0,
                    self._execute_pending
                )
                self._pending_timer.start()
    
    def _execute_pending(self) -> None:
        """Execute the pending function call."""
        with self._lock:
            if self._pending_func is not None:
                self._last_call = time.time() * 1000
                try:
                    self._pending_func(*self._pending_args, **self._pending_kwargs)
                except Exception as e:
                    logger.error(f"Throttled function error: {e}")
                
                self._pending_func = None
    
    def __call__(self, func: Callable) -> Callable:
        """Use as decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.call(func, *args, **kwargs)
        
        return wrapper


# Global instances for convenience
_debouncers: Dict[str, Debouncer] = {}
_throttlers: Dict[str, Throttler] = {}


def debounce(delay_ms: int = 300, key: Optional[str] = None) -> Callable:
    """
    Decorator for debouncing function calls.
    
    Args:
        delay_ms: Delay in milliseconds
        key: Optional key for shared debouncer
        
    Returns:
        Decorated function
        
    Example:
        @debounce(delay_ms=300)
        def search(query):
            return perform_search(query)
    """
    def decorator(func: Callable) -> Callable:
        debouncer_key = key or f"{func.__module__}.{func.__name__}"
        
        if debouncer_key not in _debouncers:
            _debouncers[debouncer_key] = Debouncer(delay_ms)
        
        debouncer = _debouncers[debouncer_key]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            debouncer.call(func, *args, **kwargs)
        
        wrapper.cancel = debouncer.cancel
        wrapper.flush = debouncer.flush
        
        return wrapper
    
    return decorator


def throttle(interval_ms: int = 100, key: Optional[str] = None) -> Callable:
    """
    Decorator for throttling function calls.
    
    Args:
        interval_ms: Minimum interval between calls in milliseconds
        key: Optional key for shared throttler
        
    Returns:
        Decorated function
        
    Example:
        @throttle(interval_ms=100)
        def on_scroll(position):
            update_scroll_position(position)
    """
    def decorator(func: Callable) -> Callable:
        throttler_key = key or f"{func.__module__}.{func.__name__}"
        
        if throttler_key not in _throttlers:
            _throttlers[throttler_key] = Throttler(interval_ms)
        
        throttler = _throttlers[throttler_key]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            throttler.call(func, *args, **kwargs)
        
        return wrapper
    
    return decorator


class RateLimiter:
    """
    Rate limiter for API-like rate limiting.
    
    Limits the number of calls in a time window.
    
    Usage:
        limiter = RateLimiter(max_calls=10, window_seconds=60)
        
        if limiter.can_call():
            result = api_call()
            limiter.record_call()
        else:
            wait_time = limiter.wait_time()
    """
    
    def __init__(self, max_calls: int = 10, window_seconds: float = 60.0):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum calls allowed in window
            window_seconds: Time window in seconds
        """
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._call_times: list = []
        self._lock = threading.Lock()
    
    def can_call(self) -> bool:
        """Check if a call can be made."""
        with self._lock:
            self._cleanup()
            return len(self._call_times) < self.max_calls
    
    def record_call(self) -> None:
        """Record a call was made."""
        with self._lock:
            self._cleanup()
            self._call_times.append(time.time())
    
    def wait_time(self) -> float:
        """Get time to wait before next call is allowed."""
        with self._lock:
            self._cleanup()
            if len(self._call_times) < self.max_calls:
                return 0.0
            
            # Wait until oldest call expires
            oldest = self._call_times[0]
            return max(0.0, self.window_seconds - (time.time() - oldest))
    
    def _cleanup(self) -> None:
        """Remove expired call times."""
        cutoff = time.time() - self.window_seconds
        self._call_times = [t for t in self._call_times if t > cutoff]


# Streamlit-specific helpers
def st_debounce(key: str, delay_ms: int = 300) -> Debouncer:
    """
    Get or create a Streamlit-specific debouncer.
    
    Args:
        key: Unique key for the debouncer
        delay_ms: Delay in milliseconds
        
    Returns:
        Debouncer instance
    """
    full_key = f"st_debounce_{key}"
    if full_key not in _debouncers:
        _debouncers[full_key] = Debouncer(delay_ms)
    return _debouncers[full_key]


# Export
__all__ = [
    "Debouncer",
    "Throttler",
    "RateLimiter",
    "debounce",
    "throttle",
    "st_debounce",
]