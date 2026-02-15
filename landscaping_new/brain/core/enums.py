"""
Enums for Brain System

Defines all enumerations used in the brain system including risk tiers,
tool statuses, and other categorical values.
"""
from __future__ import annotations
from enum import Enum

class RiskTier(Enum):
    """
    Risk classification for tools and operations.
    
    Following security best practices, all operations are classified by risk level:
    - LOW: Safe operations that can run without confirmation
    - MEDIUM: Operations that modify data but are generally safe
    - HIGH: Operations that could significantly impact the system
    - CRITICAL: Operations that could cause data loss or system instability
    """
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ToolStatus(Enum):
    """
    Status of a tool execution.
    """
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AuditLevel(Enum):
    """
    Level of detail for audit logging.
    """
    MINIMAL = "minimal"
    STANDARD = "standard"
    VERBOSE = "verbose"

class OperationType(Enum):
    """
    Type of operation being performed.
    """
    READ = "read"
    WRITE = "write"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    CONFIGURE = "configure"

class EntityType(Enum):
    """
    Types of entities that can be operated on.
    """
    CUSTOMER = "customer"
    JOB = "job"
    INVOICE = "invoice"
    PAYMENT = "payment"
    USER = "user"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    SCHEDULE = "schedule"
    TIME_ENTRY = "time_entry"
    QUOTE = "quote"
    COMPANY = "company"
    TEAM = "team"

class ValidationStatus(Enum):
    """
    Status of validation operations.
    """
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    ERROR = "error"

class SecurityLevel(Enum):
    """
    Security classification levels.
    """
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SECRET = "secret"

class Priority(Enum):
    """
    Priority levels for operations and tasks.
    """
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class NotificationType(Enum):
    """
    Types of notifications that can be sent.
    """
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    ALERT = "alert"

class ChannelType(Enum):
    """
    Communication channel types.
    """
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    INTERNAL = "internal"