"""
Money invariants implementation.

Checks:
- M-001: Invoice balance consistency
- M-002: Payment non-negativity
- M-003: Payment doesn't exceed invoice
- M-004: Refund doesn't exceed payment
- M-005: Deposit consistency
- M-006: Credit note validity
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/03_invariants.md
- LLM_AGENT_QUICKSTART.md
"""
from brain.invariants.checker import InvariantChecker, ViolationSeverity
from typing import Dict, Any

class MoneyInvariants(InvariantChecker):
    """Money-related invariant checks."""

    def check_invoice_balance_consistency(self, invoice: Dict[str, Any]) -> bool:
        """
        M-001: Check invoice.balance_due = invoice.total_amount - invoice.paid_amount
        
        Args:
            invoice: Invoice entity with total_amount, paid_amount, balance_due
            
        Returns:
            True if consistent, False otherwise
        """
        total = invoice.get('total_amount', 0)
        paid = invoice.get('paid_amount', 0)
        balance = invoice.get('balance_due', 0)
        expected_balance = total - paid
        if abs(balance - expected_balance) > 0.01:
            self.add_violation(code='INV_MONEY_BALANCE_MISMATCH', severity=ViolationSeverity.CRITICAL, entity_type='invoice', entity_id=invoice.get('id'), message=f'Invoice balance mismatch: expected {expected_balance}, got {balance}', details={'total_amount': total, 'paid_amount': paid, 'balance_due': balance, 'expected_balance': expected_balance})
            return False
        return True

    def check_payment_non_negativity(self, entity: Dict[str, Any], entity_type: str) -> bool:
        """
        M-002: Check that all money amounts are non-negative.
        
        Args:
            entity: Invoice or Payment entity
            entity_type: "invoice" or "payment"
            
        Returns:
            True if all amounts non-negative, False otherwise
        """
        if entity_type == 'invoice':
            checks = [('total_amount', entity.get('total_amount', 0)), ('paid_amount', entity.get('paid_amount', 0)), ('balance_due', entity.get('balance_due', 0))]
        elif entity_type == 'payment':
            checks = [('amount', entity.get('amount', 0))]
        else:
            return True
        for field_name, value in checks:
            if value < 0:
                self.add_violation(code='INV_MONEY_NEGATIVE_VALUE', severity=ViolationSeverity.CRITICAL, entity_type=entity_type, entity_id=entity.get('id'), message=f'Negative value found: {field_name} = {value}', details={field_name: value})
                return False
        return True

    def check_payment_not_exceed_invoice(self, payment_amount: float, invoice: Dict[str, Any]) -> bool:
        """
        M-003: Check that payment doesn't exceed remaining invoice balance.
        
        Args:
            payment_amount: Amount being paid
            invoice: Invoice entity
            
        Returns:
            True if payment valid, False otherwise
        """
        total = invoice.get('total_amount', 0)
        paid = invoice.get('paid_amount', 0)
        remaining = total - paid
        if payment_amount > remaining + 0.01:
            self.add_violation(code='INV_MONEY_OVERPAYMENT', severity=ViolationSeverity.CRITICAL, entity_type='payment', entity_id=None, message=f'Payment {payment_amount} exceeds remaining balance {remaining}', details={'payment_amount': payment_amount, 'invoice_total': total, 'invoice_paid': paid, 'remaining_balance': remaining, 'overpayment': payment_amount - remaining})
            return False
        return True

    def check_refund_not_exceed_payment(self, refund_amount: float, payment: Dict[str, Any]) -> bool:
        """
        M-004: Check that refund doesn't exceed payment amount.
        
        Args:
            refund_amount: Amount being refunded
            payment: Payment entity
            
        Returns:
            True if refund valid, False otherwise
        """
        payment_amount = payment.get('amount', 0)
        if refund_amount > payment_amount:
            self.add_violation(code='INV_MONEY_EXCESSIVE_REFUND', severity=ViolationSeverity.CRITICAL, entity_type='refund', entity_id=None, message=f'Refund {refund_amount} exceeds payment {payment_amount}', details={'refund_amount': refund_amount, 'payment_amount': payment_amount, 'excess': refund_amount - payment_amount})
            return False
        return True

    def check_deposit_consistency(self, job: Dict[str, Any]) -> bool:
        """
        M-005: Check deposit doesn't exceed quoted price.
        
        Args:
            job: Job entity
            
        Returns:
            True if consistent, False otherwise
        """
        deposit = job.get('deposit', 0) if job else 0
        quoted_price = job.get('quoted_price', 0) if job else 0
        if deposit > quoted_price:
            self.add_violation(code='INV_MONEY_DEPOSIT_MISMATCH', severity=ViolationSeverity.HIGH, entity_type='job', entity_id=job.get('id', '') if job else '', message=f'Deposit {deposit} exceeds quoted price {quoted_price}', details={'deposit': deposit, 'quoted_price': quoted_price, 'excess': deposit - quoted_price})
            return False
        return True

    def check_credit_note_validity(self, credit_amount: float, invoice: Dict[str, Any]) -> bool:
        """
        M-006: Check credit note doesn't exceed invoice total.
        
        Args:
            credit_amount: Amount of credit note
            invoice: Original invoice
            
        Returns:
            True if valid, False otherwise
        """
        if credit_amount <= 0:
            self.add_violation(code='INV_MONEY_INVALID_CREDIT', severity=ViolationSeverity.HIGH, entity_type='credit_note', entity_id=None, message=f'Credit note amount must be positive, got {credit_amount}', details={'credit_amount': credit_amount})
            return False
        invoice_total = invoice.get('total_amount', 0)
        if credit_amount > invoice_total:
            self.add_violation(code='INV_MONEY_EXCESSIVE_CREDIT', severity=ViolationSeverity.HIGH, entity_type='credit_note', entity_id=None, message=f'Credit {credit_amount} exceeds invoice total {invoice_total}', details={'credit_amount': credit_amount, 'invoice_total': invoice_total, 'excess': credit_amount - invoice_total})
            return False
        return True