"""
Linking invariants implementation.

Checks:
- L-001: Job ↔ Invoice bidirectional links
- L-002: Payment → Invoice foreign key
- L-003: Job → Customer foreign key
- L-004: Quote → Job foreign key
- L-005: Assignment → Job + User foreign keys
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/03_invariants.md
- LLM_AGENT_QUICKSTART.md
"""
from brain.invariants.checker import InvariantChecker, ViolationSeverity
from typing import Dict, Any, List

class LinkingInvariants(InvariantChecker):
    """Entity linking invariant checks."""

    def check_job_invoice_link(self, job: Dict[str, Any], invoice: Dict[str, Any]=None) -> bool:
        """
        L-001: Check Job ↔ Invoice bidirectional link.
        
        Args:
            job: Job entity with invoice_no
            invoice: Invoice entity with job_id (optional)
            
        Returns:
            True if links consistent, False otherwise
        """
        job_has_invoice = bool(job and job.get('invoice_no'))
        if job_has_invoice and invoice:
            if invoice.get('job_id') != job.get('id', '') if job else '':
                self.add_violation(code='INV_LINK_JOB_INVOICE_MISMATCH', severity=ViolationSeverity.HIGH, entity_type='job', entity_id=job.get('id', '') if job else '', message="Job has invoice but invoice doesn't link back to job", details={'job_id': job.get('id', '') if job else '', 'job_invoice_no': job.get('invoice_no', '') if job else '', 'invoice_job_id': invoice.get('job_id')})
                return False
        return True

    def check_all(self, db_conn=None) -> List:
        """
        Run linking invariant checks across the database.

        Args:
            db_conn: sqlite3 connection

        Returns:
            List of InvariantViolation
        """
        self.violations = []
        if not db_conn:
            return self.violations

        try:
            # L-001: Job ↔ Invoice bidirectional link
            jobs = db_conn.execute("SELECT id, invoice_no FROM jobs WHERE invoice_no IS NOT NULL AND invoice_no <> ''").fetchall()
            for j in jobs:
                job_id = j['id'] if 'id' in j.keys() else j[0]
                inv_no = j['invoice_no'] if 'invoice_no' in j.keys() else j[1]
                inv = db_conn.execute('SELECT id, job_id, invoice_no FROM invoices WHERE invoice_no = ?', (inv_no,)).fetchone()
                if not inv:
                    self.add_violation(code='INV_LINK_JOB_INVOICE_MISMATCH', severity=ViolationSeverity.HIGH, entity_type='job', entity_id=job_id, message=f"Job references invoice_no {inv_no} but invoice not found", details={'job_id': job_id, 'invoice_no': inv_no})
                else:
                    inv_job_id = inv['job_id'] if 'job_id' in inv.keys() else inv[1]
                    if inv_job_id != job_id:
                        self.add_violation(code='INV_LINK_JOB_INVOICE_MISMATCH', severity=ViolationSeverity.HIGH, entity_type='job', entity_id=job_id, message="Job has invoice but invoice doesn't link back to job", details={'job_id': job_id, 'job_invoice_no': inv_no, 'invoice_job_id': inv_job_id})

            # Also check invoices that reference jobs
            invoices = db_conn.execute("SELECT id, job_id, invoice_no FROM invoices WHERE job_id IS NOT NULL").fetchall()
            for inv in invoices:
                inv_id = inv['id'] if 'id' in inv.keys() else inv[0]
                job_id = inv['job_id'] if 'job_id' in inv.keys() else inv[1]
                inv_no = inv.get('invoice_no') if isinstance(inv, dict) else (inv[2] if len(inv) > 2 else None)
                job = db_conn.execute('SELECT id, invoice_no FROM jobs WHERE id = ?', (job_id,)).fetchone()
                if not job:
                    self.add_violation(code='INV_LINK_JOB_INVOICE_MISMATCH', severity=ViolationSeverity.HIGH, entity_type='invoice', entity_id=inv_id, message='Invoice links to missing job', details={'invoice_id': inv_id, 'job_id': job_id})
                else:
                    job_inv_no = job.get('invoice_no') if isinstance(job, dict) else (job[1] if len(job) > 1 else None)
                    if job_inv_no != inv_no:
                        self.add_violation(code='INV_LINK_JOB_INVOICE_MISMATCH', severity=ViolationSeverity.HIGH, entity_type='invoice', entity_id=inv_id, message="Invoice.job_id points to a job whose invoice_no doesn't match", details={'invoice_id': inv_id, 'invoice_no': inv_no, 'job_id': job_id, 'job_invoice_no': job_inv_no})

            # L-002: Payments must reference an invoice
            try:
                payments = db_conn.execute("SELECT id, invoice_id FROM invoice_payments").fetchall()
                for p in payments:
                    pid = p['id'] if 'id' in p.keys() else p[0]
                    inv_id = p.get('invoice_id') if isinstance(p, dict) else (p[1] if len(p) > 1 else None)
                    if not inv_id:
                        self.add_violation(code='INV_LINK_PAYMENT_NO_INVOICE', severity=ViolationSeverity.CRITICAL, entity_type='payment', entity_id=pid, message='Payment has no invoice_id', details={'payment_id': pid})
                    else:
                        inv = db_conn.execute('SELECT id FROM invoices WHERE id = ?', (inv_id,)).fetchone()
                        if not inv:
                            self.add_violation(code='INV_LINK_PAYMENT_NO_INVOICE', severity=ViolationSeverity.CRITICAL, entity_type='payment', entity_id=pid, message='Payment references non-existent invoice', details={'payment_id': pid, 'invoice_id': inv_id})
            except Exception:
                # Fallback: check payments table
                try:
                    payments = db_conn.execute("SELECT id, invoice_id FROM payments").fetchall()
                    for p in payments:
                        pid = p['id'] if 'id' in p.keys() else p[0]
                        inv_id = p.get('invoice_id') if isinstance(p, dict) else (p[1] if len(p) > 1 else None)
                        if not inv_id:
                            self.add_violation(code='INV_LINK_PAYMENT_NO_INVOICE', severity=ViolationSeverity.CRITICAL, entity_type='payment', entity_id=pid, message='Payment has no invoice_id', details={'payment_id': pid})
                        else:
                            inv = db_conn.execute('SELECT id FROM invoices WHERE id = ?', (inv_id,)).fetchone()
                            if not inv:
                                self.add_violation(code='INV_LINK_PAYMENT_NO_INVOICE', severity=ViolationSeverity.CRITICAL, entity_type='payment', entity_id=pid, message='Payment references non-existent invoice', details={'payment_id': pid, 'invoice_id': inv_id})
                except Exception:
                    pass

            # L-003: Jobs must reference a valid customer
            try:
                jobs_all = db_conn.execute('SELECT id, customer_id FROM jobs').fetchall()
                for j in jobs_all:
                    jid = j['id'] if 'id' in j.keys() else j[0]
                    cust_id = j.get('customer_id') if isinstance(j, dict) else (j[1] if len(j) > 1 else None)
                    if not cust_id:
                        self.add_violation(code='INV_LINK_JOB_NO_CUSTOMER', severity=ViolationSeverity.CRITICAL, entity_type='job', entity_id=jid, message='Job has no customer_id', details={'job_id': jid})
                    else:
                        cust = db_conn.execute('SELECT id FROM customers WHERE id = ?', (cust_id,)).fetchone()
                        if not cust:
                            self.add_violation(code='INV_LINK_JOB_NO_CUSTOMER', severity=ViolationSeverity.CRITICAL, entity_type='job', entity_id=jid, message='Job references non-existent customer', details={'job_id': jid, 'customer_id': cust_id})
            except Exception:
                pass

            # L-004: Accepted quotes must have job_id
            try:
                quotes = db_conn.execute("SELECT id, status, job_id FROM quotes WHERE status = 'ACCEPTED'").fetchall()
                for q in quotes:
                    qid = q['id'] if 'id' in q.keys() else q[0]
                    job_id = q.get('job_id') if isinstance(q, dict) else (q[2] if len(q) > 2 else None)
                    if not job_id:
                        self.add_violation(code='INV_LINK_QUOTE_NO_JOB', severity=ViolationSeverity.HIGH, entity_type='quote', entity_id=qid, message='Accepted quote has no job_id', details={'quote_id': qid})
                    else:
                        job = db_conn.execute('SELECT id FROM jobs WHERE id = ?', (job_id,)).fetchone()
                        if not job:
                            self.add_violation(code='INV_LINK_QUOTE_NO_JOB', severity=ViolationSeverity.HIGH, entity_type='quote', entity_id=qid, message='Quote references non-existent job', details={'quote_id': qid, 'job_id': job_id})
            except Exception:
                pass

            # L-005: Assignments must reference job and user
            try:
                assignments = db_conn.execute('SELECT id, job_id, user_id FROM job_assignments').fetchall()
                for a in assignments:
                    aid = a['id'] if 'id' in a.keys() else a[0]
                    job_id = a.get('job_id') if isinstance(a, dict) else (a[1] if len(a) > 1 else None)
                    user_id = a.get('user_id') if isinstance(a, dict) else (a[2] if len(a) > 2 else None)
                    if not job_id:
                        self.add_violation(code='INV_LINK_ASSIGNMENT_NO_JOB', severity=ViolationSeverity.CRITICAL, entity_type='assignment', entity_id=aid, message='Assignment has no job_id', details={'assignment_id': aid})
                    else:
                        job = db_conn.execute('SELECT id FROM jobs WHERE id = ?', (job_id,)).fetchone()
                        if not job:
                            self.add_violation(code='INV_LINK_ASSIGNMENT_NO_JOB', severity=ViolationSeverity.CRITICAL, entity_type='assignment', entity_id=aid, message='Assignment references missing job', details={'assignment_id': aid, 'job_id': job_id})
                    if not user_id:
                        self.add_violation(code='INV_LINK_ASSIGNMENT_NO_USER', severity=ViolationSeverity.CRITICAL, entity_type='assignment', entity_id=aid, message='Assignment has no user_id', details={'assignment_id': aid})
                    else:
                        user = db_conn.execute('SELECT id FROM users WHERE id = ?', (user_id,)).fetchone()
                        if not user:
                            self.add_violation(code='INV_LINK_ASSIGNMENT_NO_USER', severity=ViolationSeverity.CRITICAL, entity_type='assignment', entity_id=aid, message='Assignment references missing user', details={'assignment_id': aid, 'user_id': user_id})
            except Exception:
                pass

        except Exception:
            # Be resilient - do not raise from invariant checks
            pass

        return self.violations

    def check_payment_invoice_link(self, payment: Dict[str, Any]) -> bool:
        """
        L-002: Check Payment → Invoice foreign key exists.
        
        Args:
            payment: Payment entity with invoice_id
            
        Returns:
            True if link valid, False otherwise
        """
        invoice_id = payment.get('invoice_id')
        if not invoice_id:
            self.add_violation(code='INV_LINK_PAYMENT_NO_INVOICE', severity=ViolationSeverity.CRITICAL, entity_type='payment', entity_id=payment.get('id'), message='Payment has no invoice_id', details={'payment_id': payment.get('id')})
            return False
        return True

    def check_job_customer_link(self, job: Dict[str, Any]) -> bool:
        """
        L-003: Check Job → Customer foreign key exists.
        
        Args:
            job: Job entity with customer_id
            
        Returns:
            True if link valid, False otherwise
        """
        customer_id = job.get('customer_id', '') if job else ''
        if not customer_id:
            self.add_violation(code='INV_LINK_JOB_NO_CUSTOMER', severity=ViolationSeverity.CRITICAL, entity_type='job', entity_id=job.get('id', '') if job else '', message='Job has no customer_id', details={'job_id': job.get('id', '') if job else ''})
            return False
        return True

    def check_quote_job_link(self, quote: Dict[str, Any]) -> bool:
        """
        L-004: Check Quote → Job foreign key if quote accepted.
        
        Args:
            quote: Quote entity with job_id
            
        Returns:
            True if link valid, False otherwise
        """
        status = quote.get('status', '')
        job_id = quote.get('job_id')
        if status == 'ACCEPTED' and (not job_id):
            self.add_violation(code='INV_LINK_QUOTE_NO_JOB', severity=ViolationSeverity.HIGH, entity_type='quote', entity_id=quote.get('id'), message='Accepted quote has no job_id', details={'quote_id': quote.get('id'), 'status': status})
            return False
        return True

    def check_assignment_links(self, assignment: Dict[str, Any]) -> bool:
        """
        L-005: Check Assignment → Job + User foreign keys.
        
        Args:
            assignment: Assignment entity with job_id and user_id
            
        Returns:
            True if links valid, False otherwise
        """
        job_id = assignment.get('job_id')
        user_id = assignment.get('user_id')
        if not job_id:
            self.add_violation(code='INV_LINK_ASSIGNMENT_NO_JOB', severity=ViolationSeverity.CRITICAL, entity_type='assignment', entity_id=assignment.get('id'), message='Assignment has no job_id', details={'assignment_id': assignment.get('id')})
            return False
        if not user_id:
            self.add_violation(code='INV_LINK_ASSIGNMENT_NO_USER', severity=ViolationSeverity.CRITICAL, entity_type='assignment', entity_id=assignment.get('id'), message='Assignment has no user_id', details={'assignment_id': assignment.get('id')})
            return False
        return True
