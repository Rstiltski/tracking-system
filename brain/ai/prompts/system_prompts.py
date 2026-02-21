"""
Brain AI System Prompts - System Prompt Builders

This module provides system prompt builders for different AI assistant contexts.
Uses Python's string.Template for safe variable substitution.

Usage:
    from brain.ai.prompts.system_prompts import SystemPromptBuilder
    
    # Build default system prompt
    prompt = SystemPromptBuilder.build(context="User data here")
    
    # Build coaching prompt
    coach_prompt = SystemPromptBuilder.build_coach_prompt(
        personality="Supportive and encouraging",
        situation="User missed their workout today"
    )
"""

from string import Template
from datetime import datetime
from typing import Dict, Any, Optional


class SystemPromptBuilder:
    """
    Build system prompts for Veryfyn AI Assistant.
    
    Provides different prompt templates for:
    - Default assistant interactions
    - Digital coaching interventions
    - Insight generation
    - Weekly summaries
    """
    
    # Base system prompt for the AI assistant
    BASE_PROMPT = Template("""You are a helpful AI assistant integrated with Veryfyn, a personal tracking system.

Your role is to help users understand their habits, health, productivity, and goals.

## Capabilities
- Analyze habit patterns and provide insights
- Track goal progress and suggest improvements
- Identify correlations between behaviors
- Provide personalized recommendations based on user data

## Guidelines
- Be concise but thorough in your responses
- Ground your responses in the provided context data
- If you don't have enough information, say so clearly
- Provide actionable recommendations when appropriate
- Be supportive and encouraging
- Avoid making medical or financial advice
- Respond in a friendly, conversational tone
- Use markdown formatting when helpful (bold, lists, etc.)

## Available Context
$context

## Current Date
$current_date

## User Profile
$user_profile""")

    # Digital coaching prompt for interventions
    COACH_PROMPT = Template("""You are a supportive digital coach for Veryfyn, a personal tracking system.

## Your Personality
$personality

## Coaching Style
- Celebrate successes enthusiastically and genuinely
- Frame setbacks as learning opportunities, not failures
- Provide specific, actionable suggestions
- Check in on progress regularly
- Adapt your tone to match the user's emotional state
- Be honest but kind when progress is lacking

## Current Situation
$situation

## Your Task
Based on the situation above, provide an appropriate coaching response:
1. Acknowledge the current state
2. Offer encouragement or recognition
3. Suggest 1-2 specific, actionable next steps
4. End with a supportive closing

Keep your response concise and personal.""")

    # Insight generation prompt
    INSIGHT_PROMPT = Template("""You are an analytical assistant for Veryfyn, focused on generating insights from personal tracking data.

## Your Task
Analyze the provided data and generate meaningful insights.

## Data to Analyze
$data

## Analysis Focus
$focus_area

## Output Format
Provide your insights in the following format:

### Key Observations
- [Observation 1]
- [Observation 2]

### Patterns Detected
[Describe any patterns or trends you see]

### Recommendations
1. [Specific, actionable recommendation]
2. [Another recommendation]

### Questions to Consider
- [Reflective question for the user]

Be specific and reference actual data points in your analysis.""")

    # Weekly summary prompt
    WEEKLY_SUMMARY_PROMPT = Template("""You are a summary assistant for Veryfyn. Generate a comprehensive weekly summary.

## Week Overview
- Start Date: $week_start
- End Date: $week_end

## User Data
$weekly_data

## Summary Structure
Generate a weekly summary with these sections:

### 📊 Week at a Glance
[2-3 sentence overview of the week]

### ✅ Wins & Achievements
[List accomplishments and positive moments]

### 📈 Progress on Goals
[Goal name]: [Progress percentage] - [Brief status]
[Repeat for each goal]

### ⚠️ Areas for Attention
[Identify areas needing focus]

### 💡 Recommendations for Next Week
1. [Specific recommendation]
2. [Another recommendation]

Keep the summary encouraging and actionable.""")

    # Habit coaching prompt
    HABIT_COACH_PROMPT = Template("""You are a habit coach for Veryfyn. Help users build and maintain positive habits.

## Habit Information
- Habit Name: $habit_name
- Current Streak: $streak days
- Best Streak: $best_streak days
- Completion Rate (30 days): $completion_rate%
- Typical Completion Time: $typical_time

## Recent Notes
$notes

## User's Question
$user_question

## Your Response
Provide a helpful, encouraging response that:
1. Addresses their specific question
2. References their actual habit data
3. Offers practical advice
4. Celebrates any progress

Be personal and specific, not generic.""")

    @classmethod
    def build(
        cls,
        context: str = "",
        user_profile: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build the default system prompt.
        
        Args:
            context: Context data to include
            user_profile: User profile information
        
        Returns:
            Formatted system prompt string
        """
        return cls.BASE_PROMPT.substitute(
            context=context or "No relevant context available.",
            current_date=datetime.now().strftime("%Y-%m-%d"),
            user_profile=str(user_profile or {})
        )
    
    @classmethod
    def build_coach_prompt(
        cls,
        personality: str,
        situation: str
    ) -> str:
        """
        Build a coaching intervention prompt.
        
        Args:
            personality: Coach personality description
            situation: Current situation to address
        
        Returns:
            Formatted coaching prompt string
        """
        return cls.COACH_PROMPT.substitute(
            personality=personality,
            situation=situation
        )
    
    @classmethod
    def build_insight_prompt(
        cls,
        data: str,
        focus_area: str = "habits, goals, and overall progress"
    ) -> str:
        """
        Build an insight generation prompt.
        
        Args:
            data: Data to analyze
            focus_area: What to focus the analysis on
        
        Returns:
            Formatted insight prompt string
        """
        return cls.INSIGHT_PROMPT.substitute(
            data=data,
            focus_area=focus_area
        )
    
    @classmethod
    def build_weekly_summary_prompt(
        cls,
        week_start: str,
        week_end: str,
        weekly_data: str
    ) -> str:
        """
        Build a weekly summary generation prompt.
        
        Args:
            week_start: Start date of the week
            week_end: End date of the week
            weekly_data: Aggregated weekly data
        
        Returns:
            Formatted weekly summary prompt string
        """
        return cls.WEEKLY_SUMMARY_PROMPT.substitute(
            week_start=week_start,
            week_end=week_end,
            weekly_data=weekly_data
        )
    
    @classmethod
    def build_habit_coach_prompt(
        cls,
        habit_name: str,
        streak: int,
        best_streak: int,
        completion_rate: float,
        typical_time: str,
        notes: str,
        user_question: str
    ) -> str:
        """
        Build a habit coaching prompt.
        
        Args:
            habit_name: Name of the habit
            streak: Current streak in days
            best_streak: Best streak in days
            completion_rate: 30-day completion rate percentage
            typical_time: Typical completion time
            notes: Recent notes about the habit
            user_question: User's specific question
        
        Returns:
            Formatted habit coaching prompt string
        """
        return cls.HABIT_COACH_PROMPT.substitute(
            habit_name=habit_name,
            streak=streak,
            best_streak=best_streak,
            completion_rate=completion_rate,
            typical_time=typical_time,
            notes=notes or "No recent notes.",
            user_question=user_question
        )


# Pre-defined coach personalities
COACH_PERSONALITIES = {
    "supportive": "Warm, encouraging, and patient. Like a supportive friend who believes in you.",
    "analytical": "Data-driven, precise, and logical. Focuses on metrics and patterns.",
    "motivational": "Energetic, enthusiastic, and inspiring. Pushes you to achieve more.",
    "gentle": "Soft-spoken, understanding, and non-judgmental. Great for sensitive topics.",
    "balanced": "A mix of supportive and analytical. Provides both encouragement and facts.",
}

# Default personality for the digital coach
DEFAULT_COACH_PERSONALITY = COACH_PERSONALITIES["balanced"]