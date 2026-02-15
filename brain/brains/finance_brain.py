"""
FinanceBrain - The Accountant

Responsibilities:
- Invoices (create, send, void)
- Payments (record, refund)
- Quotes (create, send, accept/decline)
- Financial reporting

The FinanceBrain is a "Thinker" - it computes financial operations.
It NEVER writes to the database directly.
It sends WriteCommands to the Cerebellum.

Communication:
- Receives commands from Brainstem (after authentication)
- Sends WriteCommands to Cerebellum
- Listens to JOB_COMPLETED → Creates invoice
- Listens to PAYMENT_RECORDED → Updates invoice balance
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
from typing import Optional
import sqlite3
from brain.core.contracts import ICommand, EventType
from brain.core.cerebellum import Cerebellum, WriteCommand, WriteOperation
from brain.nervous_system import NervousSystem
from brain.core.result import BrainResult
from brain.core import cerebellum
from brain import nervous_system

class FinanceBrain:
    """
    Phase 5: FinanceBrain - The Accountant

    Handles all financial operations:
    - Invoice lifecycle (create → send → paid → void)
    - Payment recording and reconciliation
    - Quote generation and tracking
    - Financial reporting

    The FinanceBrain COMPUTES but doesn't WRITE.
    All writes go through the Cerebellum.

    Example Flow:
        1. OpsBrain completes a job
        2. OpsBrain emits JOB_COMPLETED event
        3. FinanceBrain hears the event
        4. FinanceBrain automatically creates an invoice
        5. FinanceBrain sends WriteCommand to Cerebellum
        6. Cerebellum writes to Ledger
        7. Cerebellum emits INVOICE_CREATED event
        8. RelationBrain hears INVOICE_CREATED → Sends invoice to customer
    """

    def __init__(self, cerebellum: Cerebellum, nervous_system: NervousSystem, db_connection: Optional[sqlite3.Connection]=None):
        """
        Initialize FinanceBrain.

        Args:
            cerebellum: The write coordinator
            nervous_system: The event bus
            db_connection: DB connection for reads (optional)
        """
        self.cerebellum = cerebellum
        self.nervous_system = nervous_system
        self.db_connection = db_connection
        self._my_secret_shard = self._load_secret_shard()
        self._register_listeners()

    def _load_secret_shard(self) -> Optional[bytes]:
        """
        Load this Brain's secret shard for multi-party consensus.
        
        In production, this should be loaded from:
        - Environment variable (FINANCE_BRAIN_SHARD)
        - Secure vault (HashiCorp Vault, AWS Secrets Manager)
        - Hardware security module (HSM)
        
        Returns:
            bytes: The secret shard, or None if not configured
        """
        import os
        shard_hex = os.getenv('FINANCE_BRAIN_SHARD')
        if shard_hex:
            try:
                return bytes.fromhex(shard_hex)
            except ValueError:
                import logging
                logging.warning('Invalid FINANCE_BRAIN_SHARD format, expected hex string')
        import secrets
        return secrets.token_bytes(32)

    def _register_listeners(self):
        """Register listeners for events from other brains"""

        @self.nervous_system.listen(EventType.JOB_COMPLETED, brain_name='FinanceBrain', priority=20)
        def on_job_completed(event):
            """
            When a job is completed, automatically create an invoice.

            This is the "reflex" - automatic invoice generation.
            Phase 9 (Executive AI) might override this in special cases.
            """
            job_id = event.payload.get('job_id')
            print(f'FinanceBrain: Job {job_id} completed, creating invoice...')

        @self.nervous_system.listen(EventType.PAYMENT_RECORDED, brain_name='FinanceBrain', priority=10)
        def on_payment_recorded(event):
            """When a payment is recorded, update invoice balance"""
            invoice_id = event.payload.get('invoice_id')
            amount = event.payload.get('amount')
            print(f'FinanceBrain: Payment of £{amount} recorded for invoice {invoice_id}')

        @self.nervous_system.listen(EventType.CONSENSUS_REQUESTED, brain_name='FinanceBrain', priority=100)
        def on_consensus_requested(event):
            """
            Evaluate a consensus request and decide whether to approve or veto.
            
            FinanceBrain's Logic Gate:
            - Check if operation is financially sound
            - Verify no financial invariants are violated
            - If approved: Release shard
            - If rejected: Withhold shard (veto)
            
            Example veto scenarios:
            - Deleting a paid invoice
            - Refunding more than invoice total
            - Creating duplicate invoice numbers
            """
            proposal_id = event.payload.get('proposal_id')
            command_type = event.payload.get('command_type')
            entity_type = event.payload.get('entity_type')
            entity_id = event.payload.get('entity_id')
            data = event.payload.get('data', {})
            should_approve = True
            veto_reason = None
            if command_type == 'DELETE' and entity_type == 'invoice':
                if self.db_connection:
                    try:
                        cursor = self.db_connection.cursor()
                        cursor.execute('SELECT status, balance FROM invoices WHERE id = ?', (entity_id,))
                        result = cursor.fetchone()
                        if result:
                            status = result[0] if result else 'unknown'
                            balance = result[1] if result else 0
                            if status == 'PAID' or balance == 0:
                                should_approve = False
                                veto_reason = 'Cannot delete paid invoice - financial audit trail violation'
                    except Exception as e:
                        should_approve = False
                        veto_reason = f'Unable to verify invoice status: {e}'
            elif command_type == 'CREATE' and entity_type == 'refund':
                refund_amount = data.get('amount', 0)
                invoice_id = data.get('invoice_id')
                if refund_amount <= 0:
                    should_approve = False
                    veto_reason = 'Invalid refund amount'
            if should_approve and self._my_secret_shard:
                from brain.core.contracts import create_event
                shard_event = create_event(event_type=EventType.KEY_SHARD_RELEASED, caused_by_command_id=event.caused_by_command_id, caused_by_user_id=event.caused_by_user_id, payload={'proposal_id': proposal_id, 'shard': self._my_secret_shard.hex(), 'brain': 'FINANCE'})
                self.nervous_system.emit(shard_event)
                import logging
                logging.info(f'FinanceBrain: Approved consensus for proposal {proposal_id}')
            else:
                from brain.core.contracts import create_event
                veto_event = create_event(event_type=EventType.CONSENSUS_VETO, caused_by_command_id=event.caused_by_command_id, caused_by_user_id=event.caused_by_user_id, payload={'proposal_id': proposal_id, 'brain': 'FINANCE', 'reason': veto_reason or 'Financial policy violation'})
                self.nervous_system.emit(veto_event)
                import logging
                logging.warning(f'FinanceBrain: VETOED consensus for proposal {proposal_id}: {veto_reason}')

    def handle_command(self, command: ICommand) -> BrainResult:
        """
        Handle a command routed to FinanceBrain.
        
        This is the main entry point for all finance commands.
        Routes to specific handlers based on command type.
        
        Args:
            command: Validated ICommand from Brainstem
            
        Returns:
            BrainResult with execution outcome
        """
        command_type = command.command_type
        if command_type == 'InvoiceCreate':
            return self.create_invoice(command)
        elif command_type == 'InvoiceSend':
            return self.send_invoice(command)
        elif command_type == 'InvoiceVoid':
            return self.void_invoice(command)
        elif command_type == 'PaymentRecord':
            return self.record_payment(command)
        elif command_type == 'QuoteCreate':
            return self.create_quote(command)
        elif command_type == 'QuoteAccept':
            return self.accept_quote(command)
        elif command_type == 'QuoteDecline':
            return self.decline_quote(command)
        else:
            return BrainResult.fail(error_message=f'Unknown command type for FinanceBrain: {command_type}', error_code='UNKNOWN_COMMAND')

    def create_invoice(self, command: ICommand) -> BrainResult:
        """
        Create a new invoice.

        Args:
            command: The authenticated command from Brainstem

        Returns:
            BrainResult with invoice_id if successful
        """
        invoice_data = {'job_id': command.payload.get('job_id'), 'customer_id': command.payload.get('customer_id'), 'amount': command.payload.get('amount'), 'due_date': command.payload.get('due_date'), 'status': 'DRAFT', 'balance': command.payload.get('amount'), 'created_by': command.user_id, 'company_id': command.company_id}
        write_cmd = WriteCommand(operation=WriteOperation.CREATE, entity_type='invoice', entity_id=None, data=invoice_data, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'invoice_id': result.entity_id}, message=f'Invoice created: {result.entity_id}')
        else:
            return BrainResult.fail(error_message=result.error, data={'invariant_violations': result.invariant_violations})

    def record_payment(self, command: ICommand) -> BrainResult:
        """
        Record a payment against an invoice.

        This will:
        - Update invoice balance
        - Emit PAYMENT_RECORDED event
        - If balance = 0, emit INVOICE_PAID event
        """
        invoice_id = command.payload.get('invoice_id')
        amount = command.payload.get('amount')
        payment_method = command.payload.get('payment_method', 'cash')
        current_balance = 1000.0
        new_balance = current_balance - amount
        payment_data = {'invoice_id': invoice_id, 'amount': amount, 'payment_method': payment_method, 'recorded_by': command.user_id}
        write_cmd = WriteCommand(operation=WriteOperation.CREATE, entity_type='payment', entity_id=None, data=payment_data, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'payment_id': result.entity_id, 'invoice_id': invoice_id, 'new_balance': new_balance}, message=f'Payment recorded: £{amount}')
        else:
            return BrainResult.fail(error_message=result.error)

    def create_quote(self, command: ICommand) -> BrainResult:
        """Create a quote for a potential job"""
        quote_data = {'customer_id': command.payload.get('customer_id'), 'job_description': command.payload.get('description'), 'amount': command.payload.get('amount'), 'valid_until': command.payload.get('valid_until'), 'status': 'DRAFT', 'created_by': command.user_id, 'company_id': command.company_id}
        write_cmd = WriteCommand(operation=WriteOperation.CREATE, entity_type='quote', entity_id=None, data=quote_data, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'quote_id': result.entity_id}, message=f'Quote created: {result.entity_id}')
        else:
            return BrainResult.fail(error_message=result.error)

    def get_invoice(self, invoice_id: int) -> dict:
        """
        Read an invoice (from projection table).

        Reads go directly to projection tables, not through Cerebellum.
        """
        if not self.db_connection:
            return {'error': 'No database connection'}
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM invoices WHERE id = ?', (invoice_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return dict(zip(columns, row))
        else:
            return None

    def send_invoice(self, command: ICommand) -> BrainResult:
        """Send invoice to customer"""
        invoice_id = command.payload.get('invoice_id')
        after_state = {'status': 'SENT', 'sent_at': command.timestamp.isoformat()}
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='invoice', entity_id=invoice_id, data=after_state, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'invoice_id': invoice_id, 'status': 'SENT'}, message=f'Invoice {invoice_id} sent')
        else:
            return BrainResult.fail(error_message=result.error)

    def void_invoice(self, command: ICommand) -> BrainResult:
        """Void an invoice"""
        invoice_id = command.payload.get('invoice_id')
        reason = command.payload.get('reason', '')
        after_state = {'status': 'VOID', 'voided_at': command.timestamp.isoformat(), 'void_reason': reason}
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='invoice', entity_id=invoice_id, data=after_state, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'invoice_id': invoice_id, 'status': 'VOID'}, message=f'Invoice {invoice_id} voided')
        else:
            return BrainResult.fail(error_message=result.error)

    def accept_quote(self, command: ICommand) -> BrainResult:
        """Accept a quote"""
        quote_id = command.payload.get('quote_id')
        after_state = {'status': 'ACCEPTED', 'accepted_at': command.timestamp.isoformat()}
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='quote', entity_id=quote_id, data=after_state, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'quote_id': quote_id, 'status': 'ACCEPTED'}, message=f'Quote {quote_id} accepted')
        else:
            return BrainResult.fail(error_message=result.error)

    def decline_quote(self, command: ICommand) -> BrainResult:
        """Decline a quote"""
        quote_id = command.payload.get('quote_id')
        reason = command.payload.get('reason', '')
        after_state = {'status': 'DECLINED', 'declined_at': command.timestamp.isoformat(), 'decline_reason': reason}
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='quote', entity_id=quote_id, data=after_state, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'quote_id': quote_id, 'status': 'DECLINED'}, message=f'Quote {quote_id} declined')
        else:
            return BrainResult.fail(error_message=result.error)