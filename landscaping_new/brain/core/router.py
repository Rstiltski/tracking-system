"""
Router for Brain System

Handles routing of commands to appropriate tools based on command names and parameters.
Following the architecture rules, this provides a single point of routing for all brain operations.
"""
from __future__ import annotations
import logging
import re
from typing import Dict, Any, Callable, Optional, List
from brain.core.tool import Tool
from brain.core.result import ToolOutput

# Initialize logger
logger = logging.getLogger(__name__)

class Router:
    """
    Central router for directing commands to appropriate tools.
    
    Following the architecture rules, this serves as the single point of routing
    for all brain system operations, ensuring consistent command handling and validation.
    """
    
    def __init__(self):
        self.routes: Dict[str, Tool] = {}
        self.pattern_routes: List[Dict[str, Any]] = []  # For regex-based routing
        self.middleware: List[Callable] = []
        
        logger.info("Router initialized")
    
    def register_route(self, command_name: str, tool: Tool) -> None:
        """
        Register a route for a specific command to a tool.
        
        Args:
            command_name: The name of the command to route
            tool: The tool to handle the command
        """
        if not isinstance(tool, Tool):
            raise TypeError(f"Expected Tool instance, got {type(tool)}")
        
        # Validate command name
        if not isinstance(command_name, str) or not command_name.strip():
            raise ValueError("Command name must be a non-empty string")
        
        # Normalize command name (lowercase, alphanumeric with underscores/hyphens)
        normalized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', command_name.lower().strip())
        
        self.routes[normalized_name] = tool
        logger.info(f"Registered route: {normalized_name} -> {tool.name}")
    
    def register_pattern_route(self, pattern: str, tool: Tool) -> None:
        """
        Register a route using a regex pattern.
        
        Args:
            pattern: Regex pattern to match commands
            tool: The tool to handle matching commands
        """
        if not isinstance(tool, Tool):
            raise TypeError(f"Expected Tool instance, got {type(tool)}")
        
        compiled_pattern = re.compile(pattern)
        self.pattern_routes.append({
            'pattern': compiled_pattern,
            'tool': tool
        })
        logger.info(f"Registered pattern route: {pattern} -> {tool.name}")
    
    def add_middleware(self, middleware_func: Callable) -> None:
        """
        Add middleware function to process requests before routing.
        
        Args:
            middleware_func: Function to process requests (receives command, params)
        """
        if not callable(middleware_func):
            raise TypeError("Middleware must be callable")
        
        self.middleware.append(middleware_func)
        logger.debug(f"Added middleware: {middleware_func.__name__}")
    
    def route(self, command: str, params: Dict[str, Any]) -> ToolOutput:
        """
        Route a command to the appropriate tool.
        
        Args:
            command: The command to route
            params: Parameters for the command
            
        Returns:
            ToolOutput: Result of the tool execution
        """
        # Apply middleware
        processed_command = command
        processed_params = params.copy()
        
        for middleware in self.middleware:
            try:
                result = middleware(processed_command, processed_params)
                if result and isinstance(result, tuple) and len(result) == 2:
                    processed_command, processed_params = result
            except Exception as e:
                logger.error(f"Error in middleware {middleware.__name__}: {e}")
                return ToolOutput(
                    success=False,
                    error_code="MIDDLEWARE_ERROR",
                    error_message=f"Error in middleware: {str(e)}"
                )
        
        # Normalize command name
        normalized_command = re.sub(r'[^a-zA-Z0-9_-]', '_', processed_command.lower().strip())
        
        # First, try exact match
        if normalized_command in self.routes:
            tool = self.routes[normalized_command]
            logger.info(f"Routing command '{processed_command}' to tool '{tool.name}'")
            return tool.execute(tool.validate_input(processed_params))
        
        # Then, try pattern matching
        for route_info in self.pattern_routes:
            pattern = route_info['pattern']
            tool = route_info['tool']
            
            if pattern.match(normalized_command):
                logger.info(f"Routing command '{processed_command}' to tool '{tool.name}' via pattern match")
                return tool.execute(tool.validate_input(processed_params))
        
        # Command not found
        logger.warning(f"Command '{processed_command}' not found in routes")
        return ToolOutput(
            success=False,
            error_code="COMMAND_NOT_FOUND",
            error_message=f"Command '{processed_command}' not found"
        )
    
    def get_route_info(self) -> Dict[str, str]:
        """
        Get information about all registered routes.
        
        Returns:
            Dictionary mapping command names to tool names
        """
        return {cmd: tool.name for cmd, tool in self.routes.items()}
    
    def get_available_commands(self) -> List[str]:
        """
        Get a list of all available commands.
        
        Returns:
            List of command names
        """
        return list(self.routes.keys())
    
    def command_exists(self, command: str) -> bool:
        """
        Check if a command exists in the routing table.
        
        Args:
            command: Command name to check
            
        Returns:
            True if command exists, False otherwise
        """
        normalized_command = re.sub(r'[^a-zA-Z0-9_-]', '_', command.lower().strip())
        return normalized_command in self.routes
    
    def execute_command(self, command: str, params: Dict[str, Any]) -> ToolOutput:
        """
        Convenience method to execute a command directly through routing.
        
        Args:
            command: The command to execute
            params: Parameters for the command
            
        Returns:
            ToolOutput: Result of the command execution
        """
        return self.route(command, params)

# Global router instance
router_instance = Router()