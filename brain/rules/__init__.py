"""
Rules Module - Formal Rule Definition and Management

This module provides a comprehensive system for defining, validating,
versioning, and managing business rules in the Veryfyn system.

Components:
- schema.py: Formal rule definition schema
- validator.py: Rule validation and conflict detection
- version_control.py: Rule versioning and history
- dependency_mapper.py: Rule dependency graph
- audit_trail.py: Rule change tracking
"""

from brain.rules.schema import (
    RuleDefinition,
    RuleType,
    ConflictStrategy,
    Condition,
    Action,
    RuleStatus,
)
from brain.rules.validator import RuleValidator, ValidationResult
from brain.rules.version_control import RuleVersionControl

__all__ = [
    "RuleDefinition",
    "RuleType",
    "ConflictStrategy",
    "Condition",
    "Action",
    "RuleStatus",
    "RuleValidator",
    "ValidationResult",
    "RuleVersionControl",
]