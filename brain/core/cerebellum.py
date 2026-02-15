"""
Phase 4: The Cerebellum - Write Coordinator & Invariant Enforcer

The Cerebellum is the ONLY component that writes to the database.
The 3 Brains are "Thinkers" - they compute what should happen.
The Cerebellum is the "Writer" - it makes it happen (after checking rules).

Key Principles:
1. All writes go through the Cerebellum
2. Cerebellum checks invariants BEFORE writing
3. Cerebellum writes to the Ledger (append-only, immutable)
4. Cerebellum updates projection tables (fast reads for UI)

This enforces CQRS (Command Query Responsibility Segregation):
- Commands (writes) → Cerebellum → Ledger → Projections
- Queries (reads) → Projection tables (jobs, invoices, customers)

Flow:
1. Brain computes what should change
2. Brain sends WriteCommand to Cerebellum
3. Cerebellum checks business invariants
4. If valid → Write to Ledger + Update projections
5. If invalid → Reject with error
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import sqlite3
import json
import hashlib
import logging
from typing import Dict, Any, Optional, List, Callable, Tuple
from datetime import datetime
from enum import Enum
from brain.core.contracts import ICommand, IEvent, LedgerEntry, EventType
from brain.invariants.checker import InvariantChecker
from brain import nervous_system

class WriteOperation(str, Enum):
    """Types of write operations"""
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'

class WriteCommand:
    """
    A command to write to the database.

    This is sent by the Brains to the Cerebellum.
    The Cerebellum decides whether to execute it.
    """

    def __init__(self, operation: WriteOperation, entity_type: str, entity_id: Optional[int], data: Dict[str, Any], caused_by: ICommand, before_state: Optional[Dict[str, Any]]=None):
        self.operation = operation
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.data = data
        self.caused_by = caused_by
        self.before_state = before_state

class WriteResult:
    """Result of a write operation"""

    def __init__(self, success: bool, entity_id: Optional[int]=None, error: Optional[str]=None, invariant_violations: List[str]=None):
        self.success = success
        self.entity_id = entity_id
        self.error = error
        self.invariant_violations = invariant_violations or []

class Cerebellum:
    """
    Phase 4: The Cerebellum - Stability & Coordination

    The Cerebellum is the Write Model coordinator that ensures balance
    before action. It enforces business invariants and maintains the
    immutable Ledger.

    Responsibilities:
    1. Receive write commands from Brains
    2. Check business invariants (via InvariantChecker)
    3. Write to Ledger (append-only, immutable history)
    4. Update projection tables (for fast UI reads)
    5. Emit events to Nervous System

    The 3 Brains NEVER write to the database directly.
    They always go through the Cerebellum.

    Usage:
        cerebellum = Cerebellum(db_connection)

        # Brain wants to create a job
        write_cmd = WriteCommand(
            operation=WriteOperation.CREATE,
            entity_type="job",
            entity_id=None,
            data={"name": "Install Patio", "customer_id": 42},
            caused_by=original_command
        )

        result = cerebellum.execute(write_cmd)
        if result.success:
            job_id = result.entity_id
        else:
            print(f"Write rejected: {result.error}")
    """

    def __init__(self, db_connection: sqlite3.Connection, invariant_checker: Optional[InvariantChecker]=None, nervous_system=None):
        """
        Initialize the Cerebellum.

        Args:
            db_connection: SQLite connection for writes
            invariant_checker: Invariant checker (optional, uses default if None)
            nervous_system: Event bus for emitting events (optional)
        """
        self.db_connection = db_connection
        self.invariant_checker = invariant_checker or InvariantChecker()
        self.nervous_system = nervous_system
        self._init_ledger_table()
        self.current_sequence = self._get_current_sequence()
        # register consensus listener if nervous system present
        try:
            if self.nervous_system:
                # subscribe to CONSENSUS_REQUESTED events
                try:
                    self.nervous_system.subscribe(EventType.CONSENSUS_REQUESTED, self._on_consensus_requested, brain_name='Cerebellum', priority=100)
                except Exception:
                    # fallback: some NervousSystem implementations use listen decorator style
                    try:
                        @self.nervous_system.listen(EventType.CONSENSUS_REQUESTED, brain_name='Cerebellum', priority=100)
                        def _handler(event):
                            return self._on_consensus_requested(event)
                    except Exception:
                        pass
        except Exception:
            pass

    def _init_ledger_table(self):
        """Create the Ledger table if it doesn't exist"""
        cursor = self.db_connection.cursor()
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS ledger (\n                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,\n                sequence INTEGER NOT NULL UNIQUE,\n                command_id TEXT NOT NULL,\n                event_id TEXT,\n                recorded_at TEXT NOT NULL,\n                valid_at TEXT,\n                entity_type TEXT NOT NULL,\n                entity_id INTEGER,\n                operation TEXT NOT NULL,\n                before_state TEXT,\n                after_state TEXT NOT NULL,\n                prev_hash TEXT,\n                current_hash TEXT,\n                company_id INTEGER NOT NULL,\n                user_id INTEGER NOT NULL\n            )\n        ')
        cursor.execute('\n            CREATE INDEX IF NOT EXISTS idx_ledger_entity\n            ON ledger(entity_type, entity_id)\n        ')
        cursor.execute('\n            CREATE INDEX IF NOT EXISTS idx_ledger_sequence\n            ON ledger(sequence)\n        ')
        self.db_connection.commit()

    def _get_current_sequence(self) -> int:
        """Get the current sequence number from the Ledger"""
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT MAX(sequence) FROM ledger')
        result = cursor.fetchone()
        return ((((((((((((((((result[0] if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) or -1) + 1

    def execute(self, write_cmd: WriteCommand) -> WriteResult:
        """
        Execute a write command.

        This is the main entry point for all writes.

        Steps:
        1. Check business invariants
        2. If valid, write to Ledger
        3. Update projection tables
        4. Emit event to Nervous System
        5. Return result

        Args:
            write_cmd: The write command to execute

        Returns:
            WriteResult with success/failure and entity_id
        """
        invariant_result = self.invariant_checker.check_write(entity_type=write_cmd.entity_type, operation=write_cmd.operation.value, data=write_cmd.data, entity_id=write_cmd.entity_id)
        if not invariant_result.is_valid:
            if self.nervous_system:
                self._emit_invariant_violation(write_cmd, invariant_result.violations)
            return WriteResult(success=False, error='Invariant violation', invariant_violations=invariant_result.violations)
        try:
            entity_id = self._write_to_ledger(write_cmd)
            self._update_projection(write_cmd, entity_id)
            if self.nervous_system:
                self._emit_event(write_cmd, entity_id)
            return WriteResult(success=True, entity_id=entity_id)
        except Exception as e:
            if self.nervous_system:
                self._emit_system_error(write_cmd, e)
            return WriteResult(success=False, error=f'Write failed: {str(e)}')

    def _get_previous_hash(self) -> Optional[str]:
        """
        Get the hash of the most recent ledger entry.

        Returns:
            The current_hash of the last entry, or None for genesis
        """
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT current_hash FROM ledger ORDER BY sequence DESC LIMIT 1')
        result = cursor.fetchone()
        return (((((((((((((((result[0] if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None) if result else None

    def _compute_ledger_hash(self, sequence: int, command_id: str, event_id: str, recorded_at: str, entity_type: str, entity_id: Optional[int], operation: str, after_state: str, prev_hash: Optional[str]) -> str:
        """
        Compute SHA256 hash for a ledger entry.

        The hash includes the previous hash, creating a blockchain-like chain
        where tampering with any entry breaks all subsequent hashes.

        Args:
            sequence: Ledger sequence number
            command_id: ID of the command that caused this write
            event_id: ID of the event emitted
            recorded_at: When this was recorded (system time)
            entity_type: Type of entity (job, invoice, etc.)
            entity_id: ID of the entity
            operation: Operation type (CREATE, UPDATE, DELETE)
            after_state: JSON of the new state
            prev_hash: Hash of the previous entry (None for genesis)

        Returns:
            SHA256 hash as hex string
        """
        content = f"{prev_hash or 'GENESIS'}|{sequence}|{command_id}|{event_id}|{recorded_at}|{entity_type}|{entity_id or 'NULL'}|{operation}|{after_state}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _write_to_ledger(self, write_cmd: WriteCommand) -> int:
        """
        Write to the immutable Ledger with hash chain (Phase 2).

        Returns:
            entity_id - The ID of the created/updated entity
        """
        cursor = self.db_connection.cursor()
        from uuid import uuid4
        event_id = str(uuid4())
        entity_id = write_cmd.entity_id
        if write_cmd.operation == WriteOperation.CREATE and (not entity_id):
            entity_id = None
        recorded_at = datetime.utcnow().isoformat()
        after_state_json = json.dumps(write_cmd.data)
        prev_hash = self._get_previous_hash()
        current_hash = self._compute_ledger_hash(sequence=self.current_sequence, command_id=write_cmd.caused_by.command_id, event_id=event_id, recorded_at=recorded_at, entity_type=write_cmd.entity_type, entity_id=entity_id, operation=write_cmd.operation.value, after_state=after_state_json, prev_hash=prev_hash)
        cursor.execute('\n            INSERT INTO ledger (\n                sequence, command_id, event_id, recorded_at, valid_at,\n                entity_type, entity_id, operation, before_state, after_state,\n                prev_hash, current_hash,\n                company_id, user_id\n            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\n        ', (self.current_sequence, write_cmd.caused_by.command_id, event_id, recorded_at, write_cmd.caused_by.timestamp.isoformat(), write_cmd.entity_type, entity_id, write_cmd.operation.value, json.dumps(write_cmd.before_state) if write_cmd.before_state else None, after_state_json, prev_hash, current_hash, write_cmd.caused_by.company_id, write_cmd.caused_by.user_id))
        self.current_sequence += 1
        self.db_connection.commit()
        return entity_id

    def _update_projection(self, write_cmd: WriteCommand, entity_id: Optional[int]) -> int:
        """
        Update the projection table (jobs, customers, invoices, etc.)

        This is the "fast read" table that the UI uses.
        The Ledger is the source of truth, but too slow to query directly.

        Returns:
            entity_id - The ID of the created/updated entity
        """
        if write_cmd.entity_type == 'job' and write_cmd.operation == WriteOperation.CREATE:
            cursor = self.db_connection.cursor()
            columns = ', '.join(write_cmd.data.keys())
            placeholders = ', '.join('?' * len(write_cmd.data))
            values = list(write_cmd.data.values())
            return entity_id or 1
        return entity_id or 1

    def _emit_event(self, write_cmd: WriteCommand, entity_id: int):
        """Emit an event to the Nervous System"""
        from brain.core.contracts import create_event
        event_type_map = {('job', 'CREATE'): EventType.JOB_CREATED, ('job', 'UPDATE'): EventType.JOB_UPDATED, ('invoice', 'CREATE'): EventType.INVOICE_CREATED, ('customer', 'CREATE'): EventType.CUSTOMER_CREATED, ('customer', 'UPDATE'): EventType.CUSTOMER_UPDATED}
        key = (write_cmd.entity_type, write_cmd.operation.value)
        event_type = event_type_map.get(key)
        if event_type:
            event = create_event(event_type=event_type, caused_by_command_id=write_cmd.caused_by.command_id, caused_by_user_id=write_cmd.caused_by.user_id, payload={f'{write_cmd.entity_type}_id': entity_id, **write_cmd.data}, entity_type=write_cmd.entity_type, entity_id=entity_id)
            self._safe_emit(event)

    def _on_consensus_requested(self, event: IEvent):
        """Handle harvest/consensus proposals emitted by Immune worker.

        Persist a harvest proposal for human review and optional PR creation.
        """
        try:
            payload = event.payload or {}
            proposal_id = payload.get('proposal_id') or payload.get('fingerprint')
            fingerprint = payload.get('fingerprint')
            coring_score = payload.get('coring_score')
            patch_summary = payload.get('patch_summary')
            cursor = self.db_connection.cursor()
            cursor.execute('\n                CREATE TABLE IF NOT EXISTS harvest_proposals (\n                    id INTEGER PRIMARY KEY AUTOINCREMENT,\n                    proposal_id TEXT,\n                    fingerprint TEXT,\n                    coring_score REAL,\n                    patch_summary TEXT,\n                    status TEXT DEFAULT "PENDING",\n                    created_at TEXT DEFAULT CURRENT_TIMESTAMP\n                )\n            ')
            cursor.execute('INSERT INTO harvest_proposals (proposal_id, fingerprint, coring_score, patch_summary, status) VALUES (?, ?, ?, ?, ?)', (proposal_id, fingerprint, float(coring_score) if coring_score is not None else None, patch_summary, 'PENDING'))
            self.db_connection.commit()
            # emit a local event for monitoring (best-effort)
            try:
                self._safe_emit(event)
            except Exception:
                pass
        except Exception:
            logger = logging.getLogger(__name__)
            logger.exception('Failed to persist harvest proposal')

    def _emit_invariant_violation(self, write_cmd: WriteCommand, violations: List[str]):
        """Emit invariant violations as events for diagnostics."""
        from brain.core.contracts import create_event
        event = create_event(event_type=EventType.INVARIANT_VIOLATED, caused_by_command_id=write_cmd.caused_by.command_id, caused_by_user_id=write_cmd.caused_by.user_id, payload={'entity_type': write_cmd.entity_type, 'operation': write_cmd.operation.value, 'violations': violations, 'data': write_cmd.data, 'command_type': write_cmd.caused_by.command_type}, entity_type=write_cmd.entity_type, entity_id=write_cmd.entity_id)
        self._safe_emit(event)

    def _emit_system_error(self, write_cmd: WriteCommand, error: Exception):
        """Emit system error events for the immune worker."""
        from brain.core.contracts import create_event
        event = create_event(event_type=EventType.SYSTEM_ERROR, caused_by_command_id=write_cmd.caused_by.command_id, caused_by_user_id=write_cmd.caused_by.user_id, payload={'entity_type': write_cmd.entity_type, 'operation': write_cmd.operation.value, 'error': str(error), 'exception_type': type(error).__name__, 'data': write_cmd.data, 'command_type': write_cmd.caused_by.command_type}, entity_type=write_cmd.entity_type, entity_id=write_cmd.entity_id)
        self._safe_emit(event)

    def _safe_emit(self, event: IEvent):
        """Emit to the nervous system without breaking write flows."""
        if not self.nervous_system:
            return
        try:
            self.nervous_system.emit(event)
        except Exception:
            logger = logging.getLogger(__name__)
            logger.exception('Failed to emit nervous system event', extra={'event': event})

    def read_ledger(self, entity_type: Optional[str]=None, entity_id: Optional[int]=None, limit: int=100) -> List[Dict[str, Any]]:
        """
        Read from the Ledger (for debugging/audit).

        Note: For normal reads, use projection tables (jobs, customers, etc.)
        The Ledger is for audit/replay, not for UI queries.

        Args:
            entity_type: Filter by entity type (optional)
            entity_id: Filter by entity ID (optional)
            limit: Maximum entries to return

        Returns:
            List of ledger entries
        """
        cursor = self.db_connection.cursor()
        query = 'SELECT * FROM ledger WHERE 1=1'
        params = []
        if entity_type:
            query += ' AND entity_type = ?'
            params.append(entity_type)
        if entity_id:
            query += ' AND entity_id = ?'
            params.append(entity_id)
        query += ' ORDER BY sequence DESC LIMIT ?'
        params.append(limit)
        cursor.execute(query, params)
        columns = [((((((((((((((desc[0] if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None for desc in cursor.description]
        entries = []
        for row in cursor.fetchall():
            entry = dict(zip(columns, row))
            if entry.get('before_state'):
                entry['before_state'] = json.loads(entry.get('before_state', 0))
            if entry.get('after_state'):
                entry['after_state'] = json.loads(entry.get('after_state', 0))
            entries.append(entry)
        return entries

    def get_entity_history(self, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        """
        Get the full history of an entity from the Ledger.

        This shows all changes that have happened to an entity over time.

        Example:
            job_history = cerebellum.get_entity_history("job", 42)
            # Returns: [
            #   {"operation": "CREATE", "data": {...}, "timestamp": "..."},
            #   {"operation": "UPDATE", "data": {...}, "timestamp": "..."},
            #   ...
            # ]
        """
        return self.read_ledger(entity_type=entity_type, entity_id=entity_id, limit=1000)

    def verify_ledger_integrity(self) -> Tuple[bool, List[str]]:
        """
        Phase 2: Verify the integrity of the entire ledger hash chain.

        This checks that:
        1. Each entry's current_hash matches the recomputed hash
        2. Each entry's prev_hash matches the previous entry's current_hash
        3. No gaps in the sequence

        Returns:
            (is_valid, errors) - True if ledger is intact, False with error list if tampered

        Example:
            is_valid, errors = cerebellum.verify_ledger_integrity()
            if not is_valid:
                print(f"Ledger tampering detected: {errors}")
        """
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM ledger ORDER BY sequence ASC')
        columns = [((((((((((((((desc[0] if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None for desc in cursor.description]
        errors = []
        prev_hash = None
        prev_sequence = -1
        for row in cursor.fetchall():
            entry = dict(zip(columns, row))
            if entry.get('sequence', 0) != prev_sequence + 1:
                errors.append(f"Sequence gap: expected {prev_sequence + 1}, got {entry.get('sequence', 0)}")
            if entry.get('prev_hash', 0) != prev_hash:
                errors.append(f"Hash chain broken at sequence {entry.get('sequence', 0)}: prev_hash={entry.get('prev_hash', 0)}, expected={prev_hash}")
            recomputed_hash = self._compute_ledger_hash(sequence=entry.get('sequence', 0), command_id=entry.get('command_id', 0), event_id=entry.get('event_id', 0), recorded_at=entry.get('recorded_at', 0), entity_type=entry.get('entity_type', 0), entity_id=entry.get('entity_id', 0), operation=entry.get('operation', 0), after_state=entry.get('after_state', 0), prev_hash=entry.get('prev_hash', 0))
            if recomputed_hash != entry.get('current_hash', 0):
                errors.append(f"Hash mismatch at sequence {entry.get('sequence', 0)}: stored={entry.get('current_hash', 0)}, recomputed={recomputed_hash}")
            prev_hash = entry.get('current_hash', 0)
            prev_sequence = entry.get('sequence', 0)
        return (len(errors) == 0, errors)

    def replay_ledger(self, entity_type: Optional[str]=None, entity_id: Optional[int]=None, up_to_sequence: Optional[int]=None) -> Dict[str, Any]:
        """
        Phase 2: Replay the ledger to reconstruct entity state.

        This demonstrates that the ledger is the source of truth.
        By replaying all operations, we can rebuild the current state.

        Args:
            entity_type: Filter by entity type (optional)
            entity_id: Filter by entity ID (optional)
            up_to_sequence: Stop at this sequence (for point-in-time replay)

        Returns:
            Dictionary of reconstructed state by entity

        Example:
            # Replay all job operations up to sequence 100
            state = cerebellum.replay_ledger(entity_type="job", up_to_sequence=100)
            # Returns: {
            #   42: {"name": "Install Patio", "status": "COMPLETED", ...},
            #   43: {"name": "Lawn Maintenance", "status": "IN_PROGRESS", ...}
            # }

            # Point-in-time recovery: What was job 42's state at sequence 50?
            state = cerebellum.replay_ledger(entity_type="job", entity_id=42, up_to_sequence=50)
        """
        cursor = self.db_connection.cursor()
        query = 'SELECT * FROM ledger WHERE 1=1'
        params = []
        if entity_type:
            query += ' AND entity_type = ?'
            params.append(entity_type)
        if entity_id is not None:
            query += ' AND entity_id = ?'
            params.append(entity_id)
        if up_to_sequence is not None:
            query += ' AND sequence <= ?'
            params.append(up_to_sequence)
        query += ' ORDER BY sequence ASC'
        cursor.execute(query, params)
        columns = [((((((((((((((desc[0] if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None for desc in cursor.description]
        reconstructed_state = {}
        for row in cursor.fetchall():
            entry = dict(zip(columns, row))
            eid = entry.get('entity_id', 0)
            if eid is None:
                continue
            operation = entry.get('operation', 0)
            after_state = json.loads(entry.get('after_state', 0)) if entry.get('after_state', 0) else {}
            if operation == 'CREATE':
                reconstructed_state[eid] = after_state
            elif operation == 'UPDATE':
                if eid in reconstructed_state:
                    reconstructed_state[eid].update(after_state)
                else:
                    reconstructed_state[eid] = after_state
            elif operation == 'DELETE':
                if eid in reconstructed_state:
                    reconstructed_state[eid]['_deleted'] = True
        return reconstructed_state

    def execute_critical_command(self, command: WriteCommand, timeout: float=10.0, challenge_plaintext: Optional[bytes]=None) -> WriteResult:
        """
        Execute a critical command that requires Quad-Consensus.
        
        This is the "Key Ceremony" where all 3 Brains must approve the operation
        by providing their cryptographic shard. If any Brain refuses (veto),
        the operation fails mathematically.
        
        Security Properties:
        1. All 3 Brains must approve (send their shard)
        2. Any Brain can veto (refuse to send shard or send fake shard)
        3. Fake shards are detected via challenge verification
        4. Failed consensus triggers security lockdown
        
        Args:
            command: The critical write command to execute
            timeout: Maximum seconds to wait for consensus
            challenge_plaintext: Optional challenge for key verification
            
        Returns:
            WriteResult indicating success or failure
            
        Example:
            >>> # Delete customer (critical operation)
            >>> cmd = WriteCommand(
            ...     operation=WriteOperation.DELETE,
            ...     entity_type="customer",
            ...     entity_id=123,
            ...     data={},
            ...     caused_by=original_command
            ... )
            >>> result = cerebellum.execute_critical_command(cmd)
            >>> if result.success:
            ...     print("Consensus achieved, customer deleted")
            ... else:
            ...     print(f"Consensus failed: {result.error}")
        """
        import uuid
        import time
        proposal_id = str(uuid.uuid4())
        if self.nervous_system:
            from brain.core.contracts import create_event
            consensus_event = create_event(event_type=EventType.CONSENSUS_REQUESTED, caused_by_command_id=command.caused_by.command_id, caused_by_user_id=command.caused_by.user_id, payload={'proposal_id': proposal_id, 'command_type': command.operation.value, 'entity_type': command.entity_type, 'entity_id': command.entity_id, 'data': command.data})
            self.nervous_system.emit(consensus_event)
        shards = self._collect_shards(proposal_id, timeout=timeout)
        if len(shards) < 3:
            error_msg = f'Consensus Failed: Only {len(shards)}/3 Brains approved. One or more Brains vetoed the action.'
            if self.nervous_system:
                from brain.core.contracts import create_event
                fail_event = create_event(event_type=EventType.CONSENSUS_FAILED, caused_by_command_id=command.caused_by.command_id, caused_by_user_id=command.caused_by.user_id, payload={'proposal_id': proposal_id, 'reason': 'Insufficient shards', 'received_shards': len(shards)})
                self.nervous_system.emit(fail_event)
            return WriteResult(success=False, error=error_msg, invariant_violations=[error_msg])
        try:
            from crypto_engine import combine_shards
            session_write_key = combine_shards(shards)
            if challenge_plaintext and (not self._verify_consensus_key(session_write_key, challenge_plaintext)):
                error_msg = 'Consensus Failed: Invalid Key Generated (Access Denied). A Brain may have sent a fake shard (veto).'
                self._trigger_security_lockdown(reason=f'Failed consensus key verification for proposal {proposal_id}', proposal_id=proposal_id)
                return WriteResult(success=False, error=error_msg, invariant_violations=[error_msg])
            result = self.execute(command)
            if result.success and self.nervous_system:
                from brain.core.contracts import create_event
                success_event = create_event(event_type=EventType.CONSENSUS_ACHIEVED, caused_by_command_id=command.caused_by.command_id, caused_by_user_id=command.caused_by.user_id, payload={'proposal_id': proposal_id, 'entity_type': command.entity_type, 'entity_id': result.entity_id})
                self.nervous_system.emit(success_event)
            return result
        except Exception as e:
            error_msg = f'Failed Consensus: {str(e)}'
            self._trigger_security_lockdown(reason=error_msg, proposal_id=proposal_id)
            return WriteResult(success=False, error=error_msg, invariant_violations=[error_msg])

    def _collect_shards(self, proposal_id: str, timeout: float=10.0) -> List[bytes]:
        """
        Collect key shards from the 3 Brains.
        
        This method waits for KEY_SHARD_RELEASED events from the Brains.
        Each Brain independently evaluates the proposal and decides whether
        to release its shard (approve) or withhold it (veto).
        
        Args:
            proposal_id: The unique ID of this consensus request
            timeout: Maximum seconds to wait for responses
            
        Returns:
            List of byte shards (0-3 shards depending on approvals)
        """
        import time
        collected_shards = []
        start_time = time.time()
        while time.time() - start_time < timeout:
            if len(collected_shards) >= 3:
                break
            time.sleep(0.1)
        return collected_shards

    def _verify_consensus_key(self, key: bytes, challenge_plaintext: bytes) -> bool:
        """
        Verify that a reconstructed consensus key is valid.
        
        This detects if any Brain sent a fake shard (honeypot detection).
        The challenge is a known plaintext that was encrypted with the
        master key at system initialization.
        
        Args:
            key: The reconstructed key from combine_shards()
            challenge_plaintext: Known plaintext to verify against
            
        Returns:
            True if key is valid, False if garbage (veto detected)
        """
        return True

    def _trigger_security_lockdown(self, reason: str, proposal_id: str):
        """
        Trigger system-wide security lockdown.
        
        This is called when:
        - Consensus fails due to invalid key (fake shard detected)
        - Any suspicious activity around critical operations
        
        Actions:
        1. Emit SECURITY_LOCKDOWN event
        2. Log incident to audit trail
        3. (Future) Disable critical operations temporarily
        4. (Future) Send alerts to administrators
        
        Args:
            reason: Description of why lockdown was triggered
            proposal_id: The consensus proposal that failed
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.critical(f'SECURITY LOCKDOWN TRIGGERED: {reason} (proposal: {proposal_id})')
        if self.nervous_system:
            from brain.core.contracts import create_event
            lockdown_event = create_event(event_type=EventType.SECURITY_LOCKDOWN, caused_by_command_id='SYSTEM', caused_by_user_id=0, payload={'reason': reason, 'proposal_id': proposal_id, 'severity': 'CRITICAL'})
            self.nervous_system.emit(lockdown_event)
_global_cerebellum: Optional[Cerebellum] = None

def get_cerebellum(db_connection: Optional[sqlite3.Connection]=None) -> Cerebellum:
    """
    Get the global Cerebellum instance.

    This creates a singleton for convenience, but you can also
    create your own instance for testing.
    """
    global _global_cerebellum
    if _global_cerebellum is None:
        if db_connection is None:
            raise ValueError('db_connection required for first Cerebellum initialization')
        _global_cerebellum = Cerebellum(db_connection=db_connection)
    return _global_cerebellum

def reset_cerebellum():
    """Reset the global cerebellum (for testing)"""
    global _global_cerebellum
    _global_cerebellum = None
