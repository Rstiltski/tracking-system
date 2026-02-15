"""
Invariants module for Brain architecture.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/03_invariants.md
- LLM_AGENT_QUICKSTART.md
"""

from brain.invariants.checker import InvariantChecker, InvariantViolation, ViolationSeverity
from brain.invariants.money_invariants import MoneyInvariants
from brain.invariants.linking_invariants import LinkingInvariants
from brain.invariants.idempotency_invariants import IdempotencyInvariants

__all__ = [
    'InvariantChecker',
    'InvariantViolation',
    'ViolationSeverity',
    'MoneyInvariants',
    'LinkingInvariants',
    'IdempotencyInvariants',
]
