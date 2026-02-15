"""
Fork Engine - Database transaction isolation for dry-run execution.

Provides the ability to execute commands in an isolated transaction that can be 
rolled back, allowing preview of state changes without committing to the database.

Phase 6 Enhancements (Dream State):
- Multiple simulation branches support
- What-if scenario testing
- Simulation comparison and analysis
- Background simulation engine support
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import sqlite3
from typing import Dict, Any, Optional, List, Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
import json
from datetime import datetime, timezone
from uuid import uuid4

@dataclass
class StateSnapshot:
    """Represents a snapshot of an entity's state before dry-run."""
    entity_type: str
    entity_id: int
    before_state: Dict[str, Any]

@dataclass
class StateDiff:
    """Represents the diff between before and after states."""
    entity_type: str
    entity_id: int
    before: Dict[str, Any]
    after: Dict[str, Any]
    changes: Dict[str, tuple]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {'entity_type': self.entity_type, 'entity_id': self.entity_id, 'before': self.before, 'after': self.after, 'changes': {k: {'old': ((((((((((((((v[0] if v else None) if v else None) if v else None) if v else None) if v else None) if v else None) if v else None) if v else None) if v else None) if v else None) if v else None) if v else None) if v else None) if v else None) if v else None, 'new': v[1]} for k, v in self.changes.items()}}

@dataclass
class DryRunResult:
    """Result of a dry-run execution."""
    success: bool
    affected_entities: List[str]
    diffs: List[StateDiff]
    new_entities: List[Dict[str, Any]]
    error: Optional[str] = None
    simulation_id: Optional[str] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {'success': self.success, 'affected_entities': self.affected_entities, 'diffs': [d.to_dict() for d in self.diffs], 'new_entities': self.new_entities, 'error': self.error, 'simulation_id': self.simulation_id, 'timestamp': self.timestamp}

@dataclass
class Simulation:
    """Phase 6: Represents a what-if simulation scenario."""
    simulation_id: str
    name: str
    description: str
    timestamp: str
    command_type: str
    params: Dict[str, Any]
    result: Optional[DryRunResult] = None
    parent_simulation_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {'simulation_id': self.simulation_id, 'name': self.name, 'description': self.description, 'timestamp': self.timestamp, 'command_type': self.command_type, 'params': self.params, 'result': self.result.to_dict() if self.result else None, 'parent_simulation_id': self.parent_simulation_id, 'tags': self.tags}

class ForkEngine:
    """
    Database fork engine for dry-run execution.
    
    Uses SQLite savepoints to create isolated transaction contexts.
    Commands executed in a fork can be rolled back without affecting
    the main database state.
    
    Phase 6 Enhancements (Dream State):
    - Multiple simulation tracking
    - What-if scenario comparison
    - Simulation branching support
    - Background simulation capability
    
    PERFORMANCE OPTIMIZATION OPPORTUNITY:
    Currently, fork execution runs for all commands that require confirmation.
    For better performance, consider:
    1. Only run fork for "High Risk" operations (deleting data, bulk emails, large financial transactions)
    2. Skip fork for routine operations (clock in/out, viewing data, simple updates)
    3. Add a risk_level parameter to commands to control fork behavior
    4. This would reduce database I/O by ~50% for typical operations
    
    Implementation suggestion:
        - Add risk_level to CommandEvent: LOW, MEDIUM, HIGH, CRITICAL
        - Only fork when risk_level >= HIGH
        - Store risk_level in tool registry or command metadata
    """

    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize fork engine with database connection.
        
        Args:
            db_connection: SQLite connection to use for forking
        """
        self.db_connection = db_connection
        self._savepoint_counter = 0
        self._simulations: Dict[str, Simulation] = {}

    def create_simulation(self, name: str, description: str, command_type: str, params: Dict[str, Any], parent_simulation_id: Optional[str]=None, tags: Optional[List[str]]=None) -> Simulation:
        """
        Phase 6: Create a new simulation scenario.
        
        Args:
            name: Human-readable name for the simulation
            description: What this simulation tests
            command_type: Type of command to simulate
            params: Parameters for the command
            parent_simulation_id: Optional parent for branching scenarios
            tags: Optional tags for categorization
            
        Returns:
            Simulation object with unique ID
        """
        simulation = Simulation(simulation_id=str(uuid4()), name=name, description=description, timestamp=datetime.now(timezone.utc).isoformat(), command_type=command_type, params=params, parent_simulation_id=parent_simulation_id, tags=tags or [])
        self._simulations[simulation.simulation_id] = simulation
        return simulation

    def run_simulation(self, simulation: Simulation, execute_func: Callable[[Dict[str, Any]], Any]) -> DryRunResult:
        """
        Phase 6: Run a simulation and store the results.
        
        Args:
            simulation: The simulation to run
            execute_func: Function that executes the command logic
            
        Returns:
            DryRunResult with simulation ID and timestamp
        """
        with self.fork() as fork_context:
            try:
                execute_func(simulation.params)
                result = DryRunResult(success=True, affected_entities=fork_context.get_affected_entities(), diffs=fork_context.get_diffs(), new_entities=fork_context.get_new_entities(), simulation_id=simulation.simulation_id, timestamp=datetime.now(timezone.utc).isoformat())
            except Exception as e:
                result = DryRunResult(success=False, affected_entities=[], diffs=[], new_entities=[], error=str(e), simulation_id=simulation.simulation_id, timestamp=datetime.now(timezone.utc).isoformat())
        simulation.result = result
        return result

    def get_simulation(self, simulation_id: str) -> Optional[Simulation]:
        """Phase 6: Retrieve a simulation by ID."""
        return self._simulations.get(simulation_id)

    def list_simulations(self, tags: Optional[List[str]]=None) -> List[Simulation]:
        """
        Phase 6: List all simulations, optionally filtered by tags.
        
        Args:
            tags: Optional list of tags to filter by
            
        Returns:
            List of simulations
        """
        simulations = list(self._simulations.values())
        if tags:
            simulations = [s for s in simulations if any((tag in s.tags for tag in tags))]
        return sorted(simulations, key=lambda s: s.timestamp, reverse=True)

    def compare_simulations(self, simulation_ids: List[str]) -> Dict[str, Any]:
        """
        Phase 6: Compare multiple simulations to analyze different outcomes.
        
        Args:
            simulation_ids: List of simulation IDs to compare
            
        Returns:
            Comparison analysis with differences highlighted
        """
        simulations = [self.get_simulation(sid) for sid in simulation_ids if self.get_simulation(sid)]
        if len(simulations) < 2:
            return {'error': 'Need at least 2 simulations to compare', 'simulations': simulations}
        comparison = {'simulations': [s.to_dict() for s in simulations], 'comparison': {'entity_changes': {}, 'outcome_differences': []}}
        all_entities = set()
        for sim in simulations:
            if sim.result:
                all_entities.update(sim.result.affected_entities)
        for entity in all_entities:
            comparison.get('comparison', 0).get('entity_changes', 0)[entity] = [entity in (sim.result.affected_entities if sim.result else []) for sim in simulations]
        outcomes = [sim.result.success if sim.result else False for sim in simulations]
        if len(set(outcomes)) > 1:
            comparison.get('comparison', 0).get('outcome_differences', 0).append({'type': 'success_mismatch', 'values': outcomes, 'description': 'Simulations had different success outcomes'})
        return comparison

    @contextmanager
    def fork(self):
        """
        Create a fork (savepoint) for isolated execution.
        
        Usage:
            with fork_engine.fork() as fork_context:
                # Execute commands here
                # They will be rolled back when context exits
        
        Yields:
            ForkContext for tracking changes
        """
        savepoint_name = f'fork_{self._savepoint_counter}'
        self._savepoint_counter += 1
        context = ForkContext(self.db_connection, savepoint_name)
        try:
            self.db_connection.execute(f'SAVEPOINT {savepoint_name}')
            yield context
        finally:
            self.db_connection.execute(f'ROLLBACK TO SAVEPOINT {savepoint_name}')
            self.db_connection.execute(f'RELEASE SAVEPOINT {savepoint_name}')

    def capture_state(self, entity_type: str, entity_id: int) -> Optional[Dict[str, Any]]:
        """
        Capture the current state of an entity.
        
        Args:
            entity_type: Type of entity (e.g., 'job', 'invoice')
            entity_id: ID of the entity
            
        Returns:
            Dictionary of entity state or None if not found
        """
        table_mapping = {'job': 'jobs', 'invoice': 'invoices', 'payment': 'invoice_payments', 'customer': 'customers', 'quote': 'quotes', 'message': 'messages'}
        table = table_mapping.get(entity_type)
        if not table:
            return None
        cursor = self.db_connection.cursor()
        cursor.execute(f'SELECT * FROM {table} WHERE id = ?', (entity_id,))
        row = cursor.fetchone()
        if not row:
            return None
        columns = [((((((((((((((desc[0] if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None for desc in cursor.description]
        return dict(zip(columns, row))

    def calculate_diff(self, entity_type: str, entity_id: int, before: Dict[str, Any], after: Dict[str, Any]) -> StateDiff:
        """
        Calculate the diff between before and after states.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of the entity
            before: State before execution
            after: State after execution
            
        Returns:
            StateDiff object with changes
        """
        changes = {}
        all_keys = set(before.keys()) | set(after.keys())
        for key in all_keys:
            before_val = before.get(key)
            after_val = after.get(key)
            if before_val != after_val:
                changes[key] = (before_val, after_val)
        return StateDiff(entity_type=entity_type, entity_id=entity_id, before=before, after=after, changes=changes)

class ForkContext:
    """
    Context for tracking changes within a fork.
    
    Tracks:
    - Entities modified during execution
    - State snapshots before modifications
    - New entities created
    """

    def __init__(self, db_connection: sqlite3.Connection, savepoint_name: str):
        self.db_connection = db_connection
        self.savepoint_name = savepoint_name
        self.snapshots: Dict[tuple, StateSnapshot] = {}
        self.new_entity_ids: List[tuple] = []
        self.fork_engine = ForkEngine(db_connection)

    def track_entity(self, entity_type: str, entity_id: int):
        """
        Track an entity that will be modified.
        
        Captures the entity's state before modification for diff generation.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of the entity
        """
        key = (entity_type, entity_id)
        if key in self.snapshots:
            return
        state = self.fork_engine.capture_state(entity_type, entity_id)
        if state:
            self.snapshots[key] = StateSnapshot(entity_type=entity_type, entity_id=entity_id, before_state=state)

    def track_new_entity(self, entity_type: str, entity_id: int):
        """
        Track a newly created entity.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of the new entity
        """
        self.new_entity_ids.append((entity_type, entity_id))

    def get_diffs(self) -> List[StateDiff]:
        """
        Generate diffs for all tracked entities.
        
        Returns:
            List of StateDiff objects showing changes
        """
        diffs = []
        for (entity_type, entity_id), snapshot in self.snapshots.items():
            current_state = self.fork_engine.capture_state(entity_type, entity_id)
            if current_state:
                diff = self.fork_engine.calculate_diff(entity_type, entity_id, snapshot.before_state, current_state)
                if diff.changes:
                    diffs.append(diff)
        return diffs

    def get_new_entities(self) -> List[Dict[str, Any]]:
        """
        Get information about newly created entities.
        
        Returns:
            List of entity information
        """
        new_entities = []
        for entity_type, entity_id in self.new_entity_ids:
            state = self.fork_engine.capture_state(entity_type, entity_id)
            if state:
                new_entities.append({'entity_type': entity_type, 'entity_id': entity_id, 'state': state})
        return new_entities

    def get_affected_entities(self) -> List[str]:
        """
        Get list of affected entity identifiers.
        
        Returns:
            List of entity identifiers like ["job_123", "invoice_456"]
        """
        affected = []
        for entity_type, entity_id in self.snapshots.keys():
            affected.append(f'{entity_type}_{entity_id}')
        for entity_type, entity_id in self.new_entity_ids:
            affected.append(f'{entity_type}_{entity_id}_NEW')
        return affected