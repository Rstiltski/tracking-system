"""
Recurring Job Tools - Tools for managing recurring/subscription jobs

These tools handle recurring job setup, updates, and skip date management.
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
from datetime import datetime


# ===== ADD RECURRING JOB =====

@dataclass
class AddRecurringInput(ToolInput):
    """Input for adding a recurring job."""
    template_job_id: int
    frequency: str  # daily, weekly, biweekly, monthly, quarterly, yearly
    next_date: str  # ISO date - next scheduled occurrence
    every_n: int = 1  # e.g., every 2 weeks
    end_date: Optional[str] = None  # ISO date - when to stop recurring
    day_of_week: Optional[int] = None  # 0=Monday, 6=Sunday
    day_of_month: Optional[int] = None  # 1-31
    notes: Optional[str] = ""


class AddRecurringTool(Tool):
    """Create a recurring job schedule."""

    @property
    def input_schema(self):
        return AddRecurringInput

    def execute(self, input_data: AddRecurringInput) -> ToolOutput:
        try:
            # Validate template job exists
            job = db.get_job(input_data.template_job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(
                    success=False,
                    error_code="JOB_NOT_FOUND",
                    error_message=f"Template job {input_data.template_job_id} not found"
                )

            # Validate frequency
            valid_frequencies = ["daily", "weekly", "biweekly", "monthly", "quarterly", "yearly"]
            if input_data.frequency.lower() not in valid_frequencies:
                return ToolOutput(
                    success=False,
                    error_code="INVALID_FREQUENCY",
                    error_message=f"Frequency must be one of: {', '.join(valid_frequencies)}"
                )

            # Validate every_n
            if input_data.every_n < 1:
                return ToolOutput(
                    success=False,
                    error_code="INVALID_INTERVAL",
                    error_message="Interval (every_n) must be at least 1"
                )

            # Add recurring job
            recurring_id = db.add_recurring(
                template_job_id=input_data.template_job_id,
                freq=input_data.frequency,
                every_n=input_data.every_n,
                next_date=input_data.next_date,
                end_date=input_data.end_date,
                day_of_week=input_data.day_of_week,
                day_of_month=input_data.day_of_month,
                notes=input_data.notes or ""
            )

            return ToolOutput(
                success=True,
                data={
                    "recurring_id": recurring_id,
                    "template_job_id": input_data.template_job_id,
                    "frequency": input_data.frequency,
                    "next_date": input_data.next_date
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_RECURRING_FAILED",
                error_message=f"Failed to create recurring job: {str(e)}"
            )


# ===== UPDATE RECURRING JOB =====

@dataclass
class UpdateRecurringJobInput(ToolInput):
    """Input for updating a recurring job."""
    recurring_id: int
    frequency: Optional[str] = None
    every_n: Optional[int] = None
    next_date: Optional[str] = None
    end_date: Optional[str] = None
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class UpdateRecurringJobTool(Tool):
    """Update a recurring job schedule."""

    @property
    def input_schema(self):
        return UpdateRecurringJobInput

    def execute(self, input_data: UpdateRecurringJobInput) -> ToolOutput:
        try:
            # Validate recurring job exists
            recurring = db.get_recurring_job(input_data.recurring_id)
            if not recurring:
                return ToolOutput(
                    success=False,
                    error_code="RECURRING_NOT_FOUND",
                    error_message=f"Recurring job {input_data.recurring_id} not found"
                )

            # Build update kwargs
            updates = {}
            if input_data.frequency is not None:
                updates["frequency"] = input_data.frequency
            if input_data.every_n is not None:
                updates["every_n"] = input_data.every_n
            if input_data.next_date is not None:
                updates["next_date"] = input_data.next_date
            if input_data.end_date is not None:
                updates["end_date"] = input_data.end_date
            if input_data.day_of_week is not None:
                updates["day_of_week"] = input_data.day_of_week
            if input_data.day_of_month is not None:
                updates["day_of_month"] = input_data.day_of_month
            if input_data.is_active is not None:
                updates["is_active"] = input_data.is_active
            if input_data.notes is not None:
                updates["notes"] = input_data.notes

            # Update recurring job
            db.update_recurring_job(input_data.recurring_id, **updates)

            return ToolOutput(
                success=True,
                data={
                    "recurring_id": input_data.recurring_id,
                    "updates": updates
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="UPDATE_RECURRING_FAILED",
                error_message=f"Failed to update recurring job: {str(e)}"
            )


# ===== ADD RECURRING SKIP DATE =====

@dataclass
class AddRecurringSkipDateInput(ToolInput):
    """Input for adding a skip date to a recurring job."""
    recurring_id: int
    skip_date: str  # ISO date
    reason: Optional[str] = ""


class AddRecurringSkipDateTool(Tool):
    """Add a skip date to a recurring job (e.g., for holidays)."""

    @property
    def input_schema(self):
        return AddRecurringSkipDateInput

    def execute(self, input_data: AddRecurringSkipDateInput) -> ToolOutput:
        try:
            # Validate recurring job exists
            recurring = db.get_recurring_job(input_data.recurring_id)
            if not recurring:
                return ToolOutput(
                    success=False,
                    error_code="RECURRING_NOT_FOUND",
                    error_message=f"Recurring job {input_data.recurring_id} not found"
                )

            # Add skip date
            skip_id = db.add_recurring_skip_date(
                recurring_id=input_data.recurring_id,
                skip_date=input_data.skip_date,
                reason=input_data.reason or ""
            )

            return ToolOutput(
                success=True,
                data={
                    "skip_id": skip_id,
                    "recurring_id": input_data.recurring_id,
                    "skip_date": input_data.skip_date,
                    "reason": input_data.reason or ""
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_SKIP_DATE_FAILED",
                error_message=f"Failed to add skip date: {str(e)}"
            )


# ===== DELETE RECURRING SKIP DATE =====

@dataclass
class DeleteRecurringSkipDateInput(ToolInput):
    """Input for deleting a recurring skip date."""
    skip_id: int


class DeleteRecurringSkipDateTool(Tool):
    """Delete a skip date from a recurring job."""

    @property
    def input_schema(self):
        return DeleteRecurringSkipDateInput

    def execute(self, input_data: DeleteRecurringSkipDateInput) -> ToolOutput:
        try:
            # Delete skip date
            db.delete_recurring_skip_date(input_data.skip_id)

            return ToolOutput(
                success=True,
                data={
                    "skip_id": input_data.skip_id
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="DELETE_SKIP_DATE_FAILED",
                error_message=f"Failed to delete skip date: {str(e)}"
            )
