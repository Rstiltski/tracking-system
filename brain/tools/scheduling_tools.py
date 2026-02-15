"""
Scheduling Tools - Job scheduling, rescheduling, and resource management
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

@dataclass
class ScheduleJobInput(ToolInput):
    job_id: int
    job_date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    crew_ids: Optional[list[int]] = None

class ScheduleJobTool(Tool):
    """Schedule a job with date, time, and crew assignments"""

    @property
    def input_schema(self):
        return ScheduleJobInput

    def execute(self, input_data: ScheduleJobInput) -> ToolOutput:
        try:
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(success=False, error_code='TOOL_SCHEDULE_JOB_NOT_FOUND', error_message=f'Job with ID {input_data.job_id} not found')
            try:
                datetime.strptime(input_data.job_date, '%Y-%m-%d')
            except ValueError:
                return ToolOutput(success=False, error_code='TOOL_SCHEDULE_JOB_INVALID_DATE', error_message='Invalid date format. Use YYYY-MM-DD')
            conflicts = []
            if input_data.crew_ids:
                schedule_conflicts = db.find_schedule_conflicts(input_data.job_date)
                for crew_id in input_data.crew_ids:
                    for conflict in schedule_conflicts:
                        if conflict.get('user_id') == crew_id:
                            conflicts.append({'user_id': crew_id, 'username': conflict.get('username'), 'conflicting_jobs': conflict.get('jobs')})
            db.update_job_datetime(input_data.job_id, input_data.job_date, input_data.start_time, input_data.end_time, company_id=input_data.company_id)
            assigned_crew = []
            if input_data.crew_ids:
                for crew_id in input_data.crew_ids:
                    user = db.get_user_by_id(crew_id)
                    if not user:
                        continue
                    existing = db.get_job_assignment_by_job_and_user(input_data.job_id, crew_id)
                    if not existing:
                        assignment_id = db.assign_crew_to_job(input_data.job_id, crew_id, role='crew')
                        assigned_crew.append({'assignment_id': assignment_id, 'user_id': crew_id, 'username': user.get('username', '') if user else ''})
                    else:
                        assigned_crew.append({'assignment_id': existing.get('id', 0), 'user_id': crew_id, 'username': user.get('username', '') if user else '', 'already_assigned': True})
            result_data = {'job_id': input_data.job_id, 'job_date': input_data.job_date, 'start_time': input_data.start_time, 'end_time': input_data.end_time, 'assigned_crew': assigned_crew, 'message': 'Job scheduled successfully'}
            if conflicts:
                result_data['conflicts'] = conflicts
                result_data['message'] = 'Job scheduled with scheduling conflicts - crew members are double-booked'
            return ToolOutput(success=True, data=result_data)
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_SCHEDULE_JOB_ERROR', error_message=str(e))

@dataclass
class RescheduleJobInput(ToolInput):
    job_id: int
    new_date: str
    new_start_time: Optional[str] = None
    new_end_time: Optional[str] = None
    reason: Optional[str] = None

class RescheduleJobTool(Tool):
    """Reschedule a job to a new date/time"""

    @property
    def input_schema(self):
        return RescheduleJobInput

    def execute(self, input_data: RescheduleJobInput) -> ToolOutput:
        try:
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(success=False, error_code='TOOL_RESCHEDULE_JOB_NOT_FOUND', error_message=f'Job with ID {input_data.job_id} not found')
            try:
                datetime.strptime(input_data.new_date, '%Y-%m-%d')
            except ValueError:
                return ToolOutput(success=False, error_code='TOOL_RESCHEDULE_JOB_INVALID_DATE', error_message='Invalid date format. Use YYYY-MM-DD')
            old_date = job.get('job_date', '') if job else ''
            old_start_time = job.get('start_time', '') if job else ''
            old_end_time = job.get('end_time', '') if job else ''
            conflicts = []
            crew_assignments = db.list_job_assignments(input_data.job_id)
            if crew_assignments:
                schedule_conflicts = db.find_schedule_conflicts(input_data.new_date)
                for assignment in crew_assignments:
                    user_id = assignment.get('user_id')
                    for conflict in schedule_conflicts:
                        if conflict.get('user_id') == user_id:
                            conflicts.append({'user_id': user_id, 'username': conflict.get('username'), 'conflicting_jobs': conflict.get('jobs')})
            db.update_job_datetime(input_data.job_id, input_data.new_date, input_data.new_start_time, input_data.new_end_time, company_id=input_data.company_id)
            result_data = {'job_id': input_data.job_id, 'old_date': old_date, 'old_start_time': old_start_time, 'old_end_time': old_end_time, 'new_date': input_data.new_date, 'new_start_time': input_data.new_start_time, 'new_end_time': input_data.new_end_time, 'reason': input_data.reason, 'message': 'Job rescheduled successfully'}
            if conflicts:
                result_data['conflicts'] = conflicts
                result_data['message'] = 'Job rescheduled with scheduling conflicts - assigned crew members are double-booked'
            return ToolOutput(success=True, data=result_data)
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_RESCHEDULE_JOB_ERROR', error_message=str(e))

@dataclass
class CheckAvailabilityInput(ToolInput):
    date: str
    crew_ids: Optional[list[int]] = None
    resource_name: Optional[str] = None

class CheckAvailabilityTool(Tool):
    """Check crew and resource availability for a specific date"""

    @property
    def input_schema(self):
        return CheckAvailabilityInput

    def execute(self, input_data: CheckAvailabilityInput) -> ToolOutput:
        try:
            try:
                datetime.strptime(input_data.date, '%Y-%m-%d')
            except ValueError:
                return ToolOutput(success=False, error_code='TOOL_CHECK_AVAILABILITY_INVALID_DATE', error_message='Invalid date format. Use YYYY-MM-DD')
            result_data = {'date': input_data.date, 'crew_availability': [], 'resource_availability': {}, 'schedule_conflicts': []}
            if input_data.crew_ids:
                unavailable_crew = db.find_unavailable_crew_for_date(input_data.date)
                unavailable_ids = [c.get('user_id') for c in unavailable_crew]
                for crew_id in input_data.crew_ids:
                    user = db.get_user_by_id(crew_id)
                    if not user:
                        continue
                    is_available = crew_id not in unavailable_ids
                    crew_info = {'user_id': crew_id, 'username': user.get('username', '') if user else '', 'available': is_available}
                    if not is_available:
                        for unavail in unavailable_crew:
                            if unavail.get('user_id') == crew_id:
                                crew_info['unavailable_reason'] = unavail.get('reason', 'On leave')
                                break
                    result_data.get('crew_availability', 0).append(crew_info)
            conflicts = db.find_schedule_conflicts(input_data.date)
            result_data['schedule_conflicts'] = conflicts
            if input_data.resource_name:
                jobs = db.list_jobs_for_date(input_data.date, company_id=input_data.company_id)
                resource_busy = False
                busy_job_ids = []
                bookings = db.get_json_setting('equipment_bookings', [])
                for booking in bookings:
                    if booking.get('equipment', '').lower() == input_data.resource_name.lower() and booking.get('date_from') <= input_data.date <= booking.get('date_to', input_data.date):
                        resource_busy = True
                        if booking.get('job_id'):
                            busy_job_ids.append(booking.get('job_id'))
                result_data['resource_availability'] = {'resource_name': input_data.resource_name, 'available': not resource_busy, 'booked_for_jobs': busy_job_ids if resource_busy else []}
            return ToolOutput(success=True, data=result_data)
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_CHECK_AVAILABILITY_ERROR', error_message=str(e))

@dataclass
class BookResourceInput(ToolInput):
    resource_name: str
    job_id: int
    date_from: str
    date_to: str
    notes: Optional[str] = None

class BookResourceTool(Tool):
    """Book/reserve equipment or resource for a job"""

    @property
    def input_schema(self):
        return BookResourceInput

    def execute(self, input_data: BookResourceInput) -> ToolOutput:
        try:
            if not input_data.resource_name or not input_data.resource_name.strip():
                return ToolOutput(success=False, error_code='TOOL_BOOK_RESOURCE_EMPTY_NAME', error_message='Resource name cannot be empty')
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(success=False, error_code='TOOL_BOOK_RESOURCE_JOB_NOT_FOUND', error_message=f'Job with ID {input_data.job_id} not found')
            try:
                datetime.strptime(input_data.date_from, '%Y-%m-%d')
                datetime.strptime(input_data.date_to, '%Y-%m-%d')
            except ValueError:
                return ToolOutput(success=False, error_code='TOOL_BOOK_RESOURCE_INVALID_DATE', error_message='Invalid date format. Use YYYY-MM-DD')
            if input_data.date_from > input_data.date_to:
                return ToolOutput(success=False, error_code='TOOL_BOOK_RESOURCE_INVALID_DATE_RANGE', error_message='date_from must be before or equal to date_to')
            try:
                db.add_equipment_booking(input_data.resource_name, input_data.job_id, input_data.date_from, input_data.date_to, input_data.notes or '')
                return ToolOutput(success=True, data={'resource_name': input_data.resource_name, 'job_id': input_data.job_id, 'date_from': input_data.date_from, 'date_to': input_data.date_to, 'notes': input_data.notes, 'message': 'Resource booked successfully'})
            except ValueError as e:
                return ToolOutput(success=False, error_code='TOOL_BOOK_RESOURCE_CONFLICT', error_message=str(e))
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_BOOK_RESOURCE_ERROR', error_message=str(e))

@dataclass
class ReleaseResourceInput(ToolInput):
    resource_name: str
    job_id: int

class ReleaseResourceTool(Tool):
    """Release/free a booked equipment or resource"""

    @property
    def input_schema(self):
        return ReleaseResourceInput

    def execute(self, input_data: ReleaseResourceInput) -> ToolOutput:
        try:
            if not input_data.resource_name or not input_data.resource_name.strip():
                return ToolOutput(success=False, error_code='TOOL_RELEASE_RESOURCE_EMPTY_NAME', error_message='Resource name cannot be empty')
            bookings = db.get_json_setting('equipment_bookings', [])
            found = False
            new_bookings = []
            for booking in bookings:
                if booking.get('equipment', '').lower() == input_data.resource_name.lower() and booking.get('job_id') == input_data.job_id:
                    found = True
                    continue
                new_bookings.append(booking)
            if not found:
                return ToolOutput(success=False, error_code='TOOL_RELEASE_RESOURCE_NOT_FOUND', error_message=f"No booking found for resource '{input_data.resource_name}' on job {input_data.job_id}")
            db.set_json_setting('equipment_bookings', new_bookings)
            return ToolOutput(success=True, data={'resource_name': input_data.resource_name, 'job_id': input_data.job_id, 'message': 'Resource released successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_RELEASE_RESOURCE_ERROR', error_message=str(e))

@dataclass
class CreateRecurringJobInput(ToolInput):
    customer_id: int
    title: str
    frequency: str
    start_date: str
    description: Optional[str] = None
    end_date: Optional[str] = None
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    occurrences: Optional[int] = None

class CreateRecurringJobTool(Tool):
    """Create a series of recurring jobs based on a schedule pattern"""

    @property
    def input_schema(self):
        return CreateRecurringJobInput

    def execute(self, input_data: CreateRecurringJobInput) -> ToolOutput:
        try:
            customer = db.get_customer(input_data.customer_id, company_id=input_data.company_id)
            if not customer:
                return ToolOutput(success=False, error_code='TOOL_RECURRING_JOB_CUSTOMER_NOT_FOUND', error_message=f'Customer with ID {input_data.customer_id} not found')
            if not input_data.title or not input_data.title.strip():
                return ToolOutput(success=False, error_code='TOOL_RECURRING_JOB_EMPTY_TITLE', error_message='Job title cannot be empty')
            valid_frequencies = ['weekly', 'biweekly', 'monthly', 'quarterly']
            if input_data.frequency not in valid_frequencies:
                return ToolOutput(success=False, error_code='TOOL_RECURRING_JOB_INVALID_FREQUENCY', error_message=f"Frequency must be one of: {', '.join(valid_frequencies)}")
            try:
                start_dt = datetime.strptime(input_data.start_date, '%Y-%m-%d')
            except ValueError:
                return ToolOutput(success=False, error_code='TOOL_RECURRING_JOB_INVALID_START_DATE', error_message='Invalid start_date format. Use YYYY-MM-DD')
            end_dt = None
            if input_data.end_date:
                try:
                    end_dt = datetime.strptime(input_data.end_date, '%Y-%m-%d')
                except ValueError:
                    return ToolOutput(success=False, error_code='TOOL_RECURRING_JOB_INVALID_END_DATE', error_message='Invalid end_date format. Use YYYY-MM-DD')
                if end_dt < start_dt:
                    return ToolOutput(success=False, error_code='TOOL_RECURRING_JOB_INVALID_DATE_RANGE', error_message='end_date must be after start_date')
            job_dates = []
            current_dt = start_dt
            max_jobs = input_data.occurrences or 52
            from datetime import timedelta
            while len(job_dates) < max_jobs:
                job_dates.append(current_dt.strftime('%Y-%m-%d'))
                if input_data.frequency == 'weekly':
                    current_dt += timedelta(days=7)
                elif input_data.frequency == 'biweekly':
                    current_dt += timedelta(days=14)
                elif input_data.frequency == 'monthly':
                    month = current_dt.month + 1
                    year = current_dt.year
                    if month > 12:
                        month = 1
                        year += 1
                    day = min(current_dt.day, 28)
                    current_dt = datetime(year, month, day)
                elif input_data.frequency == 'quarterly':
                    month = current_dt.month + 3
                    year = current_dt.year
                    while month > 12:
                        month -= 12
                        year += 1
                    day = min(current_dt.day, 28)
                    current_dt = datetime(year, month, day)
                if end_dt and current_dt > end_dt:
                    break
            created_jobs = []
            for job_date in job_dates:
                job_id = db.add_job(customer_id=input_data.customer_id, title=input_data.title, description=input_data.description or '', job_date=job_date, status='draft', quoted_price=0.0, created_at=datetime.now().isoformat())
                created_jobs.append({'job_id': job_id, 'job_date': job_date})
            return ToolOutput(success=True, data={'customer_id': input_data.customer_id, 'frequency': input_data.frequency, 'start_date': input_data.start_date, 'end_date': input_data.end_date, 'jobs_created': len(created_jobs), 'created_jobs': created_jobs, 'message': f'Created {len(created_jobs)} recurring jobs successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_RECURRING_JOB_ERROR', error_message=str(e))
