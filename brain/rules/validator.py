"""
Rule Validator - Validates rules for consistency and conflicts

This module provides comprehensive validation for rules including:
- Syntax validation
- Semantic validation
- Conflict detection
- Dependency validation
- Side-effect analysis

📚 REQUIRED READING BEFORE MODIFICATION:
- brain/rules/schema.py
- brain/design/02_policy_packs.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import re

from brain.rules.schema import (
    RuleDefinition,
    RuleType,
    ConflictStrategy,
    Condition,
    Action,
    ActionType,
    ConditionOperator,
)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "ERROR"      # Must be fixed before deployment
    WARNING = "WARNING"  # Should be reviewed
    INFO = "INFO"        # Informational


class ConflictType(Enum):
    """Types of rule conflicts."""
    DIRECT_CONFLICT = "DIRECT_CONFLICT"           # Same trigger, opposite actions
    PRIORITY_CONFLICT = "PRIORITY_CONFLICT"       # Circular priority dependencies
    DEPENDENCY_CONFLICT = "DEPENDENCY_CONFLICT"   # Missing dependencies
    TEMPORAL_CONFLICT = "TEMPORAL_CONFLICT"       # Timing conflicts
    SCOPE_CONFLICT = "SCOPE_CONFLICT"             # Overlapping scopes
    ACTION_CONFLICT = "ACTION_CONFLICT"           # Conflicting actions


@dataclass
class ValidationIssue:
    """A single validation issue."""
    severity: ValidationSeverity
    code: str
    message: str
    rule_id: Optional[str] = None
    field: Optional[str] = None
    suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "rule_id": self.rule_id,
            "field": self.field,
            "suggestion": self.suggestion
        }


@dataclass
class ConflictResult:
    """Result of a conflict check between rules."""
    has_conflict: bool
    conflict_type: Optional[ConflictType] = None
    rule_a_id: Optional[str] = None
    rule_b_id: Optional[str] = None
    description: str = ""
    resolution: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "has_conflict": self.has_conflict,
            "conflict_type": self.conflict_type.value if self.conflict_type else None,
            "rule_a_id": self.rule_a_id,
            "rule_b_id": self.rule_b_id,
            "description": self.description,
            "resolution": self.resolution
        }


@dataclass
class ValidationResult:
    """Complete validation result for a rule."""
    is_valid: bool
    rule_id: str
    issues: List[ValidationIssue] = field(default_factory=list)
    conflicts: List[ConflictResult] = field(default_factory=list)
    dependencies_valid: bool = True
    side_effects: List[str] = field(default_factory=list)
    validated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "is_valid": self.is_valid,
            "rule_id": self.rule_id,
            "issues": [i.to_dict() for i in self.issues],
            "conflicts": [c.to_dict() for c in self.conflicts],
            "dependencies_valid": self.dependencies_valid,
            "side_effects": self.side_effects,
            "validated_at": self.validated_at.isoformat()
        }
    
    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]
    
    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]


class RuleValidator:
    """
    Validates rules for consistency, conflicts, and correctness.
    
    This validator performs comprehensive checks:
    1. Syntax validation - Rule structure is valid
    2. Semantic validation - Rule makes logical sense
    3. Conflict detection - Rule doesn't conflict with existing rules
    4. Dependency validation - All dependencies exist and are valid
    5. Side-effect analysis - Predict what the rule will affect
    """
    
    # Reserved field names that cannot be used
    RESERVED_FIELDS = {"id", "created_at", "updated_at", "deleted_at"}
    
    # Valid operators for each rule type
    VALID_OPERATORS_BY_TYPE = {
        RuleType.POLICY: [
            ConditionOperator.EQ, ConditionOperator.NE,
            ConditionOperator.GT, ConditionOperator.GTE,
            ConditionOperator.LT, ConditionOperator.LTE,
            ConditionOperator.IN, ConditionOperator.NOT_IN,
            ConditionOperator.EXISTS, ConditionOperator.NOT_EXISTS,
            ConditionOperator.IS_NULL, ConditionOperator.IS_NOT_NULL,
            ConditionOperator.AND, ConditionOperator.OR, ConditionOperator.NOT
        ],
        RuleType.INVARIANT: [
            ConditionOperator.EQ, ConditionOperator.NE,
            ConditionOperator.GT, ConditionOperator.GTE,
            ConditionOperator.LT, ConditionOperator.LTE,
            ConditionOperator.IS_NULL, ConditionOperator.IS_NOT_NULL,
            ConditionOperator.AND, ConditionOperator.OR, ConditionOperator.NOT
        ],
        RuleType.STATE: [
            ConditionOperator.EQ, ConditionOperator.IN
        ],
        RuleType.VALIDATION: [
            ConditionOperator.EQ, ConditionOperator.NE,
            ConditionOperator.GT, ConditionOperator.GTE,
            ConditionOperator.LT, ConditionOperator.LTE,
            ConditionOperator.IN, ConditionOperator.NOT_IN,
            ConditionOperator.MATCHES, ConditionOperator.IS_NOT_NULL
        ],
    }
    
    def __init__(self, existing_rules: Optional[List[RuleDefinition]] = None):
        """
        Initialize the validator.
        
        Args:
            existing_rules: List of existing rules to check conflicts against
        """
        self.existing_rules = existing_rules or []
        self._rule_index: Dict[str, RuleDefinition] = {}
        self._rebuild_index()
    
    def _rebuild_index(self):
        """Rebuild the rule index for fast lookups."""
        self._rule_index = {rule.rule_id: rule for rule in self.existing_rules}
    
    def add_rule(self, rule: RuleDefinition):
        """Add a rule to the validator's registry."""
        self.existing_rules.append(rule)
        self._rule_index[rule.rule_id] = rule
    
    def remove_rule(self, rule_id: str):
        """Remove a rule from the validator's registry."""
        self.existing_rules = [r for r in self.existing_rules if r.rule_id != rule.rule_id]
        self._rule_index.pop(rule_id, None)
    
    def validate(self, rule: RuleDefinition) -> ValidationResult:
        """
        Perform comprehensive validation on a rule.
        
        Args:
            rule: The rule to validate
            
        Returns:
            ValidationResult with all validation findings
        """
        issues: List[ValidationIssue] = []
        
        # 1. Syntax validation
        issues.extend(self._validate_syntax(rule))
        
        # 2. Semantic validation
        issues.extend(self._validate_semantics(rule))
        
        # 3. Check dependencies
        dep_issues, deps_valid = self._validate_dependencies(rule)
        issues.extend(dep_issues)
        
        # 4. Detect conflicts
        conflicts = self._detect_conflicts(rule)
        
        # 5. Analyze side effects
        side_effects = self._analyze_side_effects(rule)
        
        # Determine overall validity
        is_valid = len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            rule_id=rule.rule_id,
            issues=issues,
            conflicts=conflicts,
            dependencies_valid=deps_valid,
            side_effects=side_effects
        )
    
    def _validate_syntax(self, rule: RuleDefinition) -> List[ValidationIssue]:
        """Validate rule syntax."""
        issues = []
        
        # Check rule_id format
        if not rule.rule_id:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="SYNTAX_001",
                message="rule_id is required",
                field="rule_id"
            ))
        elif not re.match(r'^[A-Z]+_[0-9]+$', rule.rule_id):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="SYNTAX_002",
                message="rule_id should follow format DOMAIN_### (e.g., MONEY_001)",
                field="rule_id",
                suggestion=f"Consider renaming to {rule.domain.upper()}_###"
            ))
        
        # Check rule_name
        if not rule.rule_name:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="SYNTAX_003",
                message="rule_name is required",
                field="rule_name"
            ))
        
        # Check priority range
        if not 1 <= rule.priority <= 100:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="SYNTAX_004",
                message=f"priority must be between 1 and 100, got {rule.priority}",
                field="priority"
            ))
        
        # Check version format
        if not re.match(r'^\d+\.\d+\.\d+$', rule.version):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="SYNTAX_005",
                message="version should follow SemVer format (e.g., 1.0.0)",
                field="version"
            ))
        
        # Validate conditions
        for i, condition in enumerate(rule.preconditions):
            issues.extend(self._validate_condition(condition, f"preconditions[{i}]"))
        
        for i, condition in enumerate(rule.postconditions):
            issues.extend(self._validate_condition(condition, f"postconditions[{i}]"))
        
        # Validate actions
        for i, action in enumerate(rule.actions):
            issues.extend(self._validate_action(action, f"actions[{i}]"))
        
        return issues
    
    def _validate_condition(self, condition: Condition, path: str) -> List[ValidationIssue]:
        """Validate a single condition."""
        issues = []
        
        # Check field name
        if not condition.field:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="SYNTAX_010",
                message="Condition field is required",
                field=path
            ))
        
        # Check for compound conditions
        if condition.operator in (ConditionOperator.AND, ConditionOperator.OR):
            if len(condition.conditions) < 2:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="SYNTAX_011",
                    message=f"{condition.operator.value} requires at least 2 sub-conditions",
                    field=path
                ))
        elif condition.operator == ConditionOperator.NOT:
            if len(condition.conditions) != 1:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="SYNTAX_012",
                    message="NOT requires exactly 1 sub-condition",
                    field=path
                ))
        else:
            # For non-compound operators, check that value is appropriate
            if condition.value is None and condition.operator not in (
                ConditionOperator.IS_NULL,
                ConditionOperator.IS_NOT_NULL,
                ConditionOperator.EXISTS,
                ConditionOperator.NOT_EXISTS
            ):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="SYNTAX_013",
                    message=f"Condition value is None for operator {condition.operator.value}",
                    field=path
                ))
        
        # Recursively validate nested conditions
        for i, nested in enumerate(condition.conditions):
            issues.extend(self._validate_condition(nested, f"{path}.conditions[{i}]"))
        
        return issues
    
    def _validate_action(self, action: Action, path: str) -> List[ValidationIssue]:
        """Validate a single action."""
        issues = []
        
        # Check action type
        if not action.action_type:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="SYNTAX_020",
                message="Action type is required",
                field=path
            ))
        
        # BLOCK actions should have a message
        if action.action_type == ActionType.BLOCK and not action.message:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="SYNTAX_021",
                message="BLOCK actions should have a message explaining why",
                field=path,
                suggestion="Add a message field to explain the block reason"
            ))
        
        # TRANSFORM actions need a target
        if action.action_type == ActionType.TRANSFORM and not action.target:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="SYNTAX_022",
                message="TRANSFORM actions require a target field",
                field=path
            ))
        
        return issues
    
    def _validate_semantics(self, rule: RuleDefinition) -> List[ValidationIssue]:
        """Validate rule semantics."""
        issues = []
        
        # Check for empty rule
        if not rule.preconditions and not rule.actions and not rule.postconditions:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="SEMANTIC_001",
                message="Rule has no conditions or actions - it will have no effect",
                rule_id=rule.rule_id
            ))
        
        # Check for contradictory conditions
        issues.extend(self._check_contradictory_conditions(rule))
        
        # Check for unreachable conditions
        issues.extend(self._check_unreachable_conditions(rule))
        
        # Validate action-condition alignment
        issues.extend(self._check_action_alignment(rule))
        
        # Check rule type specific semantics
        if rule.rule_type == RuleType.INVARIANT:
            issues.extend(self._validate_invariant_semantics(rule))
        elif rule.rule_type == RuleType.STATE:
            issues.extend(self._validate_state_semantics(rule))
        
        return issues
    
    def _check_contradictory_conditions(self, rule: RuleDefinition) -> List[ValidationIssue]:
        """Check for contradictory conditions within the rule."""
        issues = []
        
        # Simple check for obvious contradictions
        condition_fields = {}
        for condition in rule.preconditions:
            if condition.operator in (ConditionOperator.AND, ConditionOperator.OR, ConditionOperator.NOT):
                continue
            
            field = condition.field
            if field in condition_fields:
                existing = condition_fields[field]
                # Check for obvious contradictions
                if existing.operator == ConditionOperator.EQ and condition.operator == ConditionOperator.NE:
                    if existing.value == condition.value:
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            code="SEMANTIC_010",
                            message=f"Contradictory conditions for field {field}: == and != with same value",
                            rule_id=rule.rule_id
                        ))
            else:
                condition_fields[field] = condition
        
        return issues
    
    def _check_unreachable_conditions(self, rule: RuleDefinition) -> List[ValidationIssue]:
        """Check for conditions that will never be evaluated."""
        issues = []
        
        # This is a simplified check - a full implementation would use symbolic execution
        for i, condition in enumerate(rule.preconditions):
            # Check for conditions that are always false
            if condition.operator == ConditionOperator.EQ and condition.value is None:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="SEMANTIC_020",
                    message=f"Condition {i} compares to null with ==, consider using IS_NULL",
                    rule_id=rule.rule_id
                ))
        
        return issues
    
    def _check_action_alignment(self, rule: RuleDefinition) -> List[ValidationIssue]:
        """Check if actions align with rule type."""
        issues = []
        
        block_actions = [a for a in rule.actions if a.action_type == ActionType.BLOCK]
        allow_actions = [a for a in rule.actions if a.action_type == ActionType.ALLOW]
        
        if rule.rule_type == RuleType.POLICY:
            # Policies should have block actions
            if not block_actions:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="SEMANTIC_030",
                    message="POLICY rules typically have BLOCK actions",
                    rule_id=rule.rule_id,
                    suggestion="Consider adding a BLOCK action for when conditions are not met"
                ))
        
        if rule.rule_type == RuleType.TRIGGER:
            # Triggers should have trigger actions
            trigger_actions = [a for a in rule.actions if a.action_type == ActionType.TRIGGER]
            if not trigger_actions:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="SEMANTIC_031",
                    message="TRIGGER rules should have TRIGGER actions",
                    rule_id=rule.rule_id
                ))
        
        return issues
    
    def _validate_invariant_semantics(self, rule: RuleDefinition) -> List[ValidationIssue]:
        """Validate invariant-specific semantics."""
        issues = []
        
        # Invariants should have postconditions
        if not rule.postconditions:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="SEMANTIC_040",
                message="INVARIANT rules should define postconditions that must hold",
                rule_id=rule.rule_id
            ))
        
        return issues
    
    def _validate_state_semantics(self, rule: RuleDefinition) -> List[ValidationIssue]:
        """Validate state machine rule semantics."""
        issues = []
        
        # State rules should reference state fields
        has_state_field = any(
            'state' in c.field.lower() or 'status' in c.field.lower()
            for c in rule.preconditions
        )
        
        if not has_state_field:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="SEMANTIC_050",
                message="STATE rules typically reference state/status fields",
                rule_id=rule.rule_id
            ))
        
        return issues
    
    def _validate_dependencies(self, rule: RuleDefinition) -> Tuple[List[ValidationIssue], bool]:
        """Validate rule dependencies."""
        issues = []
        all_valid = True
        
        for dep_id in rule.depends_on:
            if dep_id not in self._rule_index:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="DEP_001",
                    message=f"Dependency on non-existent rule: {dep_id}",
                    rule_id=rule.rule_id,
                    field="depends_on"
                ))
                all_valid = False
            else:
                # Check if dependency is deprecated
                dep_rule = self._rule_index[dep_id]
                if dep_rule.deprecated:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        code="DEP_002",
                        message=f"Dependency on deprecated rule: {dep_id}",
                        rule_id=rule.rule_id,
                        field="depends_on"
                    ))
        
        # Check for circular dependencies
        if self._has_circular_dependency(rule):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="DEP_003",
                message="Circular dependency detected",
                rule_id=rule.rule_id,
                field="depends_on"
            ))
            all_valid = False
        
        return issues, all_valid
    
    def _has_circular_dependency(self, rule: RuleDefinition, visited: Optional[Set[str]] = None) -> bool:
        """Check if a rule has circular dependencies."""
        if visited is None:
            visited = set()
        
        if rule.rule_id in visited:
            return True
        
        visited.add(rule.rule_id)
        
        for dep_id in rule.depends_on:
            if dep_id in self._rule_index:
                dep_rule = self._rule_index[dep_id]
                if self._has_circular_dependency(dep_rule, visited.copy()):
                    return True
        
        return False
    
    def _detect_conflicts(self, rule: RuleDefinition) -> List[ConflictResult]:
        """Detect conflicts with existing rules."""
        conflicts = []
        
        for existing_rule in self.existing_rules:
            if existing_rule.rule_id == rule.rule_id:
                continue
            
            # Check for direct conflicts
            conflict = self._check_direct_conflict(rule, existing_rule)
            if conflict.has_conflict:
                conflicts.append(conflict)
            
            # Check for priority conflicts
            conflict = self._check_priority_conflict(rule, existing_rule)
            if conflict.has_conflict:
                conflicts.append(conflict)
            
            # Check for scope conflicts
            conflict = self._check_scope_conflict(rule, existing_rule)
            if conflict.has_conflict:
                conflicts.append(conflict)
        
        return conflicts
    
    def _check_direct_conflict(self, rule_a: RuleDefinition, rule_b: RuleDefinition) -> ConflictResult:
        """Check if two rules directly conflict."""
        # Get blocking actions from both rules
        blocks_a = [a for a in rule_a.actions if a.action_type == ActionType.BLOCK]
        blocks_b = [a for a in rule_b.actions if a.action_type == ActionType.BLOCK]
        
        # If both rules have overlapping conditions and opposite block/allow actions
        allows_a = [a for a in rule_a.actions if a.action_type == ActionType.ALLOW]
        allows_b = [a for a in rule_b.actions if a.action_type == ActionType.ALLOW]
        
        # Check for opposite actions on same domain
        if blocks_a and allows_b:
            if self._conditions_overlap(rule_a.preconditions, rule_b.preconditions):
                return ConflictResult(
                    has_conflict=True,
                    conflict_type=ConflictType.ACTION_CONFLICT,
                    rule_a_id=rule_a.rule_id,
                    rule_b_id=rule_b.rule_id,
                    description=f"Rule {rule_a.rule_id} blocks while {rule_b.rule_id} allows overlapping conditions",
                    resolution="Review priorities or add more specific conditions"
                )
        
        if blocks_b and allows_a:
            if self._conditions_overlap(rule_a.preconditions, rule_b.preconditions):
                return ConflictResult(
                    has_conflict=True,
                    conflict_type=ConflictType.ACTION_CONFLICT,
                    rule_a_id=rule_a.rule_id,
                    rule_b_id=rule_b.rule_id,
                    description=f"Rule {rule_b.rule_id} blocks while {rule_a.rule_id} allows overlapping conditions",
                    resolution="Review priorities or add more specific conditions"
                )
        
        return ConflictResult(has_conflict=False)
    
    def _check_priority_conflict(self, rule_a: RuleDefinition, rule_b: RuleDefinition) -> ConflictResult:
        """Check for priority conflicts between rules."""
        # If rule_a depends on rule_b but has higher priority
        if rule_b.rule_id in rule_a.depends_on and rule_a.priority > rule_b.priority:
            return ConflictResult(
                has_conflict=True,
                conflict_type=ConflictType.PRIORITY_CONFLICT,
                rule_a_id=rule_a.rule_id,
                rule_b_id=rule_b.rule_id,
                description=f"Rule {rule_a.rule_id} depends on {rule_b.rule_id} but has higher priority",
                resolution=f"Lower priority of {rule_a.rule_id} or raise priority of {rule_b.rule_id}"
            )
        
        return ConflictResult(has_conflict=False)
    
    def _check_scope_conflict(self, rule_a: RuleDefinition, rule_b: RuleDefinition) -> ConflictResult:
        """Check for scope conflicts between rules."""
        # Same domain and same type might conflict
        if rule_a.domain == rule_b.domain and rule_a.rule_type == rule_b.rule_type:
            # Check if they operate on the same entities
            fields_a = {c.field for c in rule_a.preconditions}
            fields_b = {c.field for c in rule_b.preconditions}
            
            overlap = fields_a & fields_b
            if overlap:
                return ConflictResult(
                    has_conflict=True,
                    conflict_type=ConflictType.SCOPE_CONFLICT,
                    rule_a_id=rule_a.rule_id,
                    rule_b_id=rule_b.rule_id,
                    description=f"Rules have overlapping scope on fields: {overlap}",
                    resolution="Consider merging rules or adding differentiation"
                )
        
        return ConflictResult(has_conflict=False)
    
    def _conditions_overlap(self, conditions_a: List[Condition], conditions_b: List[Condition]) -> bool:
        """Check if two sets of conditions overlap."""
        # Simplified check - a full implementation would use constraint solving
        fields_a = {c.field for c in conditions_a if c.operator not in (ConditionOperator.AND, ConditionOperator.OR, ConditionOperator.NOT)}
        fields_b = {c.field for c in conditions_b if c.operator not in (ConditionOperator.AND, ConditionOperator.OR, ConditionOperator.NOT)}
        
        return bool(fields_a & fields_b)
    
    def _analyze_side_effects(self, rule: RuleDefinition) -> List[str]:
        """Analyze potential side effects of a rule."""
        effects = []
        
        for action in rule.actions:
            if action.action_type == ActionType.TRANSFORM:
                effects.append(f"Modifies field: {action.target}")
            elif action.action_type == ActionType.TRIGGER:
                effects.append(f"Triggers command: {action.target}")
            elif action.action_type == ActionType.NOTIFY:
                effects.append(f"Sends notification: {action.message}")
            elif action.action_type == ActionType.REPAIR:
                effects.append(f"Auto-repairs: {action.target}")
        
        # Check for wide-reaching conditions
        all_fields = set()
        for condition in rule.preconditions:
            all_fields.add(condition.field)
        
        if len(all_fields) > 5:
            effects.append(f"Touches {len(all_fields)} fields - may have broad impact")
        
        return effects
    
    def validate_batch(self, rules: List[RuleDefinition]) -> Dict[str, ValidationResult]:
        """
        Validate multiple rules at once.
        
        Args:
            rules: List of rules to validate
            
        Returns:
            Dictionary mapping rule_id to ValidationResult
        """
        results = {}
        
        for rule in rules:
            results[rule.rule_id] = self.validate(rule)
        
        # Check inter-rule conflicts
        for i, rule_a in enumerate(rules):
            for rule_b in rules[i+1:]:
                conflict = self._check_direct_conflict(rule_a, rule_b)
                if conflict.has_conflict:
                    results[rule_a.rule_id].conflicts.append(conflict)
                    results[rule_b.rule_id].conflicts.append(conflict)
        
        return results
    
    def get_validation_summary(self, results: Dict[str, ValidationResult]) -> Dict:
        """Get a summary of validation results."""
        total = len(results)
        valid = sum(1 for r in results.values() if r.is_valid)
        with_errors = sum(1 for r in results.values() if r.errors)
        with_warnings = sum(1 for r in results.values() if r.warnings)
        with_conflicts = sum(1 for r in results.values() if r.conflicts)
        
        return {
            "total_rules": total,
            "valid": valid,
            "invalid": total - valid,
            "with_errors": with_errors,
            "with_warnings": with_warnings,
            "with_conflicts": with_conflicts,
            "validation_rate": valid / total if total > 0 else 0
        }


__all__ = [
    "ValidationSeverity",
    "ConflictType",
    "ValidationIssue",
    "ConflictResult",
    "ValidationResult",
    "RuleValidator",
]