"""
Brain AI Integration - Connects AI to Brain Tools

This module provides the integration layer between the AI assistant
and the Brain tool system, enabling the AI to:
- Access user data through tools
- Execute actions on behalf of the user
- Retrieve context for RAG

Usage:
    from brain.ai.integration import BrainIntegration
    
    integration = BrainIntegration()
    
    # Get user context for AI
    context = integration.get_user_context()
    
    # Execute a tool via AI
    result = integration.execute_tool("CreateHabit", {"name": "Exercise"})
"""

from typing import Dict, Any, List, Optional, Type
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import logging

# Brain tools
from brain.tools.registry import ToolRegistry
from brain.core.result import ToolOutput

# AI components
from brain.ai.models import ProviderConfig, AIProvider, GenerationResult
from brain.ai.assistant import AIAssistant
from brain.ai.vector_store import VectorStore
from brain.ai.context_retriever import ContextRetriever


logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """Definition of a tool for AI function calling."""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str] = field(default_factory=list)
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required
                }
            }
        }


@dataclass
class ToolExecutionResult:
    """Result of a tool execution."""
    tool_name: str
    success: bool
    result: Any
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0


class BrainIntegration:
    """
    Integration layer between AI and Brain Tools.
    
    Provides:
    - Tool registry access for AI
    - User context retrieval for RAG
    - Safe tool execution with validation
    - Function calling support for LLMs
    
    Usage:
        integration = BrainIntegration()
        
        # Get context for RAG
        context = integration.get_user_context(user_id="default")
        
        # List available tools
        tools = integration.list_available_tools()
        
        # Execute a tool
        result = integration.execute_tool("GetHabits", {})
    """
    
    # Tools that are safe for AI to execute automatically
    SAFE_TOOLS = {
        # Read-only tools
        "GetHabits", "GetTasks", "GetGoals", "GetHealthData",
        "GetJobs", "GetCustomers", "GetExpenses", "GetTimeEntries",
        "GetQuotes", "GetMaterials", "GetSchedule",
        # Analysis tools
        "AnalyzePatterns", "GenerateInsights", "GetSummary",
        # Coach tools
        "GetCoachState", "GetInterventions"
    }
    
    # Tools that require user confirmation
    SENSITIVE_TOOLS = {
        "CreateHabit", "UpdateHabit", "DeleteHabit",
        "CreateTask", "UpdateTask", "DeleteTask",
        "CreateGoal", "UpdateGoal", "DeleteGoal",
        "CreateJob", "UpdateJob", "DeleteJob",
        "CreateCustomer", "UpdateCustomer", "DeleteCustomer",
        "RecordExpense", "RecordTimeEntry"
    }
    
    # Tools that are blocked from AI execution
    BLOCKED_TOOLS = {
        "DeleteAllData", "ExportAllData", "ResetDatabase",
        "ChangePassword", "UpdatePaymentInfo"
    }
    
    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        vector_store: Optional[VectorStore] = None,
        auto_discover: bool = True
    ):
        """
        Initialize Brain Integration.
        
        Args:
            tool_registry: Optional tool registry (will create one if not provided)
            vector_store: Optional vector store for RAG
            auto_discover: Whether to auto-discover tools
        """
        self._registry = tool_registry
        self._vector_store = vector_store
        self._auto_discover = auto_discover
        self._assistant: Optional[AIAssistant] = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize the integration.
        
        Returns:
            True if successful
        """
        try:
            # Initialize tool registry
            if self._registry is None:
                self._registry = ToolRegistry(
                    lazy_loading=True,
                    auto_discover=self._auto_discover
                )
            
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Brain integration: {e}")
            return False
    
    @property
    def registry(self) -> ToolRegistry:
        """Get the tool registry."""
        if self._registry is None:
            self._registry = ToolRegistry(lazy_loading=True, auto_discover=self._auto_discover)
        return self._registry
    
    def set_assistant(self, assistant: AIAssistant) -> None:
        """Set the AI assistant instance."""
        self._assistant = assistant
    
    # ============================================
    # Tool Management
    # ============================================
    
    def list_available_tools(self) -> List[str]:
        """
        List all available tools.
        
        Returns:
            List of tool names
        """
        return self.registry.list_tools()
    
    def get_tool_definitions(self, tool_names: Optional[List[str]] = None) -> List[ToolDefinition]:
        """
        Get tool definitions for AI function calling.
        
        Args:
            tool_names: Optional list of specific tools to get
            
        Returns:
            List of ToolDefinition objects
        """
        definitions = []
        tools = tool_names or self.list_available_tools()
        
        for name in tools:
            tool = self.registry.get(name)
            if tool:
                # Extract parameters from tool schema
                params = {}
                required = []
                
                if hasattr(tool, 'input_schema'):
                    schema = tool.input_schema
                    if isinstance(schema, dict):
                        params = schema.get('properties', {})
                        required = schema.get('required', [])
                
                definition = ToolDefinition(
                    name=name,
                    description=tool.description or f"Execute {name}",
                    parameters=params,
                    required=required
                )
                definitions.append(definition)
        
        return definitions
    
    def get_tools_for_llm(self, tool_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get tool definitions in LLM-compatible format.
        
        Args:
            tool_names: Optional list of specific tools
            
        Returns:
            List of tool definitions in OpenAI format
        """
        definitions = self.get_tool_definitions(tool_names)
        return [d.to_openai_format() for d in definitions]
    
    # ============================================
    # Tool Execution
    # ============================================
    
    def execute_tool(
        self,
        name: str,
        params: Dict[str, Any],
        require_confirmation: bool = True,
        user_confirmed: bool = False
    ) -> ToolExecutionResult:
        """
        Execute a tool with safety checks.
        
        Args:
            name: Tool name
            params: Tool parameters
            require_confirmation: Whether to require confirmation for sensitive tools
            user_confirmed: Whether the user has confirmed this execution
            
        Returns:
            ToolExecutionResult
        """
        import time
        start_time = time.time()
        
        try:
            # Check if tool is blocked
            if name in self.BLOCKED_TOOLS:
                return ToolExecutionResult(
                    tool_name=name,
                    success=False,
                    result=None,
                    error_message=f"Tool '{name}' is blocked from AI execution"
                )
            
            # Check if confirmation required
            if name in self.SENSITIVE_TOOLS and require_confirmation and not user_confirmed:
                return ToolExecutionResult(
                    tool_name=name,
                    success=False,
                    result=None,
                    error_message=f"Tool '{name}' requires user confirmation"
                )
            
            # Check if tool exists
            if not self.registry.has(name):
                return ToolExecutionResult(
                    tool_name=name,
                    success=False,
                    result=None,
                    error_message=f"Tool '{name}' not found"
                )
            
            # Execute the tool
            output: ToolOutput = self.registry.execute(name, params)
            
            execution_time = (time.time() - start_time) * 1000
            
            return ToolExecutionResult(
                tool_name=name,
                success=output.success,
                result=output.data if output.success else None,
                error_message=output.error_message if not output.success else None,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error executing tool {name}: {e}")
            
            return ToolExecutionResult(
                tool_name=name,
                success=False,
                result=None,
                error_message=str(e),
                execution_time_ms=execution_time
            )
    
    def execute_safe_tool(
        self,
        name: str,
        params: Dict[str, Any]
    ) -> ToolExecutionResult:
        """
        Execute a tool that's in the safe list.
        
        Args:
            name: Tool name (must be in SAFE_TOOLS)
            params: Tool parameters
            
        Returns:
            ToolExecutionResult
        """
        if name not in self.SAFE_TOOLS:
            return ToolExecutionResult(
                tool_name=name,
                success=False,
                result=None,
                error_message=f"Tool '{name}' is not in the safe list"
            )
        
        return self.execute_tool(name, params, require_confirmation=False)
    
    # ============================================
    # Context Retrieval
    # ============================================
    
    def get_user_context(
        self,
        user_id: str = "default",
        include_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive user context for AI.
        
        Gathers data from multiple tools to build a complete context
        for the AI assistant.
        
        Args:
            user_id: User identifier
            include_types: Types of data to include (habits, tasks, goals, health)
            
        Returns:
            Dictionary with user context
        """
        context = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }
        
        include_types = include_types or ["habits", "tasks", "goals", "health"]
        
        try:
            # Get habits
            if "habits" in include_types:
                result = self.execute_safe_tool("GetHabits", {})
                if result.success:
                    context["data"]["habits"] = result.result
            
            # Get tasks
            if "tasks" in include_types:
                result = self.execute_safe_tool("GetTasks", {})
                if result.success:
                    context["data"]["tasks"] = result.result
            
            # Get goals
            if "goals" in include_types:
                result = self.execute_safe_tool("GetGoals", {})
                if result.success:
                    context["data"]["goals"] = result.result
            
            # Get health data
            if "health" in include_types:
                result = self.execute_safe_tool("GetHealthData", {})
                if result.success:
                    context["data"]["health"] = result.result
            
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            context["error"] = str(e)
        
        return context
    
    def get_weekly_summary_context(self) -> Dict[str, Any]:
        """
        Get context specifically for weekly summary generation.
        
        Returns:
            Dictionary with weekly summary context
        """
        context = {
            "period": "weekly",
            "generated_at": datetime.now().isoformat(),
            "data": {}
        }
        
        try:
            # Get habits with streaks
            result = self.execute_safe_tool("GetHabits", {})
            if result.success:
                habits = result.result or []
                context["data"]["habits"] = {
                    "total": len(habits),
                    "active": len([h for h in habits if h.get("active", True)]),
                    "best_streaks": sorted(
                        [h for h in habits if h.get("streak", 0) > 0],
                        key=lambda x: x.get("streak", 0),
                        reverse=True
                    )[:5]
                }
            
            # Get task completion
            result = self.execute_safe_tool("GetTasks", {})
            if result.success:
                tasks = result.result or []
                completed = [t for t in tasks if t.get("completed", False)]
                context["data"]["tasks"] = {
                    "total": len(tasks),
                    "completed": len(completed),
                    "completion_rate": len(completed) / len(tasks) if tasks else 0
                }
            
            # Get goals progress
            result = self.execute_safe_tool("GetGoals", {})
            if result.success:
                goals = result.result or []
                context["data"]["goals"] = {
                    "total": len(goals),
                    "in_progress": len([g for g in goals if g.get("progress", 0) < 100]),
                    "completed": len([g for g in goals if g.get("progress", 0) >= 100])
                }
            
        except Exception as e:
            logger.error(f"Error getting weekly summary context: {e}")
            context["error"] = str(e)
        
        return context
    
    # ============================================
    # RAG Integration
    # ============================================
    
    def embed_user_data(self, user_id: str = "default") -> int:
        """
        Embed user data into the vector store for RAG.
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of documents embedded
        """
        if not self._vector_store:
            logger.warning("No vector store configured")
            return 0
        
        try:
            # Get user context
            context = self.get_user_context(user_id)
            
            documents = []
            metadatas = []
            ids = []
            
            # Embed habits
            for habit in context.get("data", {}).get("habits", []):
                doc = f"Habit: {habit.get('name', 'Unknown')}\n"
                doc += f"Streak: {habit.get('streak', 0)} days\n"
                doc += f"Completion Rate: {habit.get('completion_rate', 0) * 100:.0f}%"
                
                documents.append(doc)
                metadatas.append({
                    "type": "habit",
                    "user_id": user_id,
                    "habit_id": habit.get("id"),
                    "source": "brain_integration"
                })
                ids.append(f"habit_{habit.get('id', len(ids))}")
            
            # Embed tasks
            for task in context.get("data", {}).get("tasks", []):
                doc = f"Task: {task.get('title', 'Unknown')}\n"
                doc += f"Status: {'Completed' if task.get('completed') else 'Pending'}\n"
                if task.get("due_date"):
                    doc += f"Due: {task.get('due_date')}"
                
                documents.append(doc)
                metadatas.append({
                    "type": "task",
                    "user_id": user_id,
                    "task_id": task.get("id"),
                    "source": "brain_integration"
                })
                ids.append(f"task_{task.get('id', len(ids))}")
            
            # Embed goals
            for goal in context.get("data", {}).get("goals", []):
                doc = f"Goal: {goal.get('name', 'Unknown')}\n"
                doc += f"Progress: {goal.get('progress', 0)}%\n"
                if goal.get("target"):
                    doc += f"Target: {goal.get('target')}"
                
                documents.append(doc)
                metadatas.append({
                    "type": "goal",
                    "user_id": user_id,
                    "goal_id": goal.get("id"),
                    "source": "brain_integration"
                })
                ids.append(f"goal_{goal.get('id', len(ids))}")
            
            # Add to vector store
            if documents:
                from brain.ai.models import VectorDocument
                
                for i, doc in enumerate(documents):
                    vector_doc = VectorDocument(
                        id=ids[i],
                        content=doc,
                        source_type=metadatas[i].get("type", "unknown"),
                        source_id=metadatas[i].get(f"{metadatas[i].get('type', 'unknown')}_id", ""),
                        metadata=metadatas[i]
                    )
                    self._vector_store.add_document(vector_doc)
            
            return len(documents)
            
        except Exception as e:
            logger.error(f"Error embedding user data: {e}")
            return 0
    
    # ============================================
    # AI Tool Calling
    # ============================================
    
    def process_tool_call(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        auto_confirm_safe: bool = True
    ) -> Dict[str, Any]:
        """
        Process a tool call from the AI.
        
        Args:
            tool_name: Name of the tool to call
            tool_args: Arguments for the tool
            auto_confirm_safe: Whether to auto-confirm safe tools
            
        Returns:
            Dictionary with result for AI
        """
        # Check if tool is safe and auto-confirm is enabled
        if auto_confirm_safe and tool_name in self.SAFE_TOOLS:
            result = self.execute_tool(
                tool_name,
                tool_args,
                require_confirmation=False
            )
        else:
            result = self.execute_tool(
                tool_name,
                tool_args,
                require_confirmation=True,
                user_confirmed=False
            )
        
        return {
            "tool_name": tool_name,
            "success": result.success,
            "result": result.result,
            "error": result.error_message,
            "requires_confirmation": tool_name in self.SENSITIVE_TOOLS and not result.success
        }
    
    def get_tool_call_response(self, result: ToolExecutionResult) -> str:
        """
        Generate a response string from a tool execution result.
        
        Args:
            result: Tool execution result
            
        Returns:
            String response for the AI
        """
        if result.success:
            if result.result is None:
                return f"Successfully executed {result.tool_name}."
            
            if isinstance(result.result, dict):
                return json.dumps(result.result, indent=2, default=str)
            
            if isinstance(result.result, list):
                if len(result.result) == 0:
                    return f"No results from {result.tool_name}."
                return json.dumps(result.result, indent=2, default=str)
            
            return str(result.result)
        else:
            return f"Error executing {result.tool_name}: {result.error_message}"


# Singleton instance
_default_integration: Optional[BrainIntegration] = None


def get_integration() -> BrainIntegration:
    """
    Get the default BrainIntegration instance.
    
    Returns:
        BrainIntegration instance
    """
    global _default_integration
    if _default_integration is None:
        _default_integration = BrainIntegration()
        _default_integration.initialize()
    return _default_integration


def execute_tool(name: str, params: Dict[str, Any]) -> ToolExecutionResult:
    """
    Convenience function to execute a tool.
    
    Args:
        name: Tool name
        params: Tool parameters
        
    Returns:
        ToolExecutionResult
    """
    return get_integration().execute_tool(name, params)


def get_context() -> Dict[str, Any]:
    """
    Convenience function to get user context.
    
    Returns:
        User context dictionary
    """
    return get_integration().get_user_context()