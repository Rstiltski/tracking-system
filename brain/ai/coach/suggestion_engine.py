"""
Brain AI Coach - Suggestion Engine

Generates actionable suggestions based on intervention types and user state.
Provides contextual, personalized recommendations.

Usage:
    from brain.ai.coach.suggestion_engine import SuggestionEngine
    
    engine = SuggestionEngine()
    suggestions = engine.generate(intervention_type, user_state)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import random

from brain.ai.coach.rules import InterventionType
from brain.ai.coach.personality import PersonalityConfig, CoachPersonality


@dataclass
class Suggestion:
    """
    A coaching suggestion.
    
    Attributes:
        title: Short title
        message: Full suggestion message
        action_type: Type of action (rest, adjust, celebrate, etc.)
        priority: Suggestion priority
        actionable: Whether this requires user action
        action_text: Text for action button (if applicable)
        action_data: Data for action execution
    """
    title: str
    message: str
    action_type: str
    priority: int = 3
    actionable: bool = False
    action_text: Optional[str] = None
    action_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "message": self.message,
            "action_type": self.action_type,
            "priority": self.priority,
            "actionable": self.actionable,
            "action_text": self.action_text,
            "action_data": self.action_data
        }


# Suggestion templates by intervention type
SUGGESTION_TEMPLATES = {
    InterventionType.BURNOUT_WARNING: {
        "critical": [
            {
                "title": "🚨 Critical: Take a Break",
                "message": "Your burnout risk is very high. Please consider taking immediate rest. Your health comes first.",
                "action_type": "rest",
                "priority": 1,
                "actionable": True,
                "action_text": "Activate Recovery Mode"
            },
            {
                "title": "⚠️ Urgent: Reduce Your Load",
                "message": "Your metrics indicate significant stress. Consider pausing non-essential habits for today.",
                "action_type": "reduce_load",
                "priority": 1,
                "actionable": True,
                "action_text": "Pause Optional Habits"
            }
        ],
        "high": [
            {
                "title": "😰 High Stress Detected",
                "message": "Your burnout risk is elevated. Consider taking it easy today and prioritizing rest.",
                "action_type": "rest",
                "priority": 2,
                "actionable": True,
                "action_text": "See Recovery Tips"
            }
        ],
        "moderate": [
            {
                "title": "💪 Monitor Your Energy",
                "message": "You're showing some signs of strain. Remember to take breaks and stay hydrated.",
                "action_type": "self_care",
                "priority": 3
            }
        ]
    },
    
    InterventionType.STREAK_BREAK: [
        {
            "title": "💔 Streak Broken",
            "message": "A habit streak ended. That's okay - progress isn't always linear. Let's start a new one!",
            "action_type": "encouragement",
            "priority": 3,
            "actionable": True,
            "action_text": "Start Fresh"
        },
        {
            "title": "🌱 New Beginning",
            "message": "Every day is a chance to start again. Don't let one slip define your journey.",
            "action_type": "encouragement",
            "priority": 3
        },
        {
            "title": "💪 Keep Going",
            "message": "Missing a day doesn't erase your progress. Your past streaks prove you can do this!",
            "action_type": "encouragement",
            "priority": 3
        }
    ],
    
    InterventionType.STREAK_CELEBRATION: {
        7: [
            {
                "title": "🎉 One Week Strong!",
                "message": "You've maintained a 7-day streak! The first week is the hardest - you're building momentum!",
                "action_type": "celebrate",
                "priority": 4
            }
        ],
        21: [
            {
                "title": "🏆 Habit Formed!",
                "message": "21 days! Research suggests this habit is becoming automatic. Keep up the amazing work!",
                "action_type": "celebrate",
                "priority": 3
            }
        ],
        30: [
            {
                "title": "🌟 Monthly Champion!",
                "message": "30 days of consistency! This habit is now part of who you are. Incredible dedication!",
                "action_type": "celebrate",
                "priority": 2
            }
        ],
        100: [
            {
                "title": "👑 Legendary Status!",
                "message": "100 DAYS! You've achieved something most people never do. You're an inspiration!",
                "action_type": "celebrate",
                "priority": 1
            }
        ]
    },
    
    InterventionType.MILESTONE_APPROACH: [
        {
            "title": "🎯 Almost There!",
            "message": "You're close to completing a goal! Just a little more effort to reach the finish line.",
            "action_type": "motivate",
            "priority": 3,
            "actionable": True,
            "action_text": "View Goal"
        }
    ],
    
    InterventionType.MILESTONE_CELEBRATION: [
        {
            "title": "🎊 Goal Achieved!",
            "message": "Congratulations! You've completed a goal. Take a moment to celebrate your success!",
            "action_type": "celebrate",
            "priority": 2,
            "actionable": True,
            "action_text": "Set New Goal"
        }
    ],
    
    InterventionType.IMPROVEMENT_ENCOURAGEMENT: [
        {
            "title": "📈 Getting Better!",
            "message": "Your trends are improving! Keep doing what you're doing - it's working!",
            "action_type": "positive_reinforcement",
            "priority": 4
        },
        {
            "title": "✨ Progress Detected",
            "message": "Your consistency is paying off. Your metrics are trending in the right direction!",
            "action_type": "positive_reinforcement",
            "priority": 4
        }
    ],
    
    InterventionType.LOW_ENGAGEMENT: [
        {
            "title": "👋 Missing You!",
            "message": "We noticed you haven't been around lately. Your habits are waiting for you when you're ready.",
            "action_type": "reengage",
            "priority": 3,
            "actionable": True,
            "action_text": "View Today's Habits"
        },
        {
            "title": "🌱 Time to Check In",
            "message": "A quick check-in can help maintain your progress. Even small actions count!",
            "action_type": "reengage",
            "priority": 3
        }
    ],
    
    InterventionType.RECOVERY_SUGGESTION: [
        {
            "title": "😴 Prioritize Sleep",
            "message": "Good sleep is the foundation of health. Try to get 7-8 hours tonight.",
            "action_type": "rest",
            "priority": 2
        },
        {
            "title": "🧘 Take a Breath",
            "message": "Consider a short meditation or breathing exercise to reset your mind.",
            "action_type": "self_care",
            "priority": 3
        },
        {
            "title": "🚶 Step Outside",
            "message": "A brief walk can help clear your mind and boost your energy.",
            "action_type": "self_care",
            "priority": 3
        }
    ],
    
    InterventionType.HABIT_REMINDER: [
        {
            "title": "⏰ Habit Check",
            "message": "Some habits could use your attention today. Even 5 minutes counts!",
            "action_type": "reminder",
            "priority": 3,
            "actionable": True,
            "action_text": "View Habits"
        }
    ],
    
    InterventionType.DAILY_CHECK_IN: [
        {
            "title": "☀️ Good Morning!",
            "message": "Ready to make today count? Check in on your habits and start your day right.",
            "action_type": "check_in",
            "priority": 4,
            "actionable": True,
            "action_text": "Start Today"
        },
        {
            "title": "🌙 Evening Check",
            "message": "How did today go? Take a moment to log your progress before bed.",
            "action_type": "check_in",
            "priority": 4
        }
    ],
    
    InterventionType.GOAL_DEADLINE_WARNING: [
        {
            "title": "⏳ Deadline Approaching",
            "message": "A goal deadline is coming up. Review your progress and adjust if needed.",
            "action_type": "reminder",
            "priority": 2,
            "actionable": True,
            "action_text": "View Goal"
        }
    ],
    
    InterventionType.PATTERN_DETECTED: [
        {
            "title": "🔍 Pattern Found",
            "message": "We noticed a pattern in your data. Understanding it might help improve your routine.",
            "action_type": "insight",
            "priority": 4,
            "actionable": True,
            "action_text": "View Insight"
        }
    ]
}


class SuggestionEngine:
    """
    Generates actionable suggestions based on intervention types.
    
    Features:
    - Template-based suggestions
    - Personality-aware formatting
    - Context-aware selection
    - Actionable recommendations
    
    Usage:
        engine = SuggestionEngine(personality_config)
        suggestion = engine.generate(InterventionType.BURNOUT_WARNING, user_state)
    """
    
    def __init__(self, personality: Optional[PersonalityConfig] = None):
        """
        Initialize the suggestion engine.
        
        Args:
            personality: Coach personality configuration
        """
        self.personality = personality or PersonalityConfig()
    
    def generate(
        self, 
        intervention_type: InterventionType, 
        user_state: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Suggestion:
        """
        Generate a suggestion for the given intervention type.
        
        Args:
            intervention_type: Type of intervention
            user_state: Current user state
            context: Additional context (e.g., streak days, goal progress)
            
        Returns:
            Suggestion instance
        """
        templates = SUGGESTION_TEMPLATES.get(intervention_type, [])
        template = self._select_template(templates, user_state, context)
        
        if not template:
            # Default suggestion
            template = {
                "title": "💡 Coach Note",
                "message": "Just checking in on your progress. Keep up the good work!",
                "action_type": "check_in",
                "priority": 4
            }
        
        # Apply personality formatting
        message = self._apply_personality(template["message"])
        
        return Suggestion(
            title=template.get("title", "Suggestion"),
            message=message,
            action_type=template.get("action_type", "general"),
            priority=template.get("priority", 3),
            actionable=template.get("actionable", False),
            action_text=template.get("action_text"),
            action_data=template.get("action_data", {})
        )
    
    def generate_multiple(
        self, 
        intervention_type: InterventionType,
        user_state: Dict[str, Any],
        count: int = 3
    ) -> List[Suggestion]:
        """
        Generate multiple suggestions for variety.
        
        Args:
            intervention_type: Type of intervention
            user_state: Current user state
            count: Number of suggestions
            
        Returns:
            List of suggestions
        """
        templates = SUGGESTION_TEMPLATES.get(intervention_type, [])
        
        if isinstance(templates, dict):
            # Nested structure (e.g., burnout levels)
            all_templates = []
            for level_templates in templates.values():
                if isinstance(level_templates, list):
                    all_templates.extend(level_templates)
            templates = all_templates
        
        if not templates:
            return [self.generate(intervention_type, user_state)]
        
        # Select multiple templates
        selected = random.sample(templates, min(count, len(templates)))
        
        suggestions = []
        for template in selected:
            message = self._apply_personality(template.get("message", ""))
            suggestions.append(Suggestion(
                title=template.get("title", "Suggestion"),
                message=message,
                action_type=template.get("action_type", "general"),
                priority=template.get("priority", 3),
                actionable=template.get("actionable", False),
                action_text=template.get("action_text"),
                action_data=template.get("action_data", {})
            ))
        
        return suggestions
    
    def _select_template(
        self, 
        templates: Any, 
        user_state: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Select the most appropriate template."""
        context = context or {}
        
        if isinstance(templates, dict):
            # Nested structure - select based on context
            if "burnout_risk" in user_state:
                risk = user_state["burnout_risk"]
                if risk >= 71:
                    return random.choice(templates.get("critical", [None]))
                elif risk >= 51:
                    return random.choice(templates.get("high", [None]))
                elif risk >= 31:
                    return random.choice(templates.get("moderate", [None]))
            
            # Check for streak milestone
            if "streak_days" in context:
                days = context["streak_days"]
                if days in templates:
                    return random.choice(templates[days])
            
            # Default to first available
            for value in templates.values():
                if isinstance(value, list) and value:
                    return random.choice(value)
        
        elif isinstance(templates, list) and templates:
            return random.choice(templates)
        
        return None
    
    def _apply_personality(self, message: str) -> str:
        """Apply personality modifications to message."""
        if not self.personality.use_emojis:
            # Remove emojis (simple approach)
            import re
            message = re.sub(r'[^\x00-\x7F]+', '', message).strip()
        
        # Apply tone modifications
        if self.personality.personality == CoachPersonality.DIRECT:
            # Make more concise
            sentences = message.split('. ')
            if len(sentences) > 2:
                message = '. '.join(sentences[:2])
        
        elif self.personality.personality == CoachPersonality.GENTLE:
            # Add softer language
            if message.endswith('!'):
                message = message[:-1] + '.'
        
        return message
    
    def get_recovery_suggestions(self, user_state: Dict[str, Any]) -> List[Suggestion]:
        """
        Get suggestions for recovery mode.
        
        Args:
            user_state: Current user state
            
        Returns:
            List of recovery-focused suggestions
        """
        suggestions = []
        
        # Sleep suggestion
        if user_state.get("sleep_trend") == "declining":
            suggestions.append(Suggestion(
                title="😴 Focus on Sleep",
                message="Your sleep has been declining. Consider setting an earlier bedtime tonight.",
                action_type="rest",
                priority=2,
                actionable=True,
                action_text="Set Bedtime Reminder"
            ))
        
        # Mood suggestion
        if user_state.get("mood_trend") == "declining":
            suggestions.append(Suggestion(
                title="💭 Check In With Yourself",
                message="Your mood has been lower lately. Consider journaling or talking to someone.",
                action_type="self_care",
                priority=3
            ))
        
        # General rest suggestion
        suggestions.append(Suggestion(
            title="🧘 Recovery Day",
            message="Consider making today a lighter day. It's okay to reduce your targets temporarily.",
            action_type="rest",
            priority=2,
            actionable=True,
            action_text="Reduce Today's Targets"
        ))
        
        return suggestions