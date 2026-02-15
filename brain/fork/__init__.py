"""
Fork Engine - Transaction isolation for dry-run execution.

This module provides the ability to fork database state for testing commands
without committing changes. Used for confirmation previews.

Phase 6 (Dream State):
- Multiple simulation tracking
- What-if scenario comparison
- Simulation branching support
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from brain.fork.engine import ForkEngine, Simulation, DryRunResult, StateDiff

__all__ = ['ForkEngine', 'Simulation', 'DryRunResult', 'StateDiff']
