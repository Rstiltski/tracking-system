"""
Base invariant checker implementation.

Provides framework for checking business invariants.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/03_invariants.md
- LLM_AGENT_QUICKSTART.md
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Callable
from enum import Enum


class ViolationSeverity(Enum):
    """Severity levels for invariant violations."""
    CRITICAL = "critical"  # Immediate action required, blocks operation
    HIGH = "high"          # Serious issue, flag for review
    MEDIUM = "medium"      # Should be fixed, but not urgent
    LOW = "low"            # Minor inconsistency


@dataclass
class InvariantViolation:
    """Represents an invariant violation."""
    code: str
    severity: ViolationSeverity
    entity_type: str  # "invoice", "job", "payment", etc.
    entity_id: Any
    message: str
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class InvariantChecker:
    """
    Base class for invariant checkers.
    
    Subclasses should implement specific invariant checks.
    """
    
    def __init__(self):
        self.violations: List[InvariantViolation] = []
    
    def add_violation(
        self,
        code: str,
        severity: ViolationSeverity,
        entity_type: str,
        entity_id: Any,
        message: str,
        details: Dict[str, Any] = None
    ):
        """Add an invariant violation."""
        violation = InvariantViolation(
            code=code,
            severity=severity,
            entity_type=entity_type,
            entity_id=entity_id,
            message=message,
            details=details or {}
        )
        self.violations.append(violation)
    
    def check_all(self, db_conn=None) -> List[InvariantViolation]:
        """
        Check all invariants.
        
        Args:
            db_conn: Database connection (optional)
            
        Returns:
            List of violations found
        """
        self.violations = []
        # Subclasses implement specific checks
        return self.violations
    
    def has_critical_violations(self) -> bool:
        """Check if any critical violations exist."""
        return any(v.severity == ViolationSeverity.CRITICAL for v in self.violations)

    def check_write(
        self,
        entity_type: str,
        operation: str,
        data: Dict[str, Any],
        entity_id: Any = None
    ) -> "WriteCheckResult":
        """
        Check if a write operation is valid according to business invariants.

        This is called by the Cerebellum before executing a write.

        Args:
            entity_type: Type of entity being written ("job", "invoice", etc.)
            operation: Operation type ("CREATE", "UPDATE", "DELETE")
            data: Data being written
            entity_id: ID of entity (for UPDATE/DELETE)

        Returns:
            WriteCheckResult with is_valid and list of violations
        """
        # For now, stub implementation that allows all writes
        # In full implementation, would check entity-specific invariants
        # Example:
        # - Jobs: Can't complete a job that's not started
        # - Invoices: Can't mark as paid if balance > 0
        # - Payments: Can't refund more than was paid

        violations = []

        # Add your invariant checks here
        # if entity_type == "invoice" and operation == "UPDATE":
        #     if data.get("status") == "PAID" and data.get("balance", 0) > 0:
        #         violations.append("Cannot mark invoice as PAID with balance > 0")

        return WriteCheckResult(
            is_valid=len(violations) == 0,
            violations=violations
        )


    def get_violations_by_severity(self, severity: ViolationSeverity) -> List[InvariantViolation]:
        """Get violations of a specific severity."""
        return [v for v in self.violations if v.severity == severity]

    def clear_violations(self):
        """Clear all recorded violations."""
        self.violations = []


@dataclass
class WriteCheckResult:
    """Result of checking a write operation against invariants"""
    is_valid: bool
    violations: List[str]
