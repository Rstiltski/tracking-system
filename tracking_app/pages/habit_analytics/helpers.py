"""
Helper functions for the Habit Analytics page.

Contains data retrieval and processing functions.
"""

from typing import Dict, Any, List, Optional


def get_heatmap_data(heatmap_gen, year: int) -> Dict[str, Any]:
    """
    Get heatmap data for a specific year.
    
    Args:
        heatmap_gen: HeatmapGenerator instance
        year: Year to generate heatmap for
        
    Returns:
        Dictionary with heatmap data
    """
    return heatmap_gen.generate_heatmap(year)


def get_correlation_data(correlation_analyzer) -> List[Dict[str, Any]]:
    """
    Get habit correlation data.
    
    Args:
        correlation_analyzer: CorrelationAnalyzer instance
        
    Returns:
        List of correlation dictionaries
    """
    return correlation_analyzer.calculate_habit_correlations()


def get_day_patterns(correlation_analyzer) -> Dict[str, float]:
    """
    Get day of week completion patterns.
    
    Args:
        correlation_analyzer: CorrelationAnalyzer instance
        
    Returns:
        Dictionary mapping day names to completion rates
    """
    return correlation_analyzer.get_day_of_week_patterns()


def get_summary_stats(heatmap_gen) -> Dict[str, Any]:
    """
    Get summary statistics for the analytics dashboard.
    
    Args:
        heatmap_gen: HeatmapGenerator instance
        
    Returns:
        Dictionary with summary statistics
    """
    return heatmap_gen.get_summary_stats()


def prepare_chart_data(contributions: Dict[str, int]) -> "pandas.DataFrame":
    """
    Prepare contribution data for chart display.
    
    Args:
        contributions: Dictionary mapping dates to contribution counts
        
    Returns:
        pandas DataFrame suitable for charting
    """
    import pandas as pd
    
    dates = list(contributions.keys())
    values = list(contributions.values())
    
    df = pd.DataFrame({
        "Date": pd.to_datetime(dates),
        "Contributions": values
    })
    df = df.set_index("Date")
    
    return df


def calculate_best_worst_days(patterns: Dict[str, float]) -> tuple:
    """
    Calculate best and worst days from patterns.
    
    Args:
        patterns: Dictionary mapping day names to completion rates
        
    Returns:
        Tuple of (best_day, worst_day)
    """
    if not patterns:
        return None, None
    
    best_day = max(patterns, key=patterns.get)
    worst_day = min(patterns, key=patterns.get)
    
    return best_day, worst_day