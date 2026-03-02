"""
Helper functions for the Template Sharing page.
"""

from typing import List, Any, Optional
from datetime import datetime

from .constants import (
    ALL_CATEGORIES,
    SEARCH_PLACEHOLDER,
)


def filter_templates_by_search(
    templates: List[Any],
    search: str
) -> List[Any]:
    """
    Filter templates by search query.
    
    Args:
        templates: List of template objects
        search: Search query string
        
    Returns:
        Filtered list of templates
    """
    if not search:
        return templates
    return [t for t in templates if search.lower() in t.name.lower()]


def filter_templates_by_category(
    templates: List[Any],
    category: str
) -> List[Any]:
    """
    Filter templates by category.
    
    Args:
        templates: List of template objects
        category: Category to filter by
        
    Returns:
        Filtered list of templates
    """
    if category == ALL_CATEGORIES:
        return templates
    return [t for t in templates if t.category.value == category]


def get_template_options(templates: List[Any]) -> dict:
    """
    Get template options as a dictionary for selectbox.
    
    Args:
        templates: List of template objects
        
    Returns:
        Dictionary mapping template names to template objects
    """
    return {t.name: t for t in templates}


def format_template_header(template: Any) -> str:
    """
    Format template header for display.
    
    Args:
        template: Template object
        
    Returns:
        Formatted header string
    """
    return f"**{template.name}** - {template.difficulty.value.title()} ({template.total_duration} min)"


def format_habit_list(habits: List[Any]) -> List[str]:
    """
    Format habits as a numbered list.
    
    Args:
        habits: List of habit objects
        
    Returns:
        List of formatted habit strings
    """
    return [f"{i}. {habit.icon} {habit.name} ({habit.duration_minutes} min)" 
            for i, habit in enumerate(habits, 1)]


def create_mock_shared_template(
    template_id: str,
    title: str,
    description: str,
    user_id: str,
    is_public: bool = True
) -> dict:
    """
    Create a mock shared template dictionary.
    
    Args:
        template_id: Template ID
        title: Template title
        description: Template description
        user_id: User ID who shared it
        is_public: Whether it's public
        
    Returns:
        Dictionary representing a shared template
    """
    return {
        'id': f"shared-{template_id}",
        'template_id': template_id,
        'title': title,
        'description': description,
        'user_id': user_id,
        'is_public': is_public,
        'created_at': datetime.now().isoformat(),
        'clones_count': 0,
    }