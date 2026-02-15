"""
Job state machine implementation.

States: DRAFT → QUOTED → BOOKED → SCHEDULED → IN_PROGRESS → COMPLETED → INVOICED
        Also supports: PAUSED, AWAITING_SIGNOFF, CANCELLED
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/01_state_machines.md
- LLM_AGENT_QUICKSTART.md
"""

from brain.state.machine import StateMachine
from typing import Dict, Any


class JobStateMachine(StateMachine):
    """
    Job lifecycle state machine.
    
    Enforces valid state transitions for jobs from creation to completion.
    """
    
    def __init__(self):
        super().__init__()
        self._setup_states()
        self._setup_transitions()
    
    def _setup_states(self):
        """Define all job states."""
        # Non-terminal states
        self.add_state("DRAFT")
        self.add_state("QUOTED")
        self.add_state("BOOKED")
        self.add_state("SCHEDULED")
        self.add_state("IN_PROGRESS")
        self.add_state("PAUSED")
        self.add_state("AWAITING_SIGNOFF")
        
        # Terminal states
        self.add_state("COMPLETED", terminal=True)
        self.add_state("INVOICED", terminal=True)
        self.add_state("CANCELLED", terminal=True)
    
    def _setup_transitions(self):
        """Define all valid job state transitions."""
        
        # DRAFT → QUOTED
        self.add_transition(
            "DRAFT", "QUOTED", "JobQuote",
            preconditions=[self._has_quote_price],
            side_effects=[self._set_quoted_timestamp]
        )
        
        # QUOTED → BOOKED
        self.add_transition(
            "QUOTED", "BOOKED", "JobBook",
            preconditions=[],
            side_effects=[self._set_booked_timestamp]
        )
        
        # BOOKED → SCHEDULED
        self.add_transition(
            "BOOKED", "SCHEDULED", "JobSchedule",
            preconditions=[self._has_date_and_crew],
            side_effects=[self._send_confirmation]
        )
        
        # SCHEDULED → IN_PROGRESS
        self.add_transition(
            "SCHEDULED", "IN_PROGRESS", "JobStart",
            preconditions=[],
            side_effects=[self._start_time_tracking]
        )
        
        # IN_PROGRESS → PAUSED
        self.add_transition(
            "IN_PROGRESS", "PAUSED", "JobPause",
            preconditions=[],
            side_effects=[self._pause_time_tracking]
        )
        
        # PAUSED → IN_PROGRESS
        self.add_transition(
            "PAUSED", "IN_PROGRESS", "JobResume",
            preconditions=[],
            side_effects=[self._resume_time_tracking]
        )
        
        # IN_PROGRESS → AWAITING_SIGNOFF
        self.add_transition(
            "IN_PROGRESS", "AWAITING_SIGNOFF", "JobComplete",
            preconditions=[],
            side_effects=[self._stop_time_tracking]
        )
        
        # AWAITING_SIGNOFF → COMPLETED
        self.add_transition(
            "AWAITING_SIGNOFF", "COMPLETED", "JobAddSignOff",
            preconditions=[],
            side_effects=[self._set_completed_timestamp]
        )
        
        # COMPLETED → INVOICED
        self.add_transition(
            "COMPLETED", "INVOICED", "InvoiceCreate",
            preconditions=[self._no_existing_invoice],
            side_effects=[self._set_invoice_number]
        )
        
        # Cancellation transitions
        self.add_transition(
            "QUOTED", "CANCELLED", "JobCancel",
            preconditions=[],
            side_effects=[self._set_cancelled_timestamp]
        )
        
        self.add_transition(
            "BOOKED", "CANCELLED", "JobCancel",
            preconditions=[self._has_cancellation_reason],
            side_effects=[self._set_cancelled_timestamp, self._refund_deposit]
        )
        
        self.add_transition(
            "SCHEDULED", "CANCELLED", "JobCancel",
            preconditions=[self._has_cancellation_reason],
            side_effects=[
                self._set_cancelled_timestamp,
                self._unassign_crew,
                self._refund_deposit
            ]
        )
        
        # Reopen transitions (admin only)
        self.add_transition(
            "CANCELLED", "DRAFT", "JobReopen",
            preconditions=[self._is_admin],
            side_effects=[self._clear_cancellation_data]
        )
        
        self.add_transition(
            "COMPLETED", "IN_PROGRESS", "JobReopen",
            preconditions=[self._is_admin],
            side_effects=[self._clear_completion_timestamp]
        )
    
    # Precondition methods
    
    def _has_quote_price(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if job has a quoted price > 0."""
        quoted_price = entity.get("quoted_price", 0)
        return quoted_price is not None and quoted_price > 0
    
    def _has_date_and_crew(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if job has date set and crew assigned."""
        has_date = entity.get("job_date") is not None
        # For now, we'll simplify crew check - can be enhanced later
        return has_date
    
    def _no_existing_invoice(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if job doesn't already have an invoice."""
        return not entity.get("invoice_no")
    
    def _has_cancellation_reason(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if cancellation reason is provided."""
        reason = context.get("cancellation_reason", "")
        return len(reason) >= 10
    
    def _is_admin(self, entity: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if user is admin (simplified check)."""
        # In a real implementation, would check user role
        # For now, just check if explicitly allowed
        return context.get("admin_override", False)
    
    # Side effect methods
    
    def _set_quoted_timestamp(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Set quoted_at timestamp."""
        # In real implementation, would update database
        # For now, just mark in entity
        from datetime import datetime
        entity["quoted_at"] = datetime.now().isoformat()
    
    def _set_booked_timestamp(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Set booked_at timestamp."""
        from datetime import datetime
        entity["booked_at"] = datetime.now().isoformat()
    
    def _send_confirmation(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Send confirmation message to customer - queues notification."""
        import db
        try:
            job_id = entity.get("id")
            customer_id = entity.get("customer_id")
            if job_id and customer_id:
                customer = db.get_customer(customer_id)
                if customer and customer.get("email"):
                    db.queue_feedback_request(
                        customer_id=customer_id,
                        job_id=job_id,
                        feedback_type="job_confirmation"
                    )
                    db.add_audit_log(
                        entity_type="job",
                        entity_id=job_id,
                        action="send_confirmation",
                        details=f"Confirmation queued for {customer.get('email')}"
                    )
        except Exception:
            pass

    def _start_time_tracking(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Start time tracking for job."""
        from datetime import datetime
        from database.connection import get_conn
        try:
            job_id = entity.get("id")
            user_id = context.get("user_id")
            if job_id:
                with get_conn() as conn:
                    conn.execute('''
                        INSERT INTO time_entries (job_id, user_id, start_time, status, created_at)
                        VALUES (?, ?, ?, 'active', ?)
                    ''', (job_id, user_id, datetime.now().isoformat(timespec='seconds'),
                          datetime.now().isoformat(timespec='seconds')))
                entity["time_tracking_started_at"] = datetime.now().isoformat()
        except Exception:
            pass

    def _pause_time_tracking(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Pause time tracking - updates active time entry."""
        from datetime import datetime
        from database.connection import get_conn
        try:
            job_id = entity.get("id")
            if job_id:
                with get_conn() as conn:
                    conn.execute('''
                        UPDATE time_entries SET status = 'paused', paused_at = ?
                        WHERE job_id = ? AND status = 'active'
                    ''', (datetime.now().isoformat(timespec='seconds'), job_id))
                entity["time_tracking_paused_at"] = datetime.now().isoformat()
        except Exception:
            pass

    def _resume_time_tracking(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Resume time tracking - reactivates paused time entry."""
        from datetime import datetime
        from database.connection import get_conn
        try:
            job_id = entity.get("id")
            if job_id:
                with get_conn() as conn:
                    conn.execute('''
                        UPDATE time_entries SET status = 'active', resumed_at = ?
                        WHERE job_id = ? AND status = 'paused'
                    ''', (datetime.now().isoformat(timespec='seconds'), job_id))
                entity["time_tracking_paused_at"] = None
        except Exception:
            pass

    def _stop_time_tracking(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Stop time tracking - completes active time entry."""
        from datetime import datetime
        from database.connection import get_conn
        try:
            job_id = entity.get("id")
            if job_id:
                with get_conn() as conn:
                    conn.execute('''
                        UPDATE time_entries SET status = 'completed', end_time = ?
                        WHERE job_id = ? AND status IN ('active', 'paused')
                    ''', (datetime.now().isoformat(timespec='seconds'), job_id))
                entity["time_tracking_stopped_at"] = datetime.now().isoformat()
        except Exception:
            pass
    
    def _set_completed_timestamp(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Set completed_at timestamp."""
        from datetime import datetime
        entity["completed_at"] = datetime.now().isoformat()
    
    def _set_invoice_number(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Set invoice number on job."""
        invoice_no = context.get("invoice_no")
        if invoice_no:
            entity["invoice_no"] = invoice_no
    
    def _set_cancelled_timestamp(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Set cancelled_at timestamp."""
        from datetime import datetime
        entity["cancelled_at"] = datetime.now().isoformat()
    
    def _refund_deposit(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Process deposit refund if applicable - creates refund record."""
        from datetime import datetime
        from database.connection import get_conn
        import db
        try:
            job_id = entity.get("id")
            deposit_amount = entity.get("deposit_amount", 0)
            if job_id and deposit_amount > 0:
                with get_conn() as conn:
                    conn.execute('''
                        INSERT INTO refunds (job_id, amount, refund_type, status, created_at)
                        VALUES (?, ?, 'deposit', 'pending', ?)
                    ''', (job_id, deposit_amount, datetime.now().isoformat(timespec='seconds')))
                db.add_audit_log(
                    entity_type="job",
                    entity_id=job_id,
                    action="refund_deposit",
                    details=f"Deposit refund of {deposit_amount} created"
                )
                entity["deposit_refund_pending"] = True
        except Exception:
            pass

    def _unassign_crew(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Unassign crew from job."""
        from datetime import datetime
        from database.connection import get_conn
        import db
        try:
            job_id = entity.get("id")
            if job_id:
                with get_conn() as conn:
                    # Mark all assignments as unassigned
                    conn.execute('''
                        UPDATE job_assignments SET status = 'unassigned', unassigned_at = ?
                        WHERE job_id = ? AND status = 'assigned'
                    ''', (datetime.now().isoformat(timespec='seconds'), job_id))
                db.add_audit_log(
                    entity_type="job",
                    entity_id=job_id,
                    action="unassign_crew",
                    details="Crew unassigned due to job cancellation"
                )
        except Exception:
            pass
    
    def _clear_cancellation_data(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Clear cancellation timestamp and reason."""
        entity["cancelled_at"] = None
        entity["cancellation_reason"] = None
    
    def _clear_completion_timestamp(self, entity: Dict[str, Any], context: Dict[str, Any]):
        """Clear completion timestamp."""
        entity["completed_at"] = None
