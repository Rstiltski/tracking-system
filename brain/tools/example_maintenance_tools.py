"""
Example: Creating a New Feature with AI-Native Architecture
============================================================

This example demonstrates how easy it is to add a new feature using the
AI-Native architecture. The AI only needs to create ONE file to add a
complete new feature - no need to edit brain.py or write UI code!

Example Feature: Vehicle Maintenance Tracking
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


# ===== CREATE MAINTENANCE RECORD =====

@dataclass
class CreateMaintenanceInput(ToolInput):
    vehicle_id: int
    maintenance_type: str
    description: str
    cost: float
    maintenance_date: str  # ISO format
    next_due_date: Optional[str] = None
    performed_by: Optional[str] = None


@register_tool(name="CreateMaintenance", risk="Low", category="vehicle")
class CreateMaintenanceTool(Tool):
    """Create a new vehicle maintenance record"""

    @property
    def input_schema(self):
        return CreateMaintenanceInput

    def execute(self, input_data: CreateMaintenanceInput) -> ToolOutput:
        try:
            # In a real implementation, this would call a database function
            # For this example, we'll simulate it
            
            # Simulated database call
            maintenance_id = 999  # Would come from database
            
            return ToolOutput(
                success=True,
                data={
                    "maintenance_id": maintenance_id,
                    "vehicle_id": input_data.vehicle_id,
                    "status": "recorded"
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_MAINTENANCE_CREATE_FAILED",
                error_message=str(e)
            )


# ===== SCHEDULE MAINTENANCE =====

@dataclass
class ScheduleMaintenanceInput(ToolInput):
    vehicle_id: int
    maintenance_type: str
    scheduled_date: str  # ISO format
    notes: Optional[str] = None


@register_tool(name="ScheduleMaintenance", risk="Low", category="vehicle")
class ScheduleMaintenanceTool(Tool):
    """Schedule upcoming vehicle maintenance"""

    @property
    def input_schema(self):
        return ScheduleMaintenanceInput

    def execute(self, input_data: ScheduleMaintenanceInput) -> ToolOutput:
        try:
            # Simulated database call
            schedule_id = 888
            
            return ToolOutput(
                success=True,
                data={
                    "schedule_id": schedule_id,
                    "vehicle_id": input_data.vehicle_id,
                    "scheduled_date": input_data.scheduled_date
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_MAINTENANCE_SCHEDULE_FAILED",
                error_message=str(e)
            )


# ===== THAT'S IT! =====
# 
# With AI-Native architecture:
# 1. The tools are automatically discovered and registered (thanks to @register_tool)
# 2. The UI can be generated automatically with: BrainForm("CreateMaintenance").render()
# 3. No need to edit brain.py or any other central files
# 
# The AI created ONE file and the feature is complete!
#
# To use in the UI (views/vehicles_maintenance.py):
#
#   from components.brain_ui import brain_form
#
#   def render():
#       st.title("Vehicle Maintenance")
#       
#       # That's it! The form is auto-generated
#       brain_form("CreateMaintenance", title="Record Maintenance")
#
#       # Or with more control:
#       from components.brain_ui import BrainForm
#       
#       form = BrainForm(
#           command="CreateMaintenance",
#           title="Record Vehicle Maintenance",
#           success_message="Maintenance recorded successfully!",
#           on_success=lambda result: st.balloons()
#       )
#       form.render()
