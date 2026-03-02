"""
Helper functions for the Dashboard page.

Contains utility functions for data retrieval and calculations.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Tuple

from tracking_app.storage import Storage
from tracking_app.models import Habit, Task, Goal, HabitEntry

from .constants import (
    SCORE_LOOKBACK_DAYS,
    SIMPLE_SCORE_LOOKBACK,
    MAX_STREAK_DAYS,
    ACTIVITY_LIMIT,
    WEEKLY_CHART_DAYS,
    BURNOUT_HIGH_THRESHOLD,
    BURNOUT_MODERATE_THRESHOLD,
)


def get_todays_habits(storage: Storage) -> Tuple[List[Habit], int, int]:
    """
    Get habits and completion status for today.
    
    Args:
        storage: Storage instance
        
    Returns:
        Tuple of (habits list, completed count, total count)
    """
    habits = storage.get_habits()
    today = date.today()
    
    completed = 0
    total = len(habits)
    
    for habit in habits:
        entry = storage.get_habit_entry(habit.id, today)
        if entry and not entry.skipped:
            completed += 1
    
    return habits, completed, total


def get_active_tasks(storage: Storage) -> Tuple[List[Task], int, int, int]:
    """
    Get active tasks and counts.
    
    Args:
        storage: Storage instance
        
    Returns:
        Tuple of (tasks list, high_priority count, due_today count, overdue count)
    """
    tasks = storage.get_tasks(include_completed=False)
    
    high_priority = len([t for t in tasks if t.priority == 'high'])
    due_today = len([t for t in tasks if t.due_date and t.due_date.date() == date.today()])
    overdue = len([t for t in tasks if t.due_date and t.due_date.date() < date.today()])
    
    return tasks, high_priority, due_today, overdue


def get_goals_progress(storage: Storage) -> Tuple[List[Goal], float]:
    """
    Get goals and overall progress.
    
    Args:
        storage: Storage instance
        
    Returns:
        Tuple of (goals list, average progress percentage)
    """
    goals = storage.get_goals()
    
    if not goals:
        return goals, 0
    
    total_progress = sum(g.progress_percentage for g in goals) / len(goals)
    return goals, total_progress


def get_weekly_habit_data(storage: Storage, days: int = WEEKLY_CHART_DAYS) -> Dict[str, List]:
    """
    Get habit completion data for the past N days.
    
    Args:
        storage: Storage instance
        days: Number of days to look back
        
    Returns:
        Dictionary with dates, completed counts, and total counts
    """
    habits = storage.get_habits()
    today = date.today()
    
    data = {
        'dates': [],
        'completed': [],
        'total': []
    }
    
    for i in range(days - 1, -1, -1):
        check_date = today - timedelta(days=i)
        data['dates'].append(check_date.strftime('%a'))
        
        day_completed = 0
        day_total = len(habits)
        
        for habit in habits:
            entry = storage.get_habit_entry(habit.id, check_date)
            if entry and not entry.skipped:
                day_completed += 1
        
        data['completed'].append(day_completed)
        data['total'].append(day_total)
    
    return data


def calculate_habit_scores(storage: Storage) -> List[Dict[str, Any]]:
    """
    Calculate habit scores using the brain models algorithm.
    
    Returns list of dicts with habit name, score, and trend.
    """
    try:
        from brain.models.habit import HabitScore, ScoreList
        from brain.models.frequency import Frequency
        from brain.models.entry import EntryList
    except ImportError:
        # Fallback to simple calculation if brain models not available
        return calculate_simple_scores(storage)
    
    habits = storage.get_habits()
    today = date.today()
    results = []
    
    for habit in habits:
        entries = storage.get_habit_entries(habit.id)
        
        if not entries:
            # New habit, no score yet
            results.append({
                'name': habit.name,
                'icon': habit.icon,
                'id': habit.id,
                'score': 0.0,
                'trend': 0.0
            })
            continue
        
        # Calculate score using exponential smoothing
        lookback_days = SCORE_LOOKBACK_DAYS
        scores = []
        prev_score = 0.0
        prev_trend = 0.0
        
        for i in range(lookback_days - 1, -1, -1):
            check_date = today - timedelta(days=i)
            entry = storage.get_habit_entry(habit.id, check_date)
            checkmark = 1.0 if (entry and not entry.skipped) else 0.0
            
            # Use HabitScore.compute
            score = HabitScore.compute(
                frequency=1.0,  # Daily habit
                previous_score=prev_score,
                checkmark_value=checkmark,
                previous_trend=prev_trend
            )
            scores.append(score)
            prev_score = score.value
            prev_trend = score.trend
        
        if scores:
            latest = scores[-1]
            results.append({
                'name': habit.name,
                'icon': habit.icon,
                'id': habit.id,
                'score': latest.value,
                'trend': latest.trend
            })
    
    return results


def calculate_simple_scores(storage: Storage) -> List[Dict[str, Any]]:
    """Simple score calculation fallback."""
    habits = storage.get_habits()
    today = date.today()
    results = []
    
    for habit in habits:
        # Calculate 30-day completion rate
        completed = 0
        for i in range(SIMPLE_SCORE_LOOKBACK):
            check_date = today - timedelta(days=i)
            entry = storage.get_habit_entry(habit.id, check_date)
            if entry and not entry.skipped:
                completed += 1
        
        score = completed / SIMPLE_SCORE_LOOKBACK if completed > 0 else 0.0
        
        results.append({
            'name': habit.name,
            'icon': habit.icon,
            'id': habit.id,
            'score': score,
            'trend': 0.0
        })
    
    return results


def calculate_streak(storage: Storage, habits: List[Habit]) -> int:
    """
    Calculate the overall streak (all habits completed).
    
    Args:
        storage: Storage instance
        habits: List of habits
        
    Returns:
        Number of consecutive days all habits were completed
    """
    streak = 0
    today = date.today()
    
    for i in range(MAX_STREAK_DAYS):
        check_date = today - timedelta(days=i)
        day_complete = True
        
        for habit in habits:
            entry = storage.get_habit_entry(habit.id, check_date)
            if not entry or entry.skipped:
                day_complete = False
                break
        
        if day_complete:
            streak += 1
        else:
            break
    
    return streak


def get_recent_activity(storage: Storage, limit: int = ACTIVITY_LIMIT) -> List[Dict[str, Any]]:
    """
    Get recent activity for the activity feed.
    
    Args:
        storage: Storage instance
        limit: Maximum number of activities to return
        
    Returns:
        List of activity dictionaries
    """
    activities = []
    today = date.today()
    
    # Get recent habit completions
    habits = storage.get_habits()
    for habit in habits:
        entries = storage.get_habit_entries(habit.id, end_date=today)
        for entry in entries[:3]:  # Last 3 entries per habit
            activities.append({
                'type': 'habit',
                'icon': habit.icon,
                'title': f"Completed {habit.name}",
                'date': entry.entry_date,
                'xp': 10
            })
    
    # Get recent task completions
    tasks = storage.get_tasks(include_completed=True)
    for task in tasks:
        if task.completed:
            activities.append({
                'type': 'task',
                'icon': '📋',
                'title': f"Completed: {task.title}",
                'date': task.completed_at if hasattr(task, 'completed_at') else today,
                'xp': {"high": 20, "medium": 10, "low": 5}.get(task.priority, 10)
            })
    
    # Sort by date (most recent first)
    activities.sort(key=lambda x: x['date'] if x['date'] else today, reverse=True)
    
    return activities[:limit]


def get_burnout_risk(storage: Storage) -> Dict[str, Any]:
    """
    Calculate burnout risk using brain/analysis/burnout.py.
    
    Returns dict with risk_score, risk_level, and contributing_factors.
    """
    try:
        from brain.analysis.burnout import BurnoutPredictor, BurnoutIndicators
        
        # Gather indicators from storage
        habits = storage.get_habits()
        tasks = storage.get_tasks(include_completed=False)
        today = date.today()
        
        # Calculate completion rate trend
        recent_completed = 0
        previous_completed = 0
        for habit in habits:
            for i in range(7):
                entry = storage.get_habit_entry(habit.id, today - timedelta(days=i))
                if entry and not entry.skipped:
                    recent_completed += 1
            for i in range(7, 14):
                entry = storage.get_habit_entry(habit.id, today - timedelta(days=i))
                if entry and not entry.skipped:
                    previous_completed += 1
        
        if previous_completed > 0:
            completion_trend = (recent_completed - previous_completed) / previous_completed
        else:
            completion_trend = 0
        
        # Get health data
        health_entries = storage.get_health_entries(
            start_date=today - timedelta(days=14),
            end_date=today
        )
        
        avg_sleep = sum(e.sleep_hours or 0 for e in health_entries) / len(health_entries) if health_entries else 7
        sleep_deviation = avg_sleep - 7.5  # Baseline is 7.5 hours
        
        # Create indicators
        indicators = BurnoutIndicators(
            completion_rate_trend=completion_trend,
            sleep_deviation=sleep_deviation,
            stress_level=5,  # Default, would come from user input
            days_since_checkin=0,  # They're checking in now
            streak_breaks=0,
            mood_trend=0,
            task_overload=len(tasks) / 10,  # Normalize
            habit_load=len(habits),
            missed_days=0
        )
        
        # Calculate risk
        predictor = BurnoutPredictor()
        risk = predictor.assess_risk(indicators)
        
        return {
            'score': risk.risk_score,
            'level': risk.risk_level,
            'factors': risk.contributing_factors,
            'interventions': risk.interventions[:3] if risk.interventions else []
        }
        
    except (ImportError, Exception):
        # Fallback to simple calculation
        return calculate_simple_burnout_risk(storage)


def calculate_simple_burnout_risk(storage: Storage) -> Dict[str, Any]:
    """Simple burnout risk calculation fallback."""
    habits = storage.get_habits()
    tasks = storage.get_tasks(include_completed=False)
    today = date.today()
    
    # Simple heuristics
    missed_days = 0
    for habit in habits:
        entry = storage.get_habit_entry(habit.id, today - timedelta(days=1))
        if not entry or entry.skipped:
            missed_days += 1
    
    task_overload = len(tasks) > 10
    habit_overload = len(habits) > 10
    
    risk_score = 0
    if missed_days > len(habits) / 2:
        risk_score += 30
    if task_overload:
        risk_score += 25
    if habit_overload:
        risk_score += 20
    
    if risk_score >= BURNOUT_HIGH_THRESHOLD:
        level = "high"
    elif risk_score >= BURNOUT_MODERATE_THRESHOLD:
        level = "moderate"
    else:
        level = "low"
    
    return {
        'score': risk_score,
        'level': level,
        'factors': {'missed_days': missed_days, 'task_count': len(tasks)},
        'interventions': []
    }