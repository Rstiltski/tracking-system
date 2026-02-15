"""
Core Brain components

🤖 LLM OPERATIONAL GUIDE:
========================
When working with this module, the LLM must follow these principles:

1. NON-LINEAR, HOLISTIC REASONING:
   - Assume the human user does not know how to code
   - Analyze every request: What is the user trying to achieve?
   - Consider: How does this fit into the current program?
   - Think about: Previous code, modules, or features to tie into
   - Plan for: Future extensibility and alternate uses

2. CLARIFYING QUESTIONS:
   - Always ask to build a bigger picture
   - What is the broader goal?
   - Are there related features or workflows?
   - Is there missing context or requirements?

3. CLEAR EXPLANATIONS:
   - Describe what is being changed and why
   - Offer step-by-step instructions and summaries
   - Document integration points and dependencies

4. FULL RESPONSIBILITY:
   - Make all code changes, updates, and tests
   - Ensure robust, maintainable, and extensible solutions
   - Update documentation and feature maps as needed

5. EXPANSION IDEAS:
   - Linear: Direct next steps, incremental improvements
   - Non-linear: Creative, alternative, or cross-domain uses

CRITICAL BRAIN RULES:
====================
1. NO direct database access - All operations through Tools
2. NO auto-editing scripts - Scripts detect only, never modify
3. NO placeholders - Complete implementations only
4. ALWAYS log to audit - Every command recorded
5. ALWAYS validate transitions - State machines enforced

📚 REQUIRED READING BEFORE MODIFICATION:
- PROJECT_RULES.md (root level)
- GETTING_STARTED.md (root level)
- brain/README.md
- brain/core/README.md
"""

from brain.core.command_event import CommandEvent
from brain.core.result import BrainResult, ToolOutput
from brain.core.tool import Tool, ToolInput
from brain.core.enums import Role, RiskTier, CommandStatus

__all__ = [
    "CommandEvent",
    "BrainResult",
    "ToolOutput",
    "Tool",
    "ToolInput",
    "Role",
    "RiskTier",
    "CommandStatus",
]