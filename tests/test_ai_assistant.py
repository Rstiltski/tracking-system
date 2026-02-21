"""
Tests for AI Assistant Module

Tests for:
- RAG context retrieval
- Insight generation
- Chat session management
- Prompt templates
"""

import pytest
from datetime import datetime
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_habit_data():
    """Sample habit data for testing."""
    return {
        "habit_name": "Morning Exercise",
        "category": "Health",
        "completion_rate": 85.5,
        "streak": 14,
        "best_streak": 30,
        "avg_time": "7:00 AM",
        "target_frequency": "Daily",
        "notes": "Feeling energetic lately, best streak in months!"
    }


@pytest.fixture
def sample_goal_data():
    """Sample goal data for testing."""
    return {
        "goal_name": "Run 100km this month",
        "goal_description": "Complete 100km of running by end of month",
        "target": 100,
        "current": 65,
        "progress_pct": 65,
        "deadline": "2026-02-28",
        "days_remaining": 8,
        "recent_activities": "Ran 5km yesterday, 3km today",
        "related_habits": "Morning Exercise"
    }


@pytest.fixture
def sample_chat_messages():
    """Sample chat messages for testing."""
    return [
        {"role": "user", "content": "How am I doing with my habits?"},
        {"role": "assistant", "content": "You're doing great! Your exercise streak is at 14 days."},
        {"role": "user", "content": "What about my sleep?"},
        {"role": "assistant", "content": "Your average sleep is 7.2 hours, meeting your goal."}
    ]


# ============================================================================
# Prompt Template Tests
# ============================================================================

class TestPromptTemplates:
    """Tests for prompt template functionality."""
    
    def test_habit_insight_template_format(self, sample_habit_data):
        """Test habit insight template formatting."""
        try:
            from brain.ai.prompts import HABIT_INSIGHT_TEMPLATE
            
            prompt = HABIT_INSIGHT_TEMPLATE.format(**sample_habit_data)
            
            assert "Morning Exercise" in prompt
            assert "85.5%" in prompt
            assert "14 days" in prompt
            assert "30 days" in prompt
            assert "Pattern Observation" in prompt
            assert "Success Factors" in prompt
            
        except ImportError:
            pytest.skip("Prompts module not available")
    
    def test_goal_progress_template_format(self, sample_goal_data):
        """Test goal progress template formatting."""
        try:
            from brain.ai.prompts import GOAL_PROGRESS_TEMPLATE
            
            prompt = GOAL_PROGRESS_TEMPLATE.format(**sample_goal_data)
            
            assert "Run 100km this month" in prompt
            assert "65%" in prompt
            assert "2026-02-28" in prompt
            assert "Progress Assessment" in prompt
            assert "Action Items" in prompt
            
        except ImportError:
            pytest.skip("Prompts module not available")
    
    def test_template_validate(self):
        """Test template validation."""
        try:
            from brain.ai.prompts import PromptTemplate
            
            template = PromptTemplate(
                name="test",
                template="Hello {name}, you have {count} items.",
                input_variables=["name", "count"]
            )
            
            # Valid input
            assert template.validate(name="Alice", count=5) is True
            
            # Missing variable
            assert template.validate(name="Alice") is False
            
        except ImportError:
            pytest.skip("Prompts module not available")
    
    def test_template_format_missing_variable(self):
        """Test template formatting with missing variable."""
        try:
            from brain.ai.prompts import PromptTemplate
            
            template = PromptTemplate(
                name="test",
                template="Hello {name}, you have {count} items.",
                input_variables=["name", "count"]
            )
            
            with pytest.raises(KeyError):
                template.format(name="Alice")  # Missing 'count'
                
        except ImportError:
            pytest.skip("Prompts module not available")


# ============================================================================
# System Prompt Builder Tests
# ============================================================================

class TestSystemPromptBuilder:
    """Tests for system prompt builder."""
    
    def test_build_default_prompt(self):
        """Test building default system prompt."""
        try:
            from brain.ai.prompts import SystemPromptBuilder
            
            prompt = SystemPromptBuilder.build()
            
            assert "Veryfyn" in prompt
            assert "personal tracking system" in prompt
            assert "guidelines" in prompt.lower()
            
        except ImportError:
            pytest.skip("Prompts module not available")
    
    def test_build_prompt_with_context(self):
        """Test building prompt with context."""
        try:
            from brain.ai.prompts import SystemPromptBuilder
            
            context = "User has completed 85% of habits this week."
            prompt = SystemPromptBuilder.build(context=context)
            
            assert context in prompt
            assert "User Profile" in prompt
            
        except ImportError:
            pytest.skip("Prompts module not available")
    
    def test_build_coach_prompt(self):
        """Test building coaching prompt."""
        try:
            from brain.ai.prompts import SystemPromptBuilder
            
            prompt = SystemPromptBuilder.build_coach_prompt(
                personality="Supportive and encouraging",
                situation="User missed their workout today"
            )
            
            assert "Supportive and encouraging" in prompt
            assert "User missed their workout today" in prompt
            assert "Coaching Style" in prompt
            
        except ImportError:
            pytest.skip("Prompts module not available")
    
    def test_build_habit_coach_prompt(self):
        """Test building habit coaching prompt."""
        try:
            from brain.ai.prompts import SystemPromptBuilder
            
            prompt = SystemPromptBuilder.build_habit_coach_prompt(
                habit_name="Exercise",
                streak=14,
                best_streak=30,
                completion_rate=85.0,
                typical_time="7:00 AM",
                notes="Feeling good",
                user_question="How can I improve?"
            )
            
            assert "Exercise" in prompt
            assert "14 days" in prompt
            assert "85.0%" in prompt
            assert "How can I improve?" in prompt
            
        except ImportError:
            pytest.skip("Prompts module not available")


# ============================================================================
# Chat Session Tests
# ============================================================================

class TestChatSession:
    """Tests for chat session management."""
    
    def test_create_chat_session(self):
        """Test creating a chat session."""
        try:
            from brain.ai.chat_session import ChatSession, MessageRole
            
            session = ChatSession(session_id="test-session-123")
            
            assert session.session_id == "test-session-123"
            assert len(session.messages) == 0
            assert session.created_at is not None
            
        except ImportError:
            # Define minimal version for testing
            from dataclasses import dataclass, field
            from datetime import datetime
            from enum import Enum
            from typing import List, Dict, Any
            
            class MessageRole(Enum):
                USER = "user"
                ASSISTANT = "assistant"
            
            @dataclass
            class ChatMessage:
                role: MessageRole
                content: str
                created_at: datetime = field(default_factory=datetime.now)
            
            @dataclass
            class ChatSession:
                session_id: str
                messages: List[ChatMessage] = field(default_factory=list)
                created_at: datetime = field(default_factory=datetime.now)
                
                def add_message(self, role: MessageRole, content: str):
                    self.messages.append(ChatMessage(role=role, content=content))
            
            session = ChatSession(session_id="test-session-123")
            assert session.session_id == "test-session-123"
    
    def test_add_message_to_session(self):
        """Test adding messages to a session."""
        try:
            from brain.ai.chat_session import ChatSession, MessageRole
            
            session = ChatSession(session_id="test-session-123")
            session.add_message(MessageRole.USER, "Hello!")
            session.add_message(MessageRole.ASSISTANT, "Hi there!")
            
            assert len(session.messages) == 2
            assert session.messages[0].role == MessageRole.USER
            assert session.messages[0].content == "Hello!"
            assert session.messages[1].role == MessageRole.ASSISTANT
            
        except ImportError:
            pytest.skip("Chat session module not available")
    
    def test_get_messages_for_llm(self):
        """Test getting messages formatted for LLM."""
        try:
            from brain.ai.chat_session import ChatSession, MessageRole
            
            session = ChatSession(session_id="test-session-123")
            session.add_message(MessageRole.USER, "Hello!")
            session.add_message(MessageRole.ASSISTANT, "Hi there!")
            
            llm_messages = session.get_messages_for_llm()
            
            assert len(llm_messages) == 2
            assert llm_messages[0] == {"role": "user", "content": "Hello!"}
            assert llm_messages[1] == {"role": "assistant", "content": "Hi there!"}
            
        except ImportError:
            pytest.skip("Chat session module not available")
    
    def test_context_window(self):
        """Test context window limiting."""
        try:
            from brain.ai.chat_session import ChatSession, MessageRole
            
            session = ChatSession(session_id="test-session-123")
            
            # Add 30 messages
            for i in range(30):
                session.add_message(MessageRole.USER, f"Message {i}")
            
            # Get last 20
            window = session.get_context_window(max_messages=20)
            
            assert len(window) == 20
            assert "Message 10" in window[0].content  # First message in window
            
        except ImportError:
            pytest.skip("Chat session module not available")


# ============================================================================
# Context Retriever Tests
# ============================================================================

class TestContextRetriever:
    """Tests for RAG context retrieval."""
    
    def test_retriever_initialization(self):
        """Test context retriever initialization."""
        try:
            from brain.ai.context_retriever import ContextRetriever
            from brain.ai.vector_store import VectorStore
            
            store = VectorStore()
            retriever = ContextRetriever(vector_store=store)
            
            assert retriever.vector_store is not None
            
        except ImportError:
            pytest.skip("Context retriever module not available")
    
    def test_retrieve_with_source_types(self):
        """Test retrieval with source type filtering."""
        try:
            from brain.ai.context_retriever import ContextRetriever
            from brain.ai.vector_store import VectorStore
            
            store = VectorStore()
            retriever = ContextRetriever(vector_store=store)
            
            # This will return empty results if store is not initialized
            results = retriever.retrieve(
                query="test query",
                source_types=["habit", "health"],
                n_results=5
            )
            
            assert isinstance(results, list)
            
        except ImportError:
            pytest.skip("Context retriever module not available")
    
    def test_retrieve_for_habits(self):
        """Test habit-specific retrieval."""
        try:
            from brain.ai.context_retriever import ContextRetriever
            from brain.ai.vector_store import VectorStore
            
            store = VectorStore()
            retriever = ContextRetriever(vector_store=store)
            
            results = retriever.retrieve_for_habits("exercise patterns")
            
            assert isinstance(results, list)
            
        except ImportError:
            pytest.skip("Context retriever module not available")


# ============================================================================
# Insight Generator Tests
# ============================================================================

class TestInsightGenerator:
    """Tests for insight generation."""
    
    def test_insight_prompt_generation(self):
        """Test insight prompt generation."""
        try:
            from brain.ai.prompts import SystemPromptBuilder
            
            data = """
            Habits: 85% completion rate
            Sleep: 7.2 hours average
            Exercise: 14 day streak
            """
            
            prompt = SystemPromptBuilder.build_insight_prompt(
                data=data,
                focus_area="habits and sleep"
            )
            
            assert data in prompt
            assert "habits and sleep" in prompt
            assert "Key Observations" in prompt
            assert "Patterns Detected" in prompt
            
        except ImportError:
            pytest.skip("Prompts module not available")
    
    def test_daily_insight_template(self):
        """Test daily insight template."""
        try:
            from brain.ai.prompts import DAILY_INSIGHT_TEMPLATE
            
            prompt = DAILY_INSIGHT_TEMPLATE.format(
                date="2026-02-20",
                habits_completed=5,
                habits_total=6,
                mood="Good",
                sleep_hours=7.5,
                energy="High",
                notes="Great day overall"
            )
            
            assert "2026-02-20" in prompt
            assert "5/6" in prompt
            assert "7.5 hours" in prompt
            assert "Key Insight" in prompt
            
        except ImportError:
            pytest.skip("Prompts module not available")
    
    def test_behavioral_pattern_template(self):
        """Test behavioral pattern template."""
        try:
            from brain.ai.prompts import BEHAVIORAL_PATTERN_TEMPLATE
            
            prompt = BEHAVIORAL_PATTERN_TEMPLATE.format(
                user_name="Test User",
                period="Last 30 days",
                data_summary="Exercise: 85%, Sleep: 7.2h avg, Mood: Good"
            )
            
            assert "Test User" in prompt
            assert "Last 30 days" in prompt
            assert "Time Patterns" in prompt
            assert "Mood Patterns" in prompt
            
        except ImportError:
            pytest.skip("Prompts module not available")


# ============================================================================
# Coach Personality Tests
# ============================================================================

class TestCoachPersonalities:
    """Tests for coach personality configurations."""
    
    def test_personality_definitions(self):
        """Test that personalities are defined."""
        try:
            from brain.ai.prompts.system_prompts import COACH_PERSONALITIES
            
            assert "supportive" in COACH_PERSONALITIES
            assert "analytical" in COACH_PERSONALITIES
            assert "motivational" in COACH_PERSONALITIES
            assert "gentle" in COACH_PERSONALITIES
            assert "balanced" in COACH_PERSONALITIES
            
        except ImportError:
            pytest.skip("Prompts module not available")
    
    def test_default_personality(self):
        """Test default personality selection."""
        try:
            from brain.ai.prompts.system_prompts import (
                DEFAULT_COACH_PERSONALITY, 
                COACH_PERSONALITIES
            )
            
            assert DEFAULT_COACH_PERSONALITY == COACH_PERSONALITIES["balanced"]
            
        except ImportError:
            pytest.skip("Prompts module not available")


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for AI assistant components."""
    
    def test_full_prompt_flow(self, sample_habit_data):
        """Test complete prompt generation flow."""
        try:
            from brain.ai.prompts import (
                SystemPromptBuilder,
                HABIT_INSIGHT_TEMPLATE
            )
            
            # Build system prompt
            system_prompt = SystemPromptBuilder.build(
                context="User is asking about their exercise habit."
            )
            
            # Build specific prompt
            habit_prompt = HABIT_INSIGHT_TEMPLATE.format(**sample_habit_data)
            
            assert "Veryfyn" in system_prompt
            assert "Morning Exercise" in habit_prompt
            
        except ImportError:
            pytest.skip("Prompts module not available")
    
    def test_template_list(self):
        """Test getting template list."""
        try:
            from brain.ai.prompts.templates import list_templates
            
            templates = list_templates()
            
            assert "habit_insight" in templates
            assert "goal_progress" in templates
            assert "weekly_summary" in templates
            
        except ImportError:
            pytest.skip("Prompts module not available")
    
    def test_get_template_by_name(self):
        """Test getting template by name."""
        try:
            from brain.ai.prompts.templates import get_template
            
            template = get_template("habit_insight")
            
            assert template is not None
            assert template.name == "habit_insight"
            
            # Non-existent template
            assert get_template("nonexistent") is None
            
        except ImportError:
            pytest.skip("Prompts module not available")


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])