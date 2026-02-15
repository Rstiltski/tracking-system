"""
Guardrails for Brain System

Implements validation and safety checks for the brain system.
"""
from __future__ import annotations
import logging
import re
from typing import Dict, Any, List
from brain.core.result import ValidationResult

# Initialize logger
logger = logging.getLogger(__name__)

class GuardrailValidator:
    """
    Implements guardrails to validate commands and prevent unsafe operations.
    
    This class provides validation checks to ensure commands are safe to execute.
    """
    
    def __init__(self):
        # Define dangerous patterns that should be blocked
        self.dangerous_patterns = [
            r'\bdrop\s+table\b',  # DROP TABLE
            r'\bdrop\s+database\b',  # DROP DATABASE
            r'\balter\s+table\b.*\bdrop\b',  # ALTER TABLE DROP
            r'\bdelete\s+from\s+\w+\s*$',  # DELETE without WHERE (full table delete)
            r'\bexec\b',  # EXEC (stored procedure execution)
            r'\bsp_\w+',  # Stored procedure calls
            r'\bshutdown\b',  # SHUTDOWN
            r'\bkill\b',  # KILL (process killing)
            r'\bgrant\b',  # GRANT permissions
            r'\brevoke\b',  # REVOKE permissions
        ]
        
        # Compile regex patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns]
        
        logger.info("GuardrailValidator initialized with safety checks")
    
    def validate_command(self, command: str, params: Dict[str, Any]) -> ValidationResult:
        """
        Validate a command and its parameters for safety.
        
        Args:
            command: The command to validate
            params: The parameters for the command
            
        Returns:
            ValidationResult indicating if the command is safe
        """
        # Check command name for dangerous patterns
        if self._contains_dangerous_pattern(command):
            return ValidationResult.invalid(
                reason=f"Command '{command}' contains dangerous patterns",
                suggestions=["Use safer alternatives", "Review command for security issues"]
            )
        
        # Check parameters for dangerous patterns
        params_str = str(params)
        if self._contains_dangerous_pattern(params_str):
            return ValidationResult.invalid(
                reason="Parameters contain dangerous patterns",
                suggestions=["Sanitize input parameters", "Use parameterized queries"]
            )
        
        # Additional validation checks
        validation_results = self._perform_additional_validations(command, params)
        if not validation_results.is_valid:
            return validation_results
        
        # Command is valid
        return ValidationResult.valid(
            details={
                "command": command,
                "param_count": len(params),
                "validation_passed": True
            }
        )
    
    def _contains_dangerous_pattern(self, text: str) -> bool:
        """
        Check if text contains any dangerous patterns.
        
        Args:
            text: Text to check for dangerous patterns
            
        Returns:
            True if dangerous pattern found, False otherwise
        """
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _perform_additional_validations(self, command: str, params: Dict[str, Any]) -> ValidationResult:
        """
        Perform additional validation checks specific to commands.
        
        Args:
            command: The command being validated
            params: The parameters for the command
            
        Returns:
            ValidationResult indicating validation result
        """
        # Check for SQL injection attempts in parameters
        sql_injection_patterns = [
            r"'(?:--|#|/\*|\\)",
            r"(?:union|select|insert|update|delete|drop|create|alter)\s+(?:table|database|view|index)",
            r"exec\s*\(",
        ]
        
        for param_name, param_value in params.items():
            if isinstance(param_value, str):
                for pattern in sql_injection_patterns:
                    if re.search(pattern, param_value, re.IGNORECASE):
                        return ValidationResult.invalid(
                            reason=f"Potential SQL injection detected in parameter '{param_name}'",
                            details={"parameter": param_name, "value": param_value},
                            suggestions=["Use parameterized queries", "Validate and sanitize input"]
                        )
        
        # Check for path traversal attempts
        path_traversal_patterns = [r'\.\./', r'\.\.\\', r'%2e%2e%2f', r'%2e%2e%5c']
        for param_name, param_value in params.items():
            if isinstance(param_value, str):
                for pattern in path_traversal_patterns:
                    if re.search(pattern, param_value, re.IGNORECASE):
                        return ValidationResult.invalid(
                            reason=f"Potential path traversal detected in parameter '{param_name}'",
                            details={"parameter": param_name, "value": param_value},
                            suggestions=["Validate file paths", "Use allowlists for file access"]
                        )
        
        # All additional validations passed
        return ValidationResult.valid()
    
    def add_dangerous_pattern(self, pattern: str) -> None:
        """
        Add a new dangerous pattern to the validator.
        
        Args:
            pattern: The regex pattern to add
        """
        self.dangerous_patterns.append(pattern)
        self.compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
        logger.debug(f"Added dangerous pattern: {pattern}")
    
    def get_dangerous_patterns(self) -> List[str]:
        """
        Get the list of dangerous patterns.
        
        Returns:
            List of dangerous patterns
        """
        return self.dangerous_patterns[:]
    
    def validate_data_access(self, entity_type: str, entity_id: int, operation: str) -> ValidationResult:
        """
        Validate data access for security.
        
        Args:
            entity_type: Type of entity being accessed
            entity_id: ID of the entity
            operation: Type of operation (read, write, update, delete)
            
        Returns:
            ValidationResult indicating if access is allowed
        """
        # Basic validation - in a real system, this would check permissions
        allowed_entities = ['customer', 'job', 'user', 'invoice', 'payment', 'material', 'equipment']
        
        if entity_type.lower() not in allowed_entities:
            return ValidationResult.invalid(
                reason=f"Access to entity type '{entity_type}' is not allowed",
                suggestions=["Use allowed entity types only", "Check permissions"]
            )
        
        # Validate operation
        allowed_operations = ['read', 'write', 'update', 'delete']
        if operation.lower() not in allowed_operations:
            return ValidationResult.invalid(
                reason=f"Operation '{operation}' is not allowed",
                suggestions=["Use allowed operations only"]
            )
        
        # Validate entity ID
        if entity_id <= 0:
            return ValidationResult.invalid(
                reason="Entity ID must be positive",
                suggestions=["Provide a valid entity ID"]
            )
        
        return ValidationResult.valid(
            details={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "operation": operation
            }
        )