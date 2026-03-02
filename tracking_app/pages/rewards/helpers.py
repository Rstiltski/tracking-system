"""
Helper functions for the Rewards page.
"""

from typing import Optional

from brain.behavioral.rewards import Rarity, RewardType

from .constants import RARITY_EMOJIS, RARITY_COLORS, TYPE_EMOJIS


def get_rarity_emoji(rarity: Rarity) -> str:
    """
    Get emoji for rarity level.
    
    Args:
        rarity: The rarity level
        
    Returns:
        Emoji string for the rarity
    """
    return RARITY_EMOJIS.get(rarity.name, "⚪")


def get_rarity_color(rarity: Rarity) -> str:
    """
    Get color for rarity level.
    
    Args:
        rarity: The rarity level
        
    Returns:
        Hex color string for the rarity
    """
    return RARITY_COLORS.get(rarity.name, "#9CA3AF")


def get_type_emoji(reward_type: RewardType) -> str:
    """
    Get emoji for reward type.
    
    Args:
        reward_type: The reward type
        
    Returns:
        Emoji string for the type
    """
    return TYPE_EMOJIS.get(reward_type.name, "🎁")


def format_rarity_label(rarity: Rarity) -> str:
    """
    Format rarity for display.
    
    Args:
        rarity: The rarity level
        
    Returns:
        Formatted rarity label with emoji
    """
    emoji = get_rarity_emoji(rarity)
    return f"{emoji} {rarity.value.title()}"


def format_reward_label(reward) -> str:
    """
    Format reward for display.
    
    Args:
        reward: The reward object
        
    Returns:
        Formatted reward label
    """
    return f"{reward.icon} {reward.name}"


def calculate_total_xp_from_history(history) -> int:
    """
    Calculate total XP earned from reward history.
    
    Args:
        history: RewardHistory object
        
    Returns:
        Total XP value
    """
    total = 0
    for record in history.rewards_received:
        total += record.get('value', 0)
    return total