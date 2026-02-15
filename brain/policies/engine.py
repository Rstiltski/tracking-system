"""
Policy Engine - Executes policies in order
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/02_policy_packs.md
- LLM_AGENT_QUICKSTART.md
"""

from brain.core.command_event import CommandEvent
from brain.core.result import PolicyResult
from brain.policies.security import SecurityPolicy
from brain.policies.integrity import IntegrityPolicy
from brain.policies.scheduling import SchedulingPolicy
from brain.policies.communications import CommunicationsPolicy


class PolicyEngine:
    """
    Executes policies in order.

    Policies are validation rules that run BEFORE command execution.
    If any policy denies, command execution is blocked.

    Policy execution order:
    1. Security Policy - Authentication, authorization, RBAC
    2. Integrity Policy - Data consistency, business rules
    3. Scheduling Policy - Crew conflicts, capacity limits
    4. Communications Policy - Rate limiting, duplicate prevention
    """

    def __init__(self):
        self.policies = [
            SecurityPolicy(),
            IntegrityPolicy(),
            SchedulingPolicy(),
            CommunicationsPolicy(),
        ]

    def check(self, event: CommandEvent) -> PolicyResult:
        """
        Run all policies.

        Returns:
            PolicyResult - ALLOW, DENY, WARN, or DUPLICATE
        """
        for policy in self.policies:
            result = policy.check(event)

            if result.is_denied:
                # Hard failure - stop execution
                return result

            if result.is_duplicate:
                # Return cached result (idempotent)
                return result

            if result.status == "WARN":
                # Log warning but continue
                print(f"⚠️  Policy Warning: {result.message}")

        return PolicyResult.allow()
