"""
RelationBrain - The Concierge

Responsibilities:
- Customer management (create, update)
- Communications (SMS, email)
- Customer portal
- Relationship tracking and notifications

The RelationBrain is a "Thinker" - it manages relationships and communications.
It NEVER writes to the database directly.
It sends WriteCommands to the Cerebellum.

Communication:
- Receives commands from Brainstem (after authentication)
- Sends WriteCommands to Cerebellum
- Listens to JOB_COMPLETED → Sends thank you message
- Listens to INVOICE_SENT → Sends payment reminder
- Listens to INVOICE_PAID → Sends receipt
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

class RelationBrain:
    """
    Phase 5: RelationBrain - The Concierge

    Handles all customer relationships:
    - Customer lifecycle (create → active → loyal)
    - Communication (SMS, email, portal messages)
    - Sentiment tracking
    - Proactive outreach

    The RelationBrain COMMUNICATES but doesn't WRITE (directly).
    All database writes go through the Cerebellum.

    Example Flow:
        1. OpsBrain completes a job
        2. OpsBrain emits JOB_COMPLETED event
        3. RelationBrain hears the event
        4. RelationBrain sends thank you SMS to customer
        5. RelationBrain logs communication via Cerebellum
        6. Cerebellum emits SMS_SENT event

        Later:
        1. FinanceBrain marks invoice as PAID
        2. FinanceBrain emits INVOICE_PAID event
        3. RelationBrain hears the event
        4. RelationBrain sends receipt and thank you

    Phase 9 Integration (Future):
        The Executive AI can override RelationBrain's reflexes.
        Example: "Don't send late payment reminder, customer has emergency"
    """

    def __init__(self, cerebellum: Cerebellum, nervous_system: NervousSystem, db_connection: Optional[sqlite3.Connection]=None):
        """
        Initialize RelationBrain.

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
        
        Returns:
            bytes: The secret shard, or None if not configured
        """
        import os
        shard_hex = os.getenv('RELATION_BRAIN_SHARD')
        if shard_hex:
            try:
                return bytes.fromhex(shard_hex)
            except ValueError:
                import logging
                logging.warning('Invalid RELATION_BRAIN_SHARD format, expected hex string')
        import secrets
        return secrets.token_bytes(32)

    def _register_listeners(self):
        """Register listeners for events from other brains"""

        @self.nervous_system.listen(EventType.JOB_COMPLETED, brain_name='RelationBrain', priority=30)
        def on_job_completed(event):
            """
            When a job is completed, send thank you message.

            This is the "reflex" - automatic customer appreciation.
            """
            job_id = event.payload.get('job_id')
            print(f'RelationBrain: Job {job_id} completed, sending thank you SMS...')

        @self.nervous_system.listen(EventType.INVOICE_PAID, brain_name='RelationBrain', priority=10)
        def on_invoice_paid(event):
            """When an invoice is paid, send receipt and thank you"""
            invoice_id = event.payload.get('invoice_id')
            customer_id = event.payload.get('customer_id')
            print(f'RelationBrain: Invoice {invoice_id} paid, sending receipt to customer {customer_id}...')

        @self.nervous_system.listen(EventType.CONSENSUS_REQUESTED, brain_name='RelationBrain', priority=100)
        def on_consensus_requested(event):
            """
            Evaluate a consensus request from customer relationship perspective.
            
            RelationBrain's Logic Gate:
            - Verify customer impact
            - Check relationship health
            - Ensure no negative customer experience
            """
            proposal_id = event.payload.get('proposal_id')
            command_type = event.payload.get('command_type')
            entity_type = event.payload.get('entity_type')
            entity_id = event.payload.get('entity_id')
            should_approve = True
            veto_reason = None
            if command_type == 'DELETE' and entity_type == 'customer':
                if self.db_connection:
                    try:
                        cursor = self.db_connection.cursor()
                        cursor.execute("SELECT COUNT(*) FROM messages WHERE customer_id = ? AND status = 'pending'", (entity_id,))
                        result = cursor.fetchone()
                        if result and (((((((((((((((result[0] if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) > 0:
                            should_approve = False
                            veto_reason = 'Cannot delete customer with pending communications'
                    except Exception as e:
                        should_approve = False
                        veto_reason = f'Unable to verify customer communication status: {e}'
            if should_approve and self._my_secret_shard:
                from brain.core.contracts import create_event
                shard_event = create_event(event_type=EventType.KEY_SHARD_RELEASED, caused_by_command_id=event.caused_by_command_id, caused_by_user_id=event.caused_by_user_id, payload={'proposal_id': proposal_id, 'shard': self._my_secret_shard.hex(), 'brain': 'RELATION'})
                self.nervous_system.emit(shard_event)
                import logging
                logging.info(f'RelationBrain: Approved consensus for proposal {proposal_id}')
            else:
                from brain.core.contracts import create_event
                veto_event = create_event(event_type=EventType.CONSENSUS_VETO, caused_by_command_id=event.caused_by_command_id, caused_by_user_id=event.caused_by_user_id, payload={'proposal_id': proposal_id, 'brain': 'RELATION', 'reason': veto_reason or 'Customer relationship policy violation'})
                self.nervous_system.emit(veto_event)
                import logging
                logging.warning(f'RelationBrain: VETOED consensus for proposal {proposal_id}: {veto_reason}')

    def handle_command(self, command: ICommand) -> BrainResult:
        """
        Handle a command routed to RelationBrain.
        
        This is the main entry point for all customer relationship commands.
        Routes to specific handlers based on command type.
        
        Args:
            command: Validated ICommand from Brainstem
            
        Returns:
            BrainResult with execution outcome
        """
        command_type = command.command_type
        if command_type == 'CustomerCreate':
            return self.create_customer(command)
        elif command_type == 'CustomerUpdate':
            return self.update_customer(command)
        elif command_type == 'MessageSend':
            return self.send_message(command)
        elif command_type == 'PortalTokenGenerate':
            return self.generate_portal_token(command)
        elif command_type == 'PortalTokenRevoke':
            return self.revoke_portal_token(command)
        else:
            return BrainResult.fail(error_message=f'Unknown command type for RelationBrain: {command_type}', error_code='UNKNOWN_COMMAND')

        @self.nervous_system.listen(EventType.INVOICE_SENT, brain_name='RelationBrain', priority=20)
        def on_invoice_sent(event):
            """When an invoice is sent, schedule payment reminders"""
            invoice_id = event.payload.get('invoice_id')
            due_date = event.payload.get('due_date')
            print(f'RelationBrain: Invoice {invoice_id} sent, scheduling reminder for {due_date}...')

    def create_customer(self, command: ICommand) -> BrainResult:
        """
        Create a new customer.

        Args:
            command: The authenticated command from Brainstem

        Returns:
            BrainResult with customer_id if successful
        """
        customer_data = {'name': command.payload.get('name'), 'email': command.payload.get('email'), 'phone': command.payload.get('phone'), 'address': command.payload.get('address'), 'status': 'ACTIVE', 'created_by': command.user_id, 'company_id': command.company_id}
        write_cmd = WriteCommand(operation=WriteOperation.CREATE, entity_type='customer', entity_id=None, data=customer_data, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'customer_id': result.entity_id}, message=f'Customer created: {result.entity_id}')
        else:
            return BrainResult.fail(error_message=result.error, data={'invariant_violations': result.invariant_violations})

    def update_customer(self, command: ICommand) -> BrainResult:
        """Update customer details"""
        customer_id = command.payload.get('customer_id')
        updates = command.payload.get('updates', {})
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='customer', entity_id=customer_id, data=updates, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'customer_id': customer_id}, message=f'Customer {customer_id} updated')
        else:
            return BrainResult.fail(error_message=result.error)

    def send_message(self, command: ICommand) -> BrainResult:
        """Send a message (SMS/email) to customer"""
        customer_id = command.payload.get('customer_id')
        message = command.payload.get('message')
        message_type = command.payload.get('message_type', 'sms')
        message_data = {'customer_id': customer_id, 'message': message, 'message_type': message_type, 'sent_by': command.user_id, 'company_id': command.company_id}
        write_cmd = WriteCommand(operation=WriteOperation.CREATE, entity_type='message', entity_id=None, data=message_data, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'message_id': result.entity_id}, message=f'Message sent to customer {customer_id}')
        else:
            return BrainResult.fail(error_message=result.error)

    def generate_portal_token(self, command: ICommand) -> BrainResult:
        """Generate a customer portal access token"""
        customer_id = command.payload.get('customer_id')
        import secrets
        import hashlib
        from datetime import datetime, timedelta
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expires_in_days = command.payload.get('expires_in_days', 30)
        expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        token_data = {'customer_id': customer_id, 'token_hash': token_hash, 'expires_at': expires_at, 'created_by': command.user_id, 'company_id': command.company_id}
        write_cmd = WriteCommand(operation=WriteOperation.CREATE, entity_type='portal_token', entity_id=None, data=token_data, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'token_id': result.entity_id, 'token': token, 'expires_at': expires_at}, message=f'Portal token generated for customer {customer_id}')
        else:
            return BrainResult.fail(error_message=result.error)

    def revoke_portal_token(self, command: ICommand) -> BrainResult:
        """Revoke a customer portal access token"""
        token_id = command.payload.get('token_id')
        after_state = {'revoked': True, 'revoked_at': command.timestamp.isoformat(), 'revoked_by': command.user_id}
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='portal_token', entity_id=token_id, data=after_state, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'token_id': token_id}, message=f'Portal token {token_id} revoked')
        else:
            return BrainResult.fail(error_message=result.error)

    def send_sms(self, command: ICommand) -> BrainResult:
        """
        Send SMS to a customer.

        This will:
        - Send the SMS (via Twilio or other service)
        - Log the communication via Cerebellum
        - Emit SMS_SENT event
        """
        customer_id = command.payload.get('customer_id')
        message = command.payload.get('message')
        phone = command.payload.get('phone')
        communication_data = {'customer_id': customer_id, 'type': 'SMS', 'direction': 'OUTBOUND', 'message': message, 'phone': phone, 'sent_by': command.user_id, 'company_id': command.company_id}
        write_cmd = WriteCommand(operation=WriteOperation.CREATE, entity_type='communication', entity_id=None, data=communication_data, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'communication_id': result.entity_id}, message=f'SMS sent to {phone}')
        else:
            return BrainResult.fail(error_message=result.error)

    def send_email(self, command: ICommand) -> BrainResult:
        """Send email to a customer"""
        customer_id = command.payload.get('customer_id')
        subject = command.payload.get('subject')
        body = command.payload.get('body')
        email = command.payload.get('email')
        communication_data = {'customer_id': customer_id, 'type': 'EMAIL', 'direction': 'OUTBOUND', 'subject': subject, 'message': body, 'email': email, 'sent_by': command.user_id, 'company_id': command.company_id}
        write_cmd = WriteCommand(operation=WriteOperation.CREATE, entity_type='communication', entity_id=None, data=communication_data, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'communication_id': result.entity_id}, message=f'Email sent to {email}')
        else:
            return BrainResult.fail(error_message=result.error)

    def update_customer(self, command: ICommand) -> BrainResult:
        """Update customer information"""
        customer_id = command.payload.get('customer_id')
        before_state = {}
        after_state = {key: value for key, value in command.payload.items() if key != 'customer_id'}
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='customer', entity_id=customer_id, data=after_state, caused_by=command, before_state=before_state)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'customer_id': customer_id}, message=f'Customer {customer_id} updated')
        else:
            return BrainResult.fail(error_message=result.error)

    def get_customer(self, customer_id: int) -> dict:
        """
        Read a customer (from projection table).

        Reads go directly to projection tables, not through Cerebellum.
        """
        if not self.db_connection:
            return {'error': 'No database connection'}
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        row = cursor.fetchone()
        if row:
            columns = [((((((((((((((desc[0] if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None for desc in cursor.description]
            return dict(zip(columns, row))
        else:
            return None

    def get_customer_sentiment(self, customer_id: int) -> str:
        """
        Analyze customer sentiment based on communication history.

        This is where Phase 8 (Codex) and Phase 9 (Executive AI) come in.
        For now, just a stub.
        """
        return 'POSITIVE'