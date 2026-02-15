"""
Base state machine implementation for Brain architecture.

Enforces:
- Valid state transitions
- Preconditions before transitions
- Side effects after transitions
- State invariants
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/01_state_machines.md
- LLM_AGENT_QUICKSTART.md
"""

from dataclasses import dataclass
from typing import Dict, List, Callable, Optional, Any, Tuple
from enum import Enum


class TransitionResult(Enum):
    """Result of a state transition attempt."""
    SUCCESS = "success"
    INVALID_TRANSITION = "invalid_transition"
    PRECONDITION_FAILED = "precondition_failed"
    SIDE_EFFECT_FAILED = "side_effect_failed"


@dataclass
class StateTransition:
    """Defines a state transition with preconditions and side effects."""
    from_state: str
    to_state: str
    command: str
    preconditions: List[Callable] = None  # Functions that must return True
    side_effects: List[Callable] = None   # Functions to execute after transition
    
    def __post_init__(self):
        if self.preconditions is None:
            self.preconditions = []
        if self.side_effects is None:
            self.side_effects = []


@dataclass
class TransitionAttempt:
    """Result of a state transition attempt."""
    success: bool
    result: TransitionResult
    from_state: str
    to_state: str
    error_message: Optional[str] = None
    failed_precondition: Optional[str] = None
    failed_side_effect: Optional[str] = None


class StateMachine:
    """
    Base class for state machines.
    
    Subclasses should:
    1. Define all valid states
    2. Define transitions via add_transition()
    3. Implement precondition and side effect methods
    """
    
    def __init__(self):
        self.transitions: Dict[tuple, StateTransition] = {}
        self.states: set = set()
        self.terminal_states: set = set()
        
    def add_state(self, state: str, terminal: bool = False):
        """Register a valid state."""
        self.states.add(state)
        if terminal:
            self.terminal_states.add(state)
    
    def add_transition(
        self,
        from_state: str,
        to_state: str,
        command: str,
        preconditions: List[Callable] = None,
        side_effects: List[Callable] = None
    ):
        """
        Register a valid transition.
        
        Args:
            from_state: Starting state
            to_state: Destination state
            command: Command that triggers this transition
            preconditions: List of functions that must return True
            side_effects: List of functions to execute after transition
        """
        key = (from_state, to_state, command)
        self.transitions[key] = StateTransition(
            from_state=from_state,
            to_state=to_state,
            command=command,
            preconditions=preconditions or [],
            side_effects=side_effects or []
        )
    
    def can_transition(
        self,
        from_state: str,
        to_state: str,
        command: str
    ) -> bool:
        """Check if a transition is valid (exists in transition table)."""
        key = (from_state, to_state, command)
        return key in self.transitions
    
    def check_preconditions(
        self,
        transition: StateTransition,
        entity: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check all preconditions for a transition.
        
        Args:
            transition: The transition to check
            entity: The entity being transitioned (job, invoice, etc.)
            context: Additional context (user_id, company_id, etc.)
            
        Returns:
            (success, error_message)
        """
        for precondition in transition.preconditions:
            try:
                result = precondition(entity, context)
                if not result:
                    return False, f"Precondition failed: {precondition.__name__}"
            except Exception as e:
                return False, f"Precondition error in {precondition.__name__}: {str(e)}"
        
        return True, None
    
    def execute_side_effects(
        self,
        transition: StateTransition,
        entity: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute all side effects for a transition.
        
        Args:
            transition: The transition being executed
            entity: The entity being transitioned
            context: Additional context
            
        Returns:
            (success, error_message)
        """
        for side_effect in transition.side_effects:
            try:
                side_effect(entity, context)
            except Exception as e:
                return False, f"Side effect error in {side_effect.__name__}: {str(e)}"
        
        return True, None
    
    def transition(
        self,
        from_state: str,
        to_state: str,
        command: str,
        entity: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> TransitionAttempt:
        """
        Attempt a state transition.
        
        Args:
            from_state: Current state
            to_state: Desired state
            command: Command triggering the transition
            entity: The entity to transition
            context: Additional context (optional)
            
        Returns:
            TransitionAttempt with success status and details
        """
        if context is None:
            context = {}
        
        # Check if transition is valid
        if not self.can_transition(from_state, to_state, command):
            return TransitionAttempt(
                success=False,
                result=TransitionResult.INVALID_TRANSITION,
                from_state=from_state,
                to_state=to_state,
                error_message=f"Invalid transition from {from_state} to {to_state} via {command}"
            )
        
        # Get the transition
        key = (from_state, to_state, command)
        transition = self.transitions[key]
        
        # Check preconditions
        preconditions_ok, precondition_error = self.check_preconditions(
            transition, entity, context
        )
        if not preconditions_ok:
            return TransitionAttempt(
                success=False,
                result=TransitionResult.PRECONDITION_FAILED,
                from_state=from_state,
                to_state=to_state,
                error_message=precondition_error,
                failed_precondition=precondition_error
            )
        
        # Execute side effects
        side_effects_ok, side_effect_error = self.execute_side_effects(
            transition, entity, context
        )
        if not side_effects_ok:
            return TransitionAttempt(
                success=False,
                result=TransitionResult.SIDE_EFFECT_FAILED,
                from_state=from_state,
                to_state=to_state,
                error_message=side_effect_error,
                failed_side_effect=side_effect_error
            )
        
        # Success!
        return TransitionAttempt(
            success=True,
            result=TransitionResult.SUCCESS,
            from_state=from_state,
            to_state=to_state
        )
    
    def get_valid_transitions(self, from_state: str) -> List[tuple]:
        """Get all valid transitions from a given state."""
        return [
            (t.to_state, t.command)
            for key, t in self.transitions.items()
            if t.from_state == from_state
        ]
    
    def validate_state(self, state: str) -> bool:
        """Check if a state is valid."""
        return state in self.states
    
    def is_terminal(self, state: str) -> bool:
        """Check if a state is terminal (no further transitions)."""
        return state in self.terminal_states
