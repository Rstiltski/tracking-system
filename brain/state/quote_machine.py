"""
Quote state machine implementation.

States: DRAFT → SENT → VIEWED → ACCEPTED / DECLINED / EXPIRED
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/01_state_machines.md
- LLM_AGENT_QUICKSTART.md
"""
from brain.state.machine import StateMachine
from typing import Dict, Any

class QuoteStateMachine(StateMachine):
    """
    Quote lifecycle state machine.
    
    Enforces valid state transitions for quotes from creation to acceptance or decline.
    """

    def __init__(self):
        super().__init__()
        self._setup_states()
        self._setup_transitions()

    def _setup_states(self):
        """Define all quote states."""
        self.add_state('DRAFT')
        self.add_state('SENT')
        self.add_state('VIEWED')
        self.add_state('ACCEPTED', terminal=True)
        self.add_state('DECLINED', terminal=True)
        self.add_state('EXPIRED', terminal=True)

    def _setup_transitions(self):
        """Define all valid quote state transitions."""
        self.add_transition('DRAFT', 'SENT', 'QuoteSend', preconditions=[self._has_line_items, self._has_positive_total, self._has_customer_contact], side_effects=[self._set_sent_timestamp])
        self.add_transition('SENT', 'VIEWED', 'QuoteView', preconditions=[], side_effects=[self._set_viewed_timestamp])
        self.add_transition('SENT', 'ACCEPTED', 'QuoteAccept', preconditions=[], side_effects=[self._set_accepted_timestamp, self._create_job_draft])
        self.add_transition('VIEWED', 'ACCEPTED', 'QuoteAccept', preconditions=[], side_effects=[self._set_accepted_timestamp, self._create_job_draft])
        self.add_transition('SENT', 'DECLINED', 'QuoteDecline', preconditions=[], side_effects=[self._set_declined_timestamp, self._log_decline_reason])
        self.add_transition('VIEWED', 'DECLINED', 'QuoteDecline', preconditions=[], side_effects=[self._set_declined_timestamp, self._log_decline_reason])
        self.add_transition('SENT', 'EXPIRED', 'SystemMarkExpired', preconditions=[self._is_past_valid_until], side_effects=[self._set_expired_timestamp])
        self.add_transition('VIEWED', 'EXPIRED', 'SystemMarkExpired', preconditions=[self._is_past_valid_until], side_effects=[self._set_expired_timestamp])

    def _has_line_items(self, entity_id: int, context: Dict[str, Any]) -> bool:
        """Quote must have at least one line item."""
        import db
        quote = db.get_quote_with_items(entity_id)
        if not quote:
            return False
        return len(quote.get('line_items', [])) > 0

    def _has_positive_total(self, entity_id: int, context: Dict[str, Any]) -> bool:
        """Quote total must be greater than zero."""
        import db
        quote = db.get_quote_with_items(entity_id)
        if not quote:
            return False
        return quote.get('total_amount', 0) > 0

    def _has_customer_contact(self, entity_id: int, context: Dict[str, Any]) -> bool:
        """Customer must have email or phone."""
        import db
        quote = db.get_quote_with_items(entity_id)
        if not quote:
            return False
        customer_id = quote.get('customer_id')
        if not customer_id:
            return False
        customer = db.get_customer(customer_id)
        if not customer:
            return False
        return bool(customer.get('email', '') if customer else '' or customer.get('phone', '') if customer else '')

    def _is_past_valid_until(self, entity_id: int, context: Dict[str, Any]) -> bool:
        """Check if quote is past valid_until date."""
        import db
        from datetime import datetime
        quote = db.get_quote_with_items(entity_id)
        if not quote:
            return False
        valid_until = quote.get('valid_until')
        if not valid_until:
            return False
        try:
            valid_date = datetime.fromisoformat(valid_until)
            return datetime.now() > valid_date
        except:
            return False

    def _set_sent_timestamp(self, entity_id: int, context: Dict[str, Any]) -> None:
        """Record when quote was sent."""
        from datetime import datetime
        from database.connection import get_conn
        try:
            with get_conn() as conn:
                conn.execute('''
                    UPDATE quotes SET sent_at = ?, status = 'sent' WHERE id = ?
                ''', (datetime.now().isoformat(timespec='seconds'), entity_id))
        except Exception:
            pass

    def _set_viewed_timestamp(self, entity_id: int, context: Dict[str, Any]) -> None:
        """Record when quote was viewed."""
        from datetime import datetime
        from database.connection import get_conn
        try:
            with get_conn() as conn:
                conn.execute('''
                    UPDATE quotes SET viewed_at = ? WHERE id = ? AND viewed_at IS NULL
                ''', (datetime.now().isoformat(timespec='seconds'), entity_id))
        except Exception:
            pass

    def _set_accepted_timestamp(self, entity_id: int, context: Dict[str, Any]) -> None:
        """Record when quote was accepted."""
        from datetime import datetime
        from database.connection import get_conn
        import db
        try:
            with get_conn() as conn:
                conn.execute('''
                    UPDATE quotes SET accepted_at = ?, status = 'accepted' WHERE id = ?
                ''', (datetime.now().isoformat(timespec='seconds'), entity_id))
            db.add_audit_log(
                entity_type="quote",
                entity_id=entity_id,
                action="accepted",
                details="Quote accepted by customer"
            )
        except Exception:
            pass

    def _create_job_draft(self, entity_id: int, context: Dict[str, Any]) -> None:
        """Create draft job from accepted quote."""
        from datetime import datetime
        from database.connection import get_conn
        import db
        try:
            with get_conn() as conn:
                # Get quote details
                quote = conn.execute('SELECT * FROM quotes WHERE id = ?', (entity_id,)).fetchone()
                if not quote:
                    return

                # Create job from quote
                cur = conn.execute('''
                    INSERT INTO jobs (customer_id, title, description, quoted_price, status, job_type, created_at)
                    VALUES (?, ?, ?, ?, 'Draft', ?, ?)
                ''', (
                    quote['customer_id'] if quote and 'customer_id' in quote.keys() else None,
                    quote['title'] if quote and 'title' in quote.keys() else 'Job from Quote',
                    quote['description'] if quote and 'description' in quote.keys() else '',
                    quote['total_amount'] if quote and 'total_amount' in quote.keys() else 0,
                    quote['job_type'] if quote and 'job_type' in quote.keys() else '',
                    datetime.now().isoformat(timespec='seconds')
                ))
                job_id = cur.lastrowid

                # Link quote to job
                conn.execute('UPDATE quotes SET job_id = ? WHERE id = ?', (job_id, entity_id))

                db.add_audit_log(
                    entity_type="quote",
                    entity_id=entity_id,
                    action="job_created",
                    details=f"Job #{job_id} created from quote"
                )
        except Exception:
            pass

    def _set_declined_timestamp(self, entity_id: int, context: Dict[str, Any]) -> None:
        """Record when quote was declined."""
        from datetime import datetime
        from database.connection import get_conn
        try:
            with get_conn() as conn:
                conn.execute('''
                    UPDATE quotes SET declined_at = ?, status = 'declined' WHERE id = ?
                ''', (datetime.now().isoformat(timespec='seconds'), entity_id))
        except Exception:
            pass

    def _log_decline_reason(self, entity_id: int, context: Dict[str, Any]) -> None:
        """Log the reason for declining."""
        from database.connection import get_conn
        import db
        try:
            reason = context.get("decline_reason", "")
            with get_conn() as conn:
                conn.execute('''
                    UPDATE quotes SET decline_reason = ? WHERE id = ?
                ''', (reason, entity_id))
            db.add_audit_log(
                entity_type="quote",
                entity_id=entity_id,
                action="declined",
                details=f"Decline reason: {reason}"
            )
        except Exception:
            pass

    def _set_expired_timestamp(self, entity_id: int, context: Dict[str, Any]) -> None:
        """Record when quote expired."""
        from datetime import datetime
        from database.connection import get_conn
        try:
            with get_conn() as conn:
                conn.execute('''
                    UPDATE quotes SET expired_at = ?, status = 'expired' WHERE id = ?
                ''', (datetime.now().isoformat(timespec='seconds'), entity_id))
        except Exception:
            pass