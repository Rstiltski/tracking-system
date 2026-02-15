"""
State machine module for Brain architecture.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/01_state_machines.md
- LLM_AGENT_QUICKSTART.md
"""

from brain.state.machine import StateMachine, StateTransition
from brain.state.job_machine import JobStateMachine
from brain.state.invoice_machine import InvoiceStateMachine
from brain.state.payment_machine import PaymentStateMachine

__all__ = [
    'StateMachine',
    'StateTransition',
    'JobStateMachine',
    'InvoiceStateMachine',
    'PaymentStateMachine',
]
