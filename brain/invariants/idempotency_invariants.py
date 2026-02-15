"""
Idempotency invariants implementation.

Checks:
- I-001: Unique invoice numbers per company
- I-002: Single invoice per job
- I-003: Message deduplication (5 min window)
- I-004: Payment idempotency (1 min window)
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/03_invariants.md
- LLM_AGENT_QUICKSTART.md
"""
from brain.invariants.checker import InvariantChecker, ViolationSeverity
from typing import Dict, Any, List
from datetime import datetime, timedelta
from database.queries import invoices

class IdempotencyInvariants(InvariantChecker):
    """Idempotency invariant checks."""

    def check_unique_invoice_numbers(self, invoice: Dict[str, Any], other_invoices: List[Dict[str, Any]]) -> bool:
        """
        I-001: Check invoice numbers are unique per company.
        
        Args:
            invoice: Invoice to check
            other_invoices: List of other invoices in same company
            
        Returns:
            True if unique, False otherwise
        """
        invoice_no = invoice.get('invoice_no')
        company_id = invoice.get('company_id')
        invoice_id = invoice.get('id')
        for other in other_invoices:
            if other.get('id') == invoice_id:
                continue
            if other.get('invoice_no') == invoice_no and other.get('company_id') == company_id:
                self.add_violation(code='INV_IDEMPOTENCY_DUPLICATE_INVOICE_NO', severity=ViolationSeverity.CRITICAL, entity_type='invoice', entity_id=invoice_id, message=f'Duplicate invoice number {invoice_no} in company {company_id}', details={'invoice_no': invoice_no, 'company_id': company_id, 'invoice_id': invoice_id, 'duplicate_id': other.get('id')})
                return False
        return True

    def check_single_invoice_per_job(self, job: Dict[str, Any], invoices: List[Dict[str, Any]]) -> bool:
        """
        I-002: Check only one invoice per job.
        
        Args:
            job: Job entity
            invoices: List of invoices linked to this job
            
        Returns:
            True if single invoice, False otherwise
        """
        job_id = job.get('id', '') if job else ''
        job_invoices = [inv for inv in invoices if inv.get('job_id') == job_id]
        if len(job_invoices) > 1:
            self.add_violation(code='INV_IDEMPOTENCY_MULTIPLE_INVOICES', severity=ViolationSeverity.HIGH, entity_type='job', entity_id=job_id, message=f'Job {job_id} has {len(job_invoices)} invoices', details={'job_id': job_id, 'invoice_count': len(job_invoices), 'invoice_ids': [inv.get('id') for inv in job_invoices]})
            return False
        return True

    def check_message_deduplication(self, message: Dict[str, Any], recent_messages: List[Dict[str, Any]], window_minutes: int=5) -> bool:
        """
        I-003: Check for duplicate messages in time window.
        
        Args:
            message: Message to check
            recent_messages: List of recent messages
            window_minutes: Deduplication window in minutes
            
        Returns:
            True if unique, False if duplicate
        """
        recipient = message.get('recipient')
        body = message.get('body')
        created_at = message.get('created_at')
        if not created_at:
            return True
        try:
            msg_time = datetime.fromisoformat(created_at)
            cutoff = msg_time - timedelta(minutes=window_minutes)
            for other in recent_messages:
                if other.get('id') == message.get('id'):
                    continue
                other_time_str = other.get('created_at')
                if not other_time_str:
                    continue
                other_time = datetime.fromisoformat(other_time_str)
                if other_time >= cutoff and other.get('recipient') == recipient and (other.get('body') == body):
                    self.add_violation(code='INV_IDEMPOTENCY_DUPLICATE_MESSAGE', severity=ViolationSeverity.MEDIUM, entity_type='message', entity_id=message.get('id'), message=f'Duplicate message to {recipient} within {window_minutes} minutes', details={'message_id': message.get('id'), 'duplicate_id': other.get('id'), 'recipient': recipient, 'time_diff_seconds': (msg_time - other_time).total_seconds()})
                    return False
        except (ValueError, TypeError):
            pass
        return True

    def check_payment_idempotency(self, payment: Dict[str, Any], recent_payments: List[Dict[str, Any]], window_minutes: int=1) -> bool:
        """
        I-004: Check for duplicate payments in time window.
        
        Args:
            payment: Payment to check
            recent_payments: List of recent payments
            window_minutes: Deduplication window in minutes
            
        Returns:
            True if unique, False if duplicate
        """
        invoice_id = payment.get('invoice_id')
        amount = payment.get('amount')
        created_at = payment.get('created_at')
        if not created_at:
            return True
        try:
            payment_time = datetime.fromisoformat(created_at)
            cutoff = payment_time - timedelta(minutes=window_minutes)
            for other in recent_payments:
                if other.get('id') == payment.get('id'):
                    continue
                other_time_str = other.get('created_at')
                if not other_time_str:
                    continue
                other_time = datetime.fromisoformat(other_time_str)
                if other_time >= cutoff and other.get('invoice_id') == invoice_id and (abs(other.get('amount', 0) - amount) < 0.01):
                    self.add_violation(code='INV_IDEMPOTENCY_DUPLICATE_PAYMENT', severity=ViolationSeverity.CRITICAL, entity_type='payment', entity_id=payment.get('id'), message=f'Duplicate payment of {amount} for invoice {invoice_id} within {window_minutes} minute(s)', details={'payment_id': payment.get('id'), 'duplicate_id': other.get('id'), 'invoice_id': invoice_id, 'amount': amount, 'time_diff_seconds': (payment_time - other_time).total_seconds()})
                    return False
        except (ValueError, TypeError):
            pass
        return True