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
    category = _get_score_category(score_value)
    trend_icon = "↑" if trend > 0.001 else "↓" if trend < -0.001 else "→"
    trend_color = "#10B981" if trend > 0 else "#EF4444" if trend < 0 else "#94A3B8"
    percentage = round(score_value * 100)
    
    card_html = f"""<div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.2) 100%); border: 1px solid rgba(255, 255, 255, 0.05); border-top: 3px solid {category['color']}; border-radius: 12px; padding: 16px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); display: flex; flex-direction: column; gap: 12px;">
<div style="display: flex; justify-content: space-between; align-items: flex-start;">
<div style="font-size: 28px; font-weight: 800; color: #F8FAFC; line-height: 1; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">{category['emoji']} {percentage}%</div>
<div style="font-size: 13px; font-weight: 700; color: {trend_color}; display: flex; flex-direction: column; align-items: flex-end; gap: 2px;">
<span>{trend_icon} {category['label'] if show_details else ''}</span>
</div>
</div>
<div style="width: 100%; height: 6px; background: rgba(255,255,255,0.05); border-radius: 4px; overflow: hidden; margin-top: 4px;">
<div style="width: {percentage}%; height: 100%; background: {category['color']}; border-radius: 4px; box-shadow: 0 0 10px {category['color']}80;"></div>
</div>
<div style="color: #94A3B8; font-size: 14px; font-weight: 500; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; line-height: 1.4;">{habit_name}</div>
</div>"""
    
    st.markdown(card_html, unsafe_allow_html=True)


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