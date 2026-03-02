"""
Helper functions for the Stacks page.
"""

from typing import List, Dict, Any, Optional

from brain.behavioral.habit_stacking import (
    AnchorCategory,
    AnchorPreset,
    DEFAULT_ANCHOR_PRESETS,
)


def get_category_options() -> List[str]:
    """
    Get list of category options for filtering.
    
    Returns:
        List of category names with "All" as first option
    """
    return ["All"] + [c.value.title() for c in AnchorCategory]


def filter_presets_by_category(
    category: str
) -> List[AnchorPreset]:
    """
    Filter anchor presets by category.
    
    Args:
        category: Category name or "All"
        
    Returns:
        Filtered list of anchor presets
    """
    if category == "All":
        return DEFAULT_ANCHOR_PRESETS
    
    category_enum = AnchorCategory(category.lower())
    return [p for p in DEFAULT_ANCHOR_PRESETS if p.category == category_enum]


def get_anchor_options(presets: List[AnchorPreset], custom_option: str) -> List[str]:
    """
    Get list of anchor options for selectbox.
    
    Args:
        presets: List of anchor presets
        custom_option: Label for custom option
        
    Returns:
        List of anchor option names
    """
    return [custom_option] + [p.name for p in presets]


def get_preset_by_name(presets: List[AnchorPreset], name: str) -> Optional[AnchorPreset]:
    """
    Get preset by name.
    
    Args:
        presets: List of anchor presets
        name: Preset name to find
        
    Returns:
        AnchorPreset if found, None otherwise
    """
    for preset in presets:
        if preset.name == name:
            return preset
    return None


def format_stack_chain(items: list, habit_lookup: dict) -> str:
    """
    Format stack items as a chain string.
    
    Args:
        items: List of StackItem objects
        habit_lookup: Dictionary mapping habit IDs to habits
        
    Returns:
        Formatted chain string
    """
    chain_parts = []
    for item in sorted(items, key=lambda x: x.position_index):
        habit = habit_lookup.get(item.habit_id)
        if habit:
            tiny_indicator = "🌱 " if item.is_tiny else ""
            chain_parts.append(f"{item.position_index + 1}. {tiny_indicator}{habit.icon} {habit.name}")
    return "\n".join(chain_parts)