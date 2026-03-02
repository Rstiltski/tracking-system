"""
Helper functions for the Habit Experiments page.

Contains data retrieval and experiment processing functions.
"""

from typing import Dict, Any, List, Optional
from datetime import date


def get_habit_options(storage) -> Dict[str, str]:
    """
    Get habit options for selection dropdown.
    
    Args:
        storage: Storage instance
        
    Returns:
        Dictionary mapping habit display names to IDs
    """
    habits = storage.get_habits(include_archived=False)
    return {
        f"{h.icon if hasattr(h, 'icon') else '🎯'} {h.name}": h.id
        for h in habits
    }


def calculate_experiment_progress(start_date: date, duration_days: int) -> float:
    """
    Calculate experiment progress as a percentage.
    
    Args:
        start_date: Experiment start date
        duration_days: Total duration in days
        
    Returns:
        Progress as a float between 0 and 1
    """
    days_running = (date.today() - start_date).days
    return min(1.0, days_running / duration_days)


def get_days_running(start_date: date) -> int:
    """
    Get number of days an experiment has been running.
    
    Args:
        start_date: Experiment start date
        
    Returns:
        Number of days running
    """
    return (date.today() - start_date).days


def determine_winner(results: Dict[str, Any]) -> str:
    """
    Determine the winning variant from results.
    
    Args:
        results: Dictionary with variant rates
        
    Returns:
        Winner string ("A", "B", or "Tie")
    """
    if not results:
        return "No data"
    
    a_rate = results.get("variant_a_rate", 0)
    b_rate = results.get("variant_b_rate", 0)
    
    if b_rate > a_rate:
        return "B"
    elif a_rate > b_rate:
        return "A"
    else:
        return "Tie"


def format_rate_as_percentage(rate: float) -> str:
    """
    Format a rate as a percentage string.
    
    Args:
        rate: Rate as a float between 0 and 1
        
    Returns:
        Formatted percentage string
    """
    return f"{rate * 100:.0f}%"