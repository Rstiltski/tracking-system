"""
Rule Version Control - Versioning and history management for rules

This module provides version control for rules including:
- Version tracking
- Change history
- Rollback capability
- Diff generation

📚 REQUIRED READING BEFORE MODIFICATION:
- brain/rules/schema.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import json
import hashlib
from pathlib import Path

from brain.rules.schema import RuleDefinition, RuleStatus


class ChangeType(Enum):
    """Types of changes to rules."""
    CREATED = "CREATED"
    MODIFIED = "MODIFIED"
    DEPRECATED = "DEPRECATED"
    REACTIVATED = "REACTIVATED"
    VERSION_BUMP = "VERSION_BUMP"
    STATUS_CHANGED = "STATUS_CHANGED"


@dataclass
class RuleChange:
    """A single change to a rule."""
    change_id: str
    rule_id: str
    change_type: ChangeType
    version_before: Optional[str]
    version_after: str
    timestamp: datetime
    author: str
    description: str
    diff: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "change_id": self.change_id,
            "rule_id": self.rule_id,
            "change_type": self.change_type.value,
            "version_before": self.version_before,
            "version_after": self.version_after,
            "timestamp": self.timestamp.isoformat(),
            "author": self.author,
            "description": self.description,
            "diff": self.diff,
            "reason": self.reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RuleChange':
        return cls(
            change_id=data["change_id"],
            rule_id=data["rule_id"],
            change_type=ChangeType(data["change_type"]),
            version_before=data.get("version_before"),
            version_after=data["version_after"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            author=data["author"],
            description=data["description"],
            diff=data.get("diff"),
            reason=data.get("reason")
        )


@dataclass
class RuleVersion:
    """A snapshot of a rule at a specific version."""
    rule_id: str
    version: str
    rule_definition: RuleDefinition
    created_at: datetime
    author: str
    is_current: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "rule_id": self.rule_id,
            "version": self.version,
            "rule_definition": self.rule_definition.to_dict(),
            "created_at": self.created_at.isoformat(),
            "author": self.author,
            "is_current": self.is_current
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RuleVersion':
        return cls(
            rule_id=data["rule_id"],
            version=data["version"],
            rule_definition=RuleDefinition.from_dict(data["rule_definition"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            author=data["author"],
            is_current=data.get("is_current", False)
        )


class RuleVersionControl:
    """
    Manages version control for rules.
    
    Features:
    - Track all rule changes
    - Store version history
    - Generate diffs between versions
    - Rollback to previous versions
    - Export/import version history
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize version control.
        
        Args:
            storage_path: Path to store version history (default: brain/rules/history/)
        """
        if storage_path is None:
            project_root = Path(__file__).parent.parent.parent
            storage_path = str(project_root / "brain" / "rules" / "history")
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._versions: Dict[str, List[RuleVersion]] = {}
        self._changes: List[RuleChange] = []
        self._load_history()
    
    def _load_history(self):
        """Load version history from storage."""
        history_file = self.storage_path / "rule_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                
                for rule_id, versions in data.get("versions", {}).items():
                    self._versions[rule_id] = [RuleVersion.from_dict(v) for v in versions]
                
                self._changes = [RuleChange.from_dict(c) for c in data.get("changes", [])]
            except (json.JSONDecodeError, KeyError):
                self._versions = {}
                self._changes = []
    
    def _save_history(self):
        """Save version history to storage."""
        history_file = self.storage_path / "rule_history.json"
        
        data = {
            "versions": {
                rule_id: [v.to_dict() for v in versions]
                for rule_id, versions in self._versions.items()
            },
            "changes": [c.to_dict() for c in self._changes]
        }
        
        with open(history_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_rule(self, rule: RuleDefinition, author: str = "system") -> RuleVersion:
        """
        Record a new rule creation.
        
        Args:
            rule: The rule to create
            author: Who created the rule
            
        Returns:
            The created RuleVersion
        """
        # Create initial version
        version = RuleVersion(
            rule_id=rule.rule_id,
            version=rule.version,
            rule_definition=rule,
            created_at=datetime.now(),
            author=author,
            is_current=True
        )
        
        # Initialize version list
        if rule.rule_id not in self._versions:
            self._versions[rule.rule_id] = []
        
        self._versions[rule.rule_id].append(version)
        
        # Record the change
        change = RuleChange(
            change_id=self._generate_change_id(),
            rule_id=rule.rule_id,
            change_type=ChangeType.CREATED,
            version_before=None,
            version_after=rule.version,
            timestamp=datetime.now(),
            author=author,
            description=f"Created rule {rule.rule_name}"
        )
        self._changes.append(change)
        
        self._save_history()
        return version
    
    def update_rule(
        self, 
        rule: RuleDefinition, 
        author: str = "system",
        reason: Optional[str] = None
    ) -> RuleVersion:
        """
        Record a rule update.
        
        Args:
            rule: The updated rule
            author: Who made the update
            reason: Reason for the update
            
        Returns:
            The new RuleVersion
        """
        # Get current version
        current = self.get_current_version(rule.rule_id)
        version_before = current.version if current else None
        
        # Mark old version as not current
        if rule.rule_id in self._versions:
            for v in self._versions[rule.rule_id]:
                v.is_current = False
        
        # Create new version
        version = RuleVersion(
            rule_id=rule.rule_id,
            version=rule.version,
            rule_definition=rule,
            created_at=datetime.now(),
            author=author,
            is_current=True
        )
        
        if rule.rule_id not in self._versions:
            self._versions[rule.rule_id] = []
        
        self._versions[rule.rule_id].append(version)
        
        # Generate diff
        diff = None
        if current:
            diff = self._generate_diff(current.rule_definition, rule)
        
        # Record the change
        change = RuleChange(
            change_id=self._generate_change_id(),
            rule_id=rule.rule_id,
            change_type=ChangeType.MODIFIED,
            version_before=version_before,
            version_after=rule.version,
            timestamp=datetime.now(),
            author=author,
            description=f"Updated rule {rule.rule_name}",
            diff=diff,
            reason=reason
        )
        self._changes.append(change)
        
        self._save_history()
        return version
    
    def deprecate_rule(
        self, 
        rule_id: str, 
        author: str = "system",
        reason: str = ""
    ) -> Optional[RuleVersion]:
        """
        Deprecate a rule.
        
        Args:
            rule_id: ID of the rule to deprecate
            author: Who deprecated it
            reason: Reason for deprecation
            
        Returns:
            The new deprecated version, or None if rule not found
        """
        current = self.get_current_version(rule_id)
        if not current:
            return None
        
        # Create deprecated version
        deprecated_rule = current.rule_definition.bump_version("minor")
        deprecated_rule.deprecated = True
        deprecated_rule.deprecation_message = reason
        
        return self.update_rule(
            deprecated_rule, 
            author=author,
            reason=f"Deprecated: {reason}"
        )
    
    def rollback(
        self, 
        rule_id: str, 
        target_version: str,
        author: str = "system"
    ) -> Optional[RuleVersion]:
        """
        Rollback a rule to a previous version.
        
        Args:
            rule_id: ID of the rule
            target_version: Version to rollback to
            author: Who performed the rollback
            
        Returns:
            The new version, or None if target version not found
        """
        # Find target version
        target = None
        if rule_id in self._versions:
            for v in self._versions[rule_id]:
                if v.version == target_version:
                    target = v
                    break
        
        if not target:
            return None
        
        # Create a new version with the old content
        rolled_back = target.rule_definition.bump_version("minor")
        
        return self.update_rule(
            rolled_back,
            author=author,
            reason=f"Rollback to version {target_version}"
        )
    
    def get_current_version(self, rule_id: str) -> Optional[RuleVersion]:
        """Get the current version of a rule."""
        if rule_id not in self._versions:
            return None
        
        for version in reversed(self._versions[rule_id]):
            if version.is_current:
                return version
        
        return None
    
    def get_version_history(self, rule_id: str) -> List[RuleVersion]:
        """Get all versions of a rule."""
        return self._versions.get(rule_id, [])
    
    def get_changes(self, rule_id: Optional[str] = None) -> List[RuleChange]:
        """Get changes, optionally filtered by rule."""
        if rule_id:
            return [c for c in self._changes if c.rule_id == rule_id]
        return self._changes
    
    def compare_versions(
        self, 
        rule_id: str, 
        version_a: str, 
        version_b: str
    ) -> Optional[Dict[str, Any]]:
        """Compare two versions of a rule."""
        v_a = None
        v_b = None
        
        if rule_id in self._versions:
            for v in self._versions[rule_id]:
                if v.version == version_a:
                    v_a = v
                if v.version == version_b:
                    v_b = v
        
        if not v_a or not v_b:
            return None
        
        return self._generate_diff(v_a.rule_definition, v_b.rule_definition)
    
    def _generate_diff(
        self, 
        rule_a: RuleDefinition, 
        rule_b: RuleDefinition
    ) -> Dict[str, Any]:
        """Generate a diff between two rules."""
        dict_a = rule_a.to_dict()
        dict_b = rule_b.to_dict()
        
        diff = {
            "added": {},
            "removed": {},
            "changed": {}
        }
        
        all_keys = set(dict_a.keys()) | set(dict_b.keys())
        
        for key in all_keys:
            if key not in dict_a:
                diff["added"][key] = dict_b[key]
            elif key not in dict_b:
                diff["removed"][key] = dict_a[key]
            elif dict_a[key] != dict_b[key]:
                diff["changed"][key] = {
                    "before": dict_a[key],
                    "after": dict_b[key]
                }
        
        return diff
    
    def _generate_change_id(self) -> str:
        """Generate a unique change ID."""
        timestamp = datetime.now().isoformat()
        random_bytes = hashlib.sha256(timestamp.encode()).hexdigest()[:8]
        return f"CHG-{timestamp[:10]}-{random_bytes}"
    
    def export_history(self, rule_id: Optional[str] = None) -> str:
        """Export version history as JSON."""
        if rule_id:
            data = {
                "rule_id": rule_id,
                "versions": [v.to_dict() for v in self._versions.get(rule_id, [])],
                "changes": [c.to_dict() for c in self.get_changes(rule_id)]
            }
        else:
            data = {
                "versions": {
                    rid: [v.to_dict() for v in versions]
                    for rid, versions in self._versions.items()
                },
                "changes": [c.to_dict() for c in self._changes]
            }
        
        return json.dumps(data, indent=2)
    
    def import_history(self, json_data: str, merge: bool = True):
        """
        Import version history from JSON.
        
        Args:
            json_data: JSON string of version history
            merge: If True, merge with existing history; if False, replace
        """
        data = json.loads(json_data)
        
        if not merge:
            self._versions = {}
            self._changes = []
        
        for rule_id, versions in data.get("versions", {}).items():
            if rule_id not in self._versions:
                self._versions[rule_id] = []
            
            existing_versions = {v.version for v in self._versions[rule_id]}
            for v_data in versions:
                v = RuleVersion.from_dict(v_data)
                if v.version not in existing_versions:
                    self._versions[rule_id].append(v)
        
        existing_changes = {c.change_id for c in self._changes}
        for c_data in data.get("changes", []):
            c = RuleChange.from_dict(c_data)
            if c.change_id not in existing_changes:
                self._changes.append(c)
        
        self._save_history()


__all__ = [
    "ChangeType",
    "RuleChange",
    "RuleVersion",
    "RuleVersionControl",
]