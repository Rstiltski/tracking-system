"""
Tests for AI Integration Module

Tests the integration between AI components and Brain tools including:
- BrainIntegration class
- Tool execution
- Context retrieval
- Weekly summary generation
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

# Integration module
from brain.ai.integration import (
    BrainIntegration,
    ToolDefinition,
    ToolExecutionResult,
    get_integration,
    execute_tool,
    get_context
)

# Weekly summary
from brain.ai.weekly_summary import (
    WeeklySummaryGenerator,
    WeeklySummary,
    HabitSummary,
    TaskSummary,
    GoalSummary,
    HealthSummary,
    generate_weekly_summary,
    get_summary_json
)


# ============================================
# Test Data
# ============================================

def get_mock_user_data() -> Dict[str, Any]:
    """Get mock user data for testing."""
    return {
        "habits": [
            {
                "id": "habit_1",
                "name": "Morning Exercise",
                "streak": 15,
                "best_streak": 30,
                "completion_rate": 0.85,
                "active": True
            },
            {
                "id": "habit_2",
                "name": "Meditation",
                "streak": 5,
                "best_streak": 21,
                "completion_rate": 0.60,
                "active": True
            }
        ],
        "tasks": [
            {"id": "task_1", "title": "Complete project", "completed": True, "due_date": None},
            {"id": "task_2", "title": "Review code", "completed": False, "due_date": None},
            {"id": "task_3", "title": "Write docs", "completed": True, "due_date": None}
        ],
        "goals": [
            {"id": "goal_1", "name": "Run 100km", "progress": 75, "target_date": None},
            {"id": "goal_2", "name": "Read 12 books", "progress": 40, "target_date": None}
        ],
        "health": {
            "sleep": [7.5, 6.0, 7.0, 6.5, 7.0, 6.0, 7.5],
            "mood": [4, 3, 4, 3, 4, 3, 4]
        }
    }


# ============================================
# Tool Definition Tests
# ============================================

class TestToolDefinition:
    """Tests for ToolDefinition dataclass."""
    
    def test_tool_definition_creation(self):
        """Test creating a tool definition."""
        definition = ToolDefinition(
            name="TestTool",
            description="A test tool",
            parameters={"param1": {"type": "string"}},
            required=["param1"]
        )
        
        assert definition.name == "TestTool"
        assert definition.description == "A test tool"
        assert "param1" in definition.parameters
        assert "param1" in definition.required
    
    def test_tool_definition_to_openai_format(self):
        """Test converting to OpenAI format."""
        definition = ToolDefinition(
            name="TestTool",
            description="A test tool",
            parameters={"param1": {"type": "string"}},
            required=["param1"]
        )
        
        result = definition.to_openai_format()
        
        assert result["type"] == "function"
        assert result["function"]["name"] == "TestTool"
        assert result["function"]["description"] == "A test tool"
        assert "parameters" in result["function"]
    
    def test_tool_definition_defaults(self):
        """Test default values for tool definition."""
        definition = ToolDefinition(
            name="TestTool",
            description="A test tool",
            parameters={}
        )
        
        assert definition.required == []


# ============================================
# Tool Execution Result Tests
# ============================================

class TestToolExecutionResult:
    """Tests for ToolExecutionResult dataclass."""
    
    def test_successful_result(self):
        """Test successful execution result."""
        result = ToolExecutionResult(
            tool_name="TestTool",
            success=True,
            result={"data": "value"},
            execution_time_ms=10.5
        )
        
        assert result.tool_name == "TestTool"
        assert result.success is True
        assert result.result == {"data": "value"}
        assert result.error_message is None
    
    def test_failed_result(self):
        """Test failed execution result."""
        result = ToolExecutionResult(
            tool_name="TestTool",
            success=False,
            result=None,
            error_message="Tool not found"
        )
        
        assert result.success is False
        assert result.error_message == "Tool not found"


# ============================================
# Brain Integration Tests
# ============================================

class TestBrainIntegration:
    """Tests for BrainIntegration class."""
    
    def test_integration_initialization(self):
        """Test integration initialization."""
        integration = BrainIntegration()
        
        assert integration._initialized is False
        assert integration._auto_discover is True
    
    def test_integration_initialize(self):
        """Test integration initialize method."""
        integration = BrainIntegration()
        result = integration.initialize()
        
        assert result is True
        assert integration._initialized is True
    
    def test_list_available_tools(self):
        """Test listing available tools."""
        integration = BrainIntegration()
        integration.initialize()
        
        tools = integration.list_available_tools()
        
        assert isinstance(tools, list)
    
    def test_safe_tools_constant(self):
        """Test SAFE_TOOLS constant."""
        assert "GetHabits" in BrainIntegration.SAFE_TOOLS
        assert "GetTasks" in BrainIntegration.SAFE_TOOLS
        assert "GetGoals" in BrainIntegration.SAFE_TOOLS
    
    def test_sensitive_tools_constant(self):
        """Test SENSITIVE_TOOLS constant."""
        assert "CreateHabit" in BrainIntegration.SENSITIVE_TOOLS
        assert "DeleteTask" in BrainIntegration.SENSITIVE_TOOLS
    
    def test_blocked_tools_constant(self):
        """Test BLOCKED_TOOLS constant."""
        assert "DeleteAllData" in BrainIntegration.BLOCKED_TOOLS
        assert "ResetDatabase" in BrainIntegration.BLOCKED_TOOLS
    
    def test_execute_blocked_tool(self):
        """Test executing a blocked tool."""
        integration = BrainIntegration()
        integration.initialize()
        
        result = integration.execute_tool("DeleteAllData", {})
        
        assert result.success is False
        assert result.error_message is not None
        assert "blocked" in result.error_message.lower()
    
    def test_execute_nonexistent_tool(self):
        """Test executing a non-existent tool."""
        integration = BrainIntegration()
        integration.initialize()
        
        result = integration.execute_tool("NonExistentTool", {})
        
        assert result.success is False
        assert result.error_message is not None
        assert "not found" in result.error_message.lower()
    
    def test_execute_safe_tool_not_in_list(self):
        """Test execute_safe_tool with non-safe tool."""
        integration = BrainIntegration()
        integration.initialize()
        
        result = integration.execute_safe_tool("CreateHabit", {"name": "Test"})
        
        assert result.success is False
        assert result.error_message is not None
        assert "not in the safe list" in result.error_message.lower()


# ============================================
# Context Retrieval Tests
# ============================================

class TestContextRetrieval:
    """Tests for context retrieval."""
    
    @patch('brain.ai.integration.BrainIntegration.execute_safe_tool')
    def test_get_user_context(self, mock_execute):
        """Test getting user context."""
        mock_execute.return_value = ToolExecutionResult(
            tool_name="GetHabits",
            success=True,
            result=[{"name": "Exercise", "streak": 10}]
        )
        
        integration = BrainIntegration()
        integration._initialized = True
        
        context = integration.get_user_context()
        
        assert "user_id" in context
        assert "timestamp" in context
        assert "data" in context
    
    def test_get_weekly_summary_context(self):
        """Test getting weekly summary context."""
        integration = BrainIntegration()
        integration._initialized = True
        
        # Mock execute_safe_tool
        with patch.object(integration, 'execute_safe_tool') as mock_execute:
            mock_execute.return_value = ToolExecutionResult(
                tool_name="GetHabits",
                success=True,
                result=get_mock_user_data()["habits"]
            )
            
            context = integration.get_weekly_summary_context()
            
            assert "period" in context
            assert "generated_at" in context


# ============================================
# Weekly Summary Tests
# ============================================

class TestWeeklySummaryGenerator:
    """Tests for WeeklySummaryGenerator class."""
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = WeeklySummaryGenerator()
        
        assert generator._integration is None
        assert generator._assistant is None
    
    def test_build_habit_summaries(self):
        """Test building habit summaries."""
        generator = WeeklySummaryGenerator()
        
        context = {"data": {"habits": get_mock_user_data()["habits"]}}
        
        summaries = generator._build_habit_summaries(context)
        
        assert len(summaries) == 2
        assert summaries[0].name == "Morning Exercise"
        assert summaries[0].streak == 15
    
    def test_build_task_summary(self):
        """Test building task summary."""
        generator = WeeklySummaryGenerator()
        
        context = {"data": {"tasks": get_mock_user_data()["tasks"]}}
        
        summary = generator._build_task_summary(context)
        
        assert summary.total == 3
        assert summary.completed == 2
        assert summary.completion_rate == pytest.approx(2/3, rel=0.01)
    
    def test_build_goal_summaries(self):
        """Test building goal summaries."""
        generator = WeeklySummaryGenerator()
        
        context = {"data": {"goals": get_mock_user_data()["goals"]}}
        
        summaries = generator._build_goal_summaries(context)
        
        assert len(summaries) == 2
        assert summaries[0].progress == 75
    
    def test_build_health_summary(self):
        """Test building health summary."""
        generator = WeeklySummaryGenerator()
        
        context = {"data": {"health": get_mock_user_data()["health"]}}
        
        summary = generator._build_health_summary(context)
        
        assert summary.avg_sleep is not None
        assert summary.avg_mood is not None
        assert summary.sleep_trend in ["improving", "declining", "stable"]
    
    def test_calculate_score(self):
        """Test calculating overall score."""
        generator = WeeklySummaryGenerator()
        
        habits = [
            HabitSummary(name="Test", streak=10, best_streak=20, 
                        completion_rate=0.8, status="thriving", trend="improving")
        ]
        
        tasks = TaskSummary(total=10, completed=8, completion_rate=0.8, 
                           overdue=0, categories={})
        
        goals = [
            GoalSummary(name="Test Goal", progress=50, status="on_track", 
                       days_remaining=30)
        ]
        
        health = HealthSummary(avg_sleep=7.5, sleep_trend="stable",
                              avg_mood=4.0, mood_trend="improving", alerts=[])
        
        score = generator._calculate_score(habits, tasks, goals, health)
        
        assert 0 <= score <= 100
    
    def test_generate_highlights(self):
        """Test generating highlights."""
        generator = WeeklySummaryGenerator()
        
        habits = [
            HabitSummary(name="Exercise", streak=10, best_streak=10,
                        completion_rate=0.9, status="thriving", trend="improving")
        ]
        
        tasks = TaskSummary(total=10, completed=9, completion_rate=0.9,
                           overdue=0, categories={})
        
        goals = []
        
        health = HealthSummary(avg_sleep=8.0, sleep_trend="improving",
                              avg_mood=4.5, mood_trend="improving", alerts=[])
        
        highlights = generator._generate_highlights(habits, tasks, goals, health)
        
        assert len(highlights) > 0
    
    def test_calculate_trend(self):
        """Test trend calculation."""
        generator = WeeklySummaryGenerator()
        
        # Improving trend
        data_improving = [3.0, 3.0, 4.0, 4.0, 5.0, 5.0]
        assert generator._calculate_trend(data_improving) == "improving"
        
        # Declining trend
        data_declining = [5.0, 5.0, 4.0, 4.0, 3.0, 3.0]
        assert generator._calculate_trend(data_declining) == "declining"
        
        # Stable trend
        data_stable = [4.0, 4.0, 4.0, 4.0, 4.0, 4.0]
        assert generator._calculate_trend(data_stable) == "stable"


# ============================================
# Weekly Summary Dataclass Tests
# ============================================

class TestWeeklySummaryDataclasses:
    """Tests for summary dataclasses."""
    
    def test_habit_summary(self):
        """Test HabitSummary dataclass."""
        summary = HabitSummary(
            name="Exercise",
            streak=15,
            best_streak=30,
            completion_rate=0.85,
            status="thriving",
            trend="improving"
        )
        
        assert summary.name == "Exercise"
        assert summary.streak == 15
        assert summary.status == "thriving"
    
    def test_task_summary(self):
        """Test TaskSummary dataclass."""
        summary = TaskSummary(
            total=10,
            completed=8,
            completion_rate=0.8,
            overdue=2,
            categories={"work": 5, "personal": 5}
        )
        
        assert summary.total == 10
        assert summary.completion_rate == 0.8
        assert summary.overdue == 2
    
    def test_goal_summary(self):
        """Test GoalSummary dataclass."""
        summary = GoalSummary(
            name="Run 100km",
            progress=75,
            status="on_track",
            days_remaining=30
        )
        
        assert summary.name == "Run 100km"
        assert summary.progress == 75
        assert summary.days_remaining == 30
    
    def test_health_summary(self):
        """Test HealthSummary dataclass."""
        summary = HealthSummary(
            avg_sleep=7.5,
            sleep_trend="stable",
            avg_mood=4.0,
            mood_trend="improving",
            alerts=["Low sleep detected"]
        )
        
        assert summary.avg_sleep == 7.5
        assert summary.sleep_trend == "stable"
        assert len(summary.alerts) == 1
    
    def test_weekly_summary_to_dict(self):
        """Test WeeklySummary to_dict method."""
        summary = WeeklySummary(
            generated_at=datetime.now(),
            period_start=datetime.now() - timedelta(days=7),
            period_end=datetime.now(),
            overview="Test overview",
            highlights=["Highlight 1"],
            habit_summaries=[],
            task_summary=TaskSummary(total=0, completed=0, completion_rate=0, 
                                    overdue=0, categories={}),
            goal_summaries=[],
            health_summary=HealthSummary(avg_sleep=None, sleep_trend="stable",
                                        avg_mood=None, mood_trend="stable", alerts=[]),
            insights=["Insight 1"],
            recommendations=["Rec 1"],
            encouragement="Keep going!",
            score=75.0
        )
        
        result = summary.to_dict()
        
        assert "generated_at" in result
        assert "overview" in result
        assert result["score"] == 75.0


# ============================================
# Convenience Function Tests
# ============================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_get_integration_singleton(self):
        """Test get_integration returns singleton."""
        integration1 = get_integration()
        integration2 = get_integration()
        
        assert integration1 is integration2
    
    def test_execute_tool_function(self):
        """Test execute_tool convenience function."""
        result = execute_tool("NonExistentTool", {})
        
        assert isinstance(result, ToolExecutionResult)
        assert result.success is False
    
    def test_get_context_function(self):
        """Test get_context convenience function."""
        context = get_context()
        
        assert isinstance(context, dict)
        assert "user_id" in context


# ============================================
# Integration Tests
# ============================================

class TestFullIntegration:
    """Full integration tests."""
    
    @patch('brain.ai.integration.BrainIntegration.execute_safe_tool')
    def test_full_weekly_summary_generation(self, mock_execute):
        """Test full weekly summary generation."""
        # Mock the tool responses
        mock_execute.side_effect = [
            ToolExecutionResult("GetHabits", True, get_mock_user_data()["habits"], None, 10),
            ToolExecutionResult("GetTasks", True, get_mock_user_data()["tasks"], None, 10),
            ToolExecutionResult("GetGoals", True, get_mock_user_data()["goals"], None, 10),
            ToolExecutionResult("GetHealthData", True, get_mock_user_data()["health"], None, 10),
        ]
        
        generator = WeeklySummaryGenerator()
        
        # Mock the integration
        with patch.object(generator, 'integration') as mock_integration:
            mock_integration.get_user_context.return_value = {"data": get_mock_user_data()}
            
            summary = generator.generate(include_ai_insights=False)
            
            assert isinstance(summary, WeeklySummary)
            assert summary.score >= 0
            assert summary.score <= 100
            assert len(summary.overview) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])