"""
Invoice state machine implementation.

States: DRAFT → SENT → VIEWED → PARTIALLY_PAID → PAID
        Also supports: OVERDUE, VOID
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/01_state_machines.md
- LLM_AGENT_QUICKSTART.md
"""

from brain.state.machine import StateMachine
from typing import Dict, Any


class InvoiceStateMachine(StateMachine):
    """
    Invoice lifecycle state machine.
    
    Enforces valid state transitions for invoices from creation to payment.
    """
    
    def __init__(self):
        super().__init__()
        self._setup_states()
        self._setup_transitions()
    
    def _setup_states(self):
        """Define all invoice states."""
        # Non-terminal states
        self.add_state("DRAFT")
        self.add_state("SENT")
        self.add_state("VIEWED")
        self.add_state("PARTIALLY_PAID")
        self.add_state("OVERDUE")
        
        # Terminal states
        self.add_state("PAID", terminal=True)
        self.add_state("VOID", terminal=True)
    
    def _setup_transitions(self):
        """Define all valid invoice state transitions."""
        
        # DRAFT → SENT
        self.add_transition(
            "DRAFT", "SENT", "InvoiceSend",
            preconditions=[
                self._has_positive_total,
                self._has_customer_contact,
                self._has_line_items
            ],
            side_effects=[self._set_sent_timestamp, self._send_invoice]
        )
        
        # SENT → VIEWED (portal tracking)
        self.add_transition(
            "SENT", "VIEWED", "InvoiceView",
            preconditions=[],
            side_effects=[self._set_viewed_timestamp]
        )
        
        # SENT → PARTIALLY_PAID
        self.add_transition(
            "SENT", "PARTIALLY_PAID", "PaymentRecord",
            preconditions=[self._is_partial_payment],
            side_effects=[
                self._update_paid_amount,
                self._calculate_balance,
                self._send_receipt
            ]
        )
        
        # SENT → PAID
        self.add_transition(
            "SENT", "PAID", "PaymentRecord",
            preconditions=[self._is_full_payment],
            side_effects=[
                self._set_paid_timestamp,
                self._update_paid_amount,
                self._send_receipt
            ]
        )
        
        # PARTIALLY_PAID → PAID
        self.add_transition(
            "PARTIALLY_PAID", "PAID", "PaymentRecord",
            preconditions=[self._payment_covers_balance],
            side_effects=[
                self._set_paid_timestamp,
                self._update_paid_amount,
                self._send_receipt
            ]
        )
        
        # SENT → OVERDUE (system cron)
        self.add_transition(
            "SENT", "OVERDUE", "SystemMarkOverdue",
            preconditions=[self._is_past_due],
            side_effects=[self._set_overdue_timestamp, self._create_chase_action]
        )
        
        # OVERDUE → PAID
        self.add_transition(
            "OVERDUE", "PAID", "PaymentRecord",
            preconditions=[self._payment_covers_balance],
            side_effects=[
                self._set_paid_timestamp,
                self._update_paid_amount,
                self._clear_overdue,
                self._send_receipt
            ]
        )
        
        # Void transitions
        self.add_transition(
            "DRAFT", "VOID", "InvoiceVoid",
            preconditions=[self._has_void_reason, self._is_admin],
            side_effects=[self._set_void_timestamp, self._record_void_reason]
        )
        
        self.add_transition(
            "SENT", "VOID", "InvoiceVoid",
            preconditions=[
                self._has_void_reason,
                self._is_admin,
                self._not_yet_paid
            ],
            side_effects=[
                self._set_void_timestamp,
                self._record_void_reason,
                self._send_void_notice
            ]
        )
    
    # Precondition methods
    
    def _has_positive_total(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if invoice has positive total amount."""
        total = entity.get("total_amount", 0)
        return total > 0
    
    def _has_customer_contact(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if customer has email or phone."""
        # In real implementation, would check customer record
        # For now, simplified check
        return True
    
    def _has_line_items(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if invoice has at least one line item."""
        # In real implementation, would query line items
        return True
    
    def _is_partial_payment(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if payment is partial (less than total)."""
        payment_amount = context.get("payment_amount", 0)
        total = entity.get("total_amount", 0)
        paid = entity.get("paid_amount", 0)
        
        # Check payment is positive and doesn't fully pay balance
        remaining = total - paid
        return 0 < payment_amount < remaining
    
    def _is_full_payment(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if payment covers full balance."""
        payment_amount = context.get("payment_amount", 0)
        total = entity.get("total_amount", 0)
        paid = entity.get("paid_amount", 0)
        
        remaining = total - paid
        # Allow 1 cent tolerance for rounding
        return abs(payment_amount - remaining) <= 0.01
    
    def _payment_covers_balance(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if payment covers remaining balance."""
        return self._is_full_payment(entity, context)
    
    def _is_past_due(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if invoice is past due date."""
        from datetime import datetime, date
        
        due_date_str = entity.get("due_date")
        if not due_date_str:
            return False
        
        try:
            # Handle both date and datetime strings
            if "T" in due_date_str:
                due_date = datetime.fromisoformat(due_date_str).date()
            else:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            
            return due_date < date.today()
        except:
            return False
    
    def _has_void_reason(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if void reason is provided."""
        reason = context.get("void_reason", "")
        return len(reason) >= 10
    
    def _is_admin(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if user is admin."""
        return context.get("admin_override", False)
    
    def _not_yet_paid(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if invoice has no payments yet."""
        paid_amount = entity.get("paid_amount", 0)
        return paid_amount == 0
    
    # Side effect methods
    
    def _set_sent_timestamp(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Set sent_at timestamp."""
        from datetime import datetime
        entity["sent_at"] = datetime.now().isoformat()
    
    def _send_invoice(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Send invoice to customer - queues notification for background processing."""
        import db
        try:
            invoice_id = entity.get("id")
            customer_id = entity.get("customer_id")
            if invoice_id and customer_id:
                customer = db.get_customer(customer_id)
                if customer and customer.get("email"):
                    # Queue the notification for background sending
                    db.queue_feedback_request(
                        customer_id=customer_id,
                        job_id=entity.get("job_id"),
                        feedback_type="invoice_sent"
                    )
                    # Log the action
                    db.add_audit_log(
                        entity_type="invoice",
                        entity_id=invoice_id,
                        action="send_invoice",
                        details=f"Invoice queued for sending to {customer.get('email')}"
                    )
        except Exception:
            pass  # Fail silently to not block state transition
    
    def _set_viewed_timestamp(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Set viewed_at timestamp."""
        from datetime import datetime
        entity["viewed_at"] = datetime.now().isoformat()
    
    def _update_paid_amount(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Update paid amount on invoice."""
        payment_amount = context.get("payment_amount", 0)
        current_paid = entity.get("paid_amount", 0)
        entity["paid_amount"] = current_paid + payment_amount
    
    def _calculate_balance(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Calculate and update balance due."""
        total = entity.get("total_amount", 0)
        paid = entity.get("paid_amount", 0)
        entity["balance_due"] = total - paid
    
    def _send_receipt(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Send payment receipt to customer - queues notification for background processing."""
        import db
        try:
            invoice_id = entity.get("id")
            customer_id = entity.get("customer_id")
            if invoice_id and customer_id:
                customer = db.get_customer(customer_id)
                if customer and customer.get("email"):
                    db.queue_feedback_request(
                        customer_id=customer_id,
                        job_id=entity.get("job_id"),
                        feedback_type="payment_receipt"
                    )
                    db.add_audit_log(
                        entity_type="invoice",
                        entity_id=invoice_id,
                        action="send_receipt",
                        details=f"Payment receipt queued for {customer.get('email')}"
                    )
        except Exception:
            pass
    
    def _set_paid_timestamp(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Set paid_at timestamp."""
        from datetime import datetime
        entity["paid_at"] = datetime.now().isoformat()
        entity["balance_due"] = 0
    
    def _set_overdue_timestamp(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Set overdue_at timestamp."""
        from datetime import datetime
        entity["overdue_at"] = datetime.now().isoformat()
    
    def _create_chase_action(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Create follow-up action for overdue invoice."""
        import db
        from database.connection import get_conn
        try:
            invoice_id = entity.get("id")
            customer_id = entity.get("customer_id")
            if invoice_id:
                with get_conn() as conn:
                    conn.execute('''
                        INSERT INTO action_queue (entity_type, entity_id, action_type, priority, status,
                                                 title, description, assigned_to, created_at)
                        VALUES ('invoice', ?, 'chase_payment', 'high', 'pending',
                                'Chase overdue invoice', ?, NULL, ?)
                    ''', (invoice_id, f"Invoice #{entity.get('invoice_no', invoice_id)} is overdue",
                          db._datetime.now().isoformat(timespec='seconds')))
                db.add_audit_log(
                    entity_type="invoice",
                    entity_id=invoice_id,
                    action="create_chase_action",
                    details="Chase action created for overdue invoice"
                )
        except Exception:
            pass
    
    def _clear_overdue(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Clear overdue status."""
        entity["overdue_at"] = None
    
    def _set_void_timestamp(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Set voided_at timestamp."""
        from datetime import datetime
        entity["voided_at"] = datetime.now().isoformat()
    
    def _record_void_reason(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Record void reason."""
        reason = context.get("void_reason", "")
        entity["void_reason"] = reason
    
    def _send_void_notice(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Send void notice to customer - queues notification for background processing."""
        import db
        try:
            invoice_id = entity.get("id")
            customer_id = entity.get("customer_id")
            if invoice_id and customer_id:
                customer = db.get_customer(customer_id)
                if customer and customer.get("email"):
                    db.queue_feedback_request(
                        customer_id=customer_id,
                        job_id=entity.get("job_id"),
                        feedback_type="invoice_voided"
                    )
                    db.add_audit_log(
                        entity_type="invoice",
                        entity_id=invoice_id,
                        action="send_void_notice",
                        details=f"Void notice queued for {customer.get('email')}"
                    )
        except Exception:
            pass
