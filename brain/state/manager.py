"""
State machine manager for Brain architecture.

Manages state machine lifecycle and provides validation for state transitions.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/01_state_machines.md
- LLM_AGENT_QUICKSTART.md
"""
import logging
from typing import Dict, Optional, Any
from brain.state.machine import StateMachine, TransitionAttempt, TransitionResult
from brain.state.job_machine import JobStateMachine
from brain.state.invoice_machine import InvoiceStateMachine
from brain.state.payment_machine import PaymentStateMachine
from brain.state.quote_machine import QuoteStateMachine
import db

class StateMachineManager:
    """
    Manages all state machines in the Brain.
    
    Provides:
    - State machine registration
    - State transition validation
    - Current state retrieval
    - State transition execution
    """

    def __init__(self):
        self.machines: Dict[str, StateMachine] = {}
        self._register_machines()

    def _register_machines(self):
        """Register all state machines."""
        self.machines['job'] = JobStateMachine()
        self.machines['invoice'] = InvoiceStateMachine()
        self.machines['quote'] = QuoteStateMachine()
        self.machines['payment'] = PaymentStateMachine()

    def get_machine(self, entity_type: str) -> Optional[StateMachine]:
        """Get state machine for an entity type."""
        return self.machines.get(entity_type)

    def get_current_state(self, entity_type: str, entity_id: int) -> Optional[str]:
        """
        Get current state of an entity.
        
        Args:
            entity_type: Type of entity (job, invoice)
            entity_id: ID of entity
            
        Returns:
            Current state (normalized to uppercase) or None if not found
        """
        try:
            if entity_type == 'job':
                job = db.get_job(entity_id)
                return (job.get('status', '') if job else '').upper() if job and job.get('status') else None
            elif entity_type == 'invoice':
                invoice = db.get_invoice(entity_id)
                return invoice.get('status', 0).upper() if invoice and invoice.get('status') else None
            elif entity_type == 'quote':
                quote = db.get_quote_with_items(entity_id)
                return quote.get('status', 0).upper() if quote and quote.get('status') else None
            elif entity_type == 'payment':
                try:
                    with db.get_conn() as conn:
                        row = conn.execute('SELECT status FROM invoice_payments WHERE id = ?', (entity_id,)).fetchone()
                        return row.get('status', 0).upper() if row and row.get('status') else None
                except Exception as e:
                    logging.error(f'Error fetching payment {entity_id} status: {e}')
                    return None
            return None
        except Exception:
            return None

    def validate_transition(self, entity_type: str, entity_id: int, command: str, new_state: str, context: Dict[str, Any]=None) -> TransitionAttempt:
        """
        Validate a state transition without executing it.
        
        Args:
            entity_type: Type of entity (job, invoice, payment)
            entity_id: ID of entity
            command: Command triggering the transition
            new_state: Desired new state
            context: Additional context for validation
            
        Returns:
            TransitionAttempt with validation result
        """
        machine = self.get_machine(entity_type)
        if not machine:
            return TransitionAttempt(success=False, result=TransitionResult.INVALID_TRANSITION, from_state='', to_state=new_state, error_message=f'No state machine for entity type: {entity_type}')
        entity = None
        current_state = None
        if entity_type == 'job':
            entity = db.get_job(entity_id)
            current_state = entity.get('status', 0).upper() if entity and entity.get('status') else None
        elif entity_type == 'invoice':
            entity = db.get_invoice(entity_id)
            current_state = entity.get('status', 0).upper() if entity and entity.get('status') else None
        elif entity_type == 'quote':
            entity = db.get_quote_with_items(entity_id)
            current_state = entity.get('status', 0).upper() if entity and entity.get('status') else None
        if not entity or not current_state:
            return TransitionAttempt(success=False, result=TransitionResult.INVALID_TRANSITION, from_state='', to_state=new_state, error_message=f'Entity not found: {entity_type} #{entity_id}')
        if not machine.can_transition(current_state, new_state, command):
            return TransitionAttempt(success=False, result=TransitionResult.INVALID_TRANSITION, from_state=current_state, to_state=new_state, error_message=f'Invalid transition from {current_state} to {new_state} via {command}')
        return TransitionAttempt(success=True, result=TransitionResult.SUCCESS, from_state=current_state, to_state=new_state)

    def execute_transition(self, entity_type: str, entity_id: int, command: str, new_state: str, context: Dict[str, Any]=None) -> TransitionAttempt:
        """
        Execute a state transition.
        
        Args:
            entity_type: Type of entity (job, invoice, payment)
            entity_id: ID of entity
            command: Command triggering the transition
            new_state: Desired new state
            context: Additional context for execution
            
        Returns:
            TransitionAttempt with execution result
        """
        machine = self.get_machine(entity_type)
        if not machine:
            return TransitionAttempt(success=False, result=TransitionResult.INVALID_TRANSITION, from_state='', to_state=new_state, error_message=f'No state machine for entity type: {entity_type}')
        current_state = self.get_current_state(entity_type, entity_id)
        if not current_state:
            return TransitionAttempt(success=False, result=TransitionResult.INVALID_TRANSITION, from_state='', to_state=new_state, error_message=f'Entity not found: {entity_type} #{entity_id}')
        full_context = context or {}
        full_context['entity_id'] = entity_id
        full_context['entity_type'] = entity_type
        return machine.transition(current_state, new_state, command, full_context)

    def is_terminal_state(self, entity_type: str, state: str) -> bool:
        """Check if a state is terminal."""
        machine = self.get_machine(entity_type)
        if not machine:
            return False
        return state in machine.terminal_states