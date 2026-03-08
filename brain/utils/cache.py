"""
Cache Manager - High-Performance Caching System

Provides a comprehensive caching system with TTL support, thread safety,
and automatic cleanup. Designed for the tracking system's performance optimization.

Usage:
    from brain.utils.cache import CacheManager, ConnectionPool
    
    # Initialize cache
    cache = CacheManager(default_ttl=300)
    
    # Store data
    cache.set("user_123_profile", user_data, ttl=600)
    
    # Retrieve data
    user_data = cache.get("user_123_profile")
    
    # Get cache statistics
    stats = cache.get_stats()
"""

import time
import threading
from typing import Any, Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a single cache entry."""
    value: Any
    expiry_time: float
    created_at: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)


class CacheManager:
    """
    Thread-safe cache manager with TTL support and automatic cleanup.
    
    Features:
    - TTL-based expiration
    - Thread-safe operations
    - Automatic cleanup of expired entries
    - Cache statistics and monitoring
    - LRU eviction when memory limits are reached
    """
    
    def __init__(
        self,
        default_ttl: int = 300,
        max_size: int = 10000,
        cleanup_interval: int = 60,
        enable_stats: bool = True
    ):
        """
        Initialize cache manager.
        
        Args:
            default_ttl: Default TTL in seconds
            max_size: Maximum number of cache entries
            cleanup_interval: Cleanup interval in seconds
            enable_stats: Enable hit/miss statistics
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.cleanup_interval = cleanup_interval
        self.enable_stats = enable_stats
        
        # Thread-safe storage
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0
        }
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
        logger.info(f"CacheManager initialized with TTL={default_ttl}s, max_size={max_size}")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in cache with optional TTL.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time to live in seconds (uses default if None)
        """
        ttl = ttl or self.default_ttl
        expiry_time = time.time() + ttl
        
        with self.lock:
            # Check if we need to evict entries
            if len(self.cache) >= self.max_size:
                self._evict_lru_entries(1)
            
            # Store the entry
            entry = CacheEntry(
                value=value,
                expiry_time=expiry_time,
                created_at=datetime.now()
            )
            
            self.cache[key] = entry
            
            if self.enable_stats:
                self.stats['sets'] += 1
        
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache if it exists and hasn't expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        with self.lock:
            entry = self.cache.get(key)
            
            if entry is None:
                if self.enable_stats:
                    self.stats['misses'] += 1
                return None
            
            # Check if expired
            current_time = time.time()
            if current_time > entry.expiry_time:
                del self.cache[key]
                if self.enable_stats:
                    self.stats['misses'] += 1
                logger.debug(f"Cache miss (expired): {key}")
                return None
            
            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            
            if self.enable_stats:
                self.stats['hits'] += 1
            
            logger.debug(f"Cache hit: {key}")
            return entry.value
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False if not found
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                if self.enable_stats:
                    self.stats['deletes'] += 1
                logger.debug(f"Cache delete: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            if self.enable_stats:
                self.stats['deletes'] += count
            logger.info(f"Cache cleared: {count} entries removed")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            total_entries = len(self.cache)
            expired_entries = sum(1 for entry in self.cache.values() 
                                if time.time() > entry.expiry_time)
            active_entries = total_entries - expired_entries
            
            # Calculate hit rate
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            # Get most accessed entries
            most_accessed = sorted(
                self.cache.items(),
                key=lambda x: x[1].access_count,
                reverse=True
            )[:10]
            
            return {
                'cache_size': total_entries,
                'active_entries': active_entries,
                'expired_entries': expired_entries,
                'max_size': self.max_size,
                'hit_rate_percent': round(hit_rate, 2),
                'total_hits': self.stats['hits'],
                'total_misses': self.stats['misses'],
                'total_sets': self.stats['sets'],
                'total_deletes': self.stats['deletes'],
                'total_evictions': self.stats['evictions'],
                'memory_usage_mb': self._calculate_memory_usage(),
                'most_accessed': [
                    {
                        'key': key,
                        'access_count': entry.access_count,
                        'created_at': entry.created_at.isoformat(),
                        'last_accessed': entry.last_accessed.isoformat()
                    }
                    for key, entry in most_accessed
                ]
            }
    
    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            Entry information or None if not found
        """
        with self.lock:
            entry = self.cache.get(key)
            if entry is None:
                return None
            
            current_time = time.time()
            time_remaining = max(0, entry.expiry_time - current_time)
            
            return {
                'key': key,
                'access_count': entry.access_count,
                'created_at': entry.created_at.isoformat(),
                'last_accessed': entry.last_accessed.isoformat(),
                'time_remaining_seconds': round(time_remaining, 2),
                'is_expired': current_time > entry.expiry_time
            }
    
    def clear_expired(self) -> int:
        """
        Manually clear all expired entries.
        
        Returns:
            Number of entries cleared
        """
        current_time = time.time()
        expired_keys = []
        
        with self.lock:
            for key, entry in self.cache.items():
                if current_time > entry.expiry_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
            
            if self.enable_stats:
                self.stats['deletes'] += len(expired_keys)
            
            logger.info(f"Manual cleanup: {len(expired_keys)} expired entries cleared")
            return len(expired_keys)
    
    def _evict_lru_entries(self, count: int) -> None:
        """Evict least recently used entries."""
        if count <= 0:
            return
        
        # Sort by last accessed time
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        evicted_count = 0
        for key, _ in sorted_entries[:count]:
            del self.cache[key]
            evicted_count += 1
        
        if self.enable_stats:
            self.stats['evictions'] += evicted_count
        
        logger.debug(f"LRU eviction: {evicted_count} entries evicted")
    
    def _cleanup_expired(self) -> None:
        """Remove expired cache entries."""
        current_time = time.time()
        expired_keys = []
        
        with self.lock:
            for key, entry in self.cache.items():
                if current_time > entry.expiry_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Auto cleanup: {len(expired_keys)} expired entries removed")
    
    def _calculate_memory_usage(self) -> float:
        """
        Calculate approximate memory usage of cached data.
        
        Returns:
            Memory usage in MB
        """
        try:
            import sys
            total_size = sum(sys.getsizeof(entry.value) for entry in self.cache.values())
            return round(total_size / 1024 / 1024, 2)  # Convert to MB
        except Exception:
            return 0.0
    
    def _start_cleanup_thread(self) -> None:
        """Start background thread for cache cleanup."""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(self.cleanup_interval)
                    self._cleanup_expired()
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.debug("Cache cleanup thread started")


class ConnectionPool:
    """
    Database connection pool implementation.
    
    Features:
    - Connection reuse
    - Thread-safe access
    - Connection timeout handling
    - Automatic connection management
    """
    
    def __init__(
        self,
        db_path: str,
        max_connections: int = 10,
        timeout: int = 30,
        retry_attempts: int = 3
    ):
        """
        Initialize connection pool.
        
        Args:
            db_path: Database file path
            max_connections: Maximum number of connections
            timeout: Connection timeout in seconds
            retry_attempts: Number of retry attempts for failed connections
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        
        self.connections = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.closed = False
        
        logger.info(f"ConnectionPool initialized for {db_path} (max: {max_connections})")
    
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Returns:
            Database connection
            
        Raises:
            TimeoutError: If no connection is available within timeout
            RuntimeError: If pool is closed
        """
        if self.closed:
            raise RuntimeError("Connection pool is closed")
        
        with self.condition:
            # Wait for available connection
            start_time = time.time()
            while len(self.connections) == 0 and not self.closed:
                remaining_time = self.timeout - (time.time() - start_time)
                if remaining_time <= 0:
                    raise TimeoutError("No database connections available")
                
                self.condition.wait(remaining_time)
                
                if len(self.connections) == 0 and not self.closed:
                    # Try to create a new connection if pool isn't full
                    if len(self.connections) < self.max_connections:
                        break
            
            if self.closed:
                raise RuntimeError("Connection pool is closed")
            
            if self.connections:
                return self.connections.pop()
            else:
                # Create new connection
                return self._create_connection()
    
    def return_connection(self, conn) -> None:
        """
        Return a connection to the pool.
        
        Args:
            conn: Database connection to return
        """
        with self.condition:
            if not self.closed and len(self.connections) < self.max_connections:
                self.connections.append(conn)
                self.condition.notify()
            else:
                # Close connection if pool is full or closed
                try:
                    conn.close()
                except Exception:
                    pass
    
    def close_all(self) -> None:
        """Close all connections in the pool."""
        with self.lock:
            self.closed = True
            
            # Close all existing connections
            for conn in self.connections:
                try:
                    conn.close()
                except Exception:
                    pass
            
            self.connections.clear()
            self.condition.notify_all()
            
            logger.info("All connections closed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        with self.lock:
            return {
                'db_path': self.db_path,
                'max_connections': self.max_connections,
                'active_connections': len(self.connections),
                'pool_closed': self.closed
            }
    
    def _create_connection(self):
        """Create a new database connection."""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            return conn
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise


# Global cache instance
_global_cache: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Get the global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache


# Export
__all__ = [
    'CacheManager',
    'ConnectionPool',
    'get_cache',
    'CacheEntry',
    'cached'
]


def cached(ttl: int = 300, key_prefix: str = ''):
    """
    Decorator to cache function results using CacheManager.
    
    Args:
        ttl: Time to live in seconds (default: 300)
        key_prefix: Optional prefix for cache keys
    
    Usage:
        @cached(ttl=600)
        def expensive_function(arg1, arg2):
            # ... expensive computation
            return result
    
        @cached()
        def another_function(arg):
            return compute(arg)
    """
    def decorator(func):
        import functools
        import hashlib
        import json
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__name__}"
            
            if args or kwargs:
                # Create a hash of the arguments
                key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
                key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
                cache_key = f"{cache_key}:{key_hash}"
            
            # Try to get from cache
            cache = get_cache()
            cached_value = cache.get(cache_key)
            
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # Compute and cache the result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            logger.debug(f"Cache miss for {cache_key}, computed and cached")
            
            return result
        
        return wrapper
    return decorator