"""
Payment state machine implementation.

States: PENDING → CLEARED / FAILED / REFUNDED
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/01_state_machines.md
- LLM_AGENT_QUICKSTART.md
"""

from brain.state.machine import StateMachine
from typing import Dict, Any


class PaymentStateMachine(StateMachine):
    """
    Payment lifecycle state machine.
    
    Enforces valid state transitions for payments from recording to completion.
    """
    
    def __init__(self):
        super().__init__()
        self._setup_states()
        self._setup_transitions()
    
    def _setup_states(self):
        """Define all payment states."""
        # Non-terminal states
        self.add_state("PENDING")
        
        # Terminal states
        self.add_state("CLEARED", terminal=True)
        self.add_state("FAILED", terminal=True)
        self.add_state("REFUNDED", terminal=True)
    
    def _setup_transitions(self):
        """Define all valid payment state transitions."""
        
        # PENDING → CLEARED
        self.add_transition(
            "PENDING", "CLEARED", "PaymentConfirm",
            preconditions=[],
            side_effects=[
                self._set_cleared_timestamp,
                self._apply_to_invoice,
                self._update_invoice_state,
                self._send_receipt
            ]
        )
        
        # PENDING → FAILED
        self.add_transition(
            "PENDING", "FAILED", "PaymentFail",
            preconditions=[],
            side_effects=[
                self._set_failed_timestamp,
                self._record_failure_reason,
                self._notify_customer,
                self._create_follow_up
            ]
        )
        
        # CLEARED → REFUNDED
        self.add_transition(
            "CLEARED", "REFUNDED", "PaymentRefund",
            preconditions=[
                self._has_refund_reason,
                self._is_admin,
                self._refund_amount_valid
            ],
            side_effects=[
                self._set_refunded_timestamp,
                self._record_refund_reason,
                self._process_refund,
                self._update_invoice_balance,
                self._send_refund_receipt
            ]
        )
    
    # Precondition methods
    
    def _has_refund_reason(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if refund reason is provided (min 20 chars)."""
        reason = context.get("refund_reason", "")
        return len(reason) >= 20
    
    def _is_admin(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if user is admin."""
        return context.get("admin_override", False)
    
    def _refund_amount_valid(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if refund amount doesn't exceed payment amount."""
        refund_amount = context.get("refund_amount", 0)
        payment_amount = entity.get("amount", 0)
        return 0 < refund_amount <= payment_amount
    
    # Side effect methods
    
    def _set_cleared_timestamp(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Set cleared_at timestamp."""
        from datetime import datetime
        entity["cleared_at"] = datetime.now().isoformat()
        entity["status"] = "CLEARED"
    
    def _apply_to_invoice(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Apply payment to invoice - updates invoice paid amount."""
        from database.connection import get_conn
        try:
            invoice_id = entity.get("invoice_id")
            amount = entity.get("amount", 0)
            if invoice_id and amount > 0:
                with get_conn() as conn:
                    conn.execute('''
                        UPDATE invoices SET paid_amount = COALESCE(paid_amount, 0) + ?,
                        balance_due = total_amount - (COALESCE(paid_amount, 0) + ?)
                        WHERE id = ?
                    ''', (amount, amount, invoice_id))
        except Exception:
            pass

    def _update_invoice_state(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Update invoice state based on payment."""
        from database.connection import get_conn
        try:
            invoice_id = entity.get("invoice_id")
            if invoice_id:
                with get_conn() as conn:
                    # Check if fully paid
                    row = conn.execute('''
                        SELECT total_amount, COALESCE(paid_amount, 0) as paid_amount FROM invoices WHERE id = ?
                    ''', (invoice_id,)).fetchone()
                    if row and row['paid_amount'] >= row['total_amount']:
                        conn.execute('''
                            UPDATE invoices SET status = 'paid', paid_at = ? WHERE id = ?
                        ''', (entity.get("cleared_at"), invoice_id))
                    else:
                        conn.execute('''
                            UPDATE invoices SET status = 'partial' WHERE id = ?
                        ''', (invoice_id,))
        except Exception:
            pass

    def _send_receipt(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Send payment receipt to customer - queues notification."""
        import db
        try:
            payment_id = entity.get("id")
            invoice_id = entity.get("invoice_id")
            customer_id = entity.get("customer_id")
            if payment_id and customer_id:
                customer = db.get_customer(customer_id)
                if customer and customer.get("email"):
                    db.queue_feedback_request(
                        customer_id=customer_id,
                        job_id=entity.get("job_id"),
                        feedback_type="payment_receipt"
                    )
                    db.add_audit_log(
                        entity_type="payment",
                        entity_id=payment_id,
                        action="send_receipt",
                        details=f"Receipt queued for {customer.get('email')}"
                    )
        except Exception:
            pass
    
    def _set_failed_timestamp(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Set failed_at timestamp."""
        from datetime import datetime
        entity["failed_at"] = datetime.now().isoformat()
        entity["status"] = "FAILED"
    
    def _record_failure_reason(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Record payment failure reason."""
        reason = context.get("failure_reason", "Unknown error")
        entity["failure_reason"] = reason
    
    def _notify_customer(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Notify customer of payment failure - queues notification."""
        import db
        try:
            payment_id = entity.get("id")
            customer_id = entity.get("customer_id")
            if payment_id and customer_id:
                customer = db.get_customer(customer_id)
                if customer and customer.get("email"):
                    db.queue_feedback_request(
                        customer_id=customer_id,
                        job_id=entity.get("job_id"),
                        feedback_type="payment_failed"
                    )
                    db.add_audit_log(
                        entity_type="payment",
                        entity_id=payment_id,
                        action="notify_failure",
                        details=f"Failure notification queued for {customer.get('email')}"
                    )
        except Exception:
            pass

    def _create_follow_up(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Create follow-up action for failed payment."""
        from datetime import datetime
        from database.connection import get_conn
        import db
        try:
            payment_id = entity.get("id")
            invoice_id = entity.get("invoice_id")
            if payment_id:
                with get_conn() as conn:
                    conn.execute('''
                        INSERT INTO action_queue (entity_type, entity_id, action_type, priority, status,
                                                 title, description, assigned_to, created_at)
                        VALUES ('payment', ?, 'follow_up_failed_payment', 'high', 'pending',
                                'Follow up failed payment', ?, NULL, ?)
                    ''', (payment_id, f"Payment #{payment_id} failed - follow up required",
                          datetime.now().isoformat(timespec='seconds')))
                db.add_audit_log(
                    entity_type="payment",
                    entity_id=payment_id,
                    action="create_follow_up",
                    details="Follow-up action created for failed payment"
                )
        except Exception:
            pass
    
    def _set_refunded_timestamp(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Set refunded_at timestamp."""
        from datetime import datetime
        entity["refunded_at"] = datetime.now().isoformat()
        entity["status"] = "REFUNDED"
    
    def _record_refund_reason(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Record refund reason."""
        reason = context.get("refund_reason", "")
        entity["refund_reason"] = reason
    
    def _process_refund(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Process the actual refund."""
        # In real implementation, would process via payment gateway
        refund_amount = context.get("refund_amount", 0)
        entity["refund_amount"] = refund_amount
    
    def _update_invoice_balance(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Update invoice balance after refund."""
        from database.connection import get_conn
        try:
            invoice_id = entity.get("invoice_id")
            refund_amount = entity.get("refund_amount", 0)
            if invoice_id and refund_amount > 0:
                with get_conn() as conn:
                    conn.execute('''
                        UPDATE invoices SET paid_amount = COALESCE(paid_amount, 0) - ?,
                        balance_due = total_amount - (COALESCE(paid_amount, 0) - ?),
                        status = 'sent'
                        WHERE id = ?
                    ''', (refund_amount, refund_amount, invoice_id))
        except Exception:
            pass

    def _send_refund_receipt(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Send refund receipt to customer - queues notification."""
        import db
        try:
            payment_id = entity.get("id")
            customer_id = entity.get("customer_id")
            if payment_id and customer_id:
                customer = db.get_customer(customer_id)
                if customer and customer.get("email"):
                    db.queue_feedback_request(
                        customer_id=customer_id,
                        job_id=entity.get("job_id"),
                        feedback_type="refund_processed"
                    )
                    db.add_audit_log(
                        entity_type="payment",
                        entity_id=payment_id,
                        action="send_refund_receipt",
                        details=f"Refund receipt queued for {customer.get('email')}"
                    )
        except Exception:
            pass
