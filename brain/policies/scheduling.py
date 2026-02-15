"""
Scheduling Policy - Prevent scheduling conflicts and resource over-allocation
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/02_policy_packs.md
- LLM_AGENT_QUICKSTART.md
"""
from datetime import datetime
from brain.core.command_event import CommandEvent
from brain.core.result import PolicyResult
import db

class SchedulingPolicy:
    """
    Scheduling Policy enforces scheduling constraints:
    - Crew availability checks
    - Crew conflict detection (double-booking prevention)
    - Daily capacity limits (warnings)

    This policy helps prevent:
    - Assigning crew who are unavailable
    - Double-booking crew on the same date
    - Overloading available capacity
    """

    def check(self, event: CommandEvent) -> PolicyResult:
        """
        Run all scheduling checks.

        Returns:
            PolicyResult - ALLOW, DENY, or WARN
        """
        if event.command_type not in ['ScheduleJob', 'RescheduleJob', 'AssignCrew']:
            return PolicyResult.allow()
        result = self._check_crew_conflicts(event)
        if result.is_denied:
            return result
        result = self._check_daily_capacity(event)
        if result.status == 'WARN':
            print(f'⚠️  Scheduling Warning: {result.message}')
        return PolicyResult.allow()

    def _check_crew_conflicts(self, event: CommandEvent) -> PolicyResult:
        """
        SCH-002: Ensure crew is not double-booked.

        Checks if crew members are already assigned to other jobs on the same date.
        """
        job_id = event.params.get('job_id')
        job_date = event.params.get('job_date')
        crew_ids = event.params.get('crew_ids', [])
        if not job_date or not crew_ids:
            return PolicyResult.allow()
        for crew_id in crew_ids:
            conflicts = db.list_user_assignments(crew_id, job_date)
            conflicts = [j for j in conflicts if j.get('job_id') != job_id]
            if conflicts:
                user = db.get_user(crew_id)
                crew_name = user.get('username', f'User {crew_id}') if user else f'User {crew_id}' if user else f'User {crew_id}'
                conflict_jobs = ', '.join([f"Job #{j.get('job_id')}" for j in conflicts[:3]])
                if len(conflicts) > 3:
                    conflict_jobs += f' and {len(conflicts) - 3} more'
                return PolicyResult.deny(f'{crew_name} is already assigned to {conflict_jobs} on {job_date}', error_code='SCH_CREW_CONFLICT')
        return PolicyResult.allow()

    def _check_daily_capacity(self, event: CommandEvent) -> PolicyResult:
        """
        SCH-004: Warn if daily capacity is low.

        This is a soft check (warning only) to alert users about capacity constraints.
        """
        job_date = event.params.get('job_date')
        job_id = event.params.get('job_id')
        estimated_hours = event.params.get('estimated_hours', 4.0)
        if not job_date:
            return PolicyResult.allow()
        try:
            capacity = db.calculate_daily_capacity(job_date, exclude_job_id=job_id)
            available_hours = capacity.get('available_hours', 0)
            if available_hours < estimated_hours:
                return PolicyResult.warn(f'Low capacity on {job_date}: {available_hours:.1f} hours available, {estimated_hours:.1f} hours required')
        except Exception:
            pass
        return PolicyResult.allow()