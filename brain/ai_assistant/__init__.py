"""
AI Assistant Memory Management System

This module provides enhanced memory and reasoning infrastructure for the AI
assistant working on the Veryfyn Tracking System.

IMPORTANT: These components are used BY the AI assistant during development
sessions. They are NOT part of the runtime tracking application.

Components:
- MemoryManager: Memory compression and retrieval
- ReferenceIndex: Code block reference system
- TaskDecomposer: Hierarchical task breakdown
- SessionContext: Active session state management

Usage:
    from brain.ai_assistant import MemoryManager, ReferenceIndex, TaskDecomposer, SessionContext
    
    # Initialize all components
    memory = MemoryManager()
    index = ReferenceIndex()
    decomposer = TaskDecomposer()
    context = SessionContext()
    
    # Use in AI thinking process
    relevant = memory.get_relevant_decisions(intent="Adding new feature")
    task_tree = decomposer.decompose("Add correlation analysis")
    context.add_interaction(role="user", content="Add new feature")
"""

from brain.ai_assistant.memory_manager import (
    MemoryManager,
    DecisionEntry,
    MemorySummary,
    get_memory_manager,
    get_relevant_decisions,
    log_decision,
)

from brain.ai_assistant.reference_index import (
    ReferenceIndex,
    FileReference,
    CodeBlockReference,
    create_reference,
    load_reference,
    find_references,
)

from brain.ai_assistant.task_decomposer import (
    TaskDecomposer,
    TaskTree,
    TaskNode,
    TaskStatus,
    TaskPriority,
    decompose_request,
    get_next_task,
)

from brain.ai_assistant.session_context import (
    SessionContext,
    Interaction,
    SessionState,
    get_session_context,
    add_interaction,
    get_context,
)

__all__ = [
    # Memory Manager
    "MemoryManager",
    "DecisionEntry",
    "MemorySummary",
    "get_memory_manager",
    "get_relevant_decisions",
    "log_decision",
    
    # Reference Index
    "ReferenceIndex",
    "FileReference",
    "CodeBlockReference",
    "create_reference",
    "load_reference",
    "find_references",
    
    # Task Decomposer
    "TaskDecomposer",
    "TaskTree",
    "TaskNode",
    "TaskStatus",
    "TaskPriority",
    "decompose_request",
    "get_next_task",
    
    # Session Context
    "SessionContext",
    "Interaction",
    "SessionState",
    "get_session_context",
    "add_interaction",
    "get_context",
]

__version__ = "1.0.0"
__author__ = "AI Assistant (Rigorous Architect Protocol)"
