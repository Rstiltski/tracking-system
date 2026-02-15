"""
Materials and inventory management tools for the Brain system.
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
class CreateMaterialInput(ToolInput):
    """Input for creating a material in the catalog."""
    name: str
    default_supplier: Optional[str] = ''
    supplier_id: Optional[int] = None
    default_unit_cost: float = 0.0
    unit: str = 'ea'
    notes: Optional[str] = ''
    stock_qty: float = 0.0
    reorder_point: float = 0.0
    reorder_qty: float = 1.0

class CreateMaterialTool(Tool):
    """Add a material to the catalog."""

    @property
    def input_schema(self):
        return CreateMaterialInput

    def execute(self, input_data: CreateMaterialInput) -> ToolOutput:
        """
        Create a new material in the materials library.
        
        Returns:
            ToolOutput with material_id in data
        """
        try:
            if not input_data.name or not input_data.name.strip():
                return ToolOutput(success=False, error_code='TOOL_MATERIAL_CREATE_EMPTY_NAME', error_message='Material name cannot be empty')
            if input_data.default_unit_cost < 0:
                return ToolOutput(success=False, error_code='TOOL_MATERIAL_CREATE_NEGATIVE_COST', error_message='Unit cost cannot be negative')
            if input_data.stock_qty < 0:
                return ToolOutput(success=False, error_code='TOOL_MATERIAL_CREATE_NEGATIVE_STOCK', error_message='Stock quantity cannot be negative')
            if input_data.reorder_point < 0:
                return ToolOutput(success=False, error_code='TOOL_MATERIAL_CREATE_NEGATIVE_REORDER', error_message='Reorder point cannot be negative')
            if input_data.reorder_qty <= 0:
                return ToolOutput(success=False, error_code='TOOL_MATERIAL_CREATE_INVALID_REORDER_QTY', error_message='Reorder quantity must be positive')
            material_id = db.add_material_to_library(name=input_data.name.strip(), default_supplier=input_data.default_supplier or '', supplier_id=input_data.supplier_id, default_unit_cost=input_data.default_unit_cost, unit=input_data.unit, notes=input_data.notes or '')
            if input_data.reorder_point > 0 or input_data.reorder_qty != 1.0:
                db.set_inventory_thresholds(material_id=material_id, reorder_point=input_data.reorder_point, reorder_qty=input_data.reorder_qty)
            if input_data.stock_qty > 0:
                db.adjust_inventory(material_id=material_id, delta_qty=input_data.stock_qty, reason='Initial stock')
            return ToolOutput(success=True, data={'material_id': material_id, 'name': input_data.name.strip(), 'unit_cost': input_data.default_unit_cost, 'stock_qty': input_data.stock_qty})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_MATERIAL_CREATE_FAILED', error_message=str(e))

@dataclass
class UpdateMaterialInput(ToolInput):
    """Input for updating a material's details."""
    material_id: int
    name: Optional[str] = None
    default_supplier: Optional[str] = None
    supplier_id: Optional[int] = None
    default_unit_cost: Optional[float] = None
    unit: Optional[str] = None
    notes: Optional[str] = None
    reorder_point: Optional[float] = None
    reorder_qty: Optional[float] = None

class UpdateMaterialTool(Tool):
    """Update material details and pricing."""

    @property
    def input_schema(self):
        return UpdateMaterialInput

    def execute(self, input_data: UpdateMaterialInput) -> ToolOutput:
        """
        Update an existing material's details.
        
        Returns:
            ToolOutput with updated material details in data
        """
        try:
            materials = db.list_materials_library()
            material = next((m for m in materials if m.get('id', 0) == input_data.material_id), None)
            if not material:
                return ToolOutput(success=False, error_code='TOOL_MATERIAL_UPDATE_NOT_FOUND', error_message=f'Material {input_data.material_id} not found')
            updates = {}
            if input_data.name is not None:
                if not input_data.name.strip():
                    return ToolOutput(success=False, error_code='TOOL_MATERIAL_UPDATE_EMPTY_NAME', error_message='Material name cannot be empty')
                updates['name'] = input_data.name.strip()
            if input_data.default_supplier is not None:
                updates['default_supplier'] = input_data.default_supplier
            if input_data.supplier_id is not None:
                updates['supplier_id'] = input_data.supplier_id
            if input_data.default_unit_cost is not None:
                if input_data.default_unit_cost < 0:
                    return ToolOutput(success=False, error_code='TOOL_MATERIAL_UPDATE_NEGATIVE_COST', error_message='Unit cost cannot be negative')
                updates['default_unit_cost'] = input_data.default_unit_cost
            if input_data.unit is not None:
                updates['unit'] = input_data.unit
            if input_data.notes is not None:
                updates['notes'] = input_data.notes
            if updates:
                import sqlite3
                with db.get_conn() as conn:
                    set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
                    values = list(updates.values()) + [input_data.material_id]
                    conn.execute(f'UPDATE materials_library SET {set_clause} WHERE id = ?', values)
                    conn.commit()
            if input_data.reorder_point is not None or input_data.reorder_qty is not None:
                if input_data.reorder_point is not None and input_data.reorder_point < 0:
                    return ToolOutput(success=False, error_code='TOOL_MATERIAL_UPDATE_NEGATIVE_REORDER', error_message='Reorder point cannot be negative')
                if input_data.reorder_qty is not None and input_data.reorder_qty <= 0:
                    return ToolOutput(success=False, error_code='TOOL_MATERIAL_UPDATE_INVALID_REORDER_QTY', error_message='Reorder quantity must be positive')
                db.set_inventory_thresholds(material_id=input_data.material_id, reorder_point=input_data.reorder_point if input_data.reorder_point is not None else material.get('reorder_point', 0), reorder_qty=input_data.reorder_qty if input_data.reorder_qty is not None else material.get('reorder_qty', 1))
            materials = db.list_materials_library()
            updated_material = next((m for m in materials if m.get('id', 0) == input_data.material_id), None)
            return ToolOutput(success=True, data=dict(updated_material) if updated_material else {})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_MATERIAL_UPDATE_FAILED', error_message=str(e))

@dataclass
class DeleteMaterialInput(ToolInput):
    """Input for deleting a material from the catalog."""
    material_id: int

class DeleteMaterialTool(Tool):
    """Remove a material from the catalog (HIGH RISK - requires confirmation)."""

    @property
    def input_schema(self):
        return DeleteMaterialInput

    def execute(self, input_data: DeleteMaterialInput) -> ToolOutput:
        """
        Delete a material from the materials library.
        
        Note: This is a HIGH risk operation that requires confirmation.
        
        Returns:
            ToolOutput with deleted material_id in data
        """
        try:
            materials = db.list_materials_library()
            material = next((m for m in materials if m.get('id', 0) == input_data.material_id), None)
            if not material:
                return ToolOutput(success=False, error_code='TOOL_MATERIAL_DELETE_NOT_FOUND', error_message=f'Material {input_data.material_id} not found')
            with db.get_connection() as conn:
                job_usage = conn.execute('SELECT COUNT(*) as count FROM job_materials WHERE material_id = ?', (input_data.material_id,)).fetchone()
                if job_usage and job_usage.get('count', 0) > 0:
                    return ToolOutput(success=False, error_code='TOOL_MATERIAL_DELETE_IN_USE', error_message=f"Material '{material.get('name', 0)}' is used in {job_usage.get('count', 0)} job(s) and cannot be deleted")
            material_name = material.get('name', 0)
            db.delete_material_from_library(input_data.material_id)
            return ToolOutput(success=True, data={'material_id': input_data.material_id, 'name': material_name, 'message': f"Material '{material_name}' deleted successfully"})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_MATERIAL_DELETE_FAILED', error_message=str(e))

@dataclass
class AdjustInventoryInput(ToolInput):
    """Input for adjusting material inventory levels."""
    material_id: int
    delta_qty: float
    reason: str = ''

class AdjustInventoryTool(Tool):
    """Adjust inventory quantity for a material (stock in/out)."""

    @property
    def input_schema(self):
        return AdjustInventoryInput

    def execute(self, input_data: AdjustInventoryInput) -> ToolOutput:
        """
        Adjust the inventory level of a material.
        
        Positive delta_qty = stock in (purchase, return)
        Negative delta_qty = stock out (usage, waste, damage)
        
        Returns:
            ToolOutput with new stock level in data
        """
        try:
            materials = db.list_materials_library()
            material = next((m for m in materials if m.get('id', 0) == input_data.material_id), None)
            if not material:
                return ToolOutput(success=False, error_code='TOOL_INVENTORY_ADJUST_NOT_FOUND', error_message=f'Material {input_data.material_id} not found')
            if input_data.delta_qty == 0:
                return ToolOutput(success=False, error_code='TOOL_INVENTORY_ADJUST_ZERO_DELTA', error_message='Adjustment quantity cannot be zero')
            current_stock = material.get('stock_qty', 0) or material.get('quantity_on_hand', 0) or 0
            new_stock = current_stock + input_data.delta_qty
            if new_stock < 0:
                return ToolOutput(success=False, error_code='TOOL_INVENTORY_ADJUST_NEGATIVE_RESULT', error_message=f'Adjustment of {input_data.delta_qty} would result in negative stock (current: {current_stock})')
            db.adjust_inventory(material_id=input_data.material_id, delta_qty=input_data.delta_qty, reason=input_data.reason or 'Manual adjustment')
            reorder_point = material.get('reorder_point', 0) or 0
            needs_reorder = new_stock <= reorder_point
            return ToolOutput(success=True, data={'material_id': input_data.material_id, 'material_name': material.get('name', 0), 'previous_stock': current_stock, 'adjustment': input_data.delta_qty, 'new_stock': new_stock, 'unit': material.get('unit', 'ea'), 'needs_reorder': needs_reorder, 'reorder_point': reorder_point})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_INVENTORY_ADJUST_FAILED', error_message=str(e))

@dataclass
class RecordUsageInput(ToolInput):
    """Input for recording material usage on a job."""
    job_id: int
    material_id: Optional[int] = None
    material_name: str = ''
    quantity: float = 1.0
    unit_cost: float = 0.0
    supplier: str = ''
    supplier_id: Optional[int] = None
    receipt_photo: str = ''
    notes: str = ''
    deduct_from_inventory: bool = True

class RecordUsageTool(Tool):
    """Record material usage on a job and optionally deduct from inventory."""

    @property
    def input_schema(self):
        return RecordUsageInput

    def execute(self, input_data: RecordUsageInput) -> ToolOutput:
        """
        Record that a material was used on a job.
        
        If material_id is provided and deduct_from_inventory is True,
        will automatically deduct the quantity from stock.
        
        Returns:
            ToolOutput with job_material_id in data
        """
        try:
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(success=False, error_code='TOOL_USAGE_RECORD_JOB_NOT_FOUND', error_message=f'Job {input_data.job_id} not found')
            if input_data.quantity <= 0:
                return ToolOutput(success=False, error_code='TOOL_USAGE_RECORD_INVALID_QUANTITY', error_message='Quantity must be positive')
            if input_data.unit_cost < 0:
                return ToolOutput(success=False, error_code='TOOL_USAGE_RECORD_NEGATIVE_COST', error_message='Unit cost cannot be negative')
            material_name = input_data.material_name
            if input_data.material_id:
                materials = db.list_materials_library()
                material = next((m for m in materials if m.get('id', 0) == input_data.material_id), None)
                if not material:
                    return ToolOutput(success=False, error_code='TOOL_USAGE_RECORD_MATERIAL_NOT_FOUND', error_message=f'Material {input_data.material_id} not found')
                if not material_name:
                    material_name = material.get('name', 0)
                if input_data.unit_cost == 0:
                    unit_cost = material.get('default_unit_cost', 0)
                else:
                    unit_cost = input_data.unit_cost
            else:
                if not material_name or not material_name.strip():
                    return ToolOutput(success=False, error_code='TOOL_USAGE_RECORD_NO_MATERIAL_NAME', error_message='Material name is required for custom materials')
                unit_cost = input_data.unit_cost
            total_cost = input_data.quantity * unit_cost
            job_material_id = db.add_job_material(job_id=input_data.job_id, material_name=material_name.strip(), supplier=input_data.supplier, supplier_id=input_data.supplier_id, quantity=input_data.quantity, unit_cost=unit_cost, material_id=input_data.material_id, receipt_photo=input_data.receipt_photo, notes=input_data.notes)
            inventory_adjusted = False
            if input_data.material_id and input_data.deduct_from_inventory:
                try:
                    db.adjust_inventory(material_id=input_data.material_id, delta_qty=-input_data.quantity, reason=f'Used on job {input_data.job_id}')
                    inventory_adjusted = True
                except Exception as inv_error:
                    pass
            return ToolOutput(success=True, data={'job_material_id': job_material_id, 'job_id': input_data.job_id, 'material_id': input_data.material_id, 'material_name': material_name.strip(), 'quantity': input_data.quantity, 'unit_cost': unit_cost, 'total_cost': total_cost, 'inventory_adjusted': inventory_adjusted})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_USAGE_RECORD_FAILED', error_message=str(e))

@dataclass
class ReorderMaterialInput(ToolInput):
    """Input for creating a reorder notification for a material."""
    material_id: int
    quantity: Optional[float] = None

class ReorderMaterialTool(Tool):
    """Generate a reorder notification for low-stock materials."""

    @property
    def input_schema(self):
        return ReorderMaterialInput

    def execute(self, input_data: ReorderMaterialInput) -> ToolOutput:
        """
        Create a reorder notification/reminder for a material.
        
        This is a placeholder for a future purchase order system.
        For now, it returns the details needed to manually reorder.
        
        Returns:
            ToolOutput with reorder details in data
        """
        try:
            materials = db.list_materials_library()
            material = next((m for m in materials if m.get('id', 0) == input_data.material_id), None)
            if not material:
                return ToolOutput(success=False, error_code='TOOL_REORDER_MATERIAL_NOT_FOUND', error_message=f'Material {input_data.material_id} not found')
            current_stock = material.get('stock_qty', 0) or material.get('quantity_on_hand', 0) or 0
            reorder_point = material.get('reorder_point', 0) or 0
            reorder_qty = input_data.quantity if input_data.quantity else material.get('reorder_qty', 1) or 1
            if reorder_qty <= 0:
                return ToolOutput(success=False, error_code='TOOL_REORDER_INVALID_QUANTITY', error_message='Reorder quantity must be positive')
            if current_stock > reorder_point:
                return ToolOutput(success=True, data={'material_id': input_data.material_id, 'material_name': material.get('name', 0), 'needs_reorder': False, 'current_stock': current_stock, 'reorder_point': reorder_point, 'message': f"Material '{material.get('name', 0)}' does not need reordering (stock: {current_stock}, reorder point: {reorder_point})"})
            unit_cost = material.get('default_unit_cost', 0) or 0
            estimated_cost = reorder_qty * unit_cost
            reorder_details = {'material_id': input_data.material_id, 'material_name': material.get('name', 0), 'needs_reorder': True, 'current_stock': current_stock, 'reorder_point': reorder_point, 'reorder_quantity': reorder_qty, 'unit': material.get('unit', 'ea'), 'supplier': material.get('default_supplier', ''), 'supplier_id': material.get('supplier_id'), 'unit_cost': unit_cost, 'estimated_cost': estimated_cost, 'message': f"Material '{material.get('name', 0)}' is low stock ({current_stock} {material.get('unit', 'ea')}). Reorder {reorder_qty} {material.get('unit', 'ea')} for ~£{estimated_cost:.2f}"}
            return ToolOutput(success=True, data=reorder_details)
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_REORDER_FAILED', error_message=str(e))
