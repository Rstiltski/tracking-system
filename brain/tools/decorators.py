"""
Self-Registering Decorator for Tools
=====================================

This decorator allows tools to automatically register themselves without
manually editing brain.py. This is the foundation of the AI-Native architecture.

Usage:
    @register_tool(name="CreateJob", risk="Medium")
    class CreateJobTool(Tool):
        ...

The decorator stores metadata that will be used by the auto-discovery system.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from typing import Optional, Dict, Type, Literal
from brain.core.tool import Tool

# Global registry of decorated tools - populated at import time
_DECORATED_TOOLS: Dict[str, Dict] = {}


def register_tool(
    name: Optional[str] = None,
    risk: Literal["Low", "Medium", "High"] = "Medium",
    category: Optional[str] = None,
    description: Optional[str] = None
):
    """
    Decorator to mark a tool for automatic registration.
    
    Args:
        name: Tool name (defaults to class name without 'Tool' suffix)
        risk: Risk level for the tool (Low, Medium, High)
        category: Optional category for grouping (e.g., "job", "customer", "financial")
        description: Optional description (overrides class docstring)
    
    Example:
        @register_tool(name="CreateJob", risk="Medium", category="job")
        class CreateJobTool(Tool):
            '''Create a new job record'''
            ...
    """
    def decorator(cls: Type[Tool]):
        # Determine tool name
        tool_name = name if name else cls.__name__.replace("Tool", "")
        
        # Store metadata for auto-discovery
        _DECORATED_TOOLS[tool_name] = {
            "class": cls,
            "name": tool_name,
            "risk": risk,
            "category": category,
            "description": description or cls.__doc__,
            "module": cls.__module__,
            "class_name": cls.__name__
        }
        
        return cls
    
    return decorator


def get_decorated_tools() -> Dict[str, Dict]:
    """
    Get all tools that have been decorated with @register_tool.
    
    Returns:
        Dictionary mapping tool names to their metadata
    """
    return _DECORATED_TOOLS.copy()


def clear_decorated_tools():
    """Clear the decorated tools registry (mainly for testing)"""
    _DECORATED_TOOLS.clear()
