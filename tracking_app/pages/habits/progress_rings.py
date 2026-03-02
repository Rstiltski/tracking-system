"""
Progress rings component for the Habits page.

Renders visual progress rings for habit completion statistics.
"""

import streamlit as st
from datetime import date, timedelta
from typing import List

from tracking_app.models import Habit

from .helpers import (
    get_local_date,
    is_entry_completed,
    calculate_streak,
    get_completion_rate,
    get_week_start,
    get_month_start,
)


def render_progress_ring(progress: float, label: str, color: str, size: int = 100):
    """
    Render a circular progress ring using HTML/CSS.
    
    Args:
        progress: Progress value between 0 and 1
        label: Label to display below the ring
        color: Color for the progress arc
        size: Size of the ring in pixels
    """
    percentage = int(progress * 100)
    
    # Calculate stroke-dasharray values for the ring
    # The circle's circumference is 2 * PI * radius
    radius = (size - 10) / 2
    circumference = 2 * 3.14159 * radius
    stroke_dashoffset = circumference * (1 - progress)
    
    st.markdown(
        f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0 10px;
        ">
            <div style="
                position: relative;
                width: {size}px;
                height: {size}px;
            ">
                <svg width="{size}" height="{size}" style="transform: rotate(-90deg);">
                    <!-- Background circle -->
                    <circle
                        cx="{size/2}"
                        cy="{size/2}"
                        r="{radius}"
                        fill="none"
                        stroke="#e2e8f0"
                        stroke-width="6"
                    />
                    <!-- Progress arc -->
                    <circle
                        cx="{size/2}"
                        cy="{size/2}"
                        r="{radius}"
                        fill="none"
                        stroke="{color}"
                        stroke-width="6"
                        stroke-linecap="round"
                        stroke-dasharray="{circumference}"
                        stroke-dashoffset="{stroke_dashoffset}"
                        style="transition: stroke-dashoffset 0.5s ease;"
                    />
                </svg>
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: {size/4}px;
                    font-weight: bold;
                    color: #1e293b;
                ">{percentage}%</div>
            </div>
            <div style="
                font-size: 0.85rem;
                color: #64748b;
                margin-top: 8px;
                text-align: center;
            ">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_progress_summary(habits: List[Habit], storage):
    """
    Render a summary of habit progress with multiple progress rings.
    
    Displays rings for:
    - Today's completion rate
    - This week's completion rate
    - This month's completion rate
    - Overall average streak
    
    Args:
        habits: List of all habits
        storage: Storage instance for data access
    """
    today = get_local_date()
    week_start = get_week_start(today)
    month_start = get_month_start(today)
    
    active_habits = [h for h in habits if not h.archived]
    
    if not active_habits:
        st.info("Add habits to see your progress summary!")
        return
    
    # Calculate today's progress
    completed_today = 0
    for habit in active_habits:
        entry = storage.get_habit_entry(habit.id, today)
        if is_entry_completed(entry):
            completed_today += 1
    today_progress = completed_today / len(active_habits)
    
    # Calculate this week's progress
    completed_this_week = 0
    total_this_week = 0
    for habit in active_habits:
        for i in range(7):
            day = week_start + timedelta(days=i)
            if day <= today:
                total_this_week += 1
                entry = storage.get_habit_entry(habit.id, day)
                if is_entry_completed(entry):
                    completed_this_week += 1
    week_progress = completed_this_week / total_this_week if total_this_week > 0 else 0
    
    # Calculate this month's progress
    completed_this_month = 0
    total_this_month = 0
    days_in_month = (today - month_start).days + 1
    for habit in active_habits:
        for i in range(days_in_month):
            day = month_start + timedelta(days=i)
            total_this_month += 1
            entry = storage.get_habit_entry(habit.id, day)
            if is_entry_completed(entry):
                completed_this_month += 1
    month_progress = completed_this_month / total_this_month if total_this_month > 0 else 0
    
    # Calculate average streak
    total_streak = sum(calculate_streak(storage, h.id) for h in active_habits)
    avg_streak = total_streak / len(active_habits)
    streak_progress = min(1, avg_streak / 30)  # Normalize to 30 days
    
    # Render the progress rings
    st.markdown("""
    <style>
    .progress-rings-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
        flex-wrap: wrap;
    }
    </style>
    """, unsafe_allow_html=True)
    
    cols = st.columns(4)
    
    with cols[0]:
        render_progress_ring(today_progress, "Today", "#22c55e", size=80)
    
    with cols[1]:
        render_progress_ring(week_progress, "This Week", "#3b82f6", size=80)
    
    with cols[2]:
        render_progress_ring(month_progress, "This Month", "#8b5cf6", size=80)
    
    with cols[3]:
        render_progress_ring(streak_progress, f"Avg Streak: {avg_streak:.1f}d", "#f97316", size=80)
    
    # Additional stats below the rings
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Habits", len(active_habits))
    
    with col2:
        st.metric("Completed Today", f"{completed_today}/{len(active_habits)}")
    
    with col3:
        best_streak = max(calculate_streak(storage, h.id) for h in active_habits) if active_habits else 0
        st.metric("Best Current Streak", f"{best_streak} days")
    
    with col4:
        avg_completion = sum(get_completion_rate(storage, h.id) for h in active_habits) / len(active_habits)
        st.metric("Avg Completion (30d)", f"{avg_completion:.0f}%")


def render_mini_progress_ring(progress: float, color: str = "#22c55e", size: int = 24):
    """
    Render a small progress ring for inline display.
    
    Args:
        progress: Progress value between 0 and 1
        color: Color for the progress arc
        size: Size of the ring in pixels
    """
    radius = (size - 4) / 2
    circumference = 2 * 3.14159 * radius
    stroke_dashoffset = circumference * (1 - progress)
    
    st.markdown(
        f"""
        <svg width="{size}" height="{size}" style="transform: rotate(-90deg);">
            <circle
                cx="{size/2}"
                cy="{size/2}"
                r="{radius}"
                fill="none"
                stroke="#e2e8f0"
                stroke-width="2"
            />
            <circle
                cx="{size/2}"
                cy="{size/2}"
                r="{radius}"
                fill="none"
                stroke="{color}"
                stroke-width="2"
                stroke-linecap="round"
                stroke-dasharray="{circumference}"
                stroke-dashoffset="{stroke_dashoffset}"
            />
        </svg>
        """,
        unsafe_allow_html=True
    )