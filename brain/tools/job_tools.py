"""
Job-related tools
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date
from brain.core.tool import Tool, ToolInput
from brain.core.result import ToolOutput
from brain.tools.decorators import register_tool
import db


# ===== CREATE JOB =====

@dataclass
class CreateJobInput(ToolInput):
    customer_id: int
    title: str
    description: Optional[str] = None
    job_type: str = "landscaping"
    job_date: Optional[str] = None  # ISO format string
    priority: str = "Medium"
    estimated_hours: Optional[float] = None


@register_tool(name="CreateJob", risk="Medium", category="job")
class CreateJobTool(Tool):
    """Create a new job record"""

    @property
    def input_schema(self):
        return CreateJobInput

    def execute(self, input_data: CreateJobInput) -> ToolOutput:
        try:
            # Call Brain wrapper function
            job_id = db.brain_create_job(
                customer_id=input_data.customer_id,
                title=input_data.title,
                description=input_data.description or "",
                job_date=input_data.job_date or "",
                job_type=input_data.job_type,
                company_id=input_data.company_id
            )

            return ToolOutput(
                success=True,
                data={"job_id": job_id, "status": "DRAFT"}
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_JOB_CREATE_FAILED",
                error_message=str(e)
            )


# ===== UPDATE JOB =====

@dataclass
class UpdateJobInput(ToolInput):
    job_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    job_type: Optional[str] = None
    priority: Optional[str] = None
    estimated_hours: Optional[float] = None
    quoted_price: Optional[float] = None
    status: Optional[str] = None
    job_date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


@register_tool(name="UpdateJob", risk="Medium", category="job")
class UpdateJobTool(Tool):
    """Update job details"""

    @property
    def input_schema(self):
        return UpdateJobInput

    def execute(self, input_data: UpdateJobInput) -> ToolOutput:
        try:
            # Get current job
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(
                    success=False,
                    error_code="TOOL_JOB_UPDATE_NOT_FOUND",
                    error_message=f"Job {input_data.job_id} not found"
                )

            # Build update dict
            updates = {}
            updated_fields = []

            if input_data.title is not None:
                updates["title"] = input_data.title
                updated_fields.append("title")

            if input_data.description is not None:
                updates["description"] = input_data.description
                updated_fields.append("description")

            if input_data.job_type is not None:
                updates["job_type"] = input_data.job_type
                updated_fields.append("job_type")

            if input_data.priority is not None:
                updates["priority"] = input_data.priority
                updated_fields.append("priority")

            if input_data.quoted_price is not None:
                updates["quoted_price"] = input_data.quoted_price
                updated_fields.append("quoted_price")

            if input_data.status is not None:
                updates["status"] = input_data.status
                updated_fields.append("status")

            if input_data.job_date is not None:
                updates["job_date"] = input_data.job_date
                updated_fields.append("job_date")

            if input_data.start_time is not None:
                updates["start_time"] = input_data.start_time
                updated_fields.append("start_time")

            if input_data.end_time is not None:
                updates["end_time"] = input_data.end_time
                updated_fields.append("end_time")

            if input_data.estimated_hours is not None:
                updates["estimated_duration_hours"] = input_data.estimated_hours
                updated_fields.append("estimated_hours")

            # Update job
            if updates:
                db.update_job_full(input_data.job_id, company_id=input_data.company_id, **updates)

            return ToolOutput(
                success=True,
                data={
                    "job_id": input_data.job_id,
                    "updated_fields": updated_fields
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_JOB_UPDATE_FAILED",
                error_message=str(e)
            )


# ===== GET JOB =====

@dataclass
class GetJobInput(ToolInput):
    job_id: int


@register_tool(name="GetJob", risk="Low", category="job")
class GetJobTool(Tool):
    """Retrieve job details"""

    @property
    def input_schema(self):
        return GetJobInput

    def execute(self, input_data: GetJobInput) -> ToolOutput:
        try:
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)

            if not job:
                return ToolOutput(
                    success=False,
                    error_code="TOOL_JOB_GET_NOT_FOUND",
                    error_message=f"Job {input_data.job_id} not found"
                )

            return ToolOutput(
                success=True,
                data=dict(job)
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_JOB_GET_FAILED",
                error_message=str(e)
            )
