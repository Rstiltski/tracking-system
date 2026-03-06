"""
Caching Utilities - Performance Optimization

Provides in-memory caching with TTL support for frequently accessed data.
Following PROJECT_RULES.md:
- Python-first implementation
- Thread-safe operations
- Configurable TTL and max size
"""
from __future__ import annotations

import threading
import time
import hashlib
import json
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, Generic
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheEntry(Generic[T]):
    """A single cache entry with TTL support."""
    
    def __init__(self, value: T, ttl_seconds: Optional[float] = None):
        """
        Initialize cache entry.
        
        Args:
            value: The cached value
            ttl_seconds: Time-to-live in seconds (None = no expiry)
        """
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl_seconds is None:
            return False
        return time.time() - self.created_at > self.ttl_seconds
    
    def access(self) -> T:
        """Access the cached value and update stats."""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value


class Cache:
    """
    Thread-safe in-memory cache with TTL support.
    
    Features:
    - Configurable TTL (time-to-live)
    - Maximum size with LRU eviction
    - Thread-safe operations
    - Cache statistics tracking
    
    Usage:
        cache = Cache(max_size=1000, default_ttl=300)
        
        # Set value
        cache.set("user:123", {"name": "John"}, ttl=60)
        
        # Get value
        user = cache.get("user:123")
        
        # Use decorator
        @cached(ttl=120)
        def get_habits():
            return storage.get_habits()
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: Optional[float] = 300.0
    ):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds (5 minutes default)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        # Statistics
        self._hits = 0
        self._misses = 0
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from function arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._misses += 1
                return default
            
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return default
            
            self._hits += 1
            return entry.access()
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None
    ) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds (uses default if None)
        """
        with self._lock:
            # Evict if at max size
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()
            
            entry_ttl = ttl if ttl is not None else self.default_ttl
            self._cache[key] = CacheEntry(value, entry_ttl)
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if not self._cache:
            return
        
        # Find entry with oldest last_accessed time
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )
        del self._cache[lru_key]
        logger.debug(f"Evicted LRU cache entry: {lru_key}")
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            expired_keys = [
                k for k, v in self._cache.items()
                if v.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 2),
                "default_ttl": self.default_ttl
            }
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (prefix match)
            
        Returns:
            Number of entries invalidated
        """
        with self._lock:
            keys_to_delete = [
                k for k in self._cache.keys()
                if k.startswith(pattern)
            ]
            for key in keys_to_delete:
                del self._cache[key]
            
            return len(keys_to_delete)


# Global cache instance
_cache: Optional[Cache] = None


def get_cache() -> Cache:
    """Get the global cache instance."""
    global _cache
    if _cache is None:
        _cache = Cache()
    return _cache


def cached(
    ttl: Optional[float] = None,
    key_prefix: str = "",
    cache: Optional[Cache] = None
) -> Callable:
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache keys
        cache: Cache instance (uses global if None)
        
    Returns:
        Decorated function
        
    Example:
        @cached(ttl=60, key_prefix="habits")
        def get_habits():
            return storage.get_habits()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use provided cache or global
            cache_instance = cache or get_cache()
            
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{cache_instance._generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = cache_instance.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result, ttl=ttl)
            
            logger.debug(f"Cache miss for {func.__name__}")
            return result
        
        # Add cache control methods
        wrapper.cache_clear = lambda: (cache or get_cache()).invalidate_pattern(f"{key_prefix}:{func.__name__}")
        
        return wrapper
    
    return decorator


class CachedProperty:
    """
    Cached property descriptor with TTL.
    
    Example:
        class MyClass:
            @CachedProperty(ttl=60)
            def expensive_computation(self):
                return compute_something()
    """
    
    def __init__(self, ttl: Optional[float] = None):
        self.ttl = ttl
        self.attr_name = None
    
    def __set_name__(self, owner, name):
        self.attr_name = f"_cached_{name}"
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        cache = get_cache()
        cache_key = f"{instance.__class__.__name__}_{id(instance)}_{self.attr_name}"
        
        result = cache.get(cache_key)
        if result is not None:
            return result
        
        # Compute and cache
        func = getattr(instance, self.attr_name.lstrip('_cached_'))
        result = func()
        cache.set(cache_key, result, ttl=self.ttl)
        
        return result


# Export
__all__ = [
    "Cache",
    "CacheEntry",
    "get_cache",
    "cached",
    "CachedProperty",
]