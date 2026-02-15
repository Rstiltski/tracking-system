"""
Guardrails Middleware - Prevents Infinite Loops and Spam
Part of Sentient System Phase 2.5: Sanity Checks
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import time
import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)

@dataclass
class CommandSignature:
    signature_hash: str
    timestamp: float
    count: int

class SafetyMiddleware:
    """
    Middleware that tracks command frequency to prevent:
    1. Infinite UI Loops (e.g. Calendar refresh bug)
    2. Spam/Rage clicking
    3. Accidental double-submissions
    """
    
    # Settings
    DUPLICATE_WINDOW = 1.0  # Seconds. Commands identical to the last one within this window are blocked.
    RAPID_FIRE_LIMIT = 5    # Max commands per second (even if different)
    
    def __init__(self):
        # Stores the last command info per user
        # Format: { user_id: CommandSignature }
        self._user_states: Dict[int, CommandSignature] = {}
        
        # Stores token bucket for rate limiting
        # Format: { user_id: (tokens, last_refill_time) }
        self._rate_limits: Dict[int, tuple] = {}

    def check_sanity(self, user_id: int, command_type: str, params: dict) -> bool:
        """
        Check if the command is safe to execute.
        Returns True if safe, False if it looks like spam/loop.
        """
        current_time = time.time()
        
        # 1. Create a unique signature for this exact command
        # We sort keys to ensure {'a':1, 'b':2} is the same as {'b':2, 'a':1}
        param_string = json.dumps(params, sort_keys=True, default=str)
        raw_sig = f"{command_type}:{param_string}"
        sig_hash = hashlib.md5(raw_sig.encode()).hexdigest()
        
        # 2. Get last command for this user
        last_cmd = self._user_states.get(user_id)
        
        # --- CHECK 1: THE STUTTER CHECK (Identical Loop Detection) ---
        if last_cmd and last_cmd.signature_hash == sig_hash:
            time_diff = current_time - last_cmd.timestamp
            
            if time_diff < self.DUPLICATE_WINDOW:
                logger.warning(f"[LOOP DETECTED] Blocked duplicate {command_type} for User {user_id} ({time_diff:.3f}s)")
                return False
        
        # --- CHECK 2: THE SPEED LIMIT (Rate Limiting) ---
        # Simple token bucket: max 10 commands/sec
        if not self._check_rate_limit(user_id, current_time):
            logger.warning(f"[SPAM DETECTED] User {user_id} is sending commands too fast.")
            return False

        # 3. Update State (If we passed checks)
        self._user_states[user_id] = CommandSignature(
            signature_hash=sig_hash,
            timestamp=current_time,
            count=1
        )
        return True

    def _check_rate_limit(self, user_id: int, now: float) -> bool:
        """Returns True if user has tokens remaining"""
        tokens, last_refill = self._rate_limits.get(user_id, (self.RAPID_FIRE_LIMIT, now))
        
        # Refill tokens based on time passed (1 token per second)
        elapsed = now - last_refill
        tokens = min(self.RAPID_FIRE_LIMIT, tokens + elapsed)
        
        if tokens >= 1:
            self._rate_limits[user_id] = (tokens - 1, now)
            return True
        return False

# Singleton Instance (Persists across Streamlit reruns)
_safety_instance = None

def get_safety_middleware() -> SafetyMiddleware:
    global _safety_instance
    if _safety_instance is None:
        _safety_instance = SafetyMiddleware()
    return _safety_instance
