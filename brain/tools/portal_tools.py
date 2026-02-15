"""
Portal Tools - Customer portal access management

These tools manage customer access to job portals:
- Generate secure portal tokens for customer access
- Revoke portal access when needed
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from dataclasses import dataclass
from typing import Optional
from brain.core.tool import Tool, ToolInput
from brain.core.result import ToolOutput
import db


@dataclass
class GeneratePortalTokenInput(ToolInput):
    """Input for generating a portal token."""
    job_id: int
    expires_days: Optional[int] = None  # None = no expiry


class GeneratePortalTokenTool(Tool):
    """
    Generate a secure portal token for customer access to a job.
    
    Generates a unique, secure token that allows customers to view
    job details, photos, invoices, and status updates without logging in.
    Tokens can optionally expire after a specified number of days.
    
    Risk Tier: MEDIUM (2) - Creates public access link
    Idempotent: Yes - Returns existing active token if present
    """
    
    name = "GeneratePortalToken"
    
    @property
    def input_schema(self):
        return GeneratePortalTokenInput
    
    def execute(self, input_data: GeneratePortalTokenInput) -> ToolOutput:
        """Generate or retrieve portal token for a job."""
        try:
            # Check if job exists
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(
                    success=False,
                    error_code="JOB_NOT_FOUND",
                    error_message=f"Job {input_data.job_id} not found"
                )
            
            # Generate token (returns existing if present)
            token = db.generate_job_portal_token(
                job_id=input_data.job_id,
                expires_days=input_data.expires_days
            )
            
            # Calculate expiry date if specified
            expires_at = None
            if input_data.expires_days:
                from datetime import datetime, timedelta
                expires_dt = datetime.now() + timedelta(days=input_data.expires_days)
                expires_at = expires_dt.isoformat(timespec="seconds")
            
            return ToolOutput(
                success=True,
                data={
                    "token": token,
                    "job_id": input_data.job_id,
                    "expires_at": expires_at
                }
            )
        
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_PORTAL_TOKEN_GENERATE_FAILED",
                error_message=str(e)
            )


@dataclass
class RevokePortalTokenInput(ToolInput):
    """Input for revoking a portal token."""
    token: str
    reason: Optional[str] = None  # Optional reason for audit trail


class RevokePortalTokenTool(Tool):
    """
    Revoke (deactivate) a portal token to remove customer access.
    
    Permanently disables a portal token, preventing further access
    to the job portal. This is useful when:
    - Job is cancelled or deleted
    - Customer access should be restricted
    - Token was shared inappropriately
    - New token needs to be issued
    
    Risk Tier: MEDIUM (2) - Removes access but doesn't delete data
    Idempotent: Yes - Safe to revoke already-revoked token
    """
    
    name = "RevokePortalToken"
    
    @property
    def input_schema(self):
        return RevokePortalTokenInput
    
    def execute(self, input_data: RevokePortalTokenInput) -> ToolOutput:
        """Revoke a portal token."""
        try:
            # Simply deactivate the token (idempotent - won't fail if doesn't exist)
            # We don't need to check if token exists first since deactivation is safe
            db.deactivate_portal_token(input_data.token)
            
            return ToolOutput(
                success=True,
                data={
                    "token": input_data.token,
                    "revoked": True,
                    "reason": input_data.reason
                }
            )
        
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_PORTAL_TOKEN_REVOKE_FAILED",
                error_message=str(e)
            )
