"""
OpsBrain - The Foreman

Responsibilities:
- Jobs (create, update, schedule, complete)
- Crew management
- Time tracking
- Materials and inventory
- Scheduling

The OpsBrain is a "Thinker" - it computes what should happen.
It NEVER writes to the database directly.
It sends WriteCommands to the Cerebellum.

Communication:
- Receives commands from Brainstem (after authentication)
- Sends WriteCommands to Cerebellum
- Emits events to Nervous System (via Cerebellum)
- Listens to events from other brains (via Nervous System)
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
from typing import Optional
import sqlite3
from brain.core.contracts import ICommand, EventType
from brain.core.cerebellum import Cerebellum, WriteCommand, WriteOperation, WriteResult
from brain.nervous_system import NervousSystem
from brain.core.result import BrainResult
from brain.core import cerebellum
from brain import nervous_system

class OpsBrain:
    """
    Phase 5: OpsBrain - The Foreman

    Handles all operational aspects:
    - Job lifecycle (create → schedule → in-progress → complete)
    - Crew assignments
    - Time tracking
    - Materials management
    - Scheduling

    The OpsBrain THINKS but doesn't WRITE.
    All writes go through the Cerebellum.

    Example Flow:
        1. User creates a job (via UI)
        2. Brainstem authenticates the command
        3. OpsBrain receives the command
        4. OpsBrain computes job data
        5. OpsBrain sends WriteCommand to Cerebellum
        6. Cerebellum checks invariants and writes to Ledger
        7. Cerebellum emits JOB_CREATED event
        8. FinanceBrain hears JOB_CREATED → prepares quote
        9. RelationBrain hears JOB_CREATED → notifies customer
    """

    def __init__(self, cerebellum: Cerebellum, nervous_system: NervousSystem, db_connection: Optional[sqlite3.Connection]=None):
        """
        Initialize OpsBrain.

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
        shard_hex = os.getenv('OPS_BRAIN_SHARD')
        if shard_hex:
            try:
                return bytes.fromhex(shard_hex)
            except ValueError:
                import logging
                logging.warning('Invalid OPS_BRAIN_SHARD format, expected hex string')
        import secrets
        return secrets.token_bytes(32)

    def _register_listeners(self):
        """Register listeners for events from other brains"""

        @self.nervous_system.listen(EventType.QUOTE_ACCEPTED, brain_name='OpsBrain', priority=10)
        def on_quote_accepted(event):
            """When a quote is accepted, create/update the job"""
            quote_id = event.payload.get('quote_id')
            job_id = event.payload.get('job_id')
            print(f'OpsBrain: Quote {quote_id} accepted, job {job_id} now BOOKED')

        @self.nervous_system.listen(EventType.CONSENSUS_REQUESTED, brain_name='OpsBrain', priority=100)
        def on_consensus_requested(event):
            """
            Evaluate a consensus request from operational perspective.
            
            OpsBrain's Logic Gate:
            - Verify operational feasibility
            - Check scheduling constraints
            - Ensure no active jobs are disrupted
            """
            proposal_id = event.payload.get('proposal_id')
            command_type = event.payload.get('command_type')
            entity_type = event.payload.get('entity_type')
            entity_id = event.payload.get('entity_id')
            should_approve = True
            veto_reason = None
            if command_type == 'DELETE' and entity_type == 'job':
                if self.db_connection:
                    try:
                        cursor = self.db_connection.cursor()
                        cursor.execute('SELECT status FROM jobs WHERE id = ?', (entity_id,))
                        result = cursor.fetchone()
                        if result:
                            status = (((((((((((((((result[0] if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if hasattr(result, '__getitem__') else result.get('status', 0)
                            if status in ['IN_PROGRESS', 'SCHEDULED']:
                                should_approve = False
                                veto_reason = 'Cannot delete active job - crew may be on-site'
                    except Exception as e:
                        should_approve = False
                        veto_reason = f'Unable to verify job status: {e}'
            if should_approve and self._my_secret_shard:
                from brain.core.contracts import create_event
                shard_event = create_event(event_type=EventType.KEY_SHARD_RELEASED, caused_by_command_id=event.caused_by_command_id, caused_by_user_id=event.caused_by_user_id, payload={'proposal_id': proposal_id, 'shard': self._my_secret_shard.hex(), 'brain': 'OPS'})
                self.nervous_system.emit(shard_event)
                import logging
                logging.info(f'OpsBrain: Approved consensus for proposal {proposal_id}')
            else:
                from brain.core.contracts import create_event
                veto_event = create_event(event_type=EventType.CONSENSUS_VETO, caused_by_command_id=event.caused_by_command_id, caused_by_user_id=event.caused_by_user_id, payload={'proposal_id': proposal_id, 'brain': 'OPS', 'reason': veto_reason or 'Operational policy violation'})
                self.nervous_system.emit(veto_event)
                import logging
                logging.warning(f'OpsBrain: VETOED consensus for proposal {proposal_id}: {veto_reason}')

    def create_job(self, command: ICommand) -> BrainResult:
        """
        Create a new job.

        Args:
            command: The authenticated command from Brainstem

        Returns:
            BrainResult with job_id if successful
        """
        job_data = {'name': command.payload.get('name'), 'customer_id': command.payload.get('customer_id'), 'description': command.payload.get('description'), 'status': 'DRAFT', 'created_by': command.user_id, 'company_id': command.company_id}
        write_cmd = WriteCommand(operation=WriteOperation.CREATE, entity_type='job', entity_id=None, data=job_data, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'job_id': result.entity_id}, message=f'Job created: {result.entity_id}')
        else:
            return BrainResult.fail(error_message=result.error, data={'invariant_violations': result.invariant_violations})

    def handle_command(self, command: ICommand) -> BrainResult:
        """
        Handle a command routed to OpsBrain.
        
        This is the main entry point for all operations commands.
        Routes to specific handlers based on command type.
        
        Args:
            command: Validated ICommand from Brainstem
            
        Returns:
            BrainResult with execution outcome
        """
        command_type = command.command_type
        if command_type == 'JobCreate':
            return self.create_job(command)
        elif command_type == 'JobComplete':
            return self.complete_job(command)
        elif command_type == 'JobUpdate':
            return self.update_job(command)
        elif command_type == 'JobSchedule':
            return self.schedule_job(command)
        elif command_type == 'JobStart':
            return self.start_job(command)
        elif command_type == 'JobCancel':
            return self.cancel_job(command)
        elif command_type == 'CrewAssign':
            return self.assign_crew(command)
        elif command_type == 'CrewUnassign':
            return self.unassign_crew(command)
        elif command_type == 'MaterialCreate':
            return self.create_material(command)
        elif command_type == 'MaterialUpdate':
            return self.update_material(command)
        elif command_type == 'TimeTrack':
            return self.track_time(command)
        else:
            return BrainResult.fail(error_message=f'Unknown command type for OpsBrain: {command_type}', error_code='UNKNOWN_COMMAND')

    def complete_job(self, command: ICommand) -> BrainResult:
        """
        Mark a job as complete.

        This will trigger:
        - JOB_COMPLETED event → FinanceBrain creates invoice
        - JOB_COMPLETED event → RelationBrain sends thank you
        """
        job_id = command.payload.get('job_id')
        completion_notes = command.payload.get('notes', '')
        before_state = {'status': 'IN_PROGRESS'}
        after_state = {'status': 'COMPLETED', 'completed_at': command.timestamp.isoformat(), 'completion_notes': completion_notes}
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='job', entity_id=job_id, data=after_state, caused_by=command, before_state=before_state)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'job_id': job_id, 'status': 'COMPLETED'}, message=f'Job {job_id} completed')
        else:
            return BrainResult.fail(error_message=result.error, data={'invariant_violations': result.invariant_violations})

    def schedule_job(self, command: ICommand) -> BrainResult:
        """Schedule a job for a specific date/time"""
        job_id = command.payload.get('job_id')
        scheduled_date = command.payload.get('scheduled_date')
        crew_ids = command.payload.get('crew_ids', [])
        after_state = {'status': 'SCHEDULED', 'scheduled_date': scheduled_date, 'crew_ids': crew_ids}
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='job', entity_id=job_id, data=after_state, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'job_id': job_id, 'scheduled_date': scheduled_date}, message=f'Job {job_id} scheduled for {scheduled_date}')
        else:
            return BrainResult.fail(error_message=result.error)

    def get_job(self, job_id: int) -> dict:
        """
        Read a job (from projection table).

        Note: Reads DON'T go through Cerebellum.
        Reads go directly to projection tables (fast).
        """
        if not self.db_connection:
            return {'error': 'No database connection'}
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        if row:
            columns = [((((((((((((((desc[0] if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None for desc in cursor.description]
            return dict(zip(columns, row))
        else:
            return None

    def update_job(self, command: ICommand) -> BrainResult:
        """Update job details"""
        job_id = command.payload.get('job_id')
        updates = command.payload.get('updates', {})
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='job', entity_id=job_id, data=updates, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'job_id': job_id}, message=f'Job {job_id} updated')
        else:
            return BrainResult.fail(error_message=result.error)

    def start_job(self, command: ICommand) -> BrainResult:
        """Mark job as in progress"""
        job_id = command.payload.get('job_id')
        after_state = {'status': 'IN_PROGRESS', 'started_at': command.timestamp.isoformat()}
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='job', entity_id=job_id, data=after_state, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'job_id': job_id, 'status': 'IN_PROGRESS'}, message=f'Job {job_id} started')
        else:
            return BrainResult.fail(error_message=result.error)

    def cancel_job(self, command: ICommand) -> BrainResult:
        """Cancel a job"""
        job_id = command.payload.get('job_id')
        reason = command.payload.get('reason', '')
        after_state = {'status': 'CANCELLED', 'cancelled_at': command.timestamp.isoformat(), 'cancellation_reason': reason}
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='job', entity_id=job_id, data=after_state, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'job_id': job_id, 'status': 'CANCELLED'}, message=f'Job {job_id} cancelled')
        else:
            return BrainResult.fail(error_message=result.error)

    def assign_crew(self, command: ICommand) -> BrainResult:
        """Assign crew members to a job"""
        job_id = command.payload.get('job_id')
        crew_ids = command.payload.get('crew_ids', [])
        after_state = {'crew_ids': crew_ids}
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='job', entity_id=job_id, data=after_state, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'job_id': job_id, 'crew_ids': crew_ids}, message=f'Crew assigned to job {job_id}')
        else:
            return BrainResult.fail(error_message=result.error)

    def unassign_crew(self, command: ICommand) -> BrainResult:
        """Remove crew members from a job"""
        job_id = command.payload.get('job_id')
        crew_ids = command.payload.get('crew_ids', [])
        after_state = {'crew_ids': []}
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='job', entity_id=job_id, data=after_state, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'job_id': job_id}, message=f'Crew unassigned from job {job_id}')
        else:
            return BrainResult.fail(error_message=result.error)

    def create_material(self, command: ICommand) -> BrainResult:
        """Create a new material/inventory item"""
        material_data = {'name': command.payload.get('name'), 'description': command.payload.get('description'), 'unit': command.payload.get('unit'), 'cost_per_unit': command.payload.get('cost_per_unit'), 'created_by': command.user_id, 'company_id': command.company_id}
        write_cmd = WriteCommand(operation=WriteOperation.CREATE, entity_type='material', entity_id=None, data=material_data, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'material_id': result.entity_id}, message=f'Material created: {result.entity_id}')
        else:
            return BrainResult.fail(error_message=result.error)

    def update_material(self, command: ICommand) -> BrainResult:
        """Update material/inventory item"""
        material_id = command.payload.get('material_id')
        updates = command.payload.get('updates', {})
        write_cmd = WriteCommand(operation=WriteOperation.UPDATE, entity_type='material', entity_id=material_id, data=updates, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'material_id': material_id}, message=f'Material {material_id} updated')
        else:
            return BrainResult.fail(error_message=result.error)

    def track_time(self, command: ICommand) -> BrainResult:
        """Track time for a job"""
        time_data = {'job_id': command.payload.get('job_id'), 'user_id': command.payload.get('user_id', command.user_id), 'hours': command.payload.get('hours'), 'date': command.payload.get('date'), 'notes': command.payload.get('notes', ''), 'created_by': command.user_id, 'company_id': command.company_id}
        write_cmd = WriteCommand(operation=WriteOperation.CREATE, entity_type='time_entry', entity_id=None, data=time_data, caused_by=command)
        result = self.cerebellum.execute(write_cmd)
        if result.success:
            return BrainResult.ok(data={'time_entry_id': result.entity_id}, message=f'Time tracked: {result.entity_id}')
        else:
            return BrainResult.fail(error_message=result.error)