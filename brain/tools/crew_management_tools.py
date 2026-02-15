"""
Crew Management Tools - User and crew assignment operations
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
class AssignCrewInput(ToolInput):
    job_id: int
    user_id: int
    role: Optional[str] = 'crew'
    assigned_date: Optional[str] = None
    pay_override: Optional[float] = None
    notes: Optional[str] = None

class AssignCrewTool(Tool):
    """Assign a crew member to a job"""

    @property
    def input_schema(self):
        return AssignCrewInput

    def execute(self, input_data: AssignCrewInput) -> ToolOutput:
        try:
            existing = db.get_job_assignment_by_job_and_user(input_data.job_id, input_data.user_id)
            if existing:
                return ToolOutput(success=True, data={'assignment_id': existing.get('id', 0), 'job_id': input_data.job_id, 'user_id': input_data.user_id, 'role': existing.get('role', 0), 'message': 'Crew member already assigned to this job'})
            assignment_id = db.assign_crew_to_job(input_data.job_id, input_data.user_id, input_data.role, input_data.assigned_date, input_data.pay_override, input_data.notes)
            return ToolOutput(success=True, data={'assignment_id': assignment_id, 'job_id': input_data.job_id, 'user_id': input_data.user_id, 'role': input_data.role, 'assigned_date': input_data.assigned_date, 'pay_override': input_data.pay_override, 'notes': input_data.notes, 'message': 'Crew member assigned successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_ASSIGN_CREW_ERROR', error_message=str(e))

@dataclass
class UnassignCrewInput(ToolInput):
    job_id: int
    user_id: int

class UnassignCrewTool(Tool):
    """Remove a crew member from a job"""

    @property
    def input_schema(self):
        return UnassignCrewInput

    def execute(self, input_data: UnassignCrewInput) -> ToolOutput:
        try:
            db.unassign_crew_from_job(input_data.job_id, input_data.user_id)
            return ToolOutput(success=True, data={'job_id': input_data.job_id, 'user_id': input_data.user_id, 'message': 'Crew member unassigned successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_UNASSIGN_CREW_ERROR', error_message=str(e))

@dataclass(kw_only=True)
class CreateUserInput(ToolInput):
    username: str
    password: str
    role: str
    email: str
    company_id: int

class CreateUserTool(Tool):
    """Create a new user account"""

    @property
    def input_schema(self):
        return CreateUserInput

    def execute(self, input_data: CreateUserInput) -> ToolOutput:
        try:
            user_id = db.brain_create_user(username=input_data.username, password=input_data.password, role=input_data.role, email=input_data.email, must_change_password=False, company_id=input_data.company_id)
            return ToolOutput(success=True, data={'user_id': user_id, 'username': input_data.username, 'role': input_data.role, 'message': 'User created successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_CREATE_USER_ERROR', error_message=str(e))

@dataclass
class UpdateUserInput(ToolInput):
    user_id: int
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    day_rate: Optional[float] = None
    half_day_rate: Optional[float] = None
    subscription_tier: Optional[str] = None

class UpdateUserTool(Tool):
    """Update user account details"""

    @property
    def input_schema(self):
        return UpdateUserInput

    def execute(self, input_data: UpdateUserInput) -> ToolOutput:
        try:
            update_fields = {}
            if input_data.email is not None:
                update_fields['email'] = input_data.email
            if input_data.full_name is not None:
                update_fields['full_name'] = input_data.full_name
            if input_data.phone is not None:
                update_fields['phone'] = input_data.phone
            if input_data.role is not None:
                update_fields['role'] = input_data.role
            if input_data.day_rate is not None:
                update_fields['day_rate'] = input_data.day_rate
            if input_data.half_day_rate is not None:
                update_fields['half_day_rate'] = input_data.half_day_rate
            if input_data.subscription_tier is not None:
                update_fields['subscription_tier'] = input_data.subscription_tier
            db.update_user(user_id=input_data.user_id, **update_fields)
            return ToolOutput(success=True, data={'user_id': input_data.user_id, 'message': 'User updated successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_UPDATE_USER_ERROR', error_message=str(e))

@dataclass
class DeleteUserInput(ToolInput):
    user_id: int
    reason: str

class DeleteUserTool(Tool):
    """Delete a user account (CRITICAL - requires confirmation)"""

    @property
    def input_schema(self):
        return DeleteUserInput

    def execute(self, input_data: DeleteUserInput) -> ToolOutput:
        try:
            db.delete_user(input_data.user_id)
            return ToolOutput(success=True, data={'user_id': input_data.user_id, 'message': f'User deleted: {input_data.reason}'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_DELETE_USER_ERROR', error_message=str(e))

@dataclass
class ActivateUserInput(ToolInput):
    user_id: int

class ActivateUserTool(Tool):
    """Activate a deactivated user account"""

    @property
    def input_schema(self):
        return ActivateUserInput

    def execute(self, input_data: ActivateUserInput) -> ToolOutput:
        try:
            db.activate_user(input_data.user_id)
            return ToolOutput(success=True, data={'user_id': input_data.user_id, 'message': 'User activated successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_ACTIVATE_USER_ERROR', error_message=str(e))

@dataclass
class DeactivateUserInput(ToolInput):
    user_id: int
    reason: Optional[str] = None

class DeactivateUserTool(Tool):
    """Deactivate a user account temporarily"""

    @property
    def input_schema(self):
        return DeactivateUserInput

    def execute(self, input_data: DeactivateUserInput) -> ToolOutput:
        try:
            db.deactivate_user(input_data.user_id)
            return ToolOutput(success=True, data={'user_id': input_data.user_id, 'message': f"User deactivated{(': ' + input_data.reason if input_data.reason else '')}"})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_DEACTIVATE_USER_ERROR', error_message=str(e))

@dataclass
class SetUserRoleInput(ToolInput):
    user_id: int
    new_role: str

class SetUserRoleTool(Tool):
    """Change a user's role (HIGH risk - requires confirmation)"""

    @property
    def input_schema(self):
        return SetUserRoleInput

    def execute(self, input_data: SetUserRoleInput) -> ToolOutput:
        try:
            user = db.get_user(input_data.user_id)
            old_role = user.get('role', 'Unknown') if user else 'Unknown'
            db.set_user_role(input_data.user_id, input_data.new_role)
            return ToolOutput(success=True, data={'user_id': input_data.user_id, 'old_role': old_role, 'new_role': input_data.new_role, 'message': f'User role changed from {old_role} to {input_data.new_role}'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_SET_USER_ROLE_ERROR', error_message=str(e))
