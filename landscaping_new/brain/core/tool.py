"""
Base Tool Class

Defines the base class for all AI tools in the brain system.
Following the architecture rules, all tools must inherit from this class
and implement proper risk tier classification.
"""
from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

from brain.core.enums import RiskTier
from brain.core.result import ToolOutput

# Initialize logger
logger = logging.getLogger(__name__)

class Tool(ABC):
    """
    Base class for all tools in the brain system.
    
    All tools must inherit from this class and implement:
    1. input_schema property - defines expected input parameters
    2. execute method - implements the tool's functionality
    3. Proper risk tier classification
    """
    
    def __init__(self, name: str, description: str, risk_tier: RiskTier):
        self.name = name
        self.description = description
        self.risk_tier = risk_tier
        
        # Validate risk tier
        if not isinstance(risk_tier, RiskTier):
            raise ValueError(f"risk_tier must be a RiskTier enum value, got {type(risk_tier)}")
    
    @property
    @abstractmethod
    def input_schema(self) -> type[BaseModel]:
        """
        Define the Pydantic schema for input validation.
        
        Returns:
            A Pydantic BaseModel subclass defining expected input parameters
        """
        pass
    
    def execute(self, input_data) -> ToolOutput:
        """
        Execute the tool with the provided input data.
        This is the default implementation that validates input and calls _execute.
        
        Args:
            input_data: Input data (either BaseModel instance or dict to be validated)
            
        Returns:
            ToolOutput containing the result of the operation
        """
        # If input_data is a dict, validate it against the schema
        if isinstance(input_data, dict):
            validated_data = self.validate_input(input_data)
            return self._execute(validated_data)
        else:
            # Assume it's already a validated BaseModel
            return self._execute(input_data)
    
    @abstractmethod
    def _execute(self, input_data: BaseModel) -> ToolOutput:
        """
        Execute the tool with the provided validated input data.
        
        Args:
            input_data: Input data validated against input_schema
            
        Returns:
            ToolOutput containing the result of the operation
        """
        pass
    
    def validate_input(self, raw_input: Dict[str, Any]) -> BaseModel:
        """
        Validate raw input against the tool's schema.
        
        Args:
            raw_input: Dictionary of input parameters
            
        Returns:
            Validated BaseModel instance
            
        Raises:
            ValidationError: If input doesn't match schema
        """
        schema = self.input_schema
        return schema(**raw_input)
    
    def __repr__(self) -> str:
        return f"<Tool: {self.name} (Risk: {self.risk_tier.name})>"
    
    def __str__(self) -> str:
        return f"Tool({self.name}): {self.description}"

class SimpleTool(Tool):
    """
    A simpler base class for tools that don't need complex input validation.
    Useful for basic operations that take simple parameters.
    """
    
    def __init__(self, name: str, description: str, risk_tier: RiskTier):
        super().__init__(name, description, risk_tier)
    
    @property
    def input_schema(self) -> type[BaseModel]:
        """Default schema that accepts any parameters."""
        class DefaultInput(BaseModel):
            model_config = {"extra": "allow"}  # Allow extra fields

        return DefaultInput
    
    @abstractmethod
    def execute_simple(self, **kwargs) -> ToolOutput:
        """
        Execute the tool with simple keyword arguments.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolOutput containing the result of the operation
        """
        pass
    
    def _execute(self, input_data: BaseModel) -> ToolOutput:
        """
        Execute the tool by converting BaseModel to kwargs and calling execute_simple.
        """
        # Convert BaseModel to dict and call execute_simple
        return self.execute_simple(**input_data.model_dump())

# Example implementation of a basic tool
class HealthCheckTool(SimpleTool):
    """
    Example tool that performs a basic health check.
    Demonstrates proper tool implementation following architecture rules.
    """
    
    def __init__(self):
        super().__init__(
            name="health_check",
            description="Perform a basic system health check",
            risk_tier=RiskTier.LOW
        )
    
    def execute_simple(self, **kwargs) -> ToolOutput:
        """Execute the health check."""
        try:
            # Perform health check logic
            health_status = {
                "status": "healthy",
                "timestamp": kwargs.get("timestamp"),
                "checks_passed": ["database", "memory", "disk_space"]
            }

            return ToolOutput(
                success=True,
                data=health_status,
                metadata={"message": "Health check completed successfully"}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="HEALTH_CHECK_FAILED",
                error_message=f"Health check failed: {str(e)}"
            )