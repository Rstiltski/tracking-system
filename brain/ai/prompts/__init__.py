"""
Brain AI Prompts - Prompt Engineering Module

This module provides prompt templates and builders for the Veryfyn AI Assistant.

Modules:
    system_prompts: System prompt builders for different contexts
    templates: Pre-defined prompt templates for specific tasks

Usage:
    from brain.ai.prompts import SystemPromptBuilder, PromptTemplate
    from brain.ai.prompts import HABIT_INSIGHT_TEMPLATE, GOAL_PROGRESS_TEMPLATE
    
    # Build a system prompt
    system_prompt = SystemPromptBuilder.build(context="User data here")
    
    # Use a template
    prompt = HABIT_INSIGHT_TEMPLATE.format(
        habit_name="Exercise",
        completion_rate=85,
        streak=7
    )
"""

from brain.ai.prompts.system_prompts import SystemPromptBuilder
from brain.ai.prompts.templates import (
    PromptTemplate,
    HABIT_INSIGHT_TEMPLATE,
    GOAL_PROGRESS_TEMPLATE,
    WEEKLY_SUMMARY_TEMPLATE,
    CORRELATION_TEMPLATE,
    INTERVENTION_TEMPLATE,
    DAILY_INSIGHT_TEMPLATE,
    BEHAVIORAL_PATTERN_TEMPLATE,
)

__all__ = [
    # Classes
    "SystemPromptBuilder",
    "PromptTemplate",
    # Templates
    "HABIT_INSIGHT_TEMPLATE",
    "GOAL_PROGRESS_TEMPLATE",
    "WEEKLY_SUMMARY_TEMPLATE",
    "CORRELATION_TEMPLATE",
    "INTERVENTION_TEMPLATE",
    "DAILY_INSIGHT_TEMPLATE",
    "BEHAVIORAL_PATTERN_TEMPLATE",
]
