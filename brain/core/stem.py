"""
Phase 1: The Brainstem - Survival Core

The Brainstem is the ONLY entry point for all commands.
It is the security guard that checks credentials before allowing access to the 3 Brains.

The Brainstem performs:
1. Authentication (is this a valid user?)
2. Authorization (does this user have permission?)
3. Rate limiting (is this user flooding the system?)
4. Idempotency (have we seen this command before?)

If any check fails, the command is REJECTED before reaching business logic.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

import time
import hashlib
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from brain.core.contracts import ICommand, CapabilityScope
from brain.core.result import BrainResult
from brain.policies.security import SecurityPolicy
from brain.core.command_event import CommandEvent
from brain.core.system_status import SystemStatus, DefconLevel


class RateLimiter:
    """
    Rate limiter to prevent flooding/DoS attacks.

    Uses a sliding window algorithm to track requests per user.
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[int, list] = defaultdict(list)

    def check_rate_limit(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Check if user has exceeded rate limit.

        Returns:
            (allowed, error_message) - (True, None) if allowed, (False, msg) if denied
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > window_start
        ]

        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False, f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds}s"

        # Record request
        self.requests[user_id].append(now)
        return True, None

    def reset(self, user_id: int):
        """Reset rate limit for a user (e.g., after successful login)"""
        if user_id in self.requests:
            del self.requests[user_id]


class IdempotencyGuard:
    """
    Idempotency guard to prevent duplicate command execution.

    Stores command hashes and prevents re-execution within a time window.
    """

    def __init__(self, window_hours: int = 24):
        """
        Args:
            window_hours: How long to remember commands (default 24 hours)
        """
        self.window_hours = window_hours
        self.seen_commands: Dict[str, datetime] = {}

    def _compute_hash(self, command: ICommand) -> str:
        """
        Compute hash of command for idempotency check.

        Uses: command_type + user_id + payload (excluding timestamp)
        """
        # Use idempotency_key if provided
        if command.idempotency_key:
            return command.idempotency_key

        # Otherwise, hash the command content
        content = f"{command.command_type}:{command.user_id}:{str(sorted(command.payload.items()))}"
        return hashlib.sha256(content.encode()).hexdigest()

    def check_duplicate(self, command: ICommand) -> Tuple[bool, Optional[str]]:
        """
        Check if command is a duplicate.

        Returns:
            (is_duplicate, error_message)
        """
        cmd_hash = self._compute_hash(command)
        now = datetime.utcnow()

        # Clean old entries
        cutoff = now - timedelta(hours=self.window_hours)
        self.seen_commands = {
            k: v for k, v in self.seen_commands.items()
            if v > cutoff
        }

        # Check if we've seen this command before
        if cmd_hash in self.seen_commands:
            first_seen = self.seen_commands[cmd_hash]
            return True, f"Duplicate command detected (first seen: {first_seen})"

        # Record this command
        self.seen_commands[cmd_hash] = now
        return False, None


class RiskEngine:
    """
    Phase 9.1: Risk Engine & Entropy Detection
    
    Track user behavior "weirdness" score based on anomalous actions.
    
    Instead of just counting requests, calculate a risk score based on:
    - Failed authentication attempts (+50 points)
    - 404 errors - probing for vulnerabilities (+10 points)
    - Admin actions during non-business hours (+20 points)
    - Honeypot field access (+30 points)
    - SQL injection attempts (+100 points)
    - Score decays over time (-5 points per hour for legitimate users)
    
    Enforcement levels:
    - Risk 0-30 (GREEN): Normal operation
    - Risk 31-80 (AMBER): Add 2-second delay (tar pit)
    - Risk 81+ (RED): Auto-logout + require re-authentication
    
    Example:
        risk_engine = RiskEngine()
        
        # Add risk points
        risk_engine.add_risk(user_id, 50, "FAILED_AUTH")
        
        # Check risk level
        level = risk_engine.get_risk_level(user_id)  # "AMBER" or "RED"
        
        # Enforce risk policy
        risk_engine.enforce_risk_policy(user_id)  # May throw exception or add delay
    """
    
    def __init__(self, decay_rate: float = 5.0):
        """
        Initialize Risk Engine.
        
        Args:
            decay_rate: Points to decay per hour (default: 5.0)
        """
        self.user_scores: Dict[int, float] = defaultdict(float)
        self.last_decay: Dict[int, datetime] = {}
        self.decay_rate = decay_rate
        
        # Risk point values
        self.RISK_POINTS = {
            'FAILED_AUTH': 50,
            'NOT_FOUND_404': 10,
            'ADMIN_AFTER_HOURS': 20,
            'HONEYPOT_ACCESS': 30,
            'SQL_INJECTION': 100,
            'RAPID_FIRE': 15,
            'LARGE_EXPORT': 25,
            'INVALID_INPUT': 10,
        }
        
        # Risk level thresholds
        self.AMBER_THRESHOLD = 31
        self.RED_THRESHOLD = 81
    
    def add_risk(self, user_id: int, points: int, reason: str, details: str = None):
        """
        Add risk points to user score.
        
        Args:
            user_id: User ID
            points: Points to add
            reason: Reason for adding risk (e.g., "FAILED_AUTH")
            details: Optional additional details
        """
        # Apply decay first
        self._apply_decay(user_id)
        
        # Add points
        old_score = self.user_scores[user_id]
        self.user_scores[user_id] += points
        new_score = self.user_scores[user_id]
        
        # Log risk event
        self._log_risk_event(user_id, points, reason, details, old_score, new_score)
        
        # Check if we should trigger elevated mode
        if new_score >= self.RED_THRESHOLD and old_score < self.RED_THRESHOLD:
            self._trigger_red_mode(user_id, reason)
        elif new_score >= self.AMBER_THRESHOLD and old_score < self.AMBER_THRESHOLD:
            self._trigger_amber_mode(user_id, reason)
    
    def add_risk_by_type(self, user_id: int, risk_type: str, details: str = None):
        """
        Add risk points using predefined risk type.
        
        Args:
            user_id: User ID
            risk_type: Risk type key (e.g., "FAILED_AUTH", "NOT_FOUND_404")
            details: Optional additional details
        """
        points = self.RISK_POINTS.get(risk_type, 10)
        self.add_risk(user_id, points, risk_type, details)
    
    def get_risk_score(self, user_id: int) -> float:
        """
        Get current risk score for user (after decay).
        
        Args:
            user_id: User ID
            
        Returns:
            Current risk score
        """
        self._apply_decay(user_id)
        return self.user_scores[user_id]
    
    def get_risk_level(self, user_id: int) -> str:
        """
        Get risk level: GREEN, AMBER, or RED.
        
        Args:
            user_id: User ID
            
        Returns:
            Risk level string
        """
        score = self.get_risk_score(user_id)
        
        if score >= self.RED_THRESHOLD:
            return "RED"
        elif score >= self.AMBER_THRESHOLD:
            return "AMBER"
        else:
            return "GREEN"
    
    def enforce_risk_policy(self, user_id: int):
        """
        Apply risk-based throttling or blocking.
        
        Args:
            user_id: User ID
            
        Raises:
            SecurityException: If risk score too high (RED level)
        """
        level = self.get_risk_level(user_id)
        score = self.get_risk_score(user_id)
        
        if level == "RED":
            # Block request - require re-authentication
            from brain.core.result import BrainResult
            raise Exception(f"Risk score too high ({score:.1f}). Please contact administrator.")
        
        elif level == "AMBER":
            # Tar pit delay - slow down requests
            time.sleep(2)
    
    def reset_risk(self, user_id: int, reason: str = "Manual reset"):
        """
        Reset risk score for user.
        
        Args:
            user_id: User ID
            reason: Reason for reset
        """
        old_score = self.user_scores[user_id]
        self.user_scores[user_id] = 0
        self.last_decay[user_id] = datetime.now()
        
        # Log reset
        self._log_risk_event(user_id, -old_score, "RISK_RESET", reason, old_score, 0)
    
    def _apply_decay(self, user_id: int):
        """
        Decay risk score over time (legitimate users recover).
        
        Args:
            user_id: User ID
        """
        now = datetime.now()
        last = self.last_decay.get(user_id, now)
        hours_elapsed = (now - last).total_seconds() / 3600
        
        if hours_elapsed > 0:
            decay = hours_elapsed * self.decay_rate
            self.user_scores[user_id] = max(0, self.user_scores[user_id] - decay)
            self.last_decay[user_id] = now
    
    def _log_risk_event(self, user_id: int, points: float, reason: str, 
                       details: str, old_score: float, new_score: float):
        """
        Log risk event to audit trail.
        
        Args:
            user_id: User ID
            points: Points added/removed
            reason: Reason for risk change
            details: Additional details
            old_score: Score before change
            new_score: Score after change
        """
        try:
            import db
            from datetime import datetime as dt
            
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO audit_log 
                (user_id, company_id, action, entity_type, entity_id, details, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                1,  # Company ID
                'RISK_SCORE_CHANGE',
                'user',
                user_id,
                f"{reason}: {points:+.1f} points. Score: {old_score:.1f} -> {new_score:.1f}. {details or ''}",
                dt.now()
            ))
            conn.commit()
        except Exception as e:
            # Don't fail if audit logging fails
            print(f"Warning: Failed to log risk event: {e}")
    
    def _trigger_amber_mode(self, user_id: int, reason: str):
        """
        Trigger AMBER (elevated) security mode for user.
        
        Args:
            user_id: User ID with high risk
            reason: Reason for elevation
        """
        try:
            from brain.core.system_status import trigger_elevated_mode
            trigger_elevated_mode(
                reason=f"HIGH_RISK_SCORE_USER_{user_id}",
                details=f"User {user_id} risk score exceeded AMBER threshold. Reason: {reason}",
                user_id=user_id
            )
        except ImportError:
            print(f"Warning: SystemStatus not available. User {user_id} has high risk score.")
    
    def _trigger_red_mode(self, user_id: int, reason: str):
        """
        Trigger RED (lockdown) mode for user.
        
        Args:
            user_id: User ID with critical risk
            reason: Reason for lockdown
        """
        try:
            from brain.core.system_status import trigger_kill_switch
            trigger_kill_switch(
                reason=f"CRITICAL_RISK_SCORE_USER_{user_id}",
                details=f"User {user_id} risk score exceeded RED threshold. Reason: {reason}",
                user_id=user_id
            )
        except ImportError:
            print(f"Warning: SystemStatus not available. User {user_id} has critical risk score.")


class Brainstem:
    """
    Phase 1: The Brainstem - Survival Core

    The ONLY entry point for all commands.

    Flow:
    1. User/UI creates a command
    2. Command goes through Brainstem
    3. Brainstem checks: Auth, RBAC, Rate Limit, Idempotency
    4. If all checks pass → Forward to appropriate Brain
    5. If any check fails → REJECT immediately

    Usage:
        stem = Brainstem()
        result = stem.process(command)
        if result.success:
            # Command is authenticated and authorized
            # Safe to forward to OpsBrain/FinanceBrain/RelationBrain
        else:
            # Command rejected, return error to user
    """

    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        idempotency_guard: Optional[IdempotencyGuard] = None,
        security_policy: Optional[SecurityPolicy] = None,
        risk_engine: Optional[RiskEngine] = None
    ):
        """
        Initialize the Brainstem.

        Args:
            rate_limiter: Custom rate limiter (optional)
            idempotency_guard: Custom idempotency guard (optional)
            security_policy: Custom security policy (optional)
            risk_engine: Custom risk engine (optional) - Phase 9.1
        """
        self.rate_limiter = rate_limiter or RateLimiter(
            max_requests=100,  # 100 requests
            window_seconds=60   # per minute
        )
        self.idempotency_guard = idempotency_guard or IdempotencyGuard(
            window_hours=24  # Remember commands for 24 hours
        )
        self.security_policy = security_policy or SecurityPolicy()
        self.risk_engine = risk_engine or RiskEngine(decay_rate=5.0)

    def _map_command_to_operation(self, command_type: str) -> str:
        """
        Map command type to operation name for system status checks.

        Args:
            command_type: Command type (e.g., "CreatePayment", "CreateInvoice")

        Returns:
            Operation name (e.g., "CREATE_PAYMENT")
        """
        # Convert CamelCase to UPPER_SNAKE_CASE
        # CreatePayment -> CREATE_PAYMENT
        import re
        operation = re.sub(r'(?<!^)(?=[A-Z])', '_', command_type).upper()
        return operation

    def _convert_to_command_event(self, command: ICommand) -> CommandEvent:
        """
        Convert ICommand (new) to CommandEvent (legacy).

        This allows gradual migration while maintaining backward compatibility.
        """
        return CommandEvent(
            command_id=command.command_id,
            command_type=command.command_type,
            params=command.payload,
            user_id=command.user_id,
            company_id=command.company_id,
            session_id=command.session_id,
            client_ip=command.client_ip,
            user_agent=command.user_agent,
            timestamp=command.timestamp,
            idempotency_key=command.idempotency_key,
            confirmation_token=command.confirmation_token,
            metadata=command.metadata
        )

    def process(self, command: ICommand) -> BrainResult:
        """
        Process a command through the Brainstem security checks.

        This is the MAIN ENTRY POINT for all commands.

        Args:
            command: The command to process (ICommand)

        Returns:
            BrainResult: Success if all checks pass, error if any check fails

        Security Checks:
        0. System Status - Check global kill switch (Phase 11.1)
        1. Risk Assessment - Check user risk score (Phase 9.1)
        2. Rate Limiting - Prevent DoS
        3. Idempotency - Prevent duplicates
        4. Authentication - Valid user?
        5. Authorization - Has permission?
        """

        # CHECKPOINT -1: System Status (Phase 11.1 - Kill Switch)
        # Check if system is in elevated security mode
        system_status = SystemStatus()

        # Map command type to operation for access check
        operation = self._map_command_to_operation(command.command_type)

        if not system_status.check_access(command.user_id, operation):
            level = system_status.level
            reason = system_status.reason or "Security policy"

            if level == DefconLevel.RED:
                return BrainResult.fail(
                    error_message=f"🚨 SYSTEM LOCKDOWN: {reason}. Only administrators can access the system.",
                    error_code="SYSTEM_LOCKDOWN_RED",
                    data={
                        "defcon_level": level.value,
                        "reason": reason,
                        "user_id": command.user_id
                    }
                )
            elif level == DefconLevel.AMBER:
                return BrainResult.fail(
                    error_message=f"⚠️  ELEVATED SECURITY: {reason}. This operation is temporarily restricted.",
                    error_code="SYSTEM_ELEVATED_AMBER",
                    data={
                        "defcon_level": level.value,
                        "reason": reason,
                        "operation": operation
                    }
                )

        # CHECKPOINT 0: Risk Assessment (Phase 9.1)
        # Check if user has high risk score
        risk_level = self.risk_engine.get_risk_level(command.user_id)
        risk_score = self.risk_engine.get_risk_score(command.user_id)

        # RED mode: Auto-logout required
        if risk_level == 'RED':
            # Add risk for attempting action while in RED mode
            self.risk_engine.add_risk_by_type(command.user_id, 'INVALID_INPUT',
                                             details=f"Action attempted in RED mode: {command.command_type}")
            return BrainResult.fail(
                error_message=f"Account security alert: Re-authentication required (risk score: {risk_score:.0f})",
                error_code="BRAINSTEM_HIGH_RISK_LOGOUT",
                data={"user_id": command.user_id, "risk_level": risk_level, "risk_score": risk_score}
            )

        # AMBER mode: Apply tar pit delay
        if risk_level == 'AMBER':
            self.risk_engine.enforce_risk_policy(command.user_id)
            # Delay is applied inside enforce_risk_policy()

        # CHECKPOINT 1: Rate Limiting
        allowed, error = self.rate_limiter.check_rate_limit(command.user_id)
        if not allowed:
            # Track rapid-fire attempts as suspicious
            self.risk_engine.add_risk_by_type(command.user_id, 'RAPID_FIRE',
                                             details=f"Rate limit hit: {command.command_type}")
            return BrainResult.fail(
                error_message=error,
                error_code="BRAINSTEM_RATE_LIMIT",
                data={"user_id": command.user_id}
            )

        # CHECKPOINT 2: Idempotency Check
        is_duplicate, error = self.idempotency_guard.check_duplicate(command)
        if is_duplicate:
            return BrainResult.fail(
                error_message=error,
                error_code="BRAINSTEM_DUPLICATE_COMMAND",
                data={"command_id": command.command_id}
            )

        # CHECKPOINT 3 & 4: Authentication + Authorization
        # Convert ICommand to CommandEvent for backward compatibility with SecurityPolicy
        legacy_event = self._convert_to_command_event(command)

        # Run security policy checks
        policy_result = self.security_policy.check(legacy_event)
        if policy_result.is_denied:
            # Track failed authorization as suspicious
            self.risk_engine.add_risk_by_type(command.user_id, 'INVALID_INPUT',
                                             details=f"Authorization denied: {command.command_type}")
            return BrainResult.fail(
                error_message=policy_result.reason,
                error_code=policy_result.error_code or "BRAINSTEM_SECURITY_DENIED",
                data={
                    "user_id": command.user_id,
                    "command_type": command.command_type
                }
            )

        # ALL CHECKS PASSED ✅
        # Command is authenticated, authorized, and safe to proceed
        # Reward legitimate behavior by allowing decay
        return BrainResult.ok(
            data={
                "status": "authenticated",
                "command_id": command.command_id,
                "user_id": command.user_id,
                "command_type": command.command_type,
                "risk_level": risk_level,
                "risk_score": risk_score
            },
            message="Command passed Brainstem security checks"
        )

    def reset_rate_limit(self, user_id: int):
        """Reset rate limit for a user (admin function)"""
        self.rate_limiter.reset(user_id)


# Convenience function for direct use
def authenticate_command(command: ICommand) -> BrainResult:
    """
    Authenticate a command through the Brainstem.

    This is a convenience function for one-off authentication.
    For performance, create a Brainstem instance and reuse it.

    Usage:
        cmd = create_command("JobCreate", user_id=1, payload={...})
        result = authenticate_command(cmd)
        if result.success:
            # Safe to proceed
            pass
    """
    stem = Brainstem()
    return stem.process(command)
