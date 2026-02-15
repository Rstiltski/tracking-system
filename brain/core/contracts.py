"""
Phase 0: The Constitution - Strict Contracts & Schemas

This module defines the rigid rules that every part of the system must obey.
All commands and events MUST conform to these Pydantic models.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any, Literal
from uuid import uuid4
from enum import Enum


class EventType(str, Enum):
    """Standard event types emitted by the system"""
    # Job events
    JOB_CREATED = "JOB_CREATED"
    JOB_UPDATED = "JOB_UPDATED"
    JOB_SCHEDULED = "JOB_SCHEDULED"
    JOB_STARTED = "JOB_STARTED"
    JOB_COMPLETED = "JOB_COMPLETED"
    JOB_CANCELLED = "JOB_CANCELLED"

    # Invoice events
    INVOICE_CREATED = "INVOICE_CREATED"
    INVOICE_SENT = "INVOICE_SENT"
    INVOICE_VIEWED = "INVOICE_VIEWED"
    INVOICE_PAID = "INVOICE_PAID"
    INVOICE_VOIDED = "INVOICE_VOIDED"

    # Payment events
    PAYMENT_RECORDED = "PAYMENT_RECORDED"
    PAYMENT_CLEARED = "PAYMENT_CLEARED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_REFUNDED = "PAYMENT_REFUNDED"

    # Customer events
    CUSTOMER_CREATED = "CUSTOMER_CREATED"
    CUSTOMER_UPDATED = "CUSTOMER_UPDATED"

    # Quote events
    QUOTE_CREATED = "QUOTE_CREATED"
    QUOTE_SENT = "QUOTE_SENT"
    QUOTE_ACCEPTED = "QUOTE_ACCEPTED"
    QUOTE_DECLINED = "QUOTE_DECLINED"

    # Communication events
    SMS_SENT = "SMS_SENT"
    EMAIL_SENT = "EMAIL_SENT"

    # System events
    SYSTEM_ERROR = "SYSTEM_ERROR"
    INVARIANT_VIOLATED = "INVARIANT_VIOLATED"
    
    # Consensus events
    CONSENSUS_REQUESTED = "CONSENSUS_REQUESTED"
    KEY_SHARD_RELEASED = "KEY_SHARD_RELEASED"
    CONSENSUS_VETO = "CONSENSUS_VETO"
    CONSENSUS_ACHIEVED = "CONSENSUS_ACHIEVED"
    CONSENSUS_FAILED = "CONSENSUS_FAILED"
    SECURITY_LOCKDOWN = "SECURITY_LOCKDOWN"


class ICommand(BaseModel):
    """
    The Constitution: Every command MUST have these fields.
    """
    # Identity
    command_id: str = Field(default_factory=lambda: str(uuid4()))
    command_type: str = Field(..., min_length=1)
    user_id: int = Field(..., gt=0)
    company_id: int = Field(default=1, gt=0)

    # When
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Context
    session_id: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

    # Traceability
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    correlation_id: Optional[str] = None

    # Payload
    payload: Dict[str, Any] = Field(default_factory=dict)

    # Control flags
    idempotency_key: Optional[str] = None
    confirmation_token: Optional[str] = None
    dry_run: bool = False

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # V2 Configuration
    model_config = ConfigDict(validate_assignment=True)

    @field_validator('command_type')
    @classmethod
    def validate_command_type(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("command_type cannot be empty")
        return v.strip()


class IEvent(BaseModel):
    """
    The Constitution: Every event MUST have these fields.
    """
    # Identity
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: EventType = Field(...)

    # Causality
    caused_by_command_id: str = Field(..., min_length=1)
    caused_by_user_id: int = Field(..., gt=0)

    # When
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    valid_at: Optional[datetime] = None

    # Payload
    payload: Dict[str, Any] = Field(default_factory=dict)

    # Context
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    company_id: int = Field(default=1, gt=0)

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # V2 Configuration
    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)


class IInvariant(BaseModel):
    """
    The Constitution: Business rules that cannot be violated.
    """
    invariant_id: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    severity: Literal["ERROR", "WARNING"] = "ERROR"


class LedgerEntry(BaseModel):
    """
    Phase 2: Ledger of Truth - Immutable history entry
    """
    # Identity
    entry_id: int = Field(..., gt=0)
    sequence: int = Field(..., ge=0)

    # Causality
    command_id: str = Field(...)
    event_id: str = Field(...)

    # When
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    valid_at: Optional[datetime] = None

    # What changed
    entity_type: str = Field(...)
    entity_id: int = Field(...)
    operation: Literal["CREATE", "UPDATE", "DELETE"] = Field(...)

    # Data
    before_state: Optional[Dict[str, Any]] = None
    after_state: Dict[str, Any] = Field(...)

    # Tamper evidence
    prev_hash: Optional[str] = None
    current_hash: Optional[str] = None

    # Context
    company_id: int = Field(default=1, gt=0)
    user_id: int = Field(..., gt=0)

    # V2 Configuration
    model_config = ConfigDict(validate_assignment=True)


class CapabilityScope(str, Enum):
    """Fine-grained capabilities (Phase 0.3)"""
    CAN_CREATE_JOB = "can_create_job"
    CAN_UPDATE_JOB = "can_update_job"
    CAN_DELETE_JOB = "can_delete_job"
    CAN_SCHEDULE_JOB = "can_schedule_job"
    CAN_COMPLETE_JOB = "can_complete_job"
    CAN_CREATE_INVOICE = "can_create_invoice"
    CAN_SEND_INVOICE = "can_send_invoice"
    CAN_VOID_INVOICE = "can_void_invoice"
    CAN_RECORD_PAYMENT = "can_record_payment"
    CAN_REFUND_PAYMENT = "can_refund_payment"
    CAN_CREATE_CUSTOMER = "can_create_customer"
    CAN_UPDATE_CUSTOMER = "can_update_customer"
    CAN_DELETE_CUSTOMER = "can_delete_customer"
    CAN_SEND_SMS = "can_send_sms"
    CAN_SEND_EMAIL = "can_send_email"
    CAN_REPLAY_AUDIT = "can_replay_audit"
    CAN_VIEW_LEDGER = "can_view_ledger"
    CAN_MANAGE_USERS = "can_manage_users"


def create_command(command_type: str, user_id: int, payload: Dict[str, Any], company_id: int = 1, **kwargs) -> ICommand:
    return ICommand(command_type=command_type, user_id=user_id, payload=payload, company_id=company_id, **kwargs)

def create_event(event_type: EventType, caused_by_command_id: str, caused_by_user_id: int, payload: Dict[str, Any], entity_type: Optional[str] = None, entity_id: Optional[int] = None, **kwargs) -> IEvent:
    return IEvent(event_type=event_type, caused_by_command_id=caused_by_command_id, caused_by_user_id=caused_by_user_id, payload=payload, entity_type=entity_type, entity_id=entity_id, **kwargs)
