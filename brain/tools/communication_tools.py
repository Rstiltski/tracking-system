"""
Communication tools for the Brain system.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from brain.core.tool import Tool, ToolInput
from brain.core.result import ToolOutput
import db
from services import notifications
from brand import format_money
from brain.tools.decorators import register_tool

@dataclass
class SendMessageInput(ToolInput):
    """Input for sending a single message (SMS/Email)."""
    customer_id: int
    channel: str
    subject: Optional[str] = None
    message_body: str = ''
    template_name: Optional[str] = None
    job_id: Optional[int] = None
    html_content: Optional[str] = None

@register_tool(name="SendMessage", risk="Low", category="communication")
class SendMessageTool(Tool):
    """Send a single message (SMS or Email) to a customer."""

    @property
    def input_schema(self):
        return SendMessageInput

    def execute(self, input_data: SendMessageInput) -> ToolOutput:
        """
        Send a message to a customer via SMS, Email, or both.
        
        Returns:
            ToolOutput with message_ids and status in data
        """
        try:
            customer = db.get_customer(input_data.customer_id, company_id=input_data.company_id)
            if not customer:
                return ToolOutput(success=False, error_code='TOOL_COMM_SEND_CUSTOMER_NOT_FOUND', error_message=f'Customer {input_data.customer_id} not found')
            customer = dict(customer)  # Convert sqlite3.Row to dict
            if not input_data.message_body:
                return ToolOutput(success=False, error_code='TOOL_COMM_SEND_EMPTY_MESSAGE', error_message='Message body cannot be empty')
            valid_channels = ['sms', 'email', 'both']
            if input_data.channel.lower() not in valid_channels:
                return ToolOutput(success=False, error_code='TOOL_COMM_SEND_INVALID_CHANNEL', error_message=f"Invalid channel: {input_data.channel}. Must be one of: {', '.join(valid_channels)}")
            customer_phone = customer.get('phone', '') or customer.get('mobile_phone', '')
            customer_email = customer.get('email', '')
            if input_data.channel.lower() in ['sms', 'both'] and (not customer_phone):
                return ToolOutput(success=False, error_code='TOOL_COMM_SEND_NO_PHONE', error_message=f"Customer {customer.get('name', 'Unknown')} has no phone number")
            if input_data.channel.lower() in ['email', 'both'] and (not customer_email):
                return ToolOutput(success=False, error_code='TOOL_COMM_SEND_NO_EMAIL', error_message=f"Customer {customer.get('name', 'Unknown')} has no email address")
            if input_data.channel.lower() == 'email' and (not input_data.subject):
                return ToolOutput(success=False, error_code='TOOL_COMM_SEND_NO_SUBJECT', error_message="Email subject is required when channel is 'email'")
            results = {}
            if input_data.channel.lower() in ['sms', 'both']:
                sms_success = notifications.send_notification(channel='sms', to=customer_phone, subject='', body=input_data.message_body, template=input_data.template_name or 'custom', job_id=input_data.job_id, customer_id=input_data.customer_id)
                results['sms'] = 'sent' if sms_success else 'failed'
            if input_data.channel.lower() in ['email', 'both']:
                email_success = notifications.send_notification(channel='email', to=customer_email, subject=input_data.subject or 'Message from Landscaping Services', body=input_data.message_body, template=input_data.template_name or 'custom', job_id=input_data.job_id, customer_id=input_data.customer_id, html_content=input_data.html_content)
                results['email'] = 'sent' if email_success else 'failed'
            all_sent = all((status == 'sent' for status in results.values()))
            any_sent = any((status == 'sent' for status in results.values()))
            if all_sent:
                return ToolOutput(success=True, data={'customer_id': input_data.customer_id, 'customer_name': customer.get('name', ''), 'results': results, 'sent_at': datetime.now().isoformat()})
            elif any_sent:
                return ToolOutput(success=True, data={'customer_id': input_data.customer_id, 'customer_name': customer.get('name', ''), 'results': results, 'sent_at': datetime.now().isoformat(), 'warning': 'Some messages failed to send'})
            else:
                return ToolOutput(success=False, error_code='TOOL_COMM_SEND_ALL_FAILED', error_message='All message delivery attempts failed')
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_COMM_SEND_FAILED', error_message=str(e))

@dataclass
class SendBulkMessageInput(ToolInput):
    """Input for sending bulk messages to multiple customers."""
    customer_ids: List[int]
    channel: str
    subject: Optional[str] = None
    message_body: str = ''
    template_name: Optional[str] = None
    html_content: Optional[str] = None

@register_tool(name="SendBulkMessage", risk="High", category="communication")
class SendBulkMessageTool(Tool):
    """Send bulk messages to multiple customers (HIGH risk - requires confirmation)."""

    @property
    def input_schema(self):
        return SendBulkMessageInput

    def execute(self, input_data: SendBulkMessageInput) -> ToolOutput:
        """
        Send bulk messages to multiple customers.
        
        HIGH RISK: Requires confirmation before execution.
        
        Returns:
            ToolOutput with send results for each customer
        """
        try:
            if not input_data.customer_ids:
                return ToolOutput(success=False, error_code='TOOL_COMM_BULK_NO_RECIPIENTS', error_message='No customer IDs provided')
            if not input_data.message_body:
                return ToolOutput(success=False, error_code='TOOL_COMM_BULK_EMPTY_MESSAGE', error_message='Message body cannot be empty')
            if input_data.channel.lower() not in ['sms', 'email']:
                return ToolOutput(success=False, error_code='TOOL_COMM_BULK_INVALID_CHANNEL', error_message=f"Invalid channel: {input_data.channel}. Must be 'sms' or 'email'")
            if input_data.channel.lower() == 'email' and (not input_data.subject):
                return ToolOutput(success=False, error_code='TOOL_COMM_BULK_NO_SUBJECT', error_message='Email subject is required for bulk email')
            results = []
            success_count = 0
            fail_count = 0
            for customer_id in input_data.customer_ids:
                customer = db.get_customer(customer_id, company_id=input_data.company_id)
                if not customer:
                    results.append({'customer_id': customer_id, 'status': 'failed', 'error': 'Customer not found'})
                    fail_count += 1
                    continue
                customer = dict(customer)  # Convert to dict
                if input_data.channel.lower() == 'sms':
                    contact = customer.get('phone', '') or customer.get('mobile_phone', '')
                else:
                    contact = customer.get('email', '')
                if not contact:
                    results.append({'customer_id': customer_id, 'customer_name': customer.get('name', 'Unknown'), 'status': 'failed', 'error': f'No {input_data.channel} contact info'})
                    fail_count += 1
                    continue
                send_success = notifications.send_notification(channel=input_data.channel.lower(), to=contact, subject=input_data.subject or '', body=input_data.message_body, template=input_data.template_name or 'bulk', customer_id=customer_id, html_content=input_data.html_content)
                results.append({'customer_id': customer_id, 'customer_name': customer.get('name', 'Unknown'), 'status': 'sent' if send_success else 'failed'})
                if send_success:
                    success_count += 1
                else:
                    fail_count += 1
            return ToolOutput(success=True, data={'total_recipients': len(input_data.customer_ids), 'success_count': success_count, 'fail_count': fail_count, 'channel': input_data.channel, 'results': results, 'sent_at': datetime.now().isoformat()})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_COMM_BULK_FAILED', error_message=str(e))

@dataclass
class ScheduleMessageInput(ToolInput):
    """Input for scheduling a message for later delivery."""
    customer_id: int
    channel: str
    message_body: str
    scheduled_for: str
    subject: Optional[str] = None
    template_name: Optional[str] = None
    job_id: Optional[int] = None

@register_tool(name="ScheduleMessage", risk="Low", category="communication")
class ScheduleMessageTool(Tool):
    """Schedule a message for later delivery."""

    @property
    def input_schema(self):
        return ScheduleMessageInput

    def execute(self, input_data: ScheduleMessageInput) -> ToolOutput:
        """
        Schedule a message for later delivery.
        
        Returns:
            ToolOutput with scheduled_message_id in data
        """
        try:
            customer = db.get_customer(input_data.customer_id, company_id=input_data.company_id)
            if not customer:
                return ToolOutput(success=False, error_code='TOOL_COMM_SCHEDULE_CUSTOMER_NOT_FOUND', error_message=f'Customer {input_data.customer_id} not found')
            customer = dict(customer)  # Convert to dict
            if not input_data.message_body:
                return ToolOutput(success=False, error_code='TOOL_COMM_SCHEDULE_EMPTY_MESSAGE', error_message='Message body cannot be empty')
            try:
                scheduled_dt = datetime.fromisoformat(input_data.scheduled_for)
                min_schedule_time = datetime.now() - timedelta(seconds=1)
                if scheduled_dt <= min_schedule_time:
                    return ToolOutput(success=False, error_code='TOOL_COMM_SCHEDULE_PAST_TIME', error_message='Scheduled time must be in the future')
            except ValueError:
                return ToolOutput(success=False, error_code='TOOL_COMM_SCHEDULE_INVALID_TIME', error_message=f'Invalid datetime format: {input_data.scheduled_for}')
            if input_data.channel.lower() not in ['sms', 'email']:
                return ToolOutput(success=False, error_code='TOOL_COMM_SCHEDULE_INVALID_CHANNEL', error_message=f'Invalid channel: {input_data.channel}')
            if input_data.channel.lower() == 'sms':
                contact = customer.get('phone', '') or customer.get('mobile_phone', '')
            else:
                contact = customer.get('email', '')
            if not contact:
                return ToolOutput(success=False, error_code='TOOL_COMM_SCHEDULE_NO_CONTACT', error_message=f'Customer has no {input_data.channel} contact info')
            return ToolOutput(success=True, data={'customer_id': input_data.customer_id, 'customer_name': customer.get('name', 'Unknown'), 'channel': input_data.channel, 'scheduled_for': input_data.scheduled_for, 'status': 'scheduled', 'message': 'Message scheduled successfully (requires background job processor)'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_COMM_SCHEDULE_FAILED', error_message=str(e))

@dataclass
class CancelMessageInput(ToolInput):
    """Input for canceling a scheduled message."""
    scheduled_message_id: int

@register_tool(name="CancelMessage", risk="Low", category="communication")
class CancelMessageTool(Tool):
    """Cancel a scheduled message before it's sent."""

    @property
    def input_schema(self):
        return CancelMessageInput

    def execute(self, input_data: CancelMessageInput) -> ToolOutput:
        """
        Cancel a scheduled message.
        
        Returns:
            ToolOutput with cancellation status
        """
        try:
            return ToolOutput(success=True, data={'scheduled_message_id': input_data.scheduled_message_id, 'status': 'cancelled', 'message': 'Message cancelled successfully (requires scheduled_messages table)'})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_COMM_CANCEL_FAILED', error_message=str(e))

@dataclass
class SendInvoiceEmailInput(ToolInput):
    """Input for sending invoice via email."""
    invoice_id: int
    custom_message: Optional[str] = None

@register_tool(name="SendInvoiceEmail", risk="Low", category="communication")
class SendInvoiceEmailTool(Tool):
    """Send invoice to customer via email."""

    @property
    def input_schema(self):
        return SendInvoiceEmailInput

    def execute(self, input_data: SendInvoiceEmailInput) -> ToolOutput:
        """
        Send invoice via email to customer.
        
        Returns:
            ToolOutput with send status
        """
        try:
            invoice = db.get_invoice(input_data.invoice_id)
            if not invoice:
                return ToolOutput(success=False, error_code='TOOL_COMM_INVOICE_EMAIL_NOT_FOUND', error_message=f'Invoice {input_data.invoice_id} not found')
            invoice = dict(invoice)  # Convert to dict
            customer_id = invoice.get('customer_id')
            customer = db.get_customer(customer_id, company_id=input_data.company_id)
            if not customer:
                return ToolOutput(success=False, error_code='TOOL_COMM_INVOICE_EMAIL_CUSTOMER_NOT_FOUND', error_message=f'Customer {customer_id} not found')
            customer = dict(customer)  # Convert to dict
            customer_email = customer.get('email', '')
            if not customer_email:
                return ToolOutput(success=False, error_code='TOOL_COMM_INVOICE_EMAIL_NO_EMAIL', error_message=f"Customer {customer.get('name', 'Unknown')} has no email address")
            invoice_no = invoice.get('invoice_no', f'INV-{input_data.invoice_id}')
            total = invoice.get('total', 0.0)
            subject = f'Invoice {invoice_no}'
            message_body = input_data.custom_message or f"\nDear {customer.get('name', 'Customer')},\n\nThank you for your business. Please find your invoice attached.\n\nInvoice Number: {invoice_no}\nTotal Amount: {format_money(total)}\n\nIf you have any questions, please don't hesitate to contact us.\n\nThank you for choosing our services!\n"
            success = notifications.send_notification(channel='email', to=customer_email, subject=subject, body=message_body, template='invoice_email', customer_id=customer_id, job_id=invoice.get('job_id'))
            if success:
                return ToolOutput(success=True, data={'invoice_id': input_data.invoice_id, 'invoice_no': invoice_no, 'customer_id': customer_id, 'customer_email': customer_email, 'sent_at': datetime.now().isoformat()})
            else:
                return ToolOutput(success=False, error_code='TOOL_COMM_INVOICE_EMAIL_SEND_FAILED', error_message='Failed to send invoice email')
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_COMM_INVOICE_EMAIL_FAILED', error_message=str(e))

@dataclass
class SendQuoteEmailInput(ToolInput):
    """Input for sending quote via email."""
    quote_id: int
    custom_message: Optional[str] = None

@register_tool(name="SendQuoteEmail", risk="Low", category="communication")
class SendQuoteEmailTool(Tool):
    """Send quote to customer via email."""

    @property
    def input_schema(self):
        return SendQuoteEmailInput

    def execute(self, input_data: SendQuoteEmailInput) -> ToolOutput:
        """
        Send quote via email to customer.
        
        Returns:
            ToolOutput with send status
        """
        try:
            quote = db.get_quote(input_data.quote_id)
            if not quote:
                return ToolOutput(success=False, error_code='TOOL_COMM_QUOTE_EMAIL_NOT_FOUND', error_message=f'Quote {input_data.quote_id} not found')
            quote = dict(quote)  # Convert to dict
            customer_id = quote.get('customer_id')
            customer = db.get_customer(customer_id, company_id=input_data.company_id)
            if not customer:
                return ToolOutput(success=False, error_code='TOOL_COMM_QUOTE_EMAIL_CUSTOMER_NOT_FOUND', error_message=f'Customer {customer_id} not found')
            customer = dict(customer)  # Convert to dict
            customer_email = customer.get('email', '')
            if not customer_email:
                return ToolOutput(success=False, error_code='TOOL_COMM_QUOTE_EMAIL_NO_EMAIL', error_message=f"Customer {customer.get('name', 'Unknown')} has no email address")
            quote_no = f'Q-{input_data.quote_id}'
            total = quote.get('total', 0.0)
            subject = f'Quote {quote_no}'
            message_body = input_data.custom_message or f"\nDear {customer.get('name', 'Customer')},\n\nThank you for your interest in our services. Please find your quote attached.\n\nQuote Number: {quote_no}\nTotal Amount: {format_money(total)}\nValid Until: {quote.get('valid_until', 'Contact us')}\n\nWe look forward to working with you!\n"
            success = notifications.send_notification(channel='email', to=customer_email, subject=subject, body=message_body, template='quote_email', customer_id=customer_id, job_id=quote.get('job_id'))
            if success:
                try:
                    if quote.get('status') == 'draft':
                        db.update_quote_status(input_data.quote_id, 'sent')
                except Exception as e:
                    print(f'Warning: Quote status update failed after successful send: {e}')
                return ToolOutput(success=True, data={'quote_id': input_data.quote_id, 'quote_no': quote_no, 'customer_id': customer_id, 'customer_email': customer_email, 'sent_at': datetime.now().isoformat()})
            else:
                return ToolOutput(success=False, error_code='TOOL_COMM_QUOTE_EMAIL_SEND_FAILED', error_message='Failed to send quote email')
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_COMM_QUOTE_EMAIL_FAILED', error_message=str(e))

@dataclass
class SendJobConfirmationInput(ToolInput):
    """Input for sending job confirmation to customer."""
    job_id: int
    custom_message: Optional[str] = None

@register_tool(name="SendJobConfirmation", risk="Low", category="communication")
class SendJobConfirmationTool(Tool):
    """Send job booking confirmation to customer."""

    @property
    def input_schema(self):
        return SendJobConfirmationInput

    def execute(self, input_data: SendJobConfirmationInput) -> ToolOutput:
        """
        Send job booking confirmation via SMS and/or Email.
        
        Returns:
            ToolOutput with send status
        """
        try:
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(success=False, error_code='TOOL_COMM_JOB_CONFIRM_NOT_FOUND', error_message=f'Job {input_data.job_id} not found')
            job = dict(job)  # Convert to dict
            customer_id = job.get('customer_id', '')
            customer = db.get_customer(customer_id, company_id=input_data.company_id)
            if not customer:
                return ToolOutput(success=False, error_code='TOOL_COMM_JOB_CONFIRM_CUSTOMER_NOT_FOUND', error_message=f'Customer {customer_id} not found')
            customer = dict(customer)  # Convert to dict
            customer_phone = customer.get('phone', '') or customer.get('mobile_phone', '')
            customer_email = customer.get('email', '')
            if not customer_phone and (not customer_email):
                return ToolOutput(success=False, error_code='TOOL_COMM_JOB_CONFIRM_NO_CONTACT', error_message=f"Customer {customer.get('name', 'Unknown')} has no contact information")
            job_title = job.get('title', 'Job')
            job_date = job.get('scheduled_date', 'TBD')
            message_body = input_data.custom_message or f"\nHi {customer.get('name', 'Customer')}!\n\nYour job has been confirmed:\n\nJob: {job_title}\nDate: {job_date}\n\nWe look forward to serving you!\n"
            results = {}
            if customer_phone:
                sms_success = notifications.send_notification(channel='sms', to=customer_phone, subject='', body=message_body, template='job_confirmation', job_id=input_data.job_id, customer_id=customer_id)
                results['sms'] = 'sent' if sms_success else 'failed'
            if customer_email:
                email_success = notifications.send_notification(channel='email', to=customer_email, subject=f'Job Confirmed - {job_title}', body=message_body, template='job_confirmation', job_id=input_data.job_id, customer_id=customer_id)
                results['email'] = 'sent' if email_success else 'failed'
            any_sent = any((status == 'sent' for status in results.values()))
            if any_sent:
                return ToolOutput(success=True, data={'job_id': input_data.job_id, 'customer_id': customer_id, 'results': results, 'sent_at': datetime.now().isoformat()})
            else:
                return ToolOutput(success=False, error_code='TOOL_COMM_JOB_CONFIRM_SEND_FAILED', error_message='Failed to send job confirmation')
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_COMM_JOB_CONFIRM_FAILED', error_message=str(e))

@dataclass
class SendJobReminderInput(ToolInput):
    """Input for sending job reminder to customer."""
    job_id: int
    custom_message: Optional[str] = None

@register_tool(name="SendJobReminder", risk="Low", category="communication")
class SendJobReminderTool(Tool):
    """Send job reminder to customer."""

    @property
    def input_schema(self):
        return SendJobReminderInput

    def execute(self, input_data: SendJobReminderInput) -> ToolOutput:
        """
        Send job reminder via SMS and/or Email.
        
        Returns:
            ToolOutput with send status
        """
        try:
            job = db.get_job(input_data.job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(success=False, error_code='TOOL_COMM_JOB_REMINDER_NOT_FOUND', error_message=f'Job {input_data.job_id} not found')
            job = dict(job)  # Convert to dict
            customer_id = job.get('customer_id', '')
            customer = db.get_customer(customer_id, company_id=input_data.company_id)
            if not customer:
                return ToolOutput(success=False, error_code='TOOL_COMM_JOB_REMINDER_CUSTOMER_NOT_FOUND', error_message=f'Customer {customer_id} not found')
            customer = dict(customer)  # Convert to dict
            customer_phone = customer.get('phone', '') or customer.get('mobile_phone', '')
            customer_email = customer.get('email', '')
            if not customer_phone and (not customer_email):
                return ToolOutput(success=False, error_code='TOOL_COMM_JOB_REMINDER_NO_CONTACT', error_message=f"Customer {customer.get('name', 'Unknown')} has no contact information")
            job_title = job.get('title', 'Job')
            job_date = job.get('scheduled_date', 'TBD')
            message_body = input_data.custom_message or f'\nReminder: Your scheduled job\n\nJob: {job_title}\nDate: {job_date}\n\nWe look forward to seeing you!\n'
            results = {}
            if customer_phone:
                sms_success = notifications.send_notification(channel='sms', to=customer_phone, subject='', body=message_body, template='job_reminder', job_id=input_data.job_id, customer_id=customer_id)
                results['sms'] = 'sent' if sms_success else 'failed'
            if customer_email:
                email_success = notifications.send_notification(channel='email', to=customer_email, subject=f'Reminder - {job_title}', body=message_body, template='job_reminder', job_id=input_data.job_id, customer_id=customer_id)
                results['email'] = 'sent' if email_success else 'failed'
            any_sent = any((status == 'sent' for status in results.values()))
            if any_sent:
                return ToolOutput(success=True, data={'job_id': input_data.job_id, 'customer_id': customer_id, 'results': results, 'sent_at': datetime.now().isoformat()})
            else:
                return ToolOutput(success=False, error_code='TOOL_COMM_JOB_REMINDER_SEND_FAILED', error_message='Failed to send job reminder')
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_COMM_JOB_REMINDER_FAILED', error_message=str(e))
