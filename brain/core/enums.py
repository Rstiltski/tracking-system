"""
Enumerations used throughout the Brain
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from enum import Enum, IntEnum


class Role(str, Enum):
    """User roles for RBAC"""
    OWNER = "Owner"        # Business owner (highest business role)
    ARCHITECT = "Architect"  # System admin (matches db values)
    ADMIN = "Admin"         # Business admin
    STAFF = "Staff"         # Crew/field worker
    READONLY = "ReadOnly"    # Viewer/accountant


class RiskTier(IntEnum):
    """Risk tiers for commands"""
    TRIVIAL = 1      # Read-only, safe updates
    LOW = 2          # Standard operations
    MEDIUM = 3       # Customer-facing, financial
    HIGH = 4         # Money, bulk comms
    CRITICAL = 5     # Irreversible, destructive


class CommandStatus(str, Enum):
    """Command execution status"""
    PENDING = "PENDING"
    EXECUTING = "EXECUTING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    DUPLICATE = "DUPLICATE"
    DENIED = "DENIED"


class PolicyStatus(str, Enum):
    """Policy check result status"""
    ALLOW = "ALLOW"
    DENY = "DENY"
    WARN = "WARN"
    DUPLICATE = "DUPLICATE"


class JobStatus(str, Enum):
    """Job state machine states"""
    DRAFT = "DRAFT"
    QUOTED = "QUOTED"
    BOOKED = "BOOKED"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    AWAITING_SIGNOFF = "AWAITING_SIGNOFF"
    COMPLETED = "COMPLETED"
    INVOICED = "INVOICED"
    CANCELLED = "CANCELLED"


class InvoiceStatus(str, Enum):
    """Invoice state machine states"""
    DRAFT = "DRAFT"
    SENT = "SENT"
    VIEWED = "VIEWED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    VOID = "VOID"


class PaymentStatus(str, Enum):
    """Payment state machine states"""
    PENDING = "PENDING"
    CLEARED = "CLEARED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class QuoteStatus(str, Enum):
    """Quote state machine states"""
    DRAFT = "DRAFT"
    SENT = "SENT"
    VIEWED = "VIEWED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class MessageStatus(str, Enum):
    """Message state machine states"""
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    SENDING = "SENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# Additional Enums for Application-Wide Consistency (Phase 4)

class ErrorCode(str, Enum):
    """Standardized error codes"""
    # Validation errors (1xxx)
    VALIDATION_ERROR = "E1001"
    REQUIRED_FIELD_MISSING = "E1002"
    INVALID_FORMAT = "E1003"
    INVALID_VALUE = "E1004"
    
    # Permission errors (2xxx)
    PERMISSION_DENIED = "E2001"
    UNAUTHORIZED = "E2002"
    ENTITLEMENT_REQUIRED = "E2003"
    
    # Resource errors (3xxx)
    RESOURCE_NOT_FOUND = "E3001"
    RESOURCE_ALREADY_EXISTS = "E3002"
    RESOURCE_LOCKED = "E3003"
    
    # State errors (4xxx)
    INVALID_STATE_TRANSITION = "E4001"
    BUSINESS_RULE_VIOLATION = "E4002"
    INVARIANT_VIOLATION = "E4003"
    
    # Execution errors (5xxx)
    EXECUTION_FAILED = "E5001"
    TIMEOUT = "E5002"
    EXTERNAL_SERVICE_ERROR = "E5003"
    
    # Confirmation errors (6xxx)
    CONFIRMATION_REQUIRED = "E6001"
    CONFIRMATION_INVALID = "E6002"
    CONFIRMATION_EXPIRED = "E6003"
    
    # System errors (9xxx)
    INTERNAL_ERROR = "E9001"
    DATABASE_ERROR = "E9002"
    UNKNOWN_ERROR = "E9999"


class PaymentMethod(str, Enum):
    """Payment methods"""
    CASH = "Cash"
    CARD = "Card"
    BANK_TRANSFER = "Bank Transfer"
    CHEQUE = "Cheque"
    STRIPE = "Stripe"
    PAYPAL = "PayPal"
    OTHER = "Other"


class MessageType(str, Enum):
    """Communication message types"""
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    PHONE = "phone"


class NoteType(str, Enum):
    """Customer note types"""
    GENERAL = "general"
    COMPLAINT = "complaint"
    PRAISE = "praise"
    FOLLOW_UP = "follow_up"
    INTERNAL = "internal"


class PhotoType(str, Enum):
    """Photo types for customer properties"""
    PROPERTY = "property"
    BEFORE = "before"
    AFTER = "after"
    ISSUE = "issue"
    PROGRESS = "progress"


class TeamRole(str, Enum):
    """Crew team roles"""
    LEAD = "Lead"
    ASSISTANT = "Assistant"


class SubscriptionTier(str, Enum):
    """Subscription plan tiers"""
    FREE = "FREE"
    PRO = "PRO"
    ELITE = "ELITE"


class SoilType(str, Enum):
    """Soil types for calculator (Phase 7)"""
    CLAY = "Clay"
    SAND = "Sand"
    CHALK = "Chalk"
    ROCK = "Rock"
    MADE_GROUND = "Made Ground"
    LOAM = "Loam"


class SurfaceType(str, Enum):
    """Surface types for load bearing checks (Phase 7)"""
    PATIO = "Patio"
    DRIVEWAY = "Driveway"
    PATH = "Path"
    COMMERCIAL = "Commercial"
    ROOF_TERRACE = "Roof Terrace"


class Season(str, Enum):
    """Seasons for weather adjustments (Phase 7)"""
    WINTER = "Winter"
    SUMMER = "Summer"
    SPRING = "Spring"
    AUTUMN = "Autumn"


class ExpenseCategory(str, Enum):
    """Expense categories"""
    MATERIALS = "Materials"
    FUEL = "Fuel"
    EQUIPMENT = "Equipment"
    SUBCONTRACTOR = "Subcontractor"
    PERMITS = "Permits"
    WASTE_DISPOSAL = "Waste Disposal"
    OTHER = "Other"


# Utility functions for backward compatibility and convenience

def get_error_code_description(code: str) -> str:
    """
    Get human-readable description for error code
    
    Args:
        code: Error code (e.g., "E1001")
    
    Returns:
        Description of the error code
    """
    descriptions = {
        ErrorCode.VALIDATION_ERROR: "Validation error - input data is invalid",
        ErrorCode.REQUIRED_FIELD_MISSING: "Required field is missing",
        ErrorCode.INVALID_FORMAT: "Invalid data format",
        ErrorCode.INVALID_VALUE: "Invalid value provided",
        ErrorCode.PERMISSION_DENIED: "Permission denied",
        ErrorCode.UNAUTHORIZED: "User is not authorized",
        ErrorCode.ENTITLEMENT_REQUIRED: "Feature requires higher subscription tier",
        ErrorCode.RESOURCE_NOT_FOUND: "Requested resource not found",
        ErrorCode.RESOURCE_ALREADY_EXISTS: "Resource already exists",
        ErrorCode.RESOURCE_LOCKED: "Resource is locked",
        ErrorCode.INVALID_STATE_TRANSITION: "Invalid state transition attempted",
        ErrorCode.BUSINESS_RULE_VIOLATION: "Business rule violation",
        ErrorCode.INVARIANT_VIOLATION: "Invariant violation",
        ErrorCode.EXECUTION_FAILED: "Command execution failed",
        ErrorCode.TIMEOUT: "Operation timed out",
        ErrorCode.EXTERNAL_SERVICE_ERROR: "External service error",
        ErrorCode.CONFIRMATION_REQUIRED: "Confirmation required for this operation",
        ErrorCode.CONFIRMATION_INVALID: "Invalid confirmation token",
        ErrorCode.CONFIRMATION_EXPIRED: "Confirmation token expired",
        ErrorCode.INTERNAL_ERROR: "Internal server error",
        ErrorCode.DATABASE_ERROR: "Database error",
        ErrorCode.UNKNOWN_ERROR: "Unknown error",
    }
    
    try:
        error_enum = ErrorCode(code)
        return descriptions.get(error_enum, "Unknown error code")
    except ValueError:
        return "Unknown error code"

