"""
Bulk Operations Tools - Perform operations on multiple entities at once.

These tools allow efficient batch processing of common operations.
All bulk operations are HIGH or CRITICAL risk and require confirmation.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from brain.core.tool import Tool, ToolInput
from brain.core.result import ToolOutput
import db
from datetime import datetime as _datetime

@dataclass
class BulkJobStatusUpdateInput(ToolInput):
    """Input for bulk updating job statuses."""
    job_ids: List[int]
    new_status: str
    note: Optional[str] = None

class BulkJobStatusUpdateTool(Tool):
    """
    Update status for multiple jobs at once (HIGH risk - requires confirmation).
    
    Useful for:
    - Bulk completing jobs after a major project
    - Bulk cancelling jobs due to weather
    - Batch processing job state changes
    
    Example usage:
        - Complete 10 jobs after end of season
        - Cancel 5 jobs due to weather postponement
        - Move multiple quoted jobs to "Booked" status
    """

    @property
    def input_schema(self):
        return BulkJobStatusUpdateInput

    def execute(self, input_data: BulkJobStatusUpdateInput) -> ToolOutput:
        try:
            if not input_data.job_ids:
                return ToolOutput(success=False, error_code='BULK_NO_JOBS', error_message='No job IDs provided')
            if len(input_data.job_ids) > 100:
                return ToolOutput(success=False, error_code='BULK_TOO_MANY_JOBS', error_message=f'Too many jobs ({len(input_data.job_ids)}). Maximum 100 jobs per bulk operation.')
            updated_jobs = []
            failed_jobs = []
            for job_id in input_data.job_ids:
                try:
                    job = db.get_job(job_id, company_id=input_data.company_id)
                    if not job:
                        failed_jobs.append({'job_id': job_id, 'reason': 'Job not found'})
                        continue
                    db.update_job(job_id, status=input_data.new_status)
                    if input_data.note:
                        db.add_job_note(job_id, input_data.note)
                    updated_jobs.append(job_id)
                except Exception as e:
                    failed_jobs.append({'job_id': job_id, 'reason': str(e)})
            success = len(updated_jobs) > 0
            return ToolOutput(success=success, data={'updated_count': len(updated_jobs), 'failed_count': len(failed_jobs), 'updated_jobs': updated_jobs, 'failed_jobs': failed_jobs, 'new_status': input_data.new_status, 'message': f'Successfully updated {len(updated_jobs)} of {len(input_data.job_ids)} jobs'})
        except Exception as e:
            return ToolOutput(success=False, error_code='BULK_UPDATE_FAILED', error_message=str(e))

@dataclass
class BulkDeleteExpensesInput(ToolInput):
    """Input for bulk deleting expenses."""
    expense_ids: List[int]
    reason: str

class BulkDeleteExpensesTool(Tool):
    """
    Delete multiple expenses at once (CRITICAL risk - requires confirmation).
    
    Useful for:
    - Cleaning up duplicate expenses
    - Removing test data
    - Correcting bulk data entry errors
    
    Example usage:
        - Delete 20 duplicate expenses entered by mistake
        - Remove expenses from a cancelled job
    
    Note: Requires a reason for audit purposes.
    """

    @property
    def input_schema(self):
        return BulkDeleteExpensesInput

    def execute(self, input_data: BulkDeleteExpensesInput) -> ToolOutput:
        try:
            if not input_data.expense_ids:
                return ToolOutput(success=False, error_code='BULK_NO_EXPENSES', error_message='No expense IDs provided')
            if len(input_data.expense_ids) > 50:
                return ToolOutput(success=False, error_code='BULK_TOO_MANY_EXPENSES', error_message=f'Too many expenses ({len(input_data.expense_ids)}). Maximum 50 expenses per bulk operation.')
            if not input_data.reason or len(input_data.reason.strip()) < 10:
                return ToolOutput(success=False, error_code='BULK_REASON_REQUIRED', error_message='A detailed reason (minimum 10 characters) is required for bulk delete operations')
            deleted_expenses = []
            failed_expenses = []
            for expense_id in input_data.expense_ids:
                try:
                    expense = db.get_expense(expense_id)
                    if not expense:
                        failed_expenses.append({'expense_id': expense_id, 'reason': 'Expense not found'})
                        continue
                    db.delete_expense(expense_id)
                    deleted_expenses.append({'expense_id': expense_id, 'job_id': expense.get('job_id'), 'amount': expense.get('cost'), 'item': expense.get('item')})
                except Exception as e:
                    failed_expenses.append({'expense_id': expense_id, 'reason': str(e)})
            success = len(deleted_expenses) > 0
            total_amount = sum((e.get('amount', 0) for e in deleted_expenses))
            return ToolOutput(success=success, data={'deleted_count': len(deleted_expenses), 'failed_count': len(failed_expenses), 'total_amount_deleted': total_amount, 'deleted_expenses': deleted_expenses, 'failed_expenses': failed_expenses, 'reason': input_data.reason, 'message': f'Successfully deleted {len(deleted_expenses)} of {len(input_data.expense_ids)} expenses (£{total_amount:.2f} total)'})
        except Exception as e:
            return ToolOutput(success=False, error_code='BULK_DELETE_FAILED', error_message=str(e))

@dataclass
class BulkJobAssignmentInput(ToolInput):
    """Input for bulk assigning jobs to a crew member."""
    job_ids: List[int]
    crew_member_id: int
    role: Optional[str] = 'crew'

class BulkJobAssignmentTool(Tool):
    """
    Assign multiple jobs to a crew member at once (MEDIUM risk).
    
    Useful for:
    - Assigning a week's worth of jobs to a crew member
    - Bulk scheduling crew assignments
    - Team reorganization
    
    Example usage:
        - Assign 15 jobs to John for next week
        - Assign backup crew to multiple jobs
    """

    @property
    def input_schema(self):
        return BulkJobAssignmentInput

    def execute(self, input_data: BulkJobAssignmentInput) -> ToolOutput:
        try:
            if not input_data.job_ids:
                return ToolOutput(success=False, error_code='BULK_NO_JOBS', error_message='No job IDs provided')
            if len(input_data.job_ids) > 100:
                return ToolOutput(success=False, error_code='BULK_TOO_MANY_JOBS', error_message=f'Too many jobs ({len(input_data.job_ids)}). Maximum 100 jobs per bulk operation.')
            crew_member = db.get_user(input_data.crew_member_id)
            if not crew_member:
                return ToolOutput(success=False, error_code='CREW_NOT_FOUND', error_message=f'Crew member {input_data.crew_member_id} not found')
            assigned_jobs = []
            failed_jobs = []
            conflicts = []
            for job_id in input_data.job_ids:
                try:
                    job = db.get_job(job_id, company_id=input_data.company_id)
                    if not job:
                        failed_jobs.append({'job_id': job_id, 'reason': 'Job not found'})
                        continue
                    job_date = job.get('job_date', '') if job else ''
                    if job_date:
                        existing_assignments = db.list_user_assignments(input_data.crew_member_id, assigned_date=job_date)
                        if existing_assignments:
                            conflicts.append({'job_id': job_id, 'date': job_date, 'existing_jobs': [a.get('job_id') for a in existing_assignments]})
                    crew_role = input_data.role if input_data.role in ['crew', 'lead', 'supervisor'] else 'crew'
                    db.assign_crew_to_job(job_id, input_data.crew_member_id, role=crew_role)
                    assigned_jobs.append(job_id)
                except Exception as e:
                    failed_jobs.append({'job_id': job_id, 'reason': str(e)})
            success = len(assigned_jobs) > 0
            return ToolOutput(success=success, data={'assigned_count': len(assigned_jobs), 'failed_count': len(failed_jobs), 'conflict_count': len(conflicts), 'assigned_jobs': assigned_jobs, 'failed_jobs': failed_jobs, 'scheduling_conflicts': conflicts, 'crew_member': crew_member.get('username'), 'crew_member_id': input_data.crew_member_id, 'message': f"Successfully assigned {len(assigned_jobs)} of {len(input_data.job_ids)} jobs to {crew_member.get('username')}"})
        except Exception as e:
            return ToolOutput(success=False, error_code='BULK_ASSIGN_FAILED', error_message=str(e))

@dataclass
class BulkDeleteJobsInput(ToolInput):
    """Input for bulk deleting jobs."""
    job_ids: List[int]
    reason: str

class BulkDeleteJobsTool(Tool):
    """
    Delete multiple jobs at once (CRITICAL risk - requires confirmation).
    
    Useful for:
    - Cleaning up test or spam jobs
    - Removing jobs created by recurring job errors
    
    Note: Requires a reason for audit purposes.
    """

    @property
    def input_schema(self):
        return BulkDeleteJobsInput

    def execute(self, input_data: BulkDeleteJobsInput) -> ToolOutput:
        try:
            if not input_data.job_ids:
                return ToolOutput(success=False, error_code='BULK_NO_JOBS', error_message='No job IDs provided')
            if len(input_data.job_ids) > 50:
                return ToolOutput(success=False, error_code='BULK_TOO_MANY_JOBS', error_message=f'Too many jobs ({len(input_data.job_ids)}). Maximum 50 jobs per bulk operation.')
            if not input_data.reason or len(input_data.reason.strip()) < 10:
                return ToolOutput(success=False, error_code='BULK_REASON_REQUIRED', error_message='A detailed reason (minimum 10 characters) is required for bulk delete operations')
            deleted_jobs = []
            failed_jobs = []
            for job_id in input_data.job_ids:
                try:
                    job = db.get_job(job_id, company_id=input_data.company_id)
                    if not job:
                        failed_jobs.append({'job_id': job_id, 'reason': 'Job not found'})
                        continue
                    db.delete_job(job_id, company_id=input_data.company_id)
                    deleted_jobs.append(job_id)
                except Exception as e:
                    failed_jobs.append({'job_id': job_id, 'reason': str(e)})
            success = len(deleted_jobs) > 0
            return ToolOutput(success=success, data={
                'deleted_count': len(deleted_jobs),
                'failed_count': len(failed_jobs),
                'deleted_jobs': deleted_jobs,
                'failed_jobs': failed_jobs,
                'reason': input_data.reason,
                'message': f"Successfully soft deleted {len(deleted_jobs)} of {len(input_data.job_ids)} jobs"
            })
        except Exception as e:
            return ToolOutput(success=False, error_code='BULK_DELETE_FAILED', error_message=str(e))

@dataclass
class BulkDeleteCustomersInput(ToolInput):
    """Input for bulk deleting customers."""
    customer_ids: List[int]
    reason: str

class BulkDeleteCustomersTool(Tool):
    """
    Delete multiple customers at once (CRITICAL risk - requires confirmation).
    
    Useful for:
    - Cleaning up test or spam customers
    - Removing customers created by recurring errors
    
    Note: Requires a reason for audit purposes.
    """

    @property
    def input_schema(self):
        return BulkDeleteCustomersInput

    def execute(self, input_data: BulkDeleteCustomersInput) -> ToolOutput:
        try:
            if not input_data.customer_ids:
                return ToolOutput(success=False, error_code='BULK_NO_CUSTOMERS', error_message='No customer IDs provided')
            if len(input_data.customer_ids) > 50:
                return ToolOutput(success=False, error_code='BULK_TOO_MANY_CUSTOMERS', error_message=f'Too many customers ({len(input_data.customer_ids)}). Maximum 50 customers per bulk operation.')
            if not input_data.reason or len(input_data.reason.strip()) < 10:
                return ToolOutput(success=False, error_code='BULK_REASON_REQUIRED', error_message='A detailed reason (minimum 10 characters) is required for bulk delete operations')
            deleted_customers = []
            failed_customers = []
            for customer_id in input_data.customer_ids:
                try:
                    customer = db.get_customer(customer_id, company_id=input_data.company_id)
                    if not customer:
                        failed_customers.append({'customer_id': customer_id, 'reason': 'Customer not found'})
                        continue
                    db.delete_customer(customer_id, company_id=input_data.company_id)
                    deleted_customers.append(customer_id)
                except Exception as e:
                    failed_customers.append({'customer_id': customer_id, 'reason': str(e)})
            success = len(deleted_customers) > 0
            return ToolOutput(success=success, data={
                'deleted_count': len(deleted_customers),
                'failed_count': len(failed_customers),
                'deleted_customers': deleted_customers,
                'failed_customers': failed_customers,
                'reason': input_data.reason,
                'message': f"Successfully soft deleted {len(deleted_customers)} of {len(input_data.customer_ids)} customers"
            })
        except Exception as e:
            return ToolOutput(success=False, error_code='BULK_DELETE_FAILED', error_message=str(e))
