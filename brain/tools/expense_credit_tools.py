"""
Expense and Credit Note Tools for Brain Architecture

This module implements tools for:
- Expense management (Record, Update, Delete, Link to Job)
- Credit note operations (Create, Issue, Apply, Void)
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
from dataclasses import dataclass, field
from typing import Optional
from brain.core.tool import Tool, ToolInput, ToolOutput
import db

@dataclass
class RecordExpenseInput(ToolInput):
    """Input for RecordExpense tool"""
    expense_date: str
    item: str
    cost: float
    category: str = 'Materials'
    supplier: str = ''
    job_id: Optional[int] = None
    supplier_id: Optional[int] = None

@dataclass
class RecordExpenseOutput(ToolOutput):
    """Output for RecordExpense tool"""
    expense_id: int = 0
    cost: float = 0.0
    category: str = ''
    item: str = ''
    job_id: Optional[int] = None

class RecordExpenseTool(Tool):
    """
    Record a new expense for a job or general company expense.
    
    Risk Tier: MEDIUM
    - Involves cost tracking
    - Can impact job profitability calculations
    """

    @property
    def input_schema(self):
        return RecordExpenseInput

    def execute(self, input_data: RecordExpenseInput) -> RecordExpenseOutput:
        """Record a new expense"""
        if input_data.cost <= 0:
            return RecordExpenseOutput(success=False, expense_id=0, job_id=input_data.job_id, cost=0, category='', item='', error_code='TOOL_EXPENSE_INVALID_COST', error_message='Expense cost must be greater than zero')
        if not input_data.item or not input_data.item.strip():
            return RecordExpenseOutput(success=False, expense_id=0, job_id=input_data.job_id, cost=0, category='', item='', error_code='TOOL_EXPENSE_EMPTY_ITEM', error_message='Expense item description is required')
        if input_data.job_id:
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return RecordExpenseOutput(success=False, expense_id=0, job_id=input_data.job_id, cost=0, category='', item='', error_code='TOOL_EXPENSE_JOB_NOT_FOUND', error_message=f'Job with ID {input_data.job_id} not found')
        try:
            from datetime import datetime
            datetime.strptime(input_data.expense_date, '%Y-%m-%d')
        except ValueError:
            return RecordExpenseOutput(success=False, expense_id=0, job_id=input_data.job_id, cost=0, category='', item='', error_code='TOOL_EXPENSE_INVALID_DATE', error_message='Expense date must be in YYYY-MM-DD format')
        db.add_expense(job_id=input_data.job_id or 0, expense_date=input_data.expense_date, item=input_data.item, cost=input_data.cost, category=input_data.category, supplier=input_data.supplier, supplier_id=input_data.supplier_id, company_id=input_data.company_id)
        expenses = db.list_expenses(job_id=input_data.job_id)
        expense_id = expenses[0]['id'] if expenses else 0
        return RecordExpenseOutput(success=True, expense_id=expense_id, job_id=input_data.job_id, cost=input_data.cost, category=input_data.category, item=input_data.item)

@dataclass
class UpdateExpenseInput(ToolInput):
    """Input for UpdateExpense tool"""
    expense_id: int
    item: Optional[str] = None
    cost: Optional[float] = None
    category: Optional[str] = None
    supplier: Optional[str] = None
    expense_date: Optional[str] = None

@dataclass
class UpdateExpenseOutput(ToolOutput):
    """Output for UpdateExpense tool"""
    expense_id: int = 0
    updated_fields: list = field(default_factory=list)

class UpdateExpenseTool(Tool):
    """
    Update an existing expense record.
    
    Risk Tier: LOW
    - Only modifies existing records
    - Doesn't affect financial calculations directly
    """

    @property
    def input_schema(self):
        return UpdateExpenseInput

    def execute(self, input_data: UpdateExpenseInput) -> UpdateExpenseOutput:
        """Update an expense"""
        expenses = db.list_expenses()
        expense = next((e for e in expenses if e.get('id', 0) == input_data.expense_id), None)
        if not expense:
            return UpdateExpenseOutput(success=False, expense_id=input_data.expense_id, updated_fields=[], error_code='TOOL_EXPENSE_NOT_FOUND', error_message=f'Expense with ID {input_data.expense_id} not found')
        if input_data.cost is not None and input_data.cost <= 0:
            return UpdateExpenseOutput(success=False, expense_id=input_data.expense_id, updated_fields=[], error_code='TOOL_EXPENSE_INVALID_COST', error_message='Expense cost must be greater than zero')
        if input_data.expense_date:
            try:
                from datetime import datetime
                datetime.strptime(input_data.expense_date, '%Y-%m-%d')
            except ValueError:
                return UpdateExpenseOutput(success=False, expense_id=input_data.expense_id, updated_fields=[], error_code='TOOL_EXPENSE_INVALID_DATE', error_message='Expense date must be in YYYY-MM-DD format')
        updated_fields = []
        with db.get_conn() as conn:
            updates = []
            params = []
            if input_data.item is not None:
                updates.append('item = ?')
                params.append(input_data.item)
                updated_fields.append('item')
            if input_data.cost is not None:
                updates.append('cost = ?')
                params.append(input_data.cost)
                updated_fields.append('cost')
            if input_data.category is not None:
                updates.append('category = ?')
                params.append(input_data.category)
                updated_fields.append('category')
            if input_data.supplier is not None:
                updates.append('supplier = ?')
                params.append(input_data.supplier)
                updated_fields.append('supplier')
            if input_data.expense_date is not None:
                updates.append('expense_date = ?')
                params.append(input_data.expense_date)
                updated_fields.append('expense_date')
            if updates:
                query = f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?"
                params.append(input_data.expense_id)
                conn.execute(query, params)
        return UpdateExpenseOutput(success=True, expense_id=input_data.expense_id, updated_fields=updated_fields)

@dataclass
class DeleteExpenseInput(ToolInput):
    """Input for DeleteExpense tool"""
    expense_id: int
    reason: str

@dataclass
class DeleteExpenseOutput(ToolOutput):
    """Output for DeleteExpense tool"""
    expense_id: int = 0
    deleted: bool = False

class DeleteExpenseTool(Tool):
    """
    Delete an expense record.
    
    Risk Tier: HIGH
    - Removes financial records
    - Affects job profitability calculations
    - Requires confirmation
    """

    @property
    def input_schema(self):
        return DeleteExpenseInput

    def execute(self, input_data: DeleteExpenseInput) -> DeleteExpenseOutput:
        """Delete an expense"""
        if not input_data.reason or len(input_data.reason.strip()) < 10:
            return DeleteExpenseOutput(success=False, expense_id=input_data.expense_id, deleted=False, error_code='TOOL_EXPENSE_DELETE_INVALID_REASON', error_message='Deletion reason must be at least 10 characters')
        expenses = db.list_expenses()
        expense = next((e for e in expenses if e.get('id', 0) == input_data.expense_id), None)
        if not expense:
            return DeleteExpenseOutput(success=False, expense_id=input_data.expense_id, deleted=False, error_code='TOOL_EXPENSE_NOT_FOUND', error_message=f'Expense with ID {input_data.expense_id} not found')
        db.delete_expense(input_data.expense_id)
        return DeleteExpenseOutput(success=True, expense_id=input_data.expense_id, deleted=True)

@dataclass
class LinkExpenseToJobInput(ToolInput):
    """Input for LinkExpenseToJob tool"""
    expense_id: int
    job_id: int

@dataclass
class LinkExpenseToJobOutput(ToolOutput):
    """Output for LinkExpenseToJob tool"""
    expense_id: int = 0
    job_id: int = 0
    linked: bool = False

class LinkExpenseToJobTool(Tool):
    """
    Link an expense to a job.
    
    Risk Tier: LOW
    - Only updates linking, doesn't affect amounts
    - Improves job cost tracking
    """

    @property
    def input_schema(self):
        return LinkExpenseToJobInput

    def execute(self, input_data: LinkExpenseToJobInput) -> LinkExpenseToJobOutput:
        """Link an expense to a job"""
        expenses = db.list_expenses()
        expense = next((e for e in expenses if e.get('id', 0) == input_data.expense_id), None)
        if not expense:
            return LinkExpenseToJobOutput(success=False, expense_id=input_data.expense_id, job_id=input_data.job_id, linked=False, error_code='TOOL_EXPENSE_NOT_FOUND', error_message=f'Expense with ID {input_data.expense_id} not found')
        job = db.get_job(input_data.job_id, company_id=input_data.company_id)
        if not job:
            return LinkExpenseToJobOutput(success=False, expense_id=input_data.expense_id, job_id=input_data.job_id, linked=False, error_code='TOOL_EXPENSE_JOB_NOT_FOUND', error_message=f'Job with ID {input_data.job_id} not found')
        with db.get_conn() as conn:
            conn.execute('UPDATE expenses SET job_id = ? WHERE id = ?', (input_data.job_id, input_data.expense_id))
        return LinkExpenseToJobOutput(success=True, expense_id=input_data.expense_id, job_id=input_data.job_id, linked=True)

@dataclass
class CreateCreditNoteInput(ToolInput):
    """Input for CreateCreditNote tool"""
    invoice_id: int
    amount: float
    reason: str
    created_by: Optional[int] = None

@dataclass
class CreateCreditNoteOutput(ToolOutput):
    """Output for CreateCreditNote tool"""
    credit_note_id: int = 0
    credit_note_no: str = ''
    invoice_id: int = 0
    amount: float = 0.0

class CreateCreditNoteTool(Tool):
    """
    Create a credit note for an invoice.
    
    Risk Tier: MEDIUM
    - Creates financial credit document
    - Affects invoice balance
    - Requires proper reason
    """

    @property
    def input_schema(self):
        return CreateCreditNoteInput

    def execute(self, input_data: CreateCreditNoteInput) -> CreateCreditNoteOutput:
        """Create a credit note"""
        if input_data.amount <= 0:
            return CreateCreditNoteOutput(success=False, credit_note_id=0, credit_note_no='', invoice_id=input_data.invoice_id, amount=0, error_code='TOOL_CREDIT_NOTE_INVALID_AMOUNT', error_message='Credit note amount must be greater than zero')
        if not input_data.reason or len(input_data.reason.strip()) < 10:
            return CreateCreditNoteOutput(success=False, credit_note_id=0, credit_note_no='', invoice_id=input_data.invoice_id, amount=0, error_code='TOOL_CREDIT_NOTE_INVALID_REASON', error_message='Credit note reason must be at least 10 characters')
        try:
            with db.get_conn() as conn:
                invoice = conn.execute('SELECT * FROM invoices WHERE id = ?', (input_data.invoice_id,)).fetchone()
                if not invoice:
                    return CreateCreditNoteOutput(success=False, credit_note_id=0, credit_note_no='', invoice_id=input_data.invoice_id, amount=0, error_code='TOOL_CREDIT_NOTE_INVOICE_NOT_FOUND', error_message=f'Invoice with ID {input_data.invoice_id} not found')
                invoice_dict = dict(invoice)
                balance_due = invoice_dict.get('balance_due', 0) or 0
                if input_data.amount > balance_due:
                    return CreateCreditNoteOutput(success=False, credit_note_id=0, credit_note_no='', invoice_id=input_data.invoice_id, amount=0, error_code='TOOL_CREDIT_NOTE_EXCEEDS_BALANCE', error_message=f'Credit amount ({input_data.amount}) exceeds invoice balance ({balance_due})')
        except Exception as e:
            return CreateCreditNoteOutput(success=False, credit_note_id=0, credit_note_no='', invoice_id=input_data.invoice_id, amount=0, error_code='TOOL_CREDIT_NOTE_CREATE_FAILED', error_message=f'Failed to create credit note: {str(e)}')
        try:
            credit_note_id = db.create_credit_note(invoice_id=input_data.invoice_id, amount=input_data.amount, reason=input_data.reason, created_by=input_data.created_by)
            credit_notes = db.list_credit_notes(limit=1)
            credit_note_no = credit_notes[0].get('credit_note_no', f'CN-{credit_note_id}') if credit_notes else f'CN-{credit_note_id}'
            return CreateCreditNoteOutput(success=True, credit_note_id=credit_note_id, credit_note_no=credit_note_no, invoice_id=input_data.invoice_id, amount=input_data.amount)
        except Exception as e:
            return CreateCreditNoteOutput(success=False, credit_note_id=0, credit_note_no='', invoice_id=input_data.invoice_id, amount=0, error_code='TOOL_CREDIT_NOTE_CREATE_FAILED', error_message=f'Failed to create credit note: {str(e)}')

@dataclass
class IssueCreditNoteInput(ToolInput):
    """Input for IssueCreditNote tool"""
    credit_note_id: int
    issue_reason: str

@dataclass
class IssueCreditNoteOutput(ToolOutput):
    """Output for IssueCreditNote tool"""
    credit_note_id: int = 0
    status: str = ''
    issued: bool = False

class IssueCreditNoteTool(Tool):
    """
    Issue a credit note to the customer (finalize it).
    
    Risk Tier: HIGH
    - Finalizes credit to customer
    - Affects accounts receivable
    - Requires confirmation
    """

    @property
    def input_schema(self):
        return IssueCreditNoteInput

    def execute(self, input_data: IssueCreditNoteInput) -> IssueCreditNoteOutput:
        """Issue a credit note"""
        if not input_data.issue_reason or len(input_data.issue_reason.strip()) < 10:
            return IssueCreditNoteOutput(success=False, credit_note_id=input_data.credit_note_id, status='', issued=False, error_code='TOOL_CREDIT_NOTE_INVALID_ISSUE_REASON', error_message='Issue reason must be at least 10 characters')
        credit_notes = db.list_credit_notes(limit=100)
        credit_note = next((cn for cn in credit_notes if cn.get('id', 0) == input_data.credit_note_id), None)
        if not credit_note:
            return IssueCreditNoteOutput(success=False, credit_note_id=input_data.credit_note_id, status='', issued=False, error_code='TOOL_CREDIT_NOTE_NOT_FOUND', error_message=f'Credit note with ID {input_data.credit_note_id} not found')
        if credit_note.get('status') == 'issued':
            return IssueCreditNoteOutput(success=False, credit_note_id=input_data.credit_note_id, status='issued', issued=False, error_code='TOOL_CREDIT_NOTE_ALREADY_ISSUED', error_message='Credit note has already been issued')
        with db.get_conn() as conn:
            conn.execute("UPDATE credit_notes SET status = 'issued' WHERE id = ?", (input_data.credit_note_id,))
        return IssueCreditNoteOutput(success=True, credit_note_id=input_data.credit_note_id, status='issued', issued=True)

@dataclass
class ApplyCreditNoteInput(ToolInput):
    """Input for ApplyCreditNote tool"""
    credit_note_id: int
    invoice_id: int

@dataclass
class ApplyCreditNoteOutput(ToolOutput):
    """Output for ApplyCreditNote tool"""
    credit_note_id: int = 0
    invoice_id: int = 0
    applied: bool = False
    new_balance: float = 0.0

class ApplyCreditNoteTool(Tool):
    """
    Apply a credit note to an invoice.
    
    Risk Tier: MEDIUM
    - Adjusts invoice balance
    - Financial operation
    - Should be reversible
    """

    @property
    def input_schema(self):
        return ApplyCreditNoteInput

    def execute(self, input_data: ApplyCreditNoteInput) -> ApplyCreditNoteOutput:
        """Apply a credit note to an invoice"""
        credit_notes = db.list_credit_notes(limit=100)
        credit_note = next((cn for cn in credit_notes if cn.get('id', 0) == input_data.credit_note_id), None)
        if not credit_note:
            return ApplyCreditNoteOutput(success=False, credit_note_id=input_data.credit_note_id, invoice_id=input_data.invoice_id, applied=False, new_balance=0, error_code='TOOL_CREDIT_NOTE_NOT_FOUND', error_message=f'Credit note with ID {input_data.credit_note_id} not found')
        if credit_note.get('status') != 'issued':
            return ApplyCreditNoteOutput(success=False, credit_note_id=input_data.credit_note_id, invoice_id=input_data.invoice_id, applied=False, new_balance=0, error_code='TOOL_CREDIT_NOTE_NOT_ISSUED', error_message='Credit note must be issued before it can be applied')
        with db.get_conn() as conn:
            invoice = conn.execute('SELECT * FROM invoices WHERE id = ?', (input_data.invoice_id,)).fetchone()
            if not invoice:
                return ApplyCreditNoteOutput(success=False, credit_note_id=input_data.credit_note_id, invoice_id=input_data.invoice_id, applied=False, new_balance=0, error_code='TOOL_CREDIT_NOTE_INVOICE_NOT_FOUND', error_message=f'Invoice with ID {input_data.invoice_id} not found')
            invoice_dict = dict(invoice)
            credit_amount = credit_note.get('total_amount', 0) or 0
            current_balance = invoice_dict.get('balance_due', 0) or 0
            new_balance = max(0, current_balance - credit_amount)
            conn.execute('UPDATE invoices SET balance_due = ? WHERE id = ?', (new_balance, input_data.invoice_id))
            conn.execute("UPDATE credit_notes SET status = 'applied' WHERE id = ?", (input_data.credit_note_id,))
        return ApplyCreditNoteOutput(success=True, credit_note_id=input_data.credit_note_id, invoice_id=input_data.invoice_id, applied=True, new_balance=new_balance)

@dataclass
class VoidCreditNoteInput(ToolInput):
    """Input for VoidCreditNote tool"""
    credit_note_id: int
    void_reason: str

@dataclass
class VoidCreditNoteOutput(ToolOutput):
    """Output for VoidCreditNote tool"""
    credit_note_id: int = 0
    voided: bool = False

class VoidCreditNoteTool(Tool):
    """
    Void a credit note (cancel it).
    
    Risk Tier: HIGH
    - Cancels financial credit
    - May affect customer accounts
    - Requires confirmation and reason
    """

    @property
    def input_schema(self):
        return VoidCreditNoteInput

    def execute(self, input_data: VoidCreditNoteInput) -> VoidCreditNoteOutput:
        """Void a credit note"""
        if not input_data.void_reason or len(input_data.void_reason.strip()) < 10:
            return VoidCreditNoteOutput(success=False, credit_note_id=input_data.credit_note_id, voided=False, error_code='TOOL_CREDIT_NOTE_INVALID_VOID_REASON', error_message='Void reason must be at least 10 characters')
        credit_notes = db.list_credit_notes(limit=100)
        credit_note = next((cn for cn in credit_notes if cn.get('id', 0) == input_data.credit_note_id), None)
        if not credit_note:
            return VoidCreditNoteOutput(success=False, credit_note_id=input_data.credit_note_id, voided=False, error_code='TOOL_CREDIT_NOTE_NOT_FOUND', error_message=f'Credit note with ID {input_data.credit_note_id} not found')
        if credit_note.get('status') == 'void':
            return VoidCreditNoteOutput(success=False, credit_note_id=input_data.credit_note_id, voided=False, error_code='TOOL_CREDIT_NOTE_ALREADY_VOID', error_message='Credit note has already been voided')
        if credit_note.get('status') == 'applied':
            return VoidCreditNoteOutput(success=False, credit_note_id=input_data.credit_note_id, voided=False, error_code='TOOL_CREDIT_NOTE_ALREADY_APPLIED', error_message='Cannot void a credit note that has already been applied to an invoice')
        with db.get_conn() as conn:
            if credit_note.get('status') == 'issued':
                invoice_id = credit_note.get('invoice_id')
                credit_amount = credit_note.get('total_amount', 0) or 0
                conn.execute('UPDATE invoices SET balance_due = balance_due + ? WHERE id = ?', (credit_amount, invoice_id))
            conn.execute("UPDATE credit_notes SET status = 'void' WHERE id = ?", (input_data.credit_note_id,))
        return VoidCreditNoteOutput(success=True, credit_note_id=input_data.credit_note_id, voided=True)
