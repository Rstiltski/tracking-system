"""
Miscellaneous Tools - Additional operations not fitting other categories

These tools provide functionality for photo approvals, vehicles, templates,
compliance documents, requests, and other miscellaneous operations.
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


# ===== PHOTO APPROVAL TOOLS =====

@dataclass
class AddPhotoApprovalInput(ToolInput):
    """Input for adding a photo approval."""
    photo_id: int
    customer_id: int
    approval_status: str  # approved, rejected, pending
    notes: Optional[str] = ""


class AddPhotoApprovalTool(Tool):
    """Add a photo approval record."""

    @property
    def input_schema(self):
        return AddPhotoApprovalInput

    def execute(self, input_data: AddPhotoApprovalInput) -> ToolOutput:
        try:
            # Validate status
            valid_statuses = ["approved", "rejected", "pending"]
            if input_data.approval_status not in valid_statuses:
                return ToolOutput(
                    success=False,
                    error_code="INVALID_STATUS",
                    error_message=f"Status must be one of: {', '.join(valid_statuses)}"
                )

            # Add photo approval
            approval_id = db.add_photo_approval(
                photo_id=input_data.photo_id,
                customer_id=input_data.customer_id,
                approval_status=input_data.approval_status,
                notes=input_data.notes or ""
            )

            return ToolOutput(
                success=True,
                data={
                    "approval_id": approval_id,
                    "photo_id": input_data.photo_id,
                    "approval_status": input_data.approval_status
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_APPROVAL_FAILED",
                error_message=f"Failed to add photo approval: {str(e)}"
            )


@dataclass
class UpdatePhotoApprovalStatusInput(ToolInput):
    """Input for updating photo approval status."""
    approval_id: int
    approval_status: str  # approved, rejected, pending
    notes: Optional[str] = None


class UpdatePhotoApprovalStatusTool(Tool):
    """Update the status of a photo approval."""

    @property
    def input_schema(self):
        return UpdatePhotoApprovalStatusInput

    def execute(self, input_data: UpdatePhotoApprovalStatusInput) -> ToolOutput:
        try:
            # Validate status
            valid_statuses = ["approved", "rejected", "pending"]
            if input_data.approval_status not in valid_statuses:
                return ToolOutput(
                    success=False,
                    error_code="INVALID_STATUS",
                    error_message=f"Status must be one of: {', '.join(valid_statuses)}"
                )

            # Update photo approval status
            db.update_photo_approval_status(
                approval_id=input_data.approval_id,
                approval_status=input_data.approval_status,
                notes=input_data.notes
            )

            return ToolOutput(
                success=True,
                data={
                    "approval_id": input_data.approval_id,
                    "approval_status": input_data.approval_status
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="UPDATE_APPROVAL_FAILED",
                error_message=f"Failed to update photo approval status: {str(e)}"
            )


# ===== VEHICLE/EQUIPMENT TOOLS =====

@dataclass
class AddVehicleInput(ToolInput):
    """Input for adding a vehicle."""
    name: str
    vehicle_type: str  # truck, trailer, equipment
    license_plate: Optional[str] = ""
    vin: Optional[str] = ""
    year: Optional[int] = None
    make: Optional[str] = ""
    model: Optional[str] = ""
    status: Optional[str] = "active"
    notes: Optional[str] = ""


class AddVehicleTool(Tool):
    """Add a vehicle to the fleet."""

    @property
    def input_schema(self):
        return AddVehicleInput

    def execute(self, input_data: AddVehicleInput) -> ToolOutput:
        try:
            # Validate name
            if not input_data.name or not input_data.name.strip():
                return ToolOutput(
                    success=False,
                    error_code="EMPTY_NAME",
                    error_message="Vehicle name cannot be empty"
                )

            # Add vehicle
            vehicle_id = db.add_vehicle(
                name=input_data.name,
                vehicle_type=input_data.vehicle_type,
                license_plate=input_data.license_plate or "",
                vin=input_data.vin or "",
                year=input_data.year,
                make=input_data.make or "",
                model=input_data.model or "",
                status=input_data.status or "active",
                notes=input_data.notes or ""
            )

            return ToolOutput(
                success=True,
                data={
                    "vehicle_id": vehicle_id,
                    "name": input_data.name,
                    "vehicle_type": input_data.vehicle_type
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_VEHICLE_FAILED",
                error_message=f"Failed to add vehicle: {str(e)}"
            )


@dataclass
class UpdateVehicleInput(ToolInput):
    """Input for updating a vehicle."""
    vehicle_id: int
    name: Optional[str] = None
    vehicle_type: Optional[str] = None
    license_plate: Optional[str] = None
    vin: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class UpdateVehicleTool(Tool):
    """Update vehicle details."""

    @property
    def input_schema(self):
        return UpdateVehicleInput

    def execute(self, input_data: UpdateVehicleInput) -> ToolOutput:
        try:
            # Build update kwargs
            updates = {}
            if input_data.name is not None:
                updates["name"] = input_data.name
            if input_data.vehicle_type is not None:
                updates["vehicle_type"] = input_data.vehicle_type
            if input_data.license_plate is not None:
                updates["license_plate"] = input_data.license_plate
            if input_data.vin is not None:
                updates["vin"] = input_data.vin
            if input_data.year is not None:
                updates["year"] = input_data.year
            if input_data.make is not None:
                updates["make"] = input_data.make
            if input_data.model is not None:
                updates["model"] = input_data.model
            if input_data.status is not None:
                updates["status"] = input_data.status
            if input_data.notes is not None:
                updates["notes"] = input_data.notes

            # Update vehicle
            db.update_vehicle(input_data.vehicle_id, **updates)

            return ToolOutput(
                success=True,
                data={
                    "vehicle_id": input_data.vehicle_id,
                    "updates": updates
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="UPDATE_VEHICLE_FAILED",
                error_message=f"Failed to update vehicle: {str(e)}"
            )


@dataclass
class AddToolInput(ToolInput):
    """Input for adding a tool/equipment."""
    name: str
    tool_type: str  # power tool, hand tool, equipment
    serial_number: Optional[str] = ""
    purchase_date: Optional[str] = None
    purchase_cost: Optional[float] = 0.0
    status: Optional[str] = "active"
    notes: Optional[str] = ""


class AddToolTool(Tool):
    """Add a tool or equipment item."""

    @property
    def input_schema(self):
        return AddToolInput

    def execute(self, input_data: AddToolInput) -> ToolOutput:
        try:
            # Validate name
            if not input_data.name or not input_data.name.strip():
                return ToolOutput(
                    success=False,
                    error_code="EMPTY_NAME",
                    error_message="Tool name cannot be empty"
                )

            # Add tool
            tool_id = db.add_tool(
                name=input_data.name,
                tool_type=input_data.tool_type,
                serial_number=input_data.serial_number or "",
                purchase_date=input_data.purchase_date,
                purchase_cost=input_data.purchase_cost or 0.0,
                status=input_data.status or "active",
                notes=input_data.notes or ""
            )

            return ToolOutput(
                success=True,
                data={
                    "tool_id": tool_id,
                    "name": input_data.name,
                    "tool_type": input_data.tool_type
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_TOOL_FAILED",
                error_message=f"Failed to add tool: {str(e)}"
            )


# ===== TEMPLATE TOOLS =====

@dataclass
class AddTemplateMaterialInput(ToolInput):
    """Input for adding a material to a template."""
    template_id: int
    material_name: str
    quantity: float
    unit: Optional[str] = "ea"
    notes: Optional[str] = ""


class AddTemplateMaterialTool(Tool):
    """Add a material to a job template."""

    @property
    def input_schema(self):
        return AddTemplateMaterialInput

    def execute(self, input_data: AddTemplateMaterialInput) -> ToolOutput:
        try:
            # Validate quantity
            if input_data.quantity <= 0:
                return ToolOutput(
                    success=False,
                    error_code="INVALID_QUANTITY",
                    error_message="Quantity must be positive"
                )

            # Add template material
            template_material_id = db.add_template_material(
                template_id=input_data.template_id,
                material_name=input_data.material_name,
                quantity=input_data.quantity,
                unit=input_data.unit or "ea",
                notes=input_data.notes or ""
            )

            return ToolOutput(
                success=True,
                data={
                    "template_material_id": template_material_id,
                    "template_id": input_data.template_id,
                    "material_name": input_data.material_name,
                    "quantity": input_data.quantity
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_TEMPLATE_MATERIAL_FAILED",
                error_message=f"Failed to add template material: {str(e)}"
            )


@dataclass
class AddTemplateToolInput(ToolInput):
    """Input for adding a tool to a template."""
    template_id: int
    tool_name: str
    quantity: int = 1
    notes: Optional[str] = ""


class AddTemplateToolTool(Tool):
    """Add a tool requirement to a job template."""

    @property
    def input_schema(self):
        return AddTemplateToolInput

    def execute(self, input_data: AddTemplateToolInput) -> ToolOutput:
        try:
            # Validate quantity
            if input_data.quantity <= 0:
                return ToolOutput(
                    success=False,
                    error_code="INVALID_QUANTITY",
                    error_message="Quantity must be positive"
                )

            # Add template tool
            template_tool_id = db.add_template_tool(
                template_id=input_data.template_id,
                tool_name=input_data.tool_name,
                quantity=input_data.quantity,
                notes=input_data.notes or ""
            )

            return ToolOutput(
                success=True,
                data={
                    "template_tool_id": template_tool_id,
                    "template_id": input_data.template_id,
                    "tool_name": input_data.tool_name,
                    "quantity": input_data.quantity
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_TEMPLATE_TOOL_FAILED",
                error_message=f"Failed to add template tool: {str(e)}"
            )


# ===== COMPLIANCE & DOCUMENTS =====

@dataclass
class AddComplianceDocumentInput(ToolInput):
    """Input for adding a compliance document."""
    job_id: int
    document_type: str
    document_name: str
    file_path: str
    uploaded_by: Optional[int] = None
    notes: Optional[str] = ""


class AddComplianceDocumentTool(Tool):
    """Add a compliance document to a job."""

    @property
    def input_schema(self):
        return AddComplianceDocumentInput

    def execute(self, input_data: AddComplianceDocumentInput) -> ToolOutput:
        try:
            # Validate job exists
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(
                    success=False,
                    error_code="JOB_NOT_FOUND",
                    error_message=f"Job {input_data.job_id} not found"
                )

            # Add compliance document
            doc_id = db.add_compliance_document(
                job_id=input_data.job_id,
                document_type=input_data.document_type,
                document_name=input_data.document_name,
                file_path=input_data.file_path,
                uploaded_by=input_data.uploaded_by,
                notes=input_data.notes or ""
            )

            return ToolOutput(
                success=True,
                data={
                    "document_id": doc_id,
                    "job_id": input_data.job_id,
                    "document_type": input_data.document_type,
                    "document_name": input_data.document_name
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_DOCUMENT_FAILED",
                error_message=f"Failed to add compliance document: {str(e)}"
            )


# ===== REQUEST TOOLS =====

@dataclass
class AddRequestAttachmentInput(ToolInput):
    """Input for adding an attachment to a request."""
    request_id: int
    file_name: str
    file_path: str
    file_type: Optional[str] = ""
    file_size: Optional[int] = 0


class AddRequestAttachmentTool(Tool):
    """Add an attachment to a request."""

    @property
    def input_schema(self):
        return AddRequestAttachmentInput

    def execute(self, input_data: AddRequestAttachmentInput) -> ToolOutput:
        try:
            # Add attachment
            attachment_id = db.add_request_attachment(
                request_id=input_data.request_id,
                file_name=input_data.file_name,
                file_path=input_data.file_path,
                file_type=input_data.file_type or "",
                file_size=input_data.file_size or 0
            )

            return ToolOutput(
                success=True,
                data={
                    "attachment_id": attachment_id,
                    "request_id": input_data.request_id,
                    "file_name": input_data.file_name
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_ATTACHMENT_FAILED",
                error_message=f"Failed to add request attachment: {str(e)}"
            )


@dataclass
class AddRequestCommentInput(ToolInput):
    """Input for adding a comment to a request."""
    request_id: int
    user_id: int
    comment_text: str


class AddRequestCommentTool(Tool):
    """Add a comment to a request."""

    @property
    def input_schema(self):
        return AddRequestCommentInput

    def execute(self, input_data: AddRequestCommentInput) -> ToolOutput:
        try:
            # Validate comment
            if not input_data.comment_text or not input_data.comment_text.strip():
                return ToolOutput(
                    success=False,
                    error_code="EMPTY_COMMENT",
                    error_message="Comment text cannot be empty"
                )

            # Add comment
            comment_id = db.add_request_comment(
                request_id=input_data.request_id,
                user_id=input_data.user_id,
                comment_text=input_data.comment_text.strip()
            )

            return ToolOutput(
                success=True,
                data={
                    "comment_id": comment_id,
                    "request_id": input_data.request_id
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_COMMENT_FAILED",
                error_message=f"Failed to add request comment: {str(e)}"
            )


@dataclass
class UpdateChangeRequestStatusInput(ToolInput):
    """Input for updating change request status."""
    request_id: int
    status: str  # approved, rejected, pending, completed
    updated_by: int


class UpdateChangeRequestStatusTool(Tool):
    """Update the status of a change request."""

    @property
    def input_schema(self):
        return UpdateChangeRequestStatusInput

    def execute(self, input_data: UpdateChangeRequestStatusInput) -> ToolOutput:
        try:
            # Validate status
            valid_statuses = ["approved", "rejected", "pending", "completed"]
            if input_data.status not in valid_statuses:
                return ToolOutput(
                    success=False,
                    error_code="INVALID_STATUS",
                    error_message=f"Status must be one of: {', '.join(valid_statuses)}"
                )

            # Update status
            db.update_change_request_status(
                request_id=input_data.request_id,
                status=input_data.status,
                updated_by=input_data.updated_by
            )

            return ToolOutput(
                success=True,
                data={
                    "request_id": input_data.request_id,
                    "status": input_data.status
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="UPDATE_STATUS_FAILED",
                error_message=f"Failed to update change request status: {str(e)}"
            )


# ===== PAYROLL & SUBSCRIPTION TOOLS =====

@dataclass
class AddDeductionInput(ToolInput):
    """Input for adding a payroll deduction."""
    user_id: int
    amount: float
    deduction_type: str
    deduction_date: str
    description: Optional[str] = ""


class AddDeductionTool(Tool):
    """Add a payroll deduction."""

    @property
    def input_schema(self):
        return AddDeductionInput

    def execute(self, input_data: AddDeductionInput) -> ToolOutput:
        try:
            # Validate amount
            if input_data.amount <= 0:
                return ToolOutput(
                    success=False,
                    error_code="INVALID_AMOUNT",
                    error_message="Deduction amount must be positive"
                )

            # Add deduction
            deduction_id = db.add_deduction(
                user_id=input_data.user_id,
                amount=input_data.amount,
                deduction_type=input_data.deduction_type,
                deduction_date=input_data.deduction_date,
                description=input_data.description or ""
            )

            return ToolOutput(
                success=True,
                data={
                    "deduction_id": deduction_id,
                    "user_id": input_data.user_id,
                    "amount": input_data.amount
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_DEDUCTION_FAILED",
                error_message=f"Failed to add deduction: {str(e)}"
            )


@dataclass
class AddEntitlementInput(ToolInput):
    """Input for adding a subscription entitlement."""
    subscription_id: int
    entitlement_key: str  # e.g., "addon.estimator_pro"
    granted_date: Optional[str] = None


class AddEntitlementTool(Tool):
    """Add an entitlement to a subscription."""

    @property
    def input_schema(self):
        return AddEntitlementInput

    def execute(self, input_data: AddEntitlementInput) -> ToolOutput:
        try:
            # Use current date if not provided
            granted_date = input_data.granted_date or datetime.now().strftime("%Y-%m-%d")

            # Add entitlement
            entitlement_id = db.add_entitlement(
                subscription_id=input_data.subscription_id,
                entitlement_key=input_data.entitlement_key,
                granted_date=granted_date
            )

            return ToolOutput(
                success=True,
                data={
                    "entitlement_id": entitlement_id,
                    "subscription_id": input_data.subscription_id,
                    "entitlement_key": input_data.entitlement_key
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_ENTITLEMENT_FAILED",
                error_message=f"Failed to add entitlement: {str(e)}"
            )


# ===== COMMUNICATION TOOLS =====

@dataclass
class UpdateMessageTemplateInput(ToolInput):
    """Input for updating a message template."""
    template_id: int
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    is_active: Optional[bool] = None


class UpdateMessageTemplateTool(Tool):
    """Update a message template."""

    @property
    def input_schema(self):
        return UpdateMessageTemplateInput

    def execute(self, input_data: UpdateMessageTemplateInput) -> ToolOutput:
        try:
            # Build update kwargs
            updates = {}
            if input_data.name is not None:
                updates["name"] = input_data.name
            if input_data.subject is not None:
                updates["subject"] = input_data.subject
            if input_data.body is not None:
                updates["body"] = input_data.body
            if input_data.is_active is not None:
                updates["is_active"] = input_data.is_active

            # Update template
            db.update_message_template(input_data.template_id, **updates)

            return ToolOutput(
                success=True,
                data={
                    "template_id": input_data.template_id,
                    "updates": updates
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="UPDATE_TEMPLATE_FAILED",
                error_message=f"Failed to update message template: {str(e)}"
            )


# ===== EXPENSE CATEGORY TOOL =====

@dataclass
class AddExpenseCategoryInput(ToolInput):
    """Input for adding an expense category."""
    name: str
    description: Optional[str] = ""
    is_tax_deductible: Optional[bool] = True


class AddExpenseCategoryTool(Tool):
    """Add an expense category."""

    @property
    def input_schema(self):
        return AddExpenseCategoryInput

    def execute(self, input_data: AddExpenseCategoryInput) -> ToolOutput:
        try:
            # Validate name
            if not input_data.name or not input_data.name.strip():
                return ToolOutput(
                    success=False,
                    error_code="EMPTY_NAME",
                    error_message="Category name cannot be empty"
                )

            # Add category
            category_id = db.add_expense_category(
                name=input_data.name.strip(),
                description=input_data.description or "",
                is_tax_deductible=input_data.is_tax_deductible
            )

            return ToolOutput(
                success=True,
                data={
                    "category_id": category_id,
                    "name": input_data.name.strip()
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_CATEGORY_FAILED",
                error_message=f"Failed to add expense category: {str(e)}"
            )


# ===== AUDIT LOG TOOL =====

@dataclass
class AddAuditLogInput(ToolInput):
    """Input for adding an audit log entry."""
    username: str
    action: str
    user_id: Optional[int] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    before_data: Optional[dict] = None
    after_data: Optional[dict] = None
    ip_address: Optional[str] = None
    details: Optional[str] = ""


class AddAuditLogTool(Tool):
    """Add an audit log entry (primarily for authentication events)."""

    @property
    def input_schema(self):
        return AddAuditLogInput

    def execute(self, input_data: AddAuditLogInput) -> ToolOutput:
        try:
            user_id = input_data.user_id if input_data.user_id is not None else 0

            # Add audit log
            db.add_audit_log(
                entity_type=input_data.entity_type,
                entity_id=input_data.entity_id,
                action=input_data.action,
                user_id=user_id,
                username=input_data.username,
                before_data=input_data.before_data,
                after_data=input_data.after_data,
                ip_address=input_data.ip_address,
                details=input_data.details
            )

            return ToolOutput(
                success=True,
                data={
                    "action": input_data.action,
                    "username": input_data.username
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="ADD_AUDIT_LOG_FAILED",
                error_message=f"Failed to add audit log: {str(e)}"
            )
