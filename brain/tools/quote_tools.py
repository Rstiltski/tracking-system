"""
Quote-related tools for the Brain system.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from brain.core.tool import Tool, ToolInput
from brain.core.result import ToolOutput
import db

@dataclass
class CreateQuoteInput(ToolInput):
    """Input for creating a new quote."""
    customer_id: int
    job_id: Optional[int] = None
    quote_date: Optional[str] = None
    valid_until: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[int] = None

class CreateQuoteTool(Tool):
    """Create a new quote for a customer."""

    @property
    def input_schema(self):
        return CreateQuoteInput

    def execute(self, input_data: CreateQuoteInput) -> ToolOutput:
        """
        Create a new quote record.
        
        Returns:
            ToolOutput with quote_id in data
        """
        try:
            customer = db.get_customer(input_data.customer_id, company_id=input_data.company_id)
            if not customer:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_CREATE_CUSTOMER_NOT_FOUND', error_message=f'Customer {input_data.customer_id} not found')
            if input_data.job_id:
                job = db.get_job(input_data.job_id, company_id=input_data.company_id)
                if not job:
                    return ToolOutput(success=False, error_code='TOOL_QUOTE_CREATE_JOB_NOT_FOUND', error_message=f'Job {input_data.job_id} not found')
            quote_id = db.create_quote(customer_id=input_data.customer_id, job_id=input_data.job_id, quote_date=input_data.quote_date, valid_until=input_data.valid_until, notes=input_data.notes, created_by=input_data.created_by)
            return ToolOutput(success=True, data={'quote_id': quote_id, 'customer_id': input_data.customer_id, 'status': 'draft'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_QUOTE_CREATE_FAILED', error_message=str(e))

@dataclass
class AddQuoteLineItemInput(ToolInput):
    """Input for adding a line item to a quote."""
    quote_id: int
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0
    vat_rate: float = 0.0
    category: Optional[str] = None
    material_id: Optional[int] = None
    unit: Optional[str] = None

class AddQuoteLineItemTool(Tool):
    """Add a line item to a quote."""

    @property
    def input_schema(self):
        return AddQuoteLineItemInput

    def execute(self, input_data: AddQuoteLineItemInput) -> ToolOutput:
        """
        Add a line item to an existing quote.
        
        Returns:
            ToolOutput with line_item_id in data
        """
        try:
            quote = db.get_quote_with_items(input_data.quote_id)
            if not quote:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_LINE_ITEM_QUOTE_NOT_FOUND', error_message=f'Quote {input_data.quote_id} not found')
            if input_data.quantity <= 0:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_LINE_ITEM_INVALID_QUANTITY', error_message='Quantity must be greater than 0')
            if input_data.unit_price < 0:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_LINE_ITEM_INVALID_PRICE', error_message='Unit price cannot be negative')
            line_item_id = db.add_quote_line_item(quote_id=input_data.quote_id, description=input_data.description, quantity=input_data.quantity, unit_price=input_data.unit_price, vat_rate=input_data.vat_rate, category=input_data.category, material_id=input_data.material_id, unit=input_data.unit)
            updated_quote = db.get_quote_with_items(input_data.quote_id)
            return ToolOutput(success=True, data={'line_item_id': line_item_id, 'quote_id': input_data.quote_id, 'quote_total': updated_quote.get('total_amount', 0)})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_QUOTE_LINE_ITEM_ADD_FAILED', error_message=str(e))

@dataclass
class SendQuoteInput(ToolInput):
    """Input for sending a quote to customer."""
    quote_id: int
    updated_by: Optional[int] = None

class SendQuoteTool(Tool):
    """Send a quote to customer (mark as sent)."""

    @property
    def input_schema(self):
        return SendQuoteInput

    def execute(self, input_data: SendQuoteInput) -> ToolOutput:
        """
        Send a quote to customer by updating status to 'sent'.
        
        Returns:
            ToolOutput with sent status
        """
        try:
            quote = db.get_quote_with_items(input_data.quote_id)
            if not quote:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_SEND_NOT_FOUND', error_message=f'Quote {input_data.quote_id} not found')
            if not quote.get('line_items') or len(quote.get('line_items', 0)) == 0:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_SEND_NO_LINE_ITEMS', error_message='Quote must have at least one line item before sending')
            if quote.get('total_amount', 0) <= 0:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_SEND_ZERO_TOTAL', error_message='Quote total must be greater than zero')
            db.update_quote_status(quote_id=input_data.quote_id, status='sent', updated_by=input_data.updated_by)
            return ToolOutput(success=True, data={'quote_id': input_data.quote_id, 'status': 'sent', 'sent_at': datetime.now().isoformat()})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_QUOTE_SEND_FAILED', error_message=str(e))

@dataclass
class AcceptQuoteInput(ToolInput):
    """Input for accepting a quote."""
    quote_id: int
    updated_by: Optional[int] = None

class AcceptQuoteTool(Tool):
    """Accept a quote (customer accepted)."""

    @property
    def input_schema(self):
        return AcceptQuoteInput

    def execute(self, input_data: AcceptQuoteInput) -> ToolOutput:
        """
        Accept a quote by updating status to 'accepted'.
        
        Returns:
            ToolOutput with accepted status
        """
        try:
            quote = db.get_quote_with_items(input_data.quote_id)
            if not quote:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_ACCEPT_NOT_FOUND', error_message=f'Quote {input_data.quote_id} not found')
            if quote.get('status') not in ['sent', 'accepted']:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_ACCEPT_INVALID_STATUS', error_message=f"Quote must be sent before it can be accepted (current status: {quote.get('status')})")
            db.update_quote_status(quote_id=input_data.quote_id, status='accepted', updated_by=input_data.updated_by)
            return ToolOutput(success=True, data={'quote_id': input_data.quote_id, 'status': 'accepted', 'accepted_at': datetime.now().isoformat()})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_QUOTE_ACCEPT_FAILED', error_message=str(e))

@dataclass
class DeclineQuoteInput(ToolInput):
    """Input for declining a quote."""
    quote_id: int
    reason: Optional[str] = None
    updated_by: Optional[int] = None

class DeclineQuoteTool(Tool):
    """Decline a quote (customer declined)."""

    @property
    def input_schema(self):
        return DeclineQuoteInput

    def execute(self, input_data: DeclineQuoteInput) -> ToolOutput:
        """
        Decline a quote by updating status to 'declined'.
        
        Returns:
            ToolOutput with declined status
        """
        try:
            quote = db.get_quote_with_items(input_data.quote_id)
            if not quote:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_DECLINE_NOT_FOUND', error_message=f'Quote {input_data.quote_id} not found')
            db.update_quote_status(quote_id=input_data.quote_id, status='declined', updated_by=input_data.updated_by)
            return ToolOutput(success=True, data={'quote_id': input_data.quote_id, 'status': 'declined', 'declined_at': datetime.now().isoformat(), 'reason': input_data.reason})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_QUOTE_DECLINE_FAILED', error_message=str(e))

@dataclass
class GetQuoteInput(ToolInput):
    """Input for retrieving a quote."""
    quote_id: int

class GetQuoteTool(Tool):
    """Retrieve quote details with line items."""

    @property
    def input_schema(self):
        return GetQuoteInput

    def execute(self, input_data: GetQuoteInput) -> ToolOutput:
        """
        Get quote details including all line items.
        
        Returns:
            ToolOutput with quote data including line items
        """
        try:
            quote = db.get_quote_with_items(input_data.quote_id)
            if not quote:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_GET_NOT_FOUND', error_message=f'Quote {input_data.quote_id} not found')
            return ToolOutput(success=True, data=quote)
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_QUOTE_GET_FAILED', error_message=str(e))

@dataclass
class ConvertQuoteToJobInput(ToolInput):
    """Input for converting accepted quote to a job."""
    quote_id: int
    job_date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    deposit_percentage: float = 0.0
    user_id: Optional[int] = None

class ConvertQuoteToJobTool(Tool):
    """Convert an accepted quote into a booked job."""

    @property
    def input_schema(self):
        return ConvertQuoteToJobInput

    def execute(self, input_data: ConvertQuoteToJobInput) -> ToolOutput:
        """
        Convert an accepted quote to a booked job.
        
        Returns:
            ToolOutput with new job_id
        """
        try:
            quote = db.get_quote_with_items(input_data.quote_id)
            if not quote:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_CONVERT_NOT_FOUND', error_message=f'Quote {input_data.quote_id} not found')
            if quote.get('status') != 'accepted':
                return ToolOutput(success=False, error_code='TOOL_QUOTE_CONVERT_NOT_ACCEPTED', error_message=f"Quote must be accepted before converting to job (current status: {quote.get('status')})")
            if input_data.deposit_percentage < 0 or input_data.deposit_percentage > 100:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_CONVERT_INVALID_DEPOSIT', error_message='Deposit percentage must be between 0 and 100')
            job_id = db.convert_quote_to_job(quote_id=input_data.quote_id, job_date=input_data.job_date, start_time=input_data.start_time, end_time=input_data.end_time, deposit_percentage=input_data.deposit_percentage, user_id=input_data.user_id)
            return ToolOutput(success=True, data={'job_id': job_id, 'quote_id': input_data.quote_id, 'job_date': input_data.job_date, 'deposit_percentage': input_data.deposit_percentage})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_QUOTE_CONVERT_FAILED', error_message=str(e))

@dataclass
class AddQuoteItemInput(ToolInput):
    """Input for adding a quote item to a job using the legacy quote_items table."""
    job_id: int
    item_type: str
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0

class AddQuoteItemTool(Tool):
    """Add a quote item to a job (legacy quote_items table)."""

    @property
    def input_schema(self):
        return AddQuoteItemInput

    def execute(self, input_data: AddQuoteItemInput) -> ToolOutput:
        """
        Add a quote item to a job using the legacy quote_items table.
        This is for backward compatibility with the existing UI.
        
        Returns:
            ToolOutput with quote_item_id in data
        """
        try:
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_ITEM_JOB_NOT_FOUND', error_message=f'Job {input_data.job_id} not found')
            valid_types = ['material', 'labour', 'travel', 'discount']
            if input_data.item_type not in valid_types:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_ITEM_INVALID_TYPE', error_message=f"Item type must be one of: {', '.join(valid_types)}")
            if not input_data.description or not input_data.description.strip():
                return ToolOutput(success=False, error_code='TOOL_QUOTE_ITEM_MISSING_DESCRIPTION', error_message='Description is required')
            if input_data.quantity <= 0:
                return ToolOutput(success=False, error_code='TOOL_QUOTE_ITEM_INVALID_QUANTITY', error_message='Quantity must be greater than 0')
            db.add_quote_item(job_id=input_data.job_id, item_type=input_data.item_type, description=input_data.description, quantity=input_data.quantity, unit_price=input_data.unit_price)
            quote_total = db.calculate_quote_total(input_data.job_id)
            db.update_job(input_data.job_id, quoted_price=quote_total)
            return ToolOutput(success=True, data={'job_id': input_data.job_id, 'item_type': input_data.item_type, 'description': input_data.description, 'quantity': input_data.quantity, 'unit_price': input_data.unit_price, 'quote_total': quote_total})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_QUOTE_ITEM_ADD_FAILED', error_message=str(e))
