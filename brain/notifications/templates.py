"""
Notification Templates

Jinja2-based notification templates for personalized messages.
Supports template inheritance and context-aware rendering.

Reference:
- Phase 4.1 Research Document, Section 5.4: Notification Templates
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

# Try to import Jinja2, fall back to string formatting
try:
    from jinja2 import Template, Environment, FileSystemLoader, select_autoescape
    JINJA_AVAILABLE = True
except ImportError:
    JINJA_AVAILABLE = False
    logger.warning("Jinja2 not installed. Using basic string formatting.")


@dataclass
class NotificationTemplate:
    """
    A notification template with title and message patterns.
    
    Templates support variable substitution using {{ variable }} syntax.
    """
    id: str
    name: str
    title_template: str
    message_template: str
    description: str = ""
    category: str = "general"
    variables: List[str] = field(default_factory=list)
    
    def render(self, context: Dict[str, Any]) -> tuple:
        """
        Render the template with the given context.
        
        Args:
            context: Dictionary of variables to substitute
            
        Returns:
            Tuple of (title, message)
        """
        if JINJA_AVAILABLE:
            title = Template(self.title_template).render(**context)
            message = Template(self.message_template).render(**context)
        else:
            # Basic string formatting fallback
            title = self.title_template.format(**context)
            message = self.message_template.format(**context)
        
        return title, message


class NotificationTemplates:
    """
    Collection of notification templates for the tracking system.
    
    Provides pre-built templates for common notification types
    and allows custom template registration.
    """
    
    # Default templates for each notification type
    DEFAULT_TEMPLATES = {
        # Habit reminders
        "habit_reminder": NotificationTemplate(
            id="habit_reminder",
            name="Habit Reminder",
            title_template="⏰ Time for: {{ habit_name }}",
            message_template="Don't forget to {{ habit_action }}! You're on a {{ streak }} day streak. Keep it going! 🔥",
            description="Reminder to complete a habit",
            category="habits",
            variables=["habit_name", "habit_action", "streak"],
        ),
        
        "habit_reminder_smart": NotificationTemplate(
            id="habit_reminder_smart",
            name="Smart Habit Reminder",
            title_template="⏰ Usually you {{ habit_action }} around now",
            message_template="Based on your patterns, this is a great time for {{ habit_name }}. You've completed this {{ completion_rate }}% of the time!",
            description="Smart reminder based on user patterns",
            category="habits",
            variables=["habit_name", "habit_action", "completion_rate"],
        ),
        
        "habit_streak_warning": NotificationTemplate(
            id="habit_streak_warning",
            name="Streak Warning",
            title_template="⚠️ Your {{ streak }} day streak is at risk!",
            message_template="Complete {{ habit_name }} today to keep your streak alive. Don't let {{ streak }} days of hard work disappear!",
            description="Warning when streak is about to break",
            category="habits",
            variables=["habit_name", "streak"],
        ),
        
        "habit_streak_broken": NotificationTemplate(
            id="habit_streak_broken",
            name="Streak Broken",
            title_template="💔 Streak broken for {{ habit_name }}",
            message_template="Your {{ streak }} day streak has ended. But don't worry - every day is a new chance to start fresh! Start a new streak today.",
            description="Notification when streak is broken",
            category="habits",
            variables=["habit_name", "streak"],
        ),
        
        # Task reminders
        "task_due": NotificationTemplate(
            id="task_due",
            name="Task Due",
            title_template="📋 Task due: {{ task_title }}",
            message_template="Your task '{{ task_title }}' is due {{ due_time }}. Priority: {{ priority }}.",
            description="Reminder for upcoming task deadline",
            category="tasks",
            variables=["task_title", "due_time", "priority"],
        ),
        
        "task_overdue": NotificationTemplate(
            id="task_overdue",
            name="Task Overdue",
            title_template="🚨 Overdue: {{ task_title }}",
            message_template="This task was due {{ overdue_duration }} ago. Would you like to reschedule or complete it now?",
            description="Notification for overdue tasks",
            category="tasks",
            variables=["task_title", "overdue_duration"],
        ),
        
        # Goal notifications
        "goal_deadline": NotificationTemplate(
            id="goal_deadline",
            name="Goal Deadline",
            title_template="🎯 Goal deadline approaching: {{ goal_title }}",
            message_template="You're {{ progress }}% towards '{{ goal_title }}' with {{ days_remaining }} days left. You've got this!",
            description="Reminder for goal deadlines",
            category="goals",
            variables=["goal_title", "progress", "days_remaining"],
        ),
        
        "goal_achieved": NotificationTemplate(
            id="goal_achieved",
            name="Goal Achieved",
            title_template="🎉 Goal Achieved: {{ goal_title }}!",
            message_template="Congratulations! You've completed your goal '{{ goal_title }}'! All your hard work has paid off. +{{ xp_reward }} XP!",
            description="Celebration for achieving a goal",
            category="goals",
            variables=["goal_title", "xp_reward"],
        ),
        
        # Achievement notifications
        "achievement_unlocked": NotificationTemplate(
            id="achievement_unlocked",
            name="Achievement Unlocked",
            title_template="🏆 Achievement Unlocked: {{ achievement_name }}!",
            message_template="{{ achievement_description }}. You've earned {{ xp_reward }} XP! Keep up the amazing work.",
            description="Notification for new achievements",
            category="achievements",
            variables=["achievement_name", "achievement_description", "xp_reward"],
        ),
        
        "level_up": NotificationTemplate(
            id="level_up",
            name="Level Up",
            title_template="⭐ Level Up! You're now Level {{ new_level }}!",
            message_template="Congratulations on reaching Level {{ new_level }}! You've earned {{ total_xp }} total XP. New rewards may be available!",
            description="Notification for level increases",
            category="achievements",
            variables=["new_level", "total_xp"],
        ),
        
        # Reward notifications
        "reward_received": NotificationTemplate(
            id="reward_received",
            name="Reward Received",
            title_template="{{ reward_icon }} You got: {{ reward_name }}!",
            message_template="{{ reward_description }}. {{ rarity_text }}",
            description="Notification for variable rewards",
            category="rewards",
            variables=["reward_icon", "reward_name", "reward_description", "rarity_text"],
        ),
        
        # Daily digest
        "daily_digest": NotificationTemplate(
            id="daily_digest",
            name="Daily Digest",
            title_template="📊 Your Daily Summary for {{ date }}",
            message_template="Habits completed: {{ habits_completed }}/{{ habits_total }}. Tasks done: {{ tasks_done }}. Current streak: {{ best_streak }} days. {{ xp_earned }} XP earned today!",
            description="Daily summary notification",
            category="digest",
            variables=["date", "habits_completed", "habits_total", "tasks_done", "best_streak", "xp_earned"],
        ),
        
        # System notifications
        "system_update": NotificationTemplate(
            id="system_update",
            name="System Update",
            title_template="🔔 {{ title }}",
            message_template="{{ message }}",
            description="Generic system notification",
            category="system",
            variables=["title", "message"],
        ),
        
        # Habit stack notifications
        "habit_stack_next": NotificationTemplate(
            id="habit_stack_next",
            name="Habit Stack Next",
            title_template="🔗 Next in your {{ stack_name }} stack",
            message_template="Great job completing {{ previous_habit }}! Ready for {{ next_habit }}?",
            description="Notification for next habit in stack",
            category="habits",
            variables=["stack_name", "previous_habit", "next_habit"],
        ),
        
        # Implementation intention triggered
        "intention_triggered": NotificationTemplate(
            id="intention_triggered",
            name="Intention Triggered",
            title_template="🎯 {{ intention_name }}",
            message_template="{{ trigger_context }}. Time to {{ action }}!",
            description="Notification when implementation intention is triggered",
            category="intentions",
            variables=["intention_name", "trigger_context", "action"],
        ),
    }
    
    def __init__(self):
        """Initialize the template manager."""
        self._templates = dict(self.DEFAULT_TEMPLATES)
        self._custom_templates = {}
    
    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """
        Get a template by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            NotificationTemplate or None if not found
        """
        return self._templates.get(template_id) or self._custom_templates.get(template_id)
    
    def register_template(self, template: NotificationTemplate) -> None:
        """
        Register a custom template.
        
        Args:
            template: NotificationTemplate to register
        """
        self._custom_templates[template.id] = template
        logger.info(f"Registered custom template: {template.id}")
    
    def render(
        self, 
        template_id: str, 
        context: Dict[str, Any],
        fallback_to_default: bool = True
    ) -> tuple:
        """
        Render a template with the given context.
        
        Args:
            template_id: Template identifier
            context: Dictionary of variables to substitute
            fallback_to_default: If True, use default template if custom not found
            
        Returns:
            Tuple of (title, message) or (None, None) if template not found
        """
        template = self.get_template(template_id)
        
        if template is None:
            if fallback_to_default and template_id in self.DEFAULT_TEMPLATES:
                template = self.DEFAULT_TEMPLATES[template_id]
            else:
                logger.warning(f"Template not found: {template_id}")
                return None, None
        
        try:
            return template.render(context)
        except KeyError as e:
            logger.error(f"Missing variable in template {template_id}: {e}")
            # Return template with missing variable placeholder
            return template.title_template, f"Error: Missing variable {e}"
    
    def get_templates_by_category(self, category: str) -> List[NotificationTemplate]:
        """
        Get all templates in a category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of templates in the category
        """
        return [
            t for t in self._templates.values()
            if t.category == category
        ]
    
    def get_all_templates(self) -> List[NotificationTemplate]:
        """Get all available templates."""
        return list(self._templates.values()) + list(self._custom_templates.values())
    
    def get_template_variables(self, template_id: str) -> List[str]:
        """
        Get the variables required by a template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            List of variable names
        """
        template = self.get_template(template_id)
        return template.variables if template else []


# Convenience functions
def render_notification(
    template_id: str,
    context: Dict[str, Any]
) -> tuple:
    """
    Render a notification template.
    
    Args:
        template_id: Template identifier
        context: Dictionary of variables
        
    Returns:
        Tuple of (title, message)
    """
    templates = NotificationTemplates()
    return templates.render(template_id, context)


def get_habit_reminder_context(
    habit_name: str,
    habit_action: str = None,
    streak: int = 0,
    completion_rate: float = 0.0,
    is_smart: bool = False
) -> Dict[str, Any]:
    """
    Build context for habit reminder notifications.
    
    Args:
        habit_name: Name of the habit
        habit_action: Action description (defaults to habit_name)
        streak: Current streak count
        completion_rate: Historical completion rate
        is_smart: Whether this is a smart reminder
        
    Returns:
        Context dictionary for template rendering
    """
    return {
        "habit_name": habit_name,
        "habit_action": habit_action or habit_name.lower(),
        "streak": streak,
        "completion_rate": int(completion_rate * 100),
    }


def get_task_reminder_context(
    task_title: str,
    due_time: str,
    priority: str = "medium",
    overdue_duration: str = None
) -> Dict[str, Any]:
    """
    Build context for task reminder notifications.
    
    Args:
        task_title: Title of the task
        due_time: When the task is due
        priority: Task priority
        overdue_duration: How long overdue (if applicable)
        
    Returns:
        Context dictionary for template rendering
    """
    return {
        "task_title": task_title,
        "due_time": due_time,
        "priority": priority.capitalize(),
        "overdue_duration": overdue_duration,
    }


def get_achievement_context(
    achievement_name: str,
    achievement_description: str,
    xp_reward: int
) -> Dict[str, Any]:
    """
    Build context for achievement notifications.
    
    Args:
        achievement_name: Name of the achievement
        achievement_description: Description of the achievement
        xp_reward: XP earned
        
    Returns:
        Context dictionary for template rendering
    """
    return {
        "achievement_name": achievement_name,
        "achievement_description": achievement_description,
        "xp_reward": xp_reward,
    }


def get_reward_context(
    reward_name: str,
    reward_description: str,
    reward_icon: str,
    rarity: str
) -> Dict[str, Any]:
    """
    Build context for reward notifications.
    
    Args:
        reward_name: Name of the reward
        reward_description: Description of the reward
        reward_icon: Icon/emoji for the reward
        rarity: Rarity level (common, uncommon, rare, legendary)
        
    Returns:
        Context dictionary for template rendering
    """
    rarity_texts = {
        "common": "A common find!",
        "uncommon": "Nice! This one is uncommon.",
        "rare": "Wow! A rare reward!",
        "legendary": "INCREDIBLE! A legendary reward!",
    }
    
    return {
        "reward_name": reward_name,
        "reward_description": reward_description,
        "reward_icon": reward_icon,
        "rarity_text": rarity_texts.get(rarity, "A special reward!"),
    }