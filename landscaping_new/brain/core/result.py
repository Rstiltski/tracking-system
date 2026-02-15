"""
Result Classes for Brain System

Defines standardized result classes for tool outputs, operations, and responses.
Following the architecture rules, these provide consistent return types across the system.
"""
from __future__ import annotations
import json
from typing import Any, Dict, Optional, Union, Generic, TypeVar
from dataclasses import dataclass, asdict
from datetime import datetime

T = TypeVar('T')

@dataclass
class ToolOutput(Generic[T]):
    """
    Standardized output for all brain tools.
    
    Following the architecture rules, all tools must return a ToolOutput instance
    that contains success status, data, and error information in a consistent format.
    """
    success: bool
    data: Optional[T] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate the ToolOutput after initialization."""
        if self.success and self.error_code:
            raise ValueError("Success cannot be True when error_code is provided")
        if self.success and self.error_message:
            raise ValueError("Success cannot be True when error_message is provided")
        if not self.success and not self.error_code:
            raise ValueError("Error code must be provided when success is False")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the ToolOutput to a dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert the ToolOutput to a JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def success(cls, data: Optional[T] = None, metadata: Optional[Dict[str, Any]] = None) -> ToolOutput[T]:
        """Create a successful ToolOutput."""
        return cls(success=True, data=data, metadata=metadata)
    
    @classmethod
    def failure(cls, error_code: str, error_message: str, metadata: Optional[Dict[str, Any]] = None) -> ToolOutput[T]:
        """Create a failed ToolOutput."""
        return cls(success=False, error_code=error_code, error_message=error_message, metadata=metadata)
    
    def __bool__(self) -> bool:
        """Allow boolean evaluation of ToolOutput."""
        return self.success

@dataclass
class Result(Generic[T]):
    """
    General result class for operations that aren't necessarily tool executions.
    
    Similar to ToolOutput but more general purpose, used for system operations,
    validations, and other non-tool operations.
    """
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the Result to a dictionary."""
        result_dict = asdict(self)
        result_dict['timestamp'] = self.timestamp.isoformat()
        return result_dict
    
    def to_json(self) -> str:
        """Convert the Result to a JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def success(cls, data: Optional[T] = None, message: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Result[T]:
        """Create a successful Result."""
        return cls(success=True, data=data, message=message, metadata=metadata)
    
    @classmethod
    def failure(cls, error_code: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> Result[T]:
        """Create a failed Result."""
        return cls(success=False, error_code=error_code, message=message, metadata=metadata)
    
    def __bool__(self) -> bool:
        """Allow boolean evaluation of Result."""
        return self.success

@dataclass
class ValidationResult:
    """
    Result of a validation operation.
    """
    is_valid: bool
    reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[list] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the ValidationResult to a dictionary."""
        return asdict(self)
    
    @classmethod
    def valid(cls, details: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Create a valid ValidationResult."""
        return cls(is_valid=True, details=details)
    
    @classmethod
    def invalid(cls, reason: str, details: Optional[Dict[str, Any]] = None, suggestions: Optional[list] = None) -> ValidationResult:
        """Create an invalid ValidationResult."""
        return cls(is_valid=False, reason=reason, details=details, suggestions=suggestions)

@dataclass
class AuditTrailEntry:
    """
    Entry in an audit trail for tracking operations.
    """
    operation_id: str
    operation_type: str
    entity_type: str
    entity_id: str
    user_id: str
    timestamp: datetime
    success: bool
    details: Optional[Dict[str, Any]] = None
    before_state: Optional[Any] = None
    after_state: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the AuditTrailEntry to a dictionary."""
        result_dict = asdict(self)
        result_dict['timestamp'] = self.timestamp.isoformat()
        return result_dict

@dataclass
class OperationStatus:
    """
    Status of a long-running operation.
    """
    operation_id: str
    status: str  # 'pending', 'running', 'completed', 'failed', 'cancelled'
    progress: float = 0.0  # 0.0 to 1.0
    message: Optional[str] = None
    result: Optional[Union[ToolOutput, Result]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the OperationStatus to a dictionary."""
        result_dict = asdict(self)
        result_dict['timestamp'] = self.timestamp.isoformat()
        if self.result:
            result_dict['result'] = self.result.to_dict() if hasattr(self.result, 'to_dict') else str(self.result)
        return result_dict