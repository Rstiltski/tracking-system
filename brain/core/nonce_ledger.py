"""
Nonce Ledger for Replay Attack Prevention

This module provides nonce tracking to prevent replay attacks in the secure channel.
It uses a fast in-memory store (Redis) for runtime checks with SQL fallback and audit logging.

Architecture:
- Primary: Redis with SETNX + EXPIRE for O(1) nonce checking (300s TTL)
- Fallback: SQLite for development/single-node deployments
- Audit: Async logging of accepted nonces to SQL for forensics

Usage:
    from brain.core.nonce_ledger import NonceLedger, get_nonce_ledger
    
    ledger = get_nonce_ledger()
    
    # Check if nonce was seen before
    if ledger.check_nonce("ops-brain-2024-01", "abc123..."):
        raise ReplayAttackError("Nonce reuse detected")
    
    # Record nonce as used
    ledger.record_nonce("ops-brain-2024-01", "abc123...", ttl=300)

Part of: Secure Channel Cryptographic Messaging (Phase 1 PoC)
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import os
import time
import logging
import sqlite3
from typing import Optional
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
DEFAULT_NONCE_TTL = 300
REDIS_KEY_PREFIX = 'nonce:'

class NonceLedger:
    """
    Nonce tracking service for replay protection.
    
    This service provides fast nonce checking with multiple backend options:
    1. Redis (preferred) - O(1) checks with automatic expiration
    2. SQLite (fallback) - Works everywhere, but slower for high-volume
    
    Features:
    - SETNX pattern for atomic check-and-set
    - Automatic TTL expiration in Redis
    - SQL audit trail for forensics
    - Graceful fallback if Redis unavailable
    """

    def __init__(self, redis_client: Optional['redis.Redis']=None, db_connection: Optional[sqlite3.Connection]=None, use_redis: bool=True, audit_to_sql: bool=True):
        """
        Initialize the nonce ledger.
        
        Args:
            redis_client: Redis client instance (optional)
            db_connection: SQLite connection for fallback and audit
            use_redis: Whether to use Redis if available
            audit_to_sql: Whether to log nonces to SQL for audit trail
        """
        self.redis_client = redis_client if use_redis and REDIS_AVAILABLE else None
        self.db_connection = db_connection
        self.audit_to_sql = audit_to_sql
        self._memory_nonces = {}
        if self.redis_client:
            logger.info('NonceLedger initialized with Redis backend')
        elif db_connection:
            logger.info('NonceLedger initialized with SQLite backend')
        else:
            logger.info('NonceLedger initialized with in-memory fallback')
            if not REDIS_AVAILABLE and use_redis:
                logger.warning("Redis requested but not available - install 'redis' package")
        if db_connection:
            self._init_sql_tables()

    def _init_sql_tables(self):
        """Create nonce ledger tables in SQLite"""
        cursor = self.db_connection.cursor()
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS brain_nonce_ledger (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                sender_kid TEXT NOT NULL,\n                nonce TEXT NOT NULL,\n                first_seen_at TIMESTAMP NOT NULL,\n                expires_at TIMESTAMP NOT NULL,\n                UNIQUE(sender_kid, nonce)\n            )\n        ')
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS brain_nonce_audit_log (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                sender_kid TEXT NOT NULL,\n                nonce TEXT NOT NULL,\n                accepted_at TIMESTAMP NOT NULL,\n                ttl_seconds INTEGER NOT NULL,\n                metadata TEXT\n            )\n        ')
        cursor.execute('\n            CREATE INDEX IF NOT EXISTS idx_brain_nonce_expires \n            ON brain_nonce_ledger(expires_at)\n        ')
        cursor.execute('\n            CREATE INDEX IF NOT EXISTS idx_brain_nonce_audit_sender \n            ON brain_nonce_audit_log(sender_kid, accepted_at)\n        ')
        self.db_connection.commit()
        logger.debug('Brain nonce ledger SQL tables initialized')

    def check_nonce(self, sender_kid: str, nonce: str) -> bool:
        """
        Check if a nonce has been seen before.
        
        Args:
            sender_kid: Sender's key ID
            nonce: Nonce value (base64-encoded)
            
        Returns:
            True if nonce was seen before (replay attack)
            False if nonce is new (message is legitimate)
        """
        if self.redis_client:
            return self._check_nonce_redis(sender_kid, nonce)
        elif self.db_connection:
            return self._check_nonce_sql(sender_kid, nonce)
        else:
            return self._check_nonce_memory(sender_kid, nonce)

    def _check_nonce_redis(self, sender_kid: str, nonce: str) -> bool:
        """Check nonce in Redis"""
        key = f'{REDIS_KEY_PREFIX}{sender_kid}:{nonce}'
        try:
            exists = self.redis_client.exists(key)
            return bool(exists)
        except Exception as e:
            logger.error(f'Redis nonce check failed: {e}')
            if self.db_connection:
                return self._check_nonce_sql(sender_kid, nonce)
            return False

    def _check_nonce_sql(self, sender_kid: str, nonce: str) -> bool:
        """Check nonce in SQLite"""
        cursor = self.db_connection.cursor()
        try:
            self._cleanup_expired_nonces()
            from datetime import datetime, timezone
            cursor.execute('\n                SELECT COUNT(*) FROM brain_nonce_ledger\n                WHERE sender_kid = ? AND nonce = ? AND expires_at > ?\n            ', (sender_kid, nonce, datetime.now(timezone.utc).isoformat()))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            logger.error(f'SQL nonce check failed: {e}')
            return False

    def record_nonce(self, sender_kid: str, nonce: str, ttl: int=DEFAULT_NONCE_TTL, metadata: Optional[dict]=None):
        """
        Record a nonce as used.
        
        This should be called AFTER successful envelope verification.
        
        Args:
            sender_kid: Sender's key ID
            nonce: Nonce value (base64-encoded)
            ttl: Time-to-live in seconds (default: 300)
        """
        if self.redis_client:
            self._record_nonce_redis(sender_kid, nonce, ttl)
        elif self.db_connection:
            self._record_nonce_sql(sender_kid, nonce, ttl)
        else:
            self._record_nonce_memory(sender_kid, nonce, ttl)
        if self.audit_to_sql and self.db_connection:
            self._audit_nonce_sql(sender_kid, nonce, ttl, metadata)

    def _record_nonce_redis(self, sender_kid: str, nonce: str, ttl: int):
        """Record nonce in Redis with SETNX + EXPIRE"""
        key = f'{REDIS_KEY_PREFIX}{sender_kid}:{nonce}'
        try:
            self.redis_client.setex(key, ttl, '1')
            logger.debug(f'Recorded nonce in Redis: {sender_kid} (TTL: {ttl}s)')
        except Exception as e:
            logger.error(f'Redis nonce recording failed: {e}')
            if self.db_connection:
                self._record_nonce_sql(sender_kid, nonce, ttl)

    def _record_nonce_sql(self, sender_kid: str, nonce: str, ttl: int):
        """Record nonce in SQLite"""
        cursor = self.db_connection.cursor()
        try:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(seconds=ttl)
            cursor.execute('\n                INSERT OR IGNORE INTO brain_nonce_ledger (sender_kid, nonce, first_seen_at, expires_at)\n                VALUES (?, ?, ?, ?)\n            ', (sender_kid, nonce, now.isoformat(), expires_at.isoformat()))
            self.db_connection.commit()
            logger.debug(f'Recorded nonce in SQL: {sender_kid}')
        except Exception as e:
            logger.error(f'SQL nonce recording failed: {e}')

    def _audit_nonce_sql(self, sender_kid: str, nonce: str, ttl: int, metadata: Optional[dict]=None):
        """Log nonce acceptance to audit trail"""
        cursor = self.db_connection.cursor()
        try:
            import json
            from datetime import datetime, timezone
            metadata_json = json.dumps(metadata) if metadata else None
            cursor.execute('\n                INSERT INTO brain_nonce_audit_log (sender_kid, nonce, accepted_at, ttl_seconds, metadata)\n                VALUES (?, ?, ?, ?, ?)\n            ', (sender_kid, nonce, datetime.now(timezone.utc).isoformat(), ttl, metadata_json))
            self.db_connection.commit()
            logger.debug(f'Audited nonce: {sender_kid}')
        except Exception as e:
            logger.error(f'Nonce audit logging failed: {e}')

    def _cleanup_expired_nonces(self):
        """Remove expired nonces from SQL (maintenance)"""
        cursor = self.db_connection.cursor()
        try:
            from datetime import datetime, timezone
            cursor.execute('\n                DELETE FROM brain_nonce_ledger WHERE expires_at < ?\n            ', (datetime.now(timezone.utc).isoformat(),))
            deleted = cursor.rowcount
            if deleted > 0:
                self.db_connection.commit()
                logger.debug(f'Cleaned up {deleted} expired nonces')
        except Exception as e:
            logger.error(f'Nonce cleanup failed: {e}')

    def _check_nonce_memory(self, sender_kid: str, nonce: str) -> bool:
        """Check nonce in in-memory dictionary"""
        self._cleanup_memory_nonces()
        key = f'{sender_kid}:{nonce}'
        return key in self._memory_nonces

    def _record_nonce_memory(self, sender_kid: str, nonce: str, ttl: int):
        """Record nonce in in-memory dictionary"""
        key = f'{sender_kid}:{nonce}'
        expires_at = time.time() + ttl
        self._memory_nonces[key] = expires_at
        logger.debug(f'Recorded nonce in memory: {sender_kid}')

    def _cleanup_memory_nonces(self):
        """Remove expired nonces from memory"""
        now = time.time()
        expired_keys = [k for k, exp in self._memory_nonces.items() if exp < now]
        for key in expired_keys:
            del self._memory_nonces[key]
        if expired_keys:
            logger.debug(f'Cleaned up {len(expired_keys)} expired nonces from memory')

    def get_nonce_stats(self) -> dict:
        """Get statistics about nonce usage (for monitoring)"""
        stats = {'backend': 'redis' if self.redis_client else 'sqlite', 'redis_available': REDIS_AVAILABLE}
        if self.db_connection:
            cursor = self.db_connection.cursor()
            from datetime import datetime, timezone
            cursor.execute('\n                SELECT COUNT(*) FROM brain_nonce_ledger WHERE expires_at > ?\n            ', (datetime.now(timezone.utc).isoformat(),))
            stats['active_nonces_sql'] = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM brain_nonce_audit_log')
            stats['total_audited'] = cursor.fetchone()[0]
        return stats
_global_nonce_ledger: Optional[NonceLedger] = None

def get_nonce_ledger(redis_url: Optional[str]=None, db_connection: Optional[sqlite3.Connection]=None) -> NonceLedger:
    """
    Get or create the global nonce ledger instance.
    
    Args:
        redis_url: Redis connection URL (e.g., "redis://localhost:6379/0")
        db_connection: SQLite connection for fallback
        
    Returns:
        NonceLedger instance
    """
    global _global_nonce_ledger
    if _global_nonce_ledger is None:
        redis_client = None
        if redis_url and REDIS_AVAILABLE:
            try:
                redis_client = redis.from_url(redis_url)
                redis_client.ping()
                logger.info(f'Connected to Redis: {redis_url}')
            except Exception as e:
                logger.warning(f'Failed to connect to Redis: {e}')
                redis_client = None
        _global_nonce_ledger = NonceLedger(redis_client=redis_client, db_connection=db_connection, use_redis=True, audit_to_sql=True)
    return _global_nonce_ledger

def reset_nonce_ledger():
    """Reset the global nonce ledger (for testing)"""
    global _global_nonce_ledger
    _global_nonce_ledger = None
