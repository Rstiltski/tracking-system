"""
Admin Tools - Administrative and setup operations

Tools for administrative operations:
- AddJobPhoto: Add photos to jobs
- AddEquipmentBooking: Book equipment for jobs  
- CompleteChecklistItem: Mark checklist items as complete
- AddEquipmentLog: Log equipment usage
- AddSupplier: Add supplier to library
- AddRole: Create user role
- SetRolePermissions: Set permissions for a role
- CreateTeam: Create team/crew
- AddTeamMember: Add member to team
- SetPayRule: Set pay rule for user
- AddBonus: Add bonus payment to user
- CreateInventoryItem: Create inventory item
- CreateCompany: Create company entity
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


# ============================================================================
# AddJobPhoto - Add photo to a job
# ============================================================================

@dataclass
class AddJobPhotoInput(ToolInput):
    job_id: int
    photo_type: str  # before, during, after, customer_upload
    file_path: str
    file_name: str
    caption: Optional[str] = None
    user_id: Optional[int] = None
    taken_at: Optional[str] = None
    taken_by: Optional[str] = None


class AddJobPhotoTool(Tool):
    """Add a photo to a job"""
    
    @property
    def input_schema(self):
        return AddJobPhotoInput
    
    def execute(self, input_data: AddJobPhotoInput) -> ToolOutput:
        try:
            photo_id = db.add_job_photo(
                job_id=input_data.job_id,
                photo_type=input_data.photo_type,
                file_path=input_data.file_path,
                file_name=input_data.file_name,
                caption=input_data.caption,
                user_id=input_data.user_id,
                taken_at=input_data.taken_at,
                taken_by=input_data.taken_by
            )
            
            return ToolOutput(
                success=True,
                data={
                    "photo_id": photo_id,
                    "job_id": input_data.job_id,
                    "file_path": input_data.file_path,
                    "message": "Photo added to job successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_ADD_JOB_PHOTO_ERROR",
                error_message=str(e)
            )


# ============================================================================
# AddEquipmentBooking - Book equipment for a job
# ============================================================================

@dataclass
class AddEquipmentBookingInput(ToolInput):
    equipment_name: str
    job_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    notes: Optional[str] = ""


class AddEquipmentBookingTool(Tool):
    """Book equipment for a job"""
    
    @property
    def input_schema(self):
        return AddEquipmentBookingInput
    
    def execute(self, input_data: AddEquipmentBookingInput) -> ToolOutput:
        try:
            booking_id = db.add_equipment_booking(
                name=input_data.equipment_name,
                job_id=input_data.job_id,
                date_from=input_data.start_date,
                date_to=input_data.end_date,
                notes=input_data.notes or ""
            )
            
            return ToolOutput(
                success=True,
                data={
                    "booking_id": booking_id,
                    "job_id": input_data.job_id,
                    "equipment_name": input_data.equipment_name,
                    "message": "Equipment booked successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_ADD_EQUIPMENT_BOOKING_ERROR",
                error_message=str(e)
            )


# ============================================================================
# CompleteChecklistItem - Mark checklist item as complete
# ============================================================================

@dataclass
class CompleteChecklistItemInput(ToolInput):
    item_id: int
    completed_by: int


class CompleteChecklistItemTool(Tool):
    """Mark a checklist item as complete"""
    
    @property
    def input_schema(self):
        return CompleteChecklistItemInput
    
    def execute(self, input_data: CompleteChecklistItemInput) -> ToolOutput:
        try:
            db.complete_checklist_item(
                item_id=input_data.item_id,
                completed_by=input_data.completed_by
            )
            
            return ToolOutput(
                success=True,
                data={
                    "item_id": input_data.item_id,
                    "completed_by": input_data.completed_by,
                    "message": "Checklist item marked as complete"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_COMPLETE_CHECKLIST_ITEM_ERROR",
                error_message=str(e)
            )


# ============================================================================
# AddEquipmentLog - Log equipment usage
# ============================================================================

@dataclass
class AddEquipmentLogInput(ToolInput):
    equipment_id: int
    log_type: str = "usage"  # usage, fuel, maintenance, repair
    description: Optional[str] = None
    job_id: Optional[int] = None
    log_date: Optional[str] = None
    hours_used: Optional[float] = None
    fuel_used: Optional[float] = None
    maintenance_note: str = ""
    cost: Optional[float] = None
    odometer_hours: Optional[float] = None
    performed_by: Optional[int] = None
    notes: str = ""


class AddEquipmentLogTool(Tool):
    """Log equipment usage or maintenance"""
    
    @property
    def input_schema(self):
        return AddEquipmentLogInput
    
    def execute(self, input_data: AddEquipmentLogInput) -> ToolOutput:
        try:
            log_id = db.add_equipment_log(
                equipment_id=input_data.equipment_id,
                log_type=input_data.log_type,
                description=input_data.description,
                job_id=input_data.job_id,
                log_date=input_data.log_date,
                hours_used=input_data.hours_used,
                fuel_used=input_data.fuel_used,
                maintenance_note=input_data.maintenance_note,
                cost=input_data.cost,
                odometer_hours=input_data.odometer_hours,
                performed_by=input_data.performed_by,
                notes=input_data.notes
            )
            
            return ToolOutput(
                success=True,
                data={
                    "log_id": log_id,
                    "equipment_id": input_data.equipment_id,
                    "log_type": input_data.log_type,
                    "message": "Equipment log added successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_ADD_EQUIPMENT_LOG_ERROR",
                error_message=str(e)
            )


# ============================================================================
# AddSupplier - Add supplier to library
# ============================================================================

@dataclass
class AddSupplierInput(ToolInput):
    name: str
    phone: Optional[str] = ""
    email: Optional[str] = ""
    website: Optional[str] = ""
    notes: Optional[str] = ""


class AddSupplierTool(Tool):
    """Add a supplier to the supplier library"""
    
    @property
    def input_schema(self):
        return AddSupplierInput
    
    def execute(self, input_data: AddSupplierInput) -> ToolOutput:
        try:
            supplier_id = db.add_supplier(
                name=input_data.name,
                phone=input_data.phone or "",
                email=input_data.email or "",
                website=input_data.website or "",
                notes=input_data.notes or ""
            )
            
            return ToolOutput(
                success=True,
                data={
                    "supplier_id": supplier_id,
                    "name": input_data.name,
                    "message": f"Supplier '{input_data.name}' added successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_ADD_SUPPLIER_ERROR",
                error_message=str(e)
            )


# ============================================================================
# AddRole - Create user role
# ============================================================================

@dataclass
class AddRoleInput(ToolInput):
    name: str
    description: Optional[str] = ""
    base_role: Optional[str] = None


class AddRoleTool(Tool):
    """Create a new user role"""
    
    @property
    def input_schema(self):
        return AddRoleInput
    
    def execute(self, input_data: AddRoleInput) -> ToolOutput:
        try:
            role_id = db.add_role(
                name=input_data.name,
                description=input_data.description or "",
                base_role=input_data.base_role
            )
            
            return ToolOutput(
                success=True,
                data={
                    "role_id": role_id,
                    "name": input_data.name,
                    "message": f"Role '{input_data.name}' created successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_ADD_ROLE_ERROR",
                error_message=str(e)
            )


# ============================================================================
# SetRolePermissions - Set permissions for a role
# ============================================================================

@dataclass
class SetRolePermissionsInput(ToolInput):
    role_name: str
    entity: str
    actions: list  # List of actions: create, read, update, delete


class SetRolePermissionsTool(Tool):
    """Set permissions for a role"""
    
    @property
    def input_schema(self):
        return SetRolePermissionsInput
    
    def execute(self, input_data: SetRolePermissionsInput) -> ToolOutput:
        try:
            db.set_role_permissions(
                role_name=input_data.role_name,
                entity=input_data.entity,
                actions=input_data.actions
            )
            
            return ToolOutput(
                success=True,
                data={
                    "role_name": input_data.role_name,
                    "entity": input_data.entity,
                    "actions": input_data.actions,
                    "message": f"Permissions set for role '{input_data.role_name}'"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_SET_ROLE_PERMISSIONS_ERROR",
                error_message=str(e)
            )


# ============================================================================
# CreateTeam - Create team/crew
# ============================================================================

@dataclass
class CreateTeamInput(ToolInput):
    name: str
    description: Optional[str] = ""


class CreateTeamTool(Tool):
    """Create a new team or crew"""
    
    @property
    def input_schema(self):
        return CreateTeamInput
    
    def execute(self, input_data: CreateTeamInput) -> ToolOutput:
        try:
            team_id = db.create_team(
                name=input_data.name,
                description=input_data.description or ""
            )
            
            return ToolOutput(
                success=True,
                data={
                    "team_id": team_id,
                    "name": input_data.name,
                    "message": f"Team '{input_data.name}' created successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_CREATE_TEAM_ERROR",
                error_message=str(e)
            )


# ============================================================================
# AddTeamMember - Add member to team
# ============================================================================

@dataclass
class AddTeamMemberInput(ToolInput):
    team_id: int
    user_id: int
    role: Optional[str] = "Assistant"


class AddTeamMemberTool(Tool):
    """Add a member to a team"""
    
    @property
    def input_schema(self):
        return AddTeamMemberInput
    
    def execute(self, input_data: AddTeamMemberInput) -> ToolOutput:
        try:
            db.add_team_member(
                team_id=input_data.team_id,
                user_id=input_data.user_id,
                role=input_data.role or "Assistant"
            )
            
            return ToolOutput(
                success=True,
                data={
                    "team_id": input_data.team_id,
                    "user_id": input_data.user_id,
                    "role": input_data.role,
                    "message": "Team member added successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_ADD_TEAM_MEMBER_ERROR",
                error_message=str(e)
            )


# ============================================================================
# SetPayRule - Set pay rule for user
# ============================================================================

@dataclass
class SetPayRuleInput(ToolInput):
    user_id: int
    hourly_rate: float
    overtime_multiplier: float = 1.5
    overtime_daily: float = 8.0
    overtime_weekly: float = 40.0
    weekend_multiplier: float = 1.0
    holiday_multiplier: float = 2.0
    rounding_minutes: int = 15
    effective_from: Optional[str] = None
    notes: str = ""


class SetPayRuleTool(Tool):
    """Set pay rule for a user"""
    
    @property
    def input_schema(self):
        return SetPayRuleInput
    
    def execute(self, input_data: SetPayRuleInput) -> ToolOutput:
        try:
            rule_id = db.set_pay_rule(
                user_id=input_data.user_id,
                hourly_rate=input_data.hourly_rate,
                overtime_multiplier=input_data.overtime_multiplier,
                overtime_daily=input_data.overtime_daily,
                overtime_weekly=input_data.overtime_weekly,
                weekend_multiplier=input_data.weekend_multiplier,
                holiday_multiplier=input_data.holiday_multiplier,
                rounding_minutes=input_data.rounding_minutes,
                effective_from=input_data.effective_from,
                notes=input_data.notes
            )
            
            return ToolOutput(
                success=True,
                data={
                    "rule_id": rule_id,
                    "user_id": input_data.user_id,
                    "hourly_rate": input_data.hourly_rate,
                    "message": "Pay rule set successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_SET_PAY_RULE_ERROR",
                error_message=str(e)
            )


# ============================================================================
# AddBonus - Add bonus payment to user
# ============================================================================

@dataclass
class AddBonusInput(ToolInput):
    user_id: int
    amount: float
    bonus_type: str
    bonus_date: Optional[str] = None
    job_id: Optional[int] = None
    description: str = ""
    created_by: Optional[int] = None


class AddBonusTool(Tool):
    """Add a bonus payment to a user"""
    
    @property
    def input_schema(self):
        return AddBonusInput
    
    def execute(self, input_data: AddBonusInput) -> ToolOutput:
        try:
            bonus_id = db.add_bonus(
                user_id=input_data.user_id,
                amount=input_data.amount,
                bonus_type=input_data.bonus_type,
                bonus_date=input_data.bonus_date,
                job_id=input_data.job_id,
                description=input_data.description,
                created_by=input_data.created_by
            )
            
            return ToolOutput(
                success=True,
                data={
                    "bonus_id": bonus_id,
                    "user_id": input_data.user_id,
                    "amount": input_data.amount,
                    "message": "Bonus added successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_ADD_BONUS_ERROR",
                error_message=str(e)
            )


# ============================================================================
# CreateInventoryItem - Create inventory item
# ============================================================================

@dataclass
class CreateInventoryItemInput(ToolInput):
    name: str
    category: str  # Materials, Tools, Consumables, Equipment
    unit: str  # m, kg, pieces, etc.
    current_stock: float = 0.0
    reorder_level: float = 0.0
    cost_per_unit: float = 0.0
    supplier_id: Optional[int] = None


class CreateInventoryItemTool(Tool):
    """Create an inventory item"""
    
    @property
    def input_schema(self):
        return CreateInventoryItemInput
    
    def execute(self, input_data: CreateInventoryItemInput) -> ToolOutput:
        try:
            item_id = db.create_inventory_item(
                name=input_data.name,
                category=input_data.category,
                unit=input_data.unit,
                current_stock=input_data.current_stock,
                reorder_level=input_data.reorder_level,
                cost_per_unit=input_data.cost_per_unit,
                supplier_id=input_data.supplier_id
            )
            
            return ToolOutput(
                success=True,
                data={
                    "item_id": item_id,
                    "name": input_data.name,
                    "category": input_data.category,
                    "message": f"Inventory item '{input_data.name}' created successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_CREATE_INVENTORY_ITEM_ERROR",
                error_message=str(e)
            )


# ============================================================================
# CreateCompany - Create company entity
# ============================================================================

@dataclass
class CreateCompanyInput(ToolInput):
    name: str
    trading_name: Optional[str] = None
    company_number: Optional[str] = None
    vat_number: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True


class CreateCompanyTool(Tool):
    """Create a new company entity"""
    
    @property
    def input_schema(self):
        return CreateCompanyInput
    
    def execute(self, input_data: CreateCompanyInput) -> ToolOutput:
        try:
            company_id = db.create_company(
                name=input_data.name,
                trading_name=input_data.trading_name,
                company_number=input_data.company_number,
                vat_number=input_data.vat_number,
                address=input_data.address,
                is_active=input_data.is_active
            )
            
            return ToolOutput(
                success=True,
                data={
                    "company_id": company_id,
                    "name": input_data.name,
                    "message": f"Company '{input_data.name}' created successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_CREATE_COMPANY_ERROR",
                error_message=str(e)
            )


# ============================================================================
# UpdateCompany - Update company details
# ============================================================================

@dataclass
class UpdateCompanyInput(ToolInput):
    company_id: int
    name: Optional[str] = None
    trading_name: Optional[str] = None
    company_number: Optional[str] = None
    vat_number: Optional[str] = None
    address: Optional[str] = None
    subscription_tier: Optional[str] = None
    is_active: Optional[bool] = None


class UpdateCompanyTool(Tool):
    """Update company details including subscription tier"""
    
    @property
    def input_schema(self):
        return UpdateCompanyInput
    
    def execute(self, input_data: UpdateCompanyInput) -> ToolOutput:
        try:
            # Build kwargs for update
            update_fields = {}
            if input_data.name is not None:
                update_fields["name"] = input_data.name
            if input_data.trading_name is not None:
                update_fields["trading_name"] = input_data.trading_name
            if input_data.company_number is not None:
                update_fields["company_number"] = input_data.company_number
            if input_data.vat_number is not None:
                update_fields["vat_number"] = input_data.vat_number
            if input_data.address is not None:
                update_fields["address"] = input_data.address
            if input_data.subscription_tier is not None:
                update_fields["subscription_tier"] = input_data.subscription_tier
            if input_data.is_active is not None:
                update_fields["is_active"] = input_data.is_active
            
            db.update_company(company_id=input_data.company_id, **update_fields)
            
            return ToolOutput(
                success=True,
                data={
                    "company_id": input_data.company_id,
                    "message": "Company updated successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_UPDATE_COMPANY_ERROR",
                error_message=str(e)
            )
