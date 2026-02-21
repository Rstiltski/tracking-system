"""
Brain AI Prompt Templates - Pre-defined Templates

This module provides pre-defined prompt templates for specific tasks.
Each template is designed for a particular use case with clear input variables.

Usage:
    from brain.ai.prompts.templates import HABIT_INSIGHT_TEMPLATE, GOAL_PROGRESS_TEMPLATE
    
    # Format a template with data
    prompt = HABIT_INSIGHT_TEMPLATE.format(
        habit_name="Morning Exercise",
        completion_rate=85,
        streak=14,
        best_streak=30,
        avg_time="7:00 AM",
        notes="Feeling energetic lately"
    )
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PromptTemplate:
    """
    Reusable prompt template.
    
    Attributes:
        name: Template identifier
        template: Template string with {placeholders}
        input_variables: List of required variable names
        description: What this template is used for
    """
    name: str
    template: str
    input_variables: List[str]
    description: str = ""
    
    def format(self, **kwargs) -> str:
        """
        Format the template with provided values.
        
        Args:
            **kwargs: Values for template variables
            
        Returns:
            Formatted prompt string
            
        Raises:
            KeyError: If required variable is missing
        """
        return self.template.format(**kwargs)
    
    def validate(self, **kwargs) -> bool:
        """
        Check if all required variables are provided.
        
        Args:
            **kwargs: Values to validate
            
        Returns:
            True if all required variables present
        """
        return all(var in kwargs for var in self.input_variables)


# ============================================================================
# HABIT-RELATED TEMPLATES
# ============================================================================

HABIT_INSIGHT_TEMPLATE = PromptTemplate(
    name="habit_insight",
    template="""Analyze the following habit data and provide actionable insights:

## Habit Overview
- Name: {habit_name}
- Category: {category}
- 30-Day Completion Rate: {completion_rate}%
- Current Streak: {streak} days
- Best Streak: {best_streak} days
- Average Completion Time: {avg_time}
- Target Frequency: {target_frequency}

## Recent Notes
{notes}

## Your Analysis
Please provide:

1. **Pattern Observation**: What patterns do you notice in this habit data?

2. **Success Factors**: What seems to be helping this habit succeed?

3. **Improvement Suggestions**: What specific changes could improve consistency?

4. **Optimal Timing**: Based on the average completion time, any timing recommendations?

Keep your analysis concise but actionable. Reference specific data points.""",
    input_variables=[
        "habit_name", "category", "completion_rate", "streak",
        "best_streak", "avg_time", "target_frequency", "notes"
    ],
    description="Generate insights for a single habit based on tracking data"
)

HABIT_COMPARISON_TEMPLATE = PromptTemplate(
    name="habit_comparison",
    template="""Compare these two habits and provide insights:

## Habit A: {habit_a_name}
- Completion Rate: {habit_a_rate}%
- Streak: {habit_a_streak} days
- Notes: {habit_a_notes}

## Habit B: {habit_b_name}
- Completion Rate: {habit_b_rate}%
- Streak: {habit_b_streak} days
- Notes: {habit_b_notes}

## Comparison Analysis
1. Which habit is performing better and why?
2. Are there any patterns that explain the difference?
3. Could success strategies from one habit help the other?
4. Any correlation between these habits?

Provide specific, data-driven insights.""",
    input_variables=[
        "habit_a_name", "habit_a_rate", "habit_a_streak", "habit_a_notes",
        "habit_b_name", "habit_b_rate", "habit_b_streak", "habit_b_notes"
    ],
    description="Compare two habits to find patterns and improvement opportunities"
)

# ============================================================================
# GOAL-RELATED TEMPLATES
# ============================================================================

GOAL_PROGRESS_TEMPLATE = PromptTemplate(
    name="goal_progress",
    template="""Analyze goal progress and provide recommendations:

## Goal Details
- Name: {goal_name}
- Description: {goal_description}
- Target: {target}
- Current Progress: {current}
- Progress Percentage: {progress_pct}%
- Deadline: {deadline}
- Days Remaining: {days_remaining}

## Recent Activities
{recent_activities}

## Related Habits
{related_habits}

## Analysis Required
1. **Progress Assessment**: Is this goal on track? Calculate required daily progress.

2. **Potential Blockers**: What might prevent achieving this goal?

3. **Action Items**: What specific actions should be taken?

4. **Habit Alignment**: How do the related habits support this goal?

5. **Realistic Outlook**: What's the likelihood of achieving this goal by the deadline?

Be honest but encouraging in your assessment.""",
    input_variables=[
        "goal_name", "goal_description", "target", "current",
        "progress_pct", "deadline", "days_remaining",
        "recent_activities", "related_habits"
    ],
    description="Analyze goal progress and suggest actions to stay on track"
)

# ============================================================================
# WEEKLY SUMMARY TEMPLATES
# ============================================================================

WEEKLY_SUMMARY_TEMPLATE = PromptTemplate(
    name="weekly_summary",
    template="""Generate a comprehensive weekly summary for Veryfyn:

## Week: {week_start} to {week_end}

### Habit Performance
{habit_summary}

### Goal Progress
{goal_summary}

### Health & Wellness
{health_summary}

### Key Metrics
- Habits Completed: {habits_completed}/{habits_total}
- Goals On Track: {goals_on_track}/{goals_total}
- Average Mood: {avg_mood}
- Sleep Average: {avg_sleep} hours

### Notable Events
{notable_events}

Generate a summary with:
1. **Week Highlights**: Top 3 achievements or positive moments
2. **Areas for Improvement**: 1-2 areas that need attention
3. **Next Week Focus**: Suggested priorities

Keep it encouraging and actionable.""",
    input_variables=[
        "week_start", "week_end", "habit_summary", "goal_summary",
        "health_summary", "habits_completed", "habits_total",
        "goals_on_track", "goals_total", "avg_mood", "avg_sleep",
        "notable_events"
    ],
    description="Generate a comprehensive weekly summary"
)

# ============================================================================
# CORRELATION & PATTERN TEMPLATES
# ============================================================================

CORRELATION_TEMPLATE = PromptTemplate(
    name="correlation_analysis",
    template="""Find correlations and patterns in this user data:

## Time Period: {time_period}

### Data Points
{data_points}

### Analysis Tasks
1. **Correlations**: Are there relationships between different metrics?
   - Sleep vs Mood
   - Exercise vs Energy
   - Habit completion vs Productivity

2. **Patterns**: What recurring patterns appear?
   - Day of week effects
   - Time-based patterns
   - Sequential patterns (one habit affecting another)

3. **Anomalies**: Any unusual data points or outliers?

4. **Recommendations**: Based on correlations, what should the user focus on?

Provide specific, data-backed insights. Use numbers where possible.""",
    input_variables=["time_period", "data_points"],
    description="Analyze data to find correlations between behaviors"
)

# ============================================================================
# INTERVENTION TEMPLATES
# ============================================================================

INTERVENTION_TEMPLATE = PromptTemplate(
    name="coaching_intervention",
    template="""Create a personalized coaching intervention:

## Situation
{situation}

## User Context
- Name: {user_name}
- Primary Goals: {primary_goals}
- Recent Progress: {recent_progress}
- Coach Personality: {personality}

## Intervention Type: {intervention_type}
(celebration | encouragement | course_correction | check_in)

## Guidelines for Response
1. **Tone**: Match the specified personality
2. **Length**: Keep it concise (2-3 sentences max)
3. **Action**: Include one specific, doable next step
4. **Personal**: Reference their specific data or goals

Generate the intervention message now:""",
    input_variables=[
        "situation", "user_name", "primary_goals", "recent_progress",
        "personality", "intervention_type"
    ],
    description="Generate a personalized coaching intervention message"
)

STREAK_CELEBRATION_TEMPLATE = PromptTemplate(
    name="streak_celebration",
    template="""Create a celebration message for a streak achievement:

## Achievement
- Habit: {habit_name}
- Streak: {streak} days!
- Previous Best: {previous_best} days
- Is this a new record? {is_record}

## User Preferences
- Celebration Style: {celebration_style}
- Personality: {personality}

## Message Guidelines
1. Be genuinely enthusiastic
2. Acknowledge the effort behind the streak
3. If new record, emphasize the achievement
4. End with encouragement to continue

Generate a celebration message that will make the user feel proud:""",
    input_variables=[
        "habit_name", "streak", "previous_best", "is_record",
        "celebration_style", "personality"
    ],
    description="Generate a celebration message for streak achievements"
)

# ============================================================================
# INSIGHT GENERATION TEMPLATES
# ============================================================================

DAILY_INSIGHT_TEMPLATE = PromptTemplate(
    name="daily_insight",
    template="""Generate a daily insight based on today's data:

## Today's Data
- Date: {date}
- Habits Completed: {habits_completed}/{habits_total}
- Mood: {mood}
- Sleep: {sleep_hours} hours
- Energy Level: {energy}
- Notes: {notes}

## Generate
1. **One Key Insight**: What stands out from today's data?

2. **Tomorrow's Focus**: What should the user focus on tomorrow?

3. **Encouragement**: A brief, personalized encouraging note.

Keep it brief - this is a quick daily check-in, not a deep analysis.""",
    input_variables=[
        "date", "habits_completed", "habits_total", "mood",
        "sleep_hours", "energy", "notes"
    ],
    description="Generate a quick daily insight"
)

BEHAVIORAL_PATTERN_TEMPLATE = PromptTemplate(
    name="behavioral_pattern",
    template="""Identify behavioral patterns from this data:

## User: {user_name}
## Analysis Period: {period}

### Data Summary
{data_summary}

### Pattern Detection Tasks
1. **Time Patterns**: When is the user most productive?
2. **Day Patterns**: Which days are best/worst for habits?
3. **Sequence Patterns**: Does completing one habit lead to others?
4. **Energy Patterns**: What affects the user's energy levels?
5. **Mood Patterns**: What correlates with better mood?

### Output Format
For each pattern detected:
- **Pattern**: [Description]
- **Evidence**: [Data points that support it]
- **Confidence**: [High/Medium/Low]
- **Actionable Insight**: [What to do with this knowledge]

Focus on patterns that can help the user improve.""",
    input_variables=["user_name", "period", "data_summary"],
    description="Identify deep behavioral patterns from aggregated data"
)


# ============================================================================
# EXPORT ALL TEMPLATES
# ============================================================================

ALL_TEMPLATES = {
    "habit_insight": HABIT_INSIGHT_TEMPLATE,
    "habit_comparison": HABIT_COMPARISON_TEMPLATE,
    "goal_progress": GOAL_PROGRESS_TEMPLATE,
    "weekly_summary": WEEKLY_SUMMARY_TEMPLATE,
    "correlation_analysis": CORRELATION_TEMPLATE,
    "coaching_intervention": INTERVENTION_TEMPLATE,
    "streak_celebration": STREAK_CELEBRATION_TEMPLATE,
    "daily_insight": DAILY_INSIGHT_TEMPLATE,
    "behavioral_pattern": BEHAVIORAL_PATTERN_TEMPLATE,
}


def get_template(name: str) -> Optional[PromptTemplate]:
    """
    Get a template by name.
    
    Args:
        name: Template identifier
        
    Returns:
        PromptTemplate if found, None otherwise
    """
    return ALL_TEMPLATES.get(name)


def list_templates() -> List[str]:
    """
    List all available template names.
    
    Returns:
        List of template identifiers
    """
    return list(ALL_TEMPLATES.keys())