"""
Habit Template Manager - Apply and manage habit templates.

This manager handles:
- Template browsing and search
- Template application (creating habits from templates)
- Custom template creation
- Usage tracking

Usage:
    from brain.behavioral.template_manager import TemplateManager
    
    manager = TemplateManager(storage, user_id)
    template = manager.get_template("template_morning_beginner")
    manager.apply_template(template.id)
"""
from typing import List, Dict, Any, Optional
import logging

from brain.models.habit_template import (
    HabitTemplate,
    TemplateHabit,
    TemplateCategory,
    TemplateDifficulty,
    DEFAULT_TEMPLATES,
    search_templates,
    get_templates_by_category,
    get_templates_by_difficulty,
)

logger = logging.getLogger(__name__)


class TemplateManager:
    """
    Manages habit templates and template application.

    Usage:
        manager = TemplateManager(storage, user_id)
        templates = manager.get_all_templates()
        manager.apply_template(template_id)
    """

    def __init__(self, storage: Any, user_id: str = ""):
        """
        Initialize template manager.

        Args:
            storage: Storage instance
            user_id: User ID
        """
        self.storage = storage
        self.user_id = user_id

    def get_all_templates(self) -> List[HabitTemplate]:
        """
        Get all available templates.

        Returns:
            List of all templates
        """
        # Return default templates
        # In future, could also include user-created templates
        return DEFAULT_TEMPLATES.copy()

    def get_template(self, template_id: str) -> Optional[HabitTemplate]:
        """
        Get a specific template by ID.

        Args:
            template_id: Template ID

        Returns:
            Template or None if not found
        """
        templates = self.get_all_templates()
        for template in templates:
            if template.id == template_id:
                return template
        return None

    def search_templates(self, query: str) -> List[HabitTemplate]:
        """
        Search templates by name, description, or tags.

        Args:
            query: Search query

        Returns:
            List of matching templates
        """
        return search_templates(query)

    def get_templates_by_category(
        self,
        category: TemplateCategory
    ) -> List[HabitTemplate]:
        """
        Get templates by category.

        Args:
            category: Category to filter by

        Returns:
            List of templates in category
        """
        return get_templates_by_category(category)

    def get_templates_by_difficulty(
        self,
        difficulty: TemplateDifficulty
    ) -> List[HabitTemplate]:
        """
        Get templates by difficulty.

        Args:
            difficulty: Difficulty level

        Returns:
            List of templates at difficulty level
        """
        return get_templates_by_difficulty(difficulty)

    def apply_template(
        self,
        template_id: str,
        customize: bool = False
    ) -> Dict[str, Any]:
        """
        Apply a template to create habits.

        Args:
            template_id: ID of template to apply
            customize: Whether to allow customization

        Returns:
            Result dict with created habits and status
        """
        template = self.get_template(template_id)

        if not template:
            return {
                "success": False,
                "error": "Template not found",
                "habits_created": 0
            }

        try:
            created_habits = []

            # Create each habit from template
            for template_habit in template.habits:
                habit = self.storage.create_habit(
                    name=template_habit.name,
                    description=template_habit.description,
                    frequency=template_habit.frequency,
                    icon=template_habit.icon,
                    color=template_habit.color,
                    habit_type=template_habit.habit_type,
                    target_value=template_habit.target_value,
                    target_type=template_habit.target_type
                )
                created_habits.append({
                    "id": habit.id,
                    "name": habit.name,
                    "icon": habit.icon
                })

            # Update template usage count
            self._increment_template_usage(template_id)

            logger.info(
                f"Applied template '{template.name}' for user {self.user_id}: "
                f"created {len(created_habits)} habits"
            )

            return {
                "success": True,
                "template_name": template.name,
                "habits_created": len(created_habits),
                "habits": created_habits,
                "total_duration": template.total_duration
            }

        except Exception as e:
            logger.error(f"Failed to apply template: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "habits_created": 0
            }

    def _increment_template_usage(self, template_id: str) -> None:
        """
        Increment template usage count.

        Args:
            template_id: Template ID
        """
        # In future, could store this in database
        # For now, just log it
        logger.info(f"Template {template_id} usage incremented")

    def create_custom_template(
        self,
        name: str,
        description: str,
        habit_ids: List[str],
        category: TemplateCategory = TemplateCategory.CUSTOM,
        difficulty: TemplateDifficulty = TemplateDifficulty.BEGINNER
    ) -> Optional[HabitTemplate]:
        """
        Create a custom template from existing habits.

        Args:
            name: Template name
            description: Template description
            habit_ids: IDs of habits to include
            category: Template category
            difficulty: Difficulty level

        Returns:
            Created template or None
        """
        try:
            habits = []

            # Get each habit and convert to template habit
            for i, habit_id in enumerate(habit_ids):
                habit = self.storage.get_habit(habit_id)
                if habit:
                    template_habit = TemplateHabit(
                        name=habit.name,
                        description=habit.description or "",
                        icon=habit.icon if hasattr(habit, 'icon') else "🎯",
                        color=habit.color if hasattr(habit, 'color') else "#6366f1",
                        frequency=habit.frequency if hasattr(habit, 'frequency') else "daily",
                        position=i,
                        duration_minutes=5  # Default estimate
                    )
                    habits.append(template_habit)

            if not habits:
                return None

            # Create template
            template = HabitTemplate(
                name=name,
                description=description,
                category=category,
                difficulty=difficulty,
                habits=habits,
                author=self.user_id or "User",
                is_public=False  # Custom templates are private by default
            )

            # In future, save to database
            # For now, just return it
            logger.info(f"Created custom template '{name}' with {len(habits)} habits")

            return template

        except Exception as e:
            logger.error(f"Failed to create custom template: {str(e)}")
            return None

    def get_recommended_templates(self, limit: int = 5) -> List[HabitTemplate]:
        """
        Get recommended templates for the user.

        Based on user's current habits and patterns.

        Args:
            limit: Maximum number of recommendations

        Returns:
            List of recommended templates
        """
        # Get user's current habits
        habits = self.storage.get_habits(include_archived=False)

        if not habits:
            # New user - recommend beginner templates
            return [
                t for t in DEFAULT_TEMPLATES
                if t.difficulty == TemplateDifficulty.BEGINNER
            ][:limit]

        # Analyze user's habits
        habit_count = len(habits)
        categories_used = set()

        for habit in habits:
            if hasattr(habit, 'category'):
                categories_used.add(habit.category)

        # Recommend based on gaps
        recommendations = []

        # If user has few habits, recommend beginner templates
        if habit_count < 3:
            recommendations.extend([
                t for t in DEFAULT_TEMPLATES
                if t.difficulty == TemplateDifficulty.BEGINNER
            ])

        # If user has morning habits but no evening, recommend evening
        if "morning" in str(categories_used).lower():
            evening_templates = [
                t for t in DEFAULT_TEMPLATES
                if t.category == TemplateCategory.EVENING
            ]
            recommendations.extend(evening_templates)

        # Remove duplicates and return
        seen_ids = set()
        unique_recommendations = []
        for template in recommendations:
            if template.id not in seen_ids:
                seen_ids.add(template.id)
                unique_recommendations.append(template)

        return unique_recommendations[:limit]

    def get_template_preview(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a preview of a template.

        Args:
            template_id: Template ID

        Returns:
            Preview dict or None
        """
        template = self.get_template(template_id)

        if not template:
            return None

        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "category": template.category.value,
            "difficulty": template.difficulty.value,
            "habit_count": len(template.habits),
            "total_duration": template.total_duration,
            "habits": [
                {
                    "name": h.name,
                    "icon": h.icon,
                    "duration": h.duration_minutes
                }
                for h in template.habits
            ],
            "tags": template.tags
        }


__all__ = [
    "TemplateManager",
]
