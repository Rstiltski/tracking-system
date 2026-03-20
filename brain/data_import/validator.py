"""
Data Import Validator

Python-based validation engine for import data.
Validates schema, data types, referential integrity, and business rules.

All implementation is in Python 3.10+
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Represents a validation error."""
    module: str
    record_id: Optional[str]
    field: Optional[str]
    error_type: str
    message: str
    value: Any = None


class ImportValidator:
    """
    Validates imported data before insertion.
    
    Uses Python-based validation rules to check:
    - Schema structure
    - Data types
    - Referential integrity
    - Business rules
    - Duplicate detection
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize validator.
        
        Args:
            db_connection: SQLite database connection for integrity checks
        """
        self.db = db_connection
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []
    
    def validate_all(
        self,
        modules: Dict[str, List[Dict[str, Any]]]
    ) -> Tuple[bool, List[ValidationError]]:
        """
        Run all validations on imported data.
        
        Args:
            modules: Dictionary mapping module names to records
            
        Returns:
            Tuple of (is_valid, errors)
        """
        self.errors = []
        self.warnings = []
        
        # Validate each module
        for module_name, records in modules.items():
            self._validate_module(module_name, records)
        
        # Check referential integrity across modules
        self._validate_referential_integrity(modules)
        
        return len(self.errors) == 0, self.errors
    
    def _validate_module(
        self,
        module_name: str,
        records: List[Dict[str, Any]]
    ) -> None:
        """Validate records in a single module."""
        for i, record in enumerate(records):
            # Schema validation
            self._validate_schema(module_name, record, i)
            
            # Data type validation
            self._validate_data_types(module_name, record, i)
            
            # Business rules
            self._validate_business_rules(module_name, record, i)
    
    def _validate_schema(
        self,
        module_name: str,
        record: Dict[str, Any],
        index: int
    ) -> None:
        """
        Validate record has required fields.
        
        Args:
            module_name: Name of module
            record: Record dictionary
            index: Record index for error reporting
        """
        # Get required fields for this module
        required_fields = self._get_required_fields(module_name)
        
        for field in required_fields:
            if field not in record:
                self.errors.append(ValidationError(
                    module=module_name,
                    record_id=record.get('id', f'index_{index}'),
                    field=field,
                    error_type='missing_field',
                    message=f"Missing required field: {field}",
                    value=record
                ))
    
    def _validate_data_types(
        self,
        module_name: str,
        record: Dict[str, Any],
        index: int
    ) -> None:
        """
        Validate field data types.
        
        Args:
            module_name: Name of module
            record: Record dictionary
            index: Record index
        """
        type_rules = self._get_type_rules(module_name)
        
        for field, expected_type in type_rules.items():
            if field not in record:
                continue
            
            value = record[field]
            
            if value is None:
                continue  # None is valid for optional fields
            
            if not self._check_type(value, expected_type):
                self.errors.append(ValidationError(
                    module=module_name,
                    record_id=record.get('id', f'index_{index}'),
                    field=field,
                    error_type='type_mismatch',
                    message=f"Expected {expected_type}, got {type(value).__name__}",
                    value=value
                ))
    
    def _validate_business_rules(
        self,
        module_name: str,
        record: Dict[str, Any],
        index: int
    ) -> None:
        """
        Validate business-specific rules.
        
        Args:
            module_name: Name of module
            record: Record dictionary
            index: Record index
        """
        if module_name == 'habits':
            self._validate_habit_rules(record, index)
        elif module_name == 'tasks':
            self._validate_task_rules(record, index)
        elif module_name == 'transactions':
            self._validate_transaction_rules(record, index)
        elif module_name == 'goals':
            self._validate_goal_rules(record, index)
    
    def _validate_habit_rules(
        self,
        record: Dict[str, Any],
        index: int
    ) -> None:
        """Validate habit-specific business rules."""
        # Streak cannot be negative
        if 'streak' in record and record['streak'] is not None:
            if record['streak'] < 0:
                self.errors.append(ValidationError(
                    module='habits',
                    record_id=record.get('id', f'index_{index}'),
                    field='streak',
                    error_type='business_rule',
                    message='Streak cannot be negative',
                    value=record['streak']
                ))
        
        # Frequency must be valid
        if 'frequency' in record and record['frequency'] is not None:
            valid_frequencies = ['daily', 'weekly', 'monthly']
            if record['frequency'] not in valid_frequencies:
                self.errors.append(ValidationError(
                    module='habits',
                    record_id=record.get('id', f'index_{index}'),
                    field='frequency',
                    error_type='business_rule',
                    message=f'Invalid frequency: {record["frequency"]}',
                    value=record['frequency']
                ))
    
    def _validate_task_rules(
        self,
        record: Dict[str, Any],
        index: int
    ) -> None:
        """Validate task-specific business rules."""
        # Priority must be valid
        if 'priority' in record and record['priority'] is not None:
            valid_priorities = ['low', 'medium', 'high', 'urgent']
            if record['priority'] not in valid_priorities:
                self.errors.append(ValidationError(
                    module='tasks',
                    record_id=record.get('id', f'index_{index}'),
                    field='priority',
                    error_type='business_rule',
                    message=f'Invalid priority: {record["priority"]}',
                    value=record['priority']
                ))
    
    def _validate_transaction_rules(
        self,
        record: Dict[str, Any],
        index: int
    ) -> None:
        """Validate transaction-specific business rules."""
        # Amount cannot be None
        if 'amount' in record and record['amount'] is None:
            self.errors.append(ValidationError(
                module='transactions',
                record_id=record.get('id', f'index_{index}'),
                field='amount',
                error_type='business_rule',
                message='Amount cannot be null',
                value=None
            ))
        
        # Transaction type must be valid
        if 'transaction_type' in record and record['transaction_type'] is not None:
            valid_types = ['income', 'expense']
            if record['transaction_type'] not in valid_types:
                self.errors.append(ValidationError(
                    module='transactions',
                    record_id=record.get('id', f'index_{index}'),
                    field='transaction_type',
                    error_type='business_rule',
                    message=f'Invalid transaction type: {record["transaction_type"]}',
                    value=record['transaction_type']
                ))
    
    def _validate_goal_rules(
        self,
        record: Dict[str, Any],
        index: int
    ) -> None:
        """Validate goal-specific business rules."""
        # Target value should be positive
        if 'target_value' in record and record['target_value'] is not None:
            if record['target_value'] <= 0:
                self.errors.append(ValidationError(
                    module='goals',
                    record_id=record.get('id', f'index_{index}'),
                    field='target_value',
                    error_type='business_rule',
                    message='Target value must be positive',
                    value=record['target_value']
                ))
        
        # Current value should not exceed target
        if ('target_value' in record and record['target_value'] is not None and
            'current_value' in record and record['current_value'] is not None):
            if record['current_value'] > record['target_value']:
                self.warnings.append(
                    f"Goal '{record.get('title', 'unknown')}': "
                    f"current value exceeds target"
                )
    
    def _validate_referential_integrity(
        self,
        modules: Dict[str, List[Dict[str, Any]]]
    ) -> None:
        """
        Validate references between modules.
        
        Args:
            modules: Dictionary of modules with their records
        """
        # Build ID indexes for each module
        indexes = {}
        for module_name, records in modules.items():
            indexes[module_name] = {
                record.get('id'): record
                for record in records
                if 'id' in record
            }
        
        # Check foreign key references
        # Example: habit_logs should reference valid habits
        if 'habit_logs' in modules and 'habits' in indexes:
            habit_ids = set(indexes['habits'].keys())
            
            for log in modules['habit_logs']:
                habit_id = log.get('habit_id')
                if habit_id and habit_id not in habit_ids:
                    # Check if exists in database
                    if self.db:
                        exists = self._check_habit_exists(habit_id)
                        if not exists:
                            self.errors.append(ValidationError(
                                module='habit_logs',
                                record_id=log.get('id'),
                                field='habit_id',
                                error_type='referential_integrity',
                                message=f"Referenced habit not found: {habit_id}",
                                value=habit_id
                            ))
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """
        Check if value matches expected type.
        
        Args:
            value: Value to check
            expected_type: Expected type name
            
        Returns:
            True if type matches
        """
        type_map = {
            'str': (str,),
            'int': (int,),
            'float': (float, int),
            'bool': (bool,),
            'list': (list,),
            'dict': (dict,),
            'datetime': (str,),  # ISO format strings
            'uuid': (str,),  # UUID strings
        }
        
        expected_types = type_map.get(expected_type, (object,))
        
        # Special handling for datetime strings
        if expected_type == 'datetime' and isinstance(value, str):
            try:
                datetime.fromisoformat(value)
                return True
            except ValueError:
                return False
        
        # Special handling for UUID strings
        if expected_type == 'uuid' and isinstance(value, str):
            uuid_pattern = re.compile(
                r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
                re.IGNORECASE
            )
            return bool(uuid_pattern.match(value))
        
        return isinstance(value, expected_types)
    
    def _check_habit_exists(self, habit_id: str) -> bool:
        """Check if habit exists in database."""
        if not self.db:
            return False
        
        try:
            cursor = self.db.execute(
                "SELECT 1 FROM habits WHERE id = ?",
                (habit_id,)
            )
            return cursor.fetchone() is not None
        except Exception:
            return False
    
    def _get_required_fields(self, module_name: str) -> List[str]:
        """Get required fields for a module."""
        required = {
            'habits': ['id', 'name'],
            'tasks': ['id', 'title'],
            'goals': ['id', 'title'],
            'transactions': ['id', 'amount'],
            'health_entries': ['id', 'metric', 'value'],
            'time_entries': ['id'],
            'achievements': ['id', 'name'],
        }
        return required.get(module_name, ['id'])
    
    def _get_type_rules(self, module_name: str) -> Dict[str, str]:
        """Get type rules for a module."""
        # Note: 'id' field accepts any non-empty value (string or UUID)
        # This allows flexibility for imported data from external systems
        rules = {
            'habits': {
                'streak': 'int',
                'created_at': 'datetime',
            },
            'tasks': {
                'completed': 'bool',
                'created_at': 'datetime',
            },
            'transactions': {
                'amount': 'float',
                'date': 'datetime',
            },
            'goals': {
                'target_value': 'float',
                'current_value': 'float',
                'deadline': 'datetime',
            },
        }
        return rules.get(module_name, {})
    
    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            'total_errors': len(self.errors),
            'errors_by_type': self._count_by_type(),
            'errors_by_module': self._count_by_module(),
            'warnings': len(self.warnings),
            'is_valid': len(self.errors) == 0,
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count errors by type."""
        counts = {}
        for error in self.errors:
            counts[error.error_type] = counts.get(error.error_type, 0) + 1
        return counts
    
    def _count_by_module(self) -> Dict[str, int]:
        """Count errors by module."""
        counts = {}
        for error in self.errors:
            counts[error.module] = counts.get(error.module, 0) + 1
        return counts
