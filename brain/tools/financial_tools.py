"""
Financial tools - Invoice and Payment operations
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
from dataclasses import dataclass
from typing import Optional, List, Dict
from brain.core.tool import Tool, ToolInput
from brain.core.result import ToolOutput
from brain.tools.decorators import register_tool
import db

@dataclass
class CreateInvoiceInput(ToolInput):
    job_id: int
    invoice_no: str
    total: float
    line_items: Optional[List[Dict]] = None
    due_date: Optional[str] = None
    issue_date: Optional[str] = None
    vat_mode: Optional[str] = 'none'
    notes: Optional[str] = ''
    payment_link_url: Optional[str] = None

@register_tool(name="CreateInvoice", risk="Medium", category="financial")
class CreateInvoiceTool(Tool):
    """Create invoice for a job"""

    @property
    def input_schema(self):
        return CreateInvoiceInput

    def execute(self, input_data: CreateInvoiceInput) -> ToolOutput:
        try:
            import sqlite3
            conn = sqlite3.connect(db.DB_PATH)
            job_row = conn.execute('SELECT customer_id FROM jobs WHERE id = ?', (input_data.job_id,)).fetchone()
            conn.close()
            if not job_row:
                return ToolOutput(success=False, error_code='TOOL_INVOICE_CREATE_JOB_NOT_FOUND', error_message=f'Job {input_data.job_id} not found')
            customer_id = ((((((((((((((job_row[0] if job_row else None) if job_row else None) if job_row else None) if job_row else None) if job_row else None) if job_row else None) if job_row else None) if job_row else None) if job_row else None) if job_row else None) if job_row else None) if job_row else None) if job_row else None) if job_row else None) if job_row else None
            invoice_id = db.add_invoice(invoice_no=input_data.invoice_no, customer_id=customer_id, job_id=input_data.job_id, issue_date=input_data.issue_date, due_date=input_data.due_date, status='draft', vat_mode=input_data.vat_mode or 'none', notes=input_data.notes or '', lines=input_data.line_items or [], payment_link_url=input_data.payment_link_url)
            return ToolOutput(success=True, data={'invoice_id': invoice_id, 'status': 'draft', 'invoice_no': input_data.invoice_no, 'total': input_data.total, 'customer_id': customer_id})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_INVOICE_CREATE_FAILED', error_message=str(e))

@dataclass
class SendInvoiceInput(ToolInput):
    invoice_id: int
    user_id: Optional[int] = None

@register_tool(name="SendInvoice", risk="Medium", category="financial")
class SendInvoiceTool(Tool):
    """Mark invoice as sent"""

    @property
    def input_schema(self):
        return SendInvoiceInput

    def execute(self, input_data: SendInvoiceInput) -> ToolOutput:
        try:
            invoice = db.get_invoice(input_data.invoice_id)
            if not invoice:
                return ToolOutput(success=False, error_code='TOOL_INVOICE_SEND_NOT_FOUND', error_message=f'Invoice {input_data.invoice_id} not found')
            user_id = input_data.user_id if input_data.user_id is not None else None
            db.mark_invoice_as_sent(input_data.invoice_id, user_id=user_id)
            return ToolOutput(success=True, data={'invoice_id': input_data.invoice_id, 'status': 'sent'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_INVOICE_SEND_FAILED', error_message=str(e))

@dataclass
class GetInvoiceInput(ToolInput):
    invoice_id: int

@register_tool(name="GetInvoice", risk="Low", category="financial")
class GetInvoiceTool(Tool):
    """Retrieve invoice details"""

    @property
    def input_schema(self):
        return GetInvoiceInput

    def execute(self, input_data: GetInvoiceInput) -> ToolOutput:
        try:
            invoice = db.get_invoice(input_data.invoice_id)
            if not invoice:
                return ToolOutput(success=False, error_code='TOOL_INVOICE_GET_NOT_FOUND', error_message=f'Invoice {input_data.invoice_id} not found')
            return ToolOutput(success=True, data=dict(invoice))
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_INVOICE_GET_FAILED', error_message=str(e))

@dataclass
class RecordPaymentInput(ToolInput):
    invoice_id: int
    amount: float
    payment_method: str
    payment_date: Optional[str] = None

@register_tool(name="RecordPayment", risk="Medium", category="financial")
class RecordPaymentTool(Tool):
    """Record payment against invoice"""

    @property
    def input_schema(self):
        return RecordPaymentInput

    def execute(self, input_data: RecordPaymentInput) -> ToolOutput:
        try:
            payment_id = db.brain_record_payment(invoice_id=input_data.invoice_id, amount=input_data.amount, payment_method=input_data.payment_method, payment_date=input_data.payment_date or '')
            invoice = db.get_invoice(input_data.invoice_id)
            return ToolOutput(success=True, data={'payment_id': payment_id, 'invoice_id': input_data.invoice_id, 'amount': input_data.amount, 'invoice_status': invoice.get('status', 0) if invoice else 'UNKNOWN'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_PAYMENT_RECORD_FAILED', error_message=str(e))

@dataclass
class GetPaymentInput(ToolInput):
    payment_id: int

@register_tool(name="GetPayment", risk="Low", category="financial")
class GetPaymentTool(Tool):
    """Retrieve payment details"""

    @property
    def input_schema(self):
        return GetPaymentInput

    def execute(self, input_data: GetPaymentInput) -> ToolOutput:
        try:
            payment = db.get_payment(input_data.payment_id)
            if not payment:
                return ToolOutput(success=False, error_code='TOOL_PAYMENT_GET_NOT_FOUND', error_message=f'Payment {input_data.payment_id} not found')
            return ToolOutput(success=True, data=dict(payment))
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_PAYMENT_GET_FAILED', error_message=str(e))
# ============================================================================
# UpdateInvoiceStatus - Update invoice status (e.g., mark as paid)
# ============================================================================

@dataclass
class UpdateInvoiceStatusInput(ToolInput):
    invoice_id: int
    new_status: str  # draft, sent, paid, overdue, cancelled
    notes: Optional[str] = None

@register_tool(name="UpdateInvoiceStatus", risk="Medium", category="financial")
class UpdateInvoiceStatusTool(Tool):
    """Update invoice status"""

    @property
    def input_schema(self):
        return UpdateInvoiceStatusInput

    def execute(self, input_data: UpdateInvoiceStatusInput) -> ToolOutput:
        try:
            # Check invoice exists
            invoice = db.get_invoice(input_data.invoice_id)
            if not invoice:
                return ToolOutput(
                    success=False,
                    error_code="INVOICE_NOT_FOUND",
                    error_message=f"Invoice {input_data.invoice_id} not found"
                )

            # Update status
            db.update_invoice_state(input_data.invoice_id, input_data.new_status)

            return ToolOutput(
                success=True,
                data={
                    "invoice_id": input_data.invoice_id,
                    "new_status": input_data.new_status,
                    "message": f"Invoice status updated to {input_data.new_status}"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="UPDATE_INVOICE_STATUS_FAILED",
                error_message=str(e)
            )


# ============================================================================
# GenerateReceipt - Generate payment receipt
# ============================================================================

@dataclass
class GenerateReceiptInput(ToolInput):
    payment_id: int
    invoice_id: Optional[int] = None

@register_tool(name="GenerateReceipt", risk="Low", category="financial")
class GenerateReceiptTool(Tool):
    """Generate a payment receipt"""

    @property
    def input_schema(self):
        return GenerateReceiptInput

    def execute(self, input_data: GenerateReceiptInput) -> ToolOutput:
        try:
            # Get payment details
            payment = db.get_payment(input_data.payment_id)
            if not payment:
                return ToolOutput(
                    success=False,
                    error_code="PAYMENT_NOT_FOUND",
                    error_message=f"Payment {input_data.payment_id} not found"
                )

            # Generate receipt number
            receipt_number = db.generate_receipt_number(payment_id=input_data.payment_id)

            return ToolOutput(
                success=True,
                data={
                    "payment_id": input_data.payment_id,
                    "receipt_number": receipt_number,
                    "message": "Receipt generated successfully"
                }
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="GENERATE_RECEIPT_FAILED",
                error_message=str(e)
            )
