"""
Helper functions for the Insights page.

Contains data gathering and analysis functions.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Tuple

from tracking_app.storage import Storage
from tracking_app.models import Habit, HealthEntry

from .constants import (
    COMPLETION_TREND_DAYS,
    SLEEP_DEVIATION_DAYS,
    MOOD_TREND_DAYS,
    STREAK_BREAK_LOOKBACK,
    PCS_MINIMUM_DAYS,
    CORRELATION_DAYS,
    MAX_MISSED_DAYS_LOOKBACK,
    MIN_CORRELATION_SAMPLES,
    SLEEP_BASELINE_HOURS,
    MOOD_SCORES,
    DEFAULT_STRESS_LEVEL,
    COMPLETION_TREND_SCALE,
    MOOD_TREND_SCALE,
)


def gather_burnout_indicators(storage: Storage):
    """
    Gather data for burnout prediction from storage.
    
    Returns:
        BurnoutIndicators with current metrics
    """
    try:
        from brain.analysis.burnout import BurnoutIndicators
    except ImportError:
        return None
    
    today = date.today()
    
    # Get habits
    habits = storage.get_habits()
    active_habits = [h for h in habits if not h.archived]
    
    # Calculate completion rate trend
    completion_trend = calculate_completion_trend(storage, active_habits, days=COMPLETION_TREND_DAYS)
    
    # Get sleep data from health entries
    sleep_deviation = calculate_sleep_deviation(storage, days=SLEEP_DEVIATION_DAYS)
    
    # Get mood trend
    mood_trend = calculate_mood_trend(storage, days=MOOD_TREND_DAYS)
    
    # Count streak breaks in last 7 days
    streak_breaks = count_recent_streak_breaks(storage, active_habits, days=STREAK_BREAK_LOOKBACK)
    
    # Count missed days
    missed_days = count_consecutive_missed_days(storage, active_habits)
    
    # Task overload (mock - would need task data)
    task_overload = 0.0  # TODO: Calculate from task data
    
    return BurnoutIndicators(
        completion_rate_trend=completion_trend,
        sleep_deviation=sleep_deviation,
        stress_level=DEFAULT_STRESS_LEVEL,
        days_since_checkin=0,  # User is here now
        streak_breaks=streak_breaks,
        mood_trend=mood_trend,
        task_overload=task_overload,
        habit_load=len(active_habits),
        missed_days=missed_days
    )


def calculate_completion_trend(storage: Storage, habits: List[Habit], days: int = COMPLETION_TREND_DAYS) -> float:
    """Calculate trend in completion rate."""
    if not habits:
        return 0.0
    
    today = date.today()
    
    # First half
    first_half_completions = 0
    first_half_total = 0
    for i in range(days // 2, days):
        check_date = today - timedelta(days=i)
        for habit in habits:
            entry = storage.get_habit_entry(habit.id, check_date)
            first_half_total += 1
            if entry and not entry.skipped and entry.value > 0:
                first_half_completions += 1
    
    # Second half
    second_half_completions = 0
    second_half_total = 0
    for i in range(0, days // 2):
        check_date = today - timedelta(days=i)
        for habit in habits:
            entry = storage.get_habit_entry(habit.id, check_date)
            second_half_total += 1
            if entry and not entry.skipped and entry.value > 0:
                second_half_completions += 1
    
    if first_half_total == 0 or second_half_total == 0:
        return 0.0
    
    first_rate = first_half_completions / first_half_total
    second_rate = second_half_completions / second_half_total
    
    # Normalize to -1 to 1
    diff = second_rate - first_rate
    return max(-1.0, min(1.0, diff * COMPLETION_TREND_SCALE))


def calculate_sleep_deviation(storage: Storage, days: int = SLEEP_DEVIATION_DAYS) -> float:
    """Calculate deviation from average sleep hours."""
    health_entries = storage.get_health_entries(
        start_date=date.today() - timedelta(days=days)
    )
    
    if not health_entries or len(health_entries) < 3:
        return 0.0
    
    # Get sleep hours
    sleep_hours = [e.sleep_hours for e in health_entries if e.sleep_hours]
    
    if len(sleep_hours) < 3:
        return 0.0
    
    # Calculate average and recent deviation
    if len(sleep_hours) > 3:
        avg_sleep = sum(sleep_hours[:-3]) / len(sleep_hours[:-3])
    else:
        avg_sleep = sum(sleep_hours) / len(sleep_hours)
    recent_sleep = sum(sleep_hours[-3:]) / 3
    
    return recent_sleep - avg_sleep


def calculate_mood_trend(storage: Storage, days: int = MOOD_TREND_DAYS) -> float:
    """Calculate trend in mood scores."""
    health_entries = storage.get_health_entries(
        start_date=date.today() - timedelta(days=days)
    )
    
    if not health_entries or len(health_entries) < 3:
        return 0.0
    
    scores = [MOOD_SCORES.get(e.mood, 0.5) for e in health_entries if e.mood]
    
    if len(scores) < 3:
        return 0.0
    
    # Simple trend: compare first half to second half
    mid = len(scores) // 2
    first_avg = sum(scores[:mid]) / mid if mid > 0 else 0.5
    second_avg = sum(scores[mid:]) / (len(scores) - mid) if len(scores) > mid else 0.5
    
    return max(-1.0, min(1.0, (second_avg - first_avg) * MOOD_TREND_SCALE))


def count_recent_streak_breaks(storage: Storage, habits: List[Habit], days: int = STREAK_BREAK_LOOKBACK) -> int:
    """Count streak breaks in the last N days."""
    today = date.today()
    breaks = 0
    
    for habit in habits:
        # Check if there was a completion before the window
        had_completion_before = False
        for i in range(days + 1, days + 7):
            check_date = today - timedelta(days=i)
            entry = storage.get_habit_entry(habit.id, check_date)
            if entry and not entry.skipped and entry.value > 0:
                had_completion_before = True
                break
        
        if not had_completion_before:
            continue
        
        # Count missed days in window
        for i in range(days):
            check_date = today - timedelta(days=i)
            entry = storage.get_habit_entry(habit.id, check_date)
            if not entry or (not entry.skipped and entry.value == 0):
                breaks += 1
                break  # Only count once per habit
    
    return breaks


def count_consecutive_missed_days(storage: Storage, habits: List[Habit]) -> int:
    """Count consecutive days with no completions."""
    if not habits:
        return 0
    
    today = date.today()
    missed = 0
    
    for i in range(MAX_MISSED_DAYS_LOOKBACK):
        check_date = today - timedelta(days=i)
        any_completed = False
        
        for habit in habits:
            entry = storage.get_habit_entry(habit.id, check_date)
            if entry and not entry.skipped and entry.value > 0:
                any_completed = True
                break
        
        if any_completed:
            break
        missed += 1
    
    return missed


def gather_habit_data_for_pcs(
    storage: Storage, 
    habit: Habit, 
    days: int = 30
) -> Tuple[List[bool], List]:
    """
    Gather completion and context data for PCS calculation.
    
    Returns:
        Tuple of (completion_history, context_history)
    """
    try:
        from brain.analysis.prediction import ContextVariables
    except ImportError:
        return [], []
    
    today = date.today()
    completions = []
    contexts = []
    
    # Get health entries for context
    health_entries = storage.get_health_entries(
        start_date=today - timedelta(days=days)
    )
    health_by_date = {e.entry_date: e for e in health_entries if e.entry_date}
    
    for i in range(days):
        check_date = today - timedelta(days=i)
        
        # Get completion status
        entry = storage.get_habit_entry(habit.id, check_date)
        completed = entry is not None and not entry.skipped and entry.value > 0
        completions.append(completed)
        
        # Get context for this date
        health = health_by_date.get(check_date)
        
        if health:
            context = ContextVariables(
                date=check_date.isoformat(),
                sleep_hours=health.sleep_hours,
                mood_score=MOOD_SCORES.get(health.mood, 0.5),
                day_of_week=check_date.weekday()
            )
        else:
            # Default context
            context = ContextVariables(
                date=check_date.isoformat(),
                day_of_week=check_date.weekday()
            )
        
        contexts.append(context)
    
    # Reverse to get chronological order (oldest first)
    completions.reverse()
    contexts.reverse()
    
    return completions, contexts


def calculate_habit_correlations(
    storage: Storage,
    habits: List[Habit],
    days: int = CORRELATION_DAYS
) -> List[Dict[str, Any]]:
    """
    Calculate correlations between habits.
    
    Returns:
        List of correlation results
    """
    if len(habits) < 2:
        return []
    
    try:
        from brain.analysis.correlation import CorrelationEngine
    except ImportError:
        return []
    
    today = date.today()
    habit_data = {}
    
    # Gather completion data for each habit
    for habit in habits:
        completions = []
        for i in range(days):
            check_date = today - timedelta(days=i)
            entry = storage.get_habit_entry(habit.id, check_date)
            completed = 1.0 if (entry and not entry.skipped and entry.value > 0) else 0.0
            completions.append(completed)
        habit_data[habit.name] = completions
    
    # Calculate correlations
    engine = CorrelationEngine()
    correlations = engine.analyze_habit_correlations(habit_data, min_samples=MIN_CORRELATION_SAMPLES)
    
    return [c.to_dict() for c in correlations]