"""
Integrity Policy - Data consistency and business rules
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/02_policy_packs.md
- LLM_AGENT_QUICKSTART.md
"""
from brain.core.command_event import CommandEvent
from brain.core.result import PolicyResult
import db

class IntegrityPolicy:
    """
    Integrity Policy checks:
    - INT-001: Entity existence
    - INT-002: Required fields
    - INT-003: Field validation
    - INT-004: Money consistency
    - INT-005: Job-invoice linkage
    - INT-006: Idempotency check
    """
    REQUIRED_FIELDS = {'JobCreate': ['customer_id', 'title', 'job_type'], 'CustomerCreate': ['name', 'phone'], 'InvoiceCreate': ['job_id', 'invoice_no', 'total'], 'PaymentRecord': ['invoice_id', 'amount', 'payment_method'], 'QuoteCreate': ['customer_id'], 'AddQuoteLineItem': ['quote_id', 'description'], 'QuoteSend': ['quote_id'], 'QuoteAccept': ['quote_id'], 'QuoteDecline': ['quote_id'], 'QuoteConvertToJob': ['quote_id', 'job_date']}

    def check(self, event: CommandEvent) -> PolicyResult:
        """Check integrity policies"""
        result = self._check_entity_exists(event)
        if result.is_denied:
            return result
        result = self._check_required_fields(event)
        if result.is_denied:
            return result
        result = self._check_field_validation(event)
        if result.is_denied:
            return result
        result = self._check_money_consistency(event)
        if result.is_denied:
            return result
        result = self._check_idempotency(event)
        if result.is_duplicate:
            return result
        return PolicyResult.allow()

    def _check_entity_exists(self, event: CommandEvent) -> PolicyResult:
        """INT-001: Ensure referenced entities exist"""
        params = event.params
        if 'Job' in event.command_type and 'job_id' in params:
            job_id = params.get('job_id', 0)
            job = db.get_job(job_id)
            if not job:
                return PolicyResult.deny(f'Job {job_id} does not exist', 'INT_JOB_NOT_FOUND')
        if 'customer_id' in params:
            customer_id = params.get('customer_id', 0)
            customer = db.get_customer(customer_id)
            if not customer:
                return PolicyResult.deny(f'Customer {customer_id} does not exist', 'INT_CUSTOMER_NOT_FOUND')
        if 'Invoice' in event.command_type and 'invoice_id' in params:
            invoice_id = params.get('invoice_id', 0)
            invoice = db.get_invoice(invoice_id)
            if not invoice:
                return PolicyResult.deny(f'Invoice {invoice_id} does not exist', 'INT_INVOICE_NOT_FOUND')
        return PolicyResult.allow()

    def _check_required_fields(self, event: CommandEvent) -> PolicyResult:
        """INT-002: Ensure all required fields are present"""
        required = self.REQUIRED_FIELDS.get(event.command_type, [])
        for field in required:
            if field not in event.params or event.params[field] is None:
                return PolicyResult.deny(f'Required field missing: {field}', 'INT_MISSING_REQUIRED_FIELD')
        return PolicyResult.allow()

    def _check_field_validation(self, event: CommandEvent) -> PolicyResult:
        """INT-003: Validate field formats and ranges"""
        params = event.params
        if 'amount' in params:
            amount = params.get('amount', 0)
            if amount is not None and amount <= 0:
                return PolicyResult.deny('Amount must be positive', 'INT_INVALID_AMOUNT')
        if 'quoted_price' in params:
            price = params.get('quoted_price', 0)
            if price is not None and price <= 0:
                return PolicyResult.deny('Price must be positive', 'INT_INVALID_PRICE')
        return PolicyResult.allow()

    def _check_money_consistency(self, event: CommandEvent) -> PolicyResult:
        """INT-004: Ensure financial operations are valid"""
        if event.command_type == 'PaymentRecord':
            invoice_id = event.params.get('invoice_id')
            amount = event.params.get('amount')
            if invoice_id and amount:
                invoice = db.get_invoice(invoice_id)
                if invoice:
                    remaining = invoice.get('total_amount', 0) - invoice.get('paid_amount', 0)
                    if amount > remaining:
                        return PolicyResult.deny(f'Payment amount {amount} exceeds remaining balance {remaining}', 'INT_MONEY_OVERPAYMENT')
        return PolicyResult.allow()

    def _check_idempotency(self, event: CommandEvent) -> PolicyResult:
        """INT-006: Prevent duplicate command execution"""
        if not event.idempotency_key:
            return PolicyResult.allow()
        from brain.audit import AuditLogger
        audit_logger = AuditLogger()
        existing = audit_logger.get_command_by_idempotency_key(event.command_type, event.idempotency_key)
        if existing:
            return PolicyResult.duplicate(existing.get('result_data'))
        return PolicyResult.allow()