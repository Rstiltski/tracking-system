"""
Retention Engine

Per-entity retention policy implementation.
Different data types have different retention requirements.

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from brain.lifecycle.models import RetentionPolicy, RetentionAction


logger = logging.getLogger(__name__)


# Default retention policies per entity type
DEFAULT_POLICIES = {
    'habits': {
        'archive_after_days': None,   # Never archive
        'delete_after_days': None,    # Never delete
        'cascade_to': ['habit_logs']
    },
    'habit_logs': {
        'archive_after_days': 365,    # Archive after 1 year
        'delete_after_days': 730,     # Delete after 2 years
        'cascade_to': []
    },
    'tasks': {
        'archive_after_days': 90,     # Archive after 90 days
        'delete_after_days': 365,     # Delete after 1 year
        'cascade_to': []
    },
    'transactions': {
        'archive_after_days': 2555,   # Archive after 7 years
        'delete_after_days': None,    # Never delete (financial compliance)
        'cascade_to': []
    },
    'health_entries': {
        'archive_after_days': 365,    # Archive after 1 year
        'delete_after_days': 1825,    # Delete after 5 years
        'cascade_to': []
    },
    'time_entries': {
        'archive_after_days': 180,    # Archive after 6 months
        'delete_after_days': 365,     # Delete after 1 year
        'cascade_to': []
    },
    'goals': {
        'archive_after_days': 365,    # Archive after 1 year
        'delete_after_days': 1825,    # Delete after 5 years
        'cascade_to': []
    },
    'xp_logs': {
        'archive_after_days': 90,     # Archive after 90 days
        'delete_after_days': 365,     # Delete after 1 year
        'cascade_to': []
    },
    'audit_logs': {
        'archive_after_days': 365,    # Archive after 1 year
        'delete_after_days': 2555,    # Delete after 7 years
        'cascade_to': []
    },
}


class RetentionEngine:
    """
    Per-entity retention policy engine.
    
    Manages retention policies for different entity types.
    Provides evaluation of what action to take on records.
    
    Example:
        engine = RetentionEngine(db_connection)
        
        # Get action for a record
        action = engine.evaluate('habit_logs', record)
        
        if action == RetentionAction.ARCHIVE:
            archive_manager.archive(record)
    """
    
    def __init__(self, db_connection: sqlite3.Connection = None):
        """
        Initialize retention engine.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
        self._policies: Dict[str, RetentionPolicy] = {}
        self._load_policies()
    
    def _load_policies(self) -> None:
        """Load policies from database or use defaults."""
        if self.db is None:
            # Use defaults only
            self._policies = self._create_default_policies()
            return
        
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM retention_policies WHERE enabled = 1")
            
            for row in cursor.fetchall():
                columns = [desc[0] for desc in cursor.description]
                data = dict(zip(columns, row))
                policy = RetentionPolicy.from_dict(data)
                self._policies[policy.entity_type] = policy
        except Exception:
            # Table doesn't exist yet, use defaults
            pass
        
        # Create defaults for missing policies
        for entity_type, config in DEFAULT_POLICIES.items():
            if entity_type not in self._policies:
                # Use config value - None means never archive/delete for this entity type
                policy = RetentionPolicy(
                    entity_type=entity_type,
                    archive_after_days=config['archive_after_days'],
                    delete_after_days=config['delete_after_days'],
                    cascade_to=config['cascade_to']
                )
                self._policies[entity_type] = policy
    
    def _create_default_policies(self) -> Dict[str, RetentionPolicy]:
        """Create default policies from configuration."""
        policies = {}
        for entity_type, config in DEFAULT_POLICIES.items():
            # Use config value if not None, otherwise use sensible default
            # None means never archive/delete for this entity type
            archive_days = config['archive_after_days']
            delete_days = config['delete_after_days']
            policies[entity_type] = RetentionPolicy(
                entity_type=entity_type,
                archive_after_days=archive_days,
                delete_after_days=delete_days,
                cascade_to=config['cascade_to']
            )
        return policies
    
    def get_policy(self, entity_type: str) -> Optional[RetentionPolicy]:
        """
        Get retention policy for an entity type.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            RetentionPolicy or None if not found
        """
        return self._policies.get(entity_type)
    
    def get_all_policies(self, enabled_only: bool = True) -> List[RetentionPolicy]:
        """
        Get all retention policies.
        
        Args:
            enabled_only: Only return enabled policies
            
        Returns:
            List of retention policies
        """
        policies = list(self._policies.values())
        if enabled_only:
            policies = [p for p in policies if p.enabled]
        return policies
    
    def evaluate(
        self,
        entity_type: str,
        record: Dict[str, Any]
    ) -> RetentionAction:
        """
        Evaluate what action to take on a record.
        
        Args:
            entity_type: Type of entity
            record: Record to evaluate (must have 'created_at' or 'updated_at')
            
        Returns:
            RetentionAction indicating what to do
        """
        policy = self.get_policy(entity_type)
        if not policy:
            return RetentionAction.KEEP
        
        # Get record date
        record_date = record.get('created_at') or record.get('updated_at')
        if not record_date:
            return RetentionAction.KEEP
        
        if isinstance(record_date, str):
            record_date = datetime.fromisoformat(record_date)
        
        age_days = (datetime.now() - record_date).days
        
        # Check delete threshold first (higher priority)
        # None means never delete
        if policy.delete_after_days is not None and age_days >= policy.delete_after_days:
            return RetentionAction.PURGE
        
        # Check archive threshold
        # None means never archive
        if policy.archive_after_days is not None and age_days >= policy.archive_after_days:
            return RetentionAction.ARCHIVE
        
        return RetentionAction.KEEP
    
    def get_records_to_archive(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get all records past archive threshold.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            List of records to archive
        """
        policy = self.get_policy(entity_type)
        if not policy or not policy.archive_after_days:
            return []
        
        threshold = datetime.now() - timedelta(days=policy.archive_after_days)
        
        if self.db is None:
            return []
        
        try:
            cursor = self.db.cursor()
            table_name = self._get_table_name(entity_type)
            
            cursor.execute(
                f"SELECT * FROM {table_name} WHERE created_at < ?",
                (threshold.isoformat(),)
            )
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception:
            return []
    
    def get_records_to_purge(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get all records past delete threshold.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            List of records to purge
        """
        policy = self.get_policy(entity_type)
        if not policy or not policy.delete_after_days:
            return []
        
        threshold = datetime.now() - timedelta(days=policy.delete_after_days)
        
        if self.db is None:
            return []
        
        try:
            cursor = self.db.cursor()
            table_name = self._get_table_name(entity_type)
            
            cursor.execute(
                f"SELECT * FROM {table_name} WHERE created_at < ?",
                (threshold.isoformat(),)
            )
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception:
            return []
    
    def update_policy(self, policy: RetentionPolicy) -> None:
        """
        Update or create a retention policy.
        
        Args:
            policy: Policy to update
        """
        policy.updated_at = datetime.now()
        
        if self.db is None:
            self._policies[policy.entity_type] = policy
            return
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO retention_policies
            (id, entity_type, archive_after_days, delete_after_days, enabled, cascade_to, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            policy.id,
            policy.entity_type,
            policy.archive_after_days,
            policy.delete_after_days,
            policy.enabled,
            ','.join(policy.cascade_to) if policy.cascade_to else '',
            policy.updated_at.isoformat()
        ))
        
        self.db.commit()
        self._policies[policy.entity_type] = policy
    
    def _get_table_name(self, entity_type: str) -> str:
        """Convert entity type to table name."""
        mapping = {
            'habit_logs': 'habit_logs',
            'task_logs': 'task_logs',
            'health_entries': 'health_entries',
            'time_entries': 'time_entries',
            'xp_logs': 'xp_logs',
            'audit_logs': 'audit_log',
        }
        return mapping.get(entity_type, entity_type)
    
    def get_cascade_entities(self, entity_type: str) -> List[str]:
        """
        Get entities that should be cascade deleted.
        
        Args:
            entity_type: Parent entity type
            
        Returns:
            List of child entity types
        """
        policy = self.get_policy(entity_type)
        if not policy:
            return []
        return policy.cascade_to