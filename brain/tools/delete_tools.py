"""
Delete Tools - Various deletion operations for system entities.

These tools handle deletion of templates, suppliers, roles, teams, and other system entities.
All delete operations are HIGH or CRITICAL risk and require confirmation.
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
class DeleteTemplateInput(ToolInput):
    """Input for deleting a template."""
    template_id: int

class DeleteTemplateTool(Tool):
    """Delete a template (CRITICAL risk - requires confirmation)."""

    @property
    def input_schema(self):
        return DeleteTemplateInput

    def execute(self, input_data: DeleteTemplateInput) -> ToolOutput:
        try:
            template = db.get_template(input_data.template_id)
            if not template:
                return ToolOutput(success=False, error_code='TOOL_DELETE_TEMPLATE_NOT_FOUND', error_message=f'Template {input_data.template_id} not found')
            db.delete_template(input_data.template_id)
            return ToolOutput(success=True, data={'template_id': input_data.template_id, 'message': 'Template deleted successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_DELETE_TEMPLATE_FAILED', error_message=str(e))

@dataclass
class DeleteSupplierInput(ToolInput):
    """Input for deleting a supplier."""
    supplier_id: int

class DeleteSupplierTool(Tool):
    """Delete a supplier (HIGH risk - requires confirmation)."""

    @property
    def input_schema(self):
        return DeleteSupplierInput

    def execute(self, input_data: DeleteSupplierInput) -> ToolOutput:
        try:
            supplier = db.get_supplier(input_data.supplier_id)
            if not supplier:
                return ToolOutput(success=False, error_code='TOOL_DELETE_SUPPLIER_NOT_FOUND', error_message=f'Supplier {input_data.supplier_id} not found')
            db.delete_supplier(input_data.supplier_id)
            return ToolOutput(success=True, data={'supplier_id': input_data.supplier_id, 'message': 'Supplier deleted successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_DELETE_SUPPLIER_FAILED', error_message=str(e))

@dataclass
class DeleteRoleInput(ToolInput):
    """Input for deleting a role."""
    role_name: str

class DeleteRoleTool(Tool):
    """Delete a role (CRITICAL risk - requires confirmation)."""

    @property
    def input_schema(self):
        return DeleteRoleInput

    def execute(self, input_data: DeleteRoleInput) -> ToolOutput:
        try:
            roles = db.list_roles()
            role_names = [r.get('name', 0) for r in roles]
            if input_data.role_name not in role_names:
                return ToolOutput(success=False, error_code='TOOL_DELETE_ROLE_NOT_FOUND', error_message=f"Role '{input_data.role_name}' not found")
            db.delete_role(input_data.role_name)
            return ToolOutput(success=True, data={'role_name': input_data.role_name, 'message': 'Role deleted successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_DELETE_ROLE_FAILED', error_message=str(e))

@dataclass
class DeleteTeamInput(ToolInput):
    """Input for deleting a team."""
    team_id: int

class DeleteTeamTool(Tool):
    """Delete a team (HIGH risk - requires confirmation)."""

    @property
    def input_schema(self):
        return DeleteTeamInput

    def execute(self, input_data: DeleteTeamInput) -> ToolOutput:
        try:
            team = db.get_team(input_data.team_id)
            if not team:
                return ToolOutput(success=False, error_code='TOOL_DELETE_TEAM_NOT_FOUND', error_message=f'Team {input_data.team_id} not found')
            db.delete_team(input_data.team_id)
            return ToolOutput(success=True, data={'team_id': input_data.team_id, 'message': 'Team deleted successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_DELETE_TEAM_FAILED', error_message=str(e))

@dataclass
class RemoveTeamMemberInput(ToolInput):
    """Input for removing a member from a team."""
    team_id: int
    user_id: int

class RemoveTeamMemberTool(Tool):
    """Remove a member from a team (MEDIUM risk)."""

    @property
    def input_schema(self):
        return RemoveTeamMemberInput

    def execute(self, input_data: RemoveTeamMemberInput) -> ToolOutput:
        try:
            team = db.get_team(input_data.team_id)
            if not team:
                return ToolOutput(success=False, error_code='TOOL_REMOVE_TEAM_MEMBER_TEAM_NOT_FOUND', error_message=f'Team {input_data.team_id} not found')
            db.remove_team_member(input_data.team_id, input_data.user_id)
            return ToolOutput(success=True, data={'team_id': input_data.team_id, 'user_id': input_data.user_id, 'message': 'Team member removed successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_REMOVE_TEAM_MEMBER_FAILED', error_message=str(e))

@dataclass
class DeleteRecurringJobInput(ToolInput):
    """Input for deleting a recurring job."""
    recurring_id: int

class DeleteRecurringJobTool(Tool):
    """Delete a recurring job (HIGH risk - requires confirmation)."""

    @property
    def input_schema(self):
        return DeleteRecurringJobInput

    def execute(self, input_data: DeleteRecurringJobInput) -> ToolOutput:
        try:
            recurring = db.get_recurring_job(input_data.recurring_id)
            if not recurring:
                return ToolOutput(success=False, error_code='TOOL_DELETE_RECURRING_JOB_NOT_FOUND', error_message=f'Recurring job {input_data.recurring_id} not found')
            db.delete_recurring_job(input_data.recurring_id)
            return ToolOutput(success=True, data={'recurring_id': input_data.recurring_id, 'message': 'Recurring job deleted successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_DELETE_RECURRING_JOB_FAILED', error_message=str(e))

@dataclass
class DeleteJobMaterialInput(ToolInput):
    """Input for deleting a job material."""
    job_material_id: int

class DeleteJobMaterialTool(Tool):
    """Delete a job material (MEDIUM risk)."""

    @property
    def input_schema(self):
        return DeleteJobMaterialInput

    def execute(self, input_data: DeleteJobMaterialInput) -> ToolOutput:
        try:
            db.delete_job_material(input_data.job_material_id)
            return ToolOutput(success=True, data={'job_material_id': input_data.job_material_id, 'message': 'Job material deleted successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_DELETE_JOB_MATERIAL_FAILED', error_message=str(e))

@dataclass
class DeleteQuoteItemInput(ToolInput):
    """Input for deleting a quote item."""
    quote_item_id: int

class DeleteQuoteItemTool(Tool):
    """Delete a quote item (LOW risk)."""

    @property
    def input_schema(self):
        return DeleteQuoteItemInput

    def execute(self, input_data: DeleteQuoteItemInput) -> ToolOutput:
        try:
            db.delete_quote_item(input_data.quote_item_id)
            return ToolOutput(success=True, data={'quote_item_id': input_data.quote_item_id, 'message': 'Quote item deleted successfully'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_DELETE_QUOTE_ITEM_FAILED', error_message=str(e))