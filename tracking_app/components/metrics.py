"""
Metrics Components - Display Cards and Metrics

Provides reusable metric cards for displaying stats, habit scores, and progress.

Usage:
    from tracking_app.components.metrics import (
        render_metric_card,
        render_habit_score_card,
        render_progress_card
    )
"""
import streamlit as st
from typing import Dict, Optional, Any
from datetime import date


def render_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    icon: str = "📊"
):
    """
    Render a metric card with label, value, and optional delta.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional change indicator
        icon: Emoji icon
    """
    st.metric(label=f"{icon} {label}", value=value, delta=delta)


def render_habit_score_card(
    score_value: float,
    habit_name: str = "Habit Score",
    trend: float = 0.0,
    show_details: bool = True
):
    """
    Render a habit score card with category and trend.
    
    Uses the scoring system from brain/models/habit.py:
    - Excellent (85-100%): 🌟 Green
    - Strong (70-84%): 💪 Light Green
    - Developing (50-69%): 🌱 Yellow
    - Building (30-49%): 🔧 Orange
    - Starting (0-29%): 🆕 Red
    
    Args:
        score_value: Score value (0.0 to 1.0)
        habit_name: Name of the habit
        trend: Trend value (-1.0 to 1.0)
        show_details: Whether to show category details
    """
    # Get category
    category = _get_score_category(score_value)
    trend_icon = "↑" if trend > 0.001 else "↓" if trend < -0.001 else "→"
    trend_color = "green" if trend > 0 else "red" if trend < 0 else "gray"
    
    # Create container with border color
    percentage = round(score_value * 100)
    
    # Display score
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(
            f"""
            <div style="
                padding: 1rem;
                border-radius: 0.5rem;
                border-left: 4px solid {category['color']};
                background: rgba(255,255,255,0.05);
            ">
                <div style="font-size: 1.5rem; font-weight: bold;">
                    {category['emoji']} {percentage}%
                </div>
                <div style="color: gray; font-size: 0.9rem;">
                    {habit_name}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        if show_details:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 0.5rem;">
                    <div style="font-size: 1.2rem;">{trend_icon}</div>
                    <div style="font-size: 0.8rem; color: {trend_color};">
                        {category['label']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


def _get_score_category(score: float) -> Dict[str, str]:
    """
    Get the score category for a given score value.
    
    Args:
        score: Score value (0.0 to 1.0)
        
    Returns:
        Dict with 'label', 'color', and 'emoji' keys
    """
    if score >= 0.85:
        return {"label": "Excellent", "color": "#4CAF50", "emoji": "🌟"}
    elif score >= 0.70:
        return {"label": "Strong", "color": "#8BC34A", "emoji": "💪"}
    elif score >= 0.50:
        return {"label": "Developing", "color": "#FFC107", "emoji": "🌱"}
    elif score >= 0.30:
        return {"label": "Building", "color": "#FF9800", "emoji": "🔧"}
    else:
        return {"label": "Starting", "color": "#F44336", "emoji": "🆕"}


def render_progress_card(
    title: str,
    current: float,
    target: float,
    unit: str = "",
    icon: str = "🎯"
):
    """
    Render a progress card with bar.
    
    Args:
        title: Card title
        current: Current progress value
        target: Target value
        unit: Unit of measurement
        icon: Emoji icon
    """
    st.markdown(f"**{icon} {title}**")
    
    if target > 0:
        progress = min(current / target, 1.0)
        st.progress(progress)
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"Current: {current:.1f} {unit}")
        with col2:
            st.caption(f"Target: {target:.1f} {unit}")
    else:
        st.progress(0)
        st.caption("No target set")


def render_streak_card(
    streak_count: int,
    streak_freezes: int = 0,
    best_streak: int = 0
):
    """
    Render a streak display card.
    
    Args:
        streak_count: Current streak
        streak_freezes: Available streak freezes
        best_streak: Best streak achieved
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🔥 Current Streak",
            value=f"{streak_count} days"
        )
    
    with col2:
        st.metric(
            label="❄️ Streak Freezes",
            value=streak_freezes
        )
    
    with col3:
        st.metric(
            label="🏆 Best Streak",
            value=f"{best_streak} days"
        )


def render_burnout_risk_card(
    risk_score: float,
    risk_level: str,
    contributing_factors: Optional[Dict[str, float]] = None
):
    """
    Render a burnout risk indicator card.
    
    Args:
        risk_score: Risk score (0-100)
        risk_level: Risk level (low/moderate/high/critical)
        contributing_factors: Dict of factor names and their impact
    """
    risk_colors = {
        "low": "#4CAF50",
        "moderate": "#FFC107", 
        "high": "#FF9800",
        "critical": "#F44336"
    }
    risk_emojis = {
        "low": "🟢",
        "moderate": "🟡",
        "high": "🟠",
        "critical": "🔴"
    }
    
    color = risk_colors.get(risk_level, "#808080")
    emoji = risk_emojis.get(risk_level, "⚪")
    
    st.markdown(
        f"""
        <div style="
            padding: 1rem;
            border-radius: 0.5rem;
            border: 2px solid {color};
            background: rgba(255,255,255,0.05);
        ">
            <div style="font-size: 1.2rem; font-weight: bold;">
                {emoji} Burnout Risk: {risk_level.upper()}
            </div>
            <div style="font-size: 2rem; font-weight: bold; color: {color};">
                {risk_score:.0f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if contributing_factors:
        st.caption("**Contributing Factors:**")
        for factor, impact in contributing_factors.items():
            st.caption(f"• {factor}: {impact:.1%}")


__all__ = [
    "render_metric_card",
    "render_habit_score_card",
    "render_progress_card",
    "render_streak_card",
    "render_burnout_risk_card",
]