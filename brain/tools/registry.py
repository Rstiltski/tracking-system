"""
Tool Registry - Central registry of all tools with lazy loading support
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import os
import importlib
import logging
from pathlib import Path
from typing import Optional, Dict, Callable
from brain.core.tool import Tool
from brain.core.result import ToolOutput
logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    Central registry of all tools with lazy loading support.

    Tools can be registered eagerly (at startup) or lazily (on first use).
    Lazy loading improves startup time by deferring imports until needed.
    
    Usage:
        # Eager registration (traditional)
        registry.register(CreateJobTool())
        
        # Lazy registration (optimized)
        registry.register_lazy(
            "CreateJob",
            "brain.tools.job_tools",
            "CreateJobTool"
        )
        
        # Auto-discovery (AI-Native)
        registry.auto_discover_tools()
    """

    def __init__(self, lazy_loading: bool=False, auto_discover: bool=False):
        """
        Initialize the tool registry.
        
        Args:
            lazy_loading: If True, defer tool imports until first use.
                         If False, tools must be registered eagerly (default for backward compatibility)
            auto_discover: If True, automatically discover and register decorated tools
        """
        self.tools: Dict[str, Tool] = {}
        self.lazy_loaders: Dict[str, Dict[str, str]] = {}
        self.lazy_loading = lazy_loading
        self.auto_discover = auto_discover
        if auto_discover:
            self.auto_discover_tools()

    def register(self, tool: Tool) -> None:
        """Register a tool (eager loading)"""
        self.tools[tool.name] = tool

    def register_lazy(self, tool_name: str, module_path: str, class_name: str) -> None:
        """
        Register a tool for lazy loading.
        
        The tool class will only be imported and instantiated when first accessed.
        
        Args:
            tool_name: Name of the tool (e.g., "CreateJob")
            module_path: Python module path (e.g., "brain.tools.job_tools")
            class_name: Class name in the module (e.g., "CreateJobTool")
        """
        if not self.lazy_loading:
            self._load_tool(tool_name, module_path, class_name)
        else:
            self.lazy_loaders[tool_name] = {'module': module_path, 'class': class_name}

    def _load_tool(self, tool_name: str, module_path: str, class_name: str) -> None:
        """Load a tool from its module (internal use)"""
        import importlib
        try:
            module = importlib.import_module(module_path)
            tool_class = getattr(module, class_name)
            tool_instance = tool_class()
            self.tools[tool_name] = tool_instance
        except (ImportError, AttributeError) as e:
            raise RuntimeError(f'Failed to load tool {tool_name} from {module_path}.{class_name}: {e}')

    def get(self, name: str) -> Optional[Tool]:
        """
        Get tool by name.
        
        If tool is registered for lazy loading and not yet loaded, it will be loaded now.
        """
        if name in self.tools:
            return self.tools[name]
        if name in self.lazy_loaders:
            loader_info = self.lazy_loaders[name]
            self._load_tool(name, loader_info.get('module', 0), loader_info.get('class', 0))
            return self.tools.get(name)
        return None

    def has(self, name: str) -> bool:
        """Check if tool exists (either loaded or registered for lazy loading)"""
        return name in self.tools or name in self.lazy_loaders

    def execute(self, name: str, params: dict) -> ToolOutput:
        """Execute tool by name"""
        tool = self.get(name)
        if not tool:
            return ToolOutput(success=False, error_code='TOOL_NOT_FOUND', error_message=f"Tool '{name}' not found in registry")
        return tool.run(params)

    def list_tools(self) -> list[str]:
        """List all registered tool names (both loaded and lazy)"""
        return list(set(self.tools.keys()) | set(self.lazy_loaders.keys()))

    def __len__(self) -> int:
        """Number of registered tools (both loaded and lazy)"""
        return len(set(self.tools.keys()) | set(self.lazy_loaders.keys()))

    def __contains__(self, name: str) -> bool:
        """Check if tool is registered"""
        return self.has(name)

    def auto_discover_tools(self) -> int:
        """
        Automatically discover and register all tools decorated with @register_tool.
        
        Scans all Python files in the brain/tools/ directory and imports them to
        trigger decorator registration. Returns the number of tools discovered.
        
        Returns:
            Number of tools discovered and registered
        """
        from brain.tools.decorators import get_decorated_tools
        tools_dir = Path(__file__).parent
        python_files = tools_dir.glob('*.py')
        for py_file in python_files:
            module_name = py_file.stem
            if module_name in ('__init__', 'registry', 'decorators'):
                continue
            try:
                module_path = f'brain.tools.{module_name}'
                importlib.import_module(module_path)
                logger.debug(f'Scanned module: {module_path}')
            except Exception as e:
                logger.warning(f'Failed to import {module_path} during auto-discovery: {e}')
        decorated_tools = get_decorated_tools()
        initial_count = len(self)
        for tool_name, metadata in decorated_tools.items():
            if not self.has(tool_name):
                self.register_lazy(tool_name, metadata.get('module', 0), metadata.get('class_name', 0))
                logger.debug(f'Auto-registered tool: {tool_name}')
        new_count = len(self) - initial_count
        logger.info(f'Auto-discovery complete: {new_count} new tools registered')
        return new_count