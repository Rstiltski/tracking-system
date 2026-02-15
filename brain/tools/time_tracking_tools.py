"""
Time tracking and timesheet tools for the Brain system.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from brain.core.tool import Tool, ToolInput
from brain.core.result import ToolOutput
import db


# ===== CLOCK IN =====

@dataclass
class ClockInInput(ToolInput):
    """Input for clocking in to start work."""
    job_id: int
    user_id: int
    started_at: Optional[str] = None  # ISO format datetime, defaults to now


class ClockInTool(Tool):
    """Start a timer for a job (clock in)."""

    @property
    def input_schema(self):
        return ClockInInput

    def execute(self, input_data: ClockInInput) -> ToolOutput:
        """
        Start a timer for a job.
        
        Returns:
            ToolOutput with timer_id in data
        """
        try:
            # Validate job exists
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(
                    success=False,
                    error_code="TOOL_CLOCKIN_JOB_NOT_FOUND",
                    error_message=f"Job {input_data.job_id} not found"
                )

            # Check if user already has an active timer
            active_timer = db.get_active_timer()
            if active_timer and active_timer.get('user_id') == input_data.user_id:
                return ToolOutput(
                    success=False,
                    error_code="TOOL_CLOCKIN_ALREADY_ACTIVE",
                    error_message=f"User already has an active timer (timer_id: {active_timer.get('id')})"
                )

            # Start timer
            timer_id = db.start_timer(
                job_id=input_data.job_id,
                started_at=input_data.started_at
            )

            return ToolOutput(
                success=True,
                data={
                    "timer_id": timer_id,
                    "job_id": input_data.job_id,
                    "user_id": input_data.user_id,
                    "started_at": input_data.started_at or datetime.now().isoformat()
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_CLOCKIN_FAILED",
                error_message=str(e)
            )


# ===== CLOCK OUT =====

@dataclass
class ClockOutInput(ToolInput):
    """Input for clocking out to end work."""
    timer_id: Optional[int] = None  # If None, stops the currently active timer
    ended_at: Optional[str] = None  # ISO format datetime, defaults to now
    notes: Optional[str] = ""


class ClockOutTool(Tool):
    """Stop a timer for a job (clock out)."""

    @property
    def input_schema(self):
        return ClockOutInput

    def execute(self, input_data: ClockOutInput) -> ToolOutput:
        """
        Stop a timer for a job.
        
        Returns:
            ToolOutput with work log details
        """
        try:
            # If no timer_id provided, get active timer
            if input_data.timer_id is None:
                active_timer = db.get_active_timer()
                if not active_timer:
                    return ToolOutput(
                        success=False,
                        error_code="TOOL_CLOCKOUT_NO_ACTIVE_TIMER",
                        error_message="No active timer found to stop"
                    )
                timer_id = active_timer.get('id')
            else:
                timer_id = input_data.timer_id

            # Stop timer
            work_log_id = db.stop_timer(
                timer_id=timer_id,
                ended_at=input_data.ended_at,
                notes=input_data.notes or ""
            )

            return ToolOutput(
                success=True,
                data={
                    "timer_id": timer_id,
                    "work_log_id": work_log_id,
                    "ended_at": input_data.ended_at or datetime.now().isoformat(),
                    "notes": input_data.notes
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_CLOCKOUT_FAILED",
                error_message=str(e)
            )


# ===== ADD WORK LOG =====

@dataclass
class AddWorkLogInput(ToolInput):
    """Input for adding a manual work log entry."""
    job_id: int
    user_id: int
    work_date: str  # YYYY-MM-DD
    hours: float
    notes: str
    time_type: Optional[str] = "labour"  # labour, travel, etc.
    clock_in_time: Optional[str] = None  # HH:MM format
    clock_out_time: Optional[str] = None  # HH:MM format
    break_duration: Optional[float] = 0.0  # Hours


class AddWorkLogTool(Tool):
    """Add a manual work log entry (for non-timer based work)."""

    @property
    def input_schema(self):
        return AddWorkLogInput

    def execute(self, input_data: AddWorkLogInput) -> ToolOutput:
        """
        Add a manual work log entry.
        
        Returns:
            ToolOutput with log_id in data
        """
        try:
            # Validate job exists
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(
                    success=False,
                    error_code="TOOL_ADD_WORKLOG_JOB_NOT_FOUND",
                    error_message=f"Job {input_data.job_id} not found"
                )

            # Validate hours
            if input_data.hours <= 0:
                return ToolOutput(
                    success=False,
                    error_code="TOOL_ADD_WORKLOG_INVALID_HOURS",
                    error_message="Hours must be greater than 0"
                )

            # Add work log
            log_id = db.add_work_log(
                job_id=input_data.job_id,
                work_date=input_data.work_date,
                hours=input_data.hours,
                notes=input_data.notes,
                user_id=input_data.user_id,
                time_type=input_data.time_type,
                clock_in_time=input_data.clock_in_time,
                clock_out_time=input_data.clock_out_time,
                break_duration=input_data.break_duration
            )

            return ToolOutput(
                success=True,
                data={
                    "log_id": log_id,
                    "job_id": input_data.job_id,
                    "user_id": input_data.user_id,
                    "hours": input_data.hours,
                    "work_date": input_data.work_date
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_ADD_WORKLOG_FAILED",
                error_message=str(e)
            )


# ===== UPDATE WORK LOG =====

@dataclass
class UpdateWorkLogInput(ToolInput):
    """Input for updating a work log entry."""
    log_id: int
    hours: Optional[float] = None
    notes: Optional[str] = None
    work_date: Optional[str] = None


class UpdateWorkLogTool(Tool):
    """Update an existing work log entry."""

    @property
    def input_schema(self):
        return UpdateWorkLogInput

    def execute(self, input_data: UpdateWorkLogInput) -> ToolOutput:
        """
        Update a work log entry.

        Returns:
            ToolOutput with updated log details
        """
        try:
            from database.queries.work_logs import update_work_log, get_work_log

            # Check if at least one field is being updated
            if input_data.hours is None and input_data.notes is None and input_data.work_date is None:
                return ToolOutput(
                    success=False,
                    error_code="TOOL_UPDATE_WORKLOG_NO_FIELDS",
                    error_message="No fields provided to update"
                )

            # Update the work log
            success = update_work_log(
                log_id=input_data.log_id,
                hours=input_data.hours,
                notes=input_data.notes,
                work_date=input_data.work_date
            )

            if not success:
                return ToolOutput(
                    success=False,
                    error_code="TOOL_UPDATE_WORKLOG_NOT_FOUND",
                    error_message=f"Work log {input_data.log_id} not found"
                )

            # Get the updated work log to return
            updated_log = get_work_log(input_data.log_id)

            return ToolOutput(
                success=True,
                data={
                    "log_id": input_data.log_id,
                    "hours": updated_log.get('hours') if updated_log else input_data.hours,
                    "notes": updated_log.get('notes') if updated_log else input_data.notes,
                    "work_date": updated_log.get('work_date') if updated_log else input_data.work_date
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_UPDATE_WORKLOG_FAILED",
                error_message=str(e)
            )


# ===== APPROVE TIMESHEET =====

@dataclass
class ApproveTimesheetInput(ToolInput):
    """Input for approving a user's timesheet."""
    user_id: int
    week_ending: str  # YYYY-MM-DD
    approved_by: int


class ApproveTimesheetTool(Tool):
    """Approve a user's timesheet for a week."""

    @property
    def input_schema(self):
        return ApproveTimesheetInput

    def execute(self, input_data: ApproveTimesheetInput) -> ToolOutput:
        """
        Approve a user's timesheet.
        
        Returns:
            ToolOutput with approval status
        """
        try:
            # Approve timesheet
            db.approve_timesheet(
                user_id=input_data.user_id,
                week_ending=input_data.week_ending,
                approved_by=input_data.approved_by
            )

            return ToolOutput(
                success=True,
                data={
                    "user_id": input_data.user_id,
                    "week_ending": input_data.week_ending,
                    "approved_by": input_data.approved_by,
                    "approved_at": datetime.now().isoformat()
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_APPROVE_TIMESHEET_FAILED",
                error_message=str(e)
            )


# ===== REJECT TIMESHEET =====

@dataclass
class RejectTimesheetInput(ToolInput):
    """Input for rejecting a user's timesheet."""
    user_id: int
    week_ending: str  # YYYY-MM-DD
    rejected_by: int
    reason: Optional[str] = None


class RejectTimesheetTool(Tool):
    """Reject a user's timesheet for a week."""

    @property
    def input_schema(self):
        return RejectTimesheetInput

    def execute(self, input_data: RejectTimesheetInput) -> ToolOutput:
        """
        Reject a user's timesheet.
        
        Returns:
            ToolOutput with rejection status
        """
        try:
            # Reject timesheet
            db.reject_timesheet(
                user_id=input_data.user_id,
                week_ending=input_data.week_ending,
                approved_by=input_data.rejected_by
            )

            return ToolOutput(
                success=True,
                data={
                    "user_id": input_data.user_id,
                    "week_ending": input_data.week_ending,
                    "rejected_by": input_data.rejected_by,
                    "rejected_at": datetime.now().isoformat(),
                    "reason": input_data.reason
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_REJECT_TIMESHEET_FAILED",
                error_message=str(e)
            )
