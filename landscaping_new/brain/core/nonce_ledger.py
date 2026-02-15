"""
Nonce Ledger for Brain System

Implements a nonce ledger for preventing replay attacks in the brain system.
"""
from __future__ import annotations
import hashlib
import time
from typing import Dict, Set, Optional
from datetime import datetime, timedelta

class NonceLedger:
    """
    A ledger to track nonces and prevent replay attacks.
    
    Nonces are unique tokens that can only be used once within a certain timeframe.
    This prevents malicious actors from replaying the same command multiple times.
    """
    
    def __init__(self, retention_period: int = 3600):
        """
        Initialize the nonce ledger.
        
        Args:
            retention_period: How long to retain nonces in seconds (default 1 hour)
        """
        self.retention_period = retention_period
        self.nonces: Dict[str, datetime] = {}  # nonce -> timestamp
        self.used_nonces: Set[str] = set()  # Track nonces that have been used
    
    def generate_nonce(self, data: str = "") -> str:
        """
        Generate a unique nonce based on current time and optional data.
        
        Args:
            data: Optional data to include in nonce generation
            
        Returns:
            A unique nonce string
        """
        timestamp = str(time.time())
        combined = f"{timestamp}_{data}_{hashlib.sha256(data.encode()).hexdigest()[:8]}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def is_nonce_valid(self, nonce: str) -> bool:
        """
        Check if a nonce is valid (hasn't been used and isn't expired).
        
        Args:
            nonce: The nonce to validate
            
        Returns:
            True if nonce is valid, False otherwise
        """
        # Check if nonce was already used
        if nonce in self.used_nonces:
            return False
        
        # Check if nonce exists and hasn't expired
        if nonce in self.nonces:
            timestamp = self.nonces[nonce]
            expiration_time = timestamp + timedelta(seconds=self.retention_period)
            if datetime.now() > expiration_time:
                # Nonce has expired, remove it
                del self.nonces[nonce]
                return False
            return True
        
        # Nonce doesn't exist
        return False
    
    def record_nonce(self, nonce: str) -> bool:
        """
        Record a nonce as used.
        
        Args:
            nonce: The nonce to record
            
        Returns:
            True if nonce was recorded, False if it was already used
        """
        if self.is_nonce_valid(nonce):
            self.used_nonces.add(nonce)
            self.nonces[nonce] = datetime.now()
            return True
        return False
    
    def cleanup_expired_nonces(self) -> int:
        """
        Remove expired nonces from the ledger.
        
        Returns:
            Number of nonces removed
        """
        current_time = datetime.now()
        expired_nonces = []
        
        for nonce, timestamp in self.nonces.items():
            if current_time > timestamp + timedelta(seconds=self.retention_period):
                expired_nonces.append(nonce)
        
        for nonce in expired_nonces:
            del self.nonces[nonce]
            if nonce in self.used_nonces:
                self.used_nonces.remove(nonce)
        
        return len(expired_nonces)
    
    def get_nonce_count(self) -> int:
        """Get the number of nonces in the ledger."""
        return len(self.nonces)
    
    def clear_ledger(self) -> None:
        """Clear all nonces from the ledger."""
        self.nonces.clear()
        self.used_nonces.clear()