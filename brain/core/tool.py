"""
Base classes for Tools
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, Any, Optional
from brain.core.result import ToolOutput


@dataclass(kw_only=True)
class ToolInput:
    """Base class for tool inputs"""
    company_id: Optional[int] = None


class Tool(ABC):
    """
    Base class for all tools.

    Tools are atomic operations that wrap database functions.
    They provide typed inputs/outputs and error handling.
    """

    def __init__(self, name: str = None):
        # Remove "Tool" suffix from class name if present
        if name:
            self.name = name
        else:
            self.name = self.__class__.__name__.replace("Tool", "")
        self.description: str = self.__doc__ or "No description"

    @property
    @abstractmethod
    def input_schema(self) -> Type[ToolInput]:
        """Return the input schema class"""
        pass

    @abstractmethod
    def execute(self, input_data: ToolInput) -> ToolOutput:
        """Execute the tool with validated input"""
        pass

    def validate_input(self, params: dict) -> ToolInput:
        """Validate and parse input parameters"""
        try:
            input_schema = self.input_schema
            # Filter params to only include fields defined in the schema
            # This allows the Brain to inject extra context (like user_id) without breaking tools
            if hasattr(input_schema, '__dataclass_fields__'):
                schema_fields = set(input_schema.__dataclass_fields__.keys())
                filtered_params = {k: v for k, v in params.items() if k in schema_fields}
            else:
                # If not a dataclass, pass all params (fallback for custom schemas)
                filtered_params = params
            return input_schema(**filtered_params)
        except TypeError as e:
            raise ValueError(f"Invalid input parameters for {self.name}: {e}")

    def run(self, params: dict) -> ToolOutput:
        """
        Run the tool: validate input, execute, handle errors.

        This is the main entry point for tool execution.
        """
        try:
            # Validate input
            input_data = self.validate_input(params)

            # Execute
            result = self.execute(input_data)

            return result

        except ValueError as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_VALIDATION_ERROR",
                error_message=str(e)
            )
        except Exception as e:
            return self.handle_error(e)

    def handle_error(self, error: Exception) -> ToolOutput:
        """Convert exceptions to ToolOutput"""
        error_code = f"TOOL_{self.name.upper()}_ERROR"

        # Map specific exceptions to error codes
        if isinstance(error, ValueError):
            error_code = f"TOOL_{self.name.upper()}_VALIDATION_ERROR"
        elif isinstance(error, KeyError):
            error_code = f"TOOL_{self.name.upper()}_NOT_FOUND"
        elif isinstance(error, PermissionError):
            error_code = f"TOOL_{self.name.upper()}_PERMISSION_DENIED"

        return ToolOutput(
            success=False,
            error_code=error_code,
            error_message=str(error)
        )
