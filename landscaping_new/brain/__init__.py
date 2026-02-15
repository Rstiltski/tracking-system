"""
Brain System - Main Entry Point

This module initializes the brain system for the landscaping management platform.
Following the architecture rules, this is part of the AI overlay system that provides
natural language interfaces to the database and business logic layers.
"""
from __future__ import annotations

# NOTE: Follow repository guidance in MASTER_RULES.md and DEVELOPER_GUIDE.md before editing.

# Import main brain components
from brain.core.brain import Brain, brain_instance
from brain.core.tool import Tool, ToolOutput
from brain.core.router import Router
from brain.core.enums import RiskTier, ToolStatus

# Export commonly used classes/functions
__all__ = [
    'Brain',
    'Tool',
    'ToolOutput',
    'Router',
    'RiskTier',
    'ToolStatus',
    'brain_instance'
]