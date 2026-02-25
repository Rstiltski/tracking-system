"""
UI Components Module - Reusable Streamlit Components

This module provides shared UI components used across all pages:
- Sidebar navigation
- Session state management
- Metric cards
- Charts and visualizations

Usage:
    from tracking_app.components import render_sidebar, init_session
"""
from tracking_app.components.sidebar import render_sidebar
from tracking_app.components.session import init_session_state, get_storage
from tracking_app.components.metrics import (
    render_metric_card,
    render_habit_score_card,
    render_progress_card
)
from tracking_app.components.charts import (
    render_weekly_chart,
    render_score_trend_chart
)

__all__ = [
    # Sidebar
    "render_sidebar",
    
    # Session
    "init_session_state",
    "get_storage",
    
    # Metrics
    "render_metric_card",
    "render_habit_score_card",
    "render_progress_card",
    
    # Charts
    "render_weekly_chart",
    "render_score_trend_chart",
]