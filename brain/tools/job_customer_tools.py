"""
Job & Customer Management Tools - Phase 4B

Tools for managing jobs and customers to support UI integration:
- UpdateJobStatus: Change job status
- AddJobNote: Add notes/comments to jobs
- DeleteJob: Delete jobs (CRITICAL)
- UpdateCustomer: Update customer details
- AddCustomerNote: Add notes to customers
- DeleteCustomer: Delete customers (CRITICAL)
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from dataclasses import dataclass
from typing import Optional
from brain.core.tool import Tool, ToolInput
from brain.core.result import ToolOutput
from brain.tools.decorators import register_tool
import db


# ============================================================================
# UpdateJobStatus - Change job status
# ============================================================================

@dataclass
class UpdateJobStatusInput(ToolInput):
    job_id: int
    new_status: str
    updated_by: Optional[int] = None


@register_tool(name="UpdateJobStatus", risk="Medium", category="job")
class UpdateJobStatusTool(Tool):
    """Update job status with audit trail"""

    @property
    def input_schema(self):
        return UpdateJobStatusInput

    def execute(self, input_data: UpdateJobStatusInput) -> ToolOutput:
        try:
            db.brain_update_job_status(
                job_id=input_data.job_id,
                new_status=input_data.new_status,
                updated_by=input_data.updated_by
            )

            return ToolOutput(
                success=True,
                data={
                    "job_id": input_data.job_id,
                    "new_status": input_data.new_status,
                    "message": f"Job status updated to {input_data.new_status}"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_UPDATE_JOB_STATUS_ERROR",
                error_message=str(e)
            )


# ============================================================================
# AddJobNote - Add note/comment to a job
# ============================================================================

@dataclass
class AddJobNoteInput(ToolInput):
    job_id: int
    note: str
    note_type: str = "general"  # general, technical, customer_request, etc.
    created_by: Optional[int] = None


@register_tool(name="AddJobNote", risk="Low", category="job")
class AddJobNoteTool(Tool):
    """Add a note or comment to a job"""

    @property
    def input_schema(self):
        return AddJobNoteInput

    def execute(self, input_data: AddJobNoteInput) -> ToolOutput:
        try:
            note_id = db.brain_add_job_note(
                job_id=input_data.job_id,
                note=input_data.note,
                note_type=input_data.note_type,
                created_by=input_data.created_by
            )

            return ToolOutput(
                success=True,
                data={
                    "note_id": note_id,
                    "job_id": input_data.job_id,
                    "message": "Note added to job successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_ADD_JOB_NOTE_ERROR",
                error_message=str(e)
            )


# ============================================================================
# DeleteJob - Delete a job (CRITICAL)
# ============================================================================

@dataclass
class DeleteJobInput(ToolInput):
    job_id: int
    reason: str  # Required for CRITICAL operations


@register_tool(name="DeleteJob", risk="High", category="job")
class DeleteJobTool(Tool):
    """Delete a job and all related records (CRITICAL - requires confirmation)"""

    @property
    def input_schema(self):
        return DeleteJobInput

    def execute(self, input_data: DeleteJobInput) -> ToolOutput:
        try:
            db.brain_delete_job(job_id=input_data.job_id)

            return ToolOutput(
                success=True,
                data={
                    "job_id": input_data.job_id,
                    "message": f"Job deleted: {input_data.reason}"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_DELETE_JOB_ERROR",
                error_message=str(e)
            )


# ============================================================================
# UpdateCustomer - Update customer details
# ============================================================================

@dataclass
class UpdateCustomerInput(ToolInput):
    customer_id: int
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None


@register_tool(name="UpdateCustomer", risk="Medium", category="customer")
class UpdateCustomerTool(Tool):
    """Update customer details"""

    @property
    def input_schema(self):
        return UpdateCustomerInput

    def execute(self, input_data: UpdateCustomerInput) -> ToolOutput:
        try:
            db.brain_update_customer(
                customer_id=input_data.customer_id,
                name=input_data.name,
                phone=input_data.phone,
                email=input_data.email,
                address=input_data.address,
                postcode=input_data.postcode
            )

            return ToolOutput(
                success=True,
                data={
                    "customer_id": input_data.customer_id,
                    "message": "Customer updated successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_UPDATE_CUSTOMER_ERROR",
                error_message=str(e)
            )


# ============================================================================
# AddCustomerNote - Add note to a customer
# ============================================================================

@dataclass
class AddCustomerNoteInput(ToolInput):
    customer_id: int
    note: str
    note_type: str = "general"
    is_internal: bool = True
    created_by: Optional[int] = None


@register_tool(name="AddCustomerNote", risk="Low", category="customer")
class AddCustomerNoteTool(Tool):
    """Add a note to a customer record"""

    @property
    def input_schema(self):
        return AddCustomerNoteInput

    def execute(self, input_data: AddCustomerNoteInput) -> ToolOutput:
        try:
            note_id = db.brain_add_customer_note(
                customer_id=input_data.customer_id,
                note=input_data.note,
                note_type=input_data.note_type,
                is_internal=input_data.is_internal,
                created_by=input_data.created_by
            )

            return ToolOutput(
                success=True,
                data={
                    "note_id": note_id,
                    "customer_id": input_data.customer_id,
                    "message": "Note added to customer successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_ADD_CUSTOMER_NOTE_ERROR",
                error_message=str(e)
            )


# ============================================================================
# DeleteCustomer - Delete a customer (CRITICAL)
# ============================================================================

@dataclass
class DeleteCustomerInput(ToolInput):
    customer_id: int
    reason: str  # Required for CRITICAL operations


@register_tool(name="DeleteCustomer", risk="High", category="customer")
class DeleteCustomerTool(Tool):
    """Delete a customer and related records (CRITICAL - requires confirmation)"""

    @property
    def input_schema(self):
        return DeleteCustomerInput

    def execute(self, input_data: DeleteCustomerInput) -> ToolOutput:
        try:
            # Should validate no active jobs before deleting
            # For now, just delete (foreign key constraints will prevent if jobs exist)
            db.brain_delete_customer(customer_id=input_data.customer_id)

            return ToolOutput(
                success=True,
                data={
                    "customer_id": input_data.customer_id,
                    "message": f"Customer deleted: {input_data.reason}"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_DELETE_CUSTOMER_ERROR",
                error_message=str(e)
            )
