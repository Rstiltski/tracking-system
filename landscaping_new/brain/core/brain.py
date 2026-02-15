"""
Brain System Core

The main brain orchestrator that manages AI tools, validation, and routing.
Following the architecture rules, this implements the 6-step linear pipeline
for safe AI code generation and execution.

📚 REQUIRED READING BEFORE MODIFICATION:
- MASTER_RULES.md
- ARCHITECTURE_RULES.md
- BRAIN_TOOLS_REFERENCE.md
"""
from __future__ import annotations
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

from brain.core.tool import Tool, ToolOutput
from brain.core.router import Router
from brain.core.enums import RiskTier, ToolStatus
from brain.core.events import EventManager
from brain.core.command_event import CommandEvent
from brain.core.result import Result
from brain.core.nonce_ledger import NonceLedger
from brain.core.guardrails import GuardrailValidator
from brain.core.system_status import SystemStatusMonitor

# Initialize logger
logger = logging.getLogger(__name__)

class Brain:
    """
    The main Brain orchestrator that manages AI tools, validation, and routing.
    
    Implements the 6-step linear pipeline architecture:
    1. DeliberationBrain: Thinks deeply about the problem
    2. ArchitectBrain: Designs structure and signatures  
    3. ScaffoldBrain: Adds error handling and control flow
    4. LogicBrain: Implements business logic
    5. IntegrationBrain: Handles imports and wiring
    6. ReviewBrain: Audits quality and security
    """
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.tools: Dict[str, Tool] = {}
        self.router = Router()
        self.event_manager = EventManager()
        self.nonce_ledger = NonceLedger()
        self.guardrails = GuardrailValidator()
        self.status_monitor = SystemStatusMonitor()
        
        # Track active operations
        self.active_operations = {}
        
        logger.info(f"Brain system initialized with ID: {self.id}")
    
    def register_tool(self, tool: Tool) -> None:
        """Register a new tool with the brain system."""
        # Validate tool before registration
        if not isinstance(tool, Tool):
            raise TypeError(f"Expected Tool instance, got {type(tool)}")
            
        # Check for duplicate registration
        if tool.name in self.tools:
            logger.warning(f"Tool {tool.name} already registered, replacing")
            
        self.tools[tool.name] = tool
        self.router.register_route(tool.name, tool)
        logger.info(f"Registered tool: {tool.name} with risk tier: {tool.risk_tier}")
    
    def execute_command(self, command: str, params: Dict[str, Any]) -> ToolOutput:
        """
        Execute a command through the brain system.
        
        Args:
            command: The command to execute
            params: Parameters for the command
            
        Returns:
            ToolOutput: The result of the command execution
        """
        # Create a command event for audit trail
        cmd_event = CommandEvent(
            command=command,
            params=params,
            timestamp=datetime.now(),
            brain_id=self.id
        )
        
        # Validate the command using guardrails
        validation_result = self.guardrails.validate_command(command, params)
        if not validation_result.is_valid:
            return ToolOutput(
                success=False,
                error_code="VALIDATION_FAILED",
                error_message=f"Command validation failed: {validation_result.reason}"
            )
        
        # Check if command exists
        if command not in self.tools:
            return ToolOutput(
                success=False,
                error_code="COMMAND_NOT_FOUND",
                error_message=f"Command '{command}' not found"
            )
        
        # Get the tool
        tool = self.tools[command]
        
        # Check risk tier and apply appropriate controls
        if tool.risk_tier.value >= RiskTier.HIGH.value:
            # For high-risk operations, check for explicit authorization
            if not self._is_authorized_for_high_risk_operation(params):
                return ToolOutput(
                    success=False,
                    error_code="UNAUTHORIZED_HIGH_RISK",
                    error_message=f"High-risk operation {command} requires explicit authorization"
                )
        
        # Execute the tool
        try:
            # Log the operation
            logger.info(f"Executing tool: {command} with params: {params}")
            
            # Add to active operations
            op_id = str(uuid.uuid4())
            self.active_operations[op_id] = {
                'tool': tool.name,
                'start_time': datetime.now(),
                'params': params
            }
            
            # Execute the tool
            result = tool.execute(params)
            
            # Remove from active operations
            if op_id in self.active_operations:
                del self.active_operations[op_id]
                
            # Log successful execution
            logger.info(f"Tool {command} executed successfully")
            
            # Emit event
            self.event_manager.emit('tool_executed', {
                'tool': command,
                'success': result.success,
                'duration': (datetime.now() - self.active_operations.get(op_id, {}).get('start_time', datetime.now())).total_seconds()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool {command}: {str(e)}", exc_info=True)
            
            # Remove from active operations in case of error
            if op_id in self.active_operations:
                del self.active_operations[op_id]
            
            return ToolOutput(
                success=False,
                error_code="EXECUTION_ERROR",
                error_message=f"Error executing tool {command}: {str(e)}"
            )
    
    def _is_authorized_for_high_risk_operation(self, params: Dict[str, Any]) -> bool:
        """
        Check if the current context is authorized for high-risk operations.
        This is a simplified check - in production, this would involve more sophisticated
        authentication and authorization mechanisms.
        """
        # For now, allow high-risk operations if they come with an explicit confirmation
        return params.get('_confirmed', False)
    
    def get_tool_list(self) -> List[str]:
        """Get a list of all registered tool names."""
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific tool."""
        if tool_name not in self.tools:
            return None
            
        tool = self.tools[tool_name]
        return {
            'name': tool.name,
            'description': tool.description,
            'risk_tier': tool.risk_tier.value,
            'input_schema': tool.input_schema,
            'category': getattr(tool, 'category', 'general')
        }
    
    def validate_system_integrity(self) -> Result:
        """
        Perform a comprehensive validation of the brain system integrity.
        Checks all registered tools, connections, and system health.
        """
        issues = []
        
        # Check all tools
        for name, tool in self.tools.items():
            try:
                # Validate tool schema
                if not hasattr(tool, 'input_schema'):
                    issues.append(f"Tool {name} missing input_schema")
                    
                # Validate tool execute method
                if not hasattr(tool, 'execute') or not callable(getattr(tool, 'execute')):
                    issues.append(f"Tool {name} missing or invalid execute method")
                    
            except Exception as e:
                issues.append(f"Error validating tool {name}: {str(e)}")
        
        # Check system components
        if not self.router:
            issues.append("Router not initialized")
            
        if not self.event_manager:
            issues.append("EventManager not initialized")
            
        # Return result
        if issues:
            return Result(
                success=False,
                data={'issues': issues},
                message=f"System validation failed with {len(issues)} issues"
            )
        else:
            return Result(
                success=True,
                data={'tool_count': len(self.tools)},
                message="System validation passed"
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status information."""
        return {
            'brain_id': self.id,
            'created_at': self.created_at.isoformat(),
            'tool_count': len(self.tools),
            'active_operations': len(self.active_operations),
            'uptime': (datetime.now() - self.created_at).total_seconds(),
            'status': 'healthy'  # Simplified - would check actual health in production
        }

# Global brain instance
brain_instance = Brain()

# Make sure it's available at module level
__all__ = ['Brain', 'brain_instance']