"""
Brain Context Module - The Thinking Layer

This module provides the context layer that connects AI assistants
to the brain system's thinking process.

Usage:
    from brain.context import ThinkingBrain, ContextLoader
    
    # Load context from README files
    context = ContextLoader.load_all()
    
    # Process a simple prompt through the brain
    brain = ThinkingBrain()
    result = brain.think("add a habit")
"""
# Import directly to avoid circular imports from brain/__init__.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain.context.thinking_brain import ThinkingBrain
from brain.context.context_loader import ContextLoader

__all__ = ['ThinkingBrain', 'ContextLoader']
