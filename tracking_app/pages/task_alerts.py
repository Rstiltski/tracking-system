"""
Task Alerts Settings Page

Streamlit UI for configuring task deadline alerts and daily digest.
Provides controls for deadline warning thresholds, progressive urgency,
and daily digest preferences.

Phase 4.3 Feature: Task Alert Settings UI

Usage:
    streamlit run tracking_app/pages/task_alerts.py
"""

# Conditional streamlit import for test compatibility
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None

from tracking_app.pages.task_alerts import (
    init_session_state,
    render_task_alerts_page,
    render_general_settings,
    render_deadline_thresholds,
    render_progressive_urgency,
    render_daily_digest,
    render_overdue_settings,
    render_priority_settings,
    render_today_alerts,
)
from tracking_app.pages.task_alerts.constants import DEFAULT_USER_ID


def main():
    """Main entry point for the page."""
    if HAS_STREAMLIT:
        render_task_alerts_page()
    else:
        print("Streamlit not installed. Run: pip install streamlit")


if __name__ == "__main__":
    main()