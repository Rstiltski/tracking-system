"""
Rule Schema - Formal Rule Definition Schema

This module defines the formal schema for business rules in the Veryfyn system.
Every rule must conform to this schema for consistency, validation, and versioning.

📚 REQUIRED READING BEFORE MODIFICATION:
- brain/design/02_policy_packs.md
- brain/design/03_invariants.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
import json
import hashlib


class RuleType(Enum):
    """Types of rules in the system."""
    POLICY = "POLICY"              # Preconditions that must be met (blocks execution)
    INVARIANT = "INVARIANT"        # Business rules that must always hold true
    STATE = "STATE"                # State machine transition rules
    TRANSFORMATION = "TRANSFORMATION"  # Data transformation rules
    VALIDATION = "VALIDATION"      # Input validation rules
    TRIGGER = "TRIGGER"            # Event-driven rules (fire on conditions)
    COMPUTED = "COMPUTED"          # Computed/derived value rules


class ConflictStrategy(Enum):
    """How to handle conflicts between rules."""
    OVERRIDE = "OVERRIDE"     # This rule overrides conflicting rules
    BLOCK = "BLOCK"           # This rule blocks execution if conflict
    MERGE = "MERGE"           # Attempt to merge with conflicting rule
    WARN = "WARN"             # Log warning but continue
    DEFER = "DEFER"           # Defer to higher priority rule


class RuleStatus(Enum):
    """Status of a rule."""
    DRAFT = "DRAFT"           # Rule is being drafted
    ACTIVE = "ACTIVE"         # Rule is active and enforced
    DEPRECATED = "DEPRECATED" # Rule is deprecated but still enforced
    DISABLED = "DISABLED"     # Rule is disabled
    ARCHIVED = "ARCHIVED"     # Rule is archived (historical)


class ConditionOperator(Enum):
    """Operators for conditions."""
    EQ = "=="              # Equal
    NE = "!="              # Not equal
    GT = ">"               # Greater than
    GTE = ">="             # Greater than or equal
    LT = "<"               # Less than
    LTE = "<="             # Less than or equal
    IN = "in"              # Value in list
    NOT_IN = "not in"      # Value not in list
    CONTAINS = "contains"  # String/list contains
    MATCHES = "matches"    # Regex match
    EXISTS = "exists"      # Key exists
    NOT_EXISTS = "not exists"  # Key does not exist
    IS_NULL = "is null"    # Value is null
    IS_NOT_NULL = "is not null"  # Value is not null
    AND = "AND"            # Logical AND (for nested conditions)
    OR = "OR"              # Logical OR (for nested conditions)
    NOT = "NOT"            # Logical NOT (for nested conditions)


class ActionType(Enum):
    """Types of actions a rule can perform."""
    BLOCK = "BLOCK"           # Block execution
    ALLOW = "ALLOW"           # Allow execution
    TRANSFORM = "TRANSFORM"   # Transform data
    NOTIFY = "NOTIFY"         # Send notification
    LOG = "LOG"               # Log event
    TRIGGER = "TRIGGER"       # Trigger another command
    COMPUTE = "COMPUTE"       # Compute a value
    VALIDATE = "VALIDATE"     # Validate and return result
    REPAIR = "REPAIR"         # Auto-repair an issue


@dataclass
class Condition:
    """
    A condition that must be evaluated.
    
    Conditions can be simple (field comparison) or compound (AND/OR/NOT).
    """
    field: str                           # Field path (e.g., "invoice.amount", "user.role")
    operator: ConditionOperator          # Comparison operator
    value: Any = None                    # Value to compare against
    conditions: List['Condition'] = field(default_factory=list)  # For compound conditions
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate this condition against a context.
        
        Args:
            context: Dictionary of values to evaluate against
            
        Returns:
            True if condition is met, False otherwise
        """
        # Handle compound conditions
        if self.operator == ConditionOperator.AND:
            return all(c.evaluate(context) for c in self.conditions)
        
        if self.operator == ConditionOperator.OR:
            return any(c.evaluate(context) for c in self.conditions)
        
        if self.operator == ConditionOperator.NOT:
            return not self.conditions[0].evaluate(context) if self.conditions else True
        
        # Get the actual value from context
        actual_value = self._get_field_value(context, self.field)
        
        # Handle existence checks
        if self.operator == ConditionOperator.EXISTS:
            return self.field in context or self._path_exists(context, self.field)
        
        if self.operator == ConditionOperator.NOT_EXISTS:
            return self.field not in context and not self._path_exists(context, self.field)
        
        # Handle null checks
        if self.operator == ConditionOperator.IS_NULL:
            return actual_value is None
        
        if self.operator == ConditionOperator.IS_NOT_NULL:
            return actual_value is not None
        
        # Handle comparison operators
        if self.operator == ConditionOperator.EQ:
            return actual_value == self.value
        
        if self.operator == ConditionOperator.NE:
            return actual_value != self.value
        
        if self.operator == ConditionOperator.GT:
            return actual_value is not None and actual_value > self.value
        
        if self.operator == ConditionOperator.GTE:
            return actual_value is not None and actual_value >= self.value
        
        if self.operator == ConditionOperator.LT:
            return actual_value is not None and actual_value < self.value
        
        if self.operator == ConditionOperator.LTE:
            return actual_value is not None and actual_value <= self.value
        
        if self.operator == ConditionOperator.IN:
            return actual_value in self.value if self.value else False
        
        if self.operator == ConditionOperator.NOT_IN:
            return actual_value not in self.value if self.value else True
        
        if self.operator == ConditionOperator.CONTAINS:
            if actual_value is None:
                return False
            return self.value in actual_value
        
        if self.operator == ConditionOperator.MATCHES:
            import re
            if actual_value is None:
                return False
            return bool(re.match(self.value, str(actual_value)))
        
        return False
    
    def _get_field_value(self, context: Dict[str, Any], field_path: str) -> Any:
        """Get a value from a nested dictionary using dot notation."""
        keys = field_path.split('.')
        current_value = context
        for key in keys:
            if isinstance(current_value, dict) and key in current_value:
                current_value = current_value[key]
            else:
                return None
        return current_value
    
    def _path_exists(self, context: Dict[str, Any], field_path: str) -> bool:
        """Check if a path exists in a nested dictionary."""
        keys = field_path.split('.')
        current_value = context
        for key in keys:
            if isinstance(current_value, dict) and key in current_value:
                current_value = current_value[key]
            else:
                return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "field": self.field,
            "operator": self.operator.value,
            "value": self.value,
            "conditions": [c.to_dict() for c in self.conditions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Condition':
        """Create from dictionary."""
        return cls(
            field=data["field"],
            operator=ConditionOperator(data["operator"]),
            value=data.get("value"),
            conditions=[cls.from_dict(c) for c in data.get("conditions", [])]
        )


@dataclass
class Action:
    """
    An action that a rule can perform.
    """
    action_type: ActionType
    target: Optional[str] = None           # Target field or entity
    value: Optional[Any] = None            # Value to use
    message: Optional[str] = None          # Message for notifications/logs
    params: Dict[str, Any] = field(default_factory=dict)  # Additional parameters
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "action_type": self.action_type.value,
            "target": self.target,
            "value": self.value,
            "message": self.message,
            "params": self.params
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        """Create from dictionary."""
        return cls(
            action_type=ActionType(data["action_type"]),
            target=data.get("target"),
            value=data.get("value"),
            message=data.get("message"),
            params=data.get("params", {})
        )


@dataclass
class RuleDefinition:
    """
    Formal rule definition schema.
    
    Every rule in the system must conform to this schema for:
    - Consistency across rule types
    - Validation and conflict detection
    - Version control and audit trails
    - Dependency mapping
    
    Example:
        rule = RuleDefinition(
            rule_id="MONEY_001",
            rule_name="Payment Cannot Exceed Invoice Balance",
            rule_type=RuleType.INVARIANT,
            domain="finance",
            description="Ensures payment amounts do not exceed remaining invoice balance",
            preconditions=[
                Condition(field="payment.amount", operator=ConditionOperator.GT, value=0)
            ],
            actions=[
                Action(
                    action_type=ActionType.BLOCK,
                    message="Payment amount {payment.amount} exceeds remaining balance {invoice.balance_due}"
                )
            ],
            postconditions=[
                Condition(field="invoice.balance_due", operator=ConditionOperator.GTE, value=0)
            ],
            priority=90,
            conflict_strategy=ConflictStrategy.BLOCK,
            tags=["finance", "payment", "validation"]
        )
    """
    # Identity
    rule_id: str                              # Unique identifier (e.g., "MONEY_001")
    rule_name: str                            # Human-readable name
    rule_type: RuleType                       # Type of rule
    domain: str                               # Domain (e.g., "finance", "scheduling")
    
    # Documentation
    description: str = ""                     # Detailed description
    examples: List[str] = field(default_factory=list)  # Usage examples
    tags: List[str] = field(default_factory=list)      # Tags for search
    
    # Conditions
    preconditions: List[Condition] = field(default_factory=list)    # Must be true before
    actions: List[Action] = field(default_factory=list)             # Actions to perform
    postconditions: List[Condition] = field(default_factory=list)   # Must be true after
    
    # Priority and Conflict
    priority: int = 50                        # Priority (1-100, higher = more important)
    conflict_strategy: ConflictStrategy = ConflictStrategy.WARN
    
    # Version Control
    version: str = "1.0.0"                    # SemVer version
    status: RuleStatus = RuleStatus.DRAFT     # Current status
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    author: str = "system"                    # Who created/modified
    deprecated: bool = False                  # Is this rule deprecated?
    deprecation_message: str = ""             # Message if deprecated
    superseded_by: Optional[str] = None       # ID of rule that supersedes this one
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # IDs of rules this depends on
    conflicts_with: List[str] = field(default_factory=list)  # IDs of conflicting rules
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate rule after initialization."""
        if not 1 <= self.priority <= 100:
            raise ValueError(f"Priority must be between 1 and 100, got {self.priority}")
        
        if not self.rule_id:
            raise ValueError("rule_id is required")
        
        if not self.rule_name:
            raise ValueError("rule_name is required")
    
    def evaluate(self, context: Dict[str, Any]) -> 'RuleEvaluationResult':
        """
        Evaluate this rule against a context.
        
        Args:
            context: Dictionary containing all relevant data
            
        Returns:
            RuleEvaluationResult with pass/fail and actions
        """
        # Evaluate preconditions
        precondition_results = []
        all_preconditions_met = True
        
        for condition in self.preconditions:
            result = condition.evaluate(context)
            precondition_results.append({
                "condition": condition.to_dict(),
                "result": result
            })
            if not result:
                all_preconditions_met = False
        
        # Determine if rule passes
        passed = all_preconditions_met
        
        # Determine actions to take
        actions_to_take = []
        if not passed:
            for action in self.actions:
                if action.action_type in (ActionType.BLOCK, ActionType.NOTIFY, ActionType.LOG):
                    actions_to_take.append(action)
        else:
            for action in self.actions:
                if action.action_type in (ActionType.ALLOW, ActionType.TRANSFORM, ActionType.COMPUTE):
                    actions_to_take.append(action)
        
        return RuleEvaluationResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            passed=passed,
            precondition_results=precondition_results,
            actions=actions_to_take,
            evaluated_at=datetime.now()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "rule_type": self.rule_type.value,
            "domain": self.domain,
            "description": self.description,
            "examples": self.examples,
            "tags": self.tags,
            "preconditions": [c.to_dict() for c in self.preconditions],
            "actions": [a.to_dict() for a in self.actions],
            "postconditions": [c.to_dict() for c in self.postconditions],
            "priority": self.priority,
            "conflict_strategy": self.conflict_strategy.value,
            "version": self.version,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "author": self.author,
            "deprecated": self.deprecated,
            "deprecation_message": self.deprecation_message,
            "superseded_by": self.superseded_by,
            "depends_on": self.depends_on,
            "conflicts_with": self.conflicts_with,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RuleDefinition':
        """Create from dictionary."""
        return cls(
            rule_id=data["rule_id"],
            rule_name=data["rule_name"],
            rule_type=RuleType(data["rule_type"]),
            domain=data["domain"],
            description=data.get("description", ""),
            examples=data.get("examples", []),
            tags=data.get("tags", []),
            preconditions=[Condition.from_dict(c) for c in data.get("preconditions", [])],
            actions=[Action.from_dict(a) for a in data.get("actions", [])],
            postconditions=[Condition.from_dict(c) for c in data.get("postconditions", [])],
            priority=data.get("priority", 50),
            conflict_strategy=ConflictStrategy(data.get("conflict_strategy", "WARN")),
            version=data.get("version", "1.0.0"),
            status=RuleStatus(data.get("status", "DRAFT")),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            modified_at=datetime.fromisoformat(data["modified_at"]) if "modified_at" in data else datetime.now(),
            author=data.get("author", "system"),
            deprecated=data.get("deprecated", False),
            deprecation_message=data.get("deprecation_message", ""),
            superseded_by=data.get("superseded_by"),
            depends_on=data.get("depends_on", []),
            conflicts_with=data.get("conflicts_with", []),
            metadata=data.get("metadata", {})
        )
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RuleDefinition':
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def compute_hash(self) -> str:
        """Compute a hash of the rule for integrity checking."""
        content = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def bump_version(self, bump_type: str = "patch") -> 'RuleDefinition':
        """
        Create a new version of this rule.
        
        Args:
            bump_type: "major", "minor", or "patch"
            
        Returns:
            New RuleDefinition with bumped version
        """
        parts = self.version.split('.')
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        new_version = f"{major}.{minor}.{patch}"
        
        return RuleDefinition(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            rule_type=self.rule_type,
            domain=self.domain,
            description=self.description,
            examples=self.examples.copy(),
            tags=self.tags.copy(),
            preconditions=self.preconditions.copy(),
            actions=self.actions.copy(),
            postconditions=self.postconditions.copy(),
            priority=self.priority,
            conflict_strategy=self.conflict_strategy,
            version=new_version,
            status=self.status,
            created_at=self.created_at,
            modified_at=datetime.now(),
            author=self.author,
            deprecated=self.deprecated,
            deprecation_message=self.deprecation_message,
            superseded_by=self.superseded_by,
            depends_on=self.depends_on.copy(),
            conflicts_with=self.conflicts_with.copy(),
            metadata=self.metadata.copy()
        )


@dataclass
class RuleEvaluationResult:
    """Result of evaluating a rule."""
    rule_id: str
    rule_name: str
    passed: bool
    precondition_results: List[Dict[str, Any]]
    actions: List[Action]
    evaluated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "passed": self.passed,
            "precondition_results": self.precondition_results,
            "actions": [a.to_dict() for a in self.actions],
            "evaluated_at": self.evaluated_at.isoformat()
        }


# Pre-defined rule templates for common patterns
RULE_TEMPLATES = {
    "field_required": {
        "description": "Field must have a value",
        "preconditions_template": [
            {"field": "{field}", "operator": "is not null"}
        ],
        "actions_template": [
            {"action_type": "BLOCK", "message": "{field} is required"}
        ]
    },
    "field_in_range": {
        "description": "Field must be within a range",
        "preconditions_template": [
            {"field": "{field}", "operator": ">=", "value": "{min}"},
            {"field": "{field}", "operator": "<=", "value": "{max}"}
        ],
        "actions_template": [
            {"action_type": "BLOCK", "message": "{field} must be between {min} and {max}"}
        ]
    },
    "field_matches_pattern": {
        "description": "Field must match a regex pattern",
        "preconditions_template": [
            {"field": "{field}", "operator": "matches", "value": "{pattern}"}
        ],
        "actions_template": [
            {"action_type": "BLOCK", "message": "{field} has invalid format"}
        ]
    },
    "state_transition": {
        "description": "Valid state transition rule",
        "preconditions_template": [
            {"field": "{entity}.state", "operator": "==", "value": "{from_state}"}
        ],
        "actions_template": [
            {"action_type": "ALLOW", "target": "{entity}.state", "value": "{to_state}"}
        ]
    }
}


def create_rule_from_template(template_name: str, rule_id: str, rule_name: str, 
                              domain: str, **kwargs) -> RuleDefinition:
    """
    Create a rule from a template.
    
    Args:
        template_name: Name of the template to use
        rule_id: Unique identifier for the rule
        rule_name: Human-readable name
        domain: Domain for the rule
        **kwargs: Values to substitute in template
        
    Returns:
        RuleDefinition created from template
    """
    if template_name not in RULE_TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}")
    
    template = RULE_TEMPLATES[template_name]
    
    # Substitute values in preconditions
    preconditions = []
    for pc in template.get("preconditions_template", []):
        condition_data = {}
        for key, value in pc.items():
            if isinstance(value, str):
                condition_data[key] = value.format(**kwargs)
            else:
                condition_data[key] = value
        preconditions.append(Condition.from_dict(condition_data))
    
    # Substitute values in actions
    actions = []
    for action in template.get("actions_template", []):
        action_data = {}
        for key, value in action.items():
            if isinstance(value, str):
                action_data[key] = value.format(**kwargs)
            else:
                action_data[key] = value
        actions.append(Action.from_dict(action_data))
    
    return RuleDefinition(
        rule_id=rule_id,
        rule_name=rule_name,
        rule_type=RuleType.VALIDATION,
        domain=domain,
        description=template["description"],
        preconditions=preconditions,
        actions=actions
    )


__all__ = [
    "RuleType",
    "ConflictStrategy", 
    "RuleStatus",
    "ConditionOperator",
    "ActionType",
    "Condition",
    "Action",
    "RuleDefinition",
    "RuleEvaluationResult",
    "RULE_TEMPLATES",
    "create_rule_from_template",
]