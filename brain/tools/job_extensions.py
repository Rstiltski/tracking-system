"""
Additional Job Tools - Extensions for job-related operations

These tools provide additional job management functionality beyond the core
job creation and updates, including sign-offs, variations, measurements, 
status updates, and materials.
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


# ===== ADD JOB SIGN OFF =====

@dataclass
class AddJobSignOffInput(ToolInput):
    """Input for adding a job sign-off."""
    job_id: int
    signed_by: str
    signature_data: Optional[str] = None  # Base64 encoded signature image
    sign_off_date: Optional[str] = None  # ISO date
    notes: Optional[str] = ""
    customer_id: Optional[int] = None


class AddJobSignOffTool(Tool):
    """Add a sign-off to a completed job."""

    @property
    def input_schema(self):
        return AddJobSignOffInput

    def execute(self, input_data: AddJobSignOffInput) -> ToolOutput:
        try:
            # Validate job exists
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(
                    success=False,
                    error_code="JOB_NOT_FOUND",
                    error_message=f"Job {input_data.job_id} not found"
                )

            # Use current date if not provided
            sign_off_date = input_data.sign_off_date or datetime.now().strftime("%Y-%m-%d")

            # Add sign-off
            sign_off_id = db.add_job_sign_off(
                job_id=input_data.job_id,
                signed_by=input_data.signed_by,
                signature_data=input_data.signature_data,
                sign_off_date=sign_off_date,
                notes=input_data.notes or "",
                customer_id=input_data.customer_id
            )

            return ToolOutput(
                success=True,
                data={
                    "sign_off_id": sign_off_id,
                    "job_id": input_data.job_id,
                    "signed_by": input_data.signed_by,
                    "sign_off_date": sign_off_date
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="SIGN_OFF_FAILED",
                error_message=f"Failed to add job sign-off: {str(e)}"
            )


# ===== ADD JOB VARIATION =====

@dataclass
class AddJobVariationInput(ToolInput):
    """Input for adding a job variation."""
    job_id: int
    description: str
    amount: float
    variation_date: Optional[str] = None  # ISO date
    approved_by: Optional[str] = None
    notes: Optional[str] = ""


class AddJobVariationTool(Tool):
    """Add a variation (change order) to a job."""

    @property
    def input_schema(self):
        return AddJobVariationInput

    def execute(self, input_data: AddJobVariationInput) -> ToolOutput:
        try:
            # Validate job exists
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(
                    success=False,
                    error_code="JOB_NOT_FOUND",
                    error_message=f"Job {input_data.job_id} not found"
                )

            # Validate amount
            if input_data.amount == 0:
                return ToolOutput(
                    success=False,
                    error_code="INVALID_AMOUNT",
                    error_message="Variation amount cannot be zero"
                )

            # Use current date if not provided
            variation_date = input_data.variation_date or datetime.now().strftime("%Y-%m-%d")

            # Add variation
            variation_id = db.add_job_variation(
                job_id=input_data.job_id,
                description=input_data.description,
                amount=input_data.amount,
                variation_date=variation_date,
                approved_by=input_data.approved_by,
                notes=input_data.notes or ""
            )

            return ToolOutput(
                success=True,
                data={
                    "variation_id": variation_id,
                    "job_id": input_data.job_id,
                    "description": input_data.description,
                    "amount": input_data.amount
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="VARIATION_FAILED",
                error_message=f"Failed to add job variation: {str(e)}"
            )


# ===== ADD JOB MEASUREMENT =====

@dataclass
class AddJobMeasurementInput(ToolInput):
    """Input for adding a job measurement."""
    job_id: int
    measurement_type: str  # e.g., "area", "length", "volume"
    value: float
    unit: str  # e.g., "sqft", "ft", "cuyd"
    notes: Optional[str] = ""
    measured_by: Optional[int] = None
    measured_date: Optional[str] = None


class AddJobMeasurementTool(Tool):
    """Add a measurement to a job."""

    @property
    def input_schema(self):
        return AddJobMeasurementInput

    def execute(self, input_data: AddJobMeasurementInput) -> ToolOutput:
        try:
            # Validate job exists
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(
                    success=False,
                    error_code="JOB_NOT_FOUND",
                    error_message=f"Job {input_data.job_id} not found"
                )

            # Validate value
            if input_data.value <= 0:
                return ToolOutput(
                    success=False,
                    error_code="INVALID_VALUE",
                    error_message="Measurement value must be positive"
                )

            # Use current date if not provided
            measured_date = input_data.measured_date or datetime.now().strftime("%Y-%m-%d")

            # Add measurement
            measurement_id = db.add_job_measurement(
                job_id=input_data.job_id,
                measurement_type=input_data.measurement_type,
                value=input_data.value,
                unit=input_data.unit,
                notes=input_data.notes or "",
                measured_by=input_data.measured_by,
                measured_date=measured_date
            )

            return ToolOutput(
                success=True,
                data={
                    "measurement_id": measurement_id,
                    "job_id": input_data.job_id,
                    "measurement_type": input_data.measurement_type,
                    "value": input_data.value,
                    "unit": input_data.unit
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="MEASUREMENT_FAILED",
                error_message=f"Failed to add job measurement: {str(e)}"
            )


# ===== ADD JOB STATUS UPDATE =====

@dataclass
class AddJobStatusUpdateInput(ToolInput):
    """Input for adding a job status update/note."""
    job_id: int
    update_text: str
    update_type: Optional[str] = "status"  # status, note, issue, milestone
    user_id: Optional[int] = None
    is_customer_visible: bool = False


class AddJobStatusUpdateTool(Tool):
    """Add a status update or note to a job."""

    @property
    def input_schema(self):
        return AddJobStatusUpdateInput

    def execute(self, input_data: AddJobStatusUpdateInput) -> ToolOutput:
        try:
            # Validate job exists
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(
                    success=False,
                    error_code="JOB_NOT_FOUND",
                    error_message=f"Job {input_data.job_id} not found"
                )

            # Validate update text
            if not input_data.update_text or not input_data.update_text.strip():
                return ToolOutput(
                    success=False,
                    error_code="EMPTY_UPDATE",
                    error_message="Status update text cannot be empty"
                )

            # Add status update
            update_id = db.add_job_status_update(
                job_id=input_data.job_id,
                update_text=input_data.update_text.strip(),
                update_type=input_data.update_type,
                user_id=input_data.user_id,
                is_customer_visible=input_data.is_customer_visible
            )

            return ToolOutput(
                success=True,
                data={
                    "update_id": update_id,
                    "job_id": input_data.job_id,
                    "update_text": input_data.update_text.strip(),
                    "update_type": input_data.update_type
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="STATUS_UPDATE_FAILED",
                error_message=f"Failed to add job status update: {str(e)}"
            )


# ===== ADD JOB MATERIAL =====

@dataclass
class AddJobMaterialInput(ToolInput):
    """Input for adding a material to a job."""
    job_id: int
    material_name: str
    quantity: float
    unit_cost: float
    material_id: Optional[int] = None  # Link to materials library
    unit: Optional[str] = "ea"
    notes: Optional[str] = ""
    supplier: Optional[str] = ""


class AddJobMaterialTool(Tool):
    """Add a material to a job."""

    @property
    def input_schema(self):
        return AddJobMaterialInput

    def execute(self, input_data: AddJobMaterialInput) -> ToolOutput:
        try:
            # Validate job exists
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(
                    success=False,
                    error_code="JOB_NOT_FOUND",
                    error_message=f"Job {input_data.job_id} not found"
                )

            # Validate quantity
            if input_data.quantity <= 0:
                return ToolOutput(
                    success=False,
                    error_code="INVALID_QUANTITY",
                    error_message="Material quantity must be positive"
                )

            # Validate cost
            if input_data.unit_cost < 0:
                return ToolOutput(
                    success=False,
                    error_code="INVALID_COST",
                    error_message="Material cost cannot be negative"
                )

            # Add material to job
            job_material_id = db.add_job_material(
                job_id=input_data.job_id,
                material_name=input_data.material_name,
                quantity=input_data.quantity,
                unit_cost=input_data.unit_cost,
                material_id=input_data.material_id,
                unit=input_data.unit,
                notes=input_data.notes or "",
                supplier=input_data.supplier or ""
            )

            total_cost = input_data.quantity * input_data.unit_cost

            return ToolOutput(
                success=True,
                data={
                    "job_material_id": job_material_id,
                    "job_id": input_data.job_id,
                    "material_name": input_data.material_name,
                    "quantity": input_data.quantity,
                    "unit_cost": input_data.unit_cost,
                    "total_cost": total_cost
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_MATERIAL_FAILED",
                error_message=f"Failed to add material to job: {str(e)}"
            )
