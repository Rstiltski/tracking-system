"""
Result objects returned by the Brain and Tools
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime


@dataclass
class ToolOutput:
    """Result of a tool execution"""

    success: bool
    data: Any = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def failed(self) -> bool:
        """Check if tool execution failed"""
        return not self.success

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "error_code": self.error_code,
            "error_message": self.error_message,
        }


@dataclass
class BrainResult:
    """Result of a Brain command execution"""

    # Status
    success: bool
    status: str  # SUCCESS, FAILED, DUPLICATE, DENIED

    # Data
    data: Any = None

    # Error information
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None

    # Execution details
    command_id: Optional[str] = None
    command_type: Optional[str] = None
    executed_at: datetime = field(default_factory=datetime.utcnow)
    duration_ms: Optional[int] = None

    # Execution plan
    plan: Optional[list] = None
    tool_results: Optional[list] = None

    # State transition (if applicable)
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    state_before: Optional[str] = None
    state_after: Optional[str] = None

    # Confirmation (for high-risk commands)
    requires_confirmation: bool = False
    confirmation_token: Optional[str] = None
    confirmation_expires_at: Optional[float] = None
    dry_run_preview: Optional[dict] = None  # Phase 3: Contains diff preview
    
    # Sentient System Phase 2: Learning Mode & Confidence Gate
    requires_nuclear_codes: bool = False  # True if Nuclear Codes Modal required
    requires_socratic: bool = False  # True if Socratic Chat Widget required
    confirmation_phrase: Optional[str] = None  # Phrase to type for Nuclear Codes
    confidence_score: Optional[float] = None  # AI confidence (0.0 to 1.0)
    learning_mode: Optional[bool] = None  # User's Learning Mode setting

    @property
    def failed(self) -> bool:
        """Check if command execution failed"""
        return not self.success

    @classmethod
    def ok(cls, data: Any = None, message: str = None, **kwargs) -> "BrainResult":
        """
        Create a successful result.

        Usage:
            return BrainResult.ok(data={"job_id": 42}, message="Job created")
        """
        return cls(
            success=True,
            status="SUCCESS",
            data=data,
            error_message=message,
            **kwargs
        )

    @classmethod
    def fail(cls, error_message: str, error_code: str = None, data: Any = None, **kwargs) -> "BrainResult":
        """
        Create a failed result.

        Usage:
            return BrainResult.fail(error_message="Job not found", error_code="JOB_NOT_FOUND")
        """
        return cls(
            success=False,
            status="FAILED",
            error_message=error_message,
            error_code=error_code,
            data=data,
            **kwargs
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "success": self.success,
            "status": self.status,
            "data": self.data,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "command_id": self.command_id,
            "command_type": self.command_type,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "duration_ms": self.duration_ms,
            "plan": self.plan,
            "tool_results": self.tool_results,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "state_before": self.state_before,
            "state_after": self.state_after,
            "requires_confirmation": self.requires_confirmation,
            "confirmation_token": self.confirmation_token,
            "confirmation_expires_at": self.confirmation_expires_at,
            "dry_run_preview": self.dry_run_preview,
            # Sentient System Phase 2 fields
            "requires_nuclear_codes": self.requires_nuclear_codes,
            "requires_socratic": self.requires_socratic,
            "confirmation_phrase": self.confirmation_phrase,
            "confidence_score": self.confidence_score,
            "learning_mode": self.learning_mode,
        }


@dataclass
class PolicyResult:
    """Result of a policy check"""

    status: str  # ALLOW, DENY, WARN, DUPLICATE
    message: Optional[str] = None
    error_code: Optional[str] = None
    cached_result: Optional[Any] = None

    @staticmethod
    def allow() -> "PolicyResult":
        """Create an ALLOW result"""
        return PolicyResult(status="ALLOW")

    @staticmethod
    def deny(message: str, error_code: str = None) -> "PolicyResult":
        """Create a DENY result"""
        return PolicyResult(status="DENY", message=message, error_code=error_code)

    @staticmethod
    def warn(message: str) -> "PolicyResult":
        """Create a WARN result"""
        return PolicyResult(status="WARN", message=message)

    @staticmethod
    def duplicate(cached_result: Any) -> "PolicyResult":
        """Create a DUPLICATE result (idempotent command)"""
        return PolicyResult(status="DUPLICATE", cached_result=cached_result)

    @property
    def is_allowed(self) -> bool:
        """Check if policy allows execution"""
        return self.status in ["ALLOW", "WARN"]

    @property
    def is_denied(self) -> bool:
        """Check if policy denies execution"""
        return self.status == "DENY"

    @property
    def is_duplicate(self) -> bool:
        """Check if command is duplicate"""
        return self.status == "DUPLICATE"
